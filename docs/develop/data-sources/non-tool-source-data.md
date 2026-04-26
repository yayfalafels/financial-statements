# Non-Tool Source Data

## Contents

- [Summary](#summary)
- [Source Scope](#source-scope)
- [Repository Interpretation](#repository-interpretation)
- [Monthly Closing Relevance](#monthly-closing-relevance)
- [Extractable Business Logic](#extractable-business-logic)
- [Inspection Procedure](#inspection-procedure)
- [Evidence Capture](#evidence-capture)
- [Boundary Rules](#boundary-rules)

## Summary

This guide defines how to inspect non-tool primary sources under `reference/` and convert those artifacts into practical requirements evidence.

Inspection script: `.dev/scripts/python/inspect_non_tool_sources.py`
Inspection artifact: `.dev/.artifacts/non_tool_sources_inspection.json`

## Source Scope

| id            |                         |                                |
| ------------- | ----------------------- | ------------------------------ |
| artifact_path |                         |                                |
| role          |                         |                                |
| 01            | reference/hb-finances/  | legacy financial logic context |
| 02            | reference/hb-reconcile/ | legacy reconcile logic context |
| 03            | reference/notion-bills/ | legacy bill-tracking context   |

## Repository Interpretation

`reference/hb-finances/` is a legacy integration repository that contains statement ingestion, account mapping, and posting patterns.
`reference/hb-reconcile/` is a legacy reconciliation repository that contains matching logic and edit-generation methods for closing account gaps.
`reference/notion-bills/` is a Notion export repository containing bill-cycle, payee, paid-status, and payment-date workflow evidence.

## Monthly Closing Relevance

| id                            |                                                                            |
| ----------------------------- | -------------------------------------------------------------------------- |
| artifact_path                 |                                                                            |
| use in monthly close analysis |                                                                            |
| 01                            | reference/hb-finances/statement_config.json                                |
| 02                            | reference/hb-finances/statements.py                                        |
| 03                            | reference/hb-finances/statements.db                                        |
| 04                            | reference/hb-reconcile/docs/reconcile.md                                   |
| 05                            | reference/hb-reconcile/src/reconcile/reconcile.py                          |
| 06                            | reference/hb-reconcile/account_settings/txn_heuristics.json                |
| 07                            | reference/notion-bills/Bills 15ac378f707580ee8fe2e596ca250260.md           |
| 08                            | reference/notion-bills/bills 16ec378f707580fabf99f572568f5f60.csv          |
| 09                            | reference/notion-bills/billing_period 16ec378f707580d7b472d37487ec8127.csv |
| 10                            | reference/notion-bills/bill_payee 16ec378f707580e2ae93e4173891d72c.csv     |

| id                            |                                                |
| ----------------------------- | ---------------------------------------------- |
| artifact_path                 |                                                |
| use in monthly close analysis |                                                |
| 01                            | account to source-path and db-table mapping    |
| 02                            | ingestion flow from statement files to GL      |
| 03                            | statement digital twin persistence model       |
| 04                            | reconciliation algorithm and gap equation      |
| 05                            | forward and backward transaction matching      |
| 06                            | account tolerance and heuristic controls       |
| 07                            | exported index linking bill datasets           |
| 08                            | bill-level status, amount, payee, and due flow |
| 09                            | monthly bill coverage and paid-count rollup    |
| 10                            | recurring payee grouping and continuity checks |

## Extractable Business Logic

Reusable logic that can inform design and requirements:

- statement ingestion normalization to `date`, `description`, and `amount`
- account mapping from config to source path and ledger table
- reconciliation gap equation and zero-gap closure target
- exact-amount transaction matching with date tolerance windows
- edit-reduction heuristics that preserve gap neutrality
- account-level heuristic override configuration
- recurring bill-cycle model keyed by month with bill counts and paid counts
- bill-level payment checkpoint fields: amount, paid, payee, and payment_date
- payee-level continuity expectations across billing periods

Logic that should be treated as legacy context until confirmed:

- workbook-specific paths in `reference/hb-reconcile/data/reconcile.xlsx`
- legacy gsheet UI integration details in `reference/hb-finances/gsheet_config.json`
- account flows not in current POC operational scope
- Notion URL backlink values in exported CSV rows
- locale-specific date and decimal formatting from exported Notion views

## Inspection Procedure

Run from repository root:

```powershell
.\env\Scripts\python.exe .dev\scripts\python\inspect_non_tool_sources.py
```

Procedure outputs:

- total file count per repository
- counts by doc, code, config, and data files
- sample file paths for traceability
- files with reconcile or lineage term matches
- key artifacts with role labels and existence checks
- interpretation notes connected to monthly closing relevance
- files with bill and payee term matches for bill-payment requirements evidence

## Evidence Capture

For each repository, record:

- file inventory totals
- sample file list used during inspection
- references cited for requirements decisions
- boundary classification, operational or informational
- key artifact roles and monthly-closing relevance
- extracted logic notes and unresolved ambiguity notes

## Boundary Rules

- Treat reference repositories as informational context by default.
- Use operational sources first for conflict resolution.
- Cite reference repositories only when they clarify legacy behavior.
- Do not treat reference artifacts as authoritative over current runtime data.
- User-confirmed policy for current scope: `hb-reconcile` logic is legacy reference only, not a required baseline behavior contract.
- Treat `reference/notion-bills/` as process evidence for bill-payment workflow behavior and checkpointing semantics.
- When `reference/notion-bills/` conflicts with operational ledger data, treat operational postings as authoritative and log the discrepancy.
