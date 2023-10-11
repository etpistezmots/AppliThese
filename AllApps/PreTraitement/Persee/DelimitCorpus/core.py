from django.conf import settings
import os,re, shutil
from .outils.xpath import DocRequete, DocMot
from .outils.specific import NombrePage
from pandas import DataFrame, concat
from difflib import SequenceMatcher
from .models import Revue, DocReference, Auteur, CorpusEtude, DocExtractInitial
from lxml import etree

#################  ENSEMBLE DES FONCTIONS D'EXPLORATION ###############

def ExplicitRevue(revue):
    ''' Fonction outil pour les fonctions ci-dessous'''
    error = False
    revuerealname = ""
    autrerevue = ""
    if revue == "geo":
        revuerealname = "Les Annales de Géographie"
        autrerevue = "spgeo"
    elif revue == "spgeo":
        revuerealname = "L'Espace géographique"
        autrerevue = "geo"
    else:
        error = True

    return error, revuerealname, autrerevue


def GeneralFonction(FctSpeCreate, FctSpeRecup, revue, intitule, sortedresult=False, ncomplex=False):
    dossierref = settings.DATA_DIR + "/revues/" + revue
    FichierResult = settings.RESULT_PRETRAIT_DIR + "/DelimitCorpus/" + intitule + revue + ".txt"


    # cree le dossier si n'existe pas
    dossier = FichierResult.rsplit("/", 1)[0]
    if not os.path.exists(dossier):
        os.makedirs(dossier)

    # si n'existe pas, enregistre le résultat
    if not os.path.isfile(FichierResult):
        Result = FctSpeCreate(FichierResult, dossierref)
    else:
        if not ncomplex:
            Result = FctSpeRecup(FichierResult)
        else:
            Result = FctSpeRecup(FichierResult, ncomplex)

    NbreResult = len(Result)

    if sortedresult:
        return NbreResult, sorted(Result)
    else:
        return NbreResult, Result


def EcritureResultSimple(FichierResult, Result):
    with open(FichierResult, 'w') as f:
        for SsResult in Result:
            f.write(SsResult + "\n")


def FctSpeRecupResultSimple(FichierResult):
    with open(FichierResult, 'r') as f:
        Result = f.readlines()
    return Result


def FctSpeCreateNumero(FichierResult, dossierref):
    Result = []
    for ssdossier in os.listdir(dossierref):
        Result.append(ssdossier)
    EcritureResultSimple(FichierResult, Result)
    return Result


def FctSpeCreateDocument(FichierResult, dossierref):
    Result = []
    for ssdossier in sorted(os.listdir(dossierref)):
        for fichier in sorted(os.listdir(dossierref + os.path.sep + ssdossier + os.path.sep + "tei")):
            Result.append(fichier)
    EcritureResultSimple(FichierResult, Result)
    return Result


def FctSpeCreateDocHorsNorme(FichierResult, dossierref):
    Result = []
    revue = dossierref.split("/")[-1]
    regex = "article_" + revue + "_[0-9]{4}-[0-9]{4}_[0-9]{4}_num_[0-9]{1,4}_[0-9]{1,4}_[0-9]{1,8}_tei\.xml"
    for ssdossier in sorted(os.listdir(dossierref)):
        for fichier in sorted(os.listdir(dossierref + os.path.sep + ssdossier + os.path.sep + "tei")):
            if re.match(regex, fichier) is None:
                Result.append(fichier)
    EcritureResultSimple(FichierResult, Result)
    return Result


def FctSpeCreateTypeDocArticle(FichierResult, dossierref):
    Result = []
    for ssdossier in sorted(os.listdir(dossierref)):
        for fichier in sorted(os.listdir(dossierref + os.path.sep + ssdossier + os.path.sep + "tei")):
            if fichier[0:7] == "article":
                XpathType = "/tei:TEI/tei:teiHeader/@type"
                AdresseCompletDoc = os.path.join(os.path.sep, dossierref, ssdossier, 'tei', fichier)
                DocType = DocRequete(AdresseCompletDoc, XpathType, "type", "j")
                if DocType.type not in Result:
                    Result.append(DocType.type)
    EcritureResultSimple(FichierResult, Result)
    return Result


