from django.db import models
from django.db.models import Sum, Case, When, IntegerField
from accounts.models import User
from commons.models import RichText
from problems.models import Problem
from django.utils.translation import ugettext_lazy as _


class BlogQuerySet(models.QuerySet):
  def with_likes(self):
    return self.annotate(
      likes__count=Sum(Case(When(bloglikes__flag='like', then=1), default=0, output_field=IntegerField()))
    )

  def with_dislikes(self):
    return self.annotate(
      dislikes__count=Sum(Case(When(bloglikes__flag='dislike', then=1), default=0, output_field=IntegerField()))
    )

  def with_likes_flag(self, user):
    if not user.is_authenticated:
      return self
    return self.annotate(
      likes__flag=Sum(
        Case(When(bloglikes__user=user, bloglikes__flag='like', then=1),
             When(bloglikes__user=user, bloglikes__flag='dislike', then=-1), default=0, output_field=IntegerField()))
    )


class BlogRevision(models.Model):
  title = models.TextField()
  content = models.ForeignKey(RichText, on_delete=models.SET_NULL, null=True)
  created_by = models.ForeignKey(User, on_delete=models.CASCADE)
  create_time = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ["-create_time"]


class Blog(models.Model):
  title = models.CharField(max_length=128)
  content = models.ForeignKey(RichText, on_delete=models.SET_NULL, null=True)
  created_by = models.ForeignKey(User, on_delete=models.CASCADE)

  visible = models.BooleanField("Visible to all users", default=True)
  create_time = models.DateTimeField(auto_now_add=True)
  update_time = models.DateTimeField(auto_now=True)

  likes = models.ManyToManyField(User, through='BlogLikes', related_name='blog_user_like')
  recommend = models.BooleanField(default=False)
  revisions = models.ManyToManyField(BlogRevision)
  hide_revisions = models.BooleanField("History versions only available to you", default=False)

  objects = BlogQuerySet.as_manager()

  class Meta:
    ordering = ["-edit_time"]


class BlogLikes(models.Model):
  BLOG_LIKE_FLAGS = (
    ('like', '点赞'),
    ('dislike', '点踩')
  )

  blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  flag = models.CharField(max_length=8, choices=BLOG_LIKE_FLAGS)

  class Meta:
    unique_together = ('shares', 'user')


class Comment(models.Model):
  # DEPRECATED
  text = models.TextField()
  author = models.ForeignKey(User, on_delete=models.CASCADE)
  create_time = models.DateTimeField("Created time", auto_now_add=True)
  blog = models.ForeignKey(Blog, on_delete=models.SET_NULL, null=True)
  problem = models.ForeignKey(Problem, on_delete=models.SET_NULL, null=True)

  class Meta:
    ordering = ["-create_time"]
