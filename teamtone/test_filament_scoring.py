"""
Test suite for filament_scoring module

Run with: pytest teamtone/test_filament_scoring.py -v
"""

import pytest

from teamtone.filament_scoring import (
    RANK_MULTIPLIER,
    calculate_manufacturer_bonus,
    calculate_weighted_score,
    get_best_top_manufacturer_match,
)


class TestRankMultiplier:
    """Test the rank multiplier constant produces expected behavior"""

    def test_multiplier_gives_5_percent_spread(self):
        """95% #1 manufacturer should just beat 100% #10 manufacturer"""
        # Polymaker (#1) bonus: (11 - 1) * 0.56 = 5.6
        # Atomic (#10) bonus: (11 - 10) * 0.56 = 0.56
        polymaker_score = 95 + (11 - 1) * RANK_MULTIPLIER
        atomic_score = 100 + (11 - 10) * RANK_MULTIPLIER

        assert polymaker_score > atomic_score


class TestCalculateManufacturerBonus:
    """Test manufacturer bonus calculation"""

    @pytest.mark.parametrize(
        "manufacturer,expected_rank,expected_bonus",
        [
            ("Polymaker", 1, (11 - 1) * 0.56),  # 5.6
            ("Hatchbox", 2, (11 - 2) * 0.56),  # 5.04
            ("eSUN", 3, (11 - 3) * 0.56),  # 4.48
            ("Prusament", 4, (11 - 4) * 0.56),  # 3.92
            ("Sunlu", 5, (11 - 5) * 0.56),  # 3.36
            ("Overture", 6, (11 - 6) * 0.56),  # 2.8
            ("MatterHackers", 7, (11 - 7) * 0.56),  # 2.24
            ("ColorFabb", 8, (11 - 8) * 0.56),  # 1.68
            ("Eryone", 9, (11 - 9) * 0.56),  # 1.12
            ("Atomic Filament", 10, (11 - 10) * 0.56),  # 0.56
        ],
    )
    def test_top_manufacturer_bonus(self, manufacturer, expected_rank, expected_bonus):
        """Test bonus calculation for each top manufacturer"""
        bonus = calculate_manufacturer_bonus(manufacturer)
        assert bonus == pytest.approx(expected_bonus, rel=1e-2)

    def test_non_top_manufacturer_gets_zero_bonus(self):
        """Non-top manufacturers should get zero bonus"""
        assert calculate_manufacturer_bonus("Unknown Brand") == 0.0
        assert calculate_manufacturer_bonus("Random Filament Co") == 0.0

    def test_case_insensitive_matching(self):
        """Manufacturer matching should be case insensitive"""
        polymaker_bonus = calculate_manufacturer_bonus("Polymaker")
        assert calculate_manufacturer_bonus("polymaker") == polymaker_bonus
        assert calculate_manufacturer_bonus("POLYMAKER") == polymaker_bonus


class TestCalculateWeightedScore:
    """Test weighted score calculation"""

    def test_similarity_plus_bonus(self):
        """Score should be similarity + manufacturer bonus"""
        # Polymaker bonus is 5.6
        score = calculate_weighted_score(90.0, "Polymaker")
        expected = 90.0 + (11 - 1) * RANK_MULTIPLIER
        assert score == pytest.approx(expected, rel=1e-2)

    def test_non_top_manufacturer_score_equals_similarity(self):
        """Non-top manufacturer score should equal raw similarity"""
        score = calculate_weighted_score(85.5, "Unknown Brand")
        assert score == 85.5

    def test_95_polymaker_beats_100_atomic(self):
        """95% Polymaker should beat 100% Atomic"""
        polymaker_score = calculate_weighted_score(95.0, "Polymaker")
        atomic_score = calculate_weighted_score(100.0, "Atomic Filament")
        assert polymaker_score > atomic_score

    def test_89_polymaker_loses_to_95_atomic(self):
        """89% Polymaker should lose to 95% Atomic (5.04 point spread)"""
        polymaker_score = calculate_weighted_score(89.0, "Polymaker")
        atomic_score = calculate_weighted_score(95.0, "Atomic Filament")
        assert polymaker_score < atomic_score


class TestGetBestTopManufacturerMatch:
    """Test finding best weighted match from top manufacturers"""

    def test_returns_none_for_empty_matches(self):
        """Should return (None, None) for empty matches list"""
        filament, similarity = get_best_top_manufacturer_match([])
        assert filament is None
        assert similarity is None

    def test_returns_none_for_no_top_manufacturers(self):
        """Should return (None, None) when no top manufacturers in matches"""
        matches = [
            ({"manufacturer": "Unknown Brand", "color": "Red"}, 95.0),
            ({"manufacturer": "Random Co", "color": "Blue"}, 90.0),
        ]
        filament, similarity = get_best_top_manufacturer_match(matches)
        assert filament is None
        assert similarity is None

    def test_picks_higher_ranked_manufacturer_at_equal_similarity(self):
        """Should pick higher-ranked manufacturer when similarity is equal"""
        matches = [
            ({"manufacturer": "Atomic Filament", "color": "Red"}, 90.0),
            ({"manufacturer": "Polymaker", "color": "Red"}, 90.0),
        ]
        filament, similarity = get_best_top_manufacturer_match(matches)
        assert filament["manufacturer"] == "Polymaker"
        assert similarity == 90.0

    def test_picks_95_polymaker_over_100_atomic(self):
        """Should pick 95% Polymaker over 100% Atomic"""
        matches = [
            ({"manufacturer": "Atomic Filament", "color": "Red"}, 100.0),
            ({"manufacturer": "Polymaker", "color": "Red"}, 95.0),
        ]
        filament, similarity = get_best_top_manufacturer_match(matches)
        assert filament["manufacturer"] == "Polymaker"
        assert similarity == 95.0

    def test_picks_100_atomic_over_90_polymaker(self):
        """Should pick 100% Atomic over 90% Polymaker (similarity wins)"""
        matches = [
            ({"manufacturer": "Atomic Filament", "color": "Red"}, 100.0),
            ({"manufacturer": "Polymaker", "color": "Red"}, 90.0),
        ]
        filament, similarity = get_best_top_manufacturer_match(matches)
        assert filament["manufacturer"] == "Atomic Filament"
        assert similarity == 100.0

    def test_excludes_displayed_filaments(self):
        """Should exclude already displayed filaments"""
        polymaker_filament = {"manufacturer": "Polymaker", "color": "Red"}
        atomic_filament = {"manufacturer": "Atomic Filament", "color": "Red"}
        matches = [
            (polymaker_filament, 95.0),
            (atomic_filament, 90.0),
        ]
        # Exclude the Polymaker filament
        filament, similarity = get_best_top_manufacturer_match(
            matches, displayed=[polymaker_filament]
        )
        assert filament["manufacturer"] == "Atomic Filament"
        assert similarity == 90.0

    def test_returns_none_when_all_filtered_out(self):
        """Should return (None, None) when all matches are filtered out"""
        polymaker_filament = {"manufacturer": "Polymaker", "color": "Red"}
        matches = [(polymaker_filament, 95.0)]
        filament, similarity = get_best_top_manufacturer_match(
            matches, displayed=[polymaker_filament]
        )
        assert filament is None
        assert similarity is None
