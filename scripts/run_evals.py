#!/usr/bin/env python3
"""Run answer evals from evals/cases/*.json through `claude -p` and check the regexes.

Usage:
  python3 scripts/run_evals.py [skill ...] [--ids 1,3] [--baseline] [--model MODEL]
                                [--timeout SECONDS] [--out DIR]

--baseline runs without this plugin loaded, which shows how much each skill adds.
Each call runs in an empty directory, so the model cannot read the skills from the repo.
--out saves every answer to DIR/<skill>-<id>.<pass|fail>.md for review.
Each eval is one `claude -p` call, so a full run costs tokens.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CASES = ROOT / "evals" / "cases"


def ask(prompt, baseline, model, timeout):
    cmd = ["claude", "-p", prompt, "--output-format", "text"]
    if not baseline:
        cmd += ["--plugin-dir", str(ROOT)]
    if model:
        cmd += ["--model", model]
    with tempfile.TemporaryDirectory() as empty:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=empty, stdin=subprocess.DEVNULL)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip().splitlines()[-1] if result.stderr.strip() else "claude exited non-zero")
    return result.stdout


def grade(answer, case):
    missing = [p for p in case.get("must_match", []) if not re.search(p, answer)]
    forbidden = [p for p in case.get("must_not_match", []) if re.search(p, answer)]
    return missing, forbidden


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("skills", nargs="*")
    ap.add_argument("--baseline", action="store_true")
    ap.add_argument("--model")
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--ids", help="comma-separated eval ids to run")
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    if not shutil.which("claude"):
        sys.exit("claude CLI not found on PATH")
    files = sorted(CASES.glob("*.json"))
    if args.skills:
        files = [f for f in files if f.stem in args.skills]
        unknown = set(args.skills) - {f.stem for f in files}
        if unknown:
            sys.exit(f"no eval cases for: {', '.join(sorted(unknown))}")

    wanted_ids = {int(i) for i in args.ids.split(",")} if args.ids else set()
    passed = total = 0
    for path in files:
        spec = json.loads(path.read_text(encoding="utf-8"))
        for case in spec.get("evals", []):
            if wanted_ids and case["id"] not in wanted_ids:
                continue
            total += 1
            label = f"{spec['skill_name']}#{case['id']}"
            try:
                answer = ask(case["prompt"], args.baseline, args.model, args.timeout)
            except (RuntimeError, subprocess.TimeoutExpired) as e:
                print(f"ERROR {label}: {e}")
                continue
            missing, forbidden = grade(answer, case)
            if missing or forbidden:
                print(f"FAIL  {label}: missing {missing} forbidden {forbidden}")
            else:
                passed += 1
                print(f"PASS  {label}")
            if args.out:
                args.out.mkdir(parents=True, exist_ok=True)
                status = "fail" if missing or forbidden else "pass"
                (args.out / f"{spec['skill_name']}-{case['id']}.{status}.md").write_text(answer, encoding="utf-8")

    mode = "baseline (no plugin)" if args.baseline else "with plugin"
    print(f"\n{passed}/{total} passed, {mode}")
    return 0 if total and passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
