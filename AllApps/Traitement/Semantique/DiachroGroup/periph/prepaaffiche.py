
from AllApps.Traitement.Semantique.TableauEmb.periph.amont import SelectModelFctUser, SelectResultFctUser, AllModes,\
    CreateDictFromExpe, DiffDic
from .amont import ModelFormInit


def ParaModelAndResultInitial():
    DicInitParaResult = {"terme": "espace",
                             "nresult": "30",
                             "user_restrict2": "0",
                             "methode_clustering":"saut maximal",
                             "ncluster":"4",
                             "selectLink":"Tous sans selection",
                             "compareJustNewRevue": True,
                             "stop_mots": "",
                             "calculPoidsLabel": "Simi cos par rapport terme initial",
                             "taillecluster":"Nombre termes constitutifs cluster",
                             "couleursRevues": "Annales:blue,Espace:red",
                             }
    return DicInitParaResult


def InitModelForResult(request, Modelc, DicInitModelD, DicInitFormD):

    DicInitParaResult = ParaModelAndResultInitial()

    lastresult = DicInitModelD["resultat"].objects.filter(modelc_id=Modelc.id).last()
    if lastresult:
        form2 = DicInitFormD["resultatdeb"](instance=lastresult)
    else:
        form2 = DicInitFormD["resultatdeb"](initial=DicInitParaResult)


    form = DicInitFormD["initial"](instance=Modelc)

    if request.user.is_authenticated:
        AccesToCalcul = True
        AccesToSave = False
    else:
        AccesToCalcul = False
        AccesToSave = False

    results = DicInitModelD["resultat"].objects.filter(modelc_id=Modelc.id)
    graph = "no"

    seuilselect = 0.3
    seuil100 = 30

    return form, form2, results, graph, AccesToSave, AccesToCalcul, seuilselect, seuil100


def InitModelResultBeforeSave(request, modeactuel, modele_id, test_form_result, path):

    DicInitModelD, DicInitFormD = ModelFormInit(modeactuel)

    modelsc = DicInitModelD["initial"].objects.all()
    modelscselect = SelectModelFctUser(request, modelsc)

    DicModelc = DicInitModelD["initial"].objects.get(id=modele_id)
    form = DicInitFormD["initial"](instance=DicModelc)

    # l'option user_restrict2 n'est utilisé que par les super_user
    # permet de restreindre l'affichage des résultats à des utilisateurs choisis !
    form2 = DicInitFormD["resultatdeb"](data=test_form_result.cleaned_data)

    if request.user.is_authenticated:
        AccesToCalcul = True
        AccesToSave = True
    else:
        AccesToCalcul = False
        AccesToSave = False
    graph = "yes"

    results = DicInitModelD["resultat"].objects.filter(modelc_id=modele_id)
    allmodes = AllModes()

    path_result_transfo = "temp---" + path.split("/")[-1]
    seuilselect = 0.3
    seuil100= 30
    return form, modelscselect, allmodes, form2, results, graph, AccesToSave, AccesToCalcul, seuilselect,\
           path_result_transfo, seuil100



def InitResult(request, Modelc, DicInitModelD, DicInitFormD, result_id):


    form = DicInitFormD["initial"](instance=Modelc)

    results = DicInitModelD["resultat"].objects.filter(modelc_id=Modelc.id)
    DicResultc = DicInitModelD["resultat"].objects.get(id=result_id)

    form2 = DicInitFormD["resultatdeb"](instance=DicResultc)

    # disabled all field form 2
    for fieldname in form2.fields:
        form2.fields[fieldname].disabled = True

    path_result_transfo = "save---" + DicResultc.nomresult

    AccesToCalcul = False
    AccesToSave = False
    graph = "yes"

    # Utile pour qu'un utlisateur qui sauve des résultats puisse aussi les supprimer lui même
    # la gestion de la permission se trouve dans result.html
    ResultSpeUser = False
    if DicResultc.user_restrict2.isdigit():
        if int(DicResultc.user_restrict2) == request.user.id:
            ResultSpeUser = True

    seuil100 = DicResultc.seuil100
    seuilselect = seuil100 / 100

    return form, form2, path_result_transfo, results, graph, AccesToSave, AccesToCalcul,\
           ResultSpeUser, seuilselect


