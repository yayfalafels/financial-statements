# Reconcile Gap

Use this document to reproduce and retrace the reconcile-gap case with the current retained helper scripts.

## Contents

- Scope
- Environment
- Data Files
- Retained Helper Scripts
- Current Case Summary
- Closed Findings
- Jan-Feb v4 Cash Case
- Open Balance Sheet Issue

## Scope

This prompt tracks reconcile diagnostics for these two outputs:

- `cash reconcile error`
- `position reconcile error`

The core comparison is between two ways of deriving change:

1. ending balance minus beginning balance
2. transaction-derived change by component, such as income, expense, transfers, capital gain or loss, and FX

## Environment

- Re-use the existing `env` virtual environment.
- Store reusable scripts in `data/financial-statements-reconcile/.scripts/python/`.
- Prefer keeping scripts general enough to re-run on refreshed CSV exports.

## Data Files

All reconcile inputs are under `data/financial-statements-reconcile`.

- `balances.csv`: account balances by month in account currency.
- `hb_gl.csv`: transaction ledger with SGD conversion in `amount_SGD`.
- `expenses.csv`: helper sheet derived from the GL.
- `reconcile.csv`: primary reconcile sheet and the main diagnostic target.
- `balance_sheet.csv`: balance-sheet output derived from `reconcile.csv`.
- `income_statement.csv`: income-statement output derived from `reconcile.csv` and `expenses.csv`.

`reconcile.csv` layout, current working assumptions:

| Column | Meaning |
|---|---|
| 0-2 | metadata, including account and currency |
| 3 | label |
| 4 | annual total |
| 5-6 | secondary labels |
| 7 | opening period |
| 8-19 | monthly data |
| 20 | closing period |

Important row groups in `reconcile.csv`:

- top cash section, rows near 4-14
- net-assets reconcile section, rows near 305-367
- expense helper tables, rows near 287-302

## Retained Helper Scripts

Only the scripts below are kept because they are directly useful to reproduce and retrace the current case.

| Script | Purpose |
|---|---|
| `reconcile_errors.py` | Baseline monthly extraction of cash and position reconcile errors |
| `diag_reconcile_structure.py` | Jan-Feb v4 cash bridge trace, including mixed-currency summary normalization |
| `diag_irs_direct.py` | Trace IRS liability and expense handoff into the Jan-Feb bridge |
| `diag_balance_sheet_reconcile.py` | Frame the balance-sheet reconcile error against reconcile and statement outputs |
| `diag_income_statement_vs_reconcile.py` | Compare statement net income to reconcile transaction-derived change |
| `diag_issue04_formula_audit.py` | Regression audit of issue 04 formula identities |

Run scripts with the existing environment:

```powershell
c:/Users/taylo/VSCode_yayfalafels/financial-statements/env/Scripts/python.exe data/financial-statements-reconcile/.scripts/python/reconcile_errors.py
c:/Users/taylo/VSCode_yayfalafels/financial-statements/env/Scripts/python.exe data/financial-statements-reconcile/.scripts/python/diag_reconcile_structure.py
c:/Users/taylo/VSCode_yayfalafels/financial-statements/env/Scripts/python.exe data/financial-statements-reconcile/.scripts/python/diag_irs_direct.py
c:/Users/taylo/VSCode_yayfalafels/financial-statements/env/Scripts/python.exe data/financial-statements-reconcile/.scripts/python/diag_balance_sheet_reconcile.py
c:/Users/taylo/VSCode_yayfalafels/financial-statements/env/Scripts/python.exe data/financial-statements-reconcile/.scripts/python/diag_income_statement_vs_reconcile.py
c:/Users/taylo/VSCode_yayfalafels/financial-statements/env/Scripts/python.exe data/financial-statements-reconcile/.scripts/python/diag_issue04_formula_audit.py
```

## Current Case Summary

| Issue | Status | Short result |
|---|---|---|
| Cash reconcile structural bridge issue | Closed | Earlier cash error came from bridge treatment of HB cash transfers and USD expense FX |
| Position reconcile, Nov account error | Closed | `TWH IB POSITION USD` Nov ending balance was wrong |
| Position reconcile, Apr and Sep bridge issue | Closed | Missing IRA from position buy or sell subtable |
| Jan-Feb v4 cash residual | Closed | Root cause found in paired expense helper tables |
| Balance-sheet reconcile | Open | Current remaining issue is statement-side mapping drift |

## Closed Findings

### Cash Bridge, Historical

Earlier cash reconcile gaps were created in the net-assets cash bridge rather than in raw balances.

Key historical finding:

- transaction-derived cash change did not fully align with the top cash section
- the dominant closed drivers were HB cash-transfer treatment and USD expense FX handling

This is retained only as context. The current reproducible cash case is the Jan-Feb v4 case below.

### Position Reconcile

Closed fixes:

1. Nov position error came from an incorrect ending balance for `TWH IB POSITION USD`
2. Apr and Sep position bridge residuals came from a missing IRA component in the position buy or sell subtable

These issues are closed and do not need dedicated helper scripts anymore.

