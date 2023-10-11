from django.conf import settings

from AllApps.PreTraitement.Persee.DelimitCorpus.models import DocExtractInitial, CorpusEtude, Transformer
from AllApps.PreTraitement.Persee.DelimitCorpus.outils.xpath import DocMotPageLigne
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.ExploreFct.ExpCoordGraphSimpleFct import NbMotAvantPage
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.AideTitreFct import GetAdresseCompletDoc


def InsertNewHtDePage(reduction, donnees):

    seuilgeo = donnees['seuilgeo']
    seuilspgeo = donnees['seuilspgeo']

    reductionencours = CorpusEtude.objects.filter(nom=reduction)
    docsextractencours = DocExtractInitial.objects.filter(CorpusEtudeRef=reductionencours[0])
    for doc in docsextractencours:
        nomfichierencours = doc.DocReferenceRef.TextRef
        anneeencours = doc.DocReferenceRef.annee
        addressedocencours = GetAdresseCompletDoc(nomfichierencours)
        revueencours = doc.DocReferenceRef.RevueRef.nompersee
        # recupére fin de ligne
        MotsPageLigneEnCours = DocMotPageLigne(addressedocencours)
        testlong = len(MotsPageLigneEnCours)
        for i in range(1, testlong):
            LigneEnCours = []
            #LigneEnCoursCoordHaut = []
            for j, mot in enumerate(MotsPageLigneEnCours[i]):
                if (revueencours == "geo" and int(mot[2]) > seuilgeo) or\
                        (revueencours == "spgeo" and anneeencours<1990 and int(mot[2]) > seuilspgeo):
                    LigneEnCours = []
                    break
                if j > 0 and mot[5] == "n":
                    break
                LigneEnCours.append(mot[0])
                #LigneEnCoursCoordHaut.append(int(mot[2]))

            if len(LigneEnCours)!=0:
                # if max(LigneEnCoursCoordHaut) > seuil:
                nbmots_shift = NbMotAvantPage(MotsPageLigneEnCours, i)
                NewTransformer = Transformer(DocExtractRef=doc,
                                               type='HautDePage',
                                               IndexDeb=nbmots_shift,
                                               IndexFin=nbmots_shift +  j,
                                               TextField="",
                                               comment="")
                NewTransformer.save()

