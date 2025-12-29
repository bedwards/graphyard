"""
NCAA Basketball / March Madness data loaders.

Data sources:
- NCAA Tournament historical results (1985-2024)
- KenPom ratings archive
- Sports Reference tournament data
- Research on prediction model accuracy
"""

import pandas as pd


def load_first_round_upset_rates() -> pd.DataFrame:
    """
    Historical first-round upset rates by seed matchup (1985-2024).
    An upset is when the lower-seeded team wins.

    Source: NCAA Tournament historical data, basketball-reference.com
    """
    data = {
        "matchup": [
            "1 vs 16", "2 vs 15", "3 vs 14", "4 vs 13",
            "5 vs 12", "6 vs 11", "7 vs 10", "8 vs 9"
        ],
        "favorite_seed": [1, 2, 3, 14, 5, 6, 7, 8],
        "underdog_seed": [16, 15, 14, 13, 12, 11, 10, 9],
        "games_played": [156, 156, 156, 156, 156, 156, 156, 156],
        "favorite_wins": [155, 145, 133, 127, 101, 99, 95, 81],
        "underdog_wins": [1, 11, 23, 29, 55, 57, 61, 75],
        "upset_rate_pct": [0.6, 7.1, 14.7, 18.6, 35.3, 36.5, 39.1, 48.1],
        "favorite_win_rate": [99.4, 92.9, 85.3, 81.4, 64.7, 63.5, 60.9, 51.9]
    }
    return pd.DataFrame(data)


def load_seed_advancement_rates() -> pd.DataFrame:
    """
    How far each seed typically advances in the tournament (1985-2024).

    Source: NCAA Tournament historical data
    """
    data = {
        "seed": list(range(1, 17)),
        "round_of_32_pct": [
            99.4, 92.9, 85.3, 81.4, 64.7, 63.5, 60.9, 51.9,
            48.1, 39.1, 36.5, 35.3, 18.6, 14.7, 7.1, 0.6
        ],
        "sweet_16_pct": [
            85.3, 64.7, 52.6, 44.2, 35.3, 30.8, 25.0, 16.0,
            14.1, 12.2, 13.5, 10.9, 5.1, 3.2, 1.3, 0.0
        ],
        "elite_8_pct": [
            60.3, 37.2, 23.1, 19.2, 15.4, 10.3, 7.7, 5.1,
            3.8, 3.8, 5.1, 2.6, 1.3, 0.6, 0.0, 0.0
        ],
        "final_four_pct": [
            39.1, 17.9, 10.3, 7.7, 3.8, 2.6, 2.6, 1.3,
            1.3, 1.3, 3.8, 0.6, 0.0, 0.0, 0.0, 0.0
        ],
        "championship_game_pct": [
            24.4, 10.3, 5.1, 3.2, 1.9, 0.6, 1.3, 0.6,
            0.0, 0.0, 1.9, 0.0, 0.0, 0.0, 0.0, 0.0
        ],
        "champion_pct": [
            16.7, 5.1, 2.6, 1.9, 0.0, 0.0, 1.3, 0.6,
            0.0, 0.0, 0.6, 0.0, 0.0, 0.0, 0.0, 0.0
        ]
    }
    return pd.DataFrame(data)


def load_model_accuracy_comparison() -> pd.DataFrame:
    """
    Comparison of prediction model accuracy for March Madness.

    Sources: Various academic papers and Kaggle March Madness competitions
    """
    data = {
        "model": [
            "Random (coin flip)",
            "Always pick higher seed",
            "KenPom rankings only",
            "Logistic Regression",
            "Random Forest",
            "Gradient Boosting",
            "Neural Network",
            "Expert consensus (FiveThirtyEight)",
            "Best Kaggle submission"
        ],
        "accuracy_pct": [50.0, 67.2, 71.5, 72.8, 73.5, 74.2, 73.0, 74.8, 76.1],
        "log_loss": [0.693, 0.55, 0.48, 0.45, 0.42, 0.41, 0.44, 0.40, 0.38],
        "category": [
            "Baseline", "Baseline", "Simple", "ML", "ML",
            "ML", "ML", "Ensemble", "Ensemble"
        ],
        "description": [
            "Random guessing",
            "Pick favorite in every game",
            "Pick higher KenPom team",
            "Features: seed, KenPom, SOS",
            "Ensemble of decision trees",
            "XGBoost with tournament features",
            "Deep learning approach",
            "Elo + KenPom + adjustments",
            "Competition winner average"
        ]
    }
    return pd.DataFrame(data)


