"""
game.py – Spielverwaltungs-Modul
==================================
Verwaltet den gesamten Spielablauf, alle Spieler,
die Rundenlogik und das Aktionsmenü.

Änderungen gegenüber Sprint 1:
  - Echte Spielschleife mit Jahreszeiten
  - Aktionsmenü pro Spieler pro Runde
  - Wetter wird pro Runde gewürfelt
  - Eiswein-Entscheidung im Herbst bei Frost

Sprint 2 – Weinberg & Jahreszeiten
"""

from __future__ import annotations
import json
import os
from typing import List
from player import Spieler
from region import region_auswaehlen
from grape import TRAUBEN, traube_auswaehlen
from weather import (
    wetter_wuerfeln,
    jahreszeit_berechnen,
    jahreszeit_anzeigen,
    Jahreszeit,
    Wetterzustand,
)

# Ordner für gespeicherte Spielstände
SPEICHER_ORDNER = "saves"

# Anzahl Runden pro Spiel (1 Runde = 1 Jahreszeit)
# 8 Runden = 2 komplette Jahre
RUNDEN_GESAMT = 8


# ─────────────────────────────────────────────────────────────────────────────
# Klasse: Spiel
# ─────────────────────────────────────────────────────────────────────────────
class Spiel:
    """
    Verwaltet ein komplettes Winzer-Spiel.

    Attribute:
        spiel_name               : Name des Spiels
        spieler_liste            : Liste aller Spieler
        aktuelle_runde           : Aktuelle Rundenzahl (startet bei 1)
        aktueller_spieler_index  : Index des aktiven Spielers
        runden_gesamt            : Gesamtzahl der Runden
    """

    def __init__(self, spiel_name: str = "") -> None:
        self.spiel_name: str = spiel_name
        self.spieler_liste: List[Spieler] = []
        self.aktuelle_runde: int = 1
        self.aktueller_spieler_index: int = 0
        self.runden_gesamt: int = RUNDEN_GESAMT

    # ── Spieleinrichtung ─────────────────────────────────────────────────────

    def setup_spiel(self) -> None:
        """
        Interaktive Spieleinrichtung.
        Fragt nach: Spielname, Spieleranzahl,
        Spielernamen, Regionen und Rebsorten.
        """
        print("\n" + "=" * 52)
        print("  NEUES SPIEL EINRICHTEN")
        print("=" * 52)

        # Spielname
        eingabe = input("\n  Name für dieses Spiel: ").strip()
        self.spiel_name = eingabe if eingabe else "Winzer-Spiel"

        # Spieleranzahl
        while True:
            try:
                anzahl = int(input("  Anzahl der Spieler (2–4): "))
                if 2 <= anzahl <= 4:
                    break
                print("  Bitte eine Zahl zwischen 2 und 4 eingeben.")
            except ValueError:
                print("  Ungültige Eingabe.")

        # Jeden Spieler einrichten
        for i in range(1, anzahl + 1):
            print(f"\n  {'─' * 46}")
            print(f"  Spieler {i} einrichten")
            print(f"  {'─' * 46}")

            # Name
            name_eingabe = input(f"  Name von Spieler {i}: ").strip()
            name = name_eingabe if name_eingabe else f"Spieler {i}"

            # Region wählen
            print(f"\n  {name}, wähle dein Anbaugebiet:")
            region = region_auswaehlen()

            # Spieler anlegen
            spieler = Spieler(name=name, region=region)

            # Rebsorte wählen
            print(f"\n  {name}, wähle deine Rebsorte:")
            traube = traube_auswaehlen(region.name.value)

            # Reben anpflanzen
            print(f"\n  {name} pflanzt {traube.sorte.value} an ...")
            spieler.reben_anpflanzen(traube)

            self.spieler_liste.append(spieler)
            print(f"\n{spieler.get_status()}")

    # ── Spielsteuerung ───────────────────────────────────────────────────────

    def get_aktueller_spieler(self) -> Spieler:
        """Gibt den aktuell aktiven Spieler zurück."""
        return self.spieler_liste[self.aktueller_spieler_index]

    def naechster_spieler(self) -> None:
        """
        Wechselt zum nächsten Spieler.
        Nach einem vollständigen Durchlauf → neue Runde.
        """
        self.aktueller_spieler_index += 1
        if self.aktueller_spieler_index >= len(self.spieler_liste):
            self.aktueller_spieler_index = 0
            self.aktuelle_runde += 1

    def ist_spiel_beendet(self) -> bool:
        """Gibt True zurück wenn alle Runden gespielt wurden."""
        return self.aktuelle_runde > self.runden_gesamt

    # ── Aktionsmenü ──────────────────────────────────────────────────────────

    def aktionsmenue_anzeigen(self, spieler: Spieler, jahreszeit: Jahreszeit) -> None:
        """
        Zeigt das Aktionsmenü für den aktuellen Spieler an.
        Nicht alle Aktionen sind in jeder Jahreszeit verfügbar.
        """
        print(f"\n  +── Aktionen für {spieler.name} ──────────────+")
        print(f"  | Kapital : {spieler.geld:>12,.2f} EUR          |")
        print(
            f"  | Öchsle  : {spieler.weinberg.oechsle_aktuell:>4}°"
            f"                             |"
        )
        print(f"  +─────────────────────────────────────────────+")
        print(
            f"  | [1] Weinberg düngen      "
            f"({Spieler.__mro__[0].__module__} "  # Platzhalter
            f"-{spieler.weinberg.KOSTEN_DUENGER:,.0f} EUR)  |"
        )
        print(
            f"  | [1] Weinberg düngen      "
            f"(-{spieler.weinberg.KOSTEN_DUENGER:,.0f} EUR)         |"
        )

        # Schädlingsbekämpfung nur wenn Befall vorliegt
        if spieler.weinberg.schaedlingsbefall:
            print(
                f"  | [2] Schädlinge bekämpfen "
                f"(-{spieler.weinberg.KOSTEN_SCHAEDLINGE:,.0f} EUR) ⚠|"
            )
        else:
            print(f"  | [2] Schädlinge bekämpfen " f"(kein Befall)            |")

        # Weinlese nur im Herbst
        if jahreszeit == Jahreszeit.HERBST:
            print(f"  | [3] Weinlese starten                        |")
        else:
            print(f"  | [3] Weinlese starten     " f"(nur im Herbst)          |")

        print(f"  | [4] Weinberg-Status anzeigen                |")
        print(f"  | [5] Zug beenden                             |")
        print(f"  +─────────────────────────────────────────────+")

    def spieler_zug(
        self,
        spieler: Spieler,
        jahreszeit: Jahreszeit,
        wetter_bonus: int,
        ist_frost: bool,
    ) -> bool:
        """
        Verwaltet den kompletten Zug eines Spielers.
        Der Spieler kann mehrere Aktionen pro Zug ausführen.

        Returns:
            True wenn Weinlese durchgeführt wurde
        """
        weinlese_durchgefuehrt = False

        while True:
            # Aktionsmenü anzeigen
            print(f"\n  +── Aktionsmenü ──────────────────────────────+")
            print(f"  | Spieler  : {spieler.name:<33}|")
            print(f"  | Kapital  : {spieler.geld:>12,.2f} EUR              |")
            print(
                f"  | Öchsle   : {spieler.weinberg.oechsle_aktuell:>4}°"
                f"                              |"
            )
            print(f"  | Jahreszeit: {jahreszeit.value:<32}|")
            print(f"  +─────────────────────────────────────────────+")
            print(
                f"  | [1] Düngen         "
                f"(-{spieler.weinberg.KOSTEN_DUENGER:,.0f} EUR)            |"
            )

            # Schädlinge: Warnung wenn Befall
            if spieler.weinberg.schaedlingsbefall:
                print(
                    f"  | [2] Schädlinge ⚠   "
                    f"(-{spieler.weinberg.KOSTEN_SCHAEDLINGE:,.0f} EUR)         |"
                )
            else:
                print(f"  | [2] Schädlinge     (kein Befall)            |")

            # Weinlese nur im Herbst möglich
            if jahreszeit == Jahreszeit.HERBST and not weinlese_durchgefuehrt:
                if ist_frost and spieler.weinberg.region.eiswein_moeglich:
                    print(f"  | [3] Weinlese / Eiswein wagen  ❄           |")
                else:
                    print(f"  | [3] Weinlese starten                        |")
            else:
                print(f"  | [3] Weinlese       (nur im Herbst)          |")

            print(f"  | [4] Status anzeigen                         |")
            print(f"  | [5] Zug beenden                             |")
            print(f"  +─────────────────────────────────────────────+")

            try:
                wahl = input("  Deine Wahl: ").strip()
            except (EOFError, KeyboardInterrupt):
                break

            # ── Aktion 1: Düngen ──────────────────────────
            if wahl == "1":
                spieler.weinberg_duengen()

            # ── Aktion 2: Schädlinge bekämpfen ────────────
            elif wahl == "2":
                if spieler.weinberg.schaedlingsbefall:
                    spieler.schaedlinge_bekaempfen()
                else:
                    print("  Kein Schädlingsbefall vorhanden.")

            # ── Aktion 3: Weinlese ────────────────────────
            elif wahl == "3":
                if jahreszeit != Jahreszeit.HERBST:
                    print("  ⚠ Weinlese ist nur im Herbst möglich!")
                elif weinlese_durchgefuehrt:
                    print("  ⚠ Weinlese wurde bereits durchgeführt!")
                else:
                    # Eiswein-Entscheidung bei Frost
                    if ist_frost and spieler.weinberg.region.eiswein_moeglich:
                        weinlese_durchgefuehrt = self._eiswein_entscheidung(spieler)
                    else:
                        weinlese_durchgefuehrt = True
                        print("  ✓ Weinlese wird durchgeführt!")

            # ── Aktion 4: Status anzeigen ─────────────────
            elif wahl == "4":
                print(spieler.get_status())
                spieler.weinberg_status()

            # ── Aktion 5: Zug beenden ─────────────────────
            elif wahl == "5":
                print(f"  {spieler.name} beendet seinen Zug.")
                break

            else:
                print("  Ungültige Eingabe – bitte 1 bis 5.")

        return weinlese_durchgefuehrt

    def _eiswein_entscheidung(self, spieler: Spieler) -> bool:
        """
        Fragt den Spieler ob er Eiswein wagen möchte.

        Eiswein = hohes Risiko, hohe Belohnung:
          - Frost jetzt → sehr hoher Öchsle-Wert
          - Kein Frost mehr → Trauben verfaulen!

        Returns:
            True wenn normale Weinlese,
            False wenn auf Eiswein gewartet wird
        """
        print("\n  ❄  FROST! Eiswein-Chance!")
        print("  " + "─" * 46)
        print("  Normale Weinlese jetzt:")
        print(f"    → Sicher, aktuell {spieler.weinberg.oechsle_aktuell}°")
        print("  Auf Eiswein warten:")
        print("    → Öchsle steigt auf ~115° bei weiterem Frost")
        print("    → Aber: Kein Frost mehr = Trauben verfaulen! ☠")
        print("  " + "─" * 46)

        while True:
            wahl = input("  Jetzt ernten [j] oder Eiswein wagen [e]? ").strip().lower()
            if wahl == "j":
                print("  ✓ Normale Weinlese wird durchgeführt.")
                return True
            elif wahl == "e":
                # Eiswein: Öchsle auf 115° setzen
                spieler.weinberg.oechsle_aktuell = 115
                spieler.aktion_aufzeichnen("Eiswein gewagt!")
                print("  ❄ Eiswein! Öchsle auf 115° gesetzt!")
                print("  Trauben werden bis zum ersten Frost " "hängen gelassen.")
                return True
            else:
                print("  Bitte [j] oder [e] eingeben.")

    # ── Hauptspielschleife ───────────────────────────────────────────────────

    def spielen(self) -> None:
        """
        Hauptspielschleife – läuft bis alle Runden gespielt sind.

        Ablauf pro Runde:
          1. Jahreszeit & Wetter bestimmen
          2. Jeden Spieler seinen Zug machen lassen
          3. Weinberg-Runde abschließen (Öchsle berechnen)
          4. Nach letztem Spieler: neue Runde
        """
        print("\n" + "=" * 52)
        print(f"  '{self.spiel_name}' beginnt!")
        print(f"  {self.runden_gesamt} Runden " f"({self.runden_gesamt // 4} Jahre)")
        print("=" * 52)

        while not self.ist_spiel_beendet():
            # ── Jahreszeit & Wetter ───────────────────────
            jahreszeit = jahreszeit_berechnen(self.aktuelle_runde)
            jahreszeit_anzeigen(jahreszeit, self.aktuelle_runde)

            # Wetter für alle Spieler gleich pro Runde
            wetter = wetter_wuerfeln(jahreszeit)
            print(f"\n  Wetter diese Runde:")
            print(f"  {wetter}")

            # ── Jeden Spieler dran lassen ─────────────────
            for spieler in self.spieler_liste:
                print(f"\n  {'═' * 46}")
                print(f"  Spieler am Zug: {spieler.name}")
                print(f"  {'═' * 46}")

                # Spieler-Zug durchführen
                self.spieler_zug(
                    spieler,
                    jahreszeit,
                    wetter.oechsle_bonus,
                    wetter.ist_frost,
                )

                # Weinberg-Runde abschließen
                spieler.weinberg.runde_abschliessen(jahreszeit, wetter)

                # Spieler-Runde abschließen
                spieler.runde_abschliessen()

            # ── Rangliste nach jeder Runde ────────────────
            self.rangliste_anzeigen()

            # Nächste Runde
            self.aktuelle_runde += 1

        # ── Spielende ─────────────────────────────────────
        self._spielende_anzeigen()

    def _spielende_anzeigen(self) -> None:
        """Zeigt das Spielende mit Sieger an."""
        print("\n" + "=" * 52)
        print("  SPIELENDE!")
        print("=" * 52)
        rangliste = self.get_rangliste()
        sieger = rangliste[0]
        print(f"\n  🏆 Sieger: {sieger.name}")
        print(f"  Region  : {sieger.region.name.value}")
        print(f"  Kapital : {sieger.geld:,.2f} EUR")
        print(f"  Öchsle  : {sieger.weinberg.oechsle_aktuell}°")
        print("\n  Endrangliste:")
        self.rangliste_anzeigen()

    # ── Rangliste ────────────────────────────────────────────────────────────

    def get_rangliste(self) -> List[Spieler]:
        """Gibt alle Spieler nach Kapital sortiert zurück."""
        return sorted(self.spieler_liste, key=lambda s: s.geld, reverse=True)

    def rangliste_anzeigen(self) -> None:
        """Gibt die aktuelle Rangliste auf der Konsole aus."""
        print("\n  === Rangliste ===")
        print(f"  {'Pl.':<4} {'Name':<18} " f"{'Kapital':>14}  {'Öchsle':>7}")
        print("  " + "─" * 48)
        for platz, spieler in enumerate(self.get_rangliste(), start=1):
            print(
                f"  {platz:<4} "
                f"{spieler.name:<18} "
                f"{spieler.geld:>14,.2f} EUR  "
                f"{spieler.weinberg.oechsle_aktuell:>4}°"
            )

    # ── Spielinfo ────────────────────────────────────────────────────────────

    def spielinfo_anzeigen(self) -> None:
        """Zeigt allgemeine Spielinformationen an."""
        jahreszeit = jahreszeit_berechnen(self.aktuelle_runde)
        print(f"\n  Spiel      : {self.spiel_name}")
        print(f"  Runde      : {self.aktuelle_runde}" f" / {self.runden_gesamt}")
        print(f"  Jahreszeit : {jahreszeit.value}")
        print(f"  Spieler    : {len(self.spieler_liste)}")

    # ── Serialisierung ───────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        """Wandelt das gesamte Spiel in ein Dictionary um."""
        return {
            "spiel_name": self.spiel_name,
            "aktuelle_runde": self.aktuelle_runde,
            "aktueller_spieler_index": self.aktueller_spieler_index,
            "runden_gesamt": self.runden_gesamt,
            "spieler_liste": [s.to_dict() for s in self.spieler_liste],
        }

    @classmethod
    def from_dict(cls, daten: dict) -> "Spiel":
        """Erstellt ein Spiel aus einem Dictionary."""
        spiel = cls(spiel_name=daten["spiel_name"])
        spiel.aktuelle_runde = daten["aktuelle_runde"]
        spiel.aktueller_spieler_index = daten["aktueller_spieler_index"]
        spiel.runden_gesamt = daten.get("runden_gesamt", RUNDEN_GESAMT)
        spiel.spieler_liste = [Spieler.from_dict(s) for s in daten["spieler_liste"]]
        return spiel

    # ── Speichern & Laden ────────────────────────────────────────────────────

    def speichern(self) -> None:
        """Speichert den aktuellen Spielstand als JSON-Datei."""
        os.makedirs(SPEICHER_ORDNER, exist_ok=True)
        dateiname = os.path.join(
            SPEICHER_ORDNER, self.spiel_name.replace(" ", "_") + ".json"
        )
        with open(dateiname, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        print(f"\n  ✓ Spielstand gespeichert: {dateiname}")

    @classmethod
    def laden(cls, dateiname: str) -> "Spiel":
        """Lädt einen Spielstand aus einer JSON-Datei."""
        with open(dateiname, "r", encoding="utf-8") as f:
            daten = json.load(f)
        print(f"  ✓ Spielstand geladen: {dateiname}")
        return cls.from_dict(daten)


# ─────────────────────────────────────────────────────────────────────────────
# Self-Test
# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    """
    Testet die Spielverwaltung ohne interaktive Eingaben.
    Simuliert ein komplettes 2-Spieler-Spiel über 4 Runden
    mit festen Wetterdaten.
    """
    from region import REGIONEN, RegionName
    from grape import TRAUBEN, Rebsorte
    from weather import (
        WETTER_EREIGNISSE,
        Wetterzustand,
        jahreszeit_berechnen,
        jahreszeit_anzeigen,
    )

    print("=" * 52)
    print("  SPIEL – Self-Test (automatisch, keine Eingaben)")
    print("=" * 52)

    # ── Schritt 1: Spiel & Spieler anlegen ───────────────
    print("\n  Schritt 1: Spiel anlegen")
    spiel = Spiel(spiel_name="Test-001")

    # Spieler 1: Anna – Mosel – Riesling
    anna = Spieler("Arite Zastrow", REGIONEN[RegionName.MOSEL])
    anna.reben_anpflanzen(TRAUBEN[Rebsorte.RIESLING])
    spiel.spieler_liste.append(anna)

    # Spieler 2: Ben – Pfalz – Dornfelder
    ben = Spieler("Rene Kallenbach", REGIONEN[RegionName.PFALZ])
    ben.reben_anpflanzen(TRAUBEN[Rebsorte.DORNFELDER])
    spiel.spieler_liste.append(ben)

    print(f"  Spieler: {[s.name for s in spiel.spieler_liste]}")
    spiel.spielinfo_anzeigen()

    # ── Schritt 2: 4 Runden automatisch simulieren ───────
    print("\n  Schritt 2: 4 Runden simulieren")

    # Feste Wetter für reproduzierbare Tests
    test_wetter = [
        Wetterzustand.NORMAL,  # Runde 1 – Frühling
        Wetterzustand.IDEAL,  # Runde 2 – Sommer
        Wetterzustand.REGEN,  # Runde 3 – Herbst
        Wetterzustand.FROST,  # Runde 4 – Winter
    ]

    for runde in range(1, 5):
        jahreszeit = jahreszeit_berechnen(runde)
        jahreszeit_anzeigen(jahreszeit, runde)
        wetter = WETTER_EREIGNISSE[test_wetter[runde - 1]]
        print(
            f"  Wetter: {wetter.zustand.value} "
            f"({'+' if wetter.oechsle_bonus >= 0 else ''}"
            f"{wetter.oechsle_bonus}°)"
        )

        for spieler in spiel.spieler_liste:
            # Düngen in Frühling & Sommer
            if jahreszeit in (Jahreszeit.FRUEHLING, Jahreszeit.SOMMER):
                spieler.weinberg_duengen()

            # Weinberg-Runde abschließen
            spieler.weinberg.runde_abschliessen(jahreszeit, wetter)
            spieler.runde_abschliessen()

        spiel.aktuelle_runde += 1

    # ── Schritt 3: Rangliste anzeigen ─────────────────────
    print("\n  Schritt 3: Rangliste")
    spiel.rangliste_anzeigen()

    # ── Schritt 4: Serialisierung testen ──────────────────
    print("\n  Schritt 4: Speichern & Laden")
    spiel.speichern()

    # Laden und vergleichen
    dateiname = os.path.join(SPEICHER_ORDNER, f"{spiel.spiel_name}.json")
    spiel2 = Spiel.laden(dateiname)

    gleich = (
        spiel.spiel_name == spiel2.spiel_name
        and spiel.aktuelle_runde == spiel2.aktuelle_runde
        and len(spiel.spieler_liste) == len(spiel2.spieler_liste)
        and spiel.spieler_liste[0].weinberg.oechsle_aktuell
        == spiel2.spieler_liste[0].weinberg.oechsle_aktuell
    )
    print(f"  Identisch: {'✓ Ja' if gleich else '✗ Nein'}")

    # ── Schritt 5: Zusammenfassung ────────────────────────
    print("\n" + "=" * 52)
    print("  Testergebnisse:")
    print("  " + "─" * 40)
    rangliste = spiel.get_rangliste()
    tests = [
        ("Spiel angelegt", spiel.spiel_name == "Testspiel"),
        ("2 Spieler vorhanden", len(spiel.spieler_liste) == 2),
        ("4 Runden gespielt", spiel.aktuelle_runde == 5),
        ("Öchsle aufgebaut", anna.weinberg.oechsle_aktuell > 0),
        ("Rangliste korrekt", len(rangliste) == 2),
        ("Serialisierung", gleich),
    ]
    alle_ok = True
    for test_name, ergebnis in tests:
        symbol = "✓" if ergebnis else "✗"
        print(f"  [{symbol}] {test_name}")
        if not ergebnis:
            alle_ok = False

    print("  " + "─" * 40)
    print(f"  Gesamt: {'✓ Alle Tests bestanden!' if alle_ok else '✗ Fehler!'}")
    print("=" * 52)


if __name__ == "__main__":
    main()
