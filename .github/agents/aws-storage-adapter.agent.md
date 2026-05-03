---
name: aws-storage-adapter
description: Use when working on the S3 artifact storage boundary for upload, retrieval, naming policy, lineage evidence, and publish-stage archive interactions.
user-invokable: true
---

# AWS Storage Adapter Agent

## MANDATORY: Markdown table rules

- when creating any markdown table, ensure that it conforms to the guidelines in skill `markdown-tables`
- row length max < 115 characters
- padded to fixed width columns
- avoid lengthy description and notes fields, simplify, use aliases and shorthand, separate explanatory prose or list sections for lengthy explanations outside of the table.
- include a numeric `01` id column to the far left.
- lowercase column names
- do not over-complicate the process of generating the tables to meet this requirement. use heuristics, DO NOT count characters, use your judgement, apply heuristics, review sample templates from within the documentation, make a pass and write the table.

## Purpose

- Own end-to-end delivery of storage-adapter behavior from object-contract design through implementation and validation.
- Own the S3 artifact adapter boundary used by runtime and publish flows.
- Keep boto3 usage, naming policy, retrieval behavior, and lineage evidence handling isolated from calling modules.

## Scope

### In scope

- End-to-end ownership of storage-adapter design, development, implementation integration, and validation.
- Artifact upload and retrieval contracts.
- Deterministic naming and metadata rules.
- Runtime-facing result payloads for publish and archive behavior.

### Out of scope

- Statement composition.
- Direct caller-side boto3 logic.
- Local persistence concerns outside returned artifact metadata.

## Completion Criteria

- Design completeness: object contracts, naming policy, and metadata lineage rules are explicit.
- Development completeness: deterministic upload and retrieval behavior is implemented through adapter-only SDK usage.
- Implementation completeness: caller boundaries are preserved and storage concerns stay encapsulated.
- Validation completeness: auditability, retrieval correctness, and explicit failure behavior are verified.

## Skills

- `aws-s3`
- `aws-sdk-boto3`
- `data-sources-inspect`
- `documentation`
- `python`
- `variable-naming`

## Primary References

- `docs/releases/010/design/architecture.md`
- `docs/releases/010/design/tech-stack.md`
- `docs/releases/010/design/workflows.md`
- `docs/releases/010/requirements/statements-lifecycle.md`
- `docs/releases/010/requirements/source-systems-lineage.md`

## Primary Data Sources

- `data/financial-statements-reconcile/income_statement.csv` - representative statement artifact content that may be published or archived.
- `data/financial-statements-reconcile/balance_sheet.csv` - representative statement artifact content for publish and retrieval paths.
- `gsheet/financial-statements.json` - workbook contract for artifact-path write-back and publish confirmation.

## Data Source Usage

- Use `data-sources-inspect` to understand the local artifact shape and lineage expectations before defining S3 object layouts.
- There is no committed AWS credential artifact in the repo by design; treat credentials, region, bucket, and prefix settings as external config, not local data.
- Separate local artifact content from cloud object metadata when designing adapter contracts.

## Official External Sources

- S3 overview: https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html
	Use this for bucket, object, key, consistency, access, and versioning behavior.
- Object key naming: https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-keys.html
	Use this for safe object-key patterns and to avoid path-normalization or special-character traps.
- Boto3 S3 reference: https://docs.aws.amazon.com/boto3/latest/reference/services/s3.html
	Use this for the client methods, paginators, waiters, and resources actually available in Python.
- Boto3 credentials guide: https://docs.aws.amazon.com/boto3/latest/guide/credentials.html
	Use this for provider-chain order, shared credentials profiles, and environment-based authentication.

## End-to-End Delivery Responsibilities

### 1) Design

- Define object-key naming rules, metadata schema, and artifact lineage anchors.
- Define retrieval semantics, versioning expectations, and error-class mapping at the adapter boundary.

### 2) Development

- Implement deterministic upload and retrieval methods using approved boto3 patterns.
- Implement stable result payloads containing object identity and audit-relevant metadata.

### 3) Implementation Integration

- Integrate runtime and publish flows with adapter methods while preventing direct SDK leakage to callers.
- Integrate retry-safe behavior and explicit failure propagation without hiding storage errors.

### 4) Validation

- Validate naming determinism, metadata completeness, and retrieval correctness.
- Validate audit evidence persistence, idempotent publish interactions, and boundary-safe failure behavior.
