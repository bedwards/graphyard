"""
Sabermetrics Pioneers article data loaders.

Validates and extends the work of Bill James, Mike Gimbel, and STATS, Inc.
"""

from .data import (
    load_pythagorean_validation,
    load_pythagorean_accuracy_by_decade,
    load_runs_created_validation,
    load_runs_created_historical,
    load_home_run_evolution,
    load_batting_average_evolution,
    load_strikeout_walk_evolution,
    load_stolen_base_evolution,
    load_era_definitions,
    load_legendary_seasons,
    load_pythagorean_outliers,
)

__all__ = [
    "load_pythagorean_validation",
    "load_pythagorean_accuracy_by_decade",
    "load_runs_created_validation",
    "load_runs_created_historical",
    "load_home_run_evolution",
    "load_batting_average_evolution",
    "load_strikeout_walk_evolution",
    "load_stolen_base_evolution",
    "load_era_definitions",
    "load_legendary_seasons",
    "load_pythagorean_outliers",
]
