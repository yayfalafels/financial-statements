#!/usr/bin/env python

import calendar
import csv
import datetime as dt
import json
from pathlib import Path
from typing import Any

from homebudget import HomeBudgetClient

DEFAULT_ACCOUNTS_CONFIG = Path("data/monthly-closing/balance-accounts.json")
DEFAULT_OUTPUT_CSV = Path("data/monthly-closing/account-balances.csv")
CSV_HEADERS = ["year", "month", "alias", "balance"]


def parse_key_value_args(raw_args: list[str]) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for raw_arg in raw_args:
        if ":" not in raw_arg:
            raise ValueError(
                f"Invalid argument '{raw_arg}'. Expected format: key:value"
            )

        key, value = raw_arg.split(":", 1)
        normalized_key = key.strip().replace("-", "_")
        parsed[normalized_key] = value.strip()

    return parsed


def parse_month_id(month_id: Any) -> tuple[str, str]:
    month_id_str = str(month_id)
    if len(month_id_str) != 6 or not month_id_str.isdigit():
        raise ValueError(
            f"Invalid month_id '{month_id}'. Expected six-digit YYYYMM format."
        )

    year = month_id_str[:4]
    month = month_id_str[4:6]
    return year, month


def load_accounts(accounts_config_path: Path) -> list[dict[str, Any]]:
    with accounts_config_path.open("r", encoding="utf-8") as file_handle:
        loaded_json = json.load(file_handle)

    if not isinstance(loaded_json, list):
        raise ValueError("Accounts config must be a JSON list.")

    return loaded_json


def get_month_end_date(year: str, month: str) -> dt.date:
    year_num = int(year)
    month_num = int(month)
    last_day = calendar.monthrange(year_num, month_num)[1]
    return dt.date(year_num, month_num, last_day)


def build_rows(accounts: list[dict[str, Any]], client: HomeBudgetClient) -> list[list[Any]]:
    rows: list[list[Any]] = []

    for account in accounts:
        account_name = account.get("name")
        alias = account.get("alias")
        if not account_name:
            raise ValueError(f"Missing account name for account: {account}")
        if not alias:
            raise ValueError(f"Missing alias for account: {account}")

        balances = account.get("balances", [])
        if not isinstance(balances, list):
            raise ValueError(f"Invalid balances list for alias '{alias}'")

        for balance_record in balances:
            month_id = balance_record.get("month_id")
            year, month = parse_month_id(month_id)
            month_end_date = get_month_end_date(year, month)
            balance_value = client.get_account_balance(account_name, month_end_date).balanceAmount
            rows.append([year, month, alias, balance_value])

    return rows


def write_csv(output_path: Path, rows: list[list[Any]]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as file_handle:
        writer = csv.writer(file_handle)
        writer.writerow(CSV_HEADERS)
        writer.writerows(rows)


def main() -> None:
    import sys

    args = parse_key_value_args(sys.argv[1:])

    unknown_keys = set(args.keys()) - {"accounts_config", "output_csv"}
    if unknown_keys:
        allowed_keys = "accounts_config, output_csv"
        unknown_keys_list = ", ".join(sorted(unknown_keys))
        raise ValueError(f"Unknown argument key(s): {unknown_keys_list}. Allowed: {allowed_keys}")

    accounts_config_arg = args.get("accounts_config")
    output_csv_arg = args.get("output_csv")

    accounts_config_path = Path(accounts_config_arg) if accounts_config_arg else DEFAULT_ACCOUNTS_CONFIG
    output_csv_path = Path(output_csv_arg) if output_csv_arg else DEFAULT_OUTPUT_CSV

    accounts = load_accounts(accounts_config_path)
    with HomeBudgetClient() as client:
        rows = build_rows(accounts, client)
    write_csv(output_csv_path, rows)

    print(f"Wrote {len(rows)} row(s) to {output_csv_path}")


if __name__ == "__main__":
    main()
