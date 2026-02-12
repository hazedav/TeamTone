"""
Test suite for compare_colors module

Tests color conversion and comparison functions.

Run with: pytest teamtone/test_compare_colors.py -v
"""

import pytest

from teamtone.compare_colors import (
    hex_to_rgb,
    rgb_to_hex,
    rgb_to_lab,
    euclidean_distance_rgb,
    weighted_rgb_distance,
    delta_e_cie76,
    delta_e_cie94,
    color_similarity_percentage,
    compare_colors,
    find_closest_color,
)


class TestHexToRgb:
    """Test hex_to_rgb function"""

    def test_black(self):
        """#000000 should convert to (0, 0, 0)"""
        assert hex_to_rgb("#000000") == (0, 0, 0)

    def test_white(self):
        """#FFFFFF should convert to (255, 255, 255)"""
        assert hex_to_rgb("#FFFFFF") == (255, 255, 255)

    def test_red(self):
        """#FF0000 should convert to (255, 0, 0)"""
        assert hex_to_rgb("#FF0000") == (255, 0, 0)

    def test_green(self):
        """#00FF00 should convert to (0, 255, 0)"""
        assert hex_to_rgb("#00FF00") == (0, 255, 0)

    def test_blue(self):
        """#0000FF should convert to (0, 0, 255)"""
        assert hex_to_rgb("#0000FF") == (0, 0, 255)

    def test_without_hash(self):
        """Should work without # prefix"""
        assert hex_to_rgb("FF0000") == (255, 0, 0)

    def test_lowercase(self):
        """Should work with lowercase hex"""
        assert hex_to_rgb("#ff0000") == (255, 0, 0)

    def test_mixed_case(self):
        """Should work with mixed case"""
        assert hex_to_rgb("#Ff00fF") == (255, 0, 255)

    @pytest.mark.parametrize(
        "hex_code,expected",
        [
            ("#808080", (128, 128, 128)),  # Gray
            ("#C0C0C0", (192, 192, 192)),  # Silver
            ("#800000", (128, 0, 0)),  # Maroon
            ("#FFA500", (255, 165, 0)),  # Orange
            ("#552583", (85, 37, 131)),  # Lakers purple
        ],
    )
    def test_various_colors(self, hex_code, expected):
        """Test various color conversions"""
        assert hex_to_rgb(hex_code) == expected


class TestRgbToHex:
    """Test rgb_to_hex function"""

    def test_black(self):
        """(0, 0, 0) should convert to #000000"""
        assert rgb_to_hex(0, 0, 0) == "#000000"

    def test_white(self):
        """(255, 255, 255) should convert to #ffffff"""
        result = rgb_to_hex(255, 255, 255)
        assert result.upper() == "#FFFFFF"

    def test_red(self):
        """(255, 0, 0) should convert to #ff0000"""
        result = rgb_to_hex(255, 0, 0)
        assert result.upper() == "#FF0000"

    def test_roundtrip(self):
        """Converting hex -> rgb -> hex should preserve the value"""
        original = "#A5B7C9"
        r, g, b = hex_to_rgb(original)
        result = rgb_to_hex(r, g, b)
        assert result.upper() == original


class TestRgbToLab:
    """Test rgb_to_lab function"""

    def test_black(self):
        """Black should have L=0"""
        L, a, b = rgb_to_lab(0, 0, 0)
        assert L == pytest.approx(0, abs=0.1)

    def test_white(self):
        """White should have L=100"""
        L, a, b = rgb_to_lab(255, 255, 255)
        assert L == pytest.approx(100, abs=0.5)

    def test_gray(self):
        """Gray should have a=0 and b=0 (neutral)"""
        L, a, b = rgb_to_lab(128, 128, 128)
        # Gray should be neutral (a and b close to 0)
        assert abs(a) < 1
        assert abs(b) < 1

    def test_red_positive_a(self):
        """Red should have positive a value"""
        L, a, b = rgb_to_lab(255, 0, 0)
        assert a > 0  # Red is positive on a axis

    def test_green_negative_a(self):
        """Green should have negative a value"""
        L, a, b = rgb_to_lab(0, 255, 0)
        assert a < 0  # Green is negative on a axis

    def test_blue_negative_b(self):
        """Blue should have negative b value"""
        L, a, b = rgb_to_lab(0, 0, 255)
        assert b < 0  # Blue is negative on b axis

    def test_yellow_positive_b(self):
        """Yellow should have positive b value"""
        L, a, b = rgb_to_lab(255, 255, 0)
        assert b > 0  # Yellow is positive on b axis


