---
name: gsheet-inspect
description: Inspecting Google Sheets workbooks using sqlite-gsheet package and gsheet config files for schema discovery and data validation
license: MIT
compatibility: Python 3.8+
metadata:
  author: yayfalafels
  version: 1.0.0
  repository: https://github.com/taylorhickem/sqlite-gsheet
---

## Contents

- Overview
- Summary
- Related skills
- Related documentation
- Project source-of-truth boundary
- Prerequisites
- Gsheet config file structure
- Using the existing inspection script
- Direct API usage
- When to create a new script
- Common workflows
- Troubleshooting
- Best practices
- Integration with monthly closing

## Overview

The `sqlite-gsheet` package provides a Python interface to read Google Sheets data via the Google Sheets API with pandas integration. This skill guides you through inspecting helper workbooks to discover schemas, validate data, and support monthly closing operations.

**Repository:** https://github.com/taylorhickem/sqlite-gsheet

## Related Skills

- `data-sources-inspect`: cross-source inspection methodology and stage mapping context

## Related Documentation

- **[docs/requirements/google-sheets.md](../../../docs/requirements/google-sheets.md)** - Requirement boundary and usage scope
- **[docs/requirements/dependencies.md](../../../docs/requirements/dependencies.md)** - sqlite-gsheet dependency overview
- **[docs/develop/data-sources/google-sheets-source-data.md](../../../docs/develop/data-sources/google-sheets-source-data.md)** - Source-data inventory and workbook/config references

## Summary

**Quick Reference:**

| id | task                    | path                                   |
| -- | ----------------------- | -------------------------------------- |
| 01 | inspect workbook schema | `.dev/scripts/python/inspect_helper_schemas.py` |
| 02 | configure credentials   | `.credentials/client_secret.json`      |
| 03 | define workbook mapping | `gsheet/*.json`                        |
| 04 | document source data    | `docs/develop/data-sources/google-sheets-source-data.md` |
| 05 | add custom logic        | `.dev/scripts/python/*`                |
| 06 | deep diagnostic profile | `.dev/scripts/python/profile_workbook.py` |

Reference notes:

- Requirement boundary and usage scope: [docs/requirements/google-sheets.md](../../../docs/requirements/google-sheets.md)
- Mapping and inspection method details: this skill
- Cross-source method context: skill `data-sources-inspect`
- Source-data reference details: [google-sheets-source-data.md](../../../docs/develop/data-sources/google-sheets-source-data.md)

**Remember:** Reuse existing scripts. Create new ones only for edge cases.

Tool selection guidance:

- Use `inspect_helper_schemas.py` as the default for routine multi-workbook schema inspection.
- Use `profile_workbook.py` only when you need deeper single-workbook diagnostics than the standard helper output provides.
- No single script is best for all cases; choose by inspection intent and scope.

## Project Source-of-Truth Boundary

Use this skill as the source of truth for Google Sheets inspection procedures and implementation details.

- Keep requirement documents focused on what the system must do.
- Keep procedural steps, scripts, and troubleshooting in this skill.
- For non-tool source-data references, update the data-source guide in `docs/develop/data-sources/`.

## Prerequisites

### Installation

Install the package from the local wheel file:

```bash
pip install sqlite_gsheet-2.0.1-py3-none-any.whl
```

Or if already in project dependencies:

```bash
pip install -e .
```

### Google Sheets API Credentials

**Required:** OAuth 2.0 client credentials file

**Location:** `.credentials/client_secret.json` (repository root)

**Format:** JSON file from Google Cloud Console containing:
```json
{
  "installed": {
    "client_id": "...",
    "client_secret": "...",
    "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
    ...
  }
}
```

**Setup:**
1. Create a project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Google Sheets API
3. Create OAuth 2.0 credentials (Desktop app)
4. Download JSON and save to `.credentials/client_secret.json`

## Gsheet Config File Structure

Config files are located in `gsheet/*.json` and define workbook mappings.

### Config File Format

