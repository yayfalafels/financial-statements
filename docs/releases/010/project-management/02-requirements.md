# Project tracking: Requirements

This document tracks the progress of the requirements definition milestone. It is not part of the design documents or the source-of-truth of the requirements, but rather a project management artifact to track the completion of the requirements milestone and its associated tasks.

**Completion criteria**: The requirement should define all of the functional features, custom user-defined business logic required from the user perspective, along with any relevant non-functional requirements. The requirements should be sufficiently complete that the design can proceed with minimal added input and feedback required from the user.

**Out of scope**: Detailed design decisions, implementation details, and test case definitions are out of scope for this milestone. Data migration design and implementation are out of scope for this requirements milestone and are deferred to a later phase milestone. The focus is on what the system should do, not how it should do it.


| seq | id    | status  | task                           |
| --- | ----- | ------- | -------------------------------|
| 01  | 02.10 | closed  | requirements workflow prompt   |
| 02  | 02.11 | closed  | implementation roadmap         |
| 03  | 02.14 | closed  | inspection guide               |
| 04  | 02.01 | closed  | structure and scope boundary   |
| 05  | 02.02 | closed  | workflow orchestration         |
| 06  | 02.04 | closed  | source systems and lineage     |
| 07  | 02.06 | closed  | reconciliation engine          |
| 08  | 02.12 | closed  | cpf integration                |
| 09  | 02.16 | closed  | shared costs                   |
| 10  | 02.03 | closed  | interaction and approvals      |
| 11  | 02.15 | closed  | exception and error handling   |
| 12  | 02.05 | closed  | accounting model and mapping   |
| 13  | 02.07 | closed  | statements lifecycle           |
| 14  | 02.08 | closed  | homebudget integration         |
| 15  | 02.09 | closed  | ibkr integration               |
| 16  | 02.13 | closed  | bill payment                   |
| 17  | 02.17 | closed  | user interfaces                |
| 18  | 02.18 | closed  | financial statements           |
| 19  | 02.19 | closed  | bank statements                |

_02.14 (closed) inspection guide_

- **aim of this step**: define and publish the inspection methodology that requirements work must follow before drafting or resolving requirement content.

Pre-requisite deliverable and boundary:

- primary deliverable path: `.github/skills/data-sources-inspect/SKILL.md`
- this task is methodology-only and does not belong in `docs/requirements.md` or any requirements source-of-truth subtopic documents.
- completion of this step is required before closing `02.01` and proceeding with the main requirements drafting loop.

**02.14 closure conditions, user-validated**

- `.github/skills/data-sources-inspect/SKILL.md` exists and defines inspection methodology for requirements evidence collection.
- references in workflow prompts point to skill `data-sources-inspect`.
- methodology boundaries are explicit: process guidance belongs in develop docs, while requirement statements belong in requirement docs.

02.14 gap resolution subtask table:

| seq | id       | status  | task                             |
| --- | -------- | ------- | -------------------------------- |
| 01  | 02.14.01 | closed  | prompt links verify              |
| 02  | 02.14.02 | closed  | config filename fix              |
| 03  | 02.14.03 | closed  | unreachable code fix             |
| 04  | 02.14.04 | closed  | env reference align              |
| 05  | 02.14.05 | closed  | script location define           |
| 06  | 02.14.06 | closed  | cat_map script fix               |
| 07  | 02.14.08 | closed  | req docs expand                  |
| 08  | 02.14.09 | closed  | primary refs inventory           |
| 09  | 02.14.16 | closed  | primary helper verify            |
| 10  | 02.14.10 | closed  | source coverage matrix           |
| 11  | 02.14.17 | closed  | helper schema expand             |
| 12  | 02.14.18 | closed  | google sheets formula inspector  |
| 13  | 02.14.07 | closed  | stage 2 procedure doc            |
| 14  | 02.14.11 | closed  | statement source inspect         |
| 15  | 02.14.12 | drop    | local inputs inspect             |
| 16  | 02.14.13 | closed  | non-tool source inspect          |
| 17  | 02.14.14 | closed  | source precedence inspect        |

_02.14.01 (closed) prompt links verify_

Not applicable. Prompts do not support markdown or anchor links; backtick path references are the correct format for prompt files. No change required.

_02.14.02 (closed) config filename fix_

Helper schema script references `homebudget_mapping.json`, but the active config in this repository is `homebudget-workbook.json`.

- Align script to use `gsheet/homebudget-workbook.json`.
- Add validation error message listing known config files when missing.
- Closure: script runs and returns successful profile for the `cat_map` region.

_02.14.03 (closed) unreachable code fix_

Script had an early `return None` before a later processing block in `inspect_helper_schemas.py`, leaving the lower block unreachable.

- Refactored to a single deterministic return contract (`list[dict]` region profiling results).
- Removed dead code path and retained explicit success/empty/error result states.
- Verification: `python .dev/scripts/python/inspect_helper_schemas.py` executes successfully (exit code `0`) in `.dev/env`.

_02.14.04 (closed) env reference align_

Environment references must be standardized with explicit zones and usage rules; verify implementations in guide, prompt, and helper scripts:

- `.dev/env` — local environment for helper script development and inspection; required helper dependencies are installed (`homebudget`, `sqlite-gsheet`, `requests`).
- `env/` — main execution environment for git-tracked commissioning, setup, and operational scripts; do not use for helper inspection and development operations.
- `.env` — environment variable storage; do not confuse with execution environment.

Closure criteria: guide, prompt, and helper script headers all reference the same interpreter pattern; environment zones are documented with explicit usage boundaries; verify by running helper scripts with correct environment.

Verification completed: Both helper scripts use standard `#!/usr/bin/env python` shebang. Inspection guide documents `.\env\Scripts\python.exe` as the execution interpreter. Helper script `inspect_hb_categories.py` successfully runs with `env/` venv and returns HomeBudget category data. `.dev/env` dependencies were validated by import checks (`homebudget`, `requests`, `sqlgsheet`) and by CLI execution (`.\.dev\env\Scripts\hb.exe income list`) with exit code `0`. Environment zones are explicitly defined with usage boundaries: `.dev/env` for temporary helper script development (optional), `env/` for main git-tracked scripts, `.env` for environment variables only.

_02.14.05 (closed) script location define_

Script location convention is now enforced.

- Migrated Python scripts to `.dev/scripts/python/*`.
- Migrated Bash scripts to `.dev/scripts/bash/*`.
- Removed deprecated `.dev/.scripts/` directory.
- Removed root-level `.dev/*.py` script placements.
- Updated guide and prompt references to `.dev/scripts/*` paths.

Closure: no scripts are stored in `.dev/` root or `.dev/.scripts/`; script paths are organized by type and documented in active guidance.

_02.14.06 (closed) cat_map script fix_

cat_map script has naming and import drift issues relative to the inspected runtime behavior.

- Normalize to the verified Google Sheets inspection stack used in this repo.
- Correct typos; ensure output includes column list, row count, and sample rows.
- Closure: one command executes script successfully and returns cat_map schema evidence.

_02.14.08 (closed) req docs expand_

`docs/requirements/homebudget.md` and `docs/requirements/google-sheets.md` provide only minimal overview text and do not capture project-specific inspection procedures.

- the correct location to find detailed instruction is the skill guides for `homebudget` and `gsheet-inspect`
- update all references to point to the skill guides as the source of truth for inspection procedures and implementation details.
- update the skill documents in case of any ambiguity or missing information to ensure sufficient detail is available to navigate and use these tools effectively.
- for any other tools, create new skills in `.github/skills/` with usage instructions, examples, and troubleshooting tips.
- for source data references which are not tools, create a guide in `docs/develop/data-sources/*`

Completion notes:

- `docs/requirements/homebudget.md` and `docs/requirements/google-sheets.md` now explicitly direct procedural inspection and implementation details to skill `homebudget` and `gsheet-inspect`.
- Skill references were aligned and clarified for project-specific source-of-truth boundaries.
- Source-data guides were added for non-tool references:
	- `docs/develop/data-sources/homebudget-source-data.md`
	- `docs/develop/data-sources/google-sheets-source-data.md`

_02.14.09 (closed) primary refs inventory_

Current inspection guidance in skill `data-sources-inspect` is centered on HomeBudget and Google Sheets. For POC requirements development, additional primary references are in scope and must be explicitly inventoried for inspection readiness.

- Build a canonical inventory of POC primary references at `docs/develop/data-sources/inventory.md` used by requirements, including system, artifact path, and usage intent.
- Include at minimum: HomeBudget DB and config, helper and legacy workbooks in `gsheet/*.json`, statement source artifacts, local JSON inputs in `data/monthly-closing/*`, and relevant reference repositories in `reference/*`.
- Closure: inventory is published at `docs/develop/data-sources/inventory.md` and usage updated in skill `data-sources-inspect` with explicit path-level references and no ambiguous source labels.

Completion notes:

- Inventory published at `docs/develop/data-sources/inventory.md` covering 27 primary references across HomeBudget, Google Sheets workbooks, statement sources, local inputs, and reference repositories.
- Skill `data-sources-inspect` updated: `docs/develop/data-sources/inventory.md` added to Related Documentation; Key configs list expanded to all 7 `gsheet/` workbook configs with explicit path-level references.

