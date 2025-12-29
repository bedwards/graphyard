#!/usr/bin/env python3
"""
Load Lahman Baseball Database into PostgreSQL

Downloads the latest Lahman database CSV files and loads them
into the 'lahman' schema in the graphyard database.

Usage:
    python scripts/load_lahman.py              # Full load
    python scripts/load_lahman.py --schema     # Create schema only
    python scripts/load_lahman.py --download   # Download only
"""

import argparse
import os
import sys
import zipfile
from pathlib import Path
import urllib.request
import shutil

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "datasets" / "lahman"
SCHEMA_FILE = PROJECT_ROOT / "scripts" / "lahman_schema.sql"

# Lahman download URL - from the R package source
LAHMAN_URL = "https://raw.githubusercontent.com/cdalzell/Lahman/master/source-data/baseballdatabank-master.zip"


def get_connection():
    """Get database connection."""
    return psycopg2.connect(
        host=os.getenv("GRAPHYARD_DB_HOST", "localhost"),
        port=int(os.getenv("GRAPHYARD_DB_PORT", "5432")),
        database=os.getenv("GRAPHYARD_DB_NAME", "graphyard"),
        user=os.getenv("GRAPHYARD_DB_USER", "postgres"),
        password=os.getenv("GRAPHYARD_DB_PASSWORD", "postgres"),
    )


def download_lahman():
    """Download Lahman database from R package GitHub source."""
    print("Downloading Lahman database...")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = DATA_DIR / "lahman.zip"

    # Download
    print(f"  Fetching from {LAHMAN_URL}")
    urllib.request.urlretrieve(LAHMAN_URL, zip_path)

    # Extract
    print(f"  Extracting to {DATA_DIR}")
    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(DATA_DIR)

    # Find the extracted directory (baseballdatabank-master)
    extracted_dir = DATA_DIR / "baseballdatabank-master"
    core_dir = extracted_dir / "core"

    # Also check for alternate structure
    if not core_dir.exists():
        # Try direct subdirectory
        for subdir in DATA_DIR.iterdir():
            if subdir.is_dir() and 'baseball' in subdir.name.lower():
                core_dir = subdir / "core"
                if core_dir.exists():
                    break
                # Try without core
                if (subdir / "People.csv").exists() or (subdir / "Batting.csv").exists():
                    core_dir = subdir
                    break

    if not core_dir.exists():
        # List what we have
        print(f"  Contents of {DATA_DIR}:")
        for item in DATA_DIR.iterdir():
            print(f"    {item}")
        print(f"  ERROR: Could not find CSV files")
        return None

    print(f"  CSV files located in {core_dir}")
    return core_dir


