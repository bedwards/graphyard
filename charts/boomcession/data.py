"""
Boomcession Data Loaders

Load data for charts supporting the boomcession essay - analyzing the disconnect
between GDP growth and consumer sentiment.
"""

import pandas as pd
import numpy as np


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


def load_sentiment_by_president():
    """
    Load average consumer sentiment by presidential administration.

    Chart 1: Bar chart showing sentiment rankings by president.
    """
    conn = get_db_connection()
    query = """
        SELECT
            label,
            party,
            EXTRACT(YEAR FROM term_start)::INTEGER as start_year,
            ROUND(avg_sentiment::numeric, 1) as sentiment
        FROM boomcession.sentiment_by_president
        ORDER BY term_start
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


def load_gdp_sentiment_correlation():
    """
    Calculate rolling 10-year correlation between GDP growth and sentiment.

    Chart 2: Area chart showing correlation collapse over time.
    """
    conn = get_db_connection()

    # Get annual GDP and sentiment data
    query = """
        SELECT
            year,
            AVG(gdp_growth) as gdp_growth,
            AVG(avg_sentiment) as sentiment
        FROM boomcession.gdp_sentiment_quarterly
        WHERE avg_sentiment IS NOT NULL
        GROUP BY year
        ORDER BY year
    """
    df = pd.read_sql(query, conn)
    conn.close()

    # Calculate rolling 10-year correlation
    correlations = []
    for i in range(9, len(df)):
        window = df.iloc[i-9:i+1]
        corr = window['gdp_growth'].corr(window['sentiment'])
        correlations.append({
            'year': int(df.iloc[i]['year']),
            'correlation': corr
        })

    return pd.DataFrame(correlations)


def load_gdp_sentiment_scatter():
    """
    Load GDP growth vs sentiment for scatter plot.

    Chart 3: Scatter showing the "sentiment gap" in recent years.
    """
    conn = get_db_connection()
    query = """
        SELECT
            year,
            AVG(gdp_growth) as gdp_growth,
            AVG(avg_sentiment) as sentiment
        FROM boomcession.gdp_sentiment_quarterly
        WHERE avg_sentiment IS NOT NULL
        GROUP BY year
        ORDER BY year
    """
    df = pd.read_sql(query, conn)
    conn.close()

    # Add era classification
    df['era'] = df['year'].apply(
        lambda y: 'Post-COVID (2020-2025)' if y >= 2020 else 'Historical (1970-2019)'
    )

    return df


def load_productivity_wages():
    """
    Load productivity vs wages indexed to 1979.

    Chart 5: Dual line showing the growing gap.
    """
    conn = get_db_connection()
    query = """
        SELECT
            year,
            ROUND(AVG(productivity_index)::numeric, 1) as productivity,
            ROUND(AVG(wages_index)::numeric, 1) as wages
        FROM boomcession.productivity_wages
        WHERE productivity_index IS NOT NULL AND wages_index IS NOT NULL
        GROUP BY year
        ORDER BY year
    """
    df = pd.read_sql(query, conn)
    conn.close()

    # Reshape for multi-line chart
    productivity = df[['year', 'productivity']].copy()
    productivity['metric'] = 'Productivity'
    productivity = productivity.rename(columns={'productivity': 'index'})

    wages = df[['year', 'wages']].copy()
    wages['metric'] = 'Real Wages'
    wages = wages.rename(columns={'wages': 'index'})

    return pd.concat([productivity, wages], ignore_index=True)


def load_housing_affordability():
    """
    Load housing price-to-income ratio over time.

    Chart 6: Line chart showing housing becoming unaffordable.
    """
    conn = get_db_connection()
    query = """
        SELECT
            year,
            ROUND(AVG(price_to_income_ratio)::numeric, 2) as ratio
        FROM boomcession.housing_affordability
        GROUP BY year
        ORDER BY year
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


def load_corporate_profits_pct():
    """
    Load corporate profits as percentage of GDP.

    Chart 7: Line chart showing profits capturing more of the economy.
    """
    conn = get_db_connection()
    query = """
        SELECT
            year,
            ROUND(AVG(profits_pct_gdp)::numeric, 2) as profits_pct
        FROM boomcession.corporate_profits_pct
        GROUP BY year
        ORDER BY year
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


def load_labor_share():
    """
    Load labor share of national income over time.

    Chart 9: Line showing labor's declining share.
    """
    conn = get_db_connection()
    query = """
        SELECT year, labor_share_pct
        FROM boomcession.labor_share
        ORDER BY year
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


