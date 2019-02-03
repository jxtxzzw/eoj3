import datetime
from base64 import b64decode

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, HttpResponse
from django.template import loader, Context

from accounts.models import User
from contests.models import ContestProblem
from problems.dispatcher.models import Server
from .models import Submission, SubmissionReport
from submission.util import SubmissionStatus


@login_required
def submission_code_api(request):
    c = request.GET.get('c')
    p = request.GET.get('p')
    try:
        if c:
            p = ContestProblem.objects.get(contest_id=c, identifier=p).problem_id
            submission = request.user.submission_set.filter(contest_id=c, problem_id=p).first()
        else:
            submission = request.user.submission_set.filter(problem_id=p).first()
        code = submission.code
    except (AttributeError, ValueError, ContestProblem.DoesNotExist):
        code = ''
    return HttpResponse(code, content_type='text_plain')


def render_submission(submission: Submission, permission=1, hide_problem=False, show_percent=False,
                      rejudge_available=True) -> str:
    if permission == 0:
        raise PermissionDenied
    if permission == 1 and submission.status != SubmissionStatus.COMPILE_ERROR and submission.status_message:
        submission.status_message = ''
    try:
        judge_server = Server.objects.get(pk=submission.judge_server).name
    except:
        judge_server = ''
    t = loader.get_template('components/single_submission.jinja2')
    c = Context({'submission': submission, 'hide_problem': hide_problem, 'show_percent': show_percent,
                 'server': judge_server, 'rejudge_authorized': permission >= 2 and rejudge_available})
    return t.render(c)


def render_submission_report(pk):
    try:
        report = SubmissionReport.objects.get(submission_id=pk)
        lines = report.content.strip().split("\n")
        ans = []
        for line in lines:
            meta, *b64s = line.split('|')
            if len(b64s) == 4:
                input, output, answer, checker = map(lambda txt: b64decode(txt.encode()).decode(), b64s)
                stderr = ""
            else:
                input, output, stderr, answer, checker = map(lambda txt: b64decode(txt.encode()).decode(), b64s)
            ans.append({'meta': meta, 'input': input, 'output': output, 'stderr': stderr,
                        'answer': answer, 'checker': checker})
        t = loader.get_template('components/submission_report.jinja2')
        return t.render(Context({'testcases': ans}))
    except (SubmissionReport.DoesNotExist, ValueError):
        return ''


def submission_count_api(request, name):
    user = get_object_or_404(User, username=name)
    now = datetime.datetime.now()
    one_year_ago = now.replace(year=now.year - 1)
    submissions = Submission.objects.filter(author=user, create_time__gte=one_year_ago)
    result = {submission.create_time.timestamp(): 1 for submission in submissions}
    return JsonResponse(result)
