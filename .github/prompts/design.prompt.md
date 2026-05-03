---
name: design
description: Reusable prompt to guide the design milestone from current state to closure, producing implementable design documents under docs/releases/010/design and keeping task status, artifact content, and open decisions in their proper locations.
---

# Design Milestone Workflow Prompt

## MANDATORY: Markdown table rules

- when creating any markdown table, ensure that it conforms to the guidelines in skill `markdown-tables`
- row length max < 115 characters
- padded to fixed width columns
- avoid lengthy description and notes fields, simplify, use aliases and shorthand, separate explanatory prose or list sections for lengthy explanations outside of the table.
- include a numeric `01` id column to the far left.
- lowercase column names
- do not over-complicate the process of generating the tables to meet this requirement. use heuristics, DO NOT count characters, use your judgement, apply heuristics, review sample templates from within the documentation, make a pass and write the table.

## Contents

- Overview
- Scope
- Required Skills
- Artifact Boundaries
- Objectives
- Reference Documents
- Primary Data Sources Usage
- Documentation Rules
- Requirement Change Management During Design
- Human-Agent Interaction and Handoff
- Specialized Subagent Delegation
- Task Mirror
- Task Guidance
- Workflow Loop
- Design Quality Checklist
- Completion Gate

## Overview

This prompt guides an iterative design milestone workflow from current state to closure.

The workflow converts approved requirements into implementable design documentation under
`docs/releases/010/design`. Task progress is tracked in the project management tracker at
`docs/releases/010/project-management/04-design.md`.

This is a reusable process artifact. It is not the destination for design content, task status
metadata, or open design decisions.

## Scope

In scope:

- Define and update release 010 design documents in `docs/releases/010/design`.
- Convert requirement intent in `docs/releases/010/requirements` into clear design contracts.
- Define module boundaries, adapter contracts, data model ownership, and workflow orchestration
  behavior.
- Define design traceability needed for test strategy and implementation handoff.

Out of scope:

- Production implementation code.
- Test case authoring and SIT or UAT execution.
- MVP or later release expansion beyond the POC scope.
- Data migration solution design.

## Required Skills

Use these skills throughout the design workflow.

- `task-definition` for status updates in `docs/releases/010/project-management/04-design.md`
- `markdown-tables` for formatting markdown tables in design documents and the tracker
- `data-sources-inspect` for evidence-first design from primary sources and cross-source evidence gathering before drafting adapter contracts
- `documentation` for drafting and refining design artifacts
- `markdown-tables` when creating or updating any markdown table in any document
- `accounting-logic` for M2M, forex, double-entry, FIFO, and CPF calculation verification
- `reconciliation-patterns` for tolerance examples and procedural discipline in reconcile design
- `sqlite-data-pipelines` for idempotent ingest, SCD, deterministic hashing, and staging isolation
- `variable-naming` for consistent naming conventions across design, schema, and config artifacts
- `requirements-change` for capturing and formalizing requirement changes discovered during design phases
- `python` for lightweight inspection scripts where evidence is needed

## Artifact Boundaries

- Design content destination: `docs/releases/010/design/*.md`
- Task status and closure tracking destination: `docs/releases/010/project-management/04-design.md`
- Open design decisions and conflicts: `docs/releases/010/design/requirements-decisions.md`
- Open design issues and deferred items: `docs/releases/010/design/design-issues.md`
- Requirements source: `docs/releases/010/requirements/*.md`
- Design-index final state: `docs/releases/010/design/design-index.md`
- Chat responses are temporary coordination only and are not completion artifacts.

Design documents must not reference the project tracker or any task ID. The tracker references
design docs. This boundary is one-directional.

## Objectives

- Translate approved requirements into design contracts ready for implementation.
- Define module, adapter, and data boundaries clearly enough that implementation needs no further
  design clarification.
- Produce a traceable design package: every requirement owner topic is covered or explicitly
  excluded with rationale.
- Close all open design decisions or escalate them with documented rationale to `design-issues.md`.
- Deliver a design index and handoff package ready for test strategy and implementation milestones.

## Reference Documents

Primary tracking:

- `docs/releases/010/project-management/04-design.md`

Requirements input set:

- `docs/releases/010/requirements/*.md`

Existing design documents:

- `docs/releases/010/design/architecture.md`
- `docs/releases/010/design/tech-stack.md`
- `docs/releases/010/design/design-guidelines.md`
- `docs/releases/010/design/repository-layout.md`
- `docs/releases/010/design/topic-map.md`
- `docs/releases/010/design/workflows.md`
- `docs/releases/010/design/requirements-conflicts-and-gaps.md`
- `docs/releases/010/design/requirements-decisions.md`

