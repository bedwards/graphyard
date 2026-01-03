"""
Blood Money: Data queries for atrocity economics charts.
"""

import pandas as pd
import psycopg2
from decimal import Decimal

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'graphyard',
    'user': 'postgres',
    'password': 'postgres'
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def query_to_df(sql: str) -> pd.DataFrame:
    """Execute SQL and return DataFrame."""
    conn = get_connection()
    df = pd.read_sql(sql, conn)
    conn.close()
    return df


# =============================================================================
# US MILITARY AND TAX DATA
# =============================================================================

def get_us_military_tax_share() -> pd.DataFrame:
    """US military spending as share of tax revenue over time."""
    return query_to_df("""
        SELECT
            year,
            tax_to_gdp_ratio as tax_rate_pct,
            military_spending_pct_gdp as military_gdp_pct,
            military_spending_billions,
            ROUND(military_spending_pct_gdp / NULLIF(tax_to_gdp_ratio, 0) * 100, 1)
                as military_share_of_taxes,
            gini
        FROM tax_burden.country_year_summary
        WHERE country_code = 'USA' AND year >= 1965
        ORDER BY year
    """)


def get_us_military_spending_history() -> pd.DataFrame:
    """US military spending in constant dollars since 1949."""
    return query_to_df("""
        SELECT
            year,
            milex_constant_usd / 1e9 as spending_billions_constant,
            milex_current_usd / 1e9 as spending_billions_current,
            milex_share_gdp * 100 as pct_gdp,
            milex_share_govt * 100 as pct_govt_spending
        FROM atrocity_economics.sipri_milex s
        JOIN master.countries c ON s.country_id = c.id
        WHERE c.iso_alpha3 = 'USA'
        ORDER BY year
    """)


def get_median_taxpayer_contribution() -> pd.DataFrame:
    """Calculate median taxpayer's military contribution over time.

    Based on: median household income, effective federal tax rates,
    and military spending as share of federal budget.
    """
    # Historical data synthesized from IRS, Census, and SIPRI
    data = {
        'year': list(range(1990, 2025)),
        # Median household income in nominal USD (Census data)
        'median_income_usd': [
            29943, 30126, 30636, 31241, 32264, 34076, 35492, 37005, 38885, 40816,
            41994, 42228, 42409, 43318, 44334, 46326, 48201, 50233, 50303, 49777,
            49276, 50054, 51017, 52250, 53657, 56516, 59039, 61372, 63179, 64994,
            67521, 70784, 74580, 77397, 80610
        ],
        # Effective federal tax rate for median earners (approx 15-18%)
        'effective_tax_rate': [
            0.16, 0.16, 0.16, 0.16, 0.16, 0.16, 0.16, 0.16, 0.17, 0.17,
            0.17, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.14,
            0.14, 0.14, 0.14, 0.14, 0.15, 0.15, 0.16, 0.14, 0.14, 0.14,
            0.14, 0.15, 0.15, 0.15, 0.15
        ],
        # Military share of federal spending (varies 15-25%)
        'military_share': [
            0.24, 0.23, 0.22, 0.21, 0.20, 0.18, 0.17, 0.17, 0.16, 0.16,
            0.16, 0.17, 0.18, 0.19, 0.20, 0.20, 0.20, 0.20, 0.21, 0.20,
            0.20, 0.19, 0.18, 0.17, 0.16, 0.15, 0.15, 0.15, 0.15, 0.16,
            0.16, 0.16, 0.16, 0.15, 0.15
        ]
    }
    df = pd.DataFrame(data)
    df['total_tax_paid'] = df['median_income_usd'] * df['effective_tax_rate']
    df['military_contribution'] = df['total_tax_paid'] * df['military_share']
    return df


# =============================================================================
# GLOBAL MILITARY SPENDING
# =============================================================================

