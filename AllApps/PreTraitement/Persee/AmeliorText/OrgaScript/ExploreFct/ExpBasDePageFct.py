import os, operator
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.CommunAllFct import TrameGenerale,EcritureResultIllimit,\
    LectureResultIllimit, TrameGeneraleList, EcritureResultList, LectureResultList
from AllApps.PreTraitement.Persee.DelimitCorpus.outils.xpath import DocMotPageLigne, DocErudit
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.AideTitreFct import GetAdresseCompletDoc
from lxml import etree



def AfficheBasDePageBrutSpe(doc):
    ResultInd = None
    nomfichierencours = doc.DocReferenceRef.TextRef
    dateencours = doc.DocReferenceRef.annee
    addressedocencours = GetAdresseCompletDoc(nomfichierencours)
    MotsPageLigneEnCours = DocMotPageLigne(addressedocencours)
    testlong = len(MotsPageLigneEnCours)
    AllLastLinesArticle = ['<a href="https://www.persee.fr/doc/' +
                           nomfichierencours[8:-8] + '">' + nomfichierencours[8:-8] + '</a>'
        , dateencours]
    for i in range(1, testlong):
        LigneEnCours = []
        LigneEnCoursCoordHaut = []

        for j, mot in reversed(list(enumerate(MotsPageLigneEnCours[i]))):
            if j > 0 and mot[5] == "n":
                break
            LigneEnCours.append(mot[0])
            LigneEnCoursCoordHaut.append(int(mot[2]))

        if len(LigneEnCours) != 0:
            AllLastLinesArticle.append(" ".join(list(reversed(LigneEnCours))).replace(">", "").replace("<",
                                                                                                       "") + "                  /<em>" + str(
                min(LigneEnCoursCoordHaut)) + "</em>")


    if len(AllLastLinesArticle) != 2:
        ResultInd = AllLastLinesArticle
    return ResultInd


def AfficheBasDePageBrutDo(FichierResult,reduction, revue):
    error, Result, NbreResult = TrameGenerale(FichierResult, reduction, revue, AfficheBasDePageBrutSpe,
                                              EcritureResultIllimit, LectureResultIllimit,
                                              listinsert=["Identifiant document Persée (lien portail)",
                                                          "Dernières lignes trouvées              / <em> Coordonnées spatiale minimale de la ligne </em>"],
                                              nsort=1, nsuppr=1)


    return error, Result, NbreResult



def TestMotInCoordGraph(mot,CoordGraph):
    LEFT_COORD = 1
    TOP_COORD = 2
    RIGHT_COORD = 3
    BOTTOM_COORD = 4
    # test si la position du mot est contenue dans l'intervalle de la page
    if int(mot[LEFT_COORD]) >= CoordGraph[LEFT_COORD] and \
        int(mot[LEFT_COORD]) <= CoordGraph[RIGHT_COORD] and \
        int(mot[TOP_COORD]) >= CoordGraph[TOP_COORD] and \
        int(mot[TOP_COORD]) <= CoordGraph[BOTTOM_COORD] and \
        int(mot[RIGHT_COORD]) >= CoordGraph[LEFT_COORD] and \
        int(mot[RIGHT_COORD]) <= CoordGraph[RIGHT_COORD] and \
        int(mot[BOTTOM_COORD]) >= CoordGraph[TOP_COORD] and \
        int(mot[BOTTOM_COORD]) <= CoordGraph[BOTTOM_COORD]:
        return True
    else:
        return False


def AfficheBasDePageOrderSpe(doc,revue,Result):
    nomfichierencours = doc.DocReferenceRef.TextRef
    addressedocencours = GetAdresseCompletDoc(nomfichierencours)

    # recupére fin de ligne
    MotsPageLigneEnCours = DocMotPageLigne(addressedocencours)
    testlong = len(MotsPageLigneEnCours)
    for i in range(1, testlong):
        LigneEnCours = []
        LigneEnCoursCoordHaut = []
        LigneEnCoursDetail = []
        # sur la page i en énumérant à l'envers !
        for j, mot in reversed(list(enumerate(MotsPageLigneEnCours[i]))):
            if j > 0 and mot[5] == "n":
                break
            LigneEnCours.append(mot[0])
            LigneEnCoursCoordHaut.append(int(mot[2]))
            LigneEnCoursDetail.append((mot[0], mot[1], mot[2], mot[3], mot[4]))

        if len(LigneEnCours) != 0:
            Result[0].append('<a href="https://www.persee.fr/doc/' +
                                   nomfichierencours[8:-8] + '">' + nomfichierencours[8:-8] + '</a>')
            Result[1].append(" ".join(list(reversed(LigneEnCours))))
            Result[2].append(min(LigneEnCoursCoordHaut))
            Result[3].append(str(i))
            Result[4].append(str(min(LigneEnCoursCoordHaut)))

    return Result


def AfficheBasDePageOrderDo(FichierResult,reduction, revue):
    error, Result, NbreResult = TrameGeneraleList(FichierResult, reduction, revue, AfficheBasDePageOrderSpe,
                                              EcritureResultList, LectureResultList,
                                              listinsert=["Identifiant document Persée (lien portail)",
                                                          "Dernière ligne trouvée",
                                                          "Page sur laquelle apparaît cette dernière ligne",
                                                          "Coordonnées spatiale minimale de la ligne"],
                                              nlist= 5,nsort=2, nsuppr=2, ordreverse=True)


    return error, Result, NbreResult




