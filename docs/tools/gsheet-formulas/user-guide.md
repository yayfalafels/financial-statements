# Gsheet Formulas User Guide

## Table of Contents

- [Summary](#summary)
- [References](#references)
- [Purpose](#purpose)
- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Inputs](#inputs)
- [Command Overview](#command-overview)
- [Command Contract](#command-contract)
- [Operator Scenarios](#operator-scenarios)
- [Batch Scenarios](#batch-scenarios)
- [Black Scholes Use Case](#black-scholes-use-case)
- [SIT Runbook](#sit-runbook)
- [Evidence Capture](#evidence-capture)
- [Troubleshooting](#troubleshooting)
- [Safety Notes](#safety-notes)

## Summary

- Describes operator-facing use of the `gsheet-formulas` utility for single and batch formula workflows.
- Defines the required inputs, expected outcomes, and evidence capture expectations for SIT and UAT.
- Links the operator workflow to the tracker test strategy section.

## References

- docs/tools/gsheet-formulas/requirements.md
- docs/tools/gsheet-formulas/design.md
- docs/tools/gsheet-formulas/test-strategy.md
- docs/develop/010/project-management/gsheet-formulas.md

## Purpose

Provide the operator workflow for using the utility safely in controlled workbook scenarios,
including batch operations.

## Prerequisites

- Access to the configured Google workbook.
- Runtime credential file at `.credentials/client_secret.json`.
- Safe target ranges for validation and mutation testing.

## Environment Setup

- Use the repository runtime environment at `env/`.
- Activate `env/` before running utility commands.
- Install dependencies from `requirements.txt` and `gsheet-formulas-requirements.txt`.
- Verify that `.credentials/client_secret.json` is readable in the active session.

## Inputs

| id | input         | description              |
| -- | ------------- | ------------------------ |
| 01 | client secret | auth JSON path           |
| 02 | workbook id   | target workbook          |
| 03 | range         | single-cell A1           |
| 04 | formula       | formula text             |
| 05 | ranges        | comma list for batch ops |
| 06 | batch file    | json list range formula  |

Input notes:

- The credential file is repository-local and provided out of band.
- The range must be a single-cell A1 reference.
- The formula input is required for create and update only.
- Batch read and clear require `--ranges`.
- Batch create and update require `--batch-file`.

## Command Overview

| id | command      | purpose          |
| -- | ------------ | ---------------- |
| 01 | read         | show formula     |
| 02 | create       | write formula    |
| 03 | update       | replace formula  |
| 04 | clear        | clear formula    |
| 05 | batch-read   | read many cells  |
| 06 | batch-create | write many cells |
| 07 | batch-update | replace many     |
| 08 | batch-clear  | clear many       |

Command notes:

- Exact CLI syntax will match the implementation generated from the design contract.
- Success and failure outputs must remain stable for evidence capture.

## Command Contract

Use this flag contract for all operations:

- required common flags: `--client-secret`, `--workbook-id`, `--range`
- required mutation value flag for create and update: `--formula`
- optional output controls: `--output`, `--audit-file`, `--max-retries`, `--timeout-seconds`

Batch flag contract:

- `batch-read` and `batch-clear`: `--ranges A3,B3,C3`
- `batch-create` and `batch-update`: `--batch-file path/to/file.json`
- batch file schema: list of objects with `range` and `formula`

Expected behavior by operation:

- read returns formula token using formula render mode
- create writes formula to empty or existing target as overwrite by default
- update overwrites target formula
- clear removes formula and value from target
- batch-read returns a formula map for all requested ranges
- batch-create and batch-update verify using follow-up batch-read
- batch-clear verifies all target cells are empty

## Operator Scenarios

- Read a formula from a known single cell and verify the token returned matches the sheet formula.
- Create a formula in an empty single cell and verify the sheet result.
- Update the formula in the same cell and verify the new token and displayed result.
- Clear the formula and verify the cell is empty.

## Batch Scenarios

- Batch-read formulas from `A3,B3` and verify both results.
- Batch-create formulas to `A3,B3` and verify each target.
- Batch-update formulas in `A3,B3` and verify overwrite behavior.
- Batch-clear `A3,B3` and verify both cells are empty.

Batch file example:

```json
[
	{"range": "A3", "formula": "=1+1"},
	{"range": "B3", "formula": "=2+2"}
]
```

## Black Scholes Use Case

Use batch-create to populate a labeled Black-Scholes block.

Label and input block:

| id | cell | value                |
| -- | ---- | -------------------- |
| 01 | D2   | Black-Scholes Model  |
| 02 | D3   | Spot (S)             |
| 03 | E3   | 100                  |
| 04 | D4   | Strike (K)           |
| 05 | E4   | 100                  |
| 06 | D5   | Risk-free rate (r)   |
| 07 | E5   | 0.05                 |
| 08 | D6   | Volatility (sigma)   |
| 09 | E6   | 0.2                  |
| 10 | D7   | Time to expiry (T)   |
| 11 | E7   | 1                    |

Computation cells:

| id | cell | formula key |
| -- | ---- | ----------- |
| 01 | E8   | d1          |
| 02 | E9   | d2          |
| 03 | E10  | call price  |
| 04 | E11  | put price   |

Formulas:

- E8: `(LN(E3/E4)+(E5+0.5*E6^2)*E7)/(E6*SQRT(E7))`
- E9: `E8-E6*SQRT(E7)`
- E10: `E3*IFERROR(NORM.S.DIST(E8,TRUE),NORMSDIST(E8))-E4*EXP(-E5*E7)*IFERROR(NORM.S.DIST(E9,TRUE),NORMSDIST(E9))`
- E11: `E4*EXP(-E5*E7)*IFERROR(NORM.S.DIST(-E9,TRUE),NORMSDIST(-E9))-E3*IFERROR(NORM.S.DIST(-E8,TRUE),NORMSDIST(-E8))`

Operator notes:

- In some sheets, `NORM.S.DIST` may return `#N/A`; use the `IFERROR(...,NORMSDIST(...))` fallback.
- In PowerShell, wrap formulas with `$` in single quotes when passed inline.

Scenario preconditions:

- workbook id: `1SNtnlNufcZp-44f5U1YbECUwHbkICih5cdywiu04wpI`
- target range: `A3`
- credential path: `.credentials/client_secret.json`

## SIT Runbook

Run sequence:

1. Run read on A3 and capture returned formula state.
2. Run create on A3 with a simple deterministic formula and capture output and sheet result.
3. Run update on A3 with a second deterministic formula and capture output and sheet result.
4. Run clear on A3 and capture output and post-clear sheet state.
5. Confirm audit records exist for create, update, and clear.

Batch run sequence:

1. Run batch-read on `A3,B3` and capture formula map.
2. Run batch-create from `.dev/env/batch_sit_create.json`.
3. Run batch-update from `.dev/env/batch_sit_update.json`.
4. Run batch-clear on `A3,B3`.
5. Run batch-create for the Black-Scholes payload and verify call and put outputs.

Pass criteria:

- each command exits successfully for valid input cases
- returned formula token matches expected values for read, create, and update
- clear leaves A3 empty
- audit entries include operation, workbook id, range, status, and timestamp
- batch operations return success and expected per-range values
- Black-Scholes call and put cells return numeric values, not `#N/A`

## Evidence Capture

- Capture console output for each scenario.
- Capture JSON audit output for mutation scenarios.
- Record pass and fail outcomes in the SIT and UAT evidence artifacts under `docs/tools/gsheet-formulas/`.

Evidence file suggestions:

- SIT run report: `docs/tools/gsheet-formulas/sit-report.md`
- Batch SIT report: `docs/tools/gsheet-formulas/batch-sit-report.md`
- UAT execution log: `docs/tools/gsheet-formulas/uat-report.md`

## Troubleshooting

- auth failure: verify credential file path and workbook sharing permissions
- invalid range: confirm single-cell A1 notation
- quota errors: rerun with retry policy and capture error response in report
- formula mismatch: run read-after-write check and record observed token
- batch mismatch: compare requested and resulting per-range formula map
- Black-Scholes `#N/A`: use `IFERROR(NORM.S.DIST(x,TRUE),NORMSDIST(x))`

## Safety Notes

- Release `010` uses overwrite by default.
- Use only approved SIT or UAT target ranges for mutation scenarios.
- Do not point the utility at production cells without separate operator approval.
