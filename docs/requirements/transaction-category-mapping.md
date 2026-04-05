# Transaction Category Mapping

This document defines the canonical HomeBudget transaction categories used when booking derived transactions from integration adapters. Each category label used in IBKR, CPF, and other integration documents must map to a defined entry in this table.

## Related documents

- [Account classification](account-classification.md)
- [Accounting logic](accounting-logic.md)
- [IBKR integration](ibkr-integration.md)
- [CPF integration](cpf-integration.md)

## Category schema

HomeBudget uses a hierarchical category string in the format `Parent:Child`. The categories below are the canonical values for app-owned transactions. The category schema is owned by the HomeBudget category table and should be reflected in the app JSON configuration.

## Canonical categories

| id  | derived type       | category                            |
| --- | ------------------ | ----------------------------------- |
| 01  | investment income  | `Investment:Interest`               |
| 02  | investment income  | `Investment:Profit/Loss`            |
| 03  | capital gains      | `Investment:Capital Gains`          |
| 04  | capital gains      | `Investment:Capital Gains`          |
| 05  | transfer           | _(no category — booked as transfer)_ |
| 06  | internal transfer  | _(no category — booked as transfer)_ |
| 07  | healthcare expense | `Medical:Healthcare`                |
| 08  | forex expense      | `Professional Services:Currency Conversion` |

### Category details

| id  | account type                       | description                                  |
| --- | ---------------------------------- | -------------------------------------------- |
| 01  | savings account (cash)             | interest income on IBKR cash balance         |
| 02  | savings account (cash)             | net cash income not separately categorised   |
| 03  | liquid investment, retirement      | position M2M and realised gain/loss          |
| 04  | illiquid and retirement            | all IRA income; CPF annual interest          |
| 05  | all account types                  | deposits, withdrawals, contributions         |
| 06  | savings account (cash)             | IBA buy/sell between cash and position       |
| 07  | CPF Medisave                       | Medisave gap adjustment for medical claims   |
| 08  | cost center TWH - Personal         | credit card forex processing fee reconcile   |

## Usage notes

- Categories marked as transfer do not use an expense or income category in HomeBudget; the transaction type is `transfer` between two accounts.
- `Investment:Capital Gains` covers both unrealised M2M and realised gain/loss for position accounts and retirement accounts.
- For IBA, `investment income` maps to `Investment:Profit/Loss` on the cash account; position capital gains map to `Investment:Capital Gains` on the position account.
- For IRA, all period income maps to `Investment:Capital Gains` on the position account; no cash category is used.
- For CPF, contributions are transfers; annual interest maps to `Investment:Capital Gains` on the relevant sub-account; Medisave gap adjustments map to `Medical:Healthcare`.
- The category strings above must exist in the HomeBudget category table before any transaction write is attempted. The system shall validate category existence before posting.

## Open items

- Exact `Investment:Profit/Loss` subcategory path to be confirmed against live HomeBudget category table.
- `Medical:Healthcare` subcategory path to be confirmed against live HomeBudget category table.
- Any additional categories needed for bill payment and shared cost transactions are to be defined in the bill payment requirements.
