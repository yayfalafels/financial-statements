# Gsheet Formulas Test Strategy

## Table of Contents

- [Summary](#summary)
- [References](#references)
- [Scope](#scope)
- [Test Levels](#test-levels)
- [Scenario Matrix](#scenario-matrix)
- [Data and Environment](#data-and-environment)
- [Evidence Standard](#evidence-standard)
- [Defect Triage Rules](#defect-triage-rules)
- [Exit Criteria Through SIT](#exit-criteria-through-sit)

## Summary

- Defines verification coverage from unit tests through SIT for release 010.
- Maps requirement acceptance criteria to concrete verification paths.
- Standardizes evidence and defect handling so SIT can be executed autonomously before UAT.

## References

- docs/tools/gsheet-formulas/requirements.md
- docs/tools/gsheet-formulas/design.md
- docs/tools/gsheet-formulas/user-guide.md
- docs/develop/010/project-management/gsheet-formulas.md

## Scope

- In scope: formula read, create, update, and clear behavior on single-cell A1 ranges.
- In scope: input validation, error categorization, and audit output.
- Out of scope: non-formula operations and multi-cell mutation workflows.

## Test Levels

| id | level       | purpose               | execution mode |
| -- | ----------- | --------------------- | -------------- |
| 01 | unit        | pure validation rules | local automated |
| 02 | integration | api wrappers and flow | local automated |
| 03 | SIT         | live workbook checks  | controlled live |
| 04 | UAT         | operator acceptance   | human guided   |

Level notes:

- Unit tests run without external network calls.
- Integration tests validate request and response behavior with controlled doubles.
- SIT runs against workbook 1SNtnlNufcZp-44f5U1YbECUwHbkICih5cdywiu04wpI at target A3.
- UAT remains user verification only.

## Scenario Matrix

| id | requirement set | scenario          | level path       |
| -- | --------------- | ----------------- | ---------------- |
| 01 | AC-01, AC-02    | formula read      | unit, SIT, UAT   |
| 02 | AC-03, AC-04    | create and update | integration, SIT |
| 03 | AC-05           | clear             | integration, SIT |
| 04 | AC-06 to AC-08  | bad input         | unit, integration |
| 05 | AC-09, AC-10    | audit and failures | integration, SIT |

## Data and Environment

| id | item         | value                                  |
| -- | ------------ | -------------------------------------- |
| 01 | runtime venv | gs-formula-env at repository root      |
| 02 | dependencies | install from requirements.txt          |
| 03 | credential   | .credentials/client_secret.json        |
| 04 | workbook     | 1SNtnlNufcZp-44f5U1YbECUwHbkICih5cdywiu04wpI |
| 05 | SIT range    | A3                                     |

Environment notes:

- Do not create additional project venvs for this workflow.
- Install dependencies into gs-formula-env before development and SIT.

## Evidence Standard

Each SIT run entry should capture:

- test id and scenario name
- workbook id and target range
- command executed
- observed output and result in workbook
- pass or fail outcome
- timestamp and operator or agent executor

Suggested evidence destination:

- docs/tools/gsheet-formulas/sit-report.md

## Defect Triage Rules

| id | severity | rule                    | release impact |
| -- | -------- | ----------------------- | -------------- |
| 01 | high     | blocks core CRUD path   | release block  |
| 02 | medium   | workaround exists        | fix or defer   |
| 03 | low      | cosmetic or minor output | may defer      |

## Exit Criteria Through SIT

- Unit and integration suites pass in gs-formula-env.
- SIT scenarios for read, create, update, and clear pass at A3.
- No open high-severity defects remain for release 010 scope.
- SIT evidence is published in docs with reproducible command history.
