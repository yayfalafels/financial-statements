---
name: accounting-logic
description: Worked examples and identity assertions for M2M, forex, double-entry, FIFO, and CPF accounting with calculation verification patterns.
license: MIT
compatibility: Python 3.8+
metadata:
  author: yayfalafels
  version: 1.0.0
---

## Overview

This skill provides worked examples and identity assertions for critical financial accounting calculations. Each worked example includes real workspace values, complete calculation steps, and identity assertions that must hold after the calculation. This skill prevents agent hallucination by grounding all accounting rules in concrete, verifiable examples from the workspace.

## When to Use This Skill

- Defining accounting policy for M2M, forex, double-entry, FIFO, or CPF rules.
- Implementing critical financial calculations that must be deterministic and verifiable.
- Designing reconciliation procedures and tolerance rules.
- Creating validation tests for financial calculations.
- Resolving ambiguity in accounting treatment.

## Double-Entry Bookkeeping Identity

**Identity assertion**: For every transaction, debits must equal credits. For every posting:

```
sum(debit accounts) = sum(credit accounts)
```

**Personal expense example** (from `docs/requirements/homebudget.md`):

Bill payment to Singtel (TWH UOB One SGD) for SGD 50.

| transaction | account              | debit | credit | note                            |
| ----------- | -------------------- | ----- | ------ | ------------------------------- |
| 1           | TWH - Personal       |       | 50.00  | expense in cost center          |
| 1           | TWH UOB One SGD      | 50.00 |        | credit card payment source      |

Identity check: debit (50.00) = credit (50.00) ✓

**Income posting example**:

Monthly SGD salary of 6,000 into TWH DBS Multi SGD.

| transaction | account           | debit  | credit | note                           |
| ----------- | ----------------- | ------ | ------ | ------------------------------ |
| 1           | TWH DBS Multi SGD | 6000.0 |        | income landing account         |
| 1           | Income:Salary     |        | 6000.0 | income offset                  |

Identity check: debit (6000.0) = credit (6000.0) ✓

**Transfer between accounts example**:

Transfer SGD 500 from TWH DBS Multi to TWH UOB One for spending.

| transaction | account           | debit | credit | note        |
| ----------- | ----------------- | ----- | ------ | ----------- |
| 1           | TWH UOB One SGD   | 500.0 |        | recipient   |
| 1           | TWH DBS Multi SGD |       | 500.0  | sender      |

Identity check: debit (500.0) = credit (500.0) ✓

**Forex difference settlement example**:

Charge posted to TWH Visa USD card: USD 100.00 at spot rate SGD 1.35 = SGD 135.00.
Actual billing amount after card processing: SGD 136.50 (includes 1% fee).
Difference: SGD 1.50 (recorded as expense).

| transaction | account                      | debit   | credit  | note                        |
| ----------- | ---------------------------- | ------- | ------- | --------------------------- |
| 1           | TWH - Personal               | 135.00  |         | expense at spot rate        |
| 1           | TWH Visa USD                 |         | 135.00  | credit from card            |
| 2           | TWH - Personal               | 1.50    |         | forex settlement difference |
| 2           | TWH Visa USD                 |         | 1.50    | additional credit charge    |

Identity check per transaction:
- Txn 1: debit (135.00) = credit (135.00) ✓
- Txn 2: debit (1.50) = credit (1.50) ✓

## Mark-to-Market (M2M) Accounting Identity

**Identity assertion**: At period end, investment position accounts must reflect current market value. Unrealized gains/losses must reconcile to:

```
period_end_value - period_start_value - net_cash_flow = unrealized_gain_loss
```

**M2M example** (as of Feb 28, 2026):

Starting position: 100 shares of VTI at USD 235.00 = USD 23,500.00
Cash added: USD 5,000.00 (no new share purchases, held as cash)
Market value at period end: 100 shares at USD 237.50 = USD 23,750.00

| account             | period_start | net_cash_flow | period_end_value | unrealized_change |
| ------------------- | ------------ | ------------- | ---------------- | ------------------- |
| IB POSITION USD     | 23500.00     | 0.00          | 23750.00         | 250.00              |
| TWH IB USD          | (50000.00)   | 5000.00       | (45000.00)       | 0.00                |

Period-end GL posting for unrealized gain:

| account         | debit  | credit | note                                 |
| --------------- | ------ | ------ | ------------------------------------ |
| IB POSITION USD |        | 250.00 | unrealized gain adjustment          |
| P&L:Unrealized  | 250.00 |        | P&L offset                          |

Identity check:
- position_end_value (23,750) - position_start (23,500) = unrealized (250) ✓
- GL transaction balances: debit (250) = credit (250) ✓

**Quarterly revaluation example**:

Previous position value (recorded 30-Dec): USD 23,750.00
Current market value (31-Mar): USD 24,100.00
Unrealized change: USD 350.00

