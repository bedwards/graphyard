#!/usr/bin/env python3
"""
Dual-Package Chart Generation

Generates charts using BOTH:
1. Altair (Python) - declarative grammar of graphics
2. Observable Plot (TypeScript) - D3-based high-level charting

Each chart is produced in both renderers, allowing the final article
to have two versions with different aesthetic approaches.

Usage:
    python charts/generate_dual.py              # Generate all charts
    python charts/generate_dual.py --renderer=altair    # Altair only
    python charts/generate_dual.py --renderer=plot      # Observable Plot only
"""

import argparse
import json
from pathlib import Path
import subprocess
import sys

from spec import ChartSpec, ChartType

# Add project root for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from charts.gdp.data import (
    load_world_gdp_trend,
    load_country_gdp_comparison,
    load_gdp_growth_rates,
    load_gdp_per_capita_by_income_group,
    load_gdp_components,
    load_regional_gdp,
    load_country_gdp_timeseries,
    load_country_growth_timeseries,
    load_crisis_comparison,
    load_gdp_per_capita_timeseries,
    load_life_expectancy_vs_gdp,
    load_japan_lost_decades,
    load_argentina_vs_peers,
    load_ml_feature_importance,
    load_ml_model_comparison,
    load_gini_timeseries,
    load_emissions_vs_gdp,
    load_income_share_top10_timeseries,
)
from charts.beyond_growth.data import (
    load_emissions_by_income_group,
    load_top10_income_share_timeseries,
    load_adjusted_savings_comparison,
    load_resource_depletion_by_income_group,
    load_life_expectancy_vs_gdp_all,
    load_latin_america_gini_timeseries,
    load_wellbeing_vs_footprint,
    load_adjusted_savings_timeseries,
    load_carbon_inequality_proper,
    load_emissions_per_capita_ratio,
    load_world_gdp_growth_long_term,
    load_adjusted_net_savings_by_income_group,
    load_high_wellbeing_low_footprint,
    load_gdp_threshold_analysis,
    load_cumulative_emissions_by_region,
)
from charts.baseball.data import get_loader as get_baseball_loader
from charts.marx.data import (
    load_top10_income_share,
    load_gini_index,
    load_financial_sector_growth,
    load_manufacturing_share,
    load_unemployment_rate,
    load_world_gdp_growth,
    load_capital_formation,
    load_us_sector_transformation,
    load_us_inequality_timeline,
    load_us_financialization,
    load_global_inequality_comparison,
)
from charts.sabermetrics.data import (
    load_pythagorean_validation,
    load_pythagorean_accuracy_by_decade,
    load_runs_created_validation,
    load_runs_created_historical,
    load_home_run_evolution,
    load_batting_average_evolution,
    load_strikeout_walk_evolution,
    load_stolen_base_evolution,
    load_pythagorean_outliers,
)
from charts.education.data import (
    load_learning_styles_meta_analysis,
    load_learning_styles_belief_rates,
    load_pisa_math_scores_over_time,
    load_pisa_2022_rankings,
    load_finland_decline,
    load_spending_vs_outcomes,
    load_us_state_spending_outcomes,
    load_homework_effect_by_grade,
    load_effect_size_comparison,
)
from charts.ncaa_basketball.data import (
    load_first_round_upset_rates,
    load_seed_advancement_rates,
    load_model_accuracy_comparison,
    load_kenpom_vs_seed_success,
    load_one_seed_strength_history,
    load_upset_totals_by_seed,
    load_volatility_factors,
    load_champion_profile,
    load_transfer_portal_era,
)

OUTPUT_DIR_ALTAIR = PROJECT_ROOT / "site" / "public" / "assets" / "charts" / "altair"
OUTPUT_DIR_PLOT = PROJECT_ROOT / "site" / "public" / "assets" / "charts" / "plot"
SPECS_DIR = PROJECT_ROOT / "site" / "public" / "assets" / "charts" / "specs"


