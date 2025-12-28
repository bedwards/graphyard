#!/usr/bin/env python3
"""
WDI Data Utilities

Unified tool for cleaning and loading World Development Indicators data.

Cleaning stages:
1. fix-encoding: Fix UTF-8 encoding issues
2. normalize: Normalize special characters
3. parse-csv: Parse with Python csv, fix column names
4. to-narrow: Convert wide format to narrow
5. split-entities: Split by entity type

Loading stages:
6. load-db: Load into PostgreSQL database
7. load-pandas/polars/torch: Test with various libraries

Output: datasets/WDI_CSV_clean/
Database: graphyard@localhost:5432
"""

import argparse
import csv
import os
import sys
from pathlib import Path
from typing import Optional

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
INPUT_DIR = PROJECT_ROOT / "datasets" / "WDI_CSV"
OUTPUT_DIR = PROJECT_ROOT / "datasets" / "WDI_CSV_clean"

# Files to process
WDI_FILES = [
    "WDICSV.csv",
    "WDISeries.csv",
    "WDICountry.csv",
    "WDIcountry-series.csv",
    "WDIfootnote.csv",
    "WDIseries-time.csv",
]

# Database connection
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "graphyard",
    "user": "postgres",
    "password": "postgres",
}

# Character replacements for normalization
CHAR_REPLACEMENTS = {
    "\u00a0": " ",      # Non-breaking space -> space
    "\u201c": '"',      # Left double quote -> ASCII quote
    "\u201d": '"',      # Right double quote -> ASCII quote
    "\u2018": "'",      # Left single quote -> ASCII apostrophe
    "\u2019": "'",      # Right single quote -> ASCII apostrophe
    "\u2013": "-",      # En dash -> hyphen
    "\u2014": "-",      # Em dash -> hyphen
    "\u00ac": "",       # Not sign -> remove
    "\u00f7": "/",      # Division sign -> slash
}

# Entity classification for countries vs aggregates
ENTITY_TYPES = {
    "world": ["WLD"],
    "region_geo": ["EAS", "ECS", "LCN", "MEA", "NAC", "SAS", "SSF"],
    "region_geo_sub": ["AFE", "AFW", "CEB"],
    "region_geo_exhi": ["EAP", "ECA", "LAC", "MNA", "SSA"],
    "income": ["HIC", "UMC", "LMC", "LIC", "MIC", "LMY"],
    "lending": ["IBD", "IDA", "IDB", "IDX", "IBT"],
    "region_lending": ["TEA", "TEC", "TLA", "TMN", "TSA", "TSS"],
    "demographic": ["PRE", "EAR", "LTE", "PST"],
    "small_states": ["SST", "CSS", "PSS", "OSS"],
    "political": ["ARB", "EMU", "EUU", "OED"],
    "dev_status": ["FCS", "HPC", "LDC"],
}

# Build reverse lookup
CODE_TO_TYPE = {}
for entity_type, codes in ENTITY_TYPES.items():
    for code in codes:
        CODE_TO_TYPE[code] = entity_type

# Entity type to database table mapping
ENTITY_TABLE_MAP = {
    "country": "country_data",
    "world": "world_data",
    "region_geo": "region_geo_data",
    "region_geo_sub": "region_geo_data",
    "region_geo_exhi": "region_geo_data",
    "income": "income_data",
    "lending": "lending_data",
    "region_lending": "lending_data",
    "demographic": "other_aggregate_data",
    "small_states": "other_aggregate_data",
    "political": "other_aggregate_data",
    "dev_status": "other_aggregate_data",
    "unknown_aggregate": "other_aggregate_data",
    "unknown": "other_aggregate_data",
}


def classify_entity(country_code: str, region: str) -> str:
    """Classify an entity as 'country' or a specific aggregate type."""
    if country_code in CODE_TO_TYPE:
        return CODE_TO_TYPE[country_code]
    if region and region.strip():
        return "country"
    return "unknown_aggregate"


