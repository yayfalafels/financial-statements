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
| 02  | 04.04.02 | closed  | reconciliation               |
| 03  | 04.04.03 | open    | statements                   |
| 04  | 04.04.04 | pending | data-pipeline                |
| 05  | 04.04.05 | pending | bill-payment                 |

_04.04.02 (closed) reconciliation_

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

| seq | id          | status  | task                           |
| --- | ----------- | ------- | ------------------------------ |
| 01  | 04.04.02.01 | closed  | semantic matching add          |
| 02  | 04.04.02.02 | closed  | ibkr remove from scope         |
| 03  | 04.04.02.03 | closed  | implemenation ready            |
| 04  | 04.04.02.04 | closed  | resolve gaps                   |

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

_04.04.02.04 (closed) resolve gaps_

| seq | id             | status  | risk | type | issue                                         | classification | resolution                                   |
| --- | -------------- | ------- | ---- | ---- | --------------------------------------------- | --------------- | -------------------------------------------- |
| 01  | 04.04.02.04.01 | closed  |      |      | inventory gaps                                |                 |                                             |
| 02  | 04.04.02.04.02 | closed  |  3   | bug  | forward-backward equivalence not enforced     | partial gap     | implement as mandatory correctness gate     |
| 03  | 04.04.02.04.03 | closed  |  3   | enh  | float arithmetic contamination in gap calcs   | partial gap     | enforce Decimal-only arithmetic pipeline    |
| 04  | 04.04.02.04.04 | closed  |  2   | enh  | config validation at runtime instead startup  | real gap        | validate txn_heuristics.json at agent init  |
| 05  | 04.04.02.04.09 | drop    |  1   | enh  | statement balance mismatch handling unclear   | partial gap     | specify UI integration contract             |
| 06  | 04.04.02.04.06 | drop    |  2   | enh  | heuristic pattern fragility undetected        | partial gap     | specify hit semantics and baseline tracking  |
| 07  | 04.04.02.04.05 | drop    |  2   | enh  | heuristics application audit trail missing    | not a gap       | define session metadata schema and ownership |
| 08  | 04.04.02.04.08 | drop    |  2   | enh  | statement format changes not detected         | not a gap       | implement format version tracking           |
| 09  | 04.04.02.04.07 | drop    |  2   | enh  | ambiguous matches not detected or escalated   | not a gap       | detect and escalate > 5% ambiguity          |
| 10  | 04.04.02.04.10 | drop    |  1   | enh  | cash tolerance not configurable per subtype   | not a gap       | defer to future production enhancement      |

_04.04.02.04.02 (closed) forward backward equivalence not enforced as correctness gate_

**Risk Level:** 3 (Critical)

**Context:** After heuristics application, the forward-pass greedy matching and backward-pass trivial reduction must produce identical edit sets. This equivalence is a mandatory correctness gate, not optional validation. If forward and backward sets diverge, it indicates either a heuristic bug or fundamental algorithmic inconsistency.

**Current state:** reconciliation.md prescribes that forward and backward reduced edit sets must be identical and that divergence is a correctness failure requiring fail-closed behavior.

**Zero-sum mechanism:** exact amount matching in the forward pass is the core mechanism that ensures matched pairs are transaction-level zero-sum on the reconcile gap. When `forward_match()` pairs a ledger row with amount X to a statement row with amount X, removing both from their respective sides results in zero net gap contribution (X on ledger side + (-X) on statement side = 0 gap delta). This property holds at the pair level before heuristics are applied.

**Design specificity gap:** reconciliation.md prescribes fail-closed behavior but does not currently specify: (a) the exact point in the workflow when the check executes, (b) the mechanism for raising an exception and blocking advancement, (c) what metadata must be stored (both forward and backward edit sets), (d) how the symmetric difference is computed and stored for audit trail, (e) what the exception message and recovery workflow should contain.

**Code snippet 1:** this is the heuristic-level guard that preserves the reconcile gap by rejecting any heuristic that changes it.

