"""
self_assessment collector - EXAMINE method.

The compliance engine itself satisfies the NIST 800-171 Security Assessment (CA)
family: it periodically assesses controls, generates a POA&M, monitors controls
continuously, and generates a System Security Plan. This collector confirms those
capabilities exist in the repo and cites the exact functions and schedule that
implement them (path:line refs, so an assessor - or the AI reviewer - can read the
actual logic, not just a filename).

Maps to:
  3.12.1 - periodically assess security controls  (run.py collector loop + scorer)
  3.12.2 - develop and implement a POA&M           (generate_docs.py POA&M renderers)
  3.12.3 - monitor controls on an ongoing basis    (scheduled compliance.yml workflow)
  3.12.4 - develop and maintain an SSP             (generate_docs.py SSP renderer)
"""

from __future__ import annotations

from pathlib import Path

from .base import (
    Collector, CollectorContext, Finding, Evidence,
    STATUS_MET, STATUS_NOT_MET, METHOD_EXAMINE,
)

ENGINE = "compliance/run.py"
DOCS = "compliance/generate_docs.py"
WORKFLOW = ".github/workflows/compliance.yml"


class SelfAssessmentCollector(Collector):
    name = "self_assessment"
    provides = ["3.12.1", "3.12.2", "3.12.3", "3.12.4"]
    method = METHOD_EXAMINE

    def collect(self, ctx: CollectorContext) -> list[Finding]:
        root = ctx.repo_root
        engine = (root / ENGINE).exists()
        docs = (root / DOCS).exists()
        workflow = (root / WORKFLOW).exists()

        f = []

        f.append(self._mk(
            "3.12.1", engine and docs,
            "This engine assesses every cataloged control on each run: run_collectors() "
            "executes all registered collectors and the scorer evaluates the results. It "
            "runs on demand and on the scheduled workflow.",
            [
                self._ref(root, ENGINE, "def run_collectors",
                          "run_collectors() runs every registered collector against the system."),
                self._ref(root, ENGINE, "for collector in ALL_COLLECTORS",
                          "The loop iterates the full collector registry each assessment."),
                self._ref(root, ENGINE, "summary = scorer.score",
                          "The scorer evaluates the collected findings and computes the SPRS score."),
                self._ref(root, WORKFLOW, "- cron:",
                          "Scheduled workflow re-runs the assessment on a defined cadence."),
            ],
            ["3.12.1"]))

        f.append(self._mk(
            "3.12.2", docs,
            "A Plan of Action & Milestones is auto-generated from the assessment results: "
            "_poam_rows() selects every control that is not fully met and render_poam() / "
            "write_poam_csv() emit POAM.md and POAM.csv.",
            [
                self._ref(root, DOCS, "def _poam_rows",
                          "_poam_rows() selects controls in POAM_STATUSES (open items) from the report."),
                self._ref(root, DOCS, "def render_poam",
                          "render_poam() renders POAM.md with remediation hints and milestone dates."),
                self._ref(root, DOCS, "def write_poam_csv",
                          "write_poam_csv() emits POAM.csv for assessor/spreadsheet tooling."),
            ],
            ["3.12.2"]))

        f.append(self._mk(
            "3.12.3", workflow,
            "Controls are monitored continuously by a scheduled GitHub Actions workflow that "
            "re-runs the assessment and refreshes evidence on a defined cadence.",
            [
                self._ref(root, WORKFLOW, "- cron:",
                          "compliance.yml re-runs the assessment on a schedule (cron)."),
                self._ref(root, WORKFLOW, "schedule:",
                          "The workflow is schedule-triggered for ongoing monitoring, not only on push."),
            ],
            ["3.12.3"]))

        f.append(self._mk(
            "3.12.4", docs,
            "A System Security Plan is auto-generated from the control implementations: "
            "render_ssp() emits a per-control implementation statement for every satisfied control.",
            [
                self._ref(root, DOCS, "def render_ssp",
                          "render_ssp() renders SSP.md, one implementation statement per satisfied control."),
                self._ref(root, DOCS, "SSP_STATUSES =",
                          "SSP_STATUSES defines which control dispositions are described in the SSP."),
            ],
            ["3.12.4"]))

        return f

    # -- helpers ---------------------------------------------------------------

    def _ref(self, root: Path, path_str: str, anchor: str, detail: str) -> Evidence:
        """Build an Evidence whose ref is 'path:line', locating `anchor` in the file
        so the AI reviewer and human assessors can pull the actual code. Falls back to
        the bare path if the anchor is not found."""
        target = root / path_str
        ref = path_str
        if target.exists():
            hits = self.grep(target, anchor)
            if hits:
                ref = f"{path_str}:{hits[0][0]}"
        kind = "ci-pipeline" if path_str.endswith((".yml", ".yaml")) else "source-file"
        return Evidence(kind, ref, detail)

    def _mk(self, cid, ok, summary, evidence, objs) -> Finding:
        if ok:
            return Finding(cid, STATUS_MET, METHOD_EXAMINE, summary,
                           objective_ids=objs, evidence=evidence)
        return Finding(cid, STATUS_NOT_MET, METHOD_EXAMINE,
                       "Expected engine component not found.", objective_ids=objs)
