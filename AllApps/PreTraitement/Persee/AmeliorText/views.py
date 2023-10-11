import os
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from AllApps.PreTraitement.Persee.DelimitCorpus.core import ExplicitRevue
from AllApps.PreTraitement.Persee.DelimitCorpus.models import CorpusEtude
from AllApps.PreTraitement.Persee.DelimitCorpus.views import SelectReducFctUser

from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.ExploreFct.ExpCedilleFct import \
    VerifAvantApresCedilleExist
from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.ExploreFct.ExpCoordGraphSimpleFct import \
    AfficheCoordGraphDiscontinuMaxDo

from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.ExploreFct.ExpFinDocFct import \
    AfficheLigneCenterLastPageDo, PresenceDebutLigneDo

from .OrgaScript.TraitMFct import RemoveEltAllDo, AddEltAllDo, RemoveDocDo
from .forms import  SeqChercheForm
from .models import AllExceptRemove, AllExceptAdd, DocRemove
from .periph import DicModelFormRefInsert, PrepaExplorHome, TraitExplorHome, RechercheSeqDansFichierDo,\
    PrepaPresenceMotAvantObjetInterface, PresenceMotAvantObjetInterfaceTrait, PrepaPresenceMotAvantObjetResult,PrepaSupprMotAvantObjetResult,\
    PrepaTraitHome2, PrepaTraitHome1, PrepaExplorTraitHome1, TraitHomeTrait, TraitSuppr, TraitSyntheseHome, TraitSyntheseTraitement, \
    ResultRedDebFin200Simple, ResultRedDebFin200List4, TestRef, RecupNameFct, RecupFctAttr


def home(request):
    return render(request,'AmeliorText/General/home.html')



def ReDispatch(request, mode, objet):
    '''permet de rediriger vers les pages (render) ou fonctions (redirect) voulues
    en fonction choix des utilisateurs ci dessus
    ATTENTION suit le même ordre que la présentation des fonctions ci dessous
    '''
    TraitExplorSepare = ["Titre","Resume","MotCle","HautDePage","BasDePage","Note","Figure","Biblio","FinDoc","Cedille"]
    TraitExplorEnsemble = ["Annexe","Titre123","FinMot","FinLigne"]

    if mode == "Explor":
        if objet in TraitExplorSepare:
            return redirect('AmeliorText:ExplorHome', objet)
        elif objet in TraitExplorEnsemble:
            return redirect('AmeliorText:ExplorTraitHome', objet, 0)
        else:
            return redirect('AmeliorText:home')

    elif mode == "TraitA":
        if objet in TraitExplorSepare:
            return redirect('AmeliorText:TraitHome', objet, 0)
        elif objet in TraitExplorEnsemble:
            return redirect('AmeliorText:ExplorTraitHome', objet, 0)
        else:
            return redirect('AmeliorText:home')

    elif mode == "TraitM":
        if (objet in TraitExplorSepare) or (objet in TraitExplorEnsemble):
            return redirect('AmeliorText:ExceptHome', objet)
        else:
            return redirect('AmeliorText:home')


    elif mode == "ExplorTrait":
        if objet in TraitExplorSepare:
            return redirect('AmeliorText:ExplorHome', objet)
        elif objet in TraitExplorEnsemble:
            return redirect('AmeliorText:ExplorTraitHome', objet, 0)
        else:
            return redirect('AmeliorText:home')

    else:
        return redirect('AmeliorText:home')


###################  EXPLORE TITRE ##########################


def ExplorHome(request, objet):

    if 'Effectuer' in request.POST:
        error, reduction, revuered, fonction, agreg, ref = TraitExplorHome(request, objet)
        if not error:
            if fonction == "PresenceMotAvantObjetInterface":
                url = reverse(agreg, kwargs={'reduction': reduction, 'revue': revuered, "objet": objet})
            elif fonction == "AfficheTitreTrait" or fonction == "AfficheNoteDiscontinu"\
                    or fonction=="LastPageCenter" or fonction == "DetectDebutLigne" :
                url = reverse(agreg, kwargs={'reduction': reduction, 'revue': revuered})
            elif fonction =="AfficheMotCedilleAvtApres":
                url = reverse(agreg)
            # cas FontionGeneralExplor
            else:
                url = reverse(agreg, kwargs={'reduction': reduction, 'revue': revuered, 'ref':ref})
            return HttpResponseRedirect(url)

        else:
            return render(request, 'AmeliorText/General/home.html')

    TraitExplorSepare = ["Titre", "Resume", "MotCle", "HautDePage", "BasDePage", "Note", "Figure", "Biblio", "FinDoc",
                         "Cedille"]
    TraitExplorEnsemble = ["Annexe", "Titre123", "FinMot", "FinLigne"]

    if objet in TraitExplorSepare:
        reductionsselect, fctselect, revueselect, Numero, RenduPluriel, MaqueurPartieDoc, MaqueurPartieMot \
            = PrepaExplorHome(request,objet)

        context = {"reductions": reductionsselect, "fctselect": fctselect, "objet": objet, "revueselect": revueselect,
                   "Numero":Numero,"RenduPluriel":RenduPluriel,"MaqueurPartieDoc":MaqueurPartieDoc, "MaqueurPartieMot":MaqueurPartieMot}
        return render(request, 'AmeliorText/Explor/' + objet + '/Exp' + objet + 'Home.html', context)
    elif objet in TraitExplorEnsemble:
        return redirect('AmeliorText:ExplorTraitHome', objet, 0)
    else:
        return redirect('AmeliorText:home')



