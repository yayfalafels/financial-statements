# Bill Payment and Shared Costs Reconciliation

## Overview

The bill payment and shared costs reconciliation procedure is a monthly process that involves downloading billing statements, parsing transaction data, allocating shared expenses, and updating HomeBudget with payment and allocation transactions. This process currently requires 72 minutes per session (1.2 hours), with an estimated 36 minutes (0.6 hours) of automation potential, representing $1.8k annual improvement value.

**Current effort:**
- Manual process: 72 minutes per session
- Improvement potential: 36 minutes per session (50% reduction)
- Annual value: $1.8k
- Budget for automation: 38 hours development, $1.8k cost

## Problem Statement

The current bill payment and shared costs procedure involves multiple manual data transfer steps:
1. Logging into billing accounts and downloading statements
2. Manually parsing statement data  
3. Copying transaction data into Google Sheets forms
4. Creating shared cost allocation entries
5. Transferring transactions from Google Sheets to HomeBudget
6. Updating consumption tracking database

This workflow suffers from:
- **Manual data entry burden** — Repetitive copying between statements, Google Sheets, and HomeBudget
- **Intermediate transfer steps** — Using Google Sheets as an intermediary increases steps and error potential
- **No audit trail** — Manual transfers are not logged for review
- **Shared cost complexity** — Shared expense allocations require manual calculation and entry
- **Time consumption** — 72 minutes per month is significant considering automation potential

## Automation Opportunity

With direct programmatic access to the HomeBudget SQLite database via the homebudget wrapper, the intermediate Google Sheet transfer steps can be eliminated. Automation can:

1. **Parse billing statements automatically** — Extract transaction data from downloaded billing statements (PDF/CSV)
2. **Fetch shared cost data** — Pull shared expense allocations from the shared-expenses Google Sheet
3. **Calculate allocations** — Compute user's share of joint expenses automatically
4. **Generate transactions** — Create HomeBudget transactions for bill payments and shared cost settlements programmatically
5. **Update consumption database** — Record consumption metrics (utilities, services) automatically
6. **Provide reconciliation report** — Generate summary of bill payments, shared costs, and variance checks

## Current Procedure

### Data Sources

| id | source | type | description |
| --- | --- | --- | --- |
| 1 | Billing statements | PDF/CSV files | Downloaded monthly billing statements from service providers (utilities, rent, subscriptions) |
| 2 | Shared-expenses Google Sheet | Google Sheets | Shared cost allocations with linked data (e.g., Splitwise settlements, or direct entries) |
| 3 | HomeBudget GL | SQLite database | General ledger for expense tracking, accessed via homebudget wrapper |
| 4 | Consumption database | SQLite/JSON | Tracking database for usage metrics (utilities consumption, services) |

### Manual Steps

| id | step | description | time (min) |
| --- | --- | --- | --- |
| 1 | Download statements | Login to billing accounts, download monthly statements (utilities, rent, subscriptions) | 10 |
| 2 | Parse statements | Manually extract transaction data (date, payee, amount, category) from PDFs or CSVs | 12 |
| 3 | Form update | Copy parsed transaction data into Google Sheets bill payment form | 8 |
| 4 | Fetch shared costs | Open shared-expenses sheet, review monthly allocations | 5 |
| 5 | Splitwise reconcile | Calculate user's share of joint expenses, create settlement transactions | 10 |
| 6 | HB transactions add | Transfer payment and allocation transactions from Google Sheets to HomeBudget | 12 |
| 7 | Consumption DB update | Record usage metrics (electricity kWh, water m³, etc.) in consumption tracking database | 8 |
| 8 | Verification | Cross-check statement totals with recorded transactions | 7 |

**Total current effort:** 72 minutes per session

### Improvement Opportunities

Based on the improvement opportunities assessment, the bill payment subprocess has 6 improvement steps:

| priority | step | improvement hrs | cumulative % | description |
| --- | --- | --- | --- | --- |
| 1 | HB txns add | 7 hrs ($330) | 18% | Automate adding transactions to HomeBudget programmatically via wrapper |
| 2 | Form update | 1.5 hrs ($71) | 22% | Eliminate Google Sheets form as intermediary |
| 3 | Statements parse | 1.9 hrs ($89) | 27% | Automate parsing of billing statement PDFs/CSVs |
| 4 | Statements upload | 0.9 hrs ($42) | 29% | Archive billing statements to S3 automatically |
| 5 | Splitwise txns add | 3.5 hrs ($165) | 38% | Automate shared cost allocation and settlement transactions |
| 6 | Consumption DB update | 5.2 hrs ($245) | 100% | Automate consumption tracking updates |

**Total improvement budget:** 38 hours, $1.8k

## Shared Costs Workflow

### Overview

Shared costs represent joint expenses split between multiple parties (e.g., housemates, partners). The current workflow uses:
- **Shared-expenses Google Sheet** — Contains allocation data for shared bills
- **Splitwise** — Deprecated and no longer used as an active source
- **HomeBudget** — Records expense and settlement transactions using `30 CC Hashemis` for shared settlement balance tracking

### Current Shared Costs Flow

```
Shared expense occurs
    ↓
[One party pays full amount]
    ↓
[Expense logged in shared-expenses sheet]
    ↓
[Monthly settlement: Apply one-third personal share and transfer logic]
    ↓
[User reviews shared-expenses sheet]
    ↓
[System creates settlement transfers in HB account 30 CC Hashemis]
    ↓
[User marks expenses as settled]
```

### Data Format: Shared-Expenses Google Sheet

