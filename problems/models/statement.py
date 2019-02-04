from django.db import fields


class Statement(fields.Model):
  lang = fields.CharField(choices=(
    ("english", "English"),
    ("chinese", "Chinese")
  ), max_length=20)  # not used, yet
  type = fields.CharField(default="markdown", choices=(
    ("tex", "TeX"),
    ("markdown", "Markdown"),
    ("html", "HTML"),
    ("doc", "DOC"),
    ("pdf", "PDF")
  ))
  encoding = fields.CharField(max_length=20)
  name = fields.TextField(blank=True)
  legend = fields.TextField(blank=True)
  input = fields.TextField(blank=True)
  output = fields.TextField(blank=True)
  interaction = fields.TextField(blank=True)
  notes = fields.TextField(blank=True)
  tutorial = fields.TextField(blank=True)

  packaged = fields.BooleanField(default=False)

  # render on the fly, results may be cached in the library with the following keys
  create_time = fields.DateTimeField(auto_now_add=True)
  update_time = fields.DateTimeField(auto_now=True)

  class Meta:
    ordering = ["packaged", "id"]
