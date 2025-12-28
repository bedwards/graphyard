"""
Chart Specification Schema

Defines a unified chart specification that can be rendered by both:
- Altair (Python) - declarative grammar of graphics
- Observable Plot (TypeScript) - D3-based high-level charting

This follows 2025 best practices for chart type selection:
- Comparisons → Bar charts
- Trends over time → Line charts
- Part-to-whole → Donut charts (prefer over pie, max 5 segments)
- Distributions → Histograms, violin plots
- Correlations → Scatter plots
- Rankings → Horizontal bar charts

References:
- https://www.luzmo.com/blog/chart-types
- https://guides.lib.berkeley.edu/data-visualization/type
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional
import json


class ChartType(Enum):
    """
    Chart types based on 2025 data visualization guidelines.

    Selection guide:
    - LINE: Trends over time, continuous data
    - BAR: Comparisons across categories
    - HORIZONTAL_BAR: Rankings, comparisons with long labels
    - DONUT: Part-to-whole (max 5 segments)
    - SCATTER: Correlations between two numeric variables
    - AREA: Cumulative trends, part-to-whole over time
    - HISTOGRAM: Distributions of continuous data
    """
    LINE = "line"
    BAR = "bar"
    HORIZONTAL_BAR = "horizontal_bar"
    DONUT = "donut"
    SCATTER = "scatter"
    AREA = "area"
    STACKED_AREA = "stacked_area"
    HISTOGRAM = "histogram"


@dataclass
class ChartSpec:
    """
    Unified chart specification.

    This spec is designed to be serializable to JSON for the TypeScript
    renderer while also being directly usable by the Python Altair renderer.
    """
    chart_id: str
    chart_type: ChartType
    title: str

    # Data source (Python callable or pre-loaded data)
    data_source: Optional[Callable] = None
    data: Optional[list[dict]] = None

    # Column mappings
    x: Optional[str] = None
    y: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None

    # Axis labels
    x_label: Optional[str] = None
    y_label: Optional[str] = None

    # Formatting
    x_format: Optional[str] = None  # "year", "currency", "percent", etc.
    y_format: Optional[str] = None

    # Additional options
    options: dict[str, Any] = field(default_factory=dict)

    def load_data(self) -> list[dict]:
        """Load data from source and return as list of dicts."""
        if self.data is not None:
            return self.data
        if self.data_source is not None:
            df = self.data_source()
            return df.to_dict(orient='records')
        raise ValueError(f"No data source for chart {self.chart_id}")

    def to_json(self) -> str:
        """Serialize spec to JSON for TypeScript renderer."""
        return json.dumps({
            "chartId": self.chart_id,
            "chartType": self.chart_type.value,
            "title": self.title,
            "data": self.load_data(),
            "x": self.x,
            "y": self.y,
            "color": self.color,
            "size": self.size,
            "xLabel": self.x_label,
            "yLabel": self.y_label,
            "xFormat": self.x_format,
            "yFormat": self.y_format,
            "options": self.options,
        }, default=str)


# Chart type selection helper based on 2025 guidelines
CHART_TYPE_GUIDE = """
┌─────────────────────────────────────────────────────────────────────┐
│                    CHART TYPE SELECTION GUIDE                       │
│                     (2025 Best Practices)                           │
├─────────────────────────────────────────────────────────────────────┤
│ QUESTION                          │ RECOMMENDED CHART               │
├───────────────────────────────────┼─────────────────────────────────┤
│ How does X change over time?      │ LINE                            │
│ How do categories compare?        │ BAR (vertical)                  │
│ What is the ranking?              │ HORIZONTAL_BAR                  │
│ What is the composition?          │ DONUT (max 5 parts)             │
│ How are X and Y related?          │ SCATTER                         │
│ How does composition change?      │ STACKED_AREA                    │
│ What is the distribution?         │ HISTOGRAM                       │
└───────────────────────────────────┴─────────────────────────────────┘
"""
