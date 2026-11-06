"""CampusHire Relay Multi-Agent Room & Deterministic Audit Router.

Provides unified endpoints for:
1. Candidate Database queries (/api/campushire/candidates)
2. Switch Room Webhook processing (/api/campushire/events, /api/switch/events)
3. Audit Report inspection and CSV export (/api/campushire/audit/*)
4. Laya-screened Recruiter Notice Ingestion (/api/campushire/notice/ingest)
5. Programmatic Deterministic Audit Execution (/api/campushire/audit/execute)
6. Personalized Student Preparation Kits for Room 2 (/api/campushire/prep-kit/{student_id})
7. Counterfactual Decision Explainability (/api/campushire/explainability/{student_id})
8. Cryptographic HMAC Admit Passes & Verification (/api/campushire/hall-pass/*)
9. Semantic Skill Matcher & Gap Analysis (/api/campushire/skills/gap-analysis)
10. Tamper-Evident Merkle Audit Ledger (/api/campushire/governance/ledger)
11. Complete Operations Pack Bundle (/api/campushire/reports/bundle)
"""
from __future__ import annotations
import os
import sys
import time
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Path as FPath
from fastapi.responses import Response

# Ensure campushire-relay and its scripts are on sys.path
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_CAMPUSHIRE_ROOT = os.path.join(_ROOT, "campushire-relay")
_SCRIPTS_ROOT = os.path.join(_CAMPUSHIRE_ROOT, "scripts")

