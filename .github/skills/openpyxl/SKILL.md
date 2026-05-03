---
name: openpyxl
description: Use when reading or writing Excel xlsx/xlsm files for bank statement ingest, bill parsing, or any source adapter that consumes Excel-format data files.
---

# openpyxl

## Summary

Use this skill for reusable openpyxl knowledge that applies to any module reading or writing Excel workbooks. Keep source-specific column mapping and validation logic in the source adapter agent. Use this skill for generic Workbook, Worksheet, and Cell API guidance.

## Apply This Skill When

- Reading a bank statement, bill export, or reference file delivered in xlsx or xlsm format.
- Navigating worksheets by name or index to locate the relevant sheet.
- Iterating rows or accessing specific cells to extract transaction or balance data.
- Writing formatted output to an xlsx file for review or archival.

## Rules

- Use `openpyxl.load_workbook(path, read_only=True, data_only=True)` for reading source files; `read_only=True` reduces memory for large files; `data_only=True` returns computed cell values rather than formulas.
- Access worksheets by name (`wb['Sheet1']`) rather than by index to avoid silent failures when worksheet order changes.
- Iterate rows with `ws.iter_rows(min_row=2, values_only=True)` to skip headers and get plain Python values directly.
- Do not use openpyxl for reading `.xls` (Excel 97-2003) files; those require `xlrd`.
- Install `defusedxml` alongside openpyxl in any environment that reads externally supplied workbooks; openpyxl does not guard against XML billion-laughs or quadratic-blowup attacks by default.
- Close workbooks after reading by calling `wb.close()` or using a `with` block via `contextlib.closing()` to release file handles.
- Never store openpyxl `Cell` objects across worksheet iterations; extract values immediately.

## Official Sources

- openpyxl documentation: https://openpyxl.readthedocs.io/en/stable/
  Covers `load_workbook()`, `Workbook`, `Worksheet`, `Cell`, row iteration, cell value assignment, and the security note about defusedxml.
- openpyxl tutorial: https://openpyxl.readthedocs.io/en/stable/tutorial.html
  Demonstrates the core read-write pattern: `load_workbook()`, `.active`, cell access, `.append()`, and `.save()`.

## Useful Takeaways

- `data_only=True` is required when the source file uses formulas; without it, cell values may be `None` until Excel has recalculated them.
- Key API classes are `openpyxl.workbook.workbook.Workbook`, `openpyxl.worksheet.worksheet.Worksheet`, and `openpyxl.cell.cell.Cell`.
- `ws.iter_rows(values_only=True)` returns tuples of plain Python values; this is faster and safer than accessing `.value` on each Cell object individually.
- openpyxl supports xlsx, xlsm, xltx, and xltm formats only; it does not support the older xls binary format.

## Validation Focus

- `defusedxml` is listed as a dependency for any environment that reads external workbooks.
- Worksheet is accessed by name, not by index.
- `data_only=True` is set when formulas may be present in source files.
- File handles are closed after reading; workbook is not held open beyond the extraction step.
