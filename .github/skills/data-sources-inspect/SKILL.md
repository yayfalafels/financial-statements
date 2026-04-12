---
name: data-sources-inspect
description: Inspect primary data sources across HomeBudget and Google Sheets for requirements evidence, schema discovery, and mapping validation
license: MIT
compatibility: Windows 11 and Python 3.12+
metadata:
  author: yayfalafels
  version: 1.0.0
---

## Contents

- Overview
- Summary
- Relevant skills
- Related documentation
- Project source-of-truth boundary
- HomeBudget inspection
- Google Sheets inspection
- Three-stage category mapping
- Bank statement source inspection
- Local inputs
- Non-tool source inspection
- Monthly closing process reference
- Source precedence inventory
- Source inspection reference
- Script locations and patterns
- Environment setup

## Overview

This skill defines the methodology for navigating and inspecting primary sources to support requirements validation and evidence gathering.

Use this skill for cross-source inspection workflows that combine HomeBudget and Google Sheets evidence collection.

## Summary

- Use this skill for cross-source inspection methodology during requirements work.
- Start with top-level source identification, then apply source-specific inspection procedures.
- Use companion skills for HomeBudget and Google Sheets implementation detail.

## Relevant Skills

- `homebudget`: HomeBudget API reference and procedures
- `gsheet-inspect`: Google Sheets inspection patterns
- `python`: python scripts and environment management
- `documentation`: working with text and markdown files


## Related Documentation

- [docs/develop/data-sources/inventory.md](../../../docs/develop/data-sources/inventory.md): Canonical inventory of POC primary references with explicit artifact paths and usage intent
- [docs/develop/data-sources/financial-statements-gsheet.md](../../../docs/develop/data-sources/financial-statements-gsheet.md): Financial-statements workbook structure and Stage 2 mapping region reference
- [docs/requirements/accounting-logic.md](../../../docs/requirements/accounting-logic.md): Accounting principles and transaction patterns
- [docs/requirements/account-classification.md](../../../docs/requirements/account-classification.md): Account type definitions
- [docs/requirements/transaction-category-mapping.md](../../../docs/requirements/transaction-category-mapping.md): Stage 3 mapping
- [docs/develop/data-sources/bank-statements-source-data.md](../../../docs/develop/data-sources/bank-statements-source-data.md): Bank statement source schema, account scope, stm_txns linkage, and inspection procedure
- [docs/develop/data-sources/local-inputs-source-data.md](../../../docs/develop/data-sources/local-inputs-source-data.md): Local monthly-closing input schemas, checks, and failure signals
- [docs/develop/data-sources/non-tool-source-data.md](../../../docs/develop/data-sources/non-tool-source-data.md): Reference repository inspection scope and evidence guidance
- [docs/develop/data-sources/source-precedence-inventory.md](../../../docs/develop/data-sources/source-precedence-inventory.md): Source inventory ranking and conflict inspection logging
- [reference/notion/Optimize monthly closing/Monthly closing 20bc378f707580f99849e024db8f12fb.md](../../../reference/notion/Optimize%20monthly%20closing/Monthly%20closing%2020bc378f707580f99849e024db8f12fb.md): Detailed current-state process narrative with accounts, steps, and source-tool linkage

## Project Source-of-Truth Boundary

- Keep requirement documents focused on what the system must do.
- Keep inspection process steps, script patterns, and troubleshooting in this skill.
- Keep non-tool source-data inventory details in `docs/develop/data-sources/`.

## HomeBudget Inspection

### Overview

HomeBudget is the core personal finance database. It contains:

- Accounts, including cost centers, wallets, investment accounts, and credit cards.
- Categories, including hierarchical expense and income types.
- Transactions, including expenses, income, and transfers.
- Reconciliation state.

### Category Structure

Categories in HomeBudget have two separate systems.

Expense categories:

- Hierarchical structure from parent to child categories.
- Examples include Health and Wellness to Medical expenses and Professional Services to Currency conversion.
- Queried via `client.repository.get_categories()` and `client.repository.get_subcategories(category_key)`.
- Used for expense and transfer tracking.

