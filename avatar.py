"""
avatar.py
=========
Profilbild-Baukasten: Basis-Koch (Mann/Frau) + Kopfbedeckung +
Gesichts-Accessoire + Gegenstand-Abzeichen. Alle Bilder werden live mit
Pillow zusammengesetzt, nichts wird dauerhaft auf der Festplatte gespeichert.

Nutzt ein neueres, saubereres Asset-Paket (bereits transparent) fuer Basis-
Figuren und einen Teil des Zubehoers; wo dafuer noch kein Ersatz vorliegt,
wird das urspruengliche (selbst freigestellte) Zubehoer weiterverwendet.
"""

from pathlib import Path
from PIL import Image, ImageDraw

AVATAR_DIR = Path(__file__).parent / "assets" / "avatar"

BASIS_OPTIONEN = {
    "mann": "basis2_mann.png",
    "frau": "basis2_frau.png",
}
# Gesichtsmitte (x) je Basis - wird von allen Kopf-/Gesichts-Accessoires genutzt
BASIS_MITTE_X = {"mann": 273, "frau": 254}

# (Dateiname, Zielbreite, Mitte-Y) je Basis
KOPFBEDECKUNG_OPTIONEN = {
    "keins": None,
    "kochmuetze": {
        "datei": "neu_kochmuetze.png",
        "mann": (330, 70), "frau": (300, 60),
    },
    "beanie": {
        "datei": "neu_beanie.png",
        "mann": (300, 95), "frau": (275, 85),
    },
    "barett": {
        "datei": "neu_barett.png",
        "mann": (300, 90), "frau": (275, 80),
    },
    "grillmeister_cap": {
        "datei": "neu_grillmeister_cap.png",
        "mann": (300, 100), "frau": (275, 90),
    },
    "bandana": {
        "datei": "neu_bandana.png",
        "mann": (300, 100), "frau": (275, 105),
    },
    "krone": {
        "datei": "neu_krone.png",
        "mann": (270, 90), "frau": (245, 84),
    },
    "wikinger_helm": {
        "datei": "neu_wikinger_helm.png",
        "mann": (340, 95), "frau": (310, 85),
    },
    "stirnband": {
        "datei": "neu_stirnband.png",
        "mann": (280, 108), "frau": (270, 103),
    },
}
KOPFBEDECKUNG_ANZEIGE = {
    "keins": "Keine Kopfbedeckung",
    "kochmuetze": "👨‍🍳 Kochmütze",
    "beanie": "🧢 Beanie",
    "barett": "🎨 Barett",
    "grillmeister_cap": "🧢 Grillmeister-Cap",
    "bandana": "🥷 Bandana",
    "krone": "👑 Krone",
    "wikinger_helm": "⚔️ Wikinger-Helm",
    "stirnband": "🎌 Stirnband",
}

# (Dateiname, Zielbreite, Mitte-Y) je Basis
GESICHT_OPTIONEN = {
    "keins": None,
    "sonnenbrille": {
        "datei": "neu_sonnenbrille.png",
        "mann": (230, 260), "frau": (210, 240),
    },
    "schnurrbart": {
        "datei": "neu_schnurrbart.png",
        "mann": (170, 320), "frau": (155, 300),
    },
    "bart": {
        "datei": "neu_bart.png",
        "mann": (220, 350), "frau": (200, 330),
    },
}
GESICHT_ANZEIGE = {
    "keins": "Kein Gesichts-Accessoire",
    "sonnenbrille": "🕶️ Sonnenbrille",
    "schnurrbart": "👨 Schnurrbart",
    "bart": "🧔 Vollbart",
}

# (Dateiname, Zielbreite, Mitte-Y) je Basis - sitzt am Kragen/Hals
HALS_OPTIONEN = {
    "keins": None,
    "halstuch": {
        "datei": "neu_halstuch.png",
        "mann": (220, 460), "frau": (200, 430),
    },
}
HALS_ANZEIGE = {
    "keins": "Kein Halstuch",
    "halstuch": "🧣 Halstuch",
}

