import os, csv, sys
from django.urls import resolve
from django.conf import settings
from AllApps.Traitement.Semantique.TableauEmb.models import Expe, Glove, Word2Vec, FastText, GloveR, Word2VecR, FastTextR
from AllApps.Traitement.Semantique.TableauEmb.forms import Word2VecForm, GloveForm, FastTextForm,\
    Word2VecResRedForm, GloveResRedForm, FastTextResRedForm, Word2VecResCompletForm, GloveResCompletForm, FastTextResCompletForm
from .df2html import  reducehtml, transformcolor, transformquanti, inverse
from itertools import combinations
import pandas as pd


##################### GENERAL #####################

def AllModes():
    allmodes = ["word2vec", "glove", "fasttext"]
    return allmodes


def ModelFormInit(mode):
    DicInitModelD = {}
    DicInitFormD = {}

    if mode == "word2vec":
        DicInitModelD = {"initial": Word2Vec, "resultat": Word2VecR}
        DicInitFormD = {"initial": Word2VecForm, "resultatdeb": Word2VecResRedForm, "resultatfin":  Word2VecResCompletForm}
    elif mode == "glove":
        DicInitModelD = {"initial": Glove, "resultat": GloveR}
        DicInitFormD = {"initial": GloveForm, "resultatdeb": GloveResRedForm,"resultatfin": GloveResCompletForm}
    elif mode == "fasttext":
        DicInitModelD = {"initial": FastText, "resultat": FastTextR}
        DicInitFormD = {"initial": FastTextForm, "resultatdeb": FastTextResRedForm,"resultatfin":  FastTextResCompletForm}
    return DicInitModelD, DicInitFormD


################  SELECT ########################


def SelectModelFctUser(request, modelsc):
    modelscselect = []
    # si l'utilisateur n'est pas connecté, alors tous les modèles publics
    # c'est à dire avec user_restric = 0
    if request.user.id is None:
        for elt in modelsc:
            if elt.user_restrict == "0":
                modelscselect.append(elt)
    # si l'utisateur est connecté
    else:
        # si c'est un superutilisateur, affiche tous les modèles :
        if request.user.is_superuser:
            modelscselect = list(modelsc)
        # sinon affiche que les publics et ceux correspondant à son numéro
        else:
            for elt in modelsc:
                if elt.user_restrict == "0" or str(request.user.id) in elt.user_restrict.split(","):
                    modelscselect.append(elt)
    return modelscselect



def SelectResultFctUser(request, results):
    resultsselect = []
    # si l'utilisateur n'est pas connecté, alors tous les modèles publics
    # c'est à dire avec user_restric = 0
    if request.user.id is None:
        for elt in results:
            if elt.user_restrict2 == "0":
                resultsselect.append(elt)
    # si l'utisateur est connecté
    else:
        # si c'est un superutilisateur, affiche tous les modèles :
        if request.user.is_superuser:
            resultsselect = list(results)
        # sinon affiche que les publics et ceux correspondant à son numéro
        else:
            for elt in results:
                if elt.user_restrict2 == "0" or str(request.user.id) in elt.user_restrict2.split(","):
                    resultsselect.append(elt)
    return resultsselect


def SelectLastMode(request, mode_defaut):
    AllExpeOrdr = Expe.objects.all().order_by('-id')
    # selection du modèle en fonction de l'user !
    ExpeSelectExpe = SelectModelFctUser(request, AllExpeOrdr)
    if len(ExpeSelectExpe) != 0:
        LastExpe = ExpeSelectExpe[0]
        mode = LastExpe.polymorphic_ctype.model
    else:
        mode = mode_defaut

    return mode



############## TEST ############

def TestModelExist(mode, modeleid, ModelFormGeneric):
    Exist = False
    DicInitModelD, DicInitFormD = ModelFormGeneric(mode)
    test = DicInitModelD["initial"].objects.filter(id=modeleid)
    Modelc = None
    if test.exists():
        Modelc = test[0]
        Exist = True
    return Exist, DicInitModelD, DicInitFormD, Modelc


