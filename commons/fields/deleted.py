from django.db import models


class DeletedManager(models.Manager):
  def get_queryset(self):
    return super(DeletedManager, self).get_queryset().filter(is_deleted=False)
