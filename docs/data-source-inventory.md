# Data Source Inventory and Gap Log

**Document Version:** 0.1.0  
**Last Updated:** February 23, 2026  
**Status:** Draft (Step 2 of Design Workflow)

## Table of Contents

1. [Overview](#overview)
2. [Data Source Inventory](#data-source-inventory)
3. [Integration Points and Data Flows](#integration-points-and-data-flows)
4. [Existing Calculation Logic](#existing-calculation-logic)
5. [Gap Analysis](#gap-analysis)
6. [Missing Configurations](#missing-configurations)
7. [Integration Constraints](#integration-constraints)
8. [References](#references)

---

## Overview

This document inventories all data sources feeding the financial statements application, documents existing calculation logic in the reference implementation, identifies gaps between current capabilities and the MVP design specification, and logs missing configurations.

**Key Finding:** The application architecture uses a **multi-workbook model** where helper worksheets (IBKR, CPF) are manually updated by the user, and the main financial statements workbook aggregates data from HomeB udget, helper workbooks, and forex data. This is fundamentally different from a fully automated ETL pipeline; the design accommodates significant manual data entry and validation steps.

---

## Data Source Inventory

### 1. HomeBudget Local SQLite Database

**Location:** User's local machine (path in `home_budget_config.json`)

**Purpose:** Primary transaction ledger for personal expenses and income

**Key Tables:**

| Table | Purpose | Key Fields | Status | Notes |
|---|---|---|---|---|
| `accounts` | Account registry | account_id, name, type, currency, opening_balance | ✓ Exists | HomeBudget native; supports wallets, bank, credit card |
| `categories` | Expense/income category hierarchy | category_id, name, parent_id, type | ✓ Exists | Hierarchical; maps to statement line items |
| `transactions` | Journal entries | date, account_id, category_id, amount, currency, notes | ✓ Exists | Core transaction log; must validate date, category, account refs |
| `balances` | Month-end balance snapshot | year, month, account_id, balance | Partial | May not exist for all periods; manual entry required |
| `exchange_rates` | Historical FX rates | date, currency_from, currency_to, rate | Missing | Not in HomeBudget; must fetch from Yahoo Finance |

**Data Quality Assumptions:**
- All transactions have valid `account_id` and `category_id` references
- Dates are within the current fiscal year (Jan 1 - Dec 31)
- Currencies are 3-letter ISO codes (USD, SGD)
- Numeric amounts are precise to 2 decimal places

**Data Quality Controls Needed:**
- Validate account/category references before import
- Detect and flag orphaned transactions (missing category/account)
- Check for date outliers (future dates, very old entries)
- Cross-check HomeBudget balance with computed balance (Opening + Inflows - Outflows)

**Access Patterns:**
- Read-only for statement generation
- CRUD for balance updates during account reconciliation
- CRUD for transaction entry during account update workflow

### 2. Google Sheets Main Workbook

**Workbook ID:** `1-Gy9kEUF0RbKWsztoZbVwbi65PXNhP1qPdylXod5JBE`

**Purpose:** Central statement repository and source for derived calculations

**Key Sheets:**

| Sheet | Range | Purpose | Key Fields | Status | Notes |
|---|---|---|---|---|---|
| `balances` | A1:D | Monthly account balance snapshot | year, month, account, balance_SGD | ✓ Exists | Source of truth for period-end balances |
| `forex_rates` | A1:F | Historical USD/SGD rates | year, month, date, currency, rate_SGD | ✓ Exists | Month-beginning and month-end rates; manually updated |
| `config` | A1:N | Reporting parameters | reporting_period, reporting_currency, included_entities | ✓ Exists | Defines statement scope |
| `income_statement` | A1:D | Income statement template | line_item, amount_SGD, notes | Partial | Template exists; calculations manual |
| `balance_sheet` | A1:D | Balance sheet template | asset_account, amount_SGD, liabilities_account, equity_account | Partial | Template exists; calculations manual |
| `reconcile` | A1:E | Reconciliation tracker | account, expected_balance, actual_balance, variance | Missing | No dedicated reconciliation sheet |
| `transaction_detail` | — | Supporting transaction detail | date, account, category, amount, description | Missing | Not in main workbook |

**Update Pattern:**
- Pre-flight: Fetch latest forex rates from Yahoo Finance (external), update `forex_rates` sheet
- Account update: User manually updates `balances` sheet with closing balances from statements
- Report generation: Local Python script reads `balances`, `forex_rates`, computes income/balance sheets, writes summary back

**Data Quality Assumptions:**
- `balances` sheet has entries for all accounts in the reporting period
- `forex_rates` has month-beginning and month-end rates for USD/SGD
- `config` sheet specifies valid reporting currency and period

### 3. IBKR Helper Workbook

**Workbook ID:** `1i_ITkqvLRw5AFVmzqLaHp6PHlA2OERi3E-la00Ukngg`

**Primary Sheet:** `worksheet` (worksheet!$A$1:$P$30)

**Purpose:** Interactive Brokers account positions, P&L, and holdings summary with time-series monthly tracking

**Structure:** The worksheet uses a multi-region time-series layout with shared header row:

**Header (Row 1-2):**
- Row 1: Years (2026, 2025, 2026, etc. — denotes which year each column references)
- Row 2: Statement month IDs (1, 12, 1, 2, 3, ..., 12, 1) — numeric month identifier for each column

**Data Regions** (each with Columns A-P; A contains row labels, B-P contain monthly values):

#### Region 1: IB Net Liquidity (Rows 3-10)
**Range:** worksheet!$A$3:$P$10  
**Row Labels:** BEG BAL, END BAL, INCOME, EXPENSE, NET INCOME, FEES, MARKET P&L, TOTAL P&L

| Field | Type | Description |
|---|---|---|
| BEG BAL | float | Month-opening account value in USD |
| END BAL | float | Month-closing account value in USD |
| INCOME | float | Dividends + interest received in USD |
| EXPENSE | float | Account fees + transaction costs in USD |
| NET INCOME | float | INCOME - EXPENSE in USD |
| FEES | float | Total fees charged in USD |
| MARKET P&L | float | Unrealized gains/losses on open positions |
| TOTAL P&L | float | Realized + unrealized profit/loss for month |

#### Region 2: IB Cash Account (Rows 11-15)
**Range:** worksheet!$A$11:$P$15  
**Row Labels:** BEG BAL, DEPOSITS, WITHDRAWALS, INTEREST, CHANGE BAL

| Field | Type | Description |
|---|---|---|
| BEG BAL | float | Month-opening cash balance in USD |
| DEPOSITS | float | Cash additions (new funding) in USD |
| WITHDRAWALS | float | Cash removals in USD |
| INTEREST | float | Interest earned on cash in USD |
| CHANGE BAL | float | END BAL - BEG BAL (reconciliation check) |

#### Region 3: IB Securities Holdings (Rows 16-25)
**Range:** worksheet!$A$16:$P$25  
**Row Labels:** BEG BAL, DIVIDEND INCOME, REALIZED GAIN/LOSS, FEES, MARKET GAIN/LOSS, CORPORATE ACTIONS, TRANSFERS, END BAL, plus 2 additional breakdown rows

| Field | Type | Description |
|---|---|---|
| BEG BAL | float | Month-opening securities value in USD |
| DIVIDEND INCOME | float | Dividend collected in USD |
| REALIZED GAIN/LOSS | float | Profit/loss on closed positions in USD |
| FEES | float | Trading commissions/fees in USD |
| MARKET GAIN/LOSS | float | Unrealized gain on open positions in USD |
| CORPORATE ACTIONS | float | Adjustments for splits, mergers in USD |
| TRANSFERS | float | Position adjustments from transfers in USD |
| END BAL | float | Month-closing securities value in USD |

#### Region 4: IB Summary & FX Rates (Rows 26-30)
**Range:** worksheet!$A$26:$P$30  
**Row Labels:** SGD.USD (FX rate), USD.SGD (inverse rate), USD EXPOSURE, SGD VALUE, TOTAL

| Field | Type | Description |
|---|---|---|
| SGD.USD | float | Month-end exchange rate (SGD per USD) |
| USD.SGD | float | Month-end inverse rate (USD per SGD) |
| USD EXPOSURE | float | Total gross exposure in USD |
| SGD VALUE | float | Account value converted to SGD (USD × SGD.USD rate) |
| TOTAL | float | Total account value including cash and securities |

**Data Quality Assumptions:**
- All numeric fields contain valid floats or are blank (treated as 0)
- Column headers (months) align with actual month numbers
- BEG BAL and END BAL balance (END BAL = BEG BAL + NET INCOME for liquidity)
- FX rates are between 1.2 and 1.4 (reasonable SGD/USD range)
- Date alignment: All columns represent same calendar month across rows (no data misalignment)

**Data Quality Controls Needed:**
- Validate that all numeric fields parse as floats
- Cross-check BEG BAL of current month = END BAL of prior month
- Verify FX rate consistency: USD.SGD ≈ 1/(SGD.USD)
- Ensure all columns have corresponding month values in header row (no orphaned columns)
- Flag negative balances or unusually large swings (>50% month-over-month)

**Access Pattern:**
- User manually updates worksheet monthly with data from IBKR statement PDF
- Python script reads this sheet during report generation
- Used to compute IBKR account contribution to net worth (balance sheet) and investment income
- FX rates used to convert USD amounts to SGD for consolidated reporting

**Configuration:**
```json
{
  "wkbid": "1i_ITkqvLRw5AFVmzqLaHp6PHlA2OERi3E-la00Ukngg",
  "ib_net_liquidity": {
    "header": "worksheet!$A$2:$P$2",
    "data": "worksheet!$A$4:$P$10"
  },
  "ib_cash": {
    "header": "worksheet!$A$2:$P$2",
    "data": "worksheet!$A$12:$P$15"
  },
  "ib_securities": {
    "header": "worksheet!$A$2:$P$2",
    "data": "worksheet!$A$18:$P$25"
  },
  "ib_summary": {
    "header": "worksheet!$A$2:$P$2",
    "data": "worksheet!$A$27:$P$30"
  }
}
```


### 4. CPF Helper Workbook

**Workbook ID:** `1x9Dfq5RVwvmCGqX9aIgCRoarkhLYR3mWGmRRvQnLkbo`

**Primary Sheet:** `worksheet`

**Purpose:** Singapore CPF (Central Provident Fund) statement parsing and balance tracking

**Key Fields (inferred from Singapore CPF structure):**

| Field | Purpose | Data Type | Source | Notes |
|---|---|---|---|---|
| `cpf_account_type` | Subaccount designation | str | CPF statement | OA (Ordinary), SA (Special), MA (Medisave), RA (Retirement) |
| `opening_balance_sgd` | Month-start balance | float | CPF statement | SGD per subaccount |
| `contribution_sgd` | Employer/employee contribution | float | CPF statement | Monthly contribution (if employed) |
| `interest_sgd` | Interest accrued | float | CPF statement | Annual interest on balances |
| `withdrawal_sgd` | Amount withdrawn | float | CPF statement | If any permitted withdrawal |
| `closing_balance_sgd` | Month-end balance | float | CPF statement | SGD per subaccount |

**Data Quality Assumptions:**
- CPF account types are one of: OA, SA, MA, RA
- All amounts are non-negative (CPF cannot go negative)
- Closing balance = opening + contributions + interest - withdrawals (with rounding)
- CPF data is in SGD (no currency conversion needed)

**Data Quality Controls Needed:**
- Validate account type codes
- Check balance reconciliation: opening + changes = closing
- Flag unusual withdrawals (should be rare for OA/SA unless retirement age)
- Detect missing months in statement history

**Access Pattern:**
- User manually updates worksheet with CPF statement data annually or semi-annually
- Python script reads during report generation for balance updates
- CPF is treated as long-term savings/retirement account; not included in regular income/expense statement

### 6. HomeBudget Category Mapping Workbook

**Workbook ID:** `1xF_cmgyKw2NHV6uj-bwo2O1D-eiyJwihlhFJSpMEKPg`

**Primary Sheet:** `cat_map`

**Purpose:** Map HomeBudget expense/income categories to statement line items

**Use:** Python script reads mapping on startup; applies during aggregation to group HomeBudget transactions by statement category

**Expected Content:**
- Column 1: HomeBudget category name
- Column 2+: Mapping to statement category hierarchy (Category > SubCategory > DetailItem)
- Example: `HomeBudget="Groceries"` → `Statement="Expenses > Living Expenses > Groceries"`

**Note:** Schema to be inspected directly via [.dev/.scripts/python/inspect_helper_schemas.py](.dev/.scripts/python/inspect_helper_schemas.py)

#### Yahoo Finance USD/SGD Exchange Rates

**URL:** `https://sg.finance.yahoo.com/quote/SGD%3DX/`

**Purpose:** Historical USD/SGD rates for multi-currency consolidation

**Data to Fetch:**
- Month-beginning rate (first business day of month)
- Month-end rate (last calendar day of month)

**Frequency:** Monthly (before monthly close)

**Data Quality:**
- Rates are published at market close (Singapore time)
- Public rates vs. bank rates may differ slightly; use Yahoo Finance for consistency
- Verify rate is between 1.2 and 1.4 SGD/USD (sanity check range)

**Implementation Note:** Currently manual; should be automated via Python script using `yfinance` library

### 6. Configuration Files

#### gsheet_config.json

**Location:** `gsheet/gsheet_config.json`

**Current Content:**
```json
{
  "wkbid":"1-Gy9kEUF0RbKWsztoZbVwbi65PXNhP1qPdylXod5JBE",
  "balances": {
    "data":"balances!A2:D",
    "header":"balances!A1:D1",
    "data_types": {
      "year":"int",
      "month":"int",
      "account":"str",
      "balance":"float"
    }
  },
  "forex_rates": {
    "data":"forex_rates!A3:F",
    "header":"forex_rates!A1:F1",
    "date_format": "%Y-%m-%d",
    "data_types": {
      "year":"int",
      "month":"int",
      "date":"date",
      "currency":"str",
      "rate_SGD":"float"
    }
  }
}
```

**Missing Entries (Gap):**
- IBKR helper workbook configuration
- CPF helper workbook configuration
- Statement output templates (income statement, balance sheet, reconciliation sheets)

#### home_budget_config.json

**Location:** `config.json` (in reference project) or path specified in pyproject

**Purpose:** HomeBudget database connection and category mapping

**Expected Content (inferred):**
```json
{
  "db_path": "path/to/homebudget.db",
  "db_status": "OK",
  "category_mapping": { ... },
  "account_mapping": { ... }
}
```

**Status:** Needs to be created or imported from reference project

---

## Integration Points and Data Flows

### Flow 1: Monthly Close-Out

**Trigger:** Last business day of month

**Steps:**
1. **Yahoo Finance** → Fetch USD/SGD month-end rate
2. **User updates** → IBKR and CPF helper workbooks with statements
3. **Python script** reads IBKR, CPF worksheets; computes balances
4. **HomeBudget** → User enters transactions from month (income, expenses, transfers)
5. **Google Sheets** `balances` → Python script writes month-end balances
6. **Google Sheets** `forex_rates` → Python script writes forex rates
7. **Reconciliation** → User reviews balances sheet for mismatches
8. **Report generation** → Python script reads all sources, computes income/balance sheets

### Flow 2: Account Reconciliation (Account Update Workflow)

**Workflow Steps (per workflow.md):**

| Step | Source | Target | Data Element | Mode |
|---|---|---|---|---|
| 1. Download statement | Bank website | Local file | PDF/CSV statement | Manual |
| 2. Parse statement | Local file | IBKR/CPF helper workbook | Transactions, holdings, balances | Manual |
| 3. Compute intermediate | IBKR/CPF helper workbook | Intermediate calculations | P&L, realized gains, expense detail | Formulas in worksheet |
| 4. Validate balances | IBKR/CPF helper workbook | User review | Account balance, variances | Manual |
| 5. Update HomeBudget | User input | HomeBudget database | Transactions (expenses, income, transfers) | Python CRUD |
| 6. Update master balances | IBKR/CPF balance | Google Sheets `balances` | Month-end balance | Python write |

**Dependency:** Step 5 requires Step 4 to be complete with validated balances

### Flow 3: Report Generation

**Inputs:**
- `balances` sheet (source of truth for account balances)
- `forex_rates` sheet (FX conversion rates)
- HomeBudget transactions (income and expense detail)
- IBKR helper workbook (P&L contribution to unrealized gains)
- CPF helper workbook (retirement account detail)

**Processing:**
1. Read `balances` sheet; organize by account
2. Read `forex_rates` sheet; identify month-beginning and month-end rates
3. Query HomeBudget; filter transactions by reporting period
4. Compute income statement:
   - Group expenses by category
   - Group income by type
   - Gross up by USD/SGD conversion (transaction date rate)
   - Add IBKR P&L and unrealized gains
5. Compute balance sheet:
   - Sum asset accounts converted to SGD at month-end rate
   - Sum liability accounts converted to SGD at month-end rate
   - Equity = Assets - Liabilities
6. Compute FX variance:
   - FX on transactions = sum of trans × (trans_date_rate - month_beg_rate)
   - FX on balances = sum of balances × (month_end_rate - month_beg_rate)
   - Book difference to "FX Gain/Loss" line

**Outputs:**
- PDF statement (income + balance + schedules)
- Excel workbook (with formulas and detail)
- CSV exports (for data validation)
- Google Sheets summary back to main workbook

---

## Existing Calculation Logic

### From Reference Implementation (hb-finances)

**File: `reference/hb-finances/homebudget.py`**
- **Module Purpose:** Interface with HomeBudget SQLite database
- **Key Functions:**
  - `load()` — Load config and connect to database
  - `load_hb()` — Create HomeBudgetAgent for CRUD operations
  - **Expense CRUD:** Class for adding notes, validating fields, writing to SQLite
  - **Category mapping:** Config-based mapping of HomeBudget categories to reporting categories
- **Status:** Complete reference; can be adapted for new project

**File: `reference/hb-finances/statements.py`**
- **Module Purpose:** Bank statement parsing and balance tracking
- **Key Functions:**
  - `load_config()` — Load statement_config.json for account list
  - `load_db()` — Connect to SQLite for balance tracking
  - `AccountDirectory` — Class representing statement account with balance history
  - `get_reporting_config()` — Extract reporting parameters from Google Sheets
  - **Statement parsing:** Account-specific parsers (CSV format, row skips, column mapping)
  - **Balance reconciliation:** Compute expected balance from statement detail
- **Status:** Partial; statement parsing is account-specific and requires customization per bank

**File: `reference/hb-finances/database.py`**
- **Module Purpose:** Data access layer for SQLite and Google Sheets
- **Key Functions:**
  - `load_sql()` — Create SQLAlchemy engine for HomeBudget
  - `load_gsheet()` — Initialize Google Sheets API client
  - `get_table()` — Pandas read from SQLite
  - `update_table()` — Pandas write to SQLite
  - `get_sheet()` — Pandas read from Google Sheets via `sqlite-gsheet`
- **Status:** Functional reference; demonstrates data access patterns

### Existing Calculations Not Yet Implemented

1. **Multi-currency consolidation:** No existing logic for USD/SGD conversion in reference code
2. **FX gain/loss:** Not computed; would need to track transaction-date rates separately
3. **Unrealized gains:** Not in HomeBudget; must pull from IBKR statement or helper workbook
4. **Budget variance:** Not applicable (no budget data in HomeBudget)
5. **Account hierarchies:** Reference code uses flat account list; no parent-child aggregation

---

## Gap Analysis

### Critical Gaps (Block MVP)

| Gap | Severity | Details | Impact | Mitigation |
|---|---|---|---|---|
| **FX rate history** | Critical | Yahoo Finance fetch automation missing | Cannot compute multi-currency P&L | Create `fetch_forex_rates.py` script |
| **Helper workbook config** | Critical | `gsheet_config.json` missing IBKR/CPF entries | Cannot read helper sheets | Add IBKR/CPF sheet definitions to gsheet_config.json |
| **IBKR P&L mapping** | High | Unclear which IBKR worksheet columns → statement P&L | Cannot allocate investment gains correctly | Document IBKR worksheet schema in Step 2 addendum |
| **CPF transaction history** | High | No CPF transaction detail; only annual/semi-annual snapshots | Cannot reconcile CPF month-to-month | Accept CPF as manual balance entry only; defer transaction detail to backlog |
| **HomeBudget config** | High | Category and account mapping not defined | Cannot map HomeBudget data to statement | Create `home_budget_config.json` from reference project |
| **Reconciliation sheet** | Medium | No automated balance reconciliation logic | Manual reconciliation labor-intensive | Create reconciliation formula sheet in Google Sheets template |
| **Transaction detail export** | Medium | No column mapping for statement detail | Audit trail missing for statement review | Add transaction detail DataFrame creation in report generation |

### Important Gaps (Backlog)

| Gap | Details | Backlog Priority |
|---|---|---|
| **Budget vs. actual** | Budgets not configured in HomeBudget; budget variance report deferred | Q2 2026 |
| **Cash flow statement** | Not required for MVP; add in Phase 2 | Q2 2026 |
| **Investment portfolio analysis** | No holdings detail or performance attribution | Q3 2026 |
| **Tax optimization** | No provision for tax planning or deferred tax | Q3 2026 |
| **Multi-entity consolidation** | Personal finance only; not applicable to MVP | Future |
| **Depreciation** | Personal assets held at cost; no depreciation | Future |
| **Automated statement download** | User manually downloads statements; API access not available for all institutions | Evaluate per institution |

---

## Missing Configurations

### 1. Extended gsheet_config.json

**Current Gap:** IBKR and CPF helper workbooks not defined

**Required Addition:**
```json
{
  "ibkr_helper": {
    "wkbid": "1i_ITkqvLRw5AFVmzqLaHp6PHlA2OERi3E-la00Ukngg",
    "sheet": "worksheet",
    "data_columns": {
      "position_id": "str",
      "quantity": "float",
      "cost_price": "float",
      "market_price": "float",
      "total_balance_usd": "float",
      "realized_gain_loss_usd": "float",
      "dividend_income_usd": "float",
      "fees_commissions_usd": "float"
    }
  },
  "cpf_helper": {
    "wkbid": "1x9Dfq5RVwvmCGqX9aIgCRoarkhLYR3mWGmRRvQnLkbo",
    "sheet": "worksheet",
    "data_columns": {
      "account_type": "str",
      "opening_balance_sgd": "float",
      "contributions_sgd": "float",
      "interest_sgd": "float",
      "withdrawals_sgd": "float",
      "closing_balance_sgd": "float"
    }
  }
}
```

### 2. home_budget_config.json

**Current Gap:** Not found in main project; exists in reference project only

**Required Content (inferred):**
```json
{
  "db_path": "path/to/homebudget.db",
  "db_status": "OK",
  "category_mapping": {
    "HomeBudget_Category": "Statement_Category",
    "Groceries": "Living Expenses > Groceries",
    "Salary": "Income > Employment > Salary",
    ...
  },
  "account_mapping": {
    "HomeBudget_Account": "Statement_Account",
    "Checking": "Bank Accounts",
    "IBKR": "Investments > Brokerage",
    ...
  }
}
```

### 3. statement_config.json

**Current Gap:** Not found in main project

**Required Content:**
```json
{
  "reporting_period": "YYYY-MM",
  "reporting_currency": "SGD",
  "reporting_entity": "Personal",
  "accounts": ["Wallets", "Bank", "IBKR", "CPF", "Credit Cards"],
  "start_date": "2024-01-01",
  "end_date": "2024-12-31"
}
```

---

## Integration Constraints

### Technical Constraints

1. **Google Sheets API Quota:** 300 requests/minute (batched reads acceptable)
2. **HomeBudget SQLite:** Concurrent writes not supported; application must close before script updates
3. **Windows-specific:** Bash scripts use PowerShell; cross-platform support deferred
4. **Python 3.12:** Required per environment.md; dependencies tested against 3.12.10

### Operational Constraints

1. **Manual data entry:** User updates helper workbooks; no automated statement ingestion (except forex)
2. **Monthly cadence:** Design assumes monthly close-out cycle; ad-hoc reporting not in MVP scope
3. **Single operator:** No multi-user coordination; role-based access not required
4. **Local execution:** Scripts run on user's machine; no cloud infrastructure in MVP

### Data Quality Constraints

1. **Account/category references:** HomeBudget CRUD will fail if references are invalid
2. **FX rate precision:** Yahoo Finance provides 4 decimal places; round to 2 for SGD amounts
3. **Date validation:** Transactions outside fiscal year range rejected
4. **Balance reconciliation:** Closing balance must equal Opening + Flows (tolerance: .01 SGD)

---

## Known Gaps and Ambiguities

### Schema Documentation Deferred

**IBKR Helper Workbook (`worksheet` sheet):**
- User indicated schema is too complex to document manually
- Schema inspection required: Execute `.dev/.scripts/python/inspect_helper_schemas.py`
- Output will document actual column names, data types, and sample data
- **Status:** On user's queue for inspection

**CPF Helper Workbook (`worksheet` sheet):**
- Schema inspection required: Execute `.dev/.scripts/python/inspect_helper_schemas.py`
- **Status:** On user's queue for inspection

**IBKR CSV Input Format:**
- User indicated format varies; inspection of sample statement required
- To be documented in Step 3 (Transformation Rules) after CSV samples provided

### Category Mapping Source Identified

**Workbook:** HomeBudget mapping workbook (`1xF_cmgyKw2NHV6uj-bwo2O1D-eiyJwihlhFJSpMEKPg`, sheet `cat_map`)

- Contains existing category-to-statement mappings
- Schema to be inspected via helper script
- Use this as authoritative mapping source in Python implementation

---

## References

- [Plan: Financial Statements Application Design](.github/prompts/plan-design.prompt.md)
- [docs/financial-statements-spec.md](financial-statements-spec.md)
- [docs/mvp-design.md](mvp-design.md)
- [docs/workflow.md](workflow.md)
- [docs/homebudget.md](homebudget.md)
- [docs/google-sheets.md](google-sheets.md)
- [reference/hb-finances/homebudget.py](../reference/hb-finances/homebudget.py)
- [reference/hb-finances/statements.py](../reference/hb-finances/statements.py)
- [reference/hb-finances/database.py](../reference/hb-finances/database.py)
- [gsheet/gsheet_config.json](../gsheet/gsheet_config.json)
- [.dev/.scripts/python/inspect_helper_schemas.py](.dev/.scripts/python/inspect_helper_schemas.py) — Helper tool to inspect schemas

---

**Document Status:** Complete (Step 2)  
**Next Review:** After user updates missing configurations; proceed to Step 3 (Data Transformation Rules)  
**Assigned To:** @taylorhickem  

**Action Items:**
- [ ] Run `.dev/.scripts/python/inspect_helper_schemas.py` to document IBKR/CPF/category mapping schemas
- [ ] Update `gsheet/gsheet_config.json` with IBKR and CPF helper workbook entries
- [ ] Create or import `home_budget_config.json` with category/account mapping
- [ ] Create `statement_config.json` with reporting parameters
- [ ] Create helper script: `fetch_forex_rates.py` for Yahoo Finance integration
