# Project tracking: 02.14.18 gsheet-formulas

This document tracks delivery for `02.14.18` from requirements through SIT and UAT for the Google Sheets formula CRUD utility.

## Scope

- Utility name: `gsheet-formulas`
- Runtime: Python
- Primary capability: CRUD for Google Sheets cell formulas via Google Sheets API
- Required user inputs:
  - client secret JSON file for GAS IAM automation account
  - workbook ID
  - cell range (for example `A34`)

## Milestone workflow

| seq    |             |        |               |                      |
| ------ | ----------- | ------ | ------------- | -------------------- |
| id     |             |        |               |                      |
| status |             |        |               |                      |
| phase  |             |        |               |                      |
| task   |             |        |               |                      |
| 01     | 02.14.18.08 | closed | dev docs      | tracker and workflow |
| 02     | 02.14.18.01 | closed | requirements  | finalize criteria    |
| 03     | 02.14.18.04 | closed | design        | design spec complete |
| 04     | 02.14.18.02 | closed | test strategy | verify plan and map  |
| 05     | 02.14.18.03 | closed | output files  | baseline artifacts   |
| 06     | 02.14.18.05 | closed | development   | cli formula crud     |
| 07     | 02.14.18.06 | closed | sit           | live integration run |
| 08     | 02.14.18.07 | closed | uat           | user validation      |
| 09     | 02.14.18.09 | open   | enhancement   | batch formula crud   |

## Initial target output files

