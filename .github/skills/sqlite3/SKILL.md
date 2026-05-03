---
name: sqlite3
description: Use when working on any direct sqlite3 module usage including connection management, cursor operations, transaction control, and parameterized query execution.
---

# sqlite3

## Summary

Use this skill for reusable Python `sqlite3` stdlib knowledge that applies to any module operating the SQLite local database. Keep schema definitions, query logic, and persistence contracts in the SQLite adapter agent. Use this skill for generic connection, cursor, transaction, and type-mapping API guidance.

## Apply This Skill When

- Opening or closing a connection to the local SQLite file.
- Executing a parameterized query or batch insert.
- Managing transactions: committing, rolling back, or using context manager auto-commit.
- Mapping Python types to SQLite column types or registering custom adapters.
- Enabling row factory access for named column lookups.

## Rules

- Always use `?` placeholders for parameterized queries: `cur.execute("SELECT * FROM t WHERE id = ?", (id,))`. Never interpolate values via f-strings or `%` formatting.
- Use `con.row_factory = sqlite3.Row` to enable column-name access on result rows: `row['column_name']`.
- Use `with con:` as a transaction context manager; it commits on clean exit and rolls back on exception.
- Prefer `autocommit=False` (PEP 249 compliant, default in Python 3.12+) for explicit transaction control; avoid implicit transaction behavior from legacy isolation_level settings.
- Use `cur.executemany(sql, list_of_tuples)` for batch inserts rather than looping `cur.execute()` inside Python.
- Use `cur.fetchall()` for small result sets; use `cur.fetchone()` for single-row lookups; use the cursor as an iterator for large result sets to avoid loading all rows into memory.
- Call `con.close()` explicitly when done, or open the connection with a context manager where supported.
- Register custom type adapters with `sqlite3.register_adapter()` and `sqlite3.register_converter()` for `Decimal` or `datetime` types when storing non-native types.

## Official Sources

- Python sqlite3 module documentation: https://docs.python.org/3/library/sqlite3.html
  Covers the DB-API 2.0 interface (PEP 249), `connect()`, `Connection`, `Cursor`, `Row`, transaction control, type mapping, adapter registration, and security guidance on parameterized queries.

## Useful Takeaways

- SQLite type affinity: Python `None` ↔ `NULL`, `int` ↔ `INTEGER`, `float` ↔ `REAL`, `str` ↔ `TEXT`, `bytes` ↔ `BLOB`.
- `sqlite3.Row` acts like both a tuple and a mapping; `row['col']` and `row[0]` both work.
- The `with con:` context manager does not open and close the connection; it only manages the transaction. Open and close the connection separately.
- `detect_types=sqlite3.PARSE_DECLTYPES` enables automatic type conversion for registered converters when reading from the database.
- SQL injection via `?` placeholders is the baseline security requirement; there are no exceptions.

## Validation Focus

- Every query uses `?` placeholders; no string interpolation in SQL text.
- `con.row_factory = sqlite3.Row` is set before any query that accesses columns by name.
- Batch operations use `executemany()`; Python-level loops over `execute()` are not used for bulk inserts.
- Custom adapters are registered for `Decimal` if monetary amounts are stored as TEXT and retrieved back as `Decimal`.
