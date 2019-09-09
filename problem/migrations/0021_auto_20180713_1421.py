# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-13 14:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
  dependencies = [
    ('problem', '0020_auto_20180712_1707'),
  ]

  operations = [
    migrations.AlterField(
      model_name='specialprogram',
      name='lang',
      field=models.CharField(
        choices=[('c', 'C'), ('cpp', 'C++11'), ('python', 'Python 3'), ('java', 'Java 8'), ('cc14', 'C++14'),
                 ('cc17', 'C++17'), ('cs', 'C#'), ('py2', 'Python 2'), ('scipy', 'Python (SCI)'), ('php', 'PHP 7'),
                 ('perl', 'Perl'), ('hs', 'Haskell'), ('js', 'Javascript'), ('ocaml', 'OCaml'), ('pypy', 'PyPy'),
                 ('pypy3', 'PyPy 3'), ('pas', 'Pascal'), ('rs', 'Rust'), ('scala', 'Scala'), ('text', 'Text')],
        default='cc14', max_length=12, verbose_name='language'),
    ),
  ]
