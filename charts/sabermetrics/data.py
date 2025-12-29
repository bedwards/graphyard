"""
Data loaders for the Sabermetrics Pioneers article.

Validates and extends the work of Bill James, Mike Gimbel, and STATS, Inc.
using the Lahman database (1871-2024).

Key validations:
- Pythagorean Expectation: Win% = R^2 / (R^2 + RA^2)
- Runs Created: (H + BB) * TB / (AB + BB)
- Range Factor: (PO + A) / G
"""

import pandas as pd
from shared.database import get_connection


def load_pythagorean_validation(start_year: int = 1901, end_year: int = 2024):
    """
    Validate Bill James' Pythagorean Expectation formula.

    James discovered in 1980 that a team's win percentage can be predicted
    from runs scored and runs allowed using the formula:
    Expected Win% = RS^2 / (RS^2 + RA^2)

    Returns actual vs expected wins for each team-season.
    """
    conn = get_connection()
    query = """
        SELECT year_id, team_id, name,
               wins, losses, games,
               runs as runs_scored, runs_allowed,
               CAST(wins AS FLOAT) / NULLIF(wins + losses, 0) as actual_win_pct,
               POWER(runs, 2.0) / NULLIF(POWER(runs, 2.0) + POWER(runs_allowed, 2.0), 0) as expected_win_pct
        FROM lahman.teams
        WHERE year_id BETWEEN %s AND %s
          AND runs IS NOT NULL
          AND runs_allowed IS NOT NULL
          AND wins + losses > 100
        ORDER BY year_id, team_id
    """
    df = pd.read_sql(query, conn, params=(start_year, end_year))
    conn.close()

    # Calculate expected wins and error
    df['expected_wins'] = df['expected_win_pct'] * df['games']
    df['pythagorean_error'] = df['wins'] - df['expected_wins']

    return df


def load_pythagorean_accuracy_by_decade():
    """
    Calculate Pythagorean formula accuracy by decade.
    Shows how well the formula predicts wins across different eras.
    """
    conn = get_connection()
    query = """
        SELECT
            (year_id / 10) * 10 as decade,
            COUNT(*) as team_seasons,
            AVG(POWER(runs, 2.0) / NULLIF(POWER(runs, 2.0) + POWER(runs_allowed, 2.0), 0)) as avg_expected_pct,
            AVG(CAST(wins AS FLOAT) / NULLIF(wins + losses, 0)) as avg_actual_pct
        FROM lahman.teams
        WHERE year_id >= 1901
          AND runs IS NOT NULL
          AND runs_allowed IS NOT NULL
          AND wins + losses > 100
        GROUP BY (year_id / 10) * 10
        ORDER BY decade
    """
    df = pd.read_sql(query, conn)
    conn.close()

    # Calculate accuracy (how close expected is to actual)
    df['mean_abs_error'] = abs(df['avg_expected_pct'] - df['avg_actual_pct'])

    return df


def load_runs_created_validation(year: int = 2023):
    """
    Validate Bill James' Runs Created formula at the team level.

    Basic RC = (H + BB) * TB / (AB + BB)
    Total Bases = H + 2B + 2*3B + 3*HR

    Returns team-level actual runs vs RC prediction.
    """
    conn = get_connection()
    query = """
        SELECT year_id, team_id, name,
               runs as actual_runs,
               hits, doubles, triples, home_runs, walks, at_bats,
               -- Total Bases = H + 2B + 2*3B + 3*HR
               hits + doubles + 2*triples + 3*home_runs as total_bases
        FROM lahman.teams
        WHERE year_id = %s
          AND at_bats > 0
          AND hits + walks > 0
        ORDER BY runs DESC
    """
    df = pd.read_sql(query, conn, params=(year,))
    conn.close()

    # Calculate Runs Created
    # RC = (H + BB) * TB / (AB + BB)
    df['runs_created'] = (
        (df['hits'] + df['walks']) * df['total_bases'] /
        (df['at_bats'] + df['walks'])
    )
    df['rc_error'] = df['actual_runs'] - df['runs_created']
    df['rc_error_pct'] = df['rc_error'] / df['actual_runs'] * 100

    return df


def load_runs_created_historical():
    """
    Historical accuracy of Runs Created formula across all seasons.
    """
    conn = get_connection()
    query = """
        SELECT year_id,
               COUNT(*) as teams,
               SUM(runs) as total_actual_runs,
               SUM(hits) as total_hits,
               SUM(walks) as total_walks,
               SUM(at_bats) as total_ab,
               SUM(hits + doubles + 2*triples + 3*home_runs) as total_tb
        FROM lahman.teams
        WHERE year_id >= 1901
          AND at_bats > 0
        GROUP BY year_id
        ORDER BY year_id
    """
    df = pd.read_sql(query, conn)
    conn.close()

    # Calculate league-wide Runs Created
    df['total_rc'] = (
        (df['total_hits'] + df['total_walks']) * df['total_tb'] /
        (df['total_ab'] + df['total_walks'])
    )
    df['accuracy_pct'] = 100 - abs(df['total_actual_runs'] - df['total_rc']) / df['total_actual_runs'] * 100

    return df


def load_home_run_evolution():
    """
    Track home run rates across eras to show game transformation.
    Bill James was one of the first to systematically analyze era effects.
    """
    conn = get_connection()
    query = """
        SELECT year_id,
               SUM(home_runs) as total_hr,
               SUM(games) / 2 as total_games,
               CAST(SUM(home_runs) AS FLOAT) / NULLIF(SUM(games) / 2, 0) as hr_per_game
        FROM lahman.teams
        WHERE year_id >= 1901
        GROUP BY year_id
        ORDER BY year_id
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


def load_batting_average_evolution():
    """
    Track league batting average across eras.
    Shows the Dead Ball Era, Live Ball Era, and modern changes.
    """
    conn = get_connection()
    query = """
        SELECT year_id,
               SUM(hits) as total_hits,
               SUM(at_bats) as total_ab,
               CAST(SUM(hits) AS FLOAT) / NULLIF(SUM(at_bats), 0) as league_avg
        FROM lahman.teams
        WHERE year_id >= 1901
        GROUP BY year_id
        ORDER BY year_id
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


