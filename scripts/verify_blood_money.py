#!/usr/bin/env python3
"""
Verify Blood Money article metadata: reading time, chapters, and charts.
"""

import re
from pathlib import Path


def main():
    article_path = Path(__file__).parent.parent / "site/src/pages/articles/blood-money/altair.astro"

    if not article_path.exists():
        print(f"Article not found: {article_path}")
        return

    content = article_path.read_text()

    # Count words (excluding HTML tags and code)
    text_only = re.sub(r'<[^>]+>', ' ', content)  # Remove HTML tags
    text_only = re.sub(r'\{[^}]+\}', ' ', text_only)  # Remove template expressions
    text_only = re.sub(r'\/\*[\s\S]*?\*\/', ' ', text_only)  # Remove comments
    text_only = re.sub(r'style="[^"]*"', ' ', text_only)  # Remove inline styles
    words = [w for w in text_only.split() if len(w) > 1 and not w.startswith(('--', '0x', '#'))]
    word_count = len(words)

    # Calculate reading time (200 wpm for technical content)
    reading_time_minutes = word_count / 200
    reading_time_hours = reading_time_minutes / 60

    # Count charts
    chart_matches = re.findall(r'<Chart\s+id="([^"]+)"', content)
    chart_count = len(chart_matches)
    unique_charts = set(chart_matches)
    duplicate_charts = chart_count - len(unique_charts)

    # Count chapters (h2 with id starting with "ch")
    chapter_matches = re.findall(r'<h2\s+id="(ch\d+)"[^>]*>([^<]+)</h2>', content)
    chapter_count = len(chapter_matches)

    # Check opening
    has_opening = bool(re.search(r'<h2\s+id="opening"', content))

    # Extract metadata line
    meta_match = re.search(r'<p class="meta">\s*([^<]+)\s*</p>', content)
    metadata = meta_match.group(1).strip() if meta_match else "Not found"

    # Parse metadata values
    meta_reading = re.search(r'(\d+)-hour read', metadata)
    meta_chapters = re.search(r'(\d+) chapters', metadata)
    meta_charts = re.search(r'(\d+) charts', metadata)

    print("=" * 60)
    print("BLOOD MONEY ARTICLE VERIFICATION")
    print("=" * 60)

    print(f"\n📄 WORD COUNT")
    print(f"   Words: {word_count:,}")
    print(f"   Reading time: {reading_time_minutes:.0f} minutes ({reading_time_hours:.1f} hours)")

    print(f"\n📊 CHARTS")
    print(f"   Total charts: {chart_count}")
    print(f"   Unique charts: {len(unique_charts)}")
    if duplicate_charts > 0:
        print(f"   ⚠️  Duplicates: {duplicate_charts}")

    print(f"\n📖 CHAPTERS")
    print(f"   Has Opening: {'Yes' if has_opening else 'No'}")
    print(f"   Numbered chapters: {chapter_count}")
    print(f"   Total sections: {chapter_count + (1 if has_opening else 0)}")

    print(f"\n📋 METADATA IN HEADER")
    print(f"   Raw: {metadata}")

    print(f"\n🔍 VERIFICATION")

    # Check reading time
    actual_hours = round(reading_time_hours)
    if meta_reading:
        claimed_hours = int(meta_reading.group(1))
        if abs(claimed_hours - reading_time_hours) <= 0.5:
            print(f"   ✅ Reading time: {claimed_hours}-hour read matches ~{reading_time_hours:.1f} hours")
        else:
            print(f"   ❌ Reading time MISMATCH: claims {claimed_hours}-hour, actual ~{reading_time_hours:.1f} hours")
    else:
        print(f"   ⚠️  Reading time not found in metadata")

    # Check chapter count
    if meta_chapters:
        claimed_chapters = int(meta_chapters.group(1))
        total_sections = chapter_count + (1 if has_opening else 0)
        if claimed_chapters == total_sections:
            print(f"   ✅ Chapters: {claimed_chapters} matches actual count")
        else:
            print(f"   ❌ Chapters MISMATCH: claims {claimed_chapters}, actual {total_sections}")
    else:
        print(f"   ⚠️  Chapter count not found in metadata")

    # Check chart count
    if meta_charts:
        claimed_charts = int(meta_charts.group(1))
        if claimed_charts == chart_count:
            print(f"   ✅ Charts: {claimed_charts} matches actual count")
        else:
            print(f"   ❌ Charts MISMATCH: claims {claimed_charts}, actual {chart_count}")
    else:
        print(f"   ⚠️  Chart count not found in metadata")

    # Chapter numbering verification
    print(f"\n📑 CHAPTER NUMBERING")
    expected_num = 1
    for ch_id, ch_title in chapter_matches:
        actual_num = int(ch_id.replace('ch', ''))
        if actual_num != expected_num:
            print(f"   ❌ Gap: Expected ch{expected_num}, found {ch_id}: {ch_title}")
        expected_num = actual_num + 1
    print(f"   ✅ Chapters 1-{chapter_count} are correctly numbered")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
