from django.db import models

from accounts.models import User


class Package(models.Model):
  created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
  create_time = models.DateTimeField(auto_now_add=True)


class CodeforcesPackage(Package):
  dir_name = models.CharField(max_length=64)
  remote_problem_id = models.CharField(max_length=64)
  status = models.IntegerField(default=-1, choices=(
    (-1, 'Pending'),
    (0, 'OK'),
    (1, 'Failed')
  ))
  running_time = models.FloatField(null=True)
  short_name = models.CharField(null=True, blank=True, max_length=192)
  revision = models.IntegerField(null=True)
  size = models.FloatField(null=True)
