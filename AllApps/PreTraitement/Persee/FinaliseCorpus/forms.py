from django import forms
from .models import CorpusAdd, CorpusComplet, DicoMotLemme, DicoExpression, DicoSuffixe, FNRRequest, CorpusFin


class CorpusAddForm(forms.ModelForm):
    class Meta:
        model = CorpusAdd
        fields = '__all__'

class CorpusCompletForm(forms.ModelForm):
    class Meta:
        model = CorpusComplet
        exclude = ['CorpusEtudeRef']

class CorpusCompletFormVisuel(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['CorpusEtudeRef'].label = "Corpus de base utilisé"
        self.fields['CorpusAddRef'].label = "Corpus additionnel utilisé"
        self.fields['EltRemove'].label = "Eléments enlevés"
    class Meta:
        model = CorpusComplet
        exclude = ['nom','user_restrict','date']


class DicoMotLemmeForm(forms.ModelForm):
    class Meta:
        model = DicoMotLemme
        fields = '__all__'

class DicoExpressionForm(forms.ModelForm):
    class Meta:
        model = DicoExpression
        fields = '__all__'

class DicoSuffixeForm(forms.ModelForm):
    class Meta:
        model = DicoSuffixe
        fields = '__all__'

class FNRRequestForm(forms.ModelForm):
    class Meta:
        model = FNRRequest
        fields = '__all__'

class CorpusFinForm(forms.ModelForm):
    class Meta:
        model = CorpusFin
        fields = '__all__'

class CorpusFinFormVisuel(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['CorpusCompletRef'].label = "Corpus complet utilisé"
        self.fields['PretraitIraBase'].label = "1ères tranformations (minuscule,...) "
        self.fields['DicoExpressionRef'].label = "Dictionnaire expressions utilisé"
        self.fields['DicoSuffixeRef'].label = "Liste fin de mot utilisée"
        self.fields['Lemmatisation'].label = "Lemmatisation"
        self.fields['DicoMotLemmeRef'].label = "Dictionnataire mot/lemme utilisé"
    class Meta:
        model = CorpusFin
        exclude = ['nom','user_restrict','date']