def FontionGeneralExplor(request, reduction, revue, ref):

    error = TestRef(ref)
    if error:
        return render(request, 'AmeliorText/General/home.html')

    NameFct = RecupNameFct(ref)
    FctAttr = RecupFctAttr(NameFct)

    error, revuerealname, autrerevue = ExplicitRevue(revue)
    if error:
        return render(request, 'AmeliorText/General/home.html')

    FichierResult = settings.RESULT_PRETRAIT_DIR + "/AmeliorText/" \
                    + reduction + "/" \
                    + reduction + revue + FctAttr["namesave"] +".txt"

    error, Result, NbresResult = FctAttr["fctdo"](FichierResult, reduction, revue)
    if error:
        return render(request, 'AmeliorText/General/home.html')

    if FctAttr["red"] == "simple":
        MarqueurLimitePage, ResultDeb, ResultFin = ResultRedDebFin200Simple(Result, NbresResult)

        context = {"MarqueurLimitePage": MarqueurLimitePage, "Result": Result, "NbresResult": NbresResult,
                   "ResultDeb": ResultDeb, "ResultFin": ResultFin,
                   "reduction": reduction, "revue": revue, "revuerealname": revuerealname}

    elif FctAttr["red"] == "list":
        MarqueurLimitePage, RedListDeb, RedListFin = ResultRedDebFin200List4(Result, NbresResult)

        context = {"RedListDeb": RedListDeb, "RedListFin": RedListFin, "Result": Result,
                   "MarqueurLimitePage": MarqueurLimitePage, "reduction": reduction,
                   "NbresResult": NbresResult, "revue": revue, "revuerealname": revuerealname}

    # pas de réduction
    else:
        context = {"Result": Result, "NbresResult": NbresResult,
                   "reduction": reduction, "revue": revue, "revuerealname": revuerealname}

    TraitExplorSepare = ["Titre", "Resume", "MotCle", "HautDePage", "BasDePage", "Note", "Figure", "Biblio", "FinDoc",
                         "Cedille"]
    TraitExplorEnsemble = ["Annexe", "Titre123", "FinMot", "FinLigne"]

    if FctAttr["objet"] in TraitExplorSepare:
        return render(request, 'AmeliorText/Explor/'+ FctAttr["objet"] + '/' + FctAttr["namesave"] + '.html', context)
    elif FctAttr["objet"] in TraitExplorEnsemble:
        return render(request, 'AmeliorText/ExplorTrait/' + FctAttr["objet"] + '/' + FctAttr["namesave"] + '.html', context)
    else:
        return redirect('AmeliorText:home')


def AfficheTitreTrait(request, reduction, revue):
    """permet d'afficher le résultat des traitements réalisés à parir de la précédente fonction
    Voir thèse M Beligne
    ex fichier entrée :
        rouge
        article_geo_0003-4010_1932_num_41_232_10785_tei.xml
        0.4375
        l'étude paléo- phytologique des tourbes quaternaires, les uns dans le but d'établir les origines
        L'état actuel des industries du sucre et du rhum à la Martinique
        45 – 58  → 11 - 26  (Erreur Persée. Titre exact :  Les modifications postglaciaires de la silve européenne, d'après les résultats des analyses polliniques des tourbes)    
    """

    error, revuerealname, autrerevue = ExplicitRevue(revue)
    if error:
        return render(request, 'AmeliorText/General/home.html')


    FichierResult = settings.RESULT_PRETRAIT_DIR + "/AmeliorText/" \
                    + reduction + "/" \
                    + reduction + revue + "TitresTrait.txt"
    ResultListElt = []
    SousListes = []

    # le fichier doit être entré en amont après un travail manuel
    if os.path.isfile(FichierResult):
        with open(FichierResult,"r") as f:
            content = f.readlines()

        for i, elt in enumerate(content):
            # car il y a six éléments dans chaque sous listes
            if ((i + 1) % 7 != 0):
                SousListes.append(elt.rstrip())
            else:
                ResultListElt.append(SousListes)
                SousListes = []

        context = {"ResultListElt": ResultListElt,"reduction": reduction, "revue": revue, "revuerealname":revuerealname}
        return render(request, 'AmeliorText/Explor/Titre/TitresTrait.html', context)

    else:
        return render(request, 'AmeliorText/General/home.html')



def RechercheSeqDansFichier(request):
    """ Interface pour rechercher les index d'une séquence dans un fichier
        """
    if request.method == 'POST':
        if 'Effectuer' in request.POST:
            form = SeqChercheForm(request.POST)
            if form.is_valid():
                donnees = form.cleaned_data

                error, MarqueurDocExist, result = RechercheSeqDansFichierDo(donnees)
                if error:
                    return render(request, 'AmeliorText/General/home.html')

                if not MarqueurDocExist:
                    result = "Le document " + donnees["article"] + " n'existe pas dans ce corpus"

                context = {"result":result, "reduction":donnees["corpus"] }
                return render(request, 'AmeliorText/General/ResultChercheSeq.html',context)


    Form = SeqChercheForm()
    context = {"Form":Form}
    return render(request, 'AmeliorText/General/InterfaceChercheSeq.html', context)




