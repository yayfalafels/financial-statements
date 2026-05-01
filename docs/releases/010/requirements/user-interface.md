---
title: User Interface
doc_type: requirements
topic_type: owner
owner: user-interface
scope: poc
---
# User Interface

## Table of contents

- [Purpose and boundary](#purpose-and-boundary)
- [Reference documents](#reference-documents)
- [Primary scope](#primary-scope)
- [Out of scope](#out-of-scope)
- [Google Sheets as primary session UI](#google-sheets-as-primary-session-ui)
- [Consolidated workbook assumption](#consolidated-workbook-assumption)
- [Workflow touchpoint map](#workflow-touchpoint-map)
- [Consolidated workbook page inventory](#consolidated-workbook-page-inventory)
- [Reusable page patterns](#reusable-page-patterns)
- [Financial statements review surface](#financial-statements-review-surface)
- [Data entry surfaces](#data-entry-surfaces)
- [Mapping management surface](#mapping-management-surface)
- [Session log surface](#session-log-surface)
- [CLI as parallel surface](#cli-as-parallel-surface)
- [Non-functional requirements](#non-functional-requirements)

## Purpose and boundary

This document defines user interface requirements for the POC monthly close workflow.

## Reference documents

- [workflow orchestration](workflow-orchestration.md)
- [interaction and approvals](interaction-approvals.md)
- [transaction categories](transaction-categories.md)
- [source systems and lineage](source-systems-lineage.md)
- [shared costs](shared-costs.md)
- [cpf integration](cpf-integration.md)
- [ibkr integration](ibkr-integration.md)

## Primary scope

- Google Sheets workbook surfaces used during the monthly close session
- CLI surface scope and required user behaviors
- Category data model CRUD interface requirements
- Session log surface requirements
- Non-functional interface requirements

## Out of scope

- Low-level UI layout and control implementation â€” owned by design
- Browser UI â€” deferred to a later phase
- Mobile interfaces
- Multi-user session management
- Workflow stage sequencing and checkpoint pass criteria â€” owned by workflow orchestration and interaction and approvals

## Google Sheets as primary session UI

Google Sheets is the primary session UI for the POC monthly close workflow. The user uses Google Sheets workbooks to enter period data, review reconciliation outputs, manage category mappings, and confirm close readiness at each checkpoint.

The financial statements workbook is the primary review surface for the reconcile and publish stages. It presents reconciliation checks, income statement outputs, and balance sheet outputs for user review before each commit action.

The CLI is a parallel interface for scripting and automation. It does not replace Google Sheets as the primary session surface.

## Consolidated workbook assumption

The POC UI assumption is a single consolidated Google Sheets workbook with one sheet per UI page.

- Existing sheets from the current workbook set may be copied directly where fit is complete.
- Existing sheets may be modified where the interaction exists but page shape must change.
- New sheets may be added where the workflow has user interaction with no current page.
- The consolidated workbook remains a UI surface only. Canonical persisted state remains in app schemas.

## Workflow touchpoint map

The table below maps each workflow stage to user-facing touchpoints and identifies where the interaction should occur in the consolidated workbook.

| id | stage       | touchpoint                            | io     | ui page                  | page format              | status |
| -- | ----------- | ------------------------------------- | ------ | ------------------------ | ------------------------ | ------ |
| 01 | pre-flight  | select close period and stage status  | input  | session_dashboard        | form plus stage board    | new    |
| 02 | pre-flight  | source readiness checklist            | input  | source_ingest_status     | checklist grid           | new    |
| 03 | forex       | review loaded period rates            | output | forex_rates              | month-rate table         | modify |
| 04 | data ingest | bank file receipt confirmation        | input  | source_ingest_status     | status grid              | new    |
| 05 | data ingest | ibkr period values                    | input  | ibkr_input               | period columns           | modify |
| 06 | data ingest | cpf oa, sa, ma values                 | input  | cpf_input                | period columns           | modify |
| 07 | data ingest | cash transactions                     | input  | cash_txn_entry           | transaction table        | copy   |
| 08 | data ingest | observed balances                     | input  | account_balance_input    | account-balance table    | modify |
| 09 | data ingest | investment quantity and price inputs  | input  | investment_input         | holdings table           | new    |
| 10 | data sync   | mapping sanity and sync evidence      | output | sync_review              | status and evidence grid | new    |
| 11 | reconcile   | variance and gap review               | output | reconcile_dashboard      | matrix plus filters      | modify |
| 12 | reconcile   | adjustment approval notes             | input  | reconcile_dashboard      | action columns           | modify |
| 13 | statements  | income statement                      | output | income_statement         | statement report view    | copy   |
| 14 | statements  | balance sheet                         | output | balance_sheet            | statement report view    | copy   |
| 15 | publish     | publish confirmation                  | input  | publish_control          | checklist plus confirm   | new    |
| 16 | publish     | session close log                     | input  | session_log              | append-only log table    | modify |
| 17 | bill flow   | bill record intake and status         | input  | bill_records             | lifecycle table          | new    |
| 18 | bill flow   | shared-cost allocation                | input  | shared_cost_entry        | allocation table         | modify |
| 19 | all stages  | checkpoint pass or fail feedback      | output | session_dashboard        | form plus stage board    | new    |
| 20 | reconcile   | account ledger drill-down             | output | ledger_explorer          | filterable ledger table  | new    |
| 21 | reconcile   | flagged transaction drill-down        | output | transaction_review_queue | queue plus detail panel  | new    |
| 22 | ad-hoc review | account ledger ad-hoc review        | output | ledger_explorer          | filterable ledger table  | new    |
| 23 | ad-hoc review | flagged transaction resolution      | input  | transaction_review_queue | action columns           | new    |

Status legend:

- copy: can be directly copied from an existing sheet with minimal structural change
- modify: existing sheet or range exists but requires schema or layout update
- new: no current sheet directly supports the required interaction

## Consolidated workbook page inventory

The page inventory below defines the complete POC UI scope for the consolidated workbook.

| id | page name                | primary purpose                        | source basis                           | status |
| -- | ------------------------ | -------------------------------------- | -------------------------------------- | ------ |
| 01 | session_dashboard        | period select, workflow checkpoints    | closing-session workbook intent        | new    |
| 02 | source_ingest_status     | source readiness and file receipt      | no direct page today                   | new    |
| 03 | forex_rates              | period forex review                    | financial-statements forex_rates       | modify |
| 04 | ibkr_input               | ibkr period values                     | ibkr-iba worksheet regions             | modify |
| 05 | cpf_input                | cpf period values                      | cpf worksheet regions                  | modify |
| 06 | cash_txn_entry           | cash transaction entry                 | cash-expenses recent_txns              | copy   |
| 07 | account_balance_input    | observed balances by account           | financial-statements balances plus gs  | modify |
| 08 | investment_input         | qty and unit price inputs              | closing-session manual input intent    | new    |
| 09 | category_mapping         | hb category classification             | homebudget-workbook cat_map            | modify |
| 10 | account_registry_status  | account class and status management    | financial-statements accounts          | modify |
| 11 | reconcile_dashboard      | variance review and actions            | financial-statements reconcile regions | modify |
| 12 | income_statement         | income statement review and approval   | financial-statements income_statement  | copy   |
| 13 | balance_sheet            | balance sheet review and approval      | financial-statements balance_sheet     | copy   |
| 14 | bill_records             | bill lifecycle entry and review        | shared-expenses plus bill bridge needs | new    |
| 15 | shared_cost_entry        | shared-cost entry and validation       | shared-expenses records                | modify |
| 16 | publish_control          | artifact confirmation and close        | no direct page today                   | new    |
| 17 | session_log              | append-only close history              | closing-session sessions               | modify |
| 18 | ledger_explorer          | account ledger drill-down              | no direct page today                   | new    |
| 19 | transaction_review_queue | flagged transaction review queue       | no direct page today                   | new    |
| 20 | sync_review              | data sync mapping and evidence review  | no direct page today                   | new    |

## Reusable page patterns

The consolidated workbook should use reusable page patterns so multiple workflows can share one page design with filters.

| id | reusable page     | reuse strategy                                               | applies to                 |
| -- | ----------------- | ------------------------------------------------------------ | -------------------------- |
| 01 | ledger_explorer   | one transaction table with account, period, source filters   | bank, cash, bills, ibkr    |
| 02 | account_registry  | one account list with account-type and status filters        | bank, wallets, investments |
| 03 | mapping_workspace | one mapping grid with category filters                       | category_mapping           |
| 04 | checkpoint_board  | one stage board with route and account-group filters         | all workflow stages        |
| 05 | exception_inbox   | one exception queue with stage and severity filters          | sync, reconcile, publish   |

Reusable page requirements:

- A reusable page must preserve lineage context, including period and source references.
- Filters must not hide blocking exceptions from checkpoint decisions.
- Page-level edits must maintain field contracts owned by their requirement pages.

## Financial statements review surface

The financial statements workbook is the reconcile review and statement output surface.

- The workbook presents income statement and balance sheet outputs for user review.
- The workbook provides reconciliation check regions covering cash accounts, position transfers, balance summary, expense cost centers, and forex mark-to-market.
- Users review reconciliation outputs in the workbook before approving close at the reconcile and publish checkpoints.
- The balances region in the financial statements workbook is the entry point for balance-only account observed balances.
- The forex_rates region in the financial statements workbook is the entry point for period exchange rates.
- In the consolidated workbook, these interactions are split into dedicated review and input pages while keeping the same data contracts.

## Data entry surfaces

### IBKR period data entry

The IBKR helper workbook provides a monthly column layout for user entry of IBKR period derived values.

- The workbook contains regions for net liquidity, cash, securities, and summary â€” each with period columns covering the active close range.
- Users enter IBA and IRA period values by column corresponding to each close period.
- Entries in this workbook are the input source for IBKR reconciliation.

### CPF period data entry

The CPF helper workbook provides a monthly column layout for user entry of CPF sub-account period values.

- The workbook contains regions for CPF total, OA, SA, MA, and summary â€” each with period columns covering the active close range.
- Users enter OA, SA, and MA period balances, contributions, and interest by column.
- Entries in this workbook are the input source for CPF reconciliation.

### Cash transaction entry

Cash transaction entry for TWH Cash SGD uses the cash-expenses workbook.

- The recent_txns region accepts user-entered cash transaction rows with date, description, amount, and category columns.
- Cash entries feed the data ingest stage for the cash account group.

### Shared cost record entry

The shared expenses workbook is the input surface for shared cost records during the monthly session.

- The records region accepts one row per shared cost event.
- Each record must supply date, description, total amount, participant count, user share amount, category, payee, and status fields.
- Field-level contracts for shared cost records are defined in the shared costs requirements page.

## Mapping management surface

Category and account mapping is managed through the category data model CRUD interface.

- The mapping management surface is a custom Google Sheets UI backed by backend CRUD services.
- The interface must support create, read, update, and delete operations against the category data model.
- The homebudget-workbook `cat_map` region is the current source for category classification data; the category management UI must replace ad hoc mapping file editing with a governed, service-backed update path.
- Account asset type assignment is managed through the account management UI and drives balance sheet placement.
- Mapping operations are event-driven and operate outside the monthly close run.
- Both the category management UI and the account management UI must support full lifecycle management of their respective records through a Google Sheets form without direct database access.

### category_mapping field contract

| id | field              | type        | required | unique | notes                                          |
| -- | ------------------ | ----------- | -------- | ------ | ---------------------------------------------- |
| 01 | hb_subcategory     | text        | yes      | yes    | HB subcategory name; unique within active rows |
| 02 | gl_code            | text (enum) | yes      | no     | expense line; FK to gl_code dimension          |
| 03 | subcategory_gl     | text (enum) | no       | no     | subcategory GL override; null if unused        |
| 04 | category_group_key | text (enum) | yes      | no     | cole_expenses, rental_expenses, discretionary  |
| 05 | is_active          | boolean     | yes      | no     | false for deprecated mapping rows              |

### account_registry_status field contract

| id | field       | type        | required | unique | notes                                           |
| -- | ----------- | ----------- | -------- | ------ | ----------------------------------------------- |
| 01 | account_id  | text        | yes      | yes    | canonical account identifier                    |
| 02 | asset_type  | text (enum) | yes      | no     | one of seven defined asset types                |
| 03 | owner       | text        | yes      | no     | TWH or COM; COM accounts are deprecated         |
| 04 | currency    | text        | yes      | no     | ISO 4217 currency code                          |
| 05 | stm_account | text        | no       | no     | statement digital twin key; null if not in path |
| 06 | is_active   | boolean     | yes      | no     | false for deprecated or out-of-scope accounts   |

## Session log surface

The closing-session workbook sessions region records close session events for audit and review.

- A session log entry must be written for each completed close session.
- The sessions log must support review of prior period close history from the same workbook interface.

### session_log field contract

| id | field            | type        | required | unique | notes                                      |
| -- | ---------------- | ----------- | -------- | ------ | ------------------------------------------ |
| 01 | session_id       | text        | yes      | yes    | system-generated unique session identifier |
| 02 | close_period     | text        | yes      | no     | YYYY-MM format; one row per session        |
| 03 | user_identity    | text        | yes      | no     | identifier of user who ran the session     |
| 04 | session_start_at | timestamp   | yes      | no     | UTC ISO-8601                               |
| 05 | session_end_at   | timestamp   | yes      | no     | UTC ISO-8601; set at session close commit  |
| 06 | close_outcome    | text (enum) | yes      | no     | completed, abandoned, or error             |
| 07 | notes            | text        | no       | no     | optional user notes recorded at close      |

## CLI as parallel surface

The CLI is a parallel interface for scripting and automation. It must support the same workflow stages and review checkpoints as the Google Sheets session UI through a command-driven interaction model.

- CLI review output must be human-readable and must present the same key evidence as the Google Sheets review surface for each checkpoint.
- CLI must present confirmation prompts before any destructive or commit action, consistent with the confirmation requirements defined in interaction and approvals.
- CLI must not be the exclusive path to completing a stage â€” Google Sheets remains the primary session surface.

## Non-functional requirements

- Data entry surfaces must surface validation errors at entry time and must not allow submission of records with missing required fields.
- Review surfaces must present outputs at sufficient detail for the user to confirm close readiness without opening underlying source data.
- Session log entries must be persisted before the session is marked closed.
- All Google Sheets workbooks in the consolidated workbook page inventory must be accessible through the config files in `gsheet/` without hardcoded identifiers in application code.
- The consolidated UI workbook identifier must be sourced from environment key `GS_UI_WKB_ID` in `.env` and must not be hardcoded in application code or docs.
- The consolidated workbook must expose every workflow touchpoint listed in the workflow touchpoint map.
