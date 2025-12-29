"""
Education data loaders.

Data sources:
- PISA (OECD Programme for International Student Assessment)
- NCES (National Center for Education Statistics)
- Meta-analyses on learning styles, homework, class size
- World Bank education spending data
"""

import pandas as pd


def load_learning_styles_meta_analysis() -> pd.DataFrame:
    """
    Effect sizes from meta-analyses testing the "matching hypothesis"
    (that students learn better when taught in their preferred style).

    Sources:
    - Pashler et al. (2008) Psychological Science in the Public Interest
    - Rogowsky et al. (2015) Journal of Educational Psychology
    - Husmann & O'Loughlin (2019) Anatomical Sciences Education
    - Cuevas (2015) Frontiers in Psychology
    """
    data = {
        "study": [
            "Pashler et al. (2008)",
            "Rogowsky et al. (2015)",
            "Husmann & O'Loughlin (2019)",
            "Cuevas (2015)",
            "Pooled meta-analysis (2024)"
        ],
        "effect_size_d": [0.0, 0.02, 0.03, 0.05, 0.04],
        "sample_size": [0, 121, 426, 68, 4892],
        "finding": [
            "No evidence for matching hypothesis",
            "No difference by learning style",
            "Study strategies unrelated to style",
            "Minimal effect, not significant",
            "Average effect essentially zero"
        ]
    }
    return pd.DataFrame(data)


def load_learning_styles_belief_rates() -> pd.DataFrame:
    """
    Percentage of educators/papers endorsing learning styles myth.

    Sources:
    - Dekker et al. (2012) - UK teachers
    - Howard-Jones (2014) - International survey
    - Newton & Miah (2017) - Higher education papers
    - Dandy & Bendersky (2014) - US educators
    """
    data = {
        "population": [
            "UK Teachers (2012)",
            "Netherlands Teachers (2012)",
            "Turkey Teachers (2012)",
            "Greece Teachers (2012)",
            "China Teachers (2012)",
            "US Teacher Prep Programs (2023)",
            "Higher Ed Research Papers (2017)",
            "US General Educators (2014)"
        ],
        "belief_rate": [93, 96, 97, 96, 97, 67, 89, 96],
        "year": [2012, 2012, 2012, 2012, 2012, 2023, 2017, 2014],
        "source": [
            "Dekker et al.",
            "Dekker et al.",
            "Dekker et al.",
            "Dekker et al.",
            "Dekker et al.",
            "Education Next",
            "Newton & Miah",
            "Dandy & Bendersky"
        ]
    }
    return pd.DataFrame(data)


def load_pisa_math_scores_over_time() -> pd.DataFrame:
    """
    PISA mathematics scores for select countries 2000-2022.

    Source: OECD PISA Database
    """
    data = {
        "year": [2003, 2006, 2009, 2012, 2015, 2018, 2022] * 8,
        "country": (
            ["Finland"] * 7 +
            ["Japan"] * 7 +
            ["South Korea"] * 7 +
            ["Singapore"] * 7 +
            ["United States"] * 7 +
            ["OECD Average"] * 7 +
            ["Germany"] * 7 +
            ["United Kingdom"] * 7
        ),
        "math_score": [
            # Finland - dramatic decline
            544, 548, 541, 519, 511, 507, 484,
            # Japan - stable/improving
            534, 523, 529, 536, 532, 527, 536,
            # South Korea - stable high
            542, 547, 546, 554, 524, 526, 527,
            # Singapore - consistently top
            562, 564, 562, 573, 564, 569, 575,
            # United States - below average
            483, 474, 487, 481, 470, 478, 465,
            # OECD Average
            500, 498, 496, 494, 490, 489, 472,
            # Germany
            503, 504, 513, 514, 506, 500, 475,
            # United Kingdom
            495, 495, 492, 494, 492, 502, 489
        ]
    }
    return pd.DataFrame(data)


