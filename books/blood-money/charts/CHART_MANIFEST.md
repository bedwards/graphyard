# Blood Money: Chart Manifest

**Total Charts: 70**

This document specifies every chart required for the book, including data sources, chart types, and key specifications.

---

## Chart Naming Convention

`ch{chapter:02d}-{slug}` - e.g., `ch01-deaths-by-type-20c`

---

## Opening Chapter Charts

### ch00-tax-breakdown-2024
- **Type**: HORIZONTAL BAR
- **Title**: "Where Your Federal Tax Dollar Went (2024)"
- **Data Source**: National Priorities Project / OMB
- **X-axis**: Percentage of federal budget
- **Y-axis**: Budget categories (Military, Health, Interest, etc.)
- **Highlight**: Military at 24%
- **Key Insight**: Nearly a quarter of every tax dollar goes to military

### ch00-historical-milex-share
- **Type**: LINE
- **Title**: "Military Spending as Share of Federal Budget (1940-2025)"
- **Data Source**: OMB Historical Tables, SIPRI
- **X-axis**: Year (1940-2025)
- **Y-axis**: Percentage of federal budget (0-90%)
- **Annotations**: WWII peak, Vietnam, Reagan buildup, post-9/11
- **Key Insight**: Current levels are low by historical standards but high in absolute terms

---

## Part I: Historical Survey Charts

### ch01-deaths-by-type-20c
- **Type**: STACKED BAR
- **Title**: "20th Century Deaths by Cause"
- **Data Source**: Rummel democide, UCDP, academic estimates
- **X-axis**: Category (Genocide, War-Combatant, War-Civilian, Other Democide)
- **Y-axis**: Deaths in millions
- **Color**: Distinct colors for each category
- **Key Insight**: Democide exceeds war deaths

### ch01-ucdp-vs-rummel
- **Type**: SCATTER
- **Title**: "Death Estimates: UCDP vs. Rummel"
- **Data Source**: UCDP battle deaths, Rummel democide
- **X-axis**: UCDP estimate (log scale)
- **Y-axis**: Rummel estimate (log scale)
- **Line**: 45-degree reference line
- **Key Insight**: Methodological differences create substantial variance

### ch01-direct-indirect-ratio
- **Type**: HORIZONTAL BAR
- **Title**: "Indirect Deaths Exceed Direct Deaths"
- **Data Source**: Brown Costs of War, academic studies
- **Categories**: Iraq, Afghanistan, Syria, Yemen, Vietnam
- **Bars**: Grouped (direct, indirect) for each conflict
- **Key Insight**: 4:1 indirect to direct ratio in modern conflicts

### ch01-death-counting-methods
- **Type**: DIAGRAM/TABLE
- **Title**: "How We Count the Dead"
- **Content**: Comparison matrix of methodologies (UCDP, Rummel, PTS, IBC)
- **Columns**: Coverage, Definition, Data Type, Limitations

### ch02-median-income-historical
- **Type**: LINE (multi-series)
- **Title**: "Median Income Through History (2020 PPP Dollars)"
- **Data Source**: Maddison Project, Lindert-Williamson, Census
- **X-axis**: Year (1800-2020)
- **Y-axis**: Income in 2020 international dollars
- **Series**: USA, UK, Germany, USSR/Russia, China, Japan
- **Key Insight**: Dramatic convergence in late 20th century

### ch02-tax-burden-historical
- **Type**: LINE (multi-series)
- **Title**: "Effective Tax Rate for Median Citizens"
- **Data Source**: OECD, academic estimates
- **X-axis**: Year (1800-2020)
- **Y-axis**: Effective tax rate (0-50%)
- **Series**: Same countries as above
- **Annotations**: Major tax reforms, war peaks

### ch02-mtmc-comparison
- **Type**: HORIZONTAL BAR
- **Title**: "Median Taxpayer Military Contribution by Era"
- **Data Source**: Calculated from income, tax, and military spending data
- **Y-axis**: Country-era combinations (e.g., "US 1968", "USSR 1943", "UK 1815")
- **X-axis**: MTMC in 2020 PPP dollars
- **Key Insight**: WWII era contributions dwarf peacetime

