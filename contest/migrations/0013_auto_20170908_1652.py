# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-09-08 16:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
  dependencies = [
    ('contest', '0012_auto_20170903_1245'),
  ]

  operations = [
    migrations.AlterField(
      model_name='contest',
      name='allow_code_share',
      field=models.IntegerField(choices=[(0, 'Forbidden'), (1, 'Share code after contest for AC users'),
                                         (2, 'Share code after contest for all'),
                                         (3, 'Share code after AC during contest')], default=1),
    ),
  ]
