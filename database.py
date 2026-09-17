"""
database.py
============
Zentrales DB-Modul für die Rezept-App. Nutzt SQLite (Datei rezept_app.db).
Enthält Tabellen-Definitionen und eine Hilfsfunktion für Verbindungen.

Später leicht auf Postgres umstellbar, falls die App mal "richtig" gehostet
wird - deshalb bleibt die SQL größtenteils Standard-SQL ohne SQLite-Spezialitäten.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "rezept_app.db"


def get_connection() -> sqlite3.Connection:
    """Gibt eine Verbindung zur SQLite-DB zurück, mit Foreign-Key-Support aktiviert."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


SCHEMA = """
-- Nutzer
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    xp_gesamt INTEGER NOT NULL DEFAULT 0,
    erstellt_am TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Rezepte (geteilt zwischen allen Nutzern)
CREATE TABLE IF NOT EXISTS rezepte (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    protein_typ TEXT NOT NULL,          -- Huhn, Fisch, Rind, Vegetarisch, ...
    schwierigkeit TEXT NOT NULL,        -- einfach, mittel, aufwaendig
    kategorie TEXT,                     -- z.B. Suppe, Pfannengericht, Auflauf
    gang TEXT NOT NULL DEFAULT 'Hauptgang', -- Vorspeise, Hauptgang, Dessert
    mahlzeiten TEXT NOT NULL DEFAULT 'Mittagessen,Abendessen', -- kommagetrennt: Frühstück, Mittagessen, Abendessen
    zubereitungszeit_min INTEGER,
    portionen_basis INTEGER NOT NULL DEFAULT 2,
    kalorien_pro_portion INTEGER,
    bild_url TEXT,
    zubereitung TEXT,                   -- Freitext, Schritte durch Zeilenumbruch getrennt
    ist_custom INTEGER NOT NULL DEFAULT 0,   -- 0/1
    erstellt_von INTEGER,               -- user.id, falls custom
    freigeschaltet INTEGER NOT NULL DEFAULT 1,  -- 0/1, fuer spaeteres Freischaltsystem
    FOREIGN KEY (erstellt_von) REFERENCES users(id)
);

-- Zutaten pro Rezept (bezogen auf portionen_basis)
CREATE TABLE IF NOT EXISTS zutaten (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rezept_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    menge REAL NOT NULL,
    einheit TEXT,
    FOREIGN KEY (rezept_id) REFERENCES rezepte(id) ON DELETE CASCADE
);

-- Kochprotokoll (pro Nutzer, Basis fuer XP/Achievements)
CREATE TABLE IF NOT EXISTS kochprotokoll (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    rezept_id INTEGER NOT NULL,
    datum TEXT NOT NULL DEFAULT (date('now')),
    portionen_gekocht INTEGER NOT NULL,
    xp_erhalten INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (rezept_id) REFERENCES rezepte(id)
);

-- Achievement-Definitionen
CREATE TABLE IF NOT EXISTS achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,          -- z.B. 'suppen_5'
    name TEXT NOT NULL,
    beschreibung TEXT NOT NULL
);

-- Freigeschaltete Achievements pro Nutzer
CREATE TABLE IF NOT EXISTS nutzer_achievements (
    user_id INTEGER NOT NULL,
    achievement_id INTEGER NOT NULL,
    freigeschaltet_am TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (user_id, achievement_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (achievement_id) REFERENCES achievements(id)
);

-- Wochenplan: ein Eintrag pro Tag/Nutzer/Kalenderwoche
CREATE TABLE IF NOT EXISTS wochenplan (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    kalenderwoche TEXT NOT NULL,        -- z.B. '2026-W35'
    wochentag TEXT NOT NULL,            -- Montag..Sonntag
    mahlzeit TEXT NOT NULL DEFAULT 'Abendessen',  -- Frühstück, Mittagessen, Abendessen
    rezept_id INTEGER,
    portionen INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (rezept_id) REFERENCES rezepte(id),
    UNIQUE (user_id, kalenderwoche, wochentag, mahlzeit)
);

-- Versteckte Rezepte (pro Nutzer, z.B. weil es nicht schmeckt)
CREATE TABLE IF NOT EXISTS versteckte_rezepte (
    user_id INTEGER NOT NULL,
    rezept_id INTEGER NOT NULL,
    versteckt_am TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (user_id, rezept_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (rezept_id) REFERENCES rezepte(id)
);

-- Favoriten (pro Nutzer, Lieblingsrezepte)
CREATE TABLE IF NOT EXISTS favoriten (
    user_id INTEGER NOT NULL,
    rezept_id INTEGER NOT NULL,
    hinzugefuegt_am TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (user_id, rezept_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (rezept_id) REFERENCES rezepte(id)
);

-- Einkaufslisten (Warenkorb), eine aktive + Historie pro Nutzer
CREATE TABLE IF NOT EXISTS einkaufslisten (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    erstellt_am TEXT NOT NULL DEFAULT (datetime('now')),
    abgeschlossen INTEGER NOT NULL DEFAULT 0,
    abgeschlossen_am TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS einkaufsliste_artikel (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    liste_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    menge REAL,
    einheit TEXT,
    abgehakt INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (liste_id) REFERENCES einkaufslisten(id) ON DELETE CASCADE
);

-- Freundschaften (fuer Vergleich/Bestenliste)
CREATE TABLE IF NOT EXISTS freundschaften (
    user_id INTEGER NOT NULL,
    freund_id INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'angefragt',  -- angefragt, akzeptiert
    PRIMARY KEY (user_id, freund_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (freund_id) REFERENCES users(id)
);
"""


