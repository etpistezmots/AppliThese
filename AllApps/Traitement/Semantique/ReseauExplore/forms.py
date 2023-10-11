from django import forms
from .models import  FastTextRExplo, GloveRExplo, Word2VecRExplo
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column



################################# WORD2VEC ###############################


class Word2VecResRedForm(forms.ModelForm):

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
                Column('nresult', css_class='form-group col-md-2 mb-0'),
                Column('user_restrict2', css_class='form-group col-md-2 mb-0'),
                css_class='form-row'
            )
        )
        super().__init__(*args, **kwargs)
        self.fields['nresult'].widget.attrs['size'] = 3
        self.fields['user_restrict2'].widget.attrs['size'] = 3
        revuesplit = revues.split(",")
        # Pour que revue1 apparraisse en premier
        if revue1 :
            revuechoices = [(revue1, revue1)]
            for elt in revuesplit:
                if elt != revue1:
                    revuechoices.append((elt,elt))
        else:
            revuechoices = [(elt, elt) for elt in revuesplit]
        self.fields['choixrevue'] = forms.ChoiceField(choices=revuechoices)

        epoquessplit= epoques.split(",")
        # idem epoque1
        if epoque1 :
            epoquechoices = [(epoque1, epoque1)]
            for elt in epoquessplit:
                if elt != epoque1:
                    epoquechoices.append((elt,elt))
        else:
            epoquechoices = [(elt,elt) for elt in epoquessplit]
        self.fields['choixepoque'] = forms.ChoiceField(choices=epoquechoices)


    class Meta:
        model = Word2VecRExplo
        exclude = ['modelc','nomresult','comment','indexnode','indexedge','oriented']



class Word2VecResRedSimpleForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Word2VecRExplo
        exclude = ['modelc','nomresult','comment','indexnode','indexedge','oriented']



class Word2VecResCompletForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Word2VecRExplo
        fields = '__all__'

########################### GLOVE ###################################


class GloveResRedForm(forms.ModelForm):

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
                Column('nresult', css_class='form-group col-md-2 mb-0'),
                Column('user_restrict2', css_class='form-group col-md-2 mb-0'),
                css_class='form-row'
            )
        )
        super().__init__(*args, **kwargs)
        self.fields['nresult'].widget.attrs['size'] = 3
        self.fields['user_restrict2'].widget.attrs['size'] = 3
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
        model = GloveRExplo
        exclude = ['modelc','nomresult','comment','indexnode','indexedge','oriented']



class GloveResRedSimpleForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    class Meta:
        model = GloveRExplo
        exclude = ['modelc','nomresult','comment','indexnode','indexedge','oriented']



class GloveResCompletForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = GloveRExplo
        fields = '__all__'

####################################  FAST TEXT  ######################################


class FastTextResRedForm(forms.ModelForm):
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
                Column('nresult', css_class='form-group col-md-2 mb-0'),
                Column('user_restrict2', css_class='form-group col-md-2 mb-0'),
                css_class='form-row'
            )
        )
        super().__init__(*args, **kwargs)
        self.fields['nresult'].widget.attrs['size'] = 3
        self.fields['user_restrict2'].widget.attrs['size'] = 3

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
        # idem revue
        if epoque1:
            epoquechoices = [(epoque1, epoque1)]
            for elt in epoquessplit:
                if elt != epoque1:
                    epoquechoices.append((elt, elt))
        else:
            epoquechoices = [(elt, elt) for elt in epoquessplit]
        self.fields['choixepoque'] = forms.ChoiceField(choices=epoquechoices)


    class Meta:
        model = FastTextRExplo
        exclude = ['modelc','nomresult','comment','indexnode','indexedge','oriented']



class FastTextResRedSimpleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = FastTextRExplo
        exclude = ['modelc','nomresult','comment','indexnode','indexedge','oriented']





class FastTextResCompletForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = FastTextRExplo
        fields = '__all__'

