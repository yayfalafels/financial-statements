# Requirements Conflicts and Gaps

## Table of contents

- [Summary](#summary)
- [Scope of Review](#scope-of-review)
- [Conflict Inventory](#conflict-inventory)
- [Documentation Gap Inventory](#documentation-gap-inventory)
- [Data-Source and Requirement Misalignment](#data-source-and-requirement-misalignment)
- [Resolution Priorities](#resolution-priorities)
- [Exit Criteria for This Analysis](#exit-criteria-for-this-analysis)
- [Conflicts](#conflicts)
	- [CF-01 Workflow ownership overlap](#cf-01-workflow-ownership-overlap)
	- [CF-02 Accounting ownership overlap](#cf-02-accounting-ownership-overlap)
	- [CF-03 Bill and shared-cost split implementation gap](#cf-03-bill-and-shared-cost-split-implementation-gap)
- [Documentation Gaps](#documentation-gaps)
	- [DG-01 Empty requirements index](#dg-01-empty-requirements-index)
	- [DG-02 Missing lineage page](#dg-02-missing-lineage-page)
	- [DG-03 Missing category mapping page](#dg-03-missing-category-mapping-page)
	- [DG-04 Missing reconcile engine page](#dg-04-missing-reconcile-engine-page)

## Summary

This document records current conflicts and gaps across requirement artifacts and
related source-reference documents for the POC release.

Current state across documentation gaps:

- DG-01 is resolved, canonical requirements ownership index is published.
- DG-02 is resolved, lineage owner-linkage and index alignment are published.
- DG-03 is resolved, category-mapping owner page is published.
- DG-04 is resolved, reconciliation-engine owner page is published.

Current state across ownership conflicts:

- CF-01 is resolved, workflow ownership split and destination-page coverage are published.
- CF-02 is resolved, accounting policy hierarchy and override boundaries are published.
- CF-03 is resolved, bill-payment and shared-cost boundaries and contracts are published.

Closure actions completed in this pass:

- published canonical owner index at docs/requirements.md
- published workflow owner pages:
	workflow-orchestration.md, interaction-approvals.md, statements-lifecycle.md
- published accounting hierarchy inheritance and override boundaries
- published bill-payment and shared-cost ownership boundaries and lifecycle link
  rule ownership
- published transaction-category-mapping owner page
- published reconciliation-engine owner page
- aligned cash-reconcile tolerance and canonical account naming publication

The goal is to remove ownership ambiguity and publish the remaining owner pages
required for design handoff.

Current status: ownership ambiguity is resolved for this analysis scope.

## Scope of Review

Scope boundary for this analysis step:

- This artifact identifies ownership conflicts and documentation gaps.
- Detailed exception and error handling policy definitions are out of scope here and are handled in a dedicated requirements owner document.

Reviewed requirement artifacts:

- `docs/requirements.md`
- `docs/requirements/accounting-logic.md`
- `docs/requirements/current-workflow.md`
- `docs/requirements/bill-payment.md`
- `docs/requirements/shared-costs.md`
- `docs/requirements/homebudget.md`
- `docs/requirements/google-sheets.md`
- `docs/requirements/ibkr-integration.md`
- `docs/requirements/cpf-integration.md`
- `docs/requirements/glossary.md`
- `docs/requirements/cash-reconcile.md`

Reviewed supporting references:

- `docs/about.md`
- `docs/requirements/implementation-roadmap.md`
- `docs/develop/data-sources/inventory.md`
- `docs/develop/data-sources/non-tool-source-data.md`
- `reference/notion-bills/`

## Conflict Inventory

| id | conflict area                | evidence key | impact                             |
| -- | ---------------------------- | ------------ | ---------------------------------- |
| 01 | workflow ownership overlap   | CF-01        | resolved by owner-page publication |
| 02 | accounting ownership overlap | CF-02        | resolved by hierarchy publication  |
| 03 | bill/shared-cost split gap   | CF-03        | resolved by split publication      |

Evidence keys:

- `CF-01`: ownership split published in workflow owner pages.
- `CF-02`: accounting hierarchy and override boundaries published.
- `CF-03`: split boundaries and lifecycle-link ownership published.

## Documentation Gap Inventory

| id | gap                         | evidence key | impact                             |
| -- | --------------------------- | ------------ | ---------------------------------- |
| 01 | empty requirements index    | DG-01        | resolved                           |
| 02 | lineage linkage residual    | DG-02        | resolved                           |
| 03 | missing category mapping    | DG-03        | resolved                           |
| 04 | missing reconcile engine    | DG-04        | resolved                           |

Evidence keys:

- `DG-01`: canonical owner index is published.
- `DG-02`: owner-linkage and index alignment is published.
- `DG-03`: transaction-category-mapping page is published.
- `DG-04`: reconciliation-engine page is published.

## Data-Source and Requirement Misalignment

| id | misalignment                | evidence key | impact                            |
| -- | --------------------------- | ------------ | --------------------------------- |
| 01 | tolerance policy mismatch   | DM-01        | resolved by policy alignment      |
| 02 | account naming mismatch     | DM-02        | resolved by canonical naming rule |

Evidence keys:

- `DM-01`: cash-reconcile now aligns to reconciliation-engine tolerance policy.
- `DM-02`: canonical naming rule is published with source-to-canonical mapping.

Resolved direction to publish:

- `DM-01`: align `docs/requirements/cash-reconcile.md` to use the tolerance
	policy defined in `docs/requirements/reconciliation-engine.md`.
- `DM-02`: use account names in the financial statements gsheet `accounts`
	region as canonical names, and map source-system names to canonical names
	through the account mapping mechanism.

## Resolution Priorities

1. Maintain published ownership boundaries as source-of-truth docs evolve.
2. Use this closure baseline for requirements-to-design handoff.
3. Keep cross-page links and owner index synchronized on future updates.

## Exit Criteria for This Analysis

This analysis step is complete when:

- conflicts and gaps are explicitly documented with evidence and impact
- each issue has a clear resolution direction for subsequent requirement tasks
- unresolved items are ready to be mapped into structure and scope outline work

## Conflicts

### CF-01 Workflow ownership overlap

#### Why this is a gap

The workflow requirement boundary is not explicit. A single page,
`docs/requirements/current-workflow.md`, currently combines:

- workflow sequencing and timing
- operator review and checkpoint behavior
- report-output update and close-out behavior

Because these concerns are grouped together, requirement ownership is unclear
between workflow orchestration, interaction and approvals, and statements
lifecycle requirements.

#### Source evidence

- `docs/requirements/current-workflow.md`
	- section `Sequential steps and time estimates` defines end-to-end stage flow
	- section `Account update` includes operator review actions
	- section `Report update` includes output-review and publish actions
- `.github/prompts/requirements.prompt.md`
	- separates these as distinct requirement areas:
		- `Workflow Orchestration`
		- `Interaction and Approvals`
		- `Statements Lifecycle`
- `docs/requirements/glossary.md`
	- defines separate concepts `Checkpoint`, `Workflow step`, and `Session state`,
		supporting the need for explicit ownership boundaries

#### Concrete examples of overlap

- Example 1: `current-workflow.md` lists `human review of balances and
	transactions for errors` in `Account update`.
	- overlap: can be read as both workflow stage behavior and approval policy.
- Example 2: `current-workflow.md` lists `Reconcile review` and
	`Update and review income statement and balance sheet` in `Report update`.
	- overlap: can be read as both lifecycle behavior and review-checkpoint policy.
- Example 3: `current-workflow.md` includes a single sequential table that mixes
	account update, reconcile review, statement update, and print-out.
	- overlap: orchestration flow and output lifecycle are co-located without
		ownership markers.

#### Proposed resolutions

Resolution option A: single-source split by ownership (recommended)

1. Keep `current-workflow.md` as high-level process context only.
2. Move normative requirement statements into owner pages by concern:
	 - workflow sequencing and invariants -> workflow orchestration owner page
	 - user review and confirmation gates -> interaction and approvals owner page
	 - period close, revision, and output publish rules -> statements lifecycle
		 owner page
3. Add an ownership header in each owner page:
	 - `Primary scope`
	 - `Out of scope`
	 - `See also` links to adjacent owner pages

Resolution option B: retain one page, add strict ownership tags

1. Keep all content in `current-workflow.md`.
2. Prefix each requirement block with explicit ownership tag, for example:
	 - `[orchestration]`
	 - `[approvals]`
	 - `[lifecycle]`
3. Add a top-of-page ownership map table.

Tradeoff summary:

- Option A has lower long-term ambiguity and cleaner maintenance.
- Option B is faster short-term but increases future drift risk.

#### Recommended closure criteria for CF-01

CF-01 can be closed when:

- the status for each item in tables CF-01.1 and CF-01.2 is `mapped` or `gap`
- every workflow-related requirement statement has one and only one primary
	owner destination
- `current-workflow.md` no longer acts as a competing primary source for
	approval-policy and lifecycle requirements
- cross-links between orchestration, approvals, and lifecycle pages are present
	and consistent

#### How to use the CF-01 mapping tables

Use the mapping tables as migration instructions from source sections to owner destinations.

- **mapped** means source content is usable and should be migrated into the named destination owner section, and deprecated from the source after migration.
- **gap** means destination requirement content is still missing and must be authored in the destination owner section.

The goal is that after all mapping and deprecation steps are complete, no stale, conflicting, or duplicated content remains in `docs/requirements/*`. Source sections are transitional only.

Deprecation handling rules for CF-01:

For each source section with status `mapped`:

1. If the section contains explanatory context, examples, description of the current workflow that is not normative requirement content, or historical narrative that is not normative requirement content, copy those materials to `docs/reference/` before removing them from the source.
2. Publish and cross-link the mapped content in the destination owner document.
3. Deprecate the source section from `docs/requirements/*`.
4. If all normative content has been migrated out of a source document and the content is below the threshold to justify retaining the document, migrate any residual content to the relevant owner documents and deprecate the entire source document.

Use metadata to identify each document as `owner` or `reference` and record lineage relationships.



#### Destination outlines and section mapping

| id | status | document                  | section                                  |
| -- | ------ | ------------------------- | ---------------------------------------- |
| 01 | gap    | workflow-orchestration.md | Purpose and boundary                     |
| 02 | mapped | workflow-orchestration.md | Stage model for monthly close            |
| 03 | gap    | workflow-orchestration.md | Stage entry criteria                     |
| 04 | gap    | workflow-orchestration.md | Stage exit criteria                      |
| 05 | mapped | workflow-orchestration.md | Stage inputs                             |
| 06 | mapped | workflow-orchestration.md | Stage outputs                            |
| 07 | gap    | workflow-orchestration.md | Stage invariants                         |
| 08 | gap    | workflow-orchestration.md | Rerun behavior                           |
| 09 | gap    | workflow-orchestration.md | Resume behavior                          |
| 10 | gap    | workflow-orchestration.md | Failure handling and recovery flow       |
| 11 | gap    | workflow-orchestration.md | Inter-stage dependencies and handoff rules |
| 12 | gap    | workflow-orchestration.md | Acceptance criteria                      |
| 13 | gap    | interaction-approvals.md  | Purpose and boundary                     |
| 14 | mapped | interaction-approvals.md  | Review checkpoints by workflow stage     |
| 15 | gap    | interaction-approvals.md  | Checkpoint criteria by workflow stage    |
| 16 | gap    | interaction-approvals.md  | Required user confirmations before commit |
| 17 | gap    | interaction-approvals.md  | Approval authority                       |
| 18 | gap    | interaction-approvals.md  | Escalation and rework boundary           |
| 19 | gap    | interaction-approvals.md  | Novel-decision capture and rationale logging |
| 20 | gap    | interaction-approvals.md  | Prompt and output readability requirements |
| 21 | gap    | interaction-approvals.md  | Rejection and rework behavior            |
| 22 | gap    | interaction-approvals.md  | Acceptance criteria                      |
| 23 | gap    | statements-lifecycle.md   | Purpose and boundary                     |
| 24 | mapped | statements-lifecycle.md   | Lifecycle phase behavior                 |
| 25 | gap    | statements-lifecycle.md   | Lifecycle state model by period          |
| 26 | mapped | statements-lifecycle.md   | Draft and review behavior                |
| 27 | gap    | statements-lifecycle.md   | Finalization criteria                    |
| 28 | gap    | statements-lifecycle.md   | Reopen policy                            |
| 29 | gap    | statements-lifecycle.md   | Revision policy                          |
| 30 | mapped | statements-lifecycle.md   | Publish output actions                   |
| 31 | mapped | statements-lifecycle.md   | Artifact output requirements             |
| 32 | gap    | statements-lifecycle.md   | Versioning and lineage linkage           |
| 33 | gap    | statements-lifecycle.md   | Period snapshot and immutability rules   |
| 34 | gap    | statements-lifecycle.md   | Acceptance criteria                      |

Current-workflow source document

Source file: `docs/reference/current-workflow.md` 
#### Table CF-01.1: section-to-destination mapping

Direct section-to-destination mapping table:

| id | source section    | source sub-section            | destination section           | status     |
| -- | ----------------- | ----------------------------- | ----------------------------- | ---------- |
| 01 | Overview          | workflow summary text         | Workflow Orchestration        | mapped     |
| 02 | Sequential steps  | stage order and durations     | Workflow Orchestration        | mapped     |
| 03 | Forex             | fetch and load forex rates    | Workflow Orchestration        | mapped     |
| 04 | Account update    | execution steps               | Workflow Orchestration        | mapped     |
| 05 | Account update    | human review step             | Interaction and Approvals     | mapped     |
| 06 | Report update     | reconcile review step         | Interaction and Approvals     | mapped     |
| 07 | Report update     | update and review statements  | Statements Lifecycle          | mapped     |
| 08 | Report update     | save and upload report output | Statements Lifecycle          | mapped     |
| 09 | Pre-flight checks | section body                  | Workflow Orchestration        | gap        |
| 10 | Close-out refresh | section body                  | Workflow Orchestration        | gap        |

Mapping notes:

- `01` to `08` are direct text-level mappings from explicit source steps.
- `09` and `10` remain source gaps because headings exist without rules.

#### Table CF-01.2: destination-to-source mapping

Destination-to-source coverage and gaps table:

| id | destination requirement sub-section | source subsection evidence       | status   |
| -- | ----------------------------------- | -------------------------------- | -------- |
| 01 | WO stage model                       | sequential steps and durations   | mapped   |
| 02 | WO stage inputs and outputs          | account update execution steps   | mapped   |
| 03 | WO entry criteria                    | none                             | gap      |
| 04 | WO exit criteria                     | none                             | gap      |
| 05 | WO invariants                        | none                             | gap      |
| 06 | WO rerun behavior                    | none                             | gap      |
| 07 | WO resume behavior                   | none                             | gap      |
| 08 | IA review checkpoints                | review steps in account/report   | mapped   |
| 09 | IA checkpoint criteria               | none                             | gap      |
| 10 | IA pre-commit confirmations          | none                             | gap      |
| 11 | IA approval authority                | none                             | gap      |
| 12 | IA escalation and rework policy      | none                             | gap      |
| 13 | IA decision logging                  | none                             | gap      |
| 14 | SL lifecycle phase behavior          | report update actions            | mapped   |
| 15 | SL state model by period             | none                             | gap      |
| 16 | SL finalization criteria             | none                             | gap      |
| 17 | SL publish output rules              | save and upload report output    | mapped   |
| 18 | SL reopen policy                     | none                             | gap      |
| 19 | SL revision policy                   | none                             | gap      |
| 20 | SL snapshot immutability             | none                             | gap      |

Coverage notes:

- `mapped`: direct language exists in current-workflow source text.
- `gap`: open requirement to be defined.

Bidirectional mapping conclusion:

- Source-to-destination gaps existed where current-workflow headings were present without normative requirement content (`Pre-flight checks`, `Close-out refresh`).
- Destination-to-source gaps are larger: required orchestration criteria, approvals policy, and lifecycle governance are mostly not specified and remain open for tasks 02.02, 02.03, and 02.07.
- Migration is complete: `docs/requirements/current-workflow.md` has been deleted; non-normative operational context is preserved in `docs/reference/current-workflow.md`; mapped destination sections (Stage inputs, Stage outputs, Draft and review behavior, Artifact output requirements) are now published in the owner pages.

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

- `docs/requirements/bill-payment.md`
	- detailed current procedure, automation requirements, accounts, decisions,
		and open questions
- `docs/requirements/shared-costs.md`
	- current placeholder scope for shared-cost allocation and settlement rules
- `reference/notion-bills/bills 16ec378f707580fabf99f572568f5f60.csv`
	- bill-level fields, `Name`, `amount`, `billing_cycle`, `paid`, `payee`,
		`payment_date`
- `reference/notion-bills/billing_period 16ec378f707580d7b472d37487ec8127.csv`
	- period-level coverage fields, `bills_count` and `bills_paid`
- `reference/notion-bills/bill_payee 16ec378f707580e2ae93e4173891d72c.csv`
	- recurring payee-to-bill continuity evidence across billing periods
- `docs/develop/data-sources/non-tool-source-data.md`
	- boundary rules and extractable bill-workflow logic from Notion exports
- `docs/develop/data-sources/inventory.md`
	- canonical inventory confirming Notion bills as primary process evidence
		for requirement discovery

#### Lifecycle and reconciliation checks

lifecycle state model for bill records:

| state    | meaning                                              | next states      |
| -------- | ---------------------------------------------------- | ---------------- |
| pending  | bill identified but not yet paid                     | paid, scheduled  |
| scheduled| payment is planned for a future date within period   | paid             |
| paid     | payment confirmed with bank-statement transaction    |                  |

Active bill scope:

- a bill is either active or inactive; there is no period-scoped roster or
	historical dimension tracking
- reconciliation checks apply only to active bills in the current period
- inactive bills are excluded from count and resolution checks

bill data model:

| field          | type | req | rule                                          |
| -------------- | ---- | --- | --------------------------------------------- |
| name           | text | y   | unique bill identifier                        |
| payee          | text | y   | counterparty receiving payment                |
| amount_type    | enum | y   | fixed or variable                             |
| expected_amount| dec  | n   | required when amount_type is fixed, SGD       |
| billing_cycle  | enum | y   | monthly, quarterly, or annual                 |
| active         | bool | y   | true means included in period checks          |

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

| id | check                       | source fields                        | pass condition                                                 |
| -- | --------------------------- | ------------------------------------ | -------------------------------------------------------------- |
| 01 | amount match                | bill `amount` vs statement line item | amounts equal within SGD 0.00 tolerance                        |
| 02 | payee match                 | bill `payee` vs statement payee      | payee maps to same approved counterparty                       |
| 03 | payment date within period  | bill `payment_date` vs close period  | date falls within 2 months before or after the period end date |
| 04 | paid status complete        | bill `paid` flag                     | flag is true and linkage ref is present                        |

Period-level checks:

| id | check                       | source fields                        | pass condition                                          |
| -- | --------------------------- | ------------------------------------ | ------------------------------------------------------- |
| 01 | bills count matches         | `bills_count` vs active bill rows    | count equals number of active bills for the period      |
| 02 | bills paid count matches    | `bills_paid` vs active bill rows     | paid count equals active bills in `paid` state          |
| 03 | all bills resolved          | bill state distribution              | no active bill remains in pending state                 |

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

| id | field             | type    | req | rule                   | validation baseline            |
| -- | ----------------- | ------- | --- | ---------------------- | ------------------------------ |
| 01 | record_date       | date    | y   | posting date           | valid date and within close mo |
| 02 | description       | text    | y   | short narrative        | 1 to 200 chars                 |
| 03 | total_amount_sgd  | decimal | y   | gross shared amount    | signed decimal and scale 2     |
| 04 | user_share_pct    | decimal | n   | percent split input    | > 0 and <= 1.0                 |
| 05 | user_share_amount | decimal | n   | derived: pct x total   | abs value <= abs total         |
| 06 | category          | text    | y   | allocation class       | in allowed shared-cost set     |
| 07 | payee             | text    | y   | settlement counterparty | non-empty and mapped party     |
| 08 | status            | enum    | y   | HB record state        | created or recorded            |

Shared-cost parameter constraints:

Session completion rule for shared costs:

- if any shared-cost record remains incomplete for HomeBudget recording,
	the session is incomplete

| id | parameter                  | type    | req | rule                    | validation baseline            |
| -- | -------------------------- | ------- | --- | ----------------------- | ------------------------------ |
| 01 | split_basis                | const   | y   | percentage split only   | pct                            |
| 02 | rounding_mode              | enum    | y   | monetary rounding       | half-up to 2 dp                |
| 03 | settlement_account         | text    | y   | HB settlement account   | must equal 30 CC Hashemis      |
| 04 | settlement_currency        | enum    | y   | posting currency        | SGD only                       |
| 05 | variance_tolerance_sgd     | decimal | y   | max allowed variance    | fixed 0.00                     |

Validation baseline for consumption records:

| id | field                | type    | req | rule                    | validation baseline            |
| -- | -------------------- | ------- | --- | ----------------------- | ------------------------------ |
| 01 | period_year          | int     | y   | close period year       | 2000 to 2100                   |
| 02 | period_month         | int     | y   | close period month      | 1 to 12                        |
| 03 | utility_type         | enum    | y   | metric family           | electricity water gas          |
| 04 | usage_value          | decimal | y   | measured quantity       | signed decimal                 |
| 05 | usage_unit           | enum    | y   | measurement unit        | kwh or m3                      |
| 06 | billed_amount_sgd    | decimal | y   | billed total            | signed decimal and scale 2     |
| 07 | statement_issue_date | date    | y   | source statement date   | valid date                     |
| 08 | statement_due_date   | date    | n   | payment due date        | >= issue date when present     |
| 09 | source_account       | text    | y   | paying account          | in bills in-scope account list |
| 10 | source_statement_ref | text    | y   | lineage key             | unique within period and payee |

Consumption parameter constraints:

| id | parameter              | type    | req | rule                    | validation baseline            |
| -- | ---------------------- | ------- | --- | ----------------------- | ------------------------------ |
| 01 | missing_value_policy   | enum    | y   | null handling           | block                          |
| 02 | duplicate_row_policy   | enum    | y   | dedupe handling         | reject_same_ref_same_period    |

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

**Stage 1: HomeBudget category → GL account**

Stage 1 maps HomeBudget expense categories to an internal GL account code. The
mapping data lives in the `cat_map` region of the helper workbook configured at
`gsheet/homebudget-workbook.json`. It covers expense categories only and
contains 181 rows across 10 columns. There is no equivalent Stage 1 mapping for
income transactions; income categories are assigned during the monthly closing
workflow rather than maintained as HomeBudget master data.

**Stage 2: GL account → financial statements category**

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
	(`reconcile_exp_cost_centers` → `reconcile_fin_stm_summary`) aggregate the
	mapped rows before publication to `income_statement`.

- Balance sheet path: the `accounts` region (29 rows, 7 columns: `id`, `type`,
  `owner`, `name`, `currency`, `HB account`, `stm account`) assigns each account
  to its balance sheet bucket and class. Period-ending balances come from the
  `balances` region. Currency conversion uses `forex_rates`. Rollup regions
  (`reconcile_bal_by_acct` → `reconcile_bal_summary`) aggregate per-class before
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
	 - operator-review checkpoint placement in monthly close workflow

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




