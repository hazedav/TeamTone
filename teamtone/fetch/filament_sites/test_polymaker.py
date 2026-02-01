"""
Test suite for PolymakerScraper

Run with: pytest teamtone/fetch/filament_sites/test_polymaker.py -v
"""

import pytest

from .polymaker import PolymakerScraper


@pytest.fixture
def scraper():
    """Create PolymakerScraper instance"""
    return PolymakerScraper()


class TestMaterialTypeExtraction:
    """Test material type extraction from product titles"""

    @pytest.mark.parametrize(
        "title,expected",
        [
            ("PolyLite PLA", "PLA"),
            ("PolyLite PLA Pro", "PLA"),
            ("PolyMax PETG", "PETG"),
            ("PolyFlex TPU95", "TPU"),
            ("PolyLite ABS", "ABS"),
            ("PolyMaker ASA", "ASA"),
            ("PolyMax PC", "PC"),
            ("PolyMide CoPA", "PA"),
            ("Fiberon PA12-CF10", "PA12"),
            ("Fiberon PA6-GF25", "PA6"),
            ("Unknown Product", "PLA"),  # Default fallback
        ],
    )
    def test_extract_material_type(self, scraper, title, expected):
        """Test that material types are correctly extracted from titles"""
        result = scraper._extract_material_type(title)
        assert result == expected, f"Expected {expected} for '{title}', got {result}"


class TestHexCodeExtraction:
    """Test hex code extraction from HTML"""

    def test_extract_variant_hex_codes_basic(self, scraper):
        """Test extraction of hex codes from variant metafields"""
        html = '''
        "39574341779513": {"metafields": {"hex_code": "#16161A"}}
        "39574341713977": {"metafields": {"hex_code": "#F0EBE8"}}
        '''
        result = scraper._extract_variant_hex_codes(html)

        assert "39574341779513" in result
        assert result["39574341779513"] == "#16161A"
        assert "39574341713977" in result
        assert result["39574341713977"] == "#F0EBE8"

    def test_extract_variant_hex_codes_without_hash(self, scraper):
        """Test extraction of hex codes without leading #"""
        html = '"39574341779513": {"metafields": {"hex_code": "16161A"}}'
        result = scraper._extract_variant_hex_codes(html)

        assert "39574341779513" in result
        assert result["39574341779513"] == "#16161A"

    def test_extract_variant_hex_codes_lowercase(self, scraper):
        """Test that hex codes are normalized to uppercase"""
        html = '"39574341779513": {"metafields": {"hex_code": "#abcdef"}}'
        result = scraper._extract_variant_hex_codes(html)

        assert result["39574341779513"] == "#ABCDEF"

    def test_extract_variant_hex_codes_empty(self, scraper):
        """Test extraction from HTML with no hex codes"""
        html = "<html><body>No hex codes here</body></html>"
        result = scraper._extract_variant_hex_codes(html)

        assert result == {}


class TestFilamentProductFilter:
    """Test filtering of filament vs non-filament products"""

    @pytest.mark.parametrize(
        "url,expected",
        [
            ("https://us.polymaker.com/products/polylite-pla", True),
            ("https://us.polymaker.com/products/polymax-petg", True),
            ("https://us.polymaker.com/products/polybox", False),
            ("https://us.polymaker.com/products/polydryer", False),
            ("https://us.polymaker.com/products/gift-card", False),
            ("https://us.polymaker.com/products/sample-box", False),
            ("https://us.polymaker.com/products/pla-bundle", False),
        ],
    )
    def test_is_filament_product(self, scraper, url, expected):
        """Test that filament products are correctly identified"""
        result = scraper._is_filament_product(url)
        assert result == expected, f"Expected {expected} for '{url}'"


class TestScraperProperties:
    """Test scraper property methods"""

    def test_site_name(self, scraper):
        """Test site_name property"""
        assert scraper.site_name == "us.polymaker.com"

    def test_site_url(self, scraper):
        """Test site_url property"""
        assert scraper.site_url == "https://us.polymaker.com"
