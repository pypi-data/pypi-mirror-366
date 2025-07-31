"""
Cell data extraction functionality
"""

from typing import Any

import pandas as pd
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter


def xlsx_cells(
    path: str,
    sheets: str | list[str] | None = None,
    check_filetype: bool = True,
    include_blank_cells: bool = True
) -> pd.DataFrame:
    """
    Import xlsx (Excel) cell contents into a tidy structure.

    Imports data from spreadsheets without coercing it into a rectangle.
    Each cell is represented by a row in a data frame, following the exact
    behavior of the R tidyxl package.

    Parameters
    ----------
    path : str
        Path to the Excel file (.xlsx or .xlsm)
    sheets : str, list of str, or None
        Worksheet names to read. If None, reads all sheets.
    check_filetype : bool, default True
        Whether to check that the file is a valid xlsx/xlsm file
    include_blank_cells : bool, default True
        Whether to include cells that have no value but may have formatting

    Returns
    -------
    pd.DataFrame
        A tidy DataFrame where each row represents a single cell with columns:
        - sheet: worksheet name (str)
        - address: cell address in A1 notation (str)
        - row: row number (int)
        - col: column number (int)
        - is_blank: whether cell has a value (bool)
        - content: raw cell value before type conversion (str)
        - data_type: cell type (str: error, logical, numeric, date, character, blank)
        - error: cell error value (str)
        - logical: boolean value (bool)
        - numeric: numeric value (float)
        - date: date value (datetime)
        - character: string value (str)
        - formula: cell formula (str)
        - is_array: whether formula is an array formula (bool)
        - formula_ref: range address for array/shared formulas (str)
        - formula_group: formula group index (int)
        - comment: cell comment text (str)
        - height: row height in Excel units (float)
        - width: column width in Excel units (float)
        - row_outline_level: row outline level (int)
        - col_outline_level: column outline level (int)
        - style_format: index for style formats (str)
        - local_format_id: index for local cell formats (int)
    """

    # Check file type if requested
    if check_filetype:
        if not path.lower().endswith(('.xlsx', '.xlsm')):
            raise ValueError("File must be .xlsx or .xlsm format")

    # Load workbook
    wb = load_workbook(filename=path, data_only=False, keep_vba=True)

    # Determine which sheets to process
    if sheets is None:
        sheet_names = wb.sheetnames
    elif isinstance(sheets, str):
        sheet_names = [sheets]
    else:
        sheet_names = sheets

    # Validate sheet names
    available_sheets = wb.sheetnames
    for sheet_name in sheet_names:
        if sheet_name not in available_sheets:
            raise ValueError(f"Sheet '{sheet_name}' not found. Available sheets: {available_sheets}")

    all_cells = []

    for sheet_name in sheet_names:
        ws = wb[sheet_name]

        # Get all cells in the worksheet
        for row in ws.iter_rows():
            for cell in row:
                # Determine if cell is blank
                is_blank = cell.value is None and (cell.data_type == 'n' or cell.data_type is None)

                # Skip blank cells if not requested
                if not include_blank_cells and is_blank:
                    continue

                # Get raw content as string
                content = str(cell.value) if cell.value is not None else None

                # Determine data type and extract typed values
                data_type, typed_values = _get_cell_data_and_values(cell)

                # Get formula information
                formula_info = _get_formula_info(cell)

                # Get comment
                comment = cell.comment.text if cell.comment else None

                # Get dimensions
                row_height = ws.row_dimensions[cell.row].height
                col_width = ws.column_dimensions[get_column_letter(cell.column)].width

                # Get outline levels
                row_outline_level = ws.row_dimensions[cell.row].outline_level or 0
                col_outline_level = ws.column_dimensions[get_column_letter(cell.column)].outline_level or 0

                # Create cell record matching R tidyxl structure
                cell_record = {
                    'sheet': sheet_name,
                    'address': cell.coordinate,
                    'row': cell.row,
                    'col': cell.column,
                    'is_blank': is_blank,
                    'content': content,
                    'data_type': data_type,
                    'error': typed_values.get('error'),
                    'logical': typed_values.get('logical'),
                    'numeric': typed_values.get('numeric'),
                    'date': typed_values.get('date'),
                    'character': typed_values.get('character'),
                    'formula': formula_info['formula'],
                    'is_array': formula_info['is_array'],
                    'formula_ref': formula_info['formula_ref'],
                    'formula_group': formula_info['formula_group'],
                    'comment': comment,
                    'height': row_height,
                    'width': col_width,
                    'row_outline_level': row_outline_level,
                    'col_outline_level': col_outline_level,
                    'style_format': cell.style if hasattr(cell, 'style') else None,
                    'local_format_id': id(cell.number_format) if cell.number_format else None
                }

                all_cells.append(cell_record)

    # Convert to DataFrame with proper columns even if empty
    if not all_cells:
        # Return empty DataFrame with correct column structure
        expected_columns = [
            'sheet', 'address', 'row', 'col', 'is_blank', 'content', 'data_type',
            'error', 'logical', 'numeric', 'date', 'character', 'formula',
            'is_array', 'formula_ref', 'formula_group', 'comment', 'height', 'width',
            'row_outline_level', 'col_outline_level', 'style_format', 'local_format_id'
        ]
        return pd.DataFrame(columns=expected_columns)

    df = pd.DataFrame(all_cells)

    # Sort by sheet, row, column for consistent output
    df = df.sort_values(['sheet', 'row', 'col']).reset_index(drop=True)

    return df


