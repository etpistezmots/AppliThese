

from django.conf import settings
from .amont import AllModes, ModelFormInit, SelectModelFctUser, SelectResultFctUser
from django.urls import resolve
from .df2html import transform


def ParaInitialModele(mode):
    DicInitParaModele = {}
    if mode == "word2vec":
        DicInitParaModele = {"nom": "Achoisir",
                             "user_restrict": "0",
                             "revue": "Annales,Espace",
                             "epoque": "1950-1960,1961-1971,1972-1984,1985-1995",
                             "architecture": "cbow",
                             "embedding_size": 50,
                             "context_size": 10,
                             "min_occurrences": 15,
                             "num_epochs": 100}
    elif mode == "glove":
        DicInitParaModele = {"nom": "Achoisir",
                             "user_restrict": "0",
                             "revue": "Annales,Espace",
                             "epoque": "1950-1960,1961-1971,1972-1984,1985-1995",
                             "embedding_size": 50,
                             "context_size": 10,
                             "min_occurrences": 15,
                             "num_epochs": 100}
    elif mode == "fasttext":
        DicInitParaModele = {"nom": "Achoisir",
                             "user_restrict": "0",
                             "revue": "Annales,Espace",
                             "epoque": "1950-1960,1961-1971,1972-1984,1985-1995",
                             "architecture": "cbow",
                             "embedding_size": 50,
                             "context_size": 10,
                             "min_occurrences": 15,
                             "num_epochs": 100,
                             "min_n": 3,
                             "max_n": 6}
    return DicInitParaModele



def InitHome(request,mode):
    # dictionnaire paramètres affichage par défault
    DicInitParaModele = ParaInitialModele(mode)
    # modèle et formulaire django à utiliser
    DicInitModelD, DicInitFormD = ModelFormInit(mode)

    # affiche le dernier modèle calculé
    # ou paramètres affichage par default si n'existe pas
    lastmodelc = DicInitModelD["initial"].objects.last()

    if lastmodelc:
        form = DicInitFormD["initial"](instance=lastmodelc)
    else:
        form = DicInitFormD["initial"](initial=DicInitParaModele)

    # récupère tous les modèles
    modelsc = DicInitModelD["initial"].objects.all().order_by('-id')

    # selection du modèle en fonction de l'user !
    modelscselect = SelectModelFctUser(request, modelsc)

    return form, modelscselect


def InitHomeAfterFormInvalid(request,mode):
    DicInitModelD, DicInitFormD = ModelFormInit(mode)
    # inverse id : permet d'avoir le dernier créé en premier
    modelsc = DicInitModelD["initial"].objects.all().order_by('-id')
    modelscselect = SelectModelFctUser(request, modelsc)
    allmodes = AllModes()
    return modelscselect,allmodes



def ParaInitialResult():
    DicInitParaResult = {"terme": "espace",
                             "nresult": 15,
                             "user_restrict2": "0"}
    return DicInitParaResult



def InitModelForResult(request, Modelc, DicInitModelD, DicInitFormD):

    DicInitParaResult = ParaInitialResult()

    results = DicInitModelD["resultat"].objects.filter(modelc_id=Modelc.id).order_by('-id')
    resultselect = SelectResultFctUser(request, results)

    if len(resultselect) > 0:
        lastresult = resultselect[-1]
        form2 = DicInitFormD["resultatdeb"](instance=lastresult)
    else:
        form2 = DicInitFormD["resultatdeb"](initial=DicInitParaResult)

    form = DicInitFormD["initial"](instance=Modelc)

    AccesToCalcul = True
    AccesToSave = False

    table = ""
    allmodes = AllModes()

    return form, allmodes, form2, resultselect, table, AccesToSave, AccesToCalcul


def InitModelAfterFormInvalid(request, modele_id, DicInitModelD, DicInitFormD):

    results = DicInitModelD["resultat"].objects.filter(modelc_id=modele_id)
    resultselect = SelectResultFctUser(request, results)

    modelsc = DicInitModelD["initial"].objects.all()
    modelscselect = SelectModelFctUser(request, modelsc)

    DicModelc = DicInitModelD["initial"].objects.get(id=modele_id)
    form = DicInitFormD["initial"](instance=DicModelc)

    AccesToCalcul = True
    AccesToSave = False

    table = ""
    allmodes = AllModes()

    return form, modelscselect, allmodes,  resultselect, table, AccesToSave, AccesToCalcul



def InitModelResultBeforeSave(request, modele_id, DicInitModelD, DicInitFormD, test_form_result, df):


    modelsc = DicInitModelD["initial"].objects.all()
    modelscselect = SelectModelFctUser(request, modelsc)

    DicModelc = DicInitModelD["initial"].objects.get(id=modele_id)
    form = DicInitFormD["initial"](instance=DicModelc)

    # l'option user_restrict2 n'est utilisé que par les super_user
    # permet de restreindre l'affichage des résultats à des utilisateurs choisis !
    form2 = DicInitFormD["resultatdeb"](data=test_form_result.cleaned_data)

    AccesToSave = True
    AccesToCalcul = True
    table = transform(df)

    results = DicInitModelD["resultat"].objects.filter(modelc_id=modele_id)
    allmodes = AllModes()
    return form, modelscselect, allmodes, form2, results, table, AccesToSave, AccesToCalcul


def InitResult(request, mode, modele_id, result_id):
    DicInitModelD, DicInitFormD = ModelFormInit(mode)

    models = DicInitModelD["initial"].objects.all()
    modelscselect = SelectModelFctUser(request, models)
    DicModelc = DicInitModelD["initial"].objects.get(id=modele_id)
    form = DicInitFormD["initial"](instance=DicModelc)

    results = DicInitModelD["resultat"].objects.filter(modelc_id=modele_id)
    DicResultc = DicInitModelD["resultat"].objects.get(id=result_id)
    form2 = DicInitFormD["resultatdeb"](instance=DicResultc)

    # disabled all field form 2
    for fieldname in form2.fields:
        form2.fields[fieldname].disabled = True

    pathresult = settings.RESULT_SEMANTIC_DIR + "/" + resolve(request.path).app_name  +"/" + mode + "/result"

    with open(pathresult + "/" + DicResultc.nomresult + ".txt", "r") as f:
        table = f.read()

    AccesToCalcul = False
    AccesToSave = False
    allmodes = AllModes()

    # Utile pour qu'un utlisateur qui sauve des résultats puisse aussi les supprimer lui même
    # la gestion de la permission se trouve dans result.html
    ResultSpeUser = False
    if DicResultc.user_restrict2.isdigit():
        if int(DicResultc.user_restrict2) == request.user.id:
            ResultSpeUser = True

    return form, modelscselect, allmodes, form2, results, table, AccesToSave, AccesToCalcul, ResultSpeUser


def InitResultAllSelect(request,ModelFormGeneric):
    modes = AllModes()
    AllResult = []
    for mode in modes:
        DicInitModelD, DicInitFormD = ModelFormGeneric(mode)
        ResultMode = DicInitModelD["resultat"].objects.all()
        SelectUserResultMode = SelectResultFctUser(request, ResultMode)
        AllResult.append(SelectUserResultMode)
    ZipModeResult = zip(modes, AllResult)
    return ZipModeResult




