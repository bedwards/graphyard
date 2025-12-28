#!/usr/bin/env python3
"""
PDF Generation Script

Generates publication-quality PDFs from HTML articles using WeasyPrint.
Features:
- Lexend font family for readability
- CSS Paged Media for professional print layout
- Automatic chart embedding
- Table of contents generation

Usage:
    python scripts/generate_pdf.py --article gdp
    python scripts/generate_pdf.py --all
"""

import argparse
from pathlib import Path
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration


# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
SITE_DIR = PROJECT_ROOT / "site"
DIST_DIR = SITE_DIR / "dist"
PDF_OUTPUT_DIR = PROJECT_ROOT / "articles" / "pdf"
FONTS_DIR = PROJECT_ROOT / "fonts"


# CSS for PDF styling with Lexend font
PDF_STYLES = """
@import url('https://fonts.googleapis.com/css2?family=Lexend:wght@300;400;500;600;700&display=swap');

@page {
    size: A4;
    margin: 2.5cm 2cm;

    @top-center {
        content: string(title);
        font-family: 'Lexend', sans-serif;
        font-size: 10pt;
        color: #666;
    }

    @bottom-center {
        content: counter(page);
        font-family: 'Lexend', sans-serif;
        font-size: 10pt;
    }

    @bottom-right {
        content: "Graphyard";
        font-family: 'Lexend', sans-serif;
        font-size: 9pt;
        color: #999;
    }
}

@page :first {
    @top-center { content: none; }
}

:root {
    --color-text: #1a1a2e;
    --color-text-muted: #4a5568;
    --color-accent: #2563eb;
    --color-background: #ffffff;
    --color-border: #e5e7eb;
}

* {
    box-sizing: border-box;
}

body {
    font-family: 'Lexend', -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 11pt;
    line-height: 1.7;
    color: var(--color-text);
    max-width: 100%;
    margin: 0;
    padding: 0;
}

/* Title page styling */
.article-header {
    page-break-after: always;
    text-align: center;
    padding-top: 30%;
}

.article-header h1 {
    font-size: 28pt;
    font-weight: 700;
    line-height: 1.2;
    margin-bottom: 1em;
    string-set: title content();
}

.article-header .subtitle {
    font-size: 14pt;
    color: var(--color-text-muted);
    margin-bottom: 2em;
}

.article-header .meta {
    font-size: 11pt;
    color: var(--color-text-muted);
}

/* Headings */
h1, h2, h3, h4 {
    font-weight: 600;
    line-height: 1.3;
    margin-top: 1.5em;
    margin-bottom: 0.5em;
    page-break-after: avoid;
}

h2 {
    font-size: 18pt;
    border-bottom: 1px solid var(--color-border);
    padding-bottom: 0.3em;
    page-break-before: always;
}

h2:first-of-type {
    page-break-before: avoid;
}

h3 {
    font-size: 14pt;
}

h4 {
    font-size: 12pt;
}

/* Paragraphs */
p {
    margin: 0 0 1em 0;
    text-align: justify;
    hyphens: auto;
    orphans: 3;
    widows: 3;
}

/* Links */
a {
    color: var(--color-accent);
    text-decoration: none;
}

/* Lists */
ul, ol {
    margin: 1em 0;
    padding-left: 1.5em;
}

li {
    margin-bottom: 0.5em;
}

/* Block quotes */
blockquote {
    margin: 1.5em 0;
    padding: 1em 1.5em;
    border-left: 4px solid var(--color-accent);
    background: #f8f9fa;
    font-style: italic;
}

blockquote p:last-child {
    margin-bottom: 0;
}

/* Figures and charts */
figure {
    margin: 2em 0;
    page-break-inside: avoid;
}

figure img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 0 auto;
}

figcaption {
    margin-top: 0.75em;
    font-size: 10pt;
    color: var(--color-text-muted);
    text-align: center;
    line-height: 1.5;
}

figcaption strong {
    display: block;
    font-weight: 600;
    color: var(--color-text);
    margin-bottom: 0.25em;
}

/* Tables */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 1.5em 0;
    font-size: 10pt;
    page-break-inside: avoid;
}

th, td {
    padding: 0.75em;
    border: 1px solid var(--color-border);
    text-align: left;
}

th {
    background: #f8f9fa;
    font-weight: 600;
}

/* Code */
code {
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    font-size: 0.9em;
    background: #f4f4f5;
    padding: 0.15em 0.3em;
    border-radius: 3px;
}

pre {
    background: #1e1e2e;
    color: #cdd6f4;
    padding: 1em;
    border-radius: 6px;
    overflow-x: auto;
    font-size: 9pt;
    line-height: 1.5;
    page-break-inside: avoid;
}

pre code {
    background: none;
    padding: 0;
    color: inherit;
}

/* Horizontal rules */
hr {
    border: none;
    border-top: 1px solid var(--color-border);
    margin: 2em 0;
}

/* Definition boxes */
.definition {
    margin: 1.5em 0;
    padding: 1em 1.5em;
    background: #f0f9ff;
    border-left: 4px solid var(--color-accent);
    border-radius: 0 6px 6px 0;
    page-break-inside: avoid;
}

.definition-term {
    font-weight: 600;
    font-size: 12pt;
    margin-bottom: 0.5em;
}

/* Print-specific adjustments */
@media print {
    .no-print {
        display: none;
    }

    a[href]:after {
        content: none;
    }
}
"""


