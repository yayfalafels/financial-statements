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

| Source Workbook | Source Sheet | Source Column/Metric | Target Table | Target Column | Transform Rule | Type Rule | Null Rule | Key Participation | Validation Rule | Notes |
|-----------------|--------------|----------------------|--------------|---------------|----------------|-----------|-----------|-------------------|-----------------|-------|
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

---

### financial-statements → account_balances

**Source:** `gsheet/financial-statements.json` → `balances`  
**Target:** `account_balances` (ledger layer)  
**Parser:** Tabular (PARSE-003)

| Source Workbook | Source Sheet | Source Column | Target Table | Target Column | Transform Rule | Type Rule | Null Rule | Key Participation | Validation Rule | Notes |
|-----------------|--------------|---------------|--------------|---------------|----------------|-----------|-----------|-------------------|-----------------|-------|
| financial-statements | balances | year | account_balances | period_id | FORMAT("{}-{:02d}", year, month) | str | NOT NULL | PK | YYYY-MM format | Composite from year+month |
| financial-statements | balances | month | account_balances | period_id | FORMAT("{}-{:02d}", year, month) | str | NOT NULL | PK | month BETWEEN 1 AND 12 | Composite from year+month |
| financial-statements | balances | account | account_balances | account_id | DIRECT | str | NOT NULL | PK | EXISTS IN accounts.json | Must match canonical account |
| financial-statements | balances | balance | account_balances | closing_balance | DIRECT | float | NOT NULL | — | Numeric | Negative values allowed |
| — | — | — | account_balances | currency | CONST("SGD") | str | NOT NULL | — | Valid ISO code | Hardcoded SGD |
| — | — | — | account_balances | source | CONST("gsheet_balances") | str | NOT NULL | — | — | Lineage marker |
| — | — | — | account_balances | created_at | NOW() | datetime | NOT NULL | — | — | ETL timestamp |

**Primary Key:** (period_id, account_id)

**Foreign Keys:**

- period_id → periods(period_id)

---

### financial-statements → exchange_rates

**Source:** `gsheet/financial-statements.json` → `forex_rates`  
**Target:** `exchange_rates` (reference layer, if not already in baseline schema)  
**Parser:** Tabular (PARSE-003) with row 2 skip

| Source Workbook | Source Sheet | Source Column | Target Table | Target Column | Transform Rule | Type Rule | Null Rule | Key Participation | Validation Rule | Notes |
|-----------------|--------------|---------------|--------------|---------------|----------------|-----------|-----------|-------------------|-----------------|-------|
| financial-statements | forex_rates | date | exchange_rates | date | DIRECT | date | NOT NULL | PK | YYYY-MM-DD | — |
| financial-statements | forex_rates | currency | exchange_rates | currency_from | DIRECT | str | NOT NULL | PK | Valid ISO code | 3-letter code |
| — | — | — | exchange_rates | currency_to | CONST("SGD") | str | NOT NULL | PK | Valid ISO code | Hardcoded SGD |
| financial-statements | forex_rates | rate_SGD | exchange_rates | rate | DIRECT | float | NOT NULL | — | rate > 0 | — |
| — | — | — | exchange_rates | source | CONST("gsheet_forex") | str | NOT NULL | — | — | Lineage marker |
| — | — | — | exchange_rates | created_at | NOW() | datetime | NOT NULL | — | — | ETL timestamp |

**Primary Key:** (date, currency_from, currency_to)

**Notes:**

- Row 2 is spacer, data starts at row 3
- Expect 2 entries per month per currency (month start and month end)

---

### CPF → asset_balances (or cpf_balances)

**Source:** `gsheet/cpf.json` → all sections (cpf_total, cpf_oa, cpf_sa, cpf_ma, cpf_summary)  
**Target:** `asset_balances` or dedicated `cpf_balances` table (statement layer)  
**Parser:** Multi-Section Matrix Unpivot (PARSE-002 → PARSE-001)

