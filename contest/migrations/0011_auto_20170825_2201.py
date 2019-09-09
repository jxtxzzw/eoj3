# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-08-25 22:01
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
  dependencies = [
    migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ('contest', '0010_auto_20170729_1034'),
  ]

  operations = [
    migrations.RemoveField(
      model_name='contest',
      name='contest_header',
    ),
    migrations.RemoveField(
      model_name='contest',
      name='rule',
    ),
    migrations.RemoveField(
      model_name='contestclarification',
      name='status',
    ),
    migrations.RemoveField(
      model_name='contestproblem',
      name='total_accept_number',
    ),
    migrations.RemoveField(
      model_name='contestproblem',
      name='total_submit_number',
    ),
    migrations.AddField(
      model_name='contest',
      name='allow_code_share',
      field=models.IntegerField(choices=[(0, 'Forbidden'), (1, 'Share code after contest for AC Users'),
                                         (2, 'Share code after contest for all'),
                                         (3, 'Share code after AC during contest')], default=1),
    ),
    migrations.AddField(
      model_name='contest',
      name='always_running',
      field=models.BooleanField(default=False),
    ),
    migrations.AddField(
      model_name='contest',
      name='last_counts',
      field=models.BooleanField(default=False, verbose_name='The last submission (instead of the best) will be scored'),
    ),
    migrations.AddField(
      model_name='contest',
      name='manager',
      field=models.ManyToManyField(related_name='managing_contests', to=settings.AUTH_USER_MODEL),
    ),
    migrations.AddField(
      model_name='contest',
      name='penalty_counts',
      field=models.BooleanField(default=True, verbose_name='Use penalty to sort participants with the same score'),
    ),
    migrations.AddField(
      model_name='contest',
      name='run_tests_during_contest',
      field=models.CharField(choices=[('none', 'None'), ('sample', 'Samples'), ('pretest', 'Pretests'), ('all', 'All')],
                             default='all', max_length=10),
    ),
    migrations.AddField(
      model_name='contest',
      name='scoring_method',
      field=models.CharField(choices=[('acm', 'ACM Rule'), ('oi', 'OI Rule'), ('cf', 'Codeforces Rule')], default='acm',
                             max_length=5),
    ),
    migrations.AddField(
      model_name='contest',
      name='standings_disabled',
      field=models.BooleanField(default=False, verbose_name="Users won't be able to see their standings in any case"),
    ),
    migrations.AddField(
      model_name='contest',
      name='standings_without_problem',
      field=models.BooleanField(default=False,
                                verbose_name='Show standings without a list of solved problems (often used when there is too many problems)'),
    ),
    migrations.AddField(
      model_name='contest',
      name='system_tested',
      field=models.BooleanField(default=False),
    ),
    migrations.AddField(
      model_name='contestclarification',
      name='important',
      field=models.BooleanField(default=False),
    ),
    migrations.AddField(
      model_name='contestproblem',
      name='weight',
      field=models.IntegerField(default=100),
    ),
    migrations.AlterField(
      model_name='contest',
      name='allowed_lang',
      field=models.CharField(default='c,cc14,cpp,cs,hs,java,js,ocaml,pas,perl,php,py2,pypy,python,rs', max_length=192,
                             verbose_name='Allowed languages'),
    ),
    migrations.AlterField(
      model_name='contest',
      name='end_time',
      field=models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True),
    ),
    migrations.AlterField(
      model_name='contest',
      name='freeze',
      field=models.BooleanField(default=False, verbose_name='The standings will be frozen'),
    ),
    migrations.AlterField(
      model_name='contest',
      name='standings_public',
      field=models.BooleanField(default=True, verbose_name='Make standings public even if the contest is private'),
    ),
    migrations.AlterField(
      model_name='contest',
      name='start_time',
      field=models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True),
    ),
    migrations.AlterField(
      model_name='contestclarification',
      name='time',
      field=models.DateTimeField(auto_now=True),
    ),
  ]