def TestModelAccess(request, DicInitModelD, Modelc):
    ModelscAll = DicInitModelD["initial"].objects.all()
    ModelscSelect = SelectModelFctUser(request, ModelscAll)
    Access = False
    if Modelc in ModelscSelect:
        Access = True
    return Access, ModelscSelect


def TestResultExist(modeleid, resultid, DicInitModelD):
    Exist = False
    test = DicInitModelD["resultat"].objects.filter(id=resultid)
    Resultc = None
    if test.exists():
        Resultc = test[0]
        if Resultc.modelc.id == modeleid:
            Exist = True
    return Exist, Resultc


def TestResultAccess(request, DicInitModelD, Modelc, Resultc):
    ResultsAll = DicInitModelD["resultat"].objects.filter(modelc=Modelc)
    ResultsSelect = SelectResultFctUser(request, ResultsAll)
    Access = False
    if Resultc in ResultsSelect:
        Access = True
    return Access, ResultsSelect


def TestListForCompare(request, ListeExpe, ModelFormGeneric):
    errorG2 = False
    ListeExpeList = ListeExpe.split("-")
    for expe in ListeExpeList:
        error, mode = ExpandMode(expe[0])
        if error:
            errorG2 = True
            break
        DicInitModelD, DicInitFormD = ModelFormGeneric(mode)
        if expe[1:].isdigit():
            test = DicInitModelD["resultat"].objects.filter(id=expe[1:])
            # verification expe existe
            if test.exists():
                Resultc = test[0]
                Modelc = Resultc.modelc
                ResultsAll = DicInitModelD["resultat"].objects.filter(modelc=Modelc)
                ResultsSelect = SelectResultFctUser(request, ResultsAll)
                # verification acces expe ok
                if Resultc not in ResultsSelect:
                    errorG2 = True
                    break
            else:
                errorG2 = True
                break
        else:
            errorG2 = True
            break
    return errorG2


def TestResultCompare(request, listexpesvisibles, listexpesstock, paraselect, revueselect):
    errorG = False

    if paraselect not in ["All","Diff","No"]:
        errorG = True

    if revueselect not in ["Ann","Esp","AnnEsp"]:
        errorG = True

    errorG2 = TestListForCompare(request, listexpesvisibles, ModelFormInit)
    if errorG2:
        errorG = True
    errorG2 = TestListForCompare(request, listexpesstock, ModelFormInit)
    if errorG2:
        errorG = True

    return errorG


################# RECUP DATA #####################

def RecupDataCalcul(DicInitModelD,modele_id,test_form_result):
    donnees_model = DicInitModelD["initial"].objects.get(id=modele_id)
    donnees_result = test_form_result.cleaned_data
    nom = donnees_model.nom
    revue = donnees_model.revue
    epoque = donnees_model.epoque
    terme = donnees_result["terme"]
    nresult = donnees_result["nresult"]
    return nom, revue, epoque,terme, nresult


def RecupDataSave(request):
    """Attention ne va pas chercher dans le formulaire mais dans dans enregistrement cachée dans last
    permet d'éviter que la modification d'un formulaire entre l'effectuation des résultats et leur sauvegarde ait un impact"""
    terme = request.POST.get("termelast")
    nresult = request.POST.get("nresultlast")
    name = request.POST.get("namesave")
    table = request.POST.get("table")
    return terme, nresult, name, table


def RecupUser(request):
    """Pour usage accessible qu'à des utilisateurs connectés"""
    if request.user.is_superuser:
        userencours = request.POST.get("user_restrict2last")
    else:
        userencours = str(request.user.id)
    return userencours



################  CREATE FILE AND FOLDER ############


