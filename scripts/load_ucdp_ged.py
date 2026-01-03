#!/usr/bin/env python3
"""
Load UCDP GED (Georeferenced Event Dataset) into PostgreSQL.

Populates:
- ucdp.actors (from side_a, side_b in GED)
- ucdp.conflicts (from conflict info in GED)
- ucdp.dyads (from dyad info in GED)
- ucdp.ged_events (main event data)
- Links to master.countries via Gleditsch-Ward codes
"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime

# Database connection
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'graphyard',
    'user': 'postgres',
    'password': 'postgres'
}

# Gleditsch-Ward to ISO alpha-3 mapping
# Source: https://www.andybeger.com/states/reference/gwstates.html
GW_TO_ISO = {
    2: 'USA', 20: 'CAN', 31: 'BHS', 40: 'CUB', 41: 'HTI', 42: 'DOM', 51: 'JAM',
    52: 'TTO', 53: 'BRB', 54: 'DMA', 55: 'GRD', 56: 'LCA', 57: 'VCT', 58: 'ATG',
    60: 'KNA', 70: 'MEX', 80: 'BLZ', 90: 'GTM', 91: 'HND', 92: 'SLV', 93: 'NIC',
    94: 'CRI', 95: 'PAN', 100: 'COL', 101: 'VEN', 110: 'GUY', 115: 'SUR',
    130: 'ECU', 135: 'PER', 140: 'BRA', 145: 'BOL', 150: 'PRY', 155: 'CHL',
    160: 'ARG', 165: 'URY', 200: 'GBR', 205: 'IRL', 210: 'NLD', 211: 'BEL',
    212: 'LUX', 220: 'FRA', 221: 'MCO', 223: 'LIE', 225: 'CHE', 230: 'ESP',
    232: 'AND', 235: 'PRT', 255: 'DEU', 260: 'DEU',  # 260 = West Germany -> DEU
    265: 'DEU',  # 265 = East Germany -> DEU
    290: 'POL', 305: 'AUT', 310: 'HUN', 315: 'CZE', 316: 'CZE',  # Czechoslovakia
    317: 'SVK', 325: 'ITA', 331: 'SMR', 338: 'MLT', 339: 'ALB',
    341: 'MNE', 343: 'MKD', 344: 'HRV', 345: 'SRB', 346: 'BIH', 349: 'SVN',
    350: 'GRC', 352: 'CYP', 355: 'BGR', 359: 'MDA', 360: 'ROU', 365: 'RUS',
    366: 'EST', 367: 'LVA', 368: 'LTU', 369: 'UKR', 370: 'BLR', 371: 'ARM',
    372: 'GEO', 373: 'AZE', 375: 'FIN', 380: 'SWE', 385: 'NOR', 390: 'DNK',
    395: 'ISL', 402: 'CPV', 403: 'STP', 404: 'GNB', 411: 'GNQ', 420: 'GMB',
    432: 'MLI', 433: 'SEN', 434: 'BEN', 435: 'MRT', 436: 'NER', 437: 'CIV',
    438: 'GIN', 439: 'BFA', 450: 'LBR', 451: 'SLE', 452: 'GHA', 461: 'TGO',
    471: 'CMR', 475: 'NGA', 481: 'GAB', 482: 'CAF', 483: 'TCD', 484: 'COG',
    490: 'COD', 500: 'UGA', 501: 'KEN', 510: 'TZA', 516: 'BDI', 517: 'RWA',
    520: 'SOM', 522: 'DJI', 530: 'ETH', 531: 'ERI', 540: 'AGO', 541: 'MOZ',
    551: 'ZMB', 552: 'ZWE', 553: 'MWI', 560: 'ZAF', 565: 'NAM', 570: 'LSO',
    571: 'BWA', 572: 'SWZ', 580: 'MDG', 581: 'COM', 590: 'MUS', 591: 'SYC',
    600: 'MAR', 615: 'DZA', 616: 'TUN', 620: 'LBY', 625: 'SDN', 626: 'SSD',
    630: 'IRN', 640: 'TUR', 645: 'IRQ', 651: 'EGY', 652: 'SYR', 660: 'LBN',
    663: 'JOR', 666: 'ISR', 670: 'SAU', 678: 'YEM', 679: 'YEM',  # North/South Yemen
    690: 'KWT', 692: 'BHR', 694: 'QAT', 696: 'ARE', 698: 'OMN', 700: 'AFG',
    701: 'TKM', 702: 'TJK', 703: 'KGZ', 704: 'UZB', 705: 'KAZ', 710: 'CHN',
    712: 'MNG', 713: 'TWN', 730: 'PRK', 731: 'PRK', 732: 'KOR', 740: 'JPN',
    750: 'IND', 760: 'BTN', 770: 'PAK', 771: 'BGD', 775: 'MMR', 780: 'LKA',
    781: 'MDV', 790: 'NPL', 800: 'THA', 811: 'KHM', 812: 'LAO', 816: 'VNM',
    817: 'VNM',  # South Vietnam
    820: 'MYS', 830: 'SGP', 835: 'BRN', 840: 'PHL', 850: 'IDN', 860: 'TLS',
    900: 'AUS', 910: 'PNG', 920: 'NZL', 935: 'VUT', 940: 'SLB', 950: 'FJI',
    970: 'KIR', 983: 'MHL', 986: 'PLW', 987: 'FSM', 990: 'WSM',
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def get_master_countries(conn):
    """Get mapping of ISO alpha-3 codes to country IDs."""
    query = "SELECT id, iso_alpha3, name FROM master.countries"
    df = pd.read_sql(query, conn)
    return {row['iso_alpha3']: row['id'] for _, row in df.iterrows()}


def build_gw_country_map(conn):
    """Build mapping from Gleditsch-Ward codes to master.countries IDs."""
    iso_to_master = get_master_countries(conn)
    gw_map = {}

    for gw_code, iso_code in GW_TO_ISO.items():
        if iso_code in iso_to_master:
            gw_map[gw_code] = iso_to_master[iso_code]

    print(f"  Mapped {len(gw_map)} Gleditsch-Ward codes to master.countries")
    return gw_map


def load_actors(conn, df):
    """Extract and load unique actors from GED data."""
    print("Loading actors...")

    # Extract unique actors from side_a and side_b
    actors_a = df[['side_a_new_id', 'side_a_dset_id', 'side_a']].drop_duplicates()
    actors_a.columns = ['actor_id', 'actor_dset_id', 'name']
    actors_a['actor_type'] = 'side_a'

    actors_b = df[['side_b_new_id', 'side_b_dset_id', 'side_b']].drop_duplicates()
    actors_b.columns = ['actor_id', 'actor_dset_id', 'name']
    actors_b['actor_type'] = 'side_b'

    # Combine and deduplicate by actor_id
    all_actors = pd.concat([actors_a, actors_b]).drop_duplicates(subset=['actor_id'])

    print(f"  Found {len(all_actors)} unique actors")

    # Insert into database
    cur = conn.cursor()
    cur.execute("TRUNCATE ucdp.actors RESTART IDENTITY CASCADE")

    records = [
        (int(row['actor_id']),
         int(row['actor_dset_id']) if pd.notna(row['actor_dset_id']) else None,
         str(row['name'])[:500],
         row['actor_type'])
        for _, row in all_actors.iterrows()
    ]

    insert_sql = """
        INSERT INTO ucdp.actors (actor_id, actor_dset_id, name, actor_type)
        VALUES %s
        ON CONFLICT (actor_id) DO NOTHING
    """
    execute_values(cur, insert_sql, records, page_size=500)
    conn.commit()

    # Get mapping of actor_id to internal id
    cur.execute("SELECT id, actor_id FROM ucdp.actors")
    actor_map = {row[1]: row[0] for row in cur.fetchall()}

    print(f"  Inserted {len(actor_map)} actors")
    return actor_map


def load_conflicts(conn, df):
    """Extract and load unique conflicts from GED data."""
    print("Loading conflicts...")

    conflicts = df[['conflict_new_id', 'conflict_dset_id', 'conflict_name',
                    'type_of_violence', 'region']].drop_duplicates(subset=['conflict_new_id'])

    print(f"  Found {len(conflicts)} unique conflicts")

    cur = conn.cursor()
    cur.execute("TRUNCATE ucdp.conflicts RESTART IDENTITY CASCADE")

    records = [
        (int(row['conflict_new_id']),
         int(row['conflict_dset_id']) if pd.notna(row['conflict_dset_id']) else None,
         str(row['conflict_name'])[:500],
         int(row['type_of_violence']),
         str(row['region'])[:100] if pd.notna(row['region']) else None)
        for _, row in conflicts.iterrows()
    ]

    insert_sql = """
        INSERT INTO ucdp.conflicts (conflict_id, conflict_dset_id, name, type_of_violence, region)
        VALUES %s
        ON CONFLICT (conflict_id) DO NOTHING
    """
    execute_values(cur, insert_sql, records, page_size=500)
    conn.commit()

    # Get mapping
    cur.execute("SELECT id, conflict_id FROM ucdp.conflicts")
    conflict_map = {row[1]: row[0] for row in cur.fetchall()}

    print(f"  Inserted {len(conflict_map)} conflicts")
    return conflict_map


def load_dyads(conn, df, actor_map, conflict_map):
    """Extract and load unique dyads from GED data."""
    print("Loading dyads...")

    dyads = df[['dyad_new_id', 'dyad_dset_id', 'dyad_name',
                'conflict_new_id', 'side_a_new_id', 'side_b_new_id']].drop_duplicates(subset=['dyad_new_id'])

    print(f"  Found {len(dyads)} unique dyads")

    cur = conn.cursor()
    cur.execute("TRUNCATE ucdp.dyads RESTART IDENTITY CASCADE")

    records = []
    for _, row in dyads.iterrows():
        conflict_db_id = conflict_map.get(int(row['conflict_new_id']))
        side_a_db_id = actor_map.get(int(row['side_a_new_id']))
        side_b_db_id = actor_map.get(int(row['side_b_new_id']))

        records.append((
            int(row['dyad_new_id']),
            int(row['dyad_dset_id']) if pd.notna(row['dyad_dset_id']) else None,
            str(row['dyad_name'])[:500] if pd.notna(row['dyad_name']) else None,
            conflict_db_id,
            side_a_db_id,
            side_b_db_id
        ))

    insert_sql = """
        INSERT INTO ucdp.dyads (dyad_id, dyad_dset_id, name, conflict_id, side_a_id, side_b_id)
        VALUES %s
        ON CONFLICT (dyad_id) DO NOTHING
    """
    execute_values(cur, insert_sql, records, page_size=500)
    conn.commit()

    # Get mapping
    cur.execute("SELECT id, dyad_id FROM ucdp.dyads")
    dyad_map = {row[1]: row[0] for row in cur.fetchall()}

    print(f"  Inserted {len(dyad_map)} dyads")
    return dyad_map


def load_events(conn, df, actor_map, conflict_map, dyad_map, gw_country_map):
    """Load GED events."""
    print("Loading events...")

    cur = conn.cursor()
    cur.execute("TRUNCATE ucdp.ged_events RESTART IDENTITY")

    batch_size = 10000
    total = len(df)
    inserted = 0

    for start in range(0, total, batch_size):
        batch = df.iloc[start:start + batch_size]
        records = []

        for _, row in batch.iterrows():
            # Map IDs
            conflict_db_id = conflict_map.get(int(row['conflict_new_id']))
            dyad_db_id = dyad_map.get(int(row['dyad_new_id']))
            side_a_db_id = actor_map.get(int(row['side_a_new_id']))
            side_b_db_id = actor_map.get(int(row['side_b_new_id']))
            country_db_id = gw_country_map.get(int(row['country_id'])) if pd.notna(row['country_id']) else None

            # Parse dates
            date_start = None
            date_end = None
            try:
                if pd.notna(row['date_start']):
                    date_start = pd.to_datetime(row['date_start']).date()
                if pd.notna(row['date_end']):
                    date_end = pd.to_datetime(row['date_end']).date()
            except:
                pass

            records.append((
                int(row['id']),  # event_id
                int(row['year']),
                row['active_year'] == True or str(row['active_year']).lower() == 'true',
                int(row['type_of_violence']),
                conflict_db_id,
                dyad_db_id,
                side_a_db_id,
                side_b_db_id,
                country_db_id,
                str(row['adm_1'])[:200] if pd.notna(row['adm_1']) else None,
                str(row['adm_2'])[:200] if pd.notna(row['adm_2']) else None,
                float(row['latitude']) if pd.notna(row['latitude']) else None,
                float(row['longitude']) if pd.notna(row['longitude']) else None,
                int(row['where_prec']) if pd.notna(row['where_prec']) else None,
                str(row['where_description'])[:2000] if pd.notna(row['where_description']) else None,
                date_start,
                date_end,
                int(row['date_prec']) if pd.notna(row['date_prec']) else None,
                int(row['deaths_a']) if pd.notna(row['deaths_a']) else None,
                int(row['deaths_b']) if pd.notna(row['deaths_b']) else None,
                int(row['deaths_civilians']) if pd.notna(row['deaths_civilians']) else None,
                int(row['deaths_unknown']) if pd.notna(row['deaths_unknown']) else None,
                int(row['best']) if pd.notna(row['best']) else None,
                int(row['low']) if pd.notna(row['low']) else None,
                int(row['high']) if pd.notna(row['high']) else None,
                str(row['source_article'])[:5000] if pd.notna(row['source_article']) else None,
                str(row['source_office'])[:1000] if pd.notna(row['source_office']) else None,
                int(row['number_of_sources']) if pd.notna(row['number_of_sources']) else None,
            ))

        insert_sql = """
            INSERT INTO ucdp.ged_events
            (event_id, year, active_year, type_of_violence, conflict_id, dyad_id,
             side_a_id, side_b_id, country_id, adm_1, adm_2, latitude, longitude,
             where_prec, where_description, date_start, date_end, date_prec,
             deaths_a, deaths_b, deaths_civilians, deaths_unknown,
             best_estimate, low_estimate, high_estimate,
             source_article, source_office, number_of_sources)
            VALUES %s
        """
        execute_values(cur, insert_sql, records, page_size=1000)
        inserted += len(records)
        print(f"  Inserted {inserted:,} / {total:,} events ({100*inserted/total:.1f}%)")

    conn.commit()
    print(f"  Total: {inserted:,} events inserted")
    return inserted


def add_country_code_mappings(conn, gw_country_map):
    """Add Gleditsch-Ward codes to master.country_codes."""
    print("Adding GW code mappings...")
    cur = conn.cursor()

    records = [(gw_code, master_id) for gw_code, master_id in gw_country_map.items()]

    insert_sql = """
        INSERT INTO master.country_codes (country_id, code_system, code_value)
        VALUES (%s, 'gw', %s)
        ON CONFLICT DO NOTHING
    """
    for master_id, gw_code in [(v, str(k)) for k, v in gw_country_map.items()]:
        cur.execute(insert_sql, (master_id, gw_code))

    conn.commit()
    print(f"  Added {len(records)} GW code mappings")


def main():
    print("=" * 60)
    print("Loading UCDP GED (Georeferenced Event Dataset)")
    print("=" * 60)

    # Load CSV
    print("\nReading GED CSV...")
    df = pd.read_csv('datasets/ucdp/GEDEvent_v25_1.csv', low_memory=False)
    print(f"  Loaded {len(df):,} events")
    print(f"  Year range: {df.year.min()} - {df.year.max()}")
    print(f"  Countries: {df.country.nunique()}")

    conn = get_connection()

    # Build country mapping first
    print("\nBuilding country mapping...")
    gw_country_map = build_gw_country_map(conn)

    # Load reference tables
    actor_map = load_actors(conn, df)
    conflict_map = load_conflicts(conn, df)
    dyad_map = load_dyads(conn, df, actor_map, conflict_map)

    # Load events
    event_count = load_events(conn, df, actor_map, conflict_map, dyad_map, gw_country_map)

    # Add code mappings
    add_country_code_mappings(conn, gw_country_map)

    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM ucdp.actors")
    print(f"Actors: {cur.fetchone()[0]:,}")

    cur.execute("SELECT COUNT(*) FROM ucdp.conflicts")
    print(f"Conflicts: {cur.fetchone()[0]:,}")

    cur.execute("SELECT COUNT(*) FROM ucdp.dyads")
    print(f"Dyads: {cur.fetchone()[0]:,}")

    cur.execute("SELECT COUNT(*) FROM ucdp.ged_events")
    print(f"Events: {cur.fetchone()[0]:,}")

    # Sample queries
    print("\n" + "=" * 60)
    print("Sample: Deaths by Year (2020-2024)")
    print("=" * 60)

    query = """
        SELECT
            year,
            COUNT(*) as events,
            SUM(best_estimate) as deaths_best,
            SUM(deaths_civilians) as civilian_deaths
        FROM ucdp.ged_events
        WHERE year >= 2020
        GROUP BY year
        ORDER BY year
    """
    result = pd.read_sql(query, conn)
    print(result.to_string(index=False))

    print("\n" + "=" * 60)
    print("Sample: Top 10 Countries by Events (1989-2024)")
    print("=" * 60)

    query = """
        SELECT
            c.name as country,
            COUNT(*) as events,
            SUM(g.best_estimate) as total_deaths
        FROM ucdp.ged_events g
        JOIN master.countries c ON g.country_id = c.id
        GROUP BY c.name
        ORDER BY events DESC
        LIMIT 10
    """
    result = pd.read_sql(query, conn)
    print(result.to_string(index=False))

    conn.close()
    print("\nDone!")


if __name__ == '__main__':
    main()