def get_gdp_chart_specs() -> list[ChartSpec]:
    """Define all GDP article charts."""
    return [
        ChartSpec(
            chart_id="world-gdp-trend",
            chart_type=ChartType.LINE,
            title="World GDP Over Time",
            data_source=lambda: load_world_gdp_trend(1960, 2023),
            x="year",
            y="value",
            x_label="Year",
            y_label="GDP (Current US$)",
            x_format="year",  # Prevents comma formatting (2025 not 2,025)
            y_format="trillions",
        ),
        ChartSpec(
            chart_id="world-gdp-growth",
            chart_type=ChartType.BAR,
            title="World GDP Growth Rate",
            data_source=lambda: load_gdp_growth_rates("WLD", 30),
            x="year",
            y="value",
            x_label="Year",
            y_label="Annual Growth (%)",
            x_format="year",  # Prevents comma formatting (2025 not 2,025)
            y_format="percent_raw",  # Data already in % form (3.5 = 3.5%), don't multiply
            options={"highlight_negative": True},
        ),
        ChartSpec(
            chart_id="top-10-gdp",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="World's Largest Economies (2023)",
            data_source=lambda: load_country_gdp_comparison(
                ["USA", "CHN", "JPN", "DEU", "IND", "GBR", "FRA", "BRA", "ITA", "CAN"],
                2023
            ),
            x="entity_name",
            y="value",
            x_label="Country",
            y_label="GDP (Current US$)",
            y_format="trillions",
        ),
        ChartSpec(
            chart_id="gdp-by-region",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="GDP by World Bank Region (2023)",
            data_source=lambda: load_regional_gdp(2023),
            x="entity_name",
            y="value",
            x_label="Region",
            y_label="GDP (Current US$)",
            y_format="trillions",
        ),
        ChartSpec(
            chart_id="gdp-per-capita-income-groups",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="GDP Per Capita by Income Group (2023)",
            data_source=lambda: load_gdp_per_capita_by_income_group(2023),
            x="entity_name",
            y="value",
            x_label="Income Group",
            y_label="GDP Per Capita (US$)",
            y_format="thousands",
        ),
        ChartSpec(
            chart_id="gdp-components-usa",
            chart_type=ChartType.HORIZONTAL_BAR,  # Bar chart better than pie for comparing values
            title="US GDP Components (2022)",
            data_source=lambda: load_gdp_components("USA", 2022),
            x="indicator_name",
            y="value",
            x_label="Component",
            y_label="Value (US$)",
            y_format="trillions",
        ),
        ChartSpec(
            chart_id="china-usa-gdp",
            chart_type=ChartType.LINE,
            title="The Rise of China: GDP Comparison",
            data_source=lambda: load_country_gdp_timeseries(["CHN", "USA"], 1980, 2023),
            x="year",
            y="value",
            x_label="Year",
            y_label="GDP (Current US$)",
            x_format="year",
            y_format="trillions",
            color="country",
        ),
        # Part VII: Case Studies
        ChartSpec(
            chart_id="china-growth-miracle",
            chart_type=ChartType.LINE,
            title="China's Growth Miracle (1980-2023)",
            data_source=lambda: load_country_growth_timeseries(["CHN"], 1980, 2023),
            x="year",
            y="value",
            x_label="Year",
            y_label="GDP Growth (%)",
            x_format="year",
            y_format="percent_raw",
            color="country",
        ),
        ChartSpec(
            chart_id="japan-lost-decades",
            chart_type=ChartType.BAR,
            title="Japan's Lost Decades",
            data_source=lambda: load_gdp_growth_rates("JPN", 40),
            x="year",
            y="value",
            x_label="Year",
            y_label="GDP Growth (%)",
            x_format="year",
            y_format="percent_raw",
            options={"highlight_negative": True},
        ),
        ChartSpec(
            chart_id="argentina-vs-peers",
            chart_type=ChartType.LINE,
            title="Argentina's Relative Decline",
            data_source=lambda: load_gdp_per_capita_timeseries(["ARG", "CHL", "AUS"], 1960, 2023),
            x="year",
            y="value",
            x_label="Year",
            y_label="GDP Per Capita (US$)",
            x_format="year",
            y_format="thousands",
            color="country",
        ),
        # Part VIII: Crises
        ChartSpec(
            chart_id="crisis-2008",
            chart_type=ChartType.LINE,
            title="The 2008 Financial Crisis: Global Synchronization",
            data_source=lambda: load_crisis_comparison(2009, ["USA", "DEU", "JPN", "GBR", "CHN"], 4),
            x="year",
            y="value",
            x_label="Year",
            y_label="GDP Growth (%)",
            x_format="year",
            y_format="percent_raw",
            color="country",
        ),
        ChartSpec(
            chart_id="crisis-covid",
            chart_type=ChartType.LINE,
            title="The COVID-19 Shock and Recovery",
            data_source=lambda: load_crisis_comparison(2020, ["USA", "DEU", "JPN", "GBR", "CHN", "IND"], 3),
            x="year",
            y="value",
            x_label="Year",
            y_label="GDP Growth (%)",
            x_format="year",
            y_format="percent_raw",
            color="country",
        ),
        # Part X/XI: GDP Limitations and Alternatives
        ChartSpec(
            chart_id="life-expectancy-vs-gdp",
            chart_type=ChartType.SCATTER,
            title="Life Expectancy vs GDP Per Capita (2022)",
            data_source=lambda: load_life_expectancy_vs_gdp(2022),
            x="gdp_per_capita",
            y="life_expectancy",
            x_label="GDP Per Capita (US$)",
            y_label="Life Expectancy (Years)",
            x_format="thousands",
        ),
        # Part IX: Machine Learning Forecasting
        ChartSpec(
            chart_id="ml-feature-importance",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="What Predicts GDP? Feature Importance",
            data_source=load_ml_feature_importance,
            x="feature",
            y="importance",
            x_label="Feature",
            y_label="Importance",
            y_format="percent",
        ),
        ChartSpec(
            chart_id="ml-model-comparison",
            chart_type=ChartType.BAR,
            title="Model Comparison: R² Score",
            data_source=load_ml_model_comparison,
            x="model",
            y="r_squared",
            x_label="Model",
            y_label="R² Score",
        ),
        # Part X: What GDP Doesn't Measure
        ChartSpec(
            chart_id="us-inequality-gini",
            chart_type=ChartType.LINE,
            title="Rising Inequality: US Gini Coefficient (1963-2023)",
            data_source=lambda: load_gini_timeseries(["USA"], 1963, 2023),
            x="year",
            y="value",
            x_label="Year",
            y_label="Gini Coefficient",
            x_format="year",
            color="country",
        ),
        ChartSpec(
            chart_id="emissions-vs-gdp",
            chart_type=ChartType.SCATTER,
            title="The Environmental Cost: Emissions vs GDP (2020)",
            data_source=lambda: load_emissions_vs_gdp(2020),
            x="gdp_per_capita",
            y="emissions_per_capita",
            x_label="GDP Per Capita (US$)",
            y_label="GHG Emissions (tonnes CO2e/capita)",
            x_format="thousands",
        ),
        # Part XII: Distributional National Accounts
        ChartSpec(
            chart_id="income-share-top10",
            chart_type=ChartType.LINE,
            title="Who Benefits from Growth? Income Share of Top 10%",
            data_source=lambda: load_income_share_top10_timeseries(["USA", "DEU", "GBR", "FRA"], 1980, 2023),
            x="year",
            y="value",
            x_label="Year",
            y_label="Income Share (%)",
            x_format="year",
            y_format="percent_raw",
            color="country",
        ),
    ]