## Jan-Feb v4 Cash Case

Focus only on Jan and Feb for the latest case. March onward is out of scope for this pass.

### Symptom

From `diag_reconcile_structure.py` on the current export:

| Month | Cash error | Transfer gap | M2M gap |
|---|---:|---:|---:|
| Jan | -79.65 | -79.65 | -0.05 |
| Feb | -5,192.73 | -96.59 | -5,096.14 |

Bridge interpretation:

1. Jan is essentially a transfer-side mismatch only.
2. Feb is dominated by the `M2M forex USD` purchase component.

### Important Rows

Key rows in `reconcile.csv` for Jan-Feb tracing:

- line 7: top cash `MTM FX on blances`
- line 10: top cash `HB transfers`
- line 12: top cash `HF cash xfr`
- line 321: cash-bridge `position buy/sell`
- line 325: cash-bridge `M2M forex USD`
- lines 343-347: position buy or sell summary and children
- lines 361-363: M2M cash forex summary, cash balances, and purchases
- lines 287-302: paired expense helper tables

For mixed-currency summary tables, always normalize child rows into SGD using column C currency and the monthly FX row before comparing them to SGD summary rows.

### Root Cause

The Jan-Feb v4 cash residual was caused by an inconsistency between the two expense helper tables around rows 287-302:

1. there is a USD table by `account`
2. there is an SGD table by `transfer_account`
3. the USD table included `TWH IB USD`
4. the SGD table was missing the transfer to and from `TWH IB USD`

Effect on the bridge:

1. the missing SGD-side `TWH IB USD` transfer left a residual in `M2M cash forex -> purchases`
2. in Feb that residual appears directly as `-5,096.14`
3. Jan shows the smaller related transfer-side mismatch

### Resolution Direction

To close the Jan-Feb v4 cash case:

1. add the missing `xfr to or from TWH IB USD` entry in the SGD helper table
2. keep the USD and SGD expense helper tables symmetric
3. re-run `diag_reconcile_structure.py` and `diag_irs_direct.py`

Expected result after correction:

- Jan transfer gap should close or reduce to rounding tolerance
- Feb `M2M forex USD` purchase residual should disappear from the bridge

## Open Balance Sheet Issue

The remaining open issue is the balance-sheet reconcile error.

Current working conclusion:

1. balance-sheet balance snapshots broadly tie correctly
2. net-assets reconcile is not the current primary problem
3. the material mismatch sits in statement-side net income mapping

Most important current signal:

- Sep and Oct mismatch is concentrated in personal-income path timing

Use these retained scripts for issue 04:

1. `diag_balance_sheet_reconcile.py`
2. `diag_income_statement_vs_reconcile.py`
3. `diag_issue04_formula_audit.py`

Current issue-04 direction:

1. keep the balance-sheet problem separate from the Jan-Feb cash case
2. treat it as a statement-generation or mapping defect unless a fresh export proves otherwise

Apr (+2,536.36) and Sep (+1,483.63) are independent one-sided errors requiring separate investigation.

**Next steps**:
1. Keep item 02 (month 11) closed; no further work required unless source data changes again.
2. Continue diagnostics for open months 4 and 9.

### Hypothesis H1.5 missing account in cash transfers aggregation

The aggregation formula for HB cash transfers SGD was missing several accounts, including a new credit card `TWH UOB ONE SGD`
The formula has been updated and the reconcile sheet recalculated.

### H1 post-v1 review (after re-download of reconcile.csv / balances.csv)

Executed scripts:
- `reconcile_errors.py`
- `diag_cash_v0_vs_current.py`
- `diag_cash_net_assets_delta_v0_v1.py`
- `diag_added_sgd_accounts_impact.py`

#### Current status snapshot (issue 1)

1. Position reconcile is effectively closed in v1 (`~0` monthly).
2. Cash reconcile error remains non-zero in most months; annual cash error is now `-4,054.97` (improved from `-8,643.83`).
3. The old relation `cash error ~= -HF cash xfr + FX on USD exp` no longer holds in v1.

#### What changed from v0 to v1

Using direct v0 vs v1 deltas in net-assets cash rows:

1. `balance-derived change in cash` is unchanged for all months.
2. `transaction-derived change in cash` changed, and the delta equals the cash error delta exactly month-by-month.
3. Only two transaction-side component rows changed:
   - `position buy/sell` changed in **Apr (+2,536.36)** and **Sep (+1,483.62)**.
   - `M2M forex USD` changed in **Feb, Mar, Apr, May, Jun, Jul, Aug, Oct, Nov, Dec** by small amounts matching the prior FX residual pattern (for example Feb `+541.93`).

This indicates issue 1 in v1 is now driven by **net-assets bridge component mapping/sign behavior**, not by a balance issue.

#### Link to added-account transfer update

The newly added accounts (`TWH UOB One SGD`, `TWH EZLink`) change aggregate HB transfers as expected. Their monthly `transfer_out + transfer_in` net equals the month-by-month change seen in aggregate `HB transfers` between v0 and v1.

