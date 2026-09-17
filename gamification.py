"""
gamification.py
================
Kochprotokoll, XP-Vergabe und Errungenschafts-Logik.

ACHIEVEMENTS ist die einzige Quelle der Wahrheit fuer Name/Beschreibung
je Errungenschaft (code -> (name, beschreibung)). pruefe_achievements()
legt fehlende Eintraege bei Bedarf selbst in der DB an, seed_data.py
muss also nicht synchron gehalten werden.
"""

import sqlite3
from logic import berechne_xp, level_aus_xp

PROTEINARTEN = ["Huhn", "Fisch", "Rind", "Vegetarisch"]


# ---------------------------------------------------------------
# Hilfsfunktionen ueber das (angereicherte) Kochprotokoll
# ---------------------------------------------------------------
def _anzahl_gesamt(protokoll):
    return len(protokoll)


def _anzahl_kategorie(protokoll, kategorie):
    return sum(1 for p in protokoll if p["kategorie"] == kategorie)


def _anzahl_protein(protokoll, protein_typ):
    return sum(1 for p in protokoll if p["protein_typ"] == protein_typ)


def _anzahl_schwierigkeit(protokoll, schwierigkeit):
    return sum(1 for p in protokoll if p["schwierigkeit"] == schwierigkeit)


def _max_wiederholungen_gleiches_rezept(protokoll):
    if not protokoll:
        return 0
    zaehler = {}
    for p in protokoll:
        zaehler[p["rezept_id"]] = zaehler.get(p["rezept_id"], 0) + 1
    return max(zaehler.values())


def _max_portionen_einer_session(protokoll):
    if not protokoll:
        return 0
    return max(p["portionen_gekocht"] for p in protokoll)


def _alle_schwierigkeiten_abgedeckt(protokoll):
    vorhandene = {p["schwierigkeit"] for p in protokoll}
    return {"einfach", "mittel", "aufwaendig"}.issubset(vorhandene)


def _alle_proteine_abgedeckt(protokoll):
    vorhandene = {p["protein_typ"] for p in protokoll}
    return set(PROTEINARTEN).issubset(vorhandene)


def _anzahl_gang(protokoll, gang):
    return sum(1 for p in protokoll if p["gang"] == gang)


def _alle_gaenge_abgedeckt(protokoll):
    vorhandene = {p["gang"] for p in protokoll}
    return {"Vorspeise", "Hauptgang", "Dessert"}.issubset(vorhandene)


