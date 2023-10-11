import os

from lxml import etree
from AllApps.PreTraitement.Persee.DelimitCorpus.models import CorpusEtude, DocExtractInitial
from AllApps.PreTraitement.Persee.DelimitCorpus.outils.xpath import DocRequete, DocMotPage, DocErudit
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.AideMotCleFct import read_csv_motcle
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.ExploreFct.ExpCoordGraphSimpleFct import GetListIDMots, \
    NbMotAvantPage
from AllApps.PreTraitement.Persee.DelimitCorpus.core import GetAdresseCompletDoc, FctSpeRecupResultComplexe
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.CommunAllFct import TrameGenerale,EcritureResultComplex

def AfficheResumesFrenchSpe(doc):
    ResultInd = None
    Xpathresume = "/tei:TEI/tei:text/tei:front/tei:div[@type='abstract' and @xml:lang='fre']//text()"
    dateencours = doc.DocReferenceRef.annee
    nomfichierencours = doc.DocReferenceRef.TextRef
    addressedocencours = GetAdresseCompletDoc(nomfichierencours)
    DocEnCours = DocRequete(addressedocencours, Xpathresume, "resume", "j")
    if DocEnCours.resume.strip() != "":
        ResultInd =['<a href="https://www.persee.fr/doc/' + nomfichierencours[8:-8] + '">' + nomfichierencours[8:-8] + '</a>',
                    dateencours,
                    str(dateencours),
                    DocEnCours.resume.replace("\n", " ")]
    return ResultInd


def AfficheResumesFrenchDo(FichierResult,reduction,revue):
    error, Result, NbreResult = TrameGenerale(FichierResult, reduction, revue, AfficheResumesFrenchSpe,
                                              EcritureResultComplex,FctSpeRecupResultComplexe,
                                              listinsert=["Référence du document","Date du document","Contenu textuel du résumé"],
                                              nsort=1, nsuppr=1)
    return error, Result, NbreResult



def TraitObjetCommun(nomfichierencours,addressedocencours,DataCoordinatesDocEnCoursRef,seuil,MotPonctuList,MotPonctuDico):
    MotsPageDocEnCours = DocMotPage(addressedocencours, detail=True)
    list_id_mots_objets = GetListIDMots(DataCoordinatesDocEnCoursRef,MotsPageDocEnCours)
    for k, objet in enumerate(list_id_mots_objets):
        if len(objet) != 0:
            mot1 = objet[0]
            page = DataCoordinatesDocEnCoursRef[k][0]
            nbmots_shift = NbMotAvantPage(MotsPageDocEnCours, page)
            # fin car on cherche dans les x mots (seuil) avant
            fin = mot1 - nbmots_shift - 1
            if fin - int(seuil) > 0:
                deb = fin - int(seuil)
            else:
                deb = 0
            RechercheMotIn = MotsPageDocEnCours[page][deb:fin]
            for i, motiter in enumerate(RechercheMotIn):
                for motponctu in MotPonctuList:
                    if motiter[0] == motponctu:
                        MotPonctuDico[motponctu].append((nomfichierencours, fin - deb - i))

    return MotPonctuDico



