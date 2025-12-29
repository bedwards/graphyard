# Census Annual Survey of School System Finances (F-33)

## Source

**Download URL**: https://www.census.gov/programs-surveys/school-finances/data/tables.html

**Publisher**: U.S. Census Bureau, Governments Division

**License**: Public domain (U.S. Government work)

## Description

The Annual Survey of School System Finances (Form F-33) is the Census Bureau's comprehensive collection of revenue, expenditure, debt, and asset data for all public elementary and secondary school systems in the United States. It is the primary source for understanding how public schools are funded and how money flows through the K-12 education system.

## Coverage

| Metric | Count |
|--------|-------|
| School Districts | 14,088 |
| States/Territories | 51 (50 states + DC) |
| Data Year | Fiscal Year 2023 |
| Variables | 183 columns |

## Files

| File | Size | Description |
|------|------|-------------|
| `elsec23.txt` | 8.7 MB | Main data file (CSV format) |
| `elsec23f.txt` | 10.4 MB | Flag/imputation file |

## Key Fields

### Identification

| Field | Description |
|-------|-------------|
| `STATE` | FIPS state code (01-56) |
| `PID6` | Census 6-digit school district ID |
| `NCESID` | NCES (National Center for Education Statistics) district ID |
| `NAME` | School district name |
| `FIPST` | FIPS state code (same as STATE) |
| `CONUM` | FIPS county code |
| `CBSA` | Core-Based Statistical Area code |
| `CSA` | Combined Statistical Area code |
| `SCHLEV` | School level (03 = elementary/secondary combined) |
| `YRDATA` | Data year (23 = fiscal year 2023) |
| `UNIT_TYPE` | Type of government unit (5 = school district) |

### Enrollment

| Field | Description |
|-------|-------------|
| `V33` | Fall enrollment (number of students) |

### Revenue (in thousands of dollars)

| Field | Description |
|-------|-------------|
| `TOTALREV` | Total revenue from all sources |
| `TFEDREV` | Total federal revenue |
| `TSTREV` | Total state revenue |
| `TLOCREV` | Total local revenue |

#### Federal Revenue Detail

| Field | Description |
|-------|-------------|
| `C14` | Title I (disadvantaged students) |
| `C15` | Child nutrition programs |
| `C19` | IDEA (special education) |
| `C22` | Vocational education |
| `C23` | Bilingual education |
| `C26` | Impact aid (federal property areas) |
| `C27` | Indian education |
| `B11` | Head Start |
| `C20` | Math/Science education |
| `C25` | Safe and Drug-Free Schools |
| `C36` | Other federal (through state) |
| `B10` | Other federal (direct) |

#### State Revenue Detail

| Field | Description |
|-------|-------------|
| `C01` | General formula assistance |
| `C04` | Staff improvement programs |
| `C05` | Special education programs |
| `C06` | Compensatory/basic skills |
| `C07` | Bilingual education |
| `C08` | Gifted and talented |
| `C09` | Vocational education |
| `C10` | School lunch programs |
| `C11` | Capital outlay/debt service |
| `C12` | Transportation |
| `C13` | Other state revenue |

#### Local Revenue Detail

| Field | Description |
|-------|-------------|
| `T02` | Parent government contributions |
| `T06` | Property taxes |
| `T09` | General sales taxes |
| `T15` | Individual income taxes |
| `T40` | Tuition from pupils |
| `T99` | Other local revenue |

### Expenditure (in thousands of dollars)

| Field | Description |
|-------|-------------|
| `TOTALEXP` | Total expenditures |
| `TCURELSC` | Total current elementary/secondary expenditure |
| `TCURINST` | Total current instruction expenditure |
| `TCURSSVC` | Total current support services |
| `TCUROTH` | Total current other elementary/secondary |
| `TCAPOUT` | Total capital outlay |
| `NONELSEC` | Non-elementary/secondary expenditure |

#### Instruction Expenditure Detail

| Field | Description |
|-------|-------------|
| `E13` | Instruction - salaries |
| `J13` | Instruction - employee benefits |
| `J12` | Instruction - purchased services |
| `J14` | Instruction - supplies |
| `V91` | Instruction - tuition to other districts |
| `V92` | Instruction - tuition to private schools |

#### Support Services Detail

| Field | Description |
|-------|-------------|
| `E17` | Pupil support - salaries |
| `E07` | Instructional staff support - salaries |
| `E08` | General administration - salaries |
| `E09` | School administration - salaries |
| `V40` | Operation/maintenance of plant |
| `V45` | Pupil transportation |
| `V90` | Other support services |
| `V85` | Food services |

### Debt and Assets