def get_beyond_growth_chart_specs() -> list[ChartSpec]:
    """Define all Beyond Growth article charts."""
    return [
        # Part I: The Growth Imperative - exponential growth visualization
        ChartSpec(
            chart_id="bg-world-gdp-exponential",
            chart_type=ChartType.LINE,
            title="World GDP: Exponential Growth (1960-2023)",
            data_source=load_world_gdp_growth_long_term,
            x="year",
            y="value",
            x_label="Year",
            y_label="GDP (Current US$)",
            x_format="year",
            y_format="trillions",
        ),
        # Part III: The Extraction Machine - emissions by income group
        ChartSpec(
            chart_id="bg-emissions-by-income",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="Carbon Inequality: Emissions by Income Group (2020)",
            data_source=lambda: load_emissions_by_income_group(2020),
            x="entity_name",
            y="value",
            x_label="Income Group",
            y_label="GHG Emissions (tonnes CO2e/capita)",
        ),
        # Marimekko: bar height = population share, bar width = emissions share
        # Non-overlapping groups that sum to 100% on both dimensions
        ChartSpec(
            chart_id="bg-carbon-inequality",
            chart_type=ChartType.MARIMEKKO,
            title="Who Causes Climate Change? Emissions vs Population Share",
            data_source=load_carbon_inequality_proper,
            x="width_share",
            y="height_share",
            x_label="Share of Global Emissions (%)",
            y_label="Share of World Population (%)",
        ),
        # Emissions per capita ratio - shows magnitude of inequality
        ChartSpec(
            chart_id="bg-emissions-ratio",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="Emissions Per Capita: Times Above Fair Share",
            data_source=load_emissions_per_capita_ratio,
            x="group",
            y="times_fair_share",
            x_label="Population Group",
            y_label="Times Fair Share",
        ),
        # Cumulative historical emissions by region
        ChartSpec(
            chart_id="bg-cumulative-emissions",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="Historical Responsibility: Cumulative CO2 Emissions (1990-2020)",
            data_source=load_cumulative_emissions_by_region,
            x="region",
            y="cumulative_emissions",
            x_label="Region",
            y_label="Cumulative CO2 (Mt)",
            y_format="thousands",
        ),
        # Part IV: Hitting the Ceiling - resource depletion
        ChartSpec(
            chart_id="bg-resource-depletion",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="Natural Resources Depletion by Income Group (2020)",
            data_source=lambda: load_resource_depletion_by_income_group(2020),
            x="entity_name",
            y="value",
            x_label="Income Group",
            y_label="Resource Depletion (% of GNI)",
            y_format="percent_raw",
        ),
        # Part V: Drawing the Doughnut - true wealth (adjusted net savings)
        ChartSpec(
            chart_id="bg-adjusted-net-savings",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="Genuine Wealth Creation: Adjusted Net Savings (2020)",
            data_source=lambda: load_adjusted_net_savings_by_income_group(2020),
            x="entity_name",
            y="value",
            x_label="Income Group",
            y_label="Adjusted Net Savings (% of GNI)",
            y_format="percent_raw",
        ),
        # NEW: GDP threshold analysis - shows where gains plateau
        ChartSpec(
            chart_id="bg-gdp-threshold",
            chart_type=ChartType.BAR,
            title="The Threshold: Life Expectancy by GDP Level",
            data_source=load_gdp_threshold_analysis,
            x="gdp_range",
            y="avg_life_expectancy",
            x_label="GDP Per Capita Range",
            y_label="Average Life Expectancy (Years)",
        ),
        # Part VI: Diminishing returns scatter plot
        ChartSpec(
            chart_id="bg-life-expectancy-diminishing",
            chart_type=ChartType.SCATTER,
            title="Diminishing Returns: Life Expectancy vs GDP (2022)",
            data_source=lambda: load_life_expectancy_vs_gdp_all(2022),
            x="gdp_per_capita",
            y="life_expectancy",
            x_label="GDP Per Capita (US$)",
            y_label="Life Expectancy (Years)",
            x_format="thousands",
        ),
        # NEW: Most efficient countries (high wellbeing, low footprint)
        ChartSpec(
            chart_id="bg-efficiency-leaders",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="Most Efficient: Life Expectancy Per Unit Emissions",
            data_source=load_high_wellbeing_low_footprint,
            x="country",
            y="efficiency",
            x_label="Country",
            y_label="Life Expectancy / Emissions Ratio",
        ),
        # Part VII: Buen Vivir - Latin America
        ChartSpec(
            chart_id="bg-latin-america-gini",
            chart_type=ChartType.LINE,
            title="Inequality in Latin America: Gini Coefficient (2000-2022)",
            data_source=lambda: load_latin_america_gini_timeseries(2000, 2022),
            x="year",
            y="value",
            x_label="Year",
            y_label="Gini Coefficient",
            x_format="year",
            color="country",
        ),
        # Part X: Economy We Need - wellbeing efficiency
        ChartSpec(
            chart_id="bg-wellbeing-vs-footprint",
            chart_type=ChartType.SCATTER,
            title="Wellbeing Efficiency: Life Expectancy vs Emissions (2020)",
            data_source=lambda: load_wellbeing_vs_footprint(2020),
            x="emissions_per_capita",
            y="life_expectancy",
            x_label="GHG Emissions (tonnes CO2e/capita)",
            y_label="Life Expectancy (Years)",
        ),
        # Part XI: Objections - adjusted savings over time
        ChartSpec(
            chart_id="bg-adjusted-savings-timeseries",
            chart_type=ChartType.LINE,
            title="Genuine Savings: Rich vs Poor Countries (1990-2022)",
            data_source=lambda: load_adjusted_savings_timeseries(
                ["USA", "DEU", "NGA", "BGD", "CHN", "IND"], 1990, 2022
            ),
            x="year",
            y="value",
            x_label="Year",
            y_label="Adjusted Net Savings (% of GNI)",
            x_format="year",
            y_format="percent_raw",
            color="country",
        ),
        # Top 10% income share comparison
        ChartSpec(
            chart_id="bg-inequality-trends",
            chart_type=ChartType.LINE,
            title="Rising Inequality: Top 10% Income Share",
            data_source=lambda: load_top10_income_share_timeseries(
                ["USA", "GBR", "FRA", "DEU"], 1980, 2022
            ),
            x="year",
            y="value",
            x_label="Year",
            y_label="Income Share of Top 10% (%)",
            x_format="year",
            y_format="percent_raw",
            color="country",
        ),
    ]