def load_nondiscretionary_spending():
    """
    Load non-discretionary spending (housing) as share of total PCE.

    Chart 8: Line showing spending on "stuff you don't want" growing.
    """
    conn = get_db_connection()
    query = """
        SELECT
            year,
            ROUND(AVG(housing_pct_of_pce)::numeric, 2) as housing_pct
        FROM boomcession.nondiscretionary_spending
        GROUP BY year
        ORDER BY year
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


def load_annual_sentiment():
    """
    Load annual consumer sentiment for time series.
    """
    conn = get_db_connection()
    query = """
        SELECT year, avg_sentiment as sentiment
        FROM boomcession.annual_sentiment
        ORDER BY year
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


def load_annual_gdp_growth():
    """
    Load annual GDP growth for time series.
    """
    conn = get_db_connection()
    query = """
        SELECT year, avg_gdp_growth as gdp_growth
        FROM boomcession.annual_gdp_growth
        ORDER BY year
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


def load_sentiment_gdp_dual_axis():
    """
    Load sentiment and GDP growth for dual-axis chart.

    Shows both metrics over time on same chart.
    """
    sentiment = load_annual_sentiment()
    gdp = load_annual_gdp_growth()

    # Merge on year
    df = pd.merge(sentiment, gdp, on='year', how='inner')
    return df


def load_consumer_spending_by_income():
    """
    Synthetic data for consumer spending share by income group.

    Chart 4: Based on Moody's Analytics data showing top 20%
    now account for 59% of spending (was ~50% in early 1990s).

    Note: This uses reported figures from the original article
    since detailed FRED data on spending by income quintile
    requires additional datasets.
    """
    # Based on Moody's Analytics data cited in original article
    # and other sources showing this trend
    data = []

    # Historical progression from ~1990 to 2025
    years = list(range(1990, 2026))

    # Top 20% share increased from ~50% to ~59%
    # Bottom 80% decreased from ~50% to ~41%
    for year in years:
        progress = (year - 1990) / (2025 - 1990)

        # Top 20% share grew from 50% to 59%
        top_20_share = 50 + (9 * progress)

        # Apply some noise and recession effects
        if year in [2001, 2008, 2009, 2020]:
            # Recessions temporarily reduce inequality slightly
            top_20_share -= 1.5

        bottom_80_share = 100 - top_20_share

        data.append({
            'year': year,
            'group': 'Top 20%',
            'share': round(top_20_share, 1)
        })
        data.append({
            'year': year,
            'group': 'Bottom 80%',
            'share': round(bottom_80_share, 1)
        })

    return pd.DataFrame(data)


def load_real_wage_comparison():
    """
    Load real wage growth comparison between 2018 and 2025.

    Shows identical 1.1% growth but drastically different sentiment.
    """
    data = [
        {'year': 2018, 'real_wage_growth': 1.1, 'sentiment': 98.4},
        {'year': 2025, 'real_wage_growth': 1.1, 'sentiment': 57.6},
    ]
    return pd.DataFrame(data)


def load_welfare_comparison():
    """
    Load data comparing US and Costa Rica on welfare metrics.

    Chart 10: Shows Costa Rica achieves similar life expectancy
    with 1/5 the GDP per capita - Jason Hickel's key example.
    """
    # 2022 data from World Bank / Our World in Data
    data = [
        {
            'country': 'United States',
            'gdp_per_capita': 76330,
            'life_expectancy': 77.5,
            'category': 'High GDP'
        },
        {
            'country': 'Costa Rica',
            'gdp_per_capita': 13420,
            'life_expectancy': 80.8,
            'category': 'Low GDP'
        },
        {
            'country': 'Cuba',
            'gdp_per_capita': 9500,
            'life_expectancy': 78.0,
            'category': 'Low GDP'
        },
        {
            'country': 'Japan',
            'gdp_per_capita': 33950,
            'life_expectancy': 84.8,
            'category': 'High GDP'
        },
        {
            'country': 'Spain',
            'gdp_per_capita': 29960,
            'life_expectancy': 83.3,
            'category': 'High GDP'
        },
        {
            'country': 'Vietnam',
            'gdp_per_capita': 4120,
            'life_expectancy': 75.4,
            'category': 'Low GDP'
        },
    ]
    return pd.DataFrame(data)
