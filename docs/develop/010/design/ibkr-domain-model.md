# IBKR Domain Model

**Document Version:** 0.1.0  
**Last Updated:** March 8, 2026  
**Status:** Reference

## Table of Contents

1. [Overview](#overview)
2. [IBKR Account Types](#ibkr-account-types)
3. [Account Structure](#account-structure)
4. [Asset Components](#asset-components)
5. [Legacy Mapping to Canonical Accounts](#legacy-mapping-to-canonical-accounts)
6. [Data Model Implications](#data-model-implications)
7. [Statement Sources](#statement-sources)

## Overview

Interactive Brokers (IBKR) is a multinational brokerage firm offering trading and investment services. The user has two types of accounts with IBKR:

1. **IBA** - Individual Brokerage Account (taxable investment account)
2. **IRA** - Individual Retirement Account (US tax-advantaged retirement account)

Both accounts hold investments in securities (stocks, ETFs, bonds, etc.) and cash in multiple currencies.

## IBKR Account Types

### Individual Brokerage Account (IBA)

**Type:** Taxable investment account

**Purpose:**

- General purpose investing and trading
- No contribution limits
- No withdrawal restrictions (except settlement periods)
- Capital gains taxed annually

**Tax Treatment:**

- Dividends taxed as income
- Capital gains taxed when realized
- Foreign withholding tax applied on international dividends (typically 30% US, may be reduced by tax treaty)

**Typical Holdings:**

- US stocks and ETFs
- International stocks
- Bonds
- Options (if approved)
- Cash (multiple currencies)

**Base Currency:** USD (user preference)

### Individual Retirement Account (IRA)

**Type:** US tax-advantaged retirement account (Traditional IRA or Roth IRA)

**Purpose:**

- Long-term retirement savings with tax benefits
- Contribution limits (e.g., $7,000/year in 2024, $8,000 if age 50+)
- Withdrawal restrictions before age 59½ (penalties apply unless exceptions met)

**Tax Treatment (Traditional IRA):**

- Contributions may be tax-deductible
- Growth is tax-deferred
- Withdrawals taxed as ordinary income in retirement

**Tax Treatment (Roth IRA):**

- Contributions made with after-tax dollars
- Growth is tax-free
- Qualified withdrawals in retirement are tax-free

**Typical Holdings:**

- Similar to IBA (stocks, ETFs, bonds)
- Cash (multiple currencies)

**Base Currency:** USD

**Restrictions:**

- Early withdrawal penalties (10% + income tax) if withdrawn before 59½
- Required Minimum Distributions (RMDs) starting at age 73 (for Traditional IRA)

## Account Structure

### IBA and IRA Composition

Both accounts consist of:

1. **Cash Component**
   - Cash held in various currencies (primarily USD, but may hold SGD, EUR, etc.)
   - Used for trading, dividends, interest
   - May be positive (cash balance) or negative (margin loan)
2. **Securities Component**
   - Market value of all stock positions
   - Market value of bond positions
   - Market value of ETF positions
   - Options positions (if applicable)
3. **Net Liquidation Value (NAV)**
   - Total account value = Cash + Securities + Other Assets - Liabilities
   - Primary metric for account balance
   - Fluctuates daily with market prices

### Account Hierarchy

```
IBKR Member
│
├─ Individual Brokerage Account (IBA)
│  │
│  ├─ Cash (USD, SGD, etc.)
│  ├─ Securities (Stocks, ETFs, Bonds)
│  └─ NAV (Total Account Value)
│
└─ Individual Retirement Account (IRA)
   │
   ├─ Cash (USD)
   ├─ Securities (Stocks, ETFs, Bonds)
   └─ NAV (Total Account Value)
```

## Asset Components

### Net Liquidation Value (NAV)

**Definition:** The total value of all assets if the account were liquidated at current market prices.

**Formula:**
```
NAV = Cash + Market Value of Securities + Other Assets - Margin Loans - Other Liabilities
```

**Currency:**

- Reported in base currency (USD)
- Also converted to reporting currency (SGD) using current exchange rates

### Cash

**Definition:** Uninvested cash in the account

**Characteristics:**

- Can be positive (cash available) or negative (margin debt)
- Earns interest if positive (IBKR pays interest on cash balances)
- Charged interest if negative (margin loan interest)
- May be held in multiple currencies

**Reporting:**

- Primary currency: USD
- May have SGD cash for Singapore stock trading

### Securities

**Definition:** Market value of all investment positions

**Components:**

- **Stocks:** Individual company shares
- **ETFs:** Exchange-traded funds
- **Bonds:** Fixed income securities
- **Options:** Derivative contracts (if applicable)

**Valuation:**

- Mark-to-market daily using closing prices
- Foreign securities converted to USD at current FX rates

### Profit & Loss (P&L)

**Types:**

1. **Realized P&L:** Profit/loss from closed positions (trades executed and settled)
2. **Unrealized P&L:** Paper profit/loss on open positions (market value vs. cost basis)
3. **Total P&L:** Realized + Unrealized

**Tracking:**

- Month-to-date (MTD)
- Year-to-date (YTD)
- Inception-to-date (ITD)

## Legacy Mapping to Canonical Accounts

### Legacy IBKR Workbook Accounts

`gsheet/ibkr-iba.json` defines four sections tracking IBA metrics:

| Workbook Section | Account ID (Implicit) | Purpose |
|-----------------|----------------------|---------|
| `ib_net_liquidity` | IBKR-IBA | Net Liquidation Value (NAV) and returns |
| `ib_cash` | IBKR-IBA | Cash balances by currency |
| `ib_securities` | IBKR-IBA | Securities market value and breakdown |
| `ib_summary` | IBKR-IBA | Summary metrics and P&L |

**Note:** Workbook currently tracks only IBA, not IRA (IRA may be in separate workbook or not tracked).

### Canonical Database Accounts

From the canonical account registry used by the app:

| Canonical Account ID | Type | Owner | Name | Currency | HB Account |
|---------------------|------|-------|------|----------|------------|
| TWH IB POSITION USD | investment | TWH | IB POSITION | USD | IB POSITION USD |
| TWH IB CASH USD | savings account | TWH | IB CASH | USD | TWH IB USD |
| TWH IB IRA USD | retirement | TWH | IB IRA | USD | IB IRA USD |

### Account Mapping Rules

```python
IBKR_ACCOUNT_MAP = {
    # IBA workbook sections map to two canonical accounts
    'ib_net_liquidity': {
        'nav': 'TWH IB POSITION USD',  # NAV reflects total account value
        'cash': 'TWH IB CASH USD'       # Cash component tracked separately
    },
    'ib_cash': 'TWH IB CASH USD',
    'ib_securities': 'TWH IB POSITION USD',
    'ib_summary': 'TWH IB POSITION USD',
    
    # IRA (if tracked separately)
    'ib_ira': 'TWH IB IRA USD'
}
```

### IBA Account Split Logic

**IBKR-IBA legacy workbook section** represents a **single brokerage account (IBA)** but maps to **two canonical accounts** in the database:

1. **TWH IB CASH USD** - Cash component only
2. **TWH IB POSITION USD** - Securities/positions component + total NAV

**Rationale:**

- Allows separate tracking of liquid cash vs. invested assets
- Matches HomeBudget account structure (separate cash and position accounts)
- Facilitates reconciliation of cash flows vs. market value changes

**Mapping Strategy:**

| Metric in Workbook | Canonical Account | Notes |
|--------------------|-------------------|-------|
| NAV USD | TWH IB POSITION USD | Total account value |
| NAV SGD | TWH IB POSITION USD | Converted to SGD |
| Cash USD (from ib_cash section) | TWH IB CASH USD | Cash balance |
| Cash SGD (from ib_cash section) | (Separate or included in TWH IB CASH USD) | Multi-currency handling |
| Securities Market Value | TWH IB POSITION USD | Stocks + ETFs + Bonds |
| P&L, Returns | TWH IB POSITION USD | Performance metrics |

**Reconciliation:**
```
NAV = Cash + Securities + Other
TWH IB POSITION USD (NAV) = TWH IB CASH USD (Cash) + Market Value of Securities
```

## Data Model Implications

### Storage Strategy

**Option 1: Store Both NAV and Component Balances**

- Store NAV as balance for TWH IB POSITION USD
- Store Cash as balance for TWH IB CASH USD
- Validate: NAV ≈ Cash + Securities

**Option 2: Store NAV Only, Derive Components**

- Store only NAV for TWH IB POSITION USD
- Reference legacy parity source for cash/securities breakdown

**Recommendation:** **Option 1** - Store both for auditability and separate cash flow tracking.

### Metric Types

The IBKR domain tracks numerous metrics:

| Metric Name | Description | Storage Priority | Account |
|-------------|-------------|-----------------|---------|
| BEG BAL | Opening NAV | Derive from prior END BAL | Position |
| END BAL | Closing NAV | **Store** | Position |
| INCOME | Dividends + Interest | **Store** | Position |
| RETURN | % Return for period | Store or compute | Position |
| RETURN YTD | Year-to-date % return | Store or compute | Position |
| Cash USD | Cash balance in USD | **Store** | Cash |
| Cash SGD | Cash balance in SGD | Store if held | Cash |
| Securities Market Value | Total securities value | Store | Position |
| Realized P&L | Closed position gains/losses | Store | Position |
| Unrealized P&L | Open position gains/losses | Store | Position |

### Table Structure

**Recommended Table:** `ibkr_balances` (or integrate into `investment_balances`)

```sql
CREATE TABLE ibkr_balances (
    period_id TEXT NOT NULL,
    account_id TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    amount REAL,
    currency TEXT NOT NULL,  -- 'USD' or 'SGD'
    metric_section TEXT,  -- 'ib_net_liquidity', 'ib_cash', 'ib_securities', 'ib_summary'
      source TEXT NOT NULL DEFAULT 'ibkr_statement_import',
    created_at TEXT NOT NULL,
    PRIMARY KEY (period_id, account_id, metric_name, metric_section),
    FOREIGN KEY (period_id) REFERENCES periods(period_id)
);
```

**Alternative:** Separate tables for balances vs. performance:

```sql
CREATE TABLE investment_balances (
    period_id TEXT NOT NULL,
    account_id TEXT NOT NULL,
    balance_type TEXT NOT NULL,  -- 'nav', 'cash', 'securities'
    amount REAL NOT NULL,
    currency TEXT NOT NULL,
    source TEXT NOT NULL,
    created_at TEXT NOT NULL,
    PRIMARY KEY (period_id, account_id, balance_type, currency)
);

CREATE TABLE investment_performance (
    period_id TEXT NOT NULL,
    account_id TEXT NOT NULL,
    metric_type TEXT NOT NULL,  -- 'income', 'return_mtd', 'return_ytd', 'realized_pl', 'unrealized_pl'
    value REAL NOT NULL,
    currency TEXT,
    source TEXT NOT NULL,
    created_at TEXT NOT NULL,
    PRIMARY KEY (period_id, account_id, metric_type)
);
```

### Multi-Currency Handling

IBKR accounts hold assets in multiple currencies:

**Strategy:**

1. Store amounts in original currency (USD, SGD)
2. Use `currency` field to track denomination
3. Convert to reporting currency (SGD) using `exchange_rates` table for consolidated reports

**Example Records:**
```
period_id='2026-02', account_id='TWH IB POSITION USD', metric='END BAL', amount=151924.58, currency='USD'
period_id='2026-02', account_id='TWH IB POSITION USD', metric='END BAL', amount=204590.88, currency='SGD' (converted)
```

**Decision:** Store both USD and SGD values or only USD and convert on-the-fly?

**Recommendation:** Store USD only in `ibkr_balances`, convert to SGD in reporting layer using `exchange_rates` table.

## Statement Sources

### IBKR Activity Statement (CSV)

**File Pattern:** `U{account_number}_Activity_{YYYYMM}.csv`

**Example:** `reference/statements/ibkr-iba/U1109040_Activity_202510.csv`

**Contents:**

- Account summary (NAV, cash, securities)
- Transaction list (trades, dividends, fees)
- Open positions (symbol, quantity, market value)
- Cash balances by currency
- P&L summary

**Automation Potential:** **High** - CSV is structured and consistent

### IBKR Flex Query (Custom Report)

**Format:** XML or CSV

**Contents:** User-configurable fields

**Automation Potential:** **High** - Can be automated via API

### Manual Entry Workflow (Current)

1. User logs into IBKR account portal
2. Downloads monthly activity statement (PDF or CSV)
3. Reviews NAV, cash, securities values
4. Captures values in app-native input flow or direct parser output

**Lineage:**
```
IBKR CSV → Manual Review or Parser → App Adapter → Database
```

### Automation Opportunity

**Parser for IBKR CSV:**

- Extract NAV, cash, securities from CSV
- Post values directly to the database through app adapters
- Validate against prior month for continuity

## Reconciliation Requirements

1. **NAV Composition:**
   - NAV ≈ Cash + Securities (allow small variance for accrued interest, pending trades)
2. **Balance Continuity:**
   - Current Month Opening = Prior Month Closing (adjusted for deposits/withdrawals)
3. **Currency Crosscheck:**
   - NAV USD * FX Rate ≈ NAV SGD (validate against `exchange_rates` table)
4. **P&L Reconciliation:**
   - Closing NAV = Opening NAV + Income + Realized P&L + Unrealized P&L - Withdrawals + Deposits

### Data Quality Notes

- **Manual Entry:** Current workflow is manual from statements
- **Update Frequency:** Monthly, after month-end statement is available
- **Historical Data:** IBKR provides historical statements; legacy workbook parity backfill is optional
- **Currency:** Primarily USD, with SGD conversion tracking
- **Automation Feasibility:** High, given structured CSV format