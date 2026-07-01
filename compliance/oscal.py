"""
OSCAL export for the Aeglero compliance engine.

Emits NIST OSCAL JSON for the two artifacts the engine already renders as Markdown,
so the same assessment is available in the standard, tool-interoperable format that
GRC platforms (eMASS and others) ingest:

  * output/oscal-ssp.json   -- OSCAL system-security-plan model
  * output/oscal-poam.json  -- OSCAL plan-of-action-and-milestones model

OSCAL (Open Security Controls Assessment Language) is NIST's machine-readable
standard for security documentation. See https://pages.nist.gov/OSCAL/.

UUIDs are derived deterministically (uuid5 over stable seeds) rather than randomly,
so the same control always maps to the same UUID across runs. Only the timestamp
changes between runs, which avoids spurious UUID churn in the evidence artifact.
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUTPUT_DIR = HERE / "output"
OUT_SSP = OUTPUT_DIR / "oscal-ssp.json"
OUT_POAM = OUTPUT_DIR / "oscal-poam.json"

OSCAL_VERSION = "1.1.2"
_NS = uuid.uuid5(uuid.NAMESPACE_URL, "https://aeglero.com/oscal")

# Engine status -> OSCAL implementation-status property value.
IMPL_STATUS = {
    "met": "implemented",
    "attested": "implemented",
    "policy": "implemented",
    "inherited": "implemented",
    "partial": "partial",
    "na": "not-applicable",
    "not-met": "planned",
    "not-collected": "planned",
    "error": "planned",
}


def _uuid(seed: str) -> str:
    """Deterministic UUID from a stable seed, so output is reproducible."""
    return str(uuid.uuid5(_NS, seed))


def _metadata(title: str, profile: dict, generated_at: str) -> dict:
    return {
        "title": title,
        "last-modified": generated_at,
        "version": profile.get("version", "1.0"),
        "oscal-version": OSCAL_VERSION,
        "roles": [{"id": "system-owner", "title": "System Owner"}],
        "parties": [{
            "uuid": _uuid("party:owner"),
            "type": "organization",
            "name": profile.get("owner", "System Owner"),
        }],
        "responsible-parties": [{
            "role-id": "system-owner",
            "party-uuids": [_uuid("party:owner")],
        }],
        "props": [{"name": "generated-by", "value": "Aeglero compliance engine"}],
    }


def _this_system_component(profile: dict) -> dict:
    return {
        "uuid": _uuid("component:this-system"),
        "type": "this-system",
        "title": profile["system_name"],
        "description": profile["description"],
        "status": {"state": "operational"},
    }


def build_oscal_ssp(report: dict, profile: dict) -> dict:
    generated_at = report["generated_at"]
    system_id = profile.get("system_short_name", "aeglero-emr").lower()

    implemented = []
    for c in report["controls"]:
        f = c.get("finding") or {}
        req = {
            "uuid": _uuid(f"impl-req:{c['id']}"),
            "control-id": c["id"],
            "props": [
                {"name": "implementation-status",
                 "value": IMPL_STATUS.get(c["status"], "planned")},
                {"name": "control-name", "value": c.get("title", "")},
            ],
        }
        if f.get("summary"):
            req["remarks"] = f["summary"]
        implemented.append(req)

    return {
        "system-security-plan": {
            "uuid": _uuid("ssp:root"),
            "metadata": _metadata(
                f"System Security Plan: {profile['system_name']}", profile, generated_at),
            "import-profile": {"href": "https://csrc.nist.gov/pubs/sp/800/171/r2/upd1/final"},
            "system-characteristics": {
                "system-ids": [{"id": system_id}],
                "system-name": profile["system_name"],
                "description": profile["description"],
                "security-sensitivity-level": "high",
                "system-information": {
                    "information-types": [{
                        "uuid": _uuid("information-type:phi"),
                        "title": "Protected Health Information and 42 CFR Part 2 records",
                        "description": ", ".join(profile.get("data_types", [])),
                        "confidentiality-impact": {"base": "fips-199-high"},
                        "integrity-impact": {"base": "fips-199-moderate"},
                        "availability-impact": {"base": "fips-199-moderate"},
                    }],
                },
                "security-impact-level": {
                    "security-objective-confidentiality": "fips-199-high",
                    "security-objective-integrity": "fips-199-moderate",
                    "security-objective-availability": "fips-199-moderate",
                },
                "status": {"state": "operational"},
                "authorization-boundary": {"description": profile["authorization_boundary"]},
            },
            "system-implementation": {
                "users": [{
                    "uuid": _uuid("user:system-owner"),
                    "title": profile.get("owner", "System owner"),
                    "role-ids": ["system-owner"],
                }],
                "components": [_this_system_component(profile)],
            },
            "control-implementation": {
                "description": (
                    f"NIST SP 800-171 Rev 2 control implementation as assessed by the "
                    f"Aeglero compliance engine. SPRS {report['summary']['sprs_score']} of "
                    f"{report['summary']['sprs_base']}."),
                "implemented-requirements": implemented,
            },
        }
    }


def build_oscal_poam(report: dict, profile: dict, rows: list[dict]) -> dict:
    generated_at = report["generated_at"]
    system_id = profile.get("system_short_name", "aeglero-emr").lower()

    poam_items = []
    for r in rows:
        poam_items.append({
            "uuid": _uuid(f"poam-item:{r['control_id']}"),
            "title": r["weakness_name"],
            "description": r["weakness"],
            "props": [
                {"name": "control-id", "value": r["control_id"]},
                {"name": "severity", "value": r["severity"]},
                {"name": "scheduled-completion-date", "value": r["milestone"]},
                {"name": "status", "value": r["status"]},
                {"name": "detection-source", "value": r["detection_source"]},
            ],
        })

    return {
        "plan-of-action-and-milestones": {
            "uuid": _uuid("poam:root"),
            "metadata": _metadata(
                f"Plan of Action and Milestones: {profile['system_name']}",
                profile, generated_at),
            "system-id": {"id": system_id},
            "local-definitions": {"components": [_this_system_component(profile)]},
            "poam-items": poam_items,
        }
    }


def generate(report: dict, profile: dict, rows: list[dict]) -> list[Path]:
    """Write both OSCAL documents; return the paths written."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_SSP.write_text(json.dumps(build_oscal_ssp(report, profile), indent=2) + "\n",
                       encoding="utf-8")
    OUT_POAM.write_text(json.dumps(build_oscal_poam(report, profile, rows), indent=2) + "\n",
                        encoding="utf-8")
    return [OUT_SSP, OUT_POAM]
