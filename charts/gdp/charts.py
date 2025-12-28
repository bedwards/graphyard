"""
GDP Article Chart Implementations

Each chart type follows the base Chart interface (Liskov Substitution).
"""

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from typing import Any

from ..core.base import Chart, ChartConfig, ChartData
from ..core.registry import ChartRegistry
from ..themes import get_palette


@ChartRegistry.register("line", aliases=["timeseries", "trend"])
class LineChart(Chart):
    """
    Line chart for time series data.

    Ideal for showing GDP trends over time.
    """

    def render(self) -> plt.Figure:
        fig, ax = self.create_figure()
        palette = get_palette()

        df = self.data.values
        if isinstance(df, pd.DataFrame):
            # Assume first column is x, rest are y series
            x = df.iloc[:, 0]
            for i, col in enumerate(df.columns[1:]):
                color = palette.sequence[i % len(palette.sequence)]
                ax.plot(x, df[col], label=col, color=color, linewidth=2)

            if len(df.columns) > 2:
                ax.legend(frameon=False)

        elif isinstance(df, dict):
            x = df.get('x', range(len(df.get('y', []))))
            y = df.get('y', [])
            ax.plot(x, y, color=palette.primary, linewidth=2)

        self.add_labels()
        fig.tight_layout()
        return fig


@ChartRegistry.register("bar", aliases=["column"])
class BarChart(Chart):
    """
    Bar chart for categorical comparisons.

    Ideal for comparing GDP across countries or components.
    """

    def render(self) -> plt.Figure:
        fig, ax = self.create_figure()
        palette = get_palette()

        df = self.data.values
        if isinstance(df, pd.DataFrame):
            x = df.iloc[:, 0]
            y = df.iloc[:, 1]
            colors = [palette.primary] * len(x)
            ax.bar(x, y, color=colors, edgecolor='none')

            # Rotate labels if needed
            if len(x) > 5:
                plt.xticks(rotation=45, ha='right')

        elif isinstance(df, dict):
            x = list(df.keys())
            y = list(df.values())
            ax.bar(x, y, color=palette.primary, edgecolor='none')

        self.add_labels()
        fig.tight_layout()
        return fig


@ChartRegistry.register("stacked_area", aliases=["area", "composition"])
class StackedAreaChart(Chart):
    """
    Stacked area chart for showing composition over time.

    Ideal for GDP components (C + I + G + NX).
    """

    def render(self) -> plt.Figure:
        fig, ax = self.create_figure()
        palette = get_palette()

        df = self.data.values
        if isinstance(df, pd.DataFrame):
            x = df.iloc[:, 0]
            y_cols = df.columns[1:]
            y_data = [df[col].values for col in y_cols]

            ax.stackplot(
                x, *y_data,
                labels=y_cols,
                colors=palette.sequence[:len(y_cols)],
                alpha=0.8
            )
            ax.legend(loc='upper left', frameon=False)

        self.add_labels()
        fig.tight_layout()
        return fig


@ChartRegistry.register("comparison", aliases=["side_by_side", "grouped_bar"])
class ComparisonChart(Chart):
    """
    Grouped bar chart for comparing multiple series.

    Ideal for nominal vs real GDP, or country comparisons.
    """

    def render(self) -> plt.Figure:
        fig, ax = self.create_figure()
        palette = get_palette()

        df = self.data.values
        if isinstance(df, pd.DataFrame):
            categories = df.iloc[:, 0]
            n_categories = len(categories)
            n_series = len(df.columns) - 1

            bar_width = 0.8 / n_series
            x = np.arange(n_categories)

            for i, col in enumerate(df.columns[1:]):
                offset = (i - n_series / 2 + 0.5) * bar_width
                color = palette.sequence[i % len(palette.sequence)]
                ax.bar(x + offset, df[col], bar_width,
                       label=col, color=color, edgecolor='none')

            ax.set_xticks(x)
            ax.set_xticklabels(categories)
            ax.legend(frameon=False)

            if n_categories > 5:
                plt.xticks(rotation=45, ha='right')

        self.add_labels()
        fig.tight_layout()
        return fig


