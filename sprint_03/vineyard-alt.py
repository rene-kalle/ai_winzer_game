"""
vineyard.py – Weinberg-Modul (Sprint 3)
========================================
Erweitert um:
  - weinlese()         : Trauben ernten im Herbst
  - eiswein_warten()   : Trauben hängen lassen für Eiswein
  - eiswein_auflösen() : Im Winter auflösen (Frost oder Verlust)

Eiswein-Logik:
  Herbst : Spieler entscheidet → normal ernten ODER warten
  Winter : Frost?  JA  → Eiswein! 110–128° Öchsle
           Frost?  NEIN → Trauben verfault, Ernte verloren ☠

Sprint 3 – Ernte, Kellerei & Weinqualität
"""

from __future__ import annotations
import random
from typing import Optional, Tuple
from grape import Traube, TRAUBEN, Rebsorte
from region import Region
from weather import Wetterereignis, Jahreszeit


# ─────────────────────────────────────────────────────────────────────────────
# Klasse: Weinberg
# ─────────────────────────────────────────────────────────────────────────────
class Weinberg:
    """
    Repräsentiert den Weinberg eines Spielers.

    Neu in Sprint 3:
        eiswein_wartend  : Spieler wartet auf Eiswein
        ernte_oechsle    : Öchsle-Wert der geernteten Trauben
        ernte_verfuegbar : True wenn Trauben geerntet, aber
                           noch nicht gekeltert

    Reife-Faktoren (skalieren Pflege-Bonus):
        0 Jahre →  60%
        1 Jahr  →  80%
        2 Jahre →  90%
        3+Jahre → 100%
    """

    KOSTEN_ANPFLANZEN: int = 5_000
    KOSTEN_DUENGER: int = 1_000
    KOSTEN_SCHAEDLINGE: int = 1_500

    REIFE_FAKTOREN = {0: 0.6, 1: 0.8, 2: 0.9}
    REIFE_FAKTOR_VOLL = 1.0

    def __init__(self, region: Region) -> None:
        """Erstellt einen leeren Weinberg."""
        self.region: Region = region
        self.traube: Optional[Traube] = None
        self.reben_alter: int = 0
        self.pflegezustand: int = 50
        self.geduengt: bool = False
        self.schaedlingsbefall: bool = False
        self.ernte_bereit: bool = False
        self.oechsle_aktuell: int = 0

        # NEU Sprint 3: Eiswein & Ernte
        self.eiswein_wartend: bool = False
        self.ernte_oechsle: int = 0
        self.ernte_verfuegbar: bool = False

    # ── Hilfsmethoden ────────────────────────────────────────────────────────

    def get_reife_faktor(self) -> float:
        """Gibt den Reife-Faktor für das aktuelle Reben-Alter zurück."""
        return self.REIFE_FAKTOREN.get(self.reben_alter, self.REIFE_FAKTOR_VOLL)

    # ── Darstellung ──────────────────────────────────────────────────────────

    def __str__(self) -> str:
        """Übersichtliche Darstellung des Weinbergs."""
        traube_str = self.traube.sorte.value if self.traube else "Noch nicht bepflanzt"
        schaedling_str = "⚠ JA – bekämpfen!" if self.schaedlingsbefall else "Nein"
        ernte_str = "✓ Ja" if self.ernte_bereit else "Noch nicht"
        eiswein_str = "❄ Wartet auf Frost!" if self.eiswein_wartend else "Nein"
        ernte_v_str = (
            f"✓ {self.ernte_oechsle}° bereit!" if self.ernte_verfuegbar else "Nein"
        )

        return (
            f"\n  +──── Weinberg-Status ──────────────────────+\n"
            f"  | Region          : {self.region.name.value}\n"
            f"  | Rebsorte        : {traube_str}\n"
            f"  | Reben-Alter     : {self.reben_alter} Jahr(e)\n"
            f"  | Reife           : {self.get_reife_faktor():.0%}\n"
            f"  | Pflegezustand   : {self.pflegezustand}%\n"
            f"  | Gedüngt         : {'Ja' if self.geduengt else 'Nein'}\n"
            f"  | Schädlinge      : {schaedling_str}\n"
            f"  | Erntereif       : {ernte_str}\n"
            f"  | Öchsle aktuell  : {self.oechsle_aktuell}°\n"
            f"  | Eiswein wartend : {eiswein_str}\n"
            f"  | Ernte verfügbar : {ernte_v_str}\n"
            f"  +───────────────────────────────────────────+"
        )

    # ── Aktionen Sprint 1 & 2 ────────────────────────────────────────────────

    def anpflanzen(self, traube: Traube) -> bool:
        """Pflanzt eine Rebsorte in den Weinberg."""
        if self.traube is not None:
            print("  ⚠ Der Weinberg ist bereits bepflanzt!")
            return False

        eignung = traube.get_eignung(self.region.name.value)
        if eignung == 0:
            print(
                f"  ⚠ {traube.sorte.value} ist für "
                f"{self.region.name.value} nicht geeignet!"
            )
            return False

        self.traube = traube
        self.reben_alter = 0
        self.pflegezustand = 50
        regions_bonus = eignung * 3
        self.oechsle_aktuell = traube.basis_oechsle + regions_bonus

        sterne = "★" * eignung + "☆" * (3 - eignung)
        print(f"\n  ✓ {traube.sorte.value} wurde angepflanzt!")
        print(f"  Eignung  : {sterne}")
        print(
            f"  Start-Öchsle: {traube.basis_oechsle}°"
            f" + {regions_bonus}° = {self.oechsle_aktuell}°"
        )
        return True

    def duengen(self) -> bool:
        """Düngt den Weinberg."""
        if self.traube is None:
            print("  ⚠ Erst Reben anpflanzen!")
            return False
        if self.geduengt:
            print("  ⚠ Diese Runde bereits gedüngt!")
            return False
        self.pflegezustand = min(100, self.pflegezustand + 15)
        self.geduengt = True
        print(f"  ✓ Gedüngt! Pflegezustand: {self.pflegezustand}%")
        return True

    def schaedlinge_bekaempfen(self) -> bool:
        """Bekämpft Schädlingsbefall."""
        if not self.schaedlingsbefall:
            print("  Kein Schädlingsbefall.")
            return False
        self.schaedlingsbefall = False
        self.pflegezustand = min(100, self.pflegezustand + 10)
        print(f"  ✓ Schädlinge bekämpft! " f"Pflegezustand: {self.pflegezustand}%")
        return True

    # ── NEU Sprint 3: Weinlese ───────────────────────────────────────────────

    def weinlese(self) -> Tuple[int, bool]:
        """
        Führt die normale Weinlese durch.

        Nur möglich wenn:
          - Herbst (ernte_bereit = True)
          - Nicht auf Eiswein wartend

        Returns:
            Tuple (oechsle, erfolg):
              oechsle : Ernteergebnis in Grad Öchsle
              erfolg  : True wenn Ernte erfolgreich
        """
        if not self.ernte_bereit:
            print("  ⚠ Trauben noch nicht erntereif!")
            return (0, False)

        if self.eiswein_wartend:
            print("  ⚠ Warten auf Eiswein – " "erst im Winter auflösen!")
            return (0, False)

        if self.traube is None:
            print("  ⚠ Kein Weinberg bepflanzt!")
            return (0, False)

        # Ernte durchführen
        oechsle = self.oechsle_aktuell
        self.ernte_oechsle = oechsle
        self.ernte_verfuegbar = True
        self.ernte_bereit = False

        print(f"\n  🍇 Weinlese durchgeführt!")
        print(f"  Rebsorte  : {self.traube.sorte.value}")
        print(f"  Öchsle    : {oechsle}°")
        print(f"  → Trauben bereit zum Keltern!")

        return (oechsle, True)

    def eiswein_warten(self) -> bool:
        """
        Spieler entscheidet im Herbst auf Eiswein zu warten.

        Trauben bleiben hängen bis zum Winter.
        Risiko: Kein Frost → Trauben verfaulen!

        Returns:
            True wenn erfolgreich gesetzt
        """
        if not self.ernte_bereit:
            print("  ⚠ Trauben noch nicht erntereif!")
            return False

        if not self.region.eiswein_moeglich:
            print(f"  ⚠ In {self.region.name.value} " f"ist kein Eiswein möglich!")
            return False

        self.eiswein_wartend = True
        self.ernte_bereit = False

        print(f"\n  ❄ Trauben hängen für Eiswein!")
        print(f"  Aktueller Öchsle: {self.oechsle_aktuell}°")
        print(f"  → Im Winter entscheidet der Frost!")
        print(f"  → Frost kommt: ~{self._frost_wahrscheinlichkeit():.0%} Chance")
        return True

    def eiswein_auflösen(self, wetter: Wetterereignis) -> Tuple[int, bool]:
        """
        Löst die Eiswein-Entscheidung im Winter auf.

        Wird automatisch in runde_abschliessen() aufgerufen
        wenn eiswein_wartend = True und Jahreszeit = Winter.

        Ergebnis:
          Frost     → Öchsle 110–128°, Eiswein-Flag gesetzt ✅
          Kein Frost → Ernte verloren, Öchsle = 0          ☠

        Args:
            wetter: Das aktuelle Wetterereignis

        Returns:
            Tuple (oechsle, ist_eiswein):
              oechsle    : 0 bei Verlust, 110–128 bei Erfolg
              ist_eiswein: True wenn Eiswein geerntet
        """
        if not self.eiswein_wartend:
            return (0, False)

        self.eiswein_wartend = False

        if wetter.ist_frost:
            # ✅ Frost! Eiswein-Ernte erfolgreich
            eiswein_oechsle = random.randint(110, 128)
            self.ernte_oechsle = eiswein_oechsle
            self.ernte_verfuegbar = True

            print(f"\n  ❄ FROST! Eiswein-Ernte erfolgreich!")
            print(f"  Öchsle    : {eiswein_oechsle}°")
            print(f"  → Trauben sofort keltern!")
            return (eiswein_oechsle, True)

        else:
            # ☠ Kein Frost – Trauben verfault
            self.ernte_oechsle = 0
            self.ernte_verfuegbar = False
            self.oechsle_aktuell = 0

            print(f"\n  ☠ Kein Frost! Trauben verfault!")
            print(f"  Die gesamte Ernte ist verloren!")
            print(f"  Weinberg muss neu bepflanzt werden.")
            return (0, False)

    def ernte_abholen(self) -> Tuple[int, str, bool]:
        """
        Gibt die geernteten Trauben für die Kellerei frei.

        Wird von player.py aufgerufen um Most ins Fass zu geben.

        Returns:
            Tuple (oechsle, farbe, ist_eiswein):
              oechsle    : Öchsle-Grad der Ernte
              farbe      : "rot" oder "weiss"
              ist_eiswein: True wenn Eiswein
        """
        if not self.ernte_verfuegbar:
            print("  ⚠ Keine Ernte verfügbar!")
            return (0, "", False)

        oechsle = self.ernte_oechsle
        ist_eiswein = oechsle >= 110 and self.region.eiswein_moeglich
        farbe = self.traube.farbe if self.traube else "weiss"

        # Ernte zurücksetzen
        self.ernte_verfuegbar = False
        self.ernte_oechsle = 0

        # Weinberg zurücksetzen nach Ernte
        self.oechsle_aktuell = 0

        return (oechsle, farbe, ist_eiswein)

    # ── Jahreszeiten-Logik ───────────────────────────────────────────────────

    def runde_abschliessen(
        self,
        jahreszeit: Jahreszeit,
        wetter: Wetterereignis,
    ) -> None:
        """
        Verarbeitet das Ende einer Runde.

        NEU in Sprint 3:
          - Eiswein-Auflösung im Winter
          - Trauben verfaulen wenn Eiswein-Wartezeit abläuft
        """
        if self.traube is None:
            return

        reife_faktor = self.get_reife_faktor()

        # ── Eiswein-Auflösung im Winter ───────────────────
        if jahreszeit == Jahreszeit.WINTER and self.eiswein_wartend:
            self.eiswein_auflösen(wetter)
            # Nach Eiswein-Auflösung: restliche Logik überspringen
            self._runde_abschliessen_gemeinsam(jahreszeit, wetter, reife_faktor)
            return

        print(f"\n  ┌─── Öchsle-Entwicklung ──────────────────────┐")
        print(f"  │ Öchsle zu Beginn              : " f"{self.oechsle_aktuell:>4}°")
        print(
            f"  │ Reben-Reife ({self.reben_alter} Jahr(e))          :"
            f"   {reife_faktor:.0%}"
        )

        # ── Wetter ────────────────────────────────────────
        self.oechsle_aktuell += wetter.oechsle_bonus
        v = "+" if wetter.oechsle_bonus >= 0 else ""
        print(
            f"  │ Wetter ({wetter.zustand.value:<22}): "
            f"{v}{wetter.oechsle_bonus:>3}°"
        )

        # ── Pflege-Bonus × Reife-Faktor ───────────────────
        if self.geduengt:
            basis = self.pflegezustand // 10
            pflege_bonus = int(basis * reife_faktor)
            self.oechsle_aktuell += pflege_bonus
            print(
                f"  │ Pflege ({self.pflegezustand}%÷10"
                f"={basis}×{reife_faktor:.0%})        : "
                f"+{pflege_bonus:>3}°"
            )

        # ── Schädlings-Malus ──────────────────────────────
        if self.schaedlingsbefall:
            self.oechsle_aktuell -= 10
            print(f"  │ Schädlingsbefall              :  -10°")

        # ── Spätfrost-Malus ───────────────────────────────
        if (
            jahreszeit == Jahreszeit.FRUEHLING
            and wetter.ist_frost
            and self.reben_alter == 0
        ):
            self.oechsle_aktuell -= 15
            print(f"  │ Spätfrost (Jungreben)         :  -15°")

        # Minimum 40°
        self.oechsle_aktuell = max(self.oechsle_aktuell, 40)

        print(f"  ├─────────────────────────────────────────────┤")
        print(f"  │ Öchsle nach dieser Runde      : " f"{self.oechsle_aktuell:>4}°")
        print(f"  └─────────────────────────────────────────────┘")

        # ── Herbst: Erntereife setzen ─────────────────────
        if jahreszeit == Jahreszeit.HERBST:
            if not self.eiswein_wartend:
                self.ernte_bereit = True
                print("  ✓ Trauben sind erntereif!")

        # Gemeinsame Abschlusslogik
        self._runde_abschliessen_gemeinsam(jahreszeit, wetter, reife_faktor)

    def _runde_abschliessen_gemeinsam(
        self,
        jahreszeit: Jahreszeit,
        wetter: Wetterereignis,
        reife_faktor: float,
    ) -> None:
        """
        Gemeinsame Abschluss-Logik für alle Runden.
        Wird am Ende von runde_abschliessen() aufgerufen.
        """
        # Pflegezustand sinkt
        self.pflegezustand = max(0, self.pflegezustand - 10)
        self.geduengt = False

        # Reben altern im Winter
        if jahreszeit == Jahreszeit.WINTER:
            self.reben_alter += 1
            neuer_faktor = self.get_reife_faktor()
            print(
                f"  Reben: {self.reben_alter} Jahr(e)" f" → Reife: {neuer_faktor:.0%}"
            )

        # Zufälliger Schädlingsbefall (10%)
        if random.random() < 0.10:
            self.schaedlingsbefall = True
            print("  ⚠ Schädlingsbefall entdeckt!")

    # ── Hilfsmethoden ────────────────────────────────────────────────────────

    def _frost_wahrscheinlichkeit(self) -> float:
        """
        Gibt die Frost-Wahrscheinlichkeit für die Region zurück.
        Wird für die Eiswein-Entscheidung angezeigt.
        """
        from weather import WETTER_GEWICHTE, Jahreszeit, Wetterzustand

        gewichte = WETTER_GEWICHTE[Jahreszeit.WINTER]
        gesamt = sum(gewichte.values())
        frost = gewichte.get(Wetterzustand.FROST, 0)
        return frost / gesamt if gesamt > 0 else 0

    def get_oechsle(self) -> int:
        """Gibt den aktuellen Öchsle-Wert zurück."""
        return self.oechsle_aktuell

    def oechsle_anzeigen(self) -> None:
        """Zeigt den aktuellen Öchsle-Wert an."""
        if self.traube is None:
            print("  Kein Weinberg bepflanzt.")
            return
        print(f"\n  Rebsorte      : {self.traube.sorte.value}")
        print(f"  Öchsle        : {self.oechsle_aktuell}°")
        print(f"  Pflegezustand : {self.pflegezustand}%")
        print(f"  Reben-Alter   : {self.reben_alter} Jahr(e)")
        print(f"  Reife-Faktor  : {self.get_reife_faktor():.0%}")

    # ── Serialisierung ───────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "region": self.region.to_dict(),
            "traube": (self.traube.to_dict() if self.traube else None),
            "reben_alter": self.reben_alter,
            "pflegezustand": self.pflegezustand,
            "geduengt": self.geduengt,
            "schaedlingsbefall": self.schaedlingsbefall,
            "ernte_bereit": self.ernte_bereit,
            "oechsle_aktuell": self.oechsle_aktuell,
            "eiswein_wartend": self.eiswein_wartend,
            "ernte_oechsle": self.ernte_oechsle,
            "ernte_verfuegbar": self.ernte_verfuegbar,
        }

    @classmethod
    def from_dict(cls, daten: dict) -> "Weinberg":
        from region import Region

        region = Region.from_dict(daten["region"])
        weinberg = cls(region=region)
        weinberg.reben_alter = daten["reben_alter"]
        weinberg.pflegezustand = daten["pflegezustand"]
        weinberg.geduengt = daten["geduengt"]
        weinberg.schaedlingsbefall = daten["schaedlingsbefall"]
        weinberg.ernte_bereit = daten["ernte_bereit"]
        weinberg.oechsle_aktuell = daten.get("oechsle_aktuell", 0)
        weinberg.eiswein_wartend = daten.get("eiswein_wartend", False)
        weinberg.ernte_oechsle = daten.get("ernte_oechsle", 0)
        weinberg.ernte_verfuegbar = daten.get("ernte_verfuegbar", False)
        if daten["traube"]:
            weinberg.traube = Traube.from_dict(daten["traube"])
        return weinberg