def PresenceMotAvantObjetInterface(request, reduction, revue, objet):
    '''
    Renvoie vers interface : Presencemotavant
    qui va demander mot, ponctuation et seuil de recherche
    Demande objet car va être réutilisé pour MotCle, Biblio et Annexe
    '''
    if request.method == 'POST':
        if 'Effectuer' in request.POST:
            mots = request.POST.get('mots')
            ponctuations = request.POST.get('ponctuations')
            if mots != "" or ponctuations != "":

                PossibleChange, TestPresenceResult, ContenuResult, SeuilEnCours = \
                    PresenceMotAvantObjetInterfaceTrait(request, reduction, revue, objet, mots, ponctuations)

                if PossibleChange:
                    context = {"reduction": reduction, "revue": revue, "SeuilEnCours": SeuilEnCours,
                               "TestPresenceResult": TestPresenceResult, "ContenuResult": ContenuResult,
                               "PossibleChange": PossibleChange}
                    if objet == "Annexe":
                        return render(request,'AmeliorText/ExplorTrait/' + objet + '/MotAvant' + objet + 'Interface.html',context)
                    else:
                        return render(request, 'AmeliorText/Explor/' + objet + '/MotAvant' + objet + 'Interface.html', context)
                else:
                    return render(request, 'AmeliorText/Explor/ExplorBase/AbsenceDroit.html')

            else:
                messages.add_message(request, messages.INFO, 'Les champs mots et poncuations ne doivent pas être vide')
                TestPresenceResult = False
                ContenuResult = ""
                context = {"reduction": reduction, "revue": revue, "TestPresenceResult": TestPresenceResult, "ContenuResult":ContenuResult}
            if objet == "Annexe":
                return render(request, 'AmeliorText/ExplorTrait/' + objet + '/MotAvant' + objet + 'Interface.html',context)
            else:
                return render(request, 'AmeliorText/Explor/' + objet + '/MotAvant'+ objet + 'Interface.html', context)

    # Prepa html
    error, PossibleChange, TestPresenceResult, ContenuResult, SeuilEnCours = \
        PrepaPresenceMotAvantObjetInterface(request, reduction, revue, objet)

    if not error:
        context = {"reduction": reduction, "revue": revue, "PossibleChange": PossibleChange,
                   "TestPresenceResult": TestPresenceResult, "ContenuResult": ContenuResult,
                   "SeuilEnCours": SeuilEnCours}
        if objet == "Annexe":
            return render(request, 'AmeliorText/ExplorTrait/' + objet + '/MotAvant' + objet + 'Interface.html',context)
        else:
            return render(request, 'AmeliorText/Explor/' + objet + '/MotAvant' + objet  + 'Interface.html', context)
    else:
        return render(request, 'AmeliorText/General/home.html')



def PresenceMotAvantObjetResult(request, reduction, revue, number, objet):
    '''
    Renvoie vers résultat individuel
    '''

    error, MotSpe, seuil, motponctu = PrepaPresenceMotAvantObjetResult(reduction, revue, number, objet)

    if not error:
        context = {"reduction": reduction, "revue": revue, "MotSpe": MotSpe, "seuil": seuil,
                   "motponctu": motponctu}
        if objet == "Annexe":
            return render(request,'AmeliorText/ExplorTrait/' + objet + '/MotAvant' + objet + 'Result.html',context)
        else:
            return render(request, 'AmeliorText/Explor/' + objet + '/MotAvant' + objet + 'Result.html', context)
    else:
        return redirect('AmeliorText:PresenceMotAvant'  + objet + 'Interface', reduction, revue,  objet)


def SupprMotAvantObjetResult(request, reduction, revue, objet):
    '''
    Permet suppression des résultats générés et redirection vers interface 
    '''

    error, PossibleChange, Change  = PrepaSupprMotAvantObjetResult(request, reduction, revue, objet)
    if not error and PossibleChange and Change:
        return redirect('AmeliorText:PresenceMotAvantObjetInterface', reduction, revue, objet)
    else:
        return render(request, 'AmeliorText/Explor/ExplorBase/AbsenceDroit.html')



def AfficheNoteDiscontinu(request, reduction, revue):
    '''
    Méthode qui écrit dans un fichier les notes détectés à l'aide la méthode de la fenêtre graphique 
    présentant des "discontinuités". Ces discontinuités correspondent à des coupures
    dans les intervalles de mots associés aux notes.
    '''
    error, revuerealname, autrerevue = ExplicitRevue(revue)
    if error:
        return render(request, 'AmeliorText/General/home.html')

    FichierResult1 = settings.RESULT_PRETRAIT_DIR + "/AmeliorText/"\
                    + reduction + "/"\
                    + reduction + revue + "NoteDiscontinuContenu.txt"
    FichierResult2 = settings.RESULT_PRETRAIT_DIR + "/AmeliorText/" \
                     + reduction + "/" \
                     + reduction + revue + "NoteDiscontinuPourcent.txt"

    error, RefNotes, CompteurGeneral, CompteurDiscon = \
        AfficheCoordGraphDiscontinuMaxDo(FichierResult1, FichierResult2, reduction, "note", revue)
    if error:
        return render(request, 'AmeliorText/General/home.html')

    PourcentDiscon = round(CompteurDiscon / CompteurGeneral, 2)
    NbreNotes = len(RefNotes)
    RefNotesDeb = []
    RefNotesFin = []
    MarqueurLimitePage = False
    if NbreNotes > 200:
        RefNotesDeb = RefNotes[0:100]
        RefNotesFin = RefNotes[-100:]
        MarqueurLimitePage = True
    context = {"NbreNotes": NbreNotes,"reduction": reduction,"revue":revue, "PourcentDiscon":PourcentDiscon,
               "RefNotes": RefNotes, "RefNotesDeb":RefNotesDeb, "RefNotesFin": RefNotesFin,
               "MarqueurLimitePage":MarqueurLimitePage, "revuerealname": revuerealname}
    return render(request, 'AmeliorText/Explor/Note/NoteDiscontinu.html', context)




