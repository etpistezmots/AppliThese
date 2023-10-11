import os
from scipy.cluster import hierarchy
from sklearn.cluster import  AgglomerativeClustering
from AllApps.Traitement.Semantique.ReseauExplore.core.Result import allresult
import numpy as np
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt



def ExtractFromEmbedding(mode, nommodel, revue, epoque, terme, nresult, compteur):
    """
    :return: error = True si terme n'exite pas dans le modèle
            ResultTerme = list des n termes les plus proches du terme suivant calcul similarité cosinus entre vecteur plongement
            chiffre = list correspondant aux mesures similarité cosinus précédemment calculés. Dans l'ordre correspondant à ResultTerm
            model = l'ensemble du modèle
    """
    nresultsplit = nresult.split(',')
    MarqueurDo = False
    # 1892 date création Annales
    if revue == "Annales" and int(epoque.split("-")[1]) >= 1892:
        compteur += 1
        MarqueurDo = True
    # 1892 date création Annales
    if revue == "Espace" and int(epoque.split("-")[1]) >= 1972:
        compteur += 1
        MarqueurDo = True

    error = False
    ResultTerme = []
    ResultChiffre = []
    model= None

    if MarqueurDo:
        # suivant cas un seul nombre de nresult pour tous les revue*epoque ou chaque revue*epoque à un nombre spécifié
        if len(nresultsplit) == 1:
            error, ResultTerme, ResultChiffre, model = allresult(mode, nommodel, revue, epoque, terme, int(nresult),
                                                                 retourmodelered=True, retourchiffre=True)
        else:
            error, ResultTerme, ResultChiffre, model = allresult(mode, nommodel, revue, epoque, terme, int(nresultsplit[compteur]),
                                                                 retourmodelered=True, retourchiffre=True)

    return MarqueurDo, error, ResultTerme, ResultChiffre, model, compteur


def attribcolor(x,listformword,group):
    '''
    gère l'attribution des couleurs en fonction numéro du group
    attention si changement,
    il faut aussi changer dans html result et resultvisu horizontal et vertical
    '''

    mot = listformword[x]
    for k in group:
        if mot in group[k]:
            GroupDuMot = k
    if GroupDuMot == 0:
        color = '#81BEF7'
    elif GroupDuMot == 1:
        color = '#FFFF00'
    elif GroupDuMot == 2:
        color = '#F78181'
    elif GroupDuMot == 3:
        color = '#3ADF00'
    elif GroupDuMot == 4:
        color = '#D358F7'
    elif GroupDuMot == 5:
        color = '#B09603'
    elif GroupDuMot == 6:
        color = '#FAAC58'
    elif GroupDuMot == 7:
        color = '#0040FF'
    elif GroupDuMot == 8:
        color = '#F8ADD6'
    elif GroupDuMot == 9:
        color = '#9EFDCB'
    elif GroupDuMot == 10:
        color = '#DF0101'
    elif GroupDuMot == 11:
        color = '#FE2E9A'
    elif GroupDuMot == 12:
        color = '#0080FF'
    elif GroupDuMot == 13:
        color = '#0B6121'
    elif GroupDuMot == 14:
        color = '#DF01A5'
    elif GroupDuMot == 15:
        color = '#D8CEF6'
    else:
        color = '#000000'
    return color



def DoCluster(model, methode_clustering, ncluster, nclustersplit, compteur, PathDendro, Revue, EpoqueDecompos, ResultTerme):

    word_vectors = model.wv.vectors


    # cas même nombre de cluster pour toute les époque*revue
    if len(nclustersplit) == 1:

        if methode_clustering == "saut moyen":
            agglo = AgglomerativeClustering(n_clusters=int(ncluster), affinity="cosine",
                                            linkage='average')
        else:
            agglo = AgglomerativeClustering(n_clusters=int(ncluster), affinity="cosine",
                                            linkage='complete')
    else:

        if methode_clustering == "saut moyen":
            agglo = AgglomerativeClustering(n_clusters=int(nclustersplit[compteur]), affinity="cosine",
                                            linkage='average')
        else:
            agglo = AgglomerativeClustering(n_clusters=int(nclustersplit[compteur]), affinity="cosine",
                                            linkage='complete')
    idx = agglo.fit_predict(word_vectors)

    group = {}
    for i, elt in enumerate(idx):
        if elt in group.keys():
            group[elt].append(ResultTerme[i])
        else:
            group[elt] = []
            group[elt].append(ResultTerme[i])



    if methode_clustering == "saut moyen":
        Z = hierarchy.linkage(model.vectors, method="average", metric="cosine")
    else:
        Z = hierarchy.linkage(model.vectors, method="complete", metric="cosine")

    link_cols = {}
    for i, i12 in enumerate(Z[:, :2].astype(int)):
        c1, c2 = (link_cols[x] if x > len(Z) else attribcolor(x, ResultTerme, group) for x in i12)
        link_cols[i + 1 + len(Z)] = c1


    hierarchy.dendrogram(Z, labels=np.array(ResultTerme), leaf_rotation=0, leaf_font_size=6,
                             orientation="right", link_color_func=lambda x: link_cols[x])

    Epoque1 = EpoqueDecompos.split("-")[0]
    Epoque2 = EpoqueDecompos.split("-")[1]
    plt.savefig(PathDendro + Epoque1 + Epoque2 + Revue + ".png")
    plt.close()


    return idx


