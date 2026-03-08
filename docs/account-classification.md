# Account classification

- [Overview](#overview)
- [Aims](#aims)
- [Account definitions](#account-definitions)
- [HomeBudget Account types](#homebudget-account-types)
	- [Budget: cost center `TWH - Personal`](#budget-cost-center-twh---personal)
- [Cash](#cash)
- [Credit](#credit)
- [External](#external)
- [Financial statement asset types](#financial-statement-asset-types)
	- [Asset type mapping](#asset-type-mapping)
	- [Common to all accounts](#common-to-all-accounts)
	- [cash and bank accounts](#cash-and-bank-accounts)
	- [credit](#credit-1)
	- [savings account](#savings-account)
	- [liquid investments](#liquid-investments)
	- [illiquid and retirement](#illiquid-and-retirement)

## Overview

The account classification system defines the different types of accounts in the HomeBudget system, such as cash, credit, and cost center accounts. It also defines how these accounts are interpreted on financial statements and the rules for transaction categorization and balance management for each account type.

## Aims

The general aim of the account classification system is to accurately reflect current financial position, and track changes and activity by applying Generally Accepted Accounting and Reporting Principles (GAARP) to personal finances, with simplifications adaptated to the needs of personal finances for single household.

## Account definitions

The mapping logic both between data sources and classification, should ultimately be defined in a database, and intermediate solution local JSON  file `data/monthly-closing/accounts.json`. For now the information exists in disparate sources in the HomeBudget database and financial statements google sheets workbook. In a separate step this consolidated accounts.json should be schema defined and then populated.

For investments which have combinations of mixes of asset types such as cash accounts for cash inflows and outflows, and illiquid assets which can appreciate or depreciate in value, the different components of the investment are tracked in separate accounts, such as a cash account for the cash balance and a position account for the value of the investment. 

## Scope of accounts

The financal statements google sheets workbook contains the definitive complete comprehensive list of accounts used for financial statements reporting and net worth tracking, which includes both HomeBudget accounts, plus a few additional off-HB accounts only tracked in the financial statements workbook for reporting purposes. 

Ultimately the financial statements workbook should be deprecated and migrated to a bespoke application with a database backend which this app aims to deliver.

| cat | HomeBudget | financial statements wkb | included | description |
| --- | ---------- | ----------------------- | -------- | ----------- |
| 01  | X          | X                        | yes      | active tracked accounts |
| 02  | X          |                          | no       | legacy accounts no longer in use, such as `TWH - Common` |
| 03  |            | X                        | yes       | off-HB accounts only tracked in financial statements workbook, for reporting purposes |

## HomeBudget Account types

The HomeBudget account type is a property on the Account table in the HB Database.

| id | HB account type      | example           | description                                         |
| -- | -------------------- | ----------------- | --------------------------------------------------- |
| 01 | Budget               | TWH - Personal    | cost center                                         |
| 02 | Cash                 | TWH DBS Multi SGD | real wallet or bank account                         |
| 03 | Credit               | TWH UOB One SGD   | credit card, loan or personal line of credit        |
| 04 | External             | IB POSITION USD   | anything which is not related to personal savings*  |

**Personal savings** = Personal income - personal expenses. This is tracked separately from investment related income and expenses.

### Budget: cost center `TWH - Personal`

- `TWH - Personal` is the main cost center for all personal expenses. It is a special account that serves as a consolidated cost center for all personal expenses. It is not a real wallet or bank account, but rather an accounting construct to track personal expenses in one place. 
- the month-end balance of `TWH - Personal` should always zero, so that the net of transfers from actual accounts matches the sum of expenses.
- other legacy cost centers exist in the HomeBudget and financial statements workbooks but are no longer in use, such as `TWH - Common`

## Cash

Cash accounts are real wallets or bank accounts that track the balance and transactions for a specific financial entity. They can be used as payment methods for personal expenses, and they can also earn interest income. Examples of cash accounts include `TWH DBS Multi SGD`, `TWH CITI USD`, and `TWH IB USD`.
When any account is used as a payment method for an expense, it is booked as a transfer from the cash account to the cost center `TWH - Personal`, and the actual expense is booked in `TWH - Personal`.

Cash accounts should not have negative balances, although the HomeBudget system does not enforce this rule. They can have ledger negative balances within a month, but the month-end balance should be non-negative.

## Credit

Credit works in similar way as cash, but with negative balances. Credit accounts include credit cards, loans, and personal lines of credit. Examples of credit accounts include `TWH UOB One SGD` and `30 CC Hashemis`. When a credit account is used as a payment method for an expense, it is booked as a transfer from the credit account to the cost center `TWH - Personal`, and the actual expense is booked in `TWH - Personal`.

Investment savings accounts are classified either as cash or credit, depending on the account rules whether the account can have negative balance or not. 

## External

All other accounts are classified as external, such as investment position accounts.

## Financial statement asset types

| id | asset subcategory | balance sheet asset type |
| -- | ----------------- | ------------------------ |
| 01 | wallet cash       | cash and bank accounts   |
| 02 | bank account      | cash and bank accounts   |
| 03 | savings account   | cash and bank accounts   |
| 04 | credit card       | credit                   |
| 05 | other credit      | credit                   |
| 06 | investment        | liquid investments       |
| 07 | retirement        | illiquid and retirement  |

### Asset type mapping

The account asset type mapping can currently be found in the financial statements google sheets workbook `gsheet/financial-statements.json` range `accounts`. 

| field         | example value     | notes                                      |
| --------------|-------------------|--------------------------------------------|
| id            | TWH DBS MULTI SGD | name used in financial statements workbook |
| type          | bank account      | asset subcategory                          |
| owner         | TWH               | not used, only TWH owner accounts in scope |
| name          | DBS MULTI         | account tag                                |
| currency      | SGD               | currency                                   |
| HB account    | TWH DBS Multi SGD | HomeBudget account name                    |
| stm account   | TWH DBS Multi SGD | account name in statement digital twin     |

### Common to all accounts

- depletion logic ending balance = beginning balance + inflows - outflows
- can have positive or negative balances within a month
- allowed transaction categories: transfers in and out
- fixed currency per account

### cash and bank accounts

- non-negative month-end balances
- are considered fully liquid
- bank accounts, physical cash, and virtual stored value accounts ie Amazon wallet
- subcategories: `wallet cash`, `bank account`, `savings account`
- allowed transaction categories include all cash-related income, excluding non-cash income such as capital gains and depreciation.
- can be a payment method

**Restricted income: TWH DBS Multi SGD, TWH CITI**

- all non-capital gains SGD income is booked into `TWH DBS Multi SGD`. 
- all non-capital gains USD income not already booked in investment accounts is booked into `TWH CITI`.
- all interest-earning bank accounts can book only interest income, but only the designated accounts TWH DBS Multi SGD or TWH CITI can book dividends.

### credit

- are considered fully liquid
- same rules as cash and bank accounts, but with negative balances.  
- also includes pseudo credit accounts used for accounting purposes such as 30 CC Hashemis as credit extended to other 3rd parties.
- allowed transaction categories limited only transfers in and out
- subcategories: `credit card`, `other credit`
- can be a payment method

### savings account

- cash accounts for investment accounts
- can have positive or negative balances depending on account specific rules
- are considered fully liquid
- should not be used as a payment method for personal or non-investment related expenses, with exception of CPF Medisave which is used for medical expenses payment directly from the account, but not for other expenses.
- intermediate settlement between investments and cash accounts, where deposits and withdrawals from investments are booked as transfers between the cash account and the investment account, and trades purchases/sales are booked as transfers between the cash account and the investment position accounts 
- allowed transactions include all cash-related investment income such as dividends, interest, profit/loss, but not non-cash such as capital gains, mark-to-market and depreciation. cash forex translation effects are booked as a misc profit/loss in the cash account to represent cash in multiple currencies translation into the account reporting currency.

**IBKR cash account**

- The IBKR account is divided into cash `TWH IB USD` and position `IB POSITION USD`.
- The IBKR cash account can have either positive or negative balance.  
- IBKR cash account can book all non-capital gains investment related income
- IBKR position account books all capital gain/loss and mark-to-market (M2M).
- Since the IBKR cash account can be either positive or negative, when it is positive it is classified as cash and bank account, and when it is negative it is classified as credit.  All other accounts have a fixed classification regardless of balance

**CPF Medisave**

CPF Medisave has properties of both cash bank account and retirement account.  It has properties of cash bank account because normal expenses are paid directly from this account. It has properties of retirement account because it is illiquid and earns interest.

### liquid investments

- subcategories: `investment`
- are considered fully liquid
- includes all non-retirement investment accounts such as IBKR position.
- allowed transactions include non-cash related investment changes in valuation: capital gains/loss, mark-to-market (M2M) and depreciation
- transfers in/out represent sale/purchases and are restricted usually to a few set of linked cash accounts.

### illiquid and retirement

- subcategories: `retirement`
- are considered illiquid
- includes all retirement accounts such as CPF and IRA
- allowed transactions same as liquid investments, however actual cash income such as dividends and interest are also booked as capital gains/loss due to the illiquid nature of the account
- sales/purchases are not booked and are tracked elsewhere, so transfers in or out represent contributions or withdrawals. Although there are rules on withdrawals and early withdrawal penalties, this is not captured in the program logic and only noted when such fees apply later analysis may link the two observations after-the-fact.