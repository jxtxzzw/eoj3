from django.db import models

from accounts.models import User
from commons.fields import VersionNumberField


class AppUpdate(models.Model):
  file = models.FileField(upload_to="app/%Y%m%d")
  version = VersionNumberField()
  description = models.TextField()
  create_time = models.DateTimeField(auto_now_add=True)

  class Meta:
    db_table = "app_update"
