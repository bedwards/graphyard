"""
Shared Database Infrastructure

Provides connection management and base data loading patterns
for all data sources (WDI, Lahman, etc.).
"""

import os
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Optional

import pandas as pd
import psycopg2
from psycopg2.extensions import connection as PgConnection


@dataclass
class DatabaseConfig:
    """Database connection configuration."""
    host: str = "localhost"
    port: int = 5432
    database: str = "graphyard"
    user: str = "postgres"
    password: str = "postgres"

    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        """Create config from environment variables with defaults."""
        return cls(
            host=os.getenv("GRAPHYARD_DB_HOST", "localhost"),
            port=int(os.getenv("GRAPHYARD_DB_PORT", "5432")),
            database=os.getenv("GRAPHYARD_DB_NAME", "graphyard"),
            user=os.getenv("GRAPHYARD_DB_USER", "postgres"),
            password=os.getenv("GRAPHYARD_DB_PASSWORD", "postgres"),
        )


# Global default config
_default_config: Optional[DatabaseConfig] = None


def get_default_config() -> DatabaseConfig:
    """Get or create default database configuration."""
    global _default_config
    if _default_config is None:
        _default_config = DatabaseConfig.from_env()
    return _default_config


def get_connection(config: Optional[DatabaseConfig] = None) -> PgConnection:
    """Get a database connection."""
    cfg = config or get_default_config()
    return psycopg2.connect(
        host=cfg.host,
        port=cfg.port,
        database=cfg.database,
        user=cfg.user,
        password=cfg.password,
    )


@contextmanager
def managed_connection(config: Optional[DatabaseConfig] = None):
    """Context manager for database connections."""
    conn = get_connection(config)
    try:
        yield conn
    finally:
        conn.close()


class BaseDataLoader:
    """
    Base class for domain-specific data loaders.

    Provides common patterns for querying data from PostgreSQL
    and returning pandas DataFrames.
    """

    # Subclasses should set this to their schema name
    schema: str = "public"

    def __init__(self, config: Optional[DatabaseConfig] = None):
        self.config = config

    def _get_connection(self) -> PgConnection:
        """Get a database connection."""
        return get_connection(self.config)

    def _query(self, sql: str, params: tuple = ()) -> pd.DataFrame:
        """Execute a query and return results as DataFrame."""
        with managed_connection(self.config) as conn:
            return pd.read_sql(sql, conn, params=params)

    def _query_single_value(self, sql: str, params: tuple = ()):
        """Execute a query and return a single value."""
        with managed_connection(self.config) as conn:
            cur = conn.cursor()
            cur.execute(sql, params)
            result = cur.fetchone()
            return result[0] if result else None

    def _execute(self, sql: str, params: tuple = ()) -> None:
        """Execute a statement (no return value)."""
        with managed_connection(self.config) as conn:
            cur = conn.cursor()
            cur.execute(sql, params)
            conn.commit()

    def _table(self, name: str) -> str:
        """Get fully qualified table name with schema."""
        return f"{self.schema}.{name}"

    # Common query patterns that subclasses can use

    def load_timeseries(
        self,
        table: str,
        indicator_code: str,
        entity_code: Optional[str] = None,
        start_year: int = 1960,
        end_year: int = 2024,
    ) -> pd.DataFrame:
        """Load time series data for an indicator."""
        if entity_code:
            sql = f"""
                SELECT year, value
                FROM {self._table(table)}
                WHERE indicator_code = %s
                  AND entity_code = %s
                  AND year BETWEEN %s AND %s
                ORDER BY year
            """
            return self._query(sql, (indicator_code, entity_code, start_year, end_year))
        else:
            sql = f"""
                SELECT year, value
                FROM {self._table(table)}
                WHERE indicator_code = %s
                  AND year BETWEEN %s AND %s
                ORDER BY year
            """
            return self._query(sql, (indicator_code, start_year, end_year))

    def load_cross_section(
        self,
        table: str,
        indicator_code: str,
        year: int,
        entity_table: str = "entities",
    ) -> pd.DataFrame:
        """Load cross-sectional data for a single year."""
        sql = f"""
            SELECT e.entity_name, d.value
            FROM {self._table(table)} d
            JOIN {self._table(entity_table)} e ON d.entity_code = e.entity_code
            WHERE d.indicator_code = %s
              AND d.year = %s
              AND d.value IS NOT NULL
            ORDER BY d.value DESC
        """
        return self._query(sql, (indicator_code, year))

    def load_comparison(
        self,
        table: str,
        indicator_code: str,
        entity_codes: list[str],
        start_year: int = 1960,
        end_year: int = 2024,
        entity_table: str = "entities",
    ) -> pd.DataFrame:
        """Load comparison data for multiple entities over time."""
        placeholders = ",".join(["%s"] * len(entity_codes))
        sql = f"""
            SELECT e.entity_name as entity, d.year, d.value
            FROM {self._table(table)} d
            JOIN {self._table(entity_table)} e ON d.entity_code = e.entity_code
            WHERE d.indicator_code = %s
              AND d.year BETWEEN %s AND %s
              AND d.entity_code IN ({placeholders})
            ORDER BY d.year, e.entity_name
        """
        return self._query(sql, (indicator_code, start_year, end_year, *entity_codes))
