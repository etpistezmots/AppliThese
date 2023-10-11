from django.db import models
from AllApps.Traitement.Semantique.TableauEmb.models import Glove, Word2Vec, FastText

# Create your models here.

MethodeClustering = (("saut maximal","saut maximal"),("saut moyen","saut moyen"))
ChoixPoidsLabel = (("Simi cos par rapport terme initial","Simi cos par rapport terme initial"),
                   ("1 pour tous les termes","1 pour tous les termes"),
                   ("1 pour tous les termes et label max somme intra simi cos", "1 pour tous les termes et label max somme intra simi cos"))


ChoixSelectLink = (("Methode theorie initiale","Methode theorie initiale"),
                   ("Methode DiachoExplorer", "Methode DiachoExplorer"),
                   ("Tous sans selection", "Tous sans selection"))

ChoixTailleCluter = (("Nombre termes constitutifs cluster","Nombre termes constitutifs cluster"),
                     ("Nombre occurences des termes constitutifs cluster", "Nombre occurences des termes constitutifs cluster"))




class GloveDiachro(models.Model):
    modelc = models.ForeignKey(Glove, on_delete=models.CASCADE)
    nomresult = models.CharField(max_length=200, unique=True)
    user_restrict2 = models.CharField(max_length=100)
    terme = models.CharField(max_length=100)
    nresult = models.CharField(max_length=50)
    methode_clustering = models.CharField(max_length=100, choices=MethodeClustering, blank=False, default=None)
    ncluster = models.CharField(max_length=50)
    compareJustNewRevue = models.BooleanField()
    stop_mots = models.CharField(max_length=800,blank=True)
    selectLink = models.CharField(max_length=100,choices=ChoixSelectLink, blank=False, default=None)
    calculPoidsLabel = models.CharField(max_length=100,choices=ChoixPoidsLabel, blank=False, default=None)
    taillecluster = models.CharField(max_length=100,choices=ChoixTailleCluter, blank=False, default=None)
    couleursRevues = models.CharField(max_length=200)
    seuil100 = models.PositiveIntegerField()

    def __str__(self):
        return self.nomresult



class Word2VecDiachro(models.Model):
    modelc = models.ForeignKey(Word2Vec, on_delete=models.CASCADE)
    nomresult = models.CharField(max_length=200, unique=True)
    user_restrict2 = models.CharField(max_length=100)
    terme = models.CharField(max_length=100)
    nresult = models.CharField(max_length=50)
    methode_clustering = models.CharField(max_length=100, choices=MethodeClustering, blank=False, default=None)
    ncluster = models.CharField(max_length=50)
    compareJustNewRevue = models.BooleanField()
    stop_mots = models.TextField()
    selectLink = models.CharField(max_length=100, choices=ChoixSelectLink, blank=False, default=None)
    calculPoidsLabel = models.CharField(max_length=100, choices=ChoixPoidsLabel, blank=False, default=None)
    taillecluster = models.CharField(max_length=100,choices=ChoixTailleCluter, blank=False, default=None)
    couleursRevues = models.CharField(max_length=200)
    seuil100 = models.PositiveIntegerField()


    def __str__(self):
        return self.nomresult


class FastTextDiachro(models.Model):
    modelc = models.ForeignKey(FastText, on_delete=models.CASCADE)
    nomresult = models.CharField(max_length=200, unique=True)
    user_restrict2 = models.CharField(max_length=100)
    terme = models.CharField(max_length=100)
    nresult = models.CharField(max_length=50)
    methode_clustering = models.CharField(max_length=100, choices=MethodeClustering, blank=False, default=None)
    ncluster = models.CharField(max_length=50)
    compareJustNewRevue = models.BooleanField()
    stop_mots = models.TextField()
    selectLink = models.CharField(max_length=100, choices=ChoixSelectLink, blank=False, default=None)
    calculPoidsLabel = models.CharField(max_length=100, choices=ChoixPoidsLabel, blank=False, default=None)
    taillecluster = models.CharField(max_length=100,choices=ChoixTailleCluter, blank=False, default=None)
    couleursRevues = models.CharField(max_length=200)
    seuil100 = models.PositiveIntegerField()

    def __str__(self):
        return self.nomresult