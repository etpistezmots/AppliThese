import os, shutil, csv, re, pickle, sys
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse
from django.contrib import messages
from .forms import CorpusAddForm, CorpusCompletForm, CorpusCompletFormVisuel, DicoMotLemmeForm,\
    DicoSuffixeForm,DicoExpressionForm,FNRRequestForm, CorpusFinForm,CorpusFinFormVisuel
from .models import TextAdd, CorpusAdd, CorpusComplet, DicoMotLemme, DicoSuffixe, DicoExpression, CorpusFin
from AllApps.PreTraitement.Persee.DelimitCorpus.models import DocReference, Auteur, Revue, CorpusEtude
import datetime
from langdetect import detect
from collections import Counter
from AllApps.PreTraitement.Persee.DelimitCorpus.models import CorpusEtude

# Create your views here.

def home(request):
    return render(request,'FinaliseCorpus/home.html')

def AjoutEtRetrait(request):
    reductionsall = CorpusEtude.objects.all().order_by("pk")
    reductionsselect = []
    if request.user.is_authenticated:
        for reduction in reductionsall:
            if request.user.is_superuser or (str(request.user.id) in reduction.user_restrict.split(",")):
                if reduction.SyntheseTransformRef is not None:
                    reductionsselect.append(reduction)
    context = {"reductions": reductionsselect}
    return render(request, 'FinaliseCorpus/1)AjoutEtRetraitDoc.html', context)


def AmeliorPretrait(request):
    return render(request, 'FinaliseCorpus/2)b)AmeliorPretrait.html')

def AppliEtLimitPretrait(request):
    return render(request, 'FinaliseCorpus/2)c)AppliEtLimitPretrait.html')

def CorpusAddFct(request):
    if request.method == 'POST':
        if 'Effectuer' in request.POST:
            formToSave = CorpusAddForm(data=request.POST)
            # si le formulaire est valide
            if formToSave.is_valid():
                # sauve les donneés dans la bd
                lv = formToSave.save()
                donnees = formToSave.cleaned_data
                # ajouter traitement du csv pour creer texte individuellement
                dossierref = settings.DATA_DIR + "/CorpusAdd"
                fichier = dossierref + "/" + donnees["nom"] + ".csv"

                # efface le dossier spécifique si existe et le recrée
                dossierspe = dossierref + "/" + donnees["nom"]
                if os.path.exists(dossierspe):
                    shutil.rmtree(dossierspe)
                    os.makedirs(dossierspe)
                else:
                    os.makedirs(dossierspe)

                with open(fichier, 'r') as csvfile:
                    reader = csv.reader(csvfile, delimiter='\t')
                    next(reader)
                    for row in reader:
                        # Il faut déjà que le csv soit rentré à la main
                        # n'a pas été intégré en upload car django peu adapté pour un tel usave en production
                        # https://docs.djangoproject.com/en/3.0/howto/static-files/#serving-files-uploaded-by-a-user-during-development
                        NewTextAdd = TextAdd(titre = row[1].capitalize(),
                                             nomfichier = donnees["nom"] + str(row[0]),
                                             annee = row[2],
                                             type = row[3],
                                             revue = row[4],
                                             auteurs = row[5],
                                             CorpusAddRef = CorpusAdd.objects.filter(id=row[6])[0])
                        NewTextAdd.save()

                        fichierspe = dossierspe + "/" + donnees["nom"] + str(row[0])

                        with open(fichierspe, 'w') as f:
                            f.write(row[7])

                context = {"NomCorpusAdd": donnees["nom"]}
                return render(request, 'FinaliseCorpus/CorpusAdd/SuccessAddCorpus.html',context)
            else:
                return render(request, 'FinaliseCorpus/CorpusAdd/EchecAddCorpus.html')

    if request.user.is_superuser:
        FormCorpusAdd = CorpusAddForm()
        context = {"FormCorpusAdd": FormCorpusAdd}
        return render(request, 'FinaliseCorpus/CorpusAdd/CorpusAddFct.html', context)
    else:
        return render(request, 'FinaliseCorpus/AbsenceDroit.html')


def VisualiseCorpusAdd(request, NomCorpusAdd):
    Test = CorpusAdd.objects.filter(nom=NomCorpusAdd)
    if Test.exists():
        docs = TextAdd.objects.filter(CorpusAddRef=Test[0])
        nbredocs = len(docs)
        context = {"Cadd":Test[0], "docs":docs, "nbredocs":nbredocs}
        return render(request, 'FinaliseCorpus/CorpusAdd/VisualiseAddCorpus.html', context)
    else:
        context = {"NomCorpusAddNotExsit": NomCorpusAdd}
        return render(request, 'FinaliseCorpus/CorpusAdd/EchecVisualiseAddCorpus.html', context)


def RemoveCorpusAdd(request):
    if request.method == 'POST':
        if ('Supprimer' in request.POST) and request.user.is_superuser:
            nom = request.POST.get('nom')
            CorpusToSuppr = CorpusAdd.objects.get(nom=nom)
            FichierCSVExist = settings.DATA_DIR + "/CorpusAdd/" + nom + '.csv'
            os.remove(FichierCSVExist)
            DossierText = settings.DATA_DIR + "/CorpusAdd/" + nom
            shutil.rmtree(DossierText)
            CorpusToSuppr.delete()
            context = {"nom": nom}
            return render(request, 'FinaliseCorpus/CorpusAdd/CorpusAddRemoveSuccess.html', context)

        else:
            return redirect('FinaliseCorpus:home')

    # Accès interface
    if request.user.is_superuser:
        AllCorpusAddEnCours = CorpusAdd.objects.all()
        context = {"AllCorpusAddEnCours": AllCorpusAddEnCours}
        return render(request, 'FinaliseCorpus/CorpusAdd/CorpusAddRemoveInterface.html', context)
    else:
        return redirect('FinaliseCorpus:home')


