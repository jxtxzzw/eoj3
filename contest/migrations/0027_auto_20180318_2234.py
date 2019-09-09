# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2018-03-18 22:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
  dependencies = [
    ('contest', '0026_auto_20180318_2152'),
  ]

  operations = [
    migrations.AddField(
      model_name='contest',
      name='ip_sensitive',
      field=models.BooleanField(default=False, verbose_name="Bind IP to user's account after first login"),
    ),
    migrations.AddField(
      model_name='contestparticipant',
      name='ip_address',
      field=models.GenericIPAddressField(blank=True, null=True),
    ),
  ]
