---
name: weasyprint
description: Use when generating PDFs from HTML and CSS templates as an alternative to ReportLab, particularly for statement layouts driven by HTML structure and CSS print rules.
---

# weasyprint

## Summary

Use this skill for reusable WeasyPrint knowledge that applies when HTML-and-CSS-driven PDF rendering is chosen instead of programmatic PDF construction. This skill is optional and applies only if WeasyPrint is used behind the PDF adapter contract. Keep layout templates and statement-specific CSS in the statement-builder agent. Use this skill for generic WeasyPrint Python API guidance.

## Apply This Skill When

- Rendering a financial statement, invoice, or report from an HTML template to PDF.
- Using CSS `@page` and `@media print` rules to control pagination, margins, and headers.
- Choosing between WeasyPrint (HTML/CSS driven) and ReportLab (programmatic) at the PDF adapter boundary.
- Embedding fonts, applying consistent branding, or reusing a web stylesheet for print output.

## Rules

- Use `weasyprint.HTML(string=html_str).write_pdf(path)` to render from an HTML string; use `weasyprint.HTML(filename=path)` for a local HTML file.
- Call `.write_pdf()` with no argument to return raw bytes in memory rather than writing to disk, when the output must be streamed or stored in S3.
- Pass a `base_url` argument when the HTML references relative CSS or image paths: `weasyprint.HTML(string=html_str, base_url=base_dir)`.
- Use CSS `@page` rules to set page size, margins, and running headers/footers rather than manipulating the Python API.
- Require Python 3.10 or later; WeasyPrint does not support Python 3.9 or below.
- Do not use WeasyPrint and ReportLab simultaneously for the same document; enforce a single PDF adapter path per environment.
- WeasyPrint is not based on WebKit or Gecko; test pagination behavior explicitly because it may differ from browser print preview.

## Official Sources

- WeasyPrint documentation: https://doc.courtbouillon.org/weasyprint/stable/
  Covers installation, Python library usage, CLI usage, common use cases (web applications, custom dimensions, PDF forms, metadata, attachments), and API reference.
- WeasyPrint first steps: https://doc.courtbouillon.org/weasyprint/stable/first_steps.html
  Shows the minimal Python API pattern and security considerations for untrusted HTML input.

## Useful Takeaways

- WeasyPrint's CSS layout engine is written in Python and targets pagination behavior specifically; it does not render all CSS properties that a browser would render.
- HTML + Jinja2 template rendering followed by `weasyprint.HTML(string=rendered_html).write_pdf()` is the recommended composition pattern when using both libraries.
- WeasyPrint is BSD-licensed free software maintained by CourtBouillon; it is the open-source successor to the original Kozea project.
- Security: if the HTML source is untrusted, apply content sanitization before passing to WeasyPrint, as it will follow `@import` and external resource links by default.

## Validation Focus

- Python version is 3.10 or later before WeasyPrint is imported.
- Only one PDF rendering path (WeasyPrint or ReportLab) is active per deployment; both are not called for the same artifact.
- `base_url` is set when HTML references local CSS or image assets.
- Untrusted HTML is sanitized before being passed to `weasyprint.HTML()`.
