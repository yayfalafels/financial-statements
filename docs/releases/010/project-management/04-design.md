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
| 02  | 04.03 | open    | architecture and boundaries        |
| 03  | 04.04 | pending | domain behavior                    |
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
- docs/releases/010/design/design-guidelines.md
- docs/releases/010/design/repository-layout.md (update)

Closure criteria:

- System architecture, data sources, user interface, compute, storage components laid out and defined.
- App layers, module boundaries, and data flow paths are documented.
- Read and write boundaries for each source system are explicit.
- design patterns and conventions, variable naming, coding style, coding patterns, code organization layout, and documentation standards are defined and documented.
- Repository layout reflects final module structure.
- scope and list of topics for detailed design documentation is defined and mapped to requirement topics.
    design topics should not map trivially one-to-one with requirements topics. for example, the account classification does not need a design equivalent, it is already sufficient and can be referenced by the design. design will also include new topics not covered in requirements, such as architecture, api and data-pipeline.

Closure evidence for 04.03.01:

- System architecture document created at docs/releases/010/design/architecture.md.
- Architecture includes component catalog table from raw data sources through backend, sqlite, and Google Sheets UI.
- Architecture includes system diagram and component-level specifications with functions, constraints, requirements, and interfaces.

Closure evidence for 04.03.04:

Design document output inventory mapping all 19 design documents to task origins:

| seq | design doc               | origin task  | purpose                                              |
| --- | ------------------------ | ------------ | ---------------------------------------------------- |
| 01  | architecture.md          | 04.03.01     | system architecture, component catalog, diagrams     |
| 02  | design-guidelines.md     | 04.03.05     | design patterns, naming conventions, coding style    |
| 03  | repository-layout.md     | 04.03 update | module structure, file organization, directory map   |
| 04  | data-flow.md             | 04.03.03     | per-stage data paths, source-to-sink lineage         |
| 05  | topic-map.md             | 04.03.04     | requirement-to-design traceability, component coverage |
| 06  | workflows.md             | 04.04.01     | workflow stages, gates, orchestration behavior       |
| 07  | reconciliation.md        | 04.04.02     | match algorithm, tolerance rules, variance handling  |
| 08  | statements.md            | 04.04.03     | statement builder, output format, publish lifecycle  |
| 09  | data-pipeline.md         | 04.04.04     | source ingest, lineage, transformation stages        |
| 10  | bill-payment.md          | 04.04.05     | bill intake, share allocation, HomeBudget posting    |
| 11  | user-interface.md        | 04.05.01     | Google Sheets, CLI, GAS surfaces, workbook structure |
| 12  | homebudget.md            | 04.07.01     | HomeBudget wrapper contract, read/write patterns     |
| 13  | google-sheets.md         | 04.07.02     | Google Sheets adapter contract, import/output flow   |
| 14  | bank-statements.md       | 04.07.03     | bank CSV/Excel import contract, validation rules     |
| 15  | ibkr.md                  | 04.07.04     | IBKR CSV import contract, section extraction         |
| 16  | cpf.md                   | 04.07.05     | bill PDF and cash form input contract, validation    |
| 17  | error-handling.md        | 04.08        | error taxonomy, propagation, recovery flows          |
| 18  | design-index.md          | 04.10.01     | design doc index, status, requirement traceability   |
| 19  | design-issues.md         | 04.09-04.10  | open decisions register, deferred items, closure log |

Subtasks:

| seq | id       | status  | task                                               |
| --- | -------- | ------- | -------------------------------------------------- |
| 01  | 04.03.01 | closed  | system architecture                                |
| 02  | 04.03.02 | closed  | app architecture module boundaries and assumptions |
| 03  | 04.03.03 | closed  | data flow                                          |
| 04  | 04.03.04 | closed  | topic map                                          |
| 05  | 04.03.05 | open    | design patterns and conventions                    |

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

| seq | id       | status  | task                            |
| --- | -------- | ------- | ------------------------------- |
| 01  | 04.04.01 | closed  | workflows.md                    |
| 02  | 04.04.02 | pending | reconciliation.md               |
| 03  | 04.04.03 | pending | statements.md                   |
| 04  | 04.04.04 | pending | data-pipeline.md                |
| 05  | 04.04.05 | pending | bill-payment.md                 |

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