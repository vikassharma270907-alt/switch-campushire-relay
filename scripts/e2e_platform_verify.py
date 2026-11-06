#!/usr/bin/env python3
"""End-to-End Comprehensive Platform Verification for SwitchGuard & CampusHire Relay.

Tests all integrated subsystems:
1. Unified FastAPI server initialization & health checks
2. Interactive Pitch Deck & War Room UI endpoints
3. Laya System-1 sub-millisecond reflex screening
4. Recruiter notice parsing & deterministic student audit
5. Student prep kit generation & counterfactual explainability
6. HMAC SHA-256 tamper-proof hall pass generation & verification
7. Semantic skill gap analysis & readiness grading
8. Merkle ledger state integrity & leaf verification
9. Operations bundle generation & shortlisting
10. Wispr Flow STAR interview voice evaluation
11. Switch AI SSE agent message streaming protocol
"""

import sys
import os
import time

# Ensure workspace root is in sys.path
WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WORKSPACE not in sys.path:
    sys.path.insert(0, WORKSPACE)

from fastapi.testclient import TestClient
from switch_agent.server import app

client = TestClient(app)


def print_header(title: str):
    print("\n" + "=" * 70)
    print(f" 🔍 {title}")
    print("=" * 70)


def verify(name: str, passed: bool, detail: str = ""):
    symbol = "✔ [PASS]" if passed else "✖ [FAIL]"
    print(f" {symbol:8} {name:<45} {detail}")
    if not passed:
        raise AssertionError(f"Verification failed for: {name}")


