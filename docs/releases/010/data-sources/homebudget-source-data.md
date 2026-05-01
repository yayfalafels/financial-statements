# HomeBudget Source Data Guide

This guide documents HomeBudget source-data references used by requirements and inspection work. It is not a tool usage guide.

## Boundary

- Use this guide for source-data location and field reference context.
- Use `homebudget` skill for procedural steps, command usage, and troubleshooting.

## Source Artifacts

- HomeBudget database file: `%USERPROFILE%\OneDrive\Documents\HomeBudgetData\Data\homebudget.db`
- HomeBudget config file: `%USERPROFILE%\OneDrive\Documents\HomeBudgetData\hb-config.json`
- Repository sample inputs for monthly close context: `data/monthly-closing/*`

## Core Source Entities

- Accounts: account list and account metadata consumed by close workflows.
- Categories and subcategories: expense hierarchy used for stage-1 mapping.
- Transactions: expenses, income, and transfers used for reconcile and posting logic.
- Sync metadata: sync tracking rows used by HomeBudget synchronization behavior.

## Required Reference Fields for Inspection Evidence

- Transaction identifiers and dates.
- Account identifiers and account display names.
- Category and subcategory labels where present.
- Amount, currency, and notes/description fields.
- Any source keys needed for replay and lineage.

