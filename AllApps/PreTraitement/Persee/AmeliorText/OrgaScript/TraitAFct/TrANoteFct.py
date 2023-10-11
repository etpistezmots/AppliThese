from AllApps.PreTraitement.Persee.AmeliorText.OrgaScript.TraitAFct.TrACoordGraphSimpleFct import InsertNewCoordGraphSimple


def InsertNewNote(reduction, donnees):

    SupprNoteBio = donnees['SupprNoteBio']
    SupprNoteEdito = donnees['SupprNoteEdito']
    SupprNoteBasDePage = donnees['SupprNoteBasDePage']

    # A revoir car n'est pas très efficace ...
    if SupprNoteBio:
        InsertNewCoordGraphSimple(reduction, donnees, "notebio")
    if SupprNoteEdito:
        InsertNewCoordGraphSimple(reduction, donnees, "noteedito")
    if SupprNoteBasDePage:
        InsertNewCoordGraphSimple(reduction, donnees, "note")


