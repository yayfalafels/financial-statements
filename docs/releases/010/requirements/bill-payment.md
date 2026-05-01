---
title: Bill Payment
doc_type: requirements
topic_type: owner
owner: bill-payment
scope: poc
version: 1.1
last_updated: 2026-02-28
status: Procedure documented, design completed, implementation planning ready
---
# Bill Payment Reconciliation

## Primary scope

- Bill lifecycle and bill-payment execution requirements
- Bill data model and active bill scope rules
- Bill-level and period-level reconciliation checks
- Bill-payment session completion rule

## Out of scope

- Shared-cost allocation and settlement policy details
- Shared-cost field contracts and consumption contracts

## Reference documents

- [shared costs](shared-costs.md)
- [workflow orchestration](workflow-orchestration.md)
- [reconciliation engine](reconciliation-engine.md)
- [bill payment current workflow](../../../reference/bill-payment-current-workflow.md)

## Overview

This page defines POC bill-payment and bill-lifecycle requirements for app behavior from POC onward.

## Current workflow

Current-state operational workflow, manual timings, and baseline process evidence are documented in [bill payment current workflow](../../../reference/bill-payment-current-workflow.md). Expenses are recorded directly via the HomeBudget app UI.  Additionally, the bill lifecycle is maintained using Notion. 


## App requirements

The app will provide an internal bill data model that preserves the same operational function, period-bill association, payee mapping, paid state, and payment-date tracking. The canonical raw source for bill-payment records is the app `bills` schema. During POC, Google Sheets is used only as a bridge UI for user input and review until browser UI replaces it in MVP. Treat Notion as legacy reference only, not as an active source in app workflow.

Additionaly, the app will: 

- use the HomeBudget wrapper interface for programmatic reads and controlled writes. 
- deprecate Notion

## Bills model

- bill-level fields equivalent to current workflow tracking needs: bill name, amount, billing cycle, payee, paid flag, and payment date.
- period-level rollups equivalent to current workflow checks: bills count and bills paid count.
- payee continuity view equivalent to current `bill_payee` behavior so recurring payee history remains queryable across periods.
- Derive period rollups from bill records in the app model, not from manual duplicate entry.
- Link bill entries to lifecycle checks in this page so active-bill and paid-state validations are queryable
- For paid bills, require statement-link reference for reconciliation traceability.

## User Interface

Use Google Sheets only as bridge UI during POC; it is not a data source

## Automation Design Requirements

To automate bill-payment reconciliation, the system must:

### 1. Bill-provider statement parsing
- **Input:** Downloaded billing statement files (PDF, CSV, Excel)
- **Output:** Structured bill transaction records persisted in the app `bills` schema, including date, payee, amount, category, and statement linkage fields
- **Requirements:**
  - Support multiple statement formats (utilities, rent, subscriptions)
  - Extract total due, due date, payment date
  - Handle multi-line bill items
  - Parse and ingest normalized bill records into the app `bills` schema before downstream shared-cost lifecycle checks run
  - Implement parsing in app-native bill parsing logic, with no dependency on legacy bank statement ingestion scripts

### 1A. Statement parsing contract

Statement parsing behavior is a requirement-level contract and must be fully implementable from this page without reading source scripts or raw statement files.

This section defines bill-provider statement parsing only. It is distinct from bank statement ingestion used for account transaction reconciliation; see [bank-statements.md](bank-statements.md) for that contract.

Supported input formats by account:

| id | account           | required_format_set | primary_currency | parse_contract |
| -- | ----------------- | ------------------- | ---------------- | -------------- |
| 01 | TWH DBS Multi SGD | csv and pdf         | SGD              | direct parse   |
| 02 | TWH UOB One SGD   | excel and pdf       | SGD              | direct parse   |
| 03 | TWH CITI          | csv and pdf         | USD              | direct parse   |
| 04 | TWH Visa USD      | csv and pdf         | USD              | direct parse   |

