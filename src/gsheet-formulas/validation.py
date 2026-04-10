#!/usr/bin/env python
from __future__ import annotations

import json
import os
import re

from errors import ValidationError
from models import FormulaRequest

# Accept either plain A1 or Sheet Name!A1 including quoted sheet names.
CELL_REF_PATTERN = r"\$?[A-Za-z]{1,3}\$?[1-9][0-9]*"
SHEET_NAME_PATTERN = r"(?:'[^']+(?:''[^']+)*'|[A-Za-z0-9_. -]+)!"
SINGLE_CELL_A1_REGEX = re.compile(rf"^(?:{SHEET_NAME_PATTERN})?{CELL_REF_PATTERN}$")
REQUIRED_SERVICE_ACCOUNT_KEYS = {"type", "client_email", "private_key"}


class InputValidator:
    def validate(self, request: FormulaRequest) -> None:
        self.validate_client_secret(request.client_secret)
        self.validate_workbook_id(request.workbook_id)
        if request.operation in {"read", "create", "update", "clear"}:
            self.validate_range_a1(request.range_a1)
        if request.operation in {"create", "update"}:
            self.validate_formula_text(request.formula_text)
        if request.operation in {"batch-read", "batch-clear"}:
            self.validate_ranges_list(request.ranges_a1)
        if request.operation in {"batch-create", "batch-update"}:
            self.validate_formula_by_range(request.formula_by_range)

    def validate_ranges_list(self, ranges_a1: list[str] | None) -> None:
        if not ranges_a1:
            raise ValidationError("ranges are required for batch operations")
        for range_a1 in ranges_a1:
            self.validate_range_a1(range_a1)

    def validate_formula_by_range(self, formula_by_range: dict[str, str] | None) -> None:
        if not formula_by_range:
            raise ValidationError("formula mapping is required for batch create and update")
        for range_a1, formula_text in formula_by_range.items():
            self.validate_range_a1(range_a1)
            self.validate_formula_text(formula_text)

    def validate_client_secret(self, client_secret: str) -> None:
        if not client_secret or not client_secret.strip():
            raise ValidationError("client secret path is required")
        if not os.path.isfile(client_secret):
            raise ValidationError(f"client secret file not found: {client_secret}")
        try:
            with open(client_secret, "r", encoding="utf-8") as file_obj:
                payload = json.load(file_obj)
        except OSError as exc:
            raise ValidationError(f"client secret file not readable: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise ValidationError(f"client secret file is not valid JSON: {exc}") from exc

        missing_keys = REQUIRED_SERVICE_ACCOUNT_KEYS.difference(payload.keys())
        if missing_keys:
            missing_keys_text = ", ".join(sorted(missing_keys))
            raise ValidationError(f"client secret JSON missing keys: {missing_keys_text}")

    def validate_workbook_id(self, workbook_id: str) -> None:
        if not workbook_id or not workbook_id.strip():
            raise ValidationError("workbook id is required")

    def validate_range_a1(self, range_a1: str) -> None:
        if not range_a1 or not range_a1.strip():
            raise ValidationError("range is required")
        normalized = range_a1.strip()
        if ":" in normalized or "," in normalized:
            raise ValidationError("range must be a single cell A1 reference")
        if not SINGLE_CELL_A1_REGEX.match(normalized):
            raise ValidationError("range must be a valid single cell A1 reference")

    def validate_formula_text(self, formula_text: str | None) -> None:
        if formula_text is None or not formula_text.strip():
            raise ValidationError("formula is required for create and update")
        if not formula_text.strip().startswith("="):
            raise ValidationError("formula must start with '='")