```python
def apply_account_heuristics(
    account: str,
    edits: pd.DataFrame,
    ledger: pd.DataFrame,
    stmt: pd.DataFrame,
    ledger_end: float,
    statement_end: float,
):
    """
    Apply all heuristics for a given account in sequence.

    Heuristics operate only on the edits set and must preserve the reconcile gap.
    """
    heuristics = list(GENERAL_HEURISTICS) + ACCOUNT_HEURISTICS.get(account, [])
    current_edits = edits.copy()
    total_removed = 0

    for heur_fn in heuristics:
        before_gap = compute_reconcile_gap(ledger_end, statement_end, current_edits)
        edits_new, removed, meta = heur_fn(current_edits, ledger, stmt, account)
        after_gap = compute_reconcile_gap(ledger_end, statement_end, edits_new)

        if after_gap != before_gap:
            print(f"    WARNING: {name} changed reconcile gap; reverting its effect.")
            continue

        current_edits = edits_new
        total_removed += removed
```

**Code snippet 2:** this is the final equivalence check that compares the forward and backward reduced edit sets after heuristics.

```python
    # Consistency check: forward vs backwards reduced after heuristics
    ef_sorted = edits_forward.sort_values(
        ["source", "date", "amount", "edit"]
    ).reset_index(drop=True)
    eb_sorted = edits_backwards.sort_values(
        ["source", "date", "amount", "edit"]
    ).reset_index(drop=True)

    same_shape = ef_sorted.shape == eb_sorted.shape
    same_values = ef_sorted.equals(eb_sorted)
    print("\nForward vs backwards reduced (after heuristics) consistency")
    print(f"  Same shape:  {same_shape}")
    print(f"  Same values: {same_values}")
```

**How the current implementation handles the check:** 

1. **Forward pass with exact matching:** `forward_match()` pairs ledger and statement rows by requiring exact amount equality (within date tolerance). Each matched pair has the property that ledger_amount == statement_amount, ensuring zero net gap contribution when both rows are removed.

2. **Heuristics application with gap preservation guard:** the heuristic loop computes the gap before and after each heuristic and skips any heuristic that changes it. This enforces the invariant that all transformations preserve the zero-sum property of matched pairs.

3. **Backward pass consistency:** backward construction removes forward-matched pairs from the trivial edit set. Because forward matches are zero-sum by construction (exact amount equality), their removal maintains the gap invariant.

4. **Final equivalence check:** both edit sets are compared after heuristics. The check sorts both sets and validates shape and value equality, printing the result. This serves as a correctness gate—any divergence indicates either a heuristic bug or algorithmic inconsistency.

**Why It's an Issue:** The design does not provide enough implementation guidance on how to enforce the fail-closed behavior. Without explicit specification of the exception mechanism, metadata storage, symmetric difference computation, and audit trail capture, implementation teams will infer different approaches. This creates risk of inconsistent enforcement across code paths and incomplete audit trail artifacts needed for reconciliation session validation and operator review.

**Resolution:**
1. add more detail for the forward and backwards algorithm from the reference implementation, specifically on the key controls of the exact match and valid set construction that ensure the zero-sum property before heuristics
2. Specify the execution point: equivalence check must execute after heuristics application and before tolerance evaluation, blocking advancement on divergence.
3. Define exception contract: exception type, message content (forward set, backward set, symmetric difference), and log level.
4. Specify metadata schema: both forward and backward-reduced edit sets stored as reconciliation session attributes, including shape, sorted order, and symmetric difference computed before storage.

_04.04.02.04.03 (closed) float arithmetic contamination in gap calculations_

**Risk Level:** 3 (Critical)

**Context:** All monetary amounts must use Python `Decimal` type with `Decimal(28,2)` precision and `ROUND_HALF_UP` mode. Float arithmetic can accumulate rounding errors that cause gap to be non-zero even when all edits are valid.

