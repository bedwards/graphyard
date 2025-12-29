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
    load_bottom50_vs_top10_emissions,
    load_world_gdp_growth_long_term,
    load_adjusted_net_savings_by_income_group,
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
        # Part III: The Extraction Machine - carbon colonialism
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
        ChartSpec(
            chart_id="bg-carbon-inequality",
            chart_type=ChartType.HORIZONTAL_BAR,
            title="Who Causes Climate Change? Share of Global Emissions",
            data_source=load_bottom50_vs_top10_emissions,
            x="group",
            y="share_of_emissions",
            x_label="Population Group",
            y_label="Share of Global Emissions (%)",
            y_format="percent_raw",
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
        # Part VI: Diminishing returns of GDP
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
    specs = gdp_specs + beyond_growth_specs

    print(f"\nFound {len(specs)} chart specifications")
    print(f"  - GDP article: {len(gdp_specs)} charts")
    print(f"  - Beyond Growth article: {len(beyond_growth_specs)} charts")

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
