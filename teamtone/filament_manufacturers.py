"""
Filament Manufacturers
Utilities for working with filament manufacturers.
"""

import os
import yaml

_current_dir = os.path.dirname(os.path.abspath(__file__))
_manufacturers_file = os.path.join(_current_dir, "filament_manufacturers.yaml")

try:
    with open(_manufacturers_file, "r", encoding="utf-8") as f:
        _manufacturers_data = yaml.safe_load(f)
        # Extract manufacturer names from filenames (remove .yaml extension)
        TOP_MANUFACTURERS = [
            filename.replace(".yaml", "").replace("_", " ").title()
            for filename in _manufacturers_data.get("top_manufacturers", [])
        ]
except FileNotFoundError:
    TOP_MANUFACTURERS = []


def is_top_manufacturer(manufacturer: str) -> bool:
    """
    Check if a manufacturer is in the top 10 list.

    Args:
        manufacturer (str): Manufacturer name to check

    Returns:
        bool: True if the manufacturer is in the top 10 list
    """
    if not TOP_MANUFACTURERS:
        return False
    manufacturer_lower = manufacturer.lower()
    return any(
        top_mfr.lower() in manufacturer_lower or manufacturer_lower in top_mfr.lower()
        for top_mfr in TOP_MANUFACTURERS
    )


def get_manufacturer_rank(manufacturer: str) -> int:
    """
    Get the rank of a manufacturer in the top manufacturers list.

    Args:
        manufacturer (str): Manufacturer name to check

    Returns:
        int: Rank (1-10) if in top manufacturers, 999 otherwise
    """
    if not TOP_MANUFACTURERS:
        return 999
    manufacturer_lower = manufacturer.lower()
    for i, top_mfr in enumerate(TOP_MANUFACTURERS):
        if top_mfr.lower() in manufacturer_lower or manufacturer_lower in top_mfr.lower():
            return i + 1  # 1-indexed rank
    return 999
