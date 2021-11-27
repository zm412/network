
import json

from datetime import timedelta, datetime
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import User, Post, UserFollowing
from django import forms


class Add_post(forms.ModelForm):
    body = forms.CharField(widget=forms.Textarea(attrs={'cols': 30, 'rows': 10}))
    class Meta:
        model = Post
        fields = ['title', 'body']

class Upd_post(forms.ModelForm):
    body = forms.CharField(widget=forms.Textarea(attrs={'cols': 30, 'rows': 10}))
    class Meta:
        model = Post
        fields = ['body']


def index(request):
    if request.user.is_authenticated:
        return render(request, "network/index.html", {'quantity': Post.objects.all().count()})
    else:
        return render(request, "network/login.html")

def add_like(request, post_id):
    post = Post.objects.get(id=post_id)
    message = ''

    try:
        post.likes_list_users.get(id=request.user.id)
        post.likes_list_users.remove(request.user.id)
        message = 'like is removed'
    except User.DoesNotExist:
        post.likes_list_users.add(request.user.id)
        message = 'Like is added'

    return JsonResponse({'message': message})




@csrf_exempt
def save_post(request, post_id):
    user = User.objects.get(id=request.user.id)
    answ = {}
    if int( post_id ) == 0:
        answ = func_for_save(request.POST, request.user, Add_post, 'add', post_id)
    else:
        answ = func_for_save(request.POST, request.user, Upd_post, 'upd', post_id)
    print(answ, 'answView')
    return JsonResponse({'status': answ['ok'], 'message': answ['message']})

def func_for_save(obj,  user, form_class, action, post_id=0):
    print(action, 'action')
    form = form_class(obj)
    message = ''
    ok = False
    if form.is_valid():
        if action == 'add':
            title = form.cleaned_data['title']
            body = form.cleaned_data['body']
            post = Post.objects.create( author = user, title = title, body = body)
            message = 'Successfully added'
            ok = True
        else:
            try:
                post = Post.objects.get(id=post_id)
                body = form.cleaned_data['body']
                if post.body != body:
                    post.body = body 
                    post.updated = datetime.now() 
                    post.save()
                    message = 'Successfully updated'
                    ok = True
                else:
                    message = 'there is nothing to update'
            except Post.DoesNotExist:
                message = 'data for update is not valid'
                ok = False

    else:
        print('notvalid')
        if action == 'add':
            message = 'data for add is not valid'
        else:
            message = 'data for update is not valid'
    return { 'message': message, 'ok': ok }



def get_user_info(request, following_user_id):
    user = User.objects.get(id=following_user_id)
    answ = user.followers.filter(id=request.user.id)
    return JsonResponse({'status':'ok', 'is_following': answ.count() > 0})

def user_follow(request, following_user_id, action):
    message = 'data is not valid'
    print(action, 'action', following_user_id, 'usId')
    status = False
    if following_user_id and action:
        try:
            user = User.objects.get(id=following_user_id)
            if  action == "follow" :
                UserFollowing.objects.create(
                    follower_user=request.user,
                    following_user=user)
                message = f'the current user is the  subscriber of {user.username}'
                status = True
            elif(action == 'unfollow'):
                UserFollowing.objects.filter(
                    follower_user=request.user,
                    following_user=user
                ).delete()
                message = f'the current user is not the  subscriber of {user.username} anymore'
                status = True
        except User.DoesNotExist:
            status = False
            message = 'data is not valid'
    return JsonResponse({'status': status, 'message': message})

def create_list_of_posts(post_owner_id, start, end, curr_user_id):
    post_line = []
    queryset_var = []
    id_user = post_owner_id

    if int(post_owner_id) > 0:
        queryset_var = Post.objects.filter(author__id=post_owner_id)
    elif int(post_owner_id) == 0:
        queryset_var = Post.objects.all()
        id_user = curr_user_id
    else:
        id_user = curr_user_id
        queryset_var = Post.objects.filter(author__followers__id = curr_user_id)
    posts = queryset_var.order_by("-publish").all()[start: end]
    return {'posts': posts, 'quantity': queryset_var.count(), 'id_user': id_user }


def all_posts(request):
    list_posts = Post.objects.all()
    a = 'start' in request.GET and request.GET['start']
    b = 'end' in request.GET and request.GET['end']
    c = 'post_owner_id' in request.GET and request.GET['post_owner_id']
    if a and b and c:
        start = int(request.GET.get('start'))
        end = int(request.GET.get('end'))
        post_owner_id = int(request.GET.get('post_owner_id'))
        result = create_list_of_posts(post_owner_id, start, end, request.user.id)
        id_user = result['id_user']
        user = User.objects.get(id=id_user)
        followers = [follower.get_followers() for follower in user.rel_to_set.all() ]
        followings = [following.get_followings() for following in user.rel_from_set.all() ]
        is_follower = False

        context = {
            'author':user.username,
            'following': followings,
            'followers': followers,
            'posts': [post.serialize() for post in result['posts']],
            'quantity': result['quantity'],
            'following_user': id_user,
        }
        return JsonResponse(context, safe=False)
    else:
        return HttpResponseRedirect(reverse('index'))

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
        return HttpResponseRedirect(reverse("index"), {'status': 'OK'})
    else:
        return render(request, "network/register.html")
