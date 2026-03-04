"""
Test suite for main module

Tests the CLI functions including manual color entry,
league selection, and display functions.

Run with: pytest teamtone/test_main.py -v
"""

from unittest.mock import patch

from teamtone.main import (
    print_header,
    select_league,
    select_team,
    get_manual_hex_color,
    select_filament_type,
    display_team_colors,
    display_manual_color,
    MAX_SUGGESTIONS,
    MIN_SUGGESTIONS,
)


class TestPrintHeader:
    """Test print_header function"""

    def test_prints_formatted_header(self, capsys):
        """Should print header with equals sign borders"""
        print_header("Test Header")
        output = capsys.readouterr().out

        assert "=" * 70 in output
        assert "Test Header" in output


class TestSelectLeague:
    """Test select_league function"""

    @patch("teamtone.main.input", return_value="q")
    def test_quit_returns_none(self, mock_input):
        """Pressing 'q' should return None"""
        result = select_league()
        assert result is None

    @patch("teamtone.main.input", return_value="0")
    def test_zero_returns_manual(self, mock_input):
        """Selecting 0 should return 'manual'"""
        result = select_league()
        assert result == "manual"

    @patch("teamtone.main.input", return_value="1")
    def test_valid_league_selection(self, mock_input):
        """Selecting a valid number should return that league"""
        result = select_league()
        assert result is not None
        assert result != "manual"

    @patch("teamtone.main.input", side_effect=["999", "q"])
    def test_invalid_number_reprompts(self, mock_input):
        """Invalid number should reprompt"""
        result = select_league()
        assert result is None
        assert mock_input.call_count == 2

    @patch("teamtone.main.input", side_effect=["abc", "q"])
    def test_non_numeric_reprompts(self, mock_input):
        """Non-numeric input should reprompt"""
        result = select_league()
        assert result is None
        assert mock_input.call_count == 2

    @patch("teamtone.main.input", return_value="0")
    def test_displays_manual_option(self, mock_input, capsys):
        """Should display manual entry option as option 0"""
        select_league()
        output = capsys.readouterr().out
        assert "0." in output
        assert "manually" in output.lower() or "manual" in output.lower()


class TestSelectTeam:
    """Test select_team function"""

    @patch("teamtone.main.input", return_value="q")
    def test_quit_returns_none(self, mock_input):
        """Pressing 'q' should return None"""
        result = select_team("NFL")
        assert result is None

    @patch("teamtone.main.input", return_value="b")
    def test_back_returns_back(self, mock_input):
        """Pressing 'b' should return 'back'"""
        result = select_team("NFL")
        assert result == "back"

    @patch("teamtone.main.input", return_value="1")
    def test_valid_selection(self, mock_input):
        """Valid selection should return a team name"""
        result = select_team("NFL")
        assert result is not None
        assert isinstance(result, str)
        assert result != "back"

    def test_invalid_league_returns_none(self):
        """Invalid league should return None"""
        result = select_team("NONEXISTENT")
        assert result is None

    @patch("teamtone.main.input", side_effect=["abc", "q"])
    def test_non_numeric_reprompts(self, mock_input):
        """Non-numeric input should reprompt"""
        result = select_team("NFL")
        assert result is None
        assert mock_input.call_count == 2


class TestGetManualHexColor:
    """Test get_manual_hex_color function"""

    @patch("teamtone.main.input", return_value="q")
    def test_quit_returns_none(self, mock_input):
        """Pressing 'q' should return None"""
        result = get_manual_hex_color()
        assert result is None

    @patch("teamtone.main.input", return_value="b")
    def test_back_returns_back(self, mock_input):
        """Pressing 'b' should return 'back'"""
        result = get_manual_hex_color()
        assert result == "back"

    @patch("teamtone.main.input", return_value="FF0000")
    def test_hex_without_hash(self, mock_input):
        """Should accept hex without # prefix"""
        result = get_manual_hex_color()
        assert result == "#FF0000"

    @patch("teamtone.main.input", return_value="#FF0000")
    def test_hex_with_hash(self, mock_input):
        """Should accept hex with # prefix"""
        result = get_manual_hex_color()
        assert result == "#FF0000"

    @patch("teamtone.main.input", return_value="#ff0000")
    def test_hex_lowercase_normalized(self, mock_input):
        """Should normalize lowercase hex to uppercase"""
        result = get_manual_hex_color()
        assert result == "#FF0000"

    @patch("teamtone.main.input", return_value="00ff00")
    def test_green_hex(self, mock_input):
        """Should handle green hex code"""
        result = get_manual_hex_color()
        assert result == "#00FF00"

    @patch("teamtone.main.input", side_effect=["ZZZZZZ", "q"])
    def test_invalid_hex_reprompts(self, mock_input):
        """Invalid hex characters should reprompt"""
        result = get_manual_hex_color()
        assert result is None
        assert mock_input.call_count == 2

    @patch("teamtone.main.input", side_effect=["FFF", "q"])
    def test_short_hex_reprompts(self, mock_input):
        """3-character hex should reprompt (only 6-char supported)"""
        result = get_manual_hex_color()
        assert result is None
        assert mock_input.call_count == 2

    @patch("teamtone.main.input", side_effect=["", "q"])
    def test_empty_input_reprompts(self, mock_input):
        """Empty input should reprompt"""
        result = get_manual_hex_color()
        assert result is None
        assert mock_input.call_count == 2

    @patch("teamtone.main.input", side_effect=["##FF0000", "q"])
    def test_double_hash_handled(self, mock_input):
        """Double # should be stripped and still work if valid"""
        result = get_manual_hex_color()
        # lstrip('#') removes all leading #, so ##FF0000 -> FF0000 -> valid
        assert result == "#FF0000"


