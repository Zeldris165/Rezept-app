"""
app.py
======
Etappe 1 der Rezept-App:
- Mehrbenutzer-Login (streamlit-authenticator)
- Rezept-Bibliothek mit Fotos, Filtern und Detailansicht

Start mit: streamlit run app.py
Vorher einmalig: python seed_data.py  (legt Beispiel-Nutzer & Rezepte an)
"""

import base64
import random
from pathlib import Path


def gewichtete_stichprobe(elemente: list, gewichte: list, k: int) -> list:
    """Waehlt k unterschiedliche Elemente zufaellig aus, wobei hoeher gewichtete
    Elemente bevorzugt (aber nicht ausschliesslich) gezogen werden. Kein
    Zuruecklegen - jedes Element kann nur einmal vorkommen."""
    elemente = list(elemente)
    gewichte = list(gewichte)
    ergebnis = []
    for _ in range(min(k, len(elemente))):
        gesamt = sum(gewichte)
        r = random.uniform(0, gesamt)
        kumuliert = 0
        for i, g in enumerate(gewichte):
            kumuliert += g
            if kumuliert >= r:
                ergebnis.append(elemente.pop(i))
                gewichte.pop(i)
                break
    return ergebnis


def gewichte_nach_kochlevel(rezepte_liste: list) -> list:
    """Gibt eine Gewichtsliste zurueck: Rezepte, die zum eingestellten Kochlevel
    passen, werden 4x bevorzugt gezogen - andere Schwierigkeiten bleiben aber
    weiterhin moeglich (keine harte Filterung). Bei kochlevel='alle' gibt's
    keine Gewichtung (reiner Zufall wie frueher)."""
    kochlevel = user_row["kochlevel"] or "mittel"
    if kochlevel == "alle":
        return [1 for _ in rezepte_liste]
    return [4 if r["schwierigkeit"] == kochlevel else 1 for r in rezepte_liste]

import streamlit as st
import streamlit_authenticator as stauth

from database import get_connection, init_db
from logic import level_aus_xp, xp_bis_naechstes_level
from cart import (
    get_or_create_active_liste,
    add_rezept_zu_warenkorb,
    get_artikel,
    toggle_abgehakt,
    einkauf_abschliessen,
    warenkorb_leeren,
)
from rezepte import (
    get_sichtbare_rezepte,
    get_sichtbare_rezepte_gefiltert,
    verstecke_rezept,
    get_versteckte_rezepte,
    zeige_rezept_wieder,
    ist_favorit,
    favorit_umschalten,
    get_favoriten,
    erstelle_eigene_kopie,
    erstelle_neues_rezept,
)
from glossar import BEGRIFFE, KATEGORIEN
from avatar import (
    erstelle_avatar,
    KOPFBEDECKUNG_OPTIONEN,
    KOPFBEDECKUNG_ANZEIGE,
    GESICHT_OPTIONEN,
    GESICHT_ANZEIGE,
    HALS_OPTIONEN,
    HALS_ANZEIGE,
    EXTRA_OPTIONEN,
    EXTRA_ANZEIGE,
)
from wochenplan import (
    WOCHENTAGE,
    MAHLZEITEN_TAG,
    aktuelle_kalenderwoche,
    get_wochenplan,
    setze_tag,
    entferne_tag,
)
from praeferenzen import PRAEFERENZEN
from freunde import (
    nutzer_suchen,
    sende_freundschaftsanfrage,
    eingehende_anfragen,
    anfrage_annehmen,
    anfrage_ablehnen,
    freundschaft_entfernen,
    meine_freunde,
    bestenliste,
)
from gamification import (
    kochen_markieren,
    get_alle_achievements_mit_status,
    get_achievements_gruppiert,
    get_kochprotokoll_historie,
)
from design import (
    globales_css,
    profil_karte_html,
    akzent_farbe_fuer_protein,
    akzent_farbe_fuer_kategorie,
    akzent_balken_html,
    schwierigkeit_badge_html,
)

st.set_page_config(page_title="Deckel zum Topf", page_icon="assets/branding/icon_oliv.png", layout="wide")

init_db()  # stellt sicher, dass die Tabellen existieren

APP_DIR = Path(__file__).parent


def leerer_zustand_html(text: str, bild_pfad: str = None, emoji: str = "🍽️") -> str:
    """Baut einen freundlichen, zentrierten Leerzustand-Block statt einer
    schlichten grauen Info-Box - mit Illustration oder grossem Emoji."""
    if bild_pfad:
        bild_teil = rundes_bild_html(bild_pfad, groesse=110)
    else:
        bild_teil = f'<div style="font-size:52px;">{emoji}</div>'

    return f"""
<div style="text-align:center; padding:36px 20px; background:#F7F3EA;
            border-radius:16px; margin:12px 0;">
    {bild_teil}
    <div style="margin-top:14px; color:#6B6558; font-size:15px; max-width:360px;
                margin-left:auto; margin-right:auto;">{text}</div>
</div>
"""


def rundes_bild_html(bild_pfad: str, groesse: int = 180) -> str:
    """Baut ein <img>-Tag, das die Illustration/das Bild rund zuschneidet.
    Unterstützt lokale SVG- und PNG/JPG-Dateien (base64 eingebettet) sowie externe URLs."""
    if not bild_pfad:
        return ""

    if bild_pfad.startswith("http://") or bild_pfad.startswith("https://"):
        src = bild_pfad
    else:
        voller_pfad = APP_DIR / bild_pfad
        endung = voller_pfad.suffix.lower()
        try:
            if endung == ".svg":
                svg_text = voller_pfad.read_text(encoding="utf-8")
                b64 = base64.b64encode(svg_text.encode("utf-8")).decode("utf-8")
                src = f"data:image/svg+xml;base64,{b64}"
            else:
                mime = "image/png" if endung == ".png" else "image/jpeg"
                bild_bytes = voller_pfad.read_bytes()
                b64 = base64.b64encode(bild_bytes).decode("utf-8")
                src = f"data:{mime};base64,{b64}"
        except Exception:
            return ""

    return (
        f'<img src="{src}" '
        f'style="width:{groesse}px; height:{groesse}px; border-radius:50%; '
        f'object-fit:contain; background-color:#FFFFFF; display:block; margin:0 auto; '
        f'border:3px solid #F0F0F0;" />'
    )


# ---------------------------------------------------------------
# Login
# ---------------------------------------------------------------
def lade_credentials():
    """Baut das Credentials-Dict für streamlit-authenticator direkt aus der DB."""
    conn = get_connection()
    rows = conn.execute("SELECT username, name, password_hash FROM users").fetchall()
    conn.close()
    usernames = {
        row["username"]: {"name": row["name"], "password": row["password_hash"]}
        for row in rows
    }
    return {"usernames": usernames}


credentials = lade_credentials()

if not credentials["usernames"]:
    # Frische Datenbank (z.B. erster Start auf einem neuen Deploy) - automatisch
    # mit Beispiel-Nutzern/-Rezepten befuellen, da dort kein Terminalzugriff
    # fuer `python seed_data.py` besteht.
    from seed_data import seed_users, seed_rezepte, seed_achievements
    conn_seed = get_connection()
    seed_users(conn_seed)
    seed_rezepte(conn_seed)
    seed_achievements(conn_seed)
    conn_seed.close()
    credentials = lade_credentials()

if not credentials["usernames"]:
    st.error("Datenbank konnte nicht automatisch befüllt werden.")
    st.stop()

authenticator = stauth.Authenticate(
    credentials,
    cookie_name="rezept_app_cookie",
    key="rezept_app_signature_key",  # in Produktion: aus Umgebungsvariable laden
    cookie_expiry_days=7,
)

# CSS schon vor dem Login/Splash laden, damit Buttons & Schrift von Anfang an
# im Marken-Look erscheinen (nicht erst nach dem Einloggen)
st.markdown(globales_css(None), unsafe_allow_html=True)

# --- Splash-Bildschirm: grosses Logo, muss per Klick bestaetigt werden,
# damit man es nicht nur eine Millisekunde lang sieht, bevor ein gueltiges
# Login-Cookie sofort in die App weiterleitet ---
if "splash_gesehen" not in st.session_state:
    st.session_state["splash_gesehen"] = False

if not st.session_state["splash_gesehen"]:
    splash_platzhalter = st.empty()
    with splash_platzhalter.container():
        st.markdown("<div style='height:60px;'></div>", unsafe_allow_html=True)
        col_l, col_m, col_r = st.columns([1, 2, 1])
        with col_m:
            st.markdown(
                '<div style="text-align:center;font-family:\'Fraunces\',serif;font-weight:700;'
                'font-size:24px;margin-bottom:6px;">Willkommen zum</div>',
                unsafe_allow_html=True,
            )
            st.image("assets/branding/logo_haupt_transparent.png", use_container_width=True)
            st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
            weiter_geklickt = st.button("Weiter", type="primary", use_container_width=True, key="splash_weiter")
            st.markdown(
                """
                <style>
                @keyframes splashHinweisEinblenden { from { opacity: 0; } to { opacity: 1; } }
                #stMain { transition: opacity 0.25s ease-out; }
                </style>
                <div style="text-align:center; margin-top:16px; color:#8A8578; font-size:14px;
                            opacity:0; animation: splashHinweisEinblenden 0.6s ease-in 5s forwards;">
                    👆 Klicke auf "Weiter", um fortzufahren
                </div>
                <script>
                (function() {
                    var versuche = 0;
                    var intervall = setInterval(function() {
                        versuche += 1;
                        var buttons = document.querySelectorAll('button');
                        buttons.forEach(function(btn) {
                            if (btn.innerText.trim() === 'Weiter' && !btn.dataset.fadeGebunden) {
                                btn.dataset.fadeGebunden = 'true';
                                btn.addEventListener('click', function() {
                                    var haupt = document.querySelector('[data-testid="stMain"]');
                                    if (haupt) {
                                        haupt.style.transition = 'opacity 0.3s ease-out';
                                        haupt.style.opacity = '0';
                                    }
                                });
                                clearInterval(intervall);
                            }
                        });
                        if (versuche > 20) { clearInterval(intervall); }
                    }, 100);
                })();
                </script>
                """,
                unsafe_allow_html=True,
            )
    if weiter_geklickt:
        # Platzhalter explizit leeren, BEVOR neu gerendert wird - sonst bleibt
        # der Splash-Screen beim Seitenwechsel kurz sichtbar haengen
        splash_platzhalter.empty()
        st.session_state["splash_gesehen"] = True
        st.rerun()
    st.stop()

login_logo_platzhalter = st.empty()

authenticator.login(location="main")

if st.session_state.get("authentication_status") is not True:
    with login_logo_platzhalter.container():
        col_logo_l, col_logo_m, col_logo_r = st.columns([1, 2, 1])
        with col_logo_m:
            st.image("assets/branding/logo_karte_creme.png", use_container_width=True)

if st.session_state.get("authentication_status") is False:
    st.error("Benutzername oder Passwort ist falsch.")
    st.stop()