def LangueDetectFct(request, reduction):

    DossierExtract = settings.RESULT_PRETRAIT_DIR + "/AmeliorText/"\
                    + reduction + "/fin"
    DossierResult = settings.RESULT_PRETRAIT_DIR + "/FinaliseCorpus/CorpusAmelior/"\
                    + reduction
    FichierResult = DossierResult + "/DetectLang.txt"

    print(DossierExtract)
    #/Bureau/EtPistezMots/result4/pretrait/AmeliorText/ArticlePlusCr
    if os.path.exists(DossierExtract):
        ArtSuspicNotFr = []
        if not os.path.isfile(FichierResult):
            for elt in os.listdir(DossierExtract):
                print(elt)
                fichierencours = open(DossierExtract + "/" + elt, "r")
                txt = fichierencours.read()
                if len(txt)!=0:
                    if detect(txt) != "fr":
                        ArtSuspicNotFr.append('<a href="https://www.persee.fr/doc/' +
                                       elt[8:-4] + '">' + elt[8:-4] + '</a>')

            if not os.path.exists(DossierResult):
                os.makedirs(DossierResult)

            with open(FichierResult, 'w') as f:
                f.write("Document suspecté en langue étrangère" + "\n")
                for elt in ArtSuspicNotFr:
                    f.write(elt + "\n")

            ArtSuspicNotFr.insert(0, ("Document suspecté en langue étrangère du corpus " + reduction + "\n"))


        else:
            with open(FichierResult, 'r') as f:
                ArtSuspicNotFr = f.readlines()
        context = {"ArtSuspicNotFr":ArtSuspicNotFr,"reduction":reduction}
        return render(request, 'FinaliseCorpus/ArtSuspicNotFr.html', context)
    else:
        print("TEST")
        context = {"reduction": reduction}
        return render(request, 'FinaliseCorpus/AbsenceResult.html', context)


def CorpusAddEtRemoveInterface(request, reduction):
    if request.method == 'POST':
        if 'Effectuer' in request.POST and request.user.is_superuser:
            formToSave = CorpusCompletForm(data=request.POST)
            # si le formulaire est valide
            if formToSave.is_valid():
                lv = formToSave.cleaned_data
                EltRemoveList = lv['EltRemove'].split(",")

                DossierResult = settings.RESULT_PRETRAIT_DIR + "/AmeliorText/" \
                                 + reduction + "/fin"
                DossierCSVFin = settings.RESULT_PRETRAIT_DIR + "/FinaliseCorpus/CorpusComplet"

                FichierCsvCorpusAdd = settings.DATA_DIR + "/CorpusAdd/" + lv['CorpusAddRef'].nom + ".csv"

                if not os.path.exists(DossierResult):
                    context = {"reduction": reduction}
                    return render(request, 'FinaliseCorpus/AbsenceResult.html', context)

                if not os.path.exists(DossierCSVFin):
                    os.makedirs(DossierCSVFin)


                with open(DossierCSVFin + "/" + lv['nom'] + ".csv", 'w', newline='') as f:
                    writer = csv.writer(f, delimiter='\t')
                    writer.writerow(["Id", "NomPersee", "Revue", "Date", "Type", "Titre", "Auteur", "Text"])

                    i=0
                    for i,file in enumerate(os.listdir(DossierResult)):
                        if file not in EltRemoveList:
                            with open(DossierResult + '/' + file, "r") as f2:
                                Texte = f2.read()
                            DocReferenceRef = DocReference.objects.get(TextRef=file[:-4] + "_tei.xml")
                            auteurs = DocReferenceRef.AuteursRef.all()
                            auteurstring = ""
                            for j,auteur in enumerate(auteurs):
                                if j ==0:
                                    auteurstring = auteur.prenom.replace(".","").replace(",","") + " " + auteur.nom.replace(".","").replace(",","")
                                else:
                                    auteurstring =  auteurstring + "," + auteur.prenom.replace(".","").replace(",","") + " " + auteur.nom.replace(".","").replace(",","")
                            writer.writerow([i+1, file[:-4], DocReferenceRef.RevueRef.nom,
                                             DocReferenceRef.annee, DocReferenceRef.type, DocReferenceRef.titre, auteurstring, Texte.replace("\t","").replace('"',"").replace("\n"," ")])

                    with open(FichierCsvCorpusAdd, 'r') as csvfile:
                        reader = csv.reader(csvfile, delimiter='\t')
                        next(reader)
                        for j,row in enumerate(reader):
                            writer.writerow([i + 1 + j + 1, "NoRefPersee" + str(j +1), row[4],
                                             row[2], row[3], row[1], row[5],row[7].replace("\t", "").replace('"', "").replace("\n"," ")])


                    CorpusEtudeEnCours = CorpusEtude.objects.get(nom=reduction)

                    CorpusCompletRef = CorpusComplet(nom=lv['nom'],user_restrict=lv['user_restrict'],date=datetime.datetime.now(),
                                                     CorpusEtudeRef=CorpusEtudeEnCours, CorpusAddRef=lv['CorpusAddRef'],EltRemove=lv['EltRemove'])
                    CorpusCompletRef.save()
                    context = {"nom":lv['nom']}
                    return render(request, 'FinaliseCorpus/CorpusComplet/CorpusAddEtRemoveSuccess.html',context)
            else:
                return render(request, 'FinaliseCorpus/CorpusAdd/EchecAddCorpus.html')
        else:
            return render(request, 'FinaliseCorpus/AbsenceDroit.html')

    # Accès interface
    if request.user.is_superuser:
        form = CorpusCompletForm()
        AllCorpusAddEnCours = CorpusAdd.objects.all()
        context = {"form":form,'AllCorpusAddEnCours':AllCorpusAddEnCours,"reduction":reduction}
        return render(request, 'FinaliseCorpus/CorpusComplet/CorpusAddEtRemoveInterface.html', context)
    else:
        return redirect('FinaliseCorpus:home')


def VisualiseCorpusComplet(request, NomCorpusComplet):
    Test = CorpusComplet.objects.filter(nom=NomCorpusComplet)
    if Test.exists():
        Form = CorpusCompletFormVisuel(instance=Test[0])
        context = {"Ccomplet":Test[0], "Form":Form}
        return render(request, 'FinaliseCorpus/CorpusComplet/VisualiseCorpusComplet.html', context)
    else:
        context = {"NomCorpusCompletNotExsit": NomCorpusComplet}
        return render(request, 'FinaliseCorpus/CorpusComplet/EchecVisualiseCorpusComplet.html', context)


def RemoveCorpusComplet(request):
    if request.method == 'POST':
        if 'Effectuer' in request.POST and request.user.is_superuser:
            nom = request.POST.get('nom')
            CorpusToSuppr = CorpusComplet.objects.get(nom=nom)
            FichierCSVExist = settings.RESULT_PRETRAIT_DIR + "/FinaliseCorpus/CorpusComplet/" + nom + '.csv'
            os.remove(FichierCSVExist)
            CorpusToSuppr.delete()
            context = {"nom": nom}
            return render(request, 'FinaliseCorpus/CorpusComplet/CorpusCompletRemoveSuccess.html', context)

        else:
            return redirect('FinaliseCorpus:home')

    # Accès interface
    if request.user.is_superuser:
        AllCorpusCompletEnCours = CorpusComplet.objects.all()
        context = {"AllCorpusCompletEnCours": AllCorpusCompletEnCours}
        return render(request, 'FinaliseCorpus/CorpusComplet/CorpusCompletRemoveInterface.html', context)
    else:
        return redirect('FinaliseCorpus:home')




