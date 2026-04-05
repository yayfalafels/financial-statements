# POC

**Goals**:

- Deliver a fast local proof that improves monthly close effort versus the current Google Sheets and manual process.
- Prove end-to-end feasibility across local sqlite, Google Sheets, and HomeBudget with minimal workflow disruption.
- Keep setup and operations simple for a single operator, while establishing the technical baseline for MVP hardening.

**Scope**: 

- Start from the current local-only workflow, one operator, zero cloud cost, and session-based updates.
- Add local sqlite as the working persistence layer while retaining Google Sheets assets and JSON config files.
- Keep interaction centered on CLI scripts, HomeBudget, and Google Sheets, including a new worksheet flow for financial statement reconcile.
- Retain manual bank statement download and CSV-based IBKR import, with explicit manual review checkpoints.
- Keep forecasting and cash input in their existing Google Sheets and form-driven flows.
