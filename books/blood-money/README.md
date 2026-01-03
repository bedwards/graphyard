# Blood Money: What the Median Citizen Pays for State Violence

**A Data-Driven Investigation into the Economics of Atrocity**

---

## Project Overview

This book investigates a question rarely asked with rigor: **How much does the average citizen pay—through taxes—for state violence, and what portion of that finances atrocities against civilians?**

The book takes three complementary angles:

1. **Historical Survey (1800-present)**: Examining median-income citizens across societies throughout history—what they paid in taxes, how much went to military/security apparatus, and what atrocities their contributions financed. Which historical citizen-eras "bought" the most civilian deaths per tax dollar?

2. **American Lifetime (1975-2025)**: A personal investigation spanning the author's lifetime. Assuming median income throughout, which years were worst? What was happening? How has the American taxpayer's complicity in state violence evolved over 50 years?

3. **Comparative Economics of Violence**: Rich countries spend more per casualty; poor countries achieve similar death tolls with machetes and militia. How do we fairly compare the moral burden of a $1 million cruise missile strike versus a $50 machete massacre?

---

## Core Questions

### Question 1: Historical Taxpayer Complicity
- What did a median-income citizen of Nazi Germany pay per Holocaust victim?
- What did a median Soviet citizen contribute to the Gulag system?
- What was the British citizen's cost per colonial death in India, Kenya, or Ireland?
- How does American spending on Vietnam, Iraq, and drone warfare compare?

### Question 2: The American Experience (1975-2025)
- In which year did the median American taxpayer's military contribution fund the most civilian deaths?
- How do we account for covert operations (CIA, NSF) versus declared military spending?
- What is the trajectory: are we funding more or fewer atrocities over time?
- How do indirect deaths (sanctions, refugee denial, collateral damage) factor in?

### Question 3: Rich vs. Poor Violence Economics
- Rwanda's genocide cost ~$112M in arms imports for 800,000+ deaths (~$140/death)
- US precision strikes cost millions per target—what is the cost per civilian death?
- Is there a moral difference between high-tech killing and low-tech killing?
- How should we weight intentionality, scale, and state capacity?

---

## Philosophical Framework

The book presents multiple ethical perspectives without forcing a conclusion:

### Just War Theory
- Distinguishes combatant deaths from civilian deaths
- Allows military-on-military violence under certain conditions
- Condemns targeting of civilians regardless of context
- Requires proportionality and discrimination in warfare

### Absolute Pacifism
- All violence is wrong; all tax contributions to violence are morally implicated
- Military-on-military killing is still killing
- The state has no special license to kill

### Contingent Pacifism
- War is almost never justified; perhaps no modern war qualifies
- Focuses on realistic assessment of actual wars rather than hypotheticals
- Accepts self-defense in theory while rejecting most practical applications

### The Book's Approach
We present data from all perspectives:
- Tables including only civilian deaths (just war compatible)
- Tables including all deaths (pacifist perspective)
- Analysis of declared vs. undeclared conflicts
- Treatment of direct vs. indirect deaths
- Military vs. covert operations spending

The reader can apply their own ethical framework to the data.

---

## Data Sources

### Existing in Graphyard Database

| Source | Schema | Coverage | Key Tables |
|--------|--------|----------|------------|
| UCDP (Uppsala Conflict Data) | `ucdp` | 1946-2024 | `ged_events` (50M+ conflict events), `one_sided_violence`, `battle_deaths` |
| Correlates of War | `cow` | 1816-2016 | `wars`, `war_participants`, `national_capabilities` (CINC, milex) |
| Political Terror Scale | `pts` | 1976-2024 | `country_year_scores` (state repression 1-5 scale) |
| Iraq Body Count | `ibc` | 2003-2017 | `incidents` (51K incidents), `individuals` |
| World Development Indicators | `public` | 1960-2023 | Economic indicators (GDP, tax revenue, gov spending) |
| Master Countries | `master` | — | Cross-dataset country resolution |

