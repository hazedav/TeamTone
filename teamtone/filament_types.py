"""
Filament Types Classification
Classifies material strings into base filament types using prefix matching.
"""

import os
from typing import List, Optional
import yaml

_current_dir = os.path.dirname(os.path.abspath(__file__))
_types_file = os.path.join(_current_dir, "filament_types.yaml")

# Cache for loaded data
_filament_types_data: Optional[dict] = None


def _load_filament_types() -> dict:
    """Load filament types configuration from YAML file."""
    global _filament_types_data
    if _filament_types_data is not None:
        return _filament_types_data

    try:
        with open(_types_file, "r", encoding="utf-8") as f:
            _filament_types_data = yaml.safe_load(f)
            return _filament_types_data
    except FileNotFoundError:
        _filament_types_data = {"base_types": [], "default_type": "OTHER"}
        return _filament_types_data


def get_base_types() -> List[str]:
    """
    Get list of all base filament types.

    Returns:
        List[str]: List of base type names (e.g., ['PLA', 'PETG', 'ABS', ...])
    """
    data = _load_filament_types()
    return data.get("base_types", [])


def classify_material(material: str) -> str:
    """
    Classify a material string into its base filament type using prefix matching.

    Args:
        material: Material type string (e.g., 'PLA Silk', 'PETG Basic', 'ABS')

    Returns:
        str: Base type name (e.g., 'PLA', 'PETG') or 'OTHER' if unclassified
    """
    data = _load_filament_types()
    base_types = data.get("base_types", [])
    default = data.get("default_type", "OTHER")

    material_upper = material.upper().strip()

    # Check if material starts with any base type
    for base_type in base_types:
        if material_upper.startswith(base_type):
            return base_type

    return default


def is_filament_type(material: str, base_type: str) -> bool:
    """
    Check if a material string belongs to a specific base type.

    Args:
        material: Material type string to classify
        base_type: Base type to check against

    Returns:
        bool: True if material belongs to the specified base type
    """
    return classify_material(material) == base_type.upper()
