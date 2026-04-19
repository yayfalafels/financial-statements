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
- [Escalation and rework boundary](#escalation-and-rework-boundary)
- [Decision logging and readability requirements](#decision-logging-and-readability-requirements)
- [Rejection and rework behavior](#rejection-and-rework-behavior)

## Purpose and boundary

This page is the normative owner for user interaction and approval behavior.

## Reference documents

- [workflow orchestration](workflow-orchestration.md)
- [statements lifecycle](statements-lifecycle.md)
- [exception and error handling](exception-error-handling.md)

## Primary scope

- User review checkpoints
- User confirmations before commit actions
- Approval authority and escalation paths
- Rejection and rework behavior
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
| 03 | data sync    | statement ingestion and mapping sanity       |
| 04 | reconcile    | variance review and close-blocking outcomes  |
| 05 | statements   | statement totals and classification review   |
| 06 | publish      | final artifact confirmation                  |

## Checkpoint criteria by workflow stage

- Each checkpoint must present required evidence for operator review.
- Each checkpoint must clearly show pass or fail conditions.
- A failed checkpoint blocks downstream commit actions.

## Required user confirmations before commit

- Confirmation is required before posting to persistent stores.
- Confirmation is required before publish and period close.
- Confirmation records operator identity and timestamp.

## Approval authority

- The monthly-close operator is the approver for period-level commits.
- Delegated approvals require explicit delegation record.

## Escalation and rework boundary

- Blocking variance or unresolved mapping triggers escalation.
- Escalation route and rework outcome are logged before resume.

## Decision logging and readability requirements

- Novel decisions require concise rationale log entries.
- Review outputs must be human-readable and traceable to source evidence.

## Rejection and rework behavior

- Rejecting a checkpoint keeps the current stage open.
- Rework actions must be applied before re-review.