However, this does **not** by itself close cash reconcile, which means additional bridge formulas in net-assets rows (`position buy/sell`, `M2M forex USD`) are now the critical drivers.

### Next-level hypotheses for issue 1

1. **H1.6 — Net-assets `position buy/sell` cash-side formula now has scope leakage from position fix changes.**
   - Signal: v1 `position buy/sell` changed only Apr/Sep by exactly the same magnitudes as the previously open position residuals.
2. **H1.7 — Net-assets `M2M forex USD` cash-side formula is now absorbing the prior FX residual term (`FX on USD exp`) with altered sign/scope.**
   - Signal: month deltas align with prior FX residual pattern.
3. **H1.8 — Aggregate cash rows and net-assets cash bridge rows are no longer derived from one consistent transfer taxonomy after the formula edit.**
   - Signal: aggregate transfer edits improved totals but did not produce monthly cash closure.

### Diagnostic tests to perform next

1. **Test T1: position buy/sell reconstruction (cash bridge row).**
   - Rebuild monthly `position buy/sell` from `hb_gl.csv` transfers between cash-account set and position-account set.
   - Compare to v1 net-assets `position buy/sell` row and v0 row.
   - Acceptance: identify exact row/account contributors for Apr/Sep deltas.

2. **Test T2: M2M forex USD reconstruction (cash bridge row).**
   - Recompute monthly cash FX effect from USD cash balances and FX rates, then compare to v1/v0 `M2M forex USD` row.
   - Acceptance: determine whether v1 M2M includes an added term equivalent to prior `FX on USD exp` treatment.

3. **Test T3: bridge closure simulation.**
   - Recalculate cash reconcile with controlled substitutions:
     1) v1 with v0 `position buy/sell`
     2) v1 with v0 `M2M forex USD`
     3) v1 with both substitutions
   - Acceptance: isolate each term's contribution to remaining monthly cash errors.

4. **Test T4: sheet-formula reference audit (Google Sheet only).**
   - Verify formula ranges for net-assets rows `position buy/sell` and `M2M forex USD` after the recent transfer-formula edits.
   - Acceptance: ranges and signs are intentional, month-consistent, and aligned with cash-vs-position taxonomy.

### position (open) H3/H4 — Apr and Sep residual bridge diagnostics

Scope: explain the remaining open position errors for month 4 (+2,536.36) and month 9 (+1,483.63).

#### Step A: validate where the residual is created

The net-assets position section contains two `change in position` rows:

1. `position, change in position` (balance-derived): based on beginning/ending position balances
2. `change in position` (transaction-derived): reconstructed from `position buy/sell + position forex USD + capital gain/loss retirement + capital gain/loss liquid`

The transaction-derived row is internally consistent (formula tie-out is exact to floating-point tolerance). The listed `position reconcile error` is the difference between the two `change in position` rows.

For month 4:
- balance-derived change = -29,262.65
- transaction-derived change = -26,726.29
- residual = +2,536.36

For month 9:
- balance-derived change = +9,408.22
- transaction-derived change = +10,891.85
- residual = +1,483.63

#### Step B: validate position account blocks

Account-level checks across all investment/retirement blocks (CDP, IB POSITION, CPF OA/SA, IB IRA) show that for month 4 and month 9:

- `(end balance - beginning balance) - sum txns` ties to approximately zero at the account-block level.

This indicates the open residual is not due to a simple arithmetic break inside one account block in `reconcile.csv`.

#### Step C: interim interpretation

Because account blocks tie but the two net-assets position change tracks differ, the remaining issue is likely in the bridge logic between:

1. balance-derived position change aggregation, and
2. transaction-derived decomposition inputs.

Most likely candidates are mapping/scope differences (which rows feed each side), month-boundary treatment, or FX treatment for position-related flows.

#### Step D: executed diagnostics for open items 03 and 04

##### D.1 Bridge table (net-assets rows, `reconcile.csv`)

| Month | balance-derived change | transaction-derived change | buy/sell | position FX | cap gain/loss retirement | cap gain/loss liquid | bridge residual |
|---|---:|---:|---:|---:|---:|---:|---:|
| Apr | -29,262.65 | -26,726.29 | -13,509.38 | -5,327.08 | -1,121.71 | -6,768.12 | +2,536.36 |
| Sep | +9,408.22 | +10,891.85 | +2,072.12 | +1,227.83 | +1,413.86 | +6,178.04 | +1,483.63 |

Checks:
1. `buy/sell + position FX + cap gain/loss retirement + cap gain/loss liquid` equals transaction-derived change exactly (within floating-point tolerance).
2. Bridge residual equals the `position reconcile error` row exactly for Apr and Sep.

##### D.2 Independent check of position FX component

An independent approximation was run using USD position balances (`TWH IB POSITION USD`, `TWH IB IRA USD`) and monthly FX deltas.

| Month | calculated FX (approx) | sheet position FX | difference |
|---|---:|---:|---:|
| Apr | -5,224.24 | -5,327.08 | -102.84 |
| Sep | +1,192.58 | +1,227.83 | +35.25 |

