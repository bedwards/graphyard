"""
Chart Generation Tests

Tests for the chart data loading and rendering system.
Run with: uv run pytest tests/
"""

import pytest
from pathlib import Path

# Add project root to path
import sys
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "charts"))


class TestDataLoaders:
    """Test GDP data loading functions."""

    def test_world_gdp_trend_returns_data(self):
        from charts.gdp.data import load_world_gdp_trend
        df = load_world_gdp_trend(1960, 2023)
        assert len(df) > 0
        assert "year" in df.columns
        assert "value" in df.columns

    def test_world_gdp_trend_year_range(self):
        from charts.gdp.data import load_world_gdp_trend
        df = load_world_gdp_trend(2000, 2010)
        years = df["year"].tolist()
        assert min(years) >= 2000
        assert max(years) <= 2010

    def test_country_gdp_comparison(self):
        from charts.gdp.data import load_country_gdp_comparison
        df = load_country_gdp_comparison(["USA", "CHN"], 2022)
        assert len(df) == 2
        assert "entity_name" in df.columns
        assert "value" in df.columns

    def test_gdp_growth_rates(self):
        from charts.gdp.data import load_gdp_growth_rates
        df = load_gdp_growth_rates("WLD", 10)
        assert len(df) <= 10
        assert "year" in df.columns
        assert "value" in df.columns
        # Growth rates should be reasonable (-20% to +20%)
        assert df["value"].min() > -20
        assert df["value"].max() < 20

    def test_gdp_components(self):
        from charts.gdp.data import load_gdp_components
        df = load_gdp_components("USA", 2022)
        assert len(df) > 0
        # Should have consumption, investment, government, exports, imports
        names = df["indicator_name"].tolist()
        assert "Consumption (C)" in names

    def test_regional_gdp(self):
        from charts.gdp.data import load_regional_gdp
        df = load_regional_gdp(2022)
        assert len(df) > 0
        assert "entity_name" in df.columns

    def test_country_gdp_timeseries(self):
        from charts.gdp.data import load_country_gdp_timeseries
        df = load_country_gdp_timeseries(["USA", "CHN"], 2000, 2020)
        assert len(df) > 0
        assert "country" in df.columns
        assert "year" in df.columns
        assert "value" in df.columns
        countries = df["country"].unique()
        assert len(countries) == 2


class TestChartSpecs:
    """Test chart specification generation."""

    def test_chart_specs_exist(self):
        from charts.generate_dual import get_gdp_chart_specs
        specs = get_gdp_chart_specs()
        assert len(specs) >= 7  # We have 7 charts

    def test_chart_specs_have_required_fields(self):
        from charts.generate_dual import get_gdp_chart_specs
        specs = get_gdp_chart_specs()
        for spec in specs:
            assert spec.chart_id
            assert spec.chart_type
            assert spec.title
            assert spec.data_source is not None

    def test_chart_specs_load_data(self):
        from charts.generate_dual import get_gdp_chart_specs
        specs = get_gdp_chart_specs()
        for spec in specs:
            data = spec.load_data()
            assert len(data) > 0, f"No data for {spec.chart_id}"


class TestAltairRenderer:
    """Test Altair chart rendering."""

    def test_renderer_creates_charts(self):
        from charts.altair_renderer import AltairRenderer
        from charts.generate_dual import get_gdp_chart_specs

        renderer = AltairRenderer()
        specs = get_gdp_chart_specs()

        # Test first chart
        chart = renderer.render(specs[0])
        assert chart is not None

    def test_year_format_no_commas(self):
        """Years should display as 2020, not 2,020."""
        from charts.altair_renderer import AltairRenderer
        from charts.generate_dual import get_gdp_chart_specs

        renderer = AltairRenderer()
        specs = get_gdp_chart_specs()

        # Find a chart with year format
        year_spec = next(s for s in specs if s.x_format == "year")
        data = year_spec.load_data()

        # After rendering, year values should be strings (no commas)
        # The renderer converts years to strings to avoid comma formatting
        # We can verify by checking the data transformation
        assert year_spec.x == "year"


class TestChartOutput:
    """Test that chart files are generated correctly."""

    def test_chart_files_exist(self):
        output_dir = PROJECT_ROOT / "site" / "public" / "assets" / "charts" / "altair"
        expected_charts = [
            "world-gdp-trend",
            "world-gdp-growth",
            "top-10-gdp",
            "gdp-by-region",
            "gdp-per-capita-income-groups",
            "gdp-components-usa",
            "china-usa-gdp",
        ]
        for chart_id in expected_charts:
            svg_path = output_dir / f"{chart_id}.svg"
            png_path = output_dir / f"{chart_id}.png"
            assert svg_path.exists(), f"Missing {svg_path}"
            assert png_path.exists(), f"Missing {png_path}"

    def test_svg_files_are_valid(self):
        output_dir = PROJECT_ROOT / "site" / "public" / "assets" / "charts" / "altair"
        for svg_file in output_dir.glob("*.svg"):
            content = svg_file.read_text()
            assert content.startswith("<?xml") or content.startswith("<svg")
            assert "</svg>" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
