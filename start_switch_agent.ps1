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

$Candidates = @(
    (Join-Path $WorkspaceRoot "laya-repo\.venv312\Scripts\python.exe"),
    (Join-Path $WorkspaceRoot "laya-repo\.venv\Scripts\python.exe"),
    (Join-Path $WorkspaceRoot ".venv\Scripts\python.exe")
)

$PythonExe = "python"
foreach ($Candidate in $Candidates) {
    if (Test-Path $Candidate) {
        $PythonExe = $Candidate
        break
    }
}

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host " Starting SwitchGuard AI Collaborative Agent" -ForegroundColor Cyan
Write-Host " Powered by: Switch AI + Laya Sub-Millisecond Gate + Ralph Loop" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host " Python Engine:      $PythonExe" -ForegroundColor Yellow
Write-Host " War Room UI:        http://$HostIP`:$Port/" -ForegroundColor Green
Write-Host " Switch Protocol:    http://$HostIP`:$Port/agent" -ForegroundColor Green
Write-Host " Health Endpoint:    http://$HostIP`:$Port/healthz" -ForegroundColor Green
Write-Host " Triage API:         http://$HostIP`:$Port/api/triage" -ForegroundColor Green
Write-Host "==================================================================" -ForegroundColor Gray

$env:PYTHONPATH = $WorkspaceRoot
& $PythonExe -m uvicorn api.index:app --host $HostIP --port $Port --reload
