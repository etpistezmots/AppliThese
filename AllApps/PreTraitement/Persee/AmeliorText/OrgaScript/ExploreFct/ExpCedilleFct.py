
import os
import matplotlib.pyplot as plt
from django.conf import settings
from AllApps.PreTraitement.Persee.DelimitCorpus.models import  CorpusEtude, DocTransforme
from AllApps.PreTraitement.Persee.DelimitCorpus.outils.xpath import  DocMot
import statistics
import os
from lxml import etree
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.AideTitreFct import GetAdresseCompletDoc



########################################################################
############## PARTIE CREATION DES DICTIONNAIRE ########################
########################################################################

def CreateDico():
    ############ Create DicoVerger intermediaire s'il n'existe pas: ##############
    #Quelques modifications manuelles --> DicoVergerFin.txt
    # Attention source pas disponible : pdf du livre gentimment fourni par F Verger

    BaseDicoVerger = settings.DATA_DIR + "/Dico/DicoVergerAll.txt"
    ResultDicoVerger = settings.DATA_DIR + "/Dico/DicoVergerBrut.txt"
    if not os.path.isfile(ResultDicoVerger):
        lines = [line.rstrip('\n') for line in open(BaseDicoVerger)]
        with open(ResultDicoVerger,"a") as f:
            for i,line in enumerate(lines):
                # Si c'est en majuscule et supérieur à une lettre
                if line.isupper() and len(line) > 1 and i>1:
                    f.write(line.lower() + "\n")


    ##############  Create DicoGeographe #####################################
    ResultDicoGeographe = settings.DATA_DIR + "/Dico/DicoGeographe.txt"
    if not os.path.isfile(ResultDicoGeographe):
        # A été décommenté car webdriver pas installé sur la version serveur
        '''
        driver = webdriver.Firefox()
        driver.get("http://geotheque.org/dictionnaire-des-geographes/#A")
        auteurs = driver.find_elements(By.XPATH, "//div[@class='dicoTitle']")
        '''
        listaut=[]
        # Idem précedent
        '''
        for aut in auteurs:
            if "(comme" not in aut.text:
                listaut.append(aut.text)
        '''
        with open(ResultDicoGeographe, 'a') as the_file:
            for elt in listaut:
                the_file.write(elt.lower() +'\n')


    ##################### Create DicoHypergeo ##########################
    #puis de 0 à 340 par saut de 20
    #http://www.hypergeo.eu/spip.php?mot20&amp;debut_mots_freres=0&debut_mots_freres=20#pagination_mots_freres
    ResultDicoHypergeo = settings.DATA_DIR + "/Dico/DicoHypergeo.txt"
    if not os.path.isfile(ResultDicoHypergeo):
        adressebase=["http://www.hypergeo.eu/spip.php?mot20&amp;debut_mots_freres=0#pagination_mots_freres"]
        for i in range(0,340,20):
            adresse = "http://www.hypergeo.eu/spip.php?mot20&amp;debut_mots_freres=" + str(i) +"&debut_mots_freres=" + str(i+20) +"#pagination_mots_freres"
            adressebase.append(adresse)
        listmots=[]
        '''
        for elt in adressebase:
            driver = webdriver.Firefox()
            driver.get(elt)
            mots = driver.find_elements(By.XPATH, "//div[@class='aside']/div[2]/ul/li/a")
            for mot in mots:
                if mot.text.lower() not in listmots
                    listmots.append(mot.text)
            driver.quit()
        '''
        with open(ResultDicoHypergeo, 'a') as the_file:
            for elt in listmots:
                the_file.write(elt.lower() +'\n')


    ################### Create DicoMorphalou ###########################
    # source : https://repository.ortolang.fr/api/content/morphalou/v3.1
    BaseDicoMorphalou = settings.DATA_DIR + "/Dico/Morphalou3.1_LMF.xml"
    ResultDicoMorphalou = settings.DATA_DIR + "/Dico/DicoMorphalou.txt"
    if not os.path.isfile(ResultDicoMorphalou):
        tree = etree.parse(BaseDicoMorphalou)
        mottout = tree.xpath("/lexicon/lexicalEntry/formSet/inflectedForm/orthography")
        listresult=[]

        for mot in mottout:
            for elt in mot.text.split():
                if elt not in listresult:
                    listresult.append(elt)

        with open(ResultDicoMorphalou, 'a') as the_file:
            for elt in listresult:
                the_file.write(elt.lower() +'\n')


    ################# Create DicoProlex ##################################
    # source : https://www.cnrtl.fr/lexiques/prolex/
    BaseDicoProlex= settings.DATA_DIR + "/Dico/ProLMF_2_2/ProLMF_2_2.xml"
    ResultDicoProlex= settings.DATA_DIR + "/Dico/DicoProlex.txt"
    if not os.path.isfile(ResultDicoMorphalou):
        tree = etree.parse(BaseDicoProlex)
        mottout = tree.xpath("/LexicalResource/Lexicon/LexicalEntry/Lemma")
        listresult=[]

        for mot in mottout:
            for elt in mot.text.split():
                if elt not in listresult:
                    listresult.append(elt)

        with open(ResultDicoProlex, 'a') as the_file:
            for elt in listresult:
                the_file.write(elt.lower() +'\n')


    ################### Dico Brunet crée à la main #####################
    ################### Dico Lacoste créé à la main ####################
    ################### Dico Levi-Lussault créé à la main ##############


