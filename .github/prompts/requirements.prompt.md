---
name: requirements-definition
description: Reusable and evolving prompt to guide POC-focused requirements definition from current state to closure while keeping requirements, implementation roadmap intent, design outputs, and task status in their proper artifacts.
---

# Requirements Definition Workflow Prompt

## Contents

- Overview
- Scope
- Required Skills
- Artifact Boundaries
- Objectives
- Reference Documents
- Evidence-First Clarification Policy
- Implementation Roadmap Alignment
- Main Task Mirror
- High-Level Task Guidance
- Inspection and Helper Script Guidelines
- Human-Agent Interaction and Handoff
- Workflow Loop
- Requirement Quality Checklist
- Completion Gate

## Overview

This prompt guides an iterative requirements definition workflow from current state to closure.

The workflow is POC-first and should keep requirement outcomes aligned with the implementation roadmap intent for release `0.1.0`.

It is a reusable process artifact, not the destination for final requirements content and not the destination for dynamic project task status.

## Scope

The scope of the active requirements workflow is the current release POC version `0.1.0`.

Requirements work in this prompt should prioritize defining what is required for POC success and should not expand into MVP or later-release capabilities unless explicitly approved as scope changes.

## Required Skills

Use these skills during requirements definition and evidence gathering.

- `task-definition` for status updates in `docs/develop/010/project-management/02-requirements.md`
- `documentation` for drafting and refining requirement artifacts
- `homebudget` for HomeBudget data-access and schema-inspection patterns
- `gsheet-inspect` for helper-workbook schema inspection and validation
- `variable-naming` for consistent naming conventions across requirement and design-facing terms
- `python` for lightweight inspection scripts where needed

## Artifact Boundaries

- Requirements content destination: `docs/requirements.md` and sub-docs in `docs/requirements/`
- Roadmap intent destination: `docs/requirements/implementation-roadmap.md`
- Dynamic task status destination: `docs/develop/010/project-management/02-requirements.md`
- Design destination after requirements closure: `docs/develop/010/design/*`
- Chat responses are temporary coordination only and are not completion artifacts.

## Objectives

- Define complete functional requirements from the user perspective.
- Capture user-defined business logic and constraints clearly.
- Capture relevant non-functional requirements.
- Keep requirement definitions aligned with the POC goals, scope, and feature intent documented in the implementation roadmap.
- Produce requirements that are design-ready with minimal additional clarification.

## Reference Documents

- `docs/about.md`
- `docs/requirements.md`
- `docs/develop/010/project-management/02-requirements.md`
- `docs/requirements/implementation-roadmap.md`
- `docs/requirements/poc.md`
- `docs/requirements/current-workflow.md`
- `docs/requirements/accounting-logic.md`
- `docs/requirements/account-classification.md`
- `docs/requirements/cash-reconcile.md`
- `docs/requirements/bill-payment.md`
- `docs/requirements/homebudget.md`
- `docs/requirements/google-sheets.md`
- `docs/requirements/glossary.md`
- `reference/hb-finances/`
- `reference/hb-reconcile/`

## Inspection Methodology

For guidance on navigating primary sources and inspection patterns, refer to:

- ** skill `data-sources-inspect`** — Complete methodology for HomeBudget, Google Sheets and other primary sources references used in the current workflows.

## Evidence-First Clarification Policy

Before asking the user for input, inspect available primary sources and reference documentation first.

Primary-source inspection should include, where applicable:

- Requirement and workflow docs in `docs/` and `docs/requirements/`
- Google Sheets configs and workbook inspection patterns using `gsheet-inspect`
- HomeBudget app and database inspection patterns using `homebudget`
- Existing helper scripts and read-only inspection evidence from project data artifacts

Use user clarification only after source inspection cannot resolve ambiguity.

When clarification is needed, ask concise, decision-oriented questions via toolcall `vscode_askQuestions`.

## Implementation Roadmap Alignment

The implementation roadmap should be treated as the release-intent anchor for requirements drafting.

During requirements work, use `docs/requirements/implementation-roadmap.md` to validate that requirement proposals for this milestone map to POC goals, POC scope, and POC feature boundaries.

If a requirement proposal appears to target MVP or later roadmap phases, flag it as out-of-scope for the current POC workflow and request explicit approval before including it.

## Main Task Mirror

Mirror this table from `docs/develop/010/project-management/02-requirements.md` and keep task-status updates in that tracking document.

