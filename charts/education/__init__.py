"""
Education article data loaders.

Evidence-based analysis of learning myths, international test scores, pedagogy,
Texas education policy, school choice, and machine learning predictions.
"""

from .data import (
    # Original loaders
    load_learning_styles_meta_analysis,
    load_learning_styles_belief_rates,
    load_pisa_math_scores_over_time,
    load_pisa_2022_rankings,
    load_finland_decline,
    load_spending_vs_outcomes,
    load_us_state_spending_outcomes,
    load_homework_effect_by_grade,
    load_effect_size_comparison,
    # Texas education
    load_texas_school_types,
    load_texas_district_performance,
    load_waco_schools_detail,
    load_texas_staar_trends,
    load_waco_staar_trends,
    load_staar_by_demographics,
    # School choice
    load_voucher_academic_effects,
    load_voucher_participation,
    load_charter_outcomes_credo,
    load_private_public_comparison,
    load_selection_bias_evidence,
    # Teacher compensation
    load_teacher_salary_by_state,
    load_texas_teacher_trends,
    # NAEP trends
    load_naep_reading_trends,
    load_naep_math_trends,
    load_naep_achievement_gaps,
    # Life outcomes
    load_education_earnings,
    load_education_outcomes_age25,
    load_early_childhood_roi,
    # School funding
    load_texas_funding_by_district,
    load_national_funding_comparison,
    # Alternative pathways
    load_dual_credit_outcomes,
    load_ged_vs_diploma,
    load_trade_school_outcomes,
    # Science of reading
    load_reading_instruction_research,
    # ML predictions
    predict_district_performance,
    predict_school_choice_migration,
    predict_literacy_rates,
    predict_failing_schools,
)

__all__ = [
    # Original loaders
    "load_learning_styles_meta_analysis",
    "load_learning_styles_belief_rates",
    "load_pisa_math_scores_over_time",
    "load_pisa_2022_rankings",
    "load_finland_decline",
    "load_spending_vs_outcomes",
    "load_us_state_spending_outcomes",
    "load_homework_effect_by_grade",
    "load_effect_size_comparison",
    # Texas education
    "load_texas_school_types",
    "load_texas_district_performance",
    "load_waco_schools_detail",
    "load_texas_staar_trends",
    "load_waco_staar_trends",
    "load_staar_by_demographics",
    # School choice
    "load_voucher_academic_effects",
    "load_voucher_participation",
    "load_charter_outcomes_credo",
    "load_private_public_comparison",
    "load_selection_bias_evidence",
    # Teacher compensation
    "load_teacher_salary_by_state",
    "load_texas_teacher_trends",
    # NAEP trends
    "load_naep_reading_trends",
    "load_naep_math_trends",
    "load_naep_achievement_gaps",
    # Life outcomes
    "load_education_earnings",
    "load_education_outcomes_age25",
    "load_early_childhood_roi",
    # School funding
    "load_texas_funding_by_district",
    "load_national_funding_comparison",
    # Alternative pathways
    "load_dual_credit_outcomes",
    "load_ged_vs_diploma",
    "load_trade_school_outcomes",
    # Science of reading
    "load_reading_instruction_research",
    # ML predictions
    "predict_district_performance",
    "predict_school_choice_migration",
    "predict_literacy_rates",
    "predict_failing_schools",
]
