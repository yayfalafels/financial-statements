---
name: reconciliation-patterns
description: Phase templates and tolerance examples for cash, balance-level, and transaction-level reconciliation with procedural discipline.
license: MIT
compatibility: Python 3.8+
metadata:
  author: yayfalafels
  version: 1.0.0
---

## Overview

This skill provides phase templates and tolerance examples for reconciliation workflows. Each reconciliation type (cash, balance-only, transaction-level) has a strict phase order, blocking conditions, and tolerance rules. This skill prevents procedural errors such as skipped phases, conflated methods, or incorrect variance classification.

## When to Use This Skill

- Designing reconciliation workflows for bank, credit card, or investment accounts.
- Implementing reconciliation phase execution and validation logic.
- Defining tolerance rules and variance classification for account groups.
- Creating reconciliation test cases and acceptance criteria.
- Resolving procedural disputes about phase order or variance decisions.

## Reconciliation Phase Template

All reconciliation workflows follow this ordered phase sequence:

### Phase 0: Pre-Reconcile Validation

**Purpose**: Validate that source and target data are available, complete, and in the correct state.

**Checks**:
- Statement source file exists and is readable.
- HomeBudget GL sync is current (within 1 business day of statement date).
- Period is closed or in flight (not future or past-closed).
- Account is active in both statement source and HomeBudget.
- No prior unresolved reconciliation for the same period/account pair exists.

**Blocking rule**: If any check fails, reconciliation cannot proceed. Return error with remediation guidance.

**Example implementation**:
```python
def validate_pre_reconcile(account_id, statement_period):
    checks = [
        ("statement_exists", statement_file_exists(account_id, statement_period)),
        ("hb_synced", hb_sync_age_days(account_id) <= 1),
        ("period_valid", is_open_or_in_flight_period(statement_period)),
        ("account_active", is_active_account(account_id, statement_period)),
        ("no_prior_unresolved", not has_unresolved_prior_reconcile(account_id, statement_period))
    ]
    failed = [name for name, passed in checks if not passed]
    if failed:
        raise ReconciliationBlocked(f"Pre-reconcile validation failed: {', '.join(failed)}")
```

### Phase 1: Data Staging

**Purpose**: Extract and normalize statement and GL data into a shared comparison format.

**Inputs**:
- Statement file (CSV, PDF, or Excel depending on account type).
- HomeBudget GL transactions synced to `hb_gl_txn`.

**Outputs**:
- `stmt_line` table: normalized statement line items.
- `hb_line` table: normalized HomeBudget GL lines for comparison.

**Staging rules**:
- Date normalization: all dates to ISO 8601 format.
- Amount normalization: all amounts to signed decimal, positive = inflow, negative = outflow.
- Account normalization: map statement account labels to canonical account names.
- Deduplication: remove duplicate statement lines (by statement reference, not hash).

**Example structure**:
```python
stmt_line = {
    "statement_ref": str,        # stable reference to source line
    "txn_date": date,            # ISO 8601
    "amount": Decimal,           # signed: positive = inflow
    "description": str,          # normalized payee or description
    "balance_after": Decimal,    # running balance after this line (if provided)
}

hb_line = {
    "hb_txn_uid": str,           # deterministic transaction hash
    "txn_date": date,            # ISO 8601
    "amount": Decimal,           # signed
    "description": str,          # category or memo
    "account_id": str,           # HomeBudget account ID
}
```

**Blocking rule**: If statement has no lines or GL has no lines for the period, reconciliation cannot proceed.

### Phase 2: Matching Strategy Selection

**Purpose**: Select the reconciliation method based on account type and available data.

**Match strategies**:

| strategy       | when_to_use                                     | match_key                        | tolerance_rule          |
| -------------- | ----------------------------------------------- | -------------------------------- | ----------------------- |
| transaction    | bank/credit card with itemized statement        | date + amount + (desc optional) | exact match or within ±0.01 |
| balance-only   | third-party investment or CPF account           | statement end date               | balance within tolerance |
| statement-hash | dedup-required ingest (multiple sources)        | statement ref hash               | ref match required      |

