
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("user/<int:user_id>", views.profile, name="profile"),
    path("following", views.following, name="following"),
    path("follow/<int:user_id>", views.follow_toggle, name="follow"),
    path("posts", views.posts, name="posts"),
    path("likes/<int:post_id>", views.likes, name="likes")
]
