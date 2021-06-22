import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import User, Post
from .forms import NewPostForm

from django.core.paginator import Paginator
MAX_POSTS_PER_PAGE = 10

def index(request):

    if request.method == "POST":
        posted_form = NewPostForm(request.POST)
        if posted_form.is_valid():
            new_content = posted_form.cleaned_data["content"]
            u = request.user

            npo = Post(poster=u, content=new_content)
            npo.save()
            return HttpResponseRedirect(reverse("index"))

    data = Post.objects.all().order_by("-created_on")
    p = Paginator(data, MAX_POSTS_PER_PAGE)
    
    page_num = request.GET.get("page")
    req_page = p.get_page(page_num)

    return render(request, "network/index.html", {
        "form": NewPostForm,
        "page": req_page
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


def profile(request, user_id):

    target_user = User.objects.get(id=user_id)

    data = Post.objects.filter(poster=target_user).order_by("-created_on")
    p = Paginator(data, MAX_POSTS_PER_PAGE)
    
    page_num = request.GET.get("page")
    req_page = p.get_page(page_num)


    return render(request, "network/profile.html", {
        "following_count": target_user.following.count(),
        "followers_count": target_user.followers.all().count(),
        "profile_name": target_user.username,
        "profile_id": user_id,
        "page": req_page
    })



def following(request):
    user = User.objects.get(username=request.user)
    fposts = Post.objects.filter(poster__in=user.following.all())

    p = Paginator(fposts, MAX_POSTS_PER_PAGE)
    page_num = request.GET.get("page")
    req_page = p.get_page(page_num)

    return render(request, "network/following.html", {
        "page": req_page
    })


def follow_toggle(request, user_id):
    target_user = User.objects.get(id=user_id)
    current_user = request.user

    if request.method == "PUT":
        data = json.loads(request.body)
        want_follow = data.get("want_follow")
        if want_follow is not None:
            if want_follow:
                current_user.following.add(target_user)
            else:
                current_user.following.remove(target_user)
                
            return JsonResponse({
                "message": "Follow status toggled successfully."
            }, status=201)

    elif request.method == "GET":
        status = target_user in current_user.following.all()
        return JsonResponse({
            "is_followed": status
        })

    else:
        return JsonResponse({
            "Error": "GET or PUT request required."
        }, status=400)