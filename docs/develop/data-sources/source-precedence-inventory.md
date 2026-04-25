# Source Precedence Inventory

## Contents

- [Summary](#summary)
- [Precedence Order](#precedence-order)
- [Conflict Classes](#conflict-classes)

## Summary

This guide defines source inventory and precedence ranking used for conflict inspection in requirements workflows.

## Precedence Order

| id | rank | source_group             | default_authority | notes                                                                             |
| -- | ---- | ------------------------ | ----------------- | --------------------------------------------------------------------------------- |
| 01 | 1    | statement_digital_twin   | highest           | actual transactions from bank statements sot for txn amounts in account currency  |
| 02 | 2    | homebudget_ledger        | high              | homebudget ledger sot for other txn attributes date category description          | 
| 03 | 3    | helper_workbooks         | medium            | current process that generates fin stm from sources, sot for transformation logic |
| 04 | 4    | reference_repositories   | medium            | current process that generates fin stm from sources, sot for transformation logic |
| 05 | 5    | local_manual_inputs      | suggestion        | suggested design templates for input format to be used for the POC                |

## Conflict Classes

Typical conflicting values inspected by precedence inventory:

- transaction presence
- amount and currency conversions
- date alignment and month-close assignment
- mapping lookup results
- month-end balances
- manual override values

