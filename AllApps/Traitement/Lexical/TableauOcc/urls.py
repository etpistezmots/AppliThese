from django.urls import path
from AllApps.Traitement.Lexical.TableauOcc import views

app_name = 'TableauOcc'
urlpatterns = [
    path('', views.home, name='home'),
    path('Interface/<str:mode>', views.Interface, name='Interface'),
    path('Result/<str:mode>/<int:resultid>',views.Result, name='Result'),
    path('DeleteOneOcc/<str:mode>/<int:resultid>',views.DeleteOneOcc, name='DeleteOneOcc'),
    path('DeleteMultiOcc',views.DeleteMultiOcc, name='DeleteMultiOcc'),
]