from django.db import models

from commons.fields import DeletedManager


class Server(models.Model):
  objects = DeletedManager()

  name = models.TextField()
  ip_address = models.GenericIPAddressField()
  port_number = models.PositiveIntegerField()
  public_key = models.TextField()
  private_key = models.TextField()
  concurrency = models.PositiveIntegerField()
  create_time = models.DateTimeField(auto_now_add=True)
  update_time = models.DateTimeField(auto_now=True)
  is_deleted = models.BooleanField(default=False)

  def __str__(self):
    return self.name

  class Meta:
    db_table = "servers"

  @property
  def http_address(self):
    return f"http://{self.ip_address}:{self.port_number}"
