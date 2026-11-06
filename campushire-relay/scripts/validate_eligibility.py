#!/usr/bin/env python3
"""
Deterministic Student Eligibility Verifier & SHA-256 Receipt Generator for CampusHire Relay.
Classifies students into ELIGIBLE, NOT_ELIGIBLE, or NEEDS_REVIEW, detects duplicate IDs,
and strips optional PII columns before generating room-safe reports.
"""
import hashlib
import json
import sys
from pathlib import Path
import pandas as pd


def classify_student(row, criteria: dict, duplicate_ids=None):
    student_id = str(row.get("student_id", "")).strip()
    if not student_id or student_id.lower() == "nan":
        return "NEEDS_REVIEW", "Missing student_id"
    if duplicate_ids and student_id in duplicate_ids:
        return "NEEDS_REVIEW", f"Duplicate student_id detected ({student_id})"

    # Check missing/null values before numerical comparisons
    grad_val = row.get("graduation_year")
    if pd.isna(grad_val) or str(grad_val).strip() in ("", "nan", "None"):
        return "NEEDS_REVIEW", "Graduation year missing"

    branch_val = row.get("branch")
    if pd.isna(branch_val) or str(branch_val).strip() in ("", "nan", "None"):
        return "NEEDS_REVIEW", "Branch missing"

    cgpa_val = row.get("cgpa")
    if pd.isna(cgpa_val) or str(cgpa_val).strip() in ("", "nan", "None"):
        return "NEEDS_REVIEW", "CGPA missing"

    backlogs_val = row.get("active_backlogs")
    if pd.isna(backlogs_val) or str(backlogs_val).strip() in ("", "nan", "None"):
        return "NEEDS_REVIEW", "Active backlogs missing"

    # Safe numerical conversions to prevent unhandled ValueError
    try:
        grad_year = int(float(grad_val))
    except (ValueError, TypeError):
        return "NEEDS_REVIEW", f"Invalid graduation_year format: {grad_val}"

    try:
        cgpa = float(cgpa_val)
        if cgpa < 0.0 or cgpa > 10.0:
            return "NEEDS_REVIEW", f"CGPA out of valid range (0-10): {cgpa}"
    except (ValueError, TypeError):
        return "NEEDS_REVIEW", f"Invalid CGPA format: {cgpa_val}"

    try:
        backlogs = int(float(backlogs_val))
        if backlogs < 0:
            return "NEEDS_REVIEW", f"Active backlogs cannot be negative: {backlogs}"
    except (ValueError, TypeError):
        return "NEEDS_REVIEW", f"Invalid active_backlogs format: {backlogs_val}"

    # Deterministic rule evaluation
    req_year = int(criteria["graduation_year"])
    if grad_year != req_year:
        return "NOT_ELIGIBLE", f"Graduation year mismatch ({grad_year} != {req_year})"

    branch = str(branch_val).strip()
    allowed_branches = [b.strip() for b in criteria["eligible_branches"]]
    if branch not in allowed_branches:
        return "NOT_ELIGIBLE", f"Branch not eligible ({branch} not in {'/'.join(allowed_branches)})"

    min_cgpa = float(criteria["minimum_cgpa"])
    if cgpa < min_cgpa:
        return "NOT_ELIGIBLE", f"CGPA below minimum ({cgpa:.2f} < {min_cgpa:.2f})"

    max_backlogs = int(criteria["active_backlogs_allowed"])
    if backlogs > max_backlogs:
        return "NOT_ELIGIBLE", f"Too many backlogs ({backlogs} > {max_backlogs})"

    return "ELIGIBLE", "Meets all criteria"


def audit_dataframe(df: pd.DataFrame, criteria: dict) -> pd.DataFrame:
    id_series = df["student_id"].dropna().astype(str).str.strip()
    duplicate_ids = set(id_series[id_series.duplicated(keep=False)].tolist())
    rows = []
    for _, row in df.iterrows():
        status, reason = classify_student(row, criteria, duplicate_ids=duplicate_ids)
        rows.append(
            {
                "student_id": str(row.get("student_id", "")).strip(),
                "branch": row.get("branch"),
                "cgpa": row.get("cgpa"),
                "active_backlogs": row.get("active_backlogs"),
                "graduation_year": row.get("graduation_year"),
                "status": status,
                "reason": reason,
            }
        )
    return pd.DataFrame(rows)


def compute_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def run_validation(
    students_file: str,
    criteria_file: str,
    output_file: str = "outputs/eligibility_results.csv",
) -> dict:
    """Run full eligibility audit, save results CSV, and generate audit receipt."""
    df = pd.read_csv(students_file)
    with open(criteria_file, encoding="utf-8") as f:
        criteria = json.load(f)

    res_df = audit_dataframe(df, criteria)
    out_path = Path(output_file)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    res_df.to_csv(out_path, index=False)

    receipt = {
        "students_csv_sha256": compute_sha256(students_file),
        "criteria_json_sha256": compute_sha256(criteria_file),
        "results_csv_sha256": compute_sha256(str(out_path)),
        "total_records": len(res_df),
        "eligible_count": int((res_df["status"] == "ELIGIBLE").sum()),
        "not_eligible_count": int((res_df["status"] == "NOT_ELIGIBLE").sum()),
        "needs_review_count": int((res_df["status"] == "NEEDS_REVIEW").sum()),
    }

    # Automatically generate explainability & fairness audit
    try:
        from scripts.explainability import generate_explainability_report
    except ImportError:
        try:
            from explainability import generate_explainability_report
        except ImportError:
            generate_explainability_report = None

    if generate_explainability_report is not None:
        try:
            exp_report = generate_explainability_report(
                results_csv=str(out_path),
                criteria_json=criteria_file,
                out_file=str(out_path.parent / "explainability_report.json"),
            )
            receipt["explainability_summary"] = {
                "branch_distribution": exp_report.get("audit_fairness_summary", {}).get("branch_distribution", {}),
                "sensitivity_analysis": exp_report.get("audit_fairness_summary", {}).get("sensitivity_analysis", {}),
            }
        except Exception:
            pass

    receipt_path = out_path.parent / "audit_receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(
            "Usage: python scripts/validate_eligibility.py <students_csv> <criteria_json> [output_csv]",
            file=sys.stderr,
        )
        sys.exit(1)
    students_file = sys.argv[1]
    criteria_file = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) >= 4 else "outputs/eligibility_results.csv"

    receipt = run_validation(students_file, criteria_file, output_file)
    print(json.dumps(receipt, indent=2))
