# Requirements

## Table of contents

- [Summary](#summary)
- [POC overview](#poc-overview)
- [POC scope](#poc-scope)
- [Requirements outline](#requirements-outline)
- [Requirement topics](#requirement-topics)
- [Cross-page ownership rules](#cross-page-ownership-rules)

## Summary

This page introduces the POC requirement intent, defines the active scope, and points to the separate topic pages that contain the detailed requirement statements.

## POC overview

Release `0.1.0` POC is a local monthly-close workflow for one user.

The POC requirements focus on the following outcomes:

- Retain Google Sheets as the primary session UI for monthly close.
- Retain HomeBudget as the primary real-time accounting UI and data source.
- Retain manual bank statement download and CSV-based IBKR import with manual review checkpoints.
- Retain the existing Google Sheets and form-based workflows for forecasting and cash input.
- Add local sqlite persistence for app-owned workflow state and outputs.
- Add a parallel CLI surface for scripting and automation.
- Add app-owned backend services, including CRUD support for mappings managed through a category data model and custom Google Sheets UI.
- Define schema ownership for statement staging, HomeBudget sync, mapping, and final statement-ready aggregation state.
- Define complete requirement coverage for workflow, interaction, source lineage, accounting, reconciliation, statements lifecycle, and integrations.

## POC scope

The active requirements scope is constrained to release `0.1.0` POC intent.

In scope:

- Local-only operation.
- One user.
- Session-based updates.
- Google Sheets as the primary session UI.
- HomeBudget integration for live accounting workflows.
- Local sqlite persistence.
- Category and account mapping through the category data model, custom Google Sheets UI, and backend CRUD operations.
- Manual bank statement download and CSV-based IBKR import.
- Financial close outputs across statement preparation and reconciliation.
- Bill payment and shared-cost settlement requirements.

Out of scope:

- MVP and later-phase capability expansion.
- Data migration design and implementation.
- Cloud deployment and multi-user operations.

## Requirements outline

The current outline covers the following topic groups:

- Workflow and user control, including workflow orchestration, review checkpoints, approvals, and statement lifecycle behavior.
- Accounting and close logic, including accounting policy, account classification, category mapping, and reconciliation behavior.
- Source systems and integration surfaces, including lineage and the retained operational systems and inputs used during monthly close.
- Supporting close workflows, including bill payment and shared-cost settlement.
- Reference context, including glossary terms, roadmap alignment, and current-state workflow context.

For the current detailed topic list, use the topic index table below.

## Requirement topics

The topic pages for detailed requirement are included below.

| id       |                           |           |
| -------- | ------------------------- | --------- |
| document |                           |           |
| role     |                           |           |
| 01       | workflow-orchestration.md | owner     |
| 02       | interaction-approvals.md  | owner     |
| 03       | statements-lifecycle.md   | owner     |
| 04       | source-systems-lineage.md | owner     |
| 05       | accounting-logic.md       | owner     |
| 06       | account-classification.md | owner     |
| 07       | transaction-categories.md | owner     |
| 08       | financial-statements.md   | owner     |
| 09       | reconciliation-engine.md  | owner     |
| 10       | bill-payment.md           | owner     |
| 11       | shared-costs.md           | owner     |
| 12       | homebudget.md             | owner     |
| 13       | google-sheets.md          | owner     |
| 14       | ibkr-integration.md       | owner     |
| 15       | cpf-integration.md        | owner     |
| 16       | data-model.md             | owner     |
| 17       | cash-reconcile.md         | reference |
| 18       | glossary.md               | reference |
| 19       | implementation-roadmap.md | reference |
| 20       | poc.md                    | reference |
| 21       | mvp.md                    | reference |
| 22       | dependencies.md           | reference |
| 23       | environment.md            | reference |
| 24       | user-interface.md         | owner     |

## Cross-page ownership rules

- Integration pages inherit global accounting policy from docs/requirements/accounting-logic.md.
- Shared-cost settlement is derived from bill-payment data and the lifecycle linkage rule is owned by docs/requirements/shared-costs.md.
- Tolerance policy values are owned by docs/requirements/reconciliation-engine.md.
- Canonical account naming is owned by the financial statements gsheet accounts region and mapped from source-system names.
- Data-model schema ownership and canonical schema naming are owned by docs/requirements/data-model.md.