Required normalized bill statement fields:

| id | field                 | type    | req | rule                                      |
| -- | --------------------- | ------- | --- | ----------------------------------------- |
| 01 | statement_ref         | text    | y   | unique per source account and period      |
| 02 | source_account        | text    | y   | must match accounts in scope              |
| 03 | period_year           | int     | y   | close period year                         |
| 04 | period_month          | int     | y   | close period month                        |
| 05 | payee_raw             | text    | y   | original payee text from source           |
| 06 | payee_normalized      | text    | y   | must map to one in-scope bill payee       |
| 07 | line_item_date        | date    | n   | required for itemized statements          |
| 08 | payment_date          | date    | n   | required when paid state is true          |
| 09 | due_date              | date    | n   | required if present in source statement   |
| 10 | total_due_amount      | decimal | y   | signed amount in source currency          |
| 11 | source_currency       | enum    | y   | SGD or USD                                |
| 12 | multiline_group_key   | text    | n   | required when one bill spans multiple rows|
| 13 | statement_line_ref    | text    | y   | stable linkage key for reconciliation     |

Payee normalization coverage requirements:

| id | canonical_payee | accepted_source_labels                   | settlement_account |
| -- | --------------- | ---------------------------------------- | ------------------ |
| 01 | Singtel         | Singtel                                  | TWH UOB One SGD    |
| 02 | SP Services     | SP Services and PUB                      | TWH DBS Multi SGD  |
| 03 | Rent            | landlord CC and Rent                     | TWH DBS Multi SGD  |
| 04 | WPL Spotify     | WPL spotify and Spotify                  | TWH DBS Multi SGD  |
| 05 | UOB CC          | UOB CC                                   | TWH DBS Multi SGD  |
| 06 | BOA CC          | BOA CC                                   | TWH CITI           |

Parsing rules for multi-line and totals:

- Multi-line statements must be reduced to one bill row per canonical payee per period, with traceable `multiline_group_key` and retained `statement_line_ref` lineage.
- If both item-level total and statement-level total are present, statement-level total is authoritative for `total_due_amount` and item-level values are supporting evidence only.
- If due date is missing in source, parsing remains valid and due-date-dependent checks are skipped without failing payee and amount reconciliation.
- If payment date is missing for an unpaid bill, state remains `pending` and period close rules apply.
- Parse output must be deterministic for the same source statement input and period parameters.

### 1B. Format-level extraction profiles

Extraction logic by input format must follow these profiles.

| id | format | required raw fields                                      | date rule               | amount rule              |
| -- | ------ | -------------------------------------------------------- | ----------------------- | ------------------------ |
| 01 | csv    | date plus description plus debit and credit or amount    | parse to ISO date       | debit credit net or value|
| 02 | excel  | date plus description plus transaction amount            | parse to ISO date       | preserve sign convention |
| 03 | pdf    | posted date plus payee plus amount and total due block   | parse to ISO date       | use posted bill amount   |

Per-account extraction profile requirements:

| id | account           | input_format | required date token | required amount token        | sign normalization |
| -- | ----------------- | ------------ | ------------------- | ---------------------------- | ------------------ |
| 01 | TWH DBS Multi SGD | csv and pdf  | transaction date    | debit amount and credit amount| credit minus debit |
| 02 | TWH UOB One SGD   | excel and pdf| transaction date    | transaction amount local     | outflow negative   |
| 03 | TWH CITI          | csv and pdf  | date                | debit and credit             | credit minus debit |
| 04 | TWH Visa USD      | csv and pdf  | posted date         | amount                       | preserve source sign|

### 1C. Deterministic normalization pipeline

The system must execute the same ordered pipeline for every statement parse.