| Source Workbook | Source Sheet/Section | Source Element | Target Table | Target Column | Transform Rule | Type Rule | Null Rule | Key Participation | Validation Rule | Notes |
|-----------------|----------------------|----------------|--------------|---------------|----------------|-----------|-----------|-------------------|-----------------|-------|
| cpf | {section} | column_header | cpf_balances | period_id | PARSE_PERIOD_ID(header) | str | NOT NULL | PK | YYYY-MM format | Extract from month column header |
| cpf | {section} | (section name) | cpf_balances | account_id | MAP_ACCOUNT(section) | str | NOT NULL | PK | EXISTS IN account map | cpf_total → "CPF-Total", etc. |
| cpf | {section} | row_label (col A) | cpf_balances | metric_name | DIRECT | str | NOT NULL | PK | Non-empty string | "Opening", "Contrib", etc. |
| cpf | {section} | cell_value | cpf_balances | amount | DIRECT | float | Nullable | — | Numeric or NULL | Skip empty cells |
| — | — | — | cpf_balances | currency | CONST("SGD") | str | NOT NULL | — | Valid ISO code | — |
| cpf | {section} | (section name) | cpf_balances | metric_section | DIRECT | str | NOT NULL | — | — | "cpf_total", "cpf_oa", etc. |
| — | — | — | cpf_balances | source | CONST("gsheet_cpf") | str | NOT NULL | — | — | Lineage marker |
| — | — | — | cpf_balances | created_at | NOW() | datetime | NOT NULL | — | — | ETL timestamp |

**Primary Key:** (period_id, account_id, metric_name, metric_section)

**Foreign Keys:**

- period_id → periods(period_id)
- account_id → canonical account list

**Account Mapping:**
```
cpf_total → CPF-Total
cpf_oa → CPF-OA
cpf_sa → CPF-SA
cpf_ma → CPF-MA
cpf_summary → CPF-Summary
```

**Validation Rules:**

- Cross-section balance check: Sum(CPF-OA, CPF-SA, CPF-MA closing) ≈ CPF-Total closing per month

---

### IBKR → investment_balances (or ibkr_balances)

**Source:** `gsheet/ibkr-iba.json` → all sections (ib_net_liquidity, ib_cash, ib_securities, ib_summary)  
**Target:** `investment_balances` or `ibkr_balances` (statement layer)  
**Parser:** Multi-Section Matrix Unpivot (PARSE-002 → PARSE-001)

| Source Workbook | Source Sheet/Section | Source Element | Target Table | Target Column | Transform Rule | Type Rule | Null Rule | Key Participation | Validation Rule | Notes |
|-----------------|----------------------|----------------|--------------|---------------|----------------|-----------|-----------|-------------------|-----------------|-------|
| ibkr-iba | {section} | column_header | ibkr_balances | period_id | PARSE_PERIOD_ID(header) | str | NOT NULL | PK | YYYY-MM format | Extract from month column header |
| ibkr-iba | {section} | (section name) | ibkr_balances | account_id | CONST("IBKR-IBA") | str | NOT NULL | PK | EXISTS IN account map | All sections → "IBKR-IBA" |
| ibkr-iba | {section} | row_label (col A) | ibkr_balances | metric_name | DIRECT | str | NOT NULL | PK | Non-empty string | "NAV USD", "NAV SGD", etc. |
| ibkr-iba | {section} | cell_value | ibkr_balances | amount | DIRECT | float | Nullable | — | Numeric or NULL | Skip empty cells |
| ibkr-iba | {section} | row_label (col A) | ibkr_balances | currency | EXTRACT_CURRENCY(metric_name) | str | NOT NULL | — | USD or SGD | Parse from metric name |
| ibkr-iba | {section} | (section name) | ibkr_balances | metric_section | DIRECT | str | NOT NULL | PK | — | "ib_net_liquidity", "ib_cash", etc. |
| — | — | — | ibkr_balances | source | CONST("gsheet_ibkr") | str | NOT NULL | — | — | Lineage marker |
| — | — | — | ibkr_balances | created_at | NOW() | datetime | NOT NULL | — | — | ETL timestamp |

