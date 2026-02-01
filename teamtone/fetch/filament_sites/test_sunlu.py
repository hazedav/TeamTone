"""
Test suite for SunluScraper

Run with: pytest teamtone/fetch/filament_sites/test_sunlu.py -v
"""

import pytest
from bs4 import BeautifulSoup

from .sunlu import SunluScraper


@pytest.fixture
def scraper():
    """Create SunluScraper instance"""
    return SunluScraper()


class TestMaterialTypeExtraction:
    """Test material type extraction from product URLs"""

    @pytest.mark.parametrize(
        "url,expected",
        [
            ("https://store.sunlu.com/collections/pla/products/some-pla", "PLA"),
            ("https://store.sunlu.com/collections/petg/products/petg-filament", "PETG"),
            ("https://store.sunlu.com/collections/abs/products/abs-basic", "ABS"),
            ("https://store.sunlu.com/collections/asa/products/asa-filament", "ASA"),
            ("https://store.sunlu.com/collections/tpu/products/tpu-95a", "TPU"),
            ("https://store.sunlu.com/collections/pla-plus/products/pla-plus", "PLA+"),
            # URL keywords
            ("https://store.sunlu.com/products/petg-3d-printer-filament", "PETG"),
            ("https://store.sunlu.com/products/pla-plus-filament", "PLA+"),
            ("https://store.sunlu.com/products/abs-filament-1kg", "ABS"),
            ("https://store.sunlu.com/products/tpu-flexible-filament", "TPU"),
            # Default fallback
            ("https://store.sunlu.com/products/unknown-product", "PLA"),
        ],
    )
    def test_extract_material_from_url(self, scraper, url, expected):
        """Test that material types are correctly extracted from URLs"""
        result = scraper._extract_material_from_url(url)
        assert result == expected, f"Expected {expected} for '{url}', got {result}"


class TestColorTableParsing:
    """Test parsing of color/hex tables from HTML"""

    def test_parse_color_table_basic(self, scraper):
        """Test basic color table parsing"""
        html = """
        <table>
            <tr><td>Black</td><td>#000000</td><td style="background-color: #000000;"></td></tr>
            <tr><td>White</td><td>#FFFFFF</td><td style="background-color: #FFFFFF;"></td></tr>
            <tr><td>Red</td><td>#BC2726</td><td style="background-color: #BC2726;"></td></tr>
        </table>
        """
        soup = BeautifulSoup(html, "html.parser")
        result = scraper._parse_color_table(soup)

        assert len(result) == 3
        assert ("Black", "#000000") in result
        assert ("White", "#FFFFFF") in result
        assert ("Red", "#BC2726") in result

    def test_parse_color_table_without_hash(self, scraper):
        """Test parsing hex codes without leading #"""
        html = """
        <table>
            <tr><td>Blue</td><td>1729AB</td></tr>
        </table>
        """
        soup = BeautifulSoup(html, "html.parser")
        result = scraper._parse_color_table(soup)

        assert len(result) == 1
        assert ("Blue", "#1729AB") in result

    def test_parse_color_table_lowercase_hex(self, scraper):
        """Test that hex codes are normalized to uppercase"""
        html = """
        <table>
            <tr><td>Green</td><td>#1daa27</td></tr>
        </table>
        """
        soup = BeautifulSoup(html, "html.parser")
        result = scraper._parse_color_table(soup)

        assert len(result) == 1
        assert ("Green", "#1DAA27") in result

    def test_parse_color_table_skips_headers(self, scraper):
        """Test that header rows are skipped"""
        html = """
        <table>
            <tr><td>Color</td><td>Hex Code</td></tr>
            <tr><td>Black</td><td>#000000</td></tr>
        </table>
        """
        soup = BeautifulSoup(html, "html.parser")
        result = scraper._parse_color_table(soup)

        assert len(result) == 1
        assert ("Black", "#000000") in result

    def test_parse_color_table_empty(self, scraper):
        """Test parsing HTML with no color table"""
        html = "<html><body>No table here</body></html>"
        soup = BeautifulSoup(html, "html.parser")
        result = scraper._parse_color_table(soup)

        assert result == []

    def test_parse_color_table_invalid_hex(self, scraper):
        """Test that invalid hex codes are skipped"""
        html = """
        <table>
            <tr><td>Valid</td><td>#FFFFFF</td></tr>
            <tr><td>Invalid</td><td>not-a-hex</td></tr>
            <tr><td>TooShort</td><td>#FFF</td></tr>
        </table>
        """
        soup = BeautifulSoup(html, "html.parser")
        result = scraper._parse_color_table(soup)

        assert len(result) == 1
        assert ("Valid", "#FFFFFF") in result

    def test_parse_color_table_with_parentheses(self, scraper):
        """Test parsing color names with parentheses"""
        html = """
        <table>
            <tr><td>Purple (Lavender Purple)</td><td>#685BC7</td></tr>
            <tr><td>Blue (Klein Blue)</td><td>#1729AB</td></tr>
        </table>
        """
        soup = BeautifulSoup(html, "html.parser")
        result = scraper._parse_color_table(soup)

        assert len(result) == 2
        assert ("Purple (Lavender Purple)", "#685BC7") in result
        assert ("Blue (Klein Blue)", "#1729AB") in result


class TestScraperProperties:
    """Test scraper property methods"""

    def test_site_name(self, scraper):
        """Test site_name property"""
        assert scraper.site_name == "store.sunlu.com"

    def test_site_url(self, scraper):
        """Test site_url property"""
        assert scraper.site_url == "https://store.sunlu.com"

    def test_sitemap_url(self, scraper):
        """Test SITEMAP_URL constant"""
        assert "sitemap_products" in scraper.SITEMAP_URL
        assert "store.sunlu.com" in scraper.SITEMAP_URL

    def test_collections_defined(self, scraper):
        """Test that collections are defined"""
        assert "PLA" in scraper.COLLECTIONS
        assert "PETG" in scraper.COLLECTIONS
        assert "ABS" in scraper.COLLECTIONS
        assert "TPU" in scraper.COLLECTIONS
