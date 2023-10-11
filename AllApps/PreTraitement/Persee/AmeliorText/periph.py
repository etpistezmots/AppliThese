import os, shutil
from django.conf import settings

from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.ExploreFct.ExpAnnexeFct import \
    AnnexeDivPlusieursPagesDo, ExploreEruditDonneesDo
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.ExploreFct.ExpBasDePageFct import \
    AfficheBasDePageBrutDo, AfficheBasDePageOrderDo, AfficheBasDePageOrderNiNoteNiFigDo, AfficheBasDePageTextualCombiDo
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.ExploreFct.ExpBiblioFct import PlusieursBibliosDo, \
    AfterLastBiblioDo, BiblioInCRDo
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.ExploreFct.ExpCedilleFct import \
    VerifAvantApresCedilleExist
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.ExploreFct.ExpCoordGraphSimpleFct import \
    AfficheCoordGraphDiscontinuMaxDo
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.ExploreFct.ExpFigureFct import \
    AfficheTitreFigureDetectDoFound, AfficheTitreFigureDetectDoNotFound, TitreFigureSlashDo, AfficheTitrePlusDiscontinuDo, \
    MotsPlusFrequentsTitreFigureDo
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.ExploreFct.ExpFinDocFct import \
    AfficheLigneCenterLastPageDo, PresenceDebutLigneDo
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.ExploreFct.ExpHtDePageFct import \
    AfficheHtDePageBrutDo, AfficheHtDePageOrderDo
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.ExploreFct.ExpMotCleFct import AfficheMotClesFrenchDo
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.ExploreFct.ExpNoteFct import RechercheNoteBioDo, \
    NoteBioExistDo
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.ExploreFct.ExpResumeFct import AfficheResumesFrenchDo
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.ExploreFct.ExpTitreFct import AfficheTitreDo, \
    AfficheTitreSlashDo, AfficheTitreFoundDo


from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.TraitAFct.TrAAnnexeFct import InsertNewAnnexe
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.TraitAFct.TrABasDePageFct import InsertNewBasDePage
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.TraitAFct.TrABiblioFct import InsertNewBiblio
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.TraitAFct.TrACedilleFct import InsertNewCedille
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.TraitAFct.TrAFigureFct import InsertNewFigure
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.TraitAFct.TrAFinDocFct import InsertNewFinDoc
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.TraitAFct.TrAFinLigneFct import InsertNewFinLigne
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.TraitAFct.TrAFinMotFct import InsertNewFinMot
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.TraitAFct.TrAHtDePageFct import InsertNewHtDePage
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.TraitAFct.TrAMotCleFct import InsertNewMotCle
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.TraitAFct.TrANoteFct import InsertNewNote
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.TraitAFct.TrAResumeFct import InsertNewResume
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.TraitAFct.TrATitre123Fct import InsertNewTitre123
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.TraitAFct.TrATitreFct import InsertNewTitre

from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.ExploreFct.ExpResumeFct import AfficheResumesFrenchDo, \
    PresenceMotAvantObjetDo

from lxml import etree
from AllApps.PreTraitement.Persee.DelimitCorpus.outils.xpath import DocMot

from .forms import TitreTransformForm, ResumeTransformForm, \
    MotCleTransformForm, HtDePageTransformForm, \
    BasDePageTransformForm, NoteTransformForm, \
    BiblioTransformForm, AppendixTransformForm, \
    FigureTransformForm, SousTitreTransformForm, \
    FinDocTransformForm, CedilleTransformForm, FinMotTransformForm, \
    FinLigneTransformForm

from AllApps.PreTraitement.Persee.DelimitCorpus.views import SelectReducFctUser
from AllApps.PreTraitement.Persee.DelimitCorpus.models import CorpusEtude, Revue, DocExtractInitial, Transformer, \
    SyntheseTransform, DocTransforme
from .OrgaScript.AideTitreFct import GetAdresseCompletDoc, OnPositionSequence
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.TraitAFct.TrACoordGraphSimpleFct import SupprCoordGraph

from .models import AllExceptRemove, AllExceptAdd, DocRemove, \
    TitreTransform, ResumeTransform, MotCleTransform, HtDePageTransform, \
    BasDePageTransform, NoteTransform, BiblioTransform, AppendixTransform, \
    FigureTransform, SousTitreTransform, FinDocTransform, CedilleTransform, \
    FinMotTransform, FinLigneTransform

from collections import OrderedDict


def DicModelFormRefInsert(objet, detail):
    DicoModel = {"Titre": {"modele":TitreTransform,
                             "formulaire":TitreTransformForm,
                             "numero":"b",
                             "RenduNormal":"titre",
                             "RenduPluriel": "titres",
                             "FctTrait":InsertNewTitre},
                 "Resume": {"modele":ResumeTransform,
                             "formulaire":ResumeTransformForm,
                             "numero":"c",
                             "RenduNormal":"résumé",
                              "RenduPluriel": "résumés",
                             "FctTrait":InsertNewResume},
                 "MotCle": {"modele": MotCleTransform,
                              "formulaire": MotCleTransformForm,
                              "numero": "d",
                              "RenduNormal": "mot-clé",
                                 "RenduPluriel": "mots-clés",
                                 "FctTrait": InsertNewMotCle},
                 "HautDePage": {"modele": HtDePageTransform,
                                 "formulaire": HtDePageTransformForm,
                                 "numero": "e",
                                 "RenduNormal": "haut de page",
                                  "RenduPluriel": "hauts de page",
                                 "FctTrait": InsertNewHtDePage},
                 "BasDePage": {"modele": BasDePageTransform,
                                  "formulaire": BasDePageTransformForm,
                                  "numero": "f",
                                  "RenduNormal": "bas de page",
                                    "RenduPluriel": "bas de page",
                                  "FctTrait": InsertNewBasDePage},
                 "Note": {"modele": NoteTransform,
                            "formulaire": NoteTransformForm,
                            "numero": "g",
                            "RenduNormal": "note",
                            "RenduPluriel": "notes",
                            "FctTrait": InsertNewNote},
                 "Biblio": {"modele": BiblioTransform,
                                "formulaire": BiblioTransformForm,
                                "numero": "h",
                                "RenduNormal": "bibliographie",
                              "RenduPluriel": "bibliographies",
                                "FctTrait": InsertNewBiblio},
                 "Annexe": {"modele": AppendixTransform,
                              "formulaire": AppendixTransformForm,
                              "numero": "i",
                              "RenduNormal": "annexe",
                              "RenduPluriel":"annexes",
                              "FctTrait": InsertNewAnnexe},
                 "Titre123": {"modele": SousTitreTransform,
                              "formulaire": SousTitreTransformForm,
                              "numero": "j",
                              "RenduNormal": "titre secondaire",
                              "RenduPluriel": "titres secondaires",
                              "FctTrait": InsertNewTitre123},
                 "Figure": {"modele": FigureTransform,
                              "formulaire": FigureTransformForm,
                              "numero": "k",
                              "RenduNormal": "figure",
                              "RenduPluriel": "figures",
                              "FctTrait": InsertNewFigure},
                 "FinDoc": {"modele": FinDocTransform,
                                        "formulaire": FinDocTransformForm,
                                        "numero": "l",
                                        "RenduNormal": "fin de document",
                                        "RenduPluriel": "fins de document",
                                        "FctTrait": InsertNewFinDoc},
                 "Cedille": {"modele": CedilleTransform,
                                "formulaire": CedilleTransformForm,
                                "numero": "b",
                                "RenduNormal": "cédille",
                                "RenduPluriel": "cédilles",
                                "FctTrait": InsertNewCedille},
                 "FinMot": {"modele": FinMotTransform,
                            "formulaire": FinMotTransformForm,
                                "numero": "c",
                                "RenduNormal": "fin de mot",
                                "RenduPluriel": "fins de mots",
                                   "FctTrait": InsertNewFinMot},
                 "FinLigne": {"modele": FinLigneTransform,
                                    "formulaire": FinLigneTransformForm,
                                    "numero": "d",
                                    "RenduNormal": "fin de ligne",
                                    "RenduPluriel": "fins de lignes",
                                     "FctTrait": InsertNewFinLigne}
                 }
    result = DicoModel[objet][detail]
    return result


