import io
import re
import shutil
import zipfile
from os import path, makedirs

import chardet
from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect
from django.views.generic import FormView
from django.views.generic import ListView

from polygon.models import RepositorySource
from polygon.problem.exception import RepositoryException
from polygon.problem.forms import TestCreateForm
from polygon.problem.utils import get_tmp_directory
from polygon.problem.views import PolygonProblemMixin
from utils.file_preview import sort_data_list_from_directory, sort_input_list_from_directory
from utils.hash import case_hash


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
        self.problem_id = test.problem_id
        self.test = test
        makedirs(self.workspace, exist_ok=True)

    @property
    def workspace(self):
        return path.join(settings.REPO_DIR, str(self.problem_id), 'tests')

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
        self.error = ''
        if self.test.problem.well_form_policy:
            TextFormatter.format_file(self.input_path)
            TextFormatter.format_file(self.output_path)
        self.test.input_preview = self.read_abstract(self.input_path)
        self.test.output_preview = self.read_abstract(self.output_path)
        self.test.fingerprint = case_hash(self.problem_id, self.read_binary(self.input_path),
                                          self.read_binary(self.output_path))
        self.test.size = self.get_size(self.input_path) + self.get_size(self.output_path)
        self.test.error = self.error
        self.test.save(update_fields=['input_preview', 'output_preview', 'fingerprint', 'size', 'error'])

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
            self.error = "Test not found: %s" % path.split(file)[1]
            return self.error

    def read_binary(self, file):
        try:
            with open(file, 'rb') as f:
                return f.read()
        except FileNotFoundError:
            self.error = "Test not found: %s" % path.split(file)[1]
            return self.error


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

    def form_valid(self, form):
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
            except KeyError:
                raise RepositoryException("Missing input and output")
        elif create_method == "gen":
            except_name = ''
            try:
                commands = self.get_cmd_from_commands(form.cleaned_data["generate_cmd"])
                with transaction.atomic():
                    for exe, cmd in commands:
                        except_name = exe
                        test = self.problem.repositorytest_set.create(group=form.cleaned_data["group"],
                                                                      description="Generate by \"%s %s\"" % (exe, cmd))
                        new_tests.append(test)
                        test.generator = self.problem.repositorysource_set.get(name=exe)
                        test.generate_args = cmd
                        test.save(update_fields=['generator_id', 'generate_args'])
                        tm = TestManager(test)
                        tm.refresh_test_preview()
            except RepositorySource.DoesNotExist:
                raise RepositoryException("Illegal source name '%s'" % except_name)
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

        tsm = TestSetManager(new_tests)
        if form.cleaned_data["case_order"].isdigit():
            tsm.move_after(int(form.cleaned_data["case_order"]))
        else:
            tsm.appoint_case_number()

        messages.add_message(self.request, messages.SUCCESS, '%d test(s) has been added successfully' % len(new_tests))
        return redirect(self.request.path)

    def get_success_url(self):
        return self.request.path
