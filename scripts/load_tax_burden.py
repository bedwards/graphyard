#!/usr/bin/env python3
"""
Load tax burden and income distribution data for atrocity attribution analysis.

This module calculates how much individual taxpayers contribute to state violence
through their tax payments. The core question: What is the moral burden of the
median income earner in country X in year Y?

Data Sources:
- OECD Revenue Statistics: Tax revenue by type and government level (1965-2022)
- IRS Statistics of Income: US tax burden by income percentile (2001-2020)
- UNU-WIDER WIID: Income distribution and inequality (1867-2023, 202 countries)

Attribution Framework:
1. Calculate total tax paid by median income earner
2. Determine military share of government spending
3. Estimate atrocity-linked share of military spending
4. Compute individual contribution to atrocities

Multiple attribution models are supported:
- ALL_MILITARY: All military spending enables violence
- OFFENSIVE_ONLY: Only offensive/expeditionary spending
- CIVILIAN_CASUALTIES: Proportional to documented civilian deaths
- OPERATIONS_COST: Cost of specific operations with atrocity outcomes
"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from decimal import Decimal

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'graphyard',
    'user': 'postgres',
    'password': 'postgres'
}

# OECD tax type codes
TAX_TYPES = {
    '1000': 'Income and profits',
    '1100': 'Individual income',
    '1200': 'Corporate income',
    '1300': 'Other income',
    '2000': 'Social security contributions',
    '2100': 'Employee contributions',
    '2200': 'Employer contributions',
    '3000': 'Payroll taxes',
    '4000': 'Property taxes',
    '4100': 'Recurrent property',
    '4200': 'Non-recurrent property',
    '5000': 'Goods and services',
    '5100': 'General consumption (VAT/sales)',
    '5110': 'VAT',
    '5120': 'Sales tax',
    '5200': 'Excises',
    '5300': 'Customs duties',
    '6000': 'Other taxes',
    'TOTALTAX': 'Total taxation',
}

# Government levels
GOV_LEVELS = {
    'FED': 'Federal/Central',
    'STATE': 'State/Regional',
    'LOCAL': 'Local',
    'SOCSEC': 'Social Security',
    'NES': 'Not elsewhere specified',
    'SUPRA': 'Supranational',
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def create_schema(conn):
    """Create tax_burden schema and tables."""
    cur = conn.cursor()

    cur.execute("""
        CREATE SCHEMA IF NOT EXISTS tax_burden;

        -- OECD Revenue Statistics
        DROP TABLE IF EXISTS tax_burden.oecd_revenue CASCADE;
        CREATE TABLE tax_burden.oecd_revenue (
            id SERIAL PRIMARY KEY,
            country_code CHAR(3) NOT NULL,
            country_id INTEGER REFERENCES master.countries(id),
            year SMALLINT NOT NULL,
            gov_level VARCHAR(10),
            tax_type VARCHAR(20),
            tax_name VARCHAR(100),
            variable VARCHAR(10),
            value DECIMAL(15, 4),
            unit VARCHAR(20),
            UNIQUE(country_code, year, gov_level, tax_type, variable)
        );

        -- IRS Tax Shares by Income Percentile (US-specific)
        DROP TABLE IF EXISTS tax_burden.irs_tax_shares CASCADE;
        CREATE TABLE tax_burden.irs_tax_shares (
            id SERIAL PRIMARY KEY,
            year SMALLINT NOT NULL,
            percentile VARCHAR(20) NOT NULL,
            num_returns BIGINT,
            agi_total DECIMAL(20, 2),
            agi_share DECIMAL(8, 4),
            tax_total DECIMAL(20, 2),
            tax_share DECIMAL(8, 4),
            avg_tax_rate DECIMAL(8, 4),
            UNIQUE(year, percentile)
        );

        -- Income Distribution (WIID)
        DROP TABLE IF EXISTS tax_burden.income_distribution CASCADE;
        CREATE TABLE tax_burden.income_distribution (
            id SERIAL PRIMARY KEY,
            country VARCHAR(100) NOT NULL,
            country_code CHAR(3),
            country_id INTEGER REFERENCES master.countries(id),
            year SMALLINT NOT NULL,
            gini DECIMAL(6, 4),
            palma DECIMAL(8, 4),
            ratio_top20_bottom20 DECIMAL(8, 4),
            bottom_40_share DECIMAL(6, 4),
            q1 DECIMAL(6, 4),
            q2 DECIMAL(6, 4),
            q3 DECIMAL(6, 4),
            q4 DECIMAL(6, 4),
            q5 DECIMAL(6, 4),
            d1 DECIMAL(6, 4),
            d2 DECIMAL(6, 4),
            d3 DECIMAL(6, 4),
            d4 DECIMAL(6, 4),
            d5 DECIMAL(6, 4),
            d6 DECIMAL(6, 4),
            d7 DECIMAL(6, 4),
            d8 DECIMAL(6, 4),
            d9 DECIMAL(6, 4),
            d10 DECIMAL(6, 4),
            mean_income_usd DECIMAL(15, 2),
            median_income_usd DECIMAL(15, 2),
            gdp_billions DECIMAL(15, 4),
            population_millions DECIMAL(12, 4),
            income_group VARCHAR(50),
            quality_score INTEGER,
            source TEXT
        );

        -- Median taxpayer burden (computed view)
        DROP TABLE IF EXISTS tax_burden.median_tax_burden CASCADE;
        CREATE TABLE tax_burden.median_tax_burden (
            id SERIAL PRIMARY KEY,
            country_code CHAR(3) NOT NULL,
            country_id INTEGER REFERENCES master.countries(id),
            year SMALLINT NOT NULL,
            median_income_usd DECIMAL(15, 2),
            total_tax_rate DECIMAL(8, 4),
            income_tax_rate DECIMAL(8, 4),
            consumption_tax_rate DECIMAL(8, 4),
            social_security_rate DECIMAL(8, 4),
            total_tax_paid_usd DECIMAL(15, 2),
            military_share_of_budget DECIMAL(8, 4),
            military_contribution_usd DECIMAL(15, 2),
            atrocity_attribution_model VARCHAR(50),
            atrocity_share DECIMAL(8, 4),
            atrocity_contribution_usd DECIMAL(15, 2),
            notes TEXT,
            UNIQUE(country_code, year, atrocity_attribution_model)
        );

        -- Country-year summary for easy querying
        DROP TABLE IF EXISTS tax_burden.country_year_summary CASCADE;
        CREATE TABLE tax_burden.country_year_summary (
            id SERIAL PRIMARY KEY,
            country_code CHAR(3) NOT NULL,
            country_id INTEGER REFERENCES master.countries(id),
            year SMALLINT NOT NULL,
            tax_to_gdp_ratio DECIMAL(8, 4),
            income_tax_share DECIMAL(8, 4),
            consumption_tax_share DECIMAL(8, 4),
            social_security_share DECIMAL(8, 4),
            gini DECIMAL(6, 4),
            median_income_usd DECIMAL(15, 2),
            gdp_per_capita_usd DECIMAL(15, 2),
            military_spending_pct_gdp DECIMAL(8, 4),
            military_spending_billions DECIMAL(15, 4),
            UNIQUE(country_code, year)
        );

        CREATE INDEX idx_oecd_revenue_country_year ON tax_burden.oecd_revenue(country_code, year);
        CREATE INDEX idx_income_dist_country_year ON tax_burden.income_distribution(country_code, year);
        CREATE INDEX idx_median_burden_country_year ON tax_burden.median_tax_burden(country_code, year);
    """)
    conn.commit()
    print("Schema created: tax_burden")


def load_oecd_revenue(conn):
    """Load OECD Revenue Statistics."""
    print("Loading OECD Revenue Statistics...")

    df = pd.read_csv('datasets/oecd_tax/revenue_stats.csv')
    print(f"  Raw data: {len(df):,} rows")

    # Map 3-letter country codes to master.countries
    cur = conn.cursor()
    cur.execute("SELECT iso_alpha3, id FROM master.countries WHERE iso_alpha3 IS NOT NULL")
    country_map = {row[0]: row[1] for row in cur.fetchall()}

    records = []
    for _, row in df.iterrows():
        cou = row['COU']
        if len(cou) != 3:
            continue  # Skip aggregates like OAVG

        tax_type = row['TAX']
        tax_name = TAX_TYPES.get(tax_type, tax_type)

        try:
            value = float(row['OBS_VALUE']) if pd.notna(row['OBS_VALUE']) else None
        except (ValueError, TypeError):
            value = None

        records.append((
            cou,
            country_map.get(cou),
            int(row['TIME_PERIOD']),
            row['GOV'],
            tax_type,
            tax_name,
            row['VAR'],
            value,
            row.get('UNIT_MEASURE', 'N/A')
        ))

    # Batch insert
    execute_values(cur, """
        INSERT INTO tax_burden.oecd_revenue (
            country_code, country_id, year, gov_level, tax_type, tax_name,
            variable, value, unit
        ) VALUES %s
        ON CONFLICT (country_code, year, gov_level, tax_type, variable) DO NOTHING
    """, records, page_size=10000)

    conn.commit()
    print(f"  Loaded {len(records):,} OECD revenue records")


def load_irs_data(conn):
    """Load IRS Statistics of Income tax shares by percentile."""
    print("Loading IRS tax shares data...")

    df = pd.read_excel(
        'datasets/irs_soi/tax_shares_2001_2020.xls',
        sheet_name='TAB1',
        engine='xlrd',
        header=None
    )

    # Parse the complex IRS Excel format
    # Rows 7-26 contain years 2001-2020
    # Columns represent percentiles

    percentiles = [
        'Top 0.001%', 'Top 0.01%', 'Top 0.1%', 'Top 1%',
        'Top 2%', 'Top 3%', 'Top 4%', 'Top 5%',
        'Top 10%', 'Top 20%', 'Top 25%', 'Top 30%',
        'Top 40%', 'Top 50%'
    ]

    cur = conn.cursor()
    records = []

    # Extract number of returns section (rows 7-26)
    for row_idx in range(7, 27):
        try:
            year = int(df.iloc[row_idx, 0])
            if year < 2001 or year > 2025:
                continue

            for pct_idx, pct in enumerate(percentiles):
                col_idx = pct_idx + 2  # Offset for columns
                try:
                    num_returns = int(df.iloc[row_idx, col_idx])
                    records.append((year, pct, num_returns, None, None, None, None, None))
                except (ValueError, TypeError):
                    pass
        except (ValueError, TypeError):
            continue

    execute_values(cur, """
        INSERT INTO tax_burden.irs_tax_shares (
            year, percentile, num_returns, agi_total, agi_share,
            tax_total, tax_share, avg_tax_rate
        ) VALUES %s
        ON CONFLICT (year, percentile) DO UPDATE SET
            num_returns = EXCLUDED.num_returns
    """, records)

    conn.commit()
    print(f"  Loaded {len(records)} IRS tax share records")


def load_wiid(conn):
    """Load WIID income distribution data."""
    print("Loading WIID income distribution data...")

    df = pd.read_excel('datasets/wid/WIID.xlsx', engine='openpyxl')
    print(f"  Raw data: {len(df):,} rows")

    # Map country codes
    cur = conn.cursor()
    cur.execute("SELECT iso_alpha3, id FROM master.countries WHERE iso_alpha3 IS NOT NULL")
    country_map = {row[0]: row[1] for row in cur.fetchall()}

    def safe_decimal(val):
        if pd.isna(val):
            return None
        try:
            return float(val)
        except (ValueError, TypeError):
            return None

    records = []
    for _, row in df.iterrows():
        c3 = row.get('c3')
        if pd.isna(c3):
            continue

        records.append((
            row['country'],
            c3,
            country_map.get(c3),
            int(row['year']),
            safe_decimal(row.get('gini')),
            safe_decimal(row.get('palma')),
            safe_decimal(row.get('ratio_top20bottom20')),
            safe_decimal(row.get('bottom40')),
            safe_decimal(row.get('q1')),
            safe_decimal(row.get('q2')),
            safe_decimal(row.get('q3')),
            safe_decimal(row.get('q4')),
            safe_decimal(row.get('q5')),
            safe_decimal(row.get('d1')),
            safe_decimal(row.get('d2')),
            safe_decimal(row.get('d3')),
            safe_decimal(row.get('d4')),
            safe_decimal(row.get('d5')),
            safe_decimal(row.get('d6')),
            safe_decimal(row.get('d7')),
            safe_decimal(row.get('d8')),
            safe_decimal(row.get('d9')),
            safe_decimal(row.get('d10')),
            safe_decimal(row.get('mean_usd')),
            safe_decimal(row.get('median_usd')),
            safe_decimal(row.get('gdp')) / 1e9 if pd.notna(row.get('gdp')) else None,
            safe_decimal(row.get('population')) / 1e6 if pd.notna(row.get('population')) else None,
            row.get('incomegroup'),
            int(row['quality_score']) if pd.notna(row.get('quality_score')) else None,
            row.get('source')
        ))

    execute_values(cur, """
        INSERT INTO tax_burden.income_distribution (
            country, country_code, country_id, year,
            gini, palma, ratio_top20_bottom20, bottom_40_share,
            q1, q2, q3, q4, q5,
            d1, d2, d3, d4, d5, d6, d7, d8, d9, d10,
            mean_income_usd, median_income_usd, gdp_billions,
            population_millions, income_group, quality_score, source
        ) VALUES %s
    """, records, page_size=5000)

    conn.commit()
    print(f"  Loaded {len(records):,} WIID income distribution records")


def compute_country_year_summary(conn):
    """Compute summary statistics joining tax and military data."""
    print("Computing country-year summary...")

    cur = conn.cursor()

    # First get unique country-years from OECD with tax aggregates
    cur.execute("""
        WITH tax_agg AS (
            SELECT
                country_code,
                country_id,
                year,
                MAX(CASE WHEN tax_type = 'TOTALTAX' AND variable = 'TAXGDP' AND gov_level = 'NES'
                         THEN value END) as tax_to_gdp_ratio,
                MAX(CASE WHEN tax_type = '1000' AND variable = 'TAXPER' AND gov_level = 'NES'
                         THEN value END) as income_tax_share,
                MAX(CASE WHEN tax_type = '5000' AND variable = 'TAXPER' AND gov_level = 'NES'
                         THEN value END) as consumption_tax_share,
                MAX(CASE WHEN tax_type = '2000' AND variable = 'TAXPER' AND gov_level = 'NES'
                         THEN value END) as social_security_share
            FROM tax_burden.oecd_revenue
            WHERE country_code IS NOT NULL
            GROUP BY country_code, country_id, year
        ),
        wiid_best AS (
            -- Pick highest quality observation per country-year
            SELECT DISTINCT ON (country_code, year)
                country_code, year, gini, median_income_usd,
                gdp_billions, population_millions
            FROM tax_burden.income_distribution
            WHERE country_code IS NOT NULL
            ORDER BY country_code, year, quality_score DESC NULLS LAST
        )
        INSERT INTO tax_burden.country_year_summary (
            country_code, country_id, year,
            tax_to_gdp_ratio, income_tax_share, consumption_tax_share,
            social_security_share, gini, median_income_usd,
            gdp_per_capita_usd, military_spending_pct_gdp, military_spending_billions
        )
        SELECT
            t.country_code,
            t.country_id,
            t.year,
            t.tax_to_gdp_ratio,
            t.income_tax_share,
            t.consumption_tax_share,
            t.social_security_share,
            w.gini,
            w.median_income_usd,
            CASE WHEN w.population_millions > 0
                 THEN w.gdp_billions * 1000 / w.population_millions
                 ELSE NULL END as gdp_per_capita_usd,
            s.milex_share_gdp * 100,
            s.milex_current_usd / 1000 as military_spending_billions
        FROM tax_agg t
        LEFT JOIN wiid_best w ON t.country_code = w.country_code AND t.year = w.year
        LEFT JOIN atrocity_economics.sipri_milex s ON t.country_id = s.country_id AND t.year = s.year
        ON CONFLICT (country_code, year) DO UPDATE SET
            tax_to_gdp_ratio = EXCLUDED.tax_to_gdp_ratio,
            military_spending_pct_gdp = EXCLUDED.military_spending_pct_gdp
    """)

    conn.commit()

    cur.execute("SELECT COUNT(*) FROM tax_burden.country_year_summary")
    print(f"  Created {cur.fetchone()[0]:,} country-year summary records")


def main():
    print("=" * 70)
    print("Loading Tax Burden Data for Atrocity Attribution Analysis")
    print("=" * 70)
    print()
    print("This data enables calculation of individual taxpayer contributions")
    print("to state violence through their tax payments.")
    print()

    conn = get_connection()

    create_schema(conn)
    load_oecd_revenue(conn)
    load_irs_data(conn)
    load_wiid(conn)
    compute_country_year_summary(conn)

    # Print summary
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)

    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM tax_burden.oecd_revenue")
    print(f"OECD revenue records: {cur.fetchone()[0]:,}")

    cur.execute("SELECT COUNT(DISTINCT country_code) FROM tax_burden.oecd_revenue")
    print(f"Countries in OECD data: {cur.fetchone()[0]}")

    cur.execute("SELECT MIN(year), MAX(year) FROM tax_burden.oecd_revenue")
    years = cur.fetchone()
    print(f"OECD year range: {years[0]} - {years[1]}")

    cur.execute("SELECT COUNT(*) FROM tax_burden.income_distribution")
    print(f"WIID records: {cur.fetchone()[0]:,}")

    cur.execute("SELECT COUNT(DISTINCT country_code) FROM tax_burden.income_distribution")
    print(f"Countries in WIID: {cur.fetchone()[0]}")

    # Sample query: US median taxpayer burden
    print("\n" + "=" * 70)
    print("Sample: US Tax Burden 2020")
    print("=" * 70)

    cur.execute("""
        SELECT
            cys.year,
            cys.tax_to_gdp_ratio as tax_gdp_pct,
            cys.income_tax_share,
            cys.consumption_tax_share,
            cys.social_security_share,
            cys.military_spending_pct_gdp,
            cys.military_spending_billions,
            id.median_income_usd,
            id.gini
        FROM tax_burden.country_year_summary cys
        LEFT JOIN tax_burden.income_distribution id
            ON cys.country_code = id.country_code AND cys.year = id.year
        WHERE cys.country_code = 'USA' AND cys.year = 2020
        LIMIT 1
    """)

    row = cur.fetchone()
    if row:
        year, tax_gdp, income_share, cons_share, ss_share, mil_gdp, mil_billions, median_inc, gini = row
        print(f"Year: {year}")
        print(f"Tax/GDP ratio: {tax_gdp:.1f}%")
        print(f"Income tax share: {income_share:.1f}%")
        print(f"Consumption tax share: {cons_share:.1f}%")
        print(f"Social security share: {ss_share:.1f}%")
        print(f"Military spending: {mil_gdp:.1f}% GDP (${mil_billions:.0f}B)")
        if median_inc:
            print(f"Median income: ${median_inc:,.0f}")
        if gini:
            print(f"GINI: {gini:.3f}")

        # Calculate median taxpayer military contribution
        if median_inc and tax_gdp and mil_gdp:
            effective_tax_rate = tax_gdp / 100  # Approximate
            military_share = mil_gdp / tax_gdp if tax_gdp > 0 else 0
            tax_paid = median_inc * effective_tax_rate
            military_contribution = tax_paid * military_share
            print(f"\nMedian taxpayer analysis:")
            print(f"  Estimated tax paid: ${tax_paid:,.0f}")
            print(f"  Military share of taxes: {military_share*100:.1f}%")
            print(f"  Contribution to military: ${military_contribution:,.0f}/year")

    conn.close()
    print("\nDone!")


if __name__ == '__main__':
    main()
