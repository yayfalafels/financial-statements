# Workflow Architecture Design

## Table of contents

- [Overview](#overview)
- [Workflow lifecycle](#workflow-lifecycle)
- [Step groups and checkpoint gates](#step-groups-and-checkpoint-gates)
- [Parallel and sequential execution rules](#parallel-and-sequential-execution-rules)
- [Session persistence and resume model](#session-persistence-and-resume-model)
- [Idempotency model](#idempotency-model)
- [Failure and recovery model](#failure-and-recovery-model)
- [Operational timeline and bottlenecks](#operational-timeline-and-bottlenecks)

## Overview

This document defines workflow orchestration for monthly close with checkpoint gates and resumable execution. The workflow supports both CLI step commands and guided web execution through one shared runner.

The step groups align with timing and manual boundaries in `docs/current-workflow.md` and `docs/mvp-design.md`, where statement download and review remain manual while ingestion and calculations are automated.

## Workflow lifecycle

- Start condition, user starts close for period `YYYY-MM`.
- End condition, period snapshot is finalized and archived.
- In progress state, step statuses and messages are persisted in SQLite.
- Failure state, failed step blocks dependent steps until resolved.

## Step groups and checkpoint gates

### Group A, data acquisition

- A1 fetch forex rates
- A2 query HomeBudget balances and transactions
- A3 collect statement files and current balances
- A4 collect investment and retirement inputs
- A5 load user period inputs

Checkpoint A criteria:

- Required sources loaded
- Source timestamps logged
- Mandatory account mappings resolved

### Group B, ingestion and normalization

- B1 parse statement files into canonical rows
- B2 import statement rows into digital twin tables
- B3 run pre verification against observed balances
- B4 user review for parser flags and unmatched accounts

Checkpoint B criteria:

- Ingestion completeness is confirmed
- Pre verification passes for required accounts
- Unresolved parser errors are cleared or waived

### Group C, reconciliation and posting

- C1 compute expected closing balances
- C2 run transaction level reconciliation
- C3 generate proposed edits and variance statuses
- C4 user review and decision capture for exceptions
- C5 post approved reconciliation transactions to HomeBudget

Checkpoint C criteria:

- Residual variances are within policy or documented
- Required approvals are captured
- Posting outcome is logged with success status

### Group D, statement generation

- D1 build trial balance
- D2 apply consolidation and conversion rules
- D3 generate annual ledger outputs for current year
- D4 generate income statement and balance sheet
- D5 publish review summary output

Checkpoint D criteria:

- Statement equations are internally consistent
- Required outputs are generated
- User review status is approved

### Group E, closure and archival

- E1 persist period snapshot in SQLite
- E2 write period JSON sidecar outputs
- E3 upload backup and reports to S3 when configured
- E4 close period status and archive session logs

Checkpoint E criteria:

- Persistence writes are complete
- Archive outcome is confirmed
- Period status is moved to `closed`

## Parallel and sequential execution rules

- Group A steps can run in parallel where sources are independent.
- Group B starts only after Checkpoint A passes.
- Group C starts only after Checkpoint B passes.
- Group D starts only after Checkpoint C passes.
- Group E starts only after Checkpoint D passes.

Critical path is statement ingestion and reconciliation review.

## Session persistence and resume model

Session state includes:

- Current period id
- Current step id and status
- Completed steps with timestamps
- Failed step details and recovery hints
- User decisions for checkpoint overrides

Resume rules:

- Resume at first non completed step in dependency order.
- Re run current step if prior output hash changed.
- Disallow resume if period status is `closed`.

## Idempotency model

- Acquisition steps are safe to re run and overwrite staging outputs.
- Ingestion uses dedupe keys to avoid duplicate inserts.
- Posting steps require pre post checks and write guards.
- Finalization writes use upsert contracts by period and report name.

## Failure and recovery model

### Data failures

- Missing or malformed source data blocks progression.
- Recovery path, fix source and re run failed step.

### Validation failures

- Schema or mapping validation failures block progression.
- Recovery path, update mappings then re run validation.

### Reconciliation failures

- Over tolerance variance requires user review decision.
- Recovery path, apply edits or approve waiver with explanation.

### External service failures

- API or network failures are retried with backoff.
- Recovery path, retry then continue from failed step.

## Operational timeline and bottlenecks

- Largest manual time segments are statement download and review.
- Largest automated runtime segment is parser and reconciliation matching.
- Main optimization levers are parser coverage and decision reuse.
- Baseline step durations should be tracked against the ranges listed in `docs/current-workflow.md`.
