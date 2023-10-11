from AllApps.PreTraitement.Persee.DelimitCorpus.core import GetAdresseCompletDoc, FctSpeRecupResultComplexe
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.CommunAllFct import TrameGenerale,EcritureResultComplex
from AllApps.PreTraitement.Persee.DelimitCorpus.outils.xpath import DocErudit
from lxml import etree

def AnnexeDivPlusieursPagesSpe(doc):
    ResultInd = None
    XpathAnnexe = "/tei:TEI/tei:text/tei:body/tei:div[@type='appxdiv']"
    nomfichierencours = doc.DocReferenceRef.TextRef
    addressedocencours = GetAdresseCompletDoc(nomfichierencours)
    tree = etree.parse(addressedocencours)
    AnnexesEnCours = tree.xpath(XpathAnnexe, namespaces={"tei": "http://www.tei-c.org/ns/1.0"})
    NbreAnnexes = len(AnnexesEnCours)
    if NbreAnnexes > 0:
        print(nomfichierencours)
        ListNbrBalisePbInAnnexe = []
        for annexe in AnnexesEnCours:
            CountAnnexePb = 0
            for annexepb in annexe.iterchildren(tag="{http://www.tei-c.org/ns/1.0}pb"):
                CountAnnexePb += 1
            ListNbrBalisePbInAnnexe.append(str(CountAnnexePb))
            ResultInd = ['<a href="https://www.persee.fr/doc/' +
                          nomfichierencours[8:-8] + '">' + nomfichierencours[8:-8] + '</a>',
                         NbreAnnexes,
                         str(NbreAnnexes),
                         ",".join(ListNbrBalisePbInAnnexe)]
    return ResultInd


def AnnexeDivPlusieursPagesDo(FichierResult,reduction,revue):
    error, Result, NbreResult = TrameGenerale(FichierResult, reduction, revue, AnnexeDivPlusieursPagesSpe,
                                              EcritureResultComplex,FctSpeRecupResultComplexe,
                                              listinsert=["Identifiant document Persée (lien portail)",
                                                          "Nombre d'annexes dans le document",
                                                          "Nombre de segments 'saut de page' dans chaque annexe"],
                                              nsort=1,nsuppr=1)
    return error, Result, NbreResult


def ExploreEruditDonneesSpe(doc):
    ResultInd = None
    nomfichierencours = doc.DocReferenceRef.TextRef
    addressedocencours = GetAdresseCompletDoc(nomfichierencours)
    DonneesCoordinatesDocEnCours = DocErudit(addressedocencours, typesegment="donnee")
    NbreDonnees = len(DonneesCoordinatesDocEnCours.obj)
    if NbreDonnees > 0:
        ResultInd =['<a href="https://www.persee.fr/doc/' +
                           nomfichierencours[8:-8] + '">' + nomfichierencours[8:-8] + '</a>',
                    NbreDonnees,
                    str(NbreDonnees)]
    return ResultInd


def ExploreEruditDonneesDo(FichierResult,reduction,revue):
    error, Result, NbreResult = TrameGenerale(FichierResult, reduction, revue, ExploreEruditDonneesSpe,
                                              EcritureResultComplex, FctSpeRecupResultComplexe,
                                              listinsert=["Identifiant document Persée (lien portail)",
                                                          "Nombre de segments 'données' dans le document"],
                                              nsort=1,nsuppr=1)
    return error, Result, NbreResult

