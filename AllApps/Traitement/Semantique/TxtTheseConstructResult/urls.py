from django.urls import path

from AllApps.Traitement.Semantique.TxtTheseConstructResult import views

app_name = 'TxtTheseConstructResult'
urlpatterns = [
    path('', views.home, name='home')
]