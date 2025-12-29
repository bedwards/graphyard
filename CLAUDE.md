# Claude Code Instructions for Graphyard

## Project Overview

Graphyard is a multi-domain data analysis and visualization project. Each domain has its own data source, data loaders, and essay-style articles:

| Domain | Data Source | Schema | Articles |
|--------|-------------|--------|----------|
| Economics | World Development Indicators (WDI) | `public` | GDP, Beyond Growth |
| Economics | Our World in Data (OWID) | TBD | TBD |
| Sports Analytics | Lahman Baseball Database | `lahman` | Baseball Evolution |
| Sports Analytics | Retrosheet (Game Logs + Events) | TBD | TBD |
| Sports Analytics | Statcast / Baseball Savant | TBD | TBD |
| Sports Analytics | NCAA Basketball (Kaggle March Madness) | TBD | TBD |
| Education | Census School Finance (F-33) | TBD | TBD |
| Education | Census SAIPE (School District Poverty) | TBD | TBD |
| Reference | Census Geographic Codes | - | - |

See also: [WDI.md](WDI.md), [OWID.md](OWID.md), [LAHMAN.md](LAHMAN.md), [RETROSHEET.md](RETROSHEET.md), [STATCAST.md](STATCAST.md), [NCAA_BASKETBALL.md](NCAA_BASKETBALL.md), [CENSUS_SCHOOL_FINANCE.md](CENSUS_SCHOOL_FINANCE.md), [CENSUS_SAIPE.md](CENSUS_SAIPE.md), [CENSUS_GEO.md](CENSUS_GEO.md)

The project includes:

1. **Shared Infrastructure**: Database connection management and base loader patterns (`shared/database.py`)
2. **Data Pipelines**: Domain-specific data loaders that extend `BaseDataLoader`
3. **Chart Framework**: Dual-package visualization with Altair (Python) and Observable Plot (TypeScript)
4. **ML Analytics**: Time series forecasting with XGBoost, LightGBM, CatBoost, and PyTorch
5. **Static Site**: Astro-based publication system with GitHub Pages deployment

---

## Critical Rules

### 1. Dataset Files are READ-ONLY

All source data lives in `datasets/` (gitignored). **Never modify source files directly.**

```
datasets/                    # All source data - GITIGNORED
├── WDI_CSV/                 # World Development Indicators (raw download)
│   ├── WDICSV.csv           # Main data (402K rows, 190MB)
│   ├── WDISeries.csv        # Indicator metadata
│   └── ...
├── WDI_CSV_clean/           # Processed WDI files
├── lahman/                  # Lahman Baseball Database (raw download)
│   └── baseballdatabank-master/
│       └── core/            # CSV files (People.csv, Batting.csv, etc.)
├── ncaa_basketball/         # Kaggle March Madness data
│   ├── MTeams.csv           # Men's teams
│   ├── MRegularSeasonDetailedResults.csv  # Box scores (118K games)
│   ├── MMasseyOrdinals.csv  # Computer rankings (5.5M rows, 194 systems)
│   └── ...                  # 36 CSV files total
├── census_school_finance/   # Census F-33 school finance data
│   ├── elsec23.txt          # Main data (14K districts, 183 columns)
│   └── elsec23f.txt         # Data quality flags
├── census_saipe/            # Census SAIPE poverty estimates
│   └── ussd23.txt           # School district poverty (13K districts)
├── census_geo/              # Census geographic reference files
│   ├── state.txt            # State FIPS codes (57 states/territories)
│   ├── national_county2020.txt  # County FIPS codes (3,235 counties)
│   ├── cbsa_delineation_2020.xls  # Metro/micro area definitions
│   └── all-geocodes-v2023.xlsx   # Complete geographic hierarchy
├── owid/                    # Our World in Data charts
│   ├── chart_index.json     # Index of all published charts (4,513)
│   ├── charts/              # CSV data for each chart
│   └── metadata/            # JSON metadata for each chart
├── retrosheet/              # Retrosheet baseball data
│   ├── gamelogs/            # Game summaries 1871-2024 (224 MB, 159 files)
│   └── events/              # Play-by-play 1910-2024 (882 MB, 5,413 files)
├── statcast/                # Baseball Savant Statcast data
│   └── statcast_YYYY.csv    # Pitch-by-pitch data (~500 MB/season)
└── *_clean/                 # Processed files (as needed)
```

**NEVER use `chmod +w` on these files. NEVER modify them directly.**

**Sample vs Full Downloads**: Some large datasets (OWID, Statcast) may only have samples downloaded initially. Do not hesitate to download additional data when needed for an essay. Use the download scripts in `scripts/`.