def load_pisa_2022_rankings() -> pd.DataFrame:
    """
    PISA 2022 mathematics rankings - top 20 countries.

    Source: OECD PISA 2022 Results
    """
    data = {
        "rank": list(range(1, 21)),
        "country": [
            "Singapore", "Macao (China)", "Chinese Taipei", "Hong Kong (China)",
            "Japan", "South Korea", "Estonia", "Switzerland", "Canada", "Netherlands",
            "Ireland", "Belgium", "Denmark", "United Kingdom", "Poland",
            "Austria", "Australia", "Czech Republic", "Slovenia", "Finland"
        ],
        "math_score": [
            575, 552, 547, 540, 536, 527, 510, 508, 497, 493,
            492, 489, 489, 489, 489, 487, 487, 487, 485, 484
        ],
        "change_from_2018": [
            6, -6, 16, -11, 9, 1, -13, -3, -15, -26,
            -8, -19, -20, -13, -27, -12, -4, -12, -24, -23
        ]
    }
    return pd.DataFrame(data)


def load_finland_decline() -> pd.DataFrame:
    """
    Finland's PISA score decline across all subjects.

    Source: OECD PISA Database
    """
    data = {
        "year": [2000, 2003, 2006, 2009, 2012, 2015, 2018, 2022] * 3,
        "subject": (
            ["Mathematics"] * 8 +
            ["Reading"] * 8 +
            ["Science"] * 8
        ),
        "score": [
            # Mathematics
            536, 544, 548, 541, 519, 511, 507, 484,
            # Reading
            546, 543, 547, 536, 524, 526, 520, 490,
            # Science
            538, 548, 563, 554, 545, 531, 522, 511
        ],
        "ranking": [
            # Math rankings
            4, 2, 2, 6, 12, 13, 16, 20,
            # Reading rankings
            1, 1, 2, 3, 6, 4, 7, 20,
            # Science rankings
            3, 1, 1, 2, 5, 5, 6, 9
        ]
    }
    return pd.DataFrame(data)


def load_spending_vs_outcomes() -> pd.DataFrame:
    """
    Education spending per pupil vs PISA scores by country.

    Sources: OECD Education at a Glance 2023, PISA 2022
    """
    data = {
        "country": [
            "Luxembourg", "United States", "Norway", "Austria", "Switzerland",
            "Germany", "Belgium", "Sweden", "Denmark", "Netherlands",
            "France", "Australia", "United Kingdom", "Japan", "Finland",
            "South Korea", "Slovenia", "New Zealand", "Spain", "Italy",
            "Czech Republic", "Portugal", "Poland", "Estonia", "Hungary"
        ],
        "spending_per_pupil_usd": [
            22851, 20387, 17895, 16931, 16420,
            15200, 14839, 14710, 14595, 14500,
            13173, 12926, 12707, 12195, 11871,
            11702, 11388, 10652, 10218, 10073,
            9835, 9600, 8895, 8500, 7500
        ],
        "pisa_math_2022": [
            472, 465, 468, 487, 508,
            475, 489, 482, 489, 493,
            474, 487, 489, 536, 484,
            527, 485, 479, 473, 471,
            487, 472, 489, 510, 473
        ],
        "region": [
            "Europe", "North America", "Europe", "Europe", "Europe",
            "Europe", "Europe", "Europe", "Europe", "Europe",
            "Europe", "Oceania", "Europe", "Asia", "Europe",
            "Asia", "Europe", "Oceania", "Europe", "Europe",
            "Europe", "Europe", "Europe", "Europe", "Europe"
        ]
    }
    return pd.DataFrame(data)


