"""CampusHire Relay Multi-Agent Room & Deterministic Audit Router."""
from __future__ import annotations
import os
import sys
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

# Ensure campushire-relay is on sys.path
_CAMPUSHIRE_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "campushire-relay")
if _CAMPUSHIRE_ROOT not in sys.path:
    sys.path.insert(0, _CAMPUSHIRE_ROOT)

from campushire.models import SwitchMessage
from campushire.switch_room import SwitchRoom
from campushire.storage.student_db import StudentRepository
from switch_agent.models.campushire_models import CampusHireEventRequest

router = APIRouter(tags=["CampusHire Multi-Agent Room"])

# Initialize shared student repository and SwitchRoom singleton
repo = StudentRepository()
repo.load_synthetic_dataset()
room = SwitchRoom(student_repo=repo, room_name="#placement-drive-2027")


@router.get("/api/campushire/candidates")
@router.get("/api/candidates")
def list_candidates() -> List[Dict[str, Any]]:
    """Return all candidate records in the student database with academic metrics."""
    return [c.model_dump() for c in repo.get_all_candidates()]


@router.post("/api/campushire/events")
@router.post("/api/switch/events")
def handle_switch_event(event: CampusHireEventRequest) -> Dict[str, Any]:
    """Handle incoming Switch Room webhooks and return multi-agent coordination responses."""
    try:
        msg = SwitchMessage(
            sender=event.sender,
            content=event.content,
            room=event.room,
            mentions=event.mentions,
        )
        responses = room.handle_message(msg)
        return {
            "status": "processed",
            "received_message": msg.model_dump(),
            "responses": [r.model_dump() for r in responses],
            "room_history_length": len(room.history),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/api/campushire/audit/report")
@router.get("/api/audit/report")
def get_audit_report() -> Dict[str, Any]:
    """Return the active eligibility audit report with SHA-256 cryptographic hashes."""
    if not room.active_report:
        return {"status": "no_active_audit", "message": "No active audit report available. Submit a notice to @DriveCoordinator first."}
    return room.active_report.model_dump()


@router.get("/api/campushire/audit/export-csv")
@router.get("/api/audit/export-csv")
def export_csv() -> Response:
    """Download verified candidate shortlist as a CSV file."""
    if not room.active_report:
        raise HTTPException(status_code=400, detail="No active audit report available to export.")
    csv_data = room.eligibility_auditor.export_shortlist_csv(room.active_report)
    company = room.active_report.criteria.company_name.lower().replace(" ", "_")
    filename = f"shortlist_{company}.csv"
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
