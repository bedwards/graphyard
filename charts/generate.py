#!/usr/bin/env python3
"""
Chart Generation Script

Generates all charts for the Graphyard site.
Run from project root: python charts/generate.py

Usage:
    python charts/generate.py              # Generate all charts
    python charts/generate.py --chart=gdp  # Generate specific chart set
"""

import argparse
from pathlib import Path

from charts import ChartPipeline, ChartSpec
from charts.gdp.data import (
    load_world_gdp_trend,
    load_country_gdp_comparison,
    load_gdp_growth_rates,
    load_gdp_per_capita_by_income_group,
    load_gdp_components,
    load_regional_gdp,
)

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "site" / "public" / "assets" / "charts"


def register_gdp_charts(pipeline: ChartPipeline) -> None:
    """Register all GDP-related charts."""

    # World GDP trend (line chart)
    pipeline.add(ChartSpec(
        chart_id="world-gdp-trend",
        chart_type="line",
        title="World GDP Over Time",
        data_source=lambda: load_world_gdp_trend(1960, 2023),
        config={
            "x_column": "year",
            "y_column": "value",
            "y_label": "GDP (Current US$)",
            "y_format": "trillions",
        },
    ))

    # World GDP growth rate (bar chart)
    pipeline.add(ChartSpec(
        chart_id="world-gdp-growth",
        chart_type="bar",
        title="World GDP Growth Rate",
        data_source=lambda: load_gdp_growth_rates("WLD", 30),
        config={
            "x_column": "year",
            "y_column": "value",
            "y_label": "Annual Growth (%)",
            "highlight_negative": True,
        },
    ))

    # Top 10 economies (horizontal bar)
    pipeline.add(ChartSpec(
        chart_id="top-10-gdp",
        chart_type="horizontal_bar",
        title="World's Largest Economies (2023)",
        data_source=lambda: load_country_gdp_comparison(
            ["USA", "CHN", "JPN", "DEU", "IND", "GBR", "FRA", "BRA", "ITA", "CAN"],
            2023
        ),
        config={
            "x_column": "value",
            "y_column": "entity_name",
            "x_label": "GDP (Current US$)",
            "x_format": "trillions",
        },
    ))

    # GDP by region (horizontal bar)
    pipeline.add(ChartSpec(
        chart_id="gdp-by-region",
        chart_type="horizontal_bar",
        title="GDP by World Bank Region (2023)",
        data_source=lambda: load_regional_gdp(2023),
        config={
            "x_column": "value",
            "y_column": "entity_name",
            "x_label": "GDP (Current US$)",
            "x_format": "trillions",
        },
    ))

    # GDP per capita by income group
    pipeline.add(ChartSpec(
        chart_id="gdp-per-capita-income-groups",
        chart_type="horizontal_bar",
        title="GDP Per Capita by Income Group (2023)",
        data_source=lambda: load_gdp_per_capita_by_income_group(2023),
        config={
            "x_column": "value",
            "y_column": "entity_name",
            "x_label": "GDP Per Capita (Current US$)",
            "x_format": "thousands",
        },
    ))

    # US GDP components (pie/donut)
    pipeline.add(ChartSpec(
        chart_id="gdp-components-usa",
        chart_type="pie",
        title="US GDP Components (2023)",
        data_source=lambda: load_gdp_components("USA", 2023),
        config={
            "value_column": "value",
            "label_column": "indicator_name",
        },
    ))


def main():
    parser = argparse.ArgumentParser(description="Generate charts for Graphyard")
    parser.add_argument(
        "--chart",
        type=str,
        help="Generate only charts for a specific topic (e.g., 'gdp')",
    )
    parser.add_argument(
        "--formats",
        type=str,
        default="svg,png,pdf",
        help="Output formats (comma-separated)",
    )
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    formats = [f.strip() for f in args.formats.split(",")]
    pipeline = ChartPipeline(output_dir=OUTPUT_DIR, formats=formats)

    # Register chart sets
    if args.chart is None or args.chart == "gdp":
        register_gdp_charts(pipeline)

    # Run the pipeline
    print(f"Generating charts to: {OUTPUT_DIR}")
    print(f"Formats: {', '.join(formats)}")
    print("=" * 50)

    results = pipeline.run()

    # Summary
    successful = sum(1 for r in results if r["success"])
    failed = len(results) - successful

    print("=" * 50)
    print(f"Generated: {successful} charts")
    if failed:
        print(f"Failed: {failed} charts")
        for r in results:
            if not r["success"]:
                print(f"  - {r['chart_id']}: {r['error']}")


if __name__ == "__main__":
    main()
