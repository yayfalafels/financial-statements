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
| 06 | open     | exception-error-handling | remediation flow for missing category mapping at close time       |
| 07 | open     | exception-error-handling | remediation flow for source validation failure during ingest/sync |
| 08 | open     | exception-error-handling | audit retention duration and storage format for exception events  |

## Topic index

- Bill payment, source: [docs/requirements/bill-payment.md](../../../requirements/bill-payment.md)
- Exception and error handling, source: [docs/requirements/exception-error-handling.md](../../../requirements/exception-error-handling.md) (pending)

## Bill payment

Source requirements document: [docs/requirements/bill-payment.md](../../../requirements/bill-payment.md)

### Closed Decisions

- 01 Splitwise usage, deprecated.
- 02 Commit mode, direct post to hb.
- 03 Singtel handling, incremental charges.
- 04 Google Sheets UI field mapping. GS UI is a new feature; exact field mapping is designer responsibility at design time following variable naming and data model guidelines in design-guidelines.md.
- 05 Variance tolerance policy. Bill-level tolerance is SGD 0.00 exact match per reconciliation check 01 in bill-payment.md. Escalation behavior is out-of-scope and is owned by interaction-approvals.md.

## Exception and error handling

Source requirements document: [docs/requirements/exception-error-handling.md](../../../requirements/exception-error-handling.md) (pending)

| id    | status | decision                                                                        | resolution |
| ----- | ------ | ------------------------------------------------------------------------------- | ---------- |
| EE-03 | open   | remediation flow for missing category mapping at close time                     | —          |
| EE-04 | open   | remediation flow for source validation failure during data ingest or sync       | —          |
| EE-05 | open   | audit retention duration and storage format for exception event records         | —          |
