"""
rezepte.py
==========
Logik rund um Rezepte, die über reines CRUD hinausgeht: sichtbare Rezepte
pro Nutzer (unter Berücksichtigung versteckter Rezepte), Verstecken, und
das Erstellen einer eigenen, bearbeitbaren Kopie eines Rezepts.
"""

import sqlite3


def get_sichtbare_rezepte(conn: sqlite3.Connection, user_id: int):
    """Alle Rezepte, die dieser Nutzer NICHT versteckt hat."""
    return conn.execute(
        """SELECT r.* FROM rezepte r
           WHERE r.id NOT IN (
               SELECT rezept_id FROM versteckte_rezepte WHERE user_id = ?
           )
           ORDER BY r.name""",
        (user_id,),
    ).fetchall()


def get_sichtbare_rezepte_gefiltert(conn: sqlite3.Connection, user_id: int, aktive_praeferenzen: list[str]):
    """Wie get_sichtbare_rezepte, zusätzlich nach Ernährungspräferenzen gefiltert
    (Zutaten-Stichwort-Filter, siehe praeferenzen.py)."""
    from praeferenzen import rezept_erfuellt_praeferenzen

    rezepte = get_sichtbare_rezepte(conn, user_id)
    if not aktive_praeferenzen:
        return rezepte

    gefiltert = []
    for r in rezepte:
        zutaten = conn.execute(
            "SELECT name FROM zutaten WHERE rezept_id = ?", (r["id"],)
        ).fetchall()
        namen = [z["name"] for z in zutaten]
        if rezept_erfuellt_praeferenzen(r["protein_typ"], namen, aktive_praeferenzen):
            gefiltert.append(r)
    return gefiltert


def verstecke_rezept(conn: sqlite3.Connection, user_id: int, rezept_id: int):
    """Markiert ein Rezept für diesen Nutzer als 'nicht mehr anzeigen'."""
    conn.execute(
        "INSERT OR IGNORE INTO versteckte_rezepte (user_id, rezept_id) VALUES (?, ?)",
        (user_id, rezept_id),
    )
    conn.commit()


def get_versteckte_rezepte(conn: sqlite3.Connection, user_id: int):
    """Alle Rezepte, die dieser Nutzer versteckt hat."""
    return conn.execute(
        """SELECT r.* FROM rezepte r
           JOIN versteckte_rezepte v ON v.rezept_id = r.id
           WHERE v.user_id = ?
           ORDER BY r.name""",
        (user_id,),
    ).fetchall()


def zeige_rezept_wieder(conn: sqlite3.Connection, user_id: int, rezept_id: int):
    """Nimmt ein Rezept aus der Versteckt-Liste, es erscheint wieder normal."""
    conn.execute(
        "DELETE FROM versteckte_rezepte WHERE user_id = ? AND rezept_id = ?",
        (user_id, rezept_id),
    )
    conn.commit()


def ist_favorit(conn: sqlite3.Connection, user_id: int, rezept_id: int) -> bool:
    """Prüft, ob ein Rezept für diesen Nutzer als Favorit markiert ist."""
    row = conn.execute(
        "SELECT 1 FROM favoriten WHERE user_id = ? AND rezept_id = ?",
        (user_id, rezept_id),
    ).fetchone()
    return row is not None


def favorit_umschalten(conn: sqlite3.Connection, user_id: int, rezept_id: int) -> bool:
    """Schaltet den Favoriten-Status eines Rezepts um. Gibt den neuen Status zurück
    (True = jetzt Favorit, False = nicht mehr)."""
    if ist_favorit(conn, user_id, rezept_id):
        conn.execute(
            "DELETE FROM favoriten WHERE user_id = ? AND rezept_id = ?",
            (user_id, rezept_id),
        )
        conn.commit()
        return False
    conn.execute(
        "INSERT OR IGNORE INTO favoriten (user_id, rezept_id) VALUES (?, ?)",
        (user_id, rezept_id),
    )
    conn.commit()
    return True


