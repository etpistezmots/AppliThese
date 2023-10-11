import os, tempfile, shutil, json
from django.conf import settings
from django.urls import resolve
from AllApps.Traitement.Semantique.TableauEmb.models import  Word2Vec, Glove, FastText
from AllApps.Traitement.Semantique.TableauEmb.forms import Word2VecForm, GloveForm, FastTextForm
from .. models import GloveRCluster, Word2VecRCluster, FastTextRCluster
from ..forms import GloveClusterRedForm, Word2VecClusterRedForm, FastTextClusterRedForm, \
    GloveClusterRedSimpleForm, Word2VecClusterRedSimpleForm, FastTextClusterRedSimpleForm, \
    GloveClusterCompletForm, Word2VecClusterCompletForm, FastTextClusterCompletForm
from AllApps.Traitement.Semantique.TableauEmb.periph.amont import CreateDictFromExpe, DiffDic, ExpandMode, TestListForCompare
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt


def ModelFormInit(mode):
    DicInitModelD = {}
    DicInitFormD = {}

    if mode == "glove":
        DicInitModelD = {"initial": Glove, "resultat": GloveRCluster}
        DicInitFormD = {"initial": GloveForm, "resultatdeb": GloveClusterRedForm,
                        "resultatsimple": GloveClusterRedSimpleForm, "resultatfin": GloveClusterCompletForm}
    elif mode == "word2vec":
        DicInitModelD = {"initial": Word2Vec, "resultat": Word2VecRCluster}
        DicInitFormD = {"initial": Word2VecForm, "resultatdeb": Word2VecClusterRedForm,
                        "resultatsimple": Word2VecClusterRedSimpleForm, "resultatfin": Word2VecClusterCompletForm}
    elif mode == "fasttext":
        DicInitModelD = {"initial": FastText, "resultat": FastTextRCluster}
        DicInitFormD = {"initial": FastTextForm, "resultatdeb": FastTextClusterRedForm,
                        "resultatsimple": FastTextClusterRedSimpleForm, "resultatfin": FastTextClusterCompletForm}


    return DicInitModelD, DicInitFormD


############ TEST #################

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

############# CREATE FOLDER RESULT #################

def PathResultCreate(request, mode, name):
    f_model_gen = settings.RESULT_SEMANTIC_DIR + "/" + resolve(request.path).app_name + "/" + mode + "/save"
    f_model_actual = f_model_gen + "/" + name
    if not os.path.exists(f_model_actual):
        os.makedirs(f_model_actual)
    return f_model_actual



##############  RECUP DATA ################

def RecupDataCalcul(DicInitModelD,modele_id,test_form_result):
    donnees_model = DicInitModelD["initial"].objects.get(id=modele_id)
    donnees_result = test_form_result.cleaned_data
    nom = donnees_model.nom
    revue = donnees_result['choixrevue']
    epoque = donnees_result['choixepoque']
    terme = donnees_result['terme']
    nresult = donnees_result['nresult']
    user = donnees_result["user_restrict2"]
    methode_clustering = donnees_result["methode_clustering"]
    ncluster = donnees_result["ncluster"]
    link = donnees_result["link"]
    color_singleton = donnees_result["color_singleton"]

    return nom, revue, epoque, terme, nresult, user, methode_clustering, ncluster, link, color_singleton


def RecupDataSave(request):
    revue = request.POST.get("revuechoixlast")
    epoque = request.POST.get("epoquechoixlast")
    terme = request.POST.get("termelast")
    nresult = int(request.POST.get("nresultlast"))
    pathresult = request.POST.get("pathresultlast")
    name = request.POST.get("namesave")
    methode_clustering = request.POST.get("mclusteringlast")
    ncluster = int(request.POST.get("nclusterlast"))
    link = request.POST.get("linklast")
    testnoderecup = request.POST.get('testnoderecup')
    testedgerecup = request.POST.get('testedgerecup')
    color_singleton = request.POST.get('color_singletonlast')
    return terme, nresult, revue, epoque, name, testnoderecup, testedgerecup, pathresult,methode_clustering,ncluster,\
           link,color_singleton


################ CREATE ETLECTURE RESULT #######################

