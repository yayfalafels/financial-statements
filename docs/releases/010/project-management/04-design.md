# Project tracking: Design

This document defines scope and tasks for milestone 04, design documentation, for release 0.1.0 POC.

Cross-reference boundary:

- This is a project tracking artifact and is not part of the design documentation set at docs/releases/010/design.
- Design documents must not reference this document or any task tracking IDs.

## Table of contents

- [Summary](#summary)
- [Scope](#scope)
- [Inputs and target outputs](#inputs-and-target-outputs)
- [Milestone task table](#milestone-task-table)
- [Task details](#task-details)

## Summary

Milestone 04 translates approved requirements into implementable design documentation under docs/releases/010/design.
The design plan covers architecture boundaries, data and interaction contracts, workflow behavior, and traceability needed for implementation and test planning.

## Scope

In scope:

- Define and update release 010 design documentation in docs/releases/010/design.
- Convert requirement intent in docs/releases/010/requirements into clear design contracts.
- Define module boundaries, source adapters, data model ownership, and workflow orchestration behavior.
- Define design traceability needed for test strategy and implementation handoff.

Out of scope:

- Production implementation code.
- Test case authoring and SIT or UAT execution.
- MVP or later release expansion.
- Data migration solution design.

## Inputs and target outputs

Primary requirement input set:

- docs/releases/010/requirements/*.md

Target design output set:

- docs/releases/010/design/*.md

## Milestone task table

| seq | id    | status  | task                               |
| --- | ----- | ------- | ---------------------------------- |
| 01  | 04.01 | closed  | design scope baseline              |
| 02  | 04.03 | closed  | architecture and boundaries        |
| 03  | 04.04 | open    | domain behavior                    |
| 04  | 04.05 | pending | UI and interaction                 |
| 05  | 04.06 | pending | data model and lineage             |
| 06  | 04.07 | pending | integration                        |
| 07  | 04.08 | pending | error and exception handling       |
| 08  | 04.09 | pending | design quality gate review         |
| 09  | 04.10 | pending | implementation handoff package     |

## Task details

_04.01 (closed) design scope baseline_

- Confirm release boundary and milestone objective for design documentation.
- Confirm source of truth for requirements and target design output path.
- Confirm closure conditions and handoff quality gates for milestone 04.
    
Closure criteria:

- Release scope boundary and out-of-scope exclusions.
- Requirements source path and design output path.

Subtasks:

| seq | id       | status  | task                            |
| --- | -------- | ------- | ------------------------------- |
| 01  | 04.01.01 | closed  | release scope verify            |
| 02  | 04.01.02 | closed  | requirements source lock        |
| 03  | 04.01.03 | closed  | design output path lock         |
| 04  | 04.01.04 | closed  | closure criteria define         |

_04.03 (open) architecture and boundaries_

- Define end to end architecture, layer boundaries, and service responsibilities.
- Define read and write boundaries across Google Sheets, HomeBudget, files, and sqlite.

Target outputs:

- docs/releases/010/design/architecture.md
- docs/releases/010/design/tech-stack.md
- docs/releases/010/design/design-guidelines.md
- docs/releases/010/design/repository-layout.md (update)

Closure criteria:

- System architecture, data sources, user interface, compute, storage components laid out and defined.
- App layers, module boundaries, and data flow paths are documented.
- Read and write boundaries for each source system are explicit.
- Design patterns and conventions, variable naming, coding style, coding patterns, code organization layout, and documentation standards are defined and documented.
- Repository layout reflects final module structure.
- Scope and list of topics for detailed design documentation is defined and mapped to requirement topics.
    Design topics should not map trivially one-to-one with requirements topics. For example, the account classification does not need a design equivalent, it is already sufficient and can be referenced by the design. Design will also include new topics not covered in requirements, such as architecture, API, and data-pipeline.

Subtasks:

| seq | id       | status  | task                                               |
| --- | -------- | ------- | -------------------------------------------------- |
| 01  | 04.03.01 | closed  | system architecture                                |
| 02  | 04.03.02 | closed  | app architecture module boundaries and assumptions |
| 03  | 04.03.03 | closed  | data flow                                          |
| 04  | 04.03.04 | closed  | topic map                                          |
| 05  | 04.03.05 | closed  | tech stack runtime and dependencies                |
| 06  | 04.03.06 | closed  | design patterns and conventions                    |

_04.03.01 (closed) system architecture_

Closure evidence:

- System architecture document created at docs/releases/010/design/architecture.md.
- Architecture includes component catalog table from raw data sources through backend, sqlite, and Google Sheets UI.
- Architecture includes system diagram and component-level specifications with functions, constraints, requirements, and interfaces.

_04.03.04 (closed) topic map_

Design document output inventory mapping all 20 design documents to task origins:

| seq | design doc               | origin task  | purpose                                              |
| --- | ------------------------ | ------------ | ---------------------------------------------------- |
| 01  | architecture.md          | 04.03.01     | system architecture, component catalog, diagrams     |
| 02  | design-guidelines.md     | 04.03.06     | design patterns, naming conventions, coding style    |
| 03  | tech-stack.md            | 04.03.05     | tech stack, runtime profiles, dependencies, libraries |
| 04  | repository-layout.md     | 04.03 update | module structure, file organization, directory map   |
| 05  | data-flow.md             | 04.03.03     | per-stage data paths, source-to-sink lineage         |
| 06  | topic-map.md             | 04.03.04     | requirement-to-design traceability, component coverage |
| 07  | workflows.md             | 04.04.01     | workflow stages, gates, orchestration behavior       |
| 08  | reconciliation.md        | 04.04.02     | match algorithm, tolerance rules, variance handling  |
| 09  | statements.md            | 04.04.03     | statement builder, output format, publish lifecycle  |
| 10  | data-pipeline.md         | 04.04.04     | source ingest, lineage, transformation stages        |
| 11  | bill-payment.md          | 04.04.05     | bill intake, share allocation, HomeBudget posting    |
| 12  | user-interface.md        | 04.05.01     | Google Sheets, CLI, GAS surfaces, workbook structure |
| 13  | homebudget.md            | 04.07.01     | HomeBudget wrapper contract, read/write patterns     |
| 14  | google-sheets.md         | 04.07.02     | Google Sheets adapter contract, import/output flow   |
| 15  | bank-statements.md       | 04.07.03     | bank CSV/Excel import contract, validation rules     |
| 16  | ibkr.md                  | 04.07.04     | IBKR CSV import contract, section extraction         |
| 17  | cpf.md                   | 04.07.05     | bill PDF and cash form input contract, validation    |
| 18  | error-handling.md        | 04.08        | error taxonomy, propagation, recovery flows          |
| 19  | design-index.md          | 04.10.01     | design doc index, status, requirement traceability   |
| 20  | design-issues.md         | 04.09-04.10  | open decisions register, deferred items, closure log |

_04.03.05 (closed) tech stack runtime and dependencies_

Closure evidence:

- Tech stack design document created at docs/releases/010/design/tech-stack.md.
- Runtime baseline defined for Windows local host, Python primary runtime, SQLite canonical persistence, Google Sheets UI, optional GAS bridge, optional Node.js extension runtime, and AWS S3 artifact boundary.
- Component stack matrix completed for all architecture components in docs/releases/010/design/architecture.md, including runtime path and dependency and library mapping.
- Workflow stage stack matrix completed for monthly close stages, bill payment workstream stages, and mapping maintenance workflow stages from docs/releases/010/design/workflows.md.
- Library register documented with required and optional dependencies tied to functional requirements.

_04.03.06 (closed) design patterns and conventions_

Closure evidence:

- Design guidelines document updated at docs/releases/010/design/design-guidelines.md.
- Guidelines now align with selected runtime stack and boundaries: Flask plus Waitress API runtime, direct Google SDK adapter integration, backend-neutral SQL adapter boundary, and required ReportLab PDF render path.
- API guidelines section added with route design, method policy, payload validation, idempotency key policy, error response contract, versioning policy, and a concrete workflow-stage endpoint example.
- Config-driven pattern section added with config domains, startup validation, session configuration freeze policy, precedence rules, and secret reference policy.
- Parameterization section added with stage, reconciliation, ingest, and publish parameter classes, validation rules, and audit persistence requirements.

_04.04 (pending) domain behavior_

- Draft design documentation for each domain behavior component: workflow orchestration, reconciliation, statement building, data pipeline, and bill payment.

Target outputs:

- docs/releases/010/design/workflows.md
- docs/releases/010/design/reconciliation.md
- docs/releases/010/design/statements.md
- docs/releases/010/design/data-pipeline.md
- docs/releases/010/design/bill-payment.md

Closure criteria:

- Each domain behavior doc defines module responsibilities, data contracts, and behavior rules.
- No owner topic has an open unresolved design gap blocking implementation.

Subtasks:

| seq | id       | status  | task                         |
| --- | -------- | ------- | ---------------------------- |
| 01  | 04.04.01 | closed  | workflows                    |
| 02  | 04.04.02 | open    | reconciliation               |
| 03  | 04.04.03 | pending | statements                   |
| 04  | 04.04.04 | pending | data-pipeline                |
| 05  | 04.04.05 | pending | bill-payment                 |

_04.04.02 (open) reconciliation_

Design the reconciliation engine: the match algorithm, tolerance rules, variance handling, and per-account-group procedures for the reconcile stage of the monthly close workflow.

Target output:

- docs/releases/010/design/reconciliation.md

Closure criteria:

- Reconciliation engine module responsibilities and invocation contract with the workflow orchestrator are defined.
- Transaction-level and balance-level method classes are specified with their matching algorithms, parameters, and expected outcomes.
- Account-group procedures are documented for all in-scope groups: bank statement-process, HomeBudget-native, cash, IBKR, CPF, wallets and manual-input.
- Tolerance rules, variance classification, and escalation paths are specified per account group.
- Adjustment transaction contract is defined: fields, category assignment, auto-approve vs user-approval rules, and posting targets.
- HB write-back behavior per account group is specified.
- Reconciliation closure criteria and audit record requirements are defined.

Primary sources:

- `docs/releases/010/requirements/reconciliation-engine.md` — shared workflow phases, method classes, account-group procedures, tolerance and closure rules, adjustment contract, bill accrual conflict policy
- `docs/releases/010/requirements/accounting-logic.md` — reconciliation date policy, reconciliation method classes by account type
- `docs/releases/010/design/workflows.md` (stage 6: reconcile) — orchestrator integration points, step sequence, inputs table, components table, error table; do not duplicate stage-level content; cross-reference it
- `docs/releases/010/design/architecture.md` — reconciliation engine component spec and module boundary
- `docs/releases/010/design/design-guidelines.md` — API, config, parameterization, and naming conventions to apply
- `reference/hb-reconcile/docs/reconcile.md` — legacy reconciliation algorithm and gap equation; use as implementation evidence for method class specifications
- `reference/hb-reconcile/src/reconcile/reconcile.py` — forward and backward transaction matching implementation; use as algorithm evidence, not as baseline contract
- `reference/hb-reconcile/account_settings/txn_heuristics.json` — account-level tolerance values and heuristic controls; use to inform parameter defaults and account-specific heuristic table

Topics the design document must specify:

- Module boundary: what the reconciliation engine owns vs what the workflow orchestrator and account close runtime own
- Invocation contract: how the orchestrator triggers the engine per account and how status is returned
- Method class specifications: transaction-level (forward and backwards algorithm, edits model, gap equation, heuristics, parameters) and balance-level (generic balance equation, outcome classes)
- Account-group procedure table: method class, comparison basis, source schemas, tolerance, adjustment outcome per group
- Variance handling rules: zero variance, within tolerance, exceeds tolerance — approval path and auto-approve conditions for each
- Adjustment transaction fields and posting targets: close_book schema plus HB write-back where applicable
- Bill accrual conflict policy design: how the four conflict classes (no conflict, near-end-of-month, cross-period, partial payment) map to engine behavior
- Reconciliation session record: what is persisted at close, lineage fields, audit trail requirements
- Config and parameter contract: which tolerance values are config-driven, parameterization class for reconcile parameters

Out of scope for this document:

- Stage 6 step sequence (owned by workflows.md)
- Integration adapter contracts for HB wrapper or bank statement parser (owned by 04.07 docs)
- Data pipeline ingest logic (owned by data-pipeline.md)
- Statement builder inputs and outputs (owned by statements.md)

| seq | id          | status  | task                         |
| --- | ----------- | ------- | ---------------------------- |
| 01  | 04.04.02.01 | closed  | semantic matching add        |
| 02  | 04.04.02.02 | open    | ibkr method review           |

_04.04.02.01 (closed) semantic matching add_

add two semantic matching methods

1. **statement-ledger** pair related add-remove edits and convert to `update` edit type, reducing the manual entry burden of categorizing `add` edits
2. **transfer-expense** pair hb bank statement transfer to expenses in the `TWH - Personal` cost center, matching on amount and date proximity, to reduce the manual entry burden of updating HomeBudget expenses in order to ensure the zero-sum property of the cost center when reconciliation edits are applied to the transfers

updates

| seq | id             | status  | task                                                            |
| --- | -------------- | ------- | --------------------------------------------------------------- |
| 01  | 04.04.02.01.01 | closed  | apply updates in impacted locations in requirements and design  |
| 02  | 04.04.02.01.02 | closed  | identify update locations in reconciliation doc                 |
| 03  | 04.04.02.01.03 | closed  | required inputs add hb exp                                      |
| 04  | 04.04.02.01.04 | closed  | outputs add stm_ledger_pairs and xfr_exp_pairs                  |
| 05  | 04.04.02.01.05 | closed  | post condition split into publish and post gates                |
| 06  | 04.04.02.01.06 | closed  | audit checkpoints add semantic matching and xfr-exp gates       |
| 07  | 04.04.02.01.07 | closed  | closure criteria add zero-sum cost center check                 |
| 08  | 04.04.02.01.08 | closed  | module invocation contract outputs add pairs                    |
| 09  | 04.04.02.01.09 | closed  | OOP dispatch add semantic matching and xfr-exp pairing steps    |


_04.05 (pending) UI and interaction_

- Define Google Sheets workbook structure, page inventory, and user touchpoint map for the close session.
- Define CLI command surface and GAS optional extension scope.

Target outputs:

- docs/releases/010/design/user-interface.md

Closure criteria:

- Workbook structure, page inventory, and user touchpoints are documented for all close-session interactions.
- CLI surface and GAS optional scope are defined.
- No UI interaction path has an unresolved design gap.

Subtasks:

| seq | id       | status  | task                            |
| --- | -------- | ------- | ------------------------------- |
| 01  | 04.05.01 | pending | user-interface.md               |

_04.06 (pending) data model and lineage_

- Define canonical entities, keys, and transformation stages from source ingestion to statement outputs.
- Define lineage tracking rules and reproducibility controls for period close outputs.

Target outputs:

- docs/releases/010/design/data-model.md (update)

Closure criteria:

- Canonical entities, keys, and stage schema ownership are documented.
- Lineage fields and reproducibility controls are defined for each transformation stage.
- Data model design is consistent with the accounting logic and reconciliation requirements.

Subtasks:

| seq | id       | status  | task                            |
| --- | -------- | ------- | ------------------------------- |
| 01  | 04.06.01 | pending | canonical entities              |
| 02  | 04.06.02 | pending | stage schema ownership          |
| 03  | 04.06.03 | pending | lineage fields                  |
| 04  | 04.06.04 | pending | reproducibility rules           |

_04.07 (pending) integration_ 

- Define full component design for all integration adapters: HomeBudget wrapper, Google Sheets adapter, and source adapters for bank statements, IBKR, and bill and cash inputs.
- Define input validation, retries, and failure signaling at integration boundaries.

Target outputs:

- docs/releases/010/design/homebudget.md
- docs/releases/010/design/google-sheets.md
- docs/releases/010/design/bank-statements.md
- docs/releases/010/design/ibkr.md
- docs/releases/010/design/cpf.md

Closure criteria:

- Each adapter defines read and write paths, invocation patterns, input validation rules, and error signaling.
- Retry policy and boundary failure handling are documented and consistent across adapters.
- No integration boundary has an unresolved contract gap.

Subtasks:

| seq | id       | status  | task                    |
| --- | -------- | ------- | ----------------------- |
| 01  | 04.07.01 | pending | homebudget.md           |
| 02  | 04.07.02 | pending | google-sheets.md        |
| 03  | 04.07.03 | pending | bank-statements.md      |
| 04  | 04.07.04 | pending | ibkr.md                 |
| 05  | 04.07.05 | pending | cpf.md                  |

_04.08 (pending) error and exception handling_

- Define error taxonomy, propagation paths, and user review checkpoints.
- Define recoverable versus blocking failure handling for close-cycle flows.

Target outputs:

- docs/releases/010/design/error-handling.md

Closure criteria:

- Error taxonomy covers all integration boundaries and close-cycle failure modes.
- Propagation paths and user recovery checkpoints are documented.
- Recoverable and blocking failure categories are explicitly defined.

Subtasks:

| seq | id       | status  | task                            |
| --- | -------- | ------- | ------------------------------- |
| 01  | 04.08.01 | pending | error taxonomy                  |
| 02  | 04.08.02 | pending | propagation path                |
| 03  | 04.08.03 | pending | user recovery flow              |
| 04  | 04.08.04 | pending | blocking criteria               |

_04.09 (pending) design quality gate review_

- Review design package for completeness, consistency, and requirement traceability.
- Confirm readiness for test strategy and implementation handoff.

Target outputs:

- docs/releases/010/design/design-issues.md

Closure criteria:

- All owner requirement topics have a corresponding design document.
- Open design decisions and conflicts are resolved or explicitly deferred with rationale.
- Design package is accepted as complete and ready for test strategy and implementation handoff.

Subtasks:

| seq | id       | status  | task                            |
| --- | -------- | ------- | ------------------------------- |
| 01  | 04.09.01 | pending | requirement trace verify        |
| 02  | 04.09.02 | pending | design consistency review       |
| 03  | 04.09.03 | pending | open issues triage              |
| 04  | 04.09.04 | pending | closure decision draft          |

_04.10 (pending) implementation handoff package_

- Publish implementation-ready design index and unresolved decision register.
- Hand off to test strategy and implementation milestones.

Target outputs:

- docs/releases/010/design/design-index.md
- docs/releases/010/design/design-issues.md (final update)

Closure criteria:

- Design index lists all design documents with status and traceability to requirement topics.
- Unresolved decision register is published with deferred items time-boxed or closed.
- Test strategy and implementation milestones have been formally handed off.

Subtasks:

| seq | id       | status  | task                            |
| --- | -------- | ------- | ------------------------------- |
| 01  | 04.10.01 | pending | design index publish            |
| 02  | 04.10.02 | pending | handoff assumptions capture     |
| 03  | 04.10.03 | pending | test strategy handoff           |
| 04  | 04.10.04 | pending | implementation handoff          |