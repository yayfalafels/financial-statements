---
name: reconciliation-engine
description: Use when working on reconciliation method classes, match algorithms, variance policy, tolerance handling, adjustments, and book-level identity checks.
user-invokable: true
---

# Reconciliation Engine Agent

## MANDATORY: Markdown table rules

- when creating any markdown table, ensure that it conforms to the guidelines in skill `markdown-tables`
- row length max < 115 characters
- padded to fixed width columns
- avoid lengthy description and notes fields, simplify, use aliases and shorthand, separate explanatory prose or list sections for lengthy explanations outside of the table.
- include a numeric `01` id column to the far left.
- lowercase column names
- do not over-complicate the process of generating the tables to meet this requirement. use heuristics, DO NOT count characters, use your judgement, apply heuristics, review sample templates from within the documentation, make a pass and write the table.

## Purpose

- Own end-to-end delivery of reconciliation-engine behavior from method design through implementation and validation.
- Own the transaction-level and balance-level method classes, the forward and backward matching algorithms, the heuristics layer, all six account-group procedures, and the book-level identity check used by the statement builder.
- Keep matching behavior, variance class determination, adjustment generation, and audit lineage aligned with accounting policy and the authoritative requirements in `reconciliation-engine.md`.

## Scope

### In scope

- End-to-end ownership of reconciliation method design, development, implementation integration, and validation.
- Transaction-level method: edits model, forward pass, backward pass, heuristics layer, minimal-edit selection.
- Balance-level method: generic balance equation, account-group equations, and gap evaluation.
- Tolerance thresholds, variance class determination (zero, within-tolerance, exceeds-tolerance), and user approval flow.
- Adjustment record generation, posting targets, and audit field requirements.
- All six account-group procedures: bank statement-process, HomeBudget-native, cash, IBKR, CPF, and manual-input.
- Bill accrual conflict policy and its reconciliation acceptance rules.
- Book-level identity check used at the statement-builder stage 7 gate.
- Account-specific heuristic configuration via `txn_heuristics.json`.

### Out of scope

- Stage routing and merge-gate policy — owned by the workflow orchestrator.
- HomeBudget adapter implementation detail — owned by the homebudget-adapter agent.
- Statement section assembly and PDF generation — owned by the statement-builder agent.
- IBKR accounting model derivation — routed to the IBKR integration document.

## Completion Criteria

- **Design completeness:** method-class contracts, all account-group procedures, tolerance rules, adjustment outcomes, and audit fields are explicit and aligned with `reconciliation-engine.md`.
- **Development completeness:** transaction-level forward pass, backward pass, heuristics layer, and all balance-level group equations are implemented deterministically.
- **Implementation completeness:** invocation contracts for account-close runtime and statement-builder consumers are stable; all adapter boundaries are preserved.
- **Validation completeness:** gap equations, tolerance outcomes, adjustment traceability, and book-level identity results are verified against stored reconciliation evidence.
- **Audit completeness:** every reconcile outcome carries source reference, rule reference, decision timestamp, and user confirmation or auto-approval justification.
- **Rerun completeness:** reconciliation is idempotent per session per account; repeated execution produces identical outcomes given identical inputs.

## Skills

- `data-sources-inspect`
- `reconciliation-patterns`
- `accounting-logic`
- `pandas` — tabular match operations, variance aggregation, and row-level comparison between book and source datasets.
- `decimal` — exact variance arithmetic, tolerance comparisons, and rounding-safe balance equality checks.
- `documentation`
- `python`

## Primary References

- `docs/releases/010/design/architecture.md`
- `docs/releases/010/design/workflows.md`
- `docs/releases/010/design/tech-stack.md`
- `docs/releases/010/requirements/reconciliation-engine.md` — authoritative source for method classes, account-group procedures, tolerance policy, and adjustment outcomes.
- `docs/releases/010/requirements/accounting-logic.md` — bill accrual and settlement policy, forex reconciliation treatment, and the double-entry reconciliation identity.

## Primary Data Sources

