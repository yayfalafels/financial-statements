---
title: Reconciliation Engine - Module Layout Design Summary
doc_type: design
topic_type: specification
owner: sqlite-adapter-agent
scope: POC close-session
last_updated: 2026-05-03
status: draft
---

# Reconciliation Engine - Module Layout Design Summary

## Overview

This document summarizes the module layout specification for the `reconciliation_engine` package within the `close_session` module. The layout implements a layered architecture with clean separation of concerns across models, methods, utilities, shared adapters, and configuration.

**Output format:** Complete JSON specification in `reconciliation-engine-module-layout.json` (planned artifact; not yet checked in)

---

## Design Principles

### 1. Layered Dependency Flow (Strict Acyclic)

```
Layer 5: engine.py (orchestration, calls all layers)
   ↓
Layer 4: shared adapters (app-wide persistence and external integration)
   ↓
Layer 3: methods/ (algorithms, transaction-level and balance-level)
   ↓
Layer 2: utilities/ (helpers, gap calc, heuristics, slice builder)
   ↓
Layer 1: models/ (data structures, enums, domain entities)
```

**Key invariants:**
- Models have NO external dependencies (pure data containers)
- Utilities depend on models only
- Methods depend on models and utilities (NOT on adapters or engine)
- Shared adapters depend on models only (NOT on methods or engine)
- Engine depends on all layers but contains NO algorithm logic

**Rationale:** This layering preserves testability, reusability, and separation of concerns. Methods can be tested in isolation from persistence. Shared adapters can be swapped without touching methods.

### 2. Method Dispatch via Account-Group Classification

Account group classification is **owned by the engine**, not by callers.

```
Caller requests: engine.reconcile(account, year, month, ...)
  ↓
Engine classifies account group (bank, cash, homebudget_native, cpf, manual_input)
  ↓
Engine instantiates correct method (TransactionLevelMethod or BalanceLevelMethod)
  ↓
Engine invokes method.reconcile(...)
  ↓
Method returns ReconciliationResult
```

**Account group → Method mapping:**
- **Bank statement-process** (DBS, CITI, UOB, Visa): `TransactionLevelMethod`
- **Cash** (physical wallet): `BalanceLevelMethod`
- **HomeBudget-native** (no external statement): `BalanceLevelMethod`
- **CPF** (roll-forward): `BalanceLevelMethod`
- **Manual-input** (wallets): `BalanceLevelMethod`
- **IBKR** (routed to separate integration agent, not reconciliation engine)

### 3. Heuristics as Configuration, Not Code

Heuristics rules and parameters are **loaded from JSON at runtime**, not hardcoded.

```
txn_heuristics.json
  ├── matching_config.default (date_tolerance_days: 3, amount_tolerance: 0.01)
  ├── matching_config.accounts (account overrides, e.g., UOB: 5 days)
  ├── general_heuristics (applied to all accounts)
  │   ├── net_zero_pair
  │   └── same_amount_zero_sum_cluster
  └── account_heuristics (account-specific rules)
      ├── TWH DBS Multi SGD → cpf_net_zero
      └── TWH UOB One SGD → uob_cashback_split
```

**Config discovery precedence:**
1. Check `matching_config.accounts[account]` for account-specific override
2. Fall back to `matching_config.default`
3. Collect all `general_heuristics`
4. Collect `account_heuristics[account]`
5. Apply heuristics in order for determinism

**Rationale:** Configuration-driven approach enables:
- No code changes to add account-specific heuristics
- Deterministic ordering for idempotency
- Auditable parameter values (stored with session metadata)
- Runtime parameter discovery without pre-registration

### 4. Determinism and Idempotency Guarantees

**Reconciliation must be byte-identical across reruns with identical inputs.**

Determinism achieved via:
- **Ledger slice construction:** Deterministic sorting (date ASC, then original index as tie-breaker)
- **Match pairs:** Same forward-pass algorithm with same parameters
- **Heuristics order:** Fixed order from config file, not dynamic
- **Decimal arithmetic:** Exact `decimal.Decimal` throughout (never float)
- **Adjustment ID:** Deterministic hash of `(session_id, account_id, period, rule, gap)`
- **Gap validation:** Same calculation method produces same result

