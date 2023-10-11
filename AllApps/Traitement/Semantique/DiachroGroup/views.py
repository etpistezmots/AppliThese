from django.shortcuts import render, redirect
from django.conf import settings
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse
import json, os, shutil
from django.http import HttpResponse
from ..DiachroGroup.core.BoucleDiachro import BoucleDiachro
from ..DiachroGroup.core.WriteJson import WriteJson
from ..DiachroGroup.core.ClusterAndCo import ExtractFromEmbedding,DoCluster, DoStopWord, DoPartition, DoCalculPoids,\
    CreateFichiersPoidsOri
from AllApps.Traitement.Semantique.TableauEmb.periph.amont import SelectLastMode, AllModes, TestModelExist, TestModelAccess,\
    TestResultAccess, TestResultExist, SumAndConcatlistAllSelect,ExpandMode, RecupUser, SelectResultFctUser
from AllApps.Traitement.Semantique.TableauEmb.periph.prepaaffiche import InitResultAllSelect
from AllApps.Traitement.Semantique.ReseauExplore.periph.prepaaffiche import InitHome
from AllApps.Traitement.Semantique.ReseauExplore.periph.amont import PrepaTwoResults
from .periph.amont import TestNbrTermesEtClusterOk, CreateDossierTemporaire, CreateDossierSave, CreateDossierResultDia,\
    RecupDataCalcul,RecupDataSave, ModelFormInit, DoTwoResults, TestResultCompare
from .periph.prepaaffiche import   InitModelForResult, InitModelResultBeforeSave, InitResult
from .periph.aval import RemoveOldTempFolder, CopyTempToSave

def test(request, mode, path, perioderevue):
    print(mode)
    print(path)
    print(perioderevue)
    # glove
    # temp---tmpohk_pakj
    # 19611971Annales
    context= {"mode":mode,"path":path,"perioderevue":perioderevue}
    return render(request, 'DiachroGroup/Dendro.html',context)


def homeredirect(request):
    mode_defaut = "glove"
    # selectionne le dernier mode en fonction dernière expé de l'utilisateur (sinon mode par défaut)
    mode = SelectLastMode(request, mode_defaut)
    return redirect('DiachroGroup:home', mode)


def home(request, mode):

    if request.method == 'POST':
        if 'Calculer' in request.POST:
            # renvoie vers tableau (utilise le même socle : Expe, Glove, Word2Vec, FastText)
            return redirect("Tableau:home", mode)

    ########################### INITIALISATION ##########################
    allmodes = AllModes()
    if mode not in allmodes:
        return render(request, 'TableauEmb/Error/ModeNotExist.html')

    # selectionne le dernier modèle de l'utilisateur en fonction mode (sinon None)
    lastmodel = InitHome(request, mode, ModelFormInit)
    if lastmodel:
        return redirect("DiachroGroup:modele", mode, lastmodel.id)
    else:
        context = {"modeactuel":mode, "allmodes": allmodes}
        return render(request, 'DiachroGroup/NoModel.html', context)