### ch03-colonial-deaths-map
- **Type**: CHOROPLETH MAP
- **Title**: "Colonial Deaths by Territory"
- **Data Source**: Academic estimates, Rummel
- **Geography**: World map showing colonial territories
- **Color Scale**: Deaths (log scale)
- **Key Insight**: Concentration in South Asia and Africa

### ch03-congo-population
- **Type**: LINE
- **Title**: "Congo Population Under Leopold II"
- **Data Source**: Academic estimates, census data
- **X-axis**: Year (1880-1920)
- **Y-axis**: Population in millions
- **Annotations**: Leopold's rule begins/ends, worst atrocity years
- **Key Insight**: Population decline of 1-10 million

### ch03-german-swa-spending
- **Type**: BAR
- **Title**: "German Military Spending on Southwest Africa Campaign"
- **Data Source**: German colonial records, academic estimates
- **X-axis**: Year (1904-1908)
- **Y-axis**: Reichsmarks (and 2020 USD equivalent)
- **Key Insight**: Calculated cost per Herero/Nama death

### ch03-british-india-famines
- **Type**: BAR
- **Title**: "British India Famine Death Tolls"
- **Data Source**: Academic estimates
- **X-axis**: Famine (1770, 1876-78, 1943, etc.)
- **Y-axis**: Deaths in millions
- **Annotations**: Contributing policies
- **Key Insight**: Policy-induced famines killed tens of millions

### ch04-20c-democide-treemap
- **Type**: TREEMAP
- **Title**: "20th Century Democide: 262 Million Dead"
- **Data Source**: Rummel
- **Hierarchy**: Regime → Episodes
- **Size**: Death count
- **Color**: Ideology (Communist, Fascist, Authoritarian, Colonial)
- **Key Insight**: Communist regimes dominate by count

### ch04-soviet-repression-timeline
- **Type**: LINE
- **Title**: "Soviet Political Deaths by Year"
- **Data Source**: Rummel, Memorial, academic estimates
- **X-axis**: Year (1917-1991)
- **Y-axis**: Deaths (log scale)
- **Annotations**: Civil War, Collectivization, Great Terror, WWII, Gulag
- **Key Insight**: 1930s and 1940s peaks

### ch04-nazi-war-spending
- **Type**: STACKED AREA
- **Title**: "Nazi Germany Military Spending"
- **Data Source**: Overy, economic historians
- **X-axis**: Year (1933-1945)
- **Y-axis**: Reichsmarks or GDP percentage
- **Stacks**: Army, Navy, Air Force, SS/Other
- **Key Insight**: Military consumed 70%+ of GDP at peak

### ch04-china-glf-mortality
- **Type**: LINE
- **Title**: "China Mortality During Great Leap Forward"
- **Data Source**: Demographic estimates
- **X-axis**: Year (1955-1965)
- **Y-axis**: Death rate per 1,000 and total deaths
- **Annotations**: GLF policies begin/end
- **Key Insight**: Mortality spike of 15-55 million

### ch04-totalitarian-deaths-per-dollar
- **Type**: HORIZONTAL BAR
- **Title**: "Killing Efficiency: Deaths per Million Dollars of Military Spending"
- **Data Source**: Calculated from SIPRI/historical milex and death estimates
- **Y-axis**: Regime-era
- **X-axis**: Deaths per $1M (log scale)
- **Key Insight**: Poorest regimes achieved highest efficiency

### ch05-cold-war-proxy-map
- **Type**: MAP
- **Title**: "Cold War Proxy Conflicts and Death Tolls"
- **Data Source**: UCDP, academic estimates
- **Geography**: World map with points/bubbles
- **Size**: Death toll
- **Color**: US-backed vs. Soviet-backed vs. both
- **Key Insight**: Global scope of superpower violence

