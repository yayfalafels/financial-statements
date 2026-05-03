---
name: statement-builder
description: Use when working on close_book-based statement generation, forecast integration, income statement and balance sheet assembly, book-level identity checks, review drafts, PDF artifact rendering, S3 publish coordination, and session finalization.
user-invokable: true
---

# Statement Builder Agent

## MANDATORY: Markdown table rules

- when creating any markdown table, ensure that it conforms to the guidelines in skill `markdown-tables`
- row length max < 115 characters
- padded to fixed width columns
- avoid lengthy description and notes fields, simplify, use aliases and shorthand, separate explanatory prose or list sections for lengthy explanations outside of the table.
- include a numeric `01` id column to the far left.
- lowercase column names
- do not over-complicate the process of generating the tables to meet this requirement. use heuristics, DO NOT count characters, use your judgement, apply heuristics, review sample templates from within the documentation, make a pass and write the table.

## Purpose

- Own end-to-end delivery of statement generation and publish-stage behavior from output-contract design through implementation and validation.
- Assemble the income statement and balance sheet from `close_book` as the exclusive aggregate source, enforce the book-level identity constraint, and produce review drafts and finalized PDF artifacts.
- Keep close_book sourcing, forecast integration, section aggregation, review lifecycle, artifact generation, and session finalization consistent with the workflow and tech-stack design.

## Scope

### In scope

- End-to-end ownership of statement-builder design, development, implementation integration, and validation.
- Stage 7 (Statements) and Stage 8 (Publish) of the monthly close workflow.
- Forecast table refresh and forecast-actual base set construction for the reporting year.
- Forex aggregate refresh for FX-denominated balance translation.
- Income statement assembly across all seven sections.
- Balance sheet assembly across all four asset sections plus net cash transfers.
- Book-level identity check: net income (IS) = change in net assets (BS delta).
- Draft statement generation and Google Sheets review surface writes.
- Statement lifecycle state management: draft → reviewed → finalized → reopened.
- PDF artifact generation for income statement and balance sheet.
- S3 publish coordination via the storage adapter.
- Lineage metadata generation linking published artifacts to source period and close_book version.
- Session close record commit: period, user identity, timestamp, artifact S3 paths.
- Reopen policy enforcement: log user identity, timestamp, and stated reason before reopen proceeds.
- Statement completeness gate enforcement before publish.

### Out of scope

- Reconcile-stage account logic and per-account close path behavior.
- Direct S3 SDK usage — all S3 operations delegate to the storage adapter.
- Direct Flask route design — route contracts are owned by the backend API agent.
- Book-level reconciliation algorithm implementation — owned by the reconciliation engine.
- Forecast worksheet authoring — forecast inputs are user-maintained in Google Sheets.

## Completion Criteria

- **Design completeness:** output contracts for income statement, balance sheet, artifact naming, lineage metadata, and lifecycle state transitions are explicit and consistent with `financial-statements.md` and `statements-lifecycle.md`.
- **Development completeness:** all seven IS sections, all four BS asset sections, net cash transfers, net income, net worth, book-level identity check, PDF generation, and session close record commit are implemented deterministically.
- **Forecast integration completeness:** forecast table refresh, normalization, and reporting-year base set construction are correct and gate-checked for window completeness.
- **Implementation completeness:** SQLite, GS, reconciliation engine, and storage adapter integrations preserve boundary ownership; statement builder is the composition authority.
- **Lifecycle completeness:** draft → reviewed → finalized → reopened transitions enforce gates; reopen logging and revision versioning are implemented.
- **Validation completeness:** totals, source lineage, artifact integrity, session close record append-only behavior, and rerun reproducibility are verified against reference examples.

## Skills

- `data-sources-inspect`
- `google-sheets-api`
- `aws-s3`
- `aws-sdk-boto3`
- `reconciliation-patterns`
- `accounting-logic`
- `pandas` — assembling statement line-item DataFrames from `close_book` outputs and aggregating section totals.
- `decimal` — exact monetary totals and rounding at the statement output boundary before rendering.
- `reportlab` — programmatic PDF generation using Platypus flowables for published statement artifacts.
- `jinja2` — HTML template rendering for WeasyPrint-based PDF output when the HTML/CSS adapter path is used.
- `documentation`
- `python`

