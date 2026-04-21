"""
vineyard.py – Weinberg-Modul
=============================
Repräsentiert den Weinberg eines Spielers.
Hier werden Reben angepflanzt, gepflegt und
die Traubenqualität berechnet.

Neue Konzepte in Sprint 2:
  - Objekt-Interaktion (Weinberg kennt Traube & Region)
  - Berechnungen mit mehreren Faktoren
  - Methoden die andere Objekte verwenden

Sprint 2 – Weinberg & Jahreszeiten
"""

from __future__ import annotations
from typing import Optional
from grape import Traube, TRAUBEN, Rebsorte
from region import Region
from weather import Wetterereignis, Jahreszeit


# ─────────────────────────────────────────────────────────────────────────────
# Klasse: Weinberg
# ─────────────────────────────────────────────────────────────────────────────
class Weinberg:
    """
    Repräsentiert den Weinberg eines Spielers.

    Attribute:
        region          : Das Anbaugebiet des Weinbergs
        traube          : Eingepflanzte Rebsorte (None = noch leer)
        reben_alter     : Alter der Reben in Jahren
        pflegezustand   : Pflegequalität 0–100%
        geduengt        : Ob in dieser Runde gedüngt wurde
        schaedlingsbefall: Ob Schädlingsbefall vorliegt
        ernte_bereit    : Ob die Trauben erntereif sind
        kosten_anpflanzen: Kosten für das Anpflanzen in EUR
        kosten_duenger  : Kosten für Dünger in EUR
        kosten_schaedlinge: Kosten für Schädlingsbekämpfung in EUR
    """

    # Kosten für Aktionen (Klassenvariablen – gelten für alle Weinberge)
    KOSTEN_ANPFLANZEN: int = 5_000  # EUR pro Anpflanzung
    KOSTEN_DUENGER: int = 1_000  # EUR pro Düngung
    KOSTEN_SCHAEDLINGE: int = 1_500  # EUR pro Bekämpfung

    def __init__(self, region: Region) -> None:
        """Erstellt einen leeren Weinberg in der gewählten Region."""
        self.region: Region = region
        self.traube: Optional[Traube] = None  # noch leer
        self.reben_alter: int = 0
        self.pflegezustand: int = 50  # Start: 50%
        self.geduengt: bool = False
        self.schaedlingsbefall: bool = False
        self.ernte_bereit: bool = False

    # ── Darstellung ──────────────────────────────────────────────────────────

    def __str__(self) -> str:
        """Übersichtliche Darstellung des Weinbergs."""
        traube_str = self.traube.sorte.value if self.traube else "Noch nicht bepflanzt"
        schaedling_str = "⚠ JA – bekämpfen!" if self.schaedlingsbefall else "Nein"
        ernte_str = "✓ Ja" if self.ernte_bereit else "Noch nicht"

        return (
            f"\n  +------ Weinberg-Status -------------------+\n"
            f"  | Region        : {self.region.name.value}\n"
            f"  | Rebsorte      : {traube_str}\n"
            f"  | Reben-Alter   : {self.reben_alter} Jahr(e)\n"
            f"  | Pflegezustand : {self.pflegezustand}%\n"
            f"  | Gedüngt       : {'Ja' if self.geduengt else 'Nein'}\n"
            f"  | Schädlinge    : {schaedling_str}\n"
            f"  | Erntereif     : {ernte_str}\n"
            f"  +------------------------------------------+"
        )

    # ── Aktionen ─────────────────────────────────────────────────────────────

    def anpflanzen(self, traube: Traube) -> bool:
        """
        Pflanzt eine Rebsorte in den Weinberg.

        Nur möglich wenn:
        - Weinberg noch leer ist
        - Traube für die Region geeignet ist (Eignung > 0)

        Args:
            traube: Die einzupflanzende Rebsorte

        Returns:
            True wenn erfolgreich, False wenn nicht möglich
        """
        # Bereits bepflanzt?
        if self.traube is not None:
            print("  ⚠ Der Weinberg ist bereits bepflanzt!")
            return False

        # Eignung prüfen
        eignung = traube.get_eignung(self.region.name.value)
        if eignung == 0:
            print(
                f"  ⚠ {traube.sorte.value} ist für "
                f"{self.region.name.value} nicht geeignet!"
            )
            return False

        # Anpflanzen
        self.traube = traube
        self.reben_alter = 0
        self.pflegezustand = 50

        # Eignung als Feedback anzeigen
        sterne = "★" * eignung + "☆" * (3 - eignung)
        print(f"\n  ✓ {traube.sorte.value} wurde angepflanzt!")
        print(f"  Eignung für {self.region.name.value}: {sterne}")
        return True

    def duengen(self) -> bool:
        """
        Düngt den Weinberg – verbessert den Pflegezustand.

        Kosten: 1.000 EUR
        Effekt: Pflegezustand +15%

        Returns:
            True wenn erfolgreich
        """
        if self.traube is None:
            print("  ⚠ Erst Reben anpflanzen, dann düngen!")
            return False

        if self.geduengt:
            print("  ⚠ Wurde diese Runde bereits gedüngt!")
            return False

        # Pflegezustand verbessern (max. 100%)
        self.pflegezustand = min(100, self.pflegezustand + 15)
        self.geduengt = True
        print(f"  ✓ Gedüngt! Pflegezustand: {self.pflegezustand}%")
        return True

    def schaedlinge_bekaempfen(self) -> bool:
        """
        Bekämpft einen Schädlingsbefall.

        Kosten: 1.500 EUR
        Effekt: Schädlingsbefall wird beseitigt,
                Pflegezustand +10%

        Returns:
            True wenn Schädlinge bekämpft, False wenn kein Befall
        """
        if not self.schaedlingsbefall:
            print("  Kein Schädlingsbefall vorhanden.")
            return False

        self.schaedlingsbefall = False
        self.pflegezustand = min(100, self.pflegezustand + 10)
        print("  ✓ Schädlinge bekämpft!")
        print(f"  Pflegezustand jetzt: {self.pflegezustand}%")
        return True

    # ── Jahreszeiten-Logik ───────────────────────────────────────────────────

    def runde_abschliessen(
        self, jahreszeit: Jahreszeit, wetter: Wetterereignis
    ) -> None:
        """
        Verarbeitet das Ende einer Runde:
        - Reben altern
        - Pflegezustand sinkt
        - Zufälliger Schädlingsbefall möglich
        - Erntereife im Herbst prüfen

        Args:
            jahreszeit : Die aktuelle Jahreszeit
            wetter     : Das aktuelle Wetterereignis
        """
        import random

        if self.traube is None:
            return  # Leerer Weinberg – nichts zu tun

        # Reben werden älter
        if jahreszeit == Jahreszeit.WINTER:
            self.reben_alter += 1
            print(f"  Die Reben sind jetzt {self.reben_alter} Jahr(e) alt.")

        # Pflegezustand sinkt pro Runde
        self.pflegezustand = max(0, self.pflegezustand - 10)

        # Düngung zurücksetzen für nächste Runde
        self.geduengt = False

        # Frost-Schaden im Frühling (junge Reben gefährdet)
        if (
            jahreszeit == Jahreszeit.FRUEHLING
            and wetter.ist_frost
            and self.reben_alter == 0
        ):
            self.pflegezustand = max(0, self.pflegezustand - 20)
            print("  ⚠ Spätfrost hat junge Reben geschädigt! " "-20% Pflegezustand")

        # Zufälliger Schädlingsbefall (10% Wahrscheinlichkeit)
        if random.random() < 0.10:
            self.schaedlingsbefall = True
            print("  ⚠ Schädlingsbefall entdeckt! " "Bekämpfung empfohlen.")

        # Erntereife im Herbst prüfen
        if jahreszeit == Jahreszeit.HERBST:
            self.ernte_bereit = True

    # ── Öchsle-Berechnung ────────────────────────────────────────────────────

    def get_oechsle(self, wetter_bonus: int) -> int:
        """
        Berechnet den Öchsle-Grad der Trauben.

        Die Formel berücksichtigt 4 Faktoren:
        1. Basis-Öchsle der Rebsorte
        2. Regions-Bonus (Eignung der Traube für die Region)
        3. Pflege-Bonus (Pflegezustand des Weinbergs)
        4. Wetter-Bonus (aktuelles Wetterereignis)

        Args:
            wetter_bonus: Öchsle-Einfluss des Wetters

        Returns:
            int: Berechneter Öchsle-Grad (mindestens 40°)
        """
        if self.traube is None:
            return 0

        # ── Faktor 1: Basis-Öchsle der Rebsorte ──────────────────
        oechsle = self.traube.basis_oechsle

        # ── Faktor 2: Regions-Bonus ───────────────────────────────
        # Eignung 0–3 Sterne × 3 = bis zu +9°
        eignung = self.traube.get_eignung(self.region.name.value)
        regions_bonus = eignung * 3
        oechsle += regions_bonus

        # ── Faktor 3: Pflege-Bonus ────────────────────────────────
        # Pflegezustand 0–100% → bis zu +10°
        pflege_bonus = self.pflegezustand // 10
        oechsle += pflege_bonus

        # ── Faktor 4: Wetter-Bonus ────────────────────────────────
        oechsle += wetter_bonus

        # Reben-Alter: junge Reben (< 3 Jahre) haben Abzug
        if self.reben_alter < 3:
            oechsle -= (3 - self.reben_alter) * 3
            # Alter 0 → -9°, Alter 1 → -6°, Alter 2 → -3°

        # Schädlingsbefall: Abzug wenn nicht bekämpft
        if self.schaedlingsbefall:
            oechsle -= 10
            print("  ⚠ Schädlinge haben die Trauben geschwächt! -10°")

        # Minimum: 40° (Wein bleibt immer noch Wein)
        return max(oechsle, 40)

    def oechsle_anzeigen(self, wetter_bonus: int) -> None:
        """
        Zeigt die Öchsle-Berechnung Schritt für Schritt an.
        Sehr gut für den Unterricht geeignet!
        """
        if self.traube is None:
            print("  Kein Weinberg bepflanzt.")
            return

        eignung = self.traube.get_eignung(self.region.name.value)
        regions_bonus = eignung * 3
        pflege_bonus = self.pflegezustand // 10
        alter_abzug = max(0, (3 - self.reben_alter) * 3)
        schaedling_abzug = 10 if self.schaedlingsbefall else 0

        print(f"\n  ┌─── Öchsle-Berechnung ────────────────────┐")
        print(
            f"  │ Basis ({self.traube.sorte.value:<18})  : "
            f"{self.traube.basis_oechsle:>4}°"
        )
        print(
            f"  │ + Regions-Bonus (Eignung {eignung}★×3)    : " f"+{regions_bonus:>3}°"
        )
        print(
            f"  │ + Pflege-Bonus  ({self.pflegezustand}%÷10)        : "
            f"+{pflege_bonus:>3}°"
        )
        v = "+" if wetter_bonus >= 0 else ""
        print(f"  │ + Wetter-Bonus                      : " f"{v}{wetter_bonus:>3}°")
        if alter_abzug > 0:
            print(
                f"  │ - Jungreben-Abzug ({self.reben_alter} Jahr(e))     : "
                f"-{alter_abzug:>3}°"
            )
        if schaedling_abzug > 0:
            print(
                f"  │ - Schädlingsbefall                  : " f"-{schaedling_abzug:>3}°"
            )
        gesamt = self.get_oechsle(wetter_bonus)
        print(f"  ├───────────────────────────────────────────┤")
        print(f"  │ ERGEBNIS                            : " f"{gesamt:>4}°")
        print(f"  └───────────────────────────────────────────┘")

    # ── Serialisierung ───────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        """Wandelt den Weinberg in ein Dictionary um."""
        return {
            "region": self.region.to_dict(),
            "traube": self.traube.to_dict() if self.traube else None,
            "reben_alter": self.reben_alter,
            "pflegezustand": self.pflegezustand,
            "geduengt": self.geduengt,
            "schaedlingsbefall": self.schaedlingsbefall,
            "ernte_bereit": self.ernte_bereit,
        }

    @classmethod
    def from_dict(cls, daten: dict) -> "Weinberg":
        """Erstellt einen Weinberg aus einem Dictionary."""
        from region import Region

        region = Region.from_dict(daten["region"])
        weinberg = cls(region=region)
        weinberg.reben_alter = daten["reben_alter"]
        weinberg.pflegezustand = daten["pflegezustand"]
        weinberg.geduengt = daten["geduengt"]
        weinberg.schaedlingsbefall = daten["schaedlingsbefall"]
        weinberg.ernte_bereit = daten["ernte_bereit"]
        if daten["traube"]:
            weinberg.traube = Traube.from_dict(daten["traube"])
        return weinberg


