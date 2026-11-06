"""FastAPI Webhook Server & Interactive Switch Room Simulator for CampusHire Relay."""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, Response
from typing import List, Dict, Any, Optional
from campushire.models import SwitchMessage, PlacementCriteria, AuditReport
from campushire.switch_room import SwitchRoom
from campushire.storage.student_db import StudentRepository
from campushire.config import settings

app = FastAPI(
    title=settings.app_name,
    description="Multi-agent campus placement workflow relay connected to Switch room chat.",
    version="0.1.0",
)

# Shared in-memory Switch Room instance
repo = StudentRepository()
repo.load_synthetic_dataset()
room = SwitchRoom(student_repo=repo, room_name=settings.room_name, borderline_delta=settings.borderline_cgpa_delta)

DEFAULT_CRITERIA = PlacementCriteria(
    company_name="Stripe Technologies",
    role_title="Backend Platform Engineer",
    package_ctc="28 LPA",
    min_cgpa=8.0,
    max_active_backlogs=0,
    eligible_branches=["CSE", "IT", "ECE"],
    batch_year=2027,
    deadline="Nov 15, 2026, 6:00 PM",
    drive_date="Nov 18, 2026",
)


def _ensure_active_audit(target_room: SwitchRoom) -> AuditReport:
    """Ensure room has a verified active audit report, auto-running baseline audit if needed."""
    if target_room.active_report is None:
        if target_room.active_criteria is None:
            target_room.active_criteria = DEFAULT_CRITERIA
        candidates = target_room.repo.get_all_candidates()
        if not candidates:
            target_room.repo.load_synthetic_dataset()
            candidates = target_room.repo.get_all_candidates()
        target_room.active_report = target_room.eligibility_auditor.audit_candidates(
            candidates, target_room.active_criteria
        )
    return target_room.active_report


# Ensure initial baseline report is ready immediately on serverless start
_ensure_active_audit(room)


@app.get("/health")
def health() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "app": settings.app_name, "version": "0.1.0"}


@app.get("/api/candidates")
def list_candidates() -> List[Dict[str, Any]]:
    """Return all candidate records in the student database."""
    return [c.model_dump() for c in repo.get_all_candidates()]