Income categories:

- Flat structure with no hierarchy.
- Income type names are stored as the category field in income transactions.
- Examples include salaries, dividends, interest, rebates, and reimbursements.
- Income records are currently uncategorized in HomeBudget and use `category_key = None`.
- Income categories are defined during monthly closing, not maintained as HomeBudget master data.
- Query with `client.list_incomes(start_date, end_date)`, then inspect description and amount fields.

### Key Account Patterns

Personal spending center:

- Account: `TWH - Personal`
- Role: consolidated cost center for personal expenses.
- Pattern: double-booking where funds transfer into the center and then expenses are recorded with categories.

Personal income center:

- Account: `TWH DBS Multi SGD`, or equivalent main personal account.
- Role: consolidated account for personal income.
- Pattern: income is booked to the center and non-center income is transferred back.

Investment accounts:

- Do not use expense categories.
- Use P and L classification such as M2M gains, dividends, interest, and profit or loss.
- Examples include `IB POSITION USD` and `TWH IB USD`.

### Python Inspection Pattern

Use `.dev/scripts/python/inspect_hb_categories.py` for the standard inspection flow.

```python
from homebudget import HomeBudgetClient
from datetime import datetime, timedelta

with HomeBudgetClient() as client:
    categories = client.repository.get_categories()
    for cat in categories:
        cat_key = cat.get('key') if isinstance(cat, dict) else cat.key
        subcats = client.repository.get_subcategories(cat_key)

    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    incomes = client.list_incomes(start_date=start_date, end_date=end_date)

    for inc in incomes:
        inc_date = getattr(inc, 'date', None)
        inc_description = getattr(inc, 'description', None)
        inc_amount = getattr(inc, 'amount', None)
```

### Critical Note on Income

- HomeBudget income commands do not enforce predefined income categories.
- Income labels are user-defined per transaction or batch.
- For requirements and mapping evidence, define income categories in monthly closing workflow artifacts.

## Google Sheets Inspection

### Overview

Google Sheets workbooks are used for:

- Helper workbook configuration and monthly closing validation.
- Category mapping between transaction categories and GL accounts.
- Reconciliation tracking and validation.

### Configuration Files

Workbook configs are stored in `gsheet/*.json`.

```json
{
  "wkbid": "1xF_cmgyKw2NHV6uj-bwo2O1D-eiyJwihlhFJSpMEKPg",
  "sheet_name": {
    "header": "worksheet!$A$1:$J$1",
    "data": "worksheet!$A$2:$J$182"
  }
}
```

Key configs:

- `gsheet/homebudget-workbook.json`: category mapping workbook with `cat_map` region.
- `gsheet/financial-statements.json`: statement output balances, forex rates, accounts, and expense category map.
- `gsheet/cpf.json`: CPF account balance regions.
- `gsheet/ibkr-iba.json`: IBKR IBA balance regions.
- `gsheet/cash-expenses.json`: personal cash expense transactions.
- `gsheet/closing-session.json`: monthly closing session register.
- `gsheet/shared-expenses.json`: shared expense records for bill payment workflows.

### Python Inspection Pattern

Use `sqlite-gsheet` package, following skill `gsheet-inspect`.

```python
from sqlite_gsheet import Client
import json

with open('gsheet/homebudget-workbook.json') as f:
    config = json.load(f)

client = Client(config['wkbid'])
df = client.read_range(
    range_name='cat_map!$A$1:$J$182',
    headers=True
)

print(df.columns.tolist())
print(df.head(20))
```

### Environment Note

The `sqlite-gsheet` package requires:

- `.credentials/client_secret.json` for Google Sheets API OAuth.
- Reinstallation when import fails:
  `pip install --force-reinstall --no-deps sqlite_gsheet-2.0.1-py3-none-any.whl`

## Three-Stage Category Mapping

### Stage 1: HomeBudget Category to GL Account

- Source: `cat_map` sheet in `homebudget-workbook.json`.
- Direction: HomeBudget expense category to GL account code.
- Coverage: expense categories only.

