# Requirements Conflicts and Gaps

**Document Type**: Design Analysis  
**Status**: Complete — Audit findings ready for design review  
**Created**: 2026-04-26  
**Phase**: Design Phase 1 - Discovery and Analysis

This document captures substantive specification gaps, ambiguities, and contradictions discovered during requirements audit. These findings block or constrain design work and require resolution before proceeding.

## Table of contents

- [Schema and data-model gaps](#schema-and-data-model-gaps)
- [Transaction and account classification conflicts](#transaction-and-account-classification-conflicts)
- [Reconciliation and source-of-truth ambiguities](#reconciliation-and-source-of-truth-ambiguities)
- [Specification blockers](#specification-blockers)
- [Cross-document inconsistencies](#cross-document-inconsistencies)
- [Summary by impact](#summary-by-impact)

---

## Schema and data-model gaps

### G-01: Close_book schema specification incomplete

| finding | details |
| --- | --- |
| **scope** | [data-model.md](../../../requirements/data-model.md), [financial-statements.md](../../../requirements/financial-statements.md) |
| **gap** | `close_book` is cited as "single exclusive source for all statement aggregates" but no table definitions, column contracts, or lineage keys are specified. |
| **impact** | Cannot design statement aggregation logic, reconciliation write-back targets, or lineage tracking without knowing close_book schema structure. |
| **blocker** | **yes** |
| **design decision blocked** | Module interface design, data-flow design, reconciliation write-back contract |

### G-02: Bank and bill statement schema ownership unclear

| finding | details |
| --- | --- |
| **scope** | [data-model.md](../../../requirements/data-model.md), [bank-statements.md](../../../requirements/bank-statements.md), [bill-payment.md](../../../requirements/bill-payment.md) |
| **gap** | Data-model.md defines `statements` schema as "bank statement transaction staging." Bill-payment.md defines bill statement parsing with similar contract detail. No clarity on whether bill statements also output to `statements` schema or if there is a separate `bills_staging` layer. |
| **impact** | Schema design must clarify whether `statements` holds both bank and bill data, or if billing belongs exclusively in `bills` schema. Affects reconciliation join paths and lineage. |
| **blocker** | **yes** |
| **design decision blocked** | Data layer design, reconciliation engine schema relationships |

### G-03: Mapping schema version control unspecified

| finding | details |
| --- | --- |
| **scope** | [data-model.md](../../../requirements/data-model.md), [transaction-categories.md](../../../requirements/transaction-categories.md) |
| **gap** | `mapping` schema provides mapping outputs consumed by close_book. No specification for how mapping versions are tracked if mappings change mid-period, whether there are point-in-time snapshots, or whether mapping is current state only. |
| **impact** | If a mapping is corrected after transactions have been classified, unclear whether recalculation is automatic, manual, or not supported. Affects state management and data recovery design. |
| **blocker** | no, but design risk |
| **design decision blocked** | Mapping lifecycle, version control strategy, data correction workflows |





---

## Transaction and account classification conflicts

### C-01: Forex M2M on balances — mechanism and schema placement

| finding | details |
| --- | --- |
| **scope** | [accounting-logic.md](../../../requirements/accounting-logic.md#forex-m2m-on-balances), [transaction-categories.md](../../../requirements/transaction-categories.md) |
| **conflict** | Accounting-logic.md explicitly states: "It is not recorded as an account-level HomeBudget ledger transaction, because HomeBudget ledgers balance in a single currency." Yet transaction-categories.md lists "M2M USD forex on balances" as a component type for income statement placement. |
| **ambiguity** | - Is the M2M computed only at statement aggregation time (not persisted separately)? <br>- Does it flow through close_book or remain purely derivational? <br>- Are only USD-denominated accounts affected, or all non-SGD balances? |
| **impact** | Affects whether M2M is staged as a transaction, computed at aggregation, or computed at statement-render time. Changes data-layer design, reconciliation scope, and close_book schema. |
| **blocker** | **yes** |
| **design decision blocked** | Data layer schema, statement aggregation logic, M2M computation boundary |



### CF-02 Accounting ownership overlap

#### Why this is a gap

Accounting-rule ownership is currently split across multiple requirement pages.
This creates duplicated authority for booking logic, account classification, and
integration-specific accounting treatment.

#### Source evidence

- `docs/requirements/accounting-logic.md`
	- defines baseline accounting logic and posting expectations
- `docs/requirements/ibkr-integration.md`
	- defines IBKR-specific treatment that can overlap baseline accounting policy
- `docs/requirements/cpf-integration.md`
	- defines CPF-specific treatment that can overlap baseline accounting policy
- `docs/requirements/account-classification.md`
	- defines account and category classes used by accounting rules

#### Concrete examples of overlap

- Example 1: integration pages define accounting behaviors that may conflict
	with baseline accounting policy if authority is not hierarchical.
- Example 2: classification terms and posting terms are split across pages
	without explicit precedence.

#### Proposed resolutions

[selected] Resolution option A: establish accounting policy hierarchy (recommended)

1. Keep `accounting-logic.md` as policy owner for global accounting rules.
2. Keep integration pages as constrained extensions with explicit limits.
3. Add explicit section in each integration page:
	 - `inherits from accounting policy`
	 - `integration-specific overrides`
	 - `no override areas`

Resolution option B: flatten all rules into integration pages

1. Move all accounting details to integration pages.
2. Keep baseline page as summary only.

Tradeoff summary:

- Option A preserves consistency and reduces drift.
- Option B is faster for local edits but raises contradiction risk.

#### Recommended closure criteria for CF-02

CF-02 can be closed when:

- every accounting rule has one primary owner document
- integration pages explicitly reference inherited baseline policy
- override rules are explicit and non-overlapping
- unresolved contradictory statements are removed

### CF-03 Bill and shared-cost split implementation gap

#### Why this is a gap

Split decision is selected for two normative owner pages, but strict boundary
implementation and required content coverage are incomplete. This leaves
ownership ambiguity and drift risk in current wording.

#### Bill payment intent

- The app will replace the current bill-payment workflow maintained in Notion.
- Notion will be deprecated for active bill-payment operations.
- Notion artifacts are legacy references only and are not maintained as
	ongoing operational sources.

#### Source evidence

Current bill-payment process overview from primary sources:

- monthly process starts with statement collection and bill parsing,
	then shared-cost allocation review, then posting to HomeBudget
- bill-level checkpoints track bill name, amount, payee, billing cycle,
	paid status, and payment date
- period-level coverage checkpoints track monthly bill count and paid count
- recurring payee continuity is available from payee-linked bill history
- shared settlement handling is intended to flow through HomeBudget settlement
	account `30 CC Hashemis`

Primary sources and what each provides:

---

## Specification blockers

### B-01: CPF interest posting mechanism and date handling

| finding | details |
| --- | --- |
| **scope** | [cpf-integration.md](../../../requirements/cpf-integration.md#interest-income-requirements) |
| **gap** | Specification says "interest is credited annually" and "the system shall flag interest entries greater than zero outside of the expected annual credit period for user confirmation." But doesn't specify:  - What is the "expected annual credit period"? (A specific calendar month, e.g., March?) <br> - If CPF interest is credited in Month N but for contribution period ending Month M, which period is it booked to? <br> - Is the transaction posted via HomeBudget wrapper or as a statement-level adjustment? |
| **impact** | Affects CPF reconciliation procedure, HomeBudget posting logic, and income statement categorization. |
| **blocker** | **yes** |
| **design decision blocked** | CPF reconciliation workflow, CPF transaction posting design |

### B-02: IBKR position valuation transaction model

| finding | details |
| --- | --- |
| **scope** | [ibkr-integration.md](../../../requirements/ibkr-integration.md) |
| **gap** | Specification defines top-down derivation for position change and capital gains, but doesn't specify:  - What HomeBudget transactions are created? Only end-of-period M2M? Individual trade records? Neither? <br> - Is intramonth trading activity recorded at transaction level, or only aggregated as end-of-month position delta? <br> - What schema holds intermediate derivation before validation? |
| **impact** | Affects IBKR reconciliation procedure, HomeBudget posting design, and close_book structure for investment accounts. |
| **blocker** | **yes** |
| **design decision blocked** | IBKR transaction posting design, IBKR reconciliation procedure, investment schema structure |

### B-03: Bill statement parsing contract is incomplete

| finding | details |
| --- | --- |
| **scope** | [bill-payment.md](../../../requirements/bill-payment.md) |
| **gap** | Bill-payment.md sections 1A through 1D define bill statement parsing contracts, but Section 2 (Transaction Generation) and the complete deterministic pipeline are cut off or partially visible. Missing specifications:  - What are the complete required output transaction fields from Section 2A? <br> - How are parsed bill records transformed into HomeBudget transactions? <br> - What is the complete 8-stage pipeline as promised in Section 1C? |
| **impact** | Cannot design bill parsing module or bill transaction posting without complete contract. |
| **blocker** | **yes** |
| **design decision blocked** | Bill parsing module design, bill transaction posting design |

### B-04: Lineage anchor for parsed statements

| finding | details |
| --- | --- |
| **scope** | [bank-statements.md](../../../requirements/bank-statements.md#validation-and-error-policy) |
| **gap** | Bank-statements.md requires lineage assignment with fields like `statement_ref` and `statement_line_ref`, but doesn't specify:  - What is the lineage "parent" — the physical statement file, the download session, or something else? <br> - How is file identity captured if user renames the file between runs? <br> - If the same file is re-parsed, is the prior parsed output updated or replaced? <br> - Is file integrity checked (hash, timestamp) to detect re-parse of same file? |
| **impact** | Affects reconciliation traceability, duplicate-detection logic, and audit-trail design. |
| **blocker** | no, but design risk |
| **design decision blocked** | Lineage key design, statement file identity management, re-parse idempotency |

### B-05: Transaction uniqueness vs. identity definition

| finding | details |
| --- | --- |
| **scope** | [accounting-logic.md](../../../requirements/accounting-logic.md#unique-transaction-and-de-duplication-logic) |
| **gap** | Uniqueness is defined as: "account, transaction date, amount, description." But doesn't specify:  - Is uniqueness scoped per-day, per-session, or across the entire database? <br> - If two identical transactions legitimately occur on the same day (e.g., two identical purchases), how is the duplicate system prevented from merging them incorrectly? <br> - At what point is uniqueness checked: source-ingest time, close_book consolidation, or both? <br> - What is the remediation if a true duplicate is found after posting to HomeBudget? |
| **impact** | Affects de-duplication logic, transaction identity design, and reconciliation procedure. Risk of incorrect duplicate elimination or undetected actual duplicates. |
| **blocker** | **yes** |
| **design decision blocked** | Transaction de-duplication algorithm, transaction identity contract |

| state     | meaning                                            | next states     |
| --------- | -------------------------------------------------- | --------------- |
| pending     | bill identified but not yet paid                   | paid, scheduled |
| scheduled   | payment is planned for a future date within period | paid            |
| paid        | payment confirmed with bank-statement transaction  |                 |

Active bill scope:

- a bill is either active or inactive; there is no period-scoped roster or
	historical dimension tracking
- reconciliation checks apply only to active bills in the current period
- inactive bills are excluded from count and resolution checks

bill data model:

| field           | type | req | rule                                    |
| --------------- | ---- | --- | --------------------------------------- |
| name            | text | y   | unique bill identifier                  |
| payee           | text | y   | counterparty receiving payment          |
| amount_type     | enum | y   | fixed or variable                       |
| expected_amount | dec  | n   | required when amount_type is fixed, SGD |
| billing_cycle   | enum | y   | monthly, quarterly, or annual           |
| active          | bool | y   | true means included in period checks    |

Close criteria for bill lifecycle:

- a bill may close only in `paid` or `scheduled` state
- a bill in `pending` state at session close blocks
	period closure
- once a bill reaches `paid`, it requires bank-statement transaction linkage
	to satisfy the session completion rule

Bill-payment and shared-cost lifecycle relationship:

- bill payment and shared-cost settlement are separate process tracks
- bill records may be `paid` or not paid independent of shared-cost settlement
	status
- shared-cost records may be settled or unsettled independent of bill paid
	status
- the only lifecycle dependency across the two tracks is that bill amount must
	be defined before shared-cost settlement can occur
- ownership of this linkage rule belongs to
	`docs/requirements/shared-costs.md`, because shared-cost
	settlement is a derived process on top of bill payment

Reconciliation checks by scope:

Bill-level checks:

| id | check | source fields |
| -- | ----- | ------------- |
| 01             | amount match               | bill `amount` vs statement line item |
| 02             | payee match                | bill `payee` vs statement payee      |
| 03             | payment date within period | bill `payment_date` vs close period  |
| 04             | paid status complete       | bill `paid` flag                     |

| id | check | pass condition |
| -- | ----- | -------------- |
| 01             | amount match               | amounts equal within SGD 0.00 tolerance                        |
| 02             | payee match                | payee maps to same approved counterparty                       |
| 03             | payment date within period | date falls within 2 months before or after the period end date |
| 04             | paid status complete       | flag is true and linkage ref is present                        |

Period-level checks:

| id | check | source fields |
| -- | ----- | ------------- |
| 01             | bills count matches      | `bills_count` vs active bill rows |
| 02             | bills paid count matches | `bills_paid` vs active bill rows  |
| 03             | all bills resolved       | bill state distribution           |

| id | check | pass condition |
| -- | ----- | -------------- |
| 01             | bills count matches      | count equals number of active bills for the period |
| 02             | bills paid count matches | paid count equals active bills in `paid` state     |
| 03             | all bills resolved       | no active bill remains in pending state            |

#### Field-level contract examples and validation baseline

Field-level contract means each in-scope field has explicit requirement-level
definition for type, requiredness, allowed values or range, derivation rule,
and failure action when validation fails.

Examples:

- `status` must be either `created` or `recorded`; it indicates whether the
  shared transaction has been recorded in HomeBudget.
- `payer` must map to an approved counterparty identifier; unmapped values
	are invalid and block settlement posting.
- `user_share_amount` must not exceed `total_amount` in absolute value and
	must round to 2 decimal places.
- `user_share_amount` is derived from shared percentage splits; when no explicit
	percentage is provided, the default split is equal by 1/N where N is the
	number of participants.
- `period_month` and `period_year` must map to exactly one monthly close period;
  cross-period records are invalid.

Validation baseline for shared-cost records,
`gsheet/shared-expenses.json` range `records!A:H`:

| id                  | field             | type    | req | rule                    |
| ------------------- | ----------------- | ------- | --- | ----------------------- |
| 01                  | record_date       | date    | y   | posting date            |
| 02                  | description       | text    | y   | short narrative         |
| 03                  | total_amount_sgd  | decimal | y   | gross shared amount     |
| 04                  | user_share_pct    | decimal | n   | percent split input     |
| 05                  | user_share_amount | decimal | n   | derived: pct x total    |
| 06                  | category          | text    | y   | allocation class        |
| 07                  | payee             | text    | y   | settlement counterparty |
| 08                  | status            | enum    | y   | HB record state         |

| id                  | field             | validation baseline            |
| ------------------- | ----------------- | ------------------------------ |
| 01                  | record_date       | valid date and within close mo |
| 02                  | description       | 1 to 200 chars                 |
| 03                  | total_amount_sgd  | signed decimal and scale 2     |
| 04                  | user_share_pct    | > 0 and <= 1.0                 |
| 05                  | user_share_amount | abs value <= abs total         |
| 06                  | category          | in allowed shared-cost set     |
| 07                  | payee             | non-empty and mapped party     |
| 08                  | status            | created or recorded            |

Shared-cost parameter constraints:

Session completion rule for shared costs:

- if any shared-cost record remains incomplete for HomeBudget recording,
	the session is incomplete

| id                  | parameter              | type    | req | rule                  |
| ------------------- | ---------------------- | ------- | --- | --------------------- |
| 01                  | split_basis            | const   | y   | percentage split only |
| 02                  | rounding_mode          | enum    | y   | monetary rounding     |
| 03                  | settlement_account     | text    | y   | HB settlement account |
| 04                  | settlement_currency    | enum    | y   | posting currency      |
| 05                  | variance_tolerance_sgd | decimal | y   | max allowed variance  |

| id                  | parameter              | validation baseline       |
| ------------------- | ---------------------- | ------------------------- |
| 01                  | split_basis            | pct                       |
| 02                  | rounding_mode          | half-up to 2 dp           |
| 03                  | settlement_account     | must equal 30 CC Hashemis |
| 04                  | settlement_currency    | SGD only                  |
| 05                  | variance_tolerance_sgd | fixed 0.00                |

Validation baseline for consumption records:

| id                  | field                | type    | req | rule                  |
| ------------------- | -------------------- | ------- | --- | --------------------- |
| 01                  | period_year          | int     | y   | close period year     |
| 02                  | period_month         | int     | y   | close period month    |
| 03                  | utility_type         | enum    | y   | metric family         |
| 04                  | usage_value          | decimal | y   | measured quantity     |
| 05                  | usage_unit           | enum    | y   | measurement unit      |
| 06                  | billed_amount_sgd    | decimal | y   | billed total          |
| 07                  | statement_issue_date | date    | y   | source statement date |
| 08                  | statement_due_date   | date    | n   | payment due date      |
| 09                  | source_account       | text    | y   | paying account        |
| 10                  | source_statement_ref | text    | y   | lineage key           |

| id                  | field                | validation baseline            |
| ------------------- | -------------------- | ------------------------------ |
| 01                  | period_year          | 2000 to 2100                   |
| 02                  | period_month         | 1 to 12                        |
| 03                  | utility_type         | electricity water gas          |
| 04                  | usage_value          | signed decimal                 |
| 05                  | usage_unit           | kwh or m3                      |
| 06                  | billed_amount_sgd    | signed decimal and scale 2     |
| 07                  | statement_issue_date | valid date                     |
| 08                  | statement_due_date   | >= issue date when present     |
| 09                  | source_account       | in bills in-scope account list |
| 10                  | source_statement_ref | unique within period and payee |

Consumption parameter constraints:

| id                  | parameter            | type | req | rule            | validation baseline         |
| ------------------- | -------------------- | ---- | --- | --------------- | --------------------------- |
| 01                  | missing_value_policy | enum | y   | null handling   | block                       |
| 02                  | duplicate_row_policy | enum | y   | dedupe handling | reject_same_ref_same_period |

#### Concrete examples of overlap

- Example 1: payment capture, payment status, and settlement behavior appear in
	both documents without explicit split-boundary tags and precedence rules.
- Example 2: shared-cost allocation and reimbursement logic appear in both
	documents without explicit ownership boundaries.
- Example 3: Notion deprecation intent is not expressed as a formal requirement
	boundary, so legacy-reference usage and active app ownership remain
	underspecified.

#### Decision status

Decision is confirmed: strict topic split across two normative owner pages.

Additional decision captured:

- bill-payment and shared-cost variance tolerance is fixed at SGD 0.00

#### Resolution direction

Implement strict split across two normative owner pages:

1. Keep both pages as normative owners.
2. Split boundaries by payment lifecycle versus shared-cost modeling and re-name accordingly.
3. Add strict cross-page ownership tags and source-authority boundaries.
4. Add explicit cross-links and ownership headers in both pages.

#### Residual gaps after primary-source review

The following gaps still remain after reviewing available primary sources.
These are not already fully addressed in normative requirement pages.

Cross-page split implementation gaps:

- explicit split-boundary headers are still missing in both owner pages,
	`Primary scope`, `Out of scope`, and `See also`
- publish the decided lifecycle-link rule as normative requirements: bill
	payment and shared-cost settlement are separate tracks, and bill amount must
	be defined before shared-cost settlement can occur
- cross-page acceptance criteria are not yet defined for split closure

`docs/requirements/bill-payment.md` residual content scope:

- publish the bill data model defined in this analysis, including `name`,
	`payee`, `amount_type`, `expected_amount`, `billing_cycle`, and `active`
- publish the bill lifecycle state model defined in this analysis, with states
	`pending`, `scheduled`, and `paid`, and the close criteria requiring `paid`
	or `scheduled` at session close
- publish the active bill scope rule: a bill is either active or inactive, and
	reconciliation checks apply only to active bills
- publish the bill-level and period-level reconciliation checks defined in this
	analysis, including amount match, payee match, payment date, paid status,
	bills count, bills paid count, and all-bills-resolved checks
- publish the bill-payment session completion rule: each bill is either paid
	with bank-statement transaction linkage or scheduled to be paid

`docs/requirements/shared-costs.md` residual content scope:

- publish the shared-cost field contracts defined in this analysis, including
	all eight fields of `records!A:H` and the `status` created or recorded rule
- publish the session completion rule: if any shared-cost record remains
	incomplete for HomeBudget recording, the session is incomplete
- publish the shared-cost parameter constraints defined in this analysis,
	including `split_basis`, `rounding_mode`, `settlement_account`,
	`settlement_currency`, and `variance_tolerance_sgd` fixed at SGD 0.00
- publish the consumption record field baseline defined in this analysis,
	ten fields covering period, utility type, usage, billing amount, and lineage
- publish the consumption parameter constraints: `missing_value_policy` block
	and `duplicate_row_policy` reject same ref same period
- publish ownership for lifecycle-link specification in shared-cost page,
	because shared-cost settlement is derived from bill-payment outputs

## Documentation Gaps

### DG-01 Empty requirements index

#### Closure criteria for DG-01

- `docs/requirements.md` contains a complete ownership index
- every active requirement area has one linked owner document
- no orphaned subtopic document remains unindexed

#### Why this is a gap

`docs/requirements.md` does not provide a canonical ownership index
for requirement areas, boundaries, and cross-links.

#### Source evidence

- `docs/requirements.md` (minimal structure)
- multiple subtopic docs in `docs/requirements/*` with no consolidated owner map

#### Resolution direction

Create a canonical requirements index in `docs/requirements.md` that defines:

- requirement area ownership
- required subtopic links
- explicit scope and out-of-scope boundaries
- handoff intent for design readiness

### DG-02 Missing lineage page

#### Closure criteria for DG-02

- lineage page exists with explicit source precedence rules
- lineage requirements are linked from related requirement areas
- lineage acceptance criteria are defined

#### Why this is a gap

Lineage expectations are referenced but no canonical lineage requirement page
exists to define source precedence, traceability, and audit boundaries.

#### Source evidence

- references to lineage intent in workflow and integration documents
- missing destination page: `docs/requirements/source-systems-lineage.md`

#### Resolution direction

Create `docs/requirements/source-systems-lineage.md` and define:

- source system catalog and precedence rules
- lineage requirements from source to output artifacts
- minimum audit and trace requirements

#### Current status

The canonical lineage requirement page now exists at
`docs/requirements/source-systems-lineage.md`.

The page defines source precedence, traceability requirements, and acceptance
criteria, so the original missing-page condition is resolved.

#### Residual gap

Residual work is now linkage and ownership alignment, not page creation:

- ensure owner-page cross-links from related requirement pages consistently
	point to the lineage page
- ensure `docs/requirements.md` owner index reflects lineage-page ownership
	and boundaries without ambiguity

### DG-03 Missing category mapping page

#### Closure criteria for DG-03

- mapping page exists with explicit mapping requirements
- required mapping validation behavior is specified
- mapping owner scope and workflow boundary are explicit

#### Why this is a gap

The two-stage category mapping model is implemented and documented at the
data-source level. The remaining gap is not mapping logic discovery; it is
publishing the existing logic in a dedicated requirements owner page that is
explicitly designated as the source of truth for mapping requirements.

Specific missing requirement statements:

- Stage 1 income-path policy is not yet stated in a dedicated mapping
	requirements owner page.
- Main monthly close session workflow boundary versus event-driven mapping
	change workflow boundary is not yet stated in the mapping requirements owner
	page.

Scope boundary decision:

- If any mapping is ambiguous or incomplete, close cannot proceed. This is
	outside DG-03 mapping scope and belongs to dedicated exception and error
	handling requirements.

#### Source evidence

The category mapping from raw transaction to published statement line item
operates in two distinct stages. The concept is formally defined in the
`Three-Stage Category Mapping` section of skill
`.github/skills/data-sources-inspect/SKILL.md`.

**Stage 1: HomeBudget category â†’ GL account**

Stage 1 maps HomeBudget expense categories to an internal GL account code. The
mapping data lives in the `cat_map` region of the helper workbook configured at
`gsheet/homebudget-workbook.json`. It covers expense categories only and
contains 181 rows across 10 columns. There is no equivalent Stage 1 mapping for
income transactions; income categories are assigned during the monthly closing
workflow rather than maintained as HomeBudget master data.

**Stage 2: GL account â†’ financial statements category**

Stage 2 takes the GL-enriched transaction bridge and maps it into the line items
of the published income statement and balance sheet. It is implemented inside
the `gsheet/financial-statements.json` workbook and operates through two
parallel mapping paths:

- Income statement path: source feeds (`hb_exp`, `hb_inc`, `hb_xfr`,
  `stm_txns`) are merged into `hb_gl`, which enriches each row with `amount_SGD`,
  `fa_budget`, `fa_category`, and `fa_subcategory`. The dimension table
  `fin_exp_cat_map` (33 rows, 5 columns: `fin_stm_category`, `COLE`,
  `fa_category`, `fa_subcategory`, `custom logic`) maps those enriched fields to
  income statement line items. Reconcile rollup regions
	(`reconcile_exp_cost_centers` â†’ `reconcile_fin_stm_summary`) aggregate the
	mapped rows before publication to `income_statement`.

- Balance sheet path: the `accounts` region (29 rows, 7 columns: `id`, `type`,
  `owner`, `name`, `currency`, `HB account`, `stm account`) assigns each account
  to its balance sheet bucket and class. Period-ending balances come from the
  `balances` region. Currency conversion uses `forex_rates`. Rollup regions
  (`reconcile_bal_by_acct` â†’ `reconcile_bal_summary`) aggregate per-class before
  publication to `balance_sheet`.

Stage 2 is fully documented in
`docs/develop/data-sources/financial-statements-gsheet.md`, which covers the
live workbook region map, schema evidence from inspection artifacts, accounting
logic notes, and parity-check results confirming 5/5 mapping gates pass. The
legacy cross-reference source for the income statement mapping is
`data/financial-statements-reconcile/reconcile.csv`.

Session-close completeness gate from current decisions:

- Mapping must be complete for both income and expenses for a session to close.
- If mapping is ambiguous or incomplete, close cannot proceed.
- Ambiguous or incomplete mapping stop behavior remains in dedicated exception
	and error handling scope.

**What is missing**

- destination owner page is still missing: `docs/requirements/transaction-category-mapping.md`
- normative mapping requirements are still not published in requirements docs,
	including Stage 1 income-path policy and session-close completeness for both
	income and expenses

#### Residual gap

Residual gap is limited to requirements publication and owner designation:

- document the already-known Stage 1 and Stage 2 expected-condition mapping
	behavior in `docs/requirements/transaction-category-mapping.md`
- state that category-mapping checks and reviews are event-driven and occur
	outside the main monthly close session workflow
- publish the documented session-close completeness gate in the mapping owner
	page, complete mapping for both income and expenses

#### Resolution direction

Create `docs/requirements/transaction-category-mapping.md` and define:

- mapping-stage ownership and source-of-truth boundary
- explicit non-overlap ownership boundary with related requirement pages:
	`accounting-logic.md`, `account-classification.md`,
	`source-systems-lineage.md`, `ibkr-integration.md`,
	`cpf-integration.md`, and `cash-reconcile.md`
- mapping rules and validation requirements for expected-condition operations
- event-driven mapping-change workflow boundary outside the main session
	workflow
- mapping acceptance criteria for each closing period
- explicit out-of-scope note for ambiguous or incomplete mapping stop behavior,
	referenced to exception and error handling requirements

### DG-04 Missing reconcile engine page

#### Closure criteria for DG-04

- reconcile engine page exists and is designated as owner document
- tolerance and escalation policies are explicit and testable
- reconcile closure criteria are linked from workflow and lifecycle docs

#### Why this is a gap

Reconciliation engine requirements are distributed across several documents but
there is no single owner page for reconcile policy, tolerance behavior, and
closure criteria.

#### Source evidence

- `docs/requirements/cash-reconcile.md` (partial behavior)
- glossary and workflow references to reconcile checkpoints
- missing destination page: `docs/requirements/reconciliation-engine.md`

#### Current reconciliation process and logic

The owner page is missing, but current reconciliation process logic is already
available across requirements artifacts and reference implementations.

Primary sources that define current behavior:

- `docs/requirements/accounting-logic.md`
	- account-level and transaction-level reconciliation methods
	- reconciliation date handling and pending-transaction treatment
	- account-type-specific reconciliation paths
- `docs/requirements/cash-reconcile.md`
	- cash residual-gap equation, review flow, adjustment flow, and reporting flow
	- source inputs and outputs for cash reconciliation session execution
- `docs/requirements/account-classification.md`
	- account and asset classification rules that determine reconcile path behavior
	- account-type constraints that affect allowed transaction classes
- `docs/requirements/current-workflow.md`
	- workflow stage placement for reconcile review in monthly close
- `docs/requirements/glossary.md`
	- canonical terms for reconciliation, variance, tolerance, and checkpoints
- `docs/requirements/source-systems-lineage.md`
	- cross-path reconciliation validation points and lineage requirements
- `docs/requirements/ibkr-integration.md`
	- IBKR reconcile equations, close-gate conditions, and account-specific
	acceptance checks
- `docs/requirements/cpf-integration.md`
	- CPF sub-account balance equation and gap-handling conditions
- `reference/hb-reconcile/docs/reconcile.md`
	- formal edits model, reconcile-gap equation, matching algorithm,
	backwards reduction, and heuristics layer
- `reference/hb-finances/statement_config.json`
	- account-to-statement-table bindings and source file-type configuration
- `reference/hb-finances/gsheet_config.json`
	- statement GL and balance range definitions used for reconciliation datasets
- `reference/hb-finances/statements.py`
	- statement ingestion and normalization entry points by account

Examples of how reconciliation logic can be extracted into the owner
specification:

1. Extract the core reconciliation equations:
	 - cash residual gap from `cash-reconcile.md`
	 - account-level close equation from `accounting-logic.md`
	 - edits-gap closure equation from `hb-reconcile/docs/reconcile.md`
2. Extract matching and edit-generation policy:
	 - amount and date-tolerance matching rules
	 - one-to-one match constraints
	 - unmatched ledger remove and unmatched statement add edit model
3. Extract path-specific acceptance criteria:
	 - bank and credit transaction-level close conditions
	 - IBKR IBA and IRA balance-equation close checks
	 - CPF OA, SA, MA sub-account reconcile requirements
4. Extract source-input contracts:
	 - statement digital twin and HomeBudget ledger dataset requirements
	 - required fields for transaction matching and balance validation
	 - period and account scoping rules for reconcile execution
5. Extract tolerance and stop-behavior checkpoints:
	 - tolerance definitions and review triggers from requirements docs
	 - explicit close-blocking conditions when reconcile equations do not close
	 - user-review checkpoint placement in monthly close workflow

#### Resolution direction

Create `docs/requirements/reconciliation-engine.md` and define:

- reconcile workflow stages and checkpoint expectations
- tolerance rules and variance escalation criteria
- closure criteria and period-level acceptance conditions

## Open ambiguities and information gaps, deprecated

This section is deprecated.

- No unresolved ambiguities remain for this analysis snapshot.
- Prior ambiguity responses were migrated into the relevant conflict and
	misalignment sections as publish-direction bullets.




