#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys

from errors import (
    EXIT_CODE_INTERNAL,
    FormulaError,
    InternalError,
    exit_code_for_error,
)
from models import FormulaRequest
from output import AuditWriter, ResultFormatter
from service import FormulaService

MUTATION_OPERATIONS = {"create", "update", "clear", "batch-create", "batch-update", "batch-clear"}


class CliApp:
    def __init__(self) -> None:
        self._service = FormulaService()
        self._formatter = ResultFormatter()
        self._audit_writer = AuditWriter()

    def run(self, argv: list[str]) -> int:
        parser = self._build_parser()
        args = parser.parse_args(argv)

        ranges_a1 = None
        formula_by_range = None
        if args.operation in {"batch-read", "batch-clear"}:
            ranges_a1 = [value.strip() for value in args.ranges.split(",") if value.strip()]
        if args.operation in {"batch-create", "batch-update"}:
            formula_by_range = self._load_batch_file(args.batch_file)

        request = FormulaRequest(
            operation=args.operation,
            client_secret=args.client_secret,
            workbook_id=args.workbook_id,
            range_a1=getattr(args, "range_a1", ""),
            formula_text=getattr(args, "formula", None),
            ranges_a1=ranges_a1,
            formula_by_range=formula_by_range,
            max_retries=args.max_retries,
            timeout_seconds=args.timeout_seconds,
        )

        try:
            result = self._service.execute(request)
            self._print_result(result, args.output)
            if args.audit_file and args.operation in MUTATION_OPERATIONS:
                self._audit_writer.append_record(args.audit_file, result)
            return 0
        except FormulaError as exc:
            failed_result = self._failure_result(request, exc)
            self._print_result(failed_result, args.output)
            if args.audit_file and request.operation in MUTATION_OPERATIONS:
                self._audit_writer.append_record(args.audit_file, failed_result)
            return exit_code_for_error(exc)
        except Exception as exc:  # noqa: BLE001
            err = InternalError(f"unexpected failure: {exc}")
            failed_result = self._failure_result(request, err)
            self._print_result(failed_result, args.output)
            if args.audit_file and request.operation in MUTATION_OPERATIONS:
                self._audit_writer.append_record(args.audit_file, failed_result)
            return EXIT_CODE_INTERNAL

    def _print_result(self, result, output_format: str) -> None:
        if output_format == "json":
            print(self._formatter.to_json(result))
        else:
            print(self._formatter.to_text(result))

    @staticmethod
    def _failure_result(request: FormulaRequest, error: FormulaError):
        from models import FormulaResult

        return FormulaResult(
            operation=request.operation,
            workbook_id=request.workbook_id,
            range_a1=request.range_a1,
            status="failure",
            requested_formula=request.formula_text,
            resulting_formula=None,
            error_category=error.category,
            error_message=str(error),
        )

    @staticmethod
    def _build_parser() -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(prog="gsheet-formulas")
        command_parsers = parser.add_subparsers(dest="command", required=True)

        formula_parser = command_parsers.add_parser("formula")
        operation_parsers = formula_parser.add_subparsers(dest="operation", required=True)

        for operation in ("read", "create", "update", "clear"):
            op_parser = operation_parsers.add_parser(operation)
            op_parser.add_argument("--client-secret", required=True)
            op_parser.add_argument("--workbook-id", required=True)
            op_parser.add_argument("--range", dest="range_a1", required=True)
            if operation in {"create", "update"}:
                op_parser.add_argument("--formula", required=True)
            op_parser.add_argument("--output", choices=["text", "json"], default="text")
            op_parser.add_argument("--audit-file")
            op_parser.add_argument("--max-retries", type=int, default=5)
            op_parser.add_argument("--timeout-seconds", type=int, default=30)

        for operation in ("batch-read", "batch-clear"):
            op_parser = operation_parsers.add_parser(operation)
            op_parser.add_argument("--client-secret", required=True)
            op_parser.add_argument("--workbook-id", required=True)
            op_parser.add_argument("--ranges", required=True)
            op_parser.add_argument("--output", choices=["text", "json"], default="text")
            op_parser.add_argument("--audit-file")
            op_parser.add_argument("--max-retries", type=int, default=5)
            op_parser.add_argument("--timeout-seconds", type=int, default=30)

        for operation in ("batch-create", "batch-update"):
            op_parser = operation_parsers.add_parser(operation)
            op_parser.add_argument("--client-secret", required=True)
            op_parser.add_argument("--workbook-id", required=True)
            op_parser.add_argument("--batch-file", required=True)
            op_parser.add_argument("--output", choices=["text", "json"], default="text")
            op_parser.add_argument("--audit-file")
            op_parser.add_argument("--max-retries", type=int, default=5)
            op_parser.add_argument("--timeout-seconds", type=int, default=30)

        return parser

    @staticmethod
    def _load_batch_file(batch_file: str) -> dict[str, str]:
        with open(batch_file, "r", encoding="utf-8") as file_obj:
            payload = json.load(file_obj)
        if not isinstance(payload, list):
            raise ValueError("batch file must be a list of objects")
        formula_by_range: dict[str, str] = {}
        for item in payload:
            if not isinstance(item, dict) or "range" not in item or "formula" not in item:
                raise ValueError("each batch item must include range and formula")
            formula_by_range[str(item["range"])] = str(item["formula"])
        return formula_by_range


def main() -> int:
    app = CliApp()
    return app.run(sys.argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
