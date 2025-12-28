"""
Altair Chart Convenience Functions

High-level functions for rendering specific chart types.
"""

from pathlib import Path
import altair as alt

from charts.spec import ChartSpec
from .renderer import AltairRenderer


def render_chart(spec: ChartSpec, output_dir: Path = None) -> alt.Chart:
    """
    Render a ChartSpec to an Altair chart.

    If output_dir is provided, also saves to SVG/PNG/PDF.
    """
    renderer = AltairRenderer()
    chart = renderer.render(spec)

    if output_dir:
        renderer.save(spec, output_dir)

    return chart
