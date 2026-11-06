@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0antigravity-sync.ps1" -ProjectPath "%CD%"
