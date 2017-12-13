from datetime import datetime

from dispatcher.models import Server
from polygon.problem.exception import RepositoryException
from problem.models import Problem, SpecialProgram
from problem.tasks import upload_problem_to_judge_server


def sync_problem_to_servers(problem: Problem):
    for server in Server.objects.filter(enabled=True).all():
        if not upload_problem_to_judge_server(problem, server):
            raise RepositoryException("Upload to judge server failed. Contact admin.")
        server.last_synchronize_time = datetime.now()
        server.save(update_fields=['last_synchronize_time'])
