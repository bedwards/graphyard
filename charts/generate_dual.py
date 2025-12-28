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
)
# ML forecasting available in charts.gdp.forecast if needed

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
            color="country",  # Color by country for multi-line
        ),
        # Note: GDP forecast chart requires running ML models
        # For now, the article discusses forecasting without a dedicated chart
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

    specs = get_gdp_chart_specs()
    print(f"\nFound {len(specs)} chart specifications")

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
