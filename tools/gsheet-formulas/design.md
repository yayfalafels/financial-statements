# Gsheet Formulas Design

## Table of Contents

- [Summary](#summary)
- [References](#references)
- [Design Goals](#design-goals)
- [Official Docs Scan Results](#official-docs-scan-results)
- [Architecture](#architecture)
- [Module Boundaries](#module-boundaries)
- [API Interaction Contract](#api-interaction-contract)
  - [Read Formula](#read-formula)
  - [Create Formula](#create-formula)
  - [Update Formula](#update-formula)
  - [Clear Formula](#clear-formula)
  - [Read-After-Write Verification](#read-after-write-verification)
- [Input Validation Model](#input-validation-model)
- [Retry and Error Model](#retry-and-error-model)
- [CLI Contract and Outputs](#cli-contract-and-outputs)
- [Batch Crud Design 02141809](#batch-crud-design-02141809)
- [Audit Record Contract](#audit-record-contract)
- [Requirement Traceability](#requirement-traceability)
- [Clarification Task Section](#clarification-task-section)
- [Implementation Notes](#implementation-notes)

## Summary

- Defines an implementation-ready design for a Python CLI utility that performs formula read, create, update, and clear operations in Google Sheets.
- Captures official documentation scan results and translates them into concrete design decisions.
- Specifies module boundaries, API contracts, validation rules, retry policy, and CLI output schema.

## References

- docs/tools/gsheet-formulas/requirements.md
- docs/develop/010/project-management/gsheet-formulas.md
- https://developers.google.com/workspace/sheets/api/guides/values
- https://developers.google.com/workspace/sheets/api/reference/rest/v4/spreadsheets.values/get
- https://developers.google.com/workspace/sheets/api/reference/rest/v4/spreadsheets.values/update
- https://developers.google.com/workspace/sheets/api/reference/rest/v4/spreadsheets.values/clear
- https://developers.google.com/workspace/sheets/api/reference/rest/v4/spreadsheets.values
- https://developers.google.com/workspace/sheets/api/reference/rest/v4/ValueInputOption
- https://developers.google.com/workspace/sheets/api/reference/rest/v4/ValueRenderOption
- https://developers.google.com/workspace/sheets/api/guides/concepts
- https://developers.google.com/workspace/sheets/api/limits
- https://google-auth.readthedocs.io/en/latest/reference/google.oauth2.service_account.html
- https://googleapis.github.io/google-api-python-client/docs/epy/googleapiclient.discovery-module.html

## Design Goals

- Keep behavior deterministic for single-cell formula CRUD operations.
- Fail fast on user-fixable input problems before any network mutation.
- Use service-account credentials with explicit Sheets scope.
- Keep machine-readable outputs stable for SIT and UAT evidence.

## Official Docs Scan Results

The design decisions in this section are derived from current Google documentation and Python client docs.

| id         |         |                 |                   |
| ---------- | ------- | --------------- | ----------------- |
| area       |         |                 |                   |
| decision   |         |                 |                   |
| detail key |         |                 |                   |
| 01         | read    | values.get      | render formula    |
| 02         | write   | values.update   | user_entered      |
| 03         | payload | value_range     | rows default      |
| 04         | clear   | values.clear    | keep formatting   |
| 05         | range   | A1 notation     | quoted sheets     |
| 06         | retries | exp backoff     | 429 and 5xx       |
| 07         | auth    | service account | sheets scope      |
| 08         | client  | discovery build | creds and retries |

Decision notes:

- `01`: read uses `spreadsheets.values.get` with `valueRenderOption=FORMULA` so formula tokens are returned.
- `02`: create and update use `valueInputOption=USER_ENTERED` so `=A1+B1` is stored as a formula, not a literal string.
- `03`: write payload uses `ValueRange.values` as a two-dimensional array with `ROWS` as the effective default.
- `04`: clear uses `spreadsheets.values.clear`, which clears values and formulas but keeps formatting and other cell properties.
- `05`: range input remains A1 notation and must support quoted sheet names when sheet names contain spaces or special characters.
- `06`: transient failures use truncated exponential backoff with jitter for `429` and `5xx` responses.
- `07`: authentication uses `Credentials.from_service_account_file` with explicit Sheets scope.
- `08`: client construction uses the discovery client with credentials and a controlled retry count for discovery fetches.

## Architecture

| id             |            |                         |
| -------------- | ---------- | ----------------------- |
| layer          |            |                         |
| responsibility |            |                         |
| 01             | cli        | parse args and dispatch |
| 02             | validation | validate local inputs   |
| 03             | auth       | load creds and client   |
| 04             | operations | run Sheets CRUD calls   |
| 05             | output     | format text and JSON    |

Layer notes:

- `cli`: parse commands and flags, call the service layer, and print deterministic output.
- `validation`: validate client secret path, workbook ID, and single-cell A1 range before network access.
- `auth`: load service-account credentials, apply scopes, and construct the Sheets client.
- `operations`: run read, create, update, and clear against the values endpoints.
- `output`: format console summaries and JSON audit records.

## Module Boundaries

Proposed source layout under src/gsheet-formulas:

| id     |                  |                    |
| ------ | ---------------- | ------------------ |
| module |                  |                    |
| role   |                  |                    |
| 01     | cli.py           | parse and dispatch |
| 02     | models.py        | request models     |
| 03     | validation.py    | input checks       |
| 04     | auth.py          | creds and client   |
| 05     | sheets_client.py | api wrappers       |
| 06     | service.py       | CRUD orchestration |
| 07     | output.py        | text and JSON emit |
| 08     | errors.py        | error mapping      |

Module notes:

- `cli.py`: command routing and argument parsing.
- `models.py`: typed operation request and result models.
- `validation.py`: input contract checks and typed validation errors.
- `auth.py`: service-account credential loading and client construction.
- `sheets_client.py`: low-level wrappers for `values.get`, `values.update`, and `values.clear`.
- `service.py`: business rules for read, create, update, and clear flows.
- `output.py`: standardized console and JSON output formatters.
- `errors.py`: error categories and exit code mapping.

Boundary rules:

- cli does not call Google APIs directly.
- validation does not depend on network objects.
- service orchestrates behavior and uses sheets_client only after validation passes.
- output formatting is isolated to keep tests focused on behavior.

## API Interaction Contract

### Read Formula

- Endpoint: spreadsheets.values.get
- Parameters:
  - spreadsheetId, required
  - range, required single-cell A1
  - valueRenderOption=FORMULA
- Expected success:
  - values present with formula token such as =SUM(A1:A3)
  - empty cell returns no values entry or empty nested values

### Create Formula

- Endpoint: spreadsheets.values.update
- Parameters:
  - spreadsheetId
  - range single-cell A1
  - valueInputOption=USER_ENTERED
  - includeValuesInResponse=true
  - responseValueRenderOption=FORMULA
- Request body:
  - ValueRange with values=[ [ "=<formula>" ] ]
- Behavior:
  - if target already has formula, this release overwrites by default as defined in requirements

### Update Formula

- Endpoint and payload are identical to create.
- Behavior is explicit overwrite of existing content at target cell.

### Clear Formula

- Endpoint: spreadsheets.values.clear
- Parameters:
  - spreadsheetId
  - range single-cell A1
- Behavior:
  - clears value and formula only
  - formatting and validation remain unchanged per API behavior

### Read-After-Write Verification

- After create or update, perform get with valueRenderOption=FORMULA and compare returned token to requested formula.
- After clear, perform get and verify formula state is empty.

## Input Validation Model

Validation sequence executes before any network call:

| id        |                    |                 |            |
| --------- | ------------------ | --------------- | ---------- |
| input     |                    |                 |            |
| rule      |                    |                 |            |
| error cat |                    |                 |            |
| 01        | client_secret_path | file and JSON   | validation |
| 02        | workbook_id        | non-empty text  | validation |
| 03        | range_a1           | single-cell A1  | validation |
| 04        | formula_text       | starts with `=` | validation |

Validation notes:

- `client_secret_path`: file must exist, be readable JSON, and contain expected service-account keys.
- `workbook_id`: value must be a non-empty trimmed string.
- `range_a1`: value must be valid A1 notation and must resolve to a single cell.
- `formula_text`: required for create and update, and must start with `=`.

A1 policy:

- Accept A1 and SheetName!A1 forms.
- Reject multi-cell ranges like A1:B2 for create and update.
- Reject row-only and column-only references for all CRUD commands.

## Retry and Error Model

Retry policy applies only to transient failures.

| id        |                  |              |     |
| --------- | ---------------- | ------------ | --- |
| condition |                  |              |     |
| class     |                  |              |     |
| retry     |                  |              |     |
| 01        | invalid input    | user_fixable | no  |
| 02        | auth or perm     | user_fixable | no  |
| 03        | missing resource | user_fixable | no  |
| 04        | quota 429        | transient    | yes |
| 05        | backend 5xx      | transient    | yes |

Retry notes:

- `invalid input` covers parse errors and other local validation failures.
- `auth or perm` covers `401` and `403` responses.
- `missing resource` covers `404` for missing workbook or sheet targets.
- `quota 429` and `backend 5xx` use truncated exponential backoff with jitter.

Backoff strategy:

- Truncated exponential backoff with jitter.
- wait_seconds = min 2^attempt + random 0..1, max_backoff_seconds.
- default max retries: 5.
- default max backoff: 32 seconds.

## CLI Contract and Outputs

Command surface:

| id            |                |                                |
| ------------- | -------------- | ------------------------------ |
| command       |                |                                |
| required args |                |                                |
| 01            | formula read   | secret, workbook, range        |
| 02            | formula create | secret, workbook, range, value |
| 03            | formula update | secret, workbook, range, value |
| 04            | formula clear  | secret, workbook, range        |

Argument notes:

- `secret` maps to `--client-secret`.
- `workbook` maps to `--workbook-id`.
- `range` maps to `--range`.
- `value` maps to `--formula`.

Common optional args:

- --output json or text, default text
- --audit-file path to append JSON line records
- --max-retries integer, default 5
- --timeout-seconds integer, default 30

Console output must remain concise:

- success: operation, workbook id, range, status=success
- failure: operation, workbook id, range, status=failure, error category, message

Exit codes:

| id      |     |                    |
| ------- | --- | ------------------ |
| code    |     |                    |
| meaning |     |                    |
| 01      | 0   | success            |
| 02      | 2   | validation failure |
| 03      | 3   | api failure        |
| 04      | 4   | internal failure   |

## Batch Crud Design 02141809

Native Google Sheets values batch endpoints are used for batch enhancement behavior.

Batch endpoint mapping:

| id        |              |                                 |
| --------- | ------------ | ------------------------------- |
| operation |              |                                 |
| endpoint  |              |                                 |
| 01        | batch read   | spreadsheets.values.batchGet    |
| 02        | batch create | spreadsheets.values.batchUpdate |
| 03        | batch update | spreadsheets.values.batchUpdate |
| 04        | batch clear  | spreadsheets.values.batchClear  |

Batch input model:

- `batch-read` and `batch-clear`: `--ranges A1,B2,C3`
- `batch-create` and `batch-update`: `--batch-file <json>`
- Batch file JSON format:
  - list of objects
  - each object includes `range` and `formula`

Batch verification model:

- After batch create and update, run batch read for target ranges.
- Compare requested and resulting formulas using canonical equivalence rules.
- Accept canonicalized formula tokens when semantically equivalent.

Batch output model:

- Reuse existing `FormulaResult` contract with `range_a1` as comma-separated summary.
- For batch operations, `requested_formula` and `resulting_formula` store JSON map text.
- Batch mutation operations append audit records via the existing audit writer.

## Audit Record Contract

Mutation commands create, update, and clear emit one JSON record per operation.

| id    |                   |                |
| ----- | ----------------- | -------------- |
| field |                   |                |
| type  |                   |                |
| 01    | event_at          | string utc     |
| 02    | operation         | string         |
| 03    | workbook_id       | string         |
| 04    | range_a1          | string         |
| 05    | status            | string         |
| 06    | error_category    | string or null |
| 07    | error_message     | string or null |
| 08    | requested_formula | string or null |
| 09    | resulting_formula | string or null |

Audit notes:

- `event_at` is serialized as UTC ISO-8601.
- `requested_formula` is null for read and clear.
- `resulting_formula` is null for failed mutations.

## Requirement Traceability

| id          |                  |                  |
| ----------- | ---------------- | ---------------- |
| req ids     |                  |                  |
| design area |                  |                  |
| 01          | FR-01, FR-02     | read contract    |
| 02          | FR-03, FR-04     | create contract  |
| 03          | FR-05, FR-06     | update contract  |
| 04          | FR-07, FR-08     | clear contract   |
| 05          | FR-09, FR-10     | validation rules |
| 06          | FR-11, FR-13     | output and audit |
| 07          | NFR-01, NFR-03   | validation flow  |
| 08          | NFR-02, ER-01-05 | error model      |

Traceability notes:

- Read, create, update, and clear contract sections map to the API interaction contract subsections.
- Validation rules map to the input validation model and create overwrite behavior.
- Output and audit map to CLI output and audit record sections.
- Error model maps to retry handling and runtime error categorization.

## Clarification Task Section

This section records the user decisions collected before implementation and SIT execution.

| id                |           |                       |          |
| ----------------- | --------- | --------------------- | -------- |
| area              |           |                       |          |
| resolved decision |           |                       |          |
| status            |           |                       |          |
| 01                | auth      | service account JSON  | resolved |
| 02                | SIT scope | workbook and cell set | resolved |
| 03                | safety    | overwrite by default  | resolved |
| 04                | evidence  | docs tools path       | resolved |

Resolved notes:

- `01`: use service-account credentials for runtime auth. The repository convention points to `.credentials/client_secret.json`, so this utility will use that path even though the filename is inherited from older Google Sheets tooling.
- `02`: autonomous SIT uses workbook `1SNtnlNufcZp-44f5U1YbECUwHbkICih5cdywiu04wpI` and single-cell mutation target `A3`.
- `03`: release `010` uses overwrite by default with no confirmation gate.
- `04`: SIT evidence and pre-UAT handoff artifacts should be stored under `docs/tools/gsheet-formulas/`.

## Implementation Notes

- Prefer spreadsheets.values.update for deterministic single-cell write operations in this release.
- Use spreadsheets.values.batchUpdate only when future scope adds multi-range workflows.
- Keep operation logic side-effect free except for explicit API calls and audit append actions.
- Use dedicated implementation environment `gs-formula-env` at repository root.
- Install required runtime and test dependencies in `gs-formula-env` from `requirements.txt` before development and SIT.