### Stage 2: GL Account to Financial Statements Category

- Primary workbook source: `gsheet/financial-statements.json`.
- Legacy reference source: `data/financial-statements-reconcile/reconcile.csv`.
- Direction: normalized source feeds and account classifications into statement
  categories, reconcile totals, and published statement rows.
- Companion schema guide:
  `docs/develop/data-sources/financial-statements-gsheet.md`.

Stage 2 work is not complete when you only know where the tabs live. The goal
is to extract the accounting logic, aggregation rules, and formula targets that
explain how the workbook derives `income_statement` and `balance_sheet`.

#### Stage 2 region map

| id | region          | role                     |
| -- | --------------- | ------------------------ |
| 01 | hb_exp          | HomeBudget expense feed  |
| 02 | hb_inc          | HomeBudget income feed   |
| 03 | hb_xfr          | HomeBudget transfer feed |
| 04 | stm_txns        | statement transaction    |
| 05 | hb_gl           | transaction bridge       |
| 06 | fin_exp_cat_map | expense mapping anchor   |
| 07 | accounts        | balance mapping anchor   |
| 08 | reconcile_*     | monthly rollups          |
| 09 | income_statement | published P and L        |
| 10 | balance_sheet   | published B and S        |

#### Stage 2 standard command sequence

Run these commands from the repository root using the helper-script environment.

```powershell
.\.dev\env\Scripts\python.exe .dev\scripts\python\inspect_stage2_sources.py
.\.dev\env\Scripts\python.exe .dev\scripts\python\inspect_stage2_reconcile_deep_pass.py
.\.dev\env\Scripts\python.exe .dev\scripts\python\inspect_financial_statements_workbook.py
.\.dev\env\Scripts\python.exe .dev\scripts\python\inspect_financial_statements_formulas.py
.\.dev\env\Scripts\python.exe .dev\scripts\python\inspect_stage2_parity_checks.py
```

Expected artifact outputs:

| id | output        | purpose                         |
| -- | ------------- | ------------------------------- |
| 01 | sources       | mapping anchor schema           |
| 02 | deep pass     | legacy structure check          |
| 03 | full workbook | full workbook evidence          |
| 04 | formulas      | formula token samples           |
| 05 | parity        | pass or fail parity gate checks |

Artifact paths:

- `sources`: `.dev/.artifacts/stage2_sources_inspection.json`
- `deep pass`: `.dev/.artifacts/stage2_reconcile_deep_pass.json`
- `full workbook`: `.dev/.artifacts/financial_statements_workbook_inspection.json`
- `formulas`: `.dev/.artifacts/financial_statements_formula_samples.json`
- `parity`: `.dev/.artifacts/stage2_parity_checks.json`

#### Stage 2 logic extraction workflow

1. Confirm workbook identity in `gsheet/financial-statements.json` and note the
   configured header and data references.
2. Run the three helper scripts above and use the artifacts as the source for
   row counts, column counts, headers, first-row samples, and flow summaries.
3. Build a source-grain note: `hb_exp`, `hb_inc`, `hb_xfr`, `stm_txns`, and
   `hb_ext` are all period and account feeds with the same five logical fields.
4. Build a mapping note: `hb_gl` is the canonical enriched transaction bridge
   because it contains source fields plus `amount_SGD`, `fa_budget`,
   `fa_category`, and `fa_subcategory`.
5. Build an output note: `reconcile_exp_cost_centers`,
   `reconcile_fin_stm_summary`, `reconcile_bal_by_acct`, and
   `reconcile_bal_summary` are the intermediate proof that mapped rows are being
   rolled into monthly statement totals before publication.
6. Only after the structural pass, run a formula pass on representative cells to
   capture the exact lookup and aggregation formulas.

#### Income statement extraction logic

- Treat `stm_txns` as the statement-source complement to HomeBudget feeds. In
  the reference implementation, statement files are normalized, deduped, and
  merged into the account transaction set before GL posting.
