---
name: homebudget
description: Working with the HomeBudget Python wrapper for programmatic access to HomeBudget financial data
license: MIT
compatibility: Python 3.8+
metadata:
  author: yayfalafels
  version: 2.1.1
  repository: https://github.com/yayfalafels/homebudget
  docs: https://yayfalafels.github.io/homebudget/
---

## Contents

- Overview
- Summary
- Related resources
- Related skills
- Troubleshooting guide
- Development notes
- Business logic
- Installation
- Project source-of-truth boundary
- Configuration
- Inspecting Live Values
- Quick start
- CLI usage patterns
- Sync and UI behavior
- Common issues

## Overview

The HomeBudget Python wrapper is a library and CLI for programmatic access to HomeBudget personal finance data. It enables full CRUD operations for expenses, income, and transfers with automatic sync to mobile devices.

**Official Documentation:** https://yayfalafels.github.io/homebudget/

## Summary

- Use this skill for HomeBudget inspection procedures, command usage, CRUD patterns, troubleshooting, and HB-specific booking rules.
- In this repo, always use `.dev\env` (Python 3.12.10) for all HomeBudget CLI work and helper scripts. Activate with `.dev\env\Scripts\Activate.ps1`. The `env\` directory is a separate legacy context and must not be used for HomeBudget helper-script work.
- Prefer public `HomeBudgetClient` methods over direct `client.repository` access for normal automation.
- Use the CLI when you want write operations to close and reopen the HomeBudget UI automatically.
- Treat transfer currency normalization, batch execution, and SyncUpdate behavior as part of the supported surface.
- Refer to the Business Logic section for booking patterns, account roles, and reconciliation rules specific to this repo's use of HomeBudget.
- Use requirement pages for scope boundaries only.
- Use skill `data-sources-inspect` for cross-source inspection methodology.

## Related Resources

- **Official Docs:** https://yayfalafels.github.io/homebudget/
- **User Guide:** https://yayfalafels.github.io/homebudget/user-guide/
- **Configuration Guide:** https://yayfalafels.github.io/homebudget/configuration/
- **CLI Guide:** https://yayfalafels.github.io/homebudget/cli-guide/
- **Methods Reference:** https://yayfalafels.github.io/homebudget/methods/
- **Sync Update Guide:** https://yayfalafels.github.io/homebudget/sync-update/
- **Transfer Currency Normalization:** https://yayfalafels.github.io/homebudget/transfer-currency-normalization/
- **SQLite Schema:** https://yayfalafels.github.io/homebudget/sqlite-schema/
- **Developer Guide:** https://yayfalafels.github.io/homebudget/developer-guide/
- **GitHub Repository:** https://github.com/yayfalafels/homebudget
- `docs/requirements/homebudget.md` for requirement boundary and scope.

## Related Skills

- `data-sources-inspect` for cross-source inspection methodology and evidence capture.

## Troubleshooting Guide

For detailed troubleshooting and edge cases, refer to:

- [Configuration Troubleshooting](https://yayfalafels.github.io/homebudget/configuration/#troubleshooting)
- [CLI Guide](https://yayfalafels.github.io/homebudget/cli-guide/)
- [Methods Reference](https://yayfalafels.github.io/homebudget/methods/)
- [Known Issues](https://yayfalafels.github.io/homebudget/issues/)
- [Sync Update Documentation](https://yayfalafels.github.io/homebudget/sync-update/)
- [Transfer Currency Normalization](https://yayfalafels.github.io/homebudget/transfer-currency-normalization/)

## Development Notes

### Using with Virtual Environments

For all HomeBudget CLI work and helper scripts in this repo, use `.dev\env` (Python 3.12.10). `.env` is reserved for environment variables. `env\` is a separate legacy context and must not be used for helper-script work.

```powershell
# Activate environment (Windows PowerShell)
.dev\env\Scripts\Activate.ps1

# Verify hb resolves to .dev\env
(Get-Command hb).Source   # should show ...financial-statements\.dev\env\Scripts\hb.exe