**Current state:** reconciliation.md already requires Decimal-only arithmetic, states that all monetary amounts use Decimal(28,2), and explicitly forbids float math in the reconciliation pipeline.

**Why It's an Issue:** Design prescribes Decimal-only arithmetic exclusively (state-2). Implementation uses float throughout: `float(ledger["amount"].cumsum())`, `float(edits["edit_amount"].sum())`, gap computed as `ledger_end + delta - statement_end` with float math. This is a real gap: design requirement is completely ignored in implementation.

**Resolution:**
1. Use `Decimal` type exclusively for all amount, balance, and gap calculations.
2. Never use `float()` conversion or `/` operator on Decimals without explicit `Decimal(x) / Decimal(y)` guards.
3. Add type hints to all reconciliation functions: `gap: Decimal`, `edit_amount: Decimal`, etc.
4. Enforce strict assertions at function entry points: `assert isinstance(gap, Decimal)`.
5. Add lint rules to catch float operations on financial data.

_04.04.02.04.04 (closed) config validation at runtime instead of startup_

**Risk Level:** 2 (Medium)

**Context:** Configuration files (`txn_heuristics.json`, `tolerance_config.json`) define all matching parameters, heuristic rules, and tolerance thresholds. Configuration errors should be caught at agent startup, not during reconciliation execution.

**Current state:** reconciliation.md already treats txn_heuristics.json and tolerance_config.json as ground truth and says they must be discovered at runtime and validated early.

**Why It's an Issue:** Design prescribes validation at agent/session startup with early failure (state-2). Implementation loads and validates config at reconciliation time: `load_heuristics_config()` called inside `apply_account_heuristics()`, no startup entry point. This is a real gap: design's early-detection timing is not implemented; errors only surface during reconciliation execution.

**Resolution:**
1. Validate `txn_heuristics.json` and `tolerance_config.json` at agent startup (or close-session start).
2. Check: file exists, valid JSON, all account names match account dimension, heuristic names match enabled functions, tolerance values are positive decimals.
3. Log all configuration errors with clear messages.
4. Fail agent/session startup if validation fails.
5. Include discovered parameters and config version in reconciliation session metadata for audit trail.

_04.04.02.04.05 (drop) heuristics application audit trail missing_

**Response**: overkill for single-user POC.

**Risk Level:** 2 (Medium)

**Context:** Heuristics are domain-specific, non-obvious rules that modify edit sets. Without detailed audit trail, it is difficult to diagnose why reconciliation succeeded or failed, or to validate heuristic correctness.

**Current state:** reconciliation.md already calls for deterministic heuristics, session metadata capture, and a detailed heuristics application audit trail including removed edits and invariant verification.

**Why It's an Issue:** Design prescribes audit trail collection (state-2): heuristic name, parameters, edits before/after, removed edits. Design also prescribes storage in "reconciliation session metadata" (state-2 phrase: "Store audit trail in reconciliation session metadata"). Implementation captures metadata dict per heuristic but does not define or own the "session metadata" schema or storage responsibility. This is a partial gap: design prescribes *what* to record but not *where* or *how* to persist it, leaving integration contract unspecified.

**Resolution:**
1. Define reconciliation session metadata schema: structure for collecting heuristics audit trail, metadata ownership (reconciliation engine or caller), and persistence responsibility.
2. Specify session metadata contract: what fields are required, who constructs the session object, where does it live (in-memory dict, database row, JSON artifact).
3. Update heuristics functions to populate session metadata with: heuristic name, parameters applied, edits before/after count, removed edits list.
4. Specify audit trail structure: list of heuristic application records with timestamp, name, parameters, removed count, invariant check result.
5. Include session metadata in reconciliation output contract so heuristics audit trail can be persisted and reviewed.

_04.04.02.04.06 (drop) heuristic pattern fragility undetected_

**Response** Good suggestion for full automation phase but current POC still includes human-in-the-loop.  the user will still be involved in anything that the heuristics fail to catch, so if there is a repeated pattern of transactions that the heuristics was previously catching, and now missing, user is in the loop to check and investigate.  This is sufficient for current POC phase.