### 2. Database Architecture

Each domain uses its own PostgreSQL schema in the `graphyard` database:

| Schema | Domain | Tables |
|--------|--------|--------|
| `public` | WDI Economics | indicators, entities, country_data, etc. |
| `lahman` | Baseball (Lahman) | people, batting, pitching, teams, etc. |
| `baseball` | Baseball (unified) | Consolidated tables with FK constraints |

**Design Principles**:
- **Normalized**: No duplicate data; use foreign keys
- **Master Entity Tables**: Resolve keys across datasets (e.g., countries, players)
- **Prefix tables by source** when consolidating: `lahman_batting`, `retrosheet_events`
- **Foreign key constraints** enforce referential integrity

### 3. Naming Conventions

Always use **"Indicator"** terminology, never "Series":
- Column names: `indicator_code`, `indicator_name`
- Variable names: `indicator`, not `series`
- **WDICSV.csv is the source of truth** for indicator names (not WDISeries.csv)

### 4. Output Locations

- **Cleaned CSV files**: `datasets/WDI_CSV_clean/`
- **Database**: PostgreSQL `graphyard` database
- **Charts**: `site/public/assets/charts/{altair,plot}/`

---

## Project Structure

```
graphyard/
├── CLAUDE.md                    # This file
├── docs/                        # Built site (GitHub Pages serves this)
├── shared/                      # Shared infrastructure
│   ├── __init__.py
│   └── database.py             # DatabaseConfig, BaseDataLoader
├── scripts/
│   ├── wdi_utils.py            # Clean and load WDI data
│   ├── load_lahman.py          # Download and load Lahman baseball data
│   ├── lahman_schema.sql       # PostgreSQL schema for Lahman
│   └── validate_reading_time.py # Article word count validator
├── charts/                      # Python chart generation
│   ├── generate_dual.py        # Chart generator (Altair) - all domains
│   ├── altair_renderer/        # Altair renderer
│   ├── gdp/                    # GDP article charts and data loaders
│   ├── beyond_growth/          # Beyond Growth article data loaders
│   └── baseball/               # Baseball article data loaders (LahmanLoader)
├── ml/                          # Machine learning (XGBoost, LightGBM, CatBoost)
├── site/                        # Astro source
│   ├── astro.config.mjs        # Outputs to ../docs/
│   ├── package.json
│   └── src/
│       ├── lib/articles.ts     # Article registry with domains
│       └── pages/articles/     # Article pages by domain
│           ├── gdp/            # Economics: GDP article
│           ├── beyond-growth/  # Economics: Beyond Growth article
│           └── baseball/       # Sports: Baseball article
└── datasets/                    # Git-ignored, READ-ONLY source data
```

---

## Database

PostgreSQL runs in Docker (not locally installed):

```bash
# Connection details
Host: localhost
Port: 5432
Database: graphyard (main), hex-index
User: postgres
Password: postgres
Container: hex-index-postgres
Image: postgres:16-alpine
```

Connect via CLI:
```bash
docker exec -it hex-index-postgres psql -U postgres -d graphyard
```

Backup databases:
```bash
docker exec hex-index-postgres pg_dump -U postgres -Fc graphyard > backups/graphyard_$(date +%Y%m%d).dump
docker exec hex-index-postgres pg_dump -U postgres -Fc hex-index > backups/hex-index_$(date +%Y%m%d).dump
```

Restore from backup:
```bash
docker exec -i hex-index-postgres pg_restore -U postgres -d graphyard < backups/graphyard_YYYYMMDD.dump
```

### Schema: public (WDI Data)

```
indicators          - Indicator metadata (1,513 rows)
entities            - Country/aggregate metadata (265 rows)
entity_types        - Entity type definitions (13 rows)
country_data        - Country observations (7.5M rows)
world_data          - World aggregate observations (34K rows)
region_geo_data     - Geographic region observations (495K rows)
income_data         - Income group observations (207K rows)
lending_data        - Lending category observations (348K rows)
other_aggregate_data - Other aggregate observations (454K rows)
```

### Schema: lahman (Baseball Data - Raw Lahman)

```
people              - Player biographical data (19,878 rows)
teams               - Team statistics by year (2,925 rows)
teams_franchises    - Franchise metadata (120 rows)
batting             - Batting statistics (107,429 rows)
pitching            - Pitching statistics (47,628 rows)
salaries            - Player salaries 1985-2016 (26,428 rows)
managers            - Manager records (3,536 rows)
appearances         - Games by position (107,357 rows)
```

See [LAHMAN.md](LAHMAN.md) for full schema documentation.