**Selection logic**:
```python
def select_match_strategy(account_type, has_statement_refs, has_detailed_items):
    if has_statement_refs and has_detailed_items:
        return "transaction"
    elif not has_detailed_items and has_statement_refs:
        return "statement-hash"
    else:
        return "balance-only"
```

**Blocking rule**: If the statement format does not support the selected strategy, reconciliation blocks with a format error.

### Phase 3: Transaction-Level Matching (if applicable)

**Purpose**: Match individual statement lines to HomeBudget transactions.

**Match rules**:
- Primary key: (txn_date, amount)
- Secondary filter: description contains payee or memo substring (optional, for disambiguation)
- Tolerance: ±0.01 for statement rounding

**Algorithm**:
```python
def match_transactions(stmt_lines, hb_lines):
    matched = []
    unmatched_stmt = []
    unmatched_hb = []
    
    for stmt_line in stmt_lines:
        candidates = [
            hb for hb in hb_lines
            if hb.txn_date == stmt_line.txn_date
            and abs(hb.amount - stmt_line.amount) <= 0.01
        ]
        if len(candidates) == 1:
            matched.append((stmt_line, candidates[0]))
        elif len(candidates) > 1 and stmt_line.description:
            # disambiguate by description similarity
            scored = [(c, score_description_match(c.description, stmt_line.description)) for c in candidates]
            best = max(scored, key=lambda x: x[1])
            if best[1] > 0.5:  # description similarity threshold
                matched.append((stmt_line, best[0]))
            else:
                unmatched_stmt.append(stmt_line)
        else:
            unmatched_stmt.append(stmt_line)
    
    unmatched_hb = [hb for hb in hb_lines if not any(hb in m for _, m in matched)]
    return matched, unmatched_stmt, unmatched_hb
```

**Outcome classification**:
- Matched: statement line and GL line represent the same transaction.
- Unmatched in statement: statement has a transaction not yet in HomeBudget.
- Unmatched in GL: HomeBudget has a transaction not in the statement.

### Phase 4: Balance-Level Matching (if applicable)

**Purpose**: Validate that statement and HomeBudget balances agree or identify the variance.

**Balance calculation**:
- Statement balance: final balance from statement (period-end) or calculated from opening + net movement.
- HomeBudget balance: sum of all GL transactions for the account + opening balance from prior period.

**Variance calculation**:
```python
def calculate_variance(statement_balance, hb_balance):
    variance_amount = statement_balance - hb_balance
    variance_pct = (variance_amount / abs(hb_balance)) * 100 if hb_balance != 0 else 0
    return variance_amount, variance_pct
```

**Blocking rule**: If variance exceeds tolerance, reconciliation moves to variance classification (Phase 5) instead of close.

### Phase 5: Variance Classification

**Purpose**: Classify and quantify any reconciliation variance before deciding to adjust or escalate.

**Variance categories**:

| category                | cause                                        | resolution                                  |
| ----------------------- | -------------------------------------------- | ------------------------------------------- |
| rounding                | statement rounding ±0.01 per line            | accept if < SGD/USD 0.05 total              |
| timing                  | transaction in flight (posted later)         | verify date and expect next period          |
| duplicate               | statement line appears twice                 | remove duplicate and re-reconcile           |
| missing_in_hb           | HomeBudget transaction not yet posted        | verify posting and expect next reconcile    |
| missing_in_stmt         | HomeBudget transaction not on statement      | query statement provider or escalate        |
| exchange_rate           | forex rate difference in posting             | verify rate and accept if within 0.1%       |
| bank_fee_unposted       | statement includes bank fee not yet in HB    | post fee transaction and re-reconcile       |
| reconcile_adjustment    | prior-period reconciliation adjustment       | verify adjustment posting and accept        |

