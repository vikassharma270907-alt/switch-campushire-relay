"""Triage and Switch Agent Protocol message request and response schemas."""
from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class TriageRequest(BaseModel):
    """Sub-millisecond triage request schema."""
    model_config = ConfigDict(frozen=True)
    user: str = "User"
    message: str = Field(..., min_length=1)


class AgentMessageRequest(BaseModel):
    """Switch AI Agent Protocol inbound message payload."""
    model_config = ConfigDict(frozen=True)
    sender: str = "TeamMember"
    text: Optional[str] = None
    content: Optional[str] = None
    stream: bool = False
    mentions: List[str] = Field(default_factory=list)


class RalphExecuteRequest(BaseModel):
    """Ralph autonomous loop execution request schema."""
    model_config = ConfigDict(frozen=True)
    task_name: str
    description: str = ""


class DocsLookupRequest(BaseModel):
    """Context7 documentation lookup request schema."""
    model_config = ConfigDict(frozen=True)
    library: str = Field(..., min_length=1)
    query: str = Field(..., min_length=1)
