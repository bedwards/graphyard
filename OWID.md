# Our World in Data (OWID)

## Source

**Website**: https://ourworldindata.org/

**Chart API**: https://docs.owid.io/projects/etl/api/chart-api/

**Datasette (Metadata)**: https://datasette-public.owid.io/

**GitHub**: https://github.com/owid

**License**: CC-BY 4.0 for OWID-produced content; third-party data subject to original license terms

## Description

Our World in Data (OWID) is a scientific online publication that focuses on large global problems such as poverty, disease, hunger, climate change, war, existential risks, and inequality. They present empirical research and data on how the world is changing.

OWID maintains one of the largest curated collections of global development indicators, with data sourced from major institutions (UN, World Bank, WHO, FAO) and academic research. Unlike raw data repositories, OWID provides extensively documented, cleaned, and contextualized datasets.

## Data Access Methods

### 1. Chart API (Primary)

Every chart on OWID supports direct data download by appending file extensions:

| Extension | Description |
|-----------|-------------|
| `.csv` | Chart data in CSV format |
| `.metadata.json` | Chart metadata (sources, descriptions) |
| `.zip` | Complete package (CSV + metadata + README) |
| `.readme.md` | Documentation for the chart |
| `.config.json` | Grapher configuration |

**Example**:
```
https://ourworldindata.org/grapher/life-expectancy.csv
https://ourworldindata.org/grapher/life-expectancy.metadata.json
```

### 2. Datasette API (Metadata)

The Datasette instance at `https://datasette-public.owid.io/` provides SQL access to chart metadata, but **not the actual data values**. Use it to:
- Query the chart catalog
- Find chart slugs by topic
- Explore dataset and variable metadata

### 3. Python Catalog (`owid-catalog`)

```python
pip install owid-catalog

from owid import catalog

# Search for indicators
results = catalog.find("life expectancy")
table = results.iloc[0].load()

# Get chart data directly
from owid.catalog import charts
df = charts.get_data("https://ourworldindata.org/grapher/life-expectancy")
```

## Database Statistics

| Table | Count | Description |
|-------|-------|-------------|
| `charts` | 5,227 | Total charts (4,513 published) |
| `datasets` | 4,483 | Curated datasets |
| `variables` | 616,439 | Individual indicators/metrics |
| `entities` | 23,958 | Countries, regions, and other units |
| `origins` | 10,692 | Original data sources |
| `sources` | 22,734 | Source citations |

## Download Script

```bash
# Download all published charts
python scripts/download_owid.py
```

The script:
1. Fetches the chart index from Datasette (4,513 published charts)
2. Downloads CSV data for each chart
3. Downloads metadata JSON for each chart
4. Rate limits to 2 requests/second to be respectful

**Estimated time**: ~75 minutes for full download
**Estimated size**: ~2-5 GB total (varies by chart)

## File Structure

```
datasets/owid/                  # GITIGNORED
├── chart_index.json            # Index of all published charts
├── charts/                     # CSV data files
│   ├── life-expectancy.csv
│   ├── gdp-per-capita.csv
│   └── ...
└── metadata/                   # Chart metadata
    ├── life-expectancy.json
    ├── gdp-per-capita.json
    └── ...
```

## CSV Format

All chart CSVs follow a consistent structure:

| Column | Description |
|--------|-------------|
| `Entity` | Country, region, or other geographic unit |
| `Code` | ISO 3166-1 alpha-3 code (or OWID code) |
| `Year` | Year (or `Day` for daily data) |
| `[Indicator]` | One or more data columns |

**Example** (life-expectancy.csv):
```csv
Entity,Code,Year,Period life expectancy at birth
Afghanistan,AFG,1950,28.1563
Afghanistan,AFG,1951,28.5836
Albania,ALB,1950,54.4109
...
```

## Metadata Format

Each chart's metadata includes:

```json
{
  "chart": {
    "title": "Life expectancy",
    "citation": "Riley (2005); UN WPP (2024)",
    "originalChartUrl": "https://ourworldindata.org/grapher/life-expectancy"
  },
  "columns": {
    "Period life expectancy at birth": {
      "titleShort": "Life expectancy",
      "descriptionShort": "Period life expectancy at birth...",
      "descriptionKey": ["Key insight 1", "Key insight 2"],
      "unit": "years",
      "shortUnit": "years",
      "sources": [...]
    }
  }
}
```