def PathModeleCreate(request, mode, name):
    # resolve(request.path).app_name est égale au nom de l'app. Ici "TableauEmb"
    # permet de faire une fonction plus générique
    f_model_gen = settings.RESULT_SEMANTIC_DIR + "/" + resolve(request.path).app_name + "/" + mode + "/modele"
    f_model_actual = f_model_gen + "/" + name
    if not os.path.exists(f_model_actual):
        os.makedirs(f_model_actual)


def PathResultCreate(request,mode):
    f_model_gen = settings.RESULT_SEMANTIC_DIR + "/" + resolve(request.path).app_name + "/" + mode + "/result"
    if not os.path.exists(f_model_gen):
        os.makedirs(f_model_gen)
    return f_model_gen


####################### PREPA CORE ####################

def PrepaAmontEpoqueRevue(revues, epoques):
    ListEpoques = epoques.split(",")
    ListRevues = revues.split(",")

    ListEpoquesDecompos = []
    for elt in ListEpoques:
        dateinf = int(elt.split("-")[0])
        datesup = int(elt.split("-")[1])
        ListEpoquesDecompos.append((dateinf, datesup))
    return ListRevues, ListEpoquesDecompos


class MyIter(object):
    def __init__(self, corpus, dateinf, datemax, revue):
        self.corpus = corpus
        self.dateinf = dateinf
        self.datemax = datemax
        self.revue = revue

    def __iter__(self):
        path = self.corpus
        with open(path, 'r') as f:
            csv.field_size_limit(sys.maxsize)
            reader = csv.reader(f, delimiter='\t')
            next(reader)  # skip the heading
            for row in reader:
                IdEncours, NomPerseeEnCours, RevueEnCours, DateEnCours, TypeEnCours, TitreEnCours, AuteursEnCours, TextEnCours = row
                if int(DateEnCours) >= self.dateinf and int(DateEnCours) <= self.datemax and RevueEnCours == self.revue:
                    yield TextEnCours.split()


def prepaglove(corpus, dateinf, datemax, revue):
    with open(corpus, 'r') as f_in:
        csv.field_size_limit(sys.maxsize)
        reader = csv.reader(f_in, delimiter='\t')
        next(reader)  # skip the heading
        with open(settings.GLOVE_DIR + '/textok.txt', 'w') as f_out:
            for row in reader:
                IdEncours, NomPerseeEnCours, RevueEnCours, DateEnCours, TypeEnCours, TitreEnCours, AuteursEnCours, TextEnCours = row
                if int(DateEnCours) >= dateinf and int(DateEnCours) <= datemax and RevueEnCours == revue:
                    f_out.write(TextEnCours + "\n")




################ PREPA COMPARE ##############################

def SumAndConcatlistAllSelect(request):
    tot = 0
    ConcatListExpeStock = ""
    for mode in AllModes():
        result = request.POST.getlist('selected_' + mode)
        lenresult = len(result)
        tot = tot + lenresult
        for expeid in result:
            ConcatListExpeStock = ConcatListExpeStock + mode[0] + expeid + "-"
    return ConcatListExpeStock,tot

def ExpandMode(moderesume):
    error = False
    modeselect = ""
    if moderesume == "g":
        modeselect = "glove"
    elif moderesume == "w":
        modeselect = "word2vec"
    elif moderesume == "f":
        modeselect = "fasttext"
    else:
        error = True
    return error, modeselect



def PrepaMultiResults(tot,ConcatListExpeStock):
    if tot > 5:
        tot = 5
    ConcatListExpesVisibles = "-".join(ConcatListExpeStock.split("-", tot)[:tot])
    paradefaut = "All"
    revuedefaut = "Ann"
    ndefaut = 0

    return ConcatListExpesVisibles, paradefaut, revuedefaut, ndefaut