def DicFctExplo(objet):
    DicoModel = {"Titre": OrderedDict([("Afficher Titres",'AfficheTitreSimple'),
                                      ("Afficher Titres Slash",'AfficheTitreSlash'),
                                      ("Afficher Titres trouvés",'AfficheTitreFound'),
                                      ("Afficher Titres trouvés et corrigés", 'AfficheTitreTrait')]),
                 "Resume":OrderedDict([("Afficher Résumés en français",'AfficheResumesFrench'),
                                      ("Rechercher mot spécifique avant résumé",'PresenceMotAvantObjetInterface')]),
                 "MotCle":OrderedDict([("Afficher Mots-Clés en français",'AfficheMotClesFrench'),
                                      ("Rechercher mot spécifique avant mots-clés",'PresenceMotAvantObjetInterface')]),
                 "HautDePage":OrderedDict([("Afficher tous les hauts de page",'AfficheHtDePageBrut'),
                                      ("Afficher Haut de page sup 400 ordonné",'AfficheHtDePageOrder')]),
                 "BasDePage": OrderedDict([("Afficher tous les bas de page",'AfficheBasDePageBrut'),
                                            ("Afficher bas de page ordonnés",'AfficheBasDePageOrder'),
                                            ("Idem précédent sans les figures et les notes",'AfficheBasDePageOrderNiNoteNiFig'),
                                           ("Afficher bas de page ordonée avec combinaison textuelle",'AfficheBasDePageTextualCombi')]),
                 "Note": OrderedDict([("Afficher notes biographiques existantes",'NoteBioExist'),
                                      ("Rechercher notes biographiques non référencées",'RechercheNoteBio'),
                                      ("Afficher notes Fenêtre graphique discontinue",'AfficheNoteDiscontinu')]),
                 "Biblio": OrderedDict([("Afficher partie après la dernière bibliographie sauf résumés, mots-clés, notes biographiques, figures",'AfficheApresBiblio'),
                                      ("Afficher articles avec plusieurs bibliographies",'PlusieursBiblios'),
                                      ("Rechercher mots spécifiques avant bibliographie",'PresenceMotAvantObjetInterface'),
                                      ("Afficher compte-rendus avec bibliographie",'BiblioInCR'),]),
                 "Annexe": OrderedDict([("Afficher saut de page dans les annexes",'AnnexeDivPlusieursPages'),
                                        ("Rechercher mot spécifique avant annexe",'PresenceMotAvantObjetInterface')]),
                 "Titre123": OrderedDict([]),
                 "Figure": OrderedDict([("Afficher annonces dans les titres des figures",'Mots0PlusFrequentsTitreFigure'),
                                        ("Afficher titres de figures avec un slash", 'TitreFigureAvecSlash'),
                                        ("Afficher titres détectés dans cadre Persée de la figure", 'ExplorFigureTitreIn'),
                                        ("Afficher titres non détectés dans cadre Persée de la figure",
                                         'ExplorFigureTitreNonDectect'),
                                        ("Rechercher titre de manière plus discontinue",'ExplorFigureTitrePlusDiscontinu')]),
                 "FinDoc": OrderedDict(
                     [("Afficher dernière page contenu centré", 'LastPageCenter'),
                      ("Afficher Début de ligne avec Manuscrit", 'DetectDebutLigne')]),
                 "Cedille": OrderedDict(
                     [("Cedille", 'AfficheMotCedilleAvtApres')]),
                 "FinMot": OrderedDict([]),
                 "FinLigne": OrderedDict([])
                 }
    result = DicoModel[objet]
    return result


