"""
market.py – Markt & Preisberechnung (Sprint 3)
==============================================
Berechnet Qualitätsstufe und Verkaufspreis von Weinflaschen.

Zentrale Designprinzipien:
- Lager- und Regions-Boni sind PROZENTUAL (nicht fix)
- Hochwertige Weine profitieren stärker von Lagerung
- Rotwein profitiert stärker von langer Lagerung als Weißwein
- Maximale Lagerdauer hängt von der Qualitätsstufe ab
"""

from __future__ import annotations
from dataclasses import dataclass


# ─────────────────────────────────────────────────────────────────────────────
# Qualitätsstufen
# ─────────────────────────────────────────────────────────────────────────────
# Format:
# Qualitätsname → (min_oechsle, basispreis_min, basispreis_max)

QUALITAETS_TABELLE = {
    "Tafelwein": (0, 3.0, 5.0),
    "Landwein": (57, 5.0, 8.0),
    "Qualitaetswein (QbA)": (63, 8.0, 15.0),
    "Kabinett": (67, 12.0, 18.0),
    "Spaetlese": (76, 18.0, 30.0),
    "Auslese": (83, 30.0, 60.0),
    "Beerenauslese": (110, 80.0, 150.0),
    "Eiswein": (110, 100.0, 200.0),
    "Trockenbeerenauslese": (150, 200.0, 500.0),
}


# ─────────────────────────────────────────────────────────────────────────────
# Lagerung – Prozentuale Boni
# ─────────────────────────────────────────────────────────────────────────────

# Prozentualer Lagerbonus pro Monat (vom Basispreis)
LAGER_FAKTOR_PRO_MONAT = {
    "Tafelwein": 0.010,  # 1.0 %
    "Landwein": 0.015,  # 1.5 %
    "Qualitaetswein (QbA)": 0.020,  # 2.0 %
    "Kabinett": 0.025,  # 2.5 %
    "Spaetlese": 0.030,  # 3.0 %
    "Auslese": 0.035,  # 3.5 %
    "Beerenauslese": 0.040,  # 4.0 %
    "Eiswein": 0.040,  # 4.0 %
    "Trockenbeerenauslese": 0.050,  # 5.0 %
}

# Maximale sinnvolle Lagerdauer (Monate)
MAX_LAGER_MONATE = {
    "Tafelwein": 6,
    "Landwein": 12,
    "Qualitaetswein (QbA)": 18,
    "Kabinett": 24,
    "Spaetlese": 36,
    "Auslese": 48,
    "Beerenauslese": 72,
    "Eiswein": 84,
    "Trockenbeerenauslese": 120,  # 10 Jahre
}

# Rotwein profitiert stärker von Lagerung
FARBE_LAGER_MULTIPLIKATOR = {
    "weiss": 1.0,
    "rot": 1.4,
}


# ─────────────────────────────────────────────────────────────────────────────
# Region – Prozentualer Bonus
# ─────────────────────────────────────────────────────────────────────────────

REGION_PREISFAKTOR = {
    "Mosel": 0.08,
    "Rheingau": 0.10,
    "Pfalz": 0.05,
    "Baden": 0.06,
    "Franken": 0.06,
    "Wuerttemberg": 0.04,
    "Rheinhessen": 0.04,
    "Nahe": 0.05,
    "Mittelrhein": 0.06,
    "Ahr": 0.08,
    "Sachsen": 0.05,
    "Saale-Unstrut": 0.04,
    "Hessische Bergstrasse": 0.05,
}


# ─────────────────────────────────────────────────────────────────────────────
# Dataclass: Ergebnis
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class Qualitaetsergebnis:
    stufe: str
    oechsle: int
    basispreis: float
    lager_bonus: float
    region_bonus: float
    endpreis: float
    ist_eiswein: bool

    def __str__(self) -> str:
        eiswein = "  ❄ EISWEIN\n" if self.ist_eiswein else ""
        return (
            f"\n  +── Qualitätsauswertung ───────────────────+\n"
            f"{eiswein}"
            f"  Qualitätsstufe : {self.stufe}\n"
            f"  Öchsle         : {self.oechsle:>5}°\n"
            f"  Basispreis     : {self.basispreis:>8.2f} EUR\n"
            f"  Lager-Bonus    : {self.lager_bonus:>8.2f} EUR\n"
            f"  Regions-Bonus  : {self.region_bonus:>8.2f} EUR\n"
            f"  ──────────────────────────────────────────\n"
            f"  Preis/Flasche  : {self.endpreis:>8.2f} EUR\n"
            f"  +─────────────────────────────────────────+"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Kernfunktionen
# ─────────────────────────────────────────────────────────────────────────────


def qualitaet_berechnen(oechsle: int, ist_eiswein: bool = False) -> str:
    if ist_eiswein and oechsle >= 110:
        return "Eiswein"

    for stufe, (min_o, _, _) in sorted(
        QUALITAETS_TABELLE.items(),
        key=lambda x: x[1][0],
        reverse=True,
    ):
        if oechsle >= min_o and stufe != "Eiswein":
            return stufe

    return "Tafelwein"


def preis_berechnen(
    oechsle: int,
    ist_eiswein: bool,
    lager_monate: int,
    region: str,
    farbe: str,
) -> Qualitaetsergebnis:

    stufe = qualitaet_berechnen(oechsle, ist_eiswein)
    min_o, p_min, p_max = QUALITAETS_TABELLE[stufe]

    # Basispreis proportional zur Öchsle-Spanne
    if stufe == "Trockenbeerenauslese":
        faktor = min(1.0, (oechsle - min_o) / 50)
    else:
        faktor = min(1.0, (oechsle - min_o) / max(1, (p_max - p_min)))

    basispreis = p_min + faktor * (p_max - p_min)

    # Lagerbonus
    max_monate = MAX_LAGER_MONATE[stufe]
    effektive_m = min(lager_monate, max_monate)
    lager_faktor = LAGER_FAKTOR_PRO_MONAT[stufe]
    farbe_mul = FARBE_LAGER_MULTIPLIKATOR.get(farbe, 1.0)

    lager_bonus = basispreis * lager_faktor * effektive_m * farbe_mul

    # Regionsbonus
    region_bonus = basispreis * REGION_PREISFAKTOR.get(region, 0.04)

    endpreis = round(basispreis + lager_bonus + region_bonus, 2)

    return Qualitaetsergebnis(
        stufe=stufe,
        oechsle=oechsle,
        basispreis=round(basispreis, 2),
        lager_bonus=round(lager_bonus, 2),
        region_bonus=round(region_bonus, 2),
        endpreis=endpreis,
        ist_eiswein=ist_eiswein,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Self-Test
# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    print("=" * 60)
    print("  MARKET – Self-Test (prozentuale Boni)")
    print("=" * 60)

    tests = [
        ("Tafelwein", 60, False, 6, "Mosel", "weiss"),
        ("Spätlese", 85, False, 12, "Rheingau", "weiss"),
        ("Spätlese", 85, False, 24, "Ahr", "rot"),
        ("Eiswein", 118, True, 24, "Mosel", "weiss"),
        ("Bordeaux", 90, False, 18, "Bordeaux", "rot"),  # Unbekannte Region
        ("TBA", 160, False, 60, "Rheingau", "weiss"),
    ]

    for name, o, eis, m, r, f in tests:
        print(f"\nTest: {name}, {o}°, {m} Monate, {r}, {f}")
        ergebnis = preis_berechnen(o, eis, m, r, f)
        print(ergebnis)

    print("\n✅ Self-Test abgeschlossen")


if __name__ == "__main__":
    main()