_02.14.16 (closed) primary helper verify_

Skill `gsheet-inspect` defines `.dev/scripts/python/inspect_helper_schemas.py` as the primary helper workbook schema inspection tool. This task verifies that primary-helper procedure is executable and produces expected schema evidence.

- Run `.\env\Scripts\python.exe .dev\scripts\python\inspect_helper_schemas.py`.
- Confirm output includes workbook schema profiling for helper sources, including `homebudget-workbook` / `cat_map` evidence.
- Confirm output includes row and column profile evidence required for requirements inspection notes.
- Closure: one command executes primary helper successfully and returns schema evidence aligned with skill `gsheet-inspect` guidance.

Completion notes:

- Verified command succeeded: `.\env\Scripts\python.exe .dev\scripts\python\inspect_helper_schemas.py`
- Output included helper workbook schema profiling for `ibkr-iba`, `cpf`, and `homebudget-workbook`.
- Output included `cat_map` evidence: `Shape: 181 rows, 10 columns`, inferred column list, and first-row sample.

_02.14.10 (closed) source coverage matrix_

The current skill does not provide a complete matrix showing inspection procedure coverage across all POC primary references.

- Add a source-to-procedure matrix in skill `data-sources-inspect`.
- For each primary reference, map required inspection steps, expected outputs, and linked scripts or commands.
- Flag unresolved references with explicit gaps instead of implicit omission.
- Closure: every POC primary reference has a clear inspection procedure mapping or an explicit deferred rationale.

Source coverage assessment table:

| seq | id          | status  | category         | item                 | procedure          | task     |
| --- | ----------- | ------- | ---------------- | -------------------- | ------------------ | -------- |
| 01  | 02.14.10.01 | closed  | HomeBudget       | homebudget.db         | homebudget skill   | —        |
| 02  | 02.14.10.02 | closed  | HomeBudget       | hb-config.json        | homebudget skill   | —        |
| 03  | 02.14.10.03 | closed  | Google Sheets    | ibkr-iba.json         | gsheet + script    | —        |
| 04  | 02.14.10.04 | closed  | Google Sheets    | cpf.json              | gsheet + script    | —        |
| 05  | 02.14.10.05 | closed  | Google Sheets    | homebudget-workbook   | gsheet + script    | —        |
| 06  | 02.14.10.06 | closed  | Google Sheets    | financial-statements  | gsheet only        | —        |
| 07  | 02.14.10.07 | closed  | Google Sheets    | cash-expenses.json    | gsheet only        | —        |
| 08  | 02.14.10.08 | closed  | Google Sheets    | shared-expenses.json  | gsheet only        | —        |
| 09  | 02.14.10.09 | closed  | Google Sheets    | closing-session.json  | gsheet only        | —        |
| 10  | 02.14.10.10 | closed  | Statement sources | statements (10)       | guide + script     | —        |
| 11  | 02.14.10.11 | drop    | Local inputs     | inputs (6)            | out of process scope | —      |
| 12  | 02.14.10.12 | closed  | Reference repos  | repositories (2)      | guide + script     | —        |

Coverage legend:

- `gsheet + script` — explicitly listed in skill config table and covered by `inspect_helper_schemas.py`.
- `gsheet only` — listed in skill config table with documented methodology; direct API pattern in skill applies.
- `no config` — not listed in skill config or script; gsheet methodology applies but requires explicit addition.
- `homebudget skill` — covered by `homebudget` skill, not applicable for gsheet-inspect.
- `deferred` — no skill or script defines an inspection path; addressed by cited downstream task.

_02.14.17 (closed) helper schema expand_

The primary helper schema inspection script (`inspect_helper_schemas.py`) covers ibkr-iba, cpf, and homebudget-workbook sources. Four additional Google Sheets sources (financial-statements, cash-expenses, shared-expenses, closing-session) currently require manual direct API usage.

- Either expand `inspect_helper_schemas.py` to include these four sources, or create a dedicated supplementary script for them.
- Ensure both covered and deferred sources have clear paths to procedural guidance in the skill.
- Closure: helper-source schema inspection can be executed with a single command or small script set without manual config lookup.

Sources requiring schema coverage expansion:

| seq | id           | status  | source               |
| --- | ------------ | ------- | -------------------- |
| 01  | 02.14.17.01  | closed  | financial-statements |
| 02  | 02.14.17.02  | closed  | cash-expenses        |
| 03  | 02.14.17.03  | closed  | shared-expenses      |
| 04  | 02.14.17.04  | closed  | closing-session      |

_02.14.17.02 (closed) cash-expenses_

- helper-schema coverage for `cash-expenses` is executable using the existing helper script set via `profile_workbook.py`, without requiring manual direct API calls.
- command path for repeatable schema profiling: `./env/Scripts/python.exe .dev/scripts/python/profile_workbook.py gsheet/cash-expenses.json`.
- mapping alignment completed for this subtask intent:
	- skill `gsheet-inspect` now documents `profile_workbook.py` as a supplementary mapped helper path for `cash-expenses.json`.
	- `docs/develop/data-sources/google-sheets-source-data.md` now includes explicit helper-script mapping for `cash-expenses.json`.
- scoped decision: no changes were made to `inspect_helper_schemas.py` in this subtask to avoid overlap with concurrent work on `02.14.17.01`.

_02.14.17.03 (closed) shared-expenses_

- helper-schema coverage for `shared-expenses` is now integrated in the primary batch helper script `inspect_helper_schemas.py`.
- command path for repeatable batch schema profiling: `./env/Scripts/python.exe .dev/scripts/python/inspect_helper_schemas.py`.
- verification evidence captured from batch command output:
	- workbook section: `SHARED EXPENSES WORKBOOK SCHEMA`
	- profiled region: `records`
	- schema evidence: `8 columns`, `339 rows`
- mapping alignment completed for this subtask intent:
	- skill `gsheet-inspect` documents `inspect_helper_schemas.py` as the primary batch helper path.
	- `docs/develop/data-sources/google-sheets-source-data.md` maps `shared-expenses.json` to `inspect_helper_schemas.py`.

_02.14.17.04 (closed) closing-session_

- helper-schema coverage for `closing-session` is now integrated in the primary batch helper script `inspect_helper_schemas.py`.
- command path for repeatable batch schema profiling: `./env/Scripts/python.exe .dev/scripts/python/inspect_helper_schemas.py`.
- verification evidence captured from batch command output:
	- workbook section: `CLOSING SESSION WORKBOOK SCHEMA`
	- profiled region: `sessions`
	- schema evidence: `12 columns`, `1560 rows`
- mapping alignment completed for this subtask intent:
	- skill `gsheet-inspect` documents `inspect_helper_schemas.py` as the primary batch helper path.
	- `docs/develop/data-sources/google-sheets-source-data.md` maps `closing-session.json` to `inspect_helper_schemas.py`.

_02.14.18 (closed) google sheets formulas_

Design and develop a utility tool `gsheet-formulas` which extends full CRUD capabilities for Google Sheets cell formulas. 

The tool, in python runtime, using the Google Sheets API, can retrieve, edit, create a google sheet formulas given:

1. client_secret json file corresponding to a GAS IAM automation account
2. workbook id ie `1ijbXG_wEP_icWH7xtbIO0bNVp4RbWPe1A5X1Q1i1nIo`
3. cell range ie `A34`

target outputs

 - requirements `docs/tools/gsheet-formulas/requirements.md`
 - user guide `docs/tools/gsheet-formulas/user-guide.md`
 - design document `docs/tools/gsheet-formulas/design.md`
 - task tracking doc `docs/develop/010/project-management/gsheet-formulas.md`
 - development workflow `.github/prompts/gsheet-formulas.prompt.md`
 - source code `src/gsheet-formulas/*`

Completion notes:

- `gsheet-formulas` baseline delivery is complete across requirements, design, source, tests, SIT, and UAT evidence in `docs/develop/010/project-management/gsheet-formulas.md`.
- Batch formula CRUD capability was delivered and SIT-validated, with implementation and usage documented in `docs/tools/gsheet-formulas/design.md` and `docs/tools/gsheet-formulas/user-guide.md`.
- Capability set now available for follow-on inspection workflows:
	- single and batch formula reads for workbook ranges
	- single and batch formula writes and clears for controlled test ranges
	- deterministic audit artifacts for mutation traceability

Closure decision for this tracker scope:

- `02.14.18` is closed in the requirements tracker; downstream batch enhancement/UAT tracking remains in `docs/develop/010/project-management/gsheet-formulas.md`.

_02.14.07 (closed) stage 2 procedure doc_

The txn category mapping from `GL` → `financial statements` is identified as embedded in legacy reconcile sheets, but the extraction method and source locations are not yet defined step-by-step.

- Add procedure subsection to the inspection guide: where Stage 2 lives and how to extract it.
- Include required artifacts and validation checks for parity after extraction.
- Closure: reader can reproduce Stage 2 mapping extraction without relying on chat history.

Closure decision:

- `02.14.07` is closed after parity gates were defined, implemented, and
	recorded in reproducible artifacts.