def RecupFctAttr(fct):
    DicoModel = {"AfficheTitreSimple": {"ref":"ET1",
                                        "namesave":"TitresAll",
                                        "fctdo": AfficheTitreDo,
                                        "red":"no",
                                        "objet":"Titre"},
                "AfficheTitreSlash": {"ref":"ET2",
                                        "namesave":"TitresSlash",
                                        "fctdo": AfficheTitreSlashDo,
                                        "red":"no",
                                        "objet":"Titre"},
                "AfficheTitreFound": {"ref":"ET3",
                                        "namesave":"TitresFound",
                                        "fctdo": AfficheTitreFoundDo,
                                        "red":"simple",
                                        "objet":"Titre"},
                "AfficheResumesFrench": {"ref": "ER1",
                                       "namesave": "ResumeFrench",
                                       "fctdo": AfficheResumesFrenchDo,
                                       "red": "no",
                                       "objet": "Resume"},
                "AfficheMotClesFrench": {"ref": "EM1",
                                          "namesave": "MotCleFrench",
                                          "fctdo": AfficheMotClesFrenchDo,
                                          "red": "no",
                                          "objet": "MotCle"},
                "AfficheHtDePageBrut": {"ref": "EH1",
                                          "namesave": "HtDePageBrut",
                                          "fctdo": AfficheHtDePageBrutDo,
                                          "red": "simple",
                                          "objet": "HautDePage"},
                "AfficheHtDePageOrder": {"ref": "EH2",
                                         "namesave": "HtDePageOrder",
                                         "fctdo": AfficheHtDePageOrderDo,
                                         "red": "list",
                                         "objet": "HautDePage"},
                "AfficheBasDePageBrut": {"ref": "EB1",
                                          "namesave": "BasDePageBrut",
                                          "fctdo": AfficheBasDePageBrutDo,
                                          "red": "simple",
                                          "objet": "BasDePage"},
                "AfficheBasDePageOrder": {"ref": "EB2",
                                          "namesave": "BasDePageOrder",
                                          "fctdo": AfficheBasDePageOrderDo,
                                          "red": "list",
                                          "objet": "BasDePage"},
                "AfficheBasDePageOrderNiNoteNiFig": {"ref": "EB3",
                                           "namesave": "BasDePageOrderNiNoteNiFig",
                                           "fctdo": AfficheBasDePageOrderNiNoteNiFigDo,
                                           "red": "list",
                                           "objet": "BasDePage"},
                "AfficheBasDePageTextualCombi": {"ref": "EB4",
                                           "namesave": "BasDePageTextualCombi",
                                           "fctdo": AfficheBasDePageTextualCombiDo,
                                           "red": "simple",
                                           "objet": "BasDePage"},
                "NoteBioExist": {"ref": "EN1",
                                 "namesave": "NoteBioExist",
                                 "fctdo": NoteBioExistDo,
                                 "red": "no",
                                 "objet": "Note"},
                "RechercheNoteBio": {"ref": "EN2",
                                  "namesave": "NoteBioSuspiscion",
                                  "fctdo": RechercheNoteBioDo,
                                  "red": "no",
                                  "objet": "Note"},
                "AfficheApresBiblio": {"ref": "EBl1",
                                      "namesave": "ApresBiblio",
                                      "fctdo": AfterLastBiblioDo,
                                      "red": "no",
                                      "objet": "Biblio"},
                "PlusieursBiblios": {"ref": "EBl2",
                                        "namesave": "PlusieursBiblios",
                                        "fctdo": PlusieursBibliosDo,
                                        "red": "no",
                                        "objet": "Biblio"},
                "BiblioInCR": {"ref": "EBl3",
                               "namesave": "BiblioInCR",
                               "fctdo": BiblioInCRDo,
                               "red": "no",
                               "objet": "Biblio"},
                "AnnexeDivPlusieursPages": {"ref": "EA1",
                                "namesave": "DivMultiAnnexe",
                                "fctdo": AnnexeDivPlusieursPagesDo,
                                "red": "no",
                                "objet": "Annexe"},
                "ExploreEruditDonnees": {"ref": "EA2",
                                             "namesave": "ExploreEruditDonnees",
                                             "fctdo": ExploreEruditDonneesDo,
                                             "red": "no",
                                             "objet": "Annexe"},
                "Mots0PlusFrequentsTitreFigure": {"ref": "EF1",
                                             "namesave": "FigureMotsFrequentsTitres",
                                             "fctdo": MotsPlusFrequentsTitreFigureDo,
                                             "red": "no",
                                             "objet": "Figure"},
                "TitreFigureAvecSlash": {"ref": "EF2",
                                         "namesave": "TitresFiguresAvecSlash",
                                         "fctdo": TitreFigureSlashDo,
                                         "red": "no",
                                         "objet": "Figure"},
                "ExplorFigureTitreIn": {"ref": "EF3",
                                          "namesave": "FigureTitreDetect",
                                          "fctdo": AfficheTitreFigureDetectDoFound,
                                          "red": "no",
                                          "objet": "Figure"},
                "ExplorFigureTitreNonDectect": {"ref": "EF4",
                                         "namesave": "FigureTitreNonDetect",
                                         "fctdo": AfficheTitreFigureDetectDoNotFound,
                                         "red": "no",
                                         "objet": "Figure"},
                "ExplorFigureTitrePlusDiscontinu": {"ref": "EF5",
                                                 "namesave": "FigureTitrePlusDiscontinu",
                                                 "fctdo": AfficheTitrePlusDiscontinuDo,
                                                 "red": "simple",
                                                 "objet": "Figure"}
                 }
    result = DicoModel[fct]
    return result

def TestRef(ref):
    error = False
    listref = ["ET1","ET2","ET3","ER1","EM1","EH1","EH2","EB1","EB2","EB3","EB4","EN1","EN2","EBl1","EBl2","EBl3",
               "EA1","EA2","EF1","EF2","EF3","EF4","EF5"]
    if ref not in listref:
        error = True
    return error


def RecupNameFct(ref):
    DicoModel = {"ET1":"AfficheTitreSimple",
                 "ET2":"AfficheTitreSlash",
                 "ET3":"AfficheTitreFound",
                 "ER1":"AfficheResumesFrench",
                 "EM1":"AfficheMotClesFrench",
                 "EH1":"AfficheHtDePageBrut",
                 "EH2":"AfficheHtDePageOrder",
                 "EB1":"AfficheBasDePageBrut",
                 "EB2":"AfficheBasDePageOrder",
                 "EB3":"AfficheBasDePageOrderNiNoteNiFig",
                 "EB4":"AfficheBasDePageTextualCombi",
                 "EN1": "NoteBioExist",
                 "EN2": "RechercheNoteBio",
                 "EBl1": "AfficheApresBiblio",
                 "EBl2": "PlusieursBiblios",
                 "EBl3": "BiblioInCR",
                 "EA1": "AnnexeDivPlusieursPages",
                 "EA2": "ExploreEruditDonnees",
                 "EF1": "Mots0PlusFrequentsTitreFigure",
                 "EF2": "TitreFigureAvecSlash",
                 "EF3": "ExplorFigureTitreIn",
                 "EF4": "ExplorFigureTitreNonDectect",
                 "EF5": "ExplorFigureTitrePlusDiscontinu"
                 }
    result = DicoModel[ref]
    return result




def PrepaExplorHome(request,objet):
    PartieDoc = ["Titre", "Resume", "MotCle", "HautDePage", "BasDePage", "Note", "Figure", "Titre123", "Biblio",
                 "Annexe", "FinDoc"]
    PartieMot = ["Cedille", "FinMot", "FinLigne"]
    reductionsall = CorpusEtude.objects.all()
    reductionsselect = SelectReducFctUser(request, reductionsall)
    # dictionnaires des fonctions disponibles pour chaque objet : Titre, Resumr,...
    DicoFctSpe = DicFctExplo(objet)
    fctselect = DicoFctSpe.keys()
    revueselect = ["Annales", "Espace"]
    RenduPluriel = DicModelFormRefInsert(objet, "RenduPluriel").capitalize()
    Numero = DicModelFormRefInsert(objet, "numero")
    MaqueurPartieDoc = False
    if objet in PartieDoc:
        MaqueurPartieDoc = True
    MaqueurPartieMot = False
    if objet in PartieMot:
        MaqueurPartieMot = True
    return reductionsselect, fctselect, revueselect, Numero, RenduPluriel, MaqueurPartieDoc,MaqueurPartieMot