### ch05-cia-budget-historical
- **Type**: LINE
- **Title**: "Estimated US Intelligence Budget (1947-2024)"
- **Data Source**: irp.fas.org, congressional disclosures, academic estimates
- **X-axis**: Year
- **Y-axis**: Billions of 2020 dollars
- **Annotations**: Major disclosures, budget spikes
- **Key Insight**: Hidden costs of covert operations

### ch05-guatemala-deaths-timeline
- **Type**: LINE
- **Title**: "Guatemala Conflict Deaths (1960-1996)"
- **Data Source**: CEH Truth Commission, UCDP
- **X-axis**: Year
- **Y-axis**: Deaths
- **Annotations**: 1954 coup, major massacres, peace accord
- **Key Insight**: 200,000+ dead from CIA-initiated conflict

### ch05-us-military-aid-latin-america
- **Type**: STACKED AREA
- **Title**: "US Military Aid to Latin America (1950-1990)"
- **Data Source**: USAID, congressional records
- **X-axis**: Year
- **Y-axis**: Millions of 2020 dollars
- **Stacks**: El Salvador, Guatemala, Colombia, Chile, Nicaragua (Contras), Other
- **Key Insight**: Aid patterns correlate with violence

### ch06-us-wars-cost-deaths
- **Type**: SCATTER
- **Title**: "Post-1990 US Conflicts: Cost vs. Death Toll"
- **Data Source**: CRS, Costs of War, UCDP
- **X-axis**: Total cost (billions, log scale)
- **Y-axis**: Total deaths (log scale)
- **Points**: Gulf War, Kosovo, Afghanistan, Iraq, Libya, Syria
- **Key Insight**: Iraq and Afghanistan dominate both axes

### ch06-iraq-casualties-timeline
- **Type**: LINE
- **Title**: "Iraq Conflict Deaths by Year"
- **Data Source**: Iraq Body Count, UCDP
- **X-axis**: Year (2003-2020)
- **Y-axis**: Deaths
- **Annotations**: Invasion, Surge, ISIS, withdrawal
- **Key Insight**: Peak violence 2006-2007

### ch06-afghanistan-timeline
- **Type**: LINE
- **Title**: "Afghanistan Conflict Deaths by Year"
- **Data Source**: UCDP, Costs of War
- **X-axis**: Year (2001-2021)
- **Y-axis**: Deaths
- **Annotations**: Initial invasion, surge, withdrawal
- **Key Insight**: Violence increased over time despite spending

### ch06-drone-strikes-map
- **Type**: MAP
- **Title**: "US Drone Strikes (2004-2024)"
- **Data Source**: Bureau of Investigative Journalism
- **Geography**: Focus on Pakistan, Yemen, Somalia
- **Points**: Strike locations with casualty counts
- **Color**: Civilian vs. militant casualties
- **Key Insight**: Geographic expansion of remote warfare

### ch06-post-911-cumulative
- **Type**: STACKED AREA
- **Title**: "Cumulative Post-9/11 War Deaths"
- **Data Source**: Costs of War
- **X-axis**: Year (2001-2024)
- **Y-axis**: Cumulative deaths
- **Stacks**: Afghanistan, Iraq, Pakistan, Syria, Yemen, Other
- **Key Insight**: 940,000+ direct deaths

---

## Part II: American Experience Charts

### ch07-median-income-1975-2025
- **Type**: LINE
- **Title**: "Real Median Household Income (1975-2025)"
- **Data Source**: Census Bureau, FRED
- **X-axis**: Year
- **Y-axis**: 2024 dollars
- **Annotations**: Recessions, policy changes
- **Key Insight**: Stagnation from 1975-1995, growth since

### ch07-effective-tax-rate-1975-2025
- **Type**: LINE
- **Title**: "Median Effective Federal Tax Rate (1975-2025)"
- **Data Source**: CBO, Tax Policy Center
- **X-axis**: Year
- **Y-axis**: Percentage
- **Annotations**: Reagan tax cuts, Clinton increases, Bush cuts, TCJA
- **Key Insight**: Declining burden on middle class