| id | stage                         | input                | output                  |
| -- | ----------------------------- | -------------------- | ----------------------- |
| 01 | source parse                  | statement file       | raw rows                |
| 02 | field projection              | raw rows             | required columns only   |
| 03 | date and amount normalization | projected rows       | typed values            |
| 04 | payee normalization           | typed rows           | canonical payee rows    |
| 05 | multiline consolidation       | canonical payee rows | one bill row per payee  |
| 06 | lineage key assignment        | consolidated rows    | keyed rows              |
| 07 | period assignment             | keyed rows           | period tagged rows      |
| 08 | bills schema write            | period tagged rows   | persisted bill rows     |

Normalization requirements:

- One canonical bill row must exist per canonical payee and close period.
- `statement_line_ref` must remain traceable to the source line or source total row after consolidation.
- `statement_ref` must be deterministic for the same source account, period, and statement file identity.
- `multiline_group_key` must be deterministic for the same payee and statement grouping inputs.

### 1D. Payee mapping and reconciliation precedence

Payee and amount decisions must use a strict precedence order.

| id | decision area      | precedence order                                         |
| -- | ------------------ | -------------------------------------------------------- |
| 01 | payee mapping      | explicit alias match then canonical label exact match    |
| 02 | amount selection   | statement total due then grouped line-item total         |
| 03 | payment date       | explicit paid transaction date then null for pending     |
| 04 | due date           | source due date then null                                |

If multiple aliases match different canonical payees in one statement period, parsing must fail with a blocking ambiguity error.

### 2. Transaction Generation
- **Input:** Parsed statements + bill metadata records in app `bills` schema
- **Output:** HomeBudget bill-payment transactions
- **Requirements:**
  - Map statement payees to HomeBudget categories
  - Create payment transactions (credit card payments, utility payments, rent)
  - Apply consistent date and description conventions
  - Commit directly to HomeBudget by default

### 2A. Transaction generation contract

Bill payment transaction generation must be deterministic from normalized bill rows.

Required generated transaction fields:

| id | field                | type    | req | rule                                           |
| -- | -------------------- | ------- | --- | ---------------------------------------------- |
| 01 | txn_date             | date    | y   | payment date else scheduled date               |
| 02 | txn_account          | text    | y   | must match settlement account from payee map   |
| 03 | txn_amount           | decimal | y   | absolute amount from normalized bill row       |
| 04 | txn_currency         | enum    | y   | must match normalized source currency          |
| 05 | txn_payee            | text    | y   | canonical payee                                |
| 06 | txn_description      | text    | y   | canonical format with period and payee         |
| 07 | txn_lineage_ref      | text    | y   | `statement_line_ref` carry-forward             |
| 08 | txn_status           | enum    | y   | pending or posted                              |

Description format requirement:

- Generated description must use `BILL {period_year}-{period_month} {canonical_payee}`.

Posting behavior requirements:

- If bill state is `paid`, transaction status must be `posted`.
- If bill state is `scheduled`, transaction status must be `pending` until post date.
- If bill state is `pending`, no payment transaction may be posted.

### 3. `bills` schema model, replaces Notion
- **Input:** Parsed statement outputs and bill metadata for period and payee
- **Output:** App `bills` schema records and period rollups used for bill status checks
- **Requirements:**: refer to the bills model and user interface 

### 4. Reconciliation and Reporting
- **Input:** Bill records and bill-payment transactions
- **Output:** Bill-payment reconciliation report and variance checks
- **Requirements:**
  - Summarize total bill payments for period
  - Compare to budget or historical trends
  - Flag variances for review

## Accounts in Scope

Based on [Monthly closing documentation](../../../../reference/notion/Optimize monthly closing/Monthly closing 20bc378f707580f99849e024db8f12fb.md):

| id | account           | type     | ccy | bank            | description                                  |
| -- | ----------------- | -------- | --- | --------------- | -------------------------------------------- |
| 01 | TWH DBS Multi SGD | checking | SGD | DBS             | main banking settlement hub for bill payment |
| 02 | TWH UOB One SGD   | credit   | SGD | UOB             | main credit card for variable expenses       |
| 03 | TWH Visa USD      | credit   | USD | Bank of America | USD credit card for limited purchases        |
| 04 | TWH CITI          | checking | USD | Citibank USA    | USD bank account with ACH capabilities       |

