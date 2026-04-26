---
title: Cash Reconciliation
doc_type: requirements
topic_type: owner
owner: cash-reconcile
scope: poc
reference_docs:
  - ../reference/cash-reconcile-current-workflow.md
---

# Cash Reconciliation

**Table of Contents**
- [Overview](#overview)
- [Purpose and Context](#purpose-and-context)
- [Data Sources](#data-sources)
- [Reconciliation Formula](#reconciliation-formula)
- [Workflow](#workflow)

## Overview

The POC cash reconciliation system automates the monthly process of verifying recorded cash transactions in HomeBudget against actual physical cash on hand. The system accepts a physical cash count from the user, queries HomeBudget for recorded transactions, aggregates unrecorded expenses from a Google Form, computes a reconciliation gap, and generates adjustment transactions for unexplained discrepancies with user approval.

For operational context and timing details of the current manual workflow, see [Cash Reconciliation Current Workflow](../reference/cash-reconcile-current-workflow.md).

## Purpose and Context

### Goal

Ensure the HomeBudget cash account, "Cash TWH SGD", accurately reflects the actual cash held, detecting and resolving discrepancies monthly.

### Account Scope

- **Account:** Cash TWH SGD, in SGD currency
- **Frequency:** Monthly, typically at month-end
- **User Responsibility:** Provide physical cash count; approve or modify adjustment transactions when flagged for review

### Constraints and Dependencies

- Manual cash counting is unavoidable and remains a user responsibility
- Tolerance threshold is defined in [reconciliation-engine tolerance policy](reconciliation-engine.md#tolerance-rules-and-variance-escalation)
- Gaps within tolerance trigger automatic adjustment generation
- Gaps exceeding tolerance trigger user review and approval before adjustment
- Cash account is tracked as a single-currency SGD account with no currency conversion requirements
- HomeBudget mobile app manual synchronization remains required by the current platform architecture

## Data Sources

## Canonical account naming rule

- Canonical account names come from the financial statements gsheet accounts region.
- Source-system account names are mapped to canonical names through the account mapping mechanism.

## Tolerance source of truth

Tolerance policy values are owned by docs/requirements/reconciliation-engine.md.

Cash reconciliation behavior by tolerance:

- **Within tolerance:** System automatically generates adjustment transaction with category `Balancing:Unknown`; user receives adjustment confirmation.
- **Exceeds tolerance:** System flags gap for user review; user can approve adjustment, modify gap interpretation, or investigate further. User often proceeds with adjustment creation even when exceeding tolerance.

### Input Data Sources

#### 1. Cash Expenses Google Sheet
**Purpose:** Capture cash expenses via linked Google Form  
**Format:** Google Sheet with columns:
- Date or timestamp, when expense was entered
- Expense date, when expense occurred
- Amount in SGD, presumed single currency
- Category, user-entered text that requires mapping
- Description

**Current Config Reference:** `gsheet/cash-expenses.json`
```json
{
  "wkbid": "***",
  "recent_txns": {
    "header": "recent_txns!$A$2:$D$2",
    "data": "recent_txns!$A$3:$D$500"
  }
}
```

Use the `wkbid` value from `gsheet/cash-expenses.json` at runtime. Do not publish the literal workbook ID in documentation.

**Extract Method:** Google Sheets API via sqlite-gsheet  
**Data Transformation:**
- Parse date strings
- Validate amounts as numeric and positive
- Map categories to HomeBudget category schema
- Filter by date range since last reconciliation

**Data Ingest and Staging:**
- Group GS form transactions by period and transaction category
- Create one staged aggregate row for each period and transaction category key
- Write staged aggregate rows to the `cash_staging` schema

Rerun and idempotency policy for GS cash ingest:

- GS cash inputs are treated as aggregated source input that drives HomeBudget create or update behavior.
- Re-running the same reconciliation window must be idempotent and must not create duplicate HomeBudget entries for unchanged rows.
- Flow-specific dedup key for generated HomeBudget entries is account, category, note, amount.
- If only amount changes for the same account, category, and note key, update the amount instead of creating a new entry.

#### 2. HomeBudget Wrapper Interface
**Purpose:** Source of truth for HB recorded cash transactions not recorded via the form
**Relevant resources:**
- transactions exposed by the wrapper for the cash account ledger
- accounts exposed by the wrapper, including Cash TWH SGD
- categories exposed by the wrapper for mapping and validation

**Query Window:** User-specified period, typically month-to-date  
**Primary access pattern:** list cash-account transactions for the selected period through wrapper methods

**Access Method:** HomeBudget Python wrapper package  
**Data Validation:**
- Verify account exists and is active
- Check for duplicate transaction IDs
- Validate amounts and dates

#### 3. Cash Balance Input, Current and Proposed
**Purpose:** User-provided current physical cash balance  
**Format:** closing-session Google Sheets workbook  

**Required fields per entry:**

- account name from HomeBudget
- current balance in SGD
- entry timestamp in ISO 8601 format

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
    "gap_tolerance": 20.00,
    "gap_status": "exceeds_tolerance",
    "flag_reason": "variance SGD 131.65 exceeds tolerance threshold SGD 20"
  },
  "adjustment_transaction": {
    "account": "Cash TWH SGD",
    "amount": -131.65,
    "category": "Balancing:Unknown",
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
**Destination:** HomeBudget transaction creation through the wrapper interface  
**Required Fields:**
- Date
- Account, Cash TWH SGD
- Amount as signed numeric value
- Category
- Description

## Reconciliation Formula

### Primary Reconciliation Equation

**Residual Balance Gap Formula:**
```
Residual Gap = HB Current Balance - Actual Physical Cash - Î£ Aggregated Expenses

Where:
  HB Current Balance = Sum of all Cash TWH SGD transactions from period start to end
  Actual Physical Cash = User's physical cash count in SGD
  Î£ Aggregated Expenses = Sum of expense amounts from staged wallet cash aggregate txns
```

### Interpretation

Different reconciliation gap values indicate different balance states and require different actions:

| id | gap_value | tolerance_status                | system_action             |
| -- | --------- | ------------------------------- | ------------------------- |
| 01 | â‰ˆ 0     | within cash tolerance threshold | auto-create adjustment    |
| 02 | exceeds   | > cash tolerance threshold      | flag for user review      |
| 03 | approved  | user-approved                   | create adjustment if ok'd |

**Adjustment behavior by gap value and tolerance:**

- **Gap â‰ˆ 0, within tolerance:** Reconciliation within tolerance. System automatically generates adjustment transaction with category `Balancing:Unknown`. Log session with adjustment created.
- **Gap > 0, exceeds tolerance:** HB shows MORE cash than physical count plus expenses account for. Suggests missing expenses in HomeBudget or extra transactions. System flags for user review with recommended negative adjustment. User can approve, modify, or investigate further. If approved, system creates adjustment with category `Balancing:Unknown`.
- **Gap < 0, exceeds tolerance:** HB shows LESS cash than physical count plus expenses account for. Suggests duplicate or incorrect transactions in HomeBudget, or unrecorded cash additions. System flags for user review with recommended positive adjustment. User can approve, modify, or investigate further. If approved, system creates adjustment with category `Balancing:Unknown`.

### Example Calculation

**Scenario:** February 2026 reconciliation

**Inputs:**
```
HB Beginning Balance, Feb 1: SGD 2,100.00
HB Transactions in February, net: SGD +50.00
  For example, transfer in SGD 100 and expense SGD 50.

HB Current Balance = 2,100.00 + 50.00 = SGD 2,150.00

Actual Physical Cash Count: SGD 1,884.35

Cash Expenses from Google Form, Feb and not yet in HB: SGD 347.30
```

**Calculation:**
```
Residual Gap = 2,150.00 - 1,884.35 - 347.30 = SGD -81.65
```

**Interpretation:** The residual gap is SGD -81.65, which is negative, meaning HB shows SGD 81.65 LESS cash than the physical count plus expenses account for. This could indicate:
1. Missing cash addition transaction in HB, for example an ATM withdrawal not recorded
2. Missing expense transaction in HB that's in the cash expenses form
3. Rounding error or data entry error

**Next Action:** System evaluates gap against the cash adjustment tolerance threshold. If within tolerance, adjustment is auto-created. If exceeding tolerance, user is prompted for review and approval before adjustment creation.

## Workflow

### POC Workflow Phases

The POC cash reconciliation system automates the core workflow phases while retaining user control at approval checkpoints:

**Phase 1: Input Reception**
- User provides physical cash count via closing-session Google Sheets workbook or prompted input
- System receives and stores cash balance with timestamp

**Phase 2: Data Fetch, Automated**
- Read staged wallet cash aggregate transactions for the period from the `cash_staging` schema
- Read Cash TWH SGD transactions for the period from the `hb` schema
- Validate staged inputs are present and complete for the period

**Phase 3: Calculation, Automated**
- Sum staged wallet cash aggregate transactions by period 
- Sum Cash TWH SGD transactions from the `hb` schema for the period
- Compute residual reconciliation gap using the formula defined below

**Phase 4: Adjustment Generation, Automated or User-triggered**
- Evaluate residual gap against the cash adjustment tolerance threshold
- If gap is within tolerance: automatically generate adjustment transaction
- If gap exceeds tolerance: prepare adjustment transaction and flag for user review
- All adjustments use category `Balancing:Unknown`
- Format adjustment transaction compatible with HomeBudget import

**Phase 5: Review and Approval, User Conditional**
- If gap within tolerance: notify user of auto-created adjustment; user can log session or request investigation
- If gap exceeds tolerance: flag gap and present proposed adjustment transaction for user review
- User options: approve adjustment, modify adjustment parameters, or investigate further
- User approval is required before commitment to HomeBudget

**Phase 6: Transaction Recording, Programmatic**
- Post approved adjustment transaction to `close_book`
- Post approved adjustment transaction to HomeBudget GL via the wrapper interface

**Phase 7: Reporting and Audit Trail, Automated**
- Generate reconciliation report in JSON and Markdown formats
- Log reconciliation session details including period, gap, status, and timestamp
- Archive report for audit trail
