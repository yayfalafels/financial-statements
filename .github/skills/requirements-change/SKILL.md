---
name: requirements-change
description: Manage requirement changes that surface during later development phases (design, implementation, testing) ensuring traceability, impact assessment, requirements update, downstream tracking, and responsible-party assignment.
---

# Requirements Change Management

## Summary

This skill documents the disciplined workflow for handling requirement changes that surface during design, implementation, or testing phases. It ensures that:
- All changes are formally recorded with traceability to phase and discovery context.
- Impacted requirements documents are identified and updated.
- Cascading impacts to design, test strategy, test cases, and implementation are assessed.
- Unimplemented or partially implemented impacts are captured in task backlog with ownership assignment.
- No requirement changes propagate without downstream artifact updates or explicit backlog tracking.

## Apply This Skill When

- A requirement surfaces or changes during design phase (e.g., a new reconciliation layer discovered).
- A design decision reveals a previously unknown requirement (e.g., user review and approval step for pairing).
- Implementation uncovers missing or conflicting requirements.
- Testing identifies gaps or ambiguities in requirement coverage.
- Cross-document consistency issues arise between related requirement areas.
- Scope boundary decisions need to be recorded (e.g., "this is in scope, that is not").

## Related Skills and Artifacts

- `task-definition`: For structuring backlog task entries and tracking status.
- `documentation`: For updating requirement documents and design sections.
- `variable-naming`: For consistent naming of change IDs and document shorthand keys.
- `markdown-tables`: For markdown table formatting, fixed-width padding, and row length compliance.
- `reconciliation-patterns`: Domain knowledge for reconciliation-specific requirement content.
- Requirements docs: `docs/releases/010/requirements/`
- Design docs: `docs/releases/010/design/`
- Change log: `docs/releases/010/requirements/requirements-changes.md`

## Markdown Table Formatting Reference

For detailed markdown table compliance rules, fixed-width padding, row length limits, and cell content guidelines, see `markdown-tables` skill.

Key rules summary:
- Include `id` column for tables.
- Pad columns to fixed widths (longest header or cell in each column).
- Keep total row length under 115 characters.
- Move lengthy explanations outside the table to surrounding text.
- Avoid multi-line cell content; each row must fit on one line.

## Official References

- Release 010 documentation: `docs/releases/010/`
- Requirements index: `docs/releases/010/requirements/requirements.md`
- Project management templates: `docs/releases/010/project-management/`
- SDLC AI agent design: `docs/develop/010/design/sdlc-ai-agents.md`
- Design agent: `.github/agents/design.agent.md`

## Integration with Design Workflow

When working through the design planning process, apply this skill at key discovery and decision points:

**Purpose:** Capture requirement changes discovered during design exploration, architecture decisions, and data model refinement. Design work often reveals missing or ambiguous requirements that must be formally recorded and cascaded to dependent workflows.

**When to apply:**
- During any design phase when a new requirement emerges or an existing requirement needs clarification.
- When architectural decisions impose new constraints on requirements (e.g., data model choices affect validation rules).
- When design work discovers requirement conflicts or gaps in existing documentation.

**What to do at each design phase checkpoint:**
- **Discovery phase**: Check if source data inspection reveals new requirements. Record any assumptions that should become formal requirements.
- **Architecture phase**: When defining module boundaries and data flows, identify any missing requirements for data transformation or validation.
- **Domain model phase**: When finalizing business entity definitions, check whether the model requires new or modified requirement documentation.
- **Data layer phase**: When designing schema and persistence, identify any requirements around data consistency, archiving, or audit trails.
- **Workflow phase**: When orchestrating module interactions, check whether workflow sequencing reveals new requirements for approval, validation, or handoff.
- **Module interface phase**: When defining API contracts, ensure all interface requirements are documented and approved.

Apply this skill (Steps 1–6) to formally process each change discovery, update affected requirement documents, and create backlog tasks for cascading impacts.

## Workflow

### Step 1: Establish Change Context and Authority

**Goal:** Establish who discovered the change, when, why, and who has approval authority.

