# Helper Workbooks Consolidated Data Model

**Document Version:** 0.2.0  
**Last Updated:** March 8, 2026  
**Status:** Design Proposal

## Table of Contents

1. [Overview](#overview)
2. [Design Principles](#design-principles)
3. [Schema Delta from Baseline](#schema-delta-from-baseline)
4. [Helper Workbook Tables](#helper-workbook-tables)
5. [Integration with Existing Schema](#integration-with-existing-schema)
6. [Field-Level Mappings](#field-level-mappings)
7. [Constraints and Keys](#constraints-and-keys)
8. [Data Flow Summary](#data-flow-summary)

## Overview

This document defines the consolidated app-native data model for monthly closing in `financial_statements.db`. It builds upon the baseline schema defined in [database-schema.md](../database-schema.md) and embeds the business logic that was previously captured in helper workbooks.

Helper workbooks are design/reference artifacts only in this target state. They are used for:

- Discovery of legacy structures and business rules
- One-time historical backfill and parity validation during migration
- Incident investigation when historical workbook context is needed

They are not part of the steady-state monthly closing workflow.

The model adds tables/fields required to support:

- Asset account balances and metrics (CPF, IBKR)
- Expense transaction tracking (cash expenses, shared expenses)
- Category mapping from HomeBudget to financial statement line items
- Exchange rate tracking
- Source import lineage across app adapters (not workbook-specific)

The design preserves the two-stage reconciliation model (statement layer + ledger layer) and maintains immutability for imported snapshots.

## Design Principles

### 1. Single Consolidated Database

All monthly-closing data flows into `financial_statements.db` through application adapters. No helper workbook is required in steady state.

### 2. Two-Stage Separation

Maintain distinction between:

- **Statement layer:** Raw imported snapshots from source adapters (immutable snapshots)
- **Ledger layer:** Reconciled balances and computed metrics

### 3. Denormalized Metrics Storage

For asset accounts (CPF, IBKR), store metrics in semi-normalized format:

- Unpivot matrix formats into long-format records
- One row per (period, account, metric) combination
- Preserves audit trail of workbook data

### 4. Lineage Tracking

Every imported record includes:

- `source`: Source identifier (e.g., `cpf_portal_manual`, `ibkr_activity_csv`, `homebudget_sqlite`, `yahoo_fx_api`)
- `created_at`: Import timestamp
- Optional: `import_session_id` for batch tracking

### 5. Canonical Account IDs

Use canonical account IDs from `accounts.json` / `financial-statements.json` â†’ `accounts` sheet.
Map workbook shorthand IDs (e.g., "CPF-OA") to canonical IDs (e.g., "TWH CPF OA SGD") via configuration.

### 6. Workbook Deprecation by Design

Workbook-derived layouts are treated as temporary translation inputs, not operational dependencies.

- New monthly close runs should not require reading any helper workbook
- App modules own parsing, mapping, validation, and reconciliation logic
- Workbook parity checks are limited to migration and optional audit mode

## Schema Delta from Baseline

### New Tables

1. **`asset_balances`** - Asset account metrics from CPF and IBKR app adapters
2. **`cash_transactions`** - Cash expense transactions
3. **`shared_expense_transactions`** - Shared household expense transactions  
4. **`category_mappings`** - HomeBudget category to financial statement line item mapping
5. **`source_import_log`** - Import audit trail for app adapter runs

### Modified/Extended Tables

1. **`exchange_rates`** - Already in baseline, ensure structure supports workbook data
2. **`account_balances`** - May need `balance_type` field to distinguish NAV vs components

### No Changes Required

- `periods`
- `workflow_log`
- `statement_imports`, `statement_transactions`, `statement_balances` (used for bank statements)
- `financial_statements`, `statement_line_items` (output tables)

## Helper Workbook Tables

### Table: `asset_balances`

**Purpose:** Store asset account metrics from CPF and IBKR workbooks (matrix unpivot results)

```sql
CREATE TABLE asset_balances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    period_id TEXT NOT NULL,
    account_id TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    metric_section TEXT,          -- 'cpf_oa', ' ib_net_liquidity', etc.
    amount REAL,                   -- Nullable for sparse data
    currency TEXT NOT NULL,
    source TEXT NOT NULL,          -- 'gsheet_cpf' or 'gsheet_ibkr'
    source_workbook_id TEXT,       -- Google Sheets workbook ID
    source_range TEXT,             -- 'worksheet!A4:P10' (for reference)
    created_at TEXT NOT NULL,
    UNIQUE(period_id, account_id, metric_name, metric_section),
    FOREIGN KEY(period_id) REFERENCES periods(period_id)
);

CREATE INDEX idx_asset_balances_period_account 
    ON asset_balances(period_id, account_id);
CREATE INDEX idx_asset_balances_account 
    ON asset_balances(account_id);
```

**Data Volume Estimate:** ~1,000-1,500 rows per month (5 CPF sections Ã— 7 metrics Ã— 1 period + 4 IBKR sections Ã— 7 metrics Ã— 1 period)

**Sample Records:**
```sql
-- CPF OA closing balance
INSERT INTO asset_balances VALUES (
    NULL,
    '2026-02',
    'TWH CPF OA SGD',
    'END BAL',
    'cpf_oa',
    65000.00,
    'SGD',
    'gsheet_cpf',
    '1x9Dfq5RVwvmCGqX9aIgCRoarkhLYR3mWGmRRvQnLkbo',
    'worksheet!A13:P20',
    '2026-03-08 10:30:00'
);

-- IBKR IBA NAV
INSERT INTO asset_balances VALUES (
    NULL,
    '2026-02',
    'TWH IB POSITION USD',
    'END BAL',
    'ib_net_liquidity',
    151924.58,
    'USD',
    'gsheet_ibkr',
    '1i_ITkqvLRw5AFVmzqLaHp6PHlA2OERi3E-la00Ukngg',
    'worksheet!A4:P10',
    '2026-03-08 10:30:00'
);
```

**Metric Names (Examples):**

- `BEG BAL` - Opening balance
- `END BAL` - Closing balance
- `CONTRIBUTIONS` - Inflow (CPF)
- `WITHDRAWALS` - Outflow (CPF)
- `INTEREST` - Interest earned
- `INCOME` - Dividends + interest (IBKR)
- `RETURN` - % return for period (IBKR)

---

### Table: `cash_transactions`

**Purpose:** Store cash expense transactions from cash-expenses workbook

```sql
CREATE TABLE cash_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_date TEXT NOT NULL,     -- Parsed from DD/MM/YYYY HH:MM:SS
    period_id TEXT NOT NULL,            -- Derived from transaction_date
    account_id TEXT NOT NULL,           -- 'TWH CASH SGD' or mapped cash account
    budget TEXT,                        -- 'TWH', 'WPC', etc. (from workbook)
    category TEXT,                      -- 'AC', 'drinks', 'lunch', etc.
    amount REAL NOT NULL,
    currency TEXT NOT NULL DEFAULT 'SGD',
    description TEXT,
    source TEXT NOT NULL DEFAULT 'gsheet_cash_expenses',
    source_workbook_id TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(period_id) REFERENCES periods(period_id)
);

CREATE INDEX idx_cash_transactions_period 
    ON cash_transactions(period_id);
CREATE INDEX idx_cash_transactions_date 
    ON cash_transactions(transaction_date);
CREATE INDEX idx_cash_transactions_category 
    ON cash_transactions(category);
```

**Data Volume Estimate:** ~50-100 rows per month

**Sample Records:**
```sql
INSERT INTO cash_transactions VALUES (
    NULL,
    '2026-01-24 22:51:46',
    '2026-01',
    'TWH CASH SGD',
    'TWH',
    'AC',
    19.8,
    'SGD',
    NULL,  -- No description in source
    'gsheet_cash_expenses',
    '1ijbXG_wEP_icWH7xtbIO0bNVp4RbWPe1A5X1Q1i1nIo',
    '2026-03-08 10:30:00'
);
```

---

### Table: `shared_expense_transactions`

**Purpose:** Store shared household expense transactions

```sql
CREATE TABLE shared_expense_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_date TEXT NOT NULL,
    period_id TEXT NOT NULL,
    month_id TEXT,                      -- '202110' from source (redundant but preserves source format)
    item TEXT NOT NULL,                 -- '01 electricity', '02 water', etc.
    note TEXT,
    units TEXT,                         -- 'kWh', 'm3', etc.
    quantity REAL,
    rooms INTEGER,                      -- For cost splitting
    total_price REAL NOT NULL,
    currency TEXT NOT NULL DEFAULT 'SGD',
    account_id TEXT,                    -- Mapped to shared account or null
    source TEXT NOT NULL DEFAULT 'gsheet_shared_expenses',
    source_workbook_id TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(period_id) REFERENCES periods(period_id)
);

CREATE INDEX idx_shared_expense_transactions_period 
    ON shared_expense_transactions(period_id);
CREATE INDEX idx_shared_expense_transactions_item 
    ON shared_expense_transactions(item);
```

**Data Volume Estimate:** ~10-15 rows per month (utility line items)

**Sample Records:**
```sql
INSERT INTO shared_expense_transactions VALUES (
    NULL,
    '2021-10-01',
    '2021-10',
    '202110',
    '01 electricity',
    NULL,
    'kWh',
    251,
    1,
    59.87,
    'SGD',
    'COM UOB SGD',  -- Or shared household account
    'gsheet_shared_expenses',
    '1fVkiB_CXyJl2kBFEFrRb3Eb2wytWCUo1rOvveiGKZeo',
    '2026-03-08 10:30:00'
);
```

---

### Table: `category_mappings`

**Purpose:** Map HomeBudget categories to financial statement line items

```sql
CREATE TABLE category_mappings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hb_budget_cat TEXT NOT NULL,        -- 'Common UOB_Rent_Rent'
    budget TEXT,                        -- 'Common UOB'
    cat_id TEXT,                        -- '01'
    category TEXT,                      -- 'Rent'
    subcategory TEXT,                   -- 'Rent'
    fa_cat_id TEXT,                     -- '020100'
    fa_budget TEXT,                     -- '02 household'
    fa_category TEXT,                   -- '01 rental'
    fa_subcategory TEXT,
    account TEXT,                       -- 'Cash TWH SGD' (target financial account)
    source TEXT NOT NULL DEFAULT 'gsheet_cat_map',
    source_workbook_id TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT,
    UNIQUE(hb_budget_cat)
);

CREATE INDEX idx_category_mappings_cat_id 
    ON category_mappings(cat_id);
CREATE INDEX idx_category_mappings_fa_cat_id 
    ON category_mappings(fa_cat_id);
```

**Data Volume Estimate:** ~180 rows (static reference data, infrequent updates)

**Sample Records:**
```sql
INSERT INTO category_mappings VALUES (
    NULL,
    'Common UOB_Rent_Rent',
    'Common UOB',
    '01',
    'Rent',
    'Rent',
    '020100',
    '02 household',
    '01 rental',
    NULL,
    'Cash TWH SGD',
    'gsheet_cat_map',
    '1xF_cmgyKw2NHV6uj-bwo2O1D-eiyJwihlhFJSpMEKPg',
    '2026-03-08 10:30:00',
    NULL
);
```

---

### Table: `source_import_log`

**Purpose:** Audit trail for source adapter imports

```sql
CREATE TABLE source_import_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    import_session_id TEXT UNIQUE NOT NULL,
    source_adapter TEXT NOT NULL,           -- 'cpf_adapter', 'ibkr_csv_adapter', etc.
    source_ref TEXT,                        -- file path, URL, worksheet ID, or API endpoint
    source_entity TEXT,                     -- logical dataset/section name
    period_id TEXT,                         -- If period-specific import
    records_imported INTEGER,
    status TEXT NOT NULL CHECK (status IN ('success', 'partial', 'error')),
    error_message TEXT,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    FOREIGN KEY(period_id) REFERENCES periods(period_id)
);

CREATE INDEX idx_source_import_log_period 
    ON source_import_log(period_id);
```

**Data Volume Estimate:** ~6-12 rows per monthly close (one per adapter/entity imported)

---

### Table: `exchange_rates` (Extended)

**Purpose:** Store exchange rates from app source adapters (Yahoo/API/manual)

**Baseline Schema:**
```sql
CREATE TABLE exchange_rates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    currency_pair TEXT NOT NULL,
    rate REAL NOT NULL,
    source TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(date, currency_pair)
);
```

**Extension Needed:** Ensure `currency_pair` or split into `currency_from`, `currency_to`

**Proposed Update:**
```sql
DROP TABLE IF EXISTS exchange_rates;
CREATE TABLE exchange_rates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    currency_from TEXT NOT NULL,        -- 'USD'
    currency_to TEXT NOT NULL,          -- 'SGD'
    rate REAL NOT NULL,                 -- 1.3456
    source TEXT NOT NULL,               -- 'gsheet_forex', 'yahoo_finance'
    source_ref TEXT,
    created_at TEXT NOT NULL,
    UNIQUE(date, currency_from, currency_to)
);

CREATE INDEX idx_exchange_rates_date 
    ON exchange_rates(date);
CREATE INDEX idx_exchange_rates_currencies 
    ON exchange_rates(currency_from, currency_to);
```

**Sample Records:**
```sql
INSERT INTO exchange_rates VALUES (
    NULL,
    '2026-02-01',
    'USD',
    'SGD',
    1.3456,
    'yahoo_fx_api',
    'USD/SGD monthly close feed',
    '2026-03-08 10:30:00'
);
```

---

## Integration with Existing Schema

### `account_balances` Table Enhancement

**Current Baseline:**
```sql
CREATE TABLE account_balances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    period_id TEXT NOT NULL,
    account_id TEXT NOT NULL,
    opening_balance REAL NOT NULL,
    closing_balance REAL NOT NULL,
    currency TEXT NOT NULL,
    UNIQUE(period_id, account_id),
    FOREIGN KEY(period_id) REFERENCES periods(period_id)
);
```

**Issue:** Does not support multi-metric asset accounts (e.g., IBKR NAV vs Cash vs Securities)

**Option 1: Add `balance_type` field**
```sql
ALTER TABLE account_balances ADD COLUMN balance_type TEXT DEFAULT 'closing';
-- balance_type IN ('opening', 'closing', 'nav', 'cash', 'securities')
```

**Option 2: Use separate `asset_balances` table (Recommended)**

Keep `account_balances` for simple closing balances (bank accounts, wallets).
Use `asset_balances` for complex multi-metric accounts (CPF, IBKR).

**Decision:** Use separate `asset_balances` table to avoid schema complexity.

### Canonical Account Reference

**Option 1: Create `accounts` table in database**
```sql
CREATE TABLE accounts (
    account_id TEXT PRIMARY KEY,
    account_type TEXT NOT NULL,
    owner TEXT,
    name TEXT,
    currency TEXT NOT NULL,
    hb_account TEXT,
    statement_account TEXT,
    created_at TEXT NOT NULL
);
```

**Option 2: Keep `accounts.json` as external reference**

Validate account IDs against JSON file during ETL.

**Decision:** **Option 2 (transitional)** - Keep as external reference during migration.

**Target Direction:** Move canonical account registry into app-managed reference storage (table or versioned config) so monthly closing does not depend on helper workbooks.

---

## Field-Level Mappings

### CPF Workbook â†’ `asset_balances`

| Source | Source Field | Target Field | Transform |
|--------|-------------|--------------|-----------|
| cpf.json â†’ cpf_oa | Row 1 (year) | period_id | Composite: `{year}-{month:02d}` |
| cpf.json â†’ cpf_oa | Row 2 (month) | period_id | Composite: `{year}-{month:02d}` |
| cpf.json â†’ cpf_oa | Section name | account_id | Map: cpf_oa â†’ 'TWH CPF OA SGD' |
| cpf.json â†’ cpf_oa | Column A (metric) | metric_name | Direct |
| cpf.json â†’ cpf_oa | Cell value | amount | Parse numeric, remove commas |
| cpf.json â†’ cpf_oa | (constant) | currency | 'SGD' |
| cpf.json â†’ cpf_oa | Section name | metric_section | 'cpf_oa' |
| cpf.json â†’ cpf_oa | (constant) | source | 'gsheet_cpf' |

### IBKR Workbook â†’ `asset_balances`

| Source | Source Field | Target Field | Transform |
|--------|-------------|--------------|-----------|
| ibkr-iba.json â†’ ib_net_liquidity | Row 1 (year) | period_id | Composite: `{year}-{month:02d}` |
| ibkr-iba.json â†’ ib_net_liquidity | Row 2 (month) | period_id | Composite: `{year}-{month:02d}` |
| ibkr-iba.json â†’ ib_net_liquidity | (NAV metrics) | account_id | 'TWH IB POSITION USD' |
| ibkr-iba.json â†’ ib_cash | (Cash metrics) | account_id | 'TWH IB CASH USD' |
| ibkr-iba.json â†’ ib_net_liquidity | Column A (metric) | metric_name | Direct |
| ibkr-iba.json â†’ ib_net_liquidity | Cell value | amount | Parse numeric, remove commas |
| ibkr-iba.json â†’ ib_net_liquidity | Metric name | currency | Parse: "NAV USD" â†’ 'USD', "NAV SGD" â†’ 'SGD' |
| ibkr-iba.json â†’ ib_net_liquidity | Section name | metric_section | 'ib_net_liquidity' |
| ibkr-iba.json â†’ ib_net_liquidity | (constant) | source | 'gsheet_ibkr' |

### Cash Expenses Workbook â†’ `cash_transactions`

| Source | Source Field | Target Field | Transform |
|--------|-------------|--------------|-----------|
| cash-expenses.json â†’ recent_txns | date | transaction_date | Parse: 'DD/MM/YYYY HH:MM:SS' â†’ 'YYYY-MM-DD HH:MM:SS' |
| cash-expenses.json â†’ recent_txns | (derived) | period_id | Extract: 'YYYY-MM' from transaction_date |
| cash-expenses.json â†’ recent_txns | (constant or config) | account_id | 'TWH CASH SGD' |
| cash-expenses.json â†’ recent_txns | budget | budget | Direct |
| cash-expenses.json â†’ recent_txns | category | category | Direct |
| cash-expenses.json â†’ recent_txns | amount | amount | Direct (numeric) |
| cash-expenses.json â†’ recent_txns | (constant) | currency | 'SGD' |
| cash-expenses.json â†’ recent_txns | (constant) | source | 'gsheet_cash_expenses' |

### Shared Expenses Workbook â†’ `shared_expense_transactions`

| Source | Source Field | Target Field | Transform |
|--------|-------------|--------------|-----------|
| shared-expenses.json â†’ records | date | transaction_date | Parse: 'YYYY-MM-DD' |
| shared-expenses.json â†’ records | (derived) | period_id | Extract: 'YYYY-MM' from date |
| shared-expenses.json â†’ records | month | month_id | Direct (e.g., '202110') |
| shared-expenses.json â†’ records | item | item | Direct |
| shared-expenses.json â†’ records | note | note | Direct |
| shared-expenses.json â†’ records | units | units | Direct |
| shared-expenses.json â†’ records | qty | quantity | Direct (numeric) |
| shared-expenses.json â†’ records | rooms | rooms | Direct (int) |
| shared-expenses.json â†’ records | total price | total_price | Direct (numeric) |
| shared-expenses.json â†’ records | (constant) | currency | 'SGD' |
| shared-expenses.json â†’ records | (constant or config) | account_id | 'COM UOB SGD' or shared account |
| shared-expenses.json â†’ records | (constant) | source | 'gsheet_shared_expenses' |

### Financial Statements Workbook â†’ `account_balances`

| Source | Source Field | Target Field | Transform |
|--------|-------------|--------------|-----------|
| financial-statements.json â†’ balances | year, month | period_id | Composite: `{year}-{month:02d}` |
| financial-statements.json â†’ balances | account | account_id | Direct (already canonical) |
| financial-statements.json â†’ balances | balance | closing_balance | Direct (numeric) |
| financial-statements.json â†’ balances | (constant) | currency | 'SGD' |
| financial-statements.json â†’ balances | (constant) | source | 'gsheet_balances' |

**Note:** `opening_balance` derived from prior period `closing_balance`.

### Forex Rates Workbook â†’ `exchange_rates`

| Source | Source Field | Target Field | Transform |
|--------|-------------|--------------|-----------|
| financial-statements.json â†’ forex_rates | date | date | Direct (YYYY-MM-DD) |
| financial-statements.json â†’ forex_rates | currency | currency_from | Direct |
| financial-statements.json â†’ forex_rates | (constant) | currency_to | 'SGD' |
| financial-statements.json â†’ forex_rates | rate SGD | rate | Direct (numeric) |
| financial-statements.json â†’ forex_rates | (constant) | source | 'gsheet_forex' |

---

## Constraints and Keys

### Primary Keys

All tables use auto-increment `id` as primary key for simplicity.

### Unique Constraints

- `asset_balances`: (period_id, account_id, metric_name, metric_section)
- `account_balances`: (period_id, account_id)
- `exchange_rates`: (date, currency_from, currency_to)
- `category_mappings`: (hb_budget_cat)
- `source_import_log`: (import_session_id)

### Foreign Keys

- All tables with `period_id` â†’ `periods(period_id)`
- `cash_transactions`, `shared_expense_transactions` could FK to `accounts` table if created

### Indexes

Create indexes on:

- `period_id` (for period-based queries)
- `account_id` (for account-based queries)
- `transaction_date` (for date range queries)
- `category`, `item` (for categorization queries)

---

## Data Flow Summary

### Monthly Closing ETL Flow (Target State)

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ Source Systems              â”‚
â”‚ (CSV/PDF/API/SQLite/Portal) â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
           â”‚
           â”‚ ETL Process (Python App)
           â”‚ 1. Fetch via source adapters
           â”‚ 2. Parse per schema profiles
           â”‚ 3. Transform per mapping matrix
           â”‚ 4. Validate per cross-validation rules
           â”‚
           â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ financial_statements.db     â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Statement Layer:            â”‚
â”‚ - asset_balances            â”‚
â”‚ - cash_transactions         â”‚
â”‚ - shared_expense_trans...   â”‚
â”‚ - exchange_rates            â”‚
â”‚                             â”‚
â”‚ Reference:                  â”‚
â”‚ - category_mappings         â”‚
â”‚                             â”‚
â”‚ Audit:                      â”‚
â”‚ - source_import_log         â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
           â”‚
           â”‚ Reconciliation & Reporting
           â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ Ledger Layer:               â”‚
â”‚ - account_balances          â”‚
â”‚ - reconciliation_variances  â”‚
â”‚                             â”‚
â”‚ Output:                     â”‚
â”‚ - financial_statements      â”‚
â”‚ - statement_line_items      â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### Table Relationships

```
periods
   â”œâ”€â”€ asset_balances
   â”œâ”€â”€ cash_transactions
   â”œâ”€â”€ shared_expense_transactions
   â”œâ”€â”€ exchange_rates
   â”œâ”€â”€ account_balances
    â”œâ”€â”€ source_import_log
   â””â”€â”€ financial_statements

category_mappings (independent reference table)
```

### Data Volume Projections (Per Month)

| Table | Rows/Month | Annual Rows | Growth Rate |
|-------|-----------|-------------|-------------|
| asset_balances | 1,200 | 14,400 | Linear |
| cash_transactions | 75 | 900 | Linear |
| shared_expense_transactions | 12 | 144 | Linear |
| exchange_rates | 2 | 24 | Linear |
| account_balances | 25 | 300 | Linear |
| category_mappings | 0 (static) | 180 (total) | Rare updates |
| source_import_log | 8 | 96 | Linear |

**Total Annual Inserts:** ~16,000 rows (manageable for SQLite)

---

## Implementation Notes

### Migration Strategy

1. **Phase 1:** Create/rename tables (`asset_balances`, `cash_transactions`, `shared_expense_transactions`, `category_mappings`, `source_import_log`)
2. **Phase 2:** Extend `exchange_rates` table (if needed)
3. **Phase 3:** Implement app source adapters and embedded parsers (no workbook dependency)
4. **Phase 4:** Run parity mode against helper workbooks for selected periods
5. **Phase 5:** Deprecate helper workbook ingestion paths and retain read-only reference docs
6. **Phase 6:** Integrate fully app-native reconciliation workflow

### Immutability Rules

- Once imported for a period, records should not be updated
- Re-imports should create new `import_session_id` and mark old records as superseded (or delete and re-insert)
- Maintain import audit trail in `source_import_log`

### Reconciliation Integration

- Use `asset_balances` END BAL metrics to populate `account_balances.closing_balance`
- Validate CPF-Total = sum(CPF-OA, CPF-SA, CPF-MA)
- Validate IBKR NAV SGD â‰ˆ NAV USD Ã— FX rate
- Cross-check `cash_transactions` totals against bank statement cash withdrawals

### Deprecation Guardrails

- New ETL code paths must not require `gsheet/*.json` for monthly close execution.
- Workbook-based ingestion is allowed only under explicit `parity_mode` or `backfill_mode` flags.
- Any dependency on helper workbook availability in normal runs is a release blocker.
