# POC Primary References Inventory

## Contents

- [Summary](#summary)
- [Category overview](#category-overview)
- [HomeBudget](#homebudget)
- [Google Sheets workbooks](#google-sheets-workbooks)
- [Statement sources](#statement-sources)
- [Local inputs](#local-inputs)
- [Reference repositories](#reference-repositories)
- [Process references](#process-references)

## Summary

This is the canonical inventory of POC primary references used for requirements work. Each entry records the artifact path and usage intent, grouped by source system.

Source-of-truth boundary:

- Use this inventory as the reference index for primary artifact identification.
- Use skill `data-sources-inspect` for cross-source inspection procedures and methodology.
- Use skill `homebudget` for HomeBudget API and command usage.
- Use skill `gsheet-inspect` for Google Sheets inspection procedures.

## Category overview

| id | category                | count |
| -- | ----------------------- | ----- |
| 01 | HomeBudget              |     2 |
| 02 | Google Sheets workbooks |     7 |
| 03 | Statement sources       |    10 |
| 04 | Local inputs            |     6 |
| 05 | Reference repositories  |     3 |
| 06 | Process references      |     1 |

## HomeBudget

`$HB_DATA` = `%USERPROFILE%\OneDrive\Documents\HomeBudgetData`

| id | artifact_path               | usage_intent                                                  |
| -- | --------------------------- | ------------------------------------------------------------- |
| 01 | $HB_DATA\Data\homebudget.db | Core transaction, account, and category data for requirements |
| 02 | $HB_DATA\hb-config.json     | Client config for HomeBudget Python API access                |

## Google Sheets workbooks

All config files are in `gsheet/` and map to Google Sheets workbook IDs and named data regions.

| id | artifact_path                    | usage_intent                                                 |
| -- | -------------------------------- | ------------------------------------------------------------ |
| 01 | gsheet/homebudget-workbook.json  | Stage 1 category mapping evidence via cat_map region         |
| 02 | gsheet/financial-statements.json | Output balances, forex rates, accounts, and expense cat map  |
| 03 | gsheet/cpf.json                  | CPF account balance regions for integration requirements     |
| 04 | gsheet/ibkr-iba.json             | IBKR IBA balance regions for integration requirements        |
| 05 | gsheet/cash-expenses.json        | Personal cash expense transaction evidence                   |
| 06 | gsheet/closing-session.json      | Monthly closing session register                             |
| 07 | gsheet/shared-expenses.json      | Shared expense records for bill payment requirements         |

## Statement sources

Statement sources in `reference/statements/` are organized by account. Each subdirectory contains periodic statements for the corresponding account.

| id | artifact_path                                 | usage_intent                                    |
| -- | --------------------------------------------- | ----------------------------------------------- |
| 01 | reference/statements/citi-twh/                | Citibank TWH personal credit card statements    |
| 02 | reference/statements/dbs-multi/               | DBS Multi-Currency savings statements           |
| 03 | reference/statements/ibkr-iba/                | IBKR IBA activity reports in CSV format         |
| 04 | reference/statements/ibkr-ira/                | IBKR IRA activity reports in CSV format         |
| 05 | reference/statements/others/closing-session/  | Monthly closing session PDFs                    |
| 06 | reference/statements/others/payslip/          | Payslip PDFs for income verification            |
| 07 | reference/statements/singtel/                 | Singtel utility bill statements                 |
| 08 | reference/statements/spservices/              | SP Services utility statements                  |
| 09 | reference/statements/uob/                     | UOB One bank statements                         |
| 10 | reference/statements/wells-fargo/             | Wells Fargo account statements                  |

## Local inputs

Local input files in `data/monthly-closing/` provide manual balance entries, account mappings, and transaction batch inputs for monthly close workflows.

| id | artifact_path                              | usage_intent                                             |
| -- | ------------------------------------------ | -------------------------------------------------------- |
| 01 | data/monthly-closing/accounts.json         | Account definitions with s3 IDs and statement patterns   |
| 02 | data/monthly-closing/balance-accounts.json | Balance account definitions with alias and month ID      |
| 03 | data/monthly-closing/account-balances.csv  | Historical manual account balance inputs by month        |
| 04 | data/monthly-closing/inputs.json           | Manual parameter overrides for the monthly close         |
| 05 | data/monthly-closing/txns.json             | Monthly close transaction batch for income and transfers |
| 06 | data/monthly-closing/txns.json.sample      | Sample transaction batch showing IBKR and CPF patterns   |

## Reference repositories

Reference repositories in `reference/` contain legacy artifacts and prior-generation implementation code used for requirements context and evidence.

| id | artifact_path           | usage_intent                                               |
| -- | ----------------------- | ---------------------------------------------------------- |
| 01 | reference/hb-finances/  | Legacy financial reconcile system with GL and category logic |
| 02 | reference/hb-reconcile/ | Legacy reconcile engine with transaction heuristics        |
| 03 | reference/notion-bills/ | Legacy Notion export for bill-cycle and payment-status workflow evidence |

## Process references

Process references capture detailed operator workflow evidence from historical planning artifacts. Use these sources to understand current-state execution detail when requirement docs are less granular.

| id | artifact                          | usage_intent                                                      |
| -- | --------------------------------- | ----------------------------------------------------------------- |
| 01 | notion monthly closing process[1] | Detailed current-state monthly close process and source/tool flow |

1. full path `reference/notion/Optimize monthly closing/Monthly closing 20bc378f707580f99849e024db8f12fb.md`