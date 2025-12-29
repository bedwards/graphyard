# Retrosheet Baseball Data

## Source

**Website**: https://www.retrosheet.org/

**Game Logs**: https://www.retrosheet.org/gamelogs/index.html

**Event Files**: https://www.retrosheet.org/game.htm

**License**: Free for non-commercial use with attribution

## Description

Retrosheet is a volunteer organization dedicated to computerizing play-by-play accounts of Major League Baseball games. They provide two main types of data:

1. **Game Logs**: Summary statistics for every MLB game since 1871
2. **Event Files**: Play-by-play accounts of every event in games since 1910

## Coverage

| Data Type | Years | Games | Description |
|-----------|-------|-------|-------------|
| Game Logs | 1871-2024 | ~230,000 | One row per game with scores, attendance, starting lineups |
| Event Files | 1910-2024 | ~200,000 | Every pitch, play, and substitution |

## File Structure

```
datasets/retrosheet/
├── gamelogs/           # Game-level summaries (224 MB)
│   ├── gl1871.txt      # One file per season
│   ├── gl1872.txt
│   ├── ...
│   └── gl2024.txt      # 159 files total
└── events/             # Play-by-play data (882 MB)
    ├── 1910.EDA        # American League roster
    ├── 1910.EDN        # National League roster
    ├── 1910BOS.EVA     # Boston AL events
    ├── 1910CHN.EVN     # Chicago NL events
    └── ...             # 5,413 files total
```

## Game Log Format

Each game log file is comma-delimited with 161 fields per game.

### Key Fields (Selected)

| Position | Field | Description |
|----------|-------|-------------|
| 1 | Date | YYYYMMDD format |
| 2 | Number | 0 for single game, 1/2 for doubleheader |
| 3 | Day | Day of week (3 chars) |
| 4-5 | Visiting Team/League | Team ID and league |
| 6 | Visiting Game # | Season game number for visiting team |
| 7-8 | Home Team/League | Team ID and league |
| 9 | Home Game # | Season game number for home team |
| 10-11 | Visiting/Home Score | Final scores |
| 12 | Length (outs) | Game length in outs (27 = 9 innings) |
| 13 | Day/Night | D or N |
| 14-15 | Completion Info | For suspended/protested games |
| 16 | Forfeit | If game was forfeited |
| 17 | Park ID | Ballpark identifier |
| 18 | Attendance | Official attendance |
| 19 | Time | Game duration in minutes |
| 20-21 | Line Scores | Inning-by-inning runs |
| 22-49 | Visiting Team Stats | AB, H, 2B, 3B, HR, RBI, SH, SF, HBP, BB, IBB, K, SB, CS, GIDP, CI, LOB |
| 50-77 | Home Team Stats | Same stats for home team |
| 78-81 | Pitching Stats | Visiting/Home pitchers, ER |
| 82-89 | Umpires | HP, 1B, 2B, 3B, LF, RF |
| 90-93 | Managers | Visiting/Home manager names |
| 94-101 | Win/Loss/Save | Pitcher names and IDs |
| 102-105 | GW RBI | Player who drove in winning run |
| 106-161 | Starting Lineups | 9 batters per team with positions |

### Sample (2023 Opening Day)

```
"20230330","0","Thu","MIL","NL",1,"CHN","NL",1,0,4,51,"D",...
```
Milwaukee at Chicago, March 30, 2023 - Cubs won 4-0.

## Event File Format

Event files use Retrosheet's proprietary format with three record types:

### id Record
```
id,NYA202303300
```
Unique game identifier: team + date + game number.

### info Record
```
info,visteam,SFN
info,hometeam,NYA
info,date,2023/03/30
info,starttime,1:05PM
info,attendance,45412
```
Game metadata.

### play Record
```
play,1,0,jlowe001,22,BCCBX,HR/7
```
Format: `play,inning,half,player_id,count,pitches,event`

- **inning**: 1-based inning number
- **half**: 0=visitors, 1=home
- **player_id**: Retrosheet player ID
- **count**: balls-strikes when play occurred
- **pitches**: pitch sequence (B=ball, C=called strike, S=swinging strike, X=in play, etc.)
- **event**: outcome code (HR=home run, K=strikeout, S8=single to center, etc.)

### sub Record
```
sub,smith001,"Smith",1,7,7
```
Player substitution: player_id, name, team, batting order, fielding position.

## Usage

### Python - Loading Game Logs

```python
import pandas as pd
from pathlib import Path

# Define column names (161 fields)
GAMELOG_COLS = [
    'date', 'number', 'day', 'v_team', 'v_league', 'v_game_num',
    'h_team', 'h_league', 'h_game_num', 'v_score', 'h_score',
    'length_outs', 'day_night', 'completion', 'forfeit', 'protest',
    'park_id', 'attendance', 'time_minutes', 'v_line_score', 'h_line_score',
    # ... (full list in retrosheet documentation)
]

# Load a single season
gl2023 = pd.read_csv('datasets/retrosheet/gamelogs/gl2023.txt',
                     header=None, names=GAMELOG_COLS[:21])

# Load all seasons
all_logs = []
for f in Path('datasets/retrosheet/gamelogs').glob('gl*.txt'):
    df = pd.read_csv(f, header=None)
    df['year'] = int(f.stem[2:6])
    all_logs.append(df)

gamelogs = pd.concat(all_logs)
```

### Python - Parsing Event Files

Retrosheet provides tools for parsing event files:
- **BEVENT**: Extracts play-by-play data
- **BGAME**: Extracts game-level info
- **BOX**: Creates box scores

```python
# Using retrosheet-python package (if available)
# Or use subprocess to call Retrosheet tools

import subprocess

# Convert event file to CSV using Chadwick tools
subprocess.run(['cwevent', '-y', '2023', '2023*.EV*'],
               capture_output=True, cwd='datasets/retrosheet/events')
```

Alternatively, use the `retrosheet` Python package:
```python
pip install retrosheet
```

## Tools

### Chadwick Tools

The [Chadwick Bureau](https://github.com/chadwickbureau/chadwick) provides command-line tools for parsing Retrosheet files:

- **cwevent**: Event file to CSV
- **cwgame**: Game-level summaries
- **cwbox**: Box scores
- **cwstats**: Statistical reports

Installation:
```bash
brew install chadwick  # macOS
apt install chadwick   # Ubuntu/Debian
```

### pybaseball Integration

```python
from pybaseball import retrosheet

# Get game logs for a season
logs = retrosheet.season_game_logs(2023)
```

## Notes

1. **Player IDs**: Retrosheet uses unique 8-character IDs (lastname + number)
2. **Team IDs**: 3-character codes (NYA=NY Yankees, NYN=NY Mets)
3. **Park IDs**: 5-character stadium codes
4. **Event codes**: Complex notation - see [Retrosheet Event Files](https://www.retrosheet.org/eventfile.htm)
5. **Missing data**: Some fields may be blank for older games
6. **Updates**: New data released throughout the season

## References

- [Retrosheet Documentation](https://www.retrosheet.org/boxfile.htm)
- [Game Log Fields](https://www.retrosheet.org/gamelogs/glfields.txt)
- [Event File Format](https://www.retrosheet.org/eventfile.htm)
- [Chadwick Bureau Tools](https://github.com/chadwickbureau/chadwick)
- [Analyzing Baseball Data with R](https://beanumber.github.io/abdwr3e/)
