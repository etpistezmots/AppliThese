from django.conf import settings
from lxml import etree

from AllApps.PreTraitement.Persee.DelimitCorpus.models import CorpusEtude, DocExtractInitial, Transformer
from AllApps.PreTraitement.Persee.DelimitCorpus.outils.xpath import DocMotPage, DocErudit
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.ExploreFct.ExpCoordGraphSimpleFct import GetListIDMots, \
    GetIntervalleMotsParFenetre, NbMotAvantPage
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.AideTitreFct import GetAdresseCompletDoc


# Exemple concret pour explication des 3 fonctions suivantes
# qui servent à l'agrégation :

# a = [(52,74),(78,137),(139,150),(160,192),(194,210),(220,230)]
# saut = [4,2,10,2,10]      résultat de calculsault()
# si seuil d'agrégation est 5
# indexfalse = [2,4]        résultat de defineindexesfalse

# Resultat attendu = [(52,150),(160,210),(220,230)]
# ALGO REFLEXION
# si indexfalse = [] alors simple [(premier elt, dernier elt)]
# sinon j'itere, je pars du premier elt : 2
# --> je met dans la liste [(premier elt, dernier elt du 2)]
# puis j'arrive sur le 4
# --> je mets dans la liste [(premier elt du 3, dernier elt du 4)]
# fini la liste mais il faut concle
# --> [(premier elt du 5, dernier elt]

def calculsaut(listintervalle):
    listesauts= []
    indexfin = 0
    for i,elt in enumerate(listintervalle):
        if i==0:
            indexfin = elt[1]
        else:
            saut = elt[0] - indexfin
            listesauts.append(saut)
            indexfin = elt[1]
    return listesauts

def defineindexesfalse(listsaut,seuilagreg):
    listeindexfalse = []
    for i,elt in enumerate(listsaut):
        if elt > seuilagreg:
            listeindexfalse.append(i)
    return listeindexfalse

def resultagreg(listinit,listindexfalse):
    NewIntervalleEfface = []
    if len(listindexfalse) == 0:
        NewIntervalleEfface.append((listinit[0][0], listinit[-1][1]))
    else:
        indexprec = 0
        for i, indexf in enumerate(listindexfalse):
            if i == 0:
                NewIntervalleEfface.append((listinit[0][0], listinit[indexf][1]))
            else:
                NewIntervalleEfface.append((listinit[indexprec + 1][0], listinit[indexf][1]))
            indexprec = indexf
        NewIntervalleEfface.append((listinit[indexprec + 1][0], listinit[-1][1]))
    return NewIntervalleEfface


def RecupResumeFr(document):
    doc_erudit = document.replace("tei", "erudit")
    tree = etree.parse(doc_erudit)
    XpathLangResume = "/erudit:article/erudit:liminaire/erudit:resume[@lang='fre']//erudit:alinea"

    listeLangResume = tree.xpath(XpathLangResume,
                           namespaces={"erudit": "http://www.erudit.org/xsd/article"})

    PresenceResumeBoolean = False
    ContenuResume = ""

    if len(listeLangResume)!=0:
        PresenceResumeBoolean = True
        for elt in listeLangResume:
            ContenuResume= ContenuResume + " " + elt.text

    return PresenceResumeBoolean,ContenuResume



def InsertNewResume(reduction, donnees):

    RechercheZone = donnees['zone']
    StopMots = donnees['mots']
    AjoutResumeFr = donnees['AjoutResumeFr']

    reductionencours = CorpusEtude.objects.filter(nom=reduction)
    docsextractencours = DocExtractInitial.objects.filter(CorpusEtudeRef=reductionencours[0])
    for doc in docsextractencours:
        nomfichierencours = doc.DocReferenceRef.TextRef
        addressedocencours = GetAdresseCompletDoc(nomfichierencours)
        DataCoordinatesDocEnCours = DocErudit(addressedocencours, typesegment='resume')
        MotsPageDocEnCours = DocMotPage(addressedocencours, detail=True)
        list_id_mots_resumes = GetListIDMots(DataCoordinatesDocEnCours.obj,
                                                   MotsPageDocEnCours)

        if AjoutResumeFr:
            ResumeFrPresence, ResumeFrContenu = RecupResumeFr(addressedocencours)

        for k, resume in enumerate(list_id_mots_resumes):

            list_intervalles_mots_retirer = GetIntervalleMotsParFenetre(resume)
            # Si une fenêtre graphique ne génère pas un et un seul intervalle
            if len(list_intervalles_mots_retirer) > 1:
                for l,eltagreg in enumerate(list_intervalles_mots_retirer):
                    # cas ajout resumefr uniquement pour le premier segment
                    # sinon provoque des répétitions
                    if k==0 and l==0 and AjoutResumeFr and ResumeFrPresence:
                        NewTransformer = Transformer(DocExtractRef=doc,
                                               type='Resume',
                                               IndexDeb=eltagreg[0] -1,
                                               IndexFin=eltagreg[1],
                                               TextField= ResumeFrContenu.replace("'","''"),
                                               comment="")
                        NewTransformer.save()
                    else :
                        NewTransformer = Transformer(DocExtractRef =doc,
                                                       type='Resume',
                                                       IndexDeb=eltagreg[0] - 1,
                                                       IndexFin=eltagreg[1],
                                                       TextField="",
                                                       comment="")
                        NewTransformer.save()
            # si un seul intervalle
            if len(list_intervalles_mots_retirer) == 1:
                # idem cas ajout resumefr
                if k == 0 and AjoutResumeFr and ResumeFrPresence:
                    NewTransformer = Transformer(DocExtractRef=doc,
                                               type='Resume',
                                               IndexDeb=list_intervalles_mots_retirer[0][0] - 1,
                                               IndexFin=list_intervalles_mots_retirer[0][1],
                                               TextField=ResumeFrContenu.replace("'","''"),
                                               comment="")
                    NewTransformer.save()
                else:
                    NewTransformer = Transformer(DocExtractRef=doc,
                                                   type='Resume',
                                                   IndexDeb=list_intervalles_mots_retirer[0][0] - 1,
                                                   IndexFin=list_intervalles_mots_retirer[0][1],
                                                   TextField="",
                                                   comment="")
                    NewTransformer.save()

            # Ajout de la procédure pour retirer certain mots
            if len(resume) != 0:
                mot1 = resume[0]
                page = DataCoordinatesDocEnCours.obj[k][0]
                nbmots_shift = NbMotAvantPage(MotsPageDocEnCours, page)
                # fin car on cherche dans les x mots (seuil) avant
                fin = mot1 - nbmots_shift -1
                if fin - int(RechercheZone) > 0:
                    deb = fin - int(RechercheZone)
                else:
                    deb = 0
                RechercheMotIn = MotsPageDocEnCours[page][deb:fin]
                for j,motiter in enumerate(RechercheMotIn):
                    for stopmot in StopMots.split("*"):
                        if motiter[0] == stopmot:
                            nbmots_shift = NbMotAvantPage(MotsPageDocEnCours, page)
                            index = nbmots_shift + deb +j +1

                            NewTransformer = Transformer(DocExtractRef =doc,
                                                           type='Resume',
                                                           IndexDeb=index,
                                                           IndexFin=index + 1,
                                                           TextField="",
                                                           comment="stopmot")
                            NewTransformer.save()
