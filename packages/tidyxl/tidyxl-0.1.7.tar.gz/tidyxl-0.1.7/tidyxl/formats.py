"""
Formatting information extraction functionality
"""

from typing import Any

from openpyxl import load_workbook


def xlsx_formats(path: str) -> dict[str, Any]:
    """
    Import xlsx (Excel) formatting information.

    This function extracts formatting information from Excel files,
    providing details about fonts, fills, borders, and number formats.

    Parameters
    ----------
    path : str
        Path to the Excel file (.xlsx or .xlsm)

    Returns
    -------
    dict
        Dictionary containing formatting information with keys:
        - fonts: font formatting details
        - fills: fill/background formatting details
        - borders: border formatting details
        - number_formats: number format details
    """

    wb = load_workbook(filename=path, data_only=False)

    formats: dict = {
        'fonts': [],
        'fills': [],
        'borders': [],
        'number_formats': []
    }

    # Extract font information
    if hasattr(wb, '_fonts'):
        for font in wb._fonts:
            font_info = {
                'name': font.name,
                'size': font.size,
                'bold': font.bold,
                'italic': font.italic,
                'underline': font.underline,
                'color': str(font.color.rgb) if font.color and hasattr(font.color, 'rgb') else None
            }
            formats['fonts'].append(font_info)

    # Extract fill information
    if hasattr(wb, '_fills'):
        for fill in wb._fills:
            fill_info = {
                'fill_type': fill.fill_type,
                'start_color': str(fill.start_color.rgb) if hasattr(fill.start_color, 'rgb') else None,
                'end_color': str(fill.end_color.rgb) if hasattr(fill.end_color, 'rgb') else None
            }
            formats['fills'].append(fill_info)

    # Extract border information
    if hasattr(wb, '_borders'):
        for border in wb._borders:
            border_info = {
                'left': str(border.left.style) if border.left else None,
                'right': str(border.right.style) if border.right else None,
                'top': str(border.top.style) if border.top else None,
                'bottom': str(border.bottom.style) if border.bottom else None
            }
            formats['borders'].append(border_info)

    # Extract number format information
    if hasattr(wb, '_number_formats'):
        for i, format_code in enumerate(wb._number_formats):
            formats['number_formats'].append({
                'format_code': str(format_code) if format_code else None,
                'format_id': i
            })

    return formats