# Install package
pip install homebudget
```

### Testing

Test scripts should follow the existing HomeBudget wrapper test pattern used in this repo:

1. Use config file or explicit `db_path` parameter
2. Handle missing database gracefully
3. Test with context manager for proper cleanup
4. Use `encoding="utf-8"` when reading/writing files

### Common Patterns

**Date handling:**
```python
import datetime as dt

# Use date objects, not strings
start = dt.date(2026, 1, 1)
end = dt.date.today()
expenses = client.list_expenses(start_date=start, end_date=end)
```

**Expense handling:**
```python
import datetime as dt
from decimal import Decimal
from homebudget import ExpenseDTO

# Expenses are always booked in TWH - Personal (the cost center)
# A matching transfer from the real payment account is also required
expense_dto = ExpenseDTO(
    date=dt.date(2026, 2, 16),
    category="Food (Basic)",
    subcategory="Groceries",
    amount=Decimal("43.50"),
    account="TWH - Personal",   # always the cost center, never the payment account
    notes="NTUC FairPrice"
)
```

**Income handling:**
```python
import datetime as dt
from decimal import Decimal
from homebudget import IncomeDTO

income_dto = IncomeDTO(
    date=dt.date(2026, 2, 28),
    name="Interest Income",
    amount=Decimal("0.93"),
    account="TWH DBS Multi SGD",
    notes="Monthly bank interest"
)
```

**Batch operations:**
```python
from homebudget import BatchOperation, HomeBudgetClient

operations = [
    BatchOperation(
        resource="expense",
        operation="add",
        parameters={
            "date": "2026-02-16",
            "category": "Food (Basic)",
            "subcategory": "Cheap restaurant",
            "amount": "25.50",
            "account": "TWH - Personal",
            "notes": "Lunch",
        },
    )
]

with HomeBudgetClient() as client:
    result = client.batch(operations, continue_on_error=False)
```

## Business Logic

This section defines HB-specific booking rules used in this repo. These rules govern how transactions must be structured in HomeBudget to reflect actual financial activity correctly.

### Account types and roles

| id | HB type  | example           | role                                                         |
| -- | -------- | ----------------- | ------------------------------------------------------------ |
| 01 | Budget   | TWH - Personal    | personal expense cost center; closes to zero monthly         |
| 02 | Cash     | TWH DBS Multi SGD | real wallet or bank account                                  |
| 03 | Credit   | TWH UOB One SGD   | credit card or line of credit; holds negative balances       |
| 04 | External | IB POSITION USD   | investment positions and non-personal accounts               |

Key accounts:

- `TWH - Personal` — primary personal expense cost center; month-end balance must be zero
- `TWH DBS Multi SGD` — primary personal income account; all SGD non-capital-gains income books here
- `TWH CITI` — USD income account; non-capital-gains USD income not in investment accounts books here
- `TWH IB USD` — IBKR cash account; positive balance = classified as Cash, negative balance = classified as Credit
- `IB POSITION USD` — IBKR position account; books capital gains and M2M adjustments

### Personal expense booking: double-entry pattern

Every personal expense requires two transactions in HomeBudget:

1. **Transfer** from the real payment account to `TWH - Personal`
2. **Expense** booked in `TWH - Personal` with the applicable category and subcategory

This applies regardless of payment method — cash, bank account, or credit card.

```bash
# Cash payment
hb transfer add --date 2026-02-16 --from-account "Cash TWH SGD" --to-account "TWH - Personal" --amount 25.50
hb expense add --date 2026-02-16 --category "Food (Basic)" --subcategory "Cheap restaurant" --amount 25.50 --account "TWH - Personal" --notes "Lunch"

