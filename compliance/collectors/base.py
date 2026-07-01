"""
Collector framework for the Aeglero continuous-compliance engine.

A *collector* gathers evidence for one or more NIST 800-171 controls from a real
source (source code, a running API, an AWS account, a CI run) and returns a list
of Findings. Each Finding is scored later by scorer.py.

Design goals:
  - Evidence is traceable: every Finding carries a source reference, a collection
    timestamp, and a SHA-256 hash of its evidence payload (provenance you can prove
    wasn't backdated -- mirroring Aeglero's own hash-chained audit log).
  - Collectors are honest: a collector that cannot reach its source returns an
    ERROR finding, never a fake "met".
  - Methods map to NIST 800-171A assessment methods: EXAMINE, TEST, INTERVIEW.
"""

from __future__ import annotations

import hashlib
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path

# ---- Finding status values ---------------------------------------------------
STATUS_MET = "met"                 # control satisfied; evidence present
STATUS_NOT_MET = "not-met"         # control assessed and NOT satisfied
STATUS_PARTIAL = "partial"         # partially satisfied
STATUS_NA = "na"                   # not applicable (with rationale)
STATUS_INHERITED = "inherited"     # satisfied by an external provider (e.g. AWS)
STATUS_ATTESTED = "attested"       # implemented in the app; collector pending (attested)
STATUS_POLICY = "policy"           # satisfied by an org policy/procedure document
STATUS_MANUAL = "manual"           # legacy alias (kept for back-compat)
STATUS_NOT_COLLECTED = "not-collected"  # automated control with no collector yet
STATUS_ERROR = "error"             # collector could not gather evidence

# Statuses that mean "satisfied" (retain SPRS points).
PASSING = {STATUS_MET, STATUS_NA, STATUS_INHERITED, STATUS_MANUAL,
           STATUS_ATTESTED, STATUS_POLICY}
# Statuses excluded from the "applicable controls" denominator (N/A doesn't apply;
# inherited is provided by someone else). Manual IS applicable (you satisfy it).
EXCLUDED = {STATUS_NA, STATUS_INHERITED}

# ---- NIST 800-171A assessment methods ---------------------------------------
METHOD_EXAMINE = "EXAMINE"
METHOD_TEST = "TEST"
METHOD_INTERVIEW = "INTERVIEW"


@dataclass
class Evidence:
    """A single piece of proof backing a Finding."""
    kind: str            # e.g. "source-file", "api-response", "aws-config"
    ref: str             # e.g. "backend/services/audit_logger.py:8"
    detail: str          # human-readable description of what this proves


@dataclass
class Finding:
    """The assessment result for one control, produced by a collector."""
    control_id: str
    status: str
    method: str
    summary: str
    evidence: list[Evidence] = field(default_factory=list)
    objective_ids: list[str] = field(default_factory=list)
    collector: str = ""
    collected_at: str = ""       # ISO-8601 UTC, filled in by the runner
    evidence_hash: str = ""      # SHA-256 over the evidence, filled in by the runner

    def rehash(self) -> "Finding":
        """Recompute the evidence hash (call after mutating evidence, e.g. a merge)."""
        payload = json.dumps(
            [asdict(e) for e in self.evidence],
            sort_keys=True,
            separators=(",", ":"),
        )
        self.evidence_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        return self

    def finalize(self, collector_name: str, now_iso: str) -> "Finding":
        """Stamp provenance fields. Called by the runner after collect()."""
        self.collector = collector_name
        self.collected_at = now_iso
        return self.rehash()

    def to_dict(self) -> dict:
        d = asdict(self)
        return d


@dataclass
class CollectorContext:
    """Everything a collector needs to run. Passed in by the runner."""
    repo_root: Path
    now_iso: str


class Collector(ABC):
    """Base class for all evidence collectors."""

    #: unique short name, e.g. "audit_chain"
    name: str = "unnamed"
    #: control IDs this collector produces evidence for
    provides: list[str] = []
    #: default assessment method for this collector
    method: str = METHOD_EXAMINE

    @abstractmethod
    def collect(self, ctx: CollectorContext) -> list[Finding]:
        """Gather evidence and return one Finding per control in `provides`."""
        raise NotImplementedError

    # -- small helpers shared by collectors ------------------------------------

    @staticmethod
    def grep(path: Path, needle: str) -> list[tuple[int, str]]:
        """Return (line_number, line_text) for every line containing `needle`."""
        hits: list[tuple[int, str]] = []
        try:
            for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if needle in line:
                    hits.append((i, line.strip()))
        except (OSError, UnicodeDecodeError):
            pass
        return hits


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