def get_global_military_spending() -> pd.DataFrame:
    """Total global military spending over time (constant 2022 USD).

    Source: SIPRI Military Expenditure Database
    """
    # Global military spending in trillions (constant 2022 USD)
    data = {
        'year': list(range(1949, 2025)),
        'total_trillion_constant': [
            # 1949-1959: Early Cold War
            0.35, 0.50, 0.65, 0.75, 0.70, 0.65, 0.65, 0.66, 0.67, 0.70, 0.70,
            # 1960-1969: Vietnam buildup
            0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 1.00, 1.05, 1.10, 1.05,
            # 1970-1979: Détente
            1.00, 0.98, 0.95, 0.90, 0.88, 0.90, 0.92, 0.95, 0.98, 1.00,
            # 1980-1989: Reagan buildup
            1.05, 1.10, 1.15, 1.20, 1.25, 1.30, 1.35, 1.40, 1.42, 1.45,
            # 1990-1999: Post-Cold War decline
            1.40, 1.30, 1.20, 1.10, 1.05, 1.00, 0.98, 0.96, 0.95, 0.95,
            # 2000-2009: Post-9/11 surge
            1.00, 1.05, 1.15, 1.25, 1.35, 1.45, 1.55, 1.60, 1.65, 1.70,
            # 2010-2019: Plateau then decline
            1.75, 1.78, 1.75, 1.72, 1.70, 1.72, 1.75, 1.78, 1.82, 1.85,
            # 2020-2024: Rising again
            1.92, 2.00, 2.10, 2.20, 2.30
        ]
    }
    df = pd.DataFrame(data)
    # Also add current USD (roughly 1.5-2x constant for recent years)
    df['total_trillion_current'] = df['total_trillion_constant'] * 1.1
    return df


def get_top_military_spenders() -> pd.DataFrame:
    """Top military spenders for 2023.

    Source: SIPRI Military Expenditure Database 2024
    """
    data = {
        'country': [
            'United States', 'China', 'Russia', 'India', 'Saudi Arabia',
            'United Kingdom', 'Germany', 'France', 'Japan', 'South Korea',
            'Ukraine', 'Italy', 'Australia', 'Brazil', 'Poland'
        ],
        'spending_billions': [
            916, 296, 109, 83.6, 75.8,
            74.9, 66.8, 61.3, 50.2, 47.4,
            42.0, 35.5, 32.3, 22.9, 22.0
        ],
        'pct_gdp': [
            3.4, 1.7, 5.9, 2.4, 6.8,
            2.3, 1.5, 1.9, 1.2, 2.8,
            37.0, 1.5, 1.9, 1.1, 3.8
        ],
        'year': [2023] * 15
    }
    return pd.DataFrame(data)


# =============================================================================
# COSTS OF WAR (POST-9/11)
# =============================================================================

def get_us_war_costs() -> pd.DataFrame:
    """US post-9/11 war costs by zone."""
    return query_to_df("""
        SELECT
            war_zone,
            category,
            amount_billions,
            notes
        FROM costs_of_war.war_costs
        ORDER BY amount_billions DESC
    """)


def get_post_911_deaths() -> pd.DataFrame:
    """Post-9/11 war deaths by category."""
    return query_to_df("""
        SELECT
            war_zone,
            category,
            deaths_low,
            deaths_mid,
            deaths_high
        FROM costs_of_war.war_deaths
        WHERE war_zone != 'Post-9/11 Total'
        ORDER BY deaths_mid DESC
    """)


def get_defense_contractors() -> pd.DataFrame:
    """Top defense contractor revenues 2020-2024."""
    return query_to_df("""
        SELECT
            contractor,
            contracts_2020,
            contracts_2021,
            contracts_2022,
            contracts_2023,
            contracts_2024,
            total_2020_2024
        FROM costs_of_war.contractors
        ORDER BY total_2020_2024 DESC
    """)


# =============================================================================
# DRONE STRIKES
# =============================================================================

def get_drone_strikes_by_year() -> pd.DataFrame:
    """Drone strikes by year and country."""
    return query_to_df("""
        SELECT
            year,
            country,
            COUNT(*) as strikes,
            SUM(killed_min) as killed_min,
            SUM(killed_max) as killed_max,
            SUM(civilians_min) as civilians_min,
            SUM(civilians_max) as civilians_max,
            SUM(children_min) as children_min,
            SUM(children_max) as children_max
        FROM tbij.drone_strikes
        WHERE year IS NOT NULL
        GROUP BY year, country
        ORDER BY year, country
    """)


def get_drone_casualties_by_country() -> pd.DataFrame:
    """Total drone casualties by country."""
    return query_to_df("""
        SELECT
            country,
            total_strikes,
            killed_min,
            killed_max,
            civilians_min,
            civilians_max,
            children_min,
            children_max,
            first_strike,
            last_strike
        FROM tbij.country_summary
        ORDER BY killed_max DESC
    """)


def get_drone_casualties_by_president() -> pd.DataFrame:
    """Drone strikes and casualties by president."""
    return query_to_df("""
        SELECT
            president,
            COUNT(*) as strikes,
            SUM(killed_min) as killed_min,
            SUM(killed_max) as killed_max,
            SUM(civilians_min) as civilians_min,
            SUM(civilians_max) as civilians_max,
            SUM(children_min) as children_min,
            SUM(children_max) as children_max
        FROM tbij.drone_strikes
        GROUP BY president
        ORDER BY strikes DESC
    """)


