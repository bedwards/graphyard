"""
Tolerance by the Numbers - Chart Data

All data sourced from web research with citations.
These are hardcoded from verified sources rather than database queries.
"""

import pandas as pd


def load_maga_vs_nazi_voters():
    """Peak vote counts: MAGA (2024) vs NSDAP (March 1933).

    Sources:
    - AP/Cook Political Report: 2024 National Popular Vote (77.3M for Trump)
    - German federal election records, March 1933 (17.28M for NSDAP)
    """
    return pd.DataFrame([
        {"movement": "MAGA (Trump 2024)", "voters": 77_303_573},
        {"movement": "NSDAP (March 1933)", "voters": 17_277_180},
    ])


def load_nazi_voters_vs_convicted():
    """NSDAP voters vs those convicted of war crimes post-WWII.

    Sources:
    - German federal election records, March 1933
    - USHMM: 161 convicted at Nuremberg (IMT + subsequent trials)
    - The Holocaust Explained: ~100,000 convicted in European courts
    - Times of Israel / Mary Fulbrook: 6,656 in West Germany, 12,890 in East Germany
    """
    return pd.DataFrame([
        {"category": "NSDAP Voters\n(1933)", "count": 17_277_180},
        {"category": "Convicted\n(All Courts)", "count": 100_000},
    ])


def load_genocide_comparison():
    """Deadliest genocides/democides by midpoint death toll estimate.

    Sources:
    - Rummel, R.J.: 20th Century Democide
    - USHMM Holocaust Encyclopedia
    - Frank Dikotter: Mao's Great Famine
    - UCLA Cambodian Genocide Program
    - UN Outreach Programme on Rwanda
    """
    return pd.DataFrame([
        {"event": "Imagined Genocide\nof 88M MAGA Voters", "deaths": 88_000_000, "type": "imagined"},
        {"event": "China under Mao\n(1949-1976)", "deaths": 60_000_000, "type": "historical"},
        {"event": "Nazi Germany\n(1933-1945)", "deaths": 16_000_000, "type": "historical"},
        {"event": "Soviet Union\nunder Stalin", "deaths": 13_000_000, "type": "historical"},
        {"event": "Cambodia\nKhmer Rouge", "deaths": 2_000_000, "type": "historical"},
        {"event": "Rwanda\n(1994)", "deaths": 800_000, "type": "historical"},
    ])


def load_detention_comparison():
    """MAGA voter base vs targeted population vs actual detentions.

    Sources:
    - AP: 77.3M Trump voters (2024)
    - Census Bureau: 68M Hispanic + 44M Black Americans
    - Pew Research: 14M undocumented immigrants (2023)
    - CBS News / TRAC: ~73,000 in ICE detention (Jan 2026)
    - TRAC: ~335,000 deportations in 2025
    """
    return pd.DataFrame([
        {"category": "Black + Hispanic\nAmericans", "count": 112_000_000},
        {"category": "Trump Voters\n(2024)", "count": 77_303_573},
        {"category": "Undocumented\nImmigrants", "count": 14_000_000},
        {"category": "Deportations\n(2025)", "count": 335_000},
        {"category": "ICE Detention\n(Jan 2026)", "count": 73_000},
    ])


def load_freedom_house_worst():
    """Worst-scoring countries on Freedom House Freedom in the World 2025.

    Source: Freedom House, Freedom in the World 2025 report.
    Score is 0-100, higher = more free.
    """
    return pd.DataFrame([
        {"country": "United States (2025)", "score": 84, "category": "current_us"},
        {"country": "Hungary", "score": 66, "category": "backsliding"},
        {"country": "Turkey", "score": 32, "category": "authoritarian"},
        {"country": "Russia", "score": 13, "category": "authoritarian"},
        {"country": "China", "score": 9, "category": "authoritarian"},
        {"country": "Afghanistan", "score": 6, "category": "authoritarian"},
        {"country": "Eritrea", "score": 3, "category": "authoritarian"},
        {"country": "North Korea", "score": 3, "category": "authoritarian"},
        {"country": "South Sudan", "score": 1, "category": "authoritarian"},
        {"country": "Turkmenistan", "score": 1, "category": "authoritarian"},
    ])


