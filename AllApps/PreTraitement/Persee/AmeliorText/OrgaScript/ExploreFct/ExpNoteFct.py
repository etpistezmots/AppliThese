import os
from AllApps.PreTraitement.Persee.DelimitCorpus.models import  CorpusEtude, DocExtractInitial
from AllApps.PreTraitement.Persee.DelimitCorpus.outils.xpath import  DocMotPageLigne
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.AideTitreFct import str_compare
from lxml import etree
from AllApps.PreTraitement.Persee.DelimitCorpus.core import GetAdresseCompletDoc, FctSpeRecupResultComplexe
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.CommunAllFct import TrameGenerale,EcritureResultComplex,EcritureResultIllimit,\
    LectureResultIllimit


def NoteBioExistSpe(doc):
    ResultInd = None
    nomfichierencours = doc.DocReferenceRef.TextRef
    dateencours = doc.DocReferenceRef.annee
    addressedocencours = GetAdresseCompletDoc(nomfichierencours)
    tree = etree.parse(addressedocencours.replace("tei", "erudit"))
    RechercheNoteBio = tree.xpath(
        "/erudit:article/erudit:corps/erudit:texte/erudit:page//erudit:segment[@typesegment='notebio']/erudit:alinea",
        namespaces={"erudit": "http://www.erudit.org/xsd/article"})

    if len(RechercheNoteBio) != 0:
        for note in RechercheNoteBio:
            ResultInd =['<a href="https://www.persee.fr/doc/' +nomfichierencours[8:-8] + '">' + nomfichierencours[8:-8] + '</a>',
                        dateencours,
                        note.text.replace("\n", "")]

    return ResultInd


def NoteBioExistDo(FichierResult,reduction,revue):
    error, Result, NbreResult = TrameGenerale(FichierResult, reduction, revue, NoteBioExistSpe,
                                              EcritureResultComplex,FctSpeRecupResultComplexe,
                                              listinsert=["Identifiant document Persée (lien portail)",
                                                          "Note biographique"],
                                              nsort=1,nsuppr=1)
    return error, Result, NbreResult


