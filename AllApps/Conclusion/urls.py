from django.urls import path

from AllApps.Conclusion import views

app_name = 'Conclusion'
urlpatterns = [
    path('', views.home, name='home'),
]