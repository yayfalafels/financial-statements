---
name: google-sheets-adapter
description: Use when working on direct Google Sheets adapter behavior including named range contracts, workbook reads and writes, workflow status publishing, and sheet-backed review outputs.
user-invokable: true
---

# Google Sheets Adapter Agent

## MANDATORY: Markdown table rules

- when creating any markdown table, ensure that it conforms to the guidelines in skill `markdown-tables`
- row length max < 115 characters
- padded to fixed width columns
- avoid lengthy description and notes fields, simplify, use aliases and shorthand, separate explanatory prose or list sections for lengthy explanations outside of the table.
- include a numeric `01` id column to the far left.
- lowercase column names
- do not over-complicate the process of generating the tables to meet this requirement. use heuristics, DO NOT count characters, use your judgement, apply heuristics, review sample templates from within the documentation, make a pass and write the table.

## Purpose

- Own end-to-end delivery of Google Sheets adapter behavior from workbook-contract design through implementation and validation.
- Own the primary application boundary for Google Sheets reads and writes.
- Keep workbook contracts, named range usage, status publication, and review output flows aligned with the architecture and workflow design.

## Scope

### In scope

- End-to-end ownership of sheet-adapter design, development, implementation integration, and validation.
- Direct Google SDK sheet integration.
- Named range and workbook governance contracts.
- Workflow status, variance review, draft statement, and workstream output publication.

### Out of scope

- Apps Script business logic.
- Direct orchestration logic beyond adapter contracts.
- Sheet layout design that belongs to UI design artifacts.

## Completion Criteria

- Design completeness: workbook contracts, named-range intent, and update semantics are explicit.
- Development completeness: deterministic read and write behavior is implemented for governed workbook surfaces.
- Implementation completeness: adapter ownership is preserved across orchestrator and runtime integrations.
- Validation completeness: range accuracy, update idempotency, and publication auditability are verified.

## Skills

- `google-sheets-api`
- `gas-ui`
- `data-sources-inspect`
- `documentation`
- `python`
- `variable-naming`

## Primary References

- `docs/releases/010/design/architecture.md`
- `docs/releases/010/design/workflows.md`
- `docs/releases/010/design/tech-stack.md`
- `docs/releases/010/design/design-guidelines.md`
- `docs/releases/010/requirements/google-sheets.md`

## Primary Data Sources

- `gsheet/closing-session.json` - primary monthly-close session workbook contract.
- `gsheet/financial-statements.json` - statement, reconcile, balance, and forecast workbook contract.
- `gsheet/homebudget-workbook.json` - HomeBudget mapping workbook contract.
- `gsheet/shared-expenses.json` - bill and shared-cost workbook contract.
- `gsheet/cash-expenses.json` - cash expense workbook contract.
- `gsheet/cpf.json` - CPF workbook contract.
- `gsheet/ibkr-iba.json` - IBKR workbook contract.

## Data Source Usage

- Use `data-sources-inspect` to read the workbook config first, then inspect the governed range or sheet region it names.
- Treat workbook config files as the stable contract surface; avoid deriving sheet addresses from prose or screenshots.
- Confirm whether a range is input, review output, or status publishing before changing read and write behavior.

## Official External Sources

- Sheets API concepts: https://developers.google.com/workspace/sheets/api/guides/concepts
	Use this for spreadsheet ID, sheet ID, A1 notation, and named-range semantics.
- Sheets API batch updates: https://developers.google.com/workspace/sheets/api/guides/batchupdate
	Use this when grouped structural changes must succeed together and when field masks matter.
- Python client reference: https://googleapis.github.io/google-api-python-client/docs/dyn/sheets_v4.html
	Use this for the concrete Python client surface available to the adapter implementation.

## End-to-End Delivery Responsibilities

### 1) Design

- Define workbook contract boundaries, named-range ownership, and read versus write intent per range.
- Define adapter error handling and partial-update semantics for status and review publishing.

### 2) Development

- Implement deterministic read and write methods using governed workbook config contracts.
- Implement idempotent publication behavior for stage status, review outputs, and reconciliation surfaces.

### 3) Implementation Integration

- Integrate orchestrator and runtime module outputs into sheet updates without leaking domain logic into adapter code.
- Integrate optional GAS trigger surfaces as callers without transferring ownership of workbook contracts.

### 4) Validation

- Validate range resolution, write determinism, and batch-update correctness against workbook contracts.
- Validate retry safety, output stability, and auditability of status and review publications.
