"""
Filament Colors Library
Returns filament color names, hex codes, and specifications for 3D printing filaments.
Data sourced from FilamentColors.xyz, manufacturer websites, and Amazon.
"""

import yaml
import os
from typing import Optional, Dict, List, Tuple


# Load filament data from filaments folder (one file per manufacturer)
_current_dir = os.path.dirname(os.path.abspath(__file__))
_filaments_folder = os.path.join(_current_dir, "filaments")


def _load_filaments_from_folder(folder: str) -> dict:
    """Load all filament data from manufacturer YAML files in the filaments folder"""
    import glob

    if not os.path.exists(folder):
        return {}

    all_filaments = {}

    for yaml_file in glob.glob(os.path.join(folder, "*.yaml")):
        # Skip config files (files starting with underscore)
        if os.path.basename(yaml_file).startswith("_"):
            continue

        with open(yaml_file, "r", encoding="utf-8") as f:
            manufacturer_data = yaml.safe_load(f)
            if manufacturer_data:
                all_filaments.update(manufacturer_data)

    return all_filaments


ALL_FILAMENTS = _load_filaments_from_folder(_filaments_folder)


def get_filament_color(
    manufacturer: str, material: str, color_name: str
) -> Optional[Dict]:
    """
    Get color information for a specific filament.

    Args:
        manufacturer (str): Manufacturer name (e.g., 'Overture', 'Polymaker', 'Hatchbox')
        material (str): Material type (e.g., 'PLA', 'PETG', 'PolyLite_PLA')
        color_name (str): Color name (e.g., 'Blue', 'Space Grey')

    Returns:
        Optional[Dict]: Dictionary containing color information, or None if not found
    """
    # Normalize for case-insensitive search
    manufacturer_lower = manufacturer.lower()
    material_lower = material.lower()
    color_lower = color_name.lower()

    # Search for manufacturer
    for mfr_key, materials in ALL_FILAMENTS.items():
        if mfr_key.lower() == manufacturer_lower:
            # Search for material type
            for mat_key, colors in materials.items():
                if mat_key.lower() == material_lower:
                    # Search for color
                    for color_key, color_data in colors.items():
                        if color_key.lower() == color_lower:
                            result = {
                                "manufacturer": mfr_key,
                                "material": mat_key,
                                "color": color_key,
                                "hex": color_data.get("hex"),
                                "source": color_data.get("source"),
                            }
                            # Add temperature data if available
                            if "temp_hotend" in color_data:
                                result["temp_hotend"] = color_data["temp_hotend"]
                            if "temp_bed" in color_data:
                                result["temp_bed"] = color_data["temp_bed"]
                            return result

    return None


def search_filaments(
    search_term: str, manufacturer: Optional[str] = None, material: Optional[str] = None
) -> List[Dict]:
    """
    Search for filaments by color name, optionally filtered by manufacturer and/or material.

    Args:
        search_term (str): Partial color name to search for
        manufacturer (str, optional): Filter by manufacturer name
        material (str, optional): Filter by material type

    Returns:
        List[Dict]: List of matching filaments with their information
    """
    search_lower = search_term.lower()
    manufacturer_lower = manufacturer.lower() if manufacturer else None
    material_lower = material.lower() if material else None
    results = []

    for mfr_key, materials in ALL_FILAMENTS.items():
        # Skip if manufacturer filter doesn't match
        if manufacturer_lower and mfr_key.lower() != manufacturer_lower:
            continue

        for mat_key, colors in materials.items():
            # Skip if material filter doesn't match
            if material_lower and mat_key.lower() != material_lower:
                continue

            for color_key, color_data in colors.items():
                if search_lower in color_key.lower():
                    result = {
                        "manufacturer": mfr_key,
                        "material": mat_key,
                        "color": color_key,
                        "hex": color_data.get("hex"),
                        "source": color_data.get("source"),
                    }
                    if "temp_hotend" in color_data:
                        result["temp_hotend"] = color_data["temp_hotend"]
                    if "temp_bed" in color_data:
                        result["temp_bed"] = color_data["temp_bed"]
                    if "link" in color_data:
                        result["link"] = color_data["link"]
                    results.append(result)

    return results


def get_manufacturer_colors(manufacturer: str, material: Optional[str] = None) -> Dict:
    """
    Get all colors for a specific manufacturer, optionally filtered by material.

    Args:
        manufacturer (str): Manufacturer name
        material (str, optional): Filter by material type

    Returns:
        Dict: Dictionary of materials and their colors, or None if manufacturer not found
    """
    manufacturer_lower = manufacturer.lower()
    material_lower = material.lower() if material else None

    for mfr_key, materials in ALL_FILAMENTS.items():
        if mfr_key.lower() == manufacturer_lower:
            if material_lower:
                # Return specific material's colors
                for mat_key, colors in materials.items():
                    if mat_key.lower() == material_lower:
                        return {mat_key: colors}
                return {}
            else:
                # Return all materials
                return materials

    return {}


