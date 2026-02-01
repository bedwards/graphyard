#!/usr/bin/env python3
"""
Compare PDF content with source HTML to identify discrepancies.
"""

import subprocess
import re
from pathlib import Path


def count_pdf_pages(pdf_path: Path) -> int:
    """Get page count from PDF."""
    result = subprocess.run(
        ["pdfinfo", str(pdf_path)],
        capture_output=True,
        text=True
    )
    for line in result.stdout.split("\n"):
        if line.startswith("Pages:"):
            return int(line.split(":")[1].strip())
    return 0


def count_pdf_words(pdf_path: Path) -> int:
    """Extract text from PDF and count words."""
    result = subprocess.run(
        ["pdftotext", str(pdf_path), "-"],
        capture_output=True,
        text=True
    )
    words = result.stdout.split()
    return len(words)


def count_pdf_images(pdf_path: Path) -> int:
    """Count images in PDF."""
    result = subprocess.run(
        ["pdfimages", "-list", str(pdf_path)],
        capture_output=True,
        text=True
    )
    # Subtract 1 for header line
    lines = [l for l in result.stdout.strip().split("\n") if l.strip()]
    return max(0, len(lines) - 1)


def analyze_html(html_path: Path) -> dict:
    """Analyze HTML source."""
    content = html_path.read_text()

    # Count charts
    chart_matches = re.findall(r'<img[^>]*class="[^"]*chart[^"]*"', content, re.IGNORECASE)
    svg_charts = re.findall(r'<svg[^>]*class="[^"]*marks[^"]*"', content)
    inline_svgs = content.count('<svg')

    # Count images
    img_tags = re.findall(r'<img[^>]*src="([^"]+)"', content)

    # Count words (rough estimate - remove HTML tags)
    text_only = re.sub(r'<[^>]+>', ' ', content)
    text_only = re.sub(r'\s+', ' ', text_only)
    words = len(text_only.split())

    # Count figures
    figures = content.count('<figure')

    return {
        "words": words,
        "img_tags": len(img_tags),
        "inline_svgs": inline_svgs,
        "figures": figures,
        "img_sources": img_tags[:10],  # First 10 for debugging
    }


def main():
    project_root = Path(__file__).parent.parent
    pdf_path = project_root / "articles/pdf/blood-money/altair.pdf"
    html_path = project_root / "docs/articles/blood-money/altair/index.html"

    print("=" * 60)
    print("PDF vs HTML COMPARISON")
    print("=" * 60)

    if not pdf_path.exists():
        print(f"PDF not found: {pdf_path}")
        return

    if not html_path.exists():
        print(f"HTML not found: {html_path}")
        return

    # PDF analysis
    print("\n📄 PDF ANALYSIS")
    print(f"   File: {pdf_path.name}")
    print(f"   Size: {pdf_path.stat().st_size:,} bytes")

    pdf_pages = count_pdf_pages(pdf_path)
    pdf_words = count_pdf_words(pdf_path)
    pdf_images = count_pdf_images(pdf_path)

    print(f"   Pages: {pdf_pages}")
    print(f"   Words: {pdf_words:,}")
    print(f"   Images: {pdf_images}")
    print(f"   Reading time: {pdf_words / 200:.1f} minutes ({pdf_words / 200 / 60:.1f} hours)")

    # HTML analysis
    print("\n🌐 HTML ANALYSIS")
    print(f"   File: {html_path.name}")

    html_stats = analyze_html(html_path)

    print(f"   Words (approx): {html_stats['words']:,}")
    print(f"   <img> tags: {html_stats['img_tags']}")
    print(f"   Inline SVGs: {html_stats['inline_svgs']}")
    print(f"   <figure> elements: {html_stats['figures']}")
    print(f"   Reading time: {html_stats['words'] / 200:.1f} minutes ({html_stats['words'] / 200 / 60:.1f} hours)")

    # Show sample image sources
    if html_stats['img_sources']:
        print("\n   Sample image sources:")
        for src in html_stats['img_sources'][:5]:
            print(f"     - {src[:80]}...")

    # Comparison
    print("\n🔍 DISCREPANCY ANALYSIS")

    word_diff = html_stats['words'] - pdf_words
    print(f"   Word difference: {word_diff:,} (HTML - PDF)")

    if pdf_images < html_stats['inline_svgs']:
        missing_charts = html_stats['inline_svgs'] - pdf_images
        print(f"   ⚠️  MISSING CHARTS: {missing_charts} SVGs not captured in PDF!")
        print(f"      HTML has {html_stats['inline_svgs']} inline SVGs")
        print(f"      PDF has only {pdf_images} images")
        print("\n   DIAGNOSIS: Playwright is not rendering inline SVGs to images.")
        print("   The charts exist in the HTML but are not being captured as images in the PDF.")

    # Check if charts are being loaded dynamically
    html_content = html_path.read_text()
    dynamic_charts = html_content.count('data-chart-id') or html_content.count('chart-container')
    if dynamic_charts:
        print(f"\n   Found {dynamic_charts} chart containers - charts may be loaded dynamically")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