# Credit card payment
hb transfer add --date 2026-02-20 --from-account "TWH UOB One SGD" --to-account "TWH - Personal" --amount 52.80
hb expense add --date 2026-02-20 --category "Food (Basic)" --subcategory "Groceries" --amount 52.80 --account "TWH - Personal" --notes "NTUC FairPrice"
```

### Personal income booking

All personal income is booked in the account where cash lands:

- SGD income (salary, interest, dividends): `TWH DBS Multi SGD`
- USD income not in investment accounts: `TWH CITI`

```bash
hb income add --date 2026-02-28 --name "Salary and Wages" --amount 7400.00 --account "TWH DBS Multi SGD" --notes "Flintex Feb salary"
hb income add --date 2026-02-28 --name "Interest Income" --amount 0.93 --account "TWH DBS Multi SGD" --notes "DBS monthly interest"
```

### Investment accounts: IBKR split

IBKR uses two linked accounts:

- `TWH IB USD` — IBKR cash; books interest, dividends, realized P&L, and forex cash effects
- `IB POSITION USD` — IBKR position; books capital gains and M2M adjustments

Trades are transfers between cash and position — they are not income or expense:

```bash
# IBKR deposit: bank account to IBKR cash
hb transfer add --date 2026-03-01 --from-account "TWH CITI" --to-account "TWH IB USD" --amount 5000.00 --notes "IBKR deposit"

# Stock purchase: IBKR cash to position account
hb transfer add --date 2026-03-10 --from-account "TWH IB USD" --to-account "IB POSITION USD" --amount 10000.00 --notes "AAPL buy"

# Capital gain or M2M booked as income on the position account
hb income add --date 2026-03-31 --name "Capital Gain/Loss" --amount 1880.00 --account "IB POSITION USD" --notes "AAPL M2M March"
```

### Forex on transactions

When a foreign-currency purchase is made on a credit card, three transactions are required:

1. **Expense** in `TWH - Personal` at spot exchange rate in SGD
2. **Transfer** from the credit card to `TWH - Personal` at the actual posted SGD charge
3. **Reconciliation expense** in `TWH - Personal` for the difference, category `Professional Services:Currency Conversion`

```bash
# USD 50.00 at spot 1.35 = SGD 67.50
hb expense add --date 2026-03-08 --category "Travel" --subcategory "Accommodation" --amount 67.50 --account "TWH - Personal" --notes "Airbnb NYC"

# Actual posted charge: SGD 68.20
hb transfer add --date 2026-03-08 --from-account "TWH UOB One SGD" --to-account "TWH - Personal" --amount 68.20 --notes "Airbnb NYC USD FX"

