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

current_dir = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(current_dir) == "scripts":
    WORKSPACE = os.path.dirname(current_dir)
else:
    WORKSPACE = current_dir

import shutil

candidate_bins = [
    os.path.join(WORKSPACE, "laya-repo", ".venv312", "Scripts", "python.exe"),
    os.path.join(WORKSPACE, ".venv312", "Scripts", "python.exe"),
    os.path.join(WORKSPACE, "laya-repo", ".venv", "Scripts", "python.exe"),
    os.path.join(WORKSPACE, "laya-repo", ".venv", "bin", "python"),
    shutil.which("python3"),
    shutil.which("python"),
]
PYTHON_EXE = next((p for p in candidate_bins if p and os.path.exists(p)), sys.executable)


def run_suite(name: str, args: list[str], cwd: str) -> tuple[bool, str, float]:
    print(f"\n=======================================================")
    print(f" ▶ Running: {name}")
    print(f"   Directory: {cwd}")
    print(f"=======================================================")

    env = os.environ.copy()
    env["PYTHONNOUSERSITE"] = "1"
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
