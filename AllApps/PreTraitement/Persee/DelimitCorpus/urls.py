from django.urls import path

from AllApps.PreTraitement.Persee.DelimitCorpus import views

app_name = 'DelimitCorpus'
urlpatterns = [
    path('', views.home, name='home'),
    path('reduction/<int:reduction_id>', views.reduction, name='reduction'),
    path('SupprimReduction', views.SupprReduc, name='SupprReduc'),
    path('Download/<str:sujet>/<str:revue>/<str:extension>', views.Download, name='Download'),
    path('NumeroResult/<str:revue>', views.NumeroResult, name='NumeroResult'),
    path('DocumentResult/<str:revue>', views.DocumentResult, name='DocumentResult'),
    path('DocHorsNormeResult/<str:revue>', views.DocHorsNormeResult, name='DocHorsNormeResult'),
    path('TypeDocArticleResult/<str:revue>', views.TypeDocArticleResult, name='TypeDocArticleResult'),
    path('LangArticleResult/<str:revue>', views.LangArticleResult, name='LangArticleResult'),
    path('CategArticleResult/<str:revue>/<str:mode>', views.CategArticleResult, name='CategArticleResult'),
    path('ArticleVideResult/<str:revue>', views.ArticleVideResult, name='ArticleVideResult'),
    path('VersDelimitConcrete', views.VersDelimitConcrete, name='VersDelimitConcrete'),
    path('AfficheEx/<str:option>', views.AfficheEx, name='AfficheEx'),
    path('DownloadEx/<str:fichierspe>/<str:revue>', views.DownloadEx, name='DownloadEx'),
]