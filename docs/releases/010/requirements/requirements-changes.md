---
title: Requirements Changes
doc_type: requirements
topic_type: changelog
owner: product-manager
scope: poc
last_updated: 2026-05-03
status: draft
---
# Requirements Changes

## Summary

This log records approved requirement changes for release 010 requirements documents.

## Table of contents

- [Summary](#summary)
- [Change summary table](#change-summary-table)
- [Change details](#change-details)

## Change summary table

| id | date       | change                                | status   | impacted_docs  |
| -- | ---------- | ------------------------------------- | -------- | -------------- |
| 01 | 2026-05-03 | semantic + transfer-expense pairing | approved | re, ia, hb, wo |

Doc key:

- `re`: `reconciliation-engine.md`
- `ia`: `interaction-approvals.md`
- `hb`: `homebudget.md`
- `wo`: `workflow-orchestration.md`

## Change details

### Change 01: semantic + transfer-expense pairing

Change scope:

- Add semantic matching layer requirements to transaction-level reconciliation.
- Add transfer-expense pairing requirements for `TWH - Personal` zero-sum behavior.
- Require user review and approval for pairing proposals and staged expense CRUD actions before commit.
- Add reconcile checkpoint and stage-exit coverage for pairing decisions.

Updated requirement locations:

- `reconciliation-engine.md`
  - Add `Semantic matching layer` requirements.
  - Add `Transfer-expense pairing` requirements.
  - Update shared workflow phase 6 review and approval behavior.
  - Update reconcile workflow checkpoint table.
- `interaction-approvals.md`
  - Update reconcile checkpoint focus and pass criteria.
  - Add `Reconcile-stage required approvals` section for pairing and CRUD review.
- `homebudget.md`
  - Add transfer-expense pairing and staged expense CRUD requirements in posting patterns.
  - Add write-back use case for transfer-expense paired updates.
- `workflow-orchestration.md`
  - Update reconcile account-level exit criteria for pairing resolution.
  - Update reconcile stage outputs to include pairing decisions and staged expense CRUD records.

Acceptance impact:

- Reconcile cannot close with unresolved blocking pairing findings.
- Pairing and staged expense CRUD decisions become required reconcile artifacts.
- User approval path now includes semantic and transfer-expense pairing review for transaction-level flows.
