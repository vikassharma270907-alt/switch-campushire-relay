#!/usr/bin/env python3
"""
Deterministic & Regex-Hardened Recruiter Notice Parser for CampusHire Relay.
Extracts structured eligibility rules and flags missing/ambiguous fields for human clarification.
"""
import json
import re
import sys
from pathlib import Path


def extract_notice_text(text: str) -> dict:
    header_match = re.search(r"\*\*\s*(.*?)\s*[–—-]\s*(.*?)\s*\*\*", text)
    if not header_match:
        first_line = text.strip().splitlines()[0] if text.strip() else ""
        header_match = re.search(r"^#*\s*(.*?)\s*[–—-]\s*(.*?)\s*$", first_line)

    company = header_match.group(1).strip() if header_match else None
    role = header_match.group(2).strip() if header_match else None

    year_match = re.search(r"Graduating Year:\s*(?:\*\*)?(\d{4})(?:\*\*)?", text, re.IGNORECASE)
    branches_match = re.search(r"Eligible Branches:\s*(?:\*\*)?([A-Za-z,\s/&-]+?)(?:\*\*)?(?:\n|$)", text, re.IGNORECASE)
    cgpa_match = re.search(r"Minimum CGPA:\s*(?:\*\*)?(\d+(?:\.\d+)?)(?:\*\*)?", text, re.IGNORECASE)
    backlogs_match = re.search(r"Active Backlogs Allowed:\s*(?:\*\*)?(\d+)(?:\*\*)?", text, re.IGNORECASE)
    stages_match = re.search(r"Selection Stages:\s*([^\n]+)", text, re.IGNORECASE)
    deadline_match = re.search(r"Application Deadline:\s*(?:\*\*)?([^\n*]+?)(?:\*\*)?(?:\n|$)", text, re.IGNORECASE)
    portal_deadline_match = re.search(
        r"register via the college portal by\s*([A-Za-z0-9,\s]+?)(?:\.|\n|$)",
        text,
        re.IGNORECASE,
    )

    missing_fields = []
    if not company:
        missing_fields.append("company")
    if not role:
        missing_fields.append("role")
    if not year_match:
        missing_fields.append("graduation_year")
    if not branches_match:
        missing_fields.append("eligible_branches")
    if not cgpa_match:
        missing_fields.append("minimum_cgpa")
    if not backlogs_match:
        missing_fields.append("active_backlogs_allowed")

    return {
        "company": company,
        "role": role,
        "graduation_year": int(year_match.group(1)) if year_match else None,
        "eligible_branches": [
            b.strip() for b in branches_match.group(1).split(",") if b.strip()
        ]
        if branches_match
        else [],
        "minimum_cgpa": float(cgpa_match.group(1)) if cgpa_match else None,
        "active_backlogs_allowed": int(backlogs_match.group(1)) if backlogs_match else None,
        "selection_stages": [
            s.strip().strip("*") for s in stages_match.group(1).split(",") if s.strip()
        ]
        if stages_match
        else ["Online Test", "Technical Interview", "HR Interview"],
        "application_deadline": deadline_match.group(1).strip() if deadline_match else "TBD",
        "portal_registration_deadline": portal_deadline_match.group(1).strip()
        if portal_deadline_match
        else "TBD",
        "missing_or_ambiguous_fields": missing_fields,
        "requires_human_clarification": len(missing_fields) > 0,
    }


def extract_notice(filepath: str, raise_on_missing: bool = False) -> dict:
    text = Path(filepath).read_text(encoding="utf-8")
    criteria = extract_notice_text(text)
    if raise_on_missing and criteria["requires_human_clarification"]:
        missing = ", ".join(criteria["missing_or_ambiguous_fields"])
        raise ValueError(f"Missing or ambiguous criteria fields require human clarification: {missing}")
    return criteria


def save_criteria_to_json(criteria: dict, out_path: str) -> str:
    """Serialize criteria dictionary to formatted JSON file."""
    output_str = json.dumps(criteria, indent=2)
    path = Path(out_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(output_str + "\n", encoding="utf-8")
    return output_str


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/extract_criteria.py <notice_file> [output_json]", file=sys.stderr)
        sys.exit(1)
    notice_path = sys.argv[1]
    data = extract_notice(notice_path, raise_on_missing=False)
    if len(sys.argv) >= 3:
        output_str = save_criteria_to_json(data, sys.argv[2])
    else:
        output_str = json.dumps(data, indent=2)
    print(output_str)