Period-end adjustment (SCD Type 1 update):

| account         | old_value  | new_value  | adjustment | note                   |
| --------------- | ---------- | ---------- | ---------- | ---------------------- |
| IB POSITION USD | 23750.00   | 24100.00   | 350.00     | M2M revaluation        |

GL posting:

| account         | debit  | credit | note                    |
| --------------- | ------ | ------ | ----------------------- |
| IB POSITION USD |        | 350.00 | unrealized gain         |
| P&L:Unrealized  | 350.00 |        | P&L offset              |

Identity check:
- position_change (350) = market_revaluation (350) ✓
- GL transaction balances ✓

## Foreign Exchange (Forex) Accounting Identity

**Identity assertion**: For all forex transactions, the SGD effect must equal the sum of spot-rate conversions plus any settlement differences.

```
total_sgd_debit = sum(usd_amount * spot_rate) + settlement_difference
```

**Forex transaction example**:

Credit card charge: USD 150.00
Spot rate on transaction date (March 15, 2026): SGD/USD = 1.3450
Spot-rate SGD amount: 150.00 * 1.3450 = SGD 201.75

Card billing (posted March 28, 2026): SGD 202.10 (includes 0.35 SGD card fee)
Settlement difference: SGD 202.10 - SGD 201.75 = SGD 0.35

| step                 | usd_amount | rate   | sgd_amount | note                |
| -------------------- | ---------- | ------ | ---------- | ------------------- |
| 1. transaction date  | 150.00     | 1.3450 | 201.75     | spot rate posting   |
| 2. card fee charged  | —          | —      | 0.35       | settlement diff     |
| 3. total card charge | —          | —      | 202.10     | final posting       |

GL postings:

Transaction 1 (at spot rate):
| account        | debit  | credit | note               |
| -------------- | ------ | ------ | ------------------ |
| TWH - Personal | 201.75 |        | USD expense        |
| TWH Visa USD   |        | 201.75 | credit card charge |

Transaction 2 (settlement difference):
| account                             | debit | credit | note        |
| ----------------------------------- | ----- | ------ | ----------- |
| TWH - Personal                      | 0.35  |        | forex fee   |
| TWH Visa USD                        |       | 0.35   | card charge |

Identity check:
- total_sgd = 201.75 + 0.35 = 202.10 ✓
- GL transactions balance:
  - Txn 1: debit (201.75) = credit (201.75) ✓
  - Txn 2: debit (0.35) = credit (0.35) ✓

## FIFO Lot Sequencing Identity

**Identity assertion**: For any sale, the cost basis must be calculated by applying FIFO sequencing. The total gain/loss must equal:

```
proceeds - sum(fifo_cost_basis) = realized_gain_loss
```

And the sum of remaining cost basis plus sold cost basis equals original total cost.

**FIFO example** (simplified):

Starting position: 3 lots of VTI

| lot | date       | shares | price | cost_basis |
| --- | ---------- | ------ | ----- | ---------- |
| 1   | 2025-01-15 | 30     | 235   | 7050.00    |
| 2   | 2025-06-30 | 40     | 245   | 9800.00    |
| 3   | 2026-01-10 | 50     | 240   | 12000.00   |

Sell 60 shares at price USD 250.00 on 2026-03-15.

Proceeds: 60 × 250 = USD 15,000.00

FIFO application:
- Lot 1: all 30 shares @ 235.00 = 7,050.00
- Lot 2: 30 of 40 shares @ 245.00 = 7,350.00
- Total cost basis: 14,400.00

Remaining position:
- Lot 2: 10 shares @ 245.00 = 2,450.00
- Lot 3: 50 shares @ 240.00 = 12,000.00

Realized gain: 15,000.00 - 14,400.00 = USD 600.00

GL posting:

| account          | debit   | credit  | note           |
| ---------------- | ------- | ------- | -------------- |
| TWH IB USD       | 15000.0 |         | sale proceeds  |
| IB POSITION USD  |         | 14400.0 | cost basis out |
| P&L:Realized     |         | 600.0   | realized gain  |

Identity checks:
- proceeds (15000) - cost_basis (14400) = gain (600) ✓
- GL balances: debit (15000) = credit (14400 + 600) ✓
- remaining_cost_basis (2450 + 12000 = 14450) + sold_cost_basis (14400) = original (28850) ✓

## CPF Contribution Allocation Identity

**Identity assertion**: For any CPF contribution during the period, the total amount must equal the sum of OA, SA, and MS allocations:

```
contribution_total = oa_allocation + sa_allocation + ms_allocation
```

**CPF contribution example**:

Monthly CPF deduction for March 2026: SGD 2,000.00
Allocation per CPF rules for age 35-45:
- OA: 37% = 740.00
- SA: 37% = 740.00
- MS: 8% = 160.00
- Employer match (if applicable): 20% = 400.00 (to OA)

