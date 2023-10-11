from django.db import models
from AllApps.PreTraitement.Persee.DelimitCorpus.models import CorpusEtude

# Create your models here.

class CorpusAdd(models.Model):
    nom = models.CharField(max_length=150, unique=True)
    user_restrict = models.CharField(max_length=150)
    date = models.CharField(max_length=80)

    def __str__(self):
        return self.nom

class TextAdd(models.Model):
    titre = models.CharField(max_length=550)
    nomfichier = models.CharField(max_length=150)
    annee = models.IntegerField()
    type = models.CharField(max_length=80)
    revue = models.CharField(max_length=50)
    auteurs = models.CharField(max_length=550)
    CorpusAddRef = models.ForeignKey(CorpusAdd, on_delete=models.CASCADE)

class CorpusComplet(models.Model):
    nom = models.CharField(max_length=150, unique=True)
    user_restrict = models.CharField(max_length=150)
    date = models.CharField(max_length=80)
    CorpusEtudeRef = models.ForeignKey(CorpusEtude, on_delete=models.CASCADE)
    CorpusAddRef = models.ForeignKey(CorpusAdd, on_delete=models.CASCADE)
    EltRemove = models.TextField()

    def __str__(self):
        return self.nom

class DicoMotLemme(models.Model):
    nom = models.CharField(max_length=150, unique=True)
    user_restrict = models.CharField(max_length=150)

    def __str__(self):
        return self.nom

class DicoExpression(models.Model):
    nom = models.CharField(max_length=150, unique=True)
    user_restrict = models.CharField(max_length=150)

    def __str__(self):
        return self.nom

class DicoSuffixe(models.Model):
    nom = models.CharField(max_length=150, unique=True)
    user_restrict = models.CharField(max_length=150)

    def __str__(self):
        return self.nom


class FNRRequest(models.Model):
    CorpusCompletRef = models.ForeignKey(CorpusComplet, on_delete=models.CASCADE)
    DicoExpressionRef = models.ForeignKey(DicoExpression, on_delete=models.CASCADE)
    DicoMotLemmeRef = models.ForeignKey(DicoMotLemme, on_delete=models.CASCADE)

class CorpusFin(models.Model):
    nom = models.CharField(max_length=150, unique=True)
    user_restrict = models.CharField(max_length=150)
    date = models.CharField(max_length=80)
    CorpusCompletRef = models.ForeignKey(CorpusComplet, on_delete=models.CASCADE)
    PretraitIraBase = models.BooleanField()
    DicoExpressionRef = models.ForeignKey(DicoExpression, on_delete=models.CASCADE)
    DicoSuffixeRef = models.ForeignKey(DicoSuffixe, on_delete=models.CASCADE)
    Lemmatisation = models.BooleanField()
    DicoMotLemmeRef = models.ForeignKey(DicoMotLemme, on_delete=models.CASCADE)

    def __str__(self):
        return self.nom