"""
Test suite for FilamentProfilesScraper parser

Run with: pytest teamtone/fetch/filament_sites/test_filamentprofiles.py -v
"""

import pytest
from pathlib import Path
from bs4 import BeautifulSoup

from .filamentprofiles import FilamentProfilesScraper


@pytest.fixture
def html_content():
    """Load the saved HTML file for testing"""
    html_file = Path(__file__).parent.parent / "filaments.html"
    if not html_file.exists():
        pytest.skip(f"HTML file not found: {html_file}")

    with open(html_file, "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def soup(html_content):
    """Parse HTML into BeautifulSoup object"""
    return BeautifulSoup(html_content, "html.parser")


@pytest.fixture
def scraper():
    """Create FilamentProfilesScraper instance"""
    return FilamentProfilesScraper()


@pytest.fixture
def filaments(scraper, soup):
    """Parse filaments from HTML"""
    return scraper._parse_filaments(soup)


class TestFilamentParser:
    """Test the FilamentProfilesScraper parser"""

    def test_filaments_found(self, filaments):
        """Test that filaments are found"""
        assert len(filaments) > 0, "No filaments were parsed from HTML"

    def test_filament_count(self, filaments):
        """Test expected number of filaments"""
        # Adjust this number based on your test HTML
        assert len(filaments) > 100, f"Expected > 100 filaments, got {len(filaments)}"

    def test_filament_structure(self, filaments):
        """Test that each filament has required fields"""
        required_fields = ["manufacturer", "material", "color", "hex"]

        for filament in filaments[:10]:  # Check first 10
            for field in required_fields:
                assert field in filament, (
                    f"Missing field '{field}' in filament: {filament}"
                )
                assert filament[field], (
                    f"Empty value for field '{field}' in filament: {filament}"
                )

    def test_hex_format(self, filaments):
        """Test that hex codes are properly formatted"""
        for filament in filaments[:50]:  # Check first 50
            hex_code = filament["hex"]

            # Should start with # and be 7 characters (#RRGGBB)
            assert hex_code.startswith("#"), f"Hex code should start with #: {hex_code}"
            assert len(hex_code) == 7, f"Hex code should be 7 chars: {hex_code}"

            # Should only contain valid hex characters
            assert all(c in "0123456789ABCDEFabcdef#" for c in hex_code), (
                f"Invalid hex code: {hex_code}"
            )

    def test_manufacturer_names(self, filaments):
        """Test that manufacturer names are non-empty strings"""
        for filament in filaments[:20]:
            manufacturer = filament["manufacturer"]
            assert isinstance(manufacturer, str), (
                f"Manufacturer should be string: {type(manufacturer)}"
            )
            assert len(manufacturer) > 0, "Manufacturer name is empty"

    def test_material_types(self, filaments):
        """Test that material types are valid"""
        common_materials = ["PLA", "PETG", "ABS", "TPU", "NYLON", "ASA"]

        materials_found = set()
        for filament in filaments:
            material = filament["material"].upper()
            materials_found.add(material.split()[0])  # Get base material

        # At least some common materials should be present
        assert any(mat in materials_found for mat in common_materials), (
            f"No common materials found. Got: {materials_found}"
        )

    def test_link_extraction(self, filaments):
        """Test that some filaments have purchase links"""
        filaments_with_links = [f for f in filaments if "link" in f]

        assert len(filaments_with_links) > 0, "No filaments have purchase links"

        # Check link format for first few
        for filament in filaments_with_links[:10]:
            link = filament["link"]
            assert link.startswith("http"), f"Link should start with http: {link}"

    def test_no_duplicates(self, filaments):
        """Test that there are no exact duplicate filaments"""
        seen = set()
        duplicates = []

        for filament in filaments:
            # Create unique key
            key = (
                filament["manufacturer"],
                filament["material"],
                filament["color"],
                filament["hex"],
            )

            if key in seen:
                duplicates.append(key)
            seen.add(key)

        # Some duplicates might be expected, but not too many
        assert len(duplicates) < len(filaments) * 0.1, (
            f"Too many duplicates found: {len(duplicates)}"
        )


class TestSpecificManufacturers:
    """Test parsing of specific manufacturers"""

    def test_abaflex_parsing(self, filaments):
        """Test that Abaflex filaments are parsed correctly"""
        abaflex = [f for f in filaments if "Abaflex" in f["manufacturer"]]

        if not abaflex:
            pytest.skip("Abaflex not found in test data")

        assert len(abaflex) > 0, "Abaflex filaments should be found"

        # Check one specific example if it exists
        transparent = [
            f
            for f in abaflex
            if "PETG" in f["material"] and f["color"] == "Transparent"
        ]

        if transparent:
            filament = transparent[0]
            assert filament["manufacturer"] == "Abaflex"
            assert "PETG" in filament["material"]
            assert filament["hex"] == "#BEC3C6"

    def test_common_manufacturers(self, filaments):
        """Test that common manufacturers are present"""
        manufacturers = {f["manufacturer"] for f in filaments}

        # These are just examples - adjust based on your test data
        common_brands = ["Hatchbox", "eSUN", "Polymaker", "SUNLU", "Overture"]

        # At least some should be present
        found = [brand for brand in common_brands if brand in manufacturers]
        assert len(found) > 0, (
            f"None of the common brands found. Available: {list(manufacturers)[:10]}"
        )


class TestDataQuality:
    """Test data quality and consistency"""

    def test_color_names_non_empty(self, filaments):
        """Test that color names are not empty"""
        for filament in filaments[:30]:
            assert len(filament["color"]) > 0, (
                f"Empty color name for {filament['manufacturer']}"
            )

    def test_hex_codes_unique_per_color(self, filaments):
        """Test that same manufacturer/material/color has same hex"""
        from collections import defaultdict

        color_hex_map = defaultdict(set)

        for filament in filaments:
            key = (filament["manufacturer"], filament["material"], filament["color"])
            color_hex_map[key].add(filament["hex"])

        # Each unique color should have only one hex code
        conflicts = {k: v for k, v in color_hex_map.items() if len(v) > 1}

        # Some variation might be acceptable
        assert len(conflicts) < len(color_hex_map) * 0.05, (
            f"Too many hex conflicts: {len(conflicts)}"
        )

    def test_material_type_combinations(self, filaments):
        """Test that material type combinations make sense"""
        for filament in filaments[:50]:
            material = filament["material"]

            # Basic sanity check - should have at least one word
            assert len(material.split()) >= 1, (
                f"Material type seems invalid: {material}"
            )