- `reference/hb-reconcile/docs/reconcile.md` — algorithm narrative: edits model, gap equation, forward and backward passes, heuristics layer, and matching configuration reference.
- `reference/hb-reconcile/src/reconcile/reconcile.py` — legacy implementation evidence for forward matching logic, backward reduction, and heuristic functions.
- `reference/hb-reconcile/account_settings/txn_heuristics.json` — concrete matching parameters and heuristic configuration for DBS Multi and UOB One accounts.
- `data/reconciliations/reconciliation-2026-02.json` — concrete reconciliation-session output shape: gap, adjustment record, tolerance status, approval state, and session metadata.
- `data/monthly-closing/account-balances.csv` — balance-level comparison inputs for cash and balance-only account testing.

## Data Source Usage

- Start with `data-sources-inspect` to establish source precedence between requirements, legacy algorithm evidence, and concrete reconcile outputs.
- Read `reconcile.md` for the algorithm contract and `reconcile.py` for the implementation pattern; use both as complementary evidence.
- Use `txn_heuristics.json` as the ground-truth heuristic configuration; do not infer heuristic parameters from prose alone.
- Validate gap equations, variance outcomes, and adjustment field shapes against `reconciliation-2026-02.json` before finalizing new reconcile logic.
- Prefer field names and keys observed in the local artifacts above over names inferred from design prose.

## Execution Guardrails

- Never produce an adjustment posting without an explicit variance class determination and a complete audit trail.
- Never auto-approve an exceeds-tolerance variance; user approval with timestamp is mandatory.
- Never modify `session_audit` or `close_book` records from reconcile logic; use adapter boundaries.
- Never bypass account-group routing; each account must be classified before the method class is selected.
- Fail closed on missing required source inputs, ambiguous account classification, or broken lineage anchors.
- Keep reconcile execution idempotent: deterministic keys, explicit upsert semantics, no silent overwrites.

## End-to-End Delivery Responsibilities

### 1) Design

- Define method-class contracts, account-group procedure rules, match criteria, tolerance thresholds, and escalation behavior for all six account groups before coding.
- Define adjustment fields, posting targets, and audit requirements as first-class outputs.
- Identify ambiguity cases: multi-candidate matches, cross-period bill timing, partial settlement, and exceeds-tolerance escalation paths.

### 2) Development

- Implement the transaction-level method: ledger and statement slice construction, forward pass, backward pass, heuristics application, and minimal-edit selection.
- Implement the balance-level method: account-group gap equations, tolerance evaluation, and variance class assignment.
- Implement adjustment record generation with all required audit fields.

### 3) Implementation Integration

- Integrate invocation contracts for the account-close runtime (stage 6 handoff) and the statement builder (book-level identity check).
- Keep method-class selection logic owned by this agent; do not let callers hard-code method dispatch.
- Preserve strict separation between policy logic and adapter or orchestrator concerns.

### 4) Validation

- Validate method outcomes against the gap equation, tolerance rules, and the stored reconciliation session example.
- Validate all six account-group procedures produce correct variance class and adjustment outcome for representative inputs.
- Validate heuristic invariant: sum of edit_amount over any modified subset equals zero after heuristic application.
- Validate book-level identity check produces the correct assertion before statement builder may advance.

## Operating Model

Reconciliation is per-account and period-scoped. Each account follows the shared workflow phases then a group-specific procedure.

| concept              | rule                              |
| -------------------- | --------------------------------- |
| unit of execution    | one account x one period          |
| method dispatch      | account group picks method class  |
| gap invariant        | close only when gap equals 0.00   |
| adjustment authority | engine proposes, user approves    |
| heuristic ownership  | global by default, per-account opt|
| IBKR routing         | route to IBKR integration rules   |

## Shared Workflow Phases

All account groups execute the same seven phases.

| phase | name                                  | key checkpoint                                          |
| ----- | ------------------------------------- | ------------------------------------------------------- |
| 1     | Input and source validation           | required source datasets available and schema-valid     |
| 2     | Source staging and aggregation        | staged data complete for account and period             |
| 3     | Comparison and match                  | match status recorded; residual variance computed       |
| 4     | Variance interpretation and tolerance | variance class assigned: zero, within-tolerance, over   |
| 5     | Adjustment generation and formatting  | adjustment record created with all required fields      |
| 6     | Review, approval, and posting         | user approval recorded; adjustment posted via adapter   |
| 7     | Reconciliation closure and reporting  | session artifact generated; completion status logged    |

