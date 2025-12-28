"""
Chart Registry - Factory pattern for chart creation.

Follows Open/Closed principle: add new chart types without modifying registry.
"""

from typing import Type, Callable
from .base import Chart, ChartConfig, ChartData


class ChartRegistry:
    """
    Registry for chart types (Factory + Registry patterns).

    Enables adding new chart types without modifying existing code.
    """

    _charts: dict[str, Type[Chart]] = {}
    _aliases: dict[str, str] = {}

    @classmethod
    def register(cls, name: str, aliases: list[str] | None = None) -> Callable:
        """
        Decorator to register a chart class.

        Usage:
            @ChartRegistry.register("line", aliases=["timeseries"])
            class LineChart(Chart):
                ...
        """
        def decorator(chart_class: Type[Chart]) -> Type[Chart]:
            cls._charts[name] = chart_class
            if aliases:
                for alias in aliases:
                    cls._aliases[alias] = name
            return chart_class
        return decorator

    @classmethod
    def create(
        cls,
        chart_type: str,
        data: ChartData,
        config: ChartConfig | None = None
    ) -> Chart:
        """Create a chart instance by type name."""
        # Resolve alias
        resolved_type = cls._aliases.get(chart_type, chart_type)

        if resolved_type not in cls._charts:
            available = list(cls._charts.keys()) + list(cls._aliases.keys())
            raise ValueError(
                f"Unknown chart type: {chart_type}. "
                f"Available: {', '.join(sorted(available))}"
            )

        chart_class = cls._charts[resolved_type]
        return chart_class(data, config)

    @classmethod
    def list_types(cls) -> list[str]:
        """List all registered chart types."""
        return sorted(cls._charts.keys())

    @classmethod
    def list_aliases(cls) -> dict[str, str]:
        """List all aliases and their targets."""
        return dict(cls._aliases)