elif st.session_state.get("authentication_status") is None:
    st.info("Bitte einloggen, um Deckel zum Topf zu nutzen.")
    st.stop()

# Ab hier ist der Nutzer eingeloggt
username = st.session_state["username"]
name = st.session_state["name"]

conn = get_connection()
user_row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
conn.close()

st.markdown(globales_css(user_row["hintergrundfarbe"]), unsafe_allow_html=True)

# Logo einmalig, zentriert, oben im Hauptbereich (nicht in der Sidebar)
col_logo_l, col_logo_m, col_logo_r = st.columns([1, 2, 1])
with col_logo_m:
    st.image("assets/branding/logo_haupt_transparent.png", use_container_width=True)


def aktive_praeferenzen() -> list:
    roh = user_row["ernaehrungspraeferenzen"]
    return [c for c in roh.split(",") if c] if roh else []


# ---------------------------------------------------------------
# Sidebar: Nutzerinfo, Level-Anzeige, Logout, Navigation
# ---------------------------------------------------------------
with st.sidebar:
    avatar_bild = erstelle_avatar(
        user_row["avatar_basis"] or "mann",
        user_row["avatar_kopfbedeckung"] or "kochmuetze",
        user_row["avatar_gesicht"] or "keins",
        user_row["avatar_extra"] or "keins",
        user_row["avatar_hals"] or "keins",
    )
    col_av_l, col_av_m, col_av_r = st.columns([1, 1, 1])
    with col_av_m:
        st.image(avatar_bild, use_container_width=True)

    level = level_aus_xp(user_row["xp_gesamt"])
    xp_im_level, xp_fuer_naechstes = xp_bis_naechstes_level(user_row["xp_gesamt"])
    st.markdown(
        profil_karte_html(name, level, xp_im_level, xp_fuer_naechstes),
        unsafe_allow_html=True,
    )

    st.divider()
    conn_sidebar = get_connection()
    liste_id_sidebar = get_or_create_active_liste(conn_sidebar, user_row["id"])
    anzahl_artikel = len(get_artikel(conn_sidebar, liste_id_sidebar))
    conn_sidebar.close()
    seite = st.radio(
        "Navigation",
        ["✨ Tagesvorschlag", "🍽️ Menüs", "🗓️ Wochenplanung", "📖 Rezept-Bibliothek", "🛒 Warenkorb",
         "🏆 Errungenschaften", "••• Mehr"],
        label_visibility="collapsed",
        key="haupt_navigation",
    )
    if anzahl_artikel:
        st.caption(f"🛒 {anzahl_artikel} Artikel im Warenkorb")
    st.divider()
    authenticator.logout(location="sidebar")


# ---------------------------------------------------------------
# Seite: Tagesvorschlag
# ---------------------------------------------------------------
def zeige_zufallsvorschlag(gang: str, key_prefix: str, mahlzeit: str = None, kategorien: set = None):
    """Zeigt 3 zufaellige Rezepte eines bestimmten Gangs (optional zusaetzlich nach
    Mahlzeit und/oder einer Menge erlaubter Kategorien gefiltert) mit 'neu mischen'-
    Button. key_prefix muss je Kontext eindeutig sein, da mehrere Vorschlags-Bereiche
    gleichzeitig gerendert werden koennen (z.B. innerhalb der 'Mehr'-Tabs)."""
    conn = get_connection()
    rezepte = get_sichtbare_rezepte_gefiltert(conn, user_row["id"], aktive_praeferenzen())
    conn.close()
    rezepte = [r for r in rezepte if r["gang"] == gang]
    if mahlzeit:
        rezepte = [r for r in rezepte if mahlzeit in (r["mahlzeiten"] or "").split(",")]
    if kategorien is not None:
        rezepte = [r for r in rezepte if r["kategorie"] in kategorien]

    if not rezepte:
        st.markdown(
            leerer_zustand_html(
                "Für diese Auswahl sind noch keine Rezepte da - entweder ist die "
                "Bibliothek leer, oder du hast alle versteckt.",
                bild_pfad="assets/illustrations/leer_suche.svg",
            ),
            unsafe_allow_html=True,
        )
        return

    session_key = f"vorschlag_ids_{key_prefix}_{user_row['id']}"
    verfuegbare_ids = {r["id"] for r in rezepte}

    aktuelle_ids = st.session_state.get(session_key)
    if not aktuelle_ids or not set(aktuelle_ids).issubset(verfuegbare_ids):
        anzahl = min(3, len(rezepte))
        st.session_state[session_key] = [r["id"] for r in gewichtete_stichprobe(rezepte, gewichte_nach_kochlevel(rezepte), anzahl)]

    if st.button("🎲 3 neue Vorschläge", key=f"reroll_{key_prefix}"):
        anzahl = min(3, len(rezepte))
        st.session_state[session_key] = [r["id"] for r in gewichtete_stichprobe(rezepte, gewichte_nach_kochlevel(rezepte), anzahl)]
        st.rerun()

    rezepte_by_id = {r["id"]: r for r in rezepte}
    vorschlaege = [rezepte_by_id[rid] for rid in st.session_state[session_key] if rid in rezepte_by_id]

    spalten = st.columns(len(vorschlaege))
    for col, rezept in zip(spalten, vorschlaege):
        with col:
            with st.container(border=True):
                st.markdown('<div class="karten-marker"></div>', unsafe_allow_html=True)
                st.markdown(akzent_balken_html(akzent_farbe_fuer_protein(rezept["protein_typ"])), unsafe_allow_html=True)
                bild_html = rundes_bild_html(rezept["bild_url"], groesse=160)
                if bild_html:
                    st.markdown(bild_html, unsafe_allow_html=True)
                st.markdown(f"**{rezept['name']}**")
                st.markdown(schwierigkeit_badge_html(rezept["schwierigkeit"]), unsafe_allow_html=True)
                st.caption(f"{rezept['protein_typ']} · {rezept['kalorien_pro_portion']} kcal/Portion")
                with st.expander("Details ansehen"):
                    zeige_rezept_details(rezept, key_suffix=f"_{key_prefix}")


FRUEHSTUECKSART_ICONS = {
    "Herzhaftes Frühstück": "assets/flaticon/fruehstueck_herzhaft.png",
    "Süßes Frühstück": "assets/flaticon/fruehstueck_suess.png",
}
MAHLZEIT_ICONS = {
    "Frühstück": "assets/flaticon/fruehstueck_herzhaft.png",
    "Mittagessen": "assets/flaticon/mahlzeit_mittag.png",
    "Abendessen": "assets/flaticon/mahlzeit_abend.png",
}
GANG_ICONS = {
    "Vorspeise": "assets/flaticon/salate.png",
    "Hauptgang": "assets/flaticon/pfannengerichte.png",
    "Dessert": "assets/flaticon/desserts.png",
}
ANZEIGE_GANG = {"Vorspeise": "Vorspeise", "Hauptgang": "Hauptspeise", "Dessert": "Nachspeise"}


def zeige_icon_buttons(optionen: dict, session_key: str, anzeige: dict = None, standard: str = None, icon_groesse: int = 60):
    """Zeigt eine Reihe farbiger Icon-Buttons (wie im Sidepanel) und gibt die
    aktuell gewählte Option zurück. optionen: {wert: icon_pfad}."""
    if session_key not in st.session_state:
        st.session_state[session_key] = standard or list(optionen.keys())[0]

    spalten = st.columns(len(optionen))
    for col, (wert, icon_pfad) in zip(spalten, optionen.items()):
        with col:
            if icon_pfad:
                st.markdown(rundes_bild_html(icon_pfad, groesse=icon_groesse), unsafe_allow_html=True)
            else:
                # Kein Icon fuer diese Option (z.B. "Alle") - Platzhalter in gleicher
                # Hoehe, damit der Button trotzdem buendig mit den anderen abschliesst
                st.markdown(f'<div style="height:{icon_groesse + 6}px;"></div>', unsafe_allow_html=True)
            aktiv = st.session_state[session_key] == wert
            label = anzeige[wert] if anzeige else wert
            if st.button(
                label, key=f"{session_key}_btn_{wert}", use_container_width=True,
                type="primary" if aktiv else "secondary",
            ):
                st.session_state[session_key] = wert
                st.rerun()

    return st.session_state[session_key]


def zeige_multi_icon_buttons(optionen: dict, session_key: str, anzeige: dict = None, icon_groesse: int = 60):
    """Zeigt eine Reihe farbiger Icon-Buttons zur Mehrfachauswahl - standardmäßig
    sind ALLE aktiv, ein Klick schaltet die jeweilige Option einzeln ab/an.
    Erspart einen separaten 'Alle'-Button (und dessen Höhen-Ausrichtungsproblem,
    da jetzt jede Option ein Icon hat). Gibt die Menge der ausgewählten Werte zurück."""
    if session_key not in st.session_state:
        st.session_state[session_key] = set(optionen.keys())

    spalten = st.columns(len(optionen))
    for col, (wert, icon_pfad) in zip(spalten, optionen.items()):
        with col:
            st.markdown(rundes_bild_html(icon_pfad, groesse=icon_groesse), unsafe_allow_html=True)
            aktiv = wert in st.session_state[session_key]
            label = anzeige[wert] if anzeige else wert
            if st.button(
                label, key=f"{session_key}_btn_{wert}", use_container_width=True,
                type="primary" if aktiv else "secondary",
            ):
                if aktiv:
                    st.session_state[session_key].discard(wert)
                else:
                    st.session_state[session_key].add(wert)
                st.rerun()

    return st.session_state[session_key]


def zeige_tagesvorschlag():
    st.title("✨ Tagesvorschlag")
    st.caption("3 zufällige Rezepte aus deiner Bibliothek. Gefällt dir keins? Einfach neu mischen.")

    gewaehlte_mahlzeit = zeige_icon_buttons(
        MAHLZEIT_ICONS, "tagesvorschlag_mahlzeit", standard="Mittagessen", icon_groesse=42,
    )
    st.divider()

    if gewaehlte_mahlzeit == "Frühstück":
        ausgewaehlte_kategorien = zeige_multi_icon_buttons(
            FRUEHSTUECKSART_ICONS, "tagesvorschlag_fruehstuecksart_multi", icon_groesse=42,
        )
        zeige_zufallsvorschlag(
            "Hauptgang", key_prefix=f"tages_fruehstueck_{sorted(ausgewaehlte_kategorien)}",
            mahlzeit="Frühstück", kategorien=ausgewaehlte_kategorien,
        )
    else:
        # Bewusst einfach gehalten: nur Hauptspeisen. Vorspeisen/Desserts und das
        # 3-Gänge-Menü haben ihren eigenen Bereich unter "Mehr", damit der
        # alltägliche Tagesvorschlag nicht mit einer Gang-Auswahl überfrachtet wird.
        zeige_zufallsvorschlag(
            "Hauptgang", key_prefix=f"tages_{gewaehlte_mahlzeit}", mahlzeit=gewaehlte_mahlzeit,
        )
    st.caption(
        "💡 Auf der Suche nach Vorspeisen, Desserts oder einem kompletten "
        "3-Gänge-Menü? Die findest du unter '🍽️ Menüs'."
    )


