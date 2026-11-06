"""Switch AI Agent Protocol Router supporting metadata handshake, SSE streaming, and webhooks."""
from __future__ import annotations
import json
from typing import Optional
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse

from switch_agent.config import CONFIG
from switch_agent.laya_gate import GATE
from switch_agent.models.triage_models import AgentMessageRequest

router = APIRouter(tags=["Switch AI Protocol"])

SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",
}


async def sse_event_stream(payload: dict):
    """Unified generator helper for SSE event streaming."""
    yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
    yield "data: [DONE]\n\n"


@router.get("/agent")
async def switch_agent_discovery():
    """Switch AI Agent Protocol handshake and metadata discovery."""
    return {
        "name": CONFIG.bot_name,
        "avatar": CONFIG.bot_avatar,
        "description": CONFIG.bot_description,
        "protocol": "switch-v1",
        "capabilities": [
            "triage",
            "guardrails",
            "autonomous-coding",
            "human-in-the-loop",
            "campushire-placement",
            "wispr-voice",
            "notebooklm-briefing",
            "strix-pentest",
            "500-ai-projects",
            "armoriq-receipts"
        ]
    }


@router.post("/agent")
async def switch_agent_protocol(request: Request, payload: Optional[AgentMessageRequest] = None):
    """Switch AI Agent Protocol message handler supporting SSE streaming and JSON webhooks."""
    if payload is None:
        try:
            body = await request.json()
            if not isinstance(body, dict):
                raise HTTPException(status_code=400, detail="Invalid JSON payload: expected a dictionary")
            payload = AgentMessageRequest(**body)
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid or malformed JSON in request body")

    user = payload.sender or "TeamMember"
    message = payload.text or payload.content or ""
    stream_requested = bool(payload.stream) or (request.headers.get("accept") == "text/event-stream")

    decision = GATE.evaluate_request(user, message)

    if not decision.is_safe:
        resp_text = f"🛑 Action blocked by Laya Guardrail: {decision.reason}"
        out = {
            "response": resp_text,
            "chunk": resp_text,
            "metadata": decision.to_dict()
        }
        if stream_requested:
            return StreamingResponse(sse_event_stream(out), media_type="text/event-stream", headers=SSE_HEADERS)
        return out

    if decision.requires_human_approval:
        resp_text = f"⚠️ Human-in-the-loop approval required: {decision.reason}"
        out = {
            "response": resp_text,
            "chunk": resp_text,
            "requires_approval": True,
            "metadata": decision.to_dict()
        }
        if stream_requested:
            return StreamingResponse(sse_event_stream(out), media_type="text/event-stream", headers=SSE_HEADERS)
        return out

    resp_text = f"✅ Triaged in {decision.latency_ms}ms ({decision.intent}) with confidence {decision.confidence}."
    out = {
        "response": resp_text,
        "chunk": resp_text,
        "metadata": decision.to_dict()
    }
    if stream_requested:
        return StreamingResponse(sse_event_stream(out), media_type="text/event-stream", headers=SSE_HEADERS)

    return out
