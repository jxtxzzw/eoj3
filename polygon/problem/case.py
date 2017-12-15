import io
import re
from os import path, makedirs

import chardet
from django.conf import settings
from django.shortcuts import redirect
from django.views.generic import CreateView
from django.views.generic import ListView

from polygon.models import RepositoryTest
from polygon.problem.exception import RepositoryException
from polygon.problem.forms import TestCreateForm
from polygon.problem.views import PolygonProblemMixin
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
        with open(path, 'rb') as inf:
            b = TextFormatter.well_form_binary(inf.read())
        with open(path, 'w') as ouf:
            ouf.write(b)


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

    def refresh_test_io(self):
        if self.test.problem.well_form_policy:
            TextFormatter.format_file(self.input_path)
            TextFormatter.format_file(self.output_path)
        self.test.input_preview = self.read_abstract(self.input_path)
        self.test.output_preview = self.read_abstract(self.output_path)
        self.test.fingerprint = case_hash(self.problem_id, self.read_binary(self.input_path),
                                          self.read_binary(self.output_path))
        self.test.size = path.getsize(self.input_path) + path.getsize(self.output_path)
        self.test.save(update_fields=['input_preview', 'output_preview', 'fingerprint', 'size'])

    def write_input(self, txt):
        with open(self.input_path, 'w') as f:
            f.write(txt)

    def write_output(self, txt):
        with open(self.output_path, 'w') as f:
            f.write(txt)

    @staticmethod
    def read_abstract(path):
        try:
            with open(path, 'r') as f:
                s = f.read(24)
                if f.read(1):
                    s += ' ...'
            return s
        except UnicodeDecodeError as e:
            return str(e)
        except FileNotFoundError:
            raise RepositoryException("Test path '%s' not found" % path)

    @staticmethod
    def read_binary(path):
        try:
            with open(path, 'rb') as f:
                return f.read()
        except FileNotFoundError:
            raise RepositoryException("Test path '%s' not found" % path)


class TestListView(PolygonProblemMixin, ListView):
    template_name = 'polygon/problem/test_list.jinja2'
    context_object_name = 'test_list'

    def get_queryset(self):
        return self.problem.repositorytest_set.all()


class TestCreateView(PolygonProblemMixin, CreateView):
    template_name = 'polygon/problem/source_edit.jinja2'
    form_class = TestCreateForm

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.problem = self.problem
        instance.save()
        tm = TestManager(instance)
        tm.write_input(form.cleaned_data["input"])
        tm.write_output(form.cleaned_data["output"])
        tm.refresh_test_io()
        return redirect(self.request.path)

    def get_success_url(self):
        return self.request.path
