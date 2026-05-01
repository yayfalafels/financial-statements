---
title: POC
doc_type: requirements
topic_type: reference
owner: poc
scope: poc
---
# POC

**Goals**:

- Deliver a fast local proof that improves monthly close effort versus the current Google Sheets and manual process.
- Prove end-to-end feasibility across local sqlite, Google Sheets, and HomeBudget with minimal workflow disruption.
- Keep setup and operations simple for a single user, while establishing the technical baseline for MVP hardening.

**Scope**: 

- Start from the current local-only workflow, one user, zero cloud cost, and session-based updates.
- Retain HomeBudget as the primary real-time accounting UI and data source
- Retain manual bank statement download and CSV-based IBKR import, with explicit manual review checkpoints.
- Retain forecasting and cash input in their existing Google Sheets and form-driven flows.
- Use Google Sheets as the primary session UI.
- Add local sqlite as the working persistence layer
- Add CLI as a parallel interface for scripting and automation.
- Add new worksheet flow for financial statement reconcile.
