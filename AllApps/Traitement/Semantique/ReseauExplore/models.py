from django.db import models
from polymorphic.models import PolymorphicModel
from django.contrib.auth.models import User
from AllApps.Traitement.Semantique.TableauEmb.models import Word2Vec,Glove,FastText


defautchoices = [("defaul","defaut")]

class Word2VecRExplo(models.Model):
    modelc = models.ForeignKey(Word2Vec, on_delete=models.CASCADE)
    nomresult = models.CharField(max_length=200, unique=True)
    user_restrict2 = models.CharField(max_length=100)
    choixrevue = models.CharField(max_length=100)
    choixepoque = models.CharField(max_length=100)
    terme = models.CharField(max_length=100)
    nresult = models.IntegerField()
    comment = models.CharField(max_length=500)
    indexnode = models.PositiveIntegerField()
    indexedge = models.PositiveIntegerField()
    oriented = models.CharField(max_length=4)

    def __str__(self):
        return self.nomresult




class GloveRExplo(models.Model):
    modelc = models.ForeignKey(Glove, on_delete=models.CASCADE)
    nomresult = models.CharField(max_length=200, unique=True)
    user_restrict2 = models.CharField(max_length=100)
    choixrevue = models.CharField(max_length=100)
    choixepoque = models.CharField(max_length=100)
    terme = models.CharField(max_length=100)
    nresult = models.IntegerField()
    comment = models.CharField(max_length=500)
    indexnode = models.PositiveIntegerField()
    indexedge = models.PositiveIntegerField()
    oriented = models.CharField(max_length=4)

    def __str__(self):
        return self.nomresult



class FastTextRExplo(models.Model):
    modelc = models.ForeignKey(FastText, on_delete=models.CASCADE)
    nomresult = models.CharField(max_length=200, unique=True)
    user_restrict2 = models.CharField(max_length=100)
    choixrevue = models.CharField(max_length=100)
    choixepoque = models.CharField(max_length=100)
    terme = models.CharField(max_length=100)
    nresult = models.IntegerField()
    comment = models.CharField(max_length=500)
    indexnode = models.PositiveIntegerField()
    indexedge = models.PositiveIntegerField()
    oriented = models.CharField(max_length=4)

    def __str__(self):
        return self.nomresult