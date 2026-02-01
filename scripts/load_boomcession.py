#!/usr/bin/env python3
"""
Load FRED datasets for the boomcession analysis into PostgreSQL.
"""

import os
import csv
from datetime import datetime
import psycopg2
from psycopg2.extras import execute_values

# Database connection
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "graphyard",
    "user": "postgres",
    "password": "postgres",
}

DATASETS_DIR = "/Users/bedwards/graphyard/datasets/boomcession"

# Map CSV filenames to series_id
CSV_FILES = [
    "UMCSENT.csv",
    "A191RL1Q225SBEA.csv",
    "W273RE1A156NBEA.csv",
    "LES1252881600Q.csv",
    "OPHNFB.csv",
    "W270RE1A156NBEA.csv",
    "USSTHPI.csv",
    "MEHOINUSA672N.csv",
    "MSPUS.csv",
    "PCE.csv",
    "DHLCRG3Q086SBEA.csv",
    "DHUTRC1Q027SBEA.csv",
    "CP.csv",
    "GDP.csv",
    "FIXHAI.csv",
]


def load_csv(filepath: str) -> list[tuple]:
    """Load a FRED CSV file and return list of (series_id, date, value) tuples."""
    series_id = os.path.basename(filepath).replace(".csv", "")
    rows = []

    with open(filepath, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            date_str = row["observation_date"]
            value_str = row.get(series_id, "")

            # Skip rows with missing values (FRED uses "." or empty string)
            if not value_str or value_str == ".":
                continue

            try:
                date = datetime.strptime(date_str, "%Y-%m-%d").date()
                value = float(value_str)
                rows.append((series_id, date, value))
            except (ValueError, KeyError) as e:
                print(f"  Skipping row in {series_id}: {e}")
                continue

    return rows


def main():
    """Load all FRED datasets into the boomcession schema."""
    print("Connecting to PostgreSQL...")
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Clear existing observations
    print("Clearing existing observations...")
    cur.execute("DELETE FROM boomcession.fred_observations")

    total_rows = 0

    for csv_file in CSV_FILES:
        filepath = os.path.join(DATASETS_DIR, csv_file)
        if not os.path.exists(filepath):
            print(f"  WARNING: {csv_file} not found, skipping")
            continue

        print(f"Loading {csv_file}...")
        rows = load_csv(filepath)

        if rows:
            execute_values(
                cur,
                """
                INSERT INTO boomcession.fred_observations (series_id, observation_date, value)
                VALUES %s
                ON CONFLICT (series_id, observation_date) DO UPDATE SET value = EXCLUDED.value
                """,
                rows,
            )
            print(f"  Loaded {len(rows)} rows")
            total_rows += len(rows)
        else:
            print(f"  No valid rows found")

    conn.commit()

    # Verify counts
    print("\nVerifying data loads...")
    cur.execute("""
        SELECT series_id, COUNT(*) as row_count, MIN(observation_date) as min_date, MAX(observation_date) as max_date
        FROM boomcession.fred_observations
        GROUP BY series_id
        ORDER BY series_id
    """)

    print("\n{:<25} {:>8} {:>12} {:>12}".format("Series", "Rows", "Start", "End"))
    print("-" * 60)
    for row in cur.fetchall():
        print("{:<25} {:>8} {:>12} {:>12}".format(row[0], row[1], str(row[2]), str(row[3])))

    print(f"\nTotal rows loaded: {total_rows}")

    cur.close()
    conn.close()
    print("\nDone!")


if __name__ == "__main__":
    main()
