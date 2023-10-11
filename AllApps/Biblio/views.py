from django.shortcuts import render, redirect
from django.conf import settings
from collections import OrderedDict
import os, csv


def home(request):
    return redirect("Biblio:ViewBiblioInterface", 0)


def LangDicoAll():
    MyDicoLang = {0:"Toutes",
                  1:"Français",
                  2:"Anglais"}
    return MyDicoLang

def CollectionDicoAll():
    MyCollectionDico = {0:"Toutes",
                  1:"Géographie",
                  2:"Autres sciences sociales",
                  3:"Philosophie et épistémologie",
                  4:"Humanités Numériques et données massives",
                  5:"Sémantique et Traitement Automatique du Langage"}
    return MyCollectionDico



def ViewBiblioAll(request,CollectId, LangId):
    """Ici, permet de voir les biblios stockées précédemment
    avec des boutons pour chander la collection et la langue"""
    DicoLang = LangDicoAll()
    DicoCollection = CollectionDicoAll()

    if CollectId not in DicoCollection.keys():
        return render(request, 'general/home.html')
    if LangId not in DicoLang.keys():
        return render(request,'general/home.html')

    PathFile = os.path.join(settings.BASE_DIR, "AllApps","Biblio", "ResultAll",
                            str(CollectId) + str(LangId) + ".txt")

    file_exist = os.path.exists(PathFile)
    if not file_exist:
        return render(request, 'general/home.html')

    else:
        with open(PathFile, "r") as f:
            Result= f.readlines()


    # Un peu compliqué mais sinon je n'arrivais pas à afficher les liens url avec  | safe
    # Astuce : décomposer puis reconstruire la structure dans le HTML

    ListeSourceWebPresence = []
    ListeSouceSourceWebContenu = []
    ListeLienInterfacePresence = []
    ListeLienInterfaceContenu = []
    ListePresenceItal = []
    ListeContenuItal = []
    ListeDeb = []
    ListeFin = []
    ListePossibleNewRef = []
    MultiRefPresence = []
    MultiRefVar1 = []


    for elt in Result:
        if "<i>" in elt:
            ListePresenceItal.append(True)
            eltital = elt.split('<i>', 1)[1].split("</i>", 1)[0]
            ListeContenuItal.append(eltital)
            eltdeb = elt.split(">", 1)[1].split("<i>", 1)[0]
            ListeDeb.append(eltdeb)
            eltfin = elt.split("</i>", 1)[1].split("<a href=", 1)[0]
            ListeFin.append(eltfin)
        else:
            ListePresenceItal.append(False)
            ListeContenuItal.append("")
            eltdeb = elt.split(">", 1)[1].split("<a href=", 1)[0]
            ListeDeb.append(eltdeb)
            ListeFin.append("")

        if "Vers source Web" in elt:
            eltweb = elt.split('<a href="http', 1)[1].split('">', 1)[0]
            ListeSourceWebPresence.append(True)
            ListeSouceSourceWebContenu.append('http' + eltweb)
        else:
            ListeSourceWebPresence.append(False)
            ListeSouceSourceWebContenu.append("")

        if "Vers Texte interface" in elt:

            eltint = elt.split('<a href="{% url \'', 1)[1].split("' %}", 1)[0]
            ListeLienInterfacePresence.append(True)

            if "ViewMultiRef" in eltint:
                ListeLienInterfaceContenu.append("Biblio:ViewMultiRef")
                MultiRefPresence.append(True)
                PresenceVar1 = elt.split("Biblio:ViewMultiRef' ")[1][0]
                MultiRefVar1.append(int(PresenceVar1))
                ListePossibleNewRef.append("")
            else:
                ListeLienInterfaceContenu.append(eltint)
                MultiRefPresence.append(False)
                PossibleNewRef = elt.split("\' %}#", 1)[1].split('">', 1)[0]
                ListePossibleNewRef.append(PossibleNewRef)
                MultiRefVar1.append(None)

        else:
            ListeLienInterfacePresence.append(False)
            ListeLienInterfaceContenu.append("")
            MultiRefPresence.append(False)
            ListePossibleNewRef.append(None)
            MultiRefVar1.append(None)

    ResultTest = zip(ListeDeb, ListePresenceItal, ListeContenuItal, ListeFin, ListeSourceWebPresence,
                     ListeSouceSourceWebContenu, ListeLienInterfaceContenu, ListePossibleNewRef, MultiRefPresence,
                     MultiRefVar1,ListeLienInterfacePresence)
    CollectNameIdChoices = zip(list(DicoCollection.values()),list(DicoCollection.keys()))
    LangNameIdChoices = zip(list(DicoLang.values()), list(DicoLang.keys()))
    context = {"ResultTest": ResultTest, "CollectNameIdChoices":CollectNameIdChoices,"LangNameIdChoices":LangNameIdChoices,
               "CollectIdSelect":CollectId, "LangIdSelect":LangId}
    return render(request, 'Biblio/ViewBiblioAll.html', context)