### New Datasets Required

| Dataset | Source | Coverage | Purpose |
|---------|--------|----------|---------|
| **SIPRI Military Expenditure** | sipri.org | 1949-2024 | Military spending by country-year |
| **US Intelligence Budget** | irp.fas.org, Congress | 1997-2024 | CIA/NSA/covert spending |
| **Maddison Project GDP** | rug.nl/ggdc | 1800-2023 | Historical GDP/income |
| **Historical Tax Rates** | OECD, academic | 1900-2024 | Tax burden by country-year |
| **US Median Income** | Census/FRED | 1975-2024 | Real median household income |
| **Rummel Democide** | hawaii.edu/powerkills | 1900-1999 | Government mass murder (262M deaths) |
| **ACLED Conflict Data** | acleddata.com | 1997-2024 | State violence against civilians |
| **Brown University Costs of War** | costsofwar.watson.brown.edu | 2001-2024 | Post-9/11 civilian deaths, indirect deaths |
| **Historical Military Spending** | EH.net, academic | 1800-1949 | Pre-SIPRI military expenditure |

---

## Database Schema Extensions

### New Schema: `atrocity_economics`

```sql
CREATE SCHEMA IF NOT EXISTS atrocity_economics;

-- Historical median income (purchasing power adjusted)
CREATE TABLE atrocity_economics.median_income_historical (
    id SERIAL PRIMARY KEY,
    country_id INTEGER REFERENCES master.countries(id),
    year SMALLINT NOT NULL,
    median_income_local DECIMAL(15,2),
    median_income_usd_ppp DECIMAL(15,2),  -- 2020 international dollars
    source VARCHAR(100),
    UNIQUE(country_id, year)
);

-- Military spending breakdown
CREATE TABLE atrocity_economics.military_spending (
    id SERIAL PRIMARY KEY,
    country_id INTEGER REFERENCES master.countries(id),
    year SMALLINT NOT NULL,
    total_milex_usd DECIMAL(15,2),        -- Current USD
    total_milex_constant DECIMAL(15,2),    -- Constant 2022 USD
    milex_pct_gdp DECIMAL(5,3),
    milex_per_capita DECIMAL(10,2),
    milex_pct_gov_spending DECIMAL(5,3),
    source VARCHAR(50),                    -- 'SIPRI', 'COW', 'historical'
    UNIQUE(country_id, year)
);

-- Covert/intelligence spending (where known)
CREATE TABLE atrocity_economics.intelligence_spending (
    id SERIAL PRIMARY KEY,
    country_id INTEGER REFERENCES master.countries(id),
    year SMALLINT NOT NULL,
    total_intel_usd DECIMAL(15,2),
    estimated BOOLEAN DEFAULT TRUE,
    source VARCHAR(200),
    notes TEXT
);

-- Tax rates and median taxpayer burden
CREATE TABLE atrocity_economics.tax_burden (
    id SERIAL PRIMARY KEY,
    country_id INTEGER REFERENCES master.countries(id),
    year SMALLINT NOT NULL,
    total_tax_pct_gdp DECIMAL(5,3),
    median_effective_rate DECIMAL(5,3),
    median_tax_paid_usd DECIMAL(10,2),
    source VARCHAR(100)
);

-- Atrocity episodes (unified across sources)
CREATE TABLE atrocity_economics.atrocity_episodes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(300) NOT NULL,
    perpetrator_country_id INTEGER REFERENCES master.countries(id),
    start_year SMALLINT,
    end_year SMALLINT,

    -- Death counts (best estimates)
    deaths_direct_low INTEGER,
    deaths_direct_mid INTEGER,
    deaths_direct_high INTEGER,
    deaths_indirect_low INTEGER,
    deaths_indirect_mid INTEGER,
    deaths_indirect_high INTEGER,

    -- Breakdown
    civilian_deaths INTEGER,
    combatant_deaths INTEGER,
    perpetrator_deaths INTEGER,

    -- Classification
    atrocity_type VARCHAR(50),  -- genocide, mass_killing, colonial, war_crime, etc.
    context VARCHAR(50),        -- war, peace, colonial, civil_war
    intentionality VARCHAR(50), -- targeted, indiscriminate, collateral

    -- Sources
    primary_source VARCHAR(100),
    notes TEXT
);

-- Annual atrocity attribution (for ongoing conflicts)
CREATE TABLE atrocity_economics.annual_deaths (
    id SERIAL PRIMARY KEY,
    episode_id INTEGER REFERENCES atrocity_economics.atrocity_episodes(id),
    country_id INTEGER REFERENCES master.countries(id),  -- perpetrator
    year SMALLINT NOT NULL,
    deaths_best INTEGER,
    deaths_low INTEGER,
    deaths_high INTEGER,
    civilian_pct DECIMAL(5,3),
    source VARCHAR(100)
);

-- Calculated metrics: taxpayer cost per death
CREATE TABLE atrocity_economics.taxpayer_cost_per_death (
    id SERIAL PRIMARY KEY,
    country_id INTEGER REFERENCES master.countries(id),
    year SMALLINT NOT NULL,

    -- Inputs
    median_income DECIMAL(15,2),
    median_tax_paid DECIMAL(10,2),
    milex_pct_budget DECIMAL(5,3),
    median_milex_contribution DECIMAL(10,2),

    -- Deaths attributed to this country-year
    civilian_deaths_caused INTEGER,
    total_deaths_caused INTEGER,

    -- Key metrics
    cost_per_civilian_death DECIMAL(15,2),
    cost_per_total_death DECIMAL(15,2),
    median_taxpayer_share_per_death DECIMAL(10,4),

    notes TEXT
);
```

