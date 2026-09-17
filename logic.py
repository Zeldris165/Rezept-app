"""
logic.py
========
XP- und Level-Berechnung, losgelöst von Streamlit/DB testbar.
"""

XP_PRO_SCHWIERIGKEIT = {
    "einfach": 10,
    "mittel": 20,
    "aufwaendig": 35,
}

PORTIONEN_BONUS_MAX = 4  # gedeckelter Bonus, siehe Absprache
MAX_LEVEL = 99


def berechne_xp(schwierigkeit: str, portionen_gekocht: int, portionen_basis: int) -> int:
    """XP für eine Kochsession: Basis-XP nach Schwierigkeit + kleiner,
    gedeckelter Bonus für mehr gekochte Portionen als die Basis-Menge."""
    basis_xp = XP_PRO_SCHWIERIGKEIT.get(schwierigkeit, 10)
    bonus = max(0, portionen_gekocht - portionen_basis)
    bonus = min(bonus, PORTIONEN_BONUS_MAX)
    return basis_xp + bonus


def xp_fuer_level(level: int) -> int:
    """Kumulative XP, die für dieses Level nötig ist (abgeschwächte,
    RuneScape-inspirierte Kurve). Level 1 startet bei 0 XP."""
    if level <= 1:
        return 0
    return round(50 * (level - 1) ** 1.5)


def level_aus_xp(gesamt_xp: int) -> int:
    """Ermittelt das aktuelle Level aus der Gesamt-XP (max. Level 99)."""
    level = 1
    while level < MAX_LEVEL and gesamt_xp >= xp_fuer_level(level + 1):
        level += 1
    return level


def xp_bis_naechstes_level(gesamt_xp: int) -> tuple[int, int]:
    """Gibt (aktuelle XP im Level, XP die für das naechste Level noetig sind) zurueck.
    Bei Level 99 wird (0, 0) zurueckgegeben (Maximum erreicht)."""
    level = level_aus_xp(gesamt_xp)
    if level >= MAX_LEVEL:
        return 0, 0
    xp_level_start = xp_fuer_level(level)
    xp_level_ende = xp_fuer_level(level + 1)
    return gesamt_xp - xp_level_start, xp_level_ende - xp_level_start
