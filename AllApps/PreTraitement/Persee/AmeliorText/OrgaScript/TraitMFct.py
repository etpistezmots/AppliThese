from AllApps.PreTraitement.Persee.DelimitCorpus.models import Transformer, DocExtractInitial, DocReference, CorpusEtude
from ..models import AllExceptRemove, AllExceptAdd, DocRemove



def RemoveEltAllDo(reduction,objetred,listmodif):
    success = []
    echec = []
    malformat = []
    CEconcerne = CorpusEtude.objects.filter(nom=reduction)
    if CEconcerne.exists():
        for elt in listmodif:
            eltsplit = elt.split(",")
            # si c'est un doublet ou un triplet
            if len(eltsplit) == 2 or len(eltsplit) == 3:
                nomfichier = "article_" + eltsplit[0][35:].split("\">")[0] + "_tei.xml"
                docrefconcerne = DocReference.objects.filter(TextRef=nomfichier)
                if docrefconcerne.exists():
                    docextractconcerne = DocExtractInitial.objects.filter(DocReferenceRef=docrefconcerne[0],
                                                                 CorpusEtudeRef=CEconcerne[0])
                    if docextractconcerne.exists():

                        # si c'est un doublet
                        if len(eltsplit) == 2:
                            eltstransfoconcerne = Transformer.objects.filter(DocExtractRef=docextractconcerne[0],
                                                                          type=objetred,
                                                                          IndexDeb=int(eltsplit[1]))
                            if eltstransfoconcerne.exists():
                                for elttransfo in eltstransfoconcerne:
                                    elttransfo.delete()
                                    success.append(elt + "," + str(elttransfo.IndexFin) + "," + elttransfo.TextField.replace(",", " ") + "," + elttransfo.comment)
                                    enregistrement = AllExceptRemove(CorpusEtudeRef = CEconcerne[0],
                                                                     DocExtractRef = docextractconcerne[0],
                                                                    type=objetred,
                                                                    IndexDeb = elttransfo.IndexDeb,
                                                                    IndexFin=elttransfo.IndexFin,
                                                                    TextField=elttransfo.TextField,
                                                                    comment =elttransfo.comment)
                                    enregistrement.save()

                            else:
                                echec.append(elt + ", raison : l'elt de nettoyage n'existe pas")

                         # si c'est un triplet
                        if len(eltsplit) == 3:
                            eltstransfoconcerne = Transformer.objects.filter(DocExtractRef = docextractconcerne[0],
                                                                          type=objetred,
                                                                          IndexDeb=int(eltsplit[1]),
                                                                          IndexFin=int(eltsplit[2]))
                            if eltstransfoconcerne.exists():
                                for elttransfo in eltstransfoconcerne:
                                    elttransfo.delete()
                                    success.append(elt + "," + elttransfo.TextField.replace(",", " ") + "," + elttransfo.comment)
                                    enregistrement = AllExceptRemove(CorpusEtudeRef = CEconcerne[0],
                                                                     DocExtractRef= docextractconcerne[0],
                                                                    type=objetred,
                                                                    IndexDeb=elttransfo.IndexDeb,
                                                                    IndexFin=elttransfo.IndexFin,
                                                                    TextField=elttransfo.TextField,
                                                                    comment=elttransfo.comment)
                                    enregistrement.save()
                            else:
                                echec.append(elt + ", raison : l'elt de nettoyage n'existe pas")


                    else:
                        echec.append(elt + ", raison : le doc net n'existe pas")
                else:
                    echec.append(elt + ", raison : le doc brut n'existe pas")
            # si ce n'est ni un doublet, ni un triplet
            else:
                malformat.append(elt)
    else:
        echec.append(listmodif)

    print(success)
    return success,echec,malformat