| seq | id    | status  | task                               |
| --- | ----- | ------- | ---------------------------------- |
| 01  | 02.10 | closed  | requirements workflow prompt       |
| 02  | 02.11 | closed  | implementation roadmap             |
| 03  | 02.14 | open    | inspection guide                   |
| 04  | 02.01 | open    | structure and scope boundary       |
| 05  | 02.02 | pending | workflow orchestration             |
| 06  | 02.03 | pending | interaction and approvals          |
| 07  | 02.04 | pending | source systems and lineage         |
| 08  | 02.05 | pending | accounting model and mapping       |
| 09  | 02.06 | pending | reconciliation engine              |
| 10  | 02.07 | pending | statements lifecycle               |
| 11  | 02.08 | pending | homebudget integration             |
| 12  | 02.09 | pending | ibkr integration                   |
| 13  | 02.12 | pending | cpf integration                    |
| 14  | 02.13 | pending | bill payment and shared costs      |

## High-Level Task Guidance

### 02.14 Inspection Guide

- Develop and maintain methodology guidance in skill `data-sources-inspect`.
- Define evidence-first source inspection patterns required before requirement drafting.
- Keep this task scoped to process methodology; do not place requirement content in the guide.
- Close this step before treating `02.01` as complete.

### 02.01 Structure and Scope Boundary

- Determine and validate the requirement architecture from source evidence.
- Confirm scope boundaries and success criteria for requirements completion.
- Validate scope boundaries against the POC section in `docs/requirements/implementation-roadmap.md`.
- Align terminology with `docs/requirements/glossary.md`.
- Confirm what is explicitly out of scope for this milestone, including MVP-and-beyond capabilities unless explicitly approved.

### 02.02 Workflow Orchestration

- Define required user-visible workflow stages and checkpoints.
- Define required rerun, resume, and approval behaviors.
- Define required inputs, outputs, and invariants per workflow stage.

### 02.03 Interaction and Approvals

- Define user interaction requirements for CLI and guided prompts.
- Define requirement-level output readability and review expectations.
- Define required user confirmation points before commit actions.

### 02.04 Source Systems and Lineage

- Define required source systems and required fields at requirement level.
- Define source-of-truth expectations and precedence rules.
- Define minimum lineage and source-audit requirements.

### 02.05 Accounting Model and Mapping

- Define user business logic and accounting intent requirements.
- Define required account and category mapping behavior.
- Define currency precision and conversion requirement constraints.

### 02.06 Reconciliation Engine

- Define required reconciliation workflows and tolerance behavior.
- Define required variance visibility and user alert expectations.
- Define acceptance criteria for reconciliation closure per period.

### 02.07 Statements Lifecycle

- Define required statement outputs and reporting cadence.
- Define statement lifecycle requirements by period.
- Define revision and finalization expectations.

### 02.08 HomeBudget Integration

- Define integration requirements for read and controlled write operations.
- Define idempotency and duplicate-prevention requirements.
- Define integration-failure handling expectations from the user perspective.

### 02.09 IBKR Integration

- Define required IBKR inputs and expected outputs for monthly close.
- Define requirement-level handling for balances, positions, and related mappings.
- Define lineage expectations for IBKR-derived values.

### 02.12 CPF Integration

- Define required CPF inputs and expected outputs for monthly close.
- Define requirement-level handling for CPF balances, contributions, and adjustments.
- Define lineage and reconciliation expectations for CPF-derived values.

### 02.13 Bill Payment and Shared Costs

- Define required billing statement parsing and payment capture requirements.
- Define shared-cost allocation and settlement requirements from user perspective.
- Define payment and settlement audit requirements, including status and traceability.

## Inspection and Helper Script Guidelines

### Purpose

Use helper scripts to gather evidence, verify assumptions, and reduce ambiguity before asking users for clarifications.

Use an evidence-first sequence:

1. Inspect documentation and existing requirement artifacts.
2. Inspect primary source systems directly when instructions are available.
3. Ask the user only for unresolved decisions.

**For detailed methodology on inspecting HomeBudget, Google Sheets, and category mapping stages, see skill `data-sources-inspect`.**

### Script Locations

- Preferred: `.dev/.scripts/python/`
- Optional by tool type: `.dev/.scripts/bash/`, `.dev/.scripts/cmd/`

### Environment Rules

- Use `.dev/env/` for temporary requirement-phase helper scripts.
- Use `env/` for main application behavior and stable project workflows.
- Do not create new virtual environments.

