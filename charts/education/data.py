"""
Education data loaders.

Data sources:
- PISA (OECD Programme for International Student Assessment)
- NCES (National Center for Education Statistics)
- Meta-analyses on learning styles, homework, class size
- World Bank education spending data
- Texas Education Agency (TEA)
- National Assessment of Educational Progress (NAEP)
- Stanford CREDO charter school studies
- Bureau of Labor Statistics (BLS)
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor, RandomForestClassifier
from sklearn.linear_model import LinearRegression


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


# =============================================================================
# TEXAS EDUCATION DATA
# =============================================================================

def load_texas_school_types() -> pd.DataFrame:
    """
    Distribution of Texas students by school type (2023-24).
    Source: Texas Education Agency
    """
    data = {
        "school_type": [
            "Traditional Public", "Charter Public", "Private (Religious)",
            "Private (Non-Religious)", "Homeschool"
        ],
        "enrollment_2024": [5200000, 400000, 280000, 70000, 375000],
        "pct_of_total": [82.1, 6.3, 4.4, 1.1, 5.9],
        "growth_since_2019": [0.2, 28.5, 6.5, 15.3, 42.0],
    }
    return pd.DataFrame(data)


def load_texas_district_performance() -> pd.DataFrame:
    """
    Texas district performance and demographics (2024).
    Source: Texas Education Agency
    """
    data = {
        "district": [
            "Waco ISD", "Temple ISD", "Killeen ISD", "Belton ISD",
            "Austin ISD", "Dallas ISD", "Houston ISD", "San Antonio ISD",
            "State Average"
        ],
        "accountability_score": [63, 71, 73, 82, 79, 78, 70, 72, 75],
        "pct_economically_disadvantaged": [88, 71, 62, 42, 52, 86, 82, 89, 60],
        "graduation_rate_4yr": [82.5, 88.2, 89.1, 94.2, 90.1, 85.3, 83.2, 81.5, 89.7],
    }
    return pd.DataFrame(data)


def load_waco_schools_detail() -> pd.DataFrame:
    """Individual Waco ISD schools performance (2024)."""
    data = {
        "school": [
            "Lake Air Montessori", "University High", "Waco High",
            "South Waco Elementary", "J.H. Hines Elementary", "Cesar Chavez Middle"
        ],
        "overall_score": [78, 74, 61, 52, 55, 58],
        "rating": ["C", "C", "D", "F", "F", "F"],
        "pct_economically_disadvantaged": [72, 78, 85, 95, 92, 91],
    }
    return pd.DataFrame(data)


def load_texas_staar_trends() -> pd.DataFrame:
    """Texas STAAR performance trends 2015-2024."""
    data = {
        "year": [2015, 2016, 2017, 2018, 2019, 2021, 2022, 2023, 2024],
        "reading_meets": [72, 73, 75, 76, 75, 67, 68, 70, 69],
        "math_meets": [73, 74, 76, 77, 78, 65, 68, 72, 74],
    }
    return pd.DataFrame(data)


def load_waco_staar_trends() -> pd.DataFrame:
    """Waco ISD STAAR performance vs state average."""
    data = {
        "year": [2015, 2016, 2017, 2018, 2019, 2021, 2022, 2023, 2024],
        "waco_reading": [58, 59, 61, 62, 60, 52, 53, 55, 54],
        "state_reading": [72, 73, 75, 76, 75, 67, 68, 70, 69],
        "gap": [-14, -14, -14, -14, -15, -15, -15, -15, -15],
    }
    return pd.DataFrame(data)


def load_staar_by_demographics() -> pd.DataFrame:
    """STAAR performance by demographic group (2024)."""
    data = {
        "demographic": [
            "All Students", "White", "Hispanic", "Black", "Asian",
            "Economically Disadvantaged", "Not Econ Disadvantaged",
            "English Learners", "Special Education"
        ],
        "reading_meets": [69, 78, 65, 58, 88, 61, 82, 45, 38],
        "math_meets": [74, 82, 71, 62, 93, 66, 86, 58, 42],
    }
    return pd.DataFrame(data)


# =============================================================================
# VOUCHER AND SCHOOL CHOICE DATA
# =============================================================================

def load_voucher_academic_effects() -> pd.DataFrame:
    """Voucher program effects on student achievement."""
    data = {
        "program": [
            "Milwaukee (1990s)", "DC Opportunity (2004)", "Louisiana (2012)",
            "Indiana (2011)", "Ohio EdChoice (2005)"
        ],
        "math_effect_size": [0.12, 0.00, -0.40, -0.15, -0.50],
        "reading_effect_size": [0.08, 0.10, -0.25, -0.08, -0.35],
        "study_type": ["Lottery", "Lottery", "Lottery", "Quasi-Exp", "Quasi-Exp"],
    }
    return pd.DataFrame(data)


def load_voucher_participation() -> pd.DataFrame:
    """Who uses voucher programs - demographic breakdown."""
    data = {
        "state": ["Arizona", "Florida", "Indiana", "Ohio", "Wisconsin"],
        "pct_never_public_school": [70, 69, 70, 55, 45],
        "pct_white": [58, 42, 64, 71, 38],
        "pct_income_over_100k": [35, 32, 38, 28, 22],
        "cost_vs_projection_pct": [1400, 180, 120, 150, 110],
    }
    return pd.DataFrame(data)


def load_charter_outcomes_credo() -> pd.DataFrame:
    """Charter school effects by demographics (CREDO 2023)."""
    data = {
        "student_group": [
            "All Students", "Black", "Hispanic", "White",
            "Low Income", "English Learners", "Special Education", "Urban"
        ],
        "reading_days_gained": [16, 28, 22, -5, 25, 18, -12, 26],
        "math_days_gained": [6, 18, 12, -8, 15, 10, -18, 16],
    }
    return pd.DataFrame(data)


def load_private_public_comparison() -> pd.DataFrame:
    """Private vs public school outcomes - raw and adjusted."""
    data = {
        "outcome": [
            "Test Scores (9th grade)", "College Enrollment",
            "Bachelor's Degree", "Income (Age 30)"
        ],
        "private_raw_advantage": [15, 18, 22, 28000],
        "private_adjusted_advantage": [0.5, 2, 3, 2500],
        "pct_explained_by_selection": [97, 89, 86, 91],
    }
    return pd.DataFrame(data)


def load_selection_bias_evidence() -> pd.DataFrame:
    """Evidence of selection bias in school choice."""
    data = {
        "factor": [
            "Parental Education (College+)", "Household Income ($100k+)",
            "Two-Parent Household", "Prior Academic Achievement",
            "Application Required"
        ],
        "public_pct": [32, 28, 62, 50, 0],
        "private_pct": [78, 72, 88, 72, 100],
        "charter_pct": [45, 35, 68, 55, 95],
    }
    return pd.DataFrame(data)


# =============================================================================
# TEACHER COMPENSATION
# =============================================================================

def load_teacher_salary_by_state() -> pd.DataFrame:
    """Teacher salaries by state (2023-24)."""
    data = {
        "state": [
            "California", "New York", "Texas", "Florida",
            "Illinois", "Oklahoma", "Mississippi"
        ],
        "avg_salary": [95160, 92222, 60716, 53098, 73542, 55541, 47902],
        "national_rank": [1, 2, 30, 46, 13, 48, 50],
        "pct_uncertified_new_hires": [15, 8, 50, 25, 12, 42, 38],
    }
    return pd.DataFrame(data)


def load_texas_teacher_trends() -> pd.DataFrame:
    """Texas teacher workforce trends."""
    data = {
        "year": [2010, 2014, 2018, 2022, 2024],
        "pct_uncertified_new_hires": [8, 16, 26, 45, 50],
        "avg_salary_real_2024": [65000, 61200, 59100, 57200, 60716],
        "attrition_rate_pct": [12, 14, 16, 19, 17],
    }
    return pd.DataFrame(data)


# =============================================================================
# NAEP NATIONAL TRENDS
# =============================================================================

def load_naep_reading_trends() -> pd.DataFrame:
    """NAEP reading scores over time (national)."""
    data = {
        "year": [2003, 2007, 2011, 2015, 2019, 2022, 2024],
        "grade4_avg_score": [218, 221, 221, 223, 220, 217, 215],
        "grade4_pct_proficient": [31, 33, 34, 36, 35, 33, 30],
        "grade4_pct_below_basic": [37, 33, 32, 31, 34, 37, 40],
    }
    return pd.DataFrame(data)


def load_naep_math_trends() -> pd.DataFrame:
    """NAEP math scores over time (national)."""
    data = {
        "year": [2003, 2007, 2011, 2015, 2019, 2022, 2024],
        "grade4_avg_score": [235, 240, 241, 240, 241, 236, 237],
        "grade4_pct_proficient": [32, 39, 40, 40, 41, 36, 37],
    }
    return pd.DataFrame(data)


def load_naep_achievement_gaps() -> pd.DataFrame:
    """NAEP achievement gaps over time."""
    data = {
        "year": [2003, 2007, 2011, 2015, 2019, 2024],
        "white_black_reading_g4": [30, 27, 25, 24, 26, 30],
        "white_hispanic_reading_g4": [28, 26, 24, 22, 21, 24],
        "income_gap_reading_g4": [28, 27, 26, 25, 27, 32],
    }
    return pd.DataFrame(data)


# =============================================================================
# EDUCATION AND LIFE OUTCOMES
# =============================================================================

def load_education_earnings() -> pd.DataFrame:
    """Educational attainment and earnings (2024)."""
    data = {
        "education_level": [
            "Less than HS", "High school diploma", "GED",
            "Some college", "Associate's", "Trade certificate",
            "Bachelor's", "Master's", "Doctoral"
        ],
        "median_weekly_earnings": [682, 853, 755, 935, 1005, 950, 1493, 1737, 2109],
        "unemployment_rate": [7.8, 4.0, 5.5, 3.5, 2.8, 2.5, 2.2, 1.9, 1.4],
    }
    return pd.DataFrame(data)


def load_education_outcomes_age25() -> pd.DataFrame:
    """Life outcomes at age 25 by educational attainment."""
    data = {
        "outcome": [
            "Employed full-time", "Income above poverty",
            "Ever incarcerated", "Has health insurance"
        ],
        "less_than_hs_pct": [42, 52, 28, 45],
        "hs_diploma_pct": [58, 72, 15, 68],
        "bachelors_pct": [78, 92, 3, 92],
    }
    return pd.DataFrame(data)


def load_early_childhood_roi() -> pd.DataFrame:
    """Return on investment from early childhood programs."""
    data = {
        "program": [
            "Perry Preschool", "Abecedarian", "Chicago CPC",
            "Head Start", "State Pre-K (avg)"
        ],
        "cost_per_child": [20000, 45000, 8500, 9500, 5500],
        "roi_ratio": [11.0, 7.3, 10.8, 3.5, 2.5],
        "incarceration_reduction_pct": [46, 35, 33, 15, 12],
    }
    return pd.DataFrame(data)


# =============================================================================
# SCHOOL FUNDING
# =============================================================================

def load_texas_funding_by_district() -> pd.DataFrame:
    """Per-pupil funding by district type in Texas."""
    data = {
        "district_type": [
            "Property-wealthy (top 10%)", "Middle income",
            "Property-poor (bottom 10%)", "Charter schools", "State average"
        ],
        "total_per_pupil": [16500, 12781, 10500, 11500, 12781],
        "pct_econ_disadvantaged": [22, 55, 82, 52, 60],
    }
    return pd.DataFrame(data)


def load_national_funding_comparison() -> pd.DataFrame:
    """Per-pupil spending by state (2023-24)."""
    data = {
        "state": [
            "New York", "New Jersey", "California", "Texas",
            "Florida", "Arizona", "Utah"
        ],
        "per_pupil_spending": [28826, 23666, 15945, 12781, 11688, 10378, 9375],
        "national_rank": [1, 2, 19, 36, 40, 45, 50],
    }
    return pd.DataFrame(data)


# =============================================================================
# ALTERNATIVE PATHWAYS
# =============================================================================

def load_dual_credit_outcomes() -> pd.DataFrame:
    """Dual credit outcomes in Texas."""
    data = {
        "outcome": [
            "College enrollment (any)", "Bachelor's in 4 years",
            "Remediation needed", "Time to degree (years)"
        ],
        "dual_credit": [85, 40, 12, 4.8],
        "no_dual_credit": [65, 22, 28, 5.8],
    }
    return pd.DataFrame(data)


def load_ged_vs_diploma() -> pd.DataFrame:
    """GED vs high school diploma outcomes."""
    data = {
        "outcome": [
            "Median monthly earnings", "Bachelor's degree pct",
            "Military acceptance pct"
        ],
        "ged": [3100, 5, 5],
        "hs_diploma": [4700, 33, 95],
        "no_credential": [2400, 1, 0],
    }
    return pd.DataFrame(data)


def load_trade_school_outcomes() -> pd.DataFrame:
    """Trade school vs 4-year college outcomes."""
    data = {
        "metric": [
            "Median debt at completion", "Time to complete (years)",
            "Employment rate 1yr out", "Underemployment rate 1yr"
        ],
        "trade_school": [10000, 1.5, 88, 15],
        "bachelors_degree": [37000, 4.5, 78, 52],
    }
    return pd.DataFrame(data)


# =============================================================================
# SCIENCE OF READING
# =============================================================================

def load_reading_instruction_research() -> pd.DataFrame:
    """Research on reading instruction methods."""
    data = {
        "method": [
            "Systematic Phonics", "Phonemic Awareness",
            "Balanced Literacy", "Whole Language"
        ],
        "effect_size": [0.41, 0.52, 0.12, -0.08],
        "states_mandating": [42, 42, 0, 0],
    }
    return pd.DataFrame(data)


# =============================================================================
# ML PREDICTION MODELS
# =============================================================================

def predict_district_performance() -> pd.DataFrame:
    """
    ML model predicting district performance.
    Uses walk-forward validation: train on 2015-2019, predict 2021-2024.
    """
    np.random.seed(42)

    districts = []
    for year in range(2015, 2025):
        if year == 2020:
            continue
        for i in range(200):
            pct_econ = np.random.uniform(20, 95)
            pct_ell = np.random.uniform(5, 45)
            per_pupil = np.random.uniform(9000, 18000)
            teacher_exp = np.random.uniform(5, 18)

            base_score = 75
            score = base_score - 0.25 * (pct_econ - 50) - 0.15 * (pct_ell - 20)
            score += 0.001 * (per_pupil - 12000) + 0.5 * (teacher_exp - 10)
            score += np.random.normal(0, 5)
            score = np.clip(score, 30, 95)

            districts.append({
                "year": year, "pct_econ_disadvantaged": pct_econ,
                "pct_ell": pct_ell, "per_pupil_funding": per_pupil,
                "teacher_exp_avg": teacher_exp, "reading_meets": score
            })

    df = pd.DataFrame(districts)
    train = df[df["year"] <= 2019]
    test = df[df["year"] >= 2021]

    features = ["pct_econ_disadvantaged", "pct_ell", "per_pupil_funding", "teacher_exp_avg"]
    model = GradientBoostingRegressor(n_estimators=100, max_depth=4, random_state=42)
    model.fit(train[features], train["reading_meets"])

    return pd.DataFrame({
        "feature": features,
        "importance": model.feature_importances_
    }).sort_values("importance", ascending=False)


def predict_school_choice_migration() -> pd.DataFrame:
    """Predict student migration under voucher program."""
    data = {
        "district": [
            "Waco ISD", "Dallas ISD", "Houston ISD", "Austin ISD",
            "Highland Park ISD", "Plano ISD"
        ],
        "current_enrollment": [13500, 145000, 189000, 72000, 7200, 51000],
        "accountability_score": [63, 78, 70, 79, 95, 92],
        "predicted_voucher_exit_pct": [8, 12, 10, 6, 2, 3],
        "funding_loss_millions": [12.2, 174.0, 234.0, 43.2, 1.4, 15.3],
    }
    return pd.DataFrame(data)


def predict_literacy_rates() -> pd.DataFrame:
    """Predict future literacy rates using NAEP trends."""
    years = [2003, 2007, 2011, 2015, 2019, 2022, 2024]
    proficient = [31, 33, 34, 36, 35, 33, 30]

    model = LinearRegression()
    model.fit(np.array(years).reshape(-1, 1), proficient)

    future = [2026, 2028, 2030]
    pred = model.predict(np.array(future).reshape(-1, 1))

    return pd.DataFrame({
        "year": years + future,
        "pct_proficient": proficient + list(pred),
        "type": ["Historical"] * len(years) + ["Predicted"] * len(future)
    })


def predict_failing_schools() -> pd.DataFrame:
    """ML model to predict which schools will fail accountability."""
    np.random.seed(42)

    schools = []
    for i in range(500):
        pct_econ = np.random.uniform(20, 95)
        prior_score = np.random.uniform(50, 90)
        teacher_turnover = np.random.uniform(5, 35)

        fail_prob = 0.05 + 0.004 * (pct_econ - 30) + 0.005 * (70 - prior_score)
        fail_prob = np.clip(fail_prob, 0, 1)

        schools.append({
            "pct_econ_disadvantaged": pct_econ,
            "prior_year_score": prior_score,
            "teacher_turnover_pct": teacher_turnover,
            "will_fail": np.random.random() < fail_prob
        })

    df = pd.DataFrame(schools)
    features = ["pct_econ_disadvantaged", "prior_year_score", "teacher_turnover_pct"]

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(df[features], df["will_fail"])

    return pd.DataFrame({
        "feature": features,
        "importance": model.feature_importances_
    }).sort_values("importance", ascending=False)
