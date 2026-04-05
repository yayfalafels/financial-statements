param()

$raw = [Console]::In.ReadToEnd()
if ([string]::IsNullOrWhiteSpace($raw)) {
  # No input: do nothing, allow normal approval flow
  Write-Output '{"continue":true}'
  exit 0
}

$evt = $raw | ConvertFrom-Json -Depth 20

# Tool names can vary by environment; treat common terminal names as terminal tools.
$toolName = [string]$evt.tool_name
$isTerminalTool = $toolName -match 'terminal|run.?in.?terminal|shell'

# Try common fields where command text may appear.
$cmd = ""
if ($evt.tool_input -and $evt.tool_input.command) { $cmd = [string]$evt.tool_input.command }
if (-not $cmd -and $evt.tool_input -and $evt.tool_input.args) { $cmd = [string]($evt.tool_input.args -join " ") }

$isPowerShellCommand = $cmd -match '(^|\s)(powershell|pwsh)(\s|$)'

if ($isTerminalTool -and $isPowerShellCommand) {
  # Pre-approve matching PowerShell terminal commands
  $out = @{
    hookSpecificOutput = @{
      hookEventName = "PreToolUse"
      permissionDecision = "allow"
      permissionDecisionReason = "Auto-approved by workspace hook: PowerShell terminal command."
    }
  } | ConvertTo-Json -Depth 10 -Compress
  Write-Output $out
  exit 0
}

# Fall back to normal behavior for everything else
Write-Output '{"continue":true}'
exit 0
