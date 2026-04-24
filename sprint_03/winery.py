"""
winery.py – Kellerei-Modul (Sprint 3)
=======================================
Verwaltet Fässer, Gärung, Lagerung und
Abfüllung in Flaschen.

Korrekte Übergabe an market.py:
  - Lagerdauer in Monaten (kumulativ)
  - Farbe der Rebsorte (rot/weiss)
  - Eiswein-Flag (True/False)

Neue Konzepte in Sprint 3:
  - Objekt-Zustandsmaschine (Most → gärt → reif → Flasche)
  - Listen von Objekten verwalten
  - Enum für Zustände
  - Datenfluss zwischen Klassen

Sprint 3 – Ernte, Kellerei & Weinqualität
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
from market import preis_berechnen, Qualitaetsergebnis, MAX_LAGER_MONATE


# ─────────────────────────────────────────────────────────────────────────────
# Enum: Fasszustand
# ─────────────────────────────────────────────────────────────────────────────
class Fasszustand(Enum):
    """
    Zustandsmaschine eines Fasses:
    MOST → GAERUNG → REIF → ABGEFUELLT

    Jeder Zustand erlaubt andere Aktionen:
      MOST       : frisch gekeltert, noch kein Alkohol
      GAERUNG    : Hefe wandelt Zucker in Alkohol um
      REIF       : Gärung abgeschlossen, kann gelagert werden
      ABGEFUELLT : Inhalt wurde in Flaschen abgefüllt
    """

    MOST = "Most (frisch gekeltert)"
    GAERUNG = "In Gärung"
    REIF = "Reif (lagerbereit)"
    ABGEFUELLT = "Abgefüllt"


# ─────────────────────────────────────────────────────────────────────────────
# Dataclass: Fass
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class Fass:
    """
    Repräsentiert ein Fass in der Kellerei.

    Attribute:
        fass_id          : Eindeutige Nummer des Fasses
        rebsorte         : Name der Rebsorte
        farbe            : "rot" oder "weiss"
        jahrgang         : Erntejahr
        oechsle          : Öchsle-Grad des Mosts
        ist_eiswein      : True wenn Eiswein-Ernte
        region           : Herkunftsregion
        liter            : Inhalt in Litern
        zustand          : Aktueller Fasszustand (Enum)
        lager_monate     : Monate bereits gelagert
        max_lager_monate : Maximale sinnvolle Lagerdauer
    """

    fass_id: int
    rebsorte: str
    farbe: str
    jahrgang: int
    oechsle: int
    ist_eiswein: bool
    region: str
    liter: int = 500
    zustand: Fasszustand = Fasszustand.MOST
    lager_monate: int = 0
    max_lager_monate: int = 24

    def __str__(self) -> str:
        """Übersichtliche Darstellung eines Fasses."""
        eiswein_str = " ❄ EISWEIN" if self.ist_eiswein else ""
        warnung = ""
        if (
            self.zustand == Fasszustand.REIF
            and self.lager_monate > self.max_lager_monate
        ):
            warnung = "  ⚠ ÜBERLAGERT! Qualität sinkt!\n"

        return (
            f"\n  +── Fass #{self.fass_id} ──────────────────────────+\n"
            f"  | Rebsorte    : {self.rebsorte}{eiswein_str}\n"
            f"  | Farbe       : {self.farbe}\n"
            f"  | Jahrgang    : {self.jahrgang}\n"
            f"  | Öchsle      : {self.oechsle}°\n"
            f"  | Region      : {self.region}\n"
            f"  | Liter       : {self.liter} L\n"
            f"  | Zustand     : {self.zustand.value}\n"
            f"  | Gelagert    : {self.lager_monate} Monate"
            f" (max. {self.max_lager_monate})\n"
            f"{warnung}"
            f"  +─────────────────────────────────────────+"
        )

    def get_qualitaet(self) -> Qualitaetsergebnis:
        """
        Berechnet die aktuelle Qualität und den Preis.
        Übergibt korrekt: Lagerdauer, Farbe und Eiswein-Flag.
        """
        # Überlagerte Weine verlieren Qualität
        effektive_oechsle = self.oechsle
        if self.lager_monate > self.max_lager_monate:
            ueberlagerung = self.lager_monate - self.max_lager_monate
            # Pro Monat Überlagerung: -2° Öchsle
            effektive_oechsle = max(40, self.oechsle - ueberlagerung * 2)
            if ueberlagerung > 0:
                print(
                    f"  ⚠ Fass #{self.fass_id} überlagert!"
                    f" Öchsle: {self.oechsle}°"
                    f" → {effektive_oechsle}°"
                )

        return preis_berechnen(
            oechsle=effektive_oechsle,
            ist_eiswein=self.ist_eiswein,
            lager_monate=self.lager_monate,
            region=self.region,
            farbe=self.farbe,  # ← Rot/Weiß
        )

    def to_dict(self) -> dict:
        """Serialisiert das Fass als Dictionary."""
        return {
            "fass_id": self.fass_id,
            "rebsorte": self.rebsorte,
            "farbe": self.farbe,
            "jahrgang": self.jahrgang,
            "oechsle": self.oechsle,
            "ist_eiswein": self.ist_eiswein,
            "region": self.region,
            "liter": self.liter,
            "zustand": self.zustand.value,
            "lager_monate": self.lager_monate,
            "max_lager_monate": self.max_lager_monate,
        }

    @classmethod
    def from_dict(cls, daten: dict) -> "Fass":
        """Erstellt ein Fass aus einem Dictionary."""
        fass = cls(
            fass_id=daten["fass_id"],
            rebsorte=daten["rebsorte"],
            farbe=daten["farbe"],
            jahrgang=daten["jahrgang"],
            oechsle=daten["oechsle"],
            ist_eiswein=daten["ist_eiswein"],
            region=daten["region"],
            liter=daten["liter"],
            max_lager_monate=daten["max_lager_monate"],
        )
        fass.zustand = Fasszustand(daten["zustand"])
        fass.lager_monate = daten["lager_monate"]
        return fass


# ─────────────────────────────────────────────────────────────────────────────
# Dataclass: Flasche
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class Flasche:
    """
    Repräsentiert eine abgefüllte Weinflasche.

    Attribute:
        rebsorte        : Name der Rebsorte
        farbe           : "rot" oder "weiss"
        jahrgang        : Erntejahr
        oechsle         : Öchsle-Grad
        ist_eiswein     : True wenn Eiswein
        qualitaetsstufe : Qualitätsstufe
        preis           : Verkaufspreis in EUR
        region          : Herkunftsregion
        lager_monate    : Monate gelagert
    """

    rebsorte: str
    farbe: str
    jahrgang: int
    oechsle: int
    ist_eiswein: bool
    qualitaetsstufe: str
    preis: float
    region: str
    lager_monate: int

    def __str__(self) -> str:
        eiswein_str = " ❄" if self.ist_eiswein else ""
        return (
            f"  🍷 {self.jahrgang}er {self.rebsorte}"
            f"{eiswein_str} ({self.qualitaetsstufe})"
            f" – {self.preis:.2f} EUR"
            f" | {self.oechsle}°"
            f" | {self.lager_monate} Mon."
        )

    def to_dict(self) -> dict:
        return {
            "rebsorte": self.rebsorte,
            "farbe": self.farbe,
            "jahrgang": self.jahrgang,
            "oechsle": self.oechsle,
            "ist_eiswein": self.ist_eiswein,
            "qualitaetsstufe": self.qualitaetsstufe,
            "preis": self.preis,
            "region": self.region,
            "lager_monate": self.lager_monate,
        }

    @classmethod
    def from_dict(cls, daten: dict) -> "Flasche":
        return cls(**daten)


# ─────────────────────────────────────────────────────────────────────────────
# Klasse: Kellerei
# ─────────────────────────────────────────────────────────────────────────────
class Kellerei:
    """
    Verwaltet alle Fässer und Flaschen eines Spielers.

    Attribute:
        fass_liste     : Liste aller Fässer
        flaschen_liste : Liste aller abgefüllten Flaschen
        naechste_fass_id: Zähler für eindeutige Fass-IDs
    """

    # Kosten für Kellerei-Aktionen
    KOSTEN_KELTERN: int = 2_000
    KOSTEN_ABFUELLEN: int = 1_000

    def __init__(self) -> None:
        self.fass_liste: List[Fass] = []
        self.flaschen_liste: List[Flasche] = []
        self.naechste_fass_id: int = 1

    # ── Aktionen ─────────────────────────────────────────────────────────────

    def keltern(
        self,
        rebsorte: str,
        farbe: str,
        jahrgang: int,
        oechsle: int,
        ist_eiswein: bool,
        region: str,
        liter: int = 500,
    ) -> Fass:
        """
        Keltert Most aus geernteten Trauben ins Fass.

        Berechnet automatisch die maximale Lagerdauer
        anhand der Qualitätsstufe.

        Args:
            rebsorte    : Name der Rebsorte
            farbe       : "rot" oder "weiss"
            jahrgang    : Erntejahr
            oechsle     : Öchsle-Grad der Trauben
            ist_eiswein : True wenn Eiswein-Ernte
            region      : Herkunftsregion
            liter       : Menge in Litern

        Returns:
            Fass: Das neu angelegte Fass
        """
        from market import qualitaet_berechnen

        # Qualitätsstufe bestimmen → max. Lagerdauer
        stufe = qualitaet_berechnen(oechsle, ist_eiswein)
        max_lager = MAX_LAGER_MONATE.get(stufe, 24)

        # Neues Fass anlegen
        fass = Fass(
            fass_id=self.naechste_fass_id,
            rebsorte=rebsorte,
            farbe=farbe,
            jahrgang=jahrgang,
            oechsle=oechsle,
            ist_eiswein=ist_eiswein,
            region=region,
            liter=liter,
            zustand=Fasszustand.MOST,
            max_lager_monate=max_lager,
        )
        self.fass_liste.append(fass)
        self.naechste_fass_id += 1

        eiswein_str = " (EISWEIN ❄)" if ist_eiswein else ""
        print(f"\n  ✓ Fass #{fass.fass_id} angelegt:")
        print(
            f"    {rebsorte}{eiswein_str}, {oechsle}°,"
            f" {liter}L, Jahrgang {jahrgang}"
        )
        print(f"    Qualität: {stufe}" f" | Max. Lagerung: {max_lager} Monate")
        return fass

    def gaerung_starten(self, fass_id: int) -> bool:
        """
        Startet die Gärung in einem Fass Most.

        Nur möglich wenn Zustand = MOST.

        Returns:
            True wenn erfolgreich
        """
        fass = self._fass_suchen(fass_id)
        if fass is None:
            return False

        if fass.zustand != Fasszustand.MOST:
            print(f"  ⚠ Fass #{fass_id} ist nicht im " f"Zustand 'Most'.")
            return False

        fass.zustand = Fasszustand.GAERUNG
        print(f"  ✓ Gärung in Fass #{fass_id} gestartet!")
        print(f"    Hefe wandelt Zucker in Alkohol um ...")
        return True

    def gaerung_abschliessen(self, fass_id: int) -> bool:
        """
        Schließt die Gärung ab – Fass wird reif.

        In der Realität dauert Gärung 1–4 Wochen.
        Im Spiel: 1 Runde nach Start.

        Returns:
            True wenn erfolgreich
        """
        fass = self._fass_suchen(fass_id)
        if fass is None:
            return False

        if fass.zustand != Fasszustand.GAERUNG:
            print(f"  ⚠ Fass #{fass_id} gärt nicht.")
            return False

        fass.zustand = Fasszustand.REIF
        print(f"  ✓ Gärung abgeschlossen!")
        print(f"    Fass #{fass_id} ist jetzt reif " f"und lagerbereit.")
        return True

    def fass_lagern(self, fass_id: int, monate: int = 1) -> bool:
        """
        Lagert ein Fass für eine bestimmte Anzahl Monate.

        Nur reife Fässer können gelagert werden.
        Warnt wenn maximale Lagerdauer überschritten wird.

        Args:
            fass_id : ID des zu lagernden Fasses
            monate  : Anzahl Monate (Standard: 1)

        Returns:
            True wenn erfolgreich
        """
        fass = self._fass_suchen(fass_id)
        if fass is None:
            return False

        if fass.zustand != Fasszustand.REIF:
            print(f"  ⚠ Fass #{fass_id} ist nicht reif.")
            return False

        fass.lager_monate += monate

        # Warnung bei Überlagerung
        if fass.lager_monate > fass.max_lager_monate:
            ueber = fass.lager_monate - fass.max_lager_monate
            print(f"  ⚠ Fass #{fass_id} ist " f"{ueber} Monat(e) überlagert!")
            print(f"    Qualitätsverlust: -{ueber * 2}° Öchsle!")
        else:
            verbleibend = fass.max_lager_monate - fass.lager_monate
            print(
                f"  ✓ Fass #{fass_id} gelagert:"
                f" {fass.lager_monate} Monate"
                f" (noch {verbleibend} Monate möglich)"
            )

        return True

    def abfuellen(self, fass_id: int) -> Optional[List[Flasche]]:
        """
        Füllt ein reifes Fass in Flaschen ab.

        Berechnet:
          - Qualitätsstufe
          - Preis pro Flasche (mit Lagerdauer, Farbe, Eiswein)
          - Anzahl Flaschen (750ml pro Flasche)

        Args:
            fass_id: ID des abzufüllenden Fasses

        Returns:
            Liste der neuen Flaschen, oder None bei Fehler
        """
        fass = self._fass_suchen(fass_id)
        if fass is None:
            return None

        if fass.zustand != Fasszustand.REIF:
            print(f"  ⚠ Fass #{fass_id} ist nicht reif.")
            return None

        # Qualität & Preis berechnen
        # Hier fließen Lagerdauer, Farbe und Eiswein ein!
        qualitaet = fass.get_qualitaet()
        print(qualitaet)

        # Anzahl Flaschen (750ml pro Flasche)
        anzahl_flaschen = (fass.liter * 1000) // 750
        print(f"\n  Fülle {anzahl_flaschen} Flaschen ab ...")

        # Flaschen erstellen
        neue_flaschen: List[Flasche] = []
        for _ in range(anzahl_flaschen):
            flasche = Flasche(
                rebsorte=fass.rebsorte,
                farbe=fass.farbe,
                jahrgang=fass.jahrgang,
                oechsle=fass.oechsle,
                ist_eiswein=fass.ist_eiswein,
                qualitaetsstufe=qualitaet.stufe,
                preis=qualitaet.endpreis,
                region=fass.region,
                lager_monate=fass.lager_monate,
            )
            neue_flaschen.append(flasche)

        # Flaschen zum Keller hinzufügen
        self.flaschen_liste.extend(neue_flaschen)

        # Fass als abgefüllt markieren
        fass.zustand = Fasszustand.ABGEFUELLT

        gesamtwert = anzahl_flaschen * qualitaet.endpreis
        print(f"  ✓ {anzahl_flaschen} Flaschen abgefüllt!")
        print(
            f"    {qualitaet.stufe}"
            f" | {qualitaet.endpreis:.2f} EUR/Flasche"
            f" | Gesamt: {gesamtwert:,.2f} EUR"
        )

        return neue_flaschen

    def flaschen_verkaufen(self, anzahl: Optional[int] = None) -> float:
        """
        Verkauft Flaschen aus dem Keller.

        Args:
            anzahl: Anzahl zu verkaufender Flaschen.
                    None = alle verkaufen.

        Returns:
            float: Eingenommener Betrag in EUR
        """
        if not self.flaschen_liste:
            print("  Keine Flaschen im Keller.")
            return 0.0

        # Anzahl bestimmen
        if anzahl is None or anzahl > len(self.flaschen_liste):
            anzahl = len(self.flaschen_liste)
        zu_verkaufen = self.flaschen_liste[:anzahl]

        if not zu_verkaufen:
            print("  Keine Flaschen zum Verkauf.")
            return 0.0

        # Erlös berechnen
        erloese = sum(f.preis for f in zu_verkaufen)

        print(f"\n  Verkaufe {len(zu_verkaufen)} Flaschen:")
        count: int = 0
        for flasche in zu_verkaufen:
            print(f"    {flasche}")
            count += 1
            if count >= 5:
                print(f"    ... und {len(zu_verkaufen) - count} weitere Flaschen")
                break

        # Verkaufte Flaschen entfernen
        for flasche in zu_verkaufen:
            self.flaschen_liste.remove(flasche)

        print(f"\n  ✓ Erlös: {erloese:,.2f} EUR")
        return erloese

    def kellerei_status(self) -> None:
        """Zeigt den kompletten Keller-Status an."""
        print(f"\n  +── Kellerei-Status ────────────────────────+")

        # Fässer
        fasser_aktiv = [
            f for f in self.fass_liste if f.zustand != Fasszustand.ABGEFUELLT
        ]
        print(f"  | Fässer (aktiv)  : {len(fasser_aktiv)}")
        for fass in fasser_aktiv:
            print(fass)

        # Flaschen
        print(f"\n  | Flaschen        : {len(self.flaschen_liste)}")
        if self.flaschen_liste:
            gesamtwert = sum(f.preis for f in self.flaschen_liste)
            print(f"  | Gesamtwert      : {gesamtwert:,.2f} EUR")
            # Gruppierung nach Qualitätsstufe
            stufen: dict = {}
            for f in self.flaschen_liste:
                stufen[f.qualitaetsstufe] = stufen.get(f.qualitaetsstufe, 0) + 1
            for stufe, anzahl in sorted(stufen.items()):
                print(f"    {anzahl}x {stufe}")

        print(f"  +─────────────────────────────────────────+")

    # ── Hilfsmethoden ────────────────────────────────────────────────────────

    def _fass_suchen(self, fass_id: int) -> Optional[Fass]:
        """Sucht ein Fass anhand seiner ID."""
        for fass in self.fass_liste:
            if fass.fass_id == fass_id:
                return fass
        print(f"  ⚠ Fass #{fass_id} nicht gefunden!")
        return None

    def get_fass_liste_reif(self) -> List[Fass]:
        """Gibt alle reifen Fässer zurück."""
        return [f for f in self.fass_liste if f.zustand == Fasszustand.REIF]

    def get_gesamtwert_flaschen(self) -> float:
        """Gibt den Gesamtwert aller Flaschen zurück."""
        return sum(f.preis for f in self.flaschen_liste)

    # ── Serialisierung ───────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "fass_liste": [f.to_dict() for f in self.fass_liste],
            "flaschen_liste": [f.to_dict() for f in self.flaschen_liste],
            "naechste_fass_id": self.naechste_fass_id,
        }

    @classmethod
    def from_dict(cls, daten: dict) -> "Kellerei":
        kellerei = cls()
        kellerei.fass_liste = [Fass.from_dict(f) for f in daten["fass_liste"]]
        kellerei.flaschen_liste = [
            Flasche.from_dict(f) for f in daten["flaschen_liste"]
        ]
        kellerei.naechste_fass_id = daten["naechste_fass_id"]
        return kellerei


# ─────────────────────────────────────────────────────────────────────────────
# Self-Test
# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    """
    Testet die komplette Kellerei-Kette:
    Keltern → Gärung → Lagerung → Abfüllung → Verkauf
    Dabei werden Lagerdauer, Farbe und Eiswein korrekt
    an market.py übergeben.
    """
    print("=" * 56)
    print("  KELLEREI – Self-Test")
    print("=" * 56)

    kellerei = Kellerei()

    # ── Test 1: Weißwein keltert ──────────────────────────
    print("\n  Test 1: Riesling (Weißwein, Spätlese)")
    kellerei.keltern(
        rebsorte="Riesling",
        farbe="weiss",
        jahrgang=2024,
        oechsle=85,
        ist_eiswein=False,
        region="Mosel",
        liter=500,
    )

    # ── Test 2: Rotwein keltert ───────────────────────────
    print("\n  Test 2: Spätburgunder (Rotwein, Spätlese)")
    kellerei.keltern(
        rebsorte="Spaetburgunder",
        farbe="rot",
        jahrgang=2024,
        oechsle=85,
        ist_eiswein=False,
        region="Ahr",
        liter=500,
    )

    # ── Test 3: Eiswein keltert ───────────────────────────
    print("\n  Test 3: Riesling Eiswein ❄")
    kellerei.keltern(
        rebsorte="Riesling",
        farbe="weiss",
        jahrgang=2024,
        oechsle=118,
        ist_eiswein=True,
        region="Mosel",
        liter=200,
    )

    # ── Gärung für alle Fässer ────────────────────────────
    print("\n  Gärung starten & abschließen:")
    for fass_id in [1, 2, 3]:
        kellerei.gaerung_starten(fass_id)
        kellerei.gaerung_abschliessen(fass_id)

    # ── Lagerung: unterschiedlich lang ───────────────────
    print("\n  Lagerung:")
    kellerei.fass_lagern(1, monate=12)  # Riesling 12 Monate
    kellerei.fass_lagern(2, monate=24)  # Rotwein  24 Monate
    kellerei.fass_lagern(3, monate=12)  # Eiswein  12 Monate

    # ── Kellerei-Status ───────────────────────────────────
    print("\n  Kellerei-Status vor Abfüllung:")
    kellerei.kellerei_status()

    # ── Abfüllung ─────────────────────────────────────────
    print("\n  Abfüllung:")
    print("\n  Fass 1 – Riesling Weißwein, 12 Monate:")
    kellerei.abfuellen(1)

    print("\n  Fass 2 – Spätburgunder Rotwein, 24 Monate:")
    kellerei.abfuellen(2)

    print("\n  Fass 3 – Riesling Eiswein, 12 Monate:")
    kellerei.abfuellen(3)

    # ── Preisvergleich ────────────────────────────────────
    print("\n  Preisvergleich (gleiche Qualität, andere Farbe):")
    print("  (Rotwein sollte teurer sein als Weißwein!)")
    preise = {}
    for f in kellerei.flaschen_liste:
        key = f"{f.rebsorte} ({f.farbe})"
        preise[key] = f.preis
    for name, preis in preise.items():
        print(f"    {name:<30} {preis:>8.2f} EUR")

    # ── Serialisierung ────────────────────────────────────
    print("\n  Serialisierung:")
    daten = kellerei.to_dict()
    kellerei2 = Kellerei.from_dict(daten)
    gleich = len(kellerei.fass_liste) == len(kellerei2.fass_liste) and len(
        kellerei.flaschen_liste
    ) == len(kellerei2.flaschen_liste)
    print(
        f"  Fässer   : {len(kellerei.fass_liste)}"
        f" → {len(kellerei2.fass_liste)}"
        f" {'✓' if gleich else '✗'}"
    )
    print(
        f"  Flaschen : {len(kellerei.flaschen_liste)}"
        f" → {len(kellerei2.flaschen_liste)}"
        f" {'✓' if gleich else '✗'}"
    )

    # ── Zusammenfassung ───────────────────────────────────
    print("\n" + "=" * 56)
    print("  Testergebnisse:")
    print("  " + "─" * 44)

    rotwein = next((f for f in kellerei.flaschen_liste if f.farbe == "rot"), None)
    weisswein = next(
        (
            f
            for f in kellerei.flaschen_liste
            if f.farbe == "weiss" and not f.ist_eiswein
        ),
        None,
    )
    eiswein = next((f for f in kellerei.flaschen_liste if f.ist_eiswein), None)

    tests = [
        ("3 Fässer angelegt", len(kellerei.fass_liste) == 3),
        (
            "Gärung abgeschlossen",
            all(f.zustand == Fasszustand.ABGEFUELLT for f in kellerei.fass_liste),
        ),
        ("Flaschen abgefüllt", len(kellerei.flaschen_liste) > 0),
        (
            "Rotwein teurer als Weißwein",
            rotwein and weisswein and rotwein.preis > weisswein.preis,
        ),
        (
            "Eiswein teurer als Weißwein",
            eiswein and weisswein and eiswein.preis > weisswein.preis,
        ),
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