def modele(request, mode, modele_id):

    if request.method == 'POST':

        ################ CREATION RESULTATS  #################
        if 'Calculer' in request.POST:

            # renvoie modèles et formulaires en fonction du mode
            DicInitModelD, DicInitFormD = ModelFormInit(mode)

            # pour valider le formulaire reduit qui permet affichage résultat si est valide
            test_form_result = DicInitFormD['resultatdeb'](data=request.POST)

            if test_form_result.is_valid():

                # Recupération des données
                nom, revues, epoques, terme, nresult, user, calculPoidsLabel,\
                compareJustNewRevue, selectLink, couleursRevues,methode_clustering,\
                ncluster, taillecluster, stop_mots = RecupDataCalcul(DicInitModelD,modele_id,test_form_result)

                #Fichier temporaire pour les résultat
                path = CreateDossierTemporaire(mode)

                # test nombre cluster et nombre result OK par rapport nombres d'époques et de revues
                ReponseTest = TestNbrTermesEtClusterOk(nresult,ncluster,epoques,revues)
                if ReponseTest == "notok":
                    return render(request, 'DiachroGroup/Error/NbTermesOuClusters.html')

                ################# COEUR DE L'ALGO (cf core) ######################
                # Préparation boucle en fonction des revues et des époques choisies
                compteur = -1
                ListEpoques = epoques.split(",")
                ListRevues = revues.split(",")
                nclustersplit = ncluster.split(',')

                PathDendro = path + "/Dendro/"
                if not os.path.exists(PathDendro):
                    os.makedirs(PathDendro)

                for EpoqueDecompos in ListEpoques:
                    for Revue in ListRevues:
                        # extract result modele embedding (erreur si mot demandé pas dans les résultats
                        MarqueurDo, error, ResultTerme, ResultChiffre, model, compteur = \
                            ExtractFromEmbedding(mode, nom, Revue, EpoqueDecompos, terme, nresult, compteur)

                        if MarqueurDo:
                            if not error:
                                # clustering
                                idx = DoCluster(model, methode_clustering, ncluster, nclustersplit, compteur, PathDendro, Revue, EpoqueDecompos, ResultTerme)
                                # Terme à exclure résultats si besoin (variable stop_mots)
                                ResultTerme, ResultChiffre, idx = DoStopWord(stop_mots,ResultTerme,ResultChiffre,idx)
                                # production résultat sous forme de partition
                                partition = DoPartition(idx)
                                # Calcul des poids qui vont servir pour comparaison diachronique
                                # Joue aussi sur label par ordre des termes
                                PartitionTermes, PartitionChiffres = DoCalculPoids(calculPoidsLabel,ResultTerme,ResultChiffre,partition, model)
                                # écriture des poids et de l'ordre des termes dans un fichier
                                CreateFichiersPoidsOri(path, Revue, EpoqueDecompos, PartitionTermes, PartitionChiffres)
                            else:
                                shutil.rmtree(path)
                                return render(request, 'ReseauExplore/Error/TermeNotFound.html')
                        else:
                            continue

                # Création dossier résultats pour stocker résultat diachronie
                CreateDossierResultDia(path)
                # application algorithme issu de DiachronicExplorer
                BoucleDiachro(path, revues, epoques, compareJustNewRevue, selectLink)
                # Ecriture du json
                WriteJson(path, epoques, couleursRevues, nom, terme, taillecluster)
                ####################################################################

                # au bout de 25 dossiers temp va enlever le plus ancien
                RemoveOldTempFolder(mode, 25)

                # prepa affichage
                form, modelscselect, allmodes, form2, results, graph, AccesToSave, AccesToCalcul, seuilselect, \
                path_result_transfo, seuil100 = \
                    InitModelResultBeforeSave(request, mode, modele_id, test_form_result, path)


                context = {"form": form, "models": modelscselect, "modeactuel": mode, "allmodes": allmodes,
                           "idmodeleactuel": modele_id, "form2": form2, "graph": graph,
                           "results": results,"AccesToSave": AccesToSave, "AccesToCalcul": AccesToCalcul,
                           "path_result_transfo":path_result_transfo, "seuilselect": str(seuilselect),
                           "seuil100":seuil100}


                return render(request, 'DiachroGroup/result.html', context)

            # formulaire non valide
            else:
                context = {"form": test_form_result}
                return render(request, 'TableauEmb/Error/FormInvalid.html', context)

        if 'Sauver' in request.POST:

            # Cree Dossier save si n'existe pas
            CreateDossierSave(mode)

            # récupère les données ayant servi à l'effectuation des résultats
            terme, nresult, calculPoidsLabel, compareJustNewRevue, SelectLink, couleursRevues, \
            methode_clustering, ncluster, taillecluster, stop_mots, name, pathresult, seuil100 =\
                RecupDataSave(request)

            # récup id de l'"user" ou "user_restrict2last" si superuser
            userencours = RecupUser(request)
            DicInitModelD, DicInitFormD = ModelFormInit(mode)

            # crée le formulaire à sauver
            formToSave = DicInitFormD["resultatfin"](
                    data={"terme": terme, "nresult": nresult, "user_restrict2": userencours,
                          "methode_clustering": methode_clustering, "ncluster": ncluster, "calculPoidsLabel":calculPoidsLabel,
                          "compareJustNewRevue":compareJustNewRevue, "stop_mots":stop_mots, "taillecluster":taillecluster,
                          "selectLink":SelectLink,"couleursRevues":couleursRevues,
                          "nomresult":name,"modelc":DicInitModelD["initial"].objects.get(id=modele_id),"seuil100":seuil100})

            # s'il est valide
            if formToSave.is_valid():
                # sauve dans la base de donnée
                lv = formToSave.save()
                # Copie du dossier temporaire en dossier sauvegardé
                CopyTempToSave(mode, pathresult, name)
                return redirect('DiachroGroup:result', mode, str(modele_id), str(lv.id))

            else:
                context = {"formToSave":formToSave}
                return render(request, 'DiachroGroup/Error/FormulaireEnregistr.html', context)


        ################  Suppr Model #################
        if 'SupprimerMultiModels' in request.POST:
            return redirect("TableauEmb:supprmultimodeles", mode)

        if 'SupprimerOneModel' in request.POST:
            return redirect("TableauEmb:suppronemodele", mode, modele_id)

        ############### Consult all result #####################
        if 'Consulter' in request.POST:
            return redirect("DiachroGroup:resultallselect")


    ################### Test et html initial ######################

    # test mode existe
    allmodes = AllModes()
    if mode not in allmodes:
        return render(request, 'TableauEmb/Error/ModeNotExist.html')

    # test modele existe
    Exist, DicInitModelD, DicInitFormD, Modelc = TestModelExist(mode, modele_id, ModelFormInit)
    if not Exist:
        return render(request, 'TableauEmb/Error/ModeleNotExist.html')

    # test modele access
    Access, ModelscSelect = TestModelAccess(request, DicInitModelD, Modelc)
    if not Access:
        return render(request, 'TableauEmb/Error/ModeleNoAccess.html')


    form, form2, results, graph, AccesToSave, AccesToCalcul, seuilselect, seuil100 = \
        InitModelForResult(request, Modelc, DicInitModelD, DicInitFormD)

    context = {"form": form, "models": ModelscSelect, "modeactuel":mode, "allmodes":allmodes,
               "idmodeleactuel": modele_id, "form2": form2,
               "results": results, "graph":graph, "AccesToSave": AccesToSave, "AccesToCalcul": AccesToCalcul,
               "seuilselect": str(seuilselect),"seuil100":seuil100}

    return render(request, 'DiachroGroup/result.html', context)