Legacy reference repositories for implementation evidence (read-only; not baseline contracts):

- `reference/hb-reconcile/` — transaction matching algorithm and edit-generation patterns
- `reference/hb-finances/` — statement ingestion and GL posting patterns
- `reference/notion-bills/` — bill-cycle and payment-status workflow evidence

Design conventions and platform constraints:

- `docs/about.md`
- `docs/develop/environment.md`

## Primary Data Sources Usage

Use primary data sources to derive design contracts from evidence, not assumptions.

### Purpose

- Verify real source schemas, field behavior, and lineage before defining module boundaries.
- Reduce design ambiguity by grounding contracts in observed source behavior.
- Prevent design drift from requirement intent and from current operational source patterns.

### Source precedence for design work

Use this order unless a scope definition states otherwise:

1. Requirement owner documents in `docs/releases/010/requirements/*.md`
2. Existing design contracts in `docs/releases/010/design/*.md`
3. Primary source inspection via skill `data-sources-inspect`
4. Legacy reference repositories as implementation evidence only

### Standard usage workflow

1. Start from the task scope definition in the tracker and identify required source evidence.
2. Inspect requirement and design references first to establish target contract boundaries.
3. Run source inspection steps from `data-sources-inspect` for the relevant domain:
   HomeBudget, Google Sheets, bank statements, local inputs, or non-tool references.
4. Capture only evidence that affects the target design contract, such as:
   schema ownership, field keys, tolerance defaults, lineage anchors, or formula logic.
5. Convert evidence into explicit design statements in the target design document.
6. If sources conflict, record the conflict in `requirements-decisions.md` or
   `design-issues.md` and request a user decision with evidence.

### Evidence expectations by design area

- Reconciliation design: method parameters, heuristics, and tolerance behavior grounded in
  requirements plus legacy reconcile evidence.
- Integration design: adapter read and write contracts grounded in actual source structures and
  validation behavior.
- Data pipeline and lineage design: staging schema ownership and reproducibility controls grounded
  in observed source and transformation flow.
- Statements and publish design: aggregation and output rules grounded in accounting requirements
  and source lineage constraints.

### Boundaries and guardrails

- Use read-only inspection by default.
- Treat `reference/*` repositories as evidence, not authoritative runtime contracts.
- Do not place raw inspection logs into design documents; summarize decision-relevant findings.
- Do not include secrets or cloud resource UIDs in design artifacts.

## Documentation Rules

Follow these rules in every design document and every update to this prompt.

- **Skill reference** before drafting any design section, check whether a relevant skill covers
  that topic and apply its guidance consistently.
- **Markdown tables** follow the `markdown-tables` skill for every table: use fixed-width columns
  padded to the longest cell in each column, and keep every row under 115 characters total
  including pipes and spaces. This rule is mandatory and applies to all markdown documents.
- **Table of contents** include a TOC at the top of every design document using anchor links.
  Do not use anchor links in prompt `*.prompt.md` or skill `SKILL.md` files.
- **Task IDs** task ID references such as `04.04.02` must appear only in the task mirror table
  in this prompt and in the tracker document `04-design.md`. All other locations — design docs,
  skill files, chat, and all other sections of this prompt — must use descriptive names only.
- **Closure metadata boundary** status and closure tracking belong in the tracker only. Do not
  place closure checklists, status traces, or completion notes inside design content documents or in this prompt.
- **Design decisions boundary** open decisions and conflicts belong in `requirements-decisions.md`
  or `design-issues.md`. Do not embed unresolved decisions inside design content documents.
- **Natural language in content** write design document content in reader-facing language only.
  Do not embed authoring rationale, organizational commentary, or task IDs in content docs.
- **Cross-reference discipline** design docs may reference other design docs and requirement docs.
  They must not reference the tracker, task IDs, or this prompt.
- **Secret and cloud UID handling** do not write secrets or cloud resource UIDs in any artifact.
  Reference the config key and config file path where the value is stored.

## Requirement Change Management During Design

**Reference skill**: `requirements-change`

### Purpose

Design work often reveals missing, ambiguous, or conflicting requirements that must be formally 
captured and cascaded to dependent workflows (test strategy, test cases, implementation). This section 
guides when and how to apply the requirements-change skill during design phases.

### When to Apply