- Treat `fin_exp_cat_map` as the modern statement category dimension table.
  Legacy overlap is effectively zero, so it is not a simple copy of the legacy
  reconcile labels.
- Treat `hb_gl` as the row-level accounting bridge. It is where source rows are
  converted to SGD and assigned statement mapping fields.
- Treat `reconcile_exp_cost_centers` as the first proof of grouped expense logic.
- Treat `reconcile_fin_stm_summary` as the broader monthly statement rollup that
  feeds `income_statement`.
- Business-rule extraction target: explain which `hb_gl` fields determine the
  line item and how `amount_SGD` is grouped into the visible statement rows.

#### Balance-sheet extraction logic

- Treat `accounts.id` as the key for `balances.account`.
- Treat `accounts.type` and `accounts.stm account` as the account-class and
  statement-bucket dimensions.
- Treat `forex_rates` as the month-level conversion input for SGD balances.
- Treat `reconcile_bal_by_acct` as the grouped monthly balance layer and
  `reconcile_bal_summary` as the higher class-level layer.
- Business-rule extraction target: explain how balances are converted and then
  grouped into asset, liability, and net-asset classes before `balance_sheet`
  presentation.

#### Formula extraction workflow

Current schema helpers still read displayed values only, but formula-token
inspection is available now through the underlying sqlgsheet service object.

| id | region                    | focus                     |
| -- | ------------------------- | ------------------------- |
| 01 | hb_gl                     | mapped columns U:W        |
| 02 | reconcile_exp_cost_centers | month cells               |
| 03 | reconcile_fin_stm_summary | month cells               |
| 04 | reconcile_bal_by_acct     | month cells               |
| 05 | income_statement          | visible output cells      |
| 06 | balance_sheet             | visible output cells      |

Formula procedure:

1. Use the direct API path on sqlgsheet engine service with
  `spreadsheets.values.get` and `valueRenderOption=FORMULA`.
2. Capture the formula token, the referenced ranges, the apparent join keys, and
   the aggregation grain.
3. Translate each formula into a business-rule note, for example category lookup,
   FX conversion, monthly grouping, or statement carry-forward.
4. Compare the formula-level rule against the structural rule from the helper
   artifacts. If they disagree, treat the formula token as authoritative.

Direct method via sqlgsheet:

```python
from sqlgsheet import gsheet

gsheet.CLIENT_SECRET_FILE = ".credentials/client_secret.json"
engine = gsheet.SheetsEngine()

result = engine.service.spreadsheets().values().get(
   spreadsheetId=wkbid,
   range="income_statement!D4",
   valueRenderOption="FORMULA",
).execute()
formula_token = result.get("values", [[""]])[0][0]
```

Live sample outputs from current workbook:

| id | cell                | formula token           |
| -- | ------------------- | ----------------------- |
| 01 | income_statement!D4 | =sum(D6:D8)            |
| 02 | balance_sheet!D4    | =bal_sht_prior_year!P4 |
| 03 | reconcile!H4        | =H18+H31*G1            |
| 04 | hb_gl!U2            | no formula token       |

#### Stage 2 parity checks

Run the parity helper after source, deep-pass, workbook, and formula artifacts
are available.

Parity check scope and pass or fail logic:

- GL account coverage definition: confirm canonical account columns used for
  parity (`hb_gl.account` and `accounts.HB account`) and bind coverage checks
  to the profiled account domain.
- Mapping integrity: fail if `fin_exp_cat_map` has no non-empty cells; fail if
  normalized duplicate mapping values are detected in profiled mapping text
  columns.
- `hb_exp` shape parity: pass if header and data width match, or pass if a
  one-column delta is classified as expected sparse trailing `account_id`
  behavior and sibling source feeds still present full shape.
- Formula-lineage parity: fail if any required rollup sheet in
  `{income_statement, balance_sheet, reconcile}` has no reproducible formula
  token sample.
- Normalized versus legacy label parity: use structural and coverage checks,
  not direct string equality. Treat direct overlap counts as diagnostics only.

