"""
player.py – Spieler-Modul (Sprint 3)
======================================
Erweitert um Kellerei-Aktionen:
  - weinlese_durchfuehren()  : Trauben ernten
  - eiswein_wagen()          : Auf Eiswein warten
  - most_keltern()           : Ernte ins Fass geben
  - fass_gaerung_starten()   : Gärung starten
  - fass_gaerung_abschluss() : Gärung abschließen
  - fass_lagern()            : Fass lagern
  - wein_abfuellen()         : Fass → Flaschen
  - flaschen_verkaufen()     : Flaschen verkaufen

Sprint 3 – Ernte, Kellerei & Weinqualität
"""

from __future__ import annotations
from typing import List, Optional
from region import Region
from vineyard import Weinberg
from grape import Traube
from winery import Kellerei, Fasszustand


# ─────────────────────────────────────────────────────────────────────────────
# Klasse: Spieler
# ─────────────────────────────────────────────────────────────────────────────
class Spieler:
    """
    Repräsentiert einen einzelnen Spieler.

    Neu in Sprint 3:
        keller : Kellerei-Objekt (jetzt aktiv!)
    """

    def __init__(self, name: str, region: Region) -> None:
        self.name: str = name
        self.geld: float = 50_000.0
        self.region: Region = region
        self.weinberg: Weinberg = Weinberg(region=region)
        self.keller: Kellerei = Kellerei()  # NEU Sprint 3
        self.rathaus_angemeldet: bool = False
        self.lizenzen: List[str] = []
        self.runden_aktionen: List[str] = []

    # ── Darstellung ──────────────────────────────────────────────────────────

    def __str__(self) -> str:
        return (
            f"  {self.name} "
            f"| Region: {self.region.name.value} "
            f"| Kapital: {self.geld:,.2f} EUR"
        )

    def get_status(self) -> str:
        """Ausführlicher Statusbericht des Spielers."""
        lizenz_str = ", ".join(self.lizenzen) if self.lizenzen else "Keine"
        rathaus_str = "Ja" if self.rathaus_angemeldet else "Nein"
        traube_str = (
            self.weinberg.traube.sorte.value
            if self.weinberg.traube
            else "Nicht bepflanzt"
        )
        fasser_aktiv = len(
            [f for f in self.keller.fass_liste if f.zustand != Fasszustand.ABGEFUELLT]
        )
        return (
            f"\n  +──── Spieler-Status ────────────────────────+\n"
            f"  | Name          : {self.name}\n"
            f"  | Region        : {self.region.name.value}\n"
            f"  | Kapital       : {self.geld:>12,.2f} EUR\n"
            f"  | Rebsorte      : {traube_str}\n"
            f"  | Öchsle        : {self.weinberg.oechsle_aktuell}°\n"
            f"  | Eiswein       : "
            f"{'❄ Wartend' if self.weinberg.eiswein_wartend else 'Nein'}\n"
            f"  | Ernte bereit  : "
            f"{'✓ Ja' if self.weinberg.ernte_verfuegbar else 'Nein'}"
            f" ({self.weinberg.ernte_oechsle}°)\n"
            f"  | Fässer aktiv  : {fasser_aktiv}\n"
            f"  | Flaschen      : {len(self.keller.flaschen_liste)}\n"
            f"  | Keller-Wert   : "
            f"{self.keller.get_gesamtwert_flaschen():,.2f} EUR\n"
            f"  | Rathaus       : {rathaus_str}\n"
            f"  | Lizenzen      : {lizenz_str}\n"
            f"  +────────────────────────────────────────────+"
        )

    def weinberg_status(self) -> None:
        """Gibt den Weinberg-Status aus."""
        print(f"\n  Weinberg von {self.name}:")
        print(self.weinberg)

    def keller_status(self) -> None:
        """Gibt den Kellerei-Status aus."""
        print(f"\n  Kellerei von {self.name}:")
        self.keller.kellerei_status()

    # ── Kapitalverwaltung ────────────────────────────────────────────────────

    def geld_hinzufuegen(self, betrag: float) -> None:
        """Addiert einen Betrag zum Kapital."""
        self.geld += betrag
        self.runden_aktionen.append(f"+{betrag:,.2f} EUR erhalten")

    def geld_abziehen(self, betrag: float) -> bool:
        """
        Zieht einen Betrag ab.
        Returns False wenn nicht genug Geld vorhanden.
        """
        if self.geld >= betrag:
            self.geld -= betrag
            self.runden_aktionen.append(f"-{betrag:,.2f} EUR ausgegeben")
            return True
        print(
            f"  ⚠ Nicht genug Geld!"
            f" Benötigt: {betrag:,.2f} EUR,"
            f" Vorhanden: {self.geld:,.2f} EUR"
        )
        return False

    # ── Weinberg-Aktionen ────────────────────────────────────────────────────

    def reben_anpflanzen(self, traube: Traube) -> bool:
        """Pflanzt Reben an und zieht Kosten ab."""
        if not self.geld_abziehen(Weinberg.KOSTEN_ANPFLANZEN):
            return False
        erfolg = self.weinberg.anpflanzen(traube)
        if not erfolg:
            self.geld_hinzufuegen(Weinberg.KOSTEN_ANPFLANZEN)
            return False
        self.aktion_aufzeichnen(
            f"Anpflanzen: {traube.sorte.value} "
            f"(-{Weinberg.KOSTEN_ANPFLANZEN:,.0f} EUR)"
        )
        print(f"  Kapital: {self.geld:,.2f} EUR")
        return True

    def weinberg_duengen(self) -> bool:
        """Düngt den Weinberg und zieht Kosten ab."""
        if not self.geld_abziehen(Weinberg.KOSTEN_DUENGER):
            return False
        erfolg = self.weinberg.duengen()
        if not erfolg:
            self.geld_hinzufuegen(Weinberg.KOSTEN_DUENGER)
            return False
        self.aktion_aufzeichnen(f"Gedüngt (-{Weinberg.KOSTEN_DUENGER:,.0f} EUR)")
        print(f"  Kapital: {self.geld:,.2f} EUR")
        return True

    def schaedlinge_bekaempfen(self) -> bool:
        """Bekämpft Schädlinge und zieht Kosten ab."""
        if not self.geld_abziehen(Weinberg.KOSTEN_SCHAEDLINGE):
            return False
        erfolg = self.weinberg.schaedlinge_bekaempfen()
        if not erfolg:
            self.geld_hinzufuegen(Weinberg.KOSTEN_SCHAEDLINGE)
            return False
        self.aktion_aufzeichnen(
            f"Schädlinge bekämpft " f"(-{Weinberg.KOSTEN_SCHAEDLINGE:,.0f} EUR)"
        )
        print(f"  Kapital: {self.geld:,.2f} EUR")
        return True

    # ── NEU Sprint 3: Ernte-Aktionen ─────────────────────────────────────────

    def weinlese_durchfuehren(self) -> bool:
        """
        Führt die normale Weinlese durch.

        Nur im Herbst möglich wenn ernte_bereit = True.

        Returns:
            True wenn Ernte erfolgreich
        """
        oechsle, erfolg = self.weinberg.weinlese()
        if erfolg:
            self.aktion_aufzeichnen(f"Weinlese: {oechsle}° Öchsle geerntet")
        return erfolg

    def eiswein_wagen(self) -> bool:
        """
        Spieler wartet auf Eiswein.

        Trauben hängen bis Winter.
        Risiko: Kein Frost → Ernte verloren!

        Returns:
            True wenn erfolgreich gesetzt
        """
        erfolg = self.weinberg.eiswein_warten()
        if erfolg:
            self.aktion_aufzeichnen("Eiswein: Trauben hängen gelassen ❄")
        return erfolg

    # ── NEU Sprint 3: Kellerei-Aktionen ──────────────────────────────────────

    def most_keltern(self) -> bool:
        """
        Keltert die geernteten Trauben ins Fass.

        Holt Ernte vom Weinberg und legt neues Fass an.
        Kosten: KOSTEN_KELTERN EUR

        Returns:
            True wenn erfolgreich
        """
        if not self.weinberg.ernte_verfuegbar:
            print("  ⚠ Keine Ernte zum Keltern vorhanden!")
            return False

        if not self.geld_abziehen(Kellerei.KOSTEN_KELTERN):
            return False

        # Ernte vom Weinberg holen
        oechsle, farbe, ist_eiswein = self.weinberg.ernte_abholen()

        if oechsle == 0:
            self.geld_hinzufuegen(Kellerei.KOSTEN_KELTERN)
            return False

        # Aktuelles Jahr als Jahrgang
        jahrgang = 2024 + (self.weinberg.reben_alter)

        # Ins Fass keltern
        fass = self.keller.keltern(
            rebsorte=(
                self.weinberg.traube.sorte.value
                if self.weinberg.traube
                else "Unbekannt"
            ),
            farbe=farbe,
            jahrgang=jahrgang,
            oechsle=oechsle,
            ist_eiswein=ist_eiswein,
            region=self.region.name.value,
        )

        self.aktion_aufzeichnen(
            f"Gekeltert: Fass #{fass.fass_id}"
            f" {oechsle}°"
            f" (-{Kellerei.KOSTEN_KELTERN:,.0f} EUR)"
        )
        print(f"  Kapital: {self.geld:,.2f} EUR")
        return True

    def fass_gaerung_starten(self, fass_id: int) -> bool:
        """
        Startet die Gärung in einem Fass.

        Returns:
            True wenn erfolgreich
        """
        erfolg = self.keller.gaerung_starten(fass_id)
        if erfolg:
            self.aktion_aufzeichnen(f"Gärung gestartet: Fass #{fass_id}")
        return erfolg

    def fass_gaerung_abschliessen(self, fass_id: int) -> bool:
        """
        Schließt die Gärung ab.

        Returns:
            True wenn erfolgreich
        """
        erfolg = self.keller.gaerung_abschliessen(fass_id)
        if erfolg:
            self.aktion_aufzeichnen(f"Gärung abgeschlossen: Fass #{fass_id}")
        return erfolg

    def fass_lagern(self, fass_id: int, monate: int = 1) -> bool:
        """
        Lagert ein Fass für eine bestimmte Zeit.

        Args:
            fass_id : ID des Fasses
            monate  : Anzahl Monate (Standard: 1)

        Returns:
            True wenn erfolgreich
        """
        erfolg = self.keller.fass_lagern(fass_id, monate)
        if erfolg:
            self.aktion_aufzeichnen(f"Gelagert: Fass #{fass_id}" f" +{monate} Monat(e)")
        return erfolg

    def wein_abfuellen(self, fass_id: int) -> bool:
        """
        Füllt ein Fass in Flaschen ab.

        Kosten: KOSTEN_ABFUELLEN EUR

        Returns:
            True wenn erfolgreich
        """
        if not self.geld_abziehen(Kellerei.KOSTEN_ABFUELLEN):
            return False

        flaschen = self.keller.abfuellen(fass_id)

        if flaschen is None:
            self.geld_hinzufuegen(Kellerei.KOSTEN_ABFUELLEN)
            return False

        self.aktion_aufzeichnen(
            f"Abgefüllt: Fass #{fass_id}"
            f" → {len(flaschen)} Flaschen"
            f" (-{Kellerei.KOSTEN_ABFUELLEN:,.0f} EUR)"
        )
        print(f"  Kapital: {self.geld:,.2f} EUR")
        return True

    def flaschen_verkaufen(self, anzahl: Optional[int] = None) -> float:
        """
        Verkauft Flaschen aus dem Keller.

        Args:
            anzahl: Anzahl Flaschen (None = alle)

        Returns:
            float: Einnahmen in EUR
        """
        erloese = self.keller.flaschen_verkaufen(anzahl)

        if erloese > 0:
            self.geld_hinzufuegen(erloese)
            self.aktion_aufzeichnen(f"Verkauf: +{erloese:,.2f} EUR")
            print(f"  Kapital: {self.geld:,.2f} EUR")

        return erloese

    # ── Aktionsverwaltung ────────────────────────────────────────────────────

    def aktion_aufzeichnen(self, aktion: str) -> None:
        """Zeichnet eine Aktion auf."""
        self.runden_aktionen.append(aktion)

    def runde_abschliessen(self) -> None:
        """Setzt die Aktionsliste zurück."""
        self.runden_aktionen = []

    # ── Serialisierung ───────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "geld": self.geld,
            "region": self.region.to_dict(),
            "weinberg": self.weinberg.to_dict(),
            "keller": self.keller.to_dict(),
            "rathaus_angemeldet": self.rathaus_angemeldet,
            "lizenzen": self.lizenzen,
            "runden_aktionen": self.runden_aktionen,
        }

    @classmethod
    def from_dict(cls, daten: dict) -> "Spieler":
        region = Region.from_dict(daten["region"])
        spieler = cls(name=daten["name"], region=region)
        spieler.geld = daten["geld"]
        spieler.rathaus_angemeldet = daten["rathaus_angemeldet"]
        spieler.lizenzen = daten["lizenzen"]
        spieler.runden_aktionen = daten["runden_aktionen"]
        spieler.weinberg = Weinberg.from_dict(daten["weinberg"])
        spieler.keller = Kellerei.from_dict(daten["keller"])
        return spieler


