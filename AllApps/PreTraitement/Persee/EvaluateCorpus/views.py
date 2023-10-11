import os, csv, sys, random
from django.shortcuts import render
from django.conf import settings
from AllApps.PreTraitement.Persee.FinaliseCorpus.models import CorpusFin, CorpusComplet, DicoMotLemme, DicoExpression, DicoSuffixe
from AllApps.PreTraitement.Persee.FinaliseCorpus.views import DicoMotPicke, buildcleans2
from pandas import read_csv
from lxml import etree

# Create your views here.

def SelectCorpusFinFctUser(request,CorpusFinAll):
    "selectionne les réductions a afficher en focntion de l'utilisateur"
    CorpusFinselect = []
    if request.user.id is not None:
        # si c'est un superutilisateur, affiche tous les modèles :
        if request.user.is_superuser:
            CorpusFinselect = list(CorpusFinAll)
        # sinon affiche que les publics et ceux correspondant à son numéro
        else:
            for elt in CorpusFinAll:
                if str(request.user.id) in elt.user_restrict.split(","):
                    CorpusFinselect.append(elt)
    return CorpusFinselect



def CountDocAndWord(request, corpusfin):
    CorpusToCount = CorpusFin.objects.filter(nom=corpusfin)
    if CorpusToCount.exists():
        FileCorpus = settings.RESULT_PRETRAIT_DIR  + "/FinaliseCorpus/CorpusFin/" + corpusfin + ".csv"
        csv.field_size_limit(sys.maxsize)
        compteurdocs = 0
        compteurmots = 0
        with open(FileCorpus, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter='\t')
            next(reader)
            for row in reader:
                txt = row[7]
                txtsplit = txt.split()
                lentxtsplit = len(txtsplit)
                if lentxtsplit !=0:
                    compteurdocs +=1
                    compteurmots = compteurmots + lentxtsplit
        context = {"nomcorpus":corpusfin, "compteurdocs":str(compteurdocs), "compteurmots":str(compteurmots)}
        return render(request,'EvaluateCorpus/SuccessCount.html',context)
    else:
        context = {"nomcorpus": corpusfin}
        return render(request, 'EvaluateCorpus/FailCount.html',context)



