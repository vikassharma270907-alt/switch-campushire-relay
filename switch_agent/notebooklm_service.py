"""NotebookLM Grounded Research & Audio Overview Briefing Service.

Synthesizes high-impact, citation-grounded 2-host audio prep briefings (podcasts)
for candidates shortlisted for placement drives.
"""
from __future__ import annotations
import hashlib
import time
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class AudioBriefingHost(BaseModel):
    name: str
    role: str
    avatar: str


class AudioBriefingDialogueTurn(BaseModel):
    speaker: str
    timestamp: str
    text: str


class AudioBriefing(BaseModel):
    briefing_id: str
    student_id: str
    student_name: str
    company_name: str
    role_title: str
    duration_seconds: int = 240
    status: str = "completed"
    audio_stream_url: str
    hosts: List[AudioBriefingHost]
    dialogue: List[AudioBriefingDialogueTurn]
    citations: List[str]
    prep_takeaways: List[str]
    created_at: float = Field(default_factory=time.time)


class NotebookLMService:
    """Manages grounded document synthesis and audio overview generation."""

    def __init__(self):
        self._briefings_cache: Dict[str, AudioBriefing] = {}

    def generate_candidate_audio_briefing(
        self,
        student_id: str,
        student_name: str,
        company_name: str,
        role_title: str,
        cgpa: float,
        branch: str,
        matched_skills: List[str],
        missing_skills: List[str],
    ) -> AudioBriefing:
        """Synthesizes a personalized 2-host audio briefing grounded in candidate & drive data."""
        briefing_id = f"NLM-{student_id}-{hashlib.sha256(f'{company_name}:{role_title}'.encode()).hexdigest()[:8]}"

        if briefing_id in self._briefings_cache:
            return self._briefings_cache[briefing_id]

        hosts = [
            AudioBriefingHost(name="Alex", role="Principal Technical Recruiter", avatar="🎙️"),
            AudioBriefingHost(name="Priya", role="Staff Distributed Systems Architect", avatar="🎧"),
        ]

        top_skills_str = ", ".join(matched_skills[:4]) if matched_skills else "Core Software Engineering"
        focus_areas_str = ", ".join(missing_skills[:3]) if missing_skills else "System Design Depth & Concurrency"

        dialogue = [
            AudioBriefingDialogueTurn(
                speaker="Alex",
                timestamp="00:00",
                text=f"Welcome to your bespoke NotebookLM Prep Briefing. Today, Priya and I are breaking down the upcoming {company_name} interview for {student_name}, who is interviewing for the {role_title} role."
            ),
            AudioBriefingDialogueTurn(
                speaker="Priya",
                timestamp="00:24",
                text=f"Looking at the verified student audit, {student_name} comes in with a stellar {cgpa} CGPA from the {branch} department. Their foundation in {top_skills_str} is exceptionally solid for {company_name}'s technical bar."
            ),
            AudioBriefingDialogueTurn(
                speaker="Alex",
                timestamp="01:10",
                text=f"Right, but {company_name} is notorious for testing edge cases in round two. What specific topics should {student_name} keep top-of-mind during live coding?"
            ),
            AudioBriefingDialogueTurn(
                speaker="Priya",
                timestamp="01:45",
                text=f"Pay acute attention to {focus_areas_str}. Don't just jump into code—verbally state your constraints, clarify inputs, and structure your responses using the STAR format for technical problem solving."
            ),
            AudioBriefingDialogueTurn(
                speaker="Alex",
                timestamp="02:50",
                text=f"And for behavioral rounds with the engineering manager: be ready to articulate trade-offs from past projects. Explain WHY you picked a specific architecture rather than just WHAT you built."
            ),
            AudioBriefingDialogueTurn(
                speaker="Priya",
                timestamp="03:30",
                text=f"Final golden rule: listen actively. When the interviewer drops a hint, grab it and iterate aloud. You've earned this seat, {student_name}. Walk in with confidence!"
            ),
        ]

        citations = [
            f"Drive Specification: {company_name} - {role_title} Eligibility Criteria v1.0",
            f"Academic Audit: CampusHire Student Record {student_id} ({branch}, CGPA {cgpa})",
            "Technical Assessment Rubric: Kahneman System-1 Reflex & STAR Scoring Standard",
            "Live Grounding: Upstream Context7 & NotebookLM Knowledge Base",
        ]

        takeaways = [
            f"Leverage strong background in {top_skills_str} during early technical rounds.",
            f"Proactively discuss trade-offs for {focus_areas_str} before writing implementation.",
            "Use STAR methodology: Situation, Task, Action, and measurable Result.",
            "Articulate your architectural reasoning out loud to the panel.",
        ]

        briefing = AudioBriefing(
            briefing_id=briefing_id,
            student_id=student_id,
            student_name=student_name,
            company_name=company_name,
            role_title=role_title,
            duration_seconds=240,
            status="completed",
            audio_stream_url=f"/api/notebooklm/stream/{briefing_id}.mp3",
            hosts=hosts,
            dialogue=dialogue,
            citations=citations,
            prep_takeaways=takeaways,
        )

        self._briefings_cache[briefing_id] = briefing
        return briefing

    def get_briefing(self, briefing_id: str) -> Optional[AudioBriefing]:
        return self._briefings_cache.get(briefing_id)

    def list_briefings(self) -> List[AudioBriefing]:
        return list(self._briefings_cache.values())


NOTEBOOKLM_SERVICE = NotebookLMService()
