from django.db import models
from polymorphic.models import PolymorphicModel
from AllApps.Traitement.Semantique.TableauEmb.models import Word2Vec,Glove,FastText

# Create your models here.

corpus_choices = (("/home/max/Bureau/AFCMax/Input/DataMaxGeo.csv","corpus actuel"),("autre path","autre choix text"))
revues_choices = (("Annales","Annales"),("Espace","Espace"))




MethodeClustering = (("Kmeans","Kmeans"),("saut moyen","saut moyen"),("saut minimal","saut minimal"),("saut maximal","saut maximal"))



class Word2VecRCluster(models.Model):
    modelc = models.ForeignKey(Word2Vec, on_delete=models.CASCADE)
    nomresult = models.CharField(max_length=200, unique=True)
    user_restrict2 = models.CharField(max_length=100)
    choixrevue = models.CharField(max_length=100)
    choixepoque = models.CharField(max_length=100)
    terme = models.CharField(max_length=100)
    nresult = models.PositiveIntegerField()
    methode_clustering = models.CharField(max_length=100, choices=MethodeClustering, blank=False, default=None)
    ncluster = models.PositiveIntegerField()
    link = models.BooleanField()
    color_singleton = models.BooleanField()

    def __str__(self):
        return self.nomresult



class GloveRCluster(models.Model):
    modelc = models.ForeignKey(Glove, on_delete=models.CASCADE)
    nomresult = models.CharField(max_length=200, unique=True)
    user_restrict2 = models.CharField(max_length=100)
    choixrevue = models.CharField(max_length=100)
    choixepoque = models.CharField(max_length=100)
    terme = models.CharField(max_length=100)
    nresult = models.PositiveIntegerField()
    methode_clustering = models.CharField(max_length=100, choices=MethodeClustering, blank=False, default=None)
    ncluster = models.PositiveIntegerField()
    link = models.BooleanField()
    color_singleton = models.BooleanField()

    def __str__(self):
        return self.nomresult



class FastTextRCluster(models.Model):
    modelc = models.ForeignKey(FastText, on_delete=models.CASCADE)
    nomresult = models.CharField(max_length=200, unique=True)
    user_restrict2 = models.CharField(max_length=100)
    choixrevue = models.CharField(max_length=100)
    choixepoque = models.CharField(max_length=100)
    terme = models.CharField(max_length=100)
    nresult = models.PositiveIntegerField()
    methode_clustering = models.CharField(max_length=100, choices=MethodeClustering, blank=False, default=None)
    ncluster = models.PositiveIntegerField()
    link = models.BooleanField()
    color_singleton = models.BooleanField()

    def __str__(self):
        return self.nomresult