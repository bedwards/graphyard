# NCAA Basketball Dataset (March Machine Learning Mania 2025)

## Source

**Download URL**: https://www.kaggle.com/competitions/march-machine-learning-mania-2025/data

**Publisher**: Kaggle (competition data compiled from multiple sources)

**License**: Competition rules apply; data for non-commercial/research use

## Description

This is the dataset from Kaggle's annual "March Machine Learning Mania" competition, where participants build models to predict the outcomes of the NCAA Men's and Women's basketball tournaments (March Madness). The dataset contains comprehensive historical game results, tournament brackets, team rankings, and detailed box score statistics.

## Coverage

| Division | Seasons | Teams | Regular Season Games | Tournament Games |
|----------|---------|-------|---------------------|------------------|
| Men's (M) | 1985-2025 | 380 | 192,930 | 2,518 |
| Women's (W) | 1998-2025 | 378 | 137,028 | 1,650 |
| **Total** | - | **758** | **329,958** | **4,168** |

## File Structure

Files are prefixed with `M` (Men's) or `W` (Women's) where applicable.

### Core Reference Tables

| File | Rows | Description |
|------|------|-------------|
| `MTeams.csv` / `WTeams.csv` | 380/378 | Team IDs and names |
| `MSeasons.csv` / `WSeasons.csv` | 41/28 | Season metadata (day zero, region names) |
| `Conferences.csv` | 51 | Conference abbreviations and full names |
| `Cities.csv` | 503 | City IDs for game locations |

### Game Results

| File | Rows | Description |
|------|------|-------------|
| `MRegularSeasonCompactResults.csv` | 192,930 | Regular season scores (winner, loser, scores, location) |
| `MRegularSeasonDetailedResults.csv` | 118,882 | Regular season with full box scores (2003+) |
| `MNCAATourneyCompactResults.csv` | 2,518 | NCAA tournament scores |
| `MNCAATourneyDetailedResults.csv` | 1,382 | NCAA tournament with box scores (2003+) |
| `MConferenceTourneyGames.csv` | 6,793 | Conference tournament results |
| `MSecondaryTourneyCompactResults.csv` | 1,809 | NIT and other tournaments |

### Tournament Structure

| File | Rows | Description |
|------|------|-------------|
| `MNCAATourneySeeds.csv` | 2,626 | Team seeds by season (e.g., "W01" = West region, 1 seed) |
| `MNCAATourneySlots.csv` | 2,586 | Bracket structure (which seeds play in which slots) |
| `MNCAATourneySeedRoundSlots.csv` | 776 | Mapping of seeds to game slots by round |

### Rankings and Ratings

| File | Rows | Description |
|------|------|-------------|
| `MMasseyOrdinals.csv` | **5,565,793** | Computer rankings from 194 different systems |

The Massey Ordinals file is massive because it contains rankings from 194 different computer ranking systems (Sagarin, RPI, KenPom, etc.) for every team on multiple days throughout each season since 2003.

### Team Metadata

| File | Rows | Description |
|------|------|-------------|
| `MTeamConferences.csv` | 13,388 | Team conference membership by season |
| `MTeamCoaches.csv` | 13,533 | Head coaches by team and season |
| `MTeamSpellings.csv` | 1,177 | Alternate team name spellings for matching |
| `MGameCities.csv` | 86,668 | Game locations |
| `MSecondaryTourneyTeams.csv` | 1,836 | Teams in NIT and other tournaments |

### Kaggle Submission Files

| File | Rows | Description |
|------|------|-------------|
| `SampleSubmissionStage1.csv` | 507,107 | Stage 1 submission format |
| `SampleSubmissionStage2.csv` | 131,406 | Stage 2 submission format |
| `SeedBenchmarkStage1.csv` | 507,107 | Baseline predictions using seed differences |

## Key Fields

### Game Results (Compact)

| Field | Description |
|-------|-------------|
| `Season` | Year the season started (e.g., 2024 = 2024-25 season) |
| `DayNum` | Day number relative to DayZero (season start) |
| `WTeamID` | Winning team ID |
| `WScore` | Winning team score |
| `LTeamID` | Losing team ID |
| `LScore` | Losing team score |
| `WLoc` | Game location: H (home), A (away), N (neutral) |
| `NumOT` | Number of overtime periods |

