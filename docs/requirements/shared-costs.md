---
title: Shared Costs
doc_type: requirements
topic_type: owner
owner: shared-costs
scope: poc
---
# Shared Costs

## Table of contents

- [Purpose and boundary](#purpose-and-boundary)
- [Reference documents](#reference-documents)
- [Primary scope](#primary-scope)
- [Out of scope](#out-of-scope)
- [Lifecycle-link ownership rule](#lifecycle-link-ownership-rule)
- [Field-level contract baseline](#field-level-contract-baseline)
- [Shared-cost parameter constraints](#shared-cost-parameter-constraints)
- [Session completion rule](#session-completion-rule)
- [Consumption baseline](#consumption-baseline)
- [Consumption parameter constraints](#consumption-parameter-constraints)
- [Cross-page validation rules](#cross-page-validation-rules)

## Purpose and boundary

This document defines the requirements for shared-cost allocation, settlement, and consumption tracking.

## Scope

- Shared-cost schema specifications - record contracts and validation baseline
- Shared-cost parameter constraints and settlement requirements
- Shared-cost lifecycle-link dependency on bill amount
- Consumption baseline and constraints
- Share-cost and consumption records are stored in the app `bills` schema. 
- Google Sheets is used as a minimal UI for user input and review, to be phased out in later phase with browser UI.

## Out of scope

- Bill lifecycle state model ownership
- Bill-level and period-level bill-payment reconciliation ownership

## Reference documents

- [bill payment](bill-payment.md)
- [reconciliation engine](reconciliation-engine.md)
- [exception and error handling](exception-error-handling.md)

## Lifecycle-link ownership rule

- Bill payment and shared-cost settlement are separate process tracks.
- Bill records may be paid or unpaid independent of shared costs status.
- Shared-cost records may be settled or unsettled independent of bill status.
- The only lifecycle dependency is that bill amount must be defined before shared-cost settlement can occur.

## Field-level contract baseline

Field-level contract means each in-scope field has explicit type, requiredness, allowed values, derivation rule, and failure action.

Validation baseline for shared-cost records in the app `bills` schema, with bridge UI mapping from `gsheet/shared-expenses.json` range records A to H during POC:

| id                  |                   |         |     |                         |
| ------------------- | ----------------- | ------- | --- | ----------------------- |
| field               |                   |         |     |                         |
| type                |                   |         |     |                         |
| req                 |                   |         |     |                         |
| rule                |                   |         |     |                         |
| validation baseline |                   |         |     |                         |
| 01                  | record_date       | date    | y   | posting date            |
| 02                  | description       | text    | y   | short narrative         |
| 03                  | total_amount_sgd  | decimal | y   | gross shared amount     |
| 04                  | participant_count | int     | y   | equal-share divisor N   |
| 05                  | user_share_amount | decimal | y   | derived total over N    |
| 06                  | category          | text    | y   | allocation class        |
| 07                  | payee             | text    | y   | settlement counterparty |
| 08                  | status            | enum    | y   | HB record state         |

| id                  |                   |                                |
| ------------------- | ----------------- | ------------------------------ |
| field               |                   |                                |
| type                |                   |                                |
| req                 |                   |                                |
| rule                |                   |                                |
| validation baseline |                   |                                |
| 01                  | record_date       | valid date and within close mo |
| 02                  | description       | 1 to 200 chars                 |
| 03                  | total_amount_sgd  | signed decimal and scale 2     |
| 04                  | participant_count | integer 2 or greater           |
| 05                  | user_share_amount | abs value up to abs total      |
| 06                  | category          | in allowed shared-cost set     |
| 07                  | payee             | non-empty and mapped party     |
| 08                  | status            | created or recorded            |

## Shared-cost parameter constraints

| id                  |                        |         |     |                       |
| ------------------- | ---------------------- | ------- | --- | --------------------- |
| parameter           |                        |         |     |                       |
| type                |                        |         |     |                       |
| req                 |                        |         |     |                       |
| rule                |                        |         |     |                       |
| validation baseline |                        |         |     |                       |
| 01                  | split_basis            | const   | y   | equal-share only      |
| 02                  | rounding_mode          | enum    | y   | monetary rounding     |
| 03                  | settlement_account     | text    | y   | HB settlement account |
| 04                  | settlement_currency    | enum    | y   | posting currency      |
| 05                  | variance_tolerance_sgd | decimal | y   | max allowed variance  |

| id                  |                        |                              |
| ------------------- | ---------------------- | ---------------------------- |
| parameter           |                        |                              |
| type                |                        |                              |
| req                 |                        |                              |
| rule                |                        |                              |
| validation baseline |                        |                              |
| 01                  | split_basis            | 1_over_n                     |
| 02                  | rounding_mode          | half-up to 2 dp              |
| 03                  | settlement_account     | must equal 30 CC Hashemis    |
| 04                  | settlement_currency    | SGD only                     |
| 05                  | variance_tolerance_sgd | fixed 0.00 at 0.01 precision |

## Session completion rule

- If any shared-cost record remains incomplete for HomeBudget recording, the shared-cost session is incomplete.

## Consumption baseline

Consumption records in this scope are stored in the app `bills` schema and linked to bill and shared-cost lifecycle context.

| id                  |                      |         |     |                       |
| ------------------- | -------------------- | ------- | --- | --------------------- |
| field               |                      |         |     |                       |
| type                |                      |         |     |                       |
| req                 |                      |         |     |                       |
| rule                |                      |         |     |                       |
| validation baseline |                      |         |     |                       |
| 01                  | period_year          | int     | y   | close period year     |
| 02                  | period_month         | int     | y   | close period month    |
| 03                  | utility_type         | enum    | y   | metric family         |
| 04                  | usage_value          | decimal | y   | measured quantity     |
| 05                  | usage_unit           | enum    | y   | measurement unit      |
| 06                  | billed_amount_sgd    | decimal | y   | billed total          |
| 07                  | statement_issue_date | date    | y   | source statement date |
| 08                  | statement_due_date   | date    | n   | payment due date      |
| 09                  | source_account       | text    | y   | paying account        |
| 10                  | source_statement_ref | text    | y   | lineage key           |

| id                  |                      |                                |
| ------------------- | -------------------- | ------------------------------ |
| field               |                      |                                |
| type                |                      |                                |
| req                 |                      |                                |
| rule                |                      |                                |
| validation baseline |                      |                                |
| 01                  | period_year          | 2000 to 2100                   |
| 02                  | period_month         | 1 to 12                        |
| 03                  | utility_type         | electricity water gas          |
| 04                  | usage_value          | signed decimal                 |
| 05                  | usage_unit           | kwh or m3                      |
| 06                  | billed_amount_sgd    | signed decimal and scale 2     |
| 07                  | statement_issue_date | valid date                     |
| 08                  | statement_due_date   | more than or equal issue date  |
| 09                  | source_account       | in bills in-scope account list |
| 10                  | source_statement_ref | unique within period and payee |

## Consumption parameter constraints

| id                  |                      |      |     |               |                             |
| ------------------- | -------------------- | ---- | --- | ------------- | --------------------------- |
| parameter           |                      |      |     |               |                             |
| type                |                      |      |     |               |                             |
| req                 |                      |      |     |               |                             |
| rule                |                      |      |     |               |                             |
| validation baseline |                      |      |     |               |                             |
| 01                  | missing_value_policy | enum | y   | null handling | block                       |
| 02                  | duplicate_row_policy | enum | y   | dedupe policy | reject same ref same period |

## Cross-page validation rules

- Shared-cost ownership boundaries are explicit and cross-linked to bill-payment owner page.
- Lifecycle-link dependency rule is published in this page.
- Shared-cost and consumption contracts are explicit and testable.
