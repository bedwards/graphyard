"""
Base chart abstractions following SOLID principles.

Single Responsibility: Each class has one job
Open/Closed: Extend via inheritance, don't modify
Liskov Substitution: All Chart subclasses are interchangeable
Interface Segregation: Small, focused protocols
Dependency Inversion: Depend on abstractions (Chart, Exporter)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol, runtime_checkable
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm


@dataclass
class ChartConfig:
    """Configuration for chart appearance and export."""

    # Dimensions
    width: float = 8.0          # inches
    height: float = 5.0         # inches
    dpi: int = 300              # for raster export

    # Typography
    font_family: str = "Lexend"
    font_size_title: int = 16
    font_size_label: int = 12
    font_size_tick: int = 10
    font_size_annotation: int = 9

    # Colors
    background_color: str = "#FFFFFF"
    text_color: str = "#1A1A2E"
    grid_color: str = "#E5E5E5"

    # Export
    formats: list[str] = field(default_factory=lambda: ["svg", "png", "pdf"])

    # PDF settings for editable text
    pdf_fonttype: int = 42
    svg_fonttype: str = "none"


@dataclass
class ChartData:
    """Container for chart data with metadata."""

    values: Any                 # DataFrame, array, or dict
    title: str = ""
    subtitle: str = ""
    x_label: str = ""
    y_label: str = ""
    source: str = ""
    notes: str = ""
    chart_id: str = ""          # Unique identifier for referencing


@runtime_checkable
class Exporter(Protocol):
    """Protocol for chart exporters (Interface Segregation)."""

    def export(self, fig: plt.Figure, path: Path, config: ChartConfig) -> Path:
        """Export figure to file, return path."""
        ...


class Chart(ABC):
    """
    Abstract base chart class (Abstraction + Inheritance).

    Subclasses implement render() for specific chart types (Polymorphism).
    Data and config are encapsulated (Encapsulation).
    """

    def __init__(self, data: ChartData, config: ChartConfig | None = None):
        self._data = data
        self._config = config or ChartConfig()
        self._fig: plt.Figure | None = None
        self._ax: plt.Axes | None = None
        self._setup_fonts()

    def _setup_fonts(self) -> None:
        """Configure matplotlib for publication-quality fonts."""
        # Try to use Lexend, fall back to system sans-serif
        available_fonts = {f.name for f in fm.fontManager.ttflist}

        if self._config.font_family in available_fonts:
            plt.rcParams['font.family'] = 'sans-serif'
            plt.rcParams['font.sans-serif'] = [self._config.font_family]
        else:
            # Fallback fonts in order of preference
            fallbacks = ['Inter', 'Helvetica Neue', 'Arial', 'DejaVu Sans']
            for font in fallbacks:
                if font in available_fonts:
                    plt.rcParams['font.sans-serif'] = [font]
                    break

        # PDF/SVG settings for editable text
        plt.rcParams['pdf.fonttype'] = self._config.pdf_fonttype
        plt.rcParams['svg.fonttype'] = self._config.svg_fonttype

    @property
    def data(self) -> ChartData:
        """Access chart data (Encapsulation)."""
        return self._data

    @property
    def config(self) -> ChartConfig:
        """Access chart configuration (Encapsulation)."""
        return self._config

    @property
    def figure(self) -> plt.Figure | None:
        """Access rendered figure."""
        return self._fig

    def create_figure(self) -> tuple[plt.Figure, plt.Axes]:
        """Create figure with configured dimensions and styling."""
        fig, ax = plt.subplots(
            figsize=(self._config.width, self._config.height),
            dpi=self._config.dpi,
            facecolor=self._config.background_color
        )
        ax.set_facecolor(self._config.background_color)

        # Style axes
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(self._config.grid_color)
        ax.spines['bottom'].set_color(self._config.grid_color)

        # Grid
        ax.grid(True, axis='y', color=self._config.grid_color,
                linestyle='-', linewidth=0.5, alpha=0.7)
        ax.set_axisbelow(True)

        # Tick styling
        ax.tick_params(colors=self._config.text_color,
                       labelsize=self._config.font_size_tick)

        self._fig = fig
        self._ax = ax
        return fig, ax

    def add_labels(self) -> None:
        """Add title, labels, and annotations."""
        if self._ax is None:
            return

        if self._data.title:
            self._ax.set_title(
                self._data.title,
                fontsize=self._config.font_size_title,
                fontweight='bold',
                color=self._config.text_color,
                pad=20
            )

        if self._data.x_label:
            self._ax.set_xlabel(
                self._data.x_label,
                fontsize=self._config.font_size_label,
                color=self._config.text_color
            )

        if self._data.y_label:
            self._ax.set_ylabel(
                self._data.y_label,
                fontsize=self._config.font_size_label,
                color=self._config.text_color
            )

        # Source annotation
        if self._data.source:
            self._fig.text(
                0.99, 0.01, f"Source: {self._data.source}",
                ha='right', va='bottom',
                fontsize=self._config.font_size_annotation,
                color='#666666',
                transform=self._fig.transFigure
            )

    @abstractmethod
    def render(self) -> plt.Figure:
        """
        Render the chart (Template Method pattern).

        Subclasses implement specific visualization logic.
        """
        pass

    def save(self, output_dir: Path, exporters: list[Exporter] | None = None) -> list[Path]:
        """Export chart to configured formats."""
        if self._fig is None:
            self.render()

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        paths = []
        base_name = self._data.chart_id or "chart"

        for fmt in self._config.formats:
            path = output_dir / f"{base_name}.{fmt}"
            self._fig.savefig(
                path,
                format=fmt,
                dpi=self._config.dpi,
                bbox_inches='tight',
                facecolor=self._config.background_color,
                edgecolor='none'
            )
            paths.append(path)

        return paths

    def close(self) -> None:
        """Close figure to free memory."""
        if self._fig:
            plt.close(self._fig)
            self._fig = None
            self._ax = None
