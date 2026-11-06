"""Unit tests for Explainable Decision Attribution & Fairness Audit Engine."""
import pandas as pd
import pytest
from scripts.explainability import (
    compute_counterfactual,
    audit_cohort_fairness,
    generate_explainability_report,
)

criteria = {
    "company": "Northstar Technologies",
    "role": "Graduate Engineer Trainee",
    "graduation_year": 2027,
    "eligible_branches": ["CSE", "IT"],
    "minimum_cgpa": 7.0,
    "active_backlogs_allowed": 0,
}


def test_counterfactual_cgpa_deficit():
    student = {
        "student_id": "STU004",
        "branch": "CSE",
        "cgpa": 6.8,
        "active_backlogs": 0,
        "graduation_year": 2027,
    }
    cf = compute_counterfactual(student, criteria)
    assert cf["student_id"] == "STU004"
    assert cf["is_near_boundary"] is True
    assert "cgpa" in cf["counterfactual_actions"]
    assert cf["counterfactual_actions"]["cgpa"]["delta_required"] == "+0.20"


def test_counterfactual_branch_and_backlog():
    student = {
        "student_id": "STU005",
        "branch": "ECE",
        "cgpa": 7.9,
        "active_backlogs": 1,
        "graduation_year": 2027,
    }
    cf = compute_counterfactual(student, criteria)
    assert "branch" in cf["counterfactual_actions"]
    assert "active_backlogs" in cf["counterfactual_actions"]
    assert cf["counterfactual_actions"]["active_backlogs"]["clear_required"] == 1


def test_audit_cohort_fairness():
    df = pd.DataFrame([
        {"student_id": "S1", "branch": "CSE", "status": "ELIGIBLE", "cgpa": 8.0, "active_backlogs": 0, "graduation_year": 2027},
        {"student_id": "S2", "branch": "CSE", "status": "NOT_ELIGIBLE", "cgpa": 6.8, "active_backlogs": 0, "graduation_year": 2027},
        {"student_id": "S3", "branch": "IT", "status": "ELIGIBLE", "cgpa": 7.5, "active_backlogs": 0, "graduation_year": 2027},
        {"student_id": "S4", "branch": "ECE", "status": "NOT_ELIGIBLE", "cgpa": 8.0, "active_backlogs": 0, "graduation_year": 2027},
    ])
    fairness = audit_cohort_fairness(df, criteria)
    assert fairness["total_audited"] == 4
    assert fairness["eligible_total"] == 2
    assert "CSE" in fairness["branch_distribution"]
    assert fairness["branch_distribution"]["CSE"]["pass_rate_pct"] == 50.0
    assert fairness["sensitivity_analysis"]["potential_newly_eligible_count"] == 1
    assert fairness["sensitivity_analysis"]["near_miss_candidates"][0]["student_id"] == "S2"


def test_generate_explainability_report(tmp_path):
    results_file = tmp_path / "results.csv"
    crit_file = tmp_path / "rules.json"
    out_file = tmp_path / "explain.json"

    df = pd.DataFrame([
        {"student_id": "STU001", "branch": "CSE", "status": "ELIGIBLE", "cgpa": 8.1, "active_backlogs": 0, "graduation_year": 2027},
        {"student_id": "STU004", "branch": "CSE", "status": "NOT_ELIGIBLE", "cgpa": 6.8, "active_backlogs": 0, "graduation_year": 2027},
    ])
    df.to_csv(results_file, index=False)

    import json
    crit_file.write_text(json.dumps(criteria), encoding="utf-8")

    report = generate_explainability_report(str(results_file), str(crit_file), str(out_file))
    assert out_file.exists()
    assert "audit_fairness_summary" in report
    assert "counterfactual_explanations" in report
    assert len(report["counterfactual_explanations"]) == 1
    assert report["counterfactual_explanations"][0]["student_id"] == "STU004"