def AfficheBasDePageOrderNiNoteNiFigSpe(doc,revue,Result):

    nomfichierencours = doc.DocReferenceRef.TextRef
    addressedocencours = GetAdresseCompletDoc(nomfichierencours)

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
        else:
            print("ALERT")
            print(addressedocencours)

    # récupération des notes de bas de pages
    DataCoordinatesDocEnCours = DocErudit(addressedocencours, typesegment="note")

    # recupére fin de ligne
    MotsPageLigneEnCours = DocMotPageLigne(addressedocencours)
    testlong = len(MotsPageLigneEnCours)
    for i in range(1, testlong):
        LigneEnCours = []
        LigneEnCoursCoordBas = []
        LigneEnCoursDetail = []
        # sur la page i en énumérant à l'envers !
        for j, mot in reversed(list(enumerate(MotsPageLigneEnCours[i]))):
            if j > 0 and mot[5] == "n":
                break
            LigneEnCours.append(mot[0])
            LigneEnCoursCoordBas.append(int(mot[4]))
            LigneEnCoursDetail.append((mot[0], mot[1], mot[2], mot[3], mot[4]))

        if len(LigneEnCours) != 0:

            # TEST si tous les mots dans figure !
            MarqueurAllInFigure = False
            CompteurMotInFig = 0
            FiguresSurLaPage = [eltfigure for eltfigure in ListeCoordGraphFigure if eltfigure[0] == i]
            for motdetail in LigneEnCoursDetail:
                for Figure in FiguresSurLaPage:
                    TestMotInFig = TestMotInCoordGraph(motdetail, Figure)
                    if TestMotInFig:
                        CompteurMotInFig += 1
            if CompteurMotInFig == len(LigneEnCoursDetail):
                MarqueurAllInFigure = True

            # TEST si tous les mots dans note !
            MarqueurAllInNote = False
            CompteurMotInNote = 0
            NotesSurLaPage = [eltnote for eltnote in DataCoordinatesDocEnCours.obj if
                              eltnote[0] == i]
            for motdetail in LigneEnCoursDetail:
                for Note in NotesSurLaPage:
                    TestMotInNote = TestMotInCoordGraph(motdetail, Note)
                    if TestMotInNote:
                        CompteurMotInNote += 1
            if CompteurMotInNote == len(LigneEnCoursDetail):
                MarqueurAllInNote = True

            if (not MarqueurAllInFigure) and (not MarqueurAllInNote):
                Result[0].append('<a href="https://www.persee.fr/doc/' +
                                 nomfichierencours[8:-8] + '">' + nomfichierencours[8:-8] + '</a>')
                Result[1].append(" ".join(list(reversed(LigneEnCours))))
                Result[2].append(min(LigneEnCoursCoordBas))
                Result[3].append(str(i))
                Result[4].append(str(min(LigneEnCoursCoordBas)))

    return Result


def AfficheBasDePageOrderNiNoteNiFigDo(FichierResult,reduction, revue):
    error, Result, NbreResult = TrameGeneraleList(FichierResult, reduction, revue, AfficheBasDePageOrderNiNoteNiFigSpe,
                                              EcritureResultList, LectureResultList,
                                              listinsert=["Identifiant document Persée (lien portail)",
                                                          "Dernière ligne trouvée",
                                                          "Page sur laquelle apparaît cette dernière ligne",
                                                          "Coordonnées spatiale minimale de la ligne"],
                                              nlist= 5,nsort=2, nsuppr=2, ordreverse=True)


    return error, Result, NbreResult



def AfficheBasDePageTextualCombiSpe(doc):
    ResultInd = None
    nomfichierencours = doc.DocReferenceRef.TextRef
    addressedocencours = GetAdresseCompletDoc(nomfichierencours)
    MotsPageLigneEnCours = DocMotPageLigne(addressedocencours)
    testlong = len(MotsPageLigneEnCours)
    AllLastLinesArticle = ['<a href="https://www.persee.fr/doc/' +
                           nomfichierencours[8:-8] + '">' + nomfichierencours[8:-8] + '</a>']
    for i in range(1, testlong):
        LigneEnCours = []
        for j, mot in reversed(list(enumerate(MotsPageLigneEnCours[i]))):
            if j > 0 and mot[5] == "n":
                break
            LigneEnCours.append(mot[0])
        if len(LigneEnCours) != 0:
            if LigneEnCours[-1][0:2] == "DE" or LigneEnCours[-1][0:2] == "DB" or LigneEnCours[-1][0:2] == "DK" or \
                            LigneEnCours[-1][0:3] == "ANN" or LigneEnCours[-1][0:3] == "Ann" or LigneEnCours[0][
                                                                                                -3:] == "Ann" or \
                            LigneEnCours[0][-3:] == "ANN" or LigneEnCours[-1][0:5] == "ARMAND" or LigneEnCours[-1][
                                                                                                  0:5] == "Armand" \
                    or LigneEnCours[-1][0:4] == "Gèo." or LigneEnCours[-1][0:4] == "Geo." \
                    or "Année." in LigneEnCours or "ANNEE." in LigneEnCours or "ANNÉE" in LigneEnCours:
                AllLastLinesArticle.append(" ".join(list(reversed(LigneEnCours))))

    if len(AllLastLinesArticle) != 1:
        ResultInd = AllLastLinesArticle

    return ResultInd


def AfficheBasDePageTextualCombiDo(FichierResult,reduction, revue):
    error, Result, NbreResult = TrameGenerale(FichierResult, reduction, revue, AfficheBasDePageTextualCombiSpe,
                                              EcritureResultIllimit, LectureResultIllimit,
                                              listinsert=["Identifiant document Persée (lien portail)",
                                                          "Dernières lignes trouvées"])


    return error, Result, NbreResult


