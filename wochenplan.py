"""
wochenplan.py
=============
Logik rund um die Wochenplanung: Rezept pro Wochentag UND Mahlzeit
(Frühstück/Mittagessen/Abendessen) einplanen/entfernen, und die aktuelle
Kalenderwoche bestimmen.
"""

import sqlite3
from datetime import date

WOCHENTAGE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
MAHLZEITEN_TAG = ["Frühstück", "Mittagessen", "Abendessen"]


def aktuelle_kalenderwoche() -> str:
    """Liefert die aktuelle Kalenderwoche im Format 'YYYY-Www', z.B. '2026-W35'."""
    heute = date.today()
    jahr, woche, _ = heute.isocalendar()
    return f"{jahr}-W{woche:02d}"


def get_wochenplan(conn: sqlite3.Connection, user_id: int, kalenderwoche: str) -> dict:
    """Gibt ein Dict {(wochentag, mahlzeit): row} zurueck. Slots ohne Eintrag fehlen im Dict."""
    rows = conn.execute(
        """SELECT w.*, r.name AS rezept_name, r.kalorien_pro_portion, r.bild_url,
                  r.portionen_basis, r.protein_typ, r.schwierigkeit
           FROM wochenplan w
           JOIN rezepte r ON r.id = w.rezept_id
           WHERE w.user_id = ? AND w.kalenderwoche = ?""",
        (user_id, kalenderwoche),
    ).fetchall()
    return {(row["wochentag"], row["mahlzeit"]): row for row in rows}


def setze_tag(conn: sqlite3.Connection, user_id: int, kalenderwoche: str,
              wochentag: str, rezept_id: int, portionen: int, mahlzeit: str = "Abendessen"):
    """Plant ein Rezept fuer einen Wochentag + Mahlzeit ein (ueberschreibt einen
    evtl. schon vorhandenen Eintrag fuer denselben Tag/dieselbe Mahlzeit)."""
    conn.execute(
        """INSERT INTO wochenplan (user_id, kalenderwoche, wochentag, mahlzeit, rezept_id, portionen)
           VALUES (?, ?, ?, ?, ?, ?)
           ON CONFLICT(user_id, kalenderwoche, wochentag, mahlzeit)
           DO UPDATE SET rezept_id = excluded.rezept_id, portionen = excluded.portionen""",
        (user_id, kalenderwoche, wochentag, mahlzeit, rezept_id, portionen),
    )
    conn.commit()


def entferne_tag(conn: sqlite3.Connection, user_id: int, kalenderwoche: str,
                  wochentag: str, mahlzeit: str = "Abendessen"):
    """Entfernt die Planung fuer einen einzelnen Wochentag + Mahlzeit."""
    conn.execute(
        "DELETE FROM wochenplan WHERE user_id = ? AND kalenderwoche = ? AND wochentag = ? AND mahlzeit = ?",
        (user_id, kalenderwoche, wochentag, mahlzeit),
    )
    conn.commit()
