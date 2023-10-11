from AllApps.Traitement.Semantique.TableauEmb.periph.amont import AllModes,\
    SelectModelFctUser, SelectResultFctUser
from .amont import ModelFormInit, LectureResult
from django.conf import settings



def InitHome(request,modeactuel, ModelFormGeneric):
    # modèle et formulaire à utiliser
    DicInitModelD, DicInitFormD = ModelFormGeneric(modeactuel)
    # récupère tous les modèles ordonné par inverse id
    modelsc = DicInitModelD["initial"].objects.all().order_by('-id')
    # selectionne le dernier modele de l'utilisateur en fonction mode
    modelscselect = SelectModelFctUser(request, modelsc)
    lastmodel = None
    if len(modelscselect) != 0:
        lastmodel = modelscselect[0]
    return lastmodel


def ParaInitialResult():
    DicInitParaResult = {"terme": "espace",
                        "nresult": 10,
                        "user_restrict2": "0"}
    return DicInitParaResult


def InitModelForResult(request, Modelc, DicInitModelD, DicInitFormD):
    DicInitParaResult = ParaInitialResult()

    results = DicInitModelD["resultat"].objects.filter(modelc_id=Modelc.id).all()
    resultselect = SelectResultFctUser(request, results)
    if len(resultselect)>0:
        lastresult = resultselect[-1]
        lastepoque = lastresult.choixepoque
        lastrevue = lastresult.choixrevue

    form = DicInitFormD["initial"](instance=Modelc)

    AccesToCalcul = True
    AccesToSave = False

    if len(resultselect)>0:
        form2 = DicInitFormD["resultatdeb"](instance=lastresult, epoques=Modelc.epoque, epoque1=lastepoque,
                                            revues=Modelc.revue, revue1=lastrevue)
    else:
        form2 = DicInitFormD["resultatdeb"](initial=DicInitParaResult, epoques=Modelc.epoque, revues=Modelc.revue)

    results = DicInitModelD["resultat"].objects.filter(modelc_id=Modelc.id)
    graph = "no"
    nodes_list = []
    edges_list = []
    IndexNode = 0
    IndexEdge = 0

    # par default
    oriented = "yes"

    return form, form2, results, graph, IndexNode, IndexEdge, nodes_list, edges_list,\
           AccesToSave, AccesToCalcul, oriented



def InitModelBeforeResultSave(request, mode, modele_id, terme, nresult, revue, epoque, user):
    DicInitModelD, DicInitFormD = ModelFormInit(mode)

    modelsc = DicInitModelD["initial"].objects.all()
    modelscselect = SelectModelFctUser(request, modelsc)

    DicModelc = DicInitModelD["initial"].objects.get(id=modele_id)
    form = DicInitFormD["initial"](instance=DicModelc)

    # l'option user_restrict2 n'est utilisé que par les super_user
    # permet de restreindre l'affichage des résultats à des utilisateurs choisis !
    form2 = DicInitFormD["resultatdeb"](initial={'terme': terme, "nresult": nresult, "user_restrict2": user},
                                        epoques=DicModelc.epoque, revues=DicModelc.revue, revue1=revue, epoque1=epoque)

    AccesToSave = True
    AccesToCalcul = True

    results = DicInitModelD["resultat"].objects.filter(modelc_id=modele_id)
    allmodes = AllModes()

    if 'CalculerGraphNonOrienté' in request.POST:
        oriented = "no"
    if 'CalculerGraphOrienté' in request.POST:
        oriented = "yes"

    return form, modelscselect, allmodes, form2, results, AccesToSave, AccesToCalcul, oriented



def InitResult(request, mode, Modelc, DicInitModelD, DicInitFormD, result_id):

    form = DicInitFormD["initial"](instance=Modelc)

    AllEpoquesModele = Modelc.epoque
    AllRevueModele = Modelc.revue

    results = DicInitModelD["resultat"].objects.filter(modelc_id=Modelc.id)
    DicResultc = DicInitModelD["resultat"].objects.get(id=result_id)

    epoqueencours = DicResultc.choixepoque
    revueencours = DicResultc.choixrevue

    form2 = DicInitFormD["resultatdeb"](instance=DicResultc, epoques=AllEpoquesModele, revues=AllRevueModele,
                                     epoque1=epoqueencours, revue1=revueencours)

    # disabled all field form 2
    for fieldname in form2.fields:
        form2.fields[fieldname].disabled = True

    pathresult = settings.RESULT_SEMANTIC_DIR + "/ReseauExplore/" + mode + "/result/" + DicResultc.nomresult
    indexnode = DicResultc.indexnode
    indexedge = DicResultc.indexedge
    dejaouvert, dejaouvertindex, allactions, nodes_list, edges_list = LectureResult(pathresult)

    AccesToCalcul = False
    AccesToSave = False
    graph = "yes"

    # Utile pour qu'un utlisateur qui sauve des résultats puisse aussi les supprimer lui même
    # la gestion de la permission se trouve dans result.html
    ResultSpeUser = False
    if DicResultc.user_restrict2.isdigit():
        if int(DicResultc.user_restrict2) == request.user.id:
            ResultSpeUser = True

    return form, form2, results, graph, indexnode, indexedge, dejaouvert, dejaouvertindex, \
           allactions,nodes_list,  edges_list, AccesToSave, AccesToCalcul, ResultSpeUser






