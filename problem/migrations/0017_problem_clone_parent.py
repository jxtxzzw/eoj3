# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-09 15:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
  dependencies = [
    ('problem', '0016_auto_20180704_0704'),
  ]

  operations = [
    migrations.AddField(
      model_name='problem',
      name='clone_parent',
      field=models.PositiveIntegerField(default=0),
    ),
  ]