**Idempotency contract for SQLite:**
- Same adjustment_id inserted twice → upsert produces single record
- Statement builder queries are deterministic: same close_book → same statement aggregates
- Session reopened and re-reconciled → identical adjustments with same adjustment_id

---

## Module Structure

### Root: `src/close_session/reconciliation_engine/`

#### Layer 1: Models (`models/`)

**Purpose:** Domain entities and data structures (no algorithms)

| id | file                        | classes                                 | responsibility                  |
| -- | --------------------------- | --------------------------------------- | ------------------------------- |
| 01 | account_group.py            | AccountGroup, AccountGroupClassifier    | account grouping and dispatch   |
| 02 | variance.py                 | VarianceClass, Variance                 | variance type and thresholds    |
| 03 | edits.py                    | EditsRow, EditSet                       | edit rows and gap invariants    |
| 04 | adjustment_transaction.py   | AdjustmentTransaction                   | adjustment contract and status  |
| 05 | reconciliation_session.py   | ReconciliationSession                   | session lineage and checkpoints |

**Key characteristics:**
- Pure data structures (dataclasses or Pydantic models)
- No algorithm logic
- Field validation at construction time
- Immutable audit fields (created_timestamp, adjustment_id)

#### Layer 2: Utilities (`utilities/`)

**Purpose:** Helper functions and utility classes (pure computation)

| id | file                    | classes/functions                     | responsibility                    |
| -- | ----------------------- | ------------------------------------- | --------------------------------- |
| 01 | ledger_slice_builder.py | LedgerSliceBuilder                    | deterministic slice build         |
| 02 | heuristics.py           | HeuristicsEngine, base + rule classes | heuristic reduction and checks    |
| 03 | config_loader.py        | HeuristicsConfigLoader                | config load and precedence        |
| 04 | gap_calculator.py       | compute_gap, validate_*               | gap math and balance validations  |

**Design patterns:**
- Heuristics use abstract base class for extensibility; new heuristics inherit and implement algorithm
- Config discovery is explicit and ordered (account override → default → general + account-specific)
- Gap calculation is pure function with no side effects
- All monetary calculations use `decimal.Decimal`

#### Layer 3: Methods (`methods/`)

**Purpose:** Reconciliation algorithm implementations

| id | file                 | classes                                  | responsibility                     |
| -- | -------------------- | ---------------------------------------- | ---------------------------------- |
| 01 | base.py              | BaseReconciliationMethod, ReconciliationResult | method contract and result model |
| 02 | transaction_level.py | TransactionLevelMethod                   | match, heuristics, edit reduction  |
| 03 | balance_level.py     | BalanceLevelMethod                       | balance variance and adjustments   |

**Method interface (from BaseReconciliationMethod):**
```python
class BaseReconciliationMethod(ABC):
    @abstractmethod
    def reconcile(self, account, year, month, **inputs) -> ReconciliationResult:
        """
        Reconciliation entry point.
        
        Returns: ReconciliationResult with edits, gap, variance_class, adjustment_record.
        """
```

**Correctness assertions (Transaction-level method):**
- Forward pass matches must be deterministic
- Forward edits must produce gap = 0.00
- Backward pass must produce identical edits after heuristics
- Forward == Backward is mandatory; failure → raise `HeuristicsConsistencyError`

#### Layer 4: Shared Adapters (`src/python/adapters/`)

**Purpose:** Persistence and external system integration boundaries

| id | file              | classes                  | responsibility                    |
| -- | ----------------- | ------------------------ | --------------------------------- |
| 01 | sqlite_adapter.py | ReconciliationPersistence | session and adjustment persistence |
| 02 | hb_adapter.py     | HomeBudgetAdapter        | HomeBudget posting integration     |

**Key design decision:** Shared adapters depend on models ONLY (not on methods or engine). This preserves adapter independence: persistence logic is orthogonal to reconciliation algorithms.

**Note:** `sqlite_adapter.py` is a sub-boundary within the larger SQL adapter (per architecture principle "SQLite adapter is the only SQL interface"). It is app-wide and exposes reconciliation-specific operations via scoped interfaces.

#### Layer 5: Orchestration (`engine.py`)

**Purpose:** Reconciliation workflow orchestration

