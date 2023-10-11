
import os,tempfile, shutil
from django.conf import settings
from AllApps.Traitement.Semantique.TableauEmb.periph.amont import CreateDictFromExpe, DiffDic, ExpandMode, TestListForCompare
from AllApps.Traitement.Semantique.TableauEmb.models import Expe, Glove, Word2Vec, FastText
from AllApps.Traitement.Semantique.TableauEmb.forms import Word2VecForm, GloveForm, FastTextForm
from AllApps.Traitement.Semantique.DiachroGroup.models import GloveDiachro, Word2VecDiachro, FastTextDiachro
from AllApps.Traitement.Semantique.DiachroGroup.forms import  GloveDiachroRedForm, Word2VecDiachroRedForm, FastTextDiachroRedForm,\
    GloveDiachroCompletForm, Word2VecDiachroCompletForm, FastTextDiachroCompletForm


def ModelFormInit(mode):
    DicInitModelD = {}
    DicInitFormD = {}

    if mode == "glove":
        DicInitModelD = {"initial": Glove, "resultat": GloveDiachro}
        DicInitFormD = {"initial": GloveForm, "resultatdeb": GloveDiachroRedForm, "resultatfin": GloveDiachroCompletForm}
    elif mode == "word2vec":
        DicInitModelD = {"initial": Word2Vec, "resultat": Word2VecDiachro}
        DicInitFormD = {"initial": Word2VecForm, "resultatdeb": Word2VecDiachroRedForm, "resultatfin": Word2VecDiachroCompletForm}
    elif mode == "fasttext":
        DicInitModelD = {"initial": FastText, "resultat": FastTextDiachro}
        DicInitFormD = {"initial": FastTextForm, "resultatdeb": FastTextDiachroRedForm, "resultatfin": FastTextDiachroCompletForm}
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


def TestNbrTermesEtClusterOk(nresult, ncluster, epoque, revue):
    """
    :param nresultencours: string nombre simple (ex : "5") ou nombres séparés virgule (ex: "5,4,5")
    :param ncluster: idem
    :param epoqueencours: deux dates avec tiret (ex: 1960-1976) ou multiples séparés par virgule (ex: 1960-1976,1977-1978)
    :param revueencours: "Annales" ou "Espace" ou "Annales,Espace"

    Va test si un nombre de result et de cluster par revue*epoque existante
    par exemple, si revueencours = "Annales,Espace" et si "1960-1971,1972-1985"
    il faut soit deux chaines de caractères spécificiant chacune un chiffre : nbre terme et cluster qui va s'appliquer à toutes les revue*époque
            soit deux chaines de caractères spécificiant chacune trois chiffres :
                - le premier va s'appliquer à Annales 1960-1971
                - le deuxième va s'appliquer à Annales 1972-1985
                (- Espace 1960-1971 n'existe pas : revue pas encore créée)
                - le troisième va s'applique à Espace 1972-1985

    :return: string "ok" or "notok" suivant le résultat du test

    """
    ReponseTest = "ok"
    nresultsplit = nresult.split(',')
    nclustersplit = ncluster.split(',')
    if len(nresultsplit) > 1 or len(nclustersplit) > 1:
        compteur = 0
        # si les deux = 1 "ok" sinon calcul ci dessous
        ListEpoques = epoque.split(",")
        ListRevues = revue.split(",")
        for EpoqueDecompos in ListEpoques:
            for Revue in ListRevues:
                # 1892 date création Annales
                if Revue == "Annales" and int(EpoqueDecompos.split("-")[1]) >= 1892 and int(EpoqueDecompos.split("-")[0]) <= 2000 :
                    compteur += 1
                # 1892 date création Annales
                if Revue == "Espace" and int(EpoqueDecompos.split("-")[1]) >= 1972 and int(EpoqueDecompos.split("-")[0]) <= 2000:
                    compteur += 1

        if compteur != len(nresultsplit) or compteur != len(nclustersplit):
            ReponseTest = "notok"

    return ReponseTest


########## CREATE AND DELETE FILE ############

def CreateDossierTemporaire(mode):
    """
    :param mode: string "glove","word2vec" ou "fasttext"

    crée le dossier temporaire pour stocker résultat de ce mode si n'existe pas
    + crée un sous dossier temporaire dans ce dossier pour stocker résultat qui vont être produit 

    :return: string qui renvoie au chemin du sous-dossier

    """
    folder = settings.RESULT_SEMANTIC_DIR + "/Diachro/" + mode + "/temp"
    if not os.path.exists(folder):
        os.makedirs(folder)
    path = tempfile.mkdtemp(dir=folder)
    return path


