"""Unit tests for Exam Hall Admit Pass & Verification Token Generator."""
import json
import pandas as pd
import pytest
from scripts.hall_pass_generator import (
    compute_admit_token,
    verify_admit_token,
    generate_hall_passes,
)


def test_compute_and_verify_token():
    token = compute_admit_token("STU001", "A-01", "Northstar Technologies")
    assert isinstance(token, str)
    assert len(token) == 19  # 4-4-4-4 format with hyphens
    assert verify_admit_token("STU001", "A-01", token, "Northstar Technologies") is True


def test_verify_token_tamper_detection():
    token = compute_admit_token("STU001", "A-01", "Northstar Technologies")
    # Tampering student id or seat must fail
    assert verify_admit_token("STU002", "A-01", token, "Northstar Technologies") is False
    assert verify_admit_token("STU001", "A-02", token, "Northstar Technologies") is False
    assert verify_admit_token("STU001", "A-01", "INVALID-TOKEN", "Northstar Technologies") is False


def test_generate_hall_passes_pipeline(tmp_path):
    att_file = tmp_path / "attendance.csv"
    crit_file = tmp_path / "brief.json"
    out_dir = tmp_path / "passes"

    pd.DataFrame([
        {"student_id": "STU001", "branch": "CSE", "cgpa": 8.1, "room_no": "Hall-A", "seat_no": "A-01"},
        {"student_id": "STU002", "branch": "IT", "cgpa": 7.5, "room_no": "Hall-A", "seat_no": "A-02"},
    ]).to_csv(att_file, index=False)

    crit_file.write_text(json.dumps({
        "company": "Northstar Technologies",
        "role": "Graduate Engineer Trainee"
    }), encoding="utf-8")

    res = generate_hall_passes(str(att_file), str(crit_file), str(out_dir))
    assert res["total_generated"] == 2
    assert (out_dir / "STU001_admit_pass.md").exists()
    assert (out_dir / "STU002_admit_pass.md").exists()
    assert (out_dir / "admit_manifest.json").exists()

    manifest = json.loads((out_dir / "admit_manifest.json").read_text(encoding="utf-8"))
    assert manifest["total_admit_passes"] == 2
    assert manifest["passes"][0]["verification_token"] is not None
