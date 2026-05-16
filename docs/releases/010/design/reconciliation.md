---
title: Reconciliation Design
doc_type: design
topic_type: owner
owner: reconciliation-engine
scope: poc
last_updated: 2026-05-09
status: draft
---

# Reconciliation Design

## Table of contents

- [Summary](#summary)
- [Authority](#authority)
- [Design Principles](#design-principles)
  - [Layered Dependency Flow](#layered-dependency-flow)
  - [Method Dispatch via Account-Group Classification](#method-dispatch-via-account-group-classification)
  - [Heuristics as Configuration](#heuristics-as-configuration)
  - [Determinism and Idempotency Guarantees](#determinism-and-idempotency-guarantees)
- [Key Design Decisions](#key-design-decisions)
- [Implementation guidelines](#implementation-guidelines)
- [Testing Strategy](#testing-strategy)
- [OOP Architecture and Repository Layout](#oop-architecture-and-repository-layout)
  - [Class Hierarchy Overview](#class-hierarchy-overview)
  - [Method Dispatch Contract](#method-dispatch-contract)
  - [Library Dependencies](#library-dependencies)
  - [Implementation Constraints](#implementation-constraints)
  - [Repository Layout](#repository-layout)
- [Module Structure and Layered Architecture](#module-structure-and-layered-architecture)
  - [Layer 1: Models](#layer-1-models)
  - [Layer 2: Utilities](#layer-2-utilities)
  - [Layer 3: Methods](#layer-3-methods)
  - [Layer 4: Shared Adapters](#layer-4-shared-adapters)
  - [Layer 5: Orchestration](#layer-5-orchestration)
  - [Configuration](#configuration)
  - [Data Flow Example](#data-flow-example)
- [Method Class Specifications](#method-class-specifications)
  - [Transaction-level Method Class](#transaction-level-method-class)
  - [Balance-level Method Class](#balance-level-method-class)
  - [Cross-cutting Concerns](#cross-cutting-concerns)
- [Account-group Procedures](#account-group-procedures)
  - [Procedure Table](#procedure-table)
  - [Variance Interpretation Matrix](#variance-interpretation-matrix)
  - [Tolerance Rules by Account Group](#tolerance-rules-by-account-group)
  - [Approval Authority and Override Policy](#approval-authority-and-override-policy)
- [Adjustment and Audit Contracts](#adjustment-and-audit-contracts)

## Summary

This document specifies the reconciliation method classes, account-group procedures, tolerance rules, variance interpretation, and approval authority for the POC close cycle. It provides the design contract for both the transaction-level and balance-level reconciliation methods, and the account-level reconciliation behavior after orchestrator dispatch to stage 6.

## Authority

This document is the authoritative source for reconciliation design decisions.
If any conflict exists between this document and requirements artifacts, this document supersedes those requirements for reconciliation scope.

## Design Principles

The reconciliation engine is governed by four foundational design principles that ensure correctness, determinism, testability, and operational safety.

### Layered Dependency Flow

Reconciliation is structured as a layered, acyclic dependency hierarchy:

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
- Utilities depend on models only (no persistence or business logic)
- Methods depend on models and utilities (NOT on adapters or engine)
- Shared adapters depend on models only (NOT on methods or engine)
- Engine depends on all layers but contains NO algorithm logic

**Rationale:** This layering preserves testability, reusability, and separation of concerns. Methods can be unit-tested in isolation from persistence. Shared adapters can be swapped without touching method implementations.

### Method Dispatch via Account-Group Classification

Account group classification is **owned by the engine**, not by callers. The dispatcher pattern enables polymorphic method selection without coupling callers to concrete implementations.

**Dispatch protocol:**
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
- **IBKR** (routed to source integration deterministic parsing for CSV-to-HB and close_book txns, not reconciliation engine)

### Heuristics as Configuration

Heuristics rules and parameters are **configuration-driven, not hardcoded**. This enables account-specific policy updates without code changes and guarantees deterministic ordering for idempotency.

**Configuration hierarchy:**
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

**Configuration safety guard:**
- User policy edits are made through approved UI interfaces that validate values before persistence.
- Direct manual JSON editing by end users is outside the operational contract.

**Rationale:** Configuration-driven heuristics enable:
- No code changes to add account-specific heuristics or adjust parameters
- Deterministic ordering for idempotency (applied in config file order)
- Auditable parameter values (stored with session metadata for reproducibility)
- Runtime parameter discovery without pre-registration
- Easy policy updates (e.g., "UOB date tolerance is now 5 days" → update via UI policy form)

### Determinism and Idempotency Guarantees

**Reconciliation must be byte-identical across reruns with identical inputs.** This enables safe reruns, session replay verification, and deterministic audit trails.

**Determinism achieved via:**
- **Ledger slice construction:** Deterministic sorting by `(date ASC, original_index)` as tie-breaker
- **Match pairs:** Same forward-pass algorithm with same parameters produces same pairs
- **Heuristics order:** Fixed order from config file, not dynamic or random
- **Decimal arithmetic:** Exact `decimal.Decimal` throughout; never float conversions
- **Adjustment ID:** Deterministic hash of `(session_id, account_id, period, rule, gap)`
- **Gap validation:** Same calculation method produces same result

**Idempotency contract for SQLite:**
- Same adjustment_id inserted twice → upsert produces single record (no duplicate)
- Statement builder queries are deterministic: same close_book → same statement aggregates
- Session reopened and re-reconciled → identical adjustments with same adjustment_id
- Deterministic matching enables safe retry: same reconciliation run twice is identical byte-for-byte

## Key Design Decisions

This section provides rationale for major architectural choices.

### 1. Why Separate TransactionLevelMethod and BalanceLevelMethod?

**Different algorithms, different inputs, different outputs:**

| id | aspect    | transaction-level            | balance-level                 |
| -- | --------- | ---------------------------- | ----------------------------- |
| 01 | input     | ledger and statement txns    | primary and comparison bal    |
| 02 | algorithm | forward/backward + heuristics | balance equation + variance   |
| 03 | output    | edits, gap, matches          | variance class, adjustment    |
| 04 | accounts  | bank statement-process       | cash, cpf, manual, hb-native  |

Both inherit from `BaseReconciliationMethod` for polymorphism, but the inheritance represents "both are reconciliation methods," not code reuse.

### 2. Why Heuristics as Configuration, Not Polymorphic Classes?

**Configuration-driven approach enables:**
- Add new account-specific heuristics without code changes (through UI-managed policy config)
- Runtime parameter discovery (no pre-registration)
- Deterministic ordering (applied in config file order)
- Auditable parameters (stored with session metadata for reproducibility)
- Easy policy updates (e.g., "UOB date tolerance is now 5 days" → update via UI policy form)

**Heuristic class hierarchy is for extensibility:**
- `Heuristic (ABC)` defines interface: `apply(edits_df) -> reduced_edits_df`
- Four reusable concrete classes inherit and each implement one algorithm: `NetZeroPairHeuristic`, `SameAmountZeroSumClusterHeuristic`, `KeywordFilterNetZeroHeuristic`, `PatternCrossSourceNetZeroHeuristic`
- Config file specifies which heuristics to apply and with what parameters for each account
- New account rule: add a config entry with an existing heuristic and new parameters — **zero new code**
- New algorithm type: code a class in heuristics.py, register in factory, then expose through UI config

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

## Implementation guidelines

The implementation phase must satisfy the following contracts.

| id | contract                | guideline                                                   |
| -- | ----------------------- | ----------------------------------------------------------- |
| 01 | method invocation       | no positional args for optional config inputs               |
| 02 | money arithmetic        | all amount operations use Decimal; no float conversions     |
| 03 | edit invariants         | each heuristic keeps `sum(edit_amount)` invariant            |
| 04 | deterministic ordering  | sort by date then source index before matching              |
| 05 | error taxonomy          | use typed domain exceptions only                            |
| 06 | persistence             | idempotent upsert by deterministic keys                     |
| 07 | config usage            | no hard-coded tolerance values in method classes            |

Code-complete handoff readiness is reached only when all items pass.

| id | completion_gate            | pass_condition                                        | evidence                            |
| -- | -------------------------- | ----------------------------------------------------- | ----------------------------------- |
| 01 | package scaffold           | all required modules and classes exist                | tree and import smoke test          |
| 02 | interface contract         | signatures match this design document                 | static typing and contract tests    |
| 03 | algorithm correctness      | forward and backward edit equivalence always enforced | deterministic replay tests          |
| 04 | config compliance          | runtime uses config paths with precedence rules       | config integration tests            |
| 05 | invariants                 | gap and heuristic invariants never violated           | invariant assertion suite           |
| 06 | idempotency                | duplicate execution yields byte-identical outputs     | rerun integration test              |
| 07 | boundary enforcement       | IBKR dispatch rejected as unsupported in this module  | account-group dispatch tests        |
| 08 | operational observability  | required logs and checkpoints emitted                 | log contract checks                 |
| 09 | persistence contract       | close_book and session writes are idempotent          | SQLite write-back tests             |
| 10 | failure behavior           | typed errors surfaced for all documented failure modes | exception-path tests               |

### Configuration Management and Governance

Configuration for reconciliation is managed through two primary files, validated at startup, and frozen into session snapshots for reproducibility.

**Configuration keys and precedence:**

| id | config_area        | key_path                                         | precedence_rule                  |
| -- | ------------------ | ------------------------------------------------ | -------------------------------- |
| 01 | matching default   | `matching_config.default`                        | fallback for all accounts        |
| 02 | matching override  | `matching_config.accounts.<account>`             | overrides default per account    |
| 03 | general heuristics | `general_heuristics[]`                           | applied first in listed order    |
| 04 | account heuristics | `account_heuristics.<account>[]`                 | applied after general heuristics |
| 05 | tolerance policy   | `tolerance_config.account_groups.<group>`        | consumed by balance-level method |
| 06 | feature flags      | `runtime_flags.<flag_name>`                      | default false, explicit enable   |

**Configuration governance and safety:**

- Startup pre-flight must validate both `txn_heuristics.json` and `tolerance_config.json` before reconcile stages can start. Validation failures block reconciliation.
- Configuration snapshot is captured at session start and frozen for reproducibility. No config changes during active reconciliation.
- User-facing policy updates are performed through the UI interface and validated at save time before persistence.
- Direct user edits to JSON files are out of scope for normal operation and are treated as unsafe configuration bypass. Direct edits are unsupported.

**Minimal configuration payload shape (reference):**

```json
{
  "matching_config": {
    "default": {
      "date_tolerance_days": 3,
      "amount_tolerance": 0.01
    },
    "accounts": {
      "TWH UOB One SGD": {
        "date_tolerance_days": 5
      }
    }
  },
  "general_heuristics": ["net_zero_pair", "same_amount_zero_sum_cluster"],
  "account_heuristics": {
    "TWH DBS Multi SGD": ["cpf_net_zero"],
    "TWH UOB One SGD": ["uob_cashback_split"]
  }
}
```

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

## OOP Architecture and Repository Layout

The reconciliation engine module is designed as a layered, object-oriented system with clean separation between domain models, algorithm implementations, utilities, shared adapters, and orchestration.

### Class Hierarchy Overview

**Abstract base class:**
- `ReconciliationMethod` — Defines contract for all reconciliation strategies with 4 abstract methods: `validate_inputs()`, `compute_gap()`, `classify_variance()`, `generate_adjustment()`

**Concrete method classes:**
- `TransactionLevelMethod(ReconciliationMethod)` — Bank statement matching: forward/backward passes, heuristics, edits model
- `BalanceLevelMethod(ReconciliationMethod)` — Balance equation reconciliation: cash, CPF, manual-input, HomeBudget-native

**Orchestration class:**
- `ReconciliationEngine` — Owns session state, method dispatch, adjustment posting, audit trail. Methods: `execute_reconciliation()`, `dispatch_by_account_group()`, `post_adjustment()`, `generate_session_record()`

**Domain models:**
- `AdjustmentTransaction` — Adjustment lifecycle with 20 fields and 4-state status: generated → pending_approval → approved → posted
- `ReconciliationSession` — Per-account session record with 27 fields, 8 audit checkpoints, and lineage anchors

### Library Dependencies

| id | library    | purpose                       | key_classes_methods                  |
| -- | ---------- | ----------------------------- | ------------------------------------ |
| 01 | `pandas`   | ledger/stmnt transforms       | `DataFrame`, `sort_values()`, `sum()`|
| 02 | `decimal`  | exact money arithmetic        | `Decimal`, `quantize()`              |
| 03 | `sqlite3`  | read/write sqlite schemas     | `Connection`, param queries          |
| 04 | `pydantic` | model validation              | `BaseModel`, `Field`, `validator`    |
| 05 | `uuid`     | session/adjustment ids        | `uuid.uuid4()`                       |
| 06 | `json`     | config loading                | `json.load()`                        |
| 07 | `hashlib`  | deterministic id hashing      | `hashlib.sha256()`                   |
| 08 | `logging`  | audit + checkpoint logs       | `getLogger()`, structured records    |
| 09 | `enum`     | typed status enums            | `Enum`, `auto()`                     |

### Implementation Constraints

These are **design-level constraints** that code must enforce:

| id | constraint             | definition                                                      | enforcement                                  |
| -- | ---------------------- | --------------------------------------------------------------- | -------------------------------------------- |
| 01 | deterministic matching | Same algorithm + same parameters + same row order = identical results | Rerun test with same inputs; compare output  |
| 02 | decimal arithmetic     | All monetary amounts use Decimal(28,2) with ROUND_HALF_UP       | Type annotations; validation at entry/exit   |
| 03 | idempotent posting     | Repeated post of same adjustment yields one logical record      | adjustment_id deterministic hash; upsert only |
| 04 | gap invariant          | For every edit set: sum(edit_amount) == 0.00                    | Assertion before post; pre-flight validation |
| 05 | fwd-bwd equivalence    | Forward-pass matches == backward-reduction matches after heuristics | Mandatory gate; divergence = fail-closed     |
| 06 | config is ground truth | All policy decisions resolved from config; frozen per session    | Config validated at startup; immutable after |
| 07 | config edit safety     | User policy changes routed through UI forms only                | Direct JSON edits unsupported; UI validated  |

## Module Structure and Layered Architecture

The reconciliation engine is organized into five layers with strict, acyclic dependencies. This section details each layer's responsibility, classes, and data contracts.

### Layer 1: Models

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

**Reference model snippet:**

```python
from datetime import datetime
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field


class AdjustmentStatus(str, Enum):
  GENERATED = "generated"
  PENDING_APPROVAL = "pending_approval"
  APPROVED = "approved"
  POSTED = "posted"


class AdjustmentTransaction(BaseModel):
  adjustment_id: str
  session_id: str
  account_id: str
  period_key: str
  adjustment_amount: Decimal = Field(..., decimal_places=2)
  residual_gap: Decimal = Field(..., decimal_places=2)
  status: AdjustmentStatus = AdjustmentStatus.GENERATED
  rule_reference: str
  category_code: str
  created_timestamp: datetime
```

### Layer 2: Utilities

**Purpose:** Helper functions and utility classes (pure computation)

| id | file              | functions                                 | responsibility                   |
| -- | -----------       | -----------                                | -----------                      |
| 01 | ledger_slicer.py  | slice build utilities, balance discovery   | deterministic slice construction |
| 02 | heuristics.py     | Heuristic (ABC), 4 concrete classes        | heuristic reduction              |
| 03 | config_loader.py  | config resolution, heuristic loading       | config precedence and discovery  |
| 04 | matching.py       | forward/backward matching, equivalence     | match validation                 |
| 05 | pairing.py        | statement-ledger and transfer pairing      | edit pairing recovery            |
| 06 | gap_calculator.py | gap computation, tolerance validation      | gap calculation and checks       |

**Heuristics layer:** The four concrete heuristic classes are `NetZeroPairHeuristic`, `SameAmountZeroSumClusterHeuristic`, `KeywordFilterNetZeroHeuristic`, and `PatternCrossSourceNetZeroHeuristic`. All inherit from `Heuristic (ABC)` and implement the `apply(edits_df)` contract.

**Design patterns:**
- **Stateless utilities are always functions**, not classes. Examples: slice building, gap calculation, config resolution, matching, pairing.
- **One concrete class per distinct algorithm**: Heuristics inherit from abstract base `Heuristic` for polymorphism; each subclass encapsulates one algorithm.
- **Config parameters are function arguments**, not instance state. Example: `forward_match(ledger_df, stmt_df, date_tolerance_days=3)`.
- **State cohesion**: Methods in a class operate on shared instance state. If a class has one method or only @staticmethod decorators, convert to function.
- **Config discovery is explicit and ordered**: account override → default → general + account-specific (resolved before invocation).

**Reference utility snippets:**

```python
from decimal import Decimal


def resolve_matching_config(config: dict, account: str) -> dict:
  """Resolve account-specific matching config with default fallback.
  
  Precedence: account override → default config.
  """
  default_cfg = config["matching_config"]["default"]
  account_cfg = config["matching_config"].get("accounts", {}).get(account, {})
  resolved = dict(default_cfg)
  resolved.update(account_cfg)
  return resolved


def compute_gap(ledger_end: Decimal, edits_sum: Decimal, statement_end: Decimal) -> Decimal:
  """Calculate reconcile gap with exact decimal arithmetic.
  
  gap = (ledger_end + sum(edit_amount)) - statement_end
  """
  return (ledger_end + edits_sum - statement_end).quantize(Decimal("0.01"))
```

### Layer 3: Methods

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

**Reference method snippet:**

```python
class TransactionLevelMethod(BaseReconciliationMethod):
  def reconcile(self, account, year, month, **inputs) -> ReconciliationResult:
    # Slice construction: stateless utility functions
    ledger = build_ledger_slice(inputs["hb_gl_txn"], account, year, month, inputs["opening_balance"])
    stmt = build_statement_slice(inputs["statements"], account, year, month, inputs["opening_balance"])

    # Matching: config-driven by date_tolerance_days from session config
    date_tol = self._session_config["matching_config"][account]["date_tolerance_days"]
    matches = forward_match(ledger, stmt, date_tolerance_days=date_tol)
    unmatched_ledger = set(ledger.index) - {m[0] for m in matches}
    unmatched_stmt = set(stmt.index) - {m[1] for m in matches}
    
    # Edit construction: derive from match pairs and unmatched rows
    edits_forward = self._build_edits(ledger, stmt, unmatched_ledger, unmatched_stmt)
    edits_backward = self._backward_reduce(ledger, stmt, matches)

    # Heuristics: apply configured heuristics to both forward and backward
    heuristics = HeuristicsFactory.build_for_account(self._session_config, account)
    ef = self._apply_heuristics(edits_forward, heuristics)
    eb = self._apply_heuristics(edits_backward, heuristics)
    
    # Validation: forward and backward must be equivalent (mandatory gate)
    assert_forward_backward_equivalence(ef, eb)

    # Gap calculation: stateless utility function
    gap = compute_gap(ledger["balance"].iloc[-1], ef["edit_amount"].sum(), stmt["balance"].iloc[-1])
    return ReconciliationResult(account, year, month, ef, matches, gap)
```

### Layer 4: Shared Adapters

**Purpose:** Persistence and external system integration boundaries

| id | file              | classes                  | responsibility                    |
| -- | ----------------- | ------------------------ | --------------------------------- |
| 01 | sqlite_adapter.py | ReconciliationPersistence | session and adjustment persistence |
| 02 | hb_adapter.py     | HomeBudgetAdapter        | HomeBudget posting integration     |

**Key design decision:** Shared adapters depend on models ONLY (not on methods or engine). This preserves adapter independence: persistence logic is orthogonal to reconciliation algorithms.


**Reference adapter snippet:**

```python
class ReconciliationPersistence:
  """Reconciliation persistence boundary; no SQL or dialect logic."""

  def __init__(self, sql_adapter):
    self._sql_adapter = sql_adapter

  def upsert_adjustment(self, rec: AdjustmentTransaction) -> None:
    self._sql_adapter.upsert(
      table="close_book_adjustments",
      data={
        "adjustment_id": rec.adjustment_id,
        "session_id": rec.session_id,
        "account_id": rec.account_id,
        "period_key": rec.period_key,
        "adjustment_amount": str(rec.adjustment_amount),
        "residual_gap": str(rec.residual_gap),
        "status": rec.status.value,
        "rule_reference": rec.rule_reference,
      },
      conflict_key="adjustment_id",
    )
```

The `ReconciliationPersistence` is a domain boundary. It centralizes table name, column mapping, and reconciliation-specific write semantics. Engine and methods stay unaware of persistence shape details.

### Layer 5: Orchestration

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

**Reference orchestration snippet:**

```python
class BaseReconciliationEngine:
  def reconcile(self, account: str, year: int, month: int, **inputs) -> ReconciliationResult:
    raise NotImplementedError


class ReconciliationEngine(BaseReconciliationEngine):
  def reconcile(self, account: str, year: int, month: int, **inputs) -> ReconciliationResult:
    session = self.session_repo.create(account=account, year=year, month=month)
    group = self.classifier.classify(account)
    params = self.config_snapshot.resolve(account, group)
    method = self.dispatcher.get_method(group, params)

    result = method.reconcile(account, year, month, **inputs)
    validate_postconditions(group, result)  # Stateless validation function

    if result.adjustment_record is not None:
      self.persistence.upsert_adjustment(result.adjustment_record)

    self.session_repo.close(session.session_id, result)
    return result
```

### Configuration

| id | file                  | purpose                              |
| -- | --------------------- | ------------------------------------ |
| 01 | txn_heuristics.json   | heuristic rules and account overrides |
| 02 | tolerance_config.json | tolerance limits and approval policy  |

Both files are validated during pre-flight startup, then frozen into a session config snapshot used by reconciliation execution.

### Repository Layout

**Directory structure:**
```
src/close_session/reconciliation_engine/
├─ __init__.py                          # Public API exports
├─ engine.py                            # ReconciliationEngine class
├─ models/
│  ├─ adjustment_transaction.py
│  ├─ reconciliation_session.py
│  └─ enums.py                          # VarianceClass, AdjustmentStatus, SessionStatus
├─ methods/
│  ├─ __init__.py
│  ├─ reconciliation_method.py           # Abstract base
│  ├─ transaction_level_method.py
│  └─ balance_level_method.py
├─ utilities/
│  ├─ heuristics_config.py
│  ├─ ledger_slicer.py
│  ├─ matching_algorithm.py
│  ├─ gap_validator.py
│  ├─ variance_classifier.py
│  └─ adjustment_builder.py
└─ config/
   ├─ config_loader.py
   ├─ txn_heuristics.json               # Heuristic parameters, account overrides
   └─ tolerance_config.json             # Tolerance thresholds by account group

src/python/adapters/                    # App-wide shared adapter layer
├─ sqlite_adapter.py                    # Read GL, persist session, write close_book
└─ homebudget_wrapper.py                # HB GL posting (read-only or write-back)
```

**Dependency flow — strict acyclic:**
- Layer 1: `models/` — No external dependencies
- Layer 2: `utilities/` — Depends on models only
- Layer 3: `methods/` — Depends on models, utilities
- Layer 4: shared adapters (`src/python/adapters/`) — App-wide utilities consumed by engine and other modules
- Layer 5: `engine.py` — Depends on models, utilities, methods, and shared adapter interfaces

### Data Flow Example: Bank Account Reconciliation

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
  → Pre-flight validates txn_heuristics.json and tolerance_config.json
  → Load startup-validated session config snapshot
  → discover date_tolerance_days = 3 (no override for DBS, use default)
  → discover heuristics = [net_zero_pair, same_amount_zero_sum_cluster, cpf_net_zero]

Step 3: Method dispatch
  → Instantiate TransactionLevelMethod(heuristics_config)

Step 4: Ledger slice construction
  → build_ledger_slice(hb_gl, "TWH DBS Multi SGD", 2026, 2, opening_balance)
  → Filter out balance rows (txn_type == "balance")
  → Filter out null amounts
  → Sort by date ASC, then by original index
  → Compute running balance
  → Discover opening_balance via discover_opening_balance(balances, account, year, month)
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

## Method Class Specifications

This section specifies the contract, algorithm, parameters, and invocation interface for the two reconciliation method classes.

### Transaction-level Method Class

The transaction-level method compares transactions from two independent sources — ledger and statement — and produces a minimal edit set that closes the reconcile gap to zero.

**Monetary type contract:**
- All monetary fields in this method class use `Decimal` values with quantization to 2 decimal places using `ROUND_HALF_UP`.
- Float arithmetic is forbidden in transaction-level reconciliation logic, including matching, gap computation, and heuristic validation.

#### Edits Model Structure

The method produces an edits table with the following fields and semantics:

| id | field       | type                      | description                  |
| -- | ----------- | ------------------------- | ---------------------------- |
| 01 | `source`    | `"ledger","statement"`    | row source                   |
| 02 | `date`      | iso date                  | txn date (`YYYY-MM-DD`)      |
| 03 | `amount`    | Decimal(28,2)             | txn amount in acct currency  |
| 04 | `edit`      | `"remove","add","update"` | ledger-side action           |
| 05 | `edit_amt`  | Decimal(28,2)             | signed delta from edit       |
| 06 | `note`      | string                    | txn note or description      |
| 07 | `ledger_ix` | int or null               | ledger row index (0-based)   |
| 08 | `stmt_ix`   | int or null               | statement row index (0-based)|

**Invariant requirement:** The sum of `edit_amount` over any removed or modified subset must equal zero to preserve the reconcile gap equation.

#### Gap Equation and Validity Criterion

The reconcile gap with a given edits set is defined as:

```
gap = ledger_end_balance + sum(edit_amount over all edits) - statement_end_balance
```

A solution is **valid** if and only if `gap == 0.00`, within currency rounding precision — typically 0.01 for SGD.
Among all valid solutions, the method selects the **minimal edit set** — the solution with the fewest number of edit rows.

**Requirement ref:** reconciliation-engine.md § Transaction-level method class / Edits model

#### Ledger and Statement Slice Construction

Before matching, two slices are constructed from the source GL sheets for the `(account, year, month)` scope:

**Ledger slice construction:**
1. Filter `hb_gl_txn` for rows matching account, year, month.
2. Keep transaction rows only, excluding non-transaction summary rows if present in source extracts.
3. Drop rows with null `amount`.
4. Sort by `date` ascending, with original row index as tie-breaker.
5. Compute running `balance`: `balance[i] = opening_balance + cumsum(amount)[0:i+1]`.
6. Retain only columns: `index`, `date`, `amount`, `balance`, `category`, `subcategory`, `payee`, `notes`.

**Statement slice construction:**
1. Filter `statements` transaction rows for the account and period scope.
2. Drop rows with null `amount`.
3. Sort by `date` ascending, with original row index as tie-breaker.
4. Compute running `balance`: `balance[i] = opening_balance + cumsum(amount)[0:i+1]`.
5. Retain only columns: `index`, `date`, `amount`, `balance`, `description`.

**Opening balance discovery:**
- The opening balance is the prior-period ending balance from `hb_account_dim`.
- For month M in year Y, look up the prior period row for `(account, year=Y, month=M-1)`.
- For January (month=1), look up `(account, year=Y-1, month=12)`.
- If no prior period row exists, initialization fails with a "missing opening balance" error.

**Statement ending balance cross-check:**
- The statement slice ending balance (last row `balance` value) must equal the statement period-end balance record in `statement_balance` for `(account, year, month)`.
- If the difference exceeds account precision — typically 0.01 — log a warning and flag the variance for user review before proceeding.
- This cross-check detects issues in statement ingest or GL schema inconsistency.

**Requirement ref:** reconciliation-engine.md § Account-group procedures / Bank statement-process accounts

**Reference slice construction snippet:**

```python
# Stateless utility functions grouped in a module, not a class.
# Each performs one deterministic computation on ledger or statement data.

def build_ledger_slice(hb_gl_txn, account: str, year: int, month: int, opening_balance: Decimal):
  """Build ledger slice with running balance."""
  scope = hb_gl_txn[
    (hb_gl_txn["account"] == account)
    & (hb_gl_txn["year"] == year)
    & (hb_gl_txn["month"] == month)
  ].copy()
  scope = scope[scope["amount"].notna()].sort_values(["date", "index"])
  scope["running_delta"] = scope["amount"].cumsum()
  scope["balance"] = opening_balance + scope["running_delta"]
  return scope[["index", "date", "amount", "balance", "notes"]]

def build_statement_slice(stm_txn, account: str, year: int, month: int, opening_balance: Decimal):
  """Build statement slice with running balance."""
  scope = stm_txn[
    (stm_txn["account"] == account)
    & (stm_txn["year"] == year)
    & (stm_txn["month"] == month)
  ].copy()
  scope = scope[scope["amount"].notna()].sort_values(["date", "index"])
  scope["running_delta"] = scope["amount"].cumsum()
  scope["balance"] = opening_balance + scope["running_delta"]
  return scope[["index", "date", "amount", "balance", "description"]]

def discover_opening_balance(balances, account: str, year: int, month: int) -> Decimal:
  """Look up opening balance from prior period end."""
  prior_month = month - 1 if month > 1 else 12
  prior_year = year if month > 1 else year - 1
  candidates = balances[
    (balances["account"] == account)
    & (balances["year"] == prior_year)
    & (balances["month"] == prior_month)
  ]
  if candidates.empty:
    raise ValueError(f"No opening balance for {account} {year}-{month:02d}")
  return Decimal(str(candidates.iloc[-1]["balance"]))
```

**Design principle:** Stateless pure functions (no instance state) belong in a module, not a class. Classes bundle behavior with state; functions are used when there is no state to maintain.

#### Forward Pass Algorithm

The forward pass greedily matches ledger and statement transactions that are unambiguously equivalent, then builds an initial edits set from unmatched transactions.

**Match procedure:**

For each unmatched ledger transaction:
1. Identify all statement transactions not yet matched.
2. Define `ledger_amount` and `ledger_date` from the current ledger row in the ledger slice.
3. For each statement candidate, define `statement_amount` and `statement_date` from the statement slice row.
4. Filter candidates by three-part match test; all three must hold:
  - **Amount test:** `ledger_amount == statement_amount` — exact match, same sign, exact cents, currency rounding.
  - **Date test:** `abs(ledger_date - statement_date) <= date_tolerance_days` — configurable per account, default 3.
   - **Uniqueness test:** exactly one statement candidate remains after filtering; zero or multiple candidates result in no match.
5. If exactly one candidate remains, mark the pair `(ledger_idx, stmt_idx)` as matched.
6. If zero or multiple candidates, leave the ledger transaction unmatched.

**Match results:**
- `matches`: list of `(ledger_idx, stmt_idx)` tuples.
- `unmatched_ledger`: set of ledger indices not in any match.
- `unmatched_stmt`: set of statement indices not in any match.

**Forward edits construction:**
- For each `ledger_idx` in `unmatched_ledger`: add one `remove` edit with `edit_amount = -amount`.
- For each `stmt_idx` in `unmatched_stmt`: add one `add` edit with `edit_amount = +amount`.

**Key control: Exact-amount matching ensures zero-sum property at pair level**

The forward pass enforces an exact-amount matching predicate as a mandatory control on valid matched pairs. When a ledger transaction with `amount = X` is paired to a statement transaction with `amount = X` (same sign, same cents), the pair has the property that **removing both rows from their respective sources contributes zero to the reconcile gap**.

Formally: If `(ledger[i], stmt[j])` is a matched pair with `ledger[i].amount == stmt[j].amount == X`, then:
- Ledger side contributes: `-X` (remove ledger row)
- Statement side contributes: `+X` (add statement row, so negation is `-X`)
- Net gap contribution: `-X + X = 0`

This property holds **before heuristics are applied** and is preserved by all heuristics because they operate on the invariant that any removed or modified edit subset must sum to zero.

**Expected outcome:** If GL data are internally consistent — no missing or spurious transactions — the forward edits already yield `gap == 0.00`. However, the set may not yet be minimal due to boundary conditions or timing variations.

**Requirement ref:** reconciliation-engine.md § Transaction-level method class / Forward and backwards algorithm; hb-reconcile/docs/reconcile.md § Forward algorithm

**Reference forward pass snippet:**

```python
def forward_match(ledger_df, stmt_df, date_tolerance_days: int = 3):
  """Forward pass: greedy one-to-one matching by amount and date.
  
  Returns: list of (ledger_idx, stmt_idx) match pairs.
  """
  used_stmt = set()
  matches = []

  for l_idx, l_row in ledger_df.iterrows():
    candidates = stmt_df[
      (~stmt_df.index.isin(used_stmt))
      & (stmt_df["amount"] == l_row["amount"])
      & ((stmt_df["date"] - l_row["date"]).abs().dt.days <= date_tolerance_days)
    ]
    if len(candidates) == 1:
      s_idx = candidates.index[0]
      used_stmt.add(s_idx)
      matches.append((l_idx, s_idx))

  return matches
```

#### Backward Pass Algorithm

The backward pass starts from a trivially valid solution — remove all ledger, add all statement — and reduces it using forward-match evidence. This alternative derivation serves as a correctness assertion.

**Backward procedure:**

1. **Trivial solution construction:**
   - Create a `remove` edit for every ledger transaction with `edit_amount = -amount`.
   - Create an `add` edit for every statement transaction with `edit_amount = +amount`.
   - By construction, `sum(edit_amount) = 0.00` and `gap = 0.00`.

2. **Reduction via forward matches:**
   - For each forward match pair `(ledger_idx, stmt_idx)`:
     - Remove the `remove` edit for `ledger_idx` from the trivial set.
     - Remove the `add` edit for `stmt_idx` from the trivial set.
   - The reduced set remains valid because we are removing paired edits whose `edit_amount` values sum to zero.

3. **Heuristics application:**
   - Apply the same heuristics to both the forward and backward-reduced edit sets, described in the Heuristics Layer section below.

**Correctness assertion and enforcement:**

After heuristics application, the forward and backward-reduced edit sets **must be identical** in shape and values. This equivalence is a mandatory correctness gate, not an optional validation.

_Execution point:_ The equivalence check must execute after heuristics application is complete and before tolerance evaluation proceeds. If sets diverge, reconciliation advancement is blocked.

_Exception contract:_ If forward and backward sets diverge:
- Raise a `ReconciliationInconsistencyError` exception with message content including:
  - Forward set shape (row count, columns)
  - Backward set shape (row count, columns)
  - Symmetric difference (rows in forward but not backward; rows in backward but not forward)
  - Log level: ERROR (halt-and-investigate severity)

_Metadata storage:_ Store both reduced edit sets in reconciliation session attributes with the following metadata:
  - `edits_forward_reduced`: complete DataFrame after heuristics, sorted by `(source, date, amount, edit)`
  - `edits_backward_reduced`: complete DataFrame after heuristics, sorted by `(source, date, amount, edit)`
  - `forward_backward_equivalence_check`: dict containing:
    - `check_timestamp`: ISO 8601 timestamp
    - `shapes_equal`: boolean
    - `values_equal`: boolean
    - `symmetric_difference`: list of row dicts found in one set but not the other
    - `check_result`: "pass" or "fail"

_Why it's required:_ Divergence indicates either a heuristic bug (incorrect gap preservation) or fundamental algorithmic inconsistency. Without mandatory enforcement, bugs propagate silently to tolerance evaluation and adjustment generation, corrupting the reconciliation session artifact and damaging the audit trail.

**Requirement ref:** hb-reconcile/docs/reconcile.md § Backwards algorithm

**Reference backward equivalence snippet:**

```python
def assert_forward_backward_equivalence(edits_forward, edits_backward):
  """Verify forward and backward edit sets are identical (mandatory gate).
  
  Raises: ReconciliationInconsistencyError if divergence detected.
  """
  sort_cols = ["source", "date", "amount", "edit"]
  ef = edits_forward.sort_values(sort_cols).reset_index(drop=True)
  eb = edits_backward.sort_values(sort_cols).reset_index(drop=True)

  if ef.shape != eb.shape or not ef.equals(eb):
    diff = {
      "forward_only": ef.merge(eb, how="outer", indicator=True).query("_merge == 'left_only'"),
      "backward_only": ef.merge(eb, how="outer", indicator=True).query("_merge == 'right_only'"),
    }
    raise ReconciliationInconsistencyError(diff)
```

#### Heuristics Layer

Heuristics remove redundant edits while preserving the gap invariant. All heuristics must satisfy:

```
sum(edit_amount over modified or removed subset) = 0.00
```

**General heuristics applied to all accounts:**

**1. Net-zero pairs (`net_zero_pair`)**
- **Purpose:** Remove pairs of opposite-amount edits within a configurable date window.
- **Procedure:** Identify pairs `(i, j)` where:
  - `edit_amount[i] == -edit_amount[j]` — exact opposites.
  - `abs(date[i] - date[j]) <= date_tolerance_days` — configurable, default 3.
  - `source[i] == source[j]` — both from ledger or both from statement.
  - Drop both edits from the set.
- **Gap invariant:** preserved because the two `edit_amount` values sum to zero.
- **Use case:** Captures internal "split then re-join" corrections within the ledger or statement.
- **Config source:** `txn_heuristics.json` / `general_heuristics` / `net_zero_pair`

**2. Same-amount zero-sum clusters (`same_amount_zero_sum_cluster`)**
- **Purpose:** Remove clusters of identical-amount edits from mixed sources that net to zero.
- **Procedure:** For each distinct `amount` value:
  1. Collect all edits with that amount.
  2. Require at least one `source="ledger"` edit and at least one `source="statement"` edit.
  3. Compute `cluster_sum = sum(edit_amount)` over the cluster.
  4. If `abs(cluster_sum) <= amount_tolerance` — default 0.01 — remove the entire cluster.
- **Gap invariant:** preserved because the cluster's net `edit_amount` is zero.
- **Use case:** Captures ambiguous repetitions — for example, two McDonald's charges for the same amount on consecutive days matched by ambiguity — that form a self-contained zero-sum bubble.
- **Config source:** `txn_heuristics.json` / `general_heuristics` / `same_amount_zero_sum_cluster`

**3. Keyword filter net-zero (`keyword_filter_net_zero`)**
- **Purpose:** Remove edits matching specified keywords if they sum to zero. Reusable across any account with keyword-based rules.
- **Procedure:**
  1. Select edits whose `note` field contains any of the configured keywords.
  2. Compute `subset_sum = sum(edit_amount)` over the selected subset.
  3. If `abs(subset_sum) <= amount_tolerance` — configurable, default 0.01 — drop the entire subset.
- **Gap invariant:** preserved because the subset's `edit_amount` values sum to zero.
- **Use case:** CPF allocations (DBS Multi), internal transfers, or any account-specific keyword-driven zero-sum cleanup.
- **Config parameters:** `keywords` (list of strings), `note_field` (which column to search; default "note"), `amount_tolerance` (Decimal).
- **Example config (DBS Multi SGD):**
  ```json
  {
    "name": "keyword_filter_net_zero",
    "config": {
      "keywords": ["Flintex CPF", "RSK CPF", "CPF OA", "CPF SA", "CPF MA"],
      "note_field": "note",
      "amount_tolerance": "0.01"
    }
  }
  ```
- **Example behavior:** Edits `Flintex CPF -5000`, `CPF OA +2500`, `CPF SA +2500` sum to zero → dropped.

**4. Pattern cross-source net-zero (`pattern_cross_source_net_zero`)**
- **Purpose:** Remove edit clusters matching patterns from both ledger and statement within a period window if amounts balance. Reusable across any account with pattern-matching rules.
- **Procedure:**
  1. Identify ledger edits matching `ledger_patterns` in the `note` field, within the same `(year, month)`.
  2. Identify statement edits matching `statement_patterns` in the `note` field, same period.
  3. Check if the sum of ledger amounts equals the sum of statement amounts within `amount_tolerance`.
  4. If balanced, drop the entire cluster.
- **Gap invariant:** preserved because the cluster's net amounts are zero by definition (balanced).
- **Use case:** Cashback rebates (UOB One), tax refunds, or any paired ledger-statement entries with amount splits.
- **Config parameters:** `ledger_patterns` (list of keywords), `statement_patterns` (list of keywords), `amount_tolerance` (Decimal), `period_scope` (default "month").
- **Example config (UOB One SGD):**
  ```json
  {
    "name": "pattern_cross_source_net_zero",
    "config": {
      "ledger_patterns": ["UOB One cashback"],
      "statement_patterns": ["REBATE", "CASH REBATE"],
      "amount_tolerance": "0.01",
      "period_scope": "month"
    }
  }
  ```
- **Example behavior:**
  - Ledger: `UOB One cashback 2025 11 NOV` amount=119.95 → remove edit -119.95
  - Statement: `ONE CARD ADDITIONAL REBATE` amount=19.95 → add edit +19.95
  - Statement: `UOB ONE CASH REBATE BILL REDEMPTION` amount=100.00 → add edit +100.00
  - Cluster sum: 19.95 + 100.00 = 119.95 ≈ 119.95 ✓ → drop all three edits.

**Heuristic abstraction and concrete implementations:**

**Design principle: Abstract base class for the contract; one concrete class per distinct algorithm. All account-specific behavior lives in config.**

The `Heuristic` abstract base class (ABC) is the **abstraction**. It defines the contract that all heuristics must follow:

```python
from abc import ABC, abstractmethod
from decimal import Decimal
import pandas as pd


class Heuristic(ABC):
  """Abstract base class: defines what all heuristics must do."""
  def __init__(self, enabled: bool = True):
    self._enabled = enabled

  @abstractmethod
  def apply(self, edits_df):
    """Remove redundant edits while preserving gap invariant (sum=0).
    
    Contract: subclasses must implement this method.
    """
    raise NotImplementedError

  @classmethod
  @abstractmethod
  def from_config(cls, heur_cfg: dict):
    """Construct instance from config dict.
    
    Contract: subclasses must implement this classmethod.
    """
    raise NotImplementedError
```

**Four reusable heuristic algorithms** inherit from `Heuristic`. Each encapsulates one distinct algorithm. Account-specific behavior is driven purely by config, not by separate classes:

```python
class NetZeroPairHeuristic(Heuristic):
  """Concrete implementation: Remove pairs of opposite-amount edits within date window."""
  def __init__(self, date_tolerance_days: int, amount_tolerance: Decimal, enabled: bool = True):
    super().__init__(enabled=enabled)
    self._date_tolerance_days = date_tolerance_days
    self._amount_tolerance = amount_tolerance

  @classmethod
  def from_config(cls, heur_cfg: dict):
    c = heur_cfg.get("config", {})
    return cls(
      date_tolerance_days=int(c.get("date_tolerance_days", 3)),
      amount_tolerance=Decimal(str(c.get("amount_tolerance", "0.01"))),
      enabled=bool(heur_cfg.get("enabled", True)),
    )

  def apply(self, edits_df):
    if not self._enabled:
      return edits_df
    # Remove (i, j) pairs where edit_amount[i] == -edit_amount[j] within date_tolerance_days
    # ... algorithm implementation ...
    return edits_df


class SameAmountZeroSumClusterHeuristic(Heuristic):
  """Concrete implementation: Remove clusters of same-amount edits from mixed sources that sum to zero."""
  def __init__(
    self,
    amount_tolerance: Decimal,
    require_mixed_sources: bool = True,
    min_cluster_size: int = 2,
    enabled: bool = True,
  ):
    super().__init__(enabled=enabled)
    self._amount_tolerance = amount_tolerance
    self._require_mixed_sources = require_mixed_sources
    self._min_cluster_size = min_cluster_size

  @classmethod
  def from_config(cls, heur_cfg: dict):
    c = heur_cfg.get("config", {})
    return cls(
      amount_tolerance=Decimal(str(c.get("amount_tolerance", "0.01"))),
      require_mixed_sources=bool(c.get("require_mixed_sources", True)),
      min_cluster_size=int(c.get("min_cluster_size", 2)),
      enabled=bool(heur_cfg.get("enabled", True)),
    )

  def apply(self, edits_df):
    if not self._enabled:
      return edits_df
    # Group by amount; for each group, if mixed sources and cluster_sum ≈ 0, drop all
    # ... algorithm implementation ...
    return edits_df


class KeywordFilterNetZeroHeuristic(Heuristic):
  """Concrete implementation: Remove edits matching keywords if they sum to zero.
  
  Reusable across accounts: DBS Multi (CPF keywords), or any other keyword-based rules.
  """
  def __init__(self, keywords: list, note_field: str = "note", amount_tolerance: Decimal = None, enabled: bool = True):
    super().__init__(enabled=enabled)
    self._keywords = keywords
    self._note_field = note_field
    self._amount_tolerance = amount_tolerance or Decimal("0.01")

  @classmethod
  def from_config(cls, heur_cfg: dict):
    c = heur_cfg.get("config", {})
    return cls(
      keywords=list(c.get("keywords", [])),
      note_field=str(c.get("note_field", "note")),
      amount_tolerance=Decimal(str(c.get("amount_tolerance", "0.01"))),
      enabled=bool(heur_cfg.get("enabled", True)),
    )

  def apply(self, edits_df):
    if not self._enabled:
      return edits_df
    # Select edits where note_field contains any keyword; if subset_sum ≈ 0, drop all
    # ... algorithm implementation ...
    return edits_df


class PatternCrossSourceNetZeroHeuristic(Heuristic):
  """Concrete implementation: Remove edit clusters matching patterns from both sources if balanced.
  
  Reusable across accounts: UOB One (cashback rebates), or any cross-source pattern matching.
  """
  def __init__(
    self,
    ledger_patterns: list,
    statement_patterns: list,
    amount_tolerance: Decimal = None,
    period_scope: str = "month",
    enabled: bool = True,
  ):
    super().__init__(enabled=enabled)
    self._ledger_patterns = ledger_patterns
    self._statement_patterns = statement_patterns
    self._amount_tolerance = amount_tolerance or Decimal("0.01")
    self._period_scope = period_scope

  @classmethod
  def from_config(cls, heur_cfg: dict):
    c = heur_cfg.get("config", {})
    return cls(
      ledger_patterns=list(c.get("ledger_patterns", [])),
      statement_patterns=list(c.get("statement_patterns", [])),
      amount_tolerance=Decimal(str(c.get("amount_tolerance", "0.01"))),
      period_scope=str(c.get("period_scope", "month")),
      enabled=bool(heur_cfg.get("enabled", True)),
    )

  def apply(self, edits_df):
    if not self._enabled:
      return edits_df
    # Find ledger edits matching ledger_patterns and statement edits matching statement_patterns
    # Within same period_scope, check if amounts balance. If yes, drop cluster.
    # ... algorithm implementation ...
    return edits_df
```

```python
class HeuristicsFactory:
  """Registry-based factory for constructing heuristic instances from config."""
  REGISTRY = {
    "net_zero_pair": NetZeroPairHeuristic,
    "same_amount_zero_sum_cluster": SameAmountZeroSumClusterHeuristic,
    "keyword_filter_net_zero": KeywordFilterNetZeroHeuristic,
    "pattern_cross_source_net_zero": PatternCrossSourceNetZeroHeuristic,
  }

  @classmethod
  def build_for_account(cls, config: dict, account: str) -> list:
    """Instantiate all enabled heuristics for an account from config.
    
    Dispatches by heuristic name; account-specific behavior comes from config params.
    """
    specs = []
    specs.extend(config.get("general_heuristics", []))
    specs.extend(config.get("account_heuristics", {}).get(account, []))
    return [cls.REGISTRY[spec["name"]].from_config(spec) for spec in specs]
```

**The Abstraction (`Heuristic`):**
- Defines **what** heuristics must do: implement `apply(edits_df)` and `from_config(config_dict)`.
- Enforces the contract through abstract methods.
- All heuristics inherit from this abstract base class.

**The Concrete Implementations** (four reusable algorithm classes, zero account-specific code):
- `NetZeroPairHeuristic`: Removes opposite-amount pairs within date window. Configured for any account/tolerance.
- `SameAmountZeroSumClusterHeuristic`: Removes same-amount clusters with mixed sources summing to zero. Configurable min cluster size and mixed-source requirement.
- `KeywordFilterNetZeroHeuristic`: Removes edits matching any keyword list if they sum to zero. Reusable for CPF (DBS Multi), internal transfers, or any keyword-based rules.
- `PatternCrossSourceNetZeroHeuristic`: Removes edit clusters matching ledger and statement patterns if amounts balance. Reusable for cashback rebates (UOB One), tax refunds, or any cross-source matching.

**Account-specific behavior = pure configuration:**
- DBS Multi SGD uses `KeywordFilterNetZeroHeuristic` with `keywords=["Flintex CPF", "RSK CPF", "CPF OA", "CPF SA", "CPF MA"]`.
- UOB One SGD uses `PatternCrossSourceNetZeroHeuristic` with `ledger_patterns=["UOB One cashback"]` and `statement_patterns=["REBATE", "CASH REBATE"]`.
- A new account can reuse any of these classes with different config parameters — **no new code required**.

**Factory pattern:** `HeuristicsFactory.build_for_account()` dispatches by config name. Registry is explicit and extensible. All account-specific behavior flows through config, not through class explosion.

**Config-driven account behavior:**

```json
{
  "general_heuristics": [
    {
      "name": "net_zero_pair",
      "config": {
        "date_tolerance_days": 3,
        "amount_tolerance": "0.01"
      }
    },
    {
      "name": "same_amount_zero_sum_cluster",
      "config": {
        "amount_tolerance": "0.01",
        "require_mixed_sources": true,
        "min_cluster_size": 2
      }
    }
  ],
  "account_heuristics": {
    "TWH DBS Multi SGD": [
      {
        "name": "keyword_filter_net_zero",
        "config": {
          "keywords": ["Flintex CPF", "RSK CPF", "CPF OA", "CPF SA", "CPF MA"],
          "note_field": "note",
          "amount_tolerance": "0.01"
        }
      }
    ],
    "TWH UOB One SGD": [
      {
        "name": "pattern_cross_source_net_zero",
        "config": {
          "ledger_patterns": ["UOB One cashback"],
          "statement_patterns": ["REBATE", "CASH REBATE"],
          "amount_tolerance": "0.01",
          "period_scope": "month"
        }
      }
    ],
    "new_account_xyz": [
      {
        "name": "keyword_filter_net_zero",
        "config": {
          "keywords": ["internal transfer", "adjustment"],
          "note_field": "note",
          "amount_tolerance": "0.01"
        }
      }
    ]
  }
}
```

**Key insight:** Same algorithms, different config. Adding a new account with similar rules requires only a config entry — zero new code.

#### Semantic matching layer

For a given scope of period and account, after applying heuristics for known recurring transaction patterns, apply a semantic matching layer to identify add-remove update pairs. The matching occurs between pairs of `add` and `remove` edits on the statement ledger and the action is to reclassify the `remove` edit as an `update` with the `edit_amount` set to the `amount` value of the paired `add` edit.

**user review, manual records update and approval**
As with the edits, prior to implementing actions, user must review the proposed pairs and corresponding edits.  The semantic pairing is presented to user for review and approval. user may manually update the edit and paring records, so the workflow procedure needs to account for a step for user to CRUD the edit and pair records.

**statement-ledger pairing:**
from the set of edits `add` and `remove` to the account ledger, identify add-remove pairs that meet the following conditions

_pairing condition_

1. `add.date` is within `date_tolerance_days` of `remove.date`
2. semantic, or heuristic match of `add.note` and `remove.note` — for example, a description containing "UOB One cashback" in the ledger and "REBATE" in the statement may indicate a semantic match even if the amounts differ due to timing or partial capture. The `add` note will come from the statement and will include the original statement description, which will usually be longer and more descriptive with many unnecessary information such as transaction id, so the semantic match will apply only to a substring of the full description.

_actions_

1. reclassify the `remove` edit as an `update` with the `edit_amount` set to the `amount` value of the paired `add` edit. keep all other fields unchanged.
2. remove the `add` edit.

**Reference statement-ledger pairing snippet:**

```python
def propose_statement_ledger_pairs(edits_df, date_tolerance_days: int, semantic_match_fn):
  """Propose add-remove pairs based on date and semantic match.
  
  Args:
    edits_df: DataFrame with columns [edit, date, note, ...]
    date_tolerance_days: max date delta in days
    semantic_match_fn: callable(add_note, remove_note) -> bool
  
  Returns: list of (add_idx, remove_idx) pairs.
  """
  adds = edits_df[edits_df["edit"] == "add"]
  removes = edits_df[edits_df["edit"] == "remove"]
  pairs = []

  for add_ix, add_row in adds.iterrows():
    cands = removes[
      (removes["date"] - add_row["date"]).abs().dt.days <= date_tolerance_days
      & removes["note"].map(lambda n: semantic_match_fn(add_row["note"], n))
    ]
    if not cands.empty:
      rm_ix = cands.index[0]
      pairs.append((add_ix, rm_ix))

  return pairs
```

#### Transfer-Expense pairing
Due to the double-entry accounting and zero-sum behavior of the cost center `TWH - Personal`, each transfer into or out of the `TWH - Personal` account should have a corresponding set of expense transaction(s) in the ledger for the same period which sum to -1* the transfer amount, and close to and usually on the same transfer date.  any `add`, `remove` or `update` without a corresponding CRUD action to the expenses would break this relationship and voilate the zero sum condition for the cost center account. As a default fallback, this step is manual and it is up to the user to manually repair and apply these updates to the expense transactions in HomeBudget manually to restore the zero-sum condition.

The aim of the transfer-expense pairing step, is to reduce some portion of this manual step by identifying potential pairs of transfer and expense transactions, and staging, still pending user review and approval, the corresponding edits to apply to the HB expenses.  To avoid the complexity of many-to-one pairing algorithm, unless a multi-transaction heuristic is setup, only one-to-one pairs are in scope for the generic semantic match.

The transfer-expense pairing must occur after the statement-ledger pairing step has been approved, so that the `edit_type` and `edit_amount` for the transfer is fixed.

_pairing condition_

1. `transfer.date` is within `date_tolerance_days` of `expense.date`
2. `transfer.amount` == -1 * `expense.amount`

tie-breakers for multiple candidates base on 1. semantic match of `transfer.note` and `expense.note`, then 2. by date proximity.

_actions_

The action will depend on the `edit_type`:

**remove**

delete the expense transaction

**add**

1. add a new expense with date, note set to values from the transfer record
2. set the amount=-1* transfer amount
3. unless a heuristic exists on how to fill them from clues from the transfer record, leave the expense category and subcategory blank. they will not be known and user will have to manually assign them.

**update**

1. update the expense `amount`=-1* the transfer `amount`

**Reference transfer-expense pairing snippet:**

```python
def propose_transfer_expense_pairs(transfer_edits, hb_exp, date_tolerance_days: int):
  """Propose transfer-expense pairs based on amount and date match.
  
  Args:
    transfer_edits: DataFrame with edit records from statement-ledger pairing
    hb_exp: DataFrame with HomeBudget expense transactions
    date_tolerance_days: max date delta in days
  
  Returns: list of (transfer_idx, expense_idx) pairs.
  """
  pairs = []
  for t_ix, t_row in transfer_edits.iterrows():
    cands = hb_exp[
      (hb_exp["date"] - t_row["date"]).abs().dt.days <= date_tolerance_days
      & (hb_exp["amount"] == -t_row["amount"])
    ]
    if not cands.empty:
      e_ix = cands.iloc[0].name
      pairs.append((t_ix, e_ix))
  return pairs
```

#### Method Parameters

Method behavior is controlled by account-specific parameters stored in `txn_heuristics.json` and `tolerance_config.json`.
Both files must be validated during pre-flight at close-session startup, then frozen as a session config snapshot.

| id | parameter             | usage         | config_key                                      | values          |
| -- | --------------------- | ------------- | ----------------------------------------------- | --------------- |
| 01 | `date_tolerance_days` | date window   | `matching_config.accounts.*.date_tolerance_days`| default 3; uob 3|
| 02 | `amount_tolerance`    | amount window | `matching_config.default.amount_tolerance`      | default 0.01    |

**Parameter discovery:**
1. Check `txn_heuristics.json` / `matching_config.accounts[account]` for account-specific override.
2. If not present, use `matching_config.default`.
3. Parameter values are resolved from the startup-validated session config snapshot before invoking the forward pass.

**Config management boundary:**
- User-managed reconciliation policy values are edited through the approved UI interface only.
- Direct manual edits to JSON policy files are out of contract for operational runs.
- Runtime components treat config files as backend artifacts behind the UI and config loader boundary.

**Config source:** `reference/hb-reconcile/account_settings/txn_heuristics.json`

**Requirement ref:** reconciliation-engine.md § Account-group procedures / Bank statement-process accounts § Reconciliation parameters

#### Transaction-level Method Invocation Contract

**Required inputs:**
- `account` — string: account identifier, e.g., `"TWH DBS Multi SGD"`
- `year` — int: calendar year
- `month` — int: calendar month, 1–12
- `hb_gl_txn` — DataFrame: HomeBudget transaction dataset with columns `[account, date, year, month, amount, category, subcategory, payee, notes]`
- `hb_exp` — DataFrame: HomeBudget expenses for the month with columns `[date, year, month, amount, category, subcategory, account, notes]`
- `statements` — DataFrame: statement transaction dataset with columns `[account, date, year, month, amount, description]`
- `hb_account_dim` — DataFrame: account balance dataset with prior-period rows for opening balance derivation
- `statement_balance` — DataFrame: statement period-end balance records for ending-balance cross-check
- `txn_heuristics_config` — dict: loaded configuration from `txn_heuristics.json`

**Pre-conditions:**
1. `hb_gl_txn` and `statements` must be non-empty for the account and period.
2. `hb_account_dim` must contain the prior month row for opening balance and `statement_balance` must contain the current month row for statement ending balance cross-check.
3. Account must be present in at least one heuristics list — general or account-specific — if account-specific heuristics are required.
4. Pre-flight config validation for `txn_heuristics.json` and `tolerance_config.json` must have passed for this session.

**Outputs:**
1. `edits` — DataFrame: table with columns `[source, date, amount, edit, edit_amount, note, ledger_idx, stmt_idx]`
2. `gap` — decimal: final reconcile gap, should be 0.00 or within rounding tolerance
3. `matches` — list: `(ledger_idx, stmt_idx)` tuples from forward pass
4. `stm_ledger_pairs` — list: `(stmt_idx, ledger_idx)` tuples from semantic matching layer
5. `xfr_exp_pairs` — list: `(transfer_idx, expense_idx)` tuples from transfer-expense pairing
6. `metadata` — dict: invocation metadata including opening_balance, statement_end_balance, ledger_end_balance, forward_edits_count, backward_edits_count, heuristics_applied

**Publish gate:**
conditions to publish edits for user review:
- `gap == 0.00`, within currency rounding tolerance 0.01
- `forward_edits == backward_edits` after heuristics application — a mandatory correctness assertion

**Post gate:**
conditions after user review and approval
- User-approved and updated edits received
- User-added transactions incorporated
- Second-pass validation confirms `gap == 0.00` and `forward_edits == backward_edits` after user adjustments
- Zero-sum cost center check for `TWH - Personal` passes

**Failure modes:**
- Missing opening balance → raise `MissingOpeningBalanceError`
- Statement ending balance mismatch > tolerance → log warning, allow user decision to proceed or investigate
- Forward and backward edits differ after heuristics → raise `HeuristicsConsistencyError`; this is a mandatory correctness check
- Unresolved ambiguous matches → edits remain; tolerance evaluation determines acceptance
- Config validation failed at startup → raise `ConfigValidationError`; reconciliation cannot start

**Requirement ref:** reconciliation-engine.md § Shared reconciliation patterns / Shared workflow phases

### Balance-level Method Class

The balance-level method compares derived ending balances between primary and comparison sources and computes a residual gap. It is used by accounts without detailed transaction matching.

#### Generic Balance Equation

The reconcile gap for a balance-level account is:

```
Residual Gap = Primary Balance - Comparison Balance - Σ Staged Adjustments
```

**Definitions:**

- **Primary Balance:** source-of-truth balance for the account group. For example:
  - Cash: HomeBudget ledger ending balance — sum of all `hb_gl_txn.amount` for the period
  - CPF: expected closing balance computed from roll-forward formula
  - Manual-input: pre-adjustment sum of `hb_gl_txn.amount`

- **Comparison Balance:** secondary or user-observed balance for the account group. For example:
  - Cash: user-entered physical cash count
  - CPF: user-entered closing balance from GS UI
  - Manual-input: user-entered account balance from GS UI
  - HomeBudget-native: not applicable; user review and confirmation is the comparison

- **Σ Staged Adjustments:** sum of known intermediate adjustments, transfers, or expenses. For example:
  - Cash: sum of aggregated wallet cash expenses from `cash_staging` for the period
  - CPF: contributions and interest from roll-forward formula
  - Manual-input: zero — no staged adjustments
  - HomeBudget-native: zero — all transactions already in ledger

**Account-specific equation examples:**

*Cash reconciliation:*
```
Residual Gap = HB Current Balance - Actual Physical Cash - Σ Staged Wallet Expenses
```

*CPF reconciliation:*
```
Residual Gap = Expected Closing Balance - User-Entered Closing Balance
where Expected Closing Balance = Opening Balance + Contributions + Interest
```

*Manual-input reconciliation:*
```
Residual Gap = User Balance - Pre-Adjustment Balance
where Pre-Adjustment Balance = sum(hb_gl_txn.amount) for account and period
```

#### Variance Class Outcomes and Tolerance Evaluation

After computing the residual gap, the method classifies the variance into one of three classes:

| id | class             | condition                                | action                | threshold       |
| -- | ----------------- | ---------------------------------------- | --------------------- | --------------- |
| 01 | zero variance     | `abs(residual_gap) <= amount_tolerance`  | close; no adjustment  | account-specific|
| 02 | within tolerance  | `amount_tolerance < abs(gap) <= tol`     | prep adj; confirm post| account-specific|
| 03 | exceeds tolerance | `abs(residual_gap) > tolerance_threshold`| block; require approve| account-specific|

**Tolerance thresholds by account group, from reconciliation-engine.md:**

| id | account_group      | tolerance      | notes                  |
| -- | ------------------ | -------------- | ---------------------- |
| 01 | cash twh sgd       | +/- sgd 20.00  | cash alert threshold   |
| 02 | homebudget-native  | n/a            | user confirmation      |
| 03 | cpf                | rounding       | interest/contrib roll  |
| 04 | manual-input accts | 0.00           | exact match only       |

#### Variance Propagation and Adjustment Preparation

**Within-tolerance variance:**
1. Compute `adjustment_amount = abs(residual_gap)`
2. Auto-prepare adjustment record with fields:
   - `adjustment_id`: generated unique identifier
   - `adjustment_amount`: `abs(residual_gap)` in account currency
   - `residual_gap`: original signed gap value
   - `variance_percentage`: `(residual_gap / primary_balance) * 100`
   - `status`: `"pending_approval"` — awaiting user confirmation
   - `rule_reference`: e.g., `"cash_gap_tolerance"`, `"manual_input_balance_reconciliation"`
   - `session_id`: reconciliation session identifier
   - `created_timestamp`: ISO 8601 timestamp
   - `transaction_date`: last day of period, end of day — 23:59:59
   - `description`: account-group-specific text, e.g., `"Cash reconcile adjustment 2026-02 (pending approval)"`
   - `category`: `"Balancing:Unknown"` or account-group-specific category
3. User is notified; approval is not required for within-tolerance variance.
4. Adjustment is posted on user confirmation of reconciliation completion.

**Exceeds-tolerance variance:**
1. Create adjustment record with same fields as within-tolerance case.
2. Set `status`: `"pending_approval"` with escalation flag.
3. Flag account variance and present adjustment for user review.
4. User must explicitly approve before posting; auto-approval is not allowed.
5. Record user approval timestamp and optional user comment.

**Zero variance:**
1. No adjustment transaction is created.
2. Reconciliation is closed with verification checkpoint.

**Requirement ref:** reconciliation-engine.md § Shared reconciliation patterns / Variance interpretation and adjustment behavior; § Account-group procedures / Cash reconciliation

**Reference balance-level snippet:**

```python
class BalanceLevelMethod(BaseReconciliationMethod):
  def reconcile(self, account, year, month, **inputs):
    primary_balance = inputs["primary_balance"]
    comparison_balance = inputs["comparison_balance"]
    staged_adjustments = inputs.get("staged_adjustments", 0)
    tolerance_threshold = inputs["tolerance_threshold"]

    residual_gap = primary_balance - comparison_balance - staged_adjustments
    abs_gap = abs(residual_gap)

    if abs_gap == 0:
      variance_class = "zero"
    elif abs_gap <= tolerance_threshold:
      variance_class = "within_tolerance"
    else:
      variance_class = "exceeds_tolerance"

    return residual_gap, variance_class
```

#### Balance-level Method Invocation Contract

**Required inputs:**
- `account_group` — string: cash, homebudget_native, cpf, or manual_input
- `account` — string: account identifier
- `year` — int: calendar year
- `month` — int: calendar month
- `primary_balance` — Decimal: source-of-truth balance
- `comparison_balance` — Decimal or None: secondary balance; None for HomeBudget-native
- `staged_adjustments` — Decimal: sum of known intermediate adjustments; default 0.00
- `tolerance_config` — dict: tolerance thresholds from policy configuration

**Pre-conditions:**
1. `primary_balance` must be a valid Decimal value.
2. `comparison_balance` must be a valid Decimal or None for confirmation-based accounts.
3. `account_group` must match one of the supported account-group procedure types.

**Outputs:**
1. `residual_gap` — Decimal: computed gap
2. `variance_class` — string: `"zero"`, `"within_tolerance"`, or `"exceeds_tolerance"`
3. `adjustment_record` — dict or None: adjustment transaction structure if variance is non-zero, else None
4. `metadata` — dict: invocation metadata including primary_balance, comparison_balance, tolerance_threshold, variance_percentage

**Failure modes:**
- Missing required input → raise `MissingBalanceInputError`
- Unsupported account_group → raise `UnsupportedAccountGroupError`
- User confirmation required but not provided → return adjustment in `pending_approval` state

### Cross-cutting Concerns

#### Ledger Consistency Invariants

All reconciliation methods depend on GL schema consistency:

1. **Ledger–statement opening balance consistency:** The opening balance for both ledger and statement slices must be derived from the same source — the prior period `balances` row.
2. **Ledger balance equation:** `ledger_end = opening_balance + sum(ledger.amount)` must hold exactly.
3. **Statement balance equation:** `statement_end = opening_balance + sum(statement.amount)` must hold exactly.
4. **Edits gap invariant:** `gap = ledger_end + sum(edit_amount) - statement_end` must equal 0.00 after valid solution.
5. **Heuristics invariant:** `sum(edit_amount over modified subset) == 0.00` for every heuristic application.

**Validation procedure:**
- Check opening balance availability before slice construction.
- Compute and verify ledger and statement balance equations after slice construction.
- Cross-check statement ending balance against `balances` dataset; log warnings on mismatch.
- Verify final gap equals 0.00 after edits application — a post-condition assertion.
- Verify forward and backward edit sets are identical after heuristics — a correctness assertion.

#### Heuristic Parameter Discovery and Invocation

Heuristics are discovered from startup-validated configuration and invoked at reconcile time:

1. **Config file location:** `reference/hb-reconcile/account_settings/txn_heuristics.json`
2. **Config discovery sequence:**
  - During pre-flight startup, load `txn_heuristics.json` and `tolerance_config.json` through the config loader.
  - Validate schema, required keys, account references, and value domains.
  - Persist a resolved session config snapshot; all reconcile calls read from this snapshot.
   - For each account, check `matching_config.accounts[account]` for account-specific overrides.
   - If no override, use `matching_config.default`.
   - Collect all `general_heuristics` from the config.
   - Collect all `account_heuristics[account]` entries.
3. **Invocation:** Apply heuristics in the order defined in the config.
4. **Determinism requirement:** Heuristic order and parameter values must be deterministic across sessions for idempotency.

**UI safety guard:**
- Policy values intended for operator control are set and managed through the UI interface.
- Direct JSON manipulation by end users is not a supported operational path because it bypasses field validation and corruption safeguards.

**Config example structure:**
```json
{
  "matching_config": {
    "default": {
      "date_tolerance_days": 3,
      "amount_tolerance": 0.01
    },
    "accounts": {
      "TWH UOB One SGD": {
        "date_tolerance_days": 5
      }
    }
  },
  "general_heuristics": [...],
  "account_heuristics": {...}
}
```

#### Reconciliation Idempotency Requirement

Reconciliation is idempotent per session per account: repeated execution with identical inputs — same GL rows, same balances, same period — must produce identical outputs.

**Idempotency requirements:**
1. Match pairs must be deterministic: same forward-pass algorithm, same match test, same parameter values.
2. Edits construction must be deterministic: same row ordering, same index assignment.
3. Heuristics application must be deterministic: same heuristic order, same parameter values, same subset selection.
4. Outputs must be byte-identical: same edits table, same gap value, same metadata.

**Implementation constraints:**
- Use deterministic sorting by date, then by original row index.
- Use exact Decimal arithmetic for all gap and amount calculations; never use float.
- Store heuristic parameters in the invocation metadata for audit trail.
- Fail closed on ambiguous match or configuration discovery failures.

**Requirement ref:** reconciliation-engine.md § End-to-End Delivery Responsibilities § Rerun completeness

#### Account-Group Method Dispatch

Method class selection is determined by account group classification. The classification is owned by the reconciliation engine and must occur before method invocation.

**Account-group classification:**
1. **Bank statement-process accounts:** transactions available from downloaded statement GL
   - Accounts: TWH DBS Multi SGD, TWH CITI USD, TWH UOB One SGD, TWH Visa USD
   - Method: Transaction-level
2. **HomeBudget-native accounts:** no external statement source, user review is comparison
   - Example: 30 Hashemis CC
   - Method: Balance-level
3. **Cash:** user-provided physical cash count
   - Accounts: Cash TWH SGD
   - Method: Balance-level
4. **CPF:** user-provided closing balance and contributions
   - Accounts: CPF OA, CPF SA, CPF MA
   - Method: Balance-level
5. **Manual-input balance-only:** user-provided account balance
   - Examples: Amazon wallet, digital wallets
   - Method: Balance-level

**Out of scope for this module:** IBKR accounts are routed to source integration parsing and deterministic derivation in `ibkr-integration.md`, then persisted to HB and close_book before reconciliation stage execution.

**Dispatch contract:**
- Reconciliation engine owns method selection logic.
- Account-group classifier is called before method invocation.
- Only in-scope accounts are processed; out-of-scope accounts raise `UnsupportedAccountError`.
- Callers do not hard-code method dispatch; they request reconciliation for an account and receive the result.

### Procedure Table

Each account group follows either the transaction-level or balance-level reconciliation method, with defined tolerance and adjustment behavior:

| id | account_group     | method            | tolerance        | posting_target      |
| -- | ----------------- | ----------------- | ---------------- | ------------------- |
| 01 | bank (dbs/citi/uob/visa) | transaction-level | 0.00 (+/-0.01)   | close_book + hb gl  |
| 02 | homebudget-native | balance-level     | user confirmation| close_book only     |
| 03 | cash (twh cash sgd)| balance-level    | +/- sgd 20       | close_book + hb gl  |
| 04 | cpf (oa/sa/ma)    | balance-level     | rounding         | close_book only     |
| 05 | manual-input (wallets)| balance-level  | 0.00 exact       | close_book + hb gl  |

**Details by account group:**

**Bank statement-process accounts:** Transaction-level matching against `hb_gl_txn` using forward/backward passes with heuristics — DBS CPF net-zero, UOB cashback split, and general net-zero pairs. Exact match required: date ±3 days, amount ±0.01. If unmatched items exist after edits, create `Balancing:Unmatched` adjustment per item.

**HomeBudget-native accounts:** User reviews `hb_gl_txn` ledger state and confirms it is final. User may mark corrections to be updated in HB directly. No numeric tolerance; user confirmation is the comparison basis.

**Cash reconciliation:** Balance equation: HB current balance - physical cash count - staged wallet expenses. ±SGD 20 tolerance. Within-tolerance gaps auto-prepare adjustment. Exceeds-tolerance gaps require user approval.

**CPF accounts:** Roll-forward balance validation. User confirms expected closing balance matches HB ledger. Rounding tolerance for interest/contribution calculations. Exceeds-tolerance gaps flagged for user balance correction.

**Manual-input accounts:** Zero tolerance; exact match required between user-entered balance and HB ledger. Any delta requires explicit user approval before adjustment posting.

### Variance Interpretation Matrix

Variance outcomes by class and account group:

**Interpretation:**

- **Zero variance:** Gap equals zero, within rounding tolerance. No adjustment needed. Reconciliation passes directly to closure.
- **Within-tolerance variance:** Gap exceeds zero but is within account-group tolerance threshold. Auto-prepare adjustment when applicable per account group. User notified. Adjustment posted on user confirmation.
- **Exceeds-tolerance variance:** Gap exceeds tolerance threshold. Blocks reconciliation closure. Requires explicit user approval, for example balance correction for CPF or user update for HB-native accounts. User approval recorded with timestamp and optional comment.

### Tolerance Rules by Account Group

This section details tolerance thresholds, variance evaluation, and adjustment behavior for each account group.

#### Bank statement-process accounts

**Scope:** TWH DBS Multi SGD, TWH CITI USD, TWH UOB One SGD, TWH Visa USD
**Method:** Transaction-level matching with heuristics.
**Tolerance:**
- Exact match required on amount: ±0.01 currency precision, to the cent.
- Exact match required on date: ±3 days by default, configurable per account; ±5 days for UOB One SGD when posting delays are observed.
- Account-specific heuristics enabled per `reference/hb-reconcile/account_settings/txn_heuristics.json`:
  - DBS Multi SGD: CPF net-zero cluster matching on keywords: Flintex CPF, RSK CPF, CPF OA/SA/MA.
  - UOB One SGD: cashback split matching across ledger and statement rebate lines.
  - General: net-zero pairs with opposite amounts within date tolerance; same-amount zero-sum clusters.

**Variance evaluation:**
- Forward and backwards matching passes applied per reconciliation-engine spec.
- Unmatched ledger txns generate `remove` edits; unmatched statement txns generate `add` edits.
- Heuristics reduce edit set; final gap computed as: `ledger_end_balance + Σ(edit_amount) - statement_end_balance`.
- Valid solution: gap = 0.00.

**Adjustment outcome:**
- **Zero gap:** reconciliation passes; no adjustment.
- **Exceeds-tolerance gap:** create one adjustment txn per unmatched item cluster with category `Balancing:Unmatched`, amount equal to residual edit, and reference to source statement line and ledger txn indices.
- **Post target:** close_book as primary; HB GL via wrapper as validation-only — matched source rows validated as existing in HB; unmatched source rows create new HB entries via wrapper.

**Example:** DBS Multi SGD statement shows txn on Feb 10, amount SGD 150.00, but HB ledger shows the same txn on Feb 11 — a 1-day delay. Within 3-day tolerance; matched as equivalent.

#### HomeBudget-native accounts

**Scope:** Accounts with no external statement source; managed entirely within HomeBudget — for example, 30 Hashemis CC or other closed-loop card systems with no downloadable statement.
**Method:** Balance-level with user confirmation as comparison basis.
**Tolerance:**
- User confirmation is the tolerance mechanism.
- System presents `hb_gl_txn` ledger state to user; user reviews and confirms all txns are correct or marks txns for correction.

**Variance evaluation:**
- No numeric variance computation.
- User confirmation indicates acceptance of ledger state.
- If user marks corrections: user updates categories or amounts in HomeBudget directly; system re-reads updated state.

**Adjustment outcome:**
- **User confirms ledger:** reconciliation passes; no adjustment.
- **User marks corrections:** user makes changes in HB; system re-reads; reconciliation proceeds with updated state.
- **No HB write-back:** target is close_book only; no adjustment posted via wrapper.

**Approval authority:** User confirmation acts as approval. No additional approval gate required.

#### Cash reconciliation

**Scope:** TWH Cash SGD — physical wallet cash.
**Method:** Balance-level matching with cash aggregation.
**Tolerance:**
- ±SGD 20 — the alert threshold per reconciliation-engine requirements.
- Residual Gap = HB Current Balance - Actual Physical Cash - Σ Staged Wallet Expenses.

**Variance evaluation:**
- Read staged wallet cash aggregates from `cash_staging` schema for period.
- Read `hb_gl_txn` records for account and period; compute HB current balance.
- Retrieve user-entered close balance — observed physical cash count — from GS session UI.
- Compute residual gap.
- If gap within ±SGD 20: within-tolerance condition.
- If gap exceeds ±SGD 20: exceeds-tolerance condition.

**Adjustment outcome:**
- **Within tolerance — gap ≤ ±SGD 20:** system auto-prepares adjustment txn with amount equal to negative gap and category `Balancing:Unknown`; user notified; adjustment posted on user confirmation of reconciliation completion.
- **Exceeds tolerance — gap > ±SGD 20:** system prepares adjustment and flags for user review; user must approve, modify, or investigate variance before adjustment can be posted; user approval is recorded with timestamp and optional comment.
- **Post target:** close_book as primary; HB GL via wrapper — new entries created for previously unstaged cash txns.

**Example:** HB ledger balance = SGD 500. Physical cash count = SGD 478. Staged wallet expenses = SGD 10. Gap = 500 - 478 - 10 = SGD 12. Within ±SGD 20 tolerance; auto-prepare and post SGD -12 adjustment.

#### CPF accounts

**Scope:** CPF OA, CPF SA, CPF MA, CPF RA sub-accounts.
**Method:** Balance-level roll-forward validation with rounding tolerance.
**Tolerance:**
- Rounding tolerance: 0.01, account-group specific per reconciliation-engine requirements.
- Residual Gap = User-Entered Roll-Forward Balance - Computed HB Balance.

**Variance evaluation:**
- System computes roll-forward result per CPF reconciliation rules, covering contribution, interest, and withdrawal tracking.
- User confirms roll-forward result in GS session UI.
- Read `hb_gl_txn` records for account period; compute HB balance before adjustments.
- Retrieve user-entered roll-forward balance from GS UI.
- Compute residual gap.
- If gap within ±0.01 rounding: within-tolerance condition.
- If gap exceeds ±0.01: exceeds-tolerance condition.

**Adjustment outcome:**
- **Within tolerance — gap ≤ ±0.01:** system auto-prepares adjustment with category `Balancing:Rounding` if user confirmation is obtained; adjustment posted on user confirmation.
- **Exceeds tolerance — gap > ±0.01:** system prepares adjustment and flags for user review; user must approve or investigate before posting.
- **Post target:** close_book as primary; HB GL via wrapper — verification entry posted if user-entered balance differs from computed balance.

#### Manual-input accounts

**Scope:** Wallet, balance-only, and manually-reconciled accounts where no statement source is available.
**Method:** Balance-level with user-entered balance as source of truth.
**Tolerance:**
- Zero tolerance: exact match required between user-entered balance and HB ledger.
- Residual Gap = User-Entered Balance - HB GL Balance.

**Variance evaluation:**
- Read `hb_gl_txn` records for account and period; compute HB current balance.
- Retrieve user-entered closing balance from GS session UI.
- Compute residual gap.
- If gap = 0: zero variance.
- If gap ≠ 0: variance flagged for user review; no auto-approve is allowed and explicit user approval is always required.

**Adjustment outcome:**
- **Zero gap:** reconciliation passes; no adjustment.
- **Non-zero gap:** system creates adjustment with amount equal to absolute gap and category assigned per wallet account type; user must approve before posting.
- **Post target:** close_book as primary; HB GL via wrapper — new entry created to reconcile user-entered balance with HB state.

## Adjustment and Audit Contracts

This section specifies the adjustment transaction contract, bill conflict policy, and reconciliation session record requirements for persistence, audit, and traceability.

### Adjustment Transaction Contract

**Required Fields and Data Types:**

| id | field                     | type            | constraints                   | usage                    |
| -- | ------------------------- | --------------- | ----------------------------- | ------------------------ |
| 01 | `adjustment_id`           | uuid/hash       | pk; generated                 | audit + lineage key      |
| 02 | `session_id`              | uuid            | fk; non-null                  | link to session          |
| 03 | `account_id`              | string          | valid account; non-null       | account scope            |
| 04 | `period_key`              | string yyyy-mm  | non-null                      | period scope             |
| 05 | `adjustment_amount`       | dec(28,2)       | +/- allowed                   | post variance            |
| 06 | `residual_gap`            | dec(28,2)       | abs precision                 | source gap value         |
| 07 | `variance_percentage`     | dec(6,4)        | informational                 | user review context      |
| 08 | `status`                  | enum            | generated/pending/approved/posted | lifecycle state      |
| 09 | `rule_reference`          | string          | valid policy ref              | tolerance trigger        |
| 10 | `method_class`            | enum            | txn_level or balance_level    | method used              |
| 11 | `transaction_date`        | iso date        | inside period                 | posting date             |
| 12 | `created_timestamp`       | iso datetime    | immutable at create           | creation audit anchor    |
| 13 | `user_approval_timestamp` | iso datetime    | null until approve            | approval audit anchor    |
| 14 | `user_comment`            | string(4000)    | optional                      | approval notes           |
| 15 | `description`             | string(500)     | machine-readable              | ledger posting text      |
| 16 | `category_code`           | string          | mapped `gl_code`; non-null    | gl assignment            |
| 17 | `source_reference`        | string          | optional                      | source lineage ref       |
| 18 | `auto_approve_flag`       | boolean         | default false                 | bypass marker            |

**Field Validation Rules:**

- `adjustment_amount` must be non-zero or status must remain `generated` and adjustment must not post.
- `residual_gap` absolute value must be ≥ `adjustment_amount` when both populated.
- `period_key` must match `session_id` period; cross-period adjustments rejected.
- `account_id` must be valid in account master.
- `status` transitions follow strict lifecycle: `generated` → `pending_approval` when tolerance is exceeded → `approved` → `posted`. No reverse transitions allowed.
- `category_code` must exist in mapping schema at creation time.
- `rule_reference` must reference a defined tolerance rule or system policy.
- `transaction_date` must fall within `period_key` calendar month.
- `user_approval_timestamp` must be null if status is `generated`; non-null if status is `approved` or `posted`.

**Posting Targets:**

- **close_book schema — required:** All adjustments post to `close_book` schema at account and period scope. Posting is idempotent: same adjustment retried produces one record.
- **HomeBudget GL — conditional:** Per account group:
  - Bank accounts: new GL entry with source reference to statement.
  - Cash: new GL entry with category `Balancing:Unknown`.
  - Investments: valuation adjustment entry per investment account type.
  - Wallets: new GL entry per wallet account type.
  - CPF and manual-input: verification entry if user-entered values adjusted; otherwise no HB posting.

**Status Lifecycle and Auto-Approve Conditions:**

- **Auto-approve:** Variance is zero, or variance within tolerance and account group allows auto-approve — bank zero-gap, cash ≤±SGD 20, and CPF ≤±0.01.
- **User-approval required:** Variance exceeds tolerance threshold; user must explicitly approve before posting.

**User-Approval Conditions by Account Group:**

| id | account_group | tolerance      | auto_approve    | user_approval_required |
| -- | ------------- | -------------- | --------------- | ---------------------- |
| 01 | bank accounts | 0.00 exact     | yes (zero gap)  | yes (any unmatched)    |
| 02 | cash          | +/- sgd 20     | yes (<=20)      | yes (>20)              |
| 03 | cpf           | +/- 0.01 round | yes (<=0.01)    | yes (>0.01)            |
| 04 | wallets       | 0.00 exact     | yes (zero gap)  | yes (any variance)     |
| 05 | manual-input  | 0.00 exact     | no              | yes (any variance)     |

### Bill Accrual Conflict Policy

**Conflict Classification Matrix:**

Four conflict classes govern bill accrual treatment during reconciliation:

| id | class | definition                    | engine_behavior                | acceptance_rule          |
| -- | ----- | ----------------------------- | ------------------------------ | ------------------------ |
| 01 | a     | billed = settled; same period | standard reconcile             | direct link; no override |
| 02 | b     | near eom (+/-3 days)          | shift txn date to bill period  | auto-approved timing     |
| 03 | c     | cross-period timing           | expense + bridge transfers     | override may be needed   |
| 04 | d     | partial payment across periods| expense + multi transfers      | override may be needed   |

**Acceptance Rules Detail:**

- **Blocking condition:** Any remaining difference between total billed amount and total settlement amount after all transfers is a blocking reconciliation finding unless explicitly approved with written rationale.
- **Shared billing bridge account:**
  - One account per session, e.g., `shared_billing_bridge_<period_key>`.
  - Transfers in = full bill amount on bill date; transfers out = each payment amount on settlement date.
  - Net position = transfers in - transfers out = unpaid remainder at period close.
  - At period close, net position is reconciliation checkpoint.
- **Override policy:**
  - Class A: no override needed.
  - Class B: auto-approved; no override decision.
  - Classes C and D: user may override with written rationale, which is required; override is audited.

**Bill Conflict Record Fields:**

| id | field                      | type             | content                    |
| -- | -------------------------- | ---------------- | -------------------------- |
| 01 | `conflict_id`              | uuid             | unique id                  |
| 02 | `session_id`               | uuid             | session context            |
| 03 | `bill_id`                  | string           | bill domain ref            |
| 04 | `conflict_class`           | enum             | a, b, c, or d             |
| 05 | `bill_statement_reference` | string           | bill source id             |
| 06 | `bank_statement_reference` | string           | bank source id             |
| 07 | `bill_amount`              | dec(28,2)        | full billed amount         |
| 08 | `settlement_amount`        | dec(28,2)        | total settled amount       |
| 09 | `pseudo_account_id`        | string           | bridge account id          |
| 10 | `pseudo_account_balance`   | dec(28,2)        | close net position         |
| 11 | `policy_applied`           | string           | policy code                |
| 12 | `override_rationale`       | string(4000)     | required for override      |
| 13 | `created_timestamp`        | iso datetime utc | audit anchor               |

### Reconciliation Session Record

**Session Record Fields:**

| id | field                    | type             | constraints               | purpose               |
| -- | ------------------------ | ---------------- | ------------------------- | --------------------- |
| 01 | `session_id`             | uuid             | pk; generated at start    | unique session id     |
| 02 | `period_key`             | string yyyy-mm   | non-null                  | period scope          |
| 03 | `account_id`             | string           | valid account; non-null   | account scope         |
| 04 | `account_group`          | string           | enum bank/cash/cpf...     | dispatch context      |
| 05 | `method_class`           | enum             | txn/balance/account model | algo class            |
| 06 | `session_status`         | enum             | pending..failed           | closure state         |
| 07 | `variance_amount`        | dec(28,2)        | null if zero              | pre-adjust gap        |
| 08 | `variance_tolerance`     | dec(28,2)        | group-specific            | threshold reference   |
| 09 | `exceeds_tolerance_flag` | boolean          | true if variance > tol    | approval gate         |
| 10 | `user_approval_decision` | enum             | pending/approve/etc       | user action           |
| 11 | `user_approval_timestamp`| iso datetime utc | null until decision       | approval audit        |
| 12 | `override_rationale`     | string(4000)     | required if overridden    | reason record         |
| 13 | `adjustment_id`          | uuid             | fk adjustment             | link to adjustment    |

**Lineage Requirements:**

Each session must retain source-of-truth references for traceability:

| id | lineage_anchor              | content                    | examples                      |
| -- | --------------------------- | -------------------------- | ----------------------------- |
| 01 | `statement_source_reference`| comparison source id       | statements row, bill          |
| 02 | `statement_fetch_date`      | source fetch date          | iso date                      |
| 03 | `statement_source_hash`     | deterministic source hash  | sha256 of source payload      |
| 04 | `hb_sync_timestamp`         | hb wrapper sync time       | iso datetime                  |
| 05 | `hb_sync_version`           | hb wrapper version         | reproducibility marker        |
| 06 | `matching_algorithm_version`| reconcile method version   | txn_level_v2.1...             |
| 07 | `reconciliation_outcome`    | final result               | matched/adjusted/failed       |

**Audit Trail Checkpoints:**

| id | checkpoint           | timestamp_field                  | condition          | purpose               |
| -- | -------------------- | -------------------------------- | ------------------ | --------------------- |
| 01 | session open         | `session_created_timestamp`      | always             | start account run     |
| 02 | validation pass      | `validation_checkpoint_timestamp`| if successful      | source validated      |
| 03 | matching complete    | `matching_complete_timestamp`    | always             | variance computed     |
| 04 | variance evaluated   | `variance_evaluation_timestamp`  | always             | tolerance compared    |
| 05  | adjustment generated| `adjustment_created_timestamp`   | if variance != 0   | adjustment created    |
| 05a | semantic matching   | `semantic_matching_timestamp`    | if txn-level       | stm-ledger pairs      |
| 05b | xfr-expense pairs   | `xfr_exp_pairing_timestamp`      | if xfr edits exist | transfer-expense pairs|
| 06  | user approval       | `user_approval_timestamp`        | if exceeds tol     | explicit decision     |
| 07 | adjustment posted    | `adjustment_posted_timestamp`    | if adjustment exists| posted to targets    |
| 08 | session closed       | `session_closed_timestamp`       | always             | end account run       |

**Closure Criteria — all must be satisfied:**

- All transactions in scope have match outcome: matched, in edits list, or marked non-matching with explanation.
- No unexplained blocking variance at close time; variance is zero, within tolerance, or user-approved.
- All account-group specific gates pass — for example, category completeness for bank accounts and HB write-back success.
- If variance within tolerance, automatic adjustment generated and staged.
- If variance exceeds tolerance, user approval recorded with timestamp and optional comment.
- Adjustment, if generated, posted to close_book; HB write-back attempted for applicable account groups.
- Reconciliation report generated with period, account, variance, tolerance status, and checkpoint outcomes.
- Zero-sum cost center check for `TWH - Personal` passes: net of all posted and staged transfer edits equals net of all staged expense edits.
- Session status transitioned to `complete`, `overridden`, or `failed`.

**Retention and Queryability:**

- Session records retained indefinitely in SQLite for audit trail.
- Queryable by `session_id` for full session audit, by `period_key` + `account_id` for per-account close audit, by `session_status` for workflow state, and by `variance_amount` for variance analysis.
- Post-close audit queries executable without external files or archives.

### Close_book Schema Integration

**Adjustment Posting:**

Adjustments persist to `close_book` schema using deterministic, idempotent upsert:

| id | operation               | idempotency_rule                         |
| -- | ----------------------- | ---------------------------------------- |
| 01 | create adjustment       | same variance -> same `adjustment_id`    |
| 02 | user approves           | status -> `approved`; timestamp updated  |
| 03 | post to close_book      | upsert by `adjustment_id`; no duplicates |
| 04 | statement builder reads | deterministic aggregate by period        |

**Schema Ownership:**

- **Reconciliation engine:** Owns adjustment lifecycle from generation through approval and posting to close_book.
- **close_book:** Reconciliation engine's output; statement builder's exclusive input.
- **Statement builder:** Reads close_book only; no direct reads from `statements`, `hb`, or other source schemas.

**Cross-Query Dependencies:**

Statement builder uses close_book exclusively:

| id | query_key                   | dependency_filter                        | characteristic        |
| -- | --------------------------- | ---------------------------------------- | --------------------- |
| 01 | is personal expense         | close_book class=`personal_expense`      | gl_code aggregate     |
| 02 | is investment pnl           | close_book class in (`investment_pnl`,`m2m`,`forex`)| includes m2m/forex |
| 03 | bs assets                   | close_book class=`asset`                 | includes valuations   |
| 04 | bs liabilities              | close_book class=`liability`             | includes accruals     |
| 05 | ni = delta net assets check | is net income vs bs net assets delta     | blocking validation   |

**Determinism and Rerun Safety:**

- Same reconciliation session run twice produces identical adjustments with idempotent posting.
- `adjustment_id` is deterministic hash of `(session_id, account_id, period_key, rule_reference, residual_gap)`.
- Upsert: if adjustment_id exists, update status and user_approval fields only; do not duplicate.
- Statement builder queries are deterministic: same close_book snapshot produces identical statement aggregates.

## Module Invocation Contract

The reconciliation engine is invoked by the workflow orchestrator at reconcile stage 6, per account. The invocation contract is:

**Inputs:**
- `account_id`: Account to reconcile.
- `period_key`: Calendar month in YYYY-MM format.
- `method_class`: transaction_level or balance_level, derived from account group.
- Source schemas: `statements`, `hb_gl_txn`, `hb_account_dim`, `cash_staging`, and others as determined by method and account group.
- Tolerance threshold: Per account group.
- Heuristics config: From `txn_heuristics.json` or mapping schema.

**Outputs:**
- `session_record`: Reconciliation session with status, variance, approval decision.
- `adjustment_record`: If variance non-zero; adjustment_id, amount, status, posting target.
- `stm_ledger_pairs`: list of `(stmt_idx, ledger_idx)` tuples from semantic matching (txn-level accounts only).
- `xfr_exp_pairs`: list of `(transfer_idx, expense_idx)` tuples from transfer-expense pairing (txn-level accounts only).
- `report`: Human-readable reconciliation report with matched/unmatched counts, variance explanation.

**Error Handling:**
- If required source datasets missing: blocking error; rerun data sync.
- If matching fails — unmatched items exceed tolerance: review-level error; user approval required.
- If HB write-back fails: adjustment staged in close_book; retry logged.
- If SQLite posting fails: reconciliation blocked; error surfaced.


