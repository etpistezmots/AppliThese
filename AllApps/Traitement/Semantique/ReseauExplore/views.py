from django.shortcuts import render, redirect
from django.conf import settings
from django.http import JsonResponse
from django.contrib import messages
from .core.Result import allresult
from AllApps.Traitement.Semantique.TableauEmb.periph.amont import  SelectLastMode, RecupUser, AllModes, TestModelAccess, \
    TestResultAccess, TestResultExist, SumAndConcatlistAllSelect, ExpandMode, SelectResultFctUser, TestModelExist
from AllApps.Traitement.Semantique.TableauEmb.periph.prepaaffiche import InitResultAllSelect
from .periph.prepaaffiche import  InitModelForResult, InitModelBeforeResultSave, InitResult, InitHome
from .periph.amont import RecupDataCalcul, RecupDataSave, PathResultCreate, ModelFormInit,\
    PrepaTwoResults, DoTwoResults, TestResultCompare, EcritureResult
import json, shutil



def homeredirect(request):
    mode_defaut = "glove"
    # selectionne le dernier mode en fonction dernière expé de l'utilisateur (sinon mode par défaut)
    mode = SelectLastMode(request, mode_defaut)
    return redirect('ReseauExplore:home', mode)


def home(request, mode):

    if request.method == 'POST':
        ################ Voir All Expe #################
        if 'Consulter' in request.POST:
            return redirect("ReseauExplore:resultallselect")

    ########################### Test et html initial ##########################
    allmodes = AllModes()
    if mode not in allmodes:
        return render(request, 'TableauEmb/Error/ModeNotExist.html')

    # selectionne le dernier modèle de l'utilisateur en fonction mode (sinon None)
    lastmodel = InitHome(request, mode, ModelFormInit)
    if lastmodel:
        return redirect("ReseauExplore:modele", mode, lastmodel.id)
    else:
        context = {"modeactuel": mode, "allmodes": allmodes}
        return render(request, 'ReseauExplore/NoModel.html', context)


