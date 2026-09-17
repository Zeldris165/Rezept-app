"""
freunde.py
==========
Freundschaften zwischen Nutzern: Anfragen senden/annehmen/ablehnen,
Freundesliste, und eine Bestenliste nach Level unter Freunden.

Modell: pro Freundschaft gibt es (nach Annahme) zwei Zeilen in
freundschaften - eine je Richtung, beide mit status='akzeptiert'.
Eine offene Anfrage ist nur die eine Richtung mit status='angefragt'.
"""

import sqlite3
from logic import level_aus_xp


def nutzer_suchen(conn: sqlite3.Connection, username_suche: str, eigene_id: int):
    """Sucht Nutzer per (Teil-)Username, schliesst den eigenen Account aus."""
    return conn.execute(
        "SELECT id, username, name FROM users WHERE username LIKE ? AND id != ?",
        (f"%{username_suche}%", eigene_id),
    ).fetchall()


def sende_freundschaftsanfrage(conn: sqlite3.Connection, user_id: int, ziel_user_id: int) -> bool:
    """Sendet eine Freundschaftsanfrage. Gibt False zurueck, wenn schon eine
    Anfrage/Freundschaft in irgendeiner Form existiert oder man sich selbst waehlt."""
    if user_id == ziel_user_id:
        return False
    bereits_vorhanden = conn.execute(
        "SELECT 1 FROM freundschaften WHERE user_id = ? AND freund_id = ?",
        (user_id, ziel_user_id),
    ).fetchone()
    if bereits_vorhanden:
        return False
    conn.execute(
        "INSERT INTO freundschaften (user_id, freund_id, status) VALUES (?, ?, 'angefragt')",
        (user_id, ziel_user_id),
    )
    conn.commit()
    return True


def eingehende_anfragen(conn: sqlite3.Connection, user_id: int):
    """Anfragen, die andere Nutzer AN mich geschickt haben und ich noch nicht beantwortet habe."""
    return conn.execute(
        """SELECT u.id, u.username, u.name FROM freundschaften f
           JOIN users u ON u.id = f.user_id
           WHERE f.freund_id = ? AND f.status = 'angefragt'""",
        (user_id,),
    ).fetchall()


def anfrage_annehmen(conn: sqlite3.Connection, user_id: int, anfragender_id: int):
    """Nimmt eine eingehende Anfrage an: beide Richtungen werden auf 'akzeptiert' gesetzt."""
    conn.execute(
        "UPDATE freundschaften SET status = 'akzeptiert' WHERE user_id = ? AND freund_id = ?",
        (anfragender_id, user_id),
    )
    conn.execute(
        """INSERT INTO freundschaften (user_id, freund_id, status) VALUES (?, ?, 'akzeptiert')
           ON CONFLICT(user_id, freund_id) DO UPDATE SET status = 'akzeptiert'""",
        (user_id, anfragender_id),
    )
    conn.commit()


def anfrage_ablehnen(conn: sqlite3.Connection, user_id: int, anfragender_id: int):
    """Lehnt eine eingehende Anfrage ab (loescht sie ersatzlos)."""
    conn.execute(
        "DELETE FROM freundschaften WHERE user_id = ? AND freund_id = ?",
        (anfragender_id, user_id),
    )
    conn.commit()


def freundschaft_entfernen(conn: sqlite3.Connection, user_id: int, freund_id: int):
    """Entfernt eine bestehende Freundschaft in beide Richtungen."""
    conn.execute(
        "DELETE FROM freundschaften WHERE (user_id = ? AND freund_id = ?) OR (user_id = ? AND freund_id = ?)",
        (user_id, freund_id, freund_id, user_id),
    )
    conn.commit()


def meine_freunde(conn: sqlite3.Connection, user_id: int):
    """Alle akzeptierten Freunde des Nutzers."""
    return conn.execute(
        """SELECT u.id, u.username, u.name, u.xp_gesamt FROM freundschaften f
           JOIN users u ON u.id = f.freund_id
           WHERE f.user_id = ? AND f.status = 'akzeptiert'
           ORDER BY u.xp_gesamt DESC""",
        (user_id,),
    ).fetchall()


def bestenliste(conn: sqlite3.Connection, user_id: int, eigener_name: str, eigenes_xp: int):
    """Rangliste aus mir selbst + meinen Freunden, sortiert nach XP absteigend.
    Gibt eine Liste von Dicts mit rang/name/level/xp/ist_ich zurueck."""
    freunde = meine_freunde(conn, user_id)
    eintraege = [{"name": eigener_name, "xp": eigenes_xp, "ist_ich": True}]
    for f in freunde:
        eintraege.append({"name": f["name"], "xp": f["xp_gesamt"], "ist_ich": False})

    eintraege.sort(key=lambda e: e["xp"], reverse=True)
    for i, e in enumerate(eintraege, start=1):
        e["rang"] = i
        e["level"] = level_aus_xp(e["xp"])
    return eintraege
