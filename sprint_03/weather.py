"""
weather.py – Wettersystem
==========================
Dieses Modul simuliert das Wetter für jede Runde.
Das Wetter beeinflusst direkt den Öchsle-Wert der Trauben.

Neue Konzepte in Sprint 2:
  - random-Modul (Zufallszahlen)
  - Enum für Wetterzustände
  - Dataclass für Wetterereignisse
  - Funktionen mit Rückgabewert

Sprint 2 – Weinberg & Jahreszeiten
"""

import random
from enum import Enum
from dataclasses import dataclass


# ─────────────────────────────────────────────────────────────────────────────
# Enum: Jahreszeiten
# ─────────────────────────────────────────────────────────────────────────────
class Jahreszeit(Enum):
    """Die vier Jahreszeiten – je eine pro Spielrunde."""

    FRUEHLING = "Frühling"
    SOMMER = "Sommer"
    HERBST = "Herbst"
    WINTER = "Winter"


# ─────────────────────────────────────────────────────────────────────────────
# Enum: Wetterzustände
# ─────────────────────────────────────────────────────────────────────────────
class Wetterzustand(Enum):
    """Mögliche Wetterzustände im Spiel."""

    IDEAL = "Ideales Wetter"
    NORMAL = "Normales Wetter"
    REGEN = "Starkregen"
    TROCKENHEIT = "Trockenheit"
    FROST = "Frost"
    HAGEL = "Hagel"


