---
title: Data Model
doc_type: requirements
topic_type: owner
owner: data-model
scope: poc
---
# Data model

## Table of contents

- [Summary](#summary)
- [Purpose and boundary](#purpose-and-boundary)
- [Reference documents](#reference-documents)
- [Current state](#current-state)
- [Active schema set for POC](#active-schema-set-for-poc)
- [Schema definitions](#schema-definitions)
- [Lineage and statement aggregation boundary](#lineage-and-statement-aggregation-boundary)

## Summary

This document defines data-model schema definitions, schema naming, and schema object boundaries for the POC.

The canonical app schema name for the final reconciled statement-ready state is `close_book`.

## Purpose and boundary

This page defines schema-level data-model intent for monthly close.

In scope:

- Schema-level ownership and purpose.
- Canonical schema naming for the final statement-ready app state.
- Canonical table names and identifiers for HomeBudget synced data.
- High-level lineage boundaries between schemas.

Out of scope:

- Full column-level DDL.
- Storage engine tuning and physical optimization.
- Runtime orchestration sequencing.

## Current state

This schema list is intentionally not complete.
Additional schemas and objects, for example session-state domains, are expected to be added in later data-model revisions.

## Reference documents

- [workflow orchestration](workflow-orchestration.md)
- [source systems and lineage](source-systems-lineage.md)
- [transaction category mapping](transaction-category-mapping.md)
- [account classification](account-classification.md)
- [statements lifecycle](statements-lifecycle.md)

## Active schema set for POC

| id | schema      | role                               |
| -- | ----------- | ---------------------------------- |
| 01 | close_book    | reconciled statement-ready source        |
| 02 | statements    | bank statement transaction staging       |
| 03 | hb            | HomeBudget wrapper sync state            |
| 04 | mapping       | mapping state and mapping versions       |
| 05 | cash_staging  | wallet cash GS form aggregate staging    |
| 06 | bills         | bills, shared-costs, and consumption domain |

## Schema definitions

### `close_book`

- Final source-of-truth state for reconciled transactions and mapped dimensions used for statement aggregation.
- Financial statements draw directly from this schema.
- Draws lineage from `hb`, `statements`, `cash_staging`, `bills`, `mapping`, and direct parser flows where staging is skipped.
- IBKR is an example where parsed CSV may flow directly into `close_book` rather than `statements` staging.

### `statements`

- Raw imported and staged source transactions and balances for bank-statement sources.
- Bank-statement sources are staged at transaction level.
- Preserves source-level evidence needed for lineage and reconciliation.

### `cash_staging`

- Wallet cash aggregate staging schema for GS form cash expense data.
- GS form cash transactions are never staged at transaction level. They enter as period-and-category aggregates: one row per period and category key.
- Provides the aggregated expense inputs consumed by cash reconciliation. See [cash-reconcile.md](cash-reconcile.md) for aggregation logic.

### `hb`

- HomeBudget sync schema, populated through the HomeBudget wrapper during data sync.
- Canonical objects:
  - `hb_gl_txn`
  - `hb_account_dim` as SCD type 1
  - `hb_category_dim` as SCD type 1
- `hb_gl_txn` carries `hb_txn_uid` as deterministic hashed transaction UID.

### `mapping`

- Mapping schema used for account and category mapping state.
- Provides mapping outputs consumed by `close_book` during reconcile and statement aggregation.

### `bills`

- App-owned canonical schema for bill-payment, shared-cost, settlement, and consumption records.
- Parsed bill records are stored in this schema as raw domain inputs for allocation and reconciliation logic.
- During POC, Google Sheets may be used as bridge UI for operator input and review, but canonical state remains in this schema.
- Provides bill domain lineage anchors consumed by `close_book` and bill-workstream checks.

## Lineage and statement aggregation boundary

- `close_book` is the only schema from which statement aggregates are produced.
- `statements`, `hb`, `cash_staging`, `bills`, and `mapping` feed `close_book` and provide lineage anchors.
- Lineage from source to output must remain queryable across these schema boundaries.
