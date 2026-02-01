"""
TeamTone - Main CLI
Interactive script to match team colors with 3D printing filaments
"""

from . import team_colors
from . import filament_colors
from .filament_manufacturers import is_top_manufacturer, get_manufacturer_rank
from .filament_scoring import (
    get_best_top_manufacturer_match,
    calculate_manufacturer_bonus,
    calculate_weighted_score,
)

# Maximum number of filament suggestions to display per color
MAX_SUGGESTIONS = 3
# Minimum number of similar matches to show when no exact matches found
MIN_SUGGESTIONS = 3


def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def select_league():
    """Prompt user to select a league"""
    print_header("Select a League")

    leagues = team_colors.list_all_leagues()

    if not leagues:
        print("No leagues found!")
        return None

    # Display leagues with numbers
    for i, league in enumerate(leagues, 1):
        print(f"  {i}. {league}")

    # Get user selection
    while True:
        try:
            choice = input("\nEnter league number (or 'q' to quit): ").strip()
            if choice.lower() == "q":
                return None

            choice_num = int(choice)
            if 1 <= choice_num <= len(leagues):
                return leagues[choice_num - 1]
            else:
                print(f"Please enter a number between 1 and {len(leagues)}")
        except ValueError:
            print("Please enter a valid number or 'q' to quit")


def select_team(league):
    """Prompt user to select a team from a league"""
    print_header(f"Select a Team from {league}")

    teams_data = team_colors.get_all_teams_by_league(league)

    if not teams_data:
        print(f"No teams found for {league}!")
        return None

    # Get list of team names
    team_names = sorted(teams_data.keys())

    # Display teams with numbers
    for i, team_name in enumerate(team_names, 1):
        print(f"  {i}. {team_name}")

    # Get user selection
    while True:
        try:
            choice = input(
                "\nEnter team number (or 'b' to go back, 'q' to quit): "
            ).strip()
            if choice.lower() == "q":
                return None
            if choice.lower() == "b":
                return "back"

            choice_num = int(choice)
            if 1 <= choice_num <= len(team_names):
                return team_names[choice_num - 1]
            else:
                print(f"Please enter a number between 1 and {len(team_names)}")
        except ValueError:
            print("Please enter a valid number, 'b' to go back, or 'q' to quit")