#########################  TRAVAIL SUR DICTIONNAIRE POUR LA LEMMATISATION ###################

def ExpressionGeoBrut():
    ''' Travail sur les expressions (préalable à la lemmatisation)
        Récupération de celles déja implémentées dans Iramuteq : surtout mot à trait d'union
        Rajout de celles dans dictionnaires géographie précédemment créés
        Fichier brut car va être complété manuellement pour ajout pluriels'''

    # Recupère les expressions dans dico Iramuteq
    ExpressionBaseDico = settings.DATA_DIR + '/Dico/Finalise/IraExpressionsBase.txt'
    AllExpression = []
    CompteurAll = 0
    CompteurTiret = 0
    with open(ExpressionBaseDico, "r") as f:
        content = f.readlines()
        for elt in content:
            CompteurAll+=1
            eltsplit = elt.split("\t")
            AllExpression.append(eltsplit[0])
            if "-" in eltsplit[0]:
                CompteurTiret+=1

    # Pourcentage de mot à cédille  --> 92 %
    PourcentTiret = CompteurTiret / CompteurAll
    print(PourcentTiret)


    ResultExpressionGeo = settings.DATA_DIR + '/Dico/Finalise/IraExpressionsGeoBrut.txt'
    GeoList = []
    GeoExpression = []
    dicos = ["VergerFin","Brunet","Lacoste","LevyLussault","Geographe","Hypergeo"]
    for dico in dicos:
        with open(settings.DATA_DIR  + "/Dico/Dico" + dico + ".txt") as f:
            for line in f:
                # petite subtilité pour enlever les prefixe dans Brunet
                # ex : retro-
                if line[-2]!='-':
                    # on eleve les apostrope et on splitte
                    for elt in line.replace("'", " ").replace("’", " ").split():
                        if elt.lower() not in GeoList:
                            # on complète les listes
                            GeoList.append(elt.lower())
                            if ("-" in elt) and (elt not in GeoExpression) and (elt not in AllExpression):
                                GeoExpression.append(elt)


    with open(ResultExpressionGeo, "w") as f:
        for elt in GeoExpression:
            f.write(elt + "\n")


def MotGeoBrut():
    '''Travail sur les mots (préalable à la lemmatisation)
        Récupération de ceux déja implémentés dans Iramuteq 
        Rajout de ceux dans dictionnaires géographie précédemment créés
        Fichier brut car va être complété manuellement pour ajout pluriels'''
    # Recupèrer les mots dans dico Iramuteq
    ExpressionBaseDico = settings.DATA_DIR + '/Dico/Finalise/IraMotsBase.txt'
    AllMots = []
    with open(ExpressionBaseDico, "r") as f:
        content = f.readlines()
        for elt in content:
            eltsplit = elt.split("\t")
            AllMots.append(eltsplit[0])

    ### Objectif recupérer mot géo complèter dico mot Iramuteq #######
    ResultMotGeo = settings.DATA_DIR + '/Dico/Finalise/IraMotsGeoBrut.txt'
    GeoList = []
    GeoListComplet = []
    GeoAbbrev = []
    dicos = ["VergerFin", "Brunet", "Lacoste", "LevyLussault", "Geographe", "Hypergeo"]
    for dico in dicos:
        with open(settings.DATA_DIR + "/Dico/Dico" + dico + ".txt") as f:
            for line in f:
                # petite subtilité pour enlever les prefixe dans Brunet
                # ex : retro-
                if dico == "Brunet" and line[-2] != '-':
                    # on eleve les apostrope et on splitte
                    for elt in line.replace("'", " ").replace("’", " ").split():
                        if (elt.lower() not in GeoList) and ("-" not in elt):
                            # on complète les listes
                            GeoList.append(elt.lower())
                            GeoListComplet.append((elt.lower(), dico))
                            # Attention, ne marche que pour les dicos entrés manuellement
                            if elt.isupper():
                                GeoAbbrev.append(elt.lower())

    GeoListFin = []
    for elt in GeoList:
        if elt not in AllMots:
            GeoListFin.append(elt)


    # Va créer un fichier avec pluriel et singulier pré-rempli
    with open(ResultMotGeo, 'a') as f:
        for elt in GeoListFin:
            # provenance pour ne marquer les noms de géographe au pluriel
            provenance = [item for item in GeoListComplet if item[0] == elt]
            # Gestion des pluriels
            if (provenance[0][1] != "Geographe") and (provenance[0][0][-1] != "s") and \
                    (provenance[0][0][-1] != "x") and (provenance[0][0] not in GeoAbbrev) and (
                provenance[0][0][-2:] != "al"):
                f.write(elt + "," + elt + '\n')
                f.write(elt + "s,"+ elt + '\n')
            # rajout al ---> aux, ales, ale
            if (provenance[0][1] != "Geographe") and (provenance[0][0][-2:] == "al") and \
                    (provenance[0][0] not in GeoAbbrev):
                f.write(elt + "," + elt + '\n')
                f.write(elt[:-2] + "ale,"+ elt + '\n')
                f.write(elt[:-2] + "ales," + elt +'\n')
                f.write(elt[:-2] + "aux," + elt + '\n')

            # rajout ien ---> iens, ienne, iennes
            if (provenance[0][1] != "Geographe") and (provenance[0][0][-3:] == "ien") and \
                    (provenance[0][0] not in GeoAbbrev):
                f.write(elt + "," + elt + '\n')
                f.write(elt[:-3] + "iens," + elt + '\n')
                f.write(elt[:-3] + "ienne," + elt + '\n')
                f.write(elt[:-3] + "iennes," + elt + '\n')

            # rajout iel ---> iels, ielle, ielles
            if (provenance[0][1] != "Geographe") and (provenance[0][0][-3:] == "iel") and \
                    (provenance[0][0] not in GeoAbbrev):
                f.write(elt + "," + elt + '\n')
                f.write(elt[:-3] + "iels," + elt + '\n')
                f.write(elt[:-3] + "ielle," + elt + '\n')
                f.write(elt[:-3] + "ielles," + elt + '\n')

            # rajout if ---> ive, ive, ives
            if (provenance[0][1] != "Geographe") and (provenance[0][0][-2:] == "if") and \
                    (provenance[0][0] not in GeoAbbrev):
                f.write(elt + "," + elt + '\n')
                f.write(elt[:-2] + "ifs," + elt + '\n')
                f.write(elt[:-2] + "ive," + elt + '\n')
                f.write(elt[:-2] + "ives," + elt + '\n')

            if provenance[0][1] == "Geographe":
                f.write(elt + "," + elt + '\n')

            if provenance[0][0][-1] == "s":
                f.write(elt + "," + elt + '\n')

            if provenance[0][0][-1] == "x":
                f.write(elt + "," + elt + '\n')

        for elt in GeoAbbrev:
            f.write(elt + "," + elt + '\n')



