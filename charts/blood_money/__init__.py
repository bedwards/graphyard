"""
Blood Money: Chart data for taxpayer complicity in state violence.

This module provides data for visualizing:
- Military spending trends
- Tax burden distribution
- Atrocity costs and casualties
- Historical democide
- Individual taxpayer contributions
"""

from .data import (
    # Core military and tax data
    get_us_military_tax_share,
    get_global_military_spending,
    get_top_military_spenders,
    get_us_war_costs,
    get_us_military_spending_history,
    get_median_taxpayer_contribution,
    # Drone strike data
    get_drone_strikes_by_year,
    get_drone_strikes_by_year_total,
    get_drone_casualties_by_country,
    get_drone_casualties_by_president,
    # Historical atrocities
    get_historical_democide,
    get_democide_timeline,
    get_democide_by_century,
    get_famine_deaths,
    # Post-9/11 wars
    get_post_911_deaths,
    get_defense_contractors,
    get_afghanistan_costs_by_year,
    get_iraq_costs_by_year,
    get_cumulative_war_costs,
    get_veterans_cost_projection,
    get_interest_on_war_debt,
    # Tax and inequality
    get_tax_structure_comparison,
    get_income_inequality_trends,
    # Conflict data
    get_conflict_deaths_by_year,
    get_civilian_combatant_ratio,
    # Foreign military support
    get_military_aid_israel,
    get_yemen_casualties,
    get_gaza_casualties,
    get_ukraine_aid,
    # Comparative analysis
    get_cost_per_death_comparison,
    get_gdp_vs_military_spending,
    get_military_spending_by_president,
    get_cold_war_spending_eras,
    get_central_america_deaths,
    # Moral/political
    get_war_tax_resistance_history,
    get_antiwar_protest_sizes,
    get_public_opinion_wars,
    get_spending_by_party,
    # Lifetime taxpayer analysis
    get_taxpayer_cumulative_contribution,
    get_deaths_per_taxpayer,
    # Chapter 1: Accounting of Death
    get_deaths_by_type_20c,
    get_ucdp_vs_rummel_comparison,
    get_direct_indirect_ratio,
    get_death_counting_methods,
    get_conflict_deaths_trends,
    get_civilian_military_deaths,
)

__all__ = [
    # Core military and tax data
    'get_us_military_tax_share',
    'get_global_military_spending',
    'get_top_military_spenders',
    'get_us_war_costs',
    'get_us_military_spending_history',
    'get_median_taxpayer_contribution',
    # Drone strike data
    'get_drone_strikes_by_year',
    'get_drone_strikes_by_year_total',
    'get_drone_casualties_by_country',
    'get_drone_casualties_by_president',
    # Historical atrocities
    'get_historical_democide',
    'get_democide_timeline',
    'get_democide_by_century',
    'get_famine_deaths',
    # Post-9/11 wars
    'get_post_911_deaths',
    'get_defense_contractors',
    'get_afghanistan_costs_by_year',
    'get_iraq_costs_by_year',
    'get_cumulative_war_costs',
    'get_veterans_cost_projection',
    'get_interest_on_war_debt',
    # Tax and inequality
    'get_tax_structure_comparison',
    'get_income_inequality_trends',
    # Conflict data
    'get_conflict_deaths_by_year',
    'get_civilian_combatant_ratio',
    # Foreign military support
    'get_military_aid_israel',
    'get_yemen_casualties',
    'get_gaza_casualties',
    'get_ukraine_aid',
    # Comparative analysis
    'get_cost_per_death_comparison',
    'get_gdp_vs_military_spending',
    'get_military_spending_by_president',
    'get_cold_war_spending_eras',
    'get_central_america_deaths',
    # Moral/political
    'get_war_tax_resistance_history',
    'get_antiwar_protest_sizes',
    'get_public_opinion_wars',
    'get_spending_by_party',
    # Lifetime taxpayer analysis
    'get_taxpayer_cumulative_contribution',
    'get_deaths_per_taxpayer',
    # Chapter 1: Accounting of Death
    'get_deaths_by_type_20c',
    'get_ucdp_vs_rummel_comparison',
    'get_direct_indirect_ratio',
    'get_death_counting_methods',
    'get_conflict_deaths_trends',
    'get_civilian_military_deaths',
]
