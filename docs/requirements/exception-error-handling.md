---
title: Exception and Error Handling
doc_type: requirements
topic_type: owner
owner: exception-error-handling
scope: poc
---
# Exception and Error Handling

## Table of contents

- [Purpose and boundary](#purpose-and-boundary)
- [Reference documents](#reference-documents)
- [Primary scope](#primary-scope)
- [Out of scope](#out-of-scope)
- [Exception categories](#exception-categories)
- [General exception policy](#general-exception-policy)
- [Validation errors](#validation-errors)
- [Missing category mapping](#missing-category-mapping)
- [Source validation failure](#source-validation-failure)
- [Reconciliation variance escalation](#reconciliation-variance-escalation)
- [Close-blocking conditions](#close-blocking-conditions)
- [Auditability requirements](#auditability-requirements)
- [Non-functional requirements](#non-functional-requirements)

## Purpose and boundary

This document defines the requirement-level policy for validation errors, missing mappings, unresolved exceptions, and source failures that occur during the monthly close workflow.

## Reference documents

- [workflow orchestration](workflow-orchestration.md)
- [interaction and approvals](interaction-approvals.md)
- [transaction categories](transaction-categories.md)
- [reconciliation engine](reconciliation-engine.md)
- [source systems and lineage](source-systems-lineage.md)

## Primary scope

- Validation error policy and user-visible handling behavior
- Missing category mapping detection and escalation
- Source validation failure handling during ingest and sync
- Reconciliation variance escalation policy
- Close-blocking conditions and required resolution paths
- Auditability requirements for exception events and remediation decisions

## Out of scope

- Specific reconciliation tolerance thresholds - owned by reconciliation engine
- Approval authority and confirmation UX detail - owned by interaction and approvals
- Workflow stage sequencing - owned by workflow orchestration
- Statement revision and publication policy - owned by statements lifecycle

## Exception categories

| id    | category                  | trigger                                                   | close-blocking |
| ----- | ------------------------- | --------------------------------------------------------- | -------------- |
| EE-01 | pre-flight validation     | required input absent, format invalid, period not set     | yes            |
| EE-02 | forex validation          | rate source unavailable or rate outside expected range    | yes            |
| EE-03 | missing category mapping  | transaction has no mapping for current or prior year      | yes            |
| EE-04 | source validation failure | source file schema mismatch or source data ingest failure | yes            |
| EE-05 | reconciliation variance   | variance exceeds tolerance threshold                      | yes            |
| EE-06 | publish pre-check failure | artifact output check fails at publish stage              | yes            |

## General exception policy

- All exceptions must be surfaced to the user with a clear description of the condition, the affected scope, and the required resolution action.
- Close cannot proceed while any close-blocking exception remains unresolved.
- Resolved exceptions must be recorded with the resolution method, the user identity, and a timestamp before the workflow can resume.
- The system must not silently suppress or discard exception events.
- Where multiple exceptions exist simultaneously, all blocking exceptions must be displayed together rather than sequentially one at a time.

## Validation errors

Validation errors occur during pre-flight and data sync stages when required inputs are absent or do not conform to expected schema.

- The system must check for required inputs at stage entry and reject the stage if required inputs are missing.
- Input validation must report all missing or invalid fields together, not just the first failure encountered.
- A validation error must include the affected source, the expected condition, and the observed condition.
- Validation errors block downstream stage execution until resolved.
- The user must correct the source condition before re-entry to the stage.

## Missing category mapping

A missing category mapping occurs when a transaction present in the period ledger cannot be matched to a category classification entry in the category data model.

- The system must detect unmapped transactions before the reconcile stage begins.
- If any transaction for the current period is missing a required mapping, close is blocked until the mapping is resolved.
- If the missing mapping corresponds to a HomeBudget category that exists in a prior-year transaction but has no current mapping entry, the condition is escalated to the user to resolve.
- The user must add the missing mapping entry via the category data model CRUD interface, or explicitly reclassify the transaction category in HomeBudget, before close can proceed.
- The system must display the affected transaction identifiers, the unmapped category label, and the period scope when presenting a missing-mapping exception.
- After the user resolves the mapping, the system must re-evaluate mapping completeness before permitting close.
- Resolution and the user decision are recorded before workflow resume.

Category data model integrity requirements:

- The category data model must not contain duplicate active keys. If a duplicate active key is detected, the system must surface it as a validation error before close can proceed.
- Active category records must not have null `gl_code`. A null required field is treated as a missing mapping and triggers the same blocking and escalation behavior.

## Source validation failure

A source validation failure occurs when an ingested source file does not match the expected schema, or when a source system returns an error or incomplete dataset during sync.

- The system must detect schema mismatches and source errors at the data ingest and data sync stages.
- A source validation failure blocks all downstream processing for the affected account group until the condition is resolved.
- The exception must identify the affected source system, the expected schema or record count, and the observed condition.
- Close remains open and escalated to the user to resolve.
- The user must correct the source - for example by re-downloading the file, re-entering the data, or confirming the source is unavailable for the period - before the affected stage can be retried.
- A source marked unavailable for the period by explicit user decision must be recorded with a user rationale before processing continues.
- Resolution and the user decision are recorded before workflow resume.

## Reconciliation variance escalation

Reconciliation variance escalation is defined as a close-blocking exception when variance exceeds the account-group tolerance threshold.

- Variance that exceeds the tolerance threshold triggers a blocking exception and prevents period close.
- The user must review the variance, then either approve an adjustment, modify the adjustment, or investigate and correct the source before close can proceed.
- The user approval, timestamp, and any correction rationale are recorded as part of the reconciliation exception event.
- Tolerance thresholds are defined in reconciliation engine requirements and are not redefined here.

## Close-blocking conditions

The following conditions each independently block period close:

- Any unresolved pre-flight validation error
- Any unresolved forex validation error
- Any transaction with a missing required category mapping at close time
- Any source validation failure that has not been explicitly resolved or accepted by the user
- Any reconciliation variance that exceeds the account-group tolerance threshold and has not received user approval
- Any publish pre-check failure

The user must resolve or explicitly accept each close-blocking exception before close can proceed. Explicit acceptance of an unresolvable exception must be recorded with a rationale.

## Auditability requirements

- Every exception event must be recorded with the exception category, affected scope, timestamp of detection, and current status.
- Every user resolution action must be recorded with the user identity, the resolution method, and a timestamp.
- Exception event records must be retained for the closed period and must be accessible at a later point.
- Exception event records must be stored in S3 
- Exception records must not be deleted or modified after the user resolution action is recorded.

## Non-functional requirements

- Exception messages must be human-readable and must not require technical interpretation to determine the required user action.
- Batch exception reporting - where all active blocking exceptions are shown together - is required for the reconcile and close stages.
- The exception state must be recoverable; the user must be able to reenter a blocked stage after resolving the condition without losing prior work.
