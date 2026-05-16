---
title: Glossary
doc_type: requirements
topic_type: reference
owner: glossary
scope: poc
---
# Glossary

## Table of contents

- [Related documents](#related-documents)
- [Period](#period)
- [Account](#account)
- [Account type](#account-type)
- [Asset type](#asset-type)
- [Statement terminology](#statement-terminology)
- [Raw statement file](#raw-statement-file)
- [Statement digital twin](#statement-digital-twin)
- [Statement ingestion script](#statement-ingestion-script)
- [Financial statement](#financial-statement)
- [Financial statements workbook](#financial-statements-workbook)
- [Ledger](#ledger)
- [`hb_gl_txn`](#hb_gl_txn)
- [`hb_account_dim`](#hb_account_dim)
- [`hb_category_dim`](#hb_category_dim)
- [`hb_txn_uid`](#hb_txn_uid)
- [Transaction](#transaction)
- [Transaction uniqueness key](#transaction-uniqueness-key)
- [Reconciliation](#reconciliation)
- [Reconciliation date](#reconciliation-date)
- [Variance](#variance)
- [Tolerance](#tolerance)
- [Mark to market](#mark-to-market)
- [Foreign exchange rate](#foreign-exchange-rate)
- [Forex mark to market adjustment](#forex-mark-to-market-adjustment)
- [Checkpoint](#checkpoint)
- [Session state](#session-state)
- [Workflow step](#workflow-step)
- [System component](#system-component)
- [Runtime component](#runtime-component)
- [Adapter component](#adapter-component)
- [Internal module](#internal-module)
- [Interface boundary](#interface-boundary)
- [Interaction topology](#interaction-topology)
- [Bill](#bill)
- [Shared cost](#shared-cost)
- [Novel decision](#novel-decision)
- [Period snapshot](#period-snapshot)

## Related documents

- [Account classification](account-classification.md), account types, mapping rules, and reporting classifications
- [Accounting logic](accounting-logic.md), booking rules, reconciliation rules, and transaction uniqueness
- [Current workflow reference](../../../reference/current-workflow.md), existing manual monthly closing sequence
- [App Workflows Design](workflow-orchestration.md), intended automated workflow design
- [Bill payment](bill-payment.md), shared cost allocation and bill processing context
- [Data model](data-model.md), schema ownership and canonical schema object naming

## Period

A period is a calendar month. The standard identifier is `YYYY-MM`, for example `2026-02`. A period starts on the first calendar day and ends on the last calendar day.

## Account

An account is a named balance holder in HomeBudget or in reporting scope. Examples include bank accounts, credit cards, wallet cash, cost centers, and investment positions.

## Account type

Account type is the HomeBudget internal classification, `Budget`, `Cash`, `Credit`, or `External`. It governs transaction behavior and reconciliation method.

## Asset type

Asset type is the reporting classification used in financial statements. Examples include cash and bank accounts, credit, liquid investments, and illiquid and retirement.

## Statement terminology

The term `statement` is overloaded in this project and must be qualified in design and implementation documents.

- Use `bill statement file` for provider bill files such as Singtel and SP Services statements.
- Use `bank statement file` for bank and card account source files used in bank-account reconciliation.
- Use `statement digital twin` only for parsed bank-account transactions and balances persisted in SQLite, currently `statements.db`.
- Use `bank statement ingestion script` for the legacy bank parser loader, currently `statements.py`.
- Use `financial statement` for curated reporting outputs, such as income statement and balance sheet.
- Use `financial statements workbook` for the legacy Google Sheets workbook `gsheet/financial-statements.json`, which is planned for deprecation.

Avoid using the unqualified word `statement` unless the surrounding sentence already names one of the five terms above.

## Bill statement file

Bill statement file is the downloaded source document from a bill provider, usually PDF and sometimes CSV or XLSX, parsed by app-native bill parsing logic into the `bills` schema.

## Bank statement file

Bank statement file is the downloaded source document from a bank or card provider, usually CSV, XLSX, or PDF, that is parsed and ingested for bank-account reconciliation.

## Raw statement file

Raw statement file is the downloaded source document from a financial institution or provider, usually CSV, XLSX, or PDF, that must be parsed and ingested.

## Statement digital twin

Statement digital twin is the local SQLite representation of parsed raw statement file transactions and observed balances, currently `statements.db`. It is the source of truth for transaction level reconciliation against the ledger.

## Statements digital twin

Statements digital twin (plural) refers to the collection of statement digital twins across all accounts and statement sources. Together they form the complete statement source of truth for all accounts being reconciled in a period.

## Bank statement ingestion script

Bank statement ingestion script is the legacy parser and loader that ingests bank statement files into the statement digital twin, currently `statements.py`.

## Financial statement

Financial statement is a curated reporting output produced from reconciled and classified data across sources. Primary outputs are income statement and balance sheet.

## Financial statements workbook

Financial statements workbook is the legacy Google Sheets workbook used to prepare financial statements, represented by `gsheet/financial-statements.json`. It is an interim system that will be replaced by app-native logic and SQLite persistence.

## Ledger

Ledger is the app-managed HomeBudget ledger view derived from `hb_gl_txn` for an account and period after filtering to transaction rows that affect balance.

## `hb_gl_txn`

`hb_gl_txn` is the canonical app-managed HomeBudget general-ledger transaction table. Full definition is owned by [data-model.md](data-model.md).

## `hb_account_dim`

`hb_account_dim` is the app-managed HomeBudget account dimension. Full definition is owned by [data-model.md](data-model.md).

## `hb_category_dim`

`hb_category_dim` is the app-managed HomeBudget category dimension. Full definition is owned by [data-model.md](data-model.md).

## `hb_txn_uid`

`hb_txn_uid` is the deterministic hashed transaction identifier on `hb_gl_txn`. Full definition is owned by [data-model.md](data-model.md).

## Transaction

A transaction is a dated amount entry in an account with optional category, payee, and description fields. Main transaction classes are expense, income, transfer in, and transfer out.

## Transaction uniqueness key

The uniqueness key is the tuple account, date, amount, and description. If two source rows are still identical, append a suffix such as `-01` and `-02` in description.

## Reconciliation

Reconciliation is the process that aligns ledger balances and transactions to statement digital twin balances and transactions for the same period.

## Reconciliation date

Reconciliation date is the selected cut-off date in a period. Pending transactions before that date can be carried after the cut-off with a note that preserves original transaction date context.

## Variance

Variance is the residual difference after comparing computed closing balance to observed closing balance.

## Tolerance

Tolerance is the allowed absolute variance before intervention is required.

## Mark to market

Mark to market is a valuation adjustment that updates an asset or liability to market value at period end.

## Foreign exchange rate

Foreign exchange rate is the conversion factor between currency pair values used for reporting and adjustment logic.

## Forex mark to market adjustment

Forex mark to market adjustment is the valuation change from exchange rate movement across a period, applied to foreign currency balances for reporting and reconciliation support.

## Checkpoint

Checkpoint is a workflow gate where validations are evaluated and user review may be required before the next step proceeds.

## Session state

Session state is the persisted progress record for a period close run, including current step, outcomes, and decision log.

## Workflow step

Workflow step is an executable unit of the monthly close process with defined inputs, outputs, and validation criteria.

## System component

System component is a named architecture participant in the release 010 component catalog, such as workflow orchestrator, account close runtime, statement builder, or SQLite adapter.
Use system component for cross-component ownership, contracts, and handoff behavior.
Do not use module as a synonym for system component.

## Runtime component

Runtime component is a system component that executes stage or workflow business logic and owns stage outcomes.
Examples include account close runtime and bill and shared-cost runtime.

## Adapter component

Adapter component is a system component that translates between app contracts and external or persistence interfaces.
Examples include source adapters, HomeBudget wrapper adapter, Google Sheets adapter, and SQLite adapter.

## Internal module

Internal module is a within-component code organization unit, such as a Python package, file, or import unit.
Use internal module only for repository or code-structure discussion inside a component design.
Do not use internal module for architecture-level participants.

## Interface boundary

Interface boundary is the explicit contract seam between system components, including allowed call direction, payload contract, and failure signaling behavior.
Qualify boundary terms by context when possible, such as API boundary, integration boundary, or persistence boundary.

## Interaction topology

Interaction topology is the allowed interaction pattern among system components, independent of internal code layout.
Use interaction topology for sequence and wiring constraints among components.
Do not use module layout when describing architecture-level interactions.

## Bill

Bill is the personal-finance term used in this project for the accounting concept of an invoice. For accrual treatment, the billed amount is the expense for the billing period even when settlement on the bank statement occurs in a different period or in multiple payments.

## Shared cost

Shared cost is an expense that is split across multiple parties. The personal share is booked as expense and non personal share is booked to settlement account `30 CC Hashemis`.

## Novel decision

Novel decision is a manual reconciliation or allocation choice that is not yet captured as a routine rule in code or documentation.

## Period snapshot

Period snapshot is the finalized, immutable set of balances, financial statement outputs, and workflow status for one period.