---

## Methodology

See `methodology/` folder for detailed documents on:

1. **Measuring Deaths** (`methodology/measuring_deaths.md`)
   - Direct vs. indirect deaths
   - Attribution of deaths to state actors
   - Conservative vs. inclusive estimates

2. **Median Income Estimation** (`methodology/median_income.md`)
   - Historical income estimation (pre-1900)
   - Purchasing power parity adjustments
   - Tax burden calculation

3. **Military Spending Allocation** (`methodology/military_spending.md`)
   - What counts as "military" spending
   - Covert operations and black budgets
   - Allocating spending to specific conflicts

4. **Comparative Ethics** (`methodology/comparative_ethics.md`)
   - Just war theory application
   - Pacifist perspective
   - The problem of intentionality

5. **Attribution Problems** (`methodology/attribution.md`)
   - Multi-party conflicts
   - Proxy wars and indirect support
   - Successor state responsibility

---

## Book Structure

See `outline/DETAILED_OUTLINE.md` for full chapter-by-chapter breakdown.

### Part I: The Price of Power (Historical Survey)
~50,000 words, 25+ charts

Chapters examining specific historical case studies with rigorous data analysis.

### Part II: American Reckoning (1975-2025)
~40,000 words, 20+ charts

Year-by-year analysis of the author's lifetime as a median American taxpayer.

### Part III: The Economics of Violence
~30,000 words, 15+ charts

Comparative analysis of high-budget vs. low-budget atrocities.

### Part IV: The Moral Ledger
~15,000 words, 5+ charts

Philosophical synthesis and conclusions.

---

## Chart Requirements

This book requires 65+ data visualizations. See `charts/CHART_MANIFEST.md` for complete specifications.

### Chart Categories

| Category | Count | Examples |
|----------|-------|----------|
| Time series | 25 | US milex 1975-2025, deaths by decade |
| Comparisons | 15 | Countries ranked by deaths/tax dollar |
| Case studies | 12 | Vietnam, Iraq, Cold War, colonial |
| Scatter/correlation | 8 | PTS vs milex, GDP vs atrocity rate |
| Composition | 5 | Budget breakdowns, death type composition |

