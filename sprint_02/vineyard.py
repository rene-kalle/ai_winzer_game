"""
vineyard.py – Weinberg-Modul
=============================
Repräsentiert den Weinberg eines Spielers.
Hier werden Reben angepflanzt, gepflegt und
die Traubenqualität berechnet.

Änderungen gegenüber vorheriger Version:
  - Kein Jungreben-Abzug mehr pro Runde
  - Stattdessen: Reife-Faktor skaliert den Pflege-Bonus
    Alter 0 → 60%, Alter 1 → 80%, Alter 2 → 90%, Alter 3+ → 100%
  - Realistischer und fairer für neue Spieler

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
        region            : Das Anbaugebiet des Weinbergs
        traube            : Eingepflanzte Rebsorte (None = leer)
        reben_alter       : Alter der Reben in Jahren
        pflegezustand     : Pflegequalität 0–100%
        geduengt          : Ob in dieser Runde gedüngt wurde
        schaedlingsbefall : Ob Schädlingsbefall vorliegt
        ernte_bereit      : Ob Trauben erntereif sind
        oechsle_aktuell   : Kumulativer Öchsle-Wert der Saison

    Reife-Faktor (skaliert den Pflege-Bonus):
        0 Jahre →  60%
        1 Jahr  →  80%
        2 Jahre →  90%
        3 Jahre → 100%
    """

    # Kosten für Aktionen (Klassenvariablen)
    KOSTEN_ANPFLANZEN: int = 5_000
    KOSTEN_DUENGER: int = 1_000
    KOSTEN_SCHAEDLINGE: int = 1_500

    # Reife-Faktoren je Reben-Alter
    # Schlüssel = Alter in Jahren, Wert = Faktor als Float
    REIFE_FAKTOREN = {
        0: 0.6,  # 60%  – Jungpflanze, noch nicht voll leistungsfähig
        1: 0.8,  # 80%  – zweites Jahr, deutlich besser
        2: 0.9,  # 90%  – fast ausgewachsen
    }
    REIFE_FAKTOR_VOLL = 1.0  # 100% ab dem 3. Jahr

    def __init__(self, region: Region) -> None:
        """Erstellt einen leeren Weinberg in der gewählten Region."""
        self.region: Region = region
        self.traube: Optional[Traube] = None
        self.reben_alter: int = 0
        self.pflegezustand: int = 50
        self.geduengt: bool = False
        self.schaedlingsbefall: bool = False
        self.ernte_bereit: bool = False
        self.oechsle_aktuell: int = 0

    # ── Hilfsmethode: Reife-Faktor ───────────────────────────────────────────

    def get_reife_faktor(self) -> float:
        """
        Gibt den Reife-Faktor für das aktuelle Reben-Alter zurück.

        Junge Reben bringen noch nicht die volle Leistung.
        Der Faktor skaliert den Pflege-Bonus in runde_abschliessen().

        Returns:
            float: Reife-Faktor zwischen 0.6 und 1.0
        """
        return self.REIFE_FAKTOREN.get(
            self.reben_alter, self.REIFE_FAKTOR_VOLL  # Standard ab 3 Jahren
        )

    # ── Darstellung ──────────────────────────────────────────────────────────

    def __str__(self) -> str:
        """Übersichtliche Darstellung des Weinbergs."""
        traube_str = self.traube.sorte.value if self.traube else "Noch nicht bepflanzt"
        schaedling_str = "⚠ JA – bekämpfen!" if self.schaedlingsbefall else "Nein"
        ernte_str = "✓ Ja" if self.ernte_bereit else "Noch nicht"
        reife_str = f"{self.get_reife_faktor():.0%}"

        return (
            f"\n  +------ Weinberg-Status --------------------+\n"
            f"  | Region        : {self.region.name.value}\n"
            f"  | Rebsorte      : {traube_str}\n"
            f"  | Reben-Alter   : {self.reben_alter} Jahr(e)\n"
            f"  | Reife         : {reife_str}\n"
            f"  | Pflegezustand : {self.pflegezustand}%\n"
            f"  | Gedüngt       : {'Ja' if self.geduengt else 'Nein'}\n"
            f"  | Schädlinge    : {schaedling_str}\n"
            f"  | Erntereif     : {ernte_str}\n"
            f"  | Öchsle aktuell: {self.oechsle_aktuell}°\n"
            f"  +-------------------------------------------+"
        )

    # ── Aktionen ─────────────────────────────────────────────────────────────

    def anpflanzen(self, traube: Traube) -> bool:
        """
        Pflanzt eine Rebsorte in den Weinberg.

        Setzt den Start-Öchsle-Wert:
          basis_oechsle + regions_bonus

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

        # Reben einpflanzen
        self.traube = traube
        self.reben_alter = 0
        self.pflegezustand = 50

        # Start-Öchsle: Basis + Regions-Bonus
        regions_bonus = eignung * 3
        self.oechsle_aktuell = traube.basis_oechsle + regions_bonus

        sterne = "★" * eignung + "☆" * (3 - eignung)
        print(f"\n  ✓ {traube.sorte.value} wurde angepflanzt!")
        print(f"  Eignung für {self.region.name.value}: {sterne}")
        print(
            f"  Start-Öchsle: {traube.basis_oechsle}°"
            f" + Regions-Bonus {regions_bonus}°"
            f" = {self.oechsle_aktuell}°"
        )
        print(
            f"  Reife-Faktor: {self.get_reife_faktor():.0%} " f"(Reben sind noch jung)"
        )
        return True

    def duengen(self) -> bool:
        """
        Düngt den Weinberg.

        Effekt: Pflegezustand +15%
                Der Pflege-Bonus fließt gewichtet
                mit dem Reife-Faktor in Öchsle ein.

        Returns:
            True wenn erfolgreich
        """
        if self.traube is None:
            print("  ⚠ Erst Reben anpflanzen, dann düngen!")
            return False

        if self.geduengt:
            print("  ⚠ Wurde diese Runde bereits gedüngt!")
            return False

        self.pflegezustand = min(100, self.pflegezustand + 15)
        self.geduengt = True
        print(f"  ✓ Gedüngt! Pflegezustand: {self.pflegezustand}%")
        return True

    def schaedlinge_bekaempfen(self) -> bool:
        """
        Bekämpft einen Schädlingsbefall.

        Effekt: Schädlingsbefall wird beseitigt,
                Pflegezustand +10%

        Returns:
            True wenn Schädlinge bekämpft
        """
        if not self.schaedlingsbefall:
            print("  Kein Schädlingsbefall vorhanden.")
            return False

        self.schaedlingsbefall = False
        self.pflegezustand = min(100, self.pflegezustand + 10)
        print("  ✓ Schädlinge bekämpft!")
        print(f"  Pflegezustand jetzt: {self.pflegezustand}%")
        return True

    # ── Öchsle-Berechnung (kumulativ) ────────────────────────────────────────

    def runde_abschliessen(
        self, jahreszeit: Jahreszeit, wetter: Wetterereignis
    ) -> None:
        """
        Verarbeitet das Ende einer Runde.

        Öchsle wird KUMULATIV aufgebaut:
          1. Wetter-Bonus/Malus
          2. Pflege-Bonus × Reife-Faktor (nur wenn gedüngt)
          3. Schädlings-Malus
          4. Spätfrost-Malus (nur Frühling + Jungreben)

        Kein pauschaler Jungreben-Abzug mehr –
        stattdessen skaliert der Reife-Faktor
        den Pflege-Bonus nach unten.
        """
        import random

        if self.traube is None:
            return

        # Reife-Faktor für diese Runde ermitteln
        reife_faktor = self.get_reife_faktor()

        print(f"\n  ┌─── Öchsle-Entwicklung ─────────────────────┐")
        print(f"  │ Öchsle zu Beginn              : " f"{self.oechsle_aktuell:>4}°")
        print(
            f"  │ Reben-Reife ({self.reben_alter} Jahr(e))          : "
            f"  {reife_faktor:.0%}"
        )

        # ── 1. Wetter-Bonus/Malus ─────────────────────────────────
        self.oechsle_aktuell += wetter.oechsle_bonus
        v = "+" if wetter.oechsle_bonus >= 0 else ""
        print(
            f"  │ Wetter ({wetter.zustand.value:<20}): "
            f"{v}{wetter.oechsle_bonus:>3}°"
        )

        # ── 2. Pflege-Bonus × Reife-Faktor ───────────────────────
        # Nur wenn in dieser Runde gedüngt wurde
        if self.geduengt:
            basis_bonus = self.pflegezustand // 10
            pflege_bonus = int(basis_bonus * reife_faktor)
            self.oechsle_aktuell += pflege_bonus
            print(
                f"  │ Pflege ({self.pflegezustand}%÷10={basis_bonus}"
                f" × {reife_faktor:.0%})        : "
                f"+{pflege_bonus:>3}°"
            )

        # ── 3. Schädlings-Malus ───────────────────────────────────
        if self.schaedlingsbefall:
            self.oechsle_aktuell -= 10
            print(f"  │ Schädlingsbefall              :  -10°")

        # ── 4. Spätfrost-Malus (nur Frühling + Jungreben) ────────
        if (
            jahreszeit == Jahreszeit.FRUEHLING
            and wetter.ist_frost
            and self.reben_alter == 0
        ):
            self.oechsle_aktuell -= 15
            print(f"  │ Spätfrost (Jungreben)         :  -15°")

        # Minimum: 40°
        self.oechsle_aktuell = max(self.oechsle_aktuell, 40)

        print(f"  ├─────────────────────────────────────────────┤")
        print(f"  │ Öchsle nach dieser Runde      : " f"{self.oechsle_aktuell:>4}°")
        print(f"  └─────────────────────────────────────────────┘")

        # ── Pflegezustand sinkt pro Runde ─────────────────────────
        self.pflegezustand = max(0, self.pflegezustand - 10)
        self.geduengt = False

        # ── Reben altern im Winter ────────────────────────────────
        if jahreszeit == Jahreszeit.WINTER:
            self.reben_alter += 1
            neuer_faktor = self.get_reife_faktor()
            print(
                f"  Die Reben sind jetzt {self.reben_alter} "
                f"Jahr(e) alt "
                f"→ Reife-Faktor: {neuer_faktor:.0%}"
            )

        # ── Zufälliger Schädlingsbefall (10%) ─────────────────────
        if random.random() < 0.10:
            self.schaedlingsbefall = True
            print("  ⚠ Schädlingsbefall entdeckt! " "Bekämpfung empfohlen.")

        # ── Erntereife im Herbst ──────────────────────────────────
        if jahreszeit == Jahreszeit.HERBST:
            self.ernte_bereit = True
            print("  ✓ Die Trauben sind erntereif!")

    # ── Öchsle ausgeben ──────────────────────────────────────────────────────

    def get_oechsle(self) -> int:
        """
        Gibt den aktuellen Öchsle-Wert zurück.
        Wurde kumulativ durch runde_abschliessen() aufgebaut.
        """
        return self.oechsle_aktuell

    def oechsle_anzeigen(self) -> None:
        """Zeigt den aktuellen Öchsle-Wert übersichtlich an."""
        if self.traube is None:
            print("  Kein Weinberg bepflanzt.")
            return

        print(f"\n  Rebsorte        : {self.traube.sorte.value}")
        print(f"  Öchsle aktuell  : {self.oechsle_aktuell}°")
        print(f"  Pflegezustand   : {self.pflegezustand}%")
        print(f"  Reben-Alter     : {self.reben_alter} Jahr(e)")
        print(f"  Reife-Faktor    : {self.get_reife_faktor():.0%}")

    # ── Serialisierung ───────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        """Wandelt den Weinberg in ein Dictionary um."""
        return {
            "region": self.region.to_dict(),
            "traube": (self.traube.to_dict() if self.traube else None),
            "reben_alter": self.reben_alter,
            "pflegezustand": self.pflegezustand,
            "geduengt": self.geduengt,
            "schaedlingsbefall": self.schaedlingsbefall,
            "ernte_bereit": self.ernte_bereit,
            "oechsle_aktuell": self.oechsle_aktuell,
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
        weinberg.oechsle_aktuell = daten.get("oechsle_aktuell", 0)
        if daten["traube"]:
            weinberg.traube = Traube.from_dict(daten["traube"])
        return weinberg


# ─────────────────────────────────────────────────────────────────────────────
# Self-Test
# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    """
    Testet den Weinberg mit dem neuen Reife-Faktor-System.
    Simuliert 2 komplette Jahre (8 Runden):
      Jahr 1: Frühling → Sommer → Herbst → Winter
      Jahr 2: Frühling → Sommer → Herbst → Winter
    """
    from region import REGIONEN, RegionName
    from grape import TRAUBEN, Rebsorte
    from weather import (
        wetter_wuerfeln,
        jahreszeit_berechnen,
        jahreszeit_anzeigen,
        Wetterzustand,
        WETTER_EREIGNISSE,
    )

    print("=" * 54)
    print("  WEINBERG – Self-Test (Reife-Faktor)")
    print("=" * 54)

    # ── Setup ─────────────────────────────────────────────
    region = REGIONEN[RegionName.MOSEL]
    weinberg = Weinberg(region=region)
    riesling = TRAUBEN[Rebsorte.RIESLING]
    weinberg.anpflanzen(riesling)
    print(weinberg)

    # ── 2 Jahre simulieren (8 Runden) ────────────────────
    # Feste Wetter für reproduzierbare Ergebnisse
    test_wetter = [
        Wetterzustand.NORMAL,  # Jahr 1 Frühling
        Wetterzustand.IDEAL,  # Jahr 1 Sommer
        Wetterzustand.NORMAL,  # Jahr 1 Herbst
        Wetterzustand.FROST,  # Jahr 1 Winter
        Wetterzustand.NORMAL,  # Jahr 2 Frühling
        Wetterzustand.IDEAL,  # Jahr 2 Sommer
        Wetterzustand.IDEAL,  # Jahr 2 Herbst
        Wetterzustand.FROST,  # Jahr 2 Winter
    ]

    for runde in range(1, 9):
        jahreszeit = jahreszeit_berechnen(runde)
        jahreszeit_anzeigen(jahreszeit, runde)

        # Düngen in Frühling und Sommer
        if jahreszeit in (Jahreszeit.FRUEHLING, Jahreszeit.SOMMER):
            weinberg.duengen()

        # Festes Testwetter verwenden
        wetter = WETTER_EREIGNISSE[test_wetter[runde - 1]]
        print(
            f"\n  Wetter: {wetter.zustand.value} "
            f"({'+' if wetter.oechsle_bonus >= 0 else ''}"
            f"{wetter.oechsle_bonus}°)"
        )

        weinberg.runde_abschliessen(jahreszeit, wetter)

        # Nach Herbst: Qualität anzeigen
        if jahreszeit == Jahreszeit.HERBST:
            oechsle = weinberg.get_oechsle()
            print(f"\n  ─── Ernte-Ergebnis Jahr " f"{'1' if runde <= 4 else '2'} ───")
            weinberg.oechsle_anzeigen()

            # Qualitätsstufe bestimmen
            if oechsle >= 150:
                q = "Trockenbeerenauslese 🏆"
            elif oechsle >= 110:
                q = "Beerenauslese / Eiswein 🥇"
            elif oechsle >= 90:
                q = "Auslese 🥈"
            elif oechsle >= 76:
                q = "Spätlese 🥉"
            elif oechsle >= 63:
                q = "Qualitätswein (QbA)"
            elif oechsle >= 57:
                q = "Landwein"
            else:
                q = "Tafelwein"
            print(f"  Qualität: {q}")

    # ── Reife-Faktor Vergleich anzeigen ───────────────────
    print("\n" + "=" * 54)
    print("  Reife-Faktor Übersicht:")
    print("  " + "─" * 40)
    print(f"  {'Alter':<10} {'Faktor':<10} {'Pflege-Bonus (10)'}")
    print("  " + "─" * 40)
    for alter, faktor in Weinberg.REIFE_FAKTOREN.items():
        bonus = int(10 * faktor)
        balken = "█" * bonus
        print(f"  {alter} Jahr(e)  " f"{faktor:.0%}        " f"+{bonus}°  {balken}")
    bonus_voll = int(10 * Weinberg.REIFE_FAKTOR_VOLL)
    balken_voll = "█" * bonus_voll
    print(
        f"  3+ Jahr(e) "
        f"{Weinberg.REIFE_FAKTOR_VOLL:.0%}       "
        f"+{bonus_voll}°  {balken_voll}"
    )

    # ── Serialisierung testen ─────────────────────────────
    print("\n" + "=" * 54)
    print("  Serialisierung testen:")
    daten = weinberg.to_dict()
    weinberg2 = Weinberg.from_dict(daten)
    gleich = (
        weinberg.oechsle_aktuell == weinberg2.oechsle_aktuell
        and weinberg.reben_alter == weinberg2.reben_alter
        and weinberg.traube.sorte == weinberg2.traube.sorte
    )
    print(
        f"  Original : {weinberg.traube.sorte.value}, "
        f"{weinberg.oechsle_aktuell}°, "
        f"Alter {weinberg.reben_alter} Jahr(e)"
    )
    print(
        f"  Geladen  : {weinberg2.traube.sorte.value}, "
        f"{weinberg2.oechsle_aktuell}°, "
        f"Alter {weinberg2.reben_alter} Jahr(e)"
    )
    print(f"  Identisch: {'✓ Ja' if gleich else '✗ Nein'}")

    print("\n" + "=" * 54)
    print("  Self-Test abgeschlossen!")
    print("=" * 54)


if __name__ == "__main__":
    main()
