"""
main.py – Einstiegspunkt des Winzer-Spiels
===========================================
Zeigt das Hauptmenü, startet das Spiel und
verwaltet Speichern & Laden.

Änderungen gegenüber Sprint 1:
  - Echte Spielschleife über game.spielen()
  - Spielstand speichern & laden (Vorbereitung)
  - Spielende mit Sieger-Anzeige

Ausführen mit:  python main.py

Sprint 2 – Weinberg & Jahreszeiten
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
  |    (c) Hour of Code – Lernprojekt  [Sprint 2]       |
  +=====================================================+
"""


# ─────────────────────────────────────────────────────────────────────────────
# Menü-Funktionen
# ─────────────────────────────────────────────────────────────────────────────
def hauptmenue_anzeigen() -> None:
    """Zeigt das Hauptmenü auf der Konsole an."""
    print("\n  +------------------------------------------+")
    print("  |              HAUPTMENÜ                   |")
    print("  +------------------------------------------+")
    print("  |  [1]  Neues Spiel starten                |")
    print("  |  [2]  Spiel laden                        |")
    print("  |  [3]  Beenden                            |")
    print("  +------------------------------------------+")


# ─────────────────────────────────────────────────────────────────────────────
# Spielstand laden
# ─────────────────────────────────────────────────────────────────────────────
def spielstand_auswaehlen() -> str | None:
    """
    Zeigt alle vorhandenen Spielstände an und
    lässt den Spieler einen auswählen.

    Returns:
        Dateipfad des gewählten Spielstands,
        oder None wenn kein Spielstand vorhanden.
    """
    # Speicherordner prüfen
    if not os.path.exists(SPEICHER_ORDNER):
        print("\n  Keine Spielstände vorhanden.")
        return None

    # Alle JSON-Dateien im Speicherordner suchen
    dateien = [f for f in os.listdir(SPEICHER_ORDNER) if f.endswith(".json")]

    if not dateien:
        print("\n  Keine Spielstände vorhanden.")
        return None

    # Spielstände anzeigen
    print("\n  Vorhandene Spielstände:")
    print("  " + "─" * 40)
    for i, datei in enumerate(dateien, start=1):
        # Dateigröße und Name anzeigen
        pfad = os.path.join(SPEICHER_ORDNER, datei)
        groesse = os.path.getsize(pfad) / 1024
        # Dateiname ohne .json anzeigen
        name = datei.replace(".json", "").replace("_", " ")
        print(f"  [{i:2d}] {name:<30} ({groesse:.1f} KB)")
    print("  " + "─" * 40)
    print("  [ 0] Zurück zum Hauptmenü")

    # Auswahl
    while True:
        try:
            wahl = int(input("\n  Deine Wahl: "))
            if wahl == 0:
                return None
            if 1 <= wahl <= len(dateien):
                return os.path.join(SPEICHER_ORDNER, dateien[wahl - 1])
            print(f"  Bitte zwischen 0 und {len(dateien)} wählen.")
        except ValueError:
            print("  Ungültige Eingabe – bitte eine Zahl eingeben.")


# ─────────────────────────────────────────────────────────────────────────────
# Willkommens-Anzeige
# ─────────────────────────────────────────────────────────────────────────────
def willkommen_anzeigen(spiel: Spiel) -> None:
    """Zeigt die Begrüßungsseite nach dem Setup an."""
    from weather import jahreszeit_berechnen

    print("\n" + "=" * 52)
    print(f"  Willkommen zu '{spiel.spiel_name}'!")
    print("=" * 52)
    print(f"  {len(spiel.spieler_liste)} Spieler nehmen teil:\n")

    for i, spieler in enumerate(spiel.spieler_liste, start=1):
        # Beste Sorte für die Region
        top_sorte = max(
            spieler.region.empfohlene_sorten,
            key=spieler.region.empfohlene_sorten.get,  # type: ignore
        )
        # Gewählte Rebsorte
        traube_str = (
            spieler.weinberg.traube.sorte.value
            if spieler.weinberg.traube
            else "Noch keine"
        )

        print(f"  {'─' * 46}")
        print(f"  Spieler {i}    : {spieler.name}")
        print(f"  Region       : {spieler.region.name.value}")
        print(f"  Rebsorte     : {traube_str}")
        print(f"  Startkapital : {spieler.geld:,.2f} EUR")
        print(f"  Beste Sorte  : {top_sorte}")
        if spieler.region.eiswein_moeglich:
            print(f"  ❄ Tipp       : Eiswein in deiner " f"Region möglich!")
        print()

    # Spielinfo
    jahreszeit = jahreszeit_berechnen(spiel.aktuelle_runde)
    print(f"  {'─' * 46}")
    print(
        f"  Runden gesamt : {spiel.runden_gesamt} "
        f"({spiel.runden_gesamt // 4} Jahre)"
    )
    print(f"  Startet mit   : {jahreszeit.value}")
    print(f"  {'─' * 46}")
    input("\n  Drücke Enter um zu starten ...")


