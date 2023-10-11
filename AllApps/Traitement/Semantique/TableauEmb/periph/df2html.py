import pandas as pd

def transform(df):

    test = """ """

    if not df.empty:

        # header
        test = test + """<table class="dataframe" border="1"> <thead> <tr> <th></th>"""

        # label colonnes entourées de <th>
        for elt in list(df):
            test = test + """<th>""" + elt + """</th>"""

        test = test + """</tr> </thead> <tbody>"""

        # lignes entouréesen amont de <tr> et label de </th>
        for elt in list(df.index):

            test = test + """<tr>"""
            test = test + """<th>""" + str(elt) + """</th>"""

            for elt1 in list(df.loc[elt, :]):
                if elt1 == "":
                    test = test + """<td> </td>"""
                else:
                    splitelt1 = elt1.split("\n")
                    test = test + """<td>"""
                    for i,elt2 in enumerate(splitelt1[:-1]):
                        if i == 0:
                            test = test  + elt2 + """</br>"""
                        else:
                            test = test + """<br>""" + elt2 + """</br>"""
                    test = test + """</td>"""

            test = test + """</tr>"""

        test = test + """</tbody> </table>"""

    return test

def transformcolor(df, dfsame):

    test = """ """

    if not df.empty:

        # header
        test = test + """<table class="dataframe" border="1"> <thead> <tr> <th></th>"""

        # label colonnes entourées de <th>
        for elt in list(df):
            test = test + """<th>""" + elt + """</th>"""

        test = test + """</tr> </thead> <tbody>"""

        # lignes entourées en amont de <tr> et label de </th>
        for l,elt in enumerate(list(df.index)):

            test = test + """<tr>"""
            test = test + """<th>""" + str(elt) + """</th>"""

            for c,elt1 in enumerate(list(df.loc[elt, :])):
                if elt1 == "":
                    test = test + """<td> </td>"""
                else:
                    sametermes = dfsame.iloc[l,c].split()
                    splitelt1 = elt1.split("\n")
                    test = test + """<td>"""
                    # ENIGME ICI : pourquoi faut il enlever le -1 par rapport à précedemment
                    # ça marche comme ça mais je n'ai pas plus cherché
                    for i,elt2 in enumerate(splitelt1):
                        el2split = elt2.split(" ")
                        if el2split[0] in sametermes:
                            if i == 0:
                                test = test  + """<spam class="jaune">""" + elt2 + """</spam>""" + """</br>"""
                            else:
                                test = test + """<br>""" + """<spam class="jaune">""" + elt2 + """</spam>""" + """</br>"""
                        else:
                            if i == 0:
                                test = test + elt2 + """</br>"""
                            else:
                                test = test + """<br>""" + elt2 + """</br>"""
                    test = test + """</td>"""

            test = test + """</tr>"""

        test = test + """</tbody> </table>"""

    return test


def transformquanti(df):

    test = """ """

    if not df.empty:

        # header
        test = test + """<table class="dataframe" border="1"> <thead> <tr> <th></th>"""

        # label colonnes entourées de <th>
        for elt in list(df):
            test = test + """<th>""" + elt + """</th>"""

        test = test + """</tr> </thead> <tbody>"""

        # lignes entourées en amont de <tr> et label de </th>
        for elt in list(df.index):

            test = test + """<tr>"""
            test = test + """<th>""" + str(elt) + """</th>"""

            for elt1 in list(df.loc[elt, :]):
                test = test + """<td>""" + str(round(elt1,2)) + """""""</td>"""

            test = test + """</tr>"""

        test = test + """</tbody> </table>"""

    return test


def inverse(test):

    PartieLabelColonne = test.split("""<thead> <tr> <th></th>""")[1].rsplit("""</tr> </thead> <tbody>""")[0]

    LabelsColonnesBrut = PartieLabelColonne.split("<th>")
    LabelsColonnes = []
    for elt in LabelsColonnesBrut[1:]:
        LabelsColonnes.append(elt[:-5])

    PartieLigne = test.split("""<tbody><tr>""")[1].rsplit("""</tbody> </table>""")[0]
    DecoupLigneLabelDepart = PartieLigne.split("<th>")
    LabelsLignes = []
    ContenusLignes = []
    for elt in DecoupLigneLabelDepart[1:]:
        DecoupLigneLabelFin = elt.split("</th>")[0]
        LabelsLignes.append(DecoupLigneLabelFin)

        DecoupLigneContenuDepart = elt.split("</th>")[1].split("<td>")
        ContenuLigneEnCours = []
        # mise en forme du contenu
        for elt1 in DecoupLigneContenuDepart[1:]:
            Contenu = elt1.rsplit("</td>")[0].replace("<br>", "").replace("</br>", "\n")
            # enleve le \n finale
            ContenuLigneEnCours.append(Contenu[:-1])
        ContenusLignes.append(ContenuLigneEnCours)

    # Create Dico by column
    DicoCreation = {}
    for i, elt in enumerate(LabelsColonnes):
        DicoCreation[elt] = []
        for elt1 in ContenusLignes:
            DicoCreation[elt].append(elt1[i])

    df = pd.DataFrame(DicoCreation, index=LabelsLignes)

    return df,LabelsColonnes,LabelsLignes


def reducehtml(basehtml,n, revueselect):
    newhtml = []
    Decoup = basehtml.split("<tr>")
    for i, elt in enumerate(Decoup):
        if i <= 1:
            newhtml.append(elt)
        elif i > 1 and elt[4:7] == "Esp" and revueselect == "Ann":
            continue
        elif i > 1 and elt[4:7] == "Ann" and revueselect == "Esp":
            continue
        else:
            parthtml = []
            Decoup2 = elt.split("<td>")
            for j, elt2 in enumerate(Decoup2):
                if j == 0:
                    parthtml.append(elt2)
                else:
                    if elt2.count("</br>") > n:
                        newelt = elt2.split("</br>", n)
                        parthtml.append('</br>'.join(newelt[:-1]) + '</br></td>')
                    else:
                        parthtml.append(elt2)
            joinparthtml = '<td>'.join(parthtml)
            newhtml.append(joinparthtml + '</tr>')

    joinnewhtml = '<tr>'.join(newhtml)
    resulthtml = joinnewhtml + "</tbody> </table>"
    return resulthtml
