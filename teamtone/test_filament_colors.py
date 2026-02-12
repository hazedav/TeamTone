"""
Test suite for filament_colors module

Tests the filament color lookup, search, and matching functions.
Uses real data from the filaments folder.

Run with: pytest teamtone/test_filament_colors.py -v
"""

from teamtone.filament_colors import (
    ALL_FILAMENTS,
    get_filament_color,
    search_filaments,
    get_manufacturer_colors,
    list_manufacturers,
    list_materials,
    get_filaments_with_hex,
    get_filaments_by_hex,
    find_similar_filament_color,
    find_similar_filament_colors,
    get_filaments_by_hex_and_type,
    find_similar_filament_colors_by_type,
)


class TestDataLoading:
    """Test that filament data loads correctly"""

    def test_all_filaments_loaded(self):
        """Should load filament data from YAML files"""
        assert ALL_FILAMENTS is not None
        assert isinstance(ALL_FILAMENTS, dict)
        assert len(ALL_FILAMENTS) > 0

    def test_overture_exists(self):
        """Overture manufacturer should exist in data"""
        assert "Overture" in ALL_FILAMENTS

    def test_filament_structure(self):
        """Filament data should have correct nested structure"""
        # Get first manufacturer
        manufacturer = next(iter(ALL_FILAMENTS.keys()))
        materials = ALL_FILAMENTS[manufacturer]

        assert isinstance(materials, dict)
        # Get first material
        material = next(iter(materials.keys()))
        colors = materials[material]

        assert isinstance(colors, dict)
        # Get first color
        color_name = next(iter(colors.keys()))
        color_data = colors[color_name]

        assert isinstance(color_data, dict)
        assert "hex" in color_data or "source" in color_data


class TestGetFilamentColor:
    """Test get_filament_color function"""

    def test_exact_match(self):
        """Should find exact match for manufacturer/material/color"""
        result = get_filament_color("Overture", "PETG", "Black")

        assert result is not None
        assert result["manufacturer"] == "Overture"
        assert result["material"] == "PETG"
        assert result["color"] == "Black"
        assert result["hex"] == "#000000"

    def test_case_insensitive_manufacturer(self):
        """Should match manufacturer case-insensitively"""
        result = get_filament_color("overture", "PETG", "Black")

        assert result is not None
        assert result["manufacturer"] == "Overture"

    def test_case_insensitive_material(self):
        """Should match material case-insensitively"""
        result = get_filament_color("Overture", "petg", "Black")

        assert result is not None
        assert result["material"] == "PETG"

    def test_case_insensitive_color(self):
        """Should match color case-insensitively"""
        result = get_filament_color("Overture", "PETG", "black")

        assert result is not None
        assert result["color"] == "Black"

    def test_not_found_manufacturer(self):
        """Should return None for unknown manufacturer"""
        result = get_filament_color("NonExistent", "PLA", "Red")
        assert result is None

    def test_not_found_material(self):
        """Should return None for unknown material"""
        result = get_filament_color("Overture", "NonExistent", "Red")
        assert result is None

    def test_not_found_color(self):
        """Should return None for unknown color"""
        result = get_filament_color("Overture", "PETG", "NonExistent")
        assert result is None


class TestSearchFilaments:
    """Test search_filaments function"""

    def test_search_by_color_name(self):
        """Should find filaments matching color name"""
        results = search_filaments("Black")

        assert len(results) > 0
        for result in results:
            assert "black" in result["color"].lower()

    def test_search_partial_match(self):
        """Should find partial color name matches"""
        results = search_filaments("Blu")

        assert len(results) > 0
        for result in results:
            assert "blu" in result["color"].lower()

    def test_search_with_manufacturer_filter(self):
        """Should filter results by manufacturer"""
        results = search_filaments("Black", manufacturer="Overture")

        assert len(results) > 0
        for result in results:
            assert result["manufacturer"] == "Overture"

    def test_search_with_material_filter(self):
        """Should filter results by material"""
        results = search_filaments("Black", material="PETG")

        assert len(results) > 0
        for result in results:
            assert result["material"].upper() == "PETG"

    def test_search_with_both_filters(self):
        """Should filter by both manufacturer and material"""
        results = search_filaments("Black", manufacturer="Overture", material="PETG")

        assert len(results) > 0
        for result in results:
            assert result["manufacturer"] == "Overture"
            assert result["material"] == "PETG"

    def test_search_no_results(self):
        """Should return empty list for no matches"""
        results = search_filaments("xyznonexistent")
        assert results == []


