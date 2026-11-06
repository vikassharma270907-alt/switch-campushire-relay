"""Pydantic data models and schemas for SwitchGuard and CampusHire Unified Platform."""
from .triage_models import TriageRequest, AgentMessageRequest
from .wispr_models import StarEvaluateRequest, StarEvaluateResponse, DictateApprovalRequest
from .campushire_models import CampusHireEventRequest

__all__ = [
    "TriageRequest",
    "AgentMessageRequest",
    "StarEvaluateRequest",
    "StarEvaluateResponse",
    "DictateApprovalRequest",
    "CampusHireEventRequest",
]