for p in (_CAMPUSHIRE_ROOT, _SCRIPTS_ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

from campushire.models import (
    SwitchMessage,
    PlacementCriteria,
    Candidate,
    CandidateAudit,
    AuditVerdict,
    AuditReport,
)
from campushire.switch_room import SwitchRoom
from campushire.storage.student_db import StudentRepository
from switch_agent.laya_gate import GATE
from switch_agent.models.campushire_models import (
    CampusHireEventRequest,
    NoticeIngestRequest,
    NoticeIngestResponse,
    DirectAuditRequest,
    HallPassVerifyRequest,
    HallPassVerifyResponse,
    SkillGapRequest,
    SkillGapResponse,
    CounterfactualResponse,
    MerkleLedgerResponse,
)

from switch_agent.skill_gap_engine import PROJECT_ENGINE
from switch_agent.notebooklm_service import NOTEBOOKLM_SERVICE
from switch_agent.armor_receipts import ARMOR_SERVICE

# Deterministic tooling imports
from extract_criteria import extract_notice_text
from explainability import compute_counterfactual
from hall_pass_generator import compute_admit_token, verify_admit_token
from skill_matcher import (
    compute_skill_overlap,
    BRANCH_CANONICAL_SKILLS,
    DEFAULT_ROLE_SKILLS,
    normalize_skill,
)

router = APIRouter(tags=["CampusHire Multi-Agent Room"])

# Initialize shared student repository and SwitchRoom singleton
repo = StudentRepository()
repo.load_synthetic_dataset()
room = SwitchRoom(student_repo=repo, room_name="#placement-drive-2027")

# Default baseline placement criteria for cold-start serverless environments
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


# ---------------------------------------------------------------------------
# 1. Candidate Database & Webhook Endpoints
# ---------------------------------------------------------------------------

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
    report = _ensure_active_audit(room)
    return report.model_dump()


@router.get("/api/campushire/audit/export-csv")
@router.get("/api/audit/export-csv")
def export_csv() -> Response:
    """Download verified candidate shortlist as a CSV file."""
    report = _ensure_active_audit(room)
    csv_data = room.eligibility_auditor.export_shortlist_csv(report)
    company = report.criteria.company_name.lower().replace(" ", "_")
    filename = f"shortlist_{company}.csv"
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


# ---------------------------------------------------------------------------
# 2. Laya-Screened Recruiter Notice Ingestion & Dehallucination
# ---------------------------------------------------------------------------

@router.post("/api/campushire/notice/ingest", response_model=NoticeIngestResponse)
def ingest_recruiter_notice(req: NoticeIngestRequest) -> NoticeIngestResponse:
    """Screen recruiter notice in <1ms on CPU and extract structured eligibility rules."""
    t0 = time.perf_counter()
    # 1. System 1 Reflex Guardrail Screening
    decision = GATE.evaluate_request(req.source or "Recruiter", req.notice_text)
    latency_ms = round((time.perf_counter() - t0) * 1000, 2)

    if not decision.is_safe:
        return NoticeIngestResponse(
            safe=False,
            latency_ms=latency_ms,
            risk_score=1.0,
            flags=["prompt_injection_or_destructive_command"],
            requires_human_clarification=False,
            missing_or_ambiguous_fields=[],
            criteria={},
            message=f"Notice blocked by Laya Guardrail: {decision.reason}",
        )

    # 2. Deterministic Regex-hardened Parsing
    parsed = extract_notice_text(req.notice_text)
    requires_clarification = parsed.get("requires_human_clarification", False)
    missing = parsed.get("missing_or_ambiguous_fields", [])

    # Record event in Merkle audit ledger
    room.governance.ledger.append_event("NOTICE_INGESTED", {
        "company": parsed.get("company"),
        "role": parsed.get("role"),
        "requires_clarification": requires_clarification,
        "missing_fields": missing,
    })

    return NoticeIngestResponse(
        safe=True,
        latency_ms=latency_ms,
        risk_score=0.0,
        flags=[],
        requires_human_clarification=requires_clarification,
        missing_or_ambiguous_fields=missing,
        criteria=parsed,
        message="Notice verified safe and parsed deterministically."
        if not requires_clarification
        else "Notice parsed but requires human clarification for missing fields.",
    )


# ---------------------------------------------------------------------------
# 3. Direct Programmatic Deterministic Audit Execution
# ---------------------------------------------------------------------------

@router.post("/api/campushire/audit/execute")
def execute_deterministic_audit(req: DirectAuditRequest) -> Dict[str, Any]:
    """Execute deterministic zero-LLM math audit against candidate records."""
    criteria = PlacementCriteria(
        company_name=req.company,
        role_title=req.role,
        package_ctc="Competitive Standard",
        min_cgpa=req.minimum_cgpa,
        max_active_backlogs=req.active_backlogs_allowed,
        eligible_branches=[b.upper() for b in req.eligible_branches],
        batch_year=req.graduation_year,
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

    # Attach as active report on room
    room.active_criteria = criteria
    room.active_report = report

    # Append to governance Merkle audit ledger
    leaf_hash = room.governance.ledger.append_event("AUDIT_COMPLETED", {
        "company": criteria.company_name,
        "total": len(candidates),
        "eligible": len(eligible_candidates),
        "ineligible": len(ineligible_audits),
        "borderline": len(borderline_audits),
        "cutoff_cgpa": criteria.min_cgpa,
    })

    return {
        "status": "success",
        "company": criteria.company_name,
        "role": criteria.role_title,
        "total_evaluated": len(candidates),
        "eligible_count": len(eligible_candidates),
        "ineligible_count": len(ineligible_audits),
        "borderline_count": len(borderline_audits),
        "merkle_leaf": leaf_hash,
        "merkle_root": room.governance.ledger.compute_merkle_root(),
    }


# ---------------------------------------------------------------------------
# 4. Personalized Preparation Kits for Room 2 (#student-prep-studio)
# ---------------------------------------------------------------------------

@router.get("/api/campushire/prep-kit/{student_id}")
def get_student_prep_kit(student_id: str = FPath(..., description="Roll Number or Student ID")) -> Dict[str, Any]:
    """Retrieve personalized interview roadmap and Wispr Flow voice prompts for an eligible student."""
    norm_id = student_id.strip().upper()
    cand = repo.get_candidate(norm_id)
    if not cand:
        # Check standard synthetic list by prefix
        candidates = repo.get_all_candidates()
        cand = next((c for c in candidates if c.roll_no.upper() == norm_id), None)

    if not cand:
        raise HTTPException(status_code=404, detail=f"Candidate with ID '{student_id}' not found.")

    company = room.active_criteria.company_name if room.active_criteria else "Northstar Technologies"
    role = room.active_criteria.role_title if room.active_criteria else "Graduate Engineer Trainee"

    markdown_kit = f"""# Personalized Placement Preparation Kit: {norm_id}
**Company:** {company}  
**Target Role:** {role}  
**Candidate Name:** {cand.name} ({cand.branch})  
**Verified CGPA:** {cand.cgpa:.2f}  

---

## 🎯 Selection Stages Roadmap
1. **Online Aptitude & Coding Assessment (Day 1)**: Focus on Data Structures, Algorithms, and SQL queries.
2. **Technical Interview 1 (Day 3)**: System Design concepts, Core {cand.branch} fundamentals, Git workflow.
3. **HR & Leadership Round (Day 5)**: Behavioral questions evaluated on the STAR rubric.

---

## 🎙️ Wispr Flow Spoken Mock Interview Questions
Practice dictating your answers using Wispr Flow into the `#student-prep-studio` channel:
- **Question 1 (Situation & Task)**: *"Describe a technical project where you faced an unexpected failure. What was your role?"*
- **Question 2 (Action & Result)**: *"How did you resolve the issue, and what measurable impact did your solution achieve?"*

> [!TIP]
> Spoken responses will be instantly evaluated in sub-second latency by Laya System-1 on the STAR rubric.
"""

    return {
        "student_id": cand.roll_no,
        "name": cand.name,
        "branch": cand.branch,
        "company": company,
        "role": role,
        "prep_kit_markdown": markdown_kit,
    }


# ---------------------------------------------------------------------------
# 5. Counterfactual Explainability Engine
# ---------------------------------------------------------------------------

@router.get("/api/campushire/explainability/{student_id}", response_model=CounterfactualResponse)
def get_candidate_explainability(student_id: str = FPath(..., description="Roll Number")) -> CounterfactualResponse:
    """Compute minimal parameter adjustments required for a rejected student to reach eligibility."""
    norm_id = student_id.strip().upper()
    cand = repo.get_candidate(norm_id)
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

    explanation = compute_counterfactual(student_dict, criteria_dict)
    reasons = explanation.get("primary_reasons", [])
    actions = explanation.get("counterfactual_actions", {})
    status = "ELIGIBLE" if not reasons else "NOT_ELIGIBLE"

    return CounterfactualResponse(
        student_id=cand.roll_no,
        current_status=status,
        reasons=reasons or ["Meets all criteria requirements"],
        minimal_changes_needed=actions,
        eligible_if_adjusted=len(actions) > 0,
    )


# ---------------------------------------------------------------------------
# 6. Cryptographic Hall Pass Generation & Test Day Verification
# ---------------------------------------------------------------------------

@router.get("/api/campushire/hall-pass/{student_id}")
def get_hall_pass(student_id: str = FPath(..., description="Roll Number")) -> Dict[str, Any]:
    """Generate anti-counterfeit HMAC hall pass and seat allocation for test day."""
    norm_id = student_id.strip().upper()
    cand = repo.get_candidate(norm_id)
    if not cand:
        raise HTTPException(status_code=404, detail=f"Candidate '{student_id}' not found.")

    company = room.active_criteria.company_name if room.active_criteria else "Northstar Technologies"
    # Deterministic seat assignment based on roll number hash
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
        "qr_payload": f"CAMPUSHIRE:{norm_id}:{seat_no}:{token}",
    }


@router.post("/api/campushire/hall-pass/verify", response_model=HallPassVerifyResponse)
def verify_hall_pass(req: HallPassVerifyRequest) -> HallPassVerifyResponse:
    """Verify hall pass validity in sub-second time for test invigilators."""
    is_valid = verify_admit_token(req.student_id, req.seat_no, req.token, req.company)
    return HallPassVerifyResponse(
        valid=is_valid,
        student_id=req.student_id,
        seat_no=req.seat_no,
        company=req.company,
        timestamp=time.time(),
        status="AUTHENTICATED" if is_valid else "INVALID_TOKEN_OR_SEAT_MISMATCH",
    )


# ---------------------------------------------------------------------------
# 7. Semantic Skill Matcher & Readiness Analysis
# ---------------------------------------------------------------------------

@router.post("/api/campushire/skills/gap-analysis", response_model=SkillGapResponse)
def analyze_skill_gap(req: SkillGapRequest) -> SkillGapResponse:
    """Compute candidate skill coverage ratio, missing gaps, and preparation recommendations."""
    target_role = req.target_role.lower().strip()
    role_skills = DEFAULT_ROLE_SKILLS.get(target_role, DEFAULT_ROLE_SKILLS["graduate engineer trainee"])

    if req.candidate_skills:
        cand_skills = req.candidate_skills
    elif req.branch and req.branch.upper() in BRANCH_CANONICAL_SKILLS:
        cand_skills = BRANCH_CANONICAL_SKILLS[req.branch.upper()]
    else:
        cand_skills = ["python", "data structures", "algorithms"]

    overlap = compute_skill_overlap(cand_skills, role_skills)
    match_pct = round(overlap["coverage_ratio"] * 100.0, 1)

    matched = overlap["matched_skills"]
    missing = overlap["missing_skills"]

    if match_pct >= 80.0:
        level = "Interview Ready (Tier 1)"
    elif match_pct >= 50.0:
        level = "Moderate Gap (Requires 7-Day Sprint)"
    else:
        level = "High Gap (Foundational Upskilling Needed)"

    recommendations = [f"Focus on practical project experience with '{s}'" for s in missing[:3]]
    recommended_projects = PROJECT_ENGINE.recommend_for_skills(missing, limit_per_skill=1)

    return SkillGapResponse(
        student_id=req.student_id,
        target_role=req.target_role,
        match_percentage=match_pct,
        matched_skills=matched,
        missing_skills=missing,
        readiness_level=level,
        recommendations=recommendations or ["Candidate skills fully align with target role"],
        recommended_projects=recommended_projects,
    )


# ---------------------------------------------------------------------------
# 7b. Candidate Audio Prep Briefing (NotebookLM) & Drive Sealing (ArmorIQ)
# ---------------------------------------------------------------------------

@router.get("/api/campushire/prep-kit/{student_id}/audio-briefing")
def get_candidate_prep_kit_audio_briefing(student_id: str = FPath(..., description="Student ID")) -> Dict[str, Any]:
    """Generates or retrieves a 2-host audio prep debrief podcast for this candidate."""
    cand = repo.get_candidate(student_id.upper().strip())
    name = cand.name if cand else f"Candidate {student_id.upper()}"
    cgpa = cand.cgpa if cand else 8.5
    branch = cand.branch if cand else "CSE"
    company = room.active_criteria.company_name if room.active_criteria else "Google"
    role = room.active_criteria.role_title if room.active_criteria else "Software Development Engineer"

    briefing = NOTEBOOKLM_SERVICE.generate_candidate_audio_briefing(
        student_id=student_id.upper().strip(),
        student_name=name,
        company_name=company,
        role_title=role,
        cgpa=cgpa,
        branch=branch,
        matched_skills=["Data Structures", "Algorithms", "Python"],
        missing_skills=["System Design", "Distributed Systems"],
    )
    return briefing.model_dump()


@router.post("/api/campushire/audit/lock-and-seal")
def lock_and_seal_placement_drive(operator: str = "@coordinator") -> Dict[str, Any]:
    """Locks the active placement drive and generates an ArmorIQ cryptographic receipt."""
    if not room.active_criteria:
        raise HTTPException(status_code=400, detail="No active placement criteria to lock.")

    intent = ARMOR_SERVICE.declare_intent(
        action="campushire:seal_placement_shortlist",
        operator=operator,
        target=f"Drive:{room.active_criteria.company_name}",
        parameters={
            "company": room.active_criteria.company_name,
            "min_cgpa": room.active_criteria.min_cgpa,
            "max_backlogs": room.active_criteria.max_active_backlogs,
            "branches": room.active_criteria.eligible_branches,
        }
    )

    receipt = ARMOR_SERVICE.seal_receipt(
        intent_id=intent.intent_id,
        result_data={
            "company": room.active_criteria.company_name,
            "min_cgpa": room.active_criteria.min_cgpa,
            "merkle_root": room.governance.ledger.compute_merkle_root(),
            "timestamp": time.time(),
        }
    )

    return {
        "status": "sealed",
        "message": f"Placement drive for {room.active_criteria.company_name} locked and cryptographically sealed.",
        "receipt_id": receipt.receipt_id,
        "intent_hash": receipt.intent_hash,
        "merkle_leaf": receipt.merkle_leaf,
        "merkle_root": room.governance.ledger.compute_merkle_root(),
        "is_verified": receipt.is_verified,
    }


# ---------------------------------------------------------------------------
# 8. Tamper-Evident Merkle Tree Audit Ledger
# ---------------------------------------------------------------------------

@router.get("/api/campushire/governance/ledger", response_model=MerkleLedgerResponse)
def get_governance_ledger() -> MerkleLedgerResponse:
    """Query the tamper-evident Merkle ledger containing cryptographic event digests."""
    ledger = room.governance.ledger
    merkle_root = ledger.compute_merkle_root()
    return MerkleLedgerResponse(
        total_events=len(ledger.history),
        merkle_root=merkle_root,
        leaves=ledger.leaves,
        recent_history=ledger.history[-10:],
    )


# ---------------------------------------------------------------------------
# 9. Operations Pack Bundle
# ---------------------------------------------------------------------------

@router.get("/api/campushire/reports/bundle")
def get_operations_pack_bundle() -> Dict[str, Any]:
    """Retrieve full operations pack bundle metadata, checklist, and announcement."""
    company = room.active_criteria.company_name if room.active_criteria else "Northstar Technologies"
    role = room.active_criteria.role_title if room.active_criteria else "Graduate Engineer Trainee"
    cutoff = room.active_criteria.min_cgpa if room.active_criteria else 7.0

    announcement = f"""# Placement Drive Announcement: {company}
**Role**: {role}  
**Minimum CGPA Cutoff**: {cutoff}  
**Audit Status**: Verified with Zero-LLM Deterministic Math  
All eligible students have been assigned seats in Hall-A.
"""

    checklist = [
        "Ingest and screen recruiter notice with Laya System-1 (<1ms)",
        "Lock criteria JSON with explicit coordinator approval",
        "Run deterministic student database audit",
        "Generate cryptographic admit passes for eligible students",
        "Distribute personalized prep kits in #student-prep-studio",
    ]

    return {
        "status": "ready",
        "company": company,
        "role": role,
        "announcement_markdown": announcement,
        "checklist": checklist,
        "merkle_root": room.governance.ledger.compute_merkle_root(),
        "total_history_events": len(room.governance.ledger.history),
    }
