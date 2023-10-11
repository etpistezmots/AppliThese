import os
from django.conf import settings
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.CommunAllFct import StringToSearchInErudit
from AllApps.PreTraitement.Persee.DelimitCorpus.models import  CorpusEtude, DocExtractInitial
from AllApps.PreTraitement.Persee.DelimitCorpus.outils.xpath import  DocRequete, DocMotPage, DocErudit, DocMot
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.AideTitreFct import GetAdresseCompletDoc


def calculsaut(listintervalle):
    listesauts= []
    indexfin = 0
    for i,elt in enumerate(listintervalle):
        if i==0:
            indexfin = elt[1]
        else:
            saut = elt[0] - indexfin
            listesauts.append(saut)
            indexfin = elt[1]
    return listesauts



def GetListIDMots(resumes, listmot):
    """
    Args:
        resumes (list of list): liste des résumés contenues dans l'article
            [0]: Numéro de la page du résumé
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
        resumetext_absolu: liste de liste d'identifiants de mots absolu dans l'article

    """
    resumetext_absolu = []
    LEFT_COORD = 1
    TOP_COORD = 2
    RIGHT_COORD = 3
    BOTTOM_COORD = 4
    NUMERO_PAGE = 0

    for i, resume in enumerate(resumes):

        resumetext = []
        if resume[0] in listmot.keys() and len(resume) != 0:
            listmotpage = listmot[resume[0]]
            resumetext_absolu.append([])
            nbmots = 0
            for mot in listmotpage:
                # test si la position du mot est contenue dans l'intervalle de la page
                nbmots += 1
                if int(mot[LEFT_COORD]) >= resume[LEFT_COORD] and \
                                int(mot[LEFT_COORD]) <= resume[RIGHT_COORD] and \
                                int(mot[TOP_COORD]) >= resume[TOP_COORD] and \
                                int(mot[TOP_COORD]) <= resume[BOTTOM_COORD] and \
                                int(mot[RIGHT_COORD]) >= resume[LEFT_COORD] and \
                                int(mot[RIGHT_COORD]) <= resume[RIGHT_COORD] and \
                                int(mot[BOTTOM_COORD]) >= resume[TOP_COORD] and \
                                int(mot[BOTTOM_COORD]) <= resume[BOTTOM_COORD]:
                    resumetext.append(nbmots)

        nbmots_shift = NbMotAvantPage(listmot, resume[NUMERO_PAGE])
        for n in resumetext:
            resumetext_absolu[i].append(n + nbmots_shift)
    return resumetext_absolu


def GetIntervalleMotsParFenetre(resumetext):
    """
    Permet de détecter s'il y a une exception sur une fenetre particulière
    Car sinon on a un traitement global qui rend difficile cette détection particulière
    """

    list_remove = []

    compteobtenu = 0
    for obtenue in resumetext:
        compteobtenu = compteobtenu + 1
        if compteobtenu == 1:
            obtenueref = obtenue
            indexdeb = obtenue
        if compteobtenu == len(resumetext) and compteobtenu == 1:
            list_remove.append((obtenue, obtenue))
        if compteobtenu == len(resumetext) and compteobtenu != 1:
            if obtenue != obtenueref + 1:
                list_remove.append((indexdeb, obtenueref))
                list_remove.append((obtenue, obtenue))
            else:
                list_remove.append((indexdeb, obtenue))
        else:
            if compteobtenu > 1:
                if obtenue != obtenueref + 1:
                    list_remove.append((indexdeb, obtenueref))
                    obtenueref = obtenue
                    indexdeb = obtenue
                else:
                    obtenueref = obtenue
                    continue
    return list_remove


def NbMotAvantPage(listmot, numero_page):
    compteur_mot = 0
    if numero_page > 1:
        for page in range(1, numero_page):
            compteur_mot += len(listmot[page])
    return compteur_mot


