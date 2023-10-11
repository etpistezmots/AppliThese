import os
from lxml import etree

from AllApps.PreTraitement.Persee.DelimitCorpus.core import GetAdresseCompletDoc, FctSpeRecupResultComplexe
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.CommunAllFct import TrameGenerale,EcritureResultComplex
from AllApps.PreTraitement.Persee.DelimitCorpus.models import CorpusEtude, DocExtractInitial
from AllApps.PreTraitement.Persee.DelimitCorpus.outils.xpath import DocErudit, DocMotPage
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.AideMotCleFct import read_csv_motcle
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.ExploreFct.ExpCoordGraphSimpleFct import GetListIDMots, \
    NbMotAvantPage
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.ExploreFct.ExpBasDePageFct import TestMotInCoordGraph


def TestMot(ListCoordGraph, motdetail, page):
    EltsGraphiques = ["Figure","Note","NoteBio","NoteEdito","Resume","MotCle"]
    ListeMarqueur= [False, False, False, False, False, False]
    for z,EltGraphique in enumerate(EltsGraphiques):
        EltGraphiqueSurLaPage = [eltgraph for eltgraph in ListCoordGraph[z] if eltgraph[0] == page]
        for Elt in EltGraphiqueSurLaPage:
            TestMotInElt = TestMotInCoordGraph(motdetail, Elt)
            if TestMotInElt:
                ListeMarqueur[z] = True
                break

    return ListeMarqueur

def RenvoiIndexPageLastBiblio(ListPages):
    '''
    Si les biblios sont sur pages successives ou mêmes pages, considère que font partie du même bloc 
    '''
    i = 0
    eltpre = 0
    lenListPages = len(ListPages)
    for i,elt in reversed(list(enumerate(ListPages))):
        if i + 1 == lenListPages:
            eltpre = elt

        if i + 1 < lenListPages:
            diff = eltpre - elt
            if diff > 1:
                return i +1
            else:
                eltpre = elt
    return i



