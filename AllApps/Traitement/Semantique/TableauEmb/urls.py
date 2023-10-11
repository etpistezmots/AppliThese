from django.urls import path

from AllApps.Traitement.Semantique.TableauEmb import views

app_name = 'TableauEmb'
urlpatterns = [
    path('', views.homeredirect, name='homeredirect'),
    path('home/<str:mode>', views.home, name='home'),
    path('modele/<str:mode>/<int:modele_id>', views.modele, name='modele'),
    path('result/<str:mode>/<int:modele_id>/<int:result_id>', views.result, name='result'),
    path('supprmultimodeles/<str:mode>', views.supprmultimodeles, name='supprmultimodeles'),
    path('suppronemodele/<str:mode>/<int:modele_id>', views.suppronemodele, name='suppronemodele'),
    path('supprmultiresults/<str:mode>/<int:modele_id>', views.supprmultiresults, name='supprmultiresults'),
    path('supproneresult/<str:mode>/<int:modele_id>/<int:result_id>', views.supproneresult, name='supproneresult'),
    path('resultallselect', views.resultallselect, name='resultallselect'),
    path('resultallvisu/<str:listexpesvisibles>/<str:listexpesstock>/<str:paraselect>/<str:revueselect>/<int:nselect>', views.resultallvisu, name='resultallvisu'),
    path('resultallvisucolor/<str:listexpesvisibles>/<str:listexpesstock>/<str:paraselect>/<str:revueselect>/<int:nselect>', views.resultallvisucolor, name='resultallvisucolor'),
]