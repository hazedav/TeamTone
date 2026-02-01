"""
Integration tests for scrapers

These tests make real HTTP requests to verify scrapers work against live sites.
They are skipped by default and can be run with: pytest -m integration

Run with: pytest teamtone/fetch/test_integration.py -v
"""

import os

import pytest

from filament_sites import (
    FilamentProfilesScraper,
    OvertureScraper,
    PolymakerScraper,
    SunluScraper,
)


# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


@pytest.mark.skipif(
    os.environ.get("CI") == "true",
    reason="3dfilamentprofiles.com rate-limits GitHub Actions IPs",
)
class TestFilamentProfilesScraperIntegration:
    """Integration tests for FilamentProfilesScraper"""

    def test_fetch_returns_filaments(self):
        """Scraper should return a positive number of filaments"""
        scraper = FilamentProfilesScraper()
        result = scraper.fetch(per_page=10, delay=3.0)

        assert "filaments" in result
        assert len(result["filaments"]) > 0, "Expected at least 1 filament"

    def test_filaments_have_required_fields(self):
        """Each filament should have manufacturer, material, color, hex"""
        scraper = FilamentProfilesScraper()
        result = scraper.fetch(per_page=10, delay=3.0)

        required_fields = ["manufacturer", "material", "color", "hex"]
        for filament in result["filaments"][:5]:
            for field in required_fields:
                assert field in filament, f"Missing {field} in {filament}"
                assert filament[field], f"Empty {field} in {filament}"


class TestPolymakerScraperIntegration:
    """Integration tests for PolymakerScraper"""

    def test_fetch_returns_filaments(self):
        """Scraper should return a positive number of filaments"""
        scraper = PolymakerScraper()
        result = scraper.fetch(max_products=3, delay=0.5)

        assert "filaments" in result
        assert len(result["filaments"]) > 0, "Expected at least 1 filament"

    def test_filaments_have_required_fields(self):
        """Each filament should have manufacturer, material, color, hex"""
        scraper = PolymakerScraper()
        result = scraper.fetch(max_products=3, delay=0.5)

        required_fields = ["manufacturer", "material", "color", "hex"]
        for filament in result["filaments"][:5]:
            for field in required_fields:
                assert field in filament, f"Missing {field} in {filament}"
                assert filament[field], f"Empty {field} in {filament}"

    def test_manufacturer_is_polymaker(self):
        """All filaments should be from Polymaker"""
        scraper = PolymakerScraper()
        result = scraper.fetch(max_products=3, delay=0.5)

        for filament in result["filaments"]:
            assert filament["manufacturer"] == "Polymaker"


class TestSunluScraperIntegration:
    """Integration tests for SunluScraper"""

    def test_fetch_returns_filaments(self):
        """Scraper should return a positive number of filaments"""
        scraper = SunluScraper()
        result = scraper.fetch(max_products=10, delay=0.5)

        assert "filaments" in result
        assert len(result["filaments"]) > 0, "Expected at least 1 filament"

    def test_filaments_have_required_fields(self):
        """Each filament should have manufacturer, material, color, hex"""
        scraper = SunluScraper()
        result = scraper.fetch(max_products=10, delay=0.5)

        required_fields = ["manufacturer", "material", "color", "hex"]
        for filament in result["filaments"][:5]:
            for field in required_fields:
                assert field in filament, f"Missing {field} in {filament}"
                assert filament[field], f"Empty {field} in {filament}"

    def test_manufacturer_is_sunlu(self):
        """All filaments should be from SUNLU"""
        scraper = SunluScraper()
        result = scraper.fetch(max_products=10, delay=0.5)

        for filament in result["filaments"]:
            assert filament["manufacturer"] == "SUNLU"


class TestOvertureScraperIntegration:
    """Integration tests for OvertureScraper"""

    def test_fetch_returns_filaments(self):
        """Scraper should return a positive number of filaments"""
        scraper = OvertureScraper()
        result = scraper.fetch(max_products=5, delay=0.5)

        assert "filaments" in result
        assert len(result["filaments"]) > 0, "Expected at least 1 filament"

    def test_filaments_have_required_fields(self):
        """Each filament should have manufacturer, material, color, hex"""
        scraper = OvertureScraper()
        result = scraper.fetch(max_products=5, delay=0.5)

        required_fields = ["manufacturer", "material", "color", "hex"]
        for filament in result["filaments"][:5]:
            for field in required_fields:
                assert field in filament, f"Missing {field} in {filament}"
                assert filament[field], f"Empty {field} in {filament}"

    def test_manufacturer_is_overture(self):
        """All filaments should be from Overture"""
        scraper = OvertureScraper()
        result = scraper.fetch(max_products=5, delay=0.5)

        for filament in result["filaments"]:
            assert filament["manufacturer"] == "Overture"