Interpretation: position FX in the sheet is directionally and magnitudinally consistent with independent estimates; it is unlikely to explain the full residual (+2,536.36 / +1,483.63).

##### D.3 GL mapping signal (`hb_gl.csv`)

For Apr and Sep, position-linked GL rows are predominantly unmapped (`fa_category` blank) in the extracted CSV, which prevents direct category-level reconciliation from GL alone:

| Month | buy/sell candidate sum | capital/P&L candidate sum | unmapped position-related sum |
|---|---:|---:|---:|
| Apr | 0.00 | 0.00 | -7,690.63 |
| Sep | 0.00 | 0.00 | +7,635.70 |

Interpretation: with formulas lost during sheet-to-CSV conversion and sparse FA category tagging in position-linked rows, the CSV GL export is not sufficient to fully reconstruct the position bridge taxonomy.

#### Updated conclusion for items 03 and 04

1. The residuals for Apr and Sep are confirmed to originate at the bridge between balance-derived and transaction-derived position change, not from simple arithmetic errors within account blocks.
2. Position FX appears plausible and not large enough (by itself) to explain either residual.
3. The most likely remaining root cause is mapping/scope mismatch in the net-assets bridge logic (which rows are included on each side) after formula loss in CSV conversion.

#### Next step to close 03 and 04

1. Re-open the source Google Sheet formula cells for the net-assets position bridge rows (the two `change in position` rows and their component rows) for Apr and Sep, and compare range references cell-by-cell.
2. Backfill explicit bridge formulas into a scripted reconstruction (or helper sheet) so the mapping is deterministic in CSV form.

## Issue 4 (open) balance sheet reconcile error 

The cash and position reconcile errors are close to zero within tolerance, however the balance sheet reconcile error is still materially non-zero for many months, as high as +/- 7k.

The values in the balance sheet and income statement should be traceable directly to rows in the reconcile sheet, so in principle a complete diagnostic should be possible by inspection of the csv files and cross-checking aggregations and lookups.

### Issue 4 review - current findings

Executed scripts:
- `diag_balance_sheet_reconcile.py`
- `diag_balance_sheet_rollup.py`
- `diag_balance_sheet_shift.py`
- `diag_balance_sheet_category_map.py`
- `diag_balance_sheet_vs_net_assets_block.py`
- `diag_income_statement_vs_reconcile.py`

#### F1 - current `cash reconcile error` and `position reconcile error` are no longer the driver

Current monthly reconcile errors from `reconcile.csv` are close to zero:

| Month | cash error | position error |
|---|---:|---:|
| Jan | -76.34 | 0.00 |
| Feb | 1.64 | 0.00 |
| Mar | -11.43 | -0.01 |
| Apr | 0.96 | 0.00 |
| May | 30.53 | -0.01 |
| Jun | 0.16 | 0.00 |
| Jul | -31.18 | 0.00 |
| Aug | 4.61 | 0.00 |
| Sep | 6.51 | 0.01 |
| Oct | 27.72 | 0.00 |
| Nov | 16.79 | 0.00 |
| Dec | -1.22 | 0.00 |

These are far too small to explain the balance-sheet reconcile error magnitudes (for example Sep `-7,235`, Oct `+7,004`, Dec `-7,867`).

#### F2 - balance-sheet balance snapshots are broadly correct

The balance-sheet snapshot rows are internally consistent:

1. `opening net assets` matches the prior month's `net assets` snapshot.
2. `closing net assets` matches the current month's `net assets` snapshot.
3. `change in net assets = closing net assets - opening net assets` holds to rounding tolerance.

In addition, `balance_sheet.csv` `net assets` matches the total of the reconcile beginning-balance snapshot section to rounding tolerance. This means the problem is **not primarily in the balance-sheet ending-balance snapshots**.

#### F3 - the material mismatch is in statement-side `net income`

`balance_sheet.csv` row `net income PL` is defined as `income_statement.csv` row `net income`.

When compared to the **transaction-derived** `change in net assets` row in the reconcile net-assets section, the mismatch is:

| Month | BS / IS net income | reconcile txn change in net assets | difference |
|---|---:|---:|---:|
| Jan | 4,595.00 | 4,912.36 | -317.36 |
| Feb | 13,135.00 | 13,249.93 | -114.93 |
| Mar | -493.00 | -492.75 | -0.25 |
| Apr | -23,816.00 | -23,815.71 | -0.29 |
| May | -9,520.00 | -9,519.68 | -0.32 |
| Jun | -11,863.00 | -11,863.31 | +0.31 |
| Jul | 28,506.00 | 28,506.09 | -0.09 |
| Aug | -7,102.00 | -7,102.48 | +0.48 |
| Sep | 27,953.00 | 20,920.94 | +7,032.06 |
| Oct | 7,613.00 | 14,645.15 | -7,032.15 |
| Nov | 3,783.00 | 3,783.01 | -0.01 |
| Dec | 6,302.00 | -1,565.84 | +7,867.84 |

This is the core signal for issue 04.

#### F4 - the mismatch is concentrated in two statement components

