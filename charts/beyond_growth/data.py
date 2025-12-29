"""
Beyond Growth Data Loaders

Load data for charts supporting the degrowth/post-growth essay.
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


def load_emissions_by_income_group(year: int = 2020):
    """
    Load GHG emissions per capita by World Bank income group.

    Shows carbon inequality - rich countries emit far more per capita.
    """
    import pandas as pd

    conn = get_db_connection()
    query = """
        SELECT e.entity_name, id.value
        FROM income_data id
        JOIN entities e ON id.entity_code = e.entity_code
        WHERE id.indicator_code = 'EN.GHG.ALL.PC.CE.AR5'
          AND id.year = %s
          AND id.value IS NOT NULL
        ORDER BY id.value DESC
    """
    df = pd.read_sql(query, conn, params=(year,))
    conn.close()
    return df


def load_top10_income_share_timeseries(countries: list[str], start_year: int = 1980, end_year: int = 2022):
    """
    Load income share held by top 10% over time.

    Shows rising inequality within countries.
    """
    import pandas as pd

    conn = get_db_connection()
    placeholders = ','.join(['%s'] * len(countries))
    query = f"""
        SELECT e.entity_name as country, cd.year, cd.value
        FROM country_data cd
        JOIN entities e ON cd.entity_code = e.entity_code
        WHERE cd.indicator_code = 'SI.DST.10TH.10'
          AND cd.year BETWEEN %s AND %s
          AND cd.entity_code IN ({placeholders})
          AND cd.value IS NOT NULL
        ORDER BY cd.year, e.entity_name
    """
    df = pd.read_sql(query, conn, params=[start_year, end_year] + countries)
    conn.close()
    return df


def load_adjusted_savings_comparison(year: int = 2020):
    """
    Load adjusted net savings vs gross savings by income group.

    Shows how much "wealth creation" is actually resource depletion.
    """
    import pandas as pd

    conn = get_db_connection()

    # Get both gross savings and adjusted net savings
    query = """
        SELECT
            e.entity_name,
            gross.value as gross_savings,
            adj.value as adjusted_savings
        FROM income_data gross
        JOIN income_data adj ON gross.entity_code = adj.entity_code AND gross.year = adj.year
        JOIN entities e ON gross.entity_code = e.entity_code
        WHERE gross.indicator_code = 'NY.ADJ.ICTR.GN.ZS'
          AND adj.indicator_code = 'NY.ADJ.SVNG.GN.ZS'
          AND gross.year = %s
          AND gross.value IS NOT NULL
          AND adj.value IS NOT NULL
        ORDER BY e.entity_name
    """
    df = pd.read_sql(query, conn, params=(year,))
    conn.close()

    # Reshape for grouped bar chart
    result = []
    for _, row in df.iterrows():
        result.append({
            'income_group': row['entity_name'],
            'savings_type': 'Gross Savings',
            'value': row['gross_savings']
        })
        result.append({
            'income_group': row['entity_name'],
            'savings_type': 'Adjusted Net Savings',
            'value': row['adjusted_savings']
        })

    return pd.DataFrame(result)


def load_resource_depletion_by_income_group(year: int = 2020):
    """
    Load natural resources depletion as % of GNI by income group.

    Shows extraction patterns - poor countries depleting more of their wealth.
    """
    import pandas as pd

    conn = get_db_connection()
    query = """
        SELECT e.entity_name, id.value
        FROM income_data id
        JOIN entities e ON id.entity_code = e.entity_code
        WHERE id.indicator_code = 'NY.ADJ.DRES.GN.ZS'
          AND id.year = %s
          AND id.value IS NOT NULL
        ORDER BY id.value DESC
    """
    df = pd.read_sql(query, conn, params=(year,))
    conn.close()
    return df


def load_gini_by_region(year: int = 2019):
    """
    Load Gini coefficients by region.

    Shows inequality varies dramatically by region.
    """
    import pandas as pd

    conn = get_db_connection()
    # Use country averages grouped by region concept
    query = """
        SELECT e.entity_name, rd.value
        FROM region_other_data rd
        JOIN entities e ON rd.entity_code = e.entity_code
        WHERE rd.indicator_code = 'SI.POV.GINI'
          AND rd.year = %s
          AND rd.value IS NOT NULL
        ORDER BY rd.value DESC
    """
    df = pd.read_sql(query, conn, params=(year,))
    conn.close()
    return df


def load_life_expectancy_vs_gdp_all(year: int = 2022):
    """
    Load life expectancy vs GDP per capita - all countries.

    Shows diminishing returns of GDP on wellbeing.
    """
    import pandas as pd

    conn = get_db_connection()
    query = """
        SELECT
            e.entity_name as country,
            gdp.value as gdp_per_capita,
            life.value as life_expectancy
        FROM country_data gdp
        JOIN country_data life ON gdp.entity_code = life.entity_code AND gdp.year = life.year
        JOIN entities e ON gdp.entity_code = e.entity_code
        WHERE gdp.indicator_code = 'NY.GDP.PCAP.CD'
          AND life.indicator_code = 'SP.DYN.LE00.IN'
          AND gdp.year = %s
          AND gdp.value IS NOT NULL
          AND life.value IS NOT NULL
        ORDER BY gdp.value DESC
    """
    df = pd.read_sql(query, conn, params=(year,))
    conn.close()
    return df


def load_latin_america_gini_timeseries(start_year: int = 2000, end_year: int = 2022):
    """
    Load Gini coefficient for Latin American countries over time.

    Shows Buen Vivir region's inequality trends.
    """
    import pandas as pd

    countries = ['BOL', 'ECU', 'BRA', 'ARG', 'CHL', 'COL', 'PER', 'MEX']

    conn = get_db_connection()
    placeholders = ','.join(['%s'] * len(countries))
    query = f"""
        SELECT e.entity_name as country, cd.year, cd.value
        FROM country_data cd
        JOIN entities e ON cd.entity_code = e.entity_code
        WHERE cd.indicator_code = 'SI.POV.GINI'
          AND cd.year BETWEEN %s AND %s
          AND cd.entity_code IN ({placeholders})
          AND cd.value IS NOT NULL
        ORDER BY cd.year, e.entity_name
    """
    df = pd.read_sql(query, conn, params=[start_year, end_year] + countries)
    conn.close()
    return df


def load_wellbeing_vs_footprint(year: int = 2020):
    """
    Load life expectancy vs GHG emissions per capita.

    Shows efficiency of achieving wellbeing vs environmental cost.
    """
    import pandas as pd

    conn = get_db_connection()
    query = """
        SELECT
            e.entity_name as country,
            ghg.value as emissions_per_capita,
            life.value as life_expectancy
        FROM country_data ghg
        JOIN country_data life ON ghg.entity_code = life.entity_code AND ghg.year = life.year
        JOIN entities e ON ghg.entity_code = e.entity_code
        WHERE ghg.indicator_code = 'EN.GHG.ALL.PC.CE.AR5'
          AND life.indicator_code = 'SP.DYN.LE00.IN'
          AND ghg.year = %s
          AND ghg.value IS NOT NULL
          AND life.value IS NOT NULL
        ORDER BY ghg.value DESC
    """
    df = pd.read_sql(query, conn, params=(year,))
    conn.close()
    return df


def load_adjusted_savings_timeseries(countries: list[str], start_year: int = 1990, end_year: int = 2022):
    """
    Load adjusted net savings over time for selected countries.

    Shows who's actually building wealth vs depleting it.
    """
    import pandas as pd

    conn = get_db_connection()
    placeholders = ','.join(['%s'] * len(countries))
    query = f"""
        SELECT e.entity_name as country, cd.year, cd.value
        FROM country_data cd
        JOIN entities e ON cd.entity_code = e.entity_code
        WHERE cd.indicator_code = 'NY.ADJ.SVNG.GN.ZS'
          AND cd.year BETWEEN %s AND %s
          AND cd.entity_code IN ({placeholders})
          AND cd.value IS NOT NULL
        ORDER BY cd.year, e.entity_name
    """
    df = pd.read_sql(query, conn, params=[start_year, end_year] + countries)
    conn.close()
    return df


def load_co2_damage_by_income_group(year: int = 2020):
    """
    Load CO2 damage as % of GNI by income group.

    Shows climate damage burden relative to income.
    """
    import pandas as pd

    conn = get_db_connection()
    query = """
        SELECT e.entity_name, id.value
        FROM income_data id
        JOIN entities e ON id.entity_code = e.entity_code
        WHERE id.indicator_code = 'NY.ADJ.DCO2.GN.ZS'
          AND id.year = %s
          AND id.value IS NOT NULL
        ORDER BY id.value DESC
    """
    df = pd.read_sql(query, conn, params=(year,))
    conn.close()
    return df


def load_world_gdp_growth_long_term():
    """
    Load world GDP from 1960 to show exponential growth pattern.
    """
    import pandas as pd

    conn = get_db_connection()
    query = """
        SELECT year, value
        FROM world_data
        WHERE indicator_code = 'NY.GDP.MKTP.CD'
          AND year BETWEEN 1960 AND 2023
        ORDER BY year
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


