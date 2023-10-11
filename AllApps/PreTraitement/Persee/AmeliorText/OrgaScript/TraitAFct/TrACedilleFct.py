from django.conf import settings
from AllApps.PreTraitement.Persee.DelimitCorpus.models import  CorpusEtude, DocExtractInitial, Transformer
from AllApps.PreTraitement.Persee.DelimitCorpus.outils.xpath import DocMot
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.AideTitreFct import GetAdresseCompletDoc


def InsertNewCedille(reduction, donnees):

    litigecedille = donnees['litigecedille']

    reductionencours = CorpusEtude.objects.filter(nom=reduction)
    docsextractencours = DocExtractInitial.objects.filter(CorpusEtudeRef=reductionencours[0])

    # creation dico prefixe et suffixe cedille
    ResultCedille = settings.DATA_DIR + '/Dico/DicoCedille.txt'
    EnsTot = []
    EnsDeb = []
    EnsFin = []
    with open(ResultCedille) as f:
        for line in f:
            EnsTot.append(line[:-1])
            deb = line[:-1].split("ç",1)[0]
            fin = line[:-1].split("ç",1)[1]
            if deb !="" and deb not in EnsDeb:
                EnsDeb.append(deb)
            if fin not in EnsFin:
                EnsFin.append(fin)

    if litigecedille:
        ResultCedilleLitigieux = settings.DATA_DIR + '/Dico/DicoCedilleAvtApres.txt'
        EnsLitigieux = []
        with open(ResultCedilleLitigieux) as f:
            for line in f:
                if line[-2]=="a":
                    EnsLitigieux.append(line[:-1])

    for doc in docsextractencours:
        nomfichierencours = doc.DocReferenceRef.TextRef
        addressedocencours = GetAdresseCompletDoc(nomfichierencours)
        TousLesMotsDocs = DocMot(addressedocencours)
        if len(TousLesMotsDocs) != 0:
            MarqueurPossible = False
            motavant = ""
            for i,mot in enumerate(TousLesMotsDocs):
                if MarqueurPossible:
                    if mot in EnsFin:
                        motremplace = motavant + "ç" + mot
                        if litigecedille:
                            if (motremplace in EnsTot) and (motremplace not in EnsLitigieux):
                                NewTransformer = Transformer(DocExtractRef=doc,
                                                       type='Cedille',
                                                       IndexDeb=i-1,
                                                       IndexFin=i+1,
                                                       TextField=motremplace.replace("'", "''"),
                                                       comment="")
                                NewTransformer.save()
                        else:
                            if motremplace in EnsTot:
                                NewTransformer = Transformer(DocExtractRef=doc,
                                                               type='Cedille',
                                                               IndexDeb=i - 1,
                                                               IndexFin=i + 1,
                                                               TextField=motremplace.replace("'", "''"),
                                                               comment="")
                                NewTransformer.save()

                if mot in EnsDeb:
                    MarqueurPossible = True
                    motavant = mot
                else:
                    MarqueurPossible = False