def DoStopWord(stop_mots,ResultTerme,ResultChiffre,idx):
    excludeterme = []
    IndexAExclure = []
    ResultTermeNew = []
    ResultChiffreNew = []
    IdxNew = []

    for elt in stop_mots.split("*"):
        excludeterme.append(elt)

    if excludeterme != ['']:
        for i, elt in enumerate(ResultTerme):
            if elt not in excludeterme:
                ResultTermeNew.append(elt)
                # par default les chiffres ici du modèle ...
                # change avec possibilité calculs poids par la suite
                ResultChiffreNew.append(ResultChiffre[ResultTerme.index(elt)])
            else:
                IndexAExclure.append(i)

        for i, elt in enumerate(idx):
            if i not in IndexAExclure:
                IdxNew.append(elt)

    else:
        IdxNew = idx.copy()
        ResultTermeNew= ResultTerme.copy()
        ResultChiffreNew= ResultChiffre.copy()


    return ResultTermeNew,ResultChiffreNew,IdxNew



def DoPartition(idx):
    group = {}
    for i, elt in enumerate(idx):
        if elt in group.keys():
            group[elt].append(i)
        else:
            group[elt] = []
            group[elt].append(i)

    partition = []
    for k, v in group.items():
        partition.append(v)
    return partition



#######################  POIDS ########################


def ComputeSommeGroupe(ResultTermeNew,PartitionNew,model):
    ResultChiffreNewTemp = []
    for z, elt in enumerate(ResultTermeNew):
        # itère sur les groupes
        for elt_group in PartitionNew:
            # si elt dans le groupe
            if z in elt_group:
                # va calculer la somme des poids
                # el la stocke dans variable ResultChiffreNewTemp
                somme_poids = 0
                for elt_indiv in elt_group:
                    if elt_indiv != z:
                        poids = model.similarity(elt, ResultTermeNew[elt_indiv])
                        somme_poids = somme_poids + poids
                ResultChiffreNewTemp.append(somme_poids)
    return ResultChiffreNewTemp

def PartitionOrder(ResultTerme,ResultChiffre,Partition):
    PartitionTermes= []
    PartitionChiffres = []
    # pour chaque groupe, va creer une liste avec chiffre trouvés précédement
    # et une liste des termes
    print("TEST Partition")
    print(Partition)
    for elt_group in Partition:
        ResultChiffreByGroupTemp = []
        ResultTermByGroupTemp = []
        for elt_indiv in elt_group:
            ResultChiffreByGroupTemp.append(ResultChiffre[elt_indiv])
            ResultTermByGroupTemp.append(ResultTerme[elt_indiv])
        # tri à l'intérieur du groupe
        # pour mettre les éléments importants en premier !
        ids = np.array(ResultChiffreByGroupTemp).argsort()[::-1]
        # Nouvelles listes avec cet ordre
        ResultChiffreNewSort = []
        ResultTermeNewSort = []
        for eltencore in ids:
            ResultChiffreNewSort.append(ResultChiffreByGroupTemp[eltencore])
            ResultTermeNewSort.append(ResultTermByGroupTemp[eltencore])
        PartitionTermes.append(ResultTermeNewSort)
        PartitionChiffres.append(ResultChiffreNewSort)
    print(PartitionTermes)
    return PartitionTermes,PartitionChiffres



def DoCalculPoids(calculPoidsLabel,ResultTerme,ResultChiffre,partition, model):
    # 1ere POSSIBILITE CALCUL POIDS
    if calculPoidsLabel == "Simi cos par rapport terme initial":
        PartitionTermes, PartitionChiffres = PartitionOrder(ResultTerme, ResultChiffre, partition)

    # 2ème POSSIBILITE POIDS = 1 !
    elif calculPoidsLabel == "1 pour tous les termes":
        PartitionTermes, PartitionChiffres = PartitionOrder(ResultTerme, ResultChiffre, partition)
        #  ResultChiffre initialisé à 1 !
        PartitionChiffresNew = []
        for elt in PartitionChiffres:
            PartitionChiffresNew.append([1] * len(elt))
        PartitionChiffres = PartitionChiffresNew.copy()

    # 3ème POSSIBILITE  POIDS = 1 + effort label  !
    # CalculPoids == "1 pour tous les termes" and selectLabel == "Max somme simi cos intra cluster":
    else:
        ResultChiffreNewTemp = ComputeSommeGroupe(ResultTerme, partition, model)
        PartitionTermes, PartitionChiffres = PartitionOrder(ResultTerme, ResultChiffreNewTemp,
                                                            partition)
        #  ResultChiffre initialisé à 1 !
        PartitionChiffresNew = []
        for elt in PartitionChiffres:
            PartitionChiffresNew.append([1] * len(elt))
        PartitionChiffres = PartitionChiffresNew.copy()

    return PartitionTermes,PartitionChiffres


def CreateFichiersPoidsOri(Path, Revue,EpoqueDecompos,PartitionTermes, PartitionChiffres):

    PathSauvPoidsOri = Path + "/3)Matching/DataDiaNMots"
    if not os.path.exists(PathSauvPoidsOri):
        os.makedirs(PathSauvPoidsOri)

    # va écrire les différents fichiers au fur et à mesure passe dans la boucle
    file = open(PathSauvPoidsOri + "/" + str(EpoqueDecompos.split("-")[0]) + str(EpoqueDecompos.split("-")[1]) + Revue + ".fmgs", 'w')
    for i, eltpartition in enumerate(PartitionTermes):
        file.write("G" + str(i) + "-0" + "\t" + str(len(eltpartition)) + "\t" + str(len(eltpartition)) + "\n")
        for j,elt in enumerate(eltpartition):
            file.write("\t" + elt + "\t" + str(round(PartitionChiffres[i][j], 3)) + "\n")
        file.write("\n")
    file.close()






