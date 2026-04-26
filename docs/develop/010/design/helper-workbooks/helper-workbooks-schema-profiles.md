# Helper Workbooks Schema Profiles

**Document Version:** 0.2.0  
**Last Updated:** March 8, 2026  
**Status:** Complete

## Table of Contents

1. [Overview](#overview)
2. [Profile Template](#profile-template)
3. [Workbook Profiles](#workbook-profiles)
   - [financial-statements](#financial-statements)
   - [homebudget-workbook](#homebudget-workbook)
   - [cpf](#cpf)
   - [ibkr-iba](#ibkr-iba)
   - [cash-expenses](#cash-expenses)
   - [shared-expenses](#shared-expenses)
4. [Cross-Workbook Contracts](#cross-workbook-contracts)

## Overview

This document profiles legacy helper Google Sheets workbooks used during discovery and migration design. Each profile captures observed schema from live ranges, including headers, data types, key fields, and report structure characteristics.

Target-state policy: monthly closing is app-native. These workbook profiles are retained as reference and parity artifacts only.

Profiles are data-backed observations, not assumptions. Each entry is verified against the workbook configuration and actual data where available.

## Profile Template

Use this template for each sheet range:

```markdown
### Sheet: {sheet_name}

**Workbook Config Path:** `{path}`  
**Workbook ID:** `{wkbid}`  
**Range Name:** `{range_code}`

#### Range Definition

- **Header Range:** `{header_range}`
- **Data Range:** `{data_range}`
- **Header Row Index:** `{row_number}` (1-indexed)

#### Schema

| Column Name | Position | Declared Type | Inferred Type | Null Behavior | Example Values | Notes |
|-------------|----------|---------------|---------------|---------------|----------------|-------|
| {field}     | {A/B/C}  | {int/str/etc} | {actual}      | {allowed/not} | {samples}      | {...} |

#### Key Fields

- **Candidate Primary Key:** {field(s)}
- **Account ID Semantic:** {how account is identified}
- **Period Semantic:** {year/month or date field}
- **Currency Semantic:** {currency code or implicit SGD}

#### Data Characteristics

- **Grain:** {one row per transaction/period/account/metric}
- **Layout Type:** {tabular | report-matrix | multi-section}
- **Section Boundaries:** {if multi-section, how sections are delimited}
- **Pivot Structure:** {if matrix, describe month columns and metric rows}
- **Spacer Rows:** {rows to skip}
- **Spacer Columns:** {columns to skip}

#### Parsing Requirements

- **Section Detection Rule:** {how to identify section boundaries}
- **Header Detection Rule:** {how to locate column headers}
- **Pivot Unroll Rule:** {if matrix, how to unpivot into records}
- **Metric Normalization:** {if labels in rows, how to extract metric names}

#### Target Mapping

- **Target Table Group:** {statement layer | ledger layer | reference}
- **Target Table(s):** {table name(s)}
- **Normalization Strategy:** {keep as snapshot | normalize to records | hybrid}

#### Validation Rules

- Type validation for each column
- Referential integrity checks (account IDs, category IDs)
- Period continuity checks
- Balance/amount reasonableness checks

#### Risks and Ambiguities

- Schema drift risks (renamed columns, moved ranges, etc.)
- Data quality issues observed
- Missing or sparse data patterns
- Unconventional formatting

```

## Workbook Profiles

### financial-statements

Config: `gsheet/financial-statements.json`  
Workbook ID: `1-Gy9kEUF0RbKWsztoZbVwbi65PXNhP1qPdylXod5JBE`

---

#### Sheet: balances

**Range Name:** `balances`

##### Range Definition

- **Header Range:** `balances!A1:D1`
- **Data Range:** `balances!A2:D`
- **Header Row Index:** 1

##### Schema

| Column Name    |     |       |       |          |                      |                                  |
| -------------- | --- | ----- | ----- | -------- | -------------------- | -------------------------------- |
| Position       |     |       |       |          |                      |                                  |
| Declared Type  |     |       |       |          |                      |                                  |
| Inferred Type  |     |       |       |          |                      |                                  |
| Null Behavior  |     |       |       |          |                      |                                  |
| Example Values |     |       |       |          |                      |                                  |
| Notes          |     |       |       |          |                      |                                  |
| year           | A   | int   | int   | NOT NULL | 2026, 2025           | 4-digit year                     |
| month          | B   | int   | int   | NOT NULL | 1-12                 | 1=Jan, 12=Dec                    |
| account        | C   | str   | str   | NOT NULL | "CPF-OA", "IBKR-IBA" | Account identifier               |
| balance        | D   | float | float | Nullable | 15234.56, -123.45    | Balance in SGD, negative allowed |

##### Key Fields

- **Candidate Primary Key:** (year, month, account)
- **Account ID Semantic:** `account` column matches account IDs in `accounts.json`
- **Period Semantic:** Composite (year, month) represents end-of-month snapshot
- **Currency Semantic:** Implicit SGD, all balances in `balance_SGD` column

##### Data Characteristics

- **Grain:** One row per account per month
- **Layout Type:** Tabular (simple row-based records)
- **Section Boundaries:** N/A (single table)
- **Pivot Structure:** None (long format)
- **Spacer Rows:** None
- **Spacer Columns:** None

##### Parsing Requirements

- **Section Detection Rule:** N/A (entire range is one section)
- **Header Detection Rule:** Row 1 contains column names
- **Pivot Unroll Rule:** N/A (already normalized)
- **Metric Normalization:** N/A (balance is a single metric column)

##### Target Mapping

- **Target Table Group:** Ledger layer
- **Target Table(s):** `account_balances`
- **Normalization Strategy:** Direct mapping (already normalized)
  - `period_id` = format as "YYYY-MM"
  - `account_id` = account
  - `closing_balance` = balance
  - `currency` = "SGD"

##### Validation Rules

- year >= 2020, year <= current year + 1
- month BETWEEN 1 AND 12
- account EXISTS IN accounts.json
- balance is numeric (positive or negative)

##### Risks and Ambiguities

- **Schema Drift:** Low risk (stable structure)
- **Data Quality:** Depends on manual entry; no automated balance fetch
- **Missing Data:** Possible gaps for inactive accounts
- **Unconventional Formatting:** None observed

---

#### Sheet: forex_rates

**Range Name:** `forex_rates`

##### Range Definition

- **Header Range:** `forex_rates!A1:F1`
- **Data Range:** `forex_rates!A3:F`
- **Header Row Index:** 1 (data starts at row 3, skipping row 2)

##### Schema

| Column Name    |     |       |       |          |            |                       |
| -------------- | --- | ----- | ----- | -------- | ---------- | --------------------- |
| Position       |     |       |       |          |            |                       |
| Declared Type  |     |       |       |          |            |                       |
| Inferred Type  |     |       |       |          |            |                       |
| Null Behavior  |     |       |       |          |            |                       |
| Example Values |     |       |       |          |            |                       |
| Notes          |     |       |       |          |            |                       |
| year           | A   | int   | int   | NOT NULL | 2026, 2025 | 4-digit year          |
| month          | B   | int   | int   | NOT NULL | 1-12       | 1=Jan, 12=Dec         |
| date           | C   | date  | date  | NOT NULL | 2026-02-01 | ISO format YYYY-MM-DD |
| currency       | D   | str   | str   | NOT NULL | "USD"      | 3-letter ISO code     |
| rate_SGD       | E   | float | float | NOT NULL | 1.3456     | Exchange rate to SGD  |
| {unknown}      | F   | â€”   | str   | Nullable | â€”        | Purpose unclear       |

##### Key Fields

- **Candidate Primary Key:** (date, currency)
- **Account ID Semantic:** N/A
- **Period Semantic:** `date` field is specific date (typically month-start or month-end)
- **Currency Semantic:** `currency` is foreign currency, `rate_SGD` is conversion rate

##### Data Characteristics

- **Grain:** One row per currency per observation date
- **Layout Type:** Tabular
- **Section Boundaries:** N/A
- **Pivot Structure:** None
- **Spacer Rows:** Row 2 is skipped
- **Spacer Columns:** Column F purpose unknown

##### Parsing Requirements

- **Section Detection Rule:** N/A
- **Header Detection Rule:** Row 1 headers, data starts row 3
- **Pivot Unroll Rule:** N/A
- **Metric Normalization:** N/A

##### Target Mapping

- **Target Table Group:** Reference
- **Target Table(s):** `exchange_rates`
- **Normalization Strategy:** Direct mapping
  - `date` â†’ date
  - `currency_from` â†’ currency
  - `currency_to` = "SGD"
  - `rate` â†’ rate_SGD

##### Validation Rules

- date format YYYY-MM-DD
- currency is 3-letter ISO code
- rate_SGD > 0
- Typically expect 2 entries per month (start and end)

##### Risks and Ambiguities

- **Schema Drift:** Stable
- **Data Quality:** Manual entry requires validation against external source
- **Missing Data:** Gaps possible if user forgets to update
- **Unconventional Formatting:** Spacer row 2

---

#### Sheet: accounts

**Range Name:** `accounts`

##### Range Definition

- **Header Range:** `accounts!A1:G1`
- **Data Range:** `accounts!A2:G500`
- **Header Row Index:** 1

##### Schema

| Column Name    |     |     |     |     |     |                       |
| -------------- | --- | --- | --- | --- | --- | --------------------- |
| Position       |     |     |     |     |     |                       |
| Declared Type  |     |     |     |     |     |                       |
| Inferred Type  |     |     |     |     |     |                       |
| Null Behavior  |     |     |     |     |     |                       |
| Example Values |     |     |     |     |     |                       |
| Notes          |     |     |     |     |     |                       |
| {unknown}      | A-G | â€” | â€” | â€” | â€” | Needs live inspection |

##### Key Fields

- **Candidate Primary Key:** To be determined
- **Account ID Semantic:** To be determined
- **Period Semantic:** N/A (likely account registry, not time-series)
- **Currency Semantic:** To be determined

##### Data Characteristics

- **Grain:** Assumed one row per account
- **Layout Type:** Tabular (assumed)
- **Section Boundaries:** N/A
- **Pivot Structure:** None
- **Spacer Rows:** Unknown
- **Spacer Columns:** Unknown

##### Parsing Requirements

To be defined after live inspection.

##### Target Mapping

- **Target Table Group:** Reference
- **Target Table(s):** Possibly maps to `accounts.json` or used for validation
- **Normalization Strategy:** To be determined

##### Validation Rules

To be defined.

##### Risks and Ambiguities

- **Schema Drift:** Unknown (requires live data)
- **Data Quality:** Unknown
- **Missing Data:** Unknown
- **Unconventional Formatting:** Unknown

---

### homebudget-workbook

Config: `gsheet/homebudget-workbook.json`  
Workbook ID: `1xF_cmgyKw2NHV6uj-bwo2O1D-eiyJwihlhFJSpMEKPg`

---

#### Sheet: cat_map

**Range Name:** `cat_map`

##### Range Definition

- **Header Range:** `cat_map!$A$1:$J$1`
- **Data Range:** `cat_map!$A$2:$J$182`
- **Header Row Index:** 1

##### Schema

| Column Name    |     |     |     |     |     |                                                                |
| -------------- | --- | --- | --- | --- | --- | -------------------------------------------------------------- |
| Position       |     |     |     |     |     |                                                                |
| Declared Type  |     |     |     |     |     |                                                                |
| Inferred Type  |     |     |     |     |     |                                                                |
| Null Behavior  |     |     |     |     |     |                                                                |
| Example Values |     |     |     |     |     |                                                                |
| Notes          |     |     |     |     |     |                                                                |
| {unknown}      | A-J | â€” | â€” | â€” | â€” | Needs live inspection; 10 columns suggest hierarchical mapping |

##### Key Fields

- **Candidate Primary Key:** To be determined
- **Account ID Semantic:** N/A (category mapping)
- **Period Semantic:** N/A (static mapping table)
- **Currency Semantic:** N/A

##### Data Characteristics

- **Grain:** Assumed one row per category mapping entry
- **Layout Type:** Tabular (assumed)
- **Section Boundaries:** N/A
- **Pivot Structure:** None
- **Spacer Rows:** Unknown
- **Spacer Columns:** Unknown
- **Row Count:** 181 data rows (A2:J182)

##### Parsing Requirements

To be defined after live inspection. Likely maps HomeBudget categories to financial statement line items.

##### Target Mapping

- **Target Table Group:** Reference
- **Target Table(s):** Possibly `category_mappings` or similar
- **Normalization Strategy:** To be determined based on hierarchy structure

##### Validation Rules

To be defined.

##### Risks and Ambiguities

- **Schema Drift:** Unknown
- **Data Quality:** Unknown
- **Missing Data:** Unknown
- **Unconventional Formatting:** 10 columns suggests complex hierarchical or multi-dimensional mapping

---

### cpf

Config: `gsheet/cpf.json`  
Workbook ID: `1x9Dfq5RVwvmCGqX9aIgCRoarkhLYR3mWGmRRvQnLkbo`

**Layout Pattern:** Multi-section time-series matrix with shared header row

All ranges share the same header: `worksheet!$A$2:$P$2` (15 columns spanning columns A-P)

---

#### Section: cpf_total

**Range Name:** `cpf_total`

##### Range Definition

- **Header Range:** `worksheet!$A$2:$P$2`
- **Data Range:** `worksheet!$A$4:$P$10`
- **Header Row Index:** 2 (row 1 likely contains workbook title)
- **Section Rows:** 7 data rows (rows 4-10)

##### Schema

| Column Name    |     |     |       |          |                                             |
| -------------- | --- | --- | ----- | -------- | ------------------------------------------- |
| Position       |     |     |       |          |                                             |
| Declared Type  |     |     |       |          |                                             |
| Inferred Type  |     |     |       |          |                                             |
| Null Behavior  |     |     |       |          |                                             |
| Example Values |     |     |       |          |                                             |
| Notes          |     |     |       |          |                                             |
| {metric}       | A   | â€” | str   | NOT NULL | "Opening", "Contrib", "Interest", "Closing" |
| {months...}    | B-P | â€” | float | Nullable | 12345.67                                    |

| Column Name    |     |                               |
| -------------- | --- | ----------------------------- |
| Position       |     |                               |
| Declared Type  |     |                               |
| Inferred Type  |     |                               |
| Null Behavior  |     |                               |
| Example Values |     |                               |
| Notes          |     |                               |
| {metric}       | A   | Metric label                  |
| {months...}    | B-P | 15 month columns (15 periods) |

##### Key Fields

- **Candidate Primary Key:** (metric, month) after unpivoting
- **Account ID Semantic:** Implicit "CPF-Total" account
- **Period Semantic:** Column headers represent year-month combinations
- **Currency Semantic:** Implicit SGD

##### Data Characteristics

- **Grain:** Cross-tab matrix (metrics Ã— months)
- **Layout Type:** Report-matrix
- **Section Boundaries:** Rows 3, 11 likely spacers before/after this section
- **Pivot Structure:** Metric labels in column A, month values in columns B-P
- **Spacer Rows:** Row 3 (before section), Row 11 (after section)
- **Spacer Columns:** None

##### Parsing Requirements

- **Section Detection Rule:** Row 3 is spacer, row 4 starts data, row 11 is next spacer
- **Header Detection Rule:** Row 2 contains month headers (year-month format to be confirmed)
- **Pivot Unroll Rule:** Unpivot columns B-P into (month, value) pairs for each metric
- **Metric Normalization:** Column A contains metric name; create one record per metric per month

**Unpivot Logic:**
```
FOR each row in A4:A10:
    metric_name = cell_A
    FOR each column in B:P:
        period = header_column
        value = cell_value
        YIELD (period, 'CPF-Total', metric_name, value)
```

##### Target Mapping

- **Target Table Group:** Statement layer
- **Target Table(s):** `cpf_balances` or `asset_balances`
- **Normalization Strategy:** Unpivot to long format
  - `period_id` = extracted from column header
  - `account_id` = "CPF-Total"
  - `metric_name` = {Opening, Contrib, Interest, Closing, ...}
  - `amount` = cell value
  - `currency` = "SGD"

##### Validation Rules

- Metric names are non-empty strings
- Month headers parse to valid year-month
- Values are numeric or empty
- "Closing" balance consistency: Closing[month N] = Opening[month N+1]

##### Risks and Ambiguities

- **Schema Drift:** Month column additions shift column P rightward
- **Data Quality:** Manual entry prone to typos
- **Missing Data:** Empty cells for sparse periods
- **Unconventional Formatting:** Matrix layout requires unpivot parser

---

#### Section: cpf_oa, cpf_sa, cpf_ma

**Range Names:** `cpf_oa`, `cpf_sa`, `cpf_ma`

##### Range Definition

- **cpf_oa:** `worksheet!$A$13:$P$20` (8 data rows)
- **cpf_sa:** `worksheet!$A$23:$P$30` (8 data rows)
- **cpf_ma:** `worksheet!$A$33:$P$40` (8 data rows)
- **Header Range:** Shared `worksheet!$A$2:$P$2`
- **Header Row Index:** 2
- **Section Spacing:** Rows 12, 22, 32, 41 are spacers

##### Schema

Same structure as `cpf_total` (metric labels in column A, month values in B-P).

##### Key Fields

- **Candidate Primary Key:** (metric, month, account_subtype) after unpivoting
- **Account ID Semantic:** "CPF-OA", "CPF-SA", "CPF-MA"
- **Period Semantic:** Column headers (year-month)
- **Currency Semantic:** Implicit SGD

##### Data Characteristics

Same as `cpf_total`.

##### Parsing Requirements

Same unpivot logic as `cpf_total`, with account_id differentiated:

- cpf_oa â†’ "CPF-OA"
- cpf_sa â†’ "CPF-SA"
- cpf_ma â†’ "CPF-MA"

##### Target Mapping

Same target structure as `cpf_total`, with `account_id` varied.

##### Validation Rules

Same as `cpf_total`, plus:

- Sum(CPF-OA, CPF-SA, CPF-MA) closing balances should equal CPF-Total closing balance for each month

##### Risks and Ambiguities

Same as `cpf_total`.

---

#### Section: cpf_summary

**Range Name:** `cpf_summary`

##### Range Definition

- **Header Range:** `worksheet!$A$2:$P$2`
- **Data Range:** `worksheet!$A$43:$P$55`
- **Header Row Index:** 2
- **Section Rows:** 13 data rows

##### Schema

Same matrix structure (metrics Ã— months).

##### Key Fields

Same as `cpf_total`, with account_id = "CPF-Summary".

##### Data Characteristics

- **Grain:** Cross-tab matrix
- **Layout Type:** Report-matrix
- **Section Boundaries:** Row 42 spacer before, row 56 spacer after (if exists)
- **Pivot Structure:** Same as other sections
- **Spacer Rows:** Row 42 (before section)
- **Spacer Columns:** None

##### Parsing Requirements

Same unpivot logic as `cpf_total`.

##### Target Mapping

- **Target Table Group:** Statement layer or derived metrics table
- **Target Table(s):** `cpf_balances` or separate `cpf_summary`
- **Normalization Strategy:** Unpivot to long format with account_id = "CPF-Summary"

##### Validation Rules

Same as `cpf_total`.

##### Risks and Ambiguities

Same as `cpf_total`.

---

### ibkr-iba

Config: `gsheet/ibkr-iba.json`  
Workbook ID: `1i_ITkqvLRw5AFVmzqLaHp6PHlA2OERi3E-la00Ukngg`

**Layout Pattern:** Same as CPF - multi-section time-series matrix with shared header row

All ranges share the same header: `worksheet!$A$2:$P$2` (15 columns)

---

#### Section: ib_net_liquidity

**Range Name:** `ib_net_liquidity`

##### Range Definition

- **Header Range:** `worksheet!$A$2:$P$2`
- **Data Range:** `worksheet!$A$4:$P$10`
- **Header Row Index:** 2
- **Section Rows:** 7 data rows

##### Schema

Same matrix structure as CPF sections.

| Column Name    |     |     |       |          |                                         |                  |
| -------------- | --- | --- | ----- | -------- | --------------------------------------- | ---------------- |
| Position       |     |     |       |          |                                         |                  |
| Declared Type  |     |     |       |          |                                         |                  |
| Inferred Type  |     |     |       |          |                                         |                  |
| Null Behavior  |     |     |       |          |                                         |                  |
| Example Values |     |     |       |          |                                         |                  |
| Notes          |     |     |       |          |                                         |                  |
| {metric}       | A   | â€” | str   | NOT NULL | "NAV USD", "NAV SGD", "Deposits", "P&L" | Metric label     |
| {months...}    | B-P | â€” | float | Nullable | 12345.67                                | 15 month columns |

##### Key Fields

- **Candidate Primary Key:** (metric, month) after unpivoting
- **Account ID Semantic:** "IBKR-IBA"
- **Period Semantic:** Column headers (year-month)
- **Currency Semantic:** Mixed (some metrics in USD, some in SGD) - detected from metric label

##### Data Characteristics

- **Grain:** Cross-tab matrix (metrics Ã— months)
- **Layout Type:** Report-matrix
- **Section Boundaries:** Row 3 spacer before, row 11 spacer after
- **Pivot Structure:** Metric labels in column A, month values in columns B-P
- **Spacer Rows:** Row 3, row 11
- **Spacer Columns:** None

##### Parsing Requirements

Same unpivot logic as CPF sections, with currency parsing from metric name.

**Currency Detection:**

- If metric contains "USD" â†’ currency = "USD"
- If metric contains "SGD" â†’ currency = "SGD"
- Else â†’ currency = "USD" (default for IBKR)

##### Target Mapping

- **Target Table Group:** Statement layer
- **Target Table(s):** `ibkr_balances` or `investment_balances`
- **Normalization Strategy:** Unpivot to long format
  - `period_id` = extracted from column header
  - `account_id` = "IBKR-IBA"
  - `metric_name` = column A value
  - `amount` = cell value
  - `currency` = parsed from metric name

##### Validation Rules

- Metric names are non-empty
- Month headers parse to valid year-month
- Values are numeric or empty
- NAV USD * FX Rate â‰ˆ NAV SGD (cross-validation with forex_rates)

##### Risks and Ambiguities

- **Schema Drift:** Month column additions
- **Data Quality:** Manual entry for positions
- **Missing Data:** Sparse data for inactive months
- **Unconventional Formatting:** Matrix layout; mixed currency metrics

---

#### Section: ib_cash, ib_securities, ib_summary

**Range Names:** `ib_cash`, `ib_securities`, `ib_summary`

##### Range Definition

- **ib_cash:** `worksheet!$A$12:$P$15` (4 data rows)
- **ib_securities:** `worksheet!$A$18:$P$25` (8 data rows)
- **ib_summary:** `worksheet!$A$27:$P$30` (4 data rows)
- **Header Range:** Shared `worksheet!$A$2:$P$2`

##### Schema

Same matrix structure as `ib_net_liquidity`.

##### Key Fields

Same as `ib_net_liquidity`, differentiated by section context.

##### Data Characteristics

Same as `ib_net_liquidity`.

##### Parsing Requirements

Same unpivot logic, with section-specific account_id or metric_type tagging.

##### Target Mapping

Same target table, potentially with `metric_section` field to distinguish:

- ib_net_liquidity â†’ "NetLiquidity"
- ib_cash â†’ "Cash"
- ib_securities â†’ "Securities"
- ib_summary â†’ "Summary"

##### Validation Rules

Same as `ib_net_liquidity`, plus:

- Sum(ib_cash, ib_securities) â‰ˆ ib_net_liquidity for reconciliation

##### Risks and Ambiguities

Same as `ib_net_liquidity`.

---

### cash-expenses

Config: `gsheet/cash-expenses.json`  
Workbook ID: `1ijbXG_wEP_icWH7xtbIO0bNVp4RbWPe1A5X1Q1i1nIo`

---

#### Sheet: recent_txns

**Range Name:** `recent_txns`

##### Range Definition

- **Header Range:** `recent_txns!$A$2:$D$2`
- **Data Range:** `recent_txns!$A$3:$D$500`
- **Header Row Index:** 2 (row 1 likely title)

##### Schema

| Column Name    |     |     |     |     |     |                    |
| -------------- | --- | --- | --- | --- | --- | ------------------ |
| Position       |     |     |     |     |     |                    |
| Declared Type  |     |     |     |     |     |                    |
| Inferred Type  |     |     |     |     |     |                    |
| Null Behavior  |     |     |     |     |     |                    |
| Example Values |     |     |     |     |     |                    |
| Notes          |     |     |     |     |     |                    |
| {unknown}      | A   | â€” | â€” | â€” | â€” | Likely date        |
| {unknown}      | B   | â€” | â€” | â€” | â€” | Likely description |
| {unknown}      | C   | â€” | â€” | â€” | â€” | Likely category    |
| {unknown}      | D   | â€” | â€” | â€” | â€” | Likely amount      |

##### Key Fields

- **Candidate Primary Key:** To be determined (possibly date + description composite)
- **Account ID Semantic:** Likely implicit "Cash" or derived from sheet context
- **Period Semantic:** Expected date field in column A
- **Currency Semantic:** Likely implicit SGD

##### Data Characteristics

- **Grain:** One row per transaction
- **Layout Type:** Tabular (transaction list)
- **Section Boundaries:** N/A
- **Pivot Structure:** None
- **Spacer Rows:** Row 1 (title)
- **Spacer Columns:** None
- **Row Limit:** 498 rows (A3:D500)

##### Parsing Requirements

- **Section Detection Rule:** N/A
- **Header Detection Rule:** Row 2 contains column names
- **Pivot Unroll Rule:** N/A
- **Metric Normalization:** N/A

##### Target Mapping

- **Target Table Group:** Statement layer
- **Target Table(s):** `cash_transactions` or `statement_transactions`
- **Normalization Strategy:** Direct mapping (already transaction format)

##### Validation Rules

To be defined after live inspection of column names.

##### Risks and Ambiguities

- **Schema Drift:** Stable (transaction list format)
- **Data Quality:** Manual entry risks
- **Missing Data:** Sparse data for inactive periods
- **Unconventional Formatting:** Row 1 title row

---

### shared-expenses

Config: `gsheet/shared-expenses.json`  
Workbook ID: `1fVkiB_CXyJl2kBFEFrRb3Eb2wytWCUo1rOvveiGKZeo`

---

#### Sheet: records

**Range Name:** `records`

##### Range Definition

- **Header Range:** `records!$A$1:$H$1`
- **Data Range:** `records!$A$2:$H$1000`
- **Header Row Index:** 1

##### Schema

| Column Name    |     |     |     |     |     |                             |
| -------------- | --- | --- | --- | --- | --- | --------------------------- |
| Position       |     |     |     |     |     |                             |
| Declared Type  |     |     |     |     |     |                             |
| Inferred Type  |     |     |     |     |     |                             |
| Null Behavior  |     |     |     |     |     |                             |
| Example Values |     |     |     |     |     |                             |
| Notes          |     |     |     |     |     |                             |
| {unknown}      | A-H | â€” | â€” | â€” | â€” | 8 columns, needs inspection |

##### Key Fields

- **Candidate Primary Key:** To be determined
- **Account ID Semantic:** To be determined
- **Period Semantic:** Likely date field
- **Currency Semantic:** Likely SGD or mixed

##### Data Characteristics

- **Grain:** One row per shared expense transaction
- **Layout Type:** Tabular (assumed)
- **Section Boundaries:** N/A
- **Pivot Structure:** None
- **Spacer Rows:** None (header in row 1)
- **Spacer Columns:** Unknown
- **Row Limit:** 999 rows (A2:H1000)

##### Parsing Requirements

To be defined after live inspection.

##### Target Mapping

- **Target Table Group:** Statement layer
- **Target Table(s):** `shared_expense_transactions` or integrated into `statement_transactions`
- **Normalization Strategy:** To be determined

##### Validation Rules

To be defined.

##### Risks and Ambiguities

- **Schema Drift:** Unknown
- **Data Quality:** Manual entry risks
- **Missing Data:** Possible gaps
- **Unconventional Formatting:** 8 columns suggests rich transaction attributes

---

## Cross-Workbook Contracts

### Account ID Conventions

To be validated across all workbooks:

- **Canonical Source:** `gsheet/financial-statements.json` â†’ `accounts` sheet
- **Referenced In:**
  - balances sheet (financial-statements)
  - CPF sections (implicit: "CPF-Total", "CPF-OA", "CPF-SA", "CPF-MA")
  - IBKR sections (implicit: "IBKR-IBA")
  - Cash expenses (implicit: "Cash")
  - Shared expenses (to be determined)

**Validation Action Required:** Map implicit account IDs to canonical account list.

### Period Format Conventions

To be validated:

- **balances:** (year: int, month: int) composite
- **forex_rates:** date (YYYY-MM-DD)
- **CPF, IBKR:** Month column headers (format to be confirmed)
- **Cash/Shared expenses:** Date field (format to be confirmed)

**Standardization Required:** Convert all to canonical `period_id` format "YYYY-MM".

### Currency Conventions

- **Implicit SGD:** balances, CPF sections, cash expenses (assumed)
- **Explicit Currency:** forex_rates (USD/SGD)
- **Mixed Currency:** IBKR metrics (USD and SGD in metric labels)

**Validation Action Required:** Confirm currency assumptions and define conversion rules.

### Data Type Consistency

- **Numeric Types:** Declared as float, but may have int coercion in `database.py` logic
- **Date Types:** Mixed formats (YYYY-MM-DD, year/month composite)
- **String Types:** Account IDs, metric labels, category names

**Validation Action Required:** Define strict type coercion rules for ETL.
