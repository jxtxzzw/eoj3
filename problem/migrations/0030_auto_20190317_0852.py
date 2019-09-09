# Generated by Django 2.1.7 on 2019-03-17 08:52

from django.db import migrations, models


class Migration(migrations.Migration):
  dependencies = [
    ('problem', '0029_auto_20190315_1134'),
  ]

  operations = [
    migrations.AlterField(
      model_name='specialprogram',
      name='lang',
      field=models.CharField(
        choices=[('c', 'C'), ('cpp', 'C++11'), ('cc14', 'C++14'), ('cc17', 'C++17'), ('py2', 'Python 2'),
                 ('python', 'Python 3'), ('pypy', 'PyPy'), ('pypy3', 'PyPy 3'), ('java', 'Java 8'), ('pas', 'Pascal'),
                 ('text', 'Text')], default='cc14', max_length=12, verbose_name='language'),
    ),
  ]
