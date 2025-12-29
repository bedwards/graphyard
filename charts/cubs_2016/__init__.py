"""2016 Chicago Cubs analytics and retrospective data."""

from .data import (
    load_cubs_rebuild_arc,
    load_key_acquisitions_war,
    load_epstein_trades_analysis,
    load_draft_pick_outcomes,
    load_woba_2016,
    load_fip_vs_era_2016,
    load_leverage_index_2016,
    load_tango_metrics_2016,
    load_championship_window_comparison,
    load_what_went_wrong,
    load_arrieta_transformation,
    load_hendricks_value,
    load_war_prediction_model,
)

__all__ = [
    "load_cubs_rebuild_arc",
    "load_key_acquisitions_war",
    "load_epstein_trades_analysis",
    "load_draft_pick_outcomes",
    "load_woba_2016",
    "load_fip_vs_era_2016",
    "load_leverage_index_2016",
    "load_tango_metrics_2016",
    "load_championship_window_comparison",
    "load_what_went_wrong",
    "load_arrieta_transformation",
    "load_hendricks_value",
    "load_war_prediction_model",
]
