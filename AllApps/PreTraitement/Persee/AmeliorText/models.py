from django.db import models
from AllApps.PreTraitement.Persee.DelimitCorpus.models import CorpusEtude, DocExtractInitial


# Pour enregistrer choix paramètres différentes parties

class TitreTransform(models.Model):
    CorpusEtudeRef = models.ForeignKey(CorpusEtude, on_delete=models.CASCADE)
    user = models.CharField(max_length=15)
    seuil = models.FloatField()
    SupprSlashSecondPart = models.BooleanField()
    SupprBeforeTitre = models.BooleanField()


class ResumeTransform(models.Model):
    CorpusEtudeRef = models.ForeignKey(CorpusEtude, on_delete=models.CASCADE)
    user = models.CharField(max_length=15)
    mots = models.TextField(max_length=400)
    zone = models.PositiveIntegerField()
    AjoutResumeFr = models.BooleanField()


class MotCleTransform(models.Model):
    CorpusEtudeRef = models.ForeignKey(CorpusEtude, on_delete=models.CASCADE)
    user = models.CharField(max_length=15)
    mots = models.TextField(max_length=400)
    zone = models.PositiveIntegerField()
    AjoutMotCleFr = models.BooleanField()

class HtDePageTransform(models.Model):
    CorpusEtudeRef = models.ForeignKey(CorpusEtude, on_delete=models.CASCADE)
    user = models.CharField(max_length=15)
    seuilgeo = models.PositiveIntegerField()
    seuilspgeo = models.PositiveIntegerField()

class BasDePageTransform(models.Model):
    CorpusEtudeRef = models.ForeignKey(CorpusEtude, on_delete=models.CASCADE)
    user = models.CharField(max_length=15)
    SupprAnnCombiTextual = models.BooleanField()
    SupprEspSup1990 = models.BooleanField()


class NoteTransform(models.Model):
    CorpusEtudeRef = models.ForeignKey(CorpusEtude, on_delete=models.CASCADE)
    user = models.CharField(max_length=15)
    SupprNoteBio = models.BooleanField()
    SupprNoteEdito = models.BooleanField()
    SupprNoteBasDePage = models.BooleanField()


class BiblioTransform(models.Model):
    CorpusEtudeRef = models.ForeignKey(CorpusEtude, on_delete=models.CASCADE)
    user = models.CharField(max_length=15)
    SupprBilioEtFin = models.BooleanField()
    mots = models.TextField(max_length=400)
    zone = models.PositiveIntegerField()


class AppendixTransform(models.Model):
    CorpusEtudeRef = models.ForeignKey(CorpusEtude, on_delete=models.CASCADE)
    user = models.CharField(max_length=15)
    suppr = models.BooleanField()
    mots = models.TextField(max_length=400)
    zone = models.PositiveIntegerField()


class SousTitreTransform(models.Model):
    CorpusEtudeRef = models.ForeignKey(CorpusEtude, on_delete=models.CASCADE)
    user = models.CharField(max_length=15)
    remplace = models.BooleanField()


class FigureTransform(models.Model):
    CorpusEtudeRef = models.ForeignKey(CorpusEtude, on_delete=models.CASCADE)
    user = models.CharField(max_length=15)
    EssaiHomogeneTitre = models.BooleanField()
    mots = models.TextField(max_length=600)


class FinDocTransform(models.Model):
    CorpusEtudeRef = models.ForeignKey(CorpusEtude, on_delete=models.CASCADE)
    user = models.CharField(max_length=15)
    ContenuCentreRemove = models.BooleanField()
    mots = models.TextField(max_length=600)
    ManuscritRemove = models.BooleanField()


class CedilleTransform(models.Model):
    CorpusEtudeRef = models.ForeignKey(CorpusEtude, on_delete=models.CASCADE)
    user = models.CharField(max_length=15)
    litigecedille = models.BooleanField()


class FinMotTransform(models.Model):
    CorpusEtudeRef = models.ForeignKey(CorpusEtude, on_delete=models.CASCADE)
    user = models.CharField(max_length=15)


class FinLigneTransform(models.Model):
    CorpusEtudeRef = models.ForeignKey(CorpusEtude, on_delete=models.CASCADE)
    user = models.CharField(max_length=15)
    normalise = models.BooleanField()

# Pour enregistrer les exceptions manuelles

class AllExceptRemove(models.Model):
    CorpusEtudeRef = models.ForeignKey(CorpusEtude, on_delete=models.CASCADE)
    DocExtractRef = models.ForeignKey(DocExtractInitial, on_delete=models.CASCADE)
    type = models.CharField(max_length=80)
    IndexDeb = models.IntegerField()
    IndexFin = models.IntegerField()
    TextField = models.TextField()
    comment = models.CharField(max_length=250)

class AllExceptAdd(models.Model):
    CorpusEtudeRef = models.ForeignKey(CorpusEtude, on_delete=models.CASCADE)
    DocExtractRef = models.ForeignKey(DocExtractInitial, on_delete=models.CASCADE)
    type = models.CharField(max_length=80)
    IndexDeb = models.IntegerField()
    IndexFin = models.IntegerField()
    TextField = models.TextField()
    comment = models.CharField(max_length=250)

class DocRemove(models.Model):
    CorpusEtudeRef = models.ForeignKey(CorpusEtude, on_delete=models.CASCADE)
    DocExtractRef = models.ForeignKey(DocExtractInitial, on_delete=models.CASCADE)
    type = models.CharField(max_length=80)
    comment = models.CharField(max_length=250)