def CreateDicoExpressionPretrait():
    '''Crée Dico Expression a partir Iramuteq
     + fichier précédemment obtenu nouvelles expressions géo + pluriel (Net)
     + mot composé provenant dictionnaire Prolex (noms propre)s'''
    # Recupère les expressions dans dico Iramuteq
    ExpressionBaseDico = settings.DATA_DIR + '/Dico/Finalise/IraExpressionsBase.txt'
    AllExpression = []
    AllExpressionLem = []
    with open(ExpressionBaseDico, "r") as f:
        content = f.readlines()
        for elt in content:
            eltsplit = elt.split("\t")
            AllExpression.append(eltsplit[0])
            AllExpressionLem.append((eltsplit[0],eltsplit[1]))

    ExpressionGeoDico = settings.DATA_DIR + '/Dico/Finalise/IraExpressionsGeoNet.txt'
    with open(ExpressionGeoDico, "r") as f:
        content = f.readlines()
        for elt in content:
            eltsplit = elt.split(",")
            AllExpression.append(eltsplit[0].replace("-", "_"))
            AllExpressionLem.append((eltsplit[0],eltsplit[1].rstrip().replace("-","_")))

    NomPropreDico = settings.DATA_DIR + "/Dico/DicoProlex.txt"
    with open(NomPropreDico, "r") as f:
        content = f.readlines()
        for elt in content:
            eltnet = elt.rstrip().lower()
            # isdigit pour enlever A_1 etc...
            if ("-" in eltnet) and (eltnet not in AllExpression) and not(eltnet[-1].isdigit()):
                AllExpressionLem.append((eltnet,eltnet.replace("-","_")))

    sorted(AllExpressionLem)

    Result = settings.DATA_DIR + "/Dico/Finalise/IraExpressionsAmelior1.txt"
    with open(Result, 'w') as f:
        for elt1,elt2 in AllExpressionLem:
            f.write(elt1 + "\t" + elt2 + "\n")


def CreateDicoMotPretrait():
    MotBaseDico = settings.DATA_DIR + 'Dico/Finalise/IraMotsBase.txt'
    AllMot = []
    AllMotLem = []
    with open(MotBaseDico, "r") as f:
        content = f.readlines()
        for elt in content:
            eltsplit = elt.split("\t")
            AllMot.append(eltsplit[0])
            AllMotLem.append((eltsplit[0],eltsplit[1]))

    # Ajouter MotGeo sans tiret
    ResultMotGeo = settings.DATA_DIR + '/Dico/Finalise/IraMotsGeoNet.txt'
    with open(ResultMotGeo, "r") as f:
        content = f.readlines()
        for elt in content:
            eltnet = elt.rstrip()
            eltsplit = eltnet.split(",")
            AllMot.append(eltsplit[0])
            AllMotLem.append((eltsplit[0], eltsplit[1]))

    # Ajouter NomPropre sans tiret
    NomPropreDico = settings.DATA_DIR + "/Dico/DicoProlex.txt"
    with open(NomPropreDico, "r") as f:
        content = f.readlines()
        for elt in content:
            eltnet = elt.rstrip().lower()
            # isdigit pour enlever A_1 etc...
            if ("-" not in eltnet) and (eltnet not in AllMot) and not (eltnet[-1].isdigit()):
                AllMot.append(eltnet)
                AllMotLem.append((eltnet, eltnet))

    # Ajouter Expression
    ResultExpressionGeo = settings.DATA_DIR + "/Dico/Finalise/IraExpressionsAmelior1.txt"
    with open(ResultExpressionGeo, "r") as f:
        content = f.readlines()
        for elt in content:
            eltnet = elt.rstrip()
            eltsplit = eltnet.split("\t")
            if  eltsplit[1] not in AllMot:
                AllMotLem.append((eltsplit[1], eltsplit[1]))

    sorted(AllMotLem)

    Result = settings.DATA_DIR + "/Dico/Finalise/IraMotsAmelior1.txt"
    with open(Result, 'w') as f:
        for elt1, elt2 in AllMotLem:
            f.write(elt1 + "\t" + elt2 + "\n")



############################ ADAPTE A PARTIR TRAITEMENT IRAMUTEQ ############################

def dolower(txt):
    return txt.lower()

def firstclean(txt):
    txt = txt.replace('’', "'")
    txt = txt.replace('œ', 'oe')
    return txt.replace('...', ' ').replace('?', ' ? ').replace('.', ' . ').replace('!', ' ! ').replace(',', ' , ').replace(';', ' ; ').replace(':', ' : ').replace('…', ' ')

def docharact(txt):
    rule = "[^a-zA-Z0-9àÀâÂäÄáÁéÉèÈêÊëËìÌîÎïÏòÒôÔöÖùÙûÛüÜçÇßœŒ’ñ.:,;!?*'_-]"
    return re.sub(rule, ' ', txt)


def make_expression(txt,expressions):
    for expression in expressions:
        if expression[0] in txt:
            txt = txt.replace(expression[0], expression[1])
    return txt

def do_apos_et_tiret(txt):
    return txt.replace('\'', ' ').replace('-', ' ')


def buildcleans(text,expressions):
    textlower = dolower(text)
    textfirstclean = firstclean(textlower)
    textnettoiecaract = docharact(textfirstclean)
    textexpression = make_expression(textnettoiecaract,expressions)
    TextTransform = do_apos_et_tiret(textexpression)
    return TextTransform


###################################  DICO ET FORMES NON RECONNUES ########################

def AddDicoMotLemme(request):
    if request.method == 'POST':
        if ('Effectuer' in request.POST) and request.user.is_superuser:
            formToSave = DicoMotLemmeForm(data=request.POST)
            # si le formulaire est valide
            if formToSave.is_valid():
                # sauve les donneés dans la bd
                lv = formToSave.save()
                nomdico = lv.nom
                context = {"nomdico": nomdico}
                return render(request, 'FinaliseCorpus/Dico/AddMotLemmeSuccess.html', context)
            else:
                return render(request, 'FinaliseCorpus/Dico/AddMotLemmeFail.html')
        elif 'Retour' in request.POST:
            return redirect('FinaliseCorpus:home')
        else:
            return render(request, 'FinaliseCorpus/Dico/AddMotLemmeFail.html')
    form = DicoMotLemmeForm()
    context = {"form": form}
    return render(request, 'FinaliseCorpus/Dico/AddMotLemmeInterface.html', context)


