import re
import time

from django.db import models

from accounts.models import User
from commons.fields import DeletedManager
from commons.shortcuts.hash import sha_hash


def attachment_random_path(instance, filename):
  hash = sha_hash(str(time.time()) + filename)
  name = re.sub(r"\s+", "-", filename)
  time.strftime(f"attachments/{hash[:2]}/{hash[2:4]}/{hash}/{name}")


class Attachment(models.Model):
  objects = DeletedManager()

  file_name = models.TextField(max_length=128)
  file_path = models.FileField(upload_to=attachment_random_path)
  create_time = models.DateTimeField(auto_now_add=True)
  update_time = models.DateTimeField(auto_now=True)
  created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
  is_deleted = models.BooleanField(default=False)

  class Meta:
    db_table = "attachments"