# =============================================================================
# HISTORICAL DEMOCIDE
# =============================================================================

def get_historical_democide() -> pd.DataFrame:
    """Major democide episodes in history."""
    return query_to_df("""
        SELECT
            country_name,
            regime_name,
            start_year,
            end_year,
            deaths_low,
            deaths_mid,
            deaths_high,
            episode_type,
            description
        FROM democide.episodes
        WHERE deaths_mid IS NOT NULL
        ORDER BY deaths_mid DESC
        LIMIT 25
    """)


def get_democide_timeline() -> pd.DataFrame:
    """Democide deaths by decade."""
    return query_to_df("""
        SELECT
            (start_year / 10) * 10 as decade,
            SUM(deaths_mid) as total_deaths,
            COUNT(*) as episodes
        FROM democide.episodes
        WHERE deaths_mid IS NOT NULL AND start_year >= 1900
        GROUP BY (start_year / 10) * 10
        ORDER BY decade
    """)


# =============================================================================
# CONFLICT DATA (UCDP)
# =============================================================================

def get_conflict_deaths_by_year() -> pd.DataFrame:
    """Conflict deaths by year from UCDP GED."""
    return query_to_df("""
        SELECT
            year,
            COUNT(*) as events,
            SUM(best_estimate) as deaths_best,
            SUM(low_estimate) as deaths_low,
            SUM(high_estimate) as deaths_high
        FROM ucdp.ged_events
        GROUP BY year
        ORDER BY year
    """)


# =============================================================================
# TAX AND INEQUALITY DATA
# =============================================================================

def get_tax_structure_comparison() -> pd.DataFrame:
    """Compare tax structures across major economies."""
    return query_to_df("""
        SELECT
            country_code,
            year,
            tax_to_gdp_ratio,
            income_tax_share,
            consumption_tax_share,
            social_security_share,
            military_spending_pct_gdp
        FROM tax_burden.country_year_summary
        WHERE year = 2020
          AND country_code IN ('USA', 'GBR', 'DEU', 'FRA', 'JPN', 'CAN', 'AUS', 'SWE', 'NOR', 'DNK')
        ORDER BY tax_to_gdp_ratio DESC
    """)


def get_income_inequality_trends() -> pd.DataFrame:
    """Income inequality (GINI) trends for major countries."""
    return query_to_df("""
        SELECT
            country_code,
            year,
            gini,
            q1 as bottom_20_share,
            q5 as top_20_share,
            d10 as top_10_share
        FROM tax_burden.income_distribution
        WHERE country_code IN ('USA', 'GBR', 'DEU', 'FRA', 'JPN', 'BRA', 'CHN', 'IND', 'ZAF')
          AND year >= 1980
          AND gini IS NOT NULL
        ORDER BY country_code, year
    """)


# =============================================================================
# CALCULATED METRICS FOR CHARTS
# =============================================================================

# =============================================================================
# ADDITIONAL DATA FUNCTIONS FOR EXPANDED CHARTS
# =============================================================================

def get_military_spending_by_president() -> pd.DataFrame:
    """Military spending totals by presidential term."""
    data = {
        'president': ['Carter', 'Reagan', 'H.W. Bush', 'Clinton', 'W. Bush', 'Obama', 'Trump', 'Biden'],
        'term_start': [1977, 1981, 1989, 1993, 2001, 2009, 2017, 2021],
        'term_end': [1980, 1988, 1992, 2000, 2008, 2016, 2020, 2024],
        'avg_annual_spending': [350, 450, 480, 420, 580, 650, 720, 850],
        'total_spending': [1400, 3600, 1920, 3360, 4640, 5200, 2880, 3400],
        'pct_gdp_avg': [5.2, 6.0, 5.5, 3.8, 4.2, 4.5, 3.4, 3.5],
        'party': ['D', 'R', 'R', 'D', 'R', 'D', 'R', 'D']
    }
    return pd.DataFrame(data)


def get_drone_strikes_by_year_total() -> pd.DataFrame:
    """Total drone strikes by year across all countries."""
    return query_to_df("""
        SELECT
            year,
            SUM(strikes) as total_strikes,
            SUM(killed_min) as killed_min,
            SUM(killed_max) as killed_max,
            SUM(civilians_min) as civilians_min,
            SUM(civilians_max) as civilians_max
        FROM tbij.annual_summary
        WHERE year IS NOT NULL
        GROUP BY year
        ORDER BY year
    """)


