"""
Data loaders for the Marx retrospective article.

Loads economic indicators that illustrate Marx's key theoretical claims:
- Concentration of capital (wealth inequality, income shares)
- Falling rate of profit and financialization
- Reserve army of labor (unemployment)
- Periodic crises (GDP growth volatility)
- Structural transformation (manufacturing to services)
"""

import pandas as pd
import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "graphyard",
    "user": "postgres",
    "password": "postgres",
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def load_top10_income_share(countries: list[str] = None, start_year: int = 1980, end_year: int = 2023):
    """
    Load income share held by top 10% over time.
    Shows concentration of income - a key Marxist concern.
    """
    if countries is None:
        countries = ["USA", "GBR", "DEU", "FRA", "CHN", "IND"]

    conn = get_connection()
    placeholders = ",".join(["%s"] * len(countries))
    query = f"""
        SELECT cd.entity_code, e.entity_name as short_name, cd.year, cd.value
        FROM country_data cd
        JOIN entities e ON cd.entity_code = e.entity_code
        WHERE cd.indicator_code = 'SI.DST.10TH.10'
          AND cd.entity_code IN ({placeholders})
          AND cd.year BETWEEN %s AND %s
          AND cd.value IS NOT NULL
        ORDER BY cd.entity_code, cd.year
    """
    df = pd.read_sql(query, conn, params=countries + [start_year, end_year])
    conn.close()
    return df


def load_gini_index(countries: list[str] = None, start_year: int = 1980, end_year: int = 2023):
    """
    Load Gini coefficient over time.
    Higher Gini = more inequality. Marx predicted increasing concentration.
    """
    if countries is None:
        countries = ["USA", "GBR", "DEU", "CHN", "BRA", "ZAF"]

    conn = get_connection()
    placeholders = ",".join(["%s"] * len(countries))
    query = f"""
        SELECT cd.entity_code, e.entity_name as short_name, cd.year, cd.value
        FROM country_data cd
        JOIN entities e ON cd.entity_code = e.entity_code
        WHERE cd.indicator_code = 'SI.POV.GINI'
          AND cd.entity_code IN ({placeholders})
          AND cd.year BETWEEN %s AND %s
          AND cd.value IS NOT NULL
        ORDER BY cd.entity_code, cd.year
    """
    df = pd.read_sql(query, conn, params=countries + [start_year, end_year])
    conn.close()
    return df


def load_financial_sector_growth(countries: list[str] = None, start_year: int = 1960, end_year: int = 2023):
    """
    Load domestic credit by financial sector as % of GDP.
    Shows financialization - capital moving from production to speculation.
    """
    if countries is None:
        countries = ["USA", "GBR", "JPN", "CHN"]

    conn = get_connection()
    placeholders = ",".join(["%s"] * len(countries))
    query = f"""
        SELECT cd.entity_code, e.entity_name as short_name, cd.year, cd.value
        FROM country_data cd
        JOIN entities e ON cd.entity_code = e.entity_code
        WHERE cd.indicator_code = 'FS.AST.DOMS.GD.ZS'
          AND cd.entity_code IN ({placeholders})
          AND cd.year BETWEEN %s AND %s
          AND cd.value IS NOT NULL
        ORDER BY cd.entity_code, cd.year
    """
    df = pd.read_sql(query, conn, params=countries + [start_year, end_year])
    conn.close()
    return df


def load_manufacturing_share(countries: list[str] = None, start_year: int = 1960, end_year: int = 2023):
    """
    Load manufacturing value added as % of GDP.
    Shows deindustrialization in advanced economies.
    """
    if countries is None:
        countries = ["USA", "GBR", "DEU", "CHN", "IND"]

    conn = get_connection()
    placeholders = ",".join(["%s"] * len(countries))
    query = f"""
        SELECT cd.entity_code, e.entity_name as short_name, cd.year, cd.value
        FROM country_data cd
        JOIN entities e ON cd.entity_code = e.entity_code
        WHERE cd.indicator_code = 'NV.IND.MANF.ZS'
          AND cd.entity_code IN ({placeholders})
          AND cd.year BETWEEN %s AND %s
          AND cd.value IS NOT NULL
        ORDER BY cd.entity_code, cd.year
    """
    df = pd.read_sql(query, conn, params=countries + [start_year, end_year])
    conn.close()
    return df


