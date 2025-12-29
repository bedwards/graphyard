#!/usr/bin/env python3
"""
Download Our World in Data (OWID) charts and metadata.

This script:
1. Queries the OWID Datasette API to get all published chart slugs
2. Downloads CSV data and metadata for each chart
3. Saves to datasets/owid/

Rate limited to be respectful of OWID servers.
"""

import json
import os
import time
from pathlib import Path
from typing import Generator

import requests

# Configuration
DATASETTE_URL = "https://datasette-public.owid.io/owid"
GRAPHER_URL = "https://ourworldindata.org/grapher"
OUTPUT_DIR = Path("datasets/owid")
CHARTS_DIR = OUTPUT_DIR / "charts"
METADATA_DIR = OUTPUT_DIR / "metadata"
RATE_LIMIT_SECONDS = 0.5  # 2 requests per second
PAGE_SIZE = 1000  # Datasette page size

# Create output directories
CHARTS_DIR.mkdir(parents=True, exist_ok=True)
METADATA_DIR.mkdir(parents=True, exist_ok=True)


def get_published_chart_slugs() -> Generator[dict, None, None]:
    """Fetch all published chart slugs from Datasette API."""
    offset = 0

    while True:
        url = f"{DATASETTE_URL}/charts.json"
        params = {
            "_size": PAGE_SIZE,
            "_shape": "objects",
            "isPublished": 1,
            "_offset": offset,
        }

        print(f"Fetching charts from offset {offset}...")
        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        rows = data.get("rows", [])

        if not rows:
            break

        for row in rows:
            yield {
                "id": row["id"],
                "slug": row["slug"],
                "title": row["title"],
                "type": row["type"],
            }

        # Check if there are more pages
        if len(rows) < PAGE_SIZE:
            break

        offset += PAGE_SIZE
        time.sleep(RATE_LIMIT_SECONDS)


def download_chart_csv(slug: str) -> bool:
    """Download CSV data for a chart. Returns True if successful."""
    csv_path = CHARTS_DIR / f"{slug}.csv"

    # Skip if already downloaded
    if csv_path.exists() and csv_path.stat().st_size > 0:
        return True

    url = f"{GRAPHER_URL}/{slug}.csv"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        csv_path.write_text(response.text)
        return True

    except requests.RequestException as e:
        print(f"  Error downloading {slug}: {e}")
        return False


def download_chart_metadata(slug: str) -> bool:
    """Download metadata for a chart. Returns True if successful."""
    meta_path = METADATA_DIR / f"{slug}.json"

    # Skip if already downloaded
    if meta_path.exists() and meta_path.stat().st_size > 0:
        return True

    url = f"{GRAPHER_URL}/{slug}.metadata.json"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        meta_path.write_text(response.text)
        return True

    except requests.RequestException as e:
        print(f"  Error downloading metadata for {slug}: {e}")
        return False


def save_chart_index(charts: list[dict]):
    """Save index of all charts."""
    index_path = OUTPUT_DIR / "chart_index.json"
    with open(index_path, "w") as f:
        json.dump(charts, f, indent=2)
    print(f"Saved chart index with {len(charts)} charts")


def main():
    print("=" * 60)
    print("Our World in Data Downloader")
    print("=" * 60)

    # Phase 1: Get all chart slugs
    print("\nPhase 1: Fetching chart index from Datasette...")
    charts = list(get_published_chart_slugs())
    print(f"Found {len(charts)} published charts")

    # Save chart index
    save_chart_index(charts)

    # Phase 2: Download CSVs
    print(f"\nPhase 2: Downloading chart CSVs to {CHARTS_DIR}...")
    csv_success = 0
    csv_fail = 0

    for i, chart in enumerate(charts, 1):
        slug = chart["slug"]

        if i % 100 == 0 or i == 1:
            print(f"Progress: {i}/{len(charts)} ({100*i/len(charts):.1f}%)")

        if download_chart_csv(slug):
            csv_success += 1
        else:
            csv_fail += 1

        time.sleep(RATE_LIMIT_SECONDS)

    print(f"CSV download complete: {csv_success} success, {csv_fail} failed")

    # Phase 3: Download metadata
    print(f"\nPhase 3: Downloading chart metadata to {METADATA_DIR}...")
    meta_success = 0
    meta_fail = 0

    for i, chart in enumerate(charts, 1):
        slug = chart["slug"]

        if i % 100 == 0 or i == 1:
            print(f"Progress: {i}/{len(charts)} ({100*i/len(charts):.1f}%)")

        if download_chart_metadata(slug):
            meta_success += 1
        else:
            meta_fail += 1

        time.sleep(RATE_LIMIT_SECONDS)

    print(f"Metadata download complete: {meta_success} success, {meta_fail} failed")

    # Summary
    print("\n" + "=" * 60)
    print("Download Complete")
    print("=" * 60)
    print(f"Charts: {len(charts)}")
    print(f"CSVs downloaded: {csv_success}")
    print(f"Metadata downloaded: {meta_success}")
    print(f"Output directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