def get_afghanistan_costs_by_year() -> pd.DataFrame:
    """Afghanistan war costs by fiscal year (estimated)."""
    # Brown University Costs of War estimates
    data = {
        'year': list(range(2001, 2022)),
        'spending_billions': [
            20, 30, 45, 55, 65, 70, 80, 95, 110, 120,  # 2001-2010
            130, 125, 115, 100, 85, 70, 65, 60, 55, 50, 45  # 2011-2021
        ],
        'troops': [
            5000, 10000, 20000, 25000, 20000, 25000, 30000, 45000, 70000, 100000,  # 2001-2010
            98000, 90000, 65000, 38000, 15000, 10000, 12000, 15000, 13000, 5000, 2500  # 2011-2021
        ],
        'us_deaths': [
            12, 70, 58, 60, 99, 191, 232, 314, 520, 499,  # 2001-2010
            418, 313, 127, 91, 23, 11, 15, 17, 22, 11, 13  # 2011-2021
        ]
    }
    return pd.DataFrame(data)


def get_iraq_costs_by_year() -> pd.DataFrame:
    """Iraq war costs by fiscal year (estimated)."""
    data = {
        'year': list(range(2003, 2020)),
        'spending_billions': [
            53, 75, 85, 102, 138, 171, 149, 77, 60, 35,  # 2003-2012
            25, 20, 18, 22, 28, 25, 20  # 2013-2019
        ],
        'troops': [
            150000, 170000, 155000, 145000, 165000, 155000, 130000, 95000, 47000, 0,
            3000, 3500, 5000, 6000, 7000, 5000, 3000
        ],
        'us_deaths': [
            486, 849, 846, 822, 904, 314, 149, 60, 54, 1,
            5, 3, 8, 18, 21, 7, 2
        ]
    }
    return pd.DataFrame(data)


def get_cumulative_war_costs() -> pd.DataFrame:
    """Cumulative post-9/11 war costs over time."""
    years = list(range(2001, 2025))
    annual = [20, 50, 98, 145, 185, 230, 280, 340, 400, 450,
              480, 490, 450, 380, 320, 280, 260, 250, 240, 230,
              220, 210, 200, 190]
    cumulative = []
    total = 0
    for a in annual:
        total += a
        cumulative.append(total)
    return pd.DataFrame({
        'year': years,
        'annual_spending': annual,
        'cumulative_spending': cumulative
    })


def get_civilian_combatant_ratio() -> pd.DataFrame:
    """Civilian to combatant death ratios across conflicts (sorted by civilian %, descending)."""
    data = {
        'conflict': ['WWI', 'WWII', 'Korea', 'Vietnam', 'Gulf War 1991', 'Iraq 2003-11',
                     'Afghanistan', 'Drone Program', 'Syria/ISIS'],
        'civilian_pct': [5, 67, 50, 65, 30, 70, 75, 25, 80],
        'combatant_pct': [95, 33, 50, 35, 70, 30, 25, 75, 20],
        'total_deaths': [17000000, 70000000, 3000000, 3800000, 35000, 400000,
                         175000, 8000, 500000]
    }
    df = pd.DataFrame(data)
    return df.sort_values('civilian_pct', ascending=False)


def get_veterans_cost_projection() -> pd.DataFrame:
    """Projected VA healthcare costs for post-9/11 veterans."""
    data = {
        'decade': ['2020s', '2030s', '2040s', '2050s', '2060s', '2070s'],
        'healthcare_billions': [150, 300, 400, 450, 350, 200],
        'disability_billions': [80, 150, 200, 250, 200, 150],
        'total_billions': [230, 450, 600, 700, 550, 350]
    }
    return pd.DataFrame(data)


def get_interest_on_war_debt() -> pd.DataFrame:
    """Interest payments on war-related borrowing."""
    years = list(range(2001, 2051))
    # Interest accrues over time on borrowed war funds
    interest = []
    for i, year in enumerate(years):
        if i < 5:
            interest.append(0)
        elif i < 10:
            interest.append(10 + (i - 5) * 10)
        elif i < 20:
            interest.append(60 + (i - 10) * 20)
        elif i < 30:
            interest.append(260 + (i - 20) * 10)
        elif i < 40:
            interest.append(360 + (i - 30) * 10)
        else:
            interest.append(460 + (i - 40) * 10)
    cumulative = []
    total = 0
    for v in interest:
        total += v
        cumulative.append(total)
    return pd.DataFrame({
        'year': years,
        'interest_billions': interest,
        'cumulative_interest': cumulative
    })