### Schema: baseball (Unified Baseball Data)

```
players             - Master player table linking all ID systems (19,878 rows)
                      Links: lahman_id, retrosheet_id, mlb_id, bbref_id
statcast_pitches    - Pitch-by-pitch Statcast data 2024-2025 (1,471,491 rows)
                      Includes: pitch type, velocity, spin, location, exit velo, xBA, xwOBA
retrosheet_gamelogs - Game summaries 1871-2024 (231,888 games)
                      Includes: scores, batting stats, attendance, park
```

Data sources consolidated with foreign key linkage potential across ID systems.

### Schema: master (Cross-dataset Entity Resolution)

```
countries           - Canonical country data with ISO codes (217 rows)
country_codes       - Code mappings (WDI, COW, UN codes) (1,000 rows)
code_systems        - Registry of coding systems
```

### Schema: pts (Political Terror Scale)

```
country_year_scores - Human rights violation scores 1976-2024 (10,531 rows)
```

### Schema: cow (Correlates of War)

```
wars                - Wars 1816-present (95 inter-state wars)
war_participants    - War participation records (337 rows)
national_capabilities - CINC scores 1816-2016 (15,951 rows)
mids                - Militarized Interstate Disputes
mid_participants    - MID participation
alliances           - Formal military alliances
alliance_members    - Alliance membership
```

### Schema: ucdp (Uppsala Conflict Data Program)

```
conflicts           - Armed conflicts 1946-present
actors              - Conflict parties (governments, rebels)
dyads               - Pairs of actors in conflict
ged_events          - Georeferenced conflict events (300K+ events)
battle_deaths       - Annual battle death aggregates
one_sided_violence  - Violence against civilians
```

### Schema: ibc (Iraq Body Count)

```
incidents           - Documented civilian casualty incidents (51,608 rows)
individuals         - Individual casualty records
```

### Schema: health (Health Data)

```
covid_country_day   - COVID-19 daily data by country (429,435 rows)
jhu_covid_timeseries - JHU time series data
indicators          - Health indicator definitions
indicator_values    - Health indicator values
```

---

## Chart Framework

Charts are rendered with **Altair** (Python) using vl-convert for static SVG/PNG export.

### Chart Type Selection

| Question | Chart Type |
|----------|------------|
| How does X change over time? | LINE |
| How do categories compare? | BAR |
| What is the ranking? | HORIZONTAL_BAR |
| What is the composition? | DONUT (max 5 parts) |
| How are X and Y related? | SCATTER |
| What is the distribution? | HISTOGRAM |

### Commands

```bash
cd site
npm run dev                 # Development server
npm run build               # Build site (auto-generates charts)
npm run preview             # Preview production build
```

---

## Machine Learning Framework

### Hardware: Mac Studio (Apple Silicon)

**M1/M2 Max with unified memory and GPU.** Key performance findings from benchmarks:

| Framework | Time | Notes |
|-----------|------|-------|
| **CatBoost** | 0.21s | Fastest - highly optimized CPU |
| **DIY PyTorch (MPS)** | 0.58s | Simple custom TabularNet |
| **LightGBM** | 0.62s | Fast leaf-wise boosting |
| **XGBoost** | 0.74s | Solid all-rounder |
| TabNet | 29s+ | Avoid - framework overhead |
| PyTorch Lightning | 26s+ | Avoid - excessive overhead |

**Key insight**: Well-optimized CPU algorithms (CatBoost, LightGBM) beat GPU-accelerated neural networks for tabular data at medium scale. Reserve PyTorch MPS for custom architectures where GPU parallelism matters.

### Framework Selection

| Task | Use | Avoid |
|------|-----|-------|
| **Tabular regression/classification** | CatBoost (default) | TabNet, Lightning |
| **Time series forecasting** | CatBoost → LightGBM → XGBoost | Complex neural nets |
| **Categorical features** | CatBoost (native handling) | Manual encoding |
| **GPU experimentation** | DIY PyTorch + MPS | High-overhead frameworks |
| **Production deployment** | Gradient boosting models | Neural nets (unless justified) |

### Installed Packages

```
PyTorch 2.9+      - MPS backend for Apple Silicon GPU
XGBoost 3.1+      - Gradient boosting (CPU on Mac)
LightGBM 4.6+     - Fast leaf-wise boosting (CPU on Mac)
CatBoost 1.2+     - Categorical feature handling (CPU on Mac)
Skforecast 0.19+  - Time series forecasting utilities
```

### Writing Guidelines