02.14.07 subtask table:

| seq | id          | status  | task                      |
| --- | ----------- | ------- | ------------------------- |
| 01  | 02.14.07.01 | closed  | locate stage 2 sources    |
| 02  | 02.14.07.02 | closed  | inspect fs gsheet schemas |
| 03  | 02.14.07.03 | closed  | create fs-gsheet guide    |
| 04  | 02.14.07.04 | closed  | write stage 2 procedure   |
| 05  | 02.14.07.05 | closed  | define parity checks      |

_02.14.07.01 (closed) locate stage 2 sources_

The Stage 2 GL → financial statements category mapping exists in two forms: a structured region in the `financial-statements.json` gsheet workbook (`fin_expense_cat_map` sheet, range `fin_expense_cat_map!A1:E500`), and embedded row labels in the legacy `reconcile.csv` net-assets section (rows ~305–367). A third candidate is the `accounts` sheet in the same workbook, which may carry GL account to balance-sheet category assignments.

- Confirm all locations where Stage 2 mapping is defined or derived: `fin_expense_cat_map`, `accounts` sheet, and reconcile structure row labels.
- Identify whether the gsheet `fin_expense_cat_map` region is the authoritative extracted form or still a partial extraction of the legacy reconcile structure.
- Confirm which mapping dimensions are covered (income statement expense lines, balance sheet lines, or both).
- Closure: a definitive source list for Stage 2 is documented with coverage dimensions noted.

Completion notes:

- Confirmed Stage 2 workbook source paths from `gsheet/financial-statements.json`:
	- `fin_exp_cat_map` mapped to `fin_expense_cat_map!A2:E500` with header `A1:E1`
	- `accounts` mapped to `accounts!A2:G500` with header `A1:G1`
- Confirmed legacy reconcile structural labels are present in `data/financial-statements-reconcile/reconcile.csv` under the net-assets and classification blocks, including labels such as `expenses`, `active income`, `other income`, and `capital gain/loss`.
- Source coverage decision:
	- Income-statement mapping path: `fin_expense_cat_map` + reconcile labels.
	- Balance-sheet mapping path: `accounts` + reconcile labels.

02.14.18 capability application notes for 02.14.07:

- Apply `batch-read` from `gsheet-formulas` to inspect formula presence and dependency patterns across Stage 2 mapping regions without manual per-cell calls.
- Apply `read` for targeted cell-level verification where specific mapping formulas must be traced to sheet logic.
- Use mutation capabilities (`batch-create`, `batch-update`, `batch-clear`) only in controlled test ranges to prototype parity-check helper formulas before codifying checks in the inspection procedure.
- Reuse audit outputs from formula mutation tests as reproducibility evidence when documenting Stage 2 extraction and parity validation methodology.

_02.14.07.02 (closed) inspect fs gsheet schemas_

Schema evidence for the `financial-statements.json` workbook is not yet captured with column list, row count, and sample rows.

- Run gsheet inspection on the `fin_expense_cat_map` region (`fin_expense_cat_map!A1:E500`).
- Run gsheet inspection on the `accounts` region (`accounts!A1:G500`).
- Capture column names, row counts, and first-row samples for both regions as inspection evidence.
- Closure: schema evidence for both regions is captured and can be cited in the guide and skill.

Completion notes:

- Added first-pass helper script `.dev/scripts/python/inspect_stage2_sources.py` and generated artifact `.dev/.artifacts/stage2_sources_inspection.json`.
- Captured Stage 2 workbook schema evidence from `gsheet/financial-statements.json`:
	- `fin_exp_cat_map` (`fin_expense_cat_map!A2:E500`): `33` rows, `5` columns.
	- `accounts` (`accounts!A2:G500`): `29` rows, `7` columns.
- Captured header and first-row evidence:
	- `fin_exp_cat_map` headers: `fin_stm_category`, `COLE`, `fa_category`, `fa_subcategory`, `custom logic`.
	- `fin_exp_cat_map` first row sample includes `fin_stm_category=food`, `fa_category=01 food`.
	- `accounts` headers: `id`, `type`, `owner`, `name`, `currency`, `HB account`, `stm account`.
	- `accounts` first row sample includes `id=TWH CASH SGD`, `name=CASH`, `HB account=Cash TWH SGD`.
- Added second-pass helper `.dev/scripts/python/inspect_stage2_reconcile_deep_pass.py` and artifact `.dev/.artifacts/stage2_reconcile_deep_pass.json` to support deeper legacy-to-workbook comparison for downstream `02.14.07.03` through `02.14.07.05`.

_02.14.07.03 (closed) create fs-gsheet guide_

No dedicated guide exists for the `financial-statements.json` workbook structure, its sheet regions, and their role in Stage 2 mapping.

- Create `docs/develop/data-sources/financial-statements-gsheet.md`.
- Document workbook id, all defined regions (balances, forex_rates, accounts, fin_expense_cat_map), their range notation, column schemas, and row count evidence from `02.14.07.02`.
- Highlight the Stage 2 mapping role of `fin_expense_cat_map` and `accounts` with notes on coverage dimensions (income statement vs balance sheet).
- Cross-reference the legacy `reconcile.csv` structure as the source this region was extracted from.
- Closure: guide is published and referenced from skill `data-sources-inspect` related documentation.

work completed:

- Expanded `docs/develop/data-sources/financial-statements-gsheet.md` from a narrow four-region schema note into a full workbook guide covering all `27` configured regions in `gsheet/financial-statements.json`.
- Added live evidence for the bridge, reconcile, and final-output layers using `.dev/.artifacts/financial_statements_workbook_inspection.json`.
- Added formula-level evidence using `.dev/.artifacts/financial_statements_formula_samples.json`.
- Documented the current transformation topology:
	- `hb_exp and hb_inc and hb_xfr and stm_txns -> hb_gl -> reconcile_fin_stm_summary -> income_statement`
	- `fin_exp_cat_map -> hb_gl -> reconcile_exp_cost_centers`
	- `accounts and balances and forex_rates -> reconcile_bal_by_acct -> balance_sheet`
	- cash and FX support paths through `reconcile_cash_*`, `reconcile_fx_m2m_summary`, and related private-detail regions.
- Added direct sqlgsheet formula inspection method to `docs/develop/data-sources/financial-statements-gsheet.md` with live examples:
	- `income_statement!D4 =sum(D6:D8)`
	- `balance_sheet!D4 =bal_sht_prior_year!P4`
	- `reconcile!H4 =H18+H31*G1`
- Captured residual gaps for follow-on parity work instead of leaving the guide incomplete:
	- `hb_exp` header and column count mismatch
	- formula-level lineage inside `reconcile` still to be formalized by parity criteria
	- legacy labels and normalized mapping labels are not direct one-to-one matches

Prerequisite review for moving to `02.14.07.04`:

- Required guide enhancements for `02.14.07.03` are complete, including formula extraction guidance and sample evidence.
- Skill `data-sources-inspect` now references the formula helper command and formula artifact.
- No blocking pre-requisites remain for `02.14.07.04`; proceed with procedure hardening and reproducibility checks.

_02.14.07.04 (closed) write stage 2 procedure_

The Stage 2 section in skill `data-sources-inspect` is a stub: source is noted as legacy reconcile sheets and status is marked partial.

- Replace the stub with a step-by-step extraction procedure: which config file, which sheet range, which API call, and what output to capture.
- Add separate sub-steps for income-statement expense mapping (via `fin_expense_cat_map`) and balance-sheet account classification (via `accounts` sheet).
- Reference `docs/develop/data-sources/financial-statements-gsheet.md` as the companion schema reference.
- Closure: a reader can reproduce Stage 2 extraction with one set of commands and without relying on chat history.

Work completed:

- Replaced the Stage 2 stub in `.github/skills/data-sources-inspect/SKILL.md` with a reproducible command sequence using:
	- `.dev/scripts/python/inspect_stage2_sources.py`
	- `.dev/scripts/python/inspect_stage2_reconcile_deep_pass.py`
	- `.dev/scripts/python/inspect_financial_statements_workbook.py`
	- `.dev/scripts/python/inspect_financial_statements_formulas.py`
- Added an explicit extraction workflow covering:
	- source region identification from `gsheet/financial-statements.json`
	- source-feed normalization through `hb_exp`, `hb_inc`, `hb_xfr`, and `stm_txns`
	- expense mapping through `fin_exp_cat_map`, `hb_gl`, and reconcile summaries
	- balance-sheet classification through `accounts`, `balances`, `forex_rates`, and reconcile summaries
	- supporting cash, FX, transfer, and private-income reconcile detail regions
	- formula extraction targets for representative rollup and output cells
- Added direct sqlgsheet method and live formula samples as reproducible evidence for the formula extraction workflow.
- Added required evidence outputs and completion criteria so a reader can reproduce the inspection workflow without relying on chat history.
- Recorded the current live anomalies and parity gaps instead of hiding them in the procedure text.

pending open tasks

- No additional blocker remains for `02.14.07.04` closure.
- Remaining open work is intentionally deferred to `02.14.07.05` parity checks:
	- formalize parity criteria for `hb_exp` header and column mismatch handling
	- define pass and fail rules for formula-lineage parity in reconcile regions
	- define parity strategy for normalized mapping labels versus legacy labels