def ensure_output_dir():
    """Create output directory if it doesn't exist."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_country_metadata() -> dict:
    """Load country metadata to get Region field for classification."""
    country_path = INPUT_DIR / "WDICountry.csv"
    metadata = {}
    with open(country_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = row["Country Code"]
            region = row.get("Region", "").strip()
            metadata[code] = {
                "region": region,
                "entity_type": classify_entity(code, region),
            }
    return metadata


# =============================================================================
# CLEANING FUNCTIONS
# =============================================================================

def fix_encoding(input_path: Path, output_path: Path) -> dict:
    """Fix encoding issues at byte level."""
    stats = {"bytes_read": 0, "encoding_detected": None, "errors_fixed": 0}

    with open(input_path, "rb") as f:
        raw_bytes = f.read()
    stats["bytes_read"] = len(raw_bytes)

    encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "iso-8859-1"]
    decoded = None

    for encoding in encodings:
        try:
            decoded = raw_bytes.decode(encoding)
            stats["encoding_detected"] = encoding
            break
        except UnicodeDecodeError:
            continue

    if decoded is None:
        decoded = raw_bytes.decode("utf-8", errors="replace")
        stats["encoding_detected"] = "utf-8 (with replacements)"
        stats["errors_fixed"] = decoded.count("\ufffd")

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        f.write(decoded)

    return stats


def normalize_text(text: str, stats: dict) -> str:
    """Normalize special characters in a text string."""
    for old_char, new_char in CHAR_REPLACEMENTS.items():
        count = text.count(old_char)
        if count > 0:
            stats["replacement_counts"][repr(old_char)] = stats["replacement_counts"].get(repr(old_char), 0) + count
            stats["chars_replaced"] += count
            text = text.replace(old_char, new_char)
    return text


def normalize_characters(input_path: Path, output_path: Path) -> dict:
    """Normalize special characters, preserving CSV structure."""
    stats = {"chars_replaced": 0, "replacement_counts": {}}

    with open(input_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = [[normalize_text(cell, stats) for cell in row] for row in reader]

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    return stats


def parse_csv(input_path: Path, output_path: Path) -> dict:
    """Parse CSV, validate structure, fix column names."""
    stats = {"rows_read": 0, "rows_written": 0, "columns_renamed": []}

    with open(input_path, "r", encoding="utf-8") as f:
        rows = list(csv.reader(f))

    if not rows:
        return stats

    stats["rows_read"] = len(rows)
    header = rows[0]

    # Rename Series Code -> Indicator Code
    new_header = []
    for col in header:
        if col == "Series Code":
            new_header.append("Indicator Code")
            stats["columns_renamed"].append(("Series Code", "Indicator Code"))
        else:
            new_header.append(col)

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(new_header)
        for row in rows[1:]:
            writer.writerow(row)
            stats["rows_written"] += 1

    return stats


def wide_to_narrow(input_path: Path, output_path: Path) -> dict:
    """Transform wide format (year columns) to narrow format (year rows)."""
    stats = {"input_rows": 0, "output_rows": 0, "year_columns": 0}

    with open(input_path, "r", encoding="utf-8") as f:
        rows = list(csv.reader(f))

    if not rows:
        return stats

    header = rows[0]
    stats["input_rows"] = len(rows) - 1

    # Identify year columns
    id_cols = []
    year_cols = []
    for col in header:
        if col.isdigit() and 1900 <= int(col) <= 2100:
            year_cols.append(col)
        else:
            id_cols.append(col)

    stats["year_columns"] = len(year_cols)

    if not year_cols:
        with open(output_path, "w", encoding="utf-8", newline="") as f:
            csv.writer(f).writerows(rows)
        stats["output_rows"] = stats["input_rows"]
        return stats

    new_header = id_cols + ["Year", "Value"]

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(new_header)

        for row in rows[1:]:
            id_values = [row[header.index(col)] for col in id_cols]
            for year_col in year_cols:
                year_idx = header.index(year_col)
                value = row[year_idx] if year_idx < len(row) else ""
                if value.strip():
                    writer.writerow(id_values + [year_col, value])
                    stats["output_rows"] += 1

    return stats


def split_by_entity_type(input_path: Path, output_dir: Path) -> dict:
    """Split data file by entity type."""
    stats = {"input_rows": 0, "output_files": {}, "entity_counts": {}}

    metadata = load_country_metadata()

    with open(input_path, "r", encoding="utf-8") as f:
        rows = list(csv.reader(f))

    if not rows:
        return stats

    header = rows[0]
    stats["input_rows"] = len(rows) - 1

    # Find country code column
    code_col_idx = None
    for i, col in enumerate(header):
        if col in ("Country Code", "CountryCode"):
            code_col_idx = i
            break

    if code_col_idx is None:
        stats["error"] = "No Country Code column found"
        return stats

    # Group by entity type
    entity_rows = {}
    for row in rows[1:]:
        if len(row) <= code_col_idx:
            continue
        code = row[code_col_idx]
        entity_type = metadata.get(code, {}).get("entity_type", "unknown")
        if entity_type not in entity_rows:
            entity_rows[entity_type] = []
        entity_rows[entity_type].append(row)

    # Write separate files
    base_name = input_path.stem
    for entity_type, type_rows in entity_rows.items():
        output_path = output_dir / f"{base_name}_{entity_type}.csv"
        with open(output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(type_rows)
        stats["output_files"][entity_type] = str(output_path)
        stats["entity_counts"][entity_type] = len(type_rows)

    return stats


# =============================================================================
# DATABASE LOADING FUNCTIONS
# =============================================================================

def get_db_connection():
    """Get database connection."""
    try:
        import psycopg2
        return psycopg2.connect(**DB_CONFIG)
    except ImportError:
        print("ERROR: psycopg2 not installed. Run: pip install psycopg2-binary")
        sys.exit(1)


def load_db_indicators(conn, verbose=True) -> int:
    """Load indicator metadata into database."""
    from psycopg2.extras import execute_values

    clean_path = OUTPUT_DIR / "WDISeries_parsed.csv"
    orig_path = INPUT_DIR / "WDISeries.csv"
    path = clean_path if clean_path.exists() else orig_path

    if verbose:
        print(f"  Loading indicators from {path.name}...")

    with open(path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # Load indicator names from WDICSV (source of truth)
    wdi_path = INPUT_DIR / "WDICSV.csv"
    indicator_names = {}
    with open(wdi_path, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            code = row["Indicator Code"]
            if code not in indicator_names:
                indicator_names[code] = row["Indicator Name"]

    data = []
    for row in rows:
        code = row.get("Indicator Code") or row.get("Series Code")
        name = indicator_names.get(code, row.get("Indicator Name", ""))
        data.append((
            code, name,
            row.get("Topic", ""),
            row.get("Short definition", ""),
            row.get("Long definition", ""),
            row.get("Unit of measure", ""),
            row.get("Periodicity", ""),
            row.get("Aggregation method", ""),
            row.get("Source", ""),
            row.get("License Type", ""),
        ))

    with conn.cursor() as cur:
        execute_values(cur, """
            INSERT INTO indicators (
                indicator_code, indicator_name, topic, short_definition,
                long_definition, unit_of_measure, periodicity,
                aggregation_method, source, license_type
            ) VALUES %s
            ON CONFLICT (indicator_code) DO UPDATE SET
                indicator_name = EXCLUDED.indicator_name,
                topic = EXCLUDED.topic
        """, data)
        conn.commit()

    if verbose:
        print(f"    Loaded {len(data)} indicators")
    return len(data)


def load_db_entities(conn, verbose=True) -> int:
    """Load entity metadata into database."""
    from psycopg2.extras import execute_values

    path = INPUT_DIR / "WDICountry.csv"

    if verbose:
        print(f"  Loading entities from {path.name}...")

    with open(path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    data = []
    for row in rows:
        code = row["Country Code"]
        region = row.get("Region", "").strip()
        entity_type = classify_entity(code, region)
        data.append((
            code,
            row.get("Short Name", ""),
            entity_type,
            row.get("Long Name", ""),
            row.get("Currency Unit", ""),
            region if region else None,
            row.get("Income Group", "").strip() or None,
            row.get("Special Notes", ""),
        ))

    with conn.cursor() as cur:
        execute_values(cur, """
            INSERT INTO entities (
                entity_code, entity_name, entity_type, long_name,
                currency_unit, region, income_group, special_notes
            ) VALUES %s
            ON CONFLICT (entity_code) DO UPDATE SET
                entity_name = EXCLUDED.entity_name,
                entity_type = EXCLUDED.entity_type
        """, data)
        conn.commit()

    if verbose:
        print(f"    Loaded {len(data)} entities")
    return len(data)


def load_db_observations(conn, verbose=True) -> int:
    """Load observation data into database."""
    from psycopg2.extras import execute_values

    narrow_path = OUTPUT_DIR / "WDICSV_narrow.csv"
    if not narrow_path.exists():
        print("ERROR: Run --to-narrow first to create narrow format file")
        return 0

    if verbose:
        print(f"  Loading observations from {narrow_path.name}...")

    metadata = load_country_metadata()

    with open(narrow_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if verbose:
        print(f"    Read {len(rows)} rows, classifying...")

    # Group by target table
    table_data = {
        "country_data": [],
        "world_data": [],
        "region_geo_data": [],
        "income_data": [],
        "lending_data": [],
        "other_aggregate_data": [],
    }

    for row in rows:
        code = row["Country Code"]
        indicator = row["Indicator Code"]
        year = int(row["Year"])
        try:
            value = float(row["Value"])
        except (ValueError, TypeError):
            continue

        entity_type = metadata.get(code, {}).get("entity_type", "unknown")
        table = ENTITY_TABLE_MAP.get(entity_type, "other_aggregate_data")

        if table == "world_data":
            table_data[table].append((indicator, year, value))
        elif table == "other_aggregate_data":
            table_data[table].append((code, indicator, year, value, entity_type))
        else:
            table_data[table].append((code, indicator, year, value))

    total = 0
    with conn.cursor() as cur:
        for table, data in table_data.items():
            if not data:
                continue
            if verbose:
                print(f"    Inserting {len(data)} {table} rows...")

            if table == "world_data":
                execute_values(cur, """
                    INSERT INTO world_data (indicator_code, year, value) VALUES %s
                    ON CONFLICT (indicator_code, year) DO UPDATE SET value = EXCLUDED.value
                """, data, page_size=10000)
            elif table == "other_aggregate_data":
                execute_values(cur, """
                    INSERT INTO other_aggregate_data (entity_code, indicator_code, year, value, aggregate_type) VALUES %s
                    ON CONFLICT (entity_code, indicator_code, year) DO UPDATE SET value = EXCLUDED.value
                """, data, page_size=10000)
            else:
                execute_values(cur, f"""
                    INSERT INTO {table} (entity_code, indicator_code, year, value) VALUES %s
                    ON CONFLICT (entity_code, indicator_code, year) DO UPDATE SET value = EXCLUDED.value
                """, data, page_size=10000)

            total += len(data)

        conn.commit()

    if verbose:
        print(f"    Total: {total} observations")
    return total


# =============================================================================
# HIGH-LEVEL LOADERS
# =============================================================================

def load_pandas(input_path: Path) -> dict:
    """Load CSV with pandas and return stats."""
    try:
        import pandas as pd
    except ImportError:
        return {"error": "pandas not installed"}

    df = pd.read_csv(input_path)
    return {
        "rows": len(df),
        "columns": list(df.columns),
        "memory_mb": df.memory_usage(deep=True).sum() / 1024 / 1024,
    }


def load_polars(input_path: Path) -> dict:
    """Load CSV with polars and return stats."""
    try:
        import polars as pl
    except ImportError:
        return {"error": "polars not installed"}

    df = pl.read_csv(input_path)
    return {
        "rows": len(df),
        "columns": df.columns,
        "memory_mb": df.estimated_size() / 1024 / 1024,
    }


def load_torch(input_path: Path) -> dict:
    """Load CSV into PyTorch tensor."""
    try:
        import torch
    except ImportError:
        return {"error": "torch not installed"}

    with open(input_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if not rows or "Value" not in rows[0]:
        return {"info": "Not narrow format"}

    values = []
    for row in rows:
        try:
            values.append(float(row["Value"]))
        except (ValueError, TypeError):
            continue

    if values:
        tensor = torch.tensor(values, dtype=torch.float32)
        return {
            "shape": list(tensor.shape),
            "min": float(tensor.min()),
            "max": float(tensor.max()),
            "mean": float(tensor.mean()),
        }
    return {"info": "No numeric values"}


# =============================================================================
# PIPELINE
# =============================================================================

def process_file(filename: str, stages: list[str], verbose: bool = True) -> dict:
    """Process a single file through specified stages."""
    results = {"filename": filename, "stages": {}}

    input_path = INPUT_DIR / filename
    if not input_path.exists():
        results["error"] = f"File not found: {input_path}"
        return results

    ensure_output_dir()

    base_name = Path(filename).stem
    ext = Path(filename).suffix
    current_input = input_path

    # Stage 1: Fix encoding
    if "encoding" in stages or "all" in stages:
        output_path = OUTPUT_DIR / f"{base_name}_utf8{ext}"
        if verbose:
            print(f"  [1] Fixing encoding: {filename}")
        results["stages"]["encoding"] = fix_encoding(current_input, output_path)
        current_input = output_path

    # Stage 2: Normalize characters
    if "normalize" in stages or "all" in stages:
        output_path = OUTPUT_DIR / f"{base_name}_normalized{ext}"
        if verbose:
            print(f"  [2] Normalizing characters: {filename}")
        results["stages"]["normalize"] = normalize_characters(current_input, output_path)
        current_input = output_path

    # Stage 3: Parse CSV
    if "csv" in stages or "all" in stages:
        output_path = OUTPUT_DIR / f"{base_name}_parsed{ext}"
        if verbose:
            print(f"  [3] Parsing CSV: {filename}")
        results["stages"]["csv"] = parse_csv(current_input, output_path)
        current_input = output_path

    # Stage 4: Wide to Narrow
    narrow_path = None
    if ("narrow" in stages or "all" in stages) and "WDICSV" in filename:
        output_path = OUTPUT_DIR / f"{base_name}_narrow{ext}"
        if verbose:
            print(f"  [4] Converting wide to narrow: {filename}")
        results["stages"]["narrow"] = wide_to_narrow(current_input, output_path)
        narrow_path = output_path
        current_input = output_path

    # Stage 4b: Split by entity type
    if ("split" in stages or "all" in stages) and "WDICSV" in filename:
        if verbose:
            print(f"  [4b] Splitting by entity type: {filename}")
        results["stages"]["split"] = split_by_entity_type(current_input, OUTPUT_DIR)

    # Stage 5a: Load with pandas
    if "pandas" in stages:
        if verbose:
            print(f"  [5a] Loading with pandas: {filename}")
        results["stages"]["pandas"] = load_pandas(current_input)

    # Stage 5b: Load with polars
    if "polars" in stages:
        if verbose:
            print(f"  [5b] Loading with polars: {filename}")
        results["stages"]["polars"] = load_polars(current_input)

    # Stage 5c: Load with torch
    if "torch" in stages:
        if verbose:
            print(f"  [5c] Loading with torch: {filename}")
        results["stages"]["torch"] = load_torch(narrow_path or current_input)

    # Final clean version
    if "all" in stages:
        final_path = OUTPUT_DIR / filename
        if verbose:
            print(f"  [*] Writing final: {filename}")
        with open(current_input, "r", encoding="utf-8") as src:
            with open(final_path, "w", encoding="utf-8", newline="") as dst:
                dst.write(src.read())

    return results


def main():
    parser = argparse.ArgumentParser(
        description="WDI Data Utilities - Clean and load World Development Indicators",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s clean --all                    # Full cleaning pipeline
  %(prog)s clean --to-narrow              # Just convert to narrow format
  %(prog)s clean -f WDICSV.csv --all      # Clean single file
  %(prog)s load --all                     # Load all into database
  %(prog)s load --indicators --entities   # Load just metadata
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command")

    # Clean subcommand
    clean_parser = subparsers.add_parser("clean", help="Clean WDI data files")
    clean_parser.add_argument("--all", action="store_true", help="Run all cleaning stages")
    clean_parser.add_argument("--fix-encoding", action="store_true", help="Fix UTF-8 encoding")
    clean_parser.add_argument("--normalize", action="store_true", help="Normalize special characters")
    clean_parser.add_argument("--parse-csv", action="store_true", help="Parse with Python csv")
    clean_parser.add_argument("--to-narrow", action="store_true", help="Convert wide to narrow format")
    clean_parser.add_argument("--split-entities", action="store_true", help="Split by entity type")
    clean_parser.add_argument("--load-pandas", action="store_true", help="Test with pandas")
    clean_parser.add_argument("--load-polars", action="store_true", help="Test with polars")
    clean_parser.add_argument("--load-torch", action="store_true", help="Test with PyTorch")
    clean_parser.add_argument("-f", "--file", type=str, help="Process single file")
    clean_parser.add_argument("-q", "--quiet", action="store_true", help="Suppress output")

    # Load subcommand
    load_parser = subparsers.add_parser("load", help="Load data into PostgreSQL")
    load_parser.add_argument("--all", action="store_true", help="Load all data")
    load_parser.add_argument("--indicators", action="store_true", help="Load indicator metadata")
    load_parser.add_argument("--entities", action="store_true", help="Load entity metadata")
    load_parser.add_argument("--observations", action="store_true", help="Load observation data")
    load_parser.add_argument("-q", "--quiet", action="store_true", help="Suppress output")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    verbose = not args.quiet

    if args.command == "clean":
        stages = []
        if args.all:
            stages = ["all"]
        else:
            if args.fix_encoding:
                stages.append("encoding")
            if args.normalize:
                stages.append("normalize")
            if args.parse_csv:
                stages.append("csv")
            if args.to_narrow:
                stages.append("narrow")
            if args.split_entities:
                stages.append("split")
            if args.load_pandas:
                stages.append("pandas")
            if args.load_polars:
                stages.append("polars")
            if args.load_torch:
                stages.append("torch")

        if not stages:
            clean_parser.print_help()
            sys.exit(1)

        files = [args.file] if args.file else WDI_FILES

        if verbose:
            print("WDI Data Utilities - Clean")
            print(f"Input:  {INPUT_DIR}")
            print(f"Output: {OUTPUT_DIR}")
            print(f"Stages: {stages}")
            print()

        for filename in files:
            if verbose:
                print(f"Processing: {filename}")
            results = process_file(filename, stages, verbose)
            if verbose:
                for stage, stats in results.get("stages", {}).items():
                    if "error" in stats:
                        print(f"  {stage}: ERROR - {stats['error']}")
                    else:
                        key_stats = {k: v for k, v in stats.items() if k not in ["columns", "dtypes", "output_files", "replacement_counts"]}
                        print(f"  {stage}: {key_stats}")
                print()

    elif args.command == "load":
        if not any([args.all, args.indicators, args.entities, args.observations]):
            load_parser.print_help()
            sys.exit(1)

        if verbose:
            print("WDI Data Utilities - Load")
            print(f"Database: {DB_CONFIG['database']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}")
            print()

        conn = get_db_connection()
        try:
            if args.indicators or args.all:
                load_db_indicators(conn, verbose)
            if args.entities or args.all:
                load_db_entities(conn, verbose)
            if args.observations or args.all:
                load_db_observations(conn, verbose)

            if verbose:
                print("\nDone!")
        finally:
            conn.close()


if __name__ == "__main__":
    main()