def result(request, mode, modele_id, result_id):

    if request.method == 'POST':

        ################  Suppr Result #################
        if 'SupprimerMultiResults' in request.POST:
            return redirect("DiachroGroup:supprmultiresults", mode, modele_id)

        if 'SupprimerOneResult' in request.POST:
            return redirect("DiachroGroup:supproneresult", mode, modele_id, result_id)

        ############### Consult all result #####################
        if 'Consulter' in request.POST:
            return redirect("DiachroGroup:resultallselect")

    ######################### Test et prepa html  ##########################################
    # test mode existe
    allmodes = AllModes()
    if mode not in allmodes:
        return render(request, 'TableauEmb/Error/ModeNotExist.html')

    # test modele existe
    Exist, DicInitModelD, DicInitFormD, Modelc = TestModelExist(mode, modele_id, ModelFormInit)
    if not Exist:
        return render(request, 'TableauEmb/Error/ModeleNotExist.html')

    # test modele access
    Access, ModelscSelect = TestModelAccess(request, DicInitModelD, Modelc)
    if not Access:
        return render(request, 'TableauEmb/Error/ModeleNoAccess.html')

    # test result existe
    Exist, Resultc = TestResultExist(modele_id, result_id, DicInitModelD)
    if not Exist:
        return render(request, 'TableauEmb/Error/ResultNotExist.html')

    # test result access
    Access, ResultsSelect = TestResultAccess(request, DicInitModelD, Modelc, Resultc)
    if not Access:
        return render(request, 'TableauEmb/Error/ResultNoAccess.html')


    form, form2, path_result_transfo, results, graph, AccesToSave, AccesToCalcul, \
    ResultSpeUser, seuilselect = InitResult(request, Modelc, DicInitModelD, DicInitFormD, result_id)

    context = {"form": form, "models": ModelscSelect, "modeactuel": mode, "allmodes": allmodes,
               "idmodeleactuel": modele_id, "form2": form2,
               "results": results, "idresultactuel": result_id, "graph": graph,
               "AccesToSave": AccesToSave, "AccesToCalcul": AccesToCalcul, "ResultSpeUser": ResultSpeUser,
               "path_result_transfo": path_result_transfo, "seuilselect": str(seuilselect)}

    return render(request, 'DiachroGroup/result.html', context)


############################################################
###########    FONCTION SUPPR ET AFFICHE        ##############
#############################################################