Expected parity evidence from current workbook:

- `.dev/.artifacts/stage2_parity_checks.json`
- summary status `pass`
- formula-lineage parity status `pass` with all required rollup sheets present
- `hb_exp` classification `expected_sparse_trailing_column`

#### Evidence required for requirements work

- Config file path and region references
- Artifact paths under `.dev/.artifacts/`
- Shared source grain across source and statement feeds
- Mapping columns in `hb_gl`
- Classification columns in `accounts`
- Rollup regions that sit between mapped rows and published statements
- Formula tokens for representative cells in rollup and output regions
- Open anomalies that affect parity or reproducibility

#### Current findings to carry forward

- The live full-workbook helper now confirms `stm_txns` as a valid source region
  and includes it in the income-statement flow.
- The deep-pass helper shows very low direct overlap between legacy reconcile
  labels and the normalized Stage 2 mapping sheets.
- Formula samples were captured with direct API calls via sqlgsheet service and
  saved in `.dev/.artifacts/financial_statements_formula_samples.json`.
- Parity checks classify `hb_exp` as `expected_sparse_trailing_column`, so the
  current shape mismatch is now documented as expected sparse behavior.
- Direct overlap between legacy and normalized labels remains intentionally low
  and is tracked as a diagnostic metric, not a parity gate.

#### Stage 2 completion test

Stage 2 extraction is complete enough for requirements drafting when a reader
can:

- identify the source feeds and their common grain
- identify where row-level mapping happens in `hb_gl`
- identify where balance classification happens in `accounts`
- identify the reconcile layers that prove the monthly rollups
- identify the output layers that publish the final statements
- reproduce schema, formula, and parity passes without relying on chat history

### Stage 3: Financial Statements Category to Derived Transaction Type

- Source: IBKR and CPF integration requirement documents.
- Direction: financial statements category to integration-specific classification.
- Coverage: expense and investment income cases.

### Mapping Asymmetry Warning

- Stages 1 and 2 are expense-focused.
- Stage 3 includes expense and income use cases.
- Personal income labels do not flow through HomeBudget category hierarchy.

## Bank Statement Source Inspection

### Overview

Bank statement source inspection covers the four statement-process bank accounts that feed the statement digital twin. Transaction sources are statement files, with PDFs retained as archive evidence where available. The reference database and ingestion script are in `reference/hb-finances/`. The canonical account list is at `data/monthly-closing/accounts.json`.

Account scope — only these four accounts are in `stm_txns`:

| id | account_name        | db_table           | currency |
| -- | ------------------- | ------------------ | -------- |
| 01 | TWH DBS Multi SGD   | TWH_DBS_MULTI_SGD  | SGD      |
| 02 | TWH CITI            | TWH_CITI_USD       | USD      |
| 03 | TWH UOB One SGD     | TWH_UOB_ONE_SGD    | SGD      |
| 04 | TWH Visa USD        | TWH_BOA_TRAVEL_USD | USD      |

IBKR, CPF, and balance-only accounts are outside this path.

Wells Fargo USD is a bank account but is outside the regular `statements.py` and `statements.db` process in current operations.

### Standard Inspection Command

```powershell
.\env\Scripts\python.exe .dev\scripts\python\inspect_statements_db.py
```

Expected artifact: `.dev/.artifacts/statements_db_inspection.json`

### Minimum Checks

- All four POC account tables are present: `TWH_DBS_MULTI_SGD`, `TWH_CITI_USD`, `TWH_UOB_ONE_SGD`, `TWH_BOA_TRAVEL_USD`
- `GL` table is present with a nonzero row count
- `balances` table is present with a nonzero row count
- All account tables have `date`, `description`, and `amount` columns at minimum
- `GL.account` values match the HB account names in `data/monthly-closing/accounts.json`
- Date format is consistent ISO date pattern across all account tables

### Schema Reference

For full schema details, table descriptions, and common anomalies, see `docs/develop/data-sources/bank-statements-source-data.md`.

## Local Inputs

