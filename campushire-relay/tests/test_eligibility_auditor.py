"""Tests for @EligibilityAuditor agent."""

import pytest
from campushire.agents.eligibility_auditor import EligibilityAuditor
from campushire.models import PlacementCriteria, Candidate, AuditVerdict
from campushire.storage.student_db import StudentRepository


@pytest.fixture
def criteria():
    return PlacementCriteria(
        company_name="NexaCorp",
        role_title="Software Engineer",
        package_ctc="18 LPA",
        min_cgpa=8.0,
        max_active_backlogs=0,
        eligible_branches=["CSE", "IT", "ECE"],
        batch_year=2027,
        deadline="Nov 12, 2026",
        drive_date="Nov 16, 2026",
    )


@pytest.fixture
def repo():
    r = StudentRepository()
    r.load_synthetic_dataset()
    return r


@pytest.fixture
def auditor():
    return EligibilityAuditor(borderline_delta=0.1)


def test_audit_single_eligible_candidate(auditor, criteria):
    candidate = Candidate(
        roll_no="23CS01",
        name="Aarav Sharma",
        email="aarav@college.edu",
        branch="CSE",
        cgpa=9.32,
        active_backlogs=0,
        batch_year=2027,
    )
    result = auditor.audit_candidate(candidate, criteria)
    assert result.verdict == AuditVerdict.ELIGIBLE
    assert len(result.reasons) == 0


def test_audit_single_borderline_candidate(auditor, criteria):
    candidate = Candidate(
        roll_no="23CS04",
        name="Kunal Roy",
        email="kunal@college.edu",
        branch="CSE",
        cgpa=7.96,  # 8.0 - 0.1 <= 7.96 < 8.0
        active_backlogs=0,
        batch_year=2027,
    )
    result = auditor.audit_candidate(candidate, criteria)
    assert result.verdict == AuditVerdict.BORDERLINE
    assert any("borderline" in r.lower() for r in result.reasons)


def test_audit_single_ineligible_backlog(auditor, criteria):
    candidate = Candidate(
        roll_no="23CS06",
        name="Vikram Das",
        email="vikram@college.edu",
        branch="CSE",
        cgpa=8.5,
        active_backlogs=1,  # Ineligible
        batch_year=2027,
    )
    result = auditor.audit_candidate(candidate, criteria)
    assert result.verdict == AuditVerdict.INELIGIBLE
    assert any("backlog" in r.lower() for r in result.reasons)


def test_audit_batch_dataset(auditor, repo, criteria):
    candidates = repo.get_all_candidates()
    report = auditor.audit_candidates(candidates, criteria)

    assert report.total_evaluated == len(candidates)
    assert report.eligible_count > 0
    assert report.borderline_count > 0
    assert report.ineligible_count > 0
    assert report.eligible_count + report.borderline_count + report.ineligible_count == report.total_evaluated

    # Verify Markdown formatting
    markdown = auditor.format_audit_summary_markdown(report)
    assert "📊 ELIGIBILITY AUDIT REPORT" in markdown
    assert "Verified Shortlisted Candidates" in markdown
    assert "Borderline Review Queue" in markdown

    # Verify CSV export
    csv_data = auditor.export_shortlist_csv(report)
    assert "roll_no,name,email,branch,cgpa" in csv_data
    assert "23CS01" in csv_data
