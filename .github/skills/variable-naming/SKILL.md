---
name: variable-naming
description: Naming conventions for SQL schema objects and Python variables across code, database, and config artifacts.
license: MIT
compatibility: Python 3.8+
metadata:
  author: yayfalafels
  version: 1.0.0
---

## Overview

This skill defines simple, consistent naming rules to reduce ambiguity across SQL, Python source code, and configuration files.

## Rules

- **SQL Object Attribute Naming:** Use `<object>.<attribute>` for table columns, avoiding redundant qualifiers.
- **SQL Primary and Foreign Key Naming:** Use `id` for primary keys and `<foreign_table>_id` for foreign keys, with optional tags for disambiguation.
- **Carry-Through Naming Across Layers:** Use the same variable name for the same concept across all layers to minimize aliasing.
- **Python PEP Naming Conventions:** Follow standard Python naming conventions for classes, variables, and functions.
- **SQL Table Naming Baseline:** Use singular snake_case table names.
- **SQL Reserved Word Avoidance:** Avoid reserved words in identifiers.
- **Enum Value Naming:** Use lowercase snake_case across SQL, JSON, and Python literals.
- **Approved Abbreviations:** Allow only common approved abbreviations.
- **Timestamp Field Convention:** Standardize `_at` and `_date` fields with UTC ISO-8601 serialization.
- **Boolean Naming:** Prefix booleans with `is_`, `has_`, or `can_`.
- **Unit and Currency Suffixes:** Include unit/currency suffixes when ambiguity is possible.
- **External vs Internal ID Naming:** Distinguish external IDs from internal `id`.
- **Method Naming Orientation:** Prefer `object.action` or `object_action` orientation for function and method names.

## SQL Object Attribute Naming

Use SQL `<object>.<attribute>` for `table_name.column_name`.

If the attribute is already fully specified by the table path, do not add a redundant qualifier that repeats the table meaning.

Example: use `reconcile.balance` instead of `reconcile.reconcile_balance`.

## SQL Primary and Foreign Key Naming

Use `id` as the primary key for all tables (`<object>.id`).

If a table has a composite natural key, still add a surrogate primary key `id`.

Name foreign keys as `<foreign_table>_<optional_tag>_id`, with `<foreign_table>_id` as the default.

Example: to reference `reconcile`, use `reconcile_id`.

Only add `<optional_tag>` when there are multiple references to the same foreign table and disambiguation is required.

## Carry-Through Naming Across Layers

Carry the same variable name through source data, Python modules, database schema, JSON config, and interfaces when referring to the same concept.

Minimize arbitrary alias injection.

Example: if the concept is `cash` in module X, keep `cash` in module Y rather than introducing `cash_notes` for the same concept.

## Python PEP Naming Conventions

Use standard Python naming conventions in source code:

- `CapWords` for classes
- `lowercase_with_underscores` for variables and functions
- `UPPERCASE` for constants

## SQL Table Naming Baseline

Use singular snake_case table names.

Examples:

- `account`, not `accounts`
- `reconcile_session`, not `reconcile_sessions`

## SQL Reserved Word Avoidance

Avoid SQL reserved words for table and column identifiers.

Use descriptive alternatives instead of quoting reserved words.

Examples:

- `txn_date` instead of `date`
- `sort_order` instead of `order`

## Enum Value Naming

Use lowercase snake_case enum and status values across SQL, JSON, and Python literals.

Examples:

- `in_progress`
- `closed`
- `failed`

## Approved Abbreviations

Allow only common approved abbreviations. Do not invent ad hoc abbreviations.

Common approved examples:

- `id`
- `qty`
- `amt`
- `cfg`
- `txn`

## Timestamp Field Convention

Use standardized time field names and formats:

- `created_at`
- `updated_at`
- `resolved_at`

Use `_date` for date-only fields and `_at` for timestamps.

Serialize timestamps in UTC ISO-8601 when persisted outside runtime objects.

## Boolean Naming

Name boolean fields and variables with semantic prefixes:

- `is_current`
- `has_errors`
- `can_retry`

## Unit and Currency Suffixes

Add explicit unit or currency suffixes when values would otherwise be ambiguous.

Examples:

- `amount_sgd`
- `duration_minutes`
- `rate_pct`

## External vs Internal ID Naming

Use `id` for internal primary keys.

For external system identifiers, use explicit source prefixes.

Examples:

- `hb_account_id`
- `statement_txn_id`

## Method Naming Orientation

Prefer `object.action` or `object_action` naming orientation.

This aligns functional naming with later migration to class-based implementation.

Example preference:

- `account_reconcile` preferred over `reconcile_account`

Rationale:

- `account_reconcile` maps naturally to class-style `account.reconcile`.
