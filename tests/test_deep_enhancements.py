"""Comprehensive verification test suite for deep research, skills, and plugin enhancements.

Tests:
1. Google NotebookLM Audio Briefing Service & Endpoints
2. Strix Autonomous 25-Vector Adversarial Red-Team Battery
3. ArmorIQ Intent-First Governance & Cryptographic Receipts
4. 500+ AI Projects Skill-Gap Pathfinding Engine
5. CampusHire Integrated Prep-Kit Audio & Drive Sealing
6. Laya System-1 Sub-Millisecond Reflex Intent Classification
"""
from __future__ import annotations
import pytest
from fastapi.testclient import TestClient

from switch_agent.server import app
from switch_agent.laya_gate import GATE
from switch_agent.notebooklm_service import NOTEBOOKLM_SERVICE
from switch_agent.skill_gap_engine import PROJECT_ENGINE
from switch_agent.armor_receipts import ARMOR_SERVICE

client = TestClient(app)


# ---------------------------------------------------------------------------
# 1. Google NotebookLM Grounding & Audio Overview Briefing Tests
# ---------------------------------------------------------------------------

def test_notebooklm_service_generation():
    """Verify NotebookLM service generates a complete 2-host audio briefing."""
    # Arrange & Act
    briefing = NOTEBOOKLM_SERVICE.generate_candidate_audio_briefing(
        student_id="STU_TEST_01",
        student_name="Test Candidate",
        company_name="Microsoft",
        role_title="Azure Cloud Engineer",
        cgpa=9.1,
        branch="Computer Science",
        matched_skills=["Python", "Cloud Architecture", "Docker"],
        missing_skills=["Kubernetes", "Helm"],
    )

    # Assert
    assert briefing.briefing_id.startswith("NLM-STU_TEST_01-")
    assert len(briefing.hosts) == 2
    assert briefing.hosts[0].name == "Alex"
    assert briefing.hosts[1].name == "Priya"
    assert len(briefing.dialogue) >= 4
    assert len(briefing.citations) >= 2
    assert "Microsoft" in briefing.dialogue[0].text
    assert briefing.status == "completed"


def test_notebooklm_status_endpoint():
    """Verify NotebookLM health and capabilities endpoint."""
    # Act
    res = client.get("/api/notebooklm/status")

    # Assert
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "active"
    assert "Google NotebookLM" in data["engine"]
    assert len(data["capabilities"]) >= 3


def test_notebooklm_generate_and_get_endpoint():
    """Verify generating and retrieving student audio briefings via REST API."""
    # Act: Generate
    gen_res = client.post("/api/notebooklm/briefing/generate", json={
        "student_id": "STU777",
        "student_name": "Rohan Verma",
        "company_name": "Amazon",
        "role_title": "SDE-1",
        "cgpa": 8.7,
        "branch": "CSE",
        "matched_skills": ["Java", "OOP", "Data Structures"],
        "missing_skills": ["DynamoDB", "AWS CDK"],
    })
    assert gen_res.status_code == 200
    gen_data = gen_res.json()
    assert gen_data["student_id"] == "STU777"
    assert gen_data["company_name"] == "Amazon"

    # Act: Retrieve by student ID
    get_res = client.get("/api/notebooklm/briefing/STU777")
    assert get_res.status_code == 200
    get_data = get_res.json()
    assert get_data["student_id"] == "STU777"


def test_notebooklm_audio_stream_endpoint():
    """Verify audio streaming endpoint delivers playable WAV audio bytes."""
    # Act
    res = client.get("/api/notebooklm/stream/NLM-STU001.mp3")

    # Assert
    assert res.status_code == 200
    assert "audio/wav" in res.headers["content-type"]
    assert res.content.startswith(b"RIFF")
    assert b"WAVE" in res.content[:16]


# ---------------------------------------------------------------------------
# 2. 500+ AI Projects Skill-Gap Engine Tests
# ---------------------------------------------------------------------------

