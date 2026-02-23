---
name: plan-design
description: This prompt generates a detailed design plan for the Financial Statements application, covering data model mapping, calculation rules, statement generation, API surface, CLI UX, packaging, and validation strategy.
model: Auto (copilot)
agent: agent
---

## Plan: Financial Statements Application Design

This plan covers a full design pass for the Financial Statements Python application, including data source integration, financial statement concepts and formats, calculation rules and aggregations, statement generation and export, API surface and module structure, CLI UX flows, packaging, and validation strategy. It is based on the existing reference implementation in [reference/hb-finances/](reference/hb-finances/), the project workflow and design goals in [docs/workflow.md](docs/workflow.md), [docs/mvp-design.md](docs/mvp-design.md), and [docs/homebudget.md](docs/homebudget.md), plus environment constraints in [docs/develop/environment.md](docs/develop/environment.md) and Python conventions in skill `python`. Missing information exists around the precise financial statement formats required, the calculation rules for accruals and expense allocation, and the integration bridge between homebudget data and statement generation, which the design must derive from the reference code, user workflow, and financial accounting conventions.

The agent should first digest the financial statement requirements from [docs/mvp-design.md](docs/mvp-design.md) and [reference/notion/](reference/notion/) into a machine-friendly markdown reference, then analyze the reference implementation to identify data transformation pipelines, calculation rules, and export formats. Any conflicts between the docs and reference code should be logged and resolved with user feedback.

## Development tooling setup

A reusable development environment under [.dev](.dev) supports the design workflow with helper scripts and data analysis tools.

**Directory structure**
- [.dev/env](.dev/env) — Python virtual environment (git ignored)
- [.dev/requirements.txt](.dev/requirements.txt) — Python dependencies for analysis and tooling
- [.dev/.scripts/python](.dev/.scripts/python) — Python helper scripts for schema analysis, calculation validation
- [.dev/.scripts/bash](.dev/.scripts/bash) — Bash scripts for generic terminal operations

**Initial setup tasks**
1. Verify [.dev/requirements.txt](.dev/requirements.txt) includes `pandas`, `sqlalchemy`, `openpyxl`, and other analysis libraries.
2. Activate [.dev/env](.dev/env) virtual environment.
3. Install dependencies from [.dev/requirements.txt](.dev/requirements.txt).
4. Create helper scripts as needed in [.dev/.scripts/python](.dev/.scripts/python), for example `analyze_statements.py` for calculation validation.

Helper scripts are referenced directly in step processes where data analysis or transformation is needed.

## Agent workflow

**Steps**

0. Dev tooling setup
1. Financial statement requirements digest
2. Data source inventory and gap log
3. Data transformation and calculation rules
4. Financial statement domain model
5. Core API surface and module boundaries
6. Statement generation and export strategy
7. CLI UX and command map
8. Packaging and repository layout
9. Testing and validation strategy
10. Design documentation and rollout

### Step 0: Dev tooling setup

**Goal**
Initialize the development environment and helper script framework for the design workflow.

**Inputs**
- (initial setup only, no external inputs)

**Process**
- Verify [.dev/requirements.txt](.dev/requirements.txt) has dependencies: pandas, sqlalchemy, openpyxl, numpy.
- Activate [.dev/env](.dev/env) virtual environment.
- Install dependencies.
- Create directory structure [.dev/.scripts/python](.dev/.scripts/python) if not present.

**Expected outputs**
- Activated [.dev/env](.dev/env) virtual environment.
- Verified [.dev/requirements.txt](.dev/requirements.txt) with dependencies.
- Ready helper script directories.

**Structured prompt**
```
Set up the development tooling environment:
1. Verify .dev/requirements.txt has dependencies: pandas, sqlalchemy, openpyxl, numpy.
2. Activate the Python virtual environment at .dev/env.
3. Install all dependencies.
4. Verify .dev/.scripts/python is ready for analysis scripts.
```

**Autonomy and clarification**
- Safe to determine autonomously: environment activation, dependency list, directory structure.
- Needs clarification: any additional libraries required for specific data transformation or validation.

### Step 1: Financial statement requirements digest

**Goal**
Create a machine-friendly markdown reference for financial statement requirements and formats.

