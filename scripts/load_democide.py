#!/usr/bin/env python3
"""
Load democide/genocide data from PITF and Rummel estimates into PostgreSQL.

Sources:
1. PITF Genocide/Politicide dataset (1955-2018) - structured annual data
2. Rummel's Statistics of Democide (1900-1987) - historical estimates

Death magnitude scale (PITF):
    0.0 = <300 deaths
    0.5 = 300-1,000
    1.0 = 1,000-2,000
    1.5 = 2,000-4,000
    2.0 = 4,000-8,000
    2.5 = 8,000-16,000
    3.0 = 16,000-32,000
    3.5 = 32,000-64,000
    4.0 = 64,000-128,000
    4.5 = 128,000-256,000
    5.0 = 256,000-512,000
    5.5 = 512,000-1,024,000
    6.0 = 1,024,000-2,048,000
"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import math

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'graphyard',
    'user': 'postgres',
    'password': 'postgres'
}

# Rummel's major democide estimates (1900-1987)
# Source: Statistics of Democide, Death by Government
# Format: (regime, country_iso, start_year, end_year, low, mid, high, description)
RUMMEL_ESTIMATES = [
    # Mega-murderers (>1 million)
    ("Soviet Union (Stalin)", "RUS", 1917, 1987, 28_000_000, 61_911_000, 126_891_000,
     "Collectivization, Gulag, Great Terror, deportations, WWII prisoner deaths"),
    ("China (Mao)", "CHN", 1949, 1987, 32_000_000, 76_702_000, 106_000_000,
     "Land reform, Great Leap Forward famine, Cultural Revolution, laogai camps"),
    ("Nazi Germany", "DEU", 1933, 1945, 15_000_000, 20_946_000, 31_595_000,
     "Holocaust, T4 euthanasia, POW deaths, occupation killings"),
    ("Nationalist China (KMT)", "CHN", 1928, 1949, 6_000_000, 10_214_000, 18_522_000,
     "Warlord era, anti-communist campaigns, WWII atrocities"),
    ("Japan (Imperial)", "JPN", 1937, 1945, 3_000_000, 5_964_000, 10_595_000,
     "China occupation, comfort women, POW deaths, Southeast Asia"),
    ("Cambodia (Khmer Rouge)", "KHM", 1975, 1979, 1_000_000, 2_035_000, 3_000_000,
     "Year Zero, killing fields, forced labor, starvation"),

    # Centi-kilo murderers (100k - 1M)
    ("Turkey (Ottoman)", "TUR", 1909, 1918, 703_000, 1_883_000, 2_882_000,
     "Armenian Genocide, Greek and Assyrian massacres"),
    ("Vietnam (North)", "VNM", 1945, 1987, 215_000, 1_670_000, 3_311_000,
     "Land reform, reeducation camps, boat people deaths"),
    ("Poland (WWII era)", "POL", 1945, 1948, 50_000, 1_585_000, 1_585_000,
     "German expulsion deaths, political purges"),
    ("Pakistan", "PAK", 1958, 1987, 1_000_000, 1_503_000, 3_503_000,
     "Bangladesh genocide (1971), Baloch killings"),
    ("Yugoslavia (Tito)", "SRB", 1944, 1987, 500_000, 1_072_000, 1_587_000,
     "WWII reprisals, Bleiburg, political prisoners"),
    ("North Korea", "PRK", 1948, 1987, 710_000, 1_663_000, 3_549_000,
     "Korean War atrocities, political purges, camps"),
    ("Mexico (Revolution)", "MEX", 1900, 1920, 100_000, 1_417_000, 2_000_000,
     "Mexican Revolution, Cristero War"),
    ("Russia (Czarist)", "RUS", 1900, 1917, 500_000, 1_066_000, 1_633_000,
     "Pogroms, WWI losses, 1905 repression"),
    ("China (Warlord era)", "CHN", 1917, 1928, 500_000, 910_000, 1_820_000,
     "Warlord conflicts, banditry, famines"),

    # Lesser murderers (10k - 100k) - selected major cases
    ("Indonesia (1965-66)", "IDN", 1965, 1966, 250_000, 509_000, 1_000_000,
     "Anti-communist massacres after failed coup"),
    ("Uganda (Amin)", "UGA", 1971, 1979, 100_000, 300_000, 500_000,
     "Idi Amin regime killings"),
    ("Ethiopia (Derg)", "ETH", 1974, 1991, 30_000, 725_000, 1_500_000,
     "Red Terror, Eritrea war, famine deaths"),
    ("Rwanda (1994)", "RWA", 1994, 1994, 500_000, 800_000, 1_000_000,
     "Tutsi genocide"),
    ("Bangladesh (1971)", "BGD", 1971, 1971, 300_000, 1_500_000, 3_000_000,
     "Pakistan army killings during independence war"),
    ("Iraq (Saddam)", "IRQ", 1968, 2003, 100_000, 600_000, 1_000_000,
     "Anfal campaign, Shia uprising repression, political killings"),
    ("Afghanistan (Soviet)", "AFG", 1978, 1992, 500_000, 1_800_000, 2_000_000,
     "Soviet invasion, government repression"),
    ("Sudan (Civil wars)", "SDN", 1955, 2005, 500_000, 2_000_000, 2_500_000,
     "North-South civil wars, Darfur"),
    ("Nigeria (Biafra)", "NGA", 1967, 1970, 500_000, 1_000_000, 2_000_000,
     "Biafra war, blockade famine"),
    ("Congo (Leopold II)", "COD", 1885, 1908, 1_000_000, 8_000_000, 10_000_000,
     "Rubber terror in Congo Free State"),
    ("Herero Genocide", "NAM", 1904, 1907, 34_000, 65_000, 100_000,
     "German colonial genocide in Namibia"),
    ("Bosnia", "BIH", 1992, 1995, 50_000, 100_000, 200_000,
     "Bosnian War, Srebrenica massacre"),
    ("Guatemala", "GTM", 1960, 1996, 50_000, 200_000, 250_000,
     "Mayan genocide during civil war"),
    ("Argentina (Dirty War)", "ARG", 1976, 1983, 10_000, 30_000, 30_000,
     "Military junta disappearances"),
    ("Chile (Pinochet)", "CHL", 1973, 1990, 3_000, 3_200, 10_000,
     "Military coup and repression"),
    ("El Salvador", "SLV", 1979, 1992, 30_000, 75_000, 80_000,
     "Civil war massacres"),
]


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def magnitude_to_deaths(mag):
    """Convert PITF death magnitude to approximate death count (midpoint of range).

    PITF scale:
        0.0 = <300 deaths
        0.5 = 300-1,000
        1.0 = 1,000-2,000
        1.5 = 2,000-4,000
        2.0 = 4,000-8,000
        ...
        5.0 = 256,000-512,000

    Pattern: For mag >= 1.0, low = 1000 * 2^(2*(mag-1)), high = 2*low
    """
    if pd.isna(mag):
        return None
    if mag < 0.5:
        return 150  # midpoint of 0-300
    elif mag < 1.0:
        return 650  # midpoint of 300-1000
    else:
        # For mag >= 1.0: low = 1000 * 4^(mag-1)
        low = 1000 * (4 ** (mag - 1))
        high = 2 * low
        return int((low + high) / 2)


def create_schema(conn):
    """Create democide schema and tables."""
    cur = conn.cursor()

    cur.execute("""
        CREATE SCHEMA IF NOT EXISTS democide;

        DROP TABLE IF EXISTS democide.episodes CASCADE;
        DROP TABLE IF EXISTS democide.annual_data CASCADE;

        -- Episodes: distinct genocide/politicide/democide events
        CREATE TABLE democide.episodes (
            id SERIAL PRIMARY KEY,
            source VARCHAR(20) NOT NULL,  -- 'pitf' or 'rummel'
            country_id INTEGER REFERENCES master.countries(id),
            country_name VARCHAR(200),
            regime_name VARCHAR(300),
            start_year SMALLINT NOT NULL,
            end_year SMALLINT,
            deaths_low INTEGER,
            deaths_mid INTEGER,
            deaths_high INTEGER,
            death_magnitude DECIMAL(4,2),
            episode_type VARCHAR(50),  -- genocide, politicide, democide
            description TEXT,
            UNIQUE(source, country_name, start_year)
        );

        -- Annual data from PITF (year-by-year death magnitudes)
        CREATE TABLE democide.annual_data (
            id SERIAL PRIMARY KEY,
            episode_id INTEGER REFERENCES democide.episodes(id),
            country_id INTEGER REFERENCES master.countries(id),
            year SMALLINT NOT NULL,
            death_magnitude DECIMAL(4,2),
            deaths_estimate INTEGER,
            UNIQUE(episode_id, year)
        );

        CREATE INDEX idx_democide_episodes_country ON democide.episodes(country_id);
        CREATE INDEX idx_democide_episodes_years ON democide.episodes(start_year, end_year);
        CREATE INDEX idx_democide_annual_year ON democide.annual_data(year);
    """)
    conn.commit()
    print("Schema created: democide.episodes, democide.annual_data")


def get_country_map(conn):
    """Get mapping of ISO codes to master.countries IDs."""
    cur = conn.cursor()
    cur.execute("SELECT id, iso_alpha3 FROM master.countries")
    return {row[1]: row[0] for row in cur.fetchall()}


def load_pitf(conn, country_map):
    """Load PITF genocide/politicide data."""
    print("\nLoading PITF data...")

    df = pd.read_excel('datasets/rummel/PITF_GenoPoliticide_2018.xls')
    print(f"  Read {len(df)} annual observations")

    cur = conn.cursor()

    # First, create episodes (unique country + start year combinations)
    episodes = df.groupby(['COUNTRY', 'SCODE', 'CCODE', 'YRBEGIN', 'YREND']).agg({
        'DEATHMAG': 'max',
        'DESC': 'first'
    }).reset_index()

    episode_records = []
    for _, row in episodes.iterrows():
        scode = row['SCODE']
        country_id = country_map.get(scode)

        max_mag = row['DEATHMAG']
        deaths_mid = magnitude_to_deaths(max_mag)
        deaths_low = int(deaths_mid * 0.5) if deaths_mid else None
        deaths_high = int(deaths_mid * 2) if deaths_mid else None

        episode_records.append((
            'pitf',
            country_id,
            row['COUNTRY'],
            row['COUNTRY'],  # regime_name same as country for PITF
            int(row['YRBEGIN']),
            int(row['YREND']) if pd.notna(row['YREND']) else None,
            deaths_low,
            deaths_mid,
            deaths_high,
            max_mag,
            'politicide',  # PITF uses politicide/genocide
            str(row['DESC'])[:2000] if pd.notna(row['DESC']) else None
        ))

    insert_sql = """
        INSERT INTO democide.episodes
        (source, country_id, country_name, regime_name, start_year, end_year,
         deaths_low, deaths_mid, deaths_high, death_magnitude, episode_type, description)
        VALUES %s
        ON CONFLICT DO NOTHING
        RETURNING id, country_name, start_year
    """
    execute_values(cur, insert_sql, episode_records, page_size=100)
    conn.commit()

    # Get episode ID mapping
    cur.execute("""
        SELECT id, country_name, start_year FROM democide.episodes
        WHERE source = 'pitf'
    """)
    episode_map = {(row[1], row[2]): row[0] for row in cur.fetchall()}

    print(f"  Inserted {len(episode_map)} episodes")

    # Load annual data
    annual_records = []
    for _, row in df.iterrows():
        episode_id = episode_map.get((row['COUNTRY'], int(row['YRBEGIN'])))
        if not episode_id:
            continue

        scode = row['SCODE']
        country_id = country_map.get(scode)

        annual_records.append((
            episode_id,
            country_id,
            int(row['YEAR']),
            row['DEATHMAG'],
            magnitude_to_deaths(row['DEATHMAG'])
        ))

    insert_sql = """
        INSERT INTO democide.annual_data
        (episode_id, country_id, year, death_magnitude, deaths_estimate)
        VALUES %s
        ON CONFLICT DO NOTHING
    """
    execute_values(cur, insert_sql, annual_records, page_size=500)
    conn.commit()

    print(f"  Inserted {len(annual_records)} annual observations")
    return len(episode_records), len(annual_records)


def load_rummel(conn, country_map):
    """Load Rummel historical democide estimates."""
    print("\nLoading Rummel estimates...")

    cur = conn.cursor()

    records = []
    for (regime, iso, start, end, low, mid, high, desc) in RUMMEL_ESTIMATES:
        country_id = country_map.get(iso)

        # Calculate approximate death magnitude for comparison
        if mid and mid > 0:
            # Reverse engineer magnitude from midpoint
            mag = math.log2(mid / 300) + 0.5 if mid > 300 else 0
            mag = round(mag * 2) / 2  # Round to nearest 0.5
        else:
            mag = None

        records.append((
            'rummel',
            country_id,
            regime.split('(')[0].strip() if '(' in regime else regime,
            regime,
            start,
            end,
            low,
            mid,
            high,
            mag,
            'democide',
            desc
        ))

    insert_sql = """
        INSERT INTO democide.episodes
        (source, country_id, country_name, regime_name, start_year, end_year,
         deaths_low, deaths_mid, deaths_high, death_magnitude, episode_type, description)
        VALUES %s
        ON CONFLICT DO NOTHING
    """
    execute_values(cur, insert_sql, records, page_size=50)
    conn.commit()

    print(f"  Inserted {len(records)} Rummel episodes")
    return len(records)


def main():
    print("=" * 60)
    print("Loading Democide/Genocide Data")
    print("=" * 60)

    conn = get_connection()

    create_schema(conn)

    country_map = get_country_map(conn)
    print(f"Loaded {len(country_map)} country mappings")

    pitf_eps, pitf_annual = load_pitf(conn, country_map)
    rummel_count = load_rummel(conn, country_map)

    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    cur = conn.cursor()

    cur.execute("SELECT COUNT(*), SUM(deaths_mid) FROM democide.episodes WHERE source = 'pitf'")
    pitf = cur.fetchone()
    print(f"PITF episodes: {pitf[0]}, Total deaths (mid): {pitf[1]:,}")

    cur.execute("SELECT COUNT(*), SUM(deaths_mid) FROM democide.episodes WHERE source = 'rummel'")
    rummel = cur.fetchone()
    print(f"Rummel episodes: {rummel[0]}, Total deaths (mid): {rummel[1]:,}")

    cur.execute("SELECT COUNT(*) FROM democide.annual_data")
    annual = cur.fetchone()[0]
    print(f"Annual observations: {annual}")

    # Top democides
    print("\n" + "=" * 60)
    print("Top 15 Democides by Death Toll (Rummel estimates)")
    print("=" * 60)

    query = """
        SELECT regime_name, start_year, end_year,
               deaths_low, deaths_mid, deaths_high
        FROM democide.episodes
        WHERE source = 'rummel'
        ORDER BY deaths_mid DESC
        LIMIT 15
    """
    cur.execute(query)
    print(f"{'Regime':<35} {'Years':<12} {'Deaths (mid)':>15}")
    print("-" * 65)
    for row in cur.fetchall():
        years = f"{row[1]}-{row[2]}" if row[2] else str(row[1])
        print(f"{row[0]:<35} {years:<12} {row[4]:>15,}")

    # Cross-reference with military spending
    print("\n" + "=" * 60)
    print("Democide vs Military Spending (countries with both datasets)")
    print("=" * 60)

    query = """
        SELECT
            c.name as country,
            e.start_year,
            e.end_year,
            e.deaths_mid,
            COALESCE(
                (SELECT AVG(milex_constant_usd)
                 FROM atrocity_economics.sipri_milex s
                 WHERE s.country_id = c.id
                 AND s.year BETWEEN e.start_year AND COALESCE(e.end_year, e.start_year)),
                0
            )::bigint as avg_milex_millions
        FROM democide.episodes e
        JOIN master.countries c ON e.country_id = c.id
        WHERE e.deaths_mid > 100000
        ORDER BY e.deaths_mid DESC
        LIMIT 10
    """
    result = pd.read_sql(query, conn)
    print(result.to_string(index=False))

    conn.close()
    print("\nDone!")


if __name__ == '__main__':
    main()
