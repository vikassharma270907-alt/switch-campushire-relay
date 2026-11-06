"""Wispr Flow Voice Dictation & Laya STAR Rubric Scoring Router."""
from __future__ import annotations
import os
import re
import sys
from typing import Dict, Any
from fastapi import APIRouter, HTTPException

# Ensure campushire-relay and scripts are on sys.path
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_SCRIPTS = os.path.join(_ROOT, "campushire-relay", "scripts")
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)

from laya_service import LayaDecisionEngine
from campushire.models import SwitchMessage
from campushire.switch_room import AUTHORIZED_OFFICERS
from switch_agent.laya_gate import GATE
from switch_agent.routers.campushire_router import room
from switch_agent.models.wispr_models import (
    StarEvaluateRequest,
    StarEvaluateResponse,
    DictateApprovalRequest,
)

router = APIRouter(prefix="/api/wispr", tags=["Wispr Flow Voice & STAR Scoring"])
_laya_engine = LayaDecisionEngine()


@router.post("/star-evaluate", response_model=StarEvaluateResponse)
def evaluate_star(req: StarEvaluateRequest) -> StarEvaluateResponse:
    """Evaluate voice-dictated student mock interview response against the STAR framework in <50ms."""
    result = _laya_engine.evaluate_star_response(req.spoken_text, req.target_role)
    return StarEvaluateResponse(
        star_score=result["star_score"],
        dimensions=result["dimensions"],
        recommendations=result["recommendations"],
        word_count=result["word_count"],
        latency_ms=result["latency_ms"],
    )


@router.post("/dictate-approval")
def dictate_approval(req: DictateApprovalRequest) -> Dict[str, Any]:
    """Process voice-dictated placement officer approvals and waivers with System-1 guardrails."""
    # 1. System-1 Safety Guardrail Screening
    decision = GATE.evaluate_request(req.officer_name, req.spoken_audio_transcript)
    if not decision.is_safe:
        raise HTTPException(
            status_code=400,
            detail=f"Laya Guardrail Triggered: Adversarial prompt injection detected in spoken dictation ({decision.reason}).",
        )

    # 2. Authorization Check
    if req.officer_name not in AUTHORIZED_OFFICERS:
        raise HTTPException(
            status_code=403,
            detail=f"Authorization Refusal: Officer '{req.officer_name}' is not authorized to grant waivers.",
        )

    # 3. Candidate Roll No extraction
    roll_matches = re.findall(r"\b(2[0-9][A-Z]{2,4}[0-9]{2,3})\b", req.spoken_audio_transcript.upper())
    target_candidate = roll_matches[0] if roll_matches else "ALL"

    # 4. Dispatch into SwitchRoom
    msg = SwitchMessage(
        sender=req.officer_name,
        content=f"@EligibilityAuditor {req.spoken_audio_transcript}",
        room=req.room_name,
        mentions=["@EligibilityAuditor"],
    )
    responses = room.handle_message(msg)

    return {
        "status": "processed",
        "officer": req.officer_name,
        "target_candidate": target_candidate,
        "dictation": req.spoken_audio_transcript,
        "responses": [r.model_dump() for r in responses],
    }