################# EXPLOR FIN DOC #####################

def LastPageCenter(request, reduction, revue):
    '''
        Méthode qui écrit dans un fichier
        les lignes centrées de la dernière page
        '''

    error, revuerealname, autrerevue = ExplicitRevue(revue)
    if error:
        return render(request, 'AmeliorText/General/home.html')


    FichierResult = settings.RESULT_PRETRAIT_DIR + "/AmeliorText/" \
                    + reduction + "/" \
                    + reduction + revue + "LigneCenterLastPage.txt"
    error, docs_concerne_par_ligne_centre, LignesCentres = AfficheLigneCenterLastPageDo(FichierResult, reduction, revue)
    if error:
        return render(request, 'AmeliorText/General/home.html')

    NbresDocsAvecLigneCenterLastPage = len(docs_concerne_par_ligne_centre)

    # https://stackoverflow.com/questions/2415865/iterating-through-two-lists-in-django-templates
    mylist = zip(docs_concerne_par_ligne_centre, LignesCentres)
    context = {"mylist":mylist, "NbresDocsAvecLigneCenterLastPage": NbresDocsAvecLigneCenterLastPage,
               "reduction": reduction, "revue":revue}
    return render(request, 'AmeliorText/Explor/FinDoc/LastPageCentrer.html', context)


def DetectDebutLigne(request, reduction, revue):
    '''
    Méthode qui detecte les "Manuscrit reçu le ... ""
    '''

    error, revuerealname, autrerevue = ExplicitRevue(revue)
    if error:
        return render(request, 'AmeliorText/General/home.html')

    FichierResult = settings.RESULT_PRETRAIT_DIR + "/AmeliorText/" \
                    + reduction + "/" \
                    + reduction + revue + "Manuscrit"+ ".txt"

    error,docs_concerne_par_expression, LignesAvecExpressionDebut = PresenceDebutLigneDo(FichierResult, reduction, revue)
    if error:
        return render(request, 'AmeliorText/General/home.html')

    mylist = zip(docs_concerne_par_expression, LignesAvecExpressionDebut)
    NbresDocConcerne = len(docs_concerne_par_expression)
    context = {"mylist": mylist, "NbresDocConcerne": NbresDocConcerne,"reduction": reduction, "revue":revue}

    return render(request, 'AmeliorText/Explor/FinDoc/ExpressionDebutLigneResult.html',context)




####################### EXPLOR CEDILLE ##############


def AfficheMotCedilleAvtApres(request):


    FichierResult = settings.DATA_DIR + '/Dico/DicoCedilleAvtApres.txt'
    MotCedilleAvtApres = VerifAvantApresCedilleExist(FichierResult)
    MotCedilleAvtApres.sort(reverse=True)
    NbreMotCedilleAvtApres = len(MotCedilleAvtApres)
    context = {"MotCedilleAvtApres":MotCedilleAvtApres,"NbreMotCedilleAvtApres":NbreMotCedilleAvtApres}

    return render(request, 'AmeliorText/Explor/Cedille/AfficheMotCedilleAvtApres.html', context)



################### EXPLOR AND TRAIT AUTO ###############


