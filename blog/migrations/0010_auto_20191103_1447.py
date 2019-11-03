# Generated by Django 2.2.3 on 2019-11-03 14:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('problem', '0033_delete_commentsubmission'),
        ('submission', '0032_auto_20190317_0852'),
        ('contest', '0049_auto_20190317_0852'),
        ('blog', '0009_auto_20190315_1134'),
    ]

    operations = [
        migrations.AddField(
            model_name='blog',
            name='contest',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='contest.Contest'),
        ),
        migrations.AddField(
            model_name='blog',
            name='is_reward',
            field=models.BooleanField(default=False, verbose_name='是否是悬赏'),
        ),
        migrations.AddField(
            model_name='blog',
            name='problem',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='problem.Problem'),
        ),
        migrations.AddField(
            model_name='blog',
            name='submission',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='submission.Submission'),
        ),
    ]
