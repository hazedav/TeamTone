"""
Test suite for scrape_filaments wrapper module

Tests the utility functions and orchestration logic, not individual scrapers.
Individual scraper tests live in filament_sites/test_<scraper>.py

Run with: pytest teamtone/fetch/test_scrape_filaments.py -v
"""

from scrape_filaments import (
    sanitize_filename,
    load_yaml,
    save_yaml,
    merge_filament_data,
    load_filaments_from_folder,
    save_filaments_to_folder,
    SCRAPERS,
)


class TestSanitizeFilename:
    """Test filename sanitization for manufacturer names"""

    def test_simple_name(self):
        """Simple names should be lowercased"""
        assert sanitize_filename("Polymaker") == "polymaker"
        assert sanitize_filename("SUNLU") == "sunlu"

    def test_spaces_to_underscores(self):
        """Spaces should become underscores"""
        assert sanitize_filename("Atomic Filament") == "atomic_filament"
        assert sanitize_filename("Some  Double  Space") == "some_double_space"

    def test_invalid_characters(self):
        """Invalid filename characters should be replaced"""
        assert sanitize_filename("Name<>:test") == "name___test"  # Each char replaced
        assert sanitize_filename("File/Name\\Test") == "file_name_test"

    def test_leading_trailing_cleanup(self):
        """Leading/trailing underscores and dots should be removed"""
        assert sanitize_filename(".hidden") == "hidden"
        assert sanitize_filename("_underscore_") == "underscore"
        assert sanitize_filename("..dots..") == "dots"

    def test_empty_string(self):
        """Empty string should return 'unknown'"""
        assert sanitize_filename("") == "unknown"
        assert sanitize_filename("...") == "unknown"


class TestMergeFilamentData:
    """Test deep merging of filament data"""

    def test_merge_empty_existing(self):
        """Merging into empty dict should return new data"""
        new = {"Polymaker": {"PLA": {"Red": {"hex": "#FF0000"}}}}
        result = merge_filament_data({}, new)
        assert result == new

    def test_merge_empty_new(self):
        """Merging empty dict should return existing data"""
        existing = {"Polymaker": {"PLA": {"Red": {"hex": "#FF0000"}}}}
        result = merge_filament_data(existing, {})
        assert result == existing

    def test_merge_new_manufacturer(self):
        """New manufacturer should be added"""
        existing = {"Polymaker": {"PLA": {"Red": {"hex": "#FF0000"}}}}
        new = {"SUNLU": {"PETG": {"Blue": {"hex": "#0000FF"}}}}
        result = merge_filament_data(existing, new)

        assert "Polymaker" in result
        assert "SUNLU" in result
        assert result["SUNLU"]["PETG"]["Blue"]["hex"] == "#0000FF"

    def test_merge_new_material(self):
        """New material for existing manufacturer should be added"""
        existing = {"Polymaker": {"PLA": {"Red": {"hex": "#FF0000"}}}}
        new = {"Polymaker": {"PETG": {"Blue": {"hex": "#0000FF"}}}}
        result = merge_filament_data(existing, new)

        assert "PLA" in result["Polymaker"]
        assert "PETG" in result["Polymaker"]

    def test_merge_new_color(self):
        """New color for existing material should be added"""
        existing = {"Polymaker": {"PLA": {"Red": {"hex": "#FF0000"}}}}
        new = {"Polymaker": {"PLA": {"Blue": {"hex": "#0000FF"}}}}
        result = merge_filament_data(existing, new)

        assert "Red" in result["Polymaker"]["PLA"]
        assert "Blue" in result["Polymaker"]["PLA"]

    def test_merge_overwrites_existing_color(self):
        """Same color should be overwritten with new data"""
        existing = {"Polymaker": {"PLA": {"Red": {"hex": "#FF0000", "source": "old"}}}}
        new = {"Polymaker": {"PLA": {"Red": {"hex": "#EE0000", "source": "new"}}}}
        result = merge_filament_data(existing, new)

        assert result["Polymaker"]["PLA"]["Red"]["hex"] == "#EE0000"
        assert result["Polymaker"]["PLA"]["Red"]["source"] == "new"

    def test_does_not_mutate_existing(self):
        """Original existing dict should not be mutated"""
        existing = {"Polymaker": {"PLA": {"Red": {"hex": "#FF0000"}}}}
        new = {"SUNLU": {"PETG": {"Blue": {"hex": "#0000FF"}}}}

        merge_filament_data(existing, new)

        assert "SUNLU" not in existing


