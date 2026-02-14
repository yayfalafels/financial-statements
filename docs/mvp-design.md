# MVP design

## Table of contents

- [Overview](#overview)
- [Goals](#goals)
- [Non goals](#non-goals)
- [Assumptions](#assumptions)
- [Scope and workflow boundaries](#scope-and-workflow-boundaries)
- [System context](#system-context)
- [Data and artifacts](#data-and-artifacts)
- [Automation design](#automation-design)
- [Operational concerns](#operational-concerns)
- [Backlog updates](#backlog-updates)

## Overview

This document defines the MVP design for workflow automation. The MVP runs locally, targets a single operator, and produces PDF statements with S3 upload. It follows the workflow described in [docs/workflow.md](docs/workflow.md) and supports the project goals in [docs/about.md](docs/about.md).

## Goals

- Automate the repeatable workflow steps for forex, calculations, balance updates, HomeBudget CRUD, and statement upload.
- Keep manual steps for authentication, statement download, and report review.
- Produce reliable artifacts with a clear audit trail and recovery path.
- Minimize setup to a local Python and bash workflow on Windows.

## Non goals

- Web application user experience or hosted services.
- Multi user coordination and permissions.
- Full automation of report review or statement download.

## Assumptions

- The operator can access all websites needed for statement download and authentication.
- Google Sheets access is configured using the paths in [docs/google-sheets.md](docs/google-sheets.md).
- HomeBudget data is available locally as described in [docs/homebudget.md](docs/homebudget.md).
- S3 credentials are available in the local environment.

## Scope and workflow boundaries

Automated steps

- Pre flight checks for required files, credentials, and sheet access.
- Session close out steps that consolidate logs and artifacts.
- Forex rate fetch and sheet update.
- Calculations in helper workbooks for IBKR and CPF.
- CRUD updates to the balances sheet.
- CRUD updates to the HomeBudget database for income, expenses, and transfers.
- PDF statement upload to S3.

Manual steps

- Authentication and statement download.
- Report update and review, including reconcile steps.

## System context

External systems

- Google Sheets for workbook storage and worksheet updates.
- HomeBudget local database for transaction updates.
- AWS S3 for statement storage.
- Yahoo Finance for USD to SGD forex rates.

Local components

- Python scripts for data extraction, transformation, and updates.
- Bash or PowerShell scripts for orchestration and task sequencing.
- Local workspace for logs, temporary exports, and PDF files.

## Data and artifacts

Inputs

- Statement files downloaded manually.
- Existing Google Sheets workbook and helper worksheets.
- HomeBudget local database.

Outputs

- Updated worksheet tabs for forex rates, balances, and supporting calculations.
- Updated HomeBudget transactions for income, expenses, and transfers.
- PDF statements stored locally and uploaded to S3.
- Logs and run summaries for audit and recovery.

Storage locations

- Workspace data and logs under [data/](data/).
- Configuration under [gsheet/](gsheet/).
- Reference content under [reference/](reference/).

## Automation design

Execution flow

1. Pre flight checks
2. Forex rates fetch and update
3. Account updates for wallets, IBKR, and CPF
4. Balance sheet update
5. HomeBudget updates
6. Report generation review, manual
7. PDF upload to S3
8. Session close out

Script boundaries

- One orchestrator script that calls smaller step scripts.
- Step scripts are idempotent where possible and validate inputs before changes.
- Each step writes a structured log and a summary of changes.

Integration contracts

- Google Sheets uses `sqlite-gsheet` with a defined worksheet mapping.
- HomeBudget access follows the patterns in [docs/homebudget.md](docs/homebudget.md).
- S3 uploads use a standard naming convention and folder prefix by month.

Error handling and recovery

- Fail fast on missing credentials or missing sheet access.
- Log every update with a timestamp and a run identifier.
- Store a rollback snapshot for balances and HomeBudget updates.

## Operational concerns

- Logging uses a structured format with a human readable summary.
- Configuration is stored in JSON and never hard coded in scripts.
- Credentials are never committed and are validated during pre flight checks.
- Each run produces a checklist summary for manual review steps.

## Backlog updates

- Add a design milestone that captures this MVP scope and workflow boundary.
- Split automation tasks by workflow step and account type.
- Add explicit tasks for logging, rollback snapshots, and run summaries.
- Add a task for S3 naming conventions and retention policy.