class TestSelectFilamentType:
    """Test select_filament_type function"""

    @patch("teamtone.main.input", return_value="q")
    def test_quit_returns_none(self, mock_input):
        """Pressing 'q' should return None"""
        result = select_filament_type()
        assert result is None

    @patch("teamtone.main.input", return_value="b")
    def test_back_returns_back(self, mock_input):
        """Pressing 'b' should return 'back'"""
        result = select_filament_type()
        assert result == "back"

    @patch("teamtone.main.input", return_value="0")
    def test_zero_returns_empty_string(self, mock_input):
        """Selecting 0 (all types) should return empty string"""
        result = select_filament_type()
        assert result == ""

    @patch("teamtone.main.input", return_value="1")
    def test_valid_type_selection(self, mock_input):
        """Valid selection should return a filament type"""
        result = select_filament_type()
        assert result is not None
        assert isinstance(result, str)
        assert result != ""


class TestDisplayTeamColors:
    """Test display_team_colors function"""

    def test_displays_team_colors(self, capsys):
        """Should display team color information"""
        display_team_colors("Dallas Cowboys", "NFL")
        output = capsys.readouterr().out

        assert "Dallas Cowboys" in output
        assert "NFL" in output

    def test_displays_with_filament_type(self, capsys):
        """Should show filament type label when specified"""
        display_team_colors("Dallas Cowboys", "NFL", filament_type="PLA")
        output = capsys.readouterr().out

        assert "[PLA]" in output

    def test_unknown_team_shows_message(self, capsys):
        """Should show message for unknown team"""
        display_team_colors("Nonexistent Team", "NFL")
        output = capsys.readouterr().out

        assert "Could not find" in output or "no color data" in output.lower()

    def test_displays_hex_codes(self, capsys):
        """Should display hex codes for team colors"""
        display_team_colors("Dallas Cowboys", "NFL")
        output = capsys.readouterr().out

        assert "#" in output

    def test_displays_matching_filaments_section(self, capsys):
        """Should display matching filaments section"""
        display_team_colors("Dallas Cowboys", "NFL")
        output = capsys.readouterr().out

        assert "Matching Filaments" in output


class TestDisplayManualColor:
    """Test display_manual_color function"""

    def test_displays_hex_code(self, capsys):
        """Should display the target hex code"""
        display_manual_color("#FF0000")
        output = capsys.readouterr().out

        assert "#FF0000" in output

    def test_displays_with_filament_type(self, capsys):
        """Should show filament type label when specified"""
        display_manual_color("#FF0000", filament_type="PLA")
        output = capsys.readouterr().out

        assert "[PLA]" in output

    def test_displays_matching_filaments_section(self, capsys):
        """Should display matching filaments section"""
        display_manual_color("#FF0000")
        output = capsys.readouterr().out

        assert "Matching Filaments" in output

    def test_displays_target_color(self, capsys):
        """Should display the target color"""
        display_manual_color("#00FF00")
        output = capsys.readouterr().out

        assert "Target Color" in output
        assert "#00FF00" in output

    def test_black_finds_matches(self, capsys):
        """Black (#000000) should find exact matches"""
        display_manual_color("#000000")
        output = capsys.readouterr().out

        assert "exact match" in output.lower()

    def test_white_finds_matches(self, capsys):
        """White (#FFFFFF) should find exact matches"""
        display_manual_color("#FFFFFF")
        output = capsys.readouterr().out

        assert "exact match" in output.lower() or "similar" in output.lower()

    def test_rare_color_shows_similar(self, capsys):
        """A rare hex code should show similar matches"""
        display_manual_color("#123456")
        output = capsys.readouterr().out

        # Should show either exact or similar matches
        assert "match" in output.lower()

    def test_type_filter_pla(self, capsys):
        """Should filter results by PLA type"""
        display_manual_color("#000000", filament_type="PLA")
        output = capsys.readouterr().out

        assert "PLA" in output

    def test_type_filter_petg(self, capsys):
        """Should filter results by PETG type"""
        display_manual_color("#000000", filament_type="PETG")
        output = capsys.readouterr().out

        assert "PETG" in output


class TestConstants:
    """Test module constants"""

    def test_max_suggestions_positive(self):
        """MAX_SUGGESTIONS should be a positive integer"""
        assert isinstance(MAX_SUGGESTIONS, int)
        assert MAX_SUGGESTIONS > 0

    def test_min_suggestions_positive(self):
        """MIN_SUGGESTIONS should be a positive integer"""
        assert isinstance(MIN_SUGGESTIONS, int)
        assert MIN_SUGGESTIONS > 0
