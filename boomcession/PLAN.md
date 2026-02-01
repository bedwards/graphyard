# Boomcession Essay Plan for Graphyard

## Overview

A Graphyard-style essay exploring the "boomcession" phenomenon—why Americans hate what looks like an economic boom. Based on Matt Stoller's analysis, extended with Jason Hickel's degrowth framework and additional data dimensions.

## What We Have

**Existing materials in `boomcession/`:**

1. **Full article text** (boomcession.txt) - Matt Stoller's complete essay from Jan 31, 2026
2. **Four charts** (JPG files):
   - **Chart 1**: Consumer sentiment by president (bar chart, JFK through Trump 2)
   - **Chart 2**: Rolling 10-year correlation between GDP growth and consumer sentiment
   - **Chart 3**: Scatter plot of GDP growth vs. sentiment with "The Sentiment Gap"
   - **Chart 4**: Top 20% vs. Bottom 80% share of consumer spending

## Data Sources

All raw data freely downloadable from FRED and other public sources:

| Data Needed | FRED Series / Source | Status |
|-------------|---------------------|--------|
| Consumer Sentiment | UMCSENT | Available 1948-2025 |
| Real GDP Growth | A191RL1Q225SBEA | Available quarterly |
| Corporate Profits % GDP | W273RE1A156NBEA | 9.2% in 2024 |
| Real Wages | LES1252881600Q | Available 1979-2025 |
| Labor Productivity | OPHNFB | Available 1947-2025 |
| Housing Affordability | FIXHAI | Available 1971-2025 |
| Labor Share of Income | W270RE1A156NBEA | Available 1929-2024 |
| Personal Consumption Expenditures | PCE | Available 1929-2025 |
| Healthcare PCE | DHLCRG3Q086SBEA | Available 1959-2025 |
| Housing PCE | DHUTRC1Q027SBEA | Available 1959-2025 |

## Chart Plan (10 Total)

### Recreation of Original Four Charts

1. **Consumer Sentiment by President** - UMCSENT averaged by presidential term
2. **GDP-Sentiment Correlation (Rolling 10-Year)** - Shows collapse from ~0.8 to negative
3. **GDP Growth vs. Sentiment Scatter** - The "Sentiment Gap" visualization
4. **Consumer Spending Share by Income** - Top 20% vs. Bottom 80%

### Six Additional Original Charts

5. **Productivity vs. Wages (1948-2025)** - The 70% gap is the structural cause
6. **Housing Price-to-Income Ratio (1970-2025)** - Non-discretionary explosion
7. **Corporate Profits as % of GDP (1947-2025)** - Where the "boom" is going
8. **Non-Discretionary Spending Share** - Healthcare + Housing + Financial as % of PCE
9. **Labor Share of National Income (1947-2025)** - The shift from 57% to 53%
10. **Welfare Without Growth** - Costa Rica vs. USA (life expectancy vs. GDP)

## Essay Structure (~10,000 words)

### Opening Hook
The paradox: 4.4% GDP growth, lowest consumer sentiment ever recorded. Same 1.1% real wage growth in 2018 and 2025—but sentiment collapsed from 98.4 to 57.6.

### Part I: The Measurement Problem
- GDP measures exchange value, not use value (Hickel)
- Consumer spending includes things people hate paying for
- The "economic termites" extracting value without creating it

### Part II: The Historical Divergence
- Pre-1970s: Growth, wages, and sentiment moved together
- The 1970s inflection point
- Productivity-wage gap opens (70% accumulated difference)
- Labor share of income falls from 57% to 53%

### Part III: The Two Economies
- Corporate profits at record highs
- Top 20% driving 59% of consumer spending (was 50% in 1990)
- Non-discretionary spending explosion (healthcare, housing, financial services)
- Spending inequality: your dollar buys less if you're poor

### Part IV: What GDP Misses
- Hickel's framework: welfare of capitalism vs. welfare of humans
- Costa Rica example: 1/5 the GDP, higher life expectancy
- The gambling economy: second-fastest growing sector
- Monetizing previously unmeasured activity

### Part V: What Comes Next
- The need for new metrics (real income after non-discretionary spending)
- The political implications
- Brief Stoller quote on the "boomcession" dynamic

### Conclusion
Link back to the broader degrowth critique. Reference the Beyond Growth essay.

## Key Quotes to Include

### Matt Stoller (one short quote)
> "A boomcession, where the rich and corporate America experience a boom while working people feel a recession, is a very unhealthy dynamic."

### Jason Hickel
> "GDP growth is, ultimately, an indicator of the welfare of capitalism. That we have all come to see it as a proxy for the welfare of humans represents an extraordinary ideological coup."

## Database Schema

Schema: `boomcession`

Tables:
- `consumer_sentiment` - Monthly University of Michigan data
- `gdp_growth` - Quarterly real GDP growth rates
- `corporate_profits` - Annual corporate profits as % of GDP
- `labor_compensation` - Real wages and productivity indices
- `housing_affordability` - Housing price-to-income ratios
- `labor_share` - Labor share of national income
- `pce_components` - Personal consumption expenditure breakdown
- `presidential_terms` - Reference table for aggregation

## Link to Original

[The Boomcession - Matt Stoller's BIG Newsletter](https://www.thebignewsletter.com/p/the-boomcession-why-everyone-but)
