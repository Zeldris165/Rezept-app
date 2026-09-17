"""
cart.py
=======
Logik rund um den Warenkorb / die Einkaufsliste. Getrennt von app.py,
damit die Logik unabhängig von Streamlit testbar bleibt.
"""

import sqlite3


def get_or_create_active_liste(conn: sqlite3.Connection, user_id: int) -> int:
    """Gibt die ID der aktuell aktiven (nicht abgeschlossenen) Einkaufsliste
    des Nutzers zurück, legt bei Bedarf eine neue an."""
    row = conn.execute(
        "SELECT id FROM einkaufslisten WHERE user_id = ? AND abgeschlossen = 0",
        (user_id,),
    ).fetchone()
    if row:
        return row["id"]

    cur = conn.execute(
        "INSERT INTO einkaufslisten (user_id, abgeschlossen) VALUES (?, 0)",
        (user_id,),
    )
    conn.commit()
    return cur.lastrowid


def add_rezept_zu_warenkorb(conn: sqlite3.Connection, user_id: int, rezept_id: int, portionen: int):
    """Skaliert die Zutaten eines Rezepts auf die gewünschte Portionenzahl und
    fügt sie der aktiven Einkaufsliste hinzu. Gleiche Zutaten (Name + Einheit)
    werden mengenmäßig zusammengeführt statt doppelt angelegt."""
    rezept = conn.execute("SELECT * FROM rezepte WHERE id = ?", (rezept_id,)).fetchone()
    if not rezept:
        return

    faktor = portionen / rezept["portionen_basis"]
    zutaten = conn.execute("SELECT * FROM zutaten WHERE rezept_id = ?", (rezept_id,)).fetchall()

    liste_id = get_or_create_active_liste(conn, user_id)

    for z in zutaten:
        menge_skaliert = round(z["menge"] * faktor, 2)
        einheit = z["einheit"] or ""

        bestehender_artikel = conn.execute(
            """SELECT id, menge FROM einkaufsliste_artikel
               WHERE liste_id = ? AND name = ? AND IFNULL(einheit, '') = ?""",
            (liste_id, z["name"], einheit),
        ).fetchone()

        if bestehender_artikel:
            neue_menge = round(bestehender_artikel["menge"] + menge_skaliert, 2)
            conn.execute(
                "UPDATE einkaufsliste_artikel SET menge = ? WHERE id = ?",
                (neue_menge, bestehender_artikel["id"]),
            )
        else:
            conn.execute(
                """INSERT INTO einkaufsliste_artikel (liste_id, name, menge, einheit, abgehakt)
                   VALUES (?, ?, ?, ?, 0)""",
                (liste_id, z["name"], menge_skaliert, einheit),
            )
    conn.commit()


def get_artikel(conn: sqlite3.Connection, liste_id: int):
    """Alle Artikel einer Liste, sortiert nach Name."""
    return conn.execute(
        "SELECT * FROM einkaufsliste_artikel WHERE liste_id = ? ORDER BY name",
        (liste_id,),
    ).fetchall()


def toggle_abgehakt(conn: sqlite3.Connection, artikel_id: int):
    """Kehrt den abgehakt-Status eines Artikels um."""
    conn.execute(
        "UPDATE einkaufsliste_artikel SET abgehakt = 1 - abgehakt WHERE id = ?",
        (artikel_id,),
    )
    conn.commit()


def einkauf_abschliessen(conn: sqlite3.Connection, liste_id: int):
    """Schließt eine Einkaufsliste ab (archiviert sie). Ein neuer Warenkorb
    wird beim nächsten Hinzufügen automatisch neu angelegt."""
    conn.execute(
        """UPDATE einkaufslisten
           SET abgeschlossen = 1, abgeschlossen_am = datetime('now')
           WHERE id = ?""",
        (liste_id,),
    )
    conn.commit()


def warenkorb_leeren(conn: sqlite3.Connection, liste_id: int):
    """Entfernt alle Artikel aus dem aktiven Warenkorb, OHNE ihn abzuschließen -
    z.B. falls man sich beim Hinzufügen verklickt hat. Die Liste selbst bleibt
    aktiv und bereit für neue Artikel."""
    conn.execute("DELETE FROM einkaufsliste_artikel WHERE liste_id = ?", (liste_id,))
    conn.commit()
