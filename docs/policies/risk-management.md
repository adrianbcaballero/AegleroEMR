# Risk Management Policy

**Status:** Draft
**Owner:** Security Officer (system owner acts in this role for the current deployment)
**Effective date:** 2026-07-08
**Review cycle:** Annual; risk assessed on an ongoing basis and re-assessed on defined triggers
**Regulatory basis:** HIPAA 45 CFR 164.308(a)(1); NIST SP 800-30, NIST SP 800-171 Rev 2

## 1. Purpose

This policy defines how Aeglero identifies, assesses, and manages risk to PHI and to the systems that
support it, so that risk decisions are deliberate and recorded rather than implicit.

## 2. Scope

This policy covers the Aeglero application, its AWS infrastructure, its data, its vendors that touch
PHI, and its build pipeline.

## 3. Policy

### 3.1 Periodic risk assessment (3.11.1)

Risk to organizational operations, assets, and individuals is assessed periodically. A full Risk
Analysis is performed at least annually following the NIST SP 800-30 approach: identify assets and
data flows, identify threats and vulnerabilities, determine likelihood and impact, and record the
resulting risk level. The current analysis is maintained in `docs/risk-analysis.md`.

### 3.2 Continuous risk monitoring

Between formal analyses, risk is monitored continuously rather than only at a point in time. The
compliance engine runs daily, re-derives control evidence, and fails its run if posture drifts down
or the SPRS score falls below the gate. Dependency and infrastructure scanners run on every change.
These automated signals feed the risk picture and can trigger an interim assessment.

### 3.3 Asset and data inventory

An inventory of systems, data types, and the vendors that process PHI is maintained and kept current.
The vendor inventory and third-party risk ratings are recorded in `docs/vendor-register.md`.

### 3.4 Risk register and treatment

Identified risks are recorded in a risk register with a description, likelihood, impact, current
controls, and a treatment decision. Treatment options are to remediate, mitigate with a compensating
control, transfer, or formally accept. Open gaps that are accepted for now are tracked as POA&M items
in the compliance output so they are visible and time-bound rather than forgotten.

### 3.5 Triggers for an interim risk assessment

An interim Risk Analysis is performed, outside the annual cycle, when any of the following occur:

- A major architecture or infrastructure change.
- Onboarding a new vendor that will handle PHI.
- A Sev1 or Sev2 security incident.
- A significant change in the threat environment relevant to the system.

### 3.6 Decision authority

The Security Officer owns risk treatment decisions and records the rationale. Acceptance of a
material risk is documented with an owner and a review date.

## 4. Roles and responsibilities

- **Security Officer.** Owns the risk process, the register, and treatment decisions.
- **System operators.** Surface new risks as they are observed.

In the current single-operator deployment the system owner performs these roles. In a staffed
organization, risk acceptance for material risks would require review by someone other than the
person proposing it.

## 5. Review and maintenance

Reviewed at least annually and on any trigger in section 3.5. Reviews and register updates are
recorded in version control.

## Control mapping

| Control | Title | How this policy addresses it |
|---|---|---|
| 3.11.1 | Periodically assess risk to operations, assets, and individuals | Annual analysis plus continuous monitoring and triggers (sections 3.1, 3.2, 3.5) |

HIPAA basis: 45 CFR 164.308(a)(1)(ii)(A) (risk analysis), 164.308(a)(1)(ii)(B) (risk management).
