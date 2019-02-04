from django.db import models

from accounts.models import User


class Package(models.Model):
  created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
  create_time = models.DateTimeField(auto_now_add=True)
  dir_name = models.TextField()
  remote_problem_id = models.TextField(max_length=64)
  status = models.IntegerField(default=-1, choices=(
    (-1, 'Pending'),
    (0, 'OK'),
    (1, 'Failed')
  ))
  running_time = models.FloatField(null=True)
  short_name = models.TextField(null=True, blank=True)
  revision = models.IntegerField(null=True)
  size = models.FloatField(null=True)
