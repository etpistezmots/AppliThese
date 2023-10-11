from django.urls import path

from . import views

app_name = 'general'
urlpatterns = [
    path('', views.home, name='home'),
    path('useplus', views.useplus, name='useplus'),
    path('getiduser', views.getiduser, name='getiduser')
]