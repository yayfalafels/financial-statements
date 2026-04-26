# Bill Payment and Shared Cost Workflow Design

## Table of contents

- [Overview](#overview)
- [Scope and targets](#scope-and-targets)
- [Detailed subprocess steps](#detailed-subprocess-steps)
- [Statement parser architecture](#statement-parser-architecture)
- [Shared allocation model](#shared-allocation-model)
- [Consumption tracking design](#consumption-tracking-design)
- [Integration with monthly close](#integration-with-monthly-close)
- [Error handling and review gates](#error-handling-and-review-gates)

## Overview

This document defines the bill payment subprocess used during monthly close. The design keeps existing accounting rules and reduces manual handling by automating parsing, allocation, posting preparation, and consumption logging.

## Scope and targets

- Current subprocess runtime is about 72 minutes.
- Target runtime is about 36 minutes through selective automation.
- Core accounts include bank and credit accounts used for recurring bills.
- Shared cost settlement account remains `30 CC Hashemis`.

## Detailed subprocess steps

### statement collection

- Input, downloaded statement files.
- Process, user authenticates and exports files.
- Output, raw files staged in period input directory.
- Automation level, manual by design.

### parser run

- Input, staged files and parser registry.
- Process, detect bank format and parse rows to canonical bill records.
- Output, canonical bill transactions with file lineage.
- Automation level, high.

### normalization and mapping

- Input, canonical bill records and payee mapping rules.
- Process, map payees to categories and posting account contracts.
- Output, normalized posting candidates.
- Automation level, high.

### shared cost allocation

- Input, normalized records and shared expense data from sheet.
- Process, split bill amount across parties using configured weights.
- Output, personal expense rows and settlement transfer rows.
- Automation level, high.

### posting package generation

- Input, mapped and allocated records.
- Process, build HomeBudget transaction package with dedupe keys.
- Output, reviewed posting package and summary preview.
- Automation level, high.

### consumption update

- Input, parsed utility metrics such as electricity, water, and gas usage.
- Process, write monthly metrics and variance from prior months.
- Output, consumption table records and optional alert flags.
- Automation level, high.

### verification and approval

- Input, posting preview and summary checks.
- Process, user confirms totals and exceptions.
- Output, approval state for posting step.
- Automation level, manual gate.

## Statement parser architecture

Parser pattern uses registry plus adapter classes.

```text
ParserRegistry
â†’ BankParser interface
  â†’ DbsParser
  â†’ UobParser
  â†’ CitiParser
  â†’ BoaParser
```

Required parser output fields:

- statement account id
- transaction date
- posting date when available
- signed amount and currency
- description and payee
- statement row key

Validation rules:

- Required fields present
- Date parse succeeds
- Amount parse succeeds
- Currency consistent with mapped account

## Shared allocation model

- Default allocation supports one third personal and two thirds flatmate share.
- Allocation is configurable by party count and weight percentages.
- Personal share posts as expense.
- Remaining share posts as transfer to `30 CC Hashemis`.

Generalized formula:

- personal share = total amount Ã— personal weight
- settlement share = total amount âˆ’ personal share

## Consumption tracking design

Primary storage uses SQLite table.

```sql
CREATE TABLE bill_consumption (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    period_id TEXT NOT NULL,
    payee TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value REAL NOT NULL,
    unit TEXT NOT NULL,
    amount REAL,
    currency TEXT,
    created_at TEXT NOT NULL,
    UNIQUE(period_id, payee, metric_name)
);
```

In scope metrics:

- electricity kWh
- water m3
- gas m3

## Integration with monthly close

- Runs after data acquisition and before final reconciliation close.
- Produced transactions feed account reconciliation in Group C.
- Produced consumption records feed review reporting only.
- Cadence is monthly with optional ad hoc reruns for corrections.

## Error handling and review gates

- Parser error, recoverable with file specific retry.
- Mapping error, recoverable after mapping update.
- Allocation error, recoverable after shared rule correction.
- Posting error, recoverable with retry after dedupe check.
- Verification failure, requires user review before posting.
