from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

SOURCE_DIR = Path(__file__).resolve().parents[2] / "src" / "gsheet-formulas"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from models import FormulaRequest
from service import FormulaService


class FakeValuesClient:
    def __init__(self) -> None:
        self.formula_by_cell: dict[tuple[str, str], str | None] = {}
        self.force_read_formula: str | None = None

    def get_formula(self, workbook_id: str, range_a1: str) -> str | None:
        if self.force_read_formula is not None:
            return self.force_read_formula
        return self.formula_by_cell.get((workbook_id, range_a1))

    def write_formula(self, workbook_id: str, range_a1: str, formula_text: str) -> str | None:
        self.formula_by_cell[(workbook_id, range_a1)] = formula_text
        return formula_text

    def clear_formula(self, workbook_id: str, range_a1: str) -> None:
        self.formula_by_cell[(workbook_id, range_a1)] = None

    def batch_get_formulas(self, workbook_id: str, ranges_a1: list[str]) -> dict[str, str | None]:
        return {range_a1: self.formula_by_cell.get((workbook_id, range_a1)) for range_a1 in ranges_a1}

    def batch_write_formulas(self, workbook_id: str, formula_by_range: dict[str, str]) -> dict[str, str | None]:
        for range_a1, formula_text in formula_by_range.items():
            self.formula_by_cell[(workbook_id, range_a1)] = formula_text
        return {range_a1: formula_by_range[range_a1] for range_a1 in formula_by_range}

    def batch_clear_formulas(self, workbook_id: str, ranges_a1: list[str]) -> list[str]:
        for range_a1 in ranges_a1:
            self.formula_by_cell[(workbook_id, range_a1)] = None
        return ranges_a1


class FakeAuth:
    def __init__(self) -> None:
        self.service = object()

    def build_service(self, client_secret: str, max_retries: int):
        return self.service


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


@pytest.fixture()
def monkeypatched_service(monkeypatch: pytest.MonkeyPatch) -> tuple[FormulaService, FakeValuesClient]:
    fake_client = FakeValuesClient()

    def fake_client_factory(_service):
        return fake_client

    monkeypatch.setattr("service.SheetsValuesClient", fake_client_factory)
    return FormulaService(auth=FakeAuth()), fake_client


def test_create_update_clear_success(
    service_account_file: str,
    monkeypatched_service: tuple[FormulaService, FakeValuesClient],
) -> None:
    service, fake_client = monkeypatched_service
    workbook_id = "wb"
    range_a1 = "A3"

    create_result = service.execute(
        FormulaRequest(
            operation="create",
            client_secret=service_account_file,
            workbook_id=workbook_id,
            range_a1=range_a1,
            formula_text="=1+1",
        )
    )
    assert create_result.status == "success"
    assert fake_client.formula_by_cell[(workbook_id, range_a1)] == "=1+1"

    update_result = service.execute(
        FormulaRequest(
            operation="update",
            client_secret=service_account_file,
            workbook_id=workbook_id,
            range_a1=range_a1,
            formula_text="=2+2",
        )
    )
    assert update_result.status == "success"
    assert fake_client.formula_by_cell[(workbook_id, range_a1)] == "=2+2"

    clear_result = service.execute(
        FormulaRequest(
            operation="clear",
            client_secret=service_account_file,
            workbook_id=workbook_id,
            range_a1=range_a1,
        )
    )
    assert clear_result.status == "success"
    assert fake_client.formula_by_cell[(workbook_id, range_a1)] is None


def test_read_empty_cell_returns_success(
    service_account_file: str,
    monkeypatched_service: tuple[FormulaService, FakeValuesClient],
) -> None:
    service, _ = monkeypatched_service
    result = service.execute(
        FormulaRequest(
            operation="read",
            client_secret=service_account_file,
            workbook_id="wb",
            range_a1="A3",
        )
    )
    assert result.status == "success"
    assert result.resulting_formula is None


def test_update_accepts_canonicalized_formula_from_api(
    service_account_file: str,
    monkeypatched_service: tuple[FormulaService, FakeValuesClient],
) -> None:
    service, fake_client = monkeypatched_service
    fake_client.force_read_formula = "=SUM(D2:$E2)"

    result = service.execute(
        FormulaRequest(
            operation="update",
            client_secret=service_account_file,
            workbook_id="wb",
            range_a1="A3",
            formula_text="=SUM($E2:D2)",
        )
    )

    assert result.status == "success"


def test_batch_create_read_clear_success(
    service_account_file: str,
    monkeypatched_service: tuple[FormulaService, FakeValuesClient],
) -> None:
    service, fake_client = monkeypatched_service
    workbook_id = "wb"
    formula_by_range = {"A1": "=1+1", "B2": "=2+2"}

    create_result = service.execute(
        FormulaRequest(
            operation="batch-create",
            client_secret=service_account_file,
            workbook_id=workbook_id,
            range_a1="",
            formula_by_range=formula_by_range,
        )
    )
    assert create_result.status == "success"
    assert fake_client.formula_by_cell[(workbook_id, "A1")] == "=1+1"
    assert fake_client.formula_by_cell[(workbook_id, "B2")] == "=2+2"

    read_result = service.execute(
        FormulaRequest(
            operation="batch-read",
            client_secret=service_account_file,
            workbook_id=workbook_id,
            range_a1="",
            ranges_a1=["A1", "B2"],
        )
    )
    assert read_result.status == "success"

    clear_result = service.execute(
        FormulaRequest(
            operation="batch-clear",
            client_secret=service_account_file,
            workbook_id=workbook_id,
            range_a1="",
            ranges_a1=["A1", "B2"],
        )
    )
    assert clear_result.status == "success"
    assert fake_client.formula_by_cell[(workbook_id, "A1")] is None
    assert fake_client.formula_by_cell[(workbook_id, "B2")] is None
