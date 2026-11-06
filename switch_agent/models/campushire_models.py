"""CampusHire multi-agent room interaction request schemas."""
from __future__ import annotations
from typing import List
from pydantic import BaseModel, Field, ConfigDict


class CampusHireEventRequest(BaseModel):
    """Inbound Switch Room message event for multi-agent coordination."""
    model_config = ConfigDict(frozen=True)
    sender: str = "PlacementOfficer"
    content: str = Field(..., min_length=1)
    room: str = "#placement-drive-2027"
    mentions: List[str] = Field(default_factory=list)
