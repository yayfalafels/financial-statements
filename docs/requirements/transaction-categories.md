---
title: Transaction Categories
doc_type: requirements
topic_type: owner
owner: transaction-categories
scope: poc
---
# Transaction Categories

## Table of contents

- [Purpose and boundary](#purpose-and-boundary)
- [Reference documents](#reference-documents)
- [Primary scope](#primary-scope)
- [Out of scope](#out-of-scope)
- [Source of truth and ownership](#source-of-truth-and-ownership)
- [Transaction class model](#transaction-class-model)
- [Financial statement category model](#financial-statement-category-model)
- [Expense category requirements](#expense-category-requirements)
- [Income category requirements](#income-category-requirements)
- [Investment and gain or loss category requirements](#investment-and-gain-or-loss-category-requirements)
- [Income statement aggregation](#income-statement-aggregation)
- [Legacy vs new model](#legacy-vs-new-model)

## Purpose and boundary

This document defines the requirements for the transaction category model and how transactions aggregate onto the income statement. The category model is structured around transaction class, income type, expense category, and investment component type. For expense transactions, the income statement line item is determined by the expense category assigned to the transaction. For income transactions, the income statement section is determined by income type. For investment activity, income statement placement is determined by component type (mark-to-market, cash P&L, forex). Account type (balance sheet classification) is owned by account-classification.md and determines balance sheet placement, not income statement placement.

## Reference documents

- [accounting logic](accounting-logic.md)
- [account classification](account-classification.md)
- [data model](data-model.md)

## Primary scope

- Transaction class definitions and how each class determines income statement effect
- Financial statement category model for expense, income, and investment activity
- Expense category taxonomy and income statement expense line item definitions
- Category-to-income-statement mapping requirements
- Income category requirements by income type
- Investment and gain or loss category requirements by P and L component type
- Income statement aggregation rules

## Out of scope

- One-time translation from the legacy two-stage category pipeline to the new transaction-account model — documented separately in the category-account-model-translation design artifact
- User interface for managing transaction category and account updates — owned by user-interface.md
- Account asset type assignment and balance sheet placement — owned by account-classification.md
- Exception policy for missing or invalid category classifications — owned by exception-error-handling.md
- Mapping completeness gates at close time — owned by workflow-orchestration.md
- Statement lifecycle publication policy — owned by statements-lifecycle.md

## Source of truth and ownership

- The category data model is app-managed and is the source of truth for how transactions aggregate onto the income statement.
- The expense category dimension defines the income statement line items for expense-class transactions. The `gl_code` field is the canonical income statement expense line label. In the legacy Google Sheets workbook this field is named `fin_stm_category`.
- Account type, as defined in account-classification.md, governs income statement section placement for income and investment activity.
- This page owns transaction class semantics, expense category taxonomy, income category requirements, and income statement aggregation rules.
- Accounting logic owns booking policy, valuation logic, accrual timing, and special-case treatment rules that determine what transaction is produced before category roll-up is applied.
- Account classification owns asset type assignment and balance sheet placement for account balances.

## Transaction class model

Every transaction must be classified into one of the following transaction classes before income statement aggregation.

| id | transaction class | statement effect                  |
| -- | ----------------- | --------------------------------- |
| 01 | expense           | income statement expense section  |
| 02 | income            | income statement income section   |
| 03 | transfer          | no direct income statement effect |

Transaction class summaries:

- `01 expense`: consumption, operating cost, fees, taxes, and other outflows recognized as period expense. The income statement line is determined by the expense category assigned to the transaction.
- `02 income`: the broad income-side class, including personal income, CPF employer contribution, investment income, capital gains and loss, and forex translation gain or loss. The income statement section is determined by income type for personal income, and by P and L component type for investment activity.
- `03 transfer`: movement between accounts or settlement bridges that does not change period profit and loss. Transfers affect account balances but have no income statement effect.

Transaction class is a functional requirement, not a UI-only label. The system must preserve this classification in the transaction record so downstream reporting can distinguish statement-affecting activity from pure balance movement.

## Financial statement category model

The financial statements use a transaction-account model. Income statement placement is determined by transaction class and the appropriate classification dimension for each class: expense category for expenses, income type for income activity, and P and L component type for investment activity. Balance sheet placement is determined by account type, which is owned by account-classification.md.

| id | dimension           | governs                                          | ownership                  |
| -- | ------------------- | ------------------------------------------------ | -------------------------- |
| 01 | expense category    | income statement expense line for expense txns   | this doc                  |
| 02 | income type         | income statement section for income txns         | this doc                  |
| 03 | P and L component   | income statement placement for investment txns   | this doc                  |
| 04 | account type        | balance sheet section and asset classification   | account-classification.md |

The income statement is organized into sections, each driven by a different classification path.

| id | section                       | classification path                                       |
| -- | ----------------------------- | --------------------------------------------------------- |
| 01 | personal income               | income type; includes CPF employer contribution           |
| 02 | CPF contributions tracking    | balance-movement subsection; transfer class               |
| 03 | investment P and L            | P and L component type (mark-to-market, cash, forex)      |
| 04 | forex M2M on balances         | financial-statement-level derivation only                 |
| 05 | rental expenses               | expense category — rental expense group                   |
| 06 | COLE expenses                 | expense category — COLE expense group                     |
| 07 | discretionary expenses        | expense category — discretionary expense group            |

CPF employer contribution is additional income credited directly to CPF sub-accounts and aggregates into the personal income section. CPF employee contributions are transfers from the cash salary account into CPF sub-accounts; they affect balance sheet account balances only and have no net income statement effect. The CPF contributions tracking subsection is a cash-flow-like informational section that appears in both the income statement and the balance sheet, recording how salary was split between cash received and CPF sub-account credits. It does not add to or reduce net income.

Balance sheet placement is governed by account asset type and is owned by account-classification.md.

## Expense category requirements

The expense category dimension defines the income statement expense lines. Each expense category record represents a named income statement line item organized into one of three expense groups: rental, COLE expenses, or discretionary expenses.

Unified expense category table (all categories with group assignments):

| id | category_label         | gl_code              | category_group_key  |
| -- | ---------------------- | -------------------- | ------------------- |
| 01 | rental                 | rental               | rental_expenses     |
| 02 | food                   | food                 | cole_expenses       |
| 03 | transport              | transport            | cole_expenses       |
| 04 | healthcare out-of-pocket | healthcare_oop    | cole_expenses       |
| 05 | insurance              | insurance            | cole_expenses       |
| 06 | mobile                 | mobile               | cole_expenses       |
| 07 | clothing               | clothing             | cole_expenses       |
| 08 | postal services        | post                 | cole_expenses       |
| 09 | singtel internet       | singtel_internet     | cole_expenses       |
| 10 | PUB water/gas          | pub_water_gas        | cole_expenses       |
| 11 | electricity            | electricity          | cole_expenses       |
| 12 | sundries               | sundries             | cole_expenses       |
| 13 | maintenance            | maintenance          | cole_expenses       |
| 14 | fitness                | fitness              | discretionary_expenses |
| 15 | non-alcoholic drinks   | non_alcoholic_drinks | discretionary_expenses |
| 16 | alcohol                | alcohol              | discretionary_expenses |
| 17 | socializing            | socializing          | discretionary_expenses |
| 18 | it software            | it_software          | discretionary_expenses |
| 19 | it hardware            | it_hardware          | discretionary_expenses |
| 20 | books                  | books                | discretionary_expenses |
| 21 | travel                 | travel               | discretionary_expenses |
| 22 | higher education       | higher_education     | discretionary_expenses |
| 23 | projects               | projects             | discretionary_expenses |
| 24 | discretionary misc     | discretionary_misc   | discretionary_expenses |
| 25 | pets and plants        | pets_and_plants      | discretionary_expenses |
| 26 | durables               | durables             | discretionary_expenses |
| 27 | cleaning service       | cleaning_service     | discretionary_expenses |
| 28 | family gifts           | family_gifts         | discretionary_expenses |

Category record requirements:

- Each expense category record must include: `category_label`, `gl_code`, and `category_group_key` to define group membership.
- `gl_code` is the income statement line item label. It must be unique within the expense category dimension.
- `category_group_key` determines the expense group: `rental_expenses`, `cole_expenses`, or `discretionary_expenses`.
- Additional fields may include `fa_category` (bridge to normalized transaction feed, populated by category management module) and optional `fa_subcategory` and `custom_logic_note` fields.
- A transfer-designated transaction must not be assigned an expense category.
- A single expense category must not produce line items in more than one expense group.

## Income category requirements

Income categories are determined by income type. Personal income flows through the primary income account. Income types must be recognized across the following classifications. Note: account type (balance sheet concept owned by account-classification.md) determines which income statement section receives the income; income type determines what kind of income is being recognized.

| id | income type          | description  |
| -- | -------------------- | --------------------- |
| 01 | base salary          | regular salary compensation from primary employment |
| 02 | bonus                | performance or discretionary bonus payments |
| 03 | part-time            | income from secondary or contract work |
| 04 | other income         | miscellaneous income not classified above |
| 05 | taxes paid           | tax refunds or recoveries; reduces net income (negative income) |
| 06 | CPF employer contribution | employer mandatory contribution to CPF sub-accounts; recognized as income |

CPF employer contribution is income credited directly to CPF sub-accounts; it does not flow through the cash salary account but is included in total salary income. CPF employee contributions are transfers, not income; they move funds from the cash salary account into CPF sub-accounts and are recorded in the CPF contributions tracking subsection as balance-sheet transfers. CPF-specific accounting rules are defined in cpf-integration.md and accounting-logic.md.

The income category model must support income types that do not have a corresponding HomeBudget account-level transaction. CPF interest income and certain other income types are posted at financial-statement level only.

## Investment and gain or loss category requirements

Investment and gain or loss categories are determined by the P and L component type being recognized. Account type (liquid vs. illiquid, retirement vs. non-retirement) determines balance sheet placement and is owned by account-classification.md; component type determines income statement line placement for investment activity.

| id | component                  | source mechanism                                  |
| -- | -------------------------- | ------------------------------------------------- |
| 01 | mark-to-market liquid      | position revaluation, liquid investment accounts  |
| 02 | mark-to-market illiquid    | position revaluation, illiquid accounts           |
| 03 | cash profit and loss       | dividends, interest, and IB cash P and L          |
| 04 | M2M USD forex on balances  | FX rate change on USD cash balances               |

Investment and gain or loss classification rules:

- Mark-to-market adjustments are income-class activity even when they are non-cash.
- Forex translation gain or loss on balances is a financial-statement-level adjustment derived from cross-currency translation at statement time. It does not require a corresponding HomeBudget account-level ledger transaction.
- Cash P and L includes dividends, interest income, and other investment income recognized in the period.
- Capital gains treatment for retirement accounts follows the accounting policy defined in ibkr-integration.md and accounting-logic.md.

## Income statement aggregation

Income statement aggregation is determined by transaction class and the appropriate classification dimension (expense category for expenses, income type for income, P and L component type for investment), after accounting logic has produced the final recognized transaction or financial statement adjustment.

Expense aggregation:

- Expense transactions aggregate to income statement expense lines by `gl_code`.
- `gl_code` is the deterministic key for income statement line placement.
- Expense lines are further grouped into rental expenses, COLE expenses, and discretionary expenses based on `category_group_key` membership.
- This grouping distinguishes fixed committed costs (rental), essential recurring spending (COLE), and optional discretionary spending for analytical and planning purposes.

Income aggregation:

- Personal income aggregates by income type through the primary income account.
- CPF employer contribution aggregates into the personal income section by sub-account.
- CPF employee contributions are transfers and do not aggregate to income. They appear in the CPF contributions tracking subsection as informational balance-movement lines.
- Taxes paid reduces gross income.

Investment and gain or loss aggregation:

- P and L components aggregate by component type across investment accounts.
- Mark-to-market, forex M2M, and cash P and L are recognized at the financial statement layer and are not required to exist as individual HomeBudget account-level transactions.

Transfer aggregation:

- Transfer transactions do not aggregate to the income statement.

Statement completeness:

- Income statement completeness requires valid expense category coverage for all expense transactions and valid income type classification for all income transactions.
- Balance sheet completeness depends on account asset type coverage and is owned by account-classification.md.
- Statement generation has two independent governance surfaces: transaction category classification determines income statement roll-up; account asset type classification determines balance sheet roll-up. A complete monthly close requires both surfaces to be valid.

## Legacy vs new model

The requirements were updated to use a three-group expense category model (rental, COLE, discretionary) to replace the legacy two-group model (personal, household) based on expense financial characteristics rather than transaction origin. This transition was captured as design decision TC-01 in the [requirements decisions](../develop/010/design/requirements-decisions.md#decision-tc-01-expense-category-group-model-redesign) document.

**Legacy model** (prior to this requirement change):

- **Personal expenses**: spending on food, transport, entertainment, education, healthcare, and discretionary personal items
- **Household expenses**: housing (rental), utilities, insurance, household services, and durable goods

**New model** (current requirement):

- **Rental expenses**: fixed monthly housing cost (committed/non-negotiable)
- **COLE expenses**: cost-of-living expenses — essential recurring spending on food, transport, healthcare, insurance, utilities, and personal services (committed baseline)
- **Discretionary expenses**: optional spending on entertainment, travel, education, durables, and lifestyle choices (variable optional)

**Mapping from legacy to new model**: The full mapping of legacy categories to new groups is documented in the design artifact [category-account-model-translation](../develop/010/design/category-account-model-translation.md), which serves as the reference for data migration activities. For requirements purposes, the current expense category table in the "Expense category requirements" section reflects the final new model assignments.