def generate_pdf(html_path: Path, output_path: Path) -> Path:
    """
    Generate PDF from HTML file.

    Args:
        html_path: Path to source HTML file
        output_path: Path for output PDF

    Returns:
        Path to generated PDF
    """
    font_config = FontConfiguration()

    # Read HTML
    html_content = html_path.read_text()

    # Create HTML object with base URL for relative paths
    html = HTML(
        string=html_content,
        base_url=str(html_path.parent),
    )

    # Apply custom CSS
    css = CSS(string=PDF_STYLES, font_config=font_config)

    # Generate PDF
    output_path.parent.mkdir(parents=True, exist_ok=True)
    html.write_pdf(
        output_path,
        stylesheets=[css],
        font_config=font_config,
    )

    print(f"  [PDF] Generated: {output_path.name}")
    return output_path


def find_articles() -> list[tuple[str, Path]]:
    """Find all built article HTML files."""
    articles = []

    articles_dir = DIST_DIR / "articles"
    if not articles_dir.exists():
        return articles

    for domain_dir in articles_dir.iterdir():
        if domain_dir.is_dir():
            for article_dir in domain_dir.iterdir():
                if article_dir.is_dir():
                    index_html = article_dir / "index.html"
                    if index_html.exists():
                        article_id = f"{domain_dir.name}/{article_dir.name}"
                        articles.append((article_id, index_html))

    return articles


def main():
    parser = argparse.ArgumentParser(description="Generate PDFs from articles")
    parser.add_argument(
        "--article",
        help="Article ID to generate (e.g., 'gdp/altair')"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Generate PDFs for all articles"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PDF_OUTPUT_DIR,
        help="Output directory for PDFs"
    )

    args = parser.parse_args()

    print("=" * 50)
    print("PDF Generation")
    print("=" * 50)

    if args.all:
        articles = find_articles()
        if not articles:
            print("No articles found. Run 'npm run build' first.")
            return

        print(f"Found {len(articles)} articles")
        for article_id, html_path in articles:
            output_path = args.output_dir / f"{article_id.replace('/', '-')}.pdf"
            generate_pdf(html_path, output_path)

    elif args.article:
        html_path = DIST_DIR / "articles" / args.article / "index.html"
        if not html_path.exists():
            print(f"Article not found: {html_path}")
            print("Run 'npm run build' first.")
            return

        output_path = args.output_dir / f"{args.article.replace('/', '-')}.pdf"
        generate_pdf(html_path, output_path)

    else:
        parser.print_help()

    print("=" * 50)
    print("Done!")


if __name__ == "__main__":
    main()
