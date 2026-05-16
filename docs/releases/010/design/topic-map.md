---
title: Design Topic Map
doc_type: design
topic_type: reference
scope: poc
last_updated: 2026-05-02
status: draft
---

# Design Topic Map

## Summary

This document maps the full set of design topics to their target design documents. It serves two purposes: requirement traceability — every owner requirement topic is either mapped to a design doc or explicitly excluded with rationale — and component coverage — every architecture component is assigned to a design doc or grouped under a covering doc.

## Table of contents

- [Requirement traceability](#requirement-traceability)
  - [Owner topics](#owner-topics)
  - [Reference topics](#reference-topics)
- [Design-only topics](#design-only-topics)
- [Component coverage inventory](#component-coverage-inventory)
  - [Components with individual design coverage](#components-with-individual-design-coverage)
  - [Grouped components](#grouped-components)

---

## Requirement traceability

### Owner topics

Owner topics define behavioral requirements that must be translated into design contracts. Each owner topic either maps to a design doc or carries an explicit exclusion rationale.

| id | requirement topic          | design doc               | notes                                                     |
| -- | -------------------------- | ------------------------ | --------------------------------------------------------- |
| 01 | account-classification     | no design equivalent     | self-contained reference; consumed by design docs         |
| 02 | accounting-logic           | no design equivalent     | self-contained reference; consumed by design docs         |
| 03 | bank-statements            | bank-statements.md       | adapter contract for bank CSV and Excel source files      |
| 04 | bill-payment               | bill-payment.md          | bill intake, share allocation, and HomeBudget posting     |
| 05 | cash-reconcile             | cash-bills.md            | cash form input and wallet reconciliation contract        |
| 06 | cpf-integration            | cpf.md                   | CPF adapter contract for balance-level close              |
| 07 | data-model                 | data-model.md            | canonical entity model; all design docs derive from this  |
| 08 | exception-error-handling   | error-handling.md        | error taxonomy, propagation paths, and recovery behavior  |
| 09 | financial-statements       | statements.md            | statement builder aggregation and close_book sourcing     |
| 10 | google-sheets              | google-sheets.md         | Google Sheets adapter contract and workbook structure     |
| 11 | homebudget                 | homebudget.md            | HomeBudget wrapper adapter invocation contract            |
| 12 | ibkr-integration           | ibkr.md                  | IBKR CSV adapter for IBA and IRA derivation               |
| 13 | interaction-approvals      | workflows.md             | checkpoint and approval behavior within workflow stages   |
| 14 | reconciliation-engine      | reconciliation.md        | match algorithm, tolerance rules, and adjustment posting  |
| 15 | shared-costs               | bill-payment.md          | share allocation is a workstream in bill payment design   |
| 16 | source-systems-lineage     | data-pipeline.md         | source ingest, lineage anchoring, and close_book flow     |
| 17 | statements-lifecycle       | statements.md            | lifecycle states, finalization, and publish policy        |
| 18 | transaction-categories     | no design equivalent     | self-contained reference; consumed by design docs         |
| 19 | user-interface             | user-interface.md        | GS workbook page inventory, touchpoint map, CLI surface   |
| 20 | workflow-orchestration     | workflows.md             | stage routing, gate logic, state model, and checkpoints   |

### Reference topics

Reference topics define context, vocabulary, or scope boundaries. They do not require design equivalents.

| id | requirement topic       | rationale                                                     |
| -- | ----------------------- | ------------------------------------------------------------- |
| 01 | dependencies            | environment dependency register; no design translation needed |
| 02 | environment             | dev environment setup; no design translation needed           |
| 03 | glossary                | canonical vocabulary reference; consumed by all design docs   |
| 04 | implementation-roadmap  | release phasing reference; not a design behavior topic        |
| 05 | mvp                     | future scope reference; out of scope for this release         |
| 06 | poc                     | POC scope definition; consumed by design but not translated   |

---

## Design-only topics

These design docs have no direct requirement equivalent. They cover structural, architectural, or cross-cutting concerns introduced by the design phase.

| id | design doc             | purpose                                                                                  |
| -- | ---------------------- | ---------------------------------------------------------------------------------------- |
| 01 | architecture.md        | end-to-end system component model, layer boundaries, and runtime placement               |
| 02 | design-guidelines.md   | naming conventions, coding style, patterns, and documentation standards                  |
| 03 | tech-stack.md          | runtime profiles, dependency policy, component and workflow stack mapping                |
| 04 | repository-layout.md   | module structure and source tree organization                                            |
| 05 | data-flow.md           | per-stage data flow from external sources through backend to close_book and outputs      |
| 06 | topic-map.md           | this document                                                                            |

Supporting docs that exist in the design output path but are not primary design output:

| id | doc                                | purpose                                                          |
| -- | ---------------------------------- | ---------------------------------------------------------------- |
| 01 | category-account-model-translation.md | one-time translation of legacy category pipeline to new model |
| 02 | requirements-decisions.md          | resolved requirement decisions log                               |
| 03 | requirements-conflicts-and-gaps.md | requirement gap and conflict register                            |
| 04 | sdlc-ai-agents.md                  | AI agent workflow and SDLC integration notes                     |
| 05 | forex.md                           | forex translation design; supporting reference for statements.md |
| 06 | forecast.md                        | forecast design; supporting reference for statements.md          |

---

## Component coverage inventory

### Components with individual design coverage

These components are sufficiently complex or central to the close cycle that they require dedicated section coverage in their assigned design doc.

| id | component                    | design doc          | design topics covered                                 |
| -- | ---------------------------- | ------------------- | ----------------------------------------------------- |
| 01 | workflow orchestrator        | workflows.md        | stage routing, gate logic, state model, checkpoints   |
| 02 | account close runtime        | workflows.md        | per-account download, ingest, sync, and reconcile     |
| 03 | bill and shared-cost runtime | bill-payment.md     | bill intake, share allocation, HomeBudget posting     |
| 04 | reconciliation engine        | reconciliation.md   | match algorithm, tolerance rules, adjustment posting  |
| 05 | statement builder            | statements.md       | income statement and balance sheet aggregation        |
| 06 | backend API                  | all topic docs      | boundary in architecture.md; routes in topic docs     |
| 07 | SQLite app database          | data-model.md       | schema inventory; implements data-model.md entities   |
| 08 | Google Sheets session UI     | user-interface.md   | workbook structure, page inventory, touchpoint map    |
| 09 | HomeBudget wrapper adapter   | homebudget.md       | thin boundary over homebudget package; contract only  |

### Grouped components

These components are covered within the design doc of their parent or primary consumer. They do not require individual sections beyond what their covering doc provides.

| id | component             | covering design doc  | notes                                                       |
| -- | --------------------- | -------------------- | ----------------------------------------------------------- |
| 01 | source adapters       | data-pipeline.md     | bank CSV, IBKR CSV, PDF archive grouped under pipeline      |
| 02 | mapping CRUD service  | data-pipeline.md     | category mapping lifecycle is part of pipeline design       |
| 03 | SQLite adapter        | architecture.md      | backend-neutral sql boundary; boundary convention only      |
| 04 | Google Sheets adapter | google-sheets.md     | app sheet read and write boundary in Google Sheets design   |
| 05 | AWS storage adapter   | statements.md        | artifact publish and archive path in statements design      |
| 06 | logging service       | error-handling.md    | audit event and log policy alongside error handling         |
| 07 | error handling service| error-handling.md    | shared error policy and exception mapping                   |
| 08 | CLI                   | user-interface.md    | CLI surface and automation in user interface design         |
| 09 | GAS for Sheets UI     | user-interface.md    | optional click-event bridge; noted as optional extension    |

---
