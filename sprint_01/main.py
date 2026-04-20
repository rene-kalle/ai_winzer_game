"""
main.py – Einstiegspunkt des Winzer-Spiels
===========================================
Zeigt das Hauptmenü und startet das Spiel.

Ausführen mit:  python main.py

Sprint 1 – Grundlagen
"""

import os, sys
from game import Spiel


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
  |    (c) Hour of Code – Lernprojekt                   |
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
    print("  |  [2]  Spiel laden    (kommt in Sprint 5) |")
    print("  |  [3]  Beenden                            |")
    print("  +------------------------------------------+")


def willkommen_anzeigen(spiel: Spiel) -> None:
    """Zeigt die Begrüßungsseite nach dem Setup an."""
    print("\n" + "=" * 52)
    print(f"  Willkommen zu '{spiel.spiel_name}'!")
    print("=" * 52)
    print(f"  {len(spiel.spieler_liste)} Spieler nehmen teil:\n")

    for i, spieler in enumerate(spiel.spieler_liste, start=1):
        # Beste Sorte für die Region ermitteln
        top_sorte = max(
            spieler.region.empfohlene_sorten, key=spieler.region.empfohlene_sorten.get  # type: ignore
        )
        # Eiswein-Hinweis
        eiswein_hinweis = ""
        if spieler.region.eiswein_moeglich:
            eiswein_hinweis = "  ❄  Eiswein möglich – riskant aber lukrativ!"

        print(f"  Spieler {i}  : {spieler.name}")
        print(f"  Region     : {spieler.region.name.value}")
        print(f"  Startgeld  : {spieler.geld:,.2f} EUR")
        print(f"  Beste Sorte: {top_sorte}")
        if eiswein_hinweis:
            print(f"  {eiswein_hinweis}")
        print()


def sprint1_abschluss_anzeigen(spiel: Spiel) -> None:
    """Zeigt die Sprint-1-Abschlussmeldung und die Rangliste."""
    print("\n" + "=" * 52)
    print("  Sprint 1 abgeschlossen!")
    print("  Das Grundgerüst steht.")
    print("=" * 52)
    print("\n  Was wurde in Sprint 1 gebaut:\n")
    print("  [OK]  Regionen-System    (13 Anbaugebiete)")
    print("  [OK]  Traubensorten      (14 Sorten + Eignung)")
    print("  [OK]  Spieler-Klasse     (Kapital, Status)")
    print("  [OK]  Spielverwaltung    (Runden, Wechsel)")
    print("  [OK]  Serialisierung     (Vorbereitung Sprint 5)")
    print("\n  In Sprint 2 folgt:\n")
    print("  -->   Weinberg anlegen & bepflanzen")
    print("  -->   Düngen & Schädlingsbekämpfung")
    print("  -->   Jahreszeiten & Zufalls-Wetter")
    print("  -->   Öchsle-Grad Berechnung")
    print("\n" + "=" * 52)
    spiel.rangliste_anzeigen()


def clear() -> None:
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
            print("\n\n  Auf Wiedersehen! Prost!")
            sys.exit(0)

        if wahl == "1":
            # ── Neues Spiel ──────────────────────────────
            spiel = Spiel()
            spiel.setup_spiel()
            willkommen_anzeigen(spiel)
            sprint1_abschluss_anzeigen(spiel)
            print("\n  Drücke Enter zum Beenden ...")
            try:
                input()
            except (EOFError, KeyboardInterrupt):
                pass
            break

        elif wahl == "2":
            # ── Laden (kommt in Sprint 5) ────────────────
            print("\n  Spielstand laden kommt in Sprint 5.")
            print("  Dann lernst du JSON-Dateien lesen & schreiben!")

        elif wahl == "3":
            # ── Beenden ──────────────────────────────────
            print("\n  Auf Wiedersehen! Viel Erfolg beim Weinbau!")
            sys.exit(0)

        else:
            print("  Ungültige Eingabe – bitte 1, 2 oder 3 eingeben.")


# ─────────────────────────────────────────────────────────────────────────────
# Programmstart
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
