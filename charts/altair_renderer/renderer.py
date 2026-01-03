"""
Altair Renderer

Converts ChartSpec to Altair charts and exports to static formats.
"""

from pathlib import Path
from typing import Optional
import altair as alt

from charts.spec import ChartSpec, ChartType


class AltairRenderer:
    """
    Renders ChartSpec using Altair with publication-quality defaults.

    Uses the Lexend font family and a clean, minimal theme suitable
    for academic and professional publications.
    """

    # Publication-quality color palette
    COLORS = [
        "#2563eb",  # Primary blue
        "#16a34a",  # Green
        "#dc2626",  # Red
        "#9333ea",  # Purple
        "#ea580c",  # Orange
        "#0891b2",  # Cyan
    ]

    def __init__(
        self,
        width: int = 600,
        height: int = 400,
        font_family: str = "Lexend, system-ui, sans-serif",
    ):
        self.width = width
        self.height = height
        self.font_family = font_family
        self._configure_theme()

    def _configure_theme(self):
        """Configure Altair theme for publication quality."""
        def publication_theme():
            return {
                "config": {
                    "font": self.font_family,
                    "title": {
                        "font": self.font_family,
                        "fontSize": 16,
                        "fontWeight": 600,
                        "anchor": "start",
                        "color": "#1a1a2e",
                    },
                    "axis": {
                        "labelFont": self.font_family,
                        "labelFontSize": 11,
                        "labelColor": "#4a5568",
                        "titleFont": self.font_family,
                        "titleFontSize": 12,
                        "titleColor": "#1a1a2e",
                        "gridColor": "#e5e7eb",
                        "domainColor": "#9ca3af",
                    },
                    "legend": {
                        "labelFont": self.font_family,
                        "labelFontSize": 11,
                        "titleFont": self.font_family,
                        "titleFontSize": 12,
                    },
                    "view": {
                        "strokeWidth": 0,
                    },
                    "range": {
                        "category": self.COLORS,
                    },
                }
            }

        alt.themes.register("publication", publication_theme)
        alt.themes.enable("publication")

    def render(self, spec: ChartSpec) -> alt.Chart:
        """Render ChartSpec to Altair Chart object."""
        data = spec.load_data()

        # Convert year columns to strings to avoid comma formatting (DRY fix)
        # Also extract unique years for decade tick calculation
        self._year_values = []
        if spec.x_format == "year" and spec.x:
            self._year_values = sorted(set(row[spec.x] for row in data))
            data = [{**row, spec.x: str(row[spec.x])} for row in data]
        if spec.y_format == "year" and spec.y:
            self._year_values = sorted(set(row[spec.y] for row in data))
            data = [{**row, spec.y: str(row[spec.y])} for row in data]

        # Build base chart
        chart = alt.Chart(alt.Data(values=data)).properties(
            width=self.width,
            height=self.height,
            title=spec.title,
        )

        # Apply chart type
        chart = self._apply_chart_type(chart, spec)

        return chart

    def _apply_chart_type(self, chart: alt.Chart, spec: ChartSpec) -> alt.Chart:
        """Apply the appropriate mark and encoding based on chart type."""

        # Add type hints since we're using dict data (not pandas DataFrame)
        x_axis = alt.X(f"{spec.x}:Q", title=spec.x_label) if spec.x else alt.X()
        y_axis = alt.Y(f"{spec.y}:Q", title=spec.y_label) if spec.y else alt.Y()

        # Override for temporal/nominal fields
        if spec.x_format == "year":
            x_axis = alt.X(f"{spec.x}:O", title=spec.x_label)  # Ordinal for years

        # Apply formatting
        if spec.x_format:
            x_axis = self._apply_format(x_axis, spec.x_format, 'x')
        if spec.y_format:
            y_axis = self._apply_format(y_axis, spec.y_format, 'y')

        # Use string comparison for chart type to avoid enum import issues
        chart_type = spec.chart_type.value if hasattr(spec.chart_type, 'value') else str(spec.chart_type)

        if chart_type == "line":
            return chart.mark_line(strokeWidth=2.5).encode(
                x=x_axis,
                y=y_axis,
                color=alt.Color(f"{spec.color}:N") if spec.color else alt.value(self.COLORS[0]),
            )

        elif chart_type == "bar":
            # For bar charts, x is categorical (nominal) unless it's year data
            if spec.x_format == "year":
                bar_x = x_axis  # Use the ordinal year axis with formatting
            else:
                bar_x = alt.X(f"{spec.x}:N", title=spec.x_label) if spec.x else alt.X()
            return chart.mark_bar().encode(
                x=bar_x,
                y=y_axis,
                color=alt.Color(spec.color) if spec.color else alt.value(self.COLORS[0]),
            )

        elif chart_type == "horizontal_bar":
            return chart.mark_bar().encode(
                x=y_axis,  # Swap for horizontal
                y=alt.Y(
                    f"{spec.x}:N",
                    title=spec.x_label,
                    sort="-x",
                    axis=alt.Axis(labelLimit=250),  # Prevent label truncation
                ) if spec.x else alt.Y(),
                color=alt.Color(f"{spec.color}:N") if spec.color else alt.value(self.COLORS[0]),
            )

        elif chart_type == "donut":
            return chart.mark_arc(innerRadius=60).encode(
                theta=alt.Theta(spec.y, type="quantitative"),
                color=alt.Color(spec.x, type="nominal", legend=alt.Legend(title=None)),
            )

        elif chart_type == "scatter":
            mark = chart.mark_circle(size=60)
            encoding = {"x": x_axis, "y": y_axis}
            if spec.color:
                encoding["color"] = alt.Color(spec.color)
            if spec.size:
                encoding["size"] = alt.Size(spec.size)
            return mark.encode(**encoding)

        elif chart_type == "area":
            return chart.mark_area(opacity=0.7).encode(
                x=x_axis,
                y=y_axis,
                color=alt.Color(spec.color) if spec.color else alt.value(self.COLORS[0]),
            )

        elif chart_type == "stacked_area":
            return chart.mark_area().encode(
                x=x_axis,
                y=alt.Y(spec.y, stack="zero", title=spec.y_label),
                color=alt.Color(spec.color) if spec.color else alt.value(self.COLORS[0]),
            )

        elif chart_type == "histogram":
            return chart.mark_bar().encode(
                x=alt.X(spec.x, bin=True, title=spec.x_label),
                y=alt.Y("count()", title="Count"),
            )

        elif chart_type == "marimekko":
            # Marimekko chart: width encodes x value, height encodes y value
            # Data must have: group, width_share, height_share
            # We compute cumulative positions for stacking
            return self._render_marimekko(spec)

        else:
            raise ValueError(f"Unsupported chart type: {chart_type}")

    def _render_marimekko(self, spec: ChartSpec) -> alt.Chart:
        """
        Render a Marimekko chart where bar width and height encode different values.

        Data format expected:
        - group: category label
        - width_share: value for bar width (x dimension)
        - height_share: value for bar height (y dimension)

        The bars are stacked vertically, with each bar's:
        - Height proportional to height_share
        - Width extending from 0 to width_share on x-axis
        """
        # Load data from spec
        data = spec.load_data()

        # Calculate cumulative y positions for stacking
        processed_data = []
        y_cumulative = 0

        # Sort by height_share descending so largest groups are at top
        sorted_data = sorted(data, key=lambda x: x.get('height_share', 0), reverse=True)

        for row in sorted_data:
            height = row.get('height_share', 0)
            width = row.get('width_share', 0)
            group = row.get('group', '')

            processed_data.append({
                'group': group,
                'x1': 0,
                'x2': width,
                'y1': y_cumulative,
                'y2': y_cumulative + height,
                'width_share': width,
                'height_share': height,
            })
            y_cumulative += height

        # Create chart with rect marks
        marimekko = alt.Chart(alt.Data(values=processed_data)).mark_rect(
            stroke='white',
            strokeWidth=2,
        ).encode(
            x=alt.X('x1:Q', title=spec.x_label, scale=alt.Scale(domain=[0, 100])),
            x2='x2:Q',
            y=alt.Y('y1:Q', title=spec.y_label, scale=alt.Scale(domain=[0, 100])),
            y2='y2:Q',
            color=alt.Color(
                'group:N',
                legend=alt.Legend(title=None, orient='bottom'),
                scale=alt.Scale(range=self.COLORS[:len(processed_data)])
            ),
            tooltip=[
                alt.Tooltip('group:N', title='Group'),
                alt.Tooltip('width_share:Q', title=spec.x_label or 'Width', format='.1f'),
                alt.Tooltip('height_share:Q', title=spec.y_label or 'Height', format='.1f'),
            ]
        ).properties(
            width=self.width,
            height=self.height,
            title=spec.title,
        )

        # Add text labels in center of each bar
        labels = alt.Chart(alt.Data(values=processed_data)).mark_text(
            align='left',
            baseline='middle',
            dx=5,
            fontSize=12,
            fontWeight=500,
            color='white',
        ).encode(
            x=alt.X('x1:Q'),
            y=alt.Y('y_mid:Q'),
            text=alt.Text('label:N'),
        ).transform_calculate(
            y_mid='(datum.y1 + datum.y2) / 2',
            label='datum.group + ": " + format(datum.width_share, ".0f") + "%"',
        )

        return marimekko + labels

    def _apply_format(self, axis, format_type: str, axis_name: str):
        """Apply formatting to axis based on format type.

        This is the single source of truth for all axis formatting (DRY).
        Changes here propagate to all charts automatically.
        """
        # Year format: show only decades (1960, 1970, 1980...) to avoid cramped axis
        if format_type == "year":
            decade_ticks = [str(y) for y in self._year_values if y % 10 == 0]
            return axis.axis(values=decade_ticks, labelAngle=0)

        format_map = {
            "currency": "$,.0f",
            "trillions": "$,.2s",
            "billions": "$,.2s",
            "thousands": ",.0f",
            "percent": ".1%",
            "percent_raw": ".1f",  # Data already in % form (3.5 = 3.5%)
            "decimal": ".2f",
        }

        if format_type in format_map:
            return axis.axis(format=format_map[format_type])
        return axis

    def save(
        self,
        spec: ChartSpec,
        output_dir: Path,
        formats: list[str] = ["svg", "png", "pdf"],
    ) -> list[Path]:
        """
        Render and save chart to specified formats.

        Uses vl-convert for dependency-free static export.
        """
        chart = self.render(spec)
        output_dir.mkdir(parents=True, exist_ok=True)

        saved_files = []
        for fmt in formats:
            output_path = output_dir / f"{spec.chart_id}.{fmt}"
            chart.save(str(output_path))
            saved_files.append(output_path)
            print(f"  [Altair] Saved: {output_path.name}")

        return saved_files
