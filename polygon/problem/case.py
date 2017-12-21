import io
import os
import re
import shutil
import zipfile
from multiprocessing.pool import Pool
from os import path, makedirs
from threading import Thread

import chardet
import time
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views import View
from django.views.generic import FormView
from django.views.generic import ListView

from polygon.models import RepositorySource, RepositoryTest
from polygon.problem.exception import RepositoryException
from polygon.problem.forms import TestCreateForm
from polygon.problem.source import Program
from polygon.problem.utils import get_tmp_directory
from polygon.problem.views import PolygonProblemMixin
from utils.file_preview import sort_data_list_from_directory, sort_input_list_from_directory
from utils.hash import case_hash

GENERATE_PROMPT = 'Generating...\nReload the page'


class TextFormatter:
    white_space_reg = re.compile(r'[\x00-\x20\s]+')

    @staticmethod
    def read_by_formed_lines(fileobj):
        for line in fileobj:
            yield ' '.join(TextFormatter.white_space_reg.split(line.strip()))

    @staticmethod
    def well_form_text(text):
        stream = io.StringIO(text.strip())
        out_stream = io.StringIO()
        for line in TextFormatter.read_by_formed_lines(stream):
            out_stream.writelines([line, '\n'])
        out_stream.seek(0)
        return out_stream.read()

    @staticmethod
    def well_form_binary(binary):
        try:
            encoding = chardet.detect(binary).get('encoding', 'utf-8')
            return TextFormatter.well_form_text(binary.decode(encoding))
        except:
            return ''

    @staticmethod
    def format_file(path):
        try:
            with open(path, 'rb') as inf:
                b = TextFormatter.well_form_binary(inf.read())
            with open(path, 'w') as ouf:
                ouf.write(b)
        except FileNotFoundError:
            pass


class TestManager:
    def __init__(self, test):
        self.problem = test.problem
        self.test = test
        makedirs(self.workspace, exist_ok=True)

    @property
    def workspace(self):
        return path.join(settings.REPO_DIR, str(self.problem.pk), 'tests')

    @property
    def input_path(self):
        return path.join(self.workspace, '%d.in' % self.test.pk)

    @property
    def output_path(self):
        return path.join(self.workspace, '%d.out' % self.test.pk)

    @staticmethod
    def get_size(file):
        try:
            return path.getsize(file)
        except FileNotFoundError:
            return 0

    def refresh_test_preview(self):
        self.file_error = ''
        if self.test.problem.well_form_policy:
            TextFormatter.format_file(self.input_path)
            TextFormatter.format_file(self.output_path)
        self.test.input_preview = self.read_abstract(self.input_path)
        self.test.output_preview = self.read_abstract(self.output_path)
        self.test.fingerprint = case_hash(self.problem.pk, self.read_binary(self.input_path),
                                          self.read_binary(self.output_path))
        self.test.size = self.get_size(self.input_path) + self.get_size(self.output_path)
        self.test.file_error = self.file_error
        self.test.save(update_fields=['input_preview', 'output_preview', 'fingerprint', 'size', 'file_error'])

    def write_input(self, txt):
        with open(self.input_path, 'w') as f:
            f.write(txt)

    def write_output(self, txt):
        with open(self.output_path, 'w') as f:
            f.write(txt)

    def read_abstract(self, file):
        try:
            with open(file, 'r') as f:
                s = f.read(24)
                if f.read(1):
                    s += ' ...'
            return s
        except UnicodeDecodeError as e:
            return str(e)
        except FileNotFoundError:
            self.file_error = "Test not found: %s" % path.split(file)[1]
            return self.file_error

    def read_binary(self, file):
        try:
            with open(file, 'rb') as f:
                return f.read()
        except FileNotFoundError:
            self.file_error = "Test not found: %s" % path.split(file)[1]
            return self.file_error.encode()

    def regenerate_output(self):
        timeout = self.problem.time_limit / 1000 * 3  # 3 times time limit
        try:
            try:
                std = Program(self.problem.repositorysource_set.get(tag='solution_main'))
            except (RepositorySource.DoesNotExist, RepositorySource.MultipleObjectsReturned):
                raise RepositoryException("There should be one and only one main correct solution")
            std.run([], timeout, self.input_path)
            shutil.copy(std.default_output_path, self.output_path)
            if self.test.invalid:
                self.test.invalid = ''
                self.test.save(update_fields=['invalid'])
        except Exception as e:
            self.test.invalid = str(e)
            self.test.save(update_fields=['invalid'])
        self.refresh_test_preview()

    @staticmethod
    def validate_input_and_generate_output(test):
        tm = TestManager(test)
        tm.regenerate_output()


