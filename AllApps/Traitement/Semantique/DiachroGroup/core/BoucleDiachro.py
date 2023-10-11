from .diachronism import diachronism
from collections import OrderedDict
import pandas as pd
import os


class BoucleDiachro:
    def __init__(self, Path, Revues, Epoques, CompareJustNewRevue, SelectLink):

        ######################## PREPA BOUCLE ######################

        '''
        En entrée : New : booléen qui permet de faire traitement que si True
                          évite de faire à chaque fois les traitements pour les tests

        Génère en sortie : attribut de l'objet créé:
            .ListSort : la liste triée déjà par date puis par revue
            .Marqueur2Revues : booleen si 2 revues ou pas en entrée
            .AnnOnly : combien de période seul des Annales

        '''

        self.ListRevues = Revues.split(",")
        self.ListEpoques = Epoques.split(",")
        self.PathDataDiaNMots = Path + "/3)Matching/DataDiaNMots"
        self.DossierResultInOutputDia = Path + "/3)Matching/ResultDia"

        df = pd.DataFrame(columns = self.ListEpoques)
        for i in range(len(self.ListRevues)):
            df.loc[i] = [0 for n in range(len(self.ListEpoques))]
        df.index = self.ListRevues
        print(df)


        # CREATE TABLEAU AVEC PRESENCE ABSENCE DE DONNEES
        #df.loc["Ann"] = [1, 1, 1, 1, 1, 1]
        #df.loc["Esp"] = [0, 0, 0, 0, 1, 1]

        for epoque in self.ListEpoques:
            for revue in self.ListRevues:
                if (epoque.replace("-","") + revue + ".fmgs") in os.listdir(self.PathDataDiaNMots):
                    df.ix[revue, epoque] = 1

        print(df)

        # Ecriture d'OrderNode
        with open(Path + "/3)Matching/ordernode.txt", 'a') as f:
            for epoque in self.ListEpoques:
                for revue in self.ListRevues:
                    if df.ix[revue, epoque] == 1:
                        ER = epoque.replace("-", "") + revue
                        f.write(ER + "\n")



        # itération sur df et quand il y a des 1, va aller chercher le nombre de cluster
        # dans MATCHING
        # Cree Dico et list adapté

        self.DicoEpoqueRevueAvecNbreML = OrderedDict()

        for epoque in self.ListEpoques:
            self.DicoEpoqueRevueAvecNbreML[epoque] = []
            for revue in self.ListRevues:
                if df.ix[revue, epoque] == 1:
                    print(epoque.replace("-", ""))
                    NameOpenFile = epoque.replace("-", "") + revue + ".fmgs"

                    with open(self.PathDataDiaNMots + "/" + NameOpenFile, "r") as f:
                        content = f.readlines()
                    compteML = 0
                    for line in content:
                        if line[0] == "G":
                            compteML += 1
                    print(compteML)
                    print("\n")

                    self.DicoEpoqueRevueAvecNbreML[epoque].append((revue, epoque, compteML))

        print(self.DicoEpoqueRevueAvecNbreML)



        # DiachroAFaire

        self.DiachroFaite = []

        for i, elt in enumerate(self.DicoEpoqueRevueAvecNbreML.keys()):
            # match ne va concerner la dernière période
            if i < len(self.DicoEpoqueRevueAvecNbreML) - 1:
                print(elt)
                print(self.DicoEpoqueRevueAvecNbreML[elt])
                eltplus1 = self.ListEpoques[i + 1]
                print(eltplus1)
                print(self.DicoEpoqueRevueAvecNbreML[eltplus1])

                # Matche entre toutes les paires existantes
                if not CompareJustNewRevue :
                    for elt1 in self.DicoEpoqueRevueAvecNbreML[elt]:
                        for elt2 in self.DicoEpoqueRevueAvecNbreML[eltplus1]:
                            EpoqueRevue1 = elt.replace("-", "") + elt1[0]
                            EpoqueRevue2 = eltplus1.replace("-", "") + elt2[0]
                            self.TraitDiachroLocale(EpoqueRevue1,EpoqueRevue2, SelectLink)
                            self.DiachroFaite.append(EpoqueRevue1 + "Vers" + EpoqueRevue2)
                    print("\n")

                else :

                    # Match entre les revues seulement si nouvelle revue !!!
                    for elt2 in self.DicoEpoqueRevueAvecNbreML[eltplus1]:
                        if elt2[0] in [elt1[0] for elt1 in self.DicoEpoqueRevueAvecNbreML[elt]]:
                            EpoqueRevue1 = elt.replace("-", "") + elt2[0]
                            EpoqueRevue2 = eltplus1.replace("-", "") + elt2[0]
                            self.TraitDiachroLocale(EpoqueRevue1, EpoqueRevue2, SelectLink)
                            self.DiachroFaite.append(EpoqueRevue1 + "Vers" + EpoqueRevue2)
                        else:
                            for elt1 in self.DicoEpoqueRevueAvecNbreML[elt]:
                                EpoqueRevue1 = elt.replace("-", "") + elt1[0]
                                EpoqueRevue2 = eltplus1.replace("-", "") + elt2[0]
                                self.TraitDiachroLocale(EpoqueRevue1, EpoqueRevue2, SelectLink)
                                self.DiachroFaite.append(elt.replace("-", "") + elt1[0] + "Vers" + eltplus1.replace("-", "") + elt2[0])
                    print("\n")

        # Ecriture d'OrderLink
        with open(Path + "/3)Matching/orderlink.txt", 'a') as f:
            for elt in self.DiachroFaite:
                f.write(elt + "\n")


    # MARCHE AVEC DiachronismOld
    def TraitDiachroLocaleOld(self, EpoqueRevue1, EpoqueRevue2, DiviAllML):
        ER1 = self.PathDataDiaNMots + "/" + EpoqueRevue1 + ".fmgs"
        ER2 = self.PathDataDiaNMots + "/" + EpoqueRevue2 + ".fmgs"
        DiachroLocale = diachronism(ER1, ER2, DiviAllML)

        self.CompilResult = [elt for elt in DiachroLocale.Pt_s if
                             (elt['source'], elt['cible']) in DiachroLocale.ListMatch]
        self.CompilResult2 = [elt for elt in DiachroLocale.Ps_t if
                              (elt['cible'], elt['source']) in DiachroLocale.ListMatch]

        with open(self.DossierResultInOutputDia + "/" + EpoqueRevue1 + "Vers" + EpoqueRevue2 + '.txt', 'a') as f:
            for elt in self.CompilResult:
                SearchProbaOtherSens = [elt1 for elt1 in self.CompilResult2 if
                                        (elt1['cible'] == elt['source'] and elt1['source'] == elt['cible'])]
                f.write(elt["source"] + "," + elt["cible"] + "," + str(elt["proba"]) + "," + str(
                    SearchProbaOtherSens[0]['proba']) + '\n')


    def TraitDiachroLocale(self, EpoqueRevue1, EpoqueRevue2, SelectLink):
        ER1 = self.PathDataDiaNMots + "/" + EpoqueRevue1 + ".fmgs"
        ER2 = self.PathDataDiaNMots + "/" + EpoqueRevue2 + ".fmgs"
        DiachroLocale = diachronism(ER1, ER2, SelectLink)

        self.CompilResult1 = [elt for elt in DiachroLocale.Intesec1 if
                             (elt['cluster1'], elt['cluster2']) in DiachroLocale.ListMatch]
        self.CompilResult2 = [elt for elt in DiachroLocale.Intesec2 if
                              (elt['cluster2'], elt['cluster1']) in DiachroLocale.ListMatch]

        print("TEST1")
        print(self.CompilResult1)
        print("TEST2")
        print(self.CompilResult1)

        with open(self.DossierResultInOutputDia + "/" + EpoqueRevue1 + "Vers" + EpoqueRevue2 + '.txt', 'a') as f:
            for elt1 in self.CompilResult1:
                SearchProbaOtherSens = [elt2 for elt2 in self.CompilResult2 if
                                        (elt2['cluster2'] == elt1['cluster1'] and elt2['cluster1'] == elt1['cluster2'])]
                f.write(elt1["cluster1"] + "," + elt1["cluster2"] + "," + str(elt1["intersection"]) + "," +
                        str(SearchProbaOtherSens[0]['intersection']) + '\n')