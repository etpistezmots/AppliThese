from django.conf import settings

from AllApps.PreTraitement.Persee.DelimitCorpus.models import DocExtractInitial, CorpusEtude, Transformer
from AllApps.PreTraitement.Persee.DelimitCorpus.outils.xpath import DocMotPageLigne
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.ExploreFct.ExpCoordGraphSimpleFct import NbMotAvantPage
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.AideTitreFct import GetAdresseCompletDoc


def InsertNewBasDePage(reduction, donnees):

    SupprEspSup1990= donnees['SupprEspSup1990']
    SupprAnnCombiTextual = donnees['SupprAnnCombiTextual']

    reductionencours = CorpusEtude.objects.filter(nom=reduction)
    docsextractencours = DocExtractInitial.objects.filter(CorpusEtudeRef=reductionencours[0])
    for doc in docsextractencours:
        nomfichierencours = doc.DocReferenceRef.TextRef
        addressedocencours = GetAdresseCompletDoc(nomfichierencours)
        revueencours = doc.DocReferenceRef.RevueRef.nompersee
        dateencours  = doc.DocReferenceRef.annee

        MotsPageLigneEnCours = DocMotPageLigne(addressedocencours)
        testlong = len(MotsPageLigneEnCours)
        for i in range(1, testlong):
            LigneEnCours = []
            LigneEnCoursCoordBas = []
            # sur la page i en énumérant à l'envers !
            for j, mot in reversed(list(enumerate(MotsPageLigneEnCours[i]))):
                if j > 0 and mot[5] == "n":
                    break
                LigneEnCours.append(mot[0])

            if len(LigneEnCours)!=0:
                #  si Espace géograhique
                if revueencours=="spgeo":
                    if dateencours >= 1990 and SupprEspSup1990:
                        nbmots_shift = NbMotAvantPage(MotsPageLigneEnCours, i)
                        # Attention pour IndexDeb enumere à l'envers j
                        NewTransformer = Transformer(DocExtractRef=doc,
                                                       type='BasDePage',
                                                       IndexDeb=nbmots_shift + j,
                                                       IndexFin=nbmots_shift + len(MotsPageLigneEnCours[i]),
                                                       TextField="",
                                                       comment="")
                        NewTransformer.save()
                # si Annales
                else:
                    if SupprAnnCombiTextual and (LigneEnCours[-1][0:2] == "DE" or LigneEnCours[-1][0:2] == "DB"
                        or LigneEnCours[-1][0:2] == "DK" or LigneEnCours[-1][0:3] == "ANN" or LigneEnCours[-1][0:3] == "Ann"
                        or LigneEnCours[0][-3:] == "Ann" or LigneEnCours[0][-3:] == "ANN" or LigneEnCours[-1][0:5] == "ARMAND"
                        or LigneEnCours[-1][0:5] == "Armand" or LigneEnCours[-1][0:4] == "Gèo." or LigneEnCours[-1][0:4] == "Geo."
                        or "Année." in LigneEnCours or "ANNEE." in LigneEnCours or "ANNÉE" in LigneEnCours):

                        nbmots_shift = NbMotAvantPage(MotsPageLigneEnCours, i)
                        NewTransformer = Transformer(DocExtractRef=doc,
                                                       type='BasDePage',
                                                       IndexDeb=nbmots_shift +  j,
                                                       IndexFin=nbmots_shift + len(MotsPageLigneEnCours[i]),
                                                       TextField="",
                                                       comment="")
                        NewTransformer.save()
