"""Ralph Autonomous Collaborative Execution Loop Router."""
from __future__ import annotations
import tempfile
from fastapi import APIRouter
from switch_agent.config import CONFIG
from switch_agent.models.triage_models import RalphExecuteRequest
from switch_agent.ralph_runner import RalphCollaborativeRunner

router = APIRouter(prefix="/api/ralph", tags=["Ralph Autonomous Loop"])
runner = RalphCollaborativeRunner(workspace_root=CONFIG.workspace_root)


@router.post("/execute")
async def api_ralph_execute(req: RalphExecuteRequest):
    """Executes a single autonomous Ralph loop iteration on an approved story."""
    try:
        active_runner = runner
        prd = active_runner.get_or_create_prd(req.task_name, req.description)
    except (OSError, PermissionError):
        # Fallback to serverless writable temporary directory
        fallback_root = tempfile.gettempdir()
        active_runner = RalphCollaborativeRunner(workspace_root=fallback_root)
        prd = active_runner.get_or_create_prd(req.task_name, req.description)

    stories = prd.get("userStories", [])
    if not stories:
        return {"status": "no_stories", "message": "No pending stories in PRD"}

    target_story = stories[0]
    story_id = target_story.get("id", "US-001")

    events = []
    success = True
    for ev in active_runner.execute_story_iteration(story_id):
        events.append({
            "iteration": ev.iteration,
            "story_id": ev.story_id,
            "status": ev.status,
            "details": ev.details,
            "timestamp": ev.timestamp
        })
        if ev.status == "failed":
            success = False

    return {
        "status": "completed" if success else "failed",
        "story_id": story_id,
        "events": events
    }
