"""
Filament Scoring
Utilities for scoring and ranking filament matches based on similarity and manufacturer preference.
"""

from .filament_manufacturers import get_manufacturer_rank

# Multiplier for manufacturer rank bonus
# (11 - rank) * RANK_MULTIPLIER gives the bonus points
# With 0.56: #1 gets +5.6, #10 gets +0.56 (5% spread across all ranks)
# This means a 95% similar #1 manufacturer just beats a 100% similar #10 manufacturer
RANK_MULTIPLIER = 0.56


def calculate_manufacturer_bonus(manufacturer: str) -> float:
    """
    Calculate the bonus score for a manufacturer based on their rank.

    Args:
        manufacturer (str): Manufacturer name

    Returns:
        float: Bonus points (0 if not in top manufacturers)
    """
    rank = get_manufacturer_rank(manufacturer)
    if rank == 999:
        return 0.0
    return (11 - rank) * RANK_MULTIPLIER


def calculate_weighted_score(similarity: float, manufacturer: str) -> float:
    """
    Calculate a weighted score combining color similarity and manufacturer ranking.

    Args:
        similarity (float): Color similarity percentage (0-100)
        manufacturer (str): Manufacturer name

    Returns:
        float: Combined weighted score
    """
    manufacturer_bonus = calculate_manufacturer_bonus(manufacturer)
    return similarity + manufacturer_bonus


def get_best_top_manufacturer_match(matches: list, displayed: list = None) -> tuple:
    """
    Find the best match from top manufacturers using weighted scoring.

    Args:
        matches (list): List of (filament, similarity) tuples
        displayed (list): Optional list of already displayed filaments to exclude

    Returns:
        tuple: (filament, similarity) of best match, or (None, None) if no matches
    """
    if displayed is None:
        displayed = []

    from .filament_manufacturers import is_top_manufacturer

    # Filter for top manufacturers not already displayed
    top_mfr_matches = [
        (filament, similarity)
        for filament, similarity in matches
        if filament not in displayed
        and is_top_manufacturer(filament["manufacturer"])
    ]

    if not top_mfr_matches:
        return None, None

    # Find best match using weighted score
    best_match = max(
        top_mfr_matches,
        key=lambda m: calculate_weighted_score(m[1], m[0]["manufacturer"])
    )
    return best_match
