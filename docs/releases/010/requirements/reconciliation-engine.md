---
title: Reconciliation Engine
doc_type: requirements
topic_type: owner
owner: reconciliation-engine
scope: poc
---
# Reconciliation Engine

## Summary

This document defines the reconciliation requirements for the POC close cycle.

It presents shared policies and workflow phases first, then defines transaction-level and balance-level methods, and then details account-group requirements for bank statement-process, HomeBudget-native, cash, IBKR, CPF, and manual-input accounts.

## Table of contents

- [Summary](#summary)
- [Reference documents](#reference-documents)
- [Primary scope](#primary-scope)
- [Out of scope](#out-of-scope)
- [Shared reconciliation patterns](#shared-reconciliation-patterns)
  - [Shared workflow phases](#shared-workflow-phases)
  - [Reconcile workflow stages and checkpoints](#reconcile-workflow-stages-and-checkpoints)
  - [Source-input contracts](#source-input-contracts)
  - [Bill accrual conflict policy](#bill-accrual-conflict-policy)
  - [Tolerance rules and variance escalation](#tolerance-rules-and-variance-escalation)
  - [Closure criteria and period acceptance conditions](#closure-criteria-and-period-acceptance-conditions)
  - [Adjustment transaction outcomes and posting](#adjustment-transaction-outcomes-and-posting)
  - [Lineage and audit requirements](#lineage-and-audit-requirements)
- [Reconciliation method classes](#reconciliation-method-classes)
  - [Transaction-level method class](#transaction-level-method-class)
    - [Semantic matching layer](#semantic-matching-layer)
    - [Transfer-expense pairing](#transfer-expense-pairing)
  - [Balance-level method class](#balance-level-method-class)
- [Account-group procedures](#account-group-procedures)
  - [Bank statement-process accounts](#bank-statement-process-accounts)
  - [HomeBudget-native accounts](#homebudget-native-accounts)
  - [Cash reconciliation](#cash-reconciliation)
  - [IBKR accounts](#ibkr-accounts)
  - [CPF accounts](#cpf-accounts)
  - [Manual-input accounts](#manual-input-accounts)

## Reference documents

- [cash reconcile](cash-reconcile.md)
- [glossary](glossary.md)
- [source systems and lineage](source-systems-lineage.md)
- [workflow orchestration](workflow-orchestration.md)
- [exception and error handling](exception-error-handling.md)

## Primary scope

- Reconciliation workflow, stages, and checkpoint definitions
- Reconciliation logic, formulas, and tolerance evaluation
- Account-group specific reconciliation procedures and workflows
- Adjustment transaction generation, posting, and closure
- Variance interpretation and escalation policy
- Reconcile closure criteria by period and account group

## Out of scope

- Workflow orchestration stage ordering
- Statement lifecycle publication policy
- Exception-policy remediation behavior details

## Shared reconciliation patterns

This section defines requirements shared by all reconciliation account groups.

## Shared workflow phases

Reconciliation proceeds on a per-account basis. Each account follows the same shared phases.

**Phase 1: Input and source validation**

- Validate required source datasets are available for the account and period.
- Verify source data schemas match expected format.
- Confirm account scope and period scope boundaries.
- Log validation timestamp.

**Phase 2: Source staging and aggregation**

- Read source transactions and balances for the account from applicable source schemas.
- Perform account-level normalization or aggregation required for comparison.
- Validate staged data is complete for the account and period.
- Retain aggregation metadata and staging timestamp.

**Phase 3: Comparison and match**

- Execute method-class matching logic for the account.
- Record match status for each transaction or balance record.
- Identify unmatched items and compute residual variance or residual gap.
- Classify variance type.

**Phase 4: Variance interpretation and tolerance evaluation**

- Evaluate residual variance against account-group tolerance threshold.
- Classify outcome as within tolerance, exceeds tolerance, or zero variance.
- If within tolerance, prepare automatic adjustment recommendation.
- If exceeds tolerance, prepare adjustment for user review with variance explanation.
- Record variance interpretation and threshold comparison.

**Phase 5: Adjustment generation and formatting**

- Create adjustment transaction record with required fields.
- Format transaction compatible with target system, close_book and HB GL, or other destination.
- Assign category and description per account-group policy.
- Retain adjustment rule reference, timestamp, and user comment when provided.

**Phase 6: Review, approval, and posting**

- If variance is within tolerance, notify user of prepared adjustment; user can approve, investigate, or request modification.
- If variance exceeds tolerance, flag account variance and present adjustment for user review before approval.
- For transaction-level reconciliation, present semantic matching pairs and transfer-expense pairing proposals for user review before posting.
- User can edit, add, or remove proposed pair and edit records before final approval.
- User approval is required before posting.
- Post approved adjustment to close_book schema.
- Post approved adjustment to target system through wrapper interface when applicable.

**Phase 7: Reconciliation closure and reporting**

- Generate reconciliation report with period, variance, tolerance status, and checkpoint outcomes.
- Record reconciliation session details, timestamps, and decision points.
- Log completion status and close approval.
- Archive reconciliation artifacts for audit trail.

## Reconcile workflow stages and checkpoints

| id | stage               | checkpoint focus                         |
| -- | ------------------- | ---------------------------------------- |
| 01 | source readiness    | required source datasets are available   |
| 02 | match and classify  | transaction and balance matching passes  |
| 03 | semantic pairing    | proposed semantic and transfer-expense pairings reviewed |
| 04 | variance review     | residual variance reviewed and explained |
| 05 | close decision      | close criteria satisfied for all paths   |

## Tolerance rules and variance escalation

- Cash adjustment alert threshold uses plus or minus SGD 20.
- Bank statement-process accounts reconcile `statements` schema against `hb_gl_txn` using exact match to currency rounding 0.01 decimal place precision at account precision unless owner policy on this page is updated.
- Variance outside policy threshold triggers escalation and blocks close.

### Variance interpretation and adjustment behavior

**Zero variance:**
- Residual gap is effectively zero within tolerance.
- No adjustment transaction is required.
- Reconciliation is closed with verification checkpoint.

**Within tolerance, non-zero variance:**
- Residual variance falls within the account-group tolerance threshold.
- System automatically generates adjustment transaction.
- User is notified of adjustment but no approval is required.
- Adjustment is posted on user confirmation of reconciliation completion.

**Exceeds tolerance:**
- Residual variance exceeds the account-group tolerance threshold.
- System prepares adjustment transaction and flags for user review.
- User must approve, modify, or investigate variance before adjustment can be posted.
- User approval is recorded with timestamp and any user comment or correction.
- Adjustment is posted only after explicit user approval.

## Closure criteria and period acceptance conditions

- Required reconcile checks pass for all in-scope account groups.
- All transactions within scope have traceability outcome assigned: standard lineage or adjustment with rule reference.
- Unexplained blocking variance is not present at close time.
- All tolerances are either satisfied or explicitly overridden by user approval.
- Period reconcile output is recorded with lineage, checkpoint outcomes, and decision timestamps.

## Source-input contracts

- Reconcile is account-group specific; each group consumes different source schemas and comparison bases.
- HomeBudget account and category context for reconcile comes from `hb_account_dim` and `hb_category_dim`.
- Inputs must include period scope and account scope boundaries.

## Bill accrual conflict policy

Bill-domain reconciliation has dual authority and must separate expense recognition from settlement matching.

- Bill statement is authoritative for billed amount, payee, and expense breakdown.
- Bank statement is authoritative for settlement amount and settlement date.
- Reconciliation must preserve accrual treatment so the full billed amount is expensed in the billing period.

Conflict classes and required handling:

- **No conflict:** billed amount equals settlement amount and both fall in the same period. Reconcile directly with no special bridge entries.
- **Near-end-of-month timing conflict:** if bill date and bank posting date are within plus or minus 3 days of period end, and period end is more than 3 days away from the close date, the booked ledger date may be shifted to the billing period. The resulting statement-to-book timing variance is handled by bank account reconciliation, not by changing bill expense recognition.
- **Cross-period timing conflict:** if the timing does not meet the near-end-of-month rule, book the full bill expense in the billing period and create a matching transfer into the shared billing pseudo credit account. When payment posts, create the matching transfer out on the actual bank statement date.
- **Partial payment conflict:** book the full bill expense and full transfer into the shared billing pseudo credit account in the billing period. Book one or more transfers out as each payment posts on the bank statement.

Reconciliation acceptance rules for bill conflicts:

- The billed-period expense must equal the full billed amount.
- The shared billing pseudo credit account balance must equal the unpaid or timing-difference remainder.
- The bill reaches fully settled status only when transfers into and out of the shared billing pseudo credit account net to zero.
- Any remaining difference between billed amount and total settlement amount is a blocking reconciliation finding unless explicitly approved through variance treatment.

## Adjustment transaction outcomes and posting

Each reconciliation procedure produces zero or one adjustment transaction. Adjustments follow deterministic outcomes.

- **Standard lineage transaction:** transaction retains normal source lineage to origin system and source reference.
- **Adjustment transaction:** transaction is marked as system adjustment and retains adjustment rule reference, for example reconciliation engine policy or cash gap tolerance, plus adjustment timestamp and user comment when provided.

Adjustment posting targets:

- **close_book schema:** final reconciled state used for statement aggregation.
- **HomeBudget GL:** if account group integrates with HomeBudget wrapper, adjustment is posted to HB for user visibility and audit.

## Lineage and audit requirements

- Reconcile outputs must include source references and decision trace.
- Each adjustment must retain adjustment rule reference, timestamp, and user confirmation or auto-approval justification.
- Close decision must include checkpoint outcomes and timestamps for all account groups.
- Reconciliation session artifacts must be retained in audit location as defined in [source systems and lineage](source-systems-lineage.md).
- Bill conflict cases must retain both bill statement reference and bank statement reference, plus the shared billing pseudo credit account net position at close.

## Reconciliation method classes

This section defines the two method classes reused by account-group procedures.

## Transaction-level method class

Transaction-level reconciliation compares transactions from two independent sources and computes a minimal edit set required to close gap.

### Edits model

The transaction-level method produces an edits table that describes how to adjust ledger transactions to match statement transactions.

- `source` uses `"ledger"` or `"statement"` to identify transaction origin.
- `date` stores transaction date.
- `amount` stores original transaction amount in account currency.
- `edit` uses `"remove"` or `"add"` to identify adjustment operation.
- `edit_amount` stores signed delta, `-amount` for remove and `+amount` for add.
- `note` stores transaction description or notes field.
- `ledger_idx` and `stmt_idx` store original row indices for traceability.

**Reconciliation gap with edits:**

```
gap = ledger_end_balance + sum(edit_amount over all edits) - statement_end_balance
```

A valid solution satisfies `gap == 0.00`. Among valid solutions, the method prefers the minimal edit set.

### Forward and backwards algorithm

The method uses two passes.

**Forward pass:**

1. Match ledger and statement transactions that are unambiguously equivalent.
2. Match criteria:
  - Exact amount match, same sign and exact cents.
  - Date proximity, `abs(date_ledger - date_statement) ≤ date_tolerance_days`.
  - One-to-one uniqueness, exactly one unmatched statement candidate per ledger transaction.
3. Build edits from unmatched transactions.
  - Unmatched ledger transactions create `remove` edits with `edit_amount = -amount`.
  - Unmatched statement transactions create `add` edits with `edit_amount = +amount`.

**Backwards pass:**

1. Start from trivial valid solution, remove all ledger and add all statement.
2. For each forward match pair, remove corresponding remove and add edits from trivial set.
3. Apply same heuristics to forward and backwards-reduced edit sets.

**Expected method outcome:**

- Forward and backwards-reduced edit sets are identical after heuristics.
- Final gap equals `0.00` when reconcile is complete.

### Heuristics

All heuristics preserve this invariant.

```
sum(edit_amount over modified or removed subset) = 0.00
```

General heuristics for all accounts:

- Net-zero pairs, opposite amount edits within 3-day window from same source.
- Same-amount zero-sum clusters, balanced mixed-source clusters with net zero edit amount.

Account-specific heuristics:

- DBS Multi SGD, CPF net-zero cluster using CPF keyword matching.
- UOB One SGD, cashback split cluster where one ledger cashback equals multiple statement rebate lines.

### Semantic matching layer

After heuristics, transaction-level reconciliation applies a semantic matching layer over remaining `add` and `remove` edits.

- Pairing scope is account and period.
- Pairing compares `add.note` and `remove.note` with semantic or heuristic matching rules.
- Date proximity must satisfy `date_tolerance_days`.
- For approved pairs, the `add` edit is removed, the `remove` edit is reclassified as `update` and `edit_amount` is set to the paired `add.amount`.
- User review is required before semantic pair actions are committed.
- User can create, update, or delete pair and edit records before approval.

### Transfer-expense pairing

After semantic statement-ledger pairing is approved, reconciliation applies transfer-expense pairing for `TWH - Personal` zero-sum behavior.

- Pairing scope is one transfer against one expense unless an account heuristic enables multi-transaction grouping.
- Pairing requires date proximity within `date_tolerance_days` and amount equivalence where `transfer.amount = -expense.amount`.
- When multiple candidates exist, tie-breakers are semantic note match first, then date proximity.
- Pairing actions map from transfer edit type to expense CRUD actions.
- All transfer-expense actions are staged for user review and approval before HomeBudget write-back.
- If no approved pairing exists, user performs manual expense repair and reconcile cannot close with unresolved blocking variance.

### Method parameters

| id | parameter             | usage                          | example values              |
| -- | --------------------- | ------------------------------ | --------------------------- |
| 01 | `date_tolerance_days` | ± days for date matching       | 3 default, 5 for slow banks |
| 02 | `amount_tolerance`    | ± currency for amount variance | 0.01 default                |

## Balance-level method class

Balance-level reconciliation compares ending balances or derived balances between primary and comparison sources, then computes a residual gap.

### Generic balance equation

```
Residual Gap = Primary Balance - Comparison Balance - Σ Staged Adjustments
```

Definitions:

- Primary Balance is source-of-truth balance for the account group.
- Comparison Balance is secondary or user-observed balance for the account group.
- Σ Staged Adjustments is sum of known adjustments or intermediate states.

### Balance-level outcomes

- Zero variance, no adjustment required.
- Within tolerance, adjustment can be auto-prepared.
- Exceeds tolerance, user review and approval required before posting.

## Account-group procedures

Account-group procedures reuse shared workflow phases and method-class rules. This section only defines account-specific requirements.

### Bank statement-process accounts

- **Accounts in scope:** TWH DBS Multi SGD, TWH CITI USD, TWH UOB One SGD, TWH Visa USD
- **Method class:** Transaction-level method class
- **Comparison basis:** `statements` schema parsed transaction ledger, `stm_gl`, versus `hb_gl_txn` records — see [bank-statements.md](bank-statements.md) for the parser contract that populates `statements`
- **Tolerance:** Exact match required, zero tolerance for residual unmatched amounts

**Reconciliation parameters:**

- `date_tolerance_days`: 3 days default, 5 days for TWH UOB One SGD if posting delays are observed
- `amount_tolerance`: 0.00 currency units

**Account-specific method extensions:**

- Opening balance source is previous period ending balance from balances dataset.
- Statement ending balance source is current period ending balance from balances dataset.
- Statement-slice end balance must cross-check to balances dataset ending balance at account precision.
- Apply account-specific heuristics when applicable, DBS CPF cluster and UOB cashback split cluster.

**Adjustment outcome:**

- If all transactions matched and no edits remain after heuristics: reconciliation passes with zero adjustment
- If edits remain after heuristics: create adjustment transactions for each edit with category `Balancing:Unmatched`

**Acceptance:** All transactions matched or explained via edits, final gap is zero.

### HomeBudget-native accounts

- **Accounts in scope:** HomeBudget-native accounts with no external statement source, for example 30 Hashemis CC
- **Method class:** Balance-level method class
- **Comparison basis:** `hb_gl_txn` ledger state versus user review and confirmation
- **Tolerance:** User confirmation, user review is the comparison basis

**Account-specific method extensions:**

- Fetch all `hb_gl_txn` records for the account for the period
- Present ledger summary and transaction listing to user for review
- User confirms all transactions are correct or marks transactions for correction
- If corrections marked: user updates categories or amounts in HomeBudget; system re-reads updated state

**Adjustment criteria:**
- If user confirms ledger state is final: reconciliation passes, no adjustment needed
- If user marks corrections: user makes changes in HomeBudget; reconciliation proceeds with updated state

### Cash reconciliation

- **Accounts in scope:** Cash TWH SGD
- **Method class:** Balance-level method class
- **Comparison basis:** staged wallet cash aggregates plus user-entered close balance versus `hb_gl_txn` records
- **Tolerance:** Cash adjustment tolerance threshold as defined in [Tolerance rules and variance escalation](#tolerance-rules-and-variance-escalation)

**Account-specific equation:**

```
Residual Gap = HB Current Balance - Actual Physical Cash - Σ Staged Wallet Expenses
```

**Account-specific method extensions:**

- Read staged wallet cash aggregates for the account for the period from the `cash_staging` schema
- Read `hb_gl_txn` records for the account for the period
- Compute HB current balance as sum of `hb_gl_txn.amount` for the account and period
- Retrieve user-entered close balance for the period
- Compute residual gap as `HB Current Balance - Actual Physical Cash - Σ Staged Wallet Expenses`
- Evaluate gap against the cash adjustment tolerance threshold defined in [Tolerance rules and variance escalation](#tolerance-rules-and-variance-escalation)

**Adjustment criteria:**
- If gap within tolerance: auto-prepare adjustment with category Balancing:Unknown
- If gap exceeds tolerance: flag for user review; user can approve, modify, or investigate
- If user approves: generate adjustment and post to close_book and HB GL

### IBKR accounts

- **Accounts in scope:** TWH IB USD cash, IB Position USD holdings, IB IRA USD
- **Method class:** IBKR integration accounting model route
- **Owner document:** [IBKR integration](ibkr-integration.md)
- **Policy:** IBKR transactions are generated from deterministic statement derivation, not from variance-based reconciliation adjustments

**Reconciliation-engine behavior for IBKR:**

- Route IBKR accounts to the accounting model and derivation rules in [IBKR integration](ibkr-integration.md)
- Run close-gate validation checks defined by [IBKR integration](ibkr-integration.md)
- Do not create reconciliation adjustments for IBKR accounts in reconciliation-engine
- If any IBKR close-gate check fails, block close and flag the account for investigation before posting

### CPF accounts

- **Accounts in scope:** CPF OA, CPF SA, CPF MA
- **Method class:** Balance-level method class
- **Comparison basis:** user-provided monthly input records versus roll-forward and contribution consistency
- **Tolerance:** Rounding tolerance for interest and contribution roll-forward

**Account-specific equation:**

```
Residual Gap = Expected Closing Balance - User-Entered Closing Balance
```

**Account-specific method extensions:**

- Fetch user-entered CPF balances, contributions, and interest from closing-session GS UI for the account for the period
- Compute expected closing balance using roll-forward formula: Opening Balance + Contributions + Interest
- Compare computed expected balance to user-entered closing balance
- Compute residual gap as `Expected Closing Balance - User-Entered Closing Balance`
- If difference is zero or within rounding tolerance: reconciliation passes
- If difference exceeds tolerance: flag inconsistency and present to user with explanation

**Adjustment criteria:**
- If user confirms balances are correct: reconciliation passes, no adjustment needed
- If user corrects entry: system re-reads updated state and reconciliation proceeds

### Manual-input accounts

- **Accounts in scope:** Wallets and balance-only accounts, for example Amazon wallet
- **Method class:** Balance-level method class
- **Comparison basis:** user-observed current balance input versus pre-adjustment `hb_gl_txn` ledger state
- **Tolerance:** Zero tolerance for balance-only accounts, exact match required

**Account-specific method extensions:**

- Fetch user-entered current balance from closing-session GS UI for the account
- Compute pre-adjustment balance as sum of `hb_gl_txn.amount` for the account and period
- Compute required adjustment delta as `User Balance - Pre-Adjustment Balance`
- Evaluate delta against zero tolerance

**Adjustment criteria:**
- If delta is zero: no adjustment needed, reconciliation passes
- If delta is non-zero: prepare adjustment transaction with computed amount for user approval


