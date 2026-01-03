#!/usr/bin/env python3
"""
Load Brown University Costs of War Project data into PostgreSQL.

Data compiled from published research at https://costsofwar.watson.brown.edu/

Sources:
- "Profits of War: Top Beneficiaries of Pentagon Spending, 2020-2024" (July 2025)
- "Human Cost of Post-9/11 Wars" (various reports)
- "United States Spending on Israeli Military Operations" (Oct 2024)
"""

import psycopg2
from psycopg2.extras import execute_values

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'graphyard',
    'user': 'postgres',
    'password': 'postgres'
}

# Post-9/11 War Costs (billions USD, constant 2025 dollars where available)
# Source: Costs of War Project
WAR_COSTS = [
    # (war_zone, category, start_year, end_year, amount_billions, notes)
    ("Afghanistan/Pakistan", "Total War Cost", 2001, 2021, 2300, "DOD, State, USAID, VA"),
    ("Iraq/Syria", "Total War Cost", 2003, 2023, 2890, "Including 550-580K deaths"),
    ("Post-9/11 Total", "Total War Cost", 2001, 2024, 8000, "All war zones combined"),
    ("Post-9/11 Total", "Future VA Obligations", 2001, 2050, 2200, "Estimated veteran care"),
    ("Post-9/11 Total", "Interest on War Debt", 2001, 2050, 1100, "Projected interest payments"),
]

# Pentagon Spending by Year (billions USD, constant 2025 dollars)
# Source: Costs of War "Profits of War" report
PENTAGON_SPENDING = [
    # (year, pentagon_budget, contracts_to_private, pct_to_contractors)
    (2000, 507, None, None),
    (2020, 778, 421, 54),
    (2021, 764, 413, 54),
    (2022, 780, 421, 54),
    (2023, 835, 451, 54),
    (2024, 843, 455, 54),
    (2025, 1060, 572, 54),  # Includes supplemental funding
]

# Top Defense Contractors (billions USD, 2020-2024)
# Source: Costs of War "Profits of War" report
CONTRACTORS = [
    # (contractor, contracts_2020, contracts_2021, contracts_2022, contracts_2023, contracts_2024, total)
    ("Lockheed Martin", 91, 47, 51, 73, 51, 313),
    ("RTX (Raytheon)", 33, 24, 29, 32, 27, 145),
    ("General Dynamics", 27, 20, 24, 25, 20, 116),
    ("Boeing", 26, 26, 16, 23, 24, 115),
    ("Northrop Grumman", 15, 15, 15, 17, 19, 81),
]

# Post-9/11 War Deaths (cumulative through 2023)
# Source: Costs of War "Human Cost" reports
WAR_DEATHS = [
    # (war_zone, category, deaths_low, deaths_mid, deaths_high, year_through)
    ("Afghanistan", "US Military", 2401, 2461, 2461, 2021),
    ("Afghanistan", "US Contractors", 3917, 3917, 3917, 2021),
    ("Afghanistan", "Afghan Military/Police", 66000, 69000, 72000, 2021),
    ("Afghanistan", "Taliban/Opposition", 51000, 53000, 55000, 2021),
    ("Afghanistan", "Civilians", 46000, 47000, 48000, 2021),
    ("Iraq", "US Military", 4550, 4600, 4600, 2023),
    ("Iraq", "US Contractors", 3650, 3650, 3650, 2023),
    ("Iraq", "Iraqi Military/Police", 41000, 43000, 45000, 2023),
    ("Iraq", "Opposition Fighters", 34000, 36000, 38000, 2023),
    ("Iraq", "Civilians", 185000, 200000, 210000, 2023),
    ("Syria", "Civilians", 12000, 13000, 14000, 2023),
    ("Pakistan", "Civilians", 24000, 24000, 24000, 2023),
    ("Yemen", "Civilians", 12000, 12000, 12000, 2023),
    ("Post-9/11 Total", "Direct Deaths (All)", 905000, 940000, 940000, 2023),
    ("Post-9/11 Total", "Indirect Deaths", 3600000, 3700000, 3800000, 2023),
    ("Post-9/11 Total", "Total Deaths", 4500000, 4700000, 4700000, 2023),
]