def SousFonction(addressedocencours,nomfichierencours,ARechercherDansErudit,MotsPageDocEnCours,objetred):
    DataCoordinatesDocEnCours = DocErudit(addressedocencours, typesegment=ARechercherDansErudit)
    list_id_mots_coord_graph = GetListIDMots(DataCoordinatesDocEnCours.obj,
                                             MotsPageDocEnCours)

    RefCoordGraphDiscontinuInt= []
    CompteurGeneralInt = 0
    CompteurDisconInt = 0
    for k, coord_graph in enumerate(list_id_mots_coord_graph):
        CompteurGeneralInt = CompteurGeneralInt + 1

        list_intervalles_mots_retirer = GetIntervalleMotsParFenetre(coord_graph)

        # Si une fenêtre graphique ne génère pas un et un seul intervalle
        nbre_intervalles = len(list_intervalles_mots_retirer)
        if nbre_intervalles > 1:
            CompteurDisconInt = CompteurDisconInt + 1

            intervallemots = []
            for intervalle in list_intervalles_mots_retirer:
                page = DataCoordinatesDocEnCours.obj[k][0]
                nbmots_shift = NbMotAvantPage(MotsPageDocEnCours, page)
                motdeb = MotsPageDocEnCours[page][intervalle[0] - nbmots_shift - 1][0]
                motfin = MotsPageDocEnCours[page][intervalle[1] - nbmots_shift - 1][0]
                intervallemots.append((motdeb, motfin))

            sautmax = max(calculsaut(list_intervalles_mots_retirer))

            RefCoordGraphDiscontinuInt.append(
                (nomfichierencours,
                 objetred + " " + str(k + 1),
                 sautmax-1,
                 str(list_intervalles_mots_retirer),
                 str(intervallemots)))
    return RefCoordGraphDiscontinuInt, CompteurGeneralInt, CompteurDisconInt



