#!/usr/bin/env python
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal

OperationName = Literal[
    "read",
    "create",
    "update",
    "clear",
    "batch-read",
    "batch-create",
    "batch-update",
    "batch-clear",
]
OutputFormat = Literal["text", "json"]


@dataclass(frozen=True)
class FormulaRequest:
    operation: OperationName
    client_secret: str
    workbook_id: str
    range_a1: str
    formula_text: str | None = None
    ranges_a1: list[str] | None = None
    formula_by_range: dict[str, str] | None = None
    max_retries: int = 5
    timeout_seconds: int = 30


@dataclass(frozen=True)
class FormulaResult:
    operation: OperationName
    workbook_id: str
    range_a1: str
    status: Literal["success", "failure"]
    requested_formula: str | None = None
    resulting_formula: str | None = None
    error_category: str | None = None
    error_message: str | None = None


@dataclass(frozen=True)
class AuditRecord:
    event_at: str
    operation: OperationName
    workbook_id: str
    range_a1: str
    status: str
    error_category: str | None
    error_message: str | None
    requested_formula: str | None
    resulting_formula: str | None

    @classmethod
    def from_result(cls, result: FormulaResult) -> "AuditRecord":
        return cls(
            event_at=datetime.now(timezone.utc).isoformat(),
            operation=result.operation,
            workbook_id=result.workbook_id,
            range_a1=result.range_a1,
            status=result.status,
            error_category=result.error_category,
            error_message=result.error_message,
            requested_formula=result.requested_formula,
            resulting_formula=result.resulting_formula,
        )