Comparing `income_statement.csv` top rows to reconcile net-assets transaction components shows:

1. **Sep / Oct timing shift is in `personal income`**
   - Sep `personal income - (active income + other income) = +6,803.83`
   - Oct `personal income - (active income + other income) = -7,110.09`
   - This explains the Sep/Oct swing in `net income` almost entirely.

2. **Dec mismatch is in `investments PL` and `M2M USD forex`**
   - Dec `investments PL - reconcile profit and loss = +6,039.50`
   - Dec `M2M USD forex - reconcile M2M forex USD = +1,828.87`
   - Combined they explain the Dec `net income` overstatement of `+7,867.84`.

3. Jan / Feb smaller differences are also statement-side, mainly from `personal income` and expense/tax treatment, but these are secondary compared with Sep/Oct/Dec.

#### F5 - balance-sheet reconcile error is therefore downstream of income-statement mapping

Because:

1. balance snapshots tie,
2. reconcile net-assets bridge is nearly closed,
3. balance-sheet `net income PL` is sourced directly from income-statement `net income`, and
4. that `net income` is the materially misaligned row,

the balance-sheet reconcile error is best understood as a **statement-generation / statement-mapping defect**, not a remaining core reconcile defect in `reconcile.csv` balance rows.

### Next-level hypotheses for issue 04

1. **H4.1 - `income_statement.csv` `personal income` formula is month-shifted in Sep/Oct.**
   - Most likely candidate: salary / CPF / cash-income lookup ranges or month references are pointing to the wrong pivot month for one subcomponent.

2. **H4.2 - `income_statement.csv` net income rollup has month-specific source drift (now concentrated in Sep/Oct).**
   - Dec defects identified previously are resolved in the latest export; the dominant remaining signal is Sep/Oct timing movement.

3. **H4.3 - residual monthly differences are rounding or minor component-definition differences.**
   - `IS net income = net savings + investments PL + M2M USD forex + Reconcile error` does not tie exactly by integer-scale rounding deltas in many months.

### Diagnostic tests to perform next for issue 04

1. **Test B1 - formula audit for statement top rows (completed).**
    - Inputs used: formulas provided by user.
    - Checks executed in `diag_issue04_formula_audit.py`:
       - `BS reconcile error = change in net assets - net income PL` -> passes (rounding +/-1 in a few months).
       - `BS net income PL = IS net income` -> passes exactly.
       - `personal income = CPF contribution + total cash income - taxes paid` -> passes exactly for all months.
       - `investments PL = cash profit and loss + mark-to-market liquid + mark-to-market illiquid` -> passes to rounding tolerance.
       - `M2M USD forex = reconcile net-assets M2M forex USD` -> now passes to rounding tolerance, including Dec.
    - Additional finding: `IS net income = net savings + investments PL + M2M USD forex` -> matches exactly.

2. **Test B2 - subtable tie-out for Sep/Oct `personal income`.**
    - Rebuild `personal income = CPF contribution + total cash income - taxes paid` from exported rows and compare to reconcile `active income + other income`.
    - Status: completed (deep-dive) via `diag_issue04_sep_oct_attribution.py` and `diag_issue04_sep_oct_gl_trace.py`.
    - Result:
       - Sep residual (`IS net income - reconcile txn change`) = `+7,032.06`
       - Oct residual (`IS net income - reconcile txn change`) = `-7,032.15`
       - This is almost entirely explained by the personal-income path.
    - Root signal (salary-path cross-check vs GL):
       - Sep: `(IS net salary less CPF + IS CPF) - GL Salary and Wages = +7,031.83`
       - Oct: `(IS net salary less CPF + IS CPF) - GL Salary and Wages = -7,032.09`
    - Interpretation: Sep/Oct issue is a month-shift in the statement salary path (cash-income / CPF allocation), not a reconcile bridge arithmetic problem.

3. **Test B3 - subtable tie-out for Sep/Oct `net income` composition.**
   - Rebuild `investments PL` from:
     - `cash profit and loss`
     - `mark-to-market liquid`
     - `mark-to-market illiquid`
   - Plus validate Sep/Oct contributions from `net savings` and `Reconcile error` terms in the `net income` identity.
   - Goal: identify the exact source term causing the +7,032 / -7,032 Sep/Oct net-income shift.

4. **Test B4 - rerun full issue-04 snapshot after each sheet fix.**
   - Use `diag_balance_sheet_reconcile.py` and `diag_issue04_formula_audit.py` as regression checks.
   - Current latest status: Dec large error is closed; material open months are Sep/Oct.

### Working diagnosis

Issue 04 currently appears to be caused by **statement-level formula mapping drift**, with one previously found defect now fixed in latest export:

1. Sep/Oct `personal income` timing mismatch.
2. Dec `M2M USD forex` mis-mapping (previously confirmed) appears resolved after CSV refresh.
3. Sep/Oct swing is now traced to the statement salary path: `net salary less CPF` and `CPF contribution` together are shifted vs GL `Salary and Wages` by approximately +/-7,032 across Sep/Oct.

The next pass should be formula-level, not raw-ledger-level.

