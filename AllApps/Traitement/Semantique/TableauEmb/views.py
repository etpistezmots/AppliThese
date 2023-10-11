
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from .core import  Model, Result
from .periph.prepaaffiche import  InitHome, InitHomeAfterFormInvalid, ModelFormInit, InitModelForResult, \
    AllModes, InitModelAfterFormInvalid, InitModelResultBeforeSave, InitResult, InitResultAllSelect
from .periph.amont import RecupDataCalcul, RecupDataSave, RecupUser, SumAndConcatlistAllSelect, PathModeleCreate,\
    PathResultCreate, TestModelExist, TestModelAccess, TestResultExist, TestResultAccess,\
    ExpandMode, PrepaMultiResults, DoMultiResult, SelectLastMode, TestResultCompare,  SelectResultFctUser
from .periph.aval import SupprModele, SupprResult

def homeredirect(request):
    '''
    Va définir le mode par default s'il n'y a pas de dernière expe
    sinon reprend sur le dernière expe enregistrée :
    Redirige vers le home de ce mode.
    L'utilisateur pourra ensuite changer s'il le souhaitegrâce à un select.
    '''

    mode_defaut = "glove"
    # selectionne le dernier mode en fonction dernière expé de l'utilisateur (sinon mode par défaut)
    mode = SelectLastMode(request, mode_defaut)
    return redirect('TableauEmb:home', mode)


def home(request, mode):
    '''
    Affiche l'interface pour calculer un modèle suivant les différents modes
    ou pour directement consulter tous les résultats obtenus
    voir init.html
    Attention, le bouton pour calculer un nouveau modèle ne s'affiche que pour les super-utilisateurs
    '''

    if request.method == 'POST':

        ################ CONSULT RESULT  #################
        if 'Consulter' in request.POST:
            return redirect("TableauEmb:resultallselect")

        ################ DO MODELE  #################
        if 'Calculer' in request.POST:

            # modèle et formulaire django à utiliser
            DicInitModelD, DicInitFormD = ModelFormInit(mode)
            # peuple le formulaire avec la requête
            formToSave = DicInitFormD["initial"](data=request.POST)
            if formToSave.is_valid():
                donnees = formToSave.cleaned_data
                # création du dossier de sauvegarde approprié
                PathModeleCreate(request,mode, donnees["nom"])
                # Recupération nom corpus et chemin des données
                NomCorpus = donnees["CorpusFinRef"].nom
                PathCorpus = settings.RESULT_PRETRAIT_DIR + "/FinaliseCorpus/CorpusFin/" + NomCorpus + ".csv"
                # Ajout des paramètres appropriés en fonction mode
                if mode == "word2vec":
                    Model.allmodele(mode, donnees["nom"], PathCorpus, donnees["revue"], donnees["epoque"],
                                    architecture=donnees["architecture"], embedding_size=donnees["embedding_size"],
                                    context_size=donnees["context_size"],
                                    min_occurrences=donnees["min_occurrences"],
                                    num_epochs=donnees["num_epochs"])
                elif mode == "glove":
                    Model.allmodele(mode, donnees["nom"], PathCorpus, donnees["revue"], donnees["epoque"],
                                    embedding_size=donnees["embedding_size"], context_size=donnees["context_size"],
                                    min_occurrences=donnees["min_occurrences"],
                                    num_epochs=donnees["num_epochs"])
                elif mode == "fasttext":
                    Model.allmodele(mode, donnees["nom"], PathCorpus, donnees["revue"], donnees["epoque"],
                                    architecture=donnees["architecture"], embedding_size=donnees["embedding_size"],
                                    context_size=donnees["context_size"],
                                    min_occurrences=donnees["min_occurrences"],
                                    num_epochs=donnees["num_epochs"], min_n=donnees["min_n"], max_n=donnees["max_n"])

                lv = formToSave.save()

                return redirect('TableauEmb:modele', mode, str(lv.id))

            # si le formulaire n'est pas valide
            else:
                modelscselect, allmodes = InitHomeAfterFormInvalid(request,mode)
                context = {"form": formToSave, "modelscalcul": modelscselect, "modeactuel": mode,
                           "allmodes": allmodes}
                return render(request, 'TableauEmb/init.html', context)


    ########################### Test et html initial ##########################
    allmodes = AllModes()
    if mode not in allmodes:
        return render(request, 'TableauEmb/Error/ModeNotExist.html')

    form, modelscselect = InitHome(request,mode)
    context = {"form": form, "modelscalcul": modelscselect, "modeactuel": mode, "allmodes": allmodes}
    return render(request, 'TableauEmb/init.html', context)


