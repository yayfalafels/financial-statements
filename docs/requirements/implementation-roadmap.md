---
title: Implementation Roadmap
doc_type: requirements
topic_type: reference
owner: implementation-roadmap
scope: poc
---
# Implementation roadmap

This document defines the incremental development of the application in releases from the minimum viable product (MVP) to the full vision. Each release has defined scope, goals, and backlog items that build on the previous release. The roadmap is a living document that may be updated as the project evolves.

| id          |                     |               |                  |                |              |
| ----------- | ------------------- | ------------- | ---------------- | -------------- | ------------ |
| feature     |                     |               |                  |                |              |
| current     |                     |               |                  |                |              |
| POC         |                     |               |                  |                |              |
| MVP         |                     |               |                  |                |              |
| incremental |                     |               |                  |                |              |
| cloud       |                     |               |                  |                |              |
| mobile app  |                     |               |                  |                |              |
| 01          | version             | --            | 0.1.0            | 1.0.0          | 2.x          |
| 02          | goals               | --            | quick win roi    | maintainable   | time savings |
| 03          | cloud costs         | 0             | ~0               | ~0             | ***          |
| 04          | users               | 1             | 1                | 1              | 1            |
| 05          | deployment          | --            | local            | local          | ***          |
| 06          | database            | sqlite + gs   | sqlite + hb      | sqlite + hb    | ***          |
| 07          | ai agent            | no            | no               | no             | ***          |
| 08          | ui                  | hb,gs         | gs primary + cli | browser,gs, hb | ***          |
| 09          | session ui          | gsheet        | gsheet primary   | browser        | ***          |
| 10          | forecasting models  | gsheet        | exist gsheet     | exist gsheet   | ***          |
| 11          | ibkr import         | csv           | csv              | api            | api          |
| 12          | cash input          | form + gsheet | form + gsheet    | form + gsheet  | ***          |
| 13          | homebudget          | local         | local            | local          | ***          |
| 14          | updates             | session       | session          | session        | ***          |
| 15          | hb gsheet           | hb gsheet     | maintain         | maintain       | ***          |
| 16          | bank stm gsheet     | maintain      | maintain         | ui page        | ***          |
| 17          | fin stm gsheet      | maintain      | minimal          | ui page        | ui page      |
| 18          | fin stm reconcile   | gsheet        | new gsheet       | ui page        | ui page      |
| 19          | bank reconcile      | gsheet        | exist gsheet     | ui page        | ui page      |
| 20          | category mapping    | hb + fin gs   | gs ui + crud     | ui page        | ui page      |
| 21          | account             | hb + fin gs   | gs ui + crud     | ui page        | ****         |
| 22          | bank txn rel        | no            | yes              | yes            | yes          |
| 23          | exp-xfr rel         | no            | no               | yes            | yes          |
| 24          | shared exp          | gsheet        | ui page          | ui page        | ui page      |
| 25          | bills               | notion        | ui page          | ui page        | ui page      |
| 26          | bank stm import     | dwnl to csv   | dwnl to csv      | ui embed frame | embed frame  |
| 27          | hb recurring        | user hb       | user hb          | user hb        | ****         |
| 28          | hb session txn crud | user          | app              | app            | app          |

| id          |                     |              |                    |
| ----------- | ------------------- | ------------ | ------------------ |
| feature     |                     |              |                    |
| current     |                     |              |                    |
| POC         |                     |              |                    |
| MVP         |                     |              |                    |
| incremental |                     |              |                    |
| cloud       |                     |              |                    |
| mobile app  |                     |              |                    |
| 01          | version             | 3.x          | 4.x                |
| 02          | goals               | automations  | deprecate hb app   |
| 03          | cloud costs         | < $20/m      | < $30/m            |
| 04          | users               | 1            | 1                  |
| 05          | deployment          | full cloud   | mobile app + cloud |
| 06          | database            | cloud db     | client + mobile db |
| 07          | ai agent            | yes          | yes                |
| 08          | ui                  | web app, hb  | mobile app         |
| 09          | session ui          | web app      | mobile app         |
| 10          | forecasting models  | ui page      | ui page            |
| 11          | ibkr import         | api          | api                |
| 12          | cash input          | web form     | mobile app         |
| 13          | homebudget          | vm           | deprecated         |
| 14          | updates             | event-driven | real-time          |
| 15          | hb gsheet           | ui page      | deprecated         |
| 16          | bank stm gsheet     | ui page      | ui page            |
| 17          | fin stm gsheet      | ui page      | ui page            |
| 18          | fin stm reconcile   | ui page      | ui page            |
| 19          | bank reconcile      | ui page      | ui page            |
| 20          | category mapping    | ui page      | ui page            |
| 21          | account             | ui page      | ui page            |
| 22          | bank txn rel        | yes          | yes                |
| 23          | exp-xfr rel         | yes          | yes                |
| 24          | shared exp          | ui page      | ui page            |
| 25          | bills               | ui page      | ui page            |
| 26          | bank stm import     | redirect     | redirect           |
| 27          | hb recurring        | ui page      | embedded           |
| 28          | hb session txn crud | app          | deprecated         |