def SelectEchantillonEvaluate(request, corpusfin, n_docs, n_mots, n_eval):

    DossierResultG = settings.RESULT_PRETRAIT_DIR + "/EvaluateCorpus"

    if not os.path.exists(DossierResultG):
        os.makedirs(DossierResultG)

    DossierResult = settings.RESULT_PRETRAIT_DIR + "/EvaluateCorpus/" + corpusfin + "_" + str(n_docs) + "_" +\
                    str(n_mots) + "_" + str(n_eval)

    if not os.path.exists(DossierResult):
        os.makedirs(DossierResult)

    FichierResult = settings.RESULT_PRETRAIT_DIR + "/EvaluateCorpus/" + corpusfin + "_" + str(n_docs) + "_" +\
                    str(n_mots) + "_" + str(n_eval) + ".txt"

    SelectDocs = []
    SelectIndexes = []
    SelectTexts = []

    if not os.path.isfile(FichierResult):
        CorpusToCount = CorpusFin.objects.filter(nom=corpusfin)
        if CorpusToCount.exists():
            FichierCorpus = settings.RESULT_PRETRAIT_DIR + "/FinaliseCorpus/CorpusFin/" + corpusfin + ".csv"
            csv.field_size_limit(sys.maxsize)
            # liste de tous les docs
            AllDocs = []
            with open(FichierCorpus, 'r') as csvfile:
                reader = csv.reader(csvfile, delimiter='\t')
                next(reader)
                for row in reader:
                    AllDocs.append(row[1])
            # Algo de sélection
            random.shuffle(AllDocs)
            n_docstemp = n_docs
            while n_docstemp>0 and len(AllDocs)>0:
                DocSelect = AllDocs.pop()
                with open(FichierCorpus, 'r') as csvfile:
                    reader = csv.reader(csvfile, delimiter='\t')
                    next(reader)
                    for row in reader:
                        if row[1] == DocSelect:
                            txtsplit = row[7].split()
                            lentxt = len(txtsplit)
                            if lentxt > n_mots:
                                SelectDocs.append(DocSelect[8:])
                                IndexSelect = random.randrange(lentxt - n_mots)
                                SelectIndexes.append(str(IndexSelect) + " , " + str(IndexSelect +n_mots))
                                TxtSelect = txtsplit[IndexSelect:IndexSelect + n_mots]
                                SelectTexts.append(" ".join(TxtSelect))
                                n_docstemp = n_docstemp - 1


            if len(AllDocs)==0:
                context = {"corpusfin": corpusfin, "n_docs": str(n_docs), "n_mots": str(n_mots),"n_eval": str(n_eval)}
                return render(request, 'EvaluateCorpus/FailEchantillon.html',context)
            else:
                # Ecriture Fichier Result
                with open(FichierResult, 'w') as f:
                    for i,doc in enumerate(SelectDocs):
                        f.write(doc + "\n")
                        f.write(SelectIndexes[i] + "\n")
                        f.write(SelectTexts[i] + "\n")
                        f.write("\n")

                # Crée des fichiers pour préparer à l'évaluation
                for i,doc in enumerate(SelectDocs):
                    FichierPrepaEvalue = DossierResult + "/" + doc + ".csv"
                    with open(FichierPrepaEvalue, 'w', newline='',encoding="utf-8") as f:
                        writer = csv.writer(f, delimiter='\t')
                        writer.writerow(["TextActual", "TextRef", "OK", "S", "D", "I", "Delimitation","Océrisation","Lemmatisation","Autre"])
                        for mot in SelectTexts[i].split():
                            # remplissage par défault comme si tout était OK
                            writer.writerow([mot,mot,1,0,0,0,0,0,0,0])

        else:
            context = {"corpusfin": corpusfin, "n_docs": str(n_docs), "n_mots": str(n_mots), "n_eval": str(n_eval)}
            return render(request, 'EvaluateCorpus/FailEchantillon.html',context)

    else:
        # lecture fichier
        with open(FichierResult, 'r') as f:
            content = f.readlines()
            compte  = 0
            for i, elt in enumerate(content):
                decompte = i - compte
                if decompte == 0:
                    SelectDocs.append(elt)
                elif decompte == 1:
                    SelectIndexes.append(elt)
                elif decompte == 2:
                    SelectTexts.append(elt)
                else:
                    compte = i +1

    AddresseDocsPersee = []
    for doc in SelectDocs:
        AddresseDocsPersee.append("<a href='https://www.persee.fr/doc/" + doc +"'>" + doc + "</a>")

    AddresseEvaluation= []
    for doc in SelectDocs:
        AddresseEvaluation.append("<a href='https://analytics.huma-num.fr/EtPistezMots/evaluate/EvaluateDetail/" + corpusfin + "/" + str(n_docs)
                                  + "/"+ str(n_mots) + "/" + str(n_eval) + "/" + doc + "'>Détail de l'évaluation</a>")


    Result = zip(AddresseDocsPersee,SelectIndexes,SelectTexts,AddresseEvaluation)
    context = {"Result": Result, "corpusfin":corpusfin, "n_docs":str(n_docs), "n_mots":str(n_mots), "n_eval":str(n_eval)}
    return render(request, 'EvaluateCorpus/Echantillon.html', context)


def EvaluateDetail(request, corpusfin, n_docs, n_mots, n_eval, doc):
    FichierResult = settings.RESULT_PRETRAIT_DIR + "/EvaluateCorpus/" + corpusfin + "_" + str(n_docs) + "_" + \
                    str(n_mots) + "_" + str(n_eval) + "/" + doc + "Done" + ".csv"

    if os.path.exists(FichierResult):
        Essai = read_csv(FichierResult, delimiter='\t')
        tableauhtml = Essai.to_html(classes='mystyle')
        context = {"tableauhtml":tableauhtml,"corpusfin":corpusfin, "doc":doc, "n_docs": n_docs, "n_mots": n_mots, "n_eval": n_eval,
                   "str_n_docs": str(n_docs), "str_n_mots": str(n_mots), "str_n_eval": str(n_eval)}
        return render(request, 'EvaluateCorpus/EvaluateDetail.html', context)
    else:
        return render(request, 'EvaluateCorpus/EvaluateDetailFail.html')


