---
title: Tech Stack
version: 1.0
status: draft
last_updated: 2026-05-03
---

# Tech Stack

## Summary

This document defines the POC tech stack for runtimes, dependencies, and libraries across all architecture components and workflow stages.

## Table of contents

- [Scope and sources](#scope-and-sources)
- [Runtime baseline](#runtime-baseline)
- [Dependency policy](#dependency-policy)
- [Component stack matrix](#component-stack-matrix)
- [Workflow stage stack matrix](#workflow-stage-stack-matrix)
- [Library register](#library-register)
- [Operational constraints](#operational-constraints)

## Scope and sources

In scope:

- Runtime profiles for all architecture components
- Library and dependency contracts for each workflow stage
- Required and optional dependency classification

Out of scope:

- Build and deployment implementation details
- Production infrastructure sizing and scaling policy

Design sources used for functional requirements:

- architecture.md
- workflows.md
- requirements/dependencies.md
- requirements/environment.md
- requirements/workflow-orchestration.md

## Runtime baseline

| id | runtime profile    | purpose                                                     |
| -- | ------------------ | ----------------------------------------------------------- |
| 01 | windows 11 local   | operator host for file download, local processing, and CLI |
| 02 | python 3.12.10     | primary runtime for backend API, adapters, orchestration   |
| 03 | sqlite local file  | canonical persistence for close state, lineage, and output |
| 04 | google sheets ui   | primary user interaction surface for close session          |
| 05 | gas optional       | optional click-event bridge for selected sheet actions      |
| 06 | aws s3 external    | artifact archive and publish target                         |
| 07 | nodejs optional    | optional guided web workflow extension runtime              |

## Dependency policy

- Python is the required primary runtime.
- homebudget is a required dependency for HomeBudget integration boundaries.
- Google Sheets integration uses a direct Google SDK adapter implementation.
- sqlite-gsheet is excluded from the release runtime dependency path.
- PDF artifact generation uses reportlab as the required renderer for publish-stage closure.
- Optional runtimes and libraries do not gate monthly close completion.
- Every dependency must map to a functional requirement in architecture or workflows.
- Secrets and cloud resource identifiers are loaded by config key and path, never hardcoded.

## Component stack matrix

| id  | component                  | functional requirement focus                     | runtime           | dependencies and libraries                   |
| --- | -------------------------- | ------------------------------------------------ | ----------------- | -------------------------------------------- |
| 01  | bank source files          | provide statement txns by account and period     | windows 11 local  | csv, openpyxl                                |
| 02  | bank pdf archive           | retain statement evidence for lineage and audit  | windows 11 local  | pathlib, mimetypes                           |
| 03  | ibkr activity csv          | provide broker activity and nav source           | windows 11 local  | csv                                          |
| 04  | bill statement pdfs        | retain bill evidence and parsing source          | windows 11 local  | pathlib, mimetypes                           |
| 05  | yahoo finance api          | provide forex rates per required pair            | python 3.12.10    | httpx or requests                            |
| 06  | aws s3 artifact storage    | store publish artifacts and lineage snapshots    | aws s3 external   | boto3                                        |
| 07  | google sheets session ui   | collect inputs checkpoints and review actions    | google sheets ui  | google sheets workbook, named ranges         |
| 07A | gas for sheets ui optional | route selected click events to backend api       | gas optional      | apps script urlfetch service                 |
| 08  | homebudget app             | display ledger and approved write-back outcomes  | desktop app       | homebudget ui runtime                        |
| 09  | cli                        | parallel operator control and automation surface | python 3.12.10    | argparse, typer optional                     |
| 10  | backend api                | expose contracts to ui and cli callers           | python 3.12.10    | flask, pydantic, waitress                    |
| 11  | aws storage adapter        | encapsulate s3 upload and retrieval operations   | python 3.12.10    | boto3                                        |
| 12  | workflow orchestrator      | enforce stage routing and gate policy            | python 3.12.10    | pydantic, enum, datetime                     |
| 13  | account close runtime      | run ingest sync and reconcile flows by account   | python 3.12.10    | pandas, decimal                              |
| 14  | bill and shared runtime    | run bill intake allocation and posting           | python 3.12.10    | pandas, decimal                              |
| 15  | source adapters            | parse normalize and stage source records         | python 3.12.10    | pandas, csv, openpyxl                        |
| 16  | homebudget wrapper adapter | execute hb reads and controlled writes           | python 3.12.10    | homebudget>=2.1.1                            |
| 17  | mapping crud module        | manage mapping lifecycle and gate checks         | python 3.12.10    | sqlite3                                     |
| 18  | sqlite adapter             | provide single sql boundary for all schemas      | python 3.12.10    | sqlite3                                     |
| 18A | google sheets adapter      | execute sheet reads writes and status write-back | python 3.12.10    | google-api-python-client, google-auth        |
| 19  | reconciliation engine      | execute match variance tolerance and adjustment  | python 3.12.10    | decimal, pandas                              |
| 20  | statement builder          | produce income statement and balance sheet       | python 3.12.10    | pandas, decimal, jinja2, reportlab, weasyprint optional |
| 21  | logging module             | emit audit and run diagnostics                   | python 3.12.10    | logging, json                                |
| 22  | error handling module      | classify and propagate typed errors              | python 3.12.10    | pydantic, traceback                          |
| 23  | sqlite app database        | persist app owned schemas and lineage anchors    | sqlite local file | sqlite                                       |

## Workflow stage stack matrix

### Monthly close workflow

| id | stage         | functional requirement focus                                | runtime path                     | dependencies and libraries            |
| -- | ------------- | ----------------------------------------------------------- | -------------------------------- | ------------------------------------- |
| 01 | pre-flight    | validate period, config, and source readiness              | gs ui -> backend api -> sqlite   | google-auth, google-api-python-client, pydantic |
| 02 | forex         | load and validate period fx rates                          | orchestrator -> source adapter   | httpx or requests, decimal            |
| 03 | data download | capture files and gs entries per account                   | user + gs ui + downloads folder  | gs workbook, windows file system      |
| 04 | data ingest   | detect stage and validate source payloads                  | source adapter -> sqlite         | pathlib, csv, openpyxl, sqlite3       |
| 05 | data sync     | normalize records and refresh app-managed schemas          | runtimes -> adapters -> sqlite   | pandas, decimal, homebudget, gsheet   |
| 06 | reconcile     | run method match, variance checks, and write-back          | runtime -> engine -> hb + sqlite | decimal, pandas, homebudget           |
| 07 | statements    | build drafts and run book-level identity checks            | builder -> engine -> gs adapter  | pandas, decimal, google-api-python-client |
| 08 | publish       | generate artifacts, upload, finalize session               | builder -> s3 adapter -> sqlite  | boto3, reportlab, sqlite3             |

### Bill payment workstream

| id | stage            | functional requirement focus                               | runtime path                     | dependencies and libraries        |
| -- | ---------------- | ---------------------------------------------------------- | -------------------------------- | --------------------------------- |
| B1 | bill intake      | parse and stage bill records                               | bill runtime -> source adapters  | pdf parser, csv, openpyxl         |
| B2 | share allocate   | apply split rules and persist settlement rows              | bill runtime -> sqlite           | decimal, pandas                   |
| B3 | post entries     | post close_book and submit approved hb entries             | bill runtime -> hb + sqlite      | homebudget, sqlite3               |
| B4 | workstream close | close parallel workstream with audit visibility            | orchestrator -> sqlite -> gs     | google-api-python-client, logging |

### Mapping maintenance workflow

| id | stage                 | functional requirement focus                                | runtime path                   | dependencies and libraries        |
| -- | --------------------- | ----------------------------------------------------------- | ------------------------------ | --------------------------------- |
| M1 | classification review | identify unmapped categories and account assignments         | gs ui or cli -> mapping module | google-api-python-client, sqlite3 |
| M2 | mapping update        | apply mapping create update delete operations               | api -> mapping module -> sqlite | pydantic, sqlite3                 |
| M3 | gate check            | confirm completeness for workflow entry and progression     | orchestrator -> mapping module | sqlite3, pydantic                 |

## Library register

Required:

| id | library                  | scope                                           | reason                                                                 |
| -- | ------------------------ | ----------------------------------------------- | ---------------------------------------------------------------------- |
| 01 | homebudget               | hb adapter and hb sync workflows                | required by requirements dependencies and hb integration boundaries     |
| 02 | flask                    | backend api contract exposure                   | selected API framework for local-first workflows                       |
| 03 | pydantic                 | request and stage payload contracts             | required for strict typed validation at integration boundaries          |
| 04 | waitress                 | local api host                                  | selected WSGI runtime host for Flask on Windows                        |
| 05 | google-api-python-client | google sheets adapter and sheet ui integration  | required direct Google API contract for sheet read and write operations |
| 06 | google-auth              | google sheets adapter auth and token management | required service account authentication for sheets integration          |
| 07 | sqlite3                  | sqlite adapter and local persistence            | required canonical local storage boundary                              |
| 08 | pandas                   | ingest sync statements                          | required for tabular transform and deterministic stage processing       |
| 09 | decimal                  | reconcile and statement compute                 | required for financial precision and tolerance enforcement              |
| 10 | openpyxl                 | bank and bill excel parse paths                 | required for excel account profiles in data ingest and sync            |
| 11 | boto3                    | publish and archive                             | required for aws storage adapter and artifact upload                   |
| 12 | reportlab                | publish-stage pdf artifact generation           | required renderer for deterministic PDF output in close publish        |

Optional:

| id | library            | scope                               | reason                                                                |
| -- | ------------------ | ----------------------------------- | --------------------------------------------------------------------- |
| 01 | typer              | cli command ergonomics              | recommended for ergonomic cli surface                                 |
| 02 | weasyprint         | pdf generation                      | optional higher-fidelity renderer via same pdf adapter contract       |
| 03 | nodejs and express | guided web workflow extension       | optional extension runtime outside required close-session path        |

## Operational constraints

- Python environment root is env/ for application runtime.
- Design-phase helper scripts may use .dev/env only for temporary inspection tasks.
- All SQLite access is routed through the SQLite adapter boundary.
- SQLite adapter exposes a backend-neutral persistence interface and hides engine-specific details from domain and orchestration modules.
- Persistence contracts must be drop-in replaceable by another SQL adapter, including AWS-managed cloud SQL backends, without caller-facing API changes.
- Google Sheets integration is implemented through a direct Google SDK adapter boundary, not through sqlite-gsheet.
- HomeBudget writes are routed only through the HomeBudget wrapper adapter.
- Google Sheets writes are routed through the Google Sheets adapter, with optional GAS trigger bridge for selected actions.
- PDF generation is required for publish and is satisfied by the reportlab-backed renderer path.
- Workflow reruns require deterministic adapter behavior and idempotent ingest keys.
