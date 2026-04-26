# Test-Driven Development Strategy

**Document Type**: Testing Strategy  
**Status**: Active  
**Last updated**: 2026-03-08  
**Purpose**: Define comprehensive TDD testing strategy for monthly closing workflow implementation

---

## Table of Contents

- [Overview](#overview)
- [Testing Philosophy](#testing-philosophy)
- [Test Types and Taxonomy](#test-types-and-taxonomy)
- [Coverage Targets and Quality Gates](#coverage-targets-and-quality-gates)
- [Test Infrastructure and Tooling](#test-infrastructure-and-tooling)
- [Test Data Strategy](#test-data-strategy)
- [Phase-Based Acceptance Criteria](#phase-based-acceptance-criteria)
- [UAT Hybrid Automation Framework](#uat-hybrid-automation-framework)
- [Rollback and Safety Mechanisms](#rollback-and-safety-mechanisms)
- [CI/CD Integration](#cicd-integration)
- [Test Maintenance and Evolution](#test-maintenance-and-evolution)

---

## Overview

This document defines the test-driven development (TDD) strategy for implementing the financial statements application. The strategy balances rapid iteration with rigorous quality assurance through a hybrid approach: **SIT (System Integration Testing)** with mock data for core logic validation, and **UAT (User Acceptance Testing)** with real data sources for end-to-end workflow verification.

### Key Principles

1. **Test First**: Write tests before implementation (strict TDD discipline)
2. **Phase Gating**: Complete all Phase N tests before starting Phase N+1 implementation
3. **Tiered Coverage**: Higher standards for domain logic (90%) vs. adapters (70%) vs. orchestration (60%)
4. **Hybrid Validation**: SIT for algorithm correctness + UAT for integration verification
5. **Safe UAT**: Transaction-based rollback for all UAT tests on live databases
6. **Deterministic Fixtures**: Synthetic test data using real account names and categories

### Related Documentation

- [TDD Implementation Plan](../../../.github/prompts/plan-closing-tdd-implementation.prompt.md) â€” Phase-by-phase implementation roadmap
- [App Architecture](../design/app-architecture.md) â€” Layer boundaries and module contracts
- [App Workflows](../design/app-workflows.md) â€” Target automated workflows
- [Domain Model](../design/domain-model.md) â€” Core entities and business rules
- [Module Design](../design/module-design.md) â€” Interface specifications

---

## Testing Philosophy

### TDD Contract

Every feature follows this strict cycle:

1. **Design Phase**: Review specifications and define acceptance criteria
2. **Test Design Phase**: Write test cases (SIT + UAT) based on acceptance criteria
3. **Build Phase**: Implement minimal code to pass tests
4. **Validate Success**: Run tests and confirm all pass for both positive and negative scenarios
5. **Refactor**: Improve code clarity while maintaining green tests
6. **Phase Gate**: Measure coverage, check quality gates, document residual risks

### Why TDD for This Project

Financial applications demand high correctness:

- **Accounting precision**: Rounding errors compound across transactions
- **Data integrity**: Multi-source reconciliation requires exact matching
- **Audit trail**: Every mutation must be traceable and reversible
- **Regulatory compliance**: Financial statements must be reproducible
- **Edge cases**: Real-world data has endless corner cases (forex, pending txns, duplicates)

TDD ensures:

- Edge cases are codified as test scenarios
- Refactoring doesn't break accounting logic
- New features don't regress existing workflows
- Documentation stays synchronized with implementation

---

## Test Types and Taxonomy

### SIT - System Integration Testing

**Purpose**: Validate core business logic in isolation using controlled mock data

**Characteristics**:

- **Fully automated**: No user input required
- **Fast execution**: All tests complete in < 5 minutes
- **Deterministic**: Same inputs always produce same outputs
- **Mock data sources**: Physical mock SQLite databases (DB artifacts gitignored), mocked Google Sheets responses, synthetic HomeBudget fixtures
- **No external dependencies**: No network calls, no remote I/O
- **Safe to run repeatedly**: No side effects on production databases, test DBs are isolated and regenerated as needed

**Test Levels**:

1. **Unit Tests** (tests/unit/)
   - Test individual functions and classes in isolation
   - Mock all external dependencies (DBs, APIs, file system)
   - Examples: Period validation, Money arithmetic, account type detection
   - Target coverage: 90%+ for domain modules
2. **Integration Tests** (tests/integration/)
   - Test module interactions with mocked adapters
   - Validate data flow between layers
   - Examples: Reconciliation algorithm with mock statement data, bill payment with mock parser
   - Target coverage: 70%+ for cross-module logic
3. **End-to-End SIT** (tests/e2e/sit/)
   - Test complete workflow with all mocks
   - Simulate monthly closing from start to finish
   - Examples: Full closing workflow with synthetic period data
   - Target coverage: 60%+ for orchestration logic

**When to Use SIT**:

- Core domain logic (reconciliation algorithm, forex calculations)
- Adapter logic (statement parsing, Google Sheets range extraction, S3 upload)
- Utility functions (Period, Money, validation)
- Error handling and exception paths
- Edge cases (duplicate transactions, missing data, tolerance violations)

---

### UAT - User Acceptance Testing

**Purpose**: Verify real-world integration with actual data sources and manual user workflows

**Characteristics**:

- **Hybrid automation**: Scripted prompts for user input, automated verification
- **Slower execution**: May require manual steps (download statements, count cash, check balances)
- **Non-deterministic**: Depends on current state of HomeBudget, Google Sheets, live APIs
- **Real data sources**: Actual HomeBudget DB, Google Sheets workbooks, bank statement files
- **Safe rollback**: All mutations wrapped in transactions, auto-rollback on failure
- **User verification checkpoints**: Prompt user to validate results at key steps

**Test Structure**:

UAT tests follow a **guided script pattern**:

```python
def test_uat_cash_reconcile_february_2026():
    """UAT: Cash reconciliation for Feb 2026 with real data sources."""
    
    # Phase 1: Setup and user inputs
    print("\n=== UAT: Cash Reconciliation ===")
    cash_count = prompt_user_input(
        "Enter physical cash count (SGD): ",
        validator=validate_positive_decimal
    )
    
    # Phase 2: Automated data fetch
    with uat_transaction_scope():  # Auto-rollback on failure
        hb_balance = homebudget.query_balance("Cash TWH SGD", date.today())
        sheet_expenses = gsheet.fetch_range("cash-expenses", "recent_txns")
        
        # Phase 3: Execute business logic
        reconciliation = reconcile_cash(cash_count, hb_balance, sheet_expenses)
        
        # Phase 4: User verification checkpoint
        print(f"\nReconciliation variance: {reconciliation.variance} SGD")
        if abs(reconciliation.variance) > 20.00:
            print("WARNING: Variance exceeds tolerance!")
        
        user_approval = prompt_user_confirmation(
            "Create adjustment transaction? (y/n): "
        )
        
        if user_approval:
            # Phase 5: Mutation with audit trail
            txn_id = homebudget.add_transaction(reconciliation.adjustment_txn)
            print(f"âœ“ Created adjustment transaction: {txn_id}")
            
            # Phase 6: Final verification
            new_balance = homebudget.query_balance("Cash TWH SGD", date.today())
            assert abs(new_balance - cash_count) < 0.01, "Balance mismatch after adjustment!"
        else:
            raise UserRejectedError("User declined adjustment transaction")
```

**When to Use UAT**:

- Adapter verification (HomeBudget read/write, Google Sheets API, S3 upload/delete)
- End-to-end workflow validation (full monthly closing)
- User checkpoint testing (tolerance alerts, manual overrides)
- Data migration verification (workbook-to-SQLite backfill)
- Real data edge cases (discovered during manual testing)

**UAT Execution Frequency**:

- **Per phase**: At least one UAT per major feature (adapters, reconciliation, statements)
- **Pre-release**: Full UAT suite before merging to main branch
- **On-demand**: When investigating production issues or validating manual data fixes

---

### Test Type Selection Matrix

| Component                                    |           |           |
| -------------------------------------------- | --------- | --------- |
| SIT                                          |           |           |
| UAT                                          |           |           |
| Rationale                                    |           |           |
| **Core domain (accounting, reconciliation)** | âœ“âœ“âœ“ | âœ“       |
| **Adapters (HomeBudget, GSheet, parsers)**   | âœ“âœ“    | âœ“âœ“    |
| **Orchestration (workflow runner, CLI)**     | âœ“       | âœ“âœ“    |
| **Validation and error handling**            | âœ“âœ“âœ“ | âœ“       |
| **Report generation**                        | âœ“âœ“    | âœ“       |
| **Data migration**                           | âœ“       | âœ“âœ“âœ“ |

| Component                                    |                                                  |
| -------------------------------------------- | ------------------------------------------------ |
| SIT                                          |                                                  |
| UAT                                          |                                                  |
| Rationale                                    |                                                  |
| **Core domain (accounting, reconciliation)** | SIT primary, UAT for integration confidence      |
| **Adapters (HomeBudget, GSheet, parsers)**   | SIT for parsing logic, UAT for API contracts     |
| **Orchestration (workflow runner, CLI)**     | SIT for happy path, UAT for user interaction     |
| **Validation and error handling**            | SIT for all error paths, UAT for user messaging  |
| **Report generation**                        | SIT for calculations, UAT for PDF/export formats |
| **Data migration**                           | UAT critical for one-time backfill operations    |

---

## Coverage Targets and Quality Gates

### Tiered Coverage Policy

Different standards apply to different layers based on business risk and complexity:

| Layer             |     |      |                                                                           |
| ----------------- | --- | ---- | ------------------------------------------------------------------------- |
| Minimum Coverage  |     |      |                                                                           |
| Target Coverage   |     |      |                                                                           |
| Rationale         |     |      |                                                                           |
| **Domain Logic**  | 85% | 90%+ | Core accounting rules and reconciliation algorithm are high-risk          |
| **Adapters**      | 65% | 70%+ | Data access logic has external dependencies, harder to cover exhaustively |
| **Orchestration** | 50% | 60%+ | Workflow coordination has many UI/CLI paths, focus on critical flows      |
| **Utilities**     | 80% | 85%+ | Shared utilities should be bulletproof since many modules depend on them  |

### Phase Gate Quality Criteria

Before advancing from Phase N to Phase N+1, all criteria must be met:

#### Phase Completion Checklist

- [ ] **All tests pass**: Both SIT and UAT test suites green
- [ ] **Coverage targets met**: Measured with `pytest --cov`
- [ ] **No critical linting errors**: `black`, `flake8`, `mypy` clean
- [ ] **Documentation updated**: Docstrings, README, design docs reflect implementation
- [ ] **Manual UAT executed**: At least one successful UAT run with real data
- [ ] **Residual risks documented**: Known limitations and future work noted
- [ ] **Code review approved**: Peer review for accounting logic and data mutations

#### Coverage Measurement Commands

```bash
# Full coverage report
pytest --cov=src/python --cov-report=term-missing

# Per-module coverage
pytest --cov=src/python/closing/accounting --cov-report=term-missing tests/unit/accounting/

# Coverage delta (run before/after implementation)
pytest --cov=src/python --cov-report=html
# Open htmlcov/index.html to identify gaps
```

#### Coverage Exemptions

Some code paths are exempt from coverage requirements:

1. **Defensive error handling**: Unreachable paths for malformed inputs (validated upstream)
2. **Logging and debug statements**: Non-functional code for diagnostics
3. **Legacy compatibility shims**: Temporary code for migration, marked with TODO
4. **CLI help text**: Static documentation strings
5. **Type checking branches**: `if TYPE_CHECKING:` blocks

Mark exemptions with `# pragma: no cover` comments:

```python
def post_transaction(account: str, amount: float):
    if amount == 0:  # pragma: no cover - validated upstream
        raise ValueError("Zero amount not allowed")
```

---

## Test Infrastructure and Tooling

### Testing Stack

- **Test Runner**: pytest >= 7.0
- **Coverage**: pytest-cov >= 4.0
- **Mocking**: pytest-mock, unittest.mock
- **Fixtures**: pytest fixtures with autouse and scope management
- **Assertions**: pytest assertions with detailed failure messages
- **Formatting**: black >= 23.0 (consistent code style)
- **Linting**: flake8 >= 6.0 (code quality)
- **Type Checking**: mypy (static type validation - optional but recommended)

### Directory Structure

```
tests/
â”œâ”€â”€ .test_data/                 # Mock databases (DB artifacts gitignored)
â”‚   â”œâ”€â”€ mock_homebudget.db      # Mock HomeBudget SQLite database
â”‚   â”œâ”€â”€ mock_app.db             # Mock app SQLite database
â”‚   â””â”€â”€ README.md               # Database initialization documentation
â”œâ”€â”€ conftest.py                 # Shared fixtures and configuration
â”œâ”€â”€ fixtures/                   # Test data fixtures
â”‚   â”œâ”€â”€ accounts.json           # Synthetic account metadata (real names)
â”‚   â”œâ”€â”€ categories.json         # Synthetic HomeBudget categories (real names)
â”‚   â”œâ”€â”€ transactions.json       # Deterministic transaction fixtures
â”‚   â”œâ”€â”€ statements/             # Mock bank statement files
â”‚   â””â”€â”€ reconciliation/         # Reconciliation test scenarios
â”œâ”€â”€ unit/                       # Unit tests (L1: isolated functions/classes)
â”‚   â”œâ”€â”€ test_types.py
â”‚   â”œâ”€â”€ test_period.py
â”‚   â”œâ”€â”€ accounting/
â”‚   â”œâ”€â”€ reconciliation/
â”‚   â””â”€â”€ ...
â”œâ”€â”€ integration/                # Integration tests (L2: module interactions)
â”‚   â”œâ”€â”€ test_reconcile_workflow.py
â”‚   â”œâ”€â”€ test_bill_payment_flow.py
â”‚   â””â”€â”€ ...
â”œâ”€â”€ e2e/                        # End-to-end tests
â”‚   â”œâ”€â”€ sit/                    # SIT: Full workflows with mocks
â”‚   â”‚   â””â”€â”€ test_closing_workflow_sit.py
â”‚   â””â”€â”€ uat/                    # UAT: Hybrid scripts with real data
â”‚       â”œâ”€â”€ test_adapters_uat.py
â”‚       â”œâ”€â”€ test_closing_workflow_uat.py
â”‚       â””â”€â”€ uat_helpers.py      # User prompt utilities
â””â”€â”€ test_helpers/               # Test utilities (mocks, builders, assertions)
    â”œâ”€â”€ mock_homebudget.py
    â”œâ”€â”€ mock_gsheet.py
    â”œâ”€â”€ builders.py             # Fixture builders (fluent API)
    â””â”€â”€ assertions.py           # Custom assertion helpers
```

### Shared Fixtures (tests/conftest.py)

Key pytest fixtures used across test suites:

```python
@pytest.fixture
def mock_period():
    """Standard test period (Feb 2026)."""
    return Period(year=2026, month=2)

@pytest.fixture
def mock_accounts():
    """Load synthetic account metadata from fixtures/accounts.json."""
    # Uses real HomeBudget account names but with controlled balances

@pytest.fixture(scope="session")
def mock_homebudget_db():
    """Physical mock SQLite DB with HomeBudget schema and test data.
    
    Database location: tests/.test_data/mock_homebudget.db
    The generated DB artifact is gitignored and recreated on each test session.
    """
    # Populated from fixtures/transactions.json

@pytest.fixture
def mock_gsheet_client():
    """Mocked Google Sheets client with canned responses."""
    # Returns deterministic data from fixtures/

@pytest.fixture(scope="function")
def uat_transaction_scope():
    """Context manager for UAT with auto-rollback on failure."""
    # Wraps real HomeBudget DB mutations in BEGIN/ROLLBACK
```

---

## Test Data Strategy

### Synthetic Data with Real Schema

**Decision**: Use programmatically generated deterministic fixtures that mirror the structure of real HomeBudget data but with controlled, predictable values.

**Rationale**:

- **Deterministic**: Same test always produces same result
- **Reviewable**: Fixtures are human-readable JSON, easy to audit
- **Edge case coverage**: Explicitly codify corner cases (duplicates, negatives, forex, pending)
- **Realistic schema**: Use actual account names and categories from HomeBudget export

### Fixture Sources

1. **Account metadata** (fixtures/accounts.json)
   - Exported from `data/monthly-closing/accounts.json` (source of truth)
   - Real account names: "Cash TWH SGD", "TWH DBS Multi SGD", "IB POSITION USD", etc.
   - Controlled balances: Round numbers for easy mental arithmetic
2. **Category hierarchy** (fixtures/categories.json)
   - Exported from HomeBudget category list
   - Real category names: "Groceries", "Transport", "Professional Services:Currency Conversion"
   - Includes subcategory relationships
3. **Transaction templates** (fixtures/transactions.json)
   - Synthetic transactions with realistic patterns
   - Covers: income, expenses, transfers, forex, pending, duplicates
   - Controlled timestamps: Sequential dates within test period
   - Known variance scenarios: Â±$0.01 rounding, Â±$5 reconciliation gap
4. **Statement files** (fixtures/statements/)
   - Minimal CSV/XLSX files for parser testing
   - One file per supported bank format (DBS, UOB, Citi, BOA, IBKR)
   - Contains 5-10 transactions with known checksums

### Fixture Maintenance

**Update triggers**:

- HomeBudget schema change (new account types, category structure)
- New bank statement format support
- New reconciliation edge case discovered in production

**Update process**:

1. Export real data subset with sensitive values masked
2. Simplify to minimal reproducing scenario
3. Add to fixtures/ with descriptive naming
4. Update fixture documentation in fixtures/README.md

### Mock Database Management

**Purpose**: Use physical SQLite databases for SIT tests instead of in-memory databases to enable inspection, debugging, and more realistic test scenarios.

**Database Location**: `tests/.test_data/`

All mock databases are stored in this directory. Only generated DB artifacts are gitignored to avoid committing ephemeral files to version control.

**Mock Databases**:

1. **mock_homebudget.db** â€” HomeBudget schema with synthetic transaction data
   - Mimics real HomeBudget database structure
   - Populated from `fixtures/transactions.json`
   - Includes accounts, categories, transactions, tags
   - Recreated per test session for deterministic state
2. **mock_app.db** â€” Application SQLite database with session/state data
   - Financial statements snapshots
   - Session management tables
   - Reconciliation decision log
   - Exchange rate cache
   - Recreated per test session

**Database Lifecycle**:

```python
# tests/conftest.py

@pytest.fixture(scope="session", autouse=True)
def setup_test_databases():
    """Initialize mock databases at session start, clean up at session end."""
    test_data_dir = Path(__file__).parent / ".test_data"
    test_data_dir.mkdir(exist_ok=True)
    
    # Remove old databases from previous session
    for db_file in test_data_dir.glob("*.db"):
        db_file.unlink()
    
    # Initialize mock HomeBudget database
    mock_hb_path = test_data_dir / "mock_homebudget.db"
    initialize_homebudget_schema(mock_hb_path)
    load_fixtures_into_db(mock_hb_path, "fixtures/transactions.json")
    
    # Initialize mock app database
    mock_app_path = test_data_dir / "mock_app.db"
    initialize_app_schema(mock_app_path)
    
    yield
    
    # Optional: Clean up after session (or leave for debugging)
    # for db_file in test_data_dir.glob("*.db"):
    #     db_file.unlink()

@pytest.fixture(scope="function")
def mock_homebudget_db():
    """Return path to mock HomeBudget database, reset state per test."""
    db_path = Path(__file__).parent / ".test_data" / "mock_homebudget.db"
    
    # Reset to baseline state (rollback any previous test mutations)
    reset_database_to_fixtures(db_path)
    
    return str(db_path)
```

**Advantages of Physical Mock Databases**:

1. **Debuggability**: Inspect database with SQLite browser after test failure
2. **Realism**: Closer to production behavior (file locks, transactions, constraints)
3. **Performance**: Session-scoped databases persist across tests (faster than recreating in-memory DB each time)
4. **Isolation**: Each test function can reset to baseline without affecting others
5. **Inspection**: Query database state mid-test with SQL tools for debugging

**Gitignore Configuration**:

```gitignore
# Test mock databases
tests/.test_data/*.db
tests/.test_data/*-journal.db
tests/.test_data/*-shm.db
tests/.test_data/*-wal.db
```

This ensures:

- Mock databases never committed to version control
- SQLite journal/WAL files excluded
- Clean git status during test development

**Database Reset Strategies**:

- **Session reset** (autouse fixture): Delete and recreate all databases at test session start
- **Function reset** (per-test fixture): Rollback to baseline fixture state between tests
- **Manual reset**: Developer can delete `tests/.test_data/` to force clean rebuild

**Documentation**:

Create `tests/.test_data/README.md` to document:

- Database schema sources
- Fixture loading procedure
- How to inspect databases for debugging
- How to manually reset if tests fail

---

## Phase-Based Acceptance Criteria

Phase-by-phase testing scope, detailed per-phase test focus, and evolving acceptance criteria are maintained in a separate document:

- [Phase-Based Testing Acceptance Criteria](test-phase-acceptance-criteria.md)

Use this split to keep strategy guidance stable while allowing implementation-phase criteria to evolve independently.

---

## UAT Hybrid Automation Framework

### User Prompt Utilities (tests/e2e/uat/uat_helpers.py)

Standardized functions for structured user input during UAT:

```python
def prompt_user_input(prompt: str, validator: Callable[[str], bool] = None) -> str:
    """Prompt user for text input with optional validation."""
    while True:
        value = input(prompt)
        if validator is None or validator(value):
            return value
        print("Invalid input, please try again.")

def prompt_user_confirmation(prompt: str) -> bool:
    """Prompt user for yes/no confirmation."""
    response = input(prompt).strip().lower()
    return response in ['y', 'yes']

def prompt_decimal_input(prompt: str, min_val: float = None, max_val: float = None) -> float:
    """Prompt user for decimal number with range validation."""
    # Implementation with validation loop

def display_data_table(data: List[Dict], headers: List[str] = None):
    """Display tabular data for user review (e.g., parsed bill line items)."""
    # Pretty-print table to console

class UserRejectedError(Exception):
    """Raised when user declines a UAT checkpoint."""
    pass
```

### UAT Transaction Scope (tests/conftest.py)

Context manager for safe UAT execution with automatic rollback:

```python
@pytest.fixture
def uat_transaction_scope():
    """
    Context manager for UAT tests that wraps mutations in a transaction.
    
    Usage:
        with uat_transaction_scope():
            # Perform mutations on live HomeBudget DB
            hb.add_transaction(...)
            
            # If test fails or user declines, auto-rollback
            if not user_approves:
                raise UserRejectedError()
            
            # Explicit commit required to persist
            uat_transaction_scope.commit()
    """
    import sqlite3
    
    conn = sqlite3.connect(HOMEBUDGET_DB_PATH)
    conn.execute("BEGIN TRANSACTION")
    
    class TransactionScope:
        def __init__(self, connection):
            self.conn = connection
            self._committed = False
        
        def commit(self):
            self.conn.commit()
            self._committed = True
        
        def rollback(self):
            self.conn.rollback()
        
        def __enter__(self):
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            if not self._committed or exc_type is not None:
                self.conn.rollback()
                print("\nâš ï¸  Transaction rolled back (no changes persisted)")
            else:
                print("\nâœ“ Transaction committed successfully")
            self.conn.close()
    
    return TransactionScope(conn)
```

### UAT Test Template

Standard structure for all UAT tests:

```python
def test_uat_[feature_name]_[period]():
    """
    UAT: [Feature description]
    
    Prerequisites:
    - [List manual steps user must complete first]
    
    User Actions Required:
    - [List prompts user will see]
    """
    
    # Phase 1: Setup and prerequisites check
    print("\n" + "="*60)
    print(f"UAT: {feature_name}")
    print("="*60)
    print("\nPrerequisites:")
    print("- [prerequisite 1]")
    print("- [prerequisite 2]")
    
    ready = prompt_user_confirmation("\nAll prerequisites complete? (y/n): ")
    if not ready:
        pytest.skip("User not ready, skipping UAT")
    
    # Phase 2: User inputs
    user_input_1 = prompt_user_input("Enter [data 1]: ", validator=...)
    user_input_2 = prompt_decimal_input("Enter [data 2]: ", min_val=0)
    
    # Phase 3: Automated data fetch and processing
    with uat_transaction_scope() as txn:
        # Fetch from real sources
        data = homebudget.query_[...](...)
        
        # Execute business logic
        result = process_feature(user_input_1, user_input_2, data)
        
        # Phase 4: User verification checkpoint
        display_data_table(result.details)
        print(f"\nResult: {result.summary}")
        
        approval = prompt_user_confirmation("Approve and commit? (y/n): ")
        
        if approval:
            # Phase 5: Mutation and verification
            mutation_result = homebudget.add_method(result.payload)
            print(f"âœ“ Created: {mutation_result.id}")
            
            # Verify mutation succeeded
            verification_data = homebudget.query_method(mutation_result.id)
            assert verification_data is not None
            
            # Explicit commit
            txn.commit()
        else:
            raise UserRejectedError("User declined mutation")
```

### UAT Execution Workflow

1. **Pre-UAT Setup**:
   ```bash
   # Ensure HomeBudget DB is backed up
   cp reference/homebudget/homebudget.db reference/homebudget/homebudget.db.backup
   
   # Set environment variable for UAT mode
   export FINANCIAL_STATEMENTS_UAT_MODE=1
   ```

2. **Run UAT Tests**:
   ```bash
   # Run full UAT suite (interactive)
   pytest tests/e2e/uat/ -v -s
   
   # Run specific UAT test
   pytest tests/e2e/uat/test_cash_reconcile_uat.py::test_uat_cash_reconcile_feb_2026 -v -s
   ```

3. **Post-UAT Verification**:
   - Review HomeBudget app to verify changes (if committed)
   - Check session log for audit trail
   - Compare screenshots/exports before and after UAT

---

## Rollback and Safety Mechanisms

### UAT Rollback Strategy

**Primary Mechanism**: SQLite transaction-based rollback

All UAT mutations wrapped in `BEGIN TRANSACTION` / `ROLLBACK` / `COMMIT`:

```python
# Automatic rollback on test failure
with uat_transaction_scope() as txn:
    homebudget.add_transaction(...)
    # If assertion fails, transaction auto-rolls back

# Manual rollback on user rejection
with uat_transaction_scope() as txn:
    homebudget.add_transaction(...)
    if not prompt_user_confirmation("Commit?"):
        raise UserRejectedError()  # Triggers rollback
    txn.commit()  # Explicit commit required
```

**Why This Approach**:

- âœ“ **Automatic**: No manual cleanup scripts needed
- âœ“ **Atomic**: All-or-nothing, no partial mutations
- âœ“ **Fast**: SQLite transactions are instant
- âœ“ **Safe**: Zero risk of corrupting HomeBudget DB
- âœ“ **Auditable**: Transaction log captures all attempts

**HomeBudget Wrapper Requirements**:

The homebudget Python package must support passing an existing SQLite connection:

```python
# Standard usage (auto-commit)
homebudget.add_transaction(...)

# UAT usage (manual transaction control)
conn = sqlite3.connect(HOMEBUDGET_DB_PATH)
conn.execute("BEGIN TRANSACTION")
homebudget.add_transaction(..., connection=conn)
conn.rollback()  # or conn.commit()
```

**Fallback Mechanism**: Backup/Restore

If homebudget wrapper doesn't support manual transactions:

```python
import shutil
from pathlib import Path

@pytest.fixture
def uat_backup_restore():
    """Backup HomeBudget DB before UAT, restore on failure."""
    db_path = Path("reference/homebudget/homebudget.db")
    backup_path = Path("reference/homebudget/homebudget.db.uat_backup")
    
    # Backup
    shutil.copy2(db_path, backup_path)
    
    yield
    
    # Restore on failure (if backup still exists)
    if backup_path.exists():
        shutil.copy2(backup_path, db_path)
        backup_path.unlink()
        print("\nâš ï¸  HomeBudget DB restored from backup")
```

### Data Integrity Safeguards

**Pre-mutation Validation**:

- Balance equation checks (assets = liabilities + equity)
- Double-entry validation (transaction pairs balance)
- Uniqueness constraints (no duplicate transaction IDs)
- Foreign key integrity (account/category references exist)

**Post-mutation Verification**:

- Query back committed data and verify fields
- Recalculate balances and compare to expected
- Check audit log for mutation record

**User Confirmation Checkpoints**:

- Show summary of changes before commit
- Highlight high-risk mutations (e.g., large adjustments, category changes)
- Require explicit "yes" for irreversible operations

---

## CI/CD Integration

### Automated Test Execution

**On every commit** (GitHub Actions or local pre-commit hook):

```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e .[dev]
      - name: Run SIT tests
        run: pytest tests/unit tests/integration tests/e2e/sit -v --cov=src/python --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

**Pre-release UAT** (manual trigger):

```bash
# Local UAT execution before merging to main
pytest tests/e2e/uat/ -v -s --uat-period=2026-02
```

### Coverage Enforcement

**GitHub Actions**: Fail CI if coverage drops below threshold

```yaml
- name: Check coverage threshold
  run: |
    pytest --cov=src/python --cov-fail-under=70
```

**Pre-commit hook**: Remind developer to run tests before committing

```bash
#!/bin/sh
# .git/hooks/pre-commit
pytest tests/unit tests/integration -q
if [ $? -ne 0 ]; then
  echo "Tests failed, commit blocked. Fix tests or use --no-verify to override."
  exit 1
fi
```

---

## Test Maintenance and Evolution

### When to Update Tests

**Trigger scenarios**:

1. **Design change**: Acceptance criteria or algorithm updated
2. **Bug fix**: Add regression test before fixing bug
3. **New feature**: Write tests first (TDD)
4. **Refactoring**: Tests should remain green (if not, tests are too coupled to implementation)
5. **Data schema change**: Update fixtures to match new structure
6. **External API change**: Update mocks to reflect new API contract

### Test Refactoring Guidelines

**Prefer declarative over imperative**:
```python
# Bad: Tightly coupled to implementation
def test_reconcile():
    ledger = MockLedger()
    ledger.add_row(date="2026-02-01", amount=100)
    statement = MockStatement()
    statement.add_row(date="2026-02-01", amount=100)
    reconciler = Reconciler()
    result = reconciler.match(ledger.rows, statement.rows)
    assert len(result.matched) == 1
    assert result.matched[0].ledger_row.amount == 100

# Good: Focused on business outcome
def test_reconcile_exact_match():
    scenario = ReconciliationScenario(
        ledger_txns=[txn(date="2026-02-01", amount=100)],
        statement_txns=[txn(date="2026-02-01", amount=100)]
    )
    result = reconcile(scenario)
    assert_exact_match(result, count=1)
```

**Use fixture builders for complex setup**:
```python
# tests/test_helpers/builders.py
class TransactionBuilder:
    def __init__(self):
        self._date = date.today()
        self._amount = 0.0
        self._description = "Test transaction"
    
    def on_date(self, date_val):
        self._date = date_val
        return self
    
    def for_amount(self, amount):
        self._amount = amount
        return self
    
    def build(self):
        return Transaction(date=self._date, amount=self._amount, description=self._description)

# Usage in tests
def test_transaction_matching():
    ledger_txn = TransactionBuilder().on_date("2026-02-01").for_amount(100).build()
    statement_txn = TransactionBuilder().on_date("2026-02-01").for_amount(100).build()
    # ...
```

**Extract custom assertions**:
```python
# tests/test_helpers/assertions.py
def assert_balance_equation(accounts: List[Account]):
    """Verify assets = liabilities + equity."""
    assets = sum(a.balance for a in accounts if a.type == AccountType.ASSET)
    liabilities = sum(a.balance for a in accounts if a.type == AccountType.LIABILITY)
    equity = sum(a.balance for a in accounts if a.type == AccountType.EQUITY)
    
    assert abs(assets - (liabilities + equity)) < 0.01, \
        f"Balance equation violated: {assets} != {liabilities} + {equity}"
```

### Deprecated Test Cleanup

**When to remove tests**:

- Feature permanently removed (not just refactored)
- Test duplicates another test with no added value
- Test flaky due to timing/environment (replace with deterministic version)

**Deprecation process**:

1. Mark test with `@pytest.mark.skip(reason="Deprecated: [explanation]")`
2. Document deprecation in commit message
3. Remove after 1 month (ensure no dependencies)

---

## Appendix: Test Execution Reference

### Quick Commands

```bash
# Run all SIT tests
pytest tests/unit tests/integration tests/e2e/sit -v

# Run specific module tests
pytest tests/unit/accounting/ -v

# Run with coverage
pytest --cov=src/python --cov-report=term-missing

# Run fast (skip slow tests)
pytest -m "not slow"

# Run UAT for specific feature
pytest tests/e2e/uat/test_cash_reconcile_uat.py -v -s

# Run in watch mode (auto-rerun on file change)
pytest-watch
```

### Debugging Failed Tests

```bash
# Show print statements and verbose output
pytest tests/unit/test_reconcile.py -v -s

# Drop into debugger on failure
pytest tests/unit/test_reconcile.py --pdb

# Show local variables in traceback
pytest tests/unit/test_reconcile.py -l

# Re-run only failed tests
pytest --lf
```

### Coverage Analysis

```bash
# HTML coverage report (detailed line-by-line)
pytest --cov=src/python --cov-report=html
open htmlcov/index.html

# Coverage for specific module
pytest --cov=src/python/closing/reconciliation --cov-report=term-missing

# Coverage delta (compare before/after refactoring)
pytest --cov=src/python --cov-report=json -o coverage.json
# ... make code changes ...
pytest --cov=src/python --cov-report=json -o coverage_new.json
diff coverage.json coverage_new.json
```

---

## Document Maintenance

**Owner**: Test Agent (test-agent mode)  
**Review Frequency**: After each implementation phase completion  
**Update Triggers**:

- Phase gate criteria change
- New test type or pattern introduced
- Coverage targets adjusted
- UAT framework enhanced

**Version History**:

- v1.0 (2026-03-08): Initial strategy document created