class TestYamlIO:
    """Test YAML loading and saving"""

    def test_load_nonexistent_file(self, tmp_path):
        """Loading nonexistent file should return empty dict"""
        result = load_yaml(tmp_path / "nonexistent.yaml")
        assert result == {}

    def test_save_and_load_roundtrip(self, tmp_path):
        """Data should survive save/load roundtrip"""
        data = {"Polymaker": {"PLA": {"Red": {"hex": "#FF0000"}}}}
        file_path = tmp_path / "test.yaml"

        save_yaml(data, file_path)
        loaded = load_yaml(file_path)

        assert loaded == data

    def test_save_creates_parent_dirs(self, tmp_path):
        """save_yaml should create parent directories"""
        data = {"test": "data"}
        file_path = tmp_path / "nested" / "dirs" / "test.yaml"

        save_yaml(data, file_path)

        assert file_path.exists()


class TestFolderIO:
    """Test loading/saving filaments from folder"""

    def test_load_empty_folder(self, tmp_path):
        """Loading from empty folder should return empty dict"""
        result = load_filaments_from_folder(tmp_path)
        assert result == {}

    def test_load_nonexistent_folder(self, tmp_path):
        """Loading from nonexistent folder should return empty dict"""
        result = load_filaments_from_folder(tmp_path / "nonexistent")
        assert result == {}

    def test_save_and_load_folder_roundtrip(self, tmp_path):
        """Data should survive save/load folder roundtrip"""
        data = {
            "Polymaker": {"PLA": {"Red": {"hex": "#FF0000"}}},
            "SUNLU": {"PETG": {"Blue": {"hex": "#0000FF"}}},
        }

        written = save_filaments_to_folder(data, tmp_path)
        assert len(written) == 2

        loaded = load_filaments_from_folder(tmp_path)
        assert loaded == data

    def test_save_creates_individual_files(self, tmp_path):
        """Each manufacturer should get its own file"""
        data = {
            "Polymaker": {"PLA": {"Red": {"hex": "#FF0000"}}},
            "SUNLU": {"PETG": {"Blue": {"hex": "#0000FF"}}},
        }

        save_filaments_to_folder(data, tmp_path)

        assert (tmp_path / "polymaker.yaml").exists()
        assert (tmp_path / "sunlu.yaml").exists()


class TestScrapersRegistry:
    """Test scraper registry configuration"""

    def test_scrapers_dict_not_empty(self):
        """SCRAPERS should have entries"""
        assert len(SCRAPERS) > 0

    def test_filamentprofiles_scraper_exists(self):
        """filamentprofiles scraper should exist"""
        assert "filamentprofiles" in SCRAPERS

    def test_polymaker_scraper_exists(self):
        """polymaker scraper should exist"""
        assert "polymaker" in SCRAPERS

    def test_sunlu_scraper_exists(self):
        """sunlu scraper should exist"""
        assert "sunlu" in SCRAPERS

    def test_all_scrapers_are_classes(self):
        """All scraper values should be classes"""
        for name, scraper_class in SCRAPERS.items():
            assert callable(scraper_class), f"{name} scraper is not callable"

    def test_all_scrapers_have_required_methods(self):
        """All scrapers should have fetch and site_name"""
        for name, scraper_class in SCRAPERS.items():
            instance = scraper_class()
            assert hasattr(instance, "fetch"), f"{name} missing fetch method"
            assert hasattr(instance, "site_name"), f"{name} missing site_name property"
            assert hasattr(instance, "site_url"), f"{name} missing site_url property"
