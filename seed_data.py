"""
seed_data.py
============
Befüllt die Datenbank mit ein paar Beispiel-Nutzern und mehreren Beispielrezepten
(inkl. Illustration und Zutaten). Kann mehrfach ausgeführt werden, ohne Duplikate zu
erzeugen.

Ausführen mit: python seed_data.py
"""

import bcrypt
from database import get_connection, init_db

# ---------------------------------------------------------------
# Beispiel-Nutzer (Passwörter nur zum Testen - im echten Betrieb
# natürlich nicht im Klartext im Code!)
# ---------------------------------------------------------------
BEISPIEL_NUTZER = [
    {"username": "ewald", "name": "Ewald", "passwort": "testpasswort1"},
    {"username": "freund1", "name": "Freund 1", "passwort": "testpasswort2"},
]

# ---------------------------------------------------------------
# Eine Illustration pro Protein-Typ (liegt lokal unter assets/illustrations/)
# ---------------------------------------------------------------
ILLUSTRATION_JE_PROTEIN = {
    "Huhn": "assets/flaticon/haehnchengerichte.png",
    "Fisch": "assets/flaticon/fischgerichte.png",
    "Rind": "assets/flaticon/rindgerichte.png",
    "Schwein": "assets/flaticon/schweinegerichte.png",
    "Lamm": "assets/flaticon/lammgerichte.png",
    "Vegetarisch": "assets/flaticon/gemuesegerichte.png",
}

# Manche Kategorien haben ein eigenes Icon, das Vorrang vor dem Protein-Icon hat
ILLUSTRATION_JE_KATEGORIE = {
    "Suppe": "assets/flaticon/suppen.png",
    "Wokgericht": "assets/flaticon/wokgerichte.png",
    "Reisgericht": "assets/flaticon/reisgerichte.png",
    "Pastagericht": "assets/flaticon/pastagerichte.png",
    "Salat": "assets/flaticon/salate.png",
    "Beilage": "assets/flaticon/beilagen.png",
    "Auflauf": "assets/flaticon/auflaeufe.png",
    "Curry": "assets/flaticon/currys.png",
    "Dumpling": "assets/flaticon/dumplings.png",
    "Pizza": "assets/flaticon/pizzagerichte.png",
    "Dessert": "assets/flaticon/desserts.png",
    "Vorspeise": "assets/flaticon/salate.png",
    "Frühstück": "assets/illustrations/fruehstueck.svg",
    "Herzhaftes Frühstück": "assets/flaticon/fruehstueck_herzhaft.png",
    "Süßes Frühstück": "assets/flaticon/fruehstueck_suess.png",
}


def waehle_illustration(protein_typ: str, kategorie: str) -> str:
    """Kategorie-Icon hat Vorrang (z.B. Suppentopf für alle Suppen),
    sonst wird nach Protein-Typ gewaehlt."""
    if kategorie in ILLUSTRATION_JE_KATEGORIE:
        return ILLUSTRATION_JE_KATEGORIE[kategorie]
    return ILLUSTRATION_JE_PROTEIN.get(protein_typ)

