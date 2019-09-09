# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-04-06 16:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
  dependencies = [
    ('account', '0001_initial'),
  ]

  operations = [
    migrations.AddField(
      model_name='user',
      name='alien',
      field=models.CharField(blank=True, choices=[('ade.jpg', 'Ade'), ('cassie.png', 'Cassie'), ('chris.jpg', 'Chris'),
                                                  ('christian.jpg', 'Christian'), ('daniel.jpg', 'Daniel'),
                                                  ('elliot.jpg', 'Elliot'), ('elyse.png', 'Elyse'), ('eve.png', 'Eve'),
                                                  ('helen.jpg', 'Helen'), ('jenny.jpg', 'Jenny'), ('joe.jpg', 'Joe'),
                                                  ('justen.jpg', 'Justen'), ('kristy.png', 'Kristy'),
                                                  ('laura.jpg', 'Laura'), ('lena.png', 'Lena'),
                                                  ('lindsay.png', 'Lindsay'), ('mark.png', 'Mark'),
                                                  ('matt.jpg', 'Matt'), ('matthew.png', 'Matthew'),
                                                  ('molly.png', 'Molly'), ('nan.jpg', 'Nan'), ('nom.jpg', 'Nom'),
                                                  ('patrick.png', 'Patrick'), ('rachel.png', 'Rachel'),
                                                  ('steve.jpg', 'Steve'), ('stevie.jpg', 'Stevie'), ('tom.jpg', 'Tom'),
                                                  ('veronika.jpg', 'Veronika'), ('zoe.jpg', 'Zoe')], max_length=18,
                             verbose_name='alien'),
    ),
    migrations.AddField(
      model_name='user',
      name='motto',
      field=models.CharField(blank=True, max_length=192, verbose_name='motto'),
    ),
  ]
