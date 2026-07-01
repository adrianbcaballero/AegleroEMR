"""
Document generator for the Aeglero compliance engine.

Reads compliance/output/status.json (produced by run.py) and renders the two
artifacts an assessor actually lives in:

  * SSP.md   -- System Security Plan, structured after NIST SP 800-18 (system
               identification with FIPS 199 categorization, description, environment
               and boundary, applicable laws, control implementation, plan completion).
  * POAM.md  -- Plan of Action & Milestones using the standard FedRAMP/DoD column set
               (POA&M ID, weakness, detection source, severity, remediation, milestone,
               status). Also emitted as POAM.csv with the full column set for assessor
               tooling.

Usage:
    python compliance/generate_docs.py        # uses the latest status.json
"""

from __future__ import annotations

import csv
import json
import re
import shutil
from datetime import datetime, timedelta
from pathlib import Path

import oscal
import ssp_docx

HERE = Path(__file__).resolve().parent
OUTPUT_DIR = HERE / "output"
STATUS_PATH = OUTPUT_DIR / "status.json"
PROFILE_PATH = HERE / "system_profile.json"

SSP_PATH = OUTPUT_DIR / "SSP.md"
POAM_PATH = OUTPUT_DIR / "POAM.md"
POAM_CSV_PATH = OUTPUT_DIR / "POAM.csv"

DASHBOARD_DIR = HERE / "dashboard"
DASHBOARD_DATA_PATH = DASHBOARD_DIR / "data.js"
# Downloadable artifacts staged next to the dashboard so the export panel can
# serve them locally (file://) and from S3 once synced.
EXPORTS_DIR = DASHBOARD_DIR / "exports"

# Statuses that belong in the SSP (satisfied) vs the POA&M (open items).
SSP_STATUSES = {"met", "partial", "inherited", "na", "manual", "attested", "policy"}
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
    "attested": "Attested (implemented, automation pending)",
    "policy": "Satisfied by policy",
    "manual": "Satisfied by policy",
    "na": "Not applicable",
    "not-met": "Not implemented",
    "not-collected": "Not yet assessed",
    "error": "Assessment error",
}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


# Matches a repo file path with an optional ":line" suffix, e.g.
# "backend/services/audit_logger.py:9" or ".github/workflows/ci.yml".
_REF_RE = re.compile(r"^([\w.\-/]+\.\w+)(?::(\d+))?$")


def _gh_url(ref: str, base: str | None, branch: str) -> str | None:
    """Turn an evidence ref into a GitHub blob URL, or None if it isn't a file."""
    if not base:
        return None
    m = _REF_RE.match(ref or "")
    if not m:
        return None
    url = f"{base.rstrip('/')}/blob/{branch}/{m.group(1)}"
    if m.group(2):
        url += f"#L{m.group(2)}"
    return url


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
APPROVED_PATH = HERE / "approved_narratives.json"


def _load_approved() -> dict:
    """Human-approved AI narratives, keyed by control id. Empty if none."""
    try:
        return json.loads(APPROVED_PATH.read_text(encoding="utf-8")).get("narratives", {})
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _responsibility(status: str) -> str:
    """Who is responsible for a control, in SSP terms."""
    if status == "inherited":
        return "Cloud service provider (AWS), inherited"
    if status == "na":
        return "Not applicable"
    return "Aeglero (system owner)"