# Forex fee reconciliation: 68.20 - 67.50 = 0.70
hb expense add --date 2026-03-08 --category "Professional Services" --subcategory "Currency Conversion" --amount 0.70 --account "TWH - Personal" --notes "Airbnb NYC FX fee"
```

### Transaction de-duplication

Uniqueness is defined by: account + date + amount + description.

When two legitimate transactions share all four fields, append a sequential suffix to the description:

```bash
hb expense add --date 2026-02-16 --category "Transport" --subcategory "Taxi" --amount 12.00 --account "TWH - Personal" --notes "Grab taxi -01"
hb expense add --date 2026-02-16 --category "Transport" --subcategory "Taxi" --amount 12.00 --account "TWH - Personal" --notes "Grab taxi -02"
```

### Reconciliation date rules

When reconciling a bank account, transactions fall into three groups relative to the reconciliation date:

| id | group    | in statement | in HB | date   | action                                             |
| -- | -------- | ------------ | ----- | ------ | -------------------------------------------------- |
| 01 | captured | yes          | yes   | before | reconcile HB amount to match statement             |
| 02 | pending  | no           | yes   | before | move transaction date to after reconciliation date |
| 03 | forecast | no           | yes   | after  | leave as-is, out of scope for reconciliation       |

For pending transactions moved past the reconciliation date, add the actual transaction date in the notes field, for example "13 Mar". After two reconciliation periods have passed, update the transaction to its actual date.

## Installation

### Via pip

```bash
pip install homebudget
```

### Via wheel (local)

```bash
pip install homebudget-2.1.1-py3-none-any.whl
```

## Project Source-of-Truth Boundary

Use this skill as the source of truth for HomeBudget inspection procedures and implementation details.

- Keep requirement documents focused on what the system must do.
- Keep command usage, script-level workflows, and troubleshooting in this skill.
- For non-tool source-data references, update the data-source guide in `docs/develop/data-sources/`.

The Business Logic section in this skill is a derived, HB-scoped summary. The authoritative source for accounting rules and account classification is:

- `docs/requirements/accounting-logic.md` — booking patterns, double-entry rules, forex, M2M, reconciliation
- `docs/requirements/account-classification.md` — account types, asset categories, balance rules, income restrictions

When the two conflict, the requirement docs take precedence. Update this skill to stay in sync when those docs change.

## Configuration

HomeBudget requires a configuration file to locate your database.

### Configuration File Location

**Default path:**
```
%USERPROFILE%\OneDrive\Documents\HomeBudgetData\hb-config.json
```

### Configuration File Format

Create `hb-config.json` with:

```json
{
  "db_path": "C:\\Users\\YOUR_USERNAME\\OneDrive\\Documents\\HomeBudgetData\\Data\\homebudget.db",
  "sync_enabled": true,
  "base_currency": "SGD",
  "forex": {
    "cache_ttl_hours": 1
  }
}
```

**Key fields:**
- `db_path` - Absolute path to your HomeBudget database (required)
- `sync_enabled` - Controls SyncUpdate creation for direct wrapper usage; default is `true`
- `base_currency` - Base currency code like "SGD", "USD" (default: from database)
- `forex.cache_ttl_hours` - Forex rate cache validity (default: 1)

### Database Location

Default database path per official documentation:
```
%USERPROFILE%\OneDrive\Documents\HomeBudgetData\Data\homebudget.db
```

### Loading Priority

- Prefer explicit overrides for deterministic automation: `db_path=` for methods and `--db` for CLI.
- Official docs describe config loading priority as explicit override, then config file location.
- In this repo's automation, prefer explicit `db_path` or CLI `--db` when you need predictable behavior across environments.

### CLI Override

```bash
homebudget --db "C:/path/to/homebudget.db" expense list
```

## Repo Workflow

When using this skill in this repository, do this first before any HomeBudget CLI inspection:

1. Activate `.dev\env` so `hb` resolves to the correct workspace interpreter.
2. Inspect live values with `hb * list` before writing examples or making assumptions.

```powershell
# Always use .dev\env for HomeBudget CLI and all helper-script work
.dev\env\Scripts\Activate.ps1
hb account list
hb category list
hb category subcategories --category "Food (Basic)"
```

Two virtual environments exist in this repo:

| path       | Python  | purpose                                                |
| ---------- | ------- | ------------------------------------------------------ |
| `.dev\env` | 3.12.10 | development, inspection, helper scripts                |
| `env\`     | 3.11.0  | main app context for commissioning and app operations  |

use `.dev\env` for inspection, requirements, design and development tasks

Why it matters:

- A globally resolved `hb` may point at the wrong Python installation and fail on missing dependencies.
- Real examples should come from live HomeBudget data, not placeholders.

## Inspecting Live Values

Use this workflow before adding or editing examples in this skill:

1. Activate `.dev/env/` so `hb` resolves to the helper-script interpreter.
2. Inspect account names with `hb account list`.
3. Inspect expense category names with `hb category list`.
4. Inspect expense subcategory names with `hb category subcategories --category "<category>"`.
5. Inspect income records with `hb income list --limit 20` and treat the income classification field as `name`, not `category`.

Reference commands:

```powershell
.dev\env\Scripts\Activate.ps1
hb account list
hb category list
hb category subcategories --category "Food (Basic)"
hb income list --account "TWH DBS Multi SGD" --limit 20
```

Live examples observed in this repo:

- Accounts: `Cash TWH SGD`, `TWH DBS Multi SGD`, `TWH CITI`, `TWH IB USD`, `CPF MA`
- Expense categories: `Food (Basic)`, `Transport`, `Utilities`, `Professional Services`, `Travel`
- Expense subcategories under `Food (Basic)`: `Groceries`, `Cheap restaurant`, `Food Court`, `Tingkat`, `meal prep`
- Income names: `Salary and Wages`, `Interest Income`, `Refund and Promotion`, `Dividend`, `Capital Gain/Loss`, `Other Income`

## Quick Start

### Basic Usage with Context Manager

```python
import datetime as dt

from homebudget import HomeBudgetClient

