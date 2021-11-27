from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone



class User(AbstractUser):
    pass


class UserFollowing(models.Model):
    follower_user = models.ForeignKey('User',
                related_name='rel_from_set',
                on_delete=models.CASCADE)
    following_user = models.ForeignKey('User',
                related_name='rel_to_set',
                on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return '{} follows {}'.format(self.follower_user, self.following_user)

    def get_followers(self):
        return {
            'id': self.follower_user.id,
            'username': self.follower_user.username
        }

    def get_followings(self):
        return {
            'id': self.following_user.id,
            'username': self.following_user.username
        }

    def serialize(self):
        return {
            'follower': {
                'id': self.follower_user.id ,
                'username': self.follower_user.username
            },
            'following': {
                'id': self.following_user.id,
                'username': self.following_user.username
            },
            "created": self.created,
        }

User.add_to_class('following', models.ManyToManyField(
    'self', through=UserFollowing, related_name='followers', symmetrical=False))

class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=250,
                            unique_for_date='publish')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='blog_posts')
    body = models.TextField(max_length=1000)
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    likes_list_users = models.ManyToManyField(User, blank=True, related_name="likers_list")
    status = models.CharField(max_length=10,
                              choices=STATUS_CHOICES,
                              default='draft')
    follow_list_users = models.ManyToManyField(User, blank=True, related_name="followers_list")
    def serialize(self):
        return {
            "id": self.id,
            "status": self.status,
            "title": self.title,
            "author_name": self.author.username,
            "author_id": self.author.id,
            "body": self.body,
            "publish": self.publish.strftime("%b %d %Y, %I:%M %p"),
            "created": self.created.strftime("%b %d %Y, %I:%M %p"),
            "updated": self.updated.strftime("%b %d %Y, %I:%M %p"),
            "likers": [{ 'id': liker.id, 'username': liker.username } for liker in self.likes_list_users.all()]
        }

    def __str__(self):
        return f'id: {self.id}, title: {self.title}'

