"""
Test suite for team_colors module

Tests the team color lookup and search functions.
Uses real data from the teams folder.

Run with: pytest teamtone/test_team_colors.py -v
"""

import pytest

from teamtone.team_colors import (
    ALL_TEAMS,
    get_team_colors,
    search_teams,
    get_all_teams_by_league,
    list_all_leagues,
)


class TestDataLoading:
    """Test that team data loads correctly"""

    def test_all_teams_loaded(self):
        """Should load team data from YAML files"""
        assert ALL_TEAMS is not None
        assert isinstance(ALL_TEAMS, dict)
        assert len(ALL_TEAMS) > 0

    def test_nfl_exists(self):
        """NFL league should exist in data"""
        assert "NFL" in ALL_TEAMS

    def test_team_structure(self):
        """Team data should have correct structure"""
        # Get NFL data
        nfl_teams = ALL_TEAMS.get("NFL", {})
        assert len(nfl_teams) > 0

        # Get first team
        team_name = next(iter(nfl_teams.keys()))
        team_data = nfl_teams[team_name]

        assert "colors" in team_data
        assert "hex" in team_data
        assert isinstance(team_data["colors"], list)
        assert isinstance(team_data["hex"], list)


class TestGetTeamColors:
    """Test get_team_colors function"""

    def test_exact_match(self):
        """Should find exact match for team name"""
        result = get_team_colors("Dallas Cowboys")

        assert result is not None
        assert result["team"] == "Dallas Cowboys"
        assert result["league"] == "NFL"
        assert "colors" in result
        assert "hex" in result

    def test_case_insensitive(self):
        """Should match team name case-insensitively"""
        result = get_team_colors("dallas cowboys")

        assert result is not None
        assert result["team"] == "Dallas Cowboys"

    def test_with_league_filter(self):
        """Should find team in specific league"""
        result = get_team_colors("Dallas Cowboys", league="NFL")

        assert result is not None
        assert result["team"] == "Dallas Cowboys"
        assert result["league"] == "NFL"

    def test_league_case_insensitive(self):
        """Should match league case-insensitively"""
        result = get_team_colors("Dallas Cowboys", league="nfl")

        assert result is not None
        assert result["league"] == "NFL"

    def test_wrong_league_returns_none(self):
        """Should return None if team not in specified league"""
        result = get_team_colors("Dallas Cowboys", league="NBA")
        assert result is None

    def test_not_found(self):
        """Should return None for unknown team"""
        result = get_team_colors("Nonexistent Team")
        assert result is None

    def test_colors_is_list(self):
        """Colors should be a list"""
        result = get_team_colors("Dallas Cowboys")

        assert result is not None
        assert isinstance(result["colors"], list)
        assert len(result["colors"]) > 0

    def test_hex_is_list(self):
        """Hex codes should be a list"""
        result = get_team_colors("Dallas Cowboys")

        assert result is not None
        assert isinstance(result["hex"], list)
        assert len(result["hex"]) > 0

    def test_hex_format(self):
        """Hex codes should be properly formatted"""
        result = get_team_colors("Dallas Cowboys")

        assert result is not None
        for hex_code in result["hex"]:
            assert hex_code.startswith("#")
            assert len(hex_code) == 7  # #RRGGBB


class TestSearchTeams:
    """Test search_teams function"""

    def test_partial_match(self):
        """Should find teams with partial name match"""
        results = search_teams("New York")

        assert len(results) > 0
        for result in results:
            assert "new york" in result["team"].lower()

    def test_case_insensitive(self):
        """Should match case-insensitively"""
        results = search_teams("new york")

        assert len(results) > 0
        for result in results:
            assert "new york" in result["team"].lower()

    def test_single_word_search(self):
        """Should find teams with single word match"""
        results = search_teams("Cowboys")

        assert len(results) >= 1
        found_cowboys = any("Cowboys" in r["team"] for r in results)
        assert found_cowboys

    def test_returns_list(self):
        """Should return a list"""
        results = search_teams("Chicago")
        assert isinstance(results, list)

    def test_result_structure(self):
        """Results should have correct structure"""
        results = search_teams("Dallas")

        if results:
            result = results[0]
            assert "team" in result
            assert "league" in result
            assert "colors" in result
            assert "hex" in result

    def test_no_results(self):
        """Should return empty list for no matches"""
        results = search_teams("xyznonexistent")
        assert results == []

    def test_multiple_leagues(self):
        """Should find teams across multiple leagues"""
        results = search_teams("New York")

        # New York has teams in multiple leagues
        leagues = {r["league"] for r in results}
        assert len(leagues) > 1