def modele(request, mode, modele_id):

    if request.method == 'POST':

        ################ DO RESULT  #################
        if ('CalculerGraphNonOrienté' in request.POST) or ('CalculerGraphOrienté' in request.POST):

            # renvoie modèles et formulaires en fonction du mode
            DicInitModelD, DicInitFormD = ModelFormInit(mode)

            # pour valider le formulaire reduit qui permet affichage résultat si est valide
            test_form_result = DicInitFormD['resultatsimple'](data=request.POST)

            if test_form_result.is_valid():

                nom, revue, epoque, terme, nresult, user = RecupDataCalcul(DicInitModelD,modele_id,test_form_result)
                # charge le modèle
                error, ResultTerme = allresult(mode, nom, revue, epoque, terme, nresult)

                if not error :
                    graph = "yes"
                    IndexNode = 0
                    IndexEdge = 0
                    nodes_list = [{'id': 1, 'label': terme}]
                    edges_list = []
                    for i, elt in enumerate(ResultTerme):
                        # car le 1 est le mot graine
                        diconode = {'id': i + 2, 'label': elt}
                        dicoedge = {'id': i + 1, 'from': 1, 'to': i + 2}
                        nodes_list.append(diconode)
                        edges_list.append(dicoedge)

                    IndexNode = IndexNode + nresult + 1
                    IndexEdge = IndexEdge + nresult + 1
                    dejaouvert = terme
                    dejaouvertindex = "1"
                    allactions = "1" + terme

                    form, modelscselect, allmodes, form2, results, AccesToSave, AccesToCalcul, oriented = \
                        InitModelBeforeResultSave(request, mode, modele_id, terme, nresult, revue, epoque, user)

                    context = {"graph": graph, "form": form, "models": modelscselect, "modeactuel": mode, "allmodes": allmodes,
                               "idmodeleactuel": modele_id, "form2": form2, "revuechoixlast":revue, "epoquechoixlast":epoque,
                               "results": results, "IndexNode": IndexNode, "IndexEdge": IndexEdge,
                               "dejaouvert": dejaouvert, "dejaouvertindex": dejaouvertindex, "allactions": allactions,
                               "nodes_list": nodes_list, "edges_list": edges_list,
                               "AccesToSave": AccesToSave, "AccesToCalcul": AccesToCalcul, "oriented":oriented}


                    return render(request, 'ReseauExplore/result.html', context)

                else:
                    return render(request, 'ReseauExplore/Error/TermeNotFound.html')

            else:
                context = {"form":test_form_result}
                return render(request, 'TableauEmb/Error/FormInvalid.html',context)


        ################ SAVE RESULT  #################

        if 'Sauver' in request.POST:

            terme, nresult, revue, epoque, name, indexnode, indexedge, dejaouvert, dejaouvertindex, \
            allactions, testnoderecup, testedgerecup, oriented = RecupDataSave(request)

            # récup id de l'"user" ou "user_restrict2last" si superuser
            userencours = RecupUser(request)

            DicInitModelD, DicInitFormD = ModelFormInit(mode)
            DicModelc = DicInitModelD["initial"].objects.get(id=modele_id)
            formToSave = DicInitFormD["resultatfin"](data={"terme": terme, "nresult": nresult, "user_restrict2": userencours,
                                                           "choixrevue":revue,"choixepoque":epoque,"comment":"save",
                                                           "indexnode":indexnode,
                                                           "indexedge":indexedge,"nomresult":name,
                                                           "modelc":DicModelc,"oriented":oriented})

            if formToSave.is_valid():
                lv = formToSave.save()
                pathresult = PathResultCreate(request, mode, str(lv.nomresult))
                EcritureResult(pathresult, dejaouvert, dejaouvertindex, allactions, testnoderecup, testedgerecup)

                return redirect('ReseauExplore:result', mode, str(modele_id), str(lv.id), oriented)
            else:
                context = {"form":formToSave}
                return render(request, 'TableauEmb/Error/FormInvalid.html',context)


        ################  Suppr Model #################
        if 'SupprimerMultiModels' in request.POST:
            return redirect("TableauEmb:supprmultimodeles", mode)

        if 'SupprimerOneModel' in request.POST:
            return redirect("TableauEmb:suppronemodele", mode, modele_id)

        ############### Consult all result #####################
        if 'Consulter' in request.POST:
            return redirect("ReseauExplore:resultallselect")


    ########################### Test et html initial ##########################

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
    form, form2, results, graph, IndexNode, IndexEdge, nodes_list, edges_list, \
    AccesToSave, AccesToCalcul, oriented = InitModelForResult(request, Modelc, DicInitModelD, DicInitFormD)

    context = {"form": form, "models": ModelscSelect , "modeactuel":mode, "allmodes":allmodes,
               "idmodeleactuel": modele_id, "form2": form2,
               "results": results, "graph":graph,  "IndexNode": IndexNode, "IndexEdge": IndexEdge,
               "nodes_list": nodes_list, "edges_list": edges_list,
               "AccesToSave": AccesToSave, "AccesToCalcul": AccesToCalcul, "oriented":oriented}

    return render(request, 'ReseauExplore/result.html', context)




