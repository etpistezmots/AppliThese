from django.urls import path

from AllApps.EtatDesLieux import views

app_name = 'EtatDesLieux'
urlpatterns = [
    path('', views.home, name='home')
]