**Inputs**
- [docs/mvp-design.md](docs/mvp-design.md)
- [docs/homebudget.md](docs/homebudget.md)
- [reference/notion/](reference/notion/)

**Process**
- Extract financial statement requirements, formats, and workflows from design docs.
- Identify statement types: income statement, balance sheet, cash flow, budget variance.
- List calculation rules: revenue aggregation, expense categorization, accruals, foreign currency.
- Preserve examples and desired output formats.

**Expected outputs**
- Markdown reference at [docs/financial-statements-spec.md](docs/financial-statements-spec.md)
- Glossary of financial terms and statement line items
- List of ambiguous or incomplete requirements

**Structured prompt**
```
Review the MVP design and reference notes to extract financial statement requirements. Produce a markdown reference covering statement types, line item definitions, calculation rules, and desired output formats. Create a glossary of financial terms used in the project. Note any ambiguous or incomplete sections for clarification.
```

**Autonomy and clarification**
- Safe to determine autonomously: markdown structure, requirements organization, glossary formatting.
- Needs clarification: any statement formats that differ from standard accounting conventions or have special calculation rules.

**Structured ask_questions tool call**
```
ask_questions
questions:
	- header: StatementScope
		question: Which statement types should the MVP design prioritize
		options:
			- label: Income statement and expense detail only
			- label: Income statement plus balance sheet
			- label: Full suite with cash flow and budget variance
```

### Step 2: Data source inventory and gap log

**Goal**
Build a complete inventory of data sources and identify gaps in the design.

**Inputs**
- [reference/hb-finances/homebudget.py](reference/hb-finances/homebudget.py)
- [reference/hb-finances/statements.py](reference/hb-finances/statements.py)
- [docs/google-sheets.md](docs/google-sheets.md)
- [docs/homebudget.md](docs/homebudget.md)
- Output from Step 1

**Process**
- Map homebudget data flows to financial statement inputs.
- Document google-sheets exports and sqlite-gsheet integration points.
- Identify calculation logic currently in the reference code.
- Note gaps between current implementation and desired specifications.

**Expected outputs**
- Data source inventory with mapping to statements.
- Integration points: homebudget SQLite → sqlite-gsheet → Google Sheets.
- Gap log with severity and design impact.
- Notes on existing calculation logic to preserve or refactor.

**Structured prompt**
```
Review the reference implementation and documentation to map data sources to financial statements. Inventory the homebudget data, sqlite-gsheet integration, and google-sheets export flows. Extract calculation logic from the reference code. Produce a gap log listing missing features, incomplete implementations, and design conflicts. Cite specific files and functions.
```

**Autonomy and clarification**
- Safe to determine autonomously: data flow mapping, identification of existing logic, gap identification.
- Needs clarification: any integration behaviors that require user workflow validation.

**Structured ask_questions tool call**
```
ask_questions
questions:
	- header: ExportTarget
		question: Should the design optimize for Google Sheets export or support multiple export formats equally
		options:
			- label: Google Sheets primary, others secondary
			- label: Excel and CSV equal priority
			- label: Pluggable export system
```

### Step 3: Data transformation and calculation rules

**Goal**
Define the data transformation pipeline and financial calculation rules.

**Inputs**
- Output from Step 1
- Output from Step 2
- [reference/hb-finances/homebudget.py](reference/hb-finances/homebudget.py)

**Process**
- Define extraction rules: which homebudget tables and fields feed each statement.
- Specify aggregation logic: category hierarchies, account grouping, currency conversion.
- Document calculation rules: accrual adjustments, expense allocation, budget variance formulas.
- Map homebudget categorization to financial statement line items.

**Expected outputs**
- Data transformation pipeline specification.
- Calculation rules matrix by statement type and line item.
- Currency conversion and multi-entity aggregation rules.
- Notes on dependencies and calculation order.

**Structured prompt**
```
Design the data transformation pipeline and calculation rules. Specify extraction rules for each statement type, aggregation logic tied to homebudget categories, and calculation formulas for accruals, allocations, and variance. Map homebudget data to statement line items. Document currency conversion and any multi-entity aggregation logic.
```

**Autonomy and clarification**
- Safe to determine autonomously: extraction rules, aggregation hierarchy design, formula structure.
- Needs clarification: any non-standard accounting conventions or custom allocation rules specific to the user's workflow.

