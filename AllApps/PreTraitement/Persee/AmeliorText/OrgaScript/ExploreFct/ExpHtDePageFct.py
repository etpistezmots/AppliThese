import operator
import os

from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.CommunAllFct import TrameGenerale,EcritureResultIllimit,\
    LectureResultIllimit, TrameGeneraleList, EcritureResultList, LectureResultList
from AllApps.PreTraitement.Persee.DelimitCorpus.outils.xpath import DocMotPageLigne
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.AideTitreFct import GetAdresseCompletDoc



def AfficheHtDePageBrutSpe(doc):
    ResultInd = None
    nomfichierencours = doc.DocReferenceRef.TextRef
    dateencours = doc.DocReferenceRef.annee
    addressedocencours = GetAdresseCompletDoc(nomfichierencours)
    MotsPageLigneEnCours = DocMotPageLigne(addressedocencours)
    testlong = len(MotsPageLigneEnCours)
    AllFirstLinesArticle = ['<a href="https://www.persee.fr/doc/' + nomfichierencours[8:-8] + '">' + nomfichierencours[8:-8] + '</a>',
                            dateencours]
    for i in range(1, testlong):
        LigneEnCours = []
        LigneEnCoursCoordBas = []

        for j, mot in enumerate(MotsPageLigneEnCours[i]):
            if j > 0 and mot[5] == "n":
                break
            LigneEnCours.append(mot[0])
            LigneEnCoursCoordBas.append(int(mot[4]))

        if len(LigneEnCours) != 0:
            # replace pour ne gener le html. Car un <s souligne tout
            AllFirstLinesArticle.append(
                " ".join(LigneEnCours).replace(">", "").replace("<", "") + "                  /<em>" + str(
                    max(LigneEnCoursCoordBas)) + "</em>")

    if len(AllFirstLinesArticle) != 2:
        ResultInd = AllFirstLinesArticle
    return ResultInd



def AfficheHtDePageBrutDo(FichierResult,reduction, revue):
    error, Result, NbreResult = TrameGenerale(FichierResult, reduction, revue, AfficheHtDePageBrutSpe,
                                              EcritureResultIllimit, LectureResultIllimit,
                                              listinsert=["Identifiant document Persée (lien portail)",
                                                          "Premières lignes trouvées              / <em> Coordonnées spatiale maximale de la ligne </em>"],
                                              nsort=1, nsuppr=1)


    return error, Result, NbreResult




def AfficheHtDePageOrderSpe(doc,revue,Result):
    nomfichierencours = doc.DocReferenceRef.TextRef
    addressedocencours = GetAdresseCompletDoc(nomfichierencours)
    dateencours = doc.DocReferenceRef.annee
    # recupére fin de ligne
    MotsPageLigneEnCours = DocMotPageLigne(addressedocencours)
    testlong = len(MotsPageLigneEnCours)
    for i in range(1, testlong):
        LigneEnCours = []
        LigneEnCoursCoordBas = []
        LigneEnCoursDetail = []
        # sur la page i en énumérant !
        for j, mot in enumerate(MotsPageLigneEnCours[i]):
            if revue == "spgeo" and dateencours >= 1990:
                break
            if int(mot[2]) < 400:
                LigneEnCours = []
                break
            if j > 0 and mot[5] == "n":
                break
            LigneEnCours.append(mot[0])
            LigneEnCoursCoordBas.append(int(mot[4]))
            LigneEnCoursDetail.append((mot[0], mot[1], mot[2], mot[3], mot[4]))

        if len(LigneEnCours) != 0:
            Result[0].append('<a href="https://www.persee.fr/doc/' +
                                   nomfichierencours[8:-8] + '">' + nomfichierencours[8:-8] + '</a>')
            Result[1].append(" ".join(LigneEnCours))
            Result[2].append(max(LigneEnCoursCoordBas))
            Result[3].append(str(i))
            Result[4].append(str(max(LigneEnCoursCoordBas)))

    return Result



def AfficheHtDePageOrderDo(FichierResult,reduction, revue):
    error, Result, NbreResult = TrameGeneraleList(FichierResult, reduction, revue, AfficheHtDePageOrderSpe,
                                              EcritureResultList, LectureResultList,
                                              listinsert=["Identifiant document Persée (lien portail)",
                                                          "Première ligne trouvée supérieure à 400 pixel",
                                                          "Page sur laquelle apparaît cette première ligne",
                                                          "Coordonnée spatiale minimale de la ligne"],
                                              nlist= 5,nsort=2, nsuppr=2)


    return error, Result, NbreResult