Sample JSON and CSV files in `data/monthly-closing/` are sample template examples of how user inputs can be managed in the interim POC before the web ui is available.  The exact format of these are an output from a later stage during the design and are not considered a primary source of truth for requirements.

## Non-Tool Source Inspection

### Overview

Non-tool source inspection covers informational reference repositories in `reference/hb-finances/` and `reference/hb-reconcile/`.

**Repository Interpretation**

`reference/hb-finances/` is a legacy integration repository that contains statement ingestion, account mapping, and posting patterns.
`reference/hb-reconcile/` is a legacy reconciliation repository that contains matching logic and edit-generation methods for closing account gaps.

**Monthly Closing Relevance**

| id | artifact_path                                       | use in monthly close analysis                  |
| -- | --------------------------------------------------- | ---------------------------------------------- |
| 01 | reference/hb-finances/statement_config.json         | account to source-path and db-table mapping    |
| 02 | reference/hb-finances/statements.py                 | ingestion flow from statement files to GL      |
| 03 | reference/hb-finances/statements.db                 | statement digital twin persistence model       |
| 04 | reference/hb-reconcile/docs/reconcile.md            | reconciliation algorithm and gap equation      |
| 05 | reference/hb-reconcile/src/reconcile/reconcile.py   | forward and backward transaction matching      |
| 06 | reference/hb-reconcile/account_settings/txn_heuristics.json | account tolerance and heuristic controls |

### Standard Inspection Command

```powershell
.\env\Scripts\python.exe .dev\scripts\python\inspect_non_tool_sources.py
```

Expected artifact: `.dev/.artifacts/non_tool_sources_inspection.json`

### Minimum Checks

- repository file inventory is captured for both source roots
- doc, code, config, and data counts are present
- sample file paths are recorded for traceability
- reconcile or lineage mention samples are captured for evidence review
- reference-repo boundary is explicit: `hb-reconcile` treated as legacy reference, not baseline contract

### Schema Reference

For scope boundaries and evidence guidance, see `docs/develop/data-sources/non-tool-source-data.md`.

## Monthly Closing Process Reference

### Overview

Use `reference/notion/Optimize monthly closing/Monthly closing 20bc378f707580f99849e024db8f12fb.md` as a primary process-evidence artifact when requirements docs do not fully describe current-state execution detail.

This source is especially useful for:

- account-level scope confirmation
- real operator step sequencing
- source-system and tool coupling in the existing workflow
- identifying where statement, HomeBudget, and reconciliation flows intersect

### Evidence You Can Extract

- bank account scope and account-role descriptions
- monthly process sequence (bill payment, statements update, cash reconcile, account reconcile, financial statements)
- statement update mechanics and dependencies
- cash reconcile source and tool chain
- frequency and cadence details for each workflow stage

### Source-of-Truth Boundary

- Treat this file as current-state process evidence, not normative requirement authority.
- Use it to enrich requirement specificity when `docs/requirements/*` is under-specified.
- If this source conflicts with canonical requirement docs, resolve conflicts in requirement artifacts and document the decision.

### Minimum Inspection Checks

- confirm bank account list aligns with active account scope in requirements
- confirm process-stage names align with workflow orchestration terminology
- extract explicit source/tool references and map them to inventory artifacts
- flag any process behavior present here but missing from requirement docs as requirement gaps

## Source Precedence

Consider this guide for resolving conflicts between sources using precedence ranking.

| id | rank | source_group             | default_authority | notes                   |
| -- | ---- | ------------------------ | ----------------- | --------------------------------------------------------------------------------- |
| 01 | 1    | statement_digital_twin   | highest           | actual transactions from bank statements sot for txn amounts in account currency  |
| 02 | 2    | homebudget_ledger        | high              | homebudget ledger sot for other txn attributes date category description          | 
| 03 | 3    | helper_workbooks         | medium            | current process that generates fin stm from sources, sot for transformation logic |
| 04 | 4    | reference_repositories   | medium            | current process that generates fin stm from sources, sot for transformation logic |
| 05 | 5    | local_manual_inputs      | suggestion        | suggested design templates for input format to be used for the POC                |

