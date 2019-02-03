from django.db import models

from accounts.models import User


class UserStatus(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="submission_status")
  contest_id = models.PositiveIntegerField(db_index=True)
  total_count = models.PositiveIntegerField()
  total_list = models.TextField()
  ac_count = models.PositiveIntegerField()
  ac_distinct_count = models.PositiveIntegerField()
  ac_list = models.TextField()
  update_time = models.DateTimeField(auto_now=True)

  class Meta:
    unique_together = ('user', 'contest_id')