def TraitExplorHome(request, objet):
    reduction = request.POST.get('red')
    fct = request.POST.get('fct')
    revue = request.POST.get('revue')
    error = False
    ref = ""

    reductionM = CorpusEtude.objects.filter(nom=reduction)
    if not(reductionM.exists()):
        error = True
    else:
        ReductionAll = CorpusEtude.objects.all()
        reductionsselect = SelectReducFctUser(request, ReductionAll)
        if not(reductionM[0] in reductionsselect):
            error = True

    RevueM = Revue.objects.filter(nom=revue)
    revuered = ""
    if RevueM.exists():
        revuered = RevueM[0].nompersee
    else:
        error = True

    DicoFctSpe = DicFctExplo(objet)
    fctselect = DicoFctSpe.keys()
    fonction = ""
    agreg = ""
    if fct in fctselect:
        fonction = DicFctExplo(objet)[fct]
        if fonction != "AfficheTitreTrait" and fonction != "PresenceMotAvantObjetInterface"\
                and fonction != "LastPageCenter" and fonction != "DetectDebutLigne" and fonction != "AfficheNoteDiscontinu" and fonction != "AfficheMotCedilleAvtApres":
            ref = RecupFctAttr(fonction)["ref"]
            fonction = "FontionGeneralExplor"
        agreg = "AmeliorText:" + fonction
    else:
        error = True

    return error, reduction, revuered, fonction, agreg, ref

def RechercheSeqDansFichierDo(donnees):
    error = False
    MarqueurDocExist = False
    result = ""
    test = CorpusEtude.objects.filter(nom=donnees["corpus"])
    if test.exists():
        reductionencours = test[0]
        docsextractencours = DocExtractInitial.objects.filter(CorpusEtudeRef=reductionencours)

        for doc in docsextractencours:

            testdoc = doc.DocReferenceRef.TextRef

            if testdoc == donnees["article"]:
                MarqueurDocExist = True
                if donnees["typerecherche"] == "txtbrut":
                    sequence = donnees["sequence"].split(" ")
                    result = OnPositionSequence(donnees["article"], sequence, "brut")
                if donnees["typerecherche"] == "txtxml":
                    sequence = '<data>' + donnees["sequence"] + '</data>'
                    xml_root = etree.fromstring(sequence)
                    listeword = xml_root.xpath("/data/word")
                    SequenceXML = []
                    for elt in listeword:
                        SequenceXML.append((elt.text, elt.attrib['left'], elt.attrib['top'], elt.attrib['right'],
                                            elt.attrib['bottom']))
                    print(SequenceXML)
                    print(donnees["article"])
                    result = OnPositionSequence(donnees["article"], SequenceXML, "xml")
                break
    else:
        error = True

    return error,MarqueurDocExist,result

def PrepaPresenceMotAvantObjetInterface(request, reduction, revue, objet):
    TestPresenceResult = False
    ContenuResult = ""
    PossibleChange = False
    SeuilEnCours = 0
    error = False
    ObjetPossible = ["Resume","MotCle","Biblio","Annexe"]
    if objet not in ObjetPossible:
        error = True

    # si utilisateur est connecté
    ReducEnCours = CorpusEtude.objects.get(nom=reduction)
    if request.user.id is not None:
        # si c'est un super utilisateur ou s'il a les droit sur cette réduction
        if request.user.is_superuser or (str(request.user.id) in ReducEnCours.user_restrict.split(",")):
            PossibleChange = True

    FichierResult1 = settings.RESULT_PRETRAIT_DIR + "/AmeliorText/" \
                     + reduction + "/" \
                     + reduction + revue + objet + "Avt.txt"
    FichierResult2 = settings.RESULT_PRETRAIT_DIR + "/AmeliorText/" \
                     + reduction + "/" \
                     + reduction + revue + objet + "AvtNbreMotsAvt.txt"

    if os.path.isfile(FichierResult1) and os.path.isfile(FichierResult2):
        TestPresenceResult = True
        with open(FichierResult1, "r") as f:
            ContenuResult = f.read()
        with open(FichierResult2, 'r') as f:
            content = f.readlines()
            SeuilEnCours = content[0]

    return error, PossibleChange, TestPresenceResult, ContenuResult, SeuilEnCours

def PresenceMotAvantObjetInterfaceTrait(request, reduction, revue, objet, mots, ponctuations):

    seuil = request.POST.get('seuil')
    TestPresenceResult = False
    ContenuResult = ""
    SeuilEnCours = 0
    PossibleChange = False

    # si utilisateur est connecté
    ReducEnCours = CorpusEtude.objects.get(nom=reduction)
    if request.user.id is not None:
        # si c'est un super utilisateur ou s'il a les droit sur cette réduction
        if request.user.is_superuser or (str(request.user.id) in ReducEnCours.user_restrict.split(",")):
            PossibleChange = True

    FichierResult1 = settings.RESULT_PRETRAIT_DIR + "/AmeliorText/" \
                     + reduction + "/" \
                     + reduction + revue + objet + "Avt.txt"
    FichierResult2 = settings.RESULT_PRETRAIT_DIR + "/AmeliorText/" \
                     + reduction + "/" \
                     + reduction + revue + objet + "AvtNbreMotsAvt.txt"

    if PossibleChange:

        PresenceMotAvantObjetDo(FichierResult1, reduction, mots, ponctuations, seuil, revue, objet)

        with open(FichierResult1, "r") as f:
            ContenuResult = f.read()
        with open(FichierResult2, "r") as f:
            content = f.readlines()
            SeuilEnCours = content[0]

        TestPresenceResult = False

    else:
        if os.path.isfile(FichierResult1) and os.path.isfile(FichierResult2):
            TestPresenceResult = True
            with open(FichierResult1, "r") as f:
                ContenuResult = f.read()
            with open(FichierResult2, 'r') as f:
                content = f.readlines()
                SeuilEnCours = content[0]


    return PossibleChange, TestPresenceResult, ContenuResult, SeuilEnCours