def FctSpeCreateLangArticle(FichierResult, dossierref):
    Result = []
    for ssdossier in sorted(os.listdir(dossierref)):
        for fichier in sorted(os.listdir(dossierref + os.path.sep + ssdossier + os.path.sep + "tei")):
            if fichier[0:7] == "article":
                XpathType = "/tei:TEI/tei:teiHeader/@type"
                XpathLangue = "/tei:TEI/tei:teiHeader/tei:profileDesc/tei:langUsage/tei:language/text()"
                AdresseCompletDoc = os.path.join(os.path.sep, dossierref, ssdossier, 'tei', fichier)
                DocTypeCatPage = DocRequete(AdresseCompletDoc,
                                            [XpathType, XpathLangue],
                                            ["type", "langue"],
                                            ["j", "j"])
                if DocTypeCatPage.type == "article" and DocTypeCatPage.langue not in Result:
                    Result.append(DocTypeCatPage.langue)
    EcritureResultSimple(FichierResult, Result)
    return Result


def EcritureResultComplex(FichierResult, Result, n):
    with open(FichierResult, 'w') as f:
        for SsResult in Result:
            for i in range(n):
                f.write(SsResult[i] + "\n")
            f.write("\n")


def FctSpeRecupResultComplexe(FichierResult, n):
    Result = []
    with open(FichierResult, 'r') as f:
        content = f.readlines()
        SsResult = []
        for i, elt in enumerate(content):
            if ((i + 1) % (n + 1) != 0):
                SsResult.append(elt)
            else:
                Result.append(SsResult)
                SsResult = []
    return Result


def FctSpeCreateArticleVide(FichierResult, dossierref):
    Result = []
    for ssdossier in sorted(os.listdir(dossierref)):
        for fichier in sorted(os.listdir(dossierref + os.path.sep + ssdossier + os.path.sep + "tei")):
            if fichier[0:7] == "article":
                XpathType = "/tei:TEI/tei:teiHeader/@type"
                AdresseCompletDoc = os.path.join(os.path.sep, dossierref, ssdossier, 'tei', fichier)
                DocType = DocRequete(AdresseCompletDoc, XpathType, "type", "j")

                # On filtre que les articles ici
                # car choix de recherche de ne pas travailler sur les autres types
                if DocType.type == "article":

                    # Fonction qui récupère les mots !
                    Touslesmotsdoc = DocMot(AdresseCompletDoc)

                    # Si ça a récupéré aucun mots
                    if len(Touslesmotsdoc) == 0:
                        # on récupère des infos pour les afficher :
                        Xpathtitre = "/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title[@level='a' and @type='main']//text()"
                        Xpathauteur = "/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:respStmt/tei:name/text()"
                        Xpathpage = "/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:monogr/tei:imprint/tei:biblScope[@unit='pages']/text()"
                        DocTitreAutPage = DocRequete(AdresseCompletDoc,
                                                     [Xpathtitre, Xpathauteur, Xpathpage],
                                                     ["titre", "auteur", "page"],
                                                     ["j", "d", "j"]
                                                     )
                        Result.append([fichier, DocTitreAutPage.titre, str(DocTitreAutPage.auteur),
                                       str(NombrePage(DocTitreAutPage.page))])
    EcritureResultComplex(FichierResult, Result, 4)
    return Result