# ---------------------------------------------------------------
# Errungenschafts-Katalog: code -> (Name, Beschreibung, Bedingungsfunktion)
# Die Bedingungsfunktion bekommt (protokoll, level) und gibt True/False zurueck.
# ---------------------------------------------------------------
ACHIEVEMENTS = {
    "erste_schritte": ("Erste Schritte", "Dein erstes Rezept gekocht",
                        lambda p, lvl: _anzahl_gesamt(p) >= 1),
    "zehn_rezepte": ("Kochroutine", "10 Rezepte insgesamt gekocht",
                      lambda p, lvl: _anzahl_gesamt(p) >= 10),
    "zwanzig_rezepte": ("Küchenprofi", "20 Rezepte insgesamt gekocht",
                         lambda p, lvl: _anzahl_gesamt(p) >= 20),
    "fuenfzig_rezepte": ("Kochmeister", "50 Rezepte insgesamt gekocht",
                          lambda p, lvl: _anzahl_gesamt(p) >= 50),

    "suppen_5": ("Suppen-Fan", "5 Suppen gekocht",
                 lambda p, lvl: _anzahl_kategorie(p, "Suppe") >= 5),

    "stammgericht": ("Stammgericht", "Dasselbe Rezept 5-mal gekocht",
                      lambda p, lvl: _max_wiederholungen_gleiches_rezept(p) >= 5),
    "stammgericht_10": ("Familienrezept", "Dasselbe Rezept 10-mal gekocht",
                         lambda p, lvl: _max_wiederholungen_gleiches_rezept(p) >= 10),

    "alle_schwierigkeiten": ("Allrounder", "Mindestens ein Rezept jeder Schwierigkeit gekocht",
                              lambda p, lvl: _alle_schwierigkeiten_abgedeckt(p)),
    "zehn_aufwaendig": ("Sternekoch", "10 aufwändige Rezepte gekocht",
                         lambda p, lvl: _anzahl_schwierigkeit(p, "aufwaendig") >= 10),

    "grosses_festmahl": ("Festmahl", "Einmal für 8 oder mehr Portionen gekocht",
                          lambda p, lvl: _max_portionen_einer_session(p) >= 8),

    # Proteinart zum ersten Mal
    "huhn_erstmals": ("Hühnchen-Neuling", "Zum ersten Mal ein Hühnergericht gekocht",
                       lambda p, lvl: _anzahl_protein(p, "Huhn") >= 1),
    "fisch_erstmals": ("Fisch-Neuling", "Zum ersten Mal ein Fischgericht gekocht",
                        lambda p, lvl: _anzahl_protein(p, "Fisch") >= 1),
    "rind_erstmals": ("Rind-Neuling", "Zum ersten Mal ein Rindfleischgericht gekocht",
                       lambda p, lvl: _anzahl_protein(p, "Rind") >= 1),
    "vegetarisch_erstmals": ("Grüner Daumen", "Zum ersten Mal ein vegetarisches Gericht gekocht",
                              lambda p, lvl: _anzahl_protein(p, "Vegetarisch") >= 1),
    "alle_proteine": ("Allesesser", "Von jeder Proteinart (Huhn, Fisch, Rind, Vegetarisch) mindestens einmal gekocht",
                       lambda p, lvl: _alle_proteine_abgedeckt(p)),

    # Proteinart 10x
    "zehn_huhn": ("Geflügel-Experte", "10 Hühnergerichte gekocht",
                  lambda p, lvl: _anzahl_protein(p, "Huhn") >= 10),
    "zehn_fisch": ("Fischfan", "10 Fischgerichte gekocht",
                   lambda p, lvl: _anzahl_protein(p, "Fisch") >= 10),
    "zehn_rind": ("Fleischliebhaber", "10 Rindfleischgerichte gekocht",
                  lambda p, lvl: _anzahl_protein(p, "Rind") >= 10),
    "zehn_vegetarisch": ("Pflanzenpower", "10 vegetarische Gerichte gekocht",
                          lambda p, lvl: _anzahl_protein(p, "Vegetarisch") >= 10),

    # Level-Meilensteine
    "level_10": ("Aufsteiger", "Level 10 erreicht",
                 lambda p, lvl: lvl >= 10),
    "level_25": ("Fortgeschritten", "Level 25 erreicht",
                 lambda p, lvl: lvl >= 25),
    "level_50": ("Kochveteran", "Level 50 erreicht",
                 lambda p, lvl: lvl >= 50),
    "level_99": ("Legende", "Level 99 erreicht",
                 lambda p, lvl: lvl >= 99),

    # Vorspeisen & Desserts
    "vorspeise_erstmals": ("Auftakt", "Deine erste Vorspeise gekocht",
                            lambda p, lvl: _anzahl_gang(p, "Vorspeise") >= 1),
    "vorspeise_5": ("Vorspeisen-Fan", "5 Vorspeisen gekocht",
                     lambda p, lvl: _anzahl_gang(p, "Vorspeise") >= 5),
    "dessert_erstmals": ("Süßer Einstieg", "Dein erstes Dessert gekocht",
                          lambda p, lvl: _anzahl_gang(p, "Dessert") >= 1),
    "dessert_5": ("Naschkatze", "5 Desserts gekocht",
                   lambda p, lvl: _anzahl_gang(p, "Dessert") >= 5),
    "alle_gaenge": ("Menü-Erfahrung", "Je mindestens eine Vorspeise, einen Hauptgang und ein Dessert gekocht",
                     lambda p, lvl: _alle_gaenge_abgedeckt(p)),
}


