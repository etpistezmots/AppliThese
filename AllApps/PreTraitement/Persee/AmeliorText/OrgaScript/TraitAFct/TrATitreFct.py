from AllApps.PreTraitement.Persee.DelimitCorpus.outils.xpath import  DocRequete, DocMot
from AllApps.PreTraitement.Persee.DelimitCorpus.models import DocExtractInitial, CorpusEtude, Transformer
from django.conf import settings
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.AideTitreFct import GetTitreTrouvesDansTexte,TitreFRengPart, TitreFrenchEscApostrophe
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.AideTitreFct import GetAdresseCompletDoc


def InsertNewTitre(reduction, donnees):

    seuil = donnees['seuil']
    SupprSlashSecondPart = donnees['SupprSlashSecondPart']
    SupprBeforeTitre = donnees['SupprBeforeTitre']

    XpathType = "/tei:TEI/tei:teiHeader/@type"
    Xpathtitre = "/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title[@level='a' and @type='main']//text()"
    Xpathlangue = "/tei:TEI/tei:teiHeader/tei:profileDesc/tei:langUsage/tei:language/text()"
    XpathPage = "/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:monogr/tei:imprint/tei:biblScope[@unit='pages']/text()"
    XpathDate = "/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:monogr/tei:imprint/tei:date/text()"
    reductionencours = CorpusEtude.objects.filter(nom=reduction)
    docsextractencours = DocExtractInitial.objects.filter(CorpusEtudeRef=reductionencours[0])
    for doc in docsextractencours:
        nomfichierencours = doc.DocReferenceRef.TextRef
        addressedocencours = GetAdresseCompletDoc(nomfichierencours)
        DocEnCours = DocRequete(
            addressedocencours,
            [Xpathtitre, Xpathlangue, XpathType, XpathPage, XpathDate],
            ["titre", "langue", "type", "page", "date"],
            ["j", "j", "j","j","j"]
        )

        if DocEnCours.type == "article":

            Touslesmotsdoc = DocMot(addressedocencours)
            # replace \n à cause de cas comme article_geo_0003-4010_1970_num_79_434_15138_T1_0481_0000_5
            titre = DocEnCours.titre.replace("\n","")
            ResultTitreTrouve = GetTitreTrouvesDansTexte(titre,
                                                         Touslesmotsdoc,
                                                         0.95,  # premier seuil de ressemblance
                                                         50)  # Nbre de mots à analyser au début de la page

            if ResultTitreTrouve:
                if float(ResultTitreTrouve["matching_score"]) > seuil:
                    # pb apostrophe dans le titre et partie française si nécessaire!!!
                    if SupprSlashSecondPart and int(DocEnCours.date) >= 1999 and doc.DocReferenceRef.RevueRef.nom == "geo":
                        newtitre = TitreFRengPart(DocEnCours.langue,titre)
                    else:
                        newtitre = titre
                    newtitreesc = TitreFrenchEscApostrophe(newtitre)

                    NewTransformer = Transformer(DocExtractRef=doc,
                                                type='Titre',
                                                IndexDeb=ResultTitreTrouve["IndexDebut"],
                                                IndexFin=ResultTitreTrouve["IndexFin"]+1,
                                                TextField=newtitreesc,
                                                comment="")
                    NewTransformer.save()

                    # Suppression des éléments avant le titre
                    if SupprBeforeTitre and ResultTitreTrouve["IndexDebut"] != 0:

                        NewTransformer = Transformer(DocExtractRef=doc,
                                                       type='Titre',
                                                       IndexDeb=0,
                                                       IndexFin=ResultTitreTrouve["IndexDebut"],
                                                       TextField='',
                                                       comment="AvtTitre")


                        NewTransformer.save()