def AfficheCoordGraphDiscontinuMaxDo(FichierResult1, FichierResult2, reduction, objetred, revue):
    error = False
    RefCoordGraphDiscontinu = []
    CompteurGeneral = 0
    CompteurDiscon = 0
    Test = CorpusEtude.objects.filter(nom=reduction)
    if Test.exists():
        reductionencours = Test[0]
        # s'il manque un des fichiers de résultats
        if (not os.path.isfile(FichierResult1)) or (not os.path.isfile(FichierResult2)):
            # création des résultats
            docsextractencours = DocExtractInitial.objects.filter(CorpusEtudeRef=reductionencours)
            for doc in docsextractencours:
                if doc.DocReferenceRef.RevueRef.nompersee == revue:
                    nomfichierencours = doc.DocReferenceRef.TextRef
                    addressedocencours = GetAdresseCompletDoc(nomfichierencours)
                    ARechercherDansErudit = StringToSearchInErudit(objetred)
                    # pour les notes : cas :spgeo_0046-2497_1972_num_1_1_3431
                    # note compris dedans du coup gènère trois sous liste  vides pour les trois notes*
                    # D'ou nbre_intervalles > 1 (car avant =!1)

                    MotsPageDocEnCours = DocMotPage(addressedocencours, detail=True)

                    RefCoordGraphDiscontinuInt, CompteurGeneralInt, CompteurDisconInt =  SousFonction(addressedocencours,'<a href="https://www.persee.fr/doc/' +
                                               nomfichierencours[8:-8] + '">' + nomfichierencours[8:-8] + '</a>',ARechercherDansErudit,
                                                               MotsPageDocEnCours,objetred)
                    RefCoordGraphDiscontinu = RefCoordGraphDiscontinu + RefCoordGraphDiscontinuInt
                    CompteurGeneral =  CompteurGeneral + CompteurGeneralInt
                    CompteurDiscon = CompteurDiscon + CompteurDisconInt

                    # Extension pour prendre en compte résultat érudit

                    if ARechercherDansErudit=="note":
                        RefCoordGraphDiscontinuInt, CompteurGeneralInt, CompteurDisconInt = SousFonction(addressedocencours, '<a href="https://www.persee.fr/doc/' +
                                               nomfichierencours[8:-8] + '">' + nomfichierencours[8:-8] + '</a>', "notebio",
                                                                  MotsPageDocEnCours, objetred)
                        RefCoordGraphDiscontinu = RefCoordGraphDiscontinu + RefCoordGraphDiscontinuInt
                        CompteurGeneral = CompteurGeneral + CompteurGeneralInt
                        CompteurDiscon = CompteurDiscon + CompteurDisconInt
                        RefCoordGraphDiscontinuInt, CompteurGeneralInt, CompteurDisconInt = SousFonction(addressedocencours, '<a href="https://www.persee.fr/doc/' +
                                               nomfichierencours[8:-8] + '">' + nomfichierencours[8:-8] + '</a>', "noteedito",
                                                                  MotsPageDocEnCours, objetred)
                        RefCoordGraphDiscontinu = RefCoordGraphDiscontinu + RefCoordGraphDiscontinuInt
                        CompteurGeneral = CompteurGeneral + CompteurGeneralInt
                        CompteurDiscon = CompteurDiscon + CompteurDisconInt


                    if ARechercherDansErudit=="annexe":
                        RefCoordGraphDiscontinuInt, CompteurGeneralInt, CompteurDisconInt = SousFonction(addressedocencours, '<a href="https://www.persee.fr/doc/' +
                                               nomfichierencours[8:-8] + '">' + nomfichierencours[8:-8] + '</a>', "donnee",
                                                                  MotsPageDocEnCours, objetred)
                        RefCoordGraphDiscontinu = RefCoordGraphDiscontinu + RefCoordGraphDiscontinuInt
                        CompteurGeneral = CompteurGeneral + CompteurGeneralInt
                        CompteurDiscon = CompteurDiscon + CompteurDisconInt

                    if ARechercherDansErudit=="titre1":
                        RefCoordGraphDiscontinuInt, CompteurGeneralInt, CompteurDisconInt = SousFonction(addressedocencours, '<a href="https://www.persee.fr/doc/' +
                                               nomfichierencours[8:-8] + '">' + nomfichierencours[8:-8] + '</a>', "titre2",
                                                                  MotsPageDocEnCours, objetred)
                        RefCoordGraphDiscontinu = RefCoordGraphDiscontinu + RefCoordGraphDiscontinuInt
                        CompteurGeneral = CompteurGeneral + CompteurGeneralInt
                        CompteurDiscon = CompteurDiscon + CompteurDisconInt
                        RefCoordGraphDiscontinuInt, CompteurGeneralInt, CompteurDisconInt = SousFonction(addressedocencours, '<a href="https://www.persee.fr/doc/' +
                                               nomfichierencours[8:-8] + '">' + nomfichierencours[8:-8] + '</a>', "titre3",
                                                                  MotsPageDocEnCours, objetred)
                        RefCoordGraphDiscontinu = RefCoordGraphDiscontinu + RefCoordGraphDiscontinuInt
                        CompteurGeneral = CompteurGeneral + CompteurGeneralInt
                        CompteurDiscon = CompteurDiscon + CompteurDisconInt

                RefCoordGraphDiscontinu = sorted(RefCoordGraphDiscontinu, key=lambda tup: tup[2], reverse=True)

            # cree le dossier si n'existe pas
            dossier = FichierResult1.rsplit("/", 1)[0]
            if not os.path.exists(dossier):
                os.makedirs(dossier)

            # si fichier1 existe, l'efface
            if os.path.isfile(FichierResult1):
                os.remove(FichierResult1)

            # écriture fichier1
            with open(FichierResult1, 'w') as f:

                # légende
                f.write("Identifiant document" + "\n")
                f.write("Numéro de l'élément "  + objetred + "\n")
                f.write("Discontuinuité max entre les intervalles" + "\n")
                f.write("Intervalle composant l'élément par les index" + "\n")
                f.write("Intervalle composant l'élément par les mots" + "\n")
                f.write("\n")

                # complète contenu
                for line in RefCoordGraphDiscontinu:
                    for l,elt1 in enumerate(line):
                        if l==2:
                            f.write(str(elt1) + "\n")
                        else:
                            f.write(elt1 + "\n")
                    f.write("\n")

            # pour que légende apparaisse dans l'interface
            RefCoordGraphDiscontinu.insert(0, ("Identifiant document" + "\n",
                                               "Numéro de l'élément " + objetred + "\n",
                                               "Discontuinuité max entre les intervalles" + "\n",
                                               "Intervalle composant l'élément par les index" + "\n",
                                               "Intervalle composant l'élément par les mots" + "\n"))

            # si fichier2 existe, l'efface
            if os.path.isfile(FichierResult2):
                os.remove(FichierResult2)

            # écriture fichier 2
            with open(FichierResult2, 'w') as f:
                f.write("Nombre total éléments" + objetred + "\n")
                f.write("Nombre éléments" + objetred + "avec discontinuité " + "\n")
                f.write("\n")
                f.write(str(CompteurGeneral)+ "\n")
                f.write(str(CompteurDiscon))

        else:

            # récup info fichier 1
            with open(FichierResult1, 'r') as f:
                content = f.readlines()
                SousListes = []
                for i, elt in enumerate(content):
                    # petite astuce qui joue sur les multiples de cinq
                    # car il y a cinq éléments dans chaque sous listes
                    if ((i + 1) % 6 != 0):
                        SousListes.append(elt)
                    else:
                        RefCoordGraphDiscontinu.append(SousListes)
                        SousListes = []

            # récup info fichier 2
            with open(FichierResult2, 'r') as f:
                content = f.readlines()
                for i, elt in enumerate(content):
                    if i == 3:
                        CompteurGeneral = int(elt)
                    if i == 4:
                        CompteurDiscon = int(elt)

    else:
        error= True


    return error, RefCoordGraphDiscontinu, CompteurGeneral, CompteurDiscon