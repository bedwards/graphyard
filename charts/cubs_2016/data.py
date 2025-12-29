"""
2016 Chicago Cubs data loaders.

Data sources:
- Baseball-Reference.com WAR data
- FanGraphs player valuations
- MLB transaction history
- Cubs draft history
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import TimeSeriesSplit


def load_cubs_rebuild_arc() -> pd.DataFrame:
    """
    Cubs win totals and playoff results 2011-2019.
    Shows the rebuild arc under Theo Epstein through the window closing.

    Source: Baseball-Reference.com
    """
    data = {
        "year": [2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019],
        "wins": [71, 61, 66, 73, 97, 103, 92, 95, 84],
        "losses": [91, 101, 96, 89, 65, 58, 69, 68, 78],
        "win_pct": [.438, .377, .407, .451, .599, .640, .571, .583, .519],
        "playoff_result": [
            "Missed", "Missed", "Missed", "Missed", "NLCS",
            "World Series Champion", "NLCS", "Wild Card Loss", "Missed"
        ],
        "division_rank": [5, 5, 5, 5, 3, 1, 1, 1, 3],
        "run_differential": [-61, -152, -118, -36, 143, 252, 111, 108, -2],
        "era": ["Pre-Epstein", "Rebuild", "Rebuild", "Rebuild", "Contention",
                "Championship", "Window", "Window", "Decline"],
        "notes": [
            "Last year before Epstein",
            "First Epstein year, tank begins",
            "Bryant drafted #2 overall",
            "Schwarber drafted #4, Russell acquired",
            "97 wins, NLCS loss to Mets",
            "108-year drought ends",
            "Lost NLCS to Dodgers 4-1",
            "Lost Wild Card to Rockies",
            "Core begins to age out"
        ]
    }
    return pd.DataFrame(data)


def load_key_acquisitions_war() -> pd.DataFrame:
    """
    WAR outcomes for key Cubs acquisitions under Epstein.
    Compares projected value at acquisition vs actual Cubs WAR.

    Source: Baseball-Reference.com WAR
    """
    data = {
        "player": [
            "Kris Bryant", "Kyle Schwarber", "Anthony Rizzo",
            "Addison Russell", "Jake Arrieta", "Kyle Hendricks",
            "Javier Baez", "Jon Lester", "Ben Zobrist",
            "Dexter Fowler", "Jason Heyward", "Wilson Contreras"
        ],
        "acquisition_type": [
            "Draft (2013)", "Draft (2014)", "Trade (2012)",
            "Trade (2014)", "Trade (2013)", "Trade (2012)",
            "Draft (2011)", "Free Agent (2015)", "Free Agent (2016)",
            "Trade (2015)", "Free Agent (2016)", "International (2009)"
        ],
        "cubs_war_2015_2020": [
            27.0, 5.8, 18.1,
            6.5, 16.5, 17.2,
            14.9, 9.8, 8.4,
            3.2, 5.3, 11.2
        ],
        "cost_or_pick": [
            "#2 overall", "#4 overall", "Andrew Cashner",
            "Samardzija/Hammel", "Feldman/Clevenger", "Ryan Dempster",
            "#9 overall", "$155M/6yr", "$56M/4yr",
            "Dan Straily", "$184M/8yr", "$2.8M bonus"
        ],
        "peak_war_season": [
            7.7, 2.4, 5.0,
            3.6, 7.3, 4.6,
            5.3, 2.7, 4.0,
            2.6, 1.8, 3.6
        ],
        "verdict": [
            "Home Run", "Solid", "Home Run",
            "Mixed (off-field issues)", "Home Run", "Home Run",
            "Home Run", "Good", "Good",
            "Good", "Bust", "Home Run"
        ]
    }
    return pd.DataFrame(data)


def load_epstein_trades_analysis() -> pd.DataFrame:
    """
    Detailed analysis of major Epstein trades.
    Compares what Cubs gave up vs what they received.

    Source: Baseball-Reference.com, FanGraphs
    """
    data = {
        "trade_date": [
            "Jan 2012", "Jul 2012", "Jul 2012", "Jul 2013",
            "Jul 2014", "Dec 2015", "Jul 2016"
        ],
        "trade_name": [
            "Rizzo Trade", "Hendricks Trade", "Dempster Trade",
            "Arrieta Trade", "Russell Trade", "Fowler Trade",
            "Chapman Trade"
        ],
        "cubs_received": [
            "Anthony Rizzo", "Kyle Hendricks", "Cash/Prospects",
            "Jake Arrieta, Pedro Strop", "Addison Russell, Billy McKinney",
            "Dexter Fowler", "Aroldis Chapman"
        ],
        "cubs_gave_up": [
            "Andrew Cashner", "Cash considerations", "Ryan Dempster",
            "Steve Clevenger, Scott Feldman", "Jeff Samardzija, Jason Hammel",
            "Dan Straily", "Gleyber Torres, Adam Warren, etc."
        ],
        "war_received_5yr": [18.1, 17.2, 0, 19.5, 7.5, 3.2, 1.4],
        "war_given_up_5yr": [3.1, 0, 5.8, 1.2, 8.2, 2.8, 22.4],
        "net_war": [15.0, 17.2, -5.8, 18.3, -0.7, 0.4, -21.0],
        "verdict": [
            "Massive Win", "Massive Win", "Loss",
            "Massive Win", "Push (but won WS)", "Push",
            "Lost trade, won title"
        ]
    }
    return pd.DataFrame(data)


def load_draft_pick_outcomes() -> pd.DataFrame:
    """
    Cubs draft picks 2011-2015 and their outcomes.

    Source: Baseball-Reference.com, MLB.com
    """
    data = {
        "year": [2011, 2011, 2012, 2012, 2013, 2013, 2014, 2014, 2015, 2015],
        "round": [1, 1, 1, 2, 1, 2, 1, 2, 1, 2],
        "pick": [9, 43, 6, 58, 2, 41, 4, 51, 9, 67],
        "player": [
            "Javier Baez", "Daniel Vogelbach", "Albert Almora Jr.", "Duane Underwood Jr.",
            "Kris Bryant", "Rob Zastryzny", "Kyle Schwarber", "Jake Stinnett",
            "Ian Happ", "Donnie Dewees"
        ],
        "position": [
            "SS/2B", "1B/DH", "CF", "RHP",
            "3B/OF", "LHP", "C/OF", "RHP",
            "OF/2B", "OF"
        ],
        "career_war": [14.9, 0.6, 1.9, 0.0, 27.0, -0.4, 7.8, 0.0, 10.5, -0.1],
        "cubs_war": [14.9, -0.2, 1.9, 0.0, 27.0, -0.4, 5.8, 0.0, 5.2, -0.1],
        "made_majors": [True, True, True, True, True, True, True, False, True, True],
        "all_star_appearances": [2, 0, 0, 0, 4, 0, 1, 0, 1, 0],
        "verdict": [
            "Star", "Bust (for Cubs)", "Useful", "Bust",
            "Superstar", "Bust", "Star", "Bust",
            "Star", "Bust"
        ]
    }
    return pd.DataFrame(data)


def load_woba_2016() -> pd.DataFrame:
    """
    2016 Cubs hitters wOBA vs league average.
    Demonstrates Tango's wOBA metric.

    Source: FanGraphs
    """
    data = {
        "player": [
            "Kris Bryant", "Anthony Rizzo", "Ben Zobrist", "Dexter Fowler",
            "Kyle Schwarber", "Javier Baez", "Addison Russell", "Jason Heyward",
            "League Average"
        ],
        "woba": [.396, .382, .371, .362, .355, .329, .311, .290, .320],
        "is_league_avg": [False, False, False, False, False, False, False, False, True],
    }
    return pd.DataFrame(data)


def load_fip_vs_era_2016() -> pd.DataFrame:
    """
    2016 Cubs pitchers ERA vs FIP comparison.
    Demonstrates how FIP reveals true performance.
    Shows ERA - FIP differential (negative = outperformed FIP).

    Source: FanGraphs
    """
    data = {
        "player": ["Kyle Hendricks", "Jon Lester", "Jake Arrieta", "John Lackey"],
        "era": [2.13, 2.44, 3.10, 3.35],
        "fip": [2.09, 3.44, 3.33, 4.14],
    }
    df = pd.DataFrame(data)
    df["era_minus_fip"] = df["era"] - df["fip"]
    return df


def load_leverage_index_2016() -> pd.DataFrame:
    """
    2016 Cubs bullpen usage by leverage index.
    Demonstrates Tango's Leverage Index concept.

    Source: FanGraphs
    """
    data = {
        "pitcher": [
            "Aroldis Chapman", "Hector Rondon", "Pedro Strop",
            "Carl Edwards Jr.", "Mike Montgomery", "Travis Wood"
        ],
        "avg_leverage": [1.89, 1.45, 1.32, 1.21, 0.95, 0.78],
        "high_leverage_pct": [68, 52, 48, 42, 31, 24],
        "role": ["Closer", "Setup", "Setup", "Middle", "Long", "Long"],
    }
    return pd.DataFrame(data)


def load_tango_metrics_2016() -> pd.DataFrame:
    """
    Tom Tango's key metrics for 2016 Cubs players.
    wOBA, FIP, and Leverage Index usage.

    Source: FanGraphs (metrics developed by Tom Tango)
    """
    data = {
        "player": [
            "Kris Bryant", "Anthony Rizzo", "Ben Zobrist", "Addison Russell",
            "Javier Baez", "Kyle Schwarber", "Dexter Fowler", "Jason Heyward",
            "Jake Arrieta", "Jon Lester", "Kyle Hendricks", "John Lackey"
        ],
        "position": [
            "3B", "1B", "2B/OF", "SS",
            "2B/SS", "OF/C", "CF", "RF",
            "SP", "SP", "SP", "SP"
        ],
        "woba_2016": [
            .396, .382, .371, .311,
            .329, .355, .362, .290,
            None, None, None, None
        ],
        "wrc_plus_2016": [
            148, 138, 126, 90,
            103, 122, 119, 72,
            None, None, None, None
        ],
        "fip_2016": [
            None, None, None, None,
            None, None, None, None,
            3.33, 3.44, 2.09, 4.14
        ],
        "era_2016": [
            None, None, None, None,
            None, None, None, None,
            3.10, 2.44, 2.13, 3.35
        ],
        "leverage_index_usage": [
            "High", "High", "High", "Medium",
            "High", "High", "High", "Medium",
            None, None, None, None
        ],
        "war_2016": [7.7, 4.7, 4.0, 2.6, 2.3, 0.5, 2.6, 1.6, 4.0, 2.5, 4.6, 1.7]
    }
    return pd.DataFrame(data)


def load_championship_window_comparison() -> pd.DataFrame:
    """
    Playoff depth by year for Cubs vs. comparable contenders.
    Shows how far each team advanced each postseason.

    Depth scoring:
    0 = Missed playoffs
    1 = Wild Card loss
    2 = Division Series loss
    3 = Championship Series loss
    4 = World Series loss
    5 = World Series win

    Source: Baseball-Reference.com
    """
    # Cubs 2015-2019 window
    cubs_data = [
        {"team": "Cubs", "year": 2015, "depth": 3, "result": "NLCS Loss"},
        {"team": "Cubs", "year": 2016, "depth": 5, "result": "WS Win"},
        {"team": "Cubs", "year": 2017, "depth": 3, "result": "NLCS Loss"},
        {"team": "Cubs", "year": 2018, "depth": 1, "result": "WC Loss"},
        {"team": "Cubs", "year": 2019, "depth": 0, "result": "Missed"},
    ]

    # Giants 2010-2014 "dynasty" - won 3 titles but missed playoffs twice
    giants_data = [
        {"team": "Giants", "year": 2010, "depth": 5, "result": "WS Win"},
        {"team": "Giants", "year": 2011, "depth": 0, "result": "Missed"},
        {"team": "Giants", "year": 2012, "depth": 5, "result": "WS Win"},
        {"team": "Giants", "year": 2013, "depth": 0, "result": "Missed"},
        {"team": "Giants", "year": 2014, "depth": 5, "result": "WS Win"},
    ]

    # Dodgers 2017-2020 - kept losing WS until finally winning
    dodgers_data = [
        {"team": "Dodgers", "year": 2017, "depth": 4, "result": "WS Loss"},
        {"team": "Dodgers", "year": 2018, "depth": 4, "result": "WS Loss"},
        {"team": "Dodgers", "year": 2019, "depth": 2, "result": "NLDS Loss"},
        {"team": "Dodgers", "year": 2020, "depth": 5, "result": "WS Win"},
    ]

    # Astros 2017-2019 (cheating era)
    astros_data = [
        {"team": "Astros*", "year": 2017, "depth": 5, "result": "WS Win*"},
        {"team": "Astros*", "year": 2018, "depth": 3, "result": "ALCS Loss"},
        {"team": "Astros*", "year": 2019, "depth": 4, "result": "WS Loss"},
    ]

    all_data = cubs_data + giants_data + dodgers_data + astros_data
    return pd.DataFrame(all_data)


def load_what_went_wrong() -> pd.DataFrame:
    """
    Player WAR change from 2016 to 2019.
    Shows which core players declined vs improved by 2019 (missed playoffs).

    Source: Baseball-Reference.com
    """
    data = {
        "player": [
            "Kris Bryant", "Anthony Rizzo", "Addison Russell",
            "Kyle Schwarber", "Javier Baez", "Jason Heyward",
            "Jon Lester", "Jake Arrieta"
        ],
        "war_2016": [7.7, 4.7, 2.6, 0.5, 2.3, 1.6, 2.5, 4.0],
        "war_2019": [4.8, 2.8, -0.3, 1.9, 5.3, 0.5, 1.9, 0.2],
        # WAR change: war_2019 - war_2016
        "war_change": [-2.9, -1.9, -2.9, 1.4, 3.0, -1.1, -0.6, -3.8],
        "primary_cause": [
            "Injuries, shoulder issues",
            "Natural aging (30+)",
            "Off-field issues, released",
            "Breakout year",
            "Career year at 26",
            "Never lived up to contract",
            "Age decline (35)",
            "Left in FA, declined with Phillies"
        ]
    }
    return pd.DataFrame(data)


def load_arrieta_transformation() -> pd.DataFrame:
    """
    Jake Arrieta's transformation under Cubs analytics.
    Shows the dramatic improvement after trade.

    Source: FanGraphs, Baseball-Reference.com
    """
    data = {
        "year": [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020],
        "team": [
            "Orioles", "Orioles", "Orioles", "Orioles",
            "Cubs", "Cubs", "Cubs", "Cubs",
            "Phillies", "Phillies", "Phillies"
        ],
        "era": [4.66, 5.05, 6.20, 4.78, 2.53, 1.77, 3.10, 3.53, 3.96, 4.64, 5.08],
        "fip": [4.95, 4.59, 4.97, 3.82, 2.98, 2.35, 3.33, 3.45, 3.98, 4.32, 4.57],
        "whip": [1.47, 1.41, 1.55, 1.28, 1.02, 0.86, 1.08, 1.22, 1.28, 1.38, 1.40],
        "war": [-0.6, 0.9, -0.1, 2.1, 4.4, 7.3, 4.0, 2.6, 1.8, 0.2, 0.5],
    }
    return pd.DataFrame(data)


def load_hendricks_value() -> pd.DataFrame:
    """
    Kyle Hendricks as an analytics success story.
    Acquired for cash, became ace.

    Source: FanGraphs, Baseball-Reference.com
    """
    data = {
        "season": [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023],
        "era": [2.46, 3.95, 2.13, 3.03, 3.44, 3.46, 2.88, 4.77, 4.80, 3.74],
        "fip": [3.34, 3.53, 2.09, 3.61, 3.98, 3.48, 3.25, 4.39, 4.54, 4.13],
        "war": [2.3, 2.7, 4.6, 3.5, 2.2, 3.0, 1.8, 0.2, 0.5, 1.3],
        "innings": [80.1, 180.0, 190.0, 189.2, 199.0, 177.0, 81.1, 181.0, 138.2, 161.0],
        "contract_value_millions": [0.5, 0.5, 0.5, 5.5, 7.4, 10.3, 12.5, 14.0, 14.0, 16.5],
        "surplus_value_estimate": [
            "High", "High", "Very High", "High",
            "Medium", "Medium", "High", "Low", "Low", "Low"
        ]
    }
    return pd.DataFrame(data)


def load_war_prediction_model() -> pd.DataFrame:
    """
    ML model predicting Cubs core player WAR.

    Uses walk-forward validation: trains on 2012-2016 data,
    predicts 2017-2019 (held out as "future").

    Features: age, prior_year_war, war_2_years_ago, peak_war, years_since_peak
    Target: next_year_war

    Returns predictions vs actuals for visualization.
    """
    # Cubs core players with full career WAR data
    players = {
        "Kris Bryant": {
            "birth_year": 1992,
            "position": "3B",
            "war": {2015: 6.5, 2016: 7.7, 2017: 6.6, 2018: 3.2, 2019: 4.8}
        },
        "Anthony Rizzo": {
            "birth_year": 1989,
            "position": "1B",
            "war": {2012: 0.8, 2013: 2.2, 2014: 4.0, 2015: 4.2, 2016: 4.7,
                    2017: 4.4, 2018: 2.7, 2019: 2.8}
        },
        "Javier Baez": {
            "birth_year": 1992,
            "position": "SS",
            "war": {2014: -0.3, 2015: 0.0, 2016: 2.3, 2017: 3.0, 2018: 4.1, 2019: 5.3}
        },
        "Kyle Schwarber": {
            "birth_year": 1993,
            "position": "OF",
            "war": {2015: 0.5, 2016: 0.5, 2017: 1.6, 2018: 1.9, 2019: 1.9}
        },
        "Addison Russell": {
            "birth_year": 1994,
            "position": "SS",
            "war": {2015: 2.6, 2016: 2.6, 2017: 1.9, 2018: -0.6, 2019: -0.3}
        },
        "Kyle Hendricks": {
            "birth_year": 1989,
            "position": "SP",
            "war": {2014: 2.3, 2015: 2.7, 2016: 4.6, 2017: 3.5, 2018: 2.2, 2019: 3.0}
        },
        "Jon Lester": {
            "birth_year": 1984,
            "position": "SP",
            "war": {2015: 2.3, 2016: 2.5, 2017: 2.1, 2018: 2.0, 2019: 1.9}
        },
    }

    # Build training data: each row is a player-year with features
    rows = []
    for player, data in players.items():
        birth = data["birth_year"]
        position = data["position"]
        wars = data["war"]
        years = sorted(wars.keys())

        peak_war = 0
        peak_year = years[0]

        for i, year in enumerate(years[:-1]):
            age = year - birth
            current_war = wars[year]
            next_war = wars[years[i + 1]]

            if current_war > peak_war:
                peak_war = current_war
                peak_year = year

            prior_war = wars.get(year - 1, current_war)
            war_2_ago = wars.get(year - 2, prior_war)

            rows.append({
                "player": player,
                "year": year,
                "age": age,
                "position": position,
                "current_war": current_war,
                "prior_war": prior_war,
                "war_2_ago": war_2_ago,
                "peak_war": peak_war,
                "years_since_peak": year - peak_year,
                "next_year_war": next_war,
                "is_pitcher": 1 if position == "SP" else 0
            })

    df = pd.DataFrame(rows)

    # Walk-forward: train on 2012-2016, predict 2017-2018
    train = df[df["year"] <= 2016].copy()
    test = df[df["year"].isin([2017, 2018])].copy()

    features = ["age", "current_war", "prior_war", "war_2_ago",
                "peak_war", "years_since_peak", "is_pitcher"]

    X_train = train[features]
    y_train = train["next_year_war"]
    X_test = test[features]

    # Train gradient boosting model
    model = GradientBoostingRegressor(
        n_estimators=100, max_depth=3, learning_rate=0.1, random_state=42
    )
    model.fit(X_train, y_train)

    # Predict
    test = test.copy()
    test["predicted_war"] = model.predict(X_test)
    test["actual_war"] = test["next_year_war"]
    test["prediction_year"] = test["year"] + 1

    # Calculate prediction error and aggregate by player
    test["error"] = test["predicted_war"] - test["actual_war"]

    # Aggregate: average prediction error per player across years
    result = test.groupby("player").agg({
        "predicted_war": "mean",
        "actual_war": "mean",
        "error": "mean"
    }).reset_index()

    result = result.sort_values("error")
    return result
