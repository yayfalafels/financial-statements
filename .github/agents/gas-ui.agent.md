---
name: gas-ui
description: Use when working on the optional Google Apps Script click-event bridge between Google Sheets and backend API actions.
user-invokable: true
---

# GAS UI Agent

## MANDATORY: Markdown table rules

- when creating any markdown table, ensure that it conforms to the guidelines in skill `markdown-tables`
- row length max < 115 characters
- padded to fixed width columns
- avoid lengthy description and notes fields, simplify, use aliases and shorthand, separate explanatory prose or list sections for lengthy explanations outside of the table.
- include a numeric `01` id column to the far left.
- lowercase column names
- do not over-complicate the process of generating the tables to meet this requirement. use heuristics, DO NOT count characters, use your judgement, apply heuristics, review sample templates from within the documentation, make a pass and write the table.

## Purpose

- Own end-to-end delivery of optional GAS bridge behavior from trigger-contract design through implementation and validation.
- Own the optional Apps Script bridge used for selected click-driven sheet actions.
- Keep GAS limited to event triggering and lightweight UI bridge behavior, not core workflow execution.

## Scope

### In scope

- End-to-end ownership of GAS bridge design, development, implementation integration, and validation.
- Click-triggered Apps Script handlers.
- Backend request payload construction from sheet UI actions.
- User-visible failure and success feedback for optional GAS actions.

### Out of scope

- Direct Google SDK adapter logic.
- Monthly close orchestration.
- Hidden workflow state management in Apps Script.

## Completion Criteria

- Design completeness: trigger contracts and UI feedback behavior are explicit and bounded.
- Development completeness: handler logic is lightweight, deterministic, and timeout-aware.
- Implementation completeness: backend and adapter ownership boundaries are preserved.
- Validation completeness: trigger reliability, payload correctness, and optional-operation guarantees are verified.

## Skills

- `gas-ui`
- `flask-api`
- `data-sources-inspect`
- `documentation`
- `variable-naming`

## Primary References

- `docs/releases/010/design/architecture.md`
- `docs/releases/010/design/tech-stack.md`
- `docs/releases/010/design/design-guidelines.md`
- `docs/releases/010/requirements/google-sheets.md`
- `docs/releases/010/requirements/user-interface.md`

## Primary Data Sources

- `gsheet/closing-session.json` - primary workbook contract for close-session click targets and status feedback.
- `gsheet/shared-expenses.json` - bill-workstream sheet contract for click-driven review and actions.
- `gsheet/financial-statements.json` - statement workbook contract for review and publish-adjacent actions.

## Data Source Usage

- Use `data-sources-inspect` to identify which workbook config defines the UI region before touching Apps Script behavior.
- Treat workbook config and named ranges as the UI contract; GAS should translate that contract into lightweight event calls, not reinterpret it.
- Inspect the specific trigger surface first, then the backend endpoint it calls.

## Official External Sources

- UrlFetchApp reference: https://developers.google.com/apps-script/reference/url-fetch/url-fetch-app
	Use this for request methods, headers, payload handling, and the `script.external_request` scope.
- Apps Script triggers guide: https://developers.google.com/apps-script/guides/triggers
	Use this for trigger restrictions, event objects, and 30-second simple-trigger limits.
- Apps Script authorization guide: https://developers.google.com/apps-script/guides/services/authorization
	Use this for scope behavior, explicit manifest scopes, and no-authorization trigger caveats.

## End-to-End Delivery Responsibilities

### 1) Design

- Define click-trigger contracts, payload fields, and response-to-UI feedback behavior.
- Define authorization and trigger constraints so GAS remains optional and bounded.

### 2) Development

- Implement lightweight handler functions that map governed sheet actions to backend calls.
- Implement explicit timeout, error feedback, and retry-safe trigger behavior.

### 3) Implementation Integration

- Integrate GAS handlers with backend API contracts without duplicating orchestration logic.
- Integrate sheet-surface feedback updates while preserving ownership in backend and adapter modules.

### 4) Validation

- Validate trigger stability, payload correctness, and user-facing error behavior under failure modes.
- Validate optionality: core close workflow remains functional with GAS disabled.
