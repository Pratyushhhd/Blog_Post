from django.urls import path
from . import views
from .views import CustomLogoutView, CustomLoginView


urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),




    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='/login/'), name='logout'),


    path('', views.post_list, name='post_list'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/create/', views.create_post, name='create_post'),
    path('post/<int:pk>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:pk>/delete/', views.delete_post, name='delete_post'),
    path('post/<int:pk>/like/', views.like_post, name='like_post'),
]

