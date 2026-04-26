# Helper Workbooks Mapping Matrix

**Document Version:** 0.2.0  
**Last Updated:** March 8, 2026  
**Status:** Complete

## Table of Contents

1. [Overview](#overview)
2. [Source to Target Mapping](#source-to-target-mapping)
3. [Lineage Matrix](#lineage-matrix)
4. [Mapping Rules](#mapping-rules)

## Overview

This document defines the complete mapping from legacy helper workbook structures to `financial_statements.db` target tables.

Target-state policy: the mapping logic is implemented in app-native adapters and transformation modules. Helper workbooks are reference/parity inputs only and are deprecated from steady-state monthly closing.

## Source to Target Mapping

### Mapping Matrix Schema

| Source Workbook      |     |     |     |     |     |     |     |     |     |     |
| -------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Source Sheet         |     |     |     |     |     |     |     |     |     |     |
| Source Column/Metric |     |     |     |     |     |     |     |     |     |     |
| Target Table         |     |     |     |     |     |     |     |     |     |     |
| Target Column        |     |     |     |     |     |     |     |     |     |     |
| Transform Rule       |     |     |     |     |     |     |     |     |     |     |
| Type Rule            |     |     |     |     |     |     |     |     |     |     |
| Null Rule            |     |     |     |     |     |     |     |     |     |     |
| Key Participation    |     |     |     |     |     |     |     |     |     |     |
| Validation Rule      |     |     |     |     |     |     |     |     |     |     |
| Notes                |     |     |     |     |     |     |     |     |     |     |
| ...                  | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

---

### financial-statements â†’ account_balances

**Source:** `gsheet/financial-statements.json` â†’ `balances`  
**Target:** `account_balances` (ledger layer)  
**Parser:** Tabular (PARSE-003)

| Source Workbook      |          |         |                  |                 |
| -------------------- | -------- | ------- | ---------------- | --------------- |
| Source Sheet         |          |         |                  |                 |
| Source Column        |          |         |                  |                 |
| Target Table         |          |         |                  |                 |
| Target Column        |          |         |                  |                 |
| Transform Rule       |          |         |                  |                 |
| Type Rule            |          |         |                  |                 |
| Null Rule            |          |         |                  |                 |
| Key Participation    |          |         |                  |                 |
| Validation Rule      |          |         |                  |                 |
| Notes                |          |         |                  |                 |
| financial-statements | balances | year    | account_balances | period_id       |
| financial-statements | balances | month   | account_balances | period_id       |
| financial-statements | balances | account | account_balances | account_id      |
| financial-statements | balances | balance | account_balances | closing_balance |
| â€”                  | â€”      | â€”     | account_balances | currency        |
| â€”                  | â€”      | â€”     | account_balances | source          |
| â€”                  | â€”      | â€”     | account_balances | created_at      |

| Source Workbook      |          |                                  |          |          |     |
| -------------------- | -------- | -------------------------------- | -------- | -------- | --- |
| Source Sheet         |          |                                  |          |          |     |
| Source Column        |          |                                  |          |          |     |
| Target Table         |          |                                  |          |          |     |
| Target Column        |          |                                  |          |          |     |
| Transform Rule       |          |                                  |          |          |     |
| Type Rule            |          |                                  |          |          |     |
| Null Rule            |          |                                  |          |          |     |
| Key Participation    |          |                                  |          |          |     |
| Validation Rule      |          |                                  |          |          |     |
| Notes                |          |                                  |          |          |     |
| financial-statements | balances | FORMAT("{}-{:02d}", year, month) | str      | NOT NULL | PK  |
| financial-statements | balances | FORMAT("{}-{:02d}", year, month) | str      | NOT NULL | PK  |
| financial-statements | balances | DIRECT                           | str      | NOT NULL | PK  |
| financial-statements | balances | DIRECT                           | float    | NOT NULL | â€” |
| â€”                  | â€”      | CONST("SGD")                     | str      | NOT NULL | â€” |
| â€”                  | â€”      | CONST("gsheet_balances")         | str      | NOT NULL | â€” |
| â€”                  | â€”      | NOW()                            | datetime | NOT NULL | â€” |

| Source Workbook      |          |                         |                              |
| -------------------- | -------- | ----------------------- | ---------------------------- |
| Source Sheet         |          |                         |                              |
| Source Column        |          |                         |                              |
| Target Table         |          |                         |                              |
| Target Column        |          |                         |                              |
| Transform Rule       |          |                         |                              |
| Type Rule            |          |                         |                              |
| Null Rule            |          |                         |                              |
| Key Participation    |          |                         |                              |
| Validation Rule      |          |                         |                              |
| Notes                |          |                         |                              |
| financial-statements | balances | YYYY-MM format          | Composite from year+month    |
| financial-statements | balances | month BETWEEN 1 AND 12  | Composite from year+month    |
| financial-statements | balances | EXISTS IN accounts.json | Must match canonical account |
| financial-statements | balances | Numeric                 | Negative values allowed      |
| â€”                  | â€”      | Valid ISO code          | Hardcoded SGD                |
| â€”                  | â€”      | â€”                     | Lineage marker               |
| â€”                  | â€”      | â€”                     | ETL timestamp                |

**Primary Key:** (period_id, account_id)

**Foreign Keys:**

- period_id â†’ periods(period_id)

---

### financial-statements â†’ exchange_rates

**Source:** `gsheet/financial-statements.json` â†’ `forex_rates`  
**Target:** `exchange_rates` (reference layer, if not already in baseline schema)  
**Parser:** Tabular (PARSE-003) with row 2 skip

| Source Workbook      |             |          |                |               |                       |
| -------------------- | ----------- | -------- | -------------- | ------------- | --------------------- |
| Source Sheet         |             |          |                |               |                       |
| Source Column        |             |          |                |               |                       |
| Target Table         |             |          |                |               |                       |
| Target Column        |             |          |                |               |                       |
| Transform Rule       |             |          |                |               |                       |
| Type Rule            |             |          |                |               |                       |
| Null Rule            |             |          |                |               |                       |
| Key Participation    |             |          |                |               |                       |
| Validation Rule      |             |          |                |               |                       |
| Notes                |             |          |                |               |                       |
| financial-statements | forex_rates | date     | exchange_rates | date          | DIRECT                |
| financial-statements | forex_rates | currency | exchange_rates | currency_from | DIRECT                |
| â€”                  | â€”         | â€”      | exchange_rates | currency_to   | CONST("SGD")          |
| financial-statements | forex_rates | rate_SGD | exchange_rates | rate          | DIRECT                |
| â€”                  | â€”         | â€”      | exchange_rates | source        | CONST("gsheet_forex") |
| â€”                  | â€”         | â€”      | exchange_rates | created_at    | NOW()                 |

| Source Workbook      |             |          |          |     |                |                |
| -------------------- | ----------- | -------- | -------- | --- | -------------- | -------------- |
| Source Sheet         |             |          |          |     |                |                |
| Source Column        |             |          |          |     |                |                |
| Target Table         |             |          |          |     |                |                |
| Target Column        |             |          |          |     |                |                |
| Transform Rule       |             |          |          |     |                |                |
| Type Rule            |             |          |          |     |                |                |
| Null Rule            |             |          |          |     |                |                |
| Key Participation    |             |          |          |     |                |                |
| Validation Rule      |             |          |          |     |                |                |
| Notes                |             |          |          |     |                |                |
| financial-statements | forex_rates | date     | NOT NULL | PK  | YYYY-MM-DD     | â€”            |
| financial-statements | forex_rates | str      | NOT NULL | PK  | Valid ISO code | 3-letter code  |
| â€”                  | â€”         | str      | NOT NULL | PK  | Valid ISO code | Hardcoded SGD  |
| financial-statements | forex_rates | float    | NOT NULL | â€” | rate > 0       | â€”            |
| â€”                  | â€”         | str      | NOT NULL | â€” | â€”            | Lineage marker |
| â€”                  | â€”         | datetime | NOT NULL | â€” | â€”            | ETL timestamp  |

**Primary Key:** (date, currency_from, currency_to)

**Notes:**

- Row 2 is spacer, data starts at row 3
- Expect 2 entries per month per currency (month start and month end)

---

### CPF â†’ asset_balances (or cpf_balances)

**Source:** `gsheet/cpf.json` â†’ all sections (cpf_total, cpf_oa, cpf_sa, cpf_ma, cpf_summary)  
**Target:** `asset_balances` or dedicated `cpf_balances` table (statement layer)  
**Parser:** Multi-Section Matrix Unpivot (PARSE-002 â†’ PARSE-001)

| Source Workbook      |           |                   |              |                |                         |
| -------------------- | --------- | ----------------- | ------------ | -------------- | ----------------------- |
| Source Sheet/Section |           |                   |              |                |                         |
| Source Element       |           |                   |              |                |                         |
| Target Table         |           |                   |              |                |                         |
| Target Column        |           |                   |              |                |                         |
| Transform Rule       |           |                   |              |                |                         |
| Type Rule            |           |                   |              |                |                         |
| Null Rule            |           |                   |              |                |                         |
| Key Participation    |           |                   |              |                |                         |
| Validation Rule      |           |                   |              |                |                         |
| Notes                |           |                   |              |                |                         |
| cpf                  | {section} | column_header     | cpf_balances | period_id      | PARSE_PERIOD_ID(header) |
| cpf                  | {section} | (section name)    | cpf_balances | account_id     | MAP_ACCOUNT(section)    |
| cpf                  | {section} | row_label (col A) | cpf_balances | metric_name    | DIRECT                  |
| cpf                  | {section} | cell_value        | cpf_balances | amount         | DIRECT                  |
| â€”                  | â€”       | â€”               | cpf_balances | currency       | CONST("SGD")            |
| cpf                  | {section} | (section name)    | cpf_balances | metric_section | DIRECT                  |
| â€”                  | â€”       | â€”               | cpf_balances | source         | CONST("gsheet_cpf")     |
| â€”                  | â€”       | â€”               | cpf_balances | created_at     | NOW()                   |

| Source Workbook      |           |          |          |     |                       |
| -------------------- | --------- | -------- | -------- | --- | --------------------- |
| Source Sheet/Section |           |          |          |     |                       |
| Source Element       |           |          |          |     |                       |
| Target Table         |           |          |          |     |                       |
| Target Column        |           |          |          |     |                       |
| Transform Rule       |           |          |          |     |                       |
| Type Rule            |           |          |          |     |                       |
| Null Rule            |           |          |          |     |                       |
| Key Participation    |           |          |          |     |                       |
| Validation Rule      |           |          |          |     |                       |
| Notes                |           |          |          |     |                       |
| cpf                  | {section} | str      | NOT NULL | PK  | YYYY-MM format        |
| cpf                  | {section} | str      | NOT NULL | PK  | EXISTS IN account map |
| cpf                  | {section} | str      | NOT NULL | PK  | Non-empty string      |
| cpf                  | {section} | float    | Nullable | â€” | Numeric or NULL       |
| â€”                  | â€”       | str      | NOT NULL | â€” | Valid ISO code        |
| cpf                  | {section} | str      | NOT NULL | â€” | â€”                   |
| â€”                  | â€”       | str      | NOT NULL | â€” | â€”                   |
| â€”                  | â€”       | datetime | NOT NULL | â€” | â€”                   |

| Source Workbook      |           |                                  |
| -------------------- | --------- | -------------------------------- |
| Source Sheet/Section |           |                                  |
| Source Element       |           |                                  |
| Target Table         |           |                                  |
| Target Column        |           |                                  |
| Transform Rule       |           |                                  |
| Type Rule            |           |                                  |
| Null Rule            |           |                                  |
| Key Participation    |           |                                  |
| Validation Rule      |           |                                  |
| Notes                |           |                                  |
| cpf                  | {section} | Extract from month column header |
| cpf                  | {section} | cpf_total â†’ "CPF-Total", etc.  |
| cpf                  | {section} | "Opening", "Contrib", etc.       |
| cpf                  | {section} | Skip empty cells                 |
| â€”                  | â€”       | â€”                              |
| cpf                  | {section} | "cpf_total", "cpf_oa", etc.      |
| â€”                  | â€”       | Lineage marker                   |
| â€”                  | â€”       | ETL timestamp                    |

**Primary Key:** (period_id, account_id, metric_name, metric_section)

**Foreign Keys:**

- period_id â†’ periods(period_id)
- account_id â†’ canonical account list

**Account Mapping:**
```
cpf_total â†’ CPF-Total
cpf_oa â†’ CPF-OA
cpf_sa â†’ CPF-SA
cpf_ma â†’ CPF-MA
cpf_summary â†’ CPF-Summary
```

**Validation Rules:**

- Cross-section balance check: Sum(CPF-OA, CPF-SA, CPF-MA closing) â‰ˆ CPF-Total closing per month

---

### IBKR â†’ investment_balances (or ibkr_balances)

**Source:** `gsheet/ibkr-iba.json` â†’ all sections (ib_net_liquidity, ib_cash, ib_securities, ib_summary)  
**Target:** `investment_balances` or `ibkr_balances` (statement layer)  
**Parser:** Multi-Section Matrix Unpivot (PARSE-002 â†’ PARSE-001)

| Source Workbook      |           |                   |               |                |
| -------------------- | --------- | ----------------- | ------------- | -------------- |
| Source Sheet/Section |           |                   |               |                |
| Source Element       |           |                   |               |                |
| Target Table         |           |                   |               |                |
| Target Column        |           |                   |               |                |
| Transform Rule       |           |                   |               |                |
| Type Rule            |           |                   |               |                |
| Null Rule            |           |                   |               |                |
| Key Participation    |           |                   |               |                |
| Validation Rule      |           |                   |               |                |
| Notes                |           |                   |               |                |
| ibkr-iba             | {section} | column_header     | ibkr_balances | period_id      |
| ibkr-iba             | {section} | (section name)    | ibkr_balances | account_id     |
| ibkr-iba             | {section} | row_label (col A) | ibkr_balances | metric_name    |
| ibkr-iba             | {section} | cell_value        | ibkr_balances | amount         |
| ibkr-iba             | {section} | row_label (col A) | ibkr_balances | currency       |
| ibkr-iba             | {section} | (section name)    | ibkr_balances | metric_section |
| â€”                  | â€”       | â€”               | ibkr_balances | source         |
| â€”                  | â€”       | â€”               | ibkr_balances | created_at     |

| Source Workbook      |           |                               |          |          |     |
| -------------------- | --------- | ----------------------------- | -------- | -------- | --- |
| Source Sheet/Section |           |                               |          |          |     |
| Source Element       |           |                               |          |          |     |
| Target Table         |           |                               |          |          |     |
| Target Column        |           |                               |          |          |     |
| Transform Rule       |           |                               |          |          |     |
| Type Rule            |           |                               |          |          |     |
| Null Rule            |           |                               |          |          |     |
| Key Participation    |           |                               |          |          |     |
| Validation Rule      |           |                               |          |          |     |
| Notes                |           |                               |          |          |     |
| ibkr-iba             | {section} | PARSE_PERIOD_ID(header)       | str      | NOT NULL | PK  |
| ibkr-iba             | {section} | CONST("IBKR-IBA")             | str      | NOT NULL | PK  |
| ibkr-iba             | {section} | DIRECT                        | str      | NOT NULL | PK  |
| ibkr-iba             | {section} | DIRECT                        | float    | Nullable | â€” |
| ibkr-iba             | {section} | EXTRACT_CURRENCY(metric_name) | str      | NOT NULL | â€” |
| ibkr-iba             | {section} | DIRECT                        | str      | NOT NULL | PK  |
| â€”                  | â€”       | CONST("gsheet_ibkr")          | str      | NOT NULL | â€” |
| â€”                  | â€”       | NOW()                         | datetime | NOT NULL | â€” |

| Source Workbook      |           |                       |                                     |
| -------------------- | --------- | --------------------- | ----------------------------------- |
| Source Sheet/Section |           |                       |                                     |
| Source Element       |           |                       |                                     |
| Target Table         |           |                       |                                     |
| Target Column        |           |                       |                                     |
| Transform Rule       |           |                       |                                     |
| Type Rule            |           |                       |                                     |
| Null Rule            |           |                       |                                     |
| Key Participation    |           |                       |                                     |
| Validation Rule      |           |                       |                                     |
| Notes                |           |                       |                                     |
| ibkr-iba             | {section} | YYYY-MM format        | Extract from month column header    |
| ibkr-iba             | {section} | EXISTS IN account map | All sections â†’ "IBKR-IBA"         |
| ibkr-iba             | {section} | Non-empty string      | "NAV USD", "NAV SGD", etc.          |
| ibkr-iba             | {section} | Numeric or NULL       | Skip empty cells                    |
| ibkr-iba             | {section} | USD or SGD            | Parse from metric name              |
| ibkr-iba             | {section} | â€”                   | "ib_net_liquidity", "ib_cash", etc. |
| â€”                  | â€”       | â€”                   | Lineage marker                      |
| â€”                  | â€”       | â€”                   | ETL timestamp                       |

**Primary Key:** (period_id, account_id, metric_name, metric_section)

**Foreign Keys:**

- period_id â†’ periods(period_id)

**Currency Extraction Rule:**
```python
if "USD" in metric_name: return "USD"
elif "SGD" in metric_name: return "SGD"
else: return "USD"  # Default
```

**Validation Rules:**

- NAV_USD * forex_rate â‰ˆ NAV_SGD per month (cross-validate with exchange_rates table)

---

### cash-expenses â†’ cash_transactions

**Source:** `gsheet/cash-expenses.json` â†’ `recent_txns`  
**Target:** `cash_transactions` or `statement_transactions` (statement layer)  
**Parser:** Tabular (PARSE-003) with row 1 skip

**Note:** Schema needs live inspection. Placeholder mapping below.

| Source Workbook   |             |              |                   |             |
| ----------------- | ----------- | ------------ | ----------------- | ----------- |
| Source Sheet      |             |              |                   |             |
| Source Column     |             |              |                   |             |
| Target Table      |             |              |                   |             |
| Target Column     |             |              |                   |             |
| Transform Rule    |             |              |                   |             |
| Type Rule         |             |              |                   |             |
| Null Rule         |             |              |                   |             |
| Key Participation |             |              |                   |             |
| Validation Rule   |             |              |                   |             |
| Notes             |             |              |                   |             |
| cash-expenses     | recent_txns | {col_A_name} | cash_transactions | date        |
| cash-expenses     | recent_txns | {col_B_name} | cash_transactions | description |
| cash-expenses     | recent_txns | {col_C_name} | cash_transactions | category    |
| cash-expenses     | recent_txns | {col_D_name} | cash_transactions | amount      |
| â€”               | â€”         | â€”          | cash_transactions | account_id  |
| â€”               | â€”         | â€”          | cash_transactions | currency    |
| â€”               | â€”         | â€”          | cash_transactions | source      |
| â€”               | â€”         | â€”          | cash_transactions | created_at  |

| Source Workbook   |             |                               |          |          |     |
| ----------------- | ----------- | ----------------------------- | -------- | -------- | --- |
| Source Sheet      |             |                               |          |          |     |
| Source Column     |             |                               |          |          |     |
| Target Table      |             |                               |          |          |     |
| Target Column     |             |                               |          |          |     |
| Transform Rule    |             |                               |          |          |     |
| Type Rule         |             |                               |          |          |     |
| Null Rule         |             |                               |          |          |     |
| Key Participation |             |                               |          |          |     |
| Validation Rule   |             |                               |          |          |     |
| Notes             |             |                               |          |          |     |
| cash-expenses     | recent_txns | PARSE_DATE                    | date     | NOT NULL | â€” |
| cash-expenses     | recent_txns | DIRECT                        | str      | Nullable | â€” |
| cash-expenses     | recent_txns | DIRECT                        | str      | Nullable | â€” |
| cash-expenses     | recent_txns | DIRECT                        | float    | NOT NULL | â€” |
| â€”               | â€”         | CONST("Cash")                 | str      | NOT NULL | â€” |
| â€”               | â€”         | CONST("SGD")                  | str      | NOT NULL | â€” |
| â€”               | â€”         | CONST("gsheet_cash_expenses") | str      | NOT NULL | â€” |
| â€”               | â€”         | NOW()                         | datetime | NOT NULL | â€” |

| Source Workbook   |             |                       |                           |
| ----------------- | ----------- | --------------------- | ------------------------- |
| Source Sheet      |             |                       |                           |
| Source Column     |             |                       |                           |
| Target Table      |             |                       |                           |
| Target Column     |             |                       |                           |
| Transform Rule    |             |                       |                           |
| Type Rule         |             |                       |                           |
| Null Rule         |             |                       |                           |
| Key Participation |             |                       |                           |
| Validation Rule   |             |                       |                           |
| Notes             |             |                       |                           |
| cash-expenses     | recent_txns | Valid date            | Needs format confirmation |
| cash-expenses     | recent_txns | â€”                   | Transaction description   |
| cash-expenses     | recent_txns | â€”                   | Expense category          |
| cash-expenses     | recent_txns | Numeric               | Transaction amount        |
| â€”               | â€”         | EXISTS IN account map | Implicit cash account     |
| â€”               | â€”         | Valid ISO code        | Assumed SGD               |
| â€”               | â€”         | â€”                   | Lineage marker            |
| â€”               | â€”         | â€”                   | ETL timestamp             |

**Primary Key:** To be determined (possibly auto-increment ID or composite date+description+amount)

**Foreign Keys:**

- category â†’ categories (if category lookup table exists)

**Action Required:** Live inspection to confirm column names and types.

---

### shared-expenses â†’ shared_expense_transactions

**Source:** `gsheet/shared-expenses.json` â†’ `records`  
**Target:** `shared_expense_transactions` or integrated into `statement_transactions` (statement layer)  
**Parser:** Tabular (PARSE-003)

**Note:** 8 columns (A-H) need live inspection. Placeholder mapping below.

| Source Workbook   |         |                 |                             |              |
| ----------------- | ------- | --------------- | --------------------------- | ------------ |
| Source Sheet      |         |                 |                             |              |
| Source Column     |         |                 |                             |              |
| Target Table      |         |                 |                             |              |
| Target Column     |         |                 |                             |              |
| Transform Rule    |         |                 |                             |              |
| Type Rule         |         |                 |                             |              |
| Null Rule         |         |                 |                             |              |
| Key Participation |         |                 |                             |              |
| Validation Rule   |         |                 |                             |              |
| Notes             |         |                 |                             |              |
| shared-expenses   | records | {col_A_name}    | shared_expense_transactions | date         |
| shared-expenses   | records | {col_B_name}    | shared_expense_transactions | description  |
| shared-expenses   | records | {col_C_name}    | shared_expense_transactions | amount       |
| shared-expenses   | records | {col_D_name}    | shared_expense_transactions | participant  |
| shared-expenses   | records | {col_E_name}    | shared_expense_transactions | split_amount |
| shared-expenses   | records | {col_F-H_names} | shared_expense_transactions | {TBD}        |
| â€”               | â€”     | â€”             | shared_expense_transactions | currency     |
| â€”               | â€”     | â€”             | shared_expense_transactions | source       |
| â€”               | â€”     | â€”             | shared_expense_transactions | created_at   |

| Source Workbook   |         |                                 |          |          |     |                |
| ----------------- | ------- | ------------------------------- | -------- | -------- | --- | -------------- |
| Source Sheet      |         |                                 |          |          |     |                |
| Source Column     |         |                                 |          |          |     |                |
| Target Table      |         |                                 |          |          |     |                |
| Target Column     |         |                                 |          |          |     |                |
| Transform Rule    |         |                                 |          |          |     |                |
| Type Rule         |         |                                 |          |          |     |                |
| Null Rule         |         |                                 |          |          |     |                |
| Key Participation |         |                                 |          |          |     |                |
| Validation Rule   |         |                                 |          |          |     |                |
| Notes             |         |                                 |          |          |     |                |
| shared-expenses   | records | PARSE_DATE                      | date     | NOT NULL | â€” | Valid date     |
| shared-expenses   | records | DIRECT                          | str      | Nullable | â€” | â€”            |
| shared-expenses   | records | DIRECT                          | float    | NOT NULL | â€” | Numeric        |
| shared-expenses   | records | DIRECT                          | str      | Nullable | â€” | â€”            |
| shared-expenses   | records | DIRECT                          | float    | Nullable | â€” | Numeric        |
| shared-expenses   | records | TBD                             | TBD      | TBD      | â€” | â€”            |
| â€”               | â€”     | CONST("SGD")                    | str      | NOT NULL | â€” | Valid ISO code |
| â€”               | â€”     | CONST("gsheet_shared_expenses") | str      | NOT NULL | â€” | â€”            |
| â€”               | â€”     | NOW()                           | datetime | NOT NULL | â€” | â€”            |

| Source Workbook   |         |                           |
| ----------------- | ------- | ------------------------- |
| Source Sheet      |         |                           |
| Source Column     |         |                           |
| Target Table      |         |                           |
| Target Column     |         |                           |
| Transform Rule    |         |                           |
| Type Rule         |         |                           |
| Null Rule         |         |                           |
| Key Participation |         |                           |
| Validation Rule   |         |                           |
| Notes             |         |                           |
| shared-expenses   | records | Needs format confirmation |
| shared-expenses   | records | â€”                       |
| shared-expenses   | records | â€”                       |
| shared-expenses   | records | Who paid or who owes      |
| shared-expenses   | records | Individual share          |
| shared-expenses   | records | Needs inspection          |
| â€”               | â€”     | Assumed SGD, may be mixed |
| â€”               | â€”     | Lineage marker            |
| â€”               | â€”     | ETL timestamp             |

**Primary Key:** To be determined

**Action Required:** Live inspection to confirm schema.

---

### homebudget-workbook â†’ category_mappings

**Source:** `gsheet/homebudget-workbook.json` â†’ `cat_map`  
**Target:** `category_mappings` (reference layer)  
**Parser:** Tabular (PARSE-003)

**Note:** 10 columns (A-J) suggest hierarchical or multi-dimensional mapping. Needs live inspection.

| Source Workbook     |         |                 |                   |                  |
| ------------------- | ------- | --------------- | ----------------- | ---------------- |
| Source Sheet        |         |                 |                   |                  |
| Source Column       |         |                 |                   |                  |
| Target Table        |         |                 |                   |                  |
| Target Column       |         |                 |                   |                  |
| Transform Rule      |         |                 |                   |                  |
| Type Rule           |         |                 |                   |                  |
| Null Rule           |         |                 |                   |                  |
| Key Participation   |         |                 |                   |                  |
| Validation Rule     |         |                 |                   |                  |
| Notes               |         |                 |                   |                  |
| homebudget-workbook | cat_map | {col_A_name}    | category_mappings | hb_category_id   |
| homebudget-workbook | cat_map | {col_B_name}    | category_mappings | hb_category_name |
| homebudget-workbook | cat_map | {col_C-J_names} | category_mappings | {TBD}            |
| â€”                 | â€”     | â€”             | category_mappings | source           |
| â€”                 | â€”     | â€”             | category_mappings | created_at       |

| Source Workbook     |         |                         |          |          |     |                      |
| ------------------- | ------- | ----------------------- | -------- | -------- | --- | -------------------- |
| Source Sheet        |         |                         |          |          |     |                      |
| Source Column       |         |                         |          |          |     |                      |
| Target Table        |         |                         |          |          |     |                      |
| Target Column       |         |                         |          |          |     |                      |
| Transform Rule      |         |                         |          |          |     |                      |
| Type Rule           |         |                         |          |          |     |                      |
| Null Rule           |         |                         |          |          |     |                      |
| Key Participation   |         |                         |          |          |     |                      |
| Validation Rule     |         |                         |          |          |     |                      |
| Notes               |         |                         |          |          |     |                      |
| homebudget-workbook | cat_map | DIRECT                  | str/int  | NOT NULL | PK  | EXISTS IN HomeBudget |
| homebudget-workbook | cat_map | DIRECT                  | str      | Nullable | â€” | â€”                  |
| homebudget-workbook | cat_map | TBD                     | TBD      | TBD      | â€” | â€”                  |
| â€”                 | â€”     | CONST("gsheet_cat_map") | str      | NOT NULL | â€” | â€”                  |
| â€”                 | â€”     | NOW()                   | datetime | NOT NULL | â€” | â€”                  |

| Source Workbook     |         |                                             |
| ------------------- | ------- | ------------------------------------------- |
| Source Sheet        |         |                                             |
| Source Column       |         |                                             |
| Target Table        |         |                                             |
| Target Column       |         |                                             |
| Transform Rule      |         |                                             |
| Type Rule           |         |                                             |
| Null Rule           |         |                                             |
| Key Participation   |         |                                             |
| Validation Rule     |         |                                             |
| Notes               |         |                                             |
| homebudget-workbook | cat_map | HomeBudget category ID                      |
| homebudget-workbook | cat_map | Human-readable name                         |
| homebudget-workbook | cat_map | Hierarchy levels or statement line mappings |
| â€”                 | â€”     | Lineage marker                              |
| â€”                 | â€”     | ETL timestamp                               |

**Primary Key:** To be determined (likely hb_category_id)

**Action Required:** Live inspection to understand mapping structure.

---

## Lineage Matrix

This matrix traces data from raw statement files through helper workbooks to the final database tables.

### Lineage Matrix Schema

| Raw Source Path           |     |     |     |     |     |     |     |     |     |     |
| ------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Source Format             |     |     |     |     |     |     |     |     |     |     |
| Extracted Entity          |     |     |     |     |     |     |     |     |     |     |
| Helper Workbook Sheet     |     |     |     |     |     |     |     |     |     |     |
| Helper Workbook Field     |     |     |     |     |     |     |     |     |     |     |
| Canonical Record Field    |     |     |     |     |     |     |     |     |     |     |
| Target DB Table           |     |     |     |     |     |     |     |     |     |     |
| Target DB Column          |     |     |     |     |     |     |     |     |     |     |
| Transformation/Parse Rule |     |     |     |     |     |     |     |     |     |     |
| Manual Step Flag          |     |     |     |     |     |     |     |     |     |     |
| Notes                     |     |     |     |     |     |     |     |     |     |     |
| ...                       | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

---

### IBKR Statement â†’ ibkr-iba Workbook â†’ ibkr_balances

| Raw Source Path                                            |     |                             |
| ---------------------------------------------------------- | --- | --------------------------- |
| Source Format                                              |     |                             |
| Extracted Entity                                           |     |                             |
| Helper Workbook Sheet                                      |     |                             |
| Helper Workbook Field                                      |     |                             |
| Canonical Record Field                                     |     |                             |
| Target DB Table                                            |     |                             |
| Target DB Column                                           |     |                             |
| Transformation/Parse Rule                                  |     |                             |
| Manual Step Flag                                           |     |                             |
| Notes                                                      |     |                             |
| reference/statements/ibkr-iba/U1109040_Activity_YYYYMM.csv | CSV | NAV (Net Asset Value)       |
| reference/statements/ibkr-iba/U1109040_Activity_YYYYMM.csv | CSV | Cash Balance                |
| reference/statements/ibkr-iba/U1109040_Activity_YYYYMM.csv | CSV | Stock Holdings Market Value |

| Raw Source Path                                            |                        |
| ---------------------------------------------------------- | ---------------------- |
| Source Format                                              |                        |
| Extracted Entity                                           |                        |
| Helper Workbook Sheet                                      |                        |
| Helper Workbook Field                                      |                        |
| Canonical Record Field                                     |                        |
| Target DB Table                                            |                        |
| Target DB Column                                           |                        |
| Transformation/Parse Rule                                  |                        |
| Manual Step Flag                                           |                        |
| Notes                                                      |                        |
| reference/statements/ibkr-iba/U1109040_Activity_YYYYMM.csv | ibkr-iba â†’ worksheet |
| reference/statements/ibkr-iba/U1109040_Activity_YYYYMM.csv | ibkr-iba â†’ worksheet |
| reference/statements/ibkr-iba/U1109040_Activity_YYYYMM.csv | ibkr-iba â†’ worksheet |

| Raw Source Path                                            |                                       |        |
| ---------------------------------------------------------- | ------------------------------------- | ------ |
| Source Format                                              |                                       |        |
| Extracted Entity                                           |                                       |        |
| Helper Workbook Sheet                                      |                                       |        |
| Helper Workbook Field                                      |                                       |        |
| Canonical Record Field                                     |                                       |        |
| Target DB Table                                            |                                       |        |
| Target DB Column                                           |                                       |        |
| Transformation/Parse Rule                                  |                                       |        |
| Manual Step Flag                                           |                                       |        |
| Notes                                                      |                                       |        |
| reference/statements/ibkr-iba/U1109040_Activity_YYYYMM.csv | ib_net_liquidity â†’ "NAV USD" metric | amount |
| reference/statements/ibkr-iba/U1109040_Activity_YYYYMM.csv | ib_cash â†’ "Cash USD" metric         | amount |
| reference/statements/ibkr-iba/U1109040_Activity_YYYYMM.csv | ib_securities â†’ metric              | amount |

| Raw Source Path                                            |               |        |                   |
| ---------------------------------------------------------- | ------------- | ------ | ----------------- |
| Source Format                                              |               |        |                   |
| Extracted Entity                                           |               |        |                   |
| Helper Workbook Sheet                                      |               |        |                   |
| Helper Workbook Field                                      |               |        |                   |
| Canonical Record Field                                     |               |        |                   |
| Target DB Table                                            |               |        |                   |
| Target DB Column                                           |               |        |                   |
| Transformation/Parse Rule                                  |               |        |                   |
| Manual Step Flag                                           |               |        |                   |
| Notes                                                      |               |        |                   |
| reference/statements/ibkr-iba/U1109040_Activity_YYYYMM.csv | ibkr_balances | amount | PARSE-001 unpivot |
| reference/statements/ibkr-iba/U1109040_Activity_YYYYMM.csv | ibkr_balances | amount | PARSE-001 unpivot |
| reference/statements/ibkr-iba/U1109040_Activity_YYYYMM.csv | ibkr_balances | amount | PARSE-001 unpivot |

| Raw Source Path                                            |              |
| ---------------------------------------------------------- | ------------ |
| Source Format                                              |              |
| Extracted Entity                                           |              |
| Helper Workbook Sheet                                      |              |
| Helper Workbook Field                                      |              |
| Canonical Record Field                                     |              |
| Target DB Table                                            |              |
| Target DB Column                                           |              |
| Transformation/Parse Rule                                  |              |
| Manual Step Flag                                           |              |
| Notes                                                      |              |
| reference/statements/ibkr-iba/U1109040_Activity_YYYYMM.csv | Yes - Manual |
| reference/statements/ibkr-iba/U1109040_Activity_YYYYMM.csv | Yes - Manual |
| reference/statements/ibkr-iba/U1109040_Activity_YYYYMM.csv | Yes - Manual |

| Raw Source Path                                            |                                         |
| ---------------------------------------------------------- | --------------------------------------- |
| Source Format                                              |                                         |
| Extracted Entity                                           |                                         |
| Helper Workbook Sheet                                      |                                         |
| Helper Workbook Field                                      |                                         |
| Canonical Record Field                                     |                                         |
| Target DB Table                                            |                                         |
| Target DB Column                                           |                                         |
| Transformation/Parse Rule                                  |                                         |
| Manual Step Flag                                           |                                         |
| Notes                                                      |                                         |
| reference/statements/ibkr-iba/U1109040_Activity_YYYYMM.csv | User manually enters NAV from statement |
| reference/statements/ibkr-iba/U1109040_Activity_YYYYMM.csv | User enters cash from statement         |
| reference/statements/ibkr-iba/U1109040_Activity_YYYYMM.csv | User enters securities value            |

**Manual Step:** User views IBKR statement PDF/CSV and manually enters summary values into the workbook matrix cells.

---

### CPF Statement â†’ cpf Workbook â†’ cpf_balances

| Raw Source Path           |               |               |                   |                              |
| ------------------------- | ------------- | ------------- | ----------------- | ---------------------------- |
| Source Format             |               |               |                   |                              |
| Extracted Entity          |               |               |                   |                              |
| Helper Workbook Sheet     |               |               |                   |                              |
| Helper Workbook Field     |               |               |                   |                              |
| Canonical Record Field    |               |               |                   |                              |
| Target DB Table           |               |               |                   |                              |
| Target DB Column          |               |               |                   |                              |
| Transformation/Parse Rule |               |               |                   |                              |
| Manual Step Flag          |               |               |                   |                              |
| Notes                     |               |               |                   |                              |
| {CPF statement portal}    | Online Portal | OA Balance    | cpf â†’ worksheet | cpf_oa â†’ "Closing" metric  |
| {CPF statement portal}    | Online Portal | SA Balance    | cpf â†’ worksheet | cpf_sa â†’ "Closing" metric  |
| {CPF statement portal}    | Online Portal | MA Balance    | cpf â†’ worksheet | cpf_ma â†’ "Closing" metric  |
| {CPF statement portal}    | Online Portal | Contributions | cpf â†’ worksheet | cpf_oa â†’ "Contrib" metric  |
| {CPF statement portal}    | Online Portal | Interest      | cpf â†’ worksheet | cpf_oa â†’ "Interest" metric |

| Raw Source Path           |               |        |              |        |                   |              |
| ------------------------- | ------------- | ------ | ------------ | ------ | ----------------- | ------------ |
| Source Format             |               |        |              |        |                   |              |
| Extracted Entity          |               |        |              |        |                   |              |
| Helper Workbook Sheet     |               |        |              |        |                   |              |
| Helper Workbook Field     |               |        |              |        |                   |              |
| Canonical Record Field    |               |        |              |        |                   |              |
| Target DB Table           |               |        |              |        |                   |              |
| Target DB Column          |               |        |              |        |                   |              |
| Transformation/Parse Rule |               |        |              |        |                   |              |
| Manual Step Flag          |               |        |              |        |                   |              |
| Notes                     |               |        |              |        |                   |              |
| {CPF statement portal}    | Online Portal | amount | cpf_balances | amount | PARSE-001 unpivot | Yes - Manual |
| {CPF statement portal}    | Online Portal | amount | cpf_balances | amount | PARSE-001 unpivot | Yes - Manual |
| {CPF statement portal}    | Online Portal | amount | cpf_balances | amount | PARSE-001 unpivot | Yes - Manual |
| {CPF statement portal}    | Online Portal | amount | cpf_balances | amount | PARSE-001 unpivot | Yes - Manual |
| {CPF statement portal}    | Online Portal | amount | cpf_balances | amount | PARSE-001 unpivot | Yes - Manual |

| Raw Source Path           |               |                                                           |
| ------------------------- | ------------- | --------------------------------------------------------- |
| Source Format             |               |                                                           |
| Extracted Entity          |               |                                                           |
| Helper Workbook Sheet     |               |                                                           |
| Helper Workbook Field     |               |                                                           |
| Canonical Record Field    |               |                                                           |
| Target DB Table           |               |                                                           |
| Target DB Column          |               |                                                           |
| Transformation/Parse Rule |               |                                                           |
| Manual Step Flag          |               |                                                           |
| Notes                     |               |                                                           |
| {CPF statement portal}    | Online Portal | User logs into CPF portal, views balance, enters manually |
| {CPF statement portal}    | Online Portal | â€”                                                       |
| {CPF statement portal}    | Online Portal | â€”                                                       |
| {CPF statement portal}    | Online Portal | â€”                                                       |
| {CPF statement portal}    | Online Portal | â€”                                                       |

**Manual Step:** User accesses CPF online portal (no raw statement file available in repo), manually enters values into workbook.

---

### Bank Statement â†’ cash-expenses Workbook â†’ cash_transactions

| Raw Source Path                                              |     |                             |
| ------------------------------------------------------------ | --- | --------------------------- |
| Source Format                                                |     |                             |
| Extracted Entity                                             |     |                             |
| Helper Workbook Sheet                                        |     |                             |
| Helper Workbook Field                                        |     |                             |
| Canonical Record Field                                       |     |                             |
| Target DB Table                                              |     |                             |
| Target DB Column                                             |     |                             |
| Transformation/Parse Rule                                    |     |                             |
| Manual Step Flag                                             |     |                             |
| Notes                                                        |     |                             |
| reference/statements/citi-twh/Citibank Personal - YYYYMM.pdf | PDF | Cash withdrawal transaction |
| reference/statements/dbs-multi/DBSStatement_YYYYMM.pdf       | PDF | Cash transaction            |

| Raw Source Path                                              |                               |           |
| ------------------------------------------------------------ | ----------------------------- | --------- |
| Source Format                                                |                               |           |
| Extracted Entity                                             |                               |           |
| Helper Workbook Sheet                                        |                               |           |
| Helper Workbook Field                                        |                               |           |
| Canonical Record Field                                       |                               |           |
| Target DB Table                                              |                               |           |
| Target DB Column                                             |                               |           |
| Transformation/Parse Rule                                    |                               |           |
| Manual Step Flag                                             |                               |           |
| Notes                                                        |                               |           |
| reference/statements/citi-twh/Citibank Personal - YYYYMM.pdf | cash-expenses â†’ recent_txns | Row entry |
| reference/statements/dbs-multi/DBSStatement_YYYYMM.pdf       | cash-expenses â†’ recent_txns | Row entry |

| Raw Source Path                                              |             |                   |
| ------------------------------------------------------------ | ----------- | ----------------- |
| Source Format                                                |             |                   |
| Extracted Entity                                             |             |                   |
| Helper Workbook Sheet                                        |             |                   |
| Helper Workbook Field                                        |             |                   |
| Canonical Record Field                                       |             |                   |
| Target DB Table                                              |             |                   |
| Target DB Column                                             |             |                   |
| Transformation/Parse Rule                                    |             |                   |
| Manual Step Flag                                             |             |                   |
| Notes                                                        |             |                   |
| reference/statements/citi-twh/Citibank Personal - YYYYMM.pdf | transaction | cash_transactions |
| reference/statements/dbs-multi/DBSStatement_YYYYMM.pdf       | transaction | cash_transactions |

| Raw Source Path                                              |                           |                   |
| ------------------------------------------------------------ | ------------------------- | ----------------- |
| Source Format                                                |                           |                   |
| Extracted Entity                                             |                           |                   |
| Helper Workbook Sheet                                        |                           |                   |
| Helper Workbook Field                                        |                           |                   |
| Canonical Record Field                                       |                           |                   |
| Target DB Table                                              |                           |                   |
| Target DB Column                                             |                           |                   |
| Transformation/Parse Rule                                    |                           |                   |
| Manual Step Flag                                             |                           |                   |
| Notes                                                        |                           |                   |
| reference/statements/citi-twh/Citibank Personal - YYYYMM.pdf | date, amount, description | PARSE-003 tabular |
| reference/statements/dbs-multi/DBSStatement_YYYYMM.pdf       | date, amount, description | PARSE-003 tabular |

| Raw Source Path                                              |              |
| ------------------------------------------------------------ | ------------ |
| Source Format                                                |              |
| Extracted Entity                                             |              |
| Helper Workbook Sheet                                        |              |
| Helper Workbook Field                                        |              |
| Canonical Record Field                                       |              |
| Target DB Table                                              |              |
| Target DB Column                                             |              |
| Transformation/Parse Rule                                    |              |
| Manual Step Flag                                             |              |
| Notes                                                        |              |
| reference/statements/citi-twh/Citibank Personal - YYYYMM.pdf | Yes - Manual |
| reference/statements/dbs-multi/DBSStatement_YYYYMM.pdf       | Yes - Manual |

| Raw Source Path                                              |                                                     |
| ------------------------------------------------------------ | --------------------------------------------------- |
| Source Format                                                |                                                     |
| Extracted Entity                                             |                                                     |
| Helper Workbook Sheet                                        |                                                     |
| Helper Workbook Field                                        |                                                     |
| Canonical Record Field                                       |                                                     |
| Target DB Table                                              |                                                     |
| Target DB Column                                             |                                                     |
| Transformation/Parse Rule                                    |                                                     |
| Manual Step Flag                                             |                                                     |
| Notes                                                        |                                                     |
| reference/statements/citi-twh/Citibank Personal - YYYYMM.pdf | User views statement PDF, enters cash txns manually |
| reference/statements/dbs-multi/DBSStatement_YYYYMM.pdf       | â€”                                                 |

**Manual Step:** User reviews bank statement PDFs for cash withdrawals, manually records expenses in cash-expenses workbook.

---

### HomeBudget â†’ financial-statements Workbook â†’ account_balances

| Raw Source Path           |        |                 |                                   |                |
| ------------------------- | ------ | --------------- | --------------------------------- | -------------- |
| Source Format             |        |                 |                                   |                |
| Extracted Entity          |        |                 |                                   |                |
| Helper Workbook Sheet     |        |                 |                                   |                |
| Helper Workbook Field     |        |                 |                                   |                |
| Canonical Record Field    |        |                 |                                   |                |
| Target DB Table           |        |                 |                                   |                |
| Target DB Column          |        |                 |                                   |                |
| Transformation/Parse Rule |        |                 |                                   |                |
| Manual Step Flag          |        |                 |                                   |                |
| Notes                     |        |                 |                                   |                |
| HomeBudget SQLite DB      | SQLite | Account balance | financial-statements â†’ balances | balance column |

| Raw Source Path           |        |                 |                  |                 |                   |
| ------------------------- | ------ | --------------- | ---------------- | --------------- | ----------------- |
| Source Format             |        |                 |                  |                 |                   |
| Extracted Entity          |        |                 |                  |                 |                   |
| Helper Workbook Sheet     |        |                 |                  |                 |                   |
| Helper Workbook Field     |        |                 |                  |                 |                   |
| Canonical Record Field    |        |                 |                  |                 |                   |
| Target DB Table           |        |                 |                  |                 |                   |
| Target DB Column          |        |                 |                  |                 |                   |
| Transformation/Parse Rule |        |                 |                  |                 |                   |
| Manual Step Flag          |        |                 |                  |                 |                   |
| Notes                     |        |                 |                  |                 |                   |
| HomeBudget SQLite DB      | SQLite | closing_balance | account_balances | closing_balance | PARSE-003 tabular |

| Raw Source Path           |        |                |
| ------------------------- | ------ | -------------- |
| Source Format             |        |                |
| Extracted Entity          |        |                |
| Helper Workbook Sheet     |        |                |
| Helper Workbook Field     |        |                |
| Canonical Record Field    |        |                |
| Target DB Table           |        |                |
| Target DB Column          |        |                |
| Transformation/Parse Rule |        |                |
| Manual Step Flag          |        |                |
| Notes                     |        |                |
| HomeBudget SQLite DB      | SQLite | No - Automated |

| Raw Source Path           |        |                                                                             |
| ------------------------- | ------ | --------------------------------------------------------------------------- |
| Source Format             |        |                                                                             |
| Extracted Entity          |        |                                                                             |
| Helper Workbook Sheet     |        |                                                                             |
| Helper Workbook Field     |        |                                                                             |
| Canonical Record Field    |        |                                                                             |
| Target DB Table           |        |                                                                             |
| Target DB Column          |        |                                                                             |
| Transformation/Parse Rule |        |                                                                             |
| Manual Step Flag          |        |                                                                             |
| Notes                     |        |                                                                             |
| HomeBudget SQLite DB      | SQLite | Production path is direct app adapter to database, workbook parity optional |

**Manual Step:** No manual step in target-state production flow, direct HomeBudget API or DB query is required.

---

### External API â†’ financial-statements Workbook â†’ exchange_rates

| Raw Source Path           |          |                       |                                      |
| ------------------------- | -------- | --------------------- | ------------------------------------ |
| Source Format             |          |                       |                                      |
| Extracted Entity          |          |                       |                                      |
| Helper Workbook Sheet     |          |                       |                                      |
| Helper Workbook Field     |          |                       |                                      |
| Canonical Record Field    |          |                       |                                      |
| Target DB Table           |          |                       |                                      |
| Target DB Column          |          |                       |                                      |
| Transformation/Parse Rule |          |                       |                                      |
| Manual Step Flag          |          |                       |                                      |
| Notes                     |          |                       |                                      |
| Yahoo Finance API         | API/JSON | USD/SGD exchange rate | financial-statements â†’ forex_rates |

| Raw Source Path           |          |                 |      |                |      |                   |
| ------------------------- | -------- | --------------- | ---- | -------------- | ---- | ----------------- |
| Source Format             |          |                 |      |                |      |                   |
| Extracted Entity          |          |                 |      |                |      |                   |
| Helper Workbook Sheet     |          |                 |      |                |      |                   |
| Helper Workbook Field     |          |                 |      |                |      |                   |
| Canonical Record Field    |          |                 |      |                |      |                   |
| Target DB Table           |          |                 |      |                |      |                   |
| Target DB Column          |          |                 |      |                |      |                   |
| Transformation/Parse Rule |          |                 |      |                |      |                   |
| Manual Step Flag          |          |                 |      |                |      |                   |
| Notes                     |          |                 |      |                |      |                   |
| Yahoo Finance API         | API/JSON | rate_SGD column | rate | exchange_rates | rate | PARSE-003 tabular |

| Raw Source Path           |          |                |
| ------------------------- | -------- | -------------- |
| Source Format             |          |                |
| Extracted Entity          |          |                |
| Helper Workbook Sheet     |          |                |
| Helper Workbook Field     |          |                |
| Canonical Record Field    |          |                |
| Target DB Table           |          |                |
| Target DB Column          |          |                |
| Transformation/Parse Rule |          |                |
| Manual Step Flag          |          |                |
| Notes                     |          |                |
| Yahoo Finance API         | API/JSON | No - Automated |

| Raw Source Path           |          |                                                                                        |
| ------------------------- | -------- | -------------------------------------------------------------------------------------- |
| Source Format             |          |                                                                                        |
| Extracted Entity          |          |                                                                                        |
| Helper Workbook Sheet     |          |                                                                                        |
| Helper Workbook Field     |          |                                                                                        |
| Canonical Record Field    |          |                                                                                        |
| Target DB Table           |          |                                                                                        |
| Target DB Column          |          |                                                                                        |
| Transformation/Parse Rule |          |                                                                                        |
| Manual Step Flag          |          |                                                                                        |
| Notes                     |          |                                                                                        |
| Yahoo Finance API         | API/JSON | Production path writes rates directly through app FX adapter, workbook parity optional |

**Manual Step:** No manual workbook post in target-state production flow.

---

## Mapping Rules

### Transform Functions

**FORMAT(pattern, ...args):** String formatting
```python
FORMAT("{}-{:02d}", year, month)  # "2026-03" from (2026, 3)
```

**PARSE_PERIOD_ID(header_text):** Extract YYYY-MM from column header
```python
"Jan 2026" â†’ "2026-01"
"2026-01" â†’ "2026-01"
```

**PARSE_DATE(value, format):** Parse date string to date object
```python
"2026-03-08" â†’ date(2026, 3, 8)
```

**EXTRACT_CURRENCY(metric_name):** Extract currency code from metric label
```python
"NAV USD" â†’ "USD"
"Balance SGD" â†’ "SGD"
"Opening" â†’ "SGD" (default)
```

**MAP_ACCOUNT(section_name):** Map section name to canonical account ID
```python
"cpf_oa" â†’ "CPF-OA"
"ib_net_liquidity" â†’ "IBKR-IBA"
```

**DIRECT:** No transformation, direct copy

**CONST(value):** Constant value assignment

**NOW():** Current timestamp at ETL runtime

### Type Rules

- **int:** Integer, NaN-incompatible (empty â†’ 0)
- **float:** Floating point, NaN-compatible (empty â†’ None)
- **str:** String
- **date:** Date object (YYYY-MM-DD format)
- **datetime:** Datetime object with timezone

### Null Rules

- **NOT NULL:** Value required, empty values rejected or filled with default
- **Nullable:** NULL/None values allowed

### Key Participation

- **PK:** Part of primary key
- **FK:** Part of foreign key
- **â€”:** Not a key field

### Validation Rules

- **YYYY-MM format:** Regex `^\d{4}-\d{2}$`
- **EXISTS IN {table}:** Referential integrity check
- **BETWEEN x AND y:** Range check
- **Valid ISO code:** 3-letter currency code (USD, SGD, etc.)
- **Numeric:** Value is numeric (int or float)
- **> 0:** Positive numeric value

---

## Summary Statistics

### Workbook Coverage

| Workbook             |                                                          |
| -------------------- | -------------------------------------------------------- |
| Sheets Mapped        |                                                          |
| Target Tables        |                                                          |
| Manual Steps         |                                                          |
| Automated Steps      |                                                          |
| financial-statements | 3 (balances, forex_rates, accounts)                      |
| cpf                  | 5 (cpf_total, cpf_oa, cpf_sa, cpf_ma, cpf_summary)       |
| ibkr-iba             | 4 (ib_net_liquidity, ib_cash, ib_securities, ib_summary) |
| cash-expenses        | 1 (recent_txns)                                          |
| shared-expenses      | 1 (records)                                              |
| homebudget-workbook  | 1 (cat_map)                                              |

| Workbook             |                                          |                        |
| -------------------- | ---------------------------------------- | ---------------------- |
| Sheets Mapped        |                                          |                        |
| Target Tables        |                                          |                        |
| Manual Steps         |                                          |                        |
| Automated Steps      |                                          |                        |
| financial-statements | 2 (account_balances, exchange_rates)     | 1 (balances entry)     |
| cpf                  | 1 (cpf_balances or asset_balances)       | 5 (all manual entry)   |
| ibkr-iba             | 1 (ibkr_balances or investment_balances) | 4 (all manual entry)   |
| cash-expenses        | 1 (cash_transactions)                    | 1 (manual entry)       |
| shared-expenses      | 1 (shared_expense_transactions)          | 1 (manual entry)       |
| homebudget-workbook  | 1 (category_mappings)                    | 1 (manual maintenance) |

| Workbook             |                          |
| -------------------- | ------------------------ |
| Sheets Mapped        |                          |
| Target Tables        |                          |
| Manual Steps         |                          |
| Automated Steps      |                          |
| financial-statements | 1 (potential automation) |
| cpf                  | 0                        |
| ibkr-iba             | 0                        |
| cash-expenses        | 0                        |
| shared-expenses      | 0                        |
| homebudget-workbook  | 0                        |

**Total:** 15 sheet ranges â†’ 7 target tables (estimated)

**Manual vs Automated:**

- Manual steps: ~13
- Automated/automatable steps: ~2

### Data Volume Estimates

| Target Table                |                                            |                     |
| --------------------------- | ------------------------------------------ | ------------------- |
| Estimated Rows per Month    |                                            |                     |
| Estimated Annual Rows       |                                            |                     |
| Notes                       |                                            |                     |
| account_balances            | ~10-20 accounts                            | ~120-240            |
| exchange_rates              | ~2 (USD start/end)                         | ~24                 |
| cpf_balances                | ~15-20 metrics Ã— 4 accounts Ã— 5 sections | ~900-1200 unpivoted |
| ibkr_balances               | ~30-50 metrics Ã— 4 sections               | ~360-600 unpivoted  |
| cash_transactions           | ~50-100 txns/month                         | ~600-1200           |
| shared_expense_transactions | ~10-30 txns/month                          | ~120-360            |
| category_mappings           | ~180 categories (static)                   | ~180                |

| Target Table                |                                     |
| --------------------------- | ----------------------------------- |
| Estimated Rows per Month    |                                     |
| Estimated Annual Rows       |                                     |
| Notes                       |                                     |
| account_balances            | One row per account per month       |
| exchange_rates              | Minimal forex pairs                 |
| cpf_balances                | High cardinality after unpivot      |
| ibkr_balances               | Matrix unpivot                      |
| cash_transactions           | Transaction-level detail            |
| shared_expense_transactions | Transaction-level detail            |
| category_mappings           | Reference table, infrequent updates |

**Total Estimated Annual Inserts:** ~2,400-4,000 rows