def init_db():
    """Legt alle Tabellen an, falls sie noch nicht existieren, und ergänzt
    neue Spalten bei bereits bestehenden Datenbanken (einfache Migration)."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = get_connection()
    conn.executescript(SCHEMA)
    conn.commit()

    # Migration: Personalisierungs-Spalten nachtraeglich ergaenzen, falls die
    # Datenbank schon vor dieser Funktion existierte.
    for spalte, definition in [
        ("hintergrundfarbe", "TEXT"),
        ("ernaehrungspraeferenzen", "TEXT"),
        ("kochlevel", "TEXT NOT NULL DEFAULT 'mittel'"),
        ("avatar_basis", "TEXT NOT NULL DEFAULT 'mann'"),
        ("avatar_gesicht", "TEXT NOT NULL DEFAULT 'keins'"),
        ("avatar_kopfbedeckung", "TEXT NOT NULL DEFAULT 'kochmuetze'"),
        ("avatar_extra", "TEXT NOT NULL DEFAULT 'keins'"),
        ("avatar_hals", "TEXT NOT NULL DEFAULT 'keins'"),
    ]:
        try:
            conn.execute(f"ALTER TABLE users ADD COLUMN {spalte} {definition}")
            conn.commit()
        except sqlite3.OperationalError:
            pass  # Spalte existiert schon - nichts zu tun

    for spalte, definition in [
        ("gang", "TEXT NOT NULL DEFAULT 'Hauptgang'"),
        ("mahlzeiten", "TEXT NOT NULL DEFAULT 'Mittagessen,Abendessen'"),
    ]:
        try:
            conn.execute(f"ALTER TABLE rezepte ADD COLUMN {spalte} {definition}")
            conn.commit()
        except sqlite3.OperationalError:
            pass  # Spalte existiert schon - nichts zu tun

    # Migration: wochenplan-Tabelle um 'mahlzeit' erweitern, damit pro Tag bis zu
    # 3 Eintraege (Fruehstueck/Mittagessen/Abendessen) moeglich sind. SQLite kann
    # UNIQUE-Bedingungen nicht per ALTER TABLE aendern, daher wird die Tabelle bei
    # Bedarf einmalig neu aufgebaut; bestehende Eintraege gelten als 'Abendessen'.
    spalten_info = conn.execute("PRAGMA table_info(wochenplan)").fetchall()
    spaltennamen = [s["name"] for s in spalten_info]
    if spalten_info and "mahlzeit" not in spaltennamen:
        conn.execute("ALTER TABLE wochenplan RENAME TO wochenplan_alt")
        conn.execute(
            """CREATE TABLE wochenplan (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                kalenderwoche TEXT NOT NULL,
                wochentag TEXT NOT NULL,
                mahlzeit TEXT NOT NULL DEFAULT 'Abendessen',
                rezept_id INTEGER,
                portionen INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (rezept_id) REFERENCES rezepte(id),
                UNIQUE (user_id, kalenderwoche, wochentag, mahlzeit)
            )"""
        )
        conn.execute(
            """INSERT INTO wochenplan (id, user_id, kalenderwoche, wochentag, mahlzeit, rezept_id, portionen)
               SELECT id, user_id, kalenderwoche, wochentag, 'Abendessen', rezept_id, portionen
               FROM wochenplan_alt"""
        )
        conn.execute("DROP TABLE wochenplan_alt")
        conn.commit()

    conn.close()


if __name__ == "__main__":
    init_db()
    print(f"Datenbank initialisiert unter: {DB_PATH}")