def render_ssp(report: dict, profile: dict) -> str:
    s = report["summary"]
    approved = _load_approved()
    lines: list[str] = []
    a = lines.append

    a(f"# System Security Plan (SSP): {profile['system_name']}")
    a("")
    a(f"> **Auto-generated** by the Aeglero compliance engine on "
      f"{report['generated_at']}. Do not hand-edit; regenerate from `status.json`.")
    a("")
    a("> Section structure follows NIST SP 800-18 (Guide for Developing Security Plans); "
      "control implementation follows NIST SP 800-171 Rev 2.")
    a("")
    a(f"_{profile['assessment_scope_note']}_")
    a("")

    # ---- 1. System identification -------------------------------------------
    a("## 1. System identification")
    a("")
    a(f"- **System name:** {profile['system_name']} ({profile.get('system_short_name', '')})")
    a(f"- **System categorization (FIPS 199):** {profile.get('categorization', 'Not categorized')}")
    a(f"- **System type:** {profile.get('system_type', '-')}")
    a(f"- **Operational status:** {profile.get('operational_status', '-')}")
    a(f"- **System owner:** {profile['owner']}")
    a(f"- **Authorizing official:** {profile.get('authorizing_official', '-')}")
    a(f"- **Assignment of security responsibility:** {profile.get('security_contact', '-')}")
    a(f"- **Version:** {profile.get('version', '-')}")
    a(f"- **Plan date:** {report['generated_at']}")
    a("")

    # ---- 2. System description and purpose ----------------------------------
    a("## 2. System description and purpose")
    a("")
    a(profile["description"])
    a("")
    a(f"- **Information types processed:** {', '.join(profile.get('data_types', []))}")
    a(f"- **Hosting:** {profile.get('hosting', '-')}")
    a("")

    # ---- 3. System environment and authorization boundary -------------------
    a("## 3. System environment and authorization boundary")
    a("")
    a(profile["authorization_boundary"])
    a("")

    # ---- 4. Applicable laws, regulations, and guidance ----------------------
    a("## 4. Applicable laws, regulations, and guidance")
    a("")
    a("**Binding laws and regulations.**")
    a("")
    for law in profile.get("applicable_laws", []) or ["Not specified."]:
        a(f"- {law}")
    a("")
    guidance = profile.get("guidance", [])
    if guidance:
        a("**Referenced guidance.**")
        a("")
        for g in guidance:
            a(f"- {g}")
        a("")
    note = profile.get("assessment_framework_note")
    if note:
        a(f"**Assessment framework.** {note}")
        a("")

    # ---- 5. Control implementation summary ----------------------------------
    a("## 5. Control implementation summary")
    a("")
    a(f"- **Framework:** {report['framework']}")
    a(f"- **SPRS score:** {s['sprs_score']} / {s['sprs_base']} "
      f"(-{s['points_deducted']}) - _{s['sprs_basis']}_")
    a(f"- **Automated evidence coverage:** {s['automated_coverage_pct']}% "
      f"({s['controls_with_evidence']} of {s['controls_applicable']} applicable controls)")
    a(f"- **Status breakdown:** {s['status_counts']}")
    a("")

    # ---- 6. Control implementation ------------------------------------------
    a("## 6. Control implementation")
    a("")
    implemented = [c for c in report["controls"] if c["status"] in SSP_STATUSES]
    if not implemented:
        a("_No implemented controls to report._")
    for c in implemented:
        f = c.get("finding") or {}
        a(f"### {c['id']}: {c['title']}")
        a("")
        a(f"- **Family:** {c['family']} ({c.get('family_name', '')})")
        a(f"- **Implementation status:** {STATUS_LABEL.get(c['status'], c['status'])}")
        a(f"- **Responsibility:** {_responsibility(c['status'])}")
        a(f"- **SPRS weight:** {c['sprs_weight']}")
        if f:
            a(f"- **Assessment method:** {f.get('method', 'EXAMINE')}")
            objs = ", ".join(f.get("objective_ids", [])) or "-"
            a(f"- **Objectives addressed:** {objs}")
            a("")
            appr = approved.get(c["id"])
            if appr:
                a(f"**Implementation statement** (drafted with AI assistance, reviewed "
                  f"and approved {appr.get('approved_at', '')}). {appr['statement']}")
            else:
                a(f"**Implementation statement.** {f.get('summary', '')}")
            a("")
            ev = f.get("evidence", [])
            if ev:
                a("**Evidence.**")
                base = profile.get("repo_url")
                branch = profile.get("repo_branch", "main")
                for e in ev:
                    ref = e.get("ref", "")
                    url = _gh_url(ref, base, branch)
                    ref_md = f"[`{ref}`]({url})" if url else f"`{ref}`"
                    a(f"- {ref_md}: {e.get('detail','')}")
                a("")
            a(f"**Provenance.** collected by `{f.get('collector','')}` at "
              f"{f.get('collected_at','')} · evidence SHA-256 "
              f"`{f.get('evidence_hash','')[:16]}…`")
        a("")

    # ---- 7. Plan completion --------------------------------------------------
    a("## 7. Plan completion")
    a("")
    a(f"- **Plan completion date:** {report['generated_at']}")
    a(f"- **Plan approval:** {profile.get('authorizing_official', '-')}")
    a("")
    return "\n".join(lines) + "\n"


# -------------------------------------------------------------------------- POA&M
def _severity(weight: int) -> str:
    """Map the SPRS point weight to a POA&M severity/risk rating."""
    return {5: "High", 3: "Moderate", 1: "Low"}.get(weight, "Moderate")


