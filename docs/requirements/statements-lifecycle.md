# Statements Lifecycle

## Table of contents

- [Purpose and boundary](#purpose-and-boundary)
- [Reference documents](#reference-documents)
- [Primary scope](#primary-scope)
- [Out of scope](#out-of-scope)
- [Lifecycle phase behavior](#lifecycle-phase-behavior)
- [Lifecycle state model by period](#lifecycle-state-model-by-period)
- [Finalization criteria](#finalization-criteria)
- [Reopen policy](#reopen-policy)
- [Revision policy](#revision-policy)
- [Publish output rules](#publish-output-rules)
- [Versioning and lineage linkage](#versioning-and-lineage-linkage)
- [Period snapshot and immutability rules](#period-snapshot-and-immutability-rules)

## Purpose and boundary

This page is the normative owner for statement lifecycle policy by period.

## Reference documents

- [workflow orchestration](workflow-orchestration.md)
- [interaction and approvals](interaction-approvals.md)
- [source systems and lineage](source-systems-lineage.md)

## Primary scope

- Statement lifecycle states and transitions
- Finalization, reopen, and revision policy
- Publish outputs and snapshot rules
- Versioning and lineage linkage

## Out of scope

- Workflow orchestration stage sequencing
- User approval checkpoint policy
- Reconciliation algorithm details

## Lifecycle phase behavior

- Statements are created from reconciled and mapped period data.
- Statements are reviewed before finalization.
- Finalized statements are published as period artifacts.

## Lifecycle state model by period

| id | state      | meaning                                   | next states |
| -- | ---------- | ----------------------------------------- | ----------- |
| 01 | draft      | statement outputs generated for review    | reviewed    |
| 02 | reviewed   | checkpoint review complete                | finalized   |
| 03 | finalized  | period statement locked for publication   | reopened    |
| 04 | reopened   | controlled revision state after final     | finalized   |

## Finalization criteria

- Reconcile and mapping gates pass for the period.
- Required reviews are complete.
- Publish artifacts are generated and validated.

## Reopen policy

- Reopen is allowed only with documented reason.
- Reopen action must be traceable to operator and timestamp.

## Revision policy

- Revisions are versioned and lineage-linked.
- Revision rationale must be recorded before finalization.

## Publish output rules

- Publish must include income statement and balance sheet outputs.
- Publish must include lineage metadata for source traceability.

## Versioning and lineage linkage

- Each period publish event has a unique version identifier.
- Each statement output links to source lineage references.

## Period snapshot and immutability rules

- Finalized period snapshot is immutable unless reopened.
- Reopened period creates a new finalized version on close.