def ExplorTraitHome(request, objet, reduction_id):
    """ Mix Explor et Trait pour traitement sur la même page"""

    if request.method == 'POST':

        if 'Effectuer' in request.POST:
            error, reduction, revuered, fonction, agreg, ref = TraitExplorHome(request, objet)
            if not error:
                if fonction == "PresenceMotAvantObjetInterface":
                    url = reverse(agreg, kwargs={'reduction': reduction, 'revue': revuered, "objet": objet})
                else:
                    url = reverse(agreg, kwargs={'reduction': reduction, 'revue': revuered, 'ref':ref})
                return HttpResponseRedirect(url)
            else:
                return render(request, 'AmeliorText/General/home.html')

        if 'Effectuer2' in request.POST:

            userencours = -1
            if request.user.is_authenticated:
                userencours = request.user.id

            test = CorpusEtude.objects.filter(id=reduction_id)
            if not test.exists():
                return render(request, 'DelimitCorpus/ErrorCorpusNotExist.html')

            CEencours = test[0]

            # si c'est un super utilisateur ou si l'utilisateur à les droit sur cette réduction
            if request.user.is_superuser or (str(userencours) in CEencours.user_restrict.split(",")):
                FormEnCours = DicModelFormRefInsert(objet, "formulaire")
                recupdonnees = FormEnCours(request.POST)
                if recupdonnees.is_valid():
                    donnees = recupdonnees.cleaned_data

                    ListMots, RenduPluriel = TraitHomeTrait(request, objet, reduction_id, CEencours, donnees, recupdonnees)

                    context = {"donnees": donnees, "reduction": CEencours.nom, "ListMots": ListMots,
                               "RenduPluriel": RenduPluriel, "objet": objet}

                    if objet == "Annexe" or objet == "Titre123" or objet == "FinMot" or objet == "FinLigne":
                        return render(request, 'AmeliorText/ExplorTrait/' + objet + "/SuccessTrait" + objet + '.html',
                                      context)
                    else:
                        return render(request, 'AmeliorText/TraitA/' + objet + '/SuccessTrait' + objet + '.html',
                                      context)
                # formulaire invalide
                else:
                    context = {"form":recupdonnees}
                    return render(request, 'AmeliorText/Explor/ExplorBase/AbsenceDroit.html', context)


            # si l'utilisateur n'a pas les droits
            else:
                # verifie si existe déjà une transformation sur l'élément pour cette réduction
                RenduPluriel = DicModelFormRefInsert(objet, "RenduPluriel")
                ModelEnCours = DicModelFormRefInsert(objet, "modele")
                TestExistTransform = ModelEnCours.objects.filter(CorpusEtudeRef=CEencours)
                if TestExistTransform.count() == 1:
                    AncienneReductionElt = TestExistTransform[0]
                    context = {"AncienneReductionElt": AncienneReductionElt, "reduction": CEencours.nom,
                               "RenduPluriel": RenduPluriel, "objet": objet}
                    if objet == "Annexe" or objet == "Titre123" or objet == "FinMot" or objet == "FinLigne":
                        return render(request, 'AmeliorText/ExplorTrait/' + objet + "/AnnuleTrait" + objet + '.html',
                                      context)
                    else:
                        return render(request, 'AmeliorText/Trait/' + objet + '/AnnuleTrait' + objet + '.html',
                                      context)
                else:
                    context = {"reduction": reduction_id, "RenduPluriel": RenduPluriel, "objet": objet}
                    return render(request, 'AmeliorText/TraitA/TraitBase/ImpossibleTraitBase.html', context)

        if 'Supprimer' in request.POST:

            reduc = CorpusEtude.objects.get(id=reduction_id)
            url = reverse("AmeliorText:Suppr", kwargs={'reduction': reduc.nom, "objet": objet})
            return HttpResponseRedirect(url)



    TraitExplorSepare = ["Titre", "Resume", "MotCle", "HautDePage", "BasDePage", "Note", "Figure", "Biblio", "FinDoc",
                         "Cedille"]
    TraitExplorEnsemble = ["Annexe", "Titre123", "FinMot", "FinLigne"]

    if objet in TraitExplorEnsemble:
        reductionsselect, PossibleChange, CorpusExist, ChangeExist, MaqueurPartieDoc, MaqueurPartieMot, RenduPluriel, \
        Numero, fctselect, revueselect =  PrepaExplorTraitHome1(request, objet)

        # a partir du home, appelle avec reduction_id = 0
        # correspond demande de nouvelle réduction
        # sinon, on cherche si réduction existe bien et si user a un accès
        demande = None
        if reduction_id != 0:
            test = CorpusEtude.objects.filter(id=reduction_id)
            if not test.exists():
                return render(request, 'DelimitCorpus/ErrorCorpusNotExist.html')

            demande = test[0]
            if demande not in reductionsselect:
                return render(request, 'DelimitCorpus/ErrorCorpusNoAccess.html')

        CorpusExist, PossibleChange, ChangeExist, form = \
            PrepaTraitHome2(request, objet, reduction_id, demande, reductionsselect, CorpusExist, PossibleChange,
                        ChangeExist)


        context = {"reductions": reductionsselect, "fctselect": fctselect, "objet": objet, "revueselect": revueselect,
                   "form": form, "PossibleChange": PossibleChange, "ChangeExist": ChangeExist, "CorpusExist": CorpusExist,
                   "reduction_id": reduction_id, "RenduPluriel": RenduPluriel, "Numero":Numero,"MaqueurPartieDoc":MaqueurPartieDoc,
                   "MaqueurPartieMot":MaqueurPartieMot}
        return render(request, 'AmeliorText/ExplorTrait/' + objet + '/ExpTrA' + objet + 'Home.html', context)

    elif objet in TraitExplorSepare:
        return redirect('AmeliorText:ExplorHome', objet)
    else:
        return redirect('AmeliorText:home')


###################TRAIT AUTO ###############


