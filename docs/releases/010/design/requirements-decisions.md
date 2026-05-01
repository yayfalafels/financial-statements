---
doc_type: design-analysis
title: Requirements Decisions — Open Questions for User
status: Updated with user decisions
created: 2026-04-26
phase: Design Phase 1 - Discovery and Analysis
---

# Requirements Decisions

## Table of contents

- [Summary](#summary)
- [Decision inventory](#decision-inventory)
- [Resolved decisions](#resolved-decisions)
- [CPF interest timing note](#cpf-interest-timing-note)

## Summary

This document records resolved requirement decisions using the established stable ID and status format.

Most design-audit items are now resolved from user direction. Items that were design implementation details, not requirement gaps, were removed.

## Decision inventory

| seq | id | status   | topic                     | decision                          |
| --- | -- | -------- | ------------------------- | --------------------------------- |
| 01  | 01 | accepted | forex m2m                | accepted, see resolved section 01 |
| 02  | 02 | accepted | ibkr posting             | accepted, see resolved section 02 |
| 03  | 03 | accepted | ibkr m2m                 | accepted, see resolved section 02 |
| 04  | 04 | accepted | cash rerun idempotency   | accepted, see resolved section 04 |
| 05  | 05 | accepted | cash uniqueness key      | accepted, see resolved section 04 |
| 06  | 06 | accepted | duplicate identity check | accepted, see resolved section 04 |
| 07  | 07 | accepted | category sot transition  | accepted, see resolved section 07 |
| 08  | 08 | accepted | requirement boundary     | accepted, see resolved section 07 |
| 09  | 09 | accepted | cpf interest timing      | expected period is year-end through 1 Jan of following year |

---

## Resolved decisions

### 01 forex m2m data model

- Forex belongs in close_book design, not in single-currency account ledger posting.
- Roll M2M into net worth and net income totals in constant SGD basis.
- Keep implementation simple and aligned with personal-finance scope.
- Use standard accounting-software patterns for unrealized FX and keep auditability.

### 02 and 03 ibkr posting and m2m

- End-of-period aggregate entries are the default for IBKR.
- Withdrawals are transaction-level because they are bank-linked and transaction-reconciled.
- Create M2M transactions for IBKR.

### 04, 05, and 06 cash dedup and uniqueness

- GS cash is aggregated, then HB entries are created or updated.
- Re-running reconciliation should be idempotent, no duplicate creation on unchanged records.
- Use account, category, note, amount as uniqueness key for this flow.
- If amount changes and other key fields remain stable, update the amount.
- If two entries are fully identical on account, date, amount, description, raise a user exception instead of silent merge.

---

### 07 and 08 source of truth and requirement boundary

- During transition, legacy source remains source of truth until SQLite is created and validated.
- After validation, SQLite is source of truth and Google Sheets is UI only.
- Data model and schema completion is a design-stage responsibility.

## CPF interest timing note

### 09 cpf interest credit timing

- Working direction is year-end handling and after-the-fact booking accuracy.
- CPF official FAQ confirms interest is computed monthly and credited by the following year with annual compounding.
- Non-official Singapore finance references state practical credit timing as by 1 January of the following year, with observed year-end credit in some statements.
- Expected annual credit period is year-end through 1 January of the following year.
- Precision emphasis is booking correctness after credit posts, not high-precision forecast compounding.