def test_skill_gap_project_engine():
    """Verify skill gap engine parses catalog and recommends relevant projects."""
    # Arrange
    missing = ["nlp", "computer vision", "time series"]

    # Act
    recs = PROJECT_ENGINE.recommend_for_skills(missing, limit_per_skill=1)

    # Assert
    assert len(recs) == 3
    skills_addressed = {r["skill_addressed"] for r in recs}
    assert skills_addressed == set(missing)
    for r in recs:
        assert r["project_url"].startswith("http")
        assert "3-Day Sprint" in r["estimated_effort"]
        assert len(r["action_item"]) > 10


def test_campushire_skills_gap_with_project_recommendations():
    """Verify /api/campushire/skills/gap-analysis returns recommended open source projects."""
    # Act
    res = client.post("/api/campushire/skills/gap-analysis", json={
        "student_id": "23CS01",
        "branch": "CSE",
        "candidate_skills": ["python", "sql"],
        "target_role": "graduate engineer trainee",
    })

    # Assert
    assert res.status_code == 200
    data = res.json()
    assert "recommended_projects" in data
    assert isinstance(data["recommended_projects"], list)
    if data["missing_skills"]:
        assert len(data["recommended_projects"]) > 0
        first_proj = data["recommended_projects"][0]
        assert "project_title" in first_proj
        assert "project_url" in first_proj


def test_campushire_prep_kit_audio_briefing_endpoint():
    """Verify student prep kit audio briefing integration."""
    # Act
    res = client.get("/api/campushire/prep-kit/23CS01/audio-briefing")

    # Assert
    assert res.status_code == 200
    data = res.json()
    assert "briefing_id" in data
    assert data["student_id"] == "23CS01"
    assert len(data["hosts"]) == 2
    assert "audio_stream_url" in data


# ---------------------------------------------------------------------------
# 3. ArmorIQ Intent-First Governance & Cryptographic Receipts Tests
# ---------------------------------------------------------------------------

def test_armoriq_receipt_service_lifecycle():
    """Verify declaring intent, canonical SHA-256 sealing, and Merkle leaf verification."""
    # Arrange & Act: Declare intent
    intent = ARMOR_SERVICE.declare_intent(
        action="test:execute_placement_audit",
        operator="@coordinator",
        target="PlacementDrive:Google",
        parameters={"cutoff": 8.0, "branches": ["CSE"]},
    )
    assert intent.intent_id.startswith("intent-")
    assert len(intent.intent_hash) == 64  # SHA-256 hex length

    # Act: Seal receipt
    receipt = ARMOR_SERVICE.seal_receipt(
        intent_id=intent.intent_id,
        result_data={"eligible_count": 5, "status": "APPROVED"},
    )
    assert receipt.receipt_id.startswith("rcpt-")
    assert receipt.intent_hash == intent.intent_hash
    assert len(receipt.merkle_leaf) == 64

    # Act: Verify receipt
    verification = ARMOR_SERVICE.verify_receipt(receipt.receipt_id)
    assert verification["verified"] is True
    assert verification["status"] == "VALID_AND_TAMPER_FREE"

    # Act: Verify by Merkle leaf
    leaf_verification = ARMOR_SERVICE.verify_receipt(receipt.merkle_leaf)
    assert leaf_verification["verified"] is True


def test_armoriq_receipt_endpoints():
    """Verify REST endpoints for declaring, sealing, listing, and verifying receipts."""
    # 1. Declare
    dec_res = client.post("/api/security/receipts/declare", json={
        "action": "admin:verify_test_suite",
        "operator": "CI_Runner",
        "target": "PytestVerification",
        "parameters": {"suite": "full"},
    })
    assert dec_res.status_code == 200
    intent_data = dec_res.json()["intent"]
    intent_id = intent_data["intent_id"]

    # 2. Seal
    seal_res = client.post("/api/security/receipts/seal", json={
        "intent_id": intent_id,
        "result_data": {"passed": 64, "failed": 0},
    })
    assert seal_res.status_code == 200
    receipt_data = seal_res.json()["receipt"]
    receipt_id = receipt_data["receipt_id"]

    # 3. List
    list_res = client.get("/api/security/receipts")
    assert list_res.status_code == 200
    assert any(r["receipt_id"] == receipt_id for r in list_res.json())

    # 4. Verify
    verify_res = client.get(f"/api/security/receipts/verify/{receipt_id}")
    assert verify_res.status_code == 200
    assert verify_res.json()["verified"] is True


