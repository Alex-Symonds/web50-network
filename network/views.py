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
    # Get all posts, paginate and extract one page
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
                "message": "<span>ACCESS DENIED</span><br>Invalid username and/or password.".upper()
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
    user = User.objects.get(username=request.user)

    if request.user.is_authenticated:
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


def follow_toggle(request, user_id):

    if not request.user.is_authenticated:
        return render(request, "network/error.html", {
            "message": "You must be logged in to follow someone."
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
            "Error": "GET or PUT request required."
        }, status=400)


def posts(request):
    if not request.user.is_authenticated:
        return render(request, "network/error.html", {
            "message": "You must be logged in to make or edit a post."
        }, status=401)

    u = request.user

    if request.method == "POST":
        posted_form = NewPostForm(request.POST)
        if posted_form.is_valid():
            new_content = posted_form.cleaned_data["content"]
            npo = Post(poster=u, content=new_content)
            npo.save()
            return HttpResponseRedirect(reverse("index"))
      
    elif request.method == "PUT":       
        data = json.loads(request.body)
        post_id = data.get("id")
        this_post = Post.objects.get(id=post_id)

        if u == this_post.poster:
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
    
    if request.method == "PUT":
        # Check the user is logged in
        if not request.user.is_authenticated:
            return render(request, "network/error.html", {
                "message": "You must be logged in to like a post."
            }, status=401)

        user = request.user

        # Read in the JSON from the user
        data = json.loads(request.body)
        like_now = data.get("toggled_status")

        # Set previous like status
        like_before = user.liked.filter(id=post_id).exists()

        if like_now == like_before:
            return JsonResponse({
                "message": "OK"
            }, status=200)

        else:
            post = Post.objects.get(id=post_id)

            # If the user likes a previously unliked post, add it to the list
            if like_now and not like_before:
                user.liked.add(post)
                return JsonResponse({
                    "message": "Post liked successfully."
                }, status=201)

            # If the user un-likes a previously liked post, remove it from the list
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

          


    


        
            

        
 