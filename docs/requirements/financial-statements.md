---
title: Financial Statements
doc_type: requirements
topic_type: owner
owner: financial-statements
scope: poc
---
# Financial statements

## Table of contents

- [Overview](#overview)
- [Reference documents](#reference-documents)
- [Statements produced](#statements-produced)
- [Statement layouts](#statement-layouts)
- [Income statement](#income-statement)
  - [Income statement sections](#income-statement-sections)
  - [Personal income section](#personal-income-section)
  - [CPF contributions tracking section](#cpf-contributions-tracking-section)
  - [Investment P and L section](#investment-p-and-l-section)
  - [Forex M2M on balances section](#forex-m2m-on-balances-section)
  - [Expense sections: rental, COLE, and discretionary](#expense-sections-rental-cole-and-discretionary)
  - [Expense breakdown layout](#expense-breakdown-layout)
  - [Net income](#net-income)
- [Balance sheet](#balance-sheet)
  - [Balance sheet sections](#balance-sheet-sections)
  - [Net cash transfers section](#net-cash-transfers-section)
- [Roll-up and aggregation rules](#roll-up-and-aggregation-rules)
- [Statement completeness](#statement-completeness)

## Overview

The financial statements system produces a monthly income statement and balance sheet for the TWH household. The income statement covers all recognized income, investment activity, and expenses for the period. The balance sheet reflects the net worth position at the end of the period. Both statements are derived from the same underlying transaction and account data using the classification rules defined in the account and category models.

## Reference documents

- [account-classification.md](account-classification.md): defines account types, asset subcategories, and balance sheet placement rules for account balances.
- [transaction-categories.md](transaction-categories.md): defines transaction class, expense category taxonomy, income category requirements, and income statement aggregation rules.
- [accounting-logic.md](accounting-logic.md): defines booking policy, valuation logic, accrual timing, and special-case treatment rules that produce the recognized transactions consumed by statement roll-up.

## Statements produced

The system produces two statements per close period.

| id | statement         | coverage                                              |
| -- | ----------------- | ----------------------------------------------------- |
| 01 | income statement  | income, investment activity, and expenses for period  |
| 02 | balance sheet     | net worth position at end of period                   |

Both statements are denominated in SGD. Foreign currency balances and transactions are translated at the period-end rate. Forex translation effects are shown as a separate income statement line. Translation methodology is defined in accounting-logic.md.

## Statement layouts

The income statement presents top-to-bottom: income sections, then expense sections, then a net income summary.

```
Income statement
│
├── Personal income
│   ├── base salary
│   ├── bonus
│   ├── part-time
│   ├── other income
│   ├── CPF employer contribution
│   ├── taxes paid
│   └── net personal income
│
├── CPF contributions tracking  [informational — no income statement effect]
│   ├── CPF employee contribution
│   ├── CPF OA allocation
│   ├── CPF SA allocation
│   └── CPF MS allocation
│
├── Investment P and L
│   ├── M2M liquid
│   ├── M2M illiquid
│   └── cash profit and loss
│
├── Forex M2M on balances
│   └── M2M USD forex on balances
│
├── Personal expenses
│   ├── COLE
│   │   ├── food
│   │   ├── transport
│   │   ├── healthcare OOP
│   │   ├── insurance
│   │   ├── mobile
│   │   ├── clothing
│   │   ├── post
│   │   └── COLE sub-total
│   ├── Discretionary
│   │   ├── fitness
│   │   ├── non alcoholic drinks
│   │   ├── alcohol
│   │   ├── socializing
│   │   ├── IT software
│   │   ├── IT hardware
│   │   ├── books
│   │   ├── travel
│   │   ├── higher education
│   │   ├── projects
│   │   ├── discretionary misc
│   │   └── discretionary sub-total
│   └── total personal expenses
│
├── Household expenses
│   ├── Rental
│   │   ├── rental
│   │   └── rental sub-total
│   ├── COLE
│   │   ├── Singtel internet
│   │   ├── PUB water/gas
│   │   ├── electricity
│   │   ├── sundries
│   │   ├── maintenance
│   │   └── COLE sub-total
│   ├── Discretionary
│   │   ├── pets and plants
│   │   ├── durables
│   │   ├── cleaning service
│   │   ├── family gifts
│   │   └── discretionary sub-total
│   └── total household expenses
│
└── Net income
    ├── net personal income
    ├── investment P and L
    ├── forex M2M on balances
    ├── less: rental
    ├── less: COLE expenses
    ├── less: discretionary expenses
    └── net income
```

The balance sheet opens with net worth as the top-level summary figure, followed by the asset sections that derive it. Net cash transfers appears as a supplementary reconciliation section below the primary asset sections.

```
Balance sheet
│
├── Net worth  [summary — shown at top]
│
├── Cash and bank accounts
│   └── [account lines]
│
├── Credit
│   └── [account lines]
│
├── Liquid investments
│   └── [account lines]
│
├── Illiquid and retirement
│   └── [account lines]
│
└── Net cash transfers  [supplementary reconciliation — shown below asset sections]
    └── [transfer lines]
```

## Income statement

### Income statement sections

The income statement is organized into sections. Each section is fed by a specific classification path determined by transaction class, account type, and, for expense transactions, the expense category assigned to the transaction. Classification paths are defined in transaction-categories.md.

| id | section                    | income statement effect      |
| -- | -------------------------- | ---------------------------- |
| 01 | personal income            | positive — increases net     |
| 02 | CPF contributions tracking | informational — no IS effect |
| 03 | investment P and L         | positive or negative         |
| 04 | forex M2M on balances      | positive or negative         |
| 05 | rental expenses            | negative — decreases net     |
| 06 | COLE expenses              | negative — decreases net     |
| 07 | discretionary expenses     | negative — decreases net     |

Sections are presented in this order in the rendered income statement. Net income is derived after all sections are applied.

### Personal income section

Personal income aggregates all recognized income for the period through the primary income account and CPF employer sub-accounts.

| id | line item                 | source                                 |
| -- | ------------------------- | -------------------------------------- |
| 01 | base salary               | income-class txns, income account      |
| 02 | bonus                     | income-class txns, income account      |
| 03 | part-time                 | income-class txns, income account      |
| 04 | other income              | income-class txns, income account      |
| 05 | CPF employer contribution | CPF employer sub-account credits       |
| 06 | taxes paid                | income-class txns, income account      |
| 07 | net personal income       | sum of 01–05 less 06                   |

Taxes paid reduces gross income and is deducted within this section to produce net personal income. Income classification rules and CPF employer contribution treatment are defined in transaction-categories.md.

### CPF contributions tracking section

The CPF contributions tracking section is an informational subsection that appears in the income statement as a cash-flow-like view of salary distribution. It does not add to or reduce net income.

| id | line item                  | description                                      |
| -- | -------------------------- | ------------------------------------------------ |
| 01 | CPF employee contribution  | total CPF deduction from salary                  |
| 02 | CPF OA allocation          | share credited to Ordinary Account               |
| 03 | CPF SA allocation          | share credited to Special Account               |
| 04 | CPF MS allocation          | share credited to Medisave Account               |

The employee contribution total equals the sum of OA, SA, and MS allocations. These are transfer-class movements that affect balance sheet account balances only. Transfer class treatment and CPF sub-account rules are defined in transaction-categories.md and cpf-integration.md.

### Investment P and L section

Investment P and L aggregates all recognized investment activity for the period, including mark-to-market adjustments, cash profit and loss, and forex translation effects on investment positions.

| id | line item               | source mechanism                               |
| -- | ----------------------- | ---------------------------------------------- |
| 01 | M2M liquid              | position revaluation, liquid investment accts  |
| 02 | M2M illiquid            | position revaluation, illiquid accounts        |
| 03 | cash profit and loss    | dividends, interest, and IB cash P and L       |

Mark-to-market adjustments are non-cash and are posted at the financial statement layer. They do not require corresponding HomeBudget account-level transactions. Valuation methodology is defined in accounting-logic.md. Account type rules for investment accounts are defined in account-classification.md.

### Forex M2M on balances section

Forex M2M on balances is a financial-statement-level derivation that recognizes the unrealized translation effect of holding foreign currency balances.

| id | line item              | source mechanism                                |
| -- | ---------------------- | ----------------------------------------------- |
| 01 | M2M USD forex on balances | FX rate change applied to USD cash balances  |

This section contains a single derived line. It does not require a corresponding HomeBudget transaction. Translation methodology is defined in accounting-logic.md.

### Expense sections: rental, COLE, and discretionary

The income statement contains three expense sections. Each section corresponds to a category group and presents individual expense line items and a section total. Category group assignment for each expense category is defined in transaction-categories.md.

| id | section                | classification rule                                       |
| -- | ---------------------- | --------------------------------------------------------- |
| 05 | rental expenses        | `gl_code` = `rental`                                      |
| 06 | COLE expenses          | expense categories where `COLE` = yes                     |
| 07 | discretionary expenses | expense categories where `COLE` = no, excluding rental    |

Rental is a single line item presented as its own section because it represents a fixed, committed cost that is analytically distinct from cost-of-living and discretionary spending.

COLE — cost-of-living expenses — are categories flagged with `COLE = yes` in the expense category dimension. These represent recurring non-discretionary spending required to maintain the household standard of living.

Discretionary expenses are all expense categories where `COLE = no`, excluding rental. These represent spending that can vary at the user's discretion.

### Expense breakdown layout

The income statement renders expense sections in this order: rental, COLE, then discretionary. Each section presents individual category line items and a section total.

Rental expenses section layout:

| id    | line item             | type          |
| ----- | --------------------- | ------------- |
| 05.01 | rental                | detail line   |
| 05.02 | total rental expenses | section total |

COLE expenses section layout:

| id    | line item              | type          |
| ----- | ---------------------- | ------------- |
| 06.01 | food                   | detail line   |
| 06.02 | transport              | detail line   |
| 06.03 | healthcare OOP         | detail line   |
| 06.04 | insurance              | detail line   |
| 06.05 | mobile                 | detail line   |
| 06.06 | clothing               | detail line   |
| 06.07 | post                   | detail line   |
| 06.08 | Singtel internet       | detail line   |
| 06.09 | PUB water/gas          | detail line   |
| 06.10 | electricity            | detail line   |
| 06.11 | sundries               | detail line   |
| 06.12 | maintenance            | detail line   |
| 06.13 | total COLE expenses    | section total |

Discretionary expenses section layout:

| id    | line item                    | type          |
| ----- | ---------------------------- | ------------- |
| 07.01 | fitness                      | detail line   |
| 07.02 | non alcoholic drinks         | detail line   |
| 07.03 | alcohol                      | detail line   |
| 07.04 | socializing                  | detail line   |
| 07.05 | IT software                  | detail line   |
| 07.06 | IT hardware                  | detail line   |
| 07.07 | books                        | detail line   |
| 07.08 | travel                       | detail line   |
| 07.09 | higher education             | detail line   |
| 07.10 | projects                     | detail line   |
| 07.11 | discretionary misc           | detail line   |
| 07.12 | pets and plants              | detail line   |
| 07.13 | durables                     | detail line   |
| 07.14 | cleaning service             | detail line   |
| 07.15 | family gifts                 | detail line   |
| 07.16 | total discretionary expenses | section total |

The detail line order within each section follows the category table order defined in transaction-categories.md. Section totals are derived rows produced by the statement rendering layer and do not correspond to individual transactions.

### Net income

Net income is derived at the bottom of the income statement after all sections are applied.

| id | component                      |
| -- | ------------------------------ |
| 01 | net personal income            |
| 02 | investment P and L             |
| 03 | forex M2M on balances          |
| 04 | less: rental                   |
| 05 | less: COLE expenses            |
| 06 | less: discretionary expenses   |
| 07 | net income                     |

The three expense deduction lines — rental, COLE, and discretionary — represent the totals of their respective expense sections. CPF contributions tracking does not contribute to net income.

## Balance sheet

### Balance sheet sections

The balance sheet opens with net worth as the top-level summary figure. The four asset sections below it are the primary balance sheet sections; their section totals derive net worth. Asset type classification for each account is defined in account-classification.md.

| id | section                 | asset types included                       |
| -- | ----------------------- | ------------------------------------------ |
| 01 | cash and bank accounts  | wallet cash, bank account, savings account |
| 02 | credit                  | credit card, other credit                  |
| 03 | liquid investments      | investment                                 |
| 04 | illiquid and retirement | retirement                                 |

Net worth equals the sum of sections 01 through 04. It is shown as the header figure above the asset sections, not as a trailing line at the bottom. Each section presents one line per account. Balance sheet placement rules for each account are defined in account-classification.md.

### Net cash transfers section

The net cash transfers section records the net movement of funds between accounts for the period. This includes cash account-to-account transfers and investment buy and sell activity. These movements affect individual account balances within the cash and investment sections and are reflected here as a reconciliation view.

Net cash transfers do not change net worth. They are informational and appear as a reconciliation subsection below the primary balance sheet sections.

## Roll-up and aggregation rules

Income statement roll-up:

- Expense transactions aggregate to income statement expense lines by `gl_code` key. Each expense category is assigned to one of three sections — rental, COLE, or discretionary — via its `category_group_key`. The expense category table in transaction-categories.md defines the full category list and group assignments.
- Income transactions aggregate by income type through the designated income account. Income type definitions are in transaction-categories.md.
- Investment activity aggregates by P and L component across investment accounts. Component definitions are in transaction-categories.md.
- Forex M2M on balances is derived at the financial statement layer from period-end FX rates applied to foreign currency cash balances. Methodology is in accounting-logic.md.
- Transfer-class transactions have no income statement effect and are excluded from all income and expense aggregations.

Balance sheet roll-up:

- Account balances aggregate to balance sheet sections by account asset type. Asset type assignment rules are in account-classification.md.
- Mark-to-market adjustments update account balances at period-end before balance sheet production. M2M methodology is in accounting-logic.md.
- Foreign currency account balances are translated to SGD at the period-end rate before aggregation.
- The IBKR cash account is classified as cash and bank when its balance is positive and as credit when its balance is negative. This is the only account with a balance-dependent classification.

## Statement completeness

A complete monthly close requires both surfaces to be valid before statements are published.

- Income statement completeness requires valid expense category coverage for all expense-class transactions and valid income type classification for all income-class transactions. Missing `gl_code` assignments block income statement roll-up. Exception handling policy is defined in exception-error-handling.md.
- Balance sheet completeness requires valid asset type coverage for all accounts in scope. Missing asset type assignments block balance sheet roll-up and are governed by account-classification.md.
- Statement lifecycle publication gates and close-readiness checks are defined in statements-lifecycle.md and workflow-orchestration.md.
