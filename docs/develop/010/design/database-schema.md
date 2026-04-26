# Database Schema Design

## Table of contents

- [Overview](#overview)
- [Data ownership model](#data-ownership-model)
- [Primary SQLite schema](#primary-sqlite-schema)
- [Financial statement storage model](#financial-statement-storage-model)
- [JSON sidecar for novel decisions](#json-sidecar-for-novel-decisions)
- [Data integrity and immutability](#data-integrity-and-immutability)
- [Synchronization model](#synchronization-model)
- [Backup and retention model](#backup-and-retention-model)
- [Migration and versioning approach](#migration-and-versioning-approach)

## Overview

This document defines app owned persistence for monthly close. The primary store is a single SQLite database `financial_statements.db` that consolidates both raw statement data and reconciled ledger balances. Novel reconciliation decisions are stored in local per period JSON files to support algorithm maturation with low friction.

The schema maintains a two-stage reconciliation model:

- **Statement layer**: Raw imported transactions, historized statement balances, and session-scoped reconcile balances
- **Ledger layer**: Durable ledger balances computed from HomeBudget ledger after variance resolution

This two-stage model supports the reconciliation strategies defined in [domain-model.md](domain-model.md): ReconcileBase for stage-1 statement digital twin import and balance verification, and ReconcileLedger for stage-2 HomeBudget ledger transaction matching when required. ReconcileBank is retained as a backward-compatible alias. See [module-design.md](module-design.md) for implementation interfaces.

Financial statements are persisted as first class relational records with revision history, line item hierarchy, and export artifact tracking.

## Data ownership model

### Two-stage reconciliation model

The schema separates raw statement data from reconciled ledger balances to support transparent variance tracking and implements the reconciliation patterns from [domain-model.md](domain-model.md).

**Stage 1 - Statement import**:

- Parse bank statement CSV and XLSX files
- Insert transactions into `statement_transaction`
- Derive and persist historized digital twin balance in `statement_balance`
- Materialize session-scoped active reconciliation balance in `reconcile_balance`
- Log import metadata in `statement_import`

**Stage 2 - Ledger reconciliation**:

- Query HomeBudget ledger for period transactions
- Compute ledger balance
- Store ledger balance in `account_balance`
- Compare `account_balance.balance` against `reconcile_balance.balance`
- Apply account-type-specific reconciliation strategy:
    - **ReconcileBase** (statement digital twin, IBKR, CPF, wallets): Create `StatementBalance`, validate `ReconcileBalance`, then perform simple variance detection
    - **ReconcileLedger** (bank accounts, credit cards): Stage-2 transaction matching with 7 scenarios before final balance comparison
- Create `reconciliation_variance` record when difference exceeds tolerance
- Post adjustment transactions to HomeBudget when approved

**Variance formula**:
```
variance = account_balance.balance - reconcile_balance.balance
```

**Implementation note**: Domain balance types are intentionally separate in [domain-model.md](domain-model.md): `StatementBalance` is historized in `statement_balance`, `ReconcileBalance` is session-scoped in `reconcile_balance`, and `LedgerBalanceSnapshot` is durable in `account_balance`. See [module-design.md](module-design.md) for ReconcileBase and ReconcileLedger module contracts.

### App owned

- Period status and workflow log
- Raw statement transactions and observed balances
- Reconciled account balances and statement outputs
- Reconciliation variance records
- Exchange rate archive
- Statement import audit trail

### External system owned

- HomeBudget master ledger and account metadata
- Operational Google Sheets source:
    - Cash expenses workbook (`gsheet/cash-expenses.json`) as the retained raw source for cash reconciliation (`Google Forms -> Google Sheets`)
- Legacy Google Sheets helper workbooks, parity and backfill only:
  - CPF contributions workbook (`gsheet/cpf.json`)
  - Financial statements workbook (`gsheet/financial-statements.json`)
  - HomeBudget helper workbook (`gsheet/homebudget-workbook.json`)
  - IBKR IBA investment account workbook (`gsheet/ibkr-iba.json`)
  - Shared expenses workbook (`gsheet/shared-expenses.json`)
- Raw statement files and online account portals

### Shared by contract

- Account mapping file in `data/monthly-closing/accounts.json`
- User period inputs in `data/monthly-closing/inputs.json`

## Primary SQLite schema

Database name, `financial_statements.db`.

### Statement layer tables

Raw imported statement data, historized digital twin balances, and session-scoped reconcile balances.

```sql
CREATE TABLE period (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    period_key TEXT UNIQUE NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('open', 'in_progress', 'closed', 'failed')),
    created_at TEXT NOT NULL,
    finalized_at TEXT
);

CREATE TABLE reconciliation_session (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_key TEXT UNIQUE NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('active', 'closed', 'failed', 'aborted')),
    started_at TEXT NOT NULL,
    ended_at TEXT,
    period_id INTEGER NOT NULL,
    created_by TEXT,
    notes TEXT,
    FOREIGN KEY(period_id) REFERENCES period(id)
);

CREATE TABLE statement_import (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reconciliation_session_id INTEGER NOT NULL,
    import_key TEXT UNIQUE NOT NULL,
    period_id INTEGER NOT NULL,
    account_id TEXT NOT NULL,
    filename TEXT NOT NULL,
    file_size_bytes INTEGER,
    parser_name TEXT NOT NULL,
    transaction_count INTEGER,
    duplicates_skipped INTEGER,
    new_transactions INTEGER,
    status TEXT NOT NULL CHECK (status IN ('success', 'partial', 'error', 'rolled_back')),
    error_message TEXT,
    s3_object_url TEXT,
    created_at TEXT NOT NULL,
    completed_at TEXT,
    FOREIGN KEY(reconciliation_session_id) REFERENCES reconciliation_session(id),
    FOREIGN KEY(period_id) REFERENCES period(id)
);

CREATE TABLE statement_transaction (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reconciliation_session_id INTEGER NOT NULL,
    statement_import_id INTEGER NOT NULL,
    account_id TEXT NOT NULL,
    period_id INTEGER NOT NULL,
    txn_date TEXT NOT NULL,
    description TEXT NOT NULL,
    amount REAL NOT NULL,
    balance REAL,
    raw_data_json TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(reconciliation_session_id) REFERENCES reconciliation_session(id),
    FOREIGN KEY(period_id) REFERENCES period(id),
    FOREIGN KEY(statement_import_id) REFERENCES statement_import(id)
);

CREATE TABLE statement_balance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    period_id INTEGER NOT NULL,
    account_id TEXT NOT NULL,
    balance REAL NOT NULL,
    balance_date TEXT NOT NULL,
    currency TEXT NOT NULL,
    statement_import_id INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(statement_import_id, account_id),
    FOREIGN KEY(period_id) REFERENCES period(id),
    FOREIGN KEY(statement_import_id) REFERENCES statement_import(id)
);

CREATE TABLE reconcile_balance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reconciliation_session_id INTEGER NOT NULL,
    period_id INTEGER NOT NULL,
    account_id TEXT NOT NULL,
    balance REAL NOT NULL,
    balance_date TEXT NOT NULL,
    currency TEXT NOT NULL,
    statement_balance_id INTEGER,
    created_at TEXT NOT NULL,
    UNIQUE(reconciliation_session_id, period_id, account_id),
    FOREIGN KEY(reconciliation_session_id) REFERENCES reconciliation_session(id),
    FOREIGN KEY(period_id) REFERENCES period(id),
    FOREIGN KEY(statement_balance_id) REFERENCES statement_balance(id)
);
```

### Ledger and workflow tables

Reconciled balances, workflow orchestration, and variance tracking.

```sql
CREATE TABLE workflow_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    period_id INTEGER NOT NULL,
    step_name TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('pending', 'in_progress', 'completed', 'failed')),
    started_at TEXT,
    completed_at TEXT,
    message TEXT,
    FOREIGN KEY(period_id) REFERENCES period(id)
);

CREATE TABLE account_balance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    period_id INTEGER NOT NULL,
    account_id TEXT NOT NULL,
    balance REAL NOT NULL,
    currency TEXT NOT NULL,
    UNIQUE(period_id, account_id),
    FOREIGN KEY(period_id) REFERENCES period(id)
);

CREATE TABLE reconciliation_variance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    period_id INTEGER NOT NULL,
    account_id TEXT NOT NULL,
    variance REAL NOT NULL,
    tolerance REAL NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('unexplained', 'explained', 'waived')),
    explanation TEXT,
    created_at TEXT NOT NULL,
    resolved_at TEXT,
    FOREIGN KEY(period_id) REFERENCES period(id)
);

CREATE TABLE exchange_rate (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rate_date TEXT NOT NULL,
    currency_pair TEXT NOT NULL,
    rate REAL NOT NULL,
    source TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(rate_date, currency_pair)
);

CREATE TABLE financial_statement (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    period_id INTEGER NOT NULL,
    statement_type TEXT NOT NULL CHECK (statement_type IN ('income_statement', 'balance_sheet', 'cash_flow')),
    reporting_currency TEXT NOT NULL,
    as_of_date TEXT NOT NULL,
    period_snapshot TEXT NOT NULL,
    revision_no INTEGER NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('draft', 'final', 'superseded')),
    effective_from TEXT NOT NULL,
    effective_to TEXT,
    is_current INTEGER NOT NULL CHECK (is_current IN (0, 1)),
    generated_at TEXT NOT NULL,
    finalized_at TEXT,
    source_snapshot_json TEXT,
    UNIQUE(period_id, statement_type, reporting_currency, revision_no),
    UNIQUE(period_id, statement_type, reporting_currency, period_snapshot),
    FOREIGN KEY(period_id) REFERENCES period(id)
);

CREATE TABLE statement_section (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    statement_id INTEGER NOT NULL,
    section_key TEXT NOT NULL,
    display_name TEXT NOT NULL,
    sort_order INTEGER NOT NULL,
    UNIQUE(statement_id, section_key),
    FOREIGN KEY(statement_id) REFERENCES financial_statement(id)
);

CREATE TABLE statement_line_item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    statement_id INTEGER NOT NULL,
    section_id INTEGER NOT NULL,
    line_code TEXT NOT NULL,
    line_label TEXT NOT NULL,
    hierarchy_level INTEGER NOT NULL,
    parent_line_code TEXT,
    line_kind TEXT NOT NULL CHECK (line_kind IN ('leaf', 'subtotal', 'total', 'comparison')),
    sign_policy TEXT NOT NULL CHECK (sign_policy IN ('natural', 'invert')),
    amount_native REAL,
    amount_reporting REAL NOT NULL,
    currency_native TEXT,
    sort_order INTEGER NOT NULL,
    calc_metadata_json TEXT,
    UNIQUE(statement_id, line_code),
    FOREIGN KEY(statement_id) REFERENCES financial_statement(id),
    FOREIGN KEY(section_id) REFERENCES statement_section(id)
);

CREATE TABLE statement_export_artifact (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    statement_id INTEGER NOT NULL,
    artifact_type TEXT NOT NULL CHECK (artifact_type IN ('pdf', 'csv', 'xlsx', 'json_snapshot')),
    file_path TEXT,
    s3_object_url TEXT,
    checksum_sha256 TEXT,
    generated_at TEXT NOT NULL,
    UNIQUE(statement_id, artifact_type),
    FOREIGN KEY(statement_id) REFERENCES financial_statement(id)
);
```

## Financial statement storage model

- `financial_statement` stores statement headers and SCD Type 2 revision history keyed by `period_snapshot`.
- `statement_section` stores top level and intermediate section blocks.
- `statement_line_item` stores normalized line item values and hierarchy.
- `statement_export_artifact` stores generated output files linked to one statement revision.

Revision policy:

- Multiple revisions per period and statement type are allowed.
- History is modeled as SCD Type 2.
- `period_snapshot` identifies the immutable input snapshot used for a revision.
- Only one row should be current for a period, statement type, and reporting currency, where `is_current = 1` and `effective_to` is null.
- When a newer revision is promoted, the prior current row is closed with `effective_to` and marked `is_current = 0`.
- Only one revision should be marked `final` for a period, statement type, and reporting currency at close time.

## JSON sidecar for novel decisions

Path pattern, `data/monthly-closing/YYYY-MM/reconciliation-decisions.json`.

```json
[
  {
        "period_key": "2026-02",
    "account_id": "cash_twh_sgd",
        "variance": -5.23,
    "currency": "SGD",
    "decision_type": "novel",
    "resolution": "added manual transaction",
    "explanation": "statement fee row was missing from source extract",
    "resolved_at": "2026-03-01T15:23:00Z"
  }
]
```

Policy:

- Store only non routine decisions.
- Exclude routine patterns already encoded in rules.
- Keep file append only for the period until final close.

## Data integrity and immutability

- Enforce foreign keys at connection start.
- Validate period id, date, and currency fields before write.
- Enforce one reconcile balance row per reconciliation session, period, and account.
- Enforce one account balance row per period and account.
- Enforce one line code per statement revision.
- Enforce one export artifact type per statement revision.
- Enforce one current statement row per period, statement type, and reporting currency.
- Enforce immutable `period_snapshot` once a statement row is written.
- Keep `statement_balance` append-only and historized by import session.
- Block updates to statement_transaction, reconcile_balance, and account_balance when period status is `closed`.
- Block updates to financial_statement, statement_section, and statement_line_item when period status is `closed`, except status transition from `draft` to `final` before final close.
- Keep workflow log and statement_import append only.
- Statement transactions are immutable after import, delete and reimport entire session on correction.
- Reconcile balances are ephemeral: on reconciliation session close, purge `reconcile_balance` for that session after final variance artifacts are persisted.

## Synchronization model

- Statement files sync direction, app reads raw CSV and XLSX exports, imports to statement_transaction table, and writes PDF to S3.
- Statement balance sync direction, app derives historized digital twin balances and stores them in `statement_balance`.
- Reconcile balance sync direction, app creates session-scoped `reconcile_balance` for active reconciliation work.
- HomeBudget sync direction, app reads ledger transactions and computes ledger balances, stores in account_balance table, then writes reconciled adjustments back to HomeBudget.
- Cash expense workbook sync direction, app reads operational raw cash-expense rows from the linked Google Form sheet for reconciliation.
- Legacy workbook sync direction, for non-cash-expense helper workbooks app may read ranges only in parity_mode or backfill_mode.
- Report publication direction, app may publish summary outputs to Google Sheets for user review, but this is not a system-of-record path.
- Financial statement sync direction, app computes statement revisions from reconciled balances and persisted period data, stores headers and lines in statement tables, then emits export artifacts.
- Reconciliation flow:
    - validate `reconcile_balance.balance` against historized `statement_balance.balance`
    - compare `reconcile_balance.balance` vs `account_balance.balance`
    - create variances when difference exceeds tolerance
- Conflict model, detect source drift after acquisition and force step rerun.

## Backup and retention model

- Backup `financial_statements.db` to S3 after close.
- Upload PDF reports to S3 by `year/month` path.
- Keep exchange rates monthly for two year rolling window at minimum.
- Keep local JSON decision files with the same period retention as snapshots.
- Retain historized `statement_balance` as part of reconciliation audit history.
- Do not retain `reconcile_balance` from past reconciliation sessions; purge on session close and exclude from long-term retention exports.

## Migration and versioning approach

- Keep schema migrations in ordered SQL files.
- Track migration level in a metadata table.
- Apply forward only migrations in routine workflow.
- Reserve destructive changes for explicit maintenance mode.
- Migrate legacy `statement_reports` payload records into normalized financial statement tables with a one-time backfill script.
