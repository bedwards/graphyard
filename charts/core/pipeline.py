"""
Chart Pipeline - Batch processing for article charts.

Handles the complete workflow: data loading → chart creation → export.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable
import json

from .base import Chart, ChartConfig, ChartData
from .registry import ChartRegistry


@dataclass
class ChartSpec:
    """Specification for a single chart in the pipeline."""

    chart_id: str
    chart_type: str
    title: str
    data_source: str | Callable[[], Any]  # File path or data loader function
    x_label: str = ""
    y_label: str = ""
    source: str = ""
    notes: str = ""
    subtitle: str = ""
    config_overrides: dict = field(default_factory=dict)


class ChartPipeline:
    """
    Pipeline for batch chart production.

    Features:
    - Declarative chart specifications
    - Automatic data loading
    - Parallel export to multiple formats
    - Manifest generation for article integration
    """

    def __init__(
        self,
        output_dir: Path,
        base_config: ChartConfig | None = None
    ):
        self.output_dir = Path(output_dir)
        self.base_config = base_config or ChartConfig()
        self.specs: list[ChartSpec] = []
        self._charts: dict[str, Chart] = {}
        self._manifest: dict[str, dict] = {}

    def add(self, spec: ChartSpec) -> "ChartPipeline":
        """Add a chart specification (fluent interface)."""
        self.specs.append(spec)
        return self

    def add_many(self, specs: list[ChartSpec]) -> "ChartPipeline":
        """Add multiple chart specifications."""
        self.specs.extend(specs)
        return self

    def _load_data(self, spec: ChartSpec) -> Any:
        """Load data from source."""
        if callable(spec.data_source):
            return spec.data_source()
        elif isinstance(spec.data_source, str):
            path = Path(spec.data_source)
            if path.suffix == '.json':
                return json.loads(path.read_text())
            elif path.suffix == '.csv':
                import pandas as pd
                return pd.read_csv(path)
            elif path.suffix == '.parquet':
                import pandas as pd
                return pd.read_parquet(path)
            else:
                raise ValueError(f"Unsupported data format: {path.suffix}")
        else:
            # Assume it's already data
            return spec.data_source

    def _create_config(self, spec: ChartSpec) -> ChartConfig:
        """Create config with spec overrides."""
        if not spec.config_overrides:
            return self.base_config

        # Create new config with overrides
        config_dict = {
            'width': self.base_config.width,
            'height': self.base_config.height,
            'dpi': self.base_config.dpi,
            'font_family': self.base_config.font_family,
            'font_size_title': self.base_config.font_size_title,
            'font_size_label': self.base_config.font_size_label,
            'font_size_tick': self.base_config.font_size_tick,
            'font_size_annotation': self.base_config.font_size_annotation,
            'background_color': self.base_config.background_color,
            'text_color': self.base_config.text_color,
            'grid_color': self.base_config.grid_color,
            'formats': self.base_config.formats,
        }
        config_dict.update(spec.config_overrides)
        return ChartConfig(**config_dict)

    def build(self) -> dict[str, Chart]:
        """Build all charts from specifications."""
        for spec in self.specs:
            # Load data
            values = self._load_data(spec)

            # Create chart data
            chart_data = ChartData(
                values=values,
                title=spec.title,
                subtitle=spec.subtitle,
                x_label=spec.x_label,
                y_label=spec.y_label,
                source=spec.source,
                notes=spec.notes,
                chart_id=spec.chart_id,
            )

            # Create config
            config = self._create_config(spec)

            # Create chart
            chart = ChartRegistry.create(spec.chart_type, chart_data, config)
            self._charts[spec.chart_id] = chart

        return self._charts

    def render_all(self) -> "ChartPipeline":
        """Render all charts."""
        for chart in self._charts.values():
            chart.render()
        return self

    def export_all(self) -> dict[str, list[Path]]:
        """Export all charts and generate manifest."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        results = {}

        for chart_id, chart in self._charts.items():
            paths = chart.save(self.output_dir)
            results[chart_id] = paths

            # Add to manifest
            self._manifest[chart_id] = {
                'title': chart.data.title,
                'files': {p.suffix[1:]: str(p.name) for p in paths},
                'source': chart.data.source,
                'notes': chart.data.notes,
            }

        # Write manifest
        manifest_path = self.output_dir / 'manifest.json'
        manifest_path.write_text(json.dumps(self._manifest, indent=2))

        return results

    def run(self) -> dict[str, list[Path]]:
        """Execute full pipeline: build → render → export."""
        self.build()
        self.render_all()
        return self.export_all()

    def cleanup(self) -> None:
        """Close all figures to free memory."""
        for chart in self._charts.values():
            chart.close()
        self._charts.clear()