def result(request, mode, modele_id, result_id, orient):

    if request.method == 'POST':

        ################  Suppr Result #################
        if 'SupprimerMultiResults' in request.POST:
            return redirect("ReseauExplore:supprmultiresults", mode, modele_id)

        if 'SupprimerOneResult' in request.POST:
            return redirect("ReseauExplore:supproneresult", mode, modele_id, result_id)

        ############### Consult all result #####################
        if 'Consulter' in request.POST:
            return redirect("ReseauExplore:resultallselect")

    ######################### Tests et prepa html initial  ##########################################

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


    form, form2, results, graph, indexnode, indexedge, dejaouvert, dejaouvertindex, \
    allactions, nodes_list, edges_list, AccesToSave, AccesToCalcul, ResultSpeUser \
        = InitResult(request, mode, Modelc, DicInitModelD, DicInitFormD, result_id)

    context = {"form": form, "models": ModelscSelect, "modeactuel": mode, "allmodes": allmodes,
               "idmodeleactuel": modele_id, "form2": form2,
               "results": results, "idresultactuel": result_id, "graph": graph, "IndexNode": indexnode, "IndexEdge": indexedge,
               "dejaouvert":dejaouvert, "dejaouvertindex":dejaouvertindex, "allactions":allactions,
               "nodes_list": nodes_list  , "edges_list": edges_list,
               "AccesToSave": AccesToSave, "AccesToCalcul": AccesToCalcul, "ResultSpeUser": ResultSpeUser, "oriented":orient}


    return render(request, 'ReseauExplore/result.html', context)


############################################################
###########    FONCTION SUPPR ET AFFICHE        ##############
#############################################################

def resultallselect(request):

    if request.method == 'POST':

        ConcatListExpeStock, tot = SumAndConcatlistAllSelect(request)

        if tot != 0:
            ConcatListExpeStock = ConcatListExpeStock[:-1]

        if tot == 0:

            ZipModeResult = InitResultAllSelect(request, ModelFormInit)
            messages.warning(request, "Vous devez au moins selectionner une expe," + "\n" +
                                      " et pour ce module multiexpe :" + "\n" +
                                      "au moins deux, c'est encore mieux...")
            context = {'ZipModeResult': ZipModeResult}
            return render(request, 'ReseauExplore/resultallselect.html', context)

        elif tot == 1:

            error, modeselect = ExpandMode(ConcatListExpeStock[0])

            if not error:
                DicInitModelDselect, DicInitFormDselect = ModelFormInit(modeselect)
                idexpeselect = ConcatListExpeStock[1:]
                expeselect = DicInitModelDselect["resultat"].objects.filter(id=int(idexpeselect))[0]
                modeleselect = expeselect.modelc.id
                orientselect = expeselect.oriented
                return redirect('ReseauExplore:result', modeselect, modeleselect, idexpeselect, orientselect)
            else:
                return render(request, 'TableauEmb/Error/ModeNotExist.html')

        else:
            ConcatListExpesVisibles, paradefault, formatdefault, tailledefault= PrepaTwoResults(ConcatListExpeStock)
            return redirect('ReseauExplore:resultallvisu', ConcatListExpesVisibles, ConcatListExpeStock, paradefault, formatdefault, tailledefault)

    ########### Prepa Html base ##################
    ZipModeResult = InitResultAllSelect(request,ModelFormInit)
    context = {'ZipModeResult': ZipModeResult}
    return render(request, 'ReseauExplore/resultallselect.html', context)


def resultallvisu(request, listexpesvisibles, listexpesstock, paraselect, formselect, tailleselect):

    errorG = TestResultCompare(request, listexpesvisibles, listexpesstock, paraselect, formselect, tailleselect)
    if not errorG:

        expe1R, expe2R, expesR, dejaouvert1, dejaouvertindex1, allactions1, nodes_list1, edges_list1, \
        dejaouvert2, dejaouvertindex2, allactions2, nodes_list2, edges_list2, dict1, dict2, ZipExpe1, ZipExpe2,\
        parachoices, formchoices, taillechoices = DoTwoResults(listexpesvisibles,listexpesstock,paraselect)

        context = {"listexpesvisibles":listexpesvisibles, "listexpesstock":listexpesstock,
                   "expe1R":expe1R, "expe2R":expe2R, "expesR": expesR, "dejaouvert":dejaouvert1,
                   "dejaouvertindex":dejaouvertindex1, "allactions":allactions1, "nodes_list":nodes_list1,
                   "edges_list":edges_list1, "dejaouvert2":dejaouvert2,"ZipExpe1":ZipExpe1,"ZipExpe2":ZipExpe2,
                   "dejaouvertindex2":dejaouvertindex2, "allactions2":allactions2, "nodes_list2":nodes_list2,
                   "edges_list2":edges_list2,"dict1":dict1, "dict2":dict2, "paraselect":paraselect, "parachoices":parachoices,
                   "formselect": formselect, "formchoices": formchoices, "tailleselect": tailleselect, "taillechoices": taillechoices}

        if formselect == "horizontal":
            return render(request, 'ReseauExplore/horizontal.html', context)
        if formselect == "vertical":
            return render(request, 'ReseauExplore/vertical.html', context)

    else:
        return render(request, 'TableauEmb/Error/CompareError.html')


