# Lahman Baseball Database

## Source

**Download URL**: https://raw.githubusercontent.com/cdalzell/Lahman/master/source-data/baseballdatabank-master.zip

**Original Source**: https://www.seanlahman.com/baseball-archive/statistics/

**Publisher**: Sean Lahman, maintained by the Lahman community

**License**: Creative Commons Attribution-ShareAlike 3.0

## Description

The Lahman Baseball Database is the most comprehensive open-source baseball database in existence. It contains complete batting, pitching, and fielding statistics for every player who has appeared in a Major League game since 1871. The database is updated annually and is the foundation for most sabermetric research.

## Database Statistics

| Metric | Count |
|--------|-------|
| Players | 19,878 |
| Teams | 2,925 team-seasons |
| Batting records | 107,429 player-seasons |
| Pitching records | 47,628 player-seasons |
| Salary records | 26,428 |
| Managers | 3,536 stints |
| Franchises | 120 |
| Years covered | 1871-2019 |

## Tables

### Core Dimension Tables

| Table | Description |
|-------|-------------|
| `people` | Biographical information for all players, managers, umpires |
| `teams` | Team statistics by year (wins, losses, runs, etc.) |
| `teams_franchises` | Franchise metadata (names, active status) |
| `parks` | Stadium information |
| `schools` | College/university metadata |

### Performance Fact Tables

| Table | Description |
|-------|-------------|
| `batting` | Regular season batting statistics by player-year-stint |
| `pitching` | Regular season pitching statistics by player-year-stint |
| `fielding` | Regular season fielding statistics by player-year-stint-position |
| `appearances` | Games by position for each player |

### Postseason Tables

| Table | Description |
|-------|-------------|
| `batting_post` | Postseason batting statistics |
| `pitching_post` | Postseason pitching statistics |
| `series_post` | Series results (LCS, World Series, etc.) |

### Awards and Recognition

| Table | Description |
|-------|-------------|
| `awards_players` | Player awards (MVP, Cy Young, etc.) |
| `hall_of_fame` | Hall of Fame voting history |
| `allstar_full` | All-Star game appearances |

### Other Tables

| Table | Description |
|-------|-------------|
| `salaries` | Player salaries (1985-2016) |
| `managers` | Managerial records by team-year |
| `college_playing` | College attendance records |
| `home_games` | Home game attendance by park |

## Key Fields

### People Table

| Field | Description |
|-------|-------------|
| `player_id` | Unique player identifier (primary key) |
| `name_first`, `name_last` | Player name |
| `birth_year`, `birth_month`, `birth_day` | Birth date |
| `debut`, `final_game` | First and last MLB game dates |
| `bats`, `throws` | Batting/throwing hand (L/R/B) |
| `height`, `weight` | Physical measurements |

### Batting Table

| Field | Description |
|-------|-------------|
| `player_id` | Player identifier |
| `year_id` | Season year |
| `stint` | Order if player played for multiple teams that year |
| `team_id` | Team identifier |
| `at_bats`, `hits`, `doubles`, `triples`, `home_runs` | Offensive stats |
| `rbi`, `stolen_bases`, `walks`, `strikeouts` | Additional offensive stats |

### Pitching Table

| Field | Description |
|-------|-------------|
| `player_id` | Player identifier |
| `year_id` | Season year |
| `wins`, `losses` | Win-loss record |
| `games`, `games_started`, `complete_games` | Usage stats |
| `outs_pitched` | Outs recorded (innings × 3) |
| `strikeouts`, `walks`, `hits` | Per-game stats |
| `earned_runs`, `era` | Run prevention |

## Baseball Eras

The database spans multiple distinct eras of baseball history:

| Era | Years | Characteristics |
|-----|-------|-----------------|
| Dead Ball | 1901-1919 | Low scoring, contact hitting, complete games |
| Live Ball | 1920-1941 | Babe Ruth, power hitting emerges |
| WWII | 1942-1945 | Depleted rosters, quality decline |
| Integration | 1946-1960 | Jackie Robinson, expansion of talent pool |
| Expansion I | 1961-1968 | More teams, "Year of the Pitcher" (1968) |
| Free Agency | 1969-1992 | Labor changes, rising salaries |
| Steroid Era | 1993-2005 | Power explosion, broken records |
| Modern | 2006-present | Analytics revolution, strikeout surge |

## Usage

```bash
# Download and load (using project tools)
python scripts/load_lahman.py

# Verify data
python -c "
from charts.baseball.data import get_loader
loader = get_loader()
print(loader.career_home_run_leaders(10))
"
```

## Sample Queries

```sql
-- Career home run leaders
SELECT p.name_first || ' ' || p.name_last as player,
       SUM(b.home_runs) as hr
FROM lahman.batting b
JOIN lahman.people p ON b.player_id = p.player_id
GROUP BY p.player_id, p.name_first, p.name_last
ORDER BY hr DESC
LIMIT 10;

-- League batting average by year
SELECT year_id,
       SUM(hits)::float / NULLIF(SUM(at_bats), 0) as avg
FROM lahman.batting
WHERE year_id >= 1901
GROUP BY year_id
ORDER BY year_id;
```

## Data Loader API

```python
from charts.baseball.data import get_loader

loader = get_loader()

# Career leaders
loader.career_home_run_leaders(limit=25)
loader.career_batting_average_leaders(min_at_bats=3000, limit=25)
loader.career_wins_leaders(limit=25)
loader.career_strikeout_leaders(limit=25)

# Era analysis
loader.league_batting_by_era()
loader.yearly_league_batting(start_year=1901, end_year=2019)
loader.yearly_league_pitching(start_year=1901, end_year=2019)

# Historical trends
loader.home_run_evolution()
loader.strikeout_evolution()
loader.complete_game_decline()

# Salary analysis
loader.salary_growth(start_year=1985, end_year=2016)
loader.top_salaries_by_year(year=2016, limit=10)

# Team analysis
loader.franchise_wins_all_time(limit=30)
loader.dynasty_teams(min_wins=100)

# Manager analysis
loader.manager_career_wins(limit=25)
```

## Notes

1. **Primary keys**: Most tables use composite keys (player_id + year_id + stint)
2. **Stint field**: Handles players traded mid-season (stint 1, 2, etc.)
3. **Null values**: Many older records have missing data for newer stats
4. **Salary data**: Only available from 1985-2016
5. **Postseason tables**: May have loading issues; core tables are complete
