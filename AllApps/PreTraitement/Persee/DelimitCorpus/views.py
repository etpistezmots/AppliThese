
from django.shortcuts import render ,redirect
from django.http import HttpResponse
from django.conf import settings
import os, shutil
from django.contrib import messages
from .models import Revue, CorpusEtude
from .forms import VersionReducFormRed
from pandas import read_csv
from AllApps.PreTraitement.Persee.DelimitCorpus.core import ExplicitRevue, GeneralFonction, FctSpeCreateNumero, FctSpeCreateDocument,\
    FctSpeCreateDocHorsNorme, FctSpeCreateTypeDocArticle, FctSpeCreateLangArticle, FctSpeCreateArticleVide, FctSpeCreateCategArticle,\
    FctSpeRecupResultSimple, FctSpeRecupResultComplexe, SelectReducFctUser, InsertMesDonneesPersee, DoReduction


def home(request):
    return render(request,'DelimitCorpus/home.html')


#################  ENSEMBLE DES FONCTIONS D'EXPLORATION ###############

# Structure commune avec fonction de traitement (create) et de récupération
# un peu répétitif mais un "return render" ne peut pas être dans une sous fonction.
# voir pour détail traitement FctSpe dans core.py

def NumeroResult(request, revue):
    '''Pour recenser tous les numeros d'une revue'''
    error, revuerealname, autrerevue = ExplicitRevue(revue)
    if error:
        return render(request, 'DelimitCorpus/home.html')

    NbreResult, Result = GeneralFonction(FctSpeCreateNumero, FctSpeRecupResultSimple, revue, "Numero", sortedresult=True)
    context = {"Result": Result, "revueperseeref": revue,
               "revuerealname": revuerealname, "NbreResult": NbreResult,
               "autrerevue": autrerevue}

    return render(request, 'DelimitCorpus/III1NumeroResult.html', context)


def DocumentResult(request, revue):
    '''Pour recenser tous les documents d'une revue'''
    error, revuerealname, autrerevue = ExplicitRevue(revue)
    if error:
        return render(request, 'DelimitCorpus/home.html')

    NbreResult, Result = GeneralFonction(FctSpeCreateDocument, FctSpeRecupResultSimple, revue, "Document", sortedresult=True)
    context = {"Result": Result, "revueperseeref": revue,
               "revuerealname": revuerealname, "NbreResult": NbreResult,
               "autrerevue": autrerevue}
    return render(request, 'DelimitCorpus/III2DocumentResult.html', context)


def DocHorsNormeResult(request, revue):
    """ Méthode qui permet d'afficher les fichiers qui ne correspondent pas à une "norme"
        la norme est spécifiée par l'expression régulière
        Voir la ligne regex ci dessous dans la focntion spe
    """
    error, revuerealname, autrerevue = ExplicitRevue(revue)
    if error:
        return render(request, 'DelimitCorpus/home.html')

    NbreResult, Result = GeneralFonction(FctSpeCreateDocHorsNorme, FctSpeRecupResultSimple, revue, "DocHorsNorme",
                                         sortedresult=True)
    context = {"Result": Result, "revueperseeref": revue,
               "revuerealname": revuerealname, "NbreResult": NbreResult,
               "autrerevue": autrerevue}
    return render(request, 'DelimitCorpus/III3DocHorsNormeResult.html', context)


def TypeDocArticleResult(request, revue):
    """ 
    Le type a documentée par Persée en métadonnée
    "article", compte-rendu", "note biblio",....
    """
    error, revuerealname, autrerevue = ExplicitRevue(revue)
    if error:
        return render(request, 'DelimitCorpus/home.html')

    NbreResult, Result = GeneralFonction(FctSpeCreateTypeDocArticle, FctSpeRecupResultSimple, revue, "TypeDocArticle")
    context = {"Result": Result, "revueperseeref": revue,
               "revuerealname": revuerealname, "NbreResult": NbreResult,
               "autrerevue": autrerevue}
    return render(request, 'DelimitCorpus/III4TypeDocArticleResult.html', context)


def LangArticleResult(request, revue):
    """ 
    Affiche la langue des articles
    """
    error, revuerealname, autrerevue = ExplicitRevue(revue)
    if error:
        return render(request, 'DelimitCorpus/home.html')


    NbreResult, Result = GeneralFonction(FctSpeCreateLangArticle, FctSpeRecupResultSimple, revue, "LangArticle")
    context = {"Result": Result, "revueperseeref": revue,
               "revuerealname": revuerealname, "NbreResult": NbreResult,
               "autrerevue": autrerevue}
    return render(request, 'DelimitCorpus/III5LangArticleResult.html', context)