def AddEltAllDo(reduction,objetred,listmodif):
    success = []
    echec = []
    malformat = []
    existedeja = []
    CEconcerne = CorpusEtude.objects.filter(nom=reduction)
    if CEconcerne.exists():
        for elt in listmodif:
            eltsplit = elt.split(",")
            # si c'est un triplet, quadruplet ou cinqelt
            if len(eltsplit) == 3 or len(eltsplit) == 4 or len(eltsplit) == 5:
                nomfichier = "article_" + eltsplit[0][35:].split("\">")[0] + "_tei.xml"
                docrefconcerne = DocReference.objects.filter(TextRef=nomfichier)
                if docrefconcerne.exists():
                    docextractconcerne = DocExtractInitial.objects.filter(DocReferenceRef=docrefconcerne[0],
                                                                 CorpusEtudeRef=CEconcerne[0])
                    if docextractconcerne.exists():
                        if len(eltsplit) == 3:
                            eltstransfoconcerne = Transformer.objects.filter(DocExtractRef=docextractconcerne[0],
                                                                          type=objetred,
                                                                          IndexDeb=int(eltsplit[1]),
                                                                          IndexFin=int(eltsplit[2]))
                            if eltstransfoconcerne.exists():
                                existedeja.append(elt)
                            else:
                                eltcomplet = Transformer(DocExtractRef=docextractconcerne[0],
                                                            type=objetred,
                                                            IndexDeb=int(eltsplit[1]),
                                                            IndexFin=int(eltsplit[2]),
                                                          TextField="",
                                                          comment="")
                                try:
                                    eltcomplet.save()
                                except:
                                    echec.append(elt)
                                    continue

                                success.append(elt)
                                enregistrement = AllExceptAdd(CorpusEtudeRef=CEconcerne[0],
                                                              DocExtractRef=docextractconcerne[0],
                                                            type=objetred,
                                                            IndexDeb=int(eltsplit[1]),
                                                            IndexFin=int(eltsplit[2]),
                                                            TextField="",
                                                            comment="")
                                enregistrement.save()


                        if len(eltsplit) == 4:
                            eltstransfoconcerne = Transformer.objects.filter(DocExtractRef=docextractconcerne[0],
                                                                          type=objetred,
                                                                          IndexDeb=int(eltsplit[1]),
                                                                          IndexFin=int(eltsplit[2]),
                                                                          TextField=eltsplit[3],)
                            if eltstransfoconcerne.exists():
                                existedeja.append(elt)
                            else:
                                eltcomplet = Transformer(DocExtractRef=docextractconcerne[0],
                                                          type=objetred,
                                                          IndexDeb=int(eltsplit[1]),
                                                          IndexFin=int(eltsplit[2]),
                                                          TextField=eltsplit[3],
                                                          comment="")
                                try:
                                    eltcomplet.save()
                                except:
                                    echec.append(elt)
                                    continue

                                success.append(elt)
                                enregistrement = AllExceptAdd(CorpusEtudeRef=CEconcerne[0],
                                                              DocExtractRef=docextractconcerne[0],
                                                            type=objetred,
                                                            IndexDeb=int(eltsplit[1]),
                                                            IndexFin=int(eltsplit[2]),
                                                            TextField=eltsplit[3],
                                                            comment="")
                                enregistrement.save()

                        if len(eltsplit) == 5:
                            eltstransfoconcerne = Transformer.objects.filter(DocExtractRef=docextractconcerne[0],
                                                                          type=objetred,
                                                                          IndexDeb=int(eltsplit[1]),
                                                                          IndexFin=int(eltsplit[2]),
                                                                          TextField=eltsplit[3],
                                                                          comment=eltsplit[4])
                            if eltstransfoconcerne.exists():
                                existedeja.append(elt)
                            else:
                                eltcomplet = Transformer(DocExtractRef=docextractconcerne[0],
                                                          type=objetred,
                                                          IndexDeb=int(eltsplit[1]),
                                                          IndexFin=int(eltsplit[2]),
                                                          TextField=eltsplit[3],
                                                          comment=eltsplit[4])
                                try:
                                    eltcomplet.save()
                                except:
                                    echec.append(elt)
                                    continue

                                success.append(elt)
                                enregistrement = AllExceptAdd(CorpusEtudeRef=CEconcerne[0],
                                                              DocExtractRef=docextractconcerne[0],
                                                            type=objetred,
                                                            IndexDeb=int(eltsplit[1]),
                                                            IndexFin=int(eltsplit[2]),
                                                            TextField=eltsplit[3],
                                                            comment=eltsplit[4])
                                enregistrement.save()




                    else:
                        echec.append(elt + ", raison : le doc net n'existe pas")
                else:
                    echec.append(elt + ", raison : le doc brut n'existe pas")

    else:
        echec.append(listmodif)

    return success, echec, malformat, existedeja


def RemoveDocDo(reduction,objetred,listmodif):
    success = []
    echec = []
    malformat = []
    existedeja = []
    CEconcerne = CorpusEtude.objects.filter(nom=reduction)
    if CEconcerne.exists():
        for elt in listmodif:
            eltsplit = elt.split(",")

             # cas commentaire
            if len(eltsplit) == 2 :
                nomfichier = "article_" + eltsplit[0][35:].split("\">")[0] + "_tei.xml"
                docrefconcerne = DocReference.objects.filter(TextRef=nomfichier)
                if docrefconcerne.exists():
                    docextractconcerne = DocExtractInitial.objects.filter(DocReferenceRef=docrefconcerne[0],
                                                                 CorpusEtudeRef=CEconcerne[0])
                    if docextractconcerne.exists():

                        # test si existe déjà
                        testexist = DocRemove.objects.filter(CorpusEtudeRef=CEconcerne[0],
                                                             type=objetred,
                                                             DocExtractRef=docextractconcerne[0])

                        if testexist.exists():
                            existedeja.append(elt)
                        else:
                            enregistrement = DocRemove(CorpusEtudeRef=CEconcerne[0],
                                                       type=objetred,
                                                       DocExtractRef=docextractconcerne[0],
                                                       comment=eltsplit[1])
                            enregistrement.save()
                            success.append(elt)

                    else:
                        echec.append(elt + ", raison : le doc net n'existe pas")
                else:
                    echec.append(elt + ", raison : le doc brut n'existe pas")

            # cas sans commentaire
            elif len(eltsplit) == 1 :

                nomfichier = "article_" + eltsplit[0][35:].split("\">")[0] + "_tei.xml"
                docrefconcerne = DocReference.objects.filter(TextRef=nomfichier)
                if docrefconcerne.exists():
                    docextractconcerne = DocExtractInitial.objects.filter(DocReferenceRef=docrefconcerne[0],
                                                                 CorpusEtudeRef=CEconcerne[0])
                    if docextractconcerne.exists():

                        # test si existe déjà
                        testexist = DocRemove.objects.filter(CorpusEtudeRef=CEconcerne[0],
                                                             type=objetred,
                                                             DocExtractRef=docextractconcerne[0])

                        if testexist.exists():
                            existedeja.append(elt)
                        else:
                            enregistrement = DocRemove(CorpusEtudeRef=CEconcerne[0],
                                                       type=objetred,
                                                       DocExtractRef=docextractconcerne[0],
                                                       comment="")
                            enregistrement.save()
                            success.append(elt)

                    else:
                        echec.append(elt + ", raison : le doc net n'existe pas")
                else:
                    echec.append(elt + ", raison : le doc brut n'existe pas")

            # cas plus que doublet
            else:
                malformat.append(elt)

    else:
        echec.append(listmodif)

    return success, echec, malformat, existedeja