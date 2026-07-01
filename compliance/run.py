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


def _merge_findings(existing, new):
    """Fold a later collector's finding for the same control into the earlier one.

    TEST (live) evidence corroborates EXAMINE (config) evidence. If a conclusive
    live TEST disagrees with the config (e.g. Terraform says encrypted but the
    running resource is not), that is drift -> the control is downgraded and flagged.
    """
    from collectors.base import STATUS_MET, STATUS_PARTIAL, STATUS_NOT_MET

    existing.evidence = list(existing.evidence) + list(new.evidence)

    def _labels(*vals):
        out = []
        for v in vals:
            for part in (v or "").split("+"):
                p = part.strip()
                if p and p not in out:
                    out.append(p)
        return out

    existing.method = " + ".join(_labels(existing.method, new.method))
    if new.collector and new.collector not in existing.collector:
        existing.collector = f"{existing.collector}+{new.collector}"
    for o in new.objective_ids:
        if o not in existing.objective_ids:
            existing.objective_ids.append(o)

    if new.status == STATUS_NOT_MET and existing.status in (STATUS_MET, STATUS_PARTIAL):
        existing.status = STATUS_NOT_MET
        existing.summary = "DRIFT (live TEST disagrees with configuration): " + new.summary
    elif new.status == STATUS_MET and existing.status == STATUS_MET:
        existing.summary = existing.summary + " Confirmed live via TEST method."

    return existing.rehash()


def run_collectors(now_iso: str) -> list:
    ctx = CollectorContext(repo_root=REPO_ROOT, now_iso=now_iso)
    by_control: dict = {}
    order: list = []
    for collector in ALL_COLLECTORS:
        try:
            results = collector.collect(ctx)
        except Exception as exc:  # a broken collector must not sink the run
            print(f"  ! collector '{collector.name}' raised: {exc}")
            continue
        for f in results:
            f.finalize(collector.name, now_iso)
            if f.control_id in by_control:
                _merge_findings(by_control[f.control_id], f)
            else:
                by_control[f.control_id] = f
                order.append(f.control_id)
    return [by_control[cid] for cid in order]


def _disposition_finding(ctrl: dict, now_iso: str) -> dict:
    """Synthesize a finding for a control with no collector, from its catalog type.

    - inherited: satisfied by the provider (AWS) -> no collector needed
    - manual:    satisfied by an org policy/procedure document
    - na:        not applicable, with rationale
    - automated: technical control that SHOULD have a collector; if none yet ->
                 not-collected (an honest POA&M item)
    """
    ctype = ctrl.get("type", "automated")
    rationale = ctrl.get("rationale", "")
    ref = ctrl.get("evidence_ref")
    if ctype == "inherited":
        status, method = "inherited", "INHERITED"
        summary = rationale or ("Inherited from the cloud service provider (AWS); "
                                "evidenced by provider attestations (SOC 2 / FedRAMP).")
    elif ctype == "attested":
        status, method = "attested", "ATTESTED"
        summary = rationale or ("Implemented in the application; an automated collector "
                                "for this control is a roadmap item.")
    elif ctype in ("policy", "manual"):
        status, method = "policy", "POLICY"
        summary = rationale or "Satisfied by organizational policy/procedure (see docs/policies/)."
    elif ctype == "na":
        status, method = "na", "N/A"
        summary = rationale or "Not applicable to this system."
    else:  # automated with no collector yet
        status, method = "not-collected", None
        summary = "No automated evidence collected yet; a collector is pending (POA&M)."
    evidence = [{"kind": "reference", "ref": ref, "detail": summary}] if ref else []
    return {
        "control_id": ctrl["id"], "status": status, "method": method,
        "summary": summary, "evidence": evidence, "objective_ids": [],
        "collector": "catalog", "collected_at": now_iso, "evidence_hash": "",
    }


def build_report(catalog: dict, findings: list, now_iso: str) -> dict:
    real = {f.control_id: f.to_dict() for f in findings}

    # Every control gets a finding: the real collector one, or a synthesized
    # disposition based on the catalog's `type`.
    findings_by_control = {}
    for ctrl in catalog.get("controls", []):
        cid = ctrl["id"]
        findings_by_control[cid] = real.get(cid) or _disposition_finding(ctrl, now_iso)

    summary = scorer.score(catalog, findings_by_control)

    controls_view = []
    for ctrl in catalog.get("controls", []):
        cid = ctrl["id"]
        finding = findings_by_control[cid]
        controls_view.append({
            "id": cid,
            "family": ctrl.get("family"),
            "family_name": ctrl.get("family_name"),
            "title": ctrl.get("title"),
            "sprs_weight": ctrl.get("sprs_weight"),
            "type": ctrl.get("type", "automated"),
            "mappings": ctrl.get("mappings", {}),
            "status": finding["status"],
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
