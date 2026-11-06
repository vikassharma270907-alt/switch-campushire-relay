"""Unit tests for Semantic Skill Matcher & Gap Analysis Engine."""
import pytest
from scripts.skill_matcher import (
    normalize_skill,
    extract_skills_from_text,
    compute_skill_overlap,
    synthesize_gap_roadmap,
    evaluate_student_skills,
)


def test_normalize_skill():
    assert normalize_skill("  Python 3.10  ") == "python310"
    assert normalize_skill("C++") == "c++"
    assert normalize_skill("REST APIs & Microservices!") == "restapis#microservices"


def test_extract_skills_from_text():
    sample_text = (
        "We are looking for candidates skilled in Python, SQL, REST APIs, and System Design. "
        "Experience with Git and Algorithms is preferred."
    )
    skills = extract_skills_from_text(sample_text)
    assert "python" in skills
    assert "sql" in skills
    assert "rest apis" in skills
    assert "system design" in skills
    assert "git" in skills
    assert "algorithms" in skills


def test_compute_skill_overlap_perfect_match():
    cand = ["python", "sql", "git"]
    job = ["python", "sql", "git"]
    res = compute_skill_overlap(cand, job)
    assert res["match_score"] == 100.0
    assert res["coverage_ratio"] == 1.0
    assert len(res["missing_skills"]) == 0
    assert len(res["matched_skills"]) == 3


def test_compute_skill_overlap_with_gaps():
    cand = ["python", "git", "c++"]
    job = ["python", "sql", "docker", "git"]
    res = compute_skill_overlap(cand, job)
    assert res["coverage_ratio"] == 0.50  # 2 of 4 matched
    assert "sql" in res["missing_skills"]
    assert "docker" in res["missing_skills"]
    assert "python" in res["matched_skills"]
    assert "git" in res["matched_skills"]


def test_evaluate_student_skills_cse():
    res = evaluate_student_skills("STU001", "CSE", "Graduate Engineer Trainee")
    assert res["student_id"] == "STU001"
    assert res["branch"] == "CSE"
    assert res["match_score"] > 50.0
    assert "roadmap_markdown" in res
    assert "3-Day Rapid Gap-Closing Sprint" in res["roadmap_markdown"]


def test_evaluate_student_skills_it():
    res = evaluate_student_skills("STU002", "IT", "Graduate Engineer Trainee")
    assert res["student_id"] == "STU002"
    assert res["branch"] == "IT"
    assert res["match_score"] > 50.0
    assert "rest apis" in res["matched_skills"] or "sql" in res["matched_skills"]
