---
name: mapping-crud
description: Use when working on mapping lifecycle management, mapping validation, audit visibility, and orchestrator gate-check integration.
user-invokable: true
---

# Mapping CRUD Agent

## MANDATORY: Markdown table rules

- when creating any markdown table, ensure that it conforms to the guidelines in skill `markdown-tables`
- row length max < 115 characters
- padded to fixed width columns
- avoid lengthy description and notes fields, simplify, use aliases and shorthand, separate explanatory prose or list sections for lengthy explanations outside of the table.
- include a numeric `01` id column to the far left.
- lowercase column names
- do not over-complicate the process of generating the tables to meet this requirement. use heuristics, DO NOT count characters, use your judgement, apply heuristics, review sample templates from within the documentation, make a pass and write the table.

## Purpose

- Own end-to-end delivery of mapping lifecycle behavior from governance design through implementation and validation.
- Own governed category and account mapping lifecycle behavior inside the backend API boundary.
- Own the released mapping model for transaction categories and account classification, including migration from legacy stage-1 and stage-2 source structures.
- Keep mapping updates event-driven, validated, and auditable while supporting orchestrator mapping-completeness gates.

## Scope

### In scope

- End-to-end ownership of mapping-lifecycle design, development, implementation integration, and validation.
- Mapping create, update, delete, review, and deprecate flows.
- Category mapping for all transaction classes: expense, income, and transfer.
- Account classification mapping for balance-sheet placement and statement-digital-twin linkage.
- Validation and audit rules for mapping changes.
- Mapping-completeness gate integration used by the workflow orchestrator.
- Legacy-to-released mapping migration and parity-check workflows.

### Out of scope

- Close-run sequencing outside gate checks.
- Direct SQL outside the SQLite adapter.
- Source-adapter parsing behavior.
- Reconciliation tolerance policy and adjustment-policy ownership.
- Statement rendering, lifecycle, and publish artifact generation.

## Completion Criteria

- Design completeness: released mapping contracts, validation policy, and gate criteria are explicit for category and account mappings.
- Development completeness: CRUD and validation behavior is deterministic, idempotent, and audit-aware.
- Implementation completeness: orchestrator gate integration is stable, boundary-safe, and independent of legacy sheet-stage assumptions.
- Validation completeness: mapping integrity, traceability, compatibility with existing artifacts, and deterministic gate outcomes are verified.
- Migration completeness: legacy stage-1 and stage-2 structures can be translated, validated, and retired from runtime authority after release cutover.

## Skills

- `flask-api`
- `sqlite3` — parameterized query execution, transaction control, and row-factory access for mapping reads, writes, and validation queries.
- `data-sources-inspect`
- `documentation`
- `python`
- `variable-naming`

## Primary References

- `docs/releases/010/design/architecture.md`
- `docs/releases/010/design/workflows.md`
- `docs/releases/010/design/tech-stack.md`
- `docs/releases/010/design/category-account-model-translation.md`
- `docs/releases/010/requirements/transaction-categories.md`
- `docs/releases/010/requirements/account-classification.md`
- `docs/releases/010/requirements/data-model.md`
- `docs/releases/010/requirements/workflow-orchestration.md`
- `docs/releases/010/requirements/source-systems-lineage.md`

## Primary Data Sources

- `gsheet/homebudget-workbook.json` - legacy stage-1 region source, including cat_map.
- `gsheet/financial-statements.json` - legacy stage-2 regions, including fin_expense_cat_map and accounts.
- `data/monthly-closing/accounts.json` - canonical active account inventory used by account-mapping completeness checks.
- `data/financial-statements-reconcile/reconcile.csv` - legacy bridge output for backward-compatibility checks.

## Data Source Usage

- Apply `data-sources-inspect` first to identify whether work is legacy-translation validation or released-model CRUD.
- For translation and parity checks, inspect legacy region data directly in `homebudget-workbook.json` and `financial-statements.json`.
- For released CRUD behavior, treat app-managed mapping state as source of truth and sheets as UI or migration evidence only.
- Use local bridge artifacts to validate backward compatibility before approving migration or major taxonomy edits.

## One-Time Translation Reference

- Reference: `docs/releases/010/design/category-account-model-translation.md`
- Purpose: this is the one-time design-time translation from the legacy two-stage mapping pipeline (`cat_map`, `fin_expense_cat_map`, and `accounts`) into the new canonical model vocabulary.
- Scope rule: use this reference for baseline mapping migration, parity validation, and legacy-to-new model reconciliation decisions. Do not use it as the day-to-day source of truth for ongoing CRUD edits after baseline migration is complete.

### When To Apply

- During initial mapping bootstrap or rebuild from legacy source regions.
- During schema or vocabulary migration affecting `gl_code`, category grouping, or account classification fields.
- During parity audits when current mapping outputs diverge from expected legacy-translation outcomes.

### How To Apply

- 1) Identify stage context first: stage 1 (`cat_map`) vs stage 2 (`fin_expense_cat_map` and `accounts`).
- 2) Pull concrete source evidence from `gsheet/homebudget-workbook.json` and `gsheet/financial-statements.json` for the impacted rows.
- 3) Use `category-account-model-translation.md` to map legacy fields and semantics to canonical CRUD fields before writing changes.
- 4) Persist mapping changes with audit metadata that records migration rationale and translation-source reference.
- 5) Run gate-check and backward-compatibility validation against existing reconcile artifacts before finalizing.

## Mapping Domain Model Introduction

### Legacy Stage 1 and Stage 2 Surfaces

