# Bank Statement Source Data

## Contents

- [Summary](#summary)
- [Account Scope](#account-scope)
- [Statements.db Schema](#statementsdb-schema)
- [Transaction Field Schema](#transaction-field-schema)
- [GL Table](#gl-table)
- [Balances Table](#balances-table)
- [stm_txns Linkage](#stm_txns-linkage)
- [Inspection Procedure](#inspection-procedure)
- [Minimum Checks](#minimum-checks)
- [Common Anomalies](#common-anomalies)

## Summary

Bank statement source data for the POC covers four PDF-backed bank accounts ingested into `statements.db` via the reference `statements.py` ingestion script. This is the only group of accounts represented in the `stm_txns` region of the financial statements workbook. IBKR, CPF, and balance-only accounts are outside this path.

Reference location: `reference/hb-finances/statements.db`
Ingestion reference: `reference/hb-finances/statements.py`
Config reference: `reference/hb-finances/statement_config.json`
Account list: `data/monthly-closing/accounts.json`
Inspection script: `.dev/scripts/python/inspect_statements_db.py`
Inspection artifact: `.dev/.artifacts/statements_db_inspection.json`

## Account Scope

### POC Accounts

Four accounts are within the statement digital twin scope for the POC:

| id | account_name        | s3_account_id               | db_table           | currency |
| -- | ------------------- | --------------------------- | ------------------ | -------- |
| 01 | TWH DBS Multi SGD   | 02_dbs_savings_sgd          | TWH_DBS_MULTI_SGD  | SGD      |
| 02 | TWH CITI            | 04_citibank_personal        | TWH_CITI_USD       | USD      |
| 03 | TWH UOB One SGD     | 03_uob_one_visa             | TWH_UOB_ONE_SGD    | SGD      |
| 04 | TWH Visa USD        | 06_bank_of_america_visa_usd | TWH_BOA_TRAVEL_USD | USD      |

The `s3_account_id` value identifies the account's local statement file path under the operator filesystem. The `db_table` value is the SQLite table name inside `statements.db`. The canonical account name list is maintained in `data/monthly-closing/accounts.json`.

### Excluded Accounts

The following account types are outside the statement digital twin path and must not be treated as `stm_txns` sources:

- IBKR accounts — derived from CSV Activity Statements via top-down NAV methodology, not ingested into `statements.db`
- CPF accounts — manual JSON inputs with no statement download
- Balance-only accounts — observed balance only, no transaction-level statement

## Statements.db Schema

### Overview

The reference statements database is a SQLite file at `reference/hb-finances/statements.db` with eight tables:

| id | table_name         | row_count | description                            |
| -- | ------------------ | --------- | -------------------------------------- |
| 01 | TWH_DBS_MULTI_SGD  | 1200      | DBS savings — 8 cols with DBS ext      |
| 02 | TWH_CITI_USD       | 161       | Citibank personal — 3 cols             |
| 03 | TWH_UOB_ONE_SGD    | 2004      | UOB One visa — 3 cols                  |
| 04 | TWH_BOA_TRAVEL_USD | 288       | Bank of America travel visa — 3 cols   |
| 05 | GL                 | 4967      | merged ledger — all accounts combined  |
| 06 | balances           | 328       | month-end balances by account          |
| 07 | COMMON_UOB_SGD     | 241       | legacy — outside current POC scope     |
| 08 | TWH_DBS_Visa_SGD   | 1074      | legacy — outside current POC scope     |

The `GL` table is the primary merged ledger. It combines all account transactions with an account discriminator field and is the source from which `stm_txns` period aggregates are derived.

### Reference Config

Account-to-table mapping and local file paths are defined in `reference/hb-finances/statement_config.json`:

- `db_path` — SQLite connection string, default `sqlite:///statements.db`
- `accounts[name].db_table` — SQLite table name for the account
- `accounts[name].statements_path` — local filesystem path to raw statement files
- `accounts[name].statement_filetype` — file format: `csv`, `xls`, or empty

## Transaction Field Schema

### Core Fields

All POC account tables in `statements.db` share these minimum fields:

| id | field       | type  | description                           |
| -- | ----------- | ----- | ------------------------------------- |
| 01 | date        | date  | transaction date in ISO format        |
| 02 | description | str   | raw description string from statement |
| 03 | amount      | float | signed amount — negative is debit     |

### DBS Extended Fields

`TWH_DBS_MULTI_SGD` includes additional structured fields parsed from the DBS statement format:

| id | field                | type | description                          |
| -- | -------------------- | ---- | ------------------------------------ |
| 04 | Statement Code       | str  | DBS transaction type code            |
| 05 | Reference            | str  | DBS reference field                  |
| 06 | Client Reference     | str  | originator or counterparty reference |
| 07 | Additional Reference | str  | supplementary description            |
| 08 |  Misc Reference      | str  | additional miscellaneous reference   |

The leading space in ` Misc Reference` is present in the actual column name as stored in `statements.db`. This is a known ingestion artifact from the reference implementation.

## GL Table

The `GL` table is the canonical merged ledger across all accounts. It has four fields:

| id | field       | type  | description                       |
| -- | ----------- | ----- | --------------------------------- |
| 01 | date        | date  | transaction date                  |
| 02 | description | str   | raw description string            |
| 03 | amount      | float | signed transaction amount         |
| 04 | account     | str   | account name as discriminator key |

The `account` field uses the HB account name — for example, `TWH CITI` — which corresponds to the `HB account` column in the `accounts` gsheet region. Row count in the reference database: 4967 rows covering transactions from 2019 onward.

## Balances Table

The `balances` table stores month-end balance snapshots:

| id | field   | type  | description                         |
| -- | ------- | ----- | ----------------------------------- |
| 01 | date    | date  | statement close date for that month |
| 02 | year    | int   | year of the closing period          |
| 03 | month   | int   | month of the closing period         |
| 04 | account | str   | account name matching GL convention |
| 05 | balance | float | month-end closing balance           |

Row count in the reference database: 328 rows.

## stm_txns Linkage

The `stm_txns` region in the financial statements workbook is a period-level aggregate derived from the statement digital twin. It shares the same conceptual grain as `hb_exp`, `hb_inc`, and `hb_xfr` — period and account level — with these conceptual fields: `year`, `month`, `account`, `amount`, `account_id`.

The link from the `accounts` gsheet region to the statement digital twin is the `stm account` field. This field maps each account row to its corresponding table in `statements.db`, allowing per-account reconciliation against HomeBudget period totals.

Lineage path:

- Raw PDF statements downloaded to local filesystem paths in `statement_config.json`
- `statements.py` parses PDFs into per-account tables in `statements.db`
- `GL` table merges all account rows with the `account` discriminator
- `stm_txns` in the financial statements workbook aggregates GL rows per account per month

## Inspection Procedure

### Helper Script

Use `.dev/scripts/python/inspect_statements_db.py` for the standard inspection flow. This script:

- Connects to `reference/hb-finances/statements.db`
- Enumerates all tables with column lists, row counts, and three sample rows
- Saves the full evidence artifact to `.dev/.artifacts/statements_db_inspection.json`

### Command

Run from the repository root using the project virtual environment:

```powershell
.\env\Scripts\python.exe .dev\scripts\python\inspect_statements_db.py
```

### Expected Artifact

Artifact path: `.dev/.artifacts/statements_db_inspection.json`

Expected content per table:

- `columns` — list of column names in insertion order
- `row_count` — total row count
- `samples` — list of up to three sample rows as key-value dicts

## Minimum Checks

After running the inspection script, verify:

- All four POC account tables are present: `TWH_DBS_MULTI_SGD`, `TWH_CITI_USD`, `TWH_UOB_ONE_SGD`, `TWH_BOA_TRAVEL_USD`
- `GL` table is present and row count is greater than zero
- `balances` table is present and row count is greater than zero
- All account tables have `date`, `description`, and `amount` columns at minimum
- No null amounts in sample rows
- Date format is consistent ISO date pattern across all account tables
- `GL.account` values match the HB account names defined in `data/monthly-closing/accounts.json`

## Common Anomalies

- DBS extra columns — `TWH_DBS_MULTI_SGD` has eight columns; all other POC accounts have three. This is expected. The extra columns are DBS-specific structured reference fields parsed from the statement format.
- Leading space in ` Misc Reference` — the column name has a leading space in the stored schema. This is a known ingestion artifact from the reference implementation and must be handled explicitly in any schema comparison.
- Legacy tables — `COMMON_UOB_SGD` and `TWH_DBS_Visa_SGD` are present in the reference database but outside current POC account scope. Do not treat them as active statement sources.
- `TWH_CITI_USD` uses a `_USD` suffix in the table name. The account currency is USD per `accounts.json`, so the suffix is consistent — it is not an anomaly.
- Row counts are from the reference implementation data. The live operational database will have different counts across periods.