```json
{
  "wkbid": "1i_ITkqvLRw5AFVmzqLaHp6PHlA2OERi3E-la00Ukngg",
  "region_name": {
    "header": "worksheet!$A$2:$P$2",
    "data": "worksheet!$A$4:$P$10"
  },
  "another_region": {
    "header": "worksheet!$A$2:$P$2",
    "data": "worksheet!$A$13:$P$20"
  }
}
```

**Key Properties:**
- `wkbid` - Google Sheets workbook ID (from the workbook URL)
- `{region_name}` - Named data region with header and data ranges
- `header` - A1 notation range containing column headers
- `data` - A1 notation range containing data rows

**A1 Notation Examples:**
- `worksheet!$A$2:$P$2` - Single row (headers)
- `worksheet!$A$4:$P$10` - Multiple rows (data)
- `SomeSheet!$A$1:$Z$100` - Explicit sheet name

### Available Config Files

| id | config file                | purpose                          | workbook                      |
| -- | -------------------------- | -------------------------------- | ----------------------------- |
| 01 | `cpf.json`                 | CPF account balances by subaccount | CPF helper workbook         |
| 02 | `ibkr-iba.json`            | IBKR IBA account balances        | IBKR helper workbook         |
| 03 | `shared-expenses.json`     | Shared expense allocations       | Shared expenses workbook     |
| 04 | `cash-expenses.json`       | Cash expense tracking            | Cash expenses workbook       |
| 05 | `financial-statements.json`| Financial statement consolidation| Financial statements workbook|
| 06 | `homebudget-workbook.json` | HomeBudget category/account mapping | HomeBudget mapping workbook |
| 07 | `closing-session.json`     | Monthly closing session register | Closing session workbook     |

## Using the Existing Inspection Script

**Primary Tool:** `.dev/scripts/python/inspect_helper_schemas.py`

This script provides comprehensive schema inspection for helper workbooks.

## Optional Diagnostic Profiler

Use `profile_workbook.py` when you need deeper investigation for a single workbook, such as expanded row samples, inferred key hints, or focused type and null-pattern review.

Example:

```bash
# Activate environment first
.dev\env\Scripts\Activate.ps1

# Profile one workbook config
.dev\env\Scripts\python.exe .dev/scripts/python/profile_workbook.py gsheet/financial-statements.json
```

Expected output evidence includes:

- configured sheet names discovered from the workbook config
- per-sheet row count and column count
- inferred column types and sample rows

### Run the Script

```bash
# Activate environment first
.dev\env\Scripts\Activate.ps1

# Run inspection
.dev\env\Scripts\python.exe .dev/scripts/python/inspect_helper_schemas.py
```

### What It Does

1. **Loads credentials** from `.credentials/client_secret.json`
2. **Reads config files** from `gsheet/` directory
3. **Inspects multiple workbooks in one batch run:** IBKR, CPF, category mapping, financial statements, cash-expenses, shared-expenses, closing-session
4. **For each region:**
   - Reads header row
   - Reads data rows
   - Infers column data types
   - Reports shape (rows × columns)
   - Shows non-null counts
   - Displays first row as example

### Example Output

```
==========================================================================
CPF HELPER WORKBOOK SCHEMA
==========================================================================
Workbook ID: 1x9Dfq5RVwvmCGqX9aIgCRoarkhLYR3mWGmRRvQnLkbo

--- Region: cpf_total ---
Shape: 6 rows, 16 columns

Columns (inferred types):
  Category                       object          (non-null: 6/6)
  Jan                            float64         (non-null: 6/6)
  Feb                            float64         (non-null: 5/6)
  Mar                            object          (non-null: 3/6)
  ...

First row: {'Category': 'Balance', 'Jan': 12345.67, ...}
```

## Direct API Usage

For custom inspection needs or edge cases, use the sqlite-gsheet API directly.

### Basic Pattern

