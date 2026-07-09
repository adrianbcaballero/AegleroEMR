# Security Incident Response Policy

**Status:** Draft
**Owner:** Security Officer (system owner acts in this role for the current deployment)
**Effective date:** 2026-07-08
**Review cycle:** Annual; the response capability is tested at least annually
**Regulatory basis:** HIPAA 45 CFR 164.308(a)(6), 164.404 (breach notification); NIST SP 800-171 Rev 2

## 1. Purpose

This policy establishes Aeglero's capability to detect, respond to, contain, and recover from
security incidents, and to track and report them. It defines what counts as an incident, how
incidents are handled, and how the capability is tested.

## 2. Scope

This policy covers security events affecting the Aeglero application, its AWS infrastructure, its
data, and its build pipeline.

## 3. Policy

### 3.1 Incident-handling capability (3.6.1)

Aeglero maintains an operational incident-handling capability with defined phases: preparation,
detection and analysis, containment, eradication, recovery, and post-incident review. This policy
plus the incident runbook in `docs/runbooks/` constitute that capability.

### 3.2 What is an incident

A security incident is any event that actually or potentially compromises the confidentiality,
integrity, or availability of PHI or of the systems that support it. Examples include unauthorized
access, credential compromise, tampering with the audit log, malware, denial of service, or exposure
of data. A breach is an incident that results in unauthorized acquisition, access, use, or
disclosure of PHI as defined under HIPAA.

### 3.3 Severity classification

Incidents are classified to drive response urgency:

- **Sev1 (critical).** Confirmed or likely exposure of PHI, active compromise, or loss of a core
  function.
- **Sev2 (high).** Contained compromise with no confirmed PHI exposure, or a control failure that
  materially increases risk.
- **Sev3 (moderate or low).** Suspicious activity or a minor control gap with limited impact.

### 3.4 Detection sources

Incidents are detected from: CloudTrail (API and console activity), GuardDuty threat detection in the
production profile, the tamper-evident audit log and its verification endpoint (`GET /api/audit/verify`,
which reports whether the hash chain is intact), the CI security scanners (Bandit, pip-audit, Trivy,
Checkov), the daily compliance drift gate, and AWS Health and GitHub security alerts.

### 3.5 Response phases

1. **Detect and analyze.** Confirm the event, classify severity, and open an incident record.
2. **Contain.** Limit the blast radius. Depending on the incident this may mean locking affected
   accounts (which ends their sessions immediately), rotating credentials, revoking a machine role,
   or isolating a resource.
3. **Eradicate.** Remove the cause, for example a vulnerable dependency, a misconfiguration, or an
   unauthorized change.
4. **Recover.** Restore normal operation from a known good state, using the Contingency Plan where a
   restore is required, and verify integrity before returning to service.
5. **Post-incident review.** Document the timeline, root cause, and corrective actions, and feed
   improvements back into controls and policies.

### 3.6 Tracking, documentation, and reporting (3.6.2)

Every incident is tracked in an incident record from detection through closure, capturing the
timeline, severity, affected data and systems, actions taken, and outcome. Incidents that meet the
definition of a breach are reported in line with the HIPAA breach notification requirements under
45 CFR 164.404, including notification without unreasonable delay and no later than 60 days after
discovery.

### 3.7 Testing the capability (3.6.3)

The incident response capability is tested at least annually, through a tabletop exercise or a
simulated incident, to confirm that detection sources, containment actions, and recovery steps work
as intended. Findings from each test are recorded and used to update this policy and the runbook.

## 4. Roles and responsibilities

- **Security Officer.** Leads response, classifies severity, and makes notification decisions.
- **System operators.** Report suspected incidents promptly and assist with containment and recovery.

In the current single-operator deployment the system owner performs all response roles. In a staffed
organization these would separate into an incident lead, a communications owner, and technical
responders.

## 5. Review and maintenance

Reviewed at least annually and after any Sev1 or Sev2 incident. Test results and reviews are recorded
in version control.

## Control mapping

| Control | Title | How this policy addresses it |
|---|---|---|
| 3.6.1 | Establish an operational incident-handling capability | Defined phases and runbook (sections 3.1, 3.5) |
| 3.6.2 | Track, document, and report incidents | Incident records and breach reporting (section 3.6) |
| 3.6.3 | Test the incident response capability | Annual test requirement (section 3.7) |

HIPAA basis: 45 CFR 164.308(a)(6) (security incident procedures), 164.404 (breach notification).