**Check for requirement changes:** If you are in design, implementation, or testing phase, pause and assess whether the work you are doing reveals new requirements or conflicts with existing ones. If yes, apply this step immediately.

**Actions:**

1. Record the **discovery phase** and **discovery context**:
   - Phase: design, implementation, testing, or other.
   - Context: Which document, section, or work item triggered discovery.
   - Discoverer: Agent, developer, or workflow role responsible for discovery.

2. Identify **approval authority** for the change:
   - Usually the **owner** of the affected requirement document (e.g., `reconciliation-engine` owner for reconciliation changes).
   - For cross-document changes, identify primary owner and stakeholders.
   - Ensure change is **reviewed and approved** before proceeding to Step 2.

3. Record **change justification**:
   - Briefly describe why the change is necessary.
   - Include evidence: design insight, implementation blocker, test finding, or design decision rationale.
   - Link to related artifacts: design sections, issue, or code references.

**Example:**
```
Change: Add semantic matching layer to transaction-level reconciliation.
Phase: Design
Context: Reconciliation Design document, transaction-level method class section.
Discoverer: reconciliation-engine agent
Approval Authority: reconciliation-engine owner
Justification: During design of forward-pass algorithm, identified need for
  post-heuristics matching to pair add-remove edits and reduce redundant manual steps.
  This aligns with zero-sum transfer-expense behavior requirement.
Evidence: Design section "Semantic matching layer" (reconciliation.md lines 228-278)
```

### Step 2: Record Change in Requirements Change Log

**Goal:** Create an auditable change record with metadata and summary.

**Check for requirement changes:** Before recording a change, verify that the discovery context and justification are clear and complete. Confirm that the change is truly about requirements, not just implementation details.

**Location:** `docs/releases/010/requirements/requirements-changes.md`

**Actions:**

1. **Assign unique change ID**:
   - Table row gets next sequential `id` in the release (01, 02, 03, ...)
   - Assign a brief `change` name (3-7 words) describing the change

2. **Create summary row in change table** with fields:
   - `id`: Sequential number (01, 02, 03, ...)
   - `date`: Date change was approved (ISO format: YYYY-MM-DD)
   - `change`: Brief descriptive name for the change (one-line)
   - `status`: `approved` (must be approved before proceeding)
   - `impacted_docs`: Shorthand keys for affected requirement documents

3. **Create change details section** under `## Change details` with subsection `### Change <id>: <change>` containing:

   **Change scope:**
   - Bulleted list of specific requirements being added, modified, or removed.
   - Be explicit about scope boundaries: what IS in scope, what is NOT.

   **Updated requirement locations:**
   - List each impacted requirement file with specific sections or subsections.
   - Example:
     ```
     - `reconciliation-engine.md`
       - Add `Semantic matching layer` requirements.
       - Add `Transfer-expense pairing` requirements.
       - Update `Shared workflow phases` for phase 6 user approval behavior.
     - `interaction-approvals.md`
       - Update reconcile checkpoint focus and pass criteria.
       - Add `Reconcile-stage required approvals` section.
     ```

   **Acceptance impact:**
   - Describe how the change affects acceptance criteria, closure conditions, or test scope.
   - Identify any new blocking conditions or mandatory artifacts.

**Validation:**
- Ensure `id` and `change` name are unique across all prior changes in the release.
- Ensure status is `approved` before proceeding to Step 3.
- Ensure all impacted_docs are documented in Step 3.

### Step 3: Identify and Apply Requirement Updates

**Goal:** Update all affected requirement documents with the new or modified requirements.

**Check for requirement changes:** As you update each requirement document, watch for cascading effects: does updating one requirement force updates to related sections or other documents? If yes, return to Steps 1-2 for those cascading changes.

**Preparatory Research:**

1. **Locate impacted requirement files:**
   - Use `impacted_docs` from Step 2 change details.
   - Open each requirement file and search for sections related to the change.
   - Use cross-reference metadata to find related sections (e.g., requirement refs like `"ref: workflow-orchestration.md - Stage 6 exit"`).

