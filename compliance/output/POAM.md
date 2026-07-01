# Plan of Action & Milestones (POA&M) — Aeglero EMR

> **Auto-generated** by the Aeglero compliance engine on 2026-07-01T00:39:08+00:00. Regenerate from `status.json`.

- **Open items:** 3
- **SPRS points at risk:** 13

A POA&M is a maturity signal, not a failure: it records known gaps with an owner and a milestone date. Items resolve automatically when their collector next reports the control as met.

| # | Control | Status | Weakness | SPRS pts | Detected by | Remediation / milestone | Scheduled completion |
|---|---------|--------|----------|:-------:|-------------|-------------------------|----------------------|
| 1 | 3.13.8 | Not yet assessed | Control is not yet assessed by an automated collector. | 5 | — | No automated evidence is collected for this control yet. Implement or extend a collector so its status is proven continuously (see GOALS.md). | 2026-08-30 |
| 2 | 3.13.11 | Not yet assessed | Control is not yet assessed by an automated collector. | 3 | — | No automated evidence is collected for this control yet. Implement or extend a collector so its status is proven continuously (see GOALS.md). | 2026-08-30 |
| 3 | 3.11.2 | Partially implemented | Vulnerability scanning (pip-audit (Python deps), Trivy (containers/IaC/deps), Checkov (IaC compliance), pnpm audit (JS deps)) runs on every push/PR, but not on a fixed schedule, so newly disclosed CVEs in unchanged dependencies are not caught until the next commit. | 5 | EXAMINE | add a scheduled (cron) scan to satisfy 3.11.2[d] for newly identified vulnerabilities. | 2026-07-31 |
