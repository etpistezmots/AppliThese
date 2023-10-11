from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.ExploreFct.ExpCoordGraphSimpleFct import GetListIDMots, \
    GetIntervalleMotsParFenetre
from django.conf import settings

from AllApps.PreTraitement.Persee.DelimitCorpus.models import CorpusEtude, DocExtractInitial, Transformer
from AllApps.PreTraitement.Persee.DelimitCorpus.outils.xpath import DocMotPage, DocErudit
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.AideTitreFct import GetAdresseCompletDoc
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.TraitAFct.TrAResumeFct import calculsaut, \
    defineindexesfalse, resultagreg


def InsertNewCoordGraph(reduction, donnees, objet):
    if objet == "Note":
        InsertNewCoordGraphSimple(reduction, donnees, "note")
    # Quelques extensions pour s'adapter à diversité des appelations des segments erudit
    # si ce sont des notes, traitent aussi le cas notebio et noteedito
        InsertNewCoordGraphSimple(reduction, donnees, "notebio")
        InsertNewCoordGraphSimple(reduction, donnees,"noteedito")


def InsertNewCoordGraphSimple(reduction, donnees, objetred):

    SeuilAgregation = 0

    reductionencours = CorpusEtude.objects.filter(nom=reduction)
    docsextractencours = DocExtractInitial.objects.filter(CorpusEtudeRef=reductionencours[0])
    for doc in docsextractencours:
        nomfichierencours = doc.DocReferenceRef.TextRef
        addressedocencours = GetAdresseCompletDoc(nomfichierencours)
        DataCoordinatesDocEnCours = DocErudit(addressedocencours, typesegment=objetred)
        MotsPageDocEnCours = DocMotPage(addressedocencours, detail=True)
        list_id_mots_coord_graph = GetListIDMots(DataCoordinatesDocEnCours.obj,
                                                   MotsPageDocEnCours)

        for k, coord_graph in enumerate(list_id_mots_coord_graph):

            list_intervalles_mots_retirer = GetIntervalleMotsParFenetre(coord_graph)
            # Si une fenêtre graphique ne génère pas un et un seul intervalle
            if len(list_intervalles_mots_retirer) > 1:
                # procédure d'agrégation
                saut = calculsaut(list_intervalles_mots_retirer)
                indexesfalse = defineindexesfalse(saut, int(SeuilAgregation))
                myresultagreg = resultagreg(list_intervalles_mots_retirer, indexesfalse)
                # après il faut insérer dans la base de données
                for l,eltagreg in enumerate(myresultagreg):
                    NewTransformer = Transformer(DocExtractRef=doc,
                                                       type=objetred,
                                                       IndexDeb=eltagreg[0] - 1,
                                                       IndexFin=eltagreg[1],
                                                       TextField="",
                                                       comment="")
                    NewTransformer.save()
            # si un seul intervalle
            if len(list_intervalles_mots_retirer) == 1:
                NewTransformer = Transformer(DocExtractRef=doc,
                                                   type=objetred,
                                                   IndexDeb=list_intervalles_mots_retirer[0][0] - 1,
                                                   IndexFin=list_intervalles_mots_retirer[0][1],
                                                   TextField="",
                                                   comment="")
                NewTransformer.save()



def SupprCoordGraph(reduction, objet):
    if objet == "Note":
        SupprCoordGraphSimple(reduction, "note")
    # Quelques extensions pour s'adapter à diversité des appelations des segments erudit
    # si ce sont des notes, traitent aussi le cas notebio et noteedito
        SupprCoordGraphSimple(reduction, "notebio")
        SupprCoordGraphSimple(reduction, "noteedito")


def SupprCoordGraphSimple(reduction, objetred):
    VNencours = CorpusEtude.objects.get(nom=reduction)
    EltEfface = Transformer.objects.filter(type=objetred)
    for elt in EltEfface:
        if elt.DocTransformeRef.CorpusEtudeRef==VNencours:
            elt.delete()