def PrepaPresenceMotAvantObjetResult(reduction, revue, number, objet):
    FichierResult1 = settings.RESULT_PRETRAIT_DIR + "/AmeliorText/" \
                     + reduction + "/" + objet + "Result/" + number + revue + ".txt"
    FichierResult2 = settings.RESULT_PRETRAIT_DIR + "/AmeliorText/" \
                     + reduction + "/" + objet + "Result/" + number + revue + "Para.txt"
    MotSpe = []
    error = False
    seuil = 0
    motponctu = ""

    if os.path.isfile(FichierResult1) and os.path.isfile(FichierResult2):
        with open(FichierResult1, 'r') as f:
            content = f.readlines()
            SousListes = []
            for i, elt in enumerate(content):
                if ((i + 1) % 3 != 0):
                    SousListes.append(elt)
                else:
                    MotSpe.append(SousListes)
                    SousListes = []

        with open(FichierResult2, 'r') as f:
            content = f.readlines()
            mot = content[0].rstrip()
            ponctuation = content[1].rstrip()
            seuil = content[2].rstrip()
        motponctu = mot + ponctuation
    else:
        error = True

    return error, MotSpe, seuil, motponctu


def PrepaSupprMotAvantObjetResult(request, reduction, revue, objet):

    error = False
    PossibleChange = False
    Change = False
    TestReduc = CorpusEtude.objects.filter(nom=reduction)

    if TestReduc.exists():
        ReducEnCours = TestReduc[0]
    else:
        error = False

    if not error and request.user.id is not None:
        # si c'est un super utilisateur ou s'il a les droit sur cette réduction
        if request.user.is_superuser or (str(request.user.id) in ReducEnCours.user_restrict.split(",")):
            PossibleChange = True

    if PossibleChange:

        DossierResult = settings.RESULT_PRETRAIT_DIR + "/AmeliorText/" \
                        + reduction + "/" + objet + "Result"
        FichierResult1 = settings.RESULT_PRETRAIT_DIR + "/AmeliorText/" \
                         + reduction + "/" \
                         + reduction + revue + objet + "Avt.txt"
        FichierResult2 = settings.RESULT_PRETRAIT_DIR + "/AmeliorText/" \
                         + reduction + "/" \
                         + reduction + revue + objet + "AvtNbreMotsAvt.txt"

        if os.path.isfile(FichierResult1) and os.path.isfile(FichierResult2):
            shutil.rmtree(DossierResult)
            os.remove(FichierResult1)
            os.remove(FichierResult2)
            Change = True

    return error, PossibleChange, Change



def PrepaExplorTraitHome1(request, objet):
    PartieDoc = ["Titre", "Resume", "MotCle", "HautDePage", "BasDePage", "Note", "Figure", "Titre123", "Biblio",
                 "Annexe", "FinDoc"]
    PartieMot = ["Cedille", "FinMot", "FinLigne"]
    reductionsall = CorpusEtude.objects.all()
    reductionsselect = SelectReducFctUser(request, reductionsall)
    # dictionnaires des fonctions disponibles pour chaque objet : Titre, Resumr,...
    DicoFctSpe = DicFctExplo(objet)
    fctselect = DicoFctSpe.keys()
    revueselect = ["Annales", "Espace"]

    PossibleChange = False
    CorpusExist = False
    ChangeExist = False
    MaqueurPartieDoc = False
    if objet in PartieDoc:
        MaqueurPartieDoc = True
    MaqueurPartieMot = False
    if objet in PartieMot:
        MaqueurPartieMot = True

    RenduPluriel = DicModelFormRefInsert(objet, "RenduPluriel")
    Numero = DicModelFormRefInsert(objet, "numero")

    return reductionsselect, PossibleChange, CorpusExist, ChangeExist, MaqueurPartieDoc, MaqueurPartieMot, RenduPluriel,\
           Numero, fctselect, revueselect







def PrepaTraitHome1(request, objet):
    reductionsall = CorpusEtude.objects.all().order_by('id')
    reductionsselect = SelectReducFctUser(request, reductionsall)
    PossibleChange = False
    CorpusExist = False
    ChangeExist = False
    PartieDoc = ["Titre", "Resume", "MotCle", "HautDePage", "BasDePage", "Note", "Figure", "Titre123", "Biblio",
                 "Annexe", "FinDoc"]
    PartieMot = ["Cedille", "FinMot", "FinLigne"]
    MaqueurPartieDoc = False
    if objet in PartieDoc:
        MaqueurPartieDoc = True
    MaqueurPartieMot = False
    if objet in PartieMot:
        MaqueurPartieMot = True
    RenduPluriel = DicModelFormRefInsert(objet, "RenduPluriel").capitalize()
    Numero = DicModelFormRefInsert(objet, "numero")

    return reductionsselect, PossibleChange, CorpusExist, ChangeExist, MaqueurPartieDoc, MaqueurPartieMot, RenduPluriel, Numero





def PrepaTraitHome2(request, objet, reduction_id, demande, reductionsselect,CorpusExist,PossibleChange,ChangeExist):
    if reduction_id != 0:
        # test s'il existe déjà un enregistement
        CorpusExist = True
        TraitHistorique = DicModelFormRefInsert(objet, "modele").objects.filter(CorpusEtudeRef=demande)
        if TraitHistorique.exists():
            ChangeExist = True
            form = DicModelFormRefInsert(objet, "formulaire")(instance=TraitHistorique[0])
        else:
            form = DicModelFormRefInsert(objet, "formulaire")()

        if request.user.is_superuser or (str(request.user.id) in reductionsselect[0].user_restrict.split(",")):
            PossibleChange = True

    # si reduction_id = 0
    else:
        form = DicModelFormRefInsert(objet, "formulaire")()

        if len(reductionsselect) > 0:
            CorpusExist = True

            if request.user.is_superuser or (str(request.user.id) in reductionsselect[0].user_restrict.split(",")):
                PossibleChange = True
    return CorpusExist,PossibleChange,ChangeExist,form


def TraitHomeTrait(request, objet, reduction_id, CEencours, donnees, recupdonnees):

    ModelEnCours = DicModelFormRefInsert(objet, "modele")
    TestExistTransform = ModelEnCours.objects.filter(CorpusEtudeRef=CEencours)
    # si existe, l'efface avant tout
    if TestExistTransform.count() == 1:
        if objet == "Note":
            SupprCoordGraph(reduction_id, objet)
        else:
            TestExistTransform[0].delete()
            # héritage d'un essai de simplification (traitement en commun)
            # pas si simple
            EltEfface = Transformer.objects.filter(type=objet)
            for elt in EltEfface:
                if elt.DocExtractRef.CorpusEtudeRef == CEencours:
                    elt.delete()
    # effectue l'insertion
    FctInsert = DicModelFormRefInsert(objet, "FctTrait")
    FctInsert(CEencours.nom, donnees)
    # sauve la nouvelle
    recupdonnees.instance.CorpusEtudeRef = CEencours
    recupdonnees.instance.user = request.user.id
    recupdonnees.save()

    # Pour cas mots
    ListMots = []
    if objet == "Resume" or objet == "MotCle" or objet == "Biblio" \
            or objet == "Annexe" or objet == "Figure" or objet == "FinDoc":
        ListMots = donnees.get("mots").split("*")

    RenduPluriel = DicModelFormRefInsert(objet, "RenduPluriel")

    return ListMots, RenduPluriel