def ArticleVideResult(request, revue):
    """  Cherche les articles ne contenant aucun mot """
    error, revuerealname, autrerevue = ExplicitRevue(revue)
    if error:
        return render(request, 'DelimitCorpus/home.html')

    NbreResult, Result = GeneralFonction(FctSpeCreateArticleVide, FctSpeRecupResultComplexe, revue, "ArticleVide", ncomplex=4)
    context = {"Result": Result, "revueperseeref": revue,
               "revuerealname": revuerealname, "NbreResult": NbreResult,
               "autrerevue": autrerevue}
    return render(request, 'DelimitCorpus/III6ArticleVideResult.html', context)



def CategArticleResult(request, revue, mode):
    """  Notes:
            Les catégories des articles renvoient au classement dans la table des matières de la revue
            Par ex dans les Annales jusqu'à 1960:
            on va avoir souvent une première grande partie intitulée "géographie générale" avec quelques articles
            puis une "géographie régionale" avec quelques articles.
            Pour chaque article, on récupère cette info que l'on a appelé ici "catégorie"
            Pour info, pour chaque aussi  catégorie, on récupère aussi le nombre de page
            Permet pour chaque catégorie, d'avoir le nombre de page moyen et médian
    """

    if mode == "brut":
        FichierResult = settings.RESULT_PRETRAIT_DIR + "/DelimitCorpus/CategArticle" + revue + "Brut.csv"
    else:
        FichierResult = settings.RESULT_PRETRAIT_DIR + "/DelimitCorpus/CategArticle" + revue + "Agreg.csv"

    dossierref = settings.DATA_DIR + "/revues/" + revue

    # realname
    error, revuerealname, autrerevue = ExplicitRevue(revue)
    if error:
        return render(request, 'DelimitCorpus/home.html')

    # cree le dossier si n'existe pas
    dossier = FichierResult.rsplit("/", 1)[0]
    if not os.path.exists(dossier):
        os.makedirs(dossier)

    # si le fichier de résultat n'a pas encore été crée
    if not os.path.isfile(FichierResult):
        # récupération des données
        CatMoyMed = FctSpeCreateCategArticle(FichierResult,dossierref,mode)
    else:
        CatMoyMed = read_csv(FichierResult)

    # pour mettre l'index et le nom des colonnes sur la même ligne
    CatMoyMed.columns.name = CatMoyMed.index.name
    CatMoyMed.index.name = None

    # cherche la moyenne de page par catégorie et l'enregistre dans .csv
    tableauhtml = CatMoyMed.to_html(classes='mystyle')


    context= {"tableauhtml":tableauhtml,"revueperseeref":revue,
              "revuerealname": revuerealname, "autrerevue":autrerevue, "mode": mode}

    return render(request, 'DelimitCorpus/III7CategArticleResult.html', context)



def Download(request, sujet, revue, extension):
    '''Pour telecharger un fichier'''
    FichierResult = settings.RESULT_PRETRAIT_DIR + "/DelimitCorpus/" + sujet + revue + "." + extension
    response = HttpResponse(open(FichierResult, 'rb').read())

    if os.path.isfile(FichierResult):

        if extension == "txt" or extension == "csv":
            response['Content-Type'] = 'text/plain'
        # cas image
        else:
            response['Content-Type'] = 'image/' + extension
        response['Content-Disposition'] = 'attachment; filename=' + sujet + revue + "." + extension
        return response

    else:
        return render(request, 'DelimitCorpus/home.html')


###################### PARTIE III ############################

def VersDelimitConcrete(request):
    '''Vers 3)a)
        Les fonctions pour remplir la base de données
        sont à la fin de cette page : voir InsertMesDonneesPersee
        qui renvoient aux autres fonctions'''
    ################ Bouton pour emplir DB avec données de base  #################
    if 'InsererInDB' in request.POST:
        RevueDejaInDB = Revue.objects.all()
        if not RevueDejaInDB:
            InsertMesDonneesPersee()
            messages.add_message(request, messages.INFO, 'Insertion OK')
        else:
            messages.add_message(request, messages.INFO, 'Insertion déjà réalisée')
        return render(request, 'DelimitCorpus/IV1VersDelimitConcrete.html')

    return render(request, 'DelimitCorpus/IV1VersDelimitConcrete.html')



