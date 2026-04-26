# Error Handling and Validation Design

## Table of contents

- [Overview](#overview)
- [Error taxonomy](#error-taxonomy)
- [Severity model](#severity-model)
- [Recovery patterns](#recovery-patterns)
- [Validation rule catalog](#validation-rule-catalog)
- [Batch validation strategy](#batch-validation-strategy)
- [Partial success handling](#partial-success-handling)
- [Audit trail requirements](#audit-trail-requirements)
- [User messaging model](#user-messaging-model)

## Overview

This document defines a unified error and validation strategy for all workflow steps. The goal is predictable failure behavior, actionable user feedback, and complete auditability of decisions.

## Error taxonomy

### DataQualityError

- Trigger, malformed input rows, missing required fields, invalid type conversion.
- Typical source, parser and normalization stage.

### DataFreshnessError

- Trigger, source data stale beyond accepted period window.
- Typical source, delayed statement exports and outdated forex rates.

### ImportConflictError

- Trigger, duplicate row keys or conflicting updates during ingestion.
- Typical source, repeated imports without stable dedupe handling.

### ReconciliationError

- Trigger, unresolved variance above tolerance.
- Typical source, matching and variance resolution stage.

### PostingError

- Trigger, failed write to HomeBudget or app database.
- Typical source, posting and finalization stages.

### ExternalApiError

- Trigger, rate limit, timeout, auth failure.
- Typical source, Sheets, forex, and S3 adapters.

### ConfigError

- Trigger, missing required setting or invalid config value.
- Typical source, startup and step initialization.

### LogicError

- Trigger, domain invariant violation.
- Typical source, calculation and reconciliation algorithms.

## Severity model

- Fatal, workflow cannot proceed at current checkpoint.
- Recoverable, step can retry or continue with explicit user decision.
- Warning, workflow can continue and issue is logged for review.

Suggested defaults:

- Fatal, ConfigError, LogicError, mandatory DataQualityError.
- Recoverable, ExternalApiError, PostingError, ReconciliationError.
- Warning, DataFreshnessError in non critical feeds.

## Recovery patterns

- Retry with backoff for external transient failures.
- Step rerun after source correction for quality failures.
- User review gate for tolerance breaches and waivers.
- Transaction rollback and replay for posting failures.
- Resume from last completed checkpoint after recovery.

## Validation rule catalog

### Amount validation

- Currency specific precision and rounding.
- Allowed ranges by account behavior.

### Date validation

- Date is in period unless explicitly pending policy applies.
- Date is not in future for finalized events.

### Account validation

- Account exists in mapping and source system where required.
- Account type specific booking rules are enforced.

### Category validation

- Category and subcategory are valid for account use case.
- Shared allocation categories are mapped before posting.

### Period validation

- Exactly one active close session per period.
- Closed periods are immutable.

### Currency and rate validation

- Supported currency pair exists.
- Required monthly rate exists or is explicitly waived.

## Batch validation strategy

- Collect all validation issues for a stage before fail decision.
- Return grouped issue lists by severity and source.
- Surface blocking items first and warnings second.

## Partial success handling

- Track per record status during posting.
- Commit successful records in one transaction only when allowed.
- On mixed outcomes, record successful writes and produce replay file for failed rows.
- Require user approval before replay when financial impact exists.

## Audit trail requirements

Every error event should capture:

- Period id and step id
- Error type and severity
- Source system and file when available
- Structured context payload
- User decision if override or waiver is used
- Timestamp and actor id

## User messaging model

- Keep messages plain and action oriented.
- Include why it failed, what is blocked, and next action.
- Include rerun command hint for CLI mode.
- Include affected account or source in first line of error text.