_02.14.07.05 (closed) define parity checks_

Parity validation criteria are now explicit and reproducible for confirming that
the extracted Stage 2 mapping is complete enough for requirements-phase use.

- Define minimum parity checks: GL account coverage (all GL accounts in ledger have a Stage 2 mapping entry), duplicate key detection, and null category detection.
- Define the comparison path: `fin_expense_cat_map` column set compared against GL account list from HomeBudget or the `accounts` sheet.
- Add checks to the skill and guide so a reader knows when extraction is sufficient.
- Formalize parity criteria for `hb_exp` header and column mismatch handling.
- Define pass and fail rules for formula-lineage parity in reconcile regions.
- Define parity strategy for normalized mapping labels versus legacy labels.
- Closure: parity checks are explicit and reproducible against a known good reference period.

Work completed:

- Added parity helper script `.dev/scripts/python/inspect_stage2_parity_checks.py`.
- Generated artifact `.dev/.artifacts/stage2_parity_checks.json` using:
	- `stage2_sources_inspection.json`
	- `stage2_reconcile_deep_pass.json`
	- `financial_statements_workbook_inspection.json`
	- `financial_statements_formula_samples.json`
- Added Stage 2 parity procedure and gates to:
	- `.github/skills/data-sources-inspect/SKILL.md`
	- `docs/develop/data-sources/financial-statements-gsheet.md`
- Implemented and recorded parity gates for:
	- GL account coverage definition
	- mapping duplicate and null checks
	- `hb_exp` shape classification
	- formula-lineage parity across `income_statement`, `balance_sheet`, and `reconcile`
	- normalized-versus-legacy structural coverage parity
- Current parity evidence outcome: summary status `pass` (`5/5` checks passing).
- `hb_exp` parity classification outcome: `expected_sparse_trailing_column`.
- Formula-lineage parity outcome: `pass` with required rollup sheets present.

- `hb_exp` shape anomaly must be classified as expected sparse behavior or config defect before parity can pass.
- Formula-lineage parity must include at least one reproducible formula-token sample per key rollup layer.
- Legacy and normalized label parity must use structural or coverage-based checks, not direct string equality alone.

Closure decision:

- `02.14.07.05` is closed. Remaining future enhancement is optional strict
	row-level GL account coverage export; current domain-based parity gate is
	sufficient for requirements-phase reproducibility.

_02.14.11 (closed) bank statement source inspect_

POC scope includes bank statement-driven workflows and CSV-based imports. Statement-source inspection procedure is now defined with reproducible script and evidence artifacts.

**Account scope — statement digital twin path**

The statement digital twin covers four PDF-backed bank accounts only. IBKR, CPF, and balance-only accounts are outside this path and must not be treated as `stm_txns` sources.

| id | account_name        | s3_account_id               | db_table           | currency |
| -- | ------------------- | --------------------------- | ------------------ | -------- |
| 01 | TWH DBS Multi SGD   | 02_dbs_savings_sgd          | TWH_DBS_MULTI_SGD  | SGD      |
| 02 | TWH CITI            | 04_citibank_personal        | TWH_CITI_USD       | USD      |
| 03 | TWH UOB One SGD     | 03_uob_one_visa             | TWH_UOB_ONE_SGD    | SGD      |
| 04 | TWH Visa USD        | 06_bank_of_america_visa_usd | TWH_BOA_TRAVEL_USD | USD      |

**Lineage overview**

- Raw statement files: PDF downloads stored at user filesystem paths defined in `statement_config.json`.
- Ingestion script: `reference/hb-finances/statements.py` parses PDFs into `statements.db`.
- Statement digital twin: `reference/hb-finances/statements.db` — SQLite database with per-account tables and a merged `GL` table.
- Period aggregate: `stm_txns` region in the financial statements workbook aggregates GL rows per account per month, same grain as `hb_exp`, `hb_inc`, and `hb_xfr`.
- Reconciliation link: the `stm account` field in the `accounts` gsheet region maps each account to its `statements.db` table.

**statements.db tables**

| id | table_name          | rows  | type                                   |
| -- | ------------------- | ----- | -------------------------------------- |
| 01 | TWH_DBS_MULTI_SGD   | 1200  | POC account — 8 cols including DBS ext |
| 02 | TWH_CITI_USD        | 161   | POC account — 3 cols                   |
| 03 | TWH_UOB_ONE_SGD     | 2004  | POC account — 3 cols                   |
| 04 | TWH_BOA_TRAVEL_USD  | 288   | POC account — 3 cols                   |
| 05 | GL                  | 4967  | merged ledger — all accounts combined  |
| 06 | balances            | 328   | month-end balances by account          |
| 07 | COMMON_UOB_SGD      | 241   | legacy — outside current POC scope     |
| 08 | TWH_DBS_Visa_SGD    | 1074  | legacy — outside current POC scope     |

**Deliverables**

- Update `data-sources-inspect` with a dedicated section for bank statement-source inspection.
- Create `docs/develop/data-sources/bank-statements-source-data.md` covering account scope, statements.db schema, transaction field schema, stm_txns linkage, and inspection procedure.
- Create helper script `.dev/scripts/python/inspect_statements_db.py` to extract schema, row counts, and sample data from the reference database.
- Define minimum checks: all four POC account tables present, GL table nonzero, core fields present, no null amounts in samples.
- Closure: a reader can reproduce bank statement-source inspection and capture evidence without relying on chat history.

Completion notes:

- Skill updated: `.github/skills/data-sources-inspect/SKILL.md` now includes section `Bank Statement Source Inspection` with account scope, command, checks, and schema reference.
- Guide created: `docs/develop/data-sources/bank-statements-source-data.md` includes anchor-linked contents, scope boundary, schema, lineage, checks, and anomalies.
- Helper script created: `.dev/scripts/python/inspect_statements_db.py`.
- Evidence artifact generated: `.dev/.artifacts/statements_db_inspection.json`.
- Verified reproducible command success:
	- `\.\env\Scripts\python.exe .dev\scripts\python\inspect_statements_db.py`
- Verified key evidence from artifact and command output:
	- four POC account tables present
	- `GL` present with `4967` rows
	- `balances` present with `328` rows
	- core fields present in account tables: `date`, `description`, `amount`

Closure decision:

- `02.14.11` is closed. Statement-source inspection is now deterministic and reproducible without chat history.

_02.14.12 (drop) local inputs inspect_

Sample JSON and CSV files in `data/monthly-closing/` are sample template examples of how user inputs can be managed in the interim POC before the web ui is available.  The exact format of these are an output from a later stage during the design and are not considered a primary source of truth for requirements.

_02.14.13 (closed) non-tool source inspect_

Several POC primary references are non-tool sources, for example source material under `reference/*` and procedure context previously captured in non-runtime artifacts. File inventory alone is not sufficient, so this scope now includes explicit interpretation guidance tied to monthly closing behavior.

- Add explicit inspection procedure for non-tool primary references used in requirements decisions.
- Define how to extract and cite evidence from `reference/hb-finances/*`, `reference/hb-reconcile/*`, and `reference/notion-bills/*` with reproducible trace notes.
- Define boundaries for informational references versus source-of-truth operational references.
- Closure: non-tool primary-reference inspection steps are explicit and reproducible.

Completion notes:

- Guide created: `docs/develop/data-sources/non-tool-source-data.md`.
- Skill updated: `.github/skills/data-sources-inspect/SKILL.md` includes section `Non-Tool Source Inspection`.
- Helper script created: `.dev/scripts/python/inspect_non_tool_sources.py`.
- Evidence artifact generated: `.dev/.artifacts/non_tool_sources_inspection.json`.
- Verified command success:
	- `.\env\Scripts\python.exe .dev\scripts\python\inspect_non_tool_sources.py`
- Verified evidence summary:
	- `reference/hb-finances` files: `23`
	- `reference/hb-reconcile` files: `26`
	- `reference/notion-bills` files: `7`

Interpretation findings added:

- `reference/hb-finances` is a legacy integration reference for statement ingestion and posting flow:
	- `statement_config.json` maps account names to source paths and table names
	- `statements.py` defines statement normalization and GL posting flow
	- `statements.db` is the reference statement digital twin model
- `reference/hb-reconcile` is a legacy reconciliation reference:
	- `docs/reconcile.md` defines the gap equation and edit model
	- reconciliation core logic uses exact amount plus date-tolerance matching and edit reduction heuristics
	- account-specific tolerances are configured in `account_settings/txn_heuristics.json`
- `reference/notion-bills` is a legacy process export reference for bill-payment workflow behavior:
	- `Bills 15ac378f707580ee8fe2e596ca250260.md` indexes exported bill datasets
	- `bills 16ec378f707580fabf99f572568f5f60.csv` records bill-level amount, paid, payee, and payment_date fields
	- `billing_period 16ec378f707580d7b472d37487ec8127.csv` tracks monthly bill-count and paid-count rollups
	- `bill_payee 16ec378f707580e2ae93e4173891d72c.csv` captures recurring payee groupings