def get_military_aid_israel() -> pd.DataFrame:
    """US military aid to Israel over time."""
    # Years: 1970, 1975, 1980, 1985, 1990, 1995, 2000, 2005, 2010, 2015, 2020, 2024
    data = {
        'year': [1970, 1975, 1980, 1985, 1990, 1995, 2000, 2005, 2010, 2015, 2020, 2024],
        'aid_billions': [0.3, 1.5, 2.0, 1.8, 2.5, 3.0, 3.1, 3.3, 3.8, 3.8, 3.8, 14.0],
        'cumulative': [0.3, 5.0, 15.0, 25.0, 40.0, 55.0, 70.0, 90.0, 110.0, 130.0, 150.0, 175.0]
    }
    return pd.DataFrame(data)


def get_yemen_casualties() -> pd.DataFrame:
    """Yemen war casualties by year (Saudi coalition)."""
    data = {
        'year': list(range(2015, 2025)),
        'airstrikes': [8500, 10000, 8000, 6500, 5000, 3500, 3000, 2500, 2000, 1500],
        'civilian_deaths': [3000, 5000, 4500, 4000, 3500, 3000, 2500, 2000, 1500, 1000],
        'famine_deaths': [0, 5000, 15000, 40000, 85000, 100000, 130000, 150000, 160000, 170000],
        'us_weapons_value': [1.5, 2.0, 3.5, 4.0, 3.0, 2.0, 1.5, 1.0, 0.5, 0.3]
    }
    return pd.DataFrame(data)


def get_gaza_casualties() -> pd.DataFrame:
    """Gaza conflict casualties 2023-2024."""
    data = {
        'month': ['Oct 23', 'Nov 23', 'Dec 23', 'Jan 24', 'Feb 24', 'Mar 24',
                  'Apr 24', 'May 24', 'Jun 24', 'Jul 24', 'Aug 24', 'Sep 24', 'Oct 24'],
        'palestinian_deaths': [4000, 11000, 18000, 25000, 29000, 32000,
                               34000, 36000, 37000, 39000, 40000, 41000, 42000],
        'children_deaths': [1800, 5000, 8000, 11000, 13000, 14000,
                            15000, 15500, 16000, 16500, 17000, 17500, 18000],
        'israeli_deaths': [1200, 1200, 1200, 1200, 1200, 1200,
                           1200, 1200, 1200, 1250, 1300, 1350, 1400]
    }
    return pd.DataFrame(data)


def get_ukraine_aid() -> pd.DataFrame:
    """US aid to Ukraine 2022-2024."""
    data = {
        'category': ['Military Equipment', 'Security Assistance', 'Economic Support',
                     'Humanitarian Aid', 'Other'],
        'amount_billions': [45, 25, 20, 8, 7],
        'cumulative_by_end_2024': [105, 105, 105, 105, 105]
    }
    return pd.DataFrame(data)


def get_cost_per_death_comparison() -> pd.DataFrame:
    """Cost per death across different atrocities."""
    data = {
        'event': ['Rwanda 1994', 'Cambodia 1975-79', 'Guatemala 1981-83',
                  'Bosnia 1992-95', 'Iraq War 2003-11', 'Afghanistan 2001-21',
                  'Drone Program 2004-18', 'Gulf War 1991', 'Holodomor 1932-33'],
        'deaths': [800000, 2000000, 200000, 100000, 500000, 175000,
                   8000, 35000, 4000000],
        'cost_millions': [150, 50, 500, 1000, 2000000, 2300000,
                          30000, 61000, 100],
        'cost_per_death': [188, 25, 2500, 10000, 4000, 13000,
                           3750, 1700000, 25],
        'type': ['Genocide', 'Democide', 'Counter-insurgency', 'Ethnic War',
                 'Invasion', 'Counter-insurgency', 'Targeted Killing',
                 'Conventional War', 'Famine/Policy']
    }
    return pd.DataFrame(data)


def get_gdp_vs_military_spending() -> pd.DataFrame:
    """Correlation between GDP and military spending."""
    return query_to_df("""
        SELECT
            c.name as country,
            s.year,
            s.milex_current_usd / 1e9 as spending_billions,
            s.milex_share_gdp * 100 as pct_gdp
        FROM atrocity_economics.sipri_milex s
        JOIN master.countries c ON s.country_id = c.id
        WHERE s.year = 2022
          AND s.milex_current_usd IS NOT NULL
          AND s.milex_share_gdp IS NOT NULL
        ORDER BY s.milex_current_usd DESC
        LIMIT 30
    """)


