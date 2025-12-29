#!/usr/bin/env python3
"""
Load baseball data into consolidated schema.

Usage:
    python scripts/load_baseball_data.py --players      # Populate master players
    python scripts/load_baseball_data.py --statcast     # Load Statcast data
    python scripts/load_baseball_data.py --retrosheet   # Load Retrosheet gamelogs
    python scripts/load_baseball_data.py --all          # Load everything
"""

import argparse
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text
import warnings
warnings.filterwarnings('ignore')

DB_URL = "postgresql://postgres:postgres@localhost:5432/graphyard"
engine = create_engine(DB_URL)

DATASETS_DIR = Path("datasets")
STATCAST_DIR = DATASETS_DIR / "statcast"
RETROSHEET_DIR = DATASETS_DIR / "retrosheet"


def load_master_players():
    """Populate baseball.players from lahman.people."""
    print("Loading master players from Lahman...")

    with engine.connect() as conn:
        # Get players from Lahman
        df = pd.read_sql("""
            SELECT
                player_id,
                name_first,
                name_last,
                name_given,
                birth_year, birth_month, birth_day,
                death_year, death_month, death_day,
                birth_country, birth_state, birth_city,
                bats, throws,
                height, weight,
                debut, final_game,
                retro_id, bbref_id
            FROM lahman.people
        """, conn)

        print(f"  Found {len(df)} players in Lahman")

        # Clear and reload
        conn.execute(text("TRUNCATE baseball.players RESTART IDENTITY CASCADE"))

        for _, row in df.iterrows():
            # Parse dates
            birth_date = None
            if pd.notna(row['birth_year']) and pd.notna(row['birth_month']) and pd.notna(row['birth_day']):
                try:
                    birth_date = f"{int(row['birth_year'])}-{int(row['birth_month']):02d}-{int(row['birth_day']):02d}"
                except:
                    pass

            death_date = None
            if pd.notna(row['death_year']) and pd.notna(row['death_month']) and pd.notna(row['death_day']):
                try:
                    death_date = f"{int(row['death_year'])}-{int(row['death_month']):02d}-{int(row['death_day']):02d}"
                except:
                    pass

            conn.execute(text("""
                INSERT INTO baseball.players (
                    lahman_id, retrosheet_id, bbref_id,
                    name_first, name_last, name_given,
                    birth_date, death_date,
                    birth_country, birth_state, birth_city,
                    bats, throws, height_inches, weight_lbs,
                    debut_date, final_game_date
                ) VALUES (
                    :lahman_id, :retro_id, :bbref_id,
                    :first, :last, :given,
                    :birth, :death,
                    :country, :state, :city,
                    :bats, :throws, :height, :weight,
                    :debut, :final
                )
            """), {
                "lahman_id": row['player_id'],
                "retro_id": row['retro_id'] if pd.notna(row['retro_id']) else None,
                "bbref_id": row['bbref_id'] if pd.notna(row['bbref_id']) else None,
                "first": row['name_first'],
                "last": row['name_last'],
                "given": row['name_given'] if pd.notna(row['name_given']) else None,
                "birth": birth_date,
                "death": death_date,
                "country": row['birth_country'] if pd.notna(row['birth_country']) else None,
                "state": row['birth_state'] if pd.notna(row['birth_state']) else None,
                "city": row['birth_city'] if pd.notna(row['birth_city']) else None,
                "bats": row['bats'] if pd.notna(row['bats']) else None,
                "throws": row['throws'] if pd.notna(row['throws']) else None,
                "height": int(row['height']) if pd.notna(row['height']) else None,
                "weight": int(row['weight']) if pd.notna(row['weight']) else None,
                "debut": row['debut'] if pd.notna(row['debut']) else None,
                "final": row['final_game'] if pd.notna(row['final_game']) else None,
            })

        conn.commit()
        print(f"  Loaded {len(df)} players into baseball.players")


def load_mlb_ids_from_statcast():
    """Extract MLB IDs from Statcast and update players table."""
    print("Extracting MLB IDs from Statcast...")

    # Load a sample of Statcast to get player mappings
    statcast_file = STATCAST_DIR / "statcast_2024.csv"
    if not statcast_file.exists():
        print("  No Statcast file found, skipping MLB ID extraction")
        return

    # Read just player columns
    df = pd.read_csv(statcast_file, usecols=['batter', 'pitcher', 'player_name'])

    # Get unique batters
    batters = df[['batter', 'player_name']].drop_duplicates()
    batters.columns = ['mlb_id', 'name']

    # player_name is pitcher name, need to get batter names differently
    # For now, just get unique MLB IDs
    all_ids = pd.concat([
        df[['batter']].rename(columns={'batter': 'mlb_id'}),
        df[['pitcher']].rename(columns={'pitcher': 'mlb_id'})
    ]).drop_duplicates()

    print(f"  Found {len(all_ids)} unique MLB IDs in Statcast 2024")

    # Note: Matching MLB IDs to Lahman IDs requires a lookup table
    # For now, we'll store them as-is and link during query time


