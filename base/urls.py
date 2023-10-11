"""interface4 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
path('', include('general.urls')),
    path('present/', include('AllApps.Introduction.urls')),
    path('etatlieux/', include('AllApps.EtatDesLieux.urls')),
    path('delimit/', include('AllApps.PreTraitement.Persee.DelimitCorpus.urls')),
    path('amelior/', include('AllApps.PreTraitement.Persee.AmeliorText.urls')),
    path('finalise/', include('AllApps.PreTraitement.Persee.FinaliseCorpus.urls')),
    path('evaluate/', include('AllApps.PreTraitement.Persee.EvaluateCorpus.urls')),
    path('lextablocc/', include('AllApps.Traitement.Lexical.TableauOcc.urls')),
    path('semtablemb/', include('AllApps.Traitement.Semantique.TableauEmb.urls')),
    path('semreseauexplo/', include('AllApps.Traitement.Semantique.ReseauExplore.urls')),
    path('semcluster/', include('AllApps.Traitement.Semantique.Cluster.urls')),
    path('semdiachro/', include('AllApps.Traitement.Semantique.DiachroGroup.urls')),
    path('txtconstructresult/', include('AllApps.Traitement.Semantique.TxtTheseConstructResult.urls')),
    path('txtdiscu/', include('AllApps.Traitement.Semantique.TxtTheseDiscussion.urls')),
    path('conclu/', include('AllApps.Conclusion.urls')),
    path('biblio/', include('AllApps.Biblio.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('users.urls')),
    path('accounts/', include('django.contrib.auth.urls'))
]