def _poam_rows(report: dict, profile: dict) -> list[dict]:
    """Build POA&M rows using the standard FedRAMP/DoD column set."""
    poc = profile.get("point_of_contact", profile.get("owner", "-"))
    asset = profile.get("system_short_name", profile.get("system_name", "-"))
    rows = []
    n = 0
    for c in report["controls"]:
        if c["status"] not in POAM_STATUSES:
            continue
        n += 1
        f = c.get("finding")
        weakness = (f.get("summary") if f
                    else "Control is not yet assessed by an automated collector.")
        detection = (f and f.get("method")) or "Self-assessment"
        source_id = "Self-assessment"
        if f and f.get("evidence"):
            source_id = f["evidence"][0].get("ref", "Self-assessment")
        rows.append({
            "poam_id": f"POAM-{n:03d}",
            "control_id": c["id"],
            "family": c["family"],
            "status_raw": c["status"],
            "status": "Ongoing" if c["status"] == "partial" else "Open",
            "weakness_name": f"{c['id']} {c['title']}",
            "weakness": weakness,
            "detection_source": detection,
            "source_identifier": source_id,
            "asset_identifier": asset,
            "point_of_contact": poc,
            "resources_required": "Engineering time; no additional budget required.",
            "severity": _severity(c["sprs_weight"]),
            "sprs_points": c["sprs_weight"],
            "remediation": _remediation_hint(f),
            "milestone": _milestone(report["generated_at"], c["status"]),
        })
    return rows


def render_poam(report: dict, profile: dict, rows: list[dict]) -> str:
    lines: list[str] = []
    a = lines.append
    points_at_risk = sum(r["sprs_points"] for r in rows)

    a(f"# Plan of Action & Milestones (POA&M): {profile['system_name']}")
    a("")
    a(f"> **Auto-generated** by the Aeglero compliance engine on "
      f"{report['generated_at']}. Regenerate from `status.json`.")
    a("")
    a("> Columns follow the standard FedRAMP/DoD POA&M structure. The full column set "
      "(point of contact, resources, source identifier, asset) is in `POAM.csv`.")
    a("")
    a(f"- **Open items:** {len(rows)}")
    a(f"- **SPRS points at risk:** {points_at_risk}")
    a("")
    a("A POA&M is a maturity signal, not a failure: it records known gaps with an "
      "owner and a milestone date. Items resolve automatically when their collector "
      "next reports the control as met.")
    a("")
    if not rows:
        a("_No open items. All cataloged controls are met._")
        return "\n".join(lines) + "\n"

    a("| POA&M ID | Control | Weakness | Detection source | Severity | Remediation plan | Scheduled completion | Status |")
    a("|----------|---------|----------|------------------|:--------:|------------------|:--------------------:|:------:|")
    for r in rows:
        weakness = r["weakness"].replace("|", "\\|")
        remediation = r["remediation"].replace("|", "\\|")
        a(f"| {r['poam_id']} | {r['control_id']} | {weakness} | {r['detection_source']} | "
          f"{r['severity']} | {remediation} | {r['milestone']} | {r['status']} |")
    return "\n".join(lines) + "\n"


def write_poam_csv(rows: list[dict], path: Path) -> None:
    # Column order mirrors the standard FedRAMP/DoD POA&M template.
    fields = [
        "poam_id", "control_id", "family", "weakness_name", "weakness",
        "detection_source", "source_identifier", "asset_identifier",
        "point_of_contact", "resources_required", "severity", "sprs_points",
        "remediation", "milestone", "status",
    ]
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
                f"{STATUS_PATH} not found; run `python compliance/run.py` first.")
        report = _load(STATUS_PATH)
    profile = _load(PROFILE_PATH)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    SSP_PATH.write_text(render_ssp(report, profile), encoding="utf-8")

    rows = _poam_rows(report, profile)
    POAM_PATH.write_text(render_poam(report, profile, rows), encoding="utf-8")
    write_poam_csv(rows, POAM_CSV_PATH)

    # Standard machine-readable exports: OSCAL SSP + POA&M.
    oscal_paths = oscal.generate(report, profile, rows)

    # Word SSP (optional: only if python-docx is installed).
    docx_path = ssp_docx.build(report, profile)

    # Stage the downloadable bundle next to the dashboard for the export panel.
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    exportable = [SSP_PATH, POAM_PATH, POAM_CSV_PATH, *oscal_paths]
    if docx_path:
        exportable.append(docx_path)
    for src in exportable:
        shutil.copyfile(src, EXPORTS_DIR / src.name)

    # Emit the report as a JS global so dashboard/index.html can load it from
    # the local filesystem (file://) without a server or fetch/CORS issues.
    DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
    report_for_js = dict(report)
    report_for_js["repo"] = {
        "url": profile.get("repo_url"),
        "branch": profile.get("repo_branch", "main"),
    }
    DASHBOARD_DATA_PATH.write_text(
        "// AUTO-GENERATED by generate_docs.py -- do not edit.\n"
        "window.COMPLIANCE_STATUS = " + json.dumps(report_for_js, indent=2) + ";\n",
        encoding="utf-8",
    )
    return [SSP_PATH, POAM_PATH, POAM_CSV_PATH, *oscal_paths,
            *( [docx_path] if docx_path else [] ), DASHBOARD_DATA_PATH]


def main() -> int:
    paths = generate()
    print("Generated:")
    for p in paths:
        print(f"  {p.relative_to(HERE.parent)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