def load_us_freedom_decline():
    """US Freedom House score decline over time.

    Source: Freedom House, Freedom in the World annual reports.
    """
    return pd.DataFrame([
        {"year": 2006, "score": 93},
        {"year": 2008, "score": 93},
        {"year": 2010, "score": 94},
        {"year": 2012, "score": 93},
        {"year": 2014, "score": 92},
        {"year": 2016, "score": 89},
        {"year": 2017, "score": 86},
        {"year": 2018, "score": 86},
        {"year": 2019, "score": 86},
        {"year": 2020, "score": 83},
        {"year": 2021, "score": 83},
        {"year": 2022, "score": 83},
        {"year": 2023, "score": 83},
        {"year": 2024, "score": 84},
        {"year": 2025, "score": 84},
    ])


def load_accountability_rates():
    """Percentage of perpetrators who faced legal consequences in historical transitions.

    Sources:
    - USHMM: Nuremberg and denazification statistics
    - South Africa TRC records
    - Argentina transitional justice data
    - Gacaca court records (Rwanda)
    - ICTJ: Criminal Justice statistics
    """
    return pd.DataFrame([
        {"country": "Rwanda\n(Gacaca Courts)", "rate": 86.0, "tried": 1_958_634},
        {"country": "Argentina\n(1983-2024)", "rate": 4.0, "tried": 1200},
        {"country": "Germany\n(Post-WWII)", "rate": 0.6, "tried": 100_000},
        {"country": "South Africa\n(TRC)", "rate": 0.0, "tried": 0},
        {"country": "Spain\n(Post-Franco)", "rate": 0.0, "tried": 0},
    ])


def load_democratic_recovery():
    """Countries that successfully transitioned from authoritarianism.
    V-Dem Liberal Democracy Index scores before and after transition.

    Sources:
    - V-Dem Democracy Report 2025
    - Freedom House annual reports
    """
    return pd.DataFrame([
        {"country": "Portugal", "period": "Before (1973)", "score": 0.05},
        {"country": "Portugal", "period": "After (2024)", "score": 0.90},
        {"country": "Spain", "period": "Before (1975)", "score": 0.08},
        {"country": "Spain", "period": "After (2024)", "score": 0.85},
        {"country": "South Korea", "period": "Before (1986)", "score": 0.15},
        {"country": "South Korea", "period": "After (2024)", "score": 0.72},
        {"country": "South Africa", "period": "Before (1993)", "score": 0.20},
        {"country": "South Africa", "period": "After (2024)", "score": 0.62},
        {"country": "Argentina", "period": "Before (1982)", "score": 0.10},
        {"country": "Argentina", "period": "After (2024)", "score": 0.68},
    ])


def load_tolerance_world_values():
    """World Values Survey: % who would NOT want a neighbor of a different race.

    Source: World Values Survey Wave 7 (2017-2022), as reported by
    Washington Post and King's College London analysis.
    """
    return pd.DataFrame([
        {"country": "Sweden", "intolerance_pct": 1.0},
        {"country": "Brazil", "intolerance_pct": 1.0},
        {"country": "United Kingdom", "intolerance_pct": 2.0},
        {"country": "United States", "intolerance_pct": 5.0},
        {"country": "France", "intolerance_pct": 10.0},
        {"country": "Germany", "intolerance_pct": 12.0},
        {"country": "Italy", "intolerance_pct": 18.0},
        {"country": "India", "intolerance_pct": 43.5},
        {"country": "Jordan", "intolerance_pct": 51.4},
        {"country": "Bangladesh", "intolerance_pct": 71.7},
    ])


def load_perpetrator_gap():
    """The impunity gap: estimated perpetrators vs those convicted.

    Sources:
    - Mary Fulbrook research on Nazi perpetrators
    - USHMM on Holocaust perpetrators
    - The Holocaust Explained: conviction statistics
    """
    return pd.DataFrame([
        {"category": "Estimated Active\nPerpetrators", "count": 500_000},
        {"category": "Investigated\n(All Courts)", "count": 140_000},
        {"category": "Convicted\n(All Courts)", "count": 100_000},
        {"category": "Serious Sentences\n(Prison > 5 yrs)", "count": 6_656},
        {"category": "Executed", "count": 200},
    ])
