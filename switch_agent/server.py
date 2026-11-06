"""FastAPI server for SwitchGuard + Laya + Ralph collaborative agent.

Implements:
1. Switch AI HTTP & SSE Agent Protocol (/agent).
2. Sub-millisecond Laya Triage API (/api/triage).
3. Ralph Autonomous Loop execution (/api/ralph/execute).
4. Team War Room Interactive Dashboard (/ static).
"""
from __future__ import annotations
import os
import subprocess
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .config import CONFIG
from .laya_gate import GATE
from .ralph_runner import RalphCollaborativeRunner

app = FastAPI(
    title="SwitchGuard AI Agent",
    description="Collaborative AI Agent for Switch powered by Laya on-device triage and Ralph autonomous execution.",
    version="1.0.0"
)

runner = RalphCollaborativeRunner(workspace_root=CONFIG.workspace_root)
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

class TriageRequest(BaseModel):
    user: str = "User"
    message: str

class RalphExecuteRequest(BaseModel):
    task_name: str
    description: str = ""

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """Serves the interactive team war room dashboard."""
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>SwitchGuard Agent Running</h1>"

@app.post("/api/triage")
async def api_triage(req: TriageRequest):
    """Sub-millisecond Laya triage endpoint."""
    decision = GATE.evaluate_request(req.user, req.message)
    return {
        "status": "success",
        "decision": decision.to_dict()
    }

@app.post("/api/ralph/execute")
async def api_ralph_execute(req: RalphExecuteRequest):
    """Executes a single Ralph autonomous loop iteration."""
    prd = runner.get_or_create_prd(req.task_name, req.description)
    story_id = prd["userStories"][0]["id"]
    events = []
    success = True
    for ev in runner.execute_story_iteration(story_id):
        events.append({
            "iteration": ev.iteration,
            "story_id": ev.story_id,
            "status": ev.status,
            "details": ev.details,
            "timestamp": ev.timestamp
        })
        if ev.status == "failed":
            success = False

    return {
        "status": "completed" if success else "failed",
        "story_id": story_id,
        "events": events
    }

@app.post("/api/test/run")
async def api_test_run():
    """Runs test_agent_gate.py verification suite."""
    laya_repo = os.path.join(CONFIG.workspace_root, "laya-repo")
    python_exe = os.path.join(laya_repo, ".venv", "Scripts", "python.exe")
    if os.path.exists(python_exe):
        res = subprocess.run(
            [python_exe, "tests/test_agent_gate.py"],
            cwd=laya_repo,
            capture_output=True,
            text=True,
            timeout=15
        )
        return {
            "status": "passed" if res.returncode == 0 else "failed",
            "output": res.stdout or res.stderr
        }
    return {"status": "error", "output": "Python environment not found."}

@app.api_route("/agent", methods=["GET", "POST"])
async def switch_agent_protocol(request: Request):
    """Switch AI Agent Protocol endpoint supporting SSE and Webhook messages."""
    if request.method == "GET":
        # Handshake / metadata for Switch AI registration
        return {
            "name": CONFIG.bot_name,
            "avatar": CONFIG.bot_avatar,
            "description": CONFIG.bot_description,
            "protocol": "switch-v1",
            "capabilities": ["triage", "guardrails", "autonomous-coding", "human-in-the-loop"]
        }

    # Handle incoming Switch message
    data = await request.json()
    user = data.get("sender", "TeamMember")
    message = data.get("text", "") or data.get("content", "")

    decision = GATE.evaluate_request(user, message)
    if not decision.is_safe:
        return {
            "response": f"🛑 Action blocked by Laya Guardrail: {decision.reason}",
            "metadata": decision.to_dict()
        }

    if decision.requires_human_approval:
        return {
            "response": f"⚠️ Human-in-the-loop approval required: {decision.reason}",
            "requires_approval": True,
            "metadata": decision.to_dict()
        }

    return {
        "response": f"✅ Triaged in {decision.latency_ms}ms ({decision.intent}) with confidence {decision.confidence}.",
        "metadata": decision.to_dict()
    }
