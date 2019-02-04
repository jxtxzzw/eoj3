from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import BaseValidator
from django.db import models
from django.contrib.auth.models import AbstractUser

from commons.fields.languages import LanguageField
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from commons.fields import JSONField


class User(AbstractUser):
  class UsernameValidator(UnicodeUsernameValidator):
    regex = r'^[\w.+-]+$'
    message = 'Enter a valid username. This value may contain only letters, numbers, and ./+/-/_ characters.'

  class UsernameLengthValidator(BaseValidator):
    message = "Username should contain at least 6 characters."
    code = 'min_length'

    def compare(self, a, b):
      return a < b

    def clean(self, x):
      try:
        return len(x.encode("GBK"))
      except UnicodeEncodeError:
        return len(x)

  MAGIC_CHOICE = (
    ('red', "Red"),
    ('green', "Green"),
    ('teal', "Teal"),
    ('blue', "Blue"),
    ('purple', "Purple"),
    ('orange', "Orange"),
    ('grey', "Grey"),
  )

  username_validators = [UsernameValidator(), UsernameLengthValidator(6)]

  username = models.CharField("username", max_length=30, unique=True,
                              validators=username_validators,
                              error_messages={
                                'unique': "A user with that username already exists."}
                              )
  email = models.EmailField("email", max_length=192, unique=True, error_messages={
    'unique': "This email has already been used."
  })
  color = models.TextField(choices=MAGIC_CHOICE, blank=True)
  polygon_enabled = models.BooleanField(default=False)

  def __str__(self):
    return self.username

  class Meta:
    db_table = "users"


class Transaction(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  note = models.TextField(blank=True)
  create_time = models.DateTimeField(auto_now_add=True)
  credit = models.FloatField()  # or debit
  balance = models.FloatField()

  class Meta:
    db_table = "transaction"
    ordering = ["-create_time"]


class School(models.Model):
  name = models.TextField(unique=True)
  abbr = models.TextField(unique=True)
  alias = models.TextField(blank=True)

  def __str__(self):
    if self.alias:
      return "%s (%s)" % (self.name, self.alias)
    else:
      return self.name

  class Meta:
    db_table = "schools"


class UserProfile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)

  MAJOR_CHOICES = (
    ('art', '艺术'),
    ('accounting', '会计'),
    ('business', '商业'),
    ('business_admin', '工商管理'),
    ('chemistry', '化学'),
    ('communication', '通信'),
    ('ce', '计算机工程'),
    ('cs', '计算机科学'),
    ('economics', '经济'),
    ('education', '教育'),
    ('ee', '电子工程'),
    ('finance', '金融'),
    ('geology', '地理'),
    ('interaction', '人机交互'),
    ('it', '信息技术'),
    ('life', '生命科学'),
    ('mechanics', '机械'),
    ('linguistics', '语言学'),
    ('literature', '文学'),
    ('math', '数学'),
    ('se', '软件工程'),
    ('philosophy', '哲学'),
    ('physics', '物理'),
    ('politics', '政治学'),
    ('psycho', '心理学'),
    ('social', '社会学'),
    ('translation', '翻译'),
    ('others', '其他')
  )

  GENDER_CHOICES = (
    ('m', '男'),
    ('f', '女'),
    ('d', '拒绝回答')
  )

  school = models.CharField(blank=True)
  student_id = models.CharField(blank=True)
  real_name = models.CharField(blank=True)
  major = models.CharField(choices=MAJOR_CHOICES, blank=True)
  gender = models.TextField(choices=GENDER_CHOICES)
  graduate_year = models.IntegerField(blank=True, null=True)

  show_tags = models.BooleanField(default=True)
  preferred_lang = LanguageField()
  motto = models.TextField(max_length=256, blank=True)

  avatar = models.ImageField(upload_to='avatars/%Y/%m/%d/', default='avatars/default.jpg')
  avatar_small = ImageSpecField(source='avatar',
                                processors=[ResizeToFill(50, 50)],
                                format='JPEG',
                                options={'quality': 60})
  avatar_large = ImageSpecField(source='avatar',
                                processors=[ResizeToFill(500, 500)],
                                format='JPEG',
                                options={'quality': 60})
  score = models.FloatField(default=0)
  username_change_attempt = models.IntegerField(default=0)
  email_subscription = models.BooleanField(default=True)
  rating = models.IntegerField(default=0)

  class Meta:
    db_table = "user_profiles"


class UserStatus(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="submission_status")
  contest_id = models.PositiveIntegerField(db_index=True)
  total_count = models.PositiveIntegerField()
  total_list = JSONField()
  ac_count = models.PositiveIntegerField()
  ac_distinct_count = models.PositiveIntegerField()
  ac_list = JSONField()
  update_time = models.DateTimeField(auto_now=True)

  class Meta:
    unique_together = ('user', 'contest_id')
    db_table = "user_status"
