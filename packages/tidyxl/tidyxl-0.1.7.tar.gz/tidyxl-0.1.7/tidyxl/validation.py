"""
Data validation extraction functionality
"""


import pandas as pd
from openpyxl import load_workbook


def xlsx_validation(
    path: str,
    sheets: str | list[str] | None = None,
    check_filetype: bool = True
) -> pd.DataFrame:
    """
    Import data validation rules of cells in xlsx (Excel) files.

    Extracts data validation rules from Excel cells, including numeric ranges,
    date constraints, list restrictions, and custom formula-driven rules.

    Parameters
    ----------
    path : str
        Path to the Excel file (.xlsx or .xlsm)
    sheets : str, list of str, or None
        Worksheet names to read. If None, reads all sheets.
    check_filetype : bool, default True
        Whether to check that the file is a valid xlsx/xlsm file

    Returns
    -------
    pd.DataFrame
        A DataFrame with columns:
        - sheet: Worksheet with validation rule
        - ref: Cell addresses with rules (e.g., 'A1:A10')
        - type: Data validation type (whole, decimal, list, date, time, textLength, custom)
        - operator: Comparison operator (between, equal, notEqual, greaterThan, etc.)
        - formula1: First validation criterion
        - formula2: Second validation criterion (for between/notBetween)
        - allow_blank: Whether blank cells are allowed
        - show_input_message: Whether to show input message
        - show_error_message: Whether to show error message
        - prompt_title: Input message title
        - prompt: Input message text
        - error_title: Error message title
        - error: Error message text
        - error_style: Error style (stop, warning, information)
    """

    # Check file type if requested
    if check_filetype:
        if not path.lower().endswith(('.xlsx', '.xlsm')):
            raise ValueError("File must be .xlsx or .xlsm format")

    # Load workbook
    wb = load_workbook(filename=path, data_only=False)

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

    validation_list = []

    try:
        for sheet_name in sheet_names:
            ws = wb[sheet_name]

            # Get data validation rules
            if hasattr(ws, 'data_validations'):
                for dv in ws.data_validations.dataValidation:
                    validation_record = {
                        'sheet': sheet_name,
                        'ref': str(dv.sqref) if dv.sqref else None,
                        'type': dv.type,
                        'operator': dv.operator,
                        'formula1': dv.formula1,
                        'formula2': dv.formula2,
                        'allow_blank': dv.allowBlank,
                        'show_input_message': dv.showInputMessage,
                        'show_error_message': dv.showErrorMessage,
                        'prompt_title': dv.promptTitle,
                        'prompt': dv.prompt,
                        'error_title': dv.errorTitle,
                        'error': dv.error,
                        'error_style': dv.errorStyle
                    }

                    validation_list.append(validation_record)

    finally:
        wb.close()

    # Convert to DataFrame with proper columns even if empty
    if not validation_list:
        # Return empty DataFrame with correct column structure
        expected_columns = [
            'sheet', 'ref', 'type', 'operator', 'formula1', 'formula2',
            'allow_blank', 'show_input_message', 'show_error_message',
            'prompt_title', 'prompt', 'error_title', 'error', 'error_style'
        ]
        return pd.DataFrame(columns=expected_columns)

    df = pd.DataFrame(validation_list)

    # Sort by sheet, then by ref
    df = df.sort_values(['sheet', 'ref']).reset_index(drop=True)

    return df