def RechercheNoteBioSpe(doc):
    ResultInd = None

    ListGrad = ["Professeur", "Maitre", "Conférence", "Enseignant", "Ingénieur", "Technicien", "Chargé", "Recherche",
                "Etude", "Agrégé", "Recteur", "Directeur", "Docteur", "Etudiant", "Doctorant", "Post - Doctorant",
                "Membre", "Président", "Conseiller", "Allocataire", "Administrateur", "Inspecteur", "stagiaire",
                "Maître - assistant", "Attaché"]
    ListOrga = ["Université", "Institut", "CNRS", "C.N.R.S", "Scientifique" "Laboratoire", "UMR", "ENS", "E.N.S",
                "Ecole", "University", "Institute", "Department", "Direction", "Mission", "Equipe",
                "Assistant", "School", "Orstom", "ORSTOM", "INRA", "Lycée", "Collège", "Unité", "Faculté",
                "Communauté", "Universidad", "Universidade", "Comité", "Groupe", "Station", "UFR", "Maison"]

    if doc.DocReferenceRef.type == "article":
        nomfichierencours = doc.DocReferenceRef.TextRef
        addressedocencours = GetAdresseCompletDoc(nomfichierencours)
        tree = etree.parse(addressedocencours.replace("tei", "erudit"))
        MotsPageLigneEnCours = DocMotPageLigne(addressedocencours)
        RechercheNoteBio = tree.xpath(
            "/erudit:article/erudit:corps/erudit:texte/erudit:page/erudit:segment[@typesegment='notebio']",
            namespaces={"erudit": "http://www.erudit.org/xsd/article"})

        ResultIndTemp = ['<a href="https://www.persee.fr/doc/' +
                     nomfichierencours[8:-8] + '">' + nomfichierencours[8:-8] + '</a>']
        ResultIndTest = []

        # Test s'il y a une note bio dans l'article

        if len(RechercheNoteBio) == 0:

            listnomauteurs = tree.xpath(
                "/erudit:article/erudit:liminaire/erudit:grauteur//erudit:auteur/erudit:nompers/erudit:nomfamille",
                namespaces={"erudit": "http://www.erudit.org/xsd/article"})

            listprenomauteurs = tree.xpath(
                "/erudit:article/erudit:liminaire/erudit:grauteur//erudit:auteur/erudit:nompers/erudit:prenom",
                namespaces={"erudit": "http://www.erudit.org/xsd/article"})

            listauteurnoms = []
            for nomaut in listnomauteurs:
                listauteurnoms.append(nomaut.text)
            listauteurprenoms = []
            for prenomaut in listprenomauteurs:
                listauteurprenoms.append(prenomaut.text)

            listepage = tree.xpath("/erudit:article/erudit:corps/erudit:texte/erudit:page",
                                   namespaces={"erudit": "http://www.erudit.org/xsd/article"})

            # Test sur la première et la dernière page s'il y a une note bio
            for i_page in [1, len(listepage)]:

                RechercheBibliosSurPage = tree.xpath("/erudit:article/erudit:corps/erudit:texte/erudit:page[" + \
                                                     str(i_page) + "]/erudit:segment[@typesegment='biblio']",
                                                     namespaces={"erudit": "http://www.erudit.org/xsd/article"})

                ListCoordGraphBiblios = []

                if len(RechercheBibliosSurPage) != 0:

                    for biblio in RechercheBibliosSurPage:
                        coordx = biblio.attrib['coordx']
                        coordy = biblio.attrib['coordy']
                        dimx = biblio.attrib['dimx']
                        dimy = biblio.attrib['dimy']

                        left = int(coordx) * 2
                        top = int(coordy) * 2
                        right = left + int(dimx) * 2
                        bottom = top + int(dimy) * 2

                        ListCoordGraphBiblios.append((left, top, right, bottom))

                RechercheNotesSurPage = tree.xpath(
                    "/erudit:article/erudit:corps/erudit:texte/erudit:page[" + \
                    str(i_page) + "]/erudit:segment[@typesegment='note']",
                    namespaces={"erudit": "http://www.erudit.org/xsd/article"})

                ListCoordGraphNotes = []

                if len(RechercheNotesSurPage) != 0:

                    for note in RechercheNotesSurPage:
                        coordx = note.attrib['coordx']
                        coordy = note.attrib['coordy']
                        dimx = note.attrib['dimx']
                        dimy = note.attrib['dimy']

                        left = int(coordx) * 2
                        top = int(coordy) * 2
                        right = left + int(dimx) * 2
                        bottom = top + int(dimy) * 2

                        ListCoordGraphNotes.append((left, top, right, bottom))

                # Récupération des lignes sous un format plus adéquate et mediane centre
                EnsLigne = []
                Ligne = []

                for i, mot in enumerate(MotsPageLigneEnCours[i_page]):
                    if i == 0:
                        Ligne.append(mot)
                    else:
                        if mot[5] == "s":
                            Ligne.append(mot)
                        else:
                            EnsLigne.append(Ligne)
                            Ligne = [mot]

                LigneAvcNomOuPrenomNotBiblio = []
                for i, Ligne in enumerate(EnsLigne):

                    # test si ligne appartient à fenêtre biblio

                    PresenceBiblio = False
                    DicoResultBiblio = {}
                    PresenceNote = False
                    DicoResultNote = {}
                    for mot in Ligne:

                        for j, CoordBiblio in enumerate(ListCoordGraphBiblios):
                            # Si le mot est situé dans la fenêtre graphique
                            if int(mot[1]) >= CoordBiblio[0] and int(mot[1]) <= CoordBiblio[2] and \
                                            int(mot[2]) >= CoordBiblio[1] and int(mot[2]) <= CoordBiblio[3] and \
                                            int(mot[3]) >= CoordBiblio[0] and int(mot[3]) <= CoordBiblio[2] and \
                                            int(mot[4]) >= CoordBiblio[1] and int(mot[4]) <= CoordBiblio[3]:
                                if j in DicoResultBiblio:
                                    DicoResultBiblio[j] += 1
                                else:
                                    DicoResultBiblio[j] = 1

                        for j, CoordBiblio in enumerate(ListCoordGraphNotes):
                            # Si le mot est situé dans la fenêtre graphique
                            if int(mot[1]) >= CoordBiblio[0] and int(mot[1]) <= CoordBiblio[2] and \
                                            int(mot[2]) >= CoordBiblio[1] and int(mot[2]) <= CoordBiblio[3] and \
                                            int(mot[3]) >= CoordBiblio[0] and int(mot[3]) <= CoordBiblio[2] and \
                                            int(mot[4]) >= CoordBiblio[1] and int(mot[4]) <= CoordBiblio[3]:
                                if j in DicoResultNote:
                                    DicoResultNote[j] += 1
                                else:
                                    DicoResultNote[j] = 1

                    for k, v in DicoResultBiblio.items():
                        if v == len(Ligne):
                            PresenceBiblio = True
                            break

                    for k, v in DicoResultNote.items():
                        if v == len(Ligne):
                            PresenceNote = True
                            break

                    if not PresenceBiblio and not PresenceNote:

                        for mot in Ligne:

                            # test nom et prénom
                            PresenceNom = False

                            for nom in listauteurnoms:
                                if str_compare(mot[0], nom) > 0.9:
                                    PresenceNom = True
                                    if i not in LigneAvcNomOuPrenomNotBiblio:
                                        LigneAvcNomOuPrenomNotBiblio.append(i)
                                    break

                            if not PresenceNom:
                                for prenom in listauteurprenoms:
                                    if str_compare(mot[0], prenom) > 0.9:
                                        if i not in LigneAvcNomOuPrenomNotBiblio:
                                            LigneAvcNomOuPrenomNotBiblio.append(i)
                                        break

                NbreLignes = len(EnsLigne)
                if len(LigneAvcNomOuPrenomNotBiblio) != 0:
                    for numeroligne in LigneAvcNomOuPrenomNotBiblio:
                        if numeroligne != NbreLignes - 1:
                            for mot in EnsLigne[numeroligne + 1]:
                                PresenceGrad = False
                                for grad in ListGrad:
                                    if str_compare(mot[0], grad) > 0.9:
                                        if numeroligne not in ResultIndTest:
                                            if i_page == 1:
                                                ResultIndTemp.append("Première page / ligne : " + str(numeroligne + 1))
                                                ResultIndTest.append(numeroligne)
                                            else:
                                                ResultIndTemp.append(" Dernière page / ligne : " + str(numeroligne + 1))
                                                ResultIndTest.append(numeroligne)

                                        PresenceGrad = True
                                        break

                                if not PresenceGrad:
                                    for orga in ListOrga:
                                        if str_compare(mot[0], orga) > 0.9:
                                            if [nomfichierencours, numeroligne] not in ResultIndTest:
                                                if i_page == 1:
                                                    ResultIndTemp.append("Première page / ligne : " + str(numeroligne + 1))
                                                    ResultIndTest.append(numeroligne)
                                                else:
                                                    ResultIndTemp.append(" Dernière page / ligne : " + str(numeroligne + 1))
                                                    ResultIndTest.append(numeroligne)
                                            break

        if len(ResultIndTemp) != 1:
            ResultInd = ResultIndTemp

    return ResultInd



def RechercheNoteBioDo(FichierResult, reduction, revue):

    error, Result, NbreResult = TrameGenerale(FichierResult, reduction, revue, RechercheNoteBioSpe,
                                              EcritureResultIllimit, LectureResultIllimit,
                                              listinsert=["Lien vers le document où une note bibliographique non documentée est suspectée",
                                                          "Première ou derrnière page / numéro de ligne"])

    return error, Result, NbreResult

