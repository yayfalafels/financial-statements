---
name: subagent-trial-methodology
description: Controlled, evidence-based protocol for validating proposed agent enhancements before promotion to production agent stack.
license: MIT
compatibility: Python 3.8+
metadata:
  author: yayfalafels
  version: 1.0.0
---

## Overview

The subagent trial methodology provides an evidence-based protocol for evaluating whether a proposed agent enhancement — such as a new skill, instruction change, or prompt modification — actually improves agent behavior on a representative task. Trials produce direct evidence before any change is promoted to the production agent stack.

The method uses two subagents: a **control** and an **experimental**. Both receive the same task prompt. The control uses current instructions and skills. The experimental uses the proposed enhancement. Outcomes are compared to determine whether the enhancement produced a measurable improvement.

## When to Use This Skill

- Validating a new skill before promoting to production.
- Testing instruction changes on a target agent role.
- Evaluating prompt modifications for a specific task type.
- Grounding agent-stack decisions in task outcomes rather than intuition.
- Building evidence before committing to production changes.

## Purpose

- Validate agent enhancements with evidence before promoting to production.
- Distinguish one-off improvements from generalizable patterns.
- Ground agent-stack decisions in task outcomes, not intuition.
- Document how agent behavior changed under controlled conditions.
- Build a library of validated enhancements and lessons learned.

## Trial Structure

Each trial consists of:

1. A defined **enhancement hypothesis** with a specific predicted improvement.
2. A **representative task prompt** scoped to a single stage and task type.
3. A **control subagent run** with current agent instructions, skills, and prompt context.
4. An **experimental subagent run** with the proposed enhancement applied.
5. **Evaluation** of both outputs against predefined acceptance criteria.
6. **Outcome classification** from the four possible result states.

## Control Setup

The control subagent receives:

- The current production `.agent.md` instructions for the relevant agent role.
- The current set of skills declared in that agent's instructions.
- A task prompt that is representative of the target task type.
- No enhancement-specific guidance or additional context.

**Purpose**: Establish a baseline — what does the current agent stack produce for this task?

## Experimental Setup

The experimental subagent receives:

- The proposed updated `.agent.md` instructions, **or** the proposed new/updated skill content, injected directly into the subagent prompt.
- The same task prompt used for the control.
- No other differences. The only variable is the enhancement.

**Purpose**: Measure whether the enhancement changes the output in the predicted direction.

## Task Prompt Design

Trial task prompts must satisfy these criteria:

- **Single stage and task type** — avoid combining multiple stages or tasks.
- **Deterministic output shape** — the prompt should constrain the output format.
- **Representative of actual task** that motivated the enhancement hypothesis.
- **Balanced scope** — not so narrow that only one answer exists, not so broad that evaluation is ambiguous.

### Good task prompt structure:

```
Context: [inject relevant design spec or requirement section]

Task: [single, bounded task from the SDLC task inventory]

Expected output format:
- [format requirement 1]
- [format requirement 2]

Acceptance criteria:
- [criterion 1]
- [criterion 2]
- [criterion 3]
```

### Example: Document accounting policy (R-03):

```
Context:
From `docs/develop/010/design/sdlc-ai-agents.md`, Requirements stage task R-03:
"Document accounting policy: M2M, forex, double-entry, income vs transfer"

Task:
Define double-entry posting rules for personal expenses in TWH HomeBudget.
Include account pairs, debit/credit direction, and a worked example with real amounts.

Expected output format:
- Rule statement
- Account pairs (debit account → credit account)
- Complete worked example with real TWH account names and amounts

Acceptance criteria:
- Double-entry identity holds: debits = credits
- Example uses real TWH account names (e.g., "TWH - Personal", "TWH DBS Multi SGD")
- Example includes complete calculation steps, not just results
- Posting pattern is consistent with HomeBudget cost-center behavior
```

## Evaluation Criteria

Evaluation criteria must be **defined before the trial runs**. They must be **observable** without subjective interpretation.

### Suitable criteria types:

- **Presence of specific artifact** — e.g., "identity assertion present in code."
- **Absence of known failure mode** — e.g., "no missing double-entry leg."
- **Correct policy application** — e.g., "FIFO sequencing matches requirement."
- **Structural completeness** — e.g., "all required schema objects present."
- **Procedural correctness** — e.g., "phases in correct order."

### Unsuitable criteria:

- "Quality is improved" (subjective).
- "Output is more helpful" (subjective).
- "Code looks better" (subjective).

Every criterion must have a **binary pass/fail** determination.

### Example criteria table:

| criterion | type | pass condition |
| --------- | ---- | -------------- |
| identity_assertion | artifact | debit = credit shown |
| real_account_names | completeness | all names match active accounts |
| calculation_steps | completeness | all steps shown, not just result |
| posting_consistency | correctness | matches cost-center pattern |

