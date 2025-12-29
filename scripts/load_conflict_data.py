#!/usr/bin/env python3
"""
Load conflict and health datasets into PostgreSQL.

Usage:
    python scripts/load_conflict_data.py --master     # Populate master.countries
    python scripts/load_conflict_data.py --ucdp       # Load UCDP data
    python scripts/load_conflict_data.py --cow        # Load COW data
    python scripts/load_conflict_data.py --pts        # Load PTS data
    python scripts/load_conflict_data.py --ibc        # Load Iraq Body Count
    python scripts/load_conflict_data.py --covid      # Load COVID-19 data
    python scripts/load_conflict_data.py --all        # Load everything
"""

import argparse
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text
import warnings
warnings.filterwarnings('ignore')

# Database connection
DB_URL = "postgresql://postgres:postgres@localhost:5432/graphyard"
engine = create_engine(DB_URL)

DATASETS_DIR = Path("datasets")
CONFLICT_DIR = DATASETS_DIR / "conflict"
HEALTH_DIR = DATASETS_DIR / "health"


def load_master_countries():
    """Populate master.countries from WDI entities table."""
    print("Loading master.countries from WDI entities...")

    with engine.connect() as conn:
        # Get countries from WDI
        df = pd.read_sql("""
            SELECT entity_code, entity_name, region
            FROM public.entities
            WHERE entity_type = 'country'
        """, conn)

        print(f"  Found {len(df)} countries in WDI")

        # Insert into master.countries
        for _, row in df.iterrows():
            conn.execute(text("""
                INSERT INTO master.countries (iso_alpha3, name, region)
                VALUES (:code, :name, :region)
                ON CONFLICT (iso_alpha3) DO UPDATE SET
                    name = EXCLUDED.name,
                    region = EXCLUDED.region
            """), {"code": row["entity_code"], "name": row["entity_name"], "region": row["region"]})

            # Add WDI code mapping
            conn.execute(text("""
                INSERT INTO master.country_codes (country_id, code_system, code_value)
                SELECT id, 'wdi', :code
                FROM master.countries WHERE iso_alpha3 = :code
                ON CONFLICT DO NOTHING
            """), {"code": row["entity_code"]})

        conn.commit()
        print(f"  Loaded {len(df)} countries into master.countries")


def load_cow_country_codes():
    """Add COW country codes to master.country_codes from PTS data."""
    print("Loading COW country codes from PTS...")

    pts_file = CONFLICT_DIR / "PTS-2025.csv"
    df = pd.read_csv(pts_file, encoding='latin-1')

    # Get unique country mappings
    mappings = df[['WordBank_Code_A', 'COW_Code_A', 'COW_Code_N', 'UN_Code_N']].drop_duplicates()
    mappings = mappings.dropna(subset=['WordBank_Code_A'])

    with engine.connect() as conn:
        count = 0
        for _, row in mappings.iterrows():
            wb_code = row['WordBank_Code_A']
            cow_alpha = row['COW_Code_A']
            cow_num = row['COW_Code_N']
            un_code = row['UN_Code_N']

            # Get country_id from WDI code
            result = conn.execute(text("""
                SELECT country_id FROM master.country_codes
                WHERE code_system = 'wdi' AND code_value = :code
            """), {"code": wb_code}).fetchone()

            if result:
                country_id = result[0]

                # Add COW alpha
                if pd.notna(cow_alpha):
                    conn.execute(text("""
                        INSERT INTO master.country_codes (country_id, code_system, code_value)
                        VALUES (:id, 'cow_alpha', :code)
                        ON CONFLICT DO NOTHING
                    """), {"id": country_id, "code": cow_alpha})

                # Add COW numeric
                if pd.notna(cow_num):
                    conn.execute(text("""
                        INSERT INTO master.country_codes (country_id, code_system, code_value)
                        VALUES (:id, 'cow_numeric', :code)
                        ON CONFLICT DO NOTHING
                    """), {"id": country_id, "code": str(int(cow_num))})

                # Add UN code
                if pd.notna(un_code):
                    conn.execute(text("""
                        INSERT INTO master.country_codes (country_id, code_system, code_value)
                        VALUES (:id, 'un_numeric', :code)
                        ON CONFLICT DO NOTHING
                    """), {"id": country_id, "code": str(int(un_code))})

                count += 1

        conn.commit()
        print(f"  Added country codes for {count} countries")


