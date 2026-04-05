# Helper Workbooks Design Plan

## Table of contents

- [Overview](#overview)
- [Goal](#goal)
- [Scope](#scope)
- [Out of scope](#out-of-scope)
- [Architecture baseline](#architecture-baseline)
- [Environment and tooling](#environment-and-tooling)
- [Source files](#source-files)
- [Raw statement references](#raw-statement-references)
- [Report format assumptions](#report-format-assumptions)
- [Design workflow](#design-workflow)
- [Workbook inspection sequence](#workbook-inspection-sequence)
- [Schema inspection checklist](#schema-inspection-checklist)
- [Data model decisions](#data-model-decisions)
- [Mapping matrix specification](#mapping-matrix-specification)
- [Validation and risk controls](#validation-and-risk-controls)
- [Deliverables](#deliverables)
- [Acceptance criteria](#acceptance-criteria)

## Overview

This prompt defines a design only workflow for inspecting all helper Google Sheets workbooks with the sqlite gsheet helper package, understanding each schema from live ranges, and producing a consolidated data model for `financial_statements.db`.

This prompt is for design and analysis work. Do not implement migrations or ETL code in this phase.

Helper workbooks are report shaped and not strict table structures. Expect spacer rows, spacer columns, mixed section headers, matrix style month pivots, and statement style presentation.

## Goal

Design a repeatable inspection to model process that:

- Profiles every in scope helper workbook and sheet
- Validates actual headers, data types, and key fields
- Designs parsing logic from report shaped ranges into normalized or semi normalized records
- Maps source data into the consolidated SQLite schema
- Preserves the two stage model in one database, statement layer and reconciled ledger layer
- Preserves lineage from raw statement inputs to helper workbook values and then to DB targets

## Scope

In scope workbooks:

- `gsheet/cash-expenses.json`
- `gsheet/cpf.json`
- `gsheet/financial-statements.json`
- `gsheet/homebudget-workbook.json`
- `gsheet/ibkr-iba.json`
- `gsheet/shared-expenses.json`

## Out of scope

- SQL migration scripts
- Application code changes
- Historical backfill jobs
- Production rollout plan

`statements.db` is not the raw input source in this plan. It is a post parse landing store and may be used only as a lineage checkpoint.

## Architecture baseline

Use a single consolidated database, `financial_statements.db`.

Maintain two separate table groups:

- Statement layer tables for raw statement imports and observed balances
- Ledger layer tables for reconciled balances and variance tracking

Current baseline schema reference:

- `docs/develop/design/database-schema.md`

## Environment and tooling

- OS: Windows 11 Pro
- Python: 3.12.10
- IDE: VS Code
- Package: sqlite gsheet helper package

Reuse existing data access pattern from:

- `reference/hb-finances/database.py`

Focus on `load_gsheet` and `get_sheet` style behavior for range reads and type handling.

### CRITICAL: Environment management rules

1. **Development scaffolding** (construction tools, temporary only)
   - `.dev/env/` â€” Python virtual environment for helper scripts ONLY
   - `.dev/.scripts/python/` â€” Python helper scripts for diagnostics, analysis, DB inspection
   - `.dev/.scripts/bash/` â€” Bash helper scripts
   - `.dev/.scripts/cmd/` â€” Windows batch helper scripts
   - **DO NOT CREATE A NEW VIRTUAL ENV** - Reuse existing `.dev/env/`
   - **DO NOT USE `.dev/env` FOR MAIN APP** - This is scaffolding only

2. **Main application environment** (production runtime)
   - `env/` â€” Python virtual environment for wrapper package and tests (root level)
   - Used by: wrapper package, test scripts, CLI commands
   - This is the "finished building" environment

**Metaphor:** `.dev/` is scaffolding and cranes during construction. `env/` is the finished building's electrical and plumbing systems.

---

## Source files

Primary design inputs:

- `docs/develop/design/database-schema.md`
- `docs/google-sheets.md`
- `docs/develop/design/design-source-alignment.md`
- `reference/hb-finances/database.py`

Workbook configs:

- `gsheet/financial-statements.json`
- `gsheet/homebudget-workbook.json`
- `gsheet/cpf.json`
- `gsheet/ibkr-iba.json`
- `gsheet/cash-expenses.json`
- `gsheet/shared-expenses.json`

## Raw statement references

Use raw statement examples as source truth for parsing design:

- `reference/statements/citi-twh/Citibank Personal - 202509.pdf`
- `reference/statements/dbs-multi/DBSStatement_202509.pdf`
- `reference/statements/ibkr-iba/U1109040_Activity_202510.csv`
- `reference/statements/uob/UOBOne_statement_202509.pdf`

Also inspect additional folders under `reference/statements/` for coverage:

- `ibkr-ira`
- `others`
- `singtel`
- `spservices`
- `wells-fargo`

## Report format assumptions

Assume helper sheets are report layouts. They are not strict row wise transaction tables.

Expected layout patterns:

- Multi section blocks per sheet with section title rows
- Spacer rows and spacer columns
- Cross tab month columns with year and month headers
- Metric labels in first column and month values across columns
- Mixed units and mixed numeric formats in one range

Design requirement:

- Create an explicit extraction model before target table mapping
- Document parsing rules to convert report layouts into canonical record sets

## Design workflow

### Phase 1: Discovery setup

- Confirm workbook ids, sheet range names, and declared type hints from each config JSON
- Define one schema profile template for all sheets
- Define one mapping matrix template from source to target tables
- Define one report parsing rule template for section detection, header detection, pivot unrolling, and metric normalization

Output:

- Inspection template
- Mapping matrix template
- Parsing rule template

### Phase 2: Canonical anchor inspection

Inspect `gsheet/financial-statements.json` first.

- Profile `accounts`, `balances`, and `forex_rates`
- Confirm account id conventions
- Confirm period grain and currency conventions
- Confirm rate representation conventions

Output:

- Canonical account and period contracts
- Candidate key definitions for shared use

### Phase 3: Mapping workbook inspection

Inspect `gsheet/homebudget-workbook.json`.

- Profile `cat_map`
- Identify category hierarchy levels
- Determine mapping cardinality and uniqueness assumptions

Output:

- Category mapping model proposal
- Key and constraint proposal

### Phase 4: Asset workbook inspection

Inspect in parallel:

- `gsheet/cpf.json`
- `gsheet/ibkr-iba.json`

Tasks:

- Profile each sheet range and header row position
- Validate month and year axis behavior
- Identify whether source shape is wide matrix or long records
- Propose normalization strategy for queryability and lineage
- Document unpivot strategy from month columns into period keyed records
- Document section parser rules for metric label rows

Output:

- Asset data normalization design
- Sheet to table mapping proposal
- Asset parsing rule specification

### Phase 5: Expense workbook inspection

Inspect in parallel:

- `gsheet/cash-expenses.json`
- `gsheet/shared-expenses.json`

Tasks:

- Validate transaction field contracts
- Define natural dedupe keys
- Define account and category linkage fields
- Define date and amount precision rules
- Define parser rules for non tabular report segments and optional fields

Output:

- Transaction ingestion design for helper workbooks
- Dedupe and lineage design
- Expense parsing rule specification

### Phase 6: Raw statement to workbook lineage design

- Inspect raw inputs in `reference/statements/` and identify extractable entities by source
- Define source specific extraction contracts for PDF and CSV formats
- Map raw source entities to helper workbook sections and fields
- Mark manual intervention steps where helper workbook values are user entered from statement views
- Define lineage ids from raw file to workbook cell range to canonical record

Output:

- Raw to workbook lineage map
- Source specific parser contract matrix

### Phase 7: Cross workbook contract validation

- Validate account ids across all workbook outputs against canonical account list
- Validate date and period formats across all sheets
- Validate currency consistency and conversion assumptions
- Record all schema drift risks, renamed headers, moved ranges, sparse columns, and mixed type columns

Output:

- Cross workbook validation report
- Open decisions list with recommended default choices

### Phase 8: Consolidated data model design

Design and document table level integration for helper workbook data.

Include:

- Target tables in statement layer and ledger layer
- Any additional reference tables required for mapping and lineage
- Uniqueness constraints
- Foreign key relationships
- Immutable write rules for imported snapshots

Output:

- Proposed consolidated model delta from current baseline
- Field level mapping matrix with constraints

### Phase 9: Verification design

Define verification checklist for ongoing monthly use.

Include:

- Schema profile completeness checks
- Source to target mapping completeness checks
- Constraint checks on keys and referential links
- Regression check for workbook layout drift before close run

Output:

- Repeatable verification checklist
- Go and no go criteria for implementation phase

## Workbook inspection sequence

Use this sequence to reduce dependency risk:

1. `gsheet/financial-statements.json`
2. `gsheet/homebudget-workbook.json`
3. `gsheet/cpf.json` and `gsheet/ibkr-iba.json` in parallel
4. `gsheet/cash-expenses.json` and `gsheet/shared-expenses.json` in parallel
5. Cross workbook validation pass

## Schema inspection checklist

Capture for every sheet:

- Workbook id
- Sheet name
- Header range
- Data range
- Header row index
- Column names as observed
- Inferred data type per column
- Declared type rule if present
- Null and blank behavior
- Candidate key fields
- Account id semantics
- Period and date semantics
- Currency semantics
- Example value profile sample
- Risks and ambiguities
- Section boundary rules
- Pivot header rules
- Unpivot rules

## Data model decisions

For each workbook sheet, decide and document:

- Keep as normalized table or keep as raw snapshot plus normalized table
- Target table group, statement layer or ledger layer
- Grain, one row per transaction, period account, or metric snapshot
- Key strategy, natural key or surrogate key plus unique constraint
- Required lineage fields, workbook id, sheet name, range, extraction timestamp
- Normalization level, fully normalized or semi normalized snapshot plus detail rows

## Mapping matrix specification

Build one matrix with these columns:

- Source workbook config path
- Source sheet name
- Source column
- Target table
- Target column
- Transform rule
- Type rule
- Null rule
- Key participation
- Validation rule
- Notes

Build a second lineage matrix with these columns:

- Raw source path
- Source format
- Extracted entity
- Helper workbook sheet
- Helper workbook field or section
- Canonical record field
- Target DB table and column
- Transformation and parse rule id
- Manual step flag

## Validation and risk controls

Minimum controls:

- Header drift detection against previous profile
- Type drift detection for numeric and date columns
- Range boundary checks to detect missing rows
- Account id referential validation against canonical accounts
- Period continuity checks for monthly data
- Report section parser tests against spacer rows and mixed headers
- Pivot unroll checks for month and year alignment
- Raw source to workbook lineage completeness checks

## Deliverables

- Workbook schema profiles for all in scope sheets
- Parsing rule specs for report shaped sheets
- Raw statement to workbook lineage map
- Cross workbook contract validation report
- Consolidated data model delta proposal
- Source to target mapping matrix
- Verification checklist for future monthly closes

## Acceptance criteria

1. Every in scope workbook has at least one completed schema profile.
2. Every in scope sheet has source to target mapping in the matrix.
3. Every report shaped sheet has parsing rules for section detection and pivot unrolling.
4. Raw statement to workbook lineage is documented for available examples in `reference/statements/`.
5. Cross workbook contract issues are either resolved or explicitly documented.
6. The proposed model preserves two stage separation in one database.
7. Design outputs are ready for migration and ETL implementation planning.