### Game Results (Detailed) - Additional Fields

Box score statistics with W/L prefix for winner/loser:

| Field | Description |
|-------|-------------|
| `FGM` / `FGA` | Field goals made/attempted |
| `FGM3` / `FGA3` | Three-pointers made/attempted |
| `FTM` / `FTA` | Free throws made/attempted |
| `OR` / `DR` | Offensive/defensive rebounds |
| `Ast` | Assists |
| `TO` | Turnovers |
| `Stl` | Steals |
| `Blk` | Blocks |
| `PF` | Personal fouls |

### Tournament Seeds

| Field | Description |
|-------|-------------|
| `Seed` | 3-character code: Region (W/X/Y/Z) + Seed (01-16) + Play-in indicator (a/b) |
| Example | `W01` = West region, 1 seed; `X16b` = Region X, 16 seed, play-in game loser bracket |

### Massey Ordinals

| Field | Description |
|-------|-------------|
| `Season` | Season year |
| `RankingDayNum` | Day number when ranking was published |
| `SystemName` | Ranking system identifier (e.g., "SAG" for Sagarin, "POM" for KenPom) |
| `TeamID` | Team being ranked |
| `OrdinalRank` | Team's rank (1 = best) |

## Notable Ranking Systems (in MMasseyOrdinals)

| Code | System | Description |
|------|--------|-------------|
| `SAG` | Sagarin | Jeff Sagarin's rating system |
| `POM` | KenPom | Ken Pomeroy's efficiency ratings |
| `RPI` | RPI | Rating Percentage Index (NCAA official) |
| `AP` | AP Poll | Associated Press human poll |
| `USA` | USA Today | Coaches poll |
| `MOR` | Massey | Kenneth Massey's own ratings |
| `DOL` | Dolphin | Analytics-based system |
| `SEL` | Sonny Moore | Selection committee-focused |

## ML Competition Format

The Kaggle competition asks participants to predict the probability that the team with the lower TeamID wins each potential tournament matchup. Submissions are evaluated using log loss.

**Stage 1**: Predict historical tournaments (2021-2024) for model validation
**Stage 2**: Predict the current year's tournament (2025)

## Potential Features for ML Models

1. **Seed-based**: Seed differences are strong baseline predictors
2. **Massey Ordinals**: Average or ensemble of computer rankings
3. **Game statistics**: Offensive/defensive efficiency, tempo, four factors
4. **Strength of schedule**: Conference strength, opponent quality
5. **Recent form**: Win streaks, performance in last N games
6. **Coach experience**: Tournament experience, historical performance
7. **Location effects**: Distance traveled, home court advantage

## Usage

```python
import pandas as pd

# Load teams and results
teams = pd.read_csv('datasets/ncaa_basketball/MTeams.csv')
results = pd.read_csv('datasets/ncaa_basketball/MRegularSeasonCompactResults.csv')
tourney = pd.read_csv('datasets/ncaa_basketball/MNCAATourneyCompactResults.csv')
seeds = pd.read_csv('datasets/ncaa_basketball/MNCAATourneySeeds.csv')

# Load rankings (large file - may need chunking)
rankings = pd.read_csv('datasets/ncaa_basketball/MMasseyOrdinals.csv')

# Calculate win percentage by season
season_records = results.groupby(['Season', 'WTeamID']).size().reset_index(name='Wins')
```

## Notes

1. **M vs W prefix**: All tables have separate Men's (M) and Women's (W) versions
2. **Detailed stats start 2003**: Box score data only available from 2003 season onward
3. **Women's data starts 1998**: Men's data goes back to 1985
4. **Play-in games**: Since 2011, 16 seeds can have play-in indicators (a/b)
5. **Day numbering**: Day 0 is season start; tournament typically around days 134-154
6. **Massey file is huge**: 5.5M rows; consider filtering by season or system
7. **Team IDs**: Men's teams are 1000s (1101-1480), Women's are 3000s (3101-3480)
