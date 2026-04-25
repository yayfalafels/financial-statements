# CPF Domain Model

**Document Version:** 0.1.0  
**Last Updated:** March 8, 2026  
**Status:** Reference

## Table of Contents

1. [Overview](#overview)
2. [CPF Account Structure](#cpf-account-structure)
3. [Account Purpose and Rules](#account-purpose-and-rules)
4. [Monthly Contributions](#monthly-contributions)
5. [Interest Calculation](#interest-calculation)
6. [Legacy Mapping to Canonical Accounts](#legacy-mapping-to-canonical-accounts)
7. [Data Model Implications](#data-model-implications)

## Overview

The Central Provident Fund (CPF) is Singapore's comprehensive social security system. It is a mandatory savings scheme for working Singaporeans and permanent residents, covering retirement, healthcare, home ownership, family protection, and asset enhancement.

CPF accounts are individually owned but managed centrally by the CPF Board. All working adults contribute a portion of their salary (along with employer contributions) into their CPF accounts.

## CPF Account Structure

### Three Main Accounts

Every CPF member has three primary accounts:

1. **Ordinary Account (OA)**
2. **Special Account (SA)**
3. **MediSave Account (MA)**

Additionally, members who turn 55 have a fourth account:

4. **Retirement Account (RA)** - created by transferring funds from OA and SA

### Account Hierarchy

```
CPF Member
│
├─ Ordinary Account (OA)
│  └─ Used for: Housing, insurance, investment, education
│
├─ Special Account (SA)  
│  └─ Used for: Retirement, investment
│
└─ MediSave Account (MA)
   └─ Used for: Healthcare, approved medical insurance

Total CPF Balance = OA + SA + MA (+ RA if applicable)
```

## Account Purpose and Rules

### Ordinary Account (OA)

**Primary Uses:**

- Housing (downpayment, monthly mortgage, property costs)
- CPF Education Scheme (for self, children, siblings)
- CPF Investment Scheme (stocks, unit trusts, etc.)
- CPF Insurance Scheme

**Interest Rate:** 2.5% per annum (base rate) or up to 3.5% on first $20,000

**Withdrawals:**

- Generally restricted until age 55
- Can be used for approved housing and education expenses
- Can be withdrawn for investment purposes (subject to limits)

### Special Account (SA)

**Primary Uses:**

- Retirement savings
- CPF Investment Scheme (more conservative investments)

**Interest Rate:** 4% per annum (base rate) or up to 5% on first $60,000 (combined OA+SA)

**Withdrawals:**

- Highly restricted before retirement age (55)
- Primarily for retirement purposes
- More stringent investment rules

### MediSave Account (MA)

**Primary Uses:**

- Hospitalization and day surgery
- Outpatient medical care (chronic conditions)
- MediShield Life premiums (national health insurance)
- Approved private medical insurance

**Interest Rate:** 4% per annum (base rate) or up to 6% on first $60,000 (for seniors)

**Withdrawals:**

- Strictly for approved healthcare expenses
- Cannot be withdrawn in cash except under specific circumstances

## Monthly Contributions

Contributions are split between employer and employee and allocated across the three accounts based on age.

### Allocation Rates (Example for Age 35 and below)

| Total Contribution Rate | OA | SA | MA |
|------------------------|----|----|-----|
| 37% (20% employer + 17% employee) | 23% | 6% | 8% |

**Example Monthly Contribution on SGD 5,000 Salary:**

- Total contribution: SGD 1,850 (37%)
- OA: SGD 1,150 (23%)
- SA: SGD 300 (6%)
- MA: SGD 400 (8%)

### Age-Based Allocation

As members age, allocation shifts more towards MA and RA to prioritize healthcare and retirement needs.

## Interest Calculation

### Base Interest Rates

- **OA:** 2.5% p.a.
- **SA:** 4% p.a.
- **MA:** 4% p.a.

### Extra Interest

First $60,000 of combined CPF balance earns an extra 1% p.a., with up to $20,000 from OA.

**Effective Rates:**

- OA: Up to 3.5% on first $20,000
- SA: Up to 5% on next $40,000
- MA: Up to 5% on balance, 6% for seniors

### Interest Crediting

Interest is computed monthly but credited annually (December 31st).

## Legacy Mapping to Canonical Accounts

### Legacy CPF Workbook Accounts

`gsheet/cpf.json` defines five sections tracking CPF metrics:

| Workbook Section | Account ID (Implicit) | Purpose |
|-----------------|----------------------|---------|
| `cpf_total` | CPF-Total | Aggregate of all CPF accounts |
| `cpf_oa` | CPF-OA | Ordinary Account |
| `cpf_sa` | CPF-SA | Special Account |
| `cpf_ma` | CPF-MA | MediSave Account |
| `cpf_summary` | CPF-Summary | Summary metrics and derived calculations |

### Canonical Database Accounts

From the canonical account registry used by the app:

| Canonical Account ID | Type | Owner | Name | Currency | HB Account |
|---------------------|------|-------|------|----------|------------|
| TWH CPF OA SGD | retirement | TWH | CPF OA | SGD | CPF OA |
| TWH CPF SA SGD | retirement | TWH | CPF SA | SGD | CPF SA |
| TWH CPF MS SGD | savings account | TWH | CPF MS | SGD | CPF MA |

**Note:** Canonical ID uses "MS" (MediSave) but HomeBudget account name uses "MA" (MediSave Account).

### Account Mapping Rules

```python
CPF_ACCOUNT_MAP = {
    'cpf_oa': 'TWH CPF OA SGD',
    'cpf_sa': 'TWH CPF SA SGD',
    'cpf_ma': 'TWH CPF MS SGD',  # Note: MS in canonical, MA in workbook
    'cpf_total': None,  # Derived metric, no separate account
    'cpf_summary': None  # Summary/derived metrics, no separate account
}
```

### CPF-Total Calculation

CPF-Total is a **derived balance**, not a separate account:

```python
cpf_total_balance = (
    balance('TWH CPF OA SGD') +
    balance('TWH CPF SA SGD') +
    balance('TWH CPF MS SGD')
)
```

**Validation Rule:**
For each period, verify:
```
cpf_total["END BAL"] == cpf_oa["END BAL"] + cpf_sa["END BAL"] + cpf_ma["END BAL"]
```

## Data Model Implications

### Storage Strategy

**Option 1: Store CPF-Total as Separate Records**

- Store metrics from `cpf_total` section as-is
- Tag with `account_id = 'TWH CPF Total'` (create virtual account)
- Validate against sum of sub-accounts during reconciliation

**Option 2: Compute CPF-Total Dynamically**

- Do NOT store `cpf_total` metrics
- Compute totals on-the-fly by summing OA + SA + MA
- Use `cpf_total` legacy workbook data only for parity validation when enabled

**Recommendation:** **Option 2** - Avoid data duplication; compute totals dynamically.

### Metric Types

The CPF domain tracks these metrics for each account:

| Metric Name | Description | Storage |
|-------------|-------------|---------|
| BEG BAL | Opening balance (start of month) | Store or derive from prior month END BAL |
| END BAL | Closing balance (end of month) | **Store** (primary balance metric) |
| CONTRIBUTIONS | Monthly contributions from salary | **Store** (inflow) |
| WITHDRAWALS | Withdrawals for approved uses | **Store** (outflow) |
| INTEREST PAID TO OA SA | Interest credited | **Store** (inflow) |
| INTEREST PAID TO MA | Interest credited to MA | **Store** (inflow) |
| INTEREST RATE OA SA | Interest rate (%) | Store as metadata or skip |

### Table Structure

**Recommended Table:** `cpf_balances` (or integrate into `asset_balances`)

```sql
CREATE TABLE cpf_balances (
    period_id TEXT NOT NULL,
    account_id TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    amount REAL,
    currency TEXT NOT NULL DEFAULT 'SGD',
    metric_section TEXT,  -- 'cpf_oa', 'cpf_sa', 'cpf_ma', 'cpf_total', 'cpf_summary'
      source TEXT NOT NULL DEFAULT 'cpf_portal_manual',
    created_at TEXT NOT NULL,
    PRIMARY KEY (period_id, account_id, metric_name, metric_section),
    FOREIGN KEY (period_id) REFERENCES periods(period_id)
);
```

**Alternative:** Normalize into transaction-style records:

```sql
CREATE TABLE cpf_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    period_id TEXT NOT NULL,
    account_id TEXT NOT NULL,
    transaction_type TEXT NOT NULL,  -- 'contribution', 'withdrawal', 'interest', 'balance'
    amount REAL NOT NULL,
    currency TEXT NOT NULL DEFAULT 'SGD',
    source TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (period_id) REFERENCES periods(period_id)
);
```

### Reconciliation Requirements

1. **Cross-Account Summation:**
   - CPF-Total END BAL = Sum(OA, SA, MA)
2. **Balance Continuity:**
   - Current Month Opening = Prior Month Closing
3. **Balance Formula:**
   - END BAL = BEG BAL + CONTRIBUTIONS - WITHDRAWALS + INTEREST
4. **Interest Rate Validation:**
   - OA interest rate ≈ 2.5-3.5%
   - SA/MA interest rate ≈ 4-5%

### Data Quality Notes

- **Manual Entry:** CPF data is captured through app-native input from CPF portal views, no API available
- **Update Frequency:** Monthly, after CPF Board updates member accounts (typically mid-month)
- **Historical Data:** CPF portal provides historical statements; legacy workbook parity backfill is optional
- **Currency:** Always SGD (no currency conversion needed)