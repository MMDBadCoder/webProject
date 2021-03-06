from django.db import models
from django.db.models import CASCADE

from accounting.models import Account
from paging.models import Page


class Follow(models.Model):
    follower = models.ForeignKey(Account, on_delete=CASCADE, blank=False, related_name='following', db_index=True)
    followed = models.ForeignKey(Account, on_delete=CASCADE, blank=False, related_name='followed', db_index=True)

    class Meta:
        verbose_name = 'following'


class FollowPage(models.Model):
    follower = models.ForeignKey(Account, on_delete=CASCADE, blank=False, db_index=True)
    followed = models.ForeignKey(Page, on_delete=CASCADE, blank=False, db_index=True)
