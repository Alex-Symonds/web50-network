# Views for Network, a basic social network

import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator

from .models import User, Post
from .forms import NewPostForm

# Set posts per page for pagination purposes
MAX_POSTS_PER_PAGE = 10


def index(request):
    """
        Main page
    """
    # Get all posts, paginate and send one page for display
    data = Post.objects.all().order_by("-created_on")
    p = Paginator(data, MAX_POSTS_PER_PAGE)
    page_num = request.GET.get("page")
    req_page = p.get_page(page_num)

    return render(request, "network/index.html", {
        "form": NewPostForm,
        "page": req_page
    })

def login_view(request):
    """
        Log in page
    """
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
                "message": "<span>ACCESS DENIED</span><br>Invalid username and/or password.".upper()
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    """
        Log out page
    """
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    """
        Registration page
    """
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "<span>ERROR</span><br>Passwords must match.".upper()
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "<span>ERROR</span><br>Username already taken.".upper()
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


def profile(request, user_id):
    """
        Profile page for the specified user
    """
    if not User.objects.filter(id=user_id).exists():
        return render(request, "network/error.html", {
            "message": "<span>ACCESS DENIED</span><br>The requested user was not found.".upper()
        }, status=404)

    # Get user object for profile owner
    target_user = User.objects.get(id=user_id)

    # Get all posts by the profile owner and paginate
    data = Post.objects.filter(poster=target_user).order_by("-created_on")
    p = Paginator(data, MAX_POSTS_PER_PAGE)
    page_num = request.GET.get("page")
    req_page = p.get_page(page_num)

    # Set "is_following"
    if request.user.is_authenticated:
        user = User.objects.get(username=request.user)
        is_following = False
        if target_user in user.following.all():
            is_following = True
    else:
        is_following = False
   
    return render(request, "network/profile.html", {
        "following_count": target_user.following.all().count(),
        "followers_count": target_user.followers.all().count(),
        "profile_user": target_user,
        "is_following": is_following,
        "page": req_page
    })


def following(request):
    """
        Following page (i.e. posts filtered to include only users being followed by the calling user)
    """
    if request.user.is_authenticated:
        user = User.objects.get(username=request.user)
        fposts = Post.objects.filter(poster__in=user.following.all()).order_by("-created_on")

        p = Paginator(fposts, MAX_POSTS_PER_PAGE)
        page_num = request.GET.get("page")
        req_page = p.get_page(page_num)

        return render(request, "network/following.html", {
            "page": req_page,
            "isFollowing": user.following.all().count() > 0
        })
    else:
        return render(request, "network/error.html", {
            "message": "You must be logged in to view this page."
        }, status=401)        


def errors(request):
    """
        Render the error page with a message generated based on GET parameters (used when error page is called from the frontend)
    """
    get_code = request.GET.get("type")
    message = "You must be logged in to "
    if get_code == "posts":
        message += "edit a post."
    elif get_code == "likes":
        message += "adjust like status."
    elif get_code == "follow":
        message += "adjust follow status."
    else:
        message = "Action failed."
    
    return render(request, "network/error.html", {
        "message": message
    }, status=401)   


def follow_toggle(request, user_id):
    """
        Toggle or read follow status, return JSON confirmation
    """
    if not request.user.is_authenticated:
        return JsonResponse({
            "redirect": reverse("errors")
        }, status=401)

    target_user = User.objects.get(id=user_id)
    current_user = request.user

    if request.method == "PUT":
        data = json.loads(request.body)
        want_follow = data.get("toggled_status")

        if want_follow is not None:
            if want_follow:
                current_user.following.add(target_user)
                return JsonResponse({
                    "message": "Follow status toggled successfully."
                 }, status=201)
            else:
                current_user.following.remove(target_user)
                return JsonResponse({
                    "message": "Follow status toggled successfully."
                }, status=200)

    elif request.method == "GET":
        status = target_user in current_user.following.all()
        return JsonResponse({
            "is_followed": status
        }, status=100)

    else:
        return JsonResponse({
            "Error": "GET or POST request required."
        }, status=400)


def posts(request):
    """
        Create or update posts, return JSON confirmation
    """

    # New post. Page expects a HTTP Redirect of some description.
    if request.method == "POST":

        if not request.user.is_authenticated:
            return render(request, "network/error.html", {
                "message": "You must be logged in to create a post."
            }, status=401)

        posted_form = NewPostForm(request.POST)
        if posted_form.is_valid():
            u = request.user
            new_content = posted_form.cleaned_data["content"]
            npo = Post(poster=u, content=new_content)
            npo.save()
            return HttpResponseRedirect(reverse("index"))
      

    # Edit post. Page expects a JSON response.
    elif request.method == "PUT":

        if not request.user.is_authenticated:
            return JsonResponse({
                "redirect": reverse("errors")
            }, status=401)

        data = json.loads(request.body)
        post_id = data.get("id")
        if post_id == None:
            return JsonResponse({
                "message": "Error: invalid input."
            }, status=400)                
    
        this_post = Post.objects.get(id=post_id)
        if request.user == this_post.poster:

            new_content = data.get("editted_content")
            this_post.content = new_content

            try:
                this_post.save()
            except:
                return JsonResponse({
                    "message": "Server problem: post was not saved."
                }, status=500)
    
            return JsonResponse({
                "message": "Post editted successfully."
            }, status=200)

        else:
            return JsonResponse({
                "message": "Users can only edit their own posts."
            }, status=403)
                 

def likes(request, post_id):
    """
        Toggle or read likes, return JSON confirmation
    """
    if request.method == "PUT":

        # Check the user is logged in
        if not request.user.is_authenticated:
            return JsonResponse({
                "redirect": reverse("errors")
            }, status=401)
        user = request.user

        # Compare the previous like status to the request body and change it in the database if necessary
        data = json.loads(request.body)
        like_now = data.get("toggled_status")
        like_before = user.liked.filter(id=post_id).exists()

        if like_now == like_before:
            return JsonResponse({
                "message": "OK"
            }, status=200)

        else:
            post = Post.objects.get(id=post_id)

            # If the user liked a previously unliked post, add it to the list
            if like_now and not like_before:
                user.liked.add(post)
                return JsonResponse({
                    "message": "Post liked successfully."
                }, status=201)

            # If the user un-liked a previously liked post, remove it from the list
            elif not like_now and like_before:
                user.liked.remove(post)
                return JsonResponse({
                    "message": "Post un-liked successfully."
                }, status=200)

    elif request.method == "GET":

        # Check the user is logged in
        if not request.user.is_authenticated:
            return JsonResponse({
                "liked": False
            })

        # Check if the logged-in user liked this post
        user = request.user
        post = Post.objects.get(id=post_id)
        return JsonResponse({
            "liked": post in user.liked.all()
        })


        
 