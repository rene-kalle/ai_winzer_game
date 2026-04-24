"""
main.py – Einstiegspunkt des Winzer-Spiels (Sprint 3)
======================================================
Änderungen gegenüber Sprint 2:
  - Spielstand-Übersicht beim Laden verbessert
  - Gesamtvermögen (Kapital + Kellerwert) angezeigt
  - Sprint-3-Abschluss-Info aktualisiert

Ausführen mit:
  python main.py          → Spiel starten
  python main.py --test   → Self-Test

Sprint 3 – Ernte, Kellerei & Weinqualität
"""

import sys
import os
from game import Spiel, SPEICHER_ORDNER


# ─────────────────────────────────────────────────────────────────────────────
# ASCII-Logo
# ─────────────────────────────────────────────────────────────────────────────
LOGO = """
  +=====================================================+
  |                                                     |
  |    W  I  N  Z  E  R                                 |
  |    Das deutsche Weinbau-Spiel                       |
  |                                                     |
  |    Pflanze Reben an, ernte Trauben,                 |
  |    keltere feinen Wein und werde reich!             |
  |                                                     |
  |    (c) Hour of Code – Lernprojekt  [Sprint 3]       |
  +=====================================================+
"""


# ─────────────────────────────────────────────────────────────────────────────
# Hauptmenü
# ─────────────────────────────────────────────────────────────────────────────
def hauptmenue_anzeigen() -> None:
    """Zeigt das Hauptmenü an."""
    print("\n  +--------------------------------------------+")
    print("  |              HAUPTMENÜ                     |")
    print("  +--------------------------------------------+")
    print("  |  [1]  Neues Spiel starten                  |")
    print("  |  [2]  Spiel laden                          |")
    print("  |  [3]  Qualitätstabelle anzeigen            |")
    print("  |  [4]  Beenden                              |")
    print("  +--------------------------------------------+")


# ─────────────────────────────────────────────────────────────────────────────
# Spielstand laden
# ─────────────────────────────────────────────────────────────────────────────
def spielstand_auswaehlen() -> str | None:
    """
    Zeigt alle vorhandenen Spielstände an
    und lässt den Spieler einen auswählen.

    Returns:
        Dateipfad oder None wenn abgebrochen.
    """
    if not os.path.exists(SPEICHER_ORDNER):
        print("\n  Keine Spielstände vorhanden.")
        return None

    dateien = sorted([f for f in os.listdir(SPEICHER_ORDNER) if f.endswith(".json")])

    if not dateien:
        print("\n  Keine Spielstände vorhanden.")
        return None

    print("\n  Vorhandene Spielstände:")
    print("  " + "─" * 50)
    print(f"  {'Nr':<4} {'Name':<30} {'Größe':>8}")
    print("  " + "─" * 50)

    for i, datei in enumerate(dateien, start=1):
        pfad = os.path.join(SPEICHER_ORDNER, datei)
        groesse = os.path.getsize(pfad) / 1024
        name = datei.replace(".json", "").replace("_", " ")
        print(f"  [{i:2d}] {name:<30} {groesse:>6.1f} KB")

    print("  " + "─" * 50)
    print("  [ 0] Zurück")

    while True:
        try:
            wahl = int(input("\n  Deine Wahl: "))
            if wahl == 0:
                return None
            if 1 <= wahl <= len(dateien):
                return os.path.join(SPEICHER_ORDNER, dateien[wahl - 1])
            print(f"  Bitte 0–{len(dateien)} eingeben.")
        except ValueError:
            print("  Ungültige Eingabe.")


