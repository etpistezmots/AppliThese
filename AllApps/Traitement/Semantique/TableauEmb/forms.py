from django import forms
from .models import FastText, FastTextR, Glove, GloveR, Word2Vec, Word2VecR
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column

################################# WORD2VEC ###############################

class Word2VecForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        # see "rendering severals forms with helpers" in django crispy form
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('nom', css_class='form-group col-md-4 mb-0'),
                Column('user_restrict', css_class='form-group col-md-4 mb-0'),
                Column('CorpusFinRef', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('revue', css_class='form-group col-md-4 mb-0'),
                Column('epoque', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('architecture', css_class='form-group col-md-4 mb-0'),
                Column('embedding_size', css_class='form-group col-md-4 mb-0'),
                Column('context_size', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('min_occurrences', css_class='form-group col-md-4 mb-0'),
                Column('num_epochs', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            )
        )

        super().__init__(*args, **kwargs)
        self.fields['user_restrict'].widget.attrs['size'] = 5
        self.fields['epoque'].widget.attrs['size'] = 60


    def clean(self):
        cleaned_data = super().clean()
        # quelques tests basiques : voir fonction en fin de cette poage
        testbase(cleaned_data, self)

    class Meta:
        model = Word2Vec
        fields = '__all__'



# Partie result
class Word2VecResRedForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):

        self.helper = FormHelper()
        # see "rendering severals forms with helpers" in django crispy form
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('terme', css_class='form-group col-md-4 mb-0'),
                Column('nresult', css_class='form-group col-md-4 mb-0'),
                Column('user_restrict2', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            )
        )
        super().__init__(*args, **kwargs)
        self.fields['user_restrict2'].widget.attrs['size'] = 5

    def clean(self):
        cleaned_data = super().clean()
        usertest = cleaned_data.get("user_restrict2")
        testmeuser(usertest, self)
        nresulttest = cleaned_data.get("nresult")
        testmenresult(nresulttest, self)


    class Meta:
        model = Word2VecR
        exclude = ['modelc','nomresult']



class Word2VecResCompletForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        usertest = cleaned_data.get("user_restrict2")
        testmeuser(usertest, self)
        nresulttest = cleaned_data.get("nresult")
        testmenresult(nresulttest, self)


    class Meta:
        model = Word2VecR
        fields = '__all__'

########################### GLOVE ###################################

class GloveForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):

        self.helper = FormHelper()
        # see "rendering severals forms with helpers" in django crispy form
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('nom', css_class='form-group col-md-4 mb-0'),
                Column('user_restrict', css_class='form-group col-md-4 mb-0'),
                Column('CorpusFinRef', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('revue', css_class='form-group col-md-4 mb-0'),
                Column('epoque', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('embedding_size', css_class='form-group col-md-4 mb-0'),
                Column('context_size', css_class='form-group col-md-4 mb-0'),
                Column('min_occurrences', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('num_epochs', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            )
        )

        super().__init__(*args, **kwargs)
        self.fields['user_restrict'].widget.attrs['size'] = 5
        self.fields['epoque'].widget.attrs['size'] = 60


    def clean(self):
        cleaned_data = super().clean()
        # quelques tests basiques : voir fonction en fin de cette poage
        testbase(cleaned_data, self)


    class Meta:
        model = Glove
        fields = '__all__'



# Partie Result
class GloveResRedForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):

        self.helper = FormHelper()
        # see "rendering severals forms with helpers" in django crispy form
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('terme', css_class='form-group col-md-4 mb-0'),
                Column('nresult', css_class='form-group col-md-4 mb-0'),
                Column('user_restrict2', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            )
        )
        super().__init__(*args, **kwargs)
        self.fields['user_restrict2'].widget.attrs['size'] = 5

    def clean(self):
        cleaned_data = super().clean()
        usertest = cleaned_data.get("user_restrict2")
        testmeuser(usertest, self)
        nresulttest = cleaned_data.get("nresult")
        testmenresult(nresulttest, self)


    class Meta:
        model = GloveR
        exclude = ['modelc','nomresult']



class GloveResCompletForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        usertest = cleaned_data.get("user_restrict2")
        testmeuser(usertest, self)
        nresulttest = cleaned_data.get("nresult")
        testmenresult(nresulttest, self)

    class Meta:
        model = GloveR
        fields = '__all__'



####################################  FAST TEXT  ######################################

class FastTextForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):

        self.helper = FormHelper()
        # see "rendering severals forms with helpers" in django crispy form
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('nom', css_class='form-group col-md-4 mb-0'),
                Column('user_restrict', css_class='form-group col-md-4 mb-0'),
                Column('CorpusFinRef', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('revue', css_class='form-group col-md-4 mb-0'),
                Column('epoque', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('architecture', css_class='form-group col-md-4 mb-0'),
                Column('embedding_size', css_class='form-group col-md-4 mb-0'),
                Column('context_size', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('min_occurrences', css_class='form-group col-md-4 mb-0'),
                Column('num_epochs', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('min_n', css_class='form-group col-md-4 mb-0'),
                Column('max_n', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
        )

        super().__init__(*args, **kwargs)
        self.fields['user_restrict'].widget.attrs['size'] = 5
        self.fields['epoque'].widget.attrs['size'] = 60


    def clean(self):
        cleaned_data = super().clean()
        # quelques tests basiques : voir fonction en fin de cette poage
        testbase(cleaned_data, self)

    class Meta:
        model = FastText
        fields = '__all__'


# Partie Result
class FastTextResRedForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        # see "rendering severals forms with helpers" in django crispy form
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('terme', css_class='form-group col-md-4 mb-0'),
                Column('nresult', css_class='form-group col-md-4 mb-0'),
                Column('user_restrict2', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            )
        )
        super().__init__(*args, **kwargs)
        self.fields['user_restrict2'].widget.attrs['size'] = 5

    def clean(self):
        cleaned_data = super().clean()
        usertest = cleaned_data.get("user_restrict2")
        testmeuser(usertest, self)
        nresulttest = cleaned_data.get("nresult")
        testmenresult(nresulttest, self)

    class Meta:
        model = FastTextR
        exclude = ['modelc', 'nomresult']

class FastTextResCompletForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        usertest = cleaned_data.get("user_restrict2")
        testmeuser(usertest, self)
        nresulttest = cleaned_data.get("nresult")
        testmenresult(nresulttest, self)

    class Meta:
        model = FastTextR
        fields = '__all__'


################ FONCTIONS TEST ###################################
def testbase(cleaned_data, testme):
    nomtest = cleaned_data.get("nom")
    testmenom(nomtest,testme)
    usertest = cleaned_data.get("user_restrict")
    testmeuser(usertest, testme)
    epoquetest = cleaned_data.get("epoque")
    testmeepoque(epoquetest, testme)



def testmenom(nomtest, testme):
    if "." in nomtest or " " in nomtest:
        msg = "le nom n'est pas un nom de fichier de nom valide"
        testme.add_error("nom", msg)
    if nomtest == "Achoisir":
        msg = "merci de choisir un autre nom..."
        testme.add_error("nom", msg)


def testmeuser(usertest, testme):
    splittest = usertest.split(",")
    listusers = User.objects.all().values_list("id", flat=True)
    for elt in splittest:
        if not elt.isdigit():
            msg = "user doit de la forme entier ou entiers séparés par virgule"
            testme.add_error("user_restrict", msg)
        else :
            if elt != "0" and int(elt) not in listusers:
                msg = elt + " n'est pas id d'user valide"
                testme.add_error("user_restrict", msg)


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



def testmenresult(nresulttest, testme):
    if nresulttest >1000:
        msg = "le nombre d'affichage des résultat a été limité à 1000"
        testme.add_error("nresult", msg)



