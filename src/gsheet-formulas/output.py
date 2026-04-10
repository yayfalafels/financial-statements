#!/usr/bin/env python
from __future__ import annotations

import json
from dataclasses import asdict

from models import AuditRecord, FormulaResult


class ResultFormatter:
    def to_text(self, result: FormulaResult) -> str:
        base = (
            f"operation={result.operation} workbook_id={result.workbook_id} "
            f"range={result.range_a1} status={result.status}"
        )
        if result.status == "success":
            return f"{base} resulting_formula={result.resulting_formula}"
        return (
            f"{base} error_category={result.error_category} "
            f"error_message={result.error_message}"
        )

    def to_json(self, result: FormulaResult) -> str:
        return json.dumps(asdict(result), ensure_ascii=False)


class AuditWriter:
    def append_record(self, audit_file: str, result: FormulaResult) -> None:
        record = AuditRecord.from_result(result)
        with open(audit_file, "a", encoding="utf-8") as file_obj:
            file_obj.write(json.dumps(asdict(record), ensure_ascii=False))
            file_obj.write("\n")
