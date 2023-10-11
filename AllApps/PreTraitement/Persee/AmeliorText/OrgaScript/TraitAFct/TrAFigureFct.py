from django.conf import settings

from AllApps.PreTraitement.Persee.DelimitCorpus.models import CorpusEtude, DocExtractInitial, Transformer
from AllApps.PreTraitement.Persee.DelimitCorpus.outils.xpath import DocMotPage
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.ExploreFct.ExpCoordGraphSimpleFct import GetListIDMots, \
    GetIntervalleMotsParFenetre
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.ExploreFct.ExpFigureFct import GetListMots, \
    GetTitleAndCoordinateFigure
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.AideTitreFct import GetAdresseCompletDoc, GetTitreTrouvesDansTexte
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.AideTitreFct import str_compare


def InsertNewFigure(reduction, donnees):

    EssaiHomogeneTitre = donnees['EssaiHomogeneTitre']
    mots = donnees['mots']
    Listmots = mots.split("*")

    reductionencours = CorpusEtude.objects.filter(nom=reduction)
    docsextractencours = DocExtractInitial.objects.filter(CorpusEtudeRef=reductionencours[0])


    for doc in docsextractencours:
        nomfichierencours = doc.DocReferenceRef.TextRef
        addressedocencours = GetAdresseCompletDoc(nomfichierencours)
        dateencours = doc.DocReferenceRef.annee
        revueencours = doc.DocReferenceRef.RevueRef.nompersee
        DataCoordinatesDocEnCours, TitresFigureDocEnCours = GetTitleAndCoordinateFigure(addressedocencours)
        MotsPageDocEnCours = DocMotPage(addressedocencours, detail=True)
        list_mots_figures = GetListMots(DataCoordinatesDocEnCours,
                                           MotsPageDocEnCours)
        list_id_mots_figures = GetListIDMots(DataCoordinatesDocEnCours,
                                                   MotsPageDocEnCours)

        # Chercher dans les mots du titres

        if EssaiHomogeneTitre:
            for i, titrefigure in enumerate(TitresFigureDocEnCours):

                if len(titrefigure.split()) > 1 and titrefigure != "None" and titrefigure is not None:

                    # enleve la partie anglaise si An
                    if revueencours == "geo" and dateencours > 1991:
                        titrefigure = titrefigure.split("/")[0]

                    # Si le titre est supérieur à 5 mots
                    if len(titrefigure)>5:
                        compteurressemblance = 0
                        titrefiguresplit = titrefigure.split()
                        for mottitrefigure in titrefiguresplit:
                            for motensemblefigure in list_mots_figures[i]:
                                ressemblance = str_compare(mottitrefigure.lower(), motensemblefigure.lower())
                                if ressemblance > 0.8:
                                    compteurressemblance += 1
                                    break
                        ratioressemblance = compteurressemblance / len(titrefigure.split())

                        if ratioressemblance > 0.7:

                            # enleve l'annonce si est présente dans list de mot défini
                            if titrefiguresplit[0] in Listmots:
                                titrefigure = " ".join(titrefiguresplit[1:])

                            list_intervalles_mots_retirer = GetIntervalleMotsParFenetre(list_id_mots_figures[i])
                            if len(list_intervalles_mots_retirer)>0:
                                for l, eltagreg in enumerate(list_intervalles_mots_retirer):
                                    if l == 0 :
                                        NewTransformer = Transformer(DocExtractRef=doc,
                                                                       type='Figure',
                                                                       IndexDeb=eltagreg[0] - 1,
                                                                       IndexFin=eltagreg[1],
                                                                       TextField=titrefigure.replace("'", "''"),
                                                                       comment="")
                                        NewTransformer.save()
                                    # on ne rajoute pas le titre pour les autres parties
                                    else:
                                        NewTransformer = Transformer(DocExtractRef=doc,
                                                                       type='Figure',
                                                                       IndexDeb=eltagreg[0] - 1,
                                                                       IndexFin=eltagreg[1],
                                                                       TextField="",
                                                                       comment="")
                                        NewTransformer.save()

                        # Si ratio ressemblance < 0,75, on ne rajoute pas le titres
                        else:
                            list_intervalles_mots_retirer = GetIntervalleMotsParFenetre(list_id_mots_figures[i])
                            if len(list_intervalles_mots_retirer) > 0:
                                for l, eltagreg in enumerate(list_intervalles_mots_retirer):
                                    NewTransformer = Transformer(DocExtractRef=doc,
                                                                       type='Figure',
                                                                       IndexDeb=eltagreg[0] - 1,
                                                                       IndexFin=eltagreg[1],
                                                                       TextField="",
                                                                       comment="")
                                    NewTransformer.save()

                    # si le titre est inférieur ou égale à 5 mots
                    else:
                        noseuil = len(list_id_mots_figures[i])
                        ResultTitreTrouve = 0
                        if noseuil > 1:
                            ResultTitreTrouve = GetTitreTrouvesDansTexte(titrefigure,
                                                                         list_id_mots_figures[i],
                                                                         0.9,  # premier seuil de ressemblance
                                                                         noseuil)

                        if ResultTitreTrouve and ResultTitreTrouve["matching_score"] > 0.75:

                            # enleve l'annonce si est présente dans list de mot défini
                            if titrefiguresplit[0] in Listmots:
                                titrefigure = " ".join(titrefiguresplit[1:])

                            list_intervalles_mots_retirer = GetIntervalleMotsParFenetre(list_id_mots_figures[i])
                            if len(list_intervalles_mots_retirer) > 0:
                                for l, eltagreg in enumerate(list_intervalles_mots_retirer):
                                    if l == 0:
                                        NewTransformer = Transformer(DocExtractRef=doc,
                                                                       type='Figure',
                                                                       IndexDeb=eltagreg[0] - 1,
                                                                       IndexFin=eltagreg[1],
                                                                       TextField=titrefigure.replace("'", "''"),
                                                                       comment="")
                                        NewTransformer.save()
                                    # on ne rajoute pas le titre pour les autres parties
                                    else:
                                        NewTransformer = Transformer(DocExtractRef=doc,
                                                                       type='Figure',
                                                                       IndexDeb=eltagreg[0] - 1,
                                                                       IndexFin=eltagreg[1],
                                                                       TextField="",
                                                                       comment="")
                                        NewTransformer.save()

                        # Si score ressemblance < 0,75, on ne rajoute pas le titres
                        else:
                            list_intervalles_mots_retirer = GetIntervalleMotsParFenetre(list_id_mots_figures[i])
                            if len(list_intervalles_mots_retirer) > 0:
                                for l, eltagreg in enumerate(list_intervalles_mots_retirer):
                                    NewTransformer = Transformer(DocExtractRef=doc,
                                                                   type='Figure',
                                                                   IndexDeb=eltagreg[0] - 1,
                                                                   IndexFin=eltagreg[1],
                                                                   TextField="",
                                                                   comment="")

                                    NewTransformer.save()

                # Si la figure n'a pas de titre
                else:
                    list_intervalles_mots_retirer = GetIntervalleMotsParFenetre(list_id_mots_figures[i])
                    if len(list_intervalles_mots_retirer) > 0:
                        for l, eltagreg in enumerate(list_intervalles_mots_retirer):
                            NewTransformer = Transformer(DocExtractRef=doc,
                                                           type='Figure',
                                                           IndexDeb=eltagreg[0] - 1,
                                                           IndexFin=eltagreg[1],
                                                           TextField="",
                                                           comment="")

                            NewTransformer.save()




        if len(Listmots)!=0:

            FigureCoordinatesDocEnCours, TitresFigureDocEnCours = GetTitleAndCoordinateFigure(addressedocencours)

            PageAvecFigure = []
            for EltFigure in FigureCoordinatesDocEnCours:
                PageAvecFigure.append(EltFigure[0])

            CompteurMot = 0
            for page, list_mot in MotsPageDocEnCours.items():
                for mot in list_mot:
                    CompteurMot +=1
                    for wordremove in Listmots:
                        if mot[0] == wordremove and page in PageAvecFigure :
                            NewTransformer = Transformer(DocExtractRef=doc,
                                                        type='Figure',
                                                        IndexDeb=CompteurMot -1,
                                                        IndexFin= CompteurMot,
                                                        TextField="",
                                                        comment="mots annonce")
                            NewTransformer.save()




