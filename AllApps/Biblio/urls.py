from django.urls import path

from AllApps.Biblio import views

app_name = 'Biblio'
urlpatterns = [
    path('', views.home, name='home'),
    path('ViewBiblioAll/<int:CollectId>/<int:LangId>', views.ViewBiblioAll, name='ViewBiblioAll'),
    path('ViewBiblioInterface/<int:CollectId>', views.ViewBiblioInterface, name='ViewBiblioInterface'),
    path('ViewMultiRef/<int:CollectId>/<str:Ref>', views.ViewMultiRef, name='ViewMultiRef'),
]