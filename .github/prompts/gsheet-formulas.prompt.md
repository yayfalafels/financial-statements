---
name: gsheet-formulas-workflow
description: Reusable workflow prompt to deliver 02.14.18 gsheet-formulas from requirements through design, development, SIT, and UAT with artifact traceability.
---

# Gsheet Formulas Workflow Prompt

## Contents

- Overview
- Scope
- Required Skills
- Artifact Boundaries
- Objectives
- Reference Documents
- Main Task Mirror
- Phase Guidance
- Evidence and Validation Policy
- Human-Agent Interaction and Handoff
- Workflow Loop
- Quality Checklist
- Completion Gate

## Overview

This prompt guides end-to-end delivery for the Google Sheets formula CRUD utility.

The workflow is release `010` focused and keeps requirements, design, implementation, and validation artifacts in their correct destinations.

This prompt is a reusable process artifact, not the final destination for runtime source code or dynamic tracker evidence.

## Sensitive values and cloud resource identifiers

- Do not write secrets or cloud resource unique identifiers in documentation.
- Reference the config key and config file path where the value is stored.
- Google Sheets workbook IDs are cloud resource unique identifiers and must not be written literally.
- Temporary exception is allowed only when the secret or config file does not exist yet. Mark it as temporary, track it explicitly, and close it as soon as the config or secret store is created.

## Scope

In scope for this workflow:

- CRUD capabilities for formulas in Google Sheets cells/ranges.
- Input handling for client secret file, workbook ID, and A1 range.
- Documentation and delivery artifacts listed in the tracker.
- SIT and UAT evidence sufficient for release recommendation.

Out of scope unless explicitly approved:

- non-formula spreadsheet operations outside this utility scope
- major platform refactors unrelated to formula CRUD
- MVP or post-POC feature expansion

## Completion Gate

This workflow is complete when:

- all required output files exist and are populated for current scope
- 02.14.18 phase tasks are closed with evidence in tracker
- SIT and UAT outcomes support release recommendation
- deferred items and risks are documented with clear ownership

## Quality Checklist

- Requirement statements are specific and testable.
- Design decisions are traceable to requirements.
- Tests map to requirement acceptance criteria.
- Tracker statuses reflect actual artifact state.
- Tables are fixed-width and concise.
- SIT/UAT evidence is reproducible and stored in docs.

## Required Skills

Use these skills when drafting and validating artifacts.

- `task-definition` for task status and closure updates in `docs/develop/010/project-management/gsheet-formulas.md`
- `documentation` for requirements, design, and user-guide quality
- `markdown-tables` for fixed-width tracker tables and compact status reporting
- `python` for implementation and test-support scripting
- `gsheet-inspect` for workbook and range validation patterns
- `variable-naming` for consistent naming across docs and code

## Artifact Boundaries

- Requirements destination: `docs/tools/gsheet-formulas/requirements.md`
- Design destination: `docs/tools/gsheet-formulas/design.md`
- User guide destination: `docs/tools/gsheet-formulas/user-guide.md`
- Task tracking destination: `docs/develop/010/project-management/gsheet-formulas.md`
- Workflow prompt destination: `.github/prompts/gsheet-formulas.prompt.md`
- Source code destination: `src/gsheet-formulas/*`
- Chat responses are coordination only and are not completion artifacts.

## Objectives

- Define complete, testable requirements for formula CRUD behavior.
- Produce a design that is implementation-ready with minimal ambiguity.
- Implement reliable formula CRUD commands with clear error handling.
- Validate behavior through SIT and operator-focused UAT.
- Maintain traceability across requirements, design, tests, and tracker status.

## Reference Documents

- `docs/develop/010/project-management/gsheet-formulas.md`
- `docs/requirements/google-sheets.md`
- `gsheet/*.json`

## Evidence and Validation Policy

Before asking for user decisions, inspect existing artifacts and available source evidence first.

Evidence should include, where applicable:

- requirement/design/user-guide drafts
- tracker status and dependency/risk sections
- workbook config context in `gsheet/*.json`
- implementation and test outputs from local runs

Ask user questions only when ambiguity remains after source inspection.

## Human-Agent Interaction and Handoff

### Agent Can Execute Autonomously

1. Create and refine prompt, tracker, and docs artifacts.
2. Update task statuses when closure evidence is present.
3. Draft requirements, design sections, and test strategy content.
4. Implement source and tests aligned with approved design.

### Agent Must Request User Input

1. Business-rule ambiguity for formula semantics remains unresolved.
2. Scope change is implied beyond release `010`.
3. Risk acceptance is required for unresolved SIT/UAT defects.

### What to Provide When Asking

1. Exact decision required.
2. Current evidence and options.
3. Recommended default and impact.
4. A concise question using `vscode_askQuestions` when needed.

## Workflow Loop

1. Confirm active phase and target artifact.
2. Inspect source docs, tracker state, and dependencies.
3. Draft or update target artifact.
4. Validate against checklist and acceptance criteria.
5. Record closure evidence in tracker.
6. Move next phase from pending to open.

## Main Task Mirror

Mirror this table from `docs/develop/010/project-management/gsheet-formulas.md` and keep status updates in that tracker file.

| seq | id          | status  | phase                       | task                                      |
| --- | ----------- | ------- | --------------------------- | ----------------------------------------- |
| 01  | 02.14.18.08 | open    | development docs            | draft dev docs 04 task tracker and 05 dev workflow |
| 02  | 02.14.18.01 | pending | requirements                | finalize requirements and acceptance criteria |
| 03  | 02.14.18.02 | pending | test strategy               | define verification approach, coverage, and evidence |
| 04  | 02.14.18.03 | pending | initial target output files | create and baseline required docs, prompt, and source paths |
| 05  | 02.14.18.04 | pending | design                      | produce design spec for interfaces, data flow, and error handling |
| 06  | 02.14.18.05 | pending | development                 | implement utility and CLI workflows for formula CRUD |
| 07  | 02.14.18.06 | pending | SIT                         | execute system integration testing against configured workbook |
| 08  | 02.14.18.07 | pending | UAT                         | complete end-user acceptance validation and release recommendation |

## Phase Guidance

### 02.14.18.08 Development Docs

- Maintain this workflow prompt and the project tracker as the control artifacts.
- Keep task labels concise in tables and place detail in task subsections.
- Keep row width compliant with markdown table standards.

### 02.14.18.01 Requirements

- Define CRUD behavior for read, create, update, and clear formula operations.
- Define input contracts and invalid-input handling expectations.
- Define acceptance criteria that can be traced to SIT and UAT.

### 02.14.18.02 Test Strategy

- Define test levels: unit, integration, SIT, UAT.
- Define required evidence outputs and defect triage rules.
- Ensure every requirement has at least one validation path.

### 02.14.18.03 Initial Target Output Files

- Create baseline files with section templates and ownership notes.
- Confirm all required output paths exist and are linked from tracker.

### 02.14.18.04 Design

- Capture API interaction contracts and module boundaries.
- Define validation and retry/error strategy.
- Define CLI contract and standardized outputs.

### 02.14.18.05 Development

- Implement formula CRUD operations in `src/gsheet-formulas/*`.
- Add input validation, deterministic messaging, and tests.
- Keep implementation aligned to documented design decisions.

### 02.14.18.06 SIT

- Execute real API integration scenarios in controlled workbook.
- Capture pass/fail evidence and retest results.
- Confirm no release-blocking defects remain open.

### 02.14.18.07 UAT

- Run operator scenarios from the user guide.
- Validate expected workbook outcomes per operation.
- Record sign-off decision and deferred items.

