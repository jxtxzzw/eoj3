from math import log10

from problems.models import UserStatus, TagInfo, Problem
from submission.models import Submission
from submission.util import SubmissionStatus
from commons.utils import is_problem_manager


def invalidate_problem(problem: Problem, save=True):
    query_list = list(problem.submission_set.all().values("author_id", "status"))
    ac_list = list(filter(lambda x: x["status"] == SubmissionStatus.ACCEPTED, query_list))
    problem.ac_user_count = len(set(map(lambda x: x["author_id"], ac_list)))
    problem.total_user_count = len(set(map(lambda x: x["author_id"], query_list)))
    problem.ac_count = len(ac_list)
    problem.total_count = len(query_list)
    problem.reward =  max(min(5 - (.02 * problem.ac_ratio + .03 * problem.ac_user_ratio) * min(log10(problem.ac_user_count + 1), 1.2)
                             + max(6 - 2 * log10(problem.ac_user_count + 1), 0), 9.9), 0.1)
    for field in problem._meta.local_fields:
        if field.name == "update_time":
            field.auto_now = False
    if save:
        problem.save(update_fields=["ac_user_count", "total_user_count", "ac_count", "total_count", "reward"])


def invalidate_user(user_id, contest_id=0):
    if contest_id is None:
        contest_id = 0
    if contest_id:
        invalidate_user(user_id)

    if contest_id:
        submission_filter = Submission.objects.filter(author_id=user_id, contest_id=contest_id).all()
    else:
        submission_filter = Submission.objects.filter(author_id=user_id).all()
    ac_filter = submission_filter.filter(status__in=[SubmissionStatus.ACCEPTED, SubmissionStatus.PRETEST_PASSED]).all()

    total_count = submission_filter.count()
    total_list = list(submission_filter.order_by().values_list("problem_id", flat=True).distinct())
    accept_count = ac_filter.count()
    accept_list = list(ac_filter.order_by().values_list("problem_id", flat=True).distinct())
    accept_diff = len(accept_list)

    us, created = UserStatus.objects.get_or_create(user_id=user_id, contest_id=contest_id,
                                                   defaults={
                                                       "total_count": total_count,
                                                       "total_list": ",".join(map(str, total_list)),
                                                       "ac_count": accept_count,
                                                       "ac_list": ",".join(map(str, accept_list)),
                                                       "ac_distinct_count": accept_diff
                                                   })
    if not created:
        us.total_count = total_count
        us.total_list = ",".join(map(str, total_list))
        us.ac_count = accept_count
        us.ac_list = ",".join(map(str, accept_list))
        us.ac_distinct_count = accept_diff
        us.save()
    return us


def _get_or_invalidate_user(user_id, contest_id, field_name):
    try:
        return getattr(UserStatus.objects.get(user_id=user_id, contest_id=contest_id), field_name)
    except:
        return getattr(invalidate_user(user_id, contest_id), field_name)


def get_accept_submission_count(user_id, contest_id=0):
    return _get_or_invalidate_user(user_id, contest_id, "ac_count")


def get_accept_problem_count(user_id, contest_id=0):
    return _get_or_invalidate_user(user_id, contest_id, "ac_distinct_count")


def get_accept_problem_list(user_id, contest_id=0):
    t = _get_or_invalidate_user(user_id, contest_id, "ac_list")
    if not t: return []
    return list(map(int, t.split(',')))


def get_total_submission_count(user_id, contest_id=0):
    return _get_or_invalidate_user(user_id, contest_id, "total_count")


def get_attempted_problem_list(user_id, contest_id=0):
    t = _get_or_invalidate_user(user_id, contest_id, "total_list")
    if not t: return []
    return list(map(int, t.split(',')))


def is_problem_accepted(user, problem):
    return is_problem_manager(user, problem) or (user.is_authenticated and
           user.submission_set.filter(problem=problem, status=SubmissionStatus.ACCEPTED).exists())


def get_children_tag_id(tag: int = -1):
    tags = {tag}
    while True:
        adds = set(TagInfo.objects.filter(parent_id__in=tags).values_list("tag_id", flat=True))
        if (adds & tags) == adds:
            break
        tags |= adds
    return tags
