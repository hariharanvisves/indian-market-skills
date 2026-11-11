#!/usr/bin/env python3
"""Open one GitHub issue per row of docs/unverified-claims.md that has no issue yet.

Usage:
  python3 scripts/sync_issues.py            # dry run: print what would be created
  python3 scripts/sync_issues.py --apply    # create the issues (needs `gh auth login`)

Matching is by title, open or closed, so re-running never duplicates an issue.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "unverified-claims.md"
LABEL = "unverified-claim"
TITLE_MAX = 110


def parse_rows(text):
    section = None
    for line in text.splitlines():
        if line.startswith("## "):
            section = line[3:].strip()
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 4 or cells[0] in ("Skill", "") or set(cells[0]) <= set("-: "):
            continue
        skill, claim, status, source = cells
        yield section, skill.strip("`"), claim, status, source


def title_for(skill, claim):
    plain = re.sub(r"[`*]", "", claim)
    title = f"[{skill}] Verify: {plain}"
    return title if len(title) <= TITLE_MAX else title[: TITLE_MAX - 1].rstrip() + "…"


def body_for(section, skill, claim, status, source):
    return (
        f"**Skill:** [`{skill}`](../blob/main/skills/{skill}/SKILL.md)  \n"
        f"**Area:** {section}\n\n"
        f"**Claim:** {claim}\n\n"
        f"**Current status:** {status}\n\n"
        f"**Primary source to check:** {source}\n\n"
        "To close this, comment with a primary-source link (statute, gazette, CBDT, SEBI, "
        "exchange or AMFI circular, or a broker's published schedule) that confirms or "
        "corrects the claim, or open a PR that updates the skill and removes the row from "
        "`docs/unverified-claims.md`. See CONTRIBUTING.md for the sourcing rule."
    )


def gh(*args):
    return subprocess.run(["gh", *args], capture_output=True, text=True, check=True).stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    rows = list(parse_rows(DOC.read_text(encoding="utf-8")))
    existing = set()
    if args.apply:
        gh("label", "create", LABEL, "--color", "ff9933", "--description",
           "Claim waiting on a primary source", "--force")
        listed = gh("issue", "list", "--label", LABEL, "--state", "all", "--limit", "1000", "--json", "title")
        existing = {i["title"] for i in json.loads(listed)}

    created = skipped = 0
    for section, skill, claim, status, source in rows:
        title = title_for(skill, claim)
        if title in existing:
            skipped += 1
            continue
        if args.apply:
            url = gh("issue", "create", "--title", title, "--label", LABEL,
                     "--body", body_for(section, skill, claim, status, source)).strip()
            print(f"created {url}")
        else:
            print(f"would create: {title}")
        created += 1
    verb = "created" if args.apply else "to create"
    print(f"\n{len(rows)} claims, {created} {verb}, {skipped} already open")
    return 0


if __name__ == "__main__":
    sys.exit(main())
