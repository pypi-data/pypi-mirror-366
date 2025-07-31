"""
Tests for xlsx_sheet_names, xlsx_names, xlsx_validation, and xlsx_formats functions
"""

import pandas as pd
import pytest

from tidyxl import xlsx_formats, xlsx_names, xlsx_sheet_names, xlsx_validation


class TestXlsxSheetNames:

    def test_basic_functionality(self, sample_excel_file):
        """Test basic xlsx_sheet_names functionality"""
        sheets = xlsx_sheet_names(sample_excel_file)

        assert isinstance(sheets, list)
        assert len(sheets) > 0
        assert all(isinstance(sheet, str) for sheet in sheets)

    def test_multi_sheet_file(self, multi_sheet_excel_file):
        """Test with multi-sheet file"""
        sheets = xlsx_sheet_names(multi_sheet_excel_file)

        assert len(sheets) >= 3
        assert "Employees" in sheets
        assert "Products" in sheets
        assert "Summary" in sheets

    def test_order_preservation(self, multi_sheet_excel_file):
        """Test that sheet order is preserved"""
        sheets = xlsx_sheet_names(multi_sheet_excel_file)

        # Should maintain order from Excel file
        assert isinstance(sheets, list)
        # First sheet should be "Employees" (created first)
        assert sheets[0] == "Employees"

    def test_error_handling(self):
        """Test error handling"""
        with pytest.raises((FileNotFoundError, ValueError)):
            xlsx_sheet_names("non_existent_file.xlsx")

        with pytest.raises(ValueError):
            xlsx_sheet_names("test.txt", check_filetype=True)

    def test_check_filetype_parameter(self, sample_excel_file):
        """Test check_filetype parameter"""
        # Should work with correct file
        sheets = xlsx_sheet_names(sample_excel_file, check_filetype=True)
        assert len(sheets) > 0

        # Should skip check when False
        sheets = xlsx_sheet_names(sample_excel_file, check_filetype=False)
        assert len(sheets) > 0


class TestXlsxNames:

    def test_basic_functionality(self, excel_with_named_ranges):
        """Test basic xlsx_names functionality"""
        names = xlsx_names(excel_with_named_ranges)

        assert isinstance(names, pd.DataFrame)

        # Check required columns
        expected_columns = ['sheet', 'name', 'formula', 'comment', 'hidden', 'is_range']
        for col in expected_columns:
            assert col in names.columns

    def test_named_ranges_extraction(self, excel_with_named_ranges):
        """Test extraction of named ranges"""
        names = xlsx_names(excel_with_named_ranges)

        if len(names) > 0:
            # Should find the named ranges we created
            name_list = names['name'].tolist()
            assert 'DataRange' in name_list or 'ValueColumn' in name_list

            # Check formulas are present
            formulas = names['formula'].dropna()
            assert len(formulas) > 0

            # Check sheet column (may be None for global ranges)
            assert 'sheet' in names.columns

    def test_empty_file_names(self, empty_excel_file):
        """Test with file containing no named ranges"""
        names = xlsx_names(empty_excel_file)

        assert isinstance(names, pd.DataFrame)
        # Should return empty DataFrame with correct structure
        expected_columns = ['sheet', 'name', 'formula', 'comment', 'hidden', 'is_range']
        for col in expected_columns:
            assert col in names.columns

    def test_error_handling(self):
        """Test error handling for xlsx_names"""
        with pytest.raises((FileNotFoundError, ValueError)):
            xlsx_names("non_existent_file.xlsx")

        with pytest.raises(ValueError):
            xlsx_names("test.txt", check_filetype=True)


class TestXlsxValidation:

    def test_basic_functionality(self, excel_with_validation):
        """Test basic xlsx_validation functionality"""
        validation = xlsx_validation(excel_with_validation)

        assert isinstance(validation, pd.DataFrame)

        # Check required columns
        expected_columns = [
            'sheet', 'ref', 'type', 'operator', 'formula1', 'formula2',
            'allow_blank', 'show_input_message', 'show_error_message',
            'prompt_title', 'prompt', 'error_title', 'error', 'error_style'
        ]
        for col in expected_columns:
            assert col in validation.columns

    def test_validation_rules_extraction(self, excel_with_validation):
        """Test extraction of validation rules"""
        validation = xlsx_validation(excel_with_validation)

        if len(validation) > 0:
            # Should find validation rules
            assert len(validation) > 0

            # Check validation types
            types = validation['type'].dropna().unique()
            assert len(types) > 0

            # Check cell references
            refs = validation['ref'].dropna()
            assert len(refs) > 0

            # References should be in Excel format (like A2:A10)
            for ref in refs:
                assert isinstance(ref, str)
                assert len(ref) > 0

    def test_sheet_filtering(self, excel_with_validation):
        """Test sheet filtering in validation"""
        # Test reading all sheets
        all_validation = xlsx_validation(excel_with_validation)

        # Test reading specific sheet
        sheet_validation = xlsx_validation(excel_with_validation, sheets="ValidationSheet")

        # Should have same or fewer rules when filtering
        assert len(sheet_validation) <= len(all_validation)

        # All returned rules should be from specified sheet
        if len(sheet_validation) > 0:
            assert all(sheet_validation['sheet'] == "ValidationSheet")

    def test_empty_file_validation(self, empty_excel_file):
        """Test with file containing no validation rules"""
        validation = xlsx_validation(empty_excel_file)

        assert isinstance(validation, pd.DataFrame)
        # Should return empty DataFrame with correct structure
        expected_columns = ['sheet', 'ref', 'type']
        for col in expected_columns:
            assert col in validation.columns

    def test_error_handling(self):
        """Test error handling for xlsx_validation"""
        with pytest.raises((FileNotFoundError, ValueError)):
            xlsx_validation("non_existent_file.xlsx")

        with pytest.raises(ValueError):
            xlsx_validation("test.txt", check_filetype=True)

    def test_invalid_sheet_names(self, excel_with_validation):
        """Test error handling for invalid sheet names"""
        with pytest.raises(ValueError):
            xlsx_validation(excel_with_validation, sheets="NonExistentSheet")


class TestXlsxFormats:

    def test_basic_functionality(self, sample_excel_file):
        """Test basic xlsx_formats functionality"""
        formats = xlsx_formats(sample_excel_file)

        assert isinstance(formats, dict)

        # Check required keys
        expected_keys = ['fonts', 'fills', 'borders', 'number_formats']
        for key in expected_keys:
            assert key in formats
            assert isinstance(formats[key], list)

    def test_format_structure(self, sample_excel_file):
        """Test format data structure"""
        formats = xlsx_formats(sample_excel_file)

        # Check that we get some format data
        total_formats = sum(len(formats[key]) for key in formats.keys())
        assert total_formats >= 0  # May be 0 for simple files, but structure should exist

        # If we have font data, check structure
        if formats['fonts']:
            font = formats['fonts'][0]
            assert isinstance(font, dict)
            # Should have basic font properties
            expected_font_keys = ['name', 'size', 'bold', 'italic']
            for key in expected_font_keys:
                assert key in font

    def test_error_handling(self):
        """Test error handling for xlsx_formats"""
        with pytest.raises((FileNotFoundError, ValueError)):
            xlsx_formats("non_existent_file.xlsx")

    def test_empty_file_formats(self, empty_excel_file):
        """Test with empty file"""
        formats = xlsx_formats(empty_excel_file)

        assert isinstance(formats, dict)
        expected_keys = ['fonts', 'fills', 'borders', 'number_formats']
        for key in expected_keys:
            assert key in formats
            assert isinstance(formats[key], list)
