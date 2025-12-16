from django.urls import path
from . import views
from django.urls import path, include


urlpatterns = [
    path('', views.post_list, name='post_list'),          # homepage – list all posts
    path('post/<int:pk>/', views.post_detail, name='post_detail'),  # single post
    path('accounts/', include('django.contrib.auth.urls')),
    path('post/<int:pk>/edit/', views.edit_post, name='edit_post'),
    path('post/create/', views.create_post, name='create_post'),
]