# ---------------------------------------------------------------
# Kategorie je Achievement, fuer die Gruppierung auf der Errungenschaften-Seite
# ---------------------------------------------------------------
ACHIEVEMENT_KATEGORIE = {
    "erste_schritte": "Meilensteine", "zehn_rezepte": "Meilensteine",
    "zwanzig_rezepte": "Meilensteine", "fuenfzig_rezepte": "Meilensteine",

    "huhn_erstmals": "Proteinarten", "fisch_erstmals": "Proteinarten",
    "rind_erstmals": "Proteinarten", "vegetarisch_erstmals": "Proteinarten",
    "alle_proteine": "Proteinarten", "zehn_huhn": "Proteinarten",
    "zehn_fisch": "Proteinarten", "zehn_rind": "Proteinarten",
    "zehn_vegetarisch": "Proteinarten",

    "suppen_5": "Kochkunst", "stammgericht": "Kochkunst",
    "stammgericht_10": "Kochkunst", "alle_schwierigkeiten": "Kochkunst",
    "zehn_aufwaendig": "Kochkunst", "grosses_festmahl": "Kochkunst",

    "vorspeise_erstmals": "Vorspeisen & Desserts", "vorspeise_5": "Vorspeisen & Desserts",
    "dessert_erstmals": "Vorspeisen & Desserts", "dessert_5": "Vorspeisen & Desserts",
    "alle_gaenge": "Vorspeisen & Desserts",

    "level_10": "Level", "level_25": "Level", "level_50": "Level", "level_99": "Level",
}
ACHIEVEMENT_KATEGORIEN_REIHENFOLGE = [
    "Meilensteine", "Proteinarten", "Kochkunst", "Vorspeisen & Desserts", "Level",
]

# Fortschrittsberechnung (aktuell, ziel) fuer zaehlbare Achievements - fehlt ein
# Code hier, wird auf der Seite einfach kein Fortschrittsbalken angezeigt
# (z.B. bei "alle Proteine abgedeckt"-artigen Ja/Nein-Achievements).
ACHIEVEMENT_FORTSCHRITT = {
    "erste_schritte": (lambda p, lvl: (_anzahl_gesamt(p), 1)),
    "zehn_rezepte": (lambda p, lvl: (_anzahl_gesamt(p), 10)),
    "zwanzig_rezepte": (lambda p, lvl: (_anzahl_gesamt(p), 20)),
    "fuenfzig_rezepte": (lambda p, lvl: (_anzahl_gesamt(p), 50)),
    "suppen_5": (lambda p, lvl: (_anzahl_kategorie(p, "Suppe"), 5)),
    "stammgericht": (lambda p, lvl: (_max_wiederholungen_gleiches_rezept(p), 5)),
    "stammgericht_10": (lambda p, lvl: (_max_wiederholungen_gleiches_rezept(p), 10)),
    "zehn_aufwaendig": (lambda p, lvl: (_anzahl_schwierigkeit(p, "aufwaendig"), 10)),
    "grosses_festmahl": (lambda p, lvl: (_max_portionen_einer_session(p), 8)),
    "huhn_erstmals": (lambda p, lvl: (_anzahl_protein(p, "Huhn"), 1)),
    "fisch_erstmals": (lambda p, lvl: (_anzahl_protein(p, "Fisch"), 1)),
    "rind_erstmals": (lambda p, lvl: (_anzahl_protein(p, "Rind"), 1)),
    "vegetarisch_erstmals": (lambda p, lvl: (_anzahl_protein(p, "Vegetarisch"), 1)),
    "zehn_huhn": (lambda p, lvl: (_anzahl_protein(p, "Huhn"), 10)),
    "zehn_fisch": (lambda p, lvl: (_anzahl_protein(p, "Fisch"), 10)),
    "zehn_rind": (lambda p, lvl: (_anzahl_protein(p, "Rind"), 10)),
    "zehn_vegetarisch": (lambda p, lvl: (_anzahl_protein(p, "Vegetarisch"), 10)),
    "level_10": (lambda p, lvl: (lvl, 10)),
    "level_25": (lambda p, lvl: (lvl, 25)),
    "level_50": (lambda p, lvl: (lvl, 50)),
    "level_99": (lambda p, lvl: (lvl, 99)),
    "vorspeise_erstmals": (lambda p, lvl: (_anzahl_gang(p, "Vorspeise"), 1)),
    "vorspeise_5": (lambda p, lvl: (_anzahl_gang(p, "Vorspeise"), 5)),
    "dessert_erstmals": (lambda p, lvl: (_anzahl_gang(p, "Dessert"), 1)),
    "dessert_5": (lambda p, lvl: (_anzahl_gang(p, "Dessert"), 5)),
}


