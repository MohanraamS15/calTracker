from django.urls import path
from . import views
from nu import views

urlpatterns = [
    path('', views.index, name='home'),
    path('profile/', views.profile, name='profile'),
    path('log-meal/', views.log_meal, name='log_meal'),
    path('recommend/', views.recommend_meal, name='recommend_meal'),
    path('delete-meal/', views.delete_meal, name='delete_meal'),

    path("signup/", views.signup_view, name="signup"),
    path("profile/", views.profile_view, name="profile"),
    path("log-meal/", views.log_meal, name="log_meal"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),


]



