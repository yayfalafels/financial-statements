---
title: Source Systems and Data Lineage
doc_type: requirements
topic_type: owner
owner: source-systems-lineage
scope: poc
---
# Source Systems and Data Lineage

## Table of contents

- [Purpose and scope](#purpose-and-scope)
- [Reference documents](#reference-documents)
- [Source system catalog](#source-system-catalog)
- [Data flow overview](#data-flow-overview)
- [Source precedence and authority](#source-precedence-and-authority)
- [Transaction lineage requirements](#transaction-lineage-requirements)
- [Balance lineage requirements](#balance-lineage-requirements)
- [Cross-path reconciliation points](#cross-path-reconciliation-points)
- [Audit and traceability requirements](#audit-and-traceability-requirements)

## Purpose and scope

This document defines the source systems, data flow paths, and traceability requirements that underpin the monthly financial close workflow.

## Reference documents

- [accounting logic and mapping](accounting-logic.md)
- [reconciliation engine](reconciliation-engine.md)
- [transaction category mapping](transaction-category-mapping.md)
- [data model](data-model.md)

**Primary scope:**
- Identify and catalog all data sources that feed into the financial statements.
- Define which source system is the source of truth for each account or transaction category.
- Define the minimum lineage and audit trail requirements to trace financial statement outputs back to originating source systems.
- Define data precedence rules when multiple sources provide overlapping information.

**Out of scope:**
- Implementation details of extraction, transformation, or loading, ETL, logic.
- Technical schema design or database architecture.
- Integration-specific error handling, retries, or failure workflows. See integration-specific requirement pages for those.


## Source system catalog

The source systems listed below contribute to the monthly close:

| id | system name               | source type                        | lineage anchor           |
| -- | ------------------------- | ---------------------------------- | ------------------------ |
| 01 | Statement Digital Twin    | statement files + PDF archive      | app DB `statements` schema |
| 02 | HomeBudget                | wrapper sync + direct user inputs  | hb sync transaction uid  |
| 03 | IBKR                      | CSV statements                      | IBKR activity statement  |
| 04 | CPF                       | Google Sheets UI                    | closing-session workbook |
| 05 | User Manual Inputs        | user-observed balances and qty      | Google Sheets UI entries |
| 06 | Yahoo Finance             | market data API                     | API response snapshot    |
| 07 | Bills Domain              | parsed bills plus bridge UI input   | app DB `bills` schema    |

> HomeBudget sync schema objects and canonical table names are defined in [data-model.md](data-model.md).

**Source inputs and usage**

| id | format    | usage        | vol  | account group  | account                        | stmt_process |
| -- | --------- | ------------ | ---- | -------------- | ------------------------------ | ------------ |
| 01 | csv       | txn          | high | bank accounts  | TWH DBS Multi SGD              | yes          |
| 02 | pdf       | archive      | high | bank accounts  | TWH DBS Multi SGD              | yes          |
| 03 | csv       | txn          | high | bank accounts  | TWH Visa USD                   | yes          |
| 04 | pdf       | archive      | high | bank accounts  | TWH Visa USD                   | yes          |
| 05 | csv       | txn          | high | bank accounts  | TWH CITI USD                   | yes          |
| 06 | pdf       | archive      | high | bank accounts  | TWH CITI USD                   | yes          |
| 07 | excel     | txn          | high | bank accounts  | TWH UOB One SGD                | yes          |
| 08 | pdf       | archive      | high | bank accounts  | TWH UOB One SGD                | yes          |
| 09 | pdf       | txn, archive | low  | bank accounts  | Wells Fargo USD                | no           |
| 10 | gs        | txn          | high | cash           | TWH Cash SGD                   | no           |
| 11 | gs[1]     | balance      | low  | wallets        | TWH Cash USD                   | no           |
| 12 | gs[1]     | balance      | low  | wallets        | others - EZLink, Amazon, etc.. | no           |
| 13 | csv[2]    | txn          | low  | ibkr           | IBKR IBA                       | no           |
| 14 | csv[2]    | txn          | low  | ibkr           | IBKR IRA                       | no           |
| 15 | gs[1]     | qty          | low  | investments    | Silver Bullions                | no           |
| 16 | api       | unit price   | low  | investments    | Silver Bullions                | no           |
| 17 | api       | forex rates  | low  | forex          | --                             | no           |
| 18 | pdf       | txn          | high | bills          | Singtel                        | no           |
| 19 | pdf       | txn          | high | bills          | PUB SP Services                | no           |
| 20 | gs[1]     | balance      | high | bank accounts  | TWH DBS Multi SGD              | no           |
| 21 | gs[1]     | balance      | high | bank accounts  | TWH Visa USD                   | no           |
| 22 | gs[1]     | balance      | high | bank accounts  | TWH CITI USD                   | no           |
| 23 | gs[1]     | balance      | high | bank accounts  | TWH UOB One SGD                | no           |
| 24 | gs[1]     | balance      | low  | bank accounts  | Wells Fargo USD                | no           |

1. user-entered via closing-session Google Sheets workbook
2. in later version MVP will use direct api

Statement-process boundary:
- Only the four accounts TWH DBS Multi SGD, TWH Visa USD, TWH CITI USD, and TWH UOB One SGD flow through `statements.py` into the app consolidated database `statements` schema.
- Wells Fargo USD is a bank account but is outside the regular `statements.py` and app `statements` schema process.
- Some accounts have no independent statement backup source; in those cases HomeBudget is the source of truth.

## Data flow overview

The monthly close processes seven distinct reconciliation and valuation paths. This section is the authoritative definition of each path's scope, ingestion method, lineage anchor, reconciliation behavior, and in-scope accounts.

**Bank Statement Digital Twin**

- Source: statement transaction files, csv or excel, with PDF statements retained as archive evidence
- Data ingest: user downloads statement files from each bank portal and places them for processing
- Data sync: extraction and parsing into the app consolidated database `statements` schema for four in-scope bank accounts only
- Lineage anchor: app `statements` schema row reference with statement fetch date and page reference
- Reconciliation: transaction match with HomeBudget at period end
- Accounts: TWH DBS Multi SGD, TWH CITI USD, TWH UOB One SGD, TWH Visa USD

**HomeBudget**

- Source: HomeBudget Python wrapper interface
- Data ingest: no user action required; app reads through the wrapper during data sync
- Data sync: wrapper-based read of HomeBudget data into the app-managed hb schema as defined in [data-model.md](data-model.md)
- Lineage anchor: hb sync transaction uid, wrapper source reference, and app sync timestamp
- Reconciliation: user review and categorization confirmation
- Accounts: HomeBudget-native accounts with no external statement source of truth, for example 30 Hashemis CC

For this path, HomeBudget is the source of truth.

**Bills and shared-cost domain**

- Source: parsed bill statement records, shared-cost inputs, and consumption metrics
- Data ingest: parse bill statements into bill-domain records; during POC, operators may enter or review records through Google Sheets bridge UI
- Data sync: persist canonical bill-domain state in the app `bills` schema
- Lineage anchor: app `bills` schema row reference, source statement reference, and update timestamp
- Reconciliation: bill lifecycle checks, period rollups, and shared-cost settlement status checks
- Accounts: in-scope bill-payment and shared-cost accounts
- Source authority: a single bill transaction appears in up to six representations — the bill statement, the bank statement, HomeBudget, the `hb` sync schema, the `close_book` schema, and the `bills` schema. The bill statement is authoritative for expense categorization and line-item breakdown. The bank statement is authoritative for transaction amount and posting date. All other representations are secondary and must reconcile to these two sources.

**IBKR**

- Source: Interactive Brokers activity statements in CSV format
- Data ingest: user downloads activity statement CSVs from IBKR portal
- Data sync: CSV parsing and top-down NAV derivation
- Lineage anchor: IBKR statement date and activity statement line item
- Reconciliation: top-down NAV match to broker statement
- Accounts: TWH IB USD, cash; IB Position USD, holdings; IB IRA USD, IRAs

**CPF**

- Source: Google Sheets UI input, no statement download available
- Data ingest: user enters sub-account balances, contributions, and transactions via closing-session GS UI
- Data sync: roll-forward computation and transaction posting from confirmed GS UI entries
- Lineage anchor: closing-session workbook entry with timestamp and session version
- Reconciliation: user review of contribution and balance inputs
- Accounts: CPF OA, CPF SA, CPF MA

**3rd Party Manual Input by User**

- Source: user reads current balances from third-party account sources
- Data ingest: user enters observed balances via closing-session GS UI
- Data sync: system computes adjustment transactions to update and reconcile HomeBudget to entered balances
- Lineage anchor: input entry timestamp, session version, and user-confirmation event
- Reconciliation: system computes adjustment transactions to update and reconcile HomeBudget to current balances
- Accounts: wallets and balance-only accounts, for example Amazon wallet

**Cash balances**

- Sources: GS form cash transactions and HomeBudget cash account transactions via the wrapper
- Data ingest: user enters close balance via closing-session GS UI; GS form cash transactions are pulled for the period
- Data sync: GS form transactions staged and aggregated by month into the `cash_staging` schema; HB cash transactions read via the wrapper into the `hb` schema
- Lineage anchor: close-input timestamp, form batch ID, hb sync timestamp, and computed-balance snapshot
- Reconciliation: staged GS form transactions, user close balance, and `hb_gl_txn` records are compared to compute the gap; approved adjustment posted to `close_book` and HB GL via the wrapper
- Accounts: cash-ledger accounts, for example TWH Cash SGD

**Yahoo Finance, forex**

- Source: Yahoo Finance API
- Data ingest: no user action required; forex runs in parallel with data ingest after pre-flight
- Data sync: forex rates are a prerequisite input; fetched and persisted during the forex stage
- Lineage anchor: symbol, quote date/time, fetch timestamp, and stored rate snapshot
- Reconciliation: rate sanity and month-close alignment checks
- Accounts: forex conversion inputs

**Yahoo Finance plus User Input, investment pricing**

- Source: Yahoo Finance unit price + user manual quantity input
- Data ingest: user enters quantity per investment holding via closing-session GS UI; unit pricing entered or fetched
- Data sync: valuation snapshot computed from confirmed price and quantity inputs
- Lineage anchor: symbol, price timestamp, quantity input version, and user confirmation
- Reconciliation: valuation consistency checks against prior period and account movement
- Accounts: investments requiring external price with manual quantity, for example Silver Bullions

## Source precedence and authority

This section defines conflict resolution only. It applies when multiple sources provide overlapping information for the same account, transaction set, or balance.
Canonical hb schema object names used below are owned by [data-model.md](data-model.md).

### Bank statement-process accounts

Transaction authority:

1. **Primary source:** statement-source transaction files parsed into the app consolidated database `statements` schema
2. **Secondary source:** hb sync ledger state for matching and gap analysis
3. **Conflict rule:** for amount-only differences on confirmed linked transactions, statement source is authoritative. For unmatched transactions, statements remain authoritative over HomeBudget source history. The aim of the reconciliation process is to bring hb sync ledger state into alignment with statement source and then post approved adjustments back to HomeBudget through the wrapper.

Balance authority:

1. **Primary source:** user-observed current balance input for close
2. **Secondary source:** statement-derived or workbook-derived balance signals used for variance detection
3. **Conflict rule:** differences are reconciliation findings; closure requires explicit variance treatment and approval.

For bank accounts outside the statement process, for example Wells Fargo USD, HomeBudget and manual balance inputs remain the active sources unless an explicit statement workflow is defined.

### HomeBudget-native accounts

Transaction authority:

1. **Primary source:** hb sync ledger state
2. **Secondary source:** user review and correction workflow
3. **Conflict rule:** adjustments are made in HomeBudget with audit notes when required.

Balance authority:

1. **Primary source:** balance state derived from hb sync schema
2. **Secondary source:** user-observed checks where available
3. **Conflict rule:** unresolved differences are handled through explicit adjustment workflow.

### Bills domain

A single bill transaction has a footprint across up to six representations: the bill statement, the bank statement, HomeBudget, the `hb` sync schema, the `close_book` schema, and the `bills` schema.

Transaction authority:

1. **Primary source (categorization and breakdown):** bill statement — authoritative for expense category, line-item detail, and payee
2. **Primary source (amount and date):** bank statement transaction record — authoritative for posted amount and posting date
3. **Secondary sources:** HomeBudget, `hb` sync schema, `close_book` schema, and `bills` schema
4. **Conflict rule:** all secondary representations must reconcile to the bill statement and bank statement. Discrepancies are reconciliation findings requiring explicit variance treatment before close.

Detailed accrual-period booking policy and settlement conflict handling for this dual-authority case are owned by [accounting-logic.md](accounting-logic.md) and [reconciliation-engine.md](reconciliation-engine.md).

### IBKR accounts

Transaction and balance authority:

1. **Primary source:** IBKR activity statement

### CPF accounts

Transaction and balance authority:

1. **Primary source:** user-provided monthly input records
2. **Secondary source:** roll-forward and contribution consistency checks
3. **Conflict rule:** inconsistencies require corrected input and explicit confirmation.

### Manual-input accounts

Transaction authority:

1. **Primary source:** system-computed adjustment transactions derived from user-observed balances
2. **Secondary source:** pre-adjustment hb sync ledger state
3. **Conflict rule:** computed adjustments are reviewed and explicitly confirmed before commit.

Balance authority:

1. **Primary source:** user-observed current balance input
2. **Secondary source:** current balance before adjustment derived from hb sync ledger state
3. **Conflict rule:** system computes the required delta; user confirms before close.

### Cash balances

Transaction authority:

1. **Primary source:** staged wallet cash transactions from the GS form staging schema
2. **Secondary source:** derived balance from transaction sums
3. **Conflict rule:** transaction rows remain source-authoritative; balance differences are handled in balance authority.

Balance authority:

1. **Primary source:** user-entered close balance input
2. **Secondary source:** computed balance from form transaction sums
3. **Conflict rule:** user-entered close balance overrides computed form balance; the variance and adjustment action must be recorded.

### Forex rates

1. **Primary source:** Yahoo Finance quote snapshot for configured symbol/date

### Investment pricing

1. **Primary source:** Yahoo Finance price snapshot plus user quantity input

## Transaction lineage requirements

This section defines the minimum transaction metadata that must be retained after ingestion and mapping.

### Reconciliation traceability outcomes

For reconciliation closure, each transaction must satisfy exactly one traceability outcome:

- **Standard lineage transaction:** transaction retains normal source lineage to origin system and source reference
- **Adjustment transaction:** transaction is marked as system adjustment and retains adjustment rule reference, adjustment timestamp, and user comment

### Bank statement transactions

- **Invariant fields:** transaction date, amount, currency, narration/description
- **Source reference:** statement file name and row identifier, with page number when applicable
- **Parsing metadata:** extraction timestamp, parser version
- **Reconciliation linkage:** match status with hb sync ledger record, if linked
- **Lineage trail:** from statement source file → app consolidated database `statements` schema → financial statements workbook

### HomeBudget transactions

- **Invariant fields:** transaction date, amount, currency, account
- **Source reference:** hb sync transaction uid, wrapper source reference, and app sync timestamp
- **Categorization metadata:** hb sync category reference and category change history, if modified
- **Mapping lineage:** HB category → GL account mapping version used
- **Reconciliation linkage:** bank statement match status, if the account is bank-linked
- **Lineage trail:** from HomeBudget wrapper source → hb sync schema → financial statements workbook

### Cash balances

- **Scope:** cash-balance records where source inputs can come from HomeBudget and cash-source records
- **Standard source artifacts:** source system ID, source account ID, source row ID, source event date, import timestamp
- **Cash-source artifacts:** workbook identifier, sheet name, row identifier, source update timestamp
- **Reconciliation artifact:** conflict status and matched counterpart reference when HomeBudget and cash-source records overlap
- **Adjustment artifact:** adjustment rule reference, adjustment timestamp, and user comment when a system adjustment transaction is created

### IBKR balances and adjustments

- **Invariant fields:** balance date, amount, currency, account
- **Source reference:** activity statement date, activity statement line item ID or activity reference
- **Derivation metadata:** NAV calculation components, if applicable, and FX rates used
- **Reconciliation linkage:** position statement cross-check
- **Lineage trail:** from IBKR activity statement → financial statements workbook

### CPF balances and contributions

- **Invariant fields:** balance date, amount, currency, sub-account
- **Source reference:** cpf GS UI entry timestamp, input version
- **Entry metadata:** user entry timestamp, user confirmation timestamp
- **Reconciliation linkage:** contribution flow consistency
- **Lineage trail:** from GS UI closing-session entry → financial statements workbook

## Balance lineage requirements

This section defines the minimum balance metadata required for traceability, derivation, and close status reporting. Explanatory descriptions belong in program logic and supporting documentation, not in persisted balance records.

### Minimum traceability metadata per balance

| id | property               | example                 | notes          |
| -- | ---------------------- | ----------------------- | -------------- |
| 01 | period_date            | 2026-02-28              | close date     |
| 02 | source_system          | bank_statement_path     | source label   |
| 03 | account                | 1010                    | cash account   |
| 04 | amount                 | 5000.00 SGD             | reported value |
| 05 | source_date            | 2026-02-28              | statement date |
| 06 | extraction_timestamp   | 2026-03-01 11:30:00 UTC | load timestamp |
| 07 | source_reference       | app DB statements row ID | lineage key   |
| 08 | reconciliation_status  | closed                  | workflow state |

### Aggregation and derivation requirements

When a financial statement balance is derived from multiple source balances, for example consolidated bank accounts, the following lineage must be retained:

- **Components:** list of all source balances that sum to the derived balance
- **FX conversion:** if cross-currency consolidation, the FX rates and conversion dates used
- **Aggregation rule reference:** rule ID, function name, or mapping version that defines the derivation logic
- **Aggregation timestamp:** when the derivation logic was applied

## Cross-path reconciliation points

This section defines the required validation for conflict cases where two independent input sources can disagree after source ingestion and before close approval.

### Bank statement vs. HomeBudget

- **Trigger:** end of account update stage
- **Validation:** every bank statement transaction is matched to an `hb_gl_txn` record 
- **Lineage requirement:** each reconciled transaction must be either a standard lineage transaction to source or an adjustment transaction with rule reference, timestamp, and comment
- **Acceptance:** cleared transactions with matched category

### Bill domain vs. HomeBudget postings

- **Trigger:** end of bill-payment workstream before session completion
- **Validation:** `bills` schema paid-state records and settlement records match posted HomeBudget entries and statement-link references
- **Lineage requirement:** each paid bill and each settlement entry must keep source statement or allocation rule reference plus posting status
- **Acceptance:** bill and settlement states are consistent between `bills` schema and HomeBudget posting outcomes

### Cash vs. HomeBudget

- **Trigger:** end of cash update stage
- **Validation:** staged wallet cash transactions from the GS form staging schema and `hb_gl_txn` records are compared; gap is derived from staged transactions, user close balance, and HB balance
- **Lineage requirement:** each reconciled transaction must be either a standard lineage transaction to source or an adjustment transaction with rule reference, timestamp, and comment
- **Acceptance:** cash variance is resolved and close balance is confirmed

## Audit and traceability requirements

This section defines retention and closure documentation requirements for audit support.

### Traceability artifacts

The following artifacts must be retained and accessible for audit:

| id | artifact                 | location                | access     |
| -- | ------------------------ | ----------------------- | ---------- |
| 01 | Bank statement PDFs      | s3                      | read-only  |
| 02 | `statements` tables      | app database schema     | read-write |
| 03 | HomeBudget txn snapshots by month | s3             | read-only  |
| 04 | IBKR activity statements | s3                      | read-only  |
| 05 | GS UI inputs             | s3                      | read-only  |
| 06 | financial statements     | s3                      | read-only  |
| 07 | Reconciliation analysis  | s3                      | read-only  |
| 08 | Cash source snapshots    | s3                      | read-only  |
| 09 | `cash_staging` tables    | app database schema     | read-write |
| 10 | `bills` tables           | app database schema     | read-write |
