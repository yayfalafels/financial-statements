# Financial statements App

- [Overview](#overview)
- [Version](#version)
- [Related resources](#related-resources)

## Overview

The financial statements app aims to streamline the financial statements workflow, which includes fetching forex rates, updating accounts, and generating reports. The app interfaces with Google Sheets, AWS S3, and the HomeBudget App to read and update expenses, and it produces financial statements in PDF format for review and record-keeping.

## Version

Current version: `0.1.0` POC

**Goals**

- Deliver a fast local proof that improves monthly close effort versus the current Google Sheets and manual process.
- Prove end-to-end feasibility across local sqlite, Google Sheets, and HomeBudget with minimal workflow disruption.
- Keep setup and operations simple for a single operator, while establishing the technical baseline for MVP hardening.

**Included in this release**:

- local cli-based application that works with multiple integrates multiple data sources, implements accounting logic and automates data processing workflows
- current local-only workflow, one operator, zero cloud cost, and session-based updates.
- Add local sqlite as the working persistence layer while retaining Google Sheets assets and JSON config files.
- Move management of HomeBudget session transactions from user-managed activity to app-supported workflow.

for detailed release scope and features, refer to the [requirements](requirements.md) 

## Related resources

- [Current Workflow](requirements/current-workflow.md) - description of the existing manual financial statements workflow, including sequential steps and time estimates.
- [App Workflows Design](develop/010/design/app-workflows.md) - intended automated workflow design for the MVP application.
- [HomeBudget](requirements/homebudget.md) - guide to interfacing with the HomeBudget App, including reference to the `hb-finances` repository for code examples on how to read and update expenses in the HomeBudget local sqlite database.
- [Google Sheets](requirements/google-sheets.md) - guide to interfacing with Google Sheets via the Google Sheets API and the `sqlite-gsheet` utility for using pandas with Google Sheets and SQL Alchemy supported database connections.
- [Dependencies](requirements/dependencies.md) - list of dependencies, including `sqlite-gsheet`, a Python library for using pandas with Google Sheets and SQL Alchemy supported database connections.




