# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2018-01-07 12:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
  dependencies = [
    ('submission', '0015_remove_submission_judge_server'),
  ]

  operations = [
    migrations.AlterField(
      model_name='submission',
      name='lang',
      field=models.CharField(
        choices=[('c', 'C'), ('cpp', 'C++11'), ('python', 'Python 3'), ('java', 'Java 8'), ('cc14', 'C++14'),
                 ('cs', 'C#'), ('py2', 'Python 2'), ('php', 'PHP 7'), ('perl', 'Perl'), ('hs', 'Haskell'),
                 ('js', 'Javascript'), ('ocaml', 'OCaml'), ('pypy', 'PyPy'), ('pas', 'Pascal'), ('rs', 'Rust'),
                 ('scala', 'Scala')], default='cpp', max_length=12, verbose_name='Language'),
    ),
  ]
