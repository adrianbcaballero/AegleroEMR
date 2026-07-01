"""
Drift detection + SPRS gate for the Aeglero compliance engine.

Compares a freshly generated status.json against the previous one and fails
(non-zero exit) if posture regressed or the SPRS score fell below a minimum.
Used by the scheduled GitHub Actions run so a drop in compliance posture blocks
the run and surfaces an alert, rather than silently rotting between audits.

Usage:
    python compliance/check_drift.py --old prev.json --new compliance/output/status.json
    COMPLIANCE_MIN_SPRS=100 python compliance/check_drift.py --new compliance/output/status.json
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

# Statuses that count as "passing" (a move away from these is a regression).
PASSING = {"met", "na", "inherited"}


def _load(path: str | None) -> dict | None:
    if not path:
        return None
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def _status_map(report: dict) -> dict:
    return {c["id"]: c["status"] for c in report.get("controls", [])}


def main() -> int:
    ap = argparse.ArgumentParser(description="Compliance drift + SPRS gate")
    ap.add_argument("--old", help="previous status.json (baseline); optional")
    ap.add_argument("--new", required=True, help="freshly generated status.json")
    ap.add_argument("--min-sprs", type=int,
                    default=int(os.environ.get("COMPLIANCE_MIN_SPRS", "90")))
    args = ap.parse_args()

    new = _load(args.new)
    if new is None:
        print(f"ERROR: could not read new status file: {args.new}")
        return 2

    new_score = int(new["summary"]["sprs_score"])
    fail = False

    print(f"SPRS score: {new_score}  (gate: >= {args.min_sprs})")
    if new_score < args.min_sprs:
        print(f"  GATE FAIL: SPRS {new_score} is below the minimum {args.min_sprs}.")
        fail = True

    old = _load(args.old)
    if old is None:
        print("No previous baseline found - establishing baseline, skipping drift check.")
    else:
        old_score = int(old["summary"]["sprs_score"])
        delta = new_score - old_score
        print(f"Previous SPRS: {old_score}  (delta: {delta:+d})")

        old_map, new_map = _status_map(old), _status_map(new)
        regressions, improvements = [], []
        for cid, ns in new_map.items():
            os_ = old_map.get(cid)
            if os_ is None:
                continue
            if os_ in PASSING and ns not in PASSING:
                regressions.append((cid, os_, ns))
            elif os_ not in PASSING and ns in PASSING:
                improvements.append((cid, os_, ns))

        for cid, o, n in improvements:
            print(f"  improved: {cid}  {o} -> {n}")
        for cid, o, n in regressions:
            print(f"  REGRESSION: {cid}  {o} -> {n}")

        if delta < 0:
            print(f"  DRIFT: SPRS decreased by {-delta} point(s).")
            fail = True
        if regressions:
            print(f"  DRIFT: {len(regressions)} control(s) regressed from a passing state.")
            fail = True
        if not fail:
            print("No posture regression detected.")

    print("RESULT:", "FAIL" if fail else "PASS")
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
