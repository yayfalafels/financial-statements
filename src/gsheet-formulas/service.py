#!/usr/bin/env python
from __future__ import annotations

import random
import re
import time
import json

from googleapiclient.errors import HttpError

from auth import SheetsAuth
from errors import ApiError
from models import FormulaRequest, FormulaResult
from sheets_client import SheetsValuesClient
from validation import InputValidator

DEFAULT_MAX_RETRIES = 5
DEFAULT_MAX_BACKOFF_SECONDS = 32
TRANSIENT_HTTP_STATUSES = {429, 500, 502, 503, 504}
CELL_REF_REGEX = re.compile(r"^([A-Z]{1,3})([1-9][0-9]*)$")
RANGE_REF_REGEX = re.compile(r"([A-Z]{1,3}[1-9][0-9]*):([A-Z]{1,3}[1-9][0-9]*)")


class FormulaService:
    def __init__(self, validator: InputValidator | None = None, auth: SheetsAuth | None = None) -> None:
        self._validator = validator or InputValidator()
        self._auth = auth or SheetsAuth()

    def execute(self, request: FormulaRequest) -> FormulaResult:
        self._validator.validate(request)

        max_retries = max(0, request.max_retries)
        service = self._auth.build_service(request.client_secret, max_retries=max_retries)
        client = SheetsValuesClient(service)

        if request.operation == "read":
            return self._read(request, client)
        if request.operation == "create":
            return self._create_or_update(request, client)
        if request.operation == "update":
            return self._create_or_update(request, client)
        if request.operation == "clear":
            return self._clear(request, client)
        if request.operation == "batch-read":
            return self._batch_read(request, client)
        if request.operation == "batch-create":
            return self._batch_create_or_update(request, client)
        if request.operation == "batch-update":
            return self._batch_create_or_update(request, client)
        if request.operation == "batch-clear":
            return self._batch_clear(request, client)

        raise ApiError(f"unsupported operation: {request.operation}")

    def _read(self, request: FormulaRequest, client: SheetsValuesClient) -> FormulaResult:
        resulting_formula = self._with_retry(
            operation_name="read",
            max_retries=request.max_retries,
            func=lambda: client.get_formula(request.workbook_id, request.range_a1),
        )
        return FormulaResult(
            operation=request.operation,
            workbook_id=request.workbook_id,
            range_a1=request.range_a1,
            status="success",
            resulting_formula=resulting_formula,
        )

    def _create_or_update(self, request: FormulaRequest, client: SheetsValuesClient) -> FormulaResult:
        requested_formula = request.formula_text.strip() if request.formula_text else None
        self._with_retry(
            operation_name=request.operation,
            max_retries=request.max_retries,
            func=lambda: client.write_formula(request.workbook_id, request.range_a1, requested_formula),
        )
        resulting_formula = self._with_retry(
            operation_name="read_after_write",
            max_retries=request.max_retries,
            func=lambda: client.get_formula(request.workbook_id, request.range_a1),
        )
        if not self._formula_equivalent(requested_formula, resulting_formula):
            raise ApiError(
                "read-after-write verification failed: "
                f"expected '{requested_formula}' but found '{resulting_formula}'"
            )
        return FormulaResult(
            operation=request.operation,
            workbook_id=request.workbook_id,
            range_a1=request.range_a1,
            status="success",
            requested_formula=requested_formula,
            resulting_formula=resulting_formula,
        )

    def _clear(self, request: FormulaRequest, client: SheetsValuesClient) -> FormulaResult:
        self._with_retry(
            operation_name="clear",
            max_retries=request.max_retries,
            func=lambda: client.clear_formula(request.workbook_id, request.range_a1),
        )
        resulting_formula = self._with_retry(
            operation_name="read_after_clear",
            max_retries=request.max_retries,
            func=lambda: client.get_formula(request.workbook_id, request.range_a1),
        )
        if resulting_formula is not None:
            raise ApiError("clear verification failed: target cell is not empty")
        return FormulaResult(
            operation=request.operation,
            workbook_id=request.workbook_id,
            range_a1=request.range_a1,
            status="success",
            resulting_formula=None,
        )

    def _batch_read(self, request: FormulaRequest, client: SheetsValuesClient) -> FormulaResult:
        ranges_a1 = request.ranges_a1 or []
        resulting_map = self._with_retry(
            operation_name="batch-read",
            max_retries=request.max_retries,
            func=lambda: client.batch_get_formulas(request.workbook_id, ranges_a1),
        )
        return FormulaResult(
            operation=request.operation,
            workbook_id=request.workbook_id,
            range_a1=",".join(ranges_a1),
            status="success",
            resulting_formula=json.dumps(resulting_map, sort_keys=True),
        )

    def _batch_create_or_update(self, request: FormulaRequest, client: SheetsValuesClient) -> FormulaResult:
        formula_by_range = request.formula_by_range or {}
        requested_formula = json.dumps(formula_by_range, sort_keys=True)
        self._with_retry(
            operation_name=request.operation,
            max_retries=request.max_retries,
            func=lambda: client.batch_write_formulas(request.workbook_id, formula_by_range),
        )
        resulting_map = self._with_retry(
            operation_name="batch-read-after-write",
            max_retries=request.max_retries,
            func=lambda: client.batch_get_formulas(request.workbook_id, list(formula_by_range.keys())),
        )
        if not self._formula_map_equivalent(formula_by_range, resulting_map):
            raise ApiError(
                "batch read-after-write verification failed: "
                f"expected '{formula_by_range}' but found '{resulting_map}'"
            )
        return FormulaResult(
            operation=request.operation,
            workbook_id=request.workbook_id,
            range_a1=",".join(formula_by_range.keys()),
            status="success",
            requested_formula=requested_formula,
            resulting_formula=json.dumps(resulting_map, sort_keys=True),
        )

    def _batch_clear(self, request: FormulaRequest, client: SheetsValuesClient) -> FormulaResult:
        ranges_a1 = request.ranges_a1 or []
        self._with_retry(
            operation_name="batch-clear",
            max_retries=request.max_retries,
            func=lambda: client.batch_clear_formulas(request.workbook_id, ranges_a1),
        )
        resulting_map = self._with_retry(
            operation_name="batch-read-after-clear",
            max_retries=request.max_retries,
            func=lambda: client.batch_get_formulas(request.workbook_id, ranges_a1),
        )
        if any(resulting_map.get(range_a1) is not None for range_a1 in ranges_a1):
            raise ApiError("batch clear verification failed: one or more target cells are not empty")
        return FormulaResult(
            operation=request.operation,
            workbook_id=request.workbook_id,
            range_a1=",".join(ranges_a1),
            status="success",
            resulting_formula=json.dumps(resulting_map, sort_keys=True),
        )

    def _with_retry(self, operation_name: str, max_retries: int, func):
        attempts = max(0, max_retries)
        for attempt in range(attempts + 1):
            try:
                return func()
            except HttpError as exc:
                status = getattr(getattr(exc, "resp", None), "status", None)
                if status not in TRANSIENT_HTTP_STATUSES or attempt >= attempts:
                    raise ApiError(
                        f"{operation_name} failed with status {status}: {exc}"
                    ) from exc
                sleep_seconds = min((2**attempt) + random.random(), DEFAULT_MAX_BACKOFF_SECONDS)
                time.sleep(sleep_seconds)
            except ApiError:
                raise
            except Exception as exc:  # noqa: BLE001
                raise ApiError(f"{operation_name} failed: {exc}") from exc

        raise ApiError(f"{operation_name} failed after retries")

    @staticmethod
    def _formula_equivalent(requested_formula: str | None, resulting_formula: str | None) -> bool:
        if requested_formula == resulting_formula:
            return True
        if requested_formula is None or resulting_formula is None:
            return False
        return FormulaService._canonicalize_formula(requested_formula) == FormulaService._canonicalize_formula(
            resulting_formula
        )

    @staticmethod
    def _formula_map_equivalent(
        requested_formula_by_range: dict[str, str],
        resulting_formula_by_range: dict[str, str | None],
    ) -> bool:
        for range_a1, requested_formula in requested_formula_by_range.items():
            if not FormulaService._formula_equivalent(requested_formula, resulting_formula_by_range.get(range_a1)):
                return False
        return True

    @staticmethod
    def _canonicalize_formula(formula_text: str) -> str:
        normalized = formula_text.strip().upper().replace(" ", "").replace("$", "")

        def _normalize_range(match_obj: re.Match[str]) -> str:
            left = match_obj.group(1)
            right = match_obj.group(2)
            left_key = FormulaService._cell_key(left)
            right_key = FormulaService._cell_key(right)
            if left_key <= right_key:
                return f"{left}:{right}"
            return f"{right}:{left}"

        return RANGE_REF_REGEX.sub(_normalize_range, normalized)

    @staticmethod
    def _cell_key(cell_ref: str) -> tuple[int, int]:
        match_obj = CELL_REF_REGEX.match(cell_ref)
        if not match_obj:
            return (0, 0)
        col_text = match_obj.group(1)
        row_number = int(match_obj.group(2))
        col_number = 0
        for char in col_text:
            col_number = (col_number * 26) + (ord(char) - ord("A") + 1)
        return (col_number, row_number)