**Domain-centric, not tech-centric.** In essays:
- Present predictions and forecasts as natural extensions of analysis
- Don't call out "ML" or "machine learning" as special
- Focus on what readers learn, not the technology behind it
- Lead with insights, mention methodology briefly if at all
- Visualize results (feature importance, forecasts) without jargon

Example: Instead of "Our XGBoost model achieved 94% accuracy", write "Historical patterns suggest GDP will grow 2.3% next year, with consumer spending driving most of the increase."

### Time Series Challenges

1. **Different start dates**: Countries begin data collection at different years
2. **Missing values**: MCAR, MAR, MNAR patterns handled via preprocessing
3. **Optimal lag selection**: 4-9 lags optimal for annual economic data
4. **Walk-forward validation**: Proper time series evaluation (not k-fold)

### Usage

```python
from ml import prepare_panel_data, TimeSeriesForecaster, PanelForecaster

# Prepare panel data with lag features
df_prepared, metadata = prepare_panel_data(
    df,
    value_col="value",
    entity_col="entity_code",
    lags=[1, 2, 3, 4, 5],
    rolling_windows=[3, 5],
    handle_missing="linear",
    min_years=10,
)

# Compare models (CatBoost typically wins)
forecaster = TimeSeriesForecaster(
    models=["catboost", "lightgbm", "xgboost"]
)
results = forecaster.fit_and_compare(X, y, n_splits=5)

# For custom PyTorch with MPS acceleration
import torch
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
model = TabularNet(n_features, hidden_dim=64).to(device)
```

### PyTorch MPS Pattern

```python
import torch
import torch.nn as nn

class TabularNet(nn.Module):
    """Simple tabular network for Apple Silicon MPS."""
    def __init__(self, n_features: int, hidden_dim: int = 64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_features, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1)
        )

    def forward(self, x):
        return self.net(x)

# Training with MPS
device = torch.device("mps")
model = TabularNet(n_features=10).to(device)
X_tensor = torch.tensor(X.values, dtype=torch.float32).to(device)
y_tensor = torch.tensor(y.values, dtype=torch.float32).to(device)
```

---

## WDI Utilities Tool

```bash
# CLEANING
python scripts/wdi_utils.py clean --all                    # Full pipeline
python scripts/wdi_utils.py clean --to-narrow              # Wide → narrow format
python scripts/wdi_utils.py clean --split-entities         # Split by entity type

# LOADING TO DATABASE
python scripts/wdi_utils.py load --all                     # Load all into PostgreSQL
```

---

## Entity Types

The data mixes actual countries with aggregate groupings:

| Type | Examples | Description |
|------|----------|-------------|
| `country` | USA, CHN, GBR | Actual countries (have Region field) |
| `world` | WLD | Global aggregate |
| `region_geo` | EAS, ECS, LCN | World Bank geographic regions |
| `income` | HIC, UMC, LMC | Income group aggregates |
| `lending` | IDA, IBRD | Lending category aggregates |

**Important**: Countries have non-empty Region field; aggregates have empty Region.

---

## Static Site

Built with Astro. Articles organized by domain (economics, technology, climate), sorted reverse chronologically.

### Reading Time

**200 words per minute** for technical content. Validate with:
```bash
python scripts/validate_reading_time.py
```

### Deployment

Main branch deployment (GitHub Pages serves from `/docs`):

```bash
cd site
npm run build           # Builds to ../docs/ (charts auto-generated)
cd ..
git add docs/ && git commit -m "Build site" && git push
```

Site: https://bedwards.github.io/graphyard/

---

## Known Data Quality Issues

| Issue | Fix |
|-------|-----|
| Column naming inconsistency | Renamed "Series Code" to "Indicator Code" |
| Indicator name mismatches | Use WDICSV as source of truth |
| Non-ASCII characters | Normalized to ASCII equivalents |
| Wide format | Converted to narrow format |
| Mixed entity types | Split into separate tables |

---

## References

### Chart Types (2025)
- https://www.luzmo.com/blog/chart-types
- https://guides.lib.berkeley.edu/data-visualization/type

### Python Visualization
- https://altair-viz.github.io/
- https://pypi.org/project/vl-convert-python/

### TypeScript Visualization
- https://observablehq.com/plot/
- https://d3js.org/

### Time Series ML
- https://skforecast.org/
- https://cienciadedatos.net/documentos/py39-forecasting-time-series-with-skforecast-xgboost-lightgbm-catboost

### Apple Silicon ML
- https://developer.apple.com/metal/pytorch/
- https://pytorch.org/blog/introducing-accelerated-pytorch-training-on-mac/
- https://gist.github.com/bedwards/2fe3d8dc4bcd0b9fe99c6819f28dab8d (Mac M1 benchmark)