def CalculDiagrammeTaille(nresultencours, methode_clustering):
    if methode_clustering == "Kmeans":
        taillediagramme = 0
    else:
        # taille du diagramme en fonction nombre de résultats !
        if nresultencours < 6:
            taillediagramme = str(nresultencours * 60) + "px"
        elif nresultencours >= 6 and nresultencours < 11:
            taillediagramme = str(nresultencours * 55) + "px"
        elif nresultencours >= 11 and nresultencours < 21:
            taillediagramme = str(nresultencours * 50) + "px"
        elif nresultencours >= 21 and nresultencours < 41:
            taillediagramme = str(nresultencours * 45) + "px"
        elif nresultencours >= 41 and nresultencours < 61:
            taillediagramme = str(nresultencours * 35) + "px"
        elif nresultencours >= 61 and nresultencours < 81:
            taillediagramme = str(nresultencours * 30) + "px"
        else:
            taillediagramme = str(nresultencours * 25) + "px"
    return taillediagramme


def LectureResult(pathresult):
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
    return nodes_list,edges_list

################### ENREGISTREMENT ####################

def EnregistrTemp(mode, methode_clustering):
    # pas d'enregistrement dans ce cas, renvoie juste path_result_transfo
    # comme une chaine de caractères vide
    if methode_clustering == "Kmeans":
        path_result_transfo = ""
    else:
        folder = settings.RESULT_SEMANTIC_DIR + "/Cluster/" + mode + "/temp"
        if not os.path.exists(folder):
            os.makedirs(folder)

        path = tempfile.mkstemp(dir=folder, suffix='.png')
        plt.savefig(path[1])
        plt.close()

        # au bout de 15 fichiers va enlever le plus ancien
        seuil = 15
        a = [s for s in os.listdir(folder)]
        a.sort(key=lambda s: os.path.getmtime(os.path.join(folder, s)))
        if len(a) > seuil:
            os.remove(folder + "/" + a[0])

        path_result_transfo = "temp---" + path[1].split("/")[-1]
    return path_result_transfo



def SavePerm(mode, name, pathresult, pathresultsave, methode_clustering, testnoderecup, testedgerecup):
    ErrorSave = False
    with open(pathresultsave + "/noderecup.txt", "w") as f:
        testnoderecup = testnoderecup.replace("\'", "\"")
        noderecupTransform = json.loads(testnoderecup)
        if testnoderecup[0] == "[":
            for v in noderecupTransform:
                f.writelines(json.dumps(v) + "\n")
        elif testnoderecup[0] == "{":
            for k, v in noderecupTransform.items():
                f.writelines(json.dumps(v) + "\n")

    with open(pathresultsave + "/edgerecup.txt", "w") as f:
        testedgerecup = testedgerecup.replace("\'", "\"")
        edgerecupTransform = json.loads(testedgerecup)
        if testedgerecup[0] == "[":
            for v in edgerecupTransform:
                f.writelines(json.dumps(v) + "\n")
        elif testedgerecup[0] == "{":
            for k, v in edgerecupTransform.items():
                f.writelines(json.dumps(v) + "\n")

    if methode_clustering != "Kmeans":

        # sauve  dendrogramme
        foldertemp = settings.RESULT_SEMANTIC_DIR + "/Cluster/" + mode + "/temp"
        nametemp = pathresult.split("---")[1]
        filetemp = foldertemp + "/" + nametemp

        print(filetemp)

        if os.path.isfile(filetemp):
            shutil.copyfile(filetemp, pathresultsave + "/" + name + ".png")
        else:
            ErrorSave = True

    return ErrorSave


##############  COMPARE RESULT ##########

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
        pathresult = settings.RESULT_SEMANTIC_DIR + "/Cluster/" + mode + "/save/"
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
    nodes_list1, edges_list1 = LectureResult(pathresult1)
    expe2R = listExpeVisibleResultat[1]
    pathresult2 = listpathresult[1] + "/" + expe2R.nomresult
    nodes_list2, edges_list2 = LectureResult(pathresult2)

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

    taillediagramme1 = CalculDiagrammeTaille(expe1R.nresult, expe1R.methode_clustering)
    taillediagramme2 = CalculDiagrammeTaille(expe2R.nresult, expe2R.methode_clustering)

    return expe1R, expe2R, ListExpesStock, nodes_list1, edges_list1, nodes_list2, edges_list2, dict1,  dict2, \
           parachoices,formchoices, taillechoices, taillediagramme1, taillediagramme2, ZipExpe1, ZipExpe2