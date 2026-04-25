# Phase-Based Testing Acceptance Criteria

**Document Type**: Phase Acceptance Criteria  
**Status**: Active  
**Last updated**: 2026-03-08  
**Purpose**: Define phase-by-phase testing scope, evolving test focus, and acceptance criteria for implementation delivery gates

---

## Table of Contents

- [Overview](#overview)
- [How to Use This Document](#how-to-use-this-document)
- [Phase 1: Shared Infrastructure](#phase-1-shared-infrastructure)
- [Phase 2: Quick Wins - Forex and Wallets](#phase-2-quick-wins---forex-and-wallets)
- [Phase 3: Cash Reconcile Refactoring](#phase-3-cash-reconcile-refactoring)
- [Phase 4: Bill Payment Automation](#phase-4-bill-payment-automation)
- [Phase 5: Bank Statements Reconciliation](#phase-5-bank-statements-reconciliation)
- [Phase 6: IBKR Account Update](#phase-6-ibkr-account-update)
- [Phase 7: CPF Account Update](#phase-7-cpf-account-update)
- [Phase 8: Financial Statements and HB Reconciliation](#phase-8-financial-statements-and-hb-reconciliation)
- [Phase 9: CLI and Orchestration](#phase-9-cli-and-orchestration)

---

## Overview

This document contains the **phase-based testing roadmap** and **acceptance criteria** for implementation gates.

The high-level, relatively stable strategy (test philosophy, taxonomy, safety model, and governance) is maintained in:

- [Test-Driven Development Strategy](test-strategy.md)

---

## How to Use This Document

Testing follows the 9-phase implementation plan defined in [TDD Implementation Plan](../../../.github/prompts/plan-closing-tdd-implementation.prompt.md). For each phase:

1. **Reference high-level strategy** in `test-strategy.md`
2. **Implement detailed test cases** for the current phase
3. **Validate all tests pass** before moving to the next phase
4. **Update this document** as phase-level acceptance criteria evolve

---

## Phase 1: Shared Infrastructure

**Scope**: Foundation modules used by all higher-level features

**Modules**:

- `util/types.py` â€” Period, Account, TransactionData, exceptions
- `util/gsheet.py` â€” Google Sheets read-only client wrapper
- `util/homebudget.py` â€” HomeBudget accounting logic wrapper
- `util/s3.py` â€” S3 backup and report upload wrapper
- `util/validation.py` â€” Shared validation contracts
- `util/logging.py` â€” Structured logging and audit trail

**Test Strategy**:

| Module | SIT Coverage Target | UAT | Rationale |
|--------|---------------------|-----|-----------|
| types.py | 95% | None | Pure logic, no external deps |
| gsheet.py | 70% | Basic read | Mock for SIT, UAT verifies API contract |
| homebudget.py | 70% | CRUD ops | Mock for SIT, UAT verifies wrapper correctness |
| s3.py | 70% | Upload test | Mock for SIT, UAT verifies S3 upload/delete |
| validation.py | 90% | None | Shared validators must be bulletproof |
| logging.py | 60% | None | Mostly pass-through to standard library |

**SIT Test Focus**:

- Period: Valid/invalid months, year ranges, string formatting, comparison
- Account: Type validation, currency defaults, immutability
- TransactionData: Required fields, optional fields, validation
- Exceptions: Correct error types raised, messages formatted properly
- GSheet: Mocked responses, retry logic, error handling
- HomeBudget: Mocked CRUD operations, double-entry validation
- S3: Mocked boto3 responses, path formatting, retry logic, error handling

**UAT Test Focus**:

- GSheet: Fetch one range from real workbook (`cash-expenses.json` -> `recent_txns`)
- HomeBudget: Read balance from real DB, write one test transaction, verify it appears, rollback
- S3: Upload test file to configured bucket, verify exists, delete (cleanup)

**Acceptance Criteria**:

- [ ] All SIT tests pass with >85% coverage for utilities
- [ ] UAT successfully reads from Google Sheets and HomeBudget
- [ ] UAT successfully uploads to and deletes from S3
- [ ] UAT rollback mechanism verified (transaction created and reverted)
- [ ] No linting errors

---

## Phase 2: Quick Wins - Forex and Wallets

**Scope**: Low-risk features with minimal external dependencies

**Features**:

- Forex rate fetch (Yahoo Finance API -> SQLite cache)
- Wallet account balance query (read-only HomeBudget query)

**Test Strategy**:

| Feature | SIT Coverage Target | UAT | Rationale |
|---------|---------------------|-----|-----------|
| Forex fetch | 80% | API call + cache | Mock API responses for SIT, UAT verifies real API |
| Wallet balances | 85% | Read real HB | Mock HomeBudget for SIT, UAT queries live DB |

**SIT Test Focus**:

- Forex: Mocked API responses, cache hit/miss, rate validation, tolerance checks, retry logic
- Wallets: Mocked HomeBudget query, balance aggregation by currency

**UAT Test Focus**:

- Forex: Fetch USD/SGD rate for current period, verify rate is within +/-5% of prior month
- Wallets: Query balance for `Cash TWH SGD`, compare to manually read balance from app

**Acceptance Criteria**:

- [ ] Forex rate cached in SQLite, reused on subsequent calls
- [ ] Wallet balances match HomeBudget app (UAT manual verification)
- [ ] All SIT tests pass with >80% coverage

---

## Phase 3: Cash Reconcile Refactoring

**Scope**: Simplify over-designed cash reconciliation implementation

**Current State**: Complex variance explanation, custom Money class, multi-module structure

**Target State**: 1-2 modules with simplified logic, float arithmetic, shared utilities

**Test Strategy**:

| Component | SIT Coverage Target | UAT | Rationale |
|-----------|---------------------|-----|-----------|
| Cash gap calculation | 95% | E2E flow | Core business logic, high risk |
| Adjustment generation | 90% | Transaction commit | Critical for data integrity |
| Tolerance alerting | 85% | User workflow | User checkpoint must be correct |

**SIT Test Focus**:

- Gap calculation: Known scenarios (exact, +/-$0.01 rounding, +/-$20 threshold, +/-$100 gap)
- Adjustment transaction: Correct account, amount, sign, category, notes
- Tolerance logic: Alert triggered at +/-$20.01, not at +/-$19.99
- Edge cases: Zero expenses, negative gap (found cash), missing Google Sheet data

**UAT Test Focus**:

- Full workflow: User inputs cash count -> fetch GSheet -> query HB -> calculate gap -> prompt user -> create adjustment
- Rollback: Verify adjustment transaction can be rolled back if user declines
- Real data: Use actual `cash-expenses.json` workbook and `Cash TWH SGD` account

**Reconciliation Algorithm Test Strategy**:

- **SIT**: Comprehensive mock scenarios covering all gap sizes and tolerance boundaries
- **UAT**: End-to-end validation with real cash count and Google Sheet data
- **Hybrid approach**: SIT ensures algorithm correctness, UAT validates integration and UX

**Acceptance Criteria**:

- [ ] Simplified to 1-2 Python files (down from 5+)
- [ ] All SIT tests pass with >90% coverage for gap calculation
- [ ] UAT successfully creates adjustment transaction and rolls back
- [ ] Alert triggered only when variance > +/-$20

---

## Phase 4: Bill Payment Automation

**Scope**: Parse bill statements, allocate shared costs, generate HomeBudget transactions

**Modules**:

- `bill_payment/parsers.py` â€” Statement file parsers (DBS, UOB, Citi, BOA, SP Services, Singtel)
- `bill_payment/allocation.py` â€” Shared cost split logic (1/3 personal, 2/3 flatmates)
- `bill_payment/posting.py` â€” HomeBudget transaction generation (expense + settlement)

**Test Strategy**:

| Component | SIT Coverage Target | UAT | Rationale |
|-----------|---------------------|-----|-----------|
| Statement parsers | 75% | Sample files | SIT with fixtures, UAT with real PDFs/CSVs |
| Allocation logic | 90% | Manual review | Core business logic, must be exact |
| Transaction generation | 85% | HB commit | Critical for double-entry correctness |

**SIT Test Focus**:

- Parsers: Each bank format with 5-10 transaction samples, edge cases (multi-page, missing fields)
- Allocation: Known scenarios (1/3 split, 100% personal, zero bill amount)
- Posting: Verify double-entry (expense + settlement), category mapping, notes formatting

**UAT Test Focus**:

- Parse real bill statement (e.g., Feb 2026 SP Services PDF)
- upload to S3
- Verify line items extracted correctly (user reviews parsed data vs. PDF)
- Approve allocation and commit transactions to HomeBudget
- Rollback if allocation incorrect

**Acceptance Criteria**:

- [ ] All supported bill formats parse successfully in SIT
- [ ] UAT parses real bill and user approves allocation
- [ ] Double-entry transactions balance (expense = transfer + settlement)
- [ ] Statements uploaded to S3 with correct path and naming convention
- [ ] All SIT tests pass with >80% coverage

---

## Phase 5: Bank Statements Reconciliation

**Scope**: Import and reconcile active bank account and credit card statements against HomeBudget ledger

**Context**: This phase implements the most complex reconciliation logic, matching existing HomeBudget placeholder transactions to statement transactions. The reconciliation pattern established here provides a base for simpler adapters in later phases.

**Modules**:

- `account_update/bank_statement_adapter.py` â€” Bank statement parsers (DBS, UOB, Citi, BOA)
- `account_update/reconcile_base.py` â€” Base reconciliation logic
- `account_update/reconcile_bank.py` â€” Bank-specific transaction matching and pending detection

**Test Strategy**:

| Component | SIT Coverage Target | UAT | Rationale |
|-----------|---------------------|-----|-----------|
| Bank parsers | 75% | Sample files | SIT with fixtures, UAT with real CSVs/PDFs |
| Reconciliation algorithm | 90% | E2E flow | Complex matching logic, high risk |

**SIT Test Focus**:

- Parsers: Each bank format with 10-20 transaction samples, handle multi-page statements
- Reconciliation: Transaction matching by date/amount/description, pending transaction detection
- Edge cases: Duplicate transactions, amended transactions, bank fees, forex adjustments

**Transaction Matching Test Scenarios**:

1. **Exact match**: Statement txns all present in HB ledger
2. **Missing HB txn**: Statement has txn not in HB (add to HB)
3. **Missing statement txn**: HB has txn not in statement (remove from HB or mark pending)
4. **Amount mismatch**: Same txn, different amounts (forex rounding, bank adjustment)
5. **Duplicate detection**: Same day, same amount, same description (suffix with -01, -02)
6. **Pending transactions**: HB txn dated before cut-off but not in statement (defer to next period)
7. **Heuristic filtering**: Net-zero edit pairs (remove-then-add same amount)

**UAT Test Focus**:

- Import real bank statement (e.g., Feb 2026 DBS checking account)
- Verify all transactions matched or flagged as missing
- Review pending transactions (HB dated before statement but not cleared)
- Approve reconciliation adjustments and commit to HomeBudget
- Rollback if variance unexplained

**Acceptance Criteria**:

- [ ] All supported bank formats parse successfully in SIT
- [ ] Transaction matching algorithm passes all 7 SIT scenarios
- [ ] UAT successfully imports real bank statement and reconciles transactions
- [ ] Pending transaction detection works correctly
- [ ] Variance within tolerance auto-approved, over-tolerance prompts user
- [ ] All SIT tests pass with >90% coverage for matching logic, >75% for parsers

---

## Phase 6: IBKR Account Update

**Scope**: Import IBKR brokerage statements, parse positions and transactions, post to HomeBudget

**Context**: IBKR is primarily greenfield transaction creation (not matching existing placeholders), with balance verification as the main reconciliation checkpoint.

**Modules**:

- `account_update/ibkr_adapter.py` â€” IBKR statement parser and posting
- `account_update/reconcile_base.py` â€” Base reconciliation for balance verification

**Test Strategy**:

| Component | SIT Coverage Target | UAT | Rationale |
|-----------|---------------------|-----|-----------|  
| IBKR parser | 70% | Sample statement | SIT with fixture, UAT with real Activity Statement |
| Balance reconciliation | 85% | E2E flow | Simpler than transaction matching, focus on variance detection |

**SIT Test Focus**:

- IBKR: Parse multi-currency positions, cash balances, dividends, fees, M2M adjustments
- Posting: Generate transactions for positions, dividends, interest, fees
- Balance verification: Compare ending balances (cash + positions) to statement
- Edge cases: Multi-currency forex conversions, corporate actions, margin interest

**UAT Test Focus**:

- Import real IBKR statement (Feb 2026), verify balances match online portal
- Verify cash and position balances separately
- Approve generated transactions and commit to HomeBudget
- Rollback if variance unexplained

**Acceptance Criteria**:

- [ ] UAT successfully imports IBKR statement and balances match portal
- [ ] IBKR-specific parsing handles multi-currency positions correctly
- [ ] Variance within tolerance auto-approved, over-tolerance prompts user
- [ ] All SIT tests pass with >85% coverage for balance reconciliation

---

## Phase 7: CPF Account Update

**Scope**: Import CPF retirement account statements, reconcile contributions and interest against HomeBudget

**Context**: CPF has simple, predictable placeholder transactions (monthly contributions, annual interest) that are easy to identify and reconcile without complex matching.

**Modules**:

- `account_update/cpf_adapter.py` â€” CPF statement parser and reconciliation
- `account_update/reconcile_base.py` â€” Base reconciliation for balance verification

**Test Strategy**:

| Component | SIT Coverage Target | UAT | Rationale |
|-----------|---------------------|-----|-----------|
| CPF parser | 70% | Sample statement | SIT with fixture, UAT with real contribution statement |
| Balance reconciliation | 85% | E2E flow | Simple placeholder matching, focus on splits and interest |

**SIT Test Focus**:

- CPF: Extract OA/SA/MA/RA balances, contributions, interest, withdrawals
- Reconciliation: Verify contribution splits (employee/employer), interest accrual
- Edge cases: Medisave withdrawals, CPF LIFE deductions, yearly interest posting

**UAT Test Focus**:

- Import real CPF statement, verify against CPF website screenshot
- Verify contribution amounts match employer payslip
- Approve reconciliation adjustments and commit to HomeBudget
- Rollback if variance unexplained

**Acceptance Criteria**:

- [ ] UAT successfully imports CPF statement and balances match website
- [ ] CPF-specific logic handles OA/SA/MA/RA splits correctly
- [ ] Interest calculations verified against manual computation
- [ ] All SIT tests pass with >70% coverage for CPF adapter

---

## Phase 8: Financial Statements and HB Reconciliation

**Scope**: Generate consolidated financial statements from reconciled HomeBudget data

**Modules**:

- `statements/trial_balance.py` â€” Query HB ledger and aggregate by account type
- `statements/income_statement.py` â€” Income statement generation
- `statements/balance_sheet.py` â€” Balance sheet generation
- `statements/forex_adjustments.py` â€” M2M forex gain/loss calculations
- `statements/persistence.py` â€” SQLite storage for generated statements

**Test Strategy**:

| Component | SIT Coverage Target | UAT | Rationale |
|-----------|---------------------|-----|-----------|
| Trial balance | 85% | Manual review | Core accounting logic |
| Income statement | 85% | PDF review | User-facing output, must be correct |
| Balance sheet | 85% | PDF review | User-facing output, must be correct |
| Forex adjustments | 90% | Manual calc | Complex calculations, high risk |
| Persistence | 70% | None | Mostly DB CRUD, lower risk |

**SIT Test Focus**:

- Trial balance: Aggregate by account type, balance check (assets = liabilities + equity)
- Income statement: Category hierarchy, subtotals, net income calculation
- Balance sheet: Opening/closing balances, M2M adjustments, currency conversion
- Forex: Known scenarios (10% rate change, zero balance, multi-currency)

**UAT Test Focus**:

- Generate statements for Feb 2026 with real HomeBudget data
- User reviews PDF output vs. manual calculations
- User verifies balance sheet balances match account portal screenshots
- User approves statement finalization

**Acceptance Criteria**:

- [ ] Balance sheet balances (assets = liabilities + equity identity holds)
- [ ] Income statement net income matches balance sheet retained earnings delta
- [ ] UAT PDF output matches user's manual calculations
- [ ] All SIT tests pass with >85% coverage

---

## Phase 9: CLI and Orchestration

**Scope**: Command-line interface and workflow runner to execute monthly closing steps

**Modules**:

- `cli/commands.py` â€” CLI command definitions (forex, accounts, reconcile, statements, finalize)
- `orchestration/workflow_runner.py` â€” Step graph execution and checkpoint control
- `orchestration/session_manager.py` â€” Persisted step status and resume state

**Test Strategy**:

| Component | SIT Coverage Target | UAT | Rationale |
|-----------|---------------------|-----|-----------|
| CLI commands | 55% | E2E workflow | Many code paths (help, args), focus on critical flows |
| Workflow runner | 65% | E2E workflow | Orchestration logic with checkpoints |
| Session manager | 70% | Resume test | State persistence must be reliable |

**SIT Test Focus**:

- CLI: Argument parsing, command dispatch, error messages
- Workflow: Step sequencing, checkpoint gating, error recovery
- Session: State save/load, resume from checkpoint, rollback on failure

**UAT Test Focus**:

- Full monthly closing workflow: forex -> accounts -> reconcile -> statements -> finalize
- User prompted at checkpoints (variance review, statement approval)
- Interrupt workflow mid-step, resume from last checkpoint
- Verify session state saved correctly and resume works

**Acceptance Criteria**:

- [ ] UAT completes full closing workflow without errors
- [ ] Session resume works after interruption
- [ ] All user checkpoints prompt correctly
- [ ] All SIT tests pass with >60% coverage for orchestration
