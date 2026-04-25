---
title: Design Guidelines
version: 2.0
last_updated: 2026-04-25
---

# Design Guidelines

## Summary

Guidelines and policies that apply broadly across app design. These conventions govern naming, structure, and data flow decisions across Python source code, SQL schema, JSON config, Google Sheets UI, PowerShell CLI scripts, and Node.js backend and browser-based UI layers.

## Table of contents

- [Variable names](#variable-names)
- [Kebab-case](#kebab-case)
- [Pass-through](#pass-through)
- [Python](#python)
- [SQL and SQLite](#sql-and-sqlite)
- [Financial precision](#financial-precision)
- [JSON config](#json-config)
- [Google Sheets](#google-sheets)
- [PowerShell CLI](#powershell-cli)
- [Node.js](#nodejs)
- [Error handling](#error-handling)
- [Layer boundaries](#layer-boundaries)
- [Logging](#logging)
- [Secrets and credentials](#secrets-and-credentials)

## Variable names

Follow Python PEP guidelines for intuitive variable names using plain English. Aim to be as close as possible to the underlying meaning. Names should be brief and concise -- avoid excessively long variable names.

**Subject-verb ordering**

Order variable and function names as subject-attribute or subject-verb, for example `statement_close` rather than `close_statement`. This aligns naming with the OOP implementation pattern of `<class>.<method>` and `<class>.<attribute>`, making names portable when migrated to a class-based design.

**Platform conventions**

- Python variables and functions: `lowercase_with_underscores`
- Python classes: `CapWords`
- Python constants: `UPPERCASE`
- SQL table and column names: `singular_snake_case`
- JSON and config keys: `lowercase_with_underscores`
- Node.js variables and functions: `lowerCamelCase`
- Node.js classes: `UpperCamelCase`
- Node.js constants: `UPPER_SNAKE_CASE`

For additional naming rules covering SQL keys, boolean prefixes, timestamp suffixes, enum values, and approved abbreviations, refer to the variable-naming skill in `.github/skills/variable-naming/SKILL.md`.

## Kebab-case

Use lowercase kebab-case for names that appear in file names, URL slugs, and CLI parameters -- for example `statement-date`. Where the platform or runtime prohibits hyphens, replace the hyphen with an underscore -- for example `statement_date` in SQL or Python.

## Pass-through

Minimize arbitrary variations in variable names as a concept passes through the app from front-end through source code to the back-end data model. When the same concept travels across layers, keep the name identical or as close as possible.

**Example**

- UI field label: `statement_date`
- Python variable: `statement_date`
- SQL column: `statement_date`
- Node.js API field: `statementDate` (lowerCamelCase is the only permitted variation, required by JavaScript platform convention)

When a name variation is required by a platform constraint, document the mapping explicitly in the relevant design artifact. Do not introduce a new name simply for stylistic variety.

## Python

Python 3.12 is the runtime for all backend logic, adapter modules, CLI commands, and domain processing.

**Code style**

Follow PEP 8 as the baseline. Readability takes priority over brevity. Use 4-space indentation. Limit lines to 99 characters in Python source files. Prefer implicit line continuation inside parentheses over backslash continuation.

**Imports**

Order imports in three groups separated by a blank line: standard library, third-party packages, local modules. Use absolute imports. Never use wildcard imports (`from module import *`).

**Functions and methods**

Keep functions focused on a single responsibility. Prefer explicit positional arguments for required parameters. Use keyword-only arguments for optional configuration values. Avoid `*args` and `**kwargs` unless the function is a pass-through or decorator.

Use `with` statements for all file and database connection handling to guarantee cleanup.

**Exceptions**

Catch the most specific exception type available. Never use a bare `except:` clause. Use `raise X from Y` when re-raising to preserve the original traceback. Derive custom app exceptions from `Exception`, not `BaseException`.

**Type hints**

Use type hints for all public module interfaces -- function signatures and return types. Type hints on internal helpers are optional. Avoid complex generic types where a clear docstring conveys intent more directly.

**Module structure**

Group each module by: module-level constants, public classes, public functions, private helpers. Place imports at the top of every file, before any executable code.

## SQL and SQLite

SQLite is the primary persistence layer. All app schemas are housed in a single database file.

**Query construction**

Always use parameterized queries. Never concatenate user-supplied or external values into a SQL string. Use named parameters (`?` or `:name`) consistently within a file -- do not mix styles.

Example of safe parameterized query:

```python
cursor.execute(
    "SELECT * FROM account WHERE id = :account_id",
    {"account_id": account_id}
)
```

**Schema conventions**

Use singular snake_case table names. Use `id` as the surrogate primary key on every table. Name foreign keys as `<referenced_table>_id`. Avoid SQL reserved words as identifiers.

Add `created_at` and `updated_at` timestamp columns to tables that track mutable state. Store all timestamps as UTC ISO-8601 strings.

**Migrations**

Version schema changes incrementally. Never alter a deployed schema by dropping and re-creating tables manually outside a migration script. Keep migration scripts in source control under `src/db/migrations/`.

**Indexes**

Add explicit indexes on columns used in WHERE clauses for period-scoped queries, for example `account_id`, `period_date`, and `source`. Do not over-index -- each index has a write cost.

## Financial precision

Financial values require exact decimal representation. Floating-point arithmetic is not acceptable for any monetary amount, balance, or rate field.

**Storage**

Store currency amounts as integer cents where the currency has two decimal places (SGD, USD). Store amounts for currencies with other conventions using the appropriate minor unit integer. The column name must carry a currency suffix when the currency is not implicit from context, for example `amount_sgd_cents`.

Alternatively, use a `NUMERIC` or `TEXT` column with a fixed decimal string to preserve exact precision. Whichever approach is chosen, apply it consistently within each schema.

**Python arithmetic**

Use Python `decimal.Decimal` for all financial calculations. Never use `float`. Set a consistent rounding context at module initialization and document the precision and rounding mode.

Example:

```python
from decimal import Decimal, ROUND_HALF_UP

CURRENCY_PRECISION = Decimal("0.01")

def round_amount(amount: Decimal) -> Decimal:
    return amount.quantize(CURRENCY_PRECISION, rounding=ROUND_HALF_UP)
```

**Forex rates**

Store exchange rates with sufficient decimal places to avoid compounding rounding errors during conversion -- a minimum of 6 decimal places. Apply rounding only at the final output step, not at intermediate calculation steps.

**Variance tolerance**

Tolerance values for reconciliation checks are defined in requirements and must be stored as `Decimal` constants. Do not hardcode tolerance values inline -- define them as named constants with the currency they apply to.

## JSON config

JSON files serve as configuration carriers for workbook definitions, account mappings, period inputs, and session state sidecars.

**Structure**

Use flat or shallow structures where possible. Avoid deeply nested objects. Group related keys under a named object rather than using long compound key names.

**Keys**

Use `lowercase_with_underscores` for all JSON keys consistent with Python variable naming. Do not use camelCase in JSON config files even when the consumer is Node.js -- the adapter layer is responsible for translating key format.

**Required vs optional**

Document required keys explicitly at the top of any config schema definition. Required keys must cause a `ConfigError` at startup if absent. Optional keys must have documented defaults.

**Secrets**

Never store credentials, API keys, OAuth tokens, or workbook IDs in JSON config files that are committed to source control. Reference the key name and file path where the value is stored. See [Secrets and credentials](#secrets-and-credentials).

## Google Sheets

Google Sheets serves as the primary session UI and as a source for cash expense data and legacy mapping artifacts.

**Workbook and sheet tab naming**

Use lowercase kebab-case for workbook config file names, for example `closing-session.json`. Use human-readable title case for sheet tab names that appear in the UI, for example `Reconcile Summary`. Use snake_case for programmatic named ranges, for example `reconcile_summary_range`.

**Named range conventions**

Define named ranges for all ranges that the Python adapter reads or writes. Do not hardcode cell addresses in Python source code. Named ranges act as a stable contract between the spreadsheet layout and the adapter.

**Formula conventions**

Keep formulas that the app depends on as simple as possible. Complex multi-step calculations that the app must interpret should be moved to Python domain logic. Google Sheets formulas are appropriate for display formatting, conditional highlighting, and lightweight aggregations for the operator UI.

**API interaction**

Use the `sqlite-gsheet` package for reads and writes where it is compatible. Batch read and write operations to minimize API round trips. Respect Google Sheets API rate limits by catching `ExternalApiError` and applying exponential backoff on retry.

## PowerShell CLI

PowerShell scripts run on Windows 11 and serve as the local automation layer for invoking backend workflows, managing the virtual environment, and scripting batch operations.

**Script naming**

Use kebab-case for script file names, for example `run-monthly-close.ps1`. Use `Verb-Noun` for function names inside scripts, following PowerShell approved verb conventions, for example `Invoke-MonthlyClose`, `Get-PeriodInputs`.

**Parameters**

Use `-PascalCase` for script and function parameter names following PowerShell convention, for example `-StatementDate`, `-CommitMode`. Provide `[Parameter(Mandatory)]` annotations for required parameters. Document parameter purpose with inline comments.

**Exit codes**

Scripts must exit with code `0` on success and a non-zero code on failure. Use `exit 1` for user input errors and `exit 2` for system-level failures. Do not swallow errors silently -- let them propagate unless a specific recovery path is coded.

**Environment activation**

Scripts that invoke Python must activate the virtual environment at `env/Scripts/Activate.ps1` before calling any Python commands. Set execution policy to `RemoteSigned` at process scope.

**Output**

Use `Write-Output` for data that downstream scripts or the pipeline may consume. Use `Write-Host` only for operator-facing status messages that should not be captured by redirection. Use `Write-Error` for error messages.

## Node.js

Node.js serves as the backend runtime for the browser-based guided workflow UI.

**Language style**

Use `const` over `let`. Never use `var`. Use arrow functions for callbacks and inline handlers. Use `async/await` for all asynchronous operations. Avoid raw Promise chains and callbacks. Always `await` a Promise before returning it to preserve full stack traces on rejection.

**Naming**

Use `lowerCamelCase` for variables and functions. Use `UpperCamelCase` for classes. Use `UPPER_SNAKE_CASE` for module-level constants. Use kebab-case for file and directory names under `src/`.

**Module structure**

Place all imports at the top of the file before any executable code. Export only the public interface of a module -- keep internal helpers unexported. Use named exports over default exports in shared modules.

**API design**

Use RESTful route conventions with kebab-case URL paths, for example `/api/closing-session`. Return consistent response shapes across all endpoints. Include an explicit status field in error responses. Validate all request payloads at the entry point before passing data into domain logic.

**Async error handling**

Wrap route handlers in a shared error-handling wrapper or use a framework middleware that catches unhandled promise rejections. Never let unhandled rejections propagate silently. Register a `process.on('unhandledRejection')` handler at the process level as a safety net.

**TypeScript**

Use TypeScript for shared data contract types and API request and response shapes. Keep type definitions simple -- use plain interfaces and type aliases. Avoid complex generic types and type-level programming that obscures rather than clarifies intent.

## Error handling

Errors follow a layered taxonomy defined in the error handling design. The conventions below apply across Python and Node.js.

**Raise early, catch late**

Validate inputs and raise errors at the boundary where data enters the system. Let errors propagate up through domain logic without intermediate catching. Catch and handle errors at the orchestration or CLI layer where a meaningful recovery or user message is possible.

**Specificity**

Raise the most specific error class available. Never swallow exceptions with an empty `except` or `catch` block. Log the exception before re-raising or handling it.

**Financial workflow errors**

Reconciliation variances, posting failures, and data quality failures must result in a named error class from the error taxonomy -- not a generic runtime exception. This ensures the workflow runner can classify the failure and determine the correct recovery path.

**User-facing messages**

Error messages surfaced to the operator in the CLI or UI must be plain English and actionable. Do not expose raw stack traces or internal variable names in operator-facing output. Log the full error detail to the session log.

## Layer boundaries

The app follows a three-layer architecture: adapters at the base, domain logic in the middle, and orchestration at the top.

**Dependency direction**

Dependencies flow downward only. Orchestration calls domain. Domain calls adapters. Adapters never call domain or orchestration modules. Domain modules never call orchestration modules.

**Adapter isolation**

Adapters are responsible for all external I/O: HomeBudget reads, Google Sheets reads and writes, SQLite persistence, CSV parsing, and forex API calls. Domain modules must not contain direct database queries, file reads, or API calls. Pass canonical data contracts across the boundary.

**Canonical contracts**

Use the canonical data contract types defined in the data flow design as the interchange format between layers. Adapters translate external formats to canonical types on the way in and from canonical types to external formats on the way out. Domain modules operate exclusively on canonical types.

**No circular imports**

Circular module imports are a sign of a boundary violation. Resolve them by moving shared definitions to a separate types or constants module, not by reordering imports.

## Logging

Structured logging supports audit trails and session replay for monthly close operations.

**Log levels**

Use `DEBUG` for detailed internal state during development. Use `INFO` for normal workflow progress events. Use `WARNING` for recoverable anomalies such as missing optional config or a retried API call. Use `ERROR` for failures that block a workflow step. Use `CRITICAL` for failures that require immediate operator intervention.

**Structure**

Log entries must include at minimum: timestamp, level, module name, and a message string. For workflow step events, also include the period date and the stage name. For financial decision events, include the account identifier and the variance amount.

**Auditability**

Every HomeBudget write, Google Sheets write, and reconciliation decision must produce a log entry at `INFO` level or above. This log is the primary audit trail for the monthly close.

**No sensitive values in logs**

Do not log credentials, API keys, raw bank statement rows with account numbers, or personal financial details beyond what is required for audit tracing. Log account identifiers and aggregated amounts rather than individual transaction details where possible.

## Secrets and credentials

**Never in source control**

Credentials, OAuth tokens, API keys, Google service account JSON files, and workbook IDs must never appear in committed source code, config files, or documentation. Reference the key name and the file path or environment variable where the value is stored.

**Local storage**

Store secrets in a local file outside the repository root, or in a dedicated secrets directory that is covered by `.gitignore`. Document the required file names and key structure in a `docs/` reference without including the values themselves.

**Google Sheets credentials**

The Google service account credentials file path is configured via the `gsheet` config files under `gsheet/`. The credentials file itself is not committed. Refer to the gsheet inspection skill for the expected file location and structure.

**Workbook IDs**

Google Sheets workbook IDs are cloud resource unique identifiers. Do not write them in documentation or config files committed to source control. Reference the config key and config file path where the value is stored at runtime.
