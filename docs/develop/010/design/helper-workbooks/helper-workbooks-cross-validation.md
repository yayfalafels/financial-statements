# Helper Workbooks Cross-Validation Report

**Document Version:** 0.2.0  
**Last Updated:** March 8, 2026  
**Status:** Complete

## Table of Contents

1. [Overview](#overview)
2. [Account ID Contract Validation](#account-id-contract-validation)
3. [Period Format Validation](#period-format-validation)
4. [Currency Contract Validation](#currency-contract-validation)
5. [Data Type Consistency](#data-type-consistency)
6. [Schema Drift Risks](#schema-drift-risks)
7. [Cross-Workbook Reconciliation Rules](#cross-workbook-reconciliation-rules)
8. [Resolution Decisions](#resolution-decisions)

## Overview

This document validates contracts and conventions discovered from helper workbooks to ensure consistent integration into `financial_statements.db`.

Target-state policy: helper workbooks are reference artifacts only. The monthly-closing workflow is app-native and does not depend on workbook reads in production mode.

## Account ID Contract Validation

### Canonical Account List

**Source of Truth:** App-managed canonical account registry, initially seeded from `gsheet/financial-statements.json` `accounts` sheet during migration

**Observed Accounts (sample from live data):**
```
TWH CASH SGD
TWH CASH USD
TWH AMAZON USD
TWH EZLINK SGD
COM UOB SGD
TWH DBS MULTI SGD
TWH CITI USD
TWH WF USD
TWH BOA VISA USD
TWH DBS VISA SGD
WPC POSITION SGD
TWH IB CASH USD
TWH LC CASH USD
TWH CDP SGD
TWH IB POSITION USD
... (27 total accounts)
```

### Account ID Usage Across Workbooks

| Workbook             |              |                              |                           |
| -------------------- | ------------ | ---------------------------- | ------------------------- |
| Sheet                |              |                              |                           |
| Account ID Used      |              |                              |                           |
| Match Status         |              |                              |                           |
| Notes                |              |                              |                           |
| financial-statements | balances     | TWH CASH SGD, etc.           | âœ“ Canonical             |
| cpf                  | cpf_total    | CPF-Total (implicit)         | âš  Not in canonical list |
| cpf                  | cpf_oa       | CPF-OA (implicit)            | âš  Not in canonical list |
| cpf                  | cpf_sa       | CPF-SA (implicit)            | âš  Not in canonical list |
| cpf                  | cpf_ma       | CPF-MA (implicit)            | âš  Not in canonical list |
| ibkr-iba             | All sections | IBKR-IBA (implicit)          | âš  Not in canonical list |
| cash-expenses        | recent_txns  | "Cash" (implicit)            | âš  Not in canonical list |
| shared-expenses      | records      | (no explicit account)        | âŒ Missing               |
| homebudget-workbook  | cat_map      | Multiple in "account" column | âœ“ Appears to match      |

| Workbook             |              |                                                   |
| -------------------- | ------------ | ------------------------------------------------- |
| Sheet                |              |                                                   |
| Account ID Used      |              |                                                   |
| Match Status         |              |                                                   |
| Notes                |              |                                                   |
| financial-statements | balances     | Legacy seed source for canonical registry         |
| cpf                  | cpf_total    | Need to add CPF accounts                          |
| cpf                  | cpf_oa       | Need to add                                       |
| cpf                  | cpf_sa       | Need to add                                       |
| cpf                  | cpf_ma       | Need to add                                       |
| ibkr-iba             | All sections | Need to add or map to "TWH IB POSITION USD"       |
| cash-expenses        | recent_txns  | Need to map to "TWH CASH SGD" or separate account |
| shared-expenses      | records      | Need to define account for shared expenses        |
| homebudget-workbook  | cat_map      | Maps to canonical accounts                        |

### Missing Canonical Account IDs

**Required Additions to `accounts` sheet:**

**Validation Action:** âœ“ **RESOLVED**

Inspected full canonical accounts sheet. CPF and IBKR accounts exist:

- TWH CPF OA SGD (retirement)
- TWH CPF SA SGD (retirement)
- TWH CPF MS SGD (savings account) - note: "MS" in ID, "MA" in HB account name
- TWH IB POSITION USD (investment)
- TWH IB CASH USD (savings account)
- TWH IB IRA USD (retirement)

**Account ID Mapping:**

```python
CPF_ACCOUNT_MAP = {
    'cpf_oa': 'TWH CPF OA SGD',
    'cpf_sa': 'TWH CPF SA SGD',
    'cpf_ma': 'TWH CPF MS SGD',  # Note: MS in canonical ID, MA in workbook
    'cpf_total': None,  # Derived metric = sum(OA, SA, MA)
    'cpf_summary': None  # Summary metrics, not a separate account
}

IBKR_ACCOUNT_MAP = {
    'ib_net_liquidity_nav': 'TWH IB POSITION USD',  # NAV reflects total value
    'ib_net_liquidity_cash': 'TWH IB CASH USD',     # Cash component
    'ib_cash': 'TWH IB CASH USD',
    'ib_securities': 'TWH IB POSITION USD',
    'ib_summary': 'TWH IB POSITION USD',
    'ib_ira': 'TWH IB IRA USD'  # If IRA tracked separately
}
```

**See:** [cpf-domain-model.md](../cpf-domain-model.md) and [ibkr-domain-model.md](../ibkr-domain-model.md) for detailed domain logic.

### Account Naming Convention

**Observed Pattern:**

- Format: `{OWNER} {INSTITUTION} {CURRENCY}` (e.g., "TWH CASH SGD")
- Or: `{OWNER} {INSTITUTION} {TYPE} {CURRENCY}` (e.g., "TWH IB POSITION USD")

**CPF Convention:**

- Proposed: `{OWNER} CPF {SUB_ACCOUNT}` â†’ "TWH CPF OA", "TWH CPF SA", "TWH CPF MA"
- Or simpler: "CPF-OA", "CPF-SA", "CPF-MA"

**IBKR Convention:**

- Proposed: Map "IBKR-IBA" â†’ "TWH IB POSITION USD" (positions) and "TWH IB CASH USD" (cash)
- Or keep separate: "IBKR-IBA" as consolidated account

**Decision:** âœ“ **RESOLVED** - Retain existing canonical convention from the accounts registry and map workbook shorthand IDs during migration/parity only.

---

## Period Format Validation

### Period Formats Observed

| Workbook             |              |                           |                             |
| -------------------- | ------------ | ------------------------- | --------------------------- |
| Sheet                |              |                           |                             |
| Period Format        |              |                           |                             |
| Example              |              |                           |                             |
| Parse Rule           |              |                           |                             |
| financial-statements | balances     | (year: int, month: int)   | year=2026, month=2          |
| financial-statements | forex_rates  | date (YYYY-MM-DD)         | "2026-02-01"                |
| cpf                  | All sections | Row 1: year, Row 2: month | Row1[col]=2026, Row2[col]=2 |
| ibkr-iba             | All sections | Row 1: year, Row 2: month | Row1[col]=2026, Row2[col]=2 |
| cash-expenses        | recent_txns  | DD/MM/YYYY HH:MM:SS       | "24/01/2026 22:51:46"       |
| shared-expenses      | records      | YYYY-MM-DD                | "2021-10-01"                |

| Workbook             |              |                              |
| -------------------- | ------------ | ---------------------------- |
| Sheet                |              |                              |
| Period Format        |              |                              |
| Example              |              |                              |
| Parse Rule           |              |                              |
| financial-statements | balances     | Composite â†’ "2026-02"      |
| financial-statements | forex_rates  | Extract â†’ "2026-02"        |
| cpf                  | All sections | Composite â†’ "2026-02"      |
| ibkr-iba             | All sections | Composite â†’ "2026-02"      |
| cash-expenses        | recent_txns  | Parse datetime â†’ "2026-01" |
| shared-expenses      | records      | Parse date â†’ "2021-10"     |

### Canonical Period ID Format

**Proposed Standard:** `YYYY-MM` (string)

**Conversion Rules:**

```python
def to_period_id(source, value):
    if source == "balances":
        # (year, month) tuple
        year, month = value
        return f"{year:04d}-{month:02d}"
    
    elif source == "forex_rates":
        # date string "YYYY-MM-DD"
        date_obj = datetime.strptime(value, "%Y-%m-%d")
        return f"{date_obj.year:04d}-{date_obj.month:02d}"
    
    elif source in ["cpf", "ibkr-iba"]:
        # (year_from_row1, month_from_row2) tuple
        year, month = value
        return f"{year:04d}-{month:02d}"
    
    elif source == "cash_expenses":
        # "DD/MM/YYYY HH:MM:SS"
        date_obj = datetime.strptime(value, "%d/%m/%Y %H:%M:%S")
        return f"{date_obj.year:04d}-{date_obj.month:02d}"
    
    elif source == "shared_expenses":
        # "YYYY-MM-DD"
        date_obj = datetime.strptime(value, "%Y-%m-%d")
        return f"{date_obj.year:04d}-{date_obj.month:02d}"
```

**Validation:** âœ“ All formats can be converted to canonical `YYYY-MM`.

**Consistency Check:** Ensure all dates within a period fall in the same month.

---

## Currency Contract Validation

### Currency Formats Observed

| Workbook                |              |                    |                      |                   |
| ----------------------- | ------------ | ------------------ | -------------------- | ----------------- |
| Sheet                   |              |                    |                      |                   |
| Currency Representation |              |                    |                      |                   |
| Example                 |              |                    |                      |                   |
| Notes                   |              |                    |                      |                   |
| financial-statements    | balances     | Implicit SGD       | balance=513.90       | Assumed SGD       |
| financial-statements    | forex_rates  | Explicit in column | currency="USD"       | ISO code          |
| financial-statements    | accounts     | Explicit in column | currency="SGD"/"USD" | ISO code          |
| cpf                     | All sections | Implicit SGD       | amount=65000         | CPF is always SGD |
| ibkr-iba                | All sections | In metric name     | "NAV USD", "NAV SGD" | Parse from label  |
| cash-expenses           | recent_txns  | Implicit SGD       | amount=19.8          | Assumed SGD       |
| shared-expenses         | records      | Implicit SGD       | total_price=59.87    | Assumed SGD       |

### Currency Detection Rules

```python
def detect_currency(source, metric_name=None, account_id=None):
    # Explicit currency from account
    if account_id:
        # Query accounts sheet for currency
        account_currency = get_account_currency(account_id)
        if account_currency:
            return account_currency
    
    # Parse from metric name (IBKR)
    if metric_name:
        if "USD" in metric_name.upper():
            return "USD"
        elif "SGD" in metric_name.upper():
            return "SGD"
    
    # Source-specific defaults
    if source in ["cpf", "cash_expenses", "shared_expenses"]:
        return "SGD"  # Singapore-based accounts default to SGD
    
    if source == "ibkr-iba":
        return "USD"  # IBKR default base currency
    
    # Global default
    return "SGD"
```

**Validation:** âœ“ All sources have defined currency detection logic.

**Consistency:** Amounts should always be stored with explicit currency in database.

---

## Data Type Consistency

### Type Mapping Across Sources

| Field Type     |                          |                                                         |
| -------------- | ------------------------ | ------------------------------------------------------- |
| Declared Types |                          |                                                         |
| Observed Types |                          |                                                         |
| Coercion Rule  |                          |                                                         |
| Null Handling  |                          |                                                         |
| Period/Date    | int, date, datetime      | year+month int, YYYY-MM-DD str, DD/MM/YYYY HH:MM:SS str |
| Amount/Balance | float, str (with commas) | float, str like "132,847.06"                            |
| Account ID     | str                      | str (uppercase)                                         |
| Category       | str                      | str                                                     |
| Metric Name    | str                      | str                                                     |
| Currency       | str (3-letter ISO)       | str or implicit                                         |

| Field Type     |                          |                                |                             |
| -------------- | ------------------------ | ------------------------------ | --------------------------- |
| Declared Types |                          |                                |                             |
| Observed Types |                          |                                |                             |
| Coercion Rule  |                          |                                |                             |
| Null Handling  |                          |                                |                             |
| Period/Date    | int, date, datetime      | Parse to canonical YYYY-MM str | NOT NULL                    |
| Amount/Balance | float, str (with commas) | Remove commas, cast to float   | Nullable (empty cells)      |
| Account ID     | str                      | DIRECT, uppercase              | NOT NULL                    |
| Category       | str                      | DIRECT                         | Nullable                    |
| Metric Name    | str                      | DIRECT, trim whitespace        | NOT NULL (for matrix rows)  |
| Currency       | str (3-letter ISO)       | ISO code validation            | NOT NULL (default or parse) |

### Type Coercion Issues

**Issue 1: Comma-Separated Numbers**

CPF and IBKR workbooks use comma-formatted numbers:

- `"132,847.06"` â†’ `132847.06` (float)
- `"3,884.02"` â†’ `3884.02` (float)

**Resolution:** Remove commas before float conversion.

```python
def parse_numeric(value):
    if isinstance(value, str):
        value = value.replace(',', '').strip()
    if value == '' or value is None:
        return None
    return float(value)
```

**Issue 2: Empty Strings vs None**

Google Sheets API may return empty strings `""` or skip values entirely.

**Resolution:** Treat `""`, `None`, and whitespace-only strings as NULL.

```python
def is_empty(value):
    return value is None or str(value).strip() == ''
```

**Issue 3: Date Format Variety**

Multiple date formats across workbooks.

**Resolution:** Define format per source, parse accordingly with error handling.

**Validation:** âœ“ Type coercion rules defined for all field types.

---

## Schema Drift Risks

### High-Risk Drift Scenarios

| Workbook      |                         |                               |                            |
| ------------- | ----------------------- | ----------------------------- | -------------------------- |
| Risk          |                         |                               |                            |
| Impact        |                         |                               |                            |
| Detection     |                         |                               |                            |
| Mitigation    |                         |                               |                            |
| cpf, ibkr-iba | New month column added  | Column P shifts to Q          | Column count check         |
| All           | Header row text changes | Parser fails                  | Header validation          |
| All           | New account added       | Account not in canonical list | FK constraint violation    |
| cpf, ibkr-iba | New metric row inserted | Row indices shift             | Section boundary detection |
| forex_rates   | Currency pair added     | New rows                      | â€”                        |
| cash-expenses | Sheet restructured      | Parser fails                  | Column count change        |

| Workbook      |                         |                                             |
| ------------- | ----------------------- | ------------------------------------------- |
| Risk          |                         |                                             |
| Impact        |                         |                                             |
| Detection     |                         |                                             |
| Mitigation    |                         |                                             |
| cpf, ibkr-iba | New month column added  | Dynamic column range detection              |
| All           | Header row text changes | Fuzzy match or position-based parsing       |
| All           | New account added       | Pre-flight account validation               |
| cpf, ibkr-iba | New metric row inserted | Use section title as anchor, not row number |
| forex_rates   | Currency pair added     | Flexible (no issue)                         |
| cash-expenses | Sheet restructured      | Schema version check before parse           |

### Drift Detection Strategy

**Pre-Flight Checks Before Each ETL Run:**

1. **Header Validation:**
   ```python
   def validate_headers(workbook, sheet, expected_headers):
       actual_headers = fetch_headers(workbook, sheet)
       if actual_headers != expected_headers:
           # Fuzzy match or warn
           log_warning(f"Header drift detected: expected {expected_headers}, got {actual_headers}")
           # Decide: fail or proceed with warning
   ```

2. **Column Count Check:**
   ```python
   def validate_column_count(workbook, sheet, expected_count, tolerance=0):
       actual_count = get_column_count(workbook, sheet)
       if abs(actual_count - expected_count) > tolerance:
           raise SchemaError(f"Column count mismatch: expected {expected_count}, got {actual_count}")
   ```

3. **Row Boundary Validation:**
   For matrix workbooks, validate section titles:
   ```python
   def validate_section_title(workbook, sheet, row, expected_title):
       actual_title = fetch_cell(workbook, sheet, row, col='A')
       if actual_title.strip().upper() != expected_title.strip().upper():
           raise SchemaError(f"Section title mismatch at row {row}")
   ```

4. **Account Existence Check:**
   ```python
   def validate_account_exists(account_id, canonical_accounts):
       if account_id not in canonical_accounts:
           log_error(f"Unknown account ID: {account_id}")
           # Optionally raise or mark for review
   ```

**Validation:** âš  Drift detection must be implemented before production ETL.

---

## Cross-Workbook Reconciliation Rules

### Reconciliation Checkpoints

**Checkpoint 1: CPF Account Balance Summation**

Rule:
```
CPF-Total Closing Balance = CPF-OA Closing + CPF-SA Closing + CPF-MA Closing
```

Validation:
```python
def validate_cpf_totals(period_id, cpf_balances):
    oa = cpf_balances.get(('CPF-OA', period_id, 'END BAL'))
    sa = cpf_balances.get(('CPF-SA', period_id, 'END BAL'))
    ma = cpf_balances.get(('CPF-MA', period_id, 'END BAL'))
    total = cpf_balances.get(('CPF-Total', period_id, 'END BAL'))
    
    computed_total = (oa or 0) + (sa or 0) + (ma or 0)
    
    if abs(computed_total - (total or 0)) > 0.01:  # Tolerance for rounding
        raise ReconciliationError(f"CPF total mismatch for {period_id}: {computed_total} != {total}")
```

**Checkpoint 2: IBKR NAV Currency Conversion**

Rule:
```
NAV SGD â‰ˆ NAV USD Ã— forex_rate (within tolerance)
```

Validation:
```python
def validate_ibkr_nav_crosscheck(period_id, ibkr_balances, forex_rates):
    nav_usd = ibkr_balances.get(('IBKR-IBA', period_id, 'NAV USD'))
    nav_sgd = ibkr_balances.get(('IBKR-IBA', period_id, 'NAV SGD'))
    fx_rate = forex_rates.get((period_id, 'USD', 'SGD'))
    
    if nav_usd and nav_sgd and fx_rate:
        computed_sgd = nav_usd * fx_rate
        if abs(computed_sgd - nav_sgd) / nav_sgd > 0.01:  # 1% tolerance
            log_warning(f"IBKR NAV crosscheck variance for {period_id}: {computed_sgd} vs {nav_sgd}")
```

**Checkpoint 3: Balance Continuity**

Rule:
```
Opening Balance [month M] = Closing Balance [month M-1]
```

Validation:
```python
def validate_balance_continuity(account_id, period_id, current_opening, prior_closing):
    if abs(current_opening - prior_closing) > 0.01:
        log_warning(f"Balance continuity break for {account_id} at {period_id}")
```

**Checkpoint 4: Category Mapping Completeness**

Rule: All categories in `cash_transactions` and `shared_expense_transactions` must exist in `cat_map`.

Validation:
```python
def validate_category_mapping(category, cat_map):
    if category not in cat_map:
        log_error(f"Unmapped category: {category}")
```

---

## Resolution Decisions

### Decision Log

**Decision 1: Canonical Account IDs for CPF and IBKR**

**Issue:** CPF and IBKR workbooks use implicit account IDs (CPF-OA, IBKR-IBA) that differ from canonical naming.

**Decision:** âœ“ **RESOLVED** - Map workbook account IDs to existing canonical accounts:

- CPF-OA â†’ TWH CPF OA SGD
- CPF-SA â†’ TWH CPF SA SGD  
- CPF-MA â†’ TWH CPF MS SGD
- CPF-Total â†’ Derived sum (no separate account)
- IBKR-IBA â†’ TWH IB POSITION USD (NAV) + TWH IB CASH USD (Cash component)
- IBKR-IRA â†’ TWH IB IRA USD

**Rationale:** Canonical accounts already exist with appropriate naming convention. Workbook IDs are shorthand that map to full canonical IDs.

---

**Decision 2: Period ID Canonical Format**

**Issue:** Multiple period representations across workbooks.

**Options:**

1. Use `YYYY-MM` (string)
2. Use composite `(year, month)` (int tuple)
3. Use `YYYYMM` (int)

**Decision:** âœ“ **RESOLVED** - Use `YYYY-MM` (string) for consistency with industry standards and SQL date functions.

---

**Decision 3: Matrix Column Expansion Strategy**

**Issue:** Legacy CPF/IBKR workbook matrixes may add month columns over time.

**Options:**

1. Hardcode column range A:P (15 months)
2. Dynamically detect last non-empty column
3. Use config to specify current column range

**Decision:** âœ“ **RESOLVED** - Dynamic detection with sanity limit (max 24 month columns) for parity/backfill mode.

**Recommendation:** Dynamic detection with sanity check (e.g., max 24 columns for rolling 2-year view).

---

**Decision 4: Empty Cell Handling in Matrix**

**Issue:** Matrix workbooks have empty cells for future months.

**Options:**

1. Skip empty cells (do not insert records)
2. Insert records with NULL amounts
3. Fail on empty cells

**Decision:** âœ“ **RESOLVED** - Skip empty cells (do not create records for missing data).

---

**Decision 5: Shared Expenses Account Assignment**

**Issue:** Shared expenses workbook has no explicit account ID.

**Options:**

1. Create "Shared Expenses" account
2. Split expenses across participant accounts
3. Use "Common UOB" or shared household account

**Decision:** âœ“ **RESOLVED** - Use configured app account mapping (`shared_expense_default_account_id`) with validation against canonical accounts.

**Recommendation:** Review actual usage pattern - if expenses are ultimately paid from a specific account, use that account ID. Otherwise, create "Shared Expenses" as a virtual account.

---

## Summary of Validation Results

### âœ“ Validated

- Period formats are convertible to canonical `YYYY-MM`
- Currency detection rules cover all sources
- Type coercion rules defined for all field types
- Reconciliation rules defined for CPF totals and IBKR currency crosscheck

### âš  Requires Implementation

- Enforce production-mode prohibition on workbook adapters
- Implement adapter-level schema drift checks and parity-mode workbook checks
- Implement reconciliation automation in monthly closing runtime

### âŒ Blocked

- None

---

## Next Steps

1. **Implement App-Native Adapters** (source ingestion without helper workbooks)
2. **Enable Parity Mode** (temporary workbook comparison for migration confidence)
3. **Cut Over to Production Mode** (workbook-free monthly close)
4. **Deprecate Workbook ETL Paths** (retain docs only)
5. **Document Exception Handling** (what to do when validation fails)

---

## Deprecation Decision

- Helper workbooks are deprecated from the operational monthly-closing workflow.
- Production runs must source data from app adapters and app-managed schemas.
- Workbook access is limited to parity/backfill workflows with explicit approval.