## New case v3, residual cash reconcile after chart-of-accounts changes

This section documents diagnostics for the latest workbook version with two structural updates:

1. Added IRS tax liability to balance sheet as a credit liability.
2. Added silver bullion as an investment position account.

Current symptom:

1. Cash reconcile error remains non-zero in the latest export.

### Why this case is different

Both changes introduce new account taxonomy edges that can break cash bridge closure without breaking account-level arithmetic:

1. IRS tax liability can reroute tax flows from direct expense into liability movement and settlement flows.
2. Silver bullion can create position buy or sell and mark-to-market paths that must remain isolated from cash-only transaction bridges.

From prior investigations, this pattern usually means a bridge scope issue, sign mismatch, or month-shifted reference, rather than a raw balance arithmetic error.

### New hypotheses for v3 cash residual

#### H5.1 Liability scope mismatch in cash bridge

IRS tax liability rows are included in balance-sheet snapshots but not consistently reflected in the transaction-derived cash bridge. This creates a mismatch between cash change from balances and cash change from components.

Signal:

1. Months with large tax accrual or settlement activity show disproportionate cash residuals.
2. Residual aligns with delta of liability movement versus taxes-paid component.

#### H5.2 Liability sign inversion in one bridge path

IRS liability is credit-nature. One path may use debit-style sign, causing addition where subtraction is required.

Signal:

1. Residual is close to `+/-` IRS liability movement by month.
2. Replacing one sign closes most months to rounding tolerance.

#### H5.3 Silver bullion account classification leakage

Silver bullion was added as investment, but one or more formulas still classify related rows as cash-side transfer or cash-side P&L.

Signal:

1. Months with bullion buys or mark-to-market moves show offsetting anomalies in `position buy/sell` versus cash bridge rows.
2. Position reconcile stays near zero while cash reconcile worsens, suggesting cross-bridge contamination.

#### H5.4 New-account range omission in aggregate cash references

A hard-coded range in aggregate cash rows or net-assets cash bridge excludes newly inserted rows after adding IRS and bullion lines.

Signal:

1. Affected rows tie at account level but aggregate bridge misses values.
2. Residual appears only after sheet structure changes, not after pure value edits.

#### H5.5 Month shift in tax-related statement path

Tax accrual and tax payment may now be split across different row families and one lookup references adjacent month.

Signal:

1. Pairwise month pattern where month N and month N+1 residuals nearly net to zero.

### Diagnostic plan for v3

#### Test C1, baseline residual extraction and attribution table

Objective:

1. Produce a month-level table with `cash reconcile error` and key candidate drivers in one frame.

Actions:

1. Extend `reconcile_errors.py` or create `diag_cash_v3_baseline.py`.
2. Extract monthly rows for:
   - `cash reconcile error`
   - `change in cash` balance-derived
   - `change in cash` transaction-derived
   - `HB cash xfr` or `HF cash xfr`
   - `M2M forex USD`
   - `position buy/sell` on cash bridge side
   - tax-related rows including taxes paid and new IRS liability movement if present

Acceptance:

1. A single monthly table that quantifies the residual and each candidate component.

#### Test C2, liability movement bridge reconstruction

Objective:

1. Determine whether IRS liability movement is represented consistently across net-assets and statement bridges.

Actions:

1. Compute monthly `IRS liability delta = ending liability - beginning liability` from `balance_sheet.csv` or reconcile snapshot section.
2. Compare against taxes-paid and any tax-accrual rows used by transaction-derived net-income or cash bridge.
3. Test both sign conventions in a closure simulation.

Acceptance:

1. Identify one sign and placement that reduces residual materially or explain why liability is not the dominant driver.

#### Test C3, silver bullion routing validation

Objective:

1. Verify bullion-related flows remain in position pathways and are excluded from cash-only bridge components except true cash settlement effects.

Actions:

1. Identify bullion account rows in `balances.csv`, `reconcile.csv`, and `hb_gl.csv`.
2. Rebuild monthly bullion:
   - balance delta
   - transfer-in or transfer-out with cash accounts
   - mark-to-market effects if applicable
3. Check whether bullion rows are accidentally included in cash aggregate ranges.

Acceptance:

1. Confirm clean taxonomy boundary or pinpoint exact row-range leakage.

#### Test C4, range and reference drift audit after row insertions

Objective:

1. Detect hard-coded ranges that were invalidated by inserted IRS and bullion rows.

Actions:

1. Compare latest `reconcile.csv` row ordering with prior version snapshots where closure was near zero.
2. Run a row-label presence and contiguity checker to detect broken assumptions in scripts and formulas.
3. In Google Sheet, inspect formulas for net-assets cash bridge component rows and aggregate cash section totals.

Acceptance:

1. Enumerate exact formulas or range boundaries requiring correction.

#### Test C5, controlled closure simulation

Objective:

1. Isolate dominant root cause by substitution tests.

Actions:

1. Recompute monthly cash residual under controlled substitutions:
   - include IRS liability delta term with sign A and sign B
   - remove bullion-linked terms from cash bridge
   - restore prior-version references for `position buy/sell` and `M2M forex USD`
