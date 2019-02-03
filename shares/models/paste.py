from datetime import datetime, timedelta

from django.db import models

from commons.fields.languages import LanguageField
from shares.models.base import Share


class Paste(Share):
  fingerprint = models.TextField(unique=True)
  code = models.TextField(blank=False)
  lang = LanguageField()
  expire_after = models.IntegerField(choices=(
    (-1, '永不'),
    (1, '1 分钟'),
    (10, '10 分钟'),
    (60, '1 小时'),
    (300, '5 小时'),
    (1440, '1 天'),
    (43200, '30 天'),
  ), default=-1)

  @property
  def expired(self):
    return self.expire_after > 0 and datetime.now() - self.create_time > timedelta(minutes=self.expire_after)
