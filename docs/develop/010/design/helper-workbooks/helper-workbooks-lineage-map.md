# Raw Statement to Workbook Lineage Map

**Document Version:** 0.2.0  
**Last Updated:** March 8, 2026  
**Status:** In Progress

## Table of Contents

1. [Overview](#overview)
2. [Lineage Principles](#lineage-principles)
3. [Statement Source Inventory](#statement-source-inventory)
4. [Lineage Flows](#lineage-flows)
5. [Manual vs Automated Steps](#manual-vs-automated-steps)
6. [Parser Contract Matrix](#parser-contract-matrix)

## Overview

This document traces lineage from raw financial sources to final database representation, using helper workbook structures only as a legacy reference model.

Target state: the app owns ingestion, parsing, mapping, validation, and reconciliation directly. Helper workbooks are deprecated from steady-state monthly closing.

## Lineage Principles

### Data Flow Stages

```
┌─────────────────┐
│ RAW STATEMENTS  │  PDF, CSV, XLSX, Online Portals
│ (bank, broker)  │
└────────┬────────┘
         │
         ├─── Automated Parser ──┐
         │                       │
         └─── Manual Entry ──────┤
                                 ▼
                    ┌────────────────────────┐
                    │  APP SOURCE ADAPTERS   │
                    │  (ingest + parse)      │
                    └───────────┬────────────┘
                                │
                       App-native ETL/Load
                                │
                                ▼
                    ┌────────────────────────┐
                    │  financial_statements  │  SQLite Database
                    │  .db                   │
                    └────────────────────────┘
```

### Lineage Tracking Fields

All imported records should include:

- **source:** Identifier for data origin (e.g., `cpf_portal_manual`, `ibkr_activity_csv`)
- **source_file:** Original file path, API endpoint, or adapter source reference
- **source_range:** Optional, used only for legacy workbook parity/backfill mode
- **import_timestamp:** When data was extracted
- **lineage_id:** Composite ID linking raw→adapter→DB

### Transition Note

Flow descriptions below include workbook-based steps to preserve historical understanding. In implementation, those workbook nodes are replaced by app-native adapters.

## Statement Source Inventory

### Available Raw Statement Files

Based on `reference/statements/` directory:

| Institution | Account Type | Statement Format | Availability | File Pattern | Key Extractable Fields |
|-------------|--------------|------------------|--------------|--------------|----------------------|
| Citibank (TWH) | Bank | PDF | ✓ | `Citibank Personal - YYYYMM.pdf` | Transactions, closing balance, cash advances |
| DBS Multi (TWH) | Bank | PDF | ✓ | `DBSStatement_YYYYMM.pdf` | Transactions, balance |
| UOB (COM) | Bank | PDF | Partial | — | Transactions, balance |
| IBKR (IBA) | Investment | CSV | ✓ | `U1109040_Activity_YYYYMM.csv` | Trades, positions, cash, NAV |
| IBKR (IRA) | Investment | CSV | ✓ | IRA activity files | Similar to IBA |
| Wells Fargo | Bank | PDF | ✓ | WF statements | Transactions, balance |
| Singtel | Utility | PDF | ✓ | Bills | Charges |
| SP Services | Utility | PDF | ✓ | Bills | Electricity, gas, water charges |
| Others | Various | PDF/CSV | ✓ | Miscellaneous | Variable |

### Online-Only Data Sources

| Source | Access Method | Data Type | Manual Entry Required |
|--------|--------------|-----------|---------------------|
| CPF Portal | Login (no API) | Account balances, contributions | Yes |
| Yahoo Finance | API/Web scraping | Exchange rates | Semi-automated |
| HomeBudget DB | Direct SQLite access | Transactions, categories, balances | Can be automated |

## Lineage Flows

### Flow 1: IBKR Statement → App Adapter → asset_balances (Legacy workbook reference)

**Source:** `reference/statements/ibkr-iba/U1109040_Activity_YYYYMM.csv`

**Extractable Entities:**
```
CSV Structure (IBKR Activity Statement):
- Header: Multiple header rows describing account, period, currency
- Account Information: Account ID, currency base
- Cash Report: Cash balances by currency
- Open Positions: Holdings with market value
- Mark-to-Market Performance Summary: NAV, P&L
- Trades: Transaction details
```

**Legacy Reference Workbook:** `gsheet/ibkr-iba.json` → `worksheet` sections

**Lineage Path:**

```
IBKR CSV → App Adapter (primary) / Workbook Parity (temporary) → Database
┌─────────────────────────┐
│ CSV: Mark-to-Market     │
│   NAV (USD): $150,000   │
└──────────┬──────────────┘
           │ USER VIEWS STATEMENT
           │ MANUALLY ENTERS INTO WORKBOOK
           ▼
┌─────────────────────────────────┐
│ worksheet!A4:P10 (ib_net_liquidity) │
│ Row: "END BAL"                   │
│ Columns: Month values            │
│ Cell[2026-02]: 151924.58         │
└──────────┬──────────────────────┘
           │ AUTOMATED UNPIVOT
           ▼
┌─────────────────────────────────┐
│ ibkr_balances Table              │
│ period_id: 2026-02               │
│ account_id: IBKR-IBA             │
│ metric_name: END BAL             │
│ amount: 151924.58                │
│ currency: USD                    │
│ source: gsheet_ibkr              │
└──────────────────────────────────┘
```

**Manual Steps:**

1. User downloads IBKR activity CSV from broker portal
2. User opens CSV and locates NAV, cash balance, securities value
3. User manually enters values into workbook matrix cells
4. Values persist in Google Sheets

**Automated Steps (target):**

1. App adapter reads IBKR CSV directly
2. Embedded parser applies matrix-equivalent mapping rules
3. Records inserted into `asset_balances`

**Lineage Fields:**

- `source`: `ibkr_activity_csv`
- `source_file`: `reference/statements/ibkr-iba/U1109040_Activity_YYYYMM.csv`
- `source_range`: Optional legacy reference (`worksheet!A4:P10`) in parity mode
- `raw_source`: "U1109040_Activity_202602.csv" (optional manual annotation)

---

### Flow 2: CPF Portal → App Adapter → asset_balances (Legacy workbook reference)

**Source:** CPF Member Portal (online, no raw file)

**Extractable Entities:**
```
CPF Portal View:
- Ordinary Account (OA) balance
- Special Account (SA) balance
- Medisave Account (MA) balance
- Contributions (monthly)
- Interest earned
- Withdrawals
```

**Legacy Reference Workbook:** `gsheet/cpf.json` → `worksheet` sections

**Lineage Path:**

```
CPF Portal → Manual Capture Adapter (primary) / Workbook Parity (temporary) → Database
┌─────────────────────────┐
│ CPF Portal View         │
│   OA Balance: $65,000   │
│   SA Balance: $55,000   │
│   MA Balance: $45,000   │
└──────────┬──────────────┘
           │ USER LOGS IN, VIEWS ONLINE
           │ MANUALLY ENTERS INTO WORKBOOK
           ▼
┌─────────────────────────────────┐
│ worksheet!A13:P20 (cpf_oa)       │
│ Row: "END BAL"                   │
│ Cell[2026-02]: 65000             │
└──────────┬──────────────────────┘
           │ AUTOMATED UNPIVOT
           ▼
┌─────────────────────────────────┐
│ cpf_balances Table               │
│ period_id: 2026-02               │
│ account_id: CPF-OA               │
│ metric_name: END BAL             │
│ amount: 65000                    │
│ currency: SGD                    │
│ source: gsheet_cpf               │
└──────────────────────────────────┘
```

**Manual Steps:**

1. User logs into CPF Member Portal
2. User navigates to account balances view
3. User records OA, SA, MA balances manually in workbook
4. User may also record contributions and interest from transaction history

**Automated Steps (target):**

1. App capture/adaptation layer records CPF values into normalized payloads
2. Embedded parser applies section and metric mapping rules
3. Records inserted into `asset_balances`

**No Raw File:** CPF does not provide downloadable statement files in standard formats.

---

### Flow 3: Bank Statement PDF + User Cash Log → App Input → cash_transactions

**Source:** `reference/statements/{bank}/Statement_YYYYMM.pdf`

**Extractable Entities (from PDF):**
```
Bank Statement Typical Structure:
- Account summary: Opening balance, closing balance
- Transaction list: Date, description, amount, running balance
- Cash withdrawals: ATM transactions
```

**Legacy Reference Workbook:** `gsheet/cash-expenses.json` → `recent_txns`

**Lineage Path:**

```
Bank Statement PDF + Cash Log → App Entry/Import (primary) / Workbook Parity (temporary) → Database
┌──────────────────────────────┐
│ Citibank Statement PDF       │
│ 2026-02-15 | ATM WD | -500   │
└──────────┬───────────────────┘
           │ USER VIEWS PDF
           │ IDENTIFIES CASH WITHDRAWAL
           │ MANUALLY ENTERS CASH EXPENSES
           ▼
┌──────────────────────────────┐
│ recent_txns!A3:D500          │
│ Row: 24/01/2026 22:51:46 |   │
│      TWH | AC | 19.8         │
└──────────┬───────────────────┘
           │ AUTOMATED ETL
           ▼
┌──────────────────────────────┐
│ cash_transactions Table      │
│ date: 2026-01-24             │
│ account_id: Cash             │
│ category: AC                 │
│ amount: 19.8                 │
│ source: gsheet_cash_expenses │
└──────────────────────────────┘
```

**Manual Steps:**

1. User reviews bank statement PDF for cash withdrawals
2. User tracks cash expenses separately (receipts, manual log)
3. User enters individual cash expenses into workbook

**Automated Steps:**

1. ETL reads workbook via Google Sheets API
2. Parser converts tabular format directly to records
3. Records inserted into `cash_transactions` table

**Lineage Gap:** Cash withdrawal from bank statement to individual cash expense breakdown is manual and not directly traceable (user-managed allocation).

---

### Flow 4: Utility Bills → App Input/Parser → shared_expense_transactions

**Source:** `reference/statements/spservices/*.pdf` (utility bills)

**Extractable Entities:**
```
SP Services Bill:
- Electricity usage (kWh) and charge
- Water usage (m3) and charge
- Gas usage (kWh) and charge
- Refuse removal fee
- GST
```

**Legacy Reference Workbook:** `gsheet/shared-expenses.json` → `records`

**Lineage Path:**

```
Utility Bill PDF → App Entry/Parser (primary) / Workbook Parity (temporary) → Database
┌──────────────────────────────┐
│ SP Services Bill PDF         │
│ Electricity: 251 kWh, $59.87 │
│ Water: 1.4 m3, $3.83         │
│ Gas: 5 kWh, $0.94            │
└──────────┬───────────────────┘
           │ USER VIEWS BILL
           │ MANUALLY ENTERS LINE ITEMS
           ▼
┌──────────────────────────────┐
│ records!A2:H1000             │
│ 2021-10-01 | 202110 |        │
│ 01 electricity | ... | 59.87│
└──────────┬───────────────────┘
           │ AUTOMATED ETL
           ▼
┌──────────────────────────────┐
│ shared_expense_transactions  │
│ date: 2021-10-01             │
│ item: 01 electricity         │
│ amount: 59.87                │
│ source: gsheet_shared_exp    │
└──────────────────────────────┘
```

**Manual Steps:**

1. User receives utility bill (PDF or physical mail)
2. User manually enters each line item with usage and cost
3. User calculates split across rooms/participants

**Automated Steps:**

1. ETL reads workbook via Google Sheets API
2. Parser converts tabular format to records
3. Records inserted into `shared_expense_transactions` table

---

### Flow 5: Yahoo Finance API → App Adapter → exchange_rates

**Source:** Yahoo Finance API (external)

**Extractable Entities:**
```
Yahoo Finance Historical Quotes:
- Date
- Currency pair (e.g., USD/SGD)
- Exchange rate
```

**Legacy Reference Workbook:** `gsheet/financial-statements.json` → `forex_rates`

**Lineage Path:**

```
Yahoo Finance API → App FX Adapter (primary) / Workbook Parity (temporary) → Database
┌──────────────────────────────┐
│ Yahoo Finance API Response   │
│ 2026-02-01: USD/SGD = 1.3456 │
└──────────┬───────────────────┘
           │ SCRIPT FETCHES RATES
           │ POSTS TO WORKBOOK
           ▼
┌──────────────────────────────┐
│ forex_rates!A3:F             │
│ 2026-02-01 | USD | 1.3456 | │
│ 2026 | 2 | USD202602         │
└──────────┬───────────────────┘
           │ AUTOMATED ETL
           ▼
┌──────────────────────────────┐
│ exchange_rates Table         │
│ date: 2026-02-01             │
│ currency_from: USD           │
│ currency_to: SGD             │
│ rate: 1.3456                 │
│ source: gsheet_forex         │
└──────────────────────────────┘
```

**Semi-Automated Steps:**

1. User runs script to fetch rates from Yahoo Finance
2. Script posts rates to workbook via Google Sheets API
3. Values persist in workbook

**Automated Steps:**

1. ETL reads workbook via Google Sheets API
2. Parser converts tabular format to records
3. Records inserted into `exchange_rates` table

**Could Be Fully Automated:** Script could post directly to database, bypassing workbook. Workbook serves as manual review layer.

---

### Flow 6: HomeBudget DB → App Adapter → account_balances

**Source:** HomeBudget SQLite database (local file)

**Extractable Entities:**
```
HomeBudget DB:
accounts Table:
- account_id, account_name, currency, type
transactions Table:
- date, account_id, category_id, amount
balances Table (if exists):
- year, month, account_id, balance
```

**Legacy Reference Workbook:** `gsheet/financial-statements.json` → `balances`

**Lineage Path:**

```
HomeBudget DB → Direct App Query Adapter (primary) / Workbook Parity (temporary) → Database
┌──────────────────────────────┐
│ HomeBudget DB                │
│ SELECT balance FROM balances │
│ WHERE account='TWH CASH SGD' │
│ AND period='2026-02'         │
│ Result: 513.90               │
└──────────┬───────────────────┘
           │ MANUAL ENTRY OR SCRIPT
           ▼
┌──────────────────────────────┐
│ balances!A2:D                │
│ 2026 | 2 | TWH CASH SGD |    │
│ 513.90                       │
└──────────┬───────────────────┘
           │ AUTOMATED ETL
           ▼
┌──────────────────────────────┐
│ account_balances Table       │
│ period_id: 2026-02           │
│ account_id: TWH CASH SGD     │
│ closing_balance: 513.90      │
│ source: gsheet_balances      │
└──────────────────────────────┘
```

**Target State:** Direct app query and load. No workbook required.

**Migration Strategy:** Run direct adapter and workbook parity side-by-side until variance checks pass.

---

## Manual vs Automated Steps

### Target-State Policy

- Helper workbooks are not required for monthly closing runs.
- Workbook reads are allowed only in `parity_mode` and `backfill_mode`.
- App-native adapters are the default and only supported production path.

### Manual Entry Summary

| Data Source | Workbook | Reason for Manual Entry | Automation Feasibility |
|-------------|----------|------------------------|----------------------|
| CPF Portal | cpf.json | No API, no downloadable file | Low (requires web scraping or login automation) |
| IBKR Statement | ibkr-iba.json | Complex PDF/CSV, user validates values | Medium (CSV parser for activity reports) |
| Cash Expenses | cash-expenses.json | Individual expense tracking, no consolidated source | Low (user-subjective categorization) |
| Utility Bills | shared-expenses.json | PDF parsing complexity, infrequent updates | Medium (PDF parser for SP Services bills) |
| Bank Statements | cash-expenses.json (indirect) | Cash withdrawal → expense breakdown is manual | Low (gap in lineage) |
| HomeBudget Balances | financial-statements.json | Legacy workflow, could be automated | High (direct DB query possible) |

### Automated Entry Summary

| Data Source | Workbook | Automation Status | Notes |
|-------------|----------|------------------|-------|
| Yahoo Finance | forex_rates | Semi-automated | Script exists, user-triggered |
| HomeBudget Transactions | N/A (direct to DB?) | Possible future automation | Not currently via workbook |

---

## Parser Contract Matrix

### Source-Specific Parser Contracts

| Source Type | Format | Parser ID | Input Structure | Output Entities | Complexity | Status |
|-------------|--------|-----------|-----------------|-----------------|------------|--------|
| IBKR Activity | CSV | PARSE-IBKR-ACTIVITY | Multi-section CSV with headers | Trades, positions, cash, NAV | Medium | Design phase |
| IBKR Flex Query | XML/CSV | PARSE-IBKR-FLEX | Configurable report structure | Customizable | Medium | Not designed |
| Citibank Statement | PDF | PARSE-CITI-PDF | Table extraction from PDF | Transactions, balance | High | Not designed |
| DBS Statement | PDF | PARSE-DBS-PDF | Table extraction from PDF | Transactions, balance | High | Not designed |
| UOB Statement | PDF | PARSE-UOB-PDF | Table extraction from PDF | Transactions, balance | High | Not designed |
| SP Services Bill | PDF | PARSE-SPSERVICES-PDF | Line item extraction | Utility charges | Medium | Not designed |
| Yahoo Finance | API/JSON | PARSE-YAHOO-FX | API response | Exchange rates | Low | Can use existing libraries |
| HomeBudget DB | SQLite | QUERY-HB-DB | Direct SQL query | Transactions, balances, categories | Low | Can use SQLAlchemy |

### Parser Priority

Based on automation feasibility and manual effort reduction:

1. **High Priority:**
   - HomeBudget DB direct query (eliminate manual balance entry)
   - Yahoo Finance API (already semi-automated, make fully automated)
   - IBKR CSV parser (structured format, high-value automation)
2. **Medium Priority:**
   - SP Services PDF parser (reduce manual entry of recurring bills)
   - Bank statement PDF parsers (high complexity, but valuable for reconciliation)
3. **Low Priority:**
   - CPF portal scraper (login complexity, infrequent changes)
   - Cash expense tracking (inherently manual categorization)

---

## Lineage Verification

### Verification Checklist

For each monthly closing:

- [ ] IBKR: Confirm workbook NAV matches CSV statement NAV
- [ ] CPF: Confirm workbook balances match portal view (screenshot or manual note)
- [ ] Cash expenses: Confirm total cash expenses reconcile with cash withdrawals
- [ ] Shared expenses: Confirm total matches utility bill amounts
- [ ] Forex rates: Confirm rates match Yahoo Finance historical quotes
- [ ] HomeBudget: Confirm workbook balances match DB query results

### Lineage Audit Trail

Recommended fields for audit:

```sql
CREATE TABLE import_lineage (
    lineage_id TEXT PRIMARY KEY,
    source_type TEXT NOT NULL,  -- 'raw_statement', 'online_portal', 'api', 'database'
    source_identifier TEXT,      -- File path, URL, DB name
    source_timestamp TEXT,       -- When source was created/accessed
    workbook_id TEXT,
    workbook_sheet TEXT,
    workbook_range TEXT,
    target_table TEXT NOT NULL,
    target_record_id TEXT,
    import_timestamp TEXT NOT NULL,
    imported_by TEXT,            -- User or script name
    verification_status TEXT,    -- 'unverified', 'verified', 'discrepancy'
    notes TEXT
);
```