2. Compare residual reduction per scenario.

Acceptance:

1. Rank root-cause candidates by explanatory power and nominate minimum sheet fix.

### Provision after ruling out IRS liability and silver bullion

Only after H5.1 and H5.3 are both tested and ruled out with evidence, continue with non-IRS and non-bullion diagnostics.

#### Fallback hypotheses, non-IRS and non-bullion

1. **H5.6 - Legacy cash bridge sign or scope regression returned.**
   - Re-check prior known sensitive rows, especially HB or HF cash xfr, M2M forex USD, and cash-side position buy or sell signs.
2. **H5.7 - Month index drift in lookup formulas.**
   - Check for one-column shifts in Sep or Oct style timing patterns even when account mappings are correct.
3. **H5.8 - Hidden range break from row insertions unrelated to new accounts.**
   - Validate all hard-coded ranges in aggregate cash and net-assets cash bridge, even if they do not reference IRS or bullion rows directly.
4. **H5.9 - Statement to reconcile mapping drift.**
   - Confirm net-assets transaction-derived change in cash still ties to statement-side components under the current export.

#### Fallback tests

1. **Test C6 - Legacy bridge parity test.**
   - Replay old closure relations and compare to current month vectors to detect reintroduced bridge logic defects.
2. **Test C7 - Month-shift detector.**
   - Run lag or lead correlation checks on candidate rows versus residual to identify one-month reference drift.
3. **Test C8 - Full range audit.**
   - Enumerate formula ranges and compare to expected label blocks to detect silent truncation or offset.
4. **Test C9 - End-to-end cash identity replay.**
   - Reconstruct cash change from balances and from transaction components using a script-only model, then diff each term.

Acceptance for fallback path:

1. Produce at least one non-IRS and non-bullion hypothesis that explains residuals materially, or formally conclude the remaining residual is within rounding tolerance.

### Resolution strategy for v3

1. Fix taxonomy first, ensure IRS liability stays in liability bridge logic and silver bullion stays in position logic.
2. Fix signs second, especially in liability movement and FX or M2M rows feeding cash bridge.
3. Fix ranges third, replace fragile hard-coded row spans with label-based lookups or named ranges where possible.
4. Re-run regression checks from earlier issues:
   - cash and position reconcile monthly near zero
   - balance sheet reconcile explained by statement mapping only
   - no new Sep or Oct style month-shift introduced

## Jan-Feb analysis after v4 IRS recalculation

### Updated observation

After the v4 refresh, the Jan-Feb cash reconcile errors are now:

| Month | Cash error |
|---|---:|
| Jan | -79.65 |
| Feb | -5,192.73 |

These still come from line 340, but the refreshed export changes the diagnosis materially.

### What v4 fixed

The IRS liability was recalculated and now appears consistently across the raw GL and the IRS account block:

| Month | GL IRS transfer | GL SGD equivalent | IRS account block sum txns |
|---|---:|---:|---:|
| Jan | -8,670 USD | -10,956.28 SGD | -8,670 USD |
| Feb | -4,033 USD | -5,096.50 SGD | -4,033 USD |

This means the IRS liability account itself is now internally consistent.

### Correct bridge structure

The relevant cash rows are:

1. **Line 316**: balance-derived `change in cash`
   - built from the top cash section and the individual cash account blocks
   - this is cash-only and does not directly include the `TWH IRS USD` credit-liability account
2. **Line 320**: transaction-derived `change in cash`
   - sum of lines 321-326
3. **Line 340**: `cash reconcile error`
   - equals `line 320 - line 316`

The component handoffs in the refreshed export are:

1. `line 322 + line 323 + line 324 = top-section HB income`
2. `line 326 = -line 367`
3. `line 367` comes directly from `expenses.csv` total expenses

Currency note:

1. Bridge rows are compared in SGD basis.
2. USD contributions are converted back to SGD using the top-row USD.SGD monthly FX rates in `reconcile.csv` line 1.
3. For Jan-Feb this means the bridge components and `line 340` are already post-conversion SGD values.

So the expense path is working. The refreshed IRS recalculation is already flowing into line 326 through line 367.

### Where the remaining gap now comes from

The residual in line 340 is explained by two bridge differences, not by a missing IRS expense row:

| Month | line 321 - top HB transfers | line 325 - top MTM FX on balances | Total = line 340 |
|---|---:|---:|---:|
| Jan | -79.65 | -0.05 | -79.65 |
| Feb | -96.59 | -5,096.14 | -5,192.73 |

Interpretation:

1. **Transfer-side mismatch**
   - line 321 in the net-assets cash bridge does not match the top cash-section `HB transfers` row
   - Jan residual is almost entirely this transfer mismatch
   - Feb has a smaller transfer mismatch of `-96.59`
2. **M2M cash FX mismatch**
   - line 325 carries `M2M forex USD`
   - in Feb this contributes `-5,096.14`, which is almost the entire remaining Feb error
   - this is now the dominant open driver after the IRS recalculation
   - the top-section comparator for this term is `reconcile.csv` line 7, labeled `MTM FX on blances`

