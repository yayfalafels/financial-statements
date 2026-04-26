---
title: Statements Lifecycle
doc_type: requirements
topic_type: owner
owner: statements-lifecycle
scope: poc
---
# Statements Lifecycle

## Table of contents

- [Purpose and boundary](#purpose-and-boundary)
- [Reference documents](#reference-documents)
- [Primary scope](#primary-scope)
- [Out of scope](#out-of-scope)
- [Lifecycle phase behavior](#lifecycle-phase-behavior)
- [Draft and review behavior](#draft-and-review-behavior)
- [Lifecycle state model by period](#lifecycle-state-model-by-period)
- [Finalization criteria](#finalization-criteria)
- [Reopen policy](#reopen-policy)
- [Revision policy](#revision-policy)
- [Publish output rules](#publish-output-rules)
- [Artifact output requirements](#artifact-output-requirements)
- [Versioning and lineage linkage](#versioning-and-lineage-linkage)
- [Period snapshot and immutability rules](#period-snapshot-and-immutability-rules)

## Purpose and boundary

This document defines statement lifecycle policy by close period.

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

## Draft and review behavior

- The statements stage produces draft income statement and balance sheet outputs from reconciled period data.
- Draft outputs are presented to the user for review before finalization.
- Review covers statement totals, account classification, and alignment with reconcile gate outcomes.
- A draft statement must not be finalized or published without completed user review.
- If review identifies errors or unresolved items, the session remains in the reconcile stage until corrections are applied.

## Lifecycle state model by period

| id          |           |                                         |           |
| ----------- | --------- | --------------------------------------- | --------- |
| state       |           |                                         |           |
| meaning     |           |                                         |           |
| next states |           |                                         |           |
| 01          | draft     | statement outputs generated for review  | reviewed  |
| 02          | reviewed  | checkpoint review complete              | finalized |
| 03          | finalized | period statement locked for publication | reopened  |
| 04          | reopened  | controlled revision state after final   | finalized |

## Finalization criteria

- Reconcile and mapping gates pass for the period.
- Required reviews are complete.
- Publish artifacts are generated and validated.

## Reopen policy

- Reopen is allowed 
- Reopen action must be traceable to user and timestamp.

## Revision policy

- Revisions are versioned and lineage-linked.
- Revision rationale must be recorded before finalization.

## Publish output rules

- Publish must include income statement and balance sheet outputs.
- Publish must include lineage metadata for source traceability.

## Artifact output requirements

- Each publish event produces a PDF for the income statement and a PDF for the balance sheet.
- Published PDFs are uploaded to S3 and stored with a path that includes the period year and month.
- Lineage metadata linking the published artifacts to their source period inputs is required for every publish event.
- Publish must produce a session close record capturing the period, user identity, timestamp, and artifact storage locations.

## Versioning and lineage linkage

- Each period publish event has a unique version identifier.
- Each statement output links to source lineage references.

## Period snapshot and immutability rules

- Finalized period snapshot is immutable unless reopened.
- Reopened period creates a new finalized version on close.

