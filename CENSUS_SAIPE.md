# Census Small Area Income and Poverty Estimates (SAIPE) - School Districts

## Source

**Download URL**: https://www.census.gov/programs-surveys/saipe/data/datasets.html

**Publisher**: U.S. Census Bureau

**License**: Public domain (U.S. Government work)

## Description

The Small Area Income and Poverty Estimates (SAIPE) program provides annual estimates of income and poverty for all U.S. states, counties, and school districts. The school district file (`ussd23.txt`) contains poverty estimates specifically for school-age children (ages 5-17), which is critical for federal Title I funding allocations.

Title I of the Elementary and Secondary Education Act (ESEA) provides federal funds to school districts based on the number of children from low-income families. SAIPE data directly determines how billions of dollars in federal education funding are distributed.

## Coverage

| Metric | Count |
|--------|-------|
| School Districts | 13,143 |
| Data Reference Year | 2023 |
| Release Date | November 27, 2024 |

## Files

| File | Size | Description |
|------|------|-------------|
| `ussd23.txt` | 1.7 MB | School district poverty estimates (fixed-width format) |

## File Format

The data is in fixed-width format with the following layout:

| Position | Width | Field | Description |
|----------|-------|-------|-------------|
| 1-2 | 2 | State FIPS | Two-digit state FIPS code |
| 4-8 | 5 | District ID | Five-digit school district identifier |
| 10-79 | 70 | District Name | School district name (left-justified) |
| 80-88 | 9 | Total Population | Total population in school district |
| 89-98 | 10 | Children 5-17 | Number of children ages 5-17 |
| 99-108 | 10 | Children in Poverty | Number of children 5-17 in poverty |
| 109-119 | 11 | Source File | Source filename |
| 120-130 | 11 | Release Date | Data release date |

## Key Fields

| Field | Description |
|-------|-------------|
| **State FIPS** | Two-digit FIPS state code (01=Alabama, 02=Alaska, ..., 56=Wyoming) |
| **District ID** | Census school district identifier (links to F-33 data via PID6) |
| **District Name** | Full name of the school district |
| **Total Population** | Estimated total population residing in the district boundaries |
| **Children 5-17** | Estimated number of school-age children (ages 5 through 17) |
| **Children in Poverty** | Estimated number of children 5-17 living below the poverty line |

## Usage

```python
import pandas as pd

# Parse fixed-width format
colspecs = [
    (0, 2),    # State FIPS
    (3, 8),    # District ID
    (9, 79),   # District Name
    (79, 88),  # Total Population
    (88, 98),  # Children 5-17
    (98, 108), # Children in Poverty
]

names = ['state_fips', 'district_id', 'district_name',
         'total_pop', 'children_5_17', 'children_poverty']

df = pd.read_fwf('datasets/census_saipe/ussd23.txt',
                 colspecs=colspecs,
                 names=names)

# Clean up
df['district_name'] = df['district_name'].str.strip()
df['state_fips'] = df['state_fips'].astype(str).str.zfill(2)
df['district_id'] = df['district_id'].astype(str).str.zfill(5)

# Calculate poverty rate
df['poverty_rate'] = df['children_poverty'] / df['children_5_17'] * 100

# State-level aggregation
state_summary = df.groupby('state_fips').agg({
    'children_5_17': 'sum',
    'children_poverty': 'sum',
    'total_pop': 'sum'
}).reset_index()
state_summary['poverty_rate'] = state_summary['children_poverty'] / state_summary['children_5_17'] * 100
```

## Sample Data

```
01 00190 Alabaster City School District                                              34832     6631      702
01 00005 Albertville City School District                                            23117     4825     1042
01 00030 Alexander City City School District                                         16821     2691      632
01 00060 Andalusia City School District                                               8937     1502      424
01 00090 Anniston City School District                                               21578     2949     1105
```

Reading the first record:
- State: Alabama (01)
- District ID: 00190
- Name: Alabaster City School District
- Total Population: 34,832
- Children 5-17: 6,631
- Children in Poverty: 702
- **Poverty Rate**: 10.6%

## Linking to Other Datasets

### Link to F-33 School Finance

```python
# SAIPE district_id matches F-33 PID6 (last 5 digits)
saipe['district_id'] = saipe['state_fips'] + saipe['district_id']

# F-33 PID6 is 6 digits
f33['district_id'] = f33['STATE'].str.zfill(2) + f33['PID6'].str[-5:]

merged = pd.merge(f33, saipe, on='district_id', how='left')
```

### Link to Geographic Codes

```python
# State FIPS links to state.txt
# FIPS state + county can link to national_county2020.txt
```

## Title I Funding Context

The SAIPE data is central to Title I funding formulas:

1. **Basic Grants**: Proportional to children in poverty (minimum thresholds apply)
2. **Concentration Grants**: Additional funds for high-poverty districts
3. **Targeted Grants**: Weighted formula giving more to highest-poverty areas
4. **Education Finance Incentive Grants (EFIG)**: State effort and equity factors

The poverty counts in this file directly determine each district's eligibility and allocation amounts under these programs.

## Methodology

SAIPE estimates are produced using a statistical model that combines:

1. **American Community Survey (ACS)** data
2. **Current Population Survey (CPS)** income data
3. **IRS tax return data** (counts of returns by income level)
4. **SNAP/Food Stamp participation** data
5. **Decennial Census** data (as benchmarks)

The model produces estimates with associated margins of error, though the school district file contains point estimates only.

## Notes

1. **Fixed-width format**: Unlike the CSV-formatted F-33 data, SAIPE uses fixed-width columns
2. **District boundaries**: Poverty is estimated for the geographic area served by each district
3. **Population vs enrollment**: Total population includes all residents, not just students
4. **Annual updates**: SAIPE is updated annually, typically released in late fall
5. **Linking**: District IDs should match between SAIPE and F-33, but always verify
6. **Small district estimates**: Very small districts may have less reliable estimates

## Related Datasets

- **F-33 School Finance**: Revenue and expenditure data for same districts (`census_school_finance/`)
- **Geographic codes**: State and county FIPS codes (`census_geo/`)
- **County-level SAIPE**: Poverty estimates at county level (separate file)
- **State-level SAIPE**: State summary statistics (separate file)