def _get_cell_data_and_values(cell) -> tuple[str, dict[str, Any]]:
    """
    Determine the data type of a cell and extract typed values.

    Parameters
    ----------
    cell : openpyxl.cell.Cell
        The cell to analyze

    Returns
    -------
    tuple
        (data_type, typed_values_dict) where data_type is one of:
        'error', 'logical', 'numeric', 'date', 'character', 'blank'
        and typed_values_dict contains the appropriate typed value
    """

    typed_values: dict[str, Any] = {
        'error': None,
        'logical': None,
        'numeric': None,
        'date': None,
        'character': None
    }

    if cell.value is None:
        return 'blank', typed_values

    # Handle different openpyxl data types
    if cell.data_type == 'e':  # Error
        typed_values['error'] = str(cell.value)
        return 'error', typed_values

    elif cell.data_type == 'b':  # Boolean
        typed_values['logical'] = bool(cell.value)
        return 'logical', typed_values

    elif cell.data_type == 'n':  # Numeric
        # Check if it's a date by looking at number format
        if _is_date_format(cell):
            try:
                # Convert Excel date serial to datetime
                from openpyxl.utils.datetime import from_excel
                typed_values['date'] = from_excel(cell.value)
                return 'date', typed_values
            except Exception:
                # Fall back to numeric if date conversion fails
                typed_values['numeric'] = float(cell.value)
                return 'numeric', typed_values
        else:
            typed_values['numeric'] = float(cell.value)
            return 'numeric', typed_values

    elif cell.data_type == 'f':  # Formula
        # For formulas, return 'formula' as data_type and don't populate character column
        # The formula itself will be handled by _get_formula_info
        return 'formula', typed_values

    else:  # String types ('s', 'inlineStr', 'str')
        typed_values['character'] = str(cell.value)
        return 'character', typed_values


def _is_date_format(cell) -> bool:
    """
    Check if a cell's number format indicates it's a date.

    Parameters
    ----------
    cell : openpyxl.cell.Cell
        The cell to check

    Returns
    -------
    bool
        True if the cell appears to be formatted as a date
    """

    if not cell.number_format:
        return False

    # Common date format indicators
    date_indicators = ['d', 'm', 'y', 'h', 's', ':', '/', '-']
    format_str = cell.number_format.lower()

    # Check if format contains date indicators
    return any(indicator in format_str for indicator in date_indicators)


def _get_formula_info(cell) -> dict[str, Any]:
    """
    Extract formula-related information from a cell.

    Parameters
    ----------
    cell : openpyxl.cell.Cell
        The cell to analyze

    Returns
    -------
    dict
        Dictionary with formula, is_array, formula_ref, formula_group
    """

    formula_info: dict[str, Any] = {
        'formula': None,
        'is_array': False,
        'formula_ref': None,
        'formula_group': None
    }

    if cell.data_type == 'f' and cell.value:
        formula_info['formula'] = str(cell.value)

        # Check for array formula indicators
        if hasattr(cell, 'array_formula') and cell.array_formula:
            formula_info['is_array'] = True

        # Try to get formula reference range (this is limited in openpyxl)
        if hasattr(cell, 'shared_formula'):
            formula_info['formula_group'] = id(cell.shared_formula)

    return formula_info