def TraitSuppr(objet, reduction, CEencours):
    ModelEnCours = DicModelFormRefInsert(objet, "modele")
    # sélection pour la réduction concerné
    TestExistTransform = ModelEnCours.objects.filter(CorpusEtudeRef=CEencours)
    #  si elle existe
    if TestExistTransform.count() == 1:
        # efface les paramètres enregistrés
        TestExistTransform[0].delete()
        # efface les éléments
        # héritage d'un essai de simplification (traitement en commun)
        # pas si simple !
        if objet == "Note":
            SupprCoordGraph(reduction, objet)
        else:
            EltEfface = Transformer.objects.filter(type=objet)
            for elt in EltEfface:
                if elt.DocExtractRef.CorpusEtudeRef == CEencours:
                    elt.delete()


################# FINALISATION / EXTRACTION DE TEXTE ###########

def gestion_conflits(elt_nettoyage):
    """ Fonction qui permet de résoudre le problème des recouvrements d'indices
     (détection d'un haut de page dans un titre).
      Si un recouvrement est détecté, on juxtapose les éléments à retirer.
       Ex: [2:10] et [5:15] devient [2:5] et [5:15]

    Args:
        elt_nettoyage (list of dict):
            'IndexDebut': indice du début de l'élément à retirer
            'IndexFin': indice de fin de l'élément à retirer

    Return:
        elt_nettoyage (list of dict): l'argument d'entrée mis à jour.
    """
    id0 = int(elt_nettoyage[0]['IndexDeb'])
    if0 = int(elt_nettoyage[0]['IndexFin'])
    for i, elt in enumerate(elt_nettoyage[1:]):
        id1 = int(elt['IndexDeb'])
        if1 = int(elt['IndexFin'])
        if if1 <= id0:
            id0 = id1
            if0 = if1
        else:
            if id1 >= id0:
                elt_nettoyage[i + 1][
                    'IndexDeb'] = ''  # 'i+1' correspond à l'indice en cours, permet de ne pas prendre en compte si correction mots
                elt_nettoyage[i + 1]['IndexFin'] = ''  # inclus dans toute une fenêtre supprimée plus grande de partie.
            else:
                elt_nettoyage[i + 1]['IndexFin'] = id0  # 'i+1' correspond à l'indice en cours
                id0 = id1
                if0 = id0
    return elt_nettoyage


def SaveSynthese(CorpusEtu):
    seuilTitre, SupprSlashSecondPart, SupprBeforeTitre, motsResume, zoneResume, AjoutResumeFr, motstMotCle, zonetMotCle, AjoutMotCleFr, \
    seuilgeoHtdePage, seuilspgeoHtdePage, SupprAnnCombiTextualBasdePage, SupprEspSup1990BasdePage, SupprNoteBio, SupprNoteEdito, SupprNoteBasDePage, \
    SupprBilioEtFin, motsBiblio, zoneBiblio, supprAppendix, motsAppendix, zoneAppendix, remplaceSsTitre, remplaceSsTitre, \
    EssaiHomogeneTitre, motsFigure, ContenuCentreRemove, motsFinDoc, ManuscritRemove, litigecedille, FinMotTrait, \
    FinLigneNormalise, AllExceptRemoveRef, AllExceptAddRef, DocRemoveRef = TraitSaveSynthese(CorpusEtu)

    SynthToSave = SyntheseTransform(seuilTitre=seuilTitre, SupprSlashSecondPart=SupprSlashSecondPart,
                                    SupprBeforeTitre=SupprBeforeTitre,
                                    motsResume=motsResume, zoneResume=zoneResume, AjoutResumeFr=AjoutResumeFr,
                                    motstMotCle=motstMotCle, zonetMotCle=zonetMotCle, AjoutMotCleFr=AjoutMotCleFr,
                                    seuilgeoHtdePage=seuilgeoHtdePage, seuilspgeoHtdePage=seuilspgeoHtdePage,
                                    SupprAnnCombiTextualBasdePage=SupprAnnCombiTextualBasdePage,
                                    SupprEspSup1990BasdePage=SupprEspSup1990BasdePage,
                                    SupprNoteBio=SupprNoteBio, SupprNoteEdito=SupprNoteEdito,
                                    SupprNoteBasDePage=SupprNoteBasDePage,
                                    SupprBilioEtFin=SupprBilioEtFin, motsBiblio=motsBiblio, zoneBiblio=zoneBiblio,
                                    supprAppendix=supprAppendix, motsAppendix=motsAppendix, zoneAppendix=zoneAppendix,
                                    remplaceSsTitre=remplaceSsTitre,
                                    EssaiHomogeneTitre=EssaiHomogeneTitre, motsFigure=motsFigure,
                                    ContenuCentreRemove=ContenuCentreRemove, motsFinDoc=motsFinDoc,
                                    ManuscritRemove=ManuscritRemove,
                                    litigecedille=litigecedille, FinMotTrait=FinMotTrait,
                                    FinLigneNormalise=FinLigneNormalise,
                                    AllExceptRemoveRef=AllExceptRemoveRef, AllExceptAddRef=AllExceptAddRef,
                                    DocRemoveRef=DocRemoveRef)

    SynthToSave.save()
    return SynthToSave