# ─────────────────────────────────────────────────────────────────────────────
# Speichern-Abfrage
# ─────────────────────────────────────────────────────────────────────────────
def speichern_abfragen(spiel: Spiel) -> None:
    """
    Fragt nach dem Spiel ob gespeichert werden soll.
    Wird nach jeder Runde aufgerufen.
    """
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
        else:
            print("  Bitte [j] oder [n] eingeben.")


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
            wahl = input("\n  Deine Wahl (1/2/3): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n  Auf Wiedersehen! Prost! 🍷")
            sys.exit(0)

        # ── [1] Neues Spiel ───────────────────────────────
        if wahl == "1":
            spiel = Spiel()
            spiel.setup_spiel()
            willkommen_anzeigen(spiel)

            # Spielschleife starten
            spiel.spielen()

            # Nach Spielende: speichern?
            speichern_abfragen(spiel)

            # Zurück zum Hauptmenü oder beenden
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
                # Kein Spielstand gewählt → zurück zum Menü
                continue

            try:
                spiel = Spiel.laden(dateiname)
                print(f"\n  Spiel '{spiel.spiel_name}' geladen!")
                print(
                    f"  Weiter bei Runde {spiel.aktuelle_runde}"
                    f" / {spiel.runden_gesamt}"
                )
                spiel.rangliste_anzeigen()
                input("\n  Drücke Enter um weiterzuspielen ...")

                # Spielschleife fortsetzen
                spiel.spielen()

                # Nach Spielende: speichern?
                speichern_abfragen(spiel)

            except FileNotFoundError:
                print(f"  ⚠ Datei nicht gefunden: {dateiname}")
            except Exception as fehler:
                print(f"  ⚠ Fehler beim Laden: {fehler}")

        # ── [3] Beenden ───────────────────────────────────
        elif wahl == "3":
            print("\n  Auf Wiedersehen! Viel Erfolg beim Weinbau! 🍷")
            sys.exit(0)

        else:
            print("  Ungültige Eingabe – bitte 1, 2 oder 3 eingeben.")


# ─────────────────────────────────────────────────────────────────────────────
# Self-Test
# ─────────────────────────────────────────────────────────────────────────────
def self_test() -> None:
    """
    Testet alle Funktionen von main.py ohne
    interaktive Eingaben.

    Prüft:
      1. Logo wird angezeigt
      2. Spielstand-Ordner wird erkannt
      3. Spiel kann angelegt werden
      4. Willkommens-Anzeige funktioniert
      5. Spielstand wird gespeichert & gefunden
    """
    from region import REGIONEN, RegionName
    from grape import TRAUBEN, Rebsorte

    clear()
    print("=" * 52)
    print("  MAIN – Self-Test")
    print("=" * 52)

    # ── Schritt 1: Logo anzeigen ──────────────────────────
    print("\n  Schritt 1: Logo")
    print(LOGO)

    # ── Schritt 2: Spiel automatisch anlegen ─────────────
    print("\n  Schritt 2: Testspiel automatisch anlegen")
    spiel = Spiel(spiel_name="Main-Test")

    # Spieler 1
    anna = __import__("player").Spieler("Anna", REGIONEN[RegionName.MOSEL])
    anna.reben_anpflanzen(TRAUBEN[Rebsorte.RIESLING])
    spiel.spieler_liste.append(anna)

    # Spieler 2
    ben = __import__("player").Spieler("Ben", REGIONEN[RegionName.PFALZ])
    ben.reben_anpflanzen(TRAUBEN[Rebsorte.DORNFELDER])
    spiel.spieler_liste.append(ben)

    print(f"  Spieler: {[s.name for s in spiel.spieler_liste]}")

    # ── Schritt 3: Willkommens-Anzeige ────────────────────
    print("\n  Schritt 3: Willkommens-Anzeige")
    from weather import jahreszeit_berechnen

    jahreszeit = jahreszeit_berechnen(spiel.aktuelle_runde)
    print(f"  Startet mit: {jahreszeit.value}")
    print(f"  Spieler    : {len(spiel.spieler_liste)}")
    print(f"  Runden     : {spiel.runden_gesamt}")

    # ── Schritt 4: Spielstand speichern ───────────────────
    print("\n  Schritt 4: Spielstand speichern")
    spiel.speichern()

    # Gespeicherte Datei prüfen
    erwartete_datei = os.path.join(SPEICHER_ORDNER, "Main-Test.json")
    datei_vorhanden = os.path.exists(erwartete_datei)
    print(f"  Datei vorhanden: " f"{'✓ Ja' if datei_vorhanden else '✗ Nein'}")

    # ── Schritt 5: Spielstand laden ───────────────────────
    print("\n  Schritt 5: Spielstand laden")
    spiel2 = Spiel.laden(erwartete_datei)
    gleich = (
        spiel.spiel_name == spiel2.spiel_name
        and spiel.aktuelle_runde == spiel2.aktuelle_runde
        and len(spiel.spieler_liste) == len(spiel2.spieler_liste)
    )
    print(
        f"  Geladen  : '{spiel2.spiel_name}', "
        f"Runde {spiel2.aktuelle_runde}, "
        f"{len(spiel2.spieler_liste)} Spieler"
    )
    print(f"  Identisch: {'✓ Ja' if gleich else '✗ Nein'}")

    # ── Zusammenfassung ───────────────────────────────────
    print("\n" + "=" * 52)
    print("  Testergebnisse:")
    print("  " + "─" * 40)
    tests = [
        ("Logo vorhanden", len(LOGO) > 0),
        ("Spiel angelegt", spiel.spiel_name == "Main-Test"),
        ("2 Spieler vorhanden", len(spiel.spieler_liste) == 2),
        ("Jahreszeit berechnet", jahreszeit is not None),
        ("Datei gespeichert", datei_vorhanden),
        ("Laden erfolgreich", gleich),
    ]
    alle_ok = True
    for test_name, ergebnis in tests:
        symbol = "✓" if ergebnis else "✗"
        print(f"  [{symbol}] {test_name}")
        if not ergebnis:
            alle_ok = False

    print("  " + "─" * 40)
    print(f"  Gesamt: " f"{'✓ Alle Tests bestanden!' if alle_ok else '✗ Fehler!'}")
    print("=" * 52)


# ─────────────────────────────────────────────────────────────────────────────
# Programmstart
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Self-Test mit --test Parameter starten:
    #   python main.py --test
    # Normales Spiel:
    #   python main.py
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        self_test()
    else:
        main()