```python
class ReconciliationEngine:
    def reconcile(self, account, year, month, hb_gl, stm_gl, balances) -> ReconciliationResult:
        """
        End-to-end reconciliation:
        1. Classify account group
        2. Create session record
        3. Load config (heuristics, tolerances)
        4. Instantiate and invoke method
        5. Validate results
        6. Generate adjustments if needed
        7. Post to close_book via adapter
        8. Return result + lineage
        """
    
    def approve_adjustment(self, adjustment_id, user_comment) -> AdjustmentTransaction:
        """User approval gate for exceeds-tolerance adjustments."""
    
    def get_session(self, session_id) -> ReconciliationSession:
        """Retrieve session audit trail."""
```

**Engine responsibilities:**
- Account group dispatch logic
- Method polymorphism (select TransactionLevelMethod or BalanceLevelMethod)
- Session lifecycle (create, checkpoint, close)
- Adapter coordination (SQLite, HomeBudget)
- Config loading (heuristics, tolerances)
- Post-processing (adjustment generation, validation, posting)

**Engine does NOT contain:**
- Matching algorithm (in TransactionLevelMethod)
- Gap calculation (in utilities.gap_calculator)
- Heuristic rules (in utilities.heuristics)

#### Configuration (`config/`)

| id | file                  | purpose                              |
| -- | --------------------- | ------------------------------------ |
| 01 | txn_heuristics.json   | heuristic rules and account overrides |
| 02 | tolerance_config.json | tolerance limits and approval policy  |

---

## Data Flow Example: Bank Account Reconciliation

```
Input:
  account = "TWH DBS Multi SGD"
  year = 2026, month = 2
  hb_gl = DataFrame with DBS transactions
  stm_gl = DataFrame with DBS statement
  balances = DataFrame with opening balance

Step 1: Engine.reconcile() entry
  → Create ReconciliationSession record
  → AccountGroupClassifier.classify("TWH DBS Multi SGD") → AccountGroup.BANK

Step 2: Config loading
  → Load txn_heuristics.json
  → discover date_tolerance_days = 3 (no override for DBS, use default)
  → discover heuristics = [net_zero_pair, same_amount_zero_sum_cluster, cpf_net_zero]

Step 3: Method dispatch
  → Instantiate TransactionLevelMethod(heuristics_config)

Step 4: Ledger slice construction
  → LedgerSliceBuilder.build_ledger_slice(hb_gl, "TWH DBS Multi SGD", 2026, 2, balances)
  → Filter out balance rows (txn_type == "balance")
  → Filter out null amounts
  → Sort by date ASC, then by original index
  → Compute running balance
  → Discover opening_balance from balances[2026-01]
  → Return slice with columns: [date, amount, balance, notes, ...]

Step 5: Forward pass matching
  → For each unmatched ledger txn:
    → Find statement txn where amount == amount AND abs(date diff) <= 3 AND exactly one match
    → Mark as matched pair (ledger_idx, stmt_idx)
  → Collect unmatched_ledger and unmatched_stmt indices

Step 6: Forward edits construction
  → For each ledger_idx in unmatched_ledger: add remove edit with edit_amount = -amount
  → For each stmt_idx in unmatched_stmt: add add edit with edit_amount = +amount
  → Compute gap = ledger_end + sum(edit_amount) - statement_end
  → Expected: gap = 0.00 if GL data are consistent

Step 7: Backward pass (correctness check)
  → Start with trivial solution: remove all ledger, add all statement
  → For each forward match (ledger_idx, stmt_idx): remove paired edits from trivial set
  → Result: reduced edit set (should equal forward edits)

Step 8: Heuristics application
  → Apply net_zero_pair: identify opposite-amount edits within 3-day window, remove pairs
  → Apply same_amount_zero_sum_cluster: identify clusters with same amount from mixed sources, check if net sum ≈ 0, remove cluster
  → Apply cpf_net_zero: identify edits with CPF keywords, check if net sum ≈ 0, remove subset
  → Verify: forward_edits_after_heuristics == backward_edits_after_heuristics (mandatory)
  → Verify: sum(edit_amount) = 0.00 for every heuristic subset (gap invariant)

Step 9: Gap validation
  → Compute final gap = ledger_end + sum(all_edit_amount) - statement_end
  → Verify: gap ≈ 0.00 (tolerance 0.01)
  → If gap != 0.00: raise UnresolvedGapError

Step 10: Result classification
  → If gap = 0.00: zero variance → no adjustment needed
  → If gap > 0.01 (exceeds tolerance): create adjustment
    → AdjustmentTransaction(
        adjustment_id = hash(session_id, account, period, rule, gap),
        status = "pending_approval",
        adjustment_amount = abs(gap),
        rule_reference = "bank_unmatched_variance",
        category_code = "Balancing:Unmatched"
      )

Step 11: Posting (if adjustment exists)
  → ReconciliationPersistence.upsert_adjustment(adjustment_record)
  → If status = "pending_approval": await user approval
  → If status = "approved": post to close_book and HB GL via adapters

Step 12: Session closure
  → Update ReconciliationSession with final status, checkpoints, lineage
  → Return ReconciliationResult with edits, gap, matches, metadata, adjustment_id

Output:
  result = ReconciliationResult(
    edits = [EditsRow(...), EditsRow(...), ...],
    gap = 0.00,
    matches = [(ledger_idx, stmt_idx), ...],
    variance_class = VarianceClass.ZERO,
    adjustment_record = None,  # zero variance means no adjustment
    session_id = UUID(...),
    metadata = {
      opening_balance = 10000.00,
      statement_end_balance = 10500.00,
      ledger_end_balance = 10500.00,
      forward_edits_count = 2,
      backward_edits_count = 2,
      heuristics_applied = ["net_zero_pair", "same_amount_zero_sum_cluster"],
      forward_backward_equivalence = true,
      ...
    }
  )
```