def TraitHome(request, objet, reduction_id):


    if request.method == 'POST':

        if 'Effectuer' in request.POST:

            userencours = -1
            if request.user.is_authenticated:
                userencours = request.user.id

            test = CorpusEtude.objects.filter(id=reduction_id)
            if not test.exists():
                return render(request, 'DelimitCorpus/ErrorCorpusNotExist.html')

            CEencours = test[0]

            # si c'est un super utilisateur ou si l'utilisateur à les droit sur cette réduction
            if request.user.is_superuser or (str(userencours) in CEencours.user_restrict.split(",")):
                FormEnCours = DicModelFormRefInsert(objet, "formulaire")
                recupdonnees = FormEnCours(request.POST)
                if recupdonnees.is_valid():
                    donnees = recupdonnees.cleaned_data
                    ListMots, RenduPluriel = TraitHomeTrait(request, objet, reduction_id, CEencours, donnees, recupdonnees)

                    context = {"donnees": donnees, "reduction": CEencours.nom, "ListMots":ListMots, "RenduPluriel": RenduPluriel, "objet": objet}

                    if objet == "Annexe"  or objet == "Titre123" or objet == "FinMot" or objet == "FinLigne":
                            return render(request,'AmeliorText/ExplorTrait/' + objet + "/SuccessTrait" + objet + '.html',context)
                    else:
                        return render(request, 'AmeliorText/TraitA/' + objet + '/SuccessTrait' + objet + '.html',context)

            # si l'utilisateur n'a pas les droits
            else:
                # verifie si existe déjà une transformation sur l'élément pour cette réduction
                ModelEnCours = DicModelFormRefInsert(objet, "modele")
                RenduPluriel = DicModelFormRefInsert(objet, "RenduPluriel")
                TestExistTransform = ModelEnCours.objects.filter(CorpusEtudeRef =CEencours)
                if TestExistTransform.count() == 1:
                    AncienneReductionElt = TestExistTransform[0]
                    context = {"AncienneReductionElt": AncienneReductionElt, "reduction": CEencours.nom, "RenduPluriel": RenduPluriel, "objet": objet}
                    if objet == "Annexe"  or objet == "Titre123" or objet == "FinMot" or objet == "FinLigne":
                        return render(request,'AmeliorText/ExplorTrait/' + objet + "/AnnuleTrait" + objet + '.html',context)
                    else:
                        return render(request, 'AmeliorText/Trait/' + objet + '/AnnuleTrait' + objet + '.html',
                                  context)
                else:
                    context = {"reduction": reduction_id, "RenduPluriel": RenduPluriel, "objet": objet}
                    return render(request, 'AmeliorText/TraitA/TraitBase/ImpossibleTraitBase.html', context)


        if 'Supprimer' in request.POST:
            reduc = CorpusEtude.objects.get(id=reduction_id)
            url = reverse("AmeliorText:Suppr", kwargs={'reduction': reduc.nom, "objet": objet})
            return HttpResponseRedirect(url)



    TraitExplorSepare = ["Titre", "Resume", "MotCle", "HautDePage", "BasDePage", "Note", "Figure", "Biblio", "FinDoc",
                         "Cedille"]
    TraitExplorEnsemble = ["Annexe", "Titre123", "FinMot", "FinLigne"]

    if objet in TraitExplorEnsemble:
        return redirect('AmeliorText:ExplorTraitHome', objet, 0)

    elif objet in TraitExplorSepare:
        reductionsselect, PossibleChange, CorpusExist, ChangeExist, MaqueurPartieDoc, MaqueurPartieMot, RenduPluriel, Numero\
            = PrepaTraitHome1(request, objet)

        # a partir du home, appelle avec reduction_id = 0
        # correspond demande de nouvelle réduction
        # sinon, on cherche si réduction existe bien et si user a un accès
        demande = None
        if reduction_id != 0:
            test = CorpusEtude.objects.filter(id=reduction_id)
            if not test.exists():
                return render(request, 'DelimitCorpus/ErrorCorpusNotExist.html')

            demande = test[0]
            if demande not in reductionsselect:
                return render(request, 'DelimitCorpus/ErrorCorpusNoAccess.html')

        CorpusExist, PossibleChange, ChangeExist, form =\
            PrepaTraitHome2(request, objet, reduction_id, demande, reductionsselect,CorpusExist,PossibleChange,ChangeExist)


        context = {"reductions": reductionsselect, "objet":objet,"form":form,
                   "PossibleChange":PossibleChange, "ChangeExist":ChangeExist,"CorpusExist":CorpusExist,
                   "reduction_id":reduction_id, "RenduPluriel": RenduPluriel,"Numero":Numero,
                   "MaqueurPartieDoc":MaqueurPartieDoc,"MaqueurPartieMot":MaqueurPartieMot}
        return render(request, 'AmeliorText/TraitA/' + objet + '/TrA' + objet + 'Home.html', context)

    else:
        return redirect('AmeliorText:home')



#################### SUPPR ALL ################################

def Suppr(request, reduction, objet):
    # récupère le numéro d'user si l'utilisateur est connecté
    userencours = -1
    if request.user.is_authenticated:
        userencours = request.user.id

    RenduPluriel = DicModelFormRefInsert(objet, "RenduPluriel")

    Test = CorpusEtude.objects.filter(nom=reduction)
    if Test.exists():
        CEencours = Test[0]
    else:
        context = {"reduction": reduction, "RenduPluriel": RenduPluriel, "objet": objet}
        return render(request, 'AmeliorText/TraitA/TraitBase/ImpossibleSupprBase.html', context)

    # si c'est un super utilisateur ou si l'utilisateur à les droit sur cette réduction
    if request.user.is_superuser or (
        userencours in CEencours.user_restrict.split(",")):

        TraitSuppr(objet, reduction, CEencours)

        context = {"reduction": reduction, "RenduPluriel": RenduPluriel, "objet": objet}
        return render(request, 'AmeliorText/TraitA/TraitBase/SuccessSupprBase.html', context)
    else:
        context = {"reduction": reduction,"RenduPluriel": RenduPluriel, "objet": objet}
        return render(request, 'AmeliorText/TraitA/TraitBase/ImpossibleSupprBase.html', context)



   ###########################  TRAIT MANUEL  #################


