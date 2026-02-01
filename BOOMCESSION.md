# Boomcession Data Schema

Schema for analyzing the disconnect between GDP growth and consumer sentiment.

## Database Schema: `boomcession`

### Tables

| Table | Description | Rows |
|-------|-------------|------|
| `fred_series` | Metadata for each FRED data series | 15 |
| `fred_observations` | Time series observations (long format) | 4,179 |
| `presidential_terms` | US presidential terms 1953-present | 21 |

### Data Series

| Series ID | Description | Coverage | Rows |
|-----------|-------------|----------|------|
| `UMCSENT` | Consumer Sentiment Index | 1952-2025 | 668 |
| `A191RL1Q225SBEA` | Real GDP Growth Rate | 1947-2025 | 314 |
| `W273RE1A156NBEA` | Corporate Profits % GDP | 1929-2024 | 96 |
| `LES1252881600Q` | Real Median Weekly Earnings | 1979-2025 | 187 |
| `OPHNFB` | Labor Productivity Index | 1947-2025 | 315 |
| `W270RE1A156NBEA` | Labor Share of Income | 1948-2024 | 77 |
| `USSTHPI` | House Price Index | 1975-2025 | 203 |
| `MEHOINUSA672N` | Median Household Income | 1984-2024 | 41 |
| `MSPUS` | Median House Sales Price | 1963-2025 | 250 |
| `PCE` | Personal Consumption Expenditures | 1959-2025 | 803 |
| `DHLCRG3Q086SBEA` | Healthcare PCE Growth | 1947-2025 | 315 |
| `DHUTRC1Q027SBEA` | Housing PCE | 1959-2025 | 267 |
| `CP` | Corporate Profits After Tax | 1947-2025 | 315 |
| `GDP` | Nominal GDP | 1947-2025 | 315 |

### Analytical Views

| View | Purpose |
|------|---------|
| `annual_sentiment` | Yearly consumer sentiment averages |
| `sentiment_by_president` | Sentiment averaged by presidential administration |
| `gdp_sentiment_quarterly` | GDP growth paired with sentiment for correlation |
| `annual_gdp_growth` | Yearly GDP growth averages |
| `corporate_profits_pct` | Corporate profits as % of GDP over time |
| `productivity_wages` | Productivity vs wages indexed to 1979 |
| `labor_share` | Labor share of national income |
| `housing_affordability` | Price-to-income ratio for housing |
| `nondiscretionary_spending` | Housing as % of total PCE |

## Sample Queries

### Sentiment by President
```sql
SELECT label, party, ROUND(avg_sentiment::numeric, 1) as sentiment
FROM boomcession.sentiment_by_president
ORDER BY term_start;
```

### Productivity-Wage Gap
```sql
SELECT year,
       ROUND(AVG(productivity_index)::numeric, 1) as productivity,
       ROUND(AVG(wages_index)::numeric, 1) as wages,
       ROUND(AVG(gap)::numeric, 1) as gap
FROM boomcession.productivity_wages
GROUP BY year
ORDER BY year;
```

### Corporate Profits Trend
```sql
SELECT year, ROUND(AVG(profits_pct_gdp)::numeric, 2) as profits_pct_gdp
FROM boomcession.corporate_profits_pct
GROUP BY year ORDER BY year;
```

### GDP vs Sentiment Correlation Data
```sql
SELECT year,
       AVG(gdp_growth) as gdp_growth,
       AVG(avg_sentiment) as sentiment
FROM boomcession.gdp_sentiment_quarterly
WHERE avg_sentiment IS NOT NULL
GROUP BY year
ORDER BY year;
```

## Data Sources

All data from FRED (Federal Reserve Economic Data):
- Consumer Sentiment: University of Michigan
- GDP/Corporate Profits/PCE: Bureau of Economic Analysis
- Wages/Productivity: Bureau of Labor Statistics
- Housing Prices: Census Bureau, FHFA
- Median Income: Census Bureau

## Key Findings (Data Validation)

| Metric | Historical | Recent | Change |
|--------|-----------|--------|--------|
| Corporate profits % GDP | 9.65% (2019) | 12.21% (2021) | +27% |
| Labor share of income | 49.3% (1950) | 42.7% (2024) | -13% |
| Housing price-to-income | 1.37x (1985) | 5.00x (2024) | +265% |
| Sentiment: Trump (1) | 92.8 | - | - |
| Sentiment: Biden | 68.5 | - | -26% |
| Sentiment: Trump (2) | 56.3 | - | -39% |

## File Locations

- Raw data: `datasets/boomcession/`
- Loader script: `scripts/load_boomcession.py`
- Essay plan: `boomcession/PLAN.md`
- Original article: `boomcession/boomcession.txt`
- Original charts: `boomcession/boomcession-0{1-4}.jpg`