Typical conflicting values inspected by precedence inventory:

- transaction presence
- amount and currency conversions
- date alignment and month-close assignment
- mapping lookup results
- month-end balances
- manual override values


## Source Inspection Reference
This reference matrix maps all POC primary sources to their inspection procedures and tools. Use this to navigate inspection workflows for requirements validation.

| id | source                     | category             | approach                  | tool / script      |
| -- | -------------------------- | -------------------- | ------------------------- | ------------------ |
| 01 | homebudget.db              | HomeBudget           | skill homebudget API      | homebudget CLI     |
| 02 | hb-config.json             | HomeBudget           | skill homebudget config   | file inspection    |
| 03 | ibkr-iba.json              | Google Sheets        | gsheet-inspect + script   | helper_schemas.py  |
| 04 | cpf.json                   | Google Sheets        | gsheet-inspect + script   | helper_schemas.py  |
| 05 | homebudget-workbook.json   | Google Sheets        | gsheet-inspect + script   | helper_schemas.py  |
| 06 | financial-statements.json  | Google Sheets        | gsheet-inspect + script   | helper_schemas.py  |
| 07 | cash-expenses.json         | Google Sheets        | gsheet-inspect + script   | helper_schemas.py  |
| 08 | shared-expenses.json       | Google Sheets        | gsheet-inspect + script   | helper_schemas.py  |
| 09 | closing-session.json       | Google Sheets        | gsheet-inspect + script   | helper_schemas.py  |
| 10 | hb-finances/statements.db  | Statement sources    | bank-statements guide     | inspect_stm_db.py  |
| 11 | data/monthly-closing/*     | Local inputs         | dropped template scope    | n/a                |
| 12 | hb-finances/*              | Ref repos            | non-tool guide + script   | inspect_non_tool   |
| 13 | hb-reconcile/*             | Ref repos            | non-tool guide + script   | inspect_non_tool   |

**How to use this reference:**

- **skill homebudget** — Follow procedures in the `homebudget` skill for API access and database queries.
- **gsheet-inspect + script** — Run `inspect_helper_schemas.py` for primary batch schema profiling across helper workbooks.
- **gsheet-inspect API** — Reference the direct API pattern in the Google Sheets Inspection section for custom or edge-case inspection paths.
- **deferred — see docs** — These sources are covered in related documentation sections; check Contents and Related Documentation.

## Script Locations and Patterns

Inspection scripts are organized under `.dev/scripts/` by script type.

- Python scripts in `.dev/scripts/python/`.
- Bash scripts in `.dev/scripts/bash/`.
- Do not place scripts in `.dev/` root.

Examples:

- `.dev/scripts/python/inspect_hb_categories.py`
- `.dev/scripts/python/inspect_cat_map.py`

Run scripts with the project virtual environment:

```powershell
.\env\Scripts\python.exe .dev\scripts\python\inspect_hb_categories.py
```

Do not use system Python or bare `python`.

## Environment Setup

### Prerequisites

1. Python environment at `env/Scripts/python.exe`.
2. Installed packages:
   - `homebudget` 2.1.1 or later.
   - `sqlite-gsheet` 2.0.1 or later.
3. Credentials at `.credentials/client_secret.json`.
4. HomeBudget database configured by `hb-config.json` at `%USERPROFILE%\OneDrive\Documents\HomeBudgetData\`.

### Verification

```powershell
.\env\Scripts\python.exe -c "from homebudget import HomeBudgetClient; print('OK')"
.\env\Scripts\python.exe -c "from sqlite_gsheet import Client; print('OK')"
```

### Common Issues

Issue: `ModuleNotFoundError: No module named 'sqlite_gsheet'`

- Solution: reinstall from wheel using force-reinstall and no dependencies.

Issue: HomeBudget config file not found.

- Solution: create `hb-config.json` with `db_path`.

Issue: Google Sheets API credentials not found.

- Solution: download OAuth 2.0 credentials and save to `.credentials/client_secret.json`.