def ExceptHome(request, objet):

    if request.method == 'POST':
        reduction = request.POST.get('reduc')
        choice = request.POST.get('choice')

        if choice == "RemoveTransformer":
            url = reverse("AmeliorText:RemoveTransformer", kwargs={'reduction': reduction, "objet": objet})
            return HttpResponseRedirect(url)

        elif choice == "AddTransformer":
            url = reverse("AmeliorText:AddTransformer", kwargs={'reduction': reduction, "objet": objet})
            return HttpResponseRedirect(url)

        elif choice == "ConsultEltExcept":
            url = reverse("AmeliorText:ConsultEltExcept", kwargs={'reduction': reduction, "objet": objet})
            return HttpResponseRedirect(url)

        elif choice == "RemoveDoc":
            url = reverse("AmeliorText:RemoveDoc", kwargs={'reduction': reduction, "objet": objet})
            return HttpResponseRedirect(url)

        elif choice == "ConsultDocExcept":
            url = reverse("AmeliorText:ConsultDocExcept", kwargs={'reduction': reduction, "objet": objet})
            return HttpResponseRedirect(url)

        else:
            return render(request, 'AmeliorText/General/home.html')


    reductionsall = CorpusEtude.objects.all().order_by("pk")
    reductionsselect = SelectReducFctUser(request, reductionsall)
    RenduPluriel = DicModelFormRefInsert(objet,"RenduPluriel")
    Numero = DicModelFormRefInsert(objet,"numero")
    context = {"reductions": reductionsselect, "objet": objet, "RenduPluriel": RenduPluriel, "Numero": Numero}
    return render(request, 'AmeliorText/TraitM/TrMHome.html', context)



def RemoveTransformer(request, reduction, objet):
    '''Fonction permettant d'enlever des éléments par rapport au nettoyage automatique
    Le coeur est RemoveEltAllDo dans OrgaScript.TraitMFct'''

    if request.method == 'POST':
        TestText = request.POST.get("Text1")
        # récupère le numéro d'user si l'utilisateur est connecté
        userencours = -1
        if request.user.is_authenticated:
            userencours = request.user.id
        test_user_vn = userencours in CorpusEtude.objects.get(nom=reduction).user_restrict.split(",")

        if 'Effectuer' in request.POST and (request.user.is_superuser or test_user_vn):
            # controle qu'il n'y au moins une virgule dans chaque élément
            decoup = TestText.split("\n")
            controlform = True
            for elt in decoup:
                if not "," in elt:
                    controlform = False
            if controlform:
                success, echec, malformat = RemoveEltAllDo(reduction,
                                                           objet,
                                                           TestText.split("\n"))

                context = {"reduction": reduction, "success": success, "echec": echec,
                           "malformat": malformat}
                return render(request, 'AmeliorText/TraitM/RemoveEltResult.html', context)

        if 'Retour' in request.POST:
            return redirect('AmeliorText:ReDispatch', 'TraitM', objet)

    context = {"reduction": reduction}
    return render(request, 'AmeliorText/TraitM/RemoveEltInterface.html', context)



def AddTransformer(request, reduction, objet):
    '''Fonction permettant d'enlever des éléments par rapport au nettoyage automatique
    Le coeur est AddEltAllDo dans OrgaScript.TraitMFct'''

    if request.method == 'POST':
        TestText = request.POST.get("Text2")
        # récupère le numéro d'user si l'utilisateur est connecté
        userencours = -1
        if request.user.is_authenticated:
            userencours = request.user.id
        test_user_vn = userencours in CorpusEtude.objects.get(nom=reduction).user_restrict.split(",")
        if 'Effectuer' in request.POST and (request.user.is_superuser or test_user_vn):
            success, echec, malformat, existedeja = AddEltAllDo(reduction,
                                                                objet,
                                                                TestText.split("\n"))
            context = {"reduction": reduction, "success": success, "echec": echec,
                       "malformat": malformat, "existedeja": existedeja}
            return render(request, 'AmeliorText/TraitM/AddEltResult.html', context)
        if 'Retour' in request.POST:
            return redirect('AmeliorText:ReDispatch', 'TraitM', objet)

    context = {"reduction": reduction}
    return render(request, 'AmeliorText/TraitM/AddEltInterface.html', context)


def RemoveDoc(request, reduction, objet):
    '''Fonction permettant d'enlever des documents d'un corpus
    Le coeur est RemoveDocDo dans OrgaScript.TraitMFct'''

    if request.method == 'POST':
        TestText = request.POST.get("Text3")
        # récupère le numéro d'user si l'utilisateur est connecté
        userencours = -1
        if request.user.is_authenticated:
            userencours = request.user.id

        Test = CorpusEtude.objects.filter(nom=reduction)
        if Test.exists():
            CEencours = Test[0]
        else:
            return render(request, 'AmeliorText/General/home.html')

        test_user_vn = userencours in CEencours.user_restrict.split(",")
        if 'Effectuer' in request.POST and (request.user.is_superuser or test_user_vn):
            success, echec, malformat, existedeja = RemoveDocDo(reduction,objet,TestText.split("\n"))
            context = {"reduction": reduction, "success": success, "echec": echec,
                       "malformat": malformat, "existedeja": existedeja}
            return render(request, 'AmeliorText/TraitM/RemoveDocResult.html', context)
        if 'Retour' in request.POST:
            return redirect('AmeliorText:ReDispatch', 'TraitM', objet)

    context = {"reduction": reduction}
    return render(request, 'AmeliorText/TraitM/RemoveDocInterface.html', context)