def get_baseball_chart_specs() -> list[ChartSpec]:
    """Define all baseball article charts."""
    loader = get_baseball_loader()

    return [
        # Career Leaders
        ChartSpec(
            chart_id="bb-career-home-runs",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="All-Time Home Run Leaders",
            data_source=lambda: loader.career_home_run_leaders(15),
            x="player",
            y="home_runs",
            x_label="Player",
            y_label="Home Runs",
        ),
        ChartSpec(
            chart_id="bb-career-batting-avg",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="All-Time Batting Average Leaders (min 3,000 AB)",
            data_source=lambda: loader.career_batting_average_leaders(3000, 15),
            x="player",
            y="batting_avg",
            x_label="Player",
            y_label="Batting Average",
        ),
        ChartSpec(
            chart_id="bb-career-wins",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="All-Time Pitching Wins Leaders",
            data_source=lambda: loader.career_wins_leaders(15),
            x="player",
            y="wins",
            x_label="Player",
            y_label="Wins",
        ),
        ChartSpec(
            chart_id="bb-career-strikeouts",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="All-Time Strikeout Leaders (Pitchers)",
            data_source=lambda: loader.career_strikeout_leaders(15),
            x="player",
            y="strikeouts",
            x_label="Player",
            y_label="Strikeouts",
        ),

        # Era Analysis
        ChartSpec(
            chart_id="bb-era-batting",
            chart_type=ChartType.BAR,
            title="Batting Through the Ages: League Batting Average by Era",
            data_source=loader.league_batting_by_era,
            x="era",
            y="avg_batting_avg",
            x_label="Era",
            y_label="League Batting Average",
        ),
        ChartSpec(
            chart_id="bb-era-strikeouts",
            chart_type=ChartType.BAR,
            title="The Strikeout Explosion: K Rate by Era",
            data_source=loader.league_batting_by_era,
            x="era",
            y="avg_k_pct",
            x_label="Era",
            y_label="Strikeout Rate (%)",
            y_format="percent_raw",
        ),

        # Historical Trends
        ChartSpec(
            chart_id="bb-home-run-evolution",
            chart_type=ChartType.LINE,
            title="The Power Revolution: Home Runs per Team (1901-2019)",
            data_source=loader.home_run_evolution,
            x="year",
            y="hr_per_team",
            x_label="Year",
            y_label="Home Runs per Team",
            x_format="year",
        ),
        ChartSpec(
            chart_id="bb-strikeout-evolution",
            chart_type=ChartType.LINE,
            title="The Three True Outcomes: Strikeout Rate (1901-2019)",
            data_source=loader.strikeout_evolution,
            x="year",
            y="k_rate",
            x_label="Year",
            y_label="Strikeout Rate (%)",
            x_format="year",
            y_format="percent_raw",
        ),
        ChartSpec(
            chart_id="bb-complete-game-decline",
            chart_type=ChartType.LINE,
            title="The Death of the Complete Game (1901-2019)",
            data_source=loader.complete_game_decline,
            x="year",
            y="cg_pct",
            x_label="Year",
            y_label="Complete Game Rate (%)",
            x_format="year",
            y_format="percent_raw",
        ),

        # Salary Analysis
        ChartSpec(
            chart_id="bb-salary-growth",
            chart_type=ChartType.LINE,
            title="The Money Era: Average Salary Growth (1985-2016)",
            data_source=loader.salary_growth,
            x="year",
            y="avg_salary",
            x_label="Year",
            y_label="Average Salary ($)",
            x_format="year",
            y_format="millions",
        ),
        ChartSpec(
            chart_id="bb-top-salaries-2016",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="Highest Paid Players (2016)",
            data_source=lambda: loader.top_salaries_by_year(2016, 10),
            x="player",
            y="salary",
            x_label="Player",
            y_label="Salary ($)",
            y_format="millions",
        ),

        # Team Analysis
        ChartSpec(
            chart_id="bb-franchise-wins",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="Winningest Franchises of All Time",
            data_source=lambda: loader.franchise_wins_all_time(15),
            x="franchise",
            y="total_wins",
            x_label="Franchise",
            y_label="Total Wins",
        ),
        ChartSpec(
            chart_id="bb-dynasty-teams",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="100-Win Seasons: Dynasty Teams",
            data_source=lambda: loader.dynasty_teams(105),
            x="team",
            y="wins",
            x_label="Team (Year)",
            y_label="Wins",
        ),

        # Manager Analysis
        ChartSpec(
            chart_id="bb-manager-wins",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="Greatest Managers: Career Wins",
            data_source=lambda: loader.manager_career_wins(15),
            x="manager",
            y="wins",
            x_label="Manager",
            y_label="Career Wins",
        ),

        # League-wide yearly trends
        ChartSpec(
            chart_id="bb-yearly-batting-avg",
            chart_type=ChartType.LINE,
            title="League Batting Average Over Time (1901-2019)",
            data_source=lambda: loader.yearly_league_batting(1901, 2019),
            x="year",
            y="batting_avg",
            x_label="Year",
            y_label="League Batting Average",
            x_format="year",
        ),
        ChartSpec(
            chart_id="bb-yearly-era",
            chart_type=ChartType.LINE,
            title="League ERA Over Time (1901-2019)",
            data_source=lambda: loader.yearly_league_pitching(1901, 2019),
            x="year",
            y="era",
            x_label="Year",
            y_label="League ERA",
            x_format="year",
        ),
    ]


