from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name= 'index'),
    path('login/', views.login_view, name='login_view'),
    path('register/', views.register, name='register'),
    path('supervisor/', views.supervisor, name='supervisor'),
    path('motorista/', views.motorista, name='motorista'),
]