**Primary Key:** (period_id, account_id, metric_name, metric_section)

**Foreign Keys:**

- period_id → periods(period_id)

**Currency Extraction Rule:**
```python
if "USD" in metric_name: return "USD"
elif "SGD" in metric_name: return "SGD"
else: return "USD"  # Default
```

**Validation Rules:**

- NAV_USD * forex_rate ≈ NAV_SGD per month (cross-validate with exchange_rates table)

---

### cash-expenses → cash_transactions

**Source:** `gsheet/cash-expenses.json` → `recent_txns`  
**Target:** `cash_transactions` or `statement_transactions` (statement layer)  
**Parser:** Tabular (PARSE-003) with row 1 skip

**Note:** Schema needs live inspection. Placeholder mapping below.

| Source Workbook | Source Sheet | Source Column | Target Table | Target Column | Transform Rule | Type Rule | Null Rule | Key Participation | Validation Rule | Notes |
|-----------------|--------------|---------------|--------------|---------------|----------------|-----------|-----------|-------------------|-----------------|-------|
| cash-expenses | recent_txns | {col_A_name} | cash_transactions | date | PARSE_DATE | date | NOT NULL | — | Valid date | Needs format confirmation |
| cash-expenses | recent_txns | {col_B_name} | cash_transactions | description | DIRECT | str | Nullable | — | — | Transaction description |
| cash-expenses | recent_txns | {col_C_name} | cash_transactions | category | DIRECT | str | Nullable | — | — | Expense category |
| cash-expenses | recent_txns | {col_D_name} | cash_transactions | amount | DIRECT | float | NOT NULL | — | Numeric | Transaction amount |
| — | — | — | cash_transactions | account_id | CONST("Cash") | str | NOT NULL | — | EXISTS IN account map | Implicit cash account |
| — | — | — | cash_transactions | currency | CONST("SGD") | str | NOT NULL | — | Valid ISO code | Assumed SGD |
| — | — | — | cash_transactions | source | CONST("gsheet_cash_expenses") | str | NOT NULL | — | — | Lineage marker |
| — | — | — | cash_transactions | created_at | NOW() | datetime | NOT NULL | — | — | ETL timestamp |

**Primary Key:** To be determined (possibly auto-increment ID or composite date+description+amount)

**Foreign Keys:**

- category → categories (if category lookup table exists)

**Action Required:** Live inspection to confirm column names and types.

---

### shared-expenses → shared_expense_transactions

**Source:** `gsheet/shared-expenses.json` → `records`  
**Target:** `shared_expense_transactions` or integrated into `statement_transactions` (statement layer)  
**Parser:** Tabular (PARSE-003)

**Note:** 8 columns (A-H) need live inspection. Placeholder mapping below.

| Source Workbook | Source Sheet | Source Column | Target Table | Target Column | Transform Rule | Type Rule | Null Rule | Key Participation | Validation Rule | Notes |
|-----------------|--------------|---------------|--------------|---------------|----------------|-----------|-----------|-------------------|-----------------|-------|
| shared-expenses | records | {col_A_name} | shared_expense_transactions | date | PARSE_DATE | date | NOT NULL | — | Valid date | Needs format confirmation |
| shared-expenses | records | {col_B_name} | shared_expense_transactions | description | DIRECT | str | Nullable | — | — | — |
| shared-expenses | records | {col_C_name} | shared_expense_transactions | amount | DIRECT | float | NOT NULL | — | Numeric | — |
| shared-expenses | records | {col_D_name} | shared_expense_transactions | participant | DIRECT | str | Nullable | — | — | Who paid or who owes |
| shared-expenses | records | {col_E_name} | shared_expense_transactions | split_amount | DIRECT | float | Nullable | — | Numeric | Individual share |
| shared-expenses | records | {col_F-H_names} | shared_expense_transactions | {TBD} | TBD | TBD | TBD | — | — | Needs inspection |
| — | — | — | shared_expense_transactions | currency | CONST("SGD") | str | NOT NULL | — | Valid ISO code | Assumed SGD, may be mixed |
| — | — | — | shared_expense_transactions | source | CONST("gsheet_shared_expenses") | str | NOT NULL | — | — | Lineage marker |
| — | — | — | shared_expense_transactions | created_at | NOW() | datetime | NOT NULL | — | — | ETL timestamp |

