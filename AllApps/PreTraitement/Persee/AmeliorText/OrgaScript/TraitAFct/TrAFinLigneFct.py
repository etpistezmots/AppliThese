import os, pickle
from django.conf import settings
from AllApps.PreTraitement.Persee.DelimitCorpus.outils.xpath import DocMotLigne
from AllApps.PreTraitement.Persee.DelimitCorpus.models import DocExtractInitial, CorpusEtude, Transformer
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.AideTitreFct import GetAdresseCompletDoc


def CreateDicoLitige():

    ResultDicoLitigePickle = settings.DATA_DIR + '/Dico/DicoMotLitige'
    ResultDicoLitigeListPickle = settings.DATA_DIR + '/Dico/DicoMotLitigeList'
    AdresseDicoBase1 = settings.DATA_DIR + '/Dico/DicoFusionAll.txt'
    with open(AdresseDicoBase1) as f:
        content = f.readlines()

    AdresseDicoBase2 = settings.DATA_DIR + '/Dico/DicoAllPythonDico'

    infile = open(AdresseDicoBase2, 'rb')
    DicoParDeuxPremieresLettres = pickle.load(infile)
    infile.close()

    AllMotSup2 = []
    for line in content:
        mot = line[:-1]
        # il faut prendre deux car ex : la masse
        # même si beaucoup de syllabes beaucoup plus marginales
        if len(mot) >= 2:
            AllMotSup2.append(mot)

    DicoResult = {}
    DicoResultList = {}
    for i, mot in enumerate(AllMotSup2):
        print(i)
        # attention , quelques cas marginal ou ce n'est pas le cas
        # car DicoParDeuxPremieresLettres contruit avec mot >=4
        # alors que AllSup2 avec mot >=2
        if mot[0:2] in DicoParDeuxPremieresLettres:
            DicoRecherche = DicoParDeuxPremieresLettres[mot[0:2]]
            DicoRechercheAffine = [elt for elt in DicoRecherche if elt[0:len(mot)] == mot]
            # s'il est tout seul dans sa liste : pas la peine de continuer
            if len(DicoRechercheAffine) == 2:
                # test si c'est pas juste un pluriel
                if DicoRechercheAffine[0] == DicoRechercheAffine[1] + "s":
                    continue
                elif DicoRechercheAffine[0] == DicoRechercheAffine[1] + "x":
                    continue
                else:
                    for mot1 in AllMotSup2:
                        motagreg = mot + mot1
                        if motagreg in DicoRechercheAffine:
                            if mot[0:2] not in DicoResult.keys():
                                DicoResult[mot[0:2]] = []
                                DicoResult[mot[0:2]].append(motagreg)
                                DicoResultList[mot[0:2]] = []
                                DicoResultList[mot[0:2]].append([mot, mot1])
                            else:
                                DicoResult[mot[0:2]].append(motagreg)
                                DicoResultList[mot[0:2]].append([mot, mot1])

            if len(DicoRechercheAffine) > 2:
                for mot1 in AllMotSup2:
                    motagreg = mot + mot1
                    if motagreg in DicoRechercheAffine:
                        if mot[0:2] not in DicoResult.keys():
                            DicoResult[mot[0:2]] = []
                            DicoResult[mot[0:2]].append(motagreg)
                            DicoResultList[mot[0:2]] = []
                            DicoResultList[mot[0:2]].append([mot, mot1])
                        else:
                            DicoResult[mot[0:2]].append(motagreg)
                            DicoResultList[mot[0:2]].append([mot, mot1])

    outfile = open(ResultDicoLitigePickle, 'wb')
    pickle.dump(DicoResult, outfile)
    outfile.close()

    outfile = open(ResultDicoLitigeListPickle, 'wb')
    pickle.dump(DicoResultList, outfile)
    outfile.close()




def NormalisePart1(mot):
    # tout en majuscule
    if mot.isupper():
        return mot.lower(), 1
    # seulement la première lettre en majuscule
    if len(mot) > 1 and mot[0].isupper() and mot[1:].islower():
        return mot.lower(), 2
    # commence par une parenthèse
    if mot[0] == "(":
        return mot[1:], 3
    # commence par un guillemet "
    if mot[0] == '"':
        return mot[1:], 7
    # commence par un guillemet <<
    if len(mot) > 1 and mot[0:1] == "<<":
        return mot[2:], 9
    # commence par un guillemet ''
    if len(mot) > 1 and mot[0:1] == "''":
        return mot[2:], 11
    # commence par un guillemet '
    if len(mot) > 1 and mot[0] == "'":
        return mot[2:], 19
    # finit par un tiret
    if mot[-1] == '-':
        return mot[:-1], 16
    # commence par un guillemet l'
    if len(mot) > 1 and mot[0:1] == "l'":
        return mot[2:], 17
    # commence par un guillemet L'
    if len(mot) > 1 and mot[0:1] == "L'":
        return mot[2:], 18
    # si c'est pas un cas précédent
    return mot, 0