# ─────────────────────────────────────────────────────────────────────────────
# Self-Test
# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    """
    Testet den Weinberg mit vollständiger Eiswein-Logik.
    Simuliert zwei parallele Szenarien:
      Szenario A: Normale Weinlese im Herbst
      Szenario B: Auf Eiswein warten → Frost im Winter
    """
    from region import REGIONEN, RegionName
    from grape import TRAUBEN, Rebsorte
    from weather import (
        WETTER_EREIGNISSE,
        Wetterzustand,
        jahreszeit_berechnen,
        jahreszeit_anzeigen,
    )

    print("=" * 56)
    print("  WEINBERG – Self-Test (Sprint 3, Eiswein-Logik)")
    print("=" * 56)

    region = REGIONEN[RegionName.MOSEL]
    riesling = TRAUBEN[Rebsorte.RIESLING]

    # ── Szenario A: Normale Weinlese ──────────────────────
    print("\n  ═══ Szenario A: Normale Weinlese ═══")
    weinberg_a = Weinberg(region=region)
    weinberg_a.anpflanzen(riesling)

    for runde in range(1, 4):
        jz = jahreszeit_berechnen(runde)
        wetter = WETTER_EREIGNISSE[Wetterzustand.NORMAL]
        jahreszeit_anzeigen(jz, runde)
        if jz == Jahreszeit.FRUEHLING:
            weinberg_a.duengen()
        weinberg_a.runde_abschliessen(jz, wetter)

    # Herbst: normal ernten
    print("\n  → Normale Weinlese:")
    oechsle, erfolg = weinberg_a.weinlese()
    print(f"  Ergebnis: {oechsle}°, Erfolg: {erfolg}")

    # ── Szenario B: Eiswein mit Frost ─────────────────────
    print("\n  ═══ Szenario B: Eiswein (mit Frost) ═══")
    weinberg_b = Weinberg(region=region)
    weinberg_b.anpflanzen(riesling)

    for runde in range(1, 4):
        jz = jahreszeit_berechnen(runde)
        wetter = WETTER_EREIGNISSE[Wetterzustand.NORMAL]
        jahreszeit_anzeigen(jz, runde)
        weinberg_b.runde_abschliessen(jz, wetter)

    # Herbst: auf Eiswein warten
    print("\n  → Auf Eiswein warten:")
    weinberg_b.eiswein_warten()

    # Winter: Frost kommt!
    print("\n  → Winter mit Frost:")
    jz = jahreszeit_berechnen(4)
    wetter = WETTER_EREIGNISSE[Wetterzustand.FROST]
    jahreszeit_anzeigen(jz, 4)
    weinberg_b.runde_abschliessen(jz, wetter)
    oechsle, farbe, ist_eiswein = weinberg_b.ernte_abholen()
    print(f"  Ergebnis: {oechsle}°, Eiswein: {ist_eiswein}")

    # ── Szenario C: Eiswein ohne Frost (Verlust) ──────────
    print("\n  ═══ Szenario C: Eiswein (kein Frost → Verlust) ═══")
    weinberg_c = Weinberg(region=region)
    weinberg_c.anpflanzen(riesling)

    for runde in range(1, 4):
        jz = jahreszeit_berechnen(runde)
        wetter = WETTER_EREIGNISSE[Wetterzustand.NORMAL]
        weinberg_c.runde_abschliessen(jz, wetter)

    weinberg_c.eiswein_warten()

    # Winter: kein Frost!
    print("\n  → Winter OHNE Frost:")
    jz = jahreszeit_berechnen(4)
    wetter = WETTER_EREIGNISSE[Wetterzustand.NORMAL]
    weinberg_c.runde_abschliessen(jz, wetter)

    # ── Zusammenfassung ───────────────────────────────────
    print("\n" + "=" * 56)
    print("  Testergebnisse:")
    print("  " + "─" * 44)
    tests = [
        ("Szenario A: Ernte erfolgreich", erfolg),
        ("Szenario A: Öchsle > 0", oechsle > 0 if erfolg else True),
        ("Szenario B: Eiswein geerntet", ist_eiswein),
        ("Szenario B: Öchsle >= 110°", oechsle >= 110),
        ("Szenario C: Ernte verloren", not weinberg_c.ernte_verfuegbar),
        ("Eiswein-Flag korrekt", ist_eiswein == True),
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
