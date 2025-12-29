#!/usr/bin/env python3
"""
Reading Time Validator

Validates that articles achieve their stated reading time.
A true 1-hour read requires approximately 12,000 words at 200 wpm for dense technical content.

Usage:
    python scripts/validate_reading_time.py
    python scripts/validate_reading_time.py --article gdp/altair
"""

import argparse
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
ARTICLES_DIR = PROJECT_ROOT / "site" / "src" / "pages" / "articles"


def count_words(text: str) -> int:
    """Count words in text, excluding HTML tags and code blocks."""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Remove code blocks
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'`[^`]+`', '', text)
    # Count words
    words = text.split()
    return len(words)


def extract_reading_time(content: str) -> int | None:
    """Extract stated reading time from frontmatter or HTML meta tag."""
    # Check frontmatter first
    match = re.search(r'readingTime:\s*["\']?(\d+)\s*min', content)
    if match:
        return int(match.group(1))

    # Check HTML meta tag (e.g., <p class="meta">53 min read</p>)
    match = re.search(r'class="meta"[^>]*>(\d+)\s*min\s*read', content)
    if match:
        return int(match.group(1))

    return None


def validate_article(path: Path) -> dict:
    """Validate a single article's reading time."""
    content = path.read_text()

    # Extract actual word count
    word_count = count_words(content)

    # Calculate actual reading time (200 wpm for technical content)
    actual_minutes = word_count // 200

    # Extract stated reading time
    stated_minutes = extract_reading_time(content)

    # Determine if valid
    if stated_minutes is None:
        status = "missing"
        message = "No reading time found in frontmatter"
    elif abs(actual_minutes - stated_minutes) <= 5:
        status = "valid"
        message = f"Reading time validated: {actual_minutes} min actual, {stated_minutes} min stated"
    else:
        status = "invalid"
        if actual_minutes < stated_minutes:
            needed = stated_minutes * 200
            message = (
                f"UNDERCOUNT: {actual_minutes} min actual vs {stated_minutes} min stated. "
                f"Need {needed - word_count} more words ({needed} total) for {stated_minutes} min."
            )
        else:
            message = f"OVERCOUNT: {actual_minutes} min actual vs {stated_minutes} min stated."

    return {
        "path": str(path.relative_to(PROJECT_ROOT)),
        "word_count": word_count,
        "actual_minutes": actual_minutes,
        "stated_minutes": stated_minutes,
        "status": status,
        "message": message,
    }


# Minimum word counts for pre-commit hook
MINIMUM_WORDS = {
    "one-hour": 10000,   # 50 min minimum for "one-hour" reads
    "30-min": 5000,      # 25 min minimum
    "15-min": 2500,      # 12.5 min minimum
    "default": 2000,     # 10 min minimum for any article
}


def main():
    parser = argparse.ArgumentParser(description="Validate article reading times")
    parser.add_argument("--article", help="Specific article to validate (e.g., gdp/altair)")
    parser.add_argument("--strict", action="store_true",
                        help="Fail if any article is under minimum word count (for pre-commit)")
    args = parser.parse_args()

    print("=" * 60)
    print("Reading Time Validator")
    print("Target: 200 words per minute for technical content")
    if args.strict:
        print(f"STRICT MODE: Minimum {MINIMUM_WORDS['default']} words per article")
    print("=" * 60)

    if args.article:
        # Validate specific article
        article_path = ARTICLES_DIR / args.article
        if article_path.is_dir():
            # Look for .astro file
            astro_files = list(article_path.glob("*.astro"))
            if not astro_files:
                astro_files = [article_path.with_suffix(".astro")]
        else:
            astro_files = [article_path.with_suffix(".astro")]

        for path in astro_files:
            if path.exists():
                result = validate_article(path)
                print_result(result)
    else:
        # Validate all articles (skip redirect files like index.astro)
        astro_files = [
            f for f in ARTICLES_DIR.rglob("*.astro")
            if f.name != "index.astro"  # Skip redirect files
        ]

        if not astro_files:
            print("No articles found.")
            return

        results = []
        for path in astro_files:
            result = validate_article(path)
            results.append(result)

        # Print results
        valid_count = sum(1 for r in results if r["status"] == "valid")
        invalid_count = sum(1 for r in results if r["status"] == "invalid")

        print(f"\nFound {len(results)} article(s)\n")

        for result in results:
            print_result(result)

        print("\n" + "=" * 60)
        print(f"Summary: {valid_count} valid, {invalid_count} invalid")

        if invalid_count > 0:
            print("\nWARNING: Some articles don't match their stated reading time!")

        # Strict mode: check minimum word counts
        if args.strict:
            under_minimum = [r for r in results if r["word_count"] < MINIMUM_WORDS["default"]]
            if under_minimum:
                print("\n" + "!" * 60)
                print("STRICT MODE FAILURE: Articles under minimum word count!")
                print("!" * 60)
                for r in under_minimum:
                    print(f"  {r['path']}: {r['word_count']} words (need {MINIMUM_WORDS['default']})")
                print("\nDO NOT REMOVE ARTICLES - IMMEDIATELY ENHANCE THEM WITH MORE TEXT AND CHARTS!")
                sys.exit(1)
            else:
                print("\nStrict mode: All articles meet minimum word count.")

        if invalid_count > 0:
            sys.exit(1)


def print_result(result: dict):
    """Print a single validation result."""
    status_icon = {
        "valid": "✓",
        "invalid": "✗",
        "missing": "?",
    }[result["status"]]

    print(f"\n{status_icon} {result['path']}")
    print(f"  Words: {result['word_count']:,}")
    print(f"  {result['message']}")


if __name__ == "__main__":
    main()
