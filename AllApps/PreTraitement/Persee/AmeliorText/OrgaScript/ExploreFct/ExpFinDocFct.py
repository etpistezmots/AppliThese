import os, operator
from django.conf import settings
from AllApps.PreTraitement.Persee.DelimitCorpus.models import  CorpusEtude, DocExtractInitial
from AllApps.PreTraitement.Persee.DelimitCorpus.outils.xpath import  DocMotPageLigne, DocMotLigne, DocErudit
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.AideTitreFct import GetAdresseCompletDoc


def AfficheLigneCenterLastPageDo(FichierResult, reduction, revue):
    DELTA_PIXEL = 300  # Largeur de l'intervalle délimitant le centre de la page
    GAUCHE = 1
    DROITE = 3
    docs_concerne_par_ligne_centre = []
    LignesCentres = []
    error = False

    Test = CorpusEtude.objects.filter(nom=reduction)
    if Test.exists():
        CEenCours = Test[0]

        # si le fichier de résultat n'a pas encore été crée
        if not os.path.isfile(FichierResult):

            # création des résultats

            docsextractencours = DocExtractInitial.objects.filter(CorpusEtudeRef=CEenCours)
            for doc in docsextractencours :
                if doc.DocReferenceRef.RevueRef.nompersee == revue:
                    nomfichierencours = doc.DocReferenceRef.TextRef
                    addressedocencours = GetAdresseCompletDoc(nomfichierencours)

                    # ne va réaliser les traitements que si pas de biblio, sinon a déjà été enleve
                    BiblioCoordinatesDocEnCours = DocErudit(addressedocencours, typesegment="biblio")

                    if len(BiblioCoordinatesDocEnCours.obj)==0:

                        Touslesmotsdocdetail = DocMotPageLigne(addressedocencours)
                        Touslesmotsdernierepage = Touslesmotsdocdetail[list(Touslesmotsdocdetail.keys())[-1]]


                        # rechercher les coordonnées du centre de la page:
                        # moyenne des extrêmes (gauche et droite) trouvés dans le document
                        min_left = 10000
                        max_right = 0
                        for mot in Touslesmotsdernierepage:
                            if int(mot[GAUCHE]) < min_left:
                                min_left = int(mot[GAUCHE])
                            if int(mot[DROITE]) > max_right:
                                max_right = int(mot[DROITE])

                        milieu_doc = (min_left + max_right) / 2

                        # Pour chaque ligne, va regarder si est centrée
                        EnsembleLignesCentresCeDoc = []
                        SousEnsembleLignesCentresCeDoc = []
                        ligneEnCours = []
                        lignecentreprecedent = False
                        for i,mot_i in enumerate(Touslesmotsdernierepage):
                            # cas premier mot
                            if i==0:
                                ligneEnCours.append(mot_i)
                            # pour les autres mots
                            else:
                                if mot_i[5] == 's':
                                    ligneEnCours.append(mot_i)
                                # si on a un mot marquant une une nouvelle ligne
                                else:
                                    # On va tester pour la ligne précédente
                                    milieu_ligne = (int(ligneEnCours[0][GAUCHE]) + int(ligneEnCours[-1][DROITE])) / 2
                                    # cas où la ligne est centrée
                                    if milieu_ligne > (milieu_doc - DELTA_PIXEL) \
                                            and milieu_ligne < (milieu_doc + DELTA_PIXEL):
                                        # c'est sipmle on l'ajoute au sous-ensemble et on change le marqueue
                                        strlignereconstitute = [elt[0] for elt in ligneEnCours]
                                        SousEnsembleLignesCentresCeDoc.append(" ".join(strlignereconstitute))
                                        lignecentreprecedent = True
                                    # cas ou la ligne n'est pas centrée
                                    else:
                                        # si la ligne précédente est centrée
                                        if lignecentreprecedent:
                                            EnsembleLignesCentresCeDoc.append(SousEnsembleLignesCentresCeDoc)
                                            SousEnsembleLignesCentresCeDoc = []
                                            lignecentreprecedent = False
                                        # si la ligne précédente n'éait pas centrée
                                        else:
                                            lignecentreprecedent = False

                                    # on ré-initialise la ligne en cours et met le nouuveau mots
                                    ligneEnCours = []
                                    ligneEnCours.append(mot_i)
                        # cas dernière ligne
                        #même test
                        if len(ligneEnCours)!=0:
                            milieu_ligne = (int(ligneEnCours[0][GAUCHE]) + int(ligneEnCours[-1][DROITE])) / 2
                            # cas où la ligne est centrée
                            if milieu_ligne > (milieu_doc - DELTA_PIXEL) \
                                    and milieu_ligne < (milieu_doc + DELTA_PIXEL):
                                # c'est sipmle on l'ajoute au sous-ensemble et on change le marqueue
                                strlignereconstitute = [elt[0] for elt in ligneEnCours]
                                SousEnsembleLignesCentresCeDoc.append(" ".join(strlignereconstitute))
                                EnsembleLignesCentresCeDoc.append(SousEnsembleLignesCentresCeDoc)
                            # cas ou la ligne n'est pas centrée
                            else:
                                # si la ligne précédente est centrée
                                if lignecentreprecedent:
                                    EnsembleLignesCentresCeDoc.append(SousEnsembleLignesCentresCeDoc)


                        # il faut au moins deux lignes à la suite centrée
                        EnsembleLignesCentresCeDocNew = []
                        MarqueurPlusDeuxLignesSuite = False
                        for elt1 in EnsembleLignesCentresCeDoc:
                            if len(elt1)>1:
                                EnsembleLignesCentresCeDocNew.append(elt1)
                                MarqueurPlusDeuxLignesSuite = True

                        if MarqueurPlusDeuxLignesSuite:
                            docs_concerne_par_ligne_centre.append('<a href="https://www.persee.fr/doc/' +
                                               nomfichierencours[8:-8] + '">' + nomfichierencours[8:-8] + '</a>')
                            LignesCentres.append(EnsembleLignesCentresCeDocNew)

            # cree le dossier si n'existe pas
            dossier = FichierResult.rsplit("/", 1)[0]
            if not os.path.exists(dossier):
                os.makedirs(dossier)


            with open(FichierResult, 'w') as f:
                f.write("Identifiant document Persée (lien portail)" + "\n")
                f.write("Lignes centrées trouvées à la fin du document" + "\n")
                f.write("\n")
                for j,elt1 in enumerate(docs_concerne_par_ligne_centre):
                    f.write(elt1 + "\n")
                    f.write("\n")
                    for elt2 in LignesCentres[j]:
                        for elt3 in elt2:
                            f.write(elt3)
                            f.write("\n")
                        f.write("\n")
                    f.write("\n")

        else:
            with open(FichierResult, 'r') as f:
                content = f.readlines()

            nouvelarticle = True
            SousEnsembleLignesCentresCeDoc = []
            EnsembleLignesCentresCeDoc = []
            for j,line in enumerate(content):
                if line[0:7]== "<a href" or line[0:7]=="Identif":
                    docs_concerne_par_ligne_centre.append(line.strip())
                    nouvelarticle = True
                    if j != 0:
                        LignesCentres.append(EnsembleLignesCentresCeDoc)
                elif line == "\n" and nouvelarticle:
                    EnsembleLignesCentresCeDoc = []
                    SousEnsembleLignesCentresCeDoc = []
                    nouvelarticle = False
                elif line == "\n" and not nouvelarticle:
                    if len(SousEnsembleLignesCentresCeDoc)!=0:
                        EnsembleLignesCentresCeDoc.append(SousEnsembleLignesCentresCeDoc)
                    SousEnsembleLignesCentresCeDoc= []
                else:
                    SousEnsembleLignesCentresCeDoc.append(line.strip())
            LignesCentres.append(EnsembleLignesCentresCeDoc)

    else:
        error = True


    return error,docs_concerne_par_ligne_centre,LignesCentres