def AfterLastBiblioDo(FichierResult,reduction, revue):
    error = False
    StockResult = []
    NbreResult = 0

    Test = CorpusEtude.objects.filter(nom=reduction)
    if Test.exists():
        CEenCours = Test[0]

        # si le fichier de résultat n'a pas encore été crée
        if not os.path.isfile(FichierResult):
            # création des résultats
            docsextractencours = DocExtractInitial.objects.filter(CorpusEtudeRef=CEenCours)

            # pour récupérer infos mot clé
            DocImpliqueSansDoublon, AllInfo = read_csv_motcle(revue)

            for doc in docsextractencours :
                MotAfterBiblioTot = []
                if doc.DocReferenceRef.RevueRef.nompersee == revue:
                    nomfichierencours = doc.DocReferenceRef.TextRef

                    addressedocencours = GetAdresseCompletDoc(nomfichierencours)

                    # recupére des biblios
                    BiblioCoordinatesDocEnCours = DocErudit(addressedocencours, typesegment="biblio")

                    if len(BiblioCoordinatesDocEnCours.obj) > 0:
                        CoordLastBiblio = BiblioCoordinatesDocEnCours.obj[-1]


                        # recupération des id des pages
                        tree = etree.parse(addressedocencours)
                        XpathPageId = '/tei:TEI/tei:text/tei:body//tei:pb/@xml:id'
                        ListeXpathPageId = tree.xpath(XpathPageId,
                                                      namespaces={"tei": "http://www.tei-c.org/ns/1.0"})
                        ListePageId = []
                        for elt in ListeXpathPageId:
                            ListePageId.append(elt)

                        # recuperation des figures
                        XpathFigure = "/tei:TEI/tei:text/tei:body//tei:figure"
                        listeXpathFigure = tree.xpath(XpathFigure,
                                                      namespaces={"tei": "http://www.tei-c.org/ns/1.0"})
                        ListeCoordGraphFigure = []
                        for figure in listeXpathFigure:
                            MarqueurPresenceCoorGraph = False
                            MarqueurPresencePage = False
                            for elt1 in figure.iterdescendants():
                                if elt1.tag == "{http://www.tei-c.org/ns/1.0}ref":
                                    # coordonnee graph
                                    if 'type' in elt1.attrib:

                                        # ex space (751 235 760 658)
                                        refcoordgraph = elt1.get('target')
                                        coordx = int(refcoordgraph.split()[1][1:])
                                        coordy = int(refcoordgraph.split()[2])
                                        dimx = int(refcoordgraph.split()[3])
                                        dimy = int(refcoordgraph.split()[4][:-1])

                                        left = int(coordx) * 2
                                        top = int(coordy) * 2
                                        right = left + int(dimx) * 2
                                        bottom = top + int(dimy) * 2

                                        MarqueurPresenceCoorGraph = True

                                    # reference zone
                                    else:
                                        refzone = elt1.get('target')
                                        refpage = refzone.rsplit("_", 1)[0]
                                        if refpage in ListePageId:
                                            page = ListePageId.index(refpage) + 1
                                            MarqueurPresencePage = True

                            # ajoute les resultats à la liste sous la même forme que DocErudit
                            if MarqueurPresenceCoorGraph and MarqueurPresencePage:
                                ListeCoordGraphFigure.append((page, left, top, right, bottom))


                        # récupération des notes
                        NoteCoordinatesDocEnCours = DocErudit(addressedocencours, typesegment="note")
                        NoteBioCoordinatesDocEnCours = DocErudit(addressedocencours, typesegment="notebio")
                        NoteEditoCoordinatesDocEnCours = DocErudit(addressedocencours, typesegment="noteedito")

                        # récupérarion des résumes
                        ResumeCoordinatesDocEnCours = DocErudit(addressedocencours, typesegment='resume')

                        # récupération des mots-clés
                        nomfichierencoursred = nomfichierencours.split("_")[-2]
                        MotCleFind = []
                        for elt1 in AllInfo:
                            if elt1[0] == nomfichierencoursred:
                                MotCleFind.append(elt1)
                        # transform pour trouver même structure
                        # que DataCoordinatesDocEnCours dans ExploreResume car même principe
                        MotCleCoordinatesDocEnCours = []
                        for elt1 in MotCleFind:
                            if elt1[1] in ListePageId:
                                PageByArticle = ListePageId.index(elt1[1]) + 1
                                # même prcocess que DocErudit
                                left = int(elt1[2]) * 2
                                top = int(elt1[3]) * 2
                                right = left + int(elt1[4]) * 2
                                bottom = top + int(elt1[5]) * 2
                                MotCleCoordinatesDocEnCours.append((PageByArticle, left, top, right, bottom))

                        # LISTE DE TOUTES LES COORDONNEES GRAPHIQUES
                        ListCoordGraph = [ListeCoordGraphFigure, NoteCoordinatesDocEnCours.obj, NoteBioCoordinatesDocEnCours.obj,
                                          NoteEditoCoordinatesDocEnCours.obj, ResumeCoordinatesDocEnCours.obj ,MotCleCoordinatesDocEnCours]

                        # recupére tous les mots
                        MotsPageEnCours = DocMotPage(addressedocencours,detail=True)

                        # recupere les id des biblios
                        list_id_last_biblio = GetListIDMots(BiblioCoordinatesDocEnCours.obj,
                                                             MotsPageEnCours)
                        # récupère nombre de mots avant cette page
                        nbmots_shift = NbMotAvantPage(MotsPageEnCours, CoordLastBiblio[0])

                        # petite partie pour prévenir une erreur quand la dernière biblio correspond à un ensemble vide
                        # prend l'avant dernière
                        if len(list_id_last_biblio[-1]) == 0:
                            lastindexbiblio = list_id_last_biblio[-2][-1]
                        else:
                            lastindexbiblio = list_id_last_biblio[-1][-1]

                        testlong = len(MotsPageEnCours)

                        # Va iterer sur toutes les pages à partir de cette dernière biblio
                        for compteur,i in enumerate(range(CoordLastBiblio[0], testlong +1)):


                            AllMotsDeCettePage = MotsPageEnCours[i]
                            MotsAfterBiblioNiFigNiNote = []

                            for compteur1,motdetail in enumerate(AllMotsDeCettePage):

                                # sur la première page, pour les mots après la fin de la biblio
                                # pour les autres pages, pour tous les mots

                                 if (compteur == 0 and compteur1 > lastindexbiblio - nbmots_shift -1) or compteur > 0 :

                                    ListMarq = TestMot(ListCoordGraph, motdetail, i)
                                    MarqueurGlobal = False

                                    for marqueur in ListMarq:
                                        if marqueur:
                                            MarqueurGlobal = True

                                    # Si le mot n'appartient à aucunes des fenêtre graphique précédemment cherché
                                    if not MarqueurGlobal:
                                         MotsAfterBiblioNiFigNiNote.append(motdetail[0])

                            if len(MotsAfterBiblioNiFigNiNote)>0:
                                MotAfterBiblioTot.append(" ".join(MotsAfterBiblioNiFigNiNote))


                        if len(MotAfterBiblioTot)>0:
                            StockResult.append(['<a href="https://www.persee.fr/doc/' +
                                               nomfichierencours[8:-8] + '">' + nomfichierencours[8:-8] + '</a>',MotAfterBiblioTot])

            # cree le dossier si n'existe pas
            dossier = FichierResult.rsplit("/", 1)[0]
            if not os.path.exists(dossier):
                os.makedirs(dossier)

            # crée le fichier avec tri sur les dates
            with open(FichierResult, 'w') as f:

                f.write("Référence et lien du document" + "\n")
                f.write("Partie arpès la dernière biblio" + "\n")
                f.write("\n")

                for elt in StockResult:
                    f.write(elt[0] + "\n")
                    f.write(" ".join(elt[1]) + "\n")
                    f.write("\n")

            StockResult.append(["Référence et lien du document" + "\n", "Partie arpès la dernière biblio" + "\n"])



                    # sinon lit directement le ficher des résultats
        else:
            with open(FichierResult, 'r') as f:
                content = f.readlines()
                SousListes = []
                for i, elt in enumerate(content):
                    # petite astuce qui joue sur les multiples de trois
                    # car il y a deux éléments dans chaque sous listes
                    if ((i + 1) % 3 != 0):
                        SousListes.append(elt)
                    else:
                        StockResult.append(SousListes)
                        SousListes = []

    else:
        error = True

    NbreResult = len(StockResult)-1

    return error,StockResult,NbreResult


