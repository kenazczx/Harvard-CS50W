from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms
from .models import User, Post, Follow
import json
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator

class CreatePost(forms.Form):
    new_post = forms.CharField(
        label="New Post", 
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
def index(request):
    if request.method == "POST":
        form = CreatePost(request.POST)
        if form.is_valid():
            new_post = form.cleaned_data["new_post"]
            post = Post(
                text=new_post,
                user=request.user
            )
            post.save()
            
            return HttpResponseRedirect(reverse("index"))
            
    else:
        form = CreatePost()
    
    posts = Post.objects.all().order_by('-timestamp')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "network/index.html", {
        "form": form,
        "posts": posts,
        "page_obj": page_obj
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


def profile(request, username):
    profile_user = User.objects.get(username=username)
    if request.method == "POST":
        existing = Follow.objects.filter(follower=request.user, followed=profile_user)
        if existing.exists():
            existing.delete()
        else:
            Follow.objects.create(follower=request.user, followed=profile_user)
        return redirect('profile', username=username)
    user_following = False
    if request.user.is_authenticated:
        user_following = Follow.objects.filter(follower=request.user, followed=profile_user).exists()
    followers = Follow.objects.filter(followed=profile_user).count() 
    following = Follow.objects.filter(follower=profile_user).count() 
    posts = Post.objects.filter(user=profile_user).order_by('-timestamp')
    
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "network/profile.html", {
        "followers": followers,
        "following": following,
        "page_obj": page_obj,
        "username": profile_user,
        "user_following": user_following,
        "posts": posts
    })
    
    
def following(request):
    following_users = Follow.objects.filter(follower=request.user).values_list('followed', flat=True)
    posts = Post.objects.filter(user__in=following_users).order_by('-timestamp')
    
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "network/following.html", {
        "page_obj": page_obj
    })
    
    
    
@csrf_exempt
def edit_post(request, post_id):
    if request.method == "POST":
        data = json.loads(request.body)
        text = data.get("text")
        post = Post.objects.get(pk=post_id)
        if request.user != post.user:
            return HttpResponseForbidden("You cannot edit this post.")
        post.text = text
        post.save()
        return JsonResponse({"text": post.text})

@csrf_exempt
def like_post(request, post_id):
    if request.method == "POST":
        post = Post.objects.get(pk=post_id)
        
        if request.user in post.likes.all():
            post.likes.remove(request.user)
            liked = False
        else:
            post.likes.add(request.user)
            liked = True
        return JsonResponse({
            "liked": liked,
            "likes_count": post.likes.count()
        })

