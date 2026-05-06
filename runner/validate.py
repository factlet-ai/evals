"""Validate Tier 1 task YAML files against the schema.

Run this in CI to keep tasks well-formed before they get committed.

Schema rules (per tier1/task-schema.md):
  - Required fields: id, domain, factbook, query, expected_behavior,
    risk_if_wrong
  - id must match {domain}-{NNN}-{slug}
  - factbook path must resolve under tier1/factbooks/
  - expected_behavior.must_cite + must_not_contradict ids must exist in
    the referenced factbook
  - risk_if_wrong in {low, medium, high}
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

ID_RE = re.compile(r"^[a-z][a-z0-9-]*-\d{3}-[a-z0-9-]+$")
DOMAIN_RE = re.compile(r"^[a-z][a-z0-9-]*$")
RISK = {"low", "medium", "high"}
REQUIRED = {"id", "domain", "factbook", "query", "expected_behavior", "risk_if_wrong"}


def load_factbook_ids(factbook_root: Path, rel: str) -> set[str]:
    fb = yaml.safe_load((factbook_root / rel).read_text())
    return {f["id"] for f in fb["content"]}


def validate_task(task_path: Path, factbook_root: Path) -> list[str]:
    errs: list[str] = []
    try:
        t = yaml.safe_load(task_path.read_text())
    except Exception as e:
        return [f"{task_path}: YAML parse error: {e}"]

    missing = REQUIRED - set(t.keys())
    if missing:
        errs.append(f"{task_path}: missing required fields: {sorted(missing)}")
        return errs

    if not ID_RE.match(t["id"]):
        errs.append(f"{task_path}: id '{t['id']}' must match {{domain}}-{{NNN}}-{{slug}}")

    if not DOMAIN_RE.match(t["domain"]):
        errs.append(f"{task_path}: domain '{t['domain']}' must be lowercase kebab")

    fb_path = factbook_root / t["factbook"]
    if not fb_path.exists():
        errs.append(f"{task_path}: factbook '{t['factbook']}' not found at {fb_path}")
        return errs

    fb_ids = load_factbook_ids(factbook_root, t["factbook"])
    eb = t["expected_behavior"]
    for field in ("must_cite", "must_not_contradict"):
        for fid in eb.get(field, []) or []:
            if fid not in fb_ids:
                errs.append(f"{task_path}: expected_behavior.{field}: {fid} not in factbook {t['factbook']}")

    if t["risk_if_wrong"] not in RISK:
        errs.append(f"{task_path}: risk_if_wrong '{t['risk_if_wrong']}' must be one of {sorted(RISK)}")

    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", required=True)
    ap.add_argument("--factbooks", required=True)
    args = ap.parse_args()

    tasks_root = Path(args.tasks)
    factbook_root = Path(args.factbooks)
    all_errs: list[str] = []
    n = 0
    for p in sorted(tasks_root.rglob("*.yaml")):
        n += 1
        all_errs.extend(validate_task(p, factbook_root))

    if all_errs:
        for e in all_errs:
            print(f"ERROR: {e}")
        print(f"\n{len(all_errs)} validation error(s) across {n} task file(s).")
        sys.exit(1)
    print(f"OK — {n} task file(s) validated.")


if __name__ == "__main__":
    main()