# US Military Aid (billions USD)
# Source: Costs of War reports
MILITARY_AID = [
    # (recipient, start_date, end_date, amount_billions, notes)
    ("Israel", "2023-10-07", "2024-09-30", 18.2, "First year after Oct 7"),
    ("Israel", "2023-10-07", "2025-09-30", 21.7, "Two years post Oct 7"),
    ("Ukraine", "2022-02-24", "2025-03-12", 66.0, "Since Russian invasion"),
    ("Europe (sales)", "2023-01-01", "2024-12-31", 170.0, "Foreign-funded arms sales"),
]

# Displaced persons
DISPLACED = [
    # (conflict, displaced_millions, year)
    ("Post-9/11 Wars", 38.0, 2021),
    ("Gaza/Israel/Lebanon", 5.27, 2025),
]


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def create_schema(conn):
    """Create costs_of_war schema and tables."""
    cur = conn.cursor()

    cur.execute("""
        CREATE SCHEMA IF NOT EXISTS costs_of_war;

        DROP TABLE IF EXISTS costs_of_war.war_costs CASCADE;
        DROP TABLE IF EXISTS costs_of_war.pentagon_spending CASCADE;
        DROP TABLE IF EXISTS costs_of_war.contractors CASCADE;
        DROP TABLE IF EXISTS costs_of_war.war_deaths CASCADE;
        DROP TABLE IF EXISTS costs_of_war.military_aid CASCADE;
        DROP TABLE IF EXISTS costs_of_war.displaced CASCADE;

        -- War costs by zone and category
        CREATE TABLE costs_of_war.war_costs (
            id SERIAL PRIMARY KEY,
            war_zone VARCHAR(100) NOT NULL,
            category VARCHAR(100) NOT NULL,
            start_year SMALLINT,
            end_year SMALLINT,
            amount_billions DECIMAL(10,2),
            notes TEXT
        );

        -- Annual Pentagon spending
        CREATE TABLE costs_of_war.pentagon_spending (
            id SERIAL PRIMARY KEY,
            year SMALLINT NOT NULL UNIQUE,
            budget_billions DECIMAL(10,2),
            contracts_billions DECIMAL(10,2),
            pct_to_contractors DECIMAL(5,2)
        );

        -- Defense contractor revenues
        CREATE TABLE costs_of_war.contractors (
            id SERIAL PRIMARY KEY,
            contractor VARCHAR(100) NOT NULL,
            contracts_2020 DECIMAL(10,2),
            contracts_2021 DECIMAL(10,2),
            contracts_2022 DECIMAL(10,2),
            contracts_2023 DECIMAL(10,2),
            contracts_2024 DECIMAL(10,2),
            total_2020_2024 DECIMAL(10,2)
        );

        -- War deaths by zone and category
        CREATE TABLE costs_of_war.war_deaths (
            id SERIAL PRIMARY KEY,
            war_zone VARCHAR(100) NOT NULL,
            category VARCHAR(100) NOT NULL,
            deaths_low INTEGER,
            deaths_mid INTEGER,
            deaths_high INTEGER,
            year_through SMALLINT
        );

        -- US Military aid
        CREATE TABLE costs_of_war.military_aid (
            id SERIAL PRIMARY KEY,
            recipient VARCHAR(100) NOT NULL,
            start_date DATE,
            end_date DATE,
            amount_billions DECIMAL(10,2),
            notes TEXT
        );

        -- Displaced persons
        CREATE TABLE costs_of_war.displaced (
            id SERIAL PRIMARY KEY,
            conflict VARCHAR(100) NOT NULL,
            displaced_millions DECIMAL(10,2),
            year SMALLINT
        );
    """)
    conn.commit()
    print("Schema created: costs_of_war")


