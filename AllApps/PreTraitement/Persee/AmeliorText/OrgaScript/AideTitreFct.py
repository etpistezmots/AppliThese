from difflib import SequenceMatcher
from AllApps.PreTraitement.Persee.DelimitCorpus.outils.xpath import  DocMot
import os
from django.conf import settings
from AllApps.PreTraitement.Persee.DelimitCorpus.core import GetAdresseCompletDoc



def str_compare(text, pattern):
    """ Fonction qui mesure la similarité entre deux chaine de caractères.
        À quel point "pattern" ressemble à "text" ?

    Args:
        text (str)      : chaine avec laquelle on mesure la ressemblance.
        pattern (str)   : motif à reconnaitre.

    Return:
        (int): pourcentage de similarité entre le pattern et le text (donc compris entre 0 et 1).
    """
    return SequenceMatcher(None, text, pattern).ratio()


def TitreFRengPart(langue, titre):
    if titre and langue == "French":
        return titre.split("/")[0]
    else:
        return titre

def TitreFrenchEscApostrophe(titreencours):
    return titreencours.replace("'","''")


def GetTitreTrouvesDansTexte(titre, listmot, SEUIL_1, npremiers_mots_texte):
    """ Fonction qui recherche un titre dans une liste de mots.
        La méthode renvoie le titre qui a été trouvé ainsi que le texte qui précède (s'il existe)

    Args:
        titre (str)             : pattern à rechercher.
        listmot (list of str)   : liste de mots dans laquelle rechercher le titre
        seuil (float)           : seuil de détection pour la ressemblance en n-gram variable

    Return:
        (dict): {
                ratio_similarité (str),
                titre (str),
                résultat recherche du titre (str),
                chaine de caractères précédent le titre,
                indice du début,
                indice de fin
                }

    """
    # On exlus cas doc sans mot (cf doc protégé)
    # Normalement a du être enlevé lors réduction de corpus
    # mais sinon va renvoyer message erreur !!!

    if len(listmot) != 0:
        out_detect_1 = \
            AlgoSimpleDetectionTitre(listmot, titre, npremiers_mots_texte)

        # On considère que c'est bon si supérieur au seuil_1!
        if out_detect_1['matching_score'] >= SEUIL_1:
            return {
                    "matching_score": out_detect_1['matching_score'],
                    "matching_score_str": "{:.2f}".format(out_detect_1['matching_score']),
                    "titre": titre,
                    "titre_texte_corrige": out_detect_1['titre_texte_corrige'],
                    "texte_precede_titre": " ".join(listmot[0:out_detect_1['IndexDebut']]),
                    "IndexDebut": out_detect_1['IndexDebut'],
                    "IndexFin": out_detect_1['IndexFin']
                    }
            #(str(ressemblance_precedent_1), titre, result_textmining_1, " ".join(listmot[0:l_result_debut]), l_result_debut, l_result_fin)

        # Sinon,  va faire une nouvelle rechecrche un peu plus complexe
        else:

            out_detect_2 = \
                AlgoPlusComplexeDetectionTitre(listmot, titre,  npremiers_mots_texte)

            return {
                    "matching_score": out_detect_2['matching_score'],
                    "matching_score_str": "{:.2f}".format(out_detect_2['matching_score']),
                    "titre": titre,
                    "titre_texte_corrige": out_detect_2['titre_texte_corrige'],
                    "texte_precede_titre": " ".join(listmot[0:out_detect_2['IndexDebut']]),
                    "IndexDebut": out_detect_2['IndexDebut'],
                    "IndexFin": out_detect_2['IndexFin']
                    }
                    #(str(ressemblance_precedent_2), titre, result_textmining_2, " ".join(listmot[0:l_result_debut]), l_result_debut, l_result_fin )


