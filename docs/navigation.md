# Document Navigation

## Table of contents

- [Summary](#summary)
- [Scope](#scope)
- [Problem statement](#problem-statement)
- [Policy goals](#policy-goals)
- [Navigation metadata policy](#navigation-metadata-policy)
- [Document types](#document-types)
- [Topic types](#topic-types)
- [Frontmatter fields](#frontmatter-fields)
- [Relationship rules](#relationship-rules)
- [Example](#example)
- [Adoption notes](#adoption-notes)

## Summary

This document defines a navigation policy for requirement documents in `docs/requirements/*`.

The policy introduces YAML frontmatter metadata to declare document ownership and document-to-document relationships outside the prose body. The goal is to reduce ambiguity, reduce ownership conflicts, and make cross-topic navigation explicit.

## Scope

This policy applies to frontmatter metadata in `docs/requirements/*` and inventory alignment in `docs/requirements.md`.

This policy does not yet apply to:

- `docs/develop/*`
- prompt files
- skill files
- design documents

## Problem statement

The requirements set is now split across multiple topic documents. That split improves focus, but it also creates a navigation problem when ownership and related-topic links are expressed only inside prose sections.

Without explicit metadata, the documentation set is more likely to accumulate the following errors:

- ambiguous ownership across adjacent documents
- duplicated or conflicting requirement statements
- inconsistent cross-links between related topics
- drift between summary pages, owner pages, and context pages

The navigation policy addresses this by separating navigation metadata from the document body and standardizing how ownership and cross-linking are declared.

## Policy goals

- Minimize overlapping or redundant information across requirement documents.
- Where overlap is intentionally retained for summary flow or continuity, define clear ownership and explicit cross-links.
- Store ownership and relationship metadata in YAML frontmatter, separate from the prose body.

## Navigation metadata policy

Each requirement document should declare its navigation metadata in YAML frontmatter at the top of the file.

The frontmatter metadata is used to define:

- what kind of requirement document it is
- whether it is an owner page or reference page
- which topics it owns

The prose body remains responsible for the requirement content itself. Frontmatter must not replace clear body text for scope, policy, or requirement statements.

## Document types

The navigation policy distinguishes between owner documents and supporting documents.

### Owner documents

Owner documents are the authoritative requirement pages for the POC release.

If two documents appear to conflict, the owner page is the deciding source for that topic.

Owner documents include:

- owner pages that define what the system must do for a topic
- boundary pages that define requirement-level scope and source-of-truth constraints for a topic

Current examples include:

- `workflow-orchestration.md`
- `interaction-approvals.md`
- `statements-lifecycle.md`
- `source-systems-lineage.md`
- `reconciliation-engine.md`
- `transaction-category-mapping.md`
- `homebudget.md`
- `google-sheets.md`

### Supporting documents

Supporting documents help readers understand, navigate, or interpret the requirement set, but they do not own the final POC requirement policy for a topic.

Supporting documents include the following types.

#### Current workflow

Current-workflow documents describe the current workflow, operational background, or surrounding explanation. They may summarize behavior and link to owner pages, but they must not compete with those owner pages.

Current-workflow documents use topic type `reference`.

Current example:

- `current-workflow.md`

#### Requirements overview

Requirements overview documents summarize scope, structure, and document navigation across the requirements set. They are useful entry points, but they do not replace owner pages.

Current example outside the current frontmatter scope:

- `docs/requirements.md`

#### Requirements reference

Requirements reference documents provide supporting interpretation, terminology, or release framing. They may constrain how requirement pages are read, but they are not the primary owner for detailed topic policy.

Current examples include:

- `glossary.md`
- `implementation-roadmap.md`

### Classification rule of thumb

- If the page defines what the system must do for a topic in the POC release, it is an owner document.
- If the page helps readers navigate, summarize, interpret, or contextualize another page, it is a supporting document.

## Topic types

Use topic types to distinguish pages that define requirements from pages that support interpretation or current-state context. The topic type does not replace body text, but it makes the page role explicit at the metadata level.

| id | topic_type         | purpose            | use                          |
| -- | ------------------ | ------------------ | ---------------------------- |
| 01 | `owner`            | requirement owner  | defines POC requirement      |
| 02 | `reference`        | supporting reference | supports interpretation    |

## Frontmatter fields

Use the following fields as the baseline metadata contract for requirement documents.

| id | field        | required | purpose                          |
| -- | ------------ | -------- | -------------------------------- |
| 01 | `title`      | yes      | canonical document title         |
| 02 | `doc_type`   | yes      | document class                   |
| 03 | `topic_type` | yes      | `owner` or `reference`           |
| 04 | `owner`      | yes      | primary topic owner id           |
| 05 | `scope`      | yes      | active scope boundary            |

## Relationship rules

- Every requirement statement must have one primary owner document.
- Reference documents may summarize or explain flow, but they must not compete with owner documents.
- Cross-document ownership and navigation must still be stated in the body where needed.
- Minimal frontmatter identifies the document role, but it does not replace explicit prose links or ownership notes.

## Example

Example frontmatter for an owner page:

```yaml
---
title: Workflow Orchestration
doc_type: requirements
topic_type: owner
owner: workflow-orchestration
scope: poc
---
```

Example frontmatter for a reference page:

```yaml
---
title: Current Workflow
doc_type: requirements
topic_type: reference
owner: current-workflow-context
scope: poc
---
```

## Adoption notes

- Apply this policy incrementally to documents in `docs/requirements/*`.
- Start with documents that already express ownership and reference links in body text.
- Keep the frontmatter aligned with the document body until automated validation exists.
- Do not move requirement statements into frontmatter. Frontmatter is for navigation metadata only.