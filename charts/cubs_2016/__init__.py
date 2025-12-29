"""2016 Chicago Cubs analytics and retrospective data."""

from .data import (
    load_cubs_rebuild_arc,
    load_key_acquisitions_war,
    load_epstein_trades_analysis,
    load_draft_pick_outcomes,
    load_tango_metrics_2016,
    load_championship_window_comparison,
    load_what_went_wrong,
    load_arrieta_transformation,
    load_hendricks_value,
)

__all__ = [
    "load_cubs_rebuild_arc",
    "load_key_acquisitions_war",
    "load_epstein_trades_analysis",
    "load_draft_pick_outcomes",
    "load_tango_metrics_2016",
    "load_championship_window_comparison",
    "load_what_went_wrong",
    "load_arrieta_transformation",
    "load_hendricks_value",
]