def ConsultEltExcept(request, reduction, objet):
    '''Fonction permettant de consulter les éléments
    qui ont été précédemment enlevés ou ajoutés
    '''

    Test = CorpusEtude.objects.filter(nom=reduction)
    if Test.exists():
        CEencours = Test[0]
    else:
        return render(request, 'AmeliorText/General/home.html')

    removeall = AllExceptRemove.objects.filter(type=objet).filter(CorpusEtudeRef=CEencours)
    addall = AllExceptAdd.objects.filter(type=objet).filter(CorpusEtudeRef=CEencours)
    context = {"reduction": reduction, "removeall": removeall, "addall": addall, "objet": objet}
    return render(request, 'AmeliorText/TraitM/ConsultEltExcept.html', context)



def ConsultDocExcept(request, reduction, objet):
    '''Fonction permettant de consulter les documents
    qui ont été précédemment enlevés ou ajoutés
    '''

    Test = CorpusEtude.objects.filter(nom=reduction)
    if Test.exists():
        CEencours = Test[0]
    else:
        return render(request, 'AmeliorText/General/home.html')

    docremove = DocRemove.objects.filter(type=objet).filter(CorpusEtudeRef=CEencours)
    context = {"reduction": reduction, "docremove":docremove, "objet": objet}
    return render(request, 'AmeliorText/TraitM/ConsultDocExcept.html', context)



################# RESUME TRAITEMENT EFFECTUE ##################

def SyntheseHome(request):

    if request.method == 'POST':
        if 'Effectuer' in request.POST:

            reduction = request.POST.get('red')

            Test = CorpusEtude.objects.filter(nom=reduction)
            if Test.exists():
                CEencours = Test[0]
            else:
                return render(request, 'AmeliorText/General/home.html')

            # récupère le numéro d'user si l'utilisateur est connecté
            userencours = -1
            if request.user.is_authenticated:
                userencours = request.user.id

            test_user_vn = userencours in CorpusEtude.objects.get(nom=reduction).user_restrict.split(",")

            if request.user.is_superuser or test_user_vn:
                TraitSyntheseHome(reduction, CEencours)
                context = {"NomCorpusExtract": CEencours.nom}
                return render(request, 'AmeliorText/General/ExtractFin.html', context)


    reductionsall = CorpusEtude.objects.all().order_by("pk")
    reductionsselect = []
    if request.user.is_authenticated:
        for reduction in reductionsall:
            if request.user.is_superuser or (str(request.user.id) in reduction.user_restrict.split(",")):
                reductionsselect.append(reduction)
    context = {"reductions": reductionsselect}
    return render(request, 'AmeliorText/General/7Synthese.html',context)


def SyntheseTraitement(request,reduction):

    Test = CorpusEtude.objects.filter(nom=reduction)
    if Test.exists():
        CEencours = Test[0]
    else:
        return render(request, 'AmeliorText/General/home.html')

    objets, ListRed, ListPluriel, ListCheckTransform, ListTransform, ListEltRemove, ListEltAdd, ListDocRemove \
        = TraitSyntheseTraitement(CEencours)

    # cree le context
    MegaZip = zip(objets,ListRed,ListPluriel,ListCheckTransform,ListTransform,ListEltRemove,ListEltAdd,ListDocRemove)
    context = {"reduction": reduction, "MegaZip":MegaZip}

    return render(request, 'AmeliorText/General/SyntheseTraitement.html', context)



################ DOWNLOAD GENERAL ##############################

def Download(request, sujet, reduction, revue, extension):
    '''Pour telecharger un fichier'''
    FichierResult = settings.RESULT_PRETRAIT_DIR + "/AmeliorText/"\
                    + reduction + "/"\
                    + reduction + revue + sujet + "." + extension

    if os.path.isfile(FichierResult):
        response = HttpResponse(open(FichierResult, 'rb').read())
        if extension=="txt" or extension=="csv":
            response['Content-Type'] = 'text/plain'
        # cas image
        else:
            response['Content-Type'] = 'image/' + extension
        response['Content-Disposition'] = 'attachment; filename=' + reduction + revue + sujet + "." + extension
        return response
    else:
        return render(request, 'AmeliorText/General/home.html')


def DownloadDico(request, fichier):
    '''Pour telecharger un fichier de dico'''
    FichierResult = settings.DATA_DIR + "/Dico/Dico"\
                    + fichier + '.txt'
    if os.path.isfile(FichierResult):
        response = HttpResponse(open(FichierResult, 'rb').read())
        response['Content-Type'] = 'text/plain'
        response['Content-Disposition'] = 'attachment; filename=' + fichier + '.txt'
        return response
    else:
        return render(request, 'AmeliorText/General/home.html')



