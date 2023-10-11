import os
import pickle

from django.conf import settings
from lxml import etree

from AllApps.PreTraitement.Persee.DelimitCorpus.models import CorpusEtude, DocExtractInitial, Transformer
from AllApps.PreTraitement.Persee.DelimitCorpus.outils.xpath import DocMotPage
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.ExploreFct.ExpCoordGraphSimpleFct import NbMotAvantPage
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.AideTitreFct import GetAdresseCompletDoc


def InsertNewFinMot(reduction, donnees):

    # creer un dico par deux premières lettres
    # accèlère grandement les recherche par la suite
    ResultDicoPickle = settings.DATA_DIR + '/Dico/DicoAllPythonDico'
    # s'il n'exite pas déjà
    if not os.path.isfile(ResultDicoPickle):
        ResultDicoAll = settings.DATA_DIR + '/Dico/DicoFusionAll.txt'
        with open(ResultDicoAll) as f:
            content = f.readlines()
        DicoParDeuxPremieresLettres = {}
        for line in content:
            if len(line[:-1]) >= 4:
                if line[0:2] not in DicoParDeuxPremieresLettres.keys():
                    DicoParDeuxPremieresLettres[line[0:2]] = []
                    DicoParDeuxPremieresLettres[line[0:2]].append(line[:-1])
                else:
                    DicoParDeuxPremieresLettres[line[0:2]].append(line[:-1])

        filename = settings.DATA_DIR + '/Dico/DicoAllPythonDico'
        outfile = open(filename, 'wb')
        pickle.dump(DicoParDeuxPremieresLettres, outfile)
        outfile.close()
    # sinon le chage directement
    else:
        infile = open(ResultDicoPickle, 'rb')
        DicoParDeuxPremieresLettres = pickle.load(infile)
        infile.close()

    # va iterer sur les doc : dejà sur chaque mots !!
    reductionencours = CorpusEtude.objects.filter(nom=reduction)
    docsextractencours = DocExtractInitial.objects.filter(CorpusEtudeRef=reductionencours[0])
    KeyDico = DicoParDeuxPremieresLettres.keys()

    for doc in docsextractencours:
        nomfichierencours = doc.DocReferenceRef.TextRef
        addressedocencours = GetAdresseCompletDoc(nomfichierencours)

        # récupération des notes
        tree = etree.parse(addressedocencours)
        XpathNote = "/tei:TEI/tei:text/tei:body//tei:note[not(@type='biography')]/@xml:id"
        listeXpathNote = tree.xpath(XpathNote,
                                    namespaces={"tei": "http://www.tei-c.org/ns/1.0"})

        if len(listeXpathNote) != 0:
            ListeNoteId = []
            for zone in listeXpathNote:
                ListeNoteId.append(zone.rsplit("_", 1)[0])

            # recupération des id des pages
            XpathPageId = '/tei:TEI/tei:text/tei:body//tei:pb/@xml:id'
            ListeXpathPageId = tree.xpath(XpathPageId,
                                          namespaces={"tei": "http://www.tei-c.org/ns/1.0"})
            ListePageId = []
            for elt1 in ListeXpathPageId:
                ListePageId.append(elt1)

            # faire la correspondance note-page
            pageavecnote = []
            for elt1 in ListeNoteId:
                pageavecnote.append(ListePageId.index(elt1) + 1)

            TousLesMotsParPage = DocMotPage(addressedocencours)

            for page in pageavecnote:
                TousLesMotsDeCettePage = TousLesMotsParPage[page]

                for i,mot in enumerate(TousLesMotsDeCettePage):
                    if len(mot) > 3:
                        if mot[-1].isnumeric():
                            if mot[-2].isnumeric():
                                if (mot[0:2] in KeyDico) and (mot[:-2] in DicoParDeuxPremieresLettres[mot[0:2]]):
                                    NbreMotAvantPage = NbMotAvantPage(TousLesMotsParPage, page)
                                    NewTransformer = Transformer(DocExtractRef=doc,
                                                                   type='FinMot',
                                                                   IndexDeb=NbreMotAvantPage + i ,
                                                                   IndexFin=NbreMotAvantPage + i + 1,
                                                                   TextField=mot[:-2],
                                                                   comment="")
                                    NewTransformer.save()

                            else:
                                if (mot[0:2] in KeyDico) and (mot[:-1] in DicoParDeuxPremieresLettres[mot[0:2]]):
                                    NbreMotAvantPage = NbMotAvantPage(TousLesMotsParPage, page)
                                    NewTransformer = Transformer(DocExtractRef=doc,
                                                                   type='FinMot',
                                                                   IndexDeb=NbreMotAvantPage + i ,
                                                                   IndexFin=NbreMotAvantPage + i + 1,
                                                                   TextField=mot[:-1],
                                                                   comment="")
                                    NewTransformer.save()


