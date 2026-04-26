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
- [bill payment current workflow](../reference/bill-payment-current-workflow.md)

## Overview

This page defines POC bill-payment and bill-lifecycle requirements for app behavior from POC onward.

## Current workflow

Current-state operational workflow, manual timings, and baseline process evidence are documented in [bill payment current workflow](../reference/bill-payment-current-workflow.md). Expenses are recorded directly via the HomeBudget app UI.  Additionally, the bill lifecycle is maintained using Notion. 


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

### 1. Statement Parsing
- **Input:** Downloaded billing statement files (PDF, CSV, Excel)
- **Output:** Structured bill transaction records persisted in the app `bills` schema, including date, payee, amount, category, and statement linkage fields
- **Requirements:**
  - Support multiple statement formats (utilities, rent, subscriptions)
  - Extract total due, due date, payment date
  - Handle multi-line bill items
  - Parse and ingest normalized bill records into the app `bills` schema before downstream shared-cost lifecycle checks run

### 2. Transaction Generation
- **Input:** Parsed statements + bill metadata records in app `bills` schema
- **Output:** HomeBudget bill-payment transactions
- **Requirements:**
  - Map statement payees to HomeBudget categories
  - Create payment transactions (credit card payments, utility payments, rent)
  - Apply consistent date and description conventions
  - Commit directly to HomeBudget by default

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

Based on [Monthly closing documentation](../../reference/notion/Optimize monthly closing/Monthly closing 20bc378f707580f99849e024db8f12fb.md):

| id          |                   |          |     |                 |
| ----------- | ----------------- | -------- | --- | --------------- |
| account     |                   |          |     |                 |
| type        |                   |          |     |                 |
| ccy         |                   |          |     |                 |
| bank        |                   |          |     |                 |
| description |                   |          |     |                 |
| 01          | TWH DBS Multi SGD | checking | SGD | DBS             |
| 02          | TWH UOB One SGD   | credit   | SGD | UOB             |
| 03          | TWH Visa USD      | credit   | USD | Bank of America |
| 04          | TWH CITI          | checking | USD | Citibank USA    |

| id          |                   |                                              |
| ----------- | ----------------- | -------------------------------------------- |
| account     |                   |                                              |
| type        |                   |                                              |
| ccy         |                   |                                              |
| bank        |                   |                                              |
| description |                   |                                              |
| 01          | TWH DBS Multi SGD | main banking settlement hub for bill payment |
| 02          | TWH UOB One SGD   | main credit card for variable expenses       |
| 03          | TWH Visa USD      | USD credit card for limited purchases        |
| 04          | TWH CITI          | USD bank account with ACH capabilities       |

**Bills in scope:**

| id      |             |                   |                       |                       |
| ------- | ----------- | ----------------- | --------------------- | --------------------- |
| payee   |             |                   |                       |                       |
| account |             |                   |                       |                       |
| method  |             |                   |                       |                       |
| status  |             |                   |                       |                       |
| 01      | Singtel     | TWH UOB One SGD   | automatic payment     | automated (via payee) |
| 02      | SP Services | TWH DBS Multi SGD | GIRO                  | automated (via GIRO)  |
| 03      | Rent        | TWH DBS Multi SGD | standing instructions | automated (via bank)  |
| 04      | WPL Spotify | TWH DBS Multi SGD | standing instructions | automated (via bank)  |
| 05      | UOB CC      | TWH DBS Multi SGD | manual                | requires automation   |
| 06      | BOA CC      | TWH CITI          | ACH auto pay          | automated (via payee) |

- Parse bill statements and create normalized bill-payment records for all in-scope payees.
- Support payment capture for auto-pay and manual-pay methods, with explicit payment-state tracking.
- Use Google Sheets only as bridge UI for POC user interaction; keep canonical bill state in the app `bills` schema.

## Bill lifecycle and reconciliation requirements

### Active bill scope

- A bill is either active or inactive.
- Reconciliation checks apply only to active bills in the current period.
- Inactive bills are excluded from count and resolution checks.

### Bill data model

| id    |                 |      |     |                                         |
| ----- | --------------- | ---- | --- | --------------------------------------- |
| field |                 |      |     |                                         |
| type  |                 |      |     |                                         |
| req   |                 |      |     |                                         |
| rule  |                 |      |     |                                         |
| 01    | name            | text | y   | unique bill identifier                  |
| 02    | payee           | text | y   | counterparty receiving payment          |
| 03    | amount_type     | enum | y   | fixed or variable                       |
| 04    | expected_amount | dec  | n   | required when amount_type is fixed, SGD |
| 05    | billing_cycle   | enum | y   | monthly, quarterly, or annual           |
| 06    | active          | bool | y   | true means included in period checks    |

### Bill lifecycle state model

| id          |           |                                                   |                 |
| ----------- | --------- | ------------------------------------------------- | --------------- |
| state       |           |                                                   |                 |
| meaning     |           |                                                   |                 |
| next states |           |                                                   |                 |
| 01          | pending   | bill identified but not yet paid                  | paid, scheduled |
| 02          | scheduled | payment planned for a future date within period   | paid            |
| 03          | paid      | payment confirmed with statement transaction link |                 |

### Close criteria for bill lifecycle

- A bill may close only in paid or scheduled state.
- A bill in pending state at session close blocks period closure.
- A paid bill requires bank-statement transaction linkage.

### Shared-cost dependency boundary

- Shared-cost and consumption ownership belongs to [shared costs](shared-costs.md).
- Bill payment provides bill amount and paid-state inputs consumed by shared-cost lifecycle checks.

### Bill-level reconciliation checks

| id             |                            |                                    |
| -------------- | -------------------------- | ---------------------------------- |
| check          |                            |                                    |
| source fields  |                            |                                    |
| pass condition |                            |                                    |
| 01             | amount match               | bill amount vs statement line item |
| 02             | payee match                | bill payee vs statement payee      |
| 03             | payment date within period | bill payment_date vs close period  |
| 04             | paid status complete       | bill paid flag                     |

| id             |                            |                                                 |
| -------------- | -------------------------- | ----------------------------------------------- |
| check          |                            |                                                 |
| source fields  |                            |                                                 |
| pass condition |                            |                                                 |
| 01             | amount match               | amounts equal within SGD 0.00 tolerance         |
| 02             | payee match                | payee maps to same approved counterparty        |
| 03             | payment date within period | date within 2 months before or after period end |
| 04             | paid status complete       | flag is true and linkage reference is present   |

### Period-level reconciliation checks

| id             |                          |                                 |
| -------------- | ------------------------ | ------------------------------- |
| check          |                          |                                 |
| source fields  |                          |                                 |
| pass condition |                          |                                 |
| 01             | bills count matches      | bills_count vs active bill rows |
| 02             | bills paid count matches | bills_paid vs active bill rows  |
| 03             | all bills resolved       | bill state distribution         |

| id             |                          |                                                    |
| -------------- | ------------------------ | -------------------------------------------------- |
| check          |                          |                                                    |
| source fields  |                          |                                                    |
| pass condition |                          |                                                    |
| 01             | bills count matches      | count equals number of active bills for the period |
| 02             | bills paid count matches | paid count equals active bills in paid state       |
| 03             | all bills resolved       | no active bill remains in pending state            |

### Bill-payment session completion rule

- Each active bill must be either paid with statement linkage or scheduled.
