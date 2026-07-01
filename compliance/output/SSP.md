# System Security Plan (SSP): Aeglero EMR

> **Auto-generated** by the Aeglero compliance engine on 2026-07-01T08:47:48+00:00. Do not hand-edit; regenerate from `status.json`.

_Aeglero is a HIPAA-scoped healthcare system; its real regulatory obligation is HIPAA + 42 CFR Part 2. This document maps Aeglero's existing controls to NIST SP 800-171 Rev 2 to DEMONSTRATE continuous-compliance automation. Aeglero is not a federal CUI system and this is not an official assessment artifact._

## 1. System identification

- **System name:** Aeglero EMR (Aeglero)
- **Version:** 1.0
- **System owner:** Aeglero (demonstration system)
- **Hosting:** Amazon Web Services (ECS Fargate, RDS Multi-AZ, CloudFront, S3, KMS, Secrets Manager, Route 53)
- **Information types:** Protected Health Information (PHI), HIPAA Security Rule, Substance Use Disorder records, 42 CFR Part 2

**Description.** Multi-tenant electronic medical record (EMR) platform for residential addiction and behavioral-health treatment programs. Provides bed management, episode-based clinical records, a documentation builder, consent management, and a tamper-evident audit log.

## 2. Authorization boundary

AWS: CloudFront (edge) -> Application Load Balancer -> ECS Fargate (Flask/Python API) -> RDS PostgreSQL in an isolated subnet with no internet route. Static frontend bundle served from S3 via Origin Access Control. Secrets in AWS Secrets Manager; encryption via four customer-managed KMS keys.

## 3. Control implementation summary

- **Framework:** NIST SP 800-171 Rev 2
- **SPRS score:** 105 / 110 (-5) - _catalog covers 110 of 110 controls; unsatisfied controls deduct their DoD weight_
- **Automated evidence coverage:** 17.1% (14 of 82 applicable controls)
- **Status breakdown:** {'met': 13, 'attested': 46, 'policy': 22, 'na': 15, 'inherited': 13, 'partial': 1}

## 4. Control implementation details

### 3.1.1: Limit system access to authorized users and processes.

- **Family:** AC (Access Control)
- **Status:** Implemented
- **SPRS weight:** 5
- **Assessment method:** EXAMINE
- **Objectives addressed:** 3.1.1[e]

**Implementation statement.** All protected routes require authentication via the require_auth decorator; unauthenticated requests are rejected.

