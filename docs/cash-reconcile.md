# Cash Reconciliation

**Table of Contents**
- [Overview](#overview)
- [Purpose and Context](#purpose-and-context)
- [Current Manual Procedure](#current-manual-procedure)
- [Data Sources](#data-sources)
- [Reconciliation Formula](#reconciliation-formula)
- [Workflow](#workflow)
- [Timing and Effort](#timing-and-effort)

---

## Overview

Cash reconciliation is a monthly process that verifies recorded cash transactions in HomeBudget match actual physical cash on hand. The process aggregates cash expenses from a Google Form, compares against HomeBudget balance, and creates adjustment transactions for unexplained discrepancies. **Current process time: 30-140 minutes per session. Identified automation potential: 12 hours per year ($570 annual value).**

## Purpose and Context

### Goal
Ensure the HomeBudget cash account ("Cash TWH SGD") accurately reflects the actual cash held, detecting and resolving discrepancies monthly.

### Account Scope
- **Account:** Cash TWH SGD (SGD currency)
- **Frequency:** Monthly (typically month-end)
- **User Responsibility:** Count cash in hand, verify HB balance, review adjustment calculations

### Current Limitations
- Manual cash counting (unavoidable)
- Manual HB balance reading from app (30+ seconds)
- Intermediate Google Sheet transfers (multiple steps)
- No programmatic audit trail
- No configurable tolerance thresholds
- Manual mobile app synchronization required

---

## Current Manual Procedure

### Phase 1: Data Input and Collection

#### Step 1.1: Cash Physical Count
**Responsibility:** User  
**Input Method:** Manual count wallet/safe  
**Output:** Cash count in SGD

**Example:**
```
Physical cash on hand: SGD 1,884.35
```

#### Step 1.2: Provide Current Balance Input
**Responsibility:** User  
**System:** JSON file at `data/monthly-closing/inputs.json`  
**Format:**
```json
[
    {
        "account": "Cash TWH SGD",
        "parameter": "current_balance", 
        "timestamp": "2026-02-26T16:39:00.000Z",
        "value": 1884.35
    }
]
```

#### Step 1.3: Record HB Balance  
**Responsibility:** User  
**Process:** Manually open HomeBudget app, read Cash TWH SGD account balance  
**Manual Step Location:** Google Sheet "cash" with formula-assisted data entry  
**Time Estimate:** 1-2 minutes

---

### Phase 2: Data Acquisition (Automated via Google Sheets)

#### Step 2.1: Filter Recent Cash Expenses
**Source:** Google Sheet "cash expenses" (linked Google Form)  
**System:** Sheet formula with reference to "monthly closing session log"  
**Filter Criteria:** Transactions since last reconciliation date  
**Output:** Recent cash expense transactions

#### Step 2.2: Aggregate Transactions by Category
**System:** Google Sheet formulas  
**Grouping Dimensions:**
- By calendar month
- By expense category (mapped to HomeBudget categories)
- Single currency (SGD)

**Example Output:**
```
Feb 2026 Expenses:
- Food & Beverage: SGD 234.50
- Transport: SGD 45.00
- Entertainment: SGD 67.80
Total: SGD 347.30
```

#### Step 2.3: Query HomeBudget GL for Cash Account
**Source:** HomeBudget SQLite database  
**Account:** Cash TWH SGD  
**Query Window:** Month-to-date or user-specified period  
**Fields:**
- Transaction date
- Payee/description
- Category
- Amount (SGD)
- Transaction ID

---

### Phase 3: Calculation and Reconciliation (Automated via Google Sheets)

#### Step 3.1: Calculate Starting Balance
**Input:** Last month's ending cash balance  
**Source:** HomeBudget GL or manual input  
**Method:** Query HB for earliest month transaction or use prior month's closing value

**Formula:**
```
Starting Balance = Prior Month Ending Balance
```

#### Step 3.2: Calculate HB Current Balance
**Input:** HomeBudget GL transactions for the period  
**Method:** Sum of all cash transactions through period end  
**Formula:**
```
HB Current Balance = Starting Balance + ΣCash Transactions (HB GL)
```

#### Step 3.3: Calculate Expected Cash Balance
**Inputs:**
- Actual physical cash on hand (user input)
- Cash expenses from Google Form (aggregated)

**Formula:**
```
Expected Cash = Actual Physical Cash + ΣExpenses Not Yet in HB
```

#### Step 3.4: Calculate Residual Balance Gap
**Formula (Core Reconciliation Logic):**
```
Residual Gap = HB Current Balance - Actual Cash on Hand - ΣAggregated Cash Expenses

If Residual Gap ≠ 0, then:
  - Investigate missing transactions
  - Check for duplicates
  - Review data entry errors
  - Create adjustment transaction (if variance acceptable)
```

**Tolerance Threshold:** Currently undefined (all gaps require review)

**Example Calculation:**
```
HB Current Balance (Cash TWH SGD):    SGD 2,100.00
Actual Physical Cash:                 SGD 1,884.35
Recent Expenses Not Yet Recorded:     SGD 347.30
─────────────────────────────────────────────────
Residual Gap:      2,100.00 - 1,884.35 - 347.30 = SGD -131.65

Interpretation: HB balance is SGD 131.65 HIGHER than can be explained
by physical cash + recent expenses. Suggests missing expense transactions
or duplicate transactions in HB.
```

---

### Phase 4: Transaction Generation (Automated via Google Sheets)

#### Step 4.1: Generate Adjustment Transaction
**Purpose:** Account for unexplained balance variance  
**Trigger:** Residual Gap ≠ 0 and variance acceptable per tolerance threshold

**Transaction Format (HomeBudget compatible):**
```
Date:        [Period end date]
Account:     Cash TWH SGD
Amount:      [Residual Gap amount]
Category:    [TBD - "Adjustment" or "Rounding"]
Description: Cash reconcile adjustment [Period] ([variance reason])
Payee:       [System generated]
```

**Example:**
```
Date:        2026-02-28
Account:     Cash TWH SGD
Amount:      -SGD 131.65
Category:    Adjustment
Description: Cash reconcile adjustment Feb 2026 (untraced variance)
Payee:       System
```

---

### Phase 5: Review and Approval (Manual)

#### Step 5.1: Review Residual Gap
**Responsibility:** User  
**System:** Google Sheet "cash" presents calculated gap  
**Action Items:**
- If gap large (> tolerance): Investigate transaction errors
- If gap acceptable: Approve and proceed to recording

#### Step 5.2: Review Adjustment Transaction
**Inputs:** Proposed adjustment txn from Phase 4  
**System:** Google Sheet "homebudget" "add" sheet  
**User Action:** Confirm or modify adjustment parameters

---

### Phase 6: Data Recording (Current: Manual via Worksheet, Future: Programmatic)

**Current Workflow:**

#### Step 6.1: Copy Transaction Lines
**Responsibility:** User  
**Source:** Google Sheet "cash" or "homebudget"  
**Destination:** Google Sheet "homebudget" > "add" sheet  
**Manual Steps:** Select, copy, paste transaction rows  
**Time Estimate:** 2-5 minutes

#### Step 6.2: Execute HB Update Script
**Script:** `homebudget_update.py` (or equivalent)  
**Purpose:** Insert transactions into HomeBudget SQLite database  
**Manual Steps:**
1. Open terminal
2. Activate Python environment
3. Run: `python homebudget_update.py`
4. Verify transaction additions in HB app

**Time Estimate:** 3-5 minutes

**Limitation:** Changes in SQLite do not auto-sync to cloud; device must manually sync with mobile app.

#### Step 6.3: Mobile App Synchronization
**Responsibility:** User  
**Process:** Manual refresh in HomeBudget mobile app  
**Requirement:** No automatic sync of local database to cloud  
**Time Estimate:** 2-5 minutes

---

### Phase 7: Reporting and Close-out (Future Enhancement)

#### Step 7.1: Generate Reconciliation Report
**Contents** (proposed):
- Period covered
- Beginning and ending balances
- Transactions aggregated by category
- Residual variance and rationale
- Adjustment transactions applied
- Sign-off timestamp

**Formats** (proposed):
- JSON (audit trail)
- Markdown (human review)
- PDF (archive)

#### Step 7.2: Log Reconciliation Session
**System:** "Monthly closing session log" Google Sheet  
**Information Recorded:**
- Period date
- Reconciliation timestamp
- Beginning balance
- Ending balance
- Number of transactions
- Residual gap amount and status
- Adjustment transaction ID

---

### Complete Current Workflow Diagram

```
Phase 1: Input             Phase 2: Fetch              Phase 3: Calculate         Phase 4: Generate      Phase 5: Review
(5-10 min)                 (auto, <1 min)              (auto, <1 min)             (auto, <1 min)         (5-20 min)
   |                            |                            |                         |                    |
Count cash ───────────>  Fetch HB GL ────────────>  Sum HB balance ────>  Calc gap ────────────>  Review gap
   |                            |                            |                         |                    |
Read HB balance ────────>  Fetch expenses ──────────>  Agg expenses by cat   Gen adjust txn ─────>  Approve txn
   |                            |                            |                         |                    |
Record in JSON ─────────>  Validate data ────────────>  Calc residual ────>  Format for HB ──────>  Conditional:
                                                                                                    - If OK: approve
                                                                                                    - If large: investigate

Phase 6: Record                Phase 7: Report
(5-10 min)                     (auto, <1 min)
   |                                |
Insert to HB ────────────────>  Generate report
   |                                |
Sync mobile app ──────────────>  Log session
```

---

## Data Sources

### Input Data Sources

#### 1. Cash Expenses Google Sheet
**Purpose:** Capture cash expenses via linked Google Form  
**Format:** Google Sheet with columns:
- Date/Timestamp (when expense was entered)
- Expense date (when expense occurred)
- Amount (SGD, presumed single currency)
- Category (user-entered text, requires mapping)
- Description

**Current Config Reference:** `gsheet/cash-expenses.json`
```json
{
  "wkbid": "1ijbXG_wEP_icWH7xtbIO0bNVp4RbWPe1A5X1Q1i1nIo",
  "recent_txns": {
    "header": "recent_txns!$A$2:$D$2",
    "data": "recent_txns!$A$3:$D$500"
  }
}
```

**Extract Method:** Google Sheets API via sqlite-gsheet  
**Data Transformation:**
- Parse date strings
- Validate amounts (numeric, positive)
- Map categories to HomeBudget category schema
- Filter by date range (since last reconciliation)

#### 2. HomeBudget SQLite Database
**Purpose:** Source of truth for recorded cash transactions  
**Relevant Tables:**
- `transactions` — all cash account transactions
- `accounts` — account metadata including Cash TWH SGD
- `categories` — category definitions and mappings

**Query Window:** User-specified period (typically month-to-date)  
**Primary Query:**
```sql
SELECT date, payee, category, amount, currency 
FROM transactions 
WHERE account = 'Cash TWH SGD' 
  AND date BETWEEN ? AND ? 
ORDER BY date;
```

**Access Method:** HomeBudget SQLite connection via `homebudget` wrapper package  
**Data Validation:**
- Verify account exists and is active
- Check for duplicate transaction IDs
- Validate amounts and dates

#### 3. Cash Balance Input (Current and Proposed)
**Purpose:** User-provided current physical cash balance  
**Current Format:** JSON file at `data/monthly-closing/inputs.json`

**Schema:**
```json
[
    {
        "account": "string (HomeBudget account name)",
        "parameter": "string (e.g., 'current_balance')",
        "timestamp": "ISO 8601 datetime",
        "value": "number (SGD amount)"
    }
]
```

**Example:**
```json
[
    {
        "account": "Cash TWH SGD",
        "parameter": "current_balance",
        "timestamp": "2026-02-26T16:39:00.000Z",
        "value": 1884.35
    }
]
```

**Proposed Alternative Inputs** (for future user experience):
- CLI prompt during reconciliation
- Direct database entry in HomeBudget
- CSV/Excel upload
- Web form entry

---

### Output Data Sources

#### 1. Reconciliation Report
**Proposed Contents:**
```json
{
  "period": "2026-02",
  "timestamp": "2026-02-26T16:39:00.000Z",
  "reconciliation": {
    "beginning_balance_hb": 2100.00,
    "actual_physical_cash": 1884.35,
    "aggregated_expenses": 347.30,
    "residual_gap": -131.65,
    "gap_tolerance": 5.00,
    "gap_status": "review_required",
    "flag_reason": "variance exceeds tolerance threshold"
  },
  "adjustment_transaction": {
    "account": "Cash TWH SGD",
    "amount": -131.65,
    "category": "Adjustment",
    "description": "Cash reconcile adjustment Feb 2026",
    "status": "pending_approval"
  },
  "session_log": {
    "user": "system",
    "timestamp": "2026-02-26T16:39:00.000Z",
    "status": "in_progress"
  }
}
```

#### 2. HomeBudget Transaction Format
**Purpose:** Format for importing adjustment transactions into HB  
**Destination:** HomeBudget SQLite `transactions` table  
**Required Fields:**
- Date
- Account (Cash TWH SGD)
- Amount (signed numeric)
- Category
- Description

---

## Reconciliation Formula

### Primary Reconciliation Equation

**Residual Balance Gap Formula:**
```
Residual Gap = HB Current Balance - Actual Physical Cash - Σ Aggregated Expenses

Where:
  HB Current Balance = Sum of all Cash TWH SGD transactions from period start to end
  Actual Physical Cash = User's physical cash count (SGD)
  Σ Aggregated Expenses = Sum of expense amounts from cash expenses source
```

### Interpretation

| Gap Value | Meaning | Action |
|-----------|---------|--------|
| Gap ≈ 0 (within tolerance) | Reconciliation successful | Log session, no adjustment needed |
| Gap > 0 | HB shows MORE cash than physical + expenses account for; suggests missing expenses in HB or extra transactions | Investigate, create negative adjustment if approved |
| Gap < 0 | HB shows LESS cash than physical + expenses account for; suggests duplicate/incorrect transactions in HB or unrecorded cash additions | Investigate, create positive adjustment if approved |

### Example Calculation

**Scenario:** February 2026 reconciliation

**Inputs:**
```
HB Beginning Balance (Feb 1): SGD 2,100.00
HB Transactions in February (net): SGD +50.00
  (e.g., transfer in SGD 100, expense SGD 50)

HB Current Balance = 2,100.00 + 50.00 = SGD 2,150.00

Actual Physical Cash Count: SGD 1,884.35

Cash Expenses from Google Form (Feb, not yet in HB): SGD 347.30
```

**Calculation:**
```
Residual Gap = 2,150.00 - 1,884.35 - 347.30 = SGD -81.65
```

**Interpretation:** The residual gap is SGD -81.65 (negative), meaning HB shows SGD 81.65 LESS cash than the physical count plus expenses account for. This could indicate:
1. Missing cash addition transaction in HB (e.g., ATM withdrawal not recorded)
2. Missing expense transaction in HB that's in the cash expenses form
3. Rounding error or data entry error

**Next Action:** If gap falls within tolerance (e.g., ±SGD 5), create adjustment. If gap exceeds tolerance, investigate further.

---

## Workflow

### Complete Workflow Phases

**Phase 1: Input Collection (5-10 min)**
- User counts physical cash
- User provides input via file or prompt
- System receives cash balance

**Phase 2: Data Fetch (automatic, <1 min)**
- Query HomeBudget SQLite for Cash TWH SGD transactions
- Fetch cash expenses from Google Sheets API
- Validate all data sources accessible

**Phase 3: Calculation (automatic, <1 min)**
- Aggregate expenses by category
- Sum HB transactions
- Compute residual gap

**Phase 4: Review & Approval (5-20 min)**
- User reviews residual gap
- If within tolerance: approve adjustment
- If exceeds tolerance: investigate and correct records

**Phase 5: Record & Sync (5-10 min)**
- Insert adjustment transaction to HB database
- Trigger mobile app sync
- Verify data integrity

**Phase 6: Reporting (automatic, <1 min)**
- Generate reconciliation report
- Log session details

---

## Timing and Effort

### Current Manual Process

**Total Time: 30-140 minutes per session**

**Time Breakdown** (typical):
- Physical cash count: 5-10 min
- Manual HB balance reading: 1-2 min
- Data entry to sheet: 2-5 min
- Review and calculation (automated sheets): 2-5 min
- Copying transactions to HB sheet: 3-5 min
- Script execution: 2-3 min
- Mobile sync: 2-5 min
- Investigation (if variance large): 10-100 min
- Reporting/logging: 2-3 min

**Bottleneck:** Investigation of large variances (10-100 min), which is minimized with proper tolerance thresholds.

---

### Identified Automation Opportunities

**Annual Value of Automation:** $570 (12 hours per year)

**High-Priority Improvements:**
1. **HB Balance Programmatic Access** — Eliminate manual app opening (1-2 min)
2. **Direct Database Transaction Addition** — Replace script execution + sheet transfer (5-10 min)
3. **Tolerance-Based Auto-Adjustment** — Reduce manual review of small variance (5-20 min)
4. **Automated Mobile Sync** — Remove manual app refresh (2-5 min)
5. **Session Logging/Audit Trail** — Automate reporting (2-3 min)

**Estimated Automation Savings:** 15-40 minutes per session = ~180-480 minutes per year (3-8 hours)

---

## Next Steps (Automated System Design)

The automated cash reconciliation system will:
1. Accept cash balance input via CLI, JSON file, or web form
2. Query HomeBudget SQLite directly using homebudget wrapper
3. Fetch cash expenses from Google Sheets API programmatically
4. Perform all calculations automatically
5. Generate adjustment transactions programmatically
6. Commit transactions to HB database using homebudget wrapper
7. Generate comprehensive reconciliation report
8. Maintain audit trail of all reconciliation sessions
9. Support configurable tolerance thresholds
10. Provide CLI interface for ease of use

---

*Last Updated: 2026-02-26*  
*Component Status: Current Manual Procedure Documented; Automated Design in Progress*