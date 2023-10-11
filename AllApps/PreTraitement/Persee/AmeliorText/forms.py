from django import forms
from AllApps.PreTraitement.Persee.DelimitCorpus.models import CorpusEtude
from .models import TitreTransform,ResumeTransform,\
                    HtDePageTransform,BasDePageTransform,\
                    MotCleTransform, NoteTransform,\
                    BiblioTransform,AppendixTransform,FigureTransform,SousTitreTransform,\
                    FinDocTransform,CedilleTransform, FinMotTransform, FinLigneTransform

from django.core.validators import MaxValueValidator, MinValueValidator

class TitreTransformForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['seuil'].label = "Seuil ressemblance minimal (entre 0 et 1) pour les articles : "
        self.fields['seuil'].widget.attrs['size'] = 4
        self.fields['SupprSlashSecondPart'].label = "Supprimer deuxième partie après Slash (anglais) pour les articles"
        self.fields['SupprBeforeTitre'].label = "Supprimer partie avant titre pour les articles"

    class Meta:
        model = TitreTransform
        exclude = ['CorpusEtudeRef',"user"]


class ResumeTransformForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['zone'].label = "Zone recherche mots suivants:"
        self.fields['mots'].label = "Enlever mot(s) avant résumé (séparateur *):"

    class Meta:
        model = ResumeTransform
        exclude = ['CorpusEtudeRef',"user"]


class MotCleTransformForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['zone'].label = "Zone recherche mots suivants:"
        self.fields['mots'].label = "Enlever mot(s) avant mots-clés (séparateur *):"

    class Meta:
        model = MotCleTransform
        exclude = ['CorpusEtudeRef',"user"]

class HtDePageTransformForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['seuilgeo'].label = "Seuil Annales de géographie :"
        self.fields['seuilspgeo'].label = "Seuil Espace Géographique :"

    class Meta:
        model = HtDePageTransform
        exclude = ['CorpusEtudeRef',"user"]

class BasDePageTransformForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['SupprEspSup1990'].label = "Suppression bas de page Espace à partir 1990"
        self.fields['SupprAnnCombiTextual'].label = "Suppression bas de page Annales combinaisons textuelles"

    class Meta:
        model = BasDePageTransform
        exclude = ['CorpusEtudeRef',"user"]

class NoteTransformForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['SupprNoteBio'].label = "Suppression notes biographiques"
        self.fields['SupprNoteEdito'].label = "Suppression notes de l'éditeur"
        self.fields['SupprNoteBasDePage'].label = "Suppression notes de bas de page"

    class Meta:
        model = NoteTransform
        exclude = ['CorpusEtudeRef',"user"]



class BiblioTransformForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['SupprBilioEtFin'].label = "Supprimer bibliographies et parties après la dernière bibliographie"
        self.fields['mots'].label = "Enlever mot(s) avant bibliographie (séparateur *):"
        self.fields['zone'].label = "Zone recherche mots suivants:"

    class Meta:
        model = BiblioTransform
        exclude = ['CorpusEtudeRef',"user"]


class AppendixTransformForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['suppr'].label = "Supprimer annexes"
        self.fields['mots'].label = "Enlever mot(s) avant annexes (séparateur *):"
        self.fields['zone'].label = "Zone recherche mots suivants:"

    class Meta:
        model = AppendixTransform
        exclude = ['CorpusEtudeRef',"user"]



class FigureTransformForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['EssaiHomogeneTitre'].label = "Retrait du contenu et maintien des titres"
        self.fields['mots'].label = "Mots à enlever dans l'ensemble du texte  (séparateur *):"

    class Meta:
        model = FigureTransform
        exclude = ['CorpusEtudeRef',"user"]



class SousTitreTransformForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['remplace'].label = "Remplacer titres secondaires par leurs versions corrigées par l'UAR Persée"

    class Meta:
        model = SousTitreTransform
        exclude = ['CorpusEtudeRef',"user"]



class FinDocTransformForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ContenuCentreRemove'].label = "Supprimer passage dans l'Espace Géographique après une ligne centrée contenant un des termes suivants"
        self.fields['mots'].label = "Liste des termes séparés par *:"
        self.fields['ManuscritRemove'].label = "Enlever ligne commençant par 'Manuscrit' et les lignes d'arpès dans l'Espace Géographique"

    class Meta:
        model = FinDocTransform
        exclude = ['CorpusEtudeRef',"user"]



class CedilleTransformForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['litigecedille'].label = "enlever les cas litigieux définis lors de l'exploration menée"

    class Meta:
        model = CedilleTransform
        exclude = ['CorpusEtudeRef',"user"]

class FinMotTransformForm(forms.ModelForm):

    class Meta:
        model = FinMotTransform
        exclude = ['CorpusEtudeRef',"user"]


class FinLigneTransformForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = FinLigneTransform
        exclude = ['CorpusEtudeRef',"user"]



choixtype = [('txtbrut', 'txtbrut'), ('txtxml', 'txtxml')]


class SeqChercheForm(forms.Form):
    corpus = forms.ChoiceField(choices=[(corpus.nom,corpus.nom) for corpus in CorpusEtude.objects.all()])
    article = forms.CharField(widget=forms.TextInput(attrs={'size':80}))
    sequence = forms.CharField(widget=forms.Textarea)
    typerecherche = forms.ChoiceField(choices=choixtype)