# ---------------------------------------------------------------
# Seite: Rezept-Bibliothek
# ---------------------------------------------------------------
# ---------------------------------------------------------------
# Formular: Eigenes Rezept von Grund auf neu hinzufügen
# ---------------------------------------------------------------
ICON_AUSWAHL = [
    ("Huhn", "assets/flaticon/haehnchengerichte.png"),
    ("Fisch", "assets/flaticon/fischgerichte.png"),
    ("Rind", "assets/flaticon/rindgerichte.png"),
    ("Schwein", "assets/flaticon/schweinegerichte.png"),
    ("Lamm", "assets/flaticon/lammgerichte.png"),
    ("Gemüse", "assets/flaticon/gemuesegerichte.png"),
    ("Suppe", "assets/flaticon/suppen.png"),
    ("Wok", "assets/flaticon/wokgerichte.png"),
    ("Reis", "assets/flaticon/reisgerichte.png"),
    ("Pasta", "assets/flaticon/pastagerichte.png"),
    ("Salat", "assets/flaticon/salate.png"),
    ("Beilage", "assets/flaticon/beilagen.png"),
    ("Pfanne", "assets/flaticon/pfannengerichte.png"),
    ("Auflauf", "assets/flaticon/auflaeufe.png"),
    ("Curry", "assets/flaticon/currys.png"),
    ("Dumpling", "assets/flaticon/dumplings.png"),
    ("Pizza", "assets/flaticon/pizzagerichte.png"),
    ("Dessert", "assets/flaticon/desserts.png"),
]


def zeige_neues_rezept_formular():
    st.caption("Erstelle ein komplett neues Rezept für deine Bibliothek.")

    name = st.text_input("Rezeptname", key="neu_name")

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        protein_typ = st.selectbox(
            "Protein-Typ", ["Huhn", "Fisch", "Rind", "Schwein", "Lamm", "Vegetarisch"],
            key="neu_protein",
        )
    with col_b:
        schwierigkeit = st.selectbox(
            "Schwierigkeit", ["einfach", "mittel", "aufwaendig"], key="neu_schwierigkeit",
        )
    with col_c:
        kategorie = st.text_input("Kategorie", value="Pfannengericht", key="neu_kategorie")

    gang = st.selectbox(
        "Gang", ["Hauptgang", "Vorspeise", "Dessert"], key="neu_gang",
        help="Bestimmt, wo das Rezept später auftaucht: Hauptgang in Tagesvorschlag/Bibliothek, "
             "Vorspeise/Dessert nur unter 'Mehr'.",
    )
    mahlzeiten_auswahl = st.multiselect(
        "Passende Mahlzeit(en)", ["Frühstück", "Mittagessen", "Abendessen"],
        default=["Mittagessen", "Abendessen"], key="neu_mahlzeiten",
    )

    col_d, col_e, col_f = st.columns(3)
    with col_d:
        zeit = st.number_input("Zubereitungszeit (Min.)", min_value=1, value=30, key="neu_zeit")
    with col_e:
        portionen_basis = st.number_input("Portionen (Basis)", min_value=1, value=2, key="neu_portionen")
    with col_f:
        kalorien = st.number_input("kcal pro Portion", min_value=1, value=400, key="neu_kalorien")

    st.markdown("**Icon auswählen**")
    icon_key = "neu_icon_auswahl"
    if icon_key not in st.session_state:
        st.session_state[icon_key] = ICON_AUSWAHL[0][1]

    icon_spalten = st.columns(6)
    for i, (label, pfad) in enumerate(ICON_AUSWAHL):
        with icon_spalten[i % 6]:
            st.markdown(rundes_bild_html(pfad, groesse=55), unsafe_allow_html=True)
            aktiv = st.session_state[icon_key] == pfad
            if st.button(label, key=f"neu_icon_{i}", use_container_width=True,
                         type="primary" if aktiv else "secondary"):
                st.session_state[icon_key] = pfad
                st.rerun()

    zutaten_text = st.text_area(
        "Zutaten (eine pro Zeile, Format: Name;Menge;Einheit)",
        placeholder="Hühnerbrust;300;g\nZwiebel;1;Stück\nReis;150;g",
        height=120, key="neu_zutaten",
    )
    zubereitung = st.text_area("Zubereitung", height=180, key="neu_zubereitung")

    if st.button("✅ Rezept speichern", type="primary", key="neu_speichern"):
        if not name.strip():
            st.warning("Bitte gib einen Rezeptnamen ein.")
            return

        geparste_zutaten = []
        for zeile in zutaten_text.split("\n"):
            zeile = zeile.strip()
            if not zeile:
                continue
            teile = zeile.split(";")
            if len(teile) >= 2:
                zname = teile[0].strip()
                try:
                    zmenge = float(teile[1].strip())
                except ValueError:
                    zmenge = 0
                zeinheit = teile[2].strip() if len(teile) > 2 else ""
                geparste_zutaten.append((zname, zmenge, zeinheit))

        conn = get_connection()
        erstelle_neues_rezept(
            conn, user_row["id"], name.strip(), protein_typ, schwierigkeit,
            kategorie.strip() or "Sonstiges", zeit, portionen_basis, kalorien,
            st.session_state[icon_key], zubereitung, geparste_zutaten, gang,
            ",".join(mahlzeiten_auswahl) or "Mittagessen,Abendessen",
        )
        conn.close()
        st.success(f"'{name}' wurde gespeichert und erscheint jetzt in deiner Bibliothek!")
        st.session_state[icon_key] = ICON_AUSWAHL[0][1]
        st.rerun()


def zeige_rezept_bibliothek():
    st.title("📖 Rezept-Bibliothek")

    with st.expander("➕ Eigenes Rezept hinzufügen"):
        zeige_neues_rezept_formular()

    conn = get_connection()
    rezepte = get_sichtbare_rezepte_gefiltert(conn, user_row["id"], aktive_praeferenzen())
    conn.close()
    rezepte = [r for r in rezepte if r["gang"] == "Hauptgang"]

    # --- Filter ---
    TIER_ICON_JE_PROTEIN = {
        "Huhn": "assets/flaticon/tier_huhn.png",
        "Fisch": "assets/flaticon/tier_fisch.png",
        "Rind": "assets/flaticon/tier_rind.png",
        "Schwein": "assets/flaticon/tier_schwein.png",
        "Lamm": "assets/flaticon/tier_lamm.png",
        "Vegetarisch": "assets/flaticon/gemuesegerichte.png",
    }

    protein_optionen_liste = sorted({r["protein_typ"] for r in rezepte})
    protein_icons = {p: TIER_ICON_JE_PROTEIN.get(p) for p in protein_optionen_liste}

    with st.container(border=True):
        st.markdown('<div class="karten-marker"></div>', unsafe_allow_html=True)
        st.markdown("### 🔍 Filter")
        st.markdown("**Protein-Typ**")
        ausgewaehlte_proteine = zeige_multi_icon_buttons(protein_icons, "bib_protein_filter_multi", icon_groesse=38)

        col2, col3, col4 = st.columns(3)
        with col2:
            st.markdown("**Schwierigkeit**")
            schwierigkeit_optionen = ["Alle", "einfach", "mittel", "aufwaendig"]
            eigenes_kochlevel = user_row["kochlevel"] or "mittel"
            vorauswahl = "Alle" if eigenes_kochlevel == "alle" else eigenes_kochlevel
            schwierigkeit_filter = st.selectbox(
                "Schwierigkeit", schwierigkeit_optionen,
                index=schwierigkeit_optionen.index(vorauswahl),
                label_visibility="collapsed",
            )
        with col3:
            st.markdown("**Mahlzeit**")
            mahlzeit_optionen = ["Alle", "Frühstück", "Mittagessen", "Abendessen"]
            mahlzeit_filter = st.selectbox("Mahlzeit", mahlzeit_optionen, label_visibility="collapsed")
        with col4:
            st.markdown("**Suche nach Name**")
            suchtext = st.text_input("Suche nach Name", label_visibility="collapsed")

    gefiltert = [
        r for r in rezepte
        if r["protein_typ"] in ausgewaehlte_proteine
        and (schwierigkeit_filter == "Alle" or r["schwierigkeit"] == schwierigkeit_filter)
        and (mahlzeit_filter == "Alle" or mahlzeit_filter in (r["mahlzeiten"] or "").split(","))
        and (suchtext.lower() in r["name"].lower())
    ]

    if not gefiltert:
        st.markdown(
            leerer_zustand_html(
                "Keine Rezepte gefunden, die zu den Filtern passen. Versuch's mit "
                "weniger Filtern oder einem anderen Suchbegriff.",
                bild_pfad="assets/illustrations/leer_suche.svg",
            ),
            unsafe_allow_html=True,
        )
        return

    st.caption(f"{len(gefiltert)} Rezept(e) gefunden")
    zeige_rezept_karten_grid(gefiltert, key_prefix="bib")


def zeige_rezept_karten_grid(rezepte_liste, key_prefix=""):
    """Zeigt eine Liste von Rezepten als 3er-Kachel-Raster mit Details-Expander.
    key_prefix muss je Aufrufkontext eindeutig sein (z.B. bei mehreren
    gleichzeitig gerenderten Tabs), damit Widget-Keys nicht kollidieren."""
    if not rezepte_liste:
        st.markdown(
            leerer_zustand_html("Keine Rezepte gefunden.", bild_pfad="assets/illustrations/leer_suche.svg"),
            unsafe_allow_html=True,
        )
        return

    spalten = st.columns(3)
    for i, rezept in enumerate(rezepte_liste):
        with spalten[i % 3]:
            with st.container(border=True):
                st.markdown('<div class="karten-marker"></div>', unsafe_allow_html=True)
                st.markdown(akzent_balken_html(akzent_farbe_fuer_protein(rezept["protein_typ"])), unsafe_allow_html=True)
                bild_html = rundes_bild_html(rezept["bild_url"], groesse=160)
                if bild_html:
                    st.markdown(bild_html, unsafe_allow_html=True)
                st.markdown(f"**{rezept['name']}**")
                st.markdown(schwierigkeit_badge_html(rezept["schwierigkeit"]), unsafe_allow_html=True)
                st.caption(f"{rezept['protein_typ']} · {rezept['kalorien_pro_portion']} kcal/Portion")
                with st.expander("Details ansehen"):
                    zeige_rezept_details(rezept, key_suffix=f"_{key_prefix}")


