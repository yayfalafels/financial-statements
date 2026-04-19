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

Six source systems contribute to the monthly close:

| id | system name               | source type                        | lineage anchor           |
| -- | ------------------------- | ---------------------------------- | ------------------------ |
| 01 | Statement Digital Twin    | statement files + PDF archive      | app DB `statements` schema |
| 02 | HomeBudget                | app database + direct user inputs  | HomeBudget app SQLite    |
| 03 | IBKR                      | CSV statements                      | IBKR activity statement  |
| 04 | CPF                       | manual JSON                         | `inputs.json`            |
| 05 | User Manual Inputs        | user-observed balances and qty      | versioned JSON inputs    |
| 06 | Yahoo Finance             | market data API                     | API response snapshot    |

> **HomeBudget transaction ID:** HomeBudget stores transactions in separate tables by type: expense, income, and transfer. It has no unified transaction model. This system generates a synthetic HomeBudget transaction ID at import from the source pair `transaction_type` and `source_id`, for example `expense:1234` or `income:567`. All HomeBudget transaction ID references in this document refer to this system-generated identifier.

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
| 11 | json[1]   | balance      | low  | wallets        | TWH Cash USD                   | no           |
| 12 | json[1]   | balance      | low  | wallets        | others - EZLink, Amazon, etc.. | no           |
| 13 | csv[2]    | txn          | low  | ibkr           | IBKR IBA                       | no           |
| 14 | csv[2]    | txn          | low  | ibkr           | IBKR IRA                       | no           |
| 15 | json[1]   | qty          | low  | investments    | Silver Bullions                | no           |
| 16 | api       | unit price   | low  | investments    | Silver Bullions                | no           |
| 17 | api       | forex rates  | low  | forex          | --                             | no           |
| 18 | pdf       | txn          | high | bills          | Singtel                        | no           |
| 19 | pdf       | txn          | high | bills          | PUB SP Services                | no           |
| 20 | json[1]   | balance      | high | bank accounts  | TWH DBS Multi SGD              | no           |
| 21 | json[1]   | balance      | high | bank accounts  | TWH Visa USD                   | no           |
| 22 | json[1]   | balance      | high | bank accounts  | TWH CITI USD                   | no           |
| 23 | json[1]   | balance      | high | bank accounts  | TWH UOB One SGD                | no           |
| 24 | json[1]   | balance      | low  | bank accounts  | Wells Fargo USD                | no           |

1. future, currently offline manual operation + manual update directly to HomeBudget + `balances` sheet in financial statements workbook
2. in later version MVP will use direct api

Statement-process boundary:
- Only the four accounts TWH DBS Multi SGD, TWH Visa USD, TWH CITI USD, and TWH UOB One SGD flow through `statements.py` into the app consolidated database `statements` schema.
- Wells Fargo USD is a bank account but is outside the regular `statements.py` and app `statements` schema process.
- Some accounts have no independent statement backup source; in those cases HomeBudget is the source of truth.

## Data flow overview

The monthly close processes seven distinct reconciliation and valuation paths. This section is the authoritative definition of each path's scope, ingestion method, lineage anchor, reconciliation behavior, and in-scope accounts.

**Bank Statement Digital Twin**

- Source: statement transaction files, csv or excel, with PDF statements retained as archive evidence
- Ingestion: extraction and parsing into the app consolidated database `statements` schema for four in-scope bank accounts only
- Lineage anchor: app `statements` schema row reference with statement fetch date and page reference
- Reconciliation: transaction match with HomeBudget at period end
- Accounts: TWH DBS Multi SGD, TWH CITI USD, TWH UOB One SGD, TWH Visa USD

**HomeBudget**

- Source: HomeBudget app database
- Ingestion: direct read from app SQLite
- Lineage anchor: HomeBudget transaction ID and manual entry timestamp
- Reconciliation: user review and categorization confirmation
- Accounts: HomeBudget-native accounts with no external statement source of truth, for example 30 Hashemis CC

For this path, HomeBudget is the source of truth.

**IBKR**

- Source: Interactive Brokers activity statements in CSV format
- Ingestion: manual CSV upload, or automated retrieval in the MVP phase
- Lineage anchor: IBKR statement date and activity statement line item
- Reconciliation: top-down NAV match to broker statement
- Accounts: TWH IB USD, cash; IB Position USD, holdings; IB IRA USD, IRAs

**CPF**

- Source: manual JSON input, no statement download available
- Ingestion: user-provided JSON via workflow input
- Lineage anchor: `inputs.json` with timestamp and input version
- Reconciliation: user review of contribution and balance inputs
- Accounts: CPF OA, CPF SA, CPF MA

**3rd Party Manual Input by User**

- Source: user reads current balances from third-party account sources
- Ingestion: manual input into system, initially via JSON
- Lineage anchor: input file version, input timestamp, and user-confirmation event
- Reconciliation: system computes adjustment transactions to update and reconcile HomeBudget to current balances
- Accounts: wallets and balance-only accounts, for example Amazon wallet

**Cash balances**

- Source: user close-balance input and form-derived transaction sums
- Ingestion: capture user-entered close balance plus computed balance from imported form records
- Lineage anchor: close-input timestamp, operator identity, form batch ID, and computed-balance snapshot
- Reconciliation: compare user close balance against form-derived sum and compute required adjustment delta
- Rule: user close-balance input is authoritative; form-derived sum is secondary support evidence
- Accounts: cash-ledger accounts, for example TWH Cash SGD

**Yahoo Finance, forex**