**Primary Key:** To be determined

**Action Required:** Live inspection to confirm schema.

---

### homebudget-workbook → category_mappings

**Source:** `gsheet/homebudget-workbook.json` → `cat_map`  
**Target:** `category_mappings` (reference layer)  
**Parser:** Tabular (PARSE-003)

**Note:** 10 columns (A-J) suggest hierarchical or multi-dimensional mapping. Needs live inspection.

| Source Workbook | Source Sheet | Source Column | Target Table | Target Column | Transform Rule | Type Rule | Null Rule | Key Participation | Validation Rule | Notes |
|-----------------|--------------|---------------|--------------|---------------|----------------|-----------|-----------|-------------------|-----------------|-------|
| homebudget-workbook | cat_map | {col_A_name} | category_mappings | hb_category_id | DIRECT | str/int | NOT NULL | PK | EXISTS IN HomeBudget | HomeBudget category ID |
| homebudget-workbook | cat_map | {col_B_name} | category_mappings | hb_category_name | DIRECT | str | Nullable | — | — | Human-readable name |
| homebudget-workbook | cat_map | {col_C-J_names} | category_mappings | {TBD} | TBD | TBD | TBD | — | — | Hierarchy levels or statement line mappings |
| — | — | — | category_mappings | source | CONST("gsheet_cat_map") | str | NOT NULL | — | — | Lineage marker |
| — | — | — | category_mappings | created_at | NOW() | datetime | NOT NULL | — | — | ETL timestamp |

**Primary Key:** To be determined (likely hb_category_id)

**Action Required:** Live inspection to understand mapping structure.

---

## Lineage Matrix

This matrix traces data from raw statement files through helper workbooks to the final database tables.

### Lineage Matrix Schema

| Raw Source Path | Source Format | Extracted Entity | Helper Workbook Sheet | Helper Workbook Field | Canonical Record Field | Target DB Table | Target DB Column | Transformation/Parse Rule | Manual Step Flag | Notes |
|-----------------|---------------|------------------|------------------------|------------------------|------------------------|-----------------|------------------|---------------------------|------------------|-------|
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

---

### IBKR Statement → ibkr-iba Workbook → ibkr_balances

| Raw Source Path | Source Format | Extracted Entity | Helper Workbook Sheet | Helper Workbook Field | Canonical Record Field | Target DB Table | Target DB Column | Transformation/Parse Rule | Manual Step Flag | Notes |
|-----------------|---------------|------------------|------------------------|------------------------|------------------------|-----------------|------------------|---------------------------|------------------|-------|
| reference/statements/ibkr-iba/U1109040_Activity_YYYYMM.csv | CSV | NAV (Net Asset Value) | ibkr-iba → worksheet | ib_net_liquidity → "NAV USD" metric | amount | ibkr_balances | amount | PARSE-001 unpivot | Yes - Manual | User manually enters NAV from statement |
| reference/statements/ibkr-iba/U1109040_Activity_YYYYMM.csv | CSV | Cash Balance | ibkr-iba → worksheet | ib_cash → "Cash USD" metric | amount | ibkr_balances | amount | PARSE-001 unpivot | Yes - Manual | User enters cash from statement |
| reference/statements/ibkr-iba/U1109040_Activity_YYYYMM.csv | CSV | Stock Holdings Market Value | ibkr-iba → worksheet | ib_securities → metric | amount | ibkr_balances | amount | PARSE-001 unpivot | Yes - Manual | User enters securities value |