def zeige_rezept_details(rezept, key_suffix=""):
    conn = get_connection()
    zutaten = conn.execute(
        "SELECT * FROM zutaten WHERE rezept_id = ?", (rezept["id"],)
    ).fetchall()
    conn.close()

    portionen = st.number_input(
        "Portionen",
        min_value=1,
        max_value=20,
        value=rezept["portionen_basis"],
        key=f"portionen_{rezept['id']}{key_suffix}",
    )
    faktor = portionen / rezept["portionen_basis"]

    st.markdown("**Zutaten:**")
    for z in zutaten:
        menge_skaliert = round(z["menge"] * faktor, 2)
        # ganze Zahlen ohne Nachkommastellen anzeigen
        if menge_skaliert == int(menge_skaliert):
            menge_skaliert = int(menge_skaliert)
        einheit = f" {z['einheit']}" if z["einheit"] else ""
        st.markdown(f"- {menge_skaliert}{einheit} {z['name']}")

    st.markdown("**Zubereitung:**")
    schritte = [s.strip() for s in (rezept["zubereitung"] or "").split("\n") if s.strip()]
    for i, schritt in enumerate(schritte, start=1):
        st.markdown(f"**Schritt {i}.** {schritt}")

    kalorien_gesamt = round(rezept["kalorien_pro_portion"] * portionen)
    st.caption(f"≈ {rezept['kalorien_pro_portion']} kcal pro Portion · {kalorien_gesamt} kcal gesamt für {portionen} Portionen")

    conn = get_connection()
    aktuell_favorit = ist_favorit(conn, user_row["id"], rezept["id"])
    conn.close()
    favorit_label = "❤️ Favorit" if aktuell_favorit else "🤍 Zu Favoriten hinzufügen"
    if st.button(
        favorit_label, key=f"favorit_{rezept['id']}{key_suffix}", use_container_width=True,
        type="primary" if aktuell_favorit else "secondary",
    ):
        conn = get_connection()
        neuer_status = favorit_umschalten(conn, user_row["id"], rezept["id"])
        conn.close()
        if neuer_status:
            st.success(f"{rezept['name']} zu Favoriten hinzugefügt!")
        st.rerun()

    if st.button("🛒 Zum Warenkorb", key=f"warenkorb_{rezept['id']}{key_suffix}", use_container_width=True):
        conn = get_connection()
        add_rezept_zu_warenkorb(conn, user_row["id"], rezept["id"], portionen)
        conn.close()
        st.success(f"{rezept['name']} ({portionen} Portionen) wurde zum Warenkorb hinzugefügt!")
        st.rerun()

    if st.button("✅ Gekocht!", key=f"gekocht_{rezept['id']}{key_suffix}", type="primary", use_container_width=True):
        conn = get_connection()
        xp, neue_achievements = kochen_markieren(conn, user_row["id"], rezept["id"], portionen)
        conn.close()
        st.success(f"Nice, {xp} XP erhalten für {rezept['name']}! 🎉")
        for a in neue_achievements:
            st.balloons()
            st.success(f"🏆 Neue Errungenschaft freigeschaltet: **{a['name']}** – {a['beschreibung']}")
        st.rerun()

    with st.popover("⋮ Mehr", use_container_width=True):
        st.caption(
            "Erstellt eine eigene Kopie dieses Rezepts, die du frei bearbeiten "
            "kannst - das Original bleibt für alle anderen Nutzer unverändert."
        )
        neuer_name = st.text_input(
            "Name deiner Version",
            value=f"{rezept['name']} (eigene Version)",
            key=f"kopie_name_{rezept['id']}{key_suffix}",
        )
        zutaten_text = "\n".join(
            f"{z['name']};{z['menge']};{z['einheit'] or ''}" for z in zutaten
        )
        neue_zutaten_text = st.text_area(
            "Zutaten (eine pro Zeile, Format: Name;Menge;Einheit)",
            value=zutaten_text,
            height=150,
            key=f"kopie_zutaten_{rezept['id']}{key_suffix}",
        )
        neue_zubereitung = st.text_area(
            "Zubereitung",
            value=rezept["zubereitung"] or "",
            height=200,
            key=f"kopie_zubereitung_{rezept['id']}{key_suffix}",
        )
        if st.button("✏️ Eigene Version speichern", key=f"kopie_speichern_{rezept['id']}{key_suffix}"):
            geparste_zutaten = []
            for zeile in neue_zutaten_text.split("\n"):
                zeile = zeile.strip()
                if not zeile:
                    continue
                teile = zeile.split(";")
                if len(teile) >= 2:
                    name_z = teile[0].strip()
                    try:
                        menge_z = float(teile[1].strip())
                    except ValueError:
                        menge_z = 0
                    einheit_z = teile[2].strip() if len(teile) > 2 else ""
                    geparste_zutaten.append((name_z, menge_z, einheit_z))

            conn = get_connection()
            erstelle_eigene_kopie(
                conn, user_row["id"], rezept["id"],
                neuer_name, neue_zubereitung, geparste_zutaten,
            )
            conn.close()
            st.success(f"'{neuer_name}' wurde als eigenes Rezept gespeichert!")
            st.rerun()

        st.divider()

        bestaetigen_key = f"bestaetige_verstecken_{rezept['id']}{key_suffix}"
        if not st.session_state.get(bestaetigen_key, False):
            if st.button("🚫 Nicht mehr anzeigen", key=f"verstecken_{rezept['id']}{key_suffix}"):
                st.session_state[bestaetigen_key] = True
                st.rerun()
        else:
            st.warning(f"'{rezept['name']}' wirklich nicht mehr anzeigen?")
            ja_col, nein_col = st.columns(2)
            with ja_col:
                if st.button("Ja, verstecken", key=f"verstecken_ja_{rezept['id']}{key_suffix}", type="primary"):
                    conn = get_connection()
                    verstecke_rezept(conn, user_row["id"], rezept["id"])
                    conn.close()
                    st.session_state[bestaetigen_key] = False
                    st.info(f"'{rezept['name']}' wird dir ab jetzt nicht mehr vorgeschlagen.")
                    st.rerun()
            with nein_col:
                if st.button("Abbrechen", key=f"verstecken_abbrechen_{rezept['id']}{key_suffix}"):
                    st.session_state[bestaetigen_key] = False
                    st.rerun()


# ---------------------------------------------------------------
# Seite: Wochenplanung
# ---------------------------------------------------------------
def mahlzeit_ueberschrift_html(mahlzeit: str) -> str:
    """Kleine Überschrift mit echtem Icon (statt Emoji) links vom Mahlzeit-Namen."""
    icon_pfad = MAHLZEIT_ICONS.get(mahlzeit)
    bild_teil = ""
    if icon_pfad:
        voller_pfad = APP_DIR / icon_pfad
        endung = voller_pfad.suffix.lower()
        try:
            if endung == ".svg":
                inhalt = voller_pfad.read_text(encoding="utf-8").encode("utf-8")
                mime = "image/svg+xml"
            else:
                inhalt = voller_pfad.read_bytes()
                mime = "image/png"
            b64 = base64.b64encode(inhalt).decode("utf-8")
            bild_teil = (
                f'<img src="data:{mime};base64,{b64}" '
                f'style="width:30px;height:30px;border-radius:50%;object-fit:contain;'
                f'background:#FFFFFF;border:2px solid #F0F0F0;flex-shrink:0;" />'
            )
        except FileNotFoundError:
            pass
    return (
        f'<div style="display:flex;align-items:center;gap:8px;margin:8px 0 6px 0;">'
        f'{bild_teil}<span style="font-family:\'Fraunces\',serif;font-weight:700;font-size:19px;">{mahlzeit}</span></div>'
    )


def zeige_wochenplan_tag_karte(eintrag, tag, mahlzeit, kalenderwoche):
    """Zeigt das fuer diesen Tag/diese Mahlzeit bereits eingeplante Rezept."""
    col_bild, col_info = st.columns([1, 2])
    with col_bild:
        bild_html = rundes_bild_html(eintrag["bild_url"], groesse=90)
        if bild_html:
            st.markdown(bild_html, unsafe_allow_html=True)
    with col_info:
        st.markdown(f"**{eintrag['rezept_name']}**")
        st.markdown(schwierigkeit_badge_html(eintrag["schwierigkeit"]), unsafe_allow_html=True)
        st.caption(
            f"{eintrag['protein_typ']} · {eintrag['portionen']} Portionen · "
            f"{round(eintrag['kalorien_pro_portion'] * eintrag['portionen'])} kcal gesamt"
        )
    conn = get_connection()
    volles_rezept = conn.execute("SELECT * FROM rezepte WHERE id = ?", (eintrag["rezept_id"],)).fetchone()
    conn.close()
    with st.expander("Details ansehen"):
        zeige_rezept_details(volles_rezept, key_suffix=f"_wpplanned_{tag}_{mahlzeit}")

    col_gekocht, col_entfernen = st.columns(2)
    with col_gekocht:
        if st.button("✅ Gekocht!", key=f"wp_gekocht_{tag}_{mahlzeit}", type="primary", use_container_width=True):
            conn = get_connection()
            xp, neue_achievements = kochen_markieren(conn, user_row["id"], eintrag["rezept_id"], eintrag["portionen"])
            conn.close()
            st.success(f"Nice, {xp} XP erhalten für {eintrag['rezept_name']}! 🎉")
            for a in neue_achievements:
                st.balloons()
                st.success(f"🏆 Neue Errungenschaft: **{a['name']}** – {a['beschreibung']}")
            st.rerun()
    with col_entfernen:
        if st.button("🗑️ Entfernen", key=f"entfernen_{tag}_{mahlzeit}", use_container_width=True):
            conn = get_connection()
            entferne_tag(conn, user_row["id"], kalenderwoche, tag, mahlzeit)
            conn.close()
            st.rerun()