def CreateDictFromExpe(expe, DicInitModelDselect, modele, mode):
    dictR = dict(expe.__dict__)
    listelttoremoveR = ["_state", "id", "nom", "user_id", 'nomresult', 'user_restrict2', 'modelc_id']
    for elt in listelttoremoveR:
        dictR.pop(elt, None)
    expeM = DicInitModelDselect["initial"].objects.get(id=modele)
    dictM = dict(expeM.__dict__)
    listelttoremoveM = ["_state", "id", "polymorphic_ctype_id", "nom", "CorpusFinRef", "expe_ptr_id", 'user_restrict']
    for elt in listelttoremoveM:
        dictM.pop(elt, None)
    dictInit = {}
    dictInit["mode"] = mode
    dictresult = dict(**dictInit, **dictM, **dictR)
    return dictresult


def DiffDic(dic1, dic2):
    dic1diff = {}
    dic2diff = {}
    for elt in dic1.keys():
        if elt in dic2.keys():
            if dic1[elt] != dic2[elt]:
                dic1diff[elt] = dic1[elt]
                dic2diff[elt] = dic2[elt]
        else:
            dic1diff[elt] = dic1[elt]

    for elt in dic2.keys():
        if elt not in dic1.keys():
            dic2diff[elt] = dic2[elt]

    return dic1diff, dic2diff

def ExtendDiffDic(dic1, dic2, dic3):
    dic1diff = {}
    dic2diff = {}
    dic3diff = {}

    dic1diff1, dic2diff1 = DiffDic(dic1, dic2)
    dic1diff2, dic3diff1 = DiffDic(dic1, dic3)
    dic2diff2, dic3diff2 = DiffDic(dic2, dic3)

    for elt in dic1diff1.keys():
        dic1diff[elt] = dic1diff1[elt]

    for elt in dic1diff2.keys():
        if elt not in dic1diff.keys():
            dic1diff[elt] = dic1diff2[elt]

    for elt in dic2diff1.keys():
        dic2diff[elt] = dic2diff1[elt]

    for elt in dic2diff2.keys():
        if elt not in dic2diff.keys():
            dic2diff[elt] = dic2diff2[elt]

    for elt in dic3diff1.keys():
        dic3diff[elt] = dic3diff1[elt]

    for elt in dic3diff2.keys():
        if elt not in dic3diff.keys():
            dic3diff[elt] = dic3diff2[elt]

    return dic1diff, dic2diff, dic3diff


def SuperExtendDiffDic(listdict):

    comptelist = []
    listdicdiff = []
    for elt in listdict:
        comptelist.append(0)
        listdicdiff.append({})

    listdicdifftemp = []
    for elt in listdict:
        listsousdicdiff = []
        for i in range(len(listdict)):
            if i != 0:
                listsousdicdiff.append({})
        listdicdifftemp.append(listsousdicdiff)

    # https://stackoverflow.com/questions/27150990/python-itertools-combinations-how-to-obtain-the-indices-of-the-combined-numbers
    listindex = list((i, j) for ((i, _), (j, _)) in combinations(enumerate(listdict), 2))

    for i, elt in enumerate(list(combinations(listdict, 2))):
        index1 = listindex[i][0]
        comptelist[index1] = comptelist[index1] + 1
        index2 = listindex[i][1]
        comptelist[index2] = comptelist[index2] + 1

        dictemp1, dictemp2 = DiffDic(elt[0], elt[1])
        listdicdifftemp[index1][comptelist[index1] - 1] = dictemp1
        listdicdifftemp[index2][comptelist[index2] - 1] = dictemp2

    resultlistdic = []
    for elt in listdicdifftemp:
        resulttemp = {}
        for sselt in elt:
            for key in sselt.keys():
                if key not in resulttemp.keys():
                    resulttemp[key] = sselt[key]
        resultlistdic.append(resulttemp)


    return resultlistdic