**Manual Step:** User views IBKR statement PDF/CSV and manually enters summary values into the workbook matrix cells.

---

### CPF Statement → cpf Workbook → cpf_balances

| Raw Source Path | Source Format | Extracted Entity | Helper Workbook Sheet | Helper Workbook Field | Canonical Record Field | Target DB Table | Target DB Column | Transformation/Parse Rule | Manual Step Flag | Notes |
|-----------------|---------------|------------------|------------------------|------------------------|------------------------|-----------------|------------------|---------------------------|------------------|-------|
| {CPF statement portal} | Online Portal | OA Balance | cpf → worksheet | cpf_oa → "Closing" metric | amount | cpf_balances | amount | PARSE-001 unpivot | Yes - Manual | User logs into CPF portal, views balance, enters manually |
| {CPF statement portal} | Online Portal | SA Balance | cpf → worksheet | cpf_sa → "Closing" metric | amount | cpf_balances | amount | PARSE-001 unpivot | Yes - Manual | — |
| {CPF statement portal} | Online Portal | MA Balance | cpf → worksheet | cpf_ma → "Closing" metric | amount | cpf_balances | amount | PARSE-001 unpivot | Yes - Manual | — |
| {CPF statement portal} | Online Portal | Contributions | cpf → worksheet | cpf_oa → "Contrib" metric | amount | cpf_balances | amount | PARSE-001 unpivot | Yes - Manual | — |
| {CPF statement portal} | Online Portal | Interest | cpf → worksheet | cpf_oa → "Interest" metric | amount | cpf_balances | amount | PARSE-001 unpivot | Yes - Manual | — |

**Manual Step:** User accesses CPF online portal (no raw statement file available in repo), manually enters values into workbook.

---

### Bank Statement → cash-expenses Workbook → cash_transactions

| Raw Source Path | Source Format | Extracted Entity | Helper Workbook Sheet | Helper Workbook Field | Canonical Record Field | Target DB Table | Target DB Column | Transformation/Parse Rule | Manual Step Flag | Notes |
|-----------------|---------------|------------------|------------------------|------------------------|------------------------|-----------------|------------------|---------------------------|------------------|-------|
| reference/statements/citi-twh/Citibank Personal - YYYYMM.pdf | PDF | Cash withdrawal transaction | cash-expenses → recent_txns | Row entry | transaction | cash_transactions | date, amount, description | PARSE-003 tabular | Yes - Manual | User views statement PDF, enters cash txns manually |
| reference/statements/dbs-multi/DBSStatement_YYYYMM.pdf | PDF | Cash transaction | cash-expenses → recent_txns | Row entry | transaction | cash_transactions | date, amount, description | PARSE-003 tabular | Yes - Manual | — |

**Manual Step:** User reviews bank statement PDFs for cash withdrawals, manually records expenses in cash-expenses workbook.

---

### HomeBudget → financial-statements Workbook → account_balances

| Raw Source Path | Source Format | Extracted Entity | Helper Workbook Sheet | Helper Workbook Field | Canonical Record Field | Target DB Table | Target DB Column | Transformation/Parse Rule | Manual Step Flag | Notes |
|-----------------|---------------|------------------|------------------------|------------------------|------------------------|-----------------|------------------|---------------------------|------------------|-------|
| HomeBudget SQLite DB | SQLite | Account balance | financial-statements → balances | balance column | closing_balance | account_balances | closing_balance | PARSE-003 tabular | No - Automated | Production path is direct app adapter to database, workbook parity optional |

**Manual Step:** No manual step in target-state production flow, direct HomeBudget API or DB query is required.

---

### External API → financial-statements Workbook → exchange_rates

