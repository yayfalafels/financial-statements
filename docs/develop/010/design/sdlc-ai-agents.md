---
title: SDLC AI Agent Design
doc_type: design
topic_type: reference
owner: learning
scope: poc
---
# SDLC AI Agent Design

## Table of contents

- [Summary](#summary)
- [Reference documents](#reference-documents)
- [Agent inventory](#agent-inventory)
- [SDLC stage task inventory](#sdlc-stage-task-inventory)
  - [Requirements stage](#requirements-stage)
  - [Design stage](#design-stage)
  - [Implementation stage](#implementation-stage)
  - [SIT stage](#sit-stage)
  - [UAT stage](#uat-stage)
- [Skills inventory](#skills-inventory)
- [High-criticality tasks and error propagation risks](#high-criticality-tasks-and-error-propagation-risks)
- [Agent capabilities and known shortcomings](#agent-capabilities-and-known-shortcomings)
  - [Strengths by task type](#strengths-by-task-type)
  - [Known shortcomings](#known-shortcomings)
  - [Mitigations and enhancements](#mitigations-and-enhancements)
- [Subagent trial methodology](#subagent-trial-methodology)
  - [Purpose](#purpose)
  - [Trial structure](#trial-structure)
  - [Control setup](#control-setup)
  - [Experimental setup](#experimental-setup)
  - [Task prompt design](#task-prompt-design)
  - [Evaluation criteria](#evaluation-criteria)
  - [Outcome classification](#outcome-classification)
  - [Evidence standards](#evidence-standards)
  - [Trial log format](#trial-log-format)
  - [When to run a trial](#when-to-run-a-trial)
  - [Worked example scenarios](#worked-example-scenarios)

---

## Summary

This document defines the AI agent design for the financial statements POC SDLC, covering agent roles, task inventories by stage, skill requirements, high-criticality risk points, known agent shortcomings and mitigations, and a formal subagent trial methodology for evidence-based evaluation of agent enhancements.

The POC delivers a monthly close workflow that spans pre-flight validation, forex, data ingest, data sync, reconciliation, financial statement generation, and period publish. Each stage presents distinct task types that call on different agent capabilities and domain knowledge. The agent stack in this workspace operates under GitHub Copilot in VS Code agent mode with custom `.agent.md` roles, `.github/skills/` workflow guidance, and `.github/prompts/` task handoff surfaces.

The subagent trial methodology provides a controlled, evidence-based protocol for validating whether a proposed agent enhancement actually improves behavior before it is promoted to the production agent stack.

---

## Reference documents

- [docs/about.md](../../../about.md)
- [docs/requirements/poc.md](../../../requirements/poc.md)
- [docs/requirements/mvp.md](../../../requirements/mvp.md)
- [docs/requirements/workflow-orchestration.md](../../../requirements/workflow-orchestration.md)
- [docs/requirements/financial-statements.md](../../../requirements/financial-statements.md)
- [docs/requirements/reconciliation-engine.md](../../../requirements/reconciliation-engine.md)
- [docs/requirements/accounting-logic.md](../../../requirements/accounting-logic.md)
- [docs/requirements/data-model.md](../../../requirements/data-model.md)
- [docs/requirements/exception-error-handling.md](../../../requirements/exception-error-handling.md)
- [docs/requirements/interaction-approvals.md](../../../requirements/interaction-approvals.md)
- [.github/agents/](../../../../.github/agents/)

---

## Agent inventory

The workspace currently defines five purpose-scoped agents for the monthly close SDLC.

| agent             | role                                                                  | primary surface                                      |
| ----------------- | --------------------------------------------------------------------- | ---------------------------------------------------- |
| `product-manager` | end-user requirements, lifecycle prioritization, milestone ownership  | `docs/requirements/`, `docs/develop/010/project-management/` |
| `design`          | architecture, domain model, data flow, workflow specifications        | `docs/develop/010/design/`                           |
| `code-complete`   | Python implementation from approved design and passing TDD tests      | `src/python/`, `tests/`                              |
| `test`            | TDD strategy, SIT and UAT test design, coverage, and defect isolation | `tests/`, `docs/develop/010/testing/`                |
| `learning`        | agent stack improvements, prompt and skill optimization               | `.github/agents/`, `.github/skills/`, `.github/prompts/` |

Two additional specialized agents are identified as high-value candidates for the POC and MVP SDLC based on domain complexity:

| proposed agent         | rationale                                                                                                  |
| ---------------------- | ---------------------------------------------------------------------------------------------------------- |
| `financial-accounting` | M2M, forex, double-entry, CPF rules, and reconciliation policy require domain-specific validation.         |
| `python-data`          | SQLite schema, pandas pipelines, SQLAlchemy, HomeBudget and sqlite-gsheet wrappers need consistent idioms. |

---

## SDLC stage task inventory

### Requirements stage

The product-manager agent owns this stage. Tasks span end-user workflow translation, constraint documentation, acceptance criteria definition, and requirement traceability.

| id   | task                                                                          | domain                 | agent                                  |
| ---- | ----------------------------------------------------------------------------- | ---------------------- | -------------------------------------- |
| R-01 | Translate monthly close workflow steps into structured requirements            | workflow, UX           | product-manager                        |
| R-02 | Define stage entry and exit criteria for all seven workflow stages             | workflow orchestration | product-manager                        |
| R-03 | Document accounting policy: M2M, forex, double-entry, income vs transfer      | accounting logic       | product-manager + financial-accounting |
| R-04 | Define reconciliation procedures by account group: bank, HB, cash, IBKR, CPF | reconciliation         | product-manager + financial-accounting |
| R-05 | Define category mapping requirements: taxonomy, gates, blocking conditions    | transaction categories | product-manager                        |
| R-06 | Define data model schema ownership and lineage boundaries                     | data model             | product-manager + design               |
| R-07 | Define exception and error handling policy: categories, escalation paths      | error handling         | product-manager                        |
| R-08 | Define user approval checkpoints and confirmation-before-commit policy        | interaction/approvals  | product-manager                        |
| R-09 | Define tolerance thresholds and variance classification rules by account group | reconciliation         | product-manager + financial-accounting |
| R-10 | Define statement layout and roll-up rules for income statement and balance sheet | financial statements | product-manager + financial-accounting |

### Design stage

The design agent owns this stage. Tasks span architecture decisions, domain model, data flow, database schema, and module design.

| id   | task                                                                              | domain               | agent                          |
| ---- | --------------------------------------------------------------------------------- | -------------------- | ------------------------------ |
| D-01 | Design workflow orchestration: stage sequencing, entry/exit, rerun/resume         | architecture         | design                         |
| D-02 | Design domain model: account dim, category dim, GL txn, mapping, period state    | data model           | design                         |
| D-03 | Design SQLite schema for all six schemas in the active schema set                 | database             | design + python-data           |
| D-04 | Design data flow: ingest paths, staging, sync, reconcile, statement aggregation   | data flow            | design                         |
| D-05 | Design HomeBudget wrapper: GL sync, SCD Type 1 refresh, `hb_txn_uid` hashing    | integration          | design + python-data           |
| D-06 | Design reconciliation engine: method classes, balance vs txn-level, adjustments  | reconciliation       | design + financial-accounting  |
| D-07 | Design forex pipeline: rate fetch, period-end translation, M2M IS line           | accounting logic     | design + financial-accounting  |
| D-08 | Design IBKR integration: CSV parse, FIFO gain, unrealized M2M, `close_book` load | investment           | design + financial-accounting  |
| D-09 | Design CPF integration: contribution allocation, OA/SA/MS split, IS effect       | CPF accounting       | design + financial-accounting  |
| D-10 | Design bill payment and shared-cost settlement as a parallel workstream           | bills domain         | design                         |
| D-11 | Design CLI interface: command structure, session state, pre-flight and close-out  | module design        | design                         |
| D-12 | Design error taxonomy and validation strategy: layer boundaries, user output      | error handling       | design                         |

### Implementation stage

The code-complete agent owns this stage. Tasks span Python module implementation, database operations, integration adapters, and CLI.

| id   | task                                                                              | domain                  | agent                                 |
| ---- | --------------------------------------------------------------------------------- | ----------------------- | ------------------------------------- |
| I-01 | Implement pre-flight checks: files, credentials, sheet access, period validation  | Python, orchestration   | code-complete                         |
| I-02 | Implement forex rate fetch and SGD translation pipeline                           | Python, data            | code-complete                         |
| I-03 | Implement HomeBudget data sync: GL txn, dims, `hb_txn_uid` assignment            | Python, HomeBudget      | code-complete + python-data           |
| I-04 | Implement category mapping engine: lookup, completeness gate, missing detection   | Python, data            | code-complete                         |
| I-05 | Implement reconciliation engine: phase exec, match, variance, adjustment          | Python, accounting      | code-complete + financial-accounting  |
| I-06 | Implement bank statement CSV parse, dedup, staging to `statements` schema        | Python, data            | code-complete                         |
| I-07 | Implement IBKR CSV parse, FIFO gain, M2M calculation, `close_book` load          | Python, investment      | code-complete + financial-accounting  |
| I-08 | Implement CPF contribution allocation and period-level `close_book` posting       | Python, CPF             | code-complete + financial-accounting  |
| I-09 | Implement cash staging aggregate ingest from Google Sheets form data              | Python, Google Sheets   | code-complete                         |
| I-10 | Implement HomeBudget CRUD: income, expense, and transfer posting                  | Python, HomeBudget      | code-complete + python-data           |
| I-11 | Implement financial statement aggregation: IS and BS roll-up from `close_book`   | Python, accounting      | code-complete + financial-accounting  |
| I-12 | Implement session close-out: artifact consolidation, log summary, state commit    | Python, orchestration   | code-complete                         |
| I-13 | Implement CLI commands for all workflow stages                                    | Python, CLI             | code-complete                         |

### SIT stage

The test agent owns this stage. Tasks span integration test design and execution across source ingest, data sync, reconcile, and statement generation with real or representative data.

| id   | task                                                                              | domain               | agent                         |
| ---- | --------------------------------------------------------------------------------- | -------------------- | ----------------------------- |
| S-01 | Validate pre-flight: pass/fail on missing inputs, invalid period, bad credentials | test, integration    | test                          |
| S-02 | Validate forex fetch and translation: rate selection, SGD conversion, timing      | test, accounting     | test + financial-accounting   |
| S-03 | Validate HomeBudget sync: GL completeness, dim accuracy, `hb_txn_uid` determinism | test, integration    | test                          |
| S-04 | Validate category mapping gate: missing detection, blocking behavior, error surface | test, data           | test                          |
| S-05 | Validate reconciliation phases: validation, staging, match, variance, adjustment  | test, reconciliation | test + financial-accounting   |
| S-06 | Validate bank statement dedup and staging: no duplicates on rerun                 | test, data           | test                          |
| S-07 | Validate IBKR pipeline: FIFO, realized gain, M2M, `close_book` load correctness  | test, investment     | test + financial-accounting   |
| S-08 | Validate CPF accuracy: contribution split, OA/SA/MS allocation, IS effect         | test, CPF            | test + financial-accounting   |
| S-09 | Validate IS roll-up: section totals, net personal income, M2M lines, net income  | test, accounting     | test + financial-accounting   |
| S-10 | Validate BS roll-up: asset placement, account classification, net worth           | test, accounting     | test + financial-accounting   |
| S-11 | Validate close-blocking conditions block downstream commits as required           | test, error handling | test                          |
| S-12 | Validate rerun/resume: idempotent ingest, no partial-state corruption on failure  | test, integration    | test                          |

### UAT stage

The test agent and product-manager agent collaborate on this stage. Tasks span end-to-end workflow acceptance using real close-period data and user-defined acceptance scenarios.

| id   | task                                                                              | domain               | agent                                  |
| ---- | --------------------------------------------------------------------------------- | -------------------- | -------------------------------------- |
| U-01 | Execute full monthly close walkthrough for a prior period with real data          | end-to-end, workflow | test + product-manager                 |
| U-02 | Verify checkpoint UX: review surfaces present required evidence at each stage     | UX, approvals        | product-manager                        |
| U-03 | Verify statement output matches prior manually produced reference for same period | financial statements | product-manager + financial-accounting |
| U-04 | Verify reconciliation variance explanations are readable and actionable           | reconciliation, UX   | product-manager                        |
| U-05 | Verify error messages are user-readable and provide recovery guidance             | error handling, UX   | product-manager                        |
| U-06 | Verify CLI commands cover the full workflow without manual database access         | CLI, UX              | product-manager                        |
| U-07 | Verify no data loss or corruption on re-run or resume of a partial close          | resilience           | test                                   |
| U-08 | Verify S3 upload, artifact storage, and close-out produce a complete audit trail  | artifacts, audit     | test + product-manager                 |

---

## Skills inventory

The following skills are active in the workspace and their applicable SDLC stages are mapped below.

| skill                        | stages          | primary use case                                                          |
| ---------------------------- | --------------- | ------------------------------------------------------------------------- |
| `homebudget`                 | D, I, S         | HomeBudget wrapper patterns, account/category discovery, GL sync behavior |
| `gsheet-inspect`             | R, D, I, S      | Google Sheets schema, cash-expense form structure, helper workbook review |
| `data-sources-inspect`       | R, D, S         | Cross-source schema discovery, HomeBudget and GS mapping validation       |
| `variable-naming`            | D, I            | Consistent naming across SQL objects, Python variables, config artifacts  |
| `documentation`              | R, D, S, U      | Creating and updating all markdown documentation artifacts                |
| `markdown-tables`            | R, D            | Creating and maintaining structured tables in design and requirements     |
| `python`                     | I               | Idiomatic Python, code review, implementation decisions                   |
| `task-definition`            | R, D, I, S, U   | Tracking task status, subtask definition, milestone readiness             |
| `github-copilot-local-files` | learning        | Inspecting VS Code and Copilot artifacts for session evidence             |

Additional skills identified as high-value candidates for the POC and MVP:

| proposed skill            | rationale                                                                                    |
| ------------------------- | -------------------------------------------------------------------------------------------- |
| `accounting-logic`        | Double-entry, M2M, forex, FIFO, and CPF rules require worked examples to prevent hallucination. |
| `reconciliation-patterns` | Phase templates and tolerance examples reduce procedural errors across D, I, and S stages.   |
| `sqlite-data-pipelines`   | SCD Type 1, UID hashing, and idempotent ingest patterns repeat across nearly every I task.   |

---

## High-criticality tasks and error propagation risks

The following tasks carry the highest potential for error propagation or material impact on functional requirements and user experience. Errors in these tasks are likely to corrupt downstream artifacts, produce incorrect financial figures, or block the close workflow without recoverable guidance.

| id    | task                                              | risk type                           | impact                   |
| ----- | ------------------------------------------------- | ----------------------------------- | ------------------------ |
| HC-01 | Forex rate selection and SGD conversion           | Incorrect rate applied to all FX    | High financial materiality |
| HC-02 | `hb_txn_uid` deterministic hashing               | Non-deterministic or colliding UID  | Silent data corruption   |
| HC-03 | Category mapping completeness gate                | Gate bypassed or wrong evaluation   | Silent financial error   |
| HC-04 | Reconciliation tolerance and adjustment posting   | Incorrect variance classification   | Financial materiality    |
| HC-05 | IBKR FIFO realized gain calculation               | Wrong lot sequencing or per-share gain | Financial materiality |
| HC-06 | CPF contribution allocation split                 | OA/SA/MS amounts incorrect          | Financial materiality    |
| HC-07 | Double-entry posting for HomeBudget CRUD          | Missing or incorrect second leg     | Close-blocking           |
| HC-08 | Close-blocking exception evaluation               | Gate evaluated as pass incorrectly  | Compliance and audit     |
| HC-09 | Balance sheet account type classification         | Wrong asset or liability placement  | Financial materiality    |
| HC-10 | Statement roll-up aggregation boundary            | Transaction leakage across periods  | Financial materiality    |

---

## Agent capabilities and known shortcomings

### Strengths by task type

AI coding agents, including GitHub Copilot in agent mode, perform well on the following task types:

- Generating boilerplate Python modules, CLI argument parsers, and file I/O scaffolding from clear specifications.
- Translating well-defined schema design into SQLite DDL and SQLAlchemy ORM definitions.
- Identifying duplicate code, refactoring for readability, and suggesting idiomatic Python patterns when given sufficient context.
- Writing unit tests for pure functions with deterministic inputs and outputs.
- Generating markdown documentation from structured specifications.
- Searching and synthesizing information across multiple workspace files when the scope is bounded.
- Detecting obvious type errors, missing imports, and structural mistakes during code review.
- Following procedural workflows when step-by-step instructions are explicit and complete.

### Known shortcomings

The following shortcomings are well-documented for LLM-based coding agents operating on domain-specific financial workflows:

**Domain hallucination under ambiguity.** Agents fill knowledge gaps with plausible but incorrect financial domain rules. Double-entry bookkeeping, M2M accounting, FIFO lot sequencing, and CPF contribution rules all require precise calculation that agents approximate or invent when domain guidance is absent.

**Context window degradation.** As conversation depth increases, agents lose earlier context. Early design decisions or schema definitions stated at the beginning of a session may be contradicted by later implementation choices. This is especially dangerous for schema ownership boundaries and accounting policy hierarchy.

**Instruction conflict resolution.** When project instructions, skill guidance, and inline prompt instructions conflict, agents do not reliably apply the highest-priority rule. They tend to follow the most recently seen instruction, which can override earlier project-level policy.

**Weak stopping conditions.** Without explicit completion criteria, agents continue generating code or documentation beyond the required scope. This produces over-engineered solutions, adds unrequested features, and produces diffs that are larger and riskier than necessary.

**Test-implementation co-generation.** Agents tend to write tests that pass against the code they just generated rather than tests that validate correct behavior against an independent specification. This defeats TDD discipline and produces tests with low discriminative power.

**Accounting identity verification.** Agents do not spontaneously verify that double-entry transactions balance, that statement roll-ups sum correctly, or that period-end balances are consistent with opening balances plus net movements. These checks require explicit prompting or dedicated skill guidance.

**Reconciliation procedural discipline.** Reconciliation workflows have strict phase ordering, blocking conditions, and tolerance evaluation rules. Agents skip phases, conflate balance-level and transaction-level methods, or generate adjustment logic that does not match the specified policy.

**Subagent context isolation.** GitHub Copilot subagents operate with an isolated context window. They cannot access the main session's conversation history or previously established facts unless that context is explicitly injected into the subagent prompt.

**Tool over-use during exploration.** Agents call search and file-read tools speculatively, accumulating context that may never be used. This wastes premium requests and can crowd out the actual task context.

### Mitigations and enhancements

| shortcoming                        | mitigation                                                                          | enhancement type          |
| ---------------------------------- | ----------------------------------------------------------------------------------- | ------------------------- |
| Domain hallucination               | Add `accounting-logic` skill with worked M2M, forex, and CPF examples               | New skill                 |
| Context window degradation         | Scope tasks to single-stage boundaries; use handoff prompts to re-anchor context    | Prompt design             |
| Instruction conflict resolution    | Audit overlap in `.github/agents/`, skills, and `AGENTS.md`; set priority hierarchy | Agent instruction update  |
| Weak stopping conditions           | Add explicit completion criteria to every agent definition                          | Agent instruction update  |
| Test-implementation co-generation  | Enforce TDD contract; add hook to reject test and implementation in same commit     | Hook + agent instruction  |
| Accounting identity verification   | Add balance sheet, roll-up, and double-entry assertions to `accounting-logic` skill | New skill                 |
| Reconciliation procedural discipline | Add `reconciliation-patterns` skill with phase templates and tolerance examples   | New skill                 |
| Subagent context isolation         | Require context injection block in all subagent prompts                             | Prompt design             |
| Tool over-use during exploration   | Add max-search-depth guidance; prefer `Explore` subagent for research tasks        | Agent instruction update  |

---

## Subagent trial methodology

### Purpose

The subagent trial methodology provides an evidence-based protocol for evaluating whether a proposed agent enhancement, such as a new skill, instruction change, or prompt modification, actually improves agent behavior on a representative task. Trials produce direct evidence before any change is promoted to the production agent stack.

The method uses two subagents: a control and an experimental. Both receive the same task prompt. The control uses current instructions and skills. The experimental uses the proposed enhancement. Outcomes are compared to determine whether the enhancement produced a measurable improvement.

### Trial structure

Each trial consists of:

1. A defined enhancement hypothesis with a specific predicted improvement.
2. A representative task prompt scoped to a single stage and task type.
3. A control subagent run with current agent instructions, skills, and prompt context.
4. An experimental subagent run with the proposed enhancement applied.
5. Evaluation of both outputs against predefined acceptance criteria.
6. Outcome classification from the four possible result states.

### Control setup

The control subagent receives:

- The current production `.agent.md` instructions for the relevant agent role.
- The current set of skills declared in that agent's instructions.
- A task prompt that is representative of the target task type.
- No enhancement-specific guidance or additional context.

The purpose of the control is to establish a baseline: what does the current agent stack actually produce for this task?

### Experimental setup

The experimental subagent receives:

- The proposed updated `.agent.md` instructions, or the proposed new/updated skill content, injected directly into the subagent prompt.
- The same task prompt used for the control.
- No other differences. The only variable is the enhancement.

The purpose of the experimental is to measure whether the enhancement changes the output in the predicted direction.

### Task prompt design

Trial task prompts must satisfy the following criteria:

- Scoped to a single SDLC stage and a single task type.
- Specific enough to produce a deterministic expected output shape.
- Representative of the actual task that motivated the enhancement hypothesis.
- Not so narrow that only one correct answer exists, but not so broad that evaluation is ambiguous.

Good task prompts cite a specific requirement document, ask for a specific artifact type, and state the acceptance criteria in the prompt itself.

Example prompt structure:

```
Context: [inject relevant design spec or requirement section]
Task: [single, bounded task from the SDLC task inventory]
Acceptance criteria:
- [criterion 1]
- [criterion 2]
- [criterion 3]
```

### Evaluation criteria

Evaluation criteria must be defined before the trial runs. They must be observable in the subagent output without subjective interpretation. Suitable criteria types:

- Presence of a specific accounting identity check in generated code.
- Absence of a known failure mode, such as incorrect lot sequencing or missing double-entry leg.
- Correct application of a specific policy rule from the requirements.
- Structural completeness of a generated artifact, such as all required schema objects present.
- Procedural correctness, such as phases executed in the correct order.

Criteria that rely on the evaluator's judgment of overall quality or "impressiveness" are not suitable. Each criterion must have a binary pass/fail determination.

### Outcome classification

Each trial produces one of four outcome classifications:

| classification                     | control | experimental | interpretation                                                           |
| ---------------------------------- | ------- | ------------ | ------------------------------------------------------------------------ |
| Both pass                          | pass    | pass         | No regression; insufficient evidence of improvement. Consider harder task. |
| Both fail                          | fail    | fail         | Enhancement did not address the root cause. Revise the hypothesis.       |
| Control fails, Experimental passes | fail    | pass         | Direct evidence of improvement. Promote enhancement.                     |
| Control passes, Experimental fails | pass    | fail         | Enhancement introduced a regression. Reject and investigate.             |

The only outcome that constitutes direct evidence for promoting an enhancement is control fails and experimental passes.

### Evidence standards

For an enhancement to be promoted to the production agent stack, the trial evidence must show:

- At least one control-fail / experimental-pass result on a representative task.
- No control-pass / experimental-fail regressions on any other representative task for the same agent role.
- Evaluation criteria were defined before the trial ran, not after.

Informal observation that "the output looked better" is not sufficient evidence. The trial must produce a documented comparison with predefined criteria.

### Trial log format

Each trial must be documented in a trial log entry with the following fields.

```
Trial ID: [unique ID, e.g., T-001]
Date: [YYYY-MM-DD]
Enhancement hypothesis: [what the enhancement is expected to improve and why]
Enhancement type: [new skill | skill update | agent instruction update | prompt update | hook]
Target agent: [agent name]
Task prompt: [full prompt text used for both subagents]
Evaluation criteria:
  - [criterion 1]: pass/fail
  - [criterion 2]: pass/fail
  - [criterion 3]: pass/fail
Control outcome: [pass | fail] + summary of control output
Experimental outcome: [pass | fail] + summary of experimental output
Trial classification: [both pass | both fail | control fail experimental pass | control pass experimental fail]
Decision: [promote | reject | revise hypothesis]
Notes: [any observations about failure mode, unexpected behavior, or follow-up needed]
```

Trial logs are stored at `docs/develop/010/testing/agent-trials/`.

### When to run a trial

Run a trial when:

- A recurring agent failure mode has been identified and a specific enhancement is proposed to address it.
- A new skill is proposed for the `accounting-logic`, `reconciliation-patterns`, or `sqlite-data-pipelines` domains.
- An agent instruction change is proposed that affects scope boundaries, stopping conditions, or role definitions.
- A prompt design change is proposed that would affect all tasks routed to a specific agent.

Do not run a trial when:

- The change is purely cosmetic, such as fixing a typo or reformatting a bullet list.
- The change adds context that is universally beneficial and carries no risk of regression.
- The fix addresses an obvious structural error with no plausible alternative behavior.

### Worked example scenarios

The following scenarios illustrate how the trial methodology applies to the high-priority enhancements identified in this document.

**Scenario 1: Accounting-logic skill for M2M calculation**

Hypothesis: Adding an `accounting-logic` skill with worked M2M examples will cause the code-complete agent to generate IBKR M2M calculations that correctly apply unrealized gain = quantity * (period-end price - period-open price) instead of approximating or omitting the lot adjustment.

Control: code-complete agent without `accounting-logic` skill. Prompt asks for implementation of the IBKR M2M calculation function with a specification from `docs/requirements/accounting-logic.md`.

Experimental: code-complete agent with `accounting-logic` skill content injected into the subagent prompt.

Evaluation criterion: The generated function must produce the correct unrealized M2M value for the worked USO ETF example in `accounting-logic.md` given the same input parameters.

**Scenario 2: Stopping conditions for design agent**

Hypothesis: Adding explicit completion criteria to the design agent instructions will prevent the design agent from expanding schema design beyond the approved POC schema set defined in `docs/requirements/data-model.md`.

Control: design agent without explicit completion criteria. Prompt asks for database schema design for the `statements` schema.

Experimental: design agent with a completion criteria block that names the five approved schemas and states that no new schemas may be introduced without explicit approval.

Evaluation criterion: The experimental output must not define any schema object outside the approved schema set. The control output must define at least one unapproved schema object for the trial to be discriminative.

**Scenario 3: Reconciliation-patterns skill for phase ordering**

Hypothesis: Adding a `reconciliation-patterns` skill with explicit phase templates will cause the test agent to generate reconciliation SIT test cases that validate all five shared workflow phases in the correct order, rather than testing only the comparison and variance phases.

Control: test agent without `reconciliation-patterns` skill. Prompt asks for SIT test cases for the bank statement reconciliation account group.

Experimental: test agent with `reconciliation-patterns` skill content that describes all five phases and their validation checkpoints.

Evaluation criteria:
- Test cases cover Phase 1 input and source validation.
- Test cases cover Phase 2 source staging and aggregation.
- Test cases cover Phase 3 comparison and match.
- Test cases cover Phase 4 variance interpretation and tolerance evaluation.
- Test cases cover Phase 5 adjustment and closure.
