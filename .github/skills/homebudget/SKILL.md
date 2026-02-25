---
name: homebudget
description: Working with the HomeBudget Python wrapper for programmatic access to HomeBudget financial data
license: MIT
compatibility: Python 3.8+
metadata:
  author: yayfalafels
  version: 2.1.0
  repository: https://github.com/yayfalafels/homebudget
  docs: https://yayfalafels.github.io/homebudget/
---

## Overview

The HomeBudget Python wrapper is a library and CLI for programmatic access to HomeBudget personal finance data. It enables full CRUD operations for expenses, income, and transfers with automatic sync to mobile devices.

**Official Documentation:** https://yayfalafels.github.io/homebudget/

## Installation

### Via pip

```bash
pip install homebudget
```

### Via wheel (local)

```bash
pip install homebudget-2.1.0-py3-none-any.whl
```

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
- `sync_enabled` - Enable/disable SyncUpdate creation (default: true)
- `base_currency` - Base currency code like "SGD", "USD" (default: from database)
- `forex.cache_ttl_hours` - Forex rate cache validity (default: 1)

### Database Location

Default database path per official documentation:
```
%USERPROFILE%\OneDrive\Documents\HomeBudgetData\Data\homebudget.db
```

## Quick Start

### Basic Usage with Context Manager

```python
from homebudget import HomeBudgetClient

# Loads config automatically from default location
with HomeBudgetClient() as client:
    # Browse categories
    categories = client.repository.get_categories()
    
    # Browse accounts
    accounts = client.repository.list_accounts()
    
    # Query expenses
    expenses = client.list_expenses(
        start_date="2026-01-01",
        end_date="2026-02-28"
    )
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
- `client.repository.get_categories()` - List all expense categories
- `client.repository.get_subcategories(category_key)` - List subcategories for a category
- `client.repository.list_accounts()` - List all accounts

**Query Transactions:**
- `client.list_expenses(start_date, end_date)` - Query expenses
- `client.list_incomes(start_date, end_date)` - Query income
- `client.list_transfers(start_date, end_date)` - Query transfers

**Create/Update/Delete:**
- `client.add_expense(expense_dto)` - Add expense
- `client.update_expense(key, **fields)` - Update expense
- `client.delete_expense(key)` - Delete expense
- Similar methods for income and transfers

See official [Methods documentation](https://yayfalafels.github.io/homebudget/methods/) for complete API reference.

## Common Issues

### "Config file not found" Error

**Problem:** Script cannot locate `hb-config.json`

**Solutions:**
1. Create config file at default location: `%USERPROFILE%\OneDrive\Documents\HomeBudgetData\hb-config.json`
2. Use environment variable: `set HB_CONFIG=C:\path\to\hb-config.json`
3. Pass `db_path` parameter explicitly: `HomeBudgetClient(db_path="C:/path/to/homebudget.db")`

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
- See [Sync Update documentation](https://yayfalafels.github.io/homebudget/sync-update/)

### UnicodeEncodeError on Windows

**Problem:** Unicode characters fail to print in cmd.exe (cp1252 encoding)

**Solutions:**
- Use ASCII-safe characters in output (avoid emoji/box-drawing chars)
- Set environment: `set PYTHONIOENCODING=utf-8`
- Use PowerShell instead of cmd.exe

### Category/Subcategory Not Found After Query

**Problem:** Updated category list doesn't reflect recent changes

**Solutions:**
- Use `client.repository.get_categories()` for latest data (not cached)
- Reload repository if in-memory cache is stale

## Related Resources

- **Official Docs:** https://yayfalafels.github.io/homebudget/
- **User Guide:** https://yayfalafels.github.io/homebudget/user-guide/
- **Configuration Guide:** https://yayfalafels.github.io/homebudget/configuration/
- **CLI Guide:** https://yayfalafels.github.io/homebudget/cli-guide/
- **Methods Reference:** https://yayfalafels.github.io/homebudget/methods/
- **SQLite Schema:** https://yayfalafels.github.io/homebudget/sqlite-schema/
- **GitHub Repository:** https://github.com/yayfalafels/homebudget

## Development Notes

### Using with Virtual Environments

The project uses a shared virtual environment at `env/` directory. Install homebudget package using:

```bash
# Activate environment
.\env\Scripts\Activate.ps1  # Windows PowerShell
source env/bin/activate      # Linux/Mac

# Install package
pip install homebudget
```

### Testing

Test scripts should follow the pattern in [`.dev/.scripts/python/test_homebudget_wrapper.py`](.dev/.scripts/python/test_homebudget_wrapper.py):

1. Use config file or explicit `db_path` parameter
2. Handle missing database gracefully
3. Test with context manager for proper cleanup
4. Use `encoding="utf-8"` when reading/writing files

### Common Patterns

**Date handling:**
```python
import datetime as dt
from datetime import date

# Use date objects, not strings
start = dt.date(2026, 1, 1)
end = dt.date.today()
expenses = client.list_expenses(start_date=start, end_date=end)
```

**Currency handling:**
```python
from decimal import Decimal

# Use Decimal for financial amounts
amount = Decimal("123.45")
expense_dto = ExpenseDTO(
    date=dt.date.today(),
    category="Groceries",
    subcategory="Food",
    amount=amount,
    account="Wallet",
    notes="Weekly shopping"
)
```

## Troubleshooting Guide

For detailed troubleshooting and edge cases, refer to:
- [Configuration Troubleshooting](https://yayfalafels.github.io/homebudget/configuration/#troubleshooting)
- [Known Issues](https://yayfalafels.github.io/homebudget/issues/)
- [Sync Update Documentation](https://yayfalafels.github.io/homebudget/sync-update/)
