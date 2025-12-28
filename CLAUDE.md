# Claude Code Instructions for Graphyard

## Project Overview

Graphyard is a data analysis project working with World Development Indicators (WDI) data from the World Bank. The goal is to clean, normalize, and load this data for analysis.

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
- **Database**: PostgreSQL `graphyard` database (see Database section)

---

## Database

PostgreSQL is available via Docker:

```bash
# Connection details
Host: localhost
Port: 5432
Database: graphyard
User: postgres
Container: hex-index-postgres
```

Connect via CLI:
```bash
docker exec -it hex-index-postgres psql -U postgres -d graphyard
```

---

## WDI Utilities Tool

Use `scripts/wdi_utils.py` to clean and load WDI data:

```bash
# CLEANING
python scripts/wdi_utils.py clean --all                    # Full cleaning pipeline
python scripts/wdi_utils.py clean --fix-encoding           # Level 1: Fix UTF-8 encoding
python scripts/wdi_utils.py clean --normalize              # Level 2: Normalize special chars
python scripts/wdi_utils.py clean --parse-csv              # Level 3: Parse CSV, fix column names
python scripts/wdi_utils.py clean --to-narrow              # Level 4a: Wide → narrow format
python scripts/wdi_utils.py clean --split-entities         # Level 4b: Split by entity type
python scripts/wdi_utils.py clean -f WDICSV.csv --all      # Process single file

# LOADING TO DATABASE
python scripts/wdi_utils.py load --all                     # Load all into PostgreSQL
python scripts/wdi_utils.py load --indicators              # Load indicator metadata
python scripts/wdi_utils.py load --entities                # Load entity metadata
python scripts/wdi_utils.py load --observations            # Load observation data
```

---

## Data Formats

### Wide Format (Original)

Original WDICSV.csv has columns for each year:
```
Country Name, Country Code, Indicator Name, Indicator Code, 1960, 1961, ... 2024
USA, US, GDP, NY.GDP.MKTP.CD, 543300000000, 563300000000, ...
```

### Narrow Format (Cleaned)

After `--to-narrow`, each year becomes a row:
```
Country Name, Country Code, Indicator Name, Indicator Code, Year, Value
USA, US, GDP, NY.GDP.MKTP.CD, 1960, 543300000000
USA, US, GDP, NY.GDP.MKTP.CD, 1961, 563300000000
```

---

## Entity Types

The data mixes actual countries with aggregate groupings. These are separated by `--split-entities`:

| Type | Code Examples | Description |
|------|--------------|-------------|
| `country` | USA, CHN, GBR, BRA | Actual countries (have Region field in metadata) |
| `world` | WLD | Global aggregate |
| `region_geo` | EAS, ECS, LCN, SAS, SSF, NAC, MEA | Main World Bank geographic regions |
| `region_geo_sub` | AFE, AFW, CEB | Sub-regional aggregates |
| `region_geo_exhi` | EAP, ECA, LAC, SSA | Regions excluding high income |
| `income` | HIC, UMC, LMC, LIC, MIC, LMY | Income group aggregates |
| `lending` | IDA, IBRD, IBD, IDX, IBT | Lending category aggregates |
| `region_lending` | TEA, TEC, TLA, TSS | Region + Lending combinations |
| `demographic` | PRE, EAR, LTE, PST | Demographic dividend stages |
| `small_states` | SST, CSS, PSS, OSS | Small state groupings |
| `political` | ARB, EMU, EUU, OED | Political/economic groupings |
| `dev_status` | FCS, HPC, LDC | Development/fragility status |

### Important

- Countries have **non-empty Region** field in WDICountry.csv
- Aggregates have **empty Region** field
- Each aggregate type represents a different analytical dimension
- Do NOT mix countries with aggregates in the same analysis table

---

## Known Data Quality Issues

The cleaning tool (`wdi_clean.py`) addresses these issues:

| Issue | Location | Fix |
|-------|----------|-----|
| Column naming inconsistency | WDISeries uses "Series Code" | Renamed to "Indicator Code" |
| Indicator name mismatches | 96 names differ between WDICSV and WDISeries | Use WDICSV as source of truth |
| Non-ASCII characters | WDISeries has smart quotes, em-dashes, NBSP | Normalized to ASCII equivalents |
| Multiline text fields | WDISeries has embedded newlines | Handled by proper CSV parsing |
| Wide format | Year columns instead of rows | Converted to narrow format |
| Mixed entity types | Countries and aggregates mixed | Split into separate tables |

### Character Normalizations

```
" " → " "   (smart quotes to ASCII quotes)
' ' → '     (smart apostrophes to ASCII)
– — → -     (en-dash, em-dash to hyphen)
NBSP → space (non-breaking space)
```

---

## Project Structure

```
graphyard/
├── CLAUDE.md                    # This file
├── .gitignore                   # Ignores datasets/
├── scripts/
│   ├── wdi_utils.py            # Clean and load WDI data
│   └── wdi_schema.sql          # Database schema
└── datasets/
    ├── WDI_CSV/                # Source data (READ-ONLY, git-ignored)
    └── WDI_CSV_clean/          # Cleaned output (git-ignored)
```

## Database Tables

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
