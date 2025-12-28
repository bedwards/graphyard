# World Development Indicators (WDI) Dataset

## Source

**Download URL**: https://databank.worldbank.org/data/download/WDI_CSV.zip

**Publisher**: World Bank

**License**: CC BY-4.0

## Description

The World Development Indicators (WDI) is the World Bank's premier compilation of cross-country comparable data on development. The database contains 1,513 indicators for 265 countries and aggregates, with time series from 1960 to 2024.

## Files

| File | Size | Description |
|------|------|-------------|
| `WDICSV.csv` | 190 MB | Main data file with indicator values by country and year |
| `WDISeries.csv` | 6.4 MB | Indicator metadata (definitions, sources, methodology) |
| `WDICountry.csv` | 151 KB | Country/entity metadata (region, income group, currency) |
| `WDIcountry-series.csv` | 1.3 MB | Country-specific notes for indicators |
| `WDIfootnote.csv` | 73 MB | Footnotes for individual data points |
| `WDIseries-time.csv` | 15 KB | Time-specific notes for indicators |

## Data Structure

### WDICSV.csv (Main Data)

Wide format with columns:
- `Country Name` - Full country/entity name
- `Country Code` - 3-letter ISO code
- `Indicator Name` - Full indicator description
- `Indicator Code` - Unique indicator identifier
- `1960` through `2024` - Year columns with values

### WDISeries.csv (Indicator Metadata)

- `Series Code` - Indicator identifier (maps to `Indicator Code` in main data)
- `Topic` - Category (e.g., "Environment: Agricultural production")
- `Indicator Name` - Full description
- `Short definition` / `Long definition` - Detailed explanations
- `Unit of measure` - Units (%, ratio, USD, etc.)
- `Periodicity` - Data frequency (typically "Annual")
- `Source` - Original data source
- `Aggregation method` - How regional/global aggregates are computed
- `License Type` - Data license

### WDICountry.csv (Entity Metadata)

- `Country Code` - 3-letter code
- `Short Name` / `Long Name` - Entity names
- `Region` - Geographic region (empty for aggregate entities)
- `Income Group` - World Bank income classification
- `Currency Unit` - National currency
- `Special Notes` - Country-specific notes

## Entity Types

The data contains both countries and aggregate groupings:

| Type | Count | Examples |
|------|-------|----------|
| Countries | 217 | USA, CHN, GBR, BRA |
| World | 1 | WLD |
| Geographic Regions | 7 | EAS, ECS, LCN, SAS, SSF |
| Income Groups | 6 | HIC, UMC, LMC, LIC |
| Lending Categories | 5 | IDA, IBRD, IBT |
| Other Aggregates | 29 | EMU, EUU, OED, ARB |

**Key distinction**: Countries have a non-empty `Region` field; aggregates have empty `Region`.

## Sample Indicators

| Code | Name | Unit |
|------|------|------|
| NY.GDP.MKTP.CD | GDP (current US$) | USD |
| NY.GDP.PCAP.CD | GDP per capita (current US$) | USD |
| SP.POP.TOTL | Population, total | Count |
| SP.DYN.LE00.IN | Life expectancy at birth | Years |
| SI.POV.DDAY | Poverty headcount ratio at $2.15/day | % |
| EN.ATM.CO2E.PC | CO2 emissions (metric tons per capita) | Metric tons |

## Usage

```bash
# Download and extract
curl -O https://databank.worldbank.org/data/download/WDI_CSV.zip
unzip WDI_CSV.zip -d datasets/WDI_CSV/

# Clean and load (using project tools)
python scripts/wdi_utils.py clean --all
python scripts/wdi_utils.py load --all
```

## Notes

1. **Source of truth**: Use `WDICSV.csv` for indicator names (not `WDISeries.csv`)
2. **Missing values**: Empty cells indicate no data available
3. **Aggregates**: Regional/income aggregates are pre-computed by World Bank
4. **Updates**: WDI is updated quarterly; download fresh data as needed
