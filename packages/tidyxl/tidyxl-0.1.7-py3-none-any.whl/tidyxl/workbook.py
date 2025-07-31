"""
Workbook-level functionality for sheet names and metadata
"""

import re

import pandas as pd
from openpyxl import load_workbook


def xlsx_sheet_names(path: str, check_filetype: bool = True) -> list[str]:
    """
    List sheets in an xlsx (Excel) file.

    Returns the names of the sheets in a workbook, as a list of strings,
    in the order they appear when opening the spreadsheet.

    Parameters
    ----------
    path : str
        Path to the Excel file (.xlsx or .xlsm)
    check_filetype : bool, default True
        Whether to check that the file is a valid xlsx/xlsm file

    Returns
    -------
    List[str]
        List of worksheet names in their original order
    """

    # Check file type if requested
    if check_filetype:
        if not path.lower().endswith(('.xlsx', '.xlsm')):
            raise ValueError("File must be .xlsx or .xlsm format")

    # Load workbook (read-only for efficiency)
    wb = load_workbook(filename=path, read_only=True, data_only=False)

    try:
        return wb.sheetnames
    finally:
        wb.close()


def xlsx_names(path: str, check_filetype: bool = True) -> pd.DataFrame:
    """
    Import named formulas from xlsx (Excel) files.

    Extracts named ranges and named formulas (defined names) from Excel files,
    including both global and sheet-specific named ranges.

    Parameters
    ----------
    path : str
        Path to the Excel file (.xlsx or .xlsm)
    check_filetype : bool, default True
        Whether to check that the file is a valid xlsx/xlsm file

    Returns
    -------
    pd.DataFrame
        A DataFrame with columns:
        - sheet: Sheet name (None if globally defined)
        - name: Name of the formula/range
        - formula: Cell range or formula definition
        - comment: Description by spreadsheet author
        - hidden: Visibility status
        - is_range: Whether formula represents a cell range
    """

    # Check file type if requested
    if check_filetype:
        if not path.lower().endswith(('.xlsx', '.xlsm')):
            raise ValueError("File must be .xlsx or .xlsm format")

    # Load workbook
    wb = load_workbook(filename=path, data_only=False)

    names_list = []

    try:
        # Get defined names from workbook
        for name, defined_name in wb.defined_names.items():
            # Determine if it's sheet-specific or global
            sheet_name = None
            if hasattr(defined_name, 'localSheetId') and defined_name.localSheetId is not None:
                # Get sheet name by index
                sheet_names = wb.sheetnames
                if defined_name.localSheetId < len(sheet_names):
                    sheet_name = sheet_names[defined_name.localSheetId]

            # Check if it's a range (contains cell references) vs formula
            formula_text = str(defined_name.attr_text) if hasattr(defined_name, 'attr_text') and defined_name.attr_text else ""
            is_range = _is_cell_range(formula_text)

            name_record = {
                'sheet': sheet_name,
                'name': name,
                'formula': formula_text,
                'comment': getattr(defined_name, 'comment', None),
                'hidden': getattr(defined_name, 'hidden', False),
                'is_range': is_range
            }

            names_list.append(name_record)

    finally:
        wb.close()

    # Convert to DataFrame with proper columns even if empty
    if not names_list:
        # Return empty DataFrame with correct column structure
        return pd.DataFrame(columns=['sheet', 'name', 'formula', 'comment', 'hidden', 'is_range'])

    df = pd.DataFrame(names_list)

    # Sort by sheet (global first), then by name
    df['_sort_key'] = df['sheet'].fillna('')  # Global names first
    df = df.sort_values(['_sort_key', 'name']).drop('_sort_key', axis=1).reset_index(drop=True)

    return df


def _is_cell_range(formula_text: str) -> bool:
    """
    Check if a formula represents a cell range vs a complex formula.

    Parameters
    ----------
    formula_text : str
        The formula text to analyze

    Returns
    -------
    bool
        True if it appears to be a simple cell range reference
    """

    if not formula_text:
        return False

    # Remove sheet references for analysis
    clean_formula = re.sub(r'^[^!]*!', '', formula_text)

    # Simple patterns that indicate cell ranges
    range_patterns = [
        r'^[A-Z]+\d+$',  # Single cell (e.g., A1)
        r'^[A-Z]+\d+:[A-Z]+\d+$',  # Range (e.g., A1:B10)
        r'^\$?[A-Z]+\$?\d+$',  # Absolute single cell
        r'^\$?[A-Z]+\$?\d+:\$?[A-Z]+\$?\d+$',  # Absolute range
    ]

    return any(re.match(pattern, clean_formula.strip()) for pattern in range_patterns)
