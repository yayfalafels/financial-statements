---
title: Bank Statements
doc_type: requirements
topic_type: owner
owner: bank-statements
scope: poc
---
# Bank Statement Parsing

## Table of contents

- [Purpose and scope](#purpose-and-scope)
- [Reference documents](#reference-documents)
- [Reference sources](#reference-sources)
- [In-scope accounts and formats](#in-scope-accounts-and-formats)
- [Parsing module contract](#parsing-module-contract)
- [Input extraction profiles](#input-extraction-profiles)
- [Account-specific source formats](#account-specific-source-formats)
- [Transformation and normalization rules](#transformation-and-normalization-rules)
- [Validation and error policy](#validation-and-error-policy)
- [Output contract](#output-contract)
- [Determinism and idempotency](#determinism-and-idempotency)
- [Acceptance scenarios](#acceptance-scenarios)
- [POC boundary and legacy compatibility](#poc-boundary-and-legacy-compatibility)

## Purpose and scope

This page defines the requirement-level contract for bank statement parsing in POC.

It is the design-time source of truth for parser input handling, transformation rules, validation behavior, and output contracts for statement-process bank accounts.

## Reference documents

- [source systems and lineage](source-systems-lineage.md)
- [reconciliation engine](reconciliation-engine.md)
- [data model](data-model.md)
- [glossary](glossary.md)

## Reference sources

Legacy implementation evidence for design reference. These files are not requirement authority; the contract in this document takes precedence.

### Legacy parser source

File: `reference/hb-finances/statements.py`

| id | account           | function                | line |
| -- | ----------------- | ----------------------- | ---- |
| 01 | TWH DBS Multi SGD | `dbs_multi_stm_cleanup` | 314  |
| 02 | TWH UOB One SGD   | `uob_one_stm_cleanup`   | 679  |
| 03 | TWH CITI USD      | `citi_stm_cleanup`      | 272  |
| 04 | TWH Visa USD      | `boa_visa_stm_cleanup`  | 389  |

Additional config: `reference/hb-finances/statement_config.json`

### Sample statement files

Sample files present in the workspace for each in-scope account:

| id | account           | format | sample file path                                                                  |
| -- | ----------------- | ------ | --------------------------------------------------------------------------------- |
| 01 | TWH DBS Multi SGD | pdf    | `reference/statements/dbs-multi/DBSStatement_202509.pdf`                         |
| 02 | TWH DBS Multi SGD | csv    | `reference/statements/dbs-multi/transaction_history_14032026_190203.csv`         |
| 03 | TWH UOB One SGD   | pdf    | `reference/statements/uob/UOBOne_statement_202509.pdf`                           |
| 04 | TWH UOB One SGD   | excel  | `reference/statements/uob/CC_TXN_History_10032026215156.xls`                     |
| 05 | TWH CITI USD      | pdf    | `reference/statements/citi-twh/Citibank Personal - 202509.pdf`                   |
| 06 | TWH CITI USD      | csv    | `reference/statements/citi-twh/CHK_3266_20260111.csv`                            |
| 07 | TWH Visa USD      | pdf    | `reference/statements/boa-visa/BOATravel_Statement_202401.pdf`                   |
| 08 | TWH Visa USD      | csv    | `reference/statements/boa-visa/January2025_8724.csv`                             |

## In-scope accounts and formats

| id | account           | input_format_set | currency | parse_scope |
| -- | ----------------- | ---------------- | -------- | ----------- |
| 01 | TWH DBS Multi SGD | csv and pdf      | SGD      | in scope    |
| 02 | TWH UOB One SGD   | excel and pdf    | SGD      | in scope    |
| 03 | TWH CITI USD      | csv and pdf      | USD      | in scope    |
| 04 | TWH Visa USD      | csv and pdf      | USD      | in scope    |

Scope notes:

- CSV and Excel are parsing inputs for transaction rows.
- PDF is retained as archive evidence for traceability in POC.
- Wells Fargo USD is outside statement-process scope in POC.

## Parsing module contract

The parser module must provide a deterministic account-adapter pipeline with these required stages.

| id | stage                 | responsibility                                   |
| -- | --------------------- | ------------------------------------------------ |
| 01 | source loader         | load files and enumerate source rows             |
| 02 | adapter extractor     | map source columns to canonical raw fields       |
| 03 | type normalizer       | normalize dates, amounts, and text fields        |
| 04 | sign normalizer       | apply account-specific sign conventions          |
| 05 | lineage assigner      | assign file and row lineage keys                 |
| 06 | dedupe resolver       | drop exact duplicates under canonical dedupe key |
| 07 | period classifier     | assign year and month for close period           |
| 08 | validation gate       | enforce required fields and domain checks        |
| 09 | persistence writer    | write valid rows to statements schema            |

Adapter contract requirements:

- One adapter per in-scope account profile.
- Adapter behavior must be declarative from profile rules in this page.
- Adapter output must be canonical raw fields before normalization.

## Input extraction profiles

### CSV profile

| id | required token | meaning                    |
| -- | -------------- | -------------------------- |
| 01 | date           | transaction or post date   |
| 02 | description    | source narration           |
| 03 | amount         | signed amount if present   |
| 04 | debit          | debit amount if used       |
| 05 | credit         | credit amount if used      |

CSV amount derivation rule:

- If `amount` is present, use `amount`.
- Else derive as `credit - debit`.

### Excel profile

| id | required token      | meaning                        |
| -- | ------------------- | ------------------------------ |
| 01 | transaction_date    | transaction date               |
| 02 | description         | source narration               |
| 03 | transaction_amount  | transaction amount in account ccy |

Excel amount derivation rule:

- Use `transaction_amount` then apply account sign convention.

### PDF profile

| id | usage        | requirement                                       |
| -- | ------------ | ------------------------------------------------- |
| 01 | archive only | retain file identity for evidence and traceability |

## Account-specific source formats

This section defines the exact source layout contract for each in-scope bank account.

### TWH DBS Multi SGD

Source file format:

- Delimited text file parsed as CSV.
- Header preamble rows before transaction rows: `8`.

Required source columns:

| id | source column         | required | normalization target |
| -- | --------------------- | -------- | -------------------- |
| 01 | Transaction Date      | y        | `txn_date`           |
| 02 | Debit Amount          | y        | amount derivation    |
| 03 | Credit Amount         | y        | amount derivation    |
| 04 | Statement Code        | n        | `description_norm`   |
| 05 | Reference             | n        | `description_norm`   |
| 06 | Client Reference      | n        | `description_norm`   |
| 07 | Additional Reference  | n        | `description_norm`   |
| 08 | Misc Reference        | n        | `description_norm`   |

Parsing rules:

- Date format: `%d %b %Y`.
- Amount derivation: `credit_amount - debit_amount`.
- Description normalization: concatenate non-empty reference fields using `#` delimiter.

### TWH UOB One SGD

Source file format:

- Spreadsheet parsed as Excel.
- Header preamble rows before transaction rows: `9`.

Required source columns:

| id | source column              | required | normalization target |
| -- | -------------------------- | -------- | -------------------- |
| 01 | Transaction Date           | y        | `txn_date`           |
| 02 | Posting Date               | y        | row filter           |
| 03 | Description                | y        | `description_raw`    |
| 04 | Transaction Amount(Local)  | y        | amount derivation    |

Parsing rules:

- Date format: `%d %b %Y`.
- Drop rows where `Transaction Date` is null.
- Drop rows where `Posting Date` equals `PENDING`.
- Amount sign normalization: `amount_native = -1 * transaction_amount_local`.

### TWH CITI USD

Source file format:

- Delimited text file parsed as CSV.
- Skip first row and parse with fixed six-column layout.

Required source columns:

| id | source column | required | normalization target |
| -- | ------------- | -------- | -------------------- |
| 01 | Date          | y        | `txn_date`           |
| 02 | Description   | y        | `description_raw`    |
| 03 | Debit         | y        | amount derivation    |
| 04 | Credit        | y        | amount derivation    |

Parsing rules:

- Date format: `%m-%d-%Y`.
- Null debit or credit values must be treated as `0`.
- Amount derivation: `credit - debit`.

### TWH Visa USD

Source file format:

- Delimited text file parsed as CSV with header row present.

Required source columns:

| id | source column    | required | normalization target |
| -- | ---------------- | -------- | -------------------- |
| 01 | Posted Date      | y        | `txn_date`           |
| 02 | Payee            | y        | `description_raw`    |
| 03 | Amount           | y        | `amount_native`      |

Parsing rules:

- Date format: `%m/%d/%Y`.
- Amount sign is preserved from source `Amount`.

### Parser profile key differences

| id | account           | file kind | skip rows | date format  | amount logic     |
| -- | ----------------- | --------- | --------- | ------------ | ---------------- |
| 01 | TWH DBS Multi SGD | csv       | 8         | `%d %b %Y`   | credit minus debit |
| 02 | TWH UOB One SGD   | excel     | 9         | `%d %b %Y`   | negate local amount |
| 03 | TWH CITI USD      | csv       | 1         | `%m-%d-%Y`   | credit minus debit |
| 04 | TWH Visa USD      | csv       | 0         | `%m/%d/%Y`   | preserve sign      |

## Transformation and normalization rules

Required canonical transaction fields:

| id | field              | type    | req | rule                                  |
| -- | ------------------ | ------- | --- | ------------------------------------- |
| 01 | stm_txn_ref        | text    | y   | unique by account plus period plus key|
| 02 | source_account     | text    | y   | in-scope account name                 |
| 03 | txn_date           | date    | y   | ISO normalized date                   |
| 04 | posted_date        | date    | n   | keep when source provides             |
| 05 | description_raw    | text    | y   | source description                     |
| 06 | description_norm   | text    | y   | trimmed normalized description         |
| 07 | amount_native      | decimal | y   | signed amount in source currency       |
| 08 | currency           | enum    | y   | SGD or USD                             |
| 09 | statement_file_ref | text    | y   | source file identity                   |
| 10 | statement_row_ref  | text    | y   | source row identity                    |
| 11 | period_year        | int     | y   | close year                             |
| 12 | period_month       | int     | y   | close month                            |

Account sign rules:

| id | account           | sign rule                                             |
| -- | ----------------- | ----------------------------------------------------- |
| 01 | TWH DBS Multi SGD | credit minus debit when split fields are present      |
| 02 | TWH UOB One SGD   | convert outflows to negative values                   |
| 03 | TWH CITI USD      | credit minus debit when split fields are present      |
| 04 | TWH Visa USD      | preserve signed amount from canonical amount field    |

Canonical dedupe key:

- `source_account + txn_date + amount_native + description_norm`

Period assignment rules:

- Derive `period_year` and `period_month` from `txn_date`.
- Do not assign period from file name.

## Validation and error policy

Validation gates:

| id | gate                    | condition                                         | severity |
| -- | ----------------------- | ------------------------------------------------- | -------- |
| 01 | required fields present | required canonical fields are non-null            | blocking |
| 02 | date parse valid        | `txn_date` parses to valid date                   | blocking |
| 03 | amount parse valid      | `amount_native` parses to decimal                 | blocking |
| 04 | currency valid          | currency in account profile is valid              | blocking |
| 05 | account in scope        | `source_account` is in-scope account              | blocking |
| 06 | duplicate row conflict  | duplicate dedupe keys in same input batch         | warning  |

Error handling requirements:

- Any blocking validation failure must stop persistence for the affected file.
- Parser must emit a structured validation error record with file and row references.
- Warning-level duplicate conflicts may be auto-resolved by dedupe resolver and must be logged.

## Output contract

Persistence target is the app `statements` schema.

Output requirements:

- Persist only rows that pass blocking validation.
- Preserve source lineage fields for every persisted row.
- Ensure each persisted row can be joined to reconciliation by `source_account`, `txn_date`, and `amount_native`.

Minimum output artifact fields for parser run:

| id | field                 | type | req | rule                         |
| -- | --------------------- | ---- | --- | ---------------------------- |
| 01 | run_id                | text | y   | unique parser run id         |
| 02 | started_at            | text | y   | UTC ISO timestamp            |
| 03 | completed_at          | text | y   | UTC ISO timestamp            |
| 04 | files_processed       | int  | y   | count of files in run        |
| 05 | rows_persisted        | int  | y   | count of valid persisted rows|
| 06 | blocking_error_count  | int  | y   | count of blocking errors     |
| 07 | warning_count         | int  | y   | count of warning events      |

## Determinism and idempotency

Determinism requirements:

- Same input files and same parser profile must produce the same normalized rows and keys.
- Same input batch replay must produce the same persisted row set.

Idempotency requirements:

- Re-running parser on already ingested files must not create duplicate persisted rows.
- Dedupe key and lineage key behavior must guarantee stable replay outcomes.

## Acceptance scenarios

| id | scenario                     | expected result                                    |
| -- | ---------------------------- | -------------------------------------------------- |
| 01 | valid csv debit-credit input | rows parsed, normalized, persisted, no block       |
| 02 | valid excel amount input     | rows parsed with sign normalization and persisted  |
| 03 | missing required field       | file blocked with structured validation errors     |
| 04 | duplicate row replay         | no duplicate persistence on second run             |
| 05 | invalid date token           | blocking error with file and row reference         |

## POC boundary and legacy compatibility

- POC runtime may use existing legacy ingestion components.
- Requirement authority remains this document and related requirements pages.
- Design and test artifacts must align to this contract instead of implementation-specific legacy behavior.