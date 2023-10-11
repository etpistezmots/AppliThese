from django.db import models

# Modèles générant les tables dans la base de données avec les clés entre les tables

class Auteur(models.Model):
    nom = models.CharField(max_length=200)
    prenom = models.CharField(max_length=200)
    type = models.CharField(max_length=20)
    idpersee = models.CharField(max_length=20)

    def __str__(self):
        return self.nom


class Revue(models.Model):
    nom = models.CharField(max_length=150)
    nompersee = models.CharField(max_length=20)

    def __str__(self):
        return self.nom


class DocReference(models.Model):
    titre = models.CharField(max_length=550)
    url = models.CharField(max_length=250)
    TextRef = models.CharField(max_length=150)
    type = models.CharField(max_length=80)
    annee = models.IntegerField()
    RevueRef = models.ForeignKey(Revue, on_delete=models.CASCADE)
    AuteursRef = models.ManyToManyField(Auteur)

    def __str__(self):
        return self.titre


class SyntheseTransform(models.Model):
    # Tous ces champs se comprennent à partir AmeliorText.models
    # Je n'ai pas mis des clés étrangères vers ces modèles car peur de références circulaires
    # en effet, déjà des clés étrangères dans ces modèles renvoyant à CorpusEtudeRef
    seuilTitre = models.FloatField()
    SupprSlashSecondPart = models.BooleanField()
    SupprBeforeTitre = models.BooleanField()
    motsResume = models.TextField(max_length=400)
    zoneResume = models.PositiveIntegerField()
    AjoutResumeFr = models.BooleanField()
    motstMotCle = models.TextField(max_length=400)
    zonetMotCle = models.PositiveIntegerField()
    AjoutMotCleFr = models.BooleanField()
    seuilgeoHtdePage = models.PositiveIntegerField()
    seuilspgeoHtdePage = models.PositiveIntegerField()
    SupprAnnCombiTextualBasdePage = models.BooleanField()
    SupprEspSup1990BasdePage = models.BooleanField()
    SupprNoteBio = models.BooleanField()
    SupprNoteEdito = models.BooleanField()
    SupprNoteBasDePage = models.BooleanField()
    SupprBilioEtFin = models.BooleanField()
    motsBiblio = models.TextField(max_length=400)
    zoneBiblio = models.PositiveIntegerField()
    supprAppendix = models.BooleanField()
    motsAppendix = models.TextField(max_length=400)
    zoneAppendix = models.PositiveIntegerField()
    remplaceSsTitre = models.BooleanField()
    EssaiHomogeneTitre = models.BooleanField()
    motsFigure = models.TextField(max_length=600)
    ContenuCentreRemove = models.BooleanField()
    motsFinDoc = models.TextField(max_length=600)
    ManuscritRemove = models.BooleanField()
    litigecedille = models.BooleanField()
    FinMotTrait = models.BooleanField()
    FinLigneNormalise = models.BooleanField()
    AllExceptRemoveRef = models.TextField()
    AllExceptAddRef = models.TextField()
    DocRemoveRef = models.TextField()

# la virgule est importante
#https://stackoverflow.com/questions/913590/django-error-too-many-values-to-unpack/8206621
extractmot_choices = (("FromTEIDocMot","FromTEIDocMot"),)


class CorpusEtude(models.Model):
    nom = models.CharField(max_length=150, unique=True)
    user_restrict = models.CharField(max_length=150)
    date = models.CharField(max_length=80)
    revue = models.CharField(max_length=50)
    stopworddossier = models.CharField(max_length=500)
    typedoc= models.CharField(max_length=400)
    datemin = models.IntegerField()
    datemax = models.IntegerField()
    langue = models.CharField(max_length=300)
    motmin = models.IntegerField()
    pagemin = models.IntegerField()
    typecatnon = models.TextField()
    comment = models.CharField(max_length=400)
    extract_mot = models.CharField(max_length=100, choices=extractmot_choices)
    #blank et null = True pour possibilité d'enregistrement intermédiaire avant etape transform --> voir AmelioText
    SyntheseTransformRef = models.ForeignKey(SyntheseTransform, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.nom


class DocExtractInitial(models.Model):
    DocReferenceRef = models.ForeignKey(DocReference, on_delete=models.CASCADE)
    CorpusEtudeRef = models.ForeignKey(CorpusEtude, on_delete=models.CASCADE)
    TextExtract = models.CharField(max_length=150)


class DocTransforme(models.Model):
    DocExtractRef = models.ForeignKey(DocExtractInitial, on_delete=models.CASCADE)
    CorpusEtudeRef = models.ForeignKey(CorpusEtude, on_delete=models.CASCADE)
    TextTransforme = models.CharField(max_length=150)


class Transformer(models.Model):
    DocExtractRef = models.ForeignKey(DocExtractInitial, on_delete=models.CASCADE)
    type = models.CharField(max_length=80)
    IndexDeb = models.IntegerField()
    IndexFin = models.IntegerField()
    TextField = models.TextField()
    comment = models.CharField(max_length=250)










