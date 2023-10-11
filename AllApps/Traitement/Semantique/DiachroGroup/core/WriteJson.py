import os, csv, sys
from decimal import Decimal
from matplotlib import colors
from django.conf import settings
from AllApps.Traitement.Semantique.TableauEmb.views import ModelFormInit
from collections import OrderedDict

class WriteJson:

    def __init__(self, Path, Periodes, ChoixUtilisateurRevuesCouleurs, nomencours, termeencours, taillecluster):

        PathJson = Path + "/4)Json"
        os.makedirs(PathJson)

        ListPeriodes = Periodes.split(",")
        NomExpe = Path.split("/")[-1]

        PathFichierResult = PathJson + "/" + NomExpe + ".json"

        ############### 1) META #######################

        # Variables qui règlent l'intensité de gris des liens
        minstree = 0.35
        maxstree = 0.85

        # calculs basiques
        datemin = ListPeriodes[0][0:4]
        datemax = ListPeriodes[-1][5:9]
        AmplitudeAllPeriode = int(datemax) - int(datemin)
        NbrPeriodes = str(len(ListPeriodes))

        # ecrit le début du Json : les métas
        self.WriteMetaJson(PathFichierResult, datemin, datemax, NbrPeriodes, minstree, maxstree)


        ################ 2) NODE  ######################

        # variables pour calcul coord x (à reprendre pour quelque chose de plus précis au niveau calcul step
        # ici est fixe car période de même longueur de temps mais on peut faire calcul par la suite
        # dans la fonction ComputeCoordX ci dessous)
        xref = Decimal('0.0')
        xrefmilieu = Decimal('0.0')

        # elts de stockage
        perioderef = ""
        StockNbreEltByPeriodeRef = []

        # ecrit l'intro du JSON pour les Nodes
        self.WriteInitNode(PathFichierResult)

        with open(Path + "/3)Matching/ordernode.txt", 'r') as fr:
            noeuds = fr.readlines()

        '''
        testpoidsencours = self.TestPoids(Path)
        '''

        for i, elt in enumerate(noeuds):

            print(elt)

            # change la coordonnées de l'axe des x : voir fin de la boucle perioderef = elt[0:8]
            # Procédure qui s'explique car je peux avoir pour mes deux revues les mêmes périodes
            # dans ce cas, on ne saute pas au step suivant
            # les deux revues seront ensuite distingué par les couleurs
            xref, xrefmilieu = self.ComputeCoordX(elt, perioderef, xref, xrefmilieu, AmplitudeAllPeriode)

            # Recup des infos : compositions des clusters, remplit StockNbreEltByPeriodeRef (periode étant ici periode*revue)
            pathencours = Path + "/3)Matching/DataDiaNMots/" + elt[:-1] + ".fmgs"
            if not(os.path.exists(pathencours)):
                pathencours = Path + "/3)Matching/DataDiaAllMots/" + elt[:-1] + ".fmgs"

            DicoResult, StockNbreEltByPeriodeRef = self.GetCompoEns(pathencours, StockNbreEltByPeriodeRef)


            # itere sur chaque ensemble de la période considérée
            for j, elt2 in enumerate(DicoResult):

                # retient les 15 premiers termes
                SeuilMotSpecific = 15
                MotsSpecifCluster = self.GetMotSpecific(DicoResult, elt2, SeuilMotSpecific)
                print(MotsSpecifCluster)

                # Seuil 5 auteurs, 5 docs
                SeuilAuthorSpecific = 5
                SeuilDocSpecific = 5
                Author, Doc, TermesNbres, comptetot = self.GetAuthorAndDocSpecific(Path, elt, MotsSpecifCluster, SeuilAuthorSpecific, SeuilDocSpecific, nomencours, termeencours)

                if taillecluster == "Nombre termes constitutifs cluster":
                    PoidsEnCours = len(DicoResult[elt2])
                else:
                    PoidsEnCours = comptetot


                # prepa ecriture du body du Json pour les Nodes
                RevueEnCours = elt[8:-1]

                    # Determination de la couleur
                ColorRevueEnCours = self.ColorEns2(RevueEnCours, ChoixUtilisateurRevuesCouleurs)

                    # prepa ecriture fin du Json pour les Nodes
                indexDernierePeriode = len(noeuds) - 1
                indexDernierEns = len(DicoResult) - 1

                '''
                PoidsEnCours = testpoidsencours[elt[:-1]][elt2]
                '''

                # ecriture du body du json pour les nodes
                # si ce n'est pas le dernier element
                if not(i == indexDernierePeriode and j == indexDernierEns):

                    self.WriteBodyNode(elt[:-1], PathFichierResult, MotsSpecifCluster, TermesNbres, ColorRevueEnCours, xrefmilieu, PoidsEnCours, Author, Doc)

                # si c'est le dernier element
                else:
                    self.WriteEndNode(elt[:-1], PathFichierResult, MotsSpecifCluster, TermesNbres, ColorRevueEnCours, xrefmilieu, PoidsEnCours, Author, Doc)

            # Met à jour perioderef : sert à ComputeCoordX dans la boucle
            perioderef = elt[0:8]


        ################ 3) EDGE  ######################


        self.WriteInitEdge(PathFichierResult)

        # Aller chercher dans orderlink.txt
        with open(Path + "/3)Matching/orderlink.txt", 'r') as fr1:
            content = fr1.readlines()

        LastEltWithLink = self.FindLastEltWithLink(Path)

        for i, line in enumerate(content):
            print(line[:-1])
            #source, cible = line[0:11], line[15:26]
            [source, cible] = [eltdecoup for eltdecoup in line[:-1].split("Vers")]

            # Va ouvrir le fichier associé de résultat
            # pour récupérer les ensembles sources et ensembles cibles qui ont matchés
            with open(Path + "/3)Matching/ResultDia/" + line[:-1] + ".txt", "r") as fr2:
                content1 = fr2.readlines()

                EnsSource = [line1.split(",")[0].split("_")[0] for line1 in content1]
                EnsCible = [line1.split(",")[1].split("_")[0]  for line1 in content1]
                ProbaLink1 = [line1.split(",")[2][0:4] for line1 in content1]
                ProbaLink2 = [line1.split(",")[3][0:4] for line1 in content1]
                # La moyenne des deux ProbaLink précédent réduit à deux chiffres après la virgule et retransformé en str
                ProbaLink = [str(round((float(g) + float(h)) / 2, 2)) for g, h in zip(ProbaLink1, ProbaLink2)]

                # Compute assymétrie
                DiffLink = [round(float(g) - float(h), 2) for g, h in zip(ProbaLink1, ProbaLink2)]
                MoyLink = [round((float(g) + float(h)) / 2, 2) for g, h in zip(ProbaLink1, ProbaLink2)]
                MoyLinkDiv2 = [round((float(g) + float(h)) / 4, 2) for g, h in zip(ProbaLink1, ProbaLink2)]

                Assymetrie = [self.FctAssymetrie(Diff, Moy, MoyDiv2) for Diff, Moy, MoyDiv2 in
                              zip(DiffLink, MoyLink, MoyLinkDiv2)]

            print("Source :  " + source)
            print("Cible : " + cible)
            print("Ens source qui ont matché : ")
            print(EnsSource)
            print("Ens cible qui ont matché : ")
            print(EnsCible)

            # Je trouve à partir du nom : la source et la cible
            # par ex si source = 19932014Ann
            # je vais aller chercher dans la liste ordonnées = tous les ensembles précédents
            # ---> "18911911Ann", "19121931Ann","19321951Ann","19521971Ann","19721992Ann","19721992Esp
            # Je fais la somme de leur cluster grace à StockNbreEltByPeriodeRef
            # --> 5+6+5+6+6+6
            # a additionner au nombre du cluster matché pour trouver le rang

            NewSource = self.ComputeEdgeWithINdexNodes(source, EnsSource, noeuds, StockNbreEltByPeriodeRef, "source")


            # idem pour la cible:
            # on additionne tous ce qu'il y a avant et on rajoute pour le rang
            # permet de compléter link

            NewCible = self.ComputeEdgeWithINdexNodes(cible, EnsCible, noeuds, StockNbreEltByPeriodeRef,
                                                       "cible")


            # rajouter trouver mot commun et  diff !!!!
            testfolder = Path + "/3)Matching/DataDiaNMots"
            MarqueurSeuil = False
            if os.path.exists(testfolder):
                pathencourssource = Path + "/3)Matching/DataDiaNMots/" + source + ".fmgs"
                pathencourscible = Path + "/3)Matching/DataDiaNMots/" + cible + ".fmgs"
            else:
                pathencourssource = Path + "/3)Matching/DataDiaAllMots/" + source + ".fmgs"
                pathencourscible = Path + "/3)Matching/DataDiaAllMots/" + cible + ".fmgs"


            # Write Link

            for j, NewElt in enumerate(NewSource):

                TermesCommuns, TermeOnlyCible, TermeOnlySource = self.ComputeTermesCommunetDiff(pathencourssource,
                                                                                                pathencourscible,
                                                                                                EnsSource, EnsCible, j)

                # si ce n'est pas le dernier element
                if not ((LastEltWithLink == line[:-1]) and (j == len(NewSource) - 1)):
                    self.WriteBodyEdge(PathFichierResult, j, NewElt, NewCible, ProbaLink, Assymetrie, TermesCommuns,
                                       TermeOnlyCible, TermeOnlySource)
                # si c'est le dernier element
                else:
                    self.WriteLastEdge(PathFichierResult, j, NewElt, NewCible, ProbaLink, Assymetrie, TermesCommuns,
                                      TermeOnlyCible, TermeOnlySource)

        self.WriteEndEdge(PathFichierResult)




    ################# Fonctions associées ##################



    def WriteMetaJson(self, PathFichierResult, datemin, datemax, NbrPeriodes, minstree, maxstree):

        with open(PathFichierResult, 'a') as f:
            textinsert = '''{"metas": {
                "min_year":''' + datemin + ''',
                "minstre":''' + str(minstree) + ''',
                "max_year":''' + datemax + ''',
                "maxstre":''' + str(maxstree) + ''',
                "nb_ticks":''' + NbrPeriodes + '''
            },'''
            f.write(textinsert + "\n")


    def WriteInitNode(self, PathFichierResult):
        with open(PathFichierResult, 'a') as f:
            f.write('''    "nodes": [''' + "\n")


    def ComputeCoordX(self, elt, perioderef, xref, xrefmilieu, amplitude):
        if perioderef != elt[0:8]:
            AmplitudePeriodeEnCours = int(elt[4:8]) - int(elt[0:4])
            # On met le rectangle au milieu de la période
            AmplitudePeriodeEnCoursDiv2 = AmplitudePeriodeEnCours / 2
            stepmilieu = Decimal(str(round(AmplitudePeriodeEnCoursDiv2 / amplitude, 2)))
            steptot = Decimal(str(round(AmplitudePeriodeEnCours / amplitude, 2)))
            xrefmilieu = xref + stepmilieu
            xref += steptot
        return xref, xrefmilieu


    def GetCompoEns(self, pathencours, StockNbreEltByPeriodeRef):
        '''
        entrée : pathencours: indique le fichier où sont stockés les infos issus de ReinertToDia (TransformDataToDiachronism)
                 stockNbreEltByPeriodeRef: Liste qui se remplit au fur et à mesure de l'éxécution de la boucle
        sortie : la liste précédente
                 Composition du cluster sous forme de dictionnaire
        '''

        DicoResult = OrderedDict()
        NomPartie = ""

        with open(pathencours) as fr:
            content = fr.readlines()

        for line in content:
            # Si c'est la marque d'un nouvel ensemble
            # Ex "G0-0	25	19" avec des tabulations comme séparateur
            if line[0] == "G":
                # recup son nom"
                EnsInfo = line.split("\t")
                NomPartie = EnsInfo[0][1:].split("-")[0]

                # Crée une nouvel entrée dans le dico
                DicoResult[NomPartie] = OrderedDict()

            # Ex "	industrie	5488" mais aussi espace entre les ensembles (d'où le "and line[0:1]!="\n")
            if line[0] != "G" and line[0:1] != "\n":
                mot, score = line.split("\t")[1], line.split("\t")[2][:-1]

                # si correspond à un nouveau mot, insertion dans le dico avec le score correspondant
                if mot != "":
                    DicoResult[NomPartie][mot] = float(score)

        # Sauve nombre cluster
        StockNbreEltByPeriodeRef.append(len(DicoResult))

        return DicoResult,StockNbreEltByPeriodeRef


    def GetMotSpecific(self, DicoResult, elt2, SeuilMotSpecific):
        ListMotsSpecifCluster = []
        for k,elt3 in enumerate(DicoResult[elt2]):
            if k < SeuilMotSpecific:
                ListMotsSpecifCluster.append(elt3)
        return ListMotsSpecifCluster


    def GetAuthorAndDocSpecific(self, ActualPath, node, ListMotsSpecifCluster, n_auteurs, n_docs, nomencours, termeencours):
        Mode = ActualPath.split("/")[-3]
        DicInitModelD, DicInitFormD = ModelFormInit(Mode)
        CorpusName = DicInitModelD["initial"].objects.get(nom=nomencours).CorpusFinRef.nom
        fileencours = settings.RESULT_PRETRAIT_DIR + "/FinaliseCorpus/CorpusFin/" + CorpusName + ".csv"
        dateinf = int(node[0:4])
        datesup = int(node[4:8])
        revue = node[8:-1]
        AuteurDejaVu = []
        TermeDejaVu = []
        AuthorCount = []
        TermeCount = []
        DocCount = []
        compteglobal = 0
        if os.path.isfile(fileencours):
            with open(fileencours, 'r') as f_in:
                csv.field_size_limit(sys.maxsize)
                reader = csv.reader(f_in, delimiter='\t')
                next(reader)  # skip the heading
                for row in reader:
                    IdEncours, NomPerseeEnCours, RevueEnCours, DateEnCours, TypeEnCours, TitreEnCours, AuteursEnCours, TextEnCours = row
                    if int(DateEnCours) >= dateinf and int(DateEnCours) <= datesup and RevueEnCours == revue:
                        TestTermeRef = TextEnCours.count(" " + termeencours + " ")
                        if TestTermeRef >0:
                            comptecluster = 0
                            for terme in ListMotsSpecifCluster:

                                comptemotlocal = TextEnCours.count(" " + terme + " ")

                                if comptemotlocal > 0:

                                    if terme in TermeDejaVu:
                                        index = TermeDejaVu.index(terme)
                                        CountMotDejaCalcule = TermeCount[index][1]
                                        TermeCount[index] = (terme, CountMotDejaCalcule + comptemotlocal)
                                    else:
                                        TermeDejaVu.append(terme)
                                        TermeCount.append((terme, comptemotlocal))

                                    comptecluster = comptecluster + comptemotlocal

                            if comptecluster>0:

                                auteurlist = AuteursEnCours.split(",")
                                for auteur in auteurlist:
                                    if auteur != "":
                                        if auteur in AuteurDejaVu:
                                            index = AuteurDejaVu.index(auteur)
                                            CountDejaCalcule = AuthorCount[index][1]
                                            AuthorCount[index]= (auteur,CountDejaCalcule + comptecluster)
                                        else:
                                            AuteurDejaVu.append(auteur)
                                            AuthorCount.append((auteur,comptecluster))

                                DocCount.append((NomPerseeEnCours,comptecluster))

                                compteglobal = compteglobal + comptecluster

        if len(AuthorCount)>0:
            AuthorCount.sort(key=lambda tup: tup[1], reverse=True)
        if len(DocCount) > 0:
            DocCount.sort(key=lambda tup: tup[1], reverse=True)
        if len(TermeCount) > 0:
            TermeCount.sort(key=lambda tup: tup[1], reverse=True)


        if len(AuthorCount)>n_auteurs:
            AuthorCount = AuthorCount[0:n_auteurs]
        if len(DocCount)>n_docs:
            DocCount = DocCount[0:n_docs]

        AuteurFin = ""
        for i,autcount in enumerate(AuthorCount):
            if i ==0:
                AuteurFin = autcount[0] + "(" + str(autcount[1])+ ")"
            else:
                AuteurFin = AuteurFin + ", " + autcount[0] + "(" + str(autcount[1])+ ")"

        DocFin = ""
        for i,dcount in enumerate(DocCount):
            if i == 0:
                DocFin = "<a href='https://www.persee.fr/doc/" + dcount[0].split("_", 1)[-1] + "'>" \
                         + dcount[0].split("_", 3)[-1] + "</a>" + " (" + str(dcount[1]) + ")"
            else:
                DocFin = DocFin + ", " + "<a href='https://www.persee.fr/doc/" + dcount[0].split("_",1)[-1] +"'>"\
                     + dcount[0].split("_",3)[-1] + "</a>" + " (" + str(dcount[1])+ ")"

        TermeFin = ""
        for i,termcount in enumerate(TermeCount):
            if i ==0:
                TermeFin = termcount[0] + "(" + str(termcount[1])+ ")"
            else:
                TermeFin = TermeFin + ", " + termcount[0] + "(" + str(termcount[1])+ ")"


        return AuteurFin, DocFin, TermeFin, compteglobal





    def ColorEns2(self, RevueEnCours, ChoixUtilisateurRevuesCouleurs):
        ColorRevueEnCours = ""
        EltsRevueColorAssociate = ChoixUtilisateurRevuesCouleurs.split(",")
        # ['Ann:blue', 'Esp:green']
        for eltRevueColor in EltsRevueColorAssociate:
            eltRevueColorDissociate = eltRevueColor.split(":")
            if eltRevueColorDissociate[0] == RevueEnCours:
                # voir les couleurs sous matplotlib
                # https://stackoverflow.com/questions/22408237/named-colors-in-matplotlib
                ColorRevueEnCours = colors.cnames[eltRevueColorDissociate[1]]
        return ColorRevueEnCours


    def WriteBodyNode(self, elt, PathFichierResult, MotsSpecifCluster,  TermesNbres, ColorRevueEnCours, x, poids, Author, Doc):
        with open(PathFichierResult, 'a') as fw:
            fw.write('''                {
            "name":"''' + MotsSpecifCluster[0] + '''",
            "termsnbrs": "''' + TermesNbres + '''",
            "terms": "''' + ",".join(MotsSpecifCluster) + '''",
            "auteurs":"''' + Author + '''",
            "docs":"''' +  Doc + '''",
            "color":"''' + ColorRevueEnCours + '''",
            "period":"''' + elt + '''",
            "sizess":''' + str(poids) + ''',
            "posx":''' + str(x) + ''',
            "posy": 0.0
        },''' + "\n")


    def WriteEndNode(self, elt, PathFichierResult, MotsSpecifCluster, TermesNbres, ColorRevueEnCours, x, poids, Author, Doc):
        with open(PathFichierResult, 'a') as fw:
            fw.write('''                {
            "name":"''' + MotsSpecifCluster[0] + '''",
            "termsnbrs":"''' +  TermesNbres + '''",
            "terms": "''' + ",".join(MotsSpecifCluster) + '''",
            "auteurs":"''' + Author + '''",
            "Docs":"''' +  Doc + '''",
            "color":"''' + ColorRevueEnCours + '''",
            "period":"''' + elt + '''",
            "sizess":''' + str(poids) + ''',
            "posx":''' + str(x) + ''',
            "posy": 0.0
        }
        ],''')


    def WriteInitEdge(self, PathFichierResult):
        with open(PathFichierResult, 'a') as fw:
            fw.write('''    "links": [''')


    def ComputeEdgeWithINdexNodes(self, ref, EnsRef, noeuds, StockNbreEltByPeriodeRef, refstring):
        MarqueurBefore = True
        ResultBefore = []
        for elt in noeuds:
            if elt[:-1] != ref and MarqueurBefore:
                ResultBefore.append(elt[:-1])
            else:
                MarqueurBefore = False
        print("Elt avant la " + refstring + ": ")
        print(ResultBefore)
        print(len(ResultBefore))
        NbreEnsBefore = StockNbreEltByPeriodeRef[0:len(ResultBefore)]
        print(NbreEnsBefore)
        print(sum(NbreEnsBefore))
        NewRef = [int(newelt) + sum(NbreEnsBefore) for newelt in EnsRef]
        print("result addition pour la " + refstring + ": ")
        print(NewRef)
        return NewRef


    def FindLastEltWithLink(self,adresse):
        # Aller chercher dans orderlink.txt
        with open(adresse + "/3)Matching/orderlink.txt", 'r') as fr3:
            content3 = fr3.readlines()

        for elt in reversed(content3):

            with open(adresse + "/3)Matching/ResultDia/" + elt[:-1] + ".txt", 'r') as fr4:
                content4 = fr4.readlines()

            if len(content4) != 0:
                break
        return elt[:-1]


    def FctAssymetrie(self, Diff, Moy, MoyDiv2):
        if Diff >= Moy:
            return "2"
        elif Diff >= MoyDiv2 and Diff < Moy:
            return "1"
        elif Diff < MoyDiv2 and Diff > (-1 * MoyDiv2):
            return "0"
        elif Diff <= (-1 * MoyDiv2) and Diff > (-1 * Moy):
            return "-1"
        elif Diff <= (-1 * Moy):
            return "-2"


    def WriteBodyEdge(self, PathFichierResult, j, NewElt, NewCible, ProbaLink, Assymetrie, TermesCommuns, TermeOnlyCible, TermeOnlySource):
        with open(PathFichierResult, 'a') as fw:
            fw.write('''                {
                        "source":''' + str(NewElt) + ''',
                        "target":''' + str(NewCible[j]) + ''',
                        "value":''' + ProbaLink[j] + ''',
                        "assymetrie":''' + Assymetrie[j] + ''',
                        "shared":"''' + ','.join(TermesCommuns[0:5]) + '''",
                        "onlysource":"''' + ','.join(TermeOnlySource[0:5]) + '''",
                        "onlycible":"''' + ','.join(TermeOnlyCible[0:5]) + '''"
                                },''' + "\n")

    def WriteLastEdge(self, PathFichierResult, j, NewElt, NewCible, ProbaLink, Assymetrie, TermesCommuns, TermeOnlyCible, TermeOnlySource):
        with open(PathFichierResult, 'a') as fw:
            fw.write('''                {
                        "source":''' + str(NewElt) + ''',
                        "target":''' + str(NewCible[j]) + ''',
                        "value":''' + ProbaLink[j] + ''',
                        "assymetrie":''' + Assymetrie[j] + ''',
                        "shared":"''' + ','.join(TermesCommuns[0:5]) + '''",
                        "onlysource":"''' + ','.join(TermeOnlySource[0:5]) + '''",
                        "onlycible":"''' + ','.join(TermeOnlyCible[0:5]) + '''"
                                }''' + "\n")

    def WriteEndEdge(self, PathFichierResult):
        with open(PathFichierResult, 'a') as fw:
            fw.write(''']
                        }''')

    def TestPoids(self, adresse):

        pathpoids = adresse + "/3)Matching/Poids.txt"

        with open(pathpoids, "r") as f:
            content = f.readlines()

        ResultPoidsSegment = {}
        EpoqueRef = ""
        for line in content:
            if line[0] != "G":
                EpoqueRef = line[:-1]
                ResultPoidsSegment[EpoqueRef] = {}
            else:
                NumeroML = line.split("\t")[0][1:]
                PoidsML = line.split("\t")[1][:-1]
                ResultPoidsSegment[EpoqueRef][NumeroML] = PoidsML

        return ResultPoidsSegment


    def ComputeTermesCommunetDiff(self,pathencourssource,pathencourscible,EnsSource,EnsCible,j):

        TermesSources = self.GetCompoPart(pathencourssource,EnsSource[j])
        TermesCibles =self.GetCompoPart(pathencourscible, EnsCible[j])

        TermesCiblesWithoutScore = [elt[0] for elt in TermesCibles]
        TermesSourcesWithoutScore = [elt[0] for elt in TermesSources]

        TermesCommuns = [elt[0] for elt in TermesSources if elt[0] in TermesCiblesWithoutScore]
        TermeOnlyCible = [elt[0] for elt in TermesCibles if elt[0] not in TermesSourcesWithoutScore]
        TermeOnlySource = [elt[0] for elt in TermesSources if elt[0] not in TermesCiblesWithoutScore]

        return TermesCommuns,TermeOnlyCible,TermeOnlySource



    def GetCompoPart(self,pathencours, numberML):

        ListResult = []
        MarqueurMLRecherche = False

        with open(pathencours) as fr:
            content = fr.readlines()

        for line in content:
            # Si c'est la marque d'un nouvel ensemble
            # Ex "G0-0	25	19" avec des tabulations comme séparateur
            if line[0] == "G":
                if line[1] == numberML:
                    MarqueurMLRecherche = True
                else:
                    MarqueurMLRecherche = False

            # Ex "	industrie	5488" mais aussi espace entre les ensembles (d'où le "and line[0:1]!="\n")
            if line[0] != "G" and line[0:1] != "\n" and MarqueurMLRecherche == True:
                mot, score = line.split("\t")[1], line.split("\t")[2][:-1]

                # si correspond à un nouveau mot, insertion dans le dico avec le score correspondant
                if mot != "":
                    ListResult.append((mot, float(score)))

        return ListResult





