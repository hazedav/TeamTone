"""
TeamTone - Sports Team Colors Library
Returns team color names and hex codes for major sports leagues.
"""

import yaml
from pathlib import Path

# Load team data from teams folder (one file per league)
_current_dir = Path(__file__).parent
_teams_folder = _current_dir / "teams"


def _load_teams_from_folder(folder: Path) -> dict:
    """Load all team data from league YAML files in the teams folder"""
    if not folder.exists():
        return {}

    all_teams = {}

    for yaml_file in folder.glob("*.yaml"):
        league_data = yaml.safe_load(open(yaml_file, "r", encoding="utf-8"))
        if league_data:
            all_teams.update(league_data)

    return all_teams


ALL_TEAMS = _load_teams_from_folder(_teams_folder)


def get_team_colors(team_name, league=None):
    """
    Get color information for a specific team.

    Args:
        team_name (str): Name of the team
        league (str, optional): Specific league to search in (NFL, NBA, MLB, NHL, MLS)

    Returns:
        dict: Dictionary containing colors and hex codes, or None if not found
    """
    # Normalize team name for case-insensitive search
    team_name_lower = team_name.lower()

    if league:
        # Search in specific league
        league_upper = league.upper()
        if league_upper in ALL_TEAMS:
            for team, colors in ALL_TEAMS[league_upper].items():
                if team.lower() == team_name_lower:
                    return {
                        "team": team,
                        "league": league_upper,
                        "colors": colors["colors"],
                        "hex": colors["hex"],
                    }
    else:
        # Search across all leagues
        for league_name, teams in ALL_TEAMS.items():
            for team, colors in teams.items():
                if team.lower() == team_name_lower:
                    return {
                        "team": team,
                        "league": league_name,
                        "colors": colors["colors"],
                        "hex": colors["hex"],
                    }

    return None


def search_teams(search_term):
    """
    Search for teams by partial name match.

    Args:
        search_term (str): Partial team name to search for

    Returns:
        list: List of matching teams with their league information
    """
    search_term_lower = search_term.lower()
    results = []

    for league_name, teams in ALL_TEAMS.items():
        for team, colors in teams.items():
            if search_term_lower in team.lower():
                results.append(
                    {
                        "team": team,
                        "league": league_name,
                        "colors": colors["colors"],
                        "hex": colors["hex"],
                    }
                )

    return results


def get_all_teams_by_league(league):
    """
    Get all teams for a specific league.

    Args:
        league (str): League name (NFL, NBA, MLB, NHL, MLS)

    Returns:
        dict: Dictionary of all teams in the league, or None if league not found
    """
    league_upper = league.upper()
    if league_upper in ALL_TEAMS:
        return ALL_TEAMS[league_upper]
    return None


def list_all_leagues():
    """
    Get a list of all supported leagues.

    Returns:
        list: List of league names
    """
    return list(ALL_TEAMS.keys())


# Example usage
if __name__ == "__main__":
    # Example 1: Get specific team colors
    print("Example 1: Get Los Angeles Lakers colors")
    lakers = get_team_colors("Los Angeles Lakers")
    if lakers:
        print(f"Team: {lakers['team']}")
        print(f"League: {lakers['league']}")
        print(f"Colors: {', '.join(lakers['colors'])}")
        print(f"Hex Codes: {', '.join(lakers['hex'])}")

    print("\n" + "=" * 50 + "\n")

    # Example 2: Search for teams
    print("Example 2: Search for teams with 'New York' in name")
    ny_teams = search_teams("New York")
    for team in ny_teams:
        print(f"{team['team']} ({team['league']}): {', '.join(team['colors'])}")

    print("\n" + "=" * 50 + "\n")

    # Example 3: Get team by league
    print("Example 3: Get Dallas Cowboys colors (NFL)")
    cowboys = get_team_colors("Dallas Cowboys", league="NFL")
    if cowboys:
        print(f"Team: {cowboys['team']}")
        print(f"Colors: {', '.join(cowboys['colors'])}")
        print(f"Hex Codes: {', '.join(cowboys['hex'])}")

    print("\n" + "=" * 50 + "\n")

    # Example 4: List all leagues
    print("Example 4: All supported leagues")
    leagues = list_all_leagues()
    print(f"Supported leagues: {', '.join(leagues)}")
