import os, operator
from collections import Counter
from AllApps.PreTraitement.Persee.DelimitCorpus.core import GetAdresseCompletDoc, FctSpeRecupResultComplexe
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.CommunAllFct import TrameGenerale,EcritureResultComplex
from AllApps.PreTraitement.Persee.DelimitCorpus.models import  CorpusEtude, DocExtractInitial
from AllApps.PreTraitement.Persee.DelimitCorpus.outils.xpath import  DocMotPage
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.AideTitreFct import GetTitreTrouvesDansTexte, str_compare

from lxml import etree

def GetTitleAndCoordinateFigure(doc):
    '''
    Pour une fois, coordonnées graphiques présentes dans la tei
    avec en plus possibilité de récupérer le titre
    alors que pas possible dans le format érudit
    '''
    # recupération des id des pages
    tree = etree.parse(doc)
    XpathPageId = '/tei:TEI/tei:text/tei:body//tei:pb/@xml:id'
    ListeXpathPageId = tree.xpath(XpathPageId,
                           namespaces={"tei": "http://www.tei-c.org/ns/1.0"})
    ListePageId = []
    for elt in ListeXpathPageId:
        ListePageId.append(elt)

    # récupération des figures
    XpathFigure = "/tei:TEI/tei:text/tei:body//tei:figure"
    listeXpathFigure = tree.xpath(XpathFigure,
                           namespaces={"tei": "http://www.tei-c.org/ns/1.0"})
    ListeTitreFigure = []
    ListeCoordGraphFigure = []
    for figure in listeXpathFigure:
        MarqueurPresenceTitre = False
        MarqueurPresenceCoorGraph = False
        MarqueurPresencePage = False
        for elt1 in figure.iterdescendants():

            # recupération du titre
            if elt1.tag == "{http://www.tei-c.org/ns/1.0}title":
                if elt1.text is not None:
                    ListeTitreFigure.append(elt1.text)
                else:
                    ListeTitreFigure.append("None")
                MarqueurPresenceTitre = True

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
                    refpage = refzone.rsplit("_",1)[0]
                    if refpage in ListePageId:
                        page = ListePageId.index(refpage) + 1
                        MarqueurPresencePage = True

        # ajoute les resultats à la liste sous la même forme que DocErudit
        if MarqueurPresenceCoorGraph and MarqueurPresencePage:
            ListeCoordGraphFigure.append((page, left, top, right, bottom))
        else:
            print("ALERT")
            print(doc)

        # complète le titre si n'existe pas
        if not MarqueurPresenceTitre:
            ListeTitreFigure.append("None")

    return ListeCoordGraphFigure, ListeTitreFigure



def GetListMots(figures, listmot):
    """
    Args:
        figures (list of list): liste des figures contenues dans l'article
            [0]: Numéro de la page des figures
            [1]: coordonnée gauche de la fenêtre graphique
            [2]: coordonnée haute de la fenêtre graphique
            [3]: coordonnée droite de la fenêtre graphique
            [4]: coordonnée basse de la fenêtre graphique
        listmot (dict): dictionnaire de mots de l'article
            [1]: coordonnée gauche du mot
            [2]: coordonnée haute du mot
            [3]: coordonnée droite du mot
            [4]: coordonnée basse du mot

    Variables locales:
        figurestext_absolu: liste de liste des mots des figures

    """
    figuretext_absolu = []
    LEFT_COORD = 1
    TOP_COORD = 2
    RIGHT_COORD = 3
    BOTTOM_COORD = 4

    for i, figure in enumerate(figures):
        figuretext = []
        if figure[0] in listmot.keys() and len(figure) != 0:
            listmotpage = listmot[figure[0]]
            for mot in listmotpage:
                # test si la position du mot est contenue dans l'intervalle de la page
                if int(mot[LEFT_COORD]) >= figure[LEFT_COORD] and \
                                int(mot[LEFT_COORD]) <= figure[RIGHT_COORD] and \
                                int(mot[TOP_COORD]) >= figure[TOP_COORD] and \
                                int(mot[TOP_COORD]) <= figure[BOTTOM_COORD] and \
                                int(mot[RIGHT_COORD]) >= figure[LEFT_COORD] and \
                                int(mot[RIGHT_COORD]) <= figure[RIGHT_COORD] and \
                                int(mot[BOTTOM_COORD]) >= figure[TOP_COORD] and \
                                int(mot[BOTTOM_COORD]) <= figure[BOTTOM_COORD]:
                    figuretext.append(mot[0])
            figuretext_absolu.append(figuretext)
    return figuretext_absolu