### ch07-cumulative-taxes-paid
- **Type**: AREA
- **Title**: "Cumulative Lifetime Federal Taxes at Median Income"
- **Data Source**: Calculated from income and tax rate data
- **X-axis**: Age/Year
- **Y-axis**: Cumulative taxes (2024 dollars)
- **Key Insight**: Lifetime contribution reaching $X

### ch08-vietnam-total-deaths
- **Type**: BAR
- **Title**: "Vietnam War Death Toll by Category"
- **Data Source**: Academic estimates
- **Categories**: US military, ARVN, NVA/VC, Civilians (North), Civilians (South)
- **Key Insight**: ~3 million total deaths

### ch08-milex-1970s
- **Type**: LINE
- **Title**: "US Military Spending (1970-1980)"
- **Data Source**: SIPRI, OMB
- **X-axis**: Year
- **Y-axis**: Billions of 2024 dollars
- **Annotations**: Vietnam withdrawal, Carter baseline
- **Key Insight**: Post-Vietnam low before Reagan

### ch08-cold-war-proxy-deaths-1970s
- **Type**: BAR
- **Title**: "Deaths in Cold War Proxy Conflicts (1975-1980)"
- **Data Source**: UCDP, academic estimates
- **Categories**: Angola, Ethiopia, Cambodia, Afghanistan
- **Key Insight**: Conflicts continued despite detente

### ch09-reagan-milex-buildup
- **Type**: LINE
- **Title**: "Reagan Military Buildup (1980-1989)"
- **Data Source**: SIPRI, OMB
- **X-axis**: Year
- **Y-axis**: Billions of 2024 dollars
- **Highlight**: Reagan term
- **Key Insight**: Near-doubling of military spending

### ch09-central-america-deaths
- **Type**: STACKED BAR
- **Title**: "Central American Conflict Deaths (1980-1992)"
- **Data Source**: UCDP, truth commissions
- **X-axis**: Year
- **Y-axis**: Deaths
- **Stacks**: El Salvador, Guatemala, Nicaragua
- **Key Insight**: 300,000+ deaths during Reagan-Bush era

### ch09-us-military-aid-1980s
- **Type**: BAR
- **Title**: "Top US Military Aid Recipients (1980-1988)"
- **Data Source**: USAID, congressional records
- **Y-axis**: Countries
- **X-axis**: Millions of 2024 dollars
- **Key Insight**: Israel and Central America dominate

### ch10-peace-dividend-milex
- **Type**: LINE
- **Title**: "The Peace Dividend (1988-2000)"
- **Data Source**: SIPRI, OMB
- **X-axis**: Year
- **Y-axis**: Billions of 2024 dollars
- **Annotations**: Cold War ends, Gulf War, Clinton drawdown
- **Key Insight**: Spending declined but remained substantial

### ch10-1990s-conflicts-deaths
- **Type**: HORIZONTAL BAR
- **Title**: "US Military Action Death Tolls (1989-2000)"
- **Data Source**: Academic estimates, UCDP
- **Y-axis**: Conflicts (Panama, Gulf War, Somalia, Haiti, Bosnia, Kosovo)
- **X-axis**: Deaths (log scale)
- **Key Insight**: Relatively low-casualty era

### ch10-balkans-casualties
- **Type**: STACKED BAR
- **Title**: "Balkans Intervention Casualties"
- **Data Source**: ICTY, academic estimates
- **Categories**: NATO personnel, Serb military, Albanian/Kosovar civilians
- **Key Insight**: Civilian toll of "humanitarian" intervention

### ch11-post-911-milex-surge
- **Type**: LINE
- **Title**: "Post-9/11 Military Spending Surge"
- **Data Source**: SIPRI, OMB
- **X-axis**: Year (2000-2010)
- **Y-axis**: Billions of 2024 dollars
- **Annotations**: 9/11, Afghanistan, Iraq invasion
- **Key Insight**: Spending roughly doubled