def resultallselect(request):
    ''' permet d'afficher tous les résultats
        si plus d'un resultat cochés, appelle fonction suivante : resultallvisu'''

    if request.method == 'POST':

        ConcatListExpeStock, tot = SumAndConcatlistAllSelect(request)

        if tot != 0:
            ConcatListExpeStock = ConcatListExpeStock[:-1]

        if tot == 0:
            ZipModeResult = InitResultAllSelect(request, ModelFormInit)
            context = {'ZipModeResult': ZipModeResult}
            messages.warning(request, "Vous devez au moins selectionner une expe," + "\n" +
                                      " et pour ce module multiexpe :" + "\n" +
                                      "et deux, c'est encore mieux...")

            return render(request, 'DiachroGroup/resultallselect.html', context)

        elif tot == 1:
            error, modeselect = ExpandMode(ConcatListExpeStock[0])
            if not error:
                DicInitModelDselect, DicInitFormDselect = ModelFormInit(modeselect)
                idexpeselect = ConcatListExpeStock[1:]
                expeselect = DicInitModelDselect["resultat"].objects.filter(id=int(idexpeselect))[0]
                modeleselect = expeselect.modelc.id
                url = reverse("DiachroGroup:result", kwargs={'mode': modeselect, 'modele_id': modeleselect, 'result_id':int(idexpeselect)})
                return HttpResponseRedirect(url)
            else:
                return render(request, 'TableauEmb/Error/ModeNotExist.html')

        else:
            ConcatListExpesVisibles, paradefault, formatdefault, tailledefault = PrepaTwoResults(ConcatListExpeStock)
            url = reverse("DiachroGroup:resultallvisu",
                          kwargs={'listexpesvisibles': ConcatListExpesVisibles,
                                  'listexpesstock':ConcatListExpeStock,
                                  'paraselect': paradefault,
                                  'formselect': formatdefault,
                                  'tailleselect': tailledefault
                                  })

            return HttpResponseRedirect(url)


    ########### Initialisation ##################
    ZipModeResult = InitResultAllSelect(request, ModelFormInit)
    context = {'ZipModeResult': ZipModeResult}
    return render(request, 'DiachroGroup/resultallselect.html', context)



def resultallvisu(request, listexpesvisibles, listexpesstock, paraselect, formselect, tailleselect):

    errorG = TestResultCompare(request, listexpesvisibles, listexpesstock, paraselect, formselect, tailleselect)

    if not errorG:

        expe1R, expe2R,  Mode1, Mode2, expesR, dict1, dict2, \
        parachoices, formchoices, taillechoices, ZipExpe1, ZipExpe2, \
        path_result_transfo1, path_result_transfo2, seuilselect1, seuilselect2\
            = DoTwoResults(listexpesvisibles,listexpesstock,paraselect)

        context = {"listexpesvisibles":listexpesvisibles, "listexpesstock":listexpesstock,
                   "expe1R":expe1R, "expe2R":expe2R, "expesR": expesR,
                   "dict1":dict1, "dict2":dict2, "mode1": Mode1, "mode2": Mode2,
                   "ZipExpe1": ZipExpe1, "ZipExpe2": ZipExpe2,
                   "paraselect":paraselect, "parachoices":parachoices,
                   "formselect": formselect, "formchoices": formchoices,
                   "tailleselect": tailleselect, "taillechoices": taillechoices,
                   "path_result_transfo1":path_result_transfo1,"path_result_transfo2":path_result_transfo2,
                   "seuilselect1": str(seuilselect1),"seuilselect2": str(seuilselect2)}

        if formselect == "horizontal":
            return render(request, 'DiachroGroup/horizontal.html', context)
        if formselect == "vertical":
            return render(request, 'DiachroGroup/vertical.html', context)
    else:
        return render(request, 'TableauEmb/Error/CompareError.html')



def supproneresult(request, mode, modele_id, result_id):
    # test mode existe
    allmodes = AllModes()
    if mode not in allmodes:
        return render(request, 'TableauEmb/Error/ModeNotExist.html')

    # test modele existe
    Exist, DicInitModelD, DicInitFormD, Modelc = TestModelExist(mode, modele_id, ModelFormInit)
    if not Exist:
        return render(request, 'TableauEmb/Error/ModeleNotExist.html')

    # test modele access
    Access, ModelscSelect = TestModelAccess(request, DicInitModelD, Modelc)
    if not Access:
        return render(request, 'TableauEmb/Error/ModeleNoAccess.html')

    # test result existe
    Exist, Resultc = TestResultExist(modele_id, result_id, DicInitModelD)
    if not Exist:
        return render(request, 'TableauEmb/Error/ResultNotExist.html')

    # test result access
    Access, ResultsSelect = TestResultAccess(request, DicInitModelD, Modelc, Resultc)
    if not Access:
        return render(request, 'TableauEmb/Error/ResultNoAccess.html')

    # réservé au super-utilisateur ou au utilisateur ayant droit
    userexpe = Resultc.user_restrict2
    if request.user.is_superuser or (str(request.user.id) in userexpe.split(",")):
        SupprResult(mode, result_id)
        return redirect('DiachroGroup:modele', mode, modele_id)
    else:
        return render(request, 'TableauEmb/Error/SupprImpossible.html')