def PresenceMotAvantObjetDo(FichierResult,reduction,mots,ponctuations,seuil,revue, objet):
    '''
    Ressemble à même fonction que pour les resume
    Mais subtilité provient du csv
    il faut transformer pour même structure
    '''

    # création des résultats
    reductionencours = CorpusEtude.objects.filter(nom=reduction)
    docsextractencours = DocExtractInitial.objects.filter(CorpusEtudeRef=reductionencours[0])

    listmotsnew = mots.split("*")
    listponctuations = ponctuations.split("*")
    listponctuationsnew = []

    # cas pas de ponctuation:
    for elt in listponctuations:
        if elt == "no":
            listponctuationsnew.append("")
        else:
            listponctuationsnew.append(elt)

    # combinaison chaque mot + chaque ponctuation
    MotPonctuList = []
    MotPonctuDico = {}
    for mot in listmotsnew:
        for ponctuation in listponctuationsnew:
            MotPonctuList.append(mot + ponctuation)
            MotPonctuDico[mot + ponctuation] = []


    if objet == "Resume" or objet == "Biblio" or objet == "Annexe":

        for doc in docsextractencours:
            if doc.DocReferenceRef.RevueRef.nompersee == revue:
                nomfichierencours = doc.DocReferenceRef.TextRef
                addressedocencours = GetAdresseCompletDoc(nomfichierencours)
                if objet == "Resume":
                    DataCoordinatesDocEnCours = DocErudit(addressedocencours, typesegment='resume')
                if objet == "Biblio":
                    DataCoordinatesDocEnCours = DocErudit(addressedocencours, typesegment='biblio')
                if objet == "Annexe":
                    DataCoordinatesDocEnCours = DocErudit(addressedocencours, typesegment='annexe')
                MotPonctuDico = TraitObjetCommun(nomfichierencours,addressedocencours,DataCoordinatesDocEnCours.obj,
                                                 seuil,MotPonctuList,MotPonctuDico)


    if objet == "MotCle":

        # recupère les fichiers avec mots clés + infos db
        DocImpliqueSansDoublon, AllInfo = read_csv_motcle(revue)

        for doc in docsextractencours:
            if doc.DocReferenceRef.RevueRef.nompersee == revue:
                nomfichierencours = doc.DocReferenceRef.TextRef
                addressedocencours = GetAdresseCompletDoc(nomfichierencours)
                nomfichierencoursred = nomfichierencours.split("_")[-2]
                if nomfichierencoursred in DocImpliqueSansDoublon:
                    tree = etree.parse(addressedocencours.replace("tei","erudit"))
                    XpathIdPage = "/erudit:article/erudit:corps/erudit:texte//erudit:page"
                    IdPage = tree.xpath(XpathIdPage, namespaces={"erudit": "http://www.erudit.org/xsd/article"})
                    ListIdPage = []
                    if len(IdPage) != 0:
                        for elt1 in IdPage:
                            ListIdPage.append(elt1.get('id'))
                    MotCleFind = []
                    for elt1 in AllInfo:
                        if elt1[0]== nomfichierencoursred:
                            MotCleFind.append(elt1)
                    # transform pour trouver même structure
                    # que DataCoordinatesDocEnCours dans ExploreResume car même principe
                    DataCoordinatesDocEnCours = []
                    for elt1 in MotCleFind:
                        if elt1[1] in ListIdPage:
                            PageByArticle = ListIdPage.index(elt1[1]) + 1
                            # même prcocess que DocErudit
                            left = int(elt1[2])*2
                            top = int(elt1[3])*2
                            right = left + int(elt1[4]) * 2
                            bottom = top + int(elt1[5]) * 2
                            DataCoordinatesDocEnCours.append((PageByArticle,left,top,right,bottom))


                    MotPonctuDico = TraitObjetCommun(nomfichierencours, addressedocencours, DataCoordinatesDocEnCours, seuil,
                                             MotPonctuList, MotPonctuDico)

    # cree le dossier si n'existe pas
    dossier = FichierResult.rsplit("/", 1)[0]
    if not os.path.exists(dossier):
        os.makedirs(dossier)

    lastmotponctu = MotPonctuList[-1]
    compteur = 0


    with open(FichierResult, 'w') as f:
        f.write(
            """<table class="dataframe" border="1">""" + "\n" + "\t" + "<tr>" + "\n" + "\t" + "\t" + "<td>&nbsp;</td>" + "\n")
        for mot in listmotsnew:
            f.write("\t" + "\t" "<td>" + '"' + mot + '"' + "</td>" + "\n")
        f.write("\t" + "</tr>" + "\n" + "\t" + "<tr>" + "\n")

        for ponctu in listponctuationsnew:
            f.write("\t" + "\t" + "<td>" + '"' + ponctu + '"' + "</td>" + "\n")
            for mot in listmotsnew:
                compteur += 1
                motponctu = mot + ponctu
                nbrresults = len(MotPonctuDico[motponctu])
                if nbrresults == 0:
                    f.write("\t" + "\t" + "<td>" + str(nbrresults) + "</td>" + "\n")
                else:
                    f.write("\t" + "\t" + "<td>" + '<a href="' +
                            "http://127.0.0.1:8000/amelior/PresenceMotAvantObjetResult/" +
                            reduction + "/" + revue + "/" + str(compteur) + "/" + objet + '">' +
                            str(nbrresults) + "</a>" + "</td>" + "\n")

            if motponctu != lastmotponctu:
                f.write("\t" + "</tr>" + "\t" + "<tr>" + "\n")
            else:
                f.write("\t" + "</tr>" + "\n")

        f.write("</table>")

    # Création d'un fichier pour garder la variable nombre de mots avant
    with open(FichierResult[:-4] + "NbreMotsAvt.txt", 'w') as f:
        f.write(str(seuil))


    # Création sous-dossier pour stocker résultat individuel
    ssdossier = dossier + "/" + objet  +"Result"
    if not os.path.exists(ssdossier):
        os.makedirs(ssdossier)

    # résultat de tous les résultats individuels
    # même compteur que précédememt
    compteur = 0
    for ponctu in listponctuationsnew:
        for mot in listmotsnew:
            compteur += 1
            motponctu = mot + ponctu
            results = MotPonctuDico[motponctu]
            nbrresults = len(results)
            if nbrresults != 0:
                FichierResultSpe1 = ssdossier + "/" + str(compteur) + revue + ".txt"
                FichierResultSpe2 = ssdossier + "/" + str(compteur) + revue + "Para.txt"
                results = sorted(results, key=lambda tup: tup[1], reverse=True)

                with open(FichierResultSpe1, 'w') as f:

                    f.write("Référence du document" + "\n")
                    if objet == "Resume":
                        f.write("Eloignement du mot de référence par rapport à la fenêtre graphique de résumé" + "\n")
                    if objet == "MotCle":
                        f.write("Eloignement du mot de référence par rapport à la fenêtre graphique de mot clé" + "\n")
                    if objet == "Biblio":
                        f.write("Eloignement du mot de référence par rapport à la fenêtre graphique de bibliographie" + "\n")
                    if objet == "Annexe":
                        f.write("Eloignement du mot de référence par rapport à la fenêtre graphique d'annexe" + "\n")
                    f.write("\n")

                    for result in results:
                        f.write('<a href="https://www.persee.fr/doc/' +
                                result[0][8:-8] + '">' + result[0][8:-8] + '</a>' + "\n")
                        f.write(str(result[1]) + "\n")
                        f.write("\n")

                with open(FichierResultSpe2, 'w') as f:
                    f.write(mot + "\n")
                    f.write(ponctu + "\n")
                    f.write(seuil + "\n")