### ch11-afghanistan-iraq-deaths-cumulative
- **Type**: LINE (dual axis or multi-series)
- **Title**: "Cumulative Deaths: Afghanistan and Iraq"
- **Data Source**: UCDP, Costs of War
- **X-axis**: Year (2001-2021)
- **Y-axis**: Cumulative deaths
- **Series**: Afghanistan, Iraq
- **Key Insight**: Iraq accumulated deaths faster

### ch11-iraq-civilian-deaths-by-year
- **Type**: BAR
- **Title**: "Iraqi Civilian Deaths (2003-2008)"
- **Data Source**: Iraq Body Count
- **X-axis**: Year
- **Y-axis**: Deaths
- **Key Insight**: Peak during civil war 2006-2007

### ch11-detention-population
- **Type**: LINE
- **Title**: "Detention Populations Over Time"
- **Data Source**: DoD, ACLU, journalism
- **X-axis**: Year (2001-2024)
- **Y-axis**: Detainees
- **Series**: Guantanamo, Bagram, CIA black sites (estimated)
- **Key Insight**: Peak early, gradual decline

### ch12-drone-strikes-by-year
- **Type**: BAR
- **Title**: "Drone Strikes by Year and Country"
- **Data Source**: Bureau of Investigative Journalism
- **X-axis**: Year
- **Y-axis**: Number of strikes
- **Stacks**: Pakistan, Yemen, Somalia, Libya, Other
- **Key Insight**: Peak under Obama, decline after

### ch12-drone-casualties-breakdown
- **Type**: STACKED BAR
- **Title**: "Drone Strike Casualties: Who Died?"
- **Data Source**: Bureau of Investigative Journalism
- **X-axis**: Year or Country
- **Y-axis**: Deaths
- **Stacks**: Confirmed militants, Alleged militants, Civilians, Unknown
- **Key Insight**: Significant civilian toll

### ch12-milex-obama-era
- **Type**: LINE
- **Title**: "Military Spending (2008-2016)"
- **Data Source**: SIPRI, OMB
- **X-axis**: Year
- **Y-axis**: Billions of 2024 dollars
- **Annotations**: Sequestration, drawdowns
- **Key Insight**: Decline from Iraq War peaks

### ch13-yemen-casualties-timeline
- **Type**: LINE
- **Title**: "Yemen Conflict Deaths (2015-2024)"
- **Data Source**: ACLED, UCDP
- **X-axis**: Year
- **Y-axis**: Deaths
- **Annotations**: Saudi intervention, famine peaks
- **Key Insight**: One of world's worst humanitarian crises

### ch13-us-military-aid-ukraine
- **Type**: BAR
- **Title**: "US Military Aid to Ukraine"
- **Data Source**: Congressional appropriations
- **X-axis**: Fiscal year (2022-2025)
- **Y-axis**: Billions of dollars
- **Key Insight**: Historic levels of military aid

### ch13-gaza-casualties-2023-24
- **Type**: BAR
- **Title**: "Gaza Casualties (October 2023-Present)"
- **Data Source**: Gaza Health Ministry, UN
- **X-axis**: Month
- **Y-axis**: Deaths
- **Key Insight**: Rapid accumulation of civilian deaths

### ch14-50-year-timeline
- **Type**: LINE (dual axis)
- **Title**: "Fifty Years of Taxpayer-Funded Violence"
- **Data Source**: Calculated aggregation
- **X-axis**: Year (1975-2025)
- **Y-axis Left**: Median MTMC (dollars)
- **Y-axis Right**: Attributed deaths
- **Key Insight**: Correlation between spending and deaths

### ch14-worst-years-ranking
- **Type**: HORIZONTAL BAR
- **Title**: "Worst Years by Deaths per Taxpayer Dollar"
- **Data Source**: Calculated
- **Y-axis**: Year
- **X-axis**: Deaths per million MTMC dollars
- **Key Insight**: Identifies worst years

