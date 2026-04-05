# Requirements

## Table of contents

- [Release and objective](#release-and-objective)
- [POC scope boundaries](#poc-scope-boundaries)
- [Reference documents](#reference-documents)
- [Cross requirement constraints](#cross-requirement-constraints)
- [Requirement areas](#requirement-areas)
	- [02.01 Structure and scope boundary](#0201-structure-and-scope-boundary)
	- [02.02 Workflow orchestration](#0202-workflow-orchestration)
	- [02.03 Interaction and approvals](#0203-interaction-and-approvals)
	- [02.04 Source systems and lineage](#0204-source-systems-and-lineage)
	- [02.05 Accounting model and mapping](#0205-accounting-model-and-mapping)
	- [02.06 Reconciliation engine](#0206-reconciliation-engine)
	- [02.07 Statements lifecycle](#0207-statements-lifecycle)
	- [02.08 HomeBudget integration](#0208-homebudget-integration)
	- [02.09 IBKR integration](#0209-ibkr-integration)
	- [02.12 CPF integration](#0212-cpf-integration)
	- [02.13 Bill payment and shared costs](#0213-bill-payment-and-shared-costs)

## Release and objective

These requirements define release `0.1.0` proof of concept behavior.

Primary objectives:

- Deliver a faster local monthly close workflow than the current manual sheet-first workflow.
- Prove end to end feasibility across local SQLite, Google Sheets, and HomeBudget with one operator.
- Keep setup and operation simple while preserving the path to MVP hardening.

## POC scope boundaries

In scope:

- Local only execution on Windows with CLI driven workflows.
- Session based updates with explicit user checkpoints.
- Local SQLite as the working persistence layer.
- Continued use of Google Sheets and JSON configuration as integration assets.
- App supported HomeBudget session transaction create, update, and delete workflows.
- JSON driven category and account mapping.
- Bank transaction relationship logic.
- Financial statements worksheet flow limited to minimal monthly close outputs.

Out of scope:

- MVP and later capabilities, including browser first operation and cloud runtime.
- IBKR API import, POC remains CSV driven.
- Forecasting and cash input workflow changes, these remain in existing Google Sheets and form flows.
- Automated replacement of all manual review checkpoints.
- HomeBudget recurring transaction ownership, this remains user managed.
- Expense to transfer relation logic.

## Reference documents

- [docs/about.md](about.md)
- [docs/requirements/implementation-roadmap.md](requirements/implementation-roadmap.md)
- [docs/requirements/poc.md](requirements/poc.md)
- [docs/requirements/current-workflow.md](requirements/current-workflow.md)
- [docs/requirements/accounting-logic.md](requirements/accounting-logic.md)
- [docs/requirements/account-classification.md](requirements/account-classification.md)
- [docs/requirements/cash-reconcile.md](requirements/cash-reconcile.md)
- [docs/requirements/bill-payment.md](requirements/bill-payment.md)
- [docs/requirements/homebudget.md](requirements/homebudget.md)
- [docs/requirements/google-sheets.md](requirements/google-sheets.md)
- [docs/requirements/glossary.md](requirements/glossary.md)

## Cross requirement constraints

- Platform: Windows local development environment, Python 3.12 series, and local virtual environment in `env/`.
- Operator model: one operator with explicit review checkpoints.
- Auditability: each period close must retain source lineage, decision trail, and final output snapshot.
- Reliability: rerun and resume behavior must be deterministic for identical input sets.
- Security model for POC: local files and local database usage, no cloud runtime dependencies required.

## Requirement areas

Detailed requirement sources:

| id | subtopic                         | primary detail doc                                           |
| -- | -------------------------------- | ------------------------------------------------------------ |
| 01 | 02.01 structure and scope boundary | [poc.md](requirements/poc.md)                               |
| 02 | 02.02 workflow orchestration     | [current-workflow.md](requirements/current-workflow.md)     |
| 03 | 02.03 interaction and approvals  | [current-workflow.md](requirements/current-workflow.md)     |
| 04 | 02.04 source systems and lineage | [google-sheets.md](requirements/google-sheets.md)           |
| 05 | 02.05 accounting model and mapping | [accounting-logic.md](requirements/accounting-logic.md)     |
| 06 | 02.06 reconciliation engine      | [cash-reconcile.md](requirements/cash-reconcile.md)         |
| 07 | 02.07 statements lifecycle       | [current-workflow.md](requirements/current-workflow.md)     |
| 08 | 02.08 homebudget integration     | [homebudget.md](requirements/homebudget.md)                 |
| 09 | 02.09 ibkr integration           | [accounting-logic.md](requirements/accounting-logic.md)     |
| 10 | 02.12 cpf integration            | [accounting-logic.md](requirements/accounting-logic.md)     |
| 11 | 02.13 bill payment and shared costs | [bill-payment.md](requirements/bill-payment.md)             |

Supporting sources for each subtopic are listed in the `Detailed sources` line within each section.

### 02.01 Structure and scope boundary

Detailed sources: [poc.md](requirements/poc.md), [implementation-roadmap.md](requirements/implementation-roadmap.md), [glossary.md](requirements/glossary.md)

User outcome: The user can complete monthly close with a clear POC boundary and no accidental scope expansion.

Requirements:

- The requirement architecture shall remain aligned to the defined milestone structure for this release.
- The product shall enforce release `0.1.0` boundaries defined in [docs/requirements/implementation-roadmap.md](requirements/implementation-roadmap.md).
- The product shall provide only local single operator workflows for this release.
- The requirements set shall explicitly list in scope and out of scope capabilities.
- Any requested capability mapped to MVP or later roadmap phases shall be treated as deferred until explicit scope approval.

Acceptance criteria:

- Scope statements are present, testable, and aligned with roadmap POC intent.
- Requirement areas are non-overlapping and collectively cover POC behavior.
- Out of scope statements include cloud runtime, IBKR API import, and expense to transfer relation logic.

### 02.02 Workflow orchestration

Detailed sources: [current-workflow.md](requirements/current-workflow.md), [poc.md](requirements/poc.md)

User outcome: The user can run the monthly close flow in a predictable sequence and resume safely after interruption.

Requirements:

- The system shall support workflow stages for pre-flight, forex update, account update, reconcile, statement update, and close out.
- Each workflow stage shall define required inputs, outputs, and validation checkpoints.
- The workflow shall support rerun from a selected stage without corrupting previously validated outputs.
- The workflow shall support resume from persisted session state after interruption.
- The workflow shall log step results with timestamp, period, and status.

Acceptance criteria:

- A complete stage sequence exists with clear prerequisites and outputs.
- A failed or interrupted run can resume from the last successful stage.
- Each stage produces a reviewable status record.

### 02.03 Interaction and approvals

Detailed sources: [current-workflow.md](requirements/current-workflow.md), [glossary.md](requirements/glossary.md)

User outcome: The user can operate the system from CLI prompts with clear visibility and explicit approval before write actions.

Requirements:

- The system shall provide CLI commands and guided prompts for each workflow stage.
- The CLI shall present concise summaries for source inputs, computed outputs, and validation results.
- The CLI shall require explicit user confirmation before write operations to HomeBudget or persistent app stores.
- The CLI shall provide error messages with actionable next steps.
- Output formatting shall remain readable in Windows terminal defaults.

Acceptance criteria:

- All write paths include a confirmation checkpoint.
- Review summaries are shown before confirm actions.
- Users can identify failed checks and rerun the relevant stage.

### 02.04 Source systems and lineage

Detailed sources: [google-sheets.md](requirements/google-sheets.md), [homebudget.md](requirements/homebudget.md), [dependencies.md](requirements/dependencies.md)

User outcome: The user can trust source coverage and lineage for each monthly close result.

Requirements:

- The system shall ingest required sources from HomeBudget, statement digital twin sources, helper Google Sheets, and JSON config files.
- The system shall define source precedence for conflicting values.
- The system shall capture lineage metadata for each derived value, including source system and extraction timestamp.
- The system shall validate required fields before calculations proceed.
- The system shall fail fast on missing required source data and provide remediation guidance.

Source precedence baseline for POC:

- Statement digital twin balances and transactions are the source of truth for statement-backed account reconcile.
- HomeBudget ledger is the source of truth for recorded personal ledger state before adjustments.
- User inputs are source of truth for manual observed values, such as physical cash count.

Acceptance criteria:

- Required source fields are documented and validated.
- Lineage is available for each statement and reconcile output.
- Precedence rules resolve conflicts deterministically.

### 02.05 Accounting model and mapping

Detailed sources: [accounting-logic.md](requirements/accounting-logic.md), [account-classification.md](requirements/account-classification.md), [glossary.md](requirements/glossary.md)

User outcome: The user can rely on deterministic accounting behavior that matches documented personal finance intent.

Requirements:

- The system shall apply account and category mapping from app owned JSON configuration.
- The system shall enforce cost center logic where personal expenses flow through `TWH - Personal` with month end zero balance intent.
- The system shall support investment booking rules for capital gains, interest, dividends, and mark to market adjustments.
- The system shall enforce transaction uniqueness using account, transaction date, amount, and description, with deterministic suffix rules for true duplicates.
- The system shall apply period boundaries by calendar month using `YYYY-MM` identifiers.
- The system shall maintain currency precision by account currency and preserve deterministic conversion inputs.

Acceptance criteria:

- Identical source inputs produce identical classified outputs.
- Duplicate detection rules prevent accidental double posting.
- Account classification behavior aligns with [docs/requirements/account-classification.md](requirements/account-classification.md).

### 02.06 Reconciliation engine

Detailed sources: [cash-reconcile.md](requirements/cash-reconcile.md), [accounting-logic.md](requirements/accounting-logic.md), [current-workflow.md](requirements/current-workflow.md)

User outcome: The user can close reconciliation with transparent variance handling and clear closure criteria.

Requirements:

- The system shall support account level and transaction level reconciliation methods by account type.
- The system shall expose variance amounts and variance drivers before closure.
- The system shall enforce tolerance policy at account precision for statement and HomeBudget reconcile.
- The system shall support cash variance alert threshold at plus or minus SGD 20 for adjustment review.
- The system shall require explicit user approval before posting reconciliation adjustments.
- The system shall record reconciliation date and treatment for pending transactions around cutoff.

Acceptance criteria:

- Reconcile output includes matched, unmatched, and adjusted totals.
- Variance and tolerance status are visible before close approval.
- Period close cannot complete with unresolved blocking variance.

### 02.07 Statements lifecycle

Detailed sources: [current-workflow.md](requirements/current-workflow.md), [implementation-roadmap.md](requirements/implementation-roadmap.md)

User outcome: The user can produce monthly close statements with clear revision and finalization behavior.

Requirements:

- The system shall produce income statement and balance sheet outputs per monthly period.
- The statement update flow shall include a reconcile review checkpoint before statement finalization.
- The system shall support draft and finalized states for period outputs.
- The system shall preserve prior period snapshots after finalization.
- The system shall support PDF export of finalized outputs for archival workflow compatibility.

Acceptance criteria:

- Income statement and balance sheet are available for the period with reproducible values.
- Finalized output is immutable without explicit revision workflow.
- Reconcile status is visible in statement finalization summary.

### 02.08 HomeBudget integration

Detailed sources: [homebudget.md](requirements/homebudget.md), [dependencies.md](requirements/dependencies.md)

User outcome: The user can update HomeBudget safely with controlled writes and duplicate prevention.

Requirements:

- The system shall support read access for accounts, categories, and ledger transactions required for monthly close.
- The system shall support controlled create, update, and delete of session transactions used for close workflows.
- The system shall enforce idempotency guards on repeated run attempts.
- The system shall prevent duplicate transaction writes using uniqueness checks before commit.
- The system shall provide failure handling guidance for configuration, connectivity, and write errors.
- The system shall preserve compatibility with user managed HomeBudget recurring flows.

Acceptance criteria:

- Repeated execution of the same approved write set does not produce duplicate transactions.
- Failed integration steps return actionable error context.
- User confirmation occurs before each commit operation.

### 02.09 IBKR integration

Detailed sources: [accounting-logic.md](requirements/accounting-logic.md), [implementation-roadmap.md](requirements/implementation-roadmap.md)

User outcome: The user can include IBKR balances and activity in monthly close using the current CSV workflow with lineage visibility.

Requirements:

- The system shall ingest IBKR data from user downloaded CSV files for POC.
- The system shall compute and reconcile IBKR cash and position balances for period close.
- The system shall classify IBKR activity into transfers, dividends, interest, profit and loss, and mark to market components.
- The system shall maintain lineage for IBKR derived values back to source file and row context.
- The system shall support separate handling paths for IBA and IRA account behavior.
- The system shall not require IBKR API integration in POC scope.

Acceptance criteria:

- IBKR cash and position close values tie to source statements after approved adjustments.
- Classification outputs align with documented investment rules.
- Lineage data identifies each IBKR source artifact used in close outputs.

### 02.12 CPF integration

Detailed sources: [accounting-logic.md](requirements/accounting-logic.md), [current-workflow.md](requirements/current-workflow.md)

User outcome: The user can include CPF balances and activity in monthly close with clear lineage and reconcile behavior.

Requirements:

- The system shall ingest required CPF balances and contribution-related inputs for the period.
- The system shall support CPF-specific classification and reconciliation behavior aligned to account rules.
- The system shall preserve lineage for CPF-derived values back to source input and period.
- The system shall support adjustment and exception notes when CPF observed balances differ from expected values.

Acceptance criteria:

- CPF values used in statements are traceable to source inputs.
- CPF reconcile outcomes are visible in period-close review outputs.
- CPF-specific adjustments require explicit user approval before commit.

### 02.13 Bill payment and shared costs

Detailed sources: [bill-payment.md](requirements/bill-payment.md), [bill-payment-shared-costs.md](requirements/bill-payment-shared-costs.md)

User outcome: The user can process bill payments and shared-cost settlements with auditable, repeatable behavior in POC.

Requirements:

- The system shall support bill-payment capture from in-scope billing sources for monthly close.
- The system shall support shared-cost allocation and settlement requirements, including settlement account treatment.
- The system shall apply deduplication and idempotency controls for generated bill and settlement transactions.
- The system shall provide lineage and audit visibility for bill and shared-cost outputs included in close.

Acceptance criteria:

- Bill and shared-cost transactions included in period close are reproducible from source inputs.
- Settlement outputs and statuses are reviewable before commit.
- Re-run of the same approved input set does not create duplicate bill or settlement entries.


