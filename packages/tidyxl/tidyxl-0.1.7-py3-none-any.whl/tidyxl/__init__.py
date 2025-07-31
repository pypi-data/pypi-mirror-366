"""
tidyxl: Import Excel files into tidy format with cell-level data extraction

This package provides functionality to import Excel (.xlsx, .xlsm) files
into a tidy format where each row represents a single cell with all its
properties including value, formatting, formulas, and comments.
"""

from .cells import xlsx_cells
from .formats import xlsx_formats
from .validation import xlsx_validation
from .workbook import xlsx_names, xlsx_sheet_names

__version__ = "0.1.0"
__all__ = ["xlsx_cells", "xlsx_formats", "xlsx_sheet_names", "xlsx_names", "xlsx_validation"]
