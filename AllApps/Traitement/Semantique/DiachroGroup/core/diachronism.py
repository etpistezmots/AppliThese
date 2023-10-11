#!/usr/bin/env python
# -*- coding: utf-8 -*-

# fait par Max Beligné

from math import sqrt


class diachronism:
    def __init__(self, periode1, periode2, SelectLink):

        # résultats de la fonction GetLabelAndScore
        self.Data1 = {}
        self.Data2 = {}

        # résultats de la fonction ComputeIndicateur
        self.Intesec1 = []
        self.Intesec2 =[]

        # résultats de la fonction  ComputeLocalAverage
        self.PA_1 = []
        self.PA_2 = []

        # résultats de la fonction  ComputeGlobalAverage
        self.A_1 = 0
        self.A_2 = 0

        # résultats de la fonction  ComputeStandardDeviation
        self.D_1 = 0
        self.D_2 = 0

        self.ListMatch = []

        ################# OBTENTION DES DONNEES ###################

        self.GetLabelAndScore(periode1, "1")
        self.GetLabelAndScore(periode2, "2")

        ############ MATCHING (Cf http://lodel.irevues.inist.fr/isj/?id=390) ##########

        # Compute indicateur  --> correspond à Equation 13 dans article ci-dessus

        print("INDICATEUR1")
        self.ComputeIndicateur(self.Data1, self.Data2, "1")
        print("INDICATEUR2")
        self.ComputeIndicateur(self.Data2, self.Data1, "2")

        if SelectLink == "Methode DiachoExplorer" or SelectLink == "Methode theorie initiale":

            ################# MOYENNE LOCALE ######################################
            # Correspond à PA(S) et PA(T) --> Equation 14  dans article ci-dessus

            print("MOYENNE LOCALE 1")
            self.ComputeLocalAverage(self.Data1, self.Data2, self.Intesec1, self.Intesec2, SelectLink, "1")
            print("MOYENNE LOCALE 2")
            self.ComputeLocalAverage(self.Data2, self.Data1, self.Intesec2, self.Intesec1, SelectLink, "2")

            ################# MOYENNE LOCALE ######################################
            # Correspond à Global Average A(S) et A(T) --> Equation 15

            print("MOYENNE GLOBALE 1")
            self.ComputeGlobalAverage(self.PA_1, "1")
            print("MOYENNE GLOBALE 2")
            self.ComputeGlobalAverage(self.PA_2, "2")

            # Compute standard Deviation

            print("ECART TYPE 1")
            self.ComputeStandardDeviation(self.PA_1, self.A_1, "1")
            print("ECART TYPE 2")
            self.ComputeStandardDeviation(self.PA_2, self.A_2, "2")

            # Match cluster
            # variable : self.ListMatch
            self.MatchCluster(self.Data1, self.Data2, self.Intesec1, self.Intesec2, self.PA_1,
                              self.PA_2, self.A_1, self.A_2, self.D_1, self.D_2)

        else:
            self.SelectAllDifferent0(self.Data1, self.Data2, self.Intesec1, self.Intesec2)

    ###############  FONCTIONS ###################

    def GetLabelAndScore(self, pathdata, indic):

        '''
        En sortie, renvoie un dico de dico sous la forme suivante
        {"P1" : {"label1" : score1, "label2" : score2,...}, "nom ensemble 2" :....  }
        '''

        NomPartie = ""
        if indic == "1":
            DicoDataRef = self.Data1
        else:
            DicoDataRef = self.Data2

        # lit le fichier où sont stocké les données
        with open(pathdata) as f:
            content = f.readlines()

        for line in content:
            # Si c'est la marque d'un nouvel ensemble
            # Ex "G0-0	25	19" avec des tabulations comme séparateur
            if line[0] == "G":
                # recup son nom"
                EnsInfo = line.split("\t")
                NomPartie = EnsInfo[0][1:].split("-")[0] + "_" + indic

                # Crée une nouvel entrée dans le dico
                DicoDataRef[NomPartie] = {}

            # Ex "	industrie	5488" mais aussi espace entre les ensembles (d'où le "and line[0:1]!="\n")
            if line[0] != "G" and line[0:1] != "\n":
                mot, score = line.split("\t")[1], line.split("\t")[2][:-1]

                # si correspond à un nouveau mot, insertion dans le dico avec le score correspondant
                if mot != "":
                    DicoDataRef[NomPartie][mot] = float(score)


    def ComputeIndicateur(self, Ens1, Ens2, indic):
        '''
        En sortie, liste de dico {"cluster1", "cluster2", "intersection cluster1 et cluster2 / tous les elts de cluster1")
        Seuls les elts où il y a eu une intersection entre deux clusters sont marqués
        Pour les autres, la proba est égal à O car il n'y a rien au numérateur
        '''

        ListeCalculIndic = []
        for cluster1 in Ens1:
            for cluster2 in Ens2:

                print(cluster1, cluster2)

                # recherche étiquette intersection cluster1 - cluster2
                Eltcluster1 = Ens1[cluster1].keys()
                Eltcluster2 = Ens2[cluster2].keys()
                intersection = Eltcluster1 & Eltcluster2
                print(intersection)

                if len(intersection) > 0:

                    # Calcul du numerateur = somme score des étiquettes instersection
                    numerateur = 0
                    for eltI in intersection:
                        numerateur += Ens1[cluster1][eltI]
                    print(numerateur)

                    # Calcul de dénominateur = somme score étiquette

                    denominateur = 0
                    for eltLabel1 in Ens1[cluster1]:
                        denominateur += Ens1[cluster1][eltLabel1]
                    print(denominateur)

                    # Calul de l'intesection
                    if denominateur != 0:
                        intersection = numerateur / denominateur
                    else:
                        intersection = 0

                    ListeCalculIndic.append({"cluster1": cluster1, "cluster2": cluster2, "intersection": intersection})

        if indic == "1":
            self.Intesec1 = ListeCalculIndic.copy()
        else:
            self.Intesec2 = ListeCalculIndic.copy()

        print(ListeCalculIndic)

    def ComputeLocalAverage(self, Ens1, Ens2, IntersecEns1, IntersecEns2, SelectLink, indic):

        '''Variable testenv car question sur quoi on divise
        que les clusters actifs : implémentation actuelle de Nicolas. Variable : JusteActif
        Quand beaucoup de clusters comme dans le jeu Test Nicolas Préférable

        Quand peu de clusters comme dans mon jeu de test perso
        Peut se justifier : voir cas suivant

        - Le cluster 0 en période 1 active seulement le cluster 5 en période 2 à hauteur de 0.31
        - Lecluster 5 en période 2 active réciproquement le cluster 0 en période 1 à hauteur de 0.43
        mais aussi un tout petit peu (pour un seul mot) le cluster 3 en période 1 à hauteur de 0.04. Du coup, ça fait chuter sa moyenne à 0,235.
        - Comme on prend la moyenne interne, ce tout petit mot à un impact énorme'''

        MoyLocales = []

        for cluster1 in Ens1:
            print(cluster1)

            if SelectLink == "Methode DiachoExplorer":
                Liste = [result for result in IntersecEns2 if result["cluster2"] == cluster1]
            else:
                Liste = [result for result in IntersecEns1 if result["cluster1"] == cluster1]

            SommeEns = sum([result["intersection"] for result in Liste])

            Env = len(Liste)
            if Env != 0:
                MoyActivite1 = SommeEns / Env
            else:
                MoyActivite1 = 0
            print(MoyActivite1)
            print("\n")

            MoyLocales.append({"cluster": cluster1, "Moylocale": MoyActivite1})

        if indic == "1":
            self.PA_1 = MoyLocales.copy()
        else:
            self.PA_2 = MoyLocales.copy()

        print(MoyLocales)


    def ComputeGlobalAverage(self, EnsMoyLocales, indic):

        Activ = sum([elt["Moylocale"] for elt in EnsMoyLocales])
        NbreEns = len(EnsMoyLocales)
        CalculMoy = Activ / NbreEns
        if indic=="1":
            self.A_1 = CalculMoy
        else:
            self.A_2 = CalculMoy

        print(CalculMoy)

    def ComputeStandardDeviation(self, EnsMoyLocales, MoyMoy, indic):

        VarianceElt = [((elt["Moylocale"] - MoyMoy) ** 2) for elt in EnsMoyLocales]
        Variance = sum(VarianceElt) / len(VarianceElt)
        D = sqrt(Variance)
        if indic=="1":
            self.D_1 = D
        else:
            self.D_2 = D

        print(D)


    def MatchCluster(self, Ens1, Ens2, Intesec1, Intesec2, PA1, PA2, A1, A2, D1, D2):

        # itération sur toutes les combinaisons
        for cluster1 in Ens1:
            for cluster2 in Ens2:

                # recupère les indicateur calulées
                Indic1Local = [elt["intersection"] for elt in Intesec1 if
                                      (elt["cluster2"] == cluster2 and elt["cluster1"] == cluster1)]
                Indic2Local = [elt["intersection"] for elt in Intesec2 if
                                      (elt["cluster2"] == cluster1 and elt["cluster1"] == cluster2)]

                # Gère le cas où il n'y a pas d'intersection (=0)
                if len(Indic1Local) != 0:
                    Indic1Local = Indic1Local[0]
                else:
                    Indic1Local = 0

                if len(Indic2Local) != 0:
                    Indic2Local = Indic2Local[0]
                else:
                    Indic2Local = 0

                # récupere le PA1 et Pa2
                SpecificPA1 = [elt["Moylocale"] for elt in PA1 if elt["cluster"] == cluster1][0]
                SpecificPA2 = [elt["Moylocale"] for elt in PA2 if elt["cluster"] == cluster2][0]

                if Indic1Local != 0 or Indic2Local != 0:
                    # ensemble de print pour vérification
                    print("Clu1 : " + cluster1)
                    print("Clu2 : " + cluster2)
                    print("Intersec1 : " + str(Indic1Local))
                    print("Intersec1 2 : " + str(Indic2Local))
                    print("PA_1 : " + str(SpecificPA1))
                    print("PA_2 : " + str(SpecificPA2))
                    print("A_1 + D_1 : " + str(A1 + D1))
                    print("A_2 + D_2 : " + str(A2 + D2))
                    print("\n")

                # Def du matching : voir http://lodel.irevues.inist.fr/isj/?id=390
                # après l'aquation 15
                if Indic1Local >= SpecificPA1 and (Indic1Local >= A1 + D1) and Indic2Local >= SpecificPA2 and\
                        (Indic2Local >= A2 + D2):
                    self.ListMatch.append((cluster1, cluster2))


    def SelectAllDifferent0(self, Ens1, Ens2, Intesec1, Intesec2):

        # itération sur toutes les combinaisons
        for cluster1 in Ens1:
            for cluster2 in Ens2:
                # recupère les indicateur calulées
                Indic1Local = [elt["intersection"] for elt in Intesec1 if
                               (elt["cluster2"] == cluster2 and elt["cluster1"] == cluster1)]
                Indic2Local = [elt["intersection"] for elt in Intesec2 if
                               (elt["cluster2"] == cluster1 and elt["cluster1"] == cluster2)]

                # Gère le cas où il n'y a pas d'intersection (=0)
                if len(Indic1Local) != 0:
                    Indic1Local = Indic1Local[0]
                else:
                    Indic1Local = 0

                if len(Indic2Local) != 0:
                    Indic2Local = Indic2Local[0]
                else:
                    Indic2Local = 0

                if Indic1Local != 0 or Indic2Local != 0:
                    self.ListMatch.append((cluster1, cluster2))