**Tolerance thresholds**:

| account_group     | variance_tolerance | resolution_rule                    |
| ----------------- | ------------------ | ---------------------------------- |
| bank (SGD/USD)    | ±SGD/USD 5.00      | exact match or within tolerance    |
| credit_card       | ±SGD/USD 5.00      | exact match or within tolerance    |
| investment        | ±USD 0.01 per unit | accept if pricing variance only    |
| cpf_account       | ±SGD 1.00          | strict match; escalate on variance |

**Classification logic**:
```python
def classify_variance(variance_amount, account_type, matched_count, unmatched_stmt, unmatched_hb):
    # Rounding variance
    if abs(variance_amount) < 0.05 and account_type in ["bank", "credit"]:
        return ("rounding", "accept")
    
    # Timing variance (few unmatched)
    if len(unmatched_stmt) <= 2 and len(unmatched_hb) <= 2:
        if all(is_recent_date(line.txn_date) for line in unmatched_stmt + unmatched_hb):
            return ("timing", "defer")
    
    # Escalate if variance exceeds tolerance
    tolerance = get_tolerance(account_type)
    if abs(variance_amount) > tolerance:
        return ("material_variance", "escalate")
    
    return ("unclassified", "escalate")
```

### Phase 6: Adjustment Decision

**Purpose**: Decide whether to post an adjustment transaction or escalate for manual review.

**Decision rules**:
- Rounding variance ≤ tolerance: post adjustment automatically.
- Timing variance: defer to next reconciliation period.
- Material variance: escalate for manual investigation.
- Missing transaction: post missing transaction and re-reconcile.

**Adjustment posting rule**:
```python
def post_adjustment_if_eligible(variance_amount, variance_category, tolerance):
    if variance_category == "rounding" and abs(variance_amount) <= tolerance:
        adjustment_txn = create_adjustment_transaction(
            amount=variance_amount,
            description=f"Reconciliation adjustment for {variance_category}",
            post_date=statement_date,
            account_id=account_id
        )
        return adjustment_txn
    else:
        return None  # escalate for manual review
```

**Blocking rule**: If material variance cannot be classified or exceeds tolerance, reconciliation blocks with escalation required.

### Phase 7: Reconciliation Close

**Purpose**: Mark the reconciliation as complete and commit the result.

**Close actions**:
- If no variance or acceptable variance: mark reconciliation as `reconciled`.
- If adjustment posted: log adjustment transaction ID and timestamp.
- If escalation required: mark reconciliation as `pending_review` with variance details.
- Update `reconcile` table with final status, variance, and decision.

**Close query**:
```python
def close_reconciliation(reconcile_record, adjustment_txn=None, variance_category=None):
    if variance_category in ["rounding", "timing"]:
        reconcile_record.status = "reconciled"
    elif adjustment_txn:
        reconcile_record.status = "reconciled"
        reconcile_record.adjustment_txn_id = adjustment_txn.id
    else:
        reconcile_record.status = "pending_review"
        reconcile_record.escalation_reason = variance_category
    
    reconcile_record.closed_at = utc_now()
    db.session.commit()
```

## Cash Reconciliation Pattern (Bank Accounts)

**Account types**: Checking, savings, money market.

**Data sources**: Bank statement (CSV or PDF) + HomeBudget GL.

**Reconciliation contract**:

| phase | input                                | output                          |
| ----- | ------------------------------------ | ------------------------------- |
| 0     | account + period                     | pre-checks passed               |
| 1     | statement file + HB GL               | staged stmt + HB lines          |
| 2     | account type                         | match strategy = transaction    |
| 3     | stmt lines + HB lines                | matched + unmatched list        |
| 4     | HB balance + stmt balance            | variance amount                 |
| 5     | variance amount + account type       | variance category + resolution  |
| 6     | variance category + tolerance        | adjustment or escalation        |
| 7     | result + adjustment (if any)         | reconcile record updated        |