def test_campushire_lock_and_seal_endpoint():
    """Verify locking and sealing a placement drive with an ArmorIQ receipt."""
    # Ensure active criteria exists
    client.post("/api/campushire/audit/execute", json={
        "company": "Northstar Technologies",
        "role": "Graduate Engineer Trainee",
        "graduation_year": 2027,
        "eligible_branches": ["CSE", "IT"],
        "minimum_cgpa": 7.0,
        "active_backlogs_allowed": 0,
    })

    # Act
    res = client.post("/api/campushire/audit/lock-and-seal?operator=@head_coordinator")

    # Assert
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "sealed"
    assert data["receipt_id"].startswith("rcpt-")
    assert len(data["intent_hash"]) == 64
    assert len(data["merkle_leaf"]) == 64
    assert data["is_verified"] is True


# ---------------------------------------------------------------------------
# 4. Strix Autonomous 25-Vector Adversarial Red-Team Suite Tests
# ---------------------------------------------------------------------------

def test_strix_adversarial_red_team_execution():
    """Verify Strix 25-vector adversarial suite achieves 100% block rate in <5ms."""
    # Act
    res = client.post("/api/security/adversarial-audit")

    # Assert
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "completed"
    assert data["total_attack_vectors"] == 25
    assert data["blocked_count"] == 25
    assert data["block_rate_percentage"] == 100.0
    assert data["average_latency_ms"] < 5.0
    assert data["sub_millisecond_pass"] is True
    assert data["verdict"] == "HARDENED_AND_CERTIFIED"
    assert data["cryptographic_receipt_id"].startswith("rcpt-")
    assert len(data["sha256_merkle_leaf"]) == 64


def test_strix_security_badge_endpoint():
    """Verify Strix security audit certification badge endpoint."""
    # Act
    res = client.get("/api/security/badge")

    # Assert
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "certified"
    assert data["block_rate"] == "100.0%"
    assert "<1.5ms" in data["avg_defense_latency"]


# ---------------------------------------------------------------------------
# 5. Laya System-1 Sub-Millisecond Reflex Intent Classification Tests
# ---------------------------------------------------------------------------

def test_laya_gate_audio_briefing_intent():
    """Verify audio briefing query routes to NotebookLM intent with <5ms latency."""
    decision = GATE.evaluate_request("student", "generate notebooklm audio podcast briefing for STU001")
    assert decision.intent == "audio_briefing"
    assert decision.recommended_action == "NOTEBOOKLM_AUDIO_BRIEFING"
    assert decision.is_safe is True
    assert decision.confidence >= 0.90
    assert decision.latency_ms < 5.0


def test_laya_gate_skill_gap_recommendations_intent():
    """Verify 500 AI projects skill-gap query routes properly."""
    decision = GATE.evaluate_request("student", "find 500 ai projects to bridge skill gap")
    assert decision.intent == "skill_gap_recommendation"
    assert decision.recommended_action == "RECOMMEND_SKILL_GAP_PROJECTS"
    assert decision.is_safe is True
    assert decision.latency_ms < 5.0


def test_laya_gate_governance_receipt_intent():
    """Verify cryptographic receipt query routes properly."""
    decision = GATE.evaluate_request("auditor", "verify armoriq cryptographic receipt")
    assert decision.intent == "governance_receipt"
    assert decision.recommended_action == "VERIFY_ARMOR_RECEIPT"
    assert decision.is_safe is True
    assert decision.latency_ms < 5.0