2. **Assess each impacted location:**
   - Read the current requirement text carefully.
   - Identify what needs to be **added**, **modified**, or **removed**.
   - Look for cascading impacts: does this change trigger changes in related sections or other documents?

**Update Actions:**

3. **Apply requirement edits** to affected files:
   - **Add new requirements:** Insert new section headers, descriptions, and constraints.
   - **Modify existing requirements:** Update text to reflect changed behavior, scope, or constraints.
   - **Remove obsolete requirements:** Delete or archive superseded text with a deprecation note if needed.
   - **Add requirement references:** Ensure cross-references between related sections are correct and up-to-date.
   - **Update metadata:** Set `last_updated` field in document header to today's date.

4. **Validate requirement consistency:**
   - Ensure new requirements don't contradict existing requirements in the same document.
   - Verify that requirement cross-references are bidirectional and consistent.
   - Check that shared patterns (e.g., tolerance rules, workflow phases) are correctly cited.

**Example:**
```markdown
## Semantic Matching Layer (NEW SECTION)

[New requirement text for semantic matching of add-remove edit pairs]

## Transfer-Expense Pairing (NEW SECTION)

[New requirement text for transfer-expense matching for TWH - Personal zero-sum]

## Shared Workflow Phases (MODIFIED SECTION)

Phase 6: Reconcile Review and Approval
- [Existing text]
- Add: User must review and approve semantic matching proposals before commit.
- Add: User must review and approve transfer-expense pairing CRUD actions before posting.
```

### Step 4: Assess Cascading Impacts to Design and Testing

**Goal:** Identify impacts to downstream artifacts (design docs, test strategy, test cases, source code) and determine whether updates are implemented or backlogged.

**Check for requirement changes:** If your impact assessment reveals that design, test, or code changes depend on unresolved requirements, loop back to Steps 1-3 to clarify those requirements before proceeding.

**Impact Assessment:**

1. **Design phase artifacts:**
   - Check if change affects design document sections (e.g., `docs/releases/010/design/`)
   - Determine if new design sections, algorithm descriptions, or data models are needed.
   - Identify if existing design sections need to be updated or clarified.
   - **Action:** Implement updates immediately if they clarify or correct existing design intent; backlog if new design work is required.

2. **Test strategy and test cases:**
   - Check if change adds new test scenarios, acceptance criteria, or test cases.
   - Identify if existing test cases need to be modified or expanded.
   - Determine if new test fixtures or data are required.
   - **Action:** Implement straightforward test updates; backlog comprehensive test strategy reviews or large test case additions.

3. **Source code and implementation:**
   - Check if change requires new code modules, classes, or functions.
   - Identify if existing code logic or API contracts need to be updated.
   - Determine implementation complexity and dependencies.
   - **Action:** Backlog all code changes with clear ownership and acceptance criteria; do not implement unless explicitly planned in the current sprint or workflow.

4. **Configuration and schema:**
   - Check if change requires new config files, schema fields, or data structures.
   - Identify if existing configs or schemas need to be extended.
   - **Action:** Implement schema/config changes needed to unblock dependent work; backlog speculative changes.

**Example Assessment:**
```
Change: Add semantic matching layer to transaction-level reconciliation

Impact Analysis:

Design (docs/releases/010/design/reconciliation.md):
- NEW: Add "Semantic Matching Layer" section with algorithm and invocation contract.
- MODIFY: Update "Transaction-level Method Invocation Contract" to include
  new `semantic_pairs` output and `semantic_heuristics_config` input.
- Status: IMPLEMENT (clarifies design intent already present in selected section)

Test Strategy (docs/releases/010/testing/):
- NEW: Add acceptance criteria for semantic match output format and validation.
- NEW: Add test cases for end-to-end semantic matching with known pairs.
- Status: BACKLOG (test strategy review needed; create task in test agent)

Test Cases (tests/):
- NEW: Add test fixtures for add-remove edit pairs.
- NEW: Add semantic match algorithm test cases.
- Status: BACKLOG (create task in test agent; depends on design completion)

Source Code (src/):
- NEW: Add `SemanticMatcher` class in reconciliation-engine module.
- NEW: Add configuration section for semantic matching heuristics.
- MODIFY: Update `TransactionLevelReconciler` to invoke semantic matcher
  after heuristics and before edits output.
- Status: BACKLOG (create implementation tasks in code-complete agent)

Configuration (reference/hb-reconcile/account_settings/):
- NEW: Add semantic matching heuristics to `txn_heuristics.json`.
- Status: BACKLOG (depends on code implementation; create task)
```

