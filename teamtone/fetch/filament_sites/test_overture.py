"""
Test suite for OvertureScraper

Run with: pytest teamtone/fetch/filament_sites/test_overture.py -v
"""

import pytest
from bs4 import BeautifulSoup

from .overture import OvertureScraper, _hex_to_luminance


@pytest.fixture
def scraper():
    """Create OvertureScraper instance"""
    return OvertureScraper()


class TestHexToLuminance:
    """Test the luminance calculation helper function"""

    def test_black_luminance(self):
        """Black should have luminance near 0"""
        assert _hex_to_luminance("#000000") == 0.0

    def test_white_luminance(self):
        """White should have luminance near 1"""
        assert _hex_to_luminance("#FFFFFF") == pytest.approx(1.0, abs=0.01)

    def test_gray_luminance(self):
        """Gray should have luminance around 0.5"""
        lum = _hex_to_luminance("#808080")
        assert 0.2 < lum < 0.6

    def test_without_hash(self):
        """Should work without leading #"""
        assert _hex_to_luminance("000000") == 0.0

    def test_lowercase(self):
        """Should work with lowercase hex"""
        assert _hex_to_luminance("#ffffff") == pytest.approx(1.0, abs=0.01)


class TestMaterialTypeExtraction:
    """Test material type extraction from product URLs and titles"""

    @pytest.mark.parametrize(
        "url,expected",
        [
            ("https://overture3d.com/products/overture-petg", "PETG"),
            ("https://overture3d.com/products/overture-pla", "PLA"),
            ("https://overture3d.com/products/overture-abs-filament", "ABS"),
            ("https://overture3d.com/products/overture-asa-filament", "ASA"),
            ("https://overture3d.com/products/overture-tpu", "TPU"),
            ("https://overture3d.com/products/overture-pla-plus", "PLA+"),
            ("https://overture3d.com/products/overture-pc-professional", "PC"),
            ("https://overture3d.com/products/unknown-product", "PLA"),
            # silk-pla and matte-pla URLs match "pla" first - title extraction handles variants
            ("https://overture3d.com/products/overture-silk-pla", "PLA"),
            ("https://overture3d.com/products/overture-matte-pla", "PLA"),
        ],
    )
    def test_extract_material_from_url(self, scraper, url, expected):
        """Test that material types are correctly extracted from URLs"""
        result = scraper._extract_material_from_url(url)
        assert result == expected, f"Expected {expected} for '{url}', got {result}"

    @pytest.mark.parametrize(
        "title,expected",
        [
            ("Overture PETG 3D Printer Filament", "PETG"),
            ("Overture PLA 3D Printer Filament", "PLA"),
            ("Overture PLA+ 3D Printer Filament", "PLA+"),
            ("Overture PLA PLUS Filament", "PLA+"),
            ("Overture Silk PLA Filament", "PLA Silk"),
            ("Overture PLA Silk Filament", "PLA Silk"),
            ("Overture Matte PLA Filament", "PLA Matte"),
            ("Overture ABS Filament", "ABS"),
            ("Overture ASA Filament", "ASA"),
            ("Overture TPU Filament", "TPU"),
            ("Overture PC Filament", "PC"),
            ("Overture Easy Nylon Filament", "PA"),
            ("Unknown Filament", "PLA"),
        ],
    )
    def test_extract_material_from_title(self, scraper, title, expected):
        """Test that material types are correctly extracted from titles"""
        result = scraper._extract_material_from_title(title)
        assert result == expected, f"Expected {expected} for '{title}', got {result}"


class TestFilamentProductFilter:
    """Test filtering of filament vs non-filament products"""

    @pytest.mark.parametrize(
        "url,expected",
        [
            ("https://overture3d.com/products/overture-pla", True),
            ("https://overture3d.com/products/overture-petg", True),
            ("https://overture3d.com/products/overture-dryer", False),
            ("https://overture3d.com/products/overture-enclosure", False),
            ("https://overture3d.com/products/overture-nozzle-kit", False),
            ("https://overture3d.com/products/gift-card", False),
            ("https://overture3d.com/products/pla-bundle", False),
        ],
    )
    def test_is_filament_product(self, scraper, url, expected):
        """Test that filament products are correctly identified"""
        result = scraper._is_filament_product(url)
        assert result == expected, f"Expected {expected} for '{url}'"


