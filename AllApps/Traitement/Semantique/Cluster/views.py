import  shutil
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from AllApps.Traitement.Semantique.ReseauExplore.core.Result import allresult
from AllApps.Traitement.Semantique.TableauEmb.periph.prepaaffiche import InitResultAllSelect
from AllApps.Traitement.Semantique.TableauEmb.periph.amont import RecupUser, SelectLastMode, TestModelExist, \
    TestModelAccess, AllModes, TestResultExist, TestResultAccess, SumAndConcatlistAllSelect, ExpandMode, SelectResultFctUser
from AllApps.Traitement.Semantique.ReseauExplore.periph.prepaaffiche import InitHome
from AllApps.Traitement.Semantique.ReseauExplore.periph.amont import PrepaTwoResults
from .periph.prepaaffiche import InitModelForResult, InitModelResultBeforeSave, InitResult
from .periph.amont import RecupDataCalcul, RecupDataSave, PathResultCreate, ModelFormInit, CalculDiagrammeTaille, \
    DoTwoResults, TestResultCompare, EnregistrTemp, SavePerm
from .DoCluster import clustering



def homeredirect(request):

    mode_defaut = "glove"
    # selectionne le dernier mode en fonction dernière expé de l'utilisateur (sinon mode par défaut)
    mode = SelectLastMode(request, mode_defaut)
    return redirect('Cluster:home', mode)


def home(request, mode):

    if request.method == 'POST':

        ################ Voir All Expe #################
        if 'Consulter' in request.POST:
            return redirect("Cluster:resultallselect")


    ########################### Test et html initial ##########################

    allmodes = AllModes()
    if mode not in allmodes:
        return render(request, 'TableauEmb/Error/ModeNotExist.html')

    # selectionne le dernier modèle de l'utilisateur en fonction mode (sinon None)
    lastmodel = InitHome(request, mode, ModelFormInit)
    if lastmodel:
        return redirect("Cluster:modele", mode, lastmodel.id)
    else:
        context = {"modeactuel": mode, "allmodes": allmodes}
        return render(request, 'Cluster/NoModel.html', context)