- Design decisions impose new constraints that aren't documented in requirements (e.g., data model 
  choices affecting validation rules or integration boundaries).
- Source data inspection reveals edge cases, patterns, or behaviors not covered in existing requirements.
- Architectural decisions introduce new workflow sequencing, approval requirements, or error handling 
  rules.
- Conflicting requirements emerge between related specification documents or between requirements 
  and source evidence.
- Design phase discovers assumptions that should become explicit formal requirements.

### What to Do

Use the 6-step requirements-change workflow to:

1. **Establish context**: Record where the requirement change was discovered (design phase, design 
   section, evidence source, discoverer).
2. **Record the change**: Assign a change ID and document it in the requirements change log 
   (`docs/releases/010/requirements/requirements-changes.md`).
3. **Update requirement documents**: Modify affected requirement files in 
   `docs/releases/010/requirements/` to reflect the change.
4. **Assess cascading impacts**: Identify impacts to test strategy, test cases, and implementation 
   code and determine what is implemented vs. backlogged.
5. **Create backlog tasks**: Track unimplemented impacts with ownership, dependencies, and clear 
   acceptance criteria linked to the requirement change.
6. **Validate and close**: Confirm all cross-references are consistent between the change log and 
   impacted requirements, and that all impacts are tracked.

### Checkpoint Actions by Design Phase

Add these requirement-change checks to each major design phase:

- **Before starting design task**: Verify that requirements are complete and unambiguous. If gaps 
  or conflicts exist, record them via the requirements-change workflow.
- **During source inspection**: Check if actual source behavior contradicts documented requirements. 
  If yes, record the discrepancy and clarify requirements before designing.
- **During architecture phase**: When defining module boundaries and data flows, identify any missing 
  requirements for data transformation, validation, error handling, or handoff.
- **During domain model phase**: As you finalize business entity definitions, verify all requirements 
  are satisfied. Check for gaps in attribute definitions, behavioral constraints, or domain rules.
- **During data layer design**: When designing schema and persistence, identify requirements around 
  data consistency, archiving, audit trails, or schema versioning.
- **During workflow design**: When orchestrating module interactions, check whether workflow sequencing, 
  approval requirements, or checkpoint behaviors are missing or ambiguous.
- **During module interface design**: When defining API contracts, ensure all interface-level requirements 
  (validation, error handling, preconditions) are documented and unambiguous.
- **Before finalizing design**: Do a final scan of requirements-changes.md to confirm all discovered 
  changes have been formally recorded and all impacts have been cascaded to test and code backlogs.

## Human-Agent Interaction and Handoff

### Agent Can Execute Autonomously

The agent should proceed without waiting for user input when:

- Reading requirements and existing design documents to understand current state.
- Inspecting primary sources via `data-sources-inspect` patterns before designing adapter
  contracts or data schemas.
- Drafting or refining design document content in `docs/releases/010/design/`.
- Updating task status in the tracker when artifact changes confirm completion.
- Cross-referencing design docs for consistency and applying naming and convention rules.
- Running read-only evidence inspection before requesting user decisions.

### Agent Must Request User Input

The agent must request user decisions when:

- Design choices involve tradeoffs between correctness, complexity, or performance.
- Business-rule intent from requirements is ambiguous or inconsistent across source documents.
- Tolerance thresholds, approval policies, or config parameter defaults are missing.
- A design decision creates a boundary or exclusion with downstream consequences.
- Evidence-first inspection and reference-document review have been completed and still do not
  resolve the decision.

### What the Agent Must Provide When Asking

When requesting user input, the agent must provide:

- The exact decision needed.
- Current evidence and the available options.
- Impact of each option on the design and downstream implementation.
- A recommended default with rationale.
- Sources already inspected and why they were insufficient.
- The clarification request using `vscode_askQuestions`.

## Specialized Subagent Delegation

Use specialized agents for domain analysis and boundary validation before editing design
artifacts. Delegate with `runSubagent` using explicit prompts and a fixed response format.

### Task decomposition before delegation

Break each design task into independent work packets before calling subagents:

- Design analysis packet: domain logic, boundary ownership, and invariants.
- Contract packet: inputs, outputs, schemas, and error behavior.
- Consistency packet: cross-document alignment and conflict detection.
- Tracker packet: status and closure updates in tracker artifacts only.

Keep design packets separate from tracker packets. Do not mix design content edits and tracker
status updates in the same execution step.

### Design and tracker separation rules