def TraitSyntheseHome(reduction,CEencours):
    AdresseResult = settings.RESULT_PRETRAIT_DIR + "/AmeliorText/" + reduction + "/fin"
    # si une extraction est déjà existante, l'efface et la remplace !
    if os.path.exists(AdresseResult):
        shutil.rmtree(AdresseResult)
    os.makedirs(AdresseResult)

    docsextractencours = DocExtractInitial.objects.filter(CorpusEtudeRef=CEencours)
    # liste des documents à enlever
    docsremoveencours = DocRemove.objects.filter(CorpusEtudeRef=CEencours)
    DocRemoveList = []
    for docRemove in docsremoveencours:
        DocRemoveList.append(docRemove.DocExtractRef.DocReferenceRef.TextRef)

    for i, docencours in enumerate(docsextractencours):
        nomfichierencours = docencours.DocReferenceRef.TextRef
        if nomfichierencours not in DocRemoveList:
            addressedocencours = GetAdresseCompletDoc(nomfichierencours)
            NomFin = nomfichierencours.split("_tei")[0] + ".txt"
            AdresseFin = AdresseResult + '/' + NomFin
            plein_texte = DocMot(addressedocencours)
            # Attention dans l'ordre inverse car order_by("-IndexFin")
            # le moins est important !
            eltstransfo_encours_order = list(
                Transformer.objects.filter(DocExtractRef=docencours).order_by("-IndexFin").values())
            if eltstransfo_encours_order:
                eltstransfo_simplified = gestion_conflits(eltstransfo_encours_order)
                for elt in eltstransfo_simplified:
                    print(elt)
                    if elt['IndexDeb'] != '' and elt['IndexFin'] != '':
                        # efface
                        del plein_texte[elt['IndexDeb']:elt['IndexFin']]
                        # si text remplace
                        if elt['TextField'] != '':
                            plein_texte.insert(elt['IndexDeb'], elt['TextField'].replace("''", "'"))

                with open(AdresseFin, "w+") as f:
                    f.write(" ".join(plein_texte))
            else:
                with open(AdresseFin, "w+") as f:
                    f.write(" ".join(plein_texte))
            # enregistrer les doctransformes
            DocToSave = DocTransforme(DocExtractRef=docencours, CorpusEtudeRef=CEencours,
                                      TextTransforme=docencours.TextExtract)
            DocToSave.save()

    # enregistre SyntheseTransform
    SyntSave = SaveSynthese(CEencours)
    # puis complete  CorpusEtude
    CEencours.SyntheseTransformRef = SyntSave
    CEencours.save()


def TraitSyntheseTraitement(CEencours):
    objets = ["Titre", "Resume", "MotCle", "HautDePage", "BasDePage", "Note", "Titre123",
              "Biblio", "Annexe", "Figure", "FinDoc", "Cedille", "FinMot", "FinLigne"]
    ListRed = []
    ListPluriel = []
    ListCheckTransform = []
    ListTransform = []
    ListEltRemove = []
    ListEltAdd = []
    ListDocRemove = []

    for objet in objets:
        ListRed.append(objet)
        ListPluriel.append(DicModelFormRefInsert(objet, "RenduPluriel"))
        Modele = DicModelFormRefInsert(objet, "modele")

        TestTransform = Modele.objects.filter(CorpusEtudeRef=CEencours)
        if TestTransform.exists():
            ListCheckTransform.append(True)
            ListTransform.append(TestTransform.values())
        else:
            ListCheckTransform.append(False)
            ListTransform.append(Modele.objects.none())
        EltRemove = AllExceptRemove.objects.filter(CorpusEtudeRef=CEencours, type=objet)
        if EltRemove.exists():
            ListEltRemove.append(True)
        else:
            ListEltRemove.append(False)
        EltAdd = AllExceptAdd.objects.filter(CorpusEtudeRef=CEencours, type=objet)
        if EltAdd.exists():
            ListEltAdd.append(True)
        else:
            ListEltAdd.append(False)
        DocRemov = DocRemove.objects.filter(CorpusEtudeRef=CEencours, type=objet)
        if DocRemov.exists():
            ListDocRemove.append(True)
        else:
            ListDocRemove.append(False)

    return objets,ListRed,ListPluriel,ListCheckTransform,ListTransform,ListEltRemove,ListEltAdd,ListDocRemove