def load_pts_data():
    """Load Political Terror Scale data."""
    print("Loading PTS data...")

    pts_file = CONFLICT_DIR / "PTS-2025.csv"
    df = pd.read_csv(pts_file, encoding='latin-1')
    print(f"  Read {len(df)} rows from PTS-2025.csv")

    with engine.connect() as conn:
        # Clear existing data
        conn.execute(text("TRUNCATE pts.country_year_scores RESTART IDENTITY"))

        for _, row in df.iterrows():
            # Resolve country_id
            wb_code = row.get('WordBank_Code_A')
            country_id = None
            if pd.notna(wb_code):
                result = conn.execute(text("""
                    SELECT country_id FROM master.country_codes
                    WHERE code_system = 'wdi' AND code_value = :code
                """), {"code": wb_code}).fetchone()
                if result:
                    country_id = result[0]

            conn.execute(text("""
                INSERT INTO pts.country_year_scores (
                    country_id, country_name, year,
                    cow_code_alpha, cow_code_numeric, wb_code, un_code, region,
                    pts_amnesty, pts_state_dept, pts_hrw,
                    na_status_amnesty, na_status_state_dept, na_status_hrw
                ) VALUES (
                    :country_id, :name, :year,
                    :cow_a, :cow_n, :wb, :un, :region,
                    :pts_a, :pts_s, :pts_h,
                    :na_a, :na_s, :na_h
                )
            """), {
                "country_id": country_id,
                "name": row.get('Country'),
                "year": row.get('Year'),
                "cow_a": row.get('COW_Code_A') if pd.notna(row.get('COW_Code_A')) else None,
                "cow_n": int(row.get('COW_Code_N')) if pd.notna(row.get('COW_Code_N')) else None,
                "wb": row.get('WordBank_Code_A') if pd.notna(row.get('WordBank_Code_A')) else None,
                "un": int(row.get('UN_Code_N')) if pd.notna(row.get('UN_Code_N')) else None,
                "region": row.get('Region'),
                "pts_a": int(row.get('PTS_A')) if pd.notna(row.get('PTS_A')) else None,
                "pts_s": int(row.get('PTS_S')) if pd.notna(row.get('PTS_S')) else None,
                "pts_h": int(row.get('PTS_H')) if pd.notna(row.get('PTS_H')) else None,
                "na_a": int(row.get('NA_Status_A')) if pd.notna(row.get('NA_Status_A')) else None,
                "na_s": int(row.get('NA_Status_S')) if pd.notna(row.get('NA_Status_S')) else None,
                "na_h": int(row.get('NA_Status_H')) if pd.notna(row.get('NA_Status_H')) else None,
            })

        conn.commit()
        print(f"  Loaded {len(df)} country-year records into pts.country_year_scores")


def load_cow_nmc():
    """Load COW National Material Capabilities."""
    print("Loading COW National Material Capabilities...")

    nmc_file = CONFLICT_DIR / "cow" / "NMC-60-abridged.csv"
    df = pd.read_csv(nmc_file)
    print(f"  Read {len(df)} rows from NMC-60-abridged.csv")

    with engine.connect() as conn:
        conn.execute(text("TRUNCATE cow.national_capabilities RESTART IDENTITY"))

        for _, row in df.iterrows():
            cow_code = row.get('ccode')
            country_id = None

            if pd.notna(cow_code):
                result = conn.execute(text("""
                    SELECT country_id FROM master.country_codes
                    WHERE code_system = 'cow_numeric' AND code_value = :code
                """), {"code": str(int(cow_code))}).fetchone()
                if result:
                    country_id = result[0]

            conn.execute(text("""
                INSERT INTO cow.national_capabilities (
                    country_id, cow_code, state_abbrev, year,
                    milex, milper, irst, pec, tpop, upop, cinc, version
                ) VALUES (
                    :country_id, :cow_code, :abbrev, :year,
                    :milex, :milper, :irst, :pec, :tpop, :upop, :cinc, :version
                )
            """), {
                "country_id": country_id,
                "cow_code": int(cow_code) if pd.notna(cow_code) else None,
                "abbrev": row.get('stateabb'),
                "year": row.get('year'),
                "milex": int(row.get('milex')) if pd.notna(row.get('milex')) and row.get('milex') != -9 else None,
                "milper": int(row.get('milper')) if pd.notna(row.get('milper')) and row.get('milper') != -9 else None,
                "irst": int(row.get('irst')) if pd.notna(row.get('irst')) and row.get('irst') != -9 else None,
                "pec": int(row.get('pec')) if pd.notna(row.get('pec')) and row.get('pec') != -9 else None,
                "tpop": int(row.get('tpop')) if pd.notna(row.get('tpop')) and row.get('tpop') != -9 else None,
                "upop": int(row.get('upop')) if pd.notna(row.get('upop')) and row.get('upop') != -9 else None,
                "cinc": float(row.get('cinc')) if pd.notna(row.get('cinc')) and row.get('cinc') != -9 else None,
                "version": "6.0",
            })

        conn.commit()
        print(f"  Loaded {len(df)} capability records into cow.national_capabilities")


