#!/usr/bin/env python
from __future__ import annotations

from google.oauth2 import service_account
from googleapiclient.discovery import build

from errors import ApiError

SHEETS_SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


class SheetsAuth:
    def build_service(self, client_secret: str, max_retries: int):
        try:
            credentials = service_account.Credentials.from_service_account_file(
                client_secret,
                scopes=SHEETS_SCOPES,
            )
            return build(
                "sheets",
                "v4",
                credentials=credentials,
                cache_discovery=False,
                num_retries=max_retries,
            )
        except Exception as exc:  # noqa: BLE001
            raise ApiError(f"failed to initialize google sheets client: {exc}") from exc