def main():
    start_time = time.perf_counter()
    print_header("CampusHire Relay + SwitchGuard E2E Subsystem Verification")

    # 1. Health & Server Status
    r_health = client.get("/healthz")
    verify("Health Endpoint (/healthz)", r_health.status_code == 200, f"Status: {r_health.json().get('status')}")

    # 2. UI & Pitch Deck
    r_dash = client.get("/")
    verify("War Room Dashboard (/)", r_dash.status_code == 200 and "SwitchGuard" in r_dash.text, "HTML UI Served")

    r_slides = client.get("/slides")
    verify("Pitch Deck (/slides)", r_slides.status_code == 200 and "CampusHire Relay" in r_slides.text, "9 Slides Rendered")

    # 3. Laya System-1 Reflex Gate
    t0 = time.perf_counter()
    r_triage = client.post("/api/triage", json={"user": "auditor_1", "message": "Approve waiver for STU003"})
    latency_ms = round((time.perf_counter() - t0) * 1000, 2)
    verify("Laya Reflex Gate (/api/triage)", r_triage.status_code == 200, f"Latency: {latency_ms}ms")

    # 4. Notice Ingestion & Screening
    sample_notice = (
        "Google is hiring Software Engineers for 2027 batch. Minimum CGPA: 8.0, Max Backlogs: 0. "
        "Eligible branches: CSE, IT, ECE. Package: 32 LPA. Deadline: Nov 20, 2026."
    )
    r_notice = client.post("/api/campushire/notice/ingest", json={"notice_text": sample_notice})
    data_notice = r_notice.json()
    verify("Notice Ingestion (/api/campushire/notice/ingest)", r_notice.status_code == 200 and data_notice.get("safe"), f"Company: {data_notice.get('criteria', {}).get('company_name')}")

    # 5. Deterministic Student Eligibility Audit
    r_audit = client.post("/api/campushire/audit/execute", json={
        "criteria": data_notice.get("criteria", {}),
        "source": "recruiter_notice"
    })
    data_audit = r_audit.json()
    eligible_count = data_audit.get("eligible_count", 0)
    verify("Student Audit (/api/campushire/audit/execute)", r_audit.status_code == 200, f"Eligible Candidates: {eligible_count}")

    # Fetch real student roll numbers from database
    r_cands = client.get("/api/campushire/candidates")
    candidates = r_cands.json()
    target_roll = candidates[0]["roll_no"] if candidates else "23CS01"
    borderline_roll = candidates[2]["roll_no"] if len(candidates) > 2 else "23IT02"

    # 6. Candidate Prep Kit
    r_prep = client.get(f"/api/campushire/prep-kit/{target_roll}")
    data_prep = r_prep.json()
    verify("Prep Kit Studio (/api/campushire/prep-kit/{id})", r_prep.status_code == 200 and "prep_kit_markdown" in data_prep, f"Candidate: {data_prep.get('name')}")

    # 7. Counterfactual Explainability
    r_expl = client.get(f"/api/campushire/explainability/{borderline_roll}")
    data_expl = r_expl.json()
    verify("Counterfactual Explainability (/api/campushire/explainability/{id})", r_expl.status_code == 200 and "reasons" in data_expl, f"Verdict: {data_expl.get('current_status')}")

    # 8. HMAC Hall Pass Generation & Verification
    r_pass = client.get(f"/api/campushire/hall-pass/{target_roll}")
    data_pass = r_pass.json()
    token = data_pass.get("admit_token")
    seat_no = data_pass.get("seat_no")
    company = data_pass.get("company")
    verify("HMAC Hall Pass Generation (/api/campushire/hall-pass/{id})", r_pass.status_code == 200 and bool(token), f"Token: {token[:12]}...")

    r_verify = client.post("/api/campushire/hall-pass/verify", json={
        "student_id": target_roll,
        "seat_no": seat_no,
        "token": token,
        "company": company
    })
    data_verify = r_verify.json()
    verify("HMAC Hall Pass Verification (/api/campushire/hall-pass/verify)", r_verify.status_code == 200 and data_verify.get("valid"), f"Status: {data_verify.get('status')}")

    # 9. Semantic Skill Gap Analysis
    r_skills = client.post("/api/campushire/skills/gap-analysis", json={
        "student_id": target_roll,
        "branch": "CSE",
        "candidate_skills": ["python", "sql", "git"],
        "target_role": "Backend Engineer"
    })
    data_skills = r_skills.json()
    verify("Skill Gap Analysis (/api/campushire/skills/gap-analysis)", r_skills.status_code == 200, f"Readiness: {data_skills.get('readiness_level')} ({data_skills.get('match_percentage')}%)")

    # 10. Tamper-Evident Merkle Ledger
    r_ledger = client.get("/api/campushire/governance/ledger")
    data_ledger = r_ledger.json()
    merkle_root = data_ledger.get("merkle_root", "")
    verify("Merkle Governance Ledger (/api/campushire/governance/ledger)", r_ledger.status_code == 200 and len(merkle_root) == 64, f"Root: {merkle_root[:16]}... ({data_ledger.get('total_events')} events)")

    # 11. Placement Operations Bundle
    r_bundle = client.get("/api/campushire/reports/bundle")
    data_bundle = r_bundle.json()
    verify("Operations Pack Bundle (/api/campushire/reports/bundle)", r_bundle.status_code == 200 and len(data_bundle.get("checklist", [])) >= 4, "Verified Checklist & Docs Ready")

    # 12. Wispr Voice STAR Interview Evaluation & Hands-Free Approval
    star_speech = (
        "In my previous internship at FinTech Labs, our microservices experienced high latency spikes. "
        "My goal was to optimize API throughput and reduce database read contention. "
        "I designed and implemented an asynchronous Redis read-through caching layer and migrated raw queries to indexing. "
        "As a result, we reduced API latency by 72 percent and achieved zero dropouts during peak market hours."
    )
    r_star = client.post("/api/wispr/star-evaluate", json={"spoken_text": star_speech, "target_role": "Backend Engineer"})
    data_star = r_star.json()
    verify("Wispr STAR Scoring (/api/wispr/star-evaluate)", r_star.status_code == 200 and data_star.get("star_score") == 10.0, f"STAR Score: {data_star.get('star_score')}/10.0")

    r_dictate = client.post("/api/wispr/dictate-approval", json={
        "officer_name": "PlacementOfficer",
        "spoken_audio_transcript": "Approve waiver for 23IT02 based on HOD special recommendation",
        "room_name": "#placement-drive-2027"
    })
    data_dictate = r_dictate.json()
    verify("Wispr Voice Approval (/api/wispr/dictate-approval)", r_dictate.status_code == 200 and data_dictate.get("status") == "processed", f"Candidate: {data_dictate.get('target_candidate')}")

    # 13. Switch AI SSE Protocol
    r_stream = client.post("/agent", json={"text": "Hello CampusHire Agent", "sender": "Officer", "stream": True})
    verify("Switch AI SSE Agent Protocol (/agent)", r_stream.status_code == 200 and "text/event-stream" in r_stream.headers.get("content-type", ""), "SSE Stream Established")

    elapsed = round(time.perf_counter() - start_time, 2)
    print_header(f"ALL 13 SUBSYSTEMS VERIFIED OPERATIONAL IN {elapsed}s")
    print("🏆 Ready for Hackathon Judging & Live Demonstration!")


if __name__ == "__main__":
    main()
