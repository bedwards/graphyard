"""
Baseball Data Loaders

Load baseball statistics from the Lahman database for chart generation.
Uses shared database infrastructure for consistent patterns across domains.
"""

import sys
from pathlib import Path

import pandas as pd

# Add project root for shared imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from shared.database import BaseDataLoader, DatabaseConfig


class LahmanLoader(BaseDataLoader):
    """Data loader for Lahman baseball database."""

    schema = "lahman"

    # =========================================================================
    # CAREER LEADERS
    # =========================================================================

    def career_home_run_leaders(self, limit: int = 25) -> pd.DataFrame:
        """Top career home run hitters."""
        sql = f"""
            SELECT
                p.name_first || ' ' || p.name_last as player,
                SUM(b.home_runs) as home_runs,
                COUNT(DISTINCT b.year_id) as seasons,
                MIN(b.year_id) as first_year,
                MAX(b.year_id) as last_year
            FROM {self._table('batting')} b
            JOIN {self._table('people')} p ON b.player_id = p.player_id
            GROUP BY p.player_id, p.name_first, p.name_last
            HAVING SUM(b.home_runs) > 0
            ORDER BY home_runs DESC
            LIMIT %s
        """
        return self._query(sql, (limit,))

    def career_batting_average_leaders(self, min_at_bats: int = 3000, limit: int = 25) -> pd.DataFrame:
        """Top career batting average (minimum AB requirement)."""
        sql = f"""
            SELECT
                p.name_first || ' ' || p.name_last as player,
                SUM(b.hits)::float / NULLIF(SUM(b.at_bats), 0) as batting_avg,
                SUM(b.at_bats) as at_bats,
                SUM(b.hits) as hits,
                COUNT(DISTINCT b.year_id) as seasons
            FROM {self._table('batting')} b
            JOIN {self._table('people')} p ON b.player_id = p.player_id
            GROUP BY p.player_id, p.name_first, p.name_last
            HAVING SUM(b.at_bats) >= %s
            ORDER BY batting_avg DESC
            LIMIT %s
        """
        return self._query(sql, (min_at_bats, limit))

    def career_wins_leaders(self, limit: int = 25) -> pd.DataFrame:
        """Top career wins by pitchers."""
        sql = f"""
            SELECT
                p.name_first || ' ' || p.name_last as player,
                SUM(pt.wins) as wins,
                SUM(pt.losses) as losses,
                SUM(pt.wins)::float / NULLIF(SUM(pt.wins) + SUM(pt.losses), 0) as win_pct,
                COUNT(DISTINCT pt.year_id) as seasons
            FROM {self._table('pitching')} pt
            JOIN {self._table('people')} p ON pt.player_id = p.player_id
            GROUP BY p.player_id, p.name_first, p.name_last
            HAVING SUM(pt.wins) > 0
            ORDER BY wins DESC
            LIMIT %s
        """
        return self._query(sql, (limit,))

    def career_strikeout_leaders(self, limit: int = 25) -> pd.DataFrame:
        """Top career strikeouts by pitchers."""
        sql = f"""
            SELECT
                p.name_first || ' ' || p.name_last as player,
                SUM(pt.strikeouts) as strikeouts,
                SUM(pt.outs_pitched)::float / 3 as innings_pitched,
                SUM(pt.strikeouts)::float / NULLIF(SUM(pt.outs_pitched)::float / 3, 0) * 9 as k_per_9,
                COUNT(DISTINCT pt.year_id) as seasons
            FROM {self._table('pitching')} pt
            JOIN {self._table('people')} p ON pt.player_id = p.player_id
            GROUP BY p.player_id, p.name_first, p.name_last
            HAVING SUM(pt.strikeouts) > 0
            ORDER BY strikeouts DESC
            LIMIT %s
        """
        return self._query(sql, (limit,))

    # =========================================================================
    # ERA ANALYSIS (Dead Ball, Live Ball, Integration, Expansion, Steroid, Modern)
    # =========================================================================

    def league_batting_by_era(self) -> pd.DataFrame:
        """League-wide batting average by baseball era."""
        sql = f"""
            WITH era_data AS (
                SELECT
                    year_id,
                    SUM(hits)::float / NULLIF(SUM(at_bats), 0) as batting_avg,
                    SUM(home_runs)::float / NULLIF(SUM(at_bats), 0) * 100 as hr_pct,
                    SUM(strikeouts)::float / NULLIF(SUM(at_bats), 0) * 100 as k_pct,
                    CASE
                        WHEN year_id < 1920 THEN 'Dead Ball (1901-1919)'
                        WHEN year_id < 1942 THEN 'Live Ball (1920-1941)'
                        WHEN year_id < 1946 THEN 'WWII (1942-1945)'
                        WHEN year_id < 1961 THEN 'Integration (1946-1960)'
                        WHEN year_id < 1969 THEN 'Expansion I (1961-1968)'
                        WHEN year_id < 1993 THEN 'Free Agency (1969-1992)'
                        WHEN year_id < 2006 THEN 'Steroid Era (1993-2005)'
                        ELSE 'Modern (2006-present)'
                    END as era
                FROM {self._table('batting')}
                WHERE year_id >= 1901
                GROUP BY year_id
            )
            SELECT
                era,
                MIN(year_id) as start_year,
                MAX(year_id) as end_year,
                AVG(batting_avg) as avg_batting_avg,
                AVG(hr_pct) as avg_hr_pct,
                AVG(k_pct) as avg_k_pct
            FROM era_data
            GROUP BY era
            ORDER BY MIN(year_id)
        """
        return self._query(sql)

    def yearly_league_batting(self, start_year: int = 1901, end_year: int = 2023) -> pd.DataFrame:
        """League-wide batting statistics by year."""
        sql = f"""
            SELECT
                year_id as year,
                SUM(hits)::float / NULLIF(SUM(at_bats), 0) as batting_avg,
                SUM(home_runs) as total_hr,
                SUM(home_runs)::float / NULLIF(SUM(at_bats), 0) * 100 as hr_rate,
                SUM(strikeouts)::float / NULLIF(SUM(at_bats), 0) * 100 as k_rate,
                SUM(walks)::float / NULLIF(SUM(at_bats) + SUM(walks), 0) * 100 as bb_rate,
                COUNT(DISTINCT player_id) as total_batters
            FROM {self._table('batting')}
            WHERE year_id BETWEEN %s AND %s
            GROUP BY year_id
            ORDER BY year_id
        """
        return self._query(sql, (start_year, end_year))

    def yearly_league_pitching(self, start_year: int = 1901, end_year: int = 2023) -> pd.DataFrame:
        """League-wide pitching statistics by year."""
        sql = f"""
            SELECT
                year_id as year,
                SUM(earned_runs)::float / NULLIF(SUM(outs_pitched)::float / 3, 0) * 9 as era,
                SUM(strikeouts)::float / NULLIF(SUM(outs_pitched)::float / 3, 0) * 9 as k_per_9,
                SUM(walks)::float / NULLIF(SUM(outs_pitched)::float / 3, 0) * 9 as bb_per_9,
                SUM(home_runs)::float / NULLIF(SUM(outs_pitched)::float / 3, 0) * 9 as hr_per_9,
                SUM(complete_games) as complete_games,
                SUM(shutouts) as shutouts,
                COUNT(DISTINCT player_id) as total_pitchers
            FROM {self._table('pitching')}
            WHERE year_id BETWEEN %s AND %s
            GROUP BY year_id
            ORDER BY year_id
        """
        return self._query(sql, (start_year, end_year))

    # =========================================================================
    # SALARY ANALYSIS
    # =========================================================================

    def salary_growth(self, start_year: int = 1985, end_year: int = 2016) -> pd.DataFrame:
        """Average and median salary by year."""
        sql = f"""
            SELECT
                year_id as year,
                AVG(salary) as avg_salary,
                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY salary) as median_salary,
                MAX(salary) as max_salary,
                MIN(salary) as min_salary,
                COUNT(*) as num_players
            FROM {self._table('salaries')}
            WHERE year_id BETWEEN %s AND %s
              AND salary IS NOT NULL
            GROUP BY year_id
            ORDER BY year_id
        """
        return self._query(sql, (start_year, end_year))

    def top_salaries_by_year(self, year: int = 2016, limit: int = 10) -> pd.DataFrame:
        """Highest paid players in a given year."""
        sql = f"""
            SELECT
                p.name_first || ' ' || p.name_last as player,
                s.team_id,
                s.salary
            FROM {self._table('salaries')} s
            JOIN {self._table('people')} p ON s.player_id = p.player_id
            WHERE s.year_id = %s
            ORDER BY s.salary DESC
            LIMIT %s
        """
        return self._query(sql, (year, limit))

    def salary_vs_performance(self, year: int = 2016, min_at_bats: int = 400) -> pd.DataFrame:
        """Salary vs offensive production (WAR proxy using OPS)."""
        sql = f"""
            SELECT
                p.name_first || ' ' || p.name_last as player,
                s.salary,
                b.at_bats,
                b.hits,
                b.home_runs,
                b.rbi,
                b.walks,
                (b.hits::float + b.walks::float) / NULLIF(b.at_bats + b.walks, 0) as obp,
                (b.hits + b.doubles + 2*b.triples + 3*b.home_runs)::float / NULLIF(b.at_bats, 0) as slg
            FROM {self._table('salaries')} s
            JOIN {self._table('batting')} b
                ON s.player_id = b.player_id AND s.year_id = b.year_id
            JOIN {self._table('people')} p ON s.player_id = p.player_id
            WHERE s.year_id = %s
              AND b.at_bats >= %s
            ORDER BY s.salary DESC
        """
        df = self._query(sql, (year, min_at_bats))
        # Add OPS
        if not df.empty:
            df['ops'] = df['obp'] + df['slg']
        return df

    # =========================================================================
    # TEAM ANALYSIS
    # =========================================================================

    def franchise_wins_all_time(self, limit: int = 30) -> pd.DataFrame:
        """All-time wins by franchise."""
        sql = f"""
            SELECT
                tf.franch_name as franchise,
                SUM(t.wins) as total_wins,
                SUM(t.losses) as total_losses,
                SUM(t.wins)::float / NULLIF(SUM(t.wins) + SUM(t.losses), 0) as win_pct,
                COUNT(*) as seasons,
                SUM(CASE WHEN t.ws_win = 'Y' THEN 1 ELSE 0 END) as championships
            FROM {self._table('teams')} t
            JOIN {self._table('teams_franchises')} tf ON t.franch_id = tf.franch_id
            WHERE tf.active = 'Y'
            GROUP BY tf.franch_id, tf.franch_name
            ORDER BY total_wins DESC
            LIMIT %s
        """
        return self._query(sql, (limit,))

    def dynasty_teams(self, min_wins: int = 100) -> pd.DataFrame:
        """Teams with 100+ win seasons."""
        sql = f"""
            SELECT
                t.year_id as year,
                t.name as team,
                t.wins,
                t.losses,
                t.ws_win as world_series
            FROM {self._table('teams')} t
            WHERE t.wins >= %s
            ORDER BY t.wins DESC, t.year_id
        """
        return self._query(sql, (min_wins,))

    def team_season_history(self, team_id: str, start_year: int = 1901) -> pd.DataFrame:
        """Win totals for a specific team over time."""
        sql = f"""
            SELECT
                year_id as year,
                wins,
                losses,
                wins::float / NULLIF(wins + losses, 0) as win_pct,
                ws_win as world_series,
                lg_win as pennant,
                div_win as division
            FROM {self._table('teams')}
            WHERE team_id = %s OR franch_id = %s
              AND year_id >= %s
            ORDER BY year_id
        """
        return self._query(sql, (team_id, team_id, start_year))

    # =========================================================================
    # HISTORICAL TRENDS
    # =========================================================================

    def home_run_evolution(self) -> pd.DataFrame:
        """Total home runs by year showing power evolution."""
        sql = f"""
            SELECT
                year_id as year,
                SUM(home_runs) as total_hr,
                COUNT(DISTINCT team_id) as num_teams,
                SUM(home_runs)::float / COUNT(DISTINCT team_id) as hr_per_team
            FROM {self._table('batting')}
            WHERE year_id >= 1901
            GROUP BY year_id
            ORDER BY year_id
        """
        return self._query(sql)

    def strikeout_evolution(self) -> pd.DataFrame:
        """Strikeout trends over time (both batting and pitching perspective)."""
        sql = f"""
            SELECT
                year_id as year,
                SUM(strikeouts) as total_k,
                SUM(at_bats) as total_ab,
                SUM(strikeouts)::float / NULLIF(SUM(at_bats), 0) * 100 as k_rate
            FROM {self._table('batting')}
            WHERE year_id >= 1901
            GROUP BY year_id
            ORDER BY year_id
        """
        return self._query(sql)

    def complete_game_decline(self) -> pd.DataFrame:
        """Show the decline of complete games over time."""
        sql = f"""
            SELECT
                year_id as year,
                SUM(complete_games) as complete_games,
                SUM(games_started) as games_started,
                SUM(complete_games)::float / NULLIF(SUM(games_started), 0) * 100 as cg_pct
            FROM {self._table('pitching')}
            WHERE year_id >= 1901
              AND games_started > 0
            GROUP BY year_id
            ORDER BY year_id
        """
        return self._query(sql)

    # =========================================================================
    # PLAYER COMPARISONS
    # =========================================================================

    def player_career(self, player_name: str) -> pd.DataFrame:
        """Get full career batting stats for a player by name."""
        sql = f"""
            SELECT
                b.year_id as year,
                b.team_id,
                b.games,
                b.at_bats,
                b.hits,
                b.doubles,
                b.triples,
                b.home_runs,
                b.rbi,
                b.walks,
                b.strikeouts,
                b.stolen_bases,
                b.hits::float / NULLIF(b.at_bats, 0) as batting_avg
            FROM {self._table('batting')} b
            JOIN {self._table('people')} p ON b.player_id = p.player_id
            WHERE LOWER(p.name_first || ' ' || p.name_last) LIKE LOWER(%s)
            ORDER BY b.year_id
        """
        return self._query(sql, (f'%{player_name}%',))

    def compare_players(self, player_names: list[str]) -> pd.DataFrame:
        """Compare career stats for multiple players."""
        placeholders = ','.join(['%s'] * len(player_names))
        patterns = [f'%{name}%' for name in player_names]

        sql = f"""
            SELECT
                p.name_first || ' ' || p.name_last as player,
                COUNT(DISTINCT b.year_id) as seasons,
                SUM(b.games) as games,
                SUM(b.at_bats) as at_bats,
                SUM(b.hits) as hits,
                SUM(b.home_runs) as home_runs,
                SUM(b.rbi) as rbi,
                SUM(b.walks) as walks,
                SUM(b.stolen_bases) as stolen_bases,
                SUM(b.hits)::float / NULLIF(SUM(b.at_bats), 0) as batting_avg
            FROM {self._table('batting')} b
            JOIN {self._table('people')} p ON b.player_id = p.player_id
            WHERE {' OR '.join(['LOWER(p.name_first || %s || p.name_last) LIKE LOWER(%s)' for _ in player_names])}
            GROUP BY p.player_id, p.name_first, p.name_last
        """
        # Build params: each player needs ' ' and the pattern
        params = []
        for pattern in patterns:
            params.extend([' ', pattern])

        return self._query(sql, tuple(params))

    # =========================================================================
    # RECORD HOLDERS
    # =========================================================================

    def single_season_records(self) -> pd.DataFrame:
        """Notable single-season records."""
        sql = f"""
            WITH hr_record AS (
                SELECT
                    'Home Runs' as category,
                    p.name_first || ' ' || p.name_last as player,
                    b.year_id as year,
                    b.home_runs::text as value
                FROM {self._table('batting')} b
                JOIN {self._table('people')} p ON b.player_id = p.player_id
                ORDER BY b.home_runs DESC
                LIMIT 1
            ),
            hits_record AS (
                SELECT
                    'Hits' as category,
                    p.name_first || ' ' || p.name_last as player,
                    b.year_id as year,
                    b.hits::text as value
                FROM {self._table('batting')} b
                JOIN {self._table('people')} p ON b.player_id = p.player_id
                ORDER BY b.hits DESC
                LIMIT 1
            ),
            sb_record AS (
                SELECT
                    'Stolen Bases' as category,
                    p.name_first || ' ' || p.name_last as player,
                    b.year_id as year,
                    b.stolen_bases::text as value
                FROM {self._table('batting')} b
                JOIN {self._table('people')} p ON b.player_id = p.player_id
                ORDER BY b.stolen_bases DESC NULLS LAST
                LIMIT 1
            ),
            wins_record AS (
                SELECT
                    'Wins (Pitcher)' as category,
                    p.name_first || ' ' || p.name_last as player,
                    pt.year_id as year,
                    pt.wins::text as value
                FROM {self._table('pitching')} pt
                JOIN {self._table('people')} p ON pt.player_id = p.player_id
                ORDER BY pt.wins DESC
                LIMIT 1
            ),
            k_record AS (
                SELECT
                    'Strikeouts (Pitcher)' as category,
                    p.name_first || ' ' || p.name_last as player,
                    pt.year_id as year,
                    pt.strikeouts::text as value
                FROM {self._table('pitching')} pt
                JOIN {self._table('people')} p ON pt.player_id = p.player_id
                ORDER BY pt.strikeouts DESC
                LIMIT 1
            )
            SELECT * FROM hr_record
            UNION ALL SELECT * FROM hits_record
            UNION ALL SELECT * FROM sb_record
            UNION ALL SELECT * FROM wins_record
            UNION ALL SELECT * FROM k_record
        """
        return self._query(sql)

    # =========================================================================
    # MANAGERS
    # =========================================================================

    def manager_career_wins(self, limit: int = 25) -> pd.DataFrame:
        """Top managers by career wins."""
        sql = f"""
            SELECT
                p.name_first || ' ' || p.name_last as manager,
                SUM(m.wins) as wins,
                SUM(m.losses) as losses,
                SUM(m.wins)::float / NULLIF(SUM(m.wins) + SUM(m.losses), 0) as win_pct,
                COUNT(DISTINCT m.year_id) as seasons,
                COUNT(DISTINCT m.team_id) as teams
            FROM {self._table('managers')} m
            JOIN {self._table('people')} p ON m.player_id = p.player_id
            WHERE m.player_id IS NOT NULL
            GROUP BY p.player_id, p.name_first, p.name_last
            ORDER BY wins DESC
            LIMIT %s
        """
        return self._query(sql, (limit,))


# Convenience function for quick access
def get_loader(config: DatabaseConfig = None) -> LahmanLoader:
    """Get a configured Lahman data loader."""
    return LahmanLoader(config)