def supproneresult(request, mode, modele_id, result_id):

    # test mode existe
    allmodes = AllModes()
    if mode not in allmodes:
        return render(request, 'TableauEmb/Error/ModeNotExist.html')

    if request.user.id is None:
        return render(request, 'TableauEmb/Error/SupprImpossible.html')

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

    # réservé au super-utilisateur ou au utilisateur ayant droit
    userexpe = Resultc.user_restrict2
    if request.user.is_superuser or (str(request.user.id) in userexpe.split(",")):
        SupprResult(mode, result_id)
        return redirect('ReseauExplore:modele', mode, modele_id)
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

            return redirect('ReseauExplore:modele', mode, modele_id)

        if 'Retour' in request.POST:
            return redirect('ReseauExplore:modele', mode, modele_id)

     ###### test et prepa html ##############
    # test mode existe
    allmodes = AllModes()
    if mode not in allmodes:
        return render(request, 'TableauEmb/Error/ModeNotExist.html')

    if request.user.id is None:
        return render(request, 'TableauEmb/Error/SupprImpossible.html')

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
        return render(request, 'ReseauExplore/supprselectresult.html', context)
    else:
        return render(request, 'TableauEmb/Error/SupprImpossible.html')

def SupprResult(mode, result_id):
    DicInitModelDactuel, DicInitFormDactuel = ModelFormInit(mode)
    DicActuel = DicInitModelDactuel["resultat"].objects.get(id=result_id)
    DicInitModelDactuel["resultat"].objects.filter(id=result_id).delete()
    shutil.rmtree(settings.RESULT_SEMANTIC_DIR + "/ReseauExplore/" + mode + "/result/" + str(DicActuel.nomresult))

###########################################################
###########    DYNAMIQUE GRAPH (JQUERY)        ##############
#############################################################


