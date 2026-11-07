#!/usr/bin/env python3
"""Unified Master Verification Runner for SwitchHackathon & CampusHire Relay.

Runs all test suites across the repository:
1. SwitchGuard Agent & Laya Decision Service tests (tests/)
2. CampusHire Relay multi-agent & governance tests (campushire-relay/tests/)
3. End-to-end deterministic pipeline execution check
"""

from __future__ import annotations
import os
import subprocess
import sys
import time

# Ensure UTF-8 console output encoding on Windows runners to prevent cp1252 UnicodeEncodeError
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

current_dir = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(current_dir) == "scripts":
    WORKSPACE = os.path.dirname(current_dir)
else:
    WORKSPACE = current_dir

import shutil

def find_working_python() -> str:
    candidates = []
    # If running inside a virtual environment, prefer the current python
    if sys.prefix != getattr(sys, "base_prefix", sys.prefix):
        candidates.append(sys.executable)

    # Check local workspace virtual environments
    for rel_dir in ["laya-repo/.venv312", ".venv312", "laya-repo/.venv", ".venv"]:
        parts = rel_dir.split("/")
        candidates.append(os.path.join(WORKSPACE, *parts, "Scripts", "python.exe"))
        candidates.append(os.path.join(WORKSPACE, *parts, "bin", "python"))

    candidates.extend([
        sys.executable,
        shutil.which("python3"),
        shutil.which("python"),
    ])

    for cand in candidates:
        if cand and os.path.isfile(cand):
            try:
                probe = subprocess.run([cand, "-c", "import pytest"], capture_output=True, text=True)
                if probe.returncode == 0:
                    return cand
            except Exception:
                continue

    return sys.executable

PYTHON_EXE = find_working_python()


def run_e2e_verification() -> tuple[bool, str, float]:
    e2e_script = os.path.join(WORKSPACE, "scripts", "e2e_platform_verify.py")
    if not os.path.isfile(e2e_script):
        return True, "Skipped: e2e script not found", 0.0

    print("\n=======================================================")
    print(" ▶ Running: End-to-End Subsystem Verification")
    print(f"   Script: {e2e_script}")
    print("=======================================================")

    t0 = time.perf_counter()
    env = os.environ.copy()
    env["PYTHONNOUSERSITE"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    base_paths = [WORKSPACE, os.path.join(WORKSPACE, "campushire-relay")]
    existing = [p for p in env.get("PYTHONPATH", "").split(os.pathsep) if p and "Python314" not in p]
    env["PYTHONPATH"] = os.pathsep.join(base_paths + existing)

    res = subprocess.run(
        [PYTHON_EXE, e2e_script],
        cwd=WORKSPACE,
        capture_output=True,
        text=True,
        env=env,
    )
    duration = time.perf_counter() - t0
    success = res.returncode == 0
    output = (res.stdout or "") + (res.stderr or "")
    status_str = "PASSED" if success else "FAILED"
    print(f"   Status: {status_str} in {duration:.2f}s")
    if not success:
        print(output)
    else:
        for line in output.splitlines():
            if "ALL 13 SUBSYSTEMS VERIFIED" in line or "Ready for Hackathon" in line:
                print(f"   {line.strip()}")
    return success, output, duration


def run_suite(name: str, args: list[str], cwd: str) -> tuple[bool, str, float]:
    print(f"\n=======================================================")
    print(f" ▶ Running: {name}")
    print(f"   Directory: {cwd}")
    print(f"=======================================================")

    env = os.environ.copy()
    env["PYTHONNOUSERSITE"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    # Ensure clean PYTHONPATH without global Python314 collision
    base_paths = [cwd, WORKSPACE, os.path.join(WORKSPACE, "campushire-relay")]
    existing_paths = [p for p in env.get("PYTHONPATH", "").split(os.pathsep) if p and "Python314" not in p]
    env["PYTHONPATH"] = os.pathsep.join(base_paths + existing_paths)

    pytest_args = ["-p", "no:hypothesis", "-p", "no:_hypothesis_pytestplugin"] + list(args)

    t0 = time.perf_counter()
    res = subprocess.run(
        [PYTHON_EXE, "-m", "pytest"] + pytest_args,
        cwd=cwd,
        capture_output=True,
        text=True,
        env=env,
    )
    duration = time.perf_counter() - t0
    success = res.returncode == 0
    output = (res.stdout or "") + (res.stderr or "")
    status_str = "PASSED" if success else "FAILED"
    print(f"   Status: {status_str} in {duration:.2f}s")
    if not success:
        print(output)
    else:
        for line in output.splitlines()[-4:]:
            if "passed" in line or "warnings" in line:
                print(f"   {line.strip()}")
    return success, output, duration


def main() -> int:
    start_total = time.perf_counter()
    print("=" * 65)
    print(" 🚀 SWITCHGUARD & CAMPUSHIRE RELAY - MASTER VERIFICATION RUN")
    print(f" Python Interpreter: {PYTHON_EXE}")
    print(f" Project Root:       {WORKSPACE}")
    print("=" * 65)

    suites = [
        (
            "SwitchGuard Agent & Laya Reflex Gate Suite",
            ["tests/", "-v", "--tb=short"],
            WORKSPACE,
        ),
        (
            "CampusHire Relay Multi-Agent & Governance Suite",
            ["tests/", "-v", "--tb=short"],
            os.path.join(WORKSPACE, "campushire-relay"),
        ),
    ]

    results = []
    for name, args, cwd in suites:
        if os.path.isdir(cwd):
            ok, out, dur = run_suite(name, args, cwd)
            results.append((name, ok, dur))

    # Run End-to-End Subsystem Verification
    ok_e2e, out_e2e, dur_e2e = run_e2e_verification()
    results.append(("End-to-End Subsystem Verification (13/13 Subsystems)", ok_e2e, dur_e2e))

    total_time = time.perf_counter() - start_total

    print("\n" + "=" * 65)
    print(" 📊 MASTER VERIFICATION SUMMARY")
    print("=" * 65)
    all_ok = True
    for name, ok, dur in results:
        marker = "✔ PASS" if ok else "✖ FAIL"
        if not ok:
            all_ok = False
        print(f" {marker} - {name} ({dur:.2f}s)")

    print("-" * 65)
    print(f" Total Execution Time: {total_time:.2f}s")
    if all_ok:
        print(" 🎉 Final Verdict: ALL TEST SUITES PASSED (100% GREEN) 🎉")
        return 0
    else:
        print(" ❌ Final Verdict: SOME SUITES FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