def berechne_fortschritt(conn: sqlite3.Connection, user_id: int, code: str):
    """Gibt (aktuell, ziel) fuer ein zaehlbares Achievement zurueck, oder None
    wenn es kein zaehlbares Achievement ist (z.B. 'alle Proteine abgedeckt')."""
    fn = ACHIEVEMENT_FORTSCHRITT.get(code)
    if fn is None:
        return None
    protokoll = _hole_protokoll(conn, user_id)
    user = conn.execute("SELECT xp_gesamt FROM users WHERE id = ?", (user_id,)).fetchone()
    level = level_aus_xp(user["xp_gesamt"]) if user else 1
    aktuell, ziel = fn(protokoll, level)
    return min(aktuell, ziel), ziel


def _hole_protokoll(conn: sqlite3.Connection, user_id: int):
    """Kochprotokoll des Nutzers, angereichert mit kategorie/protein_typ/schwierigkeit/gang."""
    return conn.execute(
        """SELECT k.*, r.kategorie, r.protein_typ, r.schwierigkeit, r.gang
           FROM kochprotokoll k
           JOIN rezepte r ON r.id = k.rezept_id
           WHERE k.user_id = ?""",
        (user_id,),
    ).fetchall()


def _hole_oder_erstelle_achievement(conn: sqlite3.Connection, code: str):
    """Gibt die achievements-Zeile fuer den Code zurueck, legt sie bei Bedarf an."""
    row = conn.execute("SELECT * FROM achievements WHERE code = ?", (code,)).fetchone()
    if row:
        return row
    name, beschreibung, _ = ACHIEVEMENTS[code]
    conn.execute(
        "INSERT OR IGNORE INTO achievements (code, name, beschreibung) VALUES (?, ?, ?)",
        (code, name, beschreibung),
    )
    conn.commit()
    return conn.execute("SELECT * FROM achievements WHERE code = ?", (code,)).fetchone()


def pruefe_achievements(conn: sqlite3.Connection, user_id: int):
    """Prueft alle Bedingungen gegen das aktuelle Kochprotokoll/Level und schaltet
    neue Errungenschaften frei. Gibt eine Liste neu freigeschalteter Achievement-Rows zurueck."""
    protokoll = _hole_protokoll(conn, user_id)
    user = conn.execute("SELECT xp_gesamt FROM users WHERE id = ?", (user_id,)).fetchone()
    level = level_aus_xp(user["xp_gesamt"]) if user else 1

    neu_freigeschaltet = []

    for code, (name, beschreibung, bedingung) in ACHIEVEMENTS.items():
        if not bedingung(protokoll, level):
            continue
        achievement = _hole_oder_erstelle_achievement(conn, code)
        bereits_frei = conn.execute(
            "SELECT 1 FROM nutzer_achievements WHERE user_id = ? AND achievement_id = ?",
            (user_id, achievement["id"]),
        ).fetchone()
        if bereits_frei:
            continue
        conn.execute(
            "INSERT INTO nutzer_achievements (user_id, achievement_id) VALUES (?, ?)",
            (user_id, achievement["id"]),
        )
        neu_freigeschaltet.append(achievement)

    conn.commit()
    return neu_freigeschaltet