# ─────────────────────────────────────────────────────────────────────────────
# Self-Test
# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    """
    Testet alle Spieler-Aktionen in Sprint 3.
    Simuliert einen kompletten Durchlauf:
      Anpflanzen → Pflegen → Ernten → Keltern
      → Gärung → Lagern → Abfüllen → Verkaufen
    """
    from region import REGIONEN, RegionName
    from grape import TRAUBEN, Rebsorte
    from weather import (
        WETTER_EREIGNISSE,
        Wetterzustand,
        jahreszeit_berechnen,
        jahreszeit_anzeigen,
        Jahreszeit,
    )

    print("=" * 56)
    print("  SPIELER – Self-Test (Sprint 3)")
    print("=" * 56)

    # ── Setup ─────────────────────────────────────────────
    region = REGIONEN[RegionName.AHR]
    spieler = Spieler(name="Anna", region=region)
    print(f"\n  Spieler: {spieler}")

    # ── Anpflanzen ────────────────────────────────────────
    print("\n  Schritt 1: Spätburgunder anpflanzen")
    spaetburgunder = TRAUBEN[Rebsorte.SPAETBURGUNDER]
    spieler.reben_anpflanzen(spaetburgunder)

    # ── 3 Runden simulieren ───────────────────────────────
    print("\n  Schritt 2: Frühling & Sommer pflegen")
    for runde in range(1, 3):
        jz = jahreszeit_berechnen(runde)
        wetter = WETTER_EREIGNISSE[Wetterzustand.IDEAL]
        jahreszeit_anzeigen(jz, runde)
        spieler.weinberg_duengen()
        spieler.weinberg.runde_abschliessen(jz, wetter)

    # ── Herbst: normale Weinlese ──────────────────────────
    print("\n  Schritt 3: Herbst – Weinlese")
    jz = jahreszeit_berechnen(3)
    wetter = WETTER_EREIGNISSE[Wetterzustand.IDEAL]
    jahreszeit_anzeigen(jz, 3)
    spieler.weinberg.runde_abschliessen(jz, wetter)
    spieler.weinlese_durchfuehren()

    # ── Keltern ───────────────────────────────────────────
    print("\n  Schritt 4: Most keltern")
    spieler.most_keltern()

    # ── Gärung ────────────────────────────────────────────
    print("\n  Schritt 5: Gärung starten & abschließen")
    spieler.fass_gaerung_starten(1)
    spieler.fass_gaerung_abschliessen(1)

    # ── Lagerung ──────────────────────────────────────────
    print("\n  Schritt 6: Fass lagern (12 Monate)")
    spieler.fass_lagern(1, monate=12)

    # ── Abfüllen ──────────────────────────────────────────
    print("\n  Schritt 7: Wein abfüllen")
    spieler.wein_abfuellen(1)

    # ── Verkaufen ─────────────────────────────────────────
    print("\n  Schritt 8: Flaschen verkaufen")
    erloese = spieler.flaschen_verkaufen(6666)

    # ── Status ────────────────────────────────────────────
    print("\n  Schritt 9: Finaler Status")
    print(spieler.get_status())

    # ── Serialisierung ────────────────────────────────────
    print("\n  Schritt 10: Serialisierung")
    daten = spieler.to_dict()
    spieler2 = Spieler.from_dict(daten)
    gleich = (
        spieler.name == spieler2.name
        and spieler.geld == spieler2.geld
        and len(spieler.keller.fass_liste) == len(spieler2.keller.fass_liste)
    )
    print(f"  Original : {spieler.name}, {spieler.geld:,.2f} EUR")
    print(f"  Geladen  : {spieler2.name}, {spieler2.geld:,.2f} EUR")
    print(f"  Identisch: {'✓ Ja' if gleich else '✗ Nein'}")

    # ── Zusammenfassung ───────────────────────────────────
    print("\n" + "=" * 56)
    print("  Testergebnisse:")
    print("  " + "─" * 44)
    tests = [
        ("Anpflanzen erfolgreich", spieler.weinberg.traube is not None),
        ("Weinlese durchgeführt", not spieler.weinberg.ernte_verfuegbar),
        ("Fass angelegt", len(spieler.keller.fass_liste) == 1),
        (
            "Gärung abgeschlossen",
            spieler.keller.fass_liste[0].zustand == Fasszustand.ABGEFUELLT,
        ),
        ("Flaschen verkauft", len(spieler.keller.flaschen_liste) == 0),
        ("Erlös erhalten", erloese > 0),
        ("Serialisierung korrekt", gleich),
    ]
    alle_ok = True
    for test_name, ergebnis in tests:
        symbol = "✓" if ergebnis else "✗"
        print(f"  [{symbol}] {test_name}")
        if not ergebnis:
            alle_ok = False

    print("  " + "─" * 44)
    print(f"  Gesamt: " f"{'✓ Alle Tests bestanden!' if alle_ok else '✗ Fehler!'}")
    print("=" * 56)


if __name__ == "__main__":
    main()