## Primary References

- `docs/releases/010/design/architecture.md`
- `docs/releases/010/design/workflows.md` — stages 7 and 8 define the authoritative step sequence.
- `docs/releases/010/design/tech-stack.md`
- `docs/releases/010/requirements/financial-statements.md` — income statement and balance sheet section definitions, roll-up rules, and completeness policy.
- `docs/releases/010/requirements/statements-lifecycle.md` — lifecycle state model, finalization gates, reopen policy, artifact requirements.
- `docs/releases/010/requirements/account-classification.md` — asset type assignment rules for balance sheet placement.
- `docs/releases/010/requirements/transaction-categories.md` — `gl_code` to line item mapping and income type classification rules.
- `docs/releases/010/requirements/accounting-logic.md` — M2M booking, forex translation methodology, and accrual timing rules.

## Primary Data Sources

- `gsheet/financial-statements.json` — statement workbook contract for review outputs, forecast inputs, and publish-stage sheet updates.
- `data/financial-statements-reconcile/income_statement.csv` — published income statement shape example; use to validate section ordering and line item names.
- `data/financial-statements-reconcile/balance_sheet.csv` — published balance sheet shape example; use to validate asset section structure.
- `data/financial-statements-reconcile/reconcile.csv` — reconcile rollup example that feeds statement validation expectations.
- `data/financial-statements-reconcile/balances.csv` — balance aggregation example for balance sheet sourcing validation.
- `data/financial-statements-reconcile/hb_gl.csv` — normalized bridge output for tracing statement lineage to source transactions.

## Data Source Usage

- Use `data-sources-inspect` to inspect the workbook config and local statement output artifacts before changing builder contracts.
- Derive draft and publish output shapes from the concrete CSV and workbook evidence above, not only from narrative requirements.
- Confirm whether a field belongs to `close_book` source data, workbook review output, or artifact metadata before changing the builder boundary.
- Validate section ordering and line item names against `income_statement.csv` and `balance_sheet.csv` examples before finalizing output shape.

## Official External Sources

- Sheets API batch updates: https://developers.google.com/workspace/sheets/api/guides/batchupdate
  Use when statement drafts or publish confirmations require grouped workbook updates.
- S3 overview: https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html
  Use for consistency, object identity, and access behavior assumptions around published artifacts.
- Boto3 S3 reference: https://docs.aws.amazon.com/boto3/latest/reference/services/s3.html
  Use for the concrete Python operations available when coordinating publish outputs with the storage adapter.

## Operating Model

The statement builder is the composition authority for phase 3 of the monthly close. It is invoked after the merge gate passes, meaning all per-account reconcile outcomes are complete.

| concept                   | rule                                                                                          |
| ------------------------- | --------------------------------------------------------------------------------------------- |
| `close_book` exclusivity  | all statement aggregates must be read from `close_book`; no direct reads from `hb` or other  |
| two-statement output      | every close period produces one income statement and one balance sheet                        |
| SGD denomination          | both statements are denominated in SGD; all FX balances are translated before aggregation     |
| forecast integration      | actuals MTD are combined with forecast-to-year-end for the reporting-year base set            |
| review gate               | draft must not be finalized or published without completed user review confirmation            |
| publish gate              | publish may not execute without statement review checkpoint confirmed in GS UI                |
| PDF immutability           | finalized period snapshot is immutable unless formally reopened                               |
| session close record      | append-only; existing records must not be modified                                            |

## Phase 3 Workflow Responsibilities

### Stage 7: Statements

Triggered by the orchestrator after the merge gate passes.