### Step 5: Create Task Backlog Entries for Unimplemented Work

**Goal:** Ensure all unimplemented or partially implemented impacts are tracked with clear ownership, acceptance criteria, and dependencies.

**Check for requirement changes:** As you create backlog tasks, ensure each task includes clear references to the impacted requirement and change ID. If acceptance criteria are vague or unmapped to requirements, clarify requirements before creating the task.

**Task Backlog Format:**

For each unimplemented or partially implemented impact identified in Step 4:

1. **Create task entry** using the task tracking system (`manage_todo_list` or equivalent backlog):
   - Title: Concise, action-oriented description (3-7 words).
   - Description: Include change reference (e.g., `01` or `semantic + transfer-expense pairing`), scope, and acceptance criteria.
   - Owner: Assign to responsible agent or development role.
   - Status: `not-started`, `in-progress`, or `blocked` as appropriate.
   - Dependencies: List any blocking tasks or external dependencies.
   - Priority: Inherit from release schedule or change criticality.

2. **Link task to change record:**
   - Reference change ID (e.g., `01`) or change name in task description.
   - Add task ID to change details section in requirements-changes.md if central tracking is needed.

3. **Assign ownership:**
   - Design updates: assign to `design` agent or `reconciliation-engine` agent (if design work is scoped to agent domain).
   - Test updates: assign to `test` agent.
   - Code implementation: assign to `code-complete` agent or domain-specific implementation agent.
   - Configuration: assign to responsible agent (e.g., `reconciliation-engine` if config is part of agent scope).

**Example Backlog Tasks:**

```markdown
### Task 1: Design semantic matching algorithm

Change: 01
Description: Implement "Semantic Matching Layer" section in reconciliation design doc.
  Add algorithm description, invocation contract, parameters, and failure modes.
  Reference: reconciliation-engine.md - Semantic matching layer requirements.
Owner: design (reconciliation-engine)
Status: not-started
Acceptance Criteria:
  - Semantic matching algorithm section is complete and approved.
  - Invocation contract includes inputs, outputs, pre/post-conditions.
  - Design aligns with semantic matching requirement text in reconciliation-engine.md.

### Task 2: Implement SemanticMatcher class

Change: 01
Description: Implement `SemanticMatcher` class in src/python/reconciliation/
  to execute semantic matching layer algorithm. Add configuration loading,
  validation, and error handling per design spec.
Owner: code-complete
Status: not-started
Dependencies: Task 1 (design semantic matching algorithm)
Acceptance Criteria:
  - Class matches design contract signature and behavior.
  - Configuration is correctly loaded from txn_heuristics.json.
  - Error cases raise appropriate exceptions with diagnostic messages.
  - SIT test cases pass (defined in test backlog task).

### Task 3: Test semantic matching layer

Change: 01
Description: Define and implement test cases for semantic matching layer.
  Add fixtures for add-remove edit pairs, edge cases, and configuration variations.
  Ensure end-to-end reconciliation test includes semantic matching.
Owner: test
Status: not-started
Dependencies: Task 2 (implementation)
Acceptance Criteria:
  - All test cases pass.
  - Coverage includes happy path, edge cases, and failure modes.
  - Test fixtures align with reconciliation-engine requirements.
```

### Step 6: Validate and Close Change Record

**Goal:** Confirm all updates, impacts, and backlog tasks are complete and consistent.

**Check for requirement changes:** Before closing, verify that all impacted requirement documents have been reviewed and updated, all backlog tasks are created with clear ownership, and all cross-references are bidirectional and consistent. If gaps remain, loop back to the relevant step and complete the work.

