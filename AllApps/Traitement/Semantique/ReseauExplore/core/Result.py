import pandas as pd
import numpy as np
from django.conf import settings
from gensim.test.utils import  get_tmpfile
from gensim.models import KeyedVectors
from gensim.scripts.glove2word2vec import glove2word2vec
import os, pickle



def restrict_model(w2v, restricted_word_set):
    '''
    reduit le modèle en fonction d'un groupe de mot
    '''
    transi_vectors = []
    transi_index2entity = []
    transi_vectors_norm = []
    new_vectors = []
    new_vocab = {}
    new_index2entity = []
    new_vectors_norm = []

    for i in range(len(w2v.vocab)):
        word = w2v.index2entity[i]
        if word in restricted_word_set:
            transi_index2entity.append(word)
            vec = w2v.vectors[i]
            transi_vectors.append(vec)
            vec_norm = w2v.vectors_norm[i]
            transi_vectors_norm.append(vec_norm)

    # remet dans l'ordre de restricted_word_set
    # (permet de respecter ordreResultChiffre)
    for elt in restricted_word_set:
        vocab = w2v.vocab[elt]
        new_vocab[elt] = vocab
        vocab.index = len(new_index2entity)
        new_index2entity.append(elt)
        indextransi = transi_index2entity.index(elt)
        new_vectors.append(transi_vectors[indextransi])
        new_vectors_norm.append(transi_vectors_norm[indextransi])

    w2v.vocab = new_vocab
    w2v.vectors = np.array(new_vectors)
    w2v.index2entity = np.array(new_index2entity)
    w2v.index2word = np.array(new_index2entity)
    w2v.vectors_norm = np.array(new_vectors_norm)



def allresult(mode, nomencours, revueencours, epoqueencours, termeencours, nresultencours, retourmodele=False, retourmodelered=False, retourchiffre=False):

    error = False
    model = None
    ResultTerme = []
    ResultChiffre = []
    fileencours = settings.RESULT_SEMANTIC_DIR + "/TableauEmb/" + mode + "/modele/" + nomencours + "/" + \
                  epoqueencours.split("-")[0] + epoqueencours.split("-")[1] + revueencours + ".txt"

    if os.path.isfile(fileencours):

        if mode == "fasttext" or mode == "word2vec":
            model = KeyedVectors.load_word2vec_format(fileencours)

        elif mode == "glove":

            tmp_file = get_tmpfile(epoqueencours.split("-")[0] + epoqueencours.split("-")[1] + revueencours + "_word2vec.txt")
            glove2word2vec(fileencours, tmp_file)
            model = KeyedVectors.load_word2vec_format(tmp_file)

        try:
            result = model.most_similar(termeencours, topn=int(nresultencours))
            ResultTerme = [i[0] for i in result]
            ResultChiffre = [i[1] for i in result]
        except:
            error = True
    else:
        error = True


    if not retourmodele and not retourmodelered and not retourchiffre:
        return error, ResultTerme
    elif not retourmodele and not retourmodelered and retourchiffre:
        return error, ResultTerme, ResultChiffre
    elif retourmodele and not retourmodelered and not retourchiffre:
        return error, ResultTerme, model
    elif not retourmodele and retourmodelered and not retourchiffre:
        if not error:
            restrict_model(model, ResultTerme)
        return error, ResultTerme, model
    elif retourmodele and not retourmodelered and retourchiffre:
        return error, ResultTerme, ResultChiffre, model
    elif not retourmodele and retourmodelered and retourchiffre:
        if not error:
            restrict_model(model, ResultTerme)
        return error, ResultTerme, ResultChiffre, model
    else:
        return error
