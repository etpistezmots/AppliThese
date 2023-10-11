from AllApps.Traitement.Semantique.TableauEmb.models import Expe
from AllApps.Traitement.Semantique.ReseauExplore.core.Result import allresult, restrict_model
import igraph as ig
#from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.cluster import hierarchy
from sklearn.cluster import KMeans, AgglomerativeClustering
import numpy as np




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


def DoDendro1(methode1, color_singleton, model, ResultTerme, group):


    if methode1 == "saut moyen":
        Z = hierarchy.linkage(model.vectors, method="average", metric="cosine")
    elif methode1 == "saut minimal":
        Z = hierarchy.linkage(model.vectors, method="single", metric="cosine")
    else:
        Z = hierarchy.linkage(model.vectors, method="complete", metric="cosine")

    link_cols = {}
    for i, i12 in enumerate(Z[:, :2].astype(int)):
        c1, c2 = (link_cols[x] if x > len(Z) else attribcolor(x, ResultTerme, group) for x in i12)
        if color_singleton :
            link_cols[i + 1 + len(Z)] = c1
        else:
            link_cols[i + 1 + len(Z)] = c1   if c1 == c2 else "#808080"

    return Z ,link_cols




def clustering(nresult, methode_clustering, ncluster, link, ResultTerme, model, color_singleton):
    # initialise le graph (igraph --> detection communauté)
    g = ig.Graph()
    g.add_vertices(len(ResultTerme))
    g.vs["label"] = ResultTerme
    # pour vis.js (rendu graphique)
    nodes_list = []
    edges_list = []
    error = False

    word_vectors = model.wv.vectors
    # # applique k-means
    if methode_clustering == "Kmeans":
        kmeans = KMeans(n_clusters=ncluster)
        idx = kmeans.fit_predict(word_vectors)
    # applique agglo
    elif methode_clustering == "saut moyen" or methode_clustering == "saut minimal" or methode_clustering == "saut maximal":
        if methode_clustering == "saut moyen":
            agglo = AgglomerativeClustering(n_clusters=ncluster, affinity="cosine", linkage='average')
        elif methode_clustering == "saut minimal":
            agglo = AgglomerativeClustering(n_clusters=ncluster, affinity="cosine", linkage='single')
        else:
            agglo = AgglomerativeClustering(n_clusters=ncluster, affinity="cosine", linkage='complete')
        idx = agglo.fit_predict(word_vectors)
    else:
        error = True

    if not error:
        # production résultat sous forme liste de mots
        group = {}
        for i, elt in enumerate(idx):
            if elt in group.keys():
                group[elt].append(ResultTerme[i])
            else:
                group[elt] = []
                group[elt].append(ResultTerme[i])
        print(group)

        # production nodes pour forme graph
        for i, elt in enumerate(ResultTerme):
            for key in group:
                if elt in group[key]:
                    diconode = {'id': i + 1, 'label': "<b>" + elt + "</b>", 'group': key + 1}
                    nodes_list.append(diconode)
        # permet de créer des liens fictifs pour une meilleure lisibilité des groupes
        if link:
            for key in group:
                if len(group[key]) > 1:
                    for i, elt in enumerate(group[key]):
                        if i == 0:
                            eltstart = elt
                            eltavant = elt
                        else:
                            dicoedge = {'from': ResultTerme.index(eltavant) + 1, 'to': ResultTerme.index(elt) + 1,
                                        'dashes': 'true'}
                            edges_list.append(dicoedge)
                            eltavant = elt

        if methode_clustering != "Kmeans":
        ########  Pour dessiner les dendrogramme si Agglo comme choix ######

            Z, link_cols = DoDendro1(methode_clustering, color_singleton, model, ResultTerme, group)
            # manip pour régler taille police d'affichage
            if nresult < 20:
                hierarchy.dendrogram(Z, labels=np.array(ResultTerme), leaf_rotation=0, leaf_font_size=7,
                                     orientation="right", link_color_func=lambda x: link_cols[x])
            elif nresult >= 20 and nresult < 50:
                hierarchy.dendrogram(Z, labels=np.array(ResultTerme), leaf_rotation=0, leaf_font_size=6,
                                     orientation="right", link_color_func=lambda x: link_cols[x])
            else:
                hierarchy.dendrogram(Z, labels=np.array(ResultTerme), leaf_rotation=0, leaf_font_size=5,
                                     orientation="right", link_color_func=lambda x: link_cols[x])

    return nodes_list,edges_list