def list_manufacturers() -> List[str]:
    """
    Get a list of all manufacturers in the database.

    Returns:
        List[str]: List of manufacturer names
    """
    return list(ALL_FILAMENTS.keys())


def list_materials(manufacturer: Optional[str] = None) -> List[str]:
    """
    Get a list of all material types, optionally filtered by manufacturer.

    Args:
        manufacturer (str, optional): Filter by manufacturer name

    Returns:
        List[str]: List of material type names
    """
    if manufacturer:
        manufacturer_lower = manufacturer.lower()
        for mfr_key, materials in ALL_FILAMENTS.items():
            if mfr_key.lower() == manufacturer_lower:
                return list(materials.keys())
        return []
    else:
        # Get all unique material types across all manufacturers
        all_materials = set()
        for materials in ALL_FILAMENTS.values():
            all_materials.update(materials.keys())
        return sorted(list(all_materials))


def get_filaments_with_hex() -> List[Dict]:
    """
    Get all filaments that have hex color codes defined (not null).

    Returns:
        List[Dict]: List of filaments with hex codes
    """
    results = []

    for mfr_key, materials in ALL_FILAMENTS.items():
        for mat_key, colors in materials.items():
            for color_key, color_data in colors.items():
                if color_data.get("hex") is not None:
                    result = {
                        "manufacturer": mfr_key,
                        "material": mat_key,
                        "color": color_key,
                        "hex": color_data["hex"],
                        "source": color_data.get("source"),
                    }
                    if "temp_hotend" in color_data:
                        result["temp_hotend"] = color_data["temp_hotend"]
                    if "temp_bed" in color_data:
                        result["temp_bed"] = color_data["temp_bed"]
                    if "link" in color_data:
                        result["link"] = color_data["link"]
                    results.append(result)

    return results


def get_filaments_by_hex(hex_code: str) -> List[Dict]:
    """
    Find all filaments matching a specific hex color code (exact match).

    Args:
        hex_code (str): Hex color code (with or without #)

    Returns:
        List[Dict]: List of matching filaments with their information
    """
    # Normalize hex code (remove # if present, convert to uppercase)
    hex_normalized = hex_code.strip("#").upper()

    matches = []

    for mfr_key, materials in ALL_FILAMENTS.items():
        for mat_key, colors in materials.items():
            for color_key, color_data in colors.items():
                # Normalize the stored hex code
                stored_hex = color_data.get("hex", "").strip("#").upper()

                if stored_hex == hex_normalized:
                    result = {
                        "manufacturer": mfr_key,
                        "material": mat_key,
                        "color": color_key,
                        "hex": f"#{stored_hex}",
                        "source": color_data.get("source"),
                    }
                    if "temp_hotend" in color_data:
                        result["temp_hotend"] = color_data["temp_hotend"]
                    if "temp_bed" in color_data:
                        result["temp_bed"] = color_data["temp_bed"]
                    if "link" in color_data:
                        result["link"] = color_data["link"]
                    matches.append(result)

    return matches


def find_similar_filament_color(
    target_hex: str, manufacturer: Optional[str] = None
) -> Optional[Tuple[Dict, float]]:
    """
    Find the closest matching filament color to a target hex code.
    Requires the compare_colors module.

    Args:
        target_hex (str): Target hex color to match
        manufacturer (str, optional): Filter by manufacturer

    Returns:
        Optional[Tuple[Dict, float]]: Tuple of (filament_info, similarity_percentage) or None
    """
    try:
        from . import compare_colors
    except ImportError:
        try:
            import compare_colors
        except ImportError:
            raise ImportError("compare_colors module is required for color matching")

    filaments = get_filaments_with_hex()

    if manufacturer:
        manufacturer_lower = manufacturer.lower()
        filaments = [
            f for f in filaments if f["manufacturer"].lower() == manufacturer_lower
        ]

    if not filaments:
        return None

    best_match = None
    best_similarity = -1

    for filament in filaments:
        similarity = compare_colors.color_similarity_percentage(
            target_hex, filament["hex"]
        )
        if similarity > best_similarity:
            best_similarity = similarity
            best_match = filament

    return (best_match, best_similarity) if best_match else None