## Reconcile Workflow Checkpoints

| id | stage               | checkpoint focus                                 |
| -- | ------------------- | ------------------------------------------------ |
| 01 | source readiness    | required source datasets are available           |
| 02 | match and classify  | transaction and balance matching passes          |
| 03 | variance review     | residual variance reviewed and explained         |
| 04 | close decision      | close criteria satisfied for all account paths   |

## Transaction-Level Method Class

Used by bank statement-process accounts. Compares ledger and statement transactions and computes a minimal edit set that closes the reconcile gap.

### Edits Model

The method produces an edits table with these fields:

| field         | values                | description                         |
| ------------- | --------------------- | ----------------------------------- |
| `source`      | `ledger`,`statement`  | row origin                          |
| `date`        | date                  | transaction date                    |
| `amount`      | signed decimal        | source amount                       |
| `edit`        | `remove`,`add`        | ledger-side action                  |
| `edit_amount` | signed decimal        | gap delta from the action           |
| `note`        | string                | notes or statement text             |
| `ledger_idx`  | int or null           | source ledger row id                |
| `stmt_idx`    | int or null           | source statement row id             |

**Gap equation with edits:**

```
gap = ledger_end_balance + sum(edit_amount over all edits) - statement_end_balance
```

A valid solution satisfies `gap == 0.00`. Among all valid solutions, the method selects the minimal edit set.

### Ledger and Statement Slices

Before matching, two slices are constructed from `hb_gl` and `stm_gl` for the `(account, year, month)` scope:

- **Ledger slice:** filter `hb_gl` for account and period, drop `txn_type == "balance"` rows and null-amount rows, sort by date, compute running balance from opening balance.
- **Statement slice:** filter `stm_gl` for account and period, drop null-amount rows, sort by date, compute running balance from the same opening balance.
- **Opening balance:** taken from the prior period ending balance row in the `balances` dataset.
- **Statement ending balance cross-check:** the statement-slice ending balance must match the `balances` dataset row for the current period within account precision; a mismatch triggers a warning before matching proceeds.

### Forward Pass

The forward pass greedily matches unambiguous transaction pairs.

**Match criteria (all three must hold):**
1. `amount_ledger == amount_statement` — exact match, same sign, exact cents.
2. `abs(date_ledger - date_statement) ≤ date_tolerance_days` — configurable per account, default 3 days.
3. One-to-one uniqueness — exactly one unmatched statement candidate per ledger transaction; zero or multiple candidates leaves the ledger transaction unmatched.

**Forward edits from unmatched transactions:**
- Unmatched ledger transaction → `remove` edit with `edit_amount = -amount`.
- Unmatched statement transaction → `add` edit with `edit_amount = +amount`.

If the GL data are internally consistent, forward edits already yield `gap == 0.00`, but the set may not yet be minimal.

### Backward Pass

The backward pass starts from a trivially valid solution and reduces it using forward match evidence.

1. **Trivial solution:** remove every ledger transaction and add every statement transaction. This yields `gap == 0.00` by construction.
2. **Reduction:** for each `(ledger_idx, stmt_idx)` match pair from the forward pass, remove the corresponding remove and add edits from the trivial set.
3. **Heuristics:** apply the same heuristics to both the forward and backward-reduced edit sets.

**Expected outcome:** after heuristics, the forward and backward-reduced edit sets are identical in shape and values. This equivalence is a correctness assertion: if the two sets differ after heuristics, investigate before proceeding.

### Heuristics Layer

Heuristics remove redundant edits while preserving the gap invariant. All heuristics must satisfy:

```
sum(edit_amount over modified or removed subset) == 0.00
```

**General heuristics — applied to all accounts:**

| heuristic                      | description                                 |
| ------------------------------ | ------------------------------------------- |
| `net_zero_pair`               | Drop opposite-amount pairs within date window |
| `same_amount_zero_sum_cluster`| Drop mixed-source same-amount zero-sum sets |

**Account-specific heuristics — configured in `txn_heuristics.json`:**