**Tolerance rule**: ±SGD/USD 5.00 for exact-match reconciliation. Rounding variance ±0.01 per line acceptable.

**Example closing**: TWH DBS Multi SGD, March 2026

```
Statement balance (Mar 31):           SGD 10,502.15
Opening balance (Feb 28):             SGD 9,800.00
Net deposits and expenses (Mar):      SGD 702.15
HomeBudget balance (Mar 31):          SGD 10,500.00
Variance:                             SGD 2.15

Variance category:                    rounding
Resolution:                           accept (within ±SGD 5.00)

GL adjustment (if needed):            none required
Reconciliation status:                reconciled
```

## Balance-Only Reconciliation Pattern (Investment / CPF Accounts)

**Account types**: IBKR investment position, CPF account (read-only statement).

**Data sources**: Statement balance query or form (no itemized transactions) + HomeBudget GL.

**Reconciliation contract**:

| phase | input                                | output                          |
| ----- | ------------------------------------ | ------------------------------- |
| 0     | account + period                     | pre-checks passed               |
| 1     | statement balance + HB GL balance    | staged balances                 |
| 2     | account type                         | match strategy = balance-only   |
| 3     | N/A (no line matching)               | skipped                         |
| 4     | HB balance + stmt balance            | variance amount                 |
| 5     | variance amount + account type       | variance category + resolution  |
| 6     | variance category + tolerance        | adjustment or escalation        |
| 7     | result + adjustment (if any)         | reconcile record updated        |

**Tolerance rule**: ±USD 0.01 per unit for investments. ±SGD 1.00 for CPF (strict).

**Example closing**: IB POSITION USD, March 2026

```
Statement balance (Mar 31):           USD 24,100.00 (market value)
Opening balance (Feb 28):             USD 23,750.00
Mark-to-market adjustment (Mar):      USD 350.00
HomeBudget balance (Mar 31):          USD 24,100.00
Variance:                             USD 0.00

Variance category:                    exact_match
Resolution:                           reconciled
Reconciliation status:                reconciled
```

## Reconciliation Precedence Rules

When reconciliation discovers multiple issues, resolve in this order:

| precedence | issue                     | resolution                                   |
| ---------- | ------------------------- | -------------------------------------------- |
| 1          | pre-reconcile validation  | block and escalate                           |
| 2          | duplicate statement lines | remove duplicates and re-match               |
| 3          | exact match available     | use exact match and close                    |
| 4          | rounding variance         | post adjustment if within tolerance          |
| 5          | timing variance           | defer to next period                         |
| 6          | material variance         | escalate for manual review                   |

## Validation Checklist for Reconciliation Procedures

When implementing a reconciliation workflow:

- [ ] Phase 0 pre-checks are executed before any matching.
- [ ] Phase 1 staging normalizes both statement and GL to identical format.
- [ ] Phase 2 match strategy is selected based on account type and data availability.
- [ ] Phase 3 matching applies correct key and tolerance per account type.
- [ ] Phase 4 balance calculation is independent and verifiable.
- [ ] Phase 5 variance classification uses decision tree logic, not subjective judgment.
- [ ] Phase 6 adjustment decision respects tolerance bounds and escalation rules.
- [ ] Phase 7 reconciliation close logs all decisions and transaction IDs.
- [ ] Tolerance thresholds are documented per account type.
- [ ] Blocking conditions are explicit and non-ambiguous.
- [ ] Unresolved reconciliations are escalated, not silently deferred.

## Related Documentation

- `docs/requirements/reconciliation-engine.md` — POC reconciliation policy and methods.
- `docs/requirements/cash-reconcile.md` — cash reconciliation requirements.
- Agent `financial-accounting` — for defining new reconciliation tolerance rules.
- Skill `accounting-logic` — for identity assertions in reconciliation adjustments.