**Validation Checklist:**

- ✓ Change record in `requirements-changes.md` is complete with change_id, date, status, summary, impacted_docs, change scope, and acceptance impact.
- ✓ All impacted requirement documents have been reviewed and updated (or explicitly deferred with backlog task).
- ✓ Design, test, and code impacts have been assessed and documented.
- ✓ All unimplemented work is captured in backlog tasks with clear ownership and dependencies.
- ✓ Backlog tasks reference the change_id and include acceptance criteria linked to requirement text.
- ✓ Cross-references between requirements are bidirectional and consistent.
- ✓ No untracked impacts remain.

**Closure:**

1. Update change record status to `approved` (already set in Step 2; confirm it remains correct).
2. Update `last_updated` date in affected requirement documents to today's date.
3. Close change assessment by documenting any residual risks or deferred decisions.
4. Communicate change summary and backlog task assignments to responsible agents.

## Key Patterns and Rules

### Change ID Format and Sequencing

- Table identifier: Sequential `id` column (01, 02, 03, ...)
- Release: two-digit POC/release number (e.g., `010`)
- Sequence: zero-padded two-digit counter, incremented per change in the release
- Do not reuse or recycle IDs; maintain unique audit trail
- Brief change name: Used in `change` column and change details section header for quick reference
- For task references and documentation, use either the numeric `id` (e.g., `01`) or the `change` name (e.g., `semantic + transfer-expense pairing`)

### Shorthand Document Keys

Define consistent two-letter or three-letter keys for impacted documents to compact the change table. Common keys:

| key | document                         |
| --- | ------------------------------- |
| re  | reconciliation-engine.md        |
| ia  | interaction-approvals.md        |
| hb  | homebudget.md                   |
| wo  | workflow-orchestration.md       |
| cc  | cash-reconcile.md               |
| ws  | workflow-orchestration.md       |
| st  | statements-lifecycle.md          |

Maintain a key list in the requirements-changes.md document header or footer for reference.

### Status Lifecycle

- `draft`: Change is under review; not yet approved.
- `approved`: Change has been reviewed and approved by authority; ready for implementation.
- `implemented`: All requirement updates and backlog tasks are complete.
- `deferred`: Change is approved but implementation is deferred to a future release; document reason.
- `rejected`: Change was reviewed and rejected; document reason and who rejected it.

### Requirement Cross-Referencing

When a change affects multiple requirement documents, ensure cross-references are explicit:

- In document A, reference the related section in document B using format: `"ref: <filename> - <section path>"`
- Example: `"ref: workflow-orchestration.md - Stage 6 exit criteria - Reconcile"`
- Validate that back-references exist in document B pointing to document A.

### Backlog Task Linking

When creating backlog tasks for unimplemented work:

- Include the change_id in the task description or metadata.
- Link task to the specific impacted requirement section (e.g., "reconciliation-engine.md - Semantic matching layer").
- Set task dependencies explicitly: which other tasks must complete before this one can start.
- Assign ownership to a single responsible agent or role (not shared ownership).

### Markdown Table Compliance

For markdown table formatting guidance, see the `markdown-tables` skill. When creating change tables or impact assessments, follow its guidelines for fixed-width column padding and row length compliance (max 115 characters).

## Common Pitfalls and How to Avoid Them

| pitfall                        | cause                                  | prevention                          |
| ------------------------------ | -------------------------------------- | ----------------------------------- |
| Incomplete requirement updates | change recorded but docs not reviewed  | Step 3: systematically review docs  |
| Missed cascading impacts       | change affects design/test/code        | Step 4: assess all impact layers    |
| Untracked implementation work  | impacts identified but tasks not made  | Step 5: create explicit backlog     |
| Inconsistent cross-references  | bidirectional ref links broken         | Step 6: validate both directions    |
| Ambiguous ownership            | backlog tasks lack clear owner         | Step 5: single owner per task       |
| Status creep                   | change status never marked complete    | Step 6: closure checkpoint enforces |

**Prevention Strategies:**