- Design work updates only `docs/releases/010/design/*.md`.
- Tracker work updates only `docs/releases/010/project-management/04-design.md`.
- Run design drafting and reconciliation of conflicts first.
- Update tracker status only after design content is complete and validated.
- If design is blocked by open decisions, update decision artifacts and keep tracker state
  unchanged until the blocking decision is resolved.

### Specialized agent mapping guide

Use this mapping to select subagents by design concern:

- `workflow-orchestrator`: stage routing, merge gates, checkpoint semantics, handoffs.
- `reconciliation-engine`: method classes, matching logic, tolerance and variance policy.
- `sqlite-adapter`: persistence boundaries, schema contracts, transaction and idempotency rules.
- `statement-builder`: close_book rollups, statement assembly, publish and finalization behavior.
- `source-adapters`: source-specific extraction, normalization, and staging boundary contracts.
- `homebudget-adapter`: read and write-back boundaries and approval-gated posting behavior.
- `google-sheets-adapter`: workbook range contracts, status publishing, and UI data flow.
- `backend-api`: Flask route contracts, payload validation, and API boundary behavior.
- `aws-storage-adapter`: artifact upload, retrieval, naming policy, and lineage evidence.
- `bill-shared-runtime`: bill intake, allocation, posting lifecycle, and reconcile handoff.
- `account-close-runtime`: phase-2 account execution, source authority, and group behavior.
- `mapping-crud`: mapping lifecycle controls, validation gates, and audit visibility.
- `financial-accounting`: accounting policy validation for M2M, forex, FIFO, and CPF rules.

### Parallel subagent execution guidelines

Use parallel calls only when packets are independent and do not require sequential context.

- Run at most three subagents in one parallel batch for focused synthesis.
- Give each subagent a narrow scope and a required output schema.
- Require each subagent to return one key risk, one recommendation, and confidence.
- Synthesize all subagent outputs into one decision before editing files.
- If subagent findings conflict, resolve conflicts in decision artifacts before drafting.

Recommended parallel bundles:

- Reconcile design bundle: `reconciliation-engine` + `workflow-orchestrator` + `sqlite-adapter`.
- Statement publish bundle: `statement-builder` + `aws-storage-adapter` + `backend-api`.
- Adapter contract bundle: `source-adapters` + `homebudget-adapter` +
  `google-sheets-adapter`.

### Delegation execution pattern

1. Define the packet scope and expected output schema.
2. Call `runSubagent` with `agentName` for each packet.
3. Use parallel invocation only for independent packets.
4. Consolidate findings into explicit design decisions.
5. Apply design document edits.
6. Run validation and consistency checks.
7. Apply tracker updates as a separate final step.

## Workflow Loop

For each open design task:

1. Read the scope definition in the tracker. If no scope definition exists, draft one before
   starting and confirm with the user.
2. Inspect primary sources in the order specified in the scope definition. For adapter or
   schema design, use `data-sources-inspect` patterns before drafting.
3. Review existing design documents and requirements for gaps, conflicts, and consistency.
4. Draft or refine the target design document in `docs/releases/010/design/`.
5. Validate against the design quality checklist below.
6. If unresolved decisions remain after evidence-first inspection, request user input via
   `vscode_askQuestions` with full evidence context and a recommended default.
7. Integrate user decisions into the design document.
8. Update task status in the tracker and this prompt's task mirror.

## Design Quality Checklist

A design document is complete when:

- Module responsibilities and boundaries are stated explicitly.
- Data contracts — inputs, outputs, field names, and types — are defined.
- Behavior rules and decision logic are specified without ambiguity.
- Config-driven parameters are identified and their parameterization class is named.
- Integration points cross-reference the relevant adapter design documents.
- Error and blocking conditions are listed with their propagation behavior.
- All requirement owner topics in scope are addressed or explicitly excluded with rationale.
- No open design decision remains unresolved or unlogged in `design-issues.md`.
- Document follows the naming, API, and config conventions in design-guidelines.
- All markdown tables use fixed-width columns and rows under 115 characters.

## Completion Gate

The design milestone is closed when:

1. All domain behavior documents are complete and user-validated.
2. All UI and interaction documents are complete and user-validated.
3. All data model and lineage documents are complete and user-validated.
4. All integration adapter documents are complete and user-validated.
5. Error and exception handling design is complete and user-validated.
6. Design quality gate review is passed: full requirement traceability confirmed, no blocking
   open issues, all open items logged in `design-issues.md` with rationale.
