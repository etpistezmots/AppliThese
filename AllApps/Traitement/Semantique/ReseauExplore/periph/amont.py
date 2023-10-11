
import os,json
from django.conf import settings
from django.urls import resolve
from ..models import  FastTextRExplo, GloveRExplo, Word2VecRExplo
from ..forms import FastTextResRedForm,  GloveResRedForm,  Word2VecResRedForm,\
    FastTextResRedSimpleForm, GloveResRedSimpleForm, Word2VecResRedSimpleForm,\
    FastTextResCompletForm, GloveResCompletForm, Word2VecResCompletForm
from AllApps.Traitement.Semantique.TableauEmb.models import  Word2Vec, Glove, FastText
from AllApps.Traitement.Semantique.TableauEmb.forms import Word2VecForm, GloveForm, FastTextForm
from AllApps.Traitement.Semantique.TableauEmb.periph.amont import CreateDictFromExpe, DiffDic, ExpandMode, TestListForCompare

########### GENERAL #############

def ModelFormInit(mode):
    DicInitModelD = {}
    DicInitFormD = {}

    if mode == "word2vec":
        DicInitModelD = {"initial": Word2Vec, "resultat": Word2VecRExplo}
        DicInitFormD = {"initial": Word2VecForm, "resultatdeb": Word2VecResRedForm,
                        "resultatsimple": Word2VecResRedSimpleForm,"resultatfin": Word2VecResCompletForm}
    elif mode == "glove":
        DicInitModelD = {"initial": Glove, "resultat": GloveRExplo}
        DicInitFormD = {"initial": GloveForm, "resultatdeb": GloveResRedForm,
                        "resultatsimple": GloveResRedSimpleForm,"resultatfin": GloveResCompletForm}
    elif mode == "fasttext":
        DicInitModelD = {"initial": FastText, "resultat": FastTextRExplo}
        DicInitFormD = {"initial": FastTextForm, "resultatdeb": FastTextResRedForm,
                        "resultatsimple": FastTextResRedSimpleForm,"resultatfin": FastTextResCompletForm}
    return DicInitModelD, DicInitFormD


############## TEST ############



def TestResultCompare(request, listexpesvisibles, listexpesstock, paraselect, formselect, tailleselect):
    errorG = False

    if paraselect not in ["All","Diff","No"]:
        errorG = True

    if formselect not in ["vertical","horizontal"]:
        errorG = True

    if tailleselect not in ['200px', '300px', '400px', '500px', '600px', '700px', '800px', '900px', '1000px', '1100px','1200px']:
        errorG = True

    errorG2 = TestListForCompare(request, listexpesvisibles, ModelFormInit)
    if errorG2:
        errorG = True
    errorG2 = TestListForCompare(request, listexpesstock, ModelFormInit)
    if errorG2:
        errorG = True

    return errorG


################# CREATE FILE #############

def PathResultCreate(request, mode, name):
    f_model_gen = settings.RESULT_SEMANTIC_DIR + "/" + resolve(request.path).app_name + "/" + mode + "/result"
    f_model_actual = f_model_gen + "/" + name
    if not os.path.exists(f_model_actual):
        os.makedirs(f_model_actual)
    return f_model_actual

######################## RECUP DATA ######################

def RecupDataCalcul(DicInitModelD,modele_id,test_form_result):
    donnees_model = DicInitModelD["initial"].objects.get(id=modele_id)
    donnees_result = test_form_result.cleaned_data
    nom = donnees_model.nom
    revue = donnees_result['choixrevue']
    epoque = donnees_result['choixepoque']
    terme= donnees_result['terme']
    nresult = donnees_result['nresult']
    user =  donnees_result["user_restrict2"]

    return nom, revue, epoque, terme, nresult, user


def RecupDataSave(request):
    terme = request.POST.get("termelast")
    nresult = request.POST.get("nresultlast")
    revue= request.POST.get("revuechoixlast")
    epoque = request.POST.get("epoquechoixlast")
    name = request.POST.get("namesave")
    indexnode = request.POST.get("IndexNode")
    indexedge = request.POST.get("IndexEdge")
    dejaouvert = request.POST.get('dejaouvert')
    dejaouvertindex = request.POST.get('dejaouvertindex')
    allactions = request.POST.get('allactions')
    testnoderecup = request.POST.get('testnoderecup')
    testedgerecup = request.POST.get('testedgerecup')
    oriented = request.POST.get('oriented')

    return terme,nresult,revue,epoque,name,indexnode,indexedge,dejaouvert,dejaouvertindex,\
           allactions,testnoderecup,testedgerecup,oriented



############## ECRITURE / LECTURE RESULT ############


def EcritureResult(pathresult,dejaouvert,dejaouvertindex,allactions,testnoderecup,testedgerecup):
    with open(pathresult + "/dejaouvert.txt", "w") as f:
        f.write(dejaouvert)
    with open(pathresult + "/dejaouvertindex.txt", "w") as f:
        f.write(dejaouvertindex)
    with open(pathresult + "/allactions.txt", "w") as f:
        f.write(allactions)

    with open(pathresult + "/noderecup.txt", "w") as f:
        testnoderecup = testnoderecup.replace("\'", "\"")
        noderecupTransform = json.loads(testnoderecup)
        if testnoderecup[0] == "[":
            for v in noderecupTransform:
                f.writelines(json.dumps(v) + "\n")
        elif testnoderecup[0] == "{":
            for k, v in noderecupTransform.items():
                f.writelines(json.dumps(v) + "\n")

    with open(pathresult + "/edgerecup.txt", "w") as f:
        testedgerecup = testedgerecup.replace("\'", "\"")
        edgerecupTransform = json.loads(testedgerecup)
        if testedgerecup[0] == "[":
            for v in edgerecupTransform:
                f.writelines(json.dumps(v) + "\n")
        elif testedgerecup[0] == "{":
            for k, v in edgerecupTransform.items():
                f.writelines(json.dumps(v) + "\n")


