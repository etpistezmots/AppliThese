from django import forms
from .models import CorpusEtude
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column


class VersionReducFormAll(forms.ModelForm):
    def __init__(self, *args, **kwargs):
       super().__init__(*args, **kwargs)


    def clean(self):
        cleaned_data = super().clean()
        date1 = cleaned_data.get("datemin")
        date2 = cleaned_data.get("datemax")
        testepoque(date1, date2, self)
        revue0= cleaned_data.get("revue")
        testrevue(revue0, self)


    class Meta:
        model = CorpusEtude
        exclude = ['SyntheseTransformRef']



class VersionReducFormRed(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        # see "rendering severals forms with helpers" in django crispy form
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('nom', css_class='form-group col-md-4 mb-0'),
                Column('user_restrict', css_class='form-group col-md-4 mb-0'),
                Column('date', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('revue', css_class='form-group col-md-4 mb-0'),
                Column('stopworddossier', css_class='form-group col-md-4 mb-0'),
                Column('typedoc', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('datemin', css_class='form-group col-md-4 mb-0'),
                Column('datemax', css_class='form-group col-md-4 mb-0'),
                Column('langue', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('motmin', css_class='form-group col-md-4 mb-0'),
                Column('pagemin', css_class='form-group col-md-4 mb-0'),
                Column('comment', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('typecatnon', css_class='form-group col-md-8 mb-0'),
                Column('extract_mot', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            )

        )

        super().__init__(*args, **kwargs)
        self.fields['nom'].label = "Nom de la réduction"
        self.fields['stopworddossier'].label = "Stop word dossier"
        self.fields['typedoc'].label = "Type document include"
        self.fields['typecatnon'].label = "Type catégorie exclude"
        self.fields['typecatnon'].widget.attrs['rows'] = 2


    def clean(self):
        cleaned_data = super().clean()
        date1 = cleaned_data.get("datemin")
        date2 = cleaned_data.get("datemax")
        testepoque(date1, date2, self)
        revue0= cleaned_data.get("revue")
        print(revue0)
        testrevue(revue0, self)


    class Meta:
        model = CorpusEtude
        exclude = ['SyntheseTransformRef']


def testepoque(date1, date2, testme):
    if date1 < date2:
        pass
    else:
        msg = "Merci d'indiquer une datemin inférieure à la datemax"
        testme.add_error("datemin", msg)

def testrevue(revue0, testme):
    if revue0=="geo" or revue0=="spgeo" or revue0=="geo,spgeo" or revue0=="spgeo,geo":
        pass
    else:
        msg = "La revue doit être soit geo pour les Annales, soit spgeo pour l'Espace"
        testme.add_error("revue", msg)