---

## Key Design Decisions

### 1. Why Separate TransactionLevelMethod and BalanceLevelMethod?

**Different algorithms, different inputs, different outputs:**

| id | aspect    | transaction-level            | balance-level                 |
| -- | --------- | ---------------------------- | ----------------------------- |
| 01 | input     | ledger and statement txns    | primary and comparison bal    |
| 02 | algorithm | forward/backward + heuristics | balance equation + variance  |
| 03 | output    | edits, gap, matches          | variance class, adjustment    |
| 04 | accounts  | bank statement-process       | cash, cpf, manual, hb-native  |

Both inherit from `BaseReconciliationMethod` for polymorphism, but the inheritance represents "both are reconciliation methods," not code reuse.

### 2. Why Heuristics as Configuration, Not Polymorphic Classes?

**Configuration-driven approach enables:**
- Add new account-specific heuristics without code changes (JSON only)
- Runtime parameter discovery (no pre-registration)
- Deterministic ordering (applied in config file order)
- Auditable parameters (stored with session metadata for reproducibility)
- Easy policy updates (e.g., "UOB date tolerance is now 5 days" → edit JSON)

**Heuristic class hierarchy is for extensibility:**
- `Heuristic (ABC)` defines interface: `apply(edits_set) -> reduced_edits_set, diagnostics`
- `NetZeroPairHeuristic`, `CPFNetZeroHeuristic`, etc. inherit and implement algorithm
- Config file specifies which heuristics to apply in which order
- New heuristic: code a class in heuristics.py, add entry to config JSON, done

### 3. Why Adapters Don't Call Methods or Engine?

**Preserves separation of concerns:**
- Adapters are **pure persistence boundaries**, not workflow orchestrators
- Methods are **pure algorithms**, not persistence providers
- Engine is **orchestration only**, not a god object

**Benefits:**
- Adapter swap: e.g., from SQLite to PostgreSQL adapter with zero method/engine changes
- Method swap: e.g., replace TransactionLevelMethod with improved algorithm; persistence logic unchanged
- Testability: methods can be unit-tested without adapters; adapters can be integration-tested separately

### 4. Why Deterministic Adjustment ID?

**Adjustment ID is hash of `(session_id, account_id, period_key, rule_reference, residual_gap)`:**

```python
adjustment_id = SHA256(
    f"{session_id}:{account_id}:{period_key}:{rule_reference}:{gap_amount}"
)
```

