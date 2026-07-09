# Information Security Policy

**Status:** Draft
**Owner:** Security Officer (system owner acts in this role for the current deployment)
**Effective date:** 2026-07-08
**Review cycle:** Annual, or after any major architecture change or security incident
**Regulatory basis:** HIPAA Security Rule (45 CFR Part 164); NIST SP 800-171 Rev 2

## 1. Purpose

This is the top-level policy for Aeglero. It states the organization's commitment to protecting
the confidentiality, integrity, and availability of protected health information (PHI) and the
substance use disorder records covered by 42 CFR Part 2, and it establishes the policy hierarchy
that the more specific policies sit under.

## 2. Scope

This policy applies to the Aeglero application, the AWS infrastructure that hosts it, the source
code and CI/CD pipeline that build it, and every person who operates or maintains any of those.
Aeglero is assessed against NIST SP 800-171 Rev 2 as its assessment framework. NIST 800-171 is not
a legal obligation for a PHI system; it is used because it is quantifiable (SPRS) and crosswalks
cleanly to HIPAA, ONC, CMMC, and 42 CFR Part 2. The binding legal obligations are HIPAA and
42 CFR Part 2.

## 3. Policy

1. **Security program.** Security is treated as a first-class part of the system, not an add-on.
   Controls are implemented in code and infrastructure wherever possible and are assessed
   continuously by the compliance engine in `compliance/`.
2. **Policy hierarchy.** This policy is the parent document. The following policies inherit from it
   and govern their specific areas: Information Access Management, Workforce Security, Risk
   Management, Incident Response, Contingency Planning, and Device and Media Controls.
3. **Secure system design (3.13.2).** New features and infrastructure are designed with security in
   mind from the start: tenant isolation enforced at the schema and query layers, least privilege by
   default, defense in depth across the network tiers, and encryption in transit and at rest. The
   architecture is documented in `ARCHITECTURE.md` and `SECURITY.md`.
4. **Configuration and change management (3.4.3, 3.4.4).** All changes to application code,
   infrastructure, and CI configuration are made through version control. Every change goes through a
   pull request that runs the automated security gate (Bandit, pip-audit, Trivy, and Checkov) before
   it can merge. The security impact of a change is analyzed during that pull request review and by
   the scanner gate; a change that fails a scan is blocked from merging. Database changes are made
   through reversible Alembic migrations, and infrastructure changes are reviewed with
   `terraform plan` before apply.
5. **Audit log review (3.3.3).** The set of logged event types is reviewed at least annually and
   whenever a new feature introduces a meaningful state change, so that the audit log continues to
   cover every action that matters. The daily compliance run and its drift gate act as an automated
   check that audit coverage has not regressed.
6. **Security monitoring and advisories (3.14.3).** Security alerts and advisories are monitored and
   acted on. Dependency and container advisories are consumed automatically in CI by pip-audit and
   Trivy on every pull request. Platform advisories are monitored through AWS Health and GitHub
   security alerts. Relevant advisories are triaged and remediated on a risk-prioritized basis.
7. **Enforcement.** Violations of this policy or its child policies are handled under the Workforce
   Security Policy sanction process.

## 4. Roles and responsibilities

- **Security Officer.** Owns this policy and the security program, approves exceptions, and leads
  incident response.
- **Privacy Officer.** Owns PHI handling and 42 CFR Part 2 consent practices.
- **System operators.** Follow these policies and report suspected incidents.

In the current single-operator demonstration deployment, the system owner holds all three roles.
In a staffed organization these roles would be assigned to separate individuals to preserve
separation of duties.

## 5. Exceptions

Any exception to this policy must be documented with a reason, a compensating control, and an expiry
date, and approved by the Security Officer. Standing infrastructure scanner exceptions are recorded
in `docs/iac-scan-exceptions.md`.

## 6. Review and maintenance

This policy is reviewed at least annually and after any major change. The review date and outcome
are recorded in version control history.

## Control mapping

| Control | Title | How this policy addresses it |
|---|---|---|
| 3.13.2 | Security engineering in system design | Secure design principles (section 3.3) |
| 3.4.3 | Track, review, approve, audit changes | PR and CI gate process (section 3.4) |
| 3.4.4 | Analyze security impact of changes | Scanner gate and PR review (section 3.4) |
| 3.3.3 | Review and update logged events | Annual and event-driven audit review (section 3.5) |
| 3.14.3 | Monitor and act on security advisories | Automated and platform advisory monitoring (section 3.6) |

HIPAA basis: 45 CFR 164.308(a)(1) (security management), 164.316 (policies and documentation).
