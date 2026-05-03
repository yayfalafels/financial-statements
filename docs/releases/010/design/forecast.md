---
title: Forecast Design
doc_type: design
topic_type: owner
owner: forecast-design
scope: poc
last_updated: 2026-05-02
status: draft
---

# Forecast Design

## Summary

This document defines the forecasting design. Forecast is user-driven in Google Sheets interactive worksheets and is persisted by the app into dedicated forecast tables.

- Forecast values are authored in account currency. Common currency projection is produced by running forex translation on top of account currency forecast results.
- Reporting-year consolidated statements combine reconciled actuals month to date and forecast for remaining months.

## Table of contents

- [Purpose and scope](#purpose-and-scope)
- [Forecast operating model](#forecast-operating-model)
- [User input model in Google Sheets](#user-input-model-in-google-sheets)
- [Forecast pipeline](#forecast-pipeline)
- [Governing equations](#governing-equations)
- [Data model and tables](#data-model-and-tables)
- [SCD and overwrite policy](#scd-and-overwrite-policy)
- [Reporting-year statement snapshots](#reporting-year-statement-snapshots)
- [Year initialization and N plus 1 planning](#year-initialization-and-n-plus-1-planning)
- [Validation and controls](#validation-and-controls)
- [Error handling](#error-handling)

## Purpose and scope

In scope:

- Manual forecast authoring in Google Sheets with month columns and line-item rows.
- Forecast subtopics: expense budgets, income plans, target bank balances, IBKR net trades, CPF deductions and allocations, earning account returns, tax liabilities, and implied cash transfers.
- App persistence of forecast outputs into dedicated tables by account-month and subtopic.
- Reporting-year consolidated statements with reconciled actuals month to date plus forecast months.
- Dual-currency statement projection: account currency and common reporting currency.

Out of scope:

- Automated optimization of user-entered plans.
- Broker execution or tax filing workflows.

## Forecast operating model

The user remains the source authority for planning assumptions in Google Sheets. The app reads forecast inputs and computed worksheet outputs through the Google Sheets adapter and stores normalized snapshots in SQLite.

Forecast window is current month to end of reporting year. Forecast updates are continuous for current and future months.

Historical months are historized and immutable except controlled restatement.

## User input model in Google Sheets

Forecast sheets use matrix layout:

- Columns are months in YYYY-MM format.
- Rows are line entries for each topic.

User-managed inputs include:

- Forecast spending by category.
- Forecast income by source.
- Target bank account balances by month.
- Target IBKR net trade amount by month.
- CPF deductions and allocation splits across OA, SA, MA, RA.
- Target return assumptions for earning accounts, CPF, IBKR, and investments.

Sheet-calculated outputs include:

- CPF projection using deduction and allocation rules.
- Investment and IBKR projection using return and trade assumptions.
- Implied settlement and cash transfer amounts needed to satisfy fixed bank balance targets.
- IBKR leverage and performance metrics against user-defined limits.
- Expected tax liability from salary and IBKR worksheets mapped to forecast tax liability account.

## Forecast pipeline

1. User edits and confirms forecast worksheets in Google Sheets.
2. Google Sheets adapter reads period matrices and worksheet outputs.
3. Backend forecast runtime validates structure and period coverage.
4. Runtime normalizes topic outputs to table-specific models.
5. Runtime computes account-month aggregate forecast layer.
6. Runtime persists topic tables and account aggregate table.
7. Runtime updates current table rows for current and future months.
8. Runtime appends historized snapshots for audit and recovery.
9. Stage 7 statement build combines actuals and forecast for reporting-year projections.
10. Forex translation runs on forecast account-currency outputs to produce common currency projections.

## Governing equations

For account-month in account currency:

- $B_a$ is opening balance.
- $I_a$ is total income flow.
- $E_a$ is total expense flow.
- $T_a$ is net transfer flow, including implied transfers.
- $R_a$ is return flow for earning accounts.
- $N_a$ is net trade flow for IBKR.
- $C_a$ is closing balance.

Core account balance equation:

$$
C_a = B_a + I_a - E_a + T_a + R_a + N_a
$$

For fixed-target accounts, bank accounts:

$$
T_a^{implied} = C_a^{target} - (B_a + I_a - E_a + R_a + N_a)
$$

For IBKR where closing balance is not fixed:

$$
C_{ibkr} = B_{ibkr} + I_{ibkr} - E_{ibkr} + T_{ibkr} + R_{ibkr} + N_{ibkr}
$$

Tax liability projection:

$$
Tax_{m} = Tax_{salary,m} + Tax_{ibkr,m}
$$

Reporting-year consolidated statement by month $m$:

$$
Statement_{m} =
\begin{cases}
Actual_{m}, & m \leq current\_month \\
Forecast_{m}, & m > current\_month
\end{cases}
$$

Common currency projection is produced by applying forex translation equations from [docs/releases/010/design/forex.md](docs/releases/010/design/forex.md) to account-currency forecast balances and flows.

## Data model and tables

Forecast persistence uses an account aggregate table and specialized topic tables.

### 1. forecast.forecast_account_monthly

| id | column              | type    | description                          |
| -- | ------------------- | ------- | ------------------------------------ |
| 01 | id                  | integer | surrogate primary key                |
| 02 | reporting_year      | integer | forecast reporting year              |
| 03 | period_month        | text    | YYYY-MM                              |
| 04 | account_id          | text    | account identifier                   |
| 05 | account_currency    | text    | account currency code                |
| 06 | opening_balance     | numeric | opening balance in account currency  |
| 07 | income_amount       | numeric | forecast income flow                 |
| 08 | expense_amount      | numeric | forecast expense flow                |
| 09 | transfer_amount     | numeric | explicit plus implied transfers      |
| 10 | return_amount       | numeric | projected return flow                |
| 11 | net_trade_amount    | numeric | projected IBKR net trade flow        |
| 12 | tax_liability_amount | numeric | projected tax liability flow         |
| 13 | closing_balance     | numeric | forecast closing balance             |
| 14 | period_state        | text    | historical, current, future          |
| 15 | run_id              | text    | forecast run lineage id              |
| 16 | created_at          | text    | UTC ISO-8601                         |
| 17 | updated_at          | text    | UTC ISO-8601                         |

Unique key: `reporting_year + period_month + account_id`.

### 2. forecast.forecast_expense_budget_monthly

| id | column         | type    | description                       |
| -- | -------------- | ------- | --------------------------------- |
| 01 | id             | integer | surrogate primary key             |
| 02 | reporting_year | integer | forecast reporting year           |
| 03 | period_month   | text    | YYYY-MM                           |
| 04 | gl_code        | text    | expense category code             |
| 05 | amount         | numeric | budget amount in account currency |
| 06 | source_sheet   | text    | Google Sheets source tab          |
| 07 | run_id         | text    | forecast run lineage id           |
| 08 | updated_at     | text    | UTC ISO-8601                      |

### 3. forecast.forecast_income_monthly

| id | column         | type    | description                      |
| -- | -------------- | ------- | -------------------------------- |
| 01 | id             | integer | surrogate primary key            |
| 02 | reporting_year | integer | forecast reporting year          |
| 03 | period_month   | text    | YYYY-MM                          |
| 04 | income_source  | text    | salary, dividend, other          |
| 05 | account_id     | text    | receiving account                |
| 06 | amount         | numeric | income amount in account currency |
| 07 | run_id         | text    | forecast run lineage id          |
| 08 | updated_at     | text    | UTC ISO-8601                     |

### 4. forecast.forecast_ibkr_monthly

| id | column                | type    | description                        |
| -- | --------------------- | ------- | ---------------------------------- |
| 01 | id                    | integer | surrogate primary key              |
| 02 | reporting_year        | integer | forecast reporting year            |
| 03 | period_month          | text    | YYYY-MM                            |
| 04 | net_trade_amount      | numeric | projected net trades               |
| 05 | projected_return_amount | numeric | projected IBKR return             |
| 06 | leverage_ratio        | numeric | projected leverage                 |
| 07 | margin_usage_ratio    | numeric | projected margin usage             |
| 08 | leverage_limit        | numeric | user-defined leverage limit        |
| 09 | margin_limit          | numeric | user-defined margin limit          |
| 10 | is_limit_breached     | integer | 1 if breached else 0               |
| 11 | run_id                | text    | forecast run lineage id            |
| 12 | updated_at            | text    | UTC ISO-8601                       |

### 5. forecast.forecast_cpf_monthly

| id | column                 | type    | description                     |
| -- | ---------------------- | ------- | ------------------------------- |
| 01 | id                     | integer | surrogate primary key           |
| 02 | reporting_year         | integer | forecast reporting year         |
| 03 | period_month           | text    | YYYY-MM                         |
| 04 | deduction_amount       | numeric | total CPF deduction             |
| 05 | oa_allocation_amount   | numeric | OA allocation                   |
| 06 | sa_allocation_amount   | numeric | SA allocation                   |
| 07 | ma_allocation_amount   | numeric | MA allocation                   |
| 08 | ra_allocation_amount   | numeric | RA allocation                   |
| 09 | projected_return_amount | numeric | projected CPF return            |
| 10 | run_id                 | text    | forecast run lineage id         |
| 11 | updated_at             | text    | UTC ISO-8601                    |

### 6. forecast.forecast_tax_monthly

| id | column                    | type    | description                       |
| -- | ------------------------- | ------- | --------------------------------- |
| 01 | id                        | integer | surrogate primary key             |
| 02 | reporting_year            | integer | forecast reporting year           |
| 03 | period_month              | text    | YYYY-MM                           |
| 04 | salary_tax_amount         | numeric | expected salary-tax component     |
| 05 | ibkr_tax_amount           | numeric | expected IBKR-tax component       |
| 06 | total_tax_liability_amount | numeric | total expected tax liability      |
| 07 | tax_liability_account_id  | text    | liability account                 |
| 08 | run_id                    | text    | forecast run lineage id           |
| 09 | updated_at                | text    | UTC ISO-8601                      |

### 7. forecast.forecast_transfer_solver_monthly

| id | column                    | type    | description                         |
| -- | ------------------------- | ------- | ----------------------------------- |
| 01 | id                        | integer | surrogate primary key               |
| 02 | reporting_year            | integer | forecast reporting year             |
| 03 | period_month              | text    | YYYY-MM                             |
| 04 | account_id                | text    | target account                      |
| 05 | target_closing_balance    | numeric | user-specified target               |
| 06 | unconstrained_closing_balance | numeric | computed before implied transfers |
| 07 | implied_transfer_amount   | numeric | balancing transfer                  |
| 08 | counterparty_account_id   | text    | transfer counterparty               |
| 09 | run_id                    | text    | forecast run lineage id             |
| 10 | updated_at                | text    | UTC ISO-8601                        |

### 8. forecast.forecast_snapshot

| id | column              | type    | description                          |
| -- | ------------------- | ------- | ------------------------------------ |
| 01 | id                  | integer | surrogate primary key                |
| 02 | table_name          | text    | source table                         |
| 03 | natural_key         | text    | deterministic natural key string     |
| 04 | snapshot_version    | integer | monotonic version per natural key    |
| 05 | period_month        | text    | YYYY-MM                              |
| 06 | reporting_year      | integer | forecast reporting year              |
| 07 | snapshot_state      | text    | historical, current, future          |
| 08 | is_current          | integer | 1 active snapshot else 0             |
| 09 | valid_from_at       | text    | UTC ISO-8601                         |
| 10 | valid_to_at         | text    | UTC ISO-8601 or null                 |
| 11 | payload_hash        | text    | deterministic row hash               |
| 12 | run_id              | text    | forecast run lineage id              |

## SCD and overwrite policy

Past months:

- Forecast rows are historized and treated as immutable.
- Corrections require controlled restatement with new snapshot version.

Current and future months:

- Base topic tables and account aggregate table are overwritten by latest run values.
- Snapshot rows are appended for each run for lineage and recovery.

This provides operational overwrite behavior with full SCD history.

## Reporting-year statement snapshots

Consolidated statement projection is reporting-year scoped and snapshot historized at each statement generation timestamp.

### 9. close_book.forecast_statement_yearly

| id | column                    | type    | description                         |
| -- | ------------------------- | ------- | ----------------------------------- |
| 01 | id                        | integer | surrogate primary key               |
| 02 | reporting_year            | integer | statement reporting year            |
| 03 | statement_timestamp_at    | text    | generation timestamp UTC            |
| 04 | period_month              | text    | YYYY-MM                             |
| 05 | account_id                | text    | account identifier                  |
| 06 | basis_type                | text    | account_currency or reporting_currency |
| 07 | currency_code             | text    | account or common currency code     |
| 08 | data_source_type          | text    | actual_mtd or forecast              |
| 09 | income_amount             | numeric | period income                       |
| 10 | expense_amount            | numeric | period expense                      |
| 11 | balance_amount            | numeric | period closing balance              |
| 12 | net_income_amount         | numeric | period net income                   |
| 13 | run_id                    | text    | generation lineage id               |
| 14 | created_at                | text    | UTC ISO-8601                        |

Construction rule:

- For months up to current month, use reconciled actuals.
- For months after current month through year end, use forecast tables.
- Generate both account-currency and common-currency basis rows.

## Year initialization and N plus 1 planning

Forecast year workspace can be opened for a future reporting year before that year begins.

Rules:

- In year N month M, user may initialize reporting year N plus 1 at any time.
- Initialization creates monthly skeleton rows for N plus 1 from January to December.
- Input templates and solver limits are copied from latest available year as baseline.
- N plus 1 forecast remains independent from current-year forecast state.

Example:

- In October 2026, user initializes reporting year 2027 and begins forecast authoring.

## Validation and controls

- Month matrix completeness check for all months in forecast window.
- Required topic coverage check: expenses, income, bank targets, IBKR trades, CPF, returns, tax.
- Account balance identity check per account-month using forecast equation.
- Fixed-target account closure check must pass for bank accounts.
- IBKR limit check must pass or be explicitly approved with rationale.
- Tax liability projection must equal salary component plus IBKR component.
- Forecast and statement snapshots must have deterministic natural keys and monotonic versions.

## Error handling

| id | error_case                         | type      | behavior                             |
| -- | ---------------------------------- | --------- | ------------------------------------ |
| 01 | missing month column in sheet      | blocking  | stop ingest and surface sheet error  |
| 02 | missing required forecast topic    | blocking  | stop run and request user completion |
| 03 | fixed-target balance unsatisfied   | review    | flag solver output and hold publish  |
| 04 | IBKR leverage or margin breach     | review    | flag and require user acknowledgment |
| 05 | tax projection mismatch            | validation | reject tax liability write           |
| 06 | snapshot key or version conflict   | blocking  | stop write and require repair        |
| 07 | year initialization conflict       | validation | reject duplicate year initialize     |
