
from django.conf import settings
from AllApps.Traitement.Semantique.TableauEmb.models import  Expe
from .. models import GloveRCluster, Word2VecRCluster, FastTextRCluster
from .amont import ModelFormInit, LectureResult, CalculDiagrammeTaille
from AllApps.Traitement.Semantique.TableauEmb.periph.amont import SelectModelFctUser,SelectResultFctUser,\
    CreateDictFromExpe, DiffDic, AllModes



def ParaInitialResult():
    DicInitParaResult = {"terme": "espace",
                         "nresult": 25,
                         "user_restrict2": "0",
                         "methode_clustering":"Kmeans",
                         "ncluster":4,
                         "link":True,
                         "color_singleton":True}
    return DicInitParaResult



def InitModelForResult(request, Modelc, DicInitModelD, DicInitFormD):
    DicInitParaResult = ParaInitialResult()

    results = DicInitModelD["resultat"].objects.filter(modelc_id=Modelc.id).all()
    resultselect = SelectResultFctUser(request, results)
    if len(resultselect) > 0:
        lastresult = resultselect[-1]
        lastepoque = lastresult.choixepoque
        lastrevue = lastresult.choixrevue

    form = DicInitFormD["initial"](instance=Modelc)

    AccesToCalcul = True
    AccesToSave = False

    if len(resultselect) > 0:
        form2 = DicInitFormD["resultatdeb"](instance=lastresult, epoques=Modelc.epoque, epoque1=lastepoque,
                                         revues=Modelc.revue, revue1=lastrevue)
    else:
        form2 = DicInitFormD["resultatdeb"](initial=DicInitParaResult, epoques=Modelc.epoque, revues=Modelc.revue)

    results = DicInitModelD["resultat"].objects.filter(modelc_id=Modelc.id)
    graph = "no"

    return form, form2, results, graph, AccesToSave, AccesToCalcul




def InitModelResultBeforeSave(request, mode, modele_id, terme, nresult, revue, epoque, user, methode_clustering, ncluster, link, color_singleton):
    DicInitModelD, DicInitFormD = ModelFormInit(mode)
    modelsc = DicInitModelD["initial"].objects.all()
    modelscselect = SelectModelFctUser(request, modelsc)

    DicModelc = DicInitModelD["initial"].objects.get(id=modele_id)
    form = DicInitFormD["initial"](instance=DicModelc)

    # l'option user_restrict2 n'est utilisé que par les super_user
    # permet de restreindre l'affichage des résultats à des utilisateurs choisis !
    form2 = DicInitFormD["resultatdeb"](
        data={"terme": terme, "nresult": nresult, "user_restrict2": user,
              "methode_clustering": methode_clustering, "ncluster": ncluster, "link": link, "choixrevue": revue,
              "choixepoque": epoque, "color_singleton":color_singleton},
        epoques=DicModelc.epoque, revues=DicModelc.revue, revue1=revue, epoque1=epoque)

    AccesToSave = True
    AccesToCalcul = True
    graph = "yes"

    results = DicInitModelD["resultat"].objects.filter(modelc_id=modele_id)
    allmodes = AllModes()

    return form, modelscselect, allmodes, form2, results, AccesToSave, AccesToCalcul, graph




def InitResult(request, mode, Modelc, DicInitModelD, DicInitFormD, result_id):

    form = DicInitFormD["initial"](instance=Modelc)

    AllEpoquesModele = Modelc.epoque
    AllRevueModele = Modelc.revue

    results = DicInitModelD["resultat"].objects.filter(modelc_id=Modelc.id)
    DicResultc = DicInitModelD["resultat"].objects.get(id=result_id)

    epoqueencours = DicResultc.choixepoque
    revueencours = DicResultc.choixrevue

    form2 = DicInitFormD["resultatdeb"](instance=DicResultc, epoques=AllEpoquesModele, revues=AllRevueModele,
                                     epoque1=epoqueencours, revue1=revueencours)

    # disabled all field form 2
    for fieldname in form2.fields:
        form2.fields[fieldname].disabled = True

    pathresult = settings.RESULT_SEMANTIC_DIR + "/Cluster/" + mode + "/save/" + DicResultc.nomresult

    # charges les noeuds et les liens
    nodes_list,edges_list = LectureResult(pathresult)

    AccesToCalcul = False
    AccesToSave = False
    graph = "yes"

    # Utile pour qu'un utlisateur qui sauve des résultats puisse aussi les supprimer lui même
    # la gestion de la permission se trouve dans result.html
    ResultSpeUser = False
    if DicResultc.user_restrict2.isdigit():
        if int(DicResultc.user_restrict2) == request.user.id:
            ResultSpeUser = True

    # pour le diagramme
    graphic = ""
    taillediagramme = 0
    path_result_transfo = ""

    methode_clustering = DicResultc.methode_clustering
    if methode_clustering == "saut moyen" or methode_clustering == "saut minimal" or methode_clustering == "saut maximal":
        path_result_transfo = "save---" + DicResultc.nomresult + '.png'
        taillediagramme = CalculDiagrammeTaille(DicResultc.nresult, methode_clustering)

    return form, form2, results, nodes_list, edges_list, AccesToSave, AccesToCalcul, \
           ResultSpeUser, taillediagramme, methode_clustering, graphic, graph, path_result_transfo