@ChartRegistry.register("growth_rate", aliases=["change", "percent_change"])
class GrowthRateChart(Chart):
    """
    Bar chart for growth rates with positive/negative coloring.

    Ideal for showing GDP growth by year or quarter.
    """

    def render(self) -> plt.Figure:
        fig, ax = self.create_figure()
        palette = get_palette()

        df = self.data.values
        if isinstance(df, pd.DataFrame):
            x = df.iloc[:, 0]
            y = df.iloc[:, 1]
        elif isinstance(df, dict):
            x = list(df.keys())
            y = list(df.values())
        else:
            x = range(len(df))
            y = df

        # Color by positive/negative
        colors = [palette.positive if v >= 0 else palette.negative for v in y]
        ax.bar(x, y, color=colors, edgecolor='none')

        # Add zero line
        ax.axhline(y=0, color=self.config.text_color, linewidth=0.5)

        # Format as percentage
        ax.yaxis.set_major_formatter(mticker.PercentFormatter())

        if len(x) > 10:
            # Show every nth label
            step = max(1, len(x) // 10)
            ax.set_xticks(range(0, len(x), step))

        self.add_labels()
        fig.tight_layout()
        return fig


@ChartRegistry.register("component_breakdown", aliases=["breakdown", "waterfall"])
class ComponentBreakdownChart(Chart):
    """
    Horizontal bar chart showing GDP components.

    Ideal for showing C + I + G + NX = GDP breakdown.
    """

    def render(self) -> plt.Figure:
        fig, ax = self.create_figure()
        palette = get_palette()

        df = self.data.values
        if isinstance(df, pd.DataFrame):
            labels = df.iloc[:, 0]
            values = df.iloc[:, 1]
        elif isinstance(df, dict):
            labels = list(df.keys())
            values = list(df.values())
        else:
            raise ValueError("Expected DataFrame or dict")

        # Sort by value for cleaner presentation
        sorted_idx = np.argsort(values)[::-1]
        labels = [labels[i] for i in sorted_idx]
        values = [values[i] for i in sorted_idx]

        colors = palette.sequence[:len(labels)]
        y_pos = np.arange(len(labels))

        ax.barh(y_pos, values, color=colors, edgecolor='none')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels)
        ax.invert_yaxis()  # Largest at top

        # Add value labels
        for i, v in enumerate(values):
            ax.text(v + max(values) * 0.02, i, f'{v:,.0f}',
                    va='center', fontsize=self.config.font_size_annotation)

        self.add_labels()
        fig.tight_layout()
        return fig


@ChartRegistry.register("horizontal_bar", aliases=["hbar", "horizontal"])
class HorizontalBarChart(Chart):
    """
    Horizontal bar chart for ranked comparisons.

    Ideal for ranking countries by GDP or showing income group comparisons.
    """

    def render(self) -> plt.Figure:
        fig, ax = self.create_figure()
        palette = get_palette()

        df = self.data.values
        if isinstance(df, pd.DataFrame):
            labels = df.iloc[:, 0].tolist()
            values = df.iloc[:, 1].tolist()
        elif isinstance(df, dict):
            labels = list(df.keys())
            values = list(df.values())
        else:
            raise ValueError("Expected DataFrame or dict")

        y_pos = np.arange(len(labels))
        colors = [palette.sequence[i % len(palette.sequence)] for i in range(len(labels))]

        ax.barh(y_pos, values, color=colors, edgecolor='none')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels)
        ax.invert_yaxis()  # Largest at top

        self.add_labels()
        fig.tight_layout()
        return fig


@ChartRegistry.register("pie", aliases=["donut", "composition_pie"])
class PieChart(Chart):
    """
    Pie/donut chart for showing composition.

    Ideal for GDP component breakdown (C, I, G, NX).
    """

    def render(self) -> plt.Figure:
        fig, ax = self.create_figure()
        palette = get_palette()

        df = self.data.values
        if isinstance(df, pd.DataFrame):
            labels = df.iloc[:, 0].tolist()
            values = df.iloc[:, 1].tolist()
        elif isinstance(df, dict):
            labels = list(df.keys())
            values = list(df.values())
        else:
            raise ValueError("Expected DataFrame or dict")

        # Handle negative values (like imports in net exports)
        # Convert to absolute for pie, note in label
        display_values = [abs(v) for v in values]
        display_labels = [
            f"{l} (-)" if v < 0 else l
            for l, v in zip(labels, values)
        ]

        colors = palette.sequence[:len(labels)]

        # Create donut chart (hole in center)
        wedges, texts, autotexts = ax.pie(
            display_values,
            labels=display_labels,
            colors=colors,
            autopct='%1.1f%%',
            pctdistance=0.75,
            startangle=90,
            wedgeprops={'width': 0.5, 'edgecolor': 'white'},
        )

        # Style the percentage labels
        for autotext in autotexts:
            autotext.set_fontsize(self.config.font_size_annotation)

        ax.set_title(self.data.title, fontsize=self.config.font_size_title, fontweight='bold')

        fig.tight_layout()
        return fig
