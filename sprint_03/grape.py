"""
grape.py – Traubensorten-Modul
=============================
Dieses Modul definiert alle spielbaren Rebsorten mit:
- Farbe (rot / weiss)
- Basis-Öchslewert
- Geeigneten Anbaugebieten (0–3 Sterne)

Sprint 1 – Grundlagen
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict


# ─────────────────────────────────────────────────────────────────────────────
# Enum: Rebsorten
# ─────────────────────────────────────────────────────────────────────────────
class Rebsorte(Enum):
    RIESLING = "Riesling"
    SPAETBURGUNDER = "Spaetburgunder"
    MUELLER_THURGAU = "Mueller-Thurgau"
    SILVANER = "Silvaner"
    GRAUBURGUNDER = "Grauburgunder"
    WEISSBURGUNDER = "Weissburgunder"
    DORNFELDER = "Dornfelder"
    ELBLING = "Elbling"
    FRUEHBURGUNDER = "Fruehburgunder"
    GEWUERZTRAMINER = "Gewuerztraminer"
    PORTUGIESER = "Portugieser"
    TROLLINGER = "Trollinger"
    LEMBERGER = "Lemberger"
    SCHEUREBE = "Scheurebe"


# ─────────────────────────────────────────────────────────────────────────────
# Dataclass: Traube
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class Traube:
    """
    Repräsentiert eine Rebsorte im Spiel.
    """

    sorte: Rebsorte
    farbe: str  # "rot" oder "weiss"
    basis_oechsle: int  # Ausgangs-Öchslewert
    region_eignung: Dict[str, int]  # Regionname → 0–3 Sterne
    beschreibung: str

    def get_eignung(self, region_name: str) -> int:
        """
        Gibt die Eignung (0–3) dieser Traube für eine Region zurück.
        """
        return self.region_eignung.get(region_name, 0)

    def __str__(self) -> str:
        return (
            f"\nTraubensorte : {self.sorte.value}\n"
            f"Farbe        : {self.farbe}\n"
            f"Basis-Öchsle : {self.basis_oechsle}°\n"
            f"Beschreibung : {self.beschreibung}"
        )

    def to_dict(self) -> dict:
        return {
            "sorte": self.sorte.value,
            "farbe": self.farbe,
            "basis_oechsle": self.basis_oechsle,
            "region_eignung": self.region_eignung,
            "beschreibung": self.beschreibung,
        }

    @classmethod
    def from_dict(cls, daten: dict) -> "Traube":
        return cls(
            sorte=Rebsorte(daten["sorte"]),
            farbe=daten["farbe"],
            basis_oechsle=daten["basis_oechsle"],
            region_eignung=daten["region_eignung"],
            beschreibung=daten["beschreibung"],
        )


# ─────────────────────────────────────────────────────────────────────────────
# Alle Traubensorten mit realistischen Daten
# Eignung: 3 = ideal | 2 = gut | 1 = möglich | 0 = ungeeignet
# ─────────────────────────────────────────────────────────────────────────────
TRAUBEN: Dict[Rebsorte, Traube] = {
    Rebsorte.RIESLING: Traube(
        Rebsorte.RIESLING,
        "weiss",
        72,
        {
            "Mosel": 3,
            "Rheingau": 3,
            "Pfalz": 3,
            "Baden": 1,
            "Franken": 1,
            "Wuerttemberg": 2,
            "Rheinhessen": 2,
            "Nahe": 3,
            "Mittelrhein": 3,
            "Ahr": 1,
            "Sachsen": 2,
            "Saale-Unstrut": 1,
            "Hessische Bergstrasse": 3,
        },
        "König der deutschen Weißweine – elegant, mineralisch, langlebig.",
    ),
    Rebsorte.SPAETBURGUNDER: Traube(
        Rebsorte.SPAETBURGUNDER,
        "rot",
        78,
        {
            "Ahr": 3,
            "Baden": 3,
            "Rheingau": 2,
            "Pfalz": 2,
            "Wuerttemberg": 2,
            "Mosel": 1,
        },
        "Die wichtigste deutsche Rotweinsorte – fein, fruchtig, elegant.",
    ),
    Rebsorte.MUELLER_THURGAU: Traube(
        Rebsorte.MUELLER_THURGAU,
        "weiss",
        68,
        {
            "Franken": 3,
            "Rheinhessen": 3,
            "Sachsen": 3,
            "Saale-Unstrut": 3,
            "Baden": 2,
            "Pfalz": 2,
        },
        "Ertragreich, mild – häufige Einsteigersorte.",
    ),
    Rebsorte.SILVANER: Traube(
        Rebsorte.SILVANER,
        "weiss",
        70,
        {
            "Franken": 3,
            "Saale-Unstrut": 3,
            "Rheinhessen": 2,
        },
        "Fränkischer Klassiker – trocken, mineralisch.",
    ),
    Rebsorte.GRAUBURGUNDER: Traube(
        Rebsorte.GRAUBURGUNDER,
        "weiss",
        80,
        {
            "Pfalz": 3,
            "Baden": 3,
            "Wuerttemberg": 2,
        },
        "Kräftig, vollmundig – liebt warme Regionen.",
    ),
    Rebsorte.WEISSBURGUNDER: Traube(
        Rebsorte.WEISSBURGUNDER,
        "weiss",
        76,
        {
            "Baden": 2,
            "Pfalz": 2,
            "Franken": 2,
            "Sachsen": 2,
        },
        "Fein und elegant – sehr vielseitig.",
    ),
    Rebsorte.DORNFELDER: Traube(
        Rebsorte.DORNFELDER,
        "rot",
        74,
        {
            "Pfalz": 3,
            "Rheinhessen": 3,
            "Wuerttemberg": 2,
        },
        "Dunkel, fruchtig – moderne deutsche Rotweinsorte.",
    ),
    Rebsorte.ELBLING: Traube(
        Rebsorte.ELBLING,
        "weiss",
        60,
        {
            "Mosel": 2,
        },
        "Sehr alte Rebsorte – säurebetont, gut für Sekt.",
    ),
    Rebsorte.FRUEHBURGUNDER: Traube(
        Rebsorte.FRUEHBURGUNDER,
        "rot",
        76,
        {
            "Ahr": 3,
            "Baden": 2,
        },
        "Früh reifend – feiner, samtiger Rotwein.",
    ),
    Rebsorte.GEWUERZTRAMINER: Traube(
        Rebsorte.GEWUERZTRAMINER,
        "weiss",
        82,
        {
            "Pfalz": 2,
            "Baden": 2,
        },
        "Sehr aromatisch – exotische Noten.",
    ),
    Rebsorte.PORTUGIESER: Traube(
        Rebsorte.PORTUGIESER,
        "rot",
        65,
        {
            "Pfalz": 2,
            "Rheinhessen": 2,
            "Ahr": 1,
        },
        "Leichter, fruchtiger Rotwein.",
    ),
    Rebsorte.TROLLINGER: Traube(
        Rebsorte.TROLLINGER,
        "rot",
        63,
        {
            "Wuerttemberg": 3,
        },
        "Typischer Württemberger – leicht und süffig.",
    ),
    Rebsorte.LEMBERGER: Traube(
        Rebsorte.LEMBERGER,
        "rot",
        80,
        {
            "Wuerttemberg": 3,
        },
        "Kräftig, würzig – Spitzenrotwein aus Württemberg.",
    ),
    Rebsorte.SCHEUREBE: Traube(
        Rebsorte.SCHEUREBE,
        "weiss",
        78,
        {
            "Franken": 2,
            "Rheinhessen": 2,
            "Pfalz": 2,
        },
        "Aromatisch – schwarze Johannisbeere.",
    ),
}


def traube_auswaehlen(region_name_value: str) -> Traube:
    """
    Interaktive Auswahl einer Traubensorte passend
    zur gewählten Region.

    Zeigt nur geeignete Sorten an, sortiert nach
    Eignung (beste zuerst).

    Args:
        region_name_value: Regionsname als String
                           z.B. "Mosel" oder "Pfalz"

    Returns:
        Traube: Die vom Spieler gewählte Traubensorte
    """
    # Nur geeignete Sorten filtern (Eignung > 0)
    # und nach Eignung absteigend sortieren
    geeignete = sorted(
        [
            (traube, traube.get_eignung(region_name_value))
            for traube in TRAUBEN.values()
            if traube.get_eignung(region_name_value) > 0
        ],
        key=lambda x: x[1],
        reverse=True,
    )

    if not geeignete:
        print(f"  ⚠ Keine geeigneten Sorten für " f"{region_name_value} gefunden!")
        # Fallback: erste Sorte zurückgeben
        return list(TRAUBEN.values())[0]

    # Tabelle anzeigen
    print(f"\n  Geeignete Traubensorten für {region_name_value}:")
    print("  " + "─" * 56)
    print(f"  {'Nr':<4} {'Sorte':<22} {'Farbe':<8} " f"{'Eignung':<10} Öchsle")
    print("  " + "─" * 56)

    for i, (traube, eignung) in enumerate(geeignete, start=1):
        sterne = "★" * eignung + "☆" * (3 - eignung)
        print(
            f"  [{i:2d}] {traube.sorte.value:<22} "
            f"{traube.farbe:<8} {sterne:<10} "
            f"{traube.basis_oechsle}°"
        )

    print("  " + "─" * 56)

    # Eingabe mit Validierung
    while True:
        try:
            wahl = int(input("  Deine Wahl (Nummer): "))
            if 1 <= wahl <= len(geeignete):
                gewaehlte = geeignete[wahl - 1][0]
                print(f"\n  ✓ {gewaehlte.sorte.value} gewählt!")
                print(gewaehlte)
                return gewaehlte
            print(f"  Bitte zwischen 1 und " f"{len(geeignete)} wählen.")
        except ValueError:
            print("  Ungültige Eingabe – bitte eine Zahl eingeben.")


if __name__ == "__main__":
    for traube in TRAUBEN.values():
        print(traube)
