---
title: Forex Translation Design
doc_type: design
topic_type: owner
owner: forex-translation
scope: poc
last_updated: 2026-05-02
status: draft
---

# Forex Translation Design

## Summary

This document defines monthly forex translation for statement consolidation to a single reporting currency basis. The design uses a dedicated set of `close_book` forex aggregate tables at account-month level and produces period-level forex mark-to-market outputs for Stage 7 statements.

This design is separate from transaction-level forex settlement adjustments used in account reconcile for forex card charge settlement differences.

## Table of contents

- [Purpose and scope](#purpose-and-scope)
- [Workflow placement](#workflow-placement)
- [Translation policy](#translation-policy)
- [Governing equations](#governing-equations)
- [Close book forex schema](#close-book-forex-schema)
- [Aggregation method](#aggregation-method)
- [Rate timing basis](#rate-timing-basis)
- [SCD and update policy](#scd-and-update-policy)
- [Stage 7 execution algorithm](#stage-7-execution-algorithm)
- [Validation and controls](#validation-and-controls)
- [Error handling](#error-handling)

## Purpose and scope

The forex translation design serves statement-level consolidation. Its output is account-month reporting currency balances and forex mark-to-market by period for income statement and balance sheet aggregation.

The design is in scope for:

- FX-denominated assets and liabilities included in statement build.
- Account-month rollup values for beginning, transactions, ending, and forex M2M in reporting currency.
- Stage 7 statement build reads from forex aggregate tables in `close_book`.

The design is out of scope for:

- Transaction-level card settlement differences used during reconcile adjustments.
- Intraday valuation workflows.

## Workflow placement

Forex translation for statement consolidation is owned by Stage 7 statements.

- Stage 5 and Stage 6 remain account sync and reconcile workflows.
- Stage 7 executes the account-month forex translation pipeline and writes statement-ready forex aggregates to `close_book`.
- Statement builder then aggregates translated balances and forex M2M outputs with other statement sections.

## Translation policy

Reporting currency defaults to SGD.

Policy decisions:

- Base rollup grain is `account_id + period_month + reporting_currency`.
- Net transaction flow uses transaction-date conversion, native amount converted at transaction-date rate.
- Month-end valuation uses synthetic month-end close timestamp at local month-end 23:59.
- Forecast maintenance horizon is current month through end of reporting year.

## Governing equations

For each account-month row, define:

- $B_n$ as beginning balance in native currency.
- $E_n$ as ending balance in native currency.
- $T_n$ as net transaction flow in native currency for the month.
- $R_b$ as beginning basis FX rate to reporting currency.
- $R_e$ as month-end FX rate to reporting currency.
- $T_r$ as net transaction flow converted to reporting currency.

Core equations:

$$
T_r = \sum_{i=1}^{N} (txn\_amount\_{native,i} \times fx\_rate\_{txn\_date,i})
$$

$$
B_r = B_n \times R_b
$$

$$
E_r = E_n \times R_e
$$

$$
FX\_M2M_r = E_r - B_r - T_r
$$

Identity check:

$$
E_r = B_r + T_r + FX\_M2M_r
$$

Special case for account currency equal to reporting currency:

- $R_b = 1$, $R_e = 1$, and $FX\_M2M_r = 0$.

## Close book forex schema

The forex translation design introduces three tables in the `close_book` schema.

### 1. close_book.forex_rate_monthly

| id | column            | type     | description                           |
| -- | ----------------- | -------- | ------------------------------------- |
| 01 | id                | integer  | surrogate primary key                 |
| 02 | period_month      | text     | YYYY-MM                               |
| 03 | base_currency     | text     | account native currency               |
| 04 | reporting_currency | text    | default SGD                           |
| 05 | fx_rate_month_end | numeric  | month-end rate base to reporting      |
| 06 | rate_basis        | text     | synthetic_month_end_2359_local        |
| 07 | source_system     | text     | forex source id from config           |
| 08 | source_timestamp_at | text   | source quote timestamp in UTC         |
| 09 | synthetic_timestamp_at | text | local month-end 23:59 normalized UTC |
| 10 | is_locked         | integer  | 1 for finalized month, else 0         |
| 11 | created_at        | text     | UTC ISO-8601                          |
| 12 | updated_at        | text     | UTC ISO-8601                          |

### 2. close_book.forex_account_monthly

| id | column                    | type     | description                          |
| -- | ------------------------- | -------- | ------------------------------------ |
| 01 | id                        | integer  | surrogate primary key                |
| 02 | account_id                | text     | account identifier                   |
| 03 | period_month              | text     | YYYY-MM                              |
| 04 | account_currency          | text     | native currency code                 |
| 05 | reporting_currency        | text     | default SGD                          |
| 06 | beginning_balance_native  | numeric  | native opening balance               |
| 07 | net_txn_native            | numeric  | native month net flow                |
| 08 | ending_balance_native     | numeric  | native closing balance               |
| 09 | fx_rate_begin             | numeric  | beginning basis FX rate              |
| 10 | fx_rate_month_end         | numeric  | month-end FX rate                    |
| 11 | beginning_balance_reporting | numeric | reporting opening balance            |
| 12 | net_txn_reporting         | numeric  | reporting net flow at txn-date rates |
| 13 | ending_balance_reporting  | numeric  | reporting closing balance            |
| 14 | fx_m2m_reporting          | numeric  | period forex mark-to-market          |
| 15 | snapshot_state            | text     | historical, current, or forecast     |
| 16 | run_id                    | text     | forex run lineage id                 |
| 17 | created_at                | text     | UTC ISO-8601                         |
| 18 | updated_at                | text     | UTC ISO-8601                         |

Unique key: `account_id + period_month + reporting_currency`.

### 3. close_book.forex_account_monthly_snapshot

| id | column               | type     | description                         |
| -- | -------------------- | -------- | ----------------------------------- |
| 01 | id                   | integer  | surrogate primary key               |
| 02 | forex_account_monthly_id | integer | foreign key to forex_account_monthly |
| 03 | account_id           | text     | copied natural key                  |
| 04 | period_month         | text     | copied natural key                  |
| 05 | reporting_currency   | text     | copied natural key                  |
| 06 | snapshot_version     | integer  | monotonic per natural key           |
| 07 | snapshot_reason      | text     | month_close, rerun, or forecast     |
| 08 | is_current           | integer  | 1 active snapshot, else 0           |
| 09 | valid_from_at        | text     | UTC ISO-8601                        |
| 10 | valid_to_at          | text     | UTC ISO-8601 or null                |
| 11 | payload_hash         | text     | deterministic row hash              |
| 12 | run_id               | text     | forex run lineage id                |

SCD behavior is Type 2 style versioning on account-month natural key.

## Aggregation method

Account-month aggregation is deterministic and period scoped.

1. Collect source records for one account and target period from normalized schemas.
2. Derive native beginning and ending balances at period boundaries.
3. Aggregate transactions in native currency to `net_txn_native`.
4. Convert each transaction amount to reporting currency by transaction-date rate and sum to `net_txn_reporting`.
5. Apply month-end rate conversion for beginning and ending reporting balances.
6. Compute `fx_m2m_reporting` by identity equation.
7. Persist to `forex_account_monthly` and append snapshot record.

Aggregation by account group:

- Bank and card accounts use parsed statement transaction rows.
- Wallet and investment accounts use account-level month transaction feeds and valuation inputs.
- Accounts with no period transactions set `net_txn_native` and `net_txn_reporting` to zero.

## Rate timing basis

Rate timing basis is synthetic month-end close at local month-end 23:59.

Rules:

- For past months, use the month-end rate for that period and lock the row.
- If source does not provide an exact 23:59 quote, use last available quote on or before month-end and normalize to synthetic 23:59 local timestamp.
- Store both source timestamp and synthetic timestamp.

## SCD and update policy

The design uses SCD Type 2 snapshots with period-state rules.

Past months:

- Month state is `historical`.
- Base row in `forex_account_monthly` is immutable after month close.
- Every accepted restatement creates a new snapshot version and updates `is_current` pointers in snapshot table.

Current month:

- Month state is `current`.
- Row is updatable on each forex run using current available rates.
- Each run appends a new snapshot version for traceability.

Forecast months:

- Month state is `forecast`.
- Coverage horizon is current month through end of reporting year.
- Forecast rows update on each run using current spot-driven rate assumptions.
- Snapshot versions are appended on every run.

## Stage 7 execution algorithm

Stage 7 executes forex translation before final statement aggregation.

1. Resolve target period and reporting year horizon.
2. Load required FX rates and source balances and transactions.
3. Build or refresh `forex_rate_monthly` rows for periods in scope.
4. For each account and month in scope, compute aggregate values and `fx_m2m_reporting`.
5. Apply period-state policy, immutable for historical months and upsert for current and forecast months.
6. Write `forex_account_monthly` and append `forex_account_monthly_snapshot`.
7. Run identity validation and variance controls.
8. Expose Stage 7 statement builder read model from `forex_account_monthly` current rows.

## Validation and controls

Required controls:

- Equation identity check must pass per account-month: `ending = beginning + net_txn + fx_m2m` in reporting currency.
- Currency pair completeness must be present for all required conversions.
- Snapshot continuity must hold, one `is_current = 1` row per natural key in snapshot table.
- Historical month rows with `is_locked = 1` must not be updated in place.
- Decimal precision policy must follow project financial precision rules.

## Error handling

| id | error_case                    | type     | behavior                         |
| -- | ----------------------------- | -------- | -------------------------------- |
| 01 | missing month-end FX rate     | blocking | fail translation for that period |
| 02 | missing txn-date FX rate      | blocking | fail transaction conversion       |
| 03 | identity check failure        | blocking | block statement build             |
| 04 | locked historical row update  | validation | reject update and log violation |
| 05 | snapshot version gap detected | validation | block run and require repair    |
| 06 | horizon period expansion fails | review  | run current month only and flag  |