def modele(request, mode, modele_id):

    if request.method == 'POST':

        ################ DO RESULT  #################
        if 'Calculer' in request.POST:

            # renvoie modèles et formulaires en fonction du mode
            DicInitModelD, DicInitFormD = ModelFormInit(mode)

            # pour valider le formulaire reduit qui permet affichage résultat si est valide
            test_form_result = DicInitFormD['resultatsimple'](data=request.POST)

            if test_form_result.is_valid():

                nom, revue, epoque, terme, nresult, user, methode_clustering, ncluster, link, color_singleton = \
                    RecupDataCalcul(DicInitModelD,modele_id,test_form_result)

                # si le nombre de cluster supérieur nombre de mots, création d'une erreur. D'où cet ajout
                if ncluster > nresult:
                    ncluster = nresult

                # charge le modèle réduit
                error, ResultTerme, model = allresult(mode, nom, revue, epoque, terme, nresult, retourmodelered=True)

                if not error:

                    nodes_list, edges_list = clustering(nresult, methode_clustering, ncluster,link, ResultTerme, model, color_singleton)

                    path_result_transfo = EnregistrTemp(mode, methode_clustering)

                    taillediagramme = CalculDiagrammeTaille(nresult, methode_clustering)

                    ######## pour affichage html
                    form, modelscselect, allmodes, form2, results, AccesToSave, AccesToCalcul, graph =\
                        InitModelResultBeforeSave(request, mode, modele_id, terme, nresult, revue, epoque, user,
                                                    methode_clustering, ncluster, link, color_singleton)

                    context = {"form": form, "models": modelscselect, "modeactuel": mode, "allmodes": allmodes,
                               "idmodeleactuel": modele_id, "form2": form2, "graph":graph, "revuechoixlast":revue, "epoquechoixlast":epoque,
                               "results": results, "nodes_list": nodes_list, "edges_list": edges_list,
                               "AccesToSave": AccesToSave, "AccesToCalcul": AccesToCalcul, "taillediagramme":taillediagramme,
                               "methode_clustering":methode_clustering, "path_result_transfo":path_result_transfo}


                    return render(request, 'Cluster/result.html', context)

                else:
                    return render(request, 'ReseauExplore/Error/TermeNotFound.html')
            # formulaire non valide
            else:
                context = {"form": test_form_result}
                return render(request, 'TableauEmb/Error/FormInvalid.html', context)


        ################ SAVE RESULT  #################

        if 'Sauver' in request.POST:

            terme, nresult, revue, epoque, name, testnoderecup, testedgerecup, pathresult, methode_clustering,\
            ncluster, link, color_singleton = RecupDataSave(request)

            # récup id de l'"user" ou "user_restrict2last" si superuser
            userencours = RecupUser(request)
            # crée le formulaire à sauver
            DicInitModelD, DicInitFormD = ModelFormInit(mode)
            DicModelc = DicInitModelD["initial"].objects.get(id=modele_id)

            formToSave = DicInitFormD["resultatfin"](data={"terme": terme, "nresult": nresult, "user_restrict2": userencours,
                                                           "methode_clustering": methode_clustering, "ncluster":ncluster,
                                                           "link":link,"color_singleton":color_singleton,"choixrevue":revue,
                                                           "choixepoque":epoque,"modelc":DicModelc,"nomresult":name})

            # s'il est valide
            if formToSave.is_valid():
                # sauve dans la base de donnée
                lv = formToSave.save()
                # sauve les noeuds et les liens à l'adresse voulue
                pathresultsave = PathResultCreate(request, mode, str(lv.nomresult))
                ErrorSave = SavePerm(mode, name, pathresult, pathresultsave, methode_clustering, testnoderecup, testedgerecup)

                if not ErrorSave:
                    return redirect('Cluster:result', mode, str(modele_id), str(lv.id))
                else:
                    return render(request, 'Cluster/Error/PbSave.html')

            else:
                context = {"form": formToSave}
                return render(request, 'TableauEmb/Error/FormInvalid.html', context)


        ################  Suppr Model #################
        if 'SupprimerMultiModels' in request.POST:
            return redirect("TableauEmb:supprmultimodeles", mode)

        if 'SupprimerOneModel' in request.POST:
            return redirect("TableauEmb:suppronemodele", mode, modele_id)

        ############### Consult all result #####################
        if 'Consulter' in request.POST:
            return redirect("Cluster:resultallselect")


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

    # prepa html
    form, form2, results, graph, AccesToSave, AccesToCalcul = InitModelForResult(request, Modelc, DicInitModelD, DicInitFormD)

    context = {"form": form, "models": ModelscSelect, "modeactuel":mode, "allmodes":allmodes,
               "idmodeleactuel": modele_id, "form2": form2,
               "results": results, "graph":graph, "AccesToSave": AccesToSave, "AccesToCalcul": AccesToCalcul}

    return render(request, 'Cluster/result.html', context)


def result(request, mode, modele_id, result_id):

    if request.method == 'POST':

        ################  Suppr Result #################
        if 'SupprimerMultiResults' in request.POST:
            return redirect("Cluster:supprmultiresults", mode, modele_id)

        if 'SupprimerOneResult' in request.POST:
            return redirect("Cluster:supproneresult", mode, modele_id, result_id)

        ############### Consult all result #####################
        if 'Consulter' in request.POST:
            return redirect("Cluster:resultallselect")


    ############### Test et prepa html #################

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

    # prepa html
    form, form2, results, nodes_list, edges_list, AccesToSave, AccesToCalcul, \
    ResultSpeUser, taillediagramme, methode_clustering, graphic, graph, path_result_transfo =\
        InitResult(request, mode, Modelc, DicInitModelD, DicInitFormD, result_id)


    context = {"form": form, "models": ModelscSelect, "modeactuel": mode, "allmodes": allmodes,
               "idmodeleactuel": modele_id, "form2": form2, "nodes_list": nodes_list,"edges_list": edges_list,
               "results": results, "idresultactuel": result_id, "graph": graph,
               "AccesToSave": AccesToSave, "AccesToCalcul": AccesToCalcul, "ResultSpeUser": ResultSpeUser,
               "graphic": graphic, "taillediagramme":taillediagramme, "methode_clustering":methode_clustering,
               "path_result_transfo":path_result_transfo}


    return render(request, 'Cluster/result.html', context)



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
            messages.warning(request, "Vous devez au moins selectionner une expe," + "\n" +
                                      " et pour ce module multiexpe :" + "\n" +
                                      "et deux, c'est encore mieux...")
            context = {'ZipModeResult': ZipModeResult}
            return render(request, 'Cluster/resultallselect.html', context)

        elif tot == 1:

            error, modeselect = ExpandMode(ConcatListExpeStock[0])
            if not error:
                DicInitModelDselect, DicInitFormDselect = ModelFormInit(modeselect)
                idexpeselect = ConcatListExpeStock[1:]
                expeselect = DicInitModelDselect["resultat"].objects.filter(id=int(idexpeselect))[0]
                modeleselect = expeselect.modelc.id
                return redirect('Cluster:result', modeselect, modeleselect, idexpeselect)
            else:
                return render(request, 'TableauEmb/Error/ModeNotExist.html')

        else:
            ConcatListExpesVisibles, paradefault, formatdefault, tailledefault = PrepaTwoResults(ConcatListExpeStock)
            return redirect('Cluster:resultallvisu', ConcatListExpesVisibles, ConcatListExpeStock, paradefault, formatdefault, tailledefault)


    ########### Prepa Html base  ##################
    ZipModeResult = InitResultAllSelect(request, ModelFormInit)
    context = {'ZipModeResult': ZipModeResult}
    return render(request, 'Cluster/resultallselect.html', context)



