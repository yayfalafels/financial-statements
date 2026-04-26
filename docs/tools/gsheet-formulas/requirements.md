# Gsheet Formulas Requirements

## Summary

- Defines requirement-level behavior for formula CRUD in Google Sheets.
- Captures input contract, functional and non-functional requirements, and error handling.
- Establishes measurable acceptance criteria and SIT/UAT traceability.

## References

- `docs/develop/010/project-management/gsheet-formulas.md`
- `.github/prompts/gsheet-formulas.prompt.md`
- `docs/requirements/google-sheets.md`

## Table of Contents

- [Document Control](#document-control)
- [Purpose](#purpose)
- [In Scope](#in-scope)
- [Out of Scope](#out-of-scope)
- [Required Inputs](#required-inputs)
- [Functional Requirements](#functional-requirements)
- [Formula Read](#formula-read)
- [Formula Create](#formula-create)
- [Formula Update](#formula-update)
- [Formula Clear](#formula-clear)
- [Range and Conflict Policy](#range-and-conflict-policy)
- [Audit and Output](#audit-and-output)
- [Non-Functional Requirements](#non-functional-requirements)
- [Error Handling Requirements](#error-handling-requirements)
- [Acceptance Criteria](#acceptance-criteria)
- [SIT Traceability](#sit-traceability)
- [UAT Traceability](#uat-traceability)
- [Batch Enhancement 02141809](#batch-enhancement-02141809)
- [Decisions Captured From User Input](#decisions-captured-from-user-input)

## Document Control

- task id: 02.14.18.01
- release: 010
- utility: gsheet-formulas
- status: draft

## Purpose

Define requirement-level behavior for a Python utility that performs formula CRUD operations in Google Sheets using Google Sheets API.

## In Scope

- Read formula from a single cell.
- Create formula in a single cell.
- Update formula in a single cell.
- Clear formula content from a single cell.
- Input validation for client secret path, workbook id, and A1 cell range.
- Structured mutation audit output and console summary.

## Out of Scope

- OAuth user-flow authentication.
- Multi-cell write or update behavior.
- Non-formula spreadsheet operations outside the formula CRUD workflow.

## Required Inputs

| id    |                    |                          |
| ----- | ------------------ | ------------------------ |
| input |                    |                          |
| rule  |                    |                          |
| IN-01 | client secret path | required, readable JSON  |
| IN-02 | workbook id        | required, non-empty      |
| IN-03 | cell range         | required, single-cell A1 |

Input rule notes:

- IN-01 must reference an existing readable JSON credential file.
- IN-03 single-cell examples include `A34` and `Sheet1!B7`.

## Functional Requirements

### Formula Read

- FR-01: The tool must retrieve the raw formula token for the target single cell.
- FR-02: If the cell has no formula, the tool must return a deterministic empty-formula response state.

### Formula Create

- FR-03: The tool must write a formula to a single target cell when the target does not already contain a formula.
- FR-04: When formula create succeeds, the tool must return operation status and target location.

### Formula Update

- FR-05: The tool must overwrite an existing formula by default when update is requested.
- FR-06: Update must be deterministic: final cell formula equals requested formula after success response.

### Formula Clear

- FR-07: Clear operation must remove both formula and resulting value so the target cell becomes empty.
- FR-08: Clear operation must return success only after the target cell is empty.

### Range and Conflict Policy

- FR-09: Multi-cell ranges are not allowed for create or update; the tool must return a validation error.
- FR-10: If a create operation targets a cell that already has a formula, tool behavior is overwrite by default.

### Audit and Output

- FR-11: For each mutation, create update or clear, the tool must emit a structured JSON audit record.
- FR-12: For each operation, the tool must emit a concise console summary.
- FR-13: Audit records must include operation type, workbook id, cell range, timestamp, and result status.

## Non-Functional Requirements

- NFR-01: Input validation must complete before any API write call is made.
- NFR-02: Error messages must distinguish validation failures from API/runtime failures.
- NFR-03: Operation output format must be stable across runs for automation and evidence capture.
- NFR-04: The utility must use service-account credential flow only in this release scope.
- NFR-05: Mutation operations must be auditable through JSON records and console summaries.

## Error Handling Requirements

- ER-01: Missing or unreadable client secret file must return a blocking validation error.
- ER-02: Missing workbook id must return a blocking validation error.
- ER-03: Non-single-cell A1 range must return a blocking validation error.
- ER-04: API permission/auth failures must return non-validation runtime errors with actionable message.
- ER-05: Network/API failures must return failure status and preserve audit evidence of failure.

## Acceptance Criteria

| id          |                   |                      |
| ----------- | ----------------- | -------------------- |
| scenario    |                   |                      |
| pass signal |                   |                      |
| AC-01       | read with formula | formula returned     |
| AC-02       | read no formula   | empty state returned |
| AC-03       | create on empty   | formula persisted    |
| AC-04       | update formula    | new formula returned |
| AC-05       | clear formula     | target cell empty    |
| AC-06       | bad secret path   | validation error     |
| AC-07       | missing workbook  | validation error     |
| AC-08       | bad write range   | validation error     |
| AC-09       | mutation audit    | JSON record present  |
| AC-10       | API failure       | runtime error logged |

Acceptance criteria detail:

- AC-01 returns formula text with success status for target cell.
- AC-02 returns deterministic empty-formula state with success status.
- AC-03 writes formula and follow-up read returns exact formula.
- AC-04 overwrites by default and follow-up read returns new formula.
- AC-05 clears formula and value so the target cell is empty.
- AC-06 fails before API call when client secret path is invalid.
- AC-07 fails before API call when workbook id is missing.
- AC-08 fails with no mutation for invalid or multi-cell write range.
- AC-09 writes JSON audit with required fields and status.
- AC-10 returns runtime error and writes failure audit record.

## SIT Traceability

- SIT-01 maps to AC-01 and AC-02.
- SIT-02 maps to AC-03 and AC-04.
- SIT-03 maps to AC-05.
- SIT-04 maps to AC-06, AC-07, and AC-08.
- SIT-05 maps to AC-09 and AC-10.

## UAT Traceability

- UAT-01 user reads formula and confirms displayed result matches sheet cell.
- UAT-02 user creates and updates formula in one cell and confirms workbook outcome.
- UAT-03 user clears formula and confirms cell is empty.
- UAT-04 user reviews JSON audit and console summary for one successful and one failed mutation.

## Batch Enhancement 02141809

Batch enhancement scope extends the utility with multi-range formula operations while preserving
single-cell command behavior.

Batch functional requirements:

- BFR-01: batch read must retrieve formula tokens for multiple A1 ranges in one request.
- BFR-02: batch create must write formulas for multiple ranges in one request.
- BFR-03: batch update must overwrite formulas for multiple ranges in one request.
- BFR-04: batch clear must clear formulas and values for multiple ranges in one request.
- BFR-05: batch create and update must verify results with follow-up batch read.
- BFR-06: batch mutation commands must support JSON audit output.

Batch input contract:

- BIN-01: batch read and clear accept `ranges` as comma-separated single-cell A1 values.
- BIN-02: batch create and update accept a JSON file list with `range` and `formula` keys.
- BIN-03: every batch formula must start with `=`.

Batch acceptance criteria:

- BAC-01: batch read returns success with formula map for all requested ranges.
- BAC-02: batch create writes formulas and read-after-write verification passes.
- BAC-03: batch update writes formulas and read-after-write verification passes.
- BAC-04: batch clear empties all target ranges and verification passes.
- BAC-05: invalid range or formula in batch input returns validation error.
- BAC-06: batch mutation writes JSON audit records with operation and range summary.

## Decisions Captured From User Input

- clear semantics: clear formula and value, empty cell
- overwrite policy: overwrite by default
- multi-cell behavior: do not allow; return validation error
- audit output: structured JSON log plus console summary
- auth mode: service-account only