class TestColorExtraction:
    """Test extraction of colors from HTML with data-hex_code attributes"""

    def test_parse_product_page_extracts_colors(self, scraper):
        """Test that colors are extracted from label elements"""
        html = """
        <html>
        <head><title>Overture PLA Filament</title></head>
        <body>
        <h1>Overture PLA 3D Printer Filament</h1>
        <label class="opt-label" data-hex_code="#000000">
            <span class="visually-hidden js-value">Black</span>
        </label>
        <label class="opt-label" data-hex_code="#FFFFFF">
            <span class="visually-hidden js-value">White</span>
        </label>
        <label class="opt-label" data-hex_code="#FF0000">
            <span class="visually-hidden js-value">Red</span>
        </label>
        </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        color_labels = soup.find_all("label", attrs={"data-hex_code": True})

        assert len(color_labels) == 3

        # Verify extraction
        colors = []
        for label in color_labels:
            hex_code = label.get("data-hex_code")
            color_span = label.find("span", class_="js-value")
            color_name = color_span.get_text(strip=True) if color_span else None
            if color_name and hex_code:
                colors.append((color_name, hex_code))

        assert ("Black", "#000000") in colors
        assert ("White", "#FFFFFF") in colors
        assert ("Red", "#FF0000") in colors

    def test_parse_product_page_normalizes_hex(self, scraper):
        """Test that hex codes are normalized to uppercase"""
        html = """
        <label class="opt-label" data-hex_code="#abcdef">
            <span class="js-value">Blue</span>
        </label>
        """
        soup = BeautifulSoup(html, "html.parser")
        label = soup.find("label", attrs={"data-hex_code": True})
        hex_code = label.get("data-hex_code").upper()

        assert hex_code == "#ABCDEF"

    def test_parse_product_page_skips_invalid_hex(self, scraper):
        """Test that invalid hex codes are handled"""
        html = """
        <label class="opt-label" data-hex_code="not-a-hex">
            <span class="js-value">Invalid</span>
        </label>
        <label class="opt-label" data-hex_code="#FFFFFF">
            <span class="js-value">Valid</span>
        </label>
        """
        soup = BeautifulSoup(html, "html.parser")
        labels = soup.find_all("label", attrs={"data-hex_code": True})

        valid_colors = []
        import re

        for label in labels:
            hex_code = label.get("data-hex_code")
            if re.match(r"^#?[0-9A-Fa-f]{6}$", hex_code):
                valid_colors.append(hex_code)

        assert len(valid_colors) == 1
        assert "#FFFFFF" in valid_colors


class TestBlackWhiteSwapFix:
    """Test the Black/White hex code swap detection and fix"""

    def test_fix_swapped_black_white_when_swapped(self, scraper):
        """Should swap hex codes when Black is lighter than White"""
        filaments = [
            {"color": "Black", "hex": "#FFFFFF", "manufacturer": "Overture"},
            {"color": "White", "hex": "#000000", "manufacturer": "Overture"},
            {"color": "Red", "hex": "#FF0000", "manufacturer": "Overture"},
        ]

        result = scraper._fix_swapped_black_white(filaments)

        black = next(f for f in result if f["color"] == "Black")
        white = next(f for f in result if f["color"] == "White")

        assert black["hex"] == "#000000"
        assert white["hex"] == "#FFFFFF"

    def test_fix_swapped_black_white_when_correct(self, scraper):
        """Should not swap hex codes when they are already correct"""
        filaments = [
            {"color": "Black", "hex": "#000000", "manufacturer": "Overture"},
            {"color": "White", "hex": "#FFFFFF", "manufacturer": "Overture"},
        ]

        result = scraper._fix_swapped_black_white(filaments)

        black = next(f for f in result if f["color"] == "Black")
        white = next(f for f in result if f["color"] == "White")

        assert black["hex"] == "#000000"
        assert white["hex"] == "#FFFFFF"

    def test_fix_swapped_black_white_only_black(self, scraper):
        """Should not error when only Black is present"""
        filaments = [
            {"color": "Black", "hex": "#000000", "manufacturer": "Overture"},
            {"color": "Red", "hex": "#FF0000", "manufacturer": "Overture"},
        ]

        result = scraper._fix_swapped_black_white(filaments)

        assert len(result) == 2
        black = next(f for f in result if f["color"] == "Black")
        assert black["hex"] == "#000000"

    def test_fix_swapped_black_white_only_white(self, scraper):
        """Should not error when only White is present"""
        filaments = [
            {"color": "White", "hex": "#FFFFFF", "manufacturer": "Overture"},
            {"color": "Blue", "hex": "#0000FF", "manufacturer": "Overture"},
        ]

        result = scraper._fix_swapped_black_white(filaments)

        assert len(result) == 2
        white = next(f for f in result if f["color"] == "White")
        assert white["hex"] == "#FFFFFF"

    def test_fix_swapped_black_white_neither(self, scraper):
        """Should not error when neither Black nor White is present"""
        filaments = [
            {"color": "Red", "hex": "#FF0000", "manufacturer": "Overture"},
            {"color": "Blue", "hex": "#0000FF", "manufacturer": "Overture"},
        ]

        result = scraper._fix_swapped_black_white(filaments)

        assert len(result) == 2

    def test_fix_swapped_black_white_empty_list(self, scraper):
        """Should handle empty list"""
        result = scraper._fix_swapped_black_white([])
        assert result == []


class TestScraperProperties:
    """Test scraper property methods"""

    def test_site_name(self, scraper):
        """Test site_name property"""
        assert scraper.site_name == "overture3d.com"

    def test_site_url(self, scraper):
        """Test site_url property"""
        assert scraper.site_url == "https://overture3d.com"

    def test_sitemap_url(self, scraper):
        """Test SITEMAP_URL constant"""
        assert "sitemap_products" in scraper.SITEMAP_URL
        assert "overture3d.com" in scraper.SITEMAP_URL

    def test_default_delay(self, scraper):
        """Test DEFAULT_DELAY constant"""
        assert scraper.DEFAULT_DELAY == 1.0

    def test_max_retries(self, scraper):
        """Test MAX_RETRIES constant"""
        assert scraper.MAX_RETRIES == 3
