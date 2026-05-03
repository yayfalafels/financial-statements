---
title: Reconciliation Design
doc_type: design
topic_type: owner
owner: reconciliation-engine
scope: poc
last_updated: 2026-05-03
status: draft
---

# Reconciliation Design

## Summary

This document specifies the reconciliation method classes, account-group procedures, tolerance rules, variance interpretation, and approval authority for the POC close cycle. It provides the design contract for both the transaction-level and balance-level reconciliation methods, and the account-level reconciliation behavior after orchestrator dispatch to stage 6.

## Authority

This document is the authoritative source for reconciliation design decisions.
If any conflict exists between this document and requirements artifacts, this document supersedes those requirements for reconciliation scope.

## Table of contents

- [Summary](#summary)
- [Authority](#authority)
- [Method Class Specifications](#method-class-specifications)
  - [Transaction-level Method Class](#transaction-level-method-class)
  - [Balance-level Method Class](#balance-level-method-class)
  - [Cross-cutting Concerns](#cross-cutting-concerns)
- [Account-group Procedures](#account-group-procedures)
  - [Procedure Table](#procedure-table)
  - [Variance Interpretation Matrix](#variance-interpretation-matrix)
  - [Tolerance Rules by Account Group](#tolerance-rules-by-account-group)
  - [Approval Authority and Override Policy](#approval-authority-and-override-policy)
- [Key Findings](#key-findings)
- [Recommendations and Risks](#recommendations-and-risks)

## Method Class Specifications

This section specifies the contract, algorithm, parameters, and invocation interface for the two reconciliation method classes.

### Transaction-level Method Class

The transaction-level method compares transactions from two independent sources — ledger and statement — and produces a minimal edit set that closes the reconcile gap to zero.

#### Edits Model Structure

The method produces an edits table with the following fields and semantics:

| id | field       | type                      | description                  |
| -- | ----------- | ------------------------- | ---------------------------- |
| 01 | `source`    | `"ledger","statement"`    | row source                   |
| 02 | `date`      | iso date                  | txn date (`YYYY-MM-DD`)      |
| 03 | `amount`    | decimal                   | txn amount in acct currency  |
| 04 | `edit`      | `"remove","add","update"` | ledger-side action           |
| 05 | `edit_amt`  | decimal                   | signed delta from edit       |
| 06 | `note`      | string                    | txn note or description      |
| 07 | `ledger_ix` | int or null               | ledger row index (0-based)   |
| 08 | `stmt_ix`   | int or null               | statement row index (0-based)|

**Invariant requirement:** The sum of `edit_amount` over any removed or modified subset must equal zero to preserve the reconcile gap equation.

#### Gap Equation and Validity Criterion

The reconcile gap with a given edits set is defined as:

```
gap = ledger_end_balance + sum(edit_amount over all edits) - statement_end_balance
```

A solution is **valid** if and only if `gap == 0.00`, within currency rounding precision — typically 0.01 for SGD.
Among all valid solutions, the method selects the **minimal edit set** — the solution with the fewest number of edit rows.

**Requirement ref:** reconciliation-engine.md § Transaction-level method class / Edits model

#### Ledger and Statement Slice Construction

Before matching, two slices are constructed from the source GL sheets for the `(account, year, month)` scope:

**Ledger slice construction:**
1. Filter `hb_gl` for rows matching account, year, month.
2. Drop rows where `txn_type == "balance"` — these are balance assertion rows, not transactions.
3. Drop rows with null `amount`.
4. Sort by `date` ascending, with original row index as tie-breaker.
5. Compute running `balance`: `balance[i] = opening_balance + cumsum(amount)[0:i+1]`.
6. Retain only columns: `index`, `date`, `amount`, `balance`, `category`, `subcategory`, `payee`, `notes`.

**Statement slice construction:**
1. Filter `stm_gl` for rows matching account, year, month.
2. Drop rows with null `amount`.
3. Sort by `date` ascending, with original row index as tie-breaker.
4. Compute running `balance`: `balance[i] = opening_balance + cumsum(amount)[0:i+1]`.
5. Retain only columns: `index`, `date`, `amount`, `balance`, `description`.

**Opening balance discovery:**
- The opening balance is the `balance` value from the prior period row in the `balances` dataset.
- For month M in year Y, look up `(account, year=Y, month=M-1)` in `balances`.
- For January (month=1), look up `(account, year=Y-1, month=12)`.
- If no prior period row exists, initialization fails with a "missing opening balance" error.

**Statement ending balance cross-check:**
- The statement slice ending balance (last row `balance` value) must equal the `balance` value in the `balances` dataset for `(account, year, month)`.
- If the difference exceeds account precision — typically 0.01 — log a warning and flag the variance for user review before proceeding.
- This cross-check detects issues in statement ingest or GL schema inconsistency.

**Requirement ref:** reconciliation-engine.md § Account-group procedures / Bank statement-process accounts

#### Forward Pass Algorithm

The forward pass greedily matches ledger and statement transactions that are unambiguously equivalent, then builds an initial edits set from unmatched transactions.

**Match procedure:**

For each unmatched ledger transaction:
1. Identify all statement transactions not yet matched.
2. Filter candidates by three-part match test; all three must hold:
   - **Amount test:** `amount_ledger == amount_statement` — exact match, same sign, exact cents, currency rounding.
   - **Date test:** `abs(date_ledger - date_statement) <= date_tolerance_days` — configurable per account, default 3.
   - **Uniqueness test:** exactly one statement candidate remains after filtering; zero or multiple candidates result in no match.
3. If exactly one candidate remains, mark the pair `(ledger_idx, stmt_idx)` as matched.
4. If zero or multiple candidates, leave the ledger transaction unmatched.

**Match results:**
- `matches`: list of `(ledger_idx, stmt_idx)` tuples.
- `unmatched_ledger`: set of ledger indices not in any match.
- `unmatched_stmt`: set of statement indices not in any match.

**Forward edits construction:**
- For each `ledger_idx` in `unmatched_ledger`: add one `remove` edit with `edit_amount = -amount`.
- For each `stmt_idx` in `unmatched_stmt`: add one `add` edit with `edit_amount = +amount`.

**Expected outcome:** If GL data are internally consistent — no missing or spurious transactions — the forward edits already yield `gap == 0.00`. However, the set may not yet be minimal due to boundary conditions or timing variations.

**Requirement ref:** reconciliation-engine.md § Transaction-level method class / Forward and backwards algorithm; hb-reconcile/docs/reconcile.md § Forward algorithm

#### Backward Pass Algorithm

The backward pass starts from a trivially valid solution — remove all ledger, add all statement — and reduces it using forward-match evidence. This alternative derivation serves as a correctness assertion.

**Backward procedure:**

1. **Trivial solution construction:**
   - Create a `remove` edit for every ledger transaction with `edit_amount = -amount`.
   - Create an `add` edit for every statement transaction with `edit_amount = +amount`.
   - By construction, `sum(edit_amount) = 0.00` and `gap = 0.00`.

2. **Reduction via forward matches:**
   - For each forward match pair `(ledger_idx, stmt_idx)`:
     - Remove the `remove` edit for `ledger_idx` from the trivial set.
     - Remove the `add` edit for `stmt_idx` from the trivial set.
   - The reduced set remains valid because we are removing paired edits whose `edit_amount` values sum to zero.

3. **Heuristics application:**
   - Apply the same heuristics to both the forward and backward-reduced edit sets, described in the Heuristics Layer section below.

**Correctness assertion:**
- After heuristics, the forward and backward-reduced edit sets **must be identical** in shape and values.
- If they differ, this indicates a bug in the heuristics or a logical inconsistency in the algorithm and must be investigated before proceeding.
- This equivalence is a mandatory correctness check, not an optional validation.

**Requirement ref:** hb-reconcile/docs/reconcile.md § Backwards algorithm

line 76: "Filter `hb_gl` for rows", "The opening balance is the `balance` value from the prior period row in the `balances` dataset": `hb_gl`, `txn_type == "balance"` filter, these are legacy references to the current workflow and schema. preserve the abstract algorithm logic, but align with the current data model design schema and table names. review and apply updates throughout the document, algorithm descriptions for txn level reconciliation, balance level reconciliation procedures
line 111: "`amount_ledger`": jargon insertion. you introduce an unknown variable `amount_ledger` without defining and linking it to the ledger that you described in the section above describing ledger slicing construction. make the links more explicit.

#### Heuristics Layer

Heuristics remove redundant edits while preserving the gap invariant. All heuristics must satisfy:

```
sum(edit_amount over modified or removed subset) = 0.00
```

**General heuristics applied to all accounts:**

**1. Net-zero pairs (`net_zero_pair`)**
- **Purpose:** Remove pairs of opposite-amount edits within a configurable date window.
- **Procedure:** Identify pairs `(i, j)` where:
  - `edit_amount[i] == -edit_amount[j]` — exact opposites.
  - `abs(date[i] - date[j]) <= date_tolerance_days` — configurable, default 3.
  - `source[i] == source[j]` — both from ledger or both from statement.
  - Drop both edits from the set.
- **Gap invariant:** preserved because the two `edit_amount` values sum to zero.
- **Use case:** Captures internal "split then re-join" corrections within the ledger or statement.
- **Config source:** `txn_heuristics.json` / `general_heuristics` / `net_zero_pair`

**2. Same-amount zero-sum clusters (`same_amount_zero_sum_cluster`)**
- **Purpose:** Remove clusters of identical-amount edits from mixed sources that net to zero.
- **Procedure:** For each distinct `amount` value:
  1. Collect all edits with that amount.
  2. Require at least one `source="ledger"` edit and at least one `source="statement"` edit.
  3. Compute `cluster_sum = sum(edit_amount)` over the cluster.
  4. If `abs(cluster_sum) <= amount_tolerance` — default 0.01 — remove the entire cluster.
- **Gap invariant:** preserved because the cluster's net `edit_amount` is zero.
- **Use case:** Captures ambiguous repetitions — for example, two McDonald's charges for the same amount on consecutive days matched by ambiguity — that form a self-contained zero-sum bubble.
- **Config source:** `txn_heuristics.json` / `general_heuristics` / `same_amount_zero_sum_cluster`

**Account-specific heuristics configured in `txn_heuristics.json` / `account_heuristics`:**

**1. DBS Multi SGD CPF net-zero cluster (`cpf_net_zero`)**
- **Account scope:** TWH DBS Multi SGD
- **Purpose:** Remove CPF-related edits that represent internal fund allocations within the account.
- **Procedure:**
  1. Select edits whose `note` field contains any of: `"Flintex CPF"`, `"RSK CPF"`, `"CPF OA"`, `"CPF SA"`, `"CPF MA"`.
  2. Compute the sum of `amount` over the selected subset.
  3. If `abs(sum_amount) <= amount_tolerance` — default 0.01 — drop the entire subset.
- **Gap invariant:** preserved because the subset's `edit_amount` values sum to zero.
- **Config source:** `txn_heuristics.json` / `account_heuristics` / `TWH DBS Multi SGD`
- **Example:** Three edits: `Flintex CPF -5000`, `CPF OA +2500`, `CPF SA +2500`. These net to zero and represent internal CPF structure, not true ledger–statement differences.

**2. UOB One SGD cashback split (`uob_cashback_split`)**
- **Account scope:** TWH UOB One SGD
- **Purpose:** Remove cashback edits where one ledger cashback entry is split across multiple statement rebate lines.
- **Procedure:**
  1. Identify ledger `remove` edits where `amount > 0` and `note` contains `"UOB One cashback"`.
  2. Within the same `(year, month)`, identify statement `add` edits where `amount > 0` and `note` contains `"REBATE"` or `"CASH REBATE"`.
  3. Check if the sum of statement `amount` values equals the ledger cashback `amount` within `amount_tolerance`.
  4. Compute the cluster's `edit_amount` sum — zero by construction.
  5. If the cluster is balanced, drop all edits in the cluster.
- **Gap invariant:** preserved because the cluster's `edit_amount` values sum to zero.
- **Config source:** `txn_heuristics.json` / `account_heuristics` / `TWH UOB One SGD`
- **Example — UOB One Nov-2025:**
  - Ledger: `UOB One cashback 2025 11 NOV` +119.95 → `remove` edit -119.95
  - Statement: `ONE CARD ADDITIONAL REBATE` +19.95 → `add` edit +19.95
  - Statement: `UOB ONE CASH REBATE BILL REDEMPTION` +100.00 → `add` edit +100.00
  - Cluster sum: 19.95 + 100.00 = 119.95, matching the ledger cashback total. Drop all three edits.

#### Semantic matching layer

For a given scope of period and account, after applying heuristics for known recurring transaction patterns, apply a semantic matching layer to identify add-remove update pairs. The matching occurs between pairs of `add` and `remove` edits on the statement ledger and the action is to reclassify the `remove` edit as an `update` with the `edit_amount` set to the `amount` value of the paired `add` edit.

**user review, manual records update and approval**
As with the edits, prior to implementing actions, user must review the proposed pairs and corresponding edits.  The semantic pairing is presented to user for review and approval. user may manually update the edit and paring records, so the workflow procedure needs to account for a step for user to CRUD the edit and pair records.

**statement-ledger pairing:**
from the set of edits `add` and `remove` to the account ledger, identify add-remove pairs that meet the following conditions

_pairing condition_

1. `add.date` is within `date_tolerance_days` of `remove.date`
2. semantic, or heuristic match of `add.note` and `remove.note` — for example, a description containing "UOB One cashback" in the ledger and "REBATE" in the statement may indicate a semantic match even if the amounts differ due to timing or partial capture. The `add` note will come from the statement and will include the original statement description, which will usually be longer and more descriptive with many unnecessary information such as transaction id, so the semantic match will apply only to a substring of the full description.

_actions_

1. reclassify the `remove` edit as an `update` with the `edit_amount` set to the `amount` value of the paired `add` edit. keep all other fields unchanged.
2. remove the `add` edit.

#### Transfer-Expense pairing
Due to the double-entry accounting and zero-sum behavior of the cost center `TWH - Personal`, each transfer into or out of the `TWH - Personal` account should have a corresponding set of expense transaction(s) in the ledger for the same period which sum to -1* the transfer amount, and close to and usually on the same transfer date.  any `add`, `remove` or `update` without a corresponding CRUD action to the expenses would break this relationship and voilate the zero sum condition for the cost center account. As a default fallback, this step is manual and it is up to the user to manually repair and apply these updates to the expense transactions in HomeBudget manually to restore the zero-sum condition.

The aim of the transfer-expense pairing step, is to reduce some portion of this manual step by identifying potential pairs of transfer and expense transactions, and staging, still pending user review and approval, the corresponding edits to apply to the HB expenses.  To avoid the complexity of many-to-one pairing algorithm, unless a multi-transaction heuristic is setup, only one-to-one pairs are in scope for the generic semantic match.

The transfer-expense pairing must occur after the statement-ledger pairing step has been approved, so that the `edit_type` and `edit_amount` for the transfer is fixed.

_pairing condition_

1. `transfer.date` is within `date_tolerance_days` of `expense.date`
2. `transfer.amount` == -1 * `expense.amount`

tie-breakers for multiple candidates base on 1. semantic match of `transfer.note` and `expense.note`, then 2. by date proximity.

_actions_

The action will depend on the `edit_type`:

**remove**

delete the expense transaction

**add**

1. add a new expense with date, note set to values from the transfer record
2. set the amount=-1* transfer amount
3. unless a heuristic exists on how to fill them from clues from the transfer record, leave the expense category and subcategory blank. they will not be known and user will have to manually assign them.

**update**

1. update the expense `amount`=-1* the transfer `amount`

#### Method Parameters

Method behavior is controlled by account-specific parameters stored in `txn_heuristics.json`:

| id | parameter             | usage         | config_key                                      | values          |
| -- | --------------------- | ------------- | ----------------------------------------------- | --------------- |
| 01 | `date_tolerance_days` | date window   | `matching_config.accounts.*.date_tolerance_days`| default 3; uob 3|
| 02 | `amount_tolerance`    | amount window | `matching_config.default.amount_tolerance`      | default 0.01    |

**Parameter discovery:**
1. Check `txn_heuristics.json` / `matching_config.accounts[account]` for account-specific override.
2. If not present, use `matching_config.default`.
3. Parameters are discovered at runtime before invoking the forward pass.

**Config source:** `reference/hb-reconcile/account_settings/txn_heuristics.json`

**Requirement ref:** reconciliation-engine.md § Account-group procedures / Bank statement-process accounts § Reconciliation parameters

#### Transaction-level Method Invocation Contract

**Required inputs:**
- `account` — string: account identifier, e.g., `"TWH DBS Multi SGD"`
- `year` — int: calendar year
- `month` — int: calendar month, 1–12
- `hb_gl` — DataFrame: HomeBudget GL with columns `[account, date, year, month, txn_type, amount, category, subcategory, payee, notes]`
- `stm_gl` — DataFrame: statement GL with columns `[account, date, year, month, amount, description]`
- `balances` — DataFrame: balance dataset with columns `[account, date, year, month, balance]` — must contain prior month and current month rows
- `txn_heuristics_config` — dict: loaded configuration from `txn_heuristics.json`

**Pre-conditions:**
1. `hb_gl` and `stm_gl` must be non-empty for the account and period.
2. `balances` must contain both the prior month row for opening balance and current month row for statement ending balance cross-check.
3. Account must be present in at least one heuristics list — general or account-specific — if account-specific heuristics are required.

**Outputs:**
1. `edits` — DataFrame: table with columns `[source, date, amount, edit, edit_amount, note, ledger_idx, stmt_idx]`
2. `gap` — decimal: final reconcile gap, should be 0.00 or within rounding tolerance
3. `matches` — list: `(ledger_idx, stmt_idx)` tuples from forward pass
4. `metadata` — dict: invocation metadata including opening_balance, statement_end_balance, ledger_end_balance, forward_edits_count, backward_edits_count, heuristics_applied

**Post-condition:**
- `gap == 0.00`, within currency rounding tolerance 0.01
- `forward_edits == backward_edits` after heuristics application — a mandatory correctness assertion

**Failure modes:**
- Missing opening balance → raise `MissingOpeningBalanceError`
- Statement ending balance mismatch > tolerance → log warning, allow user decision to proceed or investigate
- Forward and backward edits differ after heuristics → raise `HeuristicsConsistencyError`; this is a mandatory correctness check
- Unresolved ambiguous matches → edits remain; tolerance evaluation determines acceptance

**Requirement ref:** reconciliation-engine.md § Shared reconciliation patterns / Shared workflow phases

### Balance-level Method Class

The balance-level method compares derived ending balances between primary and comparison sources and computes a residual gap. It is used by accounts without detailed transaction matching.

#### Generic Balance Equation

The reconcile gap for a balance-level account is:

```
Residual Gap = Primary Balance - Comparison Balance - Σ Staged Adjustments
```

**Definitions:**

- **Primary Balance:** source-of-truth balance for the account group. For example:
  - Cash: HomeBudget ledger ending balance — sum of all `hb_gl_txn.amount` for the period
  - CPF: expected closing balance computed from roll-forward formula
  - Manual-input: pre-adjustment sum of `hb_gl_txn.amount`
  - IBKR: not applicable; use IBKR integration derivation rules instead

- **Comparison Balance:** secondary or user-observed balance for the account group. For example:
  - Cash: user-entered physical cash count
  - CPF: user-entered closing balance from GS UI
  - Manual-input: user-entered account balance from GS UI
  - HomeBudget-native: not applicable; user review and confirmation is the comparison

- **Σ Staged Adjustments:** sum of known intermediate adjustments, transfers, or expenses. For example:
  - Cash: sum of aggregated wallet cash expenses from `cash_staging` for the period
  - CPF: contributions and interest from roll-forward formula
  - Manual-input: zero — no staged adjustments
  - HomeBudget-native: zero — all transactions already in ledger

**Account-specific equation examples:**

*Cash reconciliation:*
```
Residual Gap = HB Current Balance - Actual Physical Cash - Σ Staged Wallet Expenses
```

*CPF reconciliation:*
```
Residual Gap = Expected Closing Balance - User-Entered Closing Balance
where Expected Closing Balance = Opening Balance + Contributions + Interest
```

*Manual-input reconciliation:*
```
Residual Gap = User Balance - Pre-Adjustment Balance
where Pre-Adjustment Balance = sum(hb_gl_txn.amount) for account and period
```

#### Variance Class Outcomes and Tolerance Evaluation

After computing the residual gap, the method classifies the variance into one of three classes:

| id | class             | condition                                | action                | threshold       |
| -- | ----------------- | ---------------------------------------- | --------------------- | --------------- |
| 01 | zero variance     | `abs(residual_gap) <= amount_tolerance`  | close; no adjustment  | account-specific|
| 02 | within tolerance  | `amount_tolerance < abs(gap) <= tol`     | prep adj; confirm post| account-specific|
| 03 | exceeds tolerance | `abs(residual_gap) > tolerance_threshold`| block; require approve| account-specific|

**Tolerance thresholds by account group, from reconciliation-engine.md:**

| id | account_group      | tolerance      | notes                  |
| -- | ------------------ | -------------- | ---------------------- |
| 01 | cash twh sgd       | +/- sgd 20.00  | cash alert threshold   |
| 02 | homebudget-native  | n/a            | user confirmation      |
| 03 | cpf                | rounding       | interest/contrib roll  |
| 04 | manual-input accts | 0.00           | exact match only       |

#### Variance Propagation and Adjustment Preparation

**Within-tolerance variance:**
1. Compute `adjustment_amount = abs(residual_gap)`
2. Auto-prepare adjustment record with fields:
   - `adjustment_id`: generated unique identifier
   - `adjustment_amount`: `abs(residual_gap)` in account currency
   - `residual_gap`: original signed gap value
   - `variance_percentage`: `(residual_gap / primary_balance) * 100`
   - `status`: `"pending_approval"` — awaiting user confirmation
   - `rule_reference`: e.g., `"cash_gap_tolerance"`, `"manual_input_balance_reconciliation"`
   - `session_id`: reconciliation session identifier
   - `created_timestamp`: ISO 8601 timestamp
   - `transaction_date`: last day of period, end of day — 23:59:59
   - `description`: account-group-specific text, e.g., `"Cash reconcile adjustment 2026-02 (pending approval)"`
   - `category`: `"Balancing:Unknown"` or account-group-specific category
3. User is notified; approval is not required for within-tolerance variance.
4. Adjustment is posted on user confirmation of reconciliation completion.

**Exceeds-tolerance variance:**
1. Create adjustment record with same fields as within-tolerance case.
2. Set `status`: `"pending_approval"` with escalation flag.
3. Flag account variance and present adjustment for user review.
4. User must explicitly approve before posting; auto-approval is not allowed.
5. Record user approval timestamp and optional user comment.

**Zero variance:**
1. No adjustment transaction is created.
2. Reconciliation is closed with verification checkpoint.

**Requirement ref:** reconciliation-engine.md § Shared reconciliation patterns / Variance interpretation and adjustment behavior; § Account-group procedures / Cash reconciliation

#### Balance-level Method Invocation Contract

**Required inputs:**
- `account_group` — string: cash, homebudget_native, cpf, or manual_input
- `account` — string: account identifier
- `year` — int: calendar year
- `month` — int: calendar month
- `primary_balance` — Decimal: source-of-truth balance
- `comparison_balance` — Decimal or None: secondary balance; None for HomeBudget-native
- `staged_adjustments` — Decimal: sum of known intermediate adjustments; default 0.00
- `tolerance_config` — dict: tolerance thresholds from policy configuration

**Pre-conditions:**
1. `primary_balance` must be a valid Decimal value.
2. `comparison_balance` must be a valid Decimal or None for confirmation-based accounts.
3. `account_group` must match one of the supported account-group procedure types.

**Outputs:**
1. `residual_gap` — Decimal: computed gap
2. `variance_class` — string: `"zero"`, `"within_tolerance"`, or `"exceeds_tolerance"`
3. `adjustment_record` — dict or None: adjustment transaction structure if variance is non-zero, else None
4. `metadata` — dict: invocation metadata including primary_balance, comparison_balance, tolerance_threshold, variance_percentage

**Failure modes:**
- Missing required input → raise `MissingBalanceInputError`
- Unsupported account_group → raise `UnsupportedAccountGroupError`
- User confirmation required but not provided → return adjustment in `pending_approval` state

### Cross-cutting Concerns

#### Ledger Consistency Invariants

All reconciliation methods depend on GL schema consistency:

1. **Ledger–statement opening balance consistency:** The opening balance for both ledger and statement slices must be derived from the same source — the prior period `balances` row.
2. **Ledger balance equation:** `ledger_end = opening_balance + sum(ledger.amount)` must hold exactly.
3. **Statement balance equation:** `statement_end = opening_balance + sum(statement.amount)` must hold exactly.
4. **Edits gap invariant:** `gap = ledger_end + sum(edit_amount) - statement_end` must equal 0.00 after valid solution.
5. **Heuristics invariant:** `sum(edit_amount over modified subset) == 0.00` for every heuristic application.

**Validation procedure:**
- Check opening balance availability before slice construction.
- Compute and verify ledger and statement balance equations after slice construction.
- Cross-check statement ending balance against `balances` dataset; log warnings on mismatch.
- Verify final gap equals 0.00 after edits application — a post-condition assertion.
- Verify forward and backward edit sets are identical after heuristics — a correctness assertion.

#### Heuristic Parameter Discovery and Invocation

Heuristics are discovered and configured at invocation time from `txn_heuristics.json`:

1. **Config file location:** `reference/hb-reconcile/account_settings/txn_heuristics.json`
2. **Config discovery sequence:**
   - Load the JSON file into memory at agent initialization.
   - For each account, check `matching_config.accounts[account]` for account-specific overrides.
   - If no override, use `matching_config.default`.
   - Collect all `general_heuristics` from the config.
   - Collect all `account_heuristics[account]` entries.
3. **Invocation:** Apply heuristics in the order defined in the config.
4. **Determinism requirement:** Heuristic order and parameter values must be deterministic across sessions for idempotency.

**Config example structure:**
```json
{
  "matching_config": {
    "default": {
      "date_tolerance_days": 3,
      "amount_tolerance": 0.01
    },
    "accounts": {
      "TWH UOB One SGD": {
        "date_tolerance_days": 5
      }
    }
  },
  "general_heuristics": [...],
  "account_heuristics": {...}
}
```

#### Reconciliation Idempotency Requirement

Reconciliation is idempotent per session per account: repeated execution with identical inputs — same GL rows, same balances, same period — must produce identical outputs.

**Idempotency requirements:**
1. Match pairs must be deterministic: same forward-pass algorithm, same match test, same parameter values.
2. Edits construction must be deterministic: same row ordering, same index assignment.
3. Heuristics application must be deterministic: same heuristic order, same parameter values, same subset selection.
4. Outputs must be byte-identical: same edits table, same gap value, same metadata.

**Implementation constraints:**
- Use deterministic sorting by date, then by original row index.
- Use exact Decimal arithmetic for all gap and amount calculations; never use float.
- Store heuristic parameters in the invocation metadata for audit trail.
- Fail closed on ambiguous match or configuration discovery failures.

**Requirement ref:** reconciliation-engine.md § End-to-End Delivery Responsibilities § Rerun completeness

#### Account-Group Method Dispatch

Method class selection is determined by account group classification. The classification is owned by the reconciliation engine and must occur before method invocation.

**Account-group classification:**
1. **Bank statement-process accounts:** transactions available from downloaded statement GL
   - Accounts: TWH DBS Multi SGD, TWH CITI USD, TWH UOB One SGD, TWH Visa USD
   - Method: Transaction-level
2. **HomeBudget-native accounts:** no external statement source, user review is comparison
   - Example: 30 Hashemis CC
   - Method: Balance-level
3. **Cash:** user-provided physical cash count
   - Accounts: Cash TWH SGD
   - Method: Balance-level
4. **IBKR:** deterministic statement derivation rules — routed to IBKR integration agent
   - Accounts: TWH IB USD, IB Position USD, IB IRA USD
   - Method: IBKR accounting model — not reconciliation engine
5. **CPF:** user-provided closing balance and contributions
   - Accounts: CPF OA, CPF SA, CPF MA
   - Method: Balance-level
6. **Manual-input balance-only:** user-provided account balance
   - Examples: Amazon wallet, digital wallets
   - Method: Balance-level

**Dispatch contract:**
- Reconciliation engine owns method selection logic.
- Account-group classifier is called before method invocation.
- Callers do not hard-code method dispatch; they request reconciliation for an account and receive the result.

### Procedure Table

Each account group follows either the transaction-level or balance-level reconciliation method, with defined tolerance and adjustment behavior:

| id | account_group     | method            | tolerance        | posting_target      |
| -- | ----------------- | ----------------- | ---------------- | ------------------- |
| 01 | bank (dbs/citi/uob/visa) | transaction-level | 0.00 (+/-0.01)   | close_book + hb gl  |
| 02 | homebudget-native | balance-level     | user confirmation| close_book only     |
| 03 | cash (twh cash sgd)| balance-level    | +/- sgd 20       | close_book + hb gl  |
| 04 | ibkr (ib usd/position)| accounting model| validation gates | close_book + hb gl  |
| 05 | cpf (oa/sa/ma)    | balance-level     | rounding         | close_book only     |
| 06 | manual-input (wallets)| balance-level  | 0.00 exact       | close_book + hb gl  |

**Details by account group:**

**Bank statement-process accounts:** Transaction-level matching against `hb_gl_txn` using forward/backward passes with heuristics — DBS CPF net-zero, UOB cashback split, and general net-zero pairs. Exact match required: date ±3 days, amount ±0.01. If unmatched items exist after edits, create `Balancing:Unmatched` adjustment per item.

**HomeBudget-native accounts:** User reviews `hb_gl_txn` ledger state and confirms it is final. User may mark corrections to be updated in HB directly. No numeric tolerance; user confirmation is the comparison basis.

**Cash reconciliation:** Balance equation: HB current balance - physical cash count - staged wallet expenses. ±SGD 20 tolerance. Within-tolerance gaps auto-prepare adjustment. Exceeds-tolerance gaps require user approval.

**IBKR accounts:** Not variance-based reconciliation. Uses deterministic derivation — see [ibkr-integration.md](ibkr-integration.md). Close-gate checks validate balance equation and position consistency. If checks pass, txns posted; if fail, account blocked for investigation.

**CPF accounts:** Roll-forward balance validation. User confirms expected closing balance matches HB ledger. Rounding tolerance for interest/contribution calculations. Exceeds-tolerance gaps flagged for user balance correction.

**Manual-input accounts:** Zero tolerance; exact match required between user-entered balance and HB ledger. Any delta requires explicit user approval before adjustment posting.

### Variance Interpretation Matrix

Variance outcomes by class and account group:

**Interpretation:**

- **Zero variance:** Gap equals zero, within rounding tolerance. No adjustment needed. Reconciliation passes directly to closure.
- **Within-tolerance variance:** Gap exceeds zero but is within account-group tolerance threshold. Auto-prepare adjustment when applicable per account group. User notified. Adjustment posted on user confirmation.
- **Exceeds-tolerance variance:** Gap exceeds tolerance threshold. Blocks reconciliation closure. Requires explicit user approval — investigation for IBKR accounts, balance correction for CPF, or user update for HB-native accounts. User approval recorded with timestamp and optional comment.

### Tolerance Rules by Account Group

This section details tolerance thresholds, variance evaluation, and adjustment behavior for each account group.

#### Bank statement-process accounts

**Scope:** TWH DBS Multi SGD, TWH CITI USD, TWH UOB One SGD, TWH Visa USD
**Method:** Transaction-level matching with heuristics.
**Tolerance:**
- Exact match required on amount: ±0.01 currency precision, to the cent.
- Exact match required on date: ±3 days by default, configurable per account; ±5 days for UOB One SGD when posting delays are observed.
- Account-specific heuristics enabled per `reference/hb-reconcile/account_settings/txn_heuristics.json`:
  - DBS Multi SGD: CPF net-zero cluster matching on keywords: Flintex CPF, RSK CPF, CPF OA/SA/MA.
  - UOB One SGD: cashback split matching across ledger and statement rebate lines.
  - General: net-zero pairs with opposite amounts within date tolerance; same-amount zero-sum clusters.

**Variance evaluation:**
- Forward and backwards matching passes applied per reconciliation-engine spec.
- Unmatched ledger txns generate `remove` edits; unmatched statement txns generate `add` edits.
- Heuristics reduce edit set; final gap computed as: `ledger_end_balance + Σ(edit_amount) - statement_end_balance`.
- Valid solution: gap = 0.00.

**Adjustment outcome:**
- **Zero gap:** reconciliation passes; no adjustment.
- **Exceeds-tolerance gap:** create one adjustment txn per unmatched item cluster with category `Balancing:Unmatched`, amount equal to residual edit, and reference to source statement line and ledger txn indices.
- **Post target:** close_book as primary; HB GL via wrapper as validation-only — matched source rows validated as existing in HB; unmatched source rows create new HB entries via wrapper.

**Example:** DBS Multi SGD statement shows txn on Feb 10, amount SGD 150.00, but HB ledger shows the same txn on Feb 11 — a 1-day delay. Within 3-day tolerance; matched as equivalent.

#### HomeBudget-native accounts

**Scope:** Accounts with no external statement source; managed entirely within HomeBudget — for example, 30 Hashemis CC or other closed-loop card systems with no downloadable statement.
**Method:** Balance-level with user confirmation as comparison basis.
**Tolerance:**
- User confirmation is the tolerance mechanism.
- System presents `hb_gl_txn` ledger state to user; user reviews and confirms all txns are correct or marks txns for correction.

**Variance evaluation:**
- No numeric variance computation.
- User confirmation indicates acceptance of ledger state.
- If user marks corrections: user updates categories or amounts in HomeBudget directly; system re-reads updated state.

**Adjustment outcome:**
- **User confirms ledger:** reconciliation passes; no adjustment.
- **User marks corrections:** user makes changes in HB; system re-reads; reconciliation proceeds with updated state.
- **No HB write-back:** target is close_book only; no adjustment posted via wrapper.

**Approval authority:** User confirmation acts as approval. No additional approval gate required.

#### Cash reconciliation

**Scope:** TWH Cash SGD — physical wallet cash.
**Method:** Balance-level matching with cash aggregation.
**Tolerance:**
- ±SGD 20 — the alert threshold per reconciliation-engine requirements.
- Residual Gap = HB Current Balance - Actual Physical Cash - Σ Staged Wallet Expenses.

**Variance evaluation:**
- Read staged wallet cash aggregates from `cash_staging` schema for period.
- Read `hb_gl_txn` records for account and period; compute HB current balance.
- Retrieve user-entered close balance — observed physical cash count — from GS session UI.
- Compute residual gap.
- If gap within ±SGD 20: within-tolerance condition.
- If gap exceeds ±SGD 20: exceeds-tolerance condition.

**Adjustment outcome:**
- **Within tolerance — gap ≤ ±SGD 20:** system auto-prepares adjustment txn with amount equal to negative gap and category `Balancing:Unknown`; user notified; adjustment posted on user confirmation of reconciliation completion.
- **Exceeds tolerance — gap > ±SGD 20:** system prepares adjustment and flags for user review; user must approve, modify, or investigate variance before adjustment can be posted; user approval is recorded with timestamp and optional comment.
- **Post target:** close_book as primary; HB GL via wrapper — new entries created for previously unstaged cash txns.

**Example:** HB ledger balance = SGD 500. Physical cash count = SGD 478. Staged wallet expenses = SGD 10. Gap = 500 - 478 - 10 = SGD 12. Within ±SGD 20 tolerance; auto-prepare and post SGD -12 adjustment.

#### IBKR accounts

**Scope:** TWH IB USD cash, IB Position USD holdings, IB IRA USD.
**Method:** Accounting model derivation — see [ibkr-integration.md](ibkr-integration.md); not variance-based reconciliation.
**Tolerance:**
- No numeric tolerance applied to variance-based reconciliation.
- Validation tolerance applied per account close-gate check in ibkr-integration.md, covering balance-equation closure, NAV roll-down verification, and position quantity consistency.

**Variance evaluation:**
- IBKR statement activity and NAV reconciled via deterministic derivation logic in ibkr-integration.md.
- Close-gate checks validated per ibkr-integration.md requirements.
- Reconciliation-engine does not create variance-based adjustments for IBKR.

**Adjustment outcome:**
- **Close-gate checks pass:** derived txns posted directly to close_book and HB GL via wrapper; reconciliation passes.
- **Close-gate check fails:** account reconcile blocked; account flagged for investigation; no adjustment posted; user must resolve the underlying cause — for example, missing dividend or incorrect statement balance — before close can proceed.

**Approval authority:** Close-gate validation failures require user investigation and correction. No user approval for derived txns; txns are deterministic outputs of statement activity.

#### CPF accounts

**Scope:** CPF OA, CPF SA, CPF MA, CPF RA sub-accounts.
**Method:** Balance-level roll-forward validation with rounding tolerance.
**Tolerance:**
- Rounding tolerance: 0.01, account-group specific per reconciliation-engine requirements.
- Residual Gap = User-Entered Roll-Forward Balance - Computed HB Balance.

**Variance evaluation:**
- System computes roll-forward result per CPF reconciliation rules, covering contribution, interest, and withdrawal tracking.
- User confirms roll-forward result in GS session UI.
- Read `hb_gl_txn` records for account period; compute HB balance before adjustments.
- Retrieve user-entered roll-forward balance from GS UI.
- Compute residual gap.
- If gap within ±0.01 rounding: within-tolerance condition.
- If gap exceeds ±0.01: exceeds-tolerance condition.

**Adjustment outcome:**
- **Within tolerance — gap ≤ ±0.01:** system auto-prepares adjustment with category `Balancing:Rounding` if user confirmation is obtained; adjustment posted on user confirmation.
- **Exceeds tolerance — gap > ±0.01:** system prepares adjustment and flags for user review; user must approve or investigate before posting.
- **Post target:** close_book as primary; HB GL via wrapper — verification entry posted if user-entered balance differs from computed balance.

#### Manual-input accounts

**Scope:** Wallet, balance-only, and manually-reconciled accounts where no statement source is available.
**Method:** Balance-level with user-entered balance as source of truth.
**Tolerance:**
- Zero tolerance: exact match required between user-entered balance and HB ledger.
- Residual Gap = User-Entered Balance - HB GL Balance.

**Variance evaluation:**
- Read `hb_gl_txn` records for account and period; compute HB current balance.
- Retrieve user-entered closing balance from GS session UI.
- Compute residual gap.
- If gap = 0: zero variance.
- If gap ≠ 0: variance flagged for user review; no auto-approve is allowed and explicit user approval is always required.

**Adjustment outcome:**
- **Zero gap:** reconciliation passes; no adjustment.
- **Non-zero gap:** system creates adjustment with amount equal to absolute gap and category assigned per wallet account type; user must approve before posting.
- **Post target:** close_book as primary; HB GL via wrapper — new entry created to reconcile user-entered balance with HB state.

## Adjustment and Audit Contracts

This section specifies the adjustment transaction contract, bill conflict policy, and reconciliation session record requirements for persistence, audit, and traceability.

### Adjustment Transaction Contract

**Required Fields and Data Types:**

| id | field                     | type            | constraints                   | usage                    |
| -- | ------------------------- | --------------- | ----------------------------- | ------------------------ |
| 01 | `adjustment_id`           | uuid/hash       | pk; generated                 | audit + lineage key      |
| 02 | `session_id`              | uuid            | fk; non-null                  | link to session          |
| 03 | `account_id`              | string          | valid account; non-null       | account scope            |
| 04 | `period_key`              | string yyyy-mm  | non-null                      | period scope             |
| 05 | `adjustment_amount`       | dec(28,2)       | +/- allowed                   | post variance            |
| 06 | `residual_gap`            | dec(28,2)       | abs precision                 | source gap value         |
| 07 | `variance_percentage`     | dec(6,4)        | informational                 | user review context      |
| 08 | `status`                  | enum            | generated/pending/approved/posted | lifecycle state      |
| 09 | `rule_reference`          | string          | valid policy ref              | tolerance trigger        |
| 10 | `method_class`            | enum            | txn_level or balance_level    | method used              |
| 11 | `transaction_date`        | iso date        | inside period                 | posting date             |
| 12 | `created_timestamp`       | iso datetime    | immutable at create           | creation audit anchor    |
| 13 | `user_approval_timestamp` | iso datetime    | null until approve            | approval audit anchor    |
| 14 | `user_comment`            | string(4000)    | optional                      | approval notes           |
| 15 | `description`             | string(500)     | machine-readable              | ledger posting text      |
| 16 | `category_code`           | string          | mapped `gl_code`; non-null    | gl assignment            |
| 17 | `source_reference`        | string          | optional                      | source lineage ref       |
| 18 | `auto_approve_flag`       | boolean         | default false                 | bypass marker            |

**Field Validation Rules:**

- `adjustment_amount` must be non-zero or status must remain `generated` and adjustment must not post.
- `residual_gap` absolute value must be ≥ `adjustment_amount` when both populated.
- `period_key` must match `session_id` period; cross-period adjustments rejected.
- `account_id` must be valid in account master.
- `status` transitions follow strict lifecycle: `generated` → `pending_approval` when tolerance is exceeded → `approved` → `posted`. No reverse transitions allowed.
- `category_code` must exist in mapping schema at creation time.
- `rule_reference` must reference a defined tolerance rule or system policy.
- `transaction_date` must fall within `period_key` calendar month.
- `user_approval_timestamp` must be null if status is `generated`; non-null if status is `approved` or `posted`.

**Posting Targets:**

- **close_book schema — required:** All adjustments post to `close_book` schema at account and period scope. Posting is idempotent: same adjustment retried produces one record.
- **HomeBudget GL — conditional:** Per account group:
  - Bank accounts: new GL entry with source reference to statement.
  - Cash: new GL entry with category `Balancing:Unknown`.
  - Investments: valuation adjustment entry per investment account type.
  - Wallets: new GL entry per wallet account type.
  - CPF and manual-input: verification entry if user-entered values adjusted; otherwise no HB posting.

**Status Lifecycle and Auto-Approve Conditions:**

- **Auto-approve:** Variance is zero, or variance within tolerance and account group allows auto-approve — bank zero-gap, cash ≤±SGD 20, and CPF ≤±0.01.
- **User-approval required:** Variance exceeds tolerance threshold; user must explicitly approve before posting.

**User-Approval Conditions by Account Group:**

| id | account_group | tolerance      | auto_approve    | user_approval_required |
| -- | ------------- | -------------- | --------------- | ---------------------- |
| 01 | bank accounts | 0.00 exact     | yes (zero gap)  | yes (any unmatched)    |
| 02 | cash          | +/- sgd 20     | yes (<=20)      | yes (>20)              |
| 03 | ibkr          | per policy     | no              | yes (mismatch)         |
| 04 | cpf           | +/- 0.01 round | yes (<=0.01)    | yes (>0.01)            |
| 05 | wallets       | 0.00 exact     | yes (zero gap)  | yes (any variance)     |
| 06 | manual-input  | 0.00 exact     | no              | yes (any variance)     |

### Bill Accrual Conflict Policy

**Conflict Classification Matrix:**

Four conflict classes govern bill accrual treatment during reconciliation:

| id | class | definition                    | engine_behavior                | acceptance_rule          |
| -- | ----- | ----------------------------- | ------------------------------ | ------------------------ |
| 01 | a     | billed = settled; same period | standard reconcile             | direct link; no override |
| 02 | b     | near eom (+/-3 days)          | shift txn date to bill period  | auto-approved timing     |
| 03 | c     | cross-period timing           | expense + bridge transfers     | override may be needed   |
| 04 | d     | partial payment across periods| expense + multi transfers      | override may be needed   |

**Acceptance Rules Detail:**

- **Blocking condition:** Any remaining difference between total billed amount and total settlement amount after all transfers is a blocking reconciliation finding unless explicitly approved with written rationale.
- **Shared billing bridge account:**
  - One account per session, e.g., `shared_billing_bridge_<period_key>`.
  - Transfers in = full bill amount on bill date; transfers out = each payment amount on settlement date.
  - Net position = transfers in - transfers out = unpaid remainder at period close.
  - At period close, net position is reconciliation checkpoint.
- **Override policy:**
  - Class A: no override needed.
  - Class B: auto-approved; no override decision.
  - Classes C and D: user may override with written rationale, which is required; override is audited.

**Bill Conflict Record Fields:**

| id | field                      | type             | content                    |
| -- | -------------------------- | ---------------- | -------------------------- |
| 01 | `conflict_id`              | uuid             | unique id                  |
| 02 | `session_id`               | uuid             | session context            |
| 03 | `bill_id`                  | string           | bill domain ref            |
| 04 | `conflict_class`           | enum             | a, b, c, or d             |
| 05 | `bill_statement_reference` | string           | bill source id             |
| 06 | `bank_statement_reference` | string           | bank source id             |
| 07 | `bill_amount`              | dec(28,2)        | full billed amount         |
| 08 | `settlement_amount`        | dec(28,2)        | total settled amount       |
| 09 | `pseudo_account_id`        | string           | bridge account id          |
| 10 | `pseudo_account_balance`   | dec(28,2)        | close net position         |
| 11 | `policy_applied`           | string           | policy code                |
| 12 | `override_rationale`       | string(4000)     | required for override      |
| 13 | `created_timestamp`        | iso datetime utc | audit anchor               |

### Reconciliation Session Record

**Session Record Fields:**

| id | field                    | type             | constraints               | purpose               |
| -- | ------------------------ | ---------------- | ------------------------- | --------------------- |
| 01 | `session_id`             | uuid             | pk; generated at start    | unique session id     |
| 02 | `period_key`             | string yyyy-mm   | non-null                  | period scope          |
| 03 | `account_id`             | string           | valid account; non-null   | account scope         |
| 04 | `account_group`          | string           | enum bank/cash/ibkr/cpf...| dispatch context      |
| 05 | `method_class`           | enum             | txn/balance/account model | algo class            |
| 06 | `session_status`         | enum             | pending..failed           | closure state         |
| 07 | `variance_amount`        | dec(28,2)        | null if zero              | pre-adjust gap        |
| 08 | `variance_tolerance`     | dec(28,2)        | group-specific            | threshold reference   |
| 09 | `exceeds_tolerance_flag` | boolean          | true if variance > tol    | approval gate         |
| 10 | `user_approval_decision` | enum             | pending/approve/etc       | user action           |
| 11 | `user_approval_timestamp`| iso datetime utc | null until decision       | approval audit        |
| 12 | `override_rationale`     | string(4000)     | required if overridden    | reason record         |
| 13 | `adjustment_id`          | uuid             | fk adjustment             | link to adjustment    |

**Lineage Requirements:**

Each session must retain source-of-truth references for traceability:

| id | lineage_anchor              | content                    | examples                      |
| -- | --------------------------- | -------------------------- | ----------------------------- |
| 01 | `statement_source_reference`| comparison source id       | statements row, ibkr id, bill |
| 02 | `statement_fetch_date`      | source fetch date          | iso date                      |
| 03 | `statement_source_hash`     | deterministic source hash  | sha256 of source payload      |
| 04 | `hb_sync_timestamp`         | hb wrapper sync time       | iso datetime                  |
| 05 | `hb_sync_version`           | hb wrapper version         | reproducibility marker        |
| 06 | `matching_algorithm_version`| reconcile method version   | txn_level_v2.1...             |
| 07 | `reconciliation_outcome`    | final result               | matched/adjusted/failed       |

**Audit Trail Checkpoints:**

| id | checkpoint           | timestamp_field                  | condition          | purpose               |
| -- | -------------------- | -------------------------------- | ------------------ | --------------------- |
| 01 | session open         | `session_created_timestamp`      | always             | start account run     |
| 02 | validation pass      | `validation_checkpoint_timestamp`| if successful      | source validated      |
| 03 | matching complete    | `matching_complete_timestamp`    | always             | variance computed     |
| 04 | variance evaluated   | `variance_evaluation_timestamp`  | always             | tolerance compared    |
| 05 | adjustment generated | `adjustment_created_timestamp`   | if variance != 0   | adjustment created    |
| 06 | user approval        | `user_approval_timestamp`        | if exceeds tol     | explicit decision     |
| 07 | adjustment posted    | `adjustment_posted_timestamp`    | if adjustment exists| posted to targets    |
| 08 | session closed       | `session_closed_timestamp`       | always             | end account run       |

**Closure Criteria — all must be satisfied:**

- All transactions in scope have match outcome: matched, in edits list, or marked non-matching with explanation.
- No unexplained blocking variance at close time; variance is zero, within tolerance, or user-approved.
- All account-group specific gates pass — for example, category completeness for bank accounts and HB write-back success.
- If variance within tolerance, automatic adjustment generated and staged.
- If variance exceeds tolerance, user approval recorded with timestamp and optional comment.
- Adjustment, if generated, posted to close_book; HB write-back attempted for applicable account groups.
- Reconciliation report generated with period, account, variance, tolerance status, and checkpoint outcomes.
- Session status transitioned to `complete`, `overridden`, or `failed`.

**Retention and Queryability:**

- Session records retained indefinitely in SQLite for audit trail.
- Queryable by `session_id` for full session audit, by `period_key` + `account_id` for per-account close audit, by `session_status` for workflow state, and by `variance_amount` for variance analysis.
- Post-close audit queries executable without external files or archives.

### Close_book Schema Integration

**Adjustment Posting:**

Adjustments persist to `close_book` schema using deterministic, idempotent upsert:

| id | operation               | idempotency_rule                         |
| -- | ----------------------- | ---------------------------------------- |
| 01 | create adjustment       | same variance -> same `adjustment_id`    |
| 02 | user approves           | status -> `approved`; timestamp updated  |
| 03 | post to close_book      | upsert by `adjustment_id`; no duplicates |
| 04 | statement builder reads | deterministic aggregate by period        |

**Schema Ownership:**

- **Reconciliation engine:** Owns adjustment lifecycle from generation through approval and posting to close_book.
- **close_book:** Reconciliation engine's output; statement builder's exclusive input.
- **Statement builder:** Reads close_book only; no direct reads from `statements`, `hb`, or other source schemas.

**Cross-Query Dependencies:**

Statement builder uses close_book exclusively:

| id | query_key                   | dependency_filter                        | characteristic        |
| -- | --------------------------- | ---------------------------------------- | --------------------- |
| 01 | is personal expense         | close_book class=`personal_expense`      | gl_code aggregate     |
| 02 | is investment pnl           | close_book class in (`investment_pnl`,`m2m`,`forex`)| includes m2m/forex |
| 03 | bs assets                   | close_book class=`asset`                 | includes valuations   |
| 04 | bs liabilities              | close_book class=`liability`             | includes accruals     |
| 05 | ni = delta net assets check | is net income vs bs net assets delta     | blocking validation   |

**Determinism and Rerun Safety:**

- Same reconciliation session run twice produces identical adjustments with idempotent posting.
- `adjustment_id` is deterministic hash of `(session_id, account_id, period_key, rule_reference, residual_gap)`.
- Upsert: if adjustment_id exists, update status and user_approval fields only; do not duplicate.
- Statement builder queries are deterministic: same close_book snapshot produces identical statement aggregates.

## Module Invocation Contract

The reconciliation engine is invoked by the workflow orchestrator at reconcile stage 6, per account. The invocation contract is:

**Inputs:**
- `account_id`: Account to reconcile.
- `period_key`: Calendar month in YYYY-MM format.
- `method_class`: transaction_level or balance_level, derived from account group.
- Source schemas: `statements`, `hb_gl_txn`, `hb_account_dim`, `cash_staging`, and others as determined by method and account group.
- Tolerance threshold: Per account group.
- Heuristics config: From `txn_heuristics.json` or mapping schema.

**Outputs:**
- `session_record`: Reconciliation session with status, variance, approval decision.
- `adjustment_record`: If variance non-zero; adjustment_id, amount, status, posting target.
- `report`: Human-readable reconciliation report with matched/unmatched counts, variance explanation.

**Error Handling:**
- If required source datasets missing: blocking error; rerun data sync.
- If matching fails — unmatched items exceed tolerance: review-level error; user approval required.
- If HB write-back fails: adjustment staged in close_book; retry logged.
- If SQLite posting fails: reconciliation blocked; error surfaced.

## OOP Architecture and Repository Layout

The reconciliation engine module is designed as a layered, object-oriented system with clean separation between domain models, algorithm implementations, utilities, shared adapters, and orchestration.

### Class Hierarchy Overview

**Abstract base class:**
- `ReconciliationMethod` — Defines contract for all reconciliation strategies with 4 abstract methods: `validate_inputs()`, `compute_gap()`, `classify_variance()`, `generate_adjustment()`

**Concrete method classes:**
- `TransactionLevelMethod(ReconciliationMethod)` — Bank statement matching: forward/backward passes, heuristics, edits model
- `BalanceLevelMethod(ReconciliationMethod)` — Balance equation reconciliation: cash, CPF, manual-input, HomeBudget-native

**Orchestration class:**
- `ReconciliationEngine` — Owns session state, method dispatch, adjustment posting, audit trail. Methods: `execute_reconciliation()`, `dispatch_by_account_group()`, `post_adjustment()`, `generate_session_record()`

**Domain models:**
- `AdjustmentTransaction` — Adjustment lifecycle with 20 fields and 4-state status: generated → pending_approval → approved → posted
- `ReconciliationSession` — Per-account session record with 27 fields, 8 audit checkpoints, and lineage anchors

### Method Dispatch Contract

```
execute_reconciliation(account_id, period_key)
  ├─ classify_account_group(account_id) → 'bank' | 'cash' | 'cpf' | ...
  ├─ instantiate_method(account_group) → TransactionLevelMethod | BalanceLevelMethod
  ├─ method.validate_inputs(account_id, period_key, source_schemas)
  ├─ method.compute_gap(account_id, period_key) → Decimal
  ├─ method.classify_variance(gap, tolerance_config) → 'zero' | 'within_tolerance' | 'exceeds_tolerance'
  ├─ method.generate_adjustment(...) → dict | None
  ├─ evaluate_variance() + request_user_approval_if_needed()
  ├─ post_adjustment_to_close_book()
  └─ close_session() → ReconciliationSession
```

### Key Utility Classes

| id | utility_class         | purpose                              |
| -- | --------------------- | ------------------------------------ |
| 01 | `HeuristicsConfig`    | load config + account overrides      |
| 02 | `LedgerSlicer`        | build slices + opening balances      |
| 03 | `MatchingAlgorithm`   | forward/backward match + heuristics  |
| 04 | `GapValidator`        | assert equations + invariants        |
| 05 | `VarianceClassifier`  | classify zero/within/exceeds         |
| 06 | `AdjustmentBuilder`   | build deterministic adjustment ids   |

### Repository Layout

**Directory structure:**
```
src/close_session/reconciliation_engine/
├─ __init__.py                          # Public API exports
├─ engine.py                            # ReconciliationEngine class
├─ models/
│  ├─ adjustment_transaction.py
│  ├─ reconciliation_session.py
│  └─ enums.py                          # VarianceClass, AdjustmentStatus, SessionStatus
├─ methods/
│  ├─ __init__.py
│  ├─ reconciliation_method.py           # Abstract base
│  ├─ transaction_level_method.py
│  └─ balance_level_method.py
├─ utilities/
│  ├─ heuristics_config.py
│  ├─ ledger_slicer.py
│  ├─ matching_algorithm.py
│  ├─ gap_validator.py
│  ├─ variance_classifier.py
│  └─ adjustment_builder.py
└─ config/
   ├─ config_loader.py
   ├─ txn_heuristics.json               # Heuristic parameters, account overrides
   └─ tolerance_config.json             # Tolerance thresholds by account group

src/python/adapters/                    # App-wide shared adapter layer
├─ sqlite_adapter.py                    # Read GL, persist session, write close_book
└─ homebudget_wrapper.py                # HB GL posting (read-only or write-back)
```

**Dependency flow — strict acyclic:**
- Layer 1: `models/` — No external dependencies
- Layer 2: `utilities/` — Depends on models only
- Layer 3: `methods/` — Depends on models, utilities
- Layer 4: shared adapters (`src/python/adapters/`) — App-wide utilities consumed by engine and other modules
- Layer 5: `engine.py` — Depends on models, utilities, methods, and shared adapter interfaces

### Library Dependencies

| id | library    | purpose                       | key_classes_methods                  |
| -- | ---------- | ----------------------------- | ------------------------------------ |
| 01 | `pandas`   | ledger/stmnt transforms       | `DataFrame`, `sort_values()`, `sum()`|
| 02 | `decimal`  | exact money arithmetic        | `Decimal`, `quantize()`              |
| 03 | `sqlite3`  | read/write sqlite schemas     | `Connection`, param queries          |
| 04 | `pydantic` | model validation              | `BaseModel`, `Field`, `validator`    |
| 05 | `uuid`     | session/adjustment ids        | `uuid.uuid4()`                       |
| 06 | `json`     | config loading                | `json.load()`                        |
| 07 | `hashlib`  | deterministic id hashing      | `hashlib.sha256()`                   |
| 08 | `logging`  | audit + checkpoint logs       | `getLogger()`, structured records    |
| 09 | `enum`     | typed status enums            | `Enum`, `auto()`                     |

### Implementation Constraints

1. **Deterministic matching:** Same algorithm, same parameters, same row ordering → identical match pairs
2. **Decimal arithmetic:** All monetary amounts use `Decimal(28,2)` with `ROUND_HALF_UP`. Never float.
3. **Idempotent posting:** Adjustment_id is deterministic hash of `(session_id, account_id, period_key, rule_reference, residual_gap)`. Same variance twice produces same adjustment_id.
4. **Gap invariant:** `sum(edit_amount) == 0.00` for every edit set and heuristic application. Mandatory correctness check.
5. **Forward-backward equivalence:** Forward-pass matches must equal backward-reduction matches after heuristics. Divergence is correctness failure; fail closed.
6. **Configuration is ground truth:** txn_heuristics.json and tolerance_config.json are sole sources; discovered at runtime; stored in metadata for reproducibility.

### Design Completeness References

- **Full class hierarchy specification:** [reconciliation-class-hierarchy.json](reconciliation-class-hierarchy.json)
- **Utility and dependency design:** [reconciliation-utilities-design.json](reconciliation-utilities-design.json)
- **Module layout and import relationships:** [reconciliation-engine-module-layout.json](reconciliation-engine-module-layout.json)
- **Markdown layout summary:** [reconciliation-engine-module-layout.md](reconciliation-engine-module-layout.md)

All specifications are implementation-ready with method signatures, parameter contracts, inheritance relationships, and composition cardinality fully defined.

---

## Key Findings

### Method Class Design Findings

#### Finding 1: Forward–backward equivalence is a mandatory correctness assertion for transaction-level reconciliation

After heuristics application, the forward and backward-reduced edit sets must be identical in both shape and values. This equivalence check is not optional validation; it is a correctness gate that must block reconciliation advancement if sets differ. Divergence indicates either a heuristic bug or a fundamental algorithmic inconsistency that risks data corruption and audit trail damage.

**Implication:** Store both edit sets in reconciliation metadata; compute set difference before proceeding to tolerance evaluation. Fail closed if sets diverge; do not allow silent override without explicit documented exception process.

#### Finding 2: Edits model invariant — sum of edit_amount = 0.00 for modified subsets — is both power and constraint

The edits model provides universal representation for both forward — greedy matching — and backward — trivial reduction — derivations. The gap-preservation invariant (`sum(edit_amount) == 0.00` for any heuristic-modified subset) is simultaneously a source of power — no re-balancing needed after edits removal — and a constraint: heuristics cannot be arbitrary text-matching rules.

**Implication:** Account-specific heuristics must be carefully designed to preserve this invariant. Any heuristic that removes edits without net-zero edit_amount will silently corrupt the gap equation. Heuristic validation by computing subset sum for removed edits must be mandatory before production deployment.

#### Finding 3: Heuristic parameter discovery from config file is ground truth; parameters must be discovered at runtime, not hard-coded

The `txn_heuristics.json` file is the sole source of truth for matching parameters — date_tolerance_days and amount_tolerance — and heuristic configuration: keywords, patterns, and enabled flags. This design allows per-account customization without code changes; however, it requires the config to be version-controlled, validated at startup, and stored in invocation metadata for audit trail.

**Implication:** Validate `txn_heuristics.json` at agent startup, not at reconciliation time. Log configuration errors early. Include discovered parameters in reconciliation session metadata. When parameters change — for example, to handle new bank behavior — update config first, then validate against known historical reconciliation sessions to ensure consistency.

#### Finding 4: Balance-level tolerance thresholds are account-group-specific and asymmetric; user confirmation is a tolerance mechanism

Bank statement-process accounts require zero tolerance, while cash allows ±SGD 20 asymmetry. This asymmetry reflects source quality: bank statements are source-of-truth, while cash is subject to physical counting variance. Separately, HomeBudget-native and CPF accounts use user confirmation and roll-forward validation instead of numeric thresholds.

**Implication:** Tolerance configuration must be keyed by account group, not by individual account. Variance evaluation logic must distinguish numeric tolerance — threshold-based — from confirmation tolerance — user-validated. Adjustment preparation differs: auto-prepare for numeric groups; present for approval without pre-population for confirmation-tolerance groups.

### Account-group Procedure Findings

Bank statement-process accounts require zero tolerance, while cash allows ±SGD 20 asymmetry. This asymmetry reflects source quality and account volatility: bank statements are considered source-of-truth with deterministic txn records, while cash is subject to physical counting variance and timing ambiguity. Account groups share the same tolerance class within group — all bank accounts have zero tolerance — but different groups have different thresholds. **Implication:** tolerance configuration must be keyed by account group, not by individual account. Variance evaluation must apply group-specific threshold before presenting adjustment to POC.

### Finding 2: Variance handling diverges between transaction-level and balance-level methods

Transaction-level reconciliation for bank accounts produces a list of unmatched items as edits and requires user review per unmatched item. Balance-level reconciliation for cash, CPF, wallets, and IBKR produces a single residual gap and requires single approval decision. This difference affects the adjustment outcome structure and approval scope. **Implication:** reconciliation engine must maintain separate variance evaluation workflows for transaction-level vs. balance-level. Adjustment outcome messages and approval UI must be tailored per method class.

### Finding 3: IBKR deviates from shared reconciliation framework; uses deterministic derivation instead of variance-based adjustment

IBKR accounts do not produce reconciliation adjustments based on variance evaluation. Instead, IBKR txns are derived deterministically from statement activity following the accounting model in ibkr-integration.md. Close-gate checks validate the derived txns: balance-equation closure and NAV roll-down. If checks pass, txns are posted directly. If checks fail, reconciliation is blocked. **Implication:** IBKR reconciliation is not variance-driven and does not follow shared tolerance rules. IBKR has its own accounting model and must be routed to separate validation logic, not to general reconciliation engine.

### Finding 4: Post-target schema ownership is asymmetric: all adjustments post to close_book, but HB write-back behavior varies by account group

All account groups post approved adjustments to close_book as the primary target for period closure. However, HB write-back behavior differs: bank statement-process accounts write back matched source rows as validation-only; cash and IBKR create new HB entries via wrapper; CPF and HomeBudget-native accounts have no HB write-back. **Implication:** adjustment posting must be two-phase: first, post to close_book for all groups; second, conditionally post to HB GL via wrapper based on account group write-back policy.

### Finding 5: User confirmation is the tolerance mechanism for non-numeric account groups

HomeBudget-native and CPF accounts do not have numeric tolerance thresholds. Instead, tolerance is user confirmation — HB-native confirms the ledger is final — or roll-forward validation — CPF user corrects balance inputs. This deviates from bank/cash/wallets which have numeric thresholds and auto-prepared adjustments. **Implication:** variance evaluation logic must distinguish numeric tolerance — threshold-based — from confirmation tolerance — user-validated. Adjustment preparation workflow differs: auto-prepare for numeric tolerance groups; present for approval without pre-population for confirmation-tolerance groups.

## Recommendations and Risks

### Method Class Implementation Recommendations

**Recommendation 1: Implement mandatory forward–backward equivalence check as a correctness gate**

After heuristics application, always assert that forward and backward-reduced edit sets are identical. This equivalence check must block reconciliation advancement if sets differ. Do not allow silent override or "close anyway" unless explicitly approved through a documented exception process.

*Rationale:* Divergence between forward and backward approaches indicates either a heuristic bug or a fundamental algorithmic inconsistency. Early detection prevents data corruption and audit trail damage.

*Implementation:* Store both edit sets in reconciliation metadata; compute set difference before proceeding to tolerance evaluation. Include set comparison result in reconciliation session artifact.

**Recommendation 2: Separate configuration validation from runtime invocation**

Validate `txn_heuristics.json` at agent startup, not at reconciliation time:
1. Check config file exists and is valid JSON.
2. Verify all account names match account dimension.
3. Verify heuristic names match enabled heuristic functions.
4. Check tolerance values are valid positive decimals.
5. Fail agent startup if validation fails.

*Rationale:* Configuration errors should not emerge mid-reconciliation. Early validation provides operator visibility and prevents reconciliation cascades from propagating invalid config.

**Recommendation 3: Detailed heuristics application audit trail**

For each heuristics invocation, record:
1. Heuristic name and parameters applied.
2. Number of edits before and after.
3. Edits removed: list of `(source, date, amount, note)` tuples.
4. Verification: `sum(edit_amount over removed subset) == 0.00`.

*Rationale:* Heuristics application is non-obvious and domain-specific. Audit trail enables operator review, variant investigation, and confidence in correctness.

**Recommendation 4: Handle statement ending balance mismatch gracefully in slice construction**

When statement slice ending balance does not match `balances` dataset:
1. Log a warning with the mismatch amount and date.
2. Allow user to choose: proceed with reconciliation or investigate balance discrepancy.
3. If user proceeds, reconciliation continues but the discrepancy is flagged in the session artifact.
4. Do not silently adjust the statement ending balance.

*Rationale:* Balance mismatches indicate upstream data quality issues that may affect downstream reporting. Transparent user choice preserves control and audit trail.

**Recommendation 5: Implement Decimal-only arithmetic throughout reconciliation pipeline**

Use Python `Decimal` type exclusively for all amount, balance, and gap calculations. Never use float arithmetic. Add type hints to all reconciliation functions. Use strict assertions at function entry points: `assert isinstance(gap, Decimal)`.

*Rationale:* Float arithmetic can accumulate rounding errors that cause gap to be non-zero even when all edits are valid. Decimal ensures exact arithmetic and maintains gap invariant.

### Account-group Procedure Recommendations

**Recommendation 1: Implement account-group dispatch logic before reconciliation-engine invocation

**Recommendation:** Create account-close runtime routing logic that dispatches accounts to the correct reconciliation method class and tolerance configuration based on account group classification. Do not pass account-group classification to reconciliation-engine as a parameter; instead, resolve all account-specific configuration — method class, tolerance, source schemas, and adjustment category — before dispatch, and pass fully-resolved configuration to reconciliation-engine.

**Rationale:** Account-group classification is a design-time property; passing it at runtime increases reconciliation-engine parameter complexity and couples account classification to reconciliation-engine logic. Pre-resolving configuration simplifies engine inputs and makes configuration more testable.

### Method Class Design Risks

**Risk 1: Heuristic pattern fragility in account-specific rules**

Account-specific heuristics — CPF keywords and UOB cashback patterns — depend on consistent transaction description formatting from the source. If statement parsing changes or bank changes transaction description format, heuristics may silently fail to match, leaving edits in the final set that should have been removed.

*Mitigation:* Store heuristic hit count — the number of times each heuristic matched — in session metadata. Monitor for periods where heuristic was expected to apply but did not. Alert operator if hit count drops unexpectedly from historical baseline.

**Risk 2: Ambiguous match proliferation in forward pass**

If matching parameters are too loose — large date_tolerance_days or large amount_tolerance — one ledger transaction may match multiple statement candidates, causing the one-to-one uniqueness test to fail. This leaves the transaction unmatched, requiring an edit. If heuristics then remove the edit, the final reconciliation may appear valid but hide the underlying ambiguity.

*Mitigation:* Log the count of ambiguous matches per account per period. If ambiguity exceeds a threshold — for example, more than 5% of transactions — escalate to user for review. Include ambiguous match list in session artifact for inspection.

**Risk 3: Float arithmetic contamination in gap calculations**

If any part of the reconciliation pipeline uses float arithmetic instead of Decimal, accumulated rounding errors may cause gap to be non-zero even when all edits are valid. This is particularly dangerous in heuristics, where sum checks must be exact.

*Mitigation:* Use Decimal type exclusively for all amount, balance, and gap calculations. Never call `float()` or use `/` operator on Decimals without explicit `Decimal(x) / Decimal(y)` guards. Add type hints. Use strict assertions at function entry: `assert isinstance(gap, Decimal)`.

**Risk 4: Backward pass equivalence check not enforced as mandatory gate**

If the forward–backward equivalence check is implemented as a warning instead of a failure condition, divergence may be silently accepted and carried forward to tolerance evaluation and adjustment generation, corrupting the session artifact.

*Mitigation:* Make equivalence check a mandatory gate. Fail closed if forward and backward sets diverge. Document this as a correctness requirement, not a validation suggestion. Include equivalence result as a critical checkpoint in reconciliation report.

### Account-group Procedure Risks

**Risk 1: Cash tolerance threshold — ±SGD 20 — may be too permissive for small-variance detection**

**Risk:** Cash is managed by user manual counts. A ±SGD 20 threshold allows 4% variance on a SGD 500 wallet or 0.2% on a SGD 10,000 physical safe. For high-value cash reserves, this tolerance may hide systematic counting errors or losses. Conversely, for low-value petty cash, this tolerance is excessively strict.

**Mitigation:**
- Make cash tolerance configurable per cash account subtype — for example, petty cash vs. safe — if multi-account cash is deployed in future.
- Document the ±SGD 20 threshold as a POC-scope decision; it requires review for production deployment.
- Include cash variance in reconciliation report and long-term audit trend analysis to detect systematic cash-handling issues.

**Confidence: High** — this is a known constraint documented in requirements.

### Key Risk 2: IBKR close-gate check failures block close but do not identify root cause automatically

**Risk:** If IBKR close-gate checks fail — for example, NAV roll-down mismatch — reconciliation is blocked without automated diagnosis. POC must manually investigate IBKR statement and compare to derived txns to find the discrepancy. This could consume significant time during close if IBKR data is complex.

**Mitigation:**
- Implement diagnostic output from IBKR accounting model; close-gate checks should include detailed error messages, for example: "NAV mismatch: expected SGD 145,000, derived SGD 144,800, delta SGD 200 not accounted for in trades/dividends/interest".
- Provide POC with side-by-side statement vs. derived txn comparison in GS session UI.
- Document common IBKR close-gate failure modes and POC troubleshooting steps in user guide.

**Confidence: Medium** — IBKR derivation logic is complex; error messages must be clear to aid POC diagnosis.

### Key Risk 3: Bank statement-process tolerance of zero may fail if statement formatting changes mid-period

**Risk:** If bank statement format changes unexpectedly — for example, bank switches CSV vendor or column order — date or amount parsing may shift, causing previously-matched txns to become unmatched. POC would face bulk unmatched txns even if underlying ledger is correct.

**Mitigation:**
- Implement format detection in bank statement adapter with explicit format version tracking.
- If format change detected, log warning to GS session UI and block ingest until format is re-confirmed.
- Provide POC with format re-configuration workflow if expected format changes — for example, seasonal format change or bank upgrade.
- Test reconciliation against multiple statement formats in unit tests to catch format sensitivity early.

**Confidence: High** — format stability is a critical dependency that should be validated up front.

