import os, shutil
from django.conf import settings
from .prepaaffiche import ModelFormInit


def RemoveOldTempFolder(modeactuel, seuil):
    folder = settings.RESULT_SEMANTIC_DIR + "/Diachro/" + modeactuel + "/temp"
    a = [s for s in os.listdir(folder)]
    a.sort(key=lambda s: os.path.getmtime(os.path.join(folder, s)))
    if len(a) > seuil:
        shutil.rmtree(folder + "/" + a[0])



def CopyTempToSave(modeactuel, pathresult, name):
    foldertempbase = settings.RESULT_SEMANTIC_DIR + "/Diachro/" + modeactuel + "/temp"
    nametemp = pathresult.split("---")[1]
    foldertemp = foldertempbase + "/" + nametemp

    pathresult = settings.RESULT_SEMANTIC_DIR + "/Diachro/" + modeactuel + "/save/" + name

    # Copier le fichier !
    if os.path.isdir(foldertemp):
        shutil.copytree(foldertemp, pathresult)

    shutil.rmtree(foldertemp)
    os.rename(pathresult + "/4)Json/" + nametemp + ".json", pathresult + "/4)Json/" + name + ".json")