def create_schema():
    """Create the lahman schema."""
    print("Creating lahman schema...")

    with open(SCHEMA_FILE, 'r') as f:
        schema_sql = f.read()

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(schema_sql)
        conn.commit()
        print("  Schema created successfully")
    except Exception as e:
        print(f"  ERROR creating schema: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


# Mapping from CSV file names to table names and column mappings
TABLE_MAPPINGS = {
    "People.csv": {
        "table": "people",
        "columns": {
            "playerID": "player_id",
            "birthYear": "birth_year",
            "birthMonth": "birth_month",
            "birthDay": "birth_day",
            "birthCountry": "birth_country",
            "birthState": "birth_state",
            "birthCity": "birth_city",
            "deathYear": "death_year",
            "deathMonth": "death_month",
            "deathDay": "death_day",
            "deathCountry": "death_country",
            "deathState": "death_state",
            "deathCity": "death_city",
            "nameFirst": "name_first",
            "nameLast": "name_last",
            "nameGiven": "name_given",
            "weight": "weight",
            "height": "height",
            "bats": "bats",
            "throws": "throws",
            "debut": "debut",
            "finalGame": "final_game",
            "retroID": "retro_id",
            "bbrefID": "bbref_id",
        }
    },
    "Teams.csv": {
        "table": "teams",
        "columns": {
            "yearID": "year_id",
            "lgID": "lg_id",
            "teamID": "team_id",
            "franchID": "franch_id",
            "divID": "div_id",
            "Rank": "rank",
            "G": "games",
            "Ghome": "games_home",
            "W": "wins",
            "L": "losses",
            "DivWin": "div_win",
            "WCWin": "wc_win",
            "LgWin": "lg_win",
            "WSWin": "ws_win",
            "R": "runs",
            "AB": "at_bats",
            "H": "hits",
            "2B": "doubles",
            "3B": "triples",
            "HR": "home_runs",
            "BB": "walks",
            "SO": "strikeouts_batting",
            "SB": "stolen_bases",
            "CS": "caught_stealing",
            "HBP": "hit_by_pitch",
            "SF": "sacrifice_flies",
            "RA": "runs_allowed",
            "ER": "earned_runs",
            "ERA": "era",
            "CG": "complete_games",
            "SHO": "shutouts",
            "SV": "saves",
            "IPouts": "outs_pitched",
            "HA": "hits_allowed",
            "HRA": "home_runs_allowed",
            "BBA": "walks_allowed",
            "SOA": "strikeouts_pitching",
            "E": "errors",
            "DP": "double_plays",
            "FP": "fielding_pct",
            "name": "name",
            "park": "park",
            "attendance": "attendance",
            "BPF": "bpf",
            "PPF": "ppf",
            "teamIDBR": "team_id_br",
            "teamIDlahman45": "team_id_lahman45",
            "teamIDretro": "team_id_retro",
        }
    },
    "TeamsFranchises.csv": {
        "table": "teams_franchises",
        "columns": {
            "franchID": "franch_id",
            "franchName": "franch_name",
            "active": "active",
            "NAassoc": "na_assoc",
        }
    },
    "Parks.csv": {
        "table": "parks",
        "columns": {
            "park.key": "park_id",
            "park.name": "park_name",
            "park.alias": "park_alias",
            "city": "city",
            "state": "state",
            "country": "country",
        }
    },
    "Schools.csv": {
        "table": "schools",
        "columns": {
            "schoolID": "school_id",
            "name_full": "school_name",
            "city": "school_city",
            "state": "school_state",
            "country": "school_country",
        }
    },
    "Batting.csv": {
        "table": "batting",
        "columns": {
            "playerID": "player_id",
            "yearID": "year_id",
            "stint": "stint",
            "teamID": "team_id",
            "lgID": "lg_id",
            "G": "games",
            "AB": "at_bats",
            "R": "runs",
            "H": "hits",
            "2B": "doubles",
            "3B": "triples",
            "HR": "home_runs",
            "RBI": "rbi",
            "SB": "stolen_bases",
            "CS": "caught_stealing",
            "BB": "walks",
            "SO": "strikeouts",
            "IBB": "intentional_walks",
            "HBP": "hit_by_pitch",
            "SH": "sacrifice_hits",
            "SF": "sacrifice_flies",
            "GIDP": "gidp",
        }
    },
    "Pitching.csv": {
        "table": "pitching",
        "columns": {
            "playerID": "player_id",
            "yearID": "year_id",
            "stint": "stint",
            "teamID": "team_id",
            "lgID": "lg_id",
            "W": "wins",
            "L": "losses",
            "G": "games",
            "GS": "games_started",
            "CG": "complete_games",
            "SHO": "shutouts",
            "SV": "saves",
            "IPouts": "outs_pitched",
            "H": "hits",
            "ER": "earned_runs",
            "HR": "home_runs",
            "BB": "walks",
            "SO": "strikeouts",
            "BAOpp": "opponent_batting_avg",
            "ERA": "era",
            "IBB": "intentional_walks",
            "WP": "wild_pitches",
            "HBP": "hit_batters",
            "BK": "balks",
            "BFP": "batters_faced",
            "GF": "games_finished",
            "R": "runs",
            "SH": "sacrifice_hits",
            "SF": "sacrifice_flies",
            "GIDP": "gidp",
        }
    },
    "Fielding.csv": {
        "table": "fielding",
        "columns": {
            "playerID": "player_id",
            "yearID": "year_id",
            "stint": "stint",
            "teamID": "team_id",
            "lgID": "lg_id",
            "POS": "pos",
            "G": "games",
            "GS": "games_started",
            "InnOuts": "innings_outs",
            "PO": "putouts",
            "A": "assists",
            "E": "errors",
            "DP": "double_plays",
            "PB": "passed_balls",
            "WP": "wild_pitches",
            "SB": "stolen_bases_against",
            "CS": "caught_stealing_against",
            "ZR": "zone_rating",
        }
    },
    "Salaries.csv": {
        "table": "salaries",
        "columns": {
            "yearID": "year_id",
            "teamID": "team_id",
            "lgID": "lg_id",
            "playerID": "player_id",
            "salary": "salary",
        }
    },
    "HallOfFame.csv": {
        "table": "hall_of_fame",
        "columns": {
            "playerID": "player_id",
            "yearid": "year_id",
            "votedBy": "voted_by",
            "ballots": "ballots",
            "needed": "needed",
            "votes": "votes",
            "inducted": "inducted",
            "category": "category",
            "needed_note": "needed_note",
        }
    },
    "AllstarFull.csv": {
        "table": "allstar_full",
        "columns": {
            "playerID": "player_id",
            "yearID": "year_id",
            "gameNum": "game_num",
            "gameID": "game_id",
            "teamID": "team_id",
            "lgID": "lg_id",
            "GP": "gp",
            "startingPos": "starting_pos",
        }
    },
    "AwardsPlayers.csv": {
        "table": "awards_players",
        "columns": {
            "playerID": "player_id",
            "awardID": "award_id",
            "yearID": "year_id",
            "lgID": "lg_id",
            "tie": "tie",
            "notes": "notes",
        }
    },
    "Managers.csv": {
        "table": "managers",
        "columns": {
            "playerID": "player_id",
            "yearID": "year_id",
            "teamID": "team_id",
            "lgID": "lg_id",
            "inseason": "inseason",
            "G": "games",
            "W": "wins",
            "L": "losses",
            "rank": "rank",
            "plyrMgr": "plyr_mgr",
        }
    },
    "Appearances.csv": {
        "table": "appearances",
        "columns": {
            "yearID": "year_id",
            "teamID": "team_id",
            "lgID": "lg_id",
            "playerID": "player_id",
            "G_all": "games_all",
            "GS": "games_start",
            "G_batting": "games_batting",
            "G_defense": "games_defense",
            "G_p": "games_p",
            "G_c": "games_c",
            "G_1b": "games_1b",
            "G_2b": "games_2b",
            "G_3b": "games_3b",
            "G_ss": "games_ss",
            "G_lf": "games_lf",
            "G_cf": "games_cf",
            "G_rf": "games_rf",
            "G_of": "games_of",
            "G_dh": "games_dh",
            "G_ph": "games_ph",
            "G_pr": "games_pr",
        }
    },
    "CollegePlaying.csv": {
        "table": "college_playing",
        "columns": {
            "playerID": "player_id",
            "schoolID": "school_id",
            "yearID": "year_id",
        }
    },
    "HomeGames.csv": {
        "table": "home_games",
        "columns": {
            "year.key": "year_id",
            "league.key": "lg_id",
            "team.key": "team_id",
            "park.key": "park_id",
            "span.first": "first_game",
            "span.last": "last_game",
            "games": "games",
            "openings": "openings",
            "attendance": "attendance",
        }
    },
}

# Load order (respects foreign key dependencies)
LOAD_ORDER = [
    "People.csv",
    "Schools.csv",
    "Parks.csv",
    "TeamsFranchises.csv",
    "Teams.csv",
    "Batting.csv",
    "Pitching.csv",
    "Fielding.csv",
    "Salaries.csv",
    "HallOfFame.csv",
    "AllstarFull.csv",
    "AwardsPlayers.csv",
    "Managers.csv",
    "Appearances.csv",
    "CollegePlaying.csv",
    "HomeGames.csv",
]


def clean_value(val, col_name: str):
    """Clean a value for database insertion."""
    import math

    # Handle NaN and None
    if val is None:
        return None
    if isinstance(val, float) and math.isnan(val):
        return None

    # Handle empty strings
    if isinstance(val, str):
        val = val.strip()
        if val == '' or val.lower() == 'na' or val.lower() == 'nan':
            return None

    return val


def load_csv_to_table(csv_path: Path, mapping: dict, conn):
    """Load a CSV file into its corresponding table."""
    table_name = mapping["table"]
    col_map = mapping["columns"]

    print(f"  Loading {csv_path.name} -> lahman.{table_name}")

    # Read CSV - keep everything as string initially to avoid conversion issues
    df = pd.read_csv(csv_path, low_memory=False, dtype=str, na_values=['', 'NA'])

    # Only keep columns that exist in both CSV and mapping
    csv_cols = [c for c in col_map.keys() if c in df.columns]
    if not csv_cols:
        print(f"    WARNING: No matching columns found")
        return

    df = df[csv_cols]

    # Rename columns
    df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})

    # Get column names for insert
    columns = list(df.columns)
    col_str = ", ".join(columns)
    placeholders = ", ".join(["%s"] * len(columns))

    # Clean data - convert values
    values = []
    for _, row in df.iterrows():
        cleaned_row = tuple(clean_value(v, col) for v, col in zip(row.values, columns))
        values.append(cleaned_row)

    # Truncate existing data
    cur = conn.cursor()
    cur.execute(f"TRUNCATE lahman.{table_name} CASCADE")

    # Insert data in batches
    batch_size = 1000
    inserted = 0

    for i in range(0, len(values), batch_size):
        batch = values[i:i + batch_size]
        try:
            cur.executemany(
                f"INSERT INTO lahman.{table_name} ({col_str}) VALUES ({placeholders})",
                batch
            )
            inserted += len(batch)
        except Exception as e:
            print(f"    ERROR inserting batch: {e}")
            # Print first row of batch for debugging
            if batch:
                print(f"    First row: {batch[0][:5]}...")
            conn.rollback()
            raise

    conn.commit()
    print(f"    Inserted {inserted:,} rows")