def load_services_share(countries: list[str] = None, start_year: int = 1960, end_year: int = 2023):
    """
    Load services value added as % of GDP.
    Shows structural shift from industry to services.
    """
    if countries is None:
        countries = ["USA", "GBR", "DEU", "CHN", "IND"]

    conn = get_connection()
    placeholders = ",".join(["%s"] * len(countries))
    query = f"""
        SELECT cd.entity_code, e.entity_name as short_name, cd.year, cd.value
        FROM country_data cd
        JOIN entities e ON cd.entity_code = e.entity_code
        WHERE cd.indicator_code = 'NV.SRV.TOTL.ZS'
          AND cd.entity_code IN ({placeholders})
          AND cd.year BETWEEN %s AND %s
          AND cd.value IS NOT NULL
        ORDER BY cd.entity_code, cd.year
    """
    df = pd.read_sql(query, conn, params=countries + [start_year, end_year])
    conn.close()
    return df


def load_unemployment_rate(countries: list[str] = None, start_year: int = 1991, end_year: int = 2023):
    """
    Load unemployment rate over time.
    The "reserve army of labor" - Marx's term for the unemployed.
    """
    if countries is None:
        countries = ["USA", "GBR", "DEU", "FRA", "ESP", "GRC"]

    conn = get_connection()
    placeholders = ",".join(["%s"] * len(countries))
    query = f"""
        SELECT cd.entity_code, e.entity_name as short_name, cd.year, cd.value
        FROM country_data cd
        JOIN entities e ON cd.entity_code = e.entity_code
        WHERE cd.indicator_code = 'SL.UEM.TOTL.ZS'
          AND cd.entity_code IN ({placeholders})
          AND cd.year BETWEEN %s AND %s
          AND cd.value IS NOT NULL
        ORDER BY cd.entity_code, cd.year
    """
    df = pd.read_sql(query, conn, params=countries + [start_year, end_year])
    conn.close()
    return df


def load_world_gdp_growth(start_year: int = 1961, end_year: int = 2023):
    """
    Load world GDP growth rate to show crisis cycles.
    Periodic crises are inherent to capitalism per Marx.
    """
    conn = get_connection()
    query = """
        SELECT year, value as growth_rate
        FROM world_data
        WHERE indicator_code = 'NY.GDP.MKTP.KD.ZG'
          AND year BETWEEN %s AND %s
          AND value IS NOT NULL
        ORDER BY year
    """
    df = pd.read_sql(query, conn, params=(start_year, end_year))
    conn.close()
    return df


def load_capital_formation(countries: list[str] = None, start_year: int = 1960, end_year: int = 2023):
    """
    Load gross fixed capital formation as % of GDP.
    Investment in physical capital - the reproduction of capital.
    """
    if countries is None:
        countries = ["USA", "CHN", "DEU", "JPN", "IND"]

    conn = get_connection()
    placeholders = ",".join(["%s"] * len(countries))
    query = f"""
        SELECT cd.entity_code, e.entity_name as short_name, cd.year, cd.value
        FROM country_data cd
        JOIN entities e ON cd.entity_code = e.entity_code
        WHERE cd.indicator_code = 'NE.GDI.FTOT.ZS'
          AND cd.entity_code IN ({placeholders})
          AND cd.year BETWEEN %s AND %s
          AND cd.value IS NOT NULL
        ORDER BY cd.entity_code, cd.year
    """
    df = pd.read_sql(query, conn, params=countries + [start_year, end_year])
    conn.close()
    return df