def get_marx_chart_specs() -> list[ChartSpec]:
    """Define all Marx retrospective article charts."""
    return [
        # Income Inequality - US Top 10% share over time
        ChartSpec(
            chart_id="marx-us-top10-share",
            chart_type=ChartType.LINE,
            title="The Return of the Rentier: US Top 10% Income Share",
            data_source=load_us_inequality_timeline,
            x="year",
            y="top_10_share",
            x_label="Year",
            y_label="Income Share (%)",
            x_format="year",
            y_format="percent_raw",
        ),
        # Financialization - US financial sector as % of GDP
        ChartSpec(
            chart_id="marx-us-financialization",
            chart_type=ChartType.LINE,
            title="The Rise of Finance Capital: US Financial Sector Credit",
            data_source=load_us_financialization,
            x="year",
            y="financial_sector_pct",
            x_label="Year",
            y_label="Credit (% of GDP)",
            x_format="year",
            y_format="percent_raw",
        ),
        # Structural transformation - Manufacturing vs Services
        ChartSpec(
            chart_id="marx-us-sectors",
            chart_type=ChartType.LINE,
            title="The Hollow Economy: US Manufacturing vs Services",
            data_source=load_us_sector_transformation,
            x="year",
            y="value",
            color="sector",
            x_label="Year",
            y_label="Share of GDP (%)",
            x_format="year",
            y_format="percent_raw",
        ),
        # World GDP growth - crisis cycles
        ChartSpec(
            chart_id="marx-crisis-cycles",
            chart_type=ChartType.BAR,
            title="Capitalism's Heartbeat: World GDP Growth (1961-2023)",
            data_source=load_world_gdp_growth,
            x="year",
            y="growth_rate",
            x_label="Year",
            y_label="Annual Growth (%)",
            x_format="year",
            y_format="percent_raw",
        ),
        # Global inequality comparison
        ChartSpec(
            chart_id="marx-global-gini",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="Global Inequality: Countries by Gini Coefficient",
            data_source=lambda: load_global_inequality_comparison().head(15),
            x="short_name",
            y="gini",
            x_label="Country",
            y_label="Gini Index",
        ),
        # Unemployment - reserve army of labor
        ChartSpec(
            chart_id="marx-unemployment",
            chart_type=ChartType.LINE,
            title="The Reserve Army: Unemployment Across Europe",
            data_source=lambda: load_unemployment_rate(
                countries=["ESP", "GRC", "FRA", "DEU", "GBR"],
                start_year=1991,
                end_year=2023
            ),
            x="year",
            y="value",
            color="short_name",
            x_label="Year",
            y_label="Unemployment Rate (%)",
            x_format="year",
            y_format="percent_raw",
        ),
        # Capital formation - investment patterns
        ChartSpec(
            chart_id="marx-capital-formation",
            chart_type=ChartType.LINE,
            title="The Reproduction of Capital: Investment as % of GDP",
            data_source=lambda: load_capital_formation(
                countries=["USA", "CHN", "DEU", "JPN"],
                start_year=1970,
                end_year=2023
            ),
            x="year",
            y="value",
            color="short_name",
            x_label="Year",
            y_label="Gross Fixed Capital Formation (% of GDP)",
            x_format="year",
            y_format="percent_raw",
        ),
        # Manufacturing decline across countries
        ChartSpec(
            chart_id="marx-manufacturing-decline",
            chart_type=ChartType.LINE,
            title="The Great Hollowing: Manufacturing as % of GDP",
            data_source=lambda: load_manufacturing_share(
                countries=["USA", "GBR", "DEU", "CHN"],
                start_year=1970,
                end_year=2023
            ),
            x="year",
            y="value",
            color="short_name",
            x_label="Year",
            y_label="Manufacturing (% of GDP)",
            x_format="year",
            y_format="percent_raw",
        ),
    ]