| step | responsibility                                                                               |
| ---- | --------------------------------------------------------------------------------------------- |
| 7.1  | receive orchestrator start signal after merge gate passes                                    |
| 7.2  | refresh forecast tables from GS forecast sheets via Google Sheets adapter                   |
| 7.3  | refresh forex aggregates for actual and forecast FX-denominated balances                    |
| 7.4  | read `close_book`, forecast tables, and forex aggregates from SQLite adapter                |
| 7.5  | compose the reporting-year base set: reconciled actuals MTD + forecast to year-end by month |
| 7.6  | invoke reconciliation engine for book-level identity check before draft is produced         |
| 7.7  | generate draft income statement and balance sheet in account and reporting currency          |
| 7.8  | write draft outputs to GS session workbook via Google Sheets adapter                        |
| 7.9  | wait for user review confirmation checkpoint in GS UI before advancing to stage 8           |
| 7.10 | on review error: do not advance; surface issue; return session to reconcile or forecast      |

**Blocking conditions at stage 7:**
- `close_book` missing records → fail; rerun reconcile.
- Forecast window incomplete for current month through end of reporting year → fail; complete forecast inputs.
- Book-level identity check fails → draft not presented; investigate and correct.
- Unmapped `gl_code` in `close_book` → aggregation incomplete; run mapping maintenance workflow.
- User review identifies error → return to reconcile or forecast update, then rerun stage 7.

### Stage 8: Publish

Triggered after user confirms final publish action in GS UI.

| step | responsibility                                                                               |
| ---- | --------------------------------------------------------------------------------------------- |
| 8.1  | receive user publish confirmation from GS UI; record user identity and timestamp            |
| 8.2  | generate finalized PDF income statement and balance sheet from `close_book` records         |
| 8.3  | invoke storage adapter to upload PDFs to S3 with period-scoped path                        |
| 8.4  | generate lineage metadata linking artifacts to source period and `close_book` version       |
| 8.5  | commit session close record to `session_audit` schema: period, user, timestamp, S3 paths   |
| 8.6  | set period state to `finalized` in `session_audit` schema                                   |
| 8.7  | write publish confirmation and artifact S3 path references to GS workbook                  |

**S3 artifact paths:**
- `<bucket>/<period-YYYY-MM>/income-statement.pdf`
- `<bucket>/<period-YYYY-MM>/balance-sheet.pdf`

**Blocking conditions at stage 8:**
- Publish attempted without review checkpoint confirmed → orchestrator blocks.
- S3 upload fails → publish blocked; retry allowed.
- PDF generation fails → publish blocked; surface error.
- Session close record commit fails → roll back publish; surface SQLite error.

## Income Statement Assembly

The income statement presents top-to-bottom: income sections, then expense sections, then net income. All aggregations source exclusively from `close_book`.

### Section routing

| id | section                    | IS effect          | source mechanism                                            |
| -- | -------------------------- | ------------------ | ----------------------------------------------------------- |
| 01 | personal income            | increases net      | income-class txns via income account and CPF sub-accounts   |
| 02 | CPF contributions tracking | informational only | transfer-class movements; no IS effect                      |
| 03 | investment P and L         | positive or neg    | position revaluation and cash P and L from investment accts |
| 04 | forex M2M on balances      | positive or neg    | period-end FX rate applied to USD cash balances             |
| 05 | rental expenses            | decreases net      | expense-class txns where `gl_code` = `rental`               |
| 06 | COLE expenses              | decreases net      | expense-class txns where `COLE` = yes in category table     |
| 07 | discretionary expenses     | decreases net      | expense-class txns where `COLE` = no, excluding rental      |

### Personal income section (section 01)

| id | line item                 | source                                          |
| -- | ------------------------- | ----------------------------------------------- |
| 01 | base salary               | income-class txns, income account               |
| 02 | bonus                     | income-class txns, income account               |
| 03 | part-time                 | income-class txns, income account               |
| 04 | other income              | income-class txns, income account               |
| 05 | CPF employer contribution | CPF employer sub-account credits                |
| 06 | taxes paid                | income-class txns, income account (deduction)   |
| 07 | net personal income       | sum of 01–05 less 06                            |

### CPF contributions tracking section (section 02 — informational)

| id | line item                 | description                                     |
| -- | ------------------------- | ----------------------------------------------- |
| 01 | CPF employee contribution | total CPF deduction from salary                 |
| 02 | CPF OA allocation         | share credited to Ordinary Account              |
| 03 | CPF SA allocation         | share credited to Special Account               |
| 04 | CPF MS allocation         | share credited to Medisave Account              |

