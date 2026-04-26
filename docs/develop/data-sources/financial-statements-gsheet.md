# Financial Statements Gsheet Guide

This guide documents the live `gsheet/financial-statements.json` workbook,
shows how the configured regions fit together, and explains how to extract the
current accounting logic from source feeds through reconcile rollups into the
published statements.

## Table of Contents

- [Boundary](#boundary)
- [Workbook Identity](#workbook-identity)
- [Region Groups](#region-groups)
- [Live Evidence](#live-evidence)
- [Accounting Logic](#accounting-logic)
- [Formula Extraction](#formula-extraction)
- [Legacy Cross-Reference](#legacy-cross-reference)
- [Inspection Artifacts](#inspection-artifacts)
- [Residual Gaps](#residual-gaps)

## Boundary

- Use this guide for workbook structure, region inventory, live schema evidence,
  and source-to-statement logic extraction notes.
- Use skill `data-sources-inspect` for the reproducible inspection workflow and
  command sequence.
- Use tracker `docs/develop/010/project-management/02-requirements.md` for
  dynamic task status only.

## Workbook Identity

- Config file: `gsheet/financial-statements.json`
- Workbook id: resolve `wkbid` from the config file at runtime
- Credential path: `.credentials/client_secret.json`
- Live evidence artifact:
  `.dev/.artifacts/financial_statements_workbook_inspection.json`

## Region Groups

### Source and bridge regions

| id     |          |                          |
| ------ | -------- | ------------------------ |
| region |          |                          |
| role   |          |                          |
| 01     | hb_exp   | HomeBudget expense feed  |
| 02     | hb_inc   | HomeBudget income feed   |
| 03     | hb_xfr   | HomeBudget transfer feed |
| 04     | stm_txns | statement transaction    |
| 05     | hb_ext   | external balance feed    |
| 06     | hb_gl    | normalized GL bridge     |

Range references:

- `hb_exp`, `hb_inc`, `hb_xfr`, `stm_txns`, and `hb_ext` use header `A1:E1`
  and data `A2:E`.
- `hb_gl` uses header `hb_gl!A1:W1` and data `hb_gl!A2:W`.
- `stm_txns` is the bank-statement transaction feed from the intermediate
  statements sheet. In the reference implementation, statement files are
  normalized, deduped on the statement transaction key, then merged into the
  account transaction set before GL posting.

### Mapping and account-classification regions

| id     |                  |                               |
| ------ | ---------------- | ----------------------------- |
| region |                  |                               |
| role   |                  |                               |
| 07     | fin_exp_cat_map  | expense to statement mapping  |
| 08     | accounts         | balance-sheet account mapping |
| 09     | balances         | period ending balance input   |
| 10     | forex_rates      | SGD conversion input          |
| 11     | income_statement | published income statement    |
| 12     | balance_sheet    | published balance sheet       |

Range references:

- `fin_exp_cat_map` uses `fin_expense_cat_map!A1:E1` and
  `fin_expense_cat_map!A2:E500`.
- `accounts` uses `accounts!A1:G1` and `accounts!A2:G500`.
- `balances` uses `balances!A1:D1` and `balances!A2:D`.
- `forex_rates` uses `forex_rates!A2:F2` and `forex_rates!A3:F`.
- `income_statement` uses `income_statement!A3:P3` and
  `income_statement!A4:P74`.
- `balance_sheet` uses `balance_sheet!A3:P3` and `balance_sheet!A4:P58`.

### Reconcile regions

| id     |             |                              |
| ------ | ----------- | ---------------------------- |
| family |             |                              |
| role   |             |                              |
| 13     | cash        | cash detail and cash summary |
| 14     | position    | position detail and transfer |
| 15     | balances    | account and class rollups    |
| 16     | expenses    | cost-center rollup           |
| 17     | fx          | FX mark to market rollup     |
| 18     | fin_stm     | statement summary rollup     |
| 19     | private fx  | private FX transfer detail   |
| 20     | private inc | private income detail        |

Region families:

- Cash: `reconcile_cash_acct_summary`, `reconcile_cash_acct_summary_sgd`,
  `reconcile_cash_acct_summary_usd`, `reconcile_cash_accts`
- Position: `reconcile_pos_xfr_summary`, `reconcile_pos_accts`
- Balances: `reconcile_bal_summary`, `reconcile_bal_by_acct`
- Expenses: `reconcile_exp_cost_centers`
- FX: `reconcile_fx_m2m_summary`
- Statement summary: `reconcile_fin_stm_summary`
- Private FX detail: `reconcile_pvt_fx_xfr_sgd`, `reconcile_pvt_fx_xfr_usd`
- Private income detail: `reconcile_pvt_inc_sgd`, `reconcile_pvt_inc_usd`

## Live Evidence

Evidence was generated from live workbook inspection using
`.dev/scripts/python/inspect_financial_statements_workbook.py` in `.dev/env`.

### Core region counts

| id     |                            |      |     |
| ------ | -------------------------- | ---- | --- |
| region |                            |      |     |
| rows   |                            |      |     |
| cols   |                            |      |     |
| 01     | hb_exp                     | 42   | 4   |
| 02     | hb_inc                     | 133  | 5   |
| 03     | hb_xfr                     | 455  | 5   |
| 04     | stm_txns                   | 91   | 5   |
| 05     | hb_gl                      | 5772 | 23  |
| 06     | fin_exp_cat_map            | 33   | 5   |
| 07     | accounts                   | 29   | 7   |
| 08     | balances                   | 1376 | 4   |
| 09     | forex_rates                | 92   | 6   |
| 10     | reconcile_exp_cost_centers | 4    | 20  |
| 11     | reconcile_fin_stm_summary  | 69   | 20  |
| 12     | reconcile_bal_by_acct      | 20   | 14  |
| 13     | income_statement           | 71   | 16  |
| 14     | balance_sheet              | 55   | 16  |

### Key schema observations

- `hb_gl` headers: `date`, `txn_type`, `accountType`, `account`, `amount`,
  `currency`, `category`, `subcategory`, `payee`, `transfer_account`, `notes`,
  `txn_currency`, `currencyAmount`, `year`, `month`, `month_id`,
  `fx_rate_SGD`, `budget_factor`, `amount_SGD`, `budget_amount_SGD`,
  `fa_budget`, `fa_category`, `fa_subcategory`
- `stm_txns` shares the same five-column grain as `hb_inc`, `hb_xfr`, and
  `hb_ext`: `year`, `month`, `account`, `amount`, `account_id`
- `accounts` headers: `id`, `type`, `owner`, `name`, `currency`, `HB account`,
  `stm account`
- `fin_exp_cat_map` headers: `fin_stm_category`, `COLE`, `fa_category`,
  `fa_subcategory`, `custom logic`
- `reconcile_fin_stm_summary` is the main monthly statement summary grid before
  publication into `income_statement`.
- `reconcile_bal_by_acct` and `reconcile_bal_summary` expose the grouped
  balance-sheet layer between raw balances and `balance_sheet`.
- `reconcile_bal_summary` uses statement-class labels such as `cash` in its
  `parameter` column, which indicates a class-level rollup above account detail.

## Accounting Logic

The workbook is not only a set of mapping tables. It is a staged transformation
pipeline from normalized source feeds into monthly statement outputs.

### Derivation stages

| id     |                  |                               |
| ------ | ---------------- | ----------------------------- |
| stage  |                  |                               |
| output |                  |                               |
| 01     | source feeds     | hb_exp hb_inc hb_xfr stm_txns |
| 02     | transaction map  | hb_gl                         |
| 03     | expense rollup   | reconcile_exp_cost_centers    |
| 04     | statement rollup | reconcile_fin_stm_summary     |
| 05     | publish P and L  | income_statement              |
| 06     | balance inputs   | balances forex_rates accounts |
| 07     | balance rollup   | reconcile_bal_by_acct         |
| 08     | publish B and S  | balance_sheet                 |

### Income statement derivation

- Treat `hb_exp`, `hb_inc`, `hb_xfr`, and `stm_txns` as normalized source feeds
  at the same period and account grain.
- `stm_txns` is the statement-origin feed. It complements HomeBudget-driven
  sources with bank-statement transactions that were normalized before being
  merged into the transaction set.
- `hb_gl` is the canonical transaction bridge. It carries source transaction
  fields plus mapped accounting fields such as `amount_SGD`, `fa_budget`,
  `fa_category`, and `fa_subcategory`.
- `fin_exp_cat_map` supplies the modern statement category vocabulary. The
  deep-pass artifact shows zero direct overlap against legacy reconcile labels,
  which means this sheet is a normalized mapping table, not a verbatim export of
  the legacy statement layout.
- `reconcile_exp_cost_centers` shows the monthly rollup of mapped expense rows.
- `reconcile_fin_stm_summary` is the broader statement summary layer. It carries
  the mixed income, expense, gain, and adjustment lines that are later exposed
  in `income_statement`.
- Practical extraction rule: derive expense logic by grouping `hb_gl.amount_SGD`
  by `year`, `month`, `fa_category`, and `fa_subcategory`. Use `fa_budget` and
  `budget_factor` when the workbook splits budget and actual views.
- Practical extraction rule: derive statement-income logic by tracing which rows
  in `reconcile_fin_stm_summary` feed the visible rows in `income_statement`,
  starting with `net income` and then the supporting income and expense blocks.

### Balance sheet derivation

- `balances` is the raw period ending balance source keyed by `account`.
- `accounts.id` is the join key for `balances.account` and supplies the account
  classification fields `type`, `HB account`, and `stm account`.
- `forex_rates` supplies the period FX rate used to translate non-SGD balances
  into SGD reporting values.
- `reconcile_bal_by_acct` exposes monthly totals by statement bucket.
- `reconcile_bal_summary` exposes a higher rollup by class, for example `cash`.
- Practical extraction rule: sum assets by account class by joining
  `balances.account` to `accounts.id`, converting non-SGD balances with the
  monthly FX input, then grouping by `accounts.stm account` for statement bucket
  output and by `accounts.type` or reconcile class label for broader asset class
  totals.
- Practical extraction rule: treat the `balance_sheet` output as the published
  presentation layer that consumes `reconcile_bal_by_acct`,
  `reconcile_bal_summary`, and carried-forward income statement results such as
  `net income PL`.

### Supporting reconcile paths

- `reconcile_cash_accts` and the `reconcile_cash_acct_summary*` ranges trace
  cash movement and beginning and ending balance checks.
- `reconcile_pos_accts` and `reconcile_pos_xfr_summary` trace position movement
  and transfer effects.
- `reconcile_fx_m2m_summary` isolates the FX mark to market layer.
- The private FX and private income ranges hold supporting detail for specific
  transfer and income cases that appear in the broader reconcile summaries.

## Formula Extraction

Current schema helpers still capture displayed values and shape only, but the
same `sqlgsheet` stack already exposes the underlying Google Sheets service
object, so formula tokens can be read now using direct API calls with
`valueRenderOption=FORMULA`.

### Formula targets

| id     |                            |                          |
| ------ | -------------------------- | ------------------------ |
| region |                            |                          |
| focus  |                            |                          |
| 01     | hb_gl                      | mapped columns U:W       |
| 02     | reconcile_exp_cost_centers | monthly expense totals   |
| 03     | reconcile_fin_stm_summary  | monthly statement totals |
| 04     | reconcile_bal_by_acct      | monthly balance totals   |
| 05     | income_statement           | published row formulas   |
| 06     | balance_sheet              | published row formulas   |

Formula inspection method:

- Use Google Sheets `spreadsheets.values.get` with
  `valueRenderOption=FORMULA` on representative cells from the targets above.
- Start with the first non-empty mapped row in `hb_gl` for `fa_budget`,
  `fa_category`, and `fa_subcategory`.
- Then read representative month cells from `reconcile_exp_cost_centers`,
  `reconcile_fin_stm_summary`, and `reconcile_bal_by_acct`.
- Finish with the visible month cells in `income_statement` and `balance_sheet`
  to confirm the final presentation formulas.
- For every captured formula, record the source ranges it references, the join
  keys it uses, the aggregation grain it implies, and the business rule it
  implements.

Direct `sqlgsheet` method:

```python
from sqlgsheet import gsheet

gsheet.CLIENT_SECRET_FILE = ".credentials/client_secret.json"
engine = gsheet.SheetsEngine()

result = engine.service.spreadsheets().values().get(
    spreadsheetId=wkbid,
    range="income_statement!D4",
    valueRenderOption="FORMULA",
).execute()
formula = result.get("values", [[""]])[0][0]
```

Live formula outputs from current workbook:

| id            |                     |                        |
| ------------- | ------------------- | ---------------------- |
| cell          |                     |                        |
| formula token |                     |                        |
| 01            | income_statement!D4 | =sum(D6:D8)            |
| 02            | balance_sheet!D4    | =bal_sht_prior_year!P4 |
| 03            | reconcile!H4        | =H18+H31*G1            |
| 04            | hb_gl!U2            | no formula token       |
| 05            | hb_gl!V2            | no formula token       |
| 06            | hb_gl!W2            | no formula token       |

Example evidence artifact:

- `.dev/.artifacts/financial_statements_formula_samples.json`
- generated by `.dev/scripts/python/inspect_financial_statements_formulas.py`

## Stage 2 Parity Checks

Parity checks are required to mark Stage 2 extraction complete and reproducible
for requirements work.

Run parity helper after source, deep-pass, workbook, and formula artifacts are
fresh:

```powershell
.\.dev\env\Scripts\python.exe .dev\scripts\python\inspect_stage2_parity_checks.py
```

Parity checks and gates:

- GL account coverage definition: lock parity coverage to canonical account
  columns `hb_gl.account` and `accounts.HB account`.
- Mapping integrity: fail if mapping cells are null-only or duplicate normalized
  mapping values are detected in profiled mapping text columns.
- `hb_exp` shape parity: pass if shape is consistent, or pass with classification
  `expected_sparse_trailing_column` when only trailing `account_id` is sparse.
- Formula-lineage parity: fail if no formula-token evidence exists for any
  required rollup layer in `income_statement`, `balance_sheet`, or `reconcile`.
- Normalized versus legacy label parity: structural and coverage checks only;
  direct label overlap is diagnostic and not a gate.

Current parity outcome:

- Artifact: `.dev/.artifacts/stage2_parity_checks.json`
- Summary status: `pass` (`5/5` checks passing)
- `hb_exp` classification: `expected_sparse_trailing_column`
- Formula-lineage parity: `pass` with formula tokens found for all required
  rollup sheets

## Legacy Cross-Reference

Legacy structure source:

- `data/financial-statements-reconcile/reconcile.csv`

Observed legacy labels include:

- `expenses`, `active income`, `other income`, `capital gain/loss`
- `position buy/sell`, `cash profit and loss`, `change in net assets`

The legacy reconcile source remains useful as a structural comparison baseline,
but the live workbook and helper artifacts are now the primary source for
current logic extraction.

Legacy comparison result:

- `.dev/.artifacts/stage2_reconcile_deep_pass.json` shows very low direct label
  overlap between legacy reconcile labels and the current normalized mapping
  sheets.
- Treat legacy labels as a structural reference for parity work, not as the
  authoritative source of current category names.

## Inspection Artifacts

Artifacts currently used for Stage 2 inspection and downstream parity work:

- `.dev/.artifacts/stage2_sources_inspection.json`
- `.dev/.artifacts/stage2_reconcile_deep_pass.json`
- `.dev/.artifacts/financial_statements_workbook_inspection.json`
- `.dev/.artifacts/financial_statements_formula_samples.json`
- `.dev/.artifacts/stage2_parity_checks.json`

Helper scripts currently used:

- `.dev/scripts/python/inspect_stage2_sources.py`
- `.dev/scripts/python/inspect_stage2_reconcile_deep_pass.py`
- `.dev/scripts/python/inspect_financial_statements_workbook.py`
- `.dev/scripts/python/inspect_financial_statements_formulas.py`
- `.dev/scripts/python/inspect_stage2_parity_checks.py`

## Residual Gaps

- Direct row-level GL account coverage parity still needs a dedicated row export
  helper if strict row-wise evidence is required beyond the current domain-based
  parity gate.
- Legacy reconcile labels and current normalized mapping labels are not direct
  one-to-one matches, so parity checks must compare structure and coverage, not
  raw label equality alone.