def CreateCorpusArticlePlusCrNonLem2(request):

    if request.user.is_superuser:

        CorpusBase = settings.RESULT_PRETRAIT_DIR  + "/FinaliseCorpus/CorpusFin/ArticlePlusCrLem.csv"
        NewCorpus = settings.RESULT_PRETRAIT_DIR + "/FinaliseCorpus/CorpusFin/ArticlePlusCrLem2.csv"

        if not os.path.exists(NewCorpus):

            XpathDiveRev = '/tei:TEI/tei:text/tei:body//tei:div[@type="rev"]'

            DicoM,DicoL = DicoMotPicke("IraMotsAmelior2")
            dicomotkey = DicoM.keys()

            FichierExpression = settings.DATA_DIR + "/Dico/Finalise/IraExpressionsAmelior2.txt"
            FichierSuffixe = settings.DATA_DIR + "/Dico/Finalise/FinMots1.txt"

            with open(FichierExpression) as f:
                content = f.readlines()
            ExpressionsList = []
            for line in content:
                eltsplit = line.rstrip().split("\t")
                ExpressionsList.append((eltsplit[0], eltsplit[1]))

            with open(FichierSuffixe) as f:
                content = f.readlines()
            SuffixesList = []
            for line in content:
                eltsplit = line.rstrip().split("\t")
                SuffixesList.append((eltsplit[0], eltsplit[1]))

            csv.field_size_limit(sys.maxsize)

            with open(NewCorpus, 'a', newline='') as fresult:
                writer = csv.writer(fresult, delimiter='\t')
                writer.writerow(
                    ["Id", "NomPersee", "Revue", "Date", "Type", "Titre", "Auteur", "Text"])

                with open(CorpusBase, 'r') as csvfile:
                    reader = csv.reader(csvfile, delimiter='\t')
                    next(reader)
                    for l,row in enumerate(reader):
                        textdoc = row[7]
                        ref = row[1]
                        if ref[0:11]=="NoRefPersee":
                            writer.writerow(
                                [l, row[1], row[2], row[3], row[4], row[5], row[6], row[7]])
                        else:
                            dossier = "_".join(ref.split("_")[1:7])
                            revue = ref.split("_")[1]
                            FichierSource = settings.DATA_DIR + "/revues/" + revue + "/" + dossier + "/tei/" + ref + "_tei.xml"
                            tree = etree.parse(FichierSource)
                            test = tree.xpath(XpathDiveRev, namespaces={"tei": "http://www.tei-c.org/ns/1.0"})

                            if len(test)>0:

                                for k,elt in enumerate(test):
                                    RecupText = []
                                    for elt1 in elt.findall(".//word"):
                                        RecupText.append(elt1.text)
                                    RecupTextSansNone = [x for x in RecupText if x is not None]
                                    txtclean = buildcleans2(" ".join(RecupTextSansNone), ExpressionsList, SuffixesList)

                                    newtext = []

                                    for mot in txtclean.split():
                                        if (len(mot) >= 2) and (mot[0:2] in dicomotkey) and (mot in DicoM[mot[0:2]]):
                                            # Aller chercher lemme même index !!
                                            lem = DicoL[mot[0:2]][DicoM[mot[0:2]].index(mot)]
                                            newtext.append(lem)

                                    # methode probaliliste car il peut avoir quelques mots reconstitués
                                    # empèche reconnaissance par stricte égalité
                                    lennewtext = len(newtext)
                                    firstindex = 0
                                    lastindex = 0
                                    compte = 0

                                    if lennewtext > 2:
                                        for i, j in enumerate(range(0, lennewtext-3)):
                                            sectionnewtext = " ".join(newtext[j:j + 3])

                                            try:
                                                resultendroit = textdoc.index(sectionnewtext)
                                            except:
                                                resultendroit = -1

                                            try:
                                                resultenvers = textdoc.rindex(sectionnewtext)
                                            except:
                                                resultenvers = -1

                                            if resultendroit!=-1 and resultenvers!=-1 and resultendroit != resultenvers:
                                                compte +=1
                                                if firstindex == 0:
                                                    firstindex = resultenvers
                                                lastindex = resultenvers + len(sectionnewtext)

                                        ratio = compte / (i+1)

                                        # si plus d'un quart des tuples se répètent, on enelève la partie
                                        if ratio >0.25:
                                            textdoc = textdoc[0:firstindex] + textdoc[lastindex:]

                                if len(textdoc)>0:
                                    writer.writerow(
                                        [l, row[1], row[2], row[3], row[4], row[5], row[6], textdoc])

                            else:
                                writer.writerow(
                                    [l, row[1], row[2], row[3], row[4], row[5], row[6], row[7]])

            CorpusCompletReference = CorpusComplet.objects.filter(nom="ArticlePlusCrComplet")
            DicoExpressionReference = DicoExpression.objects.filter(nom="IraExpressionsAmelior2")
            DicoSuffixeReference = DicoSuffixe.objects.filter(nom="FinMots1")
            DicoMotLemmeReference = DicoMotLemme.objects.filter(nom="IraMotsAmelior2")


            CorpusToSave = CorpusFin(nom="ArticlePlusCrLem2",user_restrict="0",date="29/01/2021",CorpusCompletRef=CorpusCompletReference[0],
                                     PretraitIraBase=True, DicoExpressionRef=DicoExpressionReference[0], DicoSuffixeRef=DicoSuffixeReference[0],
                                     Lemmatisation=True,DicoMotLemmeRef=DicoMotLemmeReference[0])
            CorpusToSave.save()

            return render(request, 'EvaluateCorpus/CreateCorpusArticlePlusCrLem2Succes.html')
        else:
            return render(request, 'EvaluateCorpus/CreateCorpusArticlePlusCrLem2DejaOK.html')

    else:

        return render(request, 'EvaluateCorpus/CreateCorpusArticlePlusCrLem2Fail.html')