## Outcome Classification

Each trial produces one of four outcomes:

| outcome | control | experimental | interpretation |
| ------- | ------- | ------------ | --------------- |
| Both pass | pass | pass | No regression; insufficient evidence. Try harder task. |
| Both fail | fail | fail | Enhancement didn't fix root cause. Revise hypothesis. |
| **Control fails, Experimental passes** | **fail** | **pass** | **Direct evidence of improvement. Promote.** |
| Control passes, Experimental fails | pass | fail | Regression introduced. Reject and investigate. |

**Key rule**: Only **control-fail / experimental-pass** constitutes direct evidence for promotion.

## Evidence Standards for Promotion

For an enhancement to be promoted to production:

1. **At least one control-fail / experimental-pass** on a representative task.
2. **No control-pass / experimental-fail regressions** on other tasks for the same agent.
3. **Evaluation criteria defined before trial ran**, not after.
4. **Evidence documented** in a trial log (see Trial Log Format below).

**Not sufficient**: Informal observation that "output looked better." Must have documented comparison with predefined criteria.

## Trial Log Format

Each trial must be documented. Use this template:

```
## Trial ID: [unique ID, e.g., T-001]

**Date**: [YYYY-MM-DD]

**Enhancement hypothesis**: [what improvement is expected and why]

**Proposed enhancement**: [concise description]
- New skill, updated instructions, or prompt modification
- Link to draft artifact

**Target agent role**: [e.g., design, code-complete, financial-accounting]

**Target task type**: [e.g., R-03 (accounting policy), D-06 (reconciliation)]

### Evaluation Criteria

| criterion | type | pass condition |
| --------- | ---- | -------------- |
| criterion_1 | artifact/completeness/correctness | [binary pass condition] |
| criterion_2 | artifact/completeness/correctness | [binary pass condition] |

### Control Results

**Output summary**: [concise summary, max 500 chars]

| criterion | result |
| --------- | ------ |
| criterion_1 | [pass/fail with evidence] |
| criterion_2 | [pass/fail with evidence] |

**Overall**: [pass/fail]

### Experimental Results

**Output summary**: [concise summary, max 500 chars]

| criterion | result |
| --------- | ------ |
| criterion_1 | [pass/fail with evidence] |
| criterion_2 | [pass/fail with evidence] |

**Overall**: [pass/fail]

### Outcome

**Classification**: [Both pass / Both fail / Control fails, Experimental passes / Control passes, Experimental fails]

**Conclusion**: [what the trial showed]

**Recommendation**: [promote / revise hypothesis / reject / investigate regression]

### Residual Risks

- [unresolved questions or trial limitations]

### Next Steps

- [follow-up actions]
```

## Trial Inventory

Log all trial results in `.github/design/trial-inventory.md`:

```markdown
# Subagent Trial Inventory

Last updated: [YYYY-MM-DD]

## Summary

| trial_id | agent_role | enhancement | result | status |
| -------- | ---------- | ----------- | ------ | ------ |
| T-001    | design     | skill: accounting-logic | pass | promoted |
| T-002    | code-complete | instruction update | fail | rejected |

## Trial Details

[Full trial log entries in date order]
```

## Best Practices

### Before running:

- [ ] Hypothesis is a single sentence.
- [ ] Evaluation criteria are all binary (no subjective terms).
- [ ] Task prompt is from SDLC task inventory.
- [ ] Current agent output for the task is known (if available).
- [ ] Enhancement is minimal and focused (no bundled changes).

### During control run:

- [ ] Use **exact current** `.agent.md` for the role.
- [ ] Do **not** hint at evaluation criteria to control subagent.
- [ ] Capture **full response**, not summary.
- [ ] Note **timestamp and model version**.

### During experimental run:

- [ ] Inject **only the proposed enhancement**.
- [ ] Use **same task prompt** as control.
- [ ] Use **same model and parameters** as control.
- [ ] Capture **full response**.
- [ ] Note **timestamp and model version**.

### During evaluation:

- [ ] Evaluate both against **same criteria**.
- [ ] Apply **uniformly** (same threshold on both).
- [ ] Document interpretation if criteria are ambiguous.
- [ ] Do **not** change criteria post-hoc to match preferred outcome.

### After evaluation:

- [ ] Classify using four-state model.
- [ ] Document **only control-fail / experimental-pass** as promotion evidence.
- [ ] Request second evaluator for high-stakes decisions.
- [ ] Log trial in inventory.

## Related Documentation

- `docs/develop/010/design/sdlc-ai-agents.md` — SDLC task inventory and known agent shortcomings.
- `.github/agents/*.agent.md` — agent instructions and skills.
- `.github/skills/*/SKILL.md` — skill definitions.
- Agent `learning` — owns agent stack improvements and trial methodology.
