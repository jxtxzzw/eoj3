# Generated by Django 2.1.7 on 2019-03-15 11:34

from django.db import migrations, models


class Migration(migrations.Migration):
  dependencies = [
    ('contest', '0047_auto_20181113_2038'),
  ]

  operations = [
    migrations.AlterField(
      model_name='contest',
      name='allowed_lang',
      field=models.CharField(default='c,cc14,cc17,cpp,java,pas,py2,pypy,pypy3,python,scala,text', max_length=192,
                             verbose_name='允许语言'),
    ),
  ]
