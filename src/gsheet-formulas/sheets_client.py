#!/usr/bin/env python
from __future__ import annotations

from googleapiclient.errors import HttpError

from errors import ApiError


class SheetsValuesClient:
    def __init__(self, sheets_service) -> None:
        self._values = sheets_service.spreadsheets().values()

    def get_formula(self, workbook_id: str, range_a1: str) -> str | None:
        try:
            response = (
                self._values.get(
                    spreadsheetId=workbook_id,
                    range=range_a1,
                    valueRenderOption="FORMULA",
                ).execute()
            )
        except HttpError as exc:
            raise ApiError(self._format_http_error("read", exc)) from exc

        values = response.get("values", [])
        if not values or not values[0]:
            return None
        token = values[0][0]
        return token if isinstance(token, str) and token.startswith("=") else None

    def write_formula(self, workbook_id: str, range_a1: str, formula_text: str) -> str | None:
        try:
            response = (
                self._values.update(
                    spreadsheetId=workbook_id,
                    range=range_a1,
                    valueInputOption="USER_ENTERED",
                    includeValuesInResponse=True,
                    responseValueRenderOption="FORMULA",
                    body={"values": [[formula_text]]},
                ).execute()
            )
        except HttpError as exc:
            raise ApiError(self._format_http_error("write", exc)) from exc

        updated_data = response.get("updatedData", {})
        values = updated_data.get("values", [])
        if not values or not values[0]:
            return None
        token = values[0][0]
        return token if isinstance(token, str) else None

    def clear_formula(self, workbook_id: str, range_a1: str) -> None:
        try:
            self._values.clear(
                spreadsheetId=workbook_id,
                range=range_a1,
                body={},
            ).execute()
        except HttpError as exc:
            raise ApiError(self._format_http_error("clear", exc)) from exc

    def batch_get_formulas(self, workbook_id: str, ranges_a1: list[str]) -> dict[str, str | None]:
        try:
            response = (
                self._values.batchGet(
                    spreadsheetId=workbook_id,
                    ranges=ranges_a1,
                    valueRenderOption="FORMULA",
                ).execute()
            )
        except HttpError as exc:
            raise ApiError(self._format_http_error("batch-read", exc)) from exc

        formulas_by_range: dict[str, str | None] = {range_a1: None for range_a1 in ranges_a1}
        for value_range in response.get("valueRanges", []):
            range_name = value_range.get("range", "")
            # API may return canonicalized A1 notation; first cell token still maps to requested order.
            values = value_range.get("values", [])
            token = None
            if values and values[0]:
                first_value = values[0][0]
                if isinstance(first_value, str) and first_value.startswith("="):
                    token = first_value
            # Preserve request ordering and fallback matching by exact range when available.
            if range_name in formulas_by_range:
                formulas_by_range[range_name] = token
            else:
                for request_range in ranges_a1:
                    if formulas_by_range[request_range] is None:
                        formulas_by_range[request_range] = token
                        break
        return formulas_by_range

    def batch_write_formulas(self, workbook_id: str, formula_by_range: dict[str, str]) -> dict[str, str | None]:
        data = [{"range": range_a1, "values": [[formula_text]]} for range_a1, formula_text in formula_by_range.items()]
        try:
            response = (
                self._values.batchUpdate(
                    spreadsheetId=workbook_id,
                    body={
                        "valueInputOption": "USER_ENTERED",
                        "includeValuesInResponse": True,
                        "responseValueRenderOption": "FORMULA",
                        "data": data,
                    },
                ).execute()
            )
        except HttpError as exc:
            raise ApiError(self._format_http_error("batch-write", exc)) from exc

        response_tokens: dict[str, str | None] = {}
        response_ranges = list(formula_by_range.keys())
        for index, item in enumerate(response.get("responses", [])):
            range_a1 = response_ranges[index] if index < len(response_ranges) else ""
            updated_data = item.get("updatedData", {})
            values = updated_data.get("values", [])
            token = None
            if values and values[0]:
                first_value = values[0][0]
                token = first_value if isinstance(first_value, str) else None
            if range_a1:
                response_tokens[range_a1] = token
        return response_tokens

    def batch_clear_formulas(self, workbook_id: str, ranges_a1: list[str]) -> list[str]:
        try:
            response = (
                self._values.batchClear(
                    spreadsheetId=workbook_id,
                    body={"ranges": ranges_a1},
                ).execute()
            )
        except HttpError as exc:
            raise ApiError(self._format_http_error("batch-clear", exc)) from exc
        return response.get("clearedRanges", [])

    @staticmethod
    def _format_http_error(operation: str, exc: HttpError) -> str:
        status = getattr(getattr(exc, "resp", None), "status", "unknown")
        return f"{operation} request failed with status {status}: {exc}"