def load_cow_wars():
    """Load COW Inter-State Wars."""
    print("Loading COW Inter-State Wars...")

    war_file = CONFLICT_DIR / "cow" / "Inter-StateWarData_v4.0.csv"
    df = pd.read_csv(war_file)
    print(f"  Read {len(df)} rows from Inter-StateWarData_v4.0.csv")

    with engine.connect() as conn:
        conn.execute(text("TRUNCATE cow.war_participants RESTART IDENTITY CASCADE"))
        conn.execute(text("TRUNCATE cow.wars RESTART IDENTITY CASCADE"))

        # Get unique wars
        wars = df.groupby('WarNum').first().reset_index()

        for _, row in wars.iterrows():
            conn.execute(text("""
                INSERT INTO cow.wars (
                    war_num, war_name, war_type, war_type_name,
                    start_year, start_month, start_day,
                    end_year, end_month, end_day,
                    where_fought, version
                ) VALUES (
                    :war_num, :war_name, 1, 'Inter-State',
                    :start_year, :start_month, :start_day,
                    :end_year, :end_month, :end_day,
                    :where, '4.0'
                )
            """), {
                "war_num": row['WarNum'],
                "war_name": row['WarName'],
                "start_year": int(row['StartYear1']) if row['StartYear1'] != -8 else None,
                "start_month": int(row['StartMonth1']) if row['StartMonth1'] != -8 else None,
                "start_day": int(row['StartDay1']) if row['StartDay1'] != -8 else None,
                "end_year": int(row['EndYear1']) if row['EndYear1'] != -8 else None,
                "end_month": int(row['EndMonth1']) if row['EndMonth1'] != -8 else None,
                "end_day": int(row['EndDay1']) if row['EndDay1'] != -8 else None,
                "where": int(row['WhereFought']) if row['WhereFought'] != -8 else None,
            })

        # Load participants
        for _, row in df.iterrows():
            war_id_result = conn.execute(text("""
                SELECT id FROM cow.wars WHERE war_num = :num AND war_type = 1
            """), {"num": row['WarNum']}).fetchone()

            if war_id_result:
                cow_code = row['ccode']
                country_id = None
                if pd.notna(cow_code):
                    result = conn.execute(text("""
                        SELECT country_id FROM master.country_codes
                        WHERE code_system = 'cow_numeric' AND code_value = :code
                    """), {"code": str(int(cow_code))}).fetchone()
                    if result:
                        country_id = result[0]

                conn.execute(text("""
                    INSERT INTO cow.war_participants (
                        war_id, country_id, cow_code, state_name, side,
                        start_year, start_month, start_day,
                        end_year, end_month, end_day,
                        initiator, outcome, battle_deaths
                    ) VALUES (
                        :war_id, :country_id, :cow_code, :state, :side,
                        :start_year, :start_month, :start_day,
                        :end_year, :end_month, :end_day,
                        :init, :outcome, :deaths
                    )
                """), {
                    "war_id": war_id_result[0],
                    "country_id": country_id,
                    "cow_code": int(cow_code) if pd.notna(cow_code) else None,
                    "state": row['StateName'],
                    "side": int(row['Side']) if row['Side'] != -8 else None,
                    "start_year": int(row['StartYear1']) if row['StartYear1'] != -8 else None,
                    "start_month": int(row['StartMonth1']) if row['StartMonth1'] != -8 else None,
                    "start_day": int(row['StartDay1']) if row['StartDay1'] != -8 else None,
                    "end_year": int(row['EndYear1']) if row['EndYear1'] != -8 else None,
                    "end_month": int(row['EndMonth1']) if row['EndMonth1'] != -8 else None,
                    "end_day": int(row['EndDay1']) if row['EndDay1'] != -8 else None,
                    "init": row['Initiator'] == 1,
                    "outcome": int(row['Outcome']) if row['Outcome'] != -8 else None,
                    "deaths": int(row['BatDeath']) if row['BatDeath'] != -8 else None,
                })

        conn.commit()
        print(f"  Loaded {len(wars)} wars and {len(df)} participants")