**Structured ask_questions tool call**
```
ask_questions
questions:
	- header: Aggregation
		question: How should multi-currency transactions be handled in statement aggregation
		options:
			- label: Convert to single reporting currency at transaction date rate
			- label: Separate reporting currency subtotals per currency
			- label: Other, specify rule
```

### Step 4: Financial statement domain model

**Goal**
Define the domain model and data structures for statement generation.

**Inputs**
- Output from Step 1
- Output from Step 3
- [reference/hb-finances/database.py](reference/hb-finances/database.py)

**Process**
- Define domain entities: Statement, LineItem, Account, Category, Currency.
- Specify value objects: Money (amount + currency), Date, Period.
- Design the statement object graph and serialization requirements.
- Map entities to database queries and homebudget schema.

**Expected outputs**
- Domain model class diagram or specification.
- Entity definitions with properties, methods, and invariants.
- Data validation rules and constraints.
- Serialization/deserialization specifications.

**Structured prompt**
```
Design the financial statement domain model. Define entities for Statement, LineItem, Account, Category, and Period. Include value objects for Money and Date. Specify properties, validation rules, and calculation methods. Design the object graph and serialization format.
```

**Autonomy and clarification**
- Safe to determine autonomously: entity properties, value object design, class relationships.
- Needs clarification: any domain rules that differ from standard accounting models or the reference implementation.

### Step 5: Core API surface and module boundaries

**Goal**
Define the Python API and module structure for statement generation and data access.

**Inputs**
- Output from Step 1
- Output from Step 3
- Output from Step 4

**Process**
- Define module boundaries under [src/python](src/python): core, statements, export, utils.
- Specify main client type such as `FinancialStatements` with required methods.
- Define data access patterns: querying, filtering, aggregating.
- Specify export and report generation interfaces.

**Expected outputs**
- API surface list with method signatures.
- Module structure diagram or list.
- Data access patterns and query interfaces.
- Export backend interface and implementations.

**Structured prompt**
```
Using the domain model and calculation rules, design the wrapper API surface and module boundaries. Provide a list of modules, a main client type with CRUD and query method signatures, and data access interfaces. Include export backend interfaces for Google Sheets, Excel, CSV. Align operation names to financial terminology from Step 1.
```

**Autonomy and clarification**
- Safe to determine autonomously: module layout, API method signatures, export interface design.
- Needs clarification: naming conventions when financial terminology conflicts with system terminology.

**Structured ask_questions tool call**
```
ask_questions
questions:
	- header: ApiStyle
		question: Should the API emphasize functional pipelines or class based statement builders
		options:
			- label: Functional pipelines
			- label: Class based builders
			- label: Hybrid approach
```

### Step 6: Statement generation and export strategy

**Goal**
Define workflows for statement calculation, formatting, and export.

**Inputs**
- Output from Step 4
- Output from Step 5
- [docs/mvp-design.md](docs/mvp-design.md)

**Process**
- Define statement generation workflow: extract → transform → calculate → format.
- Specify formatting rules: rounding, precision, sign conventions.
- Design export backends: Google Sheets, Excel, CSV templates.
- Document caching and incremental calculation strategies.

**Expected outputs**
- Statement generation workflow specification.
- Formatting rules by statement type and currency.
- Export backend implementation plan.
- Caching and performance optimization notes.

**Structured prompt**
```
Design the statement generation and export workflow. Specify the extraction → transform → calculate → format pipeline. Include formatting rules for precision, rounding, and sign conventions. Design export backends for Google Sheets, Excel, CSV with template requirements. Note performance optimization and caching strategies.
```

**Autonomy and clarification**
- Safe to determine autonomously: pipeline structure, formatting rules, export interface.
- Needs clarification: any user-specific output formats or template requirements not standard in accounting.

### Step 7: CLI UX and command map

**Goal**
Define the CLI UX, commands, and interaction patterns.

**Inputs**
- Output from Step 5
- [docs/workflow.md](docs/workflow.md)
- Output from Step 1

**Process**
- Define commands: generate, export, list, validate, config.
- Specify input parameters and option flags.
- Design output messages and progress reporting.
- Ensure CLI vocabulary aligns with financial terminology.

