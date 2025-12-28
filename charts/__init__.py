"""
Graphyard Charts

Publication-quality chart framework following SOLID/DRY/APIE principles.

Usage:
    from charts import ChartConfig, ChartData, ChartRegistry, ChartPipeline
    from charts.gdp import LineChart, BarChart

    # Create a chart directly
    data = ChartData(values=df, title="GDP Over Time", chart_id="gdp-trend")
    chart = LineChart(data)
    chart.render()
    chart.save(Path("output/"))

    # Or use the pipeline for batch processing
    pipeline = ChartPipeline(output_dir=Path("output/"))
    pipeline.add(ChartSpec(
        chart_id="gdp-trend",
        chart_type="line",
        title="GDP Over Time",
        data_source=lambda: load_gdp_data(),
    ))
    pipeline.run()
"""

from .core import Chart, ChartConfig, ChartData, ChartRegistry, ChartPipeline
from .core.pipeline import ChartSpec
from .themes import get_palette, PUBLICATION, ECONOMIST, WORLDBANK

# Import chart types to register them
from . import gdp

__version__ = "0.1.0"

__all__ = [
    'Chart',
    'ChartConfig',
    'ChartData',
    'ChartRegistry',
    'ChartPipeline',
    'ChartSpec',
    'get_palette',
    'PUBLICATION',
    'ECONOMIST',
    'WORLDBANK',
]
