"""Tests for @DriveCoordinator agent."""

import pytest
from campushire.agents.drive_coordinator import DriveCoordinator
from campushire.models import PlacementCriteria


@pytest.fixture
def coordinator():
    return DriveCoordinator()


SAMPLE_RECRUITER_EMAIL = """
Subject: Campus Recruitment Drive 2027 - NexaCorp Technologies

Dear Placement Cell,

NexaCorp is pleased to announce our campus drive for the 2027 graduating batch.
We are hiring for the role of Graduate Software Engineer with a compensation package of 18 LPA (Fixed: 15 LPA + Performance Bonus: 3 LPA).

Eligibility Criteria:
- Minimum CGPA: 8.00 and above throughout academics
- No active backlogs allowed at the time of drive
- Target Branches: CSE, IT, and ECE
- Passing Batch: 2027

Key Dates:
- Student Registration Deadline: Nov 12, 2026, 11:59 PM
- Online Technical Assessment: Nov 16, 2026

Please share the verified shortlist by Nov 13 so we can issue test credentials.

Best regards,
University Relations Team, NexaCorp
"""


def test_drive_coordinator_parse_jd(coordinator):
    criteria = coordinator.parse_job_description(SAMPLE_RECRUITER_EMAIL)
    assert "NexaCorp" in criteria.company_name
    assert "Software Engineer" in criteria.role_title
    assert "18 LPA" in criteria.package_ctc
    assert criteria.min_cgpa == 8.0
    assert criteria.max_active_backlogs == 0
    assert "CSE" in criteria.eligible_branches
    assert "IT" in criteria.eligible_branches
    assert "ECE" in criteria.eligible_branches
    assert criteria.batch_year == 2027
    assert "Nov 12, 2026" in criteria.deadline


def test_drive_coordinator_generate_announcement(coordinator):
    criteria = coordinator.parse_job_description(SAMPLE_RECRUITER_EMAIL)
    announcement = coordinator.generate_announcement(criteria)
    assert "📢 CAMPUS PLACEMENT DRIVE" in announcement
    assert "NexaCorp" in announcement
    assert "18 LPA" in announcement
    assert "CGPA: 8.0" in announcement
    assert "CSE, IT, ECE" in announcement
    assert "Nov 12, 2026" in announcement


def test_drive_coordinator_generate_checklist(coordinator):
    criteria = coordinator.parse_job_description(SAMPLE_RECRUITER_EMAIL)
    checklist = coordinator.generate_timeline_checklist(criteria)
    assert len(checklist) >= 4
    assert any("shortlist" in item.lower() for item in checklist)
