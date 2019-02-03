from django.db import models
from django.db.models import Sum, Case, When, IntegerField
from accounts.models import User
from commons.models import Text
from shares.models.base import Share


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


class Blog(Share):
  title = models.TextField(max_length=128)
  content = models.ForeignKey(Text, on_delete=models.SET_NULL, null=True)

  likes = models.ManyToManyField(User, through='BlogLikes', related_name='blog_user_like')
  recommend = models.BooleanField(default=False)

  objects = BlogQuerySet.as_manager()

  class Meta:
    db_table = "blogs"


class BlogLikes(models.Model):
  BLOG_LIKE_FLAGS = (
    ('like', '点赞'),
    ('dislike', '点踩')
  )

  blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  flag = models.TextField(choices=BLOG_LIKE_FLAGS)

  class Meta:
    unique_together = ('blog', 'user')
    db_table = "blog_likes"
