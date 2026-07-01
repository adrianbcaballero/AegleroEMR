"""
Runner for the Aeglero continuous-compliance engine.

Usage:
    python compliance/run.py

Runs every registered collector against the repo, merges the findings with the
control catalog, scores the result (SPRS), and writes compliance/output/status.json.
Prints a human-readable summary to the console.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Make sibling modules importable whether run as a script or a module.
HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from collectors import ALL_COLLECTORS
from collectors.base import CollectorContext, utc_now_iso
import scorer
import generate_docs

REPO_ROOT = HERE.parent
CATALOG_PATH = HERE / "catalog" / "controls.json"
OUTPUT_PATH = HERE / "output" / "status.json"


def load_catalog() -> dict:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def run_collectors(now_iso: str) -> list:
    ctx = CollectorContext(repo_root=REPO_ROOT, now_iso=now_iso)
    findings = []
    for collector in ALL_COLLECTORS:
        try:
            results = collector.collect(ctx)
        except Exception as exc:  # a broken collector must not sink the run
            print(f"  ! collector '{collector.name}' raised: {exc}")
            continue
        for f in results:
            f.finalize(collector.name, now_iso)
            findings.append(f)
    return findings


def build_report(catalog: dict, findings: list, now_iso: str) -> dict:
    findings_by_control = {f.control_id: f.to_dict() for f in findings}
    summary = scorer.score(catalog, findings_by_control)

    # Per-control view merging catalog metadata with the finding (or "not-collected").
    controls_view = []
    for ctrl in catalog.get("controls", []):
        cid = ctrl["id"]
        finding = findings_by_control.get(cid)
        controls_view.append({
            "id": cid,
            "family": ctrl.get("family"),
            "family_name": ctrl.get("family_name"),
            "title": ctrl.get("title"),
            "sprs_weight": ctrl.get("sprs_weight"),
            "status": finding["status"] if finding else "not-collected",
            "finding": finding,
        })

    return {
        "generated_at": now_iso,
        "framework": catalog.get("framework"),
        "scoring_model": catalog.get("scoring_model"),
        "summary": summary,
        "controls": controls_view,
    }


def print_summary(report: dict) -> None:
    s = report["summary"]
    print("\n=== Aeglero Compliance -- SPRS summary ===")
    print(f"  Framework        : {report['framework']}")
    print(f"  Generated (UTC)  : {report['generated_at']}")
    print(f"  SPRS score       : {s['sprs_score']} / {s['sprs_base']}  "
          f"(-{s['points_deducted']})")
    print(f"  Basis            : {s['sprs_basis']}")
    print(f"  Automated cover. : {s['automated_coverage_pct']}% "
          f"({s['controls_with_evidence']}/{s['controls_applicable']} applicable)")
    print(f"  Status breakdown : {s['status_counts']}")
    print("\n  Per-control:")
    for c in report["controls"]:
        mark = {"met": "PASS", "not-met": "FAIL", "partial": "PART",
                "na": "N/A", "inherited": "INH", "error": "ERR",
                "not-collected": "----"}.get(c["status"], "?")
        print(f"    [{mark:>4}] {c['id']:<8} ({c['family']}) {c['title'][:60]}")
    print()


def main() -> int:
    now_iso = utc_now_iso()
    catalog = load_catalog()
    findings = run_collectors(now_iso)
    report = build_report(catalog, findings, now_iso)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print_summary(report)
    print(f"  Wrote {OUTPUT_PATH.relative_to(REPO_ROOT)}")

    # Render the assessor artifacts (SSP + POA&M) from the same report.
    doc_paths = generate_docs.generate(report)
    for p in doc_paths:
        print(f"  Wrote {p.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
