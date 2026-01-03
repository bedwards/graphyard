#!/usr/bin/env python3
"""
Load SIPRI and Maddison data into PostgreSQL with country linkage.
"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import re

# Database connection
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'graphyard',
    'user': 'postgres',
    'password': 'postgres'
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def get_master_countries(conn):
    """Get mapping of ISO alpha-3 codes to country IDs."""
    query = "SELECT id, iso_alpha3, name FROM master.countries"
    df = pd.read_sql(query, conn)
    return df

def normalize_country_name(name):
    """Normalize country names for matching."""
    if pd.isna(name):
        return None
    name = str(name).strip()
    # Common normalizations
    replacements = {
        'United States of America': 'USA',
        'United States': 'USA',
        'Korea, South': 'KOR',
        'Korea, North': 'PRK',
        'Korea, Republic of': 'KOR',
        "Korea, Dem. People's Rep.": 'PRK',
        'Russian Federation': 'RUS',
        'Russia': 'RUS',
        'Iran, Islamic Rep.': 'IRN',
        'Iran': 'IRN',
        'Venezuela, RB': 'VEN',
        'Venezuela (Bolivarian Republic of)': 'VEN',
        'Bolivia (Plurinational State of)': 'BOL',
        'Syrian Arab Republic': 'SYR',
        'Syria': 'SYR',
        'Egypt, Arab Rep.': 'EGY',
        'Egypt': 'EGY',
        'Congo, Dem. Rep.': 'COD',
        'Congo, DR': 'COD',
        'Congo, Rep.': 'COG',
        'Congo, Republic': 'COG',
        'Lao PDR': 'LAO',
        "Lao People's Democratic Republic": 'LAO',
        'Viet Nam': 'VNM',
        'Vietnam': 'VNM',
        'Czech Republic': 'CZE',
        'Czechia': 'CZE',
        'Slovak Republic': 'SVK',
        'Slovakia': 'SVK',
        'Türkiye': 'TUR',
        'Turkey': 'TUR',
        'Côte d\'Ivoire': 'CIV',
        'Cote d\'Ivoire': 'CIV',
        'Gambia, The': 'GMB',
        'Yemen, Rep.': 'YEM',
        'Yemen': 'YEM',
        'Myanmar (Burma)': 'MMR',
        'Myanmar': 'MMR',
        'Taiwan': 'TWN',
        'China, Taiwan Province of': 'TWN',
        'Hong Kong SAR, China': 'HKG',
        'Hong Kong': 'HKG',
        'Macao SAR, China': 'MAC',
        'Macau': 'MAC',
        'Tanzania': 'TZA',
        'Tanzania, United Republic of': 'TZA',
        'Macedonia, FYR': 'MKD',
        'North Macedonia': 'MKD',
        'Moldova': 'MDA',
        'Moldova, Republic of': 'MDA',
        'Kyrgyz Republic': 'KGZ',
        'Kyrgyzstan': 'KGZ',
        'United Kingdom': 'GBR',
        'UK': 'GBR',
    }
    return replacements.get(name, name)

def build_sipri_country_map(sipri_names, master_df):
    """Build mapping from SIPRI country names to master.countries IDs."""
    mapping = {}
    master_by_name = {row['name'].lower(): row['id'] for _, row in master_df.iterrows()}
    master_by_iso = {row['iso_alpha3']: row['id'] for _, row in master_df.iterrows()}

    for name in sipri_names:
        if pd.isna(name) or name in ['Africa', 'Americas', 'Asia & Oceania', 'Europe',
                                      'Middle East', 'North Africa', 'Sub-Saharan Africa',
                                      'Central America and the Caribbean', 'North America',
                                      'South America', 'Central Asia', 'East Asia',
                                      'Oceania', 'South Asia', 'South East Asia',
                                      'Central Europe', 'Eastern Europe', 'Western Europe']:
            continue

        # Try direct ISO match
        normalized = normalize_country_name(name)
        if normalized in master_by_iso:
            mapping[name] = master_by_iso[normalized]
            continue

        # Try name match
        name_lower = name.lower()
        if name_lower in master_by_name:
            mapping[name] = master_by_name[name_lower]
            continue

        # Try partial match
        for master_name, master_id in master_by_name.items():
            if name_lower in master_name or master_name in name_lower:
                mapping[name] = master_id
                break

    return mapping

def load_sipri(conn):
    """Load SIPRI military expenditure data."""
    print("Loading SIPRI data...")

    # Get master countries
    master_df = get_master_countries(conn)

    # Load SIPRI CSVs
    constant_usd = pd.read_csv('datasets/sipri/sipri_constant_usd.csv')
    current_usd = pd.read_csv('datasets/sipri/sipri_current_usd.csv')
    share_gdp = pd.read_csv('datasets/sipri/sipri_share_gdp.csv')
    per_capita = pd.read_csv('datasets/sipri/sipri_per_capita.csv')
    share_govt = pd.read_csv('datasets/sipri/sipri_share_govt.csv')

    # Get year columns
    year_cols_main = [c for c in constant_usd.columns if c.isdigit()]
    year_cols_percap = [c for c in per_capita.columns if c.isdigit()]
    year_cols_govt = [c for c in share_govt.columns if c.isdigit()]

    # Build country mapping
    sipri_names = constant_usd['Country'].dropna().unique()
    country_map = build_sipri_country_map(sipri_names, master_df)

    print(f"  Matched {len(country_map)} of {len(sipri_names)} SIPRI countries to master")

    # Unpivot and merge data
    records = []

    for _, row in constant_usd.iterrows():
        country_name = row['Country']
        if pd.isna(country_name) or country_name not in country_map:
            continue

        country_id = country_map[country_name]

        for year in year_cols_main:
            val_const = row.get(year)
            if pd.isna(val_const) or val_const == '...':
                continue

            # Get values from other sheets
            current_row = current_usd[current_usd['Country'] == country_name]
            gdp_row = share_gdp[share_gdp['Country'] == country_name]

            val_current = None
            val_gdp = None
            val_percap = None
            val_govt = None

            if len(current_row) > 0:
                v = current_row[year].values[0] if year in current_row.columns else None
                if v and v != '...':
                    try:
                        val_current = float(v)
                    except:
                        pass

            if len(gdp_row) > 0:
                v = gdp_row[year].values[0] if year in gdp_row.columns else None
                if v and v != '...':
                    try:
                        val_gdp = float(v)
                    except:
                        pass

            if year in year_cols_percap:
                percap_row = per_capita[per_capita['Country'] == country_name]
                if len(percap_row) > 0:
                    v = percap_row[year].values[0] if year in percap_row.columns else None
                    if v and v != '...':
                        try:
                            val_percap = float(v)
                        except:
                            pass

            if year in year_cols_govt:
                govt_row = share_govt[share_govt['Country'] == country_name]
                if len(govt_row) > 0:
                    v = govt_row[year].values[0] if year in govt_row.columns else None
                    if v and v != '...':
                        try:
                            val_govt = float(v)
                        except:
                            pass

            try:
                val_const_float = float(val_const)
            except:
                continue

            records.append((
                country_id,
                country_name,
                int(year),
                val_const_float,
                val_current,
                val_gdp,
                val_percap,
                val_govt
            ))

    print(f"  Prepared {len(records)} SIPRI records")

    # Insert into database
    cur = conn.cursor()
    cur.execute("TRUNCATE atrocity_economics.sipri_milex RESTART IDENTITY")

    insert_sql = """
        INSERT INTO atrocity_economics.sipri_milex
        (country_id, sipri_country_name, year, milex_constant_usd, milex_current_usd,
         milex_share_gdp, milex_per_capita, milex_share_govt)
        VALUES %s
    """
    execute_values(cur, insert_sql, records, page_size=1000)
    conn.commit()

    print(f"  Inserted {len(records)} SIPRI records")
    return len(records)

def load_maddison(conn):
    """Load Maddison GDP/population data."""
    print("Loading Maddison data...")

    # Get master countries
    master_df = get_master_countries(conn)
    master_by_iso = {row['iso_alpha3']: row['id'] for _, row in master_df.iterrows()}

    # Load Maddison data
    df = pd.read_csv('datasets/maddison/maddison_full_data.csv')

    # Filter to rows with data
    df = df[df['gdppc'].notna() | df['pop'].notna()]

    print(f"  Loaded {len(df)} Maddison records with data")

    # Build records with country linkage
    records = []
    matched = 0
    unmatched = set()

    for _, row in df.iterrows():
        code = row['countrycode']

        # Try to match to master.countries
        country_id = master_by_iso.get(code)
        if country_id:
            matched += 1
        else:
            unmatched.add(code)

        records.append((
            country_id,
            code,
            row['country'],
            row['region'],
            int(row['year']),
            row['gdppc'] if pd.notna(row['gdppc']) else None,
            row['pop'] if pd.notna(row['pop']) else None
        ))

    print(f"  Matched {matched} records to master.countries")
    print(f"  Unmatched codes: {sorted(unmatched)[:20]}...")

    # Insert into database
    cur = conn.cursor()
    cur.execute("TRUNCATE atrocity_economics.maddison_gdp RESTART IDENTITY")

    insert_sql = """
        INSERT INTO atrocity_economics.maddison_gdp
        (country_id, maddison_code, maddison_country, maddison_region, year,
         gdp_pc_2011_usd, population_thousands)
        VALUES %s
    """
    execute_values(cur, insert_sql, records, page_size=1000)
    conn.commit()

    print(f"  Inserted {len(records)} Maddison records")
    return len(records)

def add_country_code_mappings(conn):
    """Add SIPRI and Maddison codes to master.country_codes."""
    print("Adding code mappings...")
    cur = conn.cursor()

    # Add SIPRI mappings
    cur.execute("""
        INSERT INTO master.country_codes (country_id, code_system, code_value)
        SELECT DISTINCT country_id, 'sipri', sipri_country_name
        FROM atrocity_economics.sipri_milex
        WHERE country_id IS NOT NULL
        ON CONFLICT DO NOTHING
    """)

    # Add Maddison mappings
    cur.execute("""
        INSERT INTO master.country_codes (country_id, code_system, code_value)
        SELECT DISTINCT country_id, 'maddison', maddison_code
        FROM atrocity_economics.maddison_gdp
        WHERE country_id IS NOT NULL
        ON CONFLICT DO NOTHING
    """)

    conn.commit()
    print("  Code mappings added")

def main():
    print("=" * 60)
    print("Loading SIPRI and Maddison data")
    print("=" * 60)

    conn = get_connection()

    sipri_count = load_sipri(conn)
    maddison_count = load_maddison(conn)
    add_country_code_mappings(conn)

    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"SIPRI records: {sipri_count}")
    print(f"Maddison records: {maddison_count}")

    # Show sample query
    print("\n" + "=" * 60)
    print("Sample: US Military Spending + GDP (1975-2022)")
    print("=" * 60)

    query = """
        SELECT
            s.year,
            s.milex_constant_usd as milex_2023_usd_m,
            s.milex_share_gdp,
            m.gdp_pc_2011_usd as gdp_pc
        FROM atrocity_economics.sipri_milex s
        JOIN master.countries c ON s.country_id = c.id
        LEFT JOIN atrocity_economics.maddison_gdp m
            ON s.country_id = m.country_id AND s.year = m.year
        WHERE c.iso_alpha3 = 'USA'
        AND s.year IN (1975, 1980, 1990, 2000, 2010, 2020, 2022)
        ORDER BY s.year
    """
    df = pd.read_sql(query, conn)
    print(df.to_string(index=False))

    conn.close()
    print("\nDone!")

if __name__ == '__main__':
    main()
