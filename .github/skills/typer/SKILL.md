---
name: typer
description: Use when building optional CLI entry points for close-session scripts, admin utilities, or developer tooling using Python type hints as the CLI contract.
---

# typer

## Summary

Use this skill for reusable Typer knowledge that applies to any CLI entry point in this project. Typer is optional in this codebase; it applies only when a script benefits from structured argument parsing and auto-generated help. Keep command logic thin; delegate to existing modules rather than duplicating logic in CLI commands.

## Apply This Skill When

- Adding a CLI interface to an existing Python script or module.
- Defining a multi-command CLI application with subcommands for distinct operations.
- Accepting typed arguments (dates, file paths, integers, enums) from the command line with validation.
- Providing auto-generated `--help` output for developer or operator tooling.

## Rules

- Use `typer.run(func)` for single-function scripts; use `app = typer.Typer()` with `@app.command()` for multi-command applications.
- Use Python type hints as the only API for declaring argument types; do not add manual argument parsing alongside Typer.
- Use `typer.Option(...)` with a `help=` string for every optional parameter so `--help` output is informative.
- Use `typer.Argument(...)` for required positional parameters.
- Keep command functions as thin orchestration wrappers; business logic stays in the module being called.
- Do not use Typer for the Flask API routes; Typer is for standalone CLI entry points only.
- `typer.Exit(code=1)` exits with a non-zero code on error; use it instead of `sys.exit(1)` inside Typer commands.

## Official Sources

- Typer documentation: https://typer.tiangolo.com/
  Covers `typer.run()`, `typer.Typer()`, `@app.command()`, `typer.Argument`, `typer.Option`, subcommands, parameter types (str, int, bool, Path, Enum, DateTime), auto-completion, and testing with `typer.testing.CliRunner`.
- Typer tutorial: https://typer.tiangolo.com/tutorial/
  Step-by-step guide from a minimal single-function CLI to multi-command applications with subcommands, options, callbacks, and progress bars.

## Useful Takeaways

- Typer is the FastAPI-style sibling of Click; it is built on Click and adds Python type hint inference over Click's explicit decorator API.
- Dependencies: Click (required), rich (for formatted error output), shellingham (for shell detection during completion install); all three are installed with `pip install typer`.
- Auto-completion for Bash, Zsh, Fish, and PowerShell is enabled by calling `app --install-completion` once after installation.
- `typer.testing.CliRunner` from Click is usable with Typer apps for unit testing commands without spawning a subprocess.

## Validation Focus

- All command parameters are declared with Python type hints; no manual `sys.argv` parsing appears alongside Typer.
- Every `typer.Option` has a `help=` string.
- Command functions delegate to existing module logic rather than reimplementing it.
- `typer.Exit(code=1)` is used for error exits rather than bare `sys.exit()`.