```python
#!/usr/bin/env python3
import json
from pathlib import Path
from sqlgsheet import gsheet

# 1. Set credentials path (before creating engine)
creds_path = str(Path('.credentials/client_secret.json').resolve())
gsheet.CLIENT_SECRET_FILE = creds_path

# 2. Load config file
with open('gsheet/cpf.json') as f:
    config = json.load(f)

wkbid = config['wkbid']

# 3. Create engine
engine = gsheet.SheetsEngine()

# 4. Read a specific range
region_config = config['cpf_total']
header_data = engine.get_rangevalues(wkbid, region_config['header'])
data_values = engine.get_rangevalues(wkbid, region_config['data'])

# 5. Convert to DataFrame
import pandas as pd
header = header_data[-1] if header_data else []  # Last row for multi-row headers
df = pd.DataFrame(data_values, columns=header)

print(df.head())
```

### Key API Methods

#### `gsheet.SheetsEngine()`
Creates a connection to Google Sheets API.

**First Run:** Opens browser for OAuth authorization.  
**Subsequent Runs:** Uses cached token.

#### `engine.get_rangevalues(wkbid, range_notation)`
Reads data from a specific range.

**Parameters:**
- `wkbid` (str) - Workbook ID from config
- `range_notation` (str) - A1 notation like "Sheet1!$A$1:$D$10"

**Returns:** List of lists (rows of cells)

**Example:**
```python
data = engine.get_rangevalues(
    "1x9Dfq5RVwvmCGqX...",
    "worksheet!$A$4:$P$10"
)
# Returns: [['row1_col1', 'row1_col2', ...], ['row2_col1', ...]]
```

### Handling Multi-Row Headers

Some workbooks have headers spanning multiple rows (e.g., month/day structure).

**Best Practice:** Use the last row as column names.

```python
header_data = engine.get_rangevalues(wkbid, header_range)

# Multi-row header: [['2026', '2026', ...], ['Jan', 'Feb', ...]]
# Take last row for actual column names
header = header_data[-1] if header_data else []

df = pd.DataFrame(data_values, columns=header)
```

## When to Create a New Script

**Reuse `.dev/scripts/python/inspect_helper_schemas.py` for:**
- Inspecting standard helper workbook schemas
- Validating config file mappings
- Discovering column names and data types
- Comparing actual vs documented schemas

**Create a new script only for edge cases:**
1. **Complex transformations** - Data requires significant preprocessing
2. **Cross-workbook validation** - Comparing data across multiple workbooks
3. **Automated data quality checks** - Running validation rules on data
4. **One-off migration tasks** - Temporary scripts for data migration

### Template for New Scripts

If you must create a new script, follow this pattern:

```python
#!/usr/bin/env python3
"""
Brief description of what this script does.

Usage:
    python script_name.py

Why this exists:
    Explain the edge case that inspect_helper_schemas.py doesn't cover.
"""

import pandas as pd
import json
from pathlib import Path
from sqlgsheet import gsheet

# Set credentials (required before using gsheet)
gsheet.CLIENT_SECRET_FILE = str(Path('.credentials/client_secret.json').resolve())

def main():
    # Your custom logic here
    engine = gsheet.SheetsEngine()
    
    # Load config
    with open('gsheet/your_config.json') as f:
        config = json.load(f)
    
    # Perform edge case operation
    # ...

if __name__ == "__main__":
    main()
```

**Save location:** `.dev/scripts/python/your_script_name.py`

## Common Workflows

### Discover Schema for New Workbook

1. **Create config file** in `gsheet/new_workbook.json`:
   ```json
   {
     "wkbid": "WORKBOOK_ID_FROM_URL",
     "region_name": {
       "header": "Sheet1!$A$1:$Z$1",
       "data": "Sheet1!$A$2:$Z$100"
     }
   }
   ```

2. **Update inspection script** to include new workbook:
   ```python
  # Add to .dev/scripts/python/inspect_helper_schemas.py main()
   new_config = gsheet_dir / "new_workbook.json"
   inspect_workbook(str(new_config), "new_workbook")
   ```

3. **Run inspection** and document results in `docs/develop/helper-workbooks-schema-profiles.md`

