from django import forms
from .models import CountOcc
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column

class CountOccForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def clean(self):
        cleaned_data = super().clean()
        epoquetest = cleaned_data.get("epoque")
        testmeepoque(epoquetest, self)

    class Meta:
        model = CountOcc
        fields = '__all__'


class CountOccRedForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('terme', css_class='form-group col-md-4 mb-0'),
                Column('CorpusFinRef', css_class='form-group col-md-4 mb-0'),
                Column('user_restrict', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('revue', css_class='form-group col-md-4 mb-0'),
                Column('epoque', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            )
        )
        super().__init__(*args, **kwargs)
        self.fields['terme'].label = "Terme(s)"
        self.fields['CorpusFinRef'].label = "Corpus utilisé"
        self.fields['user_restrict'].widget.attrs['size'] = 5
        self.fields['epoque'].widget.attrs['size'] = 60

    def clean(self):
        cleaned_data = super().clean()
        epoquetest = cleaned_data.get("epoque")
        testmeepoque(epoquetest, self)

    class Meta:
        model = CountOcc
        exclude = ['nomresult','mode']



def testmeepoque(epoquetest, testme):
    splittest1 = epoquetest.split(",")
    for elt in splittest1:
        splittest2 = elt.split("-")

        if len(splittest2) != 2:
            msg = "le format de l'époque doit être formaté comme cet exemple : 1940-1959,1960-1980"
            testme.add_error("epoque", msg)
        else:
            a = splittest2[0].isdigit()
            b = splittest2[1].isdigit()
            if a and b:
                if int(splittest2[0]) < int(splittest2[1]) and len(splittest2[0]) == 4 and len(splittest2[0]) == 4:
                    pass
                else:
                    msg = "le format de l'époque doit être formaté comme cet exemple : 1940-1959,1960-1980"
                    testme.add_error("epoque", msg)
            else:
                msg = "le format de l'époque doit être formaté comme cet exemple : 1940-1959,1960-1980"
                testme.add_error("epoque", msg)
