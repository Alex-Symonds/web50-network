from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    following = models.ManyToManyField("self", related_name="followers")


class Post(models.Model):
    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    created_on = models.DateTimeField(auto_now_add=True)
    contents = models.CharField(max_length=280)
    likes = models.ManyToManyField(User, related_name="liked")

