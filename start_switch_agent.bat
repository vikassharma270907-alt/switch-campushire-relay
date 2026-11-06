@echo off
set WORKSPACE=%~dp0
set PYTHON=%WORKSPACE%laya-repo\.venv\Scripts\python.exe

echo ==================================================================
echo  Starting SwitchGuard AI Collaborative Agent
echo  Powered by: Switch AI + Laya Sub-Millisecond Gate + Ralph Loop
echo ==================================================================
echo  War Room UI:     http://127.0.0.1:8080/
echo  Switch Protocol: http://127.0.0.1:8080/agent
echo ==================================================================

set PYTHONPATH=%WORKSPACE%
"%PYTHON%" -m uvicorn switch_agent.server:app --host 127.0.0.1 --port 8080 --reload
