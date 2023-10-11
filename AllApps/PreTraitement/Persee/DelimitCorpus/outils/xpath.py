from lxml import etree

class DocRequete(object):
    """ Permet d'effectuer une requête sur un document xml.

    Attributs:
        doc     (str): Liste des noms des documents de la BDD (chemin absolu complet)
        xpath   (str): formule de requête sans le namespace
        label   (str): élément recherché (ex: titre, langue, etc. ...)
        mode    (str): Soit "j" comme joint, soit "d" comme disjoint.
                        "j": ["La France", "depuis 1891"]  --> "La France depuis 1891"
                        "d": ["La France", "depuis 1891"] reste sous forme de liste

    Notes:  Dans le cas de requêtes multiples
         avec plusieurs xpaths sous forme de listes de xpaths et de labels.
         Dans ce dernier cas :
         xpath = [xpath1, xpath2,....]
         label = [label1, label2,...]
         mode = [mode1, mode2,...]
         Dans ce cas, bien vérifier que les trois listes ont bien le même nombre d'éléments
         Après, il suffit d'interroger DocRequete.label(voulu) pour avoir le résultat

    """

    def __init__(self, doc, xpath, label, mode):

        if isinstance(xpath, str) and isinstance(label, str) and isinstance(mode, str):
            tree = etree.parse(doc)
            listelabel = tree.xpath(xpath, namespaces={"tei": "http://www.tei-c.org/ns/1.0"})

        # https://stackoverflow.com/questions/8028708/dynamically-set-local-variable
            if mode == "j":
                setattr(DocRequete, label, " ".join(listelabel))
            if mode == "d":
                setattr(DocRequete, label, listelabel)
        else:
            # Ici, pas de test si
            if not isinstance(xpath, str) and not isinstance(label , str) and not isinstance(mode , str) \
                    and len(xpath) == len(label) and len(label)==len(mode):
                tree = etree.parse(doc)
                for i in range(len(xpath)):
                    listelabel = tree.xpath(xpath[i], namespaces={"tei": "http://www.tei-c.org/ns/1.0"})
                    if mode[i] == "j":
                        setattr(DocRequete, label[i], " ".join(listelabel))
                    if mode[i] == "d":
                        setattr(DocRequete, label[i], listelabel)


def ExtractMot(elt, detail):
    if detail:
        gauche = elt.attrib["left"]
        haut = elt.attrib["top"]
        droite = elt.attrib["right"]
        bas = elt.attrib["bottom"]
        return (elt.text, gauche, haut, droite, bas)
    else:
        return elt.text



def DocMot(document, detail=False):
    """ Permet de renvoyer la liste de tous les mots non nuls
    Renvoie par défault (detail= False) les mots sous forme d'une liste
    Avec detail = True
    Renvoie sous forme d'une liste de tuple avec position graphique:
    [(Mot1, gauche, haut, bas, droite), (Mot2,....)]

    Args:
        document (str)  : chemin absolu du document
        detail (boolean):
                            True: Renvoie sous forme d'une liste de tuple avec position graphique:
                                    [(Mot1, gauche, haut, bas, droite), (Mot2,....)]
                            False: Renvoie sous forme d'une liste de mots

    Notes: Attention, certains mots peuvent être répété deux fois comme pour les biblios
    du fait du format de Persée. Pb si on essaye d'exlure ces mots car
    il existe bibliographie sur plusieurs pages avec des mots qui ne sont pas répétés
    La solution est de traiter ces mots doubles par la suite suivant ce qu'on veut :
    garder ou non les bibliographie

    Output:
        mots (list of (str ou tuples)): liste de mots ou de tuples si detail=True
    """

    mots = []

    tree = etree.parse(document)

    eltbase = tree.xpath("/tei:TEI/tei:text/tei:body", namespaces={"tei": "http://www.tei-c.org/ns/1.0"})


    # itération sur les enfants de body avec tri sur les tags trouvés
    # on exclue les tags note :
    # répétitions qu'il n'est pas utile d'avoir en double
    for elt1 in eltbase[0].iterchildren(tag=("{http://www.tei-c.org/ns/1.0}div", "{http://www.tei-c.org/ns/1.0}p")):

        # si c'est un paragraphe :
        if elt1.tag == "{http://www.tei-c.org/ns/1.0}p":
            # récupère les mots non nuls
            for elt2 in elt1.iterchildren(tag="word"):
                if elt2.text is not None:
                    # alimente la liste de mots qui va être retourné
                    # en fonction de l'option
                    mots.append(ExtractMot(elt2, detail))

        # Inclu type "bibl" et appxdiv" :
        # pb si on exclu biblio car existe bibliographie sur plusieurs pages : on perd des mots qui ne sont pas répétés
        # change le comptage des mots et il faudra plus en enlever au moment traitement biblio et appxdiv
        if elt1.tag == "{http://www.tei-c.org/ns/1.0}div":

            # voir ci dessous
            # permet de régler le cas double des "./word" et "./p/word
            for elt2 in elt1.findall(".//word"):
                if elt2.text is not None:
                    # alimente la liste de mots qui va être retourné
                    # en fonction de l'option
                    mots.append(ExtractMot(elt2, detail))

    return mots