def load_statcast_data(year=2024):
    """Load Statcast pitch data for a given year."""
    print(f"Loading Statcast {year} data...")

    statcast_file = STATCAST_DIR / f"statcast_{year}.csv"
    if not statcast_file.exists():
        print(f"  File not found: {statcast_file}")
        return

    # Read in chunks due to size
    chunk_size = 50000
    total_loaded = 0

    with engine.connect() as conn:
        # Don't truncate if loading multiple years
        if year == 2024:
            conn.execute(text("TRUNCATE baseball.statcast_pitches RESTART IDENTITY"))

        for chunk in pd.read_csv(statcast_file, chunksize=chunk_size, low_memory=False):
            # Select columns to load
            columns_map = {
                'game_pk': 'game_pk',
                'game_date': 'game_date',
                'at_bat_number': 'at_bat_number',
                'pitch_number': 'pitch_number',
                'pitcher': 'pitcher_mlb_id',
                'batter': 'batter_mlb_id',
                'pitch_type': 'pitch_type',
                'release_speed': 'release_speed',
                'release_spin_rate': 'release_spin_rate',
                'release_pos_x': 'release_pos_x',
                'release_pos_z': 'release_pos_z',
                'pfx_x': 'pfx_x',
                'pfx_z': 'pfx_z',
                'plate_x': 'plate_x',
                'plate_z': 'plate_z',
                'zone': 'zone',
                'launch_speed': 'launch_speed',
                'launch_angle': 'launch_angle',
                'hit_distance_sc': 'hit_distance',
                'bb_type': 'bb_type',
                'hc_x': 'hc_x',
                'hc_y': 'hc_y',
                'estimated_ba_using_speedangle': 'estimated_ba',
                'estimated_woba_using_speedangle': 'estimated_woba',
                'events': 'events',
                'description': 'description',
                'type': 'type',
                'balls': 'balls',
                'strikes': 'strikes',
                'outs_when_up': 'outs_when_up',
                'inning': 'inning',
                'inning_topbot': 'inning_topbot',
                'home_team': 'home_team',
                'away_team': 'away_team',
                'stand': 'stand',
                'p_throws': 'p_throws',
                'on_1b': 'on_1b',
                'on_2b': 'on_2b',
                'on_3b': 'on_3b',
                'home_score': 'home_score',
                'away_score': 'away_score',
                'bat_speed': 'bat_speed',
                'swing_length': 'swing_length',
            }

            # Filter to columns that exist
            available_cols = [c for c in columns_map.keys() if c in chunk.columns]
            df_chunk = chunk[available_cols].copy()
            df_chunk = df_chunk.rename(columns={k: v for k, v in columns_map.items() if k in available_cols})

            # Convert date
            if 'game_date' in df_chunk.columns:
                df_chunk['game_date'] = pd.to_datetime(df_chunk['game_date'], errors='coerce')

            # Insert
            df_chunk.to_sql('statcast_pitches', conn, schema='baseball',
                           if_exists='append', index=False, method='multi')

            total_loaded += len(df_chunk)
            print(f"    Loaded {total_loaded} pitches...")

        conn.commit()

    print(f"  Loaded {total_loaded} total pitches for {year}")


