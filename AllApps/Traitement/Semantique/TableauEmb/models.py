from django.db import models
from AllApps.PreTraitement.Persee.FinaliseCorpus.models import  CorpusFin
from polymorphic.models import PolymorphicModel

# variable pour modèle expe ci-dessous
revues_choices = (("Annales,Espace","Annales,Espace",),("Annales","Annales"),("Espace","Espace"))

# Attention django models supporte pas clé étrangère
# quand plusieurs base de données
# pour contourner user_restrict sous forme de liste d'users autorisé à voir l'expe
# 0 pour une expe publique accessible à tous !
# et sinonb liste des utilisateurs autorisés à voir !

class Expe(PolymorphicModel):
    nom = models.CharField(max_length=200, unique=True)
    user_restrict = models.CharField(max_length=100)
    CorpusFinRef = models.ForeignKey(CorpusFin, on_delete=models.CASCADE)
    revue = models.CharField(max_length=200, choices=revues_choices, blank=False, default=None)
    epoque = models.CharField(max_length=300)


# Dans les classes suivantes,
# R est la partie résultat (calculé à partir du modèle précédemment calculé)
# attention à la difficulté suivante :
# confusion modèle django (modeld) et modèle word embedding (modelc --> modèle calculé)

architecture_choices = (("cbow", "cbow",), ("skipgram", "skipgram"))


class Word2Vec(Expe):
    architecture = models.CharField(max_length=20, choices=architecture_choices, blank=False, default=None)
    embedding_size = models.PositiveIntegerField()
    context_size = models.PositiveIntegerField()
    min_occurrences = models.PositiveIntegerField()
    num_epochs = models.PositiveIntegerField()

    def __str__(self):
        return self.nom


class Word2VecR(models.Model):
    modelc = models.ForeignKey(Word2Vec, on_delete=models.CASCADE)
    user_restrict2 = models.CharField(max_length=100)
    nomresult = models.CharField(max_length=200, unique=True)
    terme = models.CharField(max_length=100)
    nresult = models.IntegerField()

    def __str__(self):
        return self.nomresult


class Glove(Expe):
    embedding_size = models.IntegerField()
    context_size = models.IntegerField()
    min_occurrences = models.IntegerField()
    num_epochs = models.IntegerField()

    def __str__(self):
        return self.nom


class GloveR(models.Model):
    modelc = models.ForeignKey(Glove, on_delete=models.CASCADE)
    user_restrict2 = models.CharField(max_length=100)
    nomresult = models.CharField(max_length=200, unique=True)
    terme = models.CharField(max_length=100)
    nresult = models.IntegerField()

    def __str__(self):
        return self.nomresult


class FastText(Expe):
    architecture = models.CharField(max_length=20, choices=architecture_choices, blank=False, default=None)
    embedding_size = models.PositiveIntegerField()
    context_size = models.PositiveIntegerField()
    min_occurrences = models.PositiveIntegerField()
    num_epochs = models.IntegerField()
    min_n = models.PositiveIntegerField()
    max_n = models.PositiveIntegerField()

    def __str__(self):
        return self.nom


class FastTextR(models.Model):
    modelc = models.ForeignKey(FastText, on_delete=models.CASCADE)
    user_restrict2 = models.CharField(max_length=100)
    nomresult = models.CharField(max_length=200, unique=True)
    terme = models.CharField(max_length=100)
    nresult = models.IntegerField()

    def __str__(self):
        return self.nomresult




