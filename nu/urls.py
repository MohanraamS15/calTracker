from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('profile/', views.profile, name='profile'),
    path('log-meal/', views.log_meal, name='log_meal'),
    path('recommend/', views.recommend_meal, name='recommend_meal'),
]