def display_team_colors(team_name, league):
    """Display team colors and find matching filaments"""
    print_header(f"{team_name} ({league})")

    # Get team color data
    team_data = team_colors.get_team_colors(team_name, league)

    if not team_data:
        print(f"Could not find color data for {team_name}")
        return

    colors = team_data.get("colors", [])
    hex_codes = team_data.get("hex", [])

    if not colors or not hex_codes:
        print(f"{team_name} has no color data available")
        return

    print("\nTeam Colors:")
    for color, hex_code in zip(colors, hex_codes):
        print(f"  - {color}: {hex_code}")

    # Find matching filaments for each color
    print("\n" + "-" * 70)
    print("Matching Filaments:")
    print("-" * 70)

    for color, hex_code in zip(colors, hex_codes):
        print(f"\n{color} ({hex_code}):")

        # Find exact matches
        matches = filament_colors.get_filaments_by_hex(hex_code)

        if matches:
            total_matches = len(matches)
            display_matches = matches[:MAX_SUGGESTIONS]

            if total_matches > MAX_SUGGESTIONS:
                print(
                    f"  Found {total_matches} exact match(es), showing top {MAX_SUGGESTIONS}:"
                )
            else:
                print(f"  Found {total_matches} exact match(es):")

            # Check if any of the top matches have links
            has_link = any(match.get("link") for match in display_matches)

            # Track displayed matches for top manufacturer check
            displayed_matches = list(display_matches)

            for match in display_matches:
                manufacturer = match["manufacturer"]
                material = match["material"]
                color_name = match["color"]
                temps = ""
                if match.get("temp_hotend") and match.get("temp_bed"):
                    temps = (
                        f" (Hotend: {match['temp_hotend']}C, Bed: {match['temp_bed']}C)"
                    )

                link = ""
                if match.get("link"):
                    link = f" [{match['link']}]"

                print(f"    - {manufacturer} - {material} - {color_name}{temps}{link}")

            # If none of the top matches have links, find the first one with a link
            if not has_link:
                for match in matches[MAX_SUGGESTIONS:]:
                    if match.get("link"):
                        manufacturer = match["manufacturer"]
                        material = match["material"]
                        color_name = match["color"]
                        temps = ""
                        if match.get("temp_hotend") and match.get("temp_bed"):
                            temps = f" (Hotend: {match['temp_hotend']}C, Bed: {match['temp_bed']}C)"

                        print("\n  First exact match with purchase link:")
                        print(
                            f"    - {manufacturer} - {material} - {color_name}{temps} [{match['link']}]"
                        )
                        displayed_matches.append(match)
                        break

            # If none of the displayed matches are from top 10, find the highest-ranked top manufacturer
            has_top_manufacturer = any(
                is_top_manufacturer(match["manufacturer"])
                for match in displayed_matches
            )
            if not has_top_manufacturer:
                # Find all top manufacturer matches and pick the highest-ranked one
                top_matches = [
                    match for match in matches
                    if match not in displayed_matches and is_top_manufacturer(match["manufacturer"])
                ]
                if top_matches:
                    # Sort by manufacturer rank (lowest rank = highest priority)
                    best_match = min(top_matches, key=lambda m: get_manufacturer_rank(m["manufacturer"]))
                    manufacturer = best_match["manufacturer"]
                    material = best_match["material"]
                    color_name = best_match["color"]
                    temps = ""
                    if best_match.get("temp_hotend") and best_match.get("temp_bed"):
                        temps = f" (Hotend: {best_match['temp_hotend']}C, Bed: {best_match['temp_bed']}C)"

                    link = ""
                    if best_match.get("link"):
                        link = f" [{best_match['link']}]"

                    print("\n  Nearest exact match from top manufacturer:")
                    print(
                        f"    - {manufacturer} - {material} - {color_name}{temps}{link}"
                    )
        else:
            print("  No exact matches found")

            # Try to find similar colors
            try:
                # Fetch more matches and re-sort by weighted score (similarity + manufacturer rank)
                all_matches = filament_colors.find_similar_filament_colors(
                    hex_code, limit=50
                )
                # Sort by weighted score (similarity + manufacturer bonus)
                all_matches.sort(
                    key=lambda m: calculate_weighted_score(m[1], m[0]["manufacturer"]),
                    reverse=True,
                )
                similar_matches = all_matches[:MIN_SUGGESTIONS]

                if similar_matches:
                    print(f"  Closest {len(similar_matches)} match(es) (weighted by manufacturer rank):")

                    # Check if any of the top matches have links
                    has_link = any(
                        filament.get("link") for filament, _ in similar_matches
                    )

                    # Track displayed matches for top manufacturer check
                    displayed_filaments = [filament for filament, _ in similar_matches]

                    for filament, similarity in similar_matches:
                        manufacturer = filament["manufacturer"]
                        material = filament["material"]
                        color_name = filament["color"]
                        rank_bonus = calculate_manufacturer_bonus(manufacturer)
                        temps = ""
                        if filament.get("temp_hotend") and filament.get("temp_bed"):
                            temps = f" (Hotend: {filament['temp_hotend']}C, Bed: {filament['temp_bed']}C)"

                        link = ""
                        if filament.get("link"):
                            link = f" [{filament['link']}]"

                        score_info = f"({similarity:.1f}% similar"
                        if rank_bonus > 0:
                            score_info += f" + {rank_bonus:.1f} rank bonus"
                        score_info += ")"

                        print(
                            f"    - {manufacturer} - {material} - {color_name} - {filament['hex']} {score_info}{temps}{link}"
                        )

                    # If none of the top matches have links, find the nearest one with a link
                    if not has_link:
                        for filament, similarity in all_matches:
                            if (
                                filament.get("link")
                                and filament not in displayed_filaments
                            ):
                                manufacturer = filament["manufacturer"]
                                material = filament["material"]
                                color_name = filament["color"]
                                temps = ""
                                if filament.get("temp_hotend") and filament.get(
                                    "temp_bed"
                                ):
                                    temps = f" (Hotend: {filament['temp_hotend']}C, Bed: {filament['temp_bed']}C)"

                                print("\n  Nearest match with purchase link:")
                                print(
                                    f"    - {manufacturer} - {material} - {color_name} - {filament['hex']} ({similarity:.1f}% similar){temps} [{filament['link']}]"
                                )
                                displayed_filaments.append(filament)
                                break

                    # If none of the displayed matches are from top 10, find best weighted match
                    has_top_manufacturer = any(
                        is_top_manufacturer(filament["manufacturer"])
                        for filament in displayed_filaments
                    )
                    if not has_top_manufacturer:
                        filament, similarity = get_best_top_manufacturer_match(
                            all_matches, displayed_filaments
                        )
                        if filament:
                            manufacturer = filament["manufacturer"]
                            material = filament["material"]
                            color_name = filament["color"]
                            temps = ""
                            if filament.get("temp_hotend") and filament.get(
                                "temp_bed"
                            ):
                                temps = f" (Hotend: {filament['temp_hotend']}C, Bed: {filament['temp_bed']}C)"

                            link = ""
                            if filament.get("link"):
                                link = f" [{filament['link']}]"

                            rank_bonus = calculate_manufacturer_bonus(manufacturer)
                            print("\n  Nearest match from top manufacturer:")
                            print(
                                f"    - {manufacturer} - {material} - {color_name} - {filament['hex']} ({similarity:.1f}% similar + {rank_bonus:.1f} rank bonus){temps}{link}"
                            )
            except ImportError:
                # compare_colors module not available
                pass


def main():
    """Main interactive CLI"""
    print("\n")
    print("*" * 70)
    print("*" + " " * 68 + "*")
    print(
        "*"
        + "  TeamTone - Match Sports Team Colors to 3D Printing Filaments".center(68)
        + "*"
    )
    print("*" + " " * 68 + "*")
    print("*" * 70)

    while True:
        # Select league
        league = select_league()
        if league is None:
            print("\nGoodbye!")
            break

        while True:
            # Select team
            team_name = select_team(league)
            if team_name is None:
                print("\nGoodbye!")
                return
            if team_name == "back":
                break

            # Display colors and matches
            display_team_colors(team_name, league)

            # Ask if user wants to see another team
            print("\n" + "=" * 70)
            choice = input("\nSee another team? (y/n/b to go back): ").strip().lower()
            if choice == "n":
                print("\nGoodbye!")
                return
            elif choice == "b":
                break
            # Otherwise continue to select another team from same league


if __name__ == "__main__":
    main()