def get_sabermetrics_chart_specs() -> list[ChartSpec]:
    """Define all Sabermetrics Pioneers article charts."""
    return [
        # Home run evolution - shows game transformation
        ChartSpec(
            chart_id="saber-hr-evolution",
            chart_type=ChartType.LINE,
            title="The Long Ball Era: Home Runs Per Game (1901-2019)",
            data_source=load_home_run_evolution,
            x="year_id",
            y="hr_per_game",
            x_label="Year",
            y_label="Home Runs Per Game",
            x_format="year",
        ),
        # Batting average evolution - Dead Ball to Modern
        ChartSpec(
            chart_id="saber-batting-avg",
            chart_type=ChartType.LINE,
            title="The Hitter's Game: League Batting Average (1901-2019)",
            data_source=load_batting_average_evolution,
            x="year_id",
            y="league_avg",
            x_label="Year",
            y_label="League Batting Average",
            x_format="year",
        ),
        # Strikeout/Walk evolution - Three True Outcomes
        ChartSpec(
            chart_id="saber-k-bb-rates",
            chart_type=ChartType.LINE,
            title="The Strikeout Revolution: K% and BB% (1901-2019)",
            data_source=lambda: load_strikeout_walk_evolution().melt(
                id_vars=['year_id'],
                value_vars=['k_rate', 'bb_rate'],
                var_name='stat_type',
                value_name='rate'
            ).replace({'k_rate': 'Strikeout Rate', 'bb_rate': 'Walk Rate'}),
            x="year_id",
            y="rate",
            color="stat_type",
            x_label="Year",
            y_label="Rate (%)",
            x_format="year",
        ),
        # Stolen base evolution
        ChartSpec(
            chart_id="saber-stolen-bases",
            chart_type=ChartType.LINE,
            title="The Running Game: Stolen Bases Per Game (1920-2019)",
            data_source=load_stolen_base_evolution,
            x="year_id",
            y="sb_per_game",
            x_label="Year",
            y_label="Stolen Bases Per Game",
            x_format="year",
        ),
        # Runs Created historical accuracy
        ChartSpec(
            chart_id="saber-runs-created-accuracy",
            chart_type=ChartType.LINE,
            title="Bill James Was Right: Runs Created Formula Accuracy (1901-2019)",
            data_source=load_runs_created_historical,
            x="year_id",
            y="accuracy_pct",
            x_label="Year",
            y_label="Prediction Accuracy (%)",
            x_format="year",
        ),
        # Pythagorean validation scatter plot
        ChartSpec(
            chart_id="saber-pythagorean-scatter",
            chart_type=ChartType.SCATTER,
            title="Pythagorean Expectation: Predicted vs Actual Wins (2015-2019)",
            data_source=lambda: load_pythagorean_validation(2015, 2019),
            x="expected_wins",
            y="wins",
            x_label="Pythagorean Expected Wins",
            y_label="Actual Wins",
        ),
        # Pythagorean outliers - lucky/unlucky teams
        ChartSpec(
            chart_id="saber-pythagorean-outliers",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="Luck vs Skill: Greatest Pythagorean Over/Underperformers",
            data_source=lambda: load_pythagorean_outliers().assign(
                label=lambda df: df['year_id'].astype(str) + ' ' + df['name']
            ).nlargest(10, 'pythagorean_diff'),
            x="label",
            y="pythagorean_diff",
            x_label="Team-Season",
            y_label="Wins Over Expected",
        ),
        # Runs Created vs Actual (bar comparison for 2019)
        ChartSpec(
            chart_id="saber-runs-created-2019",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="Runs Created vs Actual Runs (2019 Season)",
            data_source=lambda: load_runs_created_validation(2019).head(15),
            x="name",
            y="rc_error",
            x_label="Team",
            y_label="Actual - Predicted Runs",
        ),
    ]


