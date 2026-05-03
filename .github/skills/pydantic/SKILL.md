---
name: pydantic
description: Use when defining, validating, or serializing typed data models for API request and response payloads, configuration objects, or any structured data boundary in the backend.
---

# pydantic

## Summary

Use this skill for reusable Pydantic knowledge that applies to any module defining typed data models for validation or serialization. Keep domain-specific model classes and field semantics in the component agent. Use this skill for generic `BaseModel`, validators, and serialization API guidance.

## Apply This Skill When

- Defining a typed model for a Flask API request or response payload.
- Validating inbound JSON against a structured schema before passing to an orchestrator or runtime module.
- Serializing a domain object to a dict or JSON string for an API response.
- Configuring application settings from environment variables using `BaseSettings`.
- Generating JSON Schema output from a model class for documentation or contract testing.

## Rules

- Prefer `model_validate(data_dict)` over the deprecated `parse_obj()` for constructing a model from a dict.
- Use `model_dump()` to serialize to a dict and `model_dump_json()` for a JSON string; replace deprecated `.dict()` and `.json()` calls.
- Declare field constraints using `Field(...)` annotations: `ge`, `le`, `min_length`, `max_length`, `pattern`.
- Use `model_config = ConfigDict(strict=True)` when strict type coercion is required; use the default lax mode only when loose coercion is explicitly acceptable.
- Use `@field_validator('field_name', mode='before')` for pre-coercion cleanup and `@model_validator(mode='after')` for cross-field validation.
- Never use `Decimal` fields with the default JSON serializer without a custom encoder; Pydantic's JSON output serializes `Decimal` as a string by default in v2.
- Raise `ValueError` inside validators to produce `ValidationError`; do not raise custom exceptions inside validators.
- Use `BaseSettings` (from `pydantic-settings`) for environment-variable-backed config; do not use `BaseModel` for env config.

## Official Sources

- Pydantic documentation: https://docs.pydantic.dev/latest/
  Covers `BaseModel`, `Field`, `model_validate()`, `model_dump()`, `@field_validator`, `@model_validator`, `ConfigDict`, strict/lax modes, JSON Schema generation, and migration from v1 to v2.
- Pydantic concepts: https://docs.pydantic.dev/latest/concepts/models/
  Describes model definition, field declaration, validation behavior, serialization, and the difference between v1 and v2 API patterns.

## Useful Takeaways

- Pydantic v2 uses Rust-based validation (pydantic-core) and is significantly faster than v1; the API changed substantially between versions.
- `model_validate()` replaces `parse_obj()`, and `model_dump()` replaces `.dict()` in v2.
- `ValidationError` contains a list of error details accessible via `.errors()`; each entry includes the field path, error type, and message.
- `model_json_schema()` generates a JSON Schema dict from any `BaseModel` subclass, useful for API documentation or contract validation.
- Pydantic `Decimal` fields are validated correctly in Python but serialize to strings in JSON; annotate this behavior explicitly in API contracts.

## Validation Focus

- All API boundary models use `model_validate()` not positional construction.
- `ValidationError` is caught at the route handler and mapped to a typed error response.
- Fields with financial values use `Decimal` type, not `float`.
- `model_config = ConfigDict(strict=True)` is applied where implicit coercion (e.g., int→str) would mask upstream data errors.
