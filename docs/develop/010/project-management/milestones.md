# Backlog: POC

milestone roadmap for the POC release `0.1.0`.

This document is a project-tracking artifact for milestone status.

Cross-reference boundary:

- Current active requirements work is tracked in [02-requirements.md](02-requirements.md).
- Release intent, scope boundaries, and phase sequencing are defined in [implementation-roadmap.md](../../../requirements/implementation-roadmap.md).
- [implementation-roadmap.md](../../../requirements/implementation-roadmap.md) is a requirements reference document and does not track project-management artifacts.
- This milestone tracker translates roadmap intent into execution checkpoints and status progression.

| seq       |     |         |                          |
| --------- | --- | ------- | ------------------------ |
| id        |     |         |                          |
| status    |     |         |                          |
| milestone |     |         |                          |
| 01        | 01  | closed  | setup dev environment    |
| 02        | 03  | closed  | implementation roadmap   |
| 03        | 02  | open    | requirements             |
| 04        | 04  | pending | design                   |
| 05        | 05  | pending | test strategy            |
| 06        | 06  | pending | test cases               |
| 07        | 07  | pending | build                    |
| 08        | 08  | pending | prerequisites and setup  |
| 09        | 09  | pending | foundation modules       |
| 10        | 10  | pending | connectors               |
| 11        | 11  | pending | backend database         |
| 12        | 12  | pending | front end ui             |
| 13        | 13  | pending | accounting models        |
| 14        | 14  | pending | bank statements          |
| 15        | 15  | pending | cash                     |
| 16        | 16  | pending | account reconcile        |
| 17        | 17  | pending | financial statements     |
| 18        | 18  | pending | ibkr                     |
| 19        | 19  | pending | income                   |
| 20        | 20  | pending | cpf                      |
| 21        | 21  | pending | uat monthly closing      |
| 22        | 22  | pending | uat financial statements |
| 23        | 23  | pending | data migration           |

_01 (closed) setup dev environment_

- Scope: initialize repository workspace, baseline structure, and local tooling prerequisites for POC delivery.
- Closure conditions: repository clone verified, `AGENTS.md` and `.gitignore` present, base folders created, and team can run standard local workflows.

_03 (closed) implementation roadmap_

- Scope: maintain release intent, phase boundaries, and feature progression from current state through POC and later milestones.
- Closure conditions: roadmap tables and scope sections are internally consistent, aligned with requirements, and approved for planning use.

_02 (open) requirements_

- Scope: define user-facing functional and non-functional requirements for POC scope only, including boundaries and acceptance criteria.
- Closure conditions: requirements artifacts are coherent, design-ready, and user-validated with explicit in-scope and out-of-scope boundaries.

_04 (open) design_

- Scope: produce design specifications that implement approved requirements with clear module boundaries, data flows, and interface contracts.
- Closure conditions: design docs cover all release-critical requirements, unresolved ambiguities are closed, and implementation handoff is ready.

_05 (pending) test strategy_

- Scope: define test layers, coverage intent, and quality gates across unit, integration, SIT, and UAT for POC workflows.
- Closure conditions: strategy maps to requirement criticality, includes failure-path validation, and is accepted by design and product stakeholders.

_06 (pending) test cases_

- Scope: create executable test cases aligned to requirements, design contracts, and critical monthly-close workflow checkpoints.
- Closure conditions: test suite includes positive, negative, and edge cases with traceability to requirement outcomes and pass-fail criteria.

_07 (pending) build_

- Scope: implement production code, scripts, and wiring needed to realize approved POC design and requirements.
- Closure conditions: build is reproducible locally, core tests pass, and required features behave as specified for POC operations.

_08 (pending) prerequisites and setup_

- Scope: prepare runtime configuration, credentials, environment variables, and setup steps for local execution of the app stack.
- Closure conditions: setup guide is complete, prerequisites are verifiable, and a new machine can be configured without undocumented steps.

_09 (pending) foundation modules_

- Scope: deliver core shared modules including configuration, logging, validation helpers, and workflow orchestration primitives.
- Closure conditions: modules are reusable, covered by tests, documented at interface level, and integrated without blocking downstream features.

_10 (pending) connectors_

- Scope: implement source adapters for required systems, including stable read paths and controlled write behaviors where approved.
- Closure conditions: connector contracts are validated, error handling is explicit, and source data can be consumed reliably in POC workflows.

_11 (pending) backend database_

- Scope: implement application database schema and persistence behaviors needed for workflow state, lineage, and output reproducibility.
- Closure conditions: schema is versioned, migrations and seed paths are controlled, and required read-write paths are validated by tests.

_12 (pending) front end ui_

- Scope: deliver the POC user interaction surface aligned to workflow checkpoints and user review requirements.
- Closure conditions: key user flows are operable, required inputs and outputs are visible, and acceptance paths are validated in UAT.

_13 (pending) accounting models_

- Scope: implement accounting logic models, classification behavior, and posting rules required for POC financial processing.
- Closure conditions: model behavior matches documented accounting requirements, edge-case handling is defined, and reconciliation dependencies are satisfied.

_14 (pending) bank statements_

- Scope: implement statement ingestion and normalization for in-scope bank accounts with lineage and validation checks.
- Closure conditions: source files parse successfully, normalized outputs are consistent, and statement-driven flows pass reconciliation checks.

_15 (pending) cash_

- Scope: implement cash workflow handling for cash transactions, balances, and related reconciliation behavior in POC scope.
- Closure conditions: cash data paths are validated, variances are surfaced correctly, and close-cycle behaviors align with requirements.

_16 (pending) account reconcile_

- Scope: implement account-level reconciliation workflows, tolerance handling, and user resolution paths for mismatches.
- Closure conditions: reconcile outcomes are deterministic, unresolved items are surfaced correctly, and closure conditions are test-validated.

_17 (pending) financial statements_

- Scope: produce income statement and balance sheet outputs with required mappings, lineage traceability, and review checkpoints.
- Closure conditions: statement outputs are reproducible, mapping rules are honored, and period-close output acceptance criteria pass.

_18 (pending) ibkr_

- Scope: implement IBKR-specific ingestion, transformation, and lineage behaviors needed for POC monthly close.
- Closure conditions: IBKR data paths are validated, derived outputs match requirement expectations, and integration checks pass.

_19 (pending) income_

- Scope: implement income capture, classification, mapping, and posting paths required for POC statement generation.
- Closure conditions: income workflows are complete, mappings are validated, and downstream statement impact is verified by tests.

_20 (pending) cpf_

- Scope: implement CPF input handling, balance logic, and reconciliation behaviors for OA, SA, and MA account paths.
- Closure conditions: CPF rules are correctly applied, variance handling is explicit, and close-cycle acceptance checks pass.

_21 (pending) uat monthly closing_

- Scope: execute end-to-end user acceptance testing for the monthly closing workflow under realistic operational scenarios.
- Closure conditions: critical workflow scenarios pass, defects are triaged with resolution decisions, and user signoff is recorded.

_22 (pending) uat financial statements_

- Scope: execute user acceptance testing focused on financial statement outputs, review steps, and publication readiness.
- Closure conditions: statement accuracy and review workflows are accepted, blocking defects are resolved, and signoff criteria are met.

_23 (pending) data migration_

- Scope: later-phase design and implementation of controlled migration from legacy data stores into app-owned operational data.
- Closure conditions: migration plan, mapping, validation, cutover, and rollback rules are defined and tested; this milestone is outside current POC requirements scope.


