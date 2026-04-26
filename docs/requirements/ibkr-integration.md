---
title: IBKR Integration
doc_type: requirements
topic_type: owner
owner: ibkr-integration
scope: poc
---
# IBKR Integration

Detailed requirements for the IBKR integration.

## Table of contents

- [Related documents](#related-documents)
- [Accounts in scope](#accounts-in-scope)
- [Source format](#source-format)
- [IBA account requirements](#iba-account-requirements)
- [IRA account requirements](#ira-account-requirements)
- [Classification rules](#classification-rules)
- [Validation and close-gate requirements](#validation-and-close-gate-requirements)
- [Lineage requirements](#lineage-requirements)

## Related documents

- [Accounting logic](accounting-logic.md)
- [Implementation roadmap](implementation-roadmap.md)
- [Source systems and lineage](source-systems-lineage.md)
- [Transaction category mapping](transaction-category-mapping.md)
- [Transaction categories](transaction-categories.md)

## Inherits from accounting policy

- This page inherits global accounting policy from accounting-logic.md.

## Integration-specific overrides

- IRA income treatment is constrained to capital-gains classification due to account liquidity behavior.
- IBA top-down derivation from NAV and Cash Report is integration-specific.
- IBKR accounting model ownership is on this page, including IBA and IRA derivation and close-gate validation rules.

## No override areas

- Global reconciliation workflow policy remains in reconciliation-engine.md.
- Global tolerance policy values remain in reconciliation-engine.md.

## Accounts in scope

| account | id       | type              | currency | sub-accounts      |
| ------- | -------- | ----------------- | -------- | ----------------- |
| IBA     | U1109040 | individual margin | USD      | cash + positions  |
| IRA     | U9311815 | rollover IRA      | USD      | position only     |

Both accounts are in POC scope. IBA and IRA have different income classification and accounting-model derivation requirements and must be handled by separate processing paths.

Although the IBKR Activity Statement for IRA technically reports separate cash and position values, the IRA is treated as a single position account in this system due to its illiquid nature. Dividends and any other cash income earned on assets within the portfolio are classified as capital gains, not as liquid cash income, because the account does not permit free withdrawal. The cash balance is treated as another security and not truly cash.

## Source format

IBKR statements are downloaded manually by the user as CSV Activity Statements. The file naming convention follows the pattern `{account_id}_Activity_{YYYYMM}.csv`.

The CSV format is section-based, not a flat row format. Each row begins with a section name and a row type discriminator (`Header`, `Data`, or `Total`), followed by section-specific columns. The same file contains multiple named sections.

Sections used by the system:

| section           | purpose                                    |
| ----------------- | ------------------------------------------ |
| `Statement`       | period and account metadata                |
| `Net Asset Value` | beginning and ending totals by asset class |
| `Cash Report`     | cash movement rows used for derivation     |
| `Change in NAV`   | cross-check for deposits and withdrawals   |

## IBA account requirements

IBA balances and income are derived top-down from the `Net Asset Value` and `Cash Report` sections. No bottom-up parsing of individual trade, dividend, interest, or commission line items is required.

Posting model for generated HomeBudget entries:

- Default posting is end-of-period aggregate entries for derived components.
- Withdrawals are posted at transaction level because they link directly to bank-account transactions used in transaction-level reconciliation.
- IBKR mark-to-market entries are generated as transactions in the IBKR flow.

Derivation from `Net Asset Value`:

```
change_cash    = NAV end cash âˆ’ NAV beg cash
change_pos     = NAV change total âˆ’ change_cash
```

Derivation from `Cash Report`:

```
buy_sell              = -1 x (net trades from Cash Report)
deposit_withdrawal    = deposits + withdrawals from Cash Report
```

Cash Report mapping rules from inspected Activity Statement samples:

- Use section `Cash Report`, row type `Data`, and currency `Base Currency Summary`.
- `deposits` source row is `Deposits`, using the `Total` value.
- `withdrawals` source row is `Withdrawals`, using the `Total` value.
- `deposit_withdrawal = deposits + withdrawals`.
- `net trades from Cash Report = Trades (Sales) + Trades (Purchase)`.
- `buy_sell = -1 x net trades from Cash Report`.
- If `Deposits` or `Withdrawals` rows are not present for the month, treat the missing value as `0.00`.
- Cross-check: `deposit_withdrawal` should match `Change in NAV` row `Deposits & Withdrawals` within USD `0.01`.

Computed outputs:

```
position_capital_gains = change_pos - buy_sell
investment_income      = change_cash + buy_sell - deposit_withdrawal
```

## IRA account requirements

IRA is treated as a single position account using a simpler top-down derivation. The cash balance reported in the statement is not tracked separately; the NAV total is the position balance.

Derivation from `Net Asset Value` and `Cash Report`:

```
change_pos         = NAV total end - NAV total beg
buy_sell           = deposit_withdrawal  (from Cash Report)
capital_gains_loss = change_pos - buy_sell
```

All period income â€” dividends, interest, commissions net â€” is captured in `capital_gains_loss` without sub-type breakdown, consistent with the illiquid treatment of the account.

## Classification rules

| account | component              | classification    |
| ------- | ---------------------- | ----------------- |
| IBA     | position capital gains | capital gains     |
| IBA     | investment income      | investment income |
| IBA     | deposits/withdrawals   | transfer          |
| IBA     | buy/sell               | internal transfer |
| IRA     | capital gains/loss     | capital gains     |
| IRA     | deposits/withdrawals   | transfer          |

## Validation and close-gate requirements

- Generated ending cash balance for IBA shall match the `Net Asset Value` cash total.
- Generated ending position value for IBA shall match the `Net Asset Value` stock and bond total.
- Generated combined total for IRA shall match the `Net Asset Value` total, with no separate cash sub-account treatment.
- Validation shall run before any generated transactions are posted to HomeBudget.
- If any balance equation fails to close within tolerance USD 0.00 at precision USD 0.01, the system shall halt posting and present the variance for investigation.
- IBKR flow is generation-driven. The system shall not create reconciliation adjustments for IBKR accounts.

## Lineage requirements

Each derived value posted to HomeBudget or the close output shall carry the following lineage fields:

| field          | description                                                      |
| -------------- | ---------------------------------------------------------------- |
| `period`       | statement period in `YYYY-MM` format                             |
| `derived_type` | classification applied (e.g. `m2m`, `dividend`, `realized_gain`) |