def AlgoSimpleDetectionTitre(listmot, titre, npremiers_mots_texte):
    """ Fonction permettant de détecter un titre présent dans les npremiers_mots_texte de listmot à partir d'un titre présent dans les métadonnées. La fonction recherche à partir d'une fenêtre glissante.
    Args:
        listmot (list of (str))     : liste des mots présents dans le corps du texte.
        titre (str)                 : titre présent dans les métadonnées.
        npremiers_mots_texte (int)  : nombre de mots.

    Return:
        (dict): {
                ratio_similarité (int),
                résultat recherche du titre (str),
                indice du début (int),
                indice de fin (int)
                }
    """

    l_result_debut = 0
    l_result_fin = 0
    ressemblance_precedent_1 = 0
    result_textmining_1 = ""

    N = len(titre.split(" "))

    # Recherche sur fenêtre glissante
    for l in range(npremiers_mots_texte):
        gram = listmot[l:l + N]
        ressemblance = str_compare(' '.join(gram).lower(), titre.lower())
        if ressemblance > ressemblance_precedent_1:
            ressemblance_precedent_1 = ressemblance
            l_result_debut = l
            l_result_fin = l + N - 1
            result_textmining_1 = ' '.join(gram)

    return {
            "matching_score": ressemblance_precedent_1,
            "titre_texte_corrige": result_textmining_1,
            "IndexDebut": l_result_debut,
            "IndexFin": l_result_fin
            }


def AlgoPlusComplexeDetectionTitre(listmot, titre, npremiers_mots_texte):
    """ Fonction permettant de détecter un titre présent dans les npremiers_mots_texte de listmot à partir d'un titre présent dans les métadonnées. La fonction recherche à partir d'une fenêtre glissante à taille variable.
    Args:
        listmot (list of (str))     : liste des mots présents dans le corps du texte.
        titre (str)                 : titre présent dans les métadonnées.
        npremiers_mots_texte (int)  : nombre de mots.

    Return:
        (dict): {
                ratio_similarité (int),
                résultat recherche du titre (str),
                indice du début (int),
                indice de fin (int)
                }
    """
    l_result_debut = 0
    l_result_fin = 0
    ressemblance_precedent_2 = 0
    result_textmining_2 = ""
    N = len(titre.split(" "))

    # Recherche sur fenêtre glissante à taille variable
    # taille n-gram = f(nombre mots titre)
    if N < 10:
        M = 3
    elif (N >= 10 and N < 16):
        M = 5
    else:
        M = 7

    for delta in range(N - M, N + M):
        for l in range(npremiers_mots_texte):
            gram = listmot[l:l + delta]
            ressemblance = str_compare(' '.join(gram).lower(), titre.lower())
            if ressemblance > ressemblance_precedent_2:
                ressemblance_precedent_2 = ressemblance
                l_result_debut = l
                l_result_fin = l + delta -1
                result_textmining_2 = ' '.join(gram)

    return{
            "matching_score": ressemblance_precedent_2,
            "titre_texte_corrige": result_textmining_2,
            "IndexDebut": l_result_debut,
            "IndexFin": l_result_fin
            }


def SearchSubSequence(forward, source, target, start=0, end=None):
    """Naive search for target in source."""
    m = len(source)
    n = len(target)

    if end is None:
        end = m
    else:
        end = min(end, m)

    if n == 0 or (end-start) < n:
        # target is empty, or longer than source, so obviously can't be found.
        return None

    if forward:
        x = range(start, end-n+1)
    else:
        x = range(end-n, start-1, -1)

    for i in x:
        if source[i:i+n] == target:
            return i
    return None


def OnPositionSequence(NomDuFichier, sequence, type):
    """ OnPositionSequence permet de retrouver l'index d'une séquence recherchée

    Args:
        NomDuFichierSequence (str)"

    """

    addressedocencours = GetAdresseCompletDoc(NomDuFichier)

    if type == "brut":
        ListeRef = DocMot(addressedocencours)

    if type == "xml":
        ListeRef = DocMot(addressedocencours,detail=True)

    # Recherche dans le sens de la lecture:
    IndexD = SearchSubSequence(True,ListeRef,sequence)

    # Recherche dans le inverse:
    IndexF = SearchSubSequence(False, ListeRef, sequence)

    # Different cas :
    if IndexD is None :
        return "la sequence cherchée n'existe pas"

    if IndexD is not None and IndexD==IndexF:
        return "la sequence cherchée est unique à l'index : " + str(IndexD) + " - " + str(IndexD + len(sequence))

    if IndexD is not None and IndexD != IndexF:
        return "il existe au moins deux index de cette séquence : " + str(IndexD) + " - " + str(IndexD + len(sequence)) + " et " + str(IndexF - len(sequence)) + " - " + str(IndexF)


