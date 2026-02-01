"""
Test suite for FilamentProfilesScraper

Tests the parser logic using small, focused HTML fixtures.
Individual scraper tests should not rely on large checked-in HTML files.

Run with: pytest teamtone/fetch/filament_sites/test_filamentprofiles.py -v
"""

import pytest
from bs4 import BeautifulSoup

from .filamentprofiles import FilamentProfilesScraper


@pytest.fixture
def scraper():
    """Create FilamentProfilesScraper instance"""
    return FilamentProfilesScraper()


def make_script_html(filament_json_entries: list[str]) -> str:
    """
    Helper to create HTML with embedded Next.js script containing filament data.

    The 3dfilamentprofiles.com site embeds JSON in script tags with escaped quotes.
    Format: \\"field\\":\\"value\\"
    """
    json_content = ",".join(filament_json_entries)
    return f"""
    <html>
    <head>
        <script>
            self.__next_f.push([1,"[{json_content}]"])
        </script>
    </head>
    <body></body>
    </html>
    """


def make_filament_entry(
    id: int = 1,
    brand_name: str = "TestBrand",
    material: str = "PLA",
    material_type: str = "",
    color: str = "Red",
    rgb: str = "#FF0000",
    website: str = None,
    asin: str = None,
) -> str:
    """
    Create a single escaped JSON filament entry matching the site's format.
    """
    parts = [
        f'\\"id\\":{id}',
        f'\\"brand_name\\":\\"{brand_name}\\"',
        f'\\"material\\":\\"{material}\\"',
        f'\\"material_type\\":\\"{material_type}\\"',
        f'\\"color\\":\\"{color}\\"',
        f'\\"rgb\\":\\"{rgb}\\"',
    ]

    if website:
        parts.append(f'\\"website\\":\\"{website}\\"')

    if asin:
        parts.append(f'\\"price_data\\":{{\\"bad\\":\\"{asin}\\"}}')

    return "{" + ",".join(parts) + "}"


class TestFilamentParser:
    """Test the _parse_filaments method"""

    def test_parses_single_filament(self, scraper):
        """Should parse a single filament entry"""
        html = make_script_html(
            [
                make_filament_entry(
                    brand_name="Hatchbox",
                    material="PLA",
                    color="True Black",
                    rgb="#1A1A1A",
                )
            ]
        )
        soup = BeautifulSoup(html, "html.parser")

        filaments = scraper._parse_filaments(soup)

        assert len(filaments) == 1
        assert filaments[0]["manufacturer"] == "Hatchbox"
        assert filaments[0]["material"] == "PLA"
        assert filaments[0]["color"] == "True Black"
        assert filaments[0]["hex"] == "#1A1A1A"

    def test_parses_multiple_filaments(self, scraper):
        """Should parse multiple filament entries"""
        html = make_script_html(
            [
                make_filament_entry(
                    id=1, brand_name="Hatchbox", color="Black", rgb="#000000"
                ),
                make_filament_entry(
                    id=2, brand_name="eSUN", color="White", rgb="#FFFFFF"
                ),
                make_filament_entry(
                    id=3, brand_name="Overture", color="Red", rgb="#FF0000"
                ),
            ]
        )
        soup = BeautifulSoup(html, "html.parser")

        filaments = scraper._parse_filaments(soup)

        assert len(filaments) == 3
        manufacturers = {f["manufacturer"] for f in filaments}
        assert manufacturers == {"Hatchbox", "eSUN", "Overture"}

    def test_extracts_website_link(self, scraper):
        """Should extract website URL when present"""
        html = make_script_html(
            [
                make_filament_entry(
                    brand_name="Hatchbox",
                    color="Black",
                    rgb="#000000",
                    website="https://www.hatchbox3d.com/products/pla-black",
                )
            ]
        )
        soup = BeautifulSoup(html, "html.parser")

        filaments = scraper._parse_filaments(soup)

        assert len(filaments) == 1
        assert filaments[0]["link"] == "https://www.hatchbox3d.com/products/pla-black"

    def test_extracts_amazon_link_from_asin(self, scraper):
        """Should create Amazon link from ASIN when no website"""
        html = make_script_html(
            [
                make_filament_entry(
                    brand_name="Hatchbox",
                    color="Black",
                    rgb="#000000",
                    asin="B00J0ECR5I",
                )
            ]
        )
        soup = BeautifulSoup(html, "html.parser")

        filaments = scraper._parse_filaments(soup)

        assert len(filaments) == 1
        assert filaments[0]["link"] == "https://www.amazon.com/dp/B00J0ECR5I"

    def test_website_takes_priority_over_asin(self, scraper):
        """Website URL should be preferred over Amazon ASIN"""
        html = make_script_html(
            [
                make_filament_entry(
                    brand_name="Hatchbox",
                    color="Black",
                    rgb="#000000",
                    website="https://www.hatchbox3d.com/products/pla-black",
                    asin="B00J0ECR5I",
                )
            ]
        )
        soup = BeautifulSoup(html, "html.parser")

        filaments = scraper._parse_filaments(soup)

        assert len(filaments) == 1
        assert filaments[0]["link"] == "https://www.hatchbox3d.com/products/pla-black"

    def test_combines_material_and_material_type(self, scraper):
        """Should combine material and material_type when type is meaningful"""
        html = make_script_html(
            [
                make_filament_entry(
                    brand_name="Hatchbox",
                    material="PLA",
                    material_type="Silk",
                    color="Gold",
                    rgb="#FFD700",
                )
            ]
        )
        soup = BeautifulSoup(html, "html.parser")

        filaments = scraper._parse_filaments(soup)

        assert len(filaments) == 1
        assert filaments[0]["material"] == "PLA Silk"

    def test_ignores_empty_material_type(self, scraper):
        """Should not append empty material_type"""
        html = make_script_html(
            [
                make_filament_entry(
                    brand_name="Hatchbox",
                    material="PETG",
                    material_type="",
                    color="Blue",
                    rgb="#0000FF",
                )
            ]
        )
        soup = BeautifulSoup(html, "html.parser")

        filaments = scraper._parse_filaments(soup)

        assert len(filaments) == 1
        assert filaments[0]["material"] == "PETG"

    def test_ignores_other_material_type(self, scraper):
        """Should not append '-- Other --' material_type"""
        html = make_script_html(
            [
                make_filament_entry(
                    brand_name="Hatchbox",
                    material="ABS",
                    material_type="-- Other --",
                    color="Green",
                    rgb="#00FF00",
                )
            ]
        )
        soup = BeautifulSoup(html, "html.parser")

        filaments = scraper._parse_filaments(soup)

        assert len(filaments) == 1
        assert filaments[0]["material"] == "ABS"

    def test_returns_empty_list_for_no_data(self, scraper):
        """Should return empty list when no filament data found"""
        html = "<html><body>No data here</body></html>"
        soup = BeautifulSoup(html, "html.parser")

        filaments = scraper._parse_filaments(soup)

        assert filaments == []