def AddDicoMotExpression(request):
    if request.method == 'POST':
        if ('Effectuer' in request.POST) and request.user.is_superuser:
            formToSave = DicoExpressionForm(data=request.POST)
            # si le formulaire est valide
            if formToSave.is_valid():
                # sauve les donneés dans la bd
                lv = formToSave.save()
                nomdico = lv.nom
                context = {"nomdico": nomdico}
                return render(request, 'FinaliseCorpus/Dico/AddExpressionSuccess.html', context)
            else:
                return render(request, 'FinaliseCorpus/Dico/AddExpressionFail.html')
        elif 'Retour' in request.POST:
            return redirect('FinaliseCorpus:home')
        else:
            return render(request, 'FinaliseCorpus/Dico/AddExpressionFail.html')
    form = DicoExpressionForm()
    context = {"form": form}
    return render(request, 'FinaliseCorpus/Dico/AddExpressionInterface.html', context)


def RemoveDicoMotLemme(request):
    if request.method == 'POST':
        if ('Effectuer' in request.POST) and request.user.is_superuser:
            nomdico = request.POST.get('nom')
            DicoAEffacer = DicoMotLemme.objects.filter(nom=nomdico)
            DicoAEffacer.delete()
            context = {"nomdico": nomdico}
            return render(request, 'FinaliseCorpus/Dico/RemoveMotLemmeSuccess.html', context)
        elif 'Retour' in request.POST:
            return redirect('FinaliseCorpus:home')
        else:
            return render(request, 'FinaliseCorpus/Dico/RemoveMotLemmeFail.html')
    AllDicoMotLemme = DicoMotLemme.objects.all()
    context = {"AllDicoMotLemme": AllDicoMotLemme}
    return render(request, 'FinaliseCorpus/Dico/RemoveMotLemmeInterface.html', context)


def RemoveDicoExpression(request):
    if request.method == 'POST':
        if ('Effectuer' in request.POST) and request.user.is_superuser:
            nomdico = request.POST.get('nom')
            DicoAEffacer = DicoExpression.objects.filter(nom=nomdico)
            DicoAEffacer.delete()
            context = {"nomdico": nomdico}
            return render(request, 'FinaliseCorpus/Dico/RemoveExpressionSuccess.html', context)
        elif 'Retour' in request.POST:
            return redirect('FinaliseCorpus:home')
        else:
            return render(request, 'FinaliseCorpus/Dico/RemoveExpressionFail.html')
    AllDicoExpression = DicoExpression.objects.all()
    context = {"AllDicoExpression": AllDicoExpression}
    return render(request, 'FinaliseCorpus/Dico/RemoveExpressionInterface.html', context)


def FNROrderInterface(request):
    '''FNR : Formes Non Reconnues supérieures à 2 lettres'''

    if request.method == 'POST':

        if ('Effectuer' in request.POST) and request.user.is_superuser:

            formToSave = FNRRequestForm(data=request.POST)
            # si le formulaire est valide
            if formToSave.is_valid():
                # sauve les donneés dans la bd
                lv = formToSave.clean()

                CorpusComplet = lv['CorpusCompletRef'].nom
                DicoMot = lv['DicoMotLemmeRef'].nom
                DicoExpression = lv['DicoExpressionRef'].nom
                CorpusCompletId = str(lv['CorpusCompletRef'].id)
                DicoMotId = str(lv['DicoMotLemmeRef'].id)
                DicoExpressionId = str(lv['DicoExpressionRef'].id)

                Result = settings.RESULT_PRETRAIT_DIR +  "/FinaliseCorpus/FNR/" + CorpusCompletId + "_" + DicoMotId + "_" + DicoExpressionId +".txt"

                # Faire verif dico

                if not os.path.isfile(Result):
                    # creer un dico par deux premières lettres
                    # accèlère grandement les recherche par la suite
                    DicoIraPickleMot = settings.DATA_DIR + '/Dico/Finalise/' + DicoMot
                    # s'il n'exite pas déjà
                    if not os.path.isfile(DicoIraPickleMot):
                        ResultPrecedent = settings.DATA_DIR + '/Dico/Finalise/' + DicoMot + '.txt'
                        with open(ResultPrecedent) as f:
                            content = f.readlines()
                        DicoMotParDeuxPremieresLettres = {}
                        for line in content:
                            eltsplit =line.rstrip().split("\t")
                            if len(eltsplit[0])>=2:
                                if eltsplit[0][0:2] not in DicoMotParDeuxPremieresLettres.keys():
                                    DicoMotParDeuxPremieresLettres[eltsplit[0][0:2]] = []
                                    DicoMotParDeuxPremieresLettres[eltsplit[0][0:2]].append(eltsplit[0])
                                else:
                                    DicoMotParDeuxPremieresLettres[eltsplit[0][0:2]].append(eltsplit[0])

                        outfile1 = open(DicoIraPickleMot, 'wb')
                        pickle.dump(DicoMotParDeuxPremieresLettres, outfile1)
                        outfile1.close()
                    # sinon le charge directement
                    else:
                        infile1 = open(DicoIraPickleMot, 'rb')
                        DicoMotParDeuxPremieresLettres = pickle.load(infile1)
                        infile1.close()

                    FNR = []
                    csv.field_size_limit(sys.maxsize)
                    FichierCorpus = settings.RESULT_PRETRAIT_DIR +  "/FinaliseCorpus/CorpusComplet/"+ CorpusComplet + ".csv"
                    dicomotkey = DicoMotParDeuxPremieresLettres.keys()

                    FichierExpression = settings.DATA_DIR + '/Dico/Finalise/' + DicoExpression + '.txt'
                    with open(FichierExpression) as f:
                        content = f.readlines()
                    ExpressionsList = []
                    for line in content:
                        eltsplit = line.rstrip().split("\t")
                        ExpressionsList.append((eltsplit[0],eltsplit[1]))

                    with open(FichierCorpus, 'r') as f:
                        reader = csv.reader(f, delimiter='\t')
                        next(reader)
                        for row in reader:
                            txtencours = row[7]
                            txtclean = buildcleans(txtencours, ExpressionsList)
                            for mot in txtclean.split():
                                if (len(mot) >= 2) and (mot[0:2] in dicomotkey) and (mot not in DicoMotParDeuxPremieresLettres[mot[0:2]]):
                                    FNR.append(mot)

                    FNROrder = Counter(FNR).most_common()

                    # Creé dossier
                    DossierResult = Result.rsplit('/',1)[0]
                    if not os.path.exists(DossierResult):
                        os.makedirs(DossierResult)

                    with open(Result, 'w') as f:
                        for i,fnr in enumerate(FNROrder):
                            if i < 10000:
                                f.write(fnr[0] + "\t" + str(fnr[1]) + "\n")

                return redirect('FinaliseCorpus:FNROrderResult',CorpusCompletId,DicoMotId,DicoExpressionId)

            else :
                return render(request, 'FinaliseCorpus/FNR/FNROrderFail.html')
        else:
            return render(request, 'FinaliseCorpus/FNR/FNROrderFail.html')

    ####### Interface ###########

    form = FNRRequestForm()
    context = {"form": form}
    return render(request, 'FinaliseCorpus/FNR/FNROrderInterface.html', context)



