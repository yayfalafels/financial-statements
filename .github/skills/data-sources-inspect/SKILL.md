---
name: data-sources-inspect
description: Inspect primary data sources across HomeBudget and Google Sheets for requirements evidence, schema discovery, and mapping validation
license: MIT
compatibility: Windows 11 and Python 3.12+
metadata:
  author: yayfalafels
  version: 1.0.0
---

## Contents

- Overview
- Summary
- Relevant skills
- Related documentation
- Project source-of-truth boundary
- HomeBudget inspection
- Google Sheets inspection
- Three-stage category mapping
- Script locations and patterns
- Environment setup

## Overview

This skill defines the methodology for navigating and inspecting primary sources to support requirements validation and evidence gathering.

Use this skill for cross-source inspection workflows that combine HomeBudget and Google Sheets evidence collection.

## Summary

- Use this skill for cross-source inspection methodology during requirements work.
- Start with top-level source identification, then apply source-specific inspection procedures.
- Use companion skills for HomeBudget and Google Sheets implementation detail.

## Relevant Skills

- `homebudget`: HomeBudget API reference and procedures
- `gsheet-inspect`: Google Sheets inspection patterns
- `python`: python scripts and environment management
- `documentation`: working with text and markdown files


## Related Documentation

- [docs/develop/data-sources/inventory.md](../../../docs/develop/data-sources/inventory.md): Canonical inventory of POC primary references with explicit artifact paths and usage intent
- [docs/requirements/accounting-logic.md](../../../docs/requirements/accounting-logic.md): Accounting principles and transaction patterns
- [docs/requirements/account-classification.md](../../../docs/requirements/account-classification.md): Account type definitions
- [docs/requirements/transaction-category-mapping.md](../../../docs/requirements/transaction-category-mapping.md): Stage 3 mapping
## Project Source-of-Truth Boundary

- Keep requirement documents focused on what the system must do.
- Keep inspection process steps, script patterns, and troubleshooting in this skill.
- Keep non-tool source-data inventory details in `docs/develop/data-sources/`.

## HomeBudget Inspection

### Overview

HomeBudget is the core personal finance database. It contains:

- Accounts, including cost centers, wallets, investment accounts, and credit cards.
- Categories, including hierarchical expense and income types.
- Transactions, including expenses, income, and transfers.
- Reconciliation state.

### Category Structure

Categories in HomeBudget have two separate systems.

Expense categories:

- Hierarchical structure from parent to child categories.
- Examples include Health and Wellness to Medical expenses and Professional Services to Currency conversion.
- Queried via `client.repository.get_categories()` and `client.repository.get_subcategories(category_key)`.
- Used for expense and transfer tracking.

Income categories:

- Flat structure with no hierarchy.
- Income type names are stored as the category field in income transactions.
- Examples include salaries, dividends, interest, rebates, and reimbursements.
- Income records are currently uncategorized in HomeBudget and use `category_key = None`.
- Income categories are defined during monthly closing, not maintained as HomeBudget master data.
- Query with `client.list_incomes(start_date, end_date)`, then inspect description and amount fields.

### Key Account Patterns

Personal spending center:

- Account: `TWH - Personal`
- Role: consolidated cost center for personal expenses.
- Pattern: double-booking where funds transfer into the center and then expenses are recorded with categories.

Personal income center:

- Account: `TWH DBS Multi SGD`, or equivalent main personal account.
- Role: consolidated account for personal income.
- Pattern: income is booked to the center and non-center income is transferred back.

Investment accounts:

- Do not use expense categories.
- Use P and L classification such as M2M gains, dividends, interest, and profit or loss.
- Examples include `IB POSITION USD` and `TWH IB USD`.

### Python Inspection Pattern

Use `.dev/scripts/python/inspect_hb_categories.py` for the standard inspection flow.

```python
from homebudget import HomeBudgetClient
from datetime import datetime, timedelta

with HomeBudgetClient() as client:
    categories = client.repository.get_categories()
    for cat in categories:
        cat_key = cat.get('key') if isinstance(cat, dict) else cat.key
        subcats = client.repository.get_subcategories(cat_key)

    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    incomes = client.list_incomes(start_date=start_date, end_date=end_date)

    for inc in incomes:
        inc_date = getattr(inc, 'date', None)
        inc_description = getattr(inc, 'description', None)
        inc_amount = getattr(inc, 'amount', None)
```

### Critical Note on Income

- HomeBudget income commands do not enforce predefined income categories.
- Income labels are user-defined per transaction or batch.
- For requirements and mapping evidence, define income categories in monthly closing workflow artifacts.

## Google Sheets Inspection

### Overview

Google Sheets workbooks are used for:

- Helper workbook configuration and monthly closing validation.
- Category mapping between transaction categories and GL accounts.
- Reconciliation tracking and validation.

### Configuration Files

Workbook configs are stored in `gsheet/*.json`.

```json
{
  "wkbid": "1xF_cmgyKw2NHV6uj-bwo2O1D-eiyJwihlhFJSpMEKPg",
  "sheet_name": {
    "header": "worksheet!$A$1:$J$1",
    "data": "worksheet!$A$2:$J$182"
  }
}
```

Key configs:

- `gsheet/homebudget-workbook.json`: category mapping workbook with `cat_map` region.
- `gsheet/financial-statements.json`: statement output balances, forex rates, accounts, and expense category map.
- `gsheet/cpf.json`: CPF account balance regions.
- `gsheet/ibkr-iba.json`: IBKR IBA balance regions.
- `gsheet/cash-expenses.json`: personal cash expense transactions.
- `gsheet/closing-session.json`: monthly closing session register.
- `gsheet/shared-expenses.json`: shared expense records for bill payment workflows.
### Python Inspection Pattern