class TestSetManager:
    def __init__(self, testset):
        if len(testset) == 0:
            raise RepositoryException("Test set is empty")
        self.problem = testset[0].problem
        self.testset = testset
        makedirs(self.workspace, exist_ok=True)

    @property
    def workspace(self):
        return path.join(settings.REPO_DIR, str(self.problem.pk), 'tests')

    @transaction.atomic
    def move_after(self, case_num):
        for test in filter(lambda case: case not in self.testset and case.case_number > case_num,
                           self.problem.repositorytest_set.all()):
            test.case_number += len(self.testset)
            test.save(update_fields=['case_number'])
        for idx, test in enumerate(self.testset, start=1):
            test.case_number = case_num + idx
            test.save(update_fields=['case_number'])
        self.fix_order()

    @transaction.atomic
    def fix_order(self):
        for idx, test in enumerate(self.problem.repositorytest_set.all(), start=1):
            test.case_number = idx
            test.save(update_fields=['case_number'])
        for test in self.testset:
            test.refresh_from_db(fields=['case_number'])

    @transaction.atomic
    def appoint_case_number(self):
        # assign case number automatically to self.testset
        s = set(self.problem.repositorytest_set.values_list('case_number', flat=True))
        i = 1
        for test in self.testset:
            while i in s:
                i += 1
            test.case_number = i
            test.save(update_fields=['case_number'])
            s.add(i)
        self.fix_order()


class TestListView(PolygonProblemMixin, ListView):
    template_name = 'polygon/problem/test_list.jinja2'
    context_object_name = 'test_list'

    def get_queryset(self):
        return self.problem.repositorytest_set.all()


