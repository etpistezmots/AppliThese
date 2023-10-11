from django import forms
from .models import GloveRCluster, Word2VecRCluster, FastTextRCluster
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column




########################### GLOVE ###################################


class GloveClusterRedForm(forms.ModelForm):
    def __init__(self, epoques, revues, epoque1=None, revue1=None, *args, **kwargs):
        self.helper = FormHelper()
        # see "rendering severals forms with helpers" in django crispy form
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('choixrevue', css_class='form-group col-md-4 mb-0'),
                Column('choixepoque', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('terme', css_class='form-group col-md-4 mb-0'),
                Column('nresult', css_class='form-group col-md-4 mb-0'),
                Column('user_restrict2', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('methode_clustering', css_class='form-group col-md-4 mb-0'),
                Column('ncluster', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column(css_class='form-group col-3 offset-1'),
                Column('link', css_class='form-group col-md-2 mb-0'),
                Column('color_singleton', css_class='form-group col-md-3 mb-0'),
                css_class='form-row'
            )
        )
        super().__init__(*args, **kwargs)
        self.fields['user_restrict2'].widget.attrs['size'] = 5
        self.fields['link'].widget.attrs['size'] = 5
        revuesplit = revues.split(",")
        # Pour que revue1 apparraissent en premier
        if revue1:
            revuechoices = [(revue1, revue1)]
            for elt in revuesplit:
                if elt != revue1:
                    revuechoices.append((elt, elt))
        else:
            revuechoices = [(elt, elt) for elt in revuesplit]
        self.fields['choixrevue'] = forms.ChoiceField(choices=revuechoices)

        epoquessplit = epoques.split(",")
        # idem epoque1
        if epoque1:
            epoquechoices = [(epoque1, epoque1)]
            for elt in epoquessplit:
                if elt != epoque1:
                    epoquechoices.append((elt, elt))
        else:
            epoquechoices = [(elt, elt) for elt in epoquessplit]
        self.fields['choixepoque'] = forms.ChoiceField(choices=epoquechoices)



    class Meta:
        model = GloveRCluster
        exclude = ['modelc', 'nomresult']


class GloveClusterRedSimpleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = GloveRCluster
        exclude = ['modelc', 'nomresult']


class GloveClusterCompletForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = GloveRCluster
        fields = '__all__'


###################### WORD2VEC #######################


class Word2VecClusterRedForm(forms.ModelForm):
    def __init__(self, epoques, revues, epoque1=None, revue1=None, *args, **kwargs):
        self.helper = FormHelper()
        # see "rendering severals forms with helpers" in django crispy form
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('choixrevue', css_class='form-group col-md-4 mb-0'),
                Column('choixepoque', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('terme', css_class='form-group col-md-4 mb-0'),
                Column('nresult', css_class='form-group col-md-4 mb-0'),
                Column('user_restrict2', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('methode_clustering', css_class='form-group col-md-4 mb-0'),
                Column('ncluster', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column(css_class='form-group col-3 offset-1'),
                Column('link', css_class='form-group col-md-2 mb-0'),
                Column('color_singleton', css_class='form-group col-md-3 mb-0'),
                css_class='form-row'
            )
        )
        super().__init__(*args, **kwargs)
        self.fields['user_restrict2'].widget.attrs['size'] = 5
        self.fields['link'].widget.attrs['size'] = 5
        revuesplit = revues.split(",")
        # Pour que revue1 apparraissent en premier
        if revue1:
            revuechoices = [(revue1, revue1)]
            for elt in revuesplit:
                if elt != revue1:
                    revuechoices.append((elt, elt))
        else:
            revuechoices = [(elt, elt) for elt in revuesplit]
        self.fields['choixrevue'] = forms.ChoiceField(choices=revuechoices)

        epoquessplit = epoques.split(",")
        # idem epoque1
        if epoque1:
            epoquechoices = [(epoque1, epoque1)]
            for elt in epoquessplit:
                if elt != epoque1:
                    epoquechoices.append((elt, elt))
        else:
            epoquechoices = [(elt, elt) for elt in epoquessplit]
        self.fields['choixepoque'] = forms.ChoiceField(choices=epoquechoices)



    class Meta:
        model = Word2VecRCluster
        exclude = ['modelc', 'nomresult']


class Word2VecClusterRedSimpleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Word2VecRCluster
        exclude = ['modelc', 'nomresult']


class Word2VecClusterCompletForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Word2VecRCluster
        fields = '__all__'


##################################  FASTEXT #######################


class FastTextClusterRedForm(forms.ModelForm):
    def __init__(self, epoques, revues, epoque1=None, revue1=None, *args, **kwargs):
        self.helper = FormHelper()
        # see "rendering severals forms with helpers" in django crispy form
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('choixrevue', css_class='form-group col-md-4 mb-0'),
                Column('choixepoque', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('terme', css_class='form-group col-md-4 mb-0'),
                Column('nresult', css_class='form-group col-md-4 mb-0'),
                Column('user_restrict2', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('methode_clustering', css_class='form-group col-md-4 mb-0'),
                Column('ncluster', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column(css_class='form-group col-3 offset-1'),
                Column('link', css_class='form-group col-md-2 mb-0'),
                Column('color_singleton', css_class='form-group col-md-3 mb-0'),
                css_class='form-row'
            )
        )
        super().__init__(*args, **kwargs)
        self.fields['user_restrict2'].widget.attrs['size'] = 5
        self.fields['link'].widget.attrs['size'] = 5
        revuesplit = revues.split(",")
        # Pour que revue1 apparraissent en premier
        if revue1:
            revuechoices = [(revue1, revue1)]
            for elt in revuesplit:
                if elt != revue1:
                    revuechoices.append((elt, elt))
        else:
            revuechoices = [(elt, elt) for elt in revuesplit]
        self.fields['choixrevue'] = forms.ChoiceField(choices=revuechoices)

        epoquessplit = epoques.split(",")
        # idem epoque1
        if epoque1:
            epoquechoices = [(epoque1, epoque1)]
            for elt in epoquessplit:
                if elt != epoque1:
                    epoquechoices.append((elt, elt))
        else:
            epoquechoices = [(elt, elt) for elt in epoquessplit]
        self.fields['choixepoque'] = forms.ChoiceField(choices=epoquechoices)



    class Meta:
        model = FastTextRCluster
        exclude = ['modelc', 'nomresult']



class FastTextClusterRedSimpleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    class Meta:
        model = FastTextRCluster
        exclude = ['modelc', 'nomresult']


class FastTextClusterCompletForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = FastTextRCluster
        fields = '__all__'

