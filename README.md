# ai_winzer_game

## Beschreibung

**ai_winzer_game** ist ein deutsches Weinbau-Spiel, inspiriert vom klassischen Winzer-Spiel. Es wurde mit Hilfe von KI entwickelt und dient als Lernprojekt für Kinder und junge Studenten, um das Programmieren zu erlernen. Das Projekt ist in Sprints organisiert, um den Entwicklungsprozess schrittweise zu vermitteln.

Im Spiel übernimmst du die Rolle eines Winzers: Pflanze Reben an, ernte Trauben, keltere Wein und baue dein Vermögen auf. Das Spiel läuft über 3 Jahre (72 Runden) und berücksichtigt Jahreszeiten, Wetterbedingungen und Weinqualität.

## Sprints

Das Projekt ist in Sprints unterteilt, die jeweils neue Features und Verbesserungen hinzufügen:

- **Sprint 01**: Grundlegende Spielmechanik
- **Sprint 02**: Erweiterte Features wie Wetter und Weinberge
- **Sprint 03**: Ernte, Kellerei und Weinqualität (aktuell)

## Installation und Ausführung

### Voraussetzungen

- Python 3.x

### Spiel starten

1. Navigiere in den gewünschten Sprint-Ordner (z.B. `sprint_03`).
2. Führe das Spiel aus:

   ```bash
   python main.py
   ```

### Optionen

- `python main.py --test`: Führt einen Selbsttest durch.

## Spielregeln

- Wähle eine Region und Traubensorte.
- Pflanze Reben im Frühling.
- Ernte im Herbst, abhängig vom Wetter.
- Keltere Wein und verkaufe ihn auf dem Markt.
- Ziel: Baue dein Vermögen auf!

## Projektstruktur

- `sprint_01/`: Erster Sprint mit grundlegenden Klassen
- `sprint_02/`: Zweiter Sprint mit erweiterten Features
- `sprint_03/`: Dritter Sprint mit vollständiger Spielmechanik
  - `game.py`: Hauptspiel-Logik
  - `player.py`: Spieler-Klasse
  - `region.py`: Regionen und Trauben
  - `vineyard.py`: Weinberg-Verwaltung
  - `weather.py`: Wetter-System
  - `winery.py`: Kellerei und Weinqualität
  - `market.py`: Markt für Weinverkauf
  - `saves/`: Gespeicherte Spielstände

## Mitwirken

Dieses Projekt ist ein Lernprojekt. Beiträge sind willkommen, insbesondere von Lernenden!

## Lizenz

(c) Hour of Code – Lernprojekt
