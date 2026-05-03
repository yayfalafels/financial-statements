---
name: google-sheets-api
description: Use when working on reusable Google Sheets API concepts, batch updates, named range handling, and python client usage for direct sheet integrations.
---

# Google Sheets API

## Summary

Use this skill for reusable Google Sheets API knowledge. Keep workbook-specific range choices and project-specific sheet ownership in the agent file.

## Apply This Skill When

- Reading or writing spreadsheet data through the Sheets API.
- Using `spreadsheets.values` or `spreadsheets.batchUpdate` operations.
- Handling spreadsheet IDs, sheet IDs, A1 notation, and named ranges.
- Using the Python Google API client for Sheets operations.

## Rules

- Prefer stable named ranges or governed config keys over hardcoded coordinates in application logic.
- Use `batchUpdate` for structural or formatting changes and grouped dependent operations.
- Use explicit field masks for partial update requests.
- Keep spreadsheet identity and auth material out of source-controlled constants.
- Batch requests when possible to reduce round trips and rate-limit pressure.

## Official Sources

- Sheets API concepts: https://developers.google.com/workspace/sheets/api/guides/concepts
  This defines spreadsheet IDs, sheet IDs, A1 notation, R1C1 notation, cells, and named ranges.
- Sheets API batch updates: https://developers.google.com/workspace/sheets/api/guides/batchupdate
  `spreadsheets.batchUpdate` groups dependent updates and applies them atomically, so one failed request prevents partial structural changes.
- Python client reference: https://googleapis.github.io/google-api-python-client/docs/dyn/sheets_v4.html
  The Python client exposes the `spreadsheets()` resource plus batch helpers and connection-closing behavior.

## Useful Takeaways

- Spreadsheet IDs and sheet IDs are stable identifiers and should be treated as config values, not inferred labels.
- `batchUpdate` is for spreadsheet structure and non-value operations; plain value reads and writes belong on the values resource.
- Field masks matter because `*` can reset unspecified fields to defaults.

## Validation Focus

- The code uses the right API surface for value versus structural changes.
- Range references are stable and governed.
- Batch operations are grouped only when atomicity is desired.
- Authentication and workbook selection remain config-driven.