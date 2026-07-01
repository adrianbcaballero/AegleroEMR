"""
Document generator for the Aeglero compliance engine.

Reads compliance/output/status.json (produced by run.py) and renders the two
artifacts an assessor actually lives in:

  * SSP.md   -- System Security Plan: per-control implementation statements with
               cited evidence, for every control that is met/partial/inherited/na.
  * POAM.md  -- Plan of Action & Milestones: every control that is not fully met,
               with weakness, source, points at risk, remediation, and a milestone
               date. Also emitted as POAM.csv for spreadsheet/assessor tooling.

Usage:
    python compliance/generate_docs.py        # uses the latest status.json
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUTPUT_DIR = HERE / "output"
STATUS_PATH = OUTPUT_DIR / "status.json"
PROFILE_PATH = HERE / "system_profile.json"

SSP_PATH = OUTPUT_DIR / "SSP.md"
POAM_PATH = OUTPUT_DIR / "POAM.md"
POAM_CSV_PATH = OUTPUT_DIR / "POAM.csv"

# Statuses that belong in the SSP (implemented) vs the POA&M (open items).
SSP_STATUSES = {"met", "partial", "inherited", "na"}
POAM_STATUSES = {"not-met", "partial", "not-collected", "error"}

# Days-to-remediate by severity, used to set milestone dates.
MILESTONE_DAYS = {
    "not-met": 30,
    "partial": 30,
    "error": 15,
    "not-collected": 60,
}

STATUS_LABEL = {
    "met": "Implemented",
    "partial": "Partially implemented",
    "inherited": "Inherited (provider)",
    "na": "Not applicable",
    "not-met": "Not implemented",
    "not-collected": "Not yet assessed",
    "error": "Assessment error",
}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _remediation_hint(finding: dict | None) -> str:
    """Prefer an explicit 'POA&M:' note left by a collector; else a default."""
    if finding:
        for ev in finding.get("evidence", []):
            detail = ev.get("detail", "")
            if detail.strip().lower().startswith("poa&m:"):
                return detail.split(":", 1)[1].strip()
        return "Remediate the weakness described, then re-run the collector to confirm."
    return ("No automated evidence is collected for this control yet. Implement or "
            "extend a collector so its status is proven continuously (see GOALS.md).")


def _milestone(generated_at: str, status: str) -> str:
    base = datetime.fromisoformat(generated_at)
    days = MILESTONE_DAYS.get(status, 30)
    return (base + timedelta(days=days)).date().isoformat()


# --------------------------------------------------------------------------- SSP
def render_ssp(report: dict, profile: dict) -> str:
    s = report["summary"]
    lines: list[str] = []
    a = lines.append

    a(f"# System Security Plan (SSP) — {profile['system_name']}")
    a("")
    a(f"> **Auto-generated** by the Aeglero compliance engine on "
      f"{report['generated_at']}. Do not hand-edit; regenerate from `status.json`.")
    a("")
    a(f"_{profile['assessment_scope_note']}_")
    a("")

    a("## 1. System identification")
    a("")
    a(f"- **System name:** {profile['system_name']} ({profile['system_short_name']})")
    a(f"- **Version:** {profile['version']}")
    a(f"- **System owner:** {profile['owner']}")
    a(f"- **Hosting:** {profile['hosting']}")
    a(f"- **Information types:** {', '.join(profile['data_types'])}")
    a("")
    a(f"**Description.** {profile['description']}")
    a("")
    a("## 2. Authorization boundary")
    a("")
    a(profile["authorization_boundary"])
    a("")

    a("## 3. Control implementation summary")
    a("")
    a(f"- **Framework:** {report['framework']}")
    a(f"- **SPRS score:** {s['sprs_score']} / {s['sprs_base']} "
      f"(−{s['points_deducted']}) — _{s['sprs_basis']}_")
    a(f"- **Automated evidence coverage:** {s['automated_coverage_pct']}% "
      f"({s['controls_with_evidence']} of {s['controls_applicable']} applicable controls)")
    a(f"- **Status breakdown:** {s['status_counts']}")
    a("")

    a("## 4. Control implementation details")
    a("")
    implemented = [c for c in report["controls"] if c["status"] in SSP_STATUSES]
    if not implemented:
        a("_No implemented controls to report._")
    for c in implemented:
        f = c.get("finding") or {}
        a(f"### {c['id']} — {c['title']}")
        a("")
        a(f"- **Family:** {c['family']} ({c.get('family_name', '')})")
        a(f"- **Status:** {STATUS_LABEL.get(c['status'], c['status'])}")
        a(f"- **SPRS weight:** {c['sprs_weight']}")
        if f:
            a(f"- **Assessment method:** {f.get('method', 'EXAMINE')}")
            objs = ", ".join(f.get("objective_ids", [])) or "—"
            a(f"- **Objectives addressed:** {objs}")
            a("")
            a(f"**Implementation statement.** {f.get('summary', '')}")
            a("")
            ev = f.get("evidence", [])
            if ev:
                a("**Evidence.**")
                for e in ev:
                    a(f"- `{e.get('ref','')}` — {e.get('detail','')}")
                a("")
            a(f"**Provenance.** collected by `{f.get('collector','')}` at "
              f"{f.get('collected_at','')} · evidence SHA-256 "
              f"`{f.get('evidence_hash','')[:16]}…`")
        a("")
    return "\n".join(lines) + "\n"


# -------------------------------------------------------------------------- POA&M
def _poam_rows(report: dict) -> list[dict]:
    rows = []
    n = 0
    for c in report["controls"]:
        if c["status"] not in POAM_STATUSES:
            continue
        n += 1
        f = c.get("finding")
        weakness = (f.get("summary") if f
                    else "Control is not yet assessed by an automated collector.")
        method = (f.get("method") if f else "—")
        rows.append({
            "item": n,
            "control_id": c["id"],
            "family": c["family"],
            "status": c["status"],
            "status_label": STATUS_LABEL.get(c["status"], c["status"]),
            "weakness": weakness,
            "sprs_points": c["sprs_weight"],
            "detection": method,
            "remediation": _remediation_hint(f),
            "milestone": _milestone(report["generated_at"], c["status"]),
        })
    return rows


def render_poam(report: dict, profile: dict, rows: list[dict]) -> str:
    lines: list[str] = []
    a = lines.append
    points_at_risk = sum(r["sprs_points"] for r in rows)

    a(f"# Plan of Action & Milestones (POA&M) — {profile['system_name']}")
    a("")
    a(f"> **Auto-generated** by the Aeglero compliance engine on "
      f"{report['generated_at']}. Regenerate from `status.json`.")
    a("")
    a(f"- **Open items:** {len(rows)}")
    a(f"- **SPRS points at risk:** {points_at_risk}")
    a("")
    a("A POA&M is a maturity signal, not a failure: it records known gaps with an "
      "owner and a milestone date. Items resolve automatically when their collector "
      "next reports the control as met.")
    a("")
    if not rows:
        a("_No open items — all cataloged controls are met._")
        return "\n".join(lines) + "\n"

    a("| # | Control | Status | Weakness | SPRS pts | Detected by | Remediation / milestone | Scheduled completion |")
    a("|---|---------|--------|----------|:-------:|-------------|-------------------------|----------------------|")
    for r in rows:
        weakness = r["weakness"].replace("|", "\\|")
        remediation = r["remediation"].replace("|", "\\|")
        a(f"| {r['item']} | {r['control_id']} | {r['status_label']} | {weakness} | "
          f"{r['sprs_points']} | {r['detection']} | {remediation} | {r['milestone']} |")
    return "\n".join(lines) + "\n"


def write_poam_csv(rows: list[dict], path: Path) -> None:
    fields = ["item", "control_id", "family", "status", "weakness",
              "sprs_points", "detection", "remediation", "milestone"]
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def generate(report: dict | None = None) -> list[Path]:
    """Generate SSP + POA&M from the report (or the latest status.json)."""
    if report is None:
        if not STATUS_PATH.exists():
            raise FileNotFoundError(
                f"{STATUS_PATH} not found — run `python compliance/run.py` first.")
        report = _load(STATUS_PATH)
    profile = _load(PROFILE_PATH)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    SSP_PATH.write_text(render_ssp(report, profile), encoding="utf-8")

    rows = _poam_rows(report)
    POAM_PATH.write_text(render_poam(report, profile, rows), encoding="utf-8")
    write_poam_csv(rows, POAM_CSV_PATH)
    return [SSP_PATH, POAM_PATH, POAM_CSV_PATH]


def main() -> int:
    paths = generate()
    print("Generated:")
    for p in paths:
        print(f"  {p.relative_to(HERE.parent)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
