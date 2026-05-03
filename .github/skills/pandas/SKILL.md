---
name: pandas
description: Use when working on tabular data transforms, ingest staging, normalization, reconciliation aggregation, and statement assembly using the pandas DataFrame and Series API.
---

# pandas

## Summary

Use this skill for reusable pandas knowledge that applies to any module reading, transforming, or staging tabular financial data. Keep domain-specific transform logic in the component agent. Use this skill for generic DataFrame and Series API guidance.

## Apply This Skill When

- Reading source files (CSV, Excel, database) into DataFrames for staging or validation.
- Normalizing, filtering, grouping, or reshaping tabular data before persisting to SQLite.
- Aggregating rows for reconciliation summaries or statement line items.
- Merging or joining DataFrames across account or transaction datasets.
- Exporting DataFrames back to CSV, Excel, or SQLite for downstream consumption.

## Rules

- Prefer `pd.read_csv()`, `pd.read_excel()`, and `pd.read_sql()` as IO entry points; pass `dtype` where column types must be strict.
- Do not use `float` for monetary columns; read them as `str` then convert to `decimal.Decimal` before arithmetic.
- Use `DataFrame.copy()` when modifying a slice to avoid `SettingWithCopyWarning`.
- Prefer `DataFrame.assign()` over direct column mutation when building transform chains.
- Use `DataFrame.groupby(...).agg(...)` for aggregation; keep aggregation expressions explicit rather than relying on implicit defaults.
- Use `DataFrame.merge()` with explicit `how=` and `on=` arguments; never rely on positional join behavior.
- Avoid iterating rows with `iterrows()`; prefer vectorized operations or `DataFrame.apply()` as a last resort.
- Set `index_col` and `parse_dates` explicitly when reading source files that have natural keys or date columns.
- Use `DataFrame.to_sql()` with `if_exists='replace'` or `'append'` deliberately and document the intent.

## Official Sources

- pandas documentation: https://pandas.pydata.org/docs/
  The user guide covers IO tools, indexing, groupby, merge/join, and time series handling. The API reference covers every method signature and behavior.
- pandas overview: https://pandas.pydata.org/docs/getting_started/overview.html
  Describes Series (1D labeled array) and DataFrame (2D labeled tabular structure) as the two primary data structures, and explains why they exist as flexible containers for financial and statistical data.

## Useful Takeaways

- DataFrame columns with heterogeneous types are the intended use case; this is why pandas uses object dtype for mixed or string columns.
- `groupby` plus `agg` supports multiple named aggregations per column in a single pass, which is preferable to chaining multiple `groupby` calls.
- `pd.read_sql()` accepts both raw SQL strings and SQLAlchemy selectable objects; either works with the sqlite3 connection.
- pandas preserves trailing zeros in string representations but not in `float64` columns, which is another reason to avoid float for monetary values.

## Validation Focus

- Monetary columns are never float64 after reading; they are string or Decimal.
- Merge keys are specified explicitly; shape before and after merge is verified.
- Aggregation column names match the downstream schema expectation.
- DataFrames passed to `to_sql()` have been validated and staged before the call.
