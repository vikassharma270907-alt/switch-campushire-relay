"""Domain models and schemas for CampusHire Relay."""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class AuditVerdict(str, Enum):
    ELIGIBLE = "eligible"
    INELIGIBLE = "ineligible"
    BORDERLINE = "borderline"


class PlacementCriteria(BaseModel):
    """Extracted hiring and eligibility criteria from recruiter JD."""

    model_config = ConfigDict(frozen=True)

    company_name: str = Field(..., description="Name of the hiring company")
    role_title: str = Field(..., description="Designation / job role")
    package_ctc: str = Field(..., description="Compensation details (e.g. 18 LPA or ₹80,000/month)")
    min_cgpa: float = Field(..., ge=0.0, le=10.0, description="Minimum cut-off CGPA")
    max_active_backlogs: int = Field(default=0, ge=0, description="Maximum allowed active backlogs")
    eligible_branches: List[str] = Field(default_factory=list, description="Target departments/branches")
    batch_year: int = Field(..., description="Target graduation batch year")
    deadline: str = Field(..., description="Application submission deadline")
    drive_date: str = Field(..., description="Interview / test drive date")


class Candidate(BaseModel):
    """Student academic and placement record."""

    model_config = ConfigDict(frozen=True)

    roll_no: str
    name: str
    email: str
    branch: str
    cgpa: float
    active_backlogs: int = 0
    batch_year: int


class CandidateAudit(BaseModel):
    """Individual candidate audit evaluation."""

    model_config = ConfigDict(frozen=True)

    candidate: Candidate
    verdict: AuditVerdict
    reasons: List[str] = Field(default_factory=list)


class AuditReport(BaseModel):
    """Aggregate result of an eligibility audit against placement criteria."""

    model_config = ConfigDict(frozen=True)

    criteria: PlacementCriteria
    total_evaluated: int
    eligible_count: int
    ineligible_count: int
    borderline_count: int
    eligible_candidates: List[Candidate]
    borderline_audits: List[CandidateAudit]
    ineligible_audits: List[CandidateAudit]


class SwitchMessage(BaseModel):
    """Message payload transmitted across Switch room channels."""

    model_config = ConfigDict(frozen=True)

    sender: str
    content: str
    room: str
    mentions: List[str] = Field(default_factory=list)
    timestamp: Optional[str] = None