## POC

**Goals**:

- Deliver a fast local proof that improves monthly close effort versus the current Google Sheets and manual process.
- Prove end-to-end feasibility across local sqlite, Google Sheets, and the HomeBudget wrapper with minimal workflow disruption.
- Keep setup and operations simple for a single user, while establishing the technical baseline for MVP hardening.

**Scope**: 

- Start from the current local-only workflow, one user, zero cloud cost, and session-based updates.
- Retain Google Sheets as the primary session UI for operational workflows and data entry.
- Retain manual bank statement download and CSV-based IBKR import, with explicit manual review checkpoints.
- Retain forecasting and cash input in their existing Google Sheets and form-driven flows.
- Add local sqlite as the working persistence layer.
- Add CLI as a parallel interface for scripting and automation.
- Add data-sync materialization of `hb_gl_txn`, `hb_account_dim`, and `hb_category_dim` from HomeBudget through the wrapper.
- Add a modularized backend API. Clean separation of concerns between backend services and frontend interfaces enables future UI expansion and potential cloud deployment without major rework.
- Add new custom Google sheets UI including new worksheets for session management, financial statement reconcile, bank statements reconcile, bill payment and potentially others.

### Features

- Financial statements in Google Sheets remain minimal but are sufficient for monthly close output.
- Financial statement reconcile moves from current worksheet logic to a new worksheet workflow, while bank reconcile remains in the existing workbook flow.
- Category and account mapping move to a category data model managed through a custom Google Sheets UI with backend CRUD operations.
- HomeBudget source reads move to wrapper-driven data sync that refreshes `hb_gl_txn`, `hb_account_dim`, and `hb_category_dim`.
- Bank transaction relation handling is enabled, while expense-to-transfer relation remains out of scope for this release.
- HomeBudget and bank statement Google Sheet maintenance continues for compatibility.
- HomeBudget recurring behavior remains user-managed in HomeBudget.
- HomeBudget session transaction CRUD moves from user-managed activity to app-supported updates using the HB wrapper.
- Forecasting models and cash input stay in their current Google Sheets and Google Form pipeline.


## MVP

**Goals**:

- Ship a stable and maintainable `1.0.0` release for repeatable monthly close operations.
- Shift from current and POC sheet-heavy operations to a browser-first operational experience.
- Preserve the local cost profile while improving consistency, auditability, and user speed.

**Scope**: 

- Local deployment, local sqlite, one-user usage, and zero-cloud-cost expectations remain the runtime baseline, with no AI agent in this release.
- Browser becomes the primary session UI and primary operational surface, replacing the current Google Sheets-first session workflow.
- Google Sheets and HomeBudget integrations remain active for compatibility, while primary UI moves to app UI pages.
- IBKR import upgrades from current and POC CSV workflow to API-based import.
- Data sync continues to refresh `hb_gl_txn`, `hb_account_dim`, and `hb_category_dim` from the HomeBudget wrapper as the canonical app-managed HomeBudget state.
- Updates remain session-based with explicit user-run close cycles.

### Features

- Browser UI pages cover bank statement handling, financial statements update and review, financial statement reconcile, bank reconcile, category mapping, and account management.
- Financial statement and bank statement workflows move from maintained sheets to UI-page-driven operation.
- Bank statement import is exposed through embedded UI frame integration.
- Existing Google Sheet assets for HomeBudget integration are maintained for compatibility and transition safety.
- HomeBudget sync tables remain `hb_gl_txn`, `hb_account_dim`, and `hb_category_dim`, with `hb_txn_uid` as the synced transaction lineage key.
- Forecasting and cash input continue via Google Sheets and form-based capture.
- Bank transaction relation and expense-to-transfer relation are both supported.
- Shared expenses and bills move from current sheet and Notion workflows to UI-page-driven operation.
- HomeBudget recurring remains user-managed in HomeBudget.
- HomeBudget session transaction CRUD remains app-supported using the HB wrapper.