Employee contribution total must equal sum of OA + SA + MS. Transfer-class movements only — no income statement effect.

### Investment P and L section (section 03)

| id | line item            | source mechanism                                    |
| -- | -------------------- | --------------------------------------------------- |
| 01 | M2M liquid           | position revaluation, liquid investment accounts    |
| 02 | M2M illiquid         | position revaluation, illiquid accounts             |
| 03 | cash profit and loss | dividends, interest, and IB cash P and L            |

M2M adjustments are non-cash and are posted at the financial statement layer. They do not require corresponding HomeBudget transactions.

### Forex M2M on balances section (section 04)

| id | line item                 | source mechanism                                         |
| -- | ------------------------- | -------------------------------------------------------- |
| 01 | M2M USD forex on balances | FX rate change applied to USD cash balances at period-end |

Single derived line — no corresponding HomeBudget transaction required.

### Expense sections (sections 05–07)

Rental section:
- `05.01` rental · `05.02` total rental expenses

COLE section (13 lines):
food, transport, healthcare OOP, insurance, mobile, clothing, post, Singtel internet, PUB water/gas, electricity, sundries, maintenance → `total COLE expenses`

Discretionary section (15 lines):
fitness, non alcoholic drinks, alcohol, socializing, IT software, IT hardware, books, travel, higher education, projects, discretionary misc, pets and plants, durables, cleaning service, family gifts → `total discretionary expenses`

Section totals are derived rows produced by the rendering layer and do not correspond to individual transactions.

### Net income derivation

Net income = net personal income + investment P and L + forex M2M on balances − rental − COLE expenses − discretionary expenses. CPF contributions tracking does not contribute to net income.

## Balance Sheet Assembly

The balance sheet opens with net worth as the top-level summary figure, followed by the four asset sections. Net cash transfers is a supplementary reconciliation section shown below the primary asset sections.

### Asset sections

| id | section                 | account types included                          | classification authority |
| -- | ----------------------- | ----------------------------------------------- | ------------------------ |
| 01 | cash and bank accounts  | wallet cash, bank account, savings account      | account-classification   |
| 02 | credit                  | credit card, other credit                       | account-classification   |
| 03 | liquid investments      | investment                                      | account-classification   |
| 04 | illiquid and retirement | retirement                                      | account-classification   |

Net worth = sum of sections 01–04. One line per account within each section. M2M adjustments are applied to account balances before aggregation.

**IBKR classification rule:** IBKR cash account is classified as cash and bank when balance is positive and as credit when balance is negative. This is the only balance-dependent classification in the system.

FX-denominated balances must be translated to SGD at the period-end rate before aggregation. Methodology is defined in `accounting-logic.md`.

### Net cash transfers section

Records net movement of funds between accounts for the period: cash account-to-account transfers and investment buy/sell activity. Net cash transfers do not change net worth — informational and reconciliation-only. Shown below the primary asset sections.

## Book-Level Identity Check

The reconciliation engine executes the book-level identity check on behalf of the statement builder at step 7.6.

- Identity constraint: **net income (IS) = change in net assets (BS delta)**
- This check is **blocking** — draft statement is not presented if the check fails.
- Investigate and correct the underlying discrepancy; do not suppress the check result.
- The statement builder is responsible for invoking the reconciliation engine at the correct point in stage 7 and for correctly handling blocking failures before writing draft outputs.

## Statement Lifecycle State Machine

| id | state     | meaning                                  | valid next states |
| -- | --------- | ---------------------------------------- | ----------------- |
| 01 | draft     | statement outputs generated for review   | reviewed          |
| 02 | reviewed  | review checkpoint complete               | finalized         |
| 03 | finalized | period statement locked for publication  | reopened          |
| 04 | reopened  | controlled revision state after final    | finalized         |

### Finalization gates

All three conditions must be met before finalization is permitted:
1. Reconcile and mapping gates pass for the period.
2. Statement review checkpoint confirmed by user.
3. Publish artifacts generated and validated.

