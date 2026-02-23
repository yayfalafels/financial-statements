# Financial Statements Specification

**Document Version:** 0.1.0  
**Last Updated:** February 23, 2026  
**Status:** Draft

## Table of Contents

1. [Overview](#overview)
2. [Statement Types and Formats](#statement-types-and-formats)
3. [Financial Entities and Accounts](#financial-entities-and-accounts)
4. [Line Items and Hierarchies](#line-items-and-hierarchies)
5. [Calculation Rules](#calculation-rules)
6. [Currency and Accounting](#currency-and-accounting)
7. [Data Sources and Integration](#data-sources-and-integration)
8. [Output Formats and Export](#output-formats-and-export)
9. [Glossary of Financial Terms](#glossary-of-financial-terms)
10. [Known Gaps and Ambiguities](#known-gaps-and-ambiguities)

---

## Overview

The Financial Statements application processes personal financial data from the HomeBudget database and produces financial statements in PDF format. The primary user is a single operator managing multiple accounts and currencies, with a workflow spanning monthly closing, reconciliation, and reporting.

### Scope

**In Scope for MVP:**
- Personal finance statements based on HomeBudget expense and income data
- Multi-currency support (USD, SGD primary)
- Account types: wallets, brokerages (IBKR), retirement accounts (CPF)
- Monthly closing and balance reconciliation
- PDF generation and S3 upload

**Out of Scope for MVP:**
- Consolidated multi-entity reporting
- Tax optimization calculations
- Advanced forecasting or budgeting
- Automated email distribution
- Web-based UI (local CLI and Python API only)

---

## Statement Types and Formats

### 1. Income Statement (P&L)

**Purpose:** Show revenue and expenses over a period (typically monthly).

**Structure:**
```
Period: [YYYY-MM]
Currency: [USD/SGD/Multi-currency]

REVENUE
  Salary                           $X,XXX.XX
  Investment Income
    - Dividend                       $XX.XX
    - Capital Gains                  $XX.XX
  Other Income                       $XX.XX
                                   -----------
Total Revenue                      $X,XXX.XX

EXPENSES
  Living Expenses
    - Groceries                      $XX.XX
    - Utilities                      $XX.XX
    - Rent/Mortgage                  $XXX.XX
    - Transportation                 $XX.XX
  Investment Fees
    - Brokerage Fees                 $X.XX
    - Advisory Fees                  $XX.XX
  Other Expenses                     $XX.XX
                                   -----------
Total Expenses                       $X,XXX.XX

NET INCOME/(LOSS)                   $XXX.XX
```

**Frequency:** Monthly
**Aggregation:** Sum expenses/income by category over the period  
**Currency Reporting:** Each transaction converted to reporting currency at transaction date rate  
**Sign Convention:** Revenue positive, Expenses positive (net income = Revenue - Expenses)

### 2. Balance Sheet (Point-in-Time)

**Purpose:** Show assets, liabilities, and equity at a specific date.

**Structure:**
```
As of: [YYYY-MM-DD]

ASSETS
  Current Assets
    - Cash (Wallets)                 $X,XXX.XX
    - Bank Accounts                  $X,XXX.XX
  Investments
    - Brokerage (IBKR stocks)        $XX,XXX.XX
    - Cryptocurrency                 $X,XXX.XX
  Retirement
    - CPF (Singapore)                $X,XXX.XX
                                   -----------
Total Assets                       $XXX,XXX.XX

LIABILITIES
  Current Liabilities
    - Credit Card Payable            $XXX.XX
    - Loans Due                      $X,XXX.XX
                                   -----------
Total Liabilities                    $X,XXX.XX

EQUITY
  Beginning Balance (prior month)   $XXX,XXX.XX
  Net Income (current period)         $XX.XX
                                   -----------
Total Equity                       $XXX,XXX.XX

TOTAL LIABILITIES + EQUITY         $XXX,XXX.XX
```

**Frequency:** End of month (or on demand)
**Aggregation:** Latest market value for investments, transaction-based balance for accounts  
**Currency Reporting:** All assets converted to reporting currency (typically SGD) at statement date rate  
**Sign Convention:** Assets positive, Liabilities negative, Equity positive

### 3. Cash Flow Statement (Optional, not in initial MVP)

**Purpose:** Show sources and uses of cash over a period.

**Structure:**
```
Period: [YYYY-MM]

OPERATING ACTIVITIES
  Net Income                         $X,XXX.XX
  Adjustments
    - Depreciation                   $XX.XX
    - Investment Gains/(Losses)      $(XX.XX)
  Changes in Working Capital
    - Accounts Receivable            $XX.XX
    - Prepaid Expenses               $(XX.XX)
                                   -----------
Net Cash from Operations           $X,XXX.XX

INVESTING ACTIVITIES
  Purchase of Investments          $(X,XXX.XX)
  Sale of Investments               $X,XXX.XX
                                   -----------
Net Cash from Investing            $(XXX.XX)

FINANCING ACTIVITIES
  Loan Repayment                   $(XXX.XX)
  Dividend Paid                    $(XX.XX)
                                   -----------
Net Cash from Financing            $(XXX.XX)

NET CHANGE IN CASH                  $XXX.XX
Beginning Cash Balance             $X,XXX.XX
                                   -----------
Ending Cash Balance                $X,XXX.XX
```

**Note:** Detailed specification deferred pending user workflow clarification.

### 4. Budget Variance (Optional, not in initial MVP)

**Purpose:** Compare actual vs. budgeted expenses.

**Structure:**
```
Period: [YYYY-MM]

Category            Budget      Actual    Variance    % Variance
Groceries           $500.00     $520.00   $(20.00)    -4.0%
Utilities           $150.00     $145.28   $4.72       3.1%
Rent                $2,000.00   $2,000.00 $0.00       0.0%
                    ---------   ---------
Total Living        $2,650.00   $2,665.28 $(15.28)    -0.6%
```

**Note:** Budgets not yet configured in HomeBudget; deferred to backlog.

---

## Financial Entities and Accounts

### Account Types

| Account Type | Purpose | Currency | Balance Source |
|---|---|---|---|
| Wallet | Cash holding | Primary (SGD) | Manual entry + expenses |
| Bank Account | Checking/savings | USD, SGD | Manual entry + transfers |
| Brokerage (IBKR) | Securities | USD | Manual entry + P&L |
| CPF (Singapore) | Retirement fund | SGD | Manual entry from statements |
| Credit Card | Liability | USD, SGD | Manual entry + expenses |

### Account Hierarchy

```
ASSETS
├── Liquid
│   ├── SGD Wallet
│   ├── USD Wallet
│   └── Bank Accounts
├── Investments
│   ├── IBKR (dividends, unrealized gains)
│   ├── Cryptocurrency
│   └── Real Estate (future)
└── Retirement
    └── CPF (OA, SA, MA, RA accounts)

LIABILITIES
├── Credit Cards
├── Personal Loans
└── Mortgages (future)

EQUITY
├── Opening Balance
├── Retained Earnings
└── Dividends Paid (negative equity)
```

### Account Attributes

- **Account ID:** Unique identifier (e.g., "IBKR_USD", "CPF_OA")
- **Account Name:** Display name (e.g., "Interactive Brokers USD")
- **Account Type:** Category from table above
- **Currency:** Primary currency (USD, SGD, or multi-currency)
- **Opening Balance:** Beginning of period balance
- **Transactions:** Sum of inflows/outflows in period
- **Closing Balance:** End of period balance
- **Last Updated:** Timestamp of last balance entry

---

## Line Items and Hierarchies

### Income Categories

```
INCOME
├── Employment
│   └── Salary
├── Investment Income
│   ├── Dividends
│   ├── Interest
│   ├── Capital Gains (realized)
│   └── Unrealized Gains (mark-to-market)
├── Rental Income
├── Gifts/Transfers In
└── Other
```

### Expense Categories (from HomeBudget)

```
EXPENSES
├── Living Expenses
│   ├── Groceries
│   ├── Dining Out
│   ├── Utilities
│   ├── Rent/Mortgage
│   ├── Property Tax
│   ├── Home Maintenance
│   ├── Childcare
│   └── Other Living
├── Transportation
│   ├── Car Payment
│   ├── Fuel
│   ├── Maintenance
│   ├── Insurance
│   ├── Public Transport
│   └── Parking
├── Healthcare
│   ├── Medical
│   ├── Dental
│   ├── Pharmacy
│   └── Insurance
├── Personal & Grooming
│   ├── Clothing
│   ├── Haircut
│   └── Other
├── Entertainment & Leisure
│   ├── Dining Out
│   ├── Movies/Events
│   ├── Travel
│   ├── Hobbies
│   └── Other
├── Financial Services
│   ├── Brokerage Fees
│   ├── Bank Fees
│   ├── Advisory Fees
│   ├── Tax Preparation
│   └── Insurance
├── Subscriptions & Memberships
│   ├── Streaming Services
│   ├── Gym Membership
│   ├── Software
│   └── Other
├── Transfers & Allocations
│   ├── Savings Transfer
│   ├── Investment Transfer
│   └── Gifts/Donations
├── Investments
│   ├── Stock Purchases
│   ├── Crypto Purchases
│   ├── Real Estate
│   └── Other
└── Other Expenses
```

### Aggregation Rules

- **Detail Line:** Lowest level (e.g., "Groceries")
- **Sub-Total:** Aggregates details (e.g., "Living Expenses" = sum of groceries + utilities + rent + ...)
- **Total:** Highest level (e.g., "Total Expenses")
- **Filtering:** By account, date range, category, or currency

---

## Calculation Rules

### Period Definition

- **Reporting Period:** Calendar month (1st to last day)
- **Fiscal Year:** Jan 1 - Dec 31 (standard calendar year)
- **Custom Periods:** User-defined date ranges for special reports

### Revenue Recognition

- **Recognition Principle:** Accrual basis (transaction date, not clearance date)
- **Dividend Income:** Booked on ex-dividend date from broker statement
- **Salary:** Booked on payment date
- **Capital Gains:** Realized gains on trade settlement date; unrealized gains on month-end mark-to-market
- **Interest:** Booked on accrual date

### Expense Allocation

- **Basis:** Expense date in HomeBudget entry
- **Multi-Currency:** Converted to reporting currency at transaction date rate
- **Account Mapping:** Expense recorded against the account specified in HomeBudget entry
- **Category Mapping:** HomeBudget category maps to statement category (1-to-1 or many-to-1)

### Account Reconciliation

- **Balance Flow:** Opening Balance + Inflows - Outflows ± Adjustments = Closing Balance
- **Inflows:** Income, deposits, transfers in, investment sales proceeds
- **Outflows:** Expenses, withdrawals, transfers out, investment purchases
- **Adjustments:** FX gains/losses, dividends reinvested, fees, corporate actions

### Currency Conversion

- **Reporting Currency:** SGD (default)

**Conversion Rate Selection:**
- **For income/expense transactions:** Month-beginning USD/SGD rate (from Yahoo Finance for first business day of month)
- **For balance sheet accounts:** Month-end USD/SGD rate (from Yahoo Finance for last calendar day of month)
- **FX variance:** Booked as a separate "FX Gain/Loss" transaction to reconcile the difference between opening + movements at average rate vs. closing at month-end rate

**Transaction Conversion:**
- USD transaction → Convert to SGD using month-beginning rate
- SGD transaction → No conversion needed
- Both amounts stored: transaction in original currency, converted SGD amount

**Account Conversion:**
- Balance sheet accounts marked-to-market at month-end rate
- Opening balance + inflows/outflows at trans date rates +/- FX variance = Closing balance

- **Rounding:** 2 decimal places (.01 SGD); accumulated FX rounding booked to "FX Gains/Losses"

### Multi-Account Aggregation

- **Consolidated View:** Sum all accounts converted to reporting currency
- **By-Account View:** Each account shown in its native currency and converted value
- **Elimination:** No inter-company eliminations (personal finance only)

### Adjustment and Accrual Rules

- **Unrealized Gains/Losses:** Booked monthly on investment accounts (mark-to-market fair value)
- **Dividend Accrual:** Booked on record date if not yet received; reversed on payment date
- **FX Gains/Losses:** Computed on each transaction and month-end balance movements
- **Deferred Revenue:** Not applicable (personal finance)
- **Doubtful Debt Provision:** Not applicable

---

## Currency and Accounting

### Reporting Standards

- **Basis:** Personal financial accounting (modified accrual)
- **Standard:** No formal GAAP/IFRS compliance required; cash basis adjusted for timing differences
- **Period:** Calendar month (standard), fiscal year (Jan-Dec)

### Multi-Currency Handling

**Transaction Recording:**
- Home currency (SGD) native transactions recorded at face value
- Foreign currency (USD) transactions recorded at spot rate on transaction date
- Both amounts stored: original currency amount and converted SGD amount

**Consolidation Rule:**
- All statement line items shown in SGD
- USD accounts shown with USD balance and SGD converted balance on same line
- Total line shows SGD consolidated amount

**FX Gain/Loss Booking:**
- Unrealized gains/losses computed on month-end date diff of converted balances
- Realized gains/losses computed when position closed or converted
- Monthly FX impact booked to "Investment Income > Unrealized Gains" account

### Audit Trail

- **Transaction Audit:** Every HomeBudget entry includes date, category, account, amount, notes, user
- **Balance Audit:** Monthly opening/closing balances by account with FX adjustment detail
- **Calculation Audit:** All formulas documented; intermediate calculations exportable for review
- **Change Log:** Session logs capture every update, timestamp, and user; rollback snapshots for recovery

---

## Data Sources and Integration

### HomeBudget Database

**Connection:** Local SQLite database at path specified in config

**Key Tables:**
- `accounts` — Account definitions (checking, savings, investment, credit)
- `categories` — Expense/income categories and subcategories
- `transactions` — Journal entries (date, amount, account, category, notes)
- `balances` — Month-end balance snapshot by account
- `fx_rates` — Historical USD/SGD rates by date

**Mapping:**
- HomeBudget category → Statement category (1-to-1 mapping in config)
- HomeBudget account → Statement account (1-to-1 mapping)
- Transaction.amount + fx_rate → Reporting currency amount

**Data Quality:**
- Assumption: All transactions dated within the year and valid currencies
- Validation: Missing account/category references rejected with error
- Reconciliation: Must match monthly balance snapshot in HomeBudget

### Google Sheets Integration

**Workbooks:**
- **Main workbook (ID: `1-Gy9kEUF0RbKWsztoZbVwbi65PXNhP1qPdylXod5JBE`):** Statement templates, balances, forex rates
- **IBKR helper workbook (ID: `1i_ITkqvLRw5AFVmzqLaHp6PHlA2OERi3E-la00Ukngg`):** Interactive Brokers P&L and holdings parsing
- **CPF helper workbook (ID: `1x9Dfq5RVwvmCGqX9aIgCRoarkhLYR3mWGmRRvQnLkbo`):** Singapore CPF statement parsing and balance updates

**Main Workbook Sheets and Ranges:**
- `balances!A1:D` — Monthly account balances (year, month, account name, balance SGD)
- `forex_rates!A1:F` — Historical USD/SGD rates (year, month, date, currency, rate_SGD, ...)
- Other sheets: Income statement template, balance sheet template, reconciliation tracking

**Helper Workbook Sheets:**
- **IBKR:** `worksheet` — Position listing, P&L, corporate actions, holdings as of each month
- **CPF:** `worksheet` — CPF statement extract (OA, SA, MA, RA balances, contributions, interest)

**Update Pattern:**
- Pre-flight: Fetch latest forex rates from Yahoo Finance, update `forex_rates` sheet
- Account update:
  - Wallets: Direct read from HomeBudget
  - IBKR: User manual update to helper workbook, Python reads `worksheet` for balance and P&L
  - CPF: User manual update to helper workbook, Python reads `worksheet` for balance
- Report generation: Fetch `balances`, `forex_rates` from main workbook; compute income and balance sheets locally; write summary back to main workbook

**sqlite-gsheet Integration:**
- `sqlite-gsheet` library wraps Google Sheets API with Pandas
- Configured via `gsheet_config.json` (workbook IDs, ranges, data types, credentials path)
- Pandas DataFrame → Sheet (batch write), Sheet → Pandas DataFrame (batch read)
- Credentials: `.credentials/client_secret.json` (OAuth token from Google)

### External Data Sources

**Yahoo Finance (Forex):**
- URL: `https://sg.finance.yahoo.com/quote/SGD%3DX/`
- Monthly USD/SGD rates for historical conversion
- Refresh: Monthly (before period close)

**Brokerage APIs (Future):**
- IBKR TWS API for real-time position and P&L data
- Not in initial MVP; deferred to backlog

---

## Output Formats and Export

### PDF Statement

**Format:** Letter size (8.5" × 11"), standard fonts (Arial/Verdana)

**Contents:**
1. Cover page: Title, period, generated date, confidentiality notice
2. Income statement: Revenue, expenses, net income
3. Balance sheet: Assets, liabilities, equity at period end
4. Supporting schedules:
   - Account detail: Opening balance, inflows, outflows, closing balance
   - Category detail: Breakdown of revenue/expenses by category
   - Currency detail: Summary by currency with FX impacts
   - FX schedule: Realized and unrealized FX gains/losses

**Export:**
- PDF file stored locally under `data/{YYYY}/{YYYY-MM}/` directory
- File naming: `financial-statement_{YYYY-MM-DD}.pdf`
- S3 upload: Copy to S3 bucket `s3://financial-statements/{YYYY}/{YYYY-MM}/` with same filename

### Excel Workbook

**Format:** .xlsx with multiple sheets (optional export)

**Sheets:**
- `Summary` — Income statement and balance sheet side-by-side
- `Details` — Detailed transaction list with category mapping
- `Schedules` — Supporting schedules (account detail, category detail, FX detail)
- `Config` — Reporting configuration and calculation notes

### CSV Export

**Format:** Comma-separated values, UTF-8 encoding

**Files:**
- `income-statement_{YYYY-MM}.csv` — Line items and amounts
- `balance-sheet_{YYYY-MM}.csv` — Assets, liabilities, equity
- `transactions_{YYYY-MM}.csv` — All input transactions for verification

### Google Sheets

**Update Strategy:**
- Fetch statement data from `balances` sheet (input)
- Compute calculations locally
- Write summary back to Google Sheets `statements` sheet with cached values
- Preserve formulas and pivot tables in Google Sheets for ad-hoc analysis

---

## Glossary of Financial Terms

| Term | Definition | Example |
|---|---|---|
| **Accrual** | Income or expense recognized when earned/incurred, not when paid | Dividend booked on ex-date, not payment date |
| **Asset** | Resource owned with future economic value | Cash, stocks, real estate |
| **Balance Sheet** | Statement of assets, liabilities, and equity at a point in time | "As of Dec 31, 2024" |
| **Category** | Classification of income/expense; determines statement line item | "Groceries", "Salary", "Brokerage Fees" |
| **Cash Basis** | Revenue and expenses recorded when cash moves | Opposite of accrual |
| **Consolidated** | Combined view across multiple accounts/entities | "Total Assets across all wallets" |
| **Equity** | Ownership interest; Assets - Liabilities = Equity | Net worth |
| **Expense** | Cost incurred in operations; reduces equity | Groceries, utilities, fees |
| **FX Gain/Loss** | Profit/loss from currency fluctuation | USD dropped; SGD value of USD account fell |
| **Income** | Revenue earned; increases equity | Salary, dividends, interest |
| **Liability** | Obligation to pay or deliver goods/services | Credit card debt, loans |
| **Mark-to-Market** | Fair value based on current market price | Stock portfolio valued at today's closing price |
| **P&L (Income Statement)** | Statement of revenue and expenses over a period | "Jan 2024 profit/loss" |
| **Realized Gain** | Profit on a completed transaction | Sold stock for $200, bought for $150 = $50 realized gain |
| **Reporting Currency** | Currency in which statements are prepared | SGD |
| **Subcategory** | Second level of classification under a category | "Salary" is subcategory of "Employment" income |
| **Unrealized Gain** | Profit on open position not yet sold | Stock worth $200, cost $150 = $50 unrealized gain |

---

## Known Gaps and Ambiguities

### Clarification Needed

1. **Statement Types:** Are cash flow and budget variance statements required for MVP, or income/balance only?
   - *Current assumption:* Income statement and balance sheet required; cash flow and budget variance deferred

2. **Expense Allocation:** How should multi-account transfers be handled? (e.g., moving funds from checking to brokerage)
   - *Current assumption:* Transfers are not expenses; booked as "Transfers" and eliminated in consolidated view

3. **Investment Valuation:** How frequently should unrealized gains be computed? (daily, weekly, monthly?)
   - *Current assumption:* Monthly at period-end; historical close prices used for month-end valuation

4. **CPF Accounts:** Should CPF contributions, withdrawals, and interest be tracked separately?
   - *Current assumption:* Manual balance entry only; no detailed CPF transaction tracking in MVP

5. **Loan Accounting:** Should loan principal and interest be separated, or recorded as single payment?
   - *Current assumption:* Loan principal recorded to liability account; interest as separate expense

6. **Depreciation:** Should home, car, or other long-lived assets be depreciated?
   - *Current assumption:* No depreciation; personal assets held at cost

7. **Tax Accounting:** Should tax provisions or deferred tax be calculated?
   - *Current assumption:* No tax provisions; deferred to tax planning module (backlog)

8. **Budget Variance:** Is the budget variance report needed if budgets not yet in HomeBudget?
   - *Current assumption:* Deferred to backlog pending user workflow clarification

### To Be Resolved with User

- Preferred financial reporting standard (cash vs. accrual, GAAP alignment)?
- Required disclosure and audit trail detail for period-end close?
- Any regulatory or compliance requirements (banking, investment licensing)?
- Desired reconciliation and review procedures (who reviews, when, sign-off)?
- Long-term vision: investment portfolio analysis, tax planning, retirement projections?

---

## References

- [docs/mvp-design.md](docs/mvp-design.md) — MVP design and workflow
- [docs/workflow.md](docs/workflow.md) — Detailed financial statements workflow
- [docs/homebudget.md](docs/homebudget.md) — HomeBudget interface guide
- [docs/google-sheets.md](docs/google-sheets.md) — Google Sheets integration
- [reference/hb-finances/](reference/hb-finances/) — Reference implementation code
- [docs/repository-layout.md](docs/repository-layout.md) — Project structure

---

**Document Status:** Draft  
**Next Review:** After Step 2 (Data Source Inventory)  
**Assigned To:** @taylorhickem  