# Loads config automatically from default location
with HomeBudgetClient() as client:
    # Browse categories and accounts
    categories = client.get_categories()
    subcategories = client.get_subcategories("Food (Basic)")
    accounts = client.get_accounts()

    # Query personal expenses for a closing period
    expenses = client.list_expenses(
        start_date=dt.date(2026, 2, 1),
        end_date=dt.date(2026, 2, 28)
    )

    # Query income booked in the primary personal income account
    incomes = client.list_incomes(
        start_date=dt.date(2026, 2, 1),
        end_date=dt.date(2026, 2, 28)
    )

    # Query account balance for reconciliation
    balance = client.get_account_balance("TWH DBS Multi SGD")
```

### Override Database Path

```python
from homebudget import HomeBudgetClient

# Use explicit path, ignore config file
with HomeBudgetClient(db_path="C:/path/to/homebudget.db") as client:
    expenses = client.list_expenses()
```

### Key Methods

**Browse Data:**
- `client.get_categories()` - List all expense categories ordered by sequence number
- `client.get_subcategories(category_name)` - List subcategories for a category name
- `client.get_accounts(currency=None, account_type=None)` - List accounts with optional filters
- `client.get_account_balance(account_name, query_date=None)` - Compute balance from reconcile data

**Query Transactions:**
- `client.list_expenses(start_date=None, end_date=None)` - Query expenses
- `client.list_incomes(start_date=None, end_date=None)` - Query income
- `client.list_transfers(start_date=None, end_date=None)` - Query transfers

**Create/Update/Delete:**
- `client.add_expense(expense_dto)` - Add expense
- `client.update_expense(key, **fields)` - Update expense
- `client.delete_expense(key)` - Delete expense
- Similar methods exist for income and transfers

**Batch Operations:**
- `client.batch(operations, continue_on_error=False)` - Execute mixed add/update/delete operations
- `client.add_expenses_batch(expenses)` - Batch-add expenses
- `client.add_incomes_batch(incomes)` - Batch-add income records
- `client.add_transfers_batch(transfers)` - Batch-add transfers

**DTOs and Records:**
- Use `ExpenseDTO`, `IncomeDTO`, and `TransferDTO` for create operations.
- Read APIs return record objects such as `ExpenseRecord`, `IncomeRecord`, `TransferRecord`, and `BalanceRecord`.

See official [Methods documentation](https://yayfalafels.github.io/homebudget/methods/) for complete API reference.

## CLI Usage Patterns

Use the CLI for interactive inspection, ad hoc CRUD, and operations where automatic UI coordination matters.

In this repo, activate `.dev/env/` first so `hb` uses the correct interpreter for helper-script usage.

### Query and Reference Commands

```bash
hb category list
hb category subcategories --category "Food (Basic)"
hb account list
hb income list --account "TWH DBS Multi SGD" --limit 20
hb account balance --account "TWH DBS Multi SGD" --date 2026-02-01
hb expense list --start-date 2026-02-01 --end-date 2026-02-28 --limit 50
```

### Write Commands

Personal expenses always require a paired transfer and expense. The transfer moves funds from the real payment account into the cost center; the expense is then booked in the cost center.

```bash
# Cash payment: transfer from cash account, then book expense in cost center
hb transfer add --date 2026-02-16 --from-account "Cash TWH SGD" --to-account "TWH - Personal" --amount 25.50
hb expense add --date 2026-02-16 --category "Food (Basic)" --subcategory "Cheap restaurant" --amount 25.50 --account "TWH - Personal" --notes "Lunch"

# Credit card payment: transfer from credit card, then book expense in cost center
hb transfer add --date 2026-02-20 --from-account "TWH UOB One SGD" --to-account "TWH - Personal" --amount 52.80
hb expense add --date 2026-02-20 --category "Food (Basic)" --subcategory "Groceries" --amount 52.80 --account "TWH - Personal" --notes "NTUC FairPrice"

# Personal income: book in TWH DBS Multi SGD
hb income add --date 2026-02-28 --name "Salary and Wages" --amount 7400.00 --account "TWH DBS Multi SGD" --notes "Flintex Feb salary"
hb income add --date 2026-02-28 --name "Interest Income" --amount 0.93 --account "TWH DBS Multi SGD" --notes "DBS monthly interest"