| Field | Description |
|-------|-------------|
| `V11` | Long-term debt outstanding (beginning of year) |
| `V13` | Long-term debt issued |
| `V15` | Long-term debt retired |
| `V17` | Long-term debt outstanding (end of year) |
| `V21` | Short-term debt outstanding (beginning) |
| `V23` | Short-term debt outstanding (end) |

### Capital Outlay Detail

| Field | Description |
|-------|-------------|
| `F12` | Land and existing structures |
| `G15` | Construction |
| `K09` | Instructional equipment |
| `K10` | Other equipment |
| `K11` | All other capital outlay |

### Employee Counts (October headcount)

| Field | Description |
|-------|-------------|
| `V10` | Total FTE employees |
| `V12` | Instructional FTE |
| `V14` | Instructional aides FTE |
| `V16` | Guidance counselors FTE |
| `V18` | Librarians FTE |
| `V22` | School administrators FTE |
| `V24` | School administrative support FTE |
| `V30` | All other support staff FTE |

### Revenue Per Pupil (computed)

| Field | Description |
|-------|-------------|
| `_19H` | Total revenue per pupil |
| `_21F` | Federal revenue per pupil |
| `_31F` | State revenue per pupil |
| `_41F` | Local revenue per pupil |
| `_61V` | Current expenditure per pupil |
| `_66V` | Instruction expenditure per pupil |

### Attendance

| Field | Description |
|-------|-------------|
| `W01` | Average daily attendance (ADA) |
| `W31` | Average daily membership (ADM) |
| `W61` | High school completers |

### Teacher Salaries (AE prefix)

| Field | Description |
|-------|-------------|
| `AE1` | Total teachers |
| `AE1A`-`AE1G` | Teachers by salary range |
| `AE2` | Total teacher salary expenditure |
| `AE2A`-`AE2G` | Salary expenditure by range |
| `AE3` | Average teacher salary |
| `AE4`-`AE8` | Salary distribution statistics |

## Flag File (elsec23f.txt)

The flag file contains imputation/data quality flags for each variable with a `FL_` prefix:

| Flag | Meaning |
|------|---------|
| `R` | Reported value |
| `S` | State-reported value |
| `I` | Imputed value |
| `M` | Missing/not applicable |
| `N` | Not reported |
| `Z` | Zero (legitimate) |

## Usage

```python
import pandas as pd

# Load main data
df = pd.read_csv('datasets/census_school_finance/elsec23.txt')

# Per-pupil spending by state
df['spending_per_pupil'] = df['TOTALEXP'] * 1000 / df['V33']
state_avg = df.groupby('STATE').agg({
    'V33': 'sum',
    'TOTALEXP': 'sum',
    'TLOCREV': 'sum',
    'TSTREV': 'sum',
    'TFEDREV': 'sum'
}).reset_index()
state_avg['spending_per_pupil'] = state_avg['TOTALEXP'] * 1000 / state_avg['V33']

# Revenue composition
df['pct_local'] = df['TLOCREV'] / df['TOTALREV'] * 100
df['pct_state'] = df['TSTREV'] / df['TOTALREV'] * 100
df['pct_federal'] = df['TFEDREV'] / df['TOTALREV'] * 100
```

## Sample Queries

```sql
-- Top 10 largest districts by enrollment
SELECT NAME, STATE, V33 as enrollment,
       TOTALEXP * 1000 / V33 as spending_per_pupil
FROM school_finance
ORDER BY V33 DESC
LIMIT 10;

-- State summary with funding sources
SELECT STATE,
       SUM(V33) as total_students,
       SUM(TOTALREV) as total_revenue,
       SUM(TLOCREV) * 100.0 / SUM(TOTALREV) as pct_local,
       SUM(TSTREV) * 100.0 / SUM(TOTALREV) as pct_state,
       SUM(TFEDREV) * 100.0 / SUM(TOTALREV) as pct_federal
FROM school_finance
GROUP BY STATE
ORDER BY total_students DESC;
```

## Notes

1. **Monetary values in thousands**: All dollar amounts are in thousands (e.g., 544179 = $544,179,000)
2. **Enrollment**: V33 is fall enrollment, which may differ from average daily attendance
3. **Fiscal vs calendar year**: FY2023 typically runs July 2022 to June 2023
4. **Missing data**: Some small districts have imputed values (check flag file)
5. **Unit types**: This data covers school districts only (UNIT_TYPE=5)
6. **State variations**: Education governance varies by state (some states have independent districts, others have dependent districts)

## Related Datasets

- **SAIPE**: Poverty estimates for same school districts (`census_saipe/`)
- **Geographic codes**: FIPS codes for linking (`census_geo/`)
- **NCES Common Core of Data**: Additional school-level data
