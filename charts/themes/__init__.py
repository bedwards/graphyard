"""
Chart Themes - Publication-ready color palettes and styling.
"""

from dataclasses import dataclass


@dataclass
class ColorPalette:
    """Color palette for charts."""

    primary: str
    secondary: str
    accent: str
    positive: str
    negative: str
    neutral: str
    sequence: list[str]


# Publication theme with accessible colors
PUBLICATION = ColorPalette(
    primary="#2563EB",      # Blue
    secondary="#7C3AED",    # Purple
    accent="#F59E0B",       # Amber
    positive="#10B981",     # Green
    negative="#EF4444",     # Red
    neutral="#6B7280",      # Gray
    sequence=[
        "#2563EB",  # Blue
        "#7C3AED",  # Purple
        "#EC4899",  # Pink
        "#F59E0B",  # Amber
        "#10B981",  # Green
        "#06B6D4",  # Cyan
        "#8B5CF6",  # Violet
        "#F97316",  # Orange
    ]
)

# Economist-style muted palette
ECONOMIST = ColorPalette(
    primary="#0D6EAD",
    secondary="#8B0000",
    accent="#DAA520",
    positive="#228B22",
    negative="#8B0000",
    neutral="#4A4A4A",
    sequence=[
        "#0D6EAD",
        "#8B0000",
        "#DAA520",
        "#228B22",
        "#4B0082",
        "#FF6347",
    ]
)

# World Bank style
WORLDBANK = ColorPalette(
    primary="#002244",
    secondary="#0071BC",
    accent="#F5A623",
    positive="#00A651",
    negative="#ED1C24",
    neutral="#58595B",
    sequence=[
        "#002244",
        "#0071BC",
        "#00A651",
        "#F5A623",
        "#ED1C24",
        "#8E44AD",
    ]
)


def get_palette(name: str = "publication") -> ColorPalette:
    """Get a color palette by name."""
    palettes = {
        "publication": PUBLICATION,
        "economist": ECONOMIST,
        "worldbank": WORLDBANK,
    }
    return palettes.get(name.lower(), PUBLICATION)