def PresenceDebutLigneDo(FichierResult, reduction, revue):

    expression = "Manuscrit"
    docs_concerne_par_expression = []
    LignesAvecExpressionDebut = []
    TailleExpression = len(expression)
    error = False

    Test = CorpusEtude.objects.filter(nom=reduction)
    if Test.exists():
        CEenCours = Test[0]

        # si le fichier de résultat n'a pas encore été crée
        if not os.path.isfile(FichierResult):
            # création des résultats
            docsextractencours = DocExtractInitial.objects.filter(CorpusEtudeRef=CEenCours)
            for doc in docsextractencours :
                if doc.DocReferenceRef.RevueRef.nompersee == revue:
                    nomfichierencours = doc.DocReferenceRef.TextRef
                    addressedocencours = GetAdresseCompletDoc(nomfichierencours)
                    Touslesmotsdocdetail = DocMotLigne(addressedocencours)

                    ligneEnCours = []
                    SousListeAvecExpressionCeDoc = []
                    MarqueurLigneTrouve = False
                    for i, mot_i in enumerate(Touslesmotsdocdetail):
                        # cas premier mot
                        if i == 0:
                            ligneEnCours.append(mot_i)
                        # pour les autres mots
                        else:
                            if mot_i[5] == 's':
                                ligneEnCours.append(mot_i)
                            # si on a un mot marquant une une nouvelle ligne
                            else:
                                lignereconstitute = [elt[0] for elt in ligneEnCours]
                                strlignereconstitute = " ".join(lignereconstitute)
                                if strlignereconstitute[0:TailleExpression]==expression:
                                    if not MarqueurLigneTrouve:
                                        docs_concerne_par_expression.append('<a href="https://www.persee.fr/doc/' +
                                               nomfichierencours[8:-8] + '">' + nomfichierencours[8:-8] + '</a>')
                                        MarqueurLigneTrouve = True
                                    SousListeAvecExpressionCeDoc.append(strlignereconstitute)
                                # on ré-initialise la ligne en cours et met le nouuveau mots
                                ligneEnCours = []
                                ligneEnCours.append(mot_i)
                    # cas dernière ligne
                    # même test
                    lignereconstitute = [elt[0] for elt in ligneEnCours]
                    strlignereconstitute = " ".join(lignereconstitute)
                    if strlignereconstitute[0:TailleExpression] == expression:
                        if not MarqueurLigneTrouve:
                            docs_concerne_par_expression.append('<a href="https://www.persee.fr/doc/' +
                                               nomfichierencours[8:-8] + '">' + nomfichierencours[8:-8] + '</a>')
                        SousListeAvecExpressionCeDoc.append(strlignereconstitute)

                    if len(SousListeAvecExpressionCeDoc)!=0:
                        LignesAvecExpressionDebut.append(SousListeAvecExpressionCeDoc)

            # cree le dossier si n'existe pas
            dossier = FichierResult.rsplit("/", 1)[0]
            if not os.path.exists(dossier):
                os.makedirs(dossier)

            with open(FichierResult, 'w') as f:
                for j, elt1 in enumerate(docs_concerne_par_expression):
                    f.write(elt1 + "\n")
                    f.write("\n")
                    for elt2 in LignesAvecExpressionDebut[j]:
                        f.write(elt2)
                        f.write("\n")
                    f.write("\n")

        else:
            with open(FichierResult, 'r') as f:
                content = f.readlines()

            EnsembleLignesExpressionDebutCeDoc = []
            for j, line in enumerate(content):
                if line[0:7] == "<a href":
                    docs_concerne_par_expression.append(line.strip())
                    if j != 0:
                        LignesAvecExpressionDebut.append(EnsembleLignesExpressionDebutCeDoc)
                        EnsembleLignesExpressionDebutCeDoc = []
                elif line == "\n":
                    continue
                else:
                    EnsembleLignesExpressionDebutCeDoc.append(line.strip())

            LignesAvecExpressionDebut.append(EnsembleLignesExpressionDebutCeDoc)

    else:
        error=True

    return error,docs_concerne_par_expression,LignesAvecExpressionDebut
