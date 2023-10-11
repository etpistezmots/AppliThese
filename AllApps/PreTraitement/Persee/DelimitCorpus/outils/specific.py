def NombrePage(page):
    decoup = page.split("-")
    if len(decoup) == 1:
        nbrepage = 1
    else:
        premierepage = int(decoup[0])
        dernierepage = int(decoup[1])
        nbrepage = dernierepage - premierepage + 1
    return nbrepage



def TraceGraphMotPage(listdata, interval):
    # si min(lisdata) = 335 --> minval = 300
    # si min(lisdata) = 2135 --> minval = 2200

    minval = int(min(listdata) / 100) * 100
    maxval = (int(max(listdata) / 100) + 1) * 100

    donneex = []
    donneey = []

    for i, j in enumerate(range(minval, maxval + 100, interval)):
        if i == 0:
            InfInterval = j
        if i > 0:
            SupInterval = j
            count = 0
            for elt in listdata:
                if elt >= InfInterval and elt <= SupInterval:
                    count += 1

            # astuce pour respecter la représentation sous forme d'intervalle
            donneex.append(InfInterval + 0.1)
            donneey.append(count)
            donneex.append(SupInterval - 0.1)
            donneey.append(count)
            InfInterval = j


    return ((donneex, donneey))