def DocMotLigne(document, seuilsautligne=50, seuilsautPage=2000):
    """
        Renvoie en plus les sauts de lignes détecté par rapport à seuilsautligne
        Par defaut égal à 50 mais possibilité de le faire varier suivant les revues ou le travail effectué
        Se trouve après les coordonnées graphique du mot
        'n' pour new : c'est le début d'une nouvelle ligne
        's' pour same : la ligne continue
        Ex : avec début de ligne sur Max et Université
            ('Max', '2282', '1396', '2472', '1450', 'n'),
            ('Beligné', '2510', '1396', '2886', '1450', 's'),
            ('Université', '2220', '1499', '2425', '1530', 'n'),
            ('de', '2447', '1499', '2492', '1530', 's'),
            ('Lyon', '2514', '1498', '2882', '1530', 's'),
        Plus globalement, les résultats sont stockés comme la fonction précédente
        c'est à dire sous forme d'un liste :
            [mot1, mot2,....],

        Args : document (str)       : adresse complète du doc
               seuilsautLigne (int) : en option si besoin (seuil à partir duquel considère saut Ligne)
               seuilsautPage (int)  : en option si besoin (seuil à partir duquel considère saut Page)

        Return : list of tuple : la nouvelle donnée est en position 5

        """


    # Part du resultat de DocMotPage avec les coordonnées graphique
    resultintermed = DocMot(document, True)

    # NewDico et NewMots vont servir à stocker les résultats
    newmots = []

    for i,mot in enumerate(resultintermed):

    # Si c'est un début d'article --> notation 'n' : new
    # on garde toujours le mot précédent en mémoire : motref
        if i == 0:
            mot = mot + ("n",)
            newmots.append(mot)
            motref = mot
        else:

            # Compare la coordonnée haute du mot avec celle du précédent
            # Si inférieur seuilsautligne, on considère pas de saut --> notation 's' : same
            # Par défault seuil saut de ligne réglé à 50 mais possibilité de le changer
            # Meme fonctionnement pour seuilsautPage

            if int(mot[2])-int(motref[2]) < seuilsautligne and abs(int(mot[2])-int(motref[2])) < seuilsautPage:
                mot = mot + ("s",)
                newmots.append(mot)
        # Sinon c'est considéré comme un saut de ligne
            else:
                mot = mot + ("n",)
                newmots.append(mot)
            # important : met le mot actuel en motref pour la suite de la boucle
            motref = mot


    # renvoie comme résultat le dico créé
    return newmots



def DocMotPage(document, detail=False):
    """     Permet de renvoyer la liste de tous les mots non nuls avec la ref des pages
    Renvoie par défault (detail= False)  un dico avec comme clé les pages
    et les valeurs la liste des mots par page :
    Ex {page 1 : [mot1, mot2,....], page 2 : [mot1, mot2,...], ... }

    Paramètre:
        document (str): chemin absolu du document
        detail (boolean)

    Notes: Possibilité de detail comme fonction précédente avec mot sous forme de tuples

    return:
        mots (dict):
            {numéro de page: liste de mots de la page}
    """

    compteurpage = -1
    listemotpage = []
    mots = {}

    tree = etree.parse(document)

    eltbase = tree.xpath("/tei:TEI/tei:text/tei:body", namespaces={"tei": "http://www.tei-c.org/ns/1.0"})

    if eltbase:
        for elt1 in eltbase[0].iterchildren(tag=(
        "{http://www.tei-c.org/ns/1.0}pb", "{http://www.tei-c.org/ns/1.0}div", "{http://www.tei-c.org/ns/1.0}p")):

            # Si c'est un saut de page
            if elt1.tag == "{http://www.tei-c.org/ns/1.0}pb":
                compteurpage += 1

                # Au premier passage, il n'y a aucun mot stocké encore
                if compteurpage != 0:
                    # Après la liste de mot récupéré dans le dico tous les mots
                    # avec comme index (compteurpage)
                    mots[compteurpage] = listemotpage

                # initialise la listmotpage à chaque passage ensuite
                listemotpage = []

            # si c'est un paragraphe p:
            if elt1.tag == "{http://www.tei-c.org/ns/1.0}p":
                # récupère les mots non nuls
                for elt2 in elt1.iterchildren(tag="word"):
                    if elt2.text is not None:
                        # alimente la liste de mots qui va être retourné
                        # en fonction de l'option
                        listemotpage.append(ExtractMot(elt2, detail))

            # Si c'est un paragraphe div
            if elt1.tag == "{http://www.tei-c.org/ns/1.0}div":

                for elt2 in elt1.iterchildren():

                    # car il peut y avoir des paragraphes dans les biblios
                    if elt2.tag == "{http://www.tei-c.org/ns/1.0}pb":

                        compteurpage += 1
                        if compteurpage != 0:
                            mots[compteurpage] = listemotpage
                        listemotpage = []

                    # si c'est un paragraphe p

                    if elt2.tag == "{http://www.tei-c.org/ns/1.0}p":

                        for elt3 in elt2.iterchildren(tag="word"):
                            if elt3.text is not None:
                                # alimente la liste de mots qui va être retourné
                                # en fonction de l'option
                                listemotpage.append(ExtractMot(elt3, detail))

                    # si c'est directement un word

                    if elt2.tag == "word":

                        if elt2.text is not None:
                            # alimente la liste de mots qui va être retourné
                            # en fonction de l'option
                            listemotpage.append(ExtractMot(elt2, detail))

    # gestion de la dernière page
    mots[compteurpage + 1] = listemotpage

    return(mots)