def FctSpeCreateCategArticle(FichierResult, dossierref, mode):
    RefCategorie = []
    RefPage = []

    for ssdossier in sorted(os.listdir(dossierref)):
        for fichier in sorted(os.listdir(dossierref + os.path.sep + ssdossier + os.path.sep + "tei")):
            if fichier[0:7] == "article":
                XpathType = "/tei:TEI/tei:teiHeader/@type"
                XpathCategorie = "/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:analytic/tei:title[@type='part']/text()"
                Xpathpage = "/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:monogr/tei:imprint/tei:biblScope[@unit='pages']/text()"
                AdresseCompletDoc = os.path.join(os.path.sep, dossierref, ssdossier, 'tei', fichier)
                DocTypeCatPage = DocRequete(
                    AdresseCompletDoc,
                    [XpathType, XpathCategorie, Xpathpage],
                    ["type", "categorie", "page"],
                    ["j", "j", "j"]
                )
                if DocTypeCatPage.type == "article":
                    # Si pas de catégorie, le rend plus lisible
                    if DocTypeCatPage.categorie == "":
                        DocTypeCatPage.categorie = "Pas de catégorie"

                    # Si une catégorie ressemble à 90 % à une déjà existante, très probabalement la même
                    # Evite des doublons pour des petites différence d'écritures
                    if mode != "brut":
                        for CatExist in RefCategorie:
                            if SequenceMatcher(None, DocTypeCatPage.categorie, CatExist).ratio() > 0.90:
                                DocTypeCatPage.categorie = CatExist

                    RefCategorie.append(DocTypeCatPage.categorie)

                    # ici, la fonction NombrePage transforme juste les pages marquée en nombre:
                    # ex : 15-18  --> 3
                    RefPage.append(NombrePage(DocTypeCatPage.page))

    # crée un dico avec tous les informations récupérées
    d = dict(Categorie=RefCategorie, Page=RefPage)
    # crée un dataframe à partir du dico pour manipuler les infos
    df = DataFrame(d)
    # va regrouper les catégories ensemble et sommer sur le nombre de page
    grouped = df['Page'].groupby(df['Categorie'])
    # permet de créer un tableau avec à la fois la moyenne et la médianne
    CatMoyMed = concat([grouped.count(), grouped.mean().round(1), grouped.median()], axis=1)
    # Permet de renommer les colonnes
    CatMoyMed.columns = ["Nombre article", "Moyenne page", "Médiane page"]
    CatMoyMed.to_csv(FichierResult)

    return CatMoyMed


######################   CREATION CORPUS ETUDE ##########################


def SelectReducFctUser(request, ReducAll):
    "selectionne les réductions a afficher en focntion de l'utilisateur"
    Reducselect = []
    # si l'utilisateur n'est pas connecté, alors tous les modèles publics
    # c'est à dire avec user_restric = 0
    if request.user.id is None:
        for elt in ReducAll:
            if elt.user_restrict == "0":
                Reducselect.append(elt)
    # si l'utisateur est connecté
    else:
        # si c'est un superutilisateur, affiche tous les modèles :
        if request.user.is_superuser:
            Reducselect = list(ReducAll)
        # sinon affiche que les publics et ceux correspondant à son numéro
        else:
            for elt in ReducAll:
                if elt.user_restrict == "0" or (str(request.user.id) in elt.user_restrict.split(",")):
                    Reducselect.append(elt)
    return Reducselect


def SelectLastFctUser(ReducSelect):
    "selectionne la dernière réduction focntion de l'utilisateur"
    LastReduc = ("", 0)
    for elt in ReducSelect:
        if elt.id > LastReduc[1]:
            LastReduc = (elt.nom, elt.id)
    return LastReduc[0]



