# Financial Statements Application Design Plan

**Document Type**: Design Planning (not implementation)  
**Status**: In Progress - Hybrid workflow with AI-guided discovery and design decisions  
**Created**: 2026-02-28  
**Target Output**: Set of coherent design documents in `docs/develop/`

---

## Table of Contents

- [Overview](#overview)
- [Environment Setup and Development Discipline](#environment-setup--development-discipline)
- [Source Data Inspection Strategy](#source-data-inspection-strategy)
- [Design Assumptions](#design-assumptions)
- [Phase 1: Discovery and Analysis](#phase-1-discovery--analysis)
- [Phase 2: High-Level Architecture Design](#phase-2-high-level-architecture-design)
- [Phase 3: Domain Model Design](#phase-3-domain-model-design)
- [Phase 4: Data Layer Design](#phase-4-data-layer-design)
- [Phase 5: Workflow and Orchestration Design](#phase-5-workflow--orchestration-design)
- [Phase 6: Module Interface Design](#phase-6-module-interface-design)
- [Phase 7: Error Handling and Validation Design](#phase-7-error-handling--validation-design)
- [Document Ordering and Dependencies](#document-ordering-and-dependencies)
- [Phase 8: Cleanup](#phase-8-cleanup)

---

## Overview

This document guides the design of the Financial Statements Application: a Python-based monthly closing workflow that orchestrates data from multiple sources (HomeBudget, Google Sheets, bank statements, forex APIs) and produces consolidated financial reports.

### What This Is NOT

- **Not an implementation plan**: No code templates, test cases, or deployment scripts here
- **Not a complete specification**: Details left for implementation phase
- **Not a reinvention of existing tools**: Leverages homebudget and sqlite-gsheet packages as-is

### What This Is

**A design roadmap** that:
1. Resolves inconsistencies in existing documentation
2. Establishes clear architectural boundaries
3. Defines data flows and transformation boundaries
4. Creates a modular, extensible structure
5. Leaves implementation details for the implementation plan

### Key Design Principle: Harmonization, Not Reinvention

The app brings together 5+ independent systems (HomeBudget, Google Sheets, bank statement files, exchange rate APIs, local config) with **different data models and update cadences**. The design focuses on:

- **statements: single source of truth**: The statements are the ultimate source of truth for account balances and transactions.
- **Modular workflows**: Independent closure steps that can be reordered or parallelized
- **Shared error handling and validation**: Consistent across all modules
- **Bespoke accounting logic**: Custom rules and accounting conventions.
- **Custom persistence**: Replace Google Sheets storage with local sqlite DB.

### Workbook Deprecation Policy

- Helper workbooks are deprecated as operational dependencies.
- Workbook logic and data models must be migrated into app modules and SQLite owned tables.
- Workbook reads are allowed only for migration parity and controlled backfill workflows.
- Production monthly closing must remain workbook-free.

---

## Environment Setup and Development Discipline

### CRITICAL: Environment management rules

1. **Development scaffolding** (construction tools, temporary only)
   - `.dev/env/` — Python virtual environment for helper scripts ONLY
   - `.dev/.scripts/python/` — Python helper scripts for diagnostics, analysis, DB inspection
   - `.dev/.scripts/bash/` — Bash helper scripts
   - `.dev/.scripts/cmd/` — Windows batch helper scripts
   - **DO NOT CREATE A NEW VIRTUAL ENV** - Reuse existing `.dev/env/`
   - **DO NOT USE `.dev/env` FOR MAIN APP** - This is scaffolding only

2. **Main application environment** (production runtime)
   - `env/` — Python virtual environment for wrapper package and tests (root level)
   - Used by: wrapper package, test scripts, CLI commands
   - This is the "finished building" environment

**Metaphor:** `.dev/` is scaffolding and cranes during construction. `env/` is the finished building's electrical and plumbing systems.

---

## Source Data Inspection Strategy

### Philosophy: Trust but Verify

The design process should be **data-driven** rather than assumption-driven. Before designing abstractions, inspect the actual data sources to understand:
1. What data actually exists (vs. what docs say should exist)
2. Data quality and consistency patterns
3. Edge cases and exceptions
4. Existing naming conventions and patterns

### Primary Data Sources

1. **HomeBudget SQLite Database** (`finances.db` outside workspace)
   - Location: Specified in `reference/hb-finances/config.json` or via environment variable
   - Tables: `Account`, `Transaction`, `Category`, etc.
   - Access pattern: See `reference/hb-finances/database.py` and `homebudget.py`

2. **Legacy Helper Workbook Configs** (migration parity and backfill only, via JSON configs in `gsheet/`)
   - Financial Statements: `gsheet/financial-statements.json`
   - HomeBudget Helper: `gsheet/homebudget-workbook.json`
   - Cash Expenses: `gsheet/cash-expenses.json`
   - Shared Expenses: `gsheet/shared-expenses.json`
   - IBKR IBA: `gsheet/ibkr-iba.json`
   - CPF: `gsheet/cpf.json`

3. **Reference Implementation Patterns**
   - `reference/hb-reconcile/` — Transaction reconciliation algorithm and Excel-based GL pattern
   - `reference/hb-finances/` — HomeBudget database access patterns

4. **Configuration Files**
   - `data/monthly-closing/accounts.json` — Account definitions (to be created)
   - `data/monthly-closing/inputs.json` — User inputs for monthly closing

### Helper Scripts Strategy

**Purpose**: Create lightweight Python scripts in `.dev/.scripts/python/` to inspect and analyze source data during the design phase. These scripts are temporary scaffolding and will be discarded after design is complete.

**Location**: `.dev/.scripts/python/`

**Environment**: Use `.dev/env/` virtual environment

**Typical helper scripts**:
1. `inspect_hb_schema.py` — Query HomeBudget DB schema, list tables/columns
2. `inspect_hb_accounts.py` — Export account list with types and currencies
3. `inspect_hb_transactions.py` — Sample transactions by account type
4. `inspect_gsheet_ranges.py` — Fetch Google Sheets data to verify structure
5. `validate_account_mapping.py` — Cross-check HB accounts vs. GSheet accounts
6. `analyze_reconcile_patterns.py` — Inspect hb-reconcile Excel workbook structure

**Script template pattern**:
```python
#!/usr/bin/env python3
"""Helper script to inspect [DATA SOURCE] - TEMPORARY SCAFFOLDING"""
import sys
from pathlib import Path

# Add reference code to path if needed
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'reference/hb-finances'))

def main():
    # Inspection logic here
    pass

if __name__ == '__main__':
    main()
```

### When to Use Autonomous Investigation vs. User Prompts

**Autonomous Investigation** (AI should proceed without user input):
1. **Schema inspection**: Database tables, columns, data types
2. **Data enumeration**: List of accounts, categories, transaction types
3. **Pattern recognition**: Common transaction structures, naming conventions
4. **Consistency checking**: Cross-reference data between sources
5. **Code pattern analysis**: How reference implementations work
6. **Documentation gaps**: Missing definitions that can be inferred from data

**User Prompts Required** (genuine ambiguity or business logic decisions):
1. **Business rules**: "Should forex gains be classified as income or capital gains?"
2. **Tolerance thresholds**: "What variance is acceptable for cash reconciliation?"
3. **Workflow preferences**: "Should bill payment run before or after account reconciliation?"
4. **Data conflicts**: "Account X appears in HB but not in GSheet - which is correct?"
5. **Design trade-offs**: "Use JSON config or SQLite for account mappings?"
6. **External dependencies**: "Where is the HomeBudget database file located?"

**Investigation Process**:
```
1. Read documentation → 2. Inspect source data → 3. Analyze patterns → 4. Infer rules → 5. Verify cross-source consistency → 6. Only prompt if genuine ambiguity remains
```

---

## Design assumptions

1. **Statements are the source of truth**: All account balances and transactions are ultimately reconciled to the statements. HomeBudget is a ledger that reflects the statement data and provides classifiation and re-organization of transactions, but the net transactions and balances must match the statements after reconciliation.
2. **Accounting precision**: Precision is based on currency rules (2 decimal places for SGD, 2 for USD) and all calculations must adhere to these rules to avoid rounding issues.
3. **reconciliation tolerance and algorithm**: There are four reconciliation workflows: cash, account statements, homebudget (expenses) and financial statements. For now cash, account statements and homebudget reconciliation is in scope.  The details for the homebudget reconciliation algorithm, design and tolerance can all be found in the reference docs and source code in `references/hb-reconcile`. the cash reconcile procedure can be found in `docs/develop/cash-reconcile-workflow.md`. The tolerance is exact match to precision limit 0.00 SGD for cash, account statements and homebudget expense reconciliation. 
4. **account reconciliation workflow**: The account statement reconciliation workflow starts with user MFA authenticate and login to bank, download PDF and CSV/Excel statements, then this is the start of the automated workflow, first to import transactions in CSV and Excel from bank website download and import them into the existing SQLite DB, then save the raw PDF to AWS S3.  After ingesting the txns to the SQLite DB, the ending balance should match the balance reflected from the bank online portal read by the user and saved to JSON. Prior to committing changes to DB, the transaction imports should be pre-verified to match the ending balance and in case the validation fails, should flag to the user.  
5. **cash reconciliation alert threshold**: for the cash reconciliation workflow, an adjustment expense is created to close the gap. The threshold for alerting user is +/- SGD $20 per month. If the adjustment exceeds this threshold, then the program should notify the user to review.
6. **bill payments**: bills are treated the same as any other expense, with double-entry transfer+expense booking in HomeBudget, where the transfer from the real wallet should have a corresponding record from the account statement for that payment method if it is in the statement period.  Each bill has it's own logic for expense breakdown and for shared costs, the cost splitting accounting.
7. **shared costs**: shared costs use app-managed allocation rules and persisted records. Legacy shared-expenses workbook data can be used for parity checks and controlled backfill only. There are two bills where costs are shared - SPServices ie PUB, and Singtel.  The charges for these bills are split between flatmates (3x) with single person share (1/3) booked as an expense, itemized by categories on the bill (water, electrity, gas, others, internet) and the balance (2/3) for flatmates treated as a transfer to a credit account "30 CC Hashemis".   
8. **pattern inspection**: for any design decision, first inspect the raw sources - google sheets, sqlite databases, HomeBudget database, to understand how the rules and existing patterns are implemented.
9. **accounting period**: accounting periods are standardized to calendar months, with beginning of month the first calendar day and end of month the last calendar day.  
10. **reconciliation date**: the reconciliation date can be at any day in the month, and for pending transactions that are before reconciliation date, treat them as occuring after the reconcilaion date, and add a note in the description field of the actual transaction date "13 Mar", "25 Jan", etc... later after two reconcilation periods have passed, the dates for these transactions can be updated to the actual transaction date.

## Phase 1: Discovery and Analysis

### Goal

Establish a shared understanding of the current system design, identify inconsistencies, and define clear requirements for the unified application.

### 1.1: Document Review and Analysis

**Status**: ✓ Complete

**Key Findings**:

#### A. Consistent Themes ✓

1. **Multi-source integration** with 5+ independent data systems
2. **Monthly closing workflow** as the central orchestration pattern
3. **Domain-driven design** with immutable value objects (Period, Money, CashBalance)
4. **Currency-aware architecture** (SGD primary, USD secondary)
5. **Hierarchical accounting** (asset class → accounts, categories -> subcategories)
6. **Manual review checkpoints** at each workflow step

### 1.2: Current Design Documentation Assessment

**Sources reviewed**:
- `docs/workflow.md` — High-level workflow (15 sequential steps)
- `docs/develop/financial-statements-spec.md` — Report structure and calculation rules
- `docs/account-classification.md` — Classification of account types and mapping logic
- `docs/accounting-logic.md` — Accounting rules, patterns and techniques used in the personal finance system
- `reference/hb-reconcile/docs/reconcile.md` — Transaction reconciliation algorithm for statements vs. HomeBudget ledger
- `docs/glossary.md` — Definitions of key terms (account, transaction, reconciliation, etc.)
- `docs/bill-payment.md` — Shared cost allocation subprocess
- `docs/develop/data-source-inventory.md` — Data source APIs and refresh cadences
- `docs/develop/cash-reconcile-*.md` — Domain model and algorithms (well-specified)

**Additional sources added**:
- `reference/hb-finances/` — Reference implementation for HomeBudget database access
- `reference/hb-reconcile/src/reconcile/reconcile.py` — Working reconciliation algorithm
- `gsheet/*.json` — Google Sheets configuration files
- HomeBudget SQLite database schema (via inspection)
- Google Sheets workbooks (via API inspection)

**Cash reconcile over-design**
The cash reconciliation workflow is currently over-designed with complex variance explanation and approval process, which may be unnecessary given the nature of cash transactions and the typical variance range. A simplified approach with 1-2 modules for core logic + shared utility and interface modules to handle the google sheets and homebudget interface should be sufficient. Custom classes are not needed to represent "Money" simple float is sufficient.

**Assessment by domain**:

| Domain | Confidence | Notes |
|---|---|---|
| **Data sources** | HIGH | All sources documented |
| **Cash reconciliation domain** | TOO HIGH | over-designed, needs refactoring |
| **Account types** | HIGH | definitions available in financial statements workbook and HomeBudget |
| **Workflow steps** | MEDIUM | Sequential but handoff rules unclear |
| **Currency handling** | MEDIUM | Rules documented but no code examples |
| **Reconciliation algorithm** | MED | Generic definition provided |
| **Module boundaries** | LOW | Unclear where forex-logic lives vs. in reconciliation |
| **Bill payment integration** | LOW | Separate design; integration points vague |
| **Error handling strategy** | LOW | No unified error/warning/validation framework |

---

## Phase 2: High-Level Architecture Design

### Goal

Define the overall application structure, module boundaries, data flow, and orchestration pattern.

### 2.1: Unified Glossary and Definitions

**Status**: TO DO (AI-driven)

**Action**: Update the glossary (`docs/glossary.md`) documenting any residual ambiguous terms with examples.

**AI Prompt**:

```
1. Review all documentation in docs/ and docs/develop/ to identify terms used but not defined in docs/glossary.md

2. Inspect source data to validate definitions:
   - Query HomeBudget database for actual account types, transaction types
   - Fetch Google Sheets data to verify account classifications
   - Analyze hb-reconcile workbook structure

3. Create helper script `.dev/.scripts/python/extract_terminology.py` to:
   - Scan all markdown files for domain-specific terms
   - Cross-reference with glossary.md
   - Output list of undefined terms

4. For each undefined term:
   - First attempt: Infer definition from context and data patterns
   - If inference is clear: Add to glossary with data-backed example
   - If ambiguous: Flag for user input

5. Update docs/glossary.md with:
   - All newly defined terms
   - Data-backed examples from actual HB database or GSheets
   - Cross-references to related docs

Reference: 
- docs/accounting-logic.md
- docs/account-classification.md
- docs/workflow.md
- HomeBudget database schema
- Google Sheets configurations

Expected output: Updated docs/glossary.md with all terms defined and validated against source data
```

**Expected Output**: Single updated file with all core terms defined, removing ambiguity across the app.

---

### 2.2: Application Architecture Diagram

**Status**: TO DO (Hybrid workflow)

General guidance

1. **Module Organization**: How should the application be divided into modules?
   - By workflow step (forex_module, wallet_module, reconcile_module, etc.)
   - By data source (homebudget_module, gsheet_module, statement_module, etc.)
   - By domain/business capability (accounting_module, financial_statements_module, etc.)

User input:

>The primary module organization should have heirarchical layering with low level modules at IO data sources, and then higher level modules at the domain logic layer, and then the workflow orchestration layer at the top. The domain logic layer can be organized by domain concepts such as accounting, financial statements, reconciliation, etc... and then within each domain module, there can be submodules for specific account types or reconciliation types. The data source modules should be organized by source (homebudget, gsheet, statements) and should provide a clear interface for the domain logic to interact with the data.

2. **Orchestration Pattern**: How should the monthly closing workflow be orchestrated?
   1. CLI commands that user runs sequentially (step 1, then step 2, ...)
   2. Single CLI command that runs all steps with checkpoints
   3. DAG/pipeline runner (airflow-like) with interdependency resolution
   4. Interactive web UI with step-by-step guidance

User input

>Two options: primary 1) CLI command for individual steps with checkpoints and inputs 4) Interactive web UI with step-by-step guidance. 

3. **Persistent State Model**: How should the app track workflow progress between steps?
   1. No persistence — each step is independent; user documents progress manually
   2. Session file (JSON) tracking completed steps, errors, decisions
   3. Database (SQLite) with step log and decision history
   4. Google Sheets integration (log progress back to sheets)

User input

>3) Database (SQLite) with step log and decision history. Keep the schema lean.

**AI Action** (based on answers):

```
1. Before designing, inspect actual implementation patterns:
   - Analyze reference/hb-finances/ for database access patterns
   - Analyze reference/hb-reconcile/ for reconciliation architecture
   - Review existing src/ directory structure (if any)

2. Create helper script `.dev/.scripts/python/analyze_reference_patterns.py` to:
   - Extract module structure from reference implementations
   - Identify reusable patterns vs. bespoke logic needed
   - Map reference functions to planned workflow steps

3. Design docs/develop/app-architecture.md with:

   a. Architectural diagram (ASCII or Mermaid)
   
   b. Module classification (3-tier layered architecture):
      **Layer 1: Data Source Adapters** (lowest level)
      - homebudget_adapter (SQLite access, query/insert/update)
      - legacy_workbook_adapter (Google Sheets API via sqlite_gsheet wrapper, parity/backfill mode only)
      - statement_parser (CSV/PDF/Excel parsers by bank)
      - forex_adapter (Yahoo Finance API)
      
      **Layer 2: Domain Logic** (business rules)
      - accounting (transaction booking, double-entry logic, currency handling)
      - reconciliation (gap detection, matching algorithms, tolerance checking)
      - financial_statements (balance sheet, income statement, cash flow)
      - bill_payment (shared cost allocation, statement parsing)
      
      **Layer 3: Orchestration** (workflow execution)
      - workflow_runner (step sequencing, checkpoint validation, state persistence)
      - cli (user interface for step execution)
      
      **Shared/Cross-cutting**:
      - types (Period, Money, Account, Transaction value objects)
      - exceptions (custom error hierarchy)
      - logging (structured logging to SQLite)
      - config (YAML/JSON loaders, schema validation)
   
   c. Data flow diagram:
      ```
      Period Input → Data Adapters (parallel fetch) → Domain Logic (transform, validate) → 
      Orchestration (sequence steps) → Financial Statements Output
      ```
   
   d. Module dependency graph (which calls which, directional)
   
   e. Extension points:
      - New statement parser: Implement StatementParser interface
      - New account type: Add handler in accounting module
      - New workflow step: Register in workflow_runner

4. Include actual code patterns from reference implementations as examples

5. Cross-reference with user inputs on CLI + web UI dual interface

Reference: 
- Design decisions from Phase 2.1 and user inputs
- reference/hb-finances/database.py (DB access pattern)
- reference/hb-reconcile/src/reconcile/reconcile.py (reconciliation pattern)

Expected output: docs/develop/app-architecture.md (~5-7 pages with diagrams and code examples)
```

### 2.3: Data Flow and Transformation Boundaries

**Status**: TO DO (AI-driven discovery)

**AI Prompt**:

```
1. **Before designing data flow, trace actual data movement:**

   a. Create `.dev/.scripts/python/trace_data_sources.py` to:
      - Enumerate all data sources (HB DB, GSheets, local files)
      - For each source, list what data is read vs. written
      - Identify data freshness requirements (real-time, daily, monthly)
   
   b. Analyze reference/hb-finances/ data access patterns:
      - How does it read from HomeBudget DB?
      - How does it write back transactions?
      - What validation occurs at read/write boundaries?
   
   c. Analyze reference/hb-reconcile/ transformation pipeline:
      - What inputs does it require? (balances, hb_gl, stm_gl)
      - What transformations occur? (matching, gap analysis, edits generation)
      - What outputs does it produce? (edits table, reconciliation report)

2. **Map end-to-end data flow for monthly closing workflow:**

**Sources reviewed**:
- `docs/workflow.md` — High-level workflow (15 sequential steps)
- `docs/develop/financial-statements-spec.md` — Report structure and calculation rules
- `docs/account-classification.md` — Classification of account types and mapping logic
- `docs/accounting-logic.md` — Accounting rules, patterns and techniques used in the personal finance system
- `reference/hb-reconcile/docs/reconcile.md` — Transaction reconciliation algorithm
- `docs/glossary.md` — Definitions of key terms
- `docs/bill-payment.md` — Shared cost allocation subprocess
- `docs/develop/data-source-inventory.md` — Data source APIs and refresh cadences
- `docs/develop/cash-reconcile-*.md` — Domain model and algorithms
- Helper script outputs from trace_data_sources.py

**Design docs/develop/data-flow.md covering:**

1. **Input sources** (with actual access patterns from inspection):
   - HomeBudget SQLite: query_balance(), query_transactions(), add_transaction()
   - App-owned canonical data: balances, forex_rates, account mappings, and shared-cost rules in SQLite and local config
   - Google Sheets helper workbooks: legacy parity and backfill only
   - Bank statements: CSV/PDF downloads (manual step, then automated parsing)
   - Yahoo Finance API: exchange rates (automated fetch)
   - User inputs: inputs.json (manual cash counts, balance confirmations)

2. **Transformation pipeline** (with validation gates):
   
   Stage 1 - Data Acquisition (parallel):
   - Fetch forex rates → validate currency pairs exist
   - Query HB balances → validate accounts exist
   - Parse bank statements → validate schema matches
   - Read user inputs → validate required fields present
   
   Stage 2 - Normalization (sequential):
   - Convert all amounts to Decimal(2 places)
   - Convert all dates to standard format
   - Map account names across systems (HB ↔ Canonical Registry ↔ Statement)
   - Apply currency conversions using fetched forex rates
   
   Stage 3 - Calculation (sequential):
   - Calculate opening balances (from prior period)
   - Sum transactions per account
   - Compute expected closing balances
   - Calculate forex M2M adjustments
   - Calculate shared cost allocations
   
   Stage 4 - Reconciliation (iterative):
   - Compare computed vs. actual balances
   - Detect variances exceeding tolerance
   - Match transactions (ledger vs. statement)
   - Generate reconciliation edits
   - User review and approval
   
   Stage 5 - Finalization (sequential):
   - Post reconciliation transactions to HomeBudget
   - Generate financial statements snapshot
   - Create period summary reports
   - Archive to SQLite and S3

3. **Output targets**:
   - HomeBudget DB: Reconciliation transactions (INSERT)
   - financial_statements.db: Period snapshot (INSERT/UPDATE)
   - data/monthly-closing/{YYYY-MM}/financial-statements.json: Full snapshot (WRITE)
   - data/monthly-closing/{YYYY-MM}/reconciliation-decisions.json: Novel decisions (APPEND)
   - S3: DB backup + PDF reports (UPLOAD)
   - Optional publication target: Google Sheets summary export for user review, not part of core state model

4. **Error handling at transformation boundaries**:
   - Data fetch errors: Fatal, cannot proceed (retry with backoff)
   - Schema validation errors: Fatal, data quality issue (user must fix source)
   - Calculation errors: Fatal, logic issue (report to user with context)
   - Reconciliation variances: Recoverable, user intervention (workflow checkpoint)
   - Posting errors: Recoverable, retry or rollback (transactional)

5. **Data dependencies diagram**:
   ```
   Period Input
       ↓
   [Data Acquisition Layer - Parallel]
       ├─→ HomeBudget DB (balances, transactions)
      ├─→ Canonical App Data (accounts, forex, shared costs)
       ├─→ Bank Statements (CSV/PDF parsing)
       ├─→ Yahoo Finance (forex rates)
       └─→ User Inputs (cash counts, confirmations)
       ↓
   [Normalization Layer]
       → Validate schemas → Map cross-system IDs → Convert currencies
       ↓
   [Calculation Layer]
       → Balances → Forex M2M → Allocations → Expected values
       ↓
   [Reconciliation Layer]
       → Variance detection → Transaction matching → Edit generation → User review
       ↓
   [Finalization Layer]
      → Post to HB → Save to SQLite → Archive to S3 → Optional report publication
       ↓
   Financial Statements Output
   ```

6. **Manual checkpoints** (where workflow pauses for user):
   - After data acquisition: Verify all sources loaded
   - After reconciliation: Review and approve variances
   - After finalization: Confirm reports look correct

Format: Mermaid diagrams + narrative descriptions
Reference: 
- docs/develop/cash-reconcile-workflow.md for detailed algorithm example
- reference/hb-reconcile/ for working transformation pipeline

Expected output: docs/develop/data-flow.md (~5-7 pages with flow diagrams)
```

---

## Phase 3: Domain Model Design

### Goal

Establish a consistent, comprehensive domain model that applies across all modules.

### 3.1: Value Objects and Entities

**Status**: TO DO (Design spec + implementation guidance)

**Reference**: `docs/develop/cash-reconcile-domain-model.md` defines good patterns; generalize to all domains.

**AI Prompt**:

```
1. **Before designing, inspect actual data structures:**
   
   a. Create helper script `.dev/.scripts/python/inspect_hb_schema.py` to:
      - Connect to HomeBudget database
      - Extract table schema (Account, Transaction, Category, etc.)
      - Sample data from each table (first 10-20 rows)
      - Identify unique constraints and relationships
   
   b. Create helper script `.dev/.scripts/python/inspect_account_types.py` to:
      - Query all accounts from HomeBudget
      - Group by account type (Budget, Cash, Credit, External)
      - Show examples of each type with actual names
      - Cross-check with Google Sheets account list
   
   c. Create helper script `.dev/.scripts/python/sample_transactions.py` to:
      - Sample transactions by type (expense, income, transfer)
      - Show double-entry patterns for cost center transactions
      - Identify forex transaction patterns
      - Extract M2M adjustment patterns for investments

2. **Design docs/develop/domain-model.md as a data-validated specification:**

   1. Core Value Objects (immutable, validated against actual data):
      - Period (year: int, month: int) 
        * Validation: 1 <= month <= 12, year >= 2000
        * Example from data: Period(2026, 2) for February 2026
      
      - Money (amount: Decimal, currency: str)
        * Currencies found in HB: SGD, USD, EUR (from inspection)
        * Precision: 2 decimal places (from accounting-logic.md)
        * Example: Money(152.75, 'SGD')
      
      - Account (account_id: str, name: str, type: AccountType, currency: str)
        * Types from HB inspection: Budget, Cash, Credit, External
        * Example: Account('TWH DBS Multi SGD', 'TWH DBS Multi SGD', AccountType.CASH, 'SGD')
      
      - Transaction (date: Date, account: str, amount: Money, type: TxnType, ...)
        * Types from inspection: expense, income, transfer_in, transfer_out
        * Double-entry pattern: Transfer + Expense for cost center
        * Example: See actual HB transactions from sample_transactions.py
      
      - ExchangeRate (date: Date, currency_pair: str, rate: Decimal, source: str)
        * Pairs from GSheet forex_rates: USD/SGD, EUR/SGD
        * Source: Yahoo Finance or manual entry
        * Example from actual data: ExchangeRate(2026-02-28, 'USD/SGD', 1.3245, 'Yahoo')
      
      - Variance (amount: Decimal, tolerance: Decimal, status: VarianceStatus)
        * Status: unexplained | explained | waived
        * Tolerance from user input: 0.00 for account reconciliation, 20.00 SGD for cash
   
   2. Account Types and Specific Handling (from account-classification.md + data inspection):
      
      For each account type found in HomeBudget database:
      - **Budget (Cost Center)**: TWH - Personal
        * Input rules: Only receives transfers from real wallets + expense bookings
        * Balance calculation: Should close to zero each month
        * Reconciliation: Balance should be zero after month-end
        * No forex (always SGD)
      
      - **Cash (Bank Accounts, Wallets)**: Examples from data: TWH DBS Multi SGD, TWH Cash SGD, TWH IB USD
        * Input rules: Can be payment method, can earn interest
        * Balance: Non-negative at month-end
        * Reconciliation: Transaction-level matching with statements
        * Forex: M2M on foreign currency accounts
      
      - **Credit**: Examples: TWH UOB One SGD, 30 CC Hashemis
        * Input rules: Similar to cash but negative balances
        * Balance: Typically negative (liability)
        * Reconciliation: Transaction-level with statements
        * Forex: M2M on foreign currency cards
      
      - **External (Investments)**: Examples: IB POSITION USD, IB POSITION EUR
        * Input rules: Net P&L only, no separate expense/income
        * Balance: Unit price * quantity or lump sum valuation
        * Reconciliation: M2M adjustment to match statement
        * Forex: M2M based on currency balance changes
   
   3. Transaction Domain (from actual HB data patterns):
      - Transaction types: expense, income, transfer_out, transfer_in, balance (ignore balance type)
      - Double-entry examples from cost center:
        ```
        Txn 1: Transfer from TWH DBS Multi SGD -> TWH - Personal, -50.00 SGD
        Txn 2: Expense in TWH - Personal, category: Food & Dining:Groceries, -50.00 SGD, payee: NTUC
        ```
      - Deduplication key: (account, date, amount, description) - from accounting-logic.md
      - Category mapping: From HB Category table (inspect to list hierarchy)
   
   4. Financial Statement Domain (from financial-statements.json GSheet config):
      - Line items from actual GSheet accounts range
      - Hierarchy: Asset Type -> Account -> Balance
      - Asset types from inspection: cash and bank accounts, credit, savings account, liquid investments, illiquid and retirement
      - Period snapshot: Immutable once finalized
      - Comparison: Current vs prior period (month-over-month)
   
   5. Reconciliation Domain (generalized from hb-reconcile + accounting-logic.md):
      - Opening balance (from prior month balances sheet)
      - + Transactions (from ledger and statement)
      - = Computed closing balance
      - vs. Actual closing balance (from statement)
      - = Variance (if |variance| > tolerance)
      - Variance resolution: Edit ledger to match OR approve as unexplained
      - Algorithm from hb-reconcile/reconcile.py: Match transactions, then explain gaps

3. **Format**: 
   - Conceptual diagrams using Mermaid or ASCII
   - Pseudo-code with actual data examples
   - Cross-references to source data ("see sample_transactions.py output")
   - Do NOT implement code; focus on design clarity backed by real data

4. **Validation**:
   - Every value object should have example from actual HomeBudget or GSheet data
   - Every business rule should reference either doc or data pattern
   - Flag any assumptions that need user confirmation

Reference: 
- domain-driven-design patterns
- reference/hb-reconcile/docs/reconcile.md
- docs/accounting-logic.md
- docs/account-classification.md
- HomeBudget database inspection results
- Google Sheets data inspection results

Expected output: docs/develop/domain-model.md (~8-10 pages with data-backed examples)
```

---

## Phase 4: Data Layer Design

### Goal

Design the persistent storage layer, focusing on:
1. What data the app owns (vs. leaving in external systems)
2. Database schema for data the app owns
3. Synchronization strategy with external systems

### 4.1: Data Ownership Model

**Status**: TO DO (Design decision)

General guidance

1. **Financial Statements Storage**: Where should financial statements snapshots be stored?
   1. Google Sheets (current approach) — keep using gsheet/financial-statements.json
   2. Local JSON files (per-period) — data/monthly-closing/{YYYY-MM}/financial-statements.json
   3. SQLite database — dedicated financial_statements.db with tables per entity
   4. Hybrid: JSON for snapshots + SQLite for historical analysis

User input

>3) SQLite database — dedicated financial_statements.db with tables per entity with db backup to S3, PDF reports upload to S3, and post reports to Google Sheets of total ledger + summary reports for user review and data exploration.

2. **Reconciliation Record Storage**: How should reconciliation decisions (gap explanations, approvals) be stored?
   1. In HomeBudget as transaction notes (leave there)
   2. In local JSON file per period (data/monthly-closing/{YYYY-MM}/reconciliation.json)
   3. In SQLite reconciliation_decisions table
   4. In Google Sheets (current approach)

User input

>2) for gap explanations and decisions use a local JSON file for purpose of refining the algorithm and process. For routine reconciliation patterns well learned and captured in source code or in docs, skills, there is no need to capture these, focus on novel or edge cases that require manual review and decision that are still interrupting the workflow with human intervention needed. 

3. **Exchange Rate Archive**: Should the app maintain its own archive of exchange rates?
   1. No — always fetch from Yahoo Finance on demand
   2. Yes — SQLite table (date, pair, rate, source) for audit trail
   3. Yes — JSON file per period (data/monthly-closing/{YYYY-MM}/forex-rates.json)
   4. Yes — cached locally but read-only (user maintains via config)

User input

>2) Yes — SQLite table (date, pair, rate, source) for past 2 years history on monthly basis for all currencies used during that period.

### 4.2: Database Schema Design

**Status**: TO DO (AI-driven after user inputs)

**AI Prompt** (conditional on user inputs):

```
1. **Before designing schema, inspect actual data storage patterns:**

   a. Create `.dev/.scripts/python/inspect_gsheet_structure.py` to:
      - Fetch all sheets from financial-statements workbook
      - Document range structure (balances, accounts, forex_rates, etc.)
      - Show sample data from each range
      - Identify how historical data is stored (append vs. overwrite)
   
   b. Create `.dev/.scripts/python/inspect_hb_reconcile_data.py` to:
      - Analyze reference/hb-reconcile/data/reconcile.xlsx structure
      - Document balances, hb_gl, stm_gl sheet formats
      - Show how reconciliation decisions are currently stored
      - Extract patterns for edits tracking
   
   c. Create `.dev/.scripts/python/analyze_data_files.py` to:
      - Scan data/monthly-closing/ for existing JSON files
      - Document structure of inputs.json, reconciliation files
      - Identify what data is already being persisted locally

2. **Design docs/develop/database-schema.md defining app's persistent storage:**

   **Schema Overview**:
   - **App-owned data**: Financial statements snapshots, reconciliation decisions, workflow state
   - **External data (read-only)**: HomeBudget transaction ledger, legacy helper workbook data for parity/backfill only
   - **Cached data**: Exchange rates archive, account metadata
   
   **Storage design (based on user input: SQLite + S3 backup)**:
   
   a. **financial_statements.db** (SQLite):
      
      Tables:
      ```sql
      CREATE TABLE periods (
          period_id TEXT PRIMARY KEY,  -- 'YYYY-MM'
          year INTEGER NOT NULL,
          month INTEGER NOT NULL,
          status TEXT CHECK(status IN ('open', 'in_progress', 'closed')),
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          finalized_at TIMESTAMP
      );
      
      CREATE TABLE account_balances (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          period_id TEXT NOT NULL,
          account TEXT NOT NULL,
          opening_balance REAL NOT NULL,
          closing_balance REAL NOT NULL,
          currency TEXT NOT NULL,
          FOREIGN KEY (period_id) REFERENCES periods(period_id),
          UNIQUE(period_id, account)
      );
      
      CREATE TABLE exchange_rates (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          date DATE NOT NULL,
          currency_pair TEXT NOT NULL,  -- 'USD/SGD'
          rate REAL NOT NULL,
          source TEXT NOT NULL,  -- 'Yahoo Finance', 'Manual'
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          UNIQUE(date, currency_pair)
      );
      
      CREATE TABLE workflow_log (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          period_id TEXT NOT NULL,
          step_name TEXT NOT NULL,
          status TEXT CHECK(status IN ('pending', 'in_progress', 'completed', 'failed')),
          started_at TIMESTAMP,
          completed_at TIMESTAMP,
          error_message TEXT,
          FOREIGN KEY (period_id) REFERENCES periods(period_id)
      );
      
      CREATE TABLE reconciliation_variances (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          period_id TEXT NOT NULL,
          account TEXT NOT NULL,
          variance_amount REAL NOT NULL,
          status TEXT CHECK(status IN ('unexplained', 'explained', 'waived')),
          explanation TEXT,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          resolved_at TIMESTAMP,
          FOREIGN KEY (period_id) REFERENCES periods(period_id)
      );
      ```
   
   b. **reconciliation_decisions.json** (per-period, in data/monthly-closing/{YYYY-MM}/):
      ```json
      {
        "period": "2026-02",
        "account": "TWH DBS Multi SGD",
        "variance": -5.23,
        "explanation": "Bank fee not captured in statement CSV",
        "resolution": "Added manual transaction to HB",
        "decision_type": "novel",  // vs "routine"
        "resolved_at": "2026-03-01T15:23:00"
      }
      ```
      Only store "novel" decisions requiring manual intervention, not routine patterns.
   
   c. **Exchange rates archive** (SQLite, as per user input):
      - Past 2 years of monthly exchange rates
      - All currency pairs used in that period
      - Populated from Yahoo Finance or manual entry
   
   d. **Account metadata** (data/monthly-closing/accounts.json):
      Schema to be defined based on inspection of:
      - HomeBudget Account table
      - Google Sheets accounts range
      - docs/account-classification.md rules
      
      Proposed structure:
      ```json
      {
        "accounts": [
          {
            "id": "TWH DBS MULTI SGD",
            "hb_name": "TWH DBS Multi SGD",
            "gsheet_name": "TWH DBS MULTI SGD",
            "statement_name": "TWH DBS Multi SGD",
            "type": "bank account",
            "hb_type": "Cash",
            "asset_category": "cash and bank accounts",
            "currency": "SGD",
            "owner": "TWH",
            "reconciliation_method": "transaction_level",
            "can_be_payment_method": true,
            "can_earn_interest": true
          }
        ]
      }
      ```

3. **Data Integrity**:
   - Foreign keys enforced in SQLite
   - Validation: amounts are Decimal with 2 places, dates are valid
   - Immutability: Once period status = 'closed', no updates allowed
   - Audit trail: All edits logged with timestamp and reason

4. **Synchronization**:
   - HomeBudget: One-way write (app adds reconciliation transactions)
   - Google Sheets: Optional report publishing and parity/backfill reads only, not required for production monthly close
   - Update cadence: Per workflow step (not real-time)
   - Conflict resolution: HB changes during period close → flag as error, user must re-run

5. **Backup Strategy** (based on user input: S3):
   - financial_statements.db → S3 after each period finalization
   - PDF reports → S3 in organized structure (year/month/)
   - Optional summary report published for user review

6. **Helper scripts to validate design**:
   - `.dev/.scripts/python/create_test_db.py` - Create sample DB with test data
   - `.dev/.scripts/python/validate_schema.py` - Test all constraints and relationships

Reference:
- User inputs on storage decisions
- Inspection results from helper scripts
- reference/hb-reconcile/data/reconcile.xlsx structure
- gsheet/financial-statements.json configuration

Expected output: docs/develop/database-schema.md (~6-8 pages with SQL DDL and JSON schemas)
```

---

## Phase 5: Workflow and Orchestration Design

### Goal

Define the complete monthly closing workflow, including:
1. Sequential steps that must happen in order
2. Parallel steps that can run concurrently
3. Checkpoints and validation gates
4. Error recovery and rollback strategies

### 5.1: Workflow Architecture

**Status**: TO DO (Design spec, extending docs/workflow.md)

**AI Prompt**:

```
1. **Before designing workflow, inspect actual process artifacts:**

   a. Analyze existing monthly closing artifacts in data/monthly-closing/:
      - Review inputs.json structure (what user inputs are captured)
      - Review reconciliation JSON files (what decisions are recorded)
      - Identify manual vs automated steps from artifacts
   
   b. Review docs/workflow.md for current 15-step process:
      - Map each step to data sources and outputs
      - Identify dependencies between steps
      - Estimate time per step (manual vs automated)
   
   c. Inspect reference/hb-reconcile workflow pattern:
      - How does it handle step progression?
      - What validation occurs between steps?
      - How are errors handled and recovered?

2. **Design docs/develop/workflow-architecture.md as a detailed workflow specification:**

1. Workflow Overview:
   - Start condition: User initiates closing for period {YYYY-MM}
   - End condition: Financial statements snapshot created + user approves
   - Total estimated time: (from workflow.md)
   - Failure modes: What can go wrong? Rollback strategy?

2. Workflow Steps (from docs/workflow.md, with enhancements):
   
   Group A – Data Acquisition (parallel):
     Step A1: Fetch forex rates
     Step A2: Query wallet/checking balances from HomeBudget
     Step A3: Download bank statements and current account balances (manual)
     Step A4: Query IBKR position statement (manual)
     Step A5: Read CPF balance (manual, semi-annual)
     Checkpoint A: All data sources validated and available
   
   Group B – Data Entry and Transformation (human-intensive):
     Step B1: App parses bank statements; prepares ingestion into SQLite DB and verifies with current balances
       Step B2: App parses IBKR statement data and persists normalized IBKR metrics
       Step B3: App captures CPF balances and contribution metrics through app-native input and validation
     Step B4: User reviews and approves data entries; resolves any parsing or ingestion flags
     Checkpoint B: All account data current and validated with the statements SQLite DB digital twin
   
   Group C – Calculation and Reconciliation:
     Step C2: Post forex adjustment transactions to HomeBudget
     Step C3: Calculate expected balance for each account (from opening + transactions)
     Step C4: Compare to statement balance; detect variances
     Step C5 (iterative): Apply reconciliation algorithm to close gaps (match transactions, explain variances, or flag for review)
     Step C6: User reviews and approves reconciliation decisions, or manually intervenes to close gaps
     Checkpoint C: All variances closed or documented, HomeBudget ledger updated 
   
   Group D – Financial Statements Generation:
     Step D1: Aggregate all account balances into trial balance
     Step D2: Apply consolidation rules (forex rate conversions, eliminations)
     Step D3: Calculate M2M forex on foreign currency accounts (IBKR) using fetched rates
     Step D4: Generate complete annual ledger of accounts and transactions for current year
     Step D5: Generate Income Statement (from transactions)
     Step D6: Generate Balance Sheet (from balances)
     Step D7: User review and approval
     Checkpoint D: Statements match expectations; user approves
   
   Group E – Closure and Archival:
     Step E1: Commit transactions and updates to local SQLite DB and JSON file
     Step E2: Save financial statements snapshot (JSON + PDF)
     Step E3: Upload to S3 (if configured)
     Step E4: Archive session log
     Checkpoint E: All deliverables completed and stored

3. Checkpoint Rules:
   For each checkpoint, define:
   - Validation criteria (what must be true to pass)
   - On failure: Which steps must be repeated?
   - User override (can user force past checkpoint despite warning?)
   
4. Parallel vs. Sequential:
   - Which steps in Groups A-D can run in parallel?
   - Which require prior steps to complete?
   - Where are the critical path bottlenecks?

5. Session State:
   - What state is maintained between steps?
   - How to resume if user pauses/resumes later?
   - Idempotency: Can step N be re-run without affecting N+1?

6. Error Handling:
   - Data validation errors (malformed statement, missing account)
   - Business logic errors (variance exceeds tolerance, forex rate not available)
   - External API errors (Homepage unavailable, Yahoo Finance rate fetch fails)
   - User errors (wrong file uploaded, balance entry typo)
   
   For each error type: What's the recovery path?

Reference: docs/workflow.md (existing), docs/develop/cash-reconcile-workflow.md
Expected output: docs/develop/workflow-architecture.md (~8-10 pages, with diagrams)
```

### 5.2: Bill Payment and Shared Costs Subprocess

**Status**: INCOMPLETE in current docs

**Reference**: `docs/bill-payment.md` and `docs/develop/bill-payment-shared-costs-automation-design.md` (partial)

**AI Prompt**:

```
Complete the design of the bill payment subprocess (currently 72 minutes, >50% automatable):

Design docs/develop/bill-payment-workflow.md covering:

1. Current Subprocess Steps (from bill-payment.md):
   B1: Download statements (10 min) — manual
   B2: Parse statements (12 min) — automatable
   B3: Form update in Sheets (8 min) — automatable
   B4: Fetch shared costs (5 min) — automatable
   B5: Add to HomeBudget (12 min) — automatable
   B6: Update consumption DB (8 min) — automatable
   B7: Verification (7 min) — manual
   TOTAL: 72 min (design target: 36 min, 50% reduction)

2. Detailed Design for Each Step:
   - Input: What data is needed?
   - Process: Algorithm or user action?
   - Output: What's produced?
   - Error cases: What can go wrong?
   - Automatable? How would it work?

3. Statement Parser Architecture:
   - Support multiple bank formats (DBS, UOB, Citi, BOA)
   - Extensible pattern for adding new formats
   - Validation rules per bank (date format, amount range, etc.)

4. Shared Cost Allocation Logic:
   - Current: 1/3 + 2/3 split (user + 2 flatmates)
   - Generalize: Configurable percentages, variable number of parties
   - Integration with HomeBudget (post allocation entries to settlement account)

5. Consumption Tracking:
   - Current: Utility usage (kWh, m³, GB) mentioned; no schema
   - Design: SQLite table or JSON file to track consumption metrics
   - Reconciliation: Link consumption to bill amount

6. Integration with Main Workflow:
   - When does bill payment subprocess run relative to main closing?
   - How do allocated transactions affect reconciliation gaps?
   - Data refresh cadence (monthly, as-needed, real-time)?

Reference: docs/bill-payment.md, docs/accounting-logic.md (shared cost rules)
Expected output: docs/develop/bill-payment-workflow.md (~6-8 pages)
```

---

## Phase 6: Module Interface Design

### Goal

Define module boundaries, interfaces, and responsibilities.

### 6.1: Core Module Catalog

**Status**: TO DO (Design spec + interfaces)

**AI Prompt**:

```
Create docs/develop/module-design.md defining the app's modular structure:

1. Module Taxonomy:
   Classify all modules into 3 layers:
   
   Layer 1 — Domain/Logic Modules (independent of data sources):
   
   Layer 2 — Adapter Modules (bridge to external systems):
   
   Layer 3 — Orchestration/Support:
     - cli_module (user interface: commands, prompts)
     - workflow_runner (orchestrate steps, manage checkpoints)
     - session_manager (track progress, resume capability)
     - error_handler (unified error/warning/validation framework)
     - config_manager (load and validate configuration)
     - logging_reporter (structured session logging)

2. For Each Module, Define:
   - **Purpose**: What domain problem does it solve?
   - **Inputs**: Data types and interfaces
   - **Outputs**: Data types and side effects
   - **Key Interfaces**:
     ```
     class ModuleName:
       def primary_method(input_type) -> output_type:
           '''Docstring with example'''
       def cleanup(): # if needed
           '''On workflow completion or error'''
     ```
   - **Error Handling**: Expected exceptions; recovery paths
   - **Dependencies**: Other modules it calls
   - **Testing Strategy**: Unit vs. integration; test fixtures needed
   - **Extension Points**: Where new variations plug in (e.g., new bank format parser)

3. Module Interactions:
   - Dependency graph (Module A calls Module B calls Module C)
   - Data contract between modules (interface stability)
   - Error propagation (exceptions, logging, recovery)

4. Extensibility Pattern (for 3 areas with frequent change):
   - Bank statement parsers (new format = new parser class)
   - Account type handlers (new account type = new class following interface)
   - Financial statement line items (new category = configuration, not code)

Reference: Phase 5 (workflow steps map to module responsibilities)
Expected output: docs/develop/module-design.md (~10-12 pages, with pseudocode)
```

---

## Phase 7: Error Handling and Validation Design

### Goal

Define a unified error handling and validation strategy across all modules.

### 7.1: Error and Validation Framework

**Status**: TO DO (Design spec)

**AI Prompt**:

```
Design docs/develop/error-handling-validation.md defining unified error strategy:

1. Error Taxonomy:
   - DataQuality errors (malformed input, missing required field, type mismatch)
   - DataFreshness errors (data > N days old, from disabled source)
   - ImportConflict errors (potential duplicate, conflicting edits)
   - ReconciliationError (variance exceeds tolerance, no explanation)
   - PostingError (transaction failed to save, balance mismatch)
   - ExternalAPI errors (Yahoo Finance timeout, Google Sheets auth failure)
   - ConfigError (required setting missing, invalid value)
   - LogicError (algorithm invariant violated, e.g., debit ≠ credit)

2. For Each Error Type:
   - Severity: Fatal (stop workflow) vs. Recoverable (warn, skip, retry)
   - User-facing message: Plain language explanation
   - Recovery path: What can user do? What can app retry?
   - Logging: What details to capture for audit?

3. Validation Rules by Domain:
   - Amount validation (Decimal precision, range checks per account type)
   - Date validation (must be within period, not in future, etc.)
   - Account validation (exists in HomeBudget, correct type)
   - Category validation (permitted for account type; consistent with mappings)
   - Period validation (closed month only; no concurrent closes)
   - Currency validation (supported pair; rate available)

4. Error Handling Patterns:
   - Built-in vs. user-correctable: Which errors stop the workflow? Which are warnings?
   - Batch validation: Collect all errors before failing (better UX)
   - Partial success: Some transactions post but others fail; how to recover?
   - Idempotency: Can errant step be re-run after fix?

5. Audit Trail:
   - Log all errors (fatal and recoverable) with context
   - Capture user decisions (approve variance, force past checkpoint)
   - Enable later analysis (e.g., "how many variances per period?" trends)

Reference: docs/develop/validation-error-handling-spec.md (existing, to be extended)
Expected output: docs/develop/error-handling-validation.md (~6-8 pages)
```

---

## Document Ordering and Dependencies

Once complete, design documents should be read in this order:

1. `docs/glossary.md` — Define all terms (foundation)
2. `docs/develop/app-architecture.md` — Understand module structure
3. `docs/develop/domain-model.md` — Learn core entities and rules
4. `docs/develop/data-flow.md` — Trace data transformations
5. `docs/develop/database-schema.md` — See what data app owns
6. `docs/develop/workflow-architecture.md` — Understand main workflow
7. `docs/develop/bill-payment-workflow.md` — Understand subprocess
8. `docs/develop/module-design.md` — Learn module interfaces and responsibilities
9. `docs/develop/error-handling-validation.md` — Understand error strategy
10. `.github/prompts/plan-closing-tdd-implementation.prompt.md` — Then ready for implementation planning

---

## Phase 8: Cleanup

### Goal

Remove all temporary scaffolding helper scripts and artifacts created during the design phase. These were valuable for discovery and validation but should not persist into implementation.

### 8.1: Cleanup Checklist

**Status**: TO DO (Execute after all design documents are finalized)

**Actions**:

1. **Review and Archive Helper Scripts**:
   - Document what each helper script revealed in a summary file
   - Create `.dev/.artifacts/design-phase-insights.md` with key findings
   - Example findings to capture:
     * "HomeBudget has 45 active accounts across 3 currency types"
     * "Transaction deduplication key validated: (account, date, amount, description)"
     * "Google Sheets forex_rates uses YYYY-MM-DD format for dates"

2. **Delete Temporary Scripts**:
   ```bash
   # Remove all Python helper scripts created for inspection
   rm -rf .dev/.scripts/python/inspect_*.py
   rm -rf .dev/.scripts/python/analyze_*.py
   rm -rf .dev/.scripts/python/sample_*.py
   rm -rf .dev/.scripts/python/validate_*.py
   rm -rf .dev/.scripts/python/extract_*.py
   rm -rf .dev/.scripts/python/create_test_*.py
   ```

3. **Clean Up Temporary Data Files**:
   - Remove any temporary CSV/Excel exports from inspection
   - Remove test database files created for validation
   - Keep only final JSON configurations and documented schemas

4. **Verify .gitignore Coverage**:
   - Ensure `.dev/.artifacts/` is in .gitignore (temporary outputs)
   - Ensure `.dev/.scripts/python/__pycache__/` is ignored
   - Commit only the final design insights summary

5. **Create Design Phase Summary**:
   - `.dev/.artifacts/design-phase-summary.md`:
     ```markdown
     ## Design Phase Summary
     
     **Duration**: [Start Date] to [End Date]
     
     **Key Discoveries**:
     1. HomeBudget Database Structure
        - Tables: Account, Transaction, Category, ...
        - Key insights: [from inspection]
     
     2. Google Sheets Data Organization
        - Workbooks: financial-statements, homebudget-workbook, ...
        - Key patterns: [from inspection]
     
     3. Reference Implementation Patterns
        - hb-reconcile: Excel-based GL pattern with balances/hb_gl/stm_gl
        - hb-finances: SQLAlchemy-based DB access
     
     4. Data Quality and Consistency
        - Cross-source validation results
        - Identified gaps or inconsistencies
     
     **Design Decisions Made**:
     - Architecture: 3-tier layered (Adapters → Domain → Orchestration)
     - Storage: SQLite for app data, S3 for backups
     - Workflow: CLI primary, web UI future
     - Reconciliation: Transaction-level matching with tolerance
     
     **Open Questions for Implementation**:
     - [Any remaining ambiguities flagged for user]
     ```

6. **Validate Design Document Completeness**:
   - Check that all 9 design documents are created
   - Verify cross-references between documents are valid
   - Ensure all code examples and schemas are consistent

7. **Prepare for Implementation Phase**:
   - Tag design phase completion in git: `git tag design-phase-complete`
   - Create implementation backlog from design documents
   - Transition to `.github/prompts/plan-closing-tdd-implementation.prompt.md`

**AI Prompt for Cleanup**:

```
Execute cleanup of design phase artifacts:

1. Scan `.dev/.scripts/python/` for all helper scripts created during design
2. For each script, extract key insights into `.dev/.artifacts/design-phase-insights.md`:
   - What was inspected
   - Key findings (with data examples)
   - How it informed design decisions
3. Delete all helper scripts (they are single-use scaffolding)
4. Delete any temporary data exports (CSV, Excel, JSON samples)
5. Create `.dev/.artifacts/design-phase-summary.md` as documented above
6. Verify all 9 design documents in docs/develop/ are complete and consistent
7. Generate final checklist of any open questions requiring user input before implementation

Expected outputs:
- `.dev/.artifacts/design-phase-insights.md` (~3-5 pages)
- `.dev/.artifacts/design-phase-summary.md` (~2-3 pages)
- Clean `.dev/.scripts/python/` directory (empty or only permanent utilities)
- Verification report confirming design phase completion
```

---

**Final Step**: Once cleanup is complete and design phase is verified, proceed to implementation planning with `.github/prompts/plan-closing-tdd-implementation.prompt.md`.
