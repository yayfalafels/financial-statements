# Requirements Decisions

## Table of contents

- [Summary](#summary)
- [Decision inventory](#decision-inventory)
- [Topic index](#topic-index)
- [Bill payment](#bill-payment)

## Summary

This document is the design-side tracker for requirement decisions and open requirement questions.

Requirements documents remain static and do not link to this tracker. This tracker links to requirement sources.

## Decision inventory

| id | status   | topic                    | description                                                       |
| -- | -------- | ------------------------ | ----------------------------------------------------------------- |
| 01 | accepted | bill payment             | splitwise usage, deprecated                                       |
| 02 | accepted | bill payment             | commit mode, direct post to hb                                    |
| 03 | accepted | bill payment             | singtel handling, incremental charges                             |
| 04 | closed   | bill payment             | bridge field mapping for bills                                    |
| 05 | closed   | bill payment             | per-payee variance tolerance policy                               |
| 06 | accepted | exception-error-handling | remediation flow for missing category mapping at close time       |
| 07 | accepted | exception-error-handling | remediation flow for source validation failure during ingest/sync |
| 08 | open     | exception-error-handling | audit retention duration and storage format for exception events  |
| 09 | accepted | transaction categories   | expense category groups: rental/COLE/discretionary model           |

## Topic index

- Bill payment, source: [docs/requirements/bill-payment.md](../../../requirements/bill-payment.md)
- Exception and error handling, source: [docs/requirements/exception-error-handling.md](../../../requirements/exception-error-handling.md)
- Transaction categories, source: [docs/requirements/transaction-categories.md](../../../requirements/transaction-categories.md)

## Bill payment

Source requirements document: [docs/requirements/bill-payment.md](../../../requirements/bill-payment.md)

### Closed Decisions

- 01 Splitwise usage, deprecated.
- 02 Commit mode, direct post to hb.
- 03 Singtel handling, incremental charges.
- 04 Google Sheets UI field mapping. GS UI is a new feature; exact field mapping is designer responsibility at design time following variable naming and data model guidelines in design-guidelines.md.
- 05 Variance tolerance policy. Bill-level tolerance is SGD 0.00 exact match per reconciliation check 01 in bill-payment.md. Escalation behavior is out-of-scope and is owned by interaction-approvals.md.

## Exception and error handling

Source requirements document: [docs/requirements/exception-error-handling.md](../../../requirements/exception-error-handling.md)

| id    | status   | decision                                                                        | 
| ----- | -------- | ------------------------------------------------------------------------------- |
| EE-03 | accepted | remediation flow for missing category mapping at close time                     |
| EE-04 | accepted | remediation flow for source validation failure during data ingest or sync       |
| EE-05 | open     | audit retention duration and storage format for exception event records         |

## Transaction categories

Source requirements document: [docs/requirements/transaction-categories.md](../../../requirements/transaction-categories.md)

| id    | status   | decision                                                                        | 
| ----- | -------- | ------------------------------------------------------------------------------- |
| TC-01 | accepted | expense category group model: rental/COLE/discretionary (replaces personal/household) |

### Decision TC-01: Expense category group model redesign

**Problem statement**: The legacy personal/household expense categorization model grouped expenses by origin (whether the transaction originated from personal spending patterns vs. household/shared patterns). This origin-based grouping did not align well with analytical and operational needs, which require grouping expenses by their financial characteristics and commitment level.

**Solution**: Replace the personal/household two-group model with a three-group model based on expense characteristics:

| Group | Description | Use Case |
| ----- | ----------- | -------- |
| Rental | Fixed monthly housing cost (always rental expense only) | Separate committed fixed cost from discretionary spending for cash flow analysis |
| COLE | Cost of living expenses - essential committed spending on food, transport, insurance, utilities, healthcare, and personal services | Recurring baseline commitments for monthly budget forecasting and reconciliation |
| Discretionary | Optional spending on travel, entertainment, education, durables, and other non-essential items | Separate variable spending from fixed commitments for expense control and lifestyle analysis |

**Rationale**: 
- The three-group model aligns expense categories with their financial commitment level: rental (non-negotiable fixed), COLE (recurring essential), and discretionary (variable optional).
- This classification is more useful for financial planning (budgeting committed vs. optional spending), cash reconciliation (baseline expenses vs. anomalies), and close-cycle reporting (separating essential costs from lifestyle choices).
- The model is stable across time periods and user behavior changes, unlike origin-based grouping which is harder to justify and maintain.

**Impact**:
- Expense categories are reassigned from personal_expenses and household_expenses groups to rental_expenses, cole_expenses, or discretionary_expenses groups.
- Statement aggregation rules in financial-statements.md now group expenses into rental, COLE, and discretionary line items.
- The transaction-categories.md document includes a new "Legacy vs new model" reference section explaining the mapping from old to new group assignments.
- Design-phase translation documentation at docs/develop/010/design/category-account-model-translation.md provides the full mapping reference.

**Acceptance**: This decision is reflected in:
- docs/requirements/transaction-categories.md: Category groups table and expense category table assignments
- docs/requirements/financial-statements.md: Expense breakdown layout showing three separate sections for rental, COLE, and discretionary
- docs/develop/010/design/category-account-model-translation.md: Full mapping reference from legacy to new model (design artifact)