### Script Practices

- Keep scripts short, single-purpose, and rerunnable.
- Use read-only inspection whenever possible.
- Name scripts explicitly by intent, for example:
  - `inspect_hb_schema.py`
  - `inspect_hb_accounts.py`
  - `inspect_gsheet_ranges.py`
  - `check_source_field_coverage.py`
- Summarize findings in target docs, not in chat as the final artifact.

### Primary Source Inspection Expectations

- For Google Sheets evidence gathering, use documented `gsheet-inspect` workflows and direct workbook/config inspection before requesting user clarification. See skill `data-sources-inspect`.

- For HomeBudget evidence gathering, use documented `homebudget` workflows and database/schema inspection before requesting user clarification. See skill `data-sources-inspect`.

- For category mapping evidence, understand the three-stage mapping model (HB category → GL → financial statements) as documented in skill `data-sources-inspect`.

- Prefer read-only inspection for requirement discovery and validation unless explicit write operations are approved.

## Human-Agent Interaction and Handoff

### Agent Can Execute Autonomously

The agent should proceed without waiting for user input when:

1. Reading and cross-referencing existing documentation.
2. Inspecting HomeBudget and helper workbook schemas through approved tools and scripts.
3. Drafting and refining requirements text in `docs/requirements.md`.
4. Proposing requirement wording based on observed evidence.
5. Updating task-status rows in `docs/develop/010/project-management/02-requirements.md` when completion can be verified from artifact changes.
6. Running evidence-first inspection of available primary sources before requesting user decisions.

### Agent Must Request User Input

The agent must request user decisions when:

1. Business-rule intent is ambiguous or conflicting across sources.
2. Tolerance thresholds and approval policies are missing.
3. Source precedence decisions are unclear.
4. Requirement scope expansion is implied but not approved.
5. Tradeoffs require owner preference, for example strictness versus flexibility.
6. Relevant primary-source inspection and reference-document review have been completed and still do not resolve the decision.

### What the Agent Must Provide When Asking

When requesting user input, the agent should provide:

1. The exact decision needed.
2. The current evidence and options.
3. The impact of each option on requirements and downstream design.
4. A recommended default with rationale.
5. The inspected sources and checks already performed, including why they were insufficient.
6. The clarification request using toolcall `vscode_askQuestions`.

### What the Agent Needs from the User

The agent needs:

1. Explicit decision choices on ambiguous business rules.
2. Confirmation on tolerance and exception policies.
3. Confirmation on scope inclusion and exclusions.
4. Final acceptance that a requirement area is complete.

## Workflow Loop

For each open requirement task:

1. Inspect current docs and data evidence, including available primary-source references and inspection instructions.
2. Verify roadmap alignment against the POC section in `docs/requirements/implementation-roadmap.md`.
3. Review existing requirement documents for inconsistencies and ambiguities, then flag and resolve them in the target requirement artifacts.
4. Draft or refine requirement statements in `docs/requirements.md`.
5. Validate requirement quality for clarity and testability at requirement level.
6. If unresolved decisions remain after evidence-first inspection, ask focused user questions via toolcall `vscode_askQuestions`.
7. Integrate user decisions into `docs/requirements.md`.
8. Update task status in `docs/develop/010/project-management/02-requirements.md` using `task-definition` guidance.

## Requirement Quality Checklist

A requirement area is complete when:

- Statements are user-perspective and behavior-focused.
- Scope and exclusions are clear.
- Inputs, outputs, and invariants are explicit.
- Required business logic is captured at requirement level.
- Non-functional constraints relevant to the area are captured.
- Known ambiguities are resolved or explicitly queued for user decision.
- Each unresolved ambiguity is backed by documented source inspection and, when needed, an explicit user decision request via `vscode_askQuestions`.

## Completion Gate

Requirements milestone is closed when:

1. Pre-requisite methodology step `02.14` (inspection guide) is complete and user-validated.
2. All main requirement areas 02.01 through 02.09, plus 02.12 and 02.13, are complete and user-validated.
3. `docs/requirements.md` is coherent and design-ready.
4. Requirements are explicitly aligned to POC intent in `docs/requirements/implementation-roadmap.md`.
5. `docs/develop/010/project-management/02-requirements.md` reflects accurate final status.
6. Handoff to `docs/develop/010/design/*` can proceed with minimal additional user clarification.