def resultallvisu(request, listexpesvisibles, listexpesstock, paraselect, formselect, tailleselect):

    errorG = TestResultCompare(request, listexpesvisibles, listexpesstock, paraselect, formselect, tailleselect)

    if not errorG:

        expe1R, expe2R, expesR, nodes_list1, edges_list1, nodes_list2, edges_list2, dict1, dict2, \
        parachoices, formchoices, taillechoices, taillediagramme1, taillediagramme2, ZipExpe1, ZipExpe2 \
            = DoTwoResults(listexpesvisibles,listexpesstock,paraselect)

        context = {"listexpesvisibles":listexpesvisibles, "listexpesstock":listexpesstock,
                   "expe1R":expe1R, "expe2R":expe2R, "expesR": expesR, "dict1":dict1, "dict2":dict2, "paraselect":paraselect, "parachoices":parachoices,
                   "formselect": formselect, "formchoices": formchoices, "tailleselect": tailleselect, "taillechoices": taillechoices,
                   "nodes_list1": nodes_list1, "edges_list1": edges_list1, "nodes_list2": nodes_list2,"edges_list2": edges_list2,
                   "taillediagramme1":taillediagramme1, "taillediagramme2":taillediagramme2,"ZipExpe1":ZipExpe1,"ZipExpe2":ZipExpe2}

        if formselect == "horizontal":
            return render(request, 'Cluster/horizontal.html', context)
        if formselect == "vertical":
            return render(request, 'Cluster/vertical.html', context)
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
        return redirect('Cluster:modele', mode, modele_id)
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

            return redirect('Cluster:modele', mode, modele_id)

        if 'Retour' in request.POST:
            return redirect('Cluster:modele', mode, modele_id)

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
        return render(request, 'Cluster/supprselectresult.html', context)
    else:
        return render(request, 'TableauEmb/Error/SupprImpossible.html')


def SupprResult(mode, result_id):
    DicInitModelDactuel, DicInitFormDactuel = ModelFormInit(mode)
    DicActuel = DicInitModelDactuel["resultat"].objects.get(id=result_id)
    DicInitModelDactuel["resultat"].objects.filter(id=result_id).delete()
    shutil.rmtree(settings.RESULT_SEMANTIC_DIR + "/Cluster/" + mode + "/save/" + str(DicActuel.nomresult))


############################################################
###############    FONCTIONS  JSON        ###############
###########################################################



def affichedendro(request, mode, path):

    path_split= path.split("---")

    if path_split[0]=="temp":
        folder  = settings.RESULT_SEMANTIC_DIR + "/Cluster/" + mode + "/temp/"
    elif path_split[0]=="save":
        folder  = settings.RESULT_SEMANTIC_DIR + "/Cluster/" + mode + "/save/" +path_split[1][:-4]
    else:
        response = HttpResponse()
        return response

    image_png = open(folder + "/" + path_split[1], "rb").read()
    response = HttpResponse(image_png, content_type='image/png')
    return response


def image(request, mode, nom):
    # charge une image pré-enregistrée avec save
    adresse = settings.RESULT_SEMANTIC_DIR + "/Cluster/" + mode + "/save/" + nom + "/" + nom + ".png"
    image_data = open(adresse,"rb").read()
    return HttpResponse(image_data, content_type="image/png")