---

## File Structure

```
books/blood-money/
├── README.md                    # This file
├── research/
│   ├── sources.bib              # Bibliography
│   ├── web_research_notes.md    # Notes from web research
│   ├── existing_scholarship.md  # Survey of prior work
│   └── interviews/              # Expert interviews (if any)
├── data/
│   ├── downloads/               # Raw data downloads
│   ├── processed/               # Cleaned data files
│   └── DATASETS.md              # Dataset documentation
├── charts/
│   ├── CHART_MANIFEST.md        # Complete chart specifications
│   ├── specs/                   # Individual chart specs
│   └── drafts/                  # Work-in-progress visualizations
├── methodology/
│   ├── measuring_deaths.md
│   ├── median_income.md
│   ├── military_spending.md
│   ├── comparative_ethics.md
│   └── attribution.md
├── outline/
│   ├── DETAILED_OUTLINE.md      # Full chapter outline
│   ├── part1_historical.md
│   ├── part2_american.md
│   ├── part3_economics.md
│   └── part4_moral.md
└── notes/
    ├── session_notes/           # Per-session working notes
    └── questions.md             # Open questions to resolve
```

---

## Key Metrics to Calculate

### Per Country-Year
1. **Median income** (local currency, USD PPP)
2. **Median effective tax rate**
3. **Median tax paid** (in 2020 USD)
4. **Military spending as % of budget**
5. **Median taxpayer military contribution**
6. **Civilian deaths attributed** (direct and indirect)
7. **Cost per civilian death** (national level)
8. **Median taxpayer share per death**

### Aggregated Metrics
- **Worst years** for median taxpayer complicity
- **Worst regimes** by deaths per tax dollar
- **Trend analysis** over decades
- **Comparative rankings** across countries and eras

---

## Prior Art and References

### Academic Works
- Anderton & Brauer (2016). *Economic Aspects of Genocides, Other Mass Atrocities, and Their Prevention*
- Rummel, R.J. *Death by Government* and *Statistics of Democide*
- Bank, Stark & Thorndike (2008). *War and Taxes*
- Kreps, Sarah. *Taxing Wars*

### Data Projects
- Brown University Costs of War Project
- UCDP/PRIO Armed Conflict Database
- SIPRI Military Expenditure Database
- Political Terror Scale

### Journalism
- The Intercept's Drone Papers
- Bureau of Investigative Journalism drone strike database

---

## Timeline

Phase 1: Data Acquisition (Weeks 1-4)
- Download and integrate new datasets
- Extend database schema
- Build data loaders

Phase 2: Analysis (Weeks 5-12)
- Calculate all key metrics
- Generate draft charts
- Identify narrative themes

Phase 3: Writing (Weeks 13-30)
- Draft all chapters
- Integrate charts with text
- Iterate on narrative

Phase 4: Review (Weeks 31-36)
- Fact-check all claims against data
- External review
- Final revisions

---

## Author Context

This book is written by Brian Edwards (b. 1975, Waco, Texas). The "American Lifetime" section covers the author's own existence—from the final days of Vietnam through the War on Terror and beyond. This is not abstract history but a personal reckoning with complicity.

The author brings the same rigorous, data-driven approach used in previous graphyard projects (economics, baseball sabermetrics) to a topic usually treated with ideology rather than analysis.

---

## Ethical Considerations

This project deals with mass death and human suffering. We commit to:

1. **Accuracy**: Every death count is sourced and presented with uncertainty ranges
2. **Humanity**: Numbers represent real people; we never lose sight of that
3. **Fairness**: Multiple ethical frameworks presented without forcing conclusions
4. **Responsibility**: Our own country (US) is not exempt from scrutiny
5. **Proportion**: Historical context provided; no presentism

---

*Last updated: January 2026*
