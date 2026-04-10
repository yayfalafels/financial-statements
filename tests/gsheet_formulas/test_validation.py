from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

SOURCE_DIR = Path(__file__).resolve().parents[2] / "src" / "gsheet-formulas"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from models import FormulaRequest
from validation import InputValidator


@pytest.fixture()
def service_account_file(tmp_path: Path) -> str:
    path = tmp_path / "service-account.json"
    payload = {
        "type": "service_account",
        "client_email": "svc@example.com",
        "private_key": "-----BEGIN PRIVATE KEY-----\\nkey\\n-----END PRIVATE KEY-----\\n",
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return str(path)


def build_request(service_account_file: str, **overrides) -> FormulaRequest:
    base = FormulaRequest(
        operation="read",
        client_secret=service_account_file,
        workbook_id="workbook-id",
        range_a1="A1",
    )
    request_dict = base.__dict__ | overrides
    return FormulaRequest(**request_dict)


def test_validate_accepts_single_cell_range(service_account_file: str) -> None:
    request = build_request(service_account_file, range_a1="Sheet 1!$B$10")
    InputValidator().validate(request)


def test_validate_rejects_multi_cell_range(service_account_file: str) -> None:
    request = build_request(service_account_file, range_a1="A1:B2")
    with pytest.raises(Exception):
        InputValidator().validate(request)


def test_validate_rejects_formula_without_equals(service_account_file: str) -> None:
    request = build_request(
        service_account_file,
        operation="create",
        formula_text="SUM(A1:A3)",
    )
    with pytest.raises(Exception):
        InputValidator().validate(request)


def test_validate_rejects_missing_workbook(service_account_file: str) -> None:
    request = build_request(service_account_file, workbook_id=" ")
    with pytest.raises(Exception):
        InputValidator().validate(request)


def test_validate_batch_read_accepts_ranges(service_account_file: str) -> None:
    request = build_request(
        service_account_file,
        operation="batch-read",
        range_a1="",
        ranges_a1=["A1", "B2"],
    )
    InputValidator().validate(request)


def test_validate_batch_create_requires_formula_map(service_account_file: str) -> None:
    request = build_request(
        service_account_file,
        operation="batch-create",
        range_a1="",
        formula_by_range={"A1": "=1+1", "B2": "=2+2"},
    )
    InputValidator().validate(request)


def test_validate_batch_create_rejects_invalid_formula(service_account_file: str) -> None:
    request = build_request(
        service_account_file,
        operation="batch-create",
        range_a1="",
        formula_by_range={"A1": "SUM(A1:A3)"},
    )
    with pytest.raises(Exception):
        InputValidator().validate(request)
