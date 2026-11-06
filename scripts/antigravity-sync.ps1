<#
.SYNOPSIS
    Antigravity Project Synchronization Script
    Provisions all 434+ skills, 107+ agents, 126+ rules, 99+ workflows,
    ArmorAntigravity governance, CodeRabbit, Ralph autonomous loop, and MCP servers into the target project.
#>
param(
    [string]$ProjectPath = (Get-Location).Path,
    [switch]$AllProjects,
    [switch]$All
)

$runAll = $AllProjects.IsPresent -or $All.IsPresent
$setupScript = Join-Path $PSScriptRoot 'setup-project.ps1'
if (-not (Test-Path -LiteralPath $setupScript)) {
    $setupScript = Join-Path $env:USERPROFILE '.gemini\config\setup-project.ps1'
}

if (Test-Path -LiteralPath $setupScript) {
    & $setupScript -ProjectPath $ProjectPath -AllProjects:$runAll
} else {
    Write-Error "Antigravity setup script not found at $setupScript"
}