def load_bottom50_vs_top10_emissions():
    """
    Load data showing emissions disparity between richest and poorest.

    Returns synthetic data based on Oxfam research showing:
    - Richest 10% responsible for ~48% of emissions
    - Bottom 50% responsible for ~12% of emissions
    """
    import pandas as pd

    # Based on Oxfam "Confronting Carbon Inequality" report
    data = [
        {'group': 'Richest 1%', 'share_of_emissions': 17, 'share_of_population': 1},
        {'group': 'Richest 10%', 'share_of_emissions': 48, 'share_of_population': 10},
        {'group': 'Middle 40%', 'share_of_emissions': 40, 'share_of_population': 40},
        {'group': 'Bottom 50%', 'share_of_emissions': 12, 'share_of_population': 50},
    ]
    return pd.DataFrame(data)


def load_adjusted_net_savings_by_income_group(year: int = 2020):
    """
    Load adjusted net savings as % of GNI by income group.

    Shows genuine wealth creation - what's left after accounting for
    resource depletion, pollution damage, and depreciation.
    """
    import pandas as pd

    conn = get_db_connection()
    query = """
        SELECT e.entity_name, id.value
        FROM income_data id
        JOIN entities e ON id.entity_code = e.entity_code
        WHERE id.indicator_code = 'NY.ADJ.SVNG.GN.ZS'
          AND id.year = %s
          AND id.value IS NOT NULL
        ORDER BY id.value DESC
    """
    df = pd.read_sql(query, conn, params=(year,))
    conn.close()
    return df


def load_gdp_per_capita_vs_adjusted_per_capita(year: int = 2020):
    """
    Load comparison of GDP per capita vs Adjusted Net National Income per capita.

    Shows the gap between headline wealth and sustainable wealth.
    """
    import pandas as pd

    conn = get_db_connection()

    # Get countries with both metrics
    query = """
        SELECT
            e.entity_name as country,
            gdp.value as gdp_per_capita,
            adj.value as adjusted_per_capita
        FROM country_data gdp
        JOIN country_data adj ON gdp.entity_code = adj.entity_code AND gdp.year = adj.year
        JOIN entities e ON gdp.entity_code = e.entity_code
        WHERE gdp.indicator_code = 'NY.GDP.PCAP.CD'
          AND adj.indicator_code = 'NY.ADJ.NNTY.PC.CD'
          AND gdp.year = %s
          AND gdp.value IS NOT NULL
          AND adj.value IS NOT NULL
          AND gdp.value > 10000
        ORDER BY gdp.value DESC
        LIMIT 20
    """
    df = pd.read_sql(query, conn, params=(year,))
    conn.close()
    return df