def modele(request, mode, modele_id):
    '''
    Affiche l'interface pour calculer un résultat
    Ne peut être sauvé ou supprimé que si l'utilisateur est connecté
    voir result.html pour la gestion des permissions
    '''

    if request.method == 'POST':

        ################ DO RESULT  #################
        if 'Calculer' in request.POST:

            # renvoie modèles et formulaires en fonction du mode
            DicInitModelD, DicInitFormD = ModelFormInit(mode)

            # pour valider le formulaire reduit qui permet affichage résultat si est valide
            test_form_result = DicInitFormD['resultatdeb'](data=request.POST)

            if test_form_result.is_valid():

                nom, revue, epoque, terme, nresult = RecupDataCalcul(DicInitModelD,modele_id,test_form_result)

                # CALCUL RESULTAT
                df = Result.allresult(mode, nom,revue,epoque,terme,nresult)

                form, modelscselect, allmodes, form2, results, table, AccesToSave, AccesToCalcul = \
                    InitModelResultBeforeSave(request, modele_id, DicInitModelD, DicInitFormD, test_form_result, df)


                context = {"form": form, "models": modelscselect, "modeactuel": mode, "allmodes": allmodes,
                           "idmodeleactuel": modele_id, "form2": form2,
                           "results": results,
                           "table": table, "AccesToSave": AccesToSave, "AccesToCalcul": AccesToCalcul}

                return render(request, 'TableauEmb/result.html', context)

            # formulaire invalide
            else:
                form, ModelscSelect, allmodes, resultselect, table, AccesToSave, AccesToCalcul \
                    = InitModelAfterFormInvalid(request, modele_id, DicInitModelD, DicInitFormD)
                context = {"form": form, "models": ModelscSelect, "modeactuel": mode, "allmodes": allmodes,
                           "idmodeleactuel": modele_id, "form2": test_form_result,
                           "results": resultselect, "table": table,
                           "AccesToSave": AccesToSave, "AccesToCalcul": AccesToCalcul}
                return render(request, 'TableauEmb/result.html', context)


        ################ SAVE RESULT  #################

        if 'Sauver' in request.POST:

            terme, nresult, name, table = RecupDataSave(request)

            # récup id de l'"user" ou "user_restrict2last" si superuser
            userencours = RecupUser(request)

            DicInitModelD, DicInitFormD = ModelFormInit(mode)
            formToSave = DicInitFormD["resultatfin"](
                data={"terme": terme, "nresult": nresult, "user_restrict2": userencours,
                      "nomresult":name,"modelc":DicInitModelD["initial"].objects.get(id=modele_id)})

            if formToSave.is_valid():
                lv = formToSave.save()
                pathresult = PathResultCreate(request,mode)
                with open(pathresult + "/" + str(lv.nomresult) + ".txt", "w") as f:
                    f.write(table)
                return redirect('TableauEmb:result', mode, modele_id, lv.id)

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
            return redirect("TableauEmb:resultallselect")

    ################### Tests et prepa html initial ######################

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
    form, allmodes, form2, resultselect, table, AccesToSave, AccesToCalcul = \
        InitModelForResult(request, Modelc, DicInitModelD, DicInitFormD)


    context = {"form": form, "models": ModelscSelect, "modeactuel": mode, "allmodes": allmodes,
               "idmodeleactuel": modele_id, "form2": form2,
               "results": resultselect, "table": table,
               "AccesToSave": AccesToSave, "AccesToCalcul": AccesToCalcul}
    return render(request, 'TableauEmb/result.html', context)


def result(request, mode, modele_id, result_id):
    '''Affiche l'interface d'un resultat'''

    if request.method == 'POST':

        ################  Suppr Model #################
        if 'SupprimerMultiModels' in request.POST:
            return redirect("TableauEmb:supprmultimodeles", mode)

        if 'SupprimerOneModel' in request.POST:
            return redirect("TableauEmb:suppronemodele", mode, modele_id)

        ################  Suppr Result #################
        if 'SupprimerMultiResults' in request.POST:
            return redirect("TableauEmb:supprmultiresults", mode, modele_id)

        if 'SupprimerOneResult' in request.POST:
            return redirect("TableauEmb:supproneresult", mode, modele_id, result_id)

        ############### Consult all result #####################
        if 'Consulter' in request.POST:
            return redirect("TableauEmb:resultallselect")

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

    form, modelscselect, allmodes, form2, results, table, AccesToSave, AccesToCalcul, ResultSpeUser = \
        InitResult(request, mode, modele_id, result_id)
    context = {"form": form, "models": modelscselect, "modeactuel": mode, "allmodes": allmodes,
               "idmodeleactuel": modele_id, "form2": form2,
               "results": results, "idresultactuel": result_id,
               "table": table, "AccesToSave": AccesToSave, "AccesToCalcul": AccesToCalcul,
               "ResultSpeUser": ResultSpeUser}


    return render(request, 'TableauEmb/result.html', context)