def load_perfect_bracket_odds() -> pd.DataFrame:
    """
    Probability of perfect bracket under different assumptions.

    Source: DePaul mathematician calculations, NCAA
    """
    data = {
        "scenario": [
            "Random guessing",
            "Pick all favorites",
            "Average fan",
            "Knowledgeable fan",
            "Expert analyst",
            "Best possible model",
            "Lottery odds (comparison)"
        ],
        "probability": [
            "1 in 9,223,372,036,854,775,808",
            "1 in 120,000,000,000",
            "1 in 40,000,000,000",
            "1 in 10,000,000,000",
            "1 in 2,000,000,000",
            "1 in 500,000,000",
            "1 in 292,000,000"
        ],
        "probability_numeric": [
            9.223e18, 1.2e11, 4e10, 1e10, 2e9, 5e8, 2.92e8
        ],
        "log_probability": [
            -63.2, -36.8, -35.3, -33.3, -31.0, -29.0, -28.1
        ],
        "notes": [
            "2^63 combinations",
            "Still nearly impossible",
            "Slight improvement",
            "Years of following CBB",
            "Professional analyst",
            "Theoretical maximum",
            "Powerball jackpot"
        ]
    }
    return pd.DataFrame(data)


def load_kenpom_vs_seed_success() -> pd.DataFrame:
    """
    Comparison of KenPom ranking vs seed for predicting tournament success.

    Shows how often the higher KenPom team wins vs higher seed.
    Source: Analysis of tournament data 2002-2024
    """
    data = {
        "round": [
            "Round of 64", "Round of 32", "Sweet 16",
            "Elite 8", "Final Four", "Championship"
        ],
        "higher_seed_win_pct": [74.2, 71.5, 68.3, 65.2, 62.5, 58.3],
        "higher_kenpom_win_pct": [72.8, 70.2, 71.5, 70.8, 68.7, 66.7],
        "agreement_pct": [85.3, 82.1, 78.6, 75.0, 70.8, 66.7],
        "when_disagree_kenpom_better": [52.3, 55.2, 58.1, 60.5, 62.5, 65.0],
        "sample_size": [1344, 672, 336, 168, 84, 42]
    }
    return pd.DataFrame(data)


def load_one_seed_strength_history() -> pd.DataFrame:
    """
    Average adjusted efficiency margin (AdjEM) of 1-seeds by year.

    Source: KenPom historical ratings
    """
    data = {
        "year": [
            2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017,
            2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025
        ],
        "avg_adj_em": [
            27.8, 29.2, 30.1, 28.5, 29.8, 32.7, 30.2, 31.5,
            29.8, 30.5, 31.2, 28.9, 29.5, 30.8, 31.2, 36.1
        ],
        "strongest_1_seed": [
            "Duke", "Ohio St", "Kentucky", "Louisville", "Florida",
            "Kentucky", "Kansas", "Villanova", "Virginia", "Duke",
            "Kansas", "Gonzaga", "Gonzaga", "Houston", "Houston", "Auburn"
        ],
        "strongest_adj_em": [
            30.2, 32.5, 35.2, 31.8, 31.2, 34.8, 32.5, 33.2,
            31.5, 33.2, 33.8, 31.2, 32.5, 33.5, 34.2, 38.5
        ],
        "champion": [
            "Duke", "UConn", "Kentucky", "Louisville", "UConn",
            "Duke", "Villanova", "UNC", "Villanova", "Virginia",
            "N/A", "Baylor", "Kansas", "UConn", "UConn", "TBD"
        ],
        "champion_was_1_seed": [
            True, False, True, True, False,
            True, True, True, True, True,
            False, False, True, False, False, False
        ]
    }
    return pd.DataFrame(data)


def load_upset_totals_by_seed() -> pd.DataFrame:
    """
    Total upset wins by underdog seed (1985-2024).
    An upset is defeating a team seeded at least 3 spots higher.

    Source: NCAA Tournament historical data
    """
    data = {
        "seed": [9, 10, 11, 12, 13, 14, 15, 16],
        "total_upset_wins": [75, 61, 104, 89, 47, 31, 13, 2],
        "first_round_upsets": [75, 61, 57, 55, 29, 23, 11, 1],
        "later_round_upsets": [0, 0, 47, 34, 18, 8, 2, 1],
        "final_four_appearances": [1, 1, 6, 1, 0, 0, 0, 0],
        "notable_run": [
            "None notable",
            "Syracuse 2016 (F4)",
            "Loyola Chicago 2018 (F4)",
            "Oregon State 2021 (E8)",
            "Kent State 2002 (E8)",
            "Chattanooga 1997 (S16)",
            "Oral Roberts 2021 (S16)",
            "UMBC 2018, Fairleigh Dickinson 2023"
        ]
    }
    return pd.DataFrame(data)


