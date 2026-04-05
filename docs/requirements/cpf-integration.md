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
- [Current workflow](current-workflow.md)
- [Source systems and lineage](source-systems-lineage.md)
- [Transaction category mapping](transaction-category-mapping.md)

## Accounts in scope

| sub-account | abbreviation | description                                      |
| ----------- | ------------ | ------------------------------------------------ |
| Ordinary    | OA           | primary savings; used for housing, investment    |
| Special     | SA           | retirement savings; restricted withdrawals       |
| Medisave    | MA           | healthcare savings; restricted to medical use    |

All three sub-accounts are in POC scope.

## Input source

CPF data is entered manually by the operator via JSON. There is no downloaded statement or API connection for POC. The operator reads balances from the CPF online portal and enters them along with any known transactions for the period.

The JSON input format shall support the following fields per sub-account per period:

- `period`: `YYYY-MM`
- `sub_account`: `OA`, `SA`, or `MA`
- `opening_balance`: operator-entered balance at start of period
- `closing_balance`: operator-entered balance at end of period
- `contributions`: employer and employee contribution amounts for the period
- `interest`: interest credited for the period, if applicable
- `transactions`: list of additional transactions (Medisave only in typical periods)
- `notes`: free-text field for operator observations or exception reasons

## Contribution requirements

CPF contributions are monthly fixed amounts derived from salary. Employer and employee portions result in credits to OA, SA, and MA according to CPF contribution rate rules.

- The system shall accept monthly contribution amounts per sub-account as operator-entered JSON inputs.
- Contributions shall be treated as transfers into CPF from the salary source account.
- The system shall not calculate contribution splits automatically in POC; the operator enters the final credited amounts per sub-account.
- Contributions shall be validated as non-negative values.

## Interest income requirements

CPF interest is credited annually rather than monthly. Annual interest income is in scope for POC.

- The system shall accept interest income per sub-account as an operator-entered value in the period JSON input.
- Interest income shall be classified as investment income and booked as a credit to the relevant sub-account.
- If interest is not applicable for the current period (non-annual period), the `interest` field shall be zero or absent; the system shall treat absent as zero.
- The system shall flag interest entries greater than zero outside of the expected annual credit period for operator confirmation before posting.

## Medisave transaction requirements

Medisave sub-account (MA) may have outflows for medical claims that do not appear as monthly contributions. These follow a balance-reconcile pattern similar to a digital wallet.

- The system shall compare the operator-entered closing balance against the expected balance derived from opening balance, contributions, and interest.
- If a gap exists, the system shall present the variance and prompt the operator to investigate and provide an explanation or manual transaction entry to close the gap.
- Manual transactions logged to close Medisave gaps shall be classified as healthcare expense.
- The system shall require operator confirmation before any Medisave gap adjustment is posted.

## Reconciliation requirements

- The system shall verify the computed closing balance for each sub-account against the operator-entered closing balance.
- The balance equation for each sub-account is: `closing_balance = opening_balance + contributions + interest + transactions`.
- If the computed closing balance does not match the operator-entered closing balance, the system shall present the variance per sub-account before proceeding.
- Reconciliation shall pass for all three sub-accounts before CPF transactions are posted to HomeBudget.
- OA and SA gaps that are not explained by any entered transaction shall be flagged as unresolved and block close until the operator provides a resolution note.

## Lineage requirements

Each value posted to HomeBudget or the close output shall carry the following lineage fields:

| field           | description                                                  |
| --------------- | ------------------------------------------------------------ |
| `period`        | period in `YYYY-MM` format                                   |
| `sub_account`   | CPF sub-account identifier: `OA`, `SA`, or `MA`              |
| `input_type`    | type of entry: `contribution`, `interest`, `transaction`, `adjustment` |
| `operator_note` | free-text note from operator JSON input, if provided         |
| `derived_type`  | classification applied (e.g. `transfer`, `investment_income`, `healthcare_expense`) |
