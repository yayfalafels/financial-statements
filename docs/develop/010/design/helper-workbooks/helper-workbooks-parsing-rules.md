# Helper Workbooks Parsing Rules

**Document Version:** 0.2.0  
**Last Updated:** March 8, 2026  
**Status:** Complete

## Table of Contents

1. [Overview](#overview)
2. [Parser Rule Template](#parser-rule-template)
3. [Report Layout Parsers](#report-layout-parsers)
   - [Matrix Unpivot Parser](#matrix-unpivot-parser)
   - [Multi-Section Parser](#multi-section-parser)
   - [Tabular Parser](#tabular-parser)
4. [Workbook-Specific Rules](#workbook-specific-rules)

## Overview

This document defines parsing rules for converting report-shaped legacy workbook layouts into normalized record sets suitable for database ingestion.

Target-state policy: these parsing rules must be embedded in app adapters/modules. Helper workbooks are reference artifacts only and are not required for production monthly closing.

Legacy helper workbooks expose three primary layout patterns that inform the app parser design:

1. **Tabular:** Simple row-based records with fixed columns (e.g., transactions)
2. **Matrix:** Cross-tab format with metrics in rows and time periods in columns (e.g., CPF, IBKR)
3. **Multi-Section:** Multiple distinct data blocks in one sheet with shared or separate headers

## Parser Rule Template

Use this template to document each parsing rule:

```markdown
### Parser: {parser_name}

**Rule ID:** `{unique_id}`  
**Applies To:** {workbook(s) and sheet(s)}  
**Layout Pattern:** {tabular | matrix | multi-section}

#### Input Schema

- **Header Row:** {row number or range}
- **Data Rows:** {row range}
- **Column Structure:** {describe columns}
- **Spacer Rows:** {rows to skip}
- **Spacer Columns:** {columns to skip}

#### Parsing Steps

1. {Step 1 description}
2. {Step 2 description}
...

#### Output Schema

- **Record Format:** {describe output structure}
- **Field Mapping:** {input → output field mappings}

#### Pseudocode

```
{Parsing algorithm in pseudocode}
```

#### Edge Cases

- {Edge case 1 and handling}
- {Edge case 2 and handling}

#### Validation

- {Validation rule 1}
- {Validation rule 2}

```

## Report Layout Parsers

### Matrix Unpivot Parser

**Rule ID:** `PARSE-001`  
**Applies To:** CPF workbook (all sections), IBKR workbook (all sections)  
**Layout Pattern:** Matrix (metrics × time periods)

#### Input Schema

- **Header Row:** Row 2 (shared across all sections)
- **Data Rows:** Variable per section (e.g., rows 4-10 for cpf_total)
- **Column Structure:**
  - Column A: Metric label (string)
  - Columns B-P: Month values (numeric), 15 columns representing 15 time periods
- **Spacer Rows:** Variable (e.g., row 3 before data, row 11 after data)
- **Spacer Columns:** None

#### Parsing Steps

1. Extract header row (row 2) to get month column names (columns B-P)
2. Parse month headers into period_id format (YYYY-MM)
3. For each section:
   a. Identify data row range (e.g., rows 4-10)
   b. Skip spacer rows before and after section
   c. For each data row:
      - Extract metric label from column A
      - For each month column (B-P):
        - Extract cell value
        - Create record: (period_id, account_id, metric_name, value, currency)

4. Aggregate all records from all sections

#### Output Schema

- **Record Format:** Normalized long-format records
- **Field Mapping:**
  - `period_id` ← Parsed from column header
  - `account_id` ← Section-specific constant (e.g., "CPF-OA", "IBKR-IBA")
  - `metric_name` ← Column A value
  - `amount` ← Cell value at (row, column)
  - `currency` ← Parsed from metric name or default "SGD"
  - `metric_section` ← Section identifier (e.g., "cpf_oa", "ib_net_liquidity")

#### Pseudocode

```python
def parse_matrix_section(workbook_id, section_config, account_id):
    """
    Parse a matrix-format section into normalized records.
    
    Args:
        workbook_id: Google Sheets workbook ID
        section_config: Dict with 'header' and 'data' ranges
        account_id: Account identifier for this section
    
    Returns:
        List of records: [(period_id, account_id, metric_name, amount, currency), ...]
    """
    # 1. Fetch header row
    header_range = section_config['header']
    header_row = fetch_range(workbook_id, header_range)[0]  # First row
    
    # 2. Parse month headers (columns B-P, indices 1-15)
    month_headers = header_row[1:]  # Skip column A
    period_ids = [parse_period_id(h) for h in month_headers]
    
    # 3. Fetch data rows
    data_range = section_config['data']
    data_rows = fetch_range(workbook_id, data_range)
    
    # 4. Unpivot
    records = []
    for row in data_rows:
        metric_name = row[0]  # Column A
        if is_empty(metric_name):
            continue  # Skip spacer rows
        
        month_values = row[1:]  # Columns B-P
        for i, value in enumerate(month_values):
            if is_empty(value):
                continue  # Skip missing values
            
            period_id = period_ids[i]
            currency = extract_currency(metric_name, default="SGD")
            
            record = {
                'period_id': period_id,
                'account_id': account_id,
                'metric_name': metric_name,
                'amount': float(value),
                'currency': currency,
                'metric_section': section_config['section_name']
            }
            records.append(record)
    
    return records


def parse_period_id(header_text):
    """
    Parse period identifier from column header.
    
    Examples:
        "Jan 2026" → "2026-01"
        "2026-01" → "2026-01"
        "2026 01" → "2026-01"
    """
    # Implementation depends on actual header format
    pass


def extract_currency(metric_name, default="SGD"):
    """
    Extract currency code from metric name.
    
    Examples:
        "NAV USD" → "USD"
        "NAV SGD" → "SGD"
        "Opening Balance" → "SGD" (default)
    """
    if "USD" in metric_name:
        return "USD"
    elif "SGD" in metric_name:
        return "SGD"
    else:
        return default


def is_empty(value):
    """Check if value is None, empty string, or whitespace."""
    return value is None or str(value).strip() == ""
```

#### Edge Cases

- **Empty cells:** Skip (do not create record)
- **Non-numeric values in month columns:** Log error, skip cell
- **Metric label is empty:** Skip entire row (likely spacer)
- **Column header parse failure:** Raise error (critical)
- **More than 15 months:** Adapt B-P range to actual column count

#### Validation

- All period_ids must parse successfully to YYYY-MM format
- All amounts must be numeric (float) or empty
- Metric names must be non-empty strings
- Currency codes must be valid 3-letter ISO codes
- For CPF sections: Sum(OA, SA, MA) closing balance ≈ Total closing balance per month
- For IBKR: NAV_USD * FX_rate ≈ NAV_SGD per month

---

### Multi-Section Parser

**Rule ID:** `PARSE-002`  
**Applies To:** CPF workbook, IBKR workbook  
**Layout Pattern:** Multi-section (multiple matrix blocks with shared header)

#### Input Schema

- **Header Row:** Row 2 (shared across all sections in worksheet)
- **Sections:** Multiple data blocks separated by spacer rows
- **Section Definitions:** Specified in workbook config JSON

#### Parsing Steps

1. Parse shared header row once (row 2)
2. For each section defined in config:
   a. Extract section-specific data range
   b. Apply Matrix Unpivot Parser (PARSE-001) to section
   c. Tag records with section identifier

3. Combine all section outputs into single dataset

#### Output Schema

Same as Matrix Unpivot Parser, with `metric_section` field distinguishing sections.

#### Pseudocode

```python
def parse_multi_section_workbook(workbook_id, workbook_config, account_id_map):
    """
    Parse workbook with multiple matrix sections sharing a header.
    
    Args:
        workbook_id: Google Sheets workbook ID
        workbook_config: Dict with section configs (from JSON)
        account_id_map: Dict mapping section_name → account_id
    
    Returns:
        List of all records from all sections
    """
    all_records = []
    
    for section_name, section_config in workbook_config.items():
        if section_name == 'wkbid':
            continue  # Skip workbook ID key
        
        account_id = account_id_map.get(section_name, "UNKNOWN")
        section_config['section_name'] = section_name
        
        section_records = parse_matrix_section(workbook_id, section_config, account_id)
        all_records.extend(section_records)
    
    return all_records
```

#### Edge Cases

- **Section config missing:** Raise error
- **Account ID mapping missing:** Use section name as fallback or raise error
- **Overlapping data ranges:** Raise error (config error)

#### Validation

- All sections must have non-overlapping data ranges
- All sections must reference the same header row
- Combined record count must equal sum of individual section record counts

---

### Tabular Parser

**Rule ID:** `PARSE-003`  
**Applies To:** cash-expenses (recent_txns), shared-expenses (records), financial-statements (balances, forex_rates, accounts)  
**Layout Pattern:** Tabular (simple row-based records)

#### Input Schema

- **Header Row:** Row 1 or Row 2 (depends on workbook)
- **Data Rows:** Contiguous range starting after header
- **Column Structure:** Fixed columns per sheet
- **Spacer Rows:** Optional title row before header

#### Parsing Steps

1. Extract header row to get column names
2. Skip any spacer rows before data starts
3. For each data row:
   a. Map cell values to column names
   b. Apply type coercion per column data type specification
   c. Create record as dict

4. Filter out rows where all values are empty

#### Output Schema

- **Record Format:** Direct mapping (one sheet row → one record)
- **Field Mapping:** Column name → field name (may require renaming)

#### Pseudocode

```python
def parse_tabular_sheet(workbook_id, sheet_config):
    """
    Parse a simple tabular sheet into records.
    
    Args:
        workbook_id: Google Sheets workbook ID
        sheet_config: Dict with 'header' and 'data' ranges, optional 'data_types'
    
    Returns:
        List of records (dicts)
    """
    # 1. Fetch header
    header_range = sheet_config['header']
    header_row = fetch_range(workbook_id, header_range)[0]
    
    # 2. Fetch data
    data_range = sheet_config['data']
    data_rows = fetch_range(workbook_id, data_range)
    
    # 3. Get data types if specified
    data_types = sheet_config.get('data_types', {})
    date_format = sheet_config.get('date_format', '%Y-%m-%d')
    
    # 4. Parse rows
    records = []
    for row in data_rows:
        if is_row_empty(row):
            continue
        
        record = {}
        for i, column_name in enumerate(header_row):
            if i >= len(row):
                value = None
            else:
                value = row[i]
            
            # Apply type coercion
            if column_name in data_types:
                value = coerce_type(value, data_types[column_name], date_format)
            
            record[column_name] = value
        
        records.append(record)
    
    return records


def coerce_type(value, type_name, date_format='%Y-%m-%d'):
    """
    Coerce value to specified type.
    
    Follows logic from reference/hb-finances/database.py
    """
    if is_empty(value):
        if type_name in ['int']:
            return 0  # NaN incompatible type
        elif type_name == 'float':
            return None  # NaN compatible
        else:
            return None
    
    if type_name == 'int':
        return int(float(value))  # Handle "123.0" → 123
    elif type_name == 'float':
        return float(value)
    elif type_name == 'date':
        return parse_date(value, date_format)
    elif type_name == 'str':
        return str(value)
    else:
        return value


def is_row_empty(row):
    """Check if all values in row are empty."""
    return all(is_empty(v) for v in row)
```

#### Edge Cases

- **Row shorter than header:** Pad with None values
- **Empty rows interspersed:** Skip
- **Type coercion failure:** Log error, optionally use None or raise
- **Header row is empty:** Raise error

#### Validation

- Header must have at least one non-empty column name
- Data type coercion must succeed for all specified columns
- No duplicate column names in header

---

## Workbook-Specific Rules

### CPF Workbook Parsing

**Workbook ID:** `1x9Dfq5RVwvmCGqX9aIgCRoarkhLYR3mWGmRRvQnLkbo`  
**Primary Parser:** Multi-Section Parser (PARSE-002) → Matrix Unpivot Parser (PARSE-001)

#### Section to Account ID Mapping

```python
CPF_ACCOUNT_MAP = {
    'cpf_total': 'CPF-Total',
    'cpf_oa': 'CPF-OA',
    'cpf_sa': 'CPF-SA',
    'cpf_ma': 'CPF-MA',
    'cpf_summary': 'CPF-Summary'
}
```

#### Metric Name Standardization

Expected metric names (to be validated):

- Opening Balance
- Contributions
- Interest
- Withdrawals
- Closing Balance

**Action:** Normalize variations (e.g., "Opening", "Opening Bal") to canonical names.

---

### IBKR Workbook Parsing

**Workbook ID:** `1i_ITkqvLRw5AFVmzqLaHp6PHlA2OERi3E-la00Ukngg`  
**Primary Parser:** Multi-Section Parser (PARSE-002) → Matrix Unpivot Parser (PARSE-001)

#### Section to Account ID Mapping

```python
IBKR_ACCOUNT_MAP = {
    'ib_net_liquidity': 'IBKR-IBA',  # Or tag with section: 'IBKR-IBA-NetLiquidity'
    'ib_cash': 'IBKR-IBA',
    'ib_securities': 'IBKR-IBA',
    'ib_summary': 'IBKR-IBA'
}
```

#### Currency Extraction Rules

```python
def extract_ibkr_currency(metric_name):
    """Extract currency from IBKR metric names."""
    metric_upper = metric_name.upper()
    
    if 'USD' in metric_upper:
        return 'USD'
    elif 'SGD' in metric_upper:
        return 'SGD'
    else:
        return 'USD'  # Default to USD for IBKR
```

---

### Financial Statements Workbook Parsing

**Workbook ID:** `1-Gy9kEUF0RbKWsztoZbVwbi65PXNhP1qPdylXod5JBE`  
**Primary Parser:** Tabular Parser (PARSE-003)

#### Sheets

- **balances:** Simple tabular
- **forex_rates:** Simple tabular (skip row 2 spacer)
- **accounts:** Simple tabular

#### Special Handling: forex_rates

- Data range starts at row 3 (row 2 is spacer)
- Date field requires date format parsing

---

### Cash Expenses Workbook Parsing

**Workbook ID:** `1ijbXG_wEP_icWH7xtbIO0bNVp4RbWPe1A5X1Q1i1nIo`  
**Primary Parser:** Tabular Parser (PARSE-003)

#### Special Handling

- Header row is row 2 (row 1 is title)
- Column names to be validated from live data

---

### Shared Expenses Workbook Parsing

**Workbook ID:** `1fVkiB_CXyJl2kBFEFrRb3Eb2wytWCUo1rOvveiGKZeo`  
**Primary Parser:** Tabular Parser (PARSE-003)

#### Special Handling

- Header row is row 1
- 8 columns (A-H) to be profiled from live data

---

### HomeBudget Workbook Parsing

**Workbook ID:** `1xF_cmgyKw2NHV6uj-bwo2O1D-eiyJwihlhFJSpMEKPg`  
**Primary Parser:** Tabular Parser (PARSE-003)

#### Sheet: cat_map

- 10 columns suggesting multi-level hierarchy
- Needs live inspection to determine structure
- Likely maps HomeBudget category IDs to financial statement line items

**Parsing Strategy:** To be defined after schema inspection.

---

## Implementation Notes

### Type Coercion Reference

Based on `reference/hb-finances/database.py`:

```python
NUMERIC_TYPES = ['int', 'float']

# For int: fillna(0).astype(int)  # NaN incompatible
# For float: astype(float)  # NaN compatible
# For date: parse with date_format from config
# For str: astype(str)
```

### Empty Value Handling

- `None`, empty string `""`, whitespace `"   "` all treated as empty
- For numeric fields:
  - `int`: empty → 0
  - `float`: empty → NaN or None
- For string fields: empty → None or empty string
- For date fields: empty → None

### Error Handling Strategy

1. **Header parse errors:** CRITICAL - raise exception, halt processing
2. **Type coercion errors:** Log warning, optionally skip row or field
3. **Missing data range:** raise exception
4. **Empty sections:** Log info, return empty record list
5. **Schema drift (unexpected columns):** Log warning, proceed with known columns