| id     |                   |        |                                                        |
| ------ | ----------------- | ------ | ------------------------------------------------------ |
| output |                   |        |                                                        |
| status |                   |        |                                                        |
| file   |                   |        |                                                        |
| 01     | requirements doc  | closed | docs/tools/gsheet-formulas/requirements.md             |
| 02     | user guide        | closed | docs/tools/gsheet-formulas/user-guide.md               |
| 03     | design doc        | closed | docs/tools/gsheet-formulas/design.md                   |
| 04     | task tracker      | closed | docs/develop/010/project-management/gsheet-formulas.md |
| 05     | dev workflow      | closed | .github/prompts/gsheet-formulas.prompt.md              |
| 06     | source code       | closed | src/gsheet-formulas/*                                  |
| 07     | test strategy doc | closed | docs/tools/gsheet-formulas/test-strategy.md            |
| 08     | dependency files  | closed | requirements.txt and gsheet-formulas-requirements.txt  |

## Task details

_02.14.18.01 (closed) requirements_

- Draft requirements document created at `docs/tools/gsheet-formulas/requirements.md`.
- User decision inputs captured for clear semantics, overwrite policy, range policy, audit output, and auth mode.

- Define functional requirements for formula get, create, update, and clear/delete behavior.
- Define non-functional requirements for safety, idempotency, and auditability.
- Define required input contract:
  - client secret file path
  - workbook ID
  - A1 notation range
- Define acceptance criteria for valid, invalid, and missing input cases.

Closure criteria:

- `docs/tools/gsheet-formulas/requirements.md` includes measurable acceptance criteria for each CRUD operation.
- Requirement statements are testable and map to SIT/UAT scenarios.

_02.14.18.02 (closed) test strategy_

- Define test levels and scope: unit, integration, SIT, UAT.
- Define test data strategy for workbook fixtures and non-production credentials.
- Define required evidence format for pass/fail and defect logging.

Strategy coverage:

| id       |             |                      |                  |
| -------- | ----------- | -------------------- | ---------------- |
| level    |             |                      |                  |
| focus    |             |                      |                  |
| evidence |             |                      |                  |
| 01       | unit        | validation and model | local test pass  |
| 02       | integration | api client behavior  | mocked responses |
| 03       | SIT         | live workbook CRUD   | run report       |
| 04       | UAT         | user workflow        | sign-off record  |

Requirement verification map:

| id                |                |                   |
| ----------------- | -------------- | ----------------- |
| req set           |                |                   |
| verification path |                |                   |
| 01                | AC-01, AC-02   | unit, SIT, UAT    |
| 02                | AC-03, AC-04   | integration, SIT  |
| 03                | AC-05          | integration, SIT  |
| 04                | AC-06 to AC-08 | unit, integration |
| 05                | AC-09, AC-10   | integration, SIT  |

Evidence rules:

- Unit and integration evidence may be captured from local automated test output.
- SIT evidence must include workbook ID, target range, command used, observed result, and pass or fail status.
- UAT evidence must include user scenario outcome and sign-off decision.
- Defects must record severity, reproduction path, and retest result.

Closure criteria:

- Test strategy section is published in tracker and linked from design and user guide.
- Every requirement has at least one verification path.

Closure evidence:

- Added test level scope, requirement verification map, and evidence rules to this tracker section.
- Created `docs/tools/gsheet-formulas/test-strategy.md`.
- Created `docs/tools/gsheet-formulas/user-guide.md` with detailed user workflow and SIT runbook.

_02.14.18.03 (closed) initial target output files_

Subtasks:

| seq    |                |        |                        |
| ------ | -------------- | ------ | ---------------------- |
| id     |                |        |                        |
| status |                |        |                        |
| task   |                |        |                        |
| 01     | 02.14.18.03.01 | closed | docs baseline create   |
| 02     | 02.14.18.03.02 | closed | strategy doc create    |
| 03     | 02.14.18.03.03 | closed | source path scaffold   |
| 04     | 02.14.18.03.04 | closed | dependency file create |

- Create folder and file skeleton for all required outputs.
- Add initial headers and section templates to each target doc.
- Confirm naming and path conventions match release `010` documentation structure.

Closure criteria:

- All target files exist at required paths.
- Files include baseline sections and ownership notes.

Closure evidence:

- Added baseline source path at `src/gsheet-formulas/README.md`.
- Added detailed user guide at `docs/tools/gsheet-formulas/user-guide.md`.
- Added standalone test strategy artifact at `docs/tools/gsheet-formulas/test-strategy.md`.
- Added implementation dependency files at `requirements.txt` and `gsheet-formulas-requirements.txt`.

_02.14.18.04 (closed) design_

Design subtasks:

| seq    |                |        |                            |
| ------ | -------------- | ------ | -------------------------- |
| id     |                |        |                            |
| status |                |        |                            |
| task   |                |        |                            |
| 01     | 02.14.18.04.01 | closed | official docs scan         |
| 02     | 02.14.18.04.02 | closed | module boundary draft      |
| 03     | 02.14.18.04.03 | closed | api interaction contract   |
| 04     | 02.14.18.04.04 | closed | validation and retry model |
| 05     | 02.14.18.04.05 | closed | cli contract and outputs   |

_02.14.18.04.01 (closed) official docs scan_

Review official Google Sheets API, Google auth, and Python client documentation to confirm supported formula read and write patterns. Capture only the implementation-relevant decisions and links needed for this utility.

Closure evidence:

- Created `docs/tools/gsheet-formulas/design.md` with an official documentation scan section and implementation decisions.
- Added direct references to official docs for `spreadsheets.values.get`, `spreadsheets.values.update`, `spreadsheets.values.clear`, `ValueInputOption`, `ValueRenderOption`, usage limits, service-account auth, and Python discovery client build.

_02.14.18.04.02 (closed) module boundary draft_

Define module boundaries for authentication, input parsing, formula operations, and result formatting. Keep responsibilities separated so CRUD behavior can be tested independently.

Closure evidence:

- Added module boundaries to `docs/tools/gsheet-formulas/design.md` with explicit source layout, module roles, and boundary rules.

_02.14.18.04.03 (closed) api interaction contract_

Specify how each CRUD operation maps to Google Sheets API calls, payload shape, and expected response handling. Include the minimum request and response fields required for reliable operation.

Closure evidence:

- Added CRUD endpoint mapping, request parameters, request body shape, and read-after-write verification to `docs/tools/gsheet-formulas/design.md`.

_02.14.18.04.04 (closed) validation and retry model_

Define validation rules for client secret path, workbook ID, and A1 range input before network calls are made. Establish retry and error categorization rules for transient versus user-fixable failures.

Closure evidence:

- Added input validation rules, A1 policy, retry categories, and truncated backoff strategy to `docs/tools/gsheet-formulas/design.md`.

_02.14.18.04.05 (closed) cli contract and outputs_

Define command inputs, flags, and standardized output format for success, warning, and failure cases. Keep output concise so SIT and UAT evidence can be captured consistently.

Closure evidence:

- Added CLI command surface, option mapping, exit codes, audit schema, and resolved clarification decisions to `docs/tools/gsheet-formulas/design.md`.

Closure criteria:

- `docs/tools/gsheet-formulas/design.md` is complete enough for implementation without unresolved ambiguity.
- Design decisions are traceable to requirements.

Closure evidence:

- Resolved design-phase clarification items for auth format, SIT workbook and cell, overwrite policy, and evidence destination in `docs/tools/gsheet-formulas/design.md`.

_02.14.18.05 (closed) development_

Subtasks:

| seq    |                |        |                        |
| ------ | -------------- | ------ | ---------------------- |
| id     |                |        |                        |
| status |                |        |                        |
| task   |                |        |                        |
| 01     | 02.14.18.05.01 | closed | env setup and deps     |
| 02     | 02.14.18.05.02 | closed | module scaffold        |
| 03     | 02.14.18.05.03 | closed | read and clear impl    |
| 04     | 02.14.18.05.04 | closed | create and update impl |
| 05     | 02.14.18.05.05 | closed | validation and errors  |
| 06     | 02.14.18.05.06 | closed | tests and reports      |

- Implement source layout under `src/gsheet-formulas/*`.
- Implement commands:
  - read formula from cell/range
  - write/create formula
  - update existing formula
  - clear formula content
- Implement validation and standardized error messages.
- Add automated tests aligned with strategy.

Execution plan notes:

- Use repository runtime environment at `env/`.
- Install required libraries from `requirements.txt` and `gsheet-formulas-requirements.txt` into `env/`.
- Keep helper scripts under `.dev/.scripts/` when temporary diagnostics are required.

Closure criteria:

- CRUD operations execute successfully using configured credentials and workbook.
- Automated tests for core paths pass.

Closure evidence:

- Implemented complete module set in `src/gsheet-formulas/`: `cli.py`, `models.py`, `validation.py`, `auth.py`, `sheets_client.py`, `service.py`, `output.py`, and `errors.py`.
- Added automated tests in `tests/gsheet_formulas/test_validation.py` and `tests/gsheet_formulas/test_service.py`.
- Executed `pytest tests/gsheet_formulas -q` in `env/` with `6 passed`.

_02.14.18.06 (closed) SIT_

Subtasks:

| seq    |                |        |                       |
| ------ | -------------- | ------ | --------------------- |
| id     |                |        |                       |
| status |                |        |                       |
| task   |                |        |                       |
| 01     | 02.14.18.06.01 | closed | sit data prep         |
| 02     | 02.14.18.06.02 | closed | sit CRUD execution    |
| 03     | 02.14.18.06.03 | closed | sit result validation |
| 04     | 02.14.18.06.04 | closed | sit report publish    |

- Execute end-to-end integration scenarios using real API calls in controlled workbook.
- Validate cross-component behavior: auth, input parsing, API request construction, response handling.
- Capture SIT evidence, defects, and remediation retest results.

SIT target notes:

- workbook id: `1SNtnlNufcZp-44f5U1YbECUwHbkICih5cdywiu04wpI`
- mutation range: `A3`

Closure criteria:

- SIT run report shows required scenarios passed or approved with documented risk acceptance.
- No open high-severity defects for release scope.

Closure evidence:

- Executed live read, create, update, and clear scenarios against workbook `1SNtnlNufcZp-44f5U1YbECUwHbkICih5cdywiu04wpI` at range `A3`.
- Captured mutation audit evidence at `docs/tools/gsheet-formulas/sit-audit.jsonl`.
- Captured SIT run evidence at `docs/tools/gsheet-formulas/sit-report.md`.
- Executed negative scenarios for validation failures and API 404 failure; behavior matched error taxonomy.

_02.14.18.07 (closed) UAT_

- Execute user-focused scenarios from user guide for formula CRUD workflows.
- Validate expected outcomes in workbook after each operation.
- Collect user feedback and confirm acceptance decisions.

Closure criteria:

- UAT sign-off recorded with pass/fail outcomes per scenario.
- Release recommendation documented with any deferred items.

Closure evidence:

- Executed user-verified UAT scenarios for read, create, update, clear, and failed mutation audit behavior.
- Added deferred formula reference case using `=SUM($E2:D2)` and validated accepted token canonicalization.
- Captured UAT evidence in `docs/tools/gsheet-formulas/uat-report.md`.
- Captured UAT audit records in `docs/tools/gsheet-formulas/uat-audit.jsonl`.
- User sign-off decision: approve release recommendation.

_02.14.18.09 (open) batch crud enhancement_

Subtasks:

| seq    |                |        |                       |
| ------ | -------------- | ------ | --------------------- |
| id     |                |        |                       |
| status |                |        |                       |
| task   |                |        |                       |
| 01     | 02.14.18.09.01 | closed | requirements baseline |
| 02     | 02.14.18.09.02 | closed | design                |
| 03     | 02.14.18.09.03 | closed | development           |
| 04     | 02.14.18.09.04 | closed | sit                   |
| 05     | 02.14.18.09.05 | open   | uat                   |

Design gate subtasks:

| seq    |                   |        |                       |
| ------ | ----------------- | ------ | --------------------- |
| id     |                   |        |                       |
| status |                   |        |                       |
| task   |                   |        |                       |
| 01     | 02.14.18.09.02.01 | closed | api support research  |
| 02     | 02.14.18.09.02.02 | closed | batch contract design |

Research decision:

- Native batch support exists in Google Sheets values API.
- Read: `spreadsheets.values.batchGet`.
- Create and update: `spreadsheets.values.batchUpdate`.
- Clear: `spreadsheets.values.batchClear`.
- Decision: enhancement is in-scope and not dead on arrival.

Research evidence:

- https://developers.google.com/workspace/sheets/api/reference/rest/v4/spreadsheets.values
- https://developers.google.com/workspace/sheets/api/reference/rest/v4/spreadsheets.values/batchGet
- https://developers.google.com/workspace/sheets/api/reference/rest/v4/spreadsheets.values/batchUpdate
- https://developers.google.com/workspace/sheets/api/reference/rest/v4/spreadsheets.values/batchClear

Progress and closure evidence:

- Requirements baseline published in `docs/tools/gsheet-formulas/requirements.md` under batch enhancement section.
- Design contract published in `docs/tools/gsheet-formulas/design.md` under batch CRUD design section.
- Development completed for batch CLI and service paths in `src/gsheet-formulas/cli.py`,
  `src/gsheet-formulas/service.py`, `src/gsheet-formulas/sheets_client.py`,
  `src/gsheet-formulas/validation.py`, and `src/gsheet-formulas/models.py`.
- Added batch tests in `tests/gsheet_formulas/test_service.py` and
  `tests/gsheet_formulas/test_validation.py`.
- Local verification: `pytest tests/gsheet_formulas -q` passed with `11 passed`.

Next step in progress:

- `02.14.18.09.05` opened for UAT of batch operations.

Batch SIT evidence:

- Executed live batch-read, batch-create, batch-update, and batch-clear scenarios.
- Validated larger multi-range batch-create using the Black-Scholes labeled block payload.
- Executed negative scenarios for missing workbook input and invalid workbook ID.
- Observed no unhandled exceptions; error mapping returned expected exit codes.
- Captured SIT evidence in `docs/tools/gsheet-formulas/batch-sit-report.md`.
- Captured audit output in `docs/tools/gsheet-formulas/batch-sit-audit.jsonl`.
- Documented learnings for formula compatibility and shell quoting in the batch SIT report.

## Dependency and risk log

| seq        |            |                       |                    |        |                     |
| ---------- | ---------- | --------------------- | ------------------ | ------ | ------------------- |
| type       |            |                       |                    |        |                     |
| item       |            |                       |                    |        |                     |
| impact     |            |                       |                    |        |                     |
| status     |            |                       |                    |        |                     |
| mitigation |            |                       |                    |        |                     |
| 01         | dependency | service acct access   | blocks sit and uat | closed | validated in sit    |
| 02         | dependency | sheets api access     | blocks runtime     | closed | validated in sit    |
| 03         | risk       | overwrite by default  | data integrity     | open   | add safety control  |
| 04         | risk       | clear semantics drift | behavior mismatch  | open   | enforce req wording |

Mitigation notes:

- Row 01 validated with `.credentials/client_secret.json` in SIT.
- Row 02 validated by successful live CRUD scenarios in SIT.
- Row 03 mitigation target: add dry-run and confirmation flags in a follow-up release.
- Row 04 mitigation target: keep clear semantics explicit in requirements and user guide.

## Status update protocol

- Update status values only as: `pending`, `open`, `blocked`, `closed`.
- Record closure evidence directly under the corresponding task section.
- Keep task IDs in this tracker document only.
