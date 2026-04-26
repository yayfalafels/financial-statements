---
title: CPF Integration
doc_type: requirements
topic_type: owner
owner: cpf-integration
scope: poc
---
# CPF Integration

Detailed requirements for the CPF integration.

## Table of contents

- [Related documents](#related-documents)
- [Accounts in scope](#accounts-in-scope)
- [Input source](#input-source)
- [Contribution requirements](#contribution-requirements)
- [Interest income requirements](#interest-income-requirements)
- [Medisave transaction requirements](#medisave-transaction-requirements)
- [Reconciliation requirements](#reconciliation-requirements)
- [Lineage requirements](#lineage-requirements)

## Related documents

- [Accounting logic](accounting-logic.md)
- [Workflow orchestration](workflow-orchestration.md)
- [Source systems and lineage](source-systems-lineage.md)
- [Transaction categories](transaction-categories.md)

## Inherits from accounting policy

- This page inherits global accounting policy from accounting-logic.md.

## Integration-specific overrides

- CPF input source is Google Sheets UI for current POC.
- CPF annual interest handling is integration-specific.

## No override areas

- Global reconciliation policy ownership remains in accounting-logic.md and reconciliation-engine.md.
- Global tolerance policy values remain in reconciliation-engine.md.

## Accounts in scope

| sub-account | abbreviation | description                                   |
| ----------- | ------------ | --------------------------------------------- |
| Ordinary    | OA           | primary savings; used for housing, investment |
| Special     | SA           | retirement savings; restricted withdrawals    |
| Medisave    | MA           | healthcare savings; restricted to medical use |

All three sub-accounts are in POC scope.

## Input source

CPF data is entered manually by the user during the data ingest stage via the closing-session Google Sheets workbook. There is no downloaded statement or API connection for POC. The user reads balances from the CPF online portal and enters them along with any known transactions for the period.

The GS UI input shall support the following fields per sub-account per period:

- `period`: `YYYY-MM`
- `sub_account`: `OA`, `SA`, or `MA`
- `opening_balance`: user-entered balance at start of period
- `closing_balance`: user-entered balance at end of period
- `contributions`: employer and employee contribution amounts for the period
- `interest`: interest credited for the period, if applicable
- `transactions`: list of additional transactions (Medisave only in typical periods)
- `notes`: free-text field for user observations or exception reasons

## Contribution requirements

CPF contributions are monthly fixed amounts derived from salary. Employer and employee portions result in credits to OA, SA, and MA according to CPF contribution rate rules.

- The system shall accept monthly contribution amounts per sub-account as user-entered GS UI inputs.
- Contributions shall be treated as transfers into CPF from the salary source account.
- The system shall not calculate contribution splits automatically in POC; the user enters the final credited amounts per sub-account.
- Contributions shall be validated as non-negative values.

## Interest income requirements

CPF interest is credited annually rather than monthly. Annual interest income is in scope for POC.

CPF official FAQ states interest is computed monthly and credited to accounts by the following year, with annual compounding.

- The system shall accept interest income per sub-account as an user-entered value in the period GS UI entry.
- Interest income shall be classified as investment income and booked as a credit to the relevant sub-account.
- If interest is not applicable for the current period (non-annual period), the `interest` field shall be zero or absent; the system shall treat absent as zero.
- The system shall flag interest entries greater than zero outside of the expected annual credit period for user confirmation before posting.
- Expected annual credit period for user validation is year-end through 1 January of the following year.

## Medisave transaction requirements

Medisave sub-account (MA) may have outflows for medical claims that do not appear as monthly contributions. These follow a balance-reconcile pattern similar to a digital wallet.

- The system shall compare the user-entered closing balance against the expected balance derived from opening balance, contributions, and interest.
- If a gap exists, the system shall present the variance and prompt the user to investigate and provide an explanation or manual transaction entry to close the gap.
- Manual transactions logged to close Medisave gaps shall be classified as healthcare expense.
- The system shall require user confirmation before any Medisave gap adjustment is posted.

## Reconciliation requirements

- The system shall verify the computed closing balance for each sub-account against the user-entered closing balance.
- The balance equation for each sub-account is: `closing_balance = opening_balance + contributions + interest + transactions`.
- If the computed closing balance does not match the user-entered closing balance, the system shall present the variance per sub-account before proceeding.
- Reconciliation shall pass for all three sub-accounts before CPF transactions are posted to HomeBudget.
- OA and SA gaps that are not explained by any entered transaction shall be flagged as unresolved and block close until the user provides a resolution note.

## Lineage requirements

Each value posted to HomeBudget or the close output shall carry the following lineage fields:

| id | field         | description                                                                         |
| -- | ------------- | ----------------------------------------------------------------------------------- |
| 01 | `period`      | period in `YYYY-MM` format                                                          |
| 02 | `sub_account` | CPF sub-account identifier: `OA`, `SA`, or `MA`                                     |
| 03 | `input_type`  | type of entry: `contribution`, `interest`, `transaction`, `adjustment`             |
| 04 | `user_note`   | free-text note from user GS UI input, if provided                                   |
| 05 | `derived_type`| classification applied (e.g. `transfer`, `investment_income`, `healthcare_expense`) |