**Risk Level:** 2 (Medium)

**Context:** Account-specific heuristics (CPF keywords, UOB cashback patterns) depend on consistent transaction description formatting from the source. If statement parsing changes or bank changes description format, heuristics may silently fail to match.

**Current state:** reconciliation.md already notes heuristic parameter discovery from config as ground truth and recommends storing heuristic hit counts in session metadata to detect unexpected drops.

**Why It's an Issue:** Design prescribes hit count tracking in session metadata and baseline monitoring (state-2). Implementation heuristics track removed count, not hit count (successful match count); no session metadata aggregation. Design also does not specify hit semantics: is a hit each heuristic application or each matched subset? This is a partial gap: design prescribes *collection* of hit counts but not the semantics of what constitutes a "hit," leaving implementation ambiguous.

**Resolution:**
1. Clarify hit semantics: define "hit count" as (a) number of times heuristic successfully matched and removed edits, or (b) number of edits heuristic removed. Document which is intended.
2. Define session metadata schema for hit count aggregation: structure for storing per-heuristic hit counts across all account periods.
3. Specify baseline monitoring mechanism: how does the system determine the expected hit count? Is it per-account historical baseline, per-period expected range, or per-heuristic fixed threshold?
4. Update heuristics audit trail to include hit count per heuristic.
5. Specify reporting contract: how and where hit count trends are surfaced to operators (session artifact, GS UI summary, log output).

_04.04.02.04.07 (drop) ambiguous matches not detected or escalated_

**Response**: The algorithm has guards in place to ensure only single match, and there is a manual user review in place. this is sufficient for current POC phase.

**Risk Level:** 2 (Medium)

**Context:** If matching parameters are too loose (large date_tolerance_days or amount_tolerance), one ledger transaction may match multiple statement candidates. This causes the uniqueness test to fail, leaving the transaction unmatched. If heuristics then remove this edit, the final reconciliation appears valid but hides underlying ambiguity.

**Current state:** reconciliation.md already defines candidate matching, deterministic ordering, and a uniqueness failure path, but it does not yet spell out an explicit ambiguity threshold or escalation rule.

**Why It's an Issue:** Design prescribes detection and escalation (state-2): "Log the count of ambiguous matches... If ambiguity exceeds threshold (e.g., > 5% of transactions), escalate to user". Implementation in `forward_match()` silently skips multi-candidate matches with `if len(cand) != 1: continue` — no logging, no threshold check, no escalation. This is a real gap: design's escalation control is completely absent.

**Resolution:**
1. Log the count of ambiguous matches (multi-candidate scenarios) per account per period.
2. If ambiguity exceeds threshold (e.g., > 5% of transactions), escalate to user for review.
3. Include ambiguous match list in session artifact for inspection.
4. Implement tighter default matching parameters and allow account-specific tuning.

_04.04.02.04.08 (drop) bank statement format changes not detected_

**Response**: This is not a gap, it is already covered in scope of source ingest.  Any format change is likely to be detected as a failure exception at source ingest phase, and not leak all the way into reconciliation

**Risk Level:** 2 (Medium)

**Context:** If bank statement format changes unexpectedly (CSV vendor switch, column order change), date or amount parsing may shift. Previously-matched transactions become unmatched mid-period, causing bulk reconciliation failures.

**Current state:** reconciliation.md already says statement slices are built from sorted source rows and that balance mismatches and source-data issues should be surfaced, but it does not define explicit statement format version tracking.

**Why It's an Issue:** Design prescribes format detection and version tracking (state-2): "Implement format detection in bank statement adapter with explicit format version tracking. On format change detected, log warning to GS session UI and block ingest". Implementation has no format detection logic anywhere in statement ingest or reconciliation. This is a real gap: design's format control is entirely unimplemented.