def MotsPlusFrequentsTitreFigureDo(FichierResult,reduction,revue):
    error = False
    ResultFin = []
    NombreResults = 0

    Test = CorpusEtude.objects.filter(nom=reduction)
    if Test.exists():
        CEenCours = Test[0]

        # si le fichier de résultat n'a pas encore été crée
        if not os.path.isfile(FichierResult):
            RefTitreFigure = ""
            docsextractencours = DocExtractInitial.objects.filter(CorpusEtudeRef=CEenCours)
            # création des résultats
            for doc in docsextractencours:
                if doc.DocReferenceRef.RevueRef.nompersee == revue:
                    nomfichierencours = doc.DocReferenceRef.TextRef
                    addressedocencours = GetAdresseCompletDoc(nomfichierencours)
                    DataCoordinatesDocEnCours, TitresFigureDocEnCours = GetTitleAndCoordinateFigure(addressedocencours)

                    for titrefigure in TitresFigureDocEnCours:
                        RefTitreFigure = RefTitreFigure + " " + titrefigure.split(" ")[0]


            Result = Counter(RefTitreFigure.split(" ")).most_common()

            ResultFin = []
            for elt1 in Result:
                if elt1[0] != "" and elt1[0] != "None" and elt1[0] is not None:
                    ResultFin.append(elt1[0])

            NombreResults  = len(ResultFin)

            # cree le dossier si n'existe pas
            dossier = FichierResult.rsplit("/", 1)[0]
            if not os.path.exists(dossier):
                os.makedirs(dossier)


            with open(FichierResult, 'w') as f:

                f.write(" Termes d'annonce de figure" + "\n")
                f.write("/n")

                for elt1 in ResultFin:
                    f.write(elt1 + "\n")

            # pour que légende apparaisse dans l'interface si nouveau calcul
                ResultFin.insert("Termes d'annonce de figure" + "\n")

        else:
            with open(FichierResult, 'r') as f:
                content = f.readlines()
                ResultFin = []
                for i, elt1 in enumerate(content):
                    if i !=1:
                        ResultFin.append(elt1)
            NombreResults = len(ResultFin) - 1

    else:
        error = True

    return error, ResultFin, NombreResults


def TitreFigureSlashSpe(doc):
    ResultInd = None
    dateencours = doc.DocReferenceRef.annee
    nomfichierencours = doc.DocReferenceRef.TextRef
    addressedocencours = GetAdresseCompletDoc(nomfichierencours)
    DataCoordinatesDocEnCours, TitresFigureDocEnCours = GetTitleAndCoordinateFigure(addressedocencours)

    for titrefigure in TitresFigureDocEnCours:
        if "/" in titrefigure:
            ResultInd = [titrefigure, str(dateencours)]

    return ResultInd


def TitreFigureSlashDo(FichierResult,reduction,revue):
    error, Result, NbreResult = TrameGenerale(FichierResult, reduction, revue, TitreFigureSlashSpe,
                                              EcritureResultComplex,FctSpeRecupResultComplexe,
                                              listinsert=["Titre de la figure",
                                                          "Date du document"])
    return error, Result, NbreResult



def TitreFigureDetectFoundSpe(doc):
    ResultInd = None
    nomfichierencours = doc.DocReferenceRef.TextRef
    addressedocencours = GetAdresseCompletDoc(nomfichierencours)
    DataCoordinatesDocEnCours, TitresFigureDocEnCours = GetTitleAndCoordinateFigure(addressedocencours)
    MotsPageDocEnCours = DocMotPage(addressedocencours, detail=True)
    list_id_mots_figures = GetListMots(DataCoordinatesDocEnCours,
                                       MotsPageDocEnCours)

    # Chercher dans les mots du titres

    if len(list_id_mots_figures) == len(TitresFigureDocEnCours):
        for i, titrefigure in enumerate(TitresFigureDocEnCours):
            if titrefigure != "None":
                noseuil = len(list_id_mots_figures[i])
                ResultTitreTrouve = GetTitreTrouvesDansTexte(titrefigure,
                                                             list_id_mots_figures[i],
                                                             0.90,  # premier seuil de ressemblance
                                                             noseuil)
                if ResultTitreTrouve:
                    ResultInd = ['<a href="https://www.persee.fr/doc/' +
                                           nomfichierencours[8:-8] + '">' + nomfichierencours[8:-8] + '</a>',
                                           str(ResultTitreTrouve["matching_score"]),
                                           ResultTitreTrouve["titre_texte_corrige"],
                                           ResultTitreTrouve["titre"]]

    return ResultInd


