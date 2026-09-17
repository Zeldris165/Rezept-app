"""
praeferenzen.py
================
Ernährungspräferenzen als einfacher Zutaten-Stichwort-Filter (kein
Rezept-Tagging nötig). Bewusst simpel gehalten - siehe Hinweis in der UI:
das ist eine Orientierungshilfe, kein Ersatz für's Lesen der Zutatenliste
bei echten Unverträglichkeiten.
"""

PRAEFERENZEN = {
    "vegetarisch": "Vegetarisch",
    "vegan": "Vegan",
    "glutenfrei": "Glutenfrei",
    "laktosefrei": "Laktosefrei",
    "histaminarm": "Histaminarm",
    "fructosefrei": "Fructosefrei",
    "low_carb": "Low-Carb",
}

FLEISCH_FISCH_PROTEINE = {"Huhn", "Fisch", "Rind", "Schwein", "Lamm"}

# Zutaten-Stichworte (klein geschrieben), bei denen ein Rezept die jeweilige
# Präferenz NICHT erfüllt. Bewusst grob/konservativ gehalten.
AUSSCHLUSS_KEYWORDS = {
    "vegan": [
        "käse", "feta", "mozzarella", "sahne", "milch", "butter", "joghurt",
        "sauerrahm", "ei", "eier", "honig", "fischsauce", "austernsauce",
    ],
    "glutenfrei": [
        "mehl", "nudeln", "spaghetti", "teigwrapper", "pizzateig", "brot",
        "eiernudeln", "teigwaren", "suppennudeln",
    ],
    "laktosefrei": [
        "käse", "feta", "mozzarella", "sahne", "milch", "butter", "joghurt", "sauerrahm",
    ],
    "histaminarm": [
        "käse", "feta", "mozzarella", "sauerrahm", "joghurt", "wein", "essig",
        "sojasauce", "schokolade", "thunfisch", "tomate", "spinat",
    ],
    "fructosefrei": [
        "honig", "zucker", "apfel", "zwiebel", "tomate",
    ],
    "low_carb": [
        "reis", "nudeln", "spaghetti", "kartoffel", "zucker", "mehl", "brot",
        "pizzateig", "teigwrapper", "eiernudeln", "süßkartoffel",
    ],
}


def rezept_erfuellt_praeferenzen(protein_typ: str, zutaten_namen: list[str], aktive_codes: list[str]) -> bool:
    """Prüft, ob ein Rezept (anhand Protein-Typ + Zutatennamen) alle aktiven
    Präferenzen erfüllt. Rein Stichwort-basiert, siehe Modul-Hinweis oben."""
    namen_klein = [n.lower() for n in zutaten_namen]

    for code in aktive_codes:
        if code == "vegetarisch":
            if protein_typ in FLEISCH_FISCH_PROTEINE:
                return False
        elif code == "vegan":
            if protein_typ in FLEISCH_FISCH_PROTEINE:
                return False
            if any(any(kw in n for kw in AUSSCHLUSS_KEYWORDS["vegan"]) for n in namen_klein):
                return False
        else:
            keywords = AUSSCHLUSS_KEYWORDS.get(code, [])
            if any(any(kw in n for kw in keywords) for n in namen_klein):
                return False

    return True
