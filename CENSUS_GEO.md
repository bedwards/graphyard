# Census Geographic Reference Files

## Source

**Download URL**: https://www.census.gov/geographies/reference-files.html

**Publisher**: U.S. Census Bureau, Geography Division

**License**: Public domain (U.S. Government work)

## Description

These geographic reference files provide the official codes and names for U.S. geographic entities. They are essential for linking datasets that use different geographic identifiers (FIPS codes, CBSA codes, etc.).

## Coverage

| File | Records | Description |
|------|---------|-------------|
| `state.txt` | 57 | States, DC, and territories |
| `national_county2020.txt` | 3,235 | All U.S. counties |
| `cbsa_delineation_2020.xls` | ~1,900 | Metropolitan/micropolitan areas |
| `all-geocodes-v2023.xlsx` | ~42,000 | Complete geographic hierarchy |

## Files

### state.txt

FIPS state codes for all 50 states, DC, and U.S. territories.

**Format**: Pipe-delimited (`|`)

| Field | Description |
|-------|-------------|
| `STATE` | Two-digit FIPS state code |
| `STUSAB` | Two-letter state abbreviation (postal code) |
| `STATE_NAME` | Full state name |
| `STATENS` | Geographic Names Information System (GNIS) ID |

**Sample**:
```
STATE|STUSAB|STATE_NAME|STATENS
01|AL|Alabama|01779775
02|AK|Alaska|01785533
04|AZ|Arizona|01779777
06|CA|California|01779778
```

**Notes**:
- Codes 01-56 cover the 50 states, DC, and outlying areas
- Code 03 (unused) was formerly assigned to "Canal Zone"
- Territories included: AS (60), GU (66), MP (69), PR (72), VI (78)

### national_county2020.txt

FIPS county codes for all U.S. counties and county-equivalents.

**Format**: Pipe-delimited (`|`)

| Field | Description |
|-------|-------------|
| `STATE` | State abbreviation |
| `STATEFP` | Two-digit FIPS state code |
| `COUNTYFP` | Three-digit FIPS county code |
| `COUNTYNS` | GNIS county identifier |
| `COUNTYNAME` | County name |
| `CLASSFP` | FIPS class code |
| `FUNCSTAT` | Functional status code |

**Sample**:
```
STATE|STATEFP|COUNTYFP|COUNTYNS|COUNTYNAME|CLASSFP|FUNCSTAT
AL|01|001|00161526|Autauga County|H1|A
AL|01|003|00161527|Baldwin County|H1|A
CA|06|001|01675839|Alameda County|H1|A
CA|06|037|00277283|Los Angeles County|H1|A
```

**FIPS Class Codes (CLASSFP)**:
- `H1`: Active county or equivalent
- `H4`: Inactive county or equivalent
- `H5`: Statistical equivalent (census area, borough)
- `H6`: Incorporated place serving as county equivalent
- `C7`: Independent city (Virginia)

**Functional Status (FUNCSTAT)**:
- `A`: Active government
- `F`: Fictitious entity
- `N`: Nonfunctioning government
- `S`: Statistical entity

### cbsa_delineation_2020.xls

Core-Based Statistical Area (CBSA) definitions linking counties to metro/micro areas.

**Format**: Excel (.xls)

**Key Fields**:
- CBSA Code: 5-digit metropolitan/micropolitan area code
- CBSA Title: Metro/micro area name (e.g., "New York-Newark-Jersey City, NY-NJ-PA")
- Metropolitan/Micropolitan: Type indicator
- CSA Code: Combined Statistical Area code (for linked metros)
- CSA Title: Combined area name
- County FIPS: State + county FIPS
- Central/Outlying: Whether county is central or outlying

**Example CBSAs**:
| CBSA Code | CBSA Title | Type |
|-----------|------------|------|
| 35620 | New York-Newark-Jersey City, NY-NJ-PA | Metropolitan |
| 31080 | Los Angeles-Long Beach-Anaheim, CA | Metropolitan |
| 16980 | Chicago-Naperville-Elgin, IL-IN-WI | Metropolitan |
| 10100 | Aberdeen, SD | Micropolitan |

### all-geocodes-v2023.xlsx

Complete geographic hierarchy from nation to county subdivision.

**Format**: Excel (.xlsx)

