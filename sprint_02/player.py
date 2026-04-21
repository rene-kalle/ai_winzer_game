"""
player.py – Spieler-Modul
==========================
Repräsentiert einen Spieler im Winzer-Spiel.

Änderungen gegenüber Sprint 1:
  - Spieler bekommt beim Start einen Weinberg
  - Neue Methode: weinberg_status() für Übersicht
  - Kosten für Aktionen werden direkt abgebucht

Sprint 2 – Weinberg & Jahreszeiten
"""

from __future__ import annotations
from typing import List
from region import Region
from vineyard import Weinberg
from grape import Traube


# ─────────────────────────────────────────────────────────────────────────────
# Klasse: Spieler
# ─────────────────────────────────────────────────────────────────────────────
class Spieler:
    """
    Repräsentiert einen einzelnen Spieler.

    Attribute:
        name               : Spielername
        geld               : Kapital in Euro (Start: 50.000 EUR)
        region             : Gewähltes Weinanbaugebiet
        weinberg           : Weinberg des Spielers
        keller             : Keller-Objekt (ab Sprint 3)
        rathaus_angemeldet : Ob der Spieler im Rathaus registriert ist
        lizenzen           : Liste erworbener Lizenzen
        runden_aktionen    : Aktionen der aktuellen Runde
    """

    def __init__(self, name: str, region: Region) -> None:
        """
        Erstellt einen neuen Spieler.
        Der Weinberg wird sofort mit der gewählten
        Region angelegt – aber noch nicht bepflanzt.
        """
        self.name: str = name
        self.geld: float = 50_000.0
        self.region: Region = region
        self.weinberg: Weinberg = Weinberg(region=region)
        self.keller = None  # ab Sprint 3
        self.rathaus_angemeldet: bool = False
        self.lizenzen: List[str] = []
        self.runden_aktionen: List[str] = []

    # ── Darstellung ──────────────────────────────────────────────────────────

    def __str__(self) -> str:
        """Kurzdarstellung für die Konsole."""
        return (
            f"  {self.name} "
            f"| Region: {self.region.name.value} "
            f"| Kapital: {self.geld:,.2f} EUR"
        )

    def get_status(self) -> str:
        """Ausführlicher Statusbericht des Spielers."""
        lizenz_str = ", ".join(self.lizenzen) if self.lizenzen else "Keine"
        rathaus_str = "Ja" if self.rathaus_angemeldet else "Nein"
        traube_str = (
            self.weinberg.traube.sorte.value
            if self.weinberg.traube
            else "Noch nicht bepflanzt"
        )
        return (
            f"\n  +------ Spieler-Status ----------------------+\n"
            f"  | Name          : {self.name}\n"
            f"  | Region        : {self.region.name.value}\n"
            f"  | Kapital       : {self.geld:>12,.2f} EUR\n"
            f"  | Rebsorte      : {traube_str}\n"
            f"  | Öchsle        : {self.weinberg.oechsle_aktuell}°\n"
            f"  | Rathaus       : {rathaus_str}\n"
            f"  | Lizenzen      : {lizenz_str}\n"
            f"  +--------------------------------------------+"
        )

    def weinberg_status(self) -> None:
        """Gibt den Weinberg-Status des Spielers aus."""
        print(f"\n  Weinberg von {self.name}:")
        print(self.weinberg)

    # ── Kapitalverwaltung ────────────────────────────────────────────────────

    def geld_hinzufuegen(self, betrag: float) -> None:
        """Addiert einen Betrag zum Kapital."""
        self.geld += betrag
        self.runden_aktionen.append(f"+{betrag:,.2f} EUR erhalten")

    def geld_abziehen(self, betrag: float) -> bool:
        """
        Zieht einen Betrag vom Kapital ab.

        Returns:
            True wenn erfolgreich,
            False wenn nicht genug Geld vorhanden.
        """
        if self.geld >= betrag:
            self.geld -= betrag
            self.runden_aktionen.append(f"-{betrag:,.2f} EUR ausgegeben")
            return True
        print(
            f"  ⚠ Nicht genug Geld!"
            f" Benötigt: {betrag:,.2f} EUR,"
            f" Vorhanden: {self.geld:,.2f} EUR"
        )
        return False

    # ── Weinberg-Aktionen ────────────────────────────────────────────────────

    def reben_anpflanzen(self, traube: Traube) -> bool:
        """
        Pflanzt eine Rebsorte in den Weinberg.
        Zieht die Kosten vom Kapital ab.

        Returns:
            True wenn erfolgreich
        """
        if not self.geld_abziehen(Weinberg.KOSTEN_ANPFLANZEN):
            return False

        erfolg = self.weinberg.anpflanzen(traube)

        # Kosten zurückbuchen wenn fehlgeschlagen
        if not erfolg:
            self.geld_hinzufuegen(Weinberg.KOSTEN_ANPFLANZEN)
            return False

        self.aktion_aufzeichnen(
            f"Reben angepflanzt: {traube.sorte.value} "
            f"(-{Weinberg.KOSTEN_ANPFLANZEN:,.0f} EUR)"
        )
        print(
            f"  Kosten: -{Weinberg.KOSTEN_ANPFLANZEN:,.0f} EUR "
            f"| Kapital: {self.geld:,.2f} EUR"
        )
        return True

    def weinberg_duengen(self) -> bool:
        """
        Düngt den Weinberg.
        Zieht die Kosten vom Kapital ab.

        Returns:
            True wenn erfolgreich
        """
        if not self.geld_abziehen(Weinberg.KOSTEN_DUENGER):
            return False

        erfolg = self.weinberg.duengen()

        if not erfolg:
            self.geld_hinzufuegen(Weinberg.KOSTEN_DUENGER)
            return False

        self.aktion_aufzeichnen(f"Gedüngt (-{Weinberg.KOSTEN_DUENGER:,.0f} EUR)")
        print(
            f"  Kosten: -{Weinberg.KOSTEN_DUENGER:,.0f} EUR "
            f"| Kapital: {self.geld:,.2f} EUR"
        )
        return True

    def schaedlinge_bekaempfen(self) -> bool:
        """
        Bekämpft Schädlinge im Weinberg.
        Zieht die Kosten vom Kapital ab.

        Returns:
            True wenn erfolgreich
        """
        if not self.geld_abziehen(Weinberg.KOSTEN_SCHAEDLINGE):
            return False

        erfolg = self.weinberg.schaedlinge_bekaempfen()

        if not erfolg:
            self.geld_hinzufuegen(Weinberg.KOSTEN_SCHAEDLINGE)
            return False

        self.aktion_aufzeichnen(
            f"Schädlinge bekämpft " f"(-{Weinberg.KOSTEN_SCHAEDLINGE:,.0f} EUR)"
        )
        print(
            f"  Kosten: -{Weinberg.KOSTEN_SCHAEDLINGE:,.0f} EUR "
            f"| Kapital: {self.geld:,.2f} EUR"
        )
        return True

    # ── Aktionen ─────────────────────────────────────────────────────────────

    def aktion_aufzeichnen(self, aktion: str) -> None:
        """Zeichnet eine Aktion für die aktuelle Runde auf."""
        self.runden_aktionen.append(aktion)

    def runde_abschliessen(self) -> None:
        """Setzt die Aktionsliste am Ende einer Runde zurück."""
        self.runden_aktionen = []

    # ── Serialisierung ───────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        """Wandelt den Spieler in ein Dictionary um."""
        return {
            "name": self.name,
            "geld": self.geld,
            "region": self.region.to_dict(),
            "weinberg": self.weinberg.to_dict(),
            "rathaus_angemeldet": self.rathaus_angemeldet,
            "lizenzen": self.lizenzen,
            "runden_aktionen": self.runden_aktionen,
        }

    @classmethod
    def from_dict(cls, daten: dict) -> "Spieler":
        """Erstellt einen Spieler aus einem Dictionary."""
        region = Region.from_dict(daten["region"])
        spieler = cls(name=daten["name"], region=region)
        spieler.geld = daten["geld"]
        spieler.rathaus_angemeldet = daten["rathaus_angemeldet"]
        spieler.lizenzen = daten["lizenzen"]
        spieler.runden_aktionen = daten["runden_aktionen"]
        spieler.weinberg = Weinberg.from_dict(daten["weinberg"])
        return spieler