def resultallselect(request):
    ''' permet d'afficher tous les résultats
    si plus d'un resultat cochés, appelle fonction suivante : resultallvisu'''

    if request.method == 'POST':

        ConcatListExpeStock, tot = SumAndConcatlistAllSelect(request)

        if tot != 0:
            ConcatListExpeStock = ConcatListExpeStock[:-1]


        if 'Visualise' in request.POST or 'VisualiseColorQuanti' in request.POST:

            if tot == 0:
                ZipModeResult = InitResultAllSelect(request, ModelFormInit)
                messages.warning(request, "Vous devez au moins selectionner une expe," + "\n" +
                                 " et pour ce module multiexpe :" + "\n" +
                                 "au moins deux, c'est encore mieux...")
                context = {'ZipModeResult': ZipModeResult}
                return render(request, 'TableauEmb/resultallselect.html', context)

            elif tot == 1:

                error, modeselect = ExpandMode(ConcatListExpeStock[0])

                if not error:
                    DicInitModelDselect, DicInitFormDselect = ModelFormInit(modeselect)
                    idexpeselect = ConcatListExpeStock[1:]
                    expeselect = DicInitModelDselect["resultat"].objects.filter(id=int(idexpeselect))[0]
                    modeleselect = expeselect.modelc.id
                    return redirect('TableauEmb:result', modeselect, modeleselect, idexpeselect)
                else:
                    return render(request, 'TableauEmb/Error/ModeNotExist.html')

            else:

                ConcatListExpesVisibles, paradefaut, revuedefaut, ndefaut = PrepaMultiResults(tot,ConcatListExpeStock)

                ### Option couleur ou pas
                if 'Visualise' in request.POST:
                    return redirect('TableauEmb:resultallvisu', ConcatListExpesVisibles, ConcatListExpeStock, paradefaut, revuedefaut, ndefaut)

                if 'VisualiseColorQuanti' in request.POST:
                    return redirect('TableauEmb:resultallvisucolor', ConcatListExpesVisibles, ConcatListExpeStock, paradefaut, revuedefaut, ndefaut)


    ########### Prepa Html base ##################
    ZipModeResult = InitResultAllSelect(request,ModelFormInit)
    context = {'ZipModeResult': ZipModeResult}
    return render(request, 'TableauEmb/resultallselect.html', context)



def resultallvisu(request, listexpesvisibles, listexpesstock, paraselect, revueselect, nselect):
    if request.method == 'POST':
        if 'ColorQuanti' in request.POST:
            return redirect('TableauEmb:resultallvisucolor', listexpesvisibles, listexpesstock, paraselect, revueselect, nselect)

    errorG = TestResultCompare(request, listexpesvisibles, listexpesstock, paraselect, revueselect)
    if not errorG:
        MegaZipExpeVisibles, ListExpesStock, MiniZip, revueschoices, parachoices, nchoices, DivisEcran, tot, CompteurDiezeDiv \
            = DoMultiResult(listexpesvisibles,listexpesstock,paraselect,revueselect,nselect)

        context = {"MegaZipExpeVisibles":MegaZipExpeVisibles, "ListExpesStock": ListExpesStock,
                   "listexpesvisibles":listexpesvisibles,"listexpesstock":listexpesstock,
                   "MiniZip":MiniZip, "nselect": nselect,"revueselect": revueselect, "revueschoices": revueschoices,
                   "paraselect": paraselect, "parachoices": parachoices, "nchoices": nchoices,"DivisEcran":DivisEcran,
                   "tot":tot,"strtot":str(tot),"CompteurDiezeDiv":CompteurDiezeDiv}

        return render(request, 'TableauEmb/resultallvisu.html', context)

    else:
        return render(request, 'TableauEmb/Error/CompareError.html')


