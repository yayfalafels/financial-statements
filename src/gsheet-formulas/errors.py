#!/usr/bin/env python
from __future__ import annotations

from dataclasses import dataclass

EXIT_CODE_SUCCESS = 0
EXIT_CODE_VALIDATION = 2
EXIT_CODE_API = 3
EXIT_CODE_INTERNAL = 4

CATEGORY_VALIDATION = "validation"
CATEGORY_API = "api"
CATEGORY_INTERNAL = "internal"


@dataclass
class FormulaError(Exception):
    message: str
    category: str

    def __str__(self) -> str:
        return self.message


class ValidationError(FormulaError):
    def __init__(self, message: str) -> None:
        super().__init__(message=message, category=CATEGORY_VALIDATION)


class ApiError(FormulaError):
    def __init__(self, message: str) -> None:
        super().__init__(message=message, category=CATEGORY_API)


class InternalError(FormulaError):
    def __init__(self, message: str) -> None:
        super().__init__(message=message, category=CATEGORY_INTERNAL)


def exit_code_for_error(error: FormulaError) -> int:
    if error.category == CATEGORY_VALIDATION:
        return EXIT_CODE_VALIDATION
    if error.category == CATEGORY_API:
        return EXIT_CODE_API
    return EXIT_CODE_INTERNAL
