<#
.SYNOPSIS
    SECURE: Evaluates the safety of a proposed agent action using "Deny by Default" logic.
.DESCRIPTION
    Validates actions against a strict allowlist. Blocks destructive commands and root path operations.
.PARAMETER Action
    The operation being performed (write_to_file, run_command, etc.)
.PARAMETER Target
    The file path or command string.
.PARAMETER Plan
    Optional context about the current goal.
#>

[CmdletBinding()]
Param(
    [Parameter(Mandatory = $true)]
    [string]$Action,

    [Parameter(Mandatory = $true)]
    [string]$Target,

    [Parameter(Mandatory = $false)]
    [string]$Plan
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# --- SECURITY DEFAULT: DENY ALL ---
# We assume the action is unsafe until proven otherwise.
$RiskLevel = "HIGH"
$Allowed = $false 
$Warnings = @()
$Reason = "Unknown action or target. Explicit confirmation required."

# 1. Normalize Inputs
$Action = $Action.ToLower().Trim()
$Target = $Target.ToLower().Trim()

# 2. Define Safety Patterns (Regex)
# Destructive commands including ALL standard aliases (ri, rd, del, erase, sc, etc.)
$DestructiveCmds = "(rm\s|del\s|ri\s|rd\s|erase\s|remove-item|drop\s|truncate\s|format\s|set-content\s|sc\s|out-file\s|>\s|clear-content|clc\s)"
# Critical system or secret files
$CriticalFiles   = "(\.env|\.config|secrets|passwd|key|\.pem|\.git|id_rsa|\.ssh)"
# Root paths (Windows C:\ or Linux /)
$RootPaths       = "^([c-z]:\\|[c-z]:/$|/$|\\$)"

# 3. Security Logic

# --- CASE A: READ OPERATIONS (Safe) ---
if ($Action -match "^(view_|list_|search_|read_|get-|ls|dir|cat)") {
    $RiskLevel = "NONE"
    $Allowed = $true
    $Reason = "Read-only operation verified."
}

# --- CASE B: WRITE OPERATIONS (Caution) ---
elseif ($Action -eq "write_to_file" -or $Action -eq "replace_file_content" -or $Action -eq "append_to_file") {
    
    # Check for Critical Files first
    if ($Target -match $CriticalFiles) {
        $RiskLevel = "CRITICAL"
        $Allowed = $false
        $Warnings += "Attempt to modify sensitive configuration or secret file."
        $Reason = "Blocked write to sensitive file."
    }
    else {
        # Standard file write
        $RiskLevel = "MEDIUM"
        $Allowed = $true
        $Reason = "Modifying non-critical file content."
    }
}

# --- CASE C: COMMAND EXECUTION (High Risk) ---
elseif ($Action -eq "run_command" -or $Action -eq "invoke-expression" -or $Action -eq "iex") {
    
    # check for destructive patterns
    if ($Target -match $DestructiveCmds) {
        $RiskLevel = "CRITICAL"
        
        # Check for Root/Broad paths
        if ($Target -match $RootPaths -or $Target -match "\s\*$") {
            $Allowed = $false
            $Warnings += "Broad wildcard or root directory destruction detected."
            $Reason = "BLOCKED: Unsafe wide deletion attempt."
        }
        else {
            # Specific deletion (e.g., 'rm ./temp.txt') - Allowed but requires Agent/User confirm
            $Allowed = $true
            $Warnings += "Destructive command detected. Ensure target is correct."
            $Reason = "Destructive command (High Caution)."
        }
    }
    else {
        # Non-destructive command (e.g., 'python script.py', 'echo hello')
        $RiskLevel = "MEDIUM"
        $Allowed = $true
        $Reason = "Standard command execution."
    }
}

# 4. Final Output Construction
$Output = @{
    allowed    = $Allowed
    risk_level = $RiskLevel
    reason     = $Reason
    warnings   = $Warnings
    timestamp  = (Get-Date).ToString("o")
}

Write-Output ($Output | ConvertTo-Json -Depth 3)