import csv, os, sys
from gensim.models import FastText, Word2Vec
from sklearn.feature_extraction.text import CountVectorizer
from collections import Counter
import subprocess, pickle
from django.conf import settings
from shutil import copyfile
import gzip
from ..periph.amont import PrepaAmontEpoqueRevue, MyIter, prepaglove




def allmodele(mode, nom, corpus, revues, epoques,
              architecture="cbow", embedding_size=50, context_size=10, min_occurrences=15, num_epochs=150,
              min_n=3, max_n=6,
              locate="TableauEmb"):
    f_model_gen = settings.RESULT_SEMANTIC_DIR + "/" + locate + "/" + mode + "/modele"
    f_model_actual = f_model_gen + "/" + nom

    if not os.path.exists(f_model_actual):
        os.makedirs(f_model_actual)

    ListRevues,ListEpoquesDecompos = PrepaAmontEpoqueRevue(revues, epoques)

    for EpoqueDecompos in ListEpoquesDecompos:
        for Revue in ListRevues:


            if mode == "fasttext" or mode == "word2vec":
                if mode == "fasttext":
                    if architecture == "cbow":
                        model = FastText(sg=0, size=embedding_size, window=context_size, min_count=min_occurrences,
                                         min_n=min_n, max_n=max_n)
                    elif architecture == "skipgram":
                        model = FastText(sg=1, size=embedding_size, window=context_size, min_count=min_occurrences
                                         , min_n=min_n, max_n=max_n)
                elif mode == "word2vec":
                    if architecture == "cbow":
                        model = Word2Vec(sg=0, size=embedding_size, window=context_size, min_count=min_occurrences)
                    elif architecture == "skipgram":
                        model = Word2Vec(sg=1, size=embedding_size, window=context_size, min_count=min_occurrences)
                sentences = MyIter(corpus, EpoqueDecompos[0], EpoqueDecompos[1], Revue)
                model.build_vocab(sentences)
                total_examples = model.corpus_count

                if total_examples != 0:
                    sentences = MyIter(corpus, EpoqueDecompos[0], EpoqueDecompos[1], Revue)
                    model.train(sentences, total_examples=total_examples, epochs=num_epochs)
                    fname = f_model_actual + "/" + str(EpoqueDecompos[0]) + str(EpoqueDecompos[1]) + Revue + ".txt"
                    model.wv.save_word2vec_format(fname, binary=False)


            elif mode == "glove":

                prepaglove(corpus, EpoqueDecompos[0], EpoqueDecompos[1], Revue)


                if os.stat(settings.GLOVE_DIR + "/textok.txt").st_size != 0:
                    txt = """#!/bin/sh
                    set -e

                    CORPUS=""" + settings.GLOVE_DIR + """/textok.txt
                    VOCAB_FILE=""" + settings.GLOVE_DIR + """/vocab.txt
                    COOCCURRENCE_FILE=""" + settings.GLOVE_DIR + """/cooccurrence.bin
                    COOCCURRENCE_SHUF_FILE=""" + settings.GLOVE_DIR + """/cooccurrence.shuf.bin
                    BUILDDIR=""" + settings.GLOVE_DIR + """/build
                    SAVE_FILE=""" + settings.GLOVE_DIR + """/vectors
                    VERBOSE=2
                    MEMORY=4.0
                    VOCAB_MIN_COUNT=""" + str(min_occurrences) + """
                    VECTOR_SIZE=""" + str(embedding_size) + """
                    MAX_ITER=""" + str(num_epochs) + """
                    WINDOW_SIZE=""" + str(context_size) + """
                    BINARY=2
                    NUM_THREADS=8
                    X_MAX=10

                    echo
                    echo "$ $BUILDDIR/vocab_count -min-count $VOCAB_MIN_COUNT -verbose $VERBOSE < $CORPUS > $VOCAB_FILE"
                    $BUILDDIR/vocab_count -min-count $VOCAB_MIN_COUNT -verbose $VERBOSE < $CORPUS > $VOCAB_FILE
                    echo "$ $BUILDDIR/cooccur -memory $MEMORY -vocab-file $VOCAB_FILE -verbose $VERBOSE -window-size $WINDOW_SIZE < $CORPUS > $COOCCURRENCE_FILE"
                    $BUILDDIR/cooccur -memory $MEMORY -vocab-file $VOCAB_FILE -verbose $VERBOSE -window-size $WINDOW_SIZE < $CORPUS > $COOCCURRENCE_FILE
                    echo "$ $BUILDDIR/shuffle -memory $MEMORY -verbose $VERBOSE < $COOCCURRENCE_FILE > $COOCCURRENCE_SHUF_FILE"
                    $BUILDDIR/shuffle -memory $MEMORY -verbose $VERBOSE < $COOCCURRENCE_FILE > $COOCCURRENCE_SHUF_FILE
                    echo "$ $BUILDDIR/glove -save-file $SAVE_FILE -threads $NUM_THREADS -input-file $COOCCURRENCE_SHUF_FILE -x-max $X_MAX -iter $MAX_ITER -vector-size $VECTOR_SIZE -binary $BINARY -vocab-file $VOCAB_FILE -verbose $VERBOSE"
                    $BUILDDIR/glove -save-file $SAVE_FILE -threads $NUM_THREADS -input-file $COOCCURRENCE_SHUF_FILE -x-max $X_MAX -iter $MAX_ITER -vector-size $VECTOR_SIZE -binary $BINARY -vocab-file $VOCAB_FILE -verbose $VERBOSE
                    """

                    with open(settings.GLOVE_DIR + "/demo.sh", "w") as f:
                        f.write(txt)

                    subprocess.run(settings.GLOVE_DIR + "/demo.sh")

                    fname = f_model_actual + "/" + str(EpoqueDecompos[0]) + str(EpoqueDecompos[1]) + Revue + ".txt"
                    copyfile(settings.GLOVE_DIR + "/vectors.txt", fname)