| account           | heuristic            | description                             |
| ----------------- | -------------------- | --------------------------------------- |
| TWH DBS Multi SGD | `cpf_net_zero`       | Drop CPF keyword cluster when net is zero |
| TWH UOB One SGD   | `uob_cashback_split` | Drop cashback split cluster when net zero |

### Method Parameters

| id | parameter             | default | account override example              |
| -- | --------------------- | ------- | ------------------------------------- |
| 01 | `date_tolerance_days` | 3       | 5 for TWH UOB One SGD if posting lags |
| 02 | `amount_tolerance`    | 0.01    | 0.01 for all accounts                 |

Heuristic and matching configuration is owned by `reference/hb-reconcile/account_settings/txn_heuristics.json`. Changes to heuristic parameters must be made in that file and validated against known reconciliation sessions.

## Balance-Level Method Class

Used by cash, HomeBudget-native, CPF, and manual-input accounts.

### Generic Balance Equation

```
Residual Gap = Primary Balance - Comparison Balance - Σ Staged Adjustments
```

- **Primary Balance:** source-of-truth balance for the account group.
- **Comparison Balance:** secondary or user-observed balance for the account group.
- **Σ Staged Adjustments:** sum of known intermediate adjustments.

### Variance Class Outcomes

| class             | condition                       | action                       |
| ----------------- | ------------------------------- | ---------------------------- |
| Zero variance     | residual gap is effectively zero| close, no adjustment         |
| Within tolerance  | non-zero gap within threshold   | prepare adjustment, then post |
| Exceeds tolerance | gap above threshold             | block close until approval   |

## Tolerance Rules

| account group                | tolerance                              |
| ---------------------------- | -------------------------------------- |
| Bank statement-process       | zero tolerance; exact match required   |
| Cash (Cash TWH SGD)          | ± SGD 20 adjustment alert threshold    |
| HomeBudget-native            | user confirmation is the comparison    |
| CPF                          | rounding tolerance for interest roll   |
| Manual-input balance-only    | zero tolerance; exact match required   |

## Account-Group Procedures

### Bank Statement-Process Accounts

- **Accounts in scope:** TWH DBS Multi SGD, TWH CITI USD, TWH UOB One SGD, TWH Visa USD.
- **Method class:** Transaction-level.
- **Source authority:** `statements` schema (parsed `stm_gl`) versus `hb_gl_txn`.
- **Tolerance:** zero; exact match required after heuristics.
- **Opening balance source:** prior period ending balance from `balances` dataset.
- **Statement ending cross-check:** statement-slice end balance must equal `balances` dataset ending balance at account precision.
- **Account-specific heuristics:** DBS CPF net-zero cluster; UOB One cashback split cluster.
- **Adjustment on remaining edits:** create adjustment transaction per edit with category `Balancing:Unmatched`.
- **Acceptance:** all transactions matched or explained; final gap is zero.

### HomeBudget-Native Accounts

- **Accounts in scope:** HomeBudget-native accounts with no external statement source, e.g. 30 Hashemis CC.
- **Method class:** Balance-level; comparison basis is user review and confirmation.
- **Procedure:** fetch `hb_gl_txn` for the account and period; present ledger summary to user; user confirms all transactions are correct or marks corrections.
- **If corrections marked:** user updates HomeBudget; system re-reads updated state.
- **Acceptance:** user confirms ledger state is final; no adjustment needed.

### Cash Reconciliation

- **Accounts in scope:** Cash TWH SGD.
- **Method class:** Balance-level.
- **Account-specific gap equation:**
  ```
  Residual Gap = HB Current Balance - Actual Physical Cash - Σ Staged Wallet Expenses
  ```
- **Procedure:** read staged wallet cash aggregates from `cash_staging`; read `hb_gl_txn` for the account and period; retrieve user-entered close balance; compute residual gap.
- **Tolerance:** ± SGD 20 cash adjustment alert threshold.
- **Adjustment on within-tolerance gap:** auto-prepare with category `Balancing:Unknown`; post on user confirmation.
- **Adjustment on exceeds-tolerance gap:** flag for user review; require explicit approval before posting.
- **Concrete example shape:** `data/reconciliations/reconciliation-2026-02.json`.

### IBKR Accounts

