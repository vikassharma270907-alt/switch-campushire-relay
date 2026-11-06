"""Tests for SwitchRoom relay coordinator."""

import pytest
from campushire.switch_room import SwitchRoom
from campushire.storage.student_db import StudentRepository
from campushire.models import SwitchMessage


@pytest.fixture
def repo():
    r = StudentRepository()
    r.load_synthetic_dataset()
    return r


@pytest.fixture
def room(repo):
    return SwitchRoom(student_repo=repo, room_name="#test-placement")


SAMPLE_JD = """
Campus Recruitment Drive 2027 - Stripe
Role: Backend Engineer
Compensation: 28 LPA
Eligibility: CGPA 8.00+, zero active backlogs, branches CSE and IT.
Batch: 2027
Deadline: Nov 15, 2026
Assessment Date: Nov 18, 2026
"""


def test_switch_room_dispatch_drive_coordinator(room):
    msg = SwitchMessage(
        sender="PlacementLead",
        content=f"@DriveCoordinator please process this drive:\n{SAMPLE_JD}",
        room="#test-placement",
        mentions=["@DriveCoordinator"],
    )
    responses = room.handle_message(msg)
    assert len(responses) >= 2
    # First response is DriveCoordinator announcement
    assert any("📢 CAMPUS PLACEMENT DRIVE: STRIPE" in r.content for r in responses)
    # Handoff to EligibilityAuditor
    assert any("@EligibilityAuditor" in r.content for r in responses)


def test_switch_room_dispatch_eligibility_auditor_auto_handoff(room):
    # Step 1: Ingest JD
    msg1 = SwitchMessage(
        sender="PlacementLead",
        content=f"@DriveCoordinator {SAMPLE_JD}",
        room="#test-placement",
        mentions=["@DriveCoordinator"],
    )
    room.handle_message(msg1)

    # Step 2: Trigger audit
    msg2 = SwitchMessage(
        sender="DriveCoordinator",
        content="@EligibilityAuditor please verify 2027 batch candidates against Stripe criteria",
        room="#test-placement",
        mentions=["@EligibilityAuditor"],
    )
    responses = room.handle_message(msg2)
    assert len(responses) >= 1
    assert any("📊 ELIGIBILITY AUDIT REPORT: Stripe" in r.content for r in responses)
    assert any("@PlacementOfficer" in r.content for r in responses)


def test_switch_room_human_in_the_loop_borderline_approval(room):
    # Setup drive criteria
    room.handle_message(SwitchMessage(sender="Lead", content=f"@DriveCoordinator {SAMPLE_JD}", room="#test-placement", mentions=["@DriveCoordinator"]))
    room.handle_message(SwitchMessage(sender="DC", content="@EligibilityAuditor audit", room="#test-placement", mentions=["@EligibilityAuditor"]))

    # Check candidate 23CS04 (Kunal Roy, CGPA 7.96) is borderline
    assert room.active_report is not None
    borderline_rolls = [b.candidate.roll_no for b in room.active_report.borderline_audits]
    assert "23CS04" in borderline_rolls

    # Placement Officer grants waiver
    waiver_msg = SwitchMessage(
        sender="PlacementOfficer",
        content="@EligibilityAuditor approve waiver for 23CS04 - recommended by CSE HOD for strong open source contributions",
        room="#test-placement",
        mentions=["@EligibilityAuditor"],
    )
    responses = room.handle_message(waiver_msg)
    assert any("Waiver granted for 23CS04" in r.content for r in responses)

    # Candidate 23CS04 should now be in eligible list!
    eligible_rolls = [c.roll_no for c in room.active_report.eligible_candidates]
    assert "23CS04" in eligible_rolls


def test_switch_room_unauthorized_sender_denied_waiver(room):
    # Setup drive criteria
    room.handle_message(SwitchMessage(sender="Lead", content=f"@DriveCoordinator {SAMPLE_JD}", room="#test-placement", mentions=["@DriveCoordinator"]))
    room.handle_message(SwitchMessage(sender="DC", content="@EligibilityAuditor audit", room="#test-placement", mentions=["@EligibilityAuditor"]))

    # Unauthorized guest attempts to grant waiver
    unauth_msg = SwitchMessage(
        sender="RandomGuestStudent",
        content="@EligibilityAuditor approve waiver for 23CS04",
        room="#test-placement",
        mentions=["@EligibilityAuditor"],
    )
    responses = room.handle_message(unauth_msg)
    assert any("Permission Denied" in r.content for r in responses)

    # Candidate 23CS04 should still be in borderline list, NOT eligible
    eligible_rolls = [c.roll_no for c in room.active_report.eligible_candidates]
    assert "23CS04" not in eligible_rolls