### Revised conclusion

The old v3 explanation, that IRS was missing from the transaction-derived bridge, is no longer correct for v4.

What is true in v4:

1. IRS liability rows tie between `hb_gl.csv` and the IRS USD account block in `reconcile.csv`.
2. The expense handoff also ties: `line 326 = -line 367`, so the updated expenses sheet is already reaching the cash bridge.
3. The remaining Jan-Feb cash residual is now a **bridge mapping problem between**:
   - `line 321` versus top-section `HB transfers`, and
   - `line 325` versus top-section `MTM FX on balances`

### Next resolution direction

Focus the next sheet fix on the net-assets cash bridge rows, not on the IRS liability account block:

1. audit why `line 321` does not match the top cash `HB transfers` row for Jan-Feb
2. audit why `line 325` is carrying `-5,096.14` in Feb while the top cash `MTM FX on balances` row is zero
3. re-run the Jan-Feb bridge diagnostics after correcting those two row mappings

### Jan-Feb note on mixed-currency summary rows

For Jan-Feb diagnostics, summary subtable rows such as the position and cash P&L blocks must be compared on an SGD-normalized basis:

1. the child-row currency is in column C
2. USD child rows should be converted using the monthly FX row at the top of `reconcile.csv`
3. only after this conversion is it valid to compare the subtable breakdown to SGD summary rows such as `position buy/sell` and `cash profit and loss`

Executed script:

- `diag_reconcile_structure.py`

Jan-Feb normalized checks from the current export:

| Summary row | Jan converted child sum | Jan sheet summary | Jan delta | Feb converted child sum | Feb sheet summary | Feb delta |
|---|---:|---:|---:|---:|---:|---:|
| position buy/sell | 11,468.15 | 11,656.82 | -188.67 | -27,319.47 | -27,406.27 | 86.80 |
| cash profit and loss | -9,855.66 | -10,053.56 | 197.90 | 376.78 | 377.89 | -1.11 |

Interpretation:

1. after applying the monthly FX conversion, the visible Jan-Feb child rows still do not exactly tie to the SGD summary rows
2. this means the open Jan-Feb cash residual is not explained by a diagnostic mistake from ignoring column C currency alone
3. the Jan-Feb transfer-side issue remains a sheet-side mapping or basis mismatch in the summary handoff to line 321

### Refined Jan-Feb conclusion

With March onward ignored, the open cash reconcile residuals are:

| Month | Cash error | Transfer-side gap | M2M gap | Interpretation |
|---|---:|---:|---:|---|
| Jan | -79.65 | -79.65 | -0.05 | essentially a transfer-side summary mismatch only |
| Feb | -5,192.73 | -96.59 | -5,096.14 | dominated by the M2M purchase row, with a smaller transfer-side mismatch |

Jan finding:

1. `line 321` mirrors the cash-side signed copy of the position summary row
2. top cash `HB transfers` is `79.65` higher than that bridge row
3. Jan `M2M` is effectively closed, within rounding tolerance

Feb finding:

1. the `-5,096.14` cash reconcile component sits entirely in `M2M cash forex -> purchases`
2. this amount is on the same scale as the Feb IRS and IB USD transfer amount in SGD, which is about `5.1k`
3. the top cash section still reports zero for `MTM FX on blances` in Feb, so the open issue is a bridge-basis mismatch rather than a missing expense handoff

### Jan-Feb resolution found

The Jan-Feb root cause was found in the paired expense helper tables around rows 287-302 in `reconcile.csv`:

1. there are two companion tables, one USD `SUM of amount by account` table and one SGD `SUM of amount by transfer_account` table
2. the USD table already included `TWH IB USD`
3. the SGD table was missing the transfer to and from `TWH IB USD`

This omission explains the Jan-Feb cash-bridge behavior:

1. the missing SGD-side `TWH IB USD` transfer caused the FX purchase residual to remain in the derived `M2M cash forex -> purchases` row
2. in Feb this shows up directly as the `-5,096.14` gap between top cash `MTM FX on blances` and cash-bridge `M2M forex USD`
3. the smaller Jan transfer-side mismatch is part of the same Jan-Feb table-pair inconsistency, not a separate IRS expense-path defect

Updated interpretation:

1. the IRS liability and expense handoff were already flowing correctly
2. the remaining Jan-Feb defect was in the helper-table reconstruction of USD expense transfer recording, specifically the missing SGD-side `TWH IB USD` transfer rows
3. the resolution is to add the missing `xfr to/from TWH IB USD` in the SGD helper table so the USD and SGD expense tables remain symmetric

Status:

1. Jan-Feb root cause identified
2. prior Jan-Feb `M2M` open-item framing is superseded by this helper-table omission finding

Scripts for the refreshed v4 case:

- `diag_irs_direct.py` - verifies that the refreshed IRS liability ties between GL, the IRS account block, and the expense rollup path
- `diag_reconcile_structure.py` - shows that the open Jan-Feb residual now sits in the transfer and M2M bridge terms