class TestCreateView(PolygonProblemMixin, FormView):
    template_name = 'polygon/problem/test_create.jinja2'
    form_class = TestCreateForm

    @staticmethod
    def get_cmd_from_commands(txt):
        ret1 = []
        for x in filter(lambda x: x, map(lambda x: x.strip(), txt.split('\n'))):
            if ' ' not in x:
                a, b = x.strip(), ''
            else:
                a, b = map(lambda y: y.strip(), x.split(' ', 1))
            ret1.append((a, b))
        return ret1

    @staticmethod
    def split_files(txt):
        txt = txt.strip()
        if re.match(r'{(.*)}', txt):
            lst = filter(lambda x: x, map(lambda x: x.strip(), txt[1:-1].split(',')))
        else:
            lst = [txt]
        return list(filter(lambda x: x, lst))

    @staticmethod
    def split_args(args):
        return list(filter(lambda x: x, map(lambda x: x.strip(), args)))

    @staticmethod
    def generate(gen, args, files, tests, timeout):
        generator = Program(gen)
        if len(files) == 0:
            files = [generator.default_output_path]
        else:
            files = list(map(lambda x: path.join(generator.workspace, x), files))
        if len(files) != len(tests):
            raise RepositoryException("File count and test count differs")
        try:
            generator.run(args, timeout)
            for file, test in zip(files, tests):
                tm = TestManager(test)
                shutil.copy(file, tm.input_path)
                tm.refresh_test_preview()
        except RepositoryException as e:
            for test in tests:
                test.invalid = str(e)
                test.save(update_fields=['invalid'])

    @staticmethod
    def threaded_generate(data):
        with Pool(max(os.cpu_count() // 4, 1)) as p:
            p.starmap(TestCreateView.generate, data)

    def form_valid(self, form):
        def sort_new_tests():
            tsm = TestSetManager(new_tests)
            if form.cleaned_data["case_order"].isdigit():
                tsm.move_after(int(form.cleaned_data["case_order"]))
            else:
                tsm.appoint_case_number()

        create_method = form.cleaned_data["create_method"]
        new_tests = []
        if create_method == 'manual':
            try:
                test = self.problem.repositorytest_set.create(show_in_samples=form.cleaned_data["show_in_samples"],
                                                              show_in_pretests=form.cleaned_data["show_in_pretests"],
                                                              show_in_tests=form.cleaned_data["show_in_tests"],
                                                              manual_output_lock=form.cleaned_data[
                                                                  "manual_output_lock"],
                                                              description=form.cleaned_data["description"],
                                                              group=form.cleaned_data["group"])
                new_tests.append(test)
                tm = TestManager(test)
                tm.write_input(form.cleaned_data["input"])
                tm.write_output(form.cleaned_data["output"])
                tm.refresh_test_preview()
                sort_new_tests()
            except KeyError:
                raise RepositoryException("Missing input and output")
        elif create_method == "gen":
            commands = self.get_cmd_from_commands(form.cleaned_data["generate_cmd"])
            data = []
            for exe, cmd in commands:
                try:
                    generator = self.problem.repositorysource_set.get(name=exe)
                    if '>' in cmd:
                        args, files = cmd.split('>')
                    else:
                        args, files = cmd, ''
                    args = self.split_args(args)
                    files = self.split_files(files)
                    local_test = []
                    for i in range(max(len(files), 1)):
                        test = self.problem.repositorytest_set.create(group=form.cleaned_data["group"],
                                                                      description="Generate by \"%s %s\"" % (
                                                                      exe, cmd),
                                                                      input_preview=GENERATE_PROMPT,
                                                                      output_preview=GENERATE_PROMPT)
                        local_test.append(test)
                        new_tests.append(test)
                    data.append((generator, args, files, local_test,
                                 self.problem.time_limit / 1000 * 10 * max(len(files), 1)))  # given 10 times time limit
                except RepositorySource.DoesNotExist:
                    pass

                sort_new_tests()
                Thread(target=self.threaded_generate, args=(data,)).start()
        else:
            try:
                tmp_dir = get_tmp_directory(self.problem.pk)
                makedirs(tmp_dir)
                with zipfile.ZipFile(form.cleaned_data["upload"]) as myZip:
                    myZip.extractall(path=tmp_dir)
                zip_filename = form.cleaned_data["upload"].name
            except Exception as e:
                raise RepositoryException("Illegal zipfile uploaded: %s" % str(e))
            if create_method == "input":
                with transaction.atomic():
                    for inf in sort_input_list_from_directory(tmp_dir):
                        test = self.problem.repositorytest_set.create(
                            description="From \"%s\" in \"%s\"" % (inf, zip_filename),
                            group=form.cleaned_data["group"])
                        new_tests.append(test)
                        tm = TestManager(test)
                        shutil.copy(path.join(tmp_dir, inf), tm.input_path)
                        tm.refresh_test_preview()
            elif create_method == "match":
                with transaction.atomic():
                    for inf, ouf in sort_data_list_from_directory(tmp_dir):
                        test = self.problem.repositorytest_set.create(
                            description="From \"%s\" in \"%s\"" % (inf, zip_filename),
                            group=form.cleaned_data["group"])
                        new_tests.append(test)
                        tm = TestManager(test)
                        shutil.copy(path.join(tmp_dir, inf), tm.input_path)
                        shutil.copy(path.join(tmp_dir, ouf), tm.output_path)
                        tm.refresh_test_preview()
            else:
                raise RepositoryException("Unrecognized choice '%s'" % create_method)
            sort_new_tests()

        messages.add_message(self.request, messages.SUCCESS, '%d test(s) has been added successfully' % len(new_tests))
        return redirect(self.request.path)

    def get_success_url(self):
        return self.request.path


class TestFullTextView(PolygonProblemMixin, View):
    def get(self, *args, **kwargs):
        try:
            id = self.request.GET['id']
            test = self.problem.repositorytest_set.get(pk=id)
            tm = TestManager(test)
            if self.request.GET['t'] == 'in':
                p = tm.input_path
            elif self.request.GET['t'] == 'out':
                p = tm.output_path
            else:
                raise KeyError
            return HttpResponse(tm.read_binary(p), content_type='text/plain; charset=utf-8')
        except (KeyError, RepositoryTest.DoesNotExist):
            raise PermissionDenied


class TestRefreshView(PolygonProblemMixin, View):
    @staticmethod
    def threaded_post(testset):
        with Pool(max(os.cpu_count() // 4, 1)) as p:
            p.map(TestManager.validate_input_and_generate_output, testset)

    def post(self, *args, **kwargs):
        """
        This will:
        1. Fix order
        2. Regenerate input for generated tests
        3. Regenerate output for unlocked tests
        """
        TestSetManager(self.problem.repositorytest_set.all()).fix_order()
        self.problem.repositorytest_set.all().update(input_preview=GENERATE_PROMPT,
                                                     output_preview=GENERATE_PROMPT)
        Thread(target=self.threaded_post, args=(list(self.problem.repositorytest_set.all()),)).start()
        return HttpResponse()
