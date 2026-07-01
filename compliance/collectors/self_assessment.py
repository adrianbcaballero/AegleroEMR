"""
self_assessment collector - EXAMINE method.

The compliance engine itself satisfies the NIST 800-171 Security Assessment (CA)
family: it periodically assesses controls, generates a POA&M, monitors controls
continuously, and generates a System Security Plan. This collector confirms those
capabilities exist in the repo and reports them as evidence.

Maps to:
  3.12.1 - periodically assess security controls  (run.py + collectors)
  3.12.2 - develop and implement a POA&M           (generate_docs.py -> POAM.md/.csv)
  3.12.3 - monitor controls on an ongoing basis    (scheduled compliance.yml workflow)
  3.12.4 - develop and maintain an SSP             (generate_docs.py -> SSP.md)
"""

from __future__ import annotations

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
            "This engine assesses every cataloged control on each run and on a schedule.",
            [Evidence("source-file", ENGINE, "run.py executes all collectors and scores the controls.")],
            ["3.12.1"]))

        f.append(self._mk(
            "3.12.2", docs,
            "A Plan of Action & Milestones is auto-generated from the assessment results.",
            [Evidence("source-file", DOCS, "generate_docs.py renders POAM.md and POAM.csv from status.json.")],
            ["3.12.2"]))

        f.append(self._mk(
            "3.12.3", workflow,
            "Controls are monitored continuously by a scheduled GitHub Actions workflow with a drift gate.",
            [Evidence("ci-pipeline", WORKFLOW, "compliance.yml re-runs the assessment daily and commits refreshed evidence.")],
            ["3.12.3"]))

        f.append(self._mk(
            "3.12.4", docs,
            "A System Security Plan is auto-generated from the control implementations.",
            [Evidence("source-file", DOCS, "generate_docs.py renders SSP.md from status.json.")],
            ["3.12.4"]))

        return f

    def _mk(self, cid, ok, summary, evidence, objs) -> Finding:
        if ok:
            return Finding(cid, STATUS_MET, METHOD_EXAMINE, summary,
                           objective_ids=objs, evidence=evidence)
        return Finding(cid, STATUS_NOT_MET, METHOD_EXAMINE,
                       "Expected engine component not found.", objective_ids=objs)
