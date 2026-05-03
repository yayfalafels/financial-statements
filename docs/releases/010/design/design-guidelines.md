---
title: Design Guidelines
version: 3.0
last_updated: 2026-05-03
---

# Design Guidelines

## Summary

This document defines design guidelines for runtime choices, API behavior, adapter boundaries, configuration patterns, and parameterization rules. The guidance is implementation-ready for the selected stack and workflows.

The guidelines are aligned to current design decisions:

- Python 3.12 runtime on Windows 11 local host
- Flask plus Waitress backend API runtime
- Direct Google SDK integration in the Google Sheets adapter
- SQLite as canonical persistence through a backend-neutral SQL adapter contract
- ReportLab as the required publish-stage PDF renderer, with WeasyPrint optional

## Table of contents

- [Runtime and stack decisions](#runtime-and-stack-decisions)
- [Variable names](#variable-names)
- [Pass-through naming](#pass-through-naming)
- [Python](#python)
- [API guidelines](#api-guidelines)
- [Configuration-driven pattern](#configuration-driven-pattern)
- [Parameterization guidelines](#parameterization-guidelines)
- [SQL and SQLite](#sql-and-sqlite)
- [Financial precision](#financial-precision)
- [Google Sheets adapter](#google-sheets-adapter)
- [HomeBudget adapter](#homebudget-adapter)
- [PDF generation](#pdf-generation)
- [Google Sheets](#google-sheets)
- [PowerShell CLI](#powershell-cli)
- [Error handling](#error-handling)
- [Layer boundaries](#layer-boundaries)
- [Logging](#logging)
- [Secrets and credentials](#secrets-and-credentials)

## Runtime and stack decisions

- Backend API framework is Flask.
- Backend API host runtime is Waitress.
- Request and payload validation is Pydantic.
- Google Sheets API integration is direct Google SDK through the Google Sheets adapter boundary.
- SQL access is routed only through the SQL adapter boundary; domain and orchestration modules do not run direct SQL.
- Publish-stage PDF generation is required and uses ReportLab as the default renderer.
- WeasyPrint is an optional renderer behind the same PDF adapter contract.

## Variable names

Follow Python naming conventions with domain-meaningful names.

- Use concise names tied to accounting concepts, for example `period_key`, `reconcile_status`, `variance_amount`.
- Keep names stable across API payloads, config keys, SQLite columns, and logging fields.
- Do not invent synonyms for the same concept across modules.

Subject-verb ordering:

- Prefer subject-verb or subject-attribute ordering, for example `session_close` over `close_session`.

Platform conventions:

- Python variables and functions: `lowercase_with_underscores`
- Python classes: `CapWords`
- Python constants: `UPPERCASE`
- SQL table and column names: `singular_snake_case`
- JSON and config keys: `lowercase_with_underscores`

## Pass-through naming

Minimize arbitrary variations in variable names as a concept passes through the app from front-end through source code to the back-end data model. When the same concept travels across layers, keep the name identical or as close as possible.

Example:

- UI field label: `statement_date`
- Python variable: `statement_date`
- SQL column: `statement_date`
- API field: `statement_date`

When a name variation is required by a platform constraint, document the mapping explicitly in the relevant design artifact. Do not introduce a new name simply for stylistic variety.

## Python

Python 3.12 is the runtime for all backend logic, adapter modules, CLI commands, and domain processing.

Code style:

Follow PEP 8 as the baseline. Readability takes priority over brevity. Use 4-space indentation. Limit lines to 99 characters in Python source files. Prefer implicit line continuation inside parentheses over backslash continuation.

Imports:

Order imports in three groups separated by a blank line: standard library, third-party packages, local modules. Use absolute imports. Never use wildcard imports (`from module import *`).

Functions and methods:

Keep functions focused on a single responsibility. Prefer explicit positional arguments for required parameters. Use keyword-only arguments for optional configuration values. Avoid `*args` and `**kwargs` unless the function is a pass-through or decorator.

Use `with` statements for all file and database connection handling to guarantee cleanup.

Exceptions:

Catch the most specific exception type available. Never use a bare `except:` clause. Use `raise X from Y` when re-raising to preserve the original traceback. Derive custom app exceptions from `Exception`, not `BaseException`.

Type hints:

Use type hints for all public module interfaces -- function signatures and return types. Type hints on internal helpers are optional. Avoid complex generic types where a clear docstring conveys intent more directly.

Module structure:

Group each module by: module-level constants, public classes, public functions, private helpers. Place imports at the top of every file, before any executable code.

## API guidelines

The backend API contract is a first-class integration boundary between Google Sheets flows, CLI operations, and runtime modules.

Route design:

- Use `/api/v1/` prefix for all routes.
- Use resource-driven paths for state reads and command-driven paths for workflow actions.
- Keep route names kebab-case.

HTTP method policy:

- `GET` for read models with no side effects.
- `POST` for workflow stage commands and actions with side effects.
- `PUT` for idempotent full replacement updates.
- `PATCH` for partial updates where patch semantics are explicit.

Payload contracts:

- Validate request payloads at route boundary with Pydantic models.
- Reject unknown fields by default unless an endpoint explicitly supports extension keys.
- Return stable response envelopes: `status`, `data`, `error`, `meta`.

Idempotency and replay:

- Side-effecting `POST` routes must accept `idempotency_key`.
- The same `idempotency_key` with the same command payload must return the same command outcome.
- Duplicate keys with different payloads must return a validation conflict.

Error response contract:

- Return typed error codes, not only free-text messages.
- Include actionable remediation in `error.message`.
- Include `correlation_id` for every failed request.

Versioning:

- Backward-incompatible changes require a new API version path.
- Backward-compatible additions may extend payload fields with documented defaults.

Specific example:

`POST /api/v1/workflows/monthly-close/stage-run`

- Required request fields:
    - `period_key`
    - `stage_key`
    - `run_mode`
    - `idempotency_key`
- `run_mode` allowed values:
    - `validate_only`
    - `execute`
- Successful response includes:
    - `status: success`
    - `data.stage_status`
    - `data.stage_run_id`
    - `meta.correlation_id`
- Error response includes:
    - `status: error`
    - `error.code`
    - `error.message`
    - `error.remediation`
    - `meta.correlation_id`

## Configuration-driven pattern

Default behavior should be driven by configuration, not hardcoded constants in runtime code.

Config domains:

- Runtime config: paths, service endpoints, feature flags, retry policy.
- Source config: statement profiles, parsing maps, account-source associations.
- Workflow config: stage gates, override policy, stage dependencies.
- Accounting policy config: tolerances, rounding, adjustment policy.

Config rules:

- Required keys must fail startup validation when missing.
- Optional keys must have explicit defaults in schema.
- Config values are read at startup and bound into a typed config object.
- Dynamic reload is allowed only for approved non-critical sections.

Session configuration freeze:

- At close-session start, persist a resolved config snapshot.
- Use the snapshot for all stage execution in that session.
- Do not switch policy values mid-session without explicit operator restart.

Config precedence:

- Session override config
- Environment config
- Default config

Secrets handling:

- Secrets are referenced by config key and secure file path or environment variable.
- Secrets and cloud unique identifiers are never embedded in source-controlled docs or configs.

## Parameterization guidelines

Parameterization must make behavior explicit and testable while avoiding unconstrained runtime variability.

Parameter categories:

- Stage parameters: `stage_key`, `run_mode`, `account_group_key`.
- Reconciliation parameters: `tolerance_amount`, `method_class`, `override_reason`.
- Source ingest parameters: `source_profile_key`, `encoding_key`, `date_format_key`.
- Publish parameters: `artifact_format`, `renderer_key`, `publish_target_key`.

Parameter design rules:

- Prefer enumerated values over free-text for behavioral switches.
- Validate parameter ranges and allowed values at boundaries.
- Do not allow unsafe direct SQL fragments as route or config parameters.
- Use explicit defaults for optional parameters and document them.
- Persist effective parameter sets in stage run audit records.

Parameter consistency:

- Keep parameter names consistent across API payloads, config keys, and log fields.
- If aliasing is unavoidable, define one canonical name and translate only at boundary.

## SQL and SQLite

SQLite is the primary persistence layer. All app schemas are housed in a single database file.

Query construction:

Always use parameterized queries. Never concatenate user-supplied or external values into a SQL string. Use named parameters (`?` or `:name`) consistently within a file -- do not mix styles.

Example of safe parameterized query:

```python
cursor.execute(
    "SELECT * FROM account WHERE id = :account_id",
    {"account_id": account_id}
)
```

Schema conventions:

Use singular snake_case table names. Use `id` as the surrogate primary key on every table. Name foreign keys as `<referenced_table>_id`. Avoid SQL reserved words as identifiers.

Add `created_at` and `updated_at` timestamp columns to tables that track mutable state. Store all timestamps as UTC ISO-8601 strings.

Backend-neutral adapter contract:

- SQL adapter public methods must not expose SQLite-only behavior.
- Adapter methods should represent domain persistence actions, not caller-constructed SQL.
- Transaction semantics must stay stable if the adapter backend changes from SQLite to cloud SQL.

Migrations:

Version schema changes incrementally. Never alter a deployed schema by dropping and re-creating tables manually outside a migration script. Keep migration scripts in source control under `src/db/migrations/`.

Indexes:

Add explicit indexes on columns used in WHERE clauses for period-scoped queries, for example `account_id`, `period_date`, and `source`. Do not over-index -- each index has a write cost.

## Financial precision

Financial values require exact decimal representation. Floating-point arithmetic is not acceptable for any monetary amount, balance, or rate field.

Storage:

Store currency amounts as integer cents where the currency has two decimal places (SGD, USD). Store amounts for currencies with other conventions using the appropriate minor unit integer. The column name must carry a currency suffix when the currency is not implicit from context, for example `amount_sgd_cents`.

Alternatively, use a `NUMERIC` or `TEXT` column with a fixed decimal string to preserve exact precision. Whichever approach is chosen, apply it consistently within each schema.

Python arithmetic:

Use Python `decimal.Decimal` for all financial calculations. Never use `float`. Set a consistent rounding context at module initialization and document the precision and rounding mode.

Example:

```python
from decimal import Decimal, ROUND_HALF_UP

CURRENCY_PRECISION = Decimal("0.01")

def round_amount(amount: Decimal) -> Decimal:
    return amount.quantize(CURRENCY_PRECISION, rounding=ROUND_HALF_UP)
```

Forex rates:

Store exchange rates with sufficient decimal places to avoid compounding rounding errors during conversion -- a minimum of 6 decimal places. Apply rounding only at the final output step, not at intermediate calculation steps.

Variance tolerance:

Tolerance values for reconciliation checks are defined in requirements and must be stored as `Decimal` constants. Do not hardcode tolerance values inline -- define them as named constants with the currency they apply to.

## Google Sheets adapter

Google Sheets reads and writes must go through a dedicated adapter module that owns direct Google SDK interactions.

Adapter design:

- Convert named ranges and sheet metadata to canonical payloads.
- Batch reads and writes to minimize API round trips.
- Apply retry and backoff policy from config.
- Normalize Google API errors to app error taxonomy.

Boundary rules:

- Domain and orchestration modules do not call Google SDK directly.
- GAS usage is optional and limited to selected click-trigger scenarios.
- IMPORTRANGE stays a sheet-native behavior and is not represented as adapter API.

## HomeBudget adapter

HomeBudget access must be routed through the HomeBudget wrapper adapter.

- No direct HomeBudget DB writes outside wrapper boundary.
- Writes require approved workflow stage outcomes.
- Wrapper write results must be recorded in audit logs with correlation ids.

## PDF generation

PDF generation is a publish-stage requirement.

- ReportLab is the required renderer.
- WeasyPrint is optional behind the same PDF renderer adapter contract.
- Renderer selection must be config-driven with `renderer_key` values.
- Publish closure requires successful PDF generation before artifact upload and finalization.

## Google Sheets

Google Sheets serves as the primary session UI and as a source for cash expense data and legacy mapping artifacts.

Workbook and sheet tab naming:

Use lowercase kebab-case for workbook config file names, for example `closing-session.json`. Use human-readable title case for sheet tab names that appear in the UI, for example `Reconcile Summary`. Use snake_case for programmatic named ranges, for example `reconcile_summary_range`.

Named range conventions:

Define named ranges for all ranges that the Python adapter reads or writes. Do not hardcode cell addresses in Python source code. Named ranges act as a stable contract between the spreadsheet layout and the adapter.

Formula conventions:

Keep formulas that the app depends on as simple as possible. Complex multi-step calculations that the app must interpret should be moved to Python domain logic. Google Sheets formulas are appropriate for display formatting, conditional highlighting, and lightweight aggregations for the user UI.

API interaction:

Use direct Google SDK integration in the Google Sheets adapter. Batch read and write operations to minimize API round trips. Respect Google API rate limits by applying exponential backoff on retry.

## PowerShell CLI

PowerShell scripts run on Windows 11 and serve as the local automation layer for invoking backend workflows, managing the virtual environment, and scripting batch operations.

Script naming:

Use kebab-case for script file names, for example `run-monthly-close.ps1`. Use `Verb-Noun` for function names inside scripts, following PowerShell approved verb conventions, for example `Invoke-MonthlyClose`, `Get-PeriodInputs`.

Parameters:

Use `-PascalCase` for script and function parameter names following PowerShell convention, for example `-StatementDate`, `-CommitMode`. Provide `[Parameter(Mandatory)]` annotations for required parameters. Document parameter purpose with inline comments.

Exit codes:

Scripts must exit with code `0` on success and a non-zero code on failure. Use `exit 1` for user input errors and `exit 2` for system-level failures. Do not swallow errors silently -- let them propagate unless a specific recovery path is coded.

Environment activation:

Scripts that invoke Python must activate the virtual environment at `env/Scripts/Activate.ps1` before calling any Python commands. Set execution policy to `RemoteSigned` at process scope.

Output:

Use `Write-Output` for data that downstream scripts or the pipeline may consume. Use `Write-Host` only for user-facing status messages that should not be captured by redirection. Use `Write-Error` for error messages.

## Error handling

Errors follow a layered taxonomy defined in the error handling design.

Raise early, catch late:

Validate inputs and raise errors at the boundary where data enters the system. Let errors propagate up through domain logic without intermediate catching. Catch and handle errors at the orchestration or CLI layer where a meaningful recovery or user message is possible.

Specificity:

Raise the most specific error class available. Never swallow exceptions with an empty `except` or `catch` block. Log the exception before re-raising or handling it.

Financial workflow errors:

Reconciliation variances, posting failures, and data quality failures must result in a named error class from the error taxonomy -- not a generic runtime exception. This ensures the workflow runner can classify the failure and determine the correct recovery path.

User-facing messages:

Error messages surfaced to the user in the CLI or UI must be plain English and actionable. Do not expose raw stack traces or internal variable names in user-facing output. Log the full error detail to the session log.

## Layer boundaries

The app follows a three-layer architecture: adapters at the base, domain logic in the middle, and orchestration at the top.

Dependency direction:

Dependencies flow downward only. Orchestration calls domain. Domain calls adapters. Adapters never call domain or orchestration modules. Domain modules never call orchestration modules.

Adapter isolation:

Adapters are responsible for all external I/O: HomeBudget reads, Google Sheets reads and writes, SQLite persistence, CSV parsing, and forex API calls. Domain modules must not contain direct database queries, file reads, or API calls. Pass canonical data contracts across the boundary.

Canonical contracts:

Use the canonical data contract types defined in the data flow design as the interchange format between layers. Adapters translate external formats to canonical types on the way in and from canonical types to external formats on the way out. Domain modules operate exclusively on canonical types.

No circular imports:

Circular module imports are a sign of a boundary violation. Resolve them by moving shared definitions to a separate types or constants module, not by reordering imports.

## Logging

Structured logging supports audit trails and session replay for monthly close operations.

Log levels:

Use `DEBUG` for detailed internal state during development. Use `INFO` for normal workflow progress events. Use `WARNING` for recoverable anomalies such as missing optional config or a retried API call. Use `ERROR` for failures that block a workflow step. Use `CRITICAL` for failures that require immediate user intervention.

Structure:

Log entries must include at minimum: timestamp, level, module name, and a message string. For workflow step events, also include the period date and the stage name. For financial decision events, include the account identifier and the variance amount.

Auditability:

Every HomeBudget write, Google Sheets write, and reconciliation decision must produce a log entry at `INFO` level or above. This log is the primary audit trail for the monthly close.

No sensitive values in logs:

Do not log credentials, API keys, raw bank statement rows with account numbers, or personal financial details beyond what is required for audit tracing. Log account identifiers and aggregated amounts rather than individual transaction details where possible.

## Secrets and credentials

Never in source control:

Credentials, OAuth tokens, API keys, Google service account JSON files, and workbook IDs must never appear in committed source code, config files, or documentation. Reference the key name and the file path or environment variable where the value is stored.

Local storage:

Store secrets in a local file outside the repository root, or in a dedicated secrets directory that is covered by `.gitignore`. Document the required file names and key structure in a `docs/` reference without including the values themselves.

Google Sheets credentials:

The Google service account credentials file path is configured via the `gsheet` config files under `gsheet/`. The credentials file itself is not committed. Refer to the gsheet inspection skill for the expected file location and structure.

Workbook IDs:

Google Sheets workbook IDs are cloud resource unique identifiers. Do not write them in documentation or config files committed to source control. Reference the config key and config file path where the value is stored at runtime.
