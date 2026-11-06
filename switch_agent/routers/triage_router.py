"""Laya System-1 On-Device Triage and Reflex Security Router."""
from __future__ import annotations
from fastapi import APIRouter
from switch_agent.laya_gate import GATE
from switch_agent.models.triage_models import TriageRequest

router = APIRouter(prefix="/api", tags=["Laya System-1 Triage"])


@router.post("/triage")
async def api_triage(req: TriageRequest):
    """Sub-millisecond Laya triage endpoint with prompt-injection defense and intent calibration."""
    decision = GATE.evaluate_request(req.user, req.message)
    return {
        "status": "success",
        "decision": decision.to_dict()
    }
