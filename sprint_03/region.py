"""
region.py – Deutsches Weinanbaugebiet-Modul
=============================================
Dieses Modul definiert alle 13 offiziellen deutschen Weinanbaugebiete
mit Klimadaten, Besonderheiten und Traubenempfehlungen.

Sprint 1 – Grundlagen
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Dict


# ─────────────────────────────────────────────────────────────────────────────
# Enum: Deutsche Weinanbaugebiete
# ─────────────────────────────────────────────────────────────────────────────
class RegionName(Enum):
    MOSEL = "Mosel"
    RHEINGAU = "Rheingau"
    PFALZ = "Pfalz"
    BADEN = "Baden"
    FRANKEN = "Franken"
    WUERTTEMBERG = "Wuerttemberg"
    RHEINHESSEN = "Rheinhessen"
    NAHE = "Nahe"
    MITTELRHEIN = "Mittelrhein"
    AHR = "Ahr"
    SACHSEN = "Sachsen"
    SAALE_UNSTRUT = "Saale-Unstrut"
    HESSISCHE_BERGSTRASSE = "Hessische Bergstrasse"


# ─────────────────────────────────────────────────────────────────────────────
# Dataclass: Region
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class Region:
    """
    Repräsentiert ein deutsches Weinanbaugebiet.
    """

    name: RegionName
    beschreibung: str
    klima: str
    besonderheiten: List[str]
    eiswein_moeglich: bool
    empfohlene_sorten: Dict[str, int]  # Sorte → 1–3 Sterne

    def __str__(self) -> str:
        sorten = ", ".join(
            f"{sorte} ({'*' * sterne})"
            for sorte, sterne in self.empfohlene_sorten.items()
        )
        eiswein = "Ja" if self.eiswein_moeglich else "Nein"
        return (
            f"\n+---------------- Region ----------------+\n"
            f"  Name         : {self.name.value}\n"
            f"  Klima        : {self.klima}\n"
            f"  Eiswein      : {eiswein}\n"
            f"  Beschreibung : {self.beschreibung}\n"
            f"  Empf. Sorten : {sorten}\n"
            f"  Besonderh.   : {', '.join(self.besonderheiten)}\n"
            f"+-----------------------------------------+"
        )

    def to_dict(self) -> dict:
        return {
            "name": self.name.value,
            "beschreibung": self.beschreibung,
            "klima": self.klima,
            "besonderheiten": self.besonderheiten,
            "eiswein_moeglich": self.eiswein_moeglich,
            "empfohlene_sorten": self.empfohlene_sorten,
        }

    @classmethod
    def from_dict(cls, daten: dict) -> "Region":
        return cls(
            name=RegionName(daten["name"]),
            beschreibung=daten["beschreibung"],
            klima=daten["klima"],
            besonderheiten=daten["besonderheiten"],
            eiswein_moeglich=daten["eiswein_moeglich"],
            empfohlene_sorten=daten["empfohlene_sorten"],
        )


# ─────────────────────────────────────────────────────────────────────────────
# Alle Regionen
# ─────────────────────────────────────────────────────────────────────────────
REGIONEN: Dict[RegionName, Region] = {
    RegionName.MOSEL: Region(
        RegionName.MOSEL,
        "Steiles Flusstal mit Schieferböden – weltberühmt für Riesling.",
        "Kühl, lange Vegetationsperiode",
        ["Steillagen", "Schieferboden"],
        True,
        {"Riesling": 3, "Elbling": 2},
    ),
    RegionName.RHEINGAU: Region(
        RegionName.RHEINGAU,
        "Traditionsregion am Rhein.",
        "Mild, sonnig",
        ["Spätlese-Tradition", "Klosterweinbau"],
        True,
        {"Riesling": 3, "Spaetburgunder": 2},
    ),
    RegionName.PFALZ: Region(
        RegionName.PFALZ,
        "Eine der wärmsten Regionen Deutschlands.",
        "Warm und trocken",
        ["Hohe Erträge", "Große Vielfalt"],
        False,
        {"Riesling": 3, "Dornfelder": 3, "Grauburgunder": 3},
    ),
    RegionName.BADEN: Region(
        RegionName.BADEN,
        "Südlichste Weinregion Deutschlands.",
        "Warm bis heiß",
        ["Kaiserstuhl", "Vulkanboden"],
        False,
        {"Spaetburgunder": 3, "Grauburgunder": 3},
    ),
    RegionName.FRANKEN: Region(
        RegionName.FRANKEN,
        "Heimat des Bocksbeutels.",
        "Kontinental",
        ["Muschelkalk", "Spätfrostgefahr"],
        True,
        {"Silvaner": 3, "Mueller-Thurgau": 3},
    ),
    RegionName.WUERTTEMBERG: Region(
        RegionName.WUERTTEMBERG,
        "Rotweinregion im Neckartal.",
        "Warm",
        ["Genossenschaften"],
        False,
        {"Trollinger": 3, "Lemberger": 3},
    ),
    RegionName.RHEINHESSEN: Region(
        RegionName.RHEINHESSEN,
        "Größtes deutsches Anbaugebiet.",
        "Warm",
        ["Große Fläche"],
        False,
        {"Mueller-Thurgau": 3, "Silvaner": 2},
    ),
    RegionName.NAHE: Region(
        RegionName.NAHE,
        "Sehr vielfältige Böden.",
        "Mild",
        ["Schiefer", "Vulkanstein"],
        True,
        {"Riesling": 3},
    ),
    RegionName.MITTELRHEIN: Region(
        RegionName.MITTELRHEIN,
        "Steillagen am Rhein, UNESCO-Welterbe.",
        "Kühl",
        ["Steillagen"],
        True,
        {"Riesling": 3},
    ),
    RegionName.AHR: Region(
        RegionName.AHR,
        "Berühmt für Spätburgunder.",
        "Kühl",
        ["Rotwein-Nische"],
        True,
        {"Spaetburgunder": 3},
    ),
    RegionName.SACHSEN: Region(
        RegionName.SACHSEN,
        "Sehr kleines Anbaugebiet an der Elbe.",
        "Kontinental",
        ["Elbhänge"],
        True,
        {"Mueller-Thurgau": 3},
    ),
    RegionName.SAALE_UNSTRUT: Region(
        RegionName.SAALE_UNSTRUT,
        "Nördlichstes Anbaugebiet Deutschlands.",
        "Trocken",
        ["Terrassenweinbau"],
        True,
        {"Silvaner": 3},
    ),
    RegionName.HESSISCHE_BERGSTRASSE: Region(
        RegionName.HESSISCHE_BERGSTRASSE,
        "Sehr kleines Gebiet, früher Vegetationsbeginn.",
        "Mild",
        ["Frühling beginnt sehr früh"],
        False,
        {"Riesling": 3},
    ),
}


# ─────────────────────────────────────────────────────────────────────────────
# Region auswählen
# ─────────────────────────────────────────────────────────────────────────────
def region_auswaehlen() -> Region:
    regionen = list(REGIONEN.values())

    print("\nVerfügbare Weinanbaugebiete:")
    print("-" * 60)

    for i, region in enumerate(regionen, start=1):
        eis = "❄" if region.eiswein_moeglich else " "
        topsorte = max(region.empfohlene_sorten, key=region.empfohlene_sorten.get)  # type: ignore
        print(f"[{i:2d}] {eis} {region.name.value:28} Top: {topsorte}")

    print("-" * 60)

    while True:
        try:
            wahl = int(input("Nummer wählen: "))
            if 1 <= wahl <= len(regionen):
                return regionen[wahl - 1]
        except ValueError:
            pass
        print("Bitte eine gültige Nummer eingeben.")


def main() -> None:
    print("Willkommen zum Deutschen Weinanbaugebiete-Explorer!")
    region = region_auswaehlen()
    print(region)


if __name__ == "__main__":
    main()
