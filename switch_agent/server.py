"""FastAPI Unified Master Server for Flip the Switch Hackathon.

Integrates:
1. Switch AI Agent Protocol (/agent with SSE & Webhook support)
2. Laya System-1 Sub-Millisecond Reflex Gate (/api/triage)
3. CampusHire Relay Multi-Agent Room (/api/campushire/*, /api/switch/*)
4. Wispr Flow Voice Integration & STAR Scoring (/api/wispr/*)
5. Ralph Autonomous Execution Loop (/api/ralph/*)
6. Telemetry & Verification (/healthz, /api/health, /api/test/run, /api/pipeline/run)
7. Team War Room Interactive Dashboard (/)
"""
from __future__ import annotations
import os
import sys
import subprocess
sys.modules["switch_agent.server.subprocess"] = subprocess
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from .config import CONFIG
from .laya_gate import GATE
from .ralph_runner import RalphCollaborativeRunner
from .models.triage_models import TriageRequest, AgentMessageRequest, RalphExecuteRequest

from .routers.agent_router import router as agent_router, SSE_HEADERS
from .routers.triage_router import router as triage_router
from .routers.campushire_router import router as campushire_router
from .routers.wispr_router import router as wispr_router
from .routers.ralph_router import router as ralph_router, runner
from .routers.telemetry_router import router as telemetry_router
from .routers.docs_router import router as docs_router

app = FastAPI(
    title="SwitchGuard & CampusHire Unified AI Platform",
    description="Unified collaborative AI platform connecting Switch AI protocol, Laya System-1 reflexes, CampusHire multi-agent placement room, Wispr Flow voice scoring, and Ralph autonomous loops.",
    version="2.0.0"
)

# Enable CORS for Switch frontend clients & webhooks
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount domain routers
app.include_router(agent_router)
app.include_router(triage_router)
app.include_router(campushire_router)
app.include_router(wispr_router)
app.include_router(ralph_router)
app.include_router(telemetry_router)
app.include_router(docs_router)
app.include_router(docs_router)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """Serves the interactive team war room dashboard."""
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>SwitchGuard & CampusHire Unified Platform Running</h1>"


# Backward compatibility re-exports
__all__ = [
    "app",
    "runner",
    "GATE",
    "CONFIG",
    "TriageRequest",
    "AgentMessageRequest",
    "RalphExecuteRequest",
    "SSE_HEADERS",
]