def NormalisePart2(mot):
    # tout en majuscule
    if mot.isupper():
        return mot.lower(), 1
    # finit par une parenthèse
    if mot[-1] == ")":
        return mot[:-1], 4
    # finit par un point
    if mot[-1] == ".":
        return mot[:-1], 5
    # finit par une virgule
    if mot[-1] == ",":
        return mot[:-1], 6
    # finit par un un guillement "
    if mot[-1] == '"':
        return mot[:-1], 8
    # finit par un un guillement >>
    if len(mot) > 1 and mot[-2:-1] == ">>":
        return mot[:-2], 10
    # finit par un un guillement ''
    if len(mot) > 1 and mot[-2:-1] == "''":
        return mot[:-2], 12
    # finit par un un guillement ''
    if len(mot) > 1 and mot[-1] == "'":
        return mot[:-1], 20
    # finit par deux chiffres
    if len(mot) > 1 and mot[-1].isnumeric() and mot[-2].isnumeric():
        return mot[:-2], 14
    # finit par un chiffre
    if mot[-1].isnumeric():
        return mot[:-1], 13
    # commence par un tiret
    if mot[0] == '-':
        return mot[1:], 15
    # si c'est pas un cas précédent
    return mot, 0

def ReConstructWord(mot, indicedeb, indicefin):
    debphrase = ""
    finphrase = ""
    newmot = mot
    # si tout en majuscule à la base  --> renvoie en majuscule
    if indicedeb == 1 and indicefin == 1:
        newmot = mot.upper()
    # pour le cas ou une seule majuscule:
    # doit être géré dans le code principal
    # car cas ou c'est un nom propre
    # et cas ou c'est un début de phrase
    if indicedeb == 3:
        debphrase = "("
    if indicefin == 4:
        finphrase = ")"
    if indicefin == 5:
        finphrase = "."
    if indicefin == 6:
        finphrase = ","
    if indicedeb == 7:
        debphrase = '"'
    if indicefin == 8:
        finphrase = '"'
    if indicedeb == 9:
        debphrase = "<<"
    if indicefin == 10:
        finphrase = ">>"
    if indicedeb == 11:
        debphrase = "''"
    if indicefin == 12:
        finphrase = "''"
    # Pour le 13 et le 14, j'enlève le chiffre
    # pas de changement

    # Pour le 15 et le 16,
    # doit être géré dans le code principal
    # car cas où c'est un nom composé
    # et cas où c'est un artifice typo
    if indicedeb == 17:
        debphrase = "l'"
    if indicedeb == 18:
        debphrase = "L'"
    if indicedeb == 19:
        debphrase = "'"
    if indicedeb == 20:
        debphrase = "'"
    motfinal = debphrase + newmot + finphrase
    return motfinal

def TestMotComposeTrait(motcompose,motcomposecle,motdeb,motfin,DicoLitigeMot,DicoLitigeMotList,i, doc):
    if (motcomposecle in DicoLitigeMot.keys()) and (motcompose in DicoLitigeMot[motcomposecle]):
        indexes = [j for j, eltlitige in enumerate(DicoLitigeMot[motcomposecle]) if
                   eltlitige == motcompose]
        marqueurtest = True
        for index in indexes:
            if motdeb == DicoLitigeMotList[motcomposecle][index][0] and motfin == \
                    DicoLitigeMotList[motcomposecle][index][1]:
                marqueurtest = False
        if marqueurtest:
            NewTransformer = Transformer(DocExtractRef=doc,
                                           type='FinLigne',
                                           IndexDeb=i-1,
                                           IndexFin=i+1,
                                           TextField=motcompose,
                                           comment="")
            NewTransformer.save()


def TestMotComposeAndReconstructTrait(motcompose,motcomposecle,motdeb,codedeb,motfin,codefin,DicoLitigeMot,DicoLitigeMotList,i, doc):
    if (motcomposecle in DicoLitigeMot.keys()) and (motcompose in DicoLitigeMot[motcomposecle]):
        indexes = [j for j, eltlitige in enumerate(DicoLitigeMot[motcomposecle]) if
                   eltlitige == motcompose]
        marqueurtest = True
        for index in indexes:
            if motdeb == DicoLitigeMotList[motcomposecle][index][0] and motfin == \
                    DicoLitigeMotList[motcomposecle][index][1]:
                marqueurtest = False
        if marqueurtest:
            motreconstruit = ReConstructWord(motcompose, codedeb, codefin)
            NewTransformer = Transformer(DocExtractRef=doc,
                                           type='FinLigne',
                                           IndexDeb=i - 1,
                                           IndexFin=i + 1,
                                           TextField=motreconstruit,
                                           comment="")
            NewTransformer.save()