# ─────────────────────────────────────────────────────────────────────────────
# Self-Test: wird nur ausgeführt wenn vineyard.py direkt
# gestartet wird (nicht wenn es importiert wird)
# ─────────────────────────────────────────────────────────────────────────────
def main():
    """
    Testfunktion für den Weinberg.
    Simuliert einen kompletten Spielzug eines Spielers.
    """
    from region import REGIONEN, RegionName
    from grape import TRAUBEN, Rebsorte
    from weather import wetter_wuerfeln, jahreszeit_berechnen, jahreszeit_anzeigen

    print("=" * 52)
    print("  WEINBERG – Self-Test")
    print("=" * 52)

    # ── Schritt 1: Region wählen ──────────────────────────
    print("\n  Schritt 1: Region wird gesetzt → Mosel")
    region = REGIONEN[RegionName.MOSEL]
    weinberg = Weinberg(region=region)
    print(weinberg)

    # ── Schritt 2: Reben anpflanzen ───────────────────────
    print("\n  Schritt 2: Riesling anpflanzen")
    riesling = TRAUBEN[Rebsorte.RIESLING]
    weinberg.anpflanzen(riesling)
    print(weinberg)

    # ── Schritt 3: Falsche Sorte testen ───────────────────
    print("\n  Schritt 3: Trollinger in Mosel anpflanzen")
    print("  (Sollte fehlschlagen – Trollinger passt nicht!)")
    trollinger = TRAUBEN[Rebsorte.TROLLINGER]
    weinberg.anpflanzen(trollinger)

    # ── Schritt 4: Düngen ─────────────────────────────────
    print("\n  Schritt 4: Weinberg düngen")
    weinberg.duengen()
    print(f"  Pflegezustand nach Düngung: {weinberg.pflegezustand}%")

    # ── Schritt 5: Nochmal düngen (sollte Warnung geben) ──
    print("\n  Schritt 5: Nochmals düngen (sollte Warnung geben)")
    weinberg.duengen()

    # ── Schritt 6: Wetter würfeln (3 Runden simulieren) ───
    print("\n  Schritt 6: 3 Runden mit Wetter simulieren")
    print("  " + "─" * 46)

    for runde in range(1, 4):
        jahreszeit = jahreszeit_berechnen(runde)
        jahreszeit_anzeigen(jahreszeit, runde)
        wetter = wetter_wuerfeln(jahreszeit)
        print(wetter)

        # Öchsle berechnen und anzeigen
        weinberg.oechsle_anzeigen(wetter.oechsle_bonus)

        # Runde abschließen
        weinberg.runde_abschliessen(jahreszeit, wetter)

    # ── Schritt 7: Herbst simulieren (Erntereife!) ────────
    print("\n  Schritt 7: Herbst – Erntereife prüfen")
    from weather import Wetterzustand, WETTER_EREIGNISSE, Jahreszeit

    herbst = Jahreszeit.HERBST
    gutes_wetter = WETTER_EREIGNISSE[Wetterzustand.IDEAL]

    jahreszeit_anzeigen(herbst, 3)
    print(gutes_wetter)
    weinberg.runde_abschliessen(herbst, gutes_wetter)
    print(f"\n  Erntereif: {weinberg.ernte_bereit}")

    # ── Schritt 8: Öchsle-Endergebnis ─────────────────────
    print("\n  Schritt 8: Finale Öchsle-Berechnung")
    weinberg.oechsle_anzeigen(gutes_wetter.oechsle_bonus)

    # ── Schritt 9: Schädlingsbefall simulieren ────────────
    print("\n  Schritt 9: Schädlingsbefall simulieren")
    weinberg.schaedlingsbefall = True  # manuell setzen
    print(weinberg)
    print("\n  Schädlinge bekämpfen:")
    weinberg.schaedlinge_bekaempfen()
    print(weinberg)

    # ── Schritt 10: Serialisierung testen ─────────────────
    print("\n  Schritt 10: Serialisierung testen")
    print("  (to_dict → from_dict → wieder ein Weinberg)")
    daten = weinberg.to_dict()
    weinberg2 = Weinberg.from_dict(daten)
    print(
        f"  Original : {weinberg.traube.sorte.value}, "  # type: ignore
        f"Pflege {weinberg.pflegezustand}%"
    )
    print(
        f"  Geladen  : {weinberg2.traube.sorte.value}, "  # type: ignore
        f"Pflege {weinberg2.pflegezustand}%"
    )
    gleich = (
        weinberg.pflegezustand == weinberg2.pflegezustand
        and weinberg.traube.sorte == weinberg2.traube.sorte  # type: ignore
    )
    print(f"  Identisch: {'✓ Ja' if gleich else '✗ Nein'}")

    print("\n" + "=" * 52)
    print("  Self-Test abgeschlossen!")
    print("=" * 52)


if __name__ == "__main__":
    main()
