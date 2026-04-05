# Google Sheets

This page defines requirement-level boundaries for Google Sheets usage in the project.

Detailed inspection and implementation procedures are maintained in the Google Sheets inspection skill guide:

- skill `gsheet-inspect`

For source-data structure and workbook reference details that are not tool procedures, use:

- docs/develop/data-sources/google-sheets-source-data.md

## Scope in Requirements

Google Sheets is used as a helper and reference source for:

- Category and mapping artifacts required during requirements and parity workflows.
- Supporting workbook-based validation in non-production modes.
- Controlled extraction of legacy mappings for documentation and migration.

This page intentionally avoids duplicating script-level or API-level execution steps. Those steps belong in the skill guides.

## Procedural Source of Truth

When execution details are needed, use the following precedence:

1. skill `gsheet-inspect`
2. skill `data-sources-inspect`
3. This requirement page for scope and acceptance boundaries only
