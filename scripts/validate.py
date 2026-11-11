#!/usr/bin/env python3
"""Validate skills, agents, commands, eval cases, the rate table, links, README tables and manifests.

Usage: python3 scripts/validate.py   (exit 1 on any error; stdlib only)
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
WRITE_TOOLS = {"Bash", "Write", "Edit", "NotebookEdit", "MultiEdit"}
MAX_NAME, MAX_DESC = 64, 1024
STALE_DAYS = 180

errors = []
warnings = []


def err(path, msg):
    errors.append(f"{path.relative_to(ROOT)}: {msg}")


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        err(path, "missing frontmatter")
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        err(path, "unterminated frontmatter")
        return {}
    fields = {}
    for line in text[4:end].splitlines():
        m = re.match(r"^\s*([A-Za-z_-]+):\s*(.*)$", line)
        if m and m.group(1) not in fields:
            fields[m.group(1)] = m.group(2).strip().strip('"')
    return fields


def check_name_desc(path, fields, expected_name):
    name, desc = fields.get("name", ""), fields.get("description", "")
    if not NAME_RE.match(name) or len(name) > MAX_NAME:
        err(path, f"invalid name {name!r}")
    if name != expected_name:
        err(path, f"name {name!r} does not match file/dir {expected_name!r}")
    if not desc:
        err(path, "empty description")
    elif len(desc) > MAX_DESC:
        err(path, f"description is {len(desc)} chars (max {MAX_DESC})")


def check_links(path):
    for target in LINK_RE.findall(path.read_text(encoding="utf-8")):
        if re.match(r"^[a-z]+:", target) or target.startswith("#"):
            continue
        rel = target.split("#", 1)[0]
        if rel and not (path.parent / rel).exists():
            err(path, f"broken link {target}")


def main():
    skills = sorted(p for p in (ROOT / "skills").iterdir() if p.is_dir())
    agents = sorted((ROOT / "reviewers").glob("*.md"))
    if (ROOT / "agents").exists():
        err(ROOT / "agents", "Gemini CLI loads agents/ and rejects Claude tool names; keep reviewers in reviewers/")
    if not skills or not agents:
        err(ROOT / "README.md", "no skills or agents found")

    for d in skills:
        md = d / "SKILL.md"
        if not md.exists():
            err(d, "missing SKILL.md")
            continue
        fields = frontmatter(md)
        check_name_desc(md, fields, d.name)
        check_verified(md, fields, date.today())

    for md in agents:
        fields = frontmatter(md)
        check_name_desc(md, fields, md.stem)
        tools = {t.strip() for t in fields.get("tools", "").split(",") if t.strip()}
        if not tools:
            err(md, "agents must declare tools explicitly")
        if tools & WRITE_TOOLS:
            err(md, f"read-only agent grants {sorted(tools & WRITE_TOOLS)}")

    docs = ["README.md", "CONTRIBUTING.md", "CLAUDE.md", "AGENTS.md"]
    for md in [*(ROOT / d for d in docs), *(d / "SKILL.md" for d in skills), *agents]:
        if md.exists():
            check_links(md)

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for d in skills:
        if f"(skills/{d.name}/)" not in readme:
            err(ROOT / "README.md", f"skills table missing {d.name}")
    for md in agents:
        if f"(reviewers/{md.name})" not in readme:
            err(ROOT / "README.md", f"agents table missing {md.stem}")

    check_manifests()
    check_plugin_agents(agents)
    check_commands({md.stem for md in agents})
    check_evals({d.name for d in skills})
    check_rates({d.name for d in skills})
    check_agent_skill_refs(agents, {d.name for d in skills})

    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    print(f"{len(skills)} skills, {len(agents)} agents, {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


PLUGIN_MANIFESTS = [
    ".claude-plugin/plugin.json",
    ".codex-plugin/plugin.json",
    ".cursor-plugin/plugin.json",
    "gemini-extension.json",
]
MARKETPLACES = [".claude-plugin/marketplace.json", ".agents/plugins/marketplace.json"]


def load_json(rel):
    path = ROOT / rel
    if not path.exists():
        err(path.parent, f"missing {path.name}")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        err(path, f"invalid JSON: {e}")
        return None


def check_plugin_agents(agents):
    data = load_json(PLUGIN_MANIFESTS[0]) or {}
    listed = set(data.get("agents", []))
    expected = {f"./reviewers/{md.name}" for md in agents}
    for path in sorted(expected - listed):
        err(ROOT / PLUGIN_MANIFESTS[0], f"agents list missing {path}")
    for path in sorted(listed - expected):
        err(ROOT / PLUGIN_MANIFESTS[0], f"agents list names missing file {path}")


def check_manifests():
    """plugin.json under .claude-plugin is the version source of truth."""
    canonical = load_json(PLUGIN_MANIFESTS[0])
    if not canonical:
        return
    name, version = canonical.get("name"), canonical.get("version")
    for rel in PLUGIN_MANIFESTS[1:]:
        data = load_json(rel)
        if data and (data.get("name"), data.get("version")) != (name, version):
            err(ROOT / rel, f"name/version {data.get('name')}@{data.get('version')} != {name}@{version}")
    for rel in MARKETPLACES:
        data = load_json(rel)
        if not data:
            continue
        entries = [p for p in data.get("plugins", []) if p.get("name") == name]
        if not entries:
            err(ROOT / rel, f"no plugin entry named {name!r}")
        for entry in entries:
            if "version" in entry and entry["version"] != version:
                err(ROOT / rel, f"version {entry['version']} != {version}")


def check_verified(md, fields, today):
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", fields.get("verified", ""))
    if not m:
        err(md, 'metadata.verified must be "YYYY-MM-DD"')
        return
    age = (today - date(*map(int, m.groups()))).days
    if age > STALE_DAYS:
        warnings.append(f"{md.relative_to(ROOT)}: verified {age} days ago; re-check rates and dates")


def check_evals(skill_names):
    cases = ROOT / "evals" / "cases"
    for name in sorted(skill_names):
        path = cases / f"{name}.json"
        if not path.exists():
            err(cases, f"missing eval cases for {name}")
            continue
        try:
            spec = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            err(path, f"invalid JSON: {e}")
            continue
        if spec.get("skill_name") != name:
            err(path, f"skill_name {spec.get('skill_name')!r} != {name!r}")
        trig = spec.get("trigger", {})
        if len(trig.get("positive", [])) < 3 or len(trig.get("negative", [])) < 2:
            err(path, "need >= 3 positive and >= 2 negative trigger prompts")
        for neg in trig.get("negative", []):
            owner = neg.get("owner")
            if owner is not None and owner not in skill_names:
                err(path, f"negative trigger owner {owner!r} is not a skill")
        evals = spec.get("evals", [])
        if not 3 <= len(evals) <= 6:
            err(path, f"{len(evals)} evals (want 3 to 6)")
        ids = [e.get("id") for e in evals]
        if len(ids) != len(set(ids)):
            err(path, "duplicate eval ids")
        for e in evals:
            if not e.get("prompt") or not e.get("expectations"):
                err(path, f"eval {e.get('id')} needs prompt and expectations")
            for pattern in e.get("must_match", []) + e.get("must_not_match", []):
                try:
                    re.compile(pattern)
                except re.error as x:
                    err(path, f"eval {e.get('id')} bad regex {pattern!r}: {x}")
    for path in cases.glob("*.json"):
        if path.stem not in skill_names:
            err(path, "eval cases for a skill that does not exist")


def check_rates(skill_names):
    path = ROOT / "data" / "rates.json"
    data = load_json("data/rates.json")
    if not data:
        return
    ids = set()
    for r in data.get("rates", []):
        rid, owner, shown = r.get("id"), r.get("owner"), r.get("display")
        if rid in ids:
            err(path, f"duplicate rate id {rid!r}")
        ids.add(rid)
        if not isinstance(r.get("value"), (int, float)) or not r.get("source"):
            err(path, f"{rid}: needs a numeric value and a source")
        if owner not in skill_names:
            err(path, f"{rid}: owner {owner!r} is not a skill")
            continue
        if shown and shown not in (ROOT / "skills" / owner / "SKILL.md").read_text(encoding="utf-8"):
            err(path, f"{rid}: {shown!r} not found in {owner} (skill and table disagree)")


def check_agent_skill_refs(agents, skill_names):
    for md in agents:
        text = md.read_text(encoding="utf-8")
        m = re.search(r"## Load these skills first\n(.*?)\n## ", text, re.S)
        if not m:
            err(md, "missing '## Load these skills first' section")
            continue
        for ref in re.findall(r"(?<![A-Za-z0-9-])[a-z0-9]+(?:-[a-z0-9]+)+", m.group(1)):
            if ref not in skill_names:
                err(md, f"loads unknown skill {ref!r}")


def check_commands(agent_names):
    for md in sorted((ROOT / "commands").glob("*.md")):
        if not frontmatter(md).get("description"):
            err(md, "command missing description")
        for ref in re.findall(r"indian-market-skills:([a-z0-9-]+)", md.read_text(encoding="utf-8")):
            if ref not in agent_names:
                err(md, f"references unknown agent {ref!r}")


if __name__ == "__main__":
    sys.exit(main())