**Bills in scope:**

| id | payee       | account           | method                | status                |
| -- | ----------- | ----------------- | --------------------- | --------------------- |
| 01 | Singtel     | TWH UOB One SGD   | automatic payment     | automated (via payee) |
| 02 | SP Services | TWH DBS Multi SGD | GIRO                  | automated (via GIRO)  |
| 03 | Rent        | TWH DBS Multi SGD | standing instructions | automated (via bank)  |
| 04 | WPL Spotify | TWH DBS Multi SGD | standing instructions | automated (via bank)  |
| 05 | UOB CC      | TWH DBS Multi SGD | manual                | requires automation   |
| 06 | BOA CC      | TWH CITI          | ACH auto pay          | automated (via payee) |

- Parse bill statements and create normalized bill-payment records for all in-scope payees.
- Support payment capture for auto-pay and manual-pay methods, with explicit payment-state tracking.
- Use Google Sheets only as bridge UI for POC user interaction; keep canonical bill state in the app `bills` schema.

## Bill lifecycle and reconciliation requirements

### Active bill scope

- A bill is either active or inactive.
- Reconciliation checks apply only to active bills in the current period.
- Inactive bills are excluded from count and resolution checks.

### Bill data model

| id | field           | type | req | rule                                    |
| -- | --------------- | ---- | --- | --------------------------------------- |
| 01 | name            | text | y   | unique bill identifier                  |
| 02 | payee           | text | y   | counterparty receiving payment          |
| 03 | amount_type     | enum | y   | fixed or variable                       |
| 04 | expected_amount | dec  | n   | required when amount_type is fixed, SGD |
| 05 | billing_cycle   | enum | y   | monthly, quarterly, or annual           |
| 06 | active          | bool | y   | true means included in period checks    |

### Bill lifecycle state model

| id | state     | meaning                                           | next states     |
| -- | --------- | ------------------------------------------------- | --------------- |
| 01 | pending   | bill identified but not yet paid                  | paid, scheduled |
| 02 | scheduled | payment planned for a future date within period   | paid            |
| 03 | paid      | payment confirmed with statement transaction link |                 |

### Close criteria for bill lifecycle

- A bill may close only in paid or scheduled state.
- A bill in pending state at session close blocks period closure.
- A paid bill requires bank-statement transaction linkage.

### Shared-cost dependency boundary

- Shared-cost and consumption ownership belongs to [shared costs](shared-costs.md).
- Bill payment provides bill amount and paid-state inputs consumed by shared-cost lifecycle checks.

### Bill-level reconciliation checks

| id | check                      | source fields                      | pass condition                                  |
| -- | -------------------------- | ---------------------------------- | ----------------------------------------------- |
| 01 | amount match               | bill amount vs statement line item | amounts equal within SGD 0.00 tolerance         |
| 02 | payee match                | bill payee vs statement payee      | payee maps to same approved counterparty        |
| 03 | payment date within period | bill payment_date vs close period  | date within 2 months before or after period end |
| 04 | paid status complete       | bill paid flag                     | flag is true and linkage reference is present   |

### Period-level reconciliation checks

| id | check                    | source fields                   | pass condition                                     |
| -- | ------------------------ | ------------------------------- | -------------------------------------------------- |
| 01 | bills count matches      | bills_count vs active bill rows | count equals number of active bills for the period |
| 02 | bills paid count matches | bills_paid vs active bill rows  | paid count equals active bills in paid state       |
| 03 | all bills resolved       | bill state distribution         | no active bill remains in pending state            |

### Bill-payment session completion rule

- Each active bill must be either paid with statement linkage or scheduled.