class TestEuclideanDistanceRgb:
    """Test euclidean_distance_rgb function"""

    def test_identical_colors(self):
        """Identical colors should have distance 0"""
        assert euclidean_distance_rgb("#FF0000", "#FF0000") == 0

    def test_black_white(self):
        """Black to white should have maximum distance"""
        distance = euclidean_distance_rgb("#000000", "#FFFFFF")
        # Max is sqrt(255^2 * 3) ≈ 441.67
        assert distance == pytest.approx(441.67, rel=0.01)

    def test_symmetric(self):
        """Distance should be symmetric"""
        d1 = euclidean_distance_rgb("#FF0000", "#00FF00")
        d2 = euclidean_distance_rgb("#00FF00", "#FF0000")
        assert d1 == d2

    def test_triangle_inequality(self):
        """Should satisfy triangle inequality"""
        # d(A, C) <= d(A, B) + d(B, C)
        d_ac = euclidean_distance_rgb("#FF0000", "#0000FF")
        d_ab = euclidean_distance_rgb("#FF0000", "#00FF00")
        d_bc = euclidean_distance_rgb("#00FF00", "#0000FF")
        assert d_ac <= d_ab + d_bc + 0.001  # Small tolerance for float errors


class TestWeightedRgbDistance:
    """Test weighted_rgb_distance function"""

    def test_identical_colors(self):
        """Identical colors should have distance 0"""
        assert weighted_rgb_distance("#FF0000", "#FF0000") == 0

    def test_symmetric(self):
        """Distance should be symmetric"""
        d1 = weighted_rgb_distance("#FF0000", "#00FF00")
        d2 = weighted_rgb_distance("#00FF00", "#FF0000")
        assert d1 == pytest.approx(d2, rel=0.01)

    def test_green_weighted_more(self):
        """Green channel differences should have more weight"""
        # Same magnitude change in different channels
        d_green = weighted_rgb_distance("#808080", "#80FF80")  # Green change
        d_blue = weighted_rgb_distance("#808080", "#8080FF")  # Blue change
        # Green should have more weight (4.0 vs ~2.5 for blue)
        assert d_green > d_blue


class TestDeltaECie76:
    """Test delta_e_cie76 function"""

    def test_identical_colors(self):
        """Identical colors should have Delta E = 0"""
        assert delta_e_cie76("#FF0000", "#FF0000") == 0

    def test_similar_colors_low_delta_e(self):
        """Very similar colors should have low Delta E"""
        # Two very similar shades of red
        delta_e = delta_e_cie76("#FF0000", "#FE0101")
        assert delta_e < 5  # Should be perceptible at a glance but similar

    def test_different_colors_high_delta_e(self):
        """Very different colors should have high Delta E"""
        delta_e = delta_e_cie76("#FF0000", "#00FF00")
        assert delta_e > 50  # Red and green are very different

    def test_symmetric(self):
        """Delta E should be symmetric"""
        d1 = delta_e_cie76("#FF0000", "#0000FF")
        d2 = delta_e_cie76("#0000FF", "#FF0000")
        assert d1 == pytest.approx(d2, rel=0.001)

    def test_black_white_high_delta_e(self):
        """Black and white should have high Delta E (lightness difference)"""
        delta_e = delta_e_cie76("#000000", "#FFFFFF")
        assert delta_e > 90  # L goes from 0 to 100


class TestDeltaECie94:
    """Test delta_e_cie94 function"""

    def test_identical_colors(self):
        """Identical colors should have Delta E = 0"""
        assert delta_e_cie94("#FF0000", "#FF0000") == 0

    def test_asymmetric_by_design(self):
        """CIE94 is intentionally asymmetric (uses reference color's chroma)"""
        d1 = delta_e_cie94("#FF0000", "#0000FF")
        d2 = delta_e_cie94("#0000FF", "#FF0000")
        # Both should be positive and reasonably close but not equal
        assert d1 > 0
        assert d2 > 0
        # They should be in the same ballpark (within 50% of each other)
        assert abs(d1 - d2) / max(d1, d2) < 0.5

    def test_positive_value(self):
        """Delta E should always be positive"""
        delta_e = delta_e_cie94("#123456", "#654321")
        assert delta_e >= 0


