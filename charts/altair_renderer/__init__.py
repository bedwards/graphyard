"""
Altair Chart Renderer

Renders charts using Altair (Vega-Lite) with vl-convert for static export.
Produces publication-quality SVG, PNG, and PDF outputs.

Altair advantages (2025):
- Declarative grammar of graphics
- Statistical transformations built-in
- vl-convert: dependency-free static export
- Clean, reproducible specifications

References:
- https://altair-viz.github.io/
- https://pypi.org/project/vl-convert-python/
"""

from .renderer import AltairRenderer
from .charts import render_chart

__all__ = ['AltairRenderer', 'render_chart']