@app.post("/api/switch/events")
def handle_switch_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle incoming Switch Room webhooks and return multi-agent responses."""
    try:
        msg = SwitchMessage(
            sender=event.get("sender", "Anonymous"),
            content=event.get("content", ""),
            room=event.get("room", room.room_name),
            mentions=event.get("mentions", []),
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


@app.get("/api/audit/report")
def get_audit_report() -> Dict[str, Any]:
    """Return the active eligibility audit report in JSON format."""
    report = _ensure_active_audit(room)
    return report.model_dump()


@app.get("/api/audit/export-csv")
def export_csv() -> Response:
    """Download verified candidate shortlist as a CSV file."""
    report = _ensure_active_audit(room)
    csv_data = room.eligibility_auditor.export_shortlist_csv(report)
    filename = f"shortlist_{report.criteria.company_name.lower().replace(' ', '_')}.csv"
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


# ---------------------------------------------------------------------------
# Additional Backend Extensions for CampusHire Relay
# ---------------------------------------------------------------------------

import os
import sys
import time

_SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from extract_criteria import extract_notice_text
from explainability import compute_counterfactual
from hall_pass_generator import compute_admit_token, verify_admit_token
from skill_matcher import compute_skill_overlap, BRANCH_CANONICAL_SKILLS, DEFAULT_ROLE_SKILLS
from laya_service import LayaDecisionEngine
from campushire.models import PlacementCriteria, CandidateAudit, AuditVerdict, AuditReport

_laya_engine = LayaDecisionEngine()


@app.post("/api/notice/ingest")
def ingest_recruiter_notice(event: Dict[str, Any]) -> Dict[str, Any]:
    """Screen recruiter notice via Laya System-1 reflex and extract criteria."""
    notice_text = event.get("notice_text", "")
    t0 = time.perf_counter()
    guard = _laya_engine.check_guardrails(notice_text)
    latency_ms = round((time.perf_counter() - t0) * 1000, 2)

    if not guard.get("safe", True):
        return {
            "safe": False,
            "latency_ms": latency_ms,
            "risk_score": guard.get("risk_score", 1.0),
            "flags": guard.get("flags", []),
            "criteria": {},
            "message": "Notice blocked by Laya Guardrail: potential prompt injection or adversarial content.",
        }

    parsed = extract_notice_text(notice_text)
    return {
        "safe": True,
        "latency_ms": latency_ms,
        "risk_score": guard.get("risk_score", 0.0),
        "flags": [],
        "requires_human_clarification": parsed.get("requires_human_clarification", False),
        "missing_or_ambiguous_fields": parsed.get("missing_or_ambiguous_fields", []),
        "criteria": parsed,
        "message": "Notice parsed successfully.",
    }


@app.post("/api/audit/execute")
def execute_audit(req: Dict[str, Any]) -> Dict[str, Any]:
    """Execute deterministic zero-LLM math audit against candidate records."""
    criteria = PlacementCriteria(
        company_name=req.get("company", "Northstar Technologies"),
        role_title=req.get("role", "Graduate Engineer Trainee"),
        package_ctc=req.get("package", "Standard"),
        min_cgpa=float(req.get("minimum_cgpa", 7.0)),
        max_active_backlogs=int(req.get("active_backlogs_allowed", 0)),
        eligible_branches=[b.upper() for b in req.get("eligible_branches", ["CSE", "IT"])],
        batch_year=int(req.get("graduation_year", 2027)),
        deadline="2026-11-30",
        drive_date="2026-12-05",
    )

    candidates = repo.get_all_candidates()
    eligible_candidates: List[Candidate] = []
    borderline_audits: List[CandidateAudit] = []
    ineligible_audits: List[CandidateAudit] = []

    for cand in candidates:
        audit = room.eligibility_auditor.audit_candidate(cand, criteria)
        if audit.verdict == AuditVerdict.ELIGIBLE:
            eligible_candidates.append(cand)
        elif audit.verdict == AuditVerdict.BORDERLINE:
            borderline_audits.append(audit)
        else:
            ineligible_audits.append(audit)

    report = AuditReport(
        criteria=criteria,
        total_evaluated=len(candidates),
        eligible_count=len(eligible_candidates),
        ineligible_count=len(ineligible_audits),
        borderline_count=len(borderline_audits),
        eligible_candidates=eligible_candidates,
        borderline_audits=borderline_audits,
        ineligible_audits=ineligible_audits,
    )

    room.active_criteria = criteria
    room.active_report = report

    leaf_hash = room.governance.ledger.append_event("AUDIT_COMPLETED", {
        "company": criteria.company_name,
        "total": len(candidates),
        "eligible": len(eligible_candidates),
        "ineligible": len(ineligible_audits),
        "borderline": len(borderline_audits),
    })

    return {
        "status": "success",
        "company": criteria.company_name,
        "total_evaluated": len(candidates),
        "eligible_count": len(eligible_candidates),
        "ineligible_count": len(ineligible_audits),
        "borderline_count": len(borderline_audits),
        "merkle_leaf": leaf_hash,
        "merkle_root": room.governance.ledger.compute_merkle_root(),
    }


@app.get("/api/prep-kit/{student_id}")
def get_student_prep_kit(student_id: str) -> Dict[str, Any]:
    """Retrieve personalized interview preparation kit for an eligible student."""
    norm_id = student_id.strip().upper()
    cand = repo.get_candidate_by_roll(norm_id)
    if not cand:
        raise HTTPException(status_code=404, detail=f"Candidate '{student_id}' not found.")

    company = room.active_criteria.company_name if room.active_criteria else "Northstar Technologies"
    role = room.active_criteria.role_title if room.active_criteria else "Graduate Engineer Trainee"

    return {
        "student_id": cand.roll_no,
        "name": cand.name,
        "branch": cand.branch,
        "company": company,
        "role": role,
        "roadmap": ["Day 1: Aptitude & Coding", "Day 3: Technical Fundamentals", "Day 5: STAR Behavioral Interview"],
        "star_prompts": [
            "Describe a complex software engineering problem you solved.",
            "How do you handle production incidents or high-stakes deadlines?"
        ]
    }


@app.get("/api/explainability/{student_id}")
def get_explainability(student_id: str) -> Dict[str, Any]:
    """Compute counterfactual explanation for student's audit decision."""
    norm_id = student_id.strip().upper()
    cand = repo.get_candidate_by_roll(norm_id)
    if not cand:
        raise HTTPException(status_code=404, detail=f"Student ID '{student_id}' not found.")

    criteria_dict = {
        "graduation_year": room.active_criteria.batch_year if room.active_criteria else 2027,
        "eligible_branches": room.active_criteria.eligible_branches if room.active_criteria else ["CSE", "IT"],
        "minimum_cgpa": room.active_criteria.min_cgpa if room.active_criteria else 7.0,
        "active_backlogs_allowed": room.active_criteria.max_active_backlogs if room.active_criteria else 0,
    }

    student_dict = {
        "student_id": cand.roll_no,
        "branch": cand.branch,
        "cgpa": cand.cgpa,
        "active_backlogs": cand.active_backlogs,
        "graduation_year": cand.batch_year,
    }

    return compute_counterfactual(student_dict, criteria_dict)