**Resolution:**
1. Implement format detection in bank statement adapter with explicit format version tracking.
2. On format change detected, log warning to GS session UI and block ingest until format is re-confirmed.
3. Provide POC with format re-configuration workflow if expected format changes (seasonal or bank upgrade).
4. Test reconciliation against multiple statement formats in unit tests to catch format sensitivity early.

_04.04.02.04.09 (drop) statement balance mismatch handling unclear_

**Response** Out-of-scope for reconciliation.  if upstream processes ingest are working correctly and have appropriate validation before proceeding to reconciliation, this should not happen, so this is a tail-risk and why there is a catch for user-escalation.

**Risk Level:** 1 (Low)

**Context:** When statement slice ending balance does not match `balances` dataset, the reconciliation behavior is unspecified. Operators need explicit guidance on how to proceed.

**Current state:** reconciliation.md already says opening balance comes from hb_account_dim and that statement ending-balance mismatches should be logged and surfaced to the user, but it still treats the exact user choice flow as guidance rather than a fixed contract.

**Why It's an Issue:** Design prescribes user choice workflow (state-2): "Present explicit user choice: proceed with reconciliation or investigate balance discrepancy... flag in session artifact". Implementation detects mismatch with warning print and continues silently; no user choice mechanism. Design does not specify *who* presents the choice (Python reconciliation module vs. GS UI vs. CLI) or *how* choice flows back to reconciliation. This is a partial gap: design prescribes workflow but spans reconciliation engine and UI layers without specifying the integration contract.

**Resolution:**
1. Specify UI integration contract: who owns presenting the choice (reconciliation engine, GS session UI, CLI), what is the message/prompt format, how does user decision flow back to reconciliation?
2. Update reconciliation output contract to include a "balance_mismatch_flag" field in session metadata indicating whether mismatch occurred.
3. Define the "session artifact" structure: is mismatch flagged in a boolean field, in a list of flagged items, or in a separate validation report?
4. Specify decision flow: if user chooses "investigate," what is the reconciliation outcome? Does it remain pending, abort, or produce a draft?
5. Clarify what "flagged in session artifact" means operationally: is it a field on the session record, a separate issue record linked to session, or an entry in an audit log?

_04.04.02.04.10 (drop) cash tolerance not configurable per subtype_

**Status:** NOT A GAP — Acknowledged POC Limitation

**Risk Level:** 1 (Low)

**Context:** Cash tolerance is currently fixed at ±SGD 20 across all cash accounts. This threshold allows 4% variance on SGD 500 (petty cash) but only 0.2% on SGD 10,000 (safe). For multi-account cash in future, tolerance should be configurable per cash subtype.

**Current state:** reconciliation.md already acknowledges: "POC-scope limitation; requires refinement for production deployment. The design notes cash tolerance is keyed by account group and documents the ±SGD 20 threshold as POC decision for confirmation at production deployment.

**Why It's an Issue:** This is a feature request for future enhancement, not a design gap. The design intentionally limits v0.1.0 to single-threshold POC behavior and marks this as a refinement task for future production deployment.

**Resolution:**
Defer to v0.2.0 or later release. For v0.1.0 POC, confirm that ±SGD 20 threshold is acceptable across all cash accounts at deployment. Plan subtype-specific tolerance configuration (petty_cash_tolerance, safe_tolerance) for future release when multi-account cash is deployed.

_04.04.03 (open) statements_






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

_04.05.01 (pending) user-interface.md_

UI design placeholder for 04.04.02.04.04 (config startup validation and safety guard):

1. Define reconciliation policy config UI surfaces for `txn_heuristics` and `tolerance_config` management.
2. Define validation UX for config edits: field-level errors, blocking save rules, and remediation guidance.
3. Define apply/publish behavior: when approved edits become active and how pre-flight consumes the validated config snapshot.
4. Define safety controls: no direct end-user JSON file editing path in normal operation.
5. Define audit display requirements: show effective config version/snapshot used for the session.

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