- Monthly-closing relevance:
	- use these repositories as design-pattern references for ingestion, reconciliation, and bill-payment workflow behavior
	- do not treat them as authoritative runtime source of truth over current operational data

Scope resolution:

- user decision captured via `vscode_askQuestions`: `hb-reconcile` is legacy reference only and not a required baseline behavior contract for current design.

Closure decision:

- `02.14.13` is closed. Non-tool source inspection now includes interpretation, monthly-closing relevance, extractable logic anchors, and explicit boundary policy across `hb-finances`, `hb-reconcile`, and `notion-bills`.

_02.14.14 (closed) source precedence inspect_

Requirements call for deterministic source precedence, Inventory the sources and define their precedence relationships for each data domain (e.g. category mapping, GL accounts, cash transactions).

- Guide created: `docs/develop/data-sources/source-precedence-inventory.md`.
- Skill updated: `.github/skills/data-sources-inspect/SKILL.md` includes section `Source Precedence Inventory`.

_02.01 (closed) structure and scope boundary_

**aim of this step**: determine the structure and scope of requirements. break-up into the sub tasks of the parent 02-requirements development workflow.

requirements documentation

- main target `docs/requirements.md`
- with descriptive references to sub topics at `docs/requirements/*`

**02.01 closure conditions, user-validated**

- draft outline documented at `docs/requirements.md`
- structure is accepted as the working requirement architecture for the milestone.
- each task in the parent table for 02-requirements has a distinct user outcome and acceptance boundary for a target are of requirements documents.
- CPF and bill payment areas are explicitly included in POC scope and tracking.
- data migration is explicitly excluded from this requirements milestone scope and tracked in the dedicated data migration milestone.
- 02.01 conflicts and gaps analysis does not define exception and error policies; those requirement statements are owned by dedicated task `02.15`.
- **closure gate**: keep task open until user validates the structure above.

| seq | id       | status  | task                                   |
| --- | -------- | ------- | -------------------------------------- |
| 01  | 02.01.01 | closed  | conflicts and gap resolution           |
| 02  | 02.01.02 | closed  | requirements scope outline             |
| 03  | 02.01.04 | closed  | requirements docs inventory            |
| 04  | 02.01.03 | closed  | scope requirements tasks               |

_02.01.01 (closed) conflicts and gaps resolution_

- identify any open conflicts gaps in the current requirements documentation `docs/requirements/*`
- document at `docs/develop/010/data-sources/requirements-conflicts-and-gaps.md`

type of gaps and conflicts to identify:

- conflicts between data sources and requirements documents
- information unavailability, gaps in data sources, genuine open ambiguity given what is already made avaiable in the inventory and inspection steps
- documentation gap, gaps between what should be included in requirements, and what is currently documented in `docs/requirements/*`
- do not define exception or error handling policies in this step; capture ownership handoff only

work completed:

- gap analysis documented at `docs/develop/010/data-sources/requirements-conflicts-and-gaps.md`
- published workflow owner pages for orchestration, approvals, and statements lifecycle
- published accounting hierarchy inheritance and override boundaries
- published bill-payment and shared-cost boundaries and lifecycle-link ownership
- published canonical requirements owner index in `docs/requirements.md`
- published missing owner pages for category mapping and reconciliation engine
- published policy alignment direction for tolerance and canonical account naming
- confirmed exception and error policy ownership remains in dedicated task `02.15`

| seq | id          | status  | task                                  |
| --- | ----------- | ------- | ------------------------------------- |
| 01  | 02.01.01.01 | closed  | gap identification                    |
| 02  | 02.01.01.02 | closed  | cf 01 workflow ownership overlap      |
| 03  | 02.01.01.03 | closed  | cf 02 accounting ownership overlap    |
| 04  | 02.01.01.04 | closed  | cf 03 bill shared cost dual ownership |
| 05  | 02.01.01.05 | closed  | dg 01 empty requirements index        |
| 06  | 02.01.01.06 | closed  | dg 02 missing lineage page            |
| 07  | 02.01.01.07 | closed  | dg 03 missing category mapping page   |
| 08  | 02.01.01.08 | closed  | dg 04 missing reconcile engine page   |

_02.01.01.01 (closed) gap identification_

identify open conflicts and gaps in current requirements documentation.

actions taken:

- reviewed current requirement and source-reference documents
- recorded conflicts and documentation gaps in
	`docs/develop/010/data-sources/requirements-conflicts-and-gaps.md`

work completed:

- conflict, documentation-gap, and misalignment inventory is published

_02.01.01.02 (closed) cf 01 workflow ownership overlap_

workflow destination is unclear

actions taken:

- created `docs/requirements/workflow-orchestration.md`
- created `docs/requirements/interaction-approvals.md`
- created `docs/requirements/statements-lifecycle.md`
- updated `docs/requirements/current-workflow.md` as context-only page with
	owner-page references

work completed:

- workflow ownership split is now published and destination coverage is defined

_02.01.01.03 (closed) cf 02 accounting ownership overlap_

accounting rule authority is duplicated

actions taken:

- published accounting ownership hierarchy in
	`docs/requirements/accounting-logic.md`
- published integration inheritance and override boundaries in
	`docs/requirements/ibkr-integration.md` and
	`docs/requirements/cpf-integration.md`

work completed:

- accounting hierarchy and override boundaries are documented
- status closed by user validation

_02.01.01.04 (closed) cf 03 bill shared cost dual ownership_

one area has competing primary docs 

actions taken:

- published bill-payment primary scope, lifecycle, and reconciliation contracts
	in `docs/requirements/bill-payment.md`
- published shared-cost primary scope, field contracts, parameter constraints,
	consumption baseline, and lifecycle-link ownership in
	`docs/requirements/shared-costs.md`

work completed:

- bill and shared-cost dual ownership conflict is resolved in documentation
- status closed by user validation

_02.01.01.05 (closed) dg 01 empty requirements index_

no canonical ownership index

actions taken:

- created canonical requirements ownership index in `docs/requirements.md`
- added cross-page ownership rules and source-of-truth boundaries

work completed:

- ownership index is published and linked to owner pages
- status closed by user validation

_02.01.01.06 (closed) dg 02 missing lineage page_

closed. canonical lineage page now exists at `docs/requirements/source-systems-lineage.md`; residual scope moved forward to `02.01.04 requirements docs inventory` for cross-link and owner-index alignment.

actions taken:

- lineage owner-linkage is now reflected in the canonical owner index

work completed:

- no further change required in this subtask scope

_02.01.01.07 (closed) dg 03 missing category mapping page_

mapping requirements are incomplete

actions taken:

- created `docs/requirements/transaction-category-mapping.md`
- published stage ownership, completeness gate, and event-driven boundary

work completed:

- category mapping owner page is now published
- status closed by user validation

_02.01.01.08 (closed) dg 04 missing reconcile engine page_

reconcile ownership is split elsewhere

actions taken:

- created `docs/requirements/reconciliation-engine.md`
- published reconcile workflow checkpoints, tolerance policy ownership,
	and closure criteria
- aligned tolerance publication in `docs/requirements/cash-reconcile.md` to
	glossary policy

work completed:

- reconcile owner page is now published and linked
- status closed by user validation

_02.01.02 (closed) requirements scope outline_

| id           | status  | task                                                                  |
| ------------ | ------- | --------------------------------------------------------------------- |
| 02.01.02.01  | closed  | draft outline                                                         |
| 02.01.02.02  | closed  | refinement from current requirements state and data source inspection |

**draft requirements outline**

| id  | section                                | description                                                                                 |
| --- | -------------------------------------- | ------------------------------------------------------------------------------------------- |
| 01  | release boundary and success gate      | defined by roadmap and POC docs; prevents scope bleed into mvp                              |
| 02  | user workflow and interaction      | current workflow docs are step-driven and user-checkpoint driven                            |
| 03  | data, accounting model, reconcile      | accounting and reconcile behavior depends on source precedence and booking rules            |
| 04  | outputs and external integrations      | Bank statements, IBKR, and CPF have different integration constraints                       |
| 05  | payments and settlements               | bill and shared-cost workflow has distinct parsing, allocation, and settlement requirements |

**Boundary checks from this step**

- **no overlap**: UI behavior is separated from workflow behavior.
- **no gap**: statement output lifecycle is covered separately from reconcile logic.
- **integration split**: Bank statements and IBKR are kept as separate requirement areas due to different read, write, and lineage constraints.
- **scope decision**: bill payment and shared costs are included in POC requirements scope.
- **coverage decision**: CPF is elevated to a dedicated requirement area, not a hidden sub-scope.
- **scope exclusion**: data migration is excluded from current POC requirements scope and deferred to milestone `23 data migration` in a later phase.

Completion notes for 02.01.02.02:

- completed a fresh review of primary references and current requirements, including `docs/develop/data-sources/inventory.md`, `docs/requirements/current-workflow.md`, `docs/requirements/implementation-roadmap.md`, and the current owner pages.
- scope boundary remained valid after review, so no scope expansion was added.
- refined the landing page to introduce a requirements outline section before the topic index table.
- updated `docs/requirements.md` so the flow now reads: overview, scope, outline, topic index.

_02.01.04 (closed) requirements docs inventory_