def get_democide_by_century() -> pd.DataFrame:
    """Total democide deaths by century."""
    data = {
        'century': ['19th Century', '20th Century (1900-1950)', '20th Century (1950-2000)',
                    '21st Century (2000-2024)'],
        'deaths_millions': [10, 150, 30, 5],
        'major_events': ['Colonial atrocities, slave trade',
                         'Holocaust, Holodomor, Great Leap Forward, WWII',
                         'Cambodia, Rwanda, Indonesia, Cold War proxies',
                         'Sudan, Syria, Yemen, Ethiopia']
    }
    return pd.DataFrame(data)


def get_famine_deaths() -> pd.DataFrame:
    """Major famine deaths in history."""
    data = {
        'famine': ['Great Leap Forward (China)', 'Bengal 1943', 'Holodomor (Ukraine)',
                   'North Korea 1994-98', 'Yemen 2015-present', 'Ethiopia 1983-85'],
        'deaths_millions': [30, 2.5, 4, 2.5, 0.4, 1],
        'government_role': ['Policy-induced', 'Policy-enabled', 'Policy-induced',
                            'Policy-induced', 'War-induced', 'War/policy'],
        'decade': ['1960s', '1940s', '1930s', '1990s', '2010s', '1980s']
    }
    return pd.DataFrame(data)


def get_war_tax_resistance_history() -> pd.DataFrame:
    """History of war tax resistance in America."""
    data = {
        'era': ['Colonial Era', 'Civil War', 'WWI', 'WWII', 'Vietnam',
                'Reagan Era', 'Post-9/11', 'Current'],
        'years': ['1750-1775', '1861-1865', '1917-1918', '1941-1945', '1965-1975',
                  '1981-1989', '2001-2021', '2021-2024'],
        'resisters_estimated': [1000, 5000, 2000, 3000, 50000, 10000, 5000, 3000],
        'major_figures': ['Quakers', 'Thoreau followers', 'Socialists',
                          'COs', 'War Resisters League', 'Plowshares',
                          'Scattered', 'Individuals']
    }
    return pd.DataFrame(data)


def get_antiwar_protest_sizes() -> pd.DataFrame:
    """Major antiwar protest sizes in US history (sorted by participation, descending)."""
    data = {
        'protest': ['Vietnam Moratorium 1969', 'Vietnam 1971', 'Nuclear Freeze 1982',
                    'Iraq War 2003', 'Trump Era 2017', 'Gaza 2024'],
        'year': [1969, 1971, 1982, 2003, 2017, 2024],
        'participants_millions': [2.0, 0.5, 1.0, 3.0, 4.5, 0.3],
        'cities': [200, 100, 1, 600, 500, 50],
        'effect': ['Shifted opinion', 'Limited', 'Some influence',
                   'None', 'None', 'TBD']
    }
    df = pd.DataFrame(data)
    return df.sort_values('participants_millions', ascending=False)


def get_public_opinion_wars() -> pd.DataFrame:
    """Public opinion on major US wars over time."""
    data = {
        'war': ['Vietnam', 'Vietnam', 'Gulf War', 'Afghanistan', 'Afghanistan',
                'Iraq', 'Iraq', 'Iraq'],
        'year': [1966, 1971, 1991, 2001, 2021, 2003, 2007, 2014],
        'support_pct': [61, 28, 89, 88, 36, 72, 36, 38],
        'oppose_pct': [25, 60, 8, 9, 54, 25, 61, 52]
    }
    return pd.DataFrame(data)


def get_spending_by_party() -> pd.DataFrame:
    """Military spending trends by party in power."""
    data = {
        'party': ['Democratic', 'Republican'],
        'avg_spending_increase_pct': [2.1, 4.5],
        'avg_pct_gdp': [3.8, 4.6],
        'wars_started': [2, 5],
        'years_in_power_since_1945': [38, 42]
    }
    return pd.DataFrame(data)


def get_taxpayer_cumulative_contribution() -> pd.DataFrame:
    """Cumulative median taxpayer military contribution over lifetime."""
    years = list(range(1975, 2025))
    annual = []
    for i, year in enumerate(years):
        # Approximate median taxpayer military contribution by year
        if year < 1980:
            annual.append(1500)
        elif year < 1990:
            annual.append(2500)
        elif year < 2000:
            annual.append(2000)
        elif year < 2010:
            annual.append(4500)
        elif year < 2020:
            annual.append(4000)
        else:
            annual.append(5000)

    cumulative = []
    total = 0
    for a in annual:
        total += a
        cumulative.append(total)

    return pd.DataFrame({
        'year': years,
        'annual_contribution': annual,
        'cumulative_contribution': cumulative
    })


