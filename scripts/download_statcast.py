#!/usr/bin/env python3
"""
Download Statcast pitch-by-pitch data from Baseball Savant.

Uses pybaseball to handle the 30,000 row limit per query automatically.
Full season downloads take ~30-60 minutes due to rate limiting.

Usage:
    python scripts/download_statcast.py              # Downloads 2024 season
    python scripts/download_statcast.py 2023         # Downloads 2023 season
    python scripts/download_statcast.py 2015 2024    # Downloads 2015-2024
"""

import sys
from pathlib import Path

import pybaseball

# Enable caching to avoid re-downloading
pybaseball.cache.enable()

OUTPUT_DIR = Path("datasets/statcast")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Season date ranges (approximate - adjust for actual opening/closing days)
SEASON_DATES = {
    2015: ("2015-04-05", "2015-11-01"),
    2016: ("2016-04-03", "2016-11-02"),
    2017: ("2017-04-02", "2017-11-01"),
    2018: ("2018-03-29", "2018-10-28"),
    2019: ("2019-03-28", "2019-10-30"),
    2020: ("2020-07-23", "2020-10-27"),  # COVID shortened season
    2021: ("2021-04-01", "2021-11-02"),
    2022: ("2022-04-07", "2022-11-05"),
    2023: ("2023-03-30", "2023-11-01"),
    2024: ("2024-03-20", "2024-11-02"),
}


def download_season(year: int) -> None:
    """Download Statcast data for a single season."""
    if year not in SEASON_DATES:
        print(f"Unknown season: {year}. Valid years: {sorted(SEASON_DATES.keys())}")
        return

    start_dt, end_dt = SEASON_DATES[year]
    output_file = OUTPUT_DIR / f"statcast_{year}.csv"

    if output_file.exists():
        print(f"Season {year} already downloaded: {output_file}")
        return

    print(f"Downloading {year} season ({start_dt} to {end_dt})...")
    print("This may take 30-60 minutes due to Baseball Savant rate limits.")

    try:
        data = pybaseball.statcast(start_dt, end_dt)
        data.to_csv(output_file, index=False)
        print(f"Saved {len(data):,} pitches to {output_file}")
        print(f"File size: {output_file.stat().st_size / 1024 / 1024:.1f} MB")
    except Exception as e:
        print(f"Error downloading {year}: {e}")


def main():
    if len(sys.argv) == 1:
        # Default: download current season
        download_season(2024)
    elif len(sys.argv) == 2:
        # Single year
        download_season(int(sys.argv[1]))
    elif len(sys.argv) == 3:
        # Range of years
        start_year, end_year = int(sys.argv[1]), int(sys.argv[2])
        for year in range(start_year, end_year + 1):
            download_season(year)
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
