from django.urls import path

from AllApps.Introduction import views

app_name = 'Introduction'
urlpatterns = [
    path('', views.home, name='home'),
    path('VersTheseMBeligne', views.VersTheseMBeligne, name='VersTheseMBeligne'),
]