def EssaiCreationPlurielDesMotsGeo():
    '''Pour essayer d'avoir le pluriel des noms spécifique à la géo'''

    ResultPlurielGeo = settings.DATA_DIR + '/Dico/DicoPlurielGeoBrut.txt'
    # Quelques corrections manuelles --> PlurielGeoBrut.txt
    if not os.path.isfile(ResultPlurielGeo):
        # GeoListComplet permet de savoir de quel dico provient le mot
        # GeoAbbrev permet de savoir si le mot est une abréviation : style ASEAN
        GeoList = []
        GeoListComplet = []
        GeoAbbrev = []
        dicos = ["VergerFin","Brunet","Lacoste","LevyLussault","Geographe","Hypergeo"]
        for dico in dicos:
            with open(settings.DATA_DIR + "/Dico" + dico + ".txt") as f:
                for line in f:
                    # petite subtilité pour enlever les prefixe dans Brunet
                    # ex : retro-
                    if line[-2]!='-':
                        # on eleve les apostrope et on splitte
                        for elt in line.replace("'", " ").replace("’", " ").split():
                            if elt not in GeoList:
                                # on complète les listes
                                GeoList.append(elt.lower())
                                GeoListComplet.append((elt.lower(), dico))
                                # Attention, ne marche que pour les dicos entrés manuellement
                                if elt.isupper():
                                    GeoAbbrev.append(elt.lower())

        # récupération des mots communs et propres pas spécifiques à la géo
        # car il y a déjà les pluriels pour les noms communs
        # et ce n'est pas très approprié pour les noms propres
        nomcommun = []
        ResultDicoMorphalou = settings.DATA_DIR + "/Dico/DicoMorphalou.txt"
        with open(ResultDicoMorphalou) as f:
            for line in f:
                # -1 car sinon ajoute le \n à la fin
                nomcommun.append(line[:-1])

        nompropre = []
        ResultDicoProlex= settings.DATA_DIR + "/Dico/DicoProlex.txt"
        with open(ResultDicoProlex) as f:
            for line in f:
                nompropre.append(line[:-1])

        GeoListFin = []
        for elt in GeoList:
            if (elt not in nomcommun) and (elt not in nompropre):
                GeoListFin.append(elt)

        # Va créer un fichier avec pluriel et singulier pré-rempli
        with open(ResultPlurielGeo, 'a') as f:
            for elt in GeoListFin:
                # provenance pour ne marquer les noms de géographe au pluriel
                provenance = [item for item in GeoListComplet if item[0] == elt]
                # Gestion des plureils
                if (provenance[0][1] != "Geographe") and (provenance[0][0][-1] != "s") and\
                        (provenance[0][0][-1] != "x") and (provenance[0][0] not in GeoAbbrev)\
                        and (provenance[0][0][-2:]!="al") \
                        and (provenance[0][0][-3:] != "ien") \
                        and (provenance[0][0][-3:] != "iel") \
                        and (provenance[0][0][-2:] != "if"):
                    f.write(elt + "s" + '\n')
                # rajout al ---> aux, ales, ale
                if (provenance[0][1] != "Geographe") and (provenance[0][0][-2:] == "al") and\
                        (provenance[0][0] not in GeoAbbrev):
                    f.write(elt[:-2] + "ale" + '\n')
                    f.write(elt[:-2] + "ales" + '\n')
                    f.write(elt[:-2] + "aux" + '\n')

                # rajout ien ---> iens, ienne, iennes
                if (provenance[0][1] != "Geographe") and (provenance[0][0][-3:] == "ien") and \
                        (provenance[0][0] not in GeoAbbrev):
                    f.write(elt[:-3] + "iens" + '\n')
                    f.write(elt[:-3] + "ienne" + '\n')
                    f.write(elt[:-3] + "iennes" + '\n')

                # rajout iel ---> iels, ielle, ielles
                if (provenance[0][1] != "Geographe") and (provenance[0][0][-3:] == "iel") and \
                        (provenance[0][0] not in GeoAbbrev):
                    f.write(elt[:-3] + "iels" + '\n')
                    f.write(elt[:-3] + "ielle" +  '\n')
                    f.write(elt[:-3] + "ielles" + '\n')

                # rajout if ---> ive, ive, ives
                if (provenance[0][1] != "Geographe") and (provenance[0][0][-2:] == "if") and \
                        (provenance[0][0] not in GeoAbbrev):
                    f.write(elt[:-2] + "ifs" + '\n')
                    f.write(elt[:-2] + "ive" + '\n')
                    f.write(elt[:-2] + "ives" + '\n')



