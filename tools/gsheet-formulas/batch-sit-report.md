# Gsheet Formulas Batch SIT Report

## Summary

- Release: 010
- Task: 02.14.18.09.04
- Executor: agent
- Environment: env (Python 3.11)
- Workbook: 1SNtnlNufcZp-44f5U1YbECUwHbkICih5cdywiu04wpI
- Ranges tested: A3,B3 and D2:E11 selected cells
- Result: pass

## Scenario Results

| id       |                     |      |
| -------- | ------------------- | ---- |
| scenario |                     |      |
| outcome  |                     |      |
| 01       | batch read baseline | pass |
| 02       | batch create small  | pass |
| 03       | batch update small  | pass |
| 04       | batch clear small   | pass |
| 05       | batch create large  | pass |
| 06       | bad workbook input  | pass |
| 07       | invalid workbook id | pass |

## Command Evidence

1. `formula batch-read --ranges A3,B3`
2. `formula batch-create --batch-file .dev/env/batch_sit_create.json`
3. `formula batch-update --batch-file .dev/env/batch_sit_update.json`
4. `formula batch-clear --ranges A3,B3`
5. `formula batch-create --batch-file .dev/env/black_scholes_batch.json`
6. `formula batch-read --workbook-id " " --ranges A3,B3` with exit code 2
7. `formula batch-read --workbook-id invalid --ranges A3,B3` with exit code 3

## Findings

- No unhandled exceptions observed in SIT.
- Validation and API error mappings behaved as designed.
- Batch read, create, update, and clear completed successfully.

## Learnings

- Google Sheets in this workbook returned `#N/A` for `NORM.S.DIST` in Black-Scholes output cells.
- A compatibility-safe formula pattern is required:
	- `IFERROR(NORM.S.DIST(x,TRUE),NORMSDIST(x))`
- Range token canonicalization can reorder formula references; semantic equivalence checks should be used.
- For formulas containing `$` in PowerShell commands, pass values in single quotes to avoid shell expansion.

## Artifacts

- Audit: docs/tools/gsheet-formulas/batch-sit-audit.jsonl
- Tracker: docs/develop/010/project-management/gsheet-formulas.md