class TestColorSimilarityPercentage:
    """Test color_similarity_percentage function"""

    def test_identical_colors(self):
        """Identical colors should be 100% similar"""
        similarity = color_similarity_percentage("#FF0000", "#FF0000")
        assert similarity == 100

    def test_range_0_to_100(self):
        """Similarity should always be between 0 and 100"""
        similarity = color_similarity_percentage("#000000", "#FFFFFF")
        assert 0 <= similarity <= 100

    def test_very_different_colors(self):
        """Very different colors should have low similarity"""
        similarity = color_similarity_percentage("#000000", "#FFFFFF")
        assert similarity < 50

    def test_similar_colors(self):
        """Similar colors should have high similarity"""
        similarity = color_similarity_percentage("#FF0000", "#FE0000")
        assert similarity > 95

    @pytest.mark.parametrize(
        "method",
        ["delta_e_cie76", "delta_e_cie94", "rgb", "weighted_rgb"],
    )
    def test_all_methods(self, method):
        """All methods should return valid similarity"""
        similarity = color_similarity_percentage("#FF0000", "#00FF00", method=method)
        assert 0 <= similarity <= 100

    def test_invalid_method(self):
        """Invalid method should raise ValueError"""
        with pytest.raises(ValueError, match="Unknown method"):
            color_similarity_percentage("#FF0000", "#00FF00", method="invalid")

    def test_symmetric(self):
        """Similarity should be symmetric"""
        s1 = color_similarity_percentage("#FF0000", "#00FF00")
        s2 = color_similarity_percentage("#00FF00", "#FF0000")
        assert s1 == pytest.approx(s2, rel=0.001)


class TestCompareColors:
    """Test compare_colors function"""

    def test_returns_dict(self):
        """Should return a dictionary"""
        result = compare_colors("#FF0000", "#00FF00")
        assert isinstance(result, dict)

    def test_contains_all_metrics(self):
        """Should contain all expected metrics"""
        result = compare_colors("#FF0000", "#00FF00")

        assert "rgb_distance" in result
        assert "weighted_rgb_distance" in result
        assert "delta_e_cie76" in result
        assert "delta_e_cie94" in result
        assert "similarity_percentage" in result

    def test_identical_colors(self):
        """Identical colors should have 0 distances and 100% similarity"""
        result = compare_colors("#FF0000", "#FF0000")

        assert result["rgb_distance"] == 0
        assert result["delta_e_cie76"] == 0
        assert result["similarity_percentage"] == 100

    def test_values_are_numeric(self):
        """All values should be numeric"""
        result = compare_colors("#123456", "#654321")

        for key, value in result.items():
            assert isinstance(value, (int, float))


class TestFindClosestColor:
    """Test find_closest_color function"""

    def test_exact_match(self):
        """Should find exact match with 100% similarity"""
        color_list = [
            ("Red", "#FF0000"),
            ("Green", "#00FF00"),
            ("Blue", "#0000FF"),
        ]
        name, hex_val, similarity = find_closest_color("#FF0000", color_list)

        assert name == "Red"
        assert hex_val == "#FF0000"
        assert similarity == 100

    def test_closest_match(self):
        """Should find the closest match"""
        color_list = [
            ("Pure Red", "#FF0000"),
            ("Dark Red", "#800000"),
            ("Green", "#00FF00"),
        ]
        # A slightly different red should match Pure Red or Dark Red
        name, hex_val, similarity = find_closest_color("#FE0000", color_list)

        # Should match Pure Red (closest)
        assert name == "Pure Red"
        assert similarity > 95

    def test_returns_tuple(self):
        """Should return a tuple of (name, hex, similarity)"""
        color_list = [("Black", "#000000")]
        result = find_closest_color("#111111", color_list)

        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_single_color_list(self):
        """Should work with single color list"""
        color_list = [("Only", "#FFFFFF")]
        name, hex_val, similarity = find_closest_color("#000000", color_list)

        assert name == "Only"
        assert hex_val == "#FFFFFF"

    def test_chooses_highest_similarity(self):
        """Should choose color with highest similarity"""
        # Lakers purple
        target = "#552583"
        color_list = [
            ("Lakers Gold", "#FDB927"),
            ("Celtics Green", "#007A33"),
            ("Similar Purple", "#5A2D81"),  # Kings purple - closest
        ]
        name, hex_val, similarity = find_closest_color(target, color_list)

        assert name == "Similar Purple"


class TestColorPerception:
    """Test that color comparisons match human perception"""

    def test_similar_shades_high_similarity(self):
        """Similar shades of the same color should have high similarity"""
        # Two shades of blue
        similarity = color_similarity_percentage("#0000FF", "#0000EE")
        assert similarity > 90

    def test_complementary_colors_low_similarity(self):
        """Complementary colors should have low similarity"""
        # Red and cyan are complementary
        similarity = color_similarity_percentage("#FF0000", "#00FFFF")
        assert similarity < 50

    def test_grayscale_ordering(self):
        """Grayscale colors should order by lightness"""
        # Darker gray should be closer to black than lighter gray
        dark_gray = color_similarity_percentage("#000000", "#333333")
        light_gray = color_similarity_percentage("#000000", "#CCCCCC")
        assert dark_gray > light_gray

    def test_warm_colors_similar(self):
        """Warm colors (red, orange, yellow) should be more similar to each other"""
        red_orange = color_similarity_percentage("#FF0000", "#FF8000")
        red_blue = color_similarity_percentage("#FF0000", "#0000FF")
        assert red_orange > red_blue
