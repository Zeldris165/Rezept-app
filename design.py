"""
design.py
=========
Zentrale Design-Tokens (Farben, Typografie) und das globale CSS, das die
App von "Standard-Streamlit-Optik" auf einen eigenen, wärmeren Look bringt.
Bewusst an einer Stelle gesammelt, damit Farb-/Stiländerungen nicht über
die ganze app.py verstreut gepflegt werden müssen.
"""

# Warmer Standard-Hintergrund, falls der Nutzer keine eigene Farbe gewählt hat
# (ersetzt Streamlits reines Weiß durch einen dezenten Papierton)
DEFAULT_BG = "#FAF6EF"

TEXT_HAUPT = "#2B2823"
AKZENT_PRIMAER = "#2F6F77"   # tiefes Petrol - Buttons, Level-Balken, Linkfarbe
AKZENT_GOLD = "#C98A2B"      # gedecktes Gold - Errungenschaften, Hervorhebungen

# Farbcode je Proteinart, passend zu den Illustrations-Hintergründen
# (rot = Fleisch, blau = Fisch, grün = vegetarisch)
PROTEIN_AKZENT = {
    "Huhn": "#D9534F",
    "Rind": "#D9534F",
    "Schwein": "#D9534F",
    "Lamm": "#D9534F",
    "Fisch": "#5FA8B8",
    "Vegetarisch": "#7BAE7F",
}

# Farbcode je Kochlexikon-Kategorie, passend zu den Icon-Hintergründen
KATEGORIE_AKZENT = {
    "Feuchte Garmethoden": "#5FA8B8",
    "Trockene/heiße Garmethoden": "#D9724C",
    "Sauce & Technik": "#C98A2B",
    "Vorbereitung": "#7BAE7F",
}


def akzent_farbe_fuer_protein(protein_typ: str) -> str:
    return PROTEIN_AKZENT.get(protein_typ, "#B0AFA8")


def akzent_farbe_fuer_kategorie(kategorie: str) -> str:
    return KATEGORIE_AKZENT.get(kategorie, "#B0AFA8")


SCHWIERIGKEIT_FARBE = {
    "einfach": "#7BAE7F",
    "mittel": "#C98A2B",
    "aufwaendig": "#D9534F",
}
SCHWIERIGKEIT_ANZEIGE = {
    "einfach": "Leicht",
    "mittel": "Mittel",
    "aufwaendig": "Schwer",
}


def schwierigkeit_badge_html(schwierigkeit: str) -> str:
    """Kleines farbiges Abzeichen fuer den Schwierigkeitsgrad (Leicht/Mittel/Schwer)."""
    farbe = SCHWIERIGKEIT_FARBE.get(schwierigkeit, "#B0AFA8")
    text = SCHWIERIGKEIT_ANZEIGE.get(schwierigkeit, schwierigkeit)
    return (
        f'<span style="background:{farbe};color:white;padding:2px 10px;'
        f'border-radius:10px;font-size:12px;font-weight:600;">{text}</span>'
    )


def akzent_balken_html(farbe: str) -> str:
    """Ein kleiner farbiger Streifen oben in einer Kachel, als visueller Kategorie-Hinweis."""
    return (
        f'<div style="height:5px;width:100%;background:{farbe};'
        f'border-radius:4px;margin-bottom:10px;"></div>'
    )


def globales_css(hintergrundfarbe: str | None) -> str:
    """Baut das komplette globale CSS: Typografie, Kacheln, Buttons, Fortschrittsbalken,
    und die Hintergrundfarbe (eigene Wahl oder warmer Standard)."""
    farbe = hintergrundfarbe or DEFAULT_BG

    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
    color: {TEXT_HAUPT};
}}

h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
    font-family: 'Fraunces', serif !important;
    font-weight: 700 !important;
    letter-spacing: -0.01em;
}}

/* Seitenhintergrund: eigene Farbe oder warmer Standard statt reinem Weiss */
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"],
[data-testid="stHeader"] {{
    background: transparent !important;
}}

/* Kacheln (Rezepte, Lexikon, Wochenplan-Auswahl) - immer opak, mit Schatten und Hover */
div[data-testid="stVerticalBlock"]:has(> div.stElementContainer .karten-marker) {{
    background-color: #FFFFFF !important;
    border-radius: 16px !important;
    box-shadow: 0 2px 10px rgba(43,40,35,0.07);
    transition: box-shadow 0.15s ease, transform 0.15s ease;
}}
div[data-testid="stVerticalBlock"]:has(> div.stElementContainer .karten-marker):hover {{
    box-shadow: 0 8px 20px rgba(43,40,35,0.13);
    transform: translateY(-2px);
}}

