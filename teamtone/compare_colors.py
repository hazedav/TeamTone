"""
Color Comparison Library
Computes proximity/likeness between hex colors using various color distance metrics.
"""

import math
from typing import Tuple, Dict


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """
    Convert hex color to RGB tuple.

    Args:
        hex_color (str): Hex color string (with or without #)

    Returns:
        Tuple[int, int, int]: RGB values (0-255)
    """
    # Remove # if present
    hex_color = hex_color.lstrip('#')

    # Convert to RGB
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """
    Convert RGB values to hex color string.

    Args:
        r (int): Red value (0-255)
        g (int): Green value (0-255)
        b (int): Blue value (0-255)

    Returns:
        str: Hex color string with #
    """
    return f"#{r:02x}{g:02x}{b:02x}"


def rgb_to_lab(r: int, g: int, b: int) -> Tuple[float, float, float]:
    """
    Convert RGB to LAB color space for perceptually accurate color comparison.
    LAB is designed to be perceptually uniform.

    Args:
        r (int): Red value (0-255)
        g (int): Green value (0-255)
        b (int): Blue value (0-255)

    Returns:
        Tuple[float, float, float]: LAB values
    """
    # Normalize RGB to 0-1
    r, g, b = r / 255.0, g / 255.0, b / 255.0

    # Apply sRGB gamma correction
    def gamma_correct(channel):
        if channel <= 0.04045:
            return channel / 12.92
        else:
            return ((channel + 0.055) / 1.055) ** 2.4

    r = gamma_correct(r)
    g = gamma_correct(g)
    b = gamma_correct(b)

    # Convert to XYZ (using D65 illuminant)
    x = r * 0.4124564 + g * 0.3575761 + b * 0.1804375
    y = r * 0.2126729 + g * 0.7151522 + b * 0.0721750
    z = r * 0.0193339 + g * 0.1191920 + b * 0.9503041

    # Normalize for D65 white point
    x /= 0.95047
    y /= 1.00000
    z /= 1.08883

    # Convert XYZ to LAB
    def f(t):
        delta = 6/29
        if t > delta ** 3:
            return t ** (1/3)
        else:
            return t / (3 * delta ** 2) + 4/29

    L = 116 * f(y) - 16
    a = 500 * (f(x) - f(y))
    b_lab = 200 * (f(y) - f(z))

    return (L, a, b_lab)


def euclidean_distance_rgb(hex1: str, hex2: str) -> float:
    """
    Calculate Euclidean distance between two colors in RGB space.

    Args:
        hex1 (str): First hex color
        hex2 (str): Second hex color

    Returns:
        float: Distance value (0-441.67, where 0 is identical)
    """
    r1, g1, b1 = hex_to_rgb(hex1)
    r2, g2, b2 = hex_to_rgb(hex2)

    return math.sqrt((r2 - r1)**2 + (g2 - g1)**2 + (b2 - b1)**2)


def weighted_rgb_distance(hex1: str, hex2: str) -> float:
    """
    Calculate weighted RGB distance that accounts for human perception.
    Red and green differences are weighted more than blue.

    Args:
        hex1 (str): First hex color
        hex2 (str): Second hex color

    Returns:
        float: Weighted distance value
    """
    r1, g1, b1 = hex_to_rgb(hex1)
    r2, g2, b2 = hex_to_rgb(hex2)

    # Calculate mean red
    r_mean = (r1 + r2) / 2

    # Weighted formula based on human perception
    delta_r = r2 - r1
    delta_g = g2 - g1
    delta_b = b2 - b1

    weight_r = 2 + r_mean / 256
    weight_g = 4.0
    weight_b = 2 + (255 - r_mean) / 256

    return math.sqrt(weight_r * delta_r**2 + weight_g * delta_g**2 + weight_b * delta_b**2)


def delta_e_cie76(hex1: str, hex2: str) -> float:
    """
    Calculate Delta E (CIE76) - perceptually accurate color difference.
    This is the Euclidean distance in LAB color space.

    Delta E values:
    - 0-1: Not perceptible to human eye
    - 1-2: Perceptible through close observation
    - 2-10: Perceptible at a glance
    - 11-49: Colors are more similar than opposite
    - 50+: Colors are very different

    Args:
        hex1 (str): First hex color
        hex2 (str): Second hex color

    Returns:
        float: Delta E value (lower is more similar)
    """
    r1, g1, b1 = hex_to_rgb(hex1)
    r2, g2, b2 = hex_to_rgb(hex2)

    L1, a1, b1_lab = rgb_to_lab(r1, g1, b1)
    L2, a2, b2_lab = rgb_to_lab(r2, g2, b2)

    delta_L = L2 - L1
    delta_a = a2 - a1
    delta_b = b2_lab - b1_lab

    return math.sqrt(delta_L**2 + delta_a**2 + delta_b**2)


def delta_e_cie94(hex1: str, hex2: str) -> float:
    """
    Calculate Delta E (CIE94) - improved perceptual color difference.
    More accurate than CIE76 for specific applications.

    Args:
        hex1 (str): First hex color
        hex2 (str): Second hex color

    Returns:
        float: Delta E value (lower is more similar)
    """
    r1, g1, b1 = hex_to_rgb(hex1)
    r2, g2, b2 = hex_to_rgb(hex2)

    L1, a1, b1_lab = rgb_to_lab(r1, g1, b1)
    L2, a2, b2_lab = rgb_to_lab(r2, g2, b2)

    delta_L = L1 - L2
    C1 = math.sqrt(a1**2 + b1_lab**2)
    C2 = math.sqrt(a2**2 + b2_lab**2)
    delta_C = C1 - C2
    delta_a = a1 - a2
    delta_b = b1_lab - b2_lab
    delta_H = math.sqrt(max(0, delta_a**2 + delta_b**2 - delta_C**2))

    # Weighting factors for graphic arts
    kL = 1.0
    kC = 1.0
    kH = 1.0
    K1 = 0.045
    K2 = 0.015

    SL = 1.0
    SC = 1.0 + K1 * C1
    SH = 1.0 + K2 * C1

    delta_e = math.sqrt(
        (delta_L / (kL * SL))**2 +
        (delta_C / (kC * SC))**2 +
        (delta_H / (kH * SH))**2
    )

    return delta_e