### Validate Data Against Expected Schema

```python
# After loading DataFrame from gsheet
expected_columns = ['Category', 'Jan', 'Feb', 'Mar']
actual_columns = df.columns.tolist()

missing = set(expected_columns) - set(actual_columns)
extra = set(actual_columns) - set(expected_columns)

if missing:
    print(f"WARNING: Missing columns: {missing}")
if extra:
    print(f"INFO: Extra columns (may be new): {extra}")
```

### Export Schema Documentation

```python
# After inspection, generate schema report
schema_info = {
    'workbook': 'CPF Helper',
    'regions': {}
}

for region_name, region_config in config.items():
    if region_name == 'wkbid':
        continue
    
    # ... load df for region ...
    
    schema_info['regions'][region_name] = {
        'shape': df.shape,
        'columns': df.dtypes.astype(str).to_dict(),
        'sample': df.iloc[0].to_dict() if len(df) > 0 else None
    }

# Save to JSON for documentation
with open('schema_report.json', 'w') as f:
    json.dump(schema_info, f, indent=2)
```

## Troubleshooting

### AuthenticationError: Credentials not found

**Cause:** Missing or invalid `.credentials/client_secret.json`

**Fix:**
1. Download OAuth credentials from Google Cloud Console
2. Save to `.credentials/client_secret.json`
3. Ensure path is correct relative to script execution

### HttpError 403: Permission denied

**Cause:** Service account or OAuth user doesn't have access to workbook

**Fix:**
1. Share the Google Sheet with your OAuth email
2. Grant at least "Viewer" permission
3. Re-run script

### ValueError: columns passed, must match data

**Cause:** Header row has different column count than data rows

**Fix:**
1. Check A1 notation ranges in config file
2. Ensure header and data ranges have same column span
3. Handle ragged data:
   ```python
   # Pad columns if needed
   max_cols = len(header)
   data_values = [row + [None] * (max_cols - len(row)) for row in data_values]
   ```

### Empty DataFrame returned

**Cause:** Range notation doesn't match actual data location

**Fix:**
1. Open the Google Sheet manually
2. Verify sheet name and cell ranges
3. Update config file with correct A1 notation
4. Note: Sheet names are case-sensitive

## Best Practices

1. **Always use the existing script first** - `.dev/scripts/python/inspect_helper_schemas.py` covers most use cases
2. **Set credentials path early** - Before creating `gsheet.SheetsEngine()`
3. **Cache headers when processing multiple regions** - Avoid redundant API calls
4. **Use last row for multi-row headers** - Gives clean column names
5. **Handle ragged data** - Not all rows may have same column count
6. **Document new schemas** - Update `docs/develop/helper-workbooks-schema-profiles.md`
7. **Version config files** - Track changes to range mappings in git
8. **Test with small ranges first** - Validate A1 notation before full reads
9. **Choose tool by intent** - use `inspect_helper_schemas.py` for primary batch coverage and `profile_workbook.py` only for deeper single-workbook diagnostics

## Integration with Monthly Closing

### Design Context

Helper workbooks are **reference artifacts only** for the monthly closing system. The app-native workflow uses embedded adapters, not workbook ingestion.

**See:** skill `data-sources-inspect` for current inspection boundaries and migration context.

### When to Inspect Workbooks

1. **Parity mode** - Validate app-native adapters produce same results as workbooks
2. **Discovery phase** - Document schemas before building adapters
3. **Migration** - One-time data backfill from historical workbook data
4. **Debugging** - Compare workbook data vs app database when troubleshooting

### Production Mode Restriction

⚠️ **Production mode MUST NOT use workbook adapters or gsheet inspection.**

Runtime mode gates enforced in app:
- `production_mode` - Workbook adapters forbidden
- `parity_mode` - Workbook comparison allowed (with approval)
- `backfill_mode` - Historical workbook import allowed (with approval)

**See:** skill `data-sources-inspect` for enforcement and mode-usage guidance.