def AjaxGraphNonOriente(request):

    if request.method == 'POST':

        # recupération de toutes les variables
        modeencours = request.POST.get('modeencours', None)
        nomencours = request.POST.get('nomencours', None)
        revueencours = request.POST.get("choixrevueencours", None)
        epoqueencours = request.POST.get("choixepoqueencours", None)
        modele = request.POST.get('modele', None)
        nodeId = request.POST.get('nodeId', None)
        nodelabel = request.POST.get('nodelabel', None)
        NbreTermes = request.POST.get('numberopen', None)
        dejaouvert = request.POST.get('dejaouvert', None)
        dejaouvertindex = request.POST.get('dejaouvertindex', None)
        allactions = request.POST.get('allactions', None)
        recupindexnode = int(request.POST.get('indexnode', None))
        recupindexedge = int(request.POST.get('indexedge', None))

        # complète dejaouvert et allactions en fontion fermeture ou ouverture
        marqueurafermer = False
        dejaouverlist = dejaouvert.split(",")
        if nodelabel in dejaouverlist:
            marqueurafermer = True
            dejaouverlist.remove(nodelabel)
            dejaouvertindexlist = dejaouvertindex.split(",")
            dejaouvertindexlist.remove(nodeId)
            dejaouvertindex = ",".join(dejaouvertindexlist)
            dejaouvert = ",".join(dejaouverlist)
            allactions = allactions + ",0" + nodelabel
        else:
            if len(dejaouvertindex) == 0:
                dejaouvert = nodelabel
                dejaouvertindex = nodeId
                allactions = nodelabel
            else:
                dejaouvert = dejaouvert + "," + nodelabel
                dejaouvertindex = dejaouvertindex + "," + nodeId
                allactions = allactions + ",1" + nodelabel

        # récupération des nodes et edges du graph a partir json data
        allnodes = json.loads(request.POST.get('testdata', None))['nodes']['_data']
        recuptermes = [allnodes[elt]['label']for elt in allnodes]
        recupid = [allnodes[elt]['id'] for elt in allnodes]

        alledges = json.loads(request.POST.get('testdata', None))['edges']['_data']
        edgeid = [alledges[elt]['id'] for elt in alledges]
        edgedep = [alledges[elt]['from'] for elt in alledges]
        edgefin = [alledges[elt]['to'] for elt in alledges]

        edges_list_deja_present = []
        for i,elt in enumerate(edgeid):
            dicoedge = {'id': elt, 'from': edgedep[i], 'to': edgefin[i]}
            edges_list_deja_present.append(dicoedge)

        # charge modele et récupère les termes
        error, ResultGloveTermeNew = allresult(modeencours, nomencours, revueencours, epoqueencours, nodelabel, int(NbreTermes))

        if not error :

            # variable pour stocker les nodes et edges à ajouter ou supprimer
            nodes_list = []
            edges_list = []

            # procédure en cas fermeture !
            if marqueurafermer:
                for elt in ResultGloveTermeNew:
                    # Attention, peut avoir été fermé par l'utilisateur
                    if elt in recuptermes:
                        nodeasupprimer = True
                        # trouver  id --> regarder s'il est impliqué
                        # dans un départ ou une arrivée d'un autre edge !
                        indexinrecuptermes = recuptermes.index(elt)
                        indexcorrespondant = recupid[indexinrecuptermes]

                        # si c'est un noeud déjà ouvert, on ne le supprime pas
                        # prends en compte le cas où plus de noeud ouvert car faisait bugger sinon la deuxième expression
                        if len(dejaouvertindex) != 0 and indexcorrespondant in list(map(int, dejaouvertindex.split(","))):
                            nodeasupprimer = False
                        else:
                            # on va regarder dans les deux sens :
                            # si le noeud est impliqué dans une autre relation
                            # on ne le supprime pas
                            indicesfinother = [i for i, x in enumerate(edgefin) if
                                               x == indexcorrespondant and edgedep[i] != int(nodeId)]
                            if len(indicesfinother) > 0:
                                indicefinsame = [i for i, x in enumerate(edgefin) if
                                                 x == indexcorrespondant and edgedep[i] == int(nodeId)]
                                if len(indicefinsame) > 0:
                                    edges_list.append(edgeid[indicefinsame[0]])
                                    nodeasupprimer = False


                            indicesdepother = [i for i, x in enumerate(edgedep) if
                                               x == indexcorrespondant and edgefin[i] != int(nodeId)]
                            if len(indicesdepother) > 0:
                                indicedepsame = [i for i, x in enumerate(edgedep) if
                                                 x == indexcorrespondant and edgefin[i] == int(nodeId)]
                                if len(indicedepsame) > 0:
                                    edges_list.append(edgeid[indicedepsame[0]])
                                    nodeasupprimer = False

                        if nodeasupprimer:
                            nodes_list.append({'id': indexcorrespondant, 'label': elt})

                    NewIndexNode = int(recupindexnode)
                    NewIndexEdge = int(recupindexedge)


            # procédure en cas ouverture !
            else :

                for i,elt in enumerate(ResultGloveTermeNew):

                    if elt in recuptermes:

                        indexinrecuptermes = recuptermes.index(elt)
                        indexcorrespondant = recupid[indexinrecuptermes]
                        # va falloir checker si n'existe pas déjà comme lien dans les deux sens !
                        EdgeExist = False

                        indicesfin = [i for i, x in enumerate(edgefin) if x == indexcorrespondant]
                        for indice in indicesfin:
                            if edgedep[indice] == int(nodeId):
                                EdgeExist = True

                        indicesdep = [i for i, x in enumerate(edgedep) if x == indexcorrespondant]
                        for indice in indicesdep:
                            if edgefin[indice] == int(nodeId):
                                EdgeExist = True

                        if not EdgeExist:
                            dicoedge = {'id': recupindexedge + i + 1, 'from': int(nodeId), 'to': indexcorrespondant}
                            edges_list.append(dicoedge)

                    else:
                        diconode = {'id': recupindexnode + i + 1, 'label': elt}
                        dicoedge = {'id': recupindexedge + i + 1, 'from': int(nodeId), 'to': recupindexnode + i + 1}
                        nodes_list.append(diconode)
                        edges_list.append(dicoedge)

                NewIndexNode = int(recupindexnode) + int(NbreTermes)
                NewIndexEdge = int(recupindexedge) + int(NbreTermes)

            #print(marqueurafermer)
            #print(nodes_list)
            #print(edges_list)

            mytest= {"nodes_test":nodes_list,"edges_test":edges_list,'indexnode': str(NewIndexNode), 'indexedge': str(NewIndexEdge),
                     "dejaouvert":dejaouvert, "dejaouvertindex":dejaouvertindex, "marqueurafermer":marqueurafermer, "allactions":allactions}
            return JsonResponse(mytest)

        else:
            return render(request, 'ReseauExplore/Error/TermeNotFound.html')


