# Domain Model Design

## Table of contents

- [Overview](#overview)
- [Modeling principles](#modeling-principles)
- [Assumptions](#assumptions)
- [Core value objects](#core-value-objects)
- [Core entities](#core-entities)
- [Account type behavior rules](#account-type-behavior-rules)
- [Transaction model and patterns](#transaction-model-and-patterns)
- [Reconciliation model](#reconciliation-model)
- [Financial statement model](#financial-statement-model)
- [Statement persistence model](#statement-persistence-model)
- [Examples from current data](#examples-from-current-data)

## Overview

This document defines the domain model used by monthly close. The model is source aware but source independent, so domain rules stay stable while adapters evolve.

**Core principle**: Statements are the source of truth for account balances and transactions. HomeBudget is the ledger that reflects statement data with classification and reorganization, but net transactions and balances must match statements after reconciliation.

The model supports a two-stage reconciliation workflow:

1. **Statement layer**: Import raw statement transactions and produce historized `StatementBalance` plus session-scoped `ReconcileBalance`
2. **Ledger layer**: Produce `LedgerBalanceSnapshot` from HomeBudget and reconcile it against `ReconcileBalance`

See [database-schema.md](database-schema.md) for persistence implementation and [module-design.md](module-design.md) for reconciliation strategy classes.

## Modeling principles

- Statements are the ultimate source of truth for balances and transactions.
- Use immutable value objects for period, money, rate, and variance.
- Use explicit entities for accounts, transactions, and snapshots.
- Keep source lineage on every transaction and balance event.
- Keep reconciliation decisions explicit and auditable.
- Reconciliation complexity varies by account type and statement availability.

## Assumptions

**Assumptions**

- Account mapping table will fully bridge naming differences.
- Statement parser outputs normalized signed amounts.

**Design decisions**: to be performed by the app

- Pending transactions before cut-off are carried after reconciliation date and annotated with the original transaction date in description.
- Rare same day duplicate statement rows use uniqueness suffixes in description, for example `-01`, `-02`.
- Cash flow statement remains deferred for MVP while schema support remains enabled for later phases.

## Core value objects

### Period

- **Fields:** `year`, `month`, `period_id`.
- **Validation:** month from 1 to 12 and year at least 2000.
- **Example:** `2026-02`.

### Money

- **Fields:** `amount`, `currency`.
- **Precision rule:** currency specific decimal precision.
- **Current policy:** SGD and USD use 2 decimal places.

### ExchangeRate

- **Fields:** `rate_date`, `currency_pair`, `rate`, `source`.
- **Example:** pair from current config, `USD/SGD`.

### Variance

- **Fields:** `amount`, `currency`, `tolerance`, `status`.
- **Status values:** `unexplained`, `explained`, `waived`.

## Core entities

### Account

- **Identity:** stable `account_id` mapped across sources.
- **Core fields:** name, HomeBudget name, statement name, currency, owner.
- **Classification fields:** HomeBudget type and reporting asset type.

### Transaction

- **Identity:** source id plus derived uniqueness key.
- **Core fields:** account, date, amount, type, description, category.
- **Lineage fields:** source system, source file, load timestamp.

### StatementBalance

- **Identity:** statement snapshot revision and account.
- **Fields:** `balance`, `balance_date`, `currency`, source statement lineage.
- **Purpose:** historized digital twin closing balance from parsed statement data.
- **Lifecycle rule:** append-only history retained for audit, rerun comparison, and parser quality checks.
- **Implementation note:** persisted in `statement_balance` table. See [database-schema.md](database-schema.md).

### ReconcileBalance

- **Identity:** reconciliation session, period, and account.
- **Fields:** `balance`, `balance_date`, `currency`, source linkage to statement balance snapshot.
- **Purpose:** ephemeral balance used as active reconciliation target for the session.
- **Lifecycle rule:** session-scoped and ephemeral: retained only for the active reconciliation session and purged after session close.
- **Session scope rule:** one user session can contain multiple reconciliation sessions, where each reconciliation session is scoped to one period close run.
- **Reconciliation rule:** must be validated against `StatementBalance` before ledger reconciliation.
- **Implementation note:** persisted in `reconcile_balance` table linked to `reconciliation_session`. See [database-schema.md](database-schema.md).

### LedgerBalanceSnapshot

- **Identity:** period and account.
- **Fields:** `balance`, `currency`.
- **Purpose:** stage-2 ledger reconciliation and period-close statement generation.
- **Persistence rule:** durable historical record retained as part of period close outputs.
- **Implementation note:** persisted in `account_balance` table. See [database-schema.md](database-schema.md).

### ReconciliationDecision

- **Identity:** period, account, and decision key.
- **Fields:** variance context, action, explanation, novelty flag, approver.
- **Storage behavior:** only novel decisions are persisted to JSON sidecar.

### PeriodSnapshot

- **Identity:** period.
- **Fields:** aggregate statement values, status, finalization metadata.
- **Rule:** immutable after close.

### FinancialStatement

- **Identity:** `period_id`, `statement_type`, `reporting_currency`, and `revision_no`.
- **Core fields:** `as_of_date`, `period_snapshot`, `status`, generation timestamps, and source lineage summary.
- **SCD Type 2 fields:** `effective_from`, `effective_to`, and `is_current`.
- **Statement types:** `income_statement`, `balance_sheet`, and `cash_flow` when enabled.
- **Status values:** `draft`, `final`, and `superseded`.

### StatementLineItem

- **Identity:** statement id and stable `line_code`.
- **Core fields:** section key, display label, hierarchy depth, sign policy, and sort order.
- **Amount fields:** native amount and reporting amount.
- **Behavior:** leaf rows store direct values and subtotal rows are calculated and persisted for deterministic reruns.

### StatementExportArtifact

- **Identity:** statement id and `artifact_type`.
- **Artifact types:** `pdf`, `csv`, `xlsx`, and `json_snapshot`.
- **Core fields:** storage target, checksum, generated timestamp, and optional external URL.

## Account type behavior rules

### Budget

- **Example:** `TWH - Personal`.
- **Expected month end behavior:** closes near zero after complete expense booking.
- **Main use:** cost center for personal expenses and income routing logic.
- **Reconciliation:** not statement reconciled, balance tracked in HomeBudget only.

### Cash

- **Examples:** wallet and bank accounts.
- **Rule:** can be payment method and can hold interest income.
- **Month end expectation:** non negative for standard cash accounts.
- **Reconciliation complexity:**
  - **Wallets:** Simple balance gap calculation with adjustment transaction (uses ReconcileBase).
  - **Bank accounts:** Stage 1 statement digital twin verification with ReconcileBase, followed by stage-2 ledger transaction matching with ReconcileLedger.

### Credit

- **Examples:** cards and settlement credit accounts.
- **Rule:** same flow as cash with liability sign behavior.
- **Reconciliation complexity:** Stage 1 statement digital twin verification with ReconcileBase, followed by stage-2 ledger transaction matching with ReconcileLedger.

### External

- **Examples:** investment position accounts.
- **Rule:** valuation and investment specific classification logic.
- **Reconciliation complexity:**
  - **IBKR brokerage:** Greenfield transaction creation from statement, balance verification only (uses ReconcileBase).
  - **CPF retirement:** Simple placeholder matching for predictable monthly contributions and annual interest, balance verification (uses ReconcileBase).

## Transaction model and patterns

### Canonical transaction types

- Expense
- Income
- Transfer in
- Transfer out
- Balance rows are excluded from transactional reconciliation logic

### Cost center double entry pattern

- Transfer from payment account to cost center.
- Expense or income row booked in cost center account.

### Uniqueness and dedupe

- Key fields are account, date, amount, and description.
- Collision strategy adds sequence suffix in description.

## Reconciliation model

Reconciliation follows a two-stage workflow aligned with the persistence model in [database-schema.md](database-schema.md):

**Stage 1 - Statement import**:
- Parse bank statement CSV/XLSX files
- Store raw transactions in statement layer
- Derive and persist historized `StatementBalance`
- Materialize session-scoped `ReconcileBalance` from `StatementBalance` for active reconciliation
- Reconciliation strategy: `ReconcileBase` validates `ReconcileBalance` against `StatementBalance` consistency.

**Stage 2 - Ledger reconciliation**:
- Query HomeBudget ledger for period transactions
- Compute and persist `LedgerBalanceSnapshot`
- Compare `LedgerBalanceSnapshot.balance` vs session-scoped `ReconcileBalance.balance`
- Resolve variances through matching or adjustments
- Reconciliation strategy: `ReconcileLedger` performs transaction matching when pre-existing HomeBudget rows must be reconciled.

**Reconciliation formula**:
```text
StatementBalance (historized digital twin)
-> validated into ReconcileBalance (session-scoped)
vs LedgerBalanceSnapshot (from HomeBudget ledger)
= Residual Variance
```

**Variance formula**: `variance = ledger_balance - reconcile_balance`

**Cash reconciliation equation (wallet mode)**:
`closing_cash_expected = opening_cash + cash_inflows - cash_outflows`

`cash_gap = cash_count_observed - closing_cash_expected`

When `abs(cash_gap)` is greater than tolerance, generate an adjustment candidate and require checkpoint review.

### Base reconciliation strategy (ReconcileBase)

Used for: IBKR brokerage, CPF retirement, cash wallets

**Pattern**:
- Import parsed statement transactions into the statement digital twin.
- Derive historized `StatementBalance` from imported statement rows.
- Verify session-scoped `ReconcileBalance` is internally consistent.
- Validate `ReconcileBalance` against `StatementBalance` for the same account and period.
- Compare `LedgerBalanceSnapshot.balance` vs `ReconcileBalance.balance`.
- Generate variance record when difference exceeds tolerance.
- Post adjustment transaction to HomeBudget when approved.
- No transaction-level matching required.

**Account-specific variations**:
- **IBKR**: Greenfield transaction creation from statement, balance verification only.
- **CPF**: Predictable placeholder matching (monthly contributions, annual interest), then balance verification.
- **Wallets**: Balance gap calculation with single adjustment transaction.

### Ledger reconciliation strategy (ReconcileLedger)

Used for: Bank accounts, credit cards

Renamed to **Ledger reconciliation strategy (`ReconcileLedger`)** for clarity. `ReconcileBank` is retained only as a backward-compatible alias.

Inherits from ReconcileBase and adds stage-2 HomeBudget ledger transaction matching logic.

**Seven reconciliation scenarios**:
1. **Exact match**: Statement transaction matches HomeBudget transaction (date, amount, description)
2. **Missing in HomeBudget**: Statement transaction has no HomeBudget match → add transaction
3. **Missing in statement**: HomeBudget transaction has no statement match → may be pending or error
4. **Amount mismatch**: Matching date/description but different amount → investigate and adjust
5. **Duplicates**: Same transaction appears multiple times → deduplicate with sequence suffix
6. **Pending transactions**: HomeBudget transaction dated before statement cutoff but not on statement → carry forward
7. **Net-zero pairs**: Unmatched add and remove edits that cancel out → heuristic filtering option

**Pattern**:
- Transaction matching uses conservative one-to-one forward matching.
- Unmatched statement rows produce "add" edits.
- Unmatched HomeBudget rows produce "remove" or "pending" edits.
- Pending transaction detection for HomeBudget txns before statement cut-off.
- Heuristics can remove net-zero edit pairs without changing residual gap.
- Manual intervention required for unresolved over-tolerance variance.

**Complexity rationale**:
- Bank statements reconcile against existing HomeBudget placeholder transactions.
- Requires complex matching logic to handle timing differences and errors.
- IBKR statements are greenfield (no pre-existing HomeBudget transactions).
- CPF placeholders are highly predictable and stable.

Detailed reconciliation methods by account category and account type are maintained in `docs/accounting-logic.md` under `Reconciliation` and `Reconciliation methods by account type`.

See [module-design.md](module-design.md) for ReconcileBase and ReconcileLedger interface details.

## Financial statement model

- Statement hierarchy, statement type then section then line item.
- Income statement axis, category hierarchy with period sums.
- Balance sheet axis, asset and liability hierarchy with point in time balances.
- Period comparison, current month and prior month values are persisted as separate line items with comparison metadata.
- Conversion rule, foreign balance converted then revalued by forex logic before final line item persistence.

## Statement persistence model

- Financial statements are first class period outputs, not only rendered files.
- Statement history follows SCD Type 2 versioning.
- Each statement generation creates a new revision row, preserving prior revisions for audit and rerun comparison.
- `period_snapshot` stores the immutable period snapshot key used to identify the exact input state for that revision.
- Statement header and line items are not revised in place after period close.
- Exports are derivative artifacts linked to a specific statement revision.

SCD Type 2 rules:

- New revision inserts a new statement row with a new `period_snapshot` value.
- Prior current row is closed by setting `effective_to` and `is_current = 0`.
- New row is opened with `effective_from` and `is_current = 1`.
- Historical rows remain queryable and immutable.

Lifecycle:

- `draft`, produced after calculations complete and before manual approval.
- `final`, approved output used for distribution and period snapshot.
- `superseded`, historical revision retained after a newer final revision is promoted before close.

## Examples from current data

- User input artifact contains account `Cash TWH SGD` with period value capture.
- Existing reconciliation artifact has variance state and pending approval payload.
- Existing gsheet config confirms balances, forex_rates, and accounts ranges.
- Financial statements for the same period can coexist as multiple revisions with one final revision per statement type and currency.