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
    """Extract stated reading time from frontmatter."""
    match = re.search(r'readingTime:\s*["\']?(\d+)\s*min', content)
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


def main():
    parser = argparse.ArgumentParser(description="Validate article reading times")
    parser.add_argument("--article", help="Specific article to validate (e.g., gdp/altair)")
    args = parser.parse_args()

    print("=" * 60)
    print("Reading Time Validator")
    print("Target: 200 words per minute for technical content")
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
        # Validate all articles
        astro_files = list(ARTICLES_DIR.rglob("*.astro"))

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
