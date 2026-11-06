"""Tests for Student Database repository."""

import pytest
from campushire.models import Candidate
from campushire.storage.student_db import StudentRepository


@pytest.fixture
def repo():
    r = StudentRepository()
    r.load_synthetic_dataset()
    return r


def test_repository_load_synthetic_dataset(repo):
    candidates = repo.get_all_candidates()
    assert len(candidates) >= 10
    roll_numbers = [c.roll_no for c in candidates]
    assert len(roll_numbers) == len(set(roll_numbers)), "Roll numbers must be unique"


def test_repository_get_by_batch(repo):
    batch_2027 = repo.get_candidates_by_batch(2027)
    assert len(batch_2027) > 0
    assert all(c.batch_year == 2027 for c in batch_2027)


def test_repository_add_and_get():
    custom_repo = StudentRepository()
    candidate = Candidate(
        roll_no="23AI99",
        name="Ananya Verma",
        email="ananya@college.edu",
        branch="AI",
        cgpa=9.4,
        active_backlogs=0,
        batch_year=2027,
    )
    custom_repo.add_candidate(candidate)
    fetched = custom_repo.get_candidate("23AI99")
    assert fetched is not None
    assert fetched.name == "Ananya Verma"
    assert fetched.cgpa == 9.4
    assert custom_repo.get_candidate("NON_EXISTENT") is None