| id           | status  | task                                           |
| ------------ | ------- | ---------------------------------------------- |
| 02.01.04.01  | closed  | requirements docs inventory                    |
| 02.01.04.02  | closed  | mapping table                                  |
| 02.01.04.03  | closed  | cross references lineage and ownership         |

- primary deliverable path: `docs/navigation.md`
- define the metadata policy for ownership and cross-linking across requirement documents in `docs/requirements/*`.
- use YAML frontmatter to keep navigation metadata separate from prose body content.
- inventory the list of destination requirements documents both the main entry-point `docs/requirements.md` and the sub-topic documents under `docs/requirements/*`.
- mapping table of existing and destination docs and outcome for existing docs, split into subsection where necessary, which ones get merged, which ones get split, and which ones are new, and which ones become deprecated.
- execute requirements docs inventory plus lineage cross-reference coverage updates to related `docs/requirements/*` docs, recording any out-of-scope decisions in the inventory mapping table.

**02.01.04 closure conditions**

- publish the actual inventory of destination requirement documents across `docs/requirements.md` and the in-scope topic pages under `docs/requirements/*`.
- publish the mapping table of existing document to destination document, with explicit disposition for each item such as keep, split, merge, new, deprecated, or out of scope.
- complete the cross-reference and lineage alignment pass across the requirement pages so owner-page and supporting-page links are intentionally covered rather than implicit only.

Completion notes:

- `docs/requirements.md` now carries a complete retained-document inventory for `docs/requirements/*`, including references such as `implementation-roadmap.md`, `poc.md`, and `environment.md`.
- `docs/develop/010/data-sources/requirements-conflicts-and-gaps.md` CF-01 mapping and deprecation-handling instructions are complete; residual-gaps section removed after applying generic deprecation guidelines.
- `docs/navigation.md` now defines a concrete closure method for inventory completeness, deprecation exclusion from landing-page inventory, and cross-reference alignment checks.
- YAML frontmatter added to all 22 documents in `docs/requirements/*` declaring `title`, `doc_type`, `topic_type`, `owner`, and `scope`.
- `docs/requirements/current-workflow.md` reduced to a lean reference page pointing to owner pages and `docs/reference/current-workflow.md`.
- `docs/reference/current-workflow.md` created preserving non-normative operational context: step timing table, forex URL and procedure, account update flow, and report update flow.

_02.01.03 (closed) scope requirements tasks_

- **aim of this step**: for each topic task 02.02 through 02.16, define the scope of what constitutes a complete set of requirements for that topic, the acceptance criteria for closure, and the subtask breakdown that closes the gap between current state and complete.

| seq | id          | status  | task                          |
| --- | ----------- | ------- | ----------------------------- |
| 01  | 02.01.03.01 | closed  | workflow orchestration scope  |
| 02  | 02.01.03.02 | closed  | interaction approvals scope   |
| 03  | 02.01.03.03 | closed  | exception handling scope      |
| 04  | 02.01.03.04 | closed  | source systems scope          |
| 05  | 02.01.03.05 | closed  | accounting model scope        |
| 06  | 02.01.03.06 | closed  | reconciliation engine scope   |
| 07  | 02.01.03.07 | closed  | statements lifecycle scope    |
| 08  | 02.01.03.08 | closed  | homebudget integration scope  |
| 09  | 02.01.03.09 | closed  | ibkr integration scope        |
| 10  | 02.01.03.10 | closed  | cpf integration scope         |
| 11  | 02.01.03.11 | closed  | bill payment scope            |
| 12  | 02.01.03.12 | closed  | shared costs scope            |

_02.02 (closed) workflow orchestration_

**scope**: `docs/requirements/workflow-orchestration.md` is the owner page.

Complete requirements for this topic cover:

- All seven monthly-close stages defined with entry criteria, exit criteria, inputs, and outputs.
- Account-group route table complete for all in-scope groups including bank, IBKR, CPF, cash, wallets, investments, and others.
- Stage invariants and override policy defined.
- Rerun and resume behavior defined.
- Bill-payment parallel workstream defined and boundary with main workflow explicit.
- Inter-stage handoff and merge-gate contracts defined.

**Compliant**: stage model, route table, dependency rules, entry and exit criteria, inputs and outputs, invariants, override policy, rerun and resume behavior, and inter-stage handoff rules are all defined.

**Inspectable gaps**: None.

**Decision gaps**: None.

**Acceptance criteria**: all stage contracts are specific and unambiguous enough for design to proceed without further user input on workflow sequencing or gate conditions.

| seq | id       | status  | task                              |
| --- | -------- | ------- | --------------------------------- |
| 01  | 02.02.01 | closed  | gap review and closure confirm    |

_02.04 (closed) source systems and lineage_

**scope**: `docs/requirements/source-systems-lineage.md` is the owner page.

Complete requirements for this topic cover:

- All in-scope source systems cataloged with system name, source type, and lineage anchor.
- All seven reconciliation and valuation paths defined: bank statement digital twin, HomeBudget-native, bills domain, IBKR, CPF, manual input, cash, forex, and investment pricing.
- Source precedence and authority rules defined for each account group.
- Transaction lineage metadata defined for each source path.
- Balance lineage metadata defined.
- Cross-path reconciliation points defined.
- Audit and traceability artifact table defined.

**Compliant**: source catalog, data flow paths, precedence rules, transaction lineage, balance lineage, cross-path reconciliation points, and audit artifact table are all defined.

**Inspectable gaps**: None.

**Decision gaps**: None.

**Acceptance criteria**: every source system and path has complete authority rules, lineage metadata requirements, and audit artifact definitions that are unambiguous for design.

| seq | id       | status  | task                           |
| --- | -------- | ------- | ------------------------------ |
| 01  | 02.04.01 | closed  | gap review and closure confirm |

_02.06 (closed) reconciliation engine_

**scope**: `docs/requirements/reconciliation-engine.md` is the owner page. `docs/requirements/cash-reconcile.md` is a reference page.

Complete requirements for this topic cover:

- Shared reconciliation patterns defined: workflow phases, checkpoints, source-input contracts, bill accrual conflict policy, tolerance rules, closure criteria, adjustment posting, and lineage.
- Transaction-level method class fully defined.
- Balance-level method class fully defined.
- All account-group procedures defined: bank statement-process, HomeBudget-native, cash, IBKR, CPF, and manual-input accounts.
- Tolerance values normalized and SOT declared.
- IBKR routing behavior declared and pointed to ibkr-integration.md.

**Compliant**: all six account-group procedures are defined. Shared workflow phases, tolerance rules, closure criteria, adjustment posting, and IBKR routing behavior are defined.

**Inspectable gaps**: None.

**Documentation gaps**: None.

**Decision gaps**: None. (IBKR treatment is clear in ibkr-integration.md.)

**Acceptance criteria**: all account-group procedures are unambiguous.

| seq | id       | status  | task                                   |
| --- | -------- | ------- | -------------------------------------- |
| 01  | 02.06.01 | closed  | gap review and closure confirm         |

_02.12 (closed) cpf integration_

**scope**: `docs/requirements/cpf-integration.md` is the owner page.

Complete requirements for this topic cover:

- Accounts in scope defined: OA, SA, MA.
- Input source defined: Google Sheets UI, field list per sub-account per period.
- Contribution requirements defined.
- Interest income requirements defined including non-monthly period handling.
- Medisave transaction requirements defined including gap detection and classification.
- Reconciliation requirements defined: balance equation per sub-account, blocking behavior.
- Lineage fields defined.

**Compliant**: all sub-accounts, input fields, contribution rules, interest handling, Medisave gap rules, reconciliation equations, blocking conditions, and lineage fields are defined.

**Inspectable gaps**: None.

**Documentation gaps**: None.

**Decision gaps**: None.

**Acceptance criteria**: all CPF sub-account behaviors are unambiguous with no design-time ambiguity remaining.

| seq | id       | status  | task                           |
| --- | -------- | ------- | ------------------------------ |
| 01  | 02.12.01 | closed  | gap review and closure confirm |

_02.16 (closed) shared costs_

**scope**: `docs/requirements/shared-costs.md` is the owner page.

Complete requirements for this topic cover:

- Lifecycle-link ownership rule defined: bill amount must be defined before shared-cost settlement.
- Shared-cost field contracts defined with type, requiredness, allowed values, and validation.
- Shared-cost parameter constraints defined: split basis, rounding mode, settlement account, settlement currency, variance tolerance.
- Session completion rule defined.
- Consumption baseline field contracts defined.
- Consumption parameter constraints defined.
- Cross-page validation rules defined.

**Compliant**: lifecycle-link ownership rule, field contracts, parameter constraints, session completion rule, consumption baseline field contracts, consumption parameter constraints, and cross-page validation rules are all defined with explicit validation baselines.

**Inspectable gaps**: None.

**Documentation gaps**: None.

**Decision gaps**: None.

**Acceptance criteria**: shared-cost and consumption requirements are explicit, field-level contracts are testable, and there is no ambiguity remaining in allocation, settlement, or consumption recording behavior.

| seq | id       | status  | task                           |
| --- | -------- | ------- | ------------------------------ |
| 01  | 02.16.01 | closed  | gap review and closure confirm |

