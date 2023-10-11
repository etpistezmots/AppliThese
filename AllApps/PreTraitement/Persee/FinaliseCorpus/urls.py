from django.urls import path

from AllApps.PreTraitement.Persee.FinaliseCorpus import views

app_name = 'FinaliseCorpus'
urlpatterns = [
    path('', views.home, name='home'),
    path('AjoutEtRetrait', views.AjoutEtRetrait, name='AjoutEtRetrait'),
    path('CorpusAddFct', views.CorpusAddFct, name='CorpusAddFct'),
    path('VisualiseCorpusAdd/<str:NomCorpusAdd>', views.VisualiseCorpusAdd, name='VisualiseCorpusAdd'),
    path('RemoveCorpusAdd', views.RemoveCorpusAdd, name='RemoveCorpusAdd'),
    path('LangueDetectFct/<str:reduction>', views.LangueDetectFct, name='LangueDetectFct'),
    path('CorpusAddEtRemoveInterface/<str:reduction>', views.CorpusAddEtRemoveInterface, name='CorpusAddEtRemoveInterface'),
    path('VisualiseCorpusComplet/<str:NomCorpusComplet>', views.VisualiseCorpusComplet, name='VisualiseCorpusComplet'),
    path('RemoveCorpusComplet', views.RemoveCorpusComplet, name='RemoveCorpusComplet'),
    path('AmeliorPretrait', views.AmeliorPretrait, name='AmeliorPretrait'),
    path('FNROrderInterface', views.FNROrderInterface, name='FNROrderInterface'),
    path('FNROrderResult/<str:id_corpus>/<str:id_dicomot>/<str:id_dicoexpression>', views.FNROrderResult,
         name='FNROrderResult'),
    path('AddDicoMotLemme', views.AddDicoMotLemme, name='AddDicoMotLemme'),
    path('AddDicoMotExpression', views.AddDicoMotExpression, name='AddDicoMotExpression'),
    path('AddDicoSuffixe', views.AddDicoSuffixe, name='AddDicoSuffixe'),
    path('RemoveDicoMotLemme', views.RemoveDicoMotLemme, name='RemoveDicoMotLemme'),
    path('RemoveDicoExpression', views.RemoveDicoExpression, name='RemoveDicoExpression'),
    path('RemoveDicoSuffixe', views.RemoveDicoSuffixe, name='RemoveDicoSuffixe'),
    path('CreateDicoMotPretrait2', views.CreateDicoMotPretrait2, name='CreateDicoMotPretrait2'),
    path('AppliEtLimitPretrait', views.AppliEtLimitPretrait, name='AppliEtLimitPretrait'),
    path('CorpusFinAdd', views.CorpusFinAdd, name='CorpusFinAdd'),
    path('CorpusFinVisualise/<str:corpusfin>', views.CorpusFinVisualise, name='CorpusFinVisualise'),
    path('CorpusFinRemoveInterface', views.CorpusFinRemoveInterface, name='CorpusFinRemoveInterface'),
    path('DownloadDico/<str:fichier>', views.DownloadDico, name='DownloadDico'),
]