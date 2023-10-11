

from django.conf import settings
from lxml import etree

from AllApps.PreTraitement.Persee.DelimitCorpus.models import CorpusEtude, DocExtractInitial, Transformer
from AllApps.PreTraitement.Persee.DelimitCorpus.outils.xpath import DocMotPage, DocErudit
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.ExploreFct.ExpCoordGraphSimpleFct import GetListIDMots, \
    GetIntervalleMotsParFenetre
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.AideTitreFct import GetAdresseCompletDoc


def RecupSousTitre(document,sousobjet):
    ListeSousTitre = []
    doc_erudit = document.replace("tei", "erudit")
    tree = etree.parse(doc_erudit)
    XpathSsTitre = "/erudit:article/erudit:corps/erudit:texte//erudit:segment[@typesegment='" + sousobjet + "']"

    listeXpathSsTitre = tree.xpath(XpathSsTitre,
                           namespaces={"erudit": "http://www.erudit.org/xsd/article"})

    for sstitre in listeXpathSsTitre:
        ContenuSousTitre = ""

        for elt1 in sstitre.iterdescendants():
            ContenuSousTitre = ContenuSousTitre + " " + elt1.text

        ListeSousTitre.append(ContenuSousTitre)

    return ListeSousTitre



def InsertNewTitre123Spe(reduction, donnees,sousobjet):


    reductionencours = CorpusEtude.objects.filter(nom=reduction)
    docsextractencours = DocExtractInitial.objects.filter(CorpusEtudeRef=reductionencours[0])
    for doc in docsextractencours:
        nomfichierencours = doc.DocReferenceRef.TextRef
        addressedocencours = GetAdresseCompletDoc(nomfichierencours)
        DataCoordinatesDocEnCours = DocErudit(addressedocencours, typesegment=sousobjet)
        MotsPageDocEnCours = DocMotPage(addressedocencours, detail=True)

        ListeSousTitre = RecupSousTitre(addressedocencours,sousobjet)

        list_id_mots_soustitres = GetListIDMots(DataCoordinatesDocEnCours.obj,
                                                MotsPageDocEnCours)

        for k, soustitre in enumerate(list_id_mots_soustitres):

            list_intervalles_mots_retirer = GetIntervalleMotsParFenetre(soustitre)
            # Si une fenêtre graphique ne génère pas un et un seul intervalle
            if len(list_intervalles_mots_retirer) > 1:
                for l,eltagreg in enumerate(list_intervalles_mots_retirer):
                    # cas ajout que pour 1er intervalle
                    if l==0 and ListeSousTitre[k]!="":
                        NewTransformer = Transformer(DocExtractRef=doc,
                                               type='Titre123',
                                               IndexDeb=eltagreg[0] - 1,
                                               IndexFin=eltagreg[1],
                                               TextField= ListeSousTitre[k].replace("'","''"),
                                               comment="")
                        NewTransformer.save()
                    else :
                        NewTransformer = Transformer(DocExtractRef=doc,
                                                       type='Titre123',
                                                       IndexDeb=eltagreg[0] - 1,
                                                       IndexFin=eltagreg[1],
                                                       TextField="",
                                                       comment="")
                        NewTransformer.save()
            # si un seul intervalle
            if len(list_intervalles_mots_retirer) == 1:
                # idem cas ajout
                if ListeSousTitre[k]!="":
                    NewTransformer = Transformer(DocExtractRef=doc,
                                               type='Titre123',
                                               IndexDeb=list_intervalles_mots_retirer[0][0] - 1,
                                               IndexFin=list_intervalles_mots_retirer[0][1],
                                               TextField=ListeSousTitre[k].replace("'","''"),
                                               comment="")
                    NewTransformer.save()
                else:
                    NewTransformer = Transformer(DocExtractRef=doc,
                                                   type='Titre123',
                                                   IndexDeb=list_intervalles_mots_retirer[0][0] - 1,
                                                   IndexFin=list_intervalles_mots_retirer[0][1],
                                                   TextField="",
                                                   comment="")
                    NewTransformer.save()

def InsertNewTitre123(reduction, donnees):

    Remplace = donnees['remplace']

    # A revoir car n'est pas très efficace ...
    if Remplace:
        InsertNewTitre123Spe(reduction, donnees, "titre1")
        InsertNewTitre123Spe(reduction, donnees, "titre2")
        InsertNewTitre123Spe(reduction, donnees, "titre3")
