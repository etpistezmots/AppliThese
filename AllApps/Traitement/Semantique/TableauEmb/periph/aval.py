import shutil, os
from django.conf import settings
from .prepaaffiche import ModelFormInit
from AllApps.Traitement.Semantique.TableauEmb.models import Word2VecR, GloveR, FastTextR
from AllApps.Traitement.Semantique.ReseauExplore.models import Word2VecRExplo, GloveRExplo, FastTextRExplo
from AllApps.Traitement.Semantique.Cluster.models import Word2VecRCluster, GloveRCluster, FastTextRCluster
from AllApps.Traitement.Semantique.DiachroGroup.models import Word2VecDiachro, GloveDiachro, FastTextDiachro

def SupprModele(mode, modele_id):
    DicInitModelDactuel, DicInitFormDactuel = ModelFormInit(mode)
    DicActuel = DicInitModelDactuel["initial"].objects.get(id=modele_id)

    # Efface toutes les expes associées au modèle en fonction mode
    # A factoriser !
    if mode == "word2vec":
        ExpeTableau = Word2VecR.objects.filter(modelc=DicActuel)
        for expe in ExpeTableau:
            os.remove(settings.RESULT_SEMANTIC_DIR + "/TableauEmb/" + mode + "/result/" + expe.nomresult + ".txt")
            expe.delete()
        ExpeExplo = Word2VecRExplo.objects.filter(modelc=DicActuel)
        for expe in ExpeExplo:
            shutil.rmtree(settings.RESULT_SEMANTIC_DIR + "/ReseauExplore/" + mode + "/result/" + expe.nomresult)
            expe.delete()
        ExpeCluster = Word2VecRCluster.objects.filter(modelc=DicActuel)
        for expe in ExpeCluster:
            shutil.rmtree(settings.RESULT_SEMANTIC_DIR + "/Cluster/" + mode + "/save/" + expe.nomresult)
            expe.delete()
        ExpeDiachro = Word2VecDiachro.objects.filter(modelc=DicActuel)
        for expe in ExpeDiachro:
            shutil.rmtree(settings.RESULT_SEMANTIC_DIR + "/Diachro/" + mode + "/save/" + expe.nomresult)
            expe.delete()

    if mode == "glove":
        ExpeTableau = GloveR.objects.filter(modelc=DicActuel)
        for expe in ExpeTableau:
            os.remove(settings.RESULT_SEMANTIC_DIR + "/TableauEmb/" + mode + "/result/" + expe.nomresult + ".txt")
            expe.delete()
        ExpeExplo = GloveRExplo.objects.filter(modelc=DicActuel)
        for expe in ExpeExplo:
            shutil.rmtree(settings.RESULT_SEMANTIC_DIR + "/ReseauExplore/" + mode + "/result/" + expe.nomresult)
            expe.delete()
        ExpeCluster = GloveRCluster.objects.filter(modelc=DicActuel)
        for expe in ExpeCluster:
            shutil.rmtree(settings.RESULT_SEMANTIC_DIR + "/Cluster/" + mode + "/save/" + expe.nomresult)
            expe.delete()
        ExpeDiachro = GloveDiachro.objects.filter(modelc=DicActuel)
        for expe in ExpeDiachro:
            shutil.rmtree(settings.RESULT_SEMANTIC_DIR + "/Diachro/" + mode + "/save/" + expe.nomresult)
            expe.delete()

    if mode == "fasttext":
        ExpeTableau = FastTextR.objects.filter(modelc=DicActuel)
        for expe in ExpeTableau:
            os.remove(settings.RESULT_SEMANTIC_DIR + "/TableauEmb/" + mode + "/result/" + expe.nomresult + ".txt")
            expe.delete()
        ExpeExplo = FastTextRExplo.objects.filter(modelc=DicActuel)
        for expe in ExpeExplo:
            shutil.rmtree(settings.RESULT_SEMANTIC_DIR + "/ReseauExplore/" + mode + "/result/" + expe.nomresult)
            expe.delete()
        ExpeCluster = FastTextRCluster.objects.filter(modelc=DicActuel)
        for expe in ExpeCluster:
            shutil.rmtree(settings.RESULT_SEMANTIC_DIR + "/Cluster/" + mode + "/save/" + expe.nomresult)
            expe.delete()
        ExpeDiachro = FastTextDiachro.objects.filter(modelc=DicActuel)
        for expe in ExpeDiachro:
            shutil.rmtree(settings.RESULT_SEMANTIC_DIR + "/Diachro/" + mode + "/save/" + expe.nomresult)
            expe.delete()


    DicInitModelDactuel["initial"].objects.filter(id=modele_id).delete()
    shutil.rmtree(settings.RESULT_SEMANTIC_DIR + "/TableauEmb/" + mode + "/modele/" + str(DicActuel.nom))


def SupprResult(mode, result_id):
    DicInitModelDactuel, DicInitFormDactuel = ModelFormInit(mode)
    DicActuel = DicInitModelDactuel["resultat"].objects.get(id=result_id)
    DicInitModelDactuel["resultat"].objects.filter(id=result_id).delete()
    os.remove(settings.RESULT_SEMANTIC_DIR + "/TableauEmb/" + mode + "/result/" + str(DicActuel.nomresult) + ".txt")

