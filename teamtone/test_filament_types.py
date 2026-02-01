"""
Test suite for filament_types module

Run with: pytest teamtone/test_filament_types.py -v
"""

import pytest

from teamtone.filament_types import (
    get_base_types,
    classify_material,
    is_filament_type,
)


class TestGetBaseTypes:
    """Test get_base_types function"""

    def test_returns_list(self):
        """Should return a list"""
        types = get_base_types()
        assert isinstance(types, list)

    def test_includes_common_types(self):
        """Should include common filament types"""
        types = get_base_types()
        assert "PLA" in types
        assert "PETG" in types
        assert "ABS" in types
        assert "ASA" in types
        assert "TPU" in types

    def test_returns_non_empty_list(self):
        """Should return at least the common types"""
        types = get_base_types()
        assert len(types) >= 5


class TestClassifyMaterial:
    """Test classify_material function"""

    @pytest.mark.parametrize(
        "material,expected",
        [
            # Exact matches
            ("PLA", "PLA"),
            ("PETG", "PETG"),
            ("ABS", "ABS"),
            ("ASA", "ASA"),
            ("TPU", "TPU"),
            # Variants with suffixes
            ("PLA Silk", "PLA"),
            ("PLA Matte", "PLA"),
            ("PLA Basic", "PLA"),
            ("PLA Pro", "PLA"),
            ("PLA+/Pro", "PLA"),
            ("PLA CF", "PLA"),
            ("PLA High Speed", "PLA"),
            ("PETG Basic", "PETG"),
            ("PETG CF", "PETG"),
            ("PETG Silk", "PETG"),
            ("ABS Basic", "ABS"),
            ("ABS Translucent", "ABS"),
            ("ASA Galaxy", "ASA"),
            ("TPU 95A", "TPU"),
            ("TPU 85A", "TPU"),
            # Other types
            ("PC", "PC"),
            ("PC-ABS Basic", "PC"),
            ("PA", "PA"),
            ("PA (Nylon)", "PA"),
        ],
    )
    def test_classifies_correctly(self, material, expected):
        """Test prefix-based classification"""
        assert classify_material(material) == expected

    def test_case_insensitive(self):
        """Classification should be case insensitive"""
        assert classify_material("pla silk") == "PLA"
        assert classify_material("PETG BASIC") == "PETG"
        assert classify_material("Abs") == "ABS"

    def test_unknown_returns_other(self):
        """Unknown materials should return OTHER"""
        assert classify_material("SomethingUnknown") == "OTHER"
        assert classify_material("RandomMaterial") == "OTHER"

    def test_handles_whitespace(self):
        """Should handle leading/trailing whitespace"""
        assert classify_material("  PLA  ") == "PLA"
        assert classify_material("  PETG Basic  ") == "PETG"


class TestIsFilamentType:
    """Test is_filament_type function"""

    def test_true_for_matching_type(self):
        """Should return True when material matches type"""
        assert is_filament_type("PLA Silk", "PLA") is True
        assert is_filament_type("PETG", "PETG") is True
        assert is_filament_type("ABS Basic", "ABS") is True

    def test_false_for_non_matching_type(self):
        """Should return False when material doesn't match type"""
        assert is_filament_type("PLA Silk", "PETG") is False
        assert is_filament_type("ABS", "PLA") is False
        assert is_filament_type("TPU 95A", "ASA") is False

    def test_case_insensitive_type(self):
        """Type parameter should be case insensitive"""
        assert is_filament_type("PLA Silk", "pla") is True
        assert is_filament_type("PETG", "petg") is True