| Raw Source Path | Source Format | Extracted Entity | Helper Workbook Sheet | Helper Workbook Field | Canonical Record Field | Target DB Table | Target DB Column | Transformation/Parse Rule | Manual Step Flag | Notes |
|-----------------|---------------|------------------|------------------------|------------------------|------------------------|-----------------|------------------|---------------------------|------------------|-------|
| Yahoo Finance API | API/JSON | USD/SGD exchange rate | financial-statements → forex_rates | rate_SGD column | rate | exchange_rates | rate | PARSE-003 tabular | No - Automated | Production path writes rates directly through app FX adapter, workbook parity optional |

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
"Jan 2026" → "2026-01"
"2026-01" → "2026-01"
```

**PARSE_DATE(value, format):** Parse date string to date object
```python
"2026-03-08" → date(2026, 3, 8)
```

**EXTRACT_CURRENCY(metric_name):** Extract currency code from metric label
```python
"NAV USD" → "USD"
"Balance SGD" → "SGD"
"Opening" → "SGD" (default)
```

**MAP_ACCOUNT(section_name):** Map section name to canonical account ID
```python
"cpf_oa" → "CPF-OA"
"ib_net_liquidity" → "IBKR-IBA"
```

**DIRECT:** No transformation, direct copy

**CONST(value):** Constant value assignment

**NOW():** Current timestamp at ETL runtime

### Type Rules

- **int:** Integer, NaN-incompatible (empty → 0)
- **float:** Floating point, NaN-compatible (empty → None)
- **str:** String
- **date:** Date object (YYYY-MM-DD format)
- **datetime:** Datetime object with timezone

### Null Rules

- **NOT NULL:** Value required, empty values rejected or filled with default
- **Nullable:** NULL/None values allowed

### Key Participation

- **PK:** Part of primary key
- **FK:** Part of foreign key
- **—:** Not a key field

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

| Workbook | Sheets Mapped | Target Tables | Manual Steps | Automated Steps |
|----------|---------------|---------------|--------------|-----------------|
| financial-statements | 3 (balances, forex_rates, accounts) | 2 (account_balances, exchange_rates) | 1 (balances entry) | 1 (potential automation) |
| cpf | 5 (cpf_total, cpf_oa, cpf_sa, cpf_ma, cpf_summary) | 1 (cpf_balances or asset_balances) | 5 (all manual entry) | 0 |
| ibkr-iba | 4 (ib_net_liquidity, ib_cash, ib_securities, ib_summary) | 1 (ibkr_balances or investment_balances) | 4 (all manual entry) | 0 |
| cash-expenses | 1 (recent_txns) | 1 (cash_transactions) | 1 (manual entry) | 0 |
| shared-expenses | 1 (records) | 1 (shared_expense_transactions) | 1 (manual entry) | 0 |
| homebudget-workbook | 1 (cat_map) | 1 (category_mappings) | 1 (manual maintenance) | 0 |

**Total:** 15 sheet ranges → 7 target tables (estimated)

**Manual vs Automated:**

- Manual steps: ~13
- Automated/automatable steps: ~2

### Data Volume Estimates

| Target Table | Estimated Rows per Month | Estimated Annual Rows | Notes |
|--------------|-------------------------|----------------------|-------|
| account_balances | ~10-20 accounts | ~120-240 | One row per account per month |
| exchange_rates | ~2 (USD start/end) | ~24 | Minimal forex pairs |
| cpf_balances | ~15-20 metrics × 4 accounts × 5 sections | ~900-1200 unpivoted | High cardinality after unpivot |
| ibkr_balances | ~30-50 metrics × 4 sections | ~360-600 unpivoted | Matrix unpivot |
| cash_transactions | ~50-100 txns/month | ~600-1200 | Transaction-level detail |
| shared_expense_transactions | ~10-30 txns/month | ~120-360 | Transaction-level detail |
| category_mappings | ~180 categories (static) | ~180 | Reference table, infrequent updates |

**Total Estimated Annual Inserts:** ~2,400-4,000 rows