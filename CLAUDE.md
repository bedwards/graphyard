# Claude Code Instructions for Graphyard

## Project Overview

Graphyard is a multi-domain data analysis and visualization project. Each domain has its own data source, data loaders, and essay-style articles:

| Domain | Data Source | Schema | Articles |
|--------|-------------|--------|----------|
| Economics | World Development Indicators (WDI) | `public` | GDP, Beyond Growth |
| Sports Analytics | Lahman Baseball Database | `lahman` | Baseball Evolution |

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
│   ├── baseballdatabank-master/
│   │   └── core/            # CSV files (People.csv, Batting.csv, etc.)
│   └── lahman.zip           # Original download
└── lahman_clean/            # Processed Lahman files (if needed)
```

**NEVER use `chmod +w` on these files. NEVER modify them directly.**

### 2. Naming Conventions

Always use **"Indicator"** terminology, never "Series":
- Column names: `indicator_code`, `indicator_name`
- Variable names: `indicator`, not `series`
- **WDICSV.csv is the source of truth** for indicator names (not WDISeries.csv)

### 3. Output Locations

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

PostgreSQL is available via Docker:

```bash
# Connection details
Host: localhost
Port: 5432
Database: graphyard
User: postgres
Password: postgres
Container: hex-index-postgres
```

Connect via CLI:
```bash
docker exec -it hex-index-postgres psql -U postgres -d graphyard
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

### Schema: lahman (Baseball Data)

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

### Installed Packages (Apple Silicon Optimized)

```
PyTorch 2.9+      - MPS backend for Apple Silicon GPU
XGBoost 3.1+      - Gradient boosting (CPU on Mac)
LightGBM 4.6+     - Fast leaf-wise boosting (CPU on Mac)
CatBoost 1.2+     - Categorical feature handling (CPU on Mac)
Skforecast 0.19+  - Time series forecasting utilities
```

### Key Challenges Addressed

1. **Different start dates**: Countries begin data collection at different years
2. **Missing values**: MCAR, MAR, MNAR patterns handled via preprocessing
3. **Optimal lag selection**: Research shows 4-9 lags optimal for annual data
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

# Compare models
forecaster = TimeSeriesForecaster(
    models=["xgboost", "lightgbm", "catboost"]
)
results = forecaster.fit_and_compare(X, y, n_splits=5)

print(f"Best model: {forecaster.best_model}")
print(f"MAE: {results[forecaster.best_model].mae:.4f}")
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
