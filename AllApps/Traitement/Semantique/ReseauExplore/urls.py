from django.urls import path
from AllApps.Traitement.Semantique.ReseauExplore import views

app_name = 'ReseauExplore'
urlpatterns = [
    path('', views.homeredirect, name='homeredirect'),
    path('home/<str:mode>', views.home, name='home'),
    path('<str:mode>/modele/<int:modele_id>', views.modele, name='modele'),
    path('<str:mode>/result/<int:modele_id>/<int:result_id>/<str:orient>', views.result, name='result'),
    path('resultallselect', views.resultallselect, name='resultallselect'),
    path('resultallvisu/<str:listexpesvisibles>/<str:listexpesstock>/<str:paraselect>/<str:formselect>/<str:tailleselect>', views.resultallvisu, name='resultallvisu'),
    path('supproneresult/<str:mode>/<int:modele_id>/<int:result_id>', views.supproneresult, name='supproneresult'),
    path('supprmultiresults/<str:mode>/<int:modele_id>', views.supprmultiresults, name='supprmultiresults'),
    path('graphnonoriente', views.AjaxGraphNonOriente, name='graphnonoriente'),
    path('graphoriente', views.AjaxGraphOriente, name='graphoriente'),
]