def LectureResult(pathresult):
    with open(pathresult + "/dejaouvert.txt", "r") as f:
        dejaouvert = f.read()
    with open(pathresult + "/dejaouvertindex.txt", "r") as f:
        dejaouvertindex = f.read()
    with open(pathresult + "/allactions.txt", "r") as f:
        allactions = f.read()

    nodes_list = []
    with open(pathresult + "/noderecup.txt", "r") as f:
        content = f.readlines()
        for node in content:
            nodes_list.append(json.loads(node))

    edges_list = []
    with open(pathresult + "/edgerecup.txt", "r") as f:
        content = f.readlines()
        for edge in content:
            edges_list.append(json.loads(edge))
    return dejaouvert, dejaouvertindex, allactions, nodes_list, edges_list


################## COMPARE prepa et do ################

def PrepaTwoResults(ConcatListExpeStock):
    ConcatListExpesVisibles = "-".join(ConcatListExpeStock.split("-", 2)[:2])
    # par default
    paradefault = "All"
    formatdefault = "vertical"
    tailledefault = '600px'

    return ConcatListExpesVisibles, paradefault, formatdefault, tailledefault


def DoTwoResults(listexpesvisibles,listexpesstock,paraselect):

    ListModesVisibles = []
    ListExpesVisibleSplit = listexpesvisibles.split("-")
    for expevisible in ListExpesVisibleSplit:
        error, mode = ExpandMode(expevisible[0])
        ListModesVisibles.append(mode)


    ListExpesStock = []
    ListModesStock = []
    for expestock in listexpesstock.split("-"):
        error, mode = ExpandMode(expestock[0])
        ListModesStock.append(mode)
        DicInitModelDselect, DicInitFormDselect = ModelFormInit(mode)
        ExpeStockM = DicInitModelDselect["resultat"].objects.filter(id=int(expestock[1:]))
        ListExpesStock.append(ExpeStockM[0])

    # liste des chemins pour accèdes aux résultats des expé visibles
    listpathresult = []
    for mode in ListModesVisibles:
        pathresult = settings.RESULT_SEMANTIC_DIR + "/ReseauExplore/" + mode + "/result"
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


    expe1R = listExpeVisibleResultat[0]
    pathresult1 = listpathresult[0] + "/" + expe1R.nomresult
    dejaouvert1, dejaouvertindex1, allactions1, nodes_list1, edges_list1 = LectureResult(pathresult1)
    expe2R = listExpeVisibleResultat[1]
    pathresult2 = listpathresult[1] + "/" + expe2R.nomresult
    dejaouvert2, dejaouvertindex2, allactions2, nodes_list2, edges_list2 = LectureResult(pathresult2)

    if paraselect == "All" or paraselect == "Diff":
        dict1 = CreateDictFromExpe(expe1R, listDicInitModelDselect[0], ListModelesVisibles[0], ListModesVisibles[0])
        dict2 = CreateDictFromExpe(expe2R, listDicInitModelDselect[1], ListModelesVisibles[1], ListModesVisibles[1])

    if paraselect == "Diff":
        dict1, dict2 = DiffDic(dict1, dict2)

    if paraselect == "No":
        dict1 = {}
        dict2 = {}

    ListeExpePotentiel1=[]
    for j, expe in enumerate(ListExpesStock):
        modeexpe = ListModesStock[j]
        DecomposListEspesVisibles = listexpesvisibles.split("-")
        InsertNewElt = [modeexpe[0] + str(expe.id)] + [DecomposListEspesVisibles[1]]
        RecomposListNew = "-".join(InsertNewElt)
        ListeExpePotentiel1.append(RecomposListNew)
    ZipExpe1 = zip(ListExpesStock,ListeExpePotentiel1)

    ListeExpePotentiel2 = []
    for j, expe in enumerate(ListExpesStock):
        modeexpe = ListModesStock[j]
        DecomposListEspesVisibles = listexpesvisibles.split("-")
        InsertNewElt = [DecomposListEspesVisibles[0]] + [modeexpe[0] + str(expe.id)]
        RecomposListNew = "-".join(InsertNewElt)
        ListeExpePotentiel2.append(RecomposListNew)
    ZipExpe2 = zip(ListExpesStock, ListeExpePotentiel2)

    parachoices = ["All", "Diff", "No"]
    formchoices = ["vertical", "horizontal"]
    taillechoices = ['200px', '300px', '400px', '500px', '600px', '700px', '800px', '900px', '1000px', '1100px',
                     '1200px']
    return expe1R, expe2R, ListExpesStock, dejaouvert1, dejaouvertindex1, allactions1, nodes_list1, edges_list1,\
           dejaouvert2, dejaouvertindex2,allactions2, nodes_list2, edges_list2, dict1,  dict2, ZipExpe1, ZipExpe2,\
           parachoices,formchoices, taillechoices