def DoReduction(donnees,VNEnCours):

    result_revue = donnees["revue"].split(',')
    result_stopworddossier = donnees["stopworddossier"].split(',')
    result_typedoc = donnees["typedoc"].split(',')
    result_langues = donnees["langue"].split(',')
    result_typecatnon = donnees["typecatnon"].split('*')
    result_extract_mot = donnees["extract_mot"]

    AdresseResult = settings.RESULT_PRETRAIT_DIR + "/DelimitText/ExtractBase/" + donnees["nom"]
    # si une extraction avec même nom déjà existante, l'efface et la remplace !
    if os.path.exists(AdresseResult):
        shutil.rmtree(AdresseResult)
    os.makedirs(AdresseResult)

    for revueencours in result_revue:

        dossierref = settings.DATA_DIR + "/revues/" + revueencours
        ResultDossier = []

        # 1) Travail sur les stopword Dossier
        for dossier in os.listdir(dossierref):
            MarqueurPresence = False

            # Test pour chaque élément car il peut y en avoir plusieurs !
            for elt in result_stopworddossier:
                # Attention cas où l'utilisateur a rien mis elt==""
                if elt != "" and elt in dossier:
                    MarqueurPresence = True

            # Si rien a été détecté, garde le dossier
            if MarqueurPresence == False:
                ResultDossier.append(dossier)

        # 2) Descend au niveau des fichiers

        for dossier in sorted(ResultDossier):
            for fichier in sorted(os.listdir(dossierref + os.path.sep + dossier + os.path.sep + "tei")):

                XpathType = "/tei:TEI/tei:teiHeader/@type"
                XpathCategorie = "/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:analytic/tei:title[@type='part']/text()"
                XpathPage = "/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:monogr/tei:imprint/tei:biblScope[@unit='pages']/text()"
                XpathDate = "/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:monogr/tei:imprint/tei:date/text()"
                XpathLangue = "/tei:TEI/tei:teiHeader/tei:profileDesc/tei:langUsage/tei:language/text()"
                XpathTitre = "/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title[@level='a' and @type='main']//text()"
                XpathURL = "//tei:teiHeader/tei:fileDesc/tei:publicationStmt/tei:idno[@type='URL']//text()"
                AdresseCompletDoc = os.path.join(os.path.sep, dossierref, dossier, 'tei', fichier)

                Metadata = DocRequete(
                    AdresseCompletDoc,
                    [XpathType, XpathCategorie, XpathPage, XpathDate, XpathLangue, XpathTitre, XpathURL],
                    ["type", "categorie", "page", "date", "langue", "titre", "url"],
                    ["j", "j", "j", "j", "j", "j", "j"])

                if (result_typedoc == ["All"] or Metadata.type in result_typedoc) \
                        and int(Metadata.date) >= donnees["datemin"] and int(Metadata.date) <= donnees[
                    "datemax"] \
                        and (result_langues == ['All'] or Metadata.langue in result_langues) \
                        and (result_typecatnon == [''] or Metadata.categorie not in result_typecatnon) \
                        and NombrePage(Metadata.page) >= donnees["pagemin"]:

                    # Attention si ajout d'une nouvelle méthode d'extaction des mots,
                    # il faudrait des équivalents des fonctions DocMot, DocLigne, DocPage
                    # et nécessiterait de faire des adaptations dans AmeliorText
                    if result_extract_mot == "FromTEIDocMot":
                        # Extraction des mots
                        Touslesmotsdoc = DocMot(AdresseCompletDoc)

                        if len(Touslesmotsdoc) > donnees["motmin"]:
                            # enregistrement fichier txt brut (sans transformation)
                            NomFin = fichier.split("_tei")[0] + ".txt"
                            AdresseFin = AdresseResult + '/' + NomFin
                            with open(AdresseFin, "w+") as f:
                                f.write(" ".join(Touslesmotsdoc))

                            # Ajout d'un doc extrait
                            DocReferenceEnCours = DocReference.objects.filter(TextRef=fichier)[0]
                            NewDocExtract = DocExtractInitial(DocReferenceRef=DocReferenceEnCours,
                                                              CorpusEtudeRef=VNEnCours,
                                                              TextExtract=DocReferenceEnCours.TextRef[
                                                                          :-8] + ".txt")
                            NewDocExtract.save()




#################  ENSEMBLE DES FONCTIONS D'INSERTION DANS LA BASE DE DONNEE ###############


def InsertMesDonneesPersee():
    '''Insertion revues de mon corpus : Annales et Espace
                  doc brut : tous les documents Perser de ces deux revues
                  auteurs de ces documents'''

    # cree mes deux revues dans la base de donnée (voir fct ci dessous InsertRevue)
    # le nom persée est l'abbreviation utilisée par cet organisme pour chaque revue
    # nom qui se retrouve dans url, dans les noms des docs
    InsertRevue('Annales','geo')
    InsertRevue('Espace', 'spgeo')
    print("Revues Annales et Espace Géo insérées")

    # creer mes docs bruts
    InsertDocs("spgeo")
    InsertDocs("geo")
    print("Docs Bruts Annales et Espace Géo créés")

    # Creer mes auteurs
    InsertAuteursNew("spgeo")
    InsertAuteursNew("geo")
    print("Auteurs créés")


    # lien docbrut-auteur
    InsertDocReferenceAuteur("spgeo")
    InsertDocReferenceAuteur("geo")
    print("Liens DocReference-Auteur effectué")


def InsertRevue(nomref, nomperseeref):
    NewRevue = Revue(nom=nomref,nompersee=nomperseeref)
    NewRevue.save()