_02.03 (closed) interaction and approvals_

**scope**: `docs/requirements/interaction-approvals.md` is the owner page.

Complete requirements for this topic cover:

- Review checkpoint defined for every workflow stage with explicit pass criteria.
- Confirmation actions before every destructive or irreversible commit.
- Approval authority and escalation boundary defined.
- Rejection behavior defined with session state consequence.
- Decision logging format and readability requirements defined.

**Compliant**: checkpoint table structure, confirmation rules, approval authority, escalation boundary, rejection behavior, and decision logging requirements are defined. Per-stage checkpoint pass criteria table is now explicit in interaction-approvals.md.

**Inspectable gaps**: per-stage checkpoint pass criteria are derivable by cross-referencing stage exit criteria in workflow-orchestration.md, reconciliation engine Phase 1 input validation in reconciliation-engine.md, and statements-lifecycle.md finalization criteria. Criteria can be extracted from primary sources without new user input.

**Documentation gaps**: None.

**Decision gaps**: None.

**Acceptance criteria**: every stage checkpoint has explicit pass criteria that a design agent can translate into a deterministic acceptance check without guessing.

| seq | id       | status  | task                                        |
| --- | -------- | ------- | ------------------------------------------- |
| 01  | 02.03.01 | closed  | per-stage checkpoint criteria consolidate   |
| 02  | 02.03.02 | closed  | gap review and closure confirm              |

_02.15 (closed) exception and error handling_

- **aim of this step**: define requirement-level exception and error handling behavior in a dedicated owner document.
- primary destination owner page: `docs/requirements/exception-error-handling.md`
- include requirement statements for missing mappings, validation failures, close-blocking behavior, user remediation flow, and audit traceability.
- this scope is separated from `02.01` conflicts-and-gaps analysis to avoid mixing ownership discovery with policy definition.

Complete requirements for this topic cover:

- Missing mapping behavior: what happens when a required category or account mapping is absent at close time.
- Validation failure behavior: what blocks close, what permits override, what must be logged.
- Close-blocking conditions enumerated across all stages.
- User remediation flow: how the user resolves each class of error.
- Audit traceability: what is retained from each exception event.

**Compliant**: close-blocking condition categories are derived from stage exit criteria in workflow-orchestration.md and reconciliation-engine.md. Override and remediation policy is now consolidated in exception-error-handling.md. Single-user authorization model is explicitly stated.

**Inspectable gaps**: close-blocking conditions are fully derivable from stage exit rules in workflow-orchestration.md and reconciliation-engine.md Phase 1 input-and-validation requirements. Per-stage blocking behavior needs cross-document consolidation (documentation gap).

**Documentation gaps**: None.

**Decision gaps**: EE-05 audit retention duration is deferred as a minor non-blocking item; storage format is specified (S3). EE-03 and EE-04 are accepted — missing-category remediation escalates to user and close stays open; source-validation failure escalates to user and close stays open.

**Acceptance criteria**: owner page exists and defines behavior for every close-blocking condition class, every remediation path, and all audit retention rules.

| seq | id       | status  | task                                                  |
| --- | -------- | ------- | ----------------------------------------------------- |
| 01  | 02.15.01 | closed  | exception-error-handling decisions resolve            |
| 02  | 02.15.02 | closed  | create exception-error-handling owner page            |
| 03  | 02.15.03 | closed  | blocking and override policy consolidate              |
| 04  | 02.15.04 | closed  | gap review and closure confirm                        |

_02.05 (closed) accounting model and mapping_

**scope**: `docs/requirements/accounting-logic.md`, `docs/requirements/account-classification.md`, and `docs/requirements/transaction-categories.md` are the owner pages.

Complete requirements for this topic cover:

**Accounting logic:**
- Personal expense and income booking model defined with cost-center mechanics.
- M2M accounting defined for both indivisible and unit-price variants with examples.
- Forex effects defined: M2M on balances and forex on transactions.
- Bills accrual and settlement defined including time inconsistency and partial payment.
- Unique transaction and de-duplication logic defined.
- Accounting periods defined.
- Reconciliation method classes defined.

**Account classification:**
- All HomeBudget account types defined with examples and transaction rules.
- Financial statement asset type mapping defined with all subcategories.
- Per-asset-type rules defined for cash, credit, savings, liquid investments, and illiquid/retirement.
- Edge cases defined: IBKR positive/negative balance classification, CPF Medisave dual classification.

**Transaction categories:**
- HB category taxonomy and GL code assignment requirements defined.
- Income statement aggregation rules defined.
- Category data model as source of truth defined.

**Compliant**: accounting-logic.md is well-developed with personal expense and income booking, M2M accounting, forex effects, bills accrual, de-duplication logic, accounting periods, and reconciliation method classes defined. account-classification.md is well-developed. transaction-categories.md defines the HB category taxonomy and income statement aggregation rules. Mapping completeness gates are owned by workflow-orchestration.md. Category management UI is owned by user-interface.md. Data integrity validation rules are owned by exception-error-handling.md.

**Inspectable gaps**: category mapping and account classification field schemas are defined in helper workbook `cat_map` and account-registry `accounts` sources, and are inspectable from workbook header rows and config metadata.

**Documentation gaps**: None. Field contracts for expense category (transaction-categories.md) and account registry (account-classification.md) are now explicit with typed field contract tables.

**Decision gaps**: None.

**Acceptance criteria**: all three pages are complete and consistent. Category and account data models have explicit field contracts. No ambiguity remains in how transactions are classified and aggregated end-to-end.

| seq | id       | status  | task                                         |
| --- | -------- | ------- | -------------------------------------------- |
| 01  | 02.05.01 | closed  | category mapping field schema consolidate    |
| 02  | 02.05.02 | closed  | gap review and closure confirm               |

_02.07 (closed) statements lifecycle_

**scope**: `docs/requirements/statements-lifecycle.md` is the owner page.

Complete requirements for this topic cover:

- Lifecycle state model defined with all states, meanings, and allowed transitions.
- Draft and review behavior defined.
- Finalization criteria defined.
- Reopen policy defined with traceability requirement.
- Revision policy defined with versioning requirement.
- Publish output rules defined.
- Artifact output requirements defined: PDF per statement type, S3 upload, session close record.
- Versioning and lineage linkage defined.
- Period snapshot immutability rules defined.

**Compliant**: all lifecycle states, draft review, finalization, reopen policy structure, revision policy, publish rules, artifact output requirements, versioning, and immutability rules are defined.

**Inspectable gaps**: reopen conditions are derivable from the single-user POC model combined with workflow-orchestration rerun/resume behavior — the user may reopen whenever a correction is needed and must log the reason.

**Documentation gaps**: None. Reopen conditions and authorization are now explicitly stated in statements-lifecycle.md with a 6-bullet policy.

**Decision gaps**: None.

**Acceptance criteria**: reopen conditions and authorization are explicit. All state transitions are unambiguous and traceable.

| seq | id       | status  | task                                   |
| --- | -------- | ------- | -------------------------------------- |
| 01  | 02.07.01 | closed  | reopen conditions consolidate          |
| 02  | 02.07.02 | closed  | gap review and closure confirm         |

_02.08 (open) homebudget integration_

**scope**: `docs/requirements/homebudget.md` is the owner page. `docs/requirements/data-model.md` is the schema owner.

Complete requirements for this topic cover:

- HomeBudget role as primary user UI, operational ledger, and system of record for accounts, transactions, categories, and metadata defined.
- Integration boundary defined: all app access through the HomeBudget Python wrapper, no direct SQLite reads or writes as the product contract.
- Wrapper capability contract defined for account, category, and transaction reads plus controlled write-back behavior.
- Data sync behavior defined for app-managed `hb` schema objects.
- Schema object canonical names defined: `hb_gl_txn`, `hb_account_dim`, `hb_category_dim`.
- Lineage anchor defined: `hb_txn_uid` as deterministic hashed transaction UID.
- SCD type 1 update behavior defined for HomeBudget dimension objects.
- HomeBudget-specific account roles and posting patterns consolidated for design use.
- Reconciliation write-back behavior defined: when approved adjustments are posted back through the wrapper.
- Overlap boundary resolved for what stays in `homebudget.md` versus `accounting-logic.md`, `account-classification.md`, `data-model.md`, and `source-systems-lineage.md`.

**Compliant**: wrapper-only rule, sync objects, canonical names, lineage anchor, and SCD type 1 policy were already defined. HomeBudget role, design-time account roles, posting patterns, wrapper capability contract, adjustment write-back behavior, and overlap boundaries are now consolidated in `docs/requirements/homebudget.md`.

**Inspectable gaps**: None.

**Documentation gaps**: None.

**Decision gaps**: None.

**Acceptance criteria**: design can determine the HomeBudget boundary, required wrapper capabilities, synced objects, lineage anchor, account-role semantics, posting patterns, and approved write-back behavior by reading `homebudget.md` plus only owner-page quick references for adjacent specialized topics.