## Topic Coverage

OWID covers major global development themes:

| Category | Topics |
|----------|--------|
| **Health** | Life expectancy, disease burden, healthcare access, COVID-19, mental health |
| **Population** | Demographics, fertility, mortality, migration, urbanization |
| **Energy** | Energy consumption, electricity, renewables, fossil fuels |
| **Environment** | Climate change, CO2 emissions, biodiversity, deforestation |
| **Economy** | GDP, poverty, inequality, trade, employment |
| **Education** | Literacy, school enrollment, years of schooling |
| **Technology** | Internet, mobile phones, research & development |
| **Food** | Agriculture, hunger, nutrition, land use |
| **Conflict** | War, violence, terrorism, peace |
| **Governance** | Democracy, corruption, human rights |

## Usage Examples

### Loading a Single Chart

```python
import pandas as pd

# Direct from URL
df = pd.read_csv("https://ourworldindata.org/grapher/life-expectancy.csv")

# From downloaded file
df = pd.read_csv("datasets/owid/charts/life-expectancy.csv")

# Filter to specific countries
countries = ["United States", "China", "India", "Germany"]
df_filtered = df[df["Entity"].isin(countries)]
```

### Combining Multiple Charts

```python
import pandas as pd
from pathlib import Path

# Load multiple related charts
life_exp = pd.read_csv("datasets/owid/charts/life-expectancy.csv")
gdp = pd.read_csv("datasets/owid/charts/gdp-per-capita.csv")

# Merge on Entity + Year
merged = life_exp.merge(gdp, on=["Entity", "Code", "Year"], how="inner")
```

### Searching Chart Index

```python
import json

with open("datasets/owid/chart_index.json") as f:
    charts = json.load(f)

# Find charts about climate
climate_charts = [c for c in charts if "climate" in c["title"].lower()]
print(f"Found {len(climate_charts)} climate-related charts")
```

## Key Datasets

### Flagship Compilations

| Dataset | Description |
|---------|-------------|
| [CO2 and GHG Emissions](https://github.com/owid/co2-data) | Complete emissions data (Global Carbon Project) |
| [Energy](https://github.com/owid/energy-data) | Energy production and consumption |
| [COVID-19](https://github.com/owid/covid-19-data) | Pandemic tracking (archived) |

### Frequently Used Charts

| Chart Slug | Description |
|------------|-------------|
| `life-expectancy` | Life expectancy at birth (1950-present) |
| `gdp-per-capita` | GDP per capita (PPP-adjusted) |
| `co2-emissions` | Annual CO2 emissions by country |
| `share-of-population-in-extreme-poverty` | Poverty headcount ratio |
| `human-development-index` | HDI scores |
| `democracy-index` | V-Dem democracy scores |

## Comparison with World Development Indicators (WDI)

| Aspect | OWID | WDI |
|--------|------|-----|
| **Scope** | Curated selection (~5K charts) | Comprehensive (~1.5K indicators) |
| **Sources** | Multiple (UN, WB, WHO, academic) | World Bank primary |
| **Format** | Chart-centric (one CSV per chart) | Indicator-centric (one dataset) |
| **Documentation** | Rich context & methodology | Technical definitions |
| **Updates** | Continuous | Annual |
| **Historical depth** | Varies (some back to 1800s) | Generally 1960+ |

## Notes

1. **Rate limiting**: Be respectful when downloading; use 0.5-1 second delays
2. **Caching**: Add `?nocache` to URLs to bypass CDN caching
3. **Entity codes**: Use ISO 3166-1 alpha-3 codes for joining datasets
4. **Regional aggregates**: Include World, continents, income groups
5. **Missing data**: Charts may have gaps; check metadata for coverage
6. **Third-party licenses**: Original source licenses apply to their data

## References

- [OWID Documentation](https://docs.owid.io/)
- [Chart API](https://docs.owid.io/projects/etl/api/chart-api/)
- [Catalog API](https://docs.owid.io/projects/etl/api/catalog-api/)
- [Easier Data Reuse Announcement](https://ourworldindata.org/easier-to-reuse-our-data)
- [GitHub Repositories](https://github.com/owid)
