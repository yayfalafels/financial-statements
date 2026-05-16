---
title: Data Pipeline Specification
doc_type: architecture
topic_type: design
owner: design
scope: Cross-component data contracts from staged ingest through close_book assembly
status: open
last_updated: 2026-05-10
---

# Data Pipeline Design

## Table of Contents

- [Summary](#summary)
- [Reference documents](#reference-documents)
- [Related skills](#related-skills)
- [Component boundary](#component-boundary)
- [Runtime ownership contract](#runtime-ownership-contract)
- [Component scope boundary](#component-scope-boundary)
- [Interaction topology](#interaction-topology)
- [Stage invocation contract](#stage-invocation-contract)
- [Canonical data contracts](#canonical-data-contracts)
- [Transformation rules](#transformation-rules)
- [Idempotency and recovery](#idempotency-and-recovery)
- [Validation gates](#validation-gates)
- [Lineage and reproducibility](#lineage-and-reproducibility)

## Summary

This document defines the cross-component interface contracts for monthly close data flow from raw ingest to close_book outputs. It specifies component handoff boundaries, stage entry and exit schemas, status signaling, blocking conditions, retry policy, checkpoint semantics, and lineage guarantees across workflow orchestrator, account close runtime, bill and shared-cost runtime, source adapters, sqlite adapter, and sqlite app database.

The intent is stable inter-component coordination: internal implementation may change within a component as long as interface contracts remain compatible. All monetary values use `decimal.Decimal`, stage transitions are fail-closed, and persisted outputs carry lineage fields required for replay and audit.

This document is limited to architecture-level coordination contracts and does not define internal class design, package structure, or algorithm internals, which remain in component-specific design documents.

## Reference documents

- [Reconciliation Design](reconciliation.md)
- [Statement Builder Design](statements.md)
- [Architecture Overview](architecture.md)

## Related skills

- `sqlite3`: SQLite connection, transaction, and parameterized query execution patterns.
- `decimal`: Exact monetary arithmetic and rounding behavior for financial amounts.
- `sqlite-data-pipelines`: Idempotent ingest, deterministic hashing, and staging isolation patterns.
- `reconciliation-patterns`: Tolerance handling and reconciliation phase discipline for close workflows.

## Component boundary

The data pipeline spans six components with explicit interface boundaries and handoff directions.

**Component list:**

1. **Workflow orchestrator** — calls stage interfaces and consumes status and gate outcomes
2. **Account close runtime** — accepts account-stage inputs and emits account-stage outputs
3. **Bill and shared-cost runtime** — accepts bill-stage inputs and emits bill-stage outputs
4. **Source adapters** — emit normalized ingest payloads and ingest diagnostics
5. **SQLite adapter** — provides persistence and checkpoint interface used by runtimes
6. **SQLite app database** — stores canonical datasets consumed through sqlite adapter only

**Data flow direction:**
```
External Sources
    ↓
Source Adapters (raw ingest)
    ↓
Staging Tables (normalize, deduplicate)
    ↓
Account Close Runtime + Bill/Shared-Cost Runtime (reconcile, adjust)
    ↓
Close-book Assembly (statement-ready data)
    ↓
SQLite App Database (persist with lineage)
    ↓
Statement Builder (external, out of scope)
```

Interface rule: cross-component writes are not allowed. A runtime does not mutate another runtime dataset directly. All persistence uses sqlite adapter contracts.

## Runtime ownership contract

Each component publishes and consumes interface contracts with explicit coordination signals.

**Orchestrator to stage runtime contract:**
- Request: stage ID, session ID, input dataset refs, config snapshot ref
- Response: status, output dataset refs, gate outcomes, error payload
- Blocking: any gate failure returns `failed_blocking` and halts downstream stages

**Runtime to sqlite adapter contract:**
- Request: write canonical rows, checkpoint key, lineage fields
- Response: commit success or rollback with reason code
- Blocking: partial commit is invalid; stage returns failed status on any write error

**Source adapter to orchestrator contract:**
- Request: source extraction with ingest window and source config ref
- Response: raw or normalized payload refs, parse diagnostics, record counts
- Blocking: schema parse failure or required-field failure returns blocking status

**Cross-runtime contract:**
- Account close runtime and bill runtime exchange data through persisted canonical datasets only
- Direct in-memory cross-runtime mutation is out of contract and not allowed

## Component scope boundary

Certain design concerns are explicitly out of scope for this pipeline definition.

**Out of scope:**
- Reconciliation engine algorithm design — already covered in reconciliation.md
- Statement builder layout and rendering — already covered in statements.md
- General ledger structure and intercompany eliminations — not in close scope
- Tax and regulatory reporting — handled post-close by statement builder
- User approval workflow and signature capture — handled by UI layer
- Internal module class design, package structure, and private helper design

**In scope:**
- Data contracts between source adapters and staging
- Canonical schemas for raw, normalized, and close-book-ready datasets
- Transformation and deduplication logic
- Validation gates and fail-closed behavior
- Idempotency and recovery mechanics
- Lineage and reproducibility controls

Focus remains on data contracts and stage interface boundaries only.

## Interaction topology

This section defines interaction layout only, not repository or class layout.

**Interaction sequence:**
1. Orchestrator invokes source adapter interfaces for ingest outputs.
2. Orchestrator invokes account and bill runtime interfaces with staged input refs.
3. Runtimes invoke sqlite adapter interfaces for write and checkpoint operations.
4. Downstream consumers read only canonical persisted outputs and lineage fields.

**Layout constraint:**
- Interface changes must remain backward-compatible within a close cycle.
- New optional fields are allowed; required field changes require version bump.

## Stage invocation contract

The pipeline defines a sequence of stages with explicit input, output, status, and blocking conditions.

**Stage sequence and contracts:**

| id | stage      | in refs      | out refs     | block signal      | retry |
| -- | ---------- | ------------ | ------------ | ----------------- | ----- |
| 01 | ingest     | source specs | raw datasets | schema_invalid    | yes   |
| 02 | normalize  | raw datasets | norm datasets| count_mismatch    | yes   |
| 03 | reconcile  | norm datasets| adj datasets | balance_mismatch  | no    |
| 04 | bill_match | bill inputs  | bill outputs | fk_invalid        | yes   |
| 05 | split_cost | alloc inputs | cost outputs | sum_invalid       | yes   |
| 06 | assemble   | stage outputs| close_book   | lineage_invalid   | no    |

This table specifies interface-level coordination only. Internal algorithm steps remain component-owned.

## Canonical data contracts

The pipeline enforces strict schemas for raw, normalized, reconciled, and close-book-ready datasets.

**Dataset categories:**

1. **Raw staging** — unmodified data from source; includes source lineage and ingest timestamp
2. **Normalized staging** — canonical schema for ledger, bills, and allocations; deduplication applied
3. **Reconciled dataset** — adjustments, balance verification, and variance classification
4. **Close-book dataset** — statement-ready aggregates with all adjustments applied

**Schema requirements per dataset:**

- **Raw staging:** source_system, record_type, original_id, ingest_timestamp, lineage_hash, payload_json
- **Normalized staging:** entity_key, period_key, normalized_date, account_id, amount_decimal, description, source_record_id
- **Reconciled dataset:** adjustment_id, session_id, account_id, period_key, adjustment_reason, amount_decimal, approval_status
- **Close-book dataset:** general_ledger_line, account_code, period_key, amount_decimal, adjustment_id_list, posting_status

**Placeholder:** This section will detail the required fields, data types, nullable constraints, foreign-key relationships, and index requirements for each canonical schema. All amount fields use `decimal.Decimal`. All schemas include lineage_hash and session_id for reproducibility.

## Transformation rules

Transformations within the pipeline follow deterministic ordering and key derivation rules.

**Core transformation principles:**

1. **Deterministic ordering** — all transforms sorted by (date ASC, source_index ASC) before processing
2. **Key derivation** — entity keys are SHA256 hash of normalized tuple `(account_id, source_system, original_id, date)`
3. **Deduplication** — upsert by entity_key; newer ingest overwrites older with same key
4. **Decimal-safe amounts** — all arithmetic uses `decimal.Decimal`; no float conversions
5. **Idempotent ID generation** — IDs are deterministic hashes, never database sequences

**Transformation stages:**

- **Ingest → Raw staging:** parse source format, preserve all fields, add ingest_timestamp and lineage_hash
- **Raw staging → Normalized:** normalize account codes, date formats, amount types; apply source-specific mapping
- **Normalized → Reconciled:** apply reconciliation adjustments and variance classification
- **Reconciled → Close-book:** aggregate by general-ledger account and period; include all adjustment lineage

**Placeholder:** This section will specify the deterministic ordering rules, key derivation algorithms, deduplication upsert logic, and Decimal handling requirements. All transformations are reversible through lineage fields.

## Idempotency and recovery

The pipeline must support safe reruns and transaction-level recovery without manual state cleanup.

**Rerun behavior:**
- Same ingest with same source data produces identical staging records
- Stage restart from checkpoint produces identical outputs as fresh run
- Session replay produces byte-identical close-book dataset

**Checkpoint keys:**
- Ingest checkpoint: `(source_system, ingest_batch_id, schema_version)`
- Normalize checkpoint: `(raw_staging_record_count, normalize_rule_version)`
- Reconcile checkpoint: `(session_id, account_id, period_key)`
- Assembly checkpoint: `(close_book_session_id, record_count_hash)`

**Transaction rollback boundaries:**
- Ingest stage: rollback raw_staging writes on parse error
- Normalize stage: rollback normalized_staging writes on key collision or schema mismatch
- Reconcile stage: rollback adjustment records on variance rejection
- Assembly stage: rollback close_book writes on lineage check failure

**Placeholder:** This section will detail rerun behavior guarantees, named checkpoint keys for restart safety, transaction isolation levels per stage, and rollback scope. Idempotency enables safe retry without state inspection.

## Validation gates

Each stage enforces validation gates that block downstream progress on failure.

**Gate categories:**

1. **Schema validation** — all required fields present and correctly typed
2. **Completeness validation** — no null values in critical fields, record count threshold met
3. **Balance validation** — sum invariants hold across debit/credit sides
4. **Foreign-key validation** — all account_ids and period_keys reference valid parent records
5. **Lineage validation** — all records traceable to source artifact via session_id and hash chain

**Fail-closed behavior:**
- Validation failure blocks all downstream stages
- Failed stage must be explicitly marked for retry or skipped by operator
- No partial-pass behavior; all records must pass or entire stage fails

**Placeholder:** This section will specify validation rules per gate type, pass/fail criteria, error messages and codes, and the escalation path to operator intervention. All validation is deterministic and repeatable.

## Lineage and reproducibility

Session records and artifact hashes enable complete audit lineage and reproducible reruns.

**Session record captures:**
- Session ID (unique per close cycle and source)
- Start and end timestamps
- Stage sequence and status per stage
- Configuration snapshot at session start
- Source artifact hashes

**Lineage fields in staging tables:**
- `session_id` — links record to parent reconciliation session
- `lineage_hash` — SHA256 of record content for integrity check
- `config_snapshot_ref` — reference to frozen config used for transformation
- `source_artifact_hash` — hash of original source file

**Artifact hash requirements:**
- **Source artifacts:** hash of raw ingest payload
- **Staging tables:** deterministic hash of normalized record
- **Checkpoint records:** hash of stage output for replay validation

**Placeholder:** This section will detail session metadata structure, lineage field usage, hash chain validation, and reproducibility guarantees. Lineage enables point-in-time reconstruction and audit trail for regulatory requirements.

---
Next steps: flesh out each interface contract with field-level schemas, status enums, and versioning policy.