7. Design index is published and accurately reflects final document status.
8. `docs/releases/010/project-management/04-design.md` and the task mirror in this prompt
   reflect accurate final status.
9. Handoff to test strategy and implementation milestones can proceed with no further
   design clarification required.

## Tasks

This table is the single location in this prompt where task IDs appear. All other sections use
descriptive names. Keep this table synchronized with the tracker after each status change.

### Main tasks

| seq | id    | status  | task                           |
| --- | ----- | ------- | ------------------------------ |
| 01  | 04.01 | closed  | design scope baseline          |
| 02  | 04.03 | closed  | architecture and boundaries    |
| 03  | 04.04 | open    | domain behavior                |
| 04  | 04.05 | pending | UI and interaction             |
| 05  | 04.06 | pending | data model and lineage         |
| 06  | 04.07 | pending | integration                    |
| 07  | 04.08 | pending | error and exception handling   |
| 08  | 04.09 | pending | design quality gate review     |
| 09  | 04.10 | pending | implementation handoff package |

## Task Guidance

### Reconciliation

The scope definition lists primary
sources, topics the document must specify, and out-of-scope boundaries.

Primary source read order:

1. Requirements: reconciliation engine, accounting logic.
2. Design cross-references: workflows stage 6 (reconcile), architecture reconcile engine
   component spec, design-guidelines for conventions.
3. Legacy implementation evidence: `reference/hb-reconcile/` docs, source code, and heuristics
   config. Treat as evidence for algorithm detail, not as a baseline contract.

Design the reconciliation document to cover:

- Module boundary and invocation contract with the workflow orchestrator.
- Transaction-level method class: forward and backwards algorithm, edits model, gap equation,
  per-account heuristics, and method parameters.
- Balance-level method class: generic balance equation and three outcome classes.
- Account-group procedure table: method class, comparison basis, source schemas, tolerance,
  and adjustment outcome for all six groups.
- Variance handling matrix: zero variance, within tolerance, exceeds tolerance — approval path
  and auto-approve conditions for each.
- Adjustment transaction fields and posting targets: close_book schema and HB write-back.
- Bill accrual conflict policy: how all four conflict classes map to engine behavior.
- Reconciliation session record: persisted fields, lineage requirements, audit trail.
- Config and parameter contract: tolerance values, parameterization class for reconcile params.

Do not duplicate stage 6 step sequence from the workflows document; cross-reference it.

### Statements

Define the statement builder: inputs from the close_book schema, output formats, the publish
lifecycle, and finalization gating. Reference requirements: financial-statements, statements
lifecycle, and accounting logic. Reference workflows stage 7 (statements) and stage 8 (publish).

### Data pipeline

Define source ingest stages, transformation steps, staging schema ownership, and lineage anchors
from raw source files through the close_book output schema. Apply `sqlite-data-pipelines` skill
patterns. Reference requirements: source systems and lineage, bank statements, workflow
orchestration. Reference architecture data flow paths.

### Bill payment

Define bill intake, share allocation logic, and HomeBudget posting contract. Reference
requirements: shared costs, bills, homebudget. Reference workflows bill payment workstream steps.

### UI and interaction

Define Google Sheets workbook structure, page inventory, and user touchpoint map for the close
session. Define CLI command surface and GAS optional extension scope.

### Data model and lineage

Define canonical entities and keys from source ingest through statement output. Define stage
schema ownership, lineage tracking fields, and reproducibility controls. Apply
`sqlite-data-pipelines` SCD and deterministic hashing patterns.

### Integration

For each adapter — HomeBudget wrapper, Google Sheets, bank statements, IBKR, CPF — define read
and write paths, invocation patterns, input validation rules, error signaling, and retry policy.
Use `data-sources-inspect` evidence before drafting adapter contracts. Keep adapter contracts
separate from the reconciliation engine; cross-reference where needed.

### Error and exception handling

Define error taxonomy covering all integration boundaries and close-cycle failure modes. Define
propagation paths, user recovery checkpoints, and blocking versus recoverable failure criteria.
Reference requirements: exception and error handling.

### Design quality gate review

Verify that every requirement owner topic has a corresponding design document or an explicit
exclusion with rationale. Verify internal consistency across design docs, especially boundary
ownership and data contracts. Triage all open items in `design-issues.md`.

### Implementation handoff package

Publish the design index listing all design documents with status and requirement traceability.
Publish the final `design-issues.md` with deferred items time-boxed or closed. Confirm test
strategy and implementation milestone handoffs are ready.

