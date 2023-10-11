import os, operator
from AllApps.PreTraitement.Persee.DelimitCorpus.models import CorpusEtude, DocExtractInitial


def CreateDossier(FichierResult):
    dossier = FichierResult.rsplit("/", 1)[0]
    if not os.path.exists(dossier):
        os.makedirs(dossier)


def TrameGenerale(FichierResult,reduction,revue, FctSpeTrait, FctSpeEcriture, FctSpeLecture, listinsert=[],
                  nsort=-1,ordreverse=False,nsuppr=-1):

    error = False
    Result = []
    NbreResult = 0

    Test = CorpusEtude.objects.filter(nom=reduction)
    if Test.exists():
        CEenCours = Test[0]

        # si le fichier de résultat n'a pas encore été crée
        if not os.path.isfile(FichierResult):
            # création des résultats
            docsextractencours = DocExtractInitial.objects.filter(CorpusEtudeRef=CEenCours)
            for doc in docsextractencours:
                if doc.DocReferenceRef.RevueRef.nompersee == revue:
                    ResultInd = FctSpeTrait(doc)
                    if ResultInd is not None:
                        Result.append(ResultInd)
            CreateDossier(FichierResult)
            Result = FctSpeEcriture(FichierResult, Result, listinsert, nsort, ordreverse, nsuppr)

        # sinon lit directement le ficher des résultats
        else:
            Result = FctSpeLecture(FichierResult, len(listinsert))
            print(Result)
        # -1 car il y a eu insertion de la légende
        NbreResult = len(Result)-1

    else:
        error = True

    return error, Result, NbreResult


def Supprn(lista, n):
    NewList = []
    for t in lista:
        t.pop(n)
        NewList.append(t)
    return NewList


def EcritureResultComplex(FichierResult, Result, listinsert, nsort=-1,ordreverse=False, nsuppr=-1):

    if nsort!=-1:
        #Result.sort(key=lambda x: x[nsort])
        Result = sorted(Result, key=operator.itemgetter(nsort), reverse=ordreverse)

    # permet de supprimer un champ si nécessaire
    # peut être pratique faire tri sur champs "int" mais après garde seulement str
    if nsuppr!=-1:
        Result = Supprn(Result, nsuppr)

    with open(FichierResult, 'w') as f:
        for elt in listinsert:
            f.write(elt + "\n")
        f.write("\n")

        for SsResult in Result:
            for i in range(len(listinsert)):
                f.write(SsResult[i] + "\n")
            f.write("\n")

    # Insertion de la légende
    Result.insert(0, [elt + "\n" for elt in listinsert])
    return Result


def EcritureResultIllimit(FichierResult, Result, listinsert, nsort = -1, ordreverse = False, nsuppr = -1):

    if nsort != -1:
        # Result.sort(key=lambda x: x[nsort])
        Result = sorted(Result, key=operator.itemgetter(nsort), reverse=ordreverse)

    # permet de supprimer un champ si nécessaire
    # peut être pratique faire tri sur champs "int" mais après garde seulement str
    if nsuppr != -1:
        Result = Supprn(Result, nsuppr)

    with open(FichierResult, 'w') as f:
        for elt in listinsert:
            f.write(elt + "\n")
        f.write("\n")

        for SsResult in Result:
            for ssres in SsResult:
                f.write(ssres + "\n")
            f.write("\n")

    # Insertion de la légende
    Result.insert(0, [elt + "\n" for elt in listinsert])
    return Result


def LectureResultIllimit(FichierResult, varadjust):
    with open(FichierResult, 'r') as f:
        content = f.readlines()
        Result = []
        SsResult = []
        for elt in content:
            if elt != "\n":
                SsResult.append(elt.rstrip())
            else:
                Result.append(SsResult)
                SsResult = []
    return Result



def TrameGeneraleList(FichierResult,reduction,revue, FctSpeTrait, FctSpeEcriture, FctSpeLecture, listinsert=[],nlist=0,
                  nsort=-1,ordreverse=False,nsuppr=-1):

    error = False
    Result = []
    for i in range(nlist):
        Result.append([])

    NbreResult = 0

    Test = CorpusEtude.objects.filter(nom=reduction)
    if Test.exists():
        CEenCours = Test[0]

        # si le fichier de résultat n'a pas encore été crée
        if not os.path.isfile(FichierResult):
            # création des résultats
            docsextractencours = DocExtractInitial.objects.filter(CorpusEtudeRef=CEenCours)
            for doc in docsextractencours:
                if doc.DocReferenceRef.RevueRef.nompersee == revue:
                    Result = FctSpeTrait(doc,revue,Result)
            CreateDossier(FichierResult)
            Result = FctSpeEcriture(FichierResult, Result, listinsert, nsort, ordreverse, nsuppr)

        # sinon lit directement le ficher des résultats
        else:
            Result = FctSpeLecture(FichierResult, len(listinsert))

        # -1 car il y a eu insertion de la légende
        NbreResult = len(Result[0])-1

    else:
        error = True

    return error, Result, NbreResult



def EcritureResultList(FichierResult, Result, listinsert, nsort = -1, ordreverse = False, nsuppr = -1):

    if nsort != -1:
        # Result.sort(key=lambda x: x[nsort])
        Ord = sorted(sorted(range(len(Result[nsort])), key=lambda k: Result[nsort][k]), reverse=ordreverse)
        for i,sslist in enumerate(Result):
            sslistOrd = [sslist[elt] for elt in Ord]
            Result[i]= sslistOrd

    # permet de supprimer un champ si nécessaire
    # peut être pratique faire tri sur champs "int" mais après garde seulement str
    if nsuppr != -1:
        Result.pop(nsuppr)

    with open(FichierResult, 'w') as f:
        for elt in listinsert:
            f.write(elt + "\n")
        f.write("\n")

        for i in range(len(Result[0])):
            for sslist in Result:
                f.write(sslist[i] + "\n")
            f.write("\n")

    # Insertion de la légende
    for i,sslist in enumerate(Result):
        sslist.insert(0, listinsert[i])

    return Result


def LectureResultList(FichierResult,n):
    Result = []

    for i in range(n):
        Result.append([])

    with open(FichierResult, 'r') as f:
        content = f.readlines()
        i = -1
        for elt in content:
            if elt == "\n":
                i = -1
            else:
                i = i + 1
                Result[i].append(elt.rstrip())
    return Result




def SimplifyObject(object):
    objetred = object.split(")")[1]
    if objetred == "Mots-Cles":
        objetred = "MotCle"
    return objetred


def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False


def StringToSearchInErudit(object):
    # dans spgeo listes des segments erudit
    # ['notebio', 'resume', 'biblio', 'titre1', 'figure', 'grtitre', 'autre', 'note', 'titre2', 'tableau', 'annexe', 'noteedito', 'donnee']
    # dans geo
    # ['grtitre', 'titre1', 'autre', 'note', 'titre2', 'figure', 'tableau', 'biblio', 'notebio', 'resume', 'annexe', 'donnee', 'noteedito', 'titre3']
    # tableau compris dans figure quand recherche dans tei !!
    if object == "SousTitre":
        return "titre1"
    else:
        return object.lower()