def AjaxGraphOriente(request):

    if request.method == 'POST':

        # recupération de toutes les variables
        modeencours = request.POST.get('modeencours', None)
        nomencours = request.POST.get('nomencours', None)
        revueencours = request.POST.get("choixrevueencours", None)
        epoqueencours = request.POST.get("choixepoqueencours", None)
        modele = request.POST.get('modele', None)
        nodeId = request.POST.get('nodeId', None)
        nodelabel = request.POST.get('nodelabel', None)
        NbreTermes = request.POST.get('numberopen', None)
        dejaouvert = request.POST.get('dejaouvert', None)
        dejaouvertindex = request.POST.get('dejaouvertindex', None)
        allactions = request.POST.get('allactions', None)
        recupindexnode = int(request.POST.get('indexnode', None))
        recupindexedge = int(request.POST.get('indexedge', None))

        # complète dejaouvert et allactions en fontion fermeture ou ouverture
        marqueurafermer = False
        dejaouverlist = dejaouvert.split(",")
        if nodelabel in dejaouverlist:
            marqueurafermer = True
            dejaouverlist.remove(nodelabel)
            dejaouvertindexlist = dejaouvertindex.split(",")
            dejaouvertindexlist.remove(nodeId)
            dejaouvertindex = ",".join(dejaouvertindexlist)
            dejaouvert = ",".join(dejaouverlist)
            allactions = allactions + ",0" + nodelabel
        else:
            if len(dejaouvertindex) == 0:
                dejaouvert = nodelabel
                dejaouvertindex = nodeId
                allactions = nodelabel
            else:
                dejaouvert = dejaouvert + "," + nodelabel
                dejaouvertindex = dejaouvertindex + "," + nodeId
                allactions = allactions + ",1" + nodelabel

        # récupération des nodes et edges du graph a partir json data
        allnodes = json.loads(request.POST.get('testdata', None))['nodes']['_data']
        recuptermes = [allnodes[elt]['label'] for elt in allnodes]
        recupid = [allnodes[elt]['id'] for elt in allnodes]

        alledges = json.loads(request.POST.get('testdata', None))['edges']['_data']
        edgeid = [alledges[elt]['id'] for elt in alledges]
        edgedep = [alledges[elt]['from'] for elt in alledges]
        edgefin = [alledges[elt]['to'] for elt in alledges]

        edges_list_deja_present = []
        for i, elt in enumerate(edgeid):
            dicoedge = {'id': elt, 'from': edgedep[i], 'to': edgefin[i]}
            edges_list_deja_present.append(dicoedge)

        # charge modele et récupère les terme
        error, ResultGloveTermeNew = allresult(modeencours, nomencours, revueencours, epoqueencours, nodelabel,
                                        int(NbreTermes))

        if not error:

            # variable pour stocker les nodes et edges à ajouter ou supprimer
            nodes_list = []
            edges_list = []

            # procédure en cas fermeture !
            if marqueurafermer:
                for elt in ResultGloveTermeNew:

                    nodeasupprimer = True
                    # trouver  id --> regarder s'il est impliqué
                    # dans un départ ou une arrivée d'un autre edge !
                    indexinrecuptermes = recuptermes.index(elt)
                    indexcorrespondant = recupid[indexinrecuptermes]

                    # supprime les edges qui parte de ce noeud
                    indicefintoremove = [i for i, x in enumerate(edgefin) if
                                     x == indexcorrespondant and edgedep[i] == int(nodeId)]
                    edges_list.append(edgeid[indicefintoremove[0]])


                    # si le noeud d'arrivée est pris dans une autre relation d'arrivée,
                    # alors on ne supprime pas le noeud
                    indicesfinother = [i for i, x in enumerate(edgefin) if
                                       x == indexcorrespondant and edgedep[i] != int(nodeId)]
                    if len(indicesfinother) > 0:
                        nodeasupprimer = False

                    # si le noeud d'arrivée est pris dans une relation de départ,
                    # alors on ne supprime pas le noeud
                    indicesdepother = [i for i, x in enumerate(edgedep) if x == indexcorrespondant]
                    if len(indicesdepother) > 0:
                        nodeasupprimer = False


                    if nodeasupprimer:
                        nodes_list.append({'id': indexcorrespondant, 'label': elt})

                NewIndexNode = int(recupindexnode)
                NewIndexEdge = int(recupindexedge)


            # procédure en cas ouverture !
            else:

                for i, elt in enumerate(ResultGloveTermeNew):

                    if elt in recuptermes:

                        indexinrecuptermes = recuptermes.index(elt)
                        indexcorrespondant = recupid[indexinrecuptermes]

                        # va falloir checker si n'existe pas déjà comme lien
                        EdgeExist = False
                        indicesfin = [i for i, x in enumerate(edgefin) if x == indexcorrespondant]
                        for indice in indicesfin:
                            if edgedep[indice] == int(nodeId):
                                EdgeExist = True


                        if not EdgeExist:
                            dicoedge = {'id': recupindexedge + i + 1, 'from': int(nodeId), 'to': indexcorrespondant}
                            print(dicoedge)
                            edges_list.append(dicoedge)

                    else:
                        diconode = {'id': recupindexnode + i + 1, 'label': elt}
                        dicoedge = {'id': recupindexedge + i + 1, 'from': int(nodeId), 'to': recupindexnode + i + 1}
                        nodes_list.append(diconode)
                        edges_list.append(dicoedge)

                NewIndexNode = int(recupindexnode) + int(NbreTermes)
                NewIndexEdge = int(recupindexedge) + int(NbreTermes)

            # print(marqueurafermer)
            # print(nodes_list)
            # print(edges_list)

            mytest = {"nodes_test": nodes_list, "edges_test": edges_list, 'indexnode': str(NewIndexNode),
                      'indexedge': str(NewIndexEdge),
                      "dejaouvert": dejaouvert, "dejaouvertindex": dejaouvertindex, "marqueurafermer": marqueurafermer,
                      "allactions": allactions}
            return JsonResponse(mytest)

        else:
            return render(request, 'ReseauExplore/Error/TermeNotFound.html')