@app.get("/api/hall-pass/{student_id}")
def get_hall_pass(student_id: str) -> Dict[str, Any]:
    """Generate tamper-proof HMAC hall pass token."""
    norm_id = student_id.strip().upper()
    cand = repo.get_candidate_by_roll(norm_id)
    if not cand:
        raise HTTPException(status_code=404, detail=f"Candidate '{student_id}' not found.")

    company = room.active_criteria.company_name if room.active_criteria else "Northstar Technologies"
    seat_num = (abs(hash(norm_id)) % 60) + 1
    seat_no = f"Hall-A Seat A-{seat_num:02d}"
    token = compute_admit_token(norm_id, seat_no, company)

    return {
        "student_id": cand.roll_no,
        "name": cand.name,
        "company": company,
        "seat_no": seat_no,
        "admit_token": token,
        "status": "VERIFIED_ELIGIBLE",
    }


@app.post("/api/hall-pass/verify")
def verify_pass(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Invigilator token verification check."""
    student_id = payload.get("student_id", "")
    seat_no = payload.get("seat_no", "")
    token = payload.get("token", "")
    company = payload.get("company", "Northstar Technologies")
    valid = verify_admit_token(student_id, seat_no, token, company)
    return {
        "valid": valid,
        "student_id": student_id,
        "seat_no": seat_no,
        "company": company,
        "status": "AUTHENTICATED" if valid else "INVALID_TOKEN",
    }


@app.get("/api/governance/ledger")
def get_ledger() -> Dict[str, Any]:
    """Query tamper-evident Merkle ledger."""
    ledger = room.governance.ledger
    return {
        "total_events": len(ledger.history),
        "merkle_root": ledger.compute_merkle_root(),
        "leaves": ledger.leaves,
        "recent_history": ledger.history[-10:],
    }



@app.get("/", response_class=HTMLResponse)
def index() -> str:
    """Modern interactive Switch room simulator dashboard."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>CampusHire Relay - Switch Room Simulator</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    .message-enter { animation: fadeIn 0.3s ease-in-out; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }
  </style>
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen flex flex-col font-sans">
  <!-- Top Navigation -->
  <header class="bg-slate-800/80 backdrop-blur border-b border-slate-700 px-6 py-4 flex items-center justify-between">
    <div class="flex items-center space-x-3">
      <span class="text-2xl">⚡</span>
      <div>
        <h1 class="font-bold text-lg text-white">CampusHire Relay</h1>
        <p class="text-xs text-emerald-400">Flip the Switch Hackathon · Multi-Agent Room Integration</p>
      </div>
    </div>
    <div class="flex items-center space-x-4 text-xs">
      <span class="bg-slate-700 px-3 py-1.5 rounded-full border border-slate-600">Channel: <b class="text-indigo-400">#placement-drive-2027</b></span>
      <span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-900/60 text-emerald-400 border border-emerald-500/30">
        ● Switch Connected
      </span>
      <a href="/slides" target="_blank" class="bg-purple-600/30 border border-purple-500/50 hover:bg-purple-600 text-purple-200 hover:text-white font-medium px-3 py-1.5 rounded transition">📊 Pitch Deck</a>
      <a href="/api/audit/export-csv" class="bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-3 py-1.5 rounded transition">📥 Export CSV</a>
    </div>
  </header>

  <!-- Main Content Layout -->
  <div class="flex-1 grid grid-cols-1 lg:grid-cols-4 max-w-7xl w-full mx-auto p-4 gap-4">
    <!-- Left Panel: Presets & Controls -->
    <div class="lg:col-span-1 bg-slate-800/60 border border-slate-700 rounded-xl p-4 flex flex-col space-y-4">
      <h2 class="font-semibold text-sm text-slate-300 uppercase tracking-wider">Quick Actions</h2>
      <button onclick="loadSampleJD('stripe')" class="w-full text-left bg-slate-700 hover:bg-slate-600 p-3 rounded-lg text-xs transition border border-slate-600">
        <p class="font-bold text-white">1. Post Stripe JD (28 LPA)</p>
        <p class="text-slate-400 mt-1">@DriveCoordinator extraction & checklist</p>
      </button>
      <button onclick="triggerAudit()" class="w-full text-left bg-slate-700 hover:bg-slate-600 p-3 rounded-lg text-xs transition border border-slate-600">
        <p class="font-bold text-emerald-400">2. Run Student Audit</p>
        <p class="text-slate-400 mt-1">@EligibilityAuditor verification</p>
      </button>
      <button onclick="approveBorderline('23CS04')" class="w-full text-left bg-slate-700 hover:bg-slate-600 p-3 rounded-lg text-xs transition border border-slate-600">
        <p class="font-bold text-amber-400">3. Grant Borderline Waiver</p>
        <p class="text-slate-400 mt-1">Human-in-the-loop approval for 23CS04</p>
      </button>
      
      <div class="pt-4 border-t border-slate-700">
        <h3 class="text-xs font-semibold text-slate-400 uppercase">Room Teammates</h3>
        <div class="mt-2 space-y-2 text-xs">
          <div class="flex items-center space-x-2">
            <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
            <span><b>@DriveCoordinator</b> (AI Agent)</span>
          </div>
          <div class="flex items-center space-x-2">
            <span class="w-2 h-2 rounded-full bg-indigo-400"></span>
            <span><b>@EligibilityAuditor</b> (AI Agent)</span>
          </div>
          <div class="flex items-center space-x-2">
            <span class="w-2 h-2 rounded-full bg-amber-400"></span>
            <span><b>@PlacementOfficer</b> (Human)</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Center Panel: Switch Room Chat -->
    <div class="lg:col-span-3 bg-slate-800/90 border border-slate-700 rounded-xl flex flex-col h-[75vh]">
      <!-- Chat Messages Container -->
      <div id="chatBox" class="flex-1 overflow-y-auto p-4 space-y-4">
        <div class="text-center text-xs text-slate-500 my-2">── Room session started in #placement-drive-2027 ──</div>
      </div>

      <!-- Message Input Form -->
      <form onsubmit="sendMessage(event)" class="p-3 bg-slate-800 border-t border-slate-700 flex space-x-2">
        <input id="msgInput" type="text" placeholder="Type a message or mention @DriveCoordinator or @EligibilityAuditor..." 
          class="flex-1 bg-slate-900 border border-slate-600 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:border-indigo-500">
        <button type="submit" class="bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-5 py-2 rounded-lg text-sm transition">
          Send
        </button>
      </form>
    </div>
  </div>

  <script>
    const chatBox = document.getElementById('chatBox');
    const msgInput = document.getElementById('msgInput');

    function escapeHtml(str) {
      const p = document.createElement('p');
      p.textContent = str;
      return p.innerHTML;
    }

    function appendMessage(sender, content, isAgent = false) {
      const div = document.createElement('div');
      div.className = "flex flex-col space-y-1 message-enter " + (isAgent ? "items-start" : "items-end");
      
      let badgeClass = "bg-amber-600 text-amber-100";
      if (sender === "DriveCoordinator") badgeClass = "bg-emerald-600 text-emerald-100";
      if (sender === "EligibilityAuditor") badgeClass = "bg-indigo-600 text-indigo-100";

      div.innerHTML = `
        <div class="flex items-center space-x-2 text-xs text-slate-400 ${isAgent ? 'flex-row' : 'flex-row-reverse space-x-reverse'}">
          <span class="px-2 py-0.5 rounded font-semibold text-[10px] ${badgeClass}">${escapeHtml(sender)}</span>
          <span>Just now</span>
        </div>
        <div class="p-3.5 rounded-xl text-sm max-w-2xl whitespace-pre-wrap font-mono ${isAgent ? 'bg-slate-700/80 text-slate-100 border border-slate-600' : 'bg-indigo-600 text-white'}">
          ${escapeHtml(content)}
        </div>
      `;
      chatBox.appendChild(div);
      chatBox.scrollTop = chatBox.scrollHeight;
    }

    async function sendPayload(sender, content, mentions = []) {
      appendMessage(sender, content, sender !== "PlacementOfficer");
      try {
        const res = await fetch('/api/switch/events', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ sender, content, room: "#placement-drive-2027", mentions })
        });
        const data = await res.json();
        if (data.responses) {
          data.responses.forEach(r => appendMessage(r.sender, r.content, true));
        }
      } catch (e) {
        appendMessage("System", "Error communicating with Switch Relay: " + e.message, true);
      }
    }

    function sendMessage(e) {
      e.preventDefault();
      const val = msgInput.value.trim();
      if (!val) return;
      msgInput.value = '';
      const mentions = [];
      if (val.includes("@DriveCoordinator")) mentions.push("@DriveCoordinator");
      if (val.includes("@EligibilityAuditor")) mentions.push("@EligibilityAuditor");
      sendPayload("PlacementOfficer", val, mentions);
    }

    function loadSampleJD(type) {
      const jd = `@DriveCoordinator Campus Recruitment Drive 2027 - Stripe
Role: Backend Platform Engineer
Compensation: 28 LPA
Eligibility: Minimum CGPA 8.00, 0 active backlogs, Branches: CSE, IT, ECE
Passing Batch: 2027
Deadline: Nov 15, 2026, 6:00 PM
Assessment Date: Nov 18, 2026`;
      sendPayload("PlacementOfficer", jd, ["@DriveCoordinator"]);
    }

    function triggerAudit() {
      sendPayload("PlacementOfficer", "@EligibilityAuditor please execute eligibility audit on 2027 batch", ["@EligibilityAuditor"]);
    }

    function approveBorderline(roll) {
      sendPayload("PlacementOfficer", `@EligibilityAuditor approve waiver for ${roll} based on HOD recommendation`, ["@EligibilityAuditor"]);
    }
  </script>
</body>
</html>
"""


@app.get("/slides", response_class=HTMLResponse)
def serve_slides() -> str:
    """Serve interactive pitch deck slides."""
    slides_candidates = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "switch_agent", "static", "slides.html"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "slides.html"),
    ]
    for p in slides_candidates:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                return f.read()
    return "<h1>Pitch Deck Slides Not Found</h1>"

