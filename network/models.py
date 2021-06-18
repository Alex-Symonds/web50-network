from django.contrib.auth.models import AbstractUser
from django.db import models
import datetime

class User(AbstractUser):
    following = models.ManyToManyField("self", related_name="followers", symmetrical=False)


class Post(models.Model):
    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    created_on = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    likes = models.ManyToManyField(User, related_name="liked")

    def index_fields(self):
        return {
            "username": self.poster.username,
            "created_on": self.created_on,
            "content": self.content,
            "like_count": self.likes.count()
        }

    def __str__(self):
        return f"Post #{self.id}: {self.poster.username} @ {self.created_on - datetime.timedelta(microseconds=self.created_on.microsecond)} "