def TraitSaveSynthese(CorpusEtu):
    """
        A factoriser : il faudrait en amont changer le nom de champs de certains modèles
        d'AmeliorText pour qu'il soit unique. Permettrait de faire une fonction for sur label
        en excluant : user et CorpusEtudeRef
        en utilisant le DicModelFormRefInsert["objet"]["modele"] en itérant sur chaque objet du dico : Titre, Resume,...
        Necessite aussi de stocker valeur par défaut si modèle n'a pas été utilisé.
        """
    TestTitreTransfo = TitreTransform.objects.filter(CorpusEtudeRef=CorpusEtu)
    if TestTitreTransfo.exists():
        seuilTitre = TestTitreTransfo[0].seuil
        SupprSlashSecondPart = TestTitreTransfo[0].SupprSlashSecondPart
        SupprBeforeTitre = TestTitreTransfo[0].SupprBeforeTitre
    else:
        seuilTitre = 0
        SupprSlashSecondPart = False
        SupprBeforeTitre = False

    TestResumeTransfo = ResumeTransform.objects.filter(CorpusEtudeRef=CorpusEtu)
    if TestResumeTransfo.exists():
        motsResume = TestResumeTransfo[0].mots
        zoneResume = TestResumeTransfo[0].zone
        AjoutResumeFr = TestResumeTransfo[0].AjoutResumeFr
    else:
        motsResume = ""
        zoneResume = 0
        AjoutResumeFr = False

    TestMotCleTransfo = MotCleTransform.objects.filter(CorpusEtudeRef=CorpusEtu)
    if TestMotCleTransfo.exists():
        motstMotCle = TestMotCleTransfo[0].mots
        zonetMotCle = TestMotCleTransfo[0].zone
        AjoutMotCleFr = TestMotCleTransfo[0].AjoutMotCleFr
    else:
        motstMotCle = ""
        zonetMotCle = 0
        AjoutMotCleFr = False

    TestHtDePageTransfo = HtDePageTransform.objects.filter(CorpusEtudeRef=CorpusEtu)
    if TestHtDePageTransfo.exists():
        seuilgeoHtdePage = TestHtDePageTransfo[0].seuilgeo
        seuilspgeoHtdePage = TestHtDePageTransfo[0].seuilspgeo
    else:
        seuilgeoHtdePage = 0
        seuilspgeoHtdePage = 0

    TestBasDePageTransfo = BasDePageTransform.objects.filter(CorpusEtudeRef=CorpusEtu)
    if TestBasDePageTransfo.exists():
        SupprAnnCombiTextualBasdePage = TestBasDePageTransfo[0].SupprAnnCombiTextual
        SupprEspSup1990BasdePage = TestBasDePageTransfo[0].SupprEspSup1990
    else:
        SupprAnnCombiTextualBasdePage = False
        SupprEspSup1990BasdePage = False

    TestNoteTransfo = NoteTransform.objects.filter(CorpusEtudeRef=CorpusEtu)
    if TestNoteTransfo.exists():
        SupprNoteBio = TestNoteTransfo[0].SupprNoteBio
        SupprNoteEdito = TestNoteTransfo[0].SupprNoteEdito
        SupprNoteBasDePage = TestNoteTransfo[0].SupprNoteBasDePage
    else:
        SupprNoteBio = False
        SupprNoteEdito = False
        SupprNoteBasDePage = False

    TestBiblioTransfo = BiblioTransform.objects.filter(CorpusEtudeRef=CorpusEtu)
    if TestBiblioTransfo.exists():
        SupprBilioEtFin = TestBiblioTransfo[0].SupprBilioEtFin
        motsBiblio = TestBiblioTransfo[0].mots
        zoneBiblio = TestBiblioTransfo[0].zone
    else:
        SupprBilioEtFin = False
        motsBiblio = ""
        zoneBiblio = 0

    TestAppendixTransfo = AppendixTransform.objects.filter(CorpusEtudeRef=CorpusEtu)
    if TestAppendixTransfo.exists():
        supprAppendix = TestAppendixTransfo[0].suppr
        motsAppendix = TestAppendixTransfo[0].mots
        zoneAppendix = TestAppendixTransfo[0].zone
    else:
        supprAppendix = False
        motsAppendix = ""
        zoneAppendix = 0

    TestSousTitreTransfo = SousTitreTransform.objects.filter(CorpusEtudeRef=CorpusEtu)
    if TestSousTitreTransfo.exists():
        remplaceSsTitre = TestSousTitreTransfo[0].remplace
    else:
        remplaceSsTitre = False

    TestFigureTransfo = FigureTransform.objects.filter(CorpusEtudeRef=CorpusEtu)
    if TestFigureTransfo.exists():
        EssaiHomogeneTitre = TestFigureTransfo[0].EssaiHomogeneTitre
        motsFigure = TestFigureTransfo[0].mots
    else:
        EssaiHomogeneTitre = False
        motsFigure = ""

    TestFinDocTransfo = FinDocTransform.objects.filter(CorpusEtudeRef=CorpusEtu)
    if TestFinDocTransfo.exists():
        ContenuCentreRemove = TestFinDocTransfo[0].ContenuCentreRemove
        motsFinDoc = TestFinDocTransfo[0].mots
        ManuscritRemove = TestFinDocTransfo[0].ManuscritRemove
    else:
        ContenuCentreRemove = False
        motsFinDoc = ""
        ManuscritRemove = False

    TestCedilleTransfo = CedilleTransform.objects.filter(CorpusEtudeRef=CorpusEtu)
    if TestCedilleTransfo.exists():
        litigecedille = TestCedilleTransfo[0].litigecedille
    else:
        litigecedille = False

    TestFinMotTransfo = FinMotTransform.objects.filter(CorpusEtudeRef=CorpusEtu)
    if TestFinMotTransfo.exists():
        FinMotTrait = True
    else:
        FinMotTrait = False

    TestFinLigneTransfo = FinLigneTransform.objects.filter(CorpusEtudeRef=CorpusEtu)
    if TestFinLigneTransfo.exists():
        FinLigneNormalise = TestFinLigneTransfo[0].normalise
    else:
        FinLigneNormalise = False

    TestExceptRemoveTransfo = AllExceptRemove.objects.filter(CorpusEtudeRef=CorpusEtu)
    if TestExceptRemoveTransfo.exists():
        ListExceptRemove = []
        for ExceptRemove in TestExceptRemoveTransfo:
            ListExceptRemove.append(str(ExceptRemove.id))
        AllExceptRemoveRef = ",".join(ListExceptRemove)
    else:
        AllExceptRemoveRef = ""

    TestExceptAddTransfo = AllExceptAdd.objects.filter(CorpusEtudeRef=CorpusEtu)
    if TestExceptAddTransfo.exists():
        ListExceptAdd = []
        for ExceptAdd in TestExceptAddTransfo:
            ListExceptAdd.append(str(ExceptAdd.id))
        AllExceptAddRef = ",".join(ListExceptAdd)
    else:
        AllExceptAddRef = ""

    TestDocRemoveTransfo = DocRemove.objects.filter(CorpusEtudeRef=CorpusEtu)
    if TestDocRemoveTransfo.exists():
        ListDocRemove = []
        for doc in TestDocRemoveTransfo:
            ListDocRemove.append(str(doc.id))
        DocRemoveRef = ",".join(ListDocRemove)
    else:
        DocRemoveRef = ""

    return seuilTitre,SupprSlashSecondPart,SupprBeforeTitre,motsResume,zoneResume,AjoutResumeFr,motstMotCle,zonetMotCle,AjoutMotCleFr,\
           seuilgeoHtdePage,seuilspgeoHtdePage,SupprAnnCombiTextualBasdePage,SupprEspSup1990BasdePage,SupprNoteBio,SupprNoteEdito,SupprNoteBasDePage,\
           SupprBilioEtFin,motsBiblio,zoneBiblio,supprAppendix,motsAppendix,zoneAppendix,remplaceSsTitre,remplaceSsTitre,\
           EssaiHomogeneTitre,motsFigure,ContenuCentreRemove,motsFinDoc,ManuscritRemove,litigecedille,FinMotTrait,\
           FinLigneNormalise,AllExceptRemoveRef,AllExceptAddRef,DocRemoveRef


# Ces deux fonctions pourraient être plus générique !
# n pour 200 et l pour 4 dans la version list

def ResultRedDebFin200Simple(Result,NbresResult):
    MarqueurLimitePage = False
    ResultDeb = []
    ResultFin = []
    if NbresResult > 200:
        MarqueurLimitePage = True
        ResultDeb = Result[0:100]
        ResultFin = Result[-100:]
    return MarqueurLimitePage, ResultDeb, ResultFin


def ResultRedDebFin200List4(Result,NbresResult):
    MarqueurLimitePage = False
    Result1Deb = []
    Result2Deb = []
    Result3Deb = []
    Result4Deb = []
    Result1Fin = []
    Result2Fin = []
    Result3Fin = []
    Result4Fin = []
    if NbresResult > 200:
        MarqueurLimitePage = True
        Result1Deb = Result[0][0:100]
        Result1Fin = Result[0][-100:]
        Result2Deb = Result[1][0:100]
        Result2Fin = Result[1][-100:]
        Result3Deb = Result[2][0:100]
        Result3Fin = Result[2][-100:]
        Result4Deb = Result[3][0:100]
        Result4Fin = Result[3][-100:]
    RedListDeb = zip(Result1Deb, Result2Deb, Result3Deb, Result4Deb)
    RedListFin = zip(Result1Fin, Result2Fin, Result3Fin, Result4Fin)
    return MarqueurLimitePage, RedListDeb, RedListFin