def get_favoriten(conn: sqlite3.Connection, user_id: int):
    """Alle Rezepte, die dieser Nutzer als Favorit markiert hat, neueste zuerst."""
    return conn.execute(
        """SELECT r.* FROM rezepte r
           JOIN favoriten f ON f.rezept_id = r.id
           WHERE f.user_id = ?
           ORDER BY f.hinzugefuegt_am DESC""",
        (user_id,),
    ).fetchall()


def get_zutaten(conn: sqlite3.Connection, rezept_id: int):
    return conn.execute(
        "SELECT * FROM zutaten WHERE rezept_id = ? ORDER BY id", (rezept_id,)
    ).fetchall()


def erstelle_neues_rezept(
    conn: sqlite3.Connection,
    user_id: int,
    name: str,
    protein_typ: str,
    schwierigkeit: str,
    kategorie: str,
    zubereitungszeit_min: int,
    portionen_basis: int,
    kalorien_pro_portion: int,
    bild_url: str,
    zubereitung: str,
    zutaten: list[tuple[str, float, str]],
    gang: str = "Hauptgang",
    mahlzeiten: str = "Mittagessen,Abendessen",
):
    """Erstellt ein komplett neues, eigenes Rezept (nicht von einem Original kopiert)."""
    cur = conn.execute(
        """INSERT INTO rezepte
           (name, protein_typ, schwierigkeit, kategorie, gang, mahlzeiten, zubereitungszeit_min,
            portionen_basis, kalorien_pro_portion, bild_url, zubereitung,
            ist_custom, erstellt_von, freigeschaltet)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, 1)""",
        (
            name, protein_typ, schwierigkeit, kategorie, gang, mahlzeiten, zubereitungszeit_min,
            portionen_basis, kalorien_pro_portion, bild_url, zubereitung, user_id,
        ),
    )
    neues_rezept_id = cur.lastrowid

    for zname, menge, einheit in zutaten:
        conn.execute(
            "INSERT INTO zutaten (rezept_id, name, menge, einheit) VALUES (?, ?, ?, ?)",
            (neues_rezept_id, zname, menge, einheit),
        )

    conn.commit()
    return neues_rezept_id


def erstelle_eigene_kopie(
    conn: sqlite3.Connection,
    user_id: int,
    original_rezept_id: int,
    neuer_name: str,
    neue_zubereitung: str,
    neue_zutaten: list[tuple[str, float, str]],
):
    """Erstellt eine eigene, bearbeitbare Kopie eines Rezepts (ist_custom=1),
    ohne das Original für andere Nutzer zu verändern.

    neue_zutaten: Liste von (name, menge, einheit)-Tupeln.
    """
    original = conn.execute(
        "SELECT * FROM rezepte WHERE id = ?", (original_rezept_id,)
    ).fetchone()
    if not original:
        return None

    cur = conn.execute(
        """INSERT INTO rezepte
           (name, protein_typ, schwierigkeit, kategorie, zubereitungszeit_min,
            portionen_basis, kalorien_pro_portion, bild_url, zubereitung,
            ist_custom, erstellt_von, freigeschaltet)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, 1)""",
        (
            neuer_name,
            original["protein_typ"],
            original["schwierigkeit"],
            original["kategorie"],
            original["zubereitungszeit_min"],
            original["portionen_basis"],
            original["kalorien_pro_portion"],
            original["bild_url"],
            neue_zubereitung,
            user_id,
        ),
    )
    neues_rezept_id = cur.lastrowid

    for name, menge, einheit in neue_zutaten:
        conn.execute(
            "INSERT INTO zutaten (rezept_id, name, menge, einheit) VALUES (?, ?, ?, ?)",
            (neues_rezept_id, name, menge, einheit),
        )

    conn.commit()
    return neues_rezept_id
