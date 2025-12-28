# Claude Code Instructions for Graphyard

## Project Overview

Graphyard is a data analysis and visualization project for economic indicators, primarily using World Development Indicators (WDI) data from the World Bank. The project includes:

1. **Data Pipeline**: Clean, normalize, and load WDI data into PostgreSQL
2. **Chart Framework**: Dual-package visualization with Altair (Python) and Observable Plot (TypeScript)
3. **ML Analytics**: Time series forecasting with XGBoost, LightGBM, CatBoost, and PyTorch
4. **Static Site**: Astro-based publication system with GitHub Pages deployment

---

## Critical Rules

### 1. Dataset Files are READ-ONLY

The source files in `datasets/WDI_CSV/` are **read-only** and must NEVER be modified:

```
datasets/WDI_CSV/           # Source data - DO NOT MODIFY
├── WDICSV.csv              # Main data (402K rows, 190MB) - SOURCE OF TRUTH for indicator names
├── WDISeries.csv           # Indicator metadata (1,513 indicators)
├── WDICountry.csv          # Country/entity metadata (265 entries)
├── WDIcountry-series.csv   # Country-series notes
├── WDIfootnote.csv         # Data footnotes
└── WDIseries-time.csv      # Time series metadata
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
├── WDI.md                       # WDI dataset documentation
├── .gitignore
├── scripts/
│   ├── wdi_utils.py            # Clean and load WDI data
│   └── wdi_schema.sql          # Database schema
├── charts/                      # Python chart framework
│   ├── __init__.py
│   ├── spec.py                 # ChartSpec schema (shared with TypeScript)
│   ├── generate_dual.py        # Dual-package chart generator
│   ├── altair_renderer/        # Altair (Vega-Lite) renderer
│   ├── gdp/                    # GDP article charts and data loaders
│   └── themes/                 # Color palettes
├── ml/                          # Machine learning framework
│   ├── __init__.py
│   ├── preprocessing.py        # Missing data, lag features
│   └── forecaster.py           # XGBoost, LightGBM, CatBoost wrappers
├── site/                        # Astro static site
│   ├── astro.config.mjs
│   ├── package.json
│   ├── src/
│   │   ├── layouts/
│   │   ├── components/
│   │   ├── lib/                # Observable Plot renderer
│   │   └── pages/
│   └── scripts/
│       ├── generate-pdf.ts     # PDF export with Playwright
│       └── generate-plot-charts.ts
└── datasets/                    # Git-ignored
    ├── WDI_CSV/                # Source data (READ-ONLY)
    └── WDI_CSV_clean/          # Cleaned output
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

### Database Tables

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

---

## Chart Framework

### Dual-Package System (2025 Best Practices)

Charts are rendered with **both** packages for comparison:

| Package | Language | Strengths |
|---------|----------|-----------|
| **Altair** | Python | Declarative grammar, vl-convert for static export |
| **Observable Plot** | TypeScript | D3-based, excellent TypeScript support, ES modules |

### Chart Type Selection Guide

Based on 2025 data visualization guidelines:

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
npm run charts              # Generate with both packages
npm run charts:altair       # Altair only
npm run charts:plot         # Observable Plot only
npm run build               # Build site (auto-generates Altair charts)
npm run pdf                 # Generate PDFs with Playwright
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

Built with Astro 5.16+ and MDX:

```bash
cd site
npm run dev         # Development server
npm run build       # Production build
npm run preview     # Preview production build
```

### Article Categories

Articles are organized into two categories:

| Category | Description |
|----------|-------------|
| **Latest Research** | Analysis grounded in current academic research and data |
| **Pushing the Boundaries** | Creative synthesis of research, projecting future possibilities |

Articles are organized by domain (economics, technology, climate) and sorted reverse chronologically within each domain.

### Reading Time Requirements

**A true 1-hour read requires approximately 12,000 words** at 200 words per minute for dense technical content.

Use the validator to check reading times:
```bash
python scripts/validate_reading_time.py
python scripts/validate_reading_time.py --article gdp/altair
```

Do NOT claim a reading time that the word count doesn't support.

### Deployment

**Simple main branch deployment** (no GitHub Actions):

1. Build site locally: `cd site && npm run build`
2. Astro outputs to `docs/` folder at project root
3. Commit and push `docs/` to main branch
4. GitHub Pages serves from `main` branch `/docs` folder

```bash
# Full deployment workflow
cd site
npm run charts          # Generate charts with Altair
npm run build           # Build to ../docs/
cd ..
git add docs/
git commit -m "Build site"
git push
```

Site URL: `https://bedwards.github.io/graphyard/`

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