def reduction(request, reduction_id):
    ''' Permet d'effectuer la réduction'''
    if request.method == 'POST':
        if 'Effectuer' in request.POST:
            formToSave = VersionReducFormRed(data=request.POST)
            # si le formulaire est valide
            if formToSave.is_valid():
                # sauve les donneés dans la bd
                lv = formToSave.save()
                # récupération des données propres
                donnees = formToSave.cleaned_data

                # corpus étude en cours
                VNEnCours = CorpusEtude.objects.filter(nom=donnees["nom"])[0]

                DoReduction(donnees,VNEnCours)

                # Renvoie vers la réduction qui vient d'être effectué
                reductionsall = CorpusEtude.objects.all()
                reductionsselect = SelectReducFctUser(request, reductionsall)
                form = VersionReducFormRed(instance=VNEnCours)
                context = {"form": form, "reduction_id": VNEnCours.id, "reductions": reductionsselect}
                return render(request, 'DelimitCorpus/3cFaireReduction.html', context)

            # si le formulaire n'est pas valide !
            else:
                messages.add_message(request, messages.INFO, 'La réduction demandée a échouée')
                reductionsall = CorpusEtude.objects.all()
                reductionsselect = SelectReducFctUser(request, reductionsall)
                form = VersionReducFormRed(data=request.POST)
                context = {"form": form, "reduction_id": 0, "reductions": reductionsselect}
                return render(request, 'DelimitCorpus/IV3FaireReduction.html', context)

    ########### test et prepa html ############

    reductionsall = CorpusEtude.objects.all()
    reductionsselect = SelectReducFctUser(request, reductionsall)

    # a partir du home, appelle avec reduction_id = 0
    # correspond demande de nouvelle réduction
    # sinon, on cherche si réduction existe bien et si user a un accès
    if reduction_id != 0:
        VNtest = CorpusEtude.objects.filter(id=reduction_id)
        if not VNtest.exists():
            return render(request, 'DelimitCorpus/ErrorCorpusNotExist.html')

        VNdemande = VNtest[0]
        if VNdemande not in reductionsselect:
            return render(request, 'DelimitCorpus/ErrorCorpusNoAccess.html')

        form = VersionReducFormRed(instance=VNdemande)

    # si reduction_id = 0
    else:
        if len(reductionsselect)>0:
        # remplit formulaire avec première réduction
            form = VersionReducFormRed(instance=reductionsselect[0])
        else:
            form = VersionReducFormRed()


    context = {"form": form, "reduction_id": reduction_id, "reductions": reductionsselect}
    return render(request, 'DelimitCorpus/IV3FaireReduction.html', context)


def SupprReduc(request):
    if request.method == 'POST':
        if 'Supprimer' in request.POST:

            if request.user.is_superuser:
                ReducASuppr = request.POST.get("reduc")
                VNefface = CorpusEtude.objects.get(nom=ReducASuppr)
                AdresseResult1 = settings.RESULT_PRETRAIT_DIR + "/DelimitText/ExtractBase/" + VNefface.nom
                AdresseResult2 = settings.RESULT_PRETRAIT_DIR + "/AmeliorText/" + VNefface.nom
                # élimination des dossiers en fonction avancée
                # attention en théorie, il faudrait allait plus loin
                # sur CorpusComplet, sur CorpusFin et sur les expés associées pour effacer tous les dossiers
                if VNefface.SyntheseTransformRef is None :
                    shutil.rmtree(AdresseResult1)
                else:
                    shutil.rmtree(AdresseResult1)
                    shutil.rmtree(AdresseResult2)
                VNefface.delete()
                # message confirmation
                messages.add_message(request, messages.INFO, 'La réduction ' + ReducASuppr + ' a bien été effacée')

                reductionsall = CorpusEtude.objects.all()
                reductionsselect = SelectReducFctUser(request, reductionsall)
                context = {"reductions": reductionsselect}
                return render(request, 'DelimitCorpus/SupprimReduction.html', context)
            else:
                return render(request, 'DelimitCorpus/ErrorSupprImpossible.html')

    if request.user.is_superuser:
        reductionsall = CorpusEtude.objects.all()
        reductionsselect = SelectReducFctUser(request, reductionsall)
        context = {"reductions": reductionsselect}
        return render(request, 'DelimitCorpus/SupprimReduction.html', context)
    else:
        return render(request, 'DelimitCorpus/ErrorSupprImpossible.html')




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





