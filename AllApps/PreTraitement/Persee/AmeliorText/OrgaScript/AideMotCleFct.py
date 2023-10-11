import csv
from AllApps.PreTraitement.Persee.DelimitCorpus.models import  CorpusEtude
from django.conf import settings


def read_csv_motcle(revue):
    AdresseData = settings.DATA_DIR + "/BDPerseeMotCle/" + revue +"_keywordsComplet.csv"
    DocImplique = []
    AllInfo = []
    with open(AdresseData, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader)
        for row in reader:
            doc = row[11]
            page = row[2]
            left = row[3]
            top = row[4]
            width = row[5]
            height = row[6]
            AllInfo.append((doc, page, left, top, width, height))

            if doc != "":
                DocImplique.append(row[11])

    DocImpliqueSansDoublon = list(set(DocImplique))

    return DocImpliqueSansDoublon, AllInfo