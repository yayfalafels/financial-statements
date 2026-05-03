---
name: httpx
description: Use when making HTTP requests to external APIs such as forex rate providers, or any outbound HTTP call from the backend or adapter layer.
---

# httpx

## Summary

Use this skill for reusable httpx knowledge that applies to any module making outbound HTTP calls. Keep API-specific URL construction, response parsing, and retry policy in the component adapter. Use this skill for generic httpx client, timeout, and session management guidance.

## Apply This Skill When

- Fetching forex exchange rates from an external HTTP API (e.g. Yahoo Finance).
- Making authenticated or unauthenticated GET/POST requests from a backend or adapter module.
- Managing connection pooling across multiple requests within a single session.
- Handling HTTP errors, timeouts, and retries at the adapter boundary.

## Rules

- Prefer `httpx.Client` over top-level `httpx.get()` for any workflow that makes more than one request; `Client` provides connection pooling and shared config.
- Always set explicit timeouts: `httpx.Client(timeout=httpx.Timeout(10.0, connect=5.0))`; never rely on default unlimited timeout.
- Catch `httpx.HTTPStatusError` (raised by `response.raise_for_status()`) and `httpx.RequestError` separately; map them to domain-specific exceptions at the adapter boundary.
- Call `response.raise_for_status()` before accessing `response.json()` or `response.text` to fail fast on non-2xx responses.
- Use `client.get(url, params=dict)` to pass query parameters; never build query strings by f-string concatenation.
- Avoid the async client (`httpx.AsyncClient`) in this codebase; all close-session workflows are synchronous.
- Close the client explicitly: use `httpx.Client()` as a context manager (`with httpx.Client() as client:`) to ensure connections are released.

## Official Sources

- httpx documentation: https://www.python-httpx.org/
  Covers the sync and async client APIs, request construction, response handling, timeouts, authentication, SSL verification, and HTTP/2 configuration.
- httpx quickstart: https://www.python-httpx.org/quickstart/
  Demonstrates the requests-compatible surface: `httpx.get()`, `httpx.post()`, `response.json()`, `response.raise_for_status()`.

## Useful Takeaways

- httpx is fully type-annotated, which enables editor completion on all request and response attributes.
- `httpx.Timeout` accepts four independent timeout phases: `connect`, `read`, `write`, and `pool`; setting all four explicitly prevents silent hangs.
- HTTP/2 is supported but must be enabled explicitly: `httpx.Client(http2=True)` requires the `h2` package.
- The requests-compatible API means most `requests`-style call patterns transfer directly to httpx with minimal changes.

## Validation Focus

- Every `httpx.Client` instance is created with explicit timeouts.
- `response.raise_for_status()` is called before any response content is accessed.
- Client is closed via context manager or explicit `.close()` call.
- URL construction uses `params=` rather than string concatenation.
