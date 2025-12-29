"""
Education article data loaders.

Evidence-based analysis of learning myths, international test scores, and pedagogy.
"""

from .data import (
    load_learning_styles_meta_analysis,
    load_learning_styles_belief_rates,
    load_pisa_math_scores_over_time,
    load_pisa_2022_rankings,
    load_finland_decline,
    load_spending_vs_outcomes,
    load_us_state_spending_outcomes,
    load_homework_effect_by_grade,
    load_effect_size_comparison,
)

__all__ = [
    "load_learning_styles_meta_analysis",
    "load_learning_styles_belief_rates",
    "load_pisa_math_scores_over_time",
    "load_pisa_2022_rankings",
    "load_finland_decline",
    "load_spending_vs_outcomes",
    "load_us_state_spending_outcomes",
    "load_homework_effect_by_grade",
    "load_effect_size_comparison",
]
