# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-10-06 23:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0016_contestparticipant_is_disabled'),
    ]

    operations = [
        migrations.AddField(
            model_name='contest',
            name='case_public',
            field=models.BooleanField(default=False, verbose_name='Cases can be downloaded if paid.'),
        ),
    ]