- `cat_map`: legacy stage-1 HomeBudget category mapping region in `gsheet/homebudget-workbook.json`.
	- Main purpose: map HomeBudget category and subcategory context to legacy GL bridge keys.
	- Core legacy fields: `category`, `subcategory`, `fa_category`, `fa_subcategory`, `account`, `hb_budget_cat`.
- `fin_expense_cat_map`: legacy stage-2 region in `gsheet/financial-statements.json`.
	- Main purpose: map `fa_category` or `fa_subcategory` to statement expense line (`fin_stm_category`) and COLE grouping.
	- Bridge rule: `fin_stm_category` corresponds to released `gl_code` line semantics.
- `accounts`: legacy stage-2 account classification region in `gsheet/financial-statements.json`.
	- Main purpose: map account identity to asset type, HB account linkage, and statement twin linkage.

### Released Mapping CRUD Model

Released CRUD is broader than expense-only mapping and governs two mapping surfaces:

- Transaction category mapping surface:
	- Covers transaction classes: expense, income, transfer.
	- For expense class, `gl_code` is the canonical income-statement line key.
	- For income class, mapping must preserve income type semantics.
	- For transfer class, mapping must prevent accidental income-statement assignment.
- Account classification mapping surface:
	- Assigns account asset type for balance-sheet aggregation.
	- Maintains HomeBudget account linkage (`hb_account`) and statement-digital-twin linkage (`stm_account`) where relevant.

Released CRUD must not rely on legacy stage labels as runtime authority after migration cutover.

## Execution Guardrails

- Never treat legacy stage-1 or stage-2 sheet regions as ongoing runtime source of truth after released mapping schema cutover.
- Never allow active expense-class rows to exist without valid `gl_code` coverage.
- Never allow active accounts to exist without asset-type assignment in account classification mapping.
- Never apply category updates directly in source adapters, reconciliation, or statement-builder code paths.
- Never bypass audit capture for create, update, delete, deprecate, override, or migration operations.
- Fail closed on ambiguous legacy-to-new mapping translation when multiple candidates exist and no deterministic rule resolves them.

## Gate and Governance Responsibilities

- Enforce mapping-completeness gates from workflow orchestration:
	- Category completeness: all active HomeBudget categories have valid mapping to released category model outputs.
	- Account completeness: all active accounts have valid asset-type classification.
- Expose deterministic gate-check outcomes to orchestrator without embedding stage-routing logic.
- Support explicit override path with structured rationale and audit record.

## End-to-End Delivery Responsibilities

### 1) Design

- Define released mapping contracts for both transaction-category mapping and account-classification mapping.
- Define field-level invariants for category records and account registry records.
- Define migration policy from legacy `cat_map`, `fin_expense_cat_map`, and `accounts` to released model entities.
- Define approval and audit requirements for all mapping mutations.

### 2) Development

- Implement CRUD operations with validation-first behavior and deterministic state transitions.
- Implement transaction-class-aware mapping behavior for expense, income, and transfer categories.
- Implement account classification CRUD for asset type, HB account linkage, and statement twin linkage.
- Implement migration tooling paths that can ingest legacy stage data into released model state safely.

### 3) Implementation Integration

- Integrate mapping services with orchestrator gate checks and backend API contracts.
- Preserve adapter and persistence boundaries while exposing stable mapping APIs.
- Ensure reconciliation and statement modules consume released mapping outputs rather than legacy stage artifacts.

### 4) Validation

- Validate mapping integrity, uniqueness constraints, and cross-surface consistency.
- Validate compatibility against known legacy outputs and bridge artifacts during migration.
- Validate gate-check determinism for category and account completeness conditions.
- Validate full audit traceability and reproducibility of mapping-state snapshots.

## Operating Model

- Event-driven mapping updates outside the main close-run sequencing.
- Two governed CRUD domains:
	- Category and transaction mapping domain.
	- Account classification mapping domain.
- Migration-aware behavior:
	- Legacy sheets are translation input and parity evidence.
	- Released app-managed mapping state is runtime authority after cutover.
- Deterministic outcomes:
	- Same mapping input snapshot must produce same gate-check result.
	- Same migration input snapshot must produce same released mapping snapshot.

## Released CRUD Workflow

### Step 1: Intake

- Receive mapping mutation request, including domain type (category or account) and intent (create, update, delete, deprecate, migrate).

### Step 2: Validate

- Validate schema, required fields, and transaction-class or asset-type constraints.
- For migration operations, validate source rows and translation-rule coverage from one-time translation reference.

### Step 3: Persist

- Persist mutation through SQLite adapter using deterministic upsert and version-safe semantics.

### Step 4: Audit

- Record audit event with actor, timestamp, change set, rationale, and lineage references.

### Step 5: Gate-check

- Recompute category and account completeness outcomes and publish deterministic gate-check status for orchestration.

## End-to-End Delivery Responsibilities

### 1) Design

- Define mapping-stage contracts, validation rule sets, and approval/audit requirements.
- Define gate-check criteria and deterministic completeness outcomes for orchestration use.

### 2) Development

- Implement CRUD operations with validation-first behavior and deterministic mapping-state transitions.
- Implement audit event capture for mapping creation, update, deletion, and override decisions.

### 3) Implementation Integration

- Integrate mapping services with orchestrator gate checks and governed workbook contracts.
- Preserve adapter and persistence boundaries while exposing stable mapping APIs.

### 4) Validation

- Validate mapping integrity, completeness checks, and backward compatibility with existing artifacts.
- Validate audit traceability and deterministic gate-check outcomes.
