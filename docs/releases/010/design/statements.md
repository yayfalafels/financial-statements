---
title: Statements Design
doc_type: design
topic_type: owner
owner: statement-builder
scope: poc
last_updated: 2026-05-16
status: draft
---

# Statements Design

## Table of contents

- [Summary](#summary)
- [Authority](#authority)
- [Design principles](#design-principles)
  - [Layered dependency flow](#layered-dependency-flow)
  - [Stage dispatch ownership](#stage-dispatch-ownership)
  - [Configuration as contract](#configuration-as-contract)
  - [Determinism and idempotency guarantees](#determinism-and-idempotency-guarantees)
- [Component boundary](#component-boundary)
- [SQLite data model contract](#sqlite-data-model-contract)
  - [Two table sets and ownership](#two-table-sets-and-ownership)
  - [Statement builder target outputs](#statement-builder-target-outputs)
  - [Reporting year coverage and forecast](#reporting-year-coverage-and-forecast)
  - [Snapshot and SCD behavior](#snapshot-and-scd-behavior)
  - [Close book schemas and 2026 YTD sample values](#close-book-schemas-and-2026-ytd-sample-values)
- [Audit, reproducibility, and lineage](#audit-reproducibility-and-lineage)
- [Module structure and layered architecture](#module-structure-and-layered-architecture)
  - [Layer responsibilities](#layer-responsibilities)
  - [Data flow example draft build](#data-flow-example-draft-build)
  - [Data flow example finalize publish](#data-flow-example-finalize-publish)
- [Implementation constraints](#implementation-constraints)
- [OOP architecture and module layout](#oop-architecture-and-module-layout)
  - [Class and function applicability principle](#class-and-function-applicability-principle)
  - [Class hierarchy](#class-hierarchy)
  - [Dispatch contract](#dispatch-contract)
  - [Layered module layout](#layered-module-layout)
- [PDF renderer dependency contract](#pdf-renderer-dependency-contract)
- [Stage invocation and data contracts](#stage-invocation-and-data-contracts)
  - [Statements draft build contract](#statements-draft-build-contract)
  - [Statements finalize publish contract](#statements-finalize-publish-contract)
- [Statement layout config contract](#statement-layout-config-contract)
  - [Config format example](#config-format-example)
  - [Config interpretation pipeline](#config-interpretation-pipeline)
- [Aggregation and validation contract](#aggregation-and-validation-contract)
  - [Forex implementation contract](#forex-implementation-contract)
- [Lifecycle state model](#lifecycle-state-model)
- [Publish contract and artifact rules](#publish-contract-and-artifact-rules)

## Summary

This document defines the design contract for statements draft build and finalize publish behavior in the close workflow. The contract covers module ownership, class hierarchy, invocation payloads, statement layout configuration, aggregation logic, lifecycle guards, publish artifacts, lineage rules, and reporting-year consolidation policy.

The statement builder reads reconciled actual aggregates from close_book and forecast inputs from the forecast UI adapter, consolidates both into one reporting-year snapshot, composes draft income statement and balance sheet outputs, enforces book identity checks, and coordinates publish through the AWS storage adapter after review confirmation.

## Authority

This document is the authoritative design source for statement builder and publish runtime behavior in release 010 scope.

## Design principles

The statements runtime is governed by four design principles to ensure implementation clarity and deterministic publish behavior.

### Layered dependency flow

Statements runtime is structured as a layered, acyclic dependency hierarchy.

```text
Layer 6: orchestration and stage handlers
  ↓
Layer 5: services and lifecycle orchestration
  ↓
Layer 4: layout and aggregation engines
  ↓
Layer 3: config compiler and validators
  ↓
Layer 2: shared adapters and renderer gateways
  ↓
Layer 1: models and contracts
```

Key invariants:

- models contain data contracts only and no adapter calls.
- aggregation and forex functions are pure and Decimal-only.
- services coordinate dependencies but do not embed formula constants.
- adapters perform I O only and do not decide lifecycle transitions.
- orchestration routes stage keys and never performs statement math.

### Stage dispatch ownership

Stage routing is owned by the statements orchestration layer, not by callers.

Dispatch protocol:

```text
Caller requests: router.run_stage(stage_key, payload)
  ↓
Router resolves stage handler from registry
  ↓
DraftBuildHandler or FinalizePublishHandler validates payload
  ↓
Handler invokes service and returns typed result
```

Routing contract:

- stage key `statements` maps to draft build only.
- stage key `publish` maps to finalize and publish only.
- unsupported key is fail closed with explicit error.

### Configuration as contract

Config is executable policy, not optional metadata. Runtime behavior for layout, mapping, formula evaluation, and render hints is resolved from `statement_config.json`.

Resolution order:

1. load raw json snapshot by `config_snapshot_id`.
2. validate schema and required sections.
3. compile deterministic lookup plan.
4. execute aggregation and formula resolution using compiled plan.

Configuration safety guard:

- config snapshot is frozen per build request.
- publish must reference the same config snapshot as the reviewed draft.
- config changes after draft creation require rebuild before finalize.

### Determinism and idempotency guarantees

Statements must be byte-stable for same inputs and same renderer.

Determinism controls:

- line and section order come only from config order keys.
- all monetary values use Decimal and fixed quantization.
- formula evaluator uses a stable expression grammar and ordered resolution.
- artifact naming uses deterministic period and version path rules.

Idempotency controls:

- same idempotency key and same payload returns stored result.
- same idempotency key and different payload is blocked as conflict.
- rerun with same close_book snapshot and config snapshot reproduces same statement bundle.

## Component boundary

| id | component             | owns                                      | does not own                    |
| -- | --------------------- | ----------------------------------------- | ------------------------------- |
| 01 | workflow orchestrator | stage routing, gates, transitions         | statement math, artifact upload |
| 02 | statement builder     | draft build and finalize publish          | ingest logic, reconcile methods |
| 03 | reconciliation engine | book identity checks, reconcile contracts | statement assembly              |
| 04 | sqlite adapter        | close_book reads, draft-final writes      | aggregation rules               |
| 05 | google sheets adapter | review read, draft-publish writes         | lifecycle guard decisions       |
| 06 | forecast UI adapter   | forecast worksheet reads and normalization | statement assembly              |
| 07 | aws storage adapter   | artifact naming, upload, metadata echo    | PDF composition, session close  |

Boundary rules:

- actuals are read from close_book and forecast is read via forecast UI adapter.
- statement consolidation writes reporting-year outputs to close_book.
- Publish starts only after draft build success and review confirmation.
- Statement builder never calls source adapters used by ingest stages.
- S3 SDK calls are isolated to the AWS storage adapter boundary.

## SQLite data model contract

### Two table sets and ownership

The statements path depends on two distinct SQLite table sets with different grain and ownership.

| id | table_set                 | schema set            | grain                    | currency basis         |
| -- | ------------------------- | --------------------- | ------------------------ | ---------------------- |
| 01 | detail transaction set    | normalized and source | transaction row          | base account currency  |
| 02 | period account agg set    | close_book and forecast| account and period month | base plus reporting SGD |

Ownership rule:

- ingest and reconcile own detail transaction schemas and account-period actual aggregates.
- forecast runtime owns forecast topic tables and forecast account-month aggregates.
- statement builder consumes aggregate schemas and does not recompute transaction-level normalization.

### Statement builder target outputs

The primary statement-builder data output is period-account aggregates used for statement assembly.

| id | output_table                          | basis                 | role                          |
| -- | ------------------------------------- | --------------------- | ----------------------------- |
| 01 | close_book.forex_account_monthly      | base and reporting    | monthly account rollup input  |
| 02 | close_book.forex_account_monthly_snapshot | reporting snapshot | SCD history for monthly rollup |
| 03 | close_book.forecast_statement_yearly  | base and reporting    | reporting-year statement rows |

Output rule:

- statements draft build reads the monthly aggregate set and emits reporting-year statement rows.
- finalize publish reads reviewed statement rows and writes immutable publish artifacts.

### Reporting year coverage and forecast

A complete statement is reporting-year scoped and month-complete from January to December.

Month source rule:

- months up to current month use reconciled actuals.
- months after current month use forecast tables.
- both account-currency and reporting-currency rows are required.

Forecast integration rule:

- forecast runtime persists `forecast.forecast_account_monthly` and topic tables.
- statements draft build joins actual and forecast month rows into one reporting-year statement set.
- forex translation is applied to forecast account-currency rows before reporting-currency statement rows.

### Snapshot and SCD behavior

Statement snapshot behavior follows reporting period state rules.

| id | period_state     | update behavior                         | snapshot behavior               |
| -- | ---------------- | --------------------------------------- | ------------------------------- |
| 01 | historical year  | immutable except controlled restatement | append new version on restate   |
| 02 | current year     | rerun allowed for open months           | append snapshot each rerun      |
| 03 | future year      | rerun allowed for planning updates      | append snapshot each rerun      |

SCD contract:

- snapshot keys are deterministic and version-monotonic per natural key.
- `statement_timestamp_at` is the statement snapshot timestamp anchor for reporting-year rows.
- historical year snapshots are preserved as immutable audit history.

### Close book schemas and 2026 YTD sample values

This section defines the close-book read models used by statement builder key processes and anchors each with 2026 YTD samples.

#### 1. Source input: reconciled transaction level

Target close-book design contract for reconciled transaction rows:

| id | field               | type      | sample_2026_ytd    |
| -- | ------------------- | --------- | ------------------ |
| 01 | txn_id              | text      | hb_20260206_0001   |
| 02 | period_key          | text      | 2026-02            |
| 03 | txn_date            | text      | 2026-02-06         |
| 04 | account_id          | text      | acct_dbs_multi_sgd |
| 05 | account_name        | text      | TWH DBS Multi SGD  |
| 06 | account_type        | text      | cash               |
| 07 | txn_class           | text      | transfer_out       |
| 08 | amount_base         | numeric   | -228.15            |
| 09 | base_currency       | text      | SGD                |
| 10 | gl_code             | text      | rental             |
| 11 | category_group_key  | text      | rental             |
| 12 | source_system       | text      | homebudget_sync    |
| 13 | source_record_ref   | text      | hb_gl:2026-02-06:1 |
| 14 | reconcile_session_id| text      | rcn_2026_02_004    |

Sample 2026 YTD mapped records used by reconciliation output:

| id | period_key | txn_date   | account_name      | txn_class     | amount_reporting | gl_code     |
| -- | ---------- | ---------- | ----------------- | ------------- | ---------------- | ----------- |
| 01 | 2026-01    | 2026-01-03 | TWH - Personal    | expense       | -1200.00         | rental      |
| 02 | 2026-01    | 2026-01-03 | TWH DBS Multi SGD | transfer_out  | -1200.00         |             |
| 03 | 2026-01    | 2026-01-15 | TWH DBS Multi SGD | income        | 7400.00          | salary      |
| 04 | 2026-02    | 2026-02-05 | TWH - Personal    | expense       | -1250.00         | rental      |
| 05 | 2026-02    | 2026-02-10 | TWH DBS Multi SGD | income        | 350.00           | dividends   |

#### 2. Forecasts

The authoritative forecast schema design is defined in [docs/releases/010/design/forecast.md](docs/releases/010/design/forecast.md#L106). Target design contract schemas:

**forecast.forecast_account_monthly** account aggregate with denormalized flows:

| id | column                | type    | description                          |
| -- | --------------------- | ------- | ------------------------------------ |
| 01 | reporting_year        | integer | forecast reporting year              |
| 02 | period_month          | text    | YYYY-MM                              |
| 03 | account_id            | text    | account identifier                   |
| 04 | account_currency      | text    | account currency code                |
| 05 | opening_balance       | numeric | opening balance in account ccy       |
| 06 | income_amount         | numeric | sum of forecast income flows         |
| 07 | expense_amount        | numeric | sum of forecast expense flows        |
| 08 | transfer_amount       | numeric | explicit plus implied transfers      |
| 09 | return_amount         | numeric | projected return flow for earning accounts |
| 10 | net_trade_amount      | numeric | projected IBKR net trade flow        |
| 11 | tax_liability_amount  | numeric | projected tax liability (settlement) |
| 12 | closing_balance       | numeric | forecast closing balance             |
| 13 | period_state          | text    | historical, current, future          |
| 14 | run_id                | text    | forecast run lineage id              |

**Denormalization and flow semantics:**

The `forecast.forecast_account_monthly` table stores aggregated flows (`income_amount`, `expense_amount`, `transfer_amount`, `return_amount`, `net_trade_amount`, `tax_liability_amount`) that are mathematically derivable from topic tables. This denormalization trades storage and sync maintenance for query simplicity: statements draft build can load one account-month row instead of joining six topic tables. The closing balance identity is: `closing_balance = opening_balance + income_amount - expense_amount + transfer_amount + return_amount + net_trade_amount`. Flow semantics: income and expense flows are aggregates across all categories (e.g., total salary + investment income; total personal + investment expenses); transfers are net settlement flows; return and trade flows apply only to earning and investment accounts. The forecast runtime must ensure aggregate fields remain synchronized with source topics; any inconsistency is a data integrity error.

Sample 2026 YTD forecast account-month aggregate values.

cash accounts:

| id | period_month | account_id        | opening_balance | income_amount | expense_amount | transfer_amount | closing_balance |
| -- | ------------ | ----------------- | --------------- | ------------- | -------------- | --------------- | --------------- |
| 01 | 2026-06      | acct_wallet_sgd   | 1500.00         | 0.00          | 0.00           | 139.00          | 1639.00         |
| 02 | 2026-07      | acct_wallet_sgd   | 1639.00         | 0.00          | 0.00           | 0.00            | 1639.00         |
| 03 | 2026-06      | acct_citi_sgd     | 500.00          | 0.00          | 0.00           | 104.00          | 604.00          |
| 04 | 2026-07      | acct_citi_sgd     | 604.00          | 0.00          | 0.00           | 0.00            | 604.00          |
| 05 | 2026-06      | acct_amazon_usd   | 15.00           | 0.00          | 0.00           | 3.00            | 18.00           |
| 06 | 2026-06      | acct_wf_usd       | 35.00           | 0.00          | 0.00           | 15.00           | 50.00           |

income and expenses



#### 3. Period aggregates reporting year in base currency

Target design contract is account-month base-basis rows consumed by statement builder from `close_book.forex_account_monthly`.

| id | field                  | type    | meaning                          |
| -- | ---------------------- | ------- | -------------------------------- |
| 01 | reporting_year         | integer | reporting year                   |
| 02 | period_month           | text    | YYYY-MM                          |
| 03 | account_id             | text    | account identifier               |
| 04 | account_currency       | text    | native currency code             |
| 05 | beginning_balance_native | numeric | opening base balance           |
| 06 | net_txn_native         | numeric | period net flow in base ccy      |
| 07 | ending_balance_native  | numeric | closing base balance             |
| 08 | snapshot_state         | text    | historical, current, forecast    |
| 09 | run_id                 | text    | lineage id for aggregate run     |

Mapping note:

- Current CSV evidence is alias-balance snapshots.
- `account_id` and other derived columns are assigned during adapter normalization.

Sample 2026 YTD mapped base-currency values from `data/monthly-closing/account-balances.csv`:

| id | period_month | account_alias    | account_currency | ending_balance_native |
| -- | ------------ | ---------------- | ---------------- | --------------------- |
| 01 | 2026-01      | TWH AMAZON USD   | USD              | 38.50                 |
| 02 | 2026-02      | TWH AMAZON USD   | USD              | 18.29                 |
| 03 | 2026-01      | TWH CASH USD     | USD              | 301.08                |
| 04 | 2026-02      | TWH CASH USD     | USD              | 901.08                |
| 05 | 2026-01      | TWH CASH SGD     | SGD              | 787.45                |
| 06 | 2026-02      | TWH CASH SGD     | SGD              | 1806.45               |

#### 4. Period aggregates reporting year in reporting currency

Target design contract is reporting-basis account-month rows read from `close_book.forex_account_monthly`.

| id | field                    | type    | meaning                          |
| -- | ------------------------ | ------- | -------------------------------- |
| 01 | reporting_year           | integer | reporting year                   |
| 02 | period_month             | text    | YYYY-MM                          |
| 03 | account_id               | text    | account identifier               |
| 04 | reporting_currency       | text    | reporting currency, default SGD  |
| 05 | fx_rate_month_end        | numeric | month-end fx rate                |
| 06 | net_txn_reporting        | numeric | period net flow in reporting ccy |
| 07 | ending_balance_reporting | numeric | closing balance in reporting ccy |
| 08 | fx_m2m_reporting         | numeric | forex mark-to-market             |
| 09 | snapshot_state           | text    | historical, current, forecast    |

Mapping note:

- Current CSV evidence is statement-line reporting outputs, not account_id-grain close_book rows.
- Account-grain reporting rows are produced in close_book; statement-line values below are downstream rollups.

Sample 2026 YTD reporting-currency values from `data/financial-statements-reconcile/income_statement.csv`:

| id | period_month | statement_line | reporting_currency | amount_reporting |
| -- | ------------ | -------------- | ------------------ | ---------------- |
| 01 | 2026-01      | net income PL  | SGD                | 14694            |
| 02 | 2026-02      | net income PL  | SGD                | -33947           |
| 03 | 2026-03      | net income PL  | SGD                | -20788           |
| 04 | 2026-01      | investments PL | SGD                | 20852            |
| 05 | 2026-02      | investments PL | SGD                | -46450           |
| 06 | 2026-01      | M2M forex USD.SGD | SGD             | -5096            |

Read-model mapping for statements runtime:

- `ctx.actual_rows` is loaded by `StatementRepository.load_close_book_yearly` from close_book aggregate tables.
- Forex line resolution filters the actual-row read model for FX accounts and uses `ccy_pair` per row.
- `ctx.consolidated_rows` merges actual and forecast rows keyed by reporting year, period month, account, and basis type.

## Audit, reproducibility, and lineage

Every build and publish event must include lineage anchors.

| id | field                  | scope         | purpose                    |
| -- | ---------------------- | ------------- | -------------------------- |
| 01 | period_key             | build publish | period identity            |
| 02 | close_book_snapshot_id | build publish | aggregate source anchor    |
| 03 | config_snapshot_id     | build publish | config freeze anchor       |
| 04 | reconcile_session_refs | build publish | identity and gate lineage  |
| 05 | statement_bundle_ref   | build publish | draft to final continuity  |
| 06 | period_version_id      | publish       | immutable version key      |
| 07 | artifact_manifest      | publish       | storage evidence set       |
| 08 | session_close_ref      | publish       | append only close evidence |

Rerun reproducibility contract:

- Same period key, snapshot ids, config version, and renderer key must produce identical statement data.
- Repeated publish request with same idempotency key must be side effect free.
- Session close record is append only and never updated in place.

## Module structure and layered architecture

This section defines where implementation logic must live so the codebase remains testable and unambiguous during code-complete handoff.

### Layer responsibilities

| id | layer         | owns                                    | does not own                 |
| -- | ------------- | --------------------------------------- | ---------------------------- |
| 01 | models        | request, result, artifact contracts     | I O and formula execution    |
| 02 | adapters      | sqlite, storage, renderer, forecast UI  | lifecycle decisions          |
| 03 | config        | load, validate, compile plan            | statement arithmetic         |
| 04 | layout agg    | line resolution, rollups, blend inputs  | stage routing                |
| 05 | services      | build, publish, reopen, year consolidate| direct source adapter ingest |
| 06 | orchestration | stage dispatch and payload routing      | formula and forex math       |

Reference service boundary snippet:

```python
class StatementAssembler:
    def __init__(self, resolver: LayoutResolver, forex_fn, formula_engine):
        self.resolver = resolver
        self.forex_fn = forex_fn
        self.formula_engine = formula_engine

    def assemble(self, ctx: StatementContext) -> "StatementBundle":
    income_sections = self.resolver.resolve("income_statement", ctx.consolidated_rows)
    balance_sections = self.resolver.resolve("balance_sheet", ctx.consolidated_rows)
        forex_m2m = self.forex_fn(ctx)
        return self.formula_engine.finalize_bundle(income_sections, balance_sections, forex_m2m)


def consolidate_actual_and_forecast(
  actual_rows: list[dict],
  forecast_rows: list[dict],
  current_month: str,
) -> list[dict]:
  merged: dict[tuple[str, str, str], dict] = {}
  for row in actual_rows:
    key = (row["reporting_year"], row["period_month"], row["account_id"])
    merged[key] = row
  for row in forecast_rows:
    if row["period_month"] > current_month:
      key = (row["reporting_year"], row["period_month"], row["account_id"])
      merged[key] = row
  return [merged[k] for k in sorted(merged.keys())]
```

### Data flow example draft build

```text
Input:
  period_key=2026-02
  reporting_year=2026
  close_book_snapshot_id=cbk_2026_02_v004
  forecast_ui_snapshot_ref=gs_fc_2026_02_v012
  config_snapshot_id=stcfg_1_3_0
  idempotency_key=draft_build_2026_02_a1

Step 1: DraftBuildHandler validates request and calls BuildStatementsService.run
Step 2: Config loader validates and compiles layout plan
Step 3: SQLite gateway loads close_book snapshot actual rows for reporting year
Step 4: Forecast UI adapter loads forecast rows from Google Sheets snapshot
Step 5: Consolidation service merges actual and forecast month rows
Step 6: Layout resolver builds ordered sections and line values
Step 7: Forex function computes forex_m2m with Decimal rates
Step 8: Formula engine derives totals and identity lines
Step 9: Identity validator checks net income and net worth rules
Step 10: Repository writes draft bundle and yearly snapshot ref

Output:
  stage_status=draft_ready
  lifecycle_state=draft
  statement_bundle_ref=stb_2026_02_draft_v001
  statement_yearly_snapshot_ref=sty_2026_v009
  identity_check_status=pass
```

### Data flow example finalize publish

```text
Input:
  period_key=2026-02
  statement_bundle_ref=stb_2026_02_draft_v001
  review_checkpoint_ref=rvw_2026_02_004
  idempotency_key=finalize_publish_2026_02_a1
  publish_confirmed=true

Step 1: FinalizePublishHandler validates request and calls PublishStatementsService.run
Step 2: Service checks idempotency replay store
Step 3: Lifecycle controller enforces reviewed to finalized transition
Step 4: Version allocator issues next period_version_id
Step 5: Renderer gateway generates income and balance PDFs
Step 6: Storage gateway uploads PDFs and manifest using deterministic keys
Step 7: SQLite gateway writes finalize record and session_close_ref
Step 8: Service persists idempotency result for replay-safe response

Output:
  stage_status=finalized
  lifecycle_state=finalized
  period_version_id=2026-02-v003
  artifact_manifest=[income_pdf, balance_pdf, publish_manifest]
  session_close_ref=close_2026_02_003
```

## Implementation constraints

| id | constraint              | contract                                              |
| -- | ----------------------- | ----------------------------------------------------- |
| 01 | Decimal arithmetic      | all monetary math uses Decimal, no float arithmetic   |
| 02 | deterministic ordering  | section and line order resolved only from config      |
| 03 | idempotent writes       | publish and close writes are replay safe              |
| 04 | fail closed validation  | blocking gates stop progression on any contract break |
| 05 | config driven behavior  | no hard coded routing or formula definitions          |

## OOP architecture and module layout

### Class and function applicability principle

Use class only when behavior needs injected dependencies, invariants, or lifecycle state.

Use function for pure deterministic transforms with no external dependency.

Decision rule by scope:

| id | scope               | shape    | reason                              |
| -- | ------------------- | -------- | ----------------------------------- |
| 01 | stage orchestration | class    | dependency wiring and gate state    |
| 02 | config loading      | class    | validation policy and cache         |
| 03 | layout resolution   | class    | compiled plan and lookup indexes    |
| 04 | forex revaluation   | function | pure Decimal math on given inputs   |
| 05 | line aggregation    | function | pure grouping and deterministic sum |
| 06 | lifecycle control   | class    | transition guards and audit writes  |
| 07 | publish runtime     | class    | adapter calls and idempotency check |
| 08 | forecast loading    | class    | adapter boundary and schema checks  |
| 09 | year consolidation  | class    | actual and forecast month merge     |

Versioning policy:

- statement versioning is a data concern, not a subtype concern.
- `period_version_id` is allocated by publish runtime from persisted period history.
- behavior variants are selected by config version and feature flags, not class inheritance.

### Class hierarchy

Statement runtime uses composition with explicit services. Inheritance is limited to boundary interfaces and is not used for period versioning.

```python
from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

@dataclass(frozen=True)
class StatementBuildRequest:
    period_key: str
  reporting_year: int
    close_book_snapshot_id: str
  forecast_ui_snapshot_ref: str
    config_snapshot_id: str
    idempotency_key: str
    command_mode: str

@dataclass(frozen=True)
class StatementContext:
    period_key: str
    config: "StatementConfig"
  actual_rows: list[dict]
  forecast_rows: list[dict]
  consolidated_rows: list[dict]

class StatementRepository(Protocol):
  def load_close_book_yearly(self, reporting_year: int, snapshot_id: str) -> list[dict]: ...
    def write_draft_bundle(self, bundle: "StatementBundle") -> str: ...

class ForecastUiAdapter(Protocol):
  def load_forecast_rows(self, reporting_year: int, snapshot_ref: str) -> list[dict]: ...

class BuildStatementsService:
    def __init__(
        self,
        repo: StatementRepository,
        forecast_reader: ForecastUiAdapter,
        blender: "ForecastBlendService",
        config_loader: "StatementConfigLoader",
        layout_resolver: "LayoutResolver",
        validator: "IdentityValidator",
    ):
        self.repo = repo
        self.forecast_reader = forecast_reader
        self.blender = blender
        self.config_loader = config_loader
        self.layout_resolver = layout_resolver
        self.validator = validator

    def run(self, request: StatementBuildRequest) -> "StatementBuildResult":
        config = self.config_loader.load(request.config_snapshot_id, request.period_key)
      actual_rows = self.repo.load_close_book_yearly(
        request.reporting_year,
        request.close_book_snapshot_id,
      )
      forecast_rows = self.forecast_reader.load_forecast_rows(
        request.reporting_year,
        request.forecast_ui_snapshot_ref,
      )
      consolidated_rows = self.blender.merge(
        request.period_key,
        actual_rows,
        forecast_rows,
      )
      ctx = StatementContext(
        request.period_key,
        config,
        actual_rows,
        forecast_rows,
        consolidated_rows,
      )
        bundle = StatementAssembler(self.layout_resolver).assemble(ctx)
        self.validator.assert_identity(bundle)
        bundle_ref = self.repo.write_draft_bundle(bundle)
        return StatementBuildResult.draft_ready(bundle_ref=bundle_ref)
```

Adapter contracts use interface inheritance because backends are interchangeable.

```python
class PdfRenderer(Protocol):
    def render(self, bundle: "StatementBundle", render_hints: dict) -> bytes: ...

class ReportLabRenderer:
    def render(self, bundle: "StatementBundle", render_hints: dict) -> bytes:
        ...

class WeasyPrintRenderer:
    def render(self, bundle: "StatementBundle", render_hints: dict) -> bytes:
        ...
```

Config version behavior is policy selected, not subclass selected.

```python
class RulePolicySelector:
    def select(self, config: "StatementConfig") -> "RulePolicy":
        if config.config_version.startswith("1."):
            return RulePolicyV1()
        return RulePolicyDefault()
```

### Dispatch contract

Dispatch is a registry of stage handlers with shared runtime context.

```python
from typing import Protocol

class StageHandler(Protocol):
    stage_key: str
    def run(self, payload: dict, ctx: "RuntimeContext") -> dict: ...

class StatementStageRouter:
    def __init__(self, handlers: list[StageHandler], ctx: "RuntimeContext"):
        self._by_key = {h.stage_key: h for h in handlers}
        self._ctx = ctx

    def run_stage(self, stage_key: str, payload: dict) -> dict:
        handler = self._by_key.get(stage_key)
        if handler is None:
            raise ValueError(f"unsupported_stage:{stage_key}")
        return handler.run(payload, self._ctx)
```

Each stage has a cohesive handler class with scoped dependencies.

```python
class DraftBuildHandler:
    stage_key = "statements"

    def __init__(self, service: BuildStatementsService):
        self.service = service

    def run(self, payload: dict, ctx: "RuntimeContext") -> dict:
        request = StatementBuildRequest(**payload)
        return self.service.run(request).to_dict()

class FinalizePublishHandler:
    stage_key = "publish"

    def __init__(self, service: "PublishStatementsService"):
        self.service = service

    def run(self, payload: dict, ctx: "RuntimeContext") -> dict:
        request = StatementPublishRequest(**payload)
        return self.service.run(request).to_dict()
```

Functions are still preferred for stateless transforms.

```python
def normalize_stage_key(raw_key: str) -> str:
    return raw_key.strip().lower()
```

### Layered module layout

Layered structure is expanded by runtime scope.

```text
src/python/monthly_close/statements/
  models/
    contracts.py
    lifecycle.py
    artifacts.py
    config_schema.py
  config/
    loader.py
    validator.py
    compiler.py
  aggregation/
    consolidate.py
    groupby_rollup.py
    formulas.py
    forex.py
  layout/
    resolver.py
    line_planner.py
  services/
    build_service.py
    forecast_load_service.py
    year_snapshot_service.py
    publish_service.py
    reopen_service.py
  lifecycle/
    controller.py
    transitions.py
  publish/
    artifact_namer.py
    manifest_builder.py
    version_allocator.py
  adapters/
    forecast_ui_gateway.py
    sqlite_gateway.py
    sheets_gateway.py
    storage_gateway.py
    renderer_gateway.py
  orchestration/
    stage_handlers.py
    router.py
```

Layer dependency rule is acyclic. Orchestration depends on services. Services depend on layout, aggregation, lifecycle, and adapters. Pure math modules depend on models only.

## PDF renderer dependency contract

Renderer policy aligns with design guidelines.

| id | renderer   | role                               | status   |
| -- | ---------- | ---------------------------------- | -------- |
| 01 | reportlab  | required publish renderer          | required |
| 02 | weasyprint | optional renderer behind same API  | optional |

Dependency contract:

- renderer selection is config driven through `renderer_key`.
- publish closure requires successful PDF generation before upload.
- rendered output for identical inputs must be byte stable per renderer.

## Stage invocation and data contracts

### Statements draft build contract

Draft build creates reviewable statements and blocks publish until review confirmation.

Request fields:

| id | field                   | type    | required | notes                      |
| -- | ----------------------- | ------- | -------- | -------------------------- |
| 01 | period_key              | str     | yes      | format YYYY-MM             |
| 02 | reporting_year          | int     | yes      | target calendar year       |
| 03 | close_book_snapshot_id  | str     | yes      | actual snapshot anchor     |
| 04 | forecast_ui_snapshot_ref| str     | yes      | forecast UI read anchor    |
| 05 | config_snapshot_id      | str     | yes      | frozen config for reruns   |
| 06 | idempotency_key         | str     | yes      | deterministic replay key   |
| 07 | command_mode            | str     | no       | `validate_only` or execute |

Response fields:

| id | field                    | type   | meaning                          |
| -- | ------------------------ | ------ | -------------------------------- |
| 01 | stage_status             | str    | draft_ready or blocked           |
| 02 | lifecycle_state          | str    | draft                            |
| 03 | statement_bundle_ref     | str    | reference for review and publish |
| 04 | statement_yearly_snapshot_ref | str | reporting-year consolidated set |
| 05 | identity_check_status    | str    | pass or fail                     |
| 06 | blocking_items           | list   | validation blockers if any       |

Blocking conditions:

- close_book records missing for period scope.
- required mapping coverage incomplete.
- book identity check fails.
- forecast inputs incomplete for reporting year build.

### Statements finalize publish contract

Finalize publish finalizes reviewed drafts and writes publish artifacts.

Request fields:

| id | field                  | type | required | notes                           |
| -- | ---------------------- | ---- | -------- | ------------------------------- |
| 01 | period_key             | str  | yes      | period under publish            |
| 02 | statement_bundle_ref   | str  | yes      | reviewed draft identity         |
| 03 | review_checkpoint_ref  | str  | yes      | confirmed review record         |
| 04 | idempotency_key        | str  | yes      | publish replay control          |
| 05 | publish_confirmed      | bool | yes      | user action from GS UI          |
| 06 | reopen_reason          | str  | no       | required for reopen re-finalize |

Response fields:

| id | field             | type | meaning                              |
| -- | ----------------- | ---- | ------------------------------------ |
| 01 | stage_status      | str  | finalized or blocked                 |
| 02 | lifecycle_state   | str  | finalized                            |
| 03 | period_version_id | str  | monotonic version id for period      |
| 04 | artifact_manifest | list | artifact records with storage paths  |
| 05 | session_close_ref | str  | append only audit record key         |

Blocking conditions:

- missing review checkpoint confirmation.
- PDF generation failure.
- S3 upload failure.
- session close record commit failure.

## Statement layout config contract

`statement_config.json` is the design source for section and line ordering.

Top level schema:

| id | key                  | type | required | notes                        |
| -- | -------------------- | ---- | -------- | ---------------------------- |
| 01 | config_version       | str  | yes      | semantic version             |
| 02 | effective_from       | str  | yes      | period key lower bound       |
| 03 | statement_types      | list | yes      | income_statement and balance_sheet |
| 04 | mapping_rules        | obj  | yes      | gl and account routing       |
| 05 | derivation_rules     | obj  | yes      | totals and computed lines    |
| 06 | validation_rules     | obj  | yes      | fail closed controls         |
| 07 | render_hints         | obj  | no       | display hints only           |

Statement type block:

| id | key            | type | required | notes                         |
| -- | -------------- | ---- | -------- | ----------------------------- |
| 01 | statement_key  | str  | yes      | income_statement or balance_sheet |
| 02 | section_order  | list | yes      | deterministic top to bottom   |
| 03 | sections       | list | yes      | section definitions           |

Section block:

| id | key              | type | required | notes                         |
| -- | ---------------- | ---- | -------- | ----------------------------- |
| 01 | section_key      | str  | yes      | stable section id             |
| 02 | section_type     | str  | yes      | detail or total or info       |
| 03 | line_order       | list | yes      | deterministic line order      |
| 04 | lines            | list | yes      | line objects                  |

Line block:

| id | key                 | type | required | notes                         |
| -- | ------------------- | ---- | -------- | ----------------------------- |
| 01 | line_key            | str  | yes      | stable line id                |
| 02 | display_name        | str  | yes      | user facing label             |
| 03 | source_filter       | obj  | yes      | mapping selector              |
| 04 | formula             | str  | no       | for derived lines only        |
| 05 | informational_only  | bool | no       | true for non P and L lines    |
| 06 | source_scope        | str  | no       | actual or forecast or blended |

Version rule:

- Any section order, mapping, or formula semantics change requires `config_version` increment.

### Config format example

The runtime accepts a single canonical JSON document for both statement types.

```json
{
  "config_version": "1.3.0",
  "effective_from": "2026-01",
  "statement_types": [
    {
      "statement_key": "income_statement",
      "section_order": ["income", "expense", "net_income"],
      "sections": [
        {
          "section_key": "income",
          "section_type": "detail",
          "line_order": ["personal_income", "investments_pl"],
          "lines": [
            {
              "line_key": "personal_income",
              "display_name": "personal income",
              "source_filter": {"category_groups": ["personal_income"]}
            },
            {
              "line_key": "investments_pl",
              "display_name": "investments PL",
              "source_filter": {"category_groups": ["investments_pl"]}
            }
          ]
        },
        {
          "section_key": "net_income",
          "section_type": "total",
          "line_order": ["net_income_total"],
          "lines": [
            {
              "line_key": "net_income_total",
              "display_name": "Net income",
              "formula": "sum(section:income) - sum(section:expense) + line:forex_m2m"
            }
          ]
        }
      ]
    }
  ],
  "mapping_rules": {
    "balance_sheet_group": {
      "asset_cash_bank": ["TWH DBS Multi SGD", "TWH UOB One SGD"]
    }
  },
  "derivation_rules": {
    "forex_m2m": {
      "base_ccy": "SGD",
      "rate_source": "period_end_rates",
      "include_accounts": ["Cash TWH USD"]
    }
  },
  "validation_rules": {
    "require_full_mapping": true,
    "identity_tolerance": "0.00"
  },
  "render_hints": {
    "decimal_places": 2,
    "show_zero_lines": false
  }
}
```

### Config interpretation pipeline

Config is interpreted in four deterministic steps.

| id | step      | input          | output              |
| -- | --------- | -------------- | ------------------- |
| 01 | validate  | raw json       | typed config model  |
| 02 | compile   | typed model    | layout plan indexes |
| 03 | resolve   | plan and rows  | ordered line values |
| 04 | derive    | line values    | total and formula lines |

Validation and typing are strict and fail closed.

```python
from pydantic import BaseModel, Field

class LineConfig(BaseModel):
    line_key: str
    display_name: str
    source_filter: dict | None = None
    formula: str | None = None
    informational_only: bool = False
  source_scope: str = "blended"

class SectionConfig(BaseModel):
    section_key: str
    section_type: str
    line_order: list[str]
    lines: list[LineConfig]

class StatementTypeConfig(BaseModel):
    statement_key: str
    section_order: list[str]
    sections: list[SectionConfig]

class StatementConfig(BaseModel):
    config_version: str
    effective_from: str
    statement_types: list[StatementTypeConfig]
    mapping_rules: dict = Field(default_factory=dict)
    derivation_rules: dict = Field(default_factory=dict)
    validation_rules: dict = Field(default_factory=dict)
    render_hints: dict = Field(default_factory=dict)
```

Compilation creates lookup maps so runtime does not scan config repeatedly.

```python
@dataclass(frozen=True)
class CompiledLayoutPlan:
    section_order_by_statement: dict[str, list[str]]
    line_order_by_section: dict[tuple[str, str], list[str]]
    line_by_key: dict[tuple[str, str], LineConfig]

def compile_layout_plan(config: StatementConfig) -> CompiledLayoutPlan:
    section_order_by_statement: dict[str, list[str]] = {}
    line_order_by_section: dict[tuple[str, str], list[str]] = {}
    line_by_key: dict[tuple[str, str], LineConfig] = {}

    for st in config.statement_types:
        section_order_by_statement[st.statement_key] = list(st.section_order)
        for sec in st.sections:
            line_order_by_section[(st.statement_key, sec.section_key)] = list(sec.line_order)
            for line in sec.lines:
                line_by_key[(st.statement_key, line.line_key)] = line

    return CompiledLayoutPlan(section_order_by_statement, line_order_by_section, line_by_key)
```

Resolver interprets config using deterministic ordering only from `section_order` and `line_order`.

```python
class LayoutResolver:
    def __init__(self, plan: CompiledLayoutPlan):
        self.plan = plan

    def resolve(self, statement_key: str, rows: list[dict]) -> list["ResolvedSection"]:
        resolved_sections: list[ResolvedSection] = []
        for section_key in self.plan.section_order_by_statement[statement_key]:
            line_values = []
            for line_key in self.plan.line_order_by_section[(statement_key, section_key)]:
                cfg = self.plan.line_by_key[(statement_key, line_key)]
                line_values.append(resolve_line_value(cfg, rows))
            resolved_sections.append(ResolvedSection(section_key, line_values))
        return resolved_sections
```

## Aggregation and validation contract

Income statement aggregation:

- Expense lines roll up by `gl_code` and category group routing.
- Income lines roll up by income type routing.
- Investment lines roll up by investment classification keys.
- Forex M2M on balances is derived at statement layer.
- Transfer class entries are excluded from income effect.

Actual and forecast consolidation:

- Actual account-month rows are used from January through current month.
- Forecast account-month rows are used from month after current month through December.
- Consolidation key is `reporting_year + period_month + account_id + basis_type`.
- Consolidated rows are persisted as one reporting-year snapshot before layout resolution.

```python
class ForecastBlendService:
  def merge(
    self,
    period_key: str,
    actual_rows: list[dict],
    forecast_rows: list[dict],
  ) -> list[dict]:
    current_month = period_key
    by_key: dict[tuple[str, str, str, str], dict] = {}
    for row in actual_rows:
      key = (
        str(row["reporting_year"]),
        row["period_month"],
        row["account_id"],
        row["basis_type"],
      )
      by_key[key] = row
    for row in forecast_rows:
      if row["period_month"] > current_month:
        key = (
          str(row["reporting_year"]),
          row["period_month"],
          row["account_id"],
          row["basis_type"],
        )
        by_key[key] = row
    return [by_key[k] for k in sorted(by_key.keys())]
```

### Forex implementation contract

Forex is implemented as deterministic Decimal revaluation against period end rates.

Computation inputs:

- `fx_balance_rows`: foreign currency balance lots from close_book snapshot.
- `period_end_rates`: quote map keyed by `ccy_pair` and `period_key`.
- `base_ccy`: from `derivation_rules.forex_m2m.base_ccy`.

Per lot formula:

- historical value: $hist = foreign\_amount \times booked\_rate$
- end value: $end = foreign\_amount \times period\_end\_rate$
- lot m2m: $m2m = end - hist$

Line-level aggregation:

- forex statement line equals sum of lot m2m values after quantize to 0.01.
- quantize mode is `ROUND_HALF_UP`.

```python
from decimal import Decimal, ROUND_HALF_UP

MONEY_Q = Decimal("0.01")

def compute_forex_m2m(
    fx_balance_rows: list[dict],
    period_end_rates: dict[tuple[str, str], Decimal],
    period_key: str,
) -> Decimal:
    total = Decimal("0")
    for row in fx_balance_rows:
        foreign_amount = Decimal(str(row["foreign_amount"]))
        booked_rate = Decimal(str(row["booked_rate"]))
        ccy_pair = row["ccy_pair"]
        end_rate = period_end_rates[(ccy_pair, period_key)]

        hist_value = foreign_amount * booked_rate
        end_value = foreign_amount * end_rate
        lot_m2m = end_value - hist_value
        total += lot_m2m

    return total.quantize(MONEY_Q, rounding=ROUND_HALF_UP)
```

Config binding for forex:

```python
def resolve_forex_line(ctx: StatementContext) -> Decimal:
    fx_rule = ctx.config.derivation_rules["forex_m2m"]
    included = set(fx_rule["include_accounts"])
    rows = [r for r in ctx.close_book_rows if r["account_name"] in included and r["is_fx"]]
    rates = load_period_end_rates(base_ccy=fx_rule["base_ccy"], period_key=ctx.period_key)
    return compute_forex_m2m(rows, rates, ctx.period_key)
```

Balance sheet aggregation:

- Account balances roll up by account asset type.
- FX balances translate to SGD before section roll up.
- IBKR cash uses sign based routing, positive to cash and bank, negative to credit.

Identity formulas:

- $net\ income = net\ personal\ income + investment\ p\&l + forex\ m2m - rental - cole - discretionary$
- $net\ worth = cash\ and\ bank + credit + liquid\ investments + illiquid\ and\ retirement$

Validation gates are fail closed:

| id | validation gate        | pass condition                             |
| -- | ---------------------- | ------------------------------------------ |
| 01 | mapping coverage       | no unmapped required keys                  |
| 02 | statement completeness | all required sections and lines populated  |
| 03 | book identity          | net income equals change in net assets     |
| 04 | deterministic ordering | section and line order fully resolved      |
| 05 | forecast coverage      | all future months in reporting year present |
| 06 | blend provenance       | each row tagged actual or forecast source   |

## Lifecycle state model

Lifecycle states align with statements lifecycle requirements.

| id | state     | meaning                          | allowed next |
| -- | --------- | -------------------------------- | ------------ |
| 01 | draft     | statement generated for review   | reviewed     |
| 02 | reviewed  | user review checkpoint complete  | finalized    |
| 03 | finalized | immutable published version      | reopened     |
| 04 | reopened  | controlled correction state      | finalized    |

Transition guards:

- draft to reviewed requires explicit user review confirmation.
- reviewed to finalized requires publish confirmation and all finalize publish validations.
- finalized to reopened requires user reason logging with actor and timestamp.
- reopened to finalized creates a new version id and preserves prior versions.

Lifecycle controller implementation pattern:

```python
ALLOWED_NEXT = {
    "draft": {"reviewed"},
    "reviewed": {"finalized"},
    "finalized": {"reopened"},
    "reopened": {"finalized"},
}

class LifecycleController:
    def transition(self, from_state: str, to_state: str, event: dict) -> str:
        if to_state not in ALLOWED_NEXT[from_state]:
            raise ValueError("invalid_lifecycle_transition")
        if from_state == "reviewed" and to_state == "finalized" and not event["publish_confirmed"]:
            raise ValueError("publish_confirmation_required")
        if from_state == "finalized" and to_state == "reopened" and not event.get("reopen_reason"):
            raise ValueError("reopen_reason_required")
        return to_state
```

## Publish contract and artifact rules

Required artifact set:

| id | artifact_type           | format | required | notes                     |
| -- | ----------------------- | ------ | -------- | ------------------------- |
| 01 | income_statement_pdf    | pdf    | yes      | finalized period output   |
| 02 | balance_sheet_pdf       | pdf    | yes      | finalized period output   |
| 03 | publish_manifest        | json   | yes      | lineage and storage map   |

Path policy is deterministic and version scoped.

| id | key part         | example         | rule                         |
| -- | ---------------- | --------------- | ---------------------------- |
| 01 | root prefix      | statements      | config driven                |
| 02 | period partition | year=2026/month=02 | required in all keys      |
| 03 | period key       | period_key=2026-02 | required in all keys      |
| 04 | version segment  | publish_version=v003 | monotonic per period    |
| 05 | object name      | income_statement_2026-02_v003.pdf | deterministic |

Publish rule set:

- finalized artifact keys are write once.
- same idempotency key plus same payload returns same artifact references.
- same idempotency key plus different payload is conflict and blocked.
- reopen does not mutate prior artifact versions.

Publish runtime implementation pattern:

```python
class PublishStatementsService:
    def __init__(
        self,
        repo: "StatementRepository",
        lifecycle: LifecycleController,
        renderer: PdfRenderer,
        storage: "StorageGateway",
        version_allocator: "VersionAllocator",
    ):
        self.repo = repo
        self.lifecycle = lifecycle
        self.renderer = renderer
        self.storage = storage
        self.version_allocator = version_allocator

    def run(self, request: "StatementPublishRequest") -> "StatementPublishResult":
        replay = self.repo.lookup_idempotency(request.idempotency_key)
        if replay and replay.payload_hash == request.payload_hash:
            return replay.result
        if replay and replay.payload_hash != request.payload_hash:
            raise ValueError("idempotency_conflict")

        bundle = self.repo.load_reviewed_bundle(request.statement_bundle_ref)
        self.lifecycle.transition("reviewed", "finalized", request.to_event())
        version_id = self.version_allocator.next(request.period_key)

        income_pdf = self.renderer.render(bundle.income_statement, bundle.render_hints)
        balance_pdf = self.renderer.render(bundle.balance_sheet, bundle.render_hints)
        manifest = self.storage.upload_publish_set(request.period_key, version_id, income_pdf, balance_pdf)

        result = StatementPublishResult.finalized(version_id=version_id, manifest=manifest)
        self.repo.store_idempotency_result(request.idempotency_key, request.payload_hash, result)
        return result
```
