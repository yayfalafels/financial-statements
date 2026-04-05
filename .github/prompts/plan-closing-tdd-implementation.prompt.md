---
name: plan-closing-tdd-implementation
title: Closing Automation TDD Implementation Plan
description: Complete TDD implementation plan for the consolidated monthly closing workflow, following design documentation â†’ test cases (SIT/UAT) â†’ build â†’ validate pattern for each feature. Hybrid workflow with AI prompts and user inputs.
status: active
version: 1.0
created_date: 2026-02-28
author: GitHub Copilot
keywords:
  - closing-workflow
  - tdd
  - implementation-plan
  - financial-statements
  - shared-utilities
  - phased-delivery
phase: Implementation Planning
deliverable: Phase-by-phase TDD implementation roadmap with AI prompts and user workflows
related_files:
  - .github/prompts/plan-closing-design.prompt.md
  - docs/current-workflow.md
  - docs/develop/design/app-workflows.md
  - docs/environment.md
  - .dev/docs/sandbox/cash-reconcile/cash-reconcile-implementation-summary.md
---

## Table of Contents

- [Plan: Closing Automation TDD Implementation](#plan-closing-automation-tdd-implementation)
- [Environment usage](#environment-usage)
- [Implementation Overview](#implementation-overview)
- [Phase 1: Shared Infrastructure](#phase-1-shared-infrastructure)
- [Phase 2: Quick wins - Forex and Wallets](#phase-2-quick-wins---forex-and-wallets)
- [Phase 3: Cash Reconcile Refactoring](#phase-3-cash-reconcile-refactoring)
- [Phase 4: Bill Payment Automation](#phase-4-bill-payment-automation)
- [Phase 5: Account Update Modules (IBKR, CPF)](#phase-5-account-update-modules-ibkr-cpf)
- [Phase 6: Statements and HB Reconciliation](#phase-6-statements-and-hb-reconciliation)
- [Phase 7: CLI and Orchestration](#phase-7-cli-and-orchestration)
- [Testing Strategy](#testing-strategy)
- [Validation Gates](#validation-gates)
- [Execution Timeline](#execution-timeline)
- [Success Criteria](#success-criteria)
- [References](#references)

# Plan: Closing Automation TDD Implementation

Complete test-driven development implementation plan for the consolidated monthly closing workflow. Each feature follows the cycle: **design documentation â†’ test cases (SIT/UAT) â†’ implementation â†’ validation â†’ commit**.

## Environment usage

**CRITICAL: Environment management rules**

1. **Development scaffolding** (construction tools, temporary only)
   - `.dev/env` â€” Python virtual environment for helper scripts ONLY
   - `.dev/.scripts/python` â€” Helper scripts for diagnostics, analysis, PDF extraction
   - `.dev/.scripts/bash` â€” Bash helper scripts
   - `.dev/.scripts/cmd` â€” Windows batch helper scripts
   - **DO NOT CREATE A NEW VIRTUAL ENV** - Reuse existing `.dev/env`
   - **DO NOT USE `.dev/env` FOR MAIN APP** - This is scaffolding only

2. **Main application environment** (production runtime)
   - `env/` â€” Python virtual environment for wrapper package and tests (root level)
   - Used by: wrapper package, test scripts, CLI commands
   - This is the "finished building" environment

**Metaphor:** `.dev/` is scaffolding and cranes during construction. `env/` is the finished building's electrical and plumbing systems.

## Implementation Overview

**Phases**: 7 major phases discrete features

**Quality gates**: 100% test pass, 70%+ code coverage, manual UAT validation

## Phase 1: Shared Infrastructure

**Features**: 5 (types, gsheet, homebudget, exceptions, logging)  

All remaining phases depend on this foundation. Build first, validate thoroughly.

### 1.1: Common types and Period class

**Goal**: Define core data classes used across all modules

**Reference documents**:
- [Shared Utilities Details](plan-closing-design.prompt.md#shared-utilities-details)
- `.dev/docs/sandbox/account-statements/configuration-setup-spec.md`

#### Design phase

**AI Prompt**: Generate type requirements specification

```
Analyze the closing workflow and generate complete type definitions specification.

Input:
- Workflow steps: forex, accounts (wallets, IBKR, CPF), bill-payment, cash-reconcile, hb-reconcile, statements
- Reference: docs/current-workflow.md (manual baseline), docs/develop/design/app-workflows.md (design target), plan-closing-design.prompt.md

Output JSON spec with:
1. Period class (year/month/validation)
2. Account class (account_id/name/type/currency)
3. TransactionData class (date/amount as float/reference/notes)
4. Exception types (ValidationError, DataSourceError, PostingError, ToleranceExceededError)

Include validation rules, default values, and immutability requirements.
```

**Expected output**:
- Complete type spec with field descriptions
- Validation rules documented
- Example usage for each type

#### Test design phase (SIT - System Integration Testing)

**Test cases** (tests/unit/types.test.py):
```python
# Test Period
- test_period_valid_construction()
- test_period_invalid_month()
- test_period_string_format()
- test_period_comparison()

# Test Account
- test_account_valid_types()
- test_account_currency_default()
- test_account_readonly()

# Test TransactionData
- test_transaction_data_required_fields()
- test_transaction_data_optional_fields()
- test_transaction_data_validation()
```

**UAT - User acceptance**: Not applicable (internal types)

#### Build phase

**AI Prompt**: Implement types module

```
Implement src/python/closing/util/types.py with complete type definitions.

Requirements:
1. Use dataclasses for all types
2. Add __post_init__ validation
3. No custom __str__, __repr__, __eq__ unless needed
4. Include docstrings
5. Add type hints (from typing import)

Reference: Test cases in tests/unit/types.test.py and plan-closing-design.prompt.md Â§ Shared Utilities Details

Implement in order:
- Period (year, month with validation)
- Account (account_id, name, account_type, currency)
- TransactionData (date, amount as float, reference, notes, metadata)
- All add exception types as needed

Ensure all tests pass. No external dependencies except dataclasses.
```

**Expected output**:
- `src/python/closing/util/types.py` (~150 lines)
- All test cases passing
- Type hints complete

#### Validation phase

**Steps**:

1. Run tests: `pytest tests/unit/types.test.py -v`
2. Verify: All tests pass âœ“
3. Code review: Check for over-engineering, simplify if needed
4. Coverage: `pytest --cov=src/python/closing/util/types tests/unit/types.test.py`
5. Manual check: Type hints work with IDE autocomplete

**Validation checklist**:

- [ ] All 15+ test cases pass
- [ ] Code coverage > 95%
- [ ] No linting errors (flake8, black)
- [ ] No type checking errors (mypy)
- [ ] Immutability enforced for Period
- [ ] Validation in __post_init__

---

### 1.2: Google Sheets interface

**Goal**: Thin read-only wrapper for reference data in Google Sheets

**CRITICAL DISTINCTION**: 
- Google Sheets is read-only data source for reference data and config (shared expenses, master lists, CPF/IBKR balances)
- **NOT** used for storing financial statement data (that is section 1.4's responsibility)
- See section 1.4 for consolidated financial statement storage solution

**Reference documents**:
- `docs/google-sheets.md`
- `.dev/.scripts/python/inspect_helper_schemas.py` (working reference implementation)
- Existing read-only configs: `gsheet/*.json` (cash-expenses.json, shared-expenses.json, cpf.json, ibkr-iba.json)
- Dependencies: `pyproject.toml` includes `sqlite-gsheet>=2.0.0`

#### Design phase

**Existing setup verified**:
1. **Authentication**: Credentials at `.credentials/client_secret.json`
2. **Package**: `sqlite-gsheet` (imported as `sqlgsheet.gsheet`) already in dependencies
3. **Config pattern**: Each workbook has JSON config in `gsheet/` with workbook ID and named ranges
4. **Usage pattern** (from inspect_helper_schemas.py):
   ```python
   from sqlgsheet import gsheet
   gsheet.CLIENT_SECRET_FILE = '.credentials/client_secret.json'
   engine = gsheet.SheetsEngine()
   values = engine.get_rangevalues(wkbid, range_name)
   ```
5. **Existing read-only configs**:
   - `gsheet/cash-expenses.json` - recent transaction templates
   - `gsheet/shared-expenses.json` - household cost allocation rules
   - `gsheet/cpf.json` - CPF account reference data
   - `gsheet/ibkr-iba.json` - Interactive Brokers portfolio reference data

**Implementation approach**:
- Minimal wrapper around sqlgsheet.gsheet.SheetsEngine
- Read-only operations only (no write capability)
- Basic retry logic (2-3 attempts with exponential backoff)
- Reuse existing sqlgsheet package, no custom persistence

#### Test design phase

**Test cases** (tests/unit/gsheet/client.test.py):
```python
# Mock sqlgsheet.gsheet.SheetsEngine responses
- test_fetch_range_success()
- test_fetch_range_empty_sheet()
- test_fetch_range_api_error_handled()
- test_retry_logic_on_temporary_failure()
- test_configuration_loading()
- test_credentials_path_setting()
```

#### Build phase

**AI Prompt**: Implement read-only Google Sheets client wrapper

```
Implement src/python/closing/util/gsheet.py as thin read-only wrapper.

Requirements:
1. Use existing sqlgsheet.gsheet.SheetsEngine (already in dependencies)
2. Implement GoogleSheetsClient class with:
   - __init__(config_path: str, credentials_path: str = ".credentials/client_secret.json")
   - fetch_range(config_name: str, range_name: str) -> pd.DataFrame
   - get_engine() -> gsheet.SheetsEngine (cached)
3. Add basic retry logic (2-3 attempts with exponential backoff)
4. Add error handling with DataSourceError exceptions
5. Load config JSON (wkbid and named ranges)

Reference implementation:
- .dev/.scripts/python/inspect_helper_schemas.py (shows working usage)
- src/python/cash_reconcile/data_sources.py (GoogleSheetsSQLiteDataSource)

Existing read-only configs to support:
- gsheet/cash-expenses.json (recent_txns)
- gsheet/shared-expenses.json (records)
- gsheet/cpf.json (cpf_total, cpf_oa, cpf_sa, cpf_ma, cpf_summary)
- gsheet/ibkr-iba.json (various regions)

Test file: tests/unit/gsheet/client.test.py

Return: src/python/closing/util/gsheet.py (~80 lines - read-only only)
```

**Expected output**:
- `src/python/closing/util/gsheet.py` (~80 lines, read-only only)
- All test cases passing
- Reuses existing sqlgsheet package
- Reuses existing sqlgsheet package

#### Validation phase

**Steps**:
1. Unit tests: `pytest tests/unit/gsheet/client.test.py -v`
2. Manual test with real workbook: Run `.dev/.scripts/python/inspect_helper_schemas.py`
3. Coverage: Aim for >85%

**Validation checklist**:
- [ ] All unit tests pass
- [ ] Retry logic tested (2-3 attempts, exponential backoff)
- [ ] Error handling catches API errors and raises DataSourceError
- [ ] Configuration loading works for all existing configs
- [ ] Credentials path configurable
- [ ] Code coverage > 85%
- [ ] Works with existing gsheet/*.json configs

---

### 1.3: HomeBudget accounting logic wrapper

**Goal**: Implement bespoke accounting logic that combines basic HomeBudget operations per `docs/accounting-logic.md`

**CRITICAL DESIGN DECISION**: Do NOT re-implement HomeBudget CRUD. The homebudget Python package already provides:
- `query_balance(account, date)` 
- `query_expenses(account, period)`
- `add_posting(account, date, amount, reference, tags)`
- `mark_reconciled(txn_id)`

Instead, build business logic modules that USE these methods for accounting patterns.

**Reference documents**:
- `docs/accounting-logic.md`
- `.github/skills/homebudget/SKILL.md`
- `docs/homebudget.md`
- `data/monthly-closing/accounts.json` (account metadata source of truth)

#### Design phase

**Account metadata** (`data/monthly-closing/accounts.json`)

Source of truth for all account information:
- Account names (from HomeBudget)
- Currency (from HomeBudget DB)
- Account type (asset/liability/income/expense/equity)
- Financial statement classification (from financial-statements.json)
- S3 directory mapping (custom)

**Bespoke accounting logic modules**

Implement business logic that handles:

1. **Personal Expenses** (cost center pattern)
   - Double-entry: wallet â†’ personal cost center â†’ expense
   - Auto-detect payment method by matching transfers
   - Example: "Cash TWH SGD" â†’ "TWH - Personal" â†’ "Groceries"

2. **Personal Income** (consolidated account pattern)
   - All income flows through "TWH DBS Multi SGD"
   - Double-entry: source â†’ TWH DBS â†’ income category
   - Example: Salary â†’ "TWH DBS Multi SGD" â†’ "Employment Income"

3. **Investment Accounts** (net P&L pattern)
   - Track M2M gains/losses, dividends, interest separately
   - No expense tracking, only position + cash accounts
   - Example: "IB POSITION USD" + "TWH IB USD" for IBKR

4. **Forex Adjustments** (deferred post-transaction)
   - M2M forex on balance changes
   - Transaction-level forex from credit card statements
   - Post to "Professional Services:Currency Conversion" category

**Transaction properties config** (`data/monthly-closing/transaction_defaults.json`)

Defaults for auto-created transactions:
- Standard categories, tags, payees for bill payments
- Forex transaction category
- Notes templates for allocation/reconciliation

#### Test design phase

**Test cases** (tests/unit/accounting/personal_expenses.test.py, etc.):
```python
# Personal expenses double-entry
- test_post_personal_expense_creates_wallet_transfer()
- test_post_personal_expense_creates_category_posting()
- test_detect_payment_method_by_transfer_match()
- test_payment_method_not_found_uses_default()

# Personal income double-entry
- test_post_personal_income_creates_source_transfer()
- test_post_personal_income_creates_income_category()

# Forex calculations
- test_calculate_m2m_forex_balance_change()
- test_post_forex_adjustment_to_hb()

# Investment accounts
- test_investment_account_tracks_position_and_cash()
- test_investment_posts_dividend_separately()
```

#### Build phase

**AI Prompt**: Implement accounting logic modules

```
Implement src/python/closing/accounting/ with bespoke business logic.

DO NOT re-implement HomeBudget CRUD. Use homebudget library methods directly.

Modules to build:

1. src/python/closing/accounting/personal.py (~80 lines)
   - post_personal_expense(description, amount, wallet_account, category, date) -> (transfer_txn_id, expense_txn_id)
   - post_personal_income(description, amount, income_account, category, date) -> (source_txn_id, income_txn_id)
   - find_transfer_for_expense(expense_txn, threshold_days=3) -> transfer_txn or None

2. src/python/closing/accounting/forex.py (~60 lines)
   - calculate_m2m_forex(account, currency_balance_beg, currency_balance_end, rate_beg, rate_end) -> float
   - post_forex_adjustment(account, m2m_amount, period) -> txn_id
   - post_transaction_forex(amount_posted, amount_actual, date) -> txn_id

3. src/python/closing/accounting/investment.py (~50 lines)
   - get_investment_position(account, on_date) -> dict(position, cash_balance, currency)
   - post_dividend(investment_account, amount, date) -> txn_id
   - post_m2m_gain(investment_account, amount, date) -> txn_id

4. src/python/closing/accounting/__init__.py
   - Export public functions

Dependencies:
- Use homebudget library directly (already installed)
- Use util.types (Period, Account, TransactionData)
- Use util.exceptions (PostingError, ValidationError)
- Use util.logging (Reporter)
- Use data/monthly-closing/accounts.json for metadata
- Use data/monthly-closing/transaction_defaults.json for defaults

Test files: tests/unit/accounting/*.test.py
Reference: 
- docs/accounting-logic.md for business rules
- docs/develop/design/app-workflows.md for workflow integration context

Return:
- src/python/closing/accounting/*.py (~200 lines total)
- Tests passing with fixture HomeBudget database
```

**Expected output**:
- Modular accounting logic implementations
- Each module focused on one accounting pattern
- All business logic from accounting-logic.md implemented
- ~200 lines of business logic (not CRUD scaffolding)

#### Validation phase

**Steps**:
1. Unit tests with fixture HB database: `pytest tests/unit/accounting/ -v`
2. Verify double-entry logic correct (debits = credits)
3. Compare transaction structures to existing patterns in HomeBudget
4. Manual: Post test transactions and verify in HB UI

**Validation checklist**:
- [ ] All tests pass
- [ ] Double-entry balanced (no orphaned transactions)
- [ ] Payment method detection accurate
- [ ] Forex calculations correct per accounting-logic.md
- [ ] Investment account patterns work
- [ ] Integration with homebudget library confirmed

---

### 1.4: Financial Statements Storage

**Goal**: Custom CRUD and storage layer for consolidated financial statement data

**CRITICAL DISTINCTION**: 
- **HomeBudget** stores detailed transaction-level data (accounts, expenses, income)
- **Financial Statements** stores consolidated period-end data (account balances, forex rates, aggregated P&L, closing entries)
- Currently using Google Sheets (gsheet/financial-statements.json) â€” this needs custom local storage/DB

**Reference documents**:
- `docs/develop/design/financial-statements-spec.md`
- `gsheet/financial-statements.json` (current Google Sheets config)
- `data/monthly-closing/` (period-specific data directory)

#### Design phase

**Current state**:
- Balances stored in Google Sheets (gsheet/financial-statements.json config)
- Forex rates in Google Sheets
- Consolidated data across multiple sources
- No local database for financial statements domain

**Target state**:
- Local JSON files per period: `data/monthly-closing/{period}/financial-statements.json`
- Structure:
  ```json
  {
    "period": "2026-02",
    "generated_at": "ISO timestamp",
    "accounts": {
      "account_name": {
        "opening_balance": 1000.00,
        "closing_balance": 1200.00,
        "currency": "SGD",
        "transactions": [
          {"date": "2026-02-01", "amount": 50.0, "category": "..."}
        ]
      }
    },
    "forex_rates": {
      "USD/SGD": {"date": "2026-02-28", "rate": 1.35, "source": "yahoo_finance"}
    },
    "period_summary": {
      "total_income": 5000.00,
      "total_expenses": 2000.00,
      "forex_impact": -50.00
    }
  }
  ```

**CRUD operations needed**:
1. Write period-end snapshot (all accounts, balances, forex, summary)
2. Read period data (for reporting, comparison)
3. Update forex rates (periodic, not full write)
4. Query balances by account, date range
5. Audit trail (versioning per period)

**NOT needed**: Complex query patternsâ€”simple flat JSON files per period suffice.

#### Test design phase

**Test cases** (tests/unit/financial_statements/storage.test.py):
```python
# File I/O
- test_write_period_snapshot()
- test_read_period_data()
- test_update_forex_rates_in_period()
- test_file_not_found_raises_error()

# Data validation
- test_snapshot_includes_all_accounts()
- test_snapshot_balances_match_input()
- test_forex_rates_valid_format()

# Versioning
- test_backup_previous_version_on_write()
- test_list_available_periods()
```

#### Build phase

**AI Prompt**: Implement financial statements storage

```
Implement src/python/closing/financial_statements/storage.py for period snapshots.

Requirements:
1. Implement FinancialStatementsStore class:
   - __init__(data_dir="data/monthly-closing")
   - write_period_snapshot(period: Period, data: dict) -> str (file_path)
   - read_period_snapshot(period: Period) -> dict
   - update_forex_rates(period: Period, rates: dict[str, float]) -> None
   - list_periods() -> list[Period]
   - backup_previous_version() (auto before write)

2. JSON schema (data/monthly-closing/{YYYY-MM}/financial-statements.json):
   - period, generated_at
   - accounts: {account_name: {opening, closing, currency, transactions}}
   - forex_rates: {pair: {date, rate, source}}
   - period_summary: {income, expenses, forex_impact}
   - audit_trail: {written_by, written_at, version}

3. Validation:
   - Balances make arithmetic sense
   - Forex rates have dates
   - All required fields present
   - Data type validation (floats, dates, strings)

4. Error handling:
   - File not found â†’ DataSourceError
   - Invalid JSON â†’ ValidationError
   - Missing required fields â†’ ValidationError

Test file: tests/unit/financial_statements/storage.test.py
Reference: docs/develop/design/financial-statements-spec.md

Return: src/python/closing/financial_statements/storage.py (~120 lines)
```

**Expected output**:
- Thin storage layer for period snapshots
- Auto-versioning with backups
- Simple file-based persistence
- Clear separation from HomeBudget data

#### Validation phase

**Steps**:
1. Unit tests: `pytest tests/unit/financial_statements/storage.test.py -v`
2. Manual: Write and read a period snapshot
3. Verify file structure matches schema
4. Test backup mechanism (write twice, check backup exists)

**Validation checklist**:
- [ ] All tests pass
- [ ] File created in correct location
- [ ] JSON valid and parseable
- [ ] All required fields present on write
- [ ] Backup created before overwrite
- [ ] Read data matches written data

---

### 1.5: Exceptions and logging infrastructure

**MOVED TO 1.6** - Renumbered after Financial Statements Storage addition

---

### 1.6: Exceptions and logging infrastructure

**Goal**: Unified error handling and structured reporting

**Reference documents**:
- `plan-closing-design.prompt.md Â§ Shared Utilities Details`
- `.dev/docs/sandbox/account-statements/validation-error-handling-spec.md`

#### Design phase

**Test design phase** (tests/unit/util/exceptions.test.py):
```python
# Exception hierarchy
- test_closing_error_base_class()
- test_validation_error_inherits_from_base()
- test_data_source_error_inherits_from_base()
- test_posting_error_inherits_from_base()
- test_tolerance_exceeded_error_inherits_from_base()

# Exception context
- test_exception_preserves_message()
- test_exception_includes_context_data()
- test_exception_stacktrace_useful()
```

#### Build phase

**AI Prompt**: Implement exceptions and logging

```
Implement src/python/closing/util/exceptions.py and src/python/closing/util/logging.py

exceptions.py (~80 lines):
1. Define exception hierarchy:
   - ClosingError(Exception) - base
   - ValidationError(ClosingError) - data validation
   - DataSourceError(ClosingError) - API/data fetch errors
   - PostingError(ClosingError) - transaction posting errors
   - ToleranceExceededError(ClosingError) - variance too large
2. Each exception includes:
   - Descriptive message
   - Context dict for debugging
   - __str__ for logging

logging.py (~150 lines):
1. Implement Reporter class:
   - __init__(period: Period, session_id: str)
   - start_step(step_name: str) -> None
   - end_step(step_name: str, status: str, details: dict) -> None
   - error(step_name: str, error: Exception) -> None
   - to_json() -> str (session report)
   - to_markdown() -> str (readable summary)
2. Implement StepReport dataclass:
   - step_name, status (running/success/error)
   - start_time, end_time, duration
   - details (dict), error_message (if failed)
3. Thread-safe reporter singleton

Test files: tests/unit/util/exceptions.test.py and tests/unit/util/logging.test.py
Reference: plan-closing-design.prompt.md

Return: 
- src/python/closing/util/exceptions.py (~80 lines)
- src/python/closing/util/logging.py (~150 lines)
```

**Expected output**:
- Unified exception hierarchy
- Structured error reporting
- Session logging with JSON + markdown output

#### Validation phase

**Steps**:
1. Unit tests: `pytest tests/unit/util/exceptions.test.py tests/unit/util/logging.test.py -v`
2. Integration: Verify exceptions propagate correctly
3. Manual: Generate sample session report

**Validation checklist**:
- [ ] All unit tests pass
- [ ] Exception hierarchy correct
- [ ] Session report JSON valid
- [ ] Markdown output readable
- [ ] Code coverage > 90%

---

### 1.7: Configuration management

**Goal**: Load and validate configuration from JSON, environment, CLI

**Reference documents**:
- `.dev/docs/sandbox/account-statements/configuration-setup-spec.md`

#### Design phase

**User input needed**: Configuration file locations and defaults

**Ask questions**:
```
Configuration management setup:

1. Configuration files:
   - Config directory path (default: gsheet/)?
   - Main config file name (default: closing_config.json)?
   - Account mappings file name (default: account_mappings.json)?
   - Override via environment variables (.env)?

2. Required configuration:
   - Forex data source (Yahoo Finance, ECB, custom)?
   - Cash reconciliation tolerance (threshold)?
   - Bill payment statement directory?
   - S3 bucket for PDF uploads?

3. Defaults:
   - Default currencies (SGD)?
   - Default period (current month)?
   - Log directory?

4. Validation:
   - Fail fast on missing required config?
   - Environment-specific configs (dev, test, prod)?
```

**Expected inputs**:
- Configuration file paths
- Required vs optional settings
- Environment overrides
- Defaults per setting

#### Test design phase

**Test cases** (tests/unit/config/config.test.py):
```python
# Configuration loading
- test_load_config_from_json()
- test_load_config_from_env_override()
- test_missing_required_config_raises_error()
- test_default_values_applied()
- test_period_string_parsed_correctly()

# Configuration validation
- test_validate_all_required_fields()
- test_validate_numeric_ranges()
- test_validate_paths_exist()
```

#### Build phase

**AI Prompt**: Implement configuration management

```
Implement src/python/closing/util/config.py for configuration loading and validation.

Requirements:
1. Implement ConfigLoader class:
   - __init__() - detect and load config files
   - load_json(path: str) -> dict
   - load_env() -> dict (from .env file)
   - merge_configs(json_config: dict, env_config: dict) -> dict
   - validate(config: dict) -> None (raise ValidationError if invalid)
   - get_full_config() -> dict (merged and validated)
2. Implement config schema with required/optional fields:
   - forex_source (Yahoo Finance, ECB, etc.)
   - tolerance_cash_reconcile (tolerance)
   - homebudget_db_path
   - gsheet_workbook_ids (dict)
   - account_mappings (dict)
   - s3_bucket (optional)
3. Load from:
   - gsheet/closing_config.json (primary)
   - Environment variables with CLOSING_ prefix
   - CLI arguments (optional, passed in)
4. Provide sensible defaults

Test file: tests/unit/config/config.test.py
Reference: .dev/docs/sandbox/account-statements/configuration-setup-spec.md and user inputs

Return: src/python/closing/util/config.py (~200 lines)
```

**Expected output**:
- Configuration loading with cascading precedence
- Comprehensive validation
- Config example file

#### Validation phase

**Steps**:
1. Unit tests: `pytest tests/unit/config/config.test.py -v`
2. Manual: Load real config file and verify
3. Integration: Test config used in other modules

**Validation checklist**:
- [ ] All tests pass
- [ ] Config file schema documented
- [ ] Example config provided
- [ ] Validation catches missing required fields
- [ ] Environment override works

---

## Phase 1 Completion

**Deliverables**:
- âœ“ `src/python/closing/util/types.py` with Period, Account, TransactionData (amounts as float)
- âœ“ `src/python/closing/util/gsheet.py` thin read-only wrapper (~80 lines) around sqlgsheet
- âœ“ `src/python/closing/accounting/` modules for personal expenses, income, forex, investment (~200 lines)
- âœ“ `src/python/closing/financial_statements/storage.py` custom period snapshot storage (~120 lines)
- âœ“ `src/python/closing/util/exceptions.py` with unified exception hierarchy
- âœ“ `src/python/closing/util/logging.py` with Reporter and structured logging
- âœ“ `src/python/closing/util/config.py` with configuration management
- âœ“ `data/monthly-closing/accounts.json` account metadata (source of truth)
- âœ“ `data/monthly-closing/transaction_defaults.json` transaction templates
- âœ“ All test suites passing (>85% coverage)

**Validation**:
```bash
pytest tests/unit/ tests/integration/ -v --cov=src/python/closing --cov-report=html
# Target: >85% coverage, all tests passing
```

**Architecture summary**:
- **HomeBudget layer**: Provides transaction-level CRUD via homebudget library (unchanged, trusted)
- **Accounting logic layer**: Implements business rules for personal, investment, forex patterns
- **Financial statements layer**: Manages period snapshots and consolidated data (custom storage)
- **Shared utilities**: Types, exceptions, logging, configuration

**Go/No-Go Decision**: All tests passing? Accounting logic matches accounting-logic.md? Financial statements storage validated? â†’ Proceed to Phase 2

---

## Phase 2: Closing Workflow Integration

**Duration**: 1-2 weeks  
**Features**: 3 (forex M2M posting, wallet reconciliation, financial statement snapshot)  
**Lines of code**: ~250  
**Complexity**: Medium (integrating Phase 1 modules)

**Goal**: Integrate Phase 1 modules into end-to-end monthly closing workflow

**Architecture**:
- Input: Period (e.g., 2026-02)
- Process: Fetch balances, calculate forex M2M, post adjustments, save snapshot
- Output: `data/monthly-closing/{YYYY-MM}/financial-statements.json`

### 2.1: Forex M2M adjustment posting

**Goal**: Calculate and post M2M forex adjustments for multi-currency accounts

**Reference documents**:
- `docs/accounting-logic.md Â§ Forex â†’ M2M forex on balances`
- `src/python/closing/accounting/forex.py` (from Phase 1.3)

#### Design phase

**Input data needed**:
- Closing date (end of period)
- Account list with opening/closing balances
- Exchange rates (beginning and end of period)

**Calculation**:
```
M2M forex = currency_balance * (rate_end - rate_beg)
```

**Posting**:
1. Calculate M2M for each multi-currency account
2. Post adjustment to HomeBudget via `accounting.forex.post_m2m_forex()`
3. Include in financial statement snapshot

#### Test design phase

**Test cases** (tests/integration/closing/forex_m2m.test.py):
```python
# M2M calculation
- test_calculate_m2m_forex_debit_currency_balance_increase()
- test_calculate_m2m_forex_credit_currency_rate_depreciation()
- test_m2m_zero_if_rate_unchanged()

# Posting
- test_post_m2m_adjustment_creates_hb_transaction()
- test_post_m2m_includes_forex_category()
- test_post_m2m_includes_period_in_notes()
```

#### Build phase

**AI Prompt**: Implement forex M2M closing step

```
Implement src/python/closing/workflow/forex_m2m.py (closing step for forex adjustments).

Requirements:
1. Implement close_forex_m2m(period: Period) -> dict:
   - Get account list from data/monthly-closing/accounts.json
   - Query HomeBudget for opening balance (period start)
   - Query HomeBudget for closing balance (period end)
   - Get forex rates (from configured rate source)
   - For each multi-currency account:
     * Calculate M2M using accounting.forex.calculate_m2m_forex()
     * Post adjustment using accounting.forex.post_m2m_forex()
   - Return summary dict (accounts_processed, m2m_total, posted_count)

2. Dependencies:
   - Use accounting.forex module from Phase 1.3
   - Use homebudget library (already available)
   - Use types.Period, exceptions

3. Logging:
   - Report using util.logging.Reporter

Test file: tests/integration/closing/forex_m2m.test.py
Reference: docs/accounting-logic.md and Phase 1.3 accounting module

Return: src/python/closing/workflow/forex_m2m.py (~60 lines)
```

**Expected output**:
- Forex M2M step integrated into closing workflow
- Calculations verified against accounting rules
- HB postings validated

#### Validation phase

**Steps**:
1. Integration tests: `pytest tests/integration/closing/forex_m2m.test.py -v`
2. Manual: Run with test period, verify HB transactions created
3. Compare calculations to Excel validation

**Validation checklist**:
- [ ] All tests pass
- [ ] M2M calculations correct per accounting-logic.md
- [ ] HB transactions posted with correct amount and date
- [ ] Forex category applied

---

### 2.2: Wallet balance snapshot

**Goal**: Capture wallet balances at period end

#### Design phase

**Input**: List of wallet accounts from accounts.json

**Output**: Period snapshot with balances

#### Test design phase

**Test cases** (tests/integration/closing/wallet_snapshot.test.py):
```python
# Balance fetching
- test_fetch_wallet_balances_for_period_end()
- test_include_all_wallet_accounts()
- test_exclude_investment_accounts()

# Snapshot storage
- test_save_balances_to_period_file()
```

#### Build phase

**AI Prompt**: Implement wallet snapshot step

```
Implement src/python/closing/workflow/wallet_snapshot.py.

Requirements:
1. Implement close_wallet_balances(period: Period) -> dict:
   - Get wallet accounts from accounts.json
   - Query HomeBudget for balance on period end date
   - Save to financial_statements dict (prepared by Phase 2.3)
   - Return summary (accounts_count, snapshot_date)

Test file: tests/integration/closing/wallet_snapshot.test.py

Return: src/python/closing/workflow/wallet_snapshot.py (~30 lines)
```

#### Validation phase

**Steps**:
1. Tests: `pytest tests/integration/closing/wallet_snapshot.test.py -v`
2. Manual: Verify wallet balances in snapshot match HB UI

---

### 2.3: Financial statement period snapshot

**Goal**: Consolidate ALL period-end data into single snapshot file

#### Test design phase

**Test cases** (tests/integration/closing/period_snapshot.test.py):
```python
# Snapshot assembly
- test_create_period_snapshot_combines_all_data()
- test_snapshot_includes_forex_m2m()
- test_snapshot_includes_wallet_balances()
- test_snapshot_includes_period_summary()

# Storage
- test_save_snapshot_to_financial_statements_json()
- test_backup_previous_snapshot()
```

#### Build phase

**AI Prompt**: Implement period snapshot assembly

```
Implement src/python/closing/workflow/period_snapshot.py.

Requirements:
1. Implement assemble_period_snapshot(period: Period, data_dict: dict) -> dict:
   - Call Phase 2.1 (forex M2M)
   - Call Phase 2.2 (wallet balances)
   - Combine results into unified structure
   - Calculate period summary (total income/expenses/forex impact)
   - Return complete snapshot dict

2. Implement save_period_snapshot(period: Period, snapshot: dict) -> str:
   - Use financial_statements.storage module from Phase 1.4
   - Write to data/monthly-closing/{YYYY-MM}/financial-statements.json
   - Create backup of previous version
   - Return file path

Test file: tests/integration/closing/period_snapshot.test.py
Reference: Phase 1.4 financial_statements.storage

Return: src/python/closing/workflow/period_snapshot.py (~80 lines)
```

#### Validation phase

**Steps**:
1. Integration tests: `pytest tests/integration/closing/period_snapshot.test.py -v`
2. Manual: Run full closing workflow for test period
3. Verify snapshot file created and contains all expected data
4. Verify backup of previous version created

---

## Phase 2 Completion

**Deliverables**:
- âœ“ `src/python/closing/workflow/forex_m2m.py` - Forex M2M calculation and posting
- âœ“ `src/python/closing/workflow/wallet_snapshot.py` - Wallet balance capture
- âœ“ `src/python/closing/workflow/period_snapshot.py` - Unified snapshot assembly
- âœ“ `data/monthly-closing/{YYYY-MM}/financial-statements.json` (generated per period)
- âœ“ All integration tests passing
- âœ“ Manual closing workflow validation complete

**Validation**:
```bash
pytest tests/integration/closing/ -v
```

**Go/No-Go Decision**: Workflow completes successfully? Snapshots validated? â†’ Proceed to Phase 3

---

## Phase 3: Cash Reconcile Refactoring

**Duration**: 1-2 weeks  
**Features**: Refactor and simplify existing cash_reconcile module  
**Lines of code**: Reduce from 745 â†’ ~200  
**Complexity**: Medium-High (refactor existing code)

### 3.1: Analyze and plan refactoring

**Goal**: Port cash_reconcile to use Phase 1 utilities, reduce complexity

#### Design phase

**Current state**:
- cash_reconcile module has 745 lines across 8 files
- Contains domain models, repository, reporting, configuration (mostly covered by Phase 1)
- Core logic (gap calculation) is sound, can be reused

**Target state**:
- Refactored to ~200 lines (2 modules)
- Uses util modules for types, exceptions, logging, config
- Keep core business logic (gap calculation, posting)

#### Test redesign phase

**New test structure** (tests/integration/cash_reconcile/):
```python
# Reduced test suite focusing on core logic
tests/integration/cash_reconcile/
â”œâ”€â”€ test_reconcile_calculation.py      (gap calculation)
â”œâ”€â”€ test_reconcile_posting.py          (HB transaction creation)
â”œâ”€â”€ test_reconcile_integration.py      (end-to-end with fixture HB)
â””â”€â”€ test_reconcile_reporting.py        (JSON + markdown reports)
```

#### Build phase

**AI Prompt**: Refactor cash_reconcile module

```
Refactor src/python/cash_reconcile/ to use Phase 1 utilities.

Current state (745 lines across 8 modules):
- domain.py - entities/aggregates (reuse util.types)
- core.py - facade (can be eliminated)
- reconciliation.py - core logic (keep this)
- reports.py - reporting (reuse util.logging)
- persistence.py - sessions (reuse util.logging)
- data_sources.py - data fetching (reuse util.gsheet, homebudget)
- config.py - config (reuse util.config)
- exceptions.py - errors (reuse util.exceptions)

Target (200 lines):
- reconcile.py (~150 lines) - core reconciliation logic
- __init__.py (empty)

Steps:
1. Delete domain.py, core.py, persistence.py, data_sources.py, reports.py, config.py, exceptions.py
2. Refactor reconciliation.py â†’ reconcile.py:
   - Import util modules (types, exceptions, logging, config)
   - Keep core functions: reconcile(), post_adjustment()
   - Use Reporter instead of SessionRepository
   - Use util.exceptions error types
3. Update all imports
4. Run test suite - should pass without changes

Test files to keep and adapt:
- tests/integration/cash_reconcile/test_reconcile_*.py

Test files to remove:
- tests/unit/ cash_reconcile files (entities, repository, persistence no longer exist)

Return:
- src/python/cash_reconcile/reconcile.py (~150 lines)
- src/python/cash_reconcile/__init__.py (export)
- Updated tests (reduced scope)
```

**Expected output**:
- Simplified, maintainable cash_reconcile module
- 80% code reduction
- All tests still passing
- Better code reuse via util modules

#### Validation phase

**Steps**:
1. Run refactored tests: `pytest tests/integration/cash_reconcile/ -v`
2. Verify calculations still correct (regression tests)
3. Compare output to original (should be identical)
4. Performance test (should be faster due to less overhead)

**Validation checklist**:
- [ ] All integration tests pass
- [ ] Refactored code < 200 lines
- [ ] Old files deleted (no remnants)
- [ ] Util module reuse > 80%
- [ ] Reports identical to original
- [ ] No regressions in gap calculation

---

## Phase 4: Bill Payment Automation

**Duration**: 2 weeks  
**Features**: 3 (parsers, shared costs allocation, HB posting)  
**Lines of code**: ~240  
**Complexity**: High (statement parsing, allocation logic)

### 4.1: Statement parsers

**Goal**: Detect and parse bank statements (PDF/CSV) for 4 accounts

**Reference documents**:
- `.dev/docs/sandbox/account-statements/parser-spec.md`
- `reference/hb-finances/statements.py` (Python reference implementation)

#### Design phase

**User input needed**: Bank statement formats and account mappings

**Ask questions**:
```
Statement parsing configuration:

1. Bank accounts:
   - List of accounts (DBS, UOB, Citi, BOA)?
   - Statement file naming convention?
   - File formats (PDF, CSV, XLS)?
   - Statement directory?

2. DBS account:
   - PDF page structure (header rows, skip rows)?
   - Transaction columns (date, amount, description)?
   - Date format in statement?
   - Example statement file available for testing?

3. UOB, Citi, BOA:
   - Same questions for each bank
   - CSV format specs?
   - Column headers?

4. Parsing errors:
   - How to handle unrecognized columns?
   - How to handle parsing errors (skip, abort)?
   - Validation rules (min/max amount)?
```

#### Test design phase

**Test cases** (tests/unit/bill_payment/parsers.test.py):
```python
# Parser detection
- test_detect_dbs_statement()
- test_detect_uob_statement()
- test_detect_citi_statement()
- test_detect_boa_statement()
- test_detect_unknown_statement_raises_error()

# DBS parser
- test_dbs_parser_extracts_transactions()
- test_dbs_parser_date_format_conversion()
- test_dbs_parser_amount_parsing()
- test_dbs_parser_missing_fields_raises_error()

# Similar tests for UOB, Citi, BOA
- test_uob_parser_*()
- test_citi_parser_*()
- test_boa_parser_*()

# Integration
- test_detect_and_parse_returns_correct_parser()
```

#### Build phase

**AI Prompt**: Implement statement parsers

```
Implement src/python/closing/bill_payment/parsers.py with bank statement parsing.

Requirements:
1. Implement detect_and_parse(file_path: str) -> list[TransactionData]:
   - Detect bank by filename or content
   - Route to appropriate parser
   - Return list of TransactionData objects
2. Implement parser functions:
   - parse_dbs(file_path: str) -> list[TransactionData]
   - parse_uob(file_path: str) -> list[TransactionData]
   - parse_citi(file_path: str) -> list[TransactionData]
   - parse_boa(file_path: str) -> list[TransactionData]
3. For each parser:
   - Extract PDF using pdfplumber or similar
   - Parse CSV/XLS using pandas
   - Map columns to TransactionData fields
   - Validate each transaction
   - Handle errors with DataSourceError
4. Support utilities:
   - parse_date(date_str, format_str) -> date
   - parse_amount(amount_str) -> Decimal
   - normalize_reference(text) -> str

User inputs from design phase:
- Bank formats: ${BANK_FORMATS}
- File structures: ${FILE_STRUCTURES}
- Validation rules: ${VALIDATION_RULES}

Test file: tests/unit/bill_payment/parsers.test.py
Test data: Sample statements in tests/fixtures/statements/

Reference: .dev/docs/sandbox/account-statements/parser-spec.md and reference/hb-finances/statements.py

Return:
- src/python/closing/bill_payment/__init__.py (empty)
- src/python/closing/bill_payment/parsers.py (~150 lines)
- src/python/closing/bill_payment/utils.py (~50 lines)
```

**Expected output**:
- Parser implementations for all 4 accounts
- Auto-detection of statement type
- Comprehensive test coverage

#### Validation phase

**Steps**:
1. Parse test statements: `pytest tests/unit/bill_payment/parsers.test.py -v`
2. Manual: Parse real statements if available
3. Compare to reference implementation (statements.py)

**Validation checklist**:
- [ ] All parsers implemented
- [ ] All unit tests pass
- [ ] Detection works for all formats
- [ ] Dates parsed correctly for each bank
- [ ] Amounts match statement exactly
- [ ] Error handling for malformed files

---

### 4.2: Shared costs allocation

**Goal**: Allocate shared bill expenses across household members

**Reference documents**:
- `docs/bill-payment.md`
- `.dev/docs/sandbox/bill-payment/bill-payment-shared-costs-automation-design.md`

#### Design phase

**User input needed**: Household member names and cost allocation rules

**Ask questions**:
```
Shared costs configuration:

1. Household members:
   - List of member names?
   - Member accounts in HomeBudget?
   - Default allocation percentage for each?

2. Cost allocation rules:
   - What bills are shared (utilities, rent, etc.)?
   - How are costs split (50/50, percentage, amount)?
   - Special rules for any bills?

3. Accounts for allocation:
   - Which account pays the bill (credit card, checking)?
   - Allocation between members (income statement accounts)?
   - Override for specific transactions?
```

#### Test design phase

**Test cases** (tests/unit/bill_payment/shared_costs.test.py):
```python
# Allocation logic
- test_equal_split_two_people()
- test_percentage_based_allocation()
- test_amount_based_allocation()
- test_custom_rules_override_defaults()

# Shared cost fetching
- test_fetch_shared_expenses_from_gsheet()
- test_filter_shared_by_date_range()

# Posting
- test_allocate_creates_transactions_for_all_members()
- test_allocate_preserves_total_amount()
- test_allocate_respects_custom_rules()
```

#### Build phase

**AI Prompt**: Implement shared costs allocation

```
Implement src/python/closing/bill_payment/shared_costs.py for cost allocation.

Requirements:
1. Implement fetch_shared_expenses(period: Period) -> list[dict]:
   - Query gsheet for shared expense rules (Google Sheet tab)
   - Filter by period
   - Return list of expense definitions
2. Implement allocate_shares(expense: dict, members: list[str]) -> list[dict]:
   - Apply allocation rule to generate transactions
   - One transaction per member
   - Output list of transaction dicts (not posted yet)
   - Validate total amount preserved
3. Data structures:
   - SharedExpense (name, amount, allocation_rule, date)
   - AllocationRule (type, percentages/amounts, members)
4. Allocation types:
   - "equal" - split equally among members
   - "percentage" - by percentages (must sum to 100)
   - "amount" - by specific amounts
   - "custom" - from Google Sheet

User inputs from design phase:
- Household members: ${MEMBERS}
- Default allocation: ${DEFAULT_ALLOCATION}
- Shared expense sheet range: ${GSHEET_RANGE}

Test file: tests/unit/bill_payment/shared_costs.test.py
Reference: docs/bill-payment.md and design doc

Return: src/python/closing/bill_payment/shared_costs.py (~100 lines)
```

**Expected output**:
- Shared cost allocation logic
- Multi-member support
- Flexible allocation rules
- Validated total preservation

#### Validation phase

**Steps**:
1. Unit tests: `pytest tests/unit/bill_payment/shared_costs.test.py -v`
2. Integration: Test with real gsheet data
3. Manual: Verify allocation percentages match household agreement

**Validation checklist**:
- [ ] All tests pass
- [ ] Equal split verified (cents rounding handled)
- [ ] Custom rules work
- [ ] Total amount always preserved
- [ ] Gsheet data loaded correctly

---

### 4.3: HomeBudget transaction posting

**Goal**: Create and post allocation transactions to HomeBudget

**Reference documents**:
- `.github/skills/homebudget/SKILL.md`
- `docs/develop/design/database-schema.md`

#### Test design phase

**Test cases** (tests/integration/bill_payment/posting.test.py):
```python
# Posting
- test_post_transactions_creates_entries_in_hb()
- test_post_transactions_deduplicates_before_create()
- test_post_transactions_invalid_account_raises_error()
- test_post_transactions_atomic_all_or_none()

# Error handling
- test_post_transactions_duplicate_detected_skipped()
- test_post_transactions_posting_error_rolled_back()
```

#### Build phase

**AI Prompt**: Implement transaction posting

```
Implement src/python/closing/bill_payment/posting.py for HomeBudget posting.

Requirements:
1. Implement post_transactions(transactions: list[dict], period: Period) -> dict:
   - Check each transaction for duplicates
   - Create transaction in HomeBudget via util.homebudget
   - Return summary (created_count, skipped_count, error_count)
   - On error, rollback all changes
2. Each transaction should include:
   - date, amount, reference (description)
   - from_account, to_account (category)
   - notes (allocation note, member name)
   - tags (for filtering)
3. Error handling:
   - Skip duplicates (log as warning)
   - Validate accounts exist
   - Atomic: all succeed or all fail
   - Return detailed report

Test file: tests/integration/bill_payment/posting.test.py
Reference: util.homebudget.add_expense and util.homebudget.add_transfer

Return: src/python/closing/bill_payment/posting.py (~80 lines)
```

**Expected output**:
- Transaction posting to HomeBudget
- Duplicate handling
- Atomic operations (rollback on error)

#### Validation phase

**Steps**:
1. Integration tests: `pytest tests/integration/bill_payment/posting.test.py -v`
2. Test with fixture HB database
3. Verify transactions appear in HB GL

**Validation checklist**:
- [ ] All tests pass
- [ ] Transactions created in HB
- [ ] Duplicates skipped correctly
- [ ] Atomic behavior verified
- [ ] Integration complete

---

## Phase 5: Account Update Modules (IBKR, CPF)

**Duration**: 1 week  
**Features**: 2 (IBKR brokerage parsing, CPF statement parsing)  
**Lines of code**: ~200  
**Complexity**: Medium-High (statement formats vary)

### 5.1: IBKR statement parsing

**Goal**: Parse Interactive Brokers statement and calculate holdings

**Reference documents**:
- `.dev/docs/sandbox/account-statements/account-statements.md`
- `.dev/docs/sandbox/account-statements/parser-spec.md Â§ IBKR`

#### Design phase

**User input needed**: IBKR statement format and account mappings

**Ask questions**:
```
IBKR configuration:

1. Statement export:
   - Statement file format (CSV, XML, custom)?
   - Sections included (positions, trades, fees)?
   - Currency (USD, SGD)?
   - Account naming in statement?

2. Holdings calculation:
   - Extract cost basis or current positions?
   - Include cash balance?
   - Include unrealized P&L?
   - Currency conversion needed?

3. Account mapping:
   - IBKR account name to HomeBudget account?
   - Asset account or investment account type?

4. Validation:
   - Min/max position size?
   - Expected holdings items count?
```

#### Build phase

**AI Prompt**: Implement IBKR parser

```
Implement src/python/closing/accounts/ibkr.py for IBKR statement parsing.

Requirements:
1. Implement parse_ibkr_statement(file_path: str) -> dict:
   - Parse IBKR statement file
   - Extract positions/holdings
   - Calculate total portfolio value
   - Return dict with:
     - positions (list of {symbol, quantity, price, value})
     - total_value (float)
     - cash_balance (float)
     - date (as of date)
     - currency
2. Handle IBKR statement sections:
   - Account Information (currency, account ID)
   - Open Positions (current holdings)
   - Trades (execution prices, commissions)
   - Corporate Actions (dividends, splits)
3. Validation:
   - Verify currency matches account
   - Check for negative positions (shorts)
   - Validate prices > 0

User inputs from design phase:
- Statement format: ${IBKR_FORMAT}
- Holdings calculation: ${HOLDINGS_CALC}
- Account mapping: ${ACCOUNT_MAPPING}

Test file: tests/unit/accounts/ibkr.test.py
Test data: Sample IBKR statements in tests/fixtures/statements/

Reference: .dev/docs/sandbox/account-statements/account-statements.md

Return: src/python/closing/accounts/ibkr.py (~120 lines)
```

**Expected output**:
- IBKR statement parser
- Portfolio calculation
- Holdings summary

---

### 5.2: CPF statement parsing

**Goal**: Parse CPF statement and extract account values

**Reference documents**:
- `.dev/docs/sandbox/account-statements/account-statements.md`
- `.dev/docs/sandbox/account-statements/parser-spec.md Â§ CPF`

#### Build phase

**AI Prompt**: Implement CPF parser

```
Implement src/python/closing/accounts/cpf.py for CPF statement parsing.

Requirements:
1. Implement parse_cpf_statement(file_path: str) -> dict:
   - Parse CPF statement PDF or CSV
   - Extract account balances:
     - Ordinary Account (OA)
     - Special Account (SA)
     - Medisave Account (MA)
     - Retirement Account (RA)
   - Return dict with:
     - account_balances (dict: account_name -> float)
     - total_balance (float)
     - date (statement date)
     - currency (SGD always)
2. Handle different CPF statement formats:
   - Extract tables with account names
   - Sum component values (principal + interest)
   - Handle multipage statements
3. Validation:
   - All balances >= 0
   - Date is recent (within 3 months)
   - Currency is SGD

Test file: tests/unit/accounts/cpf.test.py
Test data: Sample CPF statements in tests/fixtures/statements/

Reference: .dev/docs/sandbox/account-statements/account-statements.md

Return: src/python/closing/accounts/cpf.py (~100 lines)
```

**Expected output**:
- CPF statement parser
- Multi-account balance extraction
- Validation and error handling

---

## Phase 6: Statements and HB Reconciliation

**Duration**: 2 weeks  
**Features**: 4 (income statement, balance sheet, PDF generation, HB reconciliation)  
**Lines of code**: ~300  
**Complexity**: High (financial calculations, reconciliation logic)

### 6.1: Income statement aggregation

### 6.2: Balance sheet aggregation

### 6.3: PDF generation and S3 upload

### 6.4: HomeBudget reconciliation

*(Detailed specifications follow similar TDD pattern as earlier phases)*

---

## Phase 7: CLI and Orchestration

**Duration**: 1 week  
**Features**: 2 (CLI commands, orchestrator)  
**Lines of code**: ~150  
**Complexity**: Low-Medium

### 7.1: CLI entry point

### 7.2: Orchestrator and step execution

---

## Testing Strategy

### Unit tests

**Coverage target**: > 85% of util and core modules

```bash
pytest tests/unit/ --cov=src/python/closing --cov-report=html
```

### Integration tests

**Coverage target**: > 70% of integration scenarios

```bash
# All integration tests with fixture database
pytest tests/integration/ -v

# Specific feature integration
pytest tests/integration/homebudget/ -v
pytest tests/integration/bill_payment/ -v
pytest tests/integration/cash_reconcile/ -v
```

### System integration tests (SIT)

**Per feature**: Run complete workflow with fixture data

```
SIT workflow:
1. Load fixture database
2. Execute feature end-to-end
3. Verify output matches expected result
4. Check Google Sheets updated correctly
5. Verify HomeBudget transactions created
6. Generate reconciliation report
7. Compare to baseline output
```

### End-to-end tests (UAT)

**Monthly closing validation**: Full workflow with real data

```
UAT workflow (after all features complete):
1. Run 'closing reconcile --period 2026-02'
2. Verify all steps complete successfully
3. Check outputs exist (JSON report, markdown summary, PDF statement)
4. Validate Google Sheets updated
5. Validate HomeBudget transactions posted
6. Verify balances reconcile
7. Compare to prior month manual closing (if available)
```

---

## Validation Gates

Each phase requires:
- âœ“ All unit + integration tests passing
- âœ“ Code coverage > 85%
- âœ“ No linting errors (flake8, black format)
- âœ“ No type errors (mypy strict)
- âœ“ User validation of configuration
- âœ“ Manual smoke test if applicable

**Go/No-Go process**:
```
Phase N complete?
â”œâ”€ Tests pass? (100%)
â”œâ”€ Coverage adequate? (>85%)
â”œâ”€ Code reviewed? (simplified, no over-engineering)
â”œâ”€ User inputs documented?
â”œâ”€ Configuration examples provided?
â””â”€ Ready for next phase? (all gates clear)
```

---

## Execution Timeline

| Phase | Duration | Start | End | Status |
|-------|----------|-------|-----|--------|
| 1: Shared infrastructure | 1 week | 3/1 | 3/7 | Planning |
| 2: Quick wins (forex, wallets) | 3-5 days | 3/8 | 3/12 | Pending |
| 3: Cash reconcile refactoring | 1-2 weeks | 3/13 | 3/26 | Pending |
| 4: Bill payment automation | 2 weeks | 3/27 | 4/9 | Pending |
| 5: Account update modules | 1 week | 4/10 | 4/16 | Pending |
| 6: Statements & HB reconcile | 2 weeks | 4/17 | 4/30 | Pending |
| 7: CLI and testing | 1 week | 5/1 | 5/7 | Pending |
| **Total** | **~9-11 weeks** | **3/1** | **5/7** | **On track** |

---

## Success Criteria

âœ“ All 7 phases complete  
âœ“ All test suites passing (>85% coverage)  
âœ“ CLI commands working (`closing reconcile --period YYYY-MM`)  
âœ“ Full closing workflow automated  
âœ“ 80% code reduction vs existing codebase  
âœ“ User documentation complete  
âœ“ User validation sign-off

---

## References

**Design documents**:
- [Consolidated Monthly Closing Automation](plan-closing-design.prompt.md)
- [docs/current-workflow.md](../../docs/current-workflow.md) - baseline manual workflow
- [docs/develop/design/app-workflows.md](../../docs/develop/design/app-workflows.md) - target automated workflow design
- [docs/develop/](../../docs/develop/) - detailed design specifications

**Skills**:
- [HomeBudget wrapper](../skills/homebudget/SKILL.md)
- Python conventions: see user-level .copilot skills configuration
- Documentation conventions: see user-level .copilot skills configuration

**Environment**:
- [docs/environment.md](../../docs/environment.md)