def PlusieursBibliosSpe(doc):
    ResultInd = None
    nomfichierencours = doc.DocReferenceRef.TextRef
    addressedocencours = GetAdresseCompletDoc(nomfichierencours)
    # recupére des biblios
    BiblioCoordinatesDocEnCours = DocErudit(addressedocencours, typesegment="biblio")

    if len(BiblioCoordinatesDocEnCours.obj) > 0:
        Pagesbiblio = [part[0] for part in BiblioCoordinatesDocEnCours.obj]
        IndexPageLastBiblio = RenvoiIndexPageLastBiblio(Pagesbiblio)

        if IndexPageLastBiblio > 0:
            ResultInd = ['<a href="https://www.persee.fr/doc/' +  nomfichierencours[8:-8] + '">' + nomfichierencours[8:-8] + '</a>', IndexPageLastBiblio + 1, str(IndexPageLastBiblio + 1)]

    return ResultInd


def PlusieursBibliosDo(FichierResult,reduction,revue):
    error, Result, NbreResult = TrameGenerale(FichierResult, reduction, revue, PlusieursBibliosSpe,
                                              EcritureResultComplex,FctSpeRecupResultComplexe,
                                              listinsert=["Identifiant document Persée (lien portail)","Nombre de bibliographies détectées"],nsort=1,nsuppr=1)
    return error, Result, NbreResult



def MaxPagesContigues(lista):
    compteur = 1
    maxcompt = 1
    eltpre = 0
    for i, elt in enumerate(lista):
        if i == 0:
            eltpre = elt
        else:
            diff = elt - eltpre
            if diff == 1:
                compteur += 1
            else:
                if compteur > maxcompt:
                    maxcompt = compteur
                compteur = 1
            eltpre = elt

    if compteur > maxcompt:
        maxcompt = compteur

    return maxcompt

def NbreGroupesPageContigu(lista):
    compteur = 1
    eltpre = 0
    for i, elt in enumerate(lista):
        if i == 0:
            eltpre = elt
        else:
            diff = elt - eltpre
            if diff > 1:
                compteur += 1
            eltpre = elt
    return compteur


def BiblioInCRSpe(doc):
    ResultInd = None
    nomfichierencours = doc.DocReferenceRef.TextRef
    addressedocencours = GetAdresseCompletDoc(nomfichierencours)
    # recupére des biblios
    BiblioCoordinatesDocEnCours = DocErudit(addressedocencours, typesegment="biblio")
    NbreBiblioErudit = len(BiblioCoordinatesDocEnCours.obj)
    Pagesbiblio = [part[0] for part in BiblioCoordinatesDocEnCours.obj]
    NbreBiblioCalcul = NbreGroupesPageContigu(Pagesbiblio)
    MaxPageBiblio = MaxPagesContigues(Pagesbiblio)
    if NbreBiblioErudit > 0:
        ResultInd= ['<a href="https://www.persee.fr/doc/' +
                            nomfichierencours[8:-8] + '">' + nomfichierencours[8:-8] + '</a>',
                            NbreBiblioCalcul,
                            str(NbreBiblioCalcul),
                            str(MaxPageBiblio)]
    return ResultInd


def BiblioInCRDo(FichierResult,reduction,revue):
    error, Result, NbreResult = TrameGenerale(FichierResult, reduction, revue, BiblioInCRSpe,
                                              EcritureResultComplex,FctSpeRecupResultComplexe,
                                              listinsert=["Identifiant document Persée (lien portail)",
                                                          "Nombre de bibliographies",
                                                          "Nombre de pages de la plus grande bibliographie"],nsort=1,nsuppr=1)
    return error, Result, NbreResult

