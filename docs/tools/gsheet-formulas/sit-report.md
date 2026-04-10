# Gsheet Formulas SIT Report

## Summary

- Release: 010
- Task: 02.14.18.06
- Executor: agent
- Environment: `env/` (Python 3.11)
- Workbook: `1SNtnlNufcZp-44f5U1YbECUwHbkICih5cdywiu04wpI`
- Range: `A3`
- Result: pass

## Preconditions

- Credential file present at `.credentials/client_secret.json`
- Google Sheets API access validated with runtime service account
- Dependencies installed from `requirements.txt` and `gsheet-formulas-requirements.txt`

## Scenario Results

| id | scenario            | command result | observed outcome                          | status |
| -- | ------------------- | -------------- | ----------------------------------------- | ------ |
| 01 | read baseline       | success        | returned `resulting_formula=null`         | pass   |
| 02 | create formula      | success        | stored and verified `=10+20`              | pass   |
| 03 | update formula      | success        | stored and verified `=30+40`              | pass   |
| 04 | clear formula       | success        | post-clear read verified empty target     | pass   |
| 05 | invalid write range | validation err | rejected `A1:B2` before mutation          | pass   |
| 06 | blank workbook id   | validation err | rejected empty workbook id                | pass   |
| 07 | invalid workbook id | api err        | returned API 404 runtime failure category | pass   |
| 08 | missing secret path | validation err | rejected unreadable credential path       | pass   |

## Command Log

1. `python src/gsheet-formulas/cli.py formula read --client-secret .credentials/client_secret.json --workbook-id 1SNtnlNufcZp-44f5U1YbECUwHbkICih5cdywiu04wpI --range A3 --output json`
2. `python src/gsheet-formulas/cli.py formula create --client-secret .credentials/client_secret.json --workbook-id 1SNtnlNufcZp-44f5U1YbECUwHbkICih5cdywiu04wpI --range A3 --formula "=10+20" --output json --audit-file docs/tools/gsheet-formulas/sit-audit.jsonl`
3. `python src/gsheet-formulas/cli.py formula update --client-secret .credentials/client_secret.json --workbook-id 1SNtnlNufcZp-44f5U1YbECUwHbkICih5cdywiu04wpI --range A3 --formula "=30+40" --output json --audit-file docs/tools/gsheet-formulas/sit-audit.jsonl`
4. `python src/gsheet-formulas/cli.py formula clear --client-secret .credentials/client_secret.json --workbook-id 1SNtnlNufcZp-44f5U1YbECUwHbkICih5cdywiu04wpI --range A3 --output json --audit-file docs/tools/gsheet-formulas/sit-audit.jsonl`
5. `python src/gsheet-formulas/cli.py formula create --client-secret .credentials/client_secret.json --workbook-id 1SNtnlNufcZp-44f5U1YbECUwHbkICih5cdywiu04wpI --range A1:B2 --formula "=1+1" --output json`
6. `python src/gsheet-formulas/cli.py formula read --client-secret .credentials/client_secret.json --workbook-id " " --range A3 --output json`
7. `python src/gsheet-formulas/cli.py formula read --client-secret .credentials/client_secret.json --workbook-id 1SNtnlNufcZp-44f5U1YbECUwHbkICih5cdywiu04wpX --range A3 --output json`
8. `python src/gsheet-formulas/cli.py formula read --client-secret .credentials/missing-secret.json --workbook-id 1SNtnlNufcZp-44f5U1YbECUwHbkICih5cdywiu04wpI --range A3 --output json`

## Evidence Artifacts

- Mutation audit log: `docs/tools/gsheet-formulas/sit-audit.jsonl`
- Tracker closure updates: `docs/develop/010/project-management/gsheet-formulas.md`

## Defect and Risk Notes

- No high-severity SIT defects observed.
- Remaining release risk is operational: overwrite-by-default behavior requires operator discipline during UAT.
