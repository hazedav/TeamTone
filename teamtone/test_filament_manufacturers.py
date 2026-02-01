"""
Test suite for filament_manufacturers module

Run with: pytest teamtone/test_filament_manufacturers.py -v
"""

import pytest

from teamtone.filament_manufacturers import (
    TOP_MANUFACTURERS,
    is_top_manufacturer,
    get_manufacturer_rank,
)


class TestTopManufacturersList:
    """Test the TOP_MANUFACTURERS list is properly loaded"""

    def test_list_is_not_empty(self):
        """TOP_MANUFACTURERS should be loaded from YAML"""
        assert len(TOP_MANUFACTURERS) > 0

    def test_list_has_10_manufacturers(self):
        """Should have exactly 10 top manufacturers"""
        assert len(TOP_MANUFACTURERS) == 10

    def test_polymaker_is_first(self):
        """Polymaker should be the #1 manufacturer"""
        assert TOP_MANUFACTURERS[0] == "Polymaker"

    def test_atomic_filament_is_last(self):
        """Atomic Filament should be the #10 manufacturer"""
        assert TOP_MANUFACTURERS[9] == "Atomic Filament"

    def test_expected_manufacturers_in_list(self):
        """All expected manufacturers should be in the list"""
        expected = [
            "Polymaker",
            "Hatchbox",
            "Esun",
            "Prusament",
            "Sunlu",
            "Overture",
            "Matterhackers",
            "Colorfabb",
            "Eryone",
            "Atomic Filament",
        ]
        assert TOP_MANUFACTURERS == expected


class TestIsTopManufacturer:
    """Test is_top_manufacturer function"""

    @pytest.mark.parametrize(
        "manufacturer",
        [
            "Polymaker",
            "Hatchbox",
            "Esun",
            "Prusament",
            "Sunlu",
            "Overture",
            "Matterhackers",
            "Colorfabb",
            "Eryone",
            "Atomic Filament",
        ],
    )
    def test_all_top_manufacturers_return_true(self, manufacturer):
        """All top manufacturers should return True"""
        assert is_top_manufacturer(manufacturer) is True

    def test_non_top_manufacturer_returns_false(self):
        """Non-top manufacturers should return False"""
        assert is_top_manufacturer("Unknown Brand") is False
        assert is_top_manufacturer("Random Filament Co") is False
        assert is_top_manufacturer("Generic PLA") is False

    @pytest.mark.parametrize(
        "manufacturer",
        [
            "polymaker",
            "POLYMAKER",
            "PoLyMaKeR",
            "hatchbox",
            "HATCHBOX",
            "esun",
            "ESUN",
        ],
    )
    def test_case_insensitive_matching(self, manufacturer):
        """Matching should be case insensitive"""
        assert is_top_manufacturer(manufacturer) is True

    @pytest.mark.parametrize(
        "manufacturer",
        [
            "Polymaker PLA",
            "Polymaker PETG Pro",
            "Hatchbox ABS",
            "eSUN Silk PLA",
            "Prusament Galaxy Black",
        ],
    )
    def test_partial_match_manufacturer_in_string(self, manufacturer):
        """Should match when top manufacturer name is part of string"""
        assert is_top_manufacturer(manufacturer) is True

    def test_empty_string_matches_due_to_substring_logic(self):
        """Empty string matches because '' in 'polymaker' is True in Python"""
        # Note: This is a quirk of the substring matching logic
        assert is_top_manufacturer("") is True


class TestGetManufacturerRank:
    """Test get_manufacturer_rank function"""

    @pytest.mark.parametrize(
        "manufacturer,expected_rank",
        [
            ("Polymaker", 1),
            ("Hatchbox", 2),
            ("Esun", 3),
            ("Prusament", 4),
            ("Sunlu", 5),
            ("Overture", 6),
            ("Matterhackers", 7),
            ("Colorfabb", 8),
            ("Eryone", 9),
            ("Atomic Filament", 10),
        ],
    )
    def test_correct_rank_for_each_manufacturer(self, manufacturer, expected_rank):
        """Each manufacturer should have the correct rank"""
        assert get_manufacturer_rank(manufacturer) == expected_rank

    def test_non_top_manufacturer_returns_999(self):
        """Non-top manufacturers should return 999"""
        assert get_manufacturer_rank("Unknown Brand") == 999
        assert get_manufacturer_rank("Random Filament Co") == 999

    @pytest.mark.parametrize(
        "manufacturer,expected_rank",
        [
            ("polymaker", 1),
            ("POLYMAKER", 1),
            ("hatchbox", 2),
            ("HATCHBOX", 2),
        ],
    )
    def test_case_insensitive_ranking(self, manufacturer, expected_rank):
        """Ranking should be case insensitive"""
        assert get_manufacturer_rank(manufacturer) == expected_rank

    @pytest.mark.parametrize(
        "manufacturer,expected_rank",
        [
            ("Polymaker PLA Pro", 1),
            ("Hatchbox True Black", 2),
            ("eSUN Silk Rainbow", 3),
        ],
    )
    def test_partial_match_ranking(self, manufacturer, expected_rank):
        """Should return correct rank for partial matches"""
        assert get_manufacturer_rank(manufacturer) == expected_rank

    def test_empty_string_matches_first_due_to_substring_logic(self):
        """Empty string matches first manufacturer because '' in 'polymaker' is True"""
        # Note: This is a quirk of the substring matching logic
        assert get_manufacturer_rank("") == 1