# ─────────────────────────────────────────────────────────────────────────────
# Willkommen-Anzeige
# ─────────────────────────────────────────────────────────────────────────────
def willkommen_anzeigen(spiel: Spiel) -> None:
    """Zeigt die Begrüßungsseite nach dem Setup."""
    from weather import jahreszeit_berechnen

    print("\n" + "=" * 54)
    print(f"  Willkommen zu '{spiel.spiel_name}'!")
    print("=" * 54)
    print(
        f"  {len(spiel.spieler_liste)} Spieler,"
        f" {spiel.runden_gesamt} Runden"
        f" ({spiel.runden_gesamt // 4} Jahre)\n"
    )

    for i, spieler in enumerate(spiel.spieler_liste, start=1):
        top_sorte = max(
            spieler.region.empfohlene_sorten,
            key=spieler.region.empfohlene_sorten.get,  # type: ignore
        )
        traube_str = (
            spieler.weinberg.traube.sorte.value if spieler.weinberg.traube else "Keine"
        )
        print(f"  {'─' * 48}")
        print(f"  Spieler {i}    : {spieler.name}")
        print(f"  Region       : {spieler.region.name.value}")
        print(f"  Rebsorte     : {traube_str}")
        print(f"  Startkapital : {spieler.geld:,.2f} EUR")
        print(f"  Beste Sorte  : {top_sorte}")
        if spieler.region.eiswein_moeglich:
            print(f"  ❄ Tipp       : Eiswein möglich" f" – riskant aber lukrativ!")
        print()

    jahreszeit = jahreszeit_berechnen(spiel.aktuelle_runde)
    print(f"  {'─' * 48}")
    print(f"  Startet mit: {jahreszeit.value}")
    print(f"  {'─' * 48}")
    input("\n  Drücke Enter um zu starten ...")


# ─────────────────────────────────────────────────────────────────────────────
# Geladener Spielstand – Übersicht
# ─────────────────────────────────────────────────────────────────────────────
def spielstand_uebersicht(spiel: Spiel) -> None:
    """
    Zeigt eine Übersicht des geladenen Spielstands.
    Neu in Sprint 3: Zeigt Kapital + Kellerwert.
    """
    from weather import jahreszeit_berechnen
    from winery import Fasszustand

    jahreszeit = jahreszeit_berechnen(spiel.aktuelle_runde)

    print("\n" + "=" * 54)
    print(f"  Spielstand: '{spiel.spiel_name}'")
    print("=" * 54)
    print(f"  Runde      : {spiel.aktuelle_runde}" f" / {spiel.runden_gesamt}")
    print(f"  Jahreszeit : {jahreszeit.value}")
    print(f"  Spieler    : {len(spiel.spieler_liste)}\n")

    for spieler in spiel.spieler_liste:
        keller_wert = spieler.keller.get_gesamtwert_flaschen()
        gesamt = spieler.geld + keller_wert
        fasser_aktiv = len(
            [
                f
                for f in spieler.keller.fass_liste
                if f.zustand != Fasszustand.ABGEFUELLT
            ]
        )
        traube_str = (
            spieler.weinberg.traube.sorte.value
            if spieler.weinberg.traube
            else "Nicht bepflanzt"
        )
        print(f"  {'─' * 48}")
        print(f"  {spieler.name}")
        print(f"    Rebsorte  : {traube_str}")
        print(f"    Öchsle    : {spieler.weinberg.oechsle_aktuell}°")
        print(f"    Kapital   : {spieler.geld:>12,.2f} EUR")
        print(
            f"    Keller    : {keller_wert:>12,.2f} EUR"
            f" ({len(spieler.keller.flaschen_liste)} Fl.,"
            f" {fasser_aktiv} Fässer)"
        )
        print(f"    Gesamt    : {gesamt:>12,.2f} EUR")
        if spieler.weinberg.eiswein_wartend:
            print(f"    ❄ Wartet auf Eiswein!")

    print(f"\n  {'─' * 48}")
    spiel.rangliste_anzeigen()


