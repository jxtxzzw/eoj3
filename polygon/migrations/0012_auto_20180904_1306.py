# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-09-04 13:06
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('problem', '0022_taginfo_parent_id'),
        ('polygon', '0011_auto_20180713_1421'),
    ]

    operations = [
        migrations.CreateModel(
            name='FavoriteProblem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='polygon_problems_favorite_by', to='problem.Problem')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='polygon_favorite_problems', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='favoriteproblem',
            unique_together=set([('user', 'problem')]),
        ),
    ]