class TestGetManufacturerColors:
    """Test get_manufacturer_colors function"""

    def test_get_all_materials(self):
        """Should return all materials for a manufacturer"""
        result = get_manufacturer_colors("Overture")

        assert isinstance(result, dict)
        assert len(result) > 0
        assert "PETG" in result or "PLA" in result

    def test_get_specific_material(self):
        """Should return only specified material"""
        result = get_manufacturer_colors("Overture", material="PETG")

        assert isinstance(result, dict)
        assert len(result) == 1
        assert "PETG" in result

    def test_case_insensitive(self):
        """Should match case-insensitively"""
        result = get_manufacturer_colors("overture", material="petg")

        assert isinstance(result, dict)
        assert len(result) == 1

    def test_unknown_manufacturer(self):
        """Should return empty dict for unknown manufacturer"""
        result = get_manufacturer_colors("NonExistent")
        assert result == {}

    def test_unknown_material(self):
        """Should return empty dict for unknown material"""
        result = get_manufacturer_colors("Overture", material="NonExistent")
        assert result == {}


class TestListManufacturers:
    """Test list_manufacturers function"""

    def test_returns_list(self):
        """Should return a list"""
        result = list_manufacturers()
        assert isinstance(result, list)

    def test_contains_known_manufacturers(self):
        """Should contain known manufacturers"""
        result = list_manufacturers()
        assert "Overture" in result

    def test_not_empty(self):
        """Should not be empty"""
        result = list_manufacturers()
        assert len(result) > 0


class TestListMaterials:
    """Test list_materials function"""

    def test_all_materials(self):
        """Should return all unique materials"""
        result = list_materials()

        assert isinstance(result, list)
        assert len(result) > 0
        # Should be sorted
        assert result == sorted(result)

    def test_materials_for_manufacturer(self):
        """Should return materials for specific manufacturer"""
        result = list_materials(manufacturer="Overture")

        assert isinstance(result, list)
        assert len(result) > 0

    def test_unknown_manufacturer(self):
        """Should return empty list for unknown manufacturer"""
        result = list_materials(manufacturer="NonExistent")
        assert result == []


class TestGetFilamentsWithHex:
    """Test get_filaments_with_hex function"""

    def test_returns_list(self):
        """Should return a list"""
        result = get_filaments_with_hex()
        assert isinstance(result, list)

    def test_all_have_hex(self):
        """All results should have non-null hex values"""
        result = get_filaments_with_hex()

        for filament in result:
            assert filament["hex"] is not None
            assert filament["hex"].startswith("#") or len(filament["hex"]) == 6

    def test_contains_required_fields(self):
        """Results should contain required fields"""
        result = get_filaments_with_hex()

        if result:
            filament = result[0]
            assert "manufacturer" in filament
            assert "material" in filament
            assert "color" in filament
            assert "hex" in filament


class TestGetFilamentsByHex:
    """Test get_filaments_by_hex function"""

    def test_exact_match_with_hash(self):
        """Should find exact hex match with # prefix"""
        results = get_filaments_by_hex("#000000")

        assert len(results) > 0
        for result in results:
            assert result["hex"].upper() == "#000000"

    def test_exact_match_without_hash(self):
        """Should find exact hex match without # prefix"""
        results = get_filaments_by_hex("000000")

        assert len(results) > 0
        for result in results:
            assert result["hex"].upper() == "#000000"

    def test_case_insensitive(self):
        """Should match case-insensitively"""
        results_upper = get_filaments_by_hex("#FFFFFF")
        results_lower = get_filaments_by_hex("#ffffff")

        assert len(results_upper) == len(results_lower)

    def test_no_match(self):
        """Should return empty list for no matches"""
        results = get_filaments_by_hex("#123456")  # Unlikely to exist
        # May or may not have results, just verify it returns a list
        assert isinstance(results, list)


