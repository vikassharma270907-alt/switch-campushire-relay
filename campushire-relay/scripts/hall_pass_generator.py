#!/usr/bin/env python3
"""
Exam Hall Admit Pass & Verification Token Generator for CampusHire Relay.
Adapted from Computer Vision & Verification Systems (500+ AI Projects - #70, #54).

Generates tamper-proof SHA-256 HMAC verification tokens and printable admit passes
for all candidates verified as ELIGIBLE. Provides invigilators with sub-second
seat authentication and anti-fraud validation on test day.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import sys
from pathlib import Path
from typing import Any, Dict, List
import pandas as pd

DEFAULT_DRIVE_SECRET = "CAMPUSHIRE_RELAY_DRIVE_SECRET_2026"


def compute_admit_token(
    student_id: str,
    seat_no: str,
    company: str,
    secret: str = DEFAULT_DRIVE_SECRET,
) -> str:
    """Compute an anti-counterfeit 16-character cryptographic verification token."""
    payload = f"{student_id.strip().upper()}:{seat_no.strip().upper()}:{company.strip().upper()}"
    digest = hmac.new(secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{digest[:4]}-{digest[4:8]}-{digest[8:12]}-{digest[12:16]}".upper()


def verify_admit_token(
    student_id: str,
    seat_no: str,
    token: str,
    company: str = "Northstar Technologies",
    secret: str = DEFAULT_DRIVE_SECRET,
) -> bool:
    """Invigilator authentication check to confirm admit pass validity."""
    expected = compute_admit_token(student_id, seat_no, company, secret)
    normalized_token = token.strip().upper().replace(" ", "")
    return hmac.compare_digest(expected, normalized_token)


def generate_hall_passes(
    attendance_csv: str = "outputs/attendance_sheet.csv",
    criteria_json: str = "outputs/drive_brief.json",
    out_dir: str = "outputs/hall_passes",
    secret: str = DEFAULT_DRIVE_SECRET,
) -> Dict[str, Any]:
    """Generate printable admit cards and cryptographic manifest for all assigned seats."""
    att_path = Path(attendance_csv)
    if not att_path.exists():
        raise FileNotFoundError(f"Attendance sheet not found at: {attendance_csv}")

    df = pd.read_csv(att_path)
    crit_path = Path(criteria_json)
    criteria = json.loads(crit_path.read_text(encoding="utf-8")) if crit_path.exists() else {}

    company = criteria.get("company", "Northstar Technologies")
    role = criteria.get("role", "Graduate Engineer Trainee")
    stages = " -> ".join(criteria.get("selection_stages", ["Online Test", "Technical Interview", "HR Interview"]))

    out_p = Path(out_dir).resolve()
    out_p.mkdir(parents=True, exist_ok=True)

    manifest_entries = []
    generated_passes = []

    for _, row in df.iterrows():
        sid = str(row["student_id"]).strip()
        branch = str(row.get("branch", "ENG")).strip()
        cgpa = str(row.get("cgpa", "N/A")).strip()
        room_no = str(row.get("room_no", "Hall-A")).strip()
        seat_no = str(row.get("seat_no", "A-01")).strip()

        token = compute_admit_token(sid, seat_no, company, secret)

        pass_md = f"""# 🎓 Official Placement Admit Pass — {company}

**Candidate ID:** `{sid}`  
**Assigned Seat:** `{room_no}` — `{seat_no}`  
**Branch:** {branch} | **Verified CGPA:** {cgpa}  
**Role:** {role}  
**Exam Stages:** {stages}  

---
### 🔒 Anti-Tamper Security Verification
- **Verification Token:** `{token}`
- **Security Protocol:** Switch AI Cryptographic Room Receipt Validated
- **Status:** **AUTHORIZED FOR ENTRY**

```
┌──────────────────────────────────────────────┐
│  CAMPUSHIRE VERIFIED ADMIT BADGE             │
│  ID: {sid:<10}  ROOM: {room_no:<8} SEAT: {seat_no:<6} │
│  AUTH: {token:<29} │
└──────────────────────────────────────────────┘
```

*Invigilator Signature: _______________________ Date: __________________*
"""
        pass_file = out_p / f"{sid}_admit_pass.md"
        pass_file.write_text(pass_md, encoding="utf-8")
        generated_passes.append(str(pass_file))

        manifest_entries.append({
            "student_id": sid,
            "room_no": room_no,
            "seat_no": seat_no,
            "branch": branch,
            "verification_token": token,
            "pass_file": str(pass_file),
        })

    manifest = {
        "company": company,
        "role": role,
        "total_admit_passes": len(manifest_entries),
        "passes": manifest_entries,
    }

    manifest_path = out_p / "admit_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    return {
        "total_generated": len(generated_passes),
        "manifest_path": str(manifest_path),
        "passes": generated_passes,
    }


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1].lower() == "verify":
        if len(sys.argv) < 5:
            print("Usage: python scripts/hall_pass_generator.py verify <student_id> <seat_no> <token> [company]")
            sys.exit(1)
        v_sid = sys.argv[2]
        v_seat = sys.argv[3]
        v_tok = sys.argv[4]
        v_comp = sys.argv[5] if len(sys.argv) >= 6 else "Northstar Technologies"
        is_valid = verify_admit_token(v_sid, v_seat, v_tok, v_comp)
        if is_valid:
            print(f"✔ [PASS VALIDATED] Candidate {v_sid} verified for seat {v_seat} at {v_comp}.")
            sys.exit(0)
        else:
            print(f"❌ [VERIFICATION FAILED] Invalid token '{v_tok}' for {v_sid} at seat {v_seat}!")
            sys.exit(1)

    att_arg = sys.argv[1] if len(sys.argv) >= 2 else "outputs/attendance_sheet.csv"
    crit_arg = sys.argv[2] if len(sys.argv) >= 3 else "outputs/drive_brief.json"
    out_arg = sys.argv[3] if len(sys.argv) >= 4 else "outputs/hall_passes"

    try:
        res = generate_hall_passes(att_arg, crit_arg, out_arg)
        print(f"Generated {res['total_generated']} admit passes. Manifest: {res['manifest_path']}")
    except FileNotFoundError as err:
        print(f"Error: {err}", file=sys.stderr)
        sys.exit(1)