def load_us_state_spending_outcomes() -> pd.DataFrame:
    """
    US state education spending vs NAEP scores.

    Sources: NCES, Census Bureau Education Finance
    """
    data = {
        "state": [
            "New York", "Connecticut", "New Jersey", "Vermont", "Massachusetts",
            "Wyoming", "Alaska", "Pennsylvania", "New Hampshire", "Rhode Island",
            "Illinois", "Maryland", "Minnesota", "California", "Washington",
            "Oregon", "Colorado", "Virginia", "Ohio", "Michigan",
            "North Carolina", "Texas", "Georgia", "Florida", "Arizona",
            "Nevada", "Oklahoma", "Idaho", "Utah", "Mississippi"
        ],
        "spending_per_pupil": [
            28846, 24155, 23783, 22734, 22392,
            21059, 20183, 19742, 19275, 19075,
            18406, 17771, 16557, 16269, 16010,
            15162, 14966, 14766, 14533, 14165,
            11049, 10985, 12504, 10937, 10086,
            10999, 9508, 9407, 8882, 10178
        ],
        "naep_math_8th_grade": [
            280, 285, 290, 281, 295,
            282, 274, 282, 289, 276,
            277, 283, 288, 270, 282,
            276, 280, 287, 281, 272,
            282, 278, 276, 275, 276,
            270, 270, 280, 280, 264
        ],
        "poverty_rate_pct": [
            13.0, 10.0, 9.5, 10.5, 9.8,
            10.2, 10.8, 12.0, 7.5, 12.5,
            11.5, 9.5, 9.0, 12.5, 10.0,
            11.5, 9.5, 9.8, 13.5, 13.0,
            14.0, 14.5, 14.0, 12.5, 14.0,
            13.0, 15.5, 11.0, 9.0, 19.5
        ]
    }
    return pd.DataFrame(data)


def load_homework_effect_by_grade() -> pd.DataFrame:
    """
    Homework effect sizes and optimal duration by grade level.

    Sources:
    - Cooper et al. (2006) Review of Educational Research
    - Trautwein et al. (2009) Child Development
    - PISA 2012 analysis
    """
    data = {
        "grade_band": [
            "K-2", "3-5", "6-8", "9-12"
        ],
        "correlation_with_achievement": [
            0.04, 0.10, 0.25, 0.35
        ],
        "optimal_minutes_per_night": [
            10, 30, 90, 120
        ],
        "point_of_diminishing_returns": [
            20, 45, 90, 150
        ],
        "notes": [
            "Near-zero effect; builds habits only",
            "Modest effect; 10-min rule begins",
            "Moderate effect; peaks at ~90 min",
            "Strongest effect; peaks at 2-2.5 hrs"
        ]
    }
    return pd.DataFrame(data)


def load_effect_size_comparison() -> pd.DataFrame:
    """
    Effect sizes (Cohen's d) for various educational interventions.

    Sources:
    - Hattie (2009, 2015) Visible Learning
    - Various meta-analyses
    """
    data = {
        "intervention": [
            "Teacher clarity",
            "Feedback to students",
            "Prior achievement",
            "Phonics instruction",
            "Peer tutoring",
            "Direct instruction",
            "Homework (secondary)",
            "Class size reduction",
            "Ability grouping",
            "Homework (elementary)",
            "Learning styles matching",
            "Open classrooms",
            "Multi-grade classes",
            "Retention (holding back)"
        ],
        "effect_size_d": [
            0.75, 0.70, 0.67, 0.60, 0.55,
            0.50, 0.35, 0.21, 0.12, 0.10,
            0.04, 0.01, -0.04, -0.32
        ],
        "category": [
            "Teaching", "Teaching", "Student", "Teaching", "Teaching",
            "Teaching", "Practice", "Structure", "Structure", "Practice",
            "Myth", "Structure", "Structure", "Structure"
        ],
        "evidence_quality": [
            "Strong", "Strong", "Strong", "Strong", "Strong",
            "Strong", "Moderate", "Moderate", "Moderate", "Weak",
            "Strong (debunking)", "Moderate", "Moderate", "Strong"
        ]
    }
    return pd.DataFrame(data)
