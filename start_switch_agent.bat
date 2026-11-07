@echo off
setlocal
set WORKSPACE=%~dp0

if exist "%WORKSPACE%laya-repo\.venv312\Scripts\python.exe" (
    set PYTHON=%WORKSPACE%laya-repo\.venv312\Scripts\python.exe
) else if exist "%WORKSPACE%laya-repo\.venv\Scripts\python.exe" (
    set PYTHON=%WORKSPACE%laya-repo\.venv\Scripts\python.exe
) else if exist "%WORKSPACE%.venv\Scripts\python.exe" (
    set PYTHON=%WORKSPACE%.venv\Scripts\python.exe
) else (
    set PYTHON=python
)

echo ==================================================================
echo  Starting SwitchGuard AI Collaborative Agent
echo  Powered by: Switch AI + Laya Sub-Millisecond Gate + Ralph Loop
echo ==================================================================
echo  War Room UI:        http://127.0.0.1:8080/
echo  Switch Protocol:    http://127.0.0.1:8080/agent
echo  Health Endpoint:    http://127.0.0.1:8080/healthz
echo ==================================================================

set PYTHONPATH=%WORKSPACE%
"%PYTHON%" -m uvicorn api.index:app --host 127.0.0.1 --port 8080 --reload
