# Generated by Django 2.1.3 on 2018-11-09 16:04

from django.db import migrations, models


class Migration(migrations.Migration):
  dependencies = [
    ('account', '0021_auto_20181106_1212'),
  ]

  operations = [
    migrations.AlterField(
      model_name='user',
      name='email_subscription',
      field=models.BooleanField(default=True, verbose_name='邮件订阅'),
    ),
  ]