**Hierarchy Levels**:
1. Nation (US)
2. Region (Northeast, Midwest, South, West)
3. Division (New England, Middle Atlantic, etc.)
4. State
5. County
6. County Subdivision (towns, townships, MCDs)

## Usage

### Python - Loading State Codes

```python
import pandas as pd

states = pd.read_csv('datasets/census_geo/state.txt', sep='|')

# Create lookup dictionary
state_names = dict(zip(states['STATE'], states['STATE_NAME']))
state_abbrevs = dict(zip(states['STATE'], states['STUSAB']))

# Example: Get state name from FIPS
print(state_names['06'])  # California
```

### Python - Loading County Codes

```python
import pandas as pd

counties = pd.read_csv('datasets/census_geo/national_county2020.txt', sep='|')

# Create full FIPS code
counties['FIPS'] = counties['STATEFP'] + counties['COUNTYFP']

# Find counties by state
ca_counties = counties[counties['STATEFP'] == '06']
```

### Python - Loading CBSA Delineations

```python
import pandas as pd

cbsa = pd.read_excel('datasets/census_geo/cbsa_delineation_2020.xls',
                     sheet_name=0, skiprows=2)

# Get all counties in a metro area
nyc_metro = cbsa[cbsa['CBSA Code'] == 35620]
```

### Linking to School Finance Data

```python
# F-33 school finance has CONUM (county FIPS) and CBSA fields
# Link to get county and metro names

finance = pd.read_csv('datasets/census_school_finance/elsec23.txt')
counties = pd.read_csv('datasets/census_geo/national_county2020.txt', sep='|')

# Create matching key in county file
counties['CONUM'] = counties['STATEFP'] + counties['COUNTYFP']

# Merge
merged = finance.merge(counties[['CONUM', 'COUNTYNAME']],
                       left_on='CONUM', right_on='CONUM', how='left')
```

## FIPS Code Reference

### State FIPS (Two Digits)

| FIPS | State | FIPS | State |
|------|-------|------|-------|
| 01 | Alabama | 27 | Minnesota |
| 02 | Alaska | 28 | Mississippi |
| 04 | Arizona | 29 | Missouri |
| 05 | Arkansas | 30 | Montana |
| 06 | California | 31 | Nebraska |
| 08 | Colorado | 32 | Nevada |
| 09 | Connecticut | 33 | New Hampshire |
| 10 | Delaware | 34 | New Jersey |
| 11 | DC | 35 | New Mexico |
| 12 | Florida | 36 | New York |
| 13 | Georgia | 37 | North Carolina |
| 15 | Hawaii | 38 | North Dakota |
| 16 | Idaho | 39 | Ohio |
| 17 | Illinois | 40 | Oklahoma |
| 18 | Indiana | 41 | Oregon |
| 19 | Iowa | 42 | Pennsylvania |
| 20 | Kansas | 44 | Rhode Island |
| 21 | Kentucky | 45 | South Carolina |
| 22 | Louisiana | 46 | South Dakota |
| 23 | Maine | 47 | Tennessee |
| 24 | Maryland | 48 | Texas |
| 25 | Massachusetts | 49 | Utah |
| 26 | Michigan | 50 | Vermont |
| 51 | Virginia | 54 | West Virginia |
| 53 | Washington | 55 | Wisconsin |
| 56 | Wyoming | | |

### Territories

| FIPS | Territory |
|------|-----------|
| 60 | American Samoa |
| 66 | Guam |
| 69 | Northern Mariana Islands |
| 72 | Puerto Rico |
| 74 | U.S. Minor Outlying Islands |
| 78 | U.S. Virgin Islands |

## Notes

1. **FIPS vs postal codes**: FIPS codes are numeric; postal abbreviations are the familiar two-letter codes
2. **County equivalents**: Louisiana has parishes, Alaska has boroughs, independent cities in Virginia
3. **2020 vintage**: County boundaries may change; these reflect 2020 Census definitions
4. **CBSA updates**: Metro area definitions are updated periodically by OMB
5. **Missing codes**: FIPS 03 (Canal Zone) and other historical codes are no longer used

## Related Datasets

- **School Finance (F-33)**: Uses CONUM and CBSA codes (`census_school_finance/`)
- **SAIPE**: Uses state FIPS codes (`census_saipe/`)
- **Census TIGER/Line**: Detailed geographic boundaries (separate download)