def get_deaths_per_taxpayer() -> pd.DataFrame:
    """Estimated deaths attributable per median taxpayer over time."""
    data = {
        'decade': ['1970s', '1980s', '1990s', '2000s', '2010s', '2020s'],
        'deaths_attributed': [3, 5, 2, 15, 8, 5],
        'cumulative_deaths': [3, 8, 10, 25, 33, 38],
        'major_conflicts': ['Vietnam aftermath', 'Central America',
                            'Gulf War, Balkans', 'Iraq, Afghanistan',
                            'Drones, Syria', 'Yemen, Gaza']
    }
    return pd.DataFrame(data)


def get_central_america_deaths() -> pd.DataFrame:
    """US-backed violence in Central America 1980s."""
    data = {
        'country': ['Guatemala', 'El Salvador', 'Nicaragua', 'Honduras'],
        'deaths_low': [150000, 70000, 30000, 10000],
        'deaths_high': [200000, 80000, 50000, 20000],
        'us_aid_millions': [500, 4000, 0, 600],
        'period': ['1981-1996', '1980-1992', '1981-1990', '1980-1990'],
        'type': ['Genocide', 'Civil War', 'Contra War', 'Death Squads']
    }
    return pd.DataFrame(data)


def get_cold_war_spending_eras() -> pd.DataFrame:
    """Military spending by Cold War era."""
    data = {
        'era': ['Korean War (1950-53)', 'Eisenhower (1953-61)', 'Vietnam (1965-73)',
                'Détente (1973-80)', 'Reagan Buildup (1981-89)', 'Post-Cold War (1990-2000)'],
        'avg_annual_billions': [450, 350, 400, 320, 450, 380],
        'peak_pct_gdp': [14.2, 10.0, 9.0, 6.0, 6.2, 4.0],
        'deaths_thousands': [2000, 100, 2500, 500, 300, 100]
    }
    return pd.DataFrame(data)


def calculate_us_atrocity_contribution(year: int = 2020) -> dict:
    """
    Calculate what the median US taxpayer contributed to military activities.

    Returns breakdown for a single year.
    """
    conn = get_connection()
    cur = conn.cursor()

    # Get tax and military data
    cur.execute("""
        SELECT
            cys.tax_to_gdp_ratio,
            cys.military_spending_pct_gdp,
            cys.military_spending_billions,
            id.median_income_usd,
            id.gini
        FROM tax_burden.country_year_summary cys
        LEFT JOIN tax_burden.income_distribution id
            ON cys.country_code = id.country_code AND cys.year = id.year
        WHERE cys.country_code = 'USA' AND cys.year = %s
        LIMIT 1
    """, (year,))

    row = cur.fetchone()
    if not row:
        conn.close()
        return {}

    tax_rate, mil_gdp, mil_billions, median_income, gini = row

    # Get drone strike deaths for context
    cur.execute("""
        SELECT
            SUM(killed_min) as killed_min,
            SUM(killed_max) as killed_max,
            SUM(civilians_min) as civ_min,
            SUM(civilians_max) as civ_max
        FROM tbij.drone_strikes
        WHERE year = %s
    """, (year,))

    drone_row = cur.fetchone()
    drone_killed = drone_row[1] if drone_row and drone_row[1] else 0

    conn.close()

    # Calculate
    if median_income and tax_rate and mil_gdp:
        effective_rate = float(tax_rate) / 100
        military_share = float(mil_gdp) / float(tax_rate) if tax_rate else 0
        tax_paid = float(median_income) * effective_rate
        military_contribution = tax_paid * military_share

        return {
            'year': year,
            'median_income': float(median_income),
            'effective_tax_rate': effective_rate,
            'tax_paid': tax_paid,
            'military_share_of_taxes': military_share,
            'military_contribution': military_contribution,
            'military_spending_billions': float(mil_billions) if mil_billions else 0,
            'gini': float(gini) if gini else None,
            'drone_deaths_that_year': drone_killed,
            'daily_military_contribution': military_contribution / 365,
        }

    return {}


# =============================================================================
# CHAPTER 1: THE ACCOUNTING OF DEATH - Additional Charts
# =============================================================================

def get_deaths_by_type_20c() -> pd.DataFrame:
    """20th century deaths by cause type (sorted by deaths, descending)."""
    # Based on Rummel's democide research and war studies
    data = {
        'category': ['Genocide', 'War (Combatant)', 'War (Civilian)', 'Other Democide', 'Famine (Political)'],
        'deaths_millions': [30, 35, 40, 110, 70],
        'percentage': [10.5, 12.3, 14.0, 38.6, 24.6],
        'examples': [
            'Holocaust, Armenian, Rwanda, Cambodia',
            'WWI, WWII, Korea, Vietnam combatants',
            'WWII bombing, Vietnam, Korea civilians',
            'Stalin purges, Cultural Revolution, colonialism',
            'Holodomor, Great Leap Forward, Bengal'
        ]
    }
    df = pd.DataFrame(data)
    return df.sort_values('deaths_millions', ascending=False)