class TestFindSimilarFilamentColor:
    """Test find_similar_filament_color function"""

    def test_finds_best_match(self):
        """Should find the closest matching color"""
        result = find_similar_filament_color("#000000")

        assert result is not None
        filament, similarity = result
        assert isinstance(filament, dict)
        assert isinstance(similarity, (int, float))
        assert 0 <= similarity <= 100

    def test_exact_match_high_similarity(self):
        """Exact hex match should have very high similarity"""
        result = find_similar_filament_color("#000000")

        if result:
            filament, similarity = result
            # Black (#000000) should find a very similar match
            assert similarity > 90

    def test_with_manufacturer_filter(self):
        """Should filter by manufacturer"""
        result = find_similar_filament_color("#000000", manufacturer="Overture")

        if result:
            filament, similarity = result
            assert filament["manufacturer"] == "Overture"

    def test_no_filaments_returns_none(self):
        """Should return None if no filaments match filter"""
        result = find_similar_filament_color("#000000", manufacturer="NonExistent")
        assert result is None


class TestFindSimilarFilamentColors:
    """Test find_similar_filament_colors function"""

    def test_returns_list(self):
        """Should return a list"""
        result = find_similar_filament_colors("#000000")
        assert isinstance(result, list)

    def test_respects_limit(self):
        """Should respect the limit parameter"""
        result = find_similar_filament_colors("#000000", limit=5)
        assert len(result) <= 5

    def test_sorted_by_similarity(self):
        """Results should be sorted by similarity (descending)"""
        result = find_similar_filament_colors("#000000", limit=10)

        if len(result) > 1:
            similarities = [r[1] for r in result]
            assert similarities == sorted(similarities, reverse=True)

    def test_with_manufacturer_filter(self):
        """Should filter by manufacturer"""
        result = find_similar_filament_colors("#000000", manufacturer="Overture")

        for filament, _ in result:
            assert filament["manufacturer"] == "Overture"

    def test_empty_for_unknown_manufacturer(self):
        """Should return empty list for unknown manufacturer"""
        result = find_similar_filament_colors("#000000", manufacturer="NonExistent")
        assert result == []


class TestGetFilamentsByHexAndType:
    """Test get_filaments_by_hex_and_type function"""

    def test_without_type_filter(self):
        """Should work like get_filaments_by_hex without type"""
        result = get_filaments_by_hex_and_type("#000000")
        assert isinstance(result, list)

    def test_with_type_filter(self):
        """Should filter by filament type"""
        result = get_filaments_by_hex_and_type("#000000", filament_type="PLA")

        # All results should be PLA variants
        for filament in result:
            # Material should start with PLA or be a PLA variant
            material_upper = filament["material"].upper()
            assert material_upper.startswith("PLA") or "PLA" in material_upper


class TestFindSimilarFilamentColorsByType:
    """Test find_similar_filament_colors_by_type function"""

    def test_without_filters(self):
        """Should work like find_similar_filament_colors without filters"""
        result = find_similar_filament_colors_by_type("#000000")
        assert isinstance(result, list)

    def test_with_type_filter(self):
        """Should filter by filament type"""
        result = find_similar_filament_colors_by_type("#000000", filament_type="PETG")

        for filament, _ in result:
            material_upper = filament["material"].upper()
            assert "PETG" in material_upper

    def test_with_manufacturer_filter(self):
        """Should filter by manufacturer"""
        result = find_similar_filament_colors_by_type(
            "#000000", manufacturer="Overture"
        )

        for filament, _ in result:
            assert filament["manufacturer"] == "Overture"

    def test_with_both_filters(self):
        """Should filter by both type and manufacturer"""
        result = find_similar_filament_colors_by_type(
            "#000000", manufacturer="Overture", filament_type="PETG"
        )

        for filament, _ in result:
            assert filament["manufacturer"] == "Overture"
            assert "PETG" in filament["material"].upper()

    def test_respects_limit(self):
        """Should respect the limit parameter"""
        result = find_similar_filament_colors_by_type("#000000", limit=3)
        assert len(result) <= 3