def load_data(csv_dir: Path):
    """Load all CSV files into the database."""
    print("Loading data into lahman schema...")

    conn = get_connection()

    for csv_name in LOAD_ORDER:
        csv_path = csv_dir / csv_name

        if not csv_path.exists():
            print(f"  SKIPPING {csv_name} (not found)")
            continue

        if csv_name not in TABLE_MAPPINGS:
            print(f"  SKIPPING {csv_name} (no mapping)")
            continue

        try:
            load_csv_to_table(csv_path, TABLE_MAPPINGS[csv_name], conn)
        except Exception as e:
            print(f"  ERROR loading {csv_name}: {e}")

    conn.close()
    print("Data loading complete!")


def verify_load():
    """Verify data was loaded correctly."""
    print("\nVerifying data load...")

    conn = get_connection()
    cur = conn.cursor()

    tables = [
        "people", "teams", "batting", "pitching", "fielding",
        "salaries", "hall_of_fame", "allstar_full"
    ]

    for table in tables:
        cur.execute(f"SELECT COUNT(*) FROM lahman.{table}")
        count = cur.fetchone()[0]
        print(f"  lahman.{table}: {count:,} rows")

    # Sample query: Top 10 career home run leaders
    print("\n  Top 10 Career Home Run Leaders:")
    cur.execute("""
        SELECT p.name_first || ' ' || p.name_last as name,
               SUM(b.home_runs) as career_hr
        FROM lahman.batting b
        JOIN lahman.people p ON b.player_id = p.player_id
        GROUP BY p.player_id, p.name_first, p.name_last
        ORDER BY career_hr DESC
        LIMIT 10
    """)
    for row in cur.fetchall():
        print(f"    {row[0]}: {row[1]:,} HR")

    cur.close()
    conn.close()


def main():
    parser = argparse.ArgumentParser(description="Load Lahman database")
    parser.add_argument("--schema", action="store_true", help="Create schema only")
    parser.add_argument("--download", action="store_true", help="Download only")
    parser.add_argument("--verify", action="store_true", help="Verify load only")
    args = parser.parse_args()

    if args.verify:
        verify_load()
        return

    if args.schema:
        create_schema()
        return

    # Full load
    csv_dir = download_lahman()
    if csv_dir is None:
        print("Download failed!")
        sys.exit(1)

    if args.download:
        print("Download complete. Use --schema and then run again to load.")
        return

    create_schema()
    load_data(csv_dir)
    verify_load()


if __name__ == "__main__":
    main()