def load_covid_data():
    """Load COVID-19 data from OWID."""
    print("Loading COVID-19 data from OWID...")

    covid_file = HEALTH_DIR / "owid_covid_data.csv"
    df = pd.read_csv(covid_file, low_memory=False)
    print(f"  Read {len(df)} rows from owid_covid_data.csv")

    # Select key columns to load
    columns_to_load = [
        'iso_code', 'location', 'continent', 'date',
        'total_cases', 'new_cases', 'total_deaths', 'new_deaths',
        'total_vaccinations', 'people_vaccinated', 'people_fully_vaccinated',
        'stringency_index', 'population', 'population_density',
        'median_age', 'gdp_per_capita', 'life_expectancy'
    ]

    df_subset = df[[c for c in columns_to_load if c in df.columns]].copy()
    df_subset['date'] = pd.to_datetime(df_subset['date'])

    with engine.connect() as conn:
        conn.execute(text("TRUNCATE health.covid_country_day RESTART IDENTITY"))

        # Batch insert
        batch_size = 10000
        total = len(df_subset)

        for i in range(0, total, batch_size):
            batch = df_subset.iloc[i:i+batch_size]
            batch.to_sql('covid_country_day', conn, schema='health',
                        if_exists='append', index=False, method='multi')
            print(f"    Loaded {min(i+batch_size, total)}/{total} rows...")

        conn.commit()
        print(f"  Loaded {total} COVID-19 records")


def load_ibc_incidents():
    """Load Iraq Body Count incidents."""
    print("Loading Iraq Body Count incidents...")

    ibc_file = CONFLICT_DIR / "ibc-incidents.csv"
    # Skip the header comment lines (11 lines of comments before column headers)
    df = pd.read_csv(ibc_file, skiprows=11)
    print(f"  Read {len(df)} rows from ibc-incidents.csv")

    with engine.connect() as conn:
        conn.execute(text("TRUNCATE ibc.incidents RESTART IDENTITY CASCADE"))

        for _, row in df.iterrows():
            conn.execute(text("""
                INSERT INTO ibc.incidents (
                    ibc_id, start_date, end_date, location, target, weapons,
                    deaths_min, deaths_max, sources
                ) VALUES (
                    :id, :start, :end, :location, :target, :weapons,
                    :min, :max, :sources
                )
            """), {
                "id": row.get('IBC code'),
                "start": pd.to_datetime(row.get('Start Date'), errors='coerce'),
                "end": pd.to_datetime(row.get('End Date'), errors='coerce'),
                "location": str(row.get('Location', ''))[:500] if pd.notna(row.get('Location')) else None,
                "target": str(row.get('Target', ''))[:500] if pd.notna(row.get('Target')) else None,
                "weapons": str(row.get('Weapons', '')) if pd.notna(row.get('Weapons')) else None,
                "min": int(row.get('Reported Minimum')) if pd.notna(row.get('Reported Minimum')) else None,
                "max": int(row.get('Reported Maximum')) if pd.notna(row.get('Reported Maximum')) else None,
                "sources": str(row.get('Sources', '')) if pd.notna(row.get('Sources')) else None,
            })

        conn.commit()
        print(f"  Loaded {len(df)} IBC incidents")


def main():
    parser = argparse.ArgumentParser(description="Load conflict and health data")
    parser.add_argument("--master", action="store_true", help="Load master.countries")
    parser.add_argument("--pts", action="store_true", help="Load PTS data")
    parser.add_argument("--cow", action="store_true", help="Load COW data")
    parser.add_argument("--covid", action="store_true", help="Load COVID data")
    parser.add_argument("--ibc", action="store_true", help="Load Iraq Body Count")
    parser.add_argument("--all", action="store_true", help="Load everything")

    args = parser.parse_args()

    if args.all or args.master:
        load_master_countries()
        load_cow_country_codes()

    if args.all or args.pts:
        load_pts_data()

    if args.all or args.cow:
        load_cow_nmc()
        load_cow_wars()

    if args.all or args.ibc:
        load_ibc_incidents()

    if args.all or args.covid:
        load_covid_data()

    print("\nDone!")


if __name__ == "__main__":
    main()
