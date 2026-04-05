# IBKR Integration

Detailed requirements for the IBKR integration.

## Table of contents

- [Related documents](#related-documents)
- [Accounts in scope](#accounts-in-scope)
- [Source format](#source-format)
- [IBA account requirements](#iba-account-requirements)
- [IRA account requirements](#ira-account-requirements)
- [Classification rules](#classification-rules)
- [Reconciliation requirements](#reconciliation-requirements)
- [Lineage requirements](#lineage-requirements)

## Related documents

- [Accounting logic](accounting-logic.md)
- [Implementation roadmap](implementation-roadmap.md)
- [Source systems and lineage](source-systems-lineage.md)
- [Transaction category mapping](transaction-category-mapping.md)

## Accounts in scope

| account | id        | type                  | currency | sub-accounts       |
| ------- | --------- | --------------------- | -------- | ------------------ |
| IBA     | U1109040  | individual margin     | USD      | cash + positions   |
| IRA     | U9311815  | rollover IRA          | USD      | position only      |

Both accounts are in POC scope. IBA and IRA have different income classification and reconciliation requirements and must be handled by separate processing paths.

Although the IBKR Activity Statement for IRA technically reports separate cash and position values, the IRA is treated as a single position account in this system due to its illiquid nature. Dividends and any other cash income earned on assets within the portfolio are classified as capital gains, not as liquid cash income, because the account does not permit free withdrawal. The cash balance is treated as another security and not truly cash.

## Source format

IBKR statements are downloaded manually by the operator as CSV Activity Statements. The file naming convention follows the pattern `{account_id}_Activity_{YYYYMM}.csv`.

The CSV format is section-based, not a flat row format. Each row begins with a section name and a row type discriminator (`Header`, `Data`, or `Total`), followed by section-specific columns. The same file contains multiple named sections.

Sections used by the system:

| section             | purpose                                          |
| ------------------- | ------------------------------------------------ |
| `Statement`         | period and account metadata                      |
| `Net Asset Value`   | beginning and ending totals by asset class       |
| `Cash Report`       | net trades, deposits, and withdrawals            |

## IBA account requirements

IBA balances and income are derived top-down from the `Net Asset Value` and `Cash Report` sections. No bottom-up parsing of individual trade, dividend, interest, or commission line items is required.

Derivation from `Net Asset Value`:

```
change_cash    = NAV end cash − NAV beg cash
change_pos     = NAV change total − change_cash
```

Derivation from `Cash Report`:

```
buy_sell              = −1 × (net trades from Cash Report)
deposit_withdrawal    = mapped directly from Cash Report  [to be specified]
```

Computed outputs:

```
position_capital_gains = change_pos − buy_sell
investment_income      = change_cash + buy_sell − deposit_withdrawal
```

The deposit and withdrawal mapping from the `Cash Report` involves additional treatment and will be specified in a follow-up.

## IRA account requirements

IRA is treated as a single position account using a simpler top-down derivation. The cash balance reported in the statement is not tracked separately; the NAV total is the position balance.

Derivation from `Net Asset Value` and `Cash Report`:

```
change_pos         = NAV total end − NAV total beg
buy_sell           = deposit_withdrawal  (from Cash Report)
capital_gains_loss = change_pos − buy_sell
```

All period income — dividends, interest, commissions net — is captured in `capital_gains_loss` without sub-type breakdown, consistent with the illiquid treatment of the account.

## Classification rules

| account | component             | classification    |
| ------- | --------------------- | ----------------- |
| IBA     | position capital gains | capital gains    |
| IBA     | investment income     | investment income |
| IBA     | deposits/withdrawals  | transfer          |
| IBA     | buy/sell              | internal transfer |
| IRA     | capital gains/loss    | capital gains     |
| IRA     | deposits/withdrawals  | transfer          |

## Reconciliation requirements

- ending cash balance for IBA shall match the `Net Asset Value` cash total.
- ending position value for IBA shall match the `Net Asset Value` stock and bond total.
- combined cash and position total for IRA shall match the `Net Asset Value` total; no separate sub-account reconciliation is performed for IRA.
- Reconciliation shall be performed before any transactions are posted to HomeBudget.
- If the balance equation does not close within a tolerance of USD 0.01, the system shall halt and present the variance for user review.

## Lineage requirements

Each derived value posted to HomeBudget or the close output shall carry the following lineage fields:

| field            | description                                              |
| ---------------- | -------------------------------------------------------- |
| `period`         | statement period in `YYYY-MM` format                     |
| `derived_type`   | classification applied (e.g. `m2m`, `dividend`, `realized_gain`) |
