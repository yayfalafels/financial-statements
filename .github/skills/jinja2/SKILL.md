---
name: jinja2
description: Use when generating text output from templates, including HTML for WeasyPrint PDF rendering, statement summaries, email bodies, or structured text reports.
---

# jinja2

## Summary

Use this skill for reusable Jinja2 knowledge that applies to any module generating text or HTML from templates. Keep template files, context-building logic, and layout decisions in the component agent. Use this skill for generic Jinja2 Environment, Template, and rendering API guidance.

## Apply This Skill When

- Rendering HTML from a Jinja2 template for WeasyPrint PDF generation.
- Generating structured text output such as summary reports, notification bodies, or review drafts.
- Composing a template with variable substitution, conditional blocks, and loops.
- Using template inheritance to separate base layout from content-specific pages.
- Rendering a template from a file-based template directory using a `FileSystemLoader`.

## Rules

- Use `jinja2.Environment(loader=FileSystemLoader(template_dir), autoescape=select_autoescape(['html']))` for HTML output; autoescape prevents XSS when user data appears in templates.
- Use `autoescape=False` only for plain-text templates (e.g., CSV, markdown) where HTML escaping is not appropriate.
- Call `env.get_template('template_name.html').render(context_dict)` as the standard rendering pattern; pass context as a `dict`.
- Use template inheritance (`{% extends 'base.html' %}` + `{% block content %}`) to avoid duplicating layout across multiple statement templates.
- Use `{% macro name(args) %}...{% endmacro %}` to extract reusable table rows or repeated fragments rather than duplicating Jinja2 blocks.
- Keep business logic out of templates; templates should only display values, not compute them.
- Never pass raw `Decimal` objects into templates without converting to string first; Jinja2 may render them unexpectedly depending on the `str()` representation.
- Use `{{ value | round(2) }}` filters only for display purposes; never rely on Jinja2 filters for authoritative financial rounding.

## Official Sources

- Jinja2 documentation: https://jinja.palletsprojects.com/en/stable/
  Covers the template designer guide (syntax, inheritance, macros, filters, tests), the `Environment` and `Template` classes, autoescaping, and the sandbox extension.
- Jinja2 API reference: https://jinja.palletsprojects.com/en/stable/api/
  Describes `Environment`, `FileSystemLoader`, `select_autoescape()`, `Template.render()`, and global/filter/test extension points.

## Useful Takeaways

- Jinja2 compiles templates to Python bytecode and caches them; the `Environment` instance should be created once and reused, not recreated per render call.
- `select_autoescape(['html', 'xml'])` is the idiomatic way to enable autoescaping only for file types that need it.
- Template inheritance `{% block %}` can be overridden at arbitrary nesting levels; `super()` calls the parent block content.
- The `Undefined` type is returned for missing context variables by default; use `StrictUndefined` to raise an error on missing variables in production builds.

## Validation Focus

- HTML-generating templates use `autoescape=True` or `select_autoescape()`.
- No financial arithmetic is performed inside Jinja2 templates or filter chains.
- All `Decimal` values are converted to string before being passed into the template context.
- The `Environment` is instantiated once per render session, not per document.
