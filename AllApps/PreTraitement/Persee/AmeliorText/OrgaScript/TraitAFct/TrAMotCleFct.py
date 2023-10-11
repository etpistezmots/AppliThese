from django.conf import settings
from lxml import etree

from AllApps.PreTraitement.Persee.DelimitCorpus.models import CorpusEtude, DocExtractInitial, Transformer
from AllApps.PreTraitement.Persee.DelimitCorpus.outils.xpath import DocMotPage
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.AideMotCleFct import read_csv_motcle
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.ExploreFct.ExpCoordGraphSimpleFct import GetListIDMots, \
    GetIntervalleMotsParFenetre, NbMotAvantPage
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.AideTitreFct import GetAdresseCompletDoc


def RecupMotCleFr(document):
    doc_erudit = document.replace("tei", "erudit")
    tree = etree.parse(doc_erudit)
    XpathFRMotCle = "/erudit:article/erudit:liminaire/erudit:grmotcle[@lang='fre']//erudit:motcle"

    listeFrMotCle = tree.xpath(XpathFRMotCle,
                           namespaces={"erudit": "http://www.erudit.org/xsd/article"})

    PresenceMotCleBoolean = False
    ContenuMotCle = ""

    if len(listeFrMotCle)!=0:
        PresenceMotCleBoolean = True
        for elt in listeFrMotCle:
            ContenuMotCle = ContenuMotCle + " " + elt.text

    return PresenceMotCleBoolean,ContenuMotCle


def InsertNewMotCle(reduction, donnees):

    RechercheZone = donnees['zone']
    StopMots = donnees['mots']
    AjoutMotCleFr = donnees['AjoutMotCleFr']

    # recupère les fichiers avec mots clés + infos db
    DocImpliqueSansDoublonGeo, AllInfoGeo = read_csv_motcle("geo")
    DocImpliqueSansDoublonSpgeo, AllInfoSpgeo = read_csv_motcle("spgeo")
    reductionencours = CorpusEtude.objects.filter(nom=reduction)
    docsextractencours = DocExtractInitial.objects.filter(CorpusEtudeRef=reductionencours[0])

    for doc in docsextractencours:
        nomfichierencours = doc.DocReferenceRef.TextRef
        addressedocencours = GetAdresseCompletDoc(nomfichierencours)
        nomfichierencoursred = nomfichierencours.split("_")[-2]

        if AjoutMotCleFr:
            MotCleFrPresence, MotCleFrContenu = RecupMotCleFr(addressedocencours)

        if doc.DocReferenceRef.RevueRef.nompersee == "geo":
            DocImpliqueSansDoublon = DocImpliqueSansDoublonGeo
            AllInfo = AllInfoGeo
        if doc.DocReferenceRef.RevueRef.nompersee== "spgeo":
            DocImpliqueSansDoublon = DocImpliqueSansDoublonSpgeo
            AllInfo = AllInfoSpgeo

        if nomfichierencoursred in DocImpliqueSansDoublon:

            MotsPageDocEnCours = DocMotPage(addressedocencours, detail=True)
            tree = etree.parse(addressedocencours.replace("tei", "erudit"))
            XpathIdPage = "/erudit:article/erudit:corps/erudit:texte//erudit:page"
            IdPage = tree.xpath(XpathIdPage, namespaces={"erudit": "http://www.erudit.org/xsd/article"})
            ListIdPage = []
            if len(IdPage) != 0:
                for elt1 in IdPage:
                    ListIdPage.append(elt1.get('id'))
            MotCleFind = []
            for elt1 in AllInfo:
                if elt1[0] == nomfichierencoursred:
                    MotCleFind.append(elt1)
            # transform pour trouver même structure
            # que DataCoordinatesDocEnCours dans ExploreResume car même principe
            DataCoordinatesDocEnCours = []
            for elt1 in MotCleFind:
                if elt1[1] in ListIdPage:
                    PageByArticle = ListIdPage.index(elt1[1]) + 1
                    # même prcocess que DocErudit
                    left = int(elt1[2]) * 2
                    top = int(elt1[3]) * 2
                    right = left + int(elt1[4]) * 2
                    bottom = top + int(elt1[5]) * 2
                    DataCoordinatesDocEnCours.append((PageByArticle, left, top, right, bottom))

            list_id_mots_motcles = GetListIDMots(DataCoordinatesDocEnCours,
                                                   MotsPageDocEnCours)
            for k, motcle in enumerate(list_id_mots_motcles):
                if len(motcle) != 0:
                    list_intervalles_mots_retirer = GetIntervalleMotsParFenetre(motcle)
                    # Si une fenêtre graphique ne génère pas un et un seul intervalle
                    for l,elt1 in enumerate(list_intervalles_mots_retirer):

                        if k==0 and l==0 and AjoutMotCleFr and MotCleFrPresence:
                            NewTransformer = Transformer(DocExtractRef=doc,
                                                       type='MotCle',
                                                       IndexDeb=elt1[0] -1,
                                                       IndexFin=elt1[1],
                                                       TextField=MotCleFrContenu.replace("'","''"),
                                                       comment="")
                            NewTransformer.save()
                        else :
                            NewTransformer = Transformer(DocExtractRef=doc,
                                                           type='MotCle',
                                                           IndexDeb=elt1[0] - 1,
                                                           IndexFin=elt1[1],
                                                           TextField="",
                                                           comment="")
                            NewTransformer.save()

                    # Ajout de la procédure pour retirer certain mots
                    mot1 = motcle[0]
                    page = DataCoordinatesDocEnCours[k][0]
                    nbmots_shift = NbMotAvantPage(MotsPageDocEnCours, page)
                    # fin car on cherche dans les x mots (seuil) avant
                    fin = mot1 - nbmots_shift - 1
                    if fin - int(RechercheZone) > 0:
                        deb = fin - int(RechercheZone)
                    else:
                        deb = 0
                    RechercheMotIn = MotsPageDocEnCours[page][deb:fin]
                    for j,motiter in enumerate(RechercheMotIn):
                        for stopmot in StopMots.split("*"):
                            if motiter[0] == stopmot:
                                nbmots_shift = NbMotAvantPage(MotsPageDocEnCours, page)
                                index = nbmots_shift + deb +j +1

                                NewTransformer = Transformer(DocExtractRef=doc,
                                                               type='MotCle',
                                                               IndexDeb=index - 1,
                                                               IndexFin=index,
                                                               TextField="",
                                                               comment="stopmot")
                                NewTransformer.save()

