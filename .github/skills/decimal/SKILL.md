---
name: decimal
description: Use when working on exact monetary arithmetic, financial rounding, currency conversion, allocation, and any operation where float precision errors are unacceptable.
---

# decimal

## Summary

Use this skill for reusable Python `decimal` module knowledge that applies to any calculation involving monetary amounts, exchange rates, pro-rata splits, or balance reconciliation. Keep domain-specific rounding policies in the component agent. Use this skill for generic Decimal API guidance.

## Apply This Skill When

- Performing addition, subtraction, multiplication, or division on monetary amounts.
- Rounding a result to a fixed number of decimal places (e.g. 2 for SGD/USD, 0 for JPY).
- Applying a forex rate to a base-currency amount to produce a reporting-currency amount.
- Allocating a total across multiple line items proportionally.
- Validating that a computed total equals the sum of its parts exactly.

## Rules

- Always construct `Decimal` from a string literal or an integer, never from a `float`: `Decimal('1.05')` not `Decimal(1.05)`.
- Use `.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)` for standard monetary rounding to 2 decimal places.
- Choose the rounding mode deliberately per domain rule: `ROUND_HALF_UP` for most financial values, `ROUND_HALF_EVEN` for statistical averages, `ROUND_DOWN` for fee calculations that must never exceed the actual amount.
- Never mix `Decimal` and `float` in the same arithmetic expression; raise `FloatOperation` traps in debug contexts to catch accidental mixing.
- Use `localcontext()` to scope precision changes rather than modifying the global context permanently.
- Use `getcontext().prec` to set thread-global precision when a consistent high-precision context is needed across all calculations in a session.
- Set precision high enough for intermediate calculations (e.g. 28) and quantize only at the output boundary.

## Official Sources

- Python decimal module documentation: https://docs.python.org/3/library/decimal.html
  Covers the `Decimal` class, `Context`, `getcontext()`, `setcontext()`, `localcontext()`, all rounding modes (`ROUND_HALF_UP`, `ROUND_HALF_EVEN`, `ROUND_DOWN`, `ROUND_CEILING`, `ROUND_FLOOR`, `ROUND_UP`, `ROUND_05UP`), signal handling, and monetary application recipes.

## Useful Takeaways

- `Decimal('0.1') + Decimal('0.2') == Decimal('0.3')` is exactly `True`; this does not hold for `float`.
- `quantize()` is the standard method for fixed-point monetary rounding; it accepts an explicit `rounding` argument that overrides the current context.
- `localcontext(prec=42)` as a context manager restores the previous context on exit, making it safe for scoped high-precision operations.
- `getcontext().traps[FloatOperation] = True` turns accidental float mixing into a raised exception during development.
- Significant trailing zeros are preserved: `Decimal('1.30')` stays as `1.30`, not `1.3`, which matters for monetary display.

## Validation Focus

- No `float` appears in any monetary variable after the input boundary.
- Every output monetary value has been quantized to the correct number of decimal places for its currency.
- Allocation totals are verified to sum exactly to the original before rounding adjustments are applied.
- Rounding mode is explicitly specified rather than relying on the context default.
