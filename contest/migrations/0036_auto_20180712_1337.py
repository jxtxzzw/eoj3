# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-12 13:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
  dependencies = [
    ('contest', '0035_contest_pdf_statement'),
  ]

  operations = [
    migrations.AlterModelOptions(
      name='contestparticipant',
      options={'ordering': ('-score', 'penalty', 'star')},
    ),
    migrations.RenameField(
      model_name='contestparticipant',
      old_name='html_cache',
      new_name='detail_raw',
    ),
    migrations.RemoveField(
      model_name='contestparticipant',
      name='rank',
    ),
  ]