# ─────────────────────────────────────────────────────────────────────────────
# Speichern-Abfrage
# ─────────────────────────────────────────────────────────────────────────────
def speichern_abfragen(spiel: Spiel) -> None:
    """Fragt nach dem Spiel ob gespeichert werden soll."""
    while True:
        try:
            wahl = input("\n  Spielstand speichern? [j/n]: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            return
        if wahl == "j":
            spiel.speichern()
            return
        elif wahl == "n":
            return
        print("  Bitte [j] oder [n] eingeben.")


# ─────────────────────────────────────────────────────────────────────────────
# Qualitätstabelle anzeigen
# ─────────────────────────────────────────────────────────────────────────────
def qualitaetstabelle_anzeigen() -> None:
    """Zeigt die Qualitätstabelle aus market.py an."""
    from market import (
        QUALITAETS_TABELLE,
        LAGER_FAKTOR_PRO_MONAT,
        MAX_LAGER_MONATE,
        FARBE_LAGER_MULTIPLIKATOR,
    )

    print("\n" + "=" * 66)
    print("  Qualitätstabelle")
    print("=" * 66)
    print(
        f"  {'Stufe':<24} {'ab °':<6}"
        f" {'€ min':>7} {'€ max':>7}"
        f" {'Lager/Mo':>9} {'Max. Mon.':>10}"
    )
    print("  " + "─" * 64)

    for stufe, (min_o, p_min, p_max) in sorted(
        QUALITAETS_TABELLE.items(),
        key=lambda x: x[1][0],
    ):
        faktor = LAGER_FAKTOR_PRO_MONAT.get(stufe, 0)
        max_m = MAX_LAGER_MONATE.get(stufe, 0)
        eis = " ❄" if stufe == "Eiswein" else "  "
        print(
            f"  {stufe:<24}{eis} {min_o:>3}°"
            f" {p_min:>7.2f}€ {p_max:>7.2f}€"
            f" {faktor*100:>8.1f}% {max_m:>9} Mo."
        )

    print("  " + "─" * 64)
    print(
        f"\n  Rotwein-Lagerbonus: "
        f"×{FARBE_LAGER_MULTIPLIKATOR['rot']:.1f}"
        f" (Weißwein: ×{FARBE_LAGER_MULTIPLIKATOR['weiss']:.1f})"
    )
    print("  Regions-Bonus: prozentual je Region (4–10%)")
    print("=" * 66)
    input("\n  Drücke Enter zum Fortfahren ...")


def clear() -> None:
    """Löscht die Konsole (plattformabhängig)."""
    os.system("cls" if os.name == "nt" else "clear")


# ─────────────────────────────────────────────────────────────────────────────
# Hauptfunktion
# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    """Hauptfunktion – startet das Spiel."""
    clear()
    print(LOGO)

    while True:
        hauptmenue_anzeigen()

        try:
            wahl = input("\n  Deine Wahl (1/2/3/4): ").strip()
            clear()
        except (EOFError, KeyboardInterrupt):
            print("\n\n  Auf Wiedersehen! Prost! 🍷")
            sys.exit(0)

        # ── [1] Neues Spiel ───────────────────────────────
        if wahl == "1":
            spiel = Spiel()
            spiel.setup_spiel()
            willkommen_anzeigen(spiel)
            spiel.spielen()
            speichern_abfragen(spiel)

            try:
                weiter = input("\n  Zurück zum Hauptmenü? [j/n]: ").strip().lower()
                if weiter != "j":
                    print("\n  Auf Wiedersehen! Prost! 🍷")
                    sys.exit(0)
            except (EOFError, KeyboardInterrupt):
                sys.exit(0)

        # ── [2] Spiel laden ───────────────────────────────
        elif wahl == "2":
            dateiname = spielstand_auswaehlen()
            if dateiname is None:
                continue

            try:
                spiel = Spiel.laden(dateiname)
                spielstand_uebersicht(spiel)
                input("\n  Drücke Enter um weiterzuspielen ...")
                spiel.spielen()
                speichern_abfragen(spiel)

            except FileNotFoundError:
                print(f"  ⚠ Datei nicht gefunden: {dateiname}")
            except Exception as fehler:
                print(f"  ⚠ Fehler beim Laden: {fehler}")

        # ── [3] Qualitätstabelle ──────────────────────────
        elif wahl == "3":
            qualitaetstabelle_anzeigen()
            clear()

        # ── [4] Beenden ───────────────────────────────────
        elif wahl == "4":
            print("\n  Auf Wiedersehen! Viel Erfolg! 🍷")
            sys.exit(0)

        else:
            print("  Ungültige Eingabe – bitte 1, 2, 3 oder 4.")


# ─────────────────────────────────────────────────────────────────────────────
# Self-Test
# ─────────────────────────────────────────────────────────────────────────────
def self_test() -> None:
    """
    Testet alle Funktionen von main.py
    ohne interaktive Eingaben.
    """
    from region import REGIONEN, RegionName
    from grape import TRAUBEN, Rebsorte
    from weather import jahreszeit_berechnen
    from market import preis_berechnen

    print("=" * 54)
    print("  MAIN – Self-Test (Sprint 3)")
    print("=" * 54)

    # ── Schritt 1: Logo ───────────────────────────────────
    print("\n  Schritt 1: Logo")
    print(LOGO)

    # ── Schritt 2: Testspiel anlegen ──────────────────────
    print("\n  Schritt 2: Testspiel anlegen")
    spiel = Spiel(spiel_name="Main-Test-S3")

    from player import Spieler

    anna = Spieler("Anna", REGIONEN[RegionName.MOSEL])
    anna.reben_anpflanzen(TRAUBEN[Rebsorte.RIESLING])
    spiel.spieler_liste.append(anna)

    ben = Spieler("Ben", REGIONEN[RegionName.AHR])
    ben.reben_anpflanzen(TRAUBEN[Rebsorte.SPAETBURGUNDER])
    spiel.spieler_liste.append(ben)

    print(f"  Spieler: {[s.name for s in spiel.spieler_liste]}")

    # ── Schritt 3: Willkommen ─────────────────────────────
    print("\n  Schritt 3: Spielinfo")
    jahreszeit = jahreszeit_berechnen(spiel.aktuelle_runde)
    print(f"  Startet mit : {jahreszeit.value}")
    print(f"  Runden      : {spiel.runden_gesamt}")
    print(f"  Spieler     : {len(spiel.spieler_liste)}")

    # ── Schritt 4: Qualitätstabelle ───────────────────────
    print("\n  Schritt 4: Qualitätstabelle prüfen")
    from market import QUALITAETS_TABELLE

    print(f"  Einträge: {len(QUALITAETS_TABELLE)}")
    for stufe, (min_o, p_min, p_max) in sorted(
        QUALITAETS_TABELLE.items(),
        key=lambda x: x[1][0],
    ):
        print(f"    {stufe:<24} ab {min_o:>3}°" f"  {p_min:.0f}–{p_max:.0f} EUR")

    # ── Schritt 5: Preisberechnung ────────────────────────
    print("\n  Schritt 5: Preisberechnung testen")
    faelle = [
        (72, False, 0, "Mosel", "weiss", "Normal"),
        (85, False, 12, "Rheingau", "weiss", "Spätlese"),
        (85, False, 24, "Ahr", "rot", "Rotwein"),
        (118, True, 12, "Mosel", "weiss", "Eiswein"),
    ]
    for o, eis, m, r, f, name in faelle:
        ergebnis = preis_berechnen(o, eis, m, r, f)
        print(f"  {name:<12}: {ergebnis.endpreis:>8.2f} EUR" f" ({ergebnis.stufe})")

    # ── Schritt 6: Speichern & Laden ──────────────────────
    print("\n  Schritt 6: Speichern & Laden")
    spiel.speichern()
    datei = os.path.join(SPEICHER_ORDNER, "Main-Test-S3.json")
    spiel2 = Spiel.laden(datei)
    gleich = spiel.spiel_name == spiel2.spiel_name and len(spiel.spieler_liste) == len(
        spiel2.spieler_liste
    )
    print(f"  Identisch: {'✓ Ja' if gleich else '✗ Nein'}")

    # ── Zusammenfassung ───────────────────────────────────
    print("\n" + "=" * 54)
    print("  Testergebnisse:")
    print("  " + "─" * 42)

    rotwein = preis_berechnen(85, False, 24, "Ahr", "rot")
    weisswein = preis_berechnen(85, False, 24, "Ahr", "weiss")
    eiswein = preis_berechnen(118, True, 12, "Mosel", "weiss")
    normal = preis_berechnen(72, False, 0, "Mosel", "weiss")

    tests = [
        ("Logo vorhanden", len(LOGO) > 0),
        ("2 Spieler angelegt", len(spiel.spieler_liste) == 2),
        ("9 Qualitätsstufen", len(QUALITAETS_TABELLE) == 9),
        ("Rotwein teurer als Weißwein", rotwein.endpreis > weisswein.endpreis),
        ("Eiswein teurer als normal", eiswein.endpreis > normal.endpreis),
        ("Speichern & Laden korrekt", gleich),
    ]
    alle_ok = True
    for test_name, ergebnis in tests:
        symbol = "✓" if ergebnis else "✗"
        print(f"  [{symbol}] {test_name}")
        if not ergebnis:
            alle_ok = False

    print("  " + "─" * 42)
    print(f"  Gesamt: " f"{'✓ Alle Tests bestanden!' if alle_ok else '✗ Fehler!'}")
    print("=" * 54)


# ─────────────────────────────────────────────────────────────────────────────
# Programmstart
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        self_test()
    else:
        main()