def kochen_markieren(conn: sqlite3.Connection, user_id: int, rezept_id: int, portionen: int):
    """Traegt eine Kochsession ins Protokoll ein, vergibt XP und prueft Errungenschaften.
    Gibt (erhaltene_xp, neu_freigeschaltete_achievements) zurueck."""
    rezept = conn.execute("SELECT * FROM rezepte WHERE id = ?", (rezept_id,)).fetchone()
    xp = berechne_xp(rezept["schwierigkeit"], portionen, rezept["portionen_basis"])

    conn.execute(
        """INSERT INTO kochprotokoll (user_id, rezept_id, portionen_gekocht, xp_erhalten)
           VALUES (?, ?, ?, ?)""",
        (user_id, rezept_id, portionen, xp),
    )
    conn.execute(
        "UPDATE users SET xp_gesamt = xp_gesamt + ? WHERE id = ?",
        (xp, user_id),
    )
    conn.commit()

    neu = pruefe_achievements(conn, user_id)
    return xp, neu


def get_achievements_gruppiert(conn: sqlite3.Connection, user_id: int):
    """Alle Achievements inkl. Status und Fortschritt, gruppiert nach Kategorie
    in fester Reihenfolge. Gibt eine Liste von (kategorie_name, [achievement_dicts]) zurueck."""
    alle = get_alle_achievements_mit_status(conn, user_id)
    protokoll = _hole_protokoll(conn, user_id)
    user = conn.execute("SELECT xp_gesamt FROM users WHERE id = ?", (user_id,)).fetchone()
    level = level_aus_xp(user["xp_gesamt"]) if user else 1

    angereichert = []
    for a in alle:
        eintrag = dict(a)
        fn = ACHIEVEMENT_FORTSCHRITT.get(a["code"])
        if fn and not a["freigeschaltet"]:
            aktuell, ziel = fn(protokoll, level)
            eintrag["fortschritt"] = (min(aktuell, ziel), ziel)
        else:
            eintrag["fortschritt"] = None
        angereichert.append(eintrag)

    gruppen = {}
    for e in angereichert:
        kat = ACHIEVEMENT_KATEGORIE.get(e["code"], "Sonstige")
        gruppen.setdefault(kat, []).append(e)

    reihenfolge = ACHIEVEMENT_KATEGORIEN_REIHENFOLGE + [k for k in gruppen if k not in ACHIEVEMENT_KATEGORIEN_REIHENFOLGE]
    return [(kat, gruppen[kat]) for kat in reihenfolge if kat in gruppen]


def get_alle_achievements_mit_status(conn: sqlite3.Connection, user_id: int):
    """Alle Achievement-Definitionen (inkl. noch nicht in der DB angelegter),
    jeweils mit Info ob der Nutzer sie schon hat."""
    for code in ACHIEVEMENTS:
        _hole_oder_erstelle_achievement(conn, code)

    return conn.execute(
        """SELECT a.*,
                  CASE WHEN na.user_id IS NULL THEN 0 ELSE 1 END AS freigeschaltet,
                  na.freigeschaltet_am
           FROM achievements a
           LEFT JOIN nutzer_achievements na
                  ON na.achievement_id = a.id AND na.user_id = ?
           ORDER BY freigeschaltet DESC, a.name""",
        (user_id,),
    ).fetchall()


def get_kochprotokoll_historie(conn: sqlite3.Connection, user_id: int, limit: int = 15):
    """Die letzten Kochsessions des Nutzers, neueste zuerst."""
    return conn.execute(
        """SELECT k.*, r.name AS rezept_name, r.bild_url
           FROM kochprotokoll k
           JOIN rezepte r ON r.id = k.rezept_id
           WHERE k.user_id = ?
           ORDER BY k.datum DESC, k.id DESC
           LIMIT ?""",
        (user_id, limit),
    ).fetchall()