def get_education_chart_specs() -> list[ChartSpec]:
    """Define all Education article charts."""
    return [
        # Learning Styles Myth - Effect Sizes
        ChartSpec(
            chart_id="edu-learning-styles-effect",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="The Learning Styles Myth: Effect Size Essentially Zero",
            data_source=load_learning_styles_meta_analysis,
            x="study",
            y="effect_size_d",
            x_label="Study",
            y_label="Effect Size (Cohen's d)",
        ),
        # Learning Styles Belief Rates
        ChartSpec(
            chart_id="edu-learning-styles-belief",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="The Persistence of a Myth: Educators Who Believe in Learning Styles",
            data_source=load_learning_styles_belief_rates,
            x="population",
            y="belief_rate",
            x_label="Population",
            y_label="Belief Rate (%)",
            y_format="percent_raw",
        ),
        # PISA Math Scores Over Time
        ChartSpec(
            chart_id="edu-pisa-math-trends",
            chart_type=ChartType.LINE,
            title="PISA Mathematics: The Rise and Fall of Nations (2003-2022)",
            data_source=load_pisa_math_scores_over_time,
            x="year",
            y="math_score",
            color="country",
            x_label="Year",
            y_label="PISA Math Score",
            x_format="year",
        ),
        # PISA 2022 Top 20 Rankings
        ChartSpec(
            chart_id="edu-pisa-2022-rankings",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="PISA 2022 Mathematics: Top 20 Countries",
            data_source=load_pisa_2022_rankings,
            x="country",
            y="math_score",
            x_label="Country",
            y_label="Math Score",
        ),
        # Finland Decline
        ChartSpec(
            chart_id="edu-finland-decline",
            chart_type=ChartType.LINE,
            title="The Fall of Finland: From First to Twentieth (2000-2022)",
            data_source=load_finland_decline,
            x="year",
            y="score",
            color="subject",
            x_label="Year",
            y_label="PISA Score",
            x_format="year",
        ),
        # Spending vs Outcomes
        ChartSpec(
            chart_id="edu-spending-vs-outcomes",
            chart_type=ChartType.SCATTER,
            title="Money Can't Buy Test Scores: Spending vs PISA Math (2022)",
            data_source=load_spending_vs_outcomes,
            x="spending_per_pupil_usd",
            y="pisa_math_2022",
            x_label="Spending Per Pupil (USD)",
            y_label="PISA Math Score",
            x_format="thousands",
        ),
        # US State Spending
        ChartSpec(
            chart_id="edu-us-state-spending",
            chart_type=ChartType.SCATTER,
            title="US States: No Correlation Between Spending and Achievement",
            data_source=load_us_state_spending_outcomes,
            x="spending_per_pupil",
            y="naep_math_8th_grade",
            x_label="Spending Per Pupil (USD)",
            y_label="NAEP 8th Grade Math",
            x_format="thousands",
        ),
        # Homework Effect by Grade
        ChartSpec(
            chart_id="edu-homework-effect",
            chart_type=ChartType.BAR,
            title="The Homework Question: Effect Size by Grade Level",
            data_source=load_homework_effect_by_grade,
            x="grade_band",
            y="correlation_with_achievement",
            x_label="Grade Level",
            y_label="Correlation with Achievement",
        ),
        # Effect Size Comparison - What Actually Works
        ChartSpec(
            chart_id="edu-effect-size-comparison",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="What Actually Works: Educational Interventions Ranked by Effect Size",
            data_source=load_effect_size_comparison,
            x="intervention",
            y="effect_size_d",
            x_label="Intervention",
            y_label="Effect Size (Cohen's d)",
        ),
    ]


def get_ncaa_basketball_chart_specs() -> list[ChartSpec]:
    """Define all NCAA Basketball / March Madness article charts."""
    return [
        # First Round Upset Rates by Matchup
        ChartSpec(
            chart_id="ncaa-first-round-upsets",
            chart_type=ChartType.BAR,
            title="First Round Upset Rates by Seed Matchup (1985-2024)",
            data_source=load_first_round_upset_rates,
            x="matchup",
            y="upset_rate_pct",
            x_label="Matchup",
            y_label="Upset Rate (%)",
        ),
        # Seed Advancement Rates
        ChartSpec(
            chart_id="ncaa-seed-advancement",
            chart_type=ChartType.LINE,
            title="How Far Each Seed Advances (1985-2024)",
            data_source=lambda: load_seed_advancement_rates().melt(
                id_vars=["seed"],
                value_vars=["round_of_32_pct", "sweet_16_pct", "elite_8_pct", "final_four_pct"],
                var_name="round",
                value_name="advancement_pct"
            ),
            x="seed",
            y="advancement_pct",
            color="round",
            x_label="Seed",
            y_label="Advancement Rate (%)",
        ),
        # Model Accuracy Comparison
        ChartSpec(
            chart_id="ncaa-model-accuracy",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="Prediction Model Accuracy: The 73% Ceiling",
            data_source=load_model_accuracy_comparison,
            x="model",
            y="accuracy_pct",
            x_label="Model",
            y_label="Accuracy (%)",
        ),
        # KenPom vs Seed Success - show when KenPom disagrees with seed, who wins
        ChartSpec(
            chart_id="ncaa-kenpom-vs-seed",
            chart_type=ChartType.BAR,
            title="When Analytics Disagree with Seeds: KenPom Advantage",
            data_source=load_kenpom_vs_seed_success,
            x="round",
            y="when_disagree_kenpom_better",
            x_label="Tournament Round",
            y_label="KenPom Pick Wins When Disagrees (%)",
        ),
        # 1-Seed Strength History
        ChartSpec(
            chart_id="ncaa-one-seed-strength",
            chart_type=ChartType.LINE,
            title="Strength of 1-Seeds Over Time (AdjEM)",
            data_source=load_one_seed_strength_history,
            x="year",
            y="avg_adj_em",
            x_label="Year",
            y_label="Average Adjusted Efficiency Margin",
            x_format="year",
        ),
        # Upset Totals by Underdog Seed
        ChartSpec(
            chart_id="ncaa-upset-totals",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="Total Upset Wins by Underdog Seed (1985-2024)",
            data_source=load_upset_totals_by_seed,
            x="seed",
            y="total_upset_wins",
            x_label="Seed",
            y_label="Total Upset Wins",
        ),
        # Volatility Factors
        ChartSpec(
            chart_id="ncaa-volatility-factors",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="Factors That Increase Upset Probability",
            data_source=load_volatility_factors,
            x="factor",
            y="upset_rate_increase_pct",
            x_label="Factor",
            y_label="Upset Rate Increase (%)",
        ),
        # Champion Profile
        ChartSpec(
            chart_id="ncaa-champion-profile",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="What Do Champions Have in Common? (2002-2024)",
            data_source=load_champion_profile,
            x="metric",
            y="percentage",
            x_label="Criterion",
            y_label="Champions Meeting Criterion (%)",
        ),
        # Transfer Portal Era
        ChartSpec(
            chart_id="ncaa-transfer-portal",
            chart_type=ChartType.LINE,
            title="The Transfer Portal Era: Roster Turnover Over Time",
            data_source=load_transfer_portal_era,
            x="year",
            y="avg_portal_players_per_team",
            x_label="Year",
            y_label="Average Transfer Players per Team",
            x_format="year",
        ),
    ]