def FNROrderResult(request,id_corpus,id_dicomot,id_dicoexpression):
    MarqueurCorpus = False
    MarquerDicoMot = False
    MarqueurDicoExpression = False
    TestCorpus = CorpusComplet.objects.filter(id=int(id_corpus))
    if TestCorpus.exists():
        MarqueurCorpus = True
    TestDicoMot = DicoMotLemme.objects.filter(id=int(id_dicomot))
    if TestDicoMot.exists():
        MarquerDicoMot = True
    TestDicoExpression = DicoExpression.objects.filter(id=int(id_dicoexpression))
    if TestDicoExpression.exists():
        MarqueurDicoExpression = True

    if MarqueurCorpus and MarquerDicoMot and MarqueurDicoExpression:
        FichierResult = settings.RESULT_PRETRAIT_DIR +  "/FinaliseCorpus/FNR/" + id_corpus + "_" + id_dicomot + "_" + id_dicoexpression +".txt"
        ResultFNR = []
        ResultFreq = []
        if os.path.isfile(FichierResult):
            with open(FichierResult, 'r') as f:
                content = f.readlines()
                for line in content:
                    LineSplit = line.rstrip().split("\t")
                    ResultFNR.append(LineSplit[0])
                    ResultFreq.append(LineSplit[1])
            Result = zip(ResultFNR,ResultFreq)
            context = {"Result":Result}
            return render(request, 'FinaliseCorpus/FNR/FNROrderResult.html', context)
        else:
            return render(request, 'FinaliseCorpus/FNR/FNROrderFail.html')


    else:
        return render(request, 'FinaliseCorpus/FNR/FNROrderFail.html')


##################################### DICO 2 et Corpusfin ###############################


def CreateDicoMotPretrait2(request):
    MotBaseDico = settings.DATA_DIR + '/Dico/Finalise/IraMotsBase.txt'
    AllMot = []
    AllMotRetenu = []
    AllMotLemRetenu = []
    with open(MotBaseDico, "r") as f:
        content = f.readlines()
        for elt in content:
            eltsplit = elt.split("\t")
            # 1ère DIFFERENCE AVEC DICO 1 : ici tri nom, verb, adj, adv en ampont
            if eltsplit[2] == "nom" or eltsplit[2] == "nom_sup" or eltsplit[2] == "ver" or eltsplit[2] == "ver_sup" \
                    or eltsplit[2] == "adj" or eltsplit[2] == "adj_sup" or eltsplit[2] == "adj_ind"\
                    or eltsplit[2] == "adv"  or eltsplit[2] == "adv_sup":
                AllMotRetenu.append(eltsplit[0])
                AllMotLemRetenu.append((eltsplit[0], eltsplit[1]))
            AllMot.append(eltsplit[0])

    # Ajouter MotGeo sans tiret
    ResultMotGeo = settings.DATA_DIR + '/Dico/Finalise/IraMotsGeoNet.txt'
    with open(ResultMotGeo, "r") as f:
        content = f.readlines()
        for elt in content:
            eltnet = elt.rstrip()
            eltsplit = eltnet.split(",")
            AllMotRetenu.append(eltsplit[0])
            AllMotLemRetenu.append((eltsplit[0], eltsplit[1]))

    # Ajouter NomPropre sans tiret
    NomPropreDico = settings.DATA_DIR + "/Dico/DicoProlex.txt"
    with open(NomPropreDico, "r") as f:
        content = f.readlines()
        for elt in content:
            eltnet = elt.rstrip().lower()
            # isdigit pour enlever A_1 etc...
            # on filtre sur allmots car sinon on peut rajouter des formes exclues précédemment
            if ("-" not in eltnet) and (eltnet not in AllMot) and not (eltnet[-1].isdigit()):
                AllMotRetenu.append(eltnet)
                AllMotLemRetenu.append((eltnet, eltnet))

    # Ajouter Expression (avec nouveau fichier IraExpressionsAmelior2 (prise en compte FNR)
    ResultExpressionGeo = settings.DATA_DIR + "/Dico/Finalise/IraExpressionsAmelior2.txt"
    with open(ResultExpressionGeo, "r") as f:
        content = f.readlines()
        for elt in content:
            eltnet = elt.rstrip()
            eltsplit = eltnet.split("\t")
            if eltsplit[1] not in AllMot:
                AllMotRetenu.append(eltsplit[1])
                AllMotLemRetenu.append((eltsplit[1], eltsplit[1]))

    # 2ème DIFFERENCE AVEC DICO 1 : ON AJOUTE LE TRAVAIL REALISE A PARTIR FORME NON RECONNUE
    FNRMot1 = settings.DATA_DIR + "/Dico/Finalise/FNRMotExtract1.txt"
    with open(FNRMot1 , "r") as f:
        content = f.readlines()
        for elt in content:
            eltnet = elt.rstrip()
            eltsplit = eltnet.split("\t")
            if eltsplit[0] not in AllMot:
                AllMotLemRetenu.append((eltsplit[0], eltsplit[1]))

    sorted(AllMotLemRetenu)

    Result = settings.DATA_DIR + "/Dico/Finalise/IraMotsAmelior2.txt"
    with open(Result, 'w') as f:
        for elt1, elt2 in AllMotLemRetenu:
            f.write(elt1 + "\t" + elt2 + "\n")

    return render(request, 'FinaliseCorpus/SuccessDicoMotLemme2.html')




    ###################### PREPA CORPUS FIN ################

        ############### BUILDCLEAN2 ##################

def AddDicoSuffixe(request):
    if request.method == 'POST':
        if ('Effectuer' in request.POST) and request.user.is_superuser:
            formToSave =  DicoSuffixeForm(data=request.POST)
            # si le formulaire est valide
            if formToSave.is_valid():
                # sauve les donneés dans la bd
                lv = formToSave.save()
                nomdico = lv.nom
                context = {"nomdico": nomdico}
                return render(request, 'FinaliseCorpus/Dico/AddSuffixeSuccess.html', context)
            else:
                return render(request, 'FinaliseCorpus/Dico/AddSuffixeFail.html')
        elif 'Retour' in request.POST:
            return redirect('FinaliseCorpus:home')
        else:
            return render(request, 'FinaliseCorpus/Dico/AddSuffixeFail.html')
    form = DicoSuffixeForm()
    context = {"form": form}
    return render(request, 'FinaliseCorpus/Dico/AddSuffixeInterface.html', context)