class TestGetAllTeamsByLeague:
    """Test get_all_teams_by_league function"""

    def test_nfl_teams(self):
        """Should return all NFL teams"""
        result = get_all_teams_by_league("NFL")

        assert result is not None
        assert isinstance(result, dict)
        assert len(result) > 0
        assert "Dallas Cowboys" in result

    def test_case_insensitive(self):
        """Should match league case-insensitively"""
        result = get_all_teams_by_league("nfl")

        assert result is not None
        assert len(result) > 0

    def test_unknown_league(self):
        """Should return None for unknown league"""
        result = get_all_teams_by_league("XYZ")
        assert result is None

    def test_nba_teams(self):
        """Should return all NBA teams"""
        result = get_all_teams_by_league("NBA")

        assert result is not None
        assert len(result) > 0

    def test_team_data_structure(self):
        """Returned teams should have correct structure"""
        result = get_all_teams_by_league("NFL")

        team_name = next(iter(result.keys()))
        team_data = result[team_name]

        assert "colors" in team_data
        assert "hex" in team_data


class TestListAllLeagues:
    """Test list_all_leagues function"""

    def test_returns_list(self):
        """Should return a list"""
        result = list_all_leagues()
        assert isinstance(result, list)

    def test_contains_major_leagues(self):
        """Should contain major US sports leagues"""
        result = list_all_leagues()

        # Should have at least NFL, NBA, MLB, NHL
        assert "NFL" in result
        assert "NBA" in result

    def test_not_empty(self):
        """Should not be empty"""
        result = list_all_leagues()
        assert len(result) > 0


class TestMultipleLeagues:
    """Test data from multiple leagues"""

    @pytest.mark.parametrize(
        "league",
        ["NFL", "NBA", "MLB", "NHL", "MLS"],
    )
    def test_league_has_teams(self, league):
        """Each league should have teams"""
        result = get_all_teams_by_league(league)

        if result is not None:  # League might not exist in test data
            assert len(result) > 0

    @pytest.mark.parametrize(
        "team,league",
        [
            ("Dallas Cowboys", "NFL"),
            ("Los Angeles Lakers", "NBA"),
            ("New York Yankees", "MLB"),
            ("Chicago Blackhawks", "NHL"),
        ],
    )
    def test_known_teams_exist(self, team, league):
        """Known teams should exist in their leagues"""
        result = get_team_colors(team, league=league)

        # Only assert if the league exists in our data
        if league in ALL_TEAMS:
            assert result is not None
            assert result["team"] == team
            assert result["league"] == league


class TestColorDataQuality:
    """Test quality of color data"""

    def test_colors_and_hex_same_length(self):
        """Colors and hex lists should have same length"""
        for league_name, teams in ALL_TEAMS.items():
            for team_name, team_data in teams.items():
                colors = team_data.get("colors", [])
                hexes = team_data.get("hex", [])
                assert len(colors) == len(hexes), (
                    f"{team_name} has {len(colors)} colors but {len(hexes)} hex codes"
                )

    def test_hex_codes_valid_format(self):
        """All hex codes should be valid format"""
        for league_name, teams in ALL_TEAMS.items():
            for team_name, team_data in teams.items():
                for hex_code in team_data.get("hex", []):
                    assert hex_code.startswith("#"), (
                        f"{team_name} has invalid hex: {hex_code}"
                    )
                    assert len(hex_code) == 7, (
                        f"{team_name} has invalid hex length: {hex_code}"
                    )
                    # Verify it's valid hex
                    try:
                        int(hex_code[1:], 16)
                    except ValueError:
                        pytest.fail(f"{team_name} has invalid hex value: {hex_code}")
