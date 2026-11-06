"""Tests for domain schemas and validation."""

import pytest
from pydantic import ValidationError
from campushire.models import PlacementCriteria, Candidate, AuditVerdict, CandidateAudit


def test_placement_criteria_valid():
    criteria = PlacementCriteria(
        company_name="Google",
        role_title="Software Development Engineer",
        package_ctc="32 LPA",
        min_cgpa=8.0,
        max_active_backlogs=0,
        eligible_branches=["CSE", "IT", "ECE"],
        batch_year=2027,
        deadline="Nov 10, 2026, 5:00 PM",
        drive_date="Nov 14, 2026",
    )
    assert criteria.company_name == "Google"
    assert criteria.min_cgpa == 8.0
    assert criteria.max_active_backlogs == 0
    assert "CSE" in criteria.eligible_branches


def test_placement_criteria_cgpa_validation():
    with pytest.raises(ValidationError):
        PlacementCriteria(
            company_name="Google",
            role_title="SDE",
            package_ctc="32 LPA",
            min_cgpa=11.5,  # Invalid: > 10.0
            eligible_branches=["CSE"],
            batch_year=2027,
            deadline="Tomorrow",
            drive_date="Next week",
        )


def test_candidate_immutability():
    candidate = Candidate(
        roll_no="23CS01",
        name="Aarav Sharma",
        email="aarav@college.edu",
        branch="CSE",
        cgpa=8.85,
        active_backlogs=0,
        batch_year=2027,
    )
    assert candidate.roll_no == "23CS01"
    with pytest.raises(ValidationError):
        # Frozen models prohibit in-place mutation
        candidate.cgpa = 9.0  # type: ignore


def test_candidate_audit_structure():
    candidate = Candidate(
        roll_no="23EC02",
        name="Priya Patel",
        email="priya@college.edu",
        branch="ECE",
        cgpa=7.95,
        active_backlogs=0,
        batch_year=2027,
    )
    audit = CandidateAudit(
        candidate=candidate,
        verdict=AuditVerdict.BORDERLINE,
        reasons=["CGPA 7.95 is within 0.1 of 8.0 threshold"],
    )
    assert audit.verdict == AuditVerdict.BORDERLINE
    assert len(audit.reasons) == 1
