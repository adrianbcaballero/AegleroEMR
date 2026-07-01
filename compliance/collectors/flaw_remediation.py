"""
flaw_remediation collector — EXAMINE method.

Proves Aeglero scans for vulnerabilities and gates merges on the results, by
examining the CI pipeline definition. No cloud creds or running services needed.

Maps to:
  3.11.2 - scan for vulnerabilities periodically and when new ones are identified
           (pip-audit, Trivy fs, pnpm audit run on every push/PR)
  3.14.1 - identify, report, and correct system flaws in a timely manner
           (Bandit SAST + scanners report flaws; Trivy exit-code 1 BLOCKS the
            merge, forcing correction before code lands)

Nuance recorded honestly: CI runs on push/PR, not on a fixed schedule, so newly
disclosed CVEs in *unchanged* dependencies aren't caught until the next commit.
That is why 3.11.2 is reported PARTIAL, not MET -- and it becomes a POA&M item.
"""

from __future__ import annotations

from .base import (
    Collector, CollectorContext, Finding, Evidence,
    STATUS_MET, STATUS_PARTIAL, STATUS_NOT_MET, STATUS_ERROR, METHOD_EXAMINE,
)

CI_SRC = ".github/workflows/ci.yml"


class FlawRemediationCollector(Collector):
    name = "flaw_remediation"
    provides = ["3.11.2", "3.14.1"]
    method = METHOD_EXAMINE

    def collect(self, ctx: CollectorContext) -> list[Finding]:
        ci_path = ctx.repo_root / CI_SRC
        if not ci_path.exists():
            return [self._error(cid, f"CI pipeline not found: {CI_SRC}")
                    for cid in self.provides]

        text = ci_path.read_text(encoding="utf-8").lower()

        # Detect the scanners and the triggers.
        scanners = {
            "Bandit (SAST)": "bandit" in text,
            "pip-audit (Python deps)": "pip-audit" in text,
            "Trivy (containers/IaC/deps)": "trivy" in text,
            "Checkov (IaC compliance)": "checkov" in text,
            "pnpm audit (JS deps)": "pnpm audit" in text,
        }
        present = [name for name, ok in scanners.items() if ok]

        runs_on_push = "push" in text
        runs_on_pr = "pull_request" in text
        runs_on_schedule = "schedule:" in text or "cron:" in text
        gates_merge = "exit-code 1" in text or "--exit-code 1" in text

        findings: list[Finding] = []

        # --- 3.14.1: flaws identified, reported, corrected timely -----------
        if present and gates_merge:
            findings.append(Finding(
                control_id="3.14.1",
                status=STATUS_MET,
                method=METHOD_EXAMINE,
                summary=("System flaws are identified by " + ", ".join(present) +
                         "; findings gate the pipeline (exit-code 1), forcing "
                         "correction before code merges."),
                objective_ids=["3.14.1[b]", "3.14.1[c]"],
                evidence=[
                    Evidence("ci-pipeline", CI_SRC,
                             f"{len(present)} scanners configured: {', '.join(present)}."),
                    Evidence("ci-pipeline", CI_SRC,
                             "A HIGH/CRITICAL finding fails the build (exit-code 1), "
                             "blocking merge until the flaw is corrected."),
                ],
            ))
        elif present:
            findings.append(Finding(
                control_id="3.14.1",
                status=STATUS_PARTIAL,
                method=METHOD_EXAMINE,
                summary=("Flaws are scanned by " + ", ".join(present) +
                         ", but the pipeline does not hard-fail on findings, so "
                         "correction is not enforced."),
                objective_ids=["3.14.1[b]"],
                evidence=[Evidence("ci-pipeline", CI_SRC,
                                   "Scanners run but no merge-blocking gate detected.")],
            ))
        else:
            findings.append(self._not_met("3.14.1", "No flaw scanners found in CI."))

        # --- 3.11.2: vulnerability scanning ---------------------------------
        vuln_scanners = [n for n in present if any(
            k in n.lower() for k in ("pip-audit", "trivy", "pnpm", "checkov"))]
        triggers = []
        if runs_on_push:
            triggers.append("push")
        if runs_on_pr:
            triggers.append("pull_request")
        if runs_on_schedule:
            triggers.append("schedule")

        if vuln_scanners and runs_on_schedule:
            findings.append(Finding(
                control_id="3.11.2",
                status=STATUS_MET,
                method=METHOD_EXAMINE,
                summary=("Vulnerability scanning runs on a defined schedule and on "
                         "every change via " + ", ".join(vuln_scanners) + "."),
                objective_ids=["3.11.2[a]", "3.11.2[d]"],
                evidence=[Evidence("ci-pipeline", CI_SRC,
                                   f"Triggers: {', '.join(triggers)}.")],
            ))
        elif vuln_scanners and (runs_on_push or runs_on_pr):
            findings.append(Finding(
                control_id="3.11.2",
                status=STATUS_PARTIAL,
                method=METHOD_EXAMINE,
                summary=("Vulnerability scanning (" + ", ".join(vuln_scanners) +
                         ") runs on every push/PR, but not on a fixed schedule, so "
                         "newly disclosed CVEs in unchanged dependencies are not "
                         "caught until the next commit."),
                objective_ids=["3.11.2[a]"],
                evidence=[
                    Evidence("ci-pipeline", CI_SRC,
                             f"Scan frequency defined by triggers: {', '.join(triggers)}."),
                    Evidence("ci-pipeline", CI_SRC,
                             "POA&M: add a scheduled (cron) scan to satisfy 3.11.2[d] "
                             "for newly identified vulnerabilities."),
                ],
            ))
        else:
            findings.append(self._not_met("3.11.2", "No dependency/vuln scanners in CI."))

        return findings

    # -- helpers ---------------------------------------------------------------

    def _not_met(self, cid: str, why: str) -> Finding:
        return Finding(control_id=cid, status=STATUS_NOT_MET,
                       method=METHOD_EXAMINE, summary=why)

    def _error(self, cid: str, why: str) -> Finding:
        return Finding(control_id=cid, status=STATUS_ERROR,
                       method=METHOD_EXAMINE, summary=why)
