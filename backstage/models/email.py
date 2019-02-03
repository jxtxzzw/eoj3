from django.db import models

from accounts.models import User


class Email(models.Model):
  title = models.TextField(max_length=192)
  content = models.TextField(blank=True)
  create_time = models.DateTimeField(auto_now_add=True)
  update_time = models.DateTimeField(auto_now=True)
  created_by = models.ForeignKey(User, null=True, related_name="sent_emails", on_delete=models.SET_NULL)
  recipients = models.ManyToManyField(User, through='EmailRecipient', related_name='received_emails')

  class Meta:
    db_table = "backstage_email"


class EmailRecipient(models.Model):
  email = models.ForeignKey(Email, on_delete=models.CASCADE)
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  status = models.IntegerField(choices=(
    (-1, 'Pending'),
    (0, 'OK'),
    (1, 'Failed')
  ), default=-1)
  create_time = models.DateTimeField(auto_now_add=True)
  update_time = models.DateTimeField(auto_now=True)
  error_message = models.TextField(blank=True)

  class Meta:
    db_table = "backstage_email_recipient"
