import subprocess
import resource
from os import path, makedirs

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView
from django.views.generic import ListView
from django.views.generic import UpdateView

from polygon.models import RepositorySource
from polygon.problem.exception import RepositoryException
from polygon.problem.forms import SourceEditForm
from polygon.problem.sync import sync_problem_to_servers
from polygon.problem.utils import LANG_CONFIG
from polygon.problem.views import PolygonProblemMixin
from problem.models import SpecialProgram
from utils import random_string
from utils.hash import code_hash


class SourceCodeView(PolygonProblemMixin, View):
    def get(self, *args, **kwargs):
        try:
            code = SpecialProgram.objects.get(fingerprint=getattr(self.problem, self.request.GET.get('t', ''))).code
            return HttpResponse(code, content_type='text/plain; charset=utf-8')
        except Exception as e:
            print(e)
            return HttpResponse()


class SourceListView(PolygonProblemMixin, ListView):
    template_name = 'polygon/problem/source_list.jinja2'
    context_object_name = 'source_list'

    def get_queryset(self):
        return self.problem.repositorysource_set.all()

    def get_select_list(self, t):
        ret = [('', 'Use Default')]
        ret += map(lambda x: (x.name, x.name), self.problem.repositorysource_set.filter(tag=t))
        ret += map(lambda x: (x.fingerprint, x.filename + ' (cloud)'),
                   SpecialProgram.objects.filter(fingerprint=getattr(self.problem, t), builtin=False))
        ret += map(lambda x: (x.fingerprint, x.filename + ' (builtin)'),
                   SpecialProgram.objects.filter(builtin=True, category=t).order_by('filename'))
        return ret

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['checkers'] = self.get_select_list('checker')
        data['validators'] = self.get_select_list('validator')
        data['interactors'] = self.get_select_list('interactor')
        return data

    def post(self, *args, **kwargs):
        # I don't know why this is here. This post is to select checker and etc. for a problem
        ts = ['checker', 'validator', 'interactor']
        try:
            for t in ts:
                fingerprint = self.request.POST.get(t, '')
                if fingerprint == '':
                    setattr(self.problem, t, '')
                    continue
                if not SpecialProgram.objects.filter(fingerprint=fingerprint).exists():
                    file_name = fingerprint
                    source = self.problem.repositorysource_set.get(name=file_name)
                    fingerprint = code_hash(source.code, source.lang)
                    if not SpecialProgram.objects.filter(fingerprint=fingerprint).exists():
                        SpecialProgram.objects.create(fingerprint=fingerprint, lang=source.lang, filename=file_name,
                                                      code=source.code, category=t)
                setattr(self.problem, t, fingerprint)
            sync_problem_to_servers(self.problem)
            self.problem.save(update_fields=ts)
        except KeyError:
            raise RepositoryException("Post info not complete")
        except RepositorySource.DoesNotExist as e:
            raise RepositoryException(str(e))
        return redirect(self.request.path)


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
        except FileNotFoundError:
            raise RepositoryException("Compiler not found. Contact admin.")

    @property
    def random_fingerprint(self):
        if not hasattr(self, '_random_fingerprint'):
            self._random_fingerprint = random_string(6)
        return self._random_fingerprint

    @property
    def default_output_path(self):
        return path.join(self.workspace, '%s.out' % self.random_fingerprint)

    @property
    def default_error_path(self):
        return path.join(self.workspace, '%s.err' % self.random_fingerprint)

    @staticmethod
    def setlimits():
        resource.setrlimit(resource.RLIMIT_FSIZE, (536870912, 536870912))

    def run(self, additional_args, timeout, input_path=None):
        if not path.exists(self.exe_path):
            self.compile()
        inf = open(input_path, 'r') if input_path is not None else None
        with open(self.default_output_path, 'w') as ouf, open(self.default_error_path, 'w') as err:
            p = subprocess.Popen(self.execute_command + additional_args, stdin=inf, stdout=ouf, stderr=err,
                                 preexec_fn=self.setlimits, cwd=self.workspace, )
            try:
                returncode = p.wait(timeout)
                if returncode:
                    raise RepositoryException('Non-zero exit code %s' % returncode)
            except subprocess.TimeoutExpired:
                raise RepositoryException("Process timed out after %d second(s)" % timeout)
