from django.contrib import admin

# Register your models here.

from .models import User, Post, UserFollowing

admin.site.register(Post)
admin.site.register(UserFollowing)
