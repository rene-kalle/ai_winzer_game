"""
vineyard.py – Weinberg-Modul
=============================
Repräsentiert den Weinberg eines Spielers.
Hier werden Reben angepflanzt, gepflegt und
die Traubenqualität berechnet.

Wichtige Änderung gegenüber erster Version:
  Der Öchsle-Wert wird KUMULATIV aufgebaut –
  jede Runde kommen Boni/Mali auf den
  bestehenden Wert obendrauf.

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
    """

    # Kosten für Aktionen (Klassenvariablen)
    KOSTEN_ANPFLANZEN: int = 5_000
    KOSTEN_DUENGER: int = 1_000
    KOSTEN_SCHAEDLINGE: int = 1_500

    def __init__(self, region: Region) -> None:
        """Erstellt einen leeren Weinberg in der gewählten Region."""
        self.region: Region = region
        self.traube: Optional[Traube] = None
        self.reben_alter: int = 0
        self.pflegezustand: int = 50
        self.geduengt: bool = False
        self.schaedlingsbefall: bool = False
        self.ernte_bereit: bool = False

        # NEU: Öchsle wächst kumulativ über die Saison
        self.oechsle_aktuell: int = 0

    # ── Darstellung ──────────────────────────────────────────────────────────

    def __str__(self) -> str:
        """Übersichtliche Darstellung des Weinbergs."""
        traube_str = self.traube.sorte.value if self.traube else "Noch nicht bepflanzt"
        schaedling_str = "⚠ JA – bekämpfen!" if self.schaedlingsbefall else "Nein"
        ernte_str = "✓ Ja" if self.ernte_bereit else "Noch nicht"

        return (
            f"\n  +------ Weinberg-Status --------------------+\n"
            f"  | Region        : {self.region.name.value}\n"
            f"  | Rebsorte      : {traube_str}\n"
            f"  | Reben-Alter   : {self.reben_alter} Jahr(e)\n"
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

        Setzt den Start-Öchsle-Wert aus:
          basis_oechsle + regions_bonus

        Returns:
            True wenn erfolgreich, False wenn nicht möglich
        """
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

        # NEU: Startwert kumulativ setzen
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
        return True

    def duengen(self) -> bool:
        """
        Düngt den Weinberg.

        Effekt: Pflegezustand +15%
                Der Pflege-Bonus fließt in
                runde_abschliessen() in Öchsle ein.

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

        Der Öchsle-Wert wird KUMULATIV aufgebaut:
        Jede Runde werden nur die Deltas
        (Wetter, Pflege, Schädlinge) addiert –
        der bisherige Wert bleibt erhalten!

        Reihenfolge der Berechnung:
          1. Wetter-Bonus/Malus
          2. Pflege-Bonus (nur wenn gedüngt)
          3. Schädlings-Malus
          4. Spätfrost-Malus (Frühling + Jungreben)
          5. Jungreben-Abzug
        """
        import random

        if self.traube is None:
            return

        print(f"\n  ┌─── Öchsle-Entwicklung ────────────────────┐")
        print(f"  │ Öchsle zu Beginn dieser Runde  : " f"{self.oechsle_aktuell:>4}°")

        # ── 1. Wetter ─────────────────────────────────────────────
        self.oechsle_aktuell += wetter.oechsle_bonus
        v = "+" if wetter.oechsle_bonus >= 0 else ""
        print(
            f"  │ Wetter ({wetter.zustand.value:<18})  : "
            f"{v}{wetter.oechsle_bonus:>3}°"
        )

        # ── 2. Pflege-Bonus (nur wenn gedüngt) ────────────────────
        # if self.geduengt:
        #     pflege_bonus = self.pflegezustand // 10
        #     self.oechsle_aktuell += pflege_bonus
        #     print(
        #         f"  │ Pflege-Bonus (gedüngt, {self.pflegezustand}%÷10)  : "
        #         f"+{pflege_bonus:>3}°"
        #     )
        # ── Reife-Faktor je Reben-Alter berechnen ─────────────────
        # Junge Reben bringen noch nicht die volle Leistung
        if self.reben_alter == 0:
            reife_faktor = 0.6  # 60%  – Jungpflanze
        elif self.reben_alter == 1:
            reife_faktor = 0.8  # 80%  – noch jung
        elif self.reben_alter == 2:
            reife_faktor = 0.9  # 90%  – fast ausgewachsen
        else:
            reife_faktor = 1.0  # 100% – volle Leistung

        print(
            f"  │ Reben-Reife ({self.reben_alter} Jahr(e))           : "
            f"  {reife_faktor:.0%}"
        )

        # ── Pflege-Bonus (nur wenn gedüngt, skaliert mit Reife) ───
        if self.geduengt:
            pflege_bonus = int((self.pflegezustand // 10) * reife_faktor)
            self.oechsle_aktuell += pflege_bonus
            print(
                f"  │ Pflege-Bonus ({self.pflegezustand}%÷10 × Reife)    : "
                f"+{pflege_bonus:>3}°"
            )

        # ── 3. Schädlings-Malus ───────────────────────────────────
        if self.schaedlingsbefall:
            self.oechsle_aktuell -= 10
            print(f"  │ Schädlingsbefall                    :  -10°")

        # ── 4. Spätfrost-Malus (Frühling + Jungreben) ────────────
        if (
            jahreszeit == Jahreszeit.FRUEHLING
            and wetter.ist_frost
            and self.reben_alter == 0
        ):
            self.oechsle_aktuell -= 20
            print(f"  │ Spätfrost (Jungreben)               :  -20°")

        # ── 5. Jungreben-Abzug (Reben < 3 Jahre) ─────────────────
        # if self.reben_alter < 3:
        #     abzug = (3 - self.reben_alter) * 3
        #     self.oechsle_aktuell -= abzug
        #     print(
        #         f"  │ Jungreben-Abzug ({self.reben_alter} Jahr(e))        :  "
        #         f"-{abzug:>2}°"
        #     )

        # Minimum: 40°
        self.oechsle_aktuell = max(self.oechsle_aktuell, 40)

        print(f"  ├───────────────────────────────────────────┤")
        print(f"  │ Öchsle nach dieser Runde       : " f"{self.oechsle_aktuell:>4}°")
        print(f"  └───────────────────────────────────────────┘")

        # ── Pflegezustand sinkt pro Runde ─────────────────────────
        self.pflegezustand = max(0, self.pflegezustand - 10)
        self.geduengt = False

        # ── Reben altern im Winter ────────────────────────────────
        if jahreszeit == Jahreszeit.WINTER:
            self.reben_alter += 1
            print(f"  Die Reben sind jetzt " f"{self.reben_alter} Jahr(e) alt.")

        # ── Zufälliger Schädlingsbefall (10%) ─────────────────────
        if random.random() < 0.10:
            self.schaedlingsbefall = True
            print("  ⚠ Schädlingsbefall entdeckt! " "Bekämpfung empfohlen.")

        # ── Erntereife im Herbst ──────────────────────────────────
        if jahreszeit == Jahreszeit.HERBST:
            self.ernte_bereit = True
            print("  ✓ Die Trauben sind erntereif!")

    def get_oechsle(self) -> int:
        """
        Gibt den aktuellen Öchsle-Wert zurück.

        Dieser wurde bereits kumulativ durch
        runde_abschliessen() aufgebaut –
        einfach auslesen!
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
            "oechsle_aktuell": self.oechsle_aktuell,  # NEU
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
    Testet den Weinberg Schritt für Schritt.
    Simuliert eine komplette Saison:
    Frühling → Sommer → Herbst
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

    print("=" * 52)
    print("  WEINBERG – Self-Test (kumulative Öchsle)")
    print("=" * 52)

    # ── Schritt 1: Weinberg anlegen ───────────────────────
    print("\n  Schritt 1: Weinberg in der Mosel anlegen")
    region = REGIONEN[RegionName.MOSEL]
    weinberg = Weinberg(region=region)
    print(weinberg)

    # ── Schritt 2: Riesling anpflanzen ───────────────────
    print("\n  Schritt 2: Riesling anpflanzen")
    riesling = TRAUBEN[Rebsorte.RIESLING]
    weinberg.anpflanzen(riesling)

    # ── Schritt 3: Falsche Sorte testen ──────────────────
    print("\n  Schritt 3: Trollinger anpflanzen (muss scheitern)")
    trollinger = TRAUBEN[Rebsorte.TROLLINGER]
    weinberg.anpflanzen(trollinger)

    # ── Schritt 4: Frühling ───────────────────────────────
    print("\n  Schritt 4: Frühling")
    jahreszeit = jahreszeit_berechnen(1)
    jahreszeit_anzeigen(jahreszeit, 1)
    weinberg.duengen()
    wetter = wetter_wuerfeln(jahreszeit)
    print(f"\n  {wetter}")
    weinberg.runde_abschliessen(jahreszeit, wetter)

    # ── Schritt 5: Sommer ─────────────────────────────────
    print("\n  Schritt 5: Sommer")
    jahreszeit = jahreszeit_berechnen(2)
    jahreszeit_anzeigen(jahreszeit, 2)
    weinberg.duengen()
    wetter = wetter_wuerfeln(jahreszeit)
    print(f"\n  {wetter}")
    weinberg.runde_abschliessen(jahreszeit, wetter)

    # ── Schritt 6: Herbst (mit fixem Wetter zum Vergleich)
    print("\n  Schritt 6: Herbst – Ernte!")
    jahreszeit = jahreszeit_berechnen(3)
    jahreszeit_anzeigen(jahreszeit, 3)
    # Festes Wetter für reproduzierbaren Test
    wetter = WETTER_EREIGNISSE[Wetterzustand.IDEAL]
    print(f"\n  {wetter}")
    weinberg.runde_abschliessen(jahreszeit, wetter)

    # ── Schritt 7: Ergebnis anzeigen ──────────────────────
    print("\n  Schritt 7: Finale Öchsle-Auswertung")
    weinberg.oechsle_anzeigen()

    # Qualitätsstufe bestimmen
    oechsle = weinberg.get_oechsle()
    if oechsle >= 150:
        qualitaet = "Trockenbeerenauslese"
    elif oechsle >= 110:
        qualitaet = "Beerenauslese / Eiswein"
    elif oechsle >= 90:
        qualitaet = "Auslese"
    elif oechsle >= 76:
        qualitaet = "Spätlese"
    elif oechsle >= 63:
        qualitaet = "Qualitätswein (QbA)"
    elif oechsle >= 57:
        qualitaet = "Landwein"
    else:
        qualitaet = "Tafelwein"
    print(f"\n  Qualitätsstufe: {qualitaet} ({oechsle}°)")

    # ── Schritt 8: Schädlingsbefall simulieren ────────────
    print("\n  Schritt 8: Schädlingsbefall simulieren")
    weinberg.schaedlingsbefall = True
    weinberg.schaedlinge_bekaempfen()

    # ── Schritt 9: Serialisierung testen ──────────────────
    print("\n  Schritt 9: Speichern & Laden testen")
    daten = weinberg.to_dict()
    weinberg2 = Weinberg.from_dict(daten)
    gleich = (
        weinberg.oechsle_aktuell == weinberg2.oechsle_aktuell
        and weinberg.traube.sorte == weinberg2.traube.sorte  # type: ignore
        and weinberg.pflegezustand == weinberg2.pflegezustand
    )
    print(
        f"  Original : {weinberg.traube.sorte.value}, "  # type: ignore
        f"{weinberg.oechsle_aktuell}°, "
        f"Pflege {weinberg.pflegezustand}%"
    )
    print(
        f"  Geladen  : {weinberg2.traube.sorte.value}, "  # type: ignore
        f"{weinberg2.oechsle_aktuell}°, "
        f"Pflege {weinberg2.pflegezustand}%"
    )
    print(f"  Identisch: {'✓ Ja' if gleich else '✗ Nein'}")

    print("\n" + "=" * 52)
    print("  Self-Test abgeschlossen!")
    print("=" * 52)


if __name__ == "__main__":
    main()
