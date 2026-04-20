"""
player.py – Spieler-Modul
==========================
Repräsentiert einen Spieler im Winzer-Spiel.

Sprint 1 – Grundlagen
"""

from __future__ import annotations
from typing import List
from region import Region


# ─────────────────────────────────────────────────────────────────────────────
# Klasse: Spieler
# ─────────────────────────────────────────────────────────────────────────────
class Spieler:
    """
    Repräsentiert einen einzelnen Spieler.

    Attribute:
        name               : Spielername
        geld               : Kapital in Euro (Start: 50.000 EUR)
        region             : Gewähltes Weinanbaugebiet
        weinberg           : Weinberg-Objekt (ab Sprint 2)
        keller             : Keller-Objekt (ab Sprint 3)
        rathaus_angemeldet : Ob der Spieler im Rathaus registriert ist
        lizenzen           : Liste erworbener Lizenzen
        runden_aktionen    : Aktionen der aktuellen Runde
    """

    def __init__(self, name: str, region: Region) -> None:
        self.name: str = name
        self.geld: float = 50_000.0  # Startkapital in Euro
        self.region: Region = region
        self.weinberg = None  # wird in Sprint 2 belegt
        self.keller = None  # wird in Sprint 3 belegt
        self.rathaus_angemeldet: bool = False
        self.lizenzen: List[str] = []
        self.runden_aktionen: List[str] = []

    # ── Darstellung ──────────────────────────────────────────────────────────

    def __str__(self) -> str:
        """Kurzdarstellung für die Konsole."""
        return (
            f"  {self.name} "
            f"| Region: {self.region.name.value} "
            f"| Kapital: {self.geld:,.2f} EUR"
        )

    def get_status(self) -> str:
        """Ausführlicher Statusbericht des Spielers."""
        lizenz_str = ", ".join(self.lizenzen) if self.lizenzen else "Keine"
        rathaus_str = "Ja" if self.rathaus_angemeldet else "Nein"
        return (
            f"\n  +------ Spieler-Status ----------------------+\n"
            f"  | Name     : {self.name}\n"
            f"  | Region   : {self.region.name.value}\n"
            f"  | Kapital  : {self.geld:>12,.2f} EUR\n"
            f"  | Rathaus  : {rathaus_str}\n"
            f"  | Lizenzen : {lizenz_str}\n"
            f"  +--------------------------------------------+"
        )

    # ── Kapitalverwaltung ────────────────────────────────────────────────────

    def geld_hinzufuegen(self, betrag: float) -> None:
        """Addiert einen Betrag zum Kapital."""
        self.geld += betrag
        self.runden_aktionen.append(f"+{betrag:,.2f} EUR erhalten")

    def geld_abziehen(self, betrag: float) -> bool:
        """
        Zieht einen Betrag vom Kapital ab.
        Gibt True zurück wenn erfolgreich,
        False wenn nicht genug Geld vorhanden.
        """
        if self.geld >= betrag:
            self.geld -= betrag
            self.runden_aktionen.append(f"-{betrag:,.2f} EUR ausgegeben")
            return True
        print(
            f"  Nicht genug Geld!"
            f" Benötigt: {betrag:,.2f} EUR,"
            f" Vorhanden: {self.geld:,.2f} EUR"
        )
        return False

    # ── Aktionen ─────────────────────────────────────────────────────────────

    def aktion_aufzeichnen(self, aktion: str) -> None:
        """Zeichnet eine Aktion für die aktuelle Runde auf."""
        self.runden_aktionen.append(aktion)

    def runde_abschliessen(self) -> None:
        """Setzt die Aktionsliste am Ende einer Runde zurück."""
        self.runden_aktionen = []

    # ── Serialisierung ───────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        """Wandelt den Spieler in ein Dictionary um (für JSON-Speicherung)."""
        return {
            "name": self.name,
            "geld": self.geld,
            "region": self.region.to_dict(),
            "rathaus_angemeldet": self.rathaus_angemeldet,
            "lizenzen": self.lizenzen,
            "runden_aktionen": self.runden_aktionen,
        }

    @classmethod
    def from_dict(cls, daten: dict) -> "Spieler":
        """Erstellt einen Spieler aus einem Dictionary (für JSON-Laden)."""
        region = Region.from_dict(daten["region"])
        spieler = cls(name=daten["name"], region=region)
        spieler.geld = daten["geld"]
        spieler.rathaus_angemeldet = daten["rathaus_angemeldet"]
        spieler.lizenzen = daten["lizenzen"]
        spieler.runden_aktionen = daten["runden_aktionen"]
        return spieler


def main() -> None:
    """Testet die Spieler-Klasse."""
    from region import REGIONEN

    print("Willkommen zum Deutschen Weinanbaugebiete-Explorer!")
    print("Bitte wählen Sie eine Region aus:")
    regionen = list(REGIONEN.values())
    for i, region in enumerate(regionen, start=1):
        eis = "❄" if region.eiswein_moeglich else " "
        topsorte = max(region.empfohlene_sorten, key=region.empfohlene_sorten.get)  # type: ignore
        print(f"[{i:2d}] {eis} {region.name.value:28} Top: {topsorte}")
    print("-" * 60)

    while True:
        try:
            auswahl = int(input("Region auswählen (Nummer): "))
            if 1 <= auswahl <= len(regionen):
                gewaehlte_region = regionen[auswahl - 1]
                break
        except ValueError:
            pass
        print("Bitte eine gültige Nummer eingeben.")

    spieler_name = input("Geben Sie Ihren Namen ein: ")
    spieler = Spieler(name=spieler_name, region=gewaehlte_region)
    print(spieler.get_status())


if __name__ == "__main__":
    main()
