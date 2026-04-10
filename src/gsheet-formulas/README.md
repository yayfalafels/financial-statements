# gsheet-formulas Source Layout

This folder is the release 010 source target for the formula CRUD utility.

Implemented modules:

- cli.py
- models.py
- validation.py
- auth.py
- sheets_client.py
- service.py
- output.py
- errors.py

## CLI usage

- Read formula:
	- `python src/gsheet-formulas/cli.py formula read --client-secret .credentials/client_secret.json --workbook-id <wkbid> --range A3`
- Create formula:
	- `python src/gsheet-formulas/cli.py formula create --client-secret .credentials/client_secret.json --workbook-id <wkbid> --range A3 --formula "=10+20"`
- Update formula:
	- `python src/gsheet-formulas/cli.py formula update --client-secret .credentials/client_secret.json --workbook-id <wkbid> --range A3 --formula "=30+40"`
- Clear formula:
	- `python src/gsheet-formulas/cli.py formula clear --client-secret .credentials/client_secret.json --workbook-id <wkbid> --range A3`

Optional flags for all commands:

- `--output text|json`
- `--audit-file <path>`
- `--max-retries <int>`
- `--timeout-seconds <int>`
