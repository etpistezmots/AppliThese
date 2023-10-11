from django.conf import settings

from AllApps.PreTraitement.Persee.DelimitCorpus.models import CorpusEtude, DocExtractInitial, Transformer
from AllApps.PreTraitement.Persee.DelimitCorpus.outils.xpath import DocMotPage, DocErudit
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.ExploreFct.ExpCoordGraphSimpleFct import GetListIDMots, \
    GetIntervalleMotsParFenetre, NbMotAvantPage
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.AideTitreFct import GetAdresseCompletDoc


def InsertNewAnnexe(reduction, donnees):

    Suppr = donnees['suppr']
    StopMots = donnees['mots']
    Zone = donnees['zone']

    reductionencours = CorpusEtude.objects.filter(nom=reduction)
    docsextractencours = DocExtractInitial.objects.filter(CorpusEtudeRef=reductionencours[0])
    for doc in docsextractencours:
        nomfichierencours = doc.DocReferenceRef.TextRef
        addressedocencours = GetAdresseCompletDoc(nomfichierencours)
        MotsPageDocEnCours = DocMotPage(addressedocencours, detail=True)
        # recupére des annexes
        AnnexeCoordinatesDocEnCours = DocErudit(addressedocencours, typesegment="annexe")


        if len(AnnexeCoordinatesDocEnCours.obj) > 0:

            list_id_mots_annexes = GetListIDMots(AnnexeCoordinatesDocEnCours.obj,
                                                 MotsPageDocEnCours)

            for k, annexe in enumerate(list_id_mots_annexes):

                list_intervalles_mots_retirer = GetIntervalleMotsParFenetre(annexe)

                if len(list_intervalles_mots_retirer) > 0:

                    for l,eltagreg in enumerate(list_intervalles_mots_retirer):
                        if Suppr :
                            NewTransformer = Transformer(DocExtractRef=doc,
                                                   type='Annexe',
                                                   IndexDeb=eltagreg[0] -1,
                                                   IndexFin=eltagreg[1],
                                                   TextField= "",
                                                   comment="")
                            NewTransformer.save()

                    # Ajout de la procédure pour retirer certain mots
                    if len(annexe) != 0:
                        mot1 = annexe[0]
                        print(AnnexeCoordinatesDocEnCours.obj)
                        page = AnnexeCoordinatesDocEnCours.obj[k][0]
                        nbmots_shift = NbMotAvantPage(MotsPageDocEnCours, page)
                        # fin car on cherche dans les x mots (seuil) avant
                        fin = mot1 - nbmots_shift - 1
                        if fin - int(Zone) > 0:
                            deb = fin - int(Zone)
                        else:
                            deb = 0
                        RechercheMotIn = MotsPageDocEnCours[page][deb:fin]
                        for j, motiter in enumerate(RechercheMotIn):
                            for stopmot in StopMots.split("*"):
                                if motiter[0] == stopmot:
                                    nbmots_shift = NbMotAvantPage(MotsPageDocEnCours, page)
                                    index = nbmots_shift + deb + j + 1

                                    NewTransformer = Transformer(DocExtractRef=doc,
                                                                   type='Annexe',
                                                                   IndexDeb=index,
                                                                   IndexFin=index + 1,
                                                                   TextField="",
                                                                   comment="stopmot")
                                    NewTransformer.save()

        # recupére des données car est codée ainsi dans certains document
        AnnexeCoordinatesDocEnCours = DocErudit(addressedocencours, typesegment="donnee")

        if len(AnnexeCoordinatesDocEnCours.obj) > 0:

            list_id_mots_annexes = GetListIDMots(AnnexeCoordinatesDocEnCours.obj,
                                                 MotsPageDocEnCours)

            for k, annexe in enumerate(list_id_mots_annexes):

                list_intervalles_mots_retirer = GetIntervalleMotsParFenetre(annexe)

                if len(list_intervalles_mots_retirer) > 0:

                    for l, eltagreg in enumerate(list_intervalles_mots_retirer):
                        if Suppr:
                            NewTransformer = Transformer(DocExtractRef=doc,
                                                           type='Annexe',
                                                           IndexDeb=eltagreg[0] - 1,
                                                           IndexFin=eltagreg[1],
                                                           TextField="",
                                                           comment="")
                            NewTransformer.save()

                    # Ajout de la procédure pour retirer certain mots
                    if len(annexe) != 0:
                        mot1 = annexe[0]
                        page = AnnexeCoordinatesDocEnCours.obj[k][0]
                        nbmots_shift = NbMotAvantPage(MotsPageDocEnCours, page)
                        # fin car on cherche dans les x mots (seuil) avant
                        fin = mot1 - nbmots_shift - 1
                        if fin - int(Zone) > 0:
                            deb = fin - int(Zone)
                        else:
                            deb = 0
                        RechercheMotIn = MotsPageDocEnCours[page][deb:fin]
                        for j, motiter in enumerate(RechercheMotIn):
                            for stopmot in StopMots.split("*"):
                                if motiter[0] == stopmot:
                                    nbmots_shift = NbMotAvantPage(MotsPageDocEnCours, page)
                                    index = nbmots_shift + deb + j + 1

                                    NewTransformer = Transformer(DocExtractRef=doc,
                                                                   type='Annexe',
                                                                   IndexDeb=index,
                                                                   IndexFin=index + 1,
                                                                   TextField="",
                                                                   comment="stopmot")
                                    NewTransformer.save()