def DocMotPageLigne(document, seuilsautligne=50):
    """ Idem fonction précédente
        mais sous forme d'un dico :
            {page 1 : [mot1, mot2,....], page 2 : [mot1, mot2,...],

        Args : document (str)       : adresse complète du doc
               seuilsautLigne (int) : en option si besoin (seuil à partir duquel considère saut Ligne)

        Return (dict of tuple) : Attention chaque mot est un tuple.
                        La nouvelle donnée (n comme new ou s comme same) est en position 5
        """

    # Part du resultat de DocMotPage avec les coordonnées graphique
    resultintermed = DocMotPage(document, True)

    # NewDico et NewMots vont servir à stocker les résultats
    newdico = {}
    for page in resultintermed.keys():
        newmots= []

        # Pour chaque page, on va regarder chaque mot
        for i,mot in enumerate(resultintermed[page]):

            # Si c'est un début de page, automatiquement c'est un début de ligne --> notation 'n' : new
            # on garde toujours le mot précédent en mémoire : motref
            if i == 0:
                mot = mot + ("n",)
                newmots.append(mot)
                motref = mot
            else:

                # Compare la coordonnée haute du mot avec celle du précédent
                # Si inférieur seuilsautligne, on considère pas de saut --> notation 's' : same
                # Par défault seuil saut de ligne réglé à 50 mais possibilité de le changer
                if int(mot[2])-int(motref[2]) < seuilsautligne:
                    mot = mot + ("s",)
                    newmots.append(mot)
                # Sinon c'est considéré comme un saut de ligne
                else:
                    mot = mot + ("n",)
                    newmots.append(mot)
                # important : met le mot actuel en motref pour la suite de la boucle
                motref = mot
        # consigne nouveaux résultats dans nouveau dico
        newdico[page]= newmots

    # renvoie comme résultat le dico créé
    return newdico


class DocErudit(object):
    """ Permet de récupérer la liste des mots ainsi que leur coordonnées graphiques dans le texte.

    Args:
        document (str): Chemin absolu du document
        typesegment (str): élément recherché (titre, resume, etc. ...)


    """
    def __init__(self, document, typesegment):

        self.obj = []
        self.GetObjectGraphicalCoordinates(document, typesegment)


    def GetObjectGraphicalCoordinates(self, document, typesegment):

        doc_erudit = document.replace("tei", "erudit")
        tree = etree.parse(doc_erudit)
        listepage = tree.xpath("/erudit:article/erudit:corps/erudit:texte/erudit:page",
                                namespaces={"erudit": "http://www.erudit.org/xsd/article"})

        # Recherche Object
        for i_page in range(1, len(listepage)+1):
            listeobject = tree.xpath("/erudit:article/erudit:corps/erudit:texte/erudit:page[" + \
                        str(i_page) + "]/erudit:segment[@typesegment='"+typesegment+"']", namespaces={"erudit": "http://www.erudit.org/xsd/article"})

            if len(listeobject) != 0:
                for obj in listeobject:
                    coordx = obj.attrib['coordx']
                    coordy = obj.attrib['coordy']
                    dimx = obj.attrib['dimx']
                    dimy = obj.attrib['dimy']

                    left = int(coordx) * 2
                    top = int(coordy) * 2
                    right = left + int(dimx) * 2
                    bottom = top + int(dimy) * 2

                    self.obj.append((i_page, left, top, right, bottom))


