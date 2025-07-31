# tidyxl

A Python package that imports Excel files (.xlsx, .xlsm) into a tidy format where each cell is represented as a single row with detailed metadata. This package is inspired by and closely mirrors the functionality of the R tidyxl package.

## Installation

```bash
pip install tidyxl
```

## Quick Start

```python
from tidyxl import xlsx_cells, xlsx_sheet_names

# Get all sheet names
sheets = xlsx_sheet_names("data.xlsx")
print(f"Found sheets: {sheets}")

# Read all cells from all sheets
cells = xlsx_cells("data.xlsx")
print(f"Total cells: {len(cells)}")

# Read specific sheet only
employees = xlsx_cells("data.xlsx", sheets="Employees")

# Filter for cells with content
content_cells = cells[~cells['is_blank']]
print(content_cells[['sheet', 'address', 'data_type', 'character', 'numeric']].head())
```

## Features

- **Tidy Format**: Each Excel cell becomes one row with comprehensive metadata
- **Complete Cell Information**: Extract values, formulas, formatting, comments, and more
- **Multiple Worksheets**: Process all sheets or specify particular ones
- **Named Ranges**: Extract and analyze Excel named ranges and formulas
- **Data Validation**: Discover data validation rules applied to cells
- **Type Safety**: Separate columns for different data types (numeric, character, logical, date, error)
- **R tidyxl Compatible**: Identical API and output structure to the R package

## Core Functions

### xlsx_cells()
Extract all cell data in tidy format:

```python
from tidyxl import xlsx_cells

# Read all sheets
cells = xlsx_cells("file.xlsx")

# Read specific sheets
cells = xlsx_cells("file.xlsx", sheets=["Sheet1", "Sheet2"])
cells = xlsx_cells("file.xlsx", sheets="Data")

# Include/exclude blank cells
cells = xlsx_cells("file.xlsx", include_blank_cells=False)
```

### xlsx_sheet_names()
List all worksheet names:

```python
from tidyxl import xlsx_sheet_names

sheets = xlsx_sheet_names("file.xlsx")
# Returns: ['Sheet1', 'Data', 'Summary']
```

### xlsx_names()
Extract named ranges and formulas:

```python
from tidyxl import xlsx_names

names = xlsx_names("file.xlsx")
print(names[['name', 'formula', 'sheet', 'is_range']])
```

### xlsx_validation()
Extract data validation rules:

```python
from tidyxl import xlsx_validation

validation = xlsx_validation("file.xlsx")
print(validation[['sheet', 'ref', 'type', 'formula1']])
```

### xlsx_formats()
Extract formatting information:

```python
from tidyxl import xlsx_formats

formats = xlsx_formats("file.xlsx")
# Returns dict with keys: fonts, fills, borders, number_formats
```

## Output Structure

The `xlsx_cells()` function returns a pandas DataFrame with 23 columns matching the R tidyxl package:

| Column | Type | Description |
|--------|------|-------------|
| `sheet` | str | Worksheet name |
| `address` | str | Cell address (A1 notation) |
| `row` | int | Row number |
| `col` | int | Column number |
| `is_blank` | bool | Whether cell has a value |
| `content` | str | Raw cell value before type conversion |
| `data_type` | str | Cell type (character, numeric, logical, date, error, blank) |
| `error` | str | Error value if cell contains error |
| `logical` | bool | Boolean value if cell contains TRUE/FALSE |
| `numeric` | float | Numeric value if cell contains number |
| `date` | datetime | Date value if cell contains date |
| `character` | str | String value if cell contains text |
| `formula` | str | Formula if cell contains formula |
| `is_array` | bool | Whether formula is array formula |
| `formula_ref` | str | Range address for array/shared formulas |
| `formula_group` | int | Formula group identifier |
| `comment` | str | Cell comment text |
| `height` | float | Row height in Excel units |
| `width` | float | Column width in Excel units |
| `row_outline_level` | int | Row outline/grouping level |
| `col_outline_level` | int | Column outline/grouping level |
| `style_format` | str | Style format identifier |
| `local_format_id` | int | Local formatting identifier |

## License

This project is licensed under the MIT License.

## Acknowledgments

- Inspired by the excellent R tidyxl package by Duncan Garmonsway
- Built on top of openpyxl for Excel file processing
- Uses pandas for data structure management