Based on [gsheet/shared-expenses.json](../../gsheet/shared-expenses.json):

```json
{
  "wkbid": "1fVkiB_CXyJl2kBFEFrRb3Eb2wytWCUo1rOvveiGKZeo",
  "records": {
    "header": "records!$A$1:$H$1",
    "data": "records!$A$2:$H$1000"
  }
}
```

**Expected schema, to be validated from the live sheet at implementation start:**
- Date
- Description
- Total amount
- User's share (percentage or amount)
- Category
- Status (pending/settled)
- Payer
- Notes

## Automation Design Requirements

To automate bill payment and shared costs reconciliation, the system must:

### 1. Statement Parsing
- **Input:** Downloaded billing statement files (PDF, CSV, Excel)
- **Output:** Structured transaction data (date, payee, amount, category)
- **Requirements:**
  - Support multiple statement formats (utilities, rent, subscriptions)
  - Extract total due, due date, payment date
  - Handle multi-line bill items

### 2. Shared Cost Allocation
- **Input:** Shared-expenses Google Sheet data
- **Output:** User's share of expenses for the period
- **Requirements:**
  - Fetch data from Google Sheets API
  - Calculate user's share based on allocation percentage or fixed amount
  - Generate settlement transactions (user pays other party, or other party pays user)
  - Mark expenses as settled

### 3. Transaction Generation
- **Input:** Parsed statements + shared cost allocations
- **Output:** HomeBudget transactions (bill payments + settlements)
- **Requirements:**
  - Map statement payees to HomeBudget categories
  - Create payment transactions (credit card payments, utility payments, rent)
  - Create settlement transactions (shared cost allocations)
  - Apply consistent date and description conventions
  - Commit directly to HomeBudget by default

### 4. Consumption Tracking
- **Input:** Parsed billing statement usage metrics (kWh, m³, GB, etc.)
- **Output:** Updated consumption database records
- **Requirements:**
  - Extract consumption metrics from statements
  - Store in consumption tracking database
  - Calculate variance from historical averages
  - Flag anomalies for review

**Metrics currently in scope:** electricity kWh, water m3, gas m3

### 5. Reconciliation and Reporting
- **Input:** All generated transactions
- **Output:** Reconciliation report and variance checks
- **Requirements:**
  - Summarize total bill payments for period
  - Summarize shared cost settlements
  - Compare to budget or historical trends
  - Flag variances for review
  - Generate audit trail

## Accounts in Scope

Based on [Monthly closing documentation](../../reference/notion/Optimize monthly closing/Monthly closing 20bc378f707580f99849e024db8f12fb.md):

| id | account | type | currency | bank | description |
| --- | --- | --- | --- | --- | --- |
| 1 | TWH DBS Multi SGD | checking | SGD | DBS | Main banking settlement hub for bill payment |
| 2 | TWH UOB One SGD | credit | SGD | UOB | Main credit card for variable and discretionary expenses |
| 3 | TWH Visa USD | credit | USD | Bank of America | USD credit card for limited purchases |
| 4 | TWH CITI | checking | USD | Citibank USA | USD bank account with ACH capabilities |

**Bills in scope:**

| id | payee | account | method | status |
| --- | --- | --- | --- | --- |
| 1 | Singtel | TWH UOB One SGD | automatic payment | automated (via payee) |
| 2 | SP Services | TWH DBS Multi SGD | GIRO | automated (via GIRO) |
| 3 | Rent | TWH DBS Multi SGD | standing instructions | automated (via bank) |
| 4 | WPL Spotify | TWH DBS Multi SGD | standing instructions | automated (via bank) |
| 5 | UOB CC | TWH DBS Multi SGD | manual | requires automation |
| 6 | BOA CC | TWH CITI | ACH auto pay | automated (via payee) |

**Note:** Several bills are already automated via GIRO, standing instructions, or payee auto-pay arrangements. The automation focus is on:
- **Parsing statements** for automated bills to record transactions in HomeBudget
- **Manual bill payments** (e.g., UOB CC) that still require manual processing
- **Shared cost allocations** which are entirely manual currently

## Next Steps

To proceed with implementation:

1. **Implement parser registry and account parser adapters**
2. **Implement direct HomeBudget commit with dedupe guards**
3. **Implement shared settlement logic for account 30 CC Hashemis**
4. **Implement Singtel incremental charge posting**
5. **Implement consumption extraction and persistence for utility metrics**
6. **Implement CLI workflow and reporting commands**

Detailed design and roadmap are documented in [bill-payment-shared-costs.md](bill-payment-shared-costs.md).

## Decisions and Open Questions

### Decisions captured

1. **Splitwise usage:** Splitwise is deprecated and not used by the automation.
2. **Settlement ledger handling:** Shared settlement balance is represented in HomeBudget account `30 CC Hashemis`.
3. **Allocation default:** Shared expenses use one-third personal share and two-thirds flatmate share.
4. **Flatmate repayment model:** Flatmates repay monthly fixed amounts as transfer in entries.
5. **Commit mode:** Automation posts directly to HomeBudget by default.
6. **Singtel handling:** Placeholder internet exists, automation adds incremental charges such as data and itemized IDD.
7. **Consumption metrics:** Electricity, water, and gas are in scope.

### Open questions

1. **Shared-expenses schema validation:** Confirm live `records!A:H` column semantics.
2. **Consumption database schema:** Confirm target table design and key constraints.
3. **Variance tolerance policy:** Confirm per metric and per payee review thresholds.

---

**Version:** 1.1  
**Last updated:** 2026-02-28  
**Status:** Procedure documented, design completed, implementation planning ready
