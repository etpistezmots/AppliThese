import os, sys, csv
from django.conf import settings
import pandas as pd


def CountOccSimple(donnees):
    ListTermes = donnees["terme"].split(",")
    ListEpoques = donnees["epoque"].split(",")
    ListRevues = donnees["revue"].split(",")
    ListEpoquesDecompos = []
    for elt in ListEpoques:
        dateinf = int(elt.split("-")[0])
        datesup = int(elt.split("-")[1])
        ListEpoquesDecompos.append((dateinf, datesup))

    df = pd.DataFrame(columns=ListEpoques)
    for i in range(len(ListRevues)):
        df.loc[i] = [0 for n in range(len(ListEpoques))]
    df.index = ListRevues
    fileencours = settings.RESULT_PRETRAIT_DIR + "/FinaliseCorpus/CorpusFin/" + donnees['CorpusFinRef'].nom + ".csv"
    if os.path.isfile(fileencours):
        with open(fileencours, 'r') as f_in:
            csv.field_size_limit(sys.maxsize)
            reader = csv.reader(f_in, delimiter='\t')
            next(reader)  # skip the heading
            for row in reader:
                IdEncours, NomPerseeEnCours, RevueEnCours, DateEnCours, TypeEnCours, TitreEnCours, AuteursEnCours, TextEnCours = row
                for i, revue in enumerate(ListRevues):
                    for j, EpoqueDecompos in enumerate(ListEpoquesDecompos):
                        dateinf = EpoqueDecompos[0]
                        datemax = EpoqueDecompos[1]
                        if int(DateEnCours) >= dateinf and int(DateEnCours) <= datemax and RevueEnCours == revue:
                            for terme in ListTermes:
                                comptelocal = TextEnCours.count(" " + terme + " ")
                                if comptelocal > 0:
                                    df.iloc[i, j] = df.iloc[i, j] + comptelocal

    return df


def CountOccByAuthor(donnees, n_auteurs):
    ListTermes = donnees["terme"].split(",")
    ListEpoques = donnees["epoque"].split(",")
    ListRevues = donnees["revue"].split(",")
    ListEpoquesDecompos = []
    for elt in ListEpoques:
        dateinf = int(elt.split("-")[0])
        datesup = int(elt.split("-")[1])
        ListEpoquesDecompos.append((dateinf, datesup))

    df = pd.DataFrame(columns=ListEpoques)
    for i in range(len(ListRevues)):
        df.loc[i] = [[] for n in range(len(ListEpoques))]
    df.index = ListRevues
    fileencours = settings.RESULT_PRETRAIT_DIR + "/FinaliseCorpus/CorpusFin/" + donnees['CorpusFinRef'].nom + ".csv"
    if os.path.isfile(fileencours):
        with open(fileencours, 'r') as f_in:
            csv.field_size_limit(sys.maxsize)
            reader = csv.reader(f_in, delimiter='\t')
            next(reader)  # skip the heading
            for row in reader:
                IdEncours, NomPerseeEnCours, RevueEnCours, DateEnCours, TypeEnCours, TitreEnCours, AuteursEnCours, TextEnCours = row
                for i, revue in enumerate(ListRevues):
                    for j, EpoqueDecompos in enumerate(ListEpoquesDecompos):
                        dateinf = EpoqueDecompos[0]
                        datemax = EpoqueDecompos[1]
                        if int(DateEnCours) >= dateinf and int(
                                DateEnCours) <= datemax and RevueEnCours == revue:
                            for terme in ListTermes:
                                comptelocal = TextEnCours.count(" " + terme + " ")
                                if comptelocal > 0:
                                    auteurlist = AuteursEnCours.split(",")
                                    for auteur in auteurlist:
                                        if auteur!="":
                                            df.iloc[i, j] = df.iloc[i, j] + [(auteur, comptelocal)]

        for i, revue in enumerate(ListRevues):
            for j, EpoqueDecompos in enumerate(ListEpoquesDecompos):
                if df.iloc[i, j] == []:
                    df.iloc[i, j] = ""
                else:
                    resultagreg = []
                    for elt in df.iloc[i, j]:
                        listauteursdejapresents = [elt1[0] for elt1 in resultagreg]
                        if elt[0] in listauteursdejapresents:
                            index = listauteursdejapresents.index(elt[0])
                            Resultdejaexistant = resultagreg[index]
                            NewCompte = elt[1] + Resultdejaexistant[1]
                            resultagreg[index] = (elt[0], NewCompte)
                        else:
                            resultagreg.append(elt)
                    # tri
                    resultagreg.sort(key=lambda tup: tup[1], reverse=True)
                    newresult = ""
                    for k, elt in enumerate(resultagreg):
                        if k < n_auteurs:
                            newresult = newresult + elt[0] + " (" + str(elt[1]) + ")" + "\n"
                    df.iloc[i, j] = newresult
    return df
