"""
game.py – Spielverwaltungs-Modul
==================================
Verwaltet den gesamten Spielablauf, alle Spieler
und die Rundenlogik.

Sprint 1 – Grundlagen
"""

from __future__ import annotations
import json
import os
from typing import List
from player import Spieler
from region import region_auswaehlen

# Ordner für gespeicherte Spielstände
SPEICHER_ORDNER = "speicherstaende"


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
    """

    def __init__(self, spiel_name: str = "") -> None:
        self.spiel_name: str = spiel_name
        self.spieler_liste: List[Spieler] = []
        self.aktuelle_runde: int = 1
        self.aktueller_spieler_index: int = 0

    # ── Spieleinrichtung ─────────────────────────────────────────────────────

    def setup_spiel(self) -> None:
        """
        Interaktive Spieleinrichtung.
        Fragt nach: Spielname, Spieleranzahl,
        Spielernamen und Regionen.
        """
        print("\n" + "=" * 50)
        print("  NEUES SPIEL EINRICHTEN")
        print("=" * 50)

        # Spielname abfragen
        eingabe = input("\n  Name für dieses Spiel: ").strip()
        self.spiel_name = eingabe if eingabe else "Winzer-Spiel"

        # Spieleranzahl abfragen (2 bis 4)
        while True:
            try:
                anzahl = int(input("  Anzahl der Spieler (2–4): "))
                if 2 <= anzahl <= 4:
                    break
                print("  Bitte eine Zahl zwischen 2 und 4 eingeben.")
            except ValueError:
                print("  Ungültige Eingabe – bitte eine Zahl eingeben.")

        # Jeden Spieler einzeln einrichten
        for i in range(1, anzahl + 1):
            print(f"\n  {'─' * 40}")
            print(f"  Spieler {i} einrichten")
            print(f"  {'─' * 40}")

            # Name abfragen
            name_eingabe = input(f"  Name von Spieler {i}: ").strip()
            name = name_eingabe if name_eingabe else f"Spieler {i}"

            # Region auswählen
            print(f"\n  {name}, wähle dein Weinanbaugebiet:")
            region = region_auswaehlen()

            # Spieler erstellen und hinzufügen
            spieler = Spieler(name=name, region=region)
            self.spieler_liste.append(spieler)
            print(f"\n  Willkommen, {name}!")
            print(spieler)

    # ── Spielsteuerung ───────────────────────────────────────────────────────

    def get_aktueller_spieler(self) -> Spieler:
        """Gibt den aktuell aktiven Spieler zurück."""
        return self.spieler_liste[self.aktueller_spieler_index]

    def naechster_spieler(self) -> None:
        """
        Wechselt zum nächsten Spieler.
        Nach einem vollständigen Durchlauf wird
        die Runde um 1 erhöht.
        """
        self.aktueller_spieler_index += 1

        # Alle Spieler waren dran → neue Runde
        if self.aktueller_spieler_index >= len(self.spieler_liste):
            self.aktueller_spieler_index = 0
            self.aktuelle_runde += 1
            print(f"\n  *** Runde {self.aktuelle_runde} beginnt! ***\n")

    # ── Rangliste ────────────────────────────────────────────────────────────

    def get_rangliste(self) -> List[Spieler]:
        """
        Gibt alle Spieler nach Kapital
        absteigend sortiert zurück.
        """
        return sorted(self.spieler_liste, key=lambda s: s.geld, reverse=True)

    def rangliste_anzeigen(self) -> None:
        """Gibt die aktuelle Rangliste auf der Konsole aus."""
        print("\n  === Aktuelle Rangliste ===")
        print(f"  {'Platz':<6} {'Name':<20} {'Kapital':>15}")
        print("  " + "─" * 44)
        for platz, spieler in enumerate(self.get_rangliste(), start=1):
            print(f"  {platz:<6} " f"{spieler.name:<20} " f"{spieler.geld:>14,.2f} EUR")

    # ── Spielinfo ────────────────────────────────────────────────────────────

    def spielinfo_anzeigen(self) -> None:
        """Zeigt allgemeine Spielinformationen an."""
        print(f"\n  Spiel   : {self.spiel_name}")
        print(f"  Runde   : {self.aktuelle_runde}")
        print(f"  Am Zug  : {self.get_aktueller_spieler().name}")
        print(f"  Spieler : {len(self.spieler_liste)}")

    # ── Serialisierung ───────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        """
        Wandelt das gesamte Spiel in ein Dictionary um
        (für JSON-Speicherung).
        """
        return {
            "spiel_name": self.spiel_name,
            "aktuelle_runde": self.aktuelle_runde,
            "aktueller_spieler_index": self.aktueller_spieler_index,
            "spieler_liste": [s.to_dict() for s in self.spieler_liste],
        }

    @classmethod
    def from_dict(cls, daten: dict) -> "Spiel":
        """Erstellt ein Spiel aus einem Dictionary (für JSON-Laden)."""
        spiel = cls(spiel_name=daten["spiel_name"])
        spiel.aktuelle_runde = daten["aktuelle_runde"]
        spiel.aktueller_spieler_index = daten["aktueller_spieler_index"]
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
        print(f"\n  Spielstand gespeichert: {dateiname}")

    @classmethod
    def laden(cls, dateiname: str) -> "Spiel":
        """Lädt einen Spielstand aus einer JSON-Datei."""
        with open(dateiname, "r", encoding="utf-8") as f:
            daten = json.load(f)
        print(f"  Spielstand geladen: {dateiname}")
        return cls.from_dict(daten)