def ViewBiblioInterface(request,CollectId):
    """Ici, permet de voir les biblios stockées précédemment
    avec des boutons pour changer la collection et la langue"""
    DicoCollection = CollectionDicoAll()

    if CollectId not in DicoCollection.keys():
        return render(request, 'general/home.html')


    PathFile = os.path.join(settings.BASE_DIR, "AllApps","Biblio", "ResultInterface",
                            str(CollectId) + "0red.txt")

    file_exist = os.path.exists(PathFile)
    if not file_exist:
        return render(request, 'general/home.html')
    else:
        with open(PathFile, "r") as f:
            Result= f.readlines()


    # Un peu compliqué mais sinon je n'arrivais pas à afficher les liens url avec  | safe
    # Astuce : décomposer puis reconstruire la structure dans le HTML
    ListeSourceWebPresence = []
    ListeSouceSourceWebContenu = []
    ListeLienInterfaceContenu = []
    ListePresenceItal = []
    ListeContenuItal = []
    ListeDeb = []
    ListeFin = []
    LidId = []
    ListePossibleNewRef = []
    MultiRefPresence = []
    MultiRefVar1 = []


    for elt in Result:
        eltid = elt.split('id="', 1)[1].split('">', 1)[0]
        LidId.append(eltid)
        if "<i>" in elt :
            ListePresenceItal.append(True)
            eltital = elt.split('<i>', 1)[1].split("</i>", 1)[0]
            ListeContenuItal.append(eltital)
            eltdeb = elt.split(">",1)[1].split("<i>", 1)[0]
            ListeDeb.append(eltdeb)
            eltfin = elt.split("</i>",1)[1].split("<a href=", 1)[0]
            ListeFin.append(eltfin)
        else:
            ListePresenceItal.append(False)
            ListeContenuItal.append("")
            eltdeb = elt.split(">",1)[1].split("<a href=", 1)[0]
            ListeDeb.append(eltdeb)
            ListeFin.append("")

        if "Vers source Web" in elt:
            eltweb = elt.split('<a href="http',1)[1].split('">', 1)[0]
            ListeSourceWebPresence.append(True)
            ListeSouceSourceWebContenu.append('http' + eltweb)
        else:
            ListeSourceWebPresence.append(False)
            ListeSouceSourceWebContenu.append("")

        eltint = elt.split('<a href="{% url \'',1)[1].split("' %}", 1)[0]


        if "ViewMultiRef" in eltint:
            ListeLienInterfaceContenu.append('Biblio:ViewMultiRef')
            MultiRefPresence.append(True)
            PresenceVar1 = elt.split("Biblio:ViewMultiRef' ")[1][0]
            MultiRefVar1.append(int(PresenceVar1))
            ListePossibleNewRef.append("")
        else:
            ListeLienInterfaceContenu.append(eltint)
            MultiRefPresence.append(False)
            PossibleNewRef = elt.split("\' %}#", 1)[1].split('">', 1)[0]
            ListePossibleNewRef.append(PossibleNewRef)
            MultiRefVar1.append(None)


    print(ListeLienInterfaceContenu)
    ResultTest = zip(LidId,ListeDeb,ListePresenceItal,ListeContenuItal,ListeFin,ListeSourceWebPresence,
                     ListeSouceSourceWebContenu,ListeLienInterfaceContenu,ListePossibleNewRef,MultiRefPresence,MultiRefVar1)
    CollectNameIdChoices = zip(list(DicoCollection.values()),list(DicoCollection.keys()))
    context = {"ResultTest": ResultTest, "CollectNameIdChoices":CollectNameIdChoices,
               "CollectIdSelect":CollectId}

    return render(request, 'Biblio/ViewBiblioInterface.html', context)



def ViewMultiRef(request, CollectId, Ref):

    PathFile1 = os.path.join(settings.BASE_DIR, "AllApps", "Biblio", "ResultMultiRef", Ref + ".csv")

    file_exist1 = os.path.exists(PathFile1)
    if not file_exist1:
        return render(request, 'general/home.html')

    else:
        Result0 = []
        Result1 = []
        Result2 = []
        Result3 = []
        Result4 = []
        with open(PathFile1, 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter='\t')
            for row in csv_reader:
                print(row)
                Result0.append(row[0])
                Result1.append(row[1])
                Result2.append(row[2])
                Result3.append(row[3] + ":home" )
                Result4.append(row[5])

    Result = zip(Result0,Result1,Result2,Result3,Result4)
    context = {"Result":Result}

    return render(request, 'Biblio/ViewMultiRef.html',context)