- **Incomplete requirement updates:** Change is recorded but affected requirement docs are not reviewed/updated. Step 3 explicitly requires reviewing each impacted doc; use cross-references to find related sections.
- **Missed cascading impacts:** Requirement change affects design, tests, or code but impacts are not assessed. Step 4 systematically checks design, testing, and code for impacts; use impact assessment as checkpoint.
- **Untracked implementation work:** Impacts are identified but backlog tasks are not created or are vague. Step 5 requires explicit task creation with acceptance criteria; link tasks back to change ID.
- **Inconsistent cross-references:** Requirement updates create bidirectional ref inconsistencies. Validate forward and back references exist in Step 6; use grep to find all refs to a changed section.
- **Ambiguous ownership:** Backlog tasks lack clear owner or ownership is shared. Step 5 requires single owner assignment; clarify owner authority with agent and domain scoping.
- **Status creep:** Change is never marked complete; status remains approved indefinitely. Step 6 checkpoint includes explicit closure criteria; mark status `implemented` when all tasks complete.

## Example Workflow: End to End

**Scenario:** Reconciliation design reveals need for semantic matching layer requirement.

### Step 1: Establish Context
```
Discovery Phase: Design
Discovery Context: Reconciliation.md design - Transaction-level Method Class
Discoverer: reconciliation-engine agent
Approval Authority: reconciliation-engine owner
Justification: Algorithm analysis reveals need for post-heuristics matching to
  reduce redundant edits and improve user experience. This aligns with transfer-
  expense pairing requirement and zero-sum cost center behavior.
Status: Approved by reconciliation-engine owner on 2026-05-03
```

### Step 2: Record in Change Log
```
Change ID: 01
Change Name: semantic and transfer-expense pairing
Change Summary Table Row:
| 01 | 2026-05-03 | semantic + transfer-expense pairing | approved | re, ia, hb, wo |

Change Details (Section header: `### Change 01: semantic + transfer-expense pairing`):

Change scope:
- Add semantic matching layer requirements to transaction-level reconciliation.
- Add transfer-expense pairing requirements for TWH - Personal zero-sum behavior.
- Require user review and approval for pairing proposals before commit.

Updated requirement locations:
- reconciliation-engine.md
  - Add `Semantic matching layer` requirements
  - Add `Transfer-expense pairing` requirements
- interaction-approvals.md
  - Update reconcile checkpoint requirements
- homebudget.md
  - Add transfer-expense write-back use case
- workflow-orchestration.md
  - Update reconcile exit criteria

Acceptance impact:
- Reconcile cannot close with unresolved pairing findings
- User approval is now required for pairing and CRUD decisions
- Semantic and transfer-expense edits are mandatory reconcile artifacts
```

### Step 3: Update Requirements
- ✓ Add "Semantic Matching Layer" section to reconciliation-engine.md
- ✓ Add "Transfer-Expense Pairing" section to reconciliation-engine.md
- ✓ Update interaction-approvals.md reconcile checkpoint section
- ✓ Update homebudget.md write-back requirements
- ✓ Update workflow-orchestration.md stage 6 exit criteria

### Step 4: Assess Cascading Impacts
```
Design doc (reconciliation.md):
  - IMPLEMENT: Add algorithm and invocation contract sections
  - Status: In progress (already drafted)

Test strategy:
  - BACKLOG: Add semantic matching layer acceptance criteria and test scenarios

Code implementation:
  - BACKLOG: SemanticMatcher class and integration tests

Configuration:
  - BACKLOG: Add semantic heuristics to txn_heuristics.json
```

### Step 5: Create Backlog Tasks
```
Task 1: Design semantic matching algorithm (assign to: design)
Task 2: Implement SemanticMatcher class (assign to: code-complete)
Task 3: Test semantic matching layer (assign to: test)
Task 4: Add semantic heuristics configuration (assign to: reconciliation-engine)
```
### Step 6: Close and Communicate
- All requirement updates applied
- All backlog tasks created with ownership
- Change status remains `approved`
- Notify affected agents of backlog tasks and dependencies
