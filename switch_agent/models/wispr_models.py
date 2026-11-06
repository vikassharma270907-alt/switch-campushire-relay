"""Wispr Flow voice integration and STAR rubric evaluation schemas."""
from __future__ import annotations
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, ConfigDict


class StarEvaluateRequest(BaseModel):
    """Wispr Flow voice transcript payload for STAR interview scoring."""
    model_config = ConfigDict(frozen=True)
    student_id: Optional[str] = Field(default="Candidate", description="Student roll no or name")
    spoken_text: str = Field(..., min_length=5, description="Voice-dictated interview answer")
    target_role: str = Field(default="Software Engineer", description="Target job role")


class StarEvaluateResponse(BaseModel):
    """STAR rubric evaluation score breakdown and constructive feedback."""
    model_config = ConfigDict(frozen=True)
    star_score: float
    dimensions: Dict[str, bool]
    recommendations: List[str]
    word_count: int
    latency_ms: float


class DictateApprovalRequest(BaseModel):
    """Voice-dictated placement officer waiver or action."""
    model_config = ConfigDict(frozen=True)
    officer_name: str = Field(default="PlacementOfficer", description="Officer identity")
    spoken_audio_transcript: str = Field(..., min_length=3, description="Wispr Flow transcribed dictation")
    room_name: str = Field(default="#placement-drive-2027", description="Target Switch room")