def supprmultiresults(request, mode, modele_id):

    if request.method == 'POST':
        if 'Supprimer' in request.POST:
            ListResultatsASuppr = request.POST.getlist('selected_resultat')
            DicInitModelD, DicInitForm = ModelFormInit(mode)
            for resultatsuppr in ListResultatsASuppr:

                # test result existe
                Exist, Resultc = TestResultExist(modele_id, resultatsuppr, DicInitModelD)
                if not Exist:
                    return render(request, 'TableauEmb/Error/ResultNotExist.html')

                userexpe = Resultc.user_restrict2
                if request.user.is_superuser or (str(request.user.id) in userexpe.split(",")):
                    SupprResult(mode, resultatsuppr)
                else:
                    return render(request, 'TableauEmb/Error/SupprImpossible.html')

            return redirect('DiachroGroup:modele', mode, modele_id)

        if 'Retour' in request.POST:
            return redirect('DiachroGroup:modele', mode, modele_id)

    ###### Test et prepa html ##############

    # test mode existe
    allmodes = AllModes()
    if mode not in allmodes:
        return render(request, 'TableauEmb/Error/ModeNotExist.html')

    # test modele existe
    Exist, DicInitModelD, DicInitFormD, Modelc = TestModelExist(mode, modele_id, ModelFormInit)
    if not Exist:
        return render(request, 'TableauEmb/Error/ModeleNotExist.html')

    # test modele access
    Access, ModelscSelect = TestModelAccess(request, DicInitModelD, Modelc)
    if not Access:
        return render(request, 'TableauEmb/Error/ModeleNoAccess.html')

    # réservé au super-utilisateur ou au utilisateur ayant droit
    usermodel = Modelc.user_restrict
    if request.user.is_superuser or (str(request.user.id) in usermodel.split(",")):
        DicInitModelDactuel, DicInitFormDactuel = ModelFormInit(mode)
        ResultatsAll = DicInitModelDactuel["resultat"].objects.all()
        resultats = SelectResultFctUser(request, ResultatsAll)
        context = {'modeactuel': mode, 'resultats': resultats}
        return render(request, 'DiachroGroup/supprselectresult.html', context)
    else:
        return render(request, 'TableauEmb/Error/SupprImpossible.html')


def SupprResult(mode, result_id):
    DicInitModelDactuel, DicInitFormDactuel = ModelFormInit(mode)
    DicActuel = DicInitModelDactuel["resultat"].objects.get(id=result_id)
    DicInitModelDactuel["resultat"].objects.filter(id=result_id).delete()
    shutil.rmtree(settings.RESULT_SEMANTIC_DIR + "/Diachro/" + mode + "/save/" + str(DicActuel.nomresult))

############################################################
######## FONCTIONS APPEL DEPUIS JAVASCRIPT  ##############
###########################################################


def jsonimport(request, mode, adresse):
    path_split = adresse.split("---")

    if path_split[0]=="temp":
        file  = settings.RESULT_SEMANTIC_DIR + "/Diachro/" + mode + "/temp/" + path_split[1] + "/4)Json/" + path_split[1] + ".json"
    elif path_split[0]=="save":
        file  = settings.RESULT_SEMANTIC_DIR + "/Diachro/" + mode + "/save/" + path_split[1] + "/4)Json/" + path_split[1]  + ".json"
    else:
        response = HttpResponse()
        return response

    print(file)
    with open(file, 'r') as f:
        data = json.loads(f.read())
    return JsonResponse(data)


def affichedendro(request, mode, path, perioderevue):

    path_split= path.split("---")

    if path_split[0]=="temp":
        file  = settings.RESULT_SEMANTIC_DIR + "/Diachro/" + mode + "/temp/" + path_split[1] + "/Dendro/"\
                  + perioderevue + ".png"
    elif path_split[0]=="save":
        file  = settings.RESULT_SEMANTIC_DIR + "/Diachro/" + mode + "/save/" +path_split[1] + "/Dendro/"\
                  + perioderevue + ".png"
    else:
        response = HttpResponse()
        return response

    image_png = open(file, "rb").read()
    response = HttpResponse(image_png, content_type='image/png')
    return response




