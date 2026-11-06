"""CampusHire multi-agent room interaction request and response schemas."""
from __future__ import annotations
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict


class CampusHireEventRequest(BaseModel):
    """Inbound Switch Room message event for multi-agent coordination."""
    model_config = ConfigDict(frozen=True)
    sender: str = "PlacementOfficer"
    content: str = Field(..., min_length=1)
    room: str = "#placement-drive-2027"
    mentions: List[str] = Field(default_factory=list)


class NoticeIngestRequest(BaseModel):
    """Recruiter notice ingestion payload for Laya screening and criteria extraction."""
    model_config = ConfigDict(frozen=True)
    notice_text: str = Field(..., min_length=10)
    source: Optional[str] = "recruiter"


class NoticeIngestResponse(BaseModel):
    """Result of notice screening and extraction."""
    safe: bool
    latency_ms: float
    risk_score: float
    flags: List[str] = Field(default_factory=list)
    requires_human_clarification: bool = False
    missing_or_ambiguous_fields: List[str] = Field(default_factory=list)
    criteria: Dict[str, Any] = Field(default_factory=dict)
    message: str


class DirectAuditRequest(BaseModel):
    """Direct deterministic audit trigger parameters."""
    model_config = ConfigDict(frozen=True)
    company: str = "Northstar Technologies"
    role: str = "Graduate Engineer Trainee"
    graduation_year: int = 2027
    eligible_branches: List[str] = Field(default_factory=lambda: ["CSE", "IT"])
    minimum_cgpa: float = Field(default=7.0, ge=0.0, le=10.0)
    active_backlogs_allowed: int = Field(default=0, ge=0)


class HallPassVerifyRequest(BaseModel):
    """Candidate hall pass verification payload for invigilators."""
    model_config = ConfigDict(frozen=True)
    student_id: str = Field(..., min_length=1)
    seat_no: str = Field(..., min_length=1)
    token: str = Field(..., min_length=8)
    company: str = "Northstar Technologies"


class HallPassVerifyResponse(BaseModel):
    """Result of hall pass token authentication."""
    valid: bool
    student_id: str
    seat_no: str
    company: str
    timestamp: float
    status: str


class SkillGapRequest(BaseModel):
    """Candidate skill gap analysis query."""
    model_config = ConfigDict(frozen=True)
    student_id: Optional[str] = None
    branch: Optional[str] = "CSE"
    candidate_skills: Optional[List[str]] = None
    target_role: str = "graduate engineer trainee"


class SkillGapResponse(BaseModel):
    """Skill gap analysis and readiness metrics."""
    student_id: Optional[str]
    target_role: str
    match_percentage: float
    matched_skills: List[str]
    missing_skills: List[str]
    readiness_level: str
    recommendations: List[str]
    recommended_projects: List[Dict[str, Any]] = Field(default_factory=list)


class CounterfactualResponse(BaseModel):
    """Counterfactual explanation for a student's audit decision."""
    student_id: str
    current_status: str
    reasons: List[str]
    minimal_changes_needed: Dict[str, Any]
    eligible_if_adjusted: bool


class MerkleLedgerResponse(BaseModel):
    """Tamper-evident Merkle audit ledger state."""
    total_events: int
    merkle_root: str
    leaves: List[str]
    recent_history: List[Dict[str, Any]]