def render_altair(specs: list[ChartSpec]) -> int:
    """Render charts using Altair."""
    from charts.altair_renderer import AltairRenderer

    print("\n" + "=" * 60)
    print("ALTAIR RENDERER (Python)")
    print("=" * 60)

    OUTPUT_DIR_ALTAIR.mkdir(parents=True, exist_ok=True)
    renderer = AltairRenderer()

    success_count = 0
    for spec in specs:
        try:
            print(f"\n  Rendering: {spec.chart_id}")
            renderer.save(spec, OUTPUT_DIR_ALTAIR, formats=["svg", "png"])
            success_count += 1
        except Exception as e:
            print(f"  [ERROR] {spec.chart_id}: {e}")

    print(f"\n  Altair: {success_count}/{len(specs)} charts generated")
    return success_count


def export_specs_for_plot(specs: list[ChartSpec]) -> None:
    """Export chart specs as JSON for TypeScript renderer."""
    SPECS_DIR.mkdir(parents=True, exist_ok=True)

    manifest = []
    for spec in specs:
        # Write individual spec file
        spec_path = SPECS_DIR / f"{spec.chart_id}.json"
        with open(spec_path, 'w') as f:
            f.write(spec.to_json())

        manifest.append({
            "chartId": spec.chart_id,
            "specFile": f"{spec.chart_id}.json",
        })

    # Write manifest
    manifest_path = SPECS_DIR / "manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f"\n  Exported {len(specs)} specs to {SPECS_DIR}")


def render_plot() -> int:
    """Render charts using Observable Plot (via Node.js)."""
    print("\n" + "=" * 60)
    print("OBSERVABLE PLOT RENDERER (TypeScript)")
    print("=" * 60)

    script_path = PROJECT_ROOT / "site" / "scripts" / "generate-plot-charts.ts"

    try:
        result = subprocess.run(
            ["node", "--experimental-strip-types", str(script_path)],
            cwd=PROJECT_ROOT / "site",
            capture_output=True,
            text=True,
        )
        print(result.stdout)
        if result.returncode != 0:
            print(f"  [ERROR] {result.stderr}")
            return 0
        return 1  # Success indicator
    except Exception as e:
        print(f"  [ERROR] Failed to run Plot renderer: {e}")
        return 0


def main():
    parser = argparse.ArgumentParser(description="Generate charts with dual packages")
    parser.add_argument(
        "--renderer",
        choices=["all", "altair", "plot"],
        default="all",
        help="Which renderer(s) to use",
    )
    args = parser.parse_args()

    print("Dual-Package Chart Generation")
    print("==============================")
    print("Renderers: Altair (Python) + Observable Plot (TypeScript)")

    # Combine all chart specs
    gdp_specs = get_gdp_chart_specs()
    beyond_growth_specs = get_beyond_growth_chart_specs()
    baseball_specs = get_baseball_chart_specs()
    marx_specs = get_marx_chart_specs()
    sabermetrics_specs = get_sabermetrics_chart_specs()
    education_specs = get_education_chart_specs()
    ncaa_basketball_specs = get_ncaa_basketball_chart_specs()
    specs = gdp_specs + beyond_growth_specs + baseball_specs + marx_specs + sabermetrics_specs + education_specs + ncaa_basketball_specs

    print(f"\nFound {len(specs)} chart specifications")
    print(f"  - GDP article: {len(gdp_specs)} charts")
    print(f"  - Beyond Growth article: {len(beyond_growth_specs)} charts")
    print(f"  - Baseball article: {len(baseball_specs)} charts")
    print(f"  - Marx article: {len(marx_specs)} charts")
    print(f"  - Sabermetrics article: {len(sabermetrics_specs)} charts")
    print(f"  - Education article: {len(education_specs)} charts")
    print(f"  - NCAA Basketball article: {len(ncaa_basketball_specs)} charts")

    # Export specs for TypeScript (always needed for Plot)
    export_specs_for_plot(specs)

    altair_count = 0
    plot_count = 0

    if args.renderer in ["all", "altair"]:
        altair_count = render_altair(specs)

    if args.renderer in ["all", "plot"]:
        plot_count = render_plot()

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    if args.renderer in ["all", "altair"]:
        print(f"  Altair:         {altair_count} charts → {OUTPUT_DIR_ALTAIR}")
    if args.renderer in ["all", "plot"]:
        print(f"  Observable Plot: see output above → {OUTPUT_DIR_PLOT}")
    print()


if __name__ == "__main__":
    main()
