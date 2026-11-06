<#
.SYNOPSIS
    Starts the SwitchGuard + Laya + Ralph Collaborative Agent Server.
#>
param(
    [int]$Port = 8080,
    [string]$HostIP = "127.0.0.1"
)

$ErrorActionPreference = "Stop"
$WorkspaceRoot = $PSScriptRoot
$PythonExe = Join-Path $WorkspaceRoot "laya-repo\.venv\Scripts\python.exe"

if (-not (Test-Path $PythonExe)) {
    Write-Error "Virtual environment python not found at $PythonExe"
    exit 1
}

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host " Starting SwitchGuard AI Collaborative Agent" -ForegroundColor Cyan
Write-Host " Powered by: Switch AI + Laya Sub-Millisecond Gate + Ralph Loop" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host " War Room UI:        http://$HostIP`:$Port/" -ForegroundColor Green
Write-Host " Switch Protocol:    http://$HostIP`:$Port/agent" -ForegroundColor Green
Write-Host " Triage API:         http://$HostIP`:$Port/api/triage" -ForegroundColor Green
Write-Host "==================================================================" -ForegroundColor Gray

$env:PYTHONPATH = $WorkspaceRoot
& $PythonExe -m uvicorn switch_agent.server:app --host $HostIP --port $Port --reload