def zeige_wochenplan_slot_auswahl(rezepte_liste, tag, mahlzeit, kalenderwoche):
    """Zeigt fuer einen noch leeren Tag/Mahlzeit-Slot 3 Zufallsvorschlaege mit
    'neu mischen', plus die Option, stattdessen die komplette Liste zu durchstoebern."""
    if not rezepte_liste:
        st.caption("Keine passenden Rezepte für diese Mahlzeit gefunden.")
        return

    auswahl_key = f"tagesauswahl_{tag}_{mahlzeit}"
    ausgewaehlte_id = st.session_state.get(auswahl_key)

    if ausgewaehlte_id is not None:
        gewaehltes_rezept = next((r for r in rezepte_liste if r["id"] == ausgewaehlte_id), None)
        if gewaehltes_rezept is None:
            st.session_state[auswahl_key] = None
            st.rerun()

        col_bild, col_info = st.columns([1, 2])
        with col_bild:
            bild_html = rundes_bild_html(gewaehltes_rezept["bild_url"], groesse=90)
            if bild_html:
                st.markdown(bild_html, unsafe_allow_html=True)
        with col_info:
            st.markdown(f"**{gewaehltes_rezept['name']}**")
            st.markdown(schwierigkeit_badge_html(gewaehltes_rezept["schwierigkeit"]), unsafe_allow_html=True)
            st.caption(gewaehltes_rezept["protein_typ"])

        with st.expander("Details ansehen"):
            zeige_rezept_details(gewaehltes_rezept, key_suffix=f"_wpconfirm_{tag}_{mahlzeit}")

        portionen = st.number_input(
            "Portionen", min_value=1, max_value=20,
            value=gewaehltes_rezept["portionen_basis"], key=f"portionen_plan_{tag}_{mahlzeit}",
        )
        col_ok, col_zurueck = st.columns(2)
        with col_ok:
            if st.button("✅ Einplanen", key=f"einplanen_{tag}_{mahlzeit}", type="primary", use_container_width=True):
                conn = get_connection()
                setze_tag(conn, user_row["id"], kalenderwoche, tag, gewaehltes_rezept["id"], portionen, mahlzeit)
                conn.close()
                st.session_state[auswahl_key] = None
                st.rerun()
        with col_zurueck:
            if st.button("↺ Andere Wahl", key=f"andere_wahl_{tag}_{mahlzeit}", use_container_width=True):
                st.session_state[auswahl_key] = None
                st.rerun()
        return

    alle_key = f"wp_alle_{tag}_{mahlzeit}"
    if alle_key not in st.session_state:
        st.session_state[alle_key] = False

    if st.session_state[alle_key]:
        anzuzeigen = rezepte_liste
        if st.button("🔽 Nur 3 Vorschläge zeigen", key=f"weniger_{tag}_{mahlzeit}"):
            st.session_state[alle_key] = False
            st.rerun()
    else:
        vorschlag_key = f"wp_vorschlag_{tag}_{mahlzeit}"
        verfuegbare_ids = {r["id"] for r in rezepte_liste}
        if vorschlag_key not in st.session_state or not set(st.session_state[vorschlag_key]).issubset(verfuegbare_ids):
            anzahl = min(3, len(rezepte_liste))
            st.session_state[vorschlag_key] = [r["id"] for r in gewichtete_stichprobe(rezepte_liste, gewichte_nach_kochlevel(rezepte_liste), anzahl)]

        col_reroll, col_alle = st.columns(2)
        with col_reroll:
            if st.button("🔄 Andere Vorschläge", key=f"reroll_{tag}_{mahlzeit}", use_container_width=True):
                anzahl = min(3, len(rezepte_liste))
                st.session_state[vorschlag_key] = [r["id"] for r in gewichtete_stichprobe(rezepte_liste, gewichte_nach_kochlevel(rezepte_liste), anzahl)]
                st.rerun()
        with col_alle:
            if st.button("📖 Alle anzeigen", key=f"allebtn_{tag}_{mahlzeit}", use_container_width=True):
                st.session_state[alle_key] = True
                st.rerun()

        rezepte_by_id = {r["id"]: r for r in rezepte_liste}
        anzuzeigen = [rezepte_by_id[rid] for rid in st.session_state[vorschlag_key] if rid in rezepte_by_id]

    spalten = st.columns(3)
    for i, r in enumerate(anzuzeigen):
        with spalten[i % 3]:
            with st.container(border=True):
                st.markdown('<div class="karten-marker"></div>', unsafe_allow_html=True)
                st.markdown(akzent_balken_html(akzent_farbe_fuer_protein(r["protein_typ"])), unsafe_allow_html=True)
                bild_html = rundes_bild_html(r["bild_url"], groesse=90)
                if bild_html:
                    st.markdown(bild_html, unsafe_allow_html=True)
                st.markdown(f"**{r['name']}**")
                st.markdown(schwierigkeit_badge_html(r["schwierigkeit"]), unsafe_allow_html=True)
                st.caption(r["protein_typ"])
                with st.expander("Details ansehen"):
                    zeige_rezept_details(r, key_suffix=f"_wptile_{tag}_{mahlzeit}")
                if st.button("Auswählen", key=f"waehlen_{tag}_{mahlzeit}_{r['id']}", use_container_width=True):
                    st.session_state[auswahl_key] = r["id"]
                    st.rerun()


def zeige_wochenplanung():
    st.title("🗓️ Wochenplanung")

    kalenderwoche = aktuelle_kalenderwoche()
    st.caption(f"Kalenderwoche {kalenderwoche} · Einkaufszettel wird erst am Ende für die ganze Woche generiert")

    conn = get_connection()
    alle_rezepte = get_sichtbare_rezepte_gefiltert(conn, user_row["id"], aktive_praeferenzen())
    plan = get_wochenplan(conn, user_row["id"], kalenderwoche)
    conn.close()
    alle_rezepte = [r for r in alle_rezepte if r["gang"] == "Hauptgang"]

    rezepte_je_mahlzeit = {
        m: [r for r in alle_rezepte if m in (r["mahlzeiten"] or "").split(",")]
        for m in MAHLZEITEN_TAG
    }

    ausgewaehlter_tag = st.radio(
        "Wochentag", WOCHENTAGE, horizontal=True, key="wochenplan_tag", label_visibility="collapsed",
    )
    st.divider()

    tag = ausgewaehlter_tag
    for i, mahlzeit in enumerate(MAHLZEITEN_TAG):
        st.markdown(mahlzeit_ueberschrift_html(mahlzeit), unsafe_allow_html=True)
        eintrag = plan.get((tag, mahlzeit))
        if eintrag:
            zeige_wochenplan_tag_karte(eintrag, tag, mahlzeit, kalenderwoche)
        else:
            zeige_wochenplan_slot_auswahl(rezepte_je_mahlzeit[mahlzeit], tag, mahlzeit, kalenderwoche)
        if i < len(MAHLZEITEN_TAG) - 1:
            st.divider()

    st.divider()

    geplante_slots = list(plan.keys())
    wochen_kcal = sum(round(plan[s]["kalorien_pro_portion"] * plan[s]["portionen"]) for s in geplante_slots)

    col_sum, col_btn = st.columns([2, 1])
    with col_sum:
        st.metric("Geplante Mahlzeiten", f"{len(geplante_slots)} / 21")
        st.metric("Kalorien diese Woche gesamt", f"{wochen_kcal} kcal")
    with col_btn:
        st.write("")
        if st.button("🛒 Einkaufszettel für die Woche generieren", type="primary", disabled=not geplante_slots):
            conn = get_connection()
            for s in geplante_slots:
                eintrag = plan[s]
                add_rezept_zu_warenkorb(conn, user_row["id"], eintrag["rezept_id"], eintrag["portionen"])
            conn.close()
            st.success(
                f"Einkaufszettel für {len(geplante_slots)} Mahlzeit(en) wurde erstellt! "
                "Schau im Warenkorb vorbei - gleiche Zutaten wurden automatisch zusammengezählt."
            )


# ---------------------------------------------------------------
# Seite: Warenkorb / Einkaufsliste
# ---------------------------------------------------------------
def zeige_warenkorb():
    st.title("🛒 Warenkorb")

    conn = get_connection()
    liste_id = get_or_create_active_liste(conn, user_row["id"])
    artikel = get_artikel(conn, liste_id)
    conn.close()

    if not artikel:
        st.markdown(
            leerer_zustand_html(
                "Dein Warenkorb ist noch leer. Geh in die Rezept-Bibliothek, wähle "
                "ein Rezept aus und füge es mit dem Button hinzu.",
                emoji="🛒",
            ),
            unsafe_allow_html=True,
        )
        return

    anzahl_abgehakt = sum(1 for a in artikel if a["abgehakt"])
    st.caption(f"{anzahl_abgehakt} von {len(artikel)} Artikeln abgehakt")

    # Bei diesen Einheiten ist die genaue Menge beim Einkaufen nicht relevant
    # (man kauft keine "3 EL Olivenöl", sondern einfach eine Flasche Olivenöl)
    EINHEITEN_OHNE_MENGENANZEIGE = {"EL", "TL", "Prise"}

    for a in artikel:
        menge = a["menge"]
        if menge == int(menge):
            menge = int(menge)
        einheit = a["einheit"] or ""

        if einheit in EINHEITEN_OHNE_MENGENANZEIGE:
            text = a["name"]
        else:
            einheit_text = f" {einheit}" if einheit else ""
            text = f"{menge}{einheit_text} {a['name']}"

        farbe = "#D9F2D9" if a["abgehakt"] else "#F5F5F5"
        text_stil = (
            "text-decoration: line-through; color: #6B6B6B;"
            if a["abgehakt"]
            else "color: #1A1A1A;"
        )

        col_text, col_btn = st.columns([6, 1])
        with col_text:
            st.markdown(
                f'<div style="background-color:{farbe}; padding:10px 14px; '
                f'border-radius:8px; margin-bottom:6px; {text_stil}">{text}</div>',
                unsafe_allow_html=True,
            )
        with col_btn:
            symbol = "↺" if a["abgehakt"] else "✓"
            if st.button(symbol, key=f"toggle_{a['id']}"):
                conn = get_connection()
                toggle_abgehakt(conn, a["id"])
                conn.close()
                st.rerun()

    st.divider()
    col_erledigt, col_leeren = st.columns(2)
    with col_erledigt:
        if st.button("✅ Einkauf erledigt", type="primary", use_container_width=True):
            conn = get_connection()
            einkauf_abschliessen(conn, liste_id)
            conn.close()
            st.success("Einkauf abgeschlossen! Ein neuer Warenkorb wird beim nächsten Hinzufügen angelegt.")
            st.rerun()

    with col_leeren:
        leeren_key = "bestaetige_warenkorb_leeren"
        if not st.session_state.get(leeren_key, False):
            if st.button("🗑️ Warenkorb leeren", use_container_width=True):
                st.session_state[leeren_key] = True
                st.rerun()
        else:
            st.warning("Wirklich alle Artikel aus dem Warenkorb entfernen?")
            ja_col, nein_col = st.columns(2)
            with ja_col:
                if st.button("Ja, leeren", type="primary", key="leeren_ja"):
                    conn = get_connection()
                    warenkorb_leeren(conn, liste_id)
                    conn.close()
                    st.session_state[leeren_key] = False
                    st.success("Warenkorb wurde geleert.")
                    st.rerun()
            with nein_col:
                if st.button("Abbrechen", key="leeren_abbrechen"):
                    st.session_state[leeren_key] = False
                    st.rerun()


# ---------------------------------------------------------------
# Seite: Kochlexikon
# ---------------------------------------------------------------
def zeige_kochlexikon():
    st.title("📚 Kochlexikon")
    st.caption("Kochfachbegriffe und Zubereitungsarten zum Nachschlagen und Einlesen.")

    col1, col2 = st.columns(2)
    with col1:
        kategorie_filter = st.selectbox("Kategorie", ["Alle"] + KATEGORIEN)
    with col2:
        suchtext = st.text_input("Suche nach Begriff")

    gefiltert = [
        b for b in BEGRIFFE
        if (kategorie_filter == "Alle" or b["kategorie"] == kategorie_filter)
        and (suchtext.lower() in b["name"].lower())
    ]

    if not gefiltert:
        st.markdown(
            leerer_zustand_html(
                "Kein Begriff gefunden, der zu den Filtern passt.",
                bild_pfad="assets/illustrations/leer_suche.svg",
            ),
            unsafe_allow_html=True,
        )
        return

    st.caption(f"{len(gefiltert)} Begriff(e)")

    spalten = st.columns(3)
    for i, begriff in enumerate(gefiltert):
        with spalten[i % 3]:
            with st.container(border=True):
                st.markdown('<div class="karten-marker"></div>', unsafe_allow_html=True)
                st.markdown(akzent_balken_html(akzent_farbe_fuer_kategorie(begriff["kategorie"])), unsafe_allow_html=True)
                bild_html = rundes_bild_html(begriff["bild"], groesse=140)
                if bild_html:
                    st.markdown(bild_html, unsafe_allow_html=True)
                st.markdown(f"**{begriff['name']}**")
                st.caption(begriff["kategorie"])
                with st.expander("Erklärung"):
                    st.markdown(begriff["erklaerung"])


