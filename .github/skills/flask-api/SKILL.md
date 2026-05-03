---
name: flask-api
description: Use when working on the Flask and Waitress backend API boundary, route contracts, payload validation, request orchestration, and module integration for monthly close workflows.
---

# Flask API

## Summary

Use this skill for reusable Flask, Pydantic, and Waitress knowledge that applies to the backend API boundary. Keep app-specific orchestration and domain ownership in the agent file. Use this skill for the generic framework guidance underneath that boundary.

## Apply This Skill When

- Defining or updating Flask routes for close-session, mapping, statement, or publish actions.
- Designing request and response payloads enforced with Pydantic models.
- Organizing backend API modules that delegate to orchestrator, runtime, adapter, and builder components.
- Wiring Waitress hosting, config loading, and boundary-level error mapping for Windows local execution.

## Rules

- Keep Flask routes thin. Route handlers validate, authorize the action, and delegate.
- Treat Pydantic models as the contract boundary for inbound and outbound payloads.
- Prefer explicit model validation errors over ad hoc request parsing.
- Use strict or carefully chosen coercion behavior at boundary models rather than relying on implicit downstream conversion.
- Keep production hosting on Waitress rather than Flask's development server.
- Normalize errors to typed API responses instead of leaking raw tracebacks across the boundary.
- Keep secrets, workbook identifiers, bucket identifiers, and service account paths in config, never inline.

## Official Sources

- Flask documentation: https://flask.palletsprojects.com/en/stable/
	Flask's user guide emphasizes application structure, blueprints, request handling, configuration, JSON responses, and dedicated error-handling patterns.
- Waitress documentation: https://docs.pylonsproject.org/projects/waitress/en/stable/
	Waitress is a production-quality pure-Python WSGI server with Windows support; its usage and reverse-proxy docs matter more than Flask's dev server docs for this repo.
- Pydantic documentation: https://pydantic.dev/docs/validation/latest/get-started/
	Pydantic highlights typed validation, strict versus lax modes, JSON Schema output, and structured validation errors that are useful at API boundaries.

## Useful Takeaways

- Flask's blueprint and application-structure guidance supports splitting the API by module boundary instead of building one monolithic route file.
- Flask's error-handling docs explicitly support returning JSON error payloads from registered handlers instead of ad hoc try and except blocks in every route.
- Waitress docs note current proxy-header hardening defaults and recommend explicit reverse-proxy configuration when trusted headers are involved.
- Pydantic's validation model is best used at the boundary once, then passed downstream as typed data.

## Validation Focus

- Route names and payload fields align with workflow stage and parameter naming.
- Handler logic delegates to the correct component boundary.
- Error responses are deterministic and user-facing at the boundary.
- API changes do not bypass adapter ownership rules.