---
title: Transaction Category Mapping
doc_type: requirements
topic_type: owner
owner: transaction-category-mapping
scope: poc
---
# Transaction Category Mapping

## Table of contents

- [Purpose and boundary](#purpose-and-boundary)
- [Reference documents](#reference-documents)
- [Primary scope](#primary-scope)
- [Out of scope](#out-of-scope)
- [Source of truth and ownership](#source-of-truth-and-ownership)
- [Category data model and CRUD interface](#category-data-model-and-crud-interface)
- [Stage 1 mapping requirements](#stage-1-mapping-requirements)
- [Stage 2 mapping requirements](#stage-2-mapping-requirements)
- [Session-close completeness gate](#session-close-completeness-gate)
- [Event-driven mapping-change workflow boundary](#event-driven-mapping-change-workflow-boundary)
- [Validation rules](#validation-rules)

## Purpose and boundary

This document defines the requirements for transaction category mapping.

## Reference documents

- [accounting logic](accounting-logic.md)
- [account classification](account-classification.md)
- [source systems and lineage](source-systems-lineage.md)
- [data model](data-model.md)
- [cash reconcile](cash-reconcile.md)
- [exception and error handling](exception-error-handling.md)

## Primary scope

- Mapping behavior from source category to reporting category
- Mapping-stage ownership and boundaries
- Mapping completeness gate for close readiness
- Mapping validation requirements for expected-condition operations

## Out of scope

- Exception-policy behavior for unresolved mapping
- Reconciliation algorithm and variance policy
- Statement lifecycle publication policy

## Source of truth and ownership

- Stage 1 and stage 2 mapping behavior is owned by this page.
- Stage 1 source evidence uses the helper workbook mapping region.
- Stage 2 source evidence uses financial statements workbook mapping regions.

## Category data model and CRUD interface

- Mapping records are managed through the category data model.
- The user interface for mapping CRUD is a custom Google Sheets UI.
- Backend CRUD services own create, read, update, and delete behavior against the category data model.
- Monthly close consumes the approved mapping state from the category data model and does not depend on ad hoc local mapping files.
- HomeBudget category source data is refreshed during data sync into the hb schema category dimension defined in [data-model.md](data-model.md).

## Stage 1 mapping requirements

- Stage 1 maps HomeBudget synced category dimension records to GL account codes.
- Stage 1 mapping uses the helper workbook cat_map region.
- Income-path category assignment is required and must be explicit.

## Stage 2 mapping requirements

- Stage 2 maps GL-enriched rows to financial statement categories.
- Income statement mapping uses expense-category mapping dimensions.
- Balance sheet mapping uses account classification mapping dimensions.

## Session-close completeness gate

- Mapping must be complete for both income and expense paths.
- If required mapping is missing, close cannot proceed.

## Event-driven mapping-change workflow boundary

- Mapping updates are event-driven and outside the main monthly-close run.
- Monthly close consumes the active approved mapping set.

## Validation rules

- Mapping tables have no duplicate active keys.
- Mapping tables have no null required category outputs.
- Session-close completeness gate is enforced for each period.