def InsertDocs(nomperseeref):

    # recupère l'instance de la revue dans la base de donnée
    RevueDansBD = Revue.objects.get(nompersee=nomperseeref)
    # Chemin où sont rangés les données de la revue
    NomduCheminRevue = settings.DATA_DIR + "/revues/" + nomperseeref

    # récupère tous les docs bruts en itérant dans les dossiers (numéros de la revue)
    DocsBrutsNewRevue = []
    for dossier in os.listdir(NomduCheminRevue):
        for fichier in os.listdir(os.path.join(NomduCheminRevue, dossier, "tei")):
            DocsBrutsNewRevue.append(fichier)

    # tri car permet un ordre plus logique pour insertion dans la BD
    DocsBrutsNewRevue.sort()


    for docbrut in DocsBrutsNewRevue:
        # pour récupérer adresse du doc à partir de son nom
        NomCheminDocReference = GetAdresseCompletDoc(docbrut)
        # requête avec //
        # pour prendre en compte cas particulier : syntaxe intiale un peu différente
        # ex teiCorpus : /home/max/Bureau/PerseeV3/Data/Revues/geo/geo_0003-4010_1892_bib_1_5/tei/corpus_geo_0003-4010_1892_bib_1_5_teiCorpus.xml
        XpathDate = "//tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:monogr/tei:imprint/tei:date//text()"
        XpathURL = "//tei:teiHeader/tei:fileDesc/tei:publicationStmt/tei:idno[@type='URL']//text()"
        XpathType = "//tei:teiHeader/@type"
        XpathTitre = "//tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title[@level='a' and @type='main']//text()"


        tree = etree.parse(NomCheminDocReference)
        date = tree.xpath(XpathDate,namespaces={"tei": "http://www.tei-c.org/ns/1.0"})[0]
        url = tree.xpath(XpathURL,namespaces={"tei": "http://www.tei-c.org/ns/1.0"})[0]
        type = tree.xpath(XpathType,namespaces={"tei": "http://www.tei-c.org/ns/1.0"})[0]
        # exception car cas où il n'y a pas de titre
        # et cas où le titre est en plusieurs parties
        testtitre = tree.xpath(XpathTitre,namespaces={"tei": "http://www.tei-c.org/ns/1.0"})
        titre = " ".join(testtitre)
        # verification des conditions pour entrer dans la base
        # voir max_length dans modele
        # possible d'en faire facilement une fonction !
        if len(url)>250:
            print("alert url")
            print(docbrut)
            print(len(url))
        if len(titre)>550:
            print("alert titre")
            print(docbrut)
            print(len(titre))
        if len(docbrut)>150:
            print("alert docbrut")
            print(docbrut)
            print(len(docbrut))

        NewDocReference = DocReference(titre=titre,url=url,TextRef=docbrut,type=type,annee=date,
                                       RevueRef=RevueDansBD)
        NewDocReference.save()


def GetAdresseCompletDoc(doc):
    path = settings.DATA_DIR + "/revues"
    groupe = doc.split('_')
    dossier = '_'.join(groupe[1:7])
    revue = groupe[1]
    AdresseCompletDoc = os.path.join(os.path.sep, path, revue, dossier, 'tei', doc)
    return AdresseCompletDoc



def InsertAuteursNew(nomperseeref):
    AuteursIndiDejaPresents = Auteur.objects.filter(type="person").values_list('idpersee', flat=True)
    # renvoie liste auteur pas dans la base (voir fonction ci dessous)
    list_author_persons = GetAuthor(settings.DATA_DIR + "/PersonnesTripleStore/PERSEE_" + nomperseeref + "_persons_2017-01-06.rdf", AuteursIndiDejaPresents)
    # Insertion de cette liste d'auteurs
    for author in list_author_persons:
        AuteurASauver = Auteur(nom=author["Nom"], prenom=author["Prenom"], type="person", idpersee=author["IdPersee"])
        AuteurASauver.save()