def load_data(conn):
    """Load all Costs of War data."""
    cur = conn.cursor()

    # War costs
    print("Loading war costs...")
    for row in WAR_COSTS:
        cur.execute("""
            INSERT INTO costs_of_war.war_costs
            (war_zone, category, start_year, end_year, amount_billions, notes)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, row)

    # Pentagon spending
    print("Loading Pentagon spending...")
    for row in PENTAGON_SPENDING:
        cur.execute("""
            INSERT INTO costs_of_war.pentagon_spending
            (year, budget_billions, contracts_billions, pct_to_contractors)
            VALUES (%s, %s, %s, %s)
        """, row)

    # Contractors
    print("Loading contractor data...")
    for row in CONTRACTORS:
        cur.execute("""
            INSERT INTO costs_of_war.contractors
            (contractor, contracts_2020, contracts_2021, contracts_2022,
             contracts_2023, contracts_2024, total_2020_2024)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, row)

    # War deaths
    print("Loading war deaths...")
    for row in WAR_DEATHS:
        cur.execute("""
            INSERT INTO costs_of_war.war_deaths
            (war_zone, category, deaths_low, deaths_mid, deaths_high, year_through)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, row)

    # Military aid
    print("Loading military aid...")
    for row in MILITARY_AID:
        cur.execute("""
            INSERT INTO costs_of_war.military_aid
            (recipient, start_date, end_date, amount_billions, notes)
            VALUES (%s, %s, %s, %s, %s)
        """, row)

    # Displaced
    print("Loading displaced persons...")
    for row in DISPLACED:
        cur.execute("""
            INSERT INTO costs_of_war.displaced
            (conflict, displaced_millions, year)
            VALUES (%s, %s, %s)
        """, row)

    conn.commit()
    print("All data loaded.")


def main():
    print("=" * 60)
    print("Loading Brown University Costs of War Project Data")
    print("=" * 60)

    conn = get_connection()

    create_schema(conn)
    load_data(conn)

    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM costs_of_war.war_costs")
    print(f"War costs records: {cur.fetchone()[0]}")

    cur.execute("SELECT COUNT(*) FROM costs_of_war.pentagon_spending")
    print(f"Pentagon spending years: {cur.fetchone()[0]}")

    cur.execute("SELECT COUNT(*) FROM costs_of_war.contractors")
    print(f"Contractors: {cur.fetchone()[0]}")

    cur.execute("SELECT COUNT(*) FROM costs_of_war.war_deaths")
    print(f"War death categories: {cur.fetchone()[0]}")

    # Key findings
    print("\n" + "=" * 60)
    print("Key Findings: Post-9/11 Wars")
    print("=" * 60)

    cur.execute("""
        SELECT war_zone, category, deaths_mid
        FROM costs_of_war.war_deaths
        WHERE war_zone = 'Post-9/11 Total'
        ORDER BY deaths_mid DESC
    """)
    print("\nDeath tolls:")
    for row in cur.fetchall():
        print(f"  {row[1]}: {row[2]:,}")

    cur.execute("""
        SELECT war_zone, SUM(amount_billions) as total
        FROM costs_of_war.war_costs
        WHERE category = 'Total War Cost'
        GROUP BY war_zone
        ORDER BY total DESC
    """)
    print("\nWar costs (billions USD):")
    for row in cur.fetchall():
        print(f"  {row[0]}: ${row[1]:,.0f}B")

    # Top contractors
    print("\n" + "=" * 60)
    print("Top Pentagon Contractors (2020-2024)")
    print("=" * 60)

    cur.execute("""
        SELECT contractor, total_2020_2024
        FROM costs_of_war.contractors
        ORDER BY total_2020_2024 DESC
    """)
    for row in cur.fetchall():
        print(f"  {row[0]}: ${row[1]:,.0f}B")

    # Cross-reference with SIPRI
    print("\n" + "=" * 60)
    print("Cross-reference: US Military Spending")
    print("(Costs of War vs SIPRI)")
    print("=" * 60)

    cur.execute("""
        SELECT
            c.year,
            c.budget_billions as cow_budget,
            s.milex_constant_usd / 1000 as sipri_milex
        FROM costs_of_war.pentagon_spending c
        LEFT JOIN atrocity_economics.sipri_milex s
            ON c.year = s.year
        JOIN master.countries mc ON s.country_id = mc.id
        WHERE mc.iso_alpha3 = 'USA'
        AND c.year >= 2020
        ORDER BY c.year
    """)
    print(f"{'Year':<6} {'CoW Budget':<12} {'SIPRI MilEx':<12}")
    print("-" * 30)
    for row in cur.fetchall():
        cow = f"${row[1]:.0f}B" if row[1] else "N/A"
        sipri = f"${row[2]:.0f}B" if row[2] else "N/A"
        print(f"{row[0]:<6} {cow:<12} {sipri:<12}")

    conn.close()
    print("\nDone!")


if __name__ == '__main__':
    main()
