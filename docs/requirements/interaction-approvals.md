---
title: Interaction and Approvals
doc_type: requirements
topic_type: owner
owner: interaction-approvals
scope: poc
---
# Interaction and Approvals

## Table of contents

- [Purpose and boundary](#purpose-and-boundary)
- [Reference documents](#reference-documents)
- [Primary scope](#primary-scope)
- [Out of scope](#out-of-scope)
- [Review checkpoints by workflow stage](#review-checkpoints-by-workflow-stage)
- [Checkpoint criteria by workflow stage](#checkpoint-criteria-by-workflow-stage)
- [Required user confirmations before commit](#required-user-confirmations-before-commit)
- [Approval authority](#approval-authority)
- [Escalation boundary](#escalation-boundary)
- [Decision logging and readability requirements](#decision-logging-and-readability-requirements)
- [Rejection behavior](#rejection-behavior)

## Purpose and boundary

This document defines requirements for user interaction and approval behavior during the monthly close workflow.

## Reference documents

- [workflow orchestration](workflow-orchestration.md)
- [statements lifecycle](statements-lifecycle.md)
- [exception and error handling](exception-error-handling.md)

## Primary scope

- User review checkpoints
- User confirmations before commit actions
- Approval authority and escalation paths
- Rejection behavior
- Decision logging requirements

## Out of scope

- Workflow stage sequencing
- Statement revision and publication policy
- Low-level implementation UI controls

## Review checkpoints by workflow stage

| id | stage        | checkpoint focus                             |
| -- | ------------ | -------------------------------------------- |
| 01 | pre-flight   | source readiness and period selection        |
| 02 | forex        | exchange-rate source and period checks       |
| 03 | data ingest  | source files received and GS UI entries confirmed |
| 04 | data sync    | mapping sanity and `hb_gl_txn` plus dimension refresh status |
| 05 | reconcile    | variance review and close-blocking outcomes  |
| 06 | statements   | statement totals and classification review   |
| 07 | publish      | final artifact confirmation                  |

## Checkpoint criteria by workflow stage

- Each checkpoint must present required evidence for user review.
- Each checkpoint must clearly show pass or fail conditions.
- A failed checkpoint blocks downstream commit actions.

## Required user confirmations before commit

- Confirmation is required before posting to persistent stores.
- Confirmation is required before publish and period close.
- Confirmation records user identity and timestamp.

## Approval authority

- The monthly-close user is the approver for period-level commits.
- Delegated approvals require explicit delegation record.

## Escalation boundary

- Blocking variance or unresolved mapping triggers escalation.
- Escalation route and outcome are logged before resume.

## Decision logging and readability requirements

- Novel decisions require concise rationale log entries.
- Review outputs must be human-readable and traceable to source evidence.

## Rejection behavior

- Rejecting a checkpoint keeps the session in the current stage.
- Corrections must be applied before re-review.