def resultallvisucolor(request, listexpesvisibles, listexpesstock, paraselect, revueselect, nselect):
    if request.method == 'POST':
        if 'ModeSimple' in request.POST:
            return redirect('TableauEmb:resultallvisu', listexpesvisibles, listexpesstock, paraselect, revueselect, nselect)

    errorG = TestResultCompare(request, listexpesvisibles, listexpesstock, paraselect, revueselect)

    if not errorG:
        MegaZipExpeVisibles, ListExpesStock, MiniZip, revueschoices, parachoices, nchoices, DivisEcran, tot, \
        CompteurDiezeDiv, tableresultquanti = DoMultiResult(listexpesvisibles,listexpesstock,paraselect,revueselect,nselect, color=True)


        context = {"MegaZipExpeVisibles": MegaZipExpeVisibles, "ListExpesStock": ListExpesStock,
                   "listexpesvisibles": listexpesvisibles, "listexpesstock": listexpesstock,
                   "MiniZip": MiniZip, "nselect": nselect, "revueselect": revueselect, "revueschoices": revueschoices,
                   "paraselect": paraselect, "parachoices": parachoices, "nchoices": nchoices, "DivisEcran": DivisEcran,
                   "tot": tot, "strtot": str(tot), "tableresultquanti":tableresultquanti, "CompteurDiezeDiv":CompteurDiezeDiv}

        return render(request, 'TableauEmb/resultallvisucolor.html', context)
    else:
        return render(request, 'TableauEmb/Error/CompareError.html')


def supprmultimodeles(request, mode):
    if request.method == 'POST':
        if 'Supprimer' in request.POST:
            ListModelesASuppr = request.POST.getlist('selected_modele')
            if request.user.is_superuser:
                for modeleasuppr in ListModelesASuppr:
                    SupprModele(mode, modeleasuppr)
                return redirect('TableauEmb:home', mode)
            else:
                return render(request, 'TableauEmb/Error/SupprImpossible.html')

        if 'Retour' in request.POST:
            return redirect('TableauEmb:home', mode)

    ###### test et prepa html ##############
    # test mode existe
    allmodes = AllModes()
    if mode not in allmodes:
        return render(request, 'TableauEmb/Error/ModeNotExist.html')

    # réservé au super-utilisateur
    if not request.user.is_superuser:
        return render(request, 'TableauEmb/Error/SupprImpossible.html')

    DicInitModelDactuel, DicInitFormDactuel = ModelFormInit(mode)
    modeles = DicInitModelDactuel["initial"].objects.all()
    context = {'modeactuel': mode, 'modeles': modeles}
    return render(request, 'TableauEmb/supprselectmodele.html', context)


def suppronemodele(request, mode, modele_id):

    # test mode existe
    allmodes = AllModes()
    if mode not in allmodes:
        return render(request, 'TableauEmb/Error/ModeNotExist.html')

    if request.user.id is None:
        return render(request, 'TableauEmb/Error/SupprImpossible.html')

    # test modele existe
    Exist, DicInitModelD, DicInitFormD, Modelc = TestModelExist(mode, modele_id,ModelFormInit)
    if not Exist:
        return render(request, 'TableauEmb/Error/ModeleNotExist.html')

    # test modele access
    Access, ModelscSelect = TestModelAccess(request, DicInitModelD, Modelc)
    if not Access:
        return render(request, 'TableauEmb/Error/ModeleNoAccess.html')

    # réservé au super-utilisateur ou au utilisateur ayant droit
    usermodel = Modelc.user_restrict
    if request.user.is_superuser or (str(request.user.id) in usermodel.split(",")):
        SupprModele(mode, modele_id)
    return redirect('TableauEmb:home', mode)


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

            return redirect('TableauEmb:modele', mode, modele_id)

        if 'Retour' in request.POST:
            return redirect('TableauEmb:modele', mode, modele_id)

    ###### test et prepa html ##############
    # test mode existe
    allmodes = AllModes()
    if mode not in allmodes:
        return render(request, 'TableauEmb/Error/ModeNotExist.html')

    if request.user.id is None:
        return render(request, 'TableauEmb/Error/SupprImpossible.html')

    # test modele existe
    Exist, DicInitModelD, DicInitFormD, Modelc = TestModelExist(mode, modele_id,ModelFormInit)
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
        resultats = SelectResultFctUser(request,ResultatsAll)
        context = {'modeactuel': mode, 'resultats': resultats}
        return render(request, 'TableauEmb/supprselectresult.html', context)
    else:
        return render(request, 'TableauEmb/Error/SupprImpossible.html')


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
        return redirect('TableauEmb:modele', mode, modele_id)
    else:
        return render(request, 'TableauEmb/Error/SupprImpossible.html')