# ─────────────────────────────────────────────────────────────────────────────
# Dataclass: Wetterereignis
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class Wetterereignis:
    """
    Repräsentiert ein konkretes Wetterereignis.

    Attribute:
        zustand        : Art des Wetters (Enum)
        oechsle_bonus  : Einfluss auf den Öchsle-Wert (kann negativ sein)
        beschreibung   : Lesbare Beschreibung für den Spieler
        ist_frost      : True wenn Frost → Eiswein möglich!
    """

    zustand: Wetterzustand
    oechsle_bonus: int
    beschreibung: str
    ist_frost: bool = False

    def __str__(self) -> str:
        vorzeichen = "+" if self.oechsle_bonus >= 0 else ""
        return (
            f"  Wetter    : {self.zustand.value}\n"
            f"  Einfluss  : {vorzeichen}{self.oechsle_bonus}° Öchsle\n"
            f"  Info      : {self.beschreibung}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Wetterereignisse je Jahreszeit
# Wahrscheinlichkeiten sind als Gewichte definiert:
# höheres Gewicht = häufiger
# ─────────────────────────────────────────────────────────────────────────────

# Alle möglichen Wetterereignisse mit ihren Auswirkungen
WETTER_EREIGNISSE = {
    Wetterzustand.IDEAL: Wetterereignis(
        Wetterzustand.IDEAL,
        oechsle_bonus=+10,
        beschreibung="Perfekte Bedingungen – Sonne und Wärme!",
    ),
    Wetterzustand.NORMAL: Wetterereignis(
        Wetterzustand.NORMAL,
        oechsle_bonus=0,
        beschreibung="Durchschnittliches Wetter – alles im grünen Bereich.",
    ),
    Wetterzustand.REGEN: Wetterereignis(
        Wetterzustand.REGEN,
        oechsle_bonus=-8,
        beschreibung="Zu viel Regen – die Trauben verwässern.",
    ),
    Wetterzustand.TROCKENHEIT: Wetterereignis(
        Wetterzustand.TROCKENHEIT,
        oechsle_bonus=-5,
        beschreibung="Trockenheit stresst die Reben.",
    ),
    Wetterzustand.FROST: Wetterereignis(
        Wetterzustand.FROST,
        oechsle_bonus=-15,
        beschreibung="Frost! Gefahr für die Ernte – aber Eiswein möglich!",
        ist_frost=True,
    ),
    Wetterzustand.HAGEL: Wetterereignis(
        Wetterzustand.HAGEL,
        oechsle_bonus=-20,
        beschreibung="Hagel zerstört Teile der Ernte!",
    ),
}

# Wetter-Wahrscheinlichkeiten je Jahreszeit
# Format: {Wetterzustand: Gewicht}
# Alle Gewichte einer Jahreszeit zusammen = Gesamtwahrscheinlichkeit
WETTER_GEWICHTE: dict = {
    Jahreszeit.FRUEHLING: {
        Wetterzustand.IDEAL: 20,
        Wetterzustand.NORMAL: 40,
        Wetterzustand.REGEN: 25,
        Wetterzustand.TROCKENHEIT: 10,
        Wetterzustand.FROST: 5,
        Wetterzustand.HAGEL: 0,
    },
    Jahreszeit.SOMMER: {
        Wetterzustand.IDEAL: 35,
        Wetterzustand.NORMAL: 35,
        Wetterzustand.REGEN: 10,
        Wetterzustand.TROCKENHEIT: 15,
        Wetterzustand.FROST: 0,
        Wetterzustand.HAGEL: 5,
    },
    Jahreszeit.HERBST: {
        Wetterzustand.IDEAL: 25,
        Wetterzustand.NORMAL: 30,
        Wetterzustand.REGEN: 20,
        Wetterzustand.TROCKENHEIT: 5,
        Wetterzustand.FROST: 15,  # ← Eiswein-Chance!
        Wetterzustand.HAGEL: 5,
    },
    Jahreszeit.WINTER: {
        Wetterzustand.IDEAL: 5,
        Wetterzustand.NORMAL: 10,
        Wetterzustand.REGEN: 10,
        Wetterzustand.TROCKENHEIT: 5,
        Wetterzustand.FROST: 90,  # ← Winter = oft Frost
        Wetterzustand.HAGEL: 0,
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# Funktion: Wetter würfeln
# ─────────────────────────────────────────────────────────────────────────────
def wetter_wuerfeln(jahreszeit: Jahreszeit) -> Wetterereignis:
    """
    Würfelt ein zufälliges Wetterereignis für die
    gegebene Jahreszeit.

    Berücksichtigt die Wahrscheinlichkeiten aus
    WETTER_GEWICHTE – manche Ereignisse sind in
    bestimmten Jahreszeiten häufiger.

    Args:
        jahreszeit: Die aktuelle Jahreszeit

    Returns:
        Wetterereignis: Das gewürfelte Ereignis
    """
    gewichte_dict = WETTER_GEWICHTE[jahreszeit]

    # Nur Ereignisse mit Gewicht > 0 berücksichtigen
    zustaende = [z for z, g in gewichte_dict.items() if g > 0]
    gewichte = [gewichte_dict[z] for z in zustaende]

    # Zufällige Auswahl mit Gewichtung
    # random.choices() berücksichtigt die Gewichte!
    gewaehlter_zustand = random.choices(zustaende, weights=gewichte, k=1)[0]

    return WETTER_EREIGNISSE[gewaehlter_zustand]


# ─────────────────────────────────────────────────────────────────────────────
# Funktion: Jahreszeit aus Runde berechnen
# ─────────────────────────────────────────────────────────────────────────────
def jahreszeit_berechnen(runde: int) -> Jahreszeit:
    """
    Berechnet die aktuelle Jahreszeit aus der Rundenzahl.

    Runde 1 → Frühling
    Runde 2 → Sommer
    Runde 3 → Herbst
    Runde 4 → Winter
    Runde 5 → Frühling (neues Jahr)
    usw.

    Args:
        runde: Aktuelle Spielrunde (startet bei 1)

    Returns:
        Jahreszeit: Die aktuelle Jahreszeit
    """
    # (runde - 1) % 4 gibt 0, 1, 2, 3 zurück
    # → passend zu den 4 Jahreszeiten
    index = (runde - 1) % 4
    return list(Jahreszeit)[index]


# ─────────────────────────────────────────────────────────────────────────────
# Funktion: Jahreszeit als Banner anzeigen
# ─────────────────────────────────────────────────────────────────────────────
def jahreszeit_anzeigen(jahreszeit: Jahreszeit, runde: int) -> None:
    """Zeigt die aktuelle Jahreszeit als Banner an."""

    # Passende Symbole je Jahreszeit
    symbole = {
        Jahreszeit.FRUEHLING: "🌸",
        Jahreszeit.SOMMER: "☀️",
        Jahreszeit.HERBST: "🍂",
        Jahreszeit.WINTER: "❄️",
    }
    symbol = symbole[jahreszeit]

    print(f"\n  {'═' * 46}")
    print(f"  {symbol}  Runde {runde} – {jahreszeit.value}  {symbol}")
    print(f"  {'═' * 46}")


def main() -> None:
    """Testet die Wetterfunktionen mit Beispielrunden."""
    for runde in range(1, 9):  # 8 Runden = 2 Jahre
        jahreszeit = jahreszeit_berechnen(runde)
        jahreszeit_anzeigen(jahreszeit, runde)
        wetter = wetter_wuerfeln(jahreszeit)
        print(wetter)


if __name__ == "__main__":
    main()
