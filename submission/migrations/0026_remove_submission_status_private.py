# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-09-14 22:37
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
  dependencies = [
    ('submission', '0025_auto_20180913_1635'),
  ]

  operations = [
    migrations.RemoveField(
      model_name='submission',
      name='status_private',
    ),
  ]