# ─────────────────────────────────────────────────────────────────────────────
# Self-Test
# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    """
    Testet alle Funktionen der Spieler-Klasse:
      1. Spieler anlegen
      2. Reben anpflanzen (mit Kostenabzug)
      3. Düngen (mit Kostenabzug)
      4. Zu wenig Geld testen
      5. Schädlinge bekämpfen
      6. Aktionsliste anzeigen
      7. Runde abschließen
      8. Serialisierung testen
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
    print("  SPIELER – Self-Test")
    print("=" * 52)

    # ── Schritt 1: Spieler anlegen ────────────────────────
    print("\n  Schritt 1: Spieler anlegen")
    region = REGIONEN[RegionName.RHEINGAU]
    spieler = Spieler(name="Anna", region=region)
    print(spieler)
    print(spieler.get_status())
    # Rene
    region = REGIONEN[RegionName.SACHSEN]
    rene = Spieler(name="Rene Kallenbach", region=region)
    print(rene)
    print(rene.get_status())

    # ── Schritt 2: Reben anpflanzen ───────────────────────
    print("\n  Schritt 2: Riesling anpflanzen")
    riesling = TRAUBEN[Rebsorte.RIESLING]
    spieler.reben_anpflanzen(riesling)
    print(spieler.get_status())
    # Rene
    rene.reben_anpflanzen(TRAUBEN[Rebsorte.MUELLER_THURGAU])
    print(rene.get_status())

    # ── Schritt 3: Nochmal anpflanzen (muss scheitern) ────
    print("\n  Schritt 3: Nochmal anpflanzen (muss scheitern)")
    spieler.reben_anpflanzen(riesling)

    # ── Schritt 4: Düngen ─────────────────────────────────
    print("\n  Schritt 4: Weinberg düngen")
    spieler.weinberg_duengen()
    rene.weinberg_duengen()

    # ── Schritt 5: Zu wenig Geld simulieren ───────────────
    print("\n  Schritt 5: Geld-Prüfung")
    print(f"  Kapital vorher: {spieler.geld:,.2f} EUR")
    spieler.geld = 500.0  # Kapital künstlich reduzieren
    print(f"  Kapital auf 500 EUR reduziert")
    print("  Versuche zu düngen (sollte scheitern):")
    spieler.weinberg_duengen()
    spieler.geld = 50_000.0  # zurücksetzen
    print(f"  Kapital zurückgesetzt: {spieler.geld:,.2f} EUR")

    # ── Schritt 6: Schädlinge simulieren ──────────────────
    print("\n  Schritt 6: Schädlingsbefall & Bekämpfung")
    spieler.weinberg.schaedlingsbefall = True
    print("  Schädlingsbefall gesetzt!")
    spieler.schaedlinge_bekaempfen()

    # ── Schritt 7: Eine Runde simulieren ──────────────────
    print("\n  Schritt 7: Frühlings-Runde simulieren")
    jahreszeit = jahreszeit_berechnen(1)
    jahreszeit_anzeigen(jahreszeit, 1)
    spieler.weinberg_duengen()
    wetter = WETTER_EREIGNISSE[Wetterzustand.IDEAL]
    print(f"\n  Wetter: {wetter.zustand.value} " f"(+{wetter.oechsle_bonus}°)")
    spieler.weinberg.runde_abschliessen(jahreszeit, wetter)
    rene.weinberg.runde_abschliessen(jahreszeit, wetter)

    # ── Schritt 8: Aktionsliste anzeigen ──────────────────
    print("\n  Schritt 8: Aktionsliste dieser Runde")
    print(f"  {len(spieler.runden_aktionen)} Aktionen aufgezeichnet:")
    for i, aktion in enumerate(spieler.runden_aktionen, 1):
        print(f"    {i}. {aktion}")

    # ── Schritt 9: Runde abschließen ──────────────────────
    print("\n  Schritt 9: Runde abschließen")
    spieler.runde_abschliessen()
    print(
        f"  Aktionsliste nach Abschluss: "
        f"{len(spieler.runden_aktionen)} Einträge "
        f"({'✓ leer' if not spieler.runden_aktionen else '✗ nicht leer'})"
    )

    # ── Schritt 10: Weinberg-Status anzeigen ──────────────
    print("\n  Schritt 10: Weinberg-Status")
    spieler.weinberg_status()

    # ── Schritt 11: Serialisierung testen ─────────────────
    print("\n  Schritt 11: Speichern & Laden testen")
    daten = spieler.to_dict()
    spieler2 = Spieler.from_dict(daten)

    gleich = (
        spieler.name == spieler2.name
        and spieler.geld == spieler2.geld
        and spieler.region.name == spieler2.region.name
        and spieler.weinberg.oechsle_aktuell == spieler2.weinberg.oechsle_aktuell
        and spieler.weinberg.traube.sorte == spieler2.weinberg.traube.sorte
    )
    print(
        f"  Original : {spieler.name}, "
        f"{spieler.geld:,.2f} EUR, "
        f"{spieler.weinberg.traube.sorte.value}, "
        f"{spieler.weinberg.oechsle_aktuell}°"
    )
    print(
        f"  Geladen  : {spieler2.name}, "
        f"{spieler2.geld:,.2f} EUR, "
        f"{spieler2.weinberg.traube.sorte.value}, "
        f"{spieler2.weinberg.oechsle_aktuell}°"
    )
    print(f"  Identisch: {'✓ Ja' if gleich else '✗ Nein'}")

    # ── Zusammenfassung ───────────────────────────────────
    print("\n" + "=" * 52)
    print("  Testergebnisse:")
    print("  " + "─" * 40)
    tests = [
        ("Spieler anlegen", True),
        ("Reben anpflanzen", spieler.weinberg.traube is not None),
        ("Doppelt anpflanzen abgew.", True),
        ("Geld-Prüfung", True),
        ("Schädlinge bekämpft", not spieler.weinberg.schaedlingsbefall),
        ("Runde abgeschlossen", len(spieler.runden_aktionen) == 0),
        ("Serialisierung", gleich),
    ]
    alle_ok = True
    for test_name, ergebnis in tests:
        symbol = "✓" if ergebnis else "✗"
        print(f"  [{symbol}] {test_name}")
        if not ergebnis:
            alle_ok = False

    print("  " + "─" * 40)
    print(
        f"  Gesamt: "
        f"{'✓ Alle Tests bestanden!' if alle_ok else '✗ Fehler gefunden!'}"
    )
    print("=" * 52)


if __name__ == "__main__":
    main()
