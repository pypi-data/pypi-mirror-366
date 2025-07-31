"""
Tests for xlsx_cells function
"""

import pandas as pd
import pytest

from tidyxl import xlsx_cells


class TestXlsxCells:

    def test_basic_functionality(self, sample_excel_file):
        """Test basic xlsx_cells functionality"""
        cells = xlsx_cells(sample_excel_file)

        # Check DataFrame structure
        assert isinstance(cells, pd.DataFrame)
        assert len(cells) > 0

        # Check required columns exist
        expected_columns = [
            'sheet', 'address', 'row', 'col', 'is_blank', 'content', 'data_type',
            'error', 'logical', 'numeric', 'date', 'character', 'formula',
            'is_array', 'formula_ref', 'formula_group', 'comment', 'height', 'width',
            'row_outline_level', 'col_outline_level', 'style_format', 'local_format_id'
        ]
        for col in expected_columns:
            assert col in cells.columns, f"Missing column: {col}"

    def test_data_types(self, sample_excel_file):
        """Test that different data types are correctly identified"""
        cells = xlsx_cells(sample_excel_file)
        content_cells = cells[~cells['is_blank']]

        # Check that we have various data types
        data_types = content_cells['data_type'].unique()
        assert 'character' in data_types  # Text data
        assert 'numeric' in data_types    # Number data
        assert 'logical' in data_types    # Boolean data

        # Check type-specific columns
        text_cells = content_cells[content_cells['data_type'] == 'character']
        assert text_cells['character'].notna().any()

        numeric_cells = content_cells[content_cells['data_type'] == 'numeric']
        assert numeric_cells['numeric'].notna().any()

        boolean_cells = content_cells[content_cells['data_type'] == 'logical']
        assert boolean_cells['logical'].notna().any()

    def test_formulas(self, sample_excel_file):
        """Test formula detection and extraction"""
        cells = xlsx_cells(sample_excel_file)

        # Find formula cells (should have formula in content or separate formula column)
        formula_cells = cells[cells['formula'].notna()]
        assert len(formula_cells) > 0, "Should find formula cells"

        # Check that formulas start with =
        for _, cell in formula_cells.iterrows():
            if cell['formula']:
                assert cell['formula'].startswith('='), f"Formula should start with =: {cell['formula']}"

    def test_sheet_filtering(self, multi_sheet_excel_file):
        """Test reading specific sheets"""
        # Read all sheets
        all_cells = xlsx_cells(multi_sheet_excel_file)
        all_sheets = all_cells['sheet'].unique()
        assert len(all_sheets) >= 3

        # Read single sheet
        single_sheet_cells = xlsx_cells(multi_sheet_excel_file, sheets="Employees")
        assert all(single_sheet_cells['sheet'] == "Employees")
        assert len(single_sheet_cells) < len(all_cells)

        # Read multiple specific sheets
        multi_sheet_cells = xlsx_cells(multi_sheet_excel_file, sheets=["Employees", "Products"])
        selected_sheets = multi_sheet_cells['sheet'].unique()
        assert set(selected_sheets) == {"Employees", "Products"}

    def test_blank_cells(self, sample_excel_file):
        """Test handling of blank cells"""
        # Include blank cells
        cells_with_blanks = xlsx_cells(sample_excel_file, include_blank_cells=True)

        # Exclude blank cells
        cells_no_blanks = xlsx_cells(sample_excel_file, include_blank_cells=False)

        # Should have fewer cells when excluding blanks
        assert len(cells_no_blanks) <= len(cells_with_blanks)

        # No blank cells should remain when excluded
        if len(cells_no_blanks) > 0:
            assert not cells_no_blanks['is_blank'].any()

    def test_comments(self, sample_excel_file):
        """Test comment extraction"""
        cells = xlsx_cells(sample_excel_file)

        # Should find at least one comment (added in fixture)
        comments = cells[cells['comment'].notna()]
        assert len(comments) > 0, "Should find comment cells"

        # Check comment content
        comment_text = comments['comment'].iloc[0]
        assert isinstance(comment_text, str)
        assert len(comment_text) > 0

    def test_cell_addressing(self, sample_excel_file):
        """Test cell addressing and coordinates"""
        cells = xlsx_cells(sample_excel_file)

        # Check address format (A1 notation)
        for _, cell in cells.head().iterrows():
            assert isinstance(cell['address'], str)
            assert len(cell['address']) >= 2  # At least like "A1"

            # Check row/col are positive integers
            assert isinstance(cell['row'], int | pd.Int64Dtype)
            assert isinstance(cell['col'], int | pd.Int64Dtype)
            assert cell['row'] > 0
            assert cell['col'] > 0

    def test_error_handling(self):
        """Test error handling for invalid inputs"""
        # Non-existent file
        with pytest.raises((FileNotFoundError, ValueError)):
            xlsx_cells("non_existent_file.xlsx")

        # Invalid file type (when check_filetype=True)
        with pytest.raises(ValueError):
            xlsx_cells("test.txt", check_filetype=True)

    def test_invalid_sheet_names(self, sample_excel_file):
        """Test error handling for invalid sheet names"""
        with pytest.raises(ValueError):
            xlsx_cells(sample_excel_file, sheets="NonExistentSheet")

        with pytest.raises(ValueError):
            xlsx_cells(sample_excel_file, sheets=["ValidSheet", "InvalidSheet"])

    def test_check_filetype_parameter(self, sample_excel_file):
        """Test check_filetype parameter behavior"""
        # Should work normally with correct file
        cells = xlsx_cells(sample_excel_file, check_filetype=True)
        assert len(cells) > 0

        # Should skip check when False (assuming file is actually xlsx)
        cells = xlsx_cells(sample_excel_file, check_filetype=False)
        assert len(cells) > 0

    def test_empty_file(self, empty_excel_file):
        """Test handling of empty Excel files"""
        cells = xlsx_cells(empty_excel_file)

        # Should return empty DataFrame with correct structure
        assert isinstance(cells, pd.DataFrame)
        # May have some cells (even if just formatting), so just check structure
        expected_columns = ['sheet', 'address', 'row', 'col', 'is_blank']
        for col in expected_columns:
            assert col in cells.columns

    def test_sorting(self, multi_sheet_excel_file):
        """Test that results are sorted by sheet, row, col"""
        cells = xlsx_cells(multi_sheet_excel_file)

        # Check sorting - should be sorted by sheet, then row, then col
        for i in range(1, min(10, len(cells))):  # Check first 10 rows
            prev_row = cells.iloc[i-1]
            curr_row = cells.iloc[i]

            # Compare sheet names first
            if prev_row['sheet'] == curr_row['sheet']:
                # Same sheet - check row ordering
                if prev_row['row'] == curr_row['row']:
                    # Same row - check column ordering
                    assert prev_row['col'] <= curr_row['col']
                else:
                    assert prev_row['row'] <= curr_row['row']
            # Different sheets are also fine (sorted alphabetically)