def load_gdp_per_capita_growth(countries: list[str] = None, start_year: int = 1960, end_year: int = 2023):
    """
    Load GDP per capita in constant 2015 US$.
    Shows material progress - but who benefits?
    """
    if countries is None:
        countries = ["USA", "CHN", "IND", "BRA", "NGA", "ETH"]

    conn = get_connection()
    placeholders = ",".join(["%s"] * len(countries))
    query = f"""
        SELECT cd.entity_code, e.entity_name as short_name, cd.year, cd.value
        FROM country_data cd
        JOIN entities e ON cd.entity_code = e.entity_code
        WHERE cd.indicator_code = 'NY.GDP.PCAP.KD'
          AND cd.entity_code IN ({placeholders})
          AND cd.year BETWEEN %s AND %s
          AND cd.value IS NOT NULL
        ORDER BY cd.entity_code, cd.year
    """
    df = pd.read_sql(query, conn, params=countries + [start_year, end_year])
    conn.close()
    return df


def load_us_sector_transformation():
    """
    Load US manufacturing vs services over time.
    Shows the structural transformation Marx did not anticipate.
    """
    conn = get_connection()
    query = """
        SELECT cd.year,
               cd.indicator_code,
               CASE
                   WHEN cd.indicator_code = 'NV.IND.MANF.ZS' THEN 'Manufacturing'
                   WHEN cd.indicator_code = 'NV.SRV.TOTL.ZS' THEN 'Services'
               END as sector,
               cd.value
        FROM country_data cd
        WHERE cd.entity_code = 'USA'
          AND cd.indicator_code IN ('NV.IND.MANF.ZS', 'NV.SRV.TOTL.ZS')
          AND cd.year BETWEEN 1960 AND 2023
          AND cd.value IS NOT NULL
        ORDER BY cd.year, sector
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


def load_us_inequality_timeline():
    """
    Load US income share top 10% over time.
    Shows the U-curve of inequality in America.
    """
    conn = get_connection()
    query = """
        SELECT year, value as top_10_share
        FROM country_data
        WHERE entity_code = 'USA'
          AND indicator_code = 'SI.DST.10TH.10'
          AND value IS NOT NULL
        ORDER BY year
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


def load_crisis_markers():
    """
    Return data for marking major economic crises.
    """
    return pd.DataFrame([
        {"year": 1929, "event": "Great Depression", "description": "Stock market crash, bank failures"},
        {"year": 1973, "event": "Oil Crisis", "description": "OPEC embargo, stagflation"},
        {"year": 2008, "event": "Financial Crisis", "description": "Subprime mortgage collapse"},
        {"year": 2020, "event": "COVID-19", "description": "Pandemic economic shutdown"},
    ])


def load_global_inequality_comparison(year: int = 2019):
    """
    Load Gini coefficients for comparison across countries.
    Shows variation in inequality across different political economies.
    """
    conn = get_connection()
    query = """
        SELECT cd.entity_code, e.entity_name as short_name, cd.value as gini
        FROM country_data cd
        JOIN entities e ON cd.entity_code = e.entity_code
        WHERE cd.indicator_code = 'SI.POV.GINI'
          AND cd.year = %s
          AND cd.value IS NOT NULL
          AND e.entity_type = 'country'
        ORDER BY cd.value DESC
        LIMIT 30
    """
    df = pd.read_sql(query, conn, params=(year,))
    conn.close()
    return df


def load_us_financialization():
    """
    Load US financial sector credit as % of GDP over time.
    Shows the rise of finance capital.
    """
    conn = get_connection()
    query = """
        SELECT year, value as financial_sector_pct
        FROM country_data
        WHERE entity_code = 'USA'
          AND indicator_code = 'FS.AST.DOMS.GD.ZS'
          AND value IS NOT NULL
        ORDER BY year
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df