def AfficheTitreFigureDetectDoFound(FichierResult,reduction,revue):
    error, Result, NbreResult = TrameGenerale(FichierResult, reduction, revue, TitreFigureDetectFoundSpe,
                                              EcritureResultComplex,FctSpeRecupResultComplexe,
                                              listinsert=["Identifiant document Persée (lien portail)",
                                                          "Score de ressemblance (mesure de Ratcliff/Obershelp)",
                                                          "Chaîne de caractère trouvée dans l'OCR présumée la plus correspondre au titre",
                                                          "Titre métadonnées(documenté par Persée)"])
    return error, Result, NbreResult




def TitreFigureDetectNotFoundSpe(doc):
    """Possible factorisation avec méthode ci dessus car c'est le même fontionnement"""
    ResultInd = None
    nomfichierencours = doc.DocReferenceRef.TextRef
    addressedocencours = GetAdresseCompletDoc(nomfichierencours)
    DataCoordinatesDocEnCours, TitresFigureDocEnCours = GetTitleAndCoordinateFigure(addressedocencours)
    MotsPageDocEnCours = DocMotPage(addressedocencours, detail=True)
    list_id_mots_figures = GetListMots(DataCoordinatesDocEnCours,
                                       MotsPageDocEnCours)

    # Chercher dans les mots du titres

    if len(list_id_mots_figures) == len(TitresFigureDocEnCours):
        for i, titrefigure in enumerate(TitresFigureDocEnCours):
            if titrefigure != "None":
                noseuil = len(list_id_mots_figures[i])
                ResultTitreTrouve = GetTitreTrouvesDansTexte(titrefigure,
                                                             list_id_mots_figures[i],
                                                             0.90,  # premier seuil de ressemblance
                                                             noseuil)
                if not ResultTitreTrouve:
                    ResultInd = ['<a href="https://www.persee.fr/doc/' +
                                              nomfichierencours[8:-8] + '">' + nomfichierencours[8:-8] + '</a>',
                                              titrefigure]

    return ResultInd


def AfficheTitreFigureDetectDoNotFound(FichierResult,reduction,revue):
    error, Result, NbreResult = TrameGenerale(FichierResult, reduction, revue, TitreFigureDetectNotFoundSpe,
                                              EcritureResultComplex,FctSpeRecupResultComplexe,
                                              listinsert=["Identifiant document Persée (lien portail)",
                                                          "Titre métadonnées(documenté par Persée)"])
    return error, Result, NbreResult




def AfficheTitrePlusDiscontinuSpe(doc):
    ResultInd = None
    nomfichierencours = doc.DocReferenceRef.TextRef
    addressedocencours = GetAdresseCompletDoc(nomfichierencours)
    DataCoordinatesDocEnCours, TitresFigureDocEnCours = GetTitleAndCoordinateFigure(addressedocencours)
    MotsPageDocEnCours = DocMotPage(addressedocencours, detail=True)
    list_id_mots_figures = GetListMots(DataCoordinatesDocEnCours,
                                       MotsPageDocEnCours)

    # Chercher dans les mots du titres

    if len(list_id_mots_figures) == len(TitresFigureDocEnCours):
        for i, titrefigure in enumerate(TitresFigureDocEnCours):
            if titrefigure != "None":
                compteurressemblance = 0
                for mottitrefigure in titrefigure.split():
                    for motensemblefigure in list_id_mots_figures[i]:
                        ressemblance = str_compare(mottitrefigure.lower(), motensemblefigure.lower())
                        if ressemblance > 0.8:
                            compteurressemblance += 1
                            break
                ratioressemblance = compteurressemblance / len(titrefigure.split())
                ResultInd = ['<a href="https://www.persee.fr/doc/' +
                                               nomfichierencours[8:-8] + '">' + nomfichierencours[8:-8] + '</a>',
                             str(ratioressemblance),
                             titrefigure]
    return ResultInd


def AfficheTitrePlusDiscontinuDo(FichierResult,reduction,revue):
    error, Result, NbreResult = TrameGenerale(FichierResult, reduction, revue, AfficheTitrePlusDiscontinuSpe,
                                              EcritureResultComplex,FctSpeRecupResultComplexe,
                                              listinsert=["Identifiant document",
                                                          "Score de ressemblance",
                                                          "Titre"],
                                              nsort=1)
    return error, Result, NbreResult