def GetAuthor(filename, author_in_bdd):
    """ Fonction qui permet d'extraire les données relatives aux auteurs (noms, prénoms,idpersee)
     à partir d'un fichier balisé de type "persons".
     La valeur retournée est la liste des auteurs qui ne figurent pas dans la base de données.

    Args:
        filename (str): Chemin absolu du fichier.
        author_in_bdd (list of str): Liste des auteurs déjà présents dans la base de données.
        origine_import (str): chaine de caractère indiquant la provenance du fichier (Persée, Cairn, ...)

    Return:
        liste_author (list of dict): Liste d'auteurs. Chaque élément de la liste est un dictionnaire.
                        dict: {'Nom':
                               'Prenom':
                               'IdPersee':
                            }
    """
    liste_author= []
    tree = etree.parse(filename)
    for i, mot in enumerate(tree.xpath("/rdf:RDF/foaf:Person", namespaces={"rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","foaf":"http://xmlns.com/foaf/0.1/","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}), 1):
        ref = tree.xpath("/rdf:RDF/foaf:Person[" + str(i) + "]/@rdf:about", namespaces={"rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","foaf":"http://xmlns.com/foaf/0.1/"})

        ref2 = ref[0].split("/", 4)[4].rsplit("#", 1)[0]


        prenom = tree.xpath("/rdf:RDF/foaf:Person[" + str(i) + "]/foaf:givenName", namespaces={"rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","foaf":"http://xmlns.com/foaf/0.1/"})
        if prenom[0].text is not None:
            prenom2 = prenom[0].text.replace("'", " ")
        else:
            prenom2=""

        nom = tree.xpath("/rdf:RDF/foaf:Person[" + str(i) + "]/foaf:familyName", namespaces={"rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","foaf":"http://xmlns.com/foaf/0.1/"})
        nom2 = nom[0].text.replace("'", " ")

        if ref2 in author_in_bdd:
            print("{}: Auteur déjà présent dans la base de données".format(nom2))
        else:
            liste_author.append({'Nom':nom2,
                                 'Prenom':prenom2,
                                 'IdPersee':ref2
                                 })
    return liste_author


def InsertDocReferenceAuteur(nomperseeref):
    tree = etree.parse(settings.DATA_DIR + "/DocsTripleStore/PERSEE_" + nomperseeref + "_doc_2017-01-09.rdf")
    NomduCheminRevue = settings.DATA_DIR + "/revues/" + nomperseeref
    for dossier in os.listdir(NomduCheminRevue):
        for fichier in os.listdir(os.path.join(NomduCheminRevue, dossier, "tei")):
            refarticlerdf = "http://data.persee.fr/doc/" + fichier.split("_", 1)[1].rsplit("_", 1)[0] + "#Web"
            listauteurs = tree.xpath("bibo:Document[@rdf:about = '" + refarticlerdf + "']/marcrel:aut/@rdf:resource", namespaces={"rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "bibo": "http://purl.org/ontology/bibo/", "marcrel": "http://id.loc.gov/vocabulary/relators/"})
            for auteur in listauteurs:
                if auteur != "http://data.persee.fr/person/#Person":
                    refauteur = auteur.split("/", 4)[4].rsplit("#", 1)[0]
                    docbrutref = DocReference.objects.get(TextRef=fichier)
                    auteursaveref = Auteur.objects.get(idpersee=refauteur)
                    docbrutref.AuteursRef.add(auteursaveref)
                # cas auteur collectif
                else:
                    IdAuteursArticle = []
                    tree2 = etree.parse(os.path.join(NomduCheminRevue, dossier, "tei", fichier))
                    InfoAuteur = tree2.xpath('/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:respStmt/tei:name',
                                            namespaces={"tei": "http://www.tei-c.org/ns/1.0"})
                    # si oui, le(s) sauve dans la base
                    # puis même processus que précedemment
                    for auteur in InfoAuteur:
                        AuteurCollectifDejaPresents = Auteur.objects.filter(type="org").values_list('nom',
                                                                                                         flat=True)
                        if auteur.text in AuteurCollectifDejaPresents:
                            IdBdCetAuteur = Auteur.objects.get(nom=auteur.text).id
                            IdAuteursArticle.append(IdBdCetAuteur)
                        else:
                            AuteurASauver = Auteur(nom=auteur.text, prenom="", type="org", idpersee="")
                            AuteurASauver.save()
                            IdAuteursArticle.append(AuteurASauver.id)

                    # complete la base auteur-doc !
                    docbrutref = DocReference.objects.get(TextRef=fichier)
                    for idauteur in IdAuteursArticle:
                        auteursaveref = Auteur.objects.get(id=idauteur)
                        docbrutref.AuteursRef.add(auteursaveref)