def RemoveDicoSuffixe(request):
    if request.method == 'POST':
        if ('Effectuer' in request.POST) and request.user.is_superuser:
            nomdico = request.POST.get('nom')
            DicoAEffacer = DicoSuffixe.objects.filter(nom=nomdico)
            DicoAEffacer.delete()
            context = {"nomdico": nomdico}
            return render(request, 'FinaliseCorpus/Dico/RemoveSuffixeSuccess.html', context)
        elif 'Retour' in request.POST:
            return redirect('FinaliseCorpus:home')
        else:
            return render(request, 'FinaliseCorpus/Dico/RemoveSuffixeFail.html')
    AllDicoSuffixe = DicoSuffixe.objects.all()
    context = {"AllDicoSuffixe": AllDicoSuffixe}
    return render(request, 'FinaliseCorpus/Dico/RemoveSuffixeInterface.html', context)


def suffixe_clean(txt,suffixes):
    for suffixe in suffixes:
        EspacePlusSuffixe = " " +  suffixe[0] + " "
        if EspacePlusSuffixe  in txt:
            txt = txt.replace(EspacePlusSuffixe, suffixe[1] + " ")
    return txt

def buildcleans2(text,expressions,suffixes):
    textlower = dolower(text)
    textfirstclean = firstclean(textlower)
    textnettoiecaract = docharact(textfirstclean)
    textsuffixeclean = suffixe_clean(textnettoiecaract,suffixes)
    textexpression = make_expression(textsuffixeclean,expressions)
    TextTransform = do_apos_et_tiret(textexpression)
    return TextTransform

    ############ PREPA  LEMMATISATION ##################

def RepereInfDeux():
    ''' Cette fonction permet de justifier un petit tri au niveau des mots de deux caractères
        car le dictionnaire des noms propres Prolex ajoute un certain bruit à ce niveau '''
    base = settings.DATA_DIR + "/Dico/Finalise/IraMotsAmelior2"
    with open(base, "r") as f:
        content = f.readlines()
        for i,elt in enumerate(content):
            eltsplit= elt.rstrip().split("\t")
            if len(eltsplit[0])<3:
                print(eltsplit[0])
                print(i)
    # Liste retenue nom ou adj ou abréviation :
    #an,ai,dé,dû,lu,fa,mi,mû,nu,os,pc,ph,va,vu,se,bû,pô,ex,as,or,ue


# En plus, j'ai enlevé quelques articles à la main : les, des, une
# et conjonctions : qui, que, car
# verbe : est --> être, sont --> être
# qui viennent aussi à priori d'un certain bruit lié au découpage de prolex en unité


def DicoMotPicke(dicomot):

    DicoIraPickleMot = settings.DATA_DIR + '/Dico/Finalise/' + dicomot + "PickleM"
    DicoIraPickleLemme = settings.DATA_DIR + '/Dico/Finalise/' + dicomot + "PickleL"
    # s'il n'exite pas déjà
    if not os.path.isfile(DicoIraPickleMot):
        ResultPrecedent = settings.DATA_DIR + "/Dico/Finalise/" + dicomot + ".txt"
        # voir fonction RepereInfDeux()
        # Attention, cette partie est spécifique à ma recherche, mériterait d'être arrangée
        # pour monter en généralité et ouverture à d'autres utilisateurs
        Liste2lettres = ['an', 'ai', 'dé', 'dû', 'lu', 'mi', 'mû', 'nu', 'os', 'pc', 'ph', 'ru', 'va', 'vu',
                         'se', 'bû', 'pô', 'ex', 'as', 'or', 'ue']
        with open(ResultPrecedent) as f:
            content = f.readlines()
        DicoMotParDeuxPremieresLettres = {}
        DicoLemmeParDeuxPremieresLettres = {}
        for line in content:
            eltsplit = line.rstrip().split("\t")
            if len(eltsplit[0]) == 2:
                if eltsplit[0] in Liste2lettres:
                    if eltsplit[0][0:2] not in DicoMotParDeuxPremieresLettres.keys():
                        DicoMotParDeuxPremieresLettres[eltsplit[0][0:2]] = []
                        DicoMotParDeuxPremieresLettres[eltsplit[0][0:2]].append(eltsplit[0])
                        DicoLemmeParDeuxPremieresLettres[eltsplit[0][0:2]] = []
                        DicoLemmeParDeuxPremieresLettres[eltsplit[0][0:2]].append(eltsplit[1])
                    else:
                        DicoMotParDeuxPremieresLettres[eltsplit[0][0:2]].append(eltsplit[0])
                        DicoLemmeParDeuxPremieresLettres[eltsplit[0][0:2]].append(eltsplit[1])

            if len(eltsplit[0]) > 2:
                if eltsplit[0][0:2] not in DicoMotParDeuxPremieresLettres.keys():
                    DicoMotParDeuxPremieresLettres[eltsplit[0][0:2]] = []
                    DicoMotParDeuxPremieresLettres[eltsplit[0][0:2]].append(eltsplit[0])
                    DicoLemmeParDeuxPremieresLettres[eltsplit[0][0:2]] = []
                    DicoLemmeParDeuxPremieresLettres[eltsplit[0][0:2]].append(eltsplit[1])
                else:
                    DicoMotParDeuxPremieresLettres[eltsplit[0][0:2]].append(eltsplit[0])
                    DicoLemmeParDeuxPremieresLettres[eltsplit[0][0:2]].append(eltsplit[1])

        outfile1 = open(DicoIraPickleMot, 'wb')
        outfile2 = open(DicoIraPickleLemme, 'wb')
        pickle.dump(DicoMotParDeuxPremieresLettres, outfile1)
        pickle.dump(DicoLemmeParDeuxPremieresLettres, outfile2)
        outfile1.close()
        outfile2.close()
    # sinon le chage directement
    else:
        infile1 = open(DicoIraPickleMot, 'rb')
        DicoMotParDeuxPremieresLettres = pickle.load(infile1)
        infile1.close()
        infile2 = open(DicoIraPickleLemme, 'rb')
        DicoLemmeParDeuxPremieresLettres = pickle.load(infile2)
        infile2.close()
    return DicoMotParDeuxPremieresLettres, DicoLemmeParDeuxPremieresLettres



