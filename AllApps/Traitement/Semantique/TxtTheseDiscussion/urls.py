from django.urls import path

from AllApps.Traitement.Semantique.TxtTheseDiscussion import views

app_name = 'TxtTheseDiscussion'
urlpatterns = [
    path('', views.home, name='home'),
]