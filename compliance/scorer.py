"""
SPRS scorer for the Aeglero compliance engine.

Implements the DoD Assessment Methodology scoring model: start at 110 and deduct
each unmet control's weight (1, 3, or 5). We report the score conservatively --
a control with no automated evidence yet ("not-collected") is treated as NOT
implemented, because under the DoD methodology you only get credit for controls
you can actually demonstrate.

Two numbers are reported:
  * sprs_score      -- conservative score over the CATALOGED controls.
  * automated_coverage -- share of applicable controls that have real evidence,
                          i.e. how much of the assessment is hands-off.

Because the seed catalog is a subset of the full 110 controls, sprs_basis makes
the partial-catalog caveat explicit so the number is never misread as a final,
full-scope SPRS score.
"""

from __future__ import annotations

from collections import Counter

from collectors.base import (
    STATUS_MET, STATUS_NOT_MET, STATUS_PARTIAL, STATUS_NA,
    STATUS_INHERITED, STATUS_ERROR, PASSING, EXCLUDED,
)

STATUS_NOT_COLLECTED = "not-collected"
SPRS_BASE = 110


def score(catalog: dict, findings_by_control: dict) -> dict:
    """
    catalog: parsed controls.json
    findings_by_control: {control_id: Finding-dict} for controls that were assessed
    Returns a scoring summary dict.
    """
    controls = catalog.get("controls", [])
    deductions = []
    status_counts: Counter = Counter()
    applicable = 0
    assessed_with_evidence = 0

    for ctrl in controls:
        cid = ctrl["id"]
        weight = int(ctrl.get("sprs_weight", 0))
        finding = findings_by_control.get(cid)
        status = finding["status"] if finding else STATUS_NOT_COLLECTED
        status_counts[status] += 1

        # Applicable-controls denominator excludes N/A and inherited.
        if status not in EXCLUDED:
            applicable += 1

        # Coverage: did we gather real evidence (met / not-met / partial)?
        if status in (STATUS_MET, STATUS_NOT_MET, STATUS_PARTIAL):
            assessed_with_evidence += 1

        # Deduct points for anything not passing.
        # not-collected and error both mean "can't claim credit" -> deduct.
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

    coverage = (round(assessed_with_evidence / applicable * 100, 1)
                if applicable else 0.0)

    return {
        "sprs_score": sprs_score,
        "sprs_base": SPRS_BASE,
        "points_deducted": total_deducted,
        "sprs_basis": (
            f"partial catalog ({len(controls)} of 110 controls seeded); "
            "score is conservative (unassessed = not implemented)"
        ),
        "automated_coverage_pct": coverage,
        "controls_total": len(controls),
        "controls_applicable": applicable,
        "controls_with_evidence": assessed_with_evidence,
        "status_counts": dict(status_counts),
        "deductions": sorted(deductions, key=lambda d: -d["points"]),
    }
