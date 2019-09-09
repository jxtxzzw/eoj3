# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-03-30 21:27
from __future__ import unicode_literals

import django.contrib.auth.models
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
  initial = True

  dependencies = [
    ('auth', '0008_alter_user_username_max_length'),
  ]

  operations = [
    migrations.CreateModel(
      name='User',
      fields=[
        ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
        ('password', models.CharField(max_length=128, verbose_name='password')),
        ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
        ('is_superuser', models.BooleanField(default=False,
                                             help_text='Designates that this user has all permissions without explicitly assigning them.',
                                             verbose_name='superuser status')),
        ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
        ('last_name', models.CharField(blank=True, max_length=30, verbose_name='last name')),
        ('is_staff',
         models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.',
                             verbose_name='staff status')),
        ('is_active', models.BooleanField(default=True,
                                          help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.',
                                          verbose_name='active')),
        ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
        ('username',
         models.CharField(error_messages={'unique': 'A user with that username already exists.'}, max_length=30,
                          unique=True, verbose_name='username')),
        ('email',
         models.EmailField(error_messages={'unique': 'This email has already been used.'}, max_length=192, unique=True,
                           verbose_name='email')),
        ('privilege',
         models.CharField(choices=[('user', 'Regular User'), ('admin', 'Admin'), ('root', 'Root')], default='user',
                          max_length=12)),
        ('school', models.CharField(blank=True, max_length=192, verbose_name='school')),
        ('create_time', models.DateTimeField(auto_now_add=True)),
        ('nickname', models.CharField(blank=True, max_length=192, verbose_name='nickname')),
        ('magic', models.CharField(blank=True,
                                   choices=[('red', 'Red'), ('green', 'Green'), ('cyan', 'Cyan'), ('blue', 'Blue'),
                                            ('purple', 'Purple'), ('orange', 'Orange'), ('grey', 'Grey')],
                                   max_length=18, verbose_name='magic')),
        ('show_tags', models.BooleanField(default=True, verbose_name='show tags')),
        ('preferred_lang',
         models.CharField(choices=[('c', 'C'), ('cpp', 'C++'), ('python', 'Python'), ('java', 'Java')], default='cpp',
                          max_length=12, verbose_name='preferred language')),
        ('groups', models.ManyToManyField(blank=True,
                                          help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
                                          related_name='user_set', related_query_name='user', to='auth.Group',
                                          verbose_name='groups')),
        ('user_permissions',
         models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set',
                                related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
      ],
      options={
        'verbose_name': 'user',
        'abstract': False,
        'verbose_name_plural': 'users',
      },
      managers=[
        ('objects', django.contrib.auth.models.UserManager()),
      ],
    ),
  ]
