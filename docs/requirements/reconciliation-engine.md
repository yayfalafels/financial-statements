# Reconciliation Engine

## Table of contents

- [Purpose and boundary](#purpose-and-boundary)
- [Reference documents](#reference-documents)
- [Primary scope](#primary-scope)
- [Out of scope](#out-of-scope)
- [Reconcile workflow stages and checkpoints](#reconcile-workflow-stages-and-checkpoints)
- [Tolerance rules and variance escalation](#tolerance-rules-and-variance-escalation)
- [Closure criteria and period acceptance conditions](#closure-criteria-and-period-acceptance-conditions)
- [Source-input contracts](#source-input-contracts)
- [Lineage and audit requirements](#lineage-and-audit-requirements)

## Purpose and boundary

This page is the normative owner for reconciliation-engine requirements.

## Reference documents

- [cash reconcile](cash-reconcile.md)
- [glossary](glossary.md)
- [source systems and lineage](source-systems-lineage.md)
- [workflow orchestration](workflow-orchestration.md)
- [exception and error handling](exception-error-handling.md)

## Primary scope

- Reconcile workflow and checkpoint expectations
- Tolerance and variance escalation policy
- Reconcile closure criteria by period
- Source-input contracts for reconcile execution

## Out of scope

- Workflow orchestration stage ordering
- Statement lifecycle publication policy
- Exception-policy remediation behavior details

## Reconcile workflow stages and checkpoints

| id | stage               | checkpoint focus                         |
| -- | ------------------- | ---------------------------------------- |
| 01 | source readiness    | required source datasets are available   |
| 02 | match and classify  | transaction and balance matching passes  |
| 03 | variance review     | residual variance reviewed and explained |
| 04 | close decision      | close criteria satisfied for all paths   |

## Tolerance rules and variance escalation

- Tolerance values are owned by this page.
- Cash adjustment alert threshold uses plus or minus SGD 20.
- Statement-digital-twin versus ledger reconcile uses exact match at account precision unless owner policy on this page is updated.
- Variance outside policy threshold triggers escalation and blocks close.

## Closure criteria and period acceptance conditions

- Required reconcile checks pass for in-scope accounts.
- Unexplained blocking variance is not present.
- Period reconcile output is recorded with lineage and checkpoint status.

## Source-input contracts

- Reconcile consumes statement digital twin, ledger, and mapping outputs.
- Inputs must include period scope and account scope boundaries.

## Lineage and audit requirements

- Reconcile outputs must include source references and decision trace.
- Close decision must include checkpoint outcomes and timestamps.

