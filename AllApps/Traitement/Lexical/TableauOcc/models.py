from django.db import models
from AllApps.PreTraitement.Persee.FinaliseCorpus.models import CorpusFin

revue_choices = (("Annales,Espace", "Annales,Espace"), ("Annales", "Annales"), ("Espace","Espace"))

class CountOcc(models.Model):
    nomresult = models.CharField(max_length=200, unique=True)
    mode = models.CharField(max_length=50)
    terme = models.CharField(max_length=300, blank=False, default=None)
    CorpusFinRef = models.ForeignKey(CorpusFin, on_delete=models.CASCADE)
    revue = models.CharField(max_length=100, choices=revue_choices)
    epoque = models.CharField(max_length=300)
    user_restrict = models.CharField(max_length=50)
