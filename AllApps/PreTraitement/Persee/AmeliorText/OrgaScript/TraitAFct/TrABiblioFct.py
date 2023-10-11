from django.conf import settings

from AllApps.PreTraitement.Persee.DelimitCorpus.models import DocExtractInitial, CorpusEtude, Transformer
from AllApps.PreTraitement.Persee.DelimitCorpus.outils.xpath import DocErudit, DocMotPage
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.ExploreFct.ExpCoordGraphSimpleFct import GetListIDMots, \
    GetIntervalleMotsParFenetre, NbMotAvantPage
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.ExploreFct.ExpBiblioFct import \
    RenvoiIndexPageLastBiblio
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.AideTitreFct import GetAdresseCompletDoc


def ProcedureRetraitMotAvt(doc,RechercheZone,StopMots,BiblioIndex,DataCoordinatesDocEnCours,MotsPageDocEnCours, mot1):
    page = DataCoordinatesDocEnCours.obj[BiblioIndex][0]
    nbmots_shift = NbMotAvantPage(MotsPageDocEnCours, page)
    # fin car on cherche dans les x mots (seuil) avant
    fin = mot1 - nbmots_shift - 1
    if fin - int(RechercheZone) > 0:
        deb = fin - int(RechercheZone)
    else:
        deb = 0
    RechercheMotIn = MotsPageDocEnCours[page][deb:fin]
    for j, motiter in enumerate(RechercheMotIn):
        for stopmot in StopMots.split("*"):
            if motiter[0] == stopmot:
                nbmots_shift = NbMotAvantPage(MotsPageDocEnCours, page)
                index = nbmots_shift + deb + j + 1

                NewTransformer = Transformer(DocExtractRef=doc,
                                               type='Biblio',
                                               IndexDeb=index -1,
                                               IndexFin=index,
                                               TextField="",
                                               comment="stopmot")
                NewTransformer.save()



def TraitLastBiblio(doc,list_id_last_biblio,MotsPageEnCours):

    FirstIndex = list_id_last_biblio[0][0] - 1
    CountAllWord = 0
    for k in MotsPageEnCours:
        CountAllWord = CountAllWord + len(MotsPageEnCours[k])
    LastIndex = CountAllWord
    NewTransformer = Transformer(DocExtractRef=doc,
                                   type='Biblio',
                                   IndexDeb=FirstIndex,
                                   IndexFin=LastIndex,
                                   TextField="",
                                   comment="")
    NewTransformer.save()




def TraitBiblioAvantLast(doc,list_id_last_biblioj):

    # Normalement list_id_last_biblioj est une liste de liste composé que d'un élément
    list_intervalles_mots_retirer = GetIntervalleMotsParFenetre(list_id_last_biblioj[0])

    if len(list_intervalles_mots_retirer) > 0:

        for l, eltagreg in enumerate(list_intervalles_mots_retirer):


            NewTransformer = Transformer(DocExtractRef=doc,
                                           type='Biblio',
                                           IndexDeb=eltagreg[0] - 1,
                                           IndexFin=eltagreg[1],
                                           TextField="",
                                           comment="")
            NewTransformer.save()





def InsertNewBiblio(reduction, donnees):

    SupprBilioEtFin = donnees['SupprBilioEtFin']
    StopMots = donnees['mots']
    Zone = donnees['zone']


    reductionencours = CorpusEtude.objects.filter(nom=reduction)
    docsextractencours = DocExtractInitial.objects.filter(CorpusEtudeRef=reductionencours[0])
    for doc in docsextractencours:
        nomfichierencours = doc.DocReferenceRef.TextRef
        addressedocencours = GetAdresseCompletDoc(nomfichierencours)
        # recupére des biblios
        BiblioCoordinatesDocEnCours = DocErudit(addressedocencours, typesegment="biblio")

        if len(BiblioCoordinatesDocEnCours.obj) > 0 :
            Pagesbiblio = [part[0] for part in BiblioCoordinatesDocEnCours.obj]
            IndexPageLastBiblio = RenvoiIndexPageLastBiblio(Pagesbiblio)

            # recupére tous les mots
            MotsPageEnCours = DocMotPage(addressedocencours, detail=True)

            if doc.DocReferenceRef.type == "article":

                if IndexPageLastBiblio == 0 :
                    # traite la biblio en enlevant jusqu'a la fin
                    CoordBiblio = [BiblioCoordinatesDocEnCours.obj[0]]
                    list_id_last_biblio = GetListIDMots(CoordBiblio, MotsPageEnCours)
                    if len(list_id_last_biblio[0]) > 0 and SupprBilioEtFin:
                        TraitLastBiblio(doc,list_id_last_biblio, MotsPageEnCours)
                    if len(list_id_last_biblio[0]) > 0 and len(StopMots) > 0 and Zone > 0:
                        ProcedureRetraitMotAvt(doc, Zone, StopMots, 0, BiblioCoordinatesDocEnCours, MotsPageEnCours, list_id_last_biblio[0][0])

                if IndexPageLastBiblio > 0:
                    # traite les biblios avant la dernière selon coordonnées graphiques
                    for j in range(0, IndexPageLastBiblio):
                        BiblioJ = [BiblioCoordinatesDocEnCours.obj[j]]
                        list_id_last_biblioj = GetListIDMots(BiblioJ, MotsPageEnCours)
                        if len(list_id_last_biblioj[0]) > 0 and SupprBilioEtFin:
                            TraitBiblioAvantLast(doc,list_id_last_biblioj)
                        if len(list_id_last_biblioj[0]) > 0  and len(StopMots) > 0 and Zone > 0:
                            ProcedureRetraitMotAvt(doc, Zone, StopMots, j, BiblioCoordinatesDocEnCours,
                                                   MotsPageEnCours, list_id_last_biblioj[0][0])

                    # traite la dernière biblio en enlevant jusqu'à la fin
                    CoordLastBiblio = [BiblioCoordinatesDocEnCours.obj[IndexPageLastBiblio]]
                    list_id_last_biblio = GetListIDMots(CoordLastBiblio, MotsPageEnCours)
                    if len(list_id_last_biblio[0]) > 0 and SupprBilioEtFin:
                        TraitLastBiblio(doc, list_id_last_biblio, MotsPageEnCours)
                    if len(list_id_last_biblio[0]) > 0 and len(StopMots) > 0 and Zone > 0:
                        ProcedureRetraitMotAvt(doc, Zone, StopMots, 0, BiblioCoordinatesDocEnCours, MotsPageEnCours,
                                               list_id_last_biblio[0][0])

            if doc.DocReferenceRef.type == "compterendu":

                # itère sur toutes les biblios
                # enlève selon coordonnées graphiques
                for j in range(0, len(BiblioCoordinatesDocEnCours.obj)):
                    BiblioJ = [BiblioCoordinatesDocEnCours.obj[j]]
                    list_id_last_biblioj = GetListIDMots(BiblioJ, MotsPageEnCours)
                    if len(list_id_last_biblioj[0]) > 0 and SupprBilioEtFin:
                        TraitBiblioAvantLast(doc, list_id_last_biblioj)
                    if len(list_id_last_biblioj[0]) > 0  and len(StopMots) > 0 and Zone > 0:
                        ProcedureRetraitMotAvt(doc, Zone, StopMots, j, BiblioCoordinatesDocEnCours,
                                               MotsPageEnCours, list_id_last_biblioj[0][0])


