from django import forms
from .models import GloveDiachro, Word2VecDiachro, FastTextDiachro
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column


######################## FORMULAIRE REDUIT PREVALIDATION ################

                ############### GLOVE #######

class GloveDiachroRedForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        # see "rendering severals forms with helpers" in django crispy form
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('terme', css_class='form-group col-md-3 mb-0'),
                Column('nresult', css_class='form-group col-md-3 mb-0'),
                Column('ncluster', css_class='form-group col-md-3 mb-0'),
                Column('user_restrict2', css_class='form-group col-md-2 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('methode_clustering', css_class='form-group col-md-4 mb-0'),
                Column('calculPoidsLabel', css_class='form-group col-md-4 mb-0'),
            ),
            Row(
                Column('taillecluster', css_class='form-group col-md-6 mb-0'),
                Column('stop_mots', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(Column('selectLink', css_class='form-group col-md-4 mb-0'),
                Column('couleursRevues', css_class='form-group col-md-4 mb-0'),
                Column('compareJustNewRevue', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
                )
        )

        super().__init__(*args, **kwargs)
        self.fields['nresult'].widget.attrs['size'] = 20
        self.fields['user_restrict2'].widget.attrs['size'] = 4
        self.fields['ncluster'].widget.attrs['size'] = 20
        self.fields['stop_mots'].widget.attrs['size'] = 50

    def clean(self):
        cleaned_data = super().clean()
        usertest = cleaned_data.get("user_restrict2")
        testmeuser(usertest, self)
        nresulttest = cleaned_data.get("nresult")
        TestNbTermesIntPositif(nresulttest, self)
        nclustertest = cleaned_data.get("ncluster")
        TestNbClustersIntPositif(nclustertest, self)

    class Meta:
        model = GloveDiachro
        exclude = ['modelc', 'nomresult','seuil100']


                 ###############  WORD2VEC ##########

class Word2VecDiachroRedForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        # see "rendering severals forms with helpers" in django crispy form
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('terme', css_class='form-group col-md-3 mb-0'),
                Column('nresult', css_class='form-group col-md-3 mb-0'),
                Column('ncluster', css_class='form-group col-md-3 mb-0'),
                Column('user_restrict2', css_class='form-group col-md-2 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('methode_clustering', css_class='form-group col-md-4 mb-0'),
                Column('calculPoidsLabel', css_class='form-group col-md-4 mb-0'),
            ),
            Row(
                Column('taillecluster', css_class='form-group col-md-6 mb-0'),
                Column('stop_mots', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(Column('selectLink', css_class='form-group col-md-4 mb-0'),
                Column('couleursRevues', css_class='form-group col-md-4 mb-0'),
                Column('compareJustNewRevue', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
                )
        )

        super().__init__(*args, **kwargs)
        self.fields['nresult'].widget.attrs['size'] = 20
        self.fields['user_restrict2'].widget.attrs['size'] = 4
        self.fields['ncluster'].widget.attrs['size'] = 20
        self.fields['stop_mots'].widget.attrs['size'] = 50

    def clean(self):
        cleaned_data = super().clean()
        usertest = cleaned_data.get("user_restrict2")
        testmeuser(usertest, self)
        nresulttest = cleaned_data.get("nresult")
        TestNbTermesIntPositif(nresulttest, self)
        nclustertest = cleaned_data.get("ncluster")
        TestNbClustersIntPositif(nclustertest, self)

    class Meta:
        model = Word2VecDiachro
        exclude = ['modelc', 'nomresult', 'seuil100']

               ################  FASTTEXT ################

class FastTextDiachroRedForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        # see "rendering severals forms with helpers" in django crispy form
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('terme', css_class='form-group col-md-3 mb-0'),
                Column('nresult', css_class='form-group col-md-3 mb-0'),
                Column('ncluster', css_class='form-group col-md-3 mb-0'),
                Column('user_restrict2', css_class='form-group col-md-2 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('methode_clustering', css_class='form-group col-md-4 mb-0'),
                Column('calculPoidsLabel', css_class='form-group col-md-4 mb-0'),
            ),
            Row(
                Column('taillecluster', css_class='form-group col-md-6 mb-0'),
                Column('stop_mots', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(Column('selectLink', css_class='form-group col-md-4 mb-0'),
                Column('couleursRevues', css_class='form-group col-md-4 mb-0'),
                Column('compareJustNewRevue', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
                )
        )

        super().__init__(*args, **kwargs)
        self.fields['nresult'].widget.attrs['size'] = 20
        self.fields['user_restrict2'].widget.attrs['size'] = 4
        self.fields['ncluster'].widget.attrs['size'] = 20
        self.fields['stop_mots'].widget.attrs['size'] = 50

    def clean(self):
        cleaned_data = super().clean()
        usertest = cleaned_data.get("user_restrict2")
        testmeuser(usertest, self)
        nresulttest = cleaned_data.get("nresult")
        TestNbTermesIntPositif(nresulttest, self)
        nclustertest = cleaned_data.get("ncluster")
        TestNbClustersIntPositif(nclustertest, self)

    class Meta:
        model = FastTextDiachro
        exclude = ['modelc', 'nomresult', 'seuil100']


######################## FORMULAIRE COMPLET VALIDATION ################

        ############### GLOVE #######

class GloveDiachroCompletForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def clean(self):
        cleaned_data = super().clean()
        usertest = cleaned_data.get("user_restrict2")
        testmeuser(usertest, self)
        nresulttest = cleaned_data.get("nresult")
        TestNbTermesIntPositif(nresulttest, self)
        nclustertest = cleaned_data.get("ncluster")
        TestNbClustersIntPositif(nclustertest, self)

    class Meta:
        model = GloveDiachro
        fields = '__all__'



            ###############  WORD2VEC ##########

class Word2VecDiachroCompletForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        usertest = cleaned_data.get("user_restrict2")
        testmeuser(usertest, self)
        nresulttest = cleaned_data.get("nresult")
        TestNbTermesIntPositif(nresulttest, self)
        nclustertest = cleaned_data.get("ncluster")
        TestNbClustersIntPositif(nclustertest, self)

    class Meta:
        model = Word2VecDiachro
        fields = '__all__'

            ################  FASTTEXT ################

class FastTextDiachroCompletForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def clean(self):
        cleaned_data = super().clean()
        usertest = cleaned_data.get("user_restrict2")
        testmeuser(usertest, self)
        nresulttest = cleaned_data.get("nresult")
        TestNbTermesIntPositif(nresulttest, self)
        nclustertest = cleaned_data.get("ncluster")
        TestNbClustersIntPositif(nclustertest, self)

    class Meta:
        model = FastTextDiachro
        fields = '__all__'


###################### FONCTIONS TEST ###################################


def TestNbTermesIntPositif(nresult, testme):
    virgsplit = nresult.split(",")
    if len(virgsplit)==1:
        if not(virgsplit[0].isdigit()):
            msg = "Le nombre de termes demandé est invalide"
            testme.add_error("nresult", msg)
        else:
            if int(virgsplit[0])==0 or int(virgsplit[0])>500:
                msg = "Le nombre de termes demandé est invalide (>0 et <500)"
                testme.add_error("nresult", msg)

    else:
        for elt in virgsplit:
            if not(elt.isdigit()):
                msg = "Le nombre de termes demandé est invalide"
                testme.add_error("nresult", msg)
            else:
                if int(elt)==0 or int(elt)>500:
                    msg = "Le nombre de termes demandé est invalide (>0 et <500)"
                    testme.add_error("nresult", msg)



def TestNbClustersIntPositif(ncluster, testme):
    virgsplit = ncluster.split(",")
    if len(virgsplit)==1:
        if not(virgsplit[0].isdigit()):
            msg = "Le nombre de clusters demandé est invalide"
            testme.add_error("ncluster", msg)
        else:
            if int(virgsplit[0])==0 or int(virgsplit[0])>20:
                msg = "Le nombre de clusters demandé est invalide (>0 et <20)"
                testme.add_error("ncluster", msg)
    else:
        for elt in virgsplit:
            if not(elt.isdigit()):
                msg = "Le nombre de clusters demandé est invalide"
                testme.add_error("ncluster", msg)
            else:
                if int(elt) == 0 or int(elt) > 20:
                    msg = "Le nombre de clusters demandé est invalide (>0 et <20)"
                    testme.add_error("ncluster", msg)


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

