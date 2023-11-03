from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect
# Create your views here.

def home(request):
    return render(request,'Introduction/home.html')


def VersTheseMBeligne(request):
    return render(request, 'Introduction/TheseMBeligne.html')

def AfficheEx(request, option):

    Article = "geo_0003-4010_1966_num_75_409_17238"
    Dossier = Article.rsplit('_',1)[0]
    AdresseGenerale = settings.DATA_DIR + "/revues/geo/" + Dossier
    if option == "tei" or option == "erudit":
        fichier = AdresseGenerale + "/" + option + "/article_" + Article  + "_" + option + ".xml"
    else :
        redirect("DelimitCorpus:home")

    xml_data = open(fichier, "r").read()
    return HttpResponse(xml_data, content_type='text/xml')



def DownloadEx(request,fichierspe, revue):

    if fichierspe == "keyword":
        FichierResult = settings.DATA_DIR + "/BDPerseeMotCle/" + revue + "_keywordsComplet.csv"
    elif fichierspe == "docstriple":
        FichierResult = settings.DATA_DIR + "/DocsTripleStore/PERSEE_" + revue + "_doc_2017-01-09.rdf"
    elif fichierspe == "perstriple":
        FichierResult = settings.DATA_DIR + "/PersonnesTripleStore/PERSEE_" + revue + "_persons_2017-01-06.rdf"
    else:
        return render(request, 'Introduction/home.html')

    response = HttpResponse(open(FichierResult, 'rb').read())

    if fichierspe == "keyword":
        response['Content-Type'] = 'csv'
        response['Content-Disposition'] = 'attachment; filename=keywords_' + revue + '.csv'
    elif fichierspe == "docstriple":
        response['Content-Type'] = ' application/rdf+xml'
        response['Content-Disposition'] = 'attachment; filename=docstriple_' + revue + '.rdf'
    elif fichierspe == "perstriple":
        response['Content-Type'] = ' application/rdf+xml'
        response['Content-Disposition'] = 'attachment; filename=perstriple_' + revue + '.rdf'
    else:
        return render(request, 'DelimitCorpus/home.html')

    return response