# ---------------------------------------------------------------
# Beispielrezepte inkl. Zutaten und ausführlicher, ganzsätziger Zubereitung
# ---------------------------------------------------------------
BEISPIEL_REZEPTE = [
    {
        "name": "Klassische Spiegeleier auf Toast",
        "protein_typ": "Vegetarisch",
        "schwierigkeit": "einfach",
        "kategorie": "Herzhaftes Frühstück",
        "gang": "Hauptgang",
        "mahlzeiten": "Frühstück",
        "bild_override": "assets/flaticon/fr_spiegelei.png",
        "zubereitungszeit_min": 10,
        "portionen_basis": 2,
        "kalorien_pro_portion": 320,
        "zubereitung": (
            "Erhitze etwas Butter oder Öl in einer beschichteten Pfanne bei "
            "mittlerer Hitze.\n"
            "Schlage die Eier vorsichtig einzeln in die Pfanne, sodass das "
            "Eigelb nicht zerläuft.\n"
            "Lass die Eier bei niedriger bis mittlerer Hitze stocken, bis das "
            "Eiweiß fest, das Eigelb aber noch flüssig ist - das dauert etwa 3 "
            "bis 4 Minuten. Für ein durchgegartes Eigelb einfach etwas länger "
            "braten.\n"
            "Toaste in der Zwischenzeit die Brotscheiben knusprig.\n"
            "Würze die Spiegeleier mit Salz und Pfeffer und lege sie auf den "
            "Toast.\n"
            "Sofort servieren, solange das Eigelb noch warm und cremig ist."
        ),
        "zutaten": [
            ("Eier", 4, "Stück"),
            ("Toastbrot", 4, "Scheiben"),
            ("Butter", 1, "EL"),
        ],
    },
    {
        "name": "Weiches Frühstücksei mit Toast-Soldaten",
        "protein_typ": "Vegetarisch",
        "schwierigkeit": "einfach",
        "kategorie": "Herzhaftes Frühstück",
        "gang": "Hauptgang",
        "mahlzeiten": "Frühstück",
        "bild_override": "assets/flaticon/fr_ei_becher.png",
        "zubereitungszeit_min": 10,
        "portionen_basis": 2,
        "kalorien_pro_portion": 220,
        "zubereitung": (
            "Bringe einen kleinen Topf mit Wasser zum Kochen.\n"
            "Lass die Eier vorsichtig mit einem Löffel ins kochende Wasser "
            "gleiten und koche sie für genau 5 bis 6 Minuten für ein weiches, "
            "cremiges Eigelb.\n"
            "Nimm die Eier heraus und schrecke sie kurz mit kaltem Wasser ab, "
            "damit sie sich leichter köpfen lassen und nicht nachgaren.\n"
            "Toaste in der Zwischenzeit die Brotscheiben und schneide sie in "
            "schmale Streifen ('Soldaten').\n"
            "Setze die Eier in Eierbecher, schlage die Spitze vorsichtig ab und "
            "würze mit etwas Salz und Pfeffer.\n"
            "Serviere die Eier sofort mit den Toast-Streifen zum Eintunken."
        ),
        "zutaten": [
            ("Eier", 2, "Stück"),
            ("Toastbrot", 3, "Scheiben"),
        ],
    },
    {
        "name": "Eier Benedikt mit Sauce Hollandaise",
        "protein_typ": "Schwein",
        "schwierigkeit": "aufwaendig",
        "kategorie": "Herzhaftes Frühstück",
        "gang": "Hauptgang",
        "mahlzeiten": "Frühstück",
        "bild_override": "assets/flaticon/fr_ei_benedikt.png",
        "zubereitungszeit_min": 35,
        "portionen_basis": 2,
        "kalorien_pro_portion": 520,
        "zubereitung": (
            "Schmelze für die Sauce Hollandaise die Butter langsam in einem "
            "kleinen Topf, ohne sie braun werden zu lassen.\n"
            "Verquirle die Eigelbe mit dem Zitronensaft und einem Spritzer "
            "Wasser in einer hitzebeständigen Schüssel über einem Wasserbad, "
            "bis die Masse cremig und leicht schaumig wird.\n"
            "Gieße die geschmolzene Butter unter ständigem Rühren in dünnem "
            "Strahl in die Eigelbmasse, bis eine dickliche, glatte Sauce "
            "entsteht. Mit Salz abschmecken und warmhalten.\n"
            "Bringe einen Topf Wasser mit einem Schuss Essig zum leichten "
            "Köcheln. Erzeuge mit einem Löffel einen Strudel und lass die Eier "
            "einzeln hineingleiten, um sie etwa 3 Minuten zu pochieren.\n"
            "Toaste die English Muffins oder Brotscheiben und belege sie mit "
            "dem Kochschinken.\n"
            "Setze je ein pochiertes Ei obenauf und beträufle alles großzügig "
            "mit der Sauce Hollandaise. Sofort servieren."
        ),
        "zutaten": [
            ("Eier", 4, "Stück"),
            ("English Muffins", 2, "Stück"),
            ("Kochschinken", 80, "g"),
            ("Butter", 100, "g"),
            ("Zitrone", 0.5, "Stück"),
            ("Essig", 1, "EL"),
        ],
    },
    {
        "name": "Vollkornbrot mit Käse und Salami",
        "protein_typ": "Schwein",
        "schwierigkeit": "einfach",
        "kategorie": "Herzhaftes Frühstück",
        "gang": "Hauptgang",
        "mahlzeiten": "Frühstück",
        "bild_override": "assets/flaticon/fr_aufschnitt_teller.png",
        "zubereitungszeit_min": 8,
        "portionen_basis": 2,
        "kalorien_pro_portion": 380,
        "zubereitung": (
            "Schneide das Vollkornbrot in Scheiben, falls es noch nicht "
            "aufgeschnitten ist.\n"
            "Schneide den Käse in dünne Scheiben oder Stücke und die Salami in "
            "Scheiben.\n"
            "Belege die Brotscheiben nach Geschmack mit Käse und Salami.\n"
            "Nach Belieben mit Butter bestreichen, bevor der Belag draufkommt.\n"
            "Am besten frisch servieren, damit das Brot knusprig bleibt."
        ),
        "zutaten": [
            ("Vollkornbrot", 4, "Scheiben"),
            ("Käse", 100, "g"),
            ("Salami", 80, "g"),
            ("Butter", 1, "EL"),
        ],
    },
    {
        "name": "Frühstücks-Wrap mit Schinken und Käse",
        "protein_typ": "Schwein",
        "schwierigkeit": "einfach",
        "kategorie": "Herzhaftes Frühstück",
        "gang": "Hauptgang",
        "mahlzeiten": "Frühstück",
        "zubereitungszeit_min": 15,
        "portionen_basis": 2,
        "kalorien_pro_portion": 410,
        "zubereitung": (
            "Erhitze eine trockene Pfanne bei mittlerer Hitze und wärme den "
            "Wrap darin von beiden Seiten kurz an, damit er weich und "
            "biegsam wird.\n"
            "Belege den Wrap mit Schinken, Käse und den Salatblättern.\n"
            "Schneide die Tomate in dünne Scheiben und verteile sie ebenfalls "
            "auf dem Wrap.\n"
            "Rolle den Wrap fest von einer Seite auf, sodass die Füllung nicht "
            "herausrutscht.\n"
            "Halbiere ihn diagonal und serviere ihn sofort."
        ),
        "zutaten": [
            ("Tortilla-Wrap", 2, "Stück"),
            ("Kochschinken", 100, "g"),
            ("Käse", 60, "g"),
            ("Tomate", 1, "Stück"),
            ("Salatblätter", 2, "Blätter"),
        ],
    },
    {
        "name": "Griechischer Joghurt mit Honig und Walnüssen",
        "protein_typ": "Vegetarisch",
        "schwierigkeit": "einfach",
        "kategorie": "Süßes Frühstück",
        "bild_override": "assets/flaticon/fr_joghurt_beeren.png",
        "gang": "Hauptgang",
        "mahlzeiten": "Frühstück",
        "zubereitungszeit_min": 5,
        "portionen_basis": 2,
        "kalorien_pro_portion": 310,
        "zubereitung": (
            "Verteile den griechischen Joghurt auf zwei Schalen.\n"
            "Hacke die Walnüsse grob.\n"
            "Beträufle den Joghurt großzügig mit Honig.\n"
            "Streue die gehackten Walnüsse darüber.\n"
            "Nach Belieben mit frischem Obst wie Beeren oder Bananenscheiben "
            "ergänzen und sofort servieren."
        ),
        "zutaten": [
            ("Griechischer Joghurt", 300, "g"),
            ("Honig", 2, "EL"),
            ("Walnüsse", 40, "g"),
        ],
    },
    {
        "name": "Omelett mit Gemüsefüllung",
        "protein_typ": "Vegetarisch",
        "schwierigkeit": "mittel",
        "kategorie": "Herzhaftes Frühstück",
        "gang": "Hauptgang",
        "mahlzeiten": "Frühstück",
        "bild_override": "assets/flaticon/fr_omelett_wrap.png",
        "zubereitungszeit_min": 15,
        "portionen_basis": 2,
        "kalorien_pro_portion": 350,
        "zubereitung": (
            "Wasche die Paprika und die Champignons und schneide beides in "
            "kleine Würfel bzw. Scheiben. Schäle die Zwiebel und schneide sie "
            "fein.\n"
            "Erhitze etwas Öl in einer Pfanne und dünste Zwiebel, Paprika und "
            "Champignons darin etwa 4 Minuten an, bis sie weich sind. Nimm das "
            "Gemüse heraus und stelle es beiseite.\n"
            "Verquirle die Eier mit Salz und Pfeffer. Gib etwas Butter in die "
            "Pfanne und gieße die Eimasse hinein, verteile sie gleichmäßig.\n"
            "Lass das Omelett bei niedriger bis mittlerer Hitze stocken, ohne "
            "es zu wenden - hebe gelegentlich den Rand an, damit flüssiges Ei "
            "nachfließen kann.\n"
            "Verteile das Gemüse auf einer Hälfte des Omeletts, sobald die "
            "Oberfläche fast fest ist. Klappe die andere Hälfte darüber.\n"
            "Lass das Omelett noch kurz durchziehen und serviere es sofort."
        ),
        "zutaten": [
            ("Eier", 4, "Stück"),
            ("Paprika", 1, "Stück"),
            ("Champignons", 80, "g"),
            ("Zwiebel", 0.5, "Stück"),
            ("Butter", 1, "EL"),
        ],
    },
    {
        "name": "Rührei mit Speck und Toast",
        "protein_typ": "Schwein",
        "schwierigkeit": "einfach",
        "kategorie": "Herzhaftes Frühstück",
        "gang": "Hauptgang",
        "mahlzeiten": "Frühstück",
        "bild_override": "assets/flaticon/fr_ruehrei.png",
        "zubereitungszeit_min": 15,
        "portionen_basis": 2,
        "kalorien_pro_portion": 420,
        "zubereitung": (
            "Brate den Speck in einer Pfanne ohne zusätzliches Fett bei mittlerer "
            "Hitze knusprig aus, etwa 4 bis 5 Minuten. Nimm ihn heraus und lass ihn "
            "auf Küchenpapier abtropfen.\n"
            "Verquirle die Eier in einer Schüssel mit einer Prise Salz und Pfeffer, "
            "bis Eigelb und Eiweiß vollständig vermischt sind.\n"
            "Gib einen kleinen Klecks Butter in das noch heiße Bratfett des Specks "
            "und gieße die verquirlten Eier hinein. Lass sie bei niedriger Hitze "
            "kurz stocken, ziehe sie dann mit einem Spatel immer wieder vom Rand "
            "zur Mitte, bis sie cremig-stückig, aber noch leicht glänzend sind.\n"
            "Toaste in der Zwischenzeit die Brotscheiben knusprig.\n"
            "Verteile das Rührei auf den Tellern, lege den knusprigen Speck "
            "obenauf und serviere mit dem Toast.\n"
            "Nach Belieben mit Schnittlauch bestreuen."
        ),
        "zutaten": [
            ("Eier", 4, "Stück"),
            ("Speck", 80, "g"),
            ("Toastbrot", 4, "Scheiben"),
            ("Butter", 1, "EL"),
        ],
    },
    {
        "name": "Overnight Oats mit Beeren",
        "protein_typ": "Vegetarisch",
        "schwierigkeit": "einfach",
        "kategorie": "Süßes Frühstück",
        "gang": "Hauptgang",
        "mahlzeiten": "Frühstück",
        "zubereitungszeit_min": 10,
        "portionen_basis": 2,
        "kalorien_pro_portion": 340,
        "zubereitung": (
            "Vermenge die Haferflocken mit der Milch, dem Joghurt und dem Honig in "
            "einer Schüssel oder direkt in zwei Gläsern, bis alles gut vermischt ist.\n"
            "Rühre eine kleine Prise Salz unter - das rundet den Geschmack ab, ohne "
            "dass man es explizit schmeckt.\n"
            "Verschließe die Gläser oder decke die Schüssel ab und stelle alles "
            "über Nacht, mindestens aber für 4 Stunden, in den Kühlschrank. Die "
            "Haferflocken quellen dabei auf und werden cremig.\n"
            "Wasche die Beeren kurz vor dem Servieren.\n"
            "Rühre die Overnight Oats am nächsten Morgen kurz durch und verteile "
            "die Beeren obenauf.\n"
            "Nach Belieben mit einem Klecks Joghurt oder ein paar Nüssen "
            "garnieren."
        ),
        "zutaten": [
            ("Haferflocken", 120, "g"),
            ("Milch", 200, "ml"),
            ("Joghurt", 100, "g"),
            ("Honig", 1, "EL"),
            ("Beeren", 150, "g"),
        ],
    },
    {
        "name": "Fluffige Pfannkuchen mit Ahornsirup",
        "protein_typ": "Vegetarisch",
        "schwierigkeit": "einfach",
        "kategorie": "Süßes Frühstück",
        "bild_override": "assets/flaticon/fr_pancakes.png",
        "gang": "Hauptgang",
        "mahlzeiten": "Frühstück",
        "zubereitungszeit_min": 25,
        "portionen_basis": 2,
        "kalorien_pro_portion": 480,
        "zubereitung": (
            "Verrühre in einer Schüssel das Mehl mit dem Backpulver, dem Zucker "
            "und einer Prise Salz.\n"
            "Verquirle in einer zweiten Schüssel die Milch mit dem Ei und der "
            "geschmolzenen Butter. Gieße die flüssigen Zutaten zu den trockenen "
            "und rühre alles nur so lange, bis kein Mehl mehr sichtbar ist - ein "
            "paar Klümpchen im Teig sind völlig in Ordnung, zu langes Rühren macht "
            "die Pfannkuchen zäh.\n"
            "Erhitze eine beschichtete Pfanne bei mittlerer Hitze und fette sie "
            "leicht ein. Gib pro Pfannkuchen etwa eine kleine Kelle Teig hinein.\n"
            "Backe die Pfannkuchen etwa 2 Minuten, bis sich an der Oberfläche "
            "Bläschen bilden und der Rand fest wird, wende sie dann und backe die "
            "zweite Seite goldbraun.\n"
            "Stapele die fertigen Pfannkuchen auf einem Teller und halte sie warm, "
            "während du den restlichen Teig genauso verbackst.\n"
            "Mit Ahornsirup beträufelt servieren, nach Belieben mit frischen "
            "Früchten."
        ),
        "zutaten": [
            ("Mehl", 200, "g"),
            ("Milch", 250, "ml"),
            ("Eier", 1, "Stück"),
            ("Butter", 30, "g"),
            ("Zucker", 1, "EL"),
            ("Backpulver", 1, "TL"),
            ("Ahornsirup", 3, "EL"),
        ],
    },
    {
        "name": "Herzhaftes Porridge mit Spiegelei",
        "protein_typ": "Vegetarisch",
        "schwierigkeit": "einfach",
        "kategorie": "Herzhaftes Frühstück",
        "gang": "Hauptgang",
        "mahlzeiten": "Frühstück",
        "zubereitungszeit_min": 15,
        "portionen_basis": 2,
        "kalorien_pro_portion": 380,
        "zubereitung": (
            "Gib die Haferflocken zusammen mit der Milch und einer Prise Salz in "
            "einen Topf. Bringe alles unter Rühren zum Kochen.\n"
            "Lass das Porridge bei niedriger Hitze etwa 5 Minuten köcheln, rühre "
            "dabei regelmäßig um, damit nichts anbrennt, bis es cremig ist.\n"
            "Erhitze in der Zwischenzeit etwas Butter in einer Pfanne und brate "
            "die Eier darin als Spiegeleier, bis das Eiweiß gestockt, das Eigelb "
            "aber noch flüssig ist.\n"
            "Verteile das Porridge auf zwei Schalen.\n"
            "Setze jeweils ein Spiegelei obenauf und würze mit Salz und Pfeffer.\n"
            "Mit etwas Schnittlauch oder Röstzwiebeln bestreut servieren."
        ),
        "zutaten": [
            ("Haferflocken", 100, "g"),
            ("Milch", 300, "ml"),
            ("Eier", 2, "Stück"),
            ("Butter", 1, "EL"),
        ],
    },
    {
        "name": "Bruschetta mit Tomaten und Basilikum",
        "protein_typ": "Vegetarisch",
        "schwierigkeit": "einfach",
        "kategorie": "Vorspeise",
        "gang": "Vorspeise",
        "zubereitungszeit_min": 15,
        "portionen_basis": 2,
        "kalorien_pro_portion": 220,
        "zubereitung": (
            "Wasche die Tomaten, entferne die Stielansätze und schneide sie in "
            "kleine Würfel. Gib sie in eine Schüssel.\n"
            "Schäle die Knoblauchzehe und hacke die Hälfte davon sehr fein, die "
            "andere Hälfte hebst du zum Einreiben des Brotes auf. Vermenge den "
            "gehackten Knoblauch mit den Tomatenwürfeln, dem Olivenöl, Salz und "
            "Pfeffer.\n"
            "Zupfe die Basilikumblätter in kleine Stücke und hebe die Hälfte davon "
            "unter die Tomatenmischung. Lass alles kurz durchziehen, während du das "
            "Brot vorbereitest.\n"
            "Schneide das Baguette in schräge Scheiben und röste sie in einer "
            "Pfanne ohne Fett oder im Ofen bei 200°C etwa 3 bis 4 Minuten pro Seite, "
            "bis sie knusprig und goldbraun sind.\n"
            "Reibe die noch warmen Brotscheiben leicht mit der aufgehobenen "
            "Knoblauchzehe ein - das verteilt ein feines Aroma, ohne zu dominant zu "
            "werden.\n"
            "Verteile die Tomatenmischung auf den Brotscheiben und garniere mit dem "
            "restlichen Basilikum. Sofort servieren, solange das Brot noch knusprig "
            "ist."
        ),
        "zutaten": [
            ("Tomaten", 4, "Stück"),
            ("Baguette", 0.5, "Stück"),
            ("Knoblauchzehe", 1, "Stück"),
            ("Basilikum", 10, "g"),
            ("Olivenöl", 3, "EL"),
        ],
    },
    {
        "name": "Cremige Kürbissuppe als Vorspeise",
        "protein_typ": "Vegetarisch",
        "schwierigkeit": "einfach",
        "kategorie": "Vorspeise",
        "gang": "Vorspeise",
        "zubereitungszeit_min": 30,
        "portionen_basis": 2,
        "kalorien_pro_portion": 190,
        "zubereitung": (
            "Schäle den Kürbis, entferne die Kerne und schneide das Fruchtfleisch "
            "in grobe Würfel. Schäle die Zwiebel und schneide sie fein.\n"
            "Erhitze etwas Öl in einem Topf und dünste die Zwiebel darin glasig an. "
            "Gib die Kürbiswürfel dazu und brate sie kurz mit, damit sie etwas "
            "Röstaroma bekommen.\n"
            "Gieße die Gemüsebrühe auf, bis der Kürbis knapp bedeckt ist. Bringe "
            "alles zum Kochen und lasse es bei mittlerer Hitze etwa 15 bis 20 "
            "Minuten köcheln, bis der Kürbis weich ist.\n"
            "Püriere die Suppe direkt im Topf mit einem Stabmixer fein, bis eine "
            "glatte, cremige Konsistenz entsteht. Falls sie zu dick ist, mit etwas "
            "mehr Brühe verdünnen.\n"
            "Rühre die Sahne unter und schmecke die Suppe mit Salz, Pfeffer und "
            "einer Prise Muskatnuss ab.\n"
            "In kleinen Schalen als Vorspeise servieren, nach Belieben mit einem "
            "Klecks Sahne und gerösteten Kürbiskernen garniert."
        ),
        "zutaten": [
            ("Kürbis", 500, "g"),
            ("Zwiebel", 1, "Stück"),
            ("Gemüsebrühe", 500, "ml"),
            ("Sahne", 50, "ml"),
            ("Öl", 1, "EL"),
        ],
    },
    {
        "name": "Carpaccio vom Rind mit Parmesan",
        "protein_typ": "Rind",
        "schwierigkeit": "mittel",
        "kategorie": "Vorspeise",
        "gang": "Vorspeise",
        "zubereitungszeit_min": 20,
        "portionen_basis": 2,
        "kalorien_pro_portion": 210,
        "zubereitung": (
            "Wickle das Rinderfilet fest in Frischhaltefolie und lege es für "
            "mindestens 1 Stunde ins Gefrierfach - leicht angefroren lässt es sich "
            "viel leichter hauchdünn schneiden.\n"
            "Nimm das Fleisch kurz vor der Zubereitung heraus und schneide es mit "
            "einem sehr scharfen Messer in hauchdünne Scheiben.\n"
            "Lege die Scheiben zwischen zwei Bögen Frischhaltefolie und klopfe sie "
            "mit einem Fleischklopfer oder dem Boden eines Topfes noch etwas "
            "flacher, bis sie fast durchscheinend sind.\n"
            "Verteile die Fleischscheiben überlappend auf zwei Tellern. Beträufle "
            "sie großzügig mit Olivenöl und dem Saft der Zitrone.\n"
            "Hobele den Parmesan in feine Späne über das Fleisch und streue die "
            "Rucola-Blätter darüber. Würze mit frisch gemahlenem Pfeffer und einer "
            "kleinen Prise Salz.\n"
            "Sofort servieren, damit das Fleisch noch schön kühl ist."
        ),
        "zutaten": [
            ("Rinderfilet", 200, "g"),
            ("Parmesan", 40, "g"),
            ("Rucola", 30, "g"),
            ("Zitrone", 1, "Stück"),
            ("Olivenöl", 3, "EL"),
        ],
    },
    {
        "name": "Tiramisu",
        "protein_typ": "Vegetarisch",
        "schwierigkeit": "mittel",
        "kategorie": "Dessert",
        "gang": "Dessert",
        "zubereitungszeit_min": 40,
        "portionen_basis": 2,
        "kalorien_pro_portion": 420,
        "zubereitung": (
            "Trenne die Eier. Verrühre die Eigelbe mit dem Zucker in einer Schüssel, "
            "bis die Masse hell und cremig ist. Rühre den Mascarpone unter, bis eine "
            "glatte Creme entsteht.\n"
            "Schlage in einer separaten, sauberen Schüssel das Eiweiß steif und "
            "hebe es vorsichtig unter die Mascarpone-Creme, damit die Masse locker "
            "bleibt.\n"
            "Gib den kalten Espresso in einen flachen Teller. Tunke die "
            "Löffelbiskuits kurz hinein - nur kurz eintauchen, damit sie nicht zu "
            "matschig werden.\n"
            "Schichte die getränkten Biskuits in eine kleine Form, verteile die "
            "Hälfte der Mascarpone-Creme darüber, wiederhole die Schichten mit den "
            "restlichen Biskuits und der restlichen Creme.\n"
            "Stelle das Tiramisu für mindestens 3 Stunden, besser über Nacht, in "
            "den Kühlschrank, damit es fest wird und die Aromen sich verbinden.\n"
            "Vor dem Servieren großzügig mit Kakaopulver bestäuben."
        ),
        "zutaten": [
            ("Eier", 2, "Stück"),
            ("Zucker", 60, "g"),
            ("Mascarpone", 250, "g"),
            ("Löffelbiskuits", 150, "g"),
            ("Espresso", 150, "ml"),
            ("Kakaopulver", 1, "EL"),
        ],
    },
    {
        "name": "Panna Cotta mit Beerensauce",
        "protein_typ": "Vegetarisch",
        "schwierigkeit": "einfach",
        "kategorie": "Dessert",
        "gang": "Dessert",
        "zubereitungszeit_min": 20,
        "portionen_basis": 2,
        "kalorien_pro_portion": 340,
        "zubereitung": (
            "Weiche die Gelatine für etwa 5 Minuten in kaltem Wasser ein, bis sie "
            "weich ist.\n"
            "Erhitze die Sahne zusammen mit dem Zucker und dem Mark der "
            "Vanilleschote in einem Topf, bis sich der Zucker aufgelöst hat - die "
            "Sahne sollte nicht kochen, nur heiß werden.\n"
            "Drücke die eingeweichte Gelatine aus und rühre sie in die heiße Sahne, "
            "bis sie sich vollständig aufgelöst hat.\n"
            "Gieße die Masse in zwei Förmchen oder Gläser und lass sie mindestens 4 "
            "Stunden im Kühlschrank fest werden.\n"
            "Erhitze für die Sauce die Beeren mit etwas Zucker in einem kleinen "
            "Topf, bis sie weich werden und etwas Saft ziehen. Lass die Sauce "
            "abkühlen.\n"
            "Stürze die Panna Cotta vorsichtig auf einen Teller oder serviere sie "
            "direkt im Glas, mit der Beerensauce obenauf."
        ),
        "zutaten": [
            ("Sahne", 400, "ml"),
            ("Zucker", 60, "g"),
            ("Gelatine", 4, "Blatt"),
            ("Vanilleschote", 1, "Stück"),
            ("Beeren", 200, "g"),
        ],
    },
    {
        "name": "Gebratener Reis mit Ei und Gemüse",
        "protein_typ": "Vegetarisch",
        "schwierigkeit": "einfach",
        "kategorie": "Reisgericht",
        "zubereitungszeit_min": 25,
        "portionen_basis": 2,
        "kalorien_pro_portion": 420,
        "zubereitung": (
            "Koche den Reis nach Packungsanweisung und lass ihn danach vollständig "
            "abkühlen, am besten schon am Vortag im Kühlschrank - kalter, leicht "
            "angetrockneter Reis wird beim Braten schön locker statt klebrig.\n"
            "Schäle die Karotte und schneide sie in kleine Würfel, schneide die "
            "Frühlingszwiebel in feine Ringe und teile die Erbsen ab, falls sie "
            "tiefgekühlt sind, lass sie kurz auftauen.\n"
            "Erhitze etwas Öl in einer großen Pfanne oder einem Wok bei hoher Hitze. "
            "Verquirle die Eier in einer Schüssel, gib sie in die Pfanne und rühre "
            "sie kurz zu Rührei, das du dann grob zerkleinerst und beiseitestellst.\n"
            "Gib etwas mehr Öl in die Pfanne, brate Karotte und Erbsen etwa 2 Minuten "
            "an. Füge den kalten Reis hinzu und brate alles unter Wenden etwa 4 "
            "Minuten, bis der Reis heiß ist und leicht anfängt zu rösten.\n"
            "Gib das Rührei zurück in die Pfanne, gieße die Sojasauce darüber und "
            "vermenge alles gut. Schmecke mit Salz und Pfeffer ab.\n"
            "Zum Schluss die Frühlingszwiebel unterheben und sofort servieren."
        ),
        "zutaten": [
            ("Reis", 200, "g"),
            ("Eier", 2, "Stück"),
            ("Karotte", 1, "Stück"),
            ("Erbsen", 100, "g"),
            ("Frühlingszwiebel", 2, "Stück"),
            ("Sojasauce", 2, "EL"),
            ("Öl", 2, "EL"),
        ],
    },
    {
        "name": "Spaghetti Aglio e Olio",
        "protein_typ": "Vegetarisch",
        "schwierigkeit": "einfach",
        "kategorie": "Pastagericht",
        "zubereitungszeit_min": 20,
        "portionen_basis": 2,
        "kalorien_pro_portion": 480,
        "zubereitung": (
            "Bringe reichlich Salzwasser zum Kochen und gare die Spaghetti darin "
            "nach Packungsanweisung bissfest. Hebe dir vor dem Abgießen eine Tasse "
            "vom Nudelwasser auf.\n"
            "Schäle den Knoblauch und schneide ihn in sehr dünne Scheiben. Erhitze "
            "das Olivenöl in einer großen Pfanne bei niedriger bis mittlerer Hitze "
            "und gib den Knoblauch hinein.\n"
            "Brate den Knoblauch langsam an, bis er goldgelb, aber nicht braun ist - "
            "das dauert etwa 3 bis 4 Minuten. Gib die Chiliflocken dazu und rühre "
            "kurz mit, damit sich die Schärfe im Öl verteilt.\n"
            "Gib die abgetropften Spaghetti direkt in die Pfanne und vermenge sie "
            "gründlich mit dem Knoblauchöl. Gieße nach und nach etwas vom "
            "aufgehobenen Nudelwasser dazu, bis eine leicht cremige Sauce entsteht, "
            "die die Nudeln überzieht.\n"
            "Schmecke mit Salz kräftig ab und hebe die gehackte Petersilie unter.\n"
            "Sofort servieren, nach Belieben mit geriebenem Parmesan bestreut."
        ),
        "zutaten": [
            ("Spaghetti", 200, "g"),
            ("Knoblauchzehe", 4, "Stück"),
            ("Olivenöl", 5, "EL"),
            ("Chiliflocken", 1, "TL"),
            ("Petersilie", 15, "g"),
        ],
    },
    {
        "name": "Griechischer Salat",
        "protein_typ": "Vegetarisch",
        "schwierigkeit": "einfach",
        "kategorie": "Salat",
        "zubereitungszeit_min": 15,
        "portionen_basis": 2,
        "kalorien_pro_portion": 320,
        "zubereitung": (
            "Wasche die Tomaten und die Gurke. Schneide die Tomaten in grobe "
            "Spalten und die Gurke in halbe Scheiben. Schäle die rote Zwiebel und "
            "schneide sie in dünne Ringe.\n"
            "Gib Tomaten, Gurke und Zwiebel zusammen mit den Oliven in eine große "
            "Schüssel und vermenge alles vorsichtig.\n"
            "Schneide den Feta in grobe Würfel oder eine dicke Scheibe und lege ihn "
            "obenauf.\n"
            "Verrühre in einer kleinen Schüssel das Olivenöl mit dem Essig, Salz, "
            "Pfeffer und dem Oregano zu einem Dressing.\n"
            "Beträufle den Salat kurz vor dem Servieren mit dem Dressing, damit das "
            "Gemüse nicht durchweicht.\n"
            "Nach Belieben mit ein paar Kapern und noch etwas Oregano bestreut "
            "servieren."
        ),
        "zutaten": [
            ("Tomaten", 3, "Stück"),
            ("Salatgurke", 1, "Stück"),
            ("Rote Zwiebel", 1, "Stück"),
            ("Feta", 150, "g"),
            ("Oliven", 80, "g"),
            ("Olivenöl", 3, "EL"),
            ("Essig", 1, "EL"),
            ("Oregano", 1, "TL"),
        ],
    },
    {
        "name": "Rosmarinkartoffeln aus dem Ofen",
        "protein_typ": "Vegetarisch",
        "schwierigkeit": "einfach",
        "kategorie": "Beilage",
        "zubereitungszeit_min": 40,
        "portionen_basis": 2,
        "kalorien_pro_portion": 260,
        "zubereitung": (
            "Heize den Backofen auf 200°C Ober-/Unterhitze vor und lege ein Blech "
            "mit Backpapier aus.\n"
            "Wasche die Kartoffeln gründlich und schneide sie ungeschält in grobe, "
            "gleich große Spalten oder Würfel, damit sie gleichmäßig garen.\n"
            "Gib die Kartoffelstücke in eine große Schüssel, beträufle sie mit "
            "Olivenöl und vermenge sie mit dem gehackten Rosmarin, den zerdrückten "
            "Knoblauchzehen (mit Schale), Salz und Pfeffer, bis alles gleichmäßig "
            "bedeckt ist.\n"
            "Verteile die Kartoffeln in einer Schicht auf dem Blech, ohne dass sie "
            "sich zu sehr überlappen - so werden sie außen knusprig statt zu "
            "dünsten.\n"
            "Backe die Kartoffeln für etwa 30 bis 35 Minuten, wende sie einmal nach "
            "der Hälfte der Zeit, bis sie außen goldbraun und knusprig und innen "
            "weich sind.\n"
            "Direkt aus dem Ofen heiß servieren."
        ),
        "zutaten": [
            ("Kartoffel", 600, "g"),
            ("Rosmarin", 2, "Zweige"),
            ("Knoblauchzehe", 3, "Stück"),
            ("Olivenöl", 3, "EL"),
        ],
    },
    {
        "name": "Kartoffel-Lauch-Auflauf mit Käse",
        "protein_typ": "Vegetarisch",
        "schwierigkeit": "mittel",
        "kategorie": "Auflauf",
        "zubereitungszeit_min": 55,
        "portionen_basis": 2,
        "kalorien_pro_portion": 540,
        "zubereitung": (
            "Schäle die Kartoffeln und schneide sie in dünne Scheiben. Wasche den "
            "Lauch gründlich, auch zwischen den Ringen, und schneide ihn in feine "
            "Ringe.\n"
            "Koche die Kartoffelscheiben in Salzwasser etwa 5 Minuten vor, bis sie "
            "leicht angegart, aber noch fest sind. Gieße sie ab.\n"
            "Heize den Backofen auf 190°C Ober-/Unterhitze vor. Erhitze etwas Öl in "
            "einer Pfanne und dünste den Lauch darin etwa 5 Minuten an, bis er weich "
            "wird.\n"
            "Verrühre die Sahne mit der Milch, einer Prise Muskatnuss, Salz und "
            "Pfeffer. Schichte die Hälfte der Kartoffeln in eine gefettete "
            "Auflaufform, verteile den Lauch darauf und bedecke ihn mit der "
            "restlichen Kartoffelschicht.\n"
            "Gieße die Sahne-Milch-Mischung gleichmäßig darüber, sodass alles knapp "
            "bedeckt ist. Streue den geriebenen Käse großzügig darüber.\n"
            "Backe den Auflauf für etwa 35 bis 40 Minuten, bis die Oberfläche "
            "goldbraun ist und die Kartoffeln weich sind."
        ),
        "zutaten": [
            ("Kartoffel", 600, "g"),
            ("Lauch", 2, "Stück"),
            ("Sahne", 200, "ml"),
            ("Milch", 100, "ml"),
            ("Geriebener Käse", 150, "g"),
        ],
    },
    {
        "name": "Rotes Thai-Curry mit Huhn",
        "protein_typ": "Huhn",
        "schwierigkeit": "mittel",
        "kategorie": "Curry",
        "zubereitungszeit_min": 30,
        "portionen_basis": 2,
        "kalorien_pro_portion": 490,
        "zubereitung": (
            "Schneide die Hühnerbrust in mundgerechte Streifen. Wasche die Paprika "
            "und die Zucchini und schneide beides in dünne Scheiben oder Streifen.\n"
            "Erhitze einen Esslöffel Öl in einem großen Topf oder einer tiefen "
            "Pfanne bei mittlerer Hitze. Gib die rote Currypaste hinein und röste "
            "sie unter Rühren etwa eine Minute an, bis sie intensiv duftet.\n"
            "Gib das Hühnerfleisch dazu und brate es rundum an, bis es nicht mehr "
            "roh ist. Gieße die Kokosmilch dazu und rühre gut um, damit sich die "
            "Currypaste vollständig darin auflöst.\n"
            "Füge Paprika und Zucchini hinzu, bringe alles zum Köcheln und lasse es "
            "bei mittlerer Hitze offen etwa 12 bis 15 Minuten köcheln, bis das "
            "Gemüse gar und die Sauce leicht eingedickt ist.\n"
            "Schmecke das Curry mit Fischsauce und einer Prise Zucker ab, um Süße "
            "und Salzigkeit auszubalancieren.\n"
            "Mit frischem Basilikum bestreut über Reis servieren."
        ),
        "zutaten": [
            ("Hühnerbrust", 300, "g"),
            ("Rote Currypaste", 2, "EL"),
            ("Kokosmilch", 400, "ml"),
            ("Rote Paprika", 1, "Stück"),
            ("Zucchini", 1, "Stück"),
            ("Fischsauce", 1, "EL"),
            ("Thai-Basilikum", 10, "g"),
        ],
    },
    {
        "name": "Gedämpfte Gemüse-Dumplings",
        "protein_typ": "Vegetarisch",
        "schwierigkeit": "mittel",
        "kategorie": "Dumpling",
        "zubereitungszeit_min": 50,
        "portionen_basis": 2,
        "kalorien_pro_portion": 380,
        "zubereitung": (
            "Putze den Chinakohl und schneide ihn sehr fein, gib ihn in eine "
            "Schüssel und vermenge ihn mit einer Prise Salz. Lass ihn 10 Minuten "
            "stehen und drücke dann überschüssige Flüssigkeit gut aus.\n"
            "Schäle die Karotte und die Frühlingszwiebeln und schneide beides sehr "
            "fein, hacke den Knoblauch und den Ingwer klein. Vermenge alles mit dem "
            "Chinakohl, der Sojasauce und dem Sesamöl zu einer gleichmäßigen "
            "Füllung.\n"
            "Lege einen Teigwrapper auf die Handfläche, gib einen Teelöffel Füllung "
            "in die Mitte. Befeuchte den Rand mit etwas Wasser und falte den "
            "Wrapper zu einem Halbmond, drücke die Ränder fest zusammen, am besten "
            "mit kleinen Falten für die klassische Dumpling-Form.\n"
            "Wiederhole das, bis Teig oder Füllung aufgebraucht sind. Lege die "
            "Dumplings mit etwas Abstand in einen mit Backpapier ausgelegten "
            "Dämpfeinsatz.\n"
            "Dämpfe die Dumplings über kochendem Wasser zugedeckt etwa 8 bis 10 "
            "Minuten, bis der Teig glasig und gar ist.\n"
            "Mit einer Dip-Sauce aus Sojasauce, etwas Essig und Chiliöl servieren."
        ),
        "zutaten": [
            ("Dumpling-Teigwrapper", 20, "Stück"),
            ("Chinakohl", 200, "g"),
            ("Karotte", 1, "Stück"),
            ("Frühlingszwiebel", 2, "Stück"),
            ("Knoblauchzehe", 1, "Stück"),
            ("Ingwer", 10, "g"),
            ("Sojasauce", 2, "EL"),
            ("Sesamöl", 1, "EL"),
        ],
    },
    {
        "name": "Pizza Margherita selbstgemacht",
        "protein_typ": "Vegetarisch",
        "schwierigkeit": "mittel",
        "kategorie": "Pizza",
        "zubereitungszeit_min": 40,
        "portionen_basis": 2,
        "kalorien_pro_portion": 620,
        "zubereitung": (
            "Heize den Backofen auf die höchstmögliche Temperatur vor (meist 250°C "
            "oder mehr), am besten mit einem Backstein oder umgedrehten Blech, das "
            "gleich mit aufheizt.\n"
            "Bemehle die Arbeitsfläche und rolle oder ziehe den Pizzateig zu einem "
            "dünnen, runden Fladen von etwa 28 bis 30 Zentimetern Durchmesser aus.\n"
            "Verteile die passierten Tomaten gleichmäßig auf dem Teig, lass dabei "
            "einen schmalen Rand für die Kruste frei. Würze die Tomatensauce mit "
            "einer Prise Salz und etwas Oregano.\n"
            "Zupfe den Mozzarella in Stücke und verteile ihn gleichmäßig auf der "
            "Pizza. Beträufle alles mit etwas Olivenöl.\n"
            "Schiebe die Pizza vorsichtig auf den heißen Stein oder das heiße Blech "
            "und backe sie etwa 8 bis 12 Minuten, bis der Rand goldbraun und "
            "leicht angebrannt gesprenkelt und der Käse geschmolzen ist.\n"
            "Direkt nach dem Backen mit frischen Basilikumblättern belegen und "
            "sofort servieren."
        ),
        "zutaten": [
            ("Pizzateig", 300, "g"),
            ("Passierte Tomaten", 150, "g"),
            ("Mozzarella", 200, "g"),
            ("Basilikum", 10, "g"),
            ("Olivenöl", 1, "EL"),
        ],
    },
    {
        "name": "Schokoladenkuchen mit flüssigem Kern",
        "protein_typ": "Vegetarisch",
        "schwierigkeit": "mittel",
        "kategorie": "Dessert",
        "gang": "Dessert",
        "zubereitungszeit_min": 30,
        "portionen_basis": 2,
        "kalorien_pro_portion": 480,
        "zubereitung": (
            "Heize den Backofen auf 200°C Ober-/Unterhitze vor und fette zwei kleine "
            "Auflaufförmchen gut mit Butter ein, bestäube sie danach mit etwas "
            "Kakaopulver, damit sich der Kuchen später leicht löst.\n"
            "Schmelze die dunkle Schokolade zusammen mit der Butter in einem "
            "Wasserbad oder vorsichtig in der Mikrowelle, bis eine glatte Masse "
            "entsteht. Lass sie etwas abkühlen.\n"
            "Verquirle die Eier mit dem Zucker in einer separaten Schüssel, bis die "
            "Masse heller und leicht schaumig wird.\n"
            "Rühre die geschmolzene Schokolade unter die Eiermasse und siebe "
            "anschließend das Mehl darüber, hebe es vorsichtig unter, bis kein Mehl "
            "mehr sichtbar ist.\n"
            "Verteile den Teig auf die vorbereiteten Förmchen und backe sie für "
            "genau 10 bis 12 Minuten - der Rand soll fest sein, die Mitte aber noch "
            "wackelig, das ergibt den flüssigen Kern.\n"
            "Lass die Küchlein eine Minute stehen, stürze sie dann vorsichtig auf "
            "einen Teller und serviere sie sofort, solange der Kern noch flüssig "
            "ist."
        ),
        "zutaten": [
            ("Dunkle Schokolade", 150, "g"),
            ("Butter", 100, "g"),
            ("Eier", 2, "Stück"),
            ("Zucker", 80, "g"),
            ("Mehl", 40, "g"),
        ],
    },
    {
        "name": "Schweinemedaillons mit Champignonrahmsauce",
        "protein_typ": "Schwein",
        "schwierigkeit": "mittel",
        "kategorie": "Pfannengericht",
        "zubereitungszeit_min": 35,
        "portionen_basis": 2,
        "kalorien_pro_portion": 520,
        "zubereitung": (
            "Schneide das Schweinefilet in etwa zwei Zentimeter dicke Medaillons und "
            "klopfe sie vorsichtig etwas flach. Würze beide Seiten mit Salz und "
            "Pfeffer.\n"
            "Erhitze das Öl zusammen mit einem Esslöffel Butter in einer Pfanne bei "
            "mittlerer bis hoher Hitze. Brate die Medaillons darin auf jeder Seite "
            "etwa 3 bis 4 Minuten scharf an, bis sie eine schöne braune Kruste haben "
            "und innen noch leicht rosa sind. Nimm sie heraus, decke sie mit Alufolie "
            "ab und lass sie ruhen, während du die Sauce zubereitest.\n"
            "Schäle die Zwiebel und schneide sie fein, putze die Champignons und "
            "schneide sie in Scheiben. Gib beides in dieselbe Pfanne und brate es bei "
            "mittlerer Hitze an, bis die Zwiebel glasig und die Champignons leicht "
            "gebräunt sind.\n"
            "Lösche mit der Brühe ab und kratze dabei den Bratensatz vom Boden der "
            "Pfanne los, das gibt der Sauce zusätzlichen Geschmack. Lass die "
            "Flüssigkeit kurz einkochen, rühre dann die Sahne ein und lass die Sauce "
            "bei niedriger Hitze 3 bis 4 Minuten leicht einköcheln, bis sie sämig "
            "wird.\n"
            "Schmecke die Sauce mit Salz, Pfeffer und einer Prise Muskatnuss ab. Gib "
            "die Medaillons zurück in die Pfanne und erwärme sie kurz in der Sauce "
            "mit.\n"
            "Serviere die Medaillons mit reichlich Sauce, zum Beispiel zusammen mit "
            "Kartoffeln oder Nudeln."
        ),
        "zutaten": [
            ("Schweinefilet", 400, "g"),
            ("Champignons", 200, "g"),
            ("Zwiebel", 1, "Stück"),
            ("Sahne", 150, "ml"),
            ("Gemüsebrühe", 100, "ml"),
            ("Butter", 1, "EL"),
            ("Öl", 1, "EL"),
        ],
    },
    {
        "name": "Geschmorte Lammkoteletts mit Rosmarin",
        "protein_typ": "Lamm",
        "schwierigkeit": "aufwaendig",
        "kategorie": "Ofengericht",
        "zubereitungszeit_min": 55,
        "portionen_basis": 2,
        "kalorien_pro_portion": 580,
        "zubereitung": (
            "Nimm die Lammkoteletts etwa 30 Minuten vor dem Kochen aus dem "
            "Kühlschrank, damit sie Zimmertemperatur annehmen - das sorgt für "
            "gleichmäßigeres Garen. Tupfe sie trocken und würze sie großzügig mit "
            "Salz und Pfeffer.\n"
            "Schäle den Knoblauch und halbiere die Zehen. Heize den Backofen auf "
            "180°C Ober-/Unterhitze vor.\n"
            "Erhitze das Öl in einer ofenfesten Pfanne bei hoher Hitze. Brate die "
            "Lammkoteletts darin auf jeder Seite etwa 2 Minuten scharf an, bis sie "
            "rundum braun sind. Gib den Knoblauch und die Rosmarinzweige mit in die "
            "Pfanne.\n"
            "Schiebe die Pfanne für etwa 8 bis 10 Minuten in den vorgeheizten Ofen, "
            "je nachdem wie durch du das Lamm magst - für einen rosa Kern reichen "
            "meist 8 Minuten bei dieser Dicke.\n"
            "Schäle in der Zwischenzeit die Kartoffeln und schneide sie in grobe "
            "Stücke. Koche sie in Salzwasser weich, gieße sie ab und stampfe sie mit "
            "etwas Butter und Milch zu einem Püree, das du mit Salz und Pfeffer "
            "abschmeckst.\n"
            "Nimm die Pfanne aus dem Ofen und lass das Fleisch einige Minuten "
            "abgedeckt ruhen, bevor du es anschneidest - so bleibt es saftig. "
            "Serviere die Lammkoteletts mit dem Kartoffelpüree und beträufle alles "
            "mit dem Bratfond aus der Pfanne."
        ),
        "zutaten": [
            ("Lammkoteletts", 400, "g"),
            ("Knoblauchzehe", 3, "Stück"),
            ("Rosmarin", 2, "Zweige"),
            ("Kartoffel", 500, "g"),
            ("Butter", 1, "EL"),
            ("Milch", 50, "ml"),
            ("Öl", 2, "EL"),
        ],
    },
    {
        "name": "Asiatisches Hühner-Wok mit Gemüse",
        "protein_typ": "Huhn",
        "schwierigkeit": "mittel",
        "kategorie": "Wokgericht",
        "zubereitungszeit_min": 30,
        "portionen_basis": 2,
        "kalorien_pro_portion": 440,
        "zubereitung": (
            "Schneide die Hühnerbrust in dünne, mundgerechte Streifen. Vermenge sie in "
            "einer Schüssel mit einem Esslöffel Sojasauce und lass sie kurz marinieren, "
            "während du das Gemüse vorbereitest - beim Wokken geht später alles sehr "
            "schnell, deshalb sollte wirklich alles bereitliegen (Mise en Place).\n"
            "Wasche die Paprika und den Brokkoli, schneide die Paprika in dünne "
            "Streifen und den Brokkoli in kleine Röschen. Schäle die Karotte und "
            "schneide sie in dünne Scheiben oder Streifen. Schäle Knoblauch und "
            "Ingwer und hacke beides fein.\n"
            "Erhitze das Öl in einem Wok oder einer großen Pfanne bei sehr hoher Hitze, "
            "bis es fast zu rauchen beginnt. Gib die Hühnerstreifen hinein und brate "
            "sie unter ständigem Rühren etwa 3 bis 4 Minuten an, bis sie rundum "
            "durchgegart und leicht gebräunt sind. Nimm das Fleisch heraus und stelle "
            "es beiseite.\n"
            "Gib Knoblauch und Ingwer in den heißen Wok und rühre sie nur wenige "
            "Sekunden mit, bis sie duften, aber nicht verbrennen. Füge Karotte, "
            "Brokkoli und Paprika hinzu und brate alles unter kräftigem Rühren und "
            "Wenden etwa 3 bis 4 Minuten, bis das Gemüse heiß, aber noch schön "
            "knackig ist.\n"
            "Gib das Hühnerfleisch zurück in den Wok, gieße die restliche Sojasauce "
            "darüber und vermenge alles kurz. Schmecke mit einer Prise Salz und "
            "Pfeffer ab.\n"
            "Serviere das Wok-Gericht sofort, solange das Gemüse noch knackig ist, "
            "nach Belieben mit Reis oder Nudeln."
        ),
        "zutaten": [
            ("Hühnerbrust", 300, "g"),
            ("Rote Paprika", 1, "Stück"),
            ("Brokkoli", 150, "g"),
            ("Karotte", 1, "Stück"),
            ("Knoblauchzehe", 2, "Stück"),
            ("Ingwer", 15, "g"),
            ("Sojasauce", 3, "EL"),
            ("Öl", 2, "EL"),
        ],
    },
    {
        "name": "Rind-Wok mit Nudeln",
        "protein_typ": "Rind",
        "schwierigkeit": "mittel",
        "kategorie": "Wokgericht",
        "zubereitungszeit_min": 35,
        "portionen_basis": 2,
        "kalorien_pro_portion": 560,
        "zubereitung": (
            "Koche die Eiernudeln nach Packungsanweisung in reichlich Salzwasser "
            "bissfest, gieße sie ab und lass sie kurz abtropfen. Ein Schuss Öl "
            "verhindert, dass sie zusammenkleben, während sie warten.\n"
            "Schneide das Rindfleisch in sehr dünne Streifen, am besten quer zur "
            "Faser - das macht es beim kurzen Braten besonders zart. Schäle Zwiebel "
            "und Knoblauch und schneide beides fein, den Lauch in feine Ringe.\n"
            "Erhitze das Öl in einem Wok bei sehr hoher Hitze. Brate das Rindfleisch "
            "portionsweise nur etwa 1 bis 2 Minuten scharf an, bis es außen Farbe "
            "bekommt, und nimm es dann sofort wieder heraus, damit es innen zart "
            "bleibt.\n"
            "Gib Zwiebel und Knoblauch in den Wok und brate sie kurz an, bis sie "
            "duften. Füge den Lauch und die Sojasprossen hinzu und brate alles unter "
            "Rühren etwa 2 Minuten, bis es heiß, aber noch bissfest ist.\n"
            "Gib die Nudeln und das Rindfleisch zurück in den Wok. Vermenge alles "
            "mit der Sojasauce und der Austernsauce und schwenke es kräftig, bis "
            "alles gleichmäßig überzogen und heiß ist.\n"
            "Sofort servieren, damit die Nudeln nicht verkleben und das Gemüse "
            "seinen Biss behält."
        ),
        "zutaten": [
            ("Rindfleisch (Streifen)", 300, "g"),
            ("Eiernudeln", 200, "g"),
            ("Zwiebel", 1, "Stück"),
            ("Lauch", 1, "Stück"),
            ("Sojasprossen", 150, "g"),
            ("Knoblauchzehe", 2, "Stück"),
            ("Sojasauce", 3, "EL"),
            ("Austernsauce", 2, "EL"),
            ("Öl", 2, "EL"),
        ],
    },
    {
        "name": "Knackiges Gemüse-Wok mit Tofu",
        "protein_typ": "Vegetarisch",
        "schwierigkeit": "einfach",
        "kategorie": "Wokgericht",
        "zubereitungszeit_min": 25,
        "portionen_basis": 2,
        "kalorien_pro_portion": 390,
        "zubereitung": (
            "Tupfe den Tofu gut trocken und schneide ihn in mundgerechte Würfel - je "
            "trockener der Tofu, desto besser wird er beim Braten außen knusprig statt "
            "zu dünsten.\n"
            "Wasche und schneide das Gemüse: die Paprika in Streifen, die Zucchini in "
            "halbe Scheiben, die Karotte in dünne Stifte. Schäle Knoblauch und Ingwer "
            "und hacke beides fein. Alles bereitlegen, denn das eigentliche Wokken "
            "geht sehr schnell.\n"
            "Erhitze einen Esslöffel Öl in einem Wok bei hoher Hitze und brate den "
            "Tofu darin rundum goldbraun und knusprig, etwa 5 bis 6 Minuten. Nimm ihn "
            "heraus und stelle ihn beiseite.\n"
            "Gib den restlichen Esslöffel Öl in den Wok, füge Knoblauch und Ingwer "
            "hinzu und rühre kurz, bis es duftet. Gib Karotte, Paprika und Zucchini "
            "dazu und brate alles unter ständigem Wenden etwa 4 Minuten, bis das "
            "Gemüse heiß, aber noch knackig ist.\n"
            "Gib den Tofu zurück in den Wok, gieße die Sojasauce darüber und "
            "vermenge alles vorsichtig, damit der Tofu nicht zerbricht.\n"
            "Mit Sesam bestreut servieren, am besten sofort und mit Reis dazu."
        ),
        "zutaten": [
            ("Tofu", 250, "g"),
            ("Rote Paprika", 1, "Stück"),
            ("Zucchini", 1, "Stück"),
            ("Karotte", 1, "Stück"),
            ("Knoblauchzehe", 2, "Stück"),
            ("Ingwer", 10, "g"),
            ("Sojasauce", 3, "EL"),
            ("Sesam", 1, "EL"),
            ("Öl", 2, "EL"),
        ],
    },
    {
        "name": "Hühnchen-Gemüse-Pfanne mit Reis",
        "protein_typ": "Huhn",
        "schwierigkeit": "einfach",
        "kategorie": "Pfannengericht",
        "zubereitungszeit_min": 25,
        "portionen_basis": 2,
        "kalorien_pro_portion": 480,
        "zubereitung": (
            "Setze zuerst den Reis auf: Gib ihn zusammen mit der doppelten Menge Wasser "
            "und einer Prise Salz in einen Topf, bringe alles kurz zum Kochen und lasse "
            "ihn dann bei geringer Hitze zugedeckt etwa 15 bis 18 Minuten quellen, bis "
            "das Wasser vollständig aufgesogen ist.\n"
            "Während der Reis kocht, schneidest du die Hühnerbrust in mundgerechte Würfel "
            "und würzt sie leicht mit Salz und Pfeffer. Erhitze das Öl in einer großen "
            "Pfanne bei mittlerer bis hoher Hitze und brate das Hühnerfleisch darin rundum "
            "goldbraun an, das dauert etwa 5 bis 6 Minuten. Nimm das Fleisch danach kurz "
            "aus der Pfanne und stelle es beiseite.\n"
            "Schneide in der Zwischenzeit die Paprika in Streifen, die Zwiebel in feine "
            "Ringe und teile den Brokkoli in kleine Röschen. Gib das Gemüse in dieselbe "
            "Pfanne und brate es unter gelegentlichem Rühren etwa 5 Minuten an, bis es "
            "noch bissfest, aber nicht mehr roh ist.\n"
            "Gib das Hühnerfleisch zurück in die Pfanne, mische alles gut durch und lösche "
            "mit der Sojasauce ab. Lass alles noch eine Minute gemeinsam köcheln, damit "
            "sich die Aromen verbinden, und schmecke abschließend mit Salz und Pfeffer ab.\n"
            "Serviere die Pfanne heiß zusammen mit dem gekochten Reis, entweder auf einem "
            "Teller angerichtet oder direkt aus der Pfanne."
        ),
        "zutaten": [
            ("Hühnerbrust", 300, "g"),
            ("Brokkoli", 200, "g"),
            ("Rote Paprika", 1, "Stück"),
            ("Zwiebel", 1, "Stück"),
            ("Reis", 150, "g"),
            ("Sojasauce", 2, "EL"),
        ],
    },
    {
        "name": "Lachsfilet mit Ofengemüse",
        "protein_typ": "Fisch",
        "schwierigkeit": "einfach",
        "kategorie": "Ofengericht",
        "zubereitungszeit_min": 30,
        "portionen_basis": 2,
        "kalorien_pro_portion": 420,
        "zubereitung": (
            "Heize den Backofen auf 200°C Ober-/Unterhitze vor, damit er beim Einschieben "
            "bereits die richtige Temperatur erreicht hat.\n"
            "Wasche die Zucchini und schneide sie in etwa einen Zentimeter dicke Scheiben. "
            "Halbiere die Kirschtomaten. Gib beides zusammen in eine große Schüssel, "
            "beträufle es mit dem Olivenöl und würze großzügig mit Salz, Pfeffer und den "
            "Kräutern deiner Wahl, zum Beispiel Thymian. Vermenge alles gut, sodass jedes "
            "Stück gleichmäßig mit Öl und Gewürzen bedeckt ist.\n"
            "Verteile das Gemüse gleichmäßig auf einem mit Backpapier ausgelegten Blech, "
            "damit es beim Backen schön Platz hat und knusprig werden kann statt zu dünsten.\n"
            "Tupfe die Lachsfilets mit etwas Küchenpapier trocken, würze sie mit Salz und "
            "Pfeffer und lege sie mittig auf das Gemüse. Beträufle die Filets mit dem Saft "
            "einer halben Zitrone.\n"
            "Schiebe das Blech in den vorgeheizten Ofen und backe alles für etwa 18 bis 20 "
            "Minuten, bis der Lachs bei leichtem Druck mit der Gabel zart zerfällt und das "
            "Gemüse an den Rändern leicht gebräunt ist.\n"
            "Serviere den Lachs direkt mit dem Ofengemüse, garniert mit den restlichen "
            "Zitronenspalten."
        ),
        "zutaten": [
            ("Lachsfilet", 300, "g"),
            ("Zucchini", 2, "Stück"),
            ("Kirschtomaten", 200, "g"),
            ("Olivenöl", 2, "EL"),
            ("Zitrone", 1, "Stück"),
        ],
    },
    {
        "name": "Rindergeschnetzeltes Stroganoff",
        "protein_typ": "Rind",
        "schwierigkeit": "mittel",
        "kategorie": "Pfannengericht",
        "zubereitungszeit_min": 40,
        "portionen_basis": 2,
        "kalorien_pro_portion": 560,
        "zubereitung": (
            "Bringe einen großen Topf mit gesalzenem Wasser zum Kochen und gare die Nudeln "
            "darin nach Packungsanweisung bissfest. Gieße sie danach ab und stelle sie "
            "beiseite, ein kleiner Schuss Öl verhindert, dass sie zusammenkleben.\n"
            "Schneide das Rindfleisch in dünne, mundgerechte Streifen - quer zur Faser "
            "geschnitten wird es besonders zart. Schäle die Zwiebel und schneide sie in "
            "feine Streifen, putze die Champignons und viertle sie.\n"
            "Erhitze etwas Öl in einer großen Pfanne bei hoher Hitze und brate das "
            "Rindfleisch portionsweise scharf an, jeweils nur etwa 1 bis 2 Minuten pro "
            "Seite, damit es außen Farbe bekommt, innen aber saftig bleibt. Nimm das "
            "Fleisch heraus und stelle es beiseite.\n"
            "Gib die Zwiebeln in dieselbe Pfanne und dünste sie glasig, dann die "
            "Champignons dazugeben und mitbraten, bis sie leicht gebräunt sind. Rühre das "
            "Tomatenmark ein und röste es kurz mit, das nimmt ihm die Säure. Lösche alles "
            "mit etwas Wasser oder Brühe ab und lasse es kurz aufkochen.\n"
            "Reduziere die Hitze, rühre den Sauerrahm unter und lass die Sauce bei "
            "niedriger Hitze kurz einköcheln, ohne sie kochen zu lassen, damit sie nicht "
            "gerinnt. Gib zum Schluss das Fleisch zurück in die Pfanne, erwärme es kurz "
            "mit und schmecke mit Salz, Pfeffer und etwas Paprikapulver ab.\n"
            "Richte die Nudeln auf Tellern an und gib das Geschnetzelte mit reichlich "
            "Sauce darüber."
        ),
        "zutaten": [
            ("Rindfleisch (Streifen)", 300, "g"),
            ("Zwiebel", 1, "Stück"),
            ("Champignons", 150, "g"),
            ("Sauerrahm", 150, "ml"),
            ("Tomatenmark", 1, "EL"),
            ("Nudeln", 150, "g"),
        ],
    },
    {
        "name": "Linsen-Gemüse-Curry",
        "protein_typ": "Vegetarisch",
        "schwierigkeit": "einfach",
        "kategorie": "Curry",
        "zubereitungszeit_min": 30,
        "portionen_basis": 2,
        "kalorien_pro_portion": 510,
        "zubereitung": (
            "Setze den Reis wie gewohnt auf (doppelte Menge Wasser, Prise Salz, zugedeckt "
            "etwa 15 bis 18 Minuten köcheln lassen), damit er fertig ist, sobald das Curry "
            "fertig ist.\n"
            "Schäle die Zwiebel und den Knoblauch und schneide beides fein. Erhitze etwas "
            "Öl in einem Topf und dünste die Zwiebel darin glasig an, gib dann den "
            "Knoblauch dazu und brate ihn kurz mit, ohne dass er braun wird. Streue das "
            "Currypulver darüber und röste es für etwa eine halbe Minute unter Rühren mit, "
            "das intensiviert das Aroma deutlich.\n"
            "Spüle die roten Linsen kurz unter kaltem Wasser ab und gib sie zusammen mit "
            "der in Scheiben geschnittenen Karotte in den Topf. Gieße die Kokosmilch dazu "
            "und fülle mit etwas Wasser auf, bis die Linsen knapp bedeckt sind.\n"
            "Lass alles aufkochen und dann bei mittlerer Hitze offen etwa 12 bis 15 "
            "Minuten köcheln, bis die Linsen weich sind und das Curry eine sämige "
            "Konsistenz bekommt. Rühre gelegentlich um, damit nichts anbrennt.\n"
            "Gib den gewaschenen Spinat erst in den letzten zwei Minuten dazu und rühre "
            "ihn unter, er soll gerade zusammenfallen, aber nicht verkochen. Schmecke das "
            "Curry mit Salz und bei Bedarf noch etwas Currypulver ab.\n"
            "Serviere das Curry heiß über dem gekochten Reis."
        ),
        "zutaten": [
            ("Rote Linsen", 150, "g"),
            ("Kokosmilch", 200, "ml"),
            ("Karotte", 1, "Stück"),
            ("Spinat", 100, "g"),
            ("Zwiebel", 1, "Stück"),
            ("Currypulver", 1, "EL"),
            ("Knoblauchzehe", 1, "Stück"),
            ("Reis", 150, "g"),
        ],
    },
    {
        "name": "Gebratener Thunfisch mit Süßkartoffelpüree",
        "protein_typ": "Fisch",
        "schwierigkeit": "aufwaendig",
        "kategorie": "Pfannengericht",
        "zubereitungszeit_min": 45,
        "portionen_basis": 2,
        "kalorien_pro_portion": 490,
        "zubereitung": (
            "Schäle die Süßkartoffeln und schneide sie in grobe Würfel. Gib sie in einen "
            "Topf mit kaltem, leicht gesalzenem Wasser, bringe es zum Kochen und lasse die "
            "Würfel etwa 15 bis 20 Minuten köcheln, bis sie mit einer Gabel mühelos "
            "durchstochen werden können.\n"
            "Gieße die Süßkartoffeln ab und stampfe sie noch heiß mit der Butter zu einem "
            "glatten Püree. Schmecke mit Salz und etwas Pfeffer ab und halte das Püree "
            "warm.\n"
            "Wasche den grünen Spargel und schneide die holzigen Enden ab. Dünste ihn in "
            "einer Pfanne mit etwas Wasser und einer Prise Salz für etwa 5 bis 7 Minuten, "
            "bis er bissfest ist, und stelle ihn dann beiseite.\n"
            "Tupfe die Thunfischsteaks trocken und wende sie rundum in Sesam, sodass sie "
            "gleichmäßig bedeckt sind. Erhitze etwas Öl in einer beschichteten Pfanne bei "
            "hoher Hitze, bis es fast zu rauchen beginnt.\n"
            "Brate die Steaks nur etwa 1 bis 1,5 Minuten pro Seite scharf an - der Kern "
            "soll innen noch rosa und glasig bleiben, außen der Sesam aber schön geröstet "
            "sein. Nimm die Steaks sofort aus der Pfanne, damit sie nicht nachgaren.\n"
            "Richte das Süßkartoffelpüree und den Spargel auf Tellern an, lege den "
            "Thunfisch obenauf und beträufle alles zum Schluss mit etwas Sojasauce."
        ),
        "zutaten": [
            ("Thunfischsteak", 300, "g"),
            ("Süßkartoffel", 2, "Stück"),
            ("Butter", 1, "EL"),
            ("Grüner Spargel", 100, "g"),
            ("Sesam", 1, "EL"),
            ("Sojasauce", 1, "EL"),
        ],
    },
    {
        "name": "Klassische Gemüsesuppe",
        "protein_typ": "Vegetarisch",
        "schwierigkeit": "einfach",
        "kategorie": "Suppe",
        "zubereitungszeit_min": 35,
        "portionen_basis": 4,
        "kalorien_pro_portion": 180,
        "zubereitung": (
            "Schäle die Karotten, den Sellerie und die Kartoffeln und schneide alles in "
            "gleichmäßig kleine Würfel, damit sie später gleichmäßig gar werden.\n"
            "Schäle die Zwiebel, schneide sie fein und dünste sie in einem großen Topf mit "
            "etwas Öl bei mittlerer Hitze glasig an, ohne dass sie Farbe annimmt.\n"
            "Gib das restliche Gemüse dazu und brate es unter Rühren etwa 2 bis 3 Minuten "
            "mit, damit sich die Aromen leicht entfalten können.\n"
            "Gieße die Gemüsebrühe auf, bringe alles zum Kochen und lasse die Suppe dann "
            "bei mittlerer Hitze offen etwa 20 Minuten köcheln, bis das Gemüse weich ist.\n"
            "Schmecke die Suppe mit Salz, Pfeffer und frischen oder getrockneten Kräutern "
            "ab, zum Beispiel Petersilie oder Liebstöckel. Wer es cremiger mag, kann einen "
            "Teil der Suppe mit dem Stabmixer fein pürieren und wieder unterrühren.\n"
            "Vor dem Servieren nochmals abschmecken, da sich der Geschmack beim Köcheln "
            "noch etwas verändert."
        ),
        "zutaten": [
            ("Karotte", 3, "Stück"),
            ("Sellerie", 100, "g"),
            ("Kartoffel", 3, "Stück"),
            ("Zwiebel", 1, "Stück"),
            ("Gemüsebrühe", 1000, "ml"),
        ],
    },
    {
        "name": "Hühnersuppe mit Nudeln",
        "protein_typ": "Huhn",
        "schwierigkeit": "mittel",
        "kategorie": "Suppe",
        "zubereitungszeit_min": 50,
        "portionen_basis": 4,
        "kalorien_pro_portion": 320,
        "zubereitung": (
            "Wasche das Suppenhuhn kurz ab und gib es zusammen mit kaltem Wasser in einen "
            "großen Topf, sodass es gut bedeckt ist. Bringe es langsam zum Kochen und "
            "schöpfe den aufsteigenden Schaum mit einer Kelle ab, das sorgt für eine "
            "klare Brühe.\n"
            "Schäle die Karotten und die Petersilienwurzel, putze den Sellerie und "
            "schneide alles grob. Gib das Wurzelgemüse zusammen mit etwas Salz zum Huhn "
            "in den Topf.\n"
            "Lasse alles bei geringer Hitze zugedeckt etwa 45 Minuten sanft köcheln, ohne "
            "dass es stark sprudelt - so bleibt die Brühe klar und das Fleisch wird "
            "zart.\n"
            "Nimm das Huhn aus dem Topf und lasse es kurz abkühlen, bis du es anfassen "
            "kannst. Löse das Fleisch von den Knochen, entferne Haut und Knochen und "
            "schneide oder zupfe das Fleisch in mundgerechte Stücke.\n"
            "Koche die Suppennudeln separat in leicht gesalzenem Wasser nach "
            "Packungsanweisung bissfest und gieße sie ab.\n"
            "Gib das Hühnerfleisch zurück in die Brühe, schmecke mit Salz und Pfeffer ab "
            "und erhitze alles noch einmal kurz. Verteile die Nudeln auf die Suppenteller "
            "und gieße die heiße Suppe darüber."
        ),
        "zutaten": [
            ("Suppenhuhn", 500, "g"),
            ("Karotte", 2, "Stück"),
            ("Sellerie", 100, "g"),
            ("Petersilienwurzel", 1, "Stück"),
            ("Suppennudeln", 150, "g"),
        ],
    },
    {
        "name": "Rindergulasch",
        "protein_typ": "Rind",
        "schwierigkeit": "aufwaendig",
        "kategorie": "Eintopf",
        "zubereitungszeit_min": 120,
        "portionen_basis": 4,
        "kalorien_pro_portion": 540,
        "zubereitung": (
            "Schäle die Zwiebeln und schneide sie in feine Würfel - je feiner, desto "
            "besser lösen sie sich später in der Sauce auf. Schneide das Rindfleisch in "
            "grobe, etwa daumengroße Würfel.\n"
            "Erhitze etwas Öl in einem großen, schweren Topf und brate das Fleisch darin "
            "portionsweise scharf von allen Seiten an. Portionsweise ist wichtig, damit "
            "das Fleisch wirklich Farbe bekommt und nicht im eigenen Saft köchelt. Nimm "
            "es nach jeder Portion kurz heraus.\n"
            "Gib die Zwiebeln in denselben Topf und brate sie bei mittlerer Hitze an, bis "
            "sie goldbraun und weich sind, das dauert etwa 10 Minuten. Nimm den Topf kurz "
            "von der Hitze, rühre das Paprikapulver ein und röste es nur ganz kurz mit, "
            "da es sonst schnell bitter wird.\n"
            "Rühre das Tomatenmark unter, gib das Fleisch zurück in den Topf und lösche "
            "alles mit der Rinderbrühe ab, sodass das Fleisch gerade bedeckt ist. Bringe "
            "alles zum Kochen.\n"
            "Reduziere die Hitze auf ein Minimum, decke den Topf zu und lasse das Gulasch "
            "etwa 90 Minuten sanft schmoren. Rühre gelegentlich um und gieße bei Bedarf "
            "etwas Wasser oder Brühe nach, falls zu viel Flüssigkeit verdunstet.\n"
            "Das Gulasch ist fertig, wenn das Fleisch butterzart ist und sich fast von "
            "selbst zerteilen lässt. Schmecke noch einmal mit Salz, Pfeffer und bei Bedarf "
            "etwas mehr Paprikapulver ab, bevor du es servierst."
        ),
        "zutaten": [
            ("Rindfleisch (Gulasch)", 600, "g"),
            ("Zwiebel", 4, "Stück"),
            ("Paprikapulver", 2, "EL"),
            ("Tomatenmark", 1, "EL"),
            ("Rinderbrühe", 500, "ml"),
        ],
    },
]