| account           | debit  | credit | note             |
| ----------------- | ------ | ------ | ---------------- |
| CPF:OA            |        | 740.00 | employee OA      |
| CPF:SA            |        | 740.00 | employee SA      |
| CPF:MS            |        | 160.00 | employee MS      |
| TWH DBS Multi SGD | 2000.0 |        | deduction from   |

Period-end GL rollup (employee portion only):

| account          | balance | note                   |
| ---------------- | ------- | ---------------------- |
| CPF:OA           | 740.00  | employee contribution  |
| CPF:SA           | 740.00  | employee contribution  |
| CPF:MS           | 160.00  | employee contribution  |
| Sum              | 1640.00 | —                      |

Note: Employer match (400.00) is posted separately.

Identity checks:
- employee_total (740 + 740 + 160) = deduction (1640) ✓
- GL transaction balances: debit (2000) = credit (740 + 740 + 160) ✓

## Period Roll-Up Identity

**Identity assertion**: For any period, the general ledger must satisfy:

```
opening_balance + net_movements = closing_balance
```

And the financial statement aggregation must match GL balances for all accounts in scope.

**Period roll-up example** (simplified):

Personal cost center account (TWH - Personal) for March 2026:

| metric              | value    | note                   |
| ------------------- | -------- | ---------------------- |
| opening_balance     | 500.00   | Feb 28 close           |
| expenses            | -2500.00 | posted in March        |
| income              | 1000.00  | transfer in            |
| transfers_in        | 500.00   | from DBS Multi         |
| net_movements       | -1000.00 | sum of activity        |
| closing_balance     | -500.00  | expected Mar 31 close  |

GL balance verification:
- opening (500) + net_movements (-1000) = closing (-500) ✓

Statement roll-up verification:
- Personal expenses (2500) - personal income (1000) - transfers_in (500) = net_movement (1000) ✓

## Reconciliation Tolerance Identity

**Identity assertion**: When a reconciliation produces a variance within tolerance, the adjustment must be posted such that:

```
hombudget_balance + adjustment = statement_balance
```

And the adjustment must be within the defined tolerance for the account group.

**Reconciliation example**:

Account: TWH DBS Multi SGD (bank account)
Statement balance as of Mar 31, 2026: SGD 10,502.15
HomeBudget GL balance as of Mar 31, 2026: SGD 10,500.00
Variance: SGD 2.15

Tolerance for bank accounts: ±SGD 5.00 (rounding tolerance)
Status: variance within tolerance, adjustment eligible.

Adjustment posting:

| account                | debit | credit | note          |
| ---------------------- | ----- | ------ | ------------- |
| TWH DBS Multi SGD      | 2.15  |        | rounding adj  |
| P&L:Reconciliation Adj |       | 2.15   | P&L offset    |

Identity check:
- hombudget_balance (10500) + adjustment (2.15) = statement_balance (10502.15) ✓
- adjustment (2.15) <= tolerance (5.00) ✓

## Validation Checklist for New Accounting Rules

When defining a new accounting rule, verify these identity assertions before implementation:

- [ ] Double-entry transactions balance (debits = credits).
- [ ] All values used in identity assertions are clearly named and sourced.
- [ ] Period roll-ups sum correctly (opening + net = closing).
- [ ] M2M revaluations reconcile to market movement.
- [ ] Forex conversions include spot rate and settlement differences.
- [ ] FIFO sequencing is deterministic and produces correct remaining balances.
- [ ] CPF splits preserve total contribution across OA/SA/MS.
- [ ] Reconciliation adjustments respect tolerance bounds.
- [ ] All worked examples use real workspace account names and periods.
- [ ] Example calculation steps are shown explicitly, not summarized.

## Implementation Validation Code Pattern

When implementing any accounting calculation, include identity assertions similar to this pattern:

```python
# Example: validate M2M unrealized gain calculation
assert (
    period_end_market_value 
    - period_start_market_value 
    - net_cash_flow 
    == unrealized_gain
), f"M2M identity failed: {period_end_market_value} - {period_start_market_value} - {net_cash_flow} != {unrealized_gain}"

# Example: validate double-entry posting
total_debits = sum(t.amount for t in transaction.lines if t.side == "debit")
total_credits = sum(t.amount for t in transaction.lines if t.side == "credit")
assert total_debits == total_credits, f"Transaction not balanced: debits {total_debits} != credits {total_credits}"
```

## Related Documentation

- `docs/requirements/accounting-logic.md` — POC accounting policy.
- `docs/requirements/reconciliation-engine.md` — reconciliation procedures and tolerance rules.
- `docs/requirements/financial-statements.md` — statement layout and aggregation rules.
- `docs/requirements/cpf-integration.md` — CPF contribution rules.
- `docs/requirements/ibkr-integration.md` — FIFO and M2M investment rules.
- Agent `financial-accounting` — for defining new accounting rules with these patterns.
