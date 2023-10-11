import pandas as pd
import numpy as np
from django.conf import settings
from gensim.test.utils import  get_tmpfile
from gensim.models import KeyedVectors
from gensim.scripts.glove2word2vec import glove2word2vec
import os, pickle, csv, sys
from ..periph.amont import PrepaAmontEpoqueRevue, MyIter, prepaglove



def allresult(mode, nomencours, revueencours, epoqueencours, termeencours, nresultencours):

    ListEpoques = epoqueencours.split(",")

    ListRevues,ListEpoquesDecompos = PrepaAmontEpoqueRevue(revueencours, epoqueencours)


    ListEpoquesDecompos = []
    for elt in ListEpoques:
        dateinf = int(elt.split("-")[0])
        datesup = int(elt.split("-")[1])
        ListEpoquesDecompos.append((dateinf, datesup))

    df = pd.DataFrame(columns=ListEpoques)
    for i in range(len(ListRevues)):
        df.loc[i] = ["" for n in range(len(ListEpoques))]
    df.index = ListRevues

    for EpoqueDecompos in ListEpoquesDecompos:
        for Revue in ListRevues:

            fileencours = settings.RESULT_SEMANTIC_DIR + "/TableauEmb/" + mode + "/modele/" + nomencours + "/" + str(EpoqueDecompos[0]) + str(EpoqueDecompos[1]) + Revue + ".txt"
            if os.path.isfile(fileencours):

                if mode == "fasttext" or mode == "word2vec":
                    model = KeyedVectors.load_word2vec_format(fileencours)

                elif mode == "glove":
                    tmp_file = get_tmpfile(str(EpoqueDecompos[0]) + str(EpoqueDecompos[1]) + Revue + "_word2vec.txt")
                    glove2word2vec(fileencours, tmp_file)
                    model = KeyedVectors.load_word2vec_format(tmp_file)

                try:
                    result = model.most_similar(termeencours, topn = int(nresultencours))
                    ResultTerme = [i[0] for i in result]
                    ResultChiffre = [i[1] for i in result]

                    TxtInDataFrame = ""

                    for i, terme in enumerate(ResultTerme):
                        TxtInDataFrame = TxtInDataFrame + terme + " (" + str(round(float(ResultChiffre[i]),2)) + ")" + "\n"

                except:
                    TxtInDataFrame = ""

                EpoqueRecompose = str(EpoqueDecompos[0]) + "-" + str(EpoqueDecompos[1])

                df.ix[Revue, EpoqueRecompose] = TxtInDataFrame


    return df

