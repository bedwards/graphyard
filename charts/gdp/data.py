"""
GDP Data Loaders

Load GDP-related data from the WDI database for chart generation.
"""

import sys
from pathlib import Path

# Add project root to path for database access
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))


def get_db_connection():
    """Get database connection to graphyard."""
    import psycopg2
    return psycopg2.connect(
        host="localhost",
        port=5432,
        database="graphyard",
        user="postgres",
        password="postgres"
    )


def load_world_gdp_trend(start_year: int = 1960, end_year: int = 2024):
    """Load world GDP over time."""
    import pandas as pd

    conn = get_db_connection()
    query = """
        SELECT year, value
        FROM world_data
        WHERE indicator_code = 'NY.GDP.MKTP.CD'
          AND year BETWEEN %s AND %s
        ORDER BY year
    """
    df = pd.read_sql(query, conn, params=(start_year, end_year))
    conn.close()
    return df


def load_country_gdp_comparison(
    countries: list[str],
    year: int = 2023
):
    """Load GDP for multiple countries for a given year."""
    import pandas as pd

    conn = get_db_connection()
    placeholders = ','.join(['%s'] * len(countries))
    query = f"""
        SELECT e.entity_name, cd.value
        FROM country_data cd
        JOIN entities e ON cd.entity_code = e.entity_code
        WHERE cd.indicator_code = 'NY.GDP.MKTP.CD'
          AND cd.year = %s
          AND cd.entity_code IN ({placeholders})
        ORDER BY cd.value DESC
    """
    df = pd.read_sql(query, conn, params=[year] + countries)
    conn.close()
    return df


def load_gdp_growth_rates(entity_code: str = 'WLD', years: int = 20):
    """Load GDP growth rates."""
    import pandas as pd

    conn = get_db_connection()

    # Determine table
    if entity_code == 'WLD':
        query = """
            SELECT year, value
            FROM world_data
            WHERE indicator_code = 'NY.GDP.MKTP.KD.ZG'
            ORDER BY year DESC
            LIMIT %s
        """
        df = pd.read_sql(query, conn, params=(years,))
    else:
        query = """
            SELECT year, value
            FROM country_data
            WHERE indicator_code = 'NY.GDP.MKTP.KD.ZG'
              AND entity_code = %s
            ORDER BY year DESC
            LIMIT %s
        """
        df = pd.read_sql(query, conn, params=(entity_code, years))

    conn.close()
    return df.sort_values('year')


def load_gdp_per_capita_by_income_group(year: int = 2023):
    """Load GDP per capita by income group."""
    import pandas as pd

    conn = get_db_connection()
    query = """
        SELECT e.entity_name, id.value
        FROM income_data id
        JOIN entities e ON id.entity_code = e.entity_code
        WHERE id.indicator_code = 'NY.GDP.PCAP.CD'
          AND id.year = %s
        ORDER BY id.value DESC
    """
    df = pd.read_sql(query, conn, params=(year,))
    conn.close()
    return df


def load_gdp_components(entity_code: str = 'USA', year: int = 2023):
    """
    Load GDP expenditure components.

    Components:
    - NE.CON.PRVT.CD: Household consumption
    - NE.CON.GOVT.CD: Government consumption
    - NE.GDI.TOTL.CD: Gross capital formation (Investment)
    - NE.EXP.GNFS.CD: Exports
    - NE.IMP.GNFS.CD: Imports (negative for net exports)
    """
    import pandas as pd

    conn = get_db_connection()
    query = """
        SELECT i.indicator_name, cd.value
        FROM country_data cd
        JOIN indicators i ON cd.indicator_code = i.indicator_code
        WHERE cd.entity_code = %s
          AND cd.year = %s
          AND cd.indicator_code IN (
              'NE.CON.PRVT.CD',
              'NE.CON.GOVT.CD',
              'NE.GDI.TOTL.CD',
              'NE.EXP.GNFS.CD',
              'NE.IMP.GNFS.CD'
          )
    """
    df = pd.read_sql(query, conn, params=(entity_code, year))
    conn.close()

    # Simplify names
    name_map = {
        'Households and NPISHs Final consumption expenditure (current US$)': 'Consumption (C)',
        'General government final consumption expenditure (current US$)': 'Government (G)',
        'Gross capital formation (current US$)': 'Investment (I)',
        'Exports of goods and services (current US$)': 'Exports',
        'Imports of goods and services (current US$)': 'Imports',
    }
    df['indicator_name'] = df['indicator_name'].map(
        lambda x: name_map.get(x, x)
    )
    return df


def load_regional_gdp(year: int = 2023):
    """Load GDP by World Bank region."""
    import pandas as pd

    conn = get_db_connection()
    query = """
        SELECT e.entity_name, rd.value
        FROM region_geo_data rd
        JOIN entities e ON rd.entity_code = e.entity_code
        WHERE rd.indicator_code = 'NY.GDP.MKTP.CD'
          AND rd.year = %s
          AND e.entity_type = 'region_geo'
        ORDER BY rd.value DESC
    """
    df = pd.read_sql(query, conn, params=(year,))
    conn.close()
    return df


def load_country_gdp_timeseries(
    countries: list[str],
    start_year: int = 1960,
    end_year: int = 2023
):
    """Load GDP time series for multiple countries."""
    import pandas as pd

    conn = get_db_connection()
    placeholders = ','.join(['%s'] * len(countries))
    query = f"""
        SELECT e.entity_name as country, cd.year, cd.value
        FROM country_data cd
        JOIN entities e ON cd.entity_code = e.entity_code
        WHERE cd.indicator_code = 'NY.GDP.MKTP.CD'
          AND cd.year BETWEEN %s AND %s
          AND cd.entity_code IN ({placeholders})
        ORDER BY cd.year, cd.value DESC
    """
    df = pd.read_sql(query, conn, params=[start_year, end_year] + countries)
    conn.close()
    return df
