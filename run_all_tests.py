"""
Unified Test Runner for AI Tech Consultant Ecosystem
Executes test suites across all 3 components:
  1. Task 1: Knowledge Brain (pytest)
  2. Task 2: Inbox Agent (Node.js / Express test suite)
  3. Task 3: Meeting to Scope (pytest)
"""
import os
import sys
import subprocess
import time
from pathlib import Path

ROOT_DIR = Path(__file__).parent.resolve()
VENV_PYTHON = ROOT_DIR / ".venv" / "Scripts" / "python.exe"
if not VENV_PYTHON.exists():
    VENV_PYTHON = Path(sys.executable)

def run_step(title: str, cmd: list, cwd: Path):
    print("\n" + "=" * 65)
    print(f"▶ {title}")
    print("=" * 65)
    start = time.time()
    res = subprocess.run(cmd, cwd=str(cwd), capture_output=False)
    elapsed = time.time() - start
    if res.returncode == 0:
        print(f"✓ {title} completed successfully in {elapsed:.1f}s")
        return True
    else:
        print(f"✗ {title} failed with exit code {res.returncode}")
        return False

def main():
    print("=" * 65)
    print("🚀 AI TECH CONSULTANT - UNIFIED QUALITY ASSURANCE TEST SUITE")
    print("=" * 65)

    results = {}

    # 1. Task 1: Knowledge Brain
    t1_dir = ROOT_DIR / "task1-knowledge-brain"
    results["Task 1: Knowledge Brain"] = run_step(
        "Task 1: Knowledge Brain Pytest Suite",
        [str(VENV_PYTHON), "-m", "pytest", "tests", "-v"],
        t1_dir
    )

    # 2. Task 2: Inbox Agent
    t2_dir = ROOT_DIR / "task2-inbox-agent"
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    results["Task 2: Inbox Agent"] = run_step(
        "Task 2: Inbox Agent Unit & Integration Suite",
        [npm_cmd, "test"],
        t2_dir
    )

    # 3. Task 3: Meeting to Scope
    t3_dir = ROOT_DIR / "task3-meeting-to-scope"
    results["Task 3: Meeting to Scope"] = run_step(
        "Task 3: Meeting to Scope Pytest Suite",
        [str(VENV_PYTHON), "-m", "pytest", "tests", "-v"],
        t3_dir
    )

    print("\n" + "=" * 65)
    print("📊 FINAL QUALITY ASSURANCE SUMMARY")
    print("=" * 65)
    all_passed = True
    for name, passed in results.items():
        status = "PASSED ✓" if passed else "FAILED ✗"
        print(f"  {name:35} : {status}")
        if not passed:
            all_passed = False

    print("=" * 65)
    if all_passed:
        print("🎉 ALL TEST SUITES PASSED CLEANLY (100% HEALTHY)!")
        sys.exit(0)
    else:
        print("❌ ONE OR MORE TEST SUITES REPORTED FAILURES.")
        sys.exit(1)

if __name__ == "__main__":
    main()
