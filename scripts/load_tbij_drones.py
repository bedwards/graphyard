#!/usr/bin/env python3
"""
Load Bureau of Investigative Journalism (TBIJ) drone strike data into PostgreSQL.

Data source: https://dronewars.github.io/data/
Original research: https://www.thebureauinvestigates.com/projects/drone-war

Coverage: US drone strikes in Pakistan, Yemen, Somalia, and Afghanistan
Time period: 2002-2018 (varies by country)
"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
import re

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'graphyard',
    'user': 'postgres',
    'password': 'postgres'
}

EXCEL_PATH = 'datasets/tbij/DroneWarsData.xlsx'


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def safe_int(val):
    """Convert value to int, handling strings and NaN."""
    if pd.isna(val):
        return None
    if isinstance(val, (int, float)):
        return int(val) if not pd.isna(val) else None
    if isinstance(val, str):
        # Try to extract number from string
        match = re.search(r'\d+', str(val))
        if match:
            return int(match.group())
    return None


def safe_float(val, is_coordinate=False):
    """Convert value to float, handling strings and NaN."""
    if pd.isna(val):
        return None
    if isinstance(val, (int, float)):
        f = float(val) if not pd.isna(val) else None
        # Sanity check for coordinates
        if is_coordinate and f is not None and abs(f) > 180:
            return None
        return f
    if isinstance(val, str):
        # Skip Excel errors and unknown values
        if '#VALUE!' in val or 'Unknown' in val:
            return None
        # Handle leading commas
        val = val.strip().lstrip(',')
        try:
            f = float(val)
            # Sanity check for coordinates
            if is_coordinate and abs(f) > 180:
                return None
            return f
        except ValueError:
            return None
    return None


def parse_date(date_str):
    """Parse date string in MM-DD-YYYY format."""
    if pd.isna(date_str):
        return None
    try:
        # Try MM-DD-YYYY format
        return datetime.strptime(str(date_str), '%m-%d-%Y').date()
    except ValueError:
        try:
            # Try DD-MM-YYYY format
            return datetime.strptime(str(date_str), '%d-%m-%Y').date()
        except ValueError:
            return None


def normalize_country(country):
    """Normalize country names."""
    if pd.isna(country):
        return None
    country = str(country).strip()
    # Remove trailing spaces
    if country == 'Afghanistan ':
        return 'Afghanistan'
    return country


def create_schema(conn):
    """Create tbij schema and tables."""
    cur = conn.cursor()

    cur.execute("""
        CREATE SCHEMA IF NOT EXISTS tbij;

        DROP TABLE IF EXISTS tbij.drone_strikes CASCADE;
        DROP TABLE IF EXISTS tbij.country_summary CASCADE;
        DROP TABLE IF EXISTS tbij.annual_summary CASCADE;

        -- Individual drone strikes
        CREATE TABLE tbij.drone_strikes (
            id SERIAL PRIMARY KEY,
            strike_id VARCHAR(20) NOT NULL,
            country VARCHAR(50) NOT NULL,
            strike_date DATE,
            year SMALLINT,
            president VARCHAR(50),
            location TEXT,
            latitude DECIMAL(10, 6),
            longitude DECIMAL(10, 6),
            killed_min INTEGER,
            killed_max INTEGER,
            civilians_min INTEGER,
            civilians_max INTEGER,
            children_min INTEGER,
            children_max INTEGER,
            injured_min INTEGER,
            civilian_ratio DECIMAL(8, 4),
            source_sheet VARCHAR(50)
        );

        -- Summary by country
        CREATE TABLE tbij.country_summary (
            id SERIAL PRIMARY KEY,
            country VARCHAR(50) NOT NULL UNIQUE,
            iso_alpha3 CHAR(3),
            total_strikes INTEGER,
            first_strike DATE,
            last_strike DATE,
            killed_min INTEGER,
            killed_max INTEGER,
            civilians_min INTEGER,
            civilians_max INTEGER,
            children_min INTEGER,
            children_max INTEGER
        );

        -- Annual summary
        CREATE TABLE tbij.annual_summary (
            id SERIAL PRIMARY KEY,
            year SMALLINT NOT NULL,
            country VARCHAR(50) NOT NULL,
            president VARCHAR(50),
            strikes INTEGER,
            killed_min INTEGER,
            killed_max INTEGER,
            civilians_min INTEGER,
            civilians_max INTEGER,
            children_min INTEGER,
            children_max INTEGER,
            UNIQUE(year, country)
        );

        CREATE INDEX idx_drone_strikes_country ON tbij.drone_strikes(country);
        CREATE INDEX idx_drone_strikes_date ON tbij.drone_strikes(strike_date);
        CREATE INDEX idx_drone_strikes_year ON tbij.drone_strikes(year);
        CREATE INDEX idx_drone_strikes_president ON tbij.drone_strikes(president);
    """)
    conn.commit()
    print("Schema created: tbij")


def load_strikes(conn):
    """Load drone strike data from Excel."""
    print("Loading drone strikes from Excel...")

    # Read the consolidated 'All' sheet
    df = pd.read_excel(EXCEL_PATH, sheet_name='All')

    print(f"  Raw data: {len(df)} rows")

    # Clean and prepare data
    records = []
    for _, row in df.iterrows():
        country = normalize_country(row['Country'])
        if not country:
            continue

        strike_date = parse_date(row.get('Date (MM-DD-YYYY)'))
        year = strike_date.year if strike_date else None

        records.append((
            str(row['Strike ID']),
            country,
            strike_date,
            year,
            row.get('President'),
            row.get('Most Specific Location'),
            safe_float(row.get('Latitude'), is_coordinate=True),
            safe_float(row.get('Longitude'), is_coordinate=True),
            safe_int(row.get('Minimum total people killed')),
            safe_int(row.get('Maximum total people killed')),
            safe_int(row.get('Minimum civilians reported killed')),
            safe_int(row.get('Maximum civilians reported killed')),
            safe_int(row.get('Minimum children reported killed')),
            safe_int(row.get('Maximum children reported killed')),
            safe_int(row.get('Minimum reported injured')),
            safe_float(row.get('Ratio of Civilians to Total Killed')),
            'All'
        ))

    cur = conn.cursor()
    execute_values(cur, """
        INSERT INTO tbij.drone_strikes (
            strike_id, country, strike_date, year, president, location,
            latitude, longitude, killed_min, killed_max,
            civilians_min, civilians_max, children_min, children_max,
            injured_min, civilian_ratio, source_sheet
        ) VALUES %s
    """, records)

    conn.commit()
    print(f"  Loaded {len(records)} drone strikes")
    return len(records)


def compute_summaries(conn):
    """Compute summary tables from strike data."""
    cur = conn.cursor()

    # Country summary
    print("Computing country summaries...")
    cur.execute("""
        INSERT INTO tbij.country_summary (
            country, total_strikes, first_strike, last_strike,
            killed_min, killed_max, civilians_min, civilians_max,
            children_min, children_max
        )
        SELECT
            country,
            COUNT(*) as total_strikes,
            MIN(strike_date) as first_strike,
            MAX(strike_date) as last_strike,
            SUM(killed_min) as killed_min,
            SUM(killed_max) as killed_max,
            SUM(civilians_min) as civilians_min,
            SUM(civilians_max) as civilians_max,
            SUM(children_min) as children_min,
            SUM(children_max) as children_max
        FROM tbij.drone_strikes
        GROUP BY country
    """)

    # Add ISO codes
    cur.execute("""
        UPDATE tbij.country_summary cs
        SET iso_alpha3 = mc.iso_alpha3
        FROM master.countries mc
        WHERE LOWER(cs.country) = LOWER(mc.name)
    """)

    # Annual summary
    print("Computing annual summaries...")
    cur.execute("""
        INSERT INTO tbij.annual_summary (
            year, country, president, strikes,
            killed_min, killed_max, civilians_min, civilians_max,
            children_min, children_max
        )
        SELECT
            year,
            country,
            MODE() WITHIN GROUP (ORDER BY president) as president,
            COUNT(*) as strikes,
            SUM(killed_min) as killed_min,
            SUM(killed_max) as killed_max,
            SUM(civilians_min) as civilians_min,
            SUM(civilians_max) as civilians_max,
            SUM(children_min) as children_min,
            SUM(children_max) as children_max
        FROM tbij.drone_strikes
        WHERE year IS NOT NULL
        GROUP BY year, country
        ORDER BY year, country
    """)

    conn.commit()


def main():
    print("=" * 60)
    print("Loading TBIJ Drone Strike Data")
    print("Bureau of Investigative Journalism / Drone Wars")
    print("=" * 60)

    conn = get_connection()

    create_schema(conn)
    total = load_strikes(conn)
    compute_summaries(conn)

    # Summary statistics
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM tbij.drone_strikes")
    print(f"Total strikes: {cur.fetchone()[0]}")

    cur.execute("""
        SELECT country, total_strikes, killed_min, killed_max,
               civilians_min, civilians_max, first_strike, last_strike
        FROM tbij.country_summary
        ORDER BY total_strikes DESC
    """)
    print("\nBy country:")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]} strikes, {row[2]}-{row[3]} killed, "
              f"{row[4]}-{row[5]} civilians ({row[6]} to {row[7]})")

    cur.execute("""
        SELECT president, COUNT(*) as strikes,
               SUM(killed_min) as killed_min, SUM(killed_max) as killed_max,
               SUM(civilians_min) as civ_min, SUM(civilians_max) as civ_max
        FROM tbij.drone_strikes
        GROUP BY president
        ORDER BY strikes DESC
    """)
    print("\nBy president:")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]} strikes, {row[2]}-{row[3]} killed, "
              f"{row[4]}-{row[5]} civilians")

    # Date range
    cur.execute("""
        SELECT MIN(strike_date), MAX(strike_date)
        FROM tbij.drone_strikes
        WHERE strike_date IS NOT NULL
    """)
    dates = cur.fetchone()
    print(f"\nDate range: {dates[0]} to {dates[1]}")

    # Total casualties
    cur.execute("""
        SELECT
            SUM(killed_min), SUM(killed_max),
            SUM(civilians_min), SUM(civilians_max),
            SUM(children_min), SUM(children_max)
        FROM tbij.drone_strikes
    """)
    totals = cur.fetchone()
    print(f"\nTotal casualties:")
    print(f"  Killed: {totals[0]:,} - {totals[1]:,}")
    print(f"  Civilians: {totals[2]:,} - {totals[3]:,}")
    print(f"  Children: {totals[4]:,} - {totals[5]:,}")

    conn.close()
    print("\nDone!")


if __name__ == '__main__':
    main()