# ---------------------------------------------------------------
# Seite: Versteckte Rezepte
# ---------------------------------------------------------------
def zeige_favoriten():
    st.title("❤️ Favoriten")
    st.caption("Deine Lieblingsrezepte auf einen Blick.")

    conn = get_connection()
    favoriten = get_favoriten(conn, user_row["id"])
    conn.close()

    if not favoriten:
        st.markdown(
            leerer_zustand_html(
                "Noch keine Favoriten. Öffne ein Rezept und klick auf "
                "'🤍 Zu Favoriten hinzufügen', um es hier zu sammeln.",
                emoji="❤️",
            ),
            unsafe_allow_html=True,
        )
        return

    st.caption(f"{len(favoriten)} Favorit(en)")
    zeige_rezept_karten_grid(favoriten, key_prefix="favoriten")


def zeige_versteckte_rezepte():
    st.title("🙈 Versteckte Rezepte")
    st.caption("Rezepte, die du dir nicht mehr vorschlagen lässt. Hier kannst du sie wiederherstellen.")

    conn = get_connection()
    versteckt = get_versteckte_rezepte(conn, user_row["id"])
    conn.close()

    if not versteckt:
        st.markdown(
            leerer_zustand_html("Du hast aktuell keine Rezepte versteckt.", emoji="🙈"),
            unsafe_allow_html=True,
        )
        return

    st.caption(f"{len(versteckt)} versteckte(s) Rezept(e)")

    spalten = st.columns(3)
    for i, rezept in enumerate(versteckt):
        with spalten[i % 3]:
            with st.container(border=True):
                st.markdown('<div class="karten-marker"></div>', unsafe_allow_html=True)
                st.markdown(akzent_balken_html(akzent_farbe_fuer_protein(rezept["protein_typ"])), unsafe_allow_html=True)
                bild_html = rundes_bild_html(rezept["bild_url"], groesse=140)
                if bild_html:
                    st.markdown(bild_html, unsafe_allow_html=True)
                st.markdown(f"**{rezept['name']}**")
                st.markdown(schwierigkeit_badge_html(rezept["schwierigkeit"]), unsafe_allow_html=True)
                st.caption(f"{rezept['protein_typ']} · {rezept['kalorien_pro_portion']} kcal/Portion")
                if st.button("↩️ Wieder anzeigen", key=f"wiederzeigen_{rezept['id']}"):
                    conn = get_connection()
                    zeige_rezept_wieder(conn, user_row["id"], rezept["id"])
                    conn.close()
                    st.success(f"'{rezept['name']}' wird dir wieder vorgeschlagen!")
                    st.rerun()


# ---------------------------------------------------------------
# Seite: Einstellungen
# ---------------------------------------------------------------
def zeige_einstellungen():
    st.title("⚙️ Einstellungen")
    st.caption("Persönliche Anpassungen - nur für dich, andere Nutzer sehen ihre eigene Einstellung.")

    st.markdown("### Hintergrundfarbe der App")

    FARBOPTIONEN = {
        "Standard": None,
        "Warmes Beige": "#FBF3E7",
        "Sanftes Blau": "#EAF3FA",
        "Sanftes Grün": "#EFF7EC",
        "Sanftes Rosa": "#FBEFEF",
        "Dezentes Grau": "#F1F1F1",
    }

    aktuelle_farbe = user_row["hintergrundfarbe"]
    namen = list(FARBOPTIONEN.keys())
    aktueller_name = next((n for n, f in FARBOPTIONEN.items() if f == aktuelle_farbe), namen[0])

    ausgewaehlt = st.radio(
        "Farbe wählen",
        namen,
        index=namen.index(aktueller_name),
        label_visibility="collapsed",
    )

    if st.button("💾 Speichern", type="primary"):
        conn = get_connection()
        conn.execute(
            "UPDATE users SET hintergrundfarbe = ? WHERE id = ?",
            (FARBOPTIONEN[ausgewaehlt], user_row["id"]),
        )
        conn.commit()
        conn.close()
        st.success("Hintergrundfarbe gespeichert!")
        st.rerun()

    st.caption("Weitere Anpassungsmöglichkeiten (z. B. Akzentfarbe, Schriftgröße) können wir jederzeit ergänzen.")

    st.divider()
    st.markdown("### Ernährungspräferenzen")
    st.caption(
        "Rezepte werden in Tagesvorschlag, Bibliothek und Wochenplanung anhand der "
        "Zutaten gefiltert. Das ist eine einfache Stichwort-basierte Orientierungshilfe, "
        "**keine medizinische Beratung** - bei Unverträglichkeiten bitte zusätzlich "
        "immer selbst die Zutatenliste prüfen."
    )

    aktuelle_codes = aktive_praeferenzen()
    ausgewaehlte_namen = st.multiselect(
        "Präferenzen auswählen",
        options=list(PRAEFERENZEN.values()),
        default=[PRAEFERENZEN[c] for c in aktuelle_codes if c in PRAEFERENZEN],
        label_visibility="collapsed",
    )

    if st.button("💾 Präferenzen speichern", type="primary"):
        name_zu_code = {v: k for k, v in PRAEFERENZEN.items()}
        neue_codes = [name_zu_code[n] for n in ausgewaehlte_namen]
        conn = get_connection()
        conn.execute(
            "UPDATE users SET ernaehrungspraeferenzen = ? WHERE id = ?",
            (",".join(neue_codes), user_row["id"]),
        )
        conn.commit()
        conn.close()
        st.success("Ernährungspräferenzen gespeichert!")
        st.rerun()

    st.divider()
    st.markdown("### Kochlevel")
    st.caption(
        "Bei Zufallsvorschlägen (Tagesvorschlag, Wochenplanung) werden Rezepte "
        "deines Kochlevels bevorzugt gezeigt - andere Schwierigkeitsgrade tauchen "
        "trotzdem gelegentlich auf, damit du nicht in einer Blase feststeckst. "
        "Der Schwierigkeits-Filter in der Bibliothek startet außerdem automatisch "
        "auf deinem Kochlevel."
    )

    kochlevel_optionen = ["alle", "einfach", "mittel", "aufwaendig"]
    kochlevel_anzeige = {
        "alle": "🎲 Alle (keine Präferenz)",
        "einfach": "🌱 Anfänger",
        "mittel": "👨‍🍳 Fortgeschritten",
        "aufwaendig": "🔥 Erfahren",
    }
    aktuelles_kochlevel = user_row["kochlevel"] or "mittel"

    neues_kochlevel = st.radio(
        "Kochlevel", kochlevel_optionen,
        index=kochlevel_optionen.index(aktuelles_kochlevel),
        format_func=lambda k: kochlevel_anzeige[k],
        horizontal=True, label_visibility="collapsed",
    )
    if neues_kochlevel != aktuelles_kochlevel:
        conn = get_connection()
        conn.execute("UPDATE users SET kochlevel = ? WHERE id = ?", (neues_kochlevel, user_row["id"]))
        conn.commit()
        conn.close()
        st.success("Kochlevel gespeichert!")
        st.rerun()

    st.divider()
    st.markdown("### Profilbild")
    st.caption("Stell dir deinen eigenen Koch-Avatar zusammen.")

    col_auswahl, col_vorschau = st.columns([3, 2])
    with col_auswahl:
        basis_optionen = ["mann", "frau"]
        basis_anzeige = {"mann": "👨 Koch", "frau": "👩 Köchin"}
        aktuelle_basis = user_row["avatar_basis"] or "mann"
        neue_basis = st.radio(
            "Basis", basis_optionen, index=basis_optionen.index(aktuelle_basis),
            format_func=lambda b: basis_anzeige[b], horizontal=True,
        )

        aktuelle_kopfbedeckung = user_row["avatar_kopfbedeckung"] or "kochmuetze"
        neue_kopfbedeckung = st.selectbox(
            "Kopfbedeckung", list(KOPFBEDECKUNG_OPTIONEN.keys()),
            index=list(KOPFBEDECKUNG_OPTIONEN.keys()).index(aktuelle_kopfbedeckung),
            format_func=lambda k: KOPFBEDECKUNG_ANZEIGE[k],
        )

        aktuelles_gesicht = user_row["avatar_gesicht"] or "keins"
        neues_gesicht = st.selectbox(
            "Gesicht", list(GESICHT_OPTIONEN.keys()),
            index=list(GESICHT_OPTIONEN.keys()).index(aktuelles_gesicht),
            format_func=lambda g: GESICHT_ANZEIGE[g],
        )

        aktueller_hals = user_row["avatar_hals"] or "keins"
        neuer_hals = st.selectbox(
            "Hals", list(HALS_OPTIONEN.keys()),
            index=list(HALS_OPTIONEN.keys()).index(aktueller_hals),
            format_func=lambda h: HALS_ANZEIGE[h],
        )

        aktuelles_extra = user_row["avatar_extra"] or "keins"
        neues_extra = st.selectbox(
            "Abzeichen", list(EXTRA_OPTIONEN.keys()),
            index=list(EXTRA_OPTIONEN.keys()).index(aktuelles_extra),
            format_func=lambda e: EXTRA_ANZEIGE[e],
        )

        if st.button("💾 Profilbild speichern", type="primary"):
            conn = get_connection()
            conn.execute(
                "UPDATE users SET avatar_basis = ?, avatar_kopfbedeckung = ?, avatar_gesicht = ?, avatar_hals = ?, avatar_extra = ? WHERE id = ?",
                (neue_basis, neue_kopfbedeckung, neues_gesicht, neuer_hals, neues_extra, user_row["id"]),
            )
            conn.commit()
            conn.close()
            st.success("Profilbild gespeichert!")
            st.rerun()

    with col_vorschau:
        vorschau = erstelle_avatar(neue_basis, neue_kopfbedeckung, neues_gesicht, neues_extra, neuer_hals)
        st.image(vorschau, use_container_width=True)