class TestManufacturerFiltering:
    """Test that dedicated scraper manufacturers are filtered out"""

    def test_skips_polymaker(self, scraper):
        """Should skip Polymaker (has dedicated scraper)"""
        html = make_script_html(
            [
                make_filament_entry(
                    brand_name="Polymaker", color="Black", rgb="#000000"
                ),
                make_filament_entry(
                    brand_name="Hatchbox", color="Black", rgb="#000000"
                ),
            ]
        )
        soup = BeautifulSoup(html, "html.parser")

        filaments = scraper._parse_filaments(soup)

        assert len(filaments) == 1
        assert filaments[0]["manufacturer"] == "Hatchbox"

    def test_skips_sunlu(self, scraper):
        """Should skip SUNLU (has dedicated scraper)"""
        html = make_script_html(
            [
                make_filament_entry(brand_name="SUNLU", color="White", rgb="#FFFFFF"),
                make_filament_entry(brand_name="eSUN", color="White", rgb="#FFFFFF"),
            ]
        )
        soup = BeautifulSoup(html, "html.parser")

        filaments = scraper._parse_filaments(soup)

        assert len(filaments) == 1
        assert filaments[0]["manufacturer"] == "eSUN"

    def test_skips_case_insensitive(self, scraper):
        """Manufacturer filtering should be case insensitive"""
        html = make_script_html(
            [
                make_filament_entry(brand_name="polymaker", color="Red", rgb="#FF0000"),
                make_filament_entry(brand_name="sunlu", color="Red", rgb="#FF0000"),
                make_filament_entry(brand_name="Overture", color="Red", rgb="#FF0000"),
            ]
        )
        soup = BeautifulSoup(html, "html.parser")

        filaments = scraper._parse_filaments(soup)

        assert len(filaments) == 1
        assert filaments[0]["manufacturer"] == "Overture"


class TestScraperProperties:
    """Test scraper property methods"""

    def test_site_name(self, scraper):
        """Test site_name property"""
        assert scraper.site_name == "3dfilamentprofiles.com"

    def test_site_url(self, scraper):
        """Test site_url property"""
        assert scraper.site_url == "https://3dfilamentprofiles.com"

    def test_user_agent_set(self, scraper):
        """Test that USER_AGENT is set"""
        assert "Chrome" in scraper.USER_AGENT

    def test_default_delay(self, scraper):
        """Test DEFAULT_DELAY is reasonable"""
        assert scraper.DEFAULT_DELAY >= 0.5
        assert scraper.DEFAULT_DELAY <= 5.0
