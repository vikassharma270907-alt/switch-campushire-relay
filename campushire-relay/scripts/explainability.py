#!/usr/bin/env python3
"""
Explainable Decision Attribution & Fairness Audit Engine for CampusHire Relay.
Adapted from Machine Learning Interpretability (500+ AI Projects - #49).

Provides deterministic counterfactual explanations for rejected student candidates,
computes cohort fairness metrics (branch selection parity), and calculates
sensitivity deltas for placement cell coordinators.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List
import pandas as pd


def compute_counterfactual(
    student_row: Dict[str, Any],
    criteria: Dict[str, Any],
) -> Dict[str, Any]:
    """Calculate the minimal parameter adjustment required to achieve ELIGIBLE status."""
    reasons = []
    perturbations = {}

    req_year = int(criteria.get("graduation_year", 2027))
    actual_year = student_row.get("graduation_year")
    if actual_year is not None and not pd.isna(actual_year):
        actual_year = int(float(actual_year))
        if actual_year != req_year:
            reasons.append(f"Graduation year mismatch ({actual_year} vs {req_year})")
            perturbations["graduation_year"] = {
                "current": actual_year,
                "target": req_year,
                "delta_years": req_year - actual_year,
            }

    allowed_branches = [b.strip().upper() for b in criteria.get("eligible_branches", ["CSE", "IT"])]
    actual_branch = str(student_row.get("branch", "")).strip().upper()
    if actual_branch not in allowed_branches:
        reasons.append(f"Branch '{actual_branch}' not in allowed list: {', '.join(allowed_branches)}")
        perturbations["branch"] = {
            "current": actual_branch,
            "target": allowed_branches,
            "eligible": False,
        }

    min_cgpa = float(criteria.get("minimum_cgpa", 7.0))
    actual_cgpa = student_row.get("cgpa")
    if actual_cgpa is not None and not pd.isna(actual_cgpa) and str(actual_cgpa).strip() != "":
        actual_cgpa = float(actual_cgpa)
        if actual_cgpa < min_cgpa:
            gap = round(min_cgpa - actual_cgpa, 2)
            reasons.append(f"CGPA deficit: {actual_cgpa:.2f} < {min_cgpa:.2f} (gap: +{gap:.2f})")
            perturbations["cgpa"] = {
                "current": actual_cgpa,
                "target": min_cgpa,
                "delta_required": f"+{gap:.2f}",
            }

    max_backlogs = int(criteria.get("active_backlogs_allowed", 0))
    actual_backlogs = student_row.get("active_backlogs")
    if actual_backlogs is not None and not pd.isna(actual_backlogs) and str(actual_backlogs).strip() != "":
        actual_backlogs = int(float(actual_backlogs))
        if actual_backlogs > max_backlogs:
            excess = actual_backlogs - max_backlogs
            reasons.append(f"Excess backlogs: {actual_backlogs} > {max_backlogs} (must clear {excess})")
            perturbations["active_backlogs"] = {
                "current": actual_backlogs,
                "target": max_backlogs,
                "clear_required": excess,
            }

    return {
        "student_id": str(student_row.get("student_id", "")),
        "primary_reasons": reasons,
        "counterfactual_actions": perturbations,
        "is_near_boundary": ("cgpa" in perturbations and float(perturbations["cgpa"]["delta_required"].replace("+", "")) <= 0.50),
    }


def audit_cohort_fairness(
    results_df: pd.DataFrame,
    criteria: Dict[str, Any],
) -> Dict[str, Any]:
    """Calculate cross-branch representation, pass rates, and sensitivity analysis."""
    total_candidates = len(results_df)
    if total_candidates == 0:
        return {"error": "Empty dataset"}

    branch_stats = {}
    for branch, group in results_df.groupby("branch"):
        total_in_branch = len(group)
        eligible_in_branch = int((group["status"] == "ELIGIBLE").sum())
        pass_rate = round((eligible_in_branch / float(total_in_branch)) * 100.0, 1)
        branch_stats[str(branch)] = {
            "total_candidates": total_in_branch,
            "eligible_count": eligible_in_branch,
            "pass_rate_pct": pass_rate,
        }

    # Sensitivity analysis: What if CGPA threshold is relaxed by 0.5?
    min_cgpa = float(criteria.get("minimum_cgpa", 7.0))
    relaxed_cgpa = max(0.0, min_cgpa - 0.50)
    
    near_miss_students = []
    for _, row in results_df.iterrows():
        if row["status"] != "ELIGIBLE":
            try:
                cgpa = float(row.get("cgpa", 0))
                branch = str(row.get("branch", "")).strip().upper()
                allowed = [b.upper() for b in criteria.get("eligible_branches", [])]
                backlogs = int(row.get("active_backlogs", 0))
                year = int(row.get("graduation_year", 0))
                
                # Check if relaxing CGPA alone would flip student to ELIGIBLE
                if (
                    branch in allowed
                    and backlogs <= int(criteria.get("active_backlogs_allowed", 0))
                    and year == int(criteria.get("graduation_year", 2027))
                    and cgpa >= relaxed_cgpa
                ):
                    near_miss_students.append({
                        "student_id": str(row["student_id"]),
                        "cgpa": cgpa,
                        "required": min_cgpa,
                        "delta": round(min_cgpa - cgpa, 2)
                    })
            except (ValueError, TypeError):
                continue

    return {
        "total_audited": total_candidates,
        "eligible_total": int((results_df["status"] == "ELIGIBLE").sum()),
        "not_eligible_total": int((results_df["status"] == "NOT_ELIGIBLE").sum()),
        "needs_review_total": int((results_df["status"] == "NEEDS_REVIEW").sum()),
        "branch_distribution": branch_stats,
        "sensitivity_analysis": {
            "relaxed_cgpa_threshold": relaxed_cgpa,
            "potential_newly_eligible_count": len(near_miss_students),
            "near_miss_candidates": near_miss_students,
        },
    }


def generate_explainability_report(
    results_csv: str = "outputs/eligibility_results.csv",
    criteria_json: str = "data/eligibility_rules.json",
    out_file: str = "outputs/explainability_report.json",
) -> Dict[str, Any]:
    """Generate complete explainability report with counterfactuals and cohort metrics."""
    res_path = Path(results_csv)
    if not res_path.exists():
        raise FileNotFoundError(f"Eligibility results not found at: {results_csv}")

    results_df = pd.read_csv(res_path)
    criteria = json.loads(Path(criteria_json).read_text(encoding="utf-8")) if Path(criteria_json).exists() else {}

    fairness = audit_cohort_fairness(results_df, criteria)

    counterfactuals = []
    for _, row in results_df.iterrows():
        if row["status"] != "ELIGIBLE":
            cf = compute_counterfactual(row.to_dict(), criteria)
            counterfactuals.append(cf)

    report = {
        "audit_fairness_summary": fairness,
        "counterfactual_explanations": counterfactuals,
    }

    out_p = Path(out_file)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    res_arg = sys.argv[1] if len(sys.argv) >= 2 else "outputs/eligibility_results.csv"
    crit_arg = sys.argv[2] if len(sys.argv) >= 3 else "data/eligibility_rules.json"
    out_arg = sys.argv[3] if len(sys.argv) >= 4 else "outputs/explainability_report.json"

    rep = generate_explainability_report(res_arg, crit_arg, out_arg)
    print(json.dumps(rep["audit_fairness_summary"], indent=2))