- Source: Yahoo Finance API
- Ingestion: fetch and persist period rates
- Lineage anchor: symbol, quote date/time, fetch timestamp, and stored rate snapshot
- Reconciliation: rate sanity and month-close alignment checks
- Accounts: forex conversion inputs

**Yahoo Finance plus User Input, investment pricing**

- Source: Yahoo Finance unit price + user manual quantity input
- Ingestion: API fetch for price plus manual quantity input capture
- Lineage anchor: symbol, price timestamp, quantity input version, and user confirmation
- Reconciliation: valuation consistency checks against prior period and account movement
- Accounts: investments requiring external price with manual quantity, for example Silver Bullions

## Source precedence and authority

This section defines conflict resolution only. It applies when multiple sources provide overlapping information for the same account, transaction set, or balance.

### Bank statement-process accounts

Transaction authority:

1. **Primary source:** statement-source transaction files parsed into the app consolidated database `statements` schema
2. **Secondary source:** HomeBudget transaction ledger for matching and gap analysis
3. **Conflict rule:** for amount only differences for confirmed linked transactions, statement source is authoritative. for unmatched transactions, ultimately statements are authoritative over HomeBudget, however, the transaction may be represented in HomeBudget in a way that the user is aware of but that particular txn was not matched in the first pass by the automated system. The aim of the reconciliation process is to bring the HomeBudget ledger into alignment with the statement source, but user review and confirmation is required for any adjustments.

Balance authority:

1. **Primary source:** user-observed current balance input for close
2. **Secondary source:** statement-derived or workbook-derived balance signals used for variance detection
3. **Conflict rule:** differences are reconciliation findings; closure requires explicit variance treatment and approval.

For bank accounts outside the statement process, for example Wells Fargo USD, HomeBudget and manual balance inputs remain the active sources unless an explicit statement workflow is defined.

### HomeBudget-native accounts

Transaction authority:

1. **Primary source:** HomeBudget transaction ledger
2. **Secondary source:** operator review and correction workflow
3. **Conflict rule:** adjustments are made in HomeBudget with audit notes when required.

Balance authority:

1. **Primary source:** HomeBudget running balance
2. **Secondary source:** user-observed checks where available
3. **Conflict rule:** unresolved differences are handled through explicit adjustment workflow.

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
2. **Secondary source:** HomeBudget pre-adjustment ledger
3. **Conflict rule:** computed adjustments are reviewed and explicitly confirmed before commit.

Balance authority:

1. **Primary source:** user-observed current balance input
2. **Secondary source:** HomeBudget current balance before adjustment
3. **Conflict rule:** system computes the required delta; operator confirms before close.

### Cash balances

Transaction authority:

1. **Primary source:** imported cash form transactions
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
- **Adjustment transaction:** transaction is marked as system adjustment and retains adjustment rule reference, adjustment timestamp, and operator comment

### Bank statement transactions

- **Invariant fields:** transaction date, amount, currency, narration/description
- **Source reference:** statement file name and row identifier, with page number when applicable
- **Parsing metadata:** extraction timestamp, parser version
- **Reconciliation linkage:** match status with HomeBudget transaction, if linked
- **Lineage trail:** from statement source file → app consolidated database `statements` schema → financial statements workbook

### HomeBudget transactions

- **Invariant fields:** transaction date, amount, currency, account
- **Source reference:** HomeBudget transaction ID, app entry timestamp
- **Categorization metadata:** category and category change history, if modified
- **Mapping lineage:** HB category → GL account mapping version used
- **Reconciliation linkage:** bank statement match status, if the account is bank-linked
- **Lineage trail:** from HomeBudget app → financial statements workbook

### Cash balances

- **Scope:** cash-balance records where source inputs can come from HomeBudget and cash-source records
- **Standard source artifacts:** source system ID, source account ID, source row ID, source event date, import timestamp
- **Cash-source artifacts:** workbook identifier, sheet name, row identifier, source update timestamp
- **Reconciliation artifact:** conflict status and matched counterpart reference when HomeBudget and cash-source records overlap
- **Adjustment artifact:** adjustment rule reference, adjustment timestamp, and operator comment when a system adjustment transaction is created

### IBKR balances and adjustments

- **Invariant fields:** balance date, amount, currency, account
- **Source reference:** activity statement date, activity statement line item ID or activity reference
- **Derivation metadata:** NAV calculation components, if applicable, and FX rates used
- **Reconciliation linkage:** position statement cross-check
- **Lineage trail:** from IBKR activity statement → financial statements workbook

### CPF balances and contributions

- **Invariant fields:** balance date, amount, currency, sub-account
- **Source reference:** JSON input file timestamp, input version
- **Entry metadata:** user entry timestamp, user confirmation timestamp
- **Reconciliation linkage:** contribution flow consistency
- **Lineage trail:** from JSON input → financial statements workbook

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
- **Validation:** every uncleared bank statement transaction is either matched to a HomeBudget transaction or has a documented exception
- **Lineage requirement:** each reconciled transaction must be either a standard lineage transaction to source or an adjustment transaction with rule reference, timestamp, and comment
- **Acceptance:** cleared transactions with matched category

### Cash vs. HomeBudget

- **Trigger:** end of cash update stage
- **Validation:** each cash-source transaction or balance delta is either matched to a HomeBudget transaction or closed through an approved adjustment
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
| 05 | JSON inputs              | s3                      | read-only  |
| 06 | financial statements     | s3                      | read-only  |
| 07 | Reconciliation analysis  | s3                      | read-only  |
| 08 | Cash source snapshots    | s3                      | read-only  |