def DoMultiResult(listexpesvisibles,listexpesstock,paraselect,revueselect,nselect,color=False):
    """A Factoriser """

    ListModesVisibles = []
    ListExpesVisibleSplit = listexpesvisibles.split("-")
    for expevisible in ListExpesVisibleSplit:
        error, mode = ExpandMode(expevisible[0])
        ListModesVisibles.append(mode)

    tot = len(ListModesVisibles)

    ListExpesStock = []
    ListModesStock = []
    for expestock in listexpesstock.split("-"):
        error, mode = ExpandMode(expestock[0])
        ListModesStock.append(mode)
        DicInitModelDselect, DicInitFormDselect = ModelFormInit(mode)
        ExpeStockM = DicInitModelDselect["resultat"].objects.filter(id =int(expestock[1:]))
        ListExpesStock.append(ExpeStockM[0])

    # liste des chemins pour accèdes aux résultats des expé visibles
    listpathresult = []
    for mode in ListModesVisibles:
        pathresult = settings.RESULT_SEMANTIC_DIR + "/TableauEmb/" + mode + "/result"
        listpathresult.append(pathresult)

    listExpeVisibleResultat = []
    listDicInitModelDselect = []
    ListModelesVisibles = []
    for i, mode in enumerate(ListModesVisibles):
        numeroexpe = int(ListExpesVisibleSplit[i][1:])
        DicInitModelDselect, DicInitFormDselect = ModelFormInit(mode)
        listDicInitModelDselect.append(DicInitModelDselect)
        expeR = DicInitModelDselect["resultat"].objects.get(id=numeroexpe)
        listExpeVisibleResultat.append(expeR)
        ListModelesVisibles.append(expeR.modelc.id)

    listnresult = []
    for expe in listExpeVisibleResultat:
        n = expe.nresult
        listnresult.append(n)
    nmin = min(listnresult)

    nref = nmin

    if nselect == 0:
        nselect = nmin

    if not color:
        listtable = []
    else:
        listedf = []

    listdictcomplet = []
    for i, pathresult in enumerate(listpathresult):
        expe = listExpeVisibleResultat[i]
        with open(pathresult + "/" + expe.nomresult + ".txt", "r") as f:
            table = f.read()
            table = reducehtml(table, nselect, revueselect)

            if not color:
                listtable.append(table)
            else:
                df, LabelsColonnes, LabelsLignes = inverse(table)
                listedf.append(df)

        if paraselect == "All" or paraselect == "Diff":
            dict = CreateDictFromExpe(expe, listDicInitModelDselect[i], ListModelesVisibles[i], ListModesVisibles[i])
            listdictcomplet.append(dict)


        if color:
            dfresult = pd.DataFrame(columns=LabelsColonnes, index=LabelsLignes)
            dfsame = pd.DataFrame(columns=LabelsColonnes, index=LabelsLignes)

            dfref = listedf[0]
            for j, col in enumerate(dfref.columns):
                for i in range(len(dfref)):

                    # Fait une liste de liste de tous les termes à comparer
                    # et une liste de tous les termes
                    ListListTermCompareAll = []
                    AllTermes = []
                    for dfcompare in listedf:
                        SousListTermCompare = []
                        decompos1 = dfcompare.iloc[i, j].split("\n")
                        for elt in decompos1:
                            mot = elt.split(" ")[0]
                            SousListTermCompare.append(mot)
                            if mot not in AllTermes:
                                AllTermes.append(mot)
                        ListListTermCompareAll.append(SousListTermCompare)

                    # Compare liste à liste
                    ResultAllTerme = 0
                    ResultSameTermeInAllList = 0
                    ListSameTermeInAllList = []
                    for l, ListTermCompare in enumerate(ListListTermCompareAll):
                        if ListTermCompare != ['']:
                            ResteListListTermCompareAll = ListListTermCompareAll[:l] + ListListTermCompareAll[l + 1:]
                            for TermeCompare in ListTermCompare:
                                ResultAllTerme += 1
                                Same = True
                                for ResteListTermCompareAll in ResteListListTermCompareAll:
                                    if TermeCompare in ResteListTermCompareAll:
                                        continue
                                    else:
                                        Same = False
                                if Same:
                                    ResultSameTermeInAllList += 1
                                    if TermeCompare not in ListSameTermeInAllList:
                                        ListSameTermeInAllList.append(TermeCompare)

                    if ResultAllTerme != 0:
                        ResultFin = ResultSameTermeInAllList / ResultAllTerme
                        dfresult.iloc[i, j] = ResultFin
                        dfsame.iloc[i, j] = " ".join(ListSameTermeInAllList)

            listtable = []
            for dfcompare in listedf:
                table = transformcolor(dfcompare, dfsame)
                listtable.append(table)

            tableresultquanti = transformquanti(dfresult)


    if paraselect == "Diff":
        listdictcomplet = SuperExtendDiffDic(listdictcomplet)

    if paraselect == "No":
        listdictcomplet = []
        for i in range(tot):
            dict = {}
            listdictcomplet.append(dict)

    ListListExpePotentielConcat = []
    for i, expe1 in enumerate(listExpeVisibleResultat):
        ListExpePotentielConcat = []
        for j, expe2 in enumerate(ListExpesStock):
            modeexpe2 = ListModesStock[j]
            DecomposListEspesVisibles = listexpesvisibles.split("-")
            DecomposListEspesVisibles.pop(i)
            InsertNewElt = DecomposListEspesVisibles[:i] + [modeexpe2[0] + str(expe2.id)] + DecomposListEspesVisibles[i:]
            RecomposListNew = "-".join(InsertNewElt)
            ListExpePotentielConcat.append([expe2, RecomposListNew])
        ListListExpePotentielConcat.append(ListExpePotentielConcat)

    revueschoices = ["AnnEsp", "Ann", "Esp"]
    parachoices = ["All", "Diff", "No"]
    nchoices = [i for i in range(1, nref + 1)]
    CompteurExpes = [str(i) for i in range(1, tot + 1)]
    CompteurExpes2 = ["expe" + str(i) for i in range(1, tot + 1)]
    CompteurDiv = ["div" + str(i) for i in range(1, tot + 1)]
    CompteurDiezeDiv = ["#div" + str(i) for i in range(1, tot + 1)]
    CompteurReducNbreExpe = []
    if tot > 2:
        CompteurReducNbreExpe = [i for i in range(tot - 1, 1, -1)]
    ConcatReducNbreExpe = []
    if tot == 3:
        ConcatReducNbreExpe = ["-".join(listexpesvisibles.split("-", 2)[:2])]
        print("-".join(listexpesvisibles.split("-", 3)[:3]))
    elif tot == 4:
        ConcatReducNbreExpe = ["-".join(listexpesvisibles.split("-", 3)[:3]),
                               "-".join(listexpesvisibles.split("-", 2)[:2])]
    elif tot == 5:
        ConcatReducNbreExpe = ["-".join(listexpesvisibles.split("-", 4)[:4]),
                               "-".join(listexpesvisibles.split("-", 3)[:3]),
                               "-".join(listexpesvisibles.split("-", 2)[:2])]

    DivisEcran = str(round(100 / tot)) + "%"

    MegaZipExpeVisibles = zip(CompteurExpes, CompteurExpes2, listExpeVisibleResultat, listtable, listdictcomplet,
                              ListListExpePotentielConcat, CompteurDiv)
    MiniZip = zip(CompteurReducNbreExpe, ConcatReducNbreExpe)

    if not color:
        return MegaZipExpeVisibles, ListExpesStock, MiniZip, revueschoices, parachoices, nchoices, DivisEcran, tot, CompteurDiezeDiv
    else:
        return MegaZipExpeVisibles, ListExpesStock, MiniZip, revueschoices, parachoices, nchoices, DivisEcran, tot, \
               CompteurDiezeDiv, tableresultquanti










