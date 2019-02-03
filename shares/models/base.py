from datetime import timedelta, datetime

from django.db import models

from accounts.models import User
from commons.fields import DeletedManager


class Share(models.Model):
  objects = DeletedManager()

  created_by = models.ForeignKey(User, null=True, related_name="created_shares", on_delete=models.SET_NULL)
  public_access = models.PositiveIntegerField(choices=(
    (0, '只有自己可见'),
    (10, '对受邀用户可见'),
    (20, '对所有人可见')
  ), default=20)
  create_time = models.DateTimeField(auto_now_add=True)
  update_time = models.DateTimeField(auto_now=True)
  invited_users = models.ManyToManyField(User, related_name="invited_shares")
  is_deleted = models.BooleanField(default=False)

  class Meta:
    db_table = "shares"
