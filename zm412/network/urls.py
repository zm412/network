
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('save_post/<int:post_id>', views.save_post, name='save_post'),
    path('posts/', views.all_posts, name='all_posts'),
    path('posts/<int:post_id>', views.add_like, name='add_like'),
    path('follow/<int:following_user_id>/<str:action>', views.user_follow, name='user_follow'),
    path('user_info/<int:following_user_id>', views.get_user_info, name='get_user_info'),
]