def load_retrosheet_gamelogs():
    """Load Retrosheet game logs."""
    print("Loading Retrosheet gamelogs...")

    gamelog_dir = RETROSHEET_DIR / "gamelogs"
    if not gamelog_dir.exists():
        print(f"  Directory not found: {gamelog_dir}")
        return

    # Retrosheet gamelogs have 161 columns - read by index position
    # See: https://www.retrosheet.org/gamelogs/glfields.txt
    # Column indices we need:
    #  0: date, 1: game_number, 2: day_of_week
    #  3: visiting_team, 4: visiting_league, 5: visiting_game_number
    #  6: home_team, 7: home_league, 8: home_game_number
    #  9: visitor_score, 10: home_score, 11: length_outs, 12: day_night
    # 16: park_id, 17: attendance, 18: duration
    # 19: visitor_line_score, 20: home_line_score
    # 21-48: visitor batting stats, 49-76: home batting stats

    col_indices = {
        0: 'date', 1: 'game_number', 2: 'day_of_week',
        3: 'visiting_team', 4: 'visiting_league', 5: 'visiting_game_number',
        6: 'home_team', 7: 'home_league', 8: 'home_game_number',
        9: 'visitor_score', 10: 'home_score', 11: 'length_outs', 12: 'day_night',
        16: 'park_id', 17: 'attendance', 18: 'duration',
        19: 'visitor_line_score', 20: 'home_line_score',
        21: 'visitor_ab', 22: 'visitor_h', 23: 'visitor_2b', 24: 'visitor_3b', 25: 'visitor_hr',
        26: 'visitor_rbi', 29: 'visitor_bb', 32: 'visitor_k', 33: 'visitor_sb', 45: 'visitor_errors',
        49: 'home_ab', 50: 'home_h', 51: 'home_2b', 52: 'home_3b', 53: 'home_hr',
        54: 'home_rbi', 57: 'home_bb', 60: 'home_k', 61: 'home_sb', 73: 'home_errors',
    }

    with engine.connect() as conn:
        conn.execute(text("TRUNCATE baseball.retrosheet_gamelogs RESTART IDENTITY"))

        total_games = 0
        for gl_file in sorted(gamelog_dir.glob("gl*.txt")):
            year = gl_file.stem[2:]  # Extract year from filename
            print(f"    Loading {gl_file.name}...")

            try:
                # Read without column names - let pandas auto-number them
                df = pd.read_csv(gl_file, header=None, low_memory=False)

                # Select only columns we need and rename
                selected_cols = list(col_indices.keys())
                df_selected = df[selected_cols].copy()
                df_selected.columns = [col_indices[i] for i in selected_cols]

                # Parse date
                df_selected['game_date'] = pd.to_datetime(df_selected['date'].astype(str), format='%Y%m%d', errors='coerce')

                # Build insert dataframe with proper column names for DB
                insert_df = pd.DataFrame({
                    'game_date': df_selected['game_date'],
                    'game_number': df_selected['game_number'],
                    'day_of_week': df_selected['day_of_week'],
                    'visiting_team': df_selected['visiting_team'],
                    'visiting_league': df_selected['visiting_league'],
                    'visiting_game_number': df_selected['visiting_game_number'],
                    'home_team': df_selected['home_team'],
                    'home_league': df_selected['home_league'],
                    'home_game_number': df_selected['home_game_number'],
                    'visitor_score': df_selected['visitor_score'],
                    'home_score': df_selected['home_score'],
                    'length_outs': df_selected['length_outs'],
                    'day_night': df_selected['day_night'],
                    'park_id': df_selected['park_id'],
                    'attendance': df_selected['attendance'],
                    'duration_minutes': df_selected['duration'],
                    'visitor_line_score': df_selected['visitor_line_score'],
                    'home_line_score': df_selected['home_line_score'],
                    'visitor_at_bats': df_selected['visitor_ab'],
                    'visitor_hits': df_selected['visitor_h'],
                    'visitor_doubles': df_selected['visitor_2b'],
                    'visitor_triples': df_selected['visitor_3b'],
                    'visitor_home_runs': df_selected['visitor_hr'],
                    'visitor_rbi': df_selected['visitor_rbi'],
                    'visitor_walks': df_selected['visitor_bb'],
                    'visitor_strikeouts': df_selected['visitor_k'],
                    'visitor_stolen_bases': df_selected['visitor_sb'],
                    'visitor_errors': df_selected['visitor_errors'],
                    'home_at_bats': df_selected['home_ab'],
                    'home_hits': df_selected['home_h'],
                    'home_doubles': df_selected['home_2b'],
                    'home_triples': df_selected['home_3b'],
                    'home_home_runs': df_selected['home_hr'],
                    'home_rbi': df_selected['home_rbi'],
                    'home_walks': df_selected['home_bb'],
                    'home_strikeouts': df_selected['home_k'],
                    'home_stolen_bases': df_selected['home_sb'],
                    'home_errors': df_selected['home_errors'],
                })

                insert_df.to_sql('retrosheet_gamelogs', conn, schema='baseball',
                                if_exists='append', index=False, method='multi')

                total_games += len(df)

            except Exception as e:
                print(f"      Error loading {gl_file.name}: {e}")
                continue

        conn.commit()
        print(f"  Loaded {total_games} total game logs")


def main():
    parser = argparse.ArgumentParser(description="Load baseball data")
    parser.add_argument("--players", action="store_true", help="Load master players")
    parser.add_argument("--statcast", action="store_true", help="Load Statcast data")
    parser.add_argument("--retrosheet", action="store_true", help="Load Retrosheet gamelogs")
    parser.add_argument("--all", action="store_true", help="Load everything")

    args = parser.parse_args()

    if args.all or args.players:
        load_master_players()
        load_mlb_ids_from_statcast()

    if args.all or args.retrosheet:
        load_retrosheet_gamelogs()

    if args.all or args.statcast:
        load_statcast_data(2024)
        load_statcast_data(2025)

    print("\nDone!")


if __name__ == "__main__":
    main()
