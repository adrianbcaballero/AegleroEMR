"""
SPRS scorer for the Aeglero compliance engine.

DoD Assessment Methodology: start at 110 and deduct each unmet control's weight
(1, 3, or 5). A control is "satisfied" (no deduction) when its status is met, N/A,
inherited (provider-supplied), or manual (policy-backed). Only not-met, partial,
not-collected, and error deduct.

Two headline numbers:
  * sprs_score        -- 110 minus deductions.
  * automated_coverage -- of the controls that are SUPPOSED to be automated
                          (type == "automated"), how many actually have collector
                          evidence. This measures how hands-off the assessment is,
                          separately from whether the control is satisfied.

Because the catalog may be a partial subset of the full 110, sprs_basis states that.
"""

from __future__ import annotations

from collections import Counter

from collectors.base import (
    STATUS_MET, STATUS_NOT_MET, STATUS_PARTIAL, STATUS_NA,
    STATUS_INHERITED, STATUS_MANUAL, STATUS_NOT_COLLECTED, STATUS_ERROR,
    PASSING, EXCLUDED,
)

SPRS_BASE = 110
# Statuses backed by real collector evidence (vs a catalog-declared disposition).
EVIDENCED = {STATUS_MET, STATUS_NOT_MET, STATUS_PARTIAL}


def score(catalog: dict, findings_by_control: dict) -> dict:
    controls = catalog.get("controls", [])
    deductions = []
    status_counts: Counter = Counter()
    type_counts: Counter = Counter()
    applicable = 0
    automated_total = 0
    automated_with_evidence = 0

    for ctrl in controls:
        cid = ctrl["id"]
        weight = int(ctrl.get("sprs_weight", 0))
        ctype = ctrl.get("type", "automated")
        finding = findings_by_control.get(cid)
        status = finding["status"] if finding else STATUS_NOT_COLLECTED

        status_counts[status] += 1
        type_counts[ctype] += 1

        if status not in EXCLUDED:
            applicable += 1

        if ctype == "automated":
            automated_total += 1
            if status in EVIDENCED:
                automated_with_evidence += 1

        # Deduct for anything not satisfied.
        if status not in PASSING:
            deductions.append({
                "control_id": cid,
                "status": status,
                "points": weight,
                "reason": (finding["summary"] if finding
                           else "No automated evidence collected yet."),
            })

    total_deducted = sum(d["points"] for d in deductions)
    sprs_score = SPRS_BASE - total_deducted

    # Automation reach: of the controls that apply (excluding N/A and provider-
    # inherited), how many are backed by a real collector rather than attested.
    coverage = (round(automated_with_evidence / applicable * 100, 1)
                if applicable else 0.0)

    return {
        "sprs_score": sprs_score,
        "sprs_base": SPRS_BASE,
        "points_deducted": total_deducted,
        "sprs_basis": (
            f"catalog covers {len(controls)} of 110 controls; "
            "unsatisfied controls deduct their DoD weight"
        ),
        "automated_coverage_pct": coverage,
        "controls_total": len(controls),
        "controls_applicable": applicable,
        "controls_with_evidence": automated_with_evidence,
        "automated_total": automated_total,
        "status_counts": dict(status_counts),
        "type_counts": dict(type_counts),
        "deductions": sorted(deductions, key=lambda d: -d["points"]),
    }