def find_similar_filament_colors(
    target_hex: str, limit: int = 3, manufacturer: Optional[str] = None
) -> List[Tuple[Dict, float]]:
    """
    Find multiple similar filament colors to a target hex code, sorted by similarity.
    Requires the compare_colors module.

    Args:
        target_hex (str): Target hex color to match
        limit (int): Maximum number of matches to return (default: 3)
        manufacturer (str, optional): Filter by manufacturer

    Returns:
        List[Tuple[Dict, float]]: List of (filament_info, similarity_percentage) tuples, sorted by similarity (best first)
    """
    try:
        from . import compare_colors
    except ImportError:
        try:
            import compare_colors
        except ImportError:
            raise ImportError("compare_colors module is required for color matching")

    filaments = get_filaments_with_hex()

    if manufacturer:
        manufacturer_lower = manufacturer.lower()
        filaments = [
            f for f in filaments if f["manufacturer"].lower() == manufacturer_lower
        ]

    if not filaments:
        return []

    # Calculate similarity for all filaments
    matches = []
    for filament in filaments:
        similarity = compare_colors.color_similarity_percentage(
            target_hex, filament["hex"]
        )
        matches.append((filament, similarity))

    # Sort by similarity (descending) and return top N
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches[:limit]


# Example usage
if __name__ == "__main__":
    print("Filament Colors Library Examples")
    print("=" * 70)

    # Example 1: Get specific filament color
    print("\nExample 1: Get Overture Blue PLA")
    blue_pla = get_filament_color("Overture", "PLA", "Blue")
    if blue_pla:
        print(f"Manufacturer: {blue_pla['manufacturer']}")
        print(f"Material: {blue_pla['material']}")
        print(f"Color: {blue_pla['color']}")
        print(f"Hex Code: {blue_pla['hex']}")
        print(f"Source: {blue_pla['source']}")
        if "temp_hotend" in blue_pla:
            print(f"Hotend Temp: {blue_pla['temp_hotend']}°C")
        if "temp_bed" in blue_pla:
            print(f"Bed Temp: {blue_pla['temp_bed']}°C")

    print("\n" + "=" * 70)

    # Example 2: Search for colors
    print("\nExample 2: Search for all 'Blue' filaments")
    blue_filaments = search_filaments("Blue")
    print(f"Found {len(blue_filaments)} blue filaments:")
    for filament in blue_filaments[:5]:  # Show first 5
        hex_str = filament["hex"] if filament["hex"] else "Not measured"
        print(
            f"  - {filament['manufacturer']} {filament['material']} {filament['color']}: {hex_str}"
        )

    print("\n" + "=" * 70)

    # Example 3: Get all colors from a manufacturer
    print("\nExample 3: Get all Overture PETG colors")
    overture_petg = get_manufacturer_colors("Overture", "PETG")
    if overture_petg:
        for material, colors in overture_petg.items():
            print(f"\n{material}:")
            for color_name, color_data in colors.items():
                hex_str = (
                    color_data.get("hex") if color_data.get("hex") else "Not measured"
                )
                print(f"  - {color_name}: {hex_str}")

    print("\n" + "=" * 70)

    # Example 4: List all manufacturers
    print("\nExample 4: All manufacturers in database")
    manufacturers = list_manufacturers()
    print(f"Manufacturers: {', '.join(manufacturers)}")

    print("\n" + "=" * 70)

    # Example 5: Get filaments with hex codes
    print("\nExample 5: Filaments with measured hex codes")
    filaments_with_hex = get_filaments_with_hex()
    print(f"Found {len(filaments_with_hex)} filaments with hex codes:")
    for filament in filaments_with_hex:
        print(
            f"  - {filament['manufacturer']} {filament['material']} {filament['color']}: {filament['hex']}"
        )

    print("\n" + "=" * 70)

    # Example 6: Find similar color (if compare_colors is available)
    print("\nExample 6: Find similar filament color to #004080")
    try:
        match = find_similar_filament_color("#004080")
        if match:
            filament, similarity = match
            print(
                f"Best match: {filament['manufacturer']} {filament['material']} {filament['color']}"
            )
            print(f"Hex: {filament['hex']}")
            print(f"Similarity: {similarity:.2f}%")
    except ImportError as e:
        print(f"Color matching unavailable: {e}")

    print("\n" + "=" * 70)
    print("\nNote: Many filaments don't have hex codes yet.")
    print("You can add them from:")
    print("  - FilamentColors.xyz (colorimeter-measured)")
    print("  - Manufacturer websites/PDF hex code lists")
    print("  - Amazon product pages")
    print("  - Your own measurements")
