"""
vineyard.py – Weinberg-Modul (Sprint 3, korrigiert)
=====================================================
Korrekturen:
  - herbst_vorbereiten() NEU: setzt ernte_bereit VOR
    dem Spielerzug, damit Spieler im Herbst sofort
    ernten kann
  - runde_abschliessen() setzt ernte_bereit NICHT mehr
    → keine doppelte Logik mehr

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

    Reife-Faktoren (skalieren Pflege-Bonus):
        0 Jahre →  60%
        1 Jahr  →  80%
        2 Jahre →  90%
        3+Jahre → 100%

    Ernte-Ablauf:
        Herbst: herbst_vorbereiten() setzt ernte_bereit = True
                Spieler führt weinlese() oder eiswein_warten() aus
        Winter: eiswein_auflösen() bei Frost oder Verlust
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
        self.eiswein_wartend: bool = False
        self.ernte_oechsle: int = 0
        self.ernte_verfuegbar: bool = False

    # ── Hilfsmethoden ────────────────────────────────────────────────────────

    def get_reife_faktor(self) -> float:
        """Gibt den Reife-Faktor für das aktuelle Reben-Alter zurück."""
        return self.REIFE_FAKTOREN.get(self.reben_alter, self.REIFE_FAKTOR_VOLL)

    # ── Darstellung ──────────────────────────────────────────────────────────

    def __str__(self) -> str:
        traube_str = self.traube.sorte.value if self.traube else "Noch nicht bepflanzt"
        schaedl_str = "⚠ JA" if self.schaedlingsbefall else "Nein"
        ernte_str = "✓ Ja" if self.ernte_bereit else "Nein"
        eiswein_str = "❄ Wartend!" if self.eiswein_wartend else "Nein"
        verfuegb_str = (
            f"✓ {self.ernte_oechsle}° bereit" if self.ernte_verfuegbar else "Nein"
        )

        return (
            f"\n  +──── Weinberg-Status ──────────────────────+\n"
            f"  | Region          : {self.region.name.value}\n"
            f"  | Rebsorte        : {traube_str}\n"
            f"  | Reben-Alter     : {self.reben_alter} Jahr(e)\n"
            f"  | Reife-Faktor    : {self.get_reife_faktor():.0%}\n"
            f"  | Pflegezustand   : {self.pflegezustand}%\n"
            f"  | Gedüngt         : {'Ja' if self.geduengt else 'Nein'}\n"
            f"  | Schädlinge      : {schaedl_str}\n"
            f"  | Erntereif       : {ernte_str}\n"
            f"  | Öchsle aktuell  : {self.oechsle_aktuell}°\n"
            f"  | Eiswein wartend : {eiswein_str}\n"
            f"  | Ernte verfügbar : {verfuegb_str}\n"
            f"  +───────────────────────────────────────────+"
        )

    # ── Aktionen: Weinberg-Pflege ─────────────────────────────────────────────

    def anpflanzen(self, traube: Traube) -> bool:
        """Pflanzt eine Rebsorte in den Weinberg."""
        if self.traube is not None:
            print("  ⚠ Weinberg bereits bepflanzt!")
            return False

        eignung = traube.get_eignung(self.region.name.value)
        if eignung == 0:
            print(
                f"  ⚠ {traube.sorte.value} ist für "
                f"{self.region.name.value} ungeeignet!"
            )
            return False

        self.traube = traube
        self.reben_alter = 0
        self.pflegezustand = 50
        regions_bonus = eignung * 3
        self.oechsle_aktuell = traube.basis_oechsle + regions_bonus

        sterne = "★" * eignung + "☆" * (3 - eignung)
        print(f"\n  ✓ {traube.sorte.value} angepflanzt!")
        print(f"  Eignung      : {sterne}")
        print(
            f"  Start-Öchsle : {traube.basis_oechsle}°"
            f" + {regions_bonus}° = {self.oechsle_aktuell}°"
        )
        print(f"  Reife-Faktor : {self.get_reife_faktor():.0%}" f" (Reben noch jung)")
        return True

    def duengen(self) -> bool:
        """Düngt den Weinberg (+15% Pflegezustand)."""
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
        print(f"  ✓ Schädlinge bekämpft!" f" Pflegezustand: {self.pflegezustand}%")
        return True

    # ── NEU: Herbst vorbereiten ──────────────────────────────────────────────

    def herbst_vorbereiten(self) -> None:
        """
        Bereitet den Weinberg für den Herbst vor.

        WICHTIG: Wird VOR dem Spielerzug aufgerufen!
        Dadurch sieht der Spieler sofort im Herbst,
        dass seine Trauben erntereif sind.

        Setzt ernte_bereit = True wenn:
          - Trauben vorhanden
          - Nicht auf Eiswein wartend
        """
        if self.traube is None:
            return

        if self.eiswein_wartend:
            print(f"  ❄ Trauben hängen noch für Eiswein" f" ({self.oechsle_aktuell}°)")
            return

        # Erntereife setzen – VOR dem Spielerzug!
        self.ernte_bereit = True
        print(f"\n  🍇 Trauben sind erntereif!" f" (Öchsle: {self.oechsle_aktuell}°)")
        print(f"  Aktion [3] Weinlese oder" f" [4] Eiswein wagen wählen.")

    # ── Aktionen: Ernte ──────────────────────────────────────────────────────

    def weinlese(self) -> Tuple[int, bool]:
        """
        Führt die normale Weinlese durch.

        Returns:
            (oechsle, erfolg)
        """
        if not self.ernte_bereit:
            print("  ⚠ Trauben noch nicht erntereif!")
            return (0, False)

        if self.eiswein_wartend:
            print("  ⚠ Wartet auf Eiswein!")
            return (0, False)

        if self.traube is None:
            print("  ⚠ Kein Weinberg bepflanzt!")
            return (0, False)

        oechsle = self.oechsle_aktuell
        self.ernte_oechsle = oechsle
        self.ernte_verfuegbar = True
        self.ernte_bereit = False

        print(f"\n  🍇 Weinlese erfolgreich!")
        print(f"  Rebsorte : {self.traube.sorte.value}")
        print(f"  Öchsle   : {oechsle}°")
        print(f"  → Jetzt keltern mit Aktion [5]!")

        return (oechsle, True)

    def eiswein_warten(self) -> bool:
        """
        Spieler wartet auf Eiswein im Winter.

        Returns:
            True wenn erfolgreich gesetzt
        """
        if not self.ernte_bereit:
            print("  ⚠ Trauben noch nicht erntereif!")
            return False

        if not self.region.eiswein_moeglich:
            print(f"  ⚠ In {self.region.name.value}" f" ist kein Eiswein möglich!")
            return False

        self.eiswein_wartend = True
        self.ernte_bereit = False

        frost_chance = self._frost_wahrscheinlichkeit()
        print(f"\n  ❄ Trauben hängen für Eiswein!")
        print(f"  Aktuell  : {self.oechsle_aktuell}°")
        print(f"  Bei Frost: 110–128° Öchsle")
        print(f"  Chance   : {frost_chance:.0%} Frost im Winter")
        print(f"  Risiko   : Kein Frost → Ernte verloren! ☠")
        return True

    def eiswein_aufloesen(self, wetter: Wetterereignis) -> Tuple[int, bool]:
        """
        Löst die Eiswein-Entscheidung im Winter auf.

        Returns:
            (oechsle, ist_eiswein)
        """
        if not self.eiswein_wartend:
            return (0, False)

        self.eiswein_wartend = False

        if wetter.ist_frost:
            # ✅ Frost! Eiswein!
            eiswein_oechsle = random.randint(110, 128)
            self.ernte_oechsle = eiswein_oechsle
            self.ernte_verfuegbar = True

            print(f"\n  ❄ FROST! Eiswein-Ernte!")
            print(f"  Öchsle   : {eiswein_oechsle}°")
            print(f"  → Sofort keltern mit Aktion [5]!")
            return (eiswein_oechsle, True)

        else:
            # ☠ Kein Frost – Verlust
            self.ernte_oechsle = 0
            self.ernte_verfuegbar = False
            self.oechsle_aktuell = 0

            print(f"\n  ☠ Kein Frost – Trauben verfault!")
            print(f"  Die gesamte Ernte ist verloren!")
            return (0, False)

    def ernte_abholen(self) -> Tuple[int, str, bool]:
        """
        Gibt geerntete Trauben für die Kellerei frei.

        Returns:
            (oechsle, farbe, ist_eiswein)
        """
        if not self.ernte_verfuegbar:
            print("  ⚠ Keine Ernte verfügbar!")
            return (0, "", False)

        oechsle = self.ernte_oechsle
        ist_eiswein = oechsle >= 110 and self.region.eiswein_moeglich
        farbe = self.traube.farbe if self.traube else "weiss"

        self.ernte_verfuegbar = False
        self.ernte_oechsle = 0
        self.oechsle_aktuell = 0

        return (oechsle, farbe, ist_eiswein)

    # ── Runden-Abschluss ─────────────────────────────────────────────────────

    def runde_abschliessen(
        self,
        jahreszeit: Jahreszeit,
        wetter: Wetterereignis,
    ) -> None:
        """
        Verarbeitet das Ende einer Runde.

        WICHTIG: ernte_bereit wird hier NICHT mehr gesetzt!
        Das passiert in herbst_vorbereiten() VOR dem Spielerzug.

        Ablauf:
          1. Eiswein-Auflösung im Winter (falls wartend)
          2. Öchsle kumulativ berechnen
          3. Gemeinsame Abschlusslogik
        """
        if self.traube is None:
            return

        reife_faktor = self.get_reife_faktor()

        # ── Winter: Eiswein auflösen ──────────────────────
        if jahreszeit == Jahreszeit.WINTER and self.eiswein_wartend:
            self.eiswein_aufloesen(wetter)
            self._runde_abschliessen_gemeinsam(jahreszeit, wetter, reife_faktor)
            return

        # ── Öchsle kumulativ berechnen ────────────────────
        print(f"\n  ┌─── Öchsle-Entwicklung ──────────────────────┐")
        print(f"  │ Öchsle zu Beginn              : " f"{self.oechsle_aktuell:>4}°")
        print(
            f"  │ Reben-Reife ({self.reben_alter} Jahr(e))"
            f"          :   {reife_faktor:.0%}"
        )

        # Wetter
        self.oechsle_aktuell += wetter.oechsle_bonus
        v = "+" if wetter.oechsle_bonus >= 0 else ""
        print(
            f"  │ Wetter ({wetter.zustand.value:<22}): "
            f"{v}{wetter.oechsle_bonus:>3}°"
        )

        # Pflege-Bonus × Reife-Faktor
        if self.geduengt:
            basis = self.pflegezustand // 10
            pflege_bonus = int(basis * reife_faktor)
            self.oechsle_aktuell += pflege_bonus
            print(
                f"  │ Pflege ({self.pflegezustand}%"
                f"÷10={basis}×{reife_faktor:.0%})       : "
                f"+{pflege_bonus:>3}°"
            )

        # Schädlings-Malus
        if self.schaedlingsbefall:
            self.oechsle_aktuell -= 10
            print(f"  │ Schädlingsbefall              :  -10°")

        # Spätfrost-Malus
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

        # Gemeinsame Abschlusslogik
        self._runde_abschliessen_gemeinsam(jahreszeit, wetter, reife_faktor)

    def _runde_abschliessen_gemeinsam(
        self,
        jahreszeit: Jahreszeit,
        wetter: Wetterereignis,
        reife_faktor: float,
    ) -> None:
        """
        Gemeinsame Abschluss-Logik für alle Runden:
          - Pflegezustand sinkt
          - Düngung zurücksetzen
          - Reben altern im Winter
          - Zufälliger Schädlingsbefall
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
        """Gibt die Winter-Frostwahrscheinlichkeit zurück."""
        from weather import WETTER_GEWICHTE, Wetterzustand

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
    Testet die korrigierte Weinlese-Logik.
    Schwerpunkt: herbst_vorbereiten() VOR Spielerzug.
    """
    from region import REGIONEN, RegionName
    from grape import TRAUBEN, Rebsorte
    from weather import WETTER_EREIGNISSE, Wetterzustand, jahreszeit_anzeigen

    print("=" * 56)
    print("  WEINBERG – Self-Test (Weinlese-Fix)")
    print("=" * 56)

    region = REGIONEN[RegionName.MOSEL]
    riesling = TRAUBEN[Rebsorte.RIESLING]

    # ── Szenario A: Normale Weinlese ──────────────────────
    print("\n  ═══ Szenario A: Normale Weinlese ═══")
    weinberg = Weinberg(region=region)
    weinberg.anpflanzen(riesling)

    # Frühling
    jz = Jahreszeit.FRUEHLING
    jahreszeit_anzeigen(jz, 1)
    weinberg.duengen()
    weinberg.runde_abschliessen(jz, WETTER_EREIGNISSE[Wetterzustand.NORMAL])

    # Sommer
    jz = Jahreszeit.SOMMER
    jahreszeit_anzeigen(jz, 2)
    weinberg.duengen()
    weinberg.runde_abschliessen(jz, WETTER_EREIGNISSE[Wetterzustand.IDEAL])

    # Herbst: herbst_vorbereiten() VOR Spielerzug
    jz = Jahreszeit.HERBST
    jahreszeit_anzeigen(jz, 3)
    print("\n  → herbst_vorbereiten() aufrufen:")
    weinberg.herbst_vorbereiten()
    print(f"  ernte_bereit = {weinberg.ernte_bereit}")  # muss True sein!

    # Spieler führt Weinlese durch
    print("\n  → Weinlese durchführen:")
    oechsle, erfolg = weinberg.weinlese()

    # runde_abschliessen() danach
    weinberg.runde_abschliessen(jz, WETTER_EREIGNISSE[Wetterzustand.NORMAL])

    # ── Szenario B: Eiswein ───────────────────────────────
    print("\n  ═══ Szenario B: Eiswein mit Frost ═══")
    weinberg_b = Weinberg(region=region)
    weinberg_b.anpflanzen(riesling)

    for jz, w in [
        (Jahreszeit.FRUEHLING, Wetterzustand.NORMAL),
        (Jahreszeit.SOMMER, Wetterzustand.IDEAL),
    ]:
        weinberg_b.runde_abschliessen(jz, WETTER_EREIGNISSE[w])

    # Herbst: Eiswein wagen
    jz = Jahreszeit.HERBST
    jahreszeit_anzeigen(jz, 3)
    weinberg_b.herbst_vorbereiten()
    print(f"  ernte_bereit = {weinberg_b.ernte_bereit}")
    weinberg_b.eiswein_warten()
    weinberg_b.runde_abschliessen(jz, WETTER_EREIGNISSE[Wetterzustand.NORMAL])

    # Winter: Frost!
    jz = Jahreszeit.WINTER
    jahreszeit_anzeigen(jz, 4)
    weinberg_b.runde_abschliessen(jz, WETTER_EREIGNISSE[Wetterzustand.FROST])
    oechsle_b, farbe_b, ist_eiswein = weinberg_b.ernte_abholen()

    # ── Zusammenfassung ───────────────────────────────────
    print("\n" + "=" * 56)
    print("  Testergebnisse:")
    print("  " + "─" * 44)
    tests = [
        ("Herbst: ernte_bereit gesetzt", erfolg),
        ("Szenario A: Öchsle > 0", oechsle > 0),
        ("Szenario B: Eiswein erkannt", ist_eiswein),
        ("Szenario B: Öchsle >= 110°", oechsle_b >= 110),
        ("Ernte nach Weinlese leer", not weinberg.ernte_verfuegbar),
    ]
    alle_ok = True
    for name, ergebnis in tests:
        symbol = "✓" if ergebnis else "✗"
        print(f"  [{symbol}] {name}")
        if not ergebnis:
            alle_ok = False

    print("  " + "─" * 44)
    print(f"  Gesamt: " f"{'✓ Alle Tests bestanden!' if alle_ok else '✗ Fehler!'}")
    print("=" * 56)


if __name__ == "__main__":
    main()
