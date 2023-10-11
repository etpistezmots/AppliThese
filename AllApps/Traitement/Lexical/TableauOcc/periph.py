import os
from .models import CountOcc
from .forms import CountOccRedForm
from django.conf import settings
from AllApps.Traitement.Semantique.TableauEmb.periph.amont import SelectModelFctUser
from AllApps.PreTraitement.Persee.FinaliseCorpus.models import CorpusFin


########### Recup Data #############

def RecupDataOcc(request):
    terme = request.POST.get("termelast")
    corpus = request.POST.get("corpuslast")
    epoque= request.POST.get("epoquelast")
    revue = request.POST.get("revuelast")
    table = request.POST.get("tablelast")
    name= request.POST.get("namesave")
    return terme, corpus, epoque, revue, table, name


########## Prepa Affichage #######

def ParaInitialResult():
    CorpusFinFirst = CorpusFin.objects.first()
    print(CorpusFinFirst)
    DicInitParaResult = {"terme": "espace",
                         "CorpusFinRef": CorpusFinFirst.id,
                         "revue": "Annales,Espace",
                         "epoque": "1950-1960,1961-1971,1972-1984,1985-1995",
                         "user_restrict": "0"}
    return DicInitParaResult


def InitOccInterface(request, mode):
    resultsAll = CountOcc.objects.filter(mode=mode)
    results = SelectModelFctUser(request, resultsAll)

    if len(results) > 0:
        form = CountOccRedForm(instance=results[-1])
    else:
        ParaInitial = ParaInitialResult()
        form = CountOccRedForm(initial=ParaInitial)

    return form, results


def InitOccResultBeforeSave(request, mode, donnees):
    PresenceNewResult = True

    PossibleSave = False
    if request.user.id is not None:
        PossibleSave = True

    idlast = ""
    if request.user.is_superuser:
        idlast = donnees['user_restrict']

    corpus = donnees['CorpusFinRef'].nom
    termelast = donnees['terme']
    revuelast = donnees['revue']
    epoquelast = donnees['epoque']

    resultsAll = CountOcc.objects.filter(mode=mode)

    results = SelectModelFctUser(request, resultsAll)

    return PresenceNewResult, PossibleSave, corpus, termelast, revuelast, epoquelast, results, idlast


def InitOccResult(request, mode, Resultc):
    filename = settings.RESULT_LEXICAL_DIR + "/TableauOcc/" + mode + "/" + str(Resultc.nomresult) + ".txt"

    with open(filename, 'r') as f:
        table = f.read()

    termesList = Resultc.terme.split(",")
    UnSeulTerme = False
    Terme = ""
    if len(termesList) == 1:
        UnSeulTerme = True
        Terme = termesList[0]

    corpus = Resultc.CorpusFinRef.nom

    # Utile pour qu'un utlisateur qui sauve des résultats puisse aussi les supprimer lui même
    ResultSpeUser = False
    if Resultc.user_restrict.isdigit():
        if int(Resultc.user_restrict) == request.user.id:
            ResultSpeUser = True

    MyForm = CountOccRedForm(instance=Resultc)
    return table, UnSeulTerme, Terme, termesList, corpus, MyForm, ResultSpeUser


################ Suppr #################

def SupprOneOcc(mode, Resultc):
    filename = settings.RESULT_LEXICAL_DIR + "/TableauOcc/" + mode + "/" + str(Resultc.nomresult) + ".txt"
    os.remove(filename)
    Resultc.delete()

def SupprMultiOcc(request):
    modes = ['Simple',"Auteur"]
    for mode in modes:
        ListOccASuppr = request.POST.getlist('selected_occ' + mode)
        for resultatsuppr in ListOccASuppr:
            Resultc = CountOcc.objects.get(id=resultatsuppr)
            SupprOneOcc(mode, Resultc)