def CreateDossierSave(mode):
    folder = settings.RESULT_SEMANTIC_DIR + "/Diachro/" + mode + "/save"
    if not os.path.exists(folder):
        os.makedirs(folder)


def CreateDossierResultDia(path):
    PathSauvResult = path + "/3)Matching/ResultDia"
    if not os.path.exists(PathSauvResult):
        os.makedirs(PathSauvResult)



def RemoveOldTempFolder(modeactuel, seuil):
    folder = settings.RESULT_SEMANTIC_DIR + "/Diachro/" + modeactuel + "/temp"
    a = [s for s in os.listdir(folder)]
    a.sort(key=lambda s: os.path.getmtime(os.path.join(folder, s)))
    if len(a) > seuil:
        shutil.rmtree(folder + "/" + a[0])



def CopyTempToSave(modeactuel, pathresult, name):
    foldertempbase = settings.RESULT_SEMANTIC_DIR + "/Diachro/" + modeactuel + "/temp"
    nametemp = pathresult.split("---")[1]
    foldertemp = foldertempbase + "/" + nametemp

    pathresult = settings.RESULT_SEMANTIC_DIR + "/Diachro/" + modeactuel + "/save/" + name

    # Copier le fichier !
    if os.path.isdir(foldertemp):
        shutil.copytree(foldertemp, pathresult)

    shutil.rmtree(foldertemp)
    os.rename(pathresult + "/4)Json/" + nametemp + ".json", pathresult + "/4)Json/" + name + ".json")


################# RECUP DATA #########################

def RecupDataCalcul(DicInitModelD,modele_id,test_form_result):

    donnees_model = DicInitModelD["initial"].objects.get(id=modele_id)
    donnees_result = test_form_result.cleaned_data
    nom = donnees_model.nom
    revues = donnees_model.revue
    epoques = donnees_model.epoque
    terme = donnees_result['terme']
    nresult = donnees_result['nresult']
    user= donnees_result['user_restrict2']
    calculPoidsLabel = donnees_result['calculPoidsLabel']
    compareJustNewRevue = donnees_result['compareJustNewRevue']
    selectLink = donnees_result['selectLink']
    couleursRevues = donnees_result['couleursRevues']
    methode_clustering = donnees_result['methode_clustering']
    ncluster = donnees_result['ncluster']
    taillecluster = donnees_result['taillecluster']
    stop_mots = donnees_result['stop_mots']

    return nom, revues, epoques, terme, nresult, user, calculPoidsLabel,compareJustNewRevue, selectLink, couleursRevues,\
           methode_clustering, ncluster, taillecluster, stop_mots




def RecupDataSave(request):
    """Attention ne va pas chercher dans le formulaire mais dans dans enregistrement cachée dans last
    permet d'éviter que la modification d'un formulaire entre l'effectuation des résultats et leur sauvegarde ait un impact"""
    terme = request.POST.get("termelast")
    nresult = request.POST.get("nresultlast")
    calculPoidsLabel = request.POST.get("calculPoidsLabellast")
    compareJustNewRevue = request.POST.get("compareJustNewRevuelast")
    SelectLink= request.POST.get("SelectLinklast")
    couleursRevues = request.POST.get("couleursRevueslast")
    methode_clustering = request.POST.get("mclusteringlast")
    taillecluster = request.POST.get("tailleclusterlast")
    ncluster = request.POST.get("nclusterlast")
    stop_mots = request.POST.get("stop_motslast")
    name = request.POST.get("namesave")
    pathresultlastencours = request.POST.get("pathresultlast")
    seuilencours = request.POST.get("myRange")
    seuil100 = int(float(seuilencours) * 100)
    return terme, nresult, calculPoidsLabel,compareJustNewRevue, SelectLink, couleursRevues,\
           methode_clustering, ncluster, taillecluster, stop_mots, name, pathresultlastencours, seuil100



################ COMPARE RESULT #################

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
        pathresult = settings.RESULT_SEMANTIC_DIR + "/Diachro/" + mode + "/save/"
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
    Mode1 = ListModesVisibles[0]
    path_result_transfo1 = "save---" + expe1R.nomresult
    expe2R = listExpeVisibleResultat[1]
    Mode2 = ListModesVisibles[1]
    path_result_transfo2 = "save---" + expe2R.nomresult

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

    seuil1_100 = expe1R.seuil100
    seuil2_100 = expe2R.seuil100
    seuilselect1 = seuil1_100 / 100
    seuilselect2 = seuil2_100 / 100

    return expe1R, expe2R, Mode1, Mode2, ListExpesStock, dict1,  dict2, \
           parachoices,formchoices,taillechoices, ZipExpe1, ZipExpe2, \
           path_result_transfo1, path_result_transfo2, seuilselect1, seuilselect2