def FusionDico():
    ResultFusion = settings.DATA_DIR + '/Dico/DicoFusionAll.txt'
    if not os.path.isfile(ResultFusion):
        dicos = ["VergerFin", "Brunet", "Lacoste", "LevyLussault", "Geographe", "Hypergeo"]
        motglobal = []
        for dico in dicos:
            with open(settings.DATA_DIR + "Dico" + dico + ".txt") as f:
                for line in f:
                    # petite subtilité pour enlever les prefixe dans Brunet
                    # ex : retro-
                    if line[-2] != '-':
                        # on eleve les apostrope et on splitte
                        for elt in line.replace("'", " ").replace("’", " ").split():
                            if elt not in motglobal:
                                # on complète les listes
                                motglobal.append(elt.lower())

        ResultPluriels = settings.DATA_DIR + "/Dico/DicoPlurielGeoNet.txt"
        with open(ResultPluriels) as f:
            for line in f:
                if line[:-1] not in motglobal:
                    # -1 car sinon ajoute le \n à la fin
                    motglobal.append(line[:-1])


        ResultDicoMorphalou = settings.DATA_DIR + "/Dico/DicoMorphalou.txt"
        with open(ResultDicoMorphalou) as f:
            for line in f:
                if line[:-1] not in motglobal:
                # -1 car sinon ajoute le \n à la fin
                    motglobal.append(line[:-1])

        ResultDicoProlex = settings.DATA_DIR + "/Dico/DicoProlex.txt"
        with open(ResultDicoProlex) as f:
            for line in f:
                if line[:-1] not in motglobal:
                    motglobal.append(line[:-1])

        with open(ResultFusion, 'a') as f:
            for elt in motglobal:
                f.write(elt + '\n')


def FusionDicoCedille():
    ResultCedille = settings.DATA_DIR + '/Dico/DicoCedille.txt'
    ResultFusion = settings.DATA_DIR + '/Dico/DicoFusionAll.txt'

    if not os.path.isfile(ResultCedille):
        motcedille = []
        with open(ResultFusion) as f:
            for line in f:
                if "ç" in line:
                    motcedille.append(line[:-1])

        with open(ResultCedille, 'a') as f:
            for elt in motcedille:
                f.write(elt + '\n')


def VerifAvantApresCedilleExist(FichierResult):
    ResultCedille = settings.DATA_DIR + '/Dico/DicoCedille.txt'
    ResultFusion =settings.DATA_DIR + '/Dico/DicoFusionAll.txt'
    motcedille = []
    motall = []
    motcedilleavtapres = []

    if not os.path.isfile(FichierResult):
        with open(ResultFusion) as f:
            for line in f:
                motall.append(line[:-1])

        with open(ResultCedille) as f:
            for line in f:
                motcedille.append(line[:-1])

        for mot in motcedille:
            eltavant = mot.split("ç")[0]
            eltapres = mot.split("ç")[1]
            if (eltavant in motall) and (eltapres in motall):
                motcedilleavtapres.append(mot)

        with open(FichierResult, 'a') as f:
            for mot in motcedilleavtapres:
                f.write(mot + '\n')

    else:
        with open(FichierResult) as f:
            for line in f:
                motcedilleavtapres.append(line[:-1])

    return motcedilleavtapres








