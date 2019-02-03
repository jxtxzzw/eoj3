from django.db.models import CharField

from commons.languages import LANG_CHOICES, DEFAULT_LANG_CODE


class LanguageField(CharField):
  def __init__(self, *args, **kwargs):
    kwargs["max_length"] = 20
    kwargs["choices"] = LANG_CHOICES
    kwargs["default"] = DEFAULT_LANG_CODE
    kwargs["blank"] = True
    kwargs["null"] = True
    super().__init__(*args, **kwargs)
