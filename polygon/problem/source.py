import subprocess
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import CreateView
from django.views.generic import ListView
from django.views.generic import UpdateView
from os import path, makedirs

from polygon.models import RepositorySource
from polygon.problem.exception import RepositoryException
from polygon.problem.forms import SourceEditForm
from polygon.problem.utils import LANG_CONFIG
from polygon.problem.views import PolygonProblemMixin
from utils import random_string


class SourceListView(PolygonProblemMixin, ListView):
    template_name = 'polygon/problem/source_list.jinja2'
    context_object_name = 'source_list'

    def get_queryset(self):
        return self.problem.repositorysource_set.all()


class SourceCreateView(PolygonProblemMixin, CreateView):
    template_name = 'polygon/problem/source_edit.jinja2'
    form_class = SourceEditForm

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.author = self.request.user
        instance.workspace = random_string()
        instance.problem = self.problem
        Program(instance).compile()
        instance.save()
        return redirect(reverse('polygon:repo_source_list', kwargs=self.kwargs))

    def get_success_url(self):
        return self.request.path


class SourceEditView(PolygonProblemMixin, UpdateView):
    template_name = 'polygon/problem/source_edit.jinja2'
    form_class = SourceEditForm

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.workspace = random_string()
        Program(instance).compile()
        instance.save()
        return redirect(self.get_success_url())

    def get_object(self, queryset=None):
        return RepositorySource.objects.get(pk=self.kwargs['source'], problem_id=self.problem.pk)

    def get_success_url(self):
        return self.request.path


class Program:

    MAX_READ_SIZE = 2048

    @staticmethod
    def split_and_format_command(cmd, **kwargs):
        ret = []
        for x in cmd.split():
            ret.append(x.format(**kwargs))
        return ret

    def __init__(self, source: RepositorySource):
        self.source = source
        try:
            _config = LANG_CONFIG[self.source.lang]
            self.workspace = path.join(settings.REPO_DIR, str(source.problem_id), 'source', self.source.workspace)
            makedirs(self.workspace, exist_ok=True)
            self.code_path = path.join(self.workspace, _config['codeFile'])
            self.exe_path = path.join(self.workspace, _config['exeFile'])
            self.compiler_command = self.split_and_format_command(_config["compilerCmd"],
                                                                  workspace=self.workspace, code_path=self.code_path,
                                                                  exe_path=self.exe_path)
            self.execute_command = self.split_and_format_command(_config["executeCmd"],
                                                                 workspace=self.workspace, code_path=self.code_path,
                                                                 exe_path=self.exe_path)
        except KeyError:
            raise RepositoryException("Unrecognized language.")

    def compile(self):
        try:
            with open(self.code_path, 'w') as code_file:
                code_file.write(self.source.code)
            pr = subprocess.run(self.compiler_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
            if pr.returncode != 0:
                # something is wrong
                raise RepositoryException(pr.stdout.decode() or pr.stderr.decode())
        except subprocess.TimeoutExpired:
            raise RepositoryException("Compilation time limit exceeded.")