EXTRA_OPTIONEN = {
    "keins": None,
    "pfanne": "neu_pfanne.png",
    "kochloeffel": "neu_kochloeffel.png",
    "pfannenwender": "neu_pfannenwender.png",
    "essstaebchen": "neu_essstaebchen.png",
    "hackmesser": "neu_hackmesser.png",
    "kelle": "neu_kelle.png",
    "schneebesen": "neu_schneebesen.png",
    "wurst_gabel": "neu_wurst_gabel.png",
    "pizza": "neu_pizza.png",
    "spaghetti": "neu_spaghetti.png",
    "sushi": "neu_sushi.png",
    "pancakes": "neu_pancakes.png",
    "kaffee": "neu_kaffee.png",
    "kolben_gruen": "neu_kolben_gruen.png",
    "kolben_rot": "neu_kolben_rot.png",
    "reagenzglas": "neu_reagenzglas.png",
    "salz": "neu_salz.png",
    "pfeffer": "neu_pfeffer.png",
}
EXTRA_ANZEIGE = {
    "keins": "Kein Abzeichen",
    "pfanne": "🍳 Pfanne",
    "kochloeffel": "🥄 Kochlöffel",
    "pfannenwender": "🔧 Pfannenwender",
    "essstaebchen": "🥢 Essstäbchen",
    "hackmesser": "🔪 Hackmesser",
    "kelle": "🥣 Schöpfkelle",
    "schneebesen": "🌀 Schneebesen",
    "wurst_gabel": "🌭 Wurst am Spieß",
    "pizza": "🍕 Pizza",
    "spaghetti": "🍝 Spaghetti",
    "sushi": "🍣 Sushi",
    "pancakes": "🥞 Pancakes",
    "kaffee": "☕ Kaffee",
    "kolben_gruen": "🧪 Grüner Kolben",
    "kolben_rot": "🧪 Roter Kolben",
    "reagenzglas": "🧫 Reagenzglas",
    "salz": "🧂 Salz",
    "pfeffer": "🧂 Pfeffer",
}


def _zubehoer_einfuegen(bild, datei, ziel_breite, mitte_x, mitte_y):
    zubehoer = Image.open(AVATAR_DIR / datei).convert("RGBA")
    skala = ziel_breite / zubehoer.width
    neue_hoehe = int(zubehoer.height * skala)
    zubehoer = zubehoer.resize((ziel_breite, neue_hoehe), Image.LANCZOS)
    pos = (int(mitte_x - ziel_breite / 2), int(mitte_y - neue_hoehe / 2))
    bild.alpha_composite(zubehoer, pos)


def erstelle_avatar(basis: str, kopfbedeckung: str = "kochmuetze", gesicht: str = "keins", extra: str = "keins", hals: str = "keins") -> Image.Image:
    """Baut das Profilbild aus Basis-Figur + optionaler Kopfbedeckung +
    optionalem Gesichts-Accessoire + optionalem Halstuch + optionalem
    Gegenstand-Abzeichen zusammen. Gibt ein PIL-Image zurueck (nichts wird
    auf der Festplatte gespeichert)."""
    basis_datei = BASIS_OPTIONEN.get(basis, BASIS_OPTIONEN["mann"])
    bild = Image.open(AVATAR_DIR / basis_datei).convert("RGBA")
    mitte_x = BASIS_MITTE_X.get(basis, BASIS_MITTE_X["mann"])

    kopf_info = KOPFBEDECKUNG_OPTIONEN.get(kopfbedeckung)
    if kopf_info:
        breite, mitte_y = kopf_info.get(basis, kopf_info["mann"])
        _zubehoer_einfuegen(bild, kopf_info["datei"], breite, mitte_x, mitte_y)

    gesicht_info = GESICHT_OPTIONEN.get(gesicht)
    if gesicht_info:
        breite, mitte_y = gesicht_info.get(basis, gesicht_info["mann"])
        _zubehoer_einfuegen(bild, gesicht_info["datei"], breite, mitte_x, mitte_y)

    hals_info = HALS_OPTIONEN.get(hals)
    if hals_info:
        breite, mitte_y = hals_info.get(basis, hals_info["mann"])
        _zubehoer_einfuegen(bild, hals_info["datei"], breite, mitte_x, mitte_y)

    extra_datei = EXTRA_OPTIONEN.get(extra)
    if extra_datei:
        bw, bh = bild.size
        durchmesser = 170
        kreis = Image.new("RGBA", (durchmesser, durchmesser), (0, 0, 0, 0))
        draw = ImageDraw.Draw(kreis)
        draw.ellipse((0, 0, durchmesser - 1, durchmesser - 1), fill=(255, 255, 255, 255), outline=(26, 26, 26, 255), width=6)
        item = Image.open(AVATAR_DIR / extra_datei).convert("RGBA")
        item_breite = int(durchmesser * 0.62)
        skala = item_breite / item.width
        item_hoehe = int(item.height * skala)
        item = item.resize((item_breite, item_hoehe), Image.LANCZOS)
        kreis.alpha_composite(item, ((durchmesser - item_breite) // 2, (durchmesser - item_hoehe) // 2))
        bild.alpha_composite(kreis, (bw - durchmesser - 5, bh - durchmesser - 15))

    return bild