**Evidence.**
- [`backend/auth_middleware.py:47`](https://github.com/adrianbcaballero/AegleroEMR/blob/main/backend/auth_middleware.py#L47): require_auth() authenticates the session before the handler runs.

**Provenance.** collected by `access_control` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `c052f0e419b984d4…`

### 3.1.2: Limit system access to permitted transactions and functions.

- **Family:** AC (Access Control)
- **Status:** Implemented
- **SPRS weight:** 5
- **Assessment method:** EXAMINE
- **Objectives addressed:** 3.1.2[b]

**Implementation statement.** RBAC restricts each route to a required permission (has_permission), and patient visibility is further limited to a user's care teams (_apply_rbac).

**Evidence.**
- [`backend/auth_middleware.py:71`](https://github.com/adrianbcaballero/AegleroEMR/blob/main/backend/auth_middleware.py#L71): require_auth(permission=...) enforces per-route permission.
- [`backend/routes/patients.py:148`](https://github.com/adrianbcaballero/AegleroEMR/blob/main/backend/routes/patients.py#L148): _apply_rbac() limits patient rows to the caller's care teams.

**Provenance.** collected by `access_control` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `e03f1d4c6bf4772c…`

### 3.1.3: Control the flow of CUI in accordance with approved authorizations.

- **Family:** AC (Access Control)
- **Status:** Attested (implemented, automation pending)
- **SPRS weight:** 1
- **Assessment method:** ATTESTED
- **Objectives addressed:** -

**Implementation statement.** Enforced by VPC subnet tiers and security-group chaining; collector pending.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.1.4: Separate duties of individuals to reduce risk of malevolent activity.

- **Family:** AC (Access Control)
- **Status:** Satisfied by policy
- **SPRS weight:** 1
- **Assessment method:** POLICY
- **Objectives addressed:** -

**Implementation statement.** RBAC role design separates duties; attested via policy.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.1.5: Employ least privilege, including for privileged accounts.

- **Family:** AC (Access Control)
- **Status:** Attested (implemented, automation pending)
- **SPRS weight:** 3
- **Assessment method:** ATTESTED
- **Objectives addressed:** -

**Implementation statement.** Least-privilege RBAC + care-team scoping; attested, automation pending.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.1.6: Use non-privileged accounts for nonsecurity functions.

- **Family:** AC (Access Control)
- **Status:** Attested (implemented, automation pending)
- **SPRS weight:** 1
- **Assessment method:** ATTESTED
- **Objectives addressed:** -

**Implementation statement.** Attested via policy.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.1.7: Prevent non-privileged users from executing privileged functions; log.

- **Family:** AC (Access Control)
- **Status:** Attested (implemented, automation pending)
- **SPRS weight:** 1
- **Assessment method:** ATTESTED
- **Objectives addressed:** -

**Implementation statement.** Privileged actions gated by permission checks and audited.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.1.8: Limit unsuccessful logon attempts.

- **Family:** AC (Access Control)
- **Status:** Attested (implemented, automation pending)
- **SPRS weight:** 3
- **Assessment method:** ATTESTED
- **Objectives addressed:** -

**Implementation statement.** Account lockout after 5 failed logons; automation pending.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.1.9: Provide privacy and security notices consistent with CUI rules.

- **Family:** AC (Access Control)
- **Status:** Satisfied by policy
- **SPRS weight:** 1
- **Assessment method:** POLICY
- **Objectives addressed:** -

**Implementation statement.** Login banner / policy; attested.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.1.10: Use session lock with pattern-hiding after inactivity.

- **Family:** AC (Access Control)
- **Status:** Attested (implemented, automation pending)
- **SPRS weight:** 3
- **Assessment method:** ATTESTED
- **Objectives addressed:** -

**Implementation statement.** 15-minute idle session timeout; automation pending.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.1.11: Terminate a user session after a defined condition.

- **Family:** AC (Access Control)
- **Status:** Attested (implemented, automation pending)
- **SPRS weight:** 3
- **Assessment method:** ATTESTED
- **Objectives addressed:** -

**Implementation statement.** Server-side session revocation; automation pending.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.1.12: Monitor and control remote access sessions.

- **Family:** AC (Access Control)
- **Status:** Attested (implemented, automation pending)
- **SPRS weight:** 5
- **Assessment method:** ATTESTED
- **Objectives addressed:** -

**Implementation statement.** All access via CloudFront/ALB; attested.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.1.13: Employ cryptographic mechanisms to protect remote access.

- **Family:** AC (Access Control)
- **Status:** Attested (implemented, automation pending)
- **SPRS weight:** 5
- **Assessment method:** ATTESTED
- **Objectives addressed:** -

**Implementation statement.** TLS 1.2+ everywhere; overlaps 3.13.8 (automated).

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.1.14: Route remote access via managed access control points.

- **Family:** AC (Access Control)
- **Status:** Attested (implemented, automation pending)
- **SPRS weight:** 1
- **Assessment method:** ATTESTED
- **Objectives addressed:** -

**Implementation statement.** CloudFront -> ALB managed entry; attested.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.1.15: Authorize remote execution of privileged commands.

- **Family:** AC (Access Control)
- **Status:** Satisfied by policy
- **SPRS weight:** 1
- **Assessment method:** POLICY
- **Objectives addressed:** -

**Implementation statement.** Policy-governed; ECS exec via SSM.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.1.16: Authorize wireless access prior to allowing connections.

- **Family:** AC (Access Control)
- **Status:** Not applicable
- **SPRS weight:** 5
- **Assessment method:** N/A
- **Objectives addressed:** -

**Implementation statement.** No wireless networks in the SaaS boundary.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.1.17: Protect wireless access using authentication and encryption.

- **Family:** AC (Access Control)
- **Status:** Not applicable
- **SPRS weight:** 5
- **Assessment method:** N/A
- **Objectives addressed:** -

**Implementation statement.** No wireless networks in the SaaS boundary.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.1.18: Control connection of mobile devices.

- **Family:** AC (Access Control)
- **Status:** Not applicable
- **SPRS weight:** 5
- **Assessment method:** N/A
- **Objectives addressed:** -

**Implementation statement.** No managed mobile devices in scope.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.1.19: Encrypt CUI on mobile devices and mobile computing platforms.

- **Family:** AC (Access Control)
- **Status:** Not applicable
- **SPRS weight:** 3
- **Assessment method:** N/A
- **Objectives addressed:** -

**Implementation statement.** No mobile devices in scope.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.1.20: Verify and control connections to external systems.

- **Family:** AC (Access Control)
- **Status:** Attested (implemented, automation pending)
- **SPRS weight:** 1
- **Assessment method:** ATTESTED
- **Objectives addressed:** -

**Implementation statement.** Boundary managed by CloudFront/WAF; attested.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.1.21: Limit use of portable storage devices on external systems.

- **Family:** AC (Access Control)
- **Status:** Not applicable
- **SPRS weight:** 1
- **Assessment method:** N/A
- **Objectives addressed:** -

**Implementation statement.** No portable storage in the SaaS boundary.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.1.22: Control CUI posted or processed on publicly accessible systems.

- **Family:** AC (Access Control)
- **Status:** Satisfied by policy
- **SPRS weight:** 1
- **Assessment method:** POLICY
- **Objectives addressed:** -

**Implementation statement.** No CUI on public systems; attested via policy.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.2.1: Ensure managers and users are aware of security risks.

- **Family:** AT (Awareness and Training)
- **Status:** Satisfied by policy
- **SPRS weight:** 5
- **Assessment method:** POLICY
- **Objectives addressed:** -

**Implementation statement.** Security awareness training program; see docs/policies/.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.2.2: Ensure personnel are trained to carry out security duties.

- **Family:** AT (Awareness and Training)
- **Status:** Satisfied by policy
- **SPRS weight:** 5
- **Assessment method:** POLICY
- **Objectives addressed:** -

**Implementation statement.** Role-based training; see docs/policies/.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.2.3: Provide security awareness training on insider threat.

- **Family:** AT (Awareness and Training)
- **Status:** Satisfied by policy
- **SPRS weight:** 1
- **Assessment method:** POLICY
- **Objectives addressed:** -

**Implementation statement.** Insider-threat awareness; see docs/policies/.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.3.1: Create and retain system audit logs.

- **Family:** AU (Audit and Accountability)
- **Status:** Implemented
- **SPRS weight:** 5
- **Assessment method:** EXAMINE
- **Objectives addressed:** 3.3.1[e], 3.3.1[f]

**Implementation statement.** Audit records are generated by log_access() and persisted to the AuditLog table (retained in Postgres).

**Evidence.**
- [`backend/services/audit_logger.py:29`](https://github.com/adrianbcaballero/AegleroEMR/blob/main/backend/services/audit_logger.py#L29): log_access() creates and stores an AuditLog row per event.

**Provenance.** collected by `audit_chain` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `f44ccc756422e990…`

### 3.3.2: Ensure actions are uniquely traceable to users.

- **Family:** AU (Audit and Accountability)
- **Status:** Implemented
- **SPRS weight:** 3
- **Assessment method:** EXAMINE
- **Objectives addressed:** 3.3.2[a], 3.3.2[b]

**Implementation statement.** Every audit record carries user_id, uniquely tracing actions to the acting user.

**Evidence.**
- [`backend/services/audit_logger.py:9`](https://github.com/adrianbcaballero/AegleroEMR/blob/main/backend/services/audit_logger.py#L9): user_id is part of the audit record content and hash input.

**Provenance.** collected by `audit_chain` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `3041c5b18177bd66…`

### 3.3.3: Review and update logged events.

- **Family:** AU (Audit and Accountability)
- **Status:** Satisfied by policy
- **SPRS weight:** 1
- **Assessment method:** POLICY
- **Objectives addressed:** -

**Implementation statement.** Logged-event set reviewed periodically; attested.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.3.4: Alert on audit logging process failure.

- **Family:** AU (Audit and Accountability)
- **Status:** Attested (implemented, automation pending)
- **SPRS weight:** 1
- **Assessment method:** ATTESTED
- **Objectives addressed:** -

**Implementation statement.** CloudWatch alarms; automation pending.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.3.5: Correlate audit review, analysis, and reporting.

- **Family:** AU (Audit and Accountability)
- **Status:** Attested (implemented, automation pending)
- **SPRS weight:** 5
- **Assessment method:** ATTESTED
- **Objectives addressed:** -

**Implementation statement.** Audit query/filter API; correlation collector pending.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.3.6: Provide audit record reduction and report generation.

- **Family:** AU (Audit and Accountability)
- **Status:** Attested (implemented, automation pending)
- **SPRS weight:** 1
- **Assessment method:** ATTESTED
- **Objectives addressed:** -

**Implementation statement.** Audit log API supports filtering/report; attested.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.3.7: Provide authoritative time source for timestamps.

- **Family:** AU (Audit and Accountability)
- **Status:** Attested (implemented, automation pending)
- **SPRS weight:** 1
- **Assessment method:** ATTESTED
- **Objectives addressed:** -

**Implementation statement.** UTC timestamps from host NTP; attested.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.3.8: Protect audit information from modification and deletion.

- **Family:** AU (Audit and Accountability)
- **Status:** Implemented
- **SPRS weight:** 5
- **Assessment method:** EXAMINE
- **Objectives addressed:** 3.3.8[b], 3.3.8[c]

**Implementation statement.** Audit log is tamper-evident: a per-tenant SHA-256 hash chain makes any modification or deletion of a past record mathematically detectable via /api/audit/verify.

**Evidence.**
- [`backend/services/audit_logger.py:9`](https://github.com/adrianbcaballero/AegleroEMR/blob/main/backend/services/audit_logger.py#L9): _compute_hash() = SHA-256(content || prev_hash) builds the chain.
- [`backend/services/audit_logger.py:9`](https://github.com/adrianbcaballero/AegleroEMR/blob/main/backend/services/audit_logger.py#L9): Each entry references the previous entry's hash (per-tenant chain).
- [`backend/routes/audit.py:246`](https://github.com/adrianbcaballero/AegleroEMR/blob/main/backend/routes/audit.py#L246): GET /api/audit/verify walks the chain and reports tampering.

**Provenance.** collected by `audit_chain` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `7e1ab282570bf134…`

### 3.3.9: Limit audit log management to a privileged subset of users.

- **Family:** AU (Audit and Accountability)
- **Status:** Attested (implemented, automation pending)
- **SPRS weight:** 1
- **Assessment method:** ATTESTED
- **Objectives addressed:** -

**Implementation statement.** audit.view permission restricts access; attested.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.4.1: Establish and maintain baseline configurations.

- **Family:** CM (Configuration Management)
- **Status:** Attested (implemented, automation pending)
- **SPRS weight:** 5
- **Assessment method:** ATTESTED
- **Objectives addressed:** -

**Implementation statement.** Terraform IaC is the baseline; collector pending.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.4.2: Establish and enforce security configuration settings.

- **Family:** CM (Configuration Management)
- **Status:** Attested (implemented, automation pending)
- **SPRS weight:** 5
- **Assessment method:** ATTESTED
- **Objectives addressed:** -

**Implementation statement.** Checkov/Trivy enforce config in CI; collector pending.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.4.3: Track, review, approve, and audit changes.

- **Family:** CM (Configuration Management)
- **Status:** Satisfied by policy
- **SPRS weight:** 1
- **Assessment method:** POLICY
- **Objectives addressed:** -

**Implementation statement.** Git history + PR reviews + branch protection; attested.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.4.4: Analyze security impact of changes prior to implementation.

- **Family:** CM (Configuration Management)
- **Status:** Satisfied by policy
- **SPRS weight:** 1
- **Assessment method:** POLICY
- **Objectives addressed:** -

**Implementation statement.** PR review + IaC scanning gates; attested.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.4.5: Define and enforce access restrictions for changes.

- **Family:** CM (Configuration Management)
- **Status:** Attested (implemented, automation pending)
- **SPRS weight:** 3
- **Assessment method:** ATTESTED
- **Objectives addressed:** -

**Implementation statement.** Branch protection + required reviews; attested.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.4.6: Employ least functionality; disable nonessential services.

- **Family:** CM (Configuration Management)
- **Status:** Attested (implemented, automation pending)
- **SPRS weight:** 5
- **Assessment method:** ATTESTED
- **Objectives addressed:** -

**Implementation statement.** Minimal container image; attested.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.4.7: Restrict nonessential programs, ports, protocols, services.

- **Family:** CM (Configuration Management)
- **Status:** Attested (implemented, automation pending)
- **SPRS weight:** 5
- **Assessment method:** ATTESTED
- **Objectives addressed:** -

**Implementation statement.** Security-group chaining restricts ports; attested.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.4.8: Apply deny-by-exception (blocklist) / permit-by-exception.

- **Family:** CM (Configuration Management)
- **Status:** Attested (implemented, automation pending)
- **SPRS weight:** 3
- **Assessment method:** ATTESTED
- **Objectives addressed:** -

**Implementation statement.** Allowlisted ingress via SGs; attested.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.4.9: Control and monitor user-installed software.

- **Family:** CM (Configuration Management)
- **Status:** Not applicable
- **SPRS weight:** 1
- **Assessment method:** N/A
- **Objectives addressed:** -

**Implementation statement.** Managed container images; no user-installed software.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.5.1: Identify system users and processes.

- **Family:** IA (Identification and Authentication)
- **Status:** Attested (implemented, automation pending)
- **SPRS weight:** 5
- **Assessment method:** ATTESTED
- **Objectives addressed:** -

**Implementation statement.** Unique user accounts per tenant; attested.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.5.2: Authenticate users and processes before access.

- **Family:** IA (Identification and Authentication)
- **Status:** Attested (implemented, automation pending)
- **SPRS weight:** 5
- **Assessment method:** ATTESTED
- **Objectives addressed:** -

**Implementation statement.** Session auth on every request; overlaps 3.1.1.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.5.3: Use multifactor authentication for account access.

- **Family:** IA (Identification and Authentication)
- **Status:** Implemented
- **SPRS weight:** 5
- **Assessment method:** EXAMINE
- **Objectives addressed:** 3.5.3[b], 3.5.3[e]

**Implementation statement.** TOTP multifactor authentication (RFC 6238 via pyotp) is implemented and enforced at login when tenant.mfa_required is set, applying to privileged and non-privileged accounts alike.

**Evidence.**
- [`backend/routes/mfa.py:4`](https://github.com/adrianbcaballero/AegleroEMR/blob/main/backend/routes/mfa.py#L4): pyotp TOTP setup/verify implements the second factor.
- [`backend/routes/auth.py:71`](https://github.com/adrianbcaballero/AegleroEMR/blob/main/backend/routes/auth.py#L71): Login enforces TOTP when tenant.mfa_required is enabled.

**Provenance.** collected by `access_control` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `3f070c86830d53df…`

### 3.5.4: Employ replay-resistant authentication mechanisms.

- **Family:** IA (Identification and Authentication)
- **Status:** Attested (implemented, automation pending)
- **SPRS weight:** 1
- **Assessment method:** ATTESTED
- **Objectives addressed:** -

**Implementation statement.** TOTP + session cookies over TLS; attested.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.5.5: Prevent reuse of identifiers for a defined period.

- **Family:** IA (Identification and Authentication)
- **Status:** Attested (implemented, automation pending)
- **SPRS weight:** 1
- **Assessment method:** ATTESTED
- **Objectives addressed:** -

**Implementation statement.** User IDs never reused; attested.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.5.6: Disable identifiers after a period of inactivity.

- **Family:** IA (Identification and Authentication)
- **Status:** Satisfied by policy
- **SPRS weight:** 1
- **Assessment method:** POLICY
- **Objectives addressed:** -

**Implementation statement.** Inactive-account disablement; policy-driven.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.5.7: Enforce minimum password complexity.

- **Family:** IA (Identification and Authentication)
- **Status:** Attested (implemented, automation pending)
- **SPRS weight:** 1
- **Assessment method:** ATTESTED
- **Objectives addressed:** -

**Implementation statement.** 12-char mixed-class policy in password_validator; collector pending.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.5.8: Prohibit password reuse for a number of generations.

- **Family:** IA (Identification and Authentication)
- **Status:** Attested (implemented, automation pending)
- **SPRS weight:** 1
- **Assessment method:** ATTESTED
- **Objectives addressed:** -

**Implementation statement.** Password history policy; attested.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.5.9: Allow temporary password use with immediate change.

- **Family:** IA (Identification and Authentication)
- **Status:** Satisfied by policy
- **SPRS weight:** 1
- **Assessment method:** POLICY
- **Objectives addressed:** -

**Implementation statement.** Admin-reset flow forces change; attested.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.5.10: Store and transmit only cryptographically-protected passwords.

- **Family:** IA (Identification and Authentication)
- **Status:** Attested (implemented, automation pending)
- **SPRS weight:** 5
- **Assessment method:** ATTESTED
- **Objectives addressed:** -

**Implementation statement.** Werkzeug scrypt hashing; overlaps 3.13.11.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.5.11: Obscure feedback of authentication information.

- **Family:** IA (Identification and Authentication)
- **Status:** Attested (implemented, automation pending)
- **SPRS weight:** 1
- **Assessment method:** ATTESTED
- **Objectives addressed:** -

**Implementation statement.** Masked password fields; attested.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.6.1: Establish an operational incident-handling capability.

- **Family:** IR (Incident Response)
- **Status:** Satisfied by policy
- **SPRS weight:** 5
- **Assessment method:** POLICY
- **Objectives addressed:** -

**Implementation statement.** IR plan + GuardDuty/CloudTrail; see docs/runbooks/.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.6.2: Track, document, and report incidents.

- **Family:** IR (Incident Response)
- **Status:** Satisfied by policy
- **SPRS weight:** 5
- **Assessment method:** POLICY
- **Objectives addressed:** -

**Implementation statement.** Incident tracking + reporting; see docs/runbooks/.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.6.3: Test the organizational incident response capability.

- **Family:** IR (Incident Response)
- **Status:** Satisfied by policy
- **SPRS weight:** 1
- **Assessment method:** POLICY
- **Objectives addressed:** -

**Implementation statement.** Tabletop exercises; see docs/policies/.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.7.1: Perform maintenance on organizational systems.

- **Family:** MA (Maintenance)
- **Status:** Inherited (provider)
- **SPRS weight:** 3
- **Assessment method:** INHERITED
- **Objectives addressed:** -

**Implementation statement.** Underlying hardware maintenance performed by AWS.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.7.2: Provide controls on tools, techniques, and personnel for maintenance.

- **Family:** MA (Maintenance)
- **Status:** Inherited (provider)
- **SPRS weight:** 5
- **Assessment method:** INHERITED
- **Objectives addressed:** -

**Implementation statement.** Physical/hardware maintenance controlled by AWS.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.7.3: Sanitize equipment removed for off-site maintenance.

- **Family:** MA (Maintenance)
- **Status:** Inherited (provider)
- **SPRS weight:** 1
- **Assessment method:** INHERITED
- **Objectives addressed:** -

**Implementation statement.** AWS media sanitization (NIST 800-88).

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.7.4: Check media containing diagnostic programs for malicious code.

- **Family:** MA (Maintenance)
- **Status:** Not applicable
- **SPRS weight:** 1
- **Assessment method:** N/A
- **Objectives addressed:** -

**Implementation statement.** No diagnostic media in the SaaS boundary.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.7.5: Require MFA for nonlocal maintenance sessions.

- **Family:** MA (Maintenance)
- **Status:** Satisfied by policy
- **SPRS weight:** 5
- **Assessment method:** POLICY
- **Objectives addressed:** -

**Implementation statement.** ECS exec via SSM with IAM; MFA on console; attested.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.7.6: Supervise maintenance activities of personnel without access.

- **Family:** MA (Maintenance)
- **Status:** Inherited (provider)
- **SPRS weight:** 1
- **Assessment method:** INHERITED
- **Objectives addressed:** -

**Implementation statement.** AWS supervises data-center maintenance personnel.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.8.1: Protect system media containing CUI.

- **Family:** MP (Media Protection)
- **Status:** Inherited (provider)
- **SPRS weight:** 3
- **Assessment method:** INHERITED
- **Objectives addressed:** -

**Implementation statement.** Storage media secured by AWS; data encrypted with KMS.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.8.2: Limit access to CUI on system media.

- **Family:** MP (Media Protection)
- **Status:** Attested (implemented, automation pending)
- **SPRS weight:** 5
- **Assessment method:** ATTESTED
- **Objectives addressed:** -

**Implementation statement.** S3/RDS access restricted via IAM/SG; attested.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.8.3: Sanitize or destroy media before disposal or reuse.

- **Family:** MP (Media Protection)
- **Status:** Inherited (provider)
- **SPRS weight:** 5
- **Assessment method:** INHERITED
- **Objectives addressed:** -

**Implementation statement.** AWS media sanitization on decommission (NIST 800-88).

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.8.4: Mark media with necessary CUI markings.

- **Family:** MP (Media Protection)
- **Status:** Not applicable
- **SPRS weight:** 1
- **Assessment method:** N/A
- **Objectives addressed:** -

**Implementation statement.** No physical media to mark.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.8.5: Control access to media during transport.

- **Family:** MP (Media Protection)
- **Status:** Not applicable
- **SPRS weight:** 3
- **Assessment method:** N/A
- **Objectives addressed:** -

**Implementation statement.** No physical media transport.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.8.6: Use cryptographic protection for CUI on media during transport.

- **Family:** MP (Media Protection)
- **Status:** Not applicable
- **SPRS weight:** 1
- **Assessment method:** N/A
- **Objectives addressed:** -

**Implementation statement.** No physical media transport; data encrypted at rest via KMS.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.8.7: Control the use of removable media.

- **Family:** MP (Media Protection)
- **Status:** Not applicable
- **SPRS weight:** 3
- **Assessment method:** N/A
- **Objectives addressed:** -

**Implementation statement.** No removable media in the SaaS boundary.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.8.8: Prohibit use of portable storage with no identifiable owner.

- **Family:** MP (Media Protection)
- **Status:** Not applicable
- **SPRS weight:** 1
- **Assessment method:** N/A
- **Objectives addressed:** -

**Implementation statement.** No portable storage in scope.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.8.9: Protect the confidentiality of backup CUI at storage locations.

- **Family:** MP (Media Protection)
- **Status:** Inherited (provider)
- **SPRS weight:** 1
- **Assessment method:** INHERITED
- **Objectives addressed:** -

**Implementation statement.** RDS automated backups encrypted with KMS in AWS.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.9.1: Screen individuals prior to authorizing access to CUI.

- **Family:** PS (Personnel Security)
- **Status:** Satisfied by policy
- **SPRS weight:** 3
- **Assessment method:** POLICY
- **Objectives addressed:** -

**Implementation statement.** Background screening policy; see docs/policies/.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.9.2: Protect CUI during and after personnel actions (termination/transfer).

- **Family:** PS (Personnel Security)
- **Status:** Satisfied by policy
- **SPRS weight:** 5
- **Assessment method:** POLICY
- **Objectives addressed:** -

**Implementation statement.** Deprovisioning on termination; see docs/policies/.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.10.1: Limit physical access to systems and equipment.

- **Family:** PE (Physical Protection)
- **Status:** Inherited (provider)
- **SPRS weight:** 5
- **Assessment method:** INHERITED
- **Objectives addressed:** -

**Implementation statement.** AWS data-center physical security (SOC 2 / FedRAMP).

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.10.2: Protect and monitor the physical facility and infrastructure.

- **Family:** PE (Physical Protection)
- **Status:** Inherited (provider)
- **SPRS weight:** 5
- **Assessment method:** INHERITED
- **Objectives addressed:** -

**Implementation statement.** AWS facility protection and monitoring.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.10.3: Escort visitors and monitor visitor activity.

- **Family:** PE (Physical Protection)
- **Status:** Inherited (provider)
- **SPRS weight:** 1
- **Assessment method:** INHERITED
- **Objectives addressed:** -

**Implementation statement.** AWS visitor controls at data centers.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.10.4: Maintain audit logs of physical access.

- **Family:** PE (Physical Protection)
- **Status:** Inherited (provider)
- **SPRS weight:** 1
- **Assessment method:** INHERITED
- **Objectives addressed:** -

**Implementation statement.** AWS physical access logging.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.10.5: Control and manage physical access devices.

- **Family:** PE (Physical Protection)
- **Status:** Inherited (provider)
- **SPRS weight:** 1
- **Assessment method:** INHERITED
- **Objectives addressed:** -

**Implementation statement.** AWS badge/key management.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.10.6: Enforce safeguarding measures for CUI at alternate work sites.

- **Family:** PE (Physical Protection)
- **Status:** Satisfied by policy
- **SPRS weight:** 1
- **Assessment method:** POLICY
- **Objectives addressed:** -

**Implementation statement.** Remote-work security policy; see docs/policies/.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.11.1: Periodically assess risk to operations and assets.

- **Family:** RA (Risk Assessment)
- **Status:** Satisfied by policy
- **SPRS weight:** 3
- **Assessment method:** POLICY
- **Objectives addressed:** -

**Implementation statement.** HIPAA Risk Analysis; see docs/risk-analysis.md.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.11.2: Scan for vulnerabilities periodically and when new ones arise.

- **Family:** RA (Risk Assessment)
- **Status:** Partially implemented
- **SPRS weight:** 5
- **Assessment method:** EXAMINE
- **Objectives addressed:** 3.11.2[a]

**Implementation statement.** Vulnerability scanning (pip-audit (Python deps), Trivy (containers/IaC/deps), Checkov (IaC compliance), pnpm audit (JS deps)) runs on every push/PR, but not on a fixed schedule, so newly disclosed CVEs in unchanged dependencies are not caught until the next commit.

**Evidence.**
- [`.github/workflows/ci.yml`](https://github.com/adrianbcaballero/AegleroEMR/blob/main/.github/workflows/ci.yml): Scan frequency defined by triggers: push, pull_request.
- [`.github/workflows/ci.yml`](https://github.com/adrianbcaballero/AegleroEMR/blob/main/.github/workflows/ci.yml): POA&M: add a scheduled (cron) scan to satisfy 3.11.2[d] for newly identified vulnerabilities.

**Provenance.** collected by `flaw_remediation` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `db60d2bac5b02da8…`

### 3.11.3: Remediate vulnerabilities in accordance with risk assessments.

- **Family:** RA (Risk Assessment)
- **Status:** Attested (implemented, automation pending)
- **SPRS weight:** 1
- **Assessment method:** ATTESTED
- **Objectives addressed:** -

**Implementation statement.** CI gates block HIGH/CRITICAL; overlaps 3.14.1.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.12.1: Periodically assess security controls for effectiveness.

- **Family:** CA (Security Assessment)
- **Status:** Implemented
- **SPRS weight:** 5
- **Assessment method:** EXAMINE
- **Objectives addressed:** 3.12.1

**Implementation statement.** This engine assesses every cataloged control on each run and on a schedule.

**Evidence.**
- [`compliance/run.py`](https://github.com/adrianbcaballero/AegleroEMR/blob/main/compliance/run.py): run.py executes all collectors and scores the controls.

**Provenance.** collected by `self_assessment` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `c076dee48c67788e…`

### 3.12.2: Develop and implement plans of action (POA&M).

- **Family:** CA (Security Assessment)
- **Status:** Implemented
- **SPRS weight:** 3
- **Assessment method:** EXAMINE
- **Objectives addressed:** 3.12.2

**Implementation statement.** A Plan of Action & Milestones is auto-generated from the assessment results.

**Evidence.**
- [`compliance/generate_docs.py`](https://github.com/adrianbcaballero/AegleroEMR/blob/main/compliance/generate_docs.py): generate_docs.py renders POAM.md and POAM.csv from status.json.

**Provenance.** collected by `self_assessment` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `fc90c8132923de8f…`

### 3.12.3: Monitor security controls on an ongoing basis.

- **Family:** CA (Security Assessment)
- **Status:** Implemented
- **SPRS weight:** 5
- **Assessment method:** EXAMINE
- **Objectives addressed:** 3.12.3

**Implementation statement.** Controls are monitored continuously by a scheduled GitHub Actions workflow with a drift gate.

**Evidence.**
- [`.github/workflows/compliance.yml`](https://github.com/adrianbcaballero/AegleroEMR/blob/main/.github/workflows/compliance.yml): compliance.yml re-runs the assessment daily and commits refreshed evidence.

**Provenance.** collected by `self_assessment` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `8ec5b8a657efb90e…`

### 3.12.4: Develop and maintain a System Security Plan (SSP).

- **Family:** CA (Security Assessment)
- **Status:** Implemented
- **SPRS weight:** 0
- **Assessment method:** EXAMINE
- **Objectives addressed:** 3.12.4

**Implementation statement.** A System Security Plan is auto-generated from the control implementations.

**Evidence.**
- [`compliance/generate_docs.py`](https://github.com/adrianbcaballero/AegleroEMR/blob/main/compliance/generate_docs.py): generate_docs.py renders SSP.md from status.json.

**Provenance.** collected by `self_assessment` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `0514e8cfdd941f70…`

### 3.13.1: Monitor, control, and protect communications at boundaries.

- **Family:** SC (System and Communications Protection)
- **Status:** Attested (implemented, automation pending)
- **SPRS weight:** 5
- **Assessment method:** ATTESTED
- **Objectives addressed:** -

**Implementation statement.** VPC tiers + SG chaining + WAF; collector pending.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.13.2: Employ architectural designs promoting effective security.

- **Family:** SC (System and Communications Protection)
- **Status:** Satisfied by policy
- **SPRS weight:** 5
- **Assessment method:** POLICY
- **Objectives addressed:** -

**Implementation statement.** Documented secure architecture; see ARCHITECTURE.md.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.13.3: Separate user functionality from system management.

- **Family:** SC (System and Communications Protection)
- **Status:** Attested (implemented, automation pending)
- **SPRS weight:** 1
- **Assessment method:** ATTESTED
- **Objectives addressed:** -

**Implementation statement.** Separate admin routes/permissions; attested.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.13.4: Prevent unauthorized information transfer via shared resources.

- **Family:** SC (System and Communications Protection)
- **Status:** Attested (implemented, automation pending)
- **SPRS weight:** 3
- **Assessment method:** ATTESTED
- **Objectives addressed:** -

**Implementation statement.** Per-tenant isolation + tenant_id scoping; attested.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.13.5: Implement subnetworks for publicly accessible components.

- **Family:** SC (System and Communications Protection)
- **Status:** Attested (implemented, automation pending)
- **SPRS weight:** 5
- **Assessment method:** ATTESTED
- **Objectives addressed:** -

**Implementation statement.** Public/private/isolated subnet tiers; attested.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.13.6: Deny network traffic by default; allow by exception.

- **Family:** SC (System and Communications Protection)
- **Status:** Attested (implemented, automation pending)
- **SPRS weight:** 3
- **Assessment method:** ATTESTED
- **Objectives addressed:** -

**Implementation statement.** Security groups deny-by-default; attested.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.13.7: Prevent split tunneling for remote devices.

- **Family:** SC (System and Communications Protection)
- **Status:** Not applicable
- **SPRS weight:** 1
- **Assessment method:** N/A
- **Objectives addressed:** -

**Implementation statement.** No remote VPN/devices in the SaaS boundary.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.13.8: Use cryptography to protect CUI during transmission.

- **Family:** SC (System and Communications Protection)
- **Status:** Implemented
- **SPRS weight:** 5
- **Assessment method:** EXAMINE
- **Objectives addressed:** 3.13.8[c]

**Implementation statement.** Data in transit is encrypted end to end: TLS 1.2+ is enforced at CloudFront and the ALB, and RDS refuses non-TLS connections.

**Evidence.**
- [`infra/rds.tf:23`](https://github.com/adrianbcaballero/AegleroEMR/blob/main/infra/rds.tf#L23): RDS parameter rds.force_ssl=1 rejects any non-TLS database connection.
- [`infra/alb.tf:109`](https://github.com/adrianbcaballero/AegleroEMR/blob/main/infra/alb.tf#L109): ALB HTTPS listener uses a TLS 1.2/1.3 security policy.
- [`infra/cloudfront.tf:205`](https://github.com/adrianbcaballero/AegleroEMR/blob/main/infra/cloudfront.tf#L205): CloudFront enforces a minimum TLS 1.2 viewer protocol version.
- [`infra/cloudfront.tf:149`](https://github.com/adrianbcaballero/AegleroEMR/blob/main/infra/cloudfront.tf#L149): CloudFront redirects all viewer traffic to HTTPS.

**Provenance.** collected by `crypto_config` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `2136645358e39391…`

### 3.13.9: Terminate network connections after inactivity.

- **Family:** SC (System and Communications Protection)
- **Status:** Attested (implemented, automation pending)
- **SPRS weight:** 1
- **Assessment method:** ATTESTED
- **Objectives addressed:** -

**Implementation statement.** Idle timeouts on sessions/keepalive; attested.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.13.10: Establish and manage cryptographic keys.

- **Family:** SC (System and Communications Protection)
- **Status:** Inherited (provider)
- **SPRS weight:** 1
- **Assessment method:** INHERITED
- **Objectives addressed:** -

**Implementation statement.** AWS KMS manages key lifecycle and rotation.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.13.11: Employ FIPS-validated cryptography to protect CUI.

- **Family:** SC (System and Communications Protection)
- **Status:** Implemented
- **SPRS weight:** 3
- **Assessment method:** EXAMINE
- **Objectives addressed:** 3.13.11[a]

**Implementation statement.** Confidentiality is protected with FIPS 140-2 validated cryptography: AWS KMS customer-managed keys (rotated) encrypt RDS storage, Secrets Manager, logs, and S3; TLS in transit terminates on AWS's FIPS-capable endpoints.

**Evidence.**
- [`infra/kms.tf:19`](https://github.com/adrianbcaballero/AegleroEMR/blob/main/infra/kms.tf#L19): 4 customer-managed AWS KMS key(s) defined. AWS KMS HSMs are FIPS 140-2 validated (NIST CMVP).
- [`infra/kms.tf:21`](https://github.com/adrianbcaballero/AegleroEMR/blob/main/infra/kms.tf#L21): Automatic annual key rotation is enabled on the KMS keys.
- [`infra/rds.tf:85`](https://github.com/adrianbcaballero/AegleroEMR/blob/main/infra/rds.tf#L85): RDS storage is encrypted at rest using a customer-managed KMS key.

**Provenance.** collected by `crypto_config` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `9ad52e2681f2b5bc…`

### 3.13.12: Prohibit remote activation of collaborative computing devices.

- **Family:** SC (System and Communications Protection)
- **Status:** Not applicable
- **SPRS weight:** 1
- **Assessment method:** N/A
- **Objectives addressed:** -

**Implementation statement.** No cameras/microphones in scope.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.13.13: Control and monitor use of mobile code.

- **Family:** SC (System and Communications Protection)
- **Status:** Attested (implemented, automation pending)
- **SPRS weight:** 1
- **Assessment method:** ATTESTED
- **Objectives addressed:** -

**Implementation statement.** CSP/headers restrict client code; attested.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.13.14: Control and monitor use of Voice over IP.

- **Family:** SC (System and Communications Protection)
- **Status:** Not applicable
- **SPRS weight:** 1
- **Assessment method:** N/A
- **Objectives addressed:** -

**Implementation statement.** No VoIP in the SaaS boundary.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.13.15: Protect authenticity of communications sessions.

- **Family:** SC (System and Communications Protection)
- **Status:** Attested (implemented, automation pending)
- **SPRS weight:** 5
- **Assessment method:** ATTESTED
- **Objectives addressed:** -

**Implementation statement.** TLS + httpOnly SameSite session cookies; attested.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.13.16: Protect the confidentiality of CUI at rest.

- **Family:** SC (System and Communications Protection)
- **Status:** Attested (implemented, automation pending)
- **SPRS weight:** 5
- **Assessment method:** ATTESTED
- **Objectives addressed:** -

**Implementation statement.** RDS/S3/Secrets encrypted with KMS; collector pending.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.14.1: Identify, report, and correct system flaws in a timely manner.

- **Family:** SI (System and Information Integrity)
- **Status:** Implemented
- **SPRS weight:** 5
- **Assessment method:** EXAMINE
- **Objectives addressed:** 3.14.1[b], 3.14.1[c]

**Implementation statement.** System flaws are identified by Bandit (SAST), pip-audit (Python deps), Trivy (containers/IaC/deps), Checkov (IaC compliance), pnpm audit (JS deps); findings gate the pipeline (exit-code 1), forcing correction before code merges.

**Evidence.**
- [`.github/workflows/ci.yml`](https://github.com/adrianbcaballero/AegleroEMR/blob/main/.github/workflows/ci.yml): 5 scanners configured: Bandit (SAST), pip-audit (Python deps), Trivy (containers/IaC/deps), Checkov (IaC compliance), pnpm audit (JS deps).
- [`.github/workflows/ci.yml`](https://github.com/adrianbcaballero/AegleroEMR/blob/main/.github/workflows/ci.yml): A HIGH/CRITICAL finding fails the build (exit-code 1), blocking merge until the flaw is corrected.

**Provenance.** collected by `flaw_remediation` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `3f153b6b1e8f5801…`

### 3.14.2: Provide protection from malicious code.

- **Family:** SI (System and Information Integrity)
- **Status:** Attested (implemented, automation pending)
- **SPRS weight:** 5
- **Assessment method:** ATTESTED
- **Objectives addressed:** -

**Implementation statement.** Trivy image/dep scanning in CI; collector pending.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.14.3: Monitor system security alerts and advisories; act on them.

- **Family:** SI (System and Information Integrity)
- **Status:** Satisfied by policy
- **SPRS weight:** 1
- **Assessment method:** POLICY
- **Objectives addressed:** -

**Implementation statement.** pip-audit/Trivy advisories + GuardDuty; attested.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.14.4: Update malicious code protection mechanisms.

- **Family:** SI (System and Information Integrity)
- **Status:** Attested (implemented, automation pending)
- **SPRS weight:** 1
- **Assessment method:** ATTESTED
- **Objectives addressed:** -

**Implementation statement.** Trivy DB updated each CI run; collector pending.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.14.5: Perform periodic and real-time scans of the system.

- **Family:** SI (System and Information Integrity)
- **Status:** Attested (implemented, automation pending)
- **SPRS weight:** 3
- **Assessment method:** ATTESTED
- **Objectives addressed:** -

**Implementation statement.** CI scans on every change; overlaps 3.11.2.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.14.6: Monitor systems to detect attacks and indicators.

- **Family:** SI (System and Information Integrity)
- **Status:** Attested (implemented, automation pending)
- **SPRS weight:** 5
- **Assessment method:** ATTESTED
- **Objectives addressed:** -

**Implementation statement.** GuardDuty + VPC Flow Logs + CloudTrail; attested.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

### 3.14.7: Identify unauthorized use of organizational systems.

- **Family:** SI (System and Information Integrity)
- **Status:** Attested (implemented, automation pending)
- **SPRS weight:** 3
- **Assessment method:** ATTESTED
- **Objectives addressed:** -

**Implementation statement.** Audit log + GuardDuty anomaly detection; attested.

**Provenance.** collected by `catalog` at 2026-07-01T08:47:48+00:00 · evidence SHA-256 `…`

