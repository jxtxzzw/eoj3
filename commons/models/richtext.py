from django.db import models

from commons.models.attachment import Attachment


class RichText(models.Model):
  raw_text = models.TextField(blank=True)
  attachments = models.ManyToManyField(Attachment)
  render_method = models.TextField(choices=(
    ("md", "Markdown"),
    ("latex", "LaTeX"),
    ("html", "HTML"),
  ), default="md")
  processed_html = models.TextField(blank=True)
  create_time = models.DateTimeField(auto_now_add=True)
  update_time = models.DateTimeField(auto_add=True)

  def save(self, **kwargs):
    # TODO: render here
    super().save(**kwargs)

  class Meta:
    db_table = "rich_texts"