Use `sqlite-gsheet` package, following skill `gsheet-inspect`.

```python
from sqlite_gsheet import Client
import json

with open('gsheet/homebudget-workbook.json') as f:
    config = json.load(f)

client = Client(config['wkbid'])
df = client.read_range(
    range_name='cat_map!$A$1:$J$182',
    headers=True
)

print(df.columns.tolist())
print(df.head(20))
```

### Environment Note

The `sqlite-gsheet` package requires:

- `.credentials/client_secret.json` for Google Sheets API OAuth.
- Reinstallation when import fails:
  `pip install --force-reinstall --no-deps sqlite_gsheet-2.0.1-py3-none-any.whl`

## Three-Stage Category Mapping

### Stage 1: HomeBudget Category to GL Account

- Source: `cat_map` sheet in `homebudget-workbook.json`.
- Direction: HomeBudget expense category to GL account code.
- Coverage: expense categories only.

### Stage 2: GL Account to Financial Statements Category

- Source: legacy reconcile sheet structures.
- Direction: GL account to financial statements line item.
- Coverage: all GL accounts.
- Status: partial and requires extraction.

### Stage 3: Financial Statements Category to Derived Transaction Type

- Source: IBKR and CPF integration requirement documents.
- Direction: financial statements category to integration-specific classification.
- Coverage: expense and investment income cases.

### Mapping Asymmetry Warning

- Stages 1 and 2 are expense-focused.
- Stage 3 includes expense and income use cases.
- Personal income labels do not flow through HomeBudget category hierarchy.

## Source Inspection Reference

This reference matrix maps all POC primary sources to their inspection procedures and tools. Use this to navigate inspection workflows for requirements validation.

| id | source                     | category             | approach                  | tool / script      |
| -- | -------------------------- | -------------------- | ------------------------- | ------------------ |
| 01 | homebudget.db              | HomeBudget           | skill homebudget API      | homebudget CLI     |
| 02 | hb-config.json             | HomeBudget           | skill homebudget config   | file inspection    |
| 03 | ibkr-iba.json              | Google Sheets        | gsheet-inspect + script   | helper_schemas.py  |
| 04 | cpf.json                   | Google Sheets        | gsheet-inspect + script   | helper_schemas.py  |
| 05 | homebudget-workbook.json   | Google Sheets        | gsheet-inspect + script   | helper_schemas.py  |
| 06 | financial-statements.json  | Google Sheets        | gsheet-inspect + script   | helper_schemas.py  |
| 07 | cash-expenses.json         | Google Sheets        | gsheet-inspect + script   | helper_schemas.py  |
| 08 | shared-expenses.json       | Google Sheets        | gsheet-inspect + script   | helper_schemas.py  |
| 09 | closing-session.json       | Google Sheets        | gsheet-inspect + script   | helper_schemas.py  |
| 10 | reference/statements/*     | Statement sources    | deferred — see docs       | —                  |
| 11 | data/monthly-closing/*     | Local inputs         | deferred — see docs       | —                  |
| 12 | reference/hb-finances/*    | Reference repos      | deferred — see docs       | —                  |
| 13 | reference/hb-reconcile/*   | Reference repos      | deferred — see docs       | —                  |

**How to use this reference:**

- **skill homebudget** — Follow procedures in the `homebudget` skill for API access and database queries.
- **gsheet-inspect + script** — Run `inspect_helper_schemas.py` for primary batch schema profiling across helper workbooks.
- **gsheet-inspect API** — Reference the direct API pattern in the Google Sheets Inspection section for custom or edge-case inspection paths.
- **deferred — see docs** — These sources are covered in related documentation sections; check Contents and Related Documentation.

## Script Locations and Patterns

Inspection scripts are organized under `.dev/scripts/` by script type.

- Python scripts in `.dev/scripts/python/`.
- Bash scripts in `.dev/scripts/bash/`.
- Do not place scripts in `.dev/` root.

Examples:

- `.dev/scripts/python/inspect_hb_categories.py`
- `.dev/scripts/python/inspect_cat_map.py`

Run scripts with the project virtual environment:

```powershell
.\env\Scripts\python.exe .dev\scripts\python\inspect_hb_categories.py
```

Do not use system Python or bare `python`.

## Environment Setup

### Prerequisites

1. Python environment at `env/Scripts/python.exe`.
2. Installed packages:
   - `homebudget` 2.1.1 or later.
   - `sqlite-gsheet` 2.0.1 or later.
3. Credentials at `.credentials/client_secret.json`.
4. HomeBudget database configured by `hb-config.json` at `%USERPROFILE%\OneDrive\Documents\HomeBudgetData\`.

### Verification

```powershell
.\env\Scripts\python.exe -c "from homebudget import HomeBudgetClient; print('OK')"
.\env\Scripts\python.exe -c "from sqlite_gsheet import Client; print('OK')"
```

### Common Issues

Issue: `ModuleNotFoundError: No module named 'sqlite_gsheet'`

- Solution: reinstall from wheel using force-reinstall and no dependencies.

Issue: HomeBudget config file not found.

- Solution: create `hb-config.json` with `db_path`.

Issue: Google Sheets API credentials not found.

- Solution: download OAuth 2.0 credentials and save to `.credentials/client_secret.json`.