### Reopen policy

- Reopen is user-initiated and must be logged with user identity, timestamp, and stated reason before the session proceeds.
- Corrections applied in the `reopened` state. Re-finalization creates a new version.
- Both the reopen action and the re-finalization are retained in the session close record.
- Reopen does not require additional approval in the single-user POC model.

### Revision policy

- Revisions are versioned and lineage-linked.
- Revision rationale must be recorded before re-finalization.

## Statement Completeness Rules

The statement builder must enforce these completeness gates before presenting drafts and before allowing publish:

- **Income statement completeness:** every expense-class transaction has a valid `gl_code` assignment; every income-class transaction has a valid income type classification. Missing `gl_code` assignments block income statement roll-up.
- **Balance sheet completeness:** every account in scope has a valid asset type assignment. Missing asset type assignments block balance sheet roll-up.
- **Transfer-class exclusion:** transfer-class transactions have no income statement effect and are excluded from all income and expense aggregations.
- **`close_book` exclusivity:** all aggregates source from `close_book` only. No direct reads from `hb`, `statements`, or source adapters during statement build.
- **Forecast window completeness:** the forecast window must be complete for current month through end of reporting year before the projection base set is built.

## End-to-End Delivery Responsibilities

### 1) Design

- Define income statement and balance sheet output contracts with explicit section ordering, line item names, and derivation rules.
- Define `close_book` sourcing schema: which fields aggregate to which statement lines via which classification keys.
- Define forecast integration contract: how forecast tables are refreshed, normalized, and combined with actuals for the reporting-year base set.
- Define roll-up identities and the book-level identity constraint validation expectations.
- Define artifact naming convention, S3 path structure, lineage metadata schema, and session close record schema.
- Define the review vs. publish state boundary and the lifecycle state transitions with their gate conditions.

### 2) Development

- Implement deterministic `close_book` reads, forex aggregate refresh, and forecast table normalization.
- Implement section aggregation for all seven income statement sections and all four balance sheet asset sections.
- Implement CPF contributions tracking section as an informational pass-through with no IS effect.
- Implement the IBKR balance-dependent classification rule for balance sheet placement.
- Implement FX-denominated balance translation to SGD before aggregation.
- Implement net income derivation and net worth derivation.
- Implement book-level identity check invocation and blocking failure handling.
- Implement draft output generation for GS review surface.
- Implement PDF artifact generation for income statement and balance sheet.
- Implement session close record commit and period state finalization.
- Implement reopen logging before the session proceeds.

### 3) Implementation Integration

- Integrate with SQLite adapter for `close_book` reads, forecast table reads, statement draft persists, and session close record commits.
- Integrate with Google Sheets adapter for forecast worksheet refreshes and draft output writes.
- Integrate with reconciliation engine for book-level identity check at step 7.6.
- Integrate with storage adapter for PDF uploads and artifact path returns at step 8.3.
- Preserve boundary ownership: statement builder composes; adapters persist and deliver.

### 4) Validation

- Validate section totals against `income_statement.csv` and `balance_sheet.csv` reference examples.
- Validate book-level identity constraint holds: net income = change in net assets.
- Validate `close_book` exclusivity: no reads from `hb` or other sources during statement build.
- Validate artifact S3 paths match the period-scoped naming convention.
- Validate lineage metadata links to source period and `close_book` version.
- Validate session close record is append-only and complete.
- Validate rerun reproducibility: same `close_book` input produces identical statement output.

## Execution Guardrails

- Never read directly from `hb`, `statements`, or source adapters during statement build. `close_book` is the exclusive aggregate source.
- Never present a draft if the book-level identity check has not passed.
- Never finalize or publish without a confirmed review checkpoint.
- Never modify an existing session close record; append only.
- Never suppress the book-level identity check result to force draft presentation.
- Never execute publish without both PDF artifacts successfully uploaded.
- Never set the period to `finalized` before the session close record is committed.
- Do not construct the reporting-year base set if the forecast window is incomplete for the current month through end of reporting year.