### ch14-cumulative-deaths-stacked
- **Type**: STACKED AREA
- **Title**: "Cumulative Deaths by Conflict (1975-2025)"
- **Data Source**: UCDP, Costs of War
- **X-axis**: Year
- **Y-axis**: Cumulative deaths
- **Stacks**: Vietnam aftermath, Cold War proxy, Post-Cold War, Post-9/11
- **Key Insight**: Where the bodies are

### ch14-cost-per-death-trend
- **Type**: LINE
- **Title**: "Cost per Attributed Death Over Time"
- **Data Source**: Calculated
- **X-axis**: Year (1975-2025)
- **Y-axis**: Dollars per death
- **Key Insight**: Rising cost of killing

### ch14-taxpayer-share-per-death
- **Type**: LINE
- **Title**: "Median Taxpayer's Share of Each Death"
- **Data Source**: Calculated
- **X-axis**: Year
- **Y-axis**: Fractional deaths per taxpayer (or dollars per death share)
- **Key Insight**: Individual taxpayer's implied contribution

---

## Part III: Economics of Violence Charts

### ch15-rwanda-killing-rate
- **Type**: LINE
- **Title**: "Rwanda Genocide: Deaths per Day"
- **Data Source**: Academic estimates
- **X-axis**: Day (April-July 1994)
- **Y-axis**: Deaths per day
- **Annotations**: Key events
- **Key Insight**: 8,000+ killed per day at peak

### ch15-low-budget-atrocities
- **Type**: SCATTER
- **Title**: "Low-Budget Mass Killing"
- **Data Source**: Multiple sources
- **X-axis**: Documented military/arms spending (log scale)
- **Y-axis**: Death toll (log scale)
- **Points**: Rwanda, Cambodia, Darfur, etc.
- **Key Insight**: Mass killing doesn't require high tech

### ch15-cost-per-death-comparison
- **Type**: HORIZONTAL BAR
- **Title**: "Cost per Death: High vs. Low Budget"
- **Data Source**: Calculated
- **Y-axis**: Conflict/atrocity
- **X-axis**: Cost per death (log scale)
- **Key Insight**: Orders of magnitude difference

### ch15-weapon-type-deaths
- **Type**: TREEMAP
- **Title**: "20th Century Atrocity Deaths by Method"
- **Data Source**: Rummel, academic estimates
- **Hierarchy**: Method category → Specific conflicts
- **Size**: Death count
- **Color**: Method type
- **Key Insight**: Small arms and starvation dominate

### ch16-weapon-costs
- **Type**: HORIZONTAL BAR
- **Title**: "The Price of Modern Weapons"
- **Data Source**: DoD, defense industry
- **Y-axis**: Weapon system
- **X-axis**: Unit cost (log scale)
- **Key Insight**: Staggering per-unit costs

### ch16-us-cost-per-death-overtime
- **Type**: LINE
- **Title**: "US Military Cost per Attributed Death (1950-2024)"
- **Data Source**: Calculated from spending and casualties
- **X-axis**: Decade
- **Y-axis**: Dollars per death (log scale)
- **Key Insight**: Increasing cost per casualty

### ch16-iraq-spending-breakdown
- **Type**: STACKED BAR
- **Title**: "Iraq War Spending Breakdown"
- **Data Source**: CRS, Costs of War
- **Categories**: Combat operations, Equipment, Personnel, Contractors, Reconstruction, Other
- **Key Insight**: Combat operations were fraction of total

### ch17-deaths-per-gdp-pct
- **Type**: SCATTER
- **Title**: "Deaths Caused vs. Military Burden"
- **Data Source**: Calculated
- **X-axis**: Military spending as % of GDP
- **Y-axis**: Attributed deaths (log scale)
- **Points**: Various country-eras
- **Trend line**: Show relationship
- **Key Insight**: Poor countries can kill efficiently

### ch17-intentionality-spectrum
- **Type**: DIAGRAM
- **Title**: "Intentionality Spectrum"
- **Content**: Visual representation from targeted genocide → collateral damage
- **Examples**: For each category
- **Key Insight**: Moral weight varies with intent

