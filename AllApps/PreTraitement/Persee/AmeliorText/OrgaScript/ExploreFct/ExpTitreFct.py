import os
from AllApps.PreTraitement.Persee.DelimitCorpus.models import  CorpusEtude, DocExtractInitial
from AllApps.PreTraitement.Persee.DelimitCorpus.outils.xpath import  DocMot, DocMotLigne
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.AideTitreFct import GetTitreTrouvesDansTexte
from AllApps.PreTraitement.Persee.DelimitCorpus.core import GetAdresseCompletDoc, FctSpeRecupResultComplexe
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.CommunAllFct import TrameGenerale,EcritureResultComplex



def AfficheTitreSpe(doc):
    titreencours = doc.DocReferenceRef.titre.replace("\n", "")
    dateencours = doc.DocReferenceRef.annee
    ResultInd = [titreencours, dateencours, str(dateencours)]
    return ResultInd


def AfficheTitreDo(FichierResult,reduction,revue):
    error, Result, NbreResult = TrameGenerale(FichierResult,reduction,revue,
                                              AfficheTitreSpe,EcritureResultComplex,
                                              FctSpeRecupResultComplexe, listinsert=["Titre du document","Date du document"],
                                              nsort=1, nsuppr=1)
    return error, Result, NbreResult


def AfficheTitreSlashSpe(doc):
    ResultInd = None
    titreencours = doc.DocReferenceRef.titre.replace("\n", "")
    # https://www.pitt.edu/~naraehan/python2/tutorial7.html
    #  "\" can be used to escape itself: "\\" is the literal backslash character
    if "/" in titreencours:
        dateencours = doc.DocReferenceRef.annee
        ResultInd = [titreencours, dateencours, str(dateencours)]
    return ResultInd


def AfficheTitreSlashDo(FichierResult,reduction,revue):
    error, Result, NbreResult = TrameGenerale(FichierResult, reduction, revue, AfficheTitreSlashSpe,
                                              EcritureResultComplex,FctSpeRecupResultComplexe,
                                              listinsert=["Titre du document","Date du document"],
                                              nsort=1,nsuppr=1)
    return error, Result, NbreResult



def AfficheTitreFoundSpe(doc):
    ResultInd = None
    nomfichierencours = doc.DocReferenceRef.TextRef
    addressedocencours = GetAdresseCompletDoc(nomfichierencours)
    Touslesmotsdoc = DocMot(addressedocencours)
    titreencours = doc.DocReferenceRef.titre.replace("\n", "")
    ResultTitreTrouve = GetTitreTrouvesDansTexte(titreencours,
                                                 Touslesmotsdoc,
                                                 0.95,
                                                 50)
    if ResultTitreTrouve:
        ResultInd =['<a href="https://www.persee.fr/doc/' +nomfichierencours[8:-8] + '">' + nomfichierencours[8:-8] + '</a>',
                    ResultTitreTrouve["matching_score"],
                    ResultTitreTrouve["matching_score_str"],
                    ResultTitreTrouve["titre_texte_corrige"],
                    ResultTitreTrouve["titre"],
                    str(ResultTitreTrouve["IndexDebut"]) + " - " + str(ResultTitreTrouve["IndexFin"])]
    return ResultInd


def AfficheTitreFoundDo(FichierResult,reduction,revue):
    error, Result, NbreResult = TrameGenerale(FichierResult, reduction, revue, AfficheTitreFoundSpe,
                                              EcritureResultComplex, FctSpeRecupResultComplexe,
                                              listinsert=["Identifiant document Persée (lien portail)",
                                                          "Score de ressemblance (mesure de Ratcliff/Obershelp)",
                                                          "Chaîne de caractère trouvée dans l'OCR présumée la plus correspondre au titre",
                                                          "Titre métadonnées (documenté par Persée)",
                                                          "Index Début - Index Fin de la chaîne de caractère présumée être le titre"],
                                              nsort=1,nsuppr=1)
    return error, Result, NbreResult

