<#
.SYNOPSIS
    Antigravity Project Synchronization Script
    Provisions all 434+ skills, 107+ agents, 126+ rules, 99+ workflows,
    CodeRabbit, Ralph autonomous loop, and MCP servers into the target project.
#>
param(
    [string]$ProjectPath = (Get-Location).Path,
    [switch]$AllProjects,
    [switch]$All
)

$runAll = $AllProjects.IsPresent -or $All.IsPresent
& "C:\Users\vikas sharma\.gemini\config\setup-project.ps1" -ProjectPath $ProjectPath -AllProjects:$runAll