def load_strikeout_walk_evolution():
    """
    Track strikeout and walk rates across eras.
    Modern era is characterized by "three true outcomes."
    """
    conn = get_connection()
    query = """
        SELECT year_id,
               CAST(SUM(strikeouts_batting) AS FLOAT) / NULLIF(SUM(at_bats), 0) * 100 as k_rate,
               CAST(SUM(walks) AS FLOAT) / NULLIF(SUM(at_bats + walks), 0) * 100 as bb_rate
        FROM lahman.teams
        WHERE year_id >= 1901
        GROUP BY year_id
        ORDER BY year_id
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


def load_stolen_base_evolution():
    """
    Track stolen base attempts and success rates.
    Shows how base-stealing strategy has changed.
    """
    conn = get_connection()
    query = """
        SELECT year_id,
               SUM(stolen_bases) as total_sb,
               SUM(caught_stealing) as total_cs,
               SUM(games) / 2 as total_games,
               CAST(SUM(stolen_bases) AS FLOAT) / NULLIF(SUM(games) / 2, 0) as sb_per_game,
               CAST(SUM(stolen_bases) AS FLOAT) / NULLIF(SUM(stolen_bases) + SUM(caught_stealing), 0) as sb_success_rate
        FROM lahman.teams
        WHERE year_id >= 1920  -- CS data mostly unavailable before 1920
          AND caught_stealing IS NOT NULL
        GROUP BY year_id
        ORDER BY year_id
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


def load_era_definitions():
    """
    Return era definitions for annotating charts.
    These eras are widely recognized in baseball history.
    """
    return pd.DataFrame([
        {"era": "Dead Ball Era", "start": 1901, "end": 1919, "description": "Low scoring, pitcher-dominated"},
        {"era": "Live Ball Era", "start": 1920, "end": 1941, "description": "Babe Ruth transforms the game"},
        {"era": "Integration Era", "start": 1947, "end": 1968, "description": "Jackie Robinson to Year of the Pitcher"},
        {"era": "Expansion Era", "start": 1969, "end": 1992, "description": "New teams, new strategies"},
        {"era": "Steroid Era", "start": 1993, "end": 2005, "description": "Record home runs, PED controversy"},
        {"era": "Modern Era", "start": 2006, "end": 2024, "description": "Analytics revolution, three true outcomes"},
    ])


def load_legendary_seasons():
    """
    Load the greatest individual seasons for comparison.
    Bill James pioneered systematic player ranking.
    """
    conn = get_connection()
    query = """
        WITH player_seasons AS (
            SELECT
                b.year_id,
                b.player_id,
                p.name_first || ' ' || p.name_last as player_name,
                b.team_id,
                SUM(b.ab) as ab,
                SUM(b.hits) as h,
                SUM(b.doubles) as "2b",
                SUM(b.triples) as "3b",
                SUM(b.home_runs) as hr,
                SUM(b.rbi) as rbi,
                SUM(b.runs) as r,
                SUM(b.walks) as bb,
                SUM(b.strikeouts) as so,
                -- Calculate basic Runs Created
                SUM(b.hits + b.walks) as on_base_events,
                SUM(b.hits + b.doubles + 2*b.triples + 3*b.home_runs) as total_bases
            FROM lahman.batting b
            JOIN lahman.people p ON b.player_id = p.player_id
            WHERE b.year_id >= 1901
            GROUP BY b.year_id, b.player_id, p.name_first, p.name_last, b.team_id
            HAVING SUM(b.ab) >= 400
        )
        SELECT *,
               CAST(h AS FLOAT) / NULLIF(ab, 0) as avg,
               CAST(on_base_events AS FLOAT) / NULLIF(ab + bb, 0) as obp_approx,
               CAST(total_bases AS FLOAT) / NULLIF(ab, 0) as slg,
               on_base_events * total_bases / NULLIF(ab + bb, 0) as runs_created
        FROM player_seasons
        ORDER BY runs_created DESC
        LIMIT 100
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


def load_pythagorean_outliers():
    """
    Find teams that most over/underperformed their Pythagorean expectation.
    These are the "lucky" and "unlucky" teams.
    """
    conn = get_connection()
    query = """
        SELECT year_id, team_id, name,
               wins, losses,
               runs as runs_scored, runs_allowed,
               CAST(wins AS FLOAT) / NULLIF(wins + losses, 0) as actual_win_pct,
               POWER(runs, 2.0) / NULLIF(POWER(runs, 2.0) + POWER(runs_allowed, 2.0), 0) as expected_win_pct
        FROM lahman.teams
        WHERE year_id >= 1901
          AND runs IS NOT NULL
          AND runs_allowed IS NOT NULL
          AND wins + losses > 100
        ORDER BY year_id, team_id
    """
    df = pd.read_sql(query, conn)
    conn.close()

    df['expected_wins'] = df['expected_win_pct'] * (df['wins'] + df['losses'])
    df['pythagorean_diff'] = df['wins'] - df['expected_wins']

    # Get top overperformers and underperformers
    overperformers = df.nlargest(20, 'pythagorean_diff')
    underperformers = df.nsmallest(20, 'pythagorean_diff')

    return pd.concat([overperformers, underperformers])