**Enables:**
- **Idempotency:** Same reconciliation session produces same adjustment_id
- **Upsert safety:** Insert same adjustment twice → single record (no duplicate)
- **Audit trail:** adjustment_id is stable across runs; session replay produces same record
- **No database sequence dependency:** adjustment_id is deterministic, not auto-increment

### 5. Why Session Record Required?

**Reconciliation audit is complex; session record captures:**
- **Lineage:** which statement version, which HB sync, which algorithm version
- **Checkpoints:** timestamps for validation pass, matching complete, variance evaluated, approval, posting
- **Metadata:** heuristics applied, parameters used, forward_backward_equivalence result
- **Traceability:** session_id links to adjustment records, bill conflicts, close-book entries

**Query use cases:**
- "What happened during Feb 2026 reconciliation for DBS account?" → fetch ReconciliationSession(2026-02, DBS)
- "Which adjustment was approved on 2026-05-03?" → query by user_approval_timestamp
- "Replay Feb 2026 reconciliation?" → read session metadata, verify outcome reproducibility

---

## Testing Strategy

### Unit Tests (layers 1-4)

| id | layer     | tests                               | examples                                  |
| -- | --------- | ----------------------------------- | ----------------------------------------- |
| 01 | models    | field validation, enum lifecycle    | test_adjustment_transaction.py            |
| 02 | utilities | pure contracts, edge cases, decimal | test_gap_calculator.py                    |
| 03 | methods   | algorithm correctness, determinism  | test_transaction_level_method.py          |
| 04 | adapters  | persistence, idempotency, errors    | test_sqlite_adapter.py                    |

Additional layer examples:
- utilities: test_ledger_slice_builder.py
- methods: test_balance_level_method.py
- adapters: test_hb_adapter.py

### Integration Tests (Layer 5)

| id | test                     | scope                            | examples                                  |
| -- | ------------------------ | -------------------------------- | ----------------------------------------- |
| 01 | end-to-end workflow      | full reconciliation path         | test_integration_bank_account.py          |
| 02 | determinism verification | same input, identical output     | rerun twice, compare result hash          |
| 03 | idempotency verification | upsert keeps one persisted row   | post twice, verify close_book count = 1   |
| 04 | account-group dispatch   | correct method chosen by account | mock method, verify chosen class          |
| 05 | config discovery         | precedence picks correct values  | verify account override vs default        |

### Validation Tests

| id | validation                   | test                                | purpose                        |
| -- | ---------------------------- | ----------------------------------- | ------------------------------ |
| 01 | gap invariant                | sum(edit_amount) = 0                | heuristics keep gap invariant  |
| 02 | forward-backward equivalence | forward_edits == backward_edits     | catch heuristic drift early    |
| 03 | balance equation             | ledger_end = opening + sum(txn)     | slice build sanity check       |
| 04 | determinism                  | reconcile twice, compare bytes      | rerun safety                   |

---

## Completion Criteria Mapping

| id | criterion                 | location                                 |
| -- | ------------------------- | ---------------------------------------- |
| 01 | design completeness       | models/ + reconciliation.md              |
| 02 | development completeness  | methods/ + utilities/                    |
| 03 | implementation completeness | src/python/adapters/sqlite_adapter.py + engine.py |
| 04 | validation completeness   | tests/ + conftest.py fixtures            |

---

## Next Steps (Post-Design)

1. **Implement models layer** (models/) with Pydantic validation
2. **Implement utilities** (gap_calculator, ledger_slice_builder, heuristics) as pure functions
3. **Implement BaseReconciliationMethod** with full type hints and docstrings
4. **Implement TransactionLevelMethod** (most complex; test thoroughly)
5. **Implement BalanceLevelMethod**
6. **Implement engine.py** orchestration logic
7. **Implement shared adapters** in `src/python/adapters/` (sqlite_adapter, hb_adapter)
8. **Write comprehensive unit and integration tests**
9. **Validate determinism** with test fixtures and rerun verification
10. **Document API** with examples and error handling

---

## References

- [reconciliation.md](reconciliation.md) — Full reconciliation method specifications
- [architecture.md](architecture.md) — System component catalog and principles
- [design-guidelines.md](design-guidelines.md) — Python, API, and naming conventions
- reconciliation-engine-module-layout.json — Planned complete JSON specification artifact
