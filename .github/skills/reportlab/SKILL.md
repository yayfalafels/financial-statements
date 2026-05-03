---
name: reportlab
description: Use when generating PDF documents directly from Python for financial statement publishing, invoice rendering, or any publish-stage artifact that requires programmatic PDF layout.
---

# reportlab

## Summary

Use this skill for reusable ReportLab knowledge that applies to PDF generation at the statement-builder or publish stage. Keep document templates, style definitions, and statement-specific layout logic in the statement-builder agent. Use this skill for generic ReportLab canvas and Platypus API guidance.

## Apply This Skill When

- Generating a PDF financial statement, summary report, or review draft from Python.
- Composing a multi-page document with tables, headings, paragraphs, and page breaks.
- Applying a consistent font, style, and page size to published output.
- Embedding tables with column spans, row styles, or conditional formatting.
- Adding page numbers, headers, or footers to a multi-page PDF.

## Rules

- Prefer the Platypus high-level API (`SimpleDocTemplate`, `Paragraph`, `Table`, `Spacer`) over the low-level `pdfgen.canvas` API for documents with flowing content.
- Use the `pdfgen.canvas` API only for fixed-position drawing, custom watermarks, or content that does not flow across pages.
- Define styles using `getSampleStyleSheet()` and extend or override as needed rather than repeating inline style dicts.
- Pass `Decimal` or string values to table cells; do not pass `float` values directly into financial table cells.
- Use `SimpleDocTemplate(path, pagesize=A4, ...)` as the entry point; set margins explicitly.
- Use `Table(data, colWidths=[...])` with explicit column widths for financial tables to ensure layout stability across runs.
- Call `doc.build(story)` as the final step; the `story` list is the ordered sequence of Platypus flowables.

## Official Sources

- ReportLab user guide: https://docs.reportlab.com/reportlab/userguide/ch1_intro/
  Introduces the two-layer architecture: low-level pdfgen canvas for direct PDF construction, and Platypus (Page Layout and Typography Using Scripts) for flowable, document-structured output.
- ReportLab open-source page: https://www.reportlab.com/opensource/
  Covers the open-source tier (ReportLab Toolkit) that this project uses, including installation and the Python 3.6+ compatibility baseline.

## Useful Takeaways

- Platypus flowable types most useful for financial statements: `Paragraph` (formatted text), `Table` (tabular data with style rules), `Spacer` (vertical whitespace), `PageBreak`, `KeepTogether`.
- `TableStyle` applies cell formatting by coordinate ranges: `('BACKGROUND', (col, row), (col, row), color)`.
- `SimpleDocTemplate` triggers a two-pass build so that page numbers can be resolved before the first pass completes.
- ReportLab can embed images, charts (from `reportlab.graphics`), and barcodes, but these are rarely needed for plain financial statement PDFs.

## Validation Focus

- All monetary values entering table cells are strings or Decimal, not float.
- Column widths are explicit and the total does not exceed the usable page width.
- Document is built once and the output path is verified to exist after `doc.build()`.
- Style overrides extend `getSampleStyleSheet()` rather than replacing it entirely.
