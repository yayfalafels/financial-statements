# Google Sheets Source Data Guide

This guide documents Google Sheets source-data references used by requirements
and inspection work. It is not a tool usage guide.

## Boundary

- Use this guide for source-data file and region references.
- Use `gsheet-inspect` skill for procedural inspection steps, script usage, and troubleshooting.

## Source Artifacts

- Credentials file: `.credentials/client_secret.json`
- Workbook configs: `gsheet/*.json`
- HomeBudget workbook config: `gsheet/homebudget-workbook.json`
- CPF workbook config: `gsheet/cpf.json`
- IBKR workbook config: `gsheet/ibkr-iba.json`
- Financial statements workbook config: `gsheet/financial-statements.json`

## Helper Schema Inspection Mapping

The table below maps source configs to the currently documented helper script path for schema profiling.

Helper script prefix: `.dev/scripts/python/`

| id            |                                    |                             |                        |
| ------------- | ---------------------------------- | --------------------------- | ---------------------- |
| source config |                                    |                             |                        |
| helper        |                                    |                             |                        |
| notes         |                                    |                             |                        |
| 01            | `gsheet/ibkr-iba.json`             | `inspect_helper_schemas.py` | primary multi-workbook |
| 02            | `gsheet/cpf.json`                  | `inspect_helper_schemas.py` | primary multi-workbook |
| 03            | `gsheet/homebudget-workbook.json`  | `inspect_helper_schemas.py` | primary multi-workbook |
| 04            | `gsheet/financial-statements.json` | `inspect_helper_schemas.py` | included in helper     |
| 05            | `gsheet/cash-expenses.json`        | `inspect_helper_schemas.py` | included in helper     |
| 06            | `gsheet/shared-expenses.json`      | `inspect_helper_schemas.py` | included in helper     |
| 07            | `gsheet/closing-session.json`      | `inspect_helper_schemas.py` | included in helper     |

For execution procedure, command patterns, and troubleshooting, use skill `gsheet-inspect`.

## Required Config Fields

- `wkbid`: workbook identifier.
- Region keys: named data regions used by inspection scripts.
- `header`: A1 notation for header rows.
- `data`: A1 notation for data ranges.

## Key Mapping Data Regions

- `cat_map` in `homebudget-workbook.json`: HomeBudget category to GL mapping source.
- Reconcile-oriented regions in helper configs: source references for parity checks and extraction tasks.
