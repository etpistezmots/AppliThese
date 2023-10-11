import os

from django.conf import settings
from lxml import etree

from AllApps.PreTraitement.Persee.DelimitCorpus.models import CorpusEtude, DocExtractInitial
from AllApps.PreTraitement.Persee.DelimitCorpus.outils.xpath import DocMotPage
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.AideMotCleFct import read_csv_motcle
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.ExploreFct.ExpCoordGraphSimpleFct import GetListIDMots, \
    NbMotAvantPage, GetIntervalleMotsParFenetre, calculsaut
from AllApps.PreTraitement.Persee.DelimitCorpus.core import GetAdresseCompletDoc, FctSpeRecupResultComplexe
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.CommunAllFct import TrameGenerale,EcritureResultComplex


def AfficheMotClesFrenchSpe(doc):
    ResultInd = None
    XpathMotCles = "/erudit:article/erudit:liminaire/erudit:grmotcle[@lang='fre']//erudit:motcle"
    dateencours = doc.DocReferenceRef.annee
    nomfichierencours = doc.DocReferenceRef.TextRef
    addressedocencours = GetAdresseCompletDoc(nomfichierencours)
    tree = etree.parse(addressedocencours.replace("tei", "erudit"))
    MotCles = tree.xpath(XpathMotCles, namespaces={"erudit": "http://www.erudit.org/xsd/article"})
    RefMotCleCetArticle = []
    if len(MotCles) != 0:
        for elt1 in MotCles:
            contenu = elt1.text
            if contenu != "":
                RefMotCleCetArticle.append(contenu)
    if len(RefMotCleCetArticle) != 0:
        ResultInd = ['<a href="https://www.persee.fr/doc/' +nomfichierencours[8:-8] + '">' + nomfichierencours[8:-8] + '</a>',
                     dateencours,
                     str(dateencours),
                     ', '.join(RefMotCleCetArticle)]
    return ResultInd

def AfficheMotClesFrenchDo(FichierResult,reduction,revue):
    error, Result, NbreResult = TrameGenerale(FichierResult, reduction, revue, AfficheMotClesFrenchSpe,
                                              EcritureResultComplex,FctSpeRecupResultComplexe,
                                              listinsert=["Référence du document","Date du document","Contenu textuel des mots clés"],
                                              nsort=1,nsuppr=1)
    return error, Result, NbreResult



def AfficheMotClesDiscontinuiteDo(FichierResult1, FichierResult2,reduction,revue):
    '''
    Ressemble à même fonction que pour les resume
    Mais subtilité provient du csv
    il faut transformer pour même structure
    '''
    RefMotClesDiscontinus = []
    CompteurGeneral = 0
    CompteurDiscon = 0

    # s'il manque un des fichiers de résultats
    if (not os.path.isfile(FichierResult1)) or (not os.path.isfile(FichierResult2)):
        # recupère les fichiers avec mots clés + infos db
        DocImpliqueSansDoublon, AllInfo = read_csv_motcle(revue)
        # création des résultats
        reductionencours = CorpusEtude.objects.filter(nom=reduction)
        docsextractencours = DocExtractInitial.objects.filter(CorpusEtudeRef=reductionencours[0])
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

                    # on reprend le même code que pour Resume
                    MotsPageDocEnCours = DocMotPage(addressedocencours, detail=True)
                    list_id_mots_motcles = GetListIDMots(DataCoordinatesDocEnCours,
                                                           MotsPageDocEnCours)

                    for k, coord_graph in enumerate(list_id_mots_motcles):

                        CompteurGeneral = CompteurGeneral + 1
                        list_intervalles_mots_retirer = GetIntervalleMotsParFenetre(coord_graph)

                        # Si une fenêtre graphique ne génère pas un et un seul intervalle
                        nbre_intervalles = len(list_intervalles_mots_retirer)
                        if nbre_intervalles > 1:

                            CompteurDiscon = CompteurDiscon + 1
                            intervallemots = []
                            for intervalle in list_intervalles_mots_retirer:
                                page = DataCoordinatesDocEnCours[k][0]
                                nbmots_shift = NbMotAvantPage(MotsPageDocEnCours, page)
                                motdeb = MotsPageDocEnCours[page][intervalle[0] - nbmots_shift - 1][0]
                                motfin = MotsPageDocEnCours[page][intervalle[1] - nbmots_shift - 1][0]
                                intervallemots.append((motdeb, motfin))

                            sautmax = max(calculsaut(list_intervalles_mots_retirer))

                            RefMotClesDiscontinus.append(
                                (nomfichierencours,
                                 "mots-cles  " + str(k + 1),
                                 sautmax,
                                 str(list_intervalles_mots_retirer),
                                 str(intervallemots)))

        RefMotClesDiscontinus = sorted(RefMotClesDiscontinus, key=lambda tup: tup[2], reverse=True)

        # cree le dossier si n'existe pas
        dossier = FichierResult1.rsplit("/", 1)[0]
        if not os.path.exists(dossier):
            os.makedirs(dossier)

        # si fichier1 existe, l'efface
        if os.path.isfile(FichierResult1):
            os.remove(FichierResult1)

        # écriture fichier1
        with open(FichierResult1, 'w') as f:

            f.write("Identifiant document" + "\n")
            f.write("Numéro de la zone de mot clé" + "\n")
            f.write("Discontuinuité max entre les intervalles" + "\n")
            f.write("Intervalle à retirer par les index" + "\n")
            f.write("Intervalle à retirer par les mots" + "\n")
            f.write("\n")

            for line in RefMotClesDiscontinus:
                for l, elt1 in enumerate(line):
                    if l == 2:
                        f.write(str(elt1) + "\n")
                    else:
                        f.write(elt1 + "\n")
                f.write("\n")

        # pour que légende apparaisse dans l'interface si nouveau calcul
        RefMotClesDiscontinus.insert(0, ("Identifiant document" + "\n",
                                           "Numéro de la zone de mot clé" + "\n",
                                           "Discontuinuité max entre les intervalles" + "\n",
                                           "Intervalle à retirer par les index" + "\n",
                                           "Intervalle à retirer par les mots" + "\n"))

        # si fichier2 existe, l'efface
        if os.path.isfile(FichierResult2):
            os.remove(FichierResult2)

        # écriture fichier 2
        with open(FichierResult2, 'w') as f:
            f.write("Nombre total éléments mots-Clés" + "\n")
            f.write("Nombre élément mots-clés avec discontinuité " + "\n")
            f.write("\n")
            f.write(str(CompteurGeneral))
            f.write(str(CompteurDiscon))

    else:

        # récup info fichier 1
        with open(FichierResult1, 'r') as f:
            content = f.readlines()
            SousListes = []
            for i, elt in enumerate(content):
                # petite astuce qui joue sur les multiples de six
                # car il y a cinq éléments dans chaque sous listes
                if ((i + 1) % 6 != 0):
                    SousListes.append(elt)
                else:
                    RefMotClesDiscontinus.append(SousListes)
                    SousListes = []

        # récup info fichier 2
        with open(FichierResult2, 'r') as f:
            content = f.readlines()
            for i, elt in enumerate(content):
                if i == 3:
                    CompteurGeneral = int(elt)
                if i == 4:
                    CompteurDiscon = int(elt)

    return RefMotClesDiscontinus, CompteurGeneral, CompteurDiscon

