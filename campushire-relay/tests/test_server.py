"""Tests for FastAPI webhook server."""

import pytest
from fastapi.testclient import TestClient
from campushire.server import app, room


@pytest.fixture
def client():
    # Ensure fresh room state for testing
    room.history.clear()
    room.active_criteria = None
    room.active_report = None
    return TestClient(app)


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "CampusHire Relay" in data["app"]


def test_get_candidates_endpoint(client):
    response = client.get("/api/candidates")
    assert response.status_code == 200
    candidates = response.json()
    assert len(candidates) >= 10
    assert any(c["roll_no"] == "23CS01" for c in candidates)


def test_switch_webhook_event_flow(client):
    # 1. Post JD event
    jd_payload = {
        "sender": "PlacementOfficer",
        "content": "@DriveCoordinator Campus Recruitment for Microsoft\nRole: SDE-1\nCTC: 44 LPA\nCutoff: 8.5 CGPA\nBatch: 2027\nDeadline: Tomorrow\nDate: Next week\nBranches: CSE, IT",
        "room": "#placement-drive-2027",
        "mentions": ["@DriveCoordinator"],
    }
    res = client.post("/api/switch/events", json=jd_payload)
    assert res.status_code == 200
    responses = res.json()["responses"]
    assert len(responses) >= 2
    assert any("Microsoft" in r["content"] for r in responses)

    # 2. Trigger Audit event
    audit_payload = {
        "sender": "DriveCoordinator",
        "content": "@EligibilityAuditor please run audit",
        "room": "#placement-drive-2027",
        "mentions": ["@EligibilityAuditor"],
    }
    res2 = client.post("/api/switch/events", json=audit_payload)
    assert res2.status_code == 200
    audit_responses = res2.json()["responses"]
    assert any("ELIGIBILITY AUDIT REPORT" in r["content"] for r in audit_responses)

    # 3. Export CSV endpoint
    csv_res = client.get("/api/audit/export-csv")
    assert csv_res.status_code == 200
    assert "text/csv" in csv_res.headers["content-type"]
    assert "roll_no,name" in csv_res.text


def test_html_ui_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "CampusHire Relay" in response.text