/* Primaere Buttons in der Akzentfarbe */
[data-testid="stBaseButton-primary"] {{
    background-color: {AKZENT_PRIMAER} !important;
    border-color: {AKZENT_PRIMAER} !important;
    border-radius: 10px !important;
    transition: transform 0.12s ease, box-shadow 0.12s ease, filter 0.12s ease;
}}
[data-testid="stBaseButton-secondary"] {{
    border-radius: 10px !important;
    transition: transform 0.12s ease, box-shadow 0.12s ease;
}}
/* Einheitlicher Hover-Effekt fuer ALLE Buttons app-weit, nicht nur einzelne Bereiche */
[data-testid="stBaseButton-primary"]:hover {{
    transform: translateY(-1px);
    box-shadow: 0 4px 10px rgba(47,111,119,0.25);
    filter: brightness(1.05);
}}
[data-testid="stBaseButton-secondary"]:hover {{
    transform: translateY(-1px);
    box-shadow: 0 4px 10px rgba(43,40,35,0.10);
}}

/* Fortschrittsbalken (Level-XP) in der Akzentfarbe */
div[data-testid="stProgressBarTrack"] > div {{
    background-color: {AKZENT_PRIMAER} !important;
}}

/* Sidebar-Navigation als Pillen statt Radiobutton-Kreise */
section[data-testid="stSidebar"] [data-testid="stRadioOption"] > div > div > div:first-child {{
    display: none;
}}
section[data-testid="stSidebar"] [data-testid="stRadioOption"] {{
    padding: 10px 14px !important;
    border-radius: 10px !important;
    margin-bottom: 3px !important;
    transition: background-color 0.15s ease, transform 0.1s ease;
    cursor: pointer;
    width: 100%;
}}
section[data-testid="stSidebar"] [data-testid="stRadioOption"]:hover {{
    background-color: rgba(47, 111, 119, 0.10) !important;
    transform: translateX(2px);
}}
section[data-testid="stSidebar"] [data-testid="stRadioOption"][data-selected="true"] {{
    background-color: {AKZENT_PRIMAER} !important;
}}
section[data-testid="stSidebar"] [data-testid="stRadioOption"][data-selected="true"] [data-testid="stMarkdownContainer"] p {{
    color: white !important;
    font-weight: 600;
}}
section[data-testid="stSidebar"] [data-testid="stRadioGroup"] {{
    gap: 0px !important;
}}

/* Errungenschaften-Kacheln: dezenter Hover-Effekt */
.errungenschaft-kachel {{
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}}
.errungenschaft-kachel:hover {{
    transform: translateY(-2px);
    box-shadow: 0 6px 14px rgba(43,40,35,0.10);
}}

/* Weniger Leerraum ganz oben, damit Logo + Inhalt hoeher sitzen */
[data-testid="stMainBlockContainer"] {{
    padding-top: 2rem !important;
}}

/* Einheitliche Abstaende: Titel -> Caption -> Inhalt, ueberall gleich */
h1 {{
    margin-bottom: 2px !important;
}}
[data-testid="stCaptionContainer"] {{
    margin-bottom: 6px !important;
}}
hr {{
    margin: 22px 0 !important;
}}
[data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:has(> [data-testid="stMarkdownContainer"] strong:only-child) {{
    margin-top: 14px !important;
}}
</style>
<div style="position:fixed;top:0;left:0;right:0;bottom:0;background-color:{farbe};z-index:-1;"></div>
"""


def profil_karte_html(name: str, level: int, xp_im_level: int, xp_fuer_naechstes: int) -> str:
    """HTML fuer die aufgehuebschte Profil-Karte oben in der Sidebar."""
    if xp_fuer_naechstes > 0:
        prozent = round(100 * xp_im_level / xp_fuer_naechstes)
        xp_zeile = f"{xp_im_level} / {xp_fuer_naechstes} XP bis Level {level + 1}"
    else:
        prozent = 100
        xp_zeile = "Maximallevel erreicht! 🎉"

    return f"""
<div style="background: linear-gradient(135deg, {AKZENT_PRIMAER} 0%, #45949C 100%);
            border-radius: 16px; padding: 16px 18px; color: white; margin-bottom: 4px;">
  <div style="font-size:15px; opacity:0.9;">👋 Hallo,</div>
  <div style="font-family:'Fraunces', serif; font-size:22px; font-weight:700; margin-bottom:8px;">
    {name}
  </div>
  <div style="display:flex; justify-content:space-between; font-size:13px; opacity:0.9; margin-bottom:4px;">
    <span>Level {level}</span>
    <span>{prozent}%</span>
  </div>
  <div style="background:rgba(255,255,255,0.3); border-radius:6px; height:8px; overflow:hidden;">
    <div style="background:{AKZENT_GOLD}; width:{prozent}%; height:100%;"></div>
  </div>
  <div style="font-size:12px; opacity:0.85; margin-top:6px;">{xp_zeile}</div>
</div>
"""
