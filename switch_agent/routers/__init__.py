"""Modular API Routers for SwitchGuard & CampusHire Unified Backend."""
from .agent_router import router as agent_router
from .triage_router import router as triage_router
from .campushire_router import router as campushire_router
from .wispr_router import router as wispr_router
from .ralph_router import router as ralph_router
from .telemetry_router import router as telemetry_router
from .docs_router import router as docs_router
from .security_router import router as security_router
from .ui_router import router as ui_router

__all__ = [
    "agent_router",
    "triage_router",
    "campushire_router",
    "wispr_router",
    "ralph_router",
    "telemetry_router",
    "docs_router",
    "security_router",
    "ui_router",
]
