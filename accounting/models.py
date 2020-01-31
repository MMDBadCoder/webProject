import random
import string

from django.contrib.auth.models import User
from django.db import models


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, )
    portfolio_site = models.URLField(blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics', blank=True)
    location = models.TextField(max_length=60, default='iran!', )
    bio = models.TextField(max_length=120, default='nothing until now')
    is_private = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class Token(models.Model):
    username = models.TextField()
    code = models.TextField()

    def __str__(self):
        return self.username + ' : ' + self.code


def create_new_token(username):
    code = get_random_code()
    token = Token(username=username, code=code)
    return token


def get_random_code():
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(20))
