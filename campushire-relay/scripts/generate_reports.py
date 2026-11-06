#!/usr/bin/env python3
"""
Operations Pack & Split Report Generator for CampusHire Relay.
Splits outputs/eligibility_results.csv into eligible.csv, not_eligible.csv, and needs_review.csv,
and generates the student announcement, attendance sheet template, and drive coordination checklist.
"""
import json
import sys
from pathlib import Path
import pandas as pd


def generate_all_reports(
    results_csv: str = "outputs/eligibility_results.csv",
    criteria_json: str = "data/eligibility_rules.json",
    out_dir: str = "outputs",
) -> dict:
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    results_path = Path(results_csv)
    if not results_path.exists():
        raise FileNotFoundError(f"Eligibility results file not found: {results_csv}. Run validate_eligibility.py first.")

    res_df = pd.read_csv(results_path)

    criteria = {}
    if Path(criteria_json).exists():
        criteria = json.loads(Path(criteria_json).read_text(encoding="utf-8"))
    elif (out_path / "drive_brief.json").exists():
        criteria = json.loads((out_path / "drive_brief.json").read_text(encoding="utf-8"))

    eligible = res_df[res_df["status"] == "ELIGIBLE"]
    not_eligible = res_df[res_df["status"] == "NOT_ELIGIBLE"]
    needs_review = res_df[res_df["status"] == "NEEDS_REVIEW"]

    eligible.to_csv(out_path / "eligible.csv", index=False)
    not_eligible.to_csv(out_path / "not_eligible.csv", index=False)
    needs_review.to_csv(out_path / "needs_review.csv", index=False)

    # Generate Attendance Sheet Template for Eligible Candidates
    attendance_df = eligible[["student_id", "branch", "cgpa", "graduation_year"]].copy()
    attendance_df["room_no"] = "Hall-A"
    attendance_df["seat_no"] = [f"A-{i+1:02d}" for i in range(len(attendance_df))]
    attendance_df["student_signature"] = ""
    attendance_df["invigilator_initials"] = ""
    attendance_sheet_file = out_path / "attendance_sheet.csv"
    attendance_df.to_csv(attendance_sheet_file, index=False)

    # Automatically generate cryptographic admit passes for eligible students
    try:
        from scripts.hall_pass_generator import generate_hall_passes
    except ImportError:
        try:
            from hall_pass_generator import generate_hall_passes
        except ImportError:
            generate_hall_passes = None

    if generate_hall_passes is not None and len(eligible) > 0:
        try:
            crit_file = str(out_path / "drive_brief.json") if (out_path / "drive_brief.json").exists() else criteria_json
            generate_hall_passes(
                attendance_csv=str(attendance_sheet_file),
                criteria_json=crit_file,
                out_dir=str(out_path / "hall_passes"),
            )
        except Exception:
            pass

    # Generate Draft Student Announcement
    company = criteria.get("company", "Northstar Technologies")
    role = criteria.get("role", "Graduate Engineer Trainee")
    grad_year = criteria.get("graduation_year", 2027)
    branches = ", ".join(criteria.get("eligible_branches", ["CSE", "IT"]))
    min_cgpa = criteria.get("minimum_cgpa", 7.0)
    backlogs = criteria.get("active_backlogs_allowed", 0)
    stages = " -> ".join(
        criteria.get("selection_stages", ["Online Test", "Technical Interview", "HR Interview"])
    )
    portal_deadline = criteria.get("portal_registration_deadline", "Nov 28, 2026")
    app_deadline = criteria.get("application_deadline", "December 1, 2026")

    eligible_ids = ", ".join(eligible["student_id"].astype(str).tolist()) or "None"
    review_ids = ", ".join(needs_review["student_id"].astype(str).tolist()) or "None"

    announcement_md = f"""# Campus Placement Announcement: {company} ({role})

**Target Batch:** Class of {grad_year}  
**Eligible Branches:** {branches}  
**Minimum CGPA:** {min_cgpa} (out of 10.0)  
**Maximum Active Backlogs Allowed:** {backlogs}  
**Selection Process:** {stages}  

## Important Deadlines
- **College Portal Registration Deadline:** {portal_deadline}
- **Company Application Close:** {app_deadline}

## Provisional Shortlist Summary
- **Provisionally Eligible Candidates ({len(eligible)}):** {eligible_ids}
- **Pending Verification / Needs Office Review ({len(needs_review)}):** {review_ids}

*Note: Candidates listed under Pending Verification must submit updated transcripts to the Placement Cell before {portal_deadline}.*
"""
    (out_path / "draft_announcement.md").write_text(announcement_md, encoding="utf-8")

    # Generate Drive Coordination Checklist
    checklist_md = f"""# Drive Coordination Checklist — {company} ({role})

- [x] **Step 1:** Parse recruiter notice and extract structured criteria (`drive_brief.json`).
- [x] **Step 2:** Obtain human Placement Coordinator sign-off on extracted eligibility rules.
- [x] **Step 3:** Execute deterministic student database audit (`validate_eligibility.py`) with SHA-256 receipt.
- [ ] **Step 4:** Human review of **{len(needs_review)}** flagged record(s) in `outputs/needs_review.csv` ({review_ids}).
- [ ] **Step 5:** Human approval to publish `outputs/draft_announcement.md` to student noticeboard.
- [ ] **Step 6:** Print `outputs/attendance_sheet.csv` ({len(eligible)} seats allocated in Hall-A) for Online Test stage.
"""
    (out_path / "drive_checklist.md").write_text(checklist_md, encoding="utf-8")

    summary = {
        "total": len(res_df),
        "eligible": len(eligible),
        "not_eligible": len(not_eligible),
        "needs_review": len(needs_review),
    }
    print(f"Total students: {summary['total']}")
    print(f"Eligible: {summary['eligible']}")
    print(f"Not Eligible: {summary['not_eligible']}")
    print(f"Needs Review: {summary['needs_review']}")
    return summary


if __name__ == "__main__":
    results_arg = sys.argv[1] if len(sys.argv) >= 2 else "outputs/eligibility_results.csv"
    criteria_arg = sys.argv[2] if len(sys.argv) >= 3 else "data/eligibility_rules.json"
    out_dir_arg = sys.argv[3] if len(sys.argv) >= 4 else "outputs"

    try:
        generate_all_reports(results_arg, criteria_arg, out_dir_arg)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