# Update and delete
hb income update 1041 --notes "DBS visa cashback"
hb transfer delete 21007 --yes
```

### Batch Commands

```bash
homebudget batch run --file operations.json
homebudget batch run --file operations.json --continue-on-error
homebudget batch run --file operations.json --error-report batch_errors.json
```

Batch JSON entries use `resource`, `operation`, and `parameters` fields matching single-record CLI commands.

## Sync and UI Behavior

- Wrapper write operations create `SyncUpdate` rows so changes propagate to devices in the sync group.
- CLI write commands always enable sync handling and UI control.
- CLI write commands close the HomeBudget UI before the transaction and reopen it after completion.
- Direct wrapper usage with `HomeBudgetClient()` manages the database connection, but UI control is only enabled when explicitly requested.
- Multi-field update operations can generate one SyncUpdate entry per changed field to mirror native behavior.
- If sync behavior matters, verify `DeviceInfo` and `SyncUpdate` tables and confirm all apps point at the same database.

For inspection work, the most relevant tables are `Account`, `Category`, `SubCategory`, `Expense`, `Income`, `Transfer`, `AccountTrans`, `DeviceInfo`, and `SyncUpdate`.

## Common Issues

### "Config file not found" Error

**Problem:** Script cannot locate `hb-config.json`

**Solutions:**
1. Create config file at default location: `%USERPROFILE%\OneDrive\Documents\HomeBudgetData\hb-config.json`
2. Pass `db_path` parameter explicitly: `HomeBudgetClient(db_path="C:/path/to/homebudget.db")`
3. Use CLI override: `homebudget --db "C:/path/to/homebudget.db" expense list`

### "Database path not in config" Error

**Problem:** Config file exists but missing `db_path` field

**Solutions:**
- Open config file and add/verify `"db_path"` key
- Ensure path uses double backslashes on Windows: `"db_path": "C:\\Users\\..."`

### "Database file not found" Error

**Problem:** `db_path` points to non-existent database

**Solutions:**
- Verify HomeBudget app has created the database
- Check that database actually exists at the specified path
- Use HomeBudget app to create sample data if database is empty

### "Sync Not Working" / Changes Don't Appear in Mobile

**Problem:** Changes made via Python don't sync to mobile device

**Solutions:**
- Verify `sync_enabled: true` in config file
- Confirm `DeviceInfo` table exists in database (HomeBudget creates this)
- Verify mobile app uses the same database file
- If you are using direct wrapper methods for writes, verify whether UI control is needed for your workflow
- See [Sync Update documentation](https://yayfalafels.github.io/homebudget/sync-update/)

### UnicodeEncodeError on Windows

**Problem:** Unicode characters fail to print in cmd.exe (cp1252 encoding)

**Solutions:**
- Use ASCII-safe characters in output (avoid emoji/box-drawing chars)
- Set environment: `set PYTHONIOENCODING=utf-8`
- Use PowerShell instead of cmd.exe

### Wrong `hb` Executable / Missing Dependency Error

**Problem:** `hb` resolves to a different Python installation and fails with import errors such as missing `requests`

**Solutions:**
- Configure the repo Python environment first
- Activate `.dev/env` before running `hb` commands
- If needed, verify the active interpreter before retrying HomeBudget CLI commands

### Category/Subcategory Not Found After Query

**Problem:** Updated category list doesn't reflect recent changes

**Solutions:**
- Use `client.get_categories()` and `client.get_subcategories(category_name)`
- Re-open the client if you need a fresh session after external changes

### Account Balance Error

**Problem:** `get_account_balance()` or `homebudget account balance` fails for an account

**Solutions:**
- Verify the account exists and has at least one reconcile balance record
- Use the exact HomeBudget account name
- Check the account's reconcile history before relying on calculated balances

### Mixed-Currency Transfer Confusion

**Problem:** Transfer amounts do not match the expected sending or receiving amount

**Solutions:**
- For mixed-currency transfers, decide whether `currency` and `currency_amount` describe the from-account or to-account side
- Provide `exchange_rate` when you need deterministic results
- Review the transfer normalization guide before bulk transfer imports


