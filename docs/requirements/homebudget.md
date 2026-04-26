---
title: HomeBudget
doc_type: requirements
topic_type: owner
owner: homebudget
scope: poc
---
# HomeBudget

HomeBudget is the primary day-to-day finance UI, the operational ledger for account and transaction state, and the write-back target for reconciled adjustments. This page defines the design-time requirement contract for HomeBudget: system role, wrapper boundary, sync contract, HomeBudget-specific posting patterns, reconciliation write-back behavior, and the ownership boundary with related requirement pages.

## Contents

- [Related references](#related-references)
- [System role](#system-role)
- [Document ownership](#document-ownership)
- [Integration boundary](#integration-boundary)
- [Wrapper capability contract](#wrapper-capability-contract)
- [Sync contract](#sync-contract)
- [Account roles in HomeBudget](#account-roles-in-homebudget)
- [Posting patterns in HomeBudget](#posting-patterns-in-homebudget)
- [Reconciliation and write-back](#reconciliation-and-write-back)
- [Design constraints](#design-constraints)

## Related references

- [accounting-logic.md](accounting-logic.md) for global accounting recognition, valuation, timing, and reconciliation policy
- [account-classification.md](account-classification.md) for balance-sheet asset classification and account-registry rules
- [data-model.md](data-model.md) for canonical schema and column ownership
- [reconciliation-engine.md](reconciliation-engine.md) for method classes and adjustment behavior
- [source-systems-lineage.md](source-systems-lineage.md) for lineage and audit trail requirements
- [cash-reconcile.md](cash-reconcile.md) for cash-account reconcile flow that reads and updates HomeBudget
- skill `homebudget` for wrapper procedures, CLI usage, troubleshooting, and implementation-level examples
- skill `data-sources-inspect` for primary-source inspection workflow
- `docs/develop/data-sources/homebudget-source-data.md` for source artifact locations and field-level inspection context

- [HomeBudget wrapper documentation](https://yayfalafels.github.io/homebudget/) — official docs root
    - [User Guide](https://yayfalafels.github.io/homebudget/user-guide/)
    - [Configuration Guide](https://yayfalafels.github.io/homebudget/configuration/)
    - [CLI Guide](https://yayfalafels.github.io/homebudget/cli-guide/)
    - [Methods Reference](https://yayfalafels.github.io/homebudget/methods/)
    - [Sync Update Guide](https://yayfalafels.github.io/homebudget/sync-update/)
    - [Transfer Currency Normalization](https://yayfalafels.github.io/homebudget/transfer-currency-normalization/)
    - [SQLite Schema](https://yayfalafels.github.io/homebudget/sqlite-schema/)
    - [GitHub Repository](https://github.com/yayfalafels/homebudget)

## System role

HomeBudget is the system of record for:

- account definitions used by monthly close and reconciliation workflows
- category and subcategory definitions used for expense mapping and validation
- expense, income, and transfer transactions used for posting and reconciliation
- transaction metadata required for lineage, replay, and audit visibility

Within the POC workflow, HomeBudget remains the primary user-facing finance ledger. The app augments that workflow with controlled sync, reconciliation, and adjustment posting, but it does not replace HomeBudget as the operational ledger surface.

## Document ownership

This page owns the HomeBudget integration contract needed at design time:

- HomeBudget role in the product workflow
- wrapper-only integration boundary
- required wrapper capabilities for reads and controlled writes
- app-managed HomeBudget sync objects and lineage anchors
- HomeBudget account roles that affect design decisions
- HomeBudget-specific posting patterns that depend on those account roles
- write-back requirements for approved reconciliation adjustments

This page does not own the full detail of adjacent topics:

- [accounting-logic.md](accounting-logic.md) owns global accounting policy and booking rules that apply across integrations
- [account-classification.md](account-classification.md) owns asset classification and account-registry rules beyond the HomeBudget surface
- [data-model.md](data-model.md) owns canonical schema and field definitions
- [source-systems-lineage.md](source-systems-lineage.md) owns end-to-end lineage policy across all systems

The overlap rule is that this page restates the subset of those topics that a design pass needs in order to reason about HomeBudget behavior, while detailed formulas, schema columns, and cross-system lineage rules remain owned by the specialized pages above.

## Integration boundary

Application access to HomeBudget shall go through the HomeBudget Python wrapper interface.

- direct SQLite reads or writes are out of scope as the application integration boundary
- direct database inspection may still be used as a diagnostic or source-reference technique, but not as the product contract
- all app-generated HomeBudget writes, including approved reconciliation adjustments, must use the wrapper boundary
- HomeBudget UI behavior and local sync behavior are part of the external system contract and must be respected by automation design

This boundary applies to both read flows and write-back flows.

## Wrapper capability contract

Design work may assume that the HomeBudget wrapper can provide the following capability classes:

- discover accounts and their HomeBudget account type and display name
- discover categories and subcategories used for mapping and validation
- read expenses, income, and transfers for a selected date window
- expose enough transaction attributes to support deterministic lineage, duplicate detection, and replay-safe app sync
- create controlled transactions generated by approved app workflows, including reconciliation adjustments and approved posting actions
- preserve notes or description, date, amount, account, and transaction-type semantics during controlled writes

This requirements page does not lock design to specific wrapper method names. It defines the capability contract that design and implementation must satisfy through the wrapper.

## Sync contract

During data sync, the app reads HomeBudget through the wrapper and materializes app-managed objects in the `hb` schema.

Canonical synced objects:

- `hb_gl_txn`
- `hb_account_dim`
- `hb_category_dim`

Sync rules:

- `hb_gl_txn` is the canonical app-managed HomeBudget general-ledger bridge used for account-based reconciliation and downstream statement mapping
- `hb_account_dim` and `hb_category_dim` use SCD type 1 update behavior
- `hb_txn_uid` is the deterministic hashed transaction lineage key on `hb_gl_txn`
- the sync contract fixes the output objects and lineage requirements but does not force a specific implementation strategy such as full refresh versus incremental refresh
- downstream statement aggregation and reconciliation operate on the app-managed synced state, not on direct HomeBudget database tables

## Account roles in HomeBudget

The following HomeBudget account roles are design-significant because they affect posting rules, reconciliation method, and statement mapping.

| id | HomeBudget role          | example              | design significance                                               |
| -- | ------------------------ | -------------------- | ----------------------------------------------------------------- |
| 01 | personal cost center     | TWH - Personal       | all personal expenses book here; month-end balance closes to zero |
| 02 | designated SGD income    | TWH DBS Multi SGD    | primary landing account for non-capital-gains SGD income          |
| 03 | designated USD income    | TWH CITI             | primary landing account for non-investment USD income             |
| 04 | payment accounts         | cash and credit accts| fund transfers into the personal cost center for expense booking  |
| 05 | investment cash          | TWH IB USD           | books investment cash movement and non-capital-gains investment income |
| 06 | investment position      | IB POSITION USD      | books capital gains and mark-to-market adjustments                |
| 07 | bill settlement bridge   | shared pseudo credit | carries temporary accrual and settlement timing differences       |

HomeBudget account type is a required design input because it drives allowed behavior at the ledger surface:

- `Budget` accounts act as cost centers rather than real wallets
- `Cash` accounts act as real wallets and bank accounts
- `Credit` accounts act as negative-balance funding sources and settlement liabilities
- `External` accounts capture non-personal or position-style balances such as investment positions

Full balance-sheet classification remains owned by [account-classification.md](account-classification.md).

## Posting patterns in HomeBudget

This section consolidates the posting patterns that a design pass needs in order to model HomeBudget correctly.

### Personal expenses

Personal expenses use a required two-transaction pattern in HomeBudget.

1. transfer from the real payment account into `TWH - Personal`
2. expense booked in `TWH - Personal` with the applicable category and subcategory

The design implication is that the payment source and the expense classification are intentionally separated in HomeBudget. Expense-analysis logic must use the expense row, while cash and liability movement uses the transfer row.

### Personal income

Personal income is booked into the account where cash lands.

- non-capital-gains SGD income books into `TWH DBS Multi SGD`
- non-investment USD income books into `TWH CITI`
- other inflows that need centralized tracking may use transfer patterns to preserve designated-income-account visibility

### Investment split between cash and position

Investment workflows use separate HomeBudget accounts for cash and position behavior.

- `TWH IB USD` books investment cash movement, interest, dividends, realized profit and loss, and forex cash effects
- `IB POSITION USD` books capital gains and mark-to-market adjustments
- investment buys and sells are modeled as transfers between investment cash and investment position, not as personal expense or income rows

### Forex on transactions

Foreign-currency card spending requires three HomeBudget effects when the posted charge differs from the spot-rate booking.

1. expense in `TWH - Personal` using the spot-rate SGD amount
2. transfer from the credit account to `TWH - Personal` using the actual posted SGD amount
3. reconciliation expense in `TWH - Personal` for the difference using category `Professional Services:Currency Conversion`

Detailed forex policy remains owned by [accounting-logic.md](accounting-logic.md).

### Bills accrual and settlement bridge

Bill workflows use HomeBudget as the operational ledger, but timing and partial-settlement differences are handled through one shared billing pseudo credit account.

- the billed-period expense is recognized in the billing period
- a matching transfer into the shared billing pseudo credit account captures the payable position
- one or more later transfers out of that account represent actual bank settlement
- the shared billing pseudo credit account must net to zero when the bill is fully settled

Detailed billing-period policy remains owned by [accounting-logic.md](accounting-logic.md) and [bill-payment.md](bill-payment.md).

## Reconciliation and write-back

HomeBudget is both a reconciliation comparison target and a write-back target.

- external statement sources are authoritative for statement facts in bank and credit-card reconciliation
- HomeBudget ledger state is compared against those sources through `hb_gl_txn`
- approved adjustments become part of the reconciled close state in `close_book`
- when the account group integrates with the HomeBudget wrapper, the same approved adjustment is posted back to HomeBudget for user visibility and audit

Each reconciliation procedure produces zero or one adjustment transaction.

- standard lineage transactions retain normal source lineage to origin system and source reference
- adjustment transactions are marked as system adjustments and must retain adjustment rule reference, timestamp, and user comment or approval justification when provided

Design must support the following HomeBudget write-back use cases:

- cash reconcile adjustments for wallet cash accounts
- balance-only reconcile adjustments for third-party balance inputs that use HomeBudget as the operational ledger target
- transaction-level reconciliation outcomes for integrated account groups where the approved correction must remain visible in HomeBudget

## Design constraints

Design work should assume the following constraints:

- HomeBudget remains the primary user UI for real-time personal-finance entry and review during POC
- the app must preserve user-visible auditability by keeping approved adjustments visible in HomeBudget
- HomeBudget-specific posting patterns are part of the product contract and cannot be normalized away by a generic ledger abstraction that loses cost-center or investment-split behavior
- wrapper procedures and source-data inspection guides are execution references, while this page is the requirement source for HomeBudget integration behavior

When execution details are needed, use this precedence:

1. this requirement page for integration behavior and acceptance boundary
2. skill `homebudget` for wrapper procedures and implementation examples
3. skill `data-sources-inspect` and `docs/develop/data-sources/homebudget-source-data.md` for source inspection evidence
