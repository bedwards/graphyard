"""
2016 Chicago Cubs data loaders.

Data sources:
- Baseball-Reference.com WAR data
- FanGraphs player valuations
- MLB transaction history
- Cubs draft history
"""

import pandas as pd


def load_cubs_rebuild_arc() -> pd.DataFrame:
    """
    Cubs win totals and playoff results 2011-2021.
    Shows the complete rebuild arc under Theo Epstein.

    Source: Baseball-Reference.com
    """
    data = {
        "year": [2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021],
        "wins": [71, 61, 66, 73, 97, 103, 92, 95, 84, 34, 71],
        "losses": [91, 101, 96, 89, 65, 58, 69, 68, 78, 26, 91],
        "win_pct": [.438, .377, .407, .451, .599, .640, .571, .583, .519, .567, .438],
        "playoff_result": [
            "Missed", "Missed", "Missed", "Missed", "NLCS",
            "World Series Champion", "NLCS", "Wild Card Loss",
            "Missed", "Wild Card Loss", "Missed"
        ],
        "division_rank": [5, 5, 5, 5, 3, 1, 1, 1, 3, 1, 4],
        "run_differential": [-61, -152, -118, -36, 143, 252, 111, 108, -2, 39, -95],
        "era": ["Pre-Epstein", "Rebuild", "Rebuild", "Rebuild", "Contention",
                "Championship", "Window", "Window", "Decline", "COVID", "Rebuild 2.0"],
        "notes": [
            "Last year before Epstein",
            "First Epstein year, tank begins",
            "Bryant drafted #2 overall",
            "Schwarber drafted #4, Russell acquired",
            "97 wins, NLCS loss to Mets",
            "108-year drought ends",
            "Lost NLCS to Dodgers 4-1",
            "Lost Wild Card to Rockies",
            "Core begins to age out",
            "60-game COVID season",
            "Fire sale at deadline"
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
    Compare Cubs' championship window to other recent dynasties.

    Source: Baseball-Reference.com
    """
    data = {
        "team": [
            "2016 Cubs", "2010s Giants", "2015-2019 Astros",
            "2017-2020 Dodgers", "2007-2013 Cardinals", "2004-2018 Red Sox"
        ],
        "window_years": ["2015-2018", "2010-2014", "2015-2019", "2017-2020", "2007-2013", "2004-2018"],
        "world_series_appearances": [1, 3, 2, 3, 3, 4],
        "world_series_wins": [1, 3, 1, 1, 2, 4],
        "playoff_appearances": [4, 5, 5, 4, 5, 7],
        "win_total_in_window": [371, 436, 468, 387, 593, 1240],
        "avg_wins_per_full_season": [93, 87, 94, 102, 85, 89],
        "core_player_wars": [
            "Bryant 27, Rizzo 18, Baez 15",
            "Posey 34, Bumgarner 24, Crawford 18",
            "Altuve 32, Bregman 28, Correa 24",
            "Betts 34, Bellinger 19, Kershaw 18",
            "Molina 27, Wainwright 22, Carpenter 21",
            "Pedroia 38, Ortiz 28, multiple"
        ],
        "cheating_factor": [
            "None proven",
            "None proven",
            "Sign-stealing 2017-2018",
            "None proven",
            "Hacked Astros (not competitive advantage)",
            "Apple Watch 2017"
        ]
    }
    return pd.DataFrame(data)


def load_what_went_wrong() -> pd.DataFrame:
    """
    Player performance decline after 2016.
    Shows WAR trajectory of core players.

    Source: Baseball-Reference.com
    """
    data = {
        "player": [
            "Kris Bryant", "Anthony Rizzo", "Addison Russell",
            "Kyle Schwarber", "Javier Baez", "Jason Heyward",
            "Jon Lester", "Jake Arrieta"
        ],
        "war_2016": [7.7, 4.7, 2.6, 0.5, 2.3, 1.6, 2.5, 4.0],
        "war_2017": [6.6, 4.4, 1.9, 1.6, 3.0, 0.3, 2.1, 2.6],
        "war_2018": [3.2, 2.7, -0.6, 1.9, 4.1, 1.2, 2.0, 1.8],
        "war_2019": [4.8, 2.8, -0.3, 1.9, 5.3, 0.5, 1.9, 0.2],
        "war_2020": [0.9, 0.7, None, -0.2, -0.3, 0.3, 0.5, None],
        "total_decline_pct": [-88, -85, -100, -60, -87, -81, -80, -100],
        "primary_cause": [
            "Injuries, shoulder issues",
            "Natural aging (30+)",
            "Domestic violence, released",
            "Strikeouts, defense issues",
            "Contact issues, aging",
            "Never lived up to contract",
            "Age decline (36+)",
            "Left in FA, age decline"
        ],
        "left_cubs": [
            "2021 (traded)", "2021 (traded)", "2019 (released)",
            "2020 (non-tendered)", "2021 (traded)", "2023 (released)",
            "2020 (walked)", "2017 (FA)"
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
        "season": [
            "2010 (BAL)", "2011 (BAL)", "2012 (BAL)", "2013 (BAL)",
            "2013 (CHC)", "2014 (CHC)", "2015 (CHC)", "2016 (CHC)",
            "2017 (CHC)", "2018 (PHI)", "2019 (PHI)", "2020 (PHI)"
        ],
        "team": [
            "Orioles", "Orioles", "Orioles", "Orioles",
            "Cubs", "Cubs", "Cubs", "Cubs",
            "Cubs", "Phillies", "Phillies", "Phillies"
        ],
        "era": [4.66, 5.05, 6.20, 5.22, 3.66, 2.53, 1.77, 3.10, 3.53, 3.96, 4.64, 5.08],
        "fip": [4.95, 4.59, 4.97, 4.35, 3.56, 2.98, 2.35, 3.33, 3.45, 3.98, 4.32, 4.57],
        "whip": [1.47, 1.41, 1.55, 1.38, 1.16, 1.02, 0.86, 1.08, 1.22, 1.28, 1.38, 1.40],
        "war": [-0.6, 0.9, -0.1, 0.4, 1.7, 4.4, 7.3, 4.0, 2.6, 1.8, 0.2, 0.5],
        "cubs_adjustments": [
            None, None, None, None,
            "Cut sinker, added cutter",
            "Improved sequencing",
            "Cy Young winner",
            "Maintained excellence",
            "Decline begins",
            None, None, None
        ]
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
