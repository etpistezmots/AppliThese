from django.conf import settings
from AllApps.PreTraitement.Persee.DelimitCorpus.models import  CorpusEtude, DocExtractInitial, Transformer
from AllApps.PreTraitement.Persee.DelimitCorpus.outils.xpath import  DocMotLigne, DocMotPageLigne, DocErudit
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.AideTitreFct import GetAdresseCompletDoc

def InsertNewFinDoc(reduction, donnees):

    ContenuCentreRemove = donnees['ContenuCentreRemove']
    mots = donnees['mots']
    ManuscritRemove = donnees['ManuscritRemove']
    DELTA_PIXEL = 300  # Largeur de l'intervalle délimitant le centre de la page
    GAUCHE = 1
    DROITE = 3

    reductionencours = CorpusEtude.objects.filter(nom=reduction)
    docsextractencours = DocExtractInitial.objects.filter(CorpusEtudeRef=reductionencours[0])
    list_mots = mots.split("*")

    for doc in docsextractencours:
        nomfichierencours = doc.DocReferenceRef.TextRef
        addressedocencours = GetAdresseCompletDoc(nomfichierencours)
        revueencours = doc.DocReferenceRef.RevueRef.nompersee

        if revueencours == "spgeo":

            Touslesmotsdocdetail = DocMotLigne(addressedocencours)

            if ManuscritRemove:

                for i, mot_i in enumerate(Touslesmotsdocdetail):
                    if mot_i[5] == 'n' and mot_i[0]== "Manuscrit":
                        NewTransformer = Transformer(DocExtractRef=doc,
                                                       type='FinDoc',
                                                       IndexDeb= i,
                                                       IndexFin=len(Touslesmotsdocdetail) + 1,
                                                       TextField="",
                                                       comment="")
                        NewTransformer.save()

            if ContenuCentreRemove:

                # ne va réaliser les traitements que si pas de biblio, sinon a déjà été enleve
                BiblioCoordinatesDocEnCours = DocErudit(addressedocencours, typesegment="biblio")

                if len(BiblioCoordinatesDocEnCours.obj)>0:

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
                    ligneEnCours = []
                    for i, mot_i in enumerate(Touslesmotsdernierepage):
                        # cas premier mot
                        if i == 0:
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
                                    for term in list_mots:
                                        if term in ligneEnCours:
                                            NewTransformer = Transformer(DocExtractRef=doc,
                                                                           type='FinDoc',
                                                                           IndexDeb=i - len(ligneEnCours),
                                                                           IndexFin=len(Touslesmotsdocdetail) + 1,
                                                                           TextField="",
                                                                           comment="")
                                            NewTransformer.save()
                                            break
                                # on ré-initialise la ligne en cours et met le nouuveau mots
                                ligneEnCours = []
                                ligneEnCours.append(mot_i)
                    # cas dernière ligne
                    # même test
                    if len(ligneEnCours) != 0:
                        milieu_ligne = (int(ligneEnCours[0][GAUCHE]) + int(ligneEnCours[-1][DROITE])) / 2
                        # cas où la ligne est centrée
                        if milieu_ligne > (milieu_doc - DELTA_PIXEL) \
                                and milieu_ligne < (milieu_doc + DELTA_PIXEL):
                            for term in list_mots:
                                if term in ligneEnCours:
                                    NewTransformer = Transformer(DocExtractRef=doc,
                                                                   type='FinDoc',
                                                                   IndexDeb=len(Touslesmotsdocdetail) - len(ligneEnCours),
                                                                   IndexFin=len(Touslesmotsdocdetail) + 1,
                                                                   TextField="",
                                                                   comment="")
                                    NewTransformer.save()
                                    break



