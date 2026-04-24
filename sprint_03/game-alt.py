"""
game.py – Spielverwaltungs-Modul (Sprint 3)
============================================
Erweitert um:
  - Vollständiges Kellerei-Aktionsmenü
  - Eiswein-Auflösung im Winter
  - Rathaus-Anmeldung
  - Fass-Auswahl im Menü

Sprint 3 – Ernte, Kellerei & Weinqualität
"""

from __future__ import annotations
import json
import os
from typing import List, Optional
from player import Spieler
from region import region_auswaehlen
from grape import TRAUBEN, traube_auswaehlen
from winery import Fasszustand
from weather import (
    wetter_wuerfeln,
    jahreszeit_berechnen,
    jahreszeit_anzeigen,
    Jahreszeit,
    Wetterzustand,
    WETTER_EREIGNISSE,
)

SPEICHER_ORDNER = "speicherstaende"
RUNDEN_GESAMT = 12  # 3 Jahre


# ─────────────────────────────────────────────────────────────────────────────
# Klasse: Spiel
# ─────────────────────────────────────────────────────────────────────────────
class Spiel:
    """
    Verwaltet ein komplettes Winzer-Spiel.

    Neu in Sprint 3:
      - Kellerei-Aktionen im Menü
      - Eiswein-Auflösung automatisch im Winter
      - Rathaus-Anmeldung
    """

    def __init__(self, spiel_name: str = "") -> None:
        self.spiel_name: str = spiel_name
        self.spieler_liste: List[Spieler] = []
        self.aktuelle_runde: int = 1
        self.aktueller_spieler_index: int = 0
        self.runden_gesamt: int = RUNDEN_GESAMT

    # ── Spieleinrichtung ─────────────────────────────────────────────────────

    def setup_spiel(self) -> None:
        """Interaktive Spieleinrichtung."""
        print("\n" + "=" * 54)
        print("  NEUES SPIEL EINRICHTEN")
        print("=" * 54)

        eingabe = input("\n  Name für dieses Spiel: ").strip()
        self.spiel_name = eingabe if eingabe else "Winzer-Spiel"

        while True:
            try:
                anzahl = int(input("  Anzahl der Spieler (2–4): "))
                if 2 <= anzahl <= 4:
                    break
                print("  Bitte zwischen 2 und 4 wählen.")
            except ValueError:
                print("  Ungültige Eingabe.")

        for i in range(1, anzahl + 1):
            print(f"\n  {'─' * 48}")
            print(f"  Spieler {i} einrichten")
            print(f"  {'─' * 48}")
            name_eingabe = input(f"  Name: ").strip()
            name = name_eingabe if name_eingabe else f"Spieler {i}"
            print(f"\n  {name}, wähle dein Anbaugebiet:")
            region = region_auswaehlen()
            spieler = Spieler(name=name, region=region)
            print(f"\n  {name}, wähle deine Rebsorte:")
            traube = traube_auswaehlen(region.name.value)
            spieler.reben_anpflanzen(traube)
            self.spieler_liste.append(spieler)
            print(f"\n{spieler.get_status()}")

    # ── Spielsteuerung ───────────────────────────────────────────────────────

    def get_aktueller_spieler(self) -> Spieler:
        return self.spieler_liste[self.aktueller_spieler_index]

    def naechster_spieler(self) -> None:
        self.aktueller_spieler_index += 1
        if self.aktueller_spieler_index >= len(self.spieler_liste):
            self.aktueller_spieler_index = 0
            self.aktuelle_runde += 1

    def ist_spiel_beendet(self) -> bool:
        return self.aktuelle_runde > self.runden_gesamt

    # ── Aktionsmenü ──────────────────────────────────────────────────────────

    def _menue_weinberg(
        self,
        spieler: Spieler,
        jahreszeit: Jahreszeit,
        ist_frost: bool,
    ) -> None:
        """Zeigt Weinberg-Aktionen an."""
        print(f"\n  +── Weinberg-Aktionen ──────────────────────+")
        print(
            f"  | [1] Düngen"
            f"         (-{spieler.weinberg.KOSTEN_DUENGER:,.0f} EUR)"
            f"             |"
        )
        if spieler.weinberg.schaedlingsbefall:
            print(
                f"  | [2] Schädlinge ⚠"
                f"  (-{spieler.weinberg.KOSTEN_SCHAEDLINGE:,.0f} EUR)"
                f"         |"
            )
        else:
            print(f"  | [2] Schädlinge" f"     (kein Befall)                |")

        # Ernte-Optionen je Jahreszeit
        if jahreszeit == Jahreszeit.HERBST:
            if spieler.weinberg.ernte_bereit:
                print(f"  | [3] Weinlese starten" f"                           |")
                if ist_frost and spieler.weinberg.region.eiswein_moeglich:
                    print(f"  | [4] Eiswein wagen ❄" f"                           |")
                else:
                    print(
                        f"  | [4] Eiswein wagen" f"   (kein Frost / Region)          |"
                    )
            else:
                print(f"  | [3] Weinlese" f"        (noch nicht reif)             |")
                print(f"  | [4] Eiswein wagen" f"   (noch nicht reif)              |")
        else:
            print(f"  | [3] Weinlese" f"        (nur im Herbst)               |")
            print(f"  | [4] Eiswein wagen" f"   (nur im Herbst)                |")
        print(f"  +───────────────────────────────────────────+")

    def _menue_kellerei(self, spieler: Spieler) -> None:
        """Zeigt Kellerei-Aktionen an."""
        fasser_reif = spieler.keller.get_fass_liste_reif()
        fasser_most = [
            f for f in spieler.keller.fass_liste if f.zustand == Fasszustand.MOST
        ]
        fasser_gaerung = [
            f for f in spieler.keller.fass_liste if f.zustand == Fasszustand.GAERUNG
        ]

        print(f"\n  +── Kellerei-Aktionen ──────────────────────+")

        # Keltern nur wenn Ernte verfügbar
        if spieler.weinberg.ernte_verfuegbar:
            print(
                f"  | [5] Keltern ✓"
                f"      (-{spieler.keller.KOSTEN_KELTERN:,.0f} EUR)"
                f"           |"
            )
        else:
            print(f"  | [5] Keltern" f"         (keine Ernte verfügbar)      |")

        # Gärung starten
        if fasser_most:
            ids = [str(f.fass_id) for f in fasser_most]
            print(f"  | [6] Gärung starten" f"  (Fass: {', '.join(ids)})            |")
        else:
            print(f"  | [6] Gärung starten" f"  (kein Most vorhanden)        |")

        # Gärung abschließen
        if fasser_gaerung:
            ids = [str(f.fass_id) for f in fasser_gaerung]
            print(f"  | [7] Gärung abschl." f"  (Fass: {', '.join(ids)})            |")
        else:
            print(f"  | [7] Gärung abschl." f"  (keine Gärung aktiv)         |")

        # Lagern
        if fasser_reif:
            ids = [str(f.fass_id) for f in fasser_reif]
            print(f"  | [8] Fass lagern" f"     (Fass: {', '.join(ids)})            |")
        else:
            print(f"  | [8] Fass lagern" f"     (kein reifes Fass)          |")

        # Abfüllen
        if fasser_reif:
            print(
                f"  | [9] Wein abfüllen"
                f"   (-{spieler.keller.KOSTEN_ABFUELLEN:,.0f} EUR)"
                f"           |"
            )
        else:
            print(f"  | [9] Wein abfüllen" f"   (kein reifes Fass)           |")

        # Verkaufen
        if spieler.keller.flaschen_liste:
            wert = spieler.keller.get_gesamtwert_flaschen()
            print(
                f"  | [V] Flaschen verk."
                f"  ({len(spieler.keller.flaschen_liste)}"
                f" Fl., ~{wert:,.0f} EUR)     |"
            )
        else:
            print(f"  | [V] Flaschen verk." f"  (keine Flaschen)             |")

        print(f"  +───────────────────────────────────────────+")

    def _menue_sonstiges(self, spieler: Spieler) -> None:
        """Zeigt sonstige Aktionen an."""
        rathaus_str = (
            "bereits angemeldet"
            if spieler.rathaus_angemeldet
            else "noch nicht angemeldet"
        )
        print(f"\n  +── Sonstiges ──────────────────────────────+")
        print(f"  | [S] Status anzeigen" f"                              |")
        print(f"  | [R] Rathaus anmelden" f"  ({rathaus_str})   |")
        print(f"  | [X] Zug beenden" f"                              |")
        print(f"  +───────────────────────────────────────────+")

    # ── Spieler-Zug ──────────────────────────────────────────────────────────

    def spieler_zug(
        self,
        spieler: Spieler,
        jahreszeit: Jahreszeit,
        ist_frost: bool,
    ) -> None:
        """
        Verwaltet den kompletten Zug eines Spielers.
        Spieler kann beliebig viele Aktionen pro Zug ausführen.
        """
        while True:
            # Kopfzeile
            print(f"\n  {'═' * 48}")
            print(
                f"  {spieler.name} ist am Zug"
                f" | Kapital: {spieler.geld:,.2f} EUR"
                f" | Öchsle: {spieler.weinberg.oechsle_aktuell}°"
            )
            if spieler.weinberg.eiswein_wartend:
                print(f"  ❄ Wartet auf Eiswein im Winter!")
            print(f"  {'═' * 48}")

            # Menüs anzeigen
            self._menue_weinberg(spieler, jahreszeit, ist_frost)
            self._menue_kellerei(spieler)
            self._menue_sonstiges(spieler)

            try:
                wahl = input("\n  Deine Wahl: ").strip().upper()
            except (EOFError, KeyboardInterrupt):
                break

            # ── Weinberg-Aktionen ──────────────────────────
            if wahl == "1":
                spieler.weinberg_duengen()

            elif wahl == "2":
                if spieler.weinberg.schaedlingsbefall:
                    spieler.schaedlinge_bekaempfen()
                else:
                    print("  Kein Schädlingsbefall.")

            elif wahl == "3":
                if jahreszeit != Jahreszeit.HERBST:
                    print("  ⚠ Weinlese nur im Herbst!")
                elif not spieler.weinberg.ernte_bereit:
                    print("  ⚠ Trauben noch nicht reif!")
                else:
                    spieler.weinlese_durchfuehren()

            elif wahl == "4":
                if jahreszeit != Jahreszeit.HERBST:
                    print("  ⚠ Eiswein-Entscheidung nur im Herbst!")
                elif not spieler.weinberg.ernte_bereit:
                    print("  ⚠ Trauben noch nicht reif!")
                elif not spieler.weinberg.region.eiswein_moeglich:
                    print("  ⚠ In dieser Region kein Eiswein möglich!")
                elif not ist_frost:
                    print("  ⚠ Kein Frost – Eiswein-Chance gering!")
                    bestaetigen = input("  Trotzdem warten? [j/n]: ").strip().lower()
                    if bestaetigen == "j":
                        spieler.eiswein_wagen()
                else:
                    spieler.eiswein_wagen()

            # ── Kellerei-Aktionen ──────────────────────────
            elif wahl == "5":
                spieler.most_keltern()

            elif wahl == "6":
                fasser = [
                    f
                    for f in spieler.keller.fass_liste
                    if f.zustand == Fasszustand.MOST
                ]
                if not fasser:
                    print("  Kein Most vorhanden.")
                else:
                    fass_id = self._fass_auswaehlen(fasser)
                    if fass_id:
                        spieler.fass_gaerung_starten(fass_id)

            elif wahl == "7":
                fasser = [
                    f
                    for f in spieler.keller.fass_liste
                    if f.zustand == Fasszustand.GAERUNG
                ]
                if not fasser:
                    print("  Keine aktive Gärung.")
                else:
                    fass_id = self._fass_auswaehlen(fasser)
                    if fass_id:
                        spieler.fass_gaerung_abschliessen(fass_id)

            elif wahl == "8":
                fasser = spieler.keller.get_fass_liste_reif()
                if not fasser:
                    print("  Kein reifes Fass vorhanden.")
                else:
                    fass_id = self._fass_auswaehlen(fasser)
                    if fass_id:
                        monate = self._monate_abfragen()
                        spieler.fass_lagern(fass_id, monate)

            elif wahl == "9":
                fasser = spieler.keller.get_fass_liste_reif()
                if not fasser:
                    print("  Kein reifes Fass vorhanden.")
                else:
                    fass_id = self._fass_auswaehlen(fasser)
                    if fass_id:
                        spieler.wein_abfuellen(fass_id)

            elif wahl == "V":
                if not spieler.keller.flaschen_liste:
                    print("  Keine Flaschen vorhanden.")
                else:
                    anzahl = self._anzahl_abfragen(len(spieler.keller.flaschen_liste))
                    spieler.flaschen_verkaufen(anzahl)

            # ── Sonstiges ─────────────────────────────────
            elif wahl == "S":
                print(spieler.get_status())
                spieler.weinberg_status()
                spieler.keller_status()

            elif wahl == "R":
                self._rathaus_anmelden(spieler)

            elif wahl == "X":
                print(f"  {spieler.name} beendet den Zug.")
                break

            else:
                print("  Ungültige Eingabe.")

    # ── Hilfsmethoden für Menü ───────────────────────────────────────────────

    def _fass_auswaehlen(self, fasser: list) -> Optional[int]:
        """Lässt den Spieler ein Fass aus einer Liste wählen."""
        if len(fasser) == 1:
            return fasser[0].fass_id

        print("\n  Welches Fass?")
        for i, fass in enumerate(fasser, 1):
            print(
                f"  [{i}] Fass #{fass.fass_id}"
                f" – {fass.rebsorte}"
                f" {fass.oechsle}°"
                f" {fass.lager_monate} Mon."
            )
        print("  [0] Abbrechen")

        while True:
            try:
                wahl = int(input("  Wahl: "))
                if wahl == 0:
                    return None
                if 1 <= wahl <= len(fasser):
                    return fasser[wahl - 1].fass_id
                print(f"  Bitte 0–{len(fasser)} eingeben.")
            except ValueError:
                print("  Ungültige Eingabe.")

    def _monate_abfragen(self) -> int:
        """Fragt nach der Anzahl Monate für die Lagerung."""
        while True:
            try:
                monate = int(input("  Wie viele Monate lagern? (1–12): "))
                if 1 <= monate <= 12:
                    return monate
                print("  Bitte zwischen 1 und 12 wählen.")
            except ValueError:
                print("  Ungültige Eingabe.")

    def _anzahl_abfragen(self, max_anzahl: int) -> Optional[int]:
        """Fragt nach der Anzahl zu verkaufender Flaschen."""
        print(f"  Verfügbare Flaschen: {max_anzahl}")
        print(f"  [0] Alle verkaufen")
        while True:
            try:
                anzahl = int(input(f"  Anzahl (0 = alle, max. {max_anzahl}): "))
                if anzahl == 0:
                    return None  # alle
                if 1 <= anzahl <= max_anzahl:
                    return anzahl
                print(f"  Bitte 0–{max_anzahl} eingeben.")
            except ValueError:
                print("  Ungültige Eingabe.")

    def _rathaus_anmelden(self, spieler: Spieler) -> None:
        """Meldet den Spieler im Rathaus an."""
        if spieler.rathaus_angemeldet:
            print("  Bereits im Rathaus angemeldet.")
            return

        KOSTEN_RATHAUS = 2_000.0
        print(f"\n  Rathaus-Anmeldung: {KOSTEN_RATHAUS:,.0f} EUR")
        print("  Pflicht vor dem ersten Verkauf!")

        if not spieler.geld_abziehen(KOSTEN_RATHAUS):
            return

        spieler.rathaus_angemeldet = True
        spieler.lizenzen.append("Weinverkauf-Lizenz")
        spieler.aktion_aufzeichnen(f"Rathaus angemeldet (-{KOSTEN_RATHAUS:,.0f} EUR)")
        print("  ✓ Angemeldet! Weinverkauf-Lizenz erhalten.")
        print(f"  Kapital: {spieler.geld:,.2f} EUR")

    # ── Hauptspielschleife ───────────────────────────────────────────────────

    def spielen(self) -> None:
        """Hauptspielschleife über alle Runden."""
        print("\n" + "=" * 54)
        print(f"  '{self.spiel_name}' beginnt!")
        print(f"  {self.runden_gesamt} Runden" f" ({self.runden_gesamt // 4} Jahre)")
        print("=" * 54)

        while not self.ist_spiel_beendet():
            # Jahreszeit & Wetter
            jahreszeit = jahreszeit_berechnen(self.aktuelle_runde)
            jahreszeit_anzeigen(jahreszeit, self.aktuelle_runde)
            wetter = wetter_wuerfeln(jahreszeit)
            print(
                f"\n  Wetter: {wetter.zustand.value}"
                f" ({'+' if wetter.oechsle_bonus >= 0 else ''}"
                f"{wetter.oechsle_bonus}°)"
            )

            # Jeden Spieler dran lassen
            for spieler in self.spieler_liste:
                print(f"\n  {'═' * 48}")
                print(f"  Am Zug: {spieler.name}")
                print(f"  {'═' * 48}")

                # Zug
                self.spieler_zug(
                    spieler,
                    jahreszeit,
                    wetter.ist_frost,
                )

                # Weinberg-Runde abschließen
                spieler.weinberg.runde_abschliessen(jahreszeit, wetter)
                spieler.runde_abschliessen()

            # Rangliste
            self.rangliste_anzeigen()
            self.aktuelle_runde += 1

        self._spielende_anzeigen()

    def _spielende_anzeigen(self) -> None:
        """Zeigt das Spielende mit Sieger an."""
        print("\n" + "=" * 54)
        print("  SPIELENDE!")
        print("=" * 54)
        rangliste = self.get_rangliste()
        sieger = rangliste[0]
        gesamtv = sieger.geld + sieger.keller.get_gesamtwert_flaschen()
        print(f"\n  🏆 Sieger: {sieger.name}")
        print(f"  Region   : {sieger.region.name.value}")
        print(f"  Kapital  : {sieger.geld:,.2f} EUR")
        print(f"  Keller   : " f"{sieger.keller.get_gesamtwert_flaschen():,.2f} EUR")
        print(f"  Gesamt   : {gesamtv:,.2f} EUR")
        print()
        self.rangliste_anzeigen()

    # ── Rangliste ────────────────────────────────────────────────────────────

    def get_rangliste(self) -> List[Spieler]:
        """Gibt Spieler nach Gesamtvermögen sortiert zurück."""
        return sorted(
            self.spieler_liste,
            key=lambda s: (s.geld + s.keller.get_gesamtwert_flaschen()),
            reverse=True,
        )

    def rangliste_anzeigen(self) -> None:
        """Zeigt die aktuelle Rangliste an."""
        print("\n  === Rangliste ===")
        print(
            f"  {'Pl.':<4} {'Name':<16}"
            f" {'Kapital':>12}"
            f" {'Keller':>10}"
            f" {'Gesamt':>12}"
        )
        print("  " + "─" * 58)
        for pl, s in enumerate(self.get_rangliste(), 1):
            keller_wert = s.keller.get_gesamtwert_flaschen()
            gesamt = s.geld + keller_wert
            print(
                f"  {pl:<4} {s.name:<16}"
                f" {s.geld:>11,.0f}€"
                f" {keller_wert:>9,.0f}€"
                f" {gesamt:>11,.0f}€"
            )

    def spielinfo_anzeigen(self) -> None:
        """Zeigt allgemeine Spielinformationen an."""
        jahreszeit = jahreszeit_berechnen(self.aktuelle_runde)
        print(f"\n  Spiel      : {self.spiel_name}")
        print(f"  Runde      : {self.aktuelle_runde}" f"/{self.runden_gesamt}")
        print(f"  Jahreszeit : {jahreszeit.value}")
        print(f"  Spieler    : {len(self.spieler_liste)}")

    # ── Serialisierung ───────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "spiel_name": self.spiel_name,
            "aktuelle_runde": self.aktuelle_runde,
            "aktueller_spieler_index": self.aktueller_spieler_index,
            "runden_gesamt": self.runden_gesamt,
            "spieler_liste": [s.to_dict() for s in self.spieler_liste],
        }

    @classmethod
    def from_dict(cls, daten: dict) -> "Spiel":
        spiel = cls(spiel_name=daten["spiel_name"])
        spiel.aktuelle_runde = daten["aktuelle_runde"]
        spiel.aktueller_spieler_index = daten["aktueller_spieler_index"]
        spiel.runden_gesamt = daten.get("runden_gesamt", RUNDEN_GESAMT)
        spiel.spieler_liste = [Spieler.from_dict(s) for s in daten["spieler_liste"]]
        return spiel

    def speichern(self) -> None:
        """Speichert den Spielstand als JSON."""
        os.makedirs(SPEICHER_ORDNER, exist_ok=True)
        dateiname = os.path.join(
            SPEICHER_ORDNER, self.spiel_name.replace(" ", "_") + ".json"
        )
        with open(dateiname, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        print(f"\n  ✓ Spielstand gespeichert: {dateiname}")

    @classmethod
    def laden(cls, dateiname: str) -> "Spiel":
        """Lädt einen Spielstand aus JSON."""
        with open(dateiname, "r", encoding="utf-8") as f:
            daten = json.load(f)
        print(f"  ✓ Geladen: {dateiname}")
        return cls.from_dict(daten)


# ─────────────────────────────────────────────────────────────────────────────
# Self-Test
# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    """
    Testet die Spielverwaltung automatisch.
    Simuliert 2 Spieler über 8 Runden (2 Jahre)
    ohne interaktive Eingaben.
    """
    from region import REGIONEN, RegionName
    from grape import TRAUBEN, Rebsorte

    print("=" * 54)
    print("  SPIEL – Self-Test (Sprint 3, automatisch)")
    print("=" * 54)

    # ── Setup ─────────────────────────────────────────────
    spiel = Spiel(spiel_name="Testspiel-S3")

    anna = Spieler("Arite Zastrow", REGIONEN[RegionName.MOSEL])
    anna.reben_anpflanzen(TRAUBEN[Rebsorte.RIESLING])
    spiel.spieler_liste.append(anna)

    ben = Spieler("Rene Kallenbach", REGIONEN[RegionName.AHR])
    ben.reben_anpflanzen(TRAUBEN[Rebsorte.SPAETBURGUNDER])
    spiel.spieler_liste.append(ben)

    print(f"  Spieler: {[s.name for s in spiel.spieler_liste]}")

    # ── 8 Runden automatisch ──────────────────────────────
    test_wetter = [
        Wetterzustand.NORMAL,  # Runde 1 – Frühling
        Wetterzustand.IDEAL,  # Runde 2 – Sommer
        Wetterzustand.NORMAL,  # Runde 3 – Herbst
        Wetterzustand.FROST,  # Runde 4 – Winter
        Wetterzustand.NORMAL,  # Runde 5 – Frühling
        Wetterzustand.IDEAL,  # Runde 6 – Sommer
        Wetterzustand.IDEAL,  # Runde 7 – Herbst
        Wetterzustand.FROST,  # Runde 8 – Winter
    ]

    for runde in range(1, 9):
        jahreszeit = jahreszeit_berechnen(runde)
        jahreszeit_anzeigen(jahreszeit, runde)
        wetter = WETTER_EREIGNISSE[test_wetter[runde - 1]]

        for spieler in spiel.spieler_liste:
            # Düngen im Frühling & Sommer
            if jahreszeit in (Jahreszeit.FRUEHLING, Jahreszeit.SOMMER):
                spieler.weinberg_duengen()

            # Herbst: Weinlese
            if jahreszeit == Jahreszeit.HERBST:
                spieler.weinberg.runde_abschliessen(jahreszeit, wetter)
                if spieler.weinberg.ernte_bereit:
                    spieler.weinlese_durchfuehren()
                    spieler.most_keltern()
                    spieler.fass_gaerung_starten(spieler.keller.naechste_fass_id - 1)
            else:
                spieler.weinberg.runde_abschliessen(jahreszeit, wetter)

            # Gärung abschließen im Winter
            if jahreszeit == Jahreszeit.WINTER:
                for fass in spieler.keller.fass_liste:
                    if fass.zustand == Fasszustand.GAERUNG:
                        spieler.fass_gaerung_abschliessen(fass.fass_id)
                        spieler.fass_lagern(fass.fass_id, 3)

            spieler.runde_abschliessen()

        spiel.aktuelle_runde += 1

    # Abfüllen & Verkaufen
    print("\n  Abfüllen & Verkaufen:")
    for spieler in spiel.spieler_liste:
        for fass in spieler.keller.get_fass_liste_reif():
            spieler.wein_abfuellen(fass.fass_id)
        spieler.flaschen_verkaufen()

    # Rangliste
    spiel.rangliste_anzeigen()

    # Serialisierung
    print("\n  Serialisierung:")
    spiel.speichern()
    datei = os.path.join(SPEICHER_ORDNER, "Testspiel-S3.json")
    spiel2 = Spiel.laden(datei)
    gleich = spiel.spiel_name == spiel2.spiel_name and len(spiel.spieler_liste) == len(
        spiel2.spieler_liste
    )

    # Zusammenfassung
    print("\n" + "=" * 54)
    print("  Testergebnisse:")
    print("  " + "─" * 42)
    tests = [
        ("2 Spieler vorhanden", len(spiel.spieler_liste) == 2),
        ("Anna hat Kapital > Start", anna.geld != 50_000.0),
        ("Ben hat Kapital > Start", ben.geld != 50_000.0),
        ("Serialisierung korrekt", gleich),
    ]
    alle_ok = True
    for name, ergebnis in tests:
        symbol = "✓" if ergebnis else "✗"
        print(f"  [{symbol}] {name}")
        if not ergebnis:
            alle_ok = False

    print("  " + "─" * 42)
    print(f"  Gesamt: " f"{'✓ Alle Tests bestanden!' if alle_ok else '✗ Fehler!'}")
    print("=" * 54)


if __name__ == "__main__":
    main()
