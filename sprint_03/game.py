"""
game.py – Spielverwaltungs-Modul (Sprint 3, korrigiert)
=========================================================
Korrekturen:
  - spielen(): herbst_vorbereiten() wird VOR spieler_zug()
    aufgerufen → Spieler sieht Erntereife sofort im Herbst
  - Eiswein-Auflösung im Winter korrekt integriert

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

SPEICHER_ORDNER = "saves"
RUNDEN_GESAMT = 72  # 3 Jahre


# ─────────────────────────────────────────────────────────────────────────────
# Klasse: Spiel
# ─────────────────────────────────────────────────────────────────────────────
class Spiel:

    def __init__(self, spiel_name: str = "") -> None:
        self.spiel_name: str = spiel_name
        self.spieler_liste: List[Spieler] = []
        self.aktuelle_runde: int = 1
        self.aktueller_spieler_index: int = 0
        self.runden_gesamt: int = RUNDEN_GESAMT

    # ── Spieleinrichtung ─────────────────────────────────────────────────────

    def setup_spiel(self) -> None:
        print("\n" + "=" * 54)
        print("  NEUES SPIEL EINRICHTEN")
        print("=" * 54)

        eingabe = input("\n  Name für dieses Spiel: ").strip()
        self.spiel_name = eingabe if eingabe else "Winzer-Spiel"

        while True:
            try:
                anzahl = int(input("  Anzahl Spieler (2–4): "))
                if 2 <= anzahl <= 4:
                    break
                print("  Bitte 2–4 eingeben.")
            except ValueError:
                print("  Ungültige Eingabe.")

        for i in range(1, anzahl + 1):
            print(f"\n  {'─' * 48}")
            print(f"  Spieler {i} einrichten")
            print(f"  {'─' * 48}")
            name_eingabe = input(f"  Name: ").strip()
            name = name_eingabe or f"Spieler {i}"
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

    # ── Aktionsmenüs ─────────────────────────────────────────────────────────

    def _menue_weinberg(
        self,
        spieler: Spieler,
        jahreszeit: Jahreszeit,
        ist_frost: bool,
    ) -> None:
        print(f"\n  +── Weinberg ───────────────────────────────+")
        print(
            f"  | [1] Düngen"
            f"        (-{spieler.weinberg.KOSTEN_DUENGER:,.0f} EUR)"
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

        # Weinlese
        if jahreszeit == Jahreszeit.HERBST and spieler.weinberg.ernte_bereit:
            print(
                f"  | [3] Weinlese ✓"
                f"     ({spieler.weinberg.oechsle_aktuell}°"
                f" Öchsle)              |"
            )
        elif jahreszeit == Jahreszeit.HERBST:
            print(f"  | [3] Weinlese" f"       (noch nicht reif)             |")
        else:
            print(f"  | [3] Weinlese" f"       (nur im Herbst)               |")

        # Eiswein
        if (
            jahreszeit == Jahreszeit.HERBST
            and spieler.weinberg.ernte_bereit
            and spieler.weinberg.region.eiswein_moeglich
        ):
            frost_hint = "❄ Frost!" if ist_frost else "kein Frost"
            print(f"  | [4] Eiswein wagen  ({frost_hint})" f"                  |")
        else:
            print(f"  | [4] Eiswein wagen" f"   (nur Herbst + Region)          |")

        print(f"  +───────────────────────────────────────────+")

    def _menue_kellerei(self, spieler: Spieler) -> None:
        fasser_reif = spieler.keller.get_fass_liste_reif()
        fasser_most = [
            f for f in spieler.keller.fass_liste if f.zustand == Fasszustand.MOST
        ]
        fasser_gaerung = [
            f for f in spieler.keller.fass_liste if f.zustand == Fasszustand.GAERUNG
        ]

        print(f"\n  +── Kellerei ───────────────────────────────+")

        if spieler.weinberg.ernte_verfuegbar:
            print(
                f"  | [5] Keltern ✓"
                f"      (-{spieler.keller.KOSTEN_KELTERN:,.0f} EUR)"
                f"           |"
            )
        else:
            print(f"  | [5] Keltern" f"         (keine Ernte)                |")

        ids = [str(f.fass_id) for f in fasser_most]
        print(
            f"  | [6] Gärung start."
            f"   {('Fass: '+','.join(ids)) if ids else '(kein Most)':<25}|"
        )

        ids = [str(f.fass_id) for f in fasser_gaerung]
        print(
            f"  | [7] Gärung abschl."
            f"  {('Fass: '+','.join(ids)) if ids else '(keine Gärung)':<24}|"
        )

        ids = [str(f.fass_id) for f in fasser_reif]
        print(
            f"  | [8] Lagern"
            f"          {('Fass: '+','.join(ids)) if ids else '(kein reifes Fass)':<23}|"
        )

        if fasser_reif:
            print(
                f"  | [9] Abfüllen"
                f"        (-{spieler.keller.KOSTEN_ABFUELLEN:,.0f} EUR)"
                f"           |"
            )
        else:
            print(f"  | [9] Abfüllen" f"        (kein reifes Fass)            |")

        if spieler.keller.flaschen_liste:
            wert = spieler.keller.get_gesamtwert_flaschen()
            print(
                f"  | [V] Verkaufen"
                f"       ({len(spieler.keller.flaschen_liste)}"
                f" Fl. ~{wert:,.0f}€)            |"
            )
        else:
            print(f"  | [V] Verkaufen" f"       (keine Flaschen)               |")

        print(f"  +───────────────────────────────────────────+")

    def _menue_sonstiges(self, spieler: Spieler) -> None:
        rathaus = "✓ angemeldet" if spieler.rathaus_angemeldet else "noch nicht"
        print(f"\n  +── Sonstiges ──────────────────────────────+")
        print(f"  | [S] Status                                |")
        print(f"  | [R] Rathaus ({rathaus:<28})  |")
        print(f"  | [X] Zug beenden                           |")
        print(f"  | [Q] Spiel beenden                         |")
        print(f"  +───────────────────────────────────────────+")

    # ── Spieler-Zug ──────────────────────────────────────────────────────────

    def spieler_zug(
        self,
        spieler: Spieler,
        jahreszeit: Jahreszeit,
        ist_frost: bool,
    ) -> None:
        """Verwaltet den Zug eines Spielers."""
        while True:
            print(f"\n  {'═' * 48}")
            print(
                f"  {spieler.name}"
                f" | {spieler.geld:,.0f}€"
                f" | {spieler.weinberg.oechsle_aktuell}°"
                f" | {jahreszeit.value}"
            )
            if spieler.weinberg.eiswein_wartend:
                print(f"  ❄ Wartet auf Eiswein!")
            if spieler.weinberg.ernte_bereit:
                print(f"  🍇 Ernte bereit:" f" {spieler.weinberg.oechsle_aktuell}°!")
            if spieler.weinberg.ernte_verfuegbar:
                print(
                    f"  🍷 Ernte im Keller:"
                    f" {spieler.weinberg.ernte_oechsle}°"
                    f" – jetzt keltern!"
                )
            print(f"  {'═' * 48}")

            self._menue_weinberg(spieler, jahreszeit, ist_frost)
            self._menue_kellerei(spieler)
            self._menue_sonstiges(spieler)

            try:
                wahl = input("\n  Wahl: ").strip().upper()
            except (EOFError, KeyboardInterrupt):
                break

            # ── Weinberg ──────────────────────────────────
            if wahl == "1":
                spieler.weinberg_duengen()

            elif wahl == "2":
                if spieler.weinberg.schaedlingsbefall:
                    spieler.schaedlinge_bekaempfen()
                else:
                    print("  Kein Schädlingsbefall.")

            elif wahl == "3":
                if jahreszeit != Jahreszeit.HERBST:
                    print("  ⚠ Nur im Herbst möglich!")
                elif not spieler.weinberg.ernte_bereit:
                    print("  ⚠ Trauben noch nicht reif!")
                else:
                    spieler.weinlese_durchfuehren()

            elif wahl == "4":
                if jahreszeit != Jahreszeit.HERBST:
                    print("  ⚠ Nur im Herbst möglich!")
                elif not spieler.weinberg.ernte_bereit:
                    print("  ⚠ Trauben noch nicht reif!")
                elif not spieler.weinberg.region.eiswein_moeglich:
                    print("  ⚠ In dieser Region kein Eiswein!")
                else:
                    if not ist_frost:
                        print("  ⚠ Kein Frost – Risiko hoch!")
                        best = input("  Trotzdem wagen? [j/n]: ").strip().lower()
                        if best != "j":
                            continue
                    spieler.eiswein_wagen()

            # ── Kellerei ──────────────────────────────────
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
                    fid = self._fass_auswaehlen(fasser)
                    if fid:
                        spieler.fass_gaerung_starten(fid)

            elif wahl == "7":
                fasser = [
                    f
                    for f in spieler.keller.fass_liste
                    if f.zustand == Fasszustand.GAERUNG
                ]
                if not fasser:
                    print("  Keine Gärung aktiv.")
                else:
                    fid = self._fass_auswaehlen(fasser)
                    if fid:
                        spieler.fass_gaerung_abschliessen(fid)

            elif wahl == "8":
                fasser = spieler.keller.get_fass_liste_reif()
                if not fasser:
                    print("  Kein reifes Fass.")
                else:
                    fid = self._fass_auswaehlen(fasser)
                    if fid:
                        monate = self._monate_abfragen()
                        spieler.fass_lagern(fid, monate)

            elif wahl == "9":
                fasser = spieler.keller.get_fass_liste_reif()
                if not fasser:
                    print("  Kein reifes Fass.")
                else:
                    fid = self._fass_auswaehlen(fasser)
                    if fid:
                        spieler.wein_abfuellen(fid)

            elif wahl == "V":
                if not spieler.keller.flaschen_liste:
                    print("  Keine Flaschen.")
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

            elif wahl == "Q":
                print(f"  {spieler.name} beendet das Spiel.")
                self.aktuelle_runde = self.runden_gesamt + 1  # Spielende erzwingen
                break

            else:
                print("  Ungültige Eingabe.")

    # ── Hilfsmethoden ────────────────────────────────────────────────────────

    def _fass_auswaehlen(self, fasser: list) -> Optional[int]:
        if len(fasser) == 1:
            return fasser[0].fass_id
        print("\n  Welches Fass?")
        for i, f in enumerate(fasser, 1):
            print(
                f"  [{i}] Fass #{f.fass_id}"
                f" – {f.rebsorte}"
                f" {f.oechsle}°"
                f" {f.lager_monate}Mo."
            )
        print("  [0] Abbrechen")
        while True:
            try:
                w = int(input("  Wahl: "))
                if w == 0:
                    return None
                if 1 <= w <= len(fasser):
                    return fasser[w - 1].fass_id
                print(f"  0–{len(fasser)} eingeben.")
            except ValueError:
                print("  Ungültige Eingabe.")

    def _monate_abfragen(self) -> int:
        while True:
            try:
                m = int(input("  Monate lagern (1–12): "))
                if 1 <= m <= 72:
                    return m
                print("  1–12 eingeben.")
            except ValueError:
                print("  Ungültige Eingabe.")

    def _anzahl_abfragen(self, max_anzahl: int) -> Optional[int]:
        print(f"  [0] Alle ({max_anzahl} Flaschen)")
        while True:
            try:
                a = int(input(f"  Anzahl (0=alle, max {max_anzahl}): "))
                if a == 0:
                    return None
                if 1 <= a <= max_anzahl:
                    return a
                print(f"  0–{max_anzahl} eingeben.")
            except ValueError:
                print("  Ungültige Eingabe.")

    def _rathaus_anmelden(self, spieler: Spieler) -> None:
        if spieler.rathaus_angemeldet:
            print("  Bereits angemeldet.")
            return
        KOSTEN = 2_000.0
        print(f"  Rathaus-Anmeldung: {KOSTEN:,.0f} EUR")
        if not spieler.geld_abziehen(KOSTEN):
            return
        spieler.rathaus_angemeldet = True
        spieler.lizenzen.append("Weinverkauf-Lizenz")
        spieler.aktion_aufzeichnen(f"Rathaus (-{KOSTEN:,.0f} EUR)")
        print("  ✓ Weinverkauf-Lizenz erhalten!")
        print(f"  Kapital: {spieler.geld:,.2f} EUR")

    # ── Hauptspielschleife ───────────────────────────────────────────────────

    def spielen(self) -> None:
        """
        Hauptspielschleife – korrigierte Reihenfolge:

          1. Jahreszeit & Wetter bestimmen
          2. Für jeden Spieler:
             a. herbst_vorbereiten() falls Herbst  ← NEU/FIX
             b. spieler_zug()
             c. runde_abschliessen()
          3. Rangliste anzeigen
          4. Nächste Runde
        """
        print("\n" + "=" * 54)
        print(f"  '{self.spiel_name}' – Los geht's!")
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
            if wetter.ist_frost:
                print(f"  ❄ Frost! Eiswein möglich!")

            for spieler in self.spieler_liste:
                print(f"\n  {'═' * 48}")
                print(f"  Am Zug: {spieler.name}")
                print(f"  {'═' * 48}")

                # ── KORREKTUR: Herbst VOR Spielerzug vorbereiten ──
                if jahreszeit == Jahreszeit.HERBST:
                    spieler.weinberg.herbst_vorbereiten()

                # Spielerzug
                self.spieler_zug(
                    spieler,
                    jahreszeit,
                    wetter.ist_frost,
                )

                # Weinberg-Runde abschließen
                spieler.weinberg.runde_abschliessen(jahreszeit, wetter)
                spieler.runde_abschliessen()

            # Rangliste nach jeder Runde
            self.rangliste_anzeigen()
            self.aktuelle_runde += 1

        self._spielende_anzeigen()

    def _spielende_anzeigen(self) -> None:
        print("\n" + "=" * 54)
        print("  SPIELENDE!")
        print("=" * 54)
        sieger = self.get_rangliste()[0]
        gesamt = sieger.geld + sieger.keller.get_gesamtwert_flaschen()
        print(f"\n  🏆 Sieger : {sieger.name}")
        print(f"  Region   : {sieger.region.name.value}")
        print(f"  Kapital  : {sieger.geld:,.2f} EUR")
        print(f"  Keller   :" f" {sieger.keller.get_gesamtwert_flaschen():,.2f} EUR")
        print(f"  Gesamt   : {gesamt:,.2f} EUR")
        self.rangliste_anzeigen()

    # ── Rangliste ────────────────────────────────────────────────────────────

    def get_rangliste(self) -> List[Spieler]:
        return sorted(
            self.spieler_liste,
            key=lambda s: (s.geld + s.keller.get_gesamtwert_flaschen()),
            reverse=True,
        )

    def rangliste_anzeigen(self) -> None:
        print("\n  === Rangliste ===")
        print(
            f"  {'Pl.':<4} {'Name':<16}"
            f" {'Kapital':>12}"
            f" {'Keller':>10}"
            f" {'Gesamt':>12}"
        )
        print("  " + "─" * 58)
        for pl, s in enumerate(self.get_rangliste(), 1):
            kw = s.keller.get_gesamtwert_flaschen()
            gesamt = s.geld + kw
            print(
                f"  {pl:<4} {s.name:<16}"
                f" {s.geld:>11,.0f}€"
                f" {kw:>9,.0f}€"
                f" {gesamt:>11,.0f}€"
            )

    def spielinfo_anzeigen(self) -> None:
        jahreszeit = jahreszeit_berechnen(self.aktuelle_runde)
        print(f"\n  Spiel     : {self.spiel_name}")
        print(f"  Runde     : {self.aktuelle_runde}" f"/{self.runden_gesamt}")
        print(f"  Jahreszeit: {jahreszeit.value}")
        print(f"  Spieler   : {len(self.spieler_liste)}")

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
        os.makedirs(SPEICHER_ORDNER, exist_ok=True)
        dateiname = os.path.join(
            SPEICHER_ORDNER, self.spiel_name.replace(" ", "_") + ".json"
        )
        with open(dateiname, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        print(f"\n  ✓ Gespeichert: {dateiname}")

    @classmethod
    def laden(cls, dateiname: str) -> "Spiel":
        with open(dateiname, "r", encoding="utf-8") as f:
            daten = json.load(f)
        print(f"  ✓ Geladen: {dateiname}")
        return cls.from_dict(daten)


# ─────────────────────────────────────────────────────────────────────────────
# Self-Test
# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    """
    Testet die korrigierte Spielschleife.
    Schwerpunkt: Herbst-Ernte korrekt verfügbar.
    """
    from region import REGIONEN, RegionName
    from grape import TRAUBEN, Rebsorte

    print("=" * 54)
    print("  SPIEL – Self-Test (Weinlese-Fix)")
    print("=" * 54)

    spiel = Spiel(spiel_name="Test-Fix")

    anna = Spieler("Anna", REGIONEN[RegionName.MOSEL])
    anna.reben_anpflanzen(TRAUBEN[Rebsorte.RIESLING])
    spiel.spieler_liste.append(anna)

    ben = Spieler("Ben", REGIONEN[RegionName.AHR])
    ben.reben_anpflanzen(TRAUBEN[Rebsorte.SPAETBURGUNDER])
    spiel.spieler_liste.append(ben)

    # 4 Runden automatisch
    test_wetter = [
        Wetterzustand.NORMAL,
        Wetterzustand.IDEAL,
        Wetterzustand.NORMAL,
        Wetterzustand.FROST,
    ]

    herbst_ernte_ok = False

    for runde in range(1, 5):
        jahreszeit = jahreszeit_berechnen(runde)
        wetter = WETTER_EREIGNISSE[test_wetter[runde - 1]]

        for spieler in spiel.spieler_liste:

            # ── KORREKTUR: herbst_vorbereiten VOR Zug ─────
            if jahreszeit == Jahreszeit.HERBST:
                spieler.weinberg.herbst_vorbereiten()

                # Prüfen ob ernte_bereit korrekt gesetzt
                if spieler.weinberg.ernte_bereit:
                    herbst_ernte_ok = True
                    print(f"  ✓ {spieler.name}:" f" ernte_bereit = True im Herbst!")

                # Automatisch ernten
                if spieler.weinberg.ernte_bereit:
                    spieler.weinlese_durchfuehren()
                    spieler.most_keltern()
                    fid = spieler.keller.naechste_fass_id - 1
                    spieler.fass_gaerung_starten(fid)

            elif jahreszeit in (Jahreszeit.FRUEHLING, Jahreszeit.SOMMER):
                spieler.weinberg_duengen()

            elif jahreszeit == Jahreszeit.WINTER:
                for fass in spieler.keller.fass_liste:
                    if fass.zustand == Fasszustand.GAERUNG:
                        spieler.fass_gaerung_abschliessen(fass.fass_id)
                        spieler.fass_lagern(fass.fass_id, 3)

            spieler.weinberg.runde_abschliessen(jahreszeit, wetter)
            spieler.runde_abschliessen()

        spiel.aktuelle_runde += 1

    # Abfüllen & Verkaufen
    for spieler in spiel.spieler_liste:
        for fass in spieler.keller.get_fass_liste_reif():
            spieler.wein_abfuellen(fass.fass_id)
        spieler.flaschen_verkaufen()

    spiel.rangliste_anzeigen()

    # Zusammenfassung
    print("\n" + "=" * 54)
    print("  Testergebnisse:")
    print("  " + "─" * 42)
    tests = [
        ("Herbst: ernte_bereit korrekt gesetzt", herbst_ernte_ok),
        ("Anna hat Erlös erzielt", anna.geld != 50_000.0),
        ("Ben hat Erlös erzielt", ben.geld != 50_000.0),
        ("Keine Flaschen mehr im Keller", len(anna.keller.flaschen_liste) == 0),
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
