# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2018-01-22 00:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
  dependencies = [
    ('account', '0015_auto_20180113_1347'),
  ]

  operations = [
    migrations.AddField(
      model_name='user',
      name='rating',
      field=models.IntegerField(default=0),
    ),
  ]