def color_similarity_percentage(hex1: str, hex2: str, method: str = 'delta_e_cie76') -> float:
    """
    Calculate color similarity as a percentage (0-100%).
    100% means identical colors, 0% means very different.

    Args:
        hex1 (str): First hex color
        hex2 (str): Second hex color
        method (str): Method to use ('delta_e_cie76', 'delta_e_cie94', 'rgb', 'weighted_rgb')

    Returns:
        float: Similarity percentage (0-100)
    """
    if method == 'delta_e_cie76':
        distance = delta_e_cie76(hex1, hex2)
        # Delta E of 100 is very different, 0 is identical
        max_distance = 100.0
    elif method == 'delta_e_cie94':
        distance = delta_e_cie94(hex1, hex2)
        max_distance = 100.0
    elif method == 'rgb':
        distance = euclidean_distance_rgb(hex1, hex2)
        # Max RGB distance is sqrt(255^2 + 255^2 + 255^2) ≈ 441.67
        max_distance = 441.67
    elif method == 'weighted_rgb':
        distance = weighted_rgb_distance(hex1, hex2)
        max_distance = 765.0  # Approximate max for weighted distance
    else:
        raise ValueError(f"Unknown method: {method}")

    # Convert distance to similarity percentage
    similarity = max(0, 100 * (1 - distance / max_distance))
    return similarity


def compare_colors(hex1: str, hex2: str) -> Dict[str, float]:
    """
    Compare two colors using multiple metrics.

    Args:
        hex1 (str): First hex color
        hex2 (str): Second hex color

    Returns:
        Dict[str, float]: Dictionary with various distance metrics and similarity
    """
    return {
        'rgb_distance': euclidean_distance_rgb(hex1, hex2),
        'weighted_rgb_distance': weighted_rgb_distance(hex1, hex2),
        'delta_e_cie76': delta_e_cie76(hex1, hex2),
        'delta_e_cie94': delta_e_cie94(hex1, hex2),
        'similarity_percentage': color_similarity_percentage(hex1, hex2, 'delta_e_cie76'),
    }


def find_closest_color(target_hex: str, color_list: list[Tuple[str, str]]) -> Tuple[str, str, float]:
    """
    Find the closest color from a list of colors.

    Args:
        target_hex (str): Target hex color to match
        color_list (list): List of tuples (name, hex_color)

    Returns:
        Tuple[str, str, float]: (name, hex, similarity_percentage) of closest match
    """
    best_match = None
    best_similarity = -1

    for name, hex_color in color_list:
        similarity = color_similarity_percentage(target_hex, hex_color)
        if similarity > best_similarity:
            best_similarity = similarity
            best_match = (name, hex_color, similarity)

    return best_match


# Example usage
if __name__ == "__main__":
    # Test with some team colors
    lakers_purple = "#552583"
    lakers_gold = "#FDB927"
    celtics_green = "#007A33"

    print("Color Comparison Examples")
    print("=" * 60)

    # Example 1: Compare Lakers colors
    print(f"\nExample 1: Lakers Purple vs Lakers Gold")
    print(f"Purple: {lakers_purple}, Gold: {lakers_gold}")
    result = compare_colors(lakers_purple, lakers_gold)
    print(f"RGB Distance: {result['rgb_distance']:.2f}")
    print(f"Delta E (CIE76): {result['delta_e_cie76']:.2f}")
    print(f"Similarity: {result['similarity_percentage']:.2f}%")

    print("\n" + "=" * 60)

    # Example 2: Compare Lakers Purple vs Celtics Green
    print(f"\nExample 2: Lakers Purple vs Celtics Green")
    print(f"Purple: {lakers_purple}, Green: {celtics_green}")
    result = compare_colors(lakers_purple, celtics_green)
    print(f"RGB Distance: {result['rgb_distance']:.2f}")
    print(f"Delta E (CIE76): {result['delta_e_cie76']:.2f}")
    print(f"Similarity: {result['similarity_percentage']:.2f}%")

    print("\n" + "=" * 60)

    # Example 3: Find closest color
    print(f"\nExample 3: Find closest color to Lakers Purple")
    colors = [
        ("Lakers Gold", lakers_gold),
        ("Celtics Green", celtics_green),
        ("Similar Purple", "#5A2D81"),  # Kings purple
    ]
    name, hex_val, similarity = find_closest_color(lakers_purple, colors)
    print(f"Closest match: {name} ({hex_val})")
    print(f"Similarity: {similarity:.2f}%")

    print("\n" + "=" * 60)

    # Example 4: Demonstrating Delta E interpretation
    print(f"\nExample 4: Delta E Interpretation Guide")
    print("0-1: Not perceptible to human eye")
    print("1-2: Perceptible through close observation")
    print("2-10: Perceptible at a glance")
    print("11-49: Colors are more similar than opposite")
    print("50+: Colors are very different")