def seed_users(conn):
    for u in BEISPIEL_NUTZER:
        exists = conn.execute(
            "SELECT id FROM users WHERE username = ?", (u["username"],)
        ).fetchone()
        if exists:
            continue
        pw_hash = bcrypt.hashpw(u["passwort"].encode(), bcrypt.gensalt()).decode()
        conn.execute(
            "INSERT INTO users (username, name, password_hash) VALUES (?, ?, ?)",
            (u["username"], u["name"], pw_hash),
        )
    conn.commit()


def seed_rezepte(conn):
    for r in BEISPIEL_REZEPTE:
        bild_url = r.get("bild_override") or waehle_illustration(r["protein_typ"], r["kategorie"])
        gang = r.get("gang", "Hauptgang")
        mahlzeiten = r.get("mahlzeiten", "Mittagessen,Abendessen")

        exists = conn.execute(
            "SELECT id FROM rezepte WHERE name = ?", (r["name"],)
        ).fetchone()
        if exists:
            # Rezept gibt es schon (z.B. aus einem frueheren Lauf) - Illustration
            # trotzdem auf den aktuellen Stand bringen, ohne alles neu anzulegen
            conn.execute(
                "UPDATE rezepte SET bild_url = ?, gang = ?, mahlzeiten = ? WHERE id = ?",
                (bild_url, gang, mahlzeiten, exists["id"]),
            )
            continue

        cur = conn.execute(
            """INSERT INTO rezepte
               (name, protein_typ, schwierigkeit, kategorie, gang, mahlzeiten, zubereitungszeit_min,
                portionen_basis, kalorien_pro_portion, bild_url, zubereitung,
                ist_custom, freigeschaltet)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 1)""",
            (
                r["name"], r["protein_typ"], r["schwierigkeit"], r["kategorie"], gang, mahlzeiten,
                r["zubereitungszeit_min"], r["portionen_basis"],
                r["kalorien_pro_portion"], bild_url, r["zubereitung"],
            ),
        )
        rezept_id = cur.lastrowid
        for name, menge, einheit in r["zutaten"]:
            conn.execute(
                "INSERT INTO zutaten (rezept_id, name, menge, einheit) VALUES (?, ?, ?, ?)",
                (rezept_id, name, menge, einheit),
            )
    conn.commit()


def seed_achievements(conn):
    from gamification import ACHIEVEMENTS
    for code, (name, beschreibung, _bedingung) in ACHIEVEMENTS.items():
        conn.execute(
            "INSERT OR IGNORE INTO achievements (code, name, beschreibung) VALUES (?, ?, ?)",
            (code, name, beschreibung),
        )
    conn.commit()


if __name__ == "__main__":
    init_db()
    conn = get_connection()
    seed_users(conn)
    seed_rezepte(conn)
    seed_achievements(conn)
    conn.close()
    print("Beispieldaten erfolgreich eingefügt.")
