# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-11-20 12:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
  dependencies = [
    ('submission', '0011_submission_ip'),
  ]

  operations = [
    migrations.AddField(
      model_name='submission',
      name='cheat_tag',
      field=models.IntegerField(default=0),
    ),
  ]
