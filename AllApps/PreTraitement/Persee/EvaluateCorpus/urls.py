from django.urls import path

from AllApps.PreTraitement.Persee.EvaluateCorpus import views

app_name = 'EvaluateCorpus'
urlpatterns = [
    path('CountDocAndWord/<str:corpusfin>', views.CountDocAndWord, name='CountDocAndWord'),
    path('SelectEchantillonEvaluate/<str:corpusfin>/<int:n_docs>/<int:n_mots>/<int:n_eval>', views.SelectEchantillonEvaluate, name='SelectEchantillonEvaluate'),
    path('EvaluateDetail/<str:corpusfin>/<int:n_docs>/<int:n_mots>/<int:n_eval>/<str:doc>', views.EvaluateDetail, name='EvaluateDetail'),
    path('CreateCorpusArticlePlusCrNonLem2', views.CreateCorpusArticlePlusCrNonLem2, name='CreateCorpusArticlePlusCrNonLem2'),
]