from os import path

from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models

from account.models import User
from problem.models import Problem


class EditSession(models.Model):
    create_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User)
    fingerprint = models.CharField(max_length=64)
    problem = models.ForeignKey(Problem)
    last_synchronize = models.DateTimeField(blank=True)

    class Meta:
        ordering = ["-last_synchronize"]
        unique_together = ["user", "problem"]  # You can have only one session.


class Run(models.Model):
    STATUS_CHOICE = (
        (1, 'complete'),
        (0, 'running'),
        (-1, 'failed')
    )

    create_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User)
    status = models.IntegerField(choices=STATUS_CHOICE)
    label = models.TextField(blank=True)
    message = models.TextField(blank=True)


class NameValidator(RegexValidator):
    regex = r'^[A-Za-z0-9_-]{2,30}$'


class RepositorySource(models.Model):
    LANG_CHOICES = (
        ('cpp', 'C++'),
        ('java', 'Java'),
        ('python', 'Python')
    )

    TAG_CHOICES = (
        ('checker', 'checker'),
        ('interactor', 'interactor'),
        ('generator', 'generator'),
        ('validator', 'validator'),
        ('solution_main', 'solution - main correct'),
        ('solution_correct', 'solution - correct'),
        ('solution_tle_or_ok', 'solution - time limit exceeded or correct'),
        ('solution_wa', 'solution - wrong answer'),
        ('solution_incorrect', 'solution - incorrect'),
        ('solution_fail', 'solution - runtime error'),
    )

    name_validator = NameValidator()

    lang = models.CharField(choices=LANG_CHOICES, default='cpp', max_length=12)
    code = models.TextField(blank=True)
    name = models.CharField(validators=[name_validator, ], max_length=24)
    author = models.ForeignKey(User)
    modified = models.DateTimeField(auto_now=True)
    tag = models.CharField(choices=TAG_CHOICES, default='checker', max_length=24)
    length = models.IntegerField(default=0)
    workspace = models.CharField(max_length=64)
    problem = models.ForeignKey(Problem)

    def save(self, *args, **kwargs):
        self.length = len(self.code.encode())
        return super().save(*args, **kwargs)

    class Meta:
        unique_together = ('problem', 'name')


class RepositoryTest(models.Model):
    fingerprint = models.CharField(max_length=64, default='invalid')
    input_preview = models.TextField(blank=True, default='N/A')
    output_preview = models.TextField(blank=True, default='N/A')
    show_in_samples = models.BooleanField(default=False)
    show_in_pretests = models.BooleanField(default=False)
    show_in_tests = models.BooleanField(default=True)
    manual_output_lock = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    case_number = models.IntegerField(default=0)
    generator = models.ForeignKey(RepositorySource, null=True)
    generate_args = models.TextField(blank=True)
    group = models.CharField(blank=True, max_length=64)
    modified = models.DateTimeField(auto_now=True)
    size = models.IntegerField(default=0)

    problem = models.ForeignKey(Problem)

    class Meta:
        ordering = ('case_number',)
