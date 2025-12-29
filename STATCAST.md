# Statcast / Baseball Savant Data

## Source

**Website**: https://baseballsavant.mlb.com/

**Statcast Search**: https://baseballsavant.mlb.com/statcast_search

**CSV Documentation**: https://baseballsavant.mlb.com/csv-docs

**License**: MLB data - personal/educational use

## Description

Statcast is MLB's tracking technology that captures player movements and ball trajectories for every pitch and play. Since 2015, it has provided unprecedented detail on pitch characteristics (velocity, spin, movement) and batted ball outcomes (exit velocity, launch angle, spray angle).

Baseball Savant is MLB's public-facing platform for accessing Statcast data.

## Coverage

| Metric | Availability |
|--------|--------------|
| Pitch tracking | 2008+ (PITCHf/x), 2015+ (Statcast) |
| Exit velocity | 2015+ |
| Launch angle | 2015+ |
| Sprint speed | 2015+ |
| Bat tracking | 2024+ |
| Pitches per season | ~700,000 |

## Download Methods

### 1. pybaseball (Recommended)

```bash
pip install pybaseball
```

```python
import pybaseball
pybaseball.cache.enable()  # Recommended for large queries

from pybaseball import statcast

# Download one week
data = statcast('2024-04-01', '2024-04-07')

# Download full season (30-60 min due to rate limits)
data = statcast('2024-03-20', '2024-11-02')
```

### 2. Download Script

```bash
python scripts/download_statcast.py              # 2024 season
python scripts/download_statcast.py 2023         # Specific year
python scripts/download_statcast.py 2015 2024    # Range of years
```

### 3. Baseball Savant Website

Manual CSV export limited to 30,000 rows per query.

## File Structure

```
datasets/statcast/
├── statcast_2024_sample.csv   # Sample (1 week, 15 MB)
├── statcast_2024.csv          # Full season (~500 MB)
├── statcast_2023.csv
└── ...
```

## Key Fields (118 columns)

### Pitch Identification

| Field | Description |
|-------|-------------|
| `pitch_type` | Pitch classification (FF=fastball, SL=slider, CH=changeup, etc.) |
| `game_date` | Date of the game |
| `pitcher` | Pitcher's MLB ID |
| `player_name` | Pitcher's name |
| `batter` | Batter's MLB ID |
| `events` | Outcome (single, strikeout, home_run, etc.) |
| `description` | Play description |

### Pitch Characteristics

| Field | Description |
|-------|-------------|
| `release_speed` | Pitch velocity at release (mph) |
| `release_spin_rate` | Spin rate (rpm) |
| `release_pos_x` | Horizontal release point (ft from center) |
| `release_pos_z` | Vertical release point (ft from ground) |
| `pfx_x` | Horizontal movement (in) |
| `pfx_z` | Vertical movement (in) |
| `plate_x` | Horizontal location at plate (ft from center) |
| `plate_z` | Vertical location at plate (ft from ground) |
| `zone` | Strike zone location (1-9 in zone, 11-14 out) |

### Batted Ball Data

| Field | Description |
|-------|-------------|
| `launch_speed` | Exit velocity (mph) |
| `launch_angle` | Launch angle (degrees) |
| `hit_distance_sc` | Projected hit distance (ft) |
| `hc_x`, `hc_y` | Hit coordinates on field |
| `bb_type` | Batted ball type (ground_ball, fly_ball, line_drive, popup) |
| `estimated_ba_using_speedangle` | xBA (expected batting average) |
| `estimated_woba_using_speedangle` | xwOBA (expected weighted on-base average) |

### Game Context

| Field | Description |
|-------|-------------|
| `game_pk` | Unique game ID |
| `at_bat_number` | At-bat number within game |
| `pitch_number` | Pitch number within at-bat |
| `inning` | Inning number |
| `inning_topbot` | Top or Bot |
| `outs_when_up` | Outs before pitch |
| `balls`, `strikes` | Count |
| `on_1b`, `on_2b`, `on_3b` | Runner IDs if on base |

### Player Info

| Field | Description |
|-------|-------------|
| `stand` | Batter stance (L/R) |
| `p_throws` | Pitcher throws (L/R) |
| `home_team`, `away_team` | Team abbreviations |
| `home_score`, `away_score` | Scores at time of pitch |

### Bat Tracking (2024+)

| Field | Description |
|-------|-------------|
| `bat_speed` | Bat speed at contact (mph) |
| `swing_length` | Swing path length (ft) |

## Pitch Types

| Code | Pitch Type |
|------|------------|
| `FF` | Four-Seam Fastball |
| `SI` | Sinker |
| `FC` | Cutter |
| `SL` | Slider |
| `CH` | Changeup |
| `CU` | Curveball |
| `KC` | Knuckle Curve |
| `FS` | Splitter |
| `KN` | Knuckleball |
| `ST` | Sweeper |
| `SV` | Slurve |

## Usage Examples

### Load and Analyze

```python
import pandas as pd

df = pd.read_csv('datasets/statcast/statcast_2024_sample.csv')

# Average fastball velocity by pitcher
fastballs = df[df['pitch_type'] == 'FF']
velo_by_pitcher = fastballs.groupby('player_name')['release_speed'].mean()
print(velo_by_pitcher.sort_values(ascending=False).head(10))

# Exit velocity distribution
batted = df[df['launch_speed'].notna()]
print(batted['launch_speed'].describe())

# Home run characteristics
hr = df[df['events'] == 'home_run']
print(f"Average HR exit velo: {hr['launch_speed'].mean():.1f} mph")
print(f"Average HR launch angle: {hr['launch_angle'].mean():.1f}°")
```

### Merge with Retrosheet

```python
# Statcast uses MLB player IDs, Retrosheet uses its own IDs
# Use a player ID mapping table for joins
```

## Rate Limits

- Baseball Savant limits queries to ~30,000 rows
- pybaseball handles this by chunking requests automatically
- Full season download takes 30-60 minutes
- Use `pybaseball.cache.enable()` to avoid re-downloading

## Notes

1. **Data availability**: Full Statcast from 2015; PITCHf/x data 2008-2014 is less complete
2. **Missing data**: Some fields may be null (e.g., no exit velocity on swinging strikes)
3. **xStats**: Expected stats (xBA, xwOBA) use historical outcomes for similar batted balls
4. **Spin axis**: Spin direction data added in recent years
5. **Bat tracking**: New in 2024, not available for older seasons

## References

- [Statcast Glossary](https://www.mlb.com/glossary/statcast)
- [Baseball Savant CSV Docs](https://baseballsavant.mlb.com/csv-docs)
- [pybaseball Documentation](https://github.com/jldbc/pybaseball)
- [Statcast Search](https://baseballsavant.mlb.com/statcast_search)