**Expected outputs**
- CLI command matrix with examples.
- Input validation and error handling guidelines.
- Output format and progress reporting rules.

**Structured prompt**
```
Design the CLI UX and command map. Include commands for generate, export, list, validate, and config, with required and optional parameters. Align command names and help text to financial terminology. Provide expected output shapes and error handling rules.
```

**Autonomy and clarification**
- Safe to determine autonomously: command structure, parameter specification, output formatting.
- Needs clarification: any user workflow preferences that should be reflected in command design.

### Step 8: Packaging and repository layout

**Goal**
Define packaging layout and repository structure for implementation.

**Inputs**
- Output from Step 5
- [docs/dependencies.md](docs/dependencies.md)
- [docs/repository-layout.md](docs/repository-layout.md)

**Process**
- Define package layout under [src/python](src/python): core, statements, export, cli.
- Identify dependencies on homebudget and sqlite-gsheet.
- Specify CLI entry points and configuration loading.
- Plan version constraints and compatibility matrix.

**Expected outputs**
- Repository layout proposal under [src/python](src/python).
- Packaging and entry point outline.
- Dependency specification and constraints.

**Structured prompt**
```
Propose a packaging layout under src/python with module structure for core, statements, export, cli. Include CLI entry points, configuration loading patterns, and dependency constraints. Specify how the design integrates with homebudget and sqlite-gsheet packages.
```

**Autonomy and clarification**
- Safe to determine autonomously: package layout, entry point design, dependency alignment.
- Needs clarification: any constraints on distribution targets or naming conventions.

**Structured ask_questions tool call**
```
ask_questions
questions:
	- header: Distribution
		question: Which distribution target should the packaging design prioritize
		options:
			- label: Internal use, local install only
			- label: Private package index
			- label: Public PyPI release
```

### Step 9: Testing and validation strategy

**Goal**
Define the testing scope and approach.

**Inputs**
- Output from Step 3
- Output from Step 4
- Output from Step 5

**Process**
- Define test categories: calculation accuracy, data transformation, export formatting, integration.
- Map tests to statement types and calculation rules.
- Specify validation checklist for release.
- Plan test data generation and fixtures.

**Expected outputs**
- Test matrix by feature area.
- Calculation accuracy test specifications.
- Integration test plan.
- Release validation checklist.

**Structured prompt**
```
Define the testing and validation strategy. Provide a test matrix for calculation accuracy, data transformation, export formatting, and integration. Include a release validation checklist. Specify test data generation and fixtures needed.
```

**Autonomy and clarification**
- Safe to determine autonomously: test categories, matrix structure, validation checklist.
- Needs clarification: desired test tooling and any minimum coverage requirements.

### Step 10: Design documentation and rollout

**Goal**
Document the design and update repository docs.

**Inputs**
- Output from Steps 1 through 9
- [docs/repository-layout.md](docs/repository-layout.md)

**Process**
- Draft comprehensive design document with diagrams.
- Update repository layout documentation.
- Create API reference documentation skeleton.
- Produce implementation roadmap.

**Expected outputs**
- Design document draft with architecture diagrams.
- Updated repository layout doc.
- API reference skeleton.
- Implementation roadmap and priorities.

**Structured prompt**
```
Assemble the design document using outputs from prior steps. Include architecture diagrams, domain model visualizations, and calculation rule tables. Update the repository layout doc with the new src/python structure. Create an API reference skeleton. Produce an implementation roadmap.
```

**Autonomy and clarification**
- Safe to determine autonomously: doc structure, diagram types, roadmap sequencing.
- Needs clarification: target audience for design docs and desired level of technical detail.

## Verification

- Manual review of calculation rules against standard accounting conventions and the user's stated workflow.
- Dry walkthrough of CLI commands against the design to ensure statement generation is correct and export formats are valid.
- Validation of data transformation pipeline using sample homebudget data.

## Decisions

- Data source is homebudget SQLite database, accessed via sqlite-gsheet integration.
- Statement types include at minimum: income statement and expense detail.
- All calculations must be reproducible and auditable from raw homebudget data.
- CLI is primary user interface; programmatic API is secondary but must support workflow automation.
- Export targets include Google Sheets as primary, with Excel and CSV as secondary formats.