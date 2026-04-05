# HomeBudget

This page defines the requirement-level boundary for HomeBudget usage.

Detailed inspection and implementation procedures are maintained in the HomeBudget skill guide:

- skill `homebudget`

For source-data structure and field references that are not tool procedures, use:

- docs/develop/data-sources/homebudget-source-data.md

## Scope in Requirements

HomeBudget is the system of record for:

- Account definitions used by the monthly closing process.
- Expense, income, and transfer transactions used for posting and reconciliation.
- Transaction metadata required for downstream lineage and replay behavior.

This page intentionally avoids duplicating command-level workflow steps. Those steps belong in the skill guides.

## Procedural Source of Truth

When execution details are needed, use the following precedence:

1. skill `homebudget`
2. skill `data-sources-inspect`
3. This requirement page for scope and acceptance boundaries only