| seq | id       | status  | task                                    |
| --- | -------- | ------- | --------------------------------------- |
| 01  | 02.08.01 | closed  | owner page scope expand                 |
| 02  | 02.08.02 | closed  | wrapper sync contract consolidate       |
| 03  | 02.08.03 | closed  | account roles and posting consolidate   |
| 04  | 02.08.04 | closed  | reconcile write-back consolidate        |
| 05  | 02.08.05 | closed  | overlap ownership resolve               |
| 06  | 02.08.06 | closed  | gap review and closure confirm          |

_02.08.06 (closed) gap review and closure confirm_

- `docs/requirements/homebudget.md` confirmed sufficient for design-time reference: covers system role, wrapper boundary, capability contract, sync objects, lineage anchor, account roles, posting patterns, write-back behavior, and design constraints without requiring a pass through skills or external wrapper docs.
- all cross-references point to specialized owner pages (`accounting-logic.md`, `account-classification.md`, `data-model.md`, `source-systems-lineage.md`) for adjacent detail; none indicate missing HomeBudget requirement content.
- no inspectable gaps, documentation gaps, or decision gaps found. `02.08` closed.

_02.09 (closed) ibkr integration_

**scope**: `docs/requirements/ibkr-integration.md` is the owner page.

Complete requirements for this topic cover:

- Accounts in scope defined: IBA and IRA with account IDs, types, and sub-account structure.
- Source format defined: section-based CSV, sections used.
- IBA derivation formulas defined: `change_cash`, `change_pos`, `buy_sell`, `position_capital_gains`, `investment_income`.
- IRA derivation formulas defined: `change_pos`, `buy_sell`, `capital_gains_loss`.
- `deposit_withdrawal` mapping from Cash Report fully specified.
- Classification rules defined for all derived components.
- Validation and close-gate checks defined for IBA and IRA.
- Lineage fields defined for all posted values.

**Compliant**: IBA and IRA derivation formulas, classification rules, validation and close-gate checks, lineage fields, and CSV row-level mapping rules are defined.

**Inspectable gaps**: None.

**Documentation gaps**: None.

**Decision gaps**: None.

**Acceptance criteria**: CSV format specification is complete. All derivation formulas produce unambiguous outputs for both accounts without further user input.

Inspection evidence used to close this scope:

- `reference/statements/ibkr-iba/U1109040_Activity_202510.csv` confirms `Cash Report` rows `Deposits` and `Withdrawals` under `Base Currency Summary`, and confirms `Trades (Sales)` and `Trades (Purchase)` source rows.
- `reference/statements/ibkr-iba/U1109040_Activity_202510.csv` confirms `Change in NAV` row `Deposits & Withdrawals` for cross-check parity.
- `reference/statements/ibkr-ira/U9311815_Activity_202510.csv` confirms the same section structure, including months where deposits and withdrawals can be absent.
- `docs/requirements/ibkr-integration.md` now specifies deterministic extraction and fallback rules for missing rows.

| seq | id       | status  | task                                   |
| --- | -------- | ------- | -------------------------------------- |
| 01  | 02.09.01 | closed  | ibkr csv format inspect and specify    |
| 02  | 02.09.02 | closed  | gap review and closure confirm         |

_02.13 (closed) bill payment_

**scope**: `docs/requirements/bill-payment.md` is the owner page.

Complete requirements for this topic cover:

- Bills in scope identified by payee, account, and payment method.
- Bill data model field contracts defined.
- Bill lifecycle state model defined with transitions.
- Close criteria for bill lifecycle defined.
- Bill-level and period-level reconciliation checks defined.
- Bill-payment session completion rule defined.
- Statement parsing requirements defined.
- Transaction generation requirements defined.
- Accounts in scope defined.

**Compliant**: bills in scope, data model, lifecycle states, close criteria, reconciliation checks, session completion rule, statement parsing requirements, and transaction generation requirements are all defined.

**Inspectable gaps**: None.

**Documentation gaps**: None.

**Decision gaps**: None.

**Acceptance criteria**: all bill payees are covered. Parsing, generation, reconciliation, and lifecycle requirements are unambiguous.

Inspection evidence used to close this scope:

- Design-time baseline is defined in `docs/requirements/bill-payment.md`, including the statement parsing contract, normalized field contract, payee normalization coverage, and multi-line parsing rules.
- Tracker scope here remains status and closure metadata only.

| seq | id       | status  | task                                    |
| --- | -------- | ------- | --------------------------------------- |
| 01  | 02.13.01 | closed  | bill-format parsing coverage verify     |
| 02  | 02.13.02 | closed  | gap review and closure confirm          |

_02.17 (closed) user interfaces_

**scope**: `docs/requirements/user-interface.md` is the owner page.

Complete requirements for this topic cover:

- Google Sheets as the primary session UI is explicitly defined with a surface catalog and per-workbook roles.
- Consolidated workbook page inventory is defined with page-level purpose, source basis, and status.
- Financial statements workbook review surface defined with reconcile and statement output roles.
- Category management and account management UI surfaces are defined with capability requirements.
- Session log surface defined with required field-level record contract.
- CLI surface scope and boundaries defined.
- Non-functional interface requirements defined.
- Out-of-scope interfaces explicitly stated.

**Compliant**: user-interface.md now defines a consolidated workbook model with 23 workflow touchpoints and inventory entries, including session_dashboard consolidation, category_mapping, account_registry_status, reconcile dashboards, statement outputs, review drill-down pages, and sync_review. Mapping management field contracts for category_mapping and account_registry_status are now explicit at requirement level. Session log field contract now defines seven fields with types, required flags, and uniqueness constraints. Non-functional requirements include environment-key resolution for the UI workbook through `GS_UI_WKB_ID` in `.env`.

**Documentation gaps**: None.

**Decision gaps**: None.

**Acceptance criteria**: all UI surfaces used in the POC workflow are defined with explicit role, scope, and field-level requirements. Category management UI, account management UI, and session log contracts are explicit enough for design to proceed without additional clarification. CLI scope and out-of-scope boundaries are explicit. No surface used during the close workflow is undocumented.

| seq | id       | status  | task                                    |
| --- | -------- | ------- | --------------------------------------- |
| 01  | 02.17.01 | closed  | create user-interface owner page        |
| 02  | 02.17.02 | closed  | category and account ui contract define |
| 03  | 02.17.03 | closed  | session log field contract define       |
| 04  | 02.17.05 | closed  | sync_review page add to inventory       |
| 05  | 02.17.04 | closed  | gap review and closure confirm          |

_02.18 (closed) category and account mgmt_

**scope**: `docs/requirements/transaction-categories.md` and `docs/requirements/account-classification.md` are owner pages.

**aim of this task**: inspect the legacy stage 1 and stage 2 logic from primary sources and translate the bespoke classification rules they encode into explicit requirements in the new category and account management model. The output is requirement statements — not new design decisions — derived from what the legacy logic already does.

Complete requirements for this topic cover:

- Legacy stage 1 logic (`cat_map` region in `gsheet/homebudget-workbook.json`) is inspected and its HB-category-to-GL mapping rules are stated explicitly as category management requirements.
- Legacy stage 2 expense mapping logic (`fin_exp_cat_map` region in `gsheet/financial-statements.json`) is inspected and its GL-to-reporting-classification rules are stated explicitly as category management requirements.
- Legacy stage 2 account classification logic (`accounts` region in `gsheet/financial-statements.json`) is inspected and its account-to-asset-type assignment rules are stated explicitly as account classification requirements.
- Translated requirements are recorded in the owner pages using the new category and account management model vocabulary, with no stage pipeline terms in requirement statements.
- Gaps between legacy logic coverage and new model requirements are identified and documented.

**Compliant**: primary sources inspected via `inspect_cat_map.py` and `inspect_stage2_sources.py`. Artifacts at `.dev/.artifacts/stage2_sources_inspection.json`.

**Inspectable gaps**: `cat_map` 181 rows 10 columns; `fin_exp_cat_map` 33 rows 5 columns; `accounts` 29 rows 7 columns. Full column-level and rule-level translation completed.

**Documentation gaps**: closed. Translation document published at `docs/develop/010/design/category-account-model-translation.md`. All 28 expense `gl_code` values, full `fin_exp_cat_map` table, full `accounts` table with asset types, and legacy-to-new model mapping table are documented. All identified gaps have dispositions.

**Decision gaps**: three items require confirmation at design time — COM UOB SGD scope in POC, CPF MS Medisave asset type, WPC POSITION SGD scope. Documented in gap analysis section of translation document.

**Acceptance criteria**: met. Every classification rule in legacy stage 1 and stage 2 sources is either translated to the new model or explicitly documented with a disposition.

**Design artifact**: published at `docs/develop/010/design/category-account-model-translation.md`.

| seq | id       | status | task                                              |
| --- | -------- | ------ | ------------------------------------------------- |
| 01  | 02.18.01 | closed | legacy stage 1 cat_map logic inspect              |
| 02  | 02.18.02 | closed | legacy stage 2 fin_exp_cat_map logic inspect      |
| 03  | 02.18.03 | closed | legacy stage 2 accounts logic inspect             |
| 04  | 02.18.04 | closed | translate to new model requirement statements     |
| 05  | 02.18.05 | closed | gap review and closure confirm                    |