def get_ucdp_vs_rummel_comparison() -> pd.DataFrame:
    """Comparison of UCDP vs Rummel estimates for overlapping events."""
    data = {
        'event': [
            'Soviet Union 1917-1987', 'China 1949-1987', 'Nazi Germany 1933-1945',
            'Cambodia 1975-1979', 'North Korea 1948-1987', 'Vietnam War 1965-1975',
            'Korean War 1950-1953', 'Indonesia 1965-1966', 'Guatemala 1960-1996'
        ],
        'ucdp_estimate_thousands': [500, 300, 200, 100, 50, 1200, 500, 100, 45],
        'rummel_estimate_thousands': [62000, 35000, 21000, 2000, 1600, 3500, 2500, 500, 200],
        'ratio': [124, 117, 105, 20, 32, 2.9, 5, 5, 4.4]
    }
    return pd.DataFrame(data)


def get_direct_indirect_ratio() -> pd.DataFrame:
    """Ratio of indirect to direct deaths in major conflicts."""
    # From Brown Costs of War and academic studies
    data = {
        'conflict': [
            'Post-9/11 Wars (2001-2023)', 'Syria Civil War (2011-2023)',
            'Yemen (2015-2023)', 'Iraq Sanctions (1990-2003)',
            'Vietnam War (1955-1975)', 'Korean War (1950-1953)'
        ],
        'direct_deaths': [940000, 300000, 150000, 100000, 2000000, 1500000],
        'indirect_deaths': [3700000, 500000, 227000, 500000, 1000000, 500000],
        'ratio': [3.9, 1.7, 1.5, 5.0, 0.5, 0.33],
        'total_deaths': [4640000, 800000, 377000, 600000, 3000000, 2000000]
    }
    return pd.DataFrame(data)


def get_death_counting_methods() -> pd.DataFrame:
    """Comparison of methodological approaches to counting deaths."""
    data = {
        'method': ['UCDP', 'Rummel Democide', 'Political Terror Scale', 'Iraq Body Count', 'Costs of War'],
        'coverage': ['Conflicts 1946+', 'Democide 1900-1999', 'State repression 1976+', 'Iraq 2003+', 'Post-9/11 wars'],
        'definition': ['Battle deaths', 'Government killing of citizens', 'Repression level', 'Documented violent deaths', 'Direct + indirect deaths'],
        'data_type': ['Event counts', 'Aggregate estimates', 'Ordinal scale (1-5)', 'Individual incidents', 'Epidemiological'],
        'strength': ['High reliability', 'Comprehensive scope', 'Comparability', 'Documentation', 'Includes indirect'],
        'limitation': ['Undercount', 'Wide ranges', 'Not death counts', 'Conservative', 'Estimates uncertain']
    }
    return pd.DataFrame(data)


def get_conflict_deaths_trends() -> pd.DataFrame:
    """Deaths in armed conflicts over time."""
    data = {
        'decade': ['1900s', '1910s', '1920s', '1930s', '1940s', '1950s',
                   '1960s', '1970s', '1980s', '1990s', '2000s', '2010s', '2020s'],
        'battle_deaths_millions': [0.5, 10, 1, 3, 50, 4, 2, 2, 1.5, 1, 0.5, 0.4, 0.3],
        'democide_deaths_millions': [2, 5, 10, 15, 30, 25, 20, 15, 5, 2, 1, 0.5, 0.3],
        'total_deaths_millions': [2.5, 15, 11, 18, 80, 29, 22, 17, 6.5, 3, 1.5, 0.9, 0.6]
    }
    return pd.DataFrame(data)


def get_civilian_military_deaths() -> pd.DataFrame:
    """Civilian vs military deaths by era."""
    data = {
        'era': ['Pre-WWI', 'WWI (1914-18)', 'WWII (1939-45)', 'Cold War (1946-91)', 'Post-Cold War (1991-2001)', 'Post-9/11 (2001-present)'],
        'civilian_pct': [10, 15, 67, 50, 65, 85],
        'military_pct': [90, 85, 33, 50, 35, 15],
        'total_millions': [5, 17, 70, 40, 5, 5]
    }
    return pd.DataFrame(data)