# ---------------------------------------------------------------
# Seite: Errungenschaften
# ---------------------------------------------------------------
def zeige_errungenschaften():
    st.title("🏆 Errungenschaften")

    conn = get_connection()
    gruppen = get_achievements_gruppiert(conn, user_row["id"])
    historie = get_kochprotokoll_historie(conn, user_row["id"], limit=10)
    conn.close()

    gesamt = sum(len(items) for _, items in gruppen)
    frei = sum(1 for _, items in gruppen for a in items if a["freigeschaltet"])
    st.caption(f"{frei} von {gesamt} freigeschaltet")

    for kategorie_name, items in gruppen:
        st.markdown(f"### {kategorie_name}")
        spalten = st.columns(3)
        for i, a in enumerate(items):
            with spalten[i % 3]:
                if a["freigeschaltet"]:
                    st.markdown(
                        '<div class="errungenschaft-kachel" style="background-color:#FFF7DA;'
                        'border:2px solid #F2C879;border-radius:16px;padding:14px;margin-bottom:10px;'
                        'box-shadow:0 2px 10px rgba(43,40,35,0.07);">'
                        '<div style="font-size:28px;">🏆</div>'
                        f'<b>{a["name"]}</b><br/>'
                        f'<span style="color:#6B6B6B;font-size:13px;">{a["beschreibung"]}</span>'
                        '</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    fortschritt_html = ""
                    if a["fortschritt"]:
                        aktuell, ziel = a["fortschritt"]
                        prozent = round(100 * aktuell / ziel) if ziel else 0
                        fortschritt_html = (
                            f'<div style="margin-top:8px;">'
                            f'<div style="background:#E5E1D8;border-radius:5px;height:6px;overflow:hidden;">'
                            f'<div style="background:#B0AFA8;width:{prozent}%;height:100%;"></div></div>'
                            f'<span style="color:#9A9A9A;font-size:11px;">{aktuell}/{ziel}</span></div>'
                        )
                    st.markdown(
                        '<div class="errungenschaft-kachel" style="background-color:#F5F5F5;'
                        'border:2px solid #E0E0E0;border-radius:16px;padding:14px;margin-bottom:10px;'
                        'box-shadow:0 2px 10px rgba(43,40,35,0.05);">'
                        '<div style="font-size:28px;opacity:0.4;">🔒</div>'
                        f'<b style="color:#9A9A9A;">{a["name"]}</b><br/>'
                        f'<span style="color:#B0B0B0;font-size:13px;">{a["beschreibung"]}</span>'
                        f'{fortschritt_html}'
                        '</div>',
                        unsafe_allow_html=True,
                    )

    st.divider()
    st.markdown("### Letzte Kochsessions")
    if not historie:
        st.markdown(
            leerer_zustand_html(
                "Noch keine Rezepte als gekocht markiert. Öffne ein Rezept und "
                "klick auf '✅ Als gekocht markieren', um deine ersten Errungenschaften freizuschalten.",
                emoji="🍳",
            ),
            unsafe_allow_html=True,
        )
        return

    for h in historie:
        col_bild, col_info = st.columns([1, 5])
        with col_bild:
            bild_html = rundes_bild_html(h["bild_url"], groesse=50)
            if bild_html:
                st.markdown(bild_html, unsafe_allow_html=True)
        with col_info:
            st.markdown(
                f"**{h['rezept_name']}** · {h['portionen_gekocht']} Portionen · "
                f"+{h['xp_erhalten']} XP · {h['datum']}"
            )


# ---------------------------------------------------------------
# Seite: Mehr (buendelt Kochlexikon, Versteckte Rezepte, Einstellungen)
# ---------------------------------------------------------------
def zeige_vorspeisen():
    st.title("🥗 Vorspeisen")
    st.caption("Kleine Gerichte für den Auftakt eines Menüs. Zufällige Tagesvorschläge findest du oben unter '✨ Tagesvorschlag'.")
    conn = get_connection()
    rezepte = get_sichtbare_rezepte_gefiltert(conn, user_row["id"], aktive_praeferenzen())
    conn.close()
    vorspeisen = [r for r in rezepte if r["gang"] == "Vorspeise"]
    st.caption(f"{len(vorspeisen)} Vorspeise(n) gefunden")
    zeige_rezept_karten_grid(vorspeisen, key_prefix="vorspeise")


def zeige_desserts():
    st.title("🍰 Desserts")
    st.caption("Süßer Abschluss für dein Menü. Zufällige Tagesvorschläge findest du oben unter '✨ Tagesvorschlag'.")
    conn = get_connection()
    rezepte = get_sichtbare_rezepte_gefiltert(conn, user_row["id"], aktive_praeferenzen())
    conn.close()
    desserts = [r for r in rezepte if r["gang"] == "Dessert"]
    st.caption(f"{len(desserts)} Dessert(s) gefunden")
    zeige_rezept_karten_grid(desserts, key_prefix="dessert")


def schlage_menue_vor(gaenge: dict, fixiert: dict = None) -> dict:
    """Waehlt eine stimmige 3-Gaenge-Kombination: bevorzugt unterschiedliche
    Proteinarten zwischen Vorspeise und Hauptgang, und peilt eine ausgewogene
    Gesamtkalorienzahl an (ueber mehrere Zufallsversuche das beste Ergebnis).
    Gaenge, die im 'fixiert'-Dict stehen, werden unveraendert uebernommen -
    nur die restlichen werden neu ausgewuerfelt."""
    import random as _random

    fixiert = fixiert or {}
    beste_kombi = None
    beste_abweichung = None
    ZIEL_KCAL = 1000
    beide_gaenge_fixiert = "Vorspeise" in fixiert and "Hauptgang" in fixiert

    for _ in range(8):
        kombi = dict(fixiert)
        for gang_name, gang_rezepte in gaenge.items():
            if gang_name in fixiert:
                continue
            if gang_rezepte:
                kombi[gang_name] = _random.choice(gang_rezepte)
        if len(kombi) < 3:
            return kombi  # nicht genug Auswahl fuer alle Gaenge - erstbestes nehmen

        # Unterschiedliche Proteinart zwischen Vorspeise und Hauptgang bevorzugen
        # (nur relevant, wenn mindestens einer der beiden gerade neu gewuerfelt wurde)
        if (
            not beide_gaenge_fixiert
            and kombi["Vorspeise"]["protein_typ"] == kombi["Hauptgang"]["protein_typ"]
            and len(gaenge["Hauptgang"]) > 1
        ):
            continue

        gesamt_kcal = sum(r["kalorien_pro_portion"] for r in kombi.values())
        abweichung = abs(gesamt_kcal - ZIEL_KCAL)
        if beste_abweichung is None or abweichung < beste_abweichung:
            beste_kombi = kombi
            beste_abweichung = abweichung

    return beste_kombi


def zeige_drei_gaenge_menue():
    st.title("🍽️ 3-Gänge-Menü")
    st.caption("Stell dir aus Vorspeise, Hauptgang und Dessert ein komplettes Menü zusammen.")

    conn = get_connection()
    rezepte = get_sichtbare_rezepte_gefiltert(conn, user_row["id"], aktive_praeferenzen())
    conn.close()

    gaenge = {
        "Vorspeise": [r for r in rezepte if r["gang"] == "Vorspeise"],
        "Hauptgang": [r for r in rezepte if r["gang"] == "Hauptgang"],
        "Dessert": [r for r in rezepte if r["gang"] == "Dessert"],
    }

    fix_keys = {gang_name: f"menue_fix_{gang_name}" for gang_name in gaenge}
    sel_keys = {gang_name: f"menue_{gang_name}" for gang_name in gaenge}

    if st.button("🎲 Passendes Menü vorschlagen", type="primary"):
        fixiert = {}
        for gang_name, gang_rezepte in gaenge.items():
            if st.session_state.get(fix_keys[gang_name]) and st.session_state.get(sel_keys[gang_name]):
                gewaehlter_name = st.session_state[sel_keys[gang_name]]
                treffer = next((r for r in gang_rezepte if r["name"] == gewaehlter_name), None)
                if treffer:
                    fixiert[gang_name] = treffer
        vorschlag = schlage_menue_vor(gaenge, fixiert)
        for gang_name, rezept in vorschlag.items():
            if gang_name not in fixiert:
                st.session_state[sel_keys[gang_name]] = rezept["name"]
        st.rerun()

    ausgewaehlt = {}
    kcal_gesamt = 0

    spalten = st.columns(3)
    for col, (gang_name, gang_rezepte) in zip(spalten, gaenge.items()):
        with col:
            st.markdown(rundes_bild_html(GANG_ICONS.get(gang_name), groesse=44), unsafe_allow_html=True)
            st.markdown(
                f'<div style="text-align:center;font-family:\'Fraunces\',serif;'
                f'font-weight:700;font-size:20px;margin-bottom:8px;">{ANZEIGE_GANG.get(gang_name, gang_name)}</div>',
                unsafe_allow_html=True,
            )
            if not gang_rezepte:
                st.info(f"Noch keine Rezepte für '{gang_name}' verfügbar.")
                continue
            namen = [r["name"] for r in gang_rezepte]
            if sel_keys[gang_name] not in st.session_state or st.session_state[sel_keys[gang_name]] not in namen:
                st.session_state[sel_keys[gang_name]] = random.choice(gang_rezepte)["name"]
            gewaehlter_name = st.session_state[sel_keys[gang_name]]
            st.checkbox("🔒 Fixieren", key=fix_keys[gang_name])
            gewaehltes_rezept = next(r for r in gang_rezepte if r["name"] == gewaehlter_name)
            ausgewaehlt[gang_name] = gewaehltes_rezept

            with st.container(border=True):
                st.markdown('<div class="karten-marker"></div>', unsafe_allow_html=True)
                st.markdown(akzent_balken_html(akzent_farbe_fuer_protein(gewaehltes_rezept["protein_typ"])), unsafe_allow_html=True)
                bild_html = rundes_bild_html(gewaehltes_rezept["bild_url"], groesse=110)
                if bild_html:
                    st.markdown(bild_html, unsafe_allow_html=True)
                st.markdown(f"**{gewaehltes_rezept['name']}**")
                st.markdown(schwierigkeit_badge_html(gewaehltes_rezept["schwierigkeit"]), unsafe_allow_html=True)
                st.caption(
                    f"{gewaehltes_rezept['protein_typ']} · "
                    f"{gewaehltes_rezept['kalorien_pro_portion']} kcal/Portion"
                )
                with st.expander("Details ansehen"):
                    zeige_rezept_details(gewaehltes_rezept, key_suffix=f"_dreigaenge_{gang_name}")
            kcal_gesamt += gewaehltes_rezept["kalorien_pro_portion"]

    st.divider()

    if len(ausgewaehlt) < 3:
        return

    st.metric("Kalorien gesamt (1 Portion je Gang)", f"{kcal_gesamt} kcal")

    col_warenkorb, col_gekocht = st.columns(2)
    with col_warenkorb:
        if st.button("🛒 Ganzes Menü zum Warenkorb hinzufügen", use_container_width=True):
            conn = get_connection()
            for r in ausgewaehlt.values():
                add_rezept_zu_warenkorb(conn, user_row["id"], r["id"], r["portionen_basis"])
            conn.close()
            st.success("Alle drei Gänge wurden zum Warenkorb hinzugefügt!")
            st.rerun()
    with col_gekocht:
        if st.button("✅ Ganzes Menü als gekocht markieren", type="primary", use_container_width=True):
            conn = get_connection()
            gesamt_xp = 0
            neue_achievements = []
            for r in ausgewaehlt.values():
                xp, neu = kochen_markieren(conn, user_row["id"], r["id"], r["portionen_basis"])
                gesamt_xp += xp
                neue_achievements.extend(neu)
            conn.close()
            st.success(f"Menü komplett! {gesamt_xp} XP erhalten. 🎉")
            for a in neue_achievements:
                st.balloons()
                st.success(f"🏆 Neue Errungenschaft: **{a['name']}** – {a['beschreibung']}")
            st.rerun()


def zeige_freunde():
    st.title("👥 Freunde")

    conn = get_connection()
    eingehend = eingehende_anfragen(conn, user_row["id"])
    conn.close()

    if eingehend:
        st.markdown("### 📨 Eingehende Anfragen")
        for anfrage in eingehend:
            col_name, col_annehmen, col_ablehnen = st.columns([3, 1, 1])
            with col_name:
                st.write(anfrage["name"])
            with col_annehmen:
                if st.button("✅ Annehmen", key=f"annehmen_{anfrage['id']}"):
                    conn = get_connection()
                    anfrage_annehmen(conn, user_row["id"], anfrage["id"])
                    conn.close()
                    st.success(f"Du bist jetzt mit {anfrage['name']} befreundet!")
                    st.rerun()
            with col_ablehnen:
                if st.button("❌ Ablehnen", key=f"ablehnen_{anfrage['id']}"):
                    conn = get_connection()
                    anfrage_ablehnen(conn, user_row["id"], anfrage["id"])
                    conn.close()
                    st.rerun()
        st.divider()

    st.markdown("### ➕ Freund hinzufügen")
    suche = st.text_input("Nutzername suchen", key="freund_suche", label_visibility="collapsed",
                           placeholder="Nutzername eingeben...")
    if suche:
        conn = get_connection()
        treffer = nutzer_suchen(conn, suche, user_row["id"])
        conn.close()
        if not treffer:
            st.caption("Kein Nutzer gefunden.")
        for t in treffer:
            col_name, col_btn = st.columns([3, 1])
            with col_name:
                st.write(f"{t['name']} ({t['username']})")
            with col_btn:
                if st.button("Anfrage senden", key=f"anfrage_{t['id']}"):
                    conn = get_connection()
                    erfolg = sende_freundschaftsanfrage(conn, user_row["id"], t["id"])
                    conn.close()
                    if erfolg:
                        st.success("Anfrage gesendet!")
                    else:
                        st.info("Es besteht bereits eine Anfrage oder Freundschaft.")
                    st.rerun()

    st.divider()
    st.markdown("### 🏆 Bestenliste")
    conn = get_connection()
    rangliste = bestenliste(conn, user_row["id"], name, user_row["xp_gesamt"])
    freunde = meine_freunde(conn, user_row["id"])
    conn.close()

    for eintrag in rangliste:
        medaille = {1: "🥇", 2: "🥈", 3: "🥉"}.get(eintrag["rang"], f"{eintrag['rang']}.")
        stil = "font-weight:700;" if eintrag["ist_ich"] else ""
        st.markdown(
            f'<div style="{stil}padding:6px 0;">{medaille} {eintrag["name"]} '
            f'{"(ich)" if eintrag["ist_ich"] else ""} — Level {eintrag["level"]} '
            f'({eintrag["xp"]} XP)</div>',
            unsafe_allow_html=True,
        )

    if freunde:
        st.divider()
        st.markdown("### Meine Freunde")
        for f in freunde:
            col_name, col_entfernen = st.columns([3, 1])
            with col_name:
                st.write(f["name"])
            with col_entfernen:
                if st.button("Entfernen", key=f"entfernen_freund_{f['id']}"):
                    conn = get_connection()
                    freundschaft_entfernen(conn, user_row["id"], f["id"])
                    conn.close()
                    st.rerun()


UNVERTRAEGLICHKEITEN_INFO = [
    {
        "name": "Laktoseintoleranz (Milchzuckerunverträglichkeit)",
        "was_ist_das": (
            "Dem Körper fehlt das Enzym Laktase oder bildet zu wenig davon, um den "
            "Milchzucker (Laktose) im Dünndarm vollständig aufzuspalten. Der "
            "unverdaute Milchzucker gelangt dadurch in den Dickdarm."
        ),
        "beschwerden": (
            "Häufig genannt werden Blähungen, Bauchschmerzen, Durchfall und Übelkeit, "
            "typischerweise etwa 30 Minuten bis 2 Stunden nach dem Verzehr "
            "laktosehaltiger Lebensmittel."
        ),
        "lebensmittel": "Milch, Sahne, viele Joghurts - Hartkäse enthält oft deutlich weniger Laktose.",
    },
    {
        "name": "Fruktosemalabsorption (Fruchtzucker-Unverträglichkeit)",
        "was_ist_das": (
            "Der Dünndarm kann Fruchtzucker (Fruktose) nur eingeschränkt aufnehmen, "
            "wodurch er teilweise unverdaut in den Dickdarm gelangt."
        ),
        "beschwerden": "Häufig genannt werden Blähungen, Bauchkrämpfe und Durchfall.",
        "lebensmittel": "Obst, Honig, und viele Fertigprodukte, die mit Fruktosesirup gesüßt sind.",
    },
    {
        "name": "Histaminintoleranz",
        "was_ist_das": (
            "Wird mit einem verminderten Abbau von Histamin im Körper in Verbindung "
            "gebracht. Gilt als besonders vielschichtig und schwer zu diagnostizieren, "
            "da die Studienlage insgesamt uneinheitlich ist."
        ),
        "beschwerden": (
            "Das Beschwerdebild wird als sehr unterschiedlich beschrieben - genannt "
            "werden u.a. Kopfschmerzen, Hautrötungen, Verdauungsbeschwerden und "
            "Herzrasen."
        ),
        "lebensmittel": "Gereifter Käse, Rotwein, geräucherte und fermentierte Produkte, manche Fischsorten.",
    },
    {
        "name": "Zöliakie & Glutensensitivität",
        "was_ist_das": (
            "Zöliakie ist eine Autoimmunerkrankung, bei der Gluten die "
            "Dünndarmschleimhaut schädigt. Bei einer Glutensensitivität treten "
            "Beschwerden auf, ohne dass diese Autoimmunreaktion nachweisbar ist."
        ),
        "beschwerden": (
            "Häufig genannt werden Verdauungsbeschwerden und Müdigkeit; bei "
            "Zöliakie kann unbehandelt langfristig auch ein Nährstoffmangel "
            "entstehen."
        ),
        "lebensmittel": "Weizen, Roggen, Gerste und daraus hergestellte Produkte wie Brot, Nudeln, Gebäck.",
    },
]


def zeige_unvertraeglichkeiten_info():
    st.title("ℹ️ Nahrungsmittelunverträglichkeiten")
    st.caption("Ein grober Überblick zur Orientierung - für Details und eine Diagnose ist immer ärztlicher Rat gefragt.")

    st.markdown(
        '<div style="background:#FFF3CD;border:2px solid #F0C674;border-radius:12px;'
        'padding:16px 18px;margin-bottom:20px;">'
        '<b>⚠️ Kein Ersatz für ärztlichen Rat</b><br/>'
        '<span style="font-size:14px;">Diese Informationen sind allgemein gehalten und '
        'dienen nur der ersten Orientierung. Sie stellen keine medizinische Beratung dar '
        'und ersetzen keine Diagnose. Bei Verdacht auf eine Unverträglichkeit oder '
        'anhaltenden Beschwerden wende dich bitte an eine Ärztin oder einen Arzt.</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    for eintrag in UNVERTRAEGLICHKEITEN_INFO:
        with st.expander(eintrag["name"]):
            st.markdown("**Was ist das?**")
            st.write(eintrag["was_ist_das"])
            st.markdown("**Häufig genannte Beschwerden**")
            st.write(eintrag["beschwerden"])
            st.markdown("**Lebensmittel, bei denen häufig vorsichtig gegessen wird**")
            st.write(eintrag["lebensmittel"])

    st.divider()
    st.markdown("### Allergie oder Intoleranz - was ist der Unterschied?")
    st.write(
        "Bei einer **Allergie** reagiert das Immunsystem auf einen an sich harmlosen "
        "Stoff - schon kleine Mengen können eine heftige Reaktion auslösen, in "
        "seltenen Fällen bis hin zu einem lebensbedrohlichen anaphylaktischen "
        "Schock. Bei einer **Intoleranz** (Unverträglichkeit) ist in der Regel kein "
        "Immunsystem beteiligt, die Beschwerden hängen meist von der verzehrten "
        "Menge ab und sind unangenehm, aber typischerweise nicht lebensbedrohlich."
    )
    st.caption(
        "Du kannst deine Ernährungspräferenzen unter 'Mehr → Einstellungen' hinterlegen, "
        "damit dir passende Rezepte vorgeschlagen werden."
    )


def zeige_menues():
    st.title("🍽️ Menüs")
    st.caption("Vorspeise, Dessert oder gleich ein komplettes Menü zusammenstellen.")

    tab_menue, tab_vorspeisen, tab_desserts = st.tabs(
        ["🍽️ Menü zusammenstellen", "🥗 Vorspeisen", "🍰 Desserts"]
    )
    with tab_menue:
        zeige_drei_gaenge_menue()
    with tab_vorspeisen:
        zeige_vorspeisen()
    with tab_desserts:
        zeige_desserts()


def zeige_mehr():
    tab_lexikon, tab_favoriten, tab_freunde, tab_info, tab_versteckt, tab_einstellungen = st.tabs(
        ["📚 Kochlexikon", "❤️ Favoriten", "👥 Freunde", "ℹ️ Unverträglichkeiten", "🙈 Versteckte Rezepte", "⚙️ Einstellungen"]
    )
    with tab_lexikon:
        zeige_kochlexikon()
    with tab_favoriten:
        zeige_favoriten()
    with tab_freunde:
        zeige_freunde()
    with tab_info:
        zeige_unvertraeglichkeiten_info()
    with tab_versteckt:
        zeige_versteckte_rezepte()
    with tab_einstellungen:
        zeige_einstellungen()


# ---------------------------------------------------------------
# Routing
# ---------------------------------------------------------------
if seite == "✨ Tagesvorschlag":
    zeige_tagesvorschlag()
elif seite == "🍽️ Menüs":
    zeige_menues()
elif seite == "📖 Rezept-Bibliothek":
    zeige_rezept_bibliothek()
elif seite == "🗓️ Wochenplanung":
    zeige_wochenplanung()
elif seite == "🏆 Errungenschaften":
    zeige_errungenschaften()
elif seite == "••• Mehr":
    zeige_mehr()
else:
    zeige_warenkorb()