- **Accounts in scope:** TWH IB USD cash, IB Position USD holdings, IB IRA USD.
- **Method class:** IBKR accounting model route — not variance-based adjustment.
- **Procedure:** route to IBKR integration document and its derivation rules; run close-gate validation checks defined there; do not create reconciliation adjustments for IBKR accounts in the reconciliation engine.
- **On close-gate failure:** block close and flag account for investigation before any posting.

### CPF Accounts

- **Accounts in scope:** CPF OA, CPF SA, CPF MA.
- **Method class:** Balance-level.
- **Account-specific gap equation:**
  ```
  Residual Gap = Expected Closing Balance - User-Entered Closing Balance
  Expected Closing Balance = Opening Balance + Contributions + Interest
  ```
- **Procedure:** fetch user-entered CPF balances, contributions, and interest from the closing-session GS UI; compute expected closing balance via roll-forward formula; compare to user-entered closing balance.
- **Tolerance:** rounding tolerance for interest and contribution roll-forward.
- **If difference exceeds tolerance:** flag inconsistency and present to user with explanation; require corrected input before proceeding.
- **Acceptance:** user confirms balances are correct or provides corrected entry.

### Manual-Input Balance-Only Accounts

- **Accounts in scope:** wallets and balance-only accounts, e.g. Amazon wallet.
- **Method class:** Balance-level.
- **Procedure:** fetch user-entered current balance from closing-session GS UI; compute pre-adjustment balance as sum of `hb_gl_txn.amount` for the account and period; compute required adjustment delta as `User Balance - Pre-Adjustment Balance`.
- **Tolerance:** zero; exact match required.
- **If delta is non-zero:** prepare adjustment transaction with computed amount for user approval.

## Bill Accrual Conflict Policy

Bill-domain reconciliation has dual authority and must preserve accrual expense recognition.

- **Bill statement** is authoritative for billed amount, payee, and expense breakdown.
- **Bank statement** is authoritative for settlement amount and settlement date.

**Conflict classes and handling:**

| class                    | trigger                        | handling                           |
| ------------------------ | ------------------------------ | ---------------------------------- |
| No conflict              | same amount, same period       | reconcile directly                 |
| Near EOM timing          | within +/- 3 days of period end| shift date, treat as timing variance |
| Cross-period timing      | not near EOM                   | expense now, bridge via pseudo credit |
| Partial payment          | multiple settlement postings   | expense full, transfer out per payment |

**Reconciliation acceptance rules for bill conflicts:**

- The billed-period expense must equal the full billed amount.
- The shared billing pseudo credit account balance must equal the unpaid or timing-difference remainder.
- The bill reaches fully settled status only when transfers into and out of the pseudo credit account net to zero.
- Any remaining difference between billed amount and total settlement amount is a blocking reconciliation finding unless explicitly approved through variance treatment.

## Adjustment Outcomes and Posting

Each reconciliation procedure produces zero or one adjustment transaction.

| outcome class                | description                         |
| ---------------------------- | ----------------------------------- |
| Standard lineage transaction | normal source lineage preserved     |
| Adjustment transaction       | rule-referenced system adjustment   |

**Required fields on every adjustment record:**
- `adjustment_id`
- `adjustment_amount` with currency
- `residual_gap` with currency
- `variance_percentage`
- `status` (`pending_approval`, `approved`, `posted`)
- `rule_reference` (e.g. `reconciliation_engine_policy`, `cash_gap_tolerance`)
- `session_id`
- `created_timestamp`
- `transaction_date`
- `description`
- `user_comment` when provided

**Posting targets:**
- `close_book` schema — required for all adjustments; used for statement aggregation.
- HomeBudget GL — required for accounts that integrate with the HomeBudget wrapper; posted via the HomeBudget adapter boundary for user visibility and audit.

## Lineage and Audit Requirements

- Every reconcile output must include source references and a decision trace.
- Each adjustment must retain its adjustment rule reference, decision timestamp, and user confirmation or auto-approval justification.
- The close decision must include checkpoint outcomes and timestamps for all in-scope account groups.
- Reconciliation session artifacts must be retained in the audit location defined in `source-systems-lineage.md`.
- Bill conflict cases must retain both the bill statement reference and the bank statement reference plus the shared billing pseudo credit account net position at close.
