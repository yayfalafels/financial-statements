# Helper Workbooks Verification Checklist

**Document Version:** 0.2.0  
**Last Updated:** March 8, 2026  
**Status:** Design Proposal

## Table of Contents

1. [Overview](#overview)
2. [Pre-Import Validation](#pre-import-validation)
3. [Import Process Validation](#import-process-validation)
4. [Post-Import Data Quality Checks](#post-import-data-quality-checks)
5. [Cross-Workbook Reconciliation](#cross-workbook-reconciliation)
6. [Schema Drift Detection](#schema-drift-detection)
7. [Go/No-Go Criteria](#gono-go-criteria)

## Overview

This checklist defines repeatable verification checks for app-native monthly closing ETL processes. It ensures data integrity, schema consistency, and reconciliation accuracy before financial statements are generated.

Helper workbook checks are transitional and only used for migration parity/backfill.

### Checklist Usage

**Frequency:** Run for every monthly closing cycle (e.g., 2026-02, 2026-03)

**Execution Context:**

- **When:** Before adapter imports and after import completion
- **Who:** Automated ETL validation script + manual review where flagged
- **Where:** `financial_statements.db` validation queries + adapter-level source checks

**Failure Response:**

- **Critical errors:** Block import, log to `source_import_log` with status='error'
- **Warnings:** Log but allow import, flag for manual review
- **Info:** Log for audit trail

---

## Pre-Import Validation

### Runtime Modes

- `production_mode`: App-native adapters only (default)
- `parity_mode`: App-native adapters plus workbook comparison for migration validation
- `backfill_mode`: Controlled historical workbook ingestion only

### PV-01: Source Adapter Configuration Exists

**Check:** Verify adapter config exists for target source

```powershell
# Example for CPF adapter config
Test-Path "config/sources/cpf_adapter.json"
```

**Expected:** File exists with valid JSON structure

**Failure Action:** **Critical** - Cannot proceed without config

---

### PV-02: Source Adapter Accessible

**Check:** Verify source is accessible via adapter (file/API/portal capture)

```python
from src.python.ingest.adapters import build_adapter

adapter = build_adapter("cpf_adapter")
adapter.healthcheck()
# Should not raise connectivity/authentication errors
```

**Expected:** Adapter health check passes

**Failure Action:** **Critical** - Cannot access source data

---

### PV-03: Target Period Exists in `periods` Table

**Check:** Verify target period (e.g., '2026-02') exists in `periods` table

```sql
SELECT period_id, status FROM periods WHERE period_id = '2026-02';
```

**Expected:** One row returned with status IN ('active', 'closing', 'pending')

**Failure Action:** **Critical** - Create period record first

---

### PV-04: No Duplicate Import Session for Period

**Check:** Verify no existing successful import for this adapter+period combination

```sql
SELECT import_session_id, status, completed_at 
FROM source_import_log
WHERE source_adapter = 'cpf_adapter'
  AND period_id = '2026-02'
  AND status = 'success';
```

**Expected:** Zero rows (no prior successful import) OR user confirms re-import

**Failure Action:** **Warning** - Flag potential duplicate, require manual confirmation

---

### PV-05: Workbook Adapter Forbidden in Production Mode

**Check:** Verify workbook adapters are not used in `production_mode`

```python
assert runtime_mode != 'production_mode' or adapter.kind != 'gsheet', \
        'Workbook adapter is not allowed in production_mode'
```

**Expected:** No workbook adapter in production runs

**Failure Action:** **Critical** - Block run and require app-native adapter path

---

### PV-06: Parity/Backfill Requires Explicit Approval

**Check:** Verify explicit approval metadata for non-production modes

```python
if runtime_mode in {'parity_mode', 'backfill_mode'}:
        assert run_context.approved_by is not None
```

**Expected:** Approval metadata present for parity/backfill runs

**Failure Action:** **Critical** - Block run without approval

---

## Import Process Validation

### IP-01: Header Schema Validation

**Check:** Verify worksheet headers match expected schema profile

```python
# Example for cash-expenses recent_txns sheet
observed_headers = engine.fetch_sheet_data(
    sheet='recent_txns',
    range='A1:D1',  # Header row
    value_render='UNFORMATTED_VALUE'
)

expected_headers = ['date', 'budget', 'category', 'amount']

assert observed_headers == expected_headers, \
    f"Header drift detected: {observed_headers} != {expected_headers}"
```

**Expected:** Headers match schema profile exactly (case-sensitive)

**Failure Action:** **Critical** - Schema drift detected, review workbook changes

---

### IP-02: Data Type Validation

**Check:** Verify critical columns parse to expected types

```python
# Example for CPF matrix workbook
# Row 1 should be numeric (year: 2025, 2026, etc.)
year_row = engine.fetch_sheet_data(
    sheet='cpf_oa',
    range='B1:P1',
    value_render='UNFORMATTED_VALUE'
)

for cell in year_row[0]:
    assert isinstance(cell, int) and 2020 <= cell <= 2050, \
        f"Invalid year value: {cell}"
```

**Expected:** All values parse to schema-defined types

**Failure Action:** **Critical** - Type drift or data corruption

---

### IP-03: Range Boundary Validation

**Check:** Verify data range has expected row counts (detect truncation)

```python
# Example for category_mappings
rows = engine.fetch_sheet_data(
    sheet='cat_map',
    range='A2:J200',  # Expected ~181 data rows
    value_render='FORMATTED_VALUE'
)

row_count = len([r for r in rows if any(r)])  # Non-empty rows
assert 170 <= row_count <= 200, \
    f"Unexpected row count: {row_count} (expected 170-200)"
```

**Expected:** Row counts within expected range (±10% tolerance)

**Failure Action:** **Warning** - Possible data truncation or expansion

---

### IP-04: Account ID Referential Validation

**Check:** Verify all account IDs exist in canonical accounts list

```python
# Load canonical accounts from accounts.json
canonical_accounts = load_accounts_from_config()

# Example: Validate CPF account mapping
cpf_account_map = {
    'cpf_oa': 'TWH CPF OA SGD',
    'cpf_sa': 'TWH CPF SA SGD',
    'cpf_ma': 'TWH CPF MS SGD',  # Note: MS not MA in canonical
    'cpf_total': None  # Derived, not imported
}

for workbook_id, canonical_id in cpf_account_map.items():
    if canonical_id is not None:
        assert canonical_id in canonical_accounts, \
            f"Unmapped account: {canonical_id}"
```

**Expected:** All mapped account IDs exist in canonical list

**Failure Action:** **Critical** - Account mapping error

---

### IP-05: Period Continuity Check

**Check:** Verify periods are consecutive without gaps

```sql
-- Check for gaps in monthly sequence
WITH period_sequence AS (
    SELECT period_id,
           LAG(period_id) OVER (ORDER BY period_id) AS prev_period
    FROM periods
)
SELECT period_id, prev_period
FROM period_sequence
WHERE period_id != date(prev_period, '+1 month', 'start of month')
  AND prev_period IS NOT NULL;
```

**Expected:** Zero rows (no gaps in monthly sequence)

**Failure Action:** **Warning** - Period sequence gap detected

---

## Post-Import Data Quality Checks

### DQ-01: No Null Values in Non-Nullable Fields

**Check:** Verify required fields have no null values

```sql
-- Example for asset_balances
SELECT period_id, account_id, metric_name
FROM asset_balances
WHERE period_id IS NULL
   OR account_id IS NULL
   OR metric_name IS NULL
   OR currency IS NULL
   OR source IS NULL;
```

**Expected:** Zero rows

**Failure Action:** **Critical** - Data integrity violation

---

### DQ-02: Currency Field Validation

**Check:** Verify all currency values are valid ISO codes

```sql
SELECT DISTINCT currency
FROM asset_balances
WHERE currency NOT IN ('SGD', 'USD', 'EUR', 'GBP');
```

**Expected:** Zero rows (all currencies are valid codes)

**Failure Action:** **Critical** - Invalid currency code

---

### DQ-03: Date Range Validation

**Check:** Verify transaction dates fall within expected period

```sql
-- Example for cash_transactions
SELECT id, transaction_date, period_id
FROM cash_transactions
WHERE substr(transaction_date, 1, 7) != period_id;
```

**Expected:** Zero rows (transaction dates align with period_id)

**Failure Action:** **Critical** - Period assignment mismatch

---

### DQ-04: Numeric Range Validation

**Check:** Verify amounts fall within reasonable bounds

```sql
-- Detect outlier balances (e.g., > $1M for CPF accounts)
SELECT period_id, account_id, metric_name, amount
FROM asset_balances
WHERE account_id LIKE '%CPF%'
  AND metric_name = 'END BAL'
  AND amount > 1000000;
```

**Expected:** Zero rows OR manual review confirms legitimacy

**Failure Action:** **Warning** - Outlier detected, review required

---

### DQ-05: Import Record Count Validation

**Check:** Verify expected number of records imported

```sql
-- Example: CPF should have ~35 records per period (5 sections × 7 metrics)
SELECT period_id, COUNT(*) AS record_count
FROM asset_balances
WHERE source = 'gsheet_cpf'
  AND period_id = '2026-02'
GROUP BY period_id
HAVING COUNT(*) < 30 OR COUNT(*) > 50;
```

**Expected:** Record counts within expected range

**Failure Action:** **Warning** - Unexpected record volume

---

## Cross-Source Reconciliation

### XW-01: CPF Account Reconciliation

**Check:** Verify CPF-Total = sum(CPF-OA, CPF-SA, CPF-MA)

```sql
WITH cpf_balances AS (
    SELECT 
        period_id,
        SUM(CASE WHEN metric_section = 'cpf_oa' AND metric_name = 'END BAL' THEN amount ELSE 0 END) AS oa_bal,
        SUM(CASE WHEN metric_section = 'cpf_sa' AND metric_name = 'END BAL' THEN amount ELSE 0 END) AS sa_bal,
        SUM(CASE WHEN metric_section = 'cpf_ma' AND metric_name = 'END BAL' THEN amount ELSE 0 END) AS ma_bal,
        SUM(CASE WHEN metric_section = 'cpf_total' AND metric_name = 'END BAL' THEN amount ELSE 0 END) AS total_bal
    FROM asset_balances
    WHERE source = 'gsheet_cpf'
      AND period_id = '2026-02'
)
SELECT 
    period_id,
    oa_bal + sa_bal + ma_bal AS computed_total,
    total_bal AS reported_total,
    ABS((oa_bal + sa_bal + ma_bal) - total_bal) AS variance
FROM cpf_balances
WHERE ABS((oa_bal + sa_bal + ma_bal) - total_bal) > 0.01;
```

**Expected:** Zero rows (computed total matches reported total ±$0.01)

**Failure Action:** **Critical** - CPF reconciliation failure

---

### XW-02: IBKR NAV Currency Reconciliation

**Check:** Verify NAV SGD ≈ NAV USD × FX rate

```sql
WITH ibkr_nav AS (
    SELECT 
        ab.period_id,
        MAX(CASE WHEN ab.currency = 'USD' AND ab.metric_name LIKE '%NAV%' THEN ab.amount END) AS nav_usd,
        MAX(CASE WHEN ab.currency = 'SGD' AND ab.metric_name LIKE '%NAV%' THEN ab.amount END) AS nav_sgd,
        er.rate AS fx_rate
    FROM asset_balances ab
    LEFT JOIN exchange_rates er 
        ON er.date = ab.period_id || '-01'
        AND er.currency_from = 'USD'
        AND er.currency_to = 'SGD'
    WHERE ab.source = 'gsheet_ibkr'
      AND ab.period_id = '2026-02'
    GROUP BY ab.period_id, er.rate
)
SELECT 
    period_id,
    nav_usd,
    nav_sgd,
    fx_rate,
    nav_usd * fx_rate AS computed_nav_sgd,
    ABS(nav_sgd - (nav_usd * fx_rate)) AS variance
FROM ibkr_nav
WHERE ABS(nav_sgd - (nav_usd * fx_rate)) / NULLIF(nav_sgd, 0) > 0.01;  -- >1% variance
```

**Expected:** Zero rows (NAV SGD within 1% of NAV USD × FX)

**Failure Action:** **Critical** - IBKR currency reconciliation failure

---

### XW-03: Balance Continuity Check

**Check:** Verify current period opening balance = prior period closing balance

```sql
WITH balance_continuity AS (
    SELECT 
        curr.period_id AS current_period,
        curr.account_id,
        curr.metric_name,
        prev.amount AS prev_closing,
        curr.amount AS curr_opening
    FROM asset_balances curr
    JOIN asset_balances prev
        ON prev.period_id = date(curr.period_id || '-01', '-1 month', 'start of month')
        AND prev.account_id = curr.account_id
        AND prev.metric_name = 'END BAL'
    WHERE curr.metric_name = 'BEG BAL'
      AND curr.period_id = '2026-02'
)
SELECT *
FROM balance_continuity
WHERE ABS(prev_closing - curr_opening) > 0.01;
```

**Expected:** Zero rows (opening = prior closing ±$0.01)

**Failure Action:** **Critical** - Balance continuity broken

---

### XW-04: Exchange Rate Completeness

**Check:** Verify all required currency pairs exist for target period

```sql
SELECT '2026-02' AS period_id, 'USD' AS currency_from, 'SGD' AS currency_to
WHERE NOT EXISTS (
    SELECT 1 FROM exchange_rates
    WHERE date = '2026-02-01'
      AND currency_from = 'USD'
      AND currency_to = 'SGD'
);
```

**Expected:** Zero rows (all required FX rates exist)

**Failure Action:** **Critical** - Missing exchange rate

---

## Schema Drift Detection

Workbook schema drift checks are parity-only controls and are not required for normal production runs.

### SD-01: Column Count Validation

**Check:** Verify worksheet column counts match baseline profile

```python
# Example for CPF workbook matrix sheets
# Expected: 16 columns (A = metric name, B-P = 15 months)

observed_cols = len(engine.fetch_sheet_data(
    sheet='cpf_oa',
    range='1:1',
    value_render='UNFORMATTED_VALUE'
)[0])

expected_cols = 16

assert observed_cols == expected_cols, \
    f"Column count drift: {observed_cols} != {expected_cols}"
```

**Expected:** Column counts match baseline

**Failure Action:** **Critical** - Schema structure changed

---

### SD-02: Row Count Drift Detection

**Check:** Detect significant row count changes (±20% from baseline)

```python
# Example for category_mappings
baseline_rows = 181  # From schema profile
observed_rows = count_non_empty_rows(engine, 'cat_map', 'A2:A200')

drift_pct = abs(observed_rows - baseline_rows) / baseline_rows

assert drift_pct <= 0.20, \
    f"Row count drift: {drift_pct*100:.1f}% (observed: {observed_rows}, baseline: {baseline_rows})"
```

**Expected:** Row counts within ±20% of baseline

**Failure Action:** **Warning** - Significant row count change

---

### SD-03: New Metric Detection

**Check:** Detect new metric names not in baseline profile

```sql
-- Example for asset_balances
SELECT DISTINCT metric_name
FROM asset_balances
WHERE source = 'gsheet_cpf'
  AND period_id = '2026-02'
  AND metric_name NOT IN ('BEG BAL', 'END BAL', 'CONTRIBUTIONS', 'WITHDRAWALS', 'INTEREST');
```

**Expected:** Zero rows (all metrics are known)

**Failure Action:** **Warning** - New metric detected, review parser

---

### SD-04: Section Name Drift

**Check:** Verify section names in matrix workbooks remain stable

```python
# Profile CPF sections from row headers
observed_sections = engine.fetch_sheet_data(
    sheet='cpf_oa',
    range='A4:A10',  # Example: metric names in section
    value_render='FORMATTED_VALUE'
)

baseline_sections = ['BEG BAL', 'CONTRIBUTIONS', 'WITHDRAWALS', 'INTEREST', 'END BAL']

# Check for unexpected section headers
new_sections = set(observed_sections) - set(baseline_sections)
assert len(new_sections) == 0, \
    f"New section headers detected: {new_sections}"
```

**Expected:** Section headers match baseline

**Failure Action:** **Warning** - Section structure changed

---

## Go/No-Go Criteria

### ETL Import Go/No-Go Decision Matrix

| Check Result | Go | No-Go | Action |
|--------------|----|----|--------|
| All Critical checks pass | ✓ | | Proceed with import |
| Workbook adapter used in production mode | | ✓ | Block run; enforce app-native adapter |
| 1+ Critical check fails | | ✓ | Block import, investigate |
| All Critical pass, some Warnings | ✓ | | Log warnings, manual review |
| Schema drift detected | | ✓ | Update schema profiles, review parser |
| Reconciliation variance >1% | | ✓ | Investigate source data |

### Monthly Closing Go/No-Go Decision Matrix

| Check Result | Go | No-Go | Action |
|--------------|----|----|--------|
| All imports successful | ✓ | | Proceed to financial statements |
| CPF reconciliation failure | | ✓ | Review CPF source inputs and adapter output |
| IBKR reconciliation failure | | ✓ | Review IBKR source inputs and adapter output |
| Balance continuity broken | | ✓ | Review prior period corrections |
| Missing exchange rates | | ✓ | Refresh FX adapter/source inputs |
| >5% data volume variance | | ✓ | Investigate record count changes |

---

## Verification Script Template

### Python Implementation Outline

```python
# monthly_closing_verification.py

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

class CheckSeverity(Enum):
    CRITICAL = 'critical'
    WARNING = 'warning'
    INFO = 'info'

@dataclass
class CheckResult:
    check_id: str
    check_name: str
    severity: CheckSeverity
    passed: bool
    message: str
    details: Optional[dict] = None

class SourceVerifier:
    def __init__(self, db_path: str, config_dir: str):
        self.db_path = db_path
        self.config_dir = config_dir
        self.results: List[CheckResult] = []
    
    def run_pre_import_checks(self, workbook_config: str, period_id: str):
        """Run PV-01 through PV-04"""
        self.results.append(self.check_config_exists(workbook_config))
        self.results.append(self.check_workbook_accessible(workbook_config))
        self.results.append(self.check_period_exists(period_id))
        self.results.append(self.check_no_duplicate_import(workbook_config, period_id))
    
    def run_import_checks(self, workbook_config: str, period_id: str):
        """Run IP-01 through IP-05"""
        self.results.append(self.validate_headers(workbook_config))
        self.results.append(self.validate_data_types(workbook_config))
        self.results.append(self.validate_range_boundaries(workbook_config))
        self.results.append(self.validate_account_ids(workbook_config))
        self.results.append(self.check_period_continuity(period_id))
    
    def run_data_quality_checks(self, period_id: str):
        """Run DQ-01 through DQ-05"""
        self.results.append(self.check_no_nulls())
        self.results.append(self.validate_currencies())
        self.results.append(self.validate_date_ranges(period_id))
        self.results.append(self.validate_numeric_ranges())
        self.results.append(self.validate_record_counts(period_id))
    
    def run_reconciliation_checks(self, period_id: str):
        """Run XW-01 through XW-04"""
        self.results.append(self.reconcile_cpf(period_id))
        self.results.append(self.reconcile_ibkr_nav(period_id))
        self.results.append(self.check_balance_continuity(period_id))
        self.results.append(self.check_exchange_rate_completeness(period_id))
    
    def run_schema_drift_checks(self, workbook_config: str):
        """Run SD-01 through SD-04"""
        self.results.append(self.check_column_counts(workbook_config))
        self.results.append(self.check_row_count_drift(workbook_config))
        self.results.append(self.detect_new_metrics(workbook_config))
        self.results.append(self.check_section_names(workbook_config))
    
    def evaluate_go_nogo(self) -> bool:
        """Evaluate go/no-go decision"""
        critical_failures = [r for r in self.results 
                           if not r.passed and r.severity == CheckSeverity.CRITICAL]
        return len(critical_failures) == 0
    
    def generate_report(self) -> str:
        """Generate verification report"""
        # Format results as markdown table
        pass

# Usage
verifier = SourceVerifier('financial_statements.db', 'config/sources/')
verifier.run_pre_import_checks('cpf_adapter', '2026-02')

if verifier.evaluate_go_nogo():
    # Proceed with import
    pass
else:
    # Block import, log failures
    print(verifier.generate_report())
```

---

## Continuous Improvement

### Checklist Maintenance

- **Quarterly Review:** Review checklist effectiveness, add checks for newly discovered issues
- **Baseline Updates:** Update row count baselines, metric lists when workbooks evolve
- **Automation Expansion:** Incrementally automate manual review steps

### Audit Trail

- Log all verification results to `source_import_log` table
- Track check execution times, failure rates over time
- Generate monthly verification summary reports