"""
Chart Framework Core

SOLID/DRY/APIE chart production framework for publication-quality visualizations.
"""

from .base import Chart, ChartConfig, ChartData
from .registry import ChartRegistry
from .pipeline import ChartPipeline

__all__ = ['Chart', 'ChartConfig', 'ChartData', 'ChartRegistry', 'ChartPipeline']
