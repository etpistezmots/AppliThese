import os
from django.shortcuts import render, redirect
from django.conf import settings
from .forms import CountOccForm, CountOccRedForm
from .models import CountOcc
from .periph import RecupDataOcc,InitOccResultBeforeSave,InitOccInterface,InitOccResult,SupprOneOcc, SupprMultiOcc
from .core import CountOccSimple, CountOccByAuthor
from AllApps.Traitement.Semantique.TableauEmb.periph.amont import SelectModelFctUser
from AllApps.Traitement.Semantique.TableauEmb.periph.df2html import transform, transformquanti
from AllApps.PreTraitement.Persee.FinaliseCorpus.models import CorpusFin


def home(request):
    return render(request, 'TableauOcc/home.html')


def Interface(request, mode):
    if request.method == 'POST':

        if 'calcul' in request.POST:

            if mode != "Simple" and mode != "Auteur":
                return render(request, 'TableauOcc/Error/ModeNotExist.html')

            formToSave = CountOccRedForm(data=request.POST)

            if formToSave.is_valid():
                donnees = formToSave.cleaned_data
                if mode == "Simple":
                    df = CountOccSimple(donnees)
                    table = transformquanti(df)
                if mode == "Auteur":
                    df = CountOccByAuthor(donnees,25)
                    table = transform(df)


                PresenceNewResult, PossibleSave, corpus, termelast, revuelast, epoquelast, results, idlast =\
                    InitOccResultBeforeSave(request, mode, donnees)

                context = {"form": formToSave, "PresenceNewResult": PresenceNewResult, "PossibleSave": PossibleSave, "table":table,
                           "corpus":corpus,"termelast":termelast,"revuelast":revuelast,"epoquelast":epoquelast,
                           "results":results, "idlast":idlast,"mode":mode}

                return render(request, 'TableauOcc/Interface.html', context)


            else:
                PresenceNewResult = False
                context = {"form": formToSave, "PresenceNewResult":PresenceNewResult,"mode":mode}
                return render(request, 'TableauOcc/Interface.html', context)



        if 'save' in request.POST:

            terme, corpus, epoque, revue, table, name = RecupDataOcc(request)

            if request.user.id is not None:
                idencours = str(request.user.id)
            else:
                return render(request, 'TableauOcc/Error/ImpossibleSave.html')

            # permet d'enregistrer des résultats pour un utilisateur donné
            if request.user.is_superuser:
                idencours = request.POST.get("idlast")

            try :
                CorpusFinEnCours = CorpusFin.objects.get(nom=corpus)
            except:
                return render(request, 'TableauOcc/Error/ImpossibleSave.html')

            formToSave = CountOccForm(data={"terme":terme, "revue":revue,"epoque":epoque,"user_restrict":idencours,
                                            "CorpusFinRef":CorpusFinEnCours.id, "nomresult":name, "mode":mode})

            if formToSave.is_valid():

                lv = formToSave.save()

                # enregistre dans un fichier la table
                pathresult = settings.RESULT_LEXICAL_DIR + "/TableauOcc/" + mode
                if not os.path.exists(pathresult):
                    os.makedirs(pathresult)
                filename = pathresult + "/" + str(lv.nomresult) + ".txt"
                with open(filename, 'w') as f:
                    f.write(table)
                return redirect('TableauOcc:Result', mode, lv.id)

            else:
                context= {"form":formToSave}
                return render(request, 'TableauOcc/Error/InvalidForm.html', context)


    ######## Test et prepa html base ###########
    if mode!= "Simple" and mode !="Auteur":
        return render(request, 'TableauOcc/Error/ModeNotExist.html')

    testcorpus = CorpusFin.objects.all()
    if not testcorpus:
        return render(request, 'TableauOcc/Error/NoCorpus.html')

    form, results = InitOccInterface(request, mode)
    context = {"form":form,"results":results,"mode":mode}
    return render(request, 'TableauOcc/Interface.html', context)



def Result(request, mode, resultid):
    if request.method == 'POST':
        if ('SupprimerOneResult' in request.POST):
            return redirect('TableauOcc:DeleteOneOcc', mode, resultid)

        if ('SupprimerMultiResults' in request.POST):
            return redirect('TableauOcc:DeleteMultiOcc')

        if ('NewResult' in request.POST):
            return redirect('TableauOcc:Interface', mode)

        if 'RetourInterface' in request.POST:
            return redirect('TableauOcc:CountOccInterface', mode)

    ######## Test et prepa html base ###########
    if mode!= "Simple" and mode !="Auteur":
        return render(request, 'TableauOcc/Error/ModeNotExist.html')

    TestAlreadyExist = CountOcc.objects.filter(mode= mode, id= resultid)
    if TestAlreadyExist.exists():
        Resultc = TestAlreadyExist[0]
        resultsAll = CountOcc.objects.filter(mode=mode)
        results= SelectModelFctUser(request, resultsAll)

        AutreResult = False
        if len(results)>1:
            AutreResult = True

        if Resultc in results:
            table, UnSeulTerme, Terme, termesList, corpus, MyForm, ResultSpeUser =\
                InitOccResult(request,mode, Resultc)

            context = {"table":table, 'UnSeulTerme':UnSeulTerme, "Terme":Terme, "termesList":termesList,
                       "corpus": corpus, "results":results,"resultid":resultid,
                       "MyForm":MyForm,"mode":mode,"ResultSpeUser":ResultSpeUser,"AutreResult":AutreResult}
            return render(request, 'TableauOcc/Result.html', context)
        else:
            return render(request, 'TableauOcc/Error/ResultNoAccess.html')

    else:
        return render(request, 'TableauOcc/Error/ResultNotExist.html')


def DeleteOneOcc(request, mode, resultid):

    # test mode
    if mode != "Simple" and mode != "Auteur":
        return render(request, 'TableauOcc/Error/ModeNotExist.html')

    if request.user.id is None:
        return render(request, 'TableauEmb/Error/SupprImpossible.html')

    #test result exist
    TestAlreadyExist = CountOcc.objects.filter(id=resultid, mode=mode)
    if TestAlreadyExist.exists():

        # test user access
        Resultc =  TestAlreadyExist[0]
        userexpe = Resultc.user_restrict

        if request.user.is_superuser or (str(request.user.id) in userexpe.split(",")):
            SupprOneOcc(mode, Resultc)
            return redirect('TableauOcc:Interface', mode)
        else:
            return render(request, 'TableauEmb/Error/SupprImpossible.html')

    else:
        return render(request, 'TableauOcc/Error/ResultNotExist.html')



def DeleteMultiOcc(request):
    if request.method == 'POST':
        if 'Supprimer' in request.POST and request.user.is_superuser:
            SupprMultiOcc(request)
            return redirect('TableauOcc:Interface', 'Simple')

        if 'Retour' in request.POST:
            return redirect('TableauOcc:Interface', 'Simple')

    ########## INIT ##############
    if request.user.is_superuser:
        results = CountOcc.objects.all()
        context = {"results":results}
        return render(request, 'TableauOcc/SupprMultiOcc.html',context)
    else:
        return render(request, 'TableauOcc/Error/SupprImpossible.html')
