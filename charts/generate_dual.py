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
    # Original loaders
    load_learning_styles_meta_analysis,
    load_learning_styles_belief_rates,
    load_pisa_math_scores_over_time,
    load_pisa_2022_rankings,
    load_finland_decline,
    load_spending_vs_outcomes,
    load_us_state_spending_outcomes,
    load_homework_effect_by_grade,
    load_effect_size_comparison,
    # Texas education
    load_texas_school_types,
    load_texas_district_performance,
    load_waco_schools_detail,
    load_texas_staar_trends,
    load_waco_staar_trends,
    load_staar_by_demographics,
    # School choice
    load_voucher_academic_effects,
    load_voucher_participation,
    load_charter_outcomes_credo,
    load_private_public_comparison,
    load_selection_bias_evidence,
    # Teacher compensation
    load_teacher_salary_by_state,
    load_texas_teacher_trends,
    # NAEP trends
    load_naep_reading_trends,
    load_naep_math_trends,
    load_naep_achievement_gaps,
    # Life outcomes
    load_education_earnings,
    load_education_outcomes_age25,
    load_early_childhood_roi,
    # School funding
    load_texas_funding_by_district,
    load_national_funding_comparison,
    # Alternative pathways
    load_dual_credit_outcomes,
    load_ged_vs_diploma,
    load_trade_school_outcomes,
    # Science of reading
    load_reading_instruction_research,
    # ML predictions
    predict_district_performance,
    predict_school_choice_migration,
    predict_literacy_rates,
    predict_failing_schools,
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
from charts.cubs_2016.data import (
    load_cubs_rebuild_arc,
    load_key_acquisitions_war,
    load_epstein_trades_analysis,
    load_draft_pick_outcomes,
    load_woba_2016,
    load_fip_vs_era_2016,
    load_leverage_index_2016,
    load_tango_metrics_2016,
    load_championship_window_comparison,
    load_what_went_wrong,
    load_arrieta_transformation,
    load_hendricks_value,
    load_war_prediction_model,
)
from charts.boomcession.data import (
    load_sentiment_by_president,
    load_gdp_sentiment_correlation,
    load_gdp_sentiment_scatter,
    load_productivity_wages,
    load_housing_affordability,
    load_corporate_profits_pct,
    load_labor_share,
    load_nondiscretionary_spending,
    load_consumer_spending_by_income,
    load_welfare_comparison,
)
from charts.blood_money.data import (
    # Core military and tax data
    get_us_military_tax_share,
    get_global_military_spending,
    get_top_military_spenders,
    get_us_war_costs,
    get_us_military_spending_history,
    get_median_taxpayer_contribution,
    # Drone strike data
    get_drone_strikes_by_year,
    get_drone_strikes_by_year_total,
    get_drone_casualties_by_country,
    get_drone_casualties_by_president,
    # Historical atrocities
    get_historical_democide,
    get_democide_timeline,
    get_democide_by_century,
    get_famine_deaths,
    # Post-9/11 wars
    get_post_911_deaths,
    get_defense_contractors,
    get_afghanistan_costs_by_year,
    get_iraq_costs_by_year,
    get_cumulative_war_costs,
    get_veterans_cost_projection,
    get_interest_on_war_debt,
    # Tax and inequality
    get_tax_structure_comparison,
    get_income_inequality_trends,
    # Conflict data
    get_conflict_deaths_by_year,
    get_civilian_combatant_ratio,
    # Foreign military support
    get_military_aid_israel,
    get_yemen_casualties,
    get_gaza_casualties,
    get_ukraine_aid,
    # Comparative analysis
    get_cost_per_death_comparison,
    get_gdp_vs_military_spending,
    get_military_spending_by_president,
    get_cold_war_spending_eras,
    get_central_america_deaths,
    # Moral/political
    get_war_tax_resistance_history,
    get_antiwar_protest_sizes,
    get_public_opinion_wars,
    get_spending_by_party,
    # Lifetime taxpayer analysis
    get_taxpayer_cumulative_contribution,
    get_deaths_per_taxpayer,
    # Chapter 1: Accounting of Death
    get_deaths_by_type_20c,
    get_ucdp_vs_rummel_comparison,
    get_direct_indirect_ratio,
    get_death_counting_methods,
    get_conflict_deaths_trends,
    get_civilian_military_deaths,
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
        # =====================================================================
        # TEXAS EDUCATION CHARTS
        # =====================================================================
        # Texas School Types Distribution
        ChartSpec(
            chart_id="edu-texas-school-types",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="Texas Students by School Type (2024)",
            data_source=load_texas_school_types,
            x="school_type",
            y="pct_of_total",
            x_label="School Type",
            y_label="% of Students",
        ),
        # Texas District Performance
        ChartSpec(
            chart_id="edu-texas-districts",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="Texas District Accountability Scores (2024)",
            data_source=load_texas_district_performance,
            x="district",
            y="accountability_score",
            x_label="District",
            y_label="Accountability Score",
        ),
        # Waco Schools Detail
        ChartSpec(
            chart_id="edu-waco-schools",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="Waco ISD Schools: Accountability Scores (2024)",
            data_source=load_waco_schools_detail,
            x="school",
            y="overall_score",
            x_label="School",
            y_label="Overall Score",
        ),
        # Texas STAAR Trends
        ChartSpec(
            chart_id="edu-texas-staar-trends",
            chart_type=ChartType.LINE,
            title="Texas STAAR Performance: Reading & Math (2015-2024)",
            data_source=load_texas_staar_trends,
            x="year",
            y="reading_meets",
            x_label="Year",
            y_label="% Meets Grade Level",
            x_format="year",
        ),
        # Waco vs State STAAR
        ChartSpec(
            chart_id="edu-waco-staar-gap",
            chart_type=ChartType.LINE,
            title="Waco ISD vs State Average: Persistent Gap",
            data_source=load_waco_staar_trends,
            x="year",
            y="gap",
            x_label="Year",
            y_label="Gap (Waco - State)",
            x_format="year",
        ),
        # STAAR by Demographics
        ChartSpec(
            chart_id="edu-staar-demographics",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="STAAR Reading Performance by Demographic (2024)",
            data_source=load_staar_by_demographics,
            x="demographic",
            y="reading_meets",
            x_label="Demographic Group",
            y_label="% Meets Grade Level",
        ),
        # =====================================================================
        # VOUCHER AND SCHOOL CHOICE CHARTS
        # =====================================================================
        # Voucher Academic Effects
        ChartSpec(
            chart_id="edu-voucher-effects",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="Voucher Program Effects on Math Achievement",
            data_source=load_voucher_academic_effects,
            x="program",
            y="math_effect_size",
            x_label="Program",
            y_label="Effect Size (SD)",
        ),
        # Voucher Participation Demographics
        ChartSpec(
            chart_id="edu-voucher-participation",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="Voucher Recipients: % Never Attended Public School",
            data_source=load_voucher_participation,
            x="state",
            y="pct_never_public_school",
            x_label="State",
            y_label="% Never in Public School",
        ),
        # Charter Outcomes by Demographics
        ChartSpec(
            chart_id="edu-charter-outcomes",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="Charter School Effect: Days of Learning Gained in Reading",
            data_source=load_charter_outcomes_credo,
            x="student_group",
            y="reading_days_gained",
            x_label="Student Group",
            y_label="Days of Learning",
        ),
        # Private vs Public Adjusted
        ChartSpec(
            chart_id="edu-private-selection-bias",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="Private School Advantage: What Selection Bias Explains",
            data_source=load_private_public_comparison,
            x="outcome",
            y="pct_explained_by_selection",
            x_label="Outcome",
            y_label="% Explained by Selection",
        ),
        # Selection Bias Evidence
        ChartSpec(
            chart_id="edu-selection-factors",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="Selection Bias: Parental Education by School Type",
            data_source=load_selection_bias_evidence,
            x="factor",
            y="private_pct",
            x_label="Factor",
            y_label="% in Private Schools",
        ),
        # =====================================================================
        # TEACHER COMPENSATION CHARTS
        # =====================================================================
        # Teacher Salary by State
        ChartSpec(
            chart_id="edu-teacher-salary-states",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="Average Teacher Salary by State (2024)",
            data_source=load_teacher_salary_by_state,
            x="state",
            y="avg_salary",
            x_label="State",
            y_label="Average Salary ($)",
        ),
        # Texas Teacher Trends
        ChartSpec(
            chart_id="edu-texas-teacher-trends",
            chart_type=ChartType.LINE,
            title="Texas Teacher Crisis: Uncertified New Hires Rising",
            data_source=load_texas_teacher_trends,
            x="year",
            y="pct_uncertified_new_hires",
            x_label="Year",
            y_label="% Uncertified",
            x_format="year",
        ),
        # =====================================================================
        # NAEP NATIONAL TRENDS CHARTS
        # =====================================================================
        # NAEP Reading Trends
        ChartSpec(
            chart_id="edu-naep-reading",
            chart_type=ChartType.LINE,
            title="NAEP 4th Grade Reading: Declining Proficiency",
            data_source=load_naep_reading_trends,
            x="year",
            y="grade4_pct_proficient",
            x_label="Year",
            y_label="% Proficient",
            x_format="year",
        ),
        # NAEP Math Trends
        ChartSpec(
            chart_id="edu-naep-math",
            chart_type=ChartType.LINE,
            title="NAEP 4th Grade Math: Post-Pandemic Collapse",
            data_source=load_naep_math_trends,
            x="year",
            y="grade4_pct_proficient",
            x_label="Year",
            y_label="% Proficient",
            x_format="year",
        ),
        # NAEP Achievement Gaps
        ChartSpec(
            chart_id="edu-naep-gaps",
            chart_type=ChartType.LINE,
            title="NAEP Achievement Gaps: Back to 2003 Levels",
            data_source=load_naep_achievement_gaps,
            x="year",
            y="white_black_reading_g4",
            x_label="Year",
            y_label="Gap (Score Points)",
            x_format="year",
        ),
        # =====================================================================
        # EDUCATION AND LIFE OUTCOMES CHARTS
        # =====================================================================
        # Education and Earnings
        ChartSpec(
            chart_id="edu-earnings-by-level",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="Education Pays: Weekly Earnings by Attainment (2024)",
            data_source=load_education_earnings,
            x="education_level",
            y="median_weekly_earnings",
            x_label="Education Level",
            y_label="Median Weekly Earnings ($)",
        ),
        # Education Outcomes at Age 25
        ChartSpec(
            chart_id="edu-outcomes-age25",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="Life at 25: Employment Rate by Education",
            data_source=lambda: load_education_outcomes_age25().melt(
                id_vars=["outcome"], var_name="education", value_name="pct"
            ).query("outcome == 'Employed full-time'"),
            x="education",
            y="pct",
            x_label="Education Level",
            y_label="% Employed Full-Time",
        ),
        # Early Childhood ROI
        ChartSpec(
            chart_id="edu-early-childhood-roi",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="Early Childhood Programs: Return on Investment",
            data_source=load_early_childhood_roi,
            x="program",
            y="roi_ratio",
            x_label="Program",
            y_label="ROI Ratio ($ Returned per $ Spent)",
        ),
        # =====================================================================
        # SCHOOL FUNDING CHARTS
        # =====================================================================
        # Texas Funding by District Type
        ChartSpec(
            chart_id="edu-texas-funding",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="Texas Per-Pupil Funding by District Wealth",
            data_source=load_texas_funding_by_district,
            x="district_type",
            y="total_per_pupil",
            x_label="District Type",
            y_label="Per-Pupil Funding ($)",
        ),
        # National Funding Comparison
        ChartSpec(
            chart_id="edu-national-funding",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="Per-Pupil Spending: Texas vs Other States",
            data_source=load_national_funding_comparison,
            x="state",
            y="per_pupil_spending",
            x_label="State",
            y_label="Per-Pupil Spending ($)",
        ),
        # =====================================================================
        # ALTERNATIVE PATHWAYS CHARTS
        # =====================================================================
        # Dual Credit Outcomes
        ChartSpec(
            chart_id="edu-dual-credit",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="Dual Credit Advantage: College Outcomes",
            data_source=load_dual_credit_outcomes,
            x="outcome",
            y="dual_credit",
            x_label="Outcome",
            y_label="Dual Credit Students (%)",
        ),
        # GED vs Diploma
        ChartSpec(
            chart_id="edu-ged-diploma",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="GED vs High School Diploma: Earnings Gap",
            data_source=load_ged_vs_diploma,
            x="outcome",
            y="hs_diploma",
            x_label="Outcome",
            y_label="HS Diploma Value",
        ),
        # Trade School vs College
        ChartSpec(
            chart_id="edu-trade-college",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="Trade School vs Bachelor's: Time and Debt",
            data_source=load_trade_school_outcomes,
            x="metric",
            y="trade_school",
            x_label="Metric",
            y_label="Trade School Value",
        ),
        # =====================================================================
        # SCIENCE OF READING CHARTS
        # =====================================================================
        # Reading Instruction Research
        ChartSpec(
            chart_id="edu-reading-methods",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="Reading Instruction: Effect Sizes by Method",
            data_source=load_reading_instruction_research,
            x="method",
            y="effect_size",
            x_label="Method",
            y_label="Effect Size",
        ),
        # =====================================================================
        # ML PREDICTION CHARTS
        # =====================================================================
        # ML Feature Importance
        ChartSpec(
            chart_id="edu-ml-features",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="ML Model: What Predicts School Performance?",
            data_source=predict_district_performance,
            x="feature",
            y="importance",
            x_label="Feature",
            y_label="Importance",
        ),
        # School Choice Migration Predictions
        ChartSpec(
            chart_id="edu-voucher-migration",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="Predicted Enrollment Loss Under Vouchers",
            data_source=predict_school_choice_migration,
            x="district",
            y="funding_loss_millions",
            x_label="District",
            y_label="Predicted Funding Loss ($M)",
        ),
        # Literacy Rate Predictions
        ChartSpec(
            chart_id="edu-literacy-forecast",
            chart_type=ChartType.LINE,
            title="Literacy Forecast: NAEP Proficiency Trajectory",
            data_source=predict_literacy_rates,
            x="year",
            y="pct_proficient",
            x_label="Year",
            y_label="% Proficient",
            x_format="year",
        ),
        # Failing Schools Prediction Features
        ChartSpec(
            chart_id="edu-failing-prediction",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="Predicting School Failure: Key Risk Factors",
            data_source=predict_failing_schools,
            x="feature",
            y="importance",
            x_label="Risk Factor",
            y_label="Importance",
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


def get_cubs_2016_chart_specs() -> list[ChartSpec]:
    """Define all Cubs 2016 retrospective article charts."""
    return [
        # Cubs Rebuild Arc
        ChartSpec(
            chart_id="cubs-rebuild-arc",
            chart_type=ChartType.LINE,
            title="The Cubs Rebuild: Wins by Season (2011-2021)",
            data_source=load_cubs_rebuild_arc,
            x="year",
            y="wins",
            x_label="Year",
            y_label="Wins",
            x_format="year",
        ),
        # Key Acquisitions WAR
        ChartSpec(
            chart_id="cubs-acquisitions-war",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="Cubs Acquisitions: WAR Delivered (2015-2020)",
            data_source=load_key_acquisitions_war,
            x="player",
            y="cubs_war_2015_2020",
            x_label="Player",
            y_label="Wins Above Replacement",
        ),
        # Trades Net WAR
        ChartSpec(
            chart_id="cubs-trades-net-war",
            chart_type=ChartType.BAR,
            title="Epstein's Trades: Net WAR Impact",
            data_source=load_epstein_trades_analysis,
            x="trade_name",
            y="net_war",
            x_label="Trade",
            y_label="Net WAR (+ = Cubs won trade)",
        ),
        # Draft Pick Outcomes
        ChartSpec(
            chart_id="cubs-draft-outcomes",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="Cubs Draft Picks 2011-2015: Career WAR",
            data_source=lambda: load_draft_pick_outcomes().sort_values("career_war", ascending=True),
            x="player",
            y="career_war",
            x_label="Player",
            y_label="Career WAR",
        ),
        # Tango Metrics - wOBA
        ChartSpec(
            chart_id="cubs-woba-2016",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="2016 Cubs Hitters: wOBA vs League Average",
            data_source=lambda: load_woba_2016().sort_values("woba", ascending=True),
            x="player",
            y="woba",
            x_label="Player",
            y_label="wOBA",
        ),
        # Tango Metrics - FIP vs ERA (shows ERA minus FIP: negative = outperformed)
        ChartSpec(
            chart_id="cubs-fip-era-2016",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="2016 Cubs Pitchers: ERA minus FIP",
            data_source=lambda: load_fip_vs_era_2016().sort_values("era_minus_fip"),
            x="player",
            y="era_minus_fip",
            x_label="Pitcher",
            y_label="ERA - FIP (negative = better than expected)",
            options={"highlight_negative": True},
        ),
        # Tango Metrics - Leverage Index
        ChartSpec(
            chart_id="cubs-leverage-2016",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="2016 Cubs Bullpen: Average Leverage Index",
            data_source=lambda: load_leverage_index_2016().sort_values("avg_leverage", ascending=True),
            x="pitcher",
            y="avg_leverage",
            x_label="Pitcher",
            y_label="Avg Leverage Index",
        ),
        # Arrieta Transformation
        ChartSpec(
            chart_id="cubs-arrieta-transformation",
            chart_type=ChartType.LINE,
            title="Jake Arrieta: ERA by Season",
            data_source=load_arrieta_transformation,
            x="year",
            y="era",
            x_label="Year",
            y_label="ERA",
            x_format="year",
        ),
        # Hendricks Value
        ChartSpec(
            chart_id="cubs-hendricks-value",
            chart_type=ChartType.LINE,
            title="Kyle Hendricks: Acquired for Cash, Became an Ace",
            data_source=load_hendricks_value,
            x="season",
            y="war",
            x_label="Season",
            y_label="WAR",
            x_format="year",
        ),
        # What Went Wrong - Player Decline
        ChartSpec(
            chart_id="cubs-player-decline",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="The Window Closes: WAR Change 2016 to 2019",
            data_source=load_what_went_wrong,
            x="player",
            y="war_change",
            x_label="Player",
            y_label="WAR Change",
        ),
        # Championship Window Comparison - Playoff Depth by Year
        ChartSpec(
            chart_id="cubs-window-comparison",
            chart_type=ChartType.LINE,
            title="Playoff Depth: Cubs vs. Other Contenders",
            data_source=load_championship_window_comparison,
            x="year",
            y="depth",
            color="team",
            x_label="Year",
            y_label="Playoff Round Reached",
            x_format="year",
        ),
        # ML WAR Predictions - Prediction Error
        ChartSpec(
            chart_id="cubs-war-predictions",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="ML Model: WAR Prediction Error (2018-2019)",
            data_source=load_war_prediction_model,
            x="player",
            y="error",
            x_label="Player",
            y_label="Prediction Error (Predicted - Actual WAR)",
        ),
    ]


def get_blood_money_chart_specs() -> list[ChartSpec]:
    """Define all Blood Money book charts - taxpayer complicity in state violence."""
    return [
        # Chapter 1: The Predicament - US Military and Taxes
        ChartSpec(
            chart_id="bm-us-military-spending-history",
            chart_type=ChartType.LINE,
            title="US Military Spending: A Half-Century of Growth",
            data_source=get_us_military_spending_history,
            x="year",
            y="spending_billions_constant",
            x_label="Year",
            y_label="Military Spending (Billions, 2022 USD)",
            x_format="year",
        ),
        ChartSpec(
            chart_id="bm-us-military-share-of-taxes",
            chart_type=ChartType.LINE,
            title="What Share of Your Taxes Goes to the Military?",
            data_source=get_us_military_tax_share,
            x="year",
            y="military_share_of_taxes",
            x_label="Year",
            y_label="Military Share of Total Taxes (%)",
            x_format="year",
        ),
        ChartSpec(
            chart_id="bm-us-military-pct-gdp",
            chart_type=ChartType.LINE,
            title="US Military Spending as Percent of GDP",
            data_source=get_us_military_spending_history,
            x="year",
            y="pct_gdp",
            x_label="Year",
            y_label="Percent of GDP",
            x_format="year",
        ),
        ChartSpec(
            chart_id="bm-top-military-spenders",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="World's Largest Military Spenders (2024)",
            data_source=get_top_military_spenders,
            x="country",
            y="spending_billions",
            x_label="Country",
            y_label="Military Spending (Billions USD)",
        ),
        ChartSpec(
            chart_id="bm-global-military-spending",
            chart_type=ChartType.LINE,
            title="Global Military Spending Over Time",
            data_source=get_global_military_spending,
            x="year",
            y="total_trillion_constant",
            x_label="Year",
            y_label="Total Global Military Spending (Trillions USD)",
            x_format="year",
        ),
        # Chapter 1: The Accounting of Death - Methodology Charts
        ChartSpec(
            chart_id="bm-deaths-by-type-20c",
            chart_type=ChartType.BAR,
            title="20th Century Deaths by Cause",
            data_source=get_deaths_by_type_20c,
            x="category",
            y="deaths_millions",
            x_label="Type of Death",
            y_label="Deaths (Millions)",
        ),
        ChartSpec(
            chart_id="bm-ucdp-vs-rummel",
            chart_type=ChartType.SCATTER,
            title="Death Estimates: UCDP vs. Rummel (Thousands)",
            data_source=get_ucdp_vs_rummel_comparison,
            x="ucdp_estimate_thousands",
            y="rummel_estimate_thousands",
            x_label="UCDP Estimate (Thousands)",
            y_label="Rummel Estimate (Thousands)",
        ),
        ChartSpec(
            chart_id="bm-direct-indirect-ratio",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="Direct vs. Indirect Deaths in Major Conflicts",
            data_source=get_direct_indirect_ratio,
            x="conflict",
            y="total_deaths",
            x_label="Conflict",
            y_label="Total Deaths",
        ),
        ChartSpec(
            chart_id="bm-conflict-deaths-trends",
            chart_type=ChartType.LINE,
            title="Global Conflict Deaths by Decade (Millions)",
            data_source=get_conflict_deaths_trends,
            x="decade",
            y="total_deaths_millions",
            x_label="Decade",
            y_label="Deaths (Millions)",
        ),
        ChartSpec(
            chart_id="bm-civilian-military-deaths",
            chart_type=ChartType.BAR,
            title="Civilian Deaths as Percentage of Total (by Era)",
            data_source=get_civilian_military_deaths,
            x="era",
            y="civilian_pct",
            x_label="Era",
            y_label="Civilian Deaths (%)",
        ),
        # Chapter 2: The American Century - Post-9/11 Wars
        ChartSpec(
            chart_id="bm-post-911-war-costs",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="Cost of Post-9/11 Wars (Billions USD)",
            data_source=get_us_war_costs,
            x="war_zone",
            y="amount_billions",
            x_label="War Zone / Category",
            y_label="Cost (Billions USD)",
        ),
        ChartSpec(
            chart_id="bm-post-911-deaths",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="Post-9/11 War Deaths by Category",
            data_source=get_post_911_deaths,
            x="category",
            y="deaths_mid",
            x_label="Category",
            y_label="Deaths (Mid Estimate)",
            color="war_zone",
        ),
        ChartSpec(
            chart_id="bm-defense-contractors",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="Top Pentagon Contractors: Who Profits from War (2020-2024)",
            data_source=get_defense_contractors,
            x="contractor",
            y="total_2020_2024",
            x_label="Contractor",
            y_label="Contract Value (Billions USD)",
        ),
        # Chapter 3: Drone Strikes
        ChartSpec(
            chart_id="bm-drone-casualties-by-country",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="Drone Strike Casualties by Country",
            data_source=get_drone_casualties_by_country,
            x="country",
            y="killed_max",
            x_label="Country",
            y_label="Deaths (High Estimate)",
        ),
        ChartSpec(
            chart_id="bm-drone-casualties-by-president",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="Drone Strikes by President",
            data_source=get_drone_casualties_by_president,
            x="president",
            y="strikes",
            x_label="President",
            y_label="Number of Strikes",
        ),
        ChartSpec(
            chart_id="bm-drone-civilians-by-president",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="Civilian Deaths from Drone Strikes by President",
            data_source=get_drone_casualties_by_president,
            x="president",
            y="civilians_max",
            x_label="President",
            y_label="Civilian Deaths (High Estimate)",
        ),
        # Chapter 4: Historical Democide
        ChartSpec(
            chart_id="bm-historical-democide",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="Government Mass Killings in History (Millions)",
            data_source=lambda: get_historical_democide().assign(
                deaths_millions=lambda x: x['deaths_mid'] / 1e6
            ),
            x="regime_name",
            y="deaths_millions",
            x_label="Regime",
            y_label="Deaths (Millions)",
        ),
        ChartSpec(
            chart_id="bm-democide-timeline",
            chart_type=ChartType.BAR,
            title="Democide Deaths by Decade (20th Century)",
            data_source=lambda: get_democide_timeline().assign(
                deaths_millions=lambda x: x['total_deaths'] / 1e6
            ),
            x="decade",
            y="deaths_millions",
            x_label="Decade",
            y_label="Deaths (Millions)",
            x_format="year",
        ),
        # Chapter 5: Tax Structure and Inequality
        ChartSpec(
            chart_id="bm-tax-structure-comparison",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="Tax Burden by Country (% of GDP, 2020)",
            data_source=get_tax_structure_comparison,
            x="country_code",
            y="tax_to_gdp_ratio",
            x_label="Country",
            y_label="Tax Revenue (% of GDP)",
        ),
        ChartSpec(
            chart_id="bm-us-inequality-trend",
            chart_type=ChartType.LINE,
            title="Income Inequality in America (GINI Index)",
            data_source=lambda: get_income_inequality_trends().query("country_code == 'USA'"),
            x="year",
            y="gini",
            x_label="Year",
            y_label="GINI Index",
            x_format="year",
        ),
        # Chapter 6: The Median Taxpayer's Contribution
        ChartSpec(
            chart_id="bm-median-taxpayer-contribution",
            chart_type=ChartType.LINE,
            title="What the Median American Taxpayer Contributes to the Military",
            data_source=get_median_taxpayer_contribution,
            x="year",
            y="military_contribution",
            x_label="Year",
            y_label="Annual Military Contribution (USD)",
            x_format="year",
        ),
        # UCDP Conflict Deaths
        ChartSpec(
            chart_id="bm-conflict-deaths-by-year",
            chart_type=ChartType.BAR,
            title="Global Conflict Deaths by Year (UCDP)",
            data_source=get_conflict_deaths_by_year,
            x="year",
            y="deaths_best",
            x_label="Year",
            y_label="Deaths (Best Estimate)",
            x_format="year",
        ),
        # =========================================================================
        # PART I: HISTORICAL SURVEY - Additional Charts
        # =========================================================================
        ChartSpec(
            chart_id="bm-cold-war-spending-eras",
            chart_type=ChartType.BAR,
            title="US Military Spending by Cold War Era",
            data_source=get_cold_war_spending_eras,
            x="era",
            y="avg_annual_billions",
            x_label="Era",
            y_label="Average Annual Spending (Billions USD)",
        ),
        ChartSpec(
            chart_id="bm-central-america-deaths",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="US-Backed Violence in Central America (1980s)",
            data_source=get_central_america_deaths,
            x="country",
            y="deaths_high",
            x_label="Country",
            y_label="Deaths (High Estimate)",
        ),
        ChartSpec(
            chart_id="bm-democide-by-century",
            chart_type=ChartType.BAR,
            title="Democide Deaths by Century",
            data_source=get_democide_by_century,
            x="century",
            y="deaths_millions",
            x_label="Period",
            y_label="Deaths (Millions)",
        ),
        ChartSpec(
            chart_id="bm-famine-deaths",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="Major Policy-Induced Famines",
            data_source=get_famine_deaths,
            x="famine",
            y="deaths_millions",
            x_label="Famine",
            y_label="Deaths (Millions)",
        ),
        # =========================================================================
        # PART II: AMERICAN RECKONING - War Cost Charts
        # =========================================================================
        ChartSpec(
            chart_id="bm-afghanistan-costs-by-year",
            chart_type=ChartType.LINE,
            title="Afghanistan War: Annual Costs (2001-2021)",
            data_source=get_afghanistan_costs_by_year,
            x="year",
            y="spending_billions",
            x_label="Year",
            y_label="Spending (Billions USD)",
            x_format="year",
        ),
        ChartSpec(
            chart_id="bm-afghanistan-troops",
            chart_type=ChartType.LINE,
            title="Afghanistan War: Troop Levels (2001-2021)",
            data_source=get_afghanistan_costs_by_year,
            x="year",
            y="troops",
            x_label="Year",
            y_label="US Troops Deployed",
            x_format="year",
        ),
        ChartSpec(
            chart_id="bm-afghanistan-us-deaths",
            chart_type=ChartType.BAR,
            title="Afghanistan War: US Military Deaths by Year",
            data_source=get_afghanistan_costs_by_year,
            x="year",
            y="us_deaths",
            x_label="Year",
            y_label="US Deaths",
            x_format="year",
        ),
        ChartSpec(
            chart_id="bm-iraq-costs-by-year",
            chart_type=ChartType.LINE,
            title="Iraq War: Annual Costs (2003-2019)",
            data_source=get_iraq_costs_by_year,
            x="year",
            y="spending_billions",
            x_label="Year",
            y_label="Spending (Billions USD)",
            x_format="year",
        ),
        ChartSpec(
            chart_id="bm-iraq-troops",
            chart_type=ChartType.LINE,
            title="Iraq War: Troop Levels (2003-2019)",
            data_source=get_iraq_costs_by_year,
            x="year",
            y="troops",
            x_label="Year",
            y_label="US Troops Deployed",
            x_format="year",
        ),
        ChartSpec(
            chart_id="bm-iraq-us-deaths",
            chart_type=ChartType.BAR,
            title="Iraq War: US Military Deaths by Year",
            data_source=get_iraq_costs_by_year,
            x="year",
            y="us_deaths",
            x_label="Year",
            y_label="US Deaths",
            x_format="year",
        ),
        ChartSpec(
            chart_id="bm-cumulative-war-costs",
            chart_type=ChartType.LINE,
            title="Cumulative Post-9/11 War Costs",
            data_source=get_cumulative_war_costs,
            x="year",
            y="cumulative_spending",
            x_label="Year",
            y_label="Cumulative Spending (Billions USD)",
            x_format="year",
        ),
        ChartSpec(
            chart_id="bm-veterans-cost-projection",
            chart_type=ChartType.BAR,
            title="Projected Veterans' Healthcare Costs by Decade",
            data_source=get_veterans_cost_projection,
            x="decade",
            y="total_billions",
            x_label="Decade",
            y_label="Total Cost (Billions USD)",
        ),
        ChartSpec(
            chart_id="bm-interest-on-war-debt",
            chart_type=ChartType.LINE,
            title="Cumulative Interest on War Debt (2001-2050)",
            data_source=get_interest_on_war_debt,
            x="year",
            y="cumulative_interest",
            x_label="Year",
            y_label="Cumulative Interest (Billions USD)",
            x_format="year",
        ),
        # =========================================================================
        # PART II: RECENT CONFLICTS - Yemen, Gaza, Ukraine
        # =========================================================================
        ChartSpec(
            chart_id="bm-military-aid-israel",
            chart_type=ChartType.LINE,
            title="US Military Aid to Israel (1970-2024)",
            data_source=get_military_aid_israel,
            x="year",
            y="cumulative",
            x_label="Year",
            y_label="Cumulative Aid (Billions USD)",
            x_format="year",
        ),
        ChartSpec(
            chart_id="bm-yemen-civilian-deaths",
            chart_type=ChartType.LINE,
            title="Yemen: Civilian Deaths from Coalition Airstrikes",
            data_source=get_yemen_casualties,
            x="year",
            y="civilian_deaths",
            x_label="Year",
            y_label="Civilian Deaths",
            x_format="year",
        ),
        ChartSpec(
            chart_id="bm-yemen-famine-deaths",
            chart_type=ChartType.LINE,
            title="Yemen: Cumulative Famine Deaths",
            data_source=get_yemen_casualties,
            x="year",
            y="famine_deaths",
            x_label="Year",
            y_label="Famine Deaths (Cumulative)",
            x_format="year",
        ),
        ChartSpec(
            chart_id="bm-gaza-deaths-timeline",
            chart_type=ChartType.LINE,
            title="Gaza: Palestinian Deaths (Oct 2023 - Oct 2024)",
            data_source=get_gaza_casualties,
            x="month",
            y="palestinian_deaths",
            x_label="Month",
            y_label="Cumulative Palestinian Deaths",
        ),
        ChartSpec(
            chart_id="bm-gaza-children-deaths",
            chart_type=ChartType.LINE,
            title="Gaza: Children Killed (Oct 2023 - Oct 2024)",
            data_source=get_gaza_casualties,
            x="month",
            y="children_deaths",
            x_label="Month",
            y_label="Cumulative Children Deaths",
        ),
        ChartSpec(
            chart_id="bm-ukraine-aid-breakdown",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="US Aid to Ukraine by Category (2022-2024)",
            data_source=get_ukraine_aid,
            x="category",
            y="amount_billions",
            x_label="Category",
            y_label="Amount (Billions USD)",
        ),
        # =========================================================================
        # PART II: SPENDING BY PRESIDENT
        # =========================================================================
        ChartSpec(
            chart_id="bm-spending-by-president",
            chart_type=ChartType.BAR,
            title="Total Military Spending by Presidential Term",
            data_source=get_military_spending_by_president,
            x="president",
            y="total_spending",
            x_label="President",
            y_label="Total Spending (Billions USD)",
        ),
        ChartSpec(
            chart_id="bm-spending-pct-gdp-by-president",
            chart_type=ChartType.BAR,
            title="Military Spending as % GDP by President",
            data_source=get_military_spending_by_president,
            x="president",
            y="pct_gdp_avg",
            x_label="President",
            y_label="Average % of GDP",
        ),
        # =========================================================================
        # PART III: ECONOMICS OF VIOLENCE - Comparative Analysis
        # =========================================================================
        ChartSpec(
            chart_id="bm-cost-per-death-comparison",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="Cost Per Death: Comparing Atrocities",
            data_source=get_cost_per_death_comparison,
            x="event",
            y="cost_per_death",
            x_label="Event",
            y_label="Cost Per Death (USD)",
        ),
        ChartSpec(
            chart_id="bm-atrocity-total-deaths",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="Total Deaths by Atrocity",
            data_source=get_cost_per_death_comparison,
            x="event",
            y="deaths",
            x_label="Event",
            y_label="Total Deaths",
        ),
        ChartSpec(
            chart_id="bm-civilian-combatant-ratio",
            chart_type=ChartType.BAR,
            title="Civilian Deaths as Percentage of Total (by Conflict)",
            data_source=get_civilian_combatant_ratio,
            x="conflict",
            y="civilian_pct",
            x_label="Conflict",
            y_label="Civilian Deaths (%)",
        ),
        ChartSpec(
            chart_id="bm-gdp-vs-military",
            chart_type=ChartType.SCATTER,
            title="Military Spending vs GDP Share (Top 30 Countries)",
            data_source=get_gdp_vs_military_spending,
            x="spending_billions",
            y="pct_gdp",
            x_label="Military Spending (Billions USD)",
            y_label="% of GDP",
            color="country:N",
        ),
        # =========================================================================
        # PART IV: MORAL LEDGER - Taxpayer Analysis
        # =========================================================================
        ChartSpec(
            chart_id="bm-taxpayer-cumulative",
            chart_type=ChartType.LINE,
            title="Cumulative Median Taxpayer Military Contribution (1975-2024)",
            data_source=get_taxpayer_cumulative_contribution,
            x="year",
            y="cumulative_contribution",
            x_label="Year",
            y_label="Cumulative Contribution (USD)",
            x_format="year",
        ),
        ChartSpec(
            chart_id="bm-taxpayer-annual",
            chart_type=ChartType.LINE,
            title="Annual Median Taxpayer Military Contribution (1975-2024)",
            data_source=get_taxpayer_cumulative_contribution,
            x="year",
            y="annual_contribution",
            x_label="Year",
            y_label="Annual Contribution (USD)",
            x_format="year",
        ),
        ChartSpec(
            chart_id="bm-deaths-per-taxpayer",
            chart_type=ChartType.BAR,
            title="Deaths Attributable to Median Taxpayer by Decade",
            data_source=get_deaths_per_taxpayer,
            x="decade",
            y="deaths_attributed",
            x_label="Decade",
            y_label="Deaths Attributed",
        ),
        ChartSpec(
            chart_id="bm-deaths-per-taxpayer-cumulative",
            chart_type=ChartType.LINE,
            title="Cumulative Deaths Attributable to Median Taxpayer",
            data_source=get_deaths_per_taxpayer,
            x="decade",
            y="cumulative_deaths",
            x_label="Decade",
            y_label="Cumulative Deaths",
        ),
        # =========================================================================
        # PART IV: RESISTANCE AND PUBLIC OPINION
        # =========================================================================
        ChartSpec(
            chart_id="bm-war-tax-resistance",
            chart_type=ChartType.BAR,
            title="War Tax Resistance in America by Era",
            data_source=get_war_tax_resistance_history,
            x="era",
            y="resisters_estimated",
            x_label="Era",
            y_label="Estimated Resisters",
        ),
        ChartSpec(
            chart_id="bm-antiwar-protests",
            chart_type=ChartType.BAR,
            title="Major Antiwar Protests: Participation",
            data_source=get_antiwar_protest_sizes,
            x="protest",
            y="participants_millions",
            x_label="Protest",
            y_label="Participants (Millions)",
        ),
        ChartSpec(
            chart_id="bm-public-opinion-wars",
            chart_type=ChartType.BAR,
            title="Public Support for Wars Over Time",
            data_source=get_public_opinion_wars,
            x="year",
            y="support_pct",
            x_label="Year",
            y_label="Support (%)",
            color="war:N",
        ),
        ChartSpec(
            chart_id="bm-spending-by-party",
            chart_type=ChartType.BAR,
            title="Military Spending Increase by Party",
            data_source=get_spending_by_party,
            x="party",
            y="avg_spending_increase_pct",
            x_label="Party",
            y_label="Average Annual Increase (%)",
        ),
    ]


def get_boomcession_chart_specs() -> list[ChartSpec]:
    """Define all Boomcession article charts."""
    return [
        ChartSpec(
            chart_id="boom-sentiment-president",
            chart_type=ChartType.BAR,
            title="Consumer Sentiment by President",
            data_source=load_sentiment_by_president,
            x="label",
            y="sentiment",
            x_label="President",
            y_label="Average Consumer Sentiment",
            options={"x_sort_order": ["Eisenhower", "JFK/LBJ", "Nixon/Ford", "Carter", "Reagan", "Bush I", "Clinton", "Bush II", "Obama", "Trump (1)", "Biden", "Trump (2)"]},
        ),
        ChartSpec(
            chart_id="boom-correlation",
            chart_type=ChartType.AREA,
            title="GDP Growth vs. Sentiment Correlation (10-Year Rolling)",
            data_source=load_gdp_sentiment_correlation,
            x="year",
            y="correlation",
            x_label="Year",
            y_label="Correlation Coefficient",
            x_format="year",
        ),
        ChartSpec(
            chart_id="boom-scatter",
            chart_type=ChartType.SCATTER,
            title="The Sentiment Gap: GDP Growth vs. Consumer Sentiment",
            data_source=load_gdp_sentiment_scatter,
            x="gdp_growth",
            y="sentiment",
            x_label="Real GDP Growth (%)",
            y_label="Consumer Sentiment",
            color="era",
        ),
        ChartSpec(
            chart_id="boom-spending-share",
            chart_type=ChartType.LINE,
            title="Share of Consumer Spending by Income Group",
            data_source=load_consumer_spending_by_income,
            x="year",
            y="share",
            x_label="Year",
            y_label="Share of Spending (%)",
            x_format="year",
            color="group",
        ),
        ChartSpec(
            chart_id="boom-productivity-wages",
            chart_type=ChartType.LINE,
            title="The Productivity-Wage Gap (Index: 1979=100)",
            data_source=load_productivity_wages,
            x="year",
            y="index",
            x_label="Year",
            y_label="Index (1979=100)",
            x_format="year",
            color="metric",
        ),
        ChartSpec(
            chart_id="boom-housing",
            chart_type=ChartType.LINE,
            title="Housing Price-to-Income Ratio",
            data_source=load_housing_affordability,
            x="year",
            y="ratio",
            x_label="Year",
            y_label="Median House Price / Median Income",
            x_format="year",
        ),
        ChartSpec(
            chart_id="boom-corporate-profits",
            chart_type=ChartType.LINE,
            title="Corporate Profits as Share of GDP",
            data_source=load_corporate_profits_pct,
            x="year",
            y="profits_pct",
            x_label="Year",
            y_label="Profits (% of GDP)",
            x_format="year",
        ),
        ChartSpec(
            chart_id="boom-nondiscretionary",
            chart_type=ChartType.LINE,
            title="Housing as Share of Personal Consumption",
            data_source=load_nondiscretionary_spending,
            x="year",
            y="housing_pct",
            x_label="Year",
            y_label="Housing (% of PCE)",
            x_format="year",
        ),
        ChartSpec(
            chart_id="boom-labor-share",
            chart_type=ChartType.LINE,
            title="Labor Share of National Income",
            data_source=load_labor_share,
            x="year",
            y="labor_share_pct",
            x_label="Year",
            y_label="Labor Share (%)",
            x_format="year",
        ),
        ChartSpec(
            chart_id="boom-welfare",
            chart_type=ChartType.SCATTER,
            title="Welfare Without Growth: Life Expectancy vs. GDP",
            data_source=load_welfare_comparison,
            x="gdp_per_capita",
            y="life_expectancy",
            x_label="GDP Per Capita (USD)",
            y_label="Life Expectancy (Years)",
            options={"show_labels": True, "label_field": "country"},
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
    cubs_2016_specs = get_cubs_2016_chart_specs()
    blood_money_specs = get_blood_money_chart_specs()
    boomcession_specs = get_boomcession_chart_specs()
    specs = gdp_specs + beyond_growth_specs + baseball_specs + marx_specs + sabermetrics_specs + education_specs + ncaa_basketball_specs + cubs_2016_specs + blood_money_specs + boomcession_specs

    print(f"\nFound {len(specs)} chart specifications")
    print(f"  - GDP article: {len(gdp_specs)} charts")
    print(f"  - Beyond Growth article: {len(beyond_growth_specs)} charts")
    print(f"  - Baseball article: {len(baseball_specs)} charts")
    print(f"  - Marx article: {len(marx_specs)} charts")
    print(f"  - Sabermetrics article: {len(sabermetrics_specs)} charts")
    print(f"  - Education article: {len(education_specs)} charts")
    print(f"  - NCAA Basketball article: {len(ncaa_basketball_specs)} charts")
    print(f"  - Cubs 2016 article: {len(cubs_2016_specs)} charts")
    print(f"  - Blood Money book: {len(blood_money_specs)} charts")
    print(f"  - Boomcession article: {len(boomcession_specs)} charts")

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