def CorpusFinAdd(request):

    if request.method == 'POST':

        if ('Effectuer' in request.POST) and request.user.is_superuser:

            formToSave = CorpusFinForm(data=request.POST)
            # si le formulaire est valide
            if formToSave.is_valid():
                choix = formToSave.cleaned_data
                FichierResult = settings.RESULT_PRETRAIT_DIR + "/FinaliseCorpus/CorpusFin/" + choix['nom'] + ".csv"

                # Creé dossier
                DossierResult = FichierResult.rsplit('/', 1)[0]
                if not os.path.exists(DossierResult):
                    os.makedirs(DossierResult)

                if not choix['PretraitIraBase'] and not choix['Lemmatisation']:
                    src = settings.RESULT_PRETRAIT_DIR + "/FinaliseCorpus/CorpusComplet/" + choix['CorpusCompletRef'].nom + ".csv"
                    # Copie simple
                    shutil.copyfile(src, FichierResult)

                if choix['Lemmatisation']:
                    DicoM,DicoL = DicoMotPicke(choix['DicoMotLemmeRef'].nom)
                    dicomotkey = DicoM.keys()

                if choix['PretraitIraBase']:
                    FichierCorpus = settings.RESULT_PRETRAIT_DIR + "/FinaliseCorpus/CorpusComplet/" + choix['CorpusCompletRef'].nom + ".csv"
                    FichierExpression = settings.DATA_DIR + '/Dico/Finalise/' + choix['DicoExpressionRef'].nom + '.txt'
                    FichierSuffixe = settings.DATA_DIR + '/Dico/Finalise/' + choix['DicoSuffixeRef'].nom + '.txt'

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

                    with open(FichierResult, 'a', newline='') as fresult:
                        writer = csv.writer(fresult, delimiter='\t')
                        writer.writerow(
                            ["Id", "NomPersee", "Revue", "Date", "Type", "Titre", "Auteur", "Text"])

                        with open(FichierCorpus, 'r') as f:
                            reader = csv.reader(f, delimiter='\t')
                            next(reader)
                            for row in reader:
                                txtencours = row[7]
                                txtclean = buildcleans2(txtencours, ExpressionsList, SuffixesList)

                                if choix['Lemmatisation']:

                                    newtext = []

                                    for mot in txtclean.split():
                                        if (len(mot) >= 2) and (mot[0:2] in dicomotkey) and (mot in DicoM[mot[0:2]]):
                                            # Aller chercher lemme même index !!
                                            lem = DicoL[mot[0:2]][DicoM[mot[0:2]].index(mot)]
                                            newtext.append(lem)

                                    writer.writerow([row[0], row[1], row[2], row[3], row[4], row[5], row[6], " ".join(newtext)])

                                else:
                                    writer.writerow(
                                        [row[0], row[1], row[2], row[3], row[4], row[5], row[6], txtclean])

                if not choix['PretraitIraBase'] and choix['Lemmatisation']:
                    FichierCorpus = settings.RESULT_PRETRAIT_DIR + "/FinaliseCorpus/CorpusComplet/" + choix['CorpusCompletRef'].nom + ".csv"

                    csv.field_size_limit(sys.maxsize)

                    with open(FichierResult, 'a', newline='') as fresult:
                        writer = csv.writer(fresult, delimiter='\t')
                        writer.writerow(
                            ["Id", "NomPersee", "Revue", "Date", "Type", "Titre", "Auteur", "Text"])

                        with open(FichierCorpus, 'r') as f:
                            reader = csv.reader(f, delimiter='\t')
                            next(reader)
                            for row in reader:
                                txtencours = row[7]

                                newtext = []
                                # par rapport à précédent cas, change à ce niveau txtclean --> txtencours
                                for mot in txtencours.split():
                                    if (len(mot) >= 2) and (mot[0:2] in dicomotkey) and (
                                        mot in DicoM[mot[0:2]]):
                                        # Aller chercher lemme même index !!
                                        lem = DicoL[mot[0:2]][DicoM[mot[0:2]].index(mot)]
                                        newtext.append(lem)

                                writer.writerow(
                                    [row[0], row[1], row[2], row[3], row[4], row[5], row[6], " ".join(newtext)])

                # SAUVER DANS BASE DE DONNEE
                formToSave.save()
                context = {"NewCorpusFin": choix['nom']}
                return render(request, 'FinaliseCorpus/CorpusFin/NewCorpusSuccess.html', context)

            else:
                return render(request, 'FinaliseCorpus/CorpusFin/NewCorpusFail.html')
        else:
            return render(request, 'FinaliseCorpus/CorpusFin/NewCorpusFail.html')


    form = CorpusFinForm()
    context = {"form":form}
    return render(request, 'FinaliseCorpus/CorpusFin/NewCorpusFin.html', context)


def CorpusFinVisualise(request, corpusfin):
    CorpusFinToVisualise = CorpusFin.objects.filter(nom=corpusfin)
    if CorpusFinToVisualise.exists():
        FormCorpusFinToVisualise = CorpusFinFormVisuel(instance=CorpusFinToVisualise[0])
        context = {"CorpusFinToVisualise": CorpusFinToVisualise,"FormCorpusFinToVisualise":FormCorpusFinToVisualise}
        return render(request, 'FinaliseCorpus/CorpusFin/VisualiseCorpusFin.html', context)
    else:
        return render(request, 'FinaliseCorpus/CorpusFin/VisualiseCorpusFinFail.html')

def CorpusFinRemoveInterface(request):

    if request.method == 'POST':

        if ('Supprimer' in request.POST) and request.user.is_superuser:
            nom = request.POST.get('cfin')
            CorpusToRemove = CorpusFin.objects.filter(nom=nom)
            if CorpusToRemove.exists():
                CorpusToRemove.delete()
                FichierToRemove = settings.RESULT_PRETRAIT_DIR + "/FinaliseCorpus/CorpusFin/" + nom + ".csv"
                os.remove(FichierToRemove)
                context = {"CorpusFinRemoveSuccess": nom}
                return render(request, 'FinaliseCorpus/CorpusFin/CorpusFinRemoveSuccess.html', context)
            else:
                return render(request, 'FinaliseCorpus/CorpusFin/CorpusFinRemoveFail.html')
        else :
            return render(request, 'FinaliseCorpus/CorpusFin/CorpusFinRemoveFail.html')


    AllCorpusFin = CorpusFin.objects.all()
    context = {"AllCorpusFin": AllCorpusFin}
    return render(request, 'FinaliseCorpus/CorpusFin/CorpusFinRemoveInterface.html', context)


def DownloadDico(request, fichier):
    '''Pour telecharger un fichier de dico'''
    FichierResult = settings.DATA_DIR + "/Dico/Finalise/"+ fichier + '.txt'
    response = HttpResponse(open(FichierResult, 'rb').read())
    response['Content-Type'] = 'text/plain'
    response['Content-Disposition'] = 'attachment; filename=' + fichier + '.txt'
    return response