def ReconstructComplexeTrait(motencours, codedeb, motdeb, motnormdeb, i, elt, KeysDicoGeneral, DicoGeneral,
                        DicoLitigeMot,DicoLitigeMotList):
    # test si mot avant + mot dans dico
    motfin = motencours[0]
    motnormfin, codefin = NormalisePart2(motfin)
    reconstituemotnorm = motnormdeb + motnormfin
    reconstituemotnormcle = reconstituemotnorm[0:2]
    # Si c'est une majuscule au départ:
    if codedeb == 2:
        motexceptionmajuscule = motdeb + motnormfin
        motexceptionmajusculecle = motexceptionmajuscule[0:2]
        # on teste déjà le cas nom propre
        if motexceptionmajusculecle in KeysDicoGeneral and \
                        motexceptionmajuscule in DicoGeneral[motexceptionmajusculecle]:
            TestMotComposeTrait(motexceptionmajuscule, motexceptionmajusculecle, motdeb, motnormfin,
                                                               DicoLitigeMot, DicoLitigeMotList,i,elt)

        else:
            if reconstituemotnormcle in KeysDicoGeneral and \
                            reconstituemotnorm in DicoGeneral[reconstituemotnormcle]:
                TestMotComposeAndReconstructTrait(reconstituemotnorm, reconstituemotnormcle, motnormdeb,
                                                                   codedeb, motnormfin, codefin,
                                                                   DicoLitigeMot, DicoLitigeMotList,i,elt)
    # Si finit par un tiret
    elif codedeb == 16:
        # on teste déjà le cas nom composé
        motexceptiontiret = motdeb + motnormfin
        motexceptiontiretcle = motexceptiontiret[0:2]
        if motexceptiontiretcle in KeysDicoGeneral and \
                        motexceptiontiret in DicoGeneral[motexceptiontiretcle]:
            TestMotComposeTrait(motexceptiontiret, motexceptiontiretcle, motdeb, motnormfin,
                                                 DicoLitigeMot, DicoLitigeMotList,i,elt)
        else:
            if reconstituemotnormcle in KeysDicoGeneral and \
                            reconstituemotnorm in DicoGeneral[reconstituemotnormcle]:
                TestMotComposeAndReconstructTrait(reconstituemotnorm, reconstituemotnormcle, motnormdeb,
                                                                   codedeb, motnormfin, codefin,
                                                                   DicoLitigeMot, DicoLitigeMotList,i,elt)
    # sinon
    else:
        if reconstituemotnormcle in KeysDicoGeneral and \
                        reconstituemotnorm in DicoGeneral[reconstituemotnorm[0:2]]:
            TestMotComposeAndReconstructTrait(reconstituemotnorm, reconstituemotnormcle, motnormdeb,
                                                               codedeb, motnormfin, codefin,
                                                               DicoLitigeMot, DicoLitigeMotList, i, elt)


def InsertNewFinLigne(reduction, donnees):

    normalise = donnees['normalise']

    # creer deux dicos par deux premières lettres
    # accèlère grandement les recherche par la suite
    ResultDicoLitigePickle = settings.DATA_DIR + '/Dico/DicoMotLitige'
    ResultDicoLitigeListPickle = settings.DATA_DIR + '/Dico/DicoMotLitigeList'

    # s'il n'exite pas déjà
    # Attention assez long !
    if not os.path.isfile(ResultDicoLitigePickle) and not(os.path.isfile(ResultDicoLitigeListPickle)):
        CreateDicoLitige()

    print('OK')
    # les charge
    infile = open(ResultDicoLitigePickle, 'rb')
    DicoLitigeMot = pickle.load(infile)
    infile.close()

    infile = open(ResultDicoLitigeListPickle, 'rb')
    DicoLitigeMotList = pickle.load(infile)
    infile.close()

    ResultDicoGeneralPickle = settings.DATA_DIR + '/Dico/DicoAllPythonDico'
    infile = open(ResultDicoGeneralPickle, 'rb')
    DicoGeneral = pickle.load(infile)
    infile.close()
    KeysDicoGeneral = DicoGeneral.keys()


    reductionencours = CorpusEtude.objects.filter(nom=reduction)
    docsextractencours = DocExtractInitial.objects.filter(CorpusEtudeRef=reductionencours[0])


    for doc in docsextractencours:
        nomfichierencours = doc.DocReferenceRef.TextRef
        addressedocencours = GetAdresseCompletDoc(nomfichierencours)
        TousLesMotsLignes = DocMotLigne(addressedocencours)


        for i, mot_i in enumerate(TousLesMotsLignes):
            # cas premier mot
            if i == 0:
                motdeb = mot_i[0]
                if normalise:
                    motnormdeb, codedeb = NormalisePart1(motdeb)
            # pour les autres mots
            else:
                if mot_i[5] == "n":
                    if normalise:
                        ReconstructComplexeTrait(mot_i, codedeb, motdeb, motnormdeb, i, doc,
                                                KeysDicoGeneral, DicoGeneral, DicoLitigeMot,DicoLitigeMotList)
                    else:
                        motfin = mot_i[0]
                        motcompose = motdeb + motfin
                        motcomposecle = motcompose[0:2]
                        # si mot composé est dans le dico général
                        if motcomposecle in KeysDicoGeneral and motcompose in DicoGeneral[motcomposecle]:
                            # si mot peut composé un litige
                            TestMotComposeTrait(motcompose, motcomposecle, motdeb, motfin, DicoLitigeMot, DicoLitigeMotList,i, doc)

                # ré-initialise pour continuer la boucle
                motdeb = mot_i[0]
                if normalise:
                    motnormdeb, codedeb = NormalisePart1(motdeb)



