---
name: gas-ui
description: Use when working on the optional Google Apps Script bridge for selected click-driven actions from Google Sheets into the backend API.
---

# GAS UI

## Summary

Use this skill for reusable Google Apps Script guidance around click-driven spreadsheet actions, UrlFetchApp calls, trigger constraints, and authorization behavior. Keep project-specific workflow design in the agent file.

## Apply This Skill When

- Designing or refining Apps Script handlers for click-triggered actions.
- Defining request payloads sent from Apps Script to backend API endpoints.
- Managing sheet-bound UI affordances that start backend actions but do not own workflow state.
- Clarifying which actions remain direct sheet reads and writes versus optional GAS-triggered calls.

## Rules

- Keep GAS limited to user-triggered click events and lightweight UI bridge logic.
- Do not move close-session orchestration or business rules into Apps Script.
- Preserve workbook governance through configured sheet names, named ranges, and approved endpoints.
- Prefer explicit payload construction and logging for each triggered event.
- Handle backend failures with user-visible status feedback in the sheet UI.
- Do not represent IMPORTRANGE behavior as GAS logic.

## Official Sources

- UrlFetchApp reference: https://developers.google.com/apps-script/reference/url-fetch/url-fetch-app
	UrlFetchApp supports `fetch`, `fetchAll`, and `getRequest`, and requires the `script.external_request` scope for outbound calls.
- Apps Script triggers guide: https://developers.google.com/apps-script/guides/triggers
	Simple triggers have strict limits, including no-authorization restrictions for some services and a 30-second runtime ceiling.
- Apps Script authorization guide: https://developers.google.com/apps-script/guides/services/authorization
	Apps Script auto-detects scopes from code, but published or tightly scoped projects can and should declare explicit scopes in the manifest.

## Useful Takeaways

- `UrlFetchApp.getRequest` is useful for inspecting the generated request shape before issuing a backend call.
- Simple triggers do not run for programmatic edits and cannot always access services requiring authorization, which is why the bridge must stay narrow.
- Installable triggers and explicit scopes are the safer path once the script goes beyond trivial menu or button behavior.

## Validation Focus

- Trigger scope is explicit and narrow.
- Backend endpoint contracts are stable and documented.
- User feedback is visible when a trigger fails or returns a blocking status.
- No hidden business state is stored only in Apps Script.