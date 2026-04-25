# Application Workflows Design

**Document Type**: Design Specification  
**Status**: Draft  
**Created**: 2026-03-08  
**Purpose**: Define intended automated workflows for the monthly closing application

---

## Table of Contents

- [Overview](#overview)
- [Design Principles](#design-principles)
- [Workflow Architecture](#workflow-architecture)
- [Primary Workflow: Monthly Closing](#primary-workflow-monthly-closing)
- [Subprocess: Bill Payment and Shared Costs](#subprocess-bill-payment-and-shared-costs)
- [Subprocess: Cash Reconciliation](#subprocess-cash-reconciliation)
- [Subprocess: Account Statement Reconciliation](#subprocess-account-statement-reconciliation)
- [Checkpoint and Validation Gates](#checkpoint-and-validation-gates)
- [Error Handling and Recovery](#error-handling-and-recovery)
- [Session State Management](#session-state-management)
- [Parallel Execution Opportunities](#parallel-execution-opportunities)

---

## Overview

This document defines the intended workflows for the financial statements application, focusing on automation, modularity, and user checkpoints. It describes the **target state** after implementing the MVP design, in contrast to the current manual workflow documented in [docs/current-workflow.md](../../current-workflow.md).

### Key Differences from Current Workflow

| Aspect | Current Workflow | App Workflow (Target) |
|--------|------------------|----------------------|
| **Orchestration** | Manual steps with Google Sheets intermediaries | CLI-driven with automated orchestration |
| **Data flow** | Manual copy/paste between systems | Programmatic adapters with validation |
| **State tracking** | Manual notes and spreadsheet logs | SQLite session state with audit trail |
| **Error handling** | Ad-hoc user investigation | Structured error taxonomy with recovery paths |
| **Checkpoints** | Implicit user review points | Explicit validation gates with approval prompts |
| **Parallelization** | Strictly sequential | Parallel execution where data-independent |

### Related Documents

- [Current Workflow](../../current-workflow.md) â€” Existing manual/semi-automated process
- [Workflow Architecture](workflow-architecture.md) â€” Detailed orchestration and state machine design (to be created)
- [Bill Payment Workflow](bill-payment-workflow.md) â€” Subprocess design (to be created)
- [Cash Reconcile Workflow](../../cash-reconcile.md) â€” Existing subprocess implementation
- [Domain Model](domain-model.md) â€” Core entities and business rules
- [Data Flow](data-flow.md) â€” End-to-end data transformations

---

## Design Principles

### 1. Modular and Composable

Each workflow step is an independent module with:

- Clear input requirements and output contracts
- Explicit dependencies on other steps
- Ability to run standalone for testing or reruns

### 2. Fail-Fast with Clear Errors

Validation happens early:

- Pre-flight checks before any mutations
- Data validation at transformation boundaries
- Clear error messages with remediation guidance

### 3. Idempotent Where Possible

Steps can be safely rerun:

- Duplicate detection for transaction imports
- Checksum validation for already-processed files
- Rollback capability for failed operations

### 4. User Checkpoints at Decision Points

Automation pauses for manual review when:

- Variance exceeds tolerance thresholds
- Novel reconciliation patterns detected
- Data conflicts require business judgment
- Final approval before committing changes

### 5. Audit Trail for All Mutations

Every change is logged with:

- Timestamp and session identifier
- Input data snapshot
- Decision rationale (automated or manual)
- Rollback information if applicable

---

## Workflow Architecture

### Execution Model

**Primary interface**: CLI with step commands
```bash
# Run full workflow
closing run --period 2026-02

# Run individual steps
closing forex --period 2026-02
closing accounts --period 2026-02 --account-type wallets
closing reconcile --period 2026-02 --mode cash
closing statements --period 2026-02
```

**Orchestration pattern**: State machine with checkpoint gates

```
[Session Start] â†’ [Pre-flight] â†’ [Forex] â†’ [Accounts] â†’ [Reconcile] â†’ [Statements] â†’ [Finalize]
                      â†“             â†“          â†“            â†“             â†“             â†“
                  [Validate]   [Checkpoint] [Checkpoint] [Checkpoint] [Checkpoint] [Archive]
```

**State persistence**: SQLite session log table

- Current step status
- Checkpoint approval records
- Error and warning history
- Novel decision log (JSON sidecar for edge cases)

---

## Primary Workflow: Monthly Closing

### Overview

The monthly closing workflow aggregates financial data from multiple sources, performs reconciliation, and generates consolidated statements.

**Current time taken**: 188-460 minutes current manual workflow

### Workflow Steps

#### Step 1: Pre-flight Checks - Automated

**Purpose**: Validate environment and prerequisites before starting

**Inputs**:

- Period identifier (YYYY-MM)
- Session configuration

**Validations**:

- HomeBudget database accessible
- Required credentials present for enabled integrations (S3 required only when archive is enabled, Google Sheets required for cash reconciliation raw source and optional for parity/review publication)
- No conflicting active session for same period
- Prior period finalized (if sequential dependency exists)

**Outputs**:

- Session record created
- Validation report

**Checkpoint**: Continue/abort decision if warnings present

---

#### Step 2: Forex Rate Fetch - Automated

**Purpose**: Retrieve and store exchange rates for the period

**Inputs**:

- Period end date
- Currency pairs (USD/SGD primary)

**Process**:

1. Query Yahoo Finance API for period-end rates
2. Validate rate is within expected range (tolerance check)
3. Store in exchange_rates table
4. Mark period as having valid forex data

**Outputs**:

- Exchange rate records in SQLite
- Optional: Post to Google Sheets for user review

**Checkpoint**: Review if rate variance > 5% from prior period

**Error handling**:

- API failure â†’ retry with exponential backoff
- Rate out of range â†’ flag for manual review
- Missing historical comparison â†’ warning only

---

#### Step 3: Account Balance Updates - Semi-automated

**Purpose**: Fetch and reconcile account balances from multiple sources

**Sub-workflows**:

1. **Wallet accounts** (direct HomeBudget query, automated)
2. **IBKR brokerage** (statement import + adapter, semi-automated)
3. **CPF retirement** (statement import + adapter, semi-automated)
4. **Credit accounts** (statement import + adapter, semi-automated)

**For each account type**:

**Inputs**:

- Downloaded statement files (manual prerequisite)
- Period identifier
- Account configuration

**Process**:

1. Parse statement file (PDF/CSV/Excel)
2. Extract transactions and balances
3. Import to statement digital twin (SQLite)
4. Validate imported balance matches observed balance
5. Run reconciliation against HomeBudget ledger
6. Generate proposed adjustment transactions
7. Upload raw statements to S3

**Outputs**:

- Statement transactions in SQLite
- Raw statements in S3
- Reconciliation variance report
- Updated statement tables with reconciled balances matched to source confirmations

**Checkpoint**: Approve reconciliation adjustments if variance within tolerance

**Manual steps remaining**:

- Statement download (requires MFA/login)
- Balance observation from online portal (input to JSON)

**Automation**:

- Statement parsing and transaction extraction
- Balance validation
- Reconciliation algorithm execution
- Transaction generation

---

#### Step 4: Bill Payment Processing - Semi-automated

**Purpose**: Process bill statements and allocate shared costs

**See**: [Bill Payment Workflow](bill-payment-workflow.md) for detailed design

**Inputs**:

- Billing statements (SP Services, Singtel, UOB CC, etc.)
- Shared expense allocation rules

**Process**:

1. Parse billing statements
2. Extract line items and consumption metrics
3. Apply shared cost allocation (1/3 personal, 2/3 flatmates)
4. Generate HomeBudget transactions (expense + settlement)
5. Update consumption tracking database
6. Upload raw statements to S3

**Outputs**:

- Parsed bill transactions
- Shared cost settlement entries
- Consumption metrics logged
- Raw statements in S3

**Checkpoint**: Review allocation before posting to HomeBudget

---

#### Step 5: Cash Reconciliation - Semi-automated

**Purpose**: Reconcile physical cash with HomeBudget ledger

**See**: [Cash Reconcile Implementation Summary](../../cash-reconcile.md)

**Inputs**:

- Cash count (user input via JSON or CLI prompt)
- Cash expenses (from Google Form -> Google Sheets)
- HomeBudget Cash TWH SGD ledger

**Process**:

1. Fetch recent cash expenses from Google Sheets
2. Query HomeBudget ledger for period transactions
3. Calculate residual variance
4. Generate adjustment transaction if variance exists

**Outputs**:

- Reconciliation report
- Adjustment transaction (if needed)

**Checkpoint**: Alert if adjustment > Â±SGD 20

---

#### Step 6: HomeBudget Transaction Commit - Semi-automated

**Purpose**: Commit all approved transactions to HomeBudget database

**Inputs**:

- Approved transaction queue from:
        - Account reconciliations
        - Bill payment allocations
        - Cash reconciliation adjustments
        - Forex adjustment transactions

**Process**:

1. Deduplicate transactions against existing HomeBudget records
2. Validate double-entry balancing
3. Batch insert via homebudget wrapper
4. Trigger mobile app sync notification (if configured)

**Outputs**:

- HomeBudget database updated
- Transaction commit log

**Checkpoint**: Final approval before commit (show transaction summary)

---

#### Step 7: Financial Statement Generation - Automated

**Purpose**: Generate consolidated financial statements from reconciled data

**Inputs**:

- HomeBudget ledger (post-reconciliation)
- Account balances (verified)
- Exchange rates (stored)
- Period configuration

**Process**:

1. Query HomeBudget for period income and expenses
2. Apply category hierarchy and mapping rules
3. Calculate forex M2M adjustments
4. Generate income statement
5. Generate balance sheet
6. Create period snapshot (immutable)
7. Insert or update statement revision rows as `draft` with SCD Type 2 semantics

**Outputs**:

- Income statement (SQLite + PDF)
- Balance sheet (SQLite + PDF)
- Period snapshot record
- `financial_statement` header, sections, and line items for current draft revision

**Checkpoint**: Review financial statements for accuracy

---

#### Step 8: Report Publication and Archive - Automated

**Purpose**: Archive statements and publish for review

**Inputs**:

- Generated PDF statements
- Period snapshot

**Process**:

1. Upload PDF to S3 with organized naming
2. Optionally post summary to Google Sheets for review
3. Create session close-out log
4. Promote approved draft statement revisions to `final` and supersede prior current revisions
5. Mark period as finalized

**Outputs**:

- S3 archive URLs
- Session completion report

**Checkpoint**: None (informational only)

---

## Subprocess: Bill Payment and Shared Costs

Detailed design to be documented in [bill-payment-workflow.md](bill-payment-workflow.md).

### Key Features

- Parser registry for multiple statement formats (DBS, UOB, Citi, BOA, SP Services, Singtel)
- Shared cost allocation with configurable split rules
- Consumption metric extraction and tracking
- Direct HomeBudget transaction generation

### Integration Points

- Runs as part of Step 4 in monthly closing workflow
- Can run standalone for bill processing outside monthly close
- Outputs feed into HomeBudget commit step

---

## Subprocess: Cash Reconciliation

Detailed implementation documented in [../../cash-reconcile.md](../../cash-reconcile.md).

### Key Features

- Google Sheets integration for operational cash-expense raw source (Google Forms-linked)
- HomeBudget ledger query and variance calculation
- Tolerance-based alerting (Â±SGD 20)
- Automatic adjustment transaction generation

### Integration Points

- Runs as part of Step 5 in monthly closing workflow
- Can run standalone for mid-month cash checks
- Outputs feed into HomeBudget commit step

---

## Subprocess: Account Statement Reconciliation

Detailed algorithm documented in `reference/hb-reconcile/docs/reconcile.md`.

### Key Features

- Statement digital twin (SQLite) as source of truth
- Transaction-level matching with conservative forward-matching algorithm
- Gap detection and closure with add/remove/update edits
- Heuristic filters to remove net-zero edit pairs
- Manual intervention for over-tolerance variances

### Integration Points

- Runs for each account in Step 3 (Account Balance Updates)
- Uses common reconciliation engine across account types
- Different tolerance and approval thresholds per account type

---

## Checkpoint and Validation Gates

### Checkpoint Types

| Type | Trigger | User Action Required |
|------|---------|---------------------|
| **Pre-flight warning** | Missing optional data or minor config issues | Acknowledge and continue or abort |
| **Variance review** | Reconciliation variance > tolerance | Investigate and approve/reject adjustment |
| **Novel decision** | Unrecognized reconciliation pattern | Explain rationale and approve action |
| **Final approval** | Before committing transactions to HomeBudget | Review summary and confirm |
| **Statement review** | After financial statement generation | Review PDF and approve finalization |

### Validation Gates

**Entry validation** (before step execution):

- Required inputs present
- Data format valid
- No conflicting state

**Exit validation** (after step execution):

- Outputs produced successfully
- Data integrity constraints satisfied
- Balance equations hold

**Cross-step validation**:

- Period snapshot consistency
- Double-entry balance preservation
- No orphaned transactions

---

## Error Handling and Recovery

### Error Classification (High-Level)

Canonical, detailed error taxonomy is defined in `docs/develop/design/error-handling-validation.md`.
This workflow document keeps only high-level operational mapping.

| Workflow Error Group | Canonical Class (Detailed Doc) | Typical Recovery |
|----------------------|---------------------------------|------------------|
| **Configuration** | `ConfigError` | Fail fast and correct configuration before rerun |
| **External integration** | `ExternalApiError` | Retry with backoff, then checkpoint for manual retry |
| **Data quality** | `DataQualityError` | Correct source data and rerun the step |
| **Data freshness** | `DataFreshnessError` | Warn or block based on step criticality |
| **Import conflict** | `ImportConflictError` | Resolve dedupe/conflict and replay import |
| **Reconciliation** | `ReconciliationError` | User review, variance explanation, or override at checkpoint |
| **Posting** | `PostingError` | Roll back transactional writes and replay |
| **Logic/invariant** | `LogicError` | Stop workflow and fix implementation issue |

### Rollback Strategy

**Transaction-level rollback**:

- HomeBudget transaction batch insert is atomic
- SQLite transactions with ROLLBACK on error
- Backup snapshot before mutation steps

**Session-level rollback**:

- Mark session as failed in state log
- Preserve error context for debugging
- Allow fresh restart from last checkpoint

**Manual recovery**:

- Session state inspection command
- Ability to skip/redo individual steps
- Override tolerance checks with documented rationale

---

## Session State Management

### State Schema

```sql
CREATE TABLE period (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        period_key TEXT UNIQUE NOT NULL,
        year INTEGER NOT NULL,
        month INTEGER NOT NULL,
        status TEXT NOT NULL, -- 'open', 'in_progress', 'closed', 'failed'
        created_at TEXT NOT NULL,
        finalized_at TEXT
);

CREATE TABLE workflow_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        period_id INTEGER NOT NULL,
        step_name TEXT NOT NULL,
        status TEXT NOT NULL, -- 'pending', 'in_progress', 'completed', 'failed'
        started_at TEXT,
        completed_at TEXT,
        message TEXT,
        FOREIGN KEY(period_id) REFERENCES period(id)
);

CREATE TABLE reconciliation_session (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_key TEXT UNIQUE NOT NULL,
        period_id INTEGER NOT NULL,
        status TEXT NOT NULL, -- 'active', 'closed', 'failed', 'aborted'
        started_at TEXT NOT NULL,
        ended_at TEXT,
        created_by TEXT,
        notes TEXT,
        FOREIGN KEY(period_id) REFERENCES period(id)
);
```

Decision capture note:

- Novel and user-intervention reconciliation decisions are persisted in `data/monthly-closing/YYYY-MM/reconciliation-decisions.json`.

### Session Lifecycle

1. **Session creation**: User runs `closing run --period YYYY-MM`
2. **Step execution**: Each step updates status and logs inputs/outputs
3. **Checkpoint handling**: Step pauses, records decision, resumes
4. **Session completion**: All steps completed, period finalized
5. **Session archive**: Older sessions pruned after retention period (default: 12 months)

---

## Parallel Execution Opportunities

### Current Sequential Dependencies

```
Pre-flight â†’ Forex â†’ Accounts â†’ Reconcile â†’ Commit â†’ Statements â†’ Archive
```

### Potential Parallelization (Future Enhancement)

**Account updates** can run in parallel (data-independent):
```
        â”Œâ”€ Wallets â”€â”
Forex â”€â”€â”¤â”€ IBKR â”€â”€â”€â”€â”¤â”€â†’ [Consolidate] â†’ Reconcile
        â””â”€ CPF â”€â”€â”€â”€â”€â”˜
```

**Bill payment** can run in parallel with account updates:
```
        â”Œâ”€ Accounts â”€â”
Forex â”€â”€â”¤â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤â”€â†’ [Consolidate] â†’ Reconcile
        â””â”€ Bills â”€â”€â”€â”€â”˜
```

**Report generation** can be parallelized by statement type:
```
              â”Œâ”€ Income Statement â”€â”€â”
Commit â”€â”€â”€â”€â”€â”€â”€â”¤â”€ Balance Sheet â”€â”€â”€â”€â”€â”¤â”€â†’ [Consolidate] â†’ Archive
              â””â”€ (Cash Flow future)â”€â”˜
```

**Implementation note**: Parallelization is a post-MVP enhancement. Initial implementation remains sequential for simplicity and easier debugging.

---

## Future Enhancements

### Planned Improvements

1. **Interactive web UI** â€” Visual workflow progress with step-by-step guidance
2. **Background worker** â€” Async execution for long-running steps
3. **Notification system** â€” Email/SMS alerts for checkpoints and completion
4. **Historical comparison** â€” Auto-variance detection vs. prior periods
5. **Machine learning** â€” Auto-categorization and anomaly detection

### Integration Opportunities

1. **Direct bank API integration** â€” Replace manual statement download
2. **Mobile app sync** â€” Automatic HomeBudget cloud sync trigger
3. **Cloud backup** â€” Automated SQLite backup to S3
4. **Collaborative review** â€” Multi-user approval workflow

---

## Summary

This workflow design represents the target state for the financial statements application MVP. It balances automation with necessary manual checkpoints, providing:

- **Efficiency**: 60%+ time reduction vs. current manual workflow
- **Reliability**: Validation gates and error handling at each step
- **Auditability**: Complete session and decision logging
- **Flexibility**: Modular design allows step reruns and parallel execution

Next steps to complete this design:

1. Detailed workflow architecture state machine ([workflow-architecture.md](workflow-architecture.md))
2. Bill payment subprocess specification ([bill-payment-workflow.md](bill-payment-workflow.md))
3. Module interface definitions ([module-design.md](module-design.md))
4. Error handling framework ([error-handling-validation.md](error-handling-validation.md))




