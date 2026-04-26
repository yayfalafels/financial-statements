---
name: github-copilot-local-files
description: Inspecting local VS Code and GitHub Copilot data files on Windows under AppData Roaming Code, including raw chat sessions, transcripts, and debug logs for troubleshooting, traceability, and workflow analysis
license: MIT
compatibility: VS Code on Windows
metadata:
  author: yayfalafels
  version: 1.0.0
---

## Contents

- Overview
- Summary
- Related documentation
- Scope boundary
- Core local paths
- High-value Copilot artifacts
- Verified inspection commands
- Workflow for direct history inspection
- Safety and privacy rules
- Troubleshooting

## Overview

This skill helps inspect local VS Code and GitHub Copilot artifacts stored under `C:\Users\<user>\AppData\Roaming\Code` on Windows. It is for direct evidence gathering from session files, transcript files, and debug logs when you need factual traceability instead of inferred history.

This skill is especially useful for:

- finding raw prior conversation histories
- verifying what tools were called and when
- validating model and extension metadata for sessions
- locating workspace-scoped chat session files

## Summary

| id | task                              | location or command                                                               |
| -- | --------------------------------- | --------------------------------------------------------------------------------- |
| 01 | open user data root               | `C:\Users\<user>\AppData\Roaming\Code`                                            |
| 02 | inspect workspace storage root    | `C:\Users\<user>\AppData\Roaming\Code\User\workspaceStorage`                      |
| 03 | inspect Copilot workspace data    | `...\workspaceStorage\<workspaceId>\GitHub.copilot-chat`                          |
| 04 | inspect raw transcript files      | `...\GitHub.copilot-chat\transcripts\*.jsonl`                                     |
| 05 | inspect debug logs                | `...\GitHub.copilot-chat\debug-logs\<sessionId>\main.jsonl`                       |
| 06 | inspect session metadata          | `...\chatSessions\*.jsonl`                                                        |
| 07 | inspect no-workspace sessions     | `C:\Users\<user>\AppData\Roaming\Code\User\globalStorage\emptyWindowChatSessions` |
| 08 | check VS Code logs by timestamp   | `C:\Users\<user>\AppData\Roaming\Code\logs\<timestamp>`                           |

## Related Documentation

- VS Code settings file locations and user data basics: https://code.visualstudio.com/docs/configure/settings
- VS Code CLI and `--user-data-dir`: https://code.visualstudio.com/docs/configure/command-line
- Manage chat sessions and export behavior: https://code.visualstudio.com/docs/copilot/chat/chat-sessions
- Debug chat interactions and persisted agent logs: https://code.visualstudio.com/docs/copilot/chat/chat-debug-view

## Scope Boundary

Use this skill for direct local file inspection under the VS Code user data tree on Windows.

Do not treat `/memories` as a disk folder path. `/memories` is a tool-scoped virtual memory system exposed by the agent runtime. For physical files and raw artifacts, use the Windows paths under `C:\Users\<user>\AppData\Roaming\Code`.

## Core Local Paths

- `C:\Users\<user>\AppData\Roaming\Code`
- `C:\Users\<user>\AppData\Roaming\Code\User`
- `C:\Users\<user>\AppData\Roaming\Code\User\workspaceStorage`
- `C:\Users\<user>\AppData\Roaming\Code\User\globalStorage`
- `C:\Users\<user>\AppData\Roaming\Code\logs`

## High-Value Copilot Artifacts

Within a workspace storage directory such as:

`C:\Users\<user>\AppData\Roaming\Code\User\workspaceStorage\<workspaceId>`

look for:

- `chatSessions\*.jsonl`
- `GitHub.copilot-chat\transcripts\*.jsonl`
- `GitHub.copilot-chat\debug-logs\<sessionId>\main.jsonl`
- `GitHub.copilot-chat\debug-logs\<sessionId>\models.json`
- `GitHub.copilot-chat\memory-tool\`
- `GitHub.copilot-chat\chat-session-resources\`

Common evidence signals:

- transcript files contain session messages and tool call records in JSONL format
- debug log `main.jsonl` contains event lines such as `session_start`
- debug log `models.json` contains model catalog details observed in the session window
- session files in `chatSessions` contain request metadata and input state snapshots

## Verified Inspection Commands

Use PowerShell commands similar to the following.

```powershell
Get-ChildItem -Path "C:\Users\$env:USERNAME\AppData\Roaming\Code\User\workspaceStorage"
```

```powershell
Get-ChildItem -Path "C:\Users\$env:USERNAME\AppData\Roaming\Code\User\workspaceStorage\<workspaceId>\GitHub.copilot-chat\transcripts"
```

```powershell
Get-ChildItem -Path "C:\Users\$env:USERNAME\AppData\Roaming\Code\User\workspaceStorage\<workspaceId>\GitHub.copilot-chat\debug-logs" -Recurse -File |
  Select-Object -First 20 FullName, Length
```

```powershell
Get-Content -Path "C:\Users\$env:USERNAME\AppData\Roaming\Code\User\workspaceStorage\<workspaceId>\GitHub.copilot-chat\transcripts\<sessionId>.jsonl" -TotalCount 5
```

```powershell
Get-Content -Path "C:\Users\$env:USERNAME\AppData\Roaming\Code\User\workspaceStorage\<workspaceId>\GitHub.copilot-chat\debug-logs\<sessionId>\main.jsonl" -TotalCount 10
```

```powershell
Get-ChildItem -Path "C:\Users\$env:USERNAME\AppData\Roaming\Code\User\globalStorage\emptyWindowChatSessions"
```

## Workflow For Direct History Inspection

1. Identify the workspace storage ID for the target workspace.
2. Open `chatSessions` to list candidate session IDs.
3. Open `GitHub.copilot-chat\transcripts` and match session IDs.
4. Read the first lines of the transcript JSONL to validate the correct session.
5. Open `debug-logs\<sessionId>\main.jsonl` for event-level diagnostics.
6. Open `debug-logs\<sessionId>\models.json` if model metadata is needed.
7. Cross-check with UI tools such as Agent Debug Logs or Chat Debug view when available.

## Safety And Privacy Rules

- Assume transcript and debug files may include sensitive prompts, file paths, and tool payloads.
- Read only the minimum lines needed to establish evidence.
- Do not copy raw secrets into repository documentation.
- Prefer summarizing findings over pasting full raw payloads.
- Keep analysis local unless explicit user approval exists for sharing.

## Troubleshooting

- If a path is missing, verify the workspace ID under `User\workspaceStorage`.
- If transcript files are absent, confirm the session ran in this workspace and was not deleted.
- If debug files are absent, enable Copilot debug logging through VS Code settings and retry.
- If outputs look truncated in terminal listing, use `ForEach-Object { $_.FullName }` to print full paths.