### ch17-moral-distance-framework
- **Type**: DIAGRAM
- **Title**: "Layers of Moral Responsibility"
- **Content**: Concentric circles from soldier → commander → government → taxpayer
- **Key Insight**: Framework for analyzing complicity

### ch17-normalized-comparison
- **Type**: HORIZONTAL BAR
- **Title**: "Atrocities Ranked by Various Metrics"
- **Data Source**: Calculated
- **Multiple panels**: Raw deaths, Deaths/GDP%, Deaths/$milex, Deaths/taxpayer
- **Key Insight**: Rankings change with normalization

### ch18-gdp-vs-democide
- **Type**: SCATTER
- **Title**: "National Wealth vs. Democide"
- **Data Source**: Maddison, Rummel
- **X-axis**: GDP per capita (log scale)
- **Y-axis**: Democide deaths (log scale)
- **Points**: 20th century regimes
- **Key Insight**: Poorest regimes killed most

### ch18-killing-efficiency
- **Type**: HORIZONTAL BAR
- **Title**: "Deaths per Million Dollars Military Spending"
- **Data Source**: Calculated
- **Y-axis**: Regime-era
- **X-axis**: Deaths per $1M
- **Key Insight**: Inverse relationship with wealth

### ch18-indirect-death-comparison
- **Type**: BAR
- **Title**: "Direct vs. Indirect Deaths"
- **Data Source**: Academic estimates
- **Grouped bars**: For each major atrocity
- **Key Insight**: Indirect deaths often exceed direct

### ch18-development-counterfactual
- **Type**: LINE
- **Title**: "Development Foregone Due to State Violence"
- **Data Source**: Calculated counterfactual
- **X-axis**: Year
- **Y-axis**: GDP per capita (actual vs. counterfactual)
- **Key Insight**: Violence stunts development

---

## Part IV: Moral Ledger Charts

### ch19-responsibility-frameworks
- **Type**: DIAGRAM
- **Title**: "Ethical Frameworks for Taxpayer Responsibility"
- **Content**: Matrix comparing Just War Theory, Pacifism, Democratic Responsibility, Structural approaches
- **Key Insight**: Different frameworks, different conclusions

### ch20-war-tax-resistance-timeline
- **Type**: LINE
- **Title**: "War Tax Resistance in the United States"
- **Data Source**: NWTRCC, academic sources
- **X-axis**: Year (1755-present)
- **Y-axis**: Documented resistance incidents or participants
- **Annotations**: Major wars
- **Key Insight**: Historical tradition of resistance

### ch20-public-opinion-vs-military-action
- **Type**: SCATTER
- **Title**: "Public Opinion vs. Military Continuation"
- **Data Source**: Polling data
- **X-axis**: Public support (%)
- **Y-axis**: Duration after crossing <50% support
- **Points**: Various conflicts
- **Key Insight**: Wars continue despite opposition

### ch21-comprehensive-ranking
- **Type**: HORIZONTAL BAR
- **Title**: "The Final Ranking: Deaths per Median Taxpayer Dollar"
- **Data Source**: Calculated across all case studies
- **Y-axis**: Country-era (sorted)
- **X-axis**: Metric
- **Key Insight**: The ultimate comparison

### ch21-final-summary-table
- **Type**: TABLE
- **Title**: "Complete Atrocity Data"
- **Columns**: Atrocity | Years | Deaths (Low-Mid-High) | Milex | Cost/Death | Median Taxpayer Share
- **Rows**: All analyzed atrocities
- **Key Insight**: The complete ledger

---

## Technical Specifications

### Common Styling
- Font: System fonts matching Graphyard site
- Colors: Muted palette; red for deaths, blue for spending, gray for neutral
- Annotations: Minimal but informative
- Axes: Always labeled with units

### Data Precision
- All death counts shown with ranges where available
- Sources cited in chart caption or appendix
- Calculated metrics documented in methodology

### Accessibility
- All charts have alt text
- Color-blind friendly palettes
- Data tables available as alternative

---

*Last updated: January 2026*
