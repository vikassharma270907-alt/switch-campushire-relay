#!/usr/bin/env python3
"""
Track 02 Extension: Personal Career & Voice Mock Interview Kit Generator.
Generates personalized preparation roadmaps and Wispr Flow voice mock interview prompts
for every student verified as ELIGIBLE in outputs/eligible.csv.
"""
import json
import re
import sys
from pathlib import Path
import pandas as pd

try:
    from scripts.skill_matcher import evaluate_student_skills
except ImportError:
    try:
        from skill_matcher import evaluate_student_skills
    except ImportError:
        evaluate_student_skills = None


def generate_student_prep_pack(
    eligible_csv: str = "outputs/eligible.csv",
    criteria_json: str = "outputs/drive_brief.json",
    out_dir: str = "outputs/student_prep",
) -> dict:
    out_path = Path(out_dir).resolve()
    out_path.mkdir(parents=True, exist_ok=True)

    eligible_path = Path(eligible_csv)
    if not eligible_path.exists():
        raise FileNotFoundError(f"Eligible students file not found: {eligible_csv}. Run generate_reports.py first.")

    eligible_df = pd.read_csv(eligible_path)
    criteria = {}
    if Path(criteria_json).exists():
        criteria = json.loads(Path(criteria_json).read_text(encoding="utf-8"))
    elif Path("data/eligibility_rules.json").exists():
        criteria = json.loads(Path("data/eligibility_rules.json").read_text(encoding="utf-8"))

    company = criteria.get("company", "Northstar Technologies")
    role = criteria.get("role", "Graduate Engineer Trainee")
    stages = criteria.get(
        "selection_stages", ["Online Test", "Technical Interview", "HR Interview"]
    )
    portal_deadline = criteria.get("portal_registration_deadline", "Nov 28, 2026")

    generated_files = []
    for _, row in eligible_df.iterrows():
        raw_sid = str(row["student_id"]).strip()
        # Sanitize student_id against path traversal and invalid filename characters
        safe_sid = re.sub(r"[^A-Za-z0-9_-]", "_", raw_sid)
        if not safe_sid:
            safe_sid = "UNKNOWN_STUDENT"

        branch = row.get("branch", "Engineering")
        cgpa = row.get("cgpa", "N/A")

        skill_section = ""
        stage_num = 1
        if evaluate_student_skills is not None:
            try:
                skill_res = evaluate_student_skills(safe_sid, branch, role)
                skill_section = f"\n## 1. Semantic Skill Match & Gap Analysis\n{skill_res['roadmap_markdown']}\n"
                stage_num = 2
            except Exception:
                pass

        prep_md = f"""# Personal Career & Creative Prep Kit: {safe_sid} — {company} ({role})

**Student Profile:** ID `{safe_sid}` | Branch: `{branch}` | Verified CGPA: `{cgpa}`  
**Portal Registration Deadline:** {portal_deadline}  
{skill_section}
## {stage_num}. Stage-by-Stage Preparation Roadmap
"""
        for idx, stage in enumerate(stages, 1):
            prep_md += (
                f"- **Stage {idx}: {stage}** — Review core {branch} fundamentals, "
                f"practice timed problem-solving, and prepare STAR-format project stories.\n"
            )

        prep_md += f"""
## {stage_num + 1}. Voice Mock Interview Prompts (Practice with Wispr Flow in `#student-prep-studio`)
1. *"Walk me through a {branch} project on your resume and explain a technical trade-off you made."*
2. *"Why are you interested in the {role} position at {company}?"*
3. *"Describe a time you debugged a failure under a tight deadline."*

### STAR Feedback Evaluation Rubric
- **Situation:** Did you set clear context (team, problem, constraint)?
- **Task:** Did you identify your specific responsibility?
- **Action:** Did you articulate the engineering decision or tool chosen?
- **Result:** Did you quantify the impact (latency, throughput, bug reduction)?
"""
        fp = (out_path / f"{safe_sid}_prep_kit.md").resolve()
        if not fp.is_relative_to(out_path):
            raise ValueError(f"Path traversal detected in student_id: {raw_sid}")

        fp.write_text(prep_md, encoding="utf-8")
        generated_files.append(str(fp))

    summary = {"kits_generated": len(generated_files), "files": generated_files}
    print(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    eligible_arg = sys.argv[1] if len(sys.argv) >= 2 else "outputs/eligible.csv"
    criteria_arg = sys.argv[2] if len(sys.argv) >= 3 else "outputs/drive_brief.json"
    out_dir_arg = sys.argv[3] if len(sys.argv) >= 4 else "outputs/student_prep"

    try:
        generate_student_prep_pack(eligible_arg, criteria_arg, out_dir_arg)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