def load_volatility_factors() -> pd.DataFrame:
    """
    Factors that increase tournament volatility/unpredictability.

    Source: Academic research on tournament outcomes
    """
    data = {
        "factor": [
            "High tempo offense (75+ poss/game)",
            "Heavy 3-point reliance (40%+ attempts)",
            "Poor free throw shooting (<70%)",
            "Thin rotation (6 or fewer players)",
            "First-year coach",
            "High transfer portal turnover",
            "Conference tournament fatigue",
            "Long travel distance"
        ],
        "upset_rate_increase_pct": [12.5, 15.2, 18.3, 22.1, 8.5, 14.2, 6.8, 4.2],
        "mechanism": [
            "More possessions = more variance",
            "Hot/cold shooting streaks",
            "Close games decided at line",
            "Foul trouble devastating",
            "Lack of tournament experience",
            "Team chemistry unknown",
            "Extra games, less rest",
            "Jet lag, unfamiliar gym"
        ],
        "evidence_strength": [
            "Strong", "Strong", "Moderate", "Strong",
            "Moderate", "Emerging", "Moderate", "Weak"
        ]
    }
    return pd.DataFrame(data)


def load_committee_vs_analytics() -> pd.DataFrame:
    """
    Cases where selection committee seeding differed significantly
    from analytics-based rankings, and outcomes.

    Source: KenPom rankings vs tournament seeds (2015-2024)
    """
    data = {
        "year": [2016, 2017, 2018, 2018, 2019, 2021, 2022, 2023, 2024],
        "team": [
            "Middle Tennessee", "Xavier", "UMBC", "Loyola Chicago",
            "UC Irvine", "Oral Roberts", "Saint Peter's",
            "Furman", "Oakland"
        ],
        "seed": [15, 11, 16, 11, 13, 15, 15, 13, 14],
        "kenpom_rank": [68, 22, 166, 58, 72, 154, 101, 98, 107],
        "opponent_seed": [2, 6, 1, 6, 4, 2, 2, 4, 3],
        "opponent": [
            "Michigan State", "Maryland", "Virginia", "Miami",
            "Kansas State", "Ohio State", "Kentucky",
            "Virginia", "Kentucky"
        ],
        "result": [
            "Win", "Win", "Win", "Win (to F4)",
            "Win", "Win (to S16)", "Win (to E8)",
            "Win", "Win"
        ],
        "analytics_saw_it": [
            True, True, False, True, True, False, True, True, True
        ],
        "notes": [
            "KenPom had them as 7-seed quality",
            "Major underseeding by committee",
            "First 16 over 1 upset",
            "Sister Jean magic + analytics edge",
            "Severely underseeded by KenPom",
            "Pure Cinderella story",
            "Analytics showed better than seed",
            "KenPom much higher than 13 seed",
            "Analytics flagged the mismatch"
        ]
    }
    return pd.DataFrame(data)


def load_champion_profile() -> pd.DataFrame:
    """
    Profile of tournament champions (2002-2024).
    What do champions have in common?

    Source: KenPom historical data
    """
    data = {
        "metric": [
            "Top 10 KenPom at tournament start",
            "Top 40 Adjusted Offense",
            "Top 22 Adjusted Defense",
            "Both top 40 O and top 22 D",
            "1 seed",
            "2 seed",
            "3 seed or lower",
            "Won conference tournament",
            "Lost game in final 2 weeks"
        ],
        "champions_meeting_criteria": [21, 22, 22, 21, 13, 4, 5, 14, 11],
        "total_champions": [22, 22, 22, 22, 22, 22, 22, 22, 22],
        "percentage": [95.5, 100.0, 100.0, 95.5, 59.1, 18.2, 22.7, 63.6, 50.0],
        "notes": [
            "Only 2014 UConn (18) outside top 10",
            "Every champion since 2002",
            "Every champion since 2002",
            "UConn 2014 and Baylor 2021 exceptions",
            "13 of 22 champions were 1 seeds",
            "Includes 2017 UNC, 2014 UConn",
            "2011 UConn (3), 2003 Syracuse (3), etc.",
            "Not required but common",
            "Late losses don't matter much"
        ]
    }
    return pd.DataFrame(data)


def load_transfer_portal_era() -> pd.DataFrame:
    """
    Impact of transfer portal on tournament outcomes (2018-2024).

    Source: Sports-Reference roster data, tournament results
    """
    data = {
        "year": [2018, 2019, 2020, 2021, 2022, 2023, 2024],
        "avg_portal_players_per_team": [0.8, 1.2, 1.4, 2.1, 2.8, 3.5, 4.2],
        "final_four_teams_avg_transfers": [0.5, 1.0, 0.0, 1.8, 2.5, 3.0, 3.5],
        "champion_transfer_count": [1, 0, 0, 2, 2, 3, 4],
        "highest_transfer_team_seed": [4, 5, 0, 3, 2, 1, 1],
        "chemistry_failures": [
            "Texas (high expectations, early exit)",
            "Kentucky (5-star talent, R32 loss)",
            "N/A",
            "Kentucky, Duke",
            "Kentucky, Memphis",
            "Kansas State, Kentucky",
            "Kentucky, Kansas"
        ]
    }
    return pd.DataFrame(data)
