"""
Builder for controls.json - the full NIST SP 800-171 Rev 2 catalog (110 controls)
with dispositions and cross-framework mappings.

Run:  python compliance/catalog/build_catalog.py   ->  writes controls.json

DRAFT DATA: the SPRS weights, dispositions (type), and HIPAA/ONC/42 CFR Part 2
mappings are best-effort and MUST be spot-checked against the authoritative sources
in ../references/SOURCES.md before being treated as final. CMMC IDs are derived
mechanically (family.Ln-id).

Disposition types:
  automated  - a collector proves it (or should; if no collector yet -> not-collected)
  inherited  - the cloud provider (AWS) supplies it
  manual     - satisfied by an org policy/procedure or manual attestation of
               implementation (evidence lives in docs/policies/ or the SSP narrative)
  na         - not applicable to this SaaS EHR, with rationale
"""

import json
from pathlib import Path

FAMILIES = {
    "AC": "Access Control", "AT": "Awareness and Training", "AU": "Audit and Accountability",
    "CM": "Configuration Management", "IA": "Identification and Authentication",
    "IR": "Incident Response", "MA": "Maintenance", "MP": "Media Protection",
    "PS": "Personnel Security", "PE": "Physical Protection", "RA": "Risk Assessment",
    "CA": "Security Assessment", "SC": "System and Communications Protection",
    "SI": "System and Information Integrity",
}

# The 17 CMMC Level 1 practices (FAR 52.204-21 basic safeguarding); everything else is L2.
L1 = {"3.1.1", "3.1.2", "3.1.20", "3.1.22", "3.5.1", "3.5.2", "3.8.3", "3.10.1",
      "3.10.3", "3.10.4", "3.10.5", "3.13.1", "3.13.5", "3.14.1", "3.14.2", "3.14.4", "3.14.5"}

# Controls that have a real collector today (status comes from the collector at runtime).
HAS_COLLECTOR = {"3.1.1", "3.1.2", "3.3.1", "3.3.2", "3.3.8", "3.5.3",
                 "3.11.2", "3.13.8", "3.13.11", "3.14.1",
                 "3.12.1", "3.12.2", "3.12.3", "3.12.4",  # CA family via self_assessment
                 "3.1.8", "3.1.11", "3.5.7",              # identity_hardening
                 "3.13.10", "3.13.16",                    # crypto_config (key mgmt, at rest)
                 "3.13.1", "3.13.5", "3.13.6"}            # network_config (boundary/subnets/deny)

# Controls that are genuinely NOT satisfied yet (no policy/procedure or implementation
# in place). They are honest gaps: scored not-met, appear in the POA&M, and deduct SPRS.
NOT_IMPLEMENTED = {
    "3.2.1", "3.2.2", "3.2.3",   # AT: no security awareness / training program yet
    "3.9.1", "3.9.2",            # PS: no personnel screening / termination policy yet
}

# Implemented in the application but not YET covered by a collector. These are
# attested (manual) rather than counted as gaps -- they are automation-roadmap
# candidates, and the "automated coverage" metric reflects that they aren't
# auto-verified yet. They must not deduct SPRS as if they were not implemented.
ROADMAP = {"3.1.3", "3.3.5", "3.4.1", "3.4.2", "3.5.7", "3.11.3",
           "3.13.1", "3.13.16", "3.14.2", "3.14.4", "3.14.5"}

# Genuine POLICY controls: satisfied by a document or human process, not by app
# code (training, personnel, incident-response plan, risk analysis, etc.).
# Every other control currently typed "manual" is really ATTESTED -- implemented
# in the application, we vouch for it, and a collector is a roadmap item.
POLICY = {
    "3.1.4", "3.1.9", "3.1.15", "3.1.22",   # AC: policy/notice/authorization
    "3.2.1", "3.2.2", "3.2.3",              # AT: training
    "3.3.3",                                 # AU: review logged-event set (process)
    "3.4.3", "3.4.4",                        # CM: change tracking/impact (process)
    "3.5.6", "3.5.9",                        # IA: inactivity disable / temp password (policy)
    "3.6.1", "3.6.2", "3.6.3",              # IR: incident response plan/testing
    "3.7.5",                                 # MA: nonlocal maintenance authorization
    "3.9.1", "3.9.2",                        # PS: personnel screening/termination
    "3.10.6",                                # PE: alternate work site policy
    "3.11.1",                                # RA: risk analysis (document)
    "3.13.2",                                # SC: secure architecture (document)
    "3.14.3",                                # SI: monitor advisories (process)
}

# Authoritative SPRS point values from the NIST SP 800-171 DoD Assessment Methodology
# v1.2.1 (June 24, 2020), Annex A - Scoring Template. This dict is the source of truth
# for weights and overrides any value in the ROWS below. 3.5.3 (MFA) and 3.13.11 (FIPS)
# carry 3-to-5 partial-credit rules; we record the full not-implemented value of 5.
# 3.12.4 (SSP) is scored NA (its absence stops the assessment); recorded as 0.
SPRS_WEIGHT = {
    "3.1.1": 5, "3.1.2": 5, "3.1.3": 1, "3.1.4": 1, "3.1.5": 3, "3.1.6": 1, "3.1.7": 1,
    "3.1.8": 1, "3.1.9": 1, "3.1.10": 1, "3.1.11": 1, "3.1.12": 5, "3.1.13": 5, "3.1.14": 1,
    "3.1.15": 1, "3.1.16": 5, "3.1.17": 5, "3.1.18": 5, "3.1.19": 3, "3.1.20": 1, "3.1.21": 1,
    "3.1.22": 1,
    "3.2.1": 5, "3.2.2": 5, "3.2.3": 1,
    "3.3.1": 5, "3.3.2": 3, "3.3.3": 1, "3.3.4": 1, "3.3.5": 5, "3.3.6": 1, "3.3.7": 1,
    "3.3.8": 1, "3.3.9": 1,
    "3.4.1": 5, "3.4.2": 5, "3.4.3": 1, "3.4.4": 1, "3.4.5": 5, "3.4.6": 5, "3.4.7": 5,
    "3.4.8": 5, "3.4.9": 1,
    "3.5.1": 5, "3.5.2": 5, "3.5.3": 5, "3.5.4": 1, "3.5.5": 1, "3.5.6": 1, "3.5.7": 1,
    "3.5.8": 1, "3.5.9": 1, "3.5.10": 5, "3.5.11": 1,
    "3.6.1": 5, "3.6.2": 5, "3.6.3": 1,
    "3.7.1": 3, "3.7.2": 5, "3.7.3": 1, "3.7.4": 3, "3.7.5": 5, "3.7.6": 1,
    "3.8.1": 3, "3.8.2": 3, "3.8.3": 5, "3.8.4": 1, "3.8.5": 1, "3.8.6": 1, "3.8.7": 5,
    "3.8.8": 3, "3.8.9": 1,
    "3.9.1": 3, "3.9.2": 5,
    "3.10.1": 5, "3.10.2": 5, "3.10.3": 1, "3.10.4": 1, "3.10.5": 1, "3.10.6": 1,
    "3.11.1": 3, "3.11.2": 5, "3.11.3": 1,
    "3.12.1": 5, "3.12.2": 3, "3.12.3": 5, "3.12.4": 0,
    "3.13.1": 5, "3.13.2": 5, "3.13.3": 1, "3.13.4": 1, "3.13.5": 5, "3.13.6": 5, "3.13.7": 1,
    "3.13.8": 3, "3.13.9": 1, "3.13.10": 1, "3.13.11": 5, "3.13.12": 1, "3.13.13": 1,
    "3.13.14": 1, "3.13.15": 5, "3.13.16": 1,
    "3.14.1": 5, "3.14.2": 5, "3.14.3": 5, "3.14.4": 5, "3.14.5": 3, "3.14.6": 5, "3.14.7": 3,
}

FAM_OF = lambda cid: {
    "3.1": "AC", "3.2": "AT", "3.3": "AU", "3.4": "CM", "3.5": "IA", "3.6": "IR",
    "3.7": "MA", "3.8": "MP", "3.9": "PS", "3.10": "PE", "3.11": "RA", "3.12": "CA",
    "3.13": "SC", "3.14": "SI",
}[".".join(cid.split(".")[:2])]

# Each row: (id, title, weight, type, hipaa, onc, part2, rationale)
# hipaa/onc/part2 = None when there is no clean mapping.
ROWS = [
    # ---- 3.1 Access Control ----
    ("3.1.1", "Limit system access to authorized users and processes.", 5, "automated", "164.312(a)(1)", "170.315(d)(1)", "2.16", ""),
    ("3.1.2", "Limit system access to permitted transactions and functions.", 5, "automated", "164.312(a)(1)", "170.315(d)(1)", "2.16", ""),
    ("3.1.3", "Control the flow of CUI in accordance with approved authorizations.", 1, "automated", None, None, None, "Enforced by VPC subnet tiers and security-group chaining; collector pending."),
    ("3.1.4", "Separate duties of individuals to reduce risk of malevolent activity.", 1, "manual", None, None, None, "RBAC role design separates duties; attested via policy."),
    ("3.1.5", "Employ least privilege, including for privileged accounts.", 3, "manual", "164.312(a)(1)", "170.315(d)(1)", None, "Least-privilege RBAC + care-team scoping; attested, automation pending."),
    ("3.1.6", "Use non-privileged accounts for nonsecurity functions.", 1, "manual", None, None, None, "Attested via policy."),
    ("3.1.7", "Prevent non-privileged users from executing privileged functions; log.", 1, "manual", None, None, None, "Privileged actions gated by permission checks and audited."),
    ("3.1.8", "Limit unsuccessful logon attempts.", 3, "manual", None, None, None, "Account lockout after 5 failed logons; automation pending."),
    ("3.1.9", "Provide privacy and security notices consistent with CUI rules.", 1, "manual", None, None, None, "Login banner / policy; attested."),
    ("3.1.10", "Use session lock with pattern-hiding after inactivity.", 3, "manual", None, "170.315(d)(5)", None, "15-minute idle session timeout; automation pending."),
    ("3.1.11", "Terminate a user session after a defined condition.", 3, "manual", "164.312(a)(2)(iii)", "170.315(d)(5)", None, "Server-side session revocation; automation pending."),
    ("3.1.12", "Monitor and control remote access sessions.", 5, "manual", "164.312(e)(1)", None, None, "All access via CloudFront/ALB; attested."),
    ("3.1.13", "Employ cryptographic mechanisms to protect remote access.", 5, "manual", "164.312(e)(2)(ii)", "170.315(d)(9)", None, "TLS 1.2+ everywhere; overlaps 3.13.8 (automated)."),
    ("3.1.14", "Route remote access via managed access control points.", 1, "manual", None, None, None, "CloudFront -> ALB managed entry; attested."),
    ("3.1.15", "Authorize remote execution of privileged commands.", 1, "manual", None, None, None, "Policy-governed; ECS exec via SSM."),
    ("3.1.16", "Authorize wireless access prior to allowing connections.", 5, "na", None, None, None, "No wireless networks in the SaaS boundary."),
    ("3.1.17", "Protect wireless access using authentication and encryption.", 5, "na", None, None, None, "No wireless networks in the SaaS boundary."),
    ("3.1.18", "Control connection of mobile devices.", 5, "na", None, None, None, "No managed mobile devices in scope."),
    ("3.1.19", "Encrypt CUI on mobile devices and mobile computing platforms.", 3, "na", None, None, None, "No mobile devices in scope."),
    ("3.1.20", "Verify and control connections to external systems.", 1, "manual", None, None, None, "Boundary managed by CloudFront/WAF; attested."),
    ("3.1.21", "Limit use of portable storage devices on external systems.", 1, "na", None, None, None, "No portable storage in the SaaS boundary."),
    ("3.1.22", "Control CUI posted or processed on publicly accessible systems.", 1, "manual", None, None, None, "No CUI on public systems; attested via policy."),

    # ---- 3.2 Awareness and Training ----
    ("3.2.1", "Ensure managers and users are aware of security risks.", 5, "manual", "164.308(a)(5)(i)", None, None, "Security awareness training program; see docs/policies/."),
    ("3.2.2", "Ensure personnel are trained to carry out security duties.", 5, "manual", "164.308(a)(5)(i)", None, None, "Role-based training; see docs/policies/."),
    ("3.2.3", "Provide security awareness training on insider threat.", 1, "manual", None, None, None, "Insider-threat awareness; see docs/policies/."),

    # ---- 3.3 Audit and Accountability ----
    ("3.3.1", "Create and retain system audit logs.", 5, "automated", "164.312(b)", "170.315(d)(10)", "2.16", ""),
    ("3.3.2", "Ensure actions are uniquely traceable to users.", 3, "automated", "164.312(b)", "170.315(d)(2)", "2.16", ""),
    ("3.3.3", "Review and update logged events.", 1, "manual", None, None, None, "Logged-event set reviewed periodically; attested."),
    ("3.3.4", "Alert on audit logging process failure.", 1, "manual", None, None, None, "CloudWatch alarms; automation pending."),
    ("3.3.5", "Correlate audit review, analysis, and reporting.", 5, "automated", None, None, None, "Audit query/filter API; correlation collector pending."),
    ("3.3.6", "Provide audit record reduction and report generation.", 1, "manual", None, "170.315(d)(3)", None, "Audit log API supports filtering/report; attested."),
    ("3.3.7", "Provide authoritative time source for timestamps.", 1, "manual", None, None, None, "UTC timestamps from host NTP; attested."),
    ("3.3.8", "Protect audit information from modification and deletion.", 5, "automated", "164.312(b), 164.312(c)(1)", "170.315(d)(2)", "2.16", ""),
    ("3.3.9", "Limit audit log management to a privileged subset of users.", 1, "manual", None, None, None, "audit.view permission restricts access; attested."),

    # ---- 3.4 Configuration Management ----
    ("3.4.1", "Establish and maintain baseline configurations.", 5, "automated", None, None, None, "Terraform IaC is the baseline; collector pending."),
    ("3.4.2", "Establish and enforce security configuration settings.", 5, "automated", None, None, None, "Checkov/Trivy enforce config in CI; collector pending."),
    ("3.4.3", "Track, review, approve, and audit changes.", 1, "manual", None, None, None, "Git history + PR reviews + branch protection; attested."),
    ("3.4.4", "Analyze security impact of changes prior to implementation.", 1, "manual", None, None, None, "PR review + IaC scanning gates; attested."),
    ("3.4.5", "Define and enforce access restrictions for changes.", 3, "manual", None, None, None, "Branch protection + required reviews; attested."),
    ("3.4.6", "Employ least functionality; disable nonessential services.", 5, "manual", None, None, None, "Minimal container image; attested."),
    ("3.4.7", "Restrict nonessential programs, ports, protocols, services.", 5, "manual", None, None, None, "Security-group chaining restricts ports; attested."),
    ("3.4.8", "Apply deny-by-exception (blocklist) / permit-by-exception.", 3, "manual", None, None, None, "Allowlisted ingress via SGs; attested."),
    ("3.4.9", "Control and monitor user-installed software.", 1, "na", None, None, None, "Managed container images; no user-installed software."),

    # ---- 3.5 Identification and Authentication ----
    ("3.5.1", "Identify system users and processes.", 5, "manual", "164.312(a)(2)(i)", None, None, "Unique user accounts per tenant; attested."),
    ("3.5.2", "Authenticate users and processes before access.", 5, "manual", "164.312(d)", None, None, "Session auth on every request; overlaps 3.1.1."),
    ("3.5.3", "Use multifactor authentication for account access.", 5, "automated", "164.312(d)", "170.315(d)(13)", None, ""),
    ("3.5.4", "Employ replay-resistant authentication mechanisms.", 1, "manual", None, None, None, "TOTP + session cookies over TLS; attested."),
    ("3.5.5", "Prevent reuse of identifiers for a defined period.", 1, "manual", None, None, None, "User IDs never reused; attested."),
    ("3.5.6", "Disable identifiers after a period of inactivity.", 1, "manual", None, None, None, "Inactive-account disablement; policy-driven."),
    ("3.5.7", "Enforce minimum password complexity.", 1, "automated", None, None, None, "12-char mixed-class policy in password_validator; collector pending."),
    ("3.5.8", "Prohibit password reuse for a number of generations.", 1, "manual", None, None, None, "Password history policy; attested."),
    ("3.5.9", "Allow temporary password use with immediate change.", 1, "manual", None, None, None, "Admin-reset flow forces change; attested."),
    ("3.5.10", "Store and transmit only cryptographically-protected passwords.", 5, "manual", "164.312(a)(2)(iv)", "170.315(d)(12)", None, "Werkzeug scrypt hashing; overlaps 3.13.11."),
    ("3.5.11", "Obscure feedback of authentication information.", 1, "manual", None, None, None, "Masked password fields; attested."),

    # ---- 3.6 Incident Response ----
    ("3.6.1", "Establish an operational incident-handling capability.", 5, "manual", "164.308(a)(6)(i)", None, "2.16", "IR plan + GuardDuty/CloudTrail; see docs/runbooks/."),
    ("3.6.2", "Track, document, and report incidents.", 5, "manual", "164.308(a)(6)(ii)", None, None, "Incident tracking + reporting; see docs/runbooks/."),
    ("3.6.3", "Test the organizational incident response capability.", 1, "manual", None, None, None, "Tabletop exercises; see docs/policies/."),

    # ---- 3.7 Maintenance ----
    ("3.7.1", "Perform maintenance on organizational systems.", 3, "inherited", None, None, None, "Underlying hardware maintenance performed by AWS."),
    ("3.7.2", "Provide controls on tools, techniques, and personnel for maintenance.", 5, "inherited", None, None, None, "Physical/hardware maintenance controlled by AWS."),
    ("3.7.3", "Sanitize equipment removed for off-site maintenance.", 1, "inherited", None, None, None, "AWS media sanitization (NIST 800-88)."),
    ("3.7.4", "Check media containing diagnostic programs for malicious code.", 1, "na", None, None, None, "No diagnostic media in the SaaS boundary."),
    ("3.7.5", "Require MFA for nonlocal maintenance sessions.", 5, "manual", None, None, None, "ECS exec via SSM with IAM; MFA on console; attested."),
    ("3.7.6", "Supervise maintenance activities of personnel without access.", 1, "inherited", None, None, None, "AWS supervises data-center maintenance personnel."),

    # ---- 3.8 Media Protection ----
    ("3.8.1", "Protect system media containing CUI.", 3, "inherited", "164.310(d)(1)", None, None, "Storage media secured by AWS; data encrypted with KMS."),
    ("3.8.2", "Limit access to CUI on system media.", 5, "manual", "164.310(d)(1)", None, None, "S3/RDS access restricted via IAM/SG; attested."),
    ("3.8.3", "Sanitize or destroy media before disposal or reuse.", 5, "inherited", "164.310(d)(2)(i), 164.310(d)(2)(ii)", None, None, "AWS media sanitization on decommission (NIST 800-88)."),
    ("3.8.4", "Mark media with necessary CUI markings.", 1, "na", None, None, None, "No physical media to mark."),
    ("3.8.5", "Control access to media during transport.", 3, "na", None, None, None, "No physical media transport."),
    ("3.8.6", "Use cryptographic protection for CUI on media during transport.", 1, "na", None, None, None, "No physical media transport; data encrypted at rest via KMS."),
    ("3.8.7", "Control the use of removable media.", 3, "na", None, None, None, "No removable media in the SaaS boundary."),
    ("3.8.8", "Prohibit use of portable storage with no identifiable owner.", 1, "na", None, None, None, "No portable storage in scope."),
    ("3.8.9", "Protect the confidentiality of backup CUI at storage locations.", 1, "inherited", "164.308(a)(7)(ii)(A)", None, None, "RDS automated backups encrypted with KMS in AWS."),

    # ---- 3.9 Personnel Security ----
    ("3.9.1", "Screen individuals prior to authorizing access to CUI.", 3, "manual", "164.308(a)(3)(ii)(B)", None, None, "Background screening policy; see docs/policies/."),
    ("3.9.2", "Protect CUI during and after personnel actions (termination/transfer).", 5, "manual", "164.308(a)(3)(ii)(C)", None, None, "Deprovisioning on termination; see docs/policies/."),

    # ---- 3.10 Physical Protection (inherited from AWS) ----
    ("3.10.1", "Limit physical access to systems and equipment.", 5, "inherited", "164.310(a)(1)", None, None, "AWS data-center physical security (SOC 2 / FedRAMP)."),
    ("3.10.2", "Protect and monitor the physical facility and infrastructure.", 5, "inherited", "164.310(a)(2)(ii)", None, None, "AWS facility protection and monitoring."),
    ("3.10.3", "Escort visitors and monitor visitor activity.", 1, "inherited", None, None, None, "AWS visitor controls at data centers."),
    ("3.10.4", "Maintain audit logs of physical access.", 1, "inherited", "164.310(a)(1)", None, None, "AWS physical access logging."),
    ("3.10.5", "Control and manage physical access devices.", 1, "inherited", None, None, None, "AWS badge/key management."),
    ("3.10.6", "Enforce safeguarding measures for CUI at alternate work sites.", 1, "manual", None, None, None, "Remote-work security policy; see docs/policies/."),

    # ---- 3.11 Risk Assessment ----
    ("3.11.1", "Periodically assess risk to operations and assets.", 3, "manual", "164.308(a)(1)(ii)(A)", None, None, "HIPAA Risk Analysis; see docs/risk-analysis.md."),
    ("3.11.2", "Scan for vulnerabilities periodically and when new ones arise.", 5, "automated", "164.308(a)(1)(ii)(B), 164.308(a)(8)", None, None, ""),
    ("3.11.3", "Remediate vulnerabilities in accordance with risk assessments.", 1, "automated", None, None, None, "CI gates block HIGH/CRITICAL; overlaps 3.14.1."),

    # ---- 3.12 Security Assessment (satisfied by THIS engine) ----
    ("3.12.1", "Periodically assess security controls for effectiveness.", 5, "automated", "164.308(a)(8)", None, None, "This compliance engine assesses controls on a schedule; collector pending."),
    ("3.12.2", "Develop and implement plans of action (POA&M).", 3, "automated", None, None, None, "This engine auto-generates the POA&M; collector pending."),
    ("3.12.3", "Monitor security controls on an ongoing basis.", 5, "automated", None, None, None, "Scheduled GitHub Actions run + drift gate; collector pending."),
    ("3.12.4", "Develop and maintain a System Security Plan (SSP).", 0, "automated", None, None, None, "This engine auto-generates the SSP; collector pending."),

    # ---- 3.13 System and Communications Protection ----
    ("3.13.1", "Monitor, control, and protect communications at boundaries.", 5, "automated", "164.312(e)(1)", None, None, "VPC tiers + SG chaining + WAF; collector pending."),
    ("3.13.2", "Employ architectural designs promoting effective security.", 5, "manual", None, None, None, "Documented secure architecture; see ARCHITECTURE.md."),
    ("3.13.3", "Separate user functionality from system management.", 1, "manual", None, None, None, "Separate admin routes/permissions; attested."),
    ("3.13.4", "Prevent unauthorized information transfer via shared resources.", 3, "manual", None, None, None, "Per-tenant isolation + tenant_id scoping; attested."),
    ("3.13.5", "Implement subnetworks for publicly accessible components.", 5, "manual", None, None, None, "Public/private/isolated subnet tiers; attested."),
    ("3.13.6", "Deny network traffic by default; allow by exception.", 3, "manual", None, None, None, "Security groups deny-by-default; attested."),
    ("3.13.7", "Prevent split tunneling for remote devices.", 1, "na", None, None, None, "No remote VPN/devices in the SaaS boundary."),
    ("3.13.8", "Use cryptography to protect CUI during transmission.", 5, "automated", "164.312(e)(1), 164.312(e)(2)(ii)", "170.315(d)(9)", None, ""),
    ("3.13.9", "Terminate network connections after inactivity.", 1, "manual", None, None, None, "Idle timeouts on sessions/keepalive; attested."),
    ("3.13.10", "Establish and manage cryptographic keys.", 1, "inherited", "164.312(a)(2)(iv)", None, None, "AWS KMS manages key lifecycle and rotation."),
    ("3.13.11", "Employ FIPS-validated cryptography to protect CUI.", 3, "automated", "164.312(a)(2)(iv), 164.312(e)(2)(ii)", "170.315(d)(12)", None, ""),
    ("3.13.12", "Prohibit remote activation of collaborative computing devices.", 1, "na", None, None, None, "No cameras/microphones in scope."),
    ("3.13.13", "Control and monitor use of mobile code.", 1, "manual", None, None, None, "CSP/headers restrict client code; attested."),
    ("3.13.14", "Control and monitor use of Voice over IP.", 1, "na", None, None, None, "No VoIP in the SaaS boundary."),
    ("3.13.15", "Protect authenticity of communications sessions.", 5, "manual", None, "170.315(d)(9)", None, "TLS + httpOnly SameSite session cookies; attested."),
    ("3.13.16", "Protect the confidentiality of CUI at rest.", 5, "automated", "164.312(a)(2)(iv)", None, None, "RDS/S3/Secrets encrypted with KMS; collector pending."),

    # ---- 3.14 System and Information Integrity ----
    ("3.14.1", "Identify, report, and correct system flaws in a timely manner.", 5, "automated", "164.308(a)(1)(ii)(B)", None, None, ""),
    ("3.14.2", "Provide protection from malicious code.", 5, "automated", "164.308(a)(5)(ii)(B)", None, None, "Trivy image/dep scanning in CI; collector pending."),
    ("3.14.3", "Monitor system security alerts and advisories; act on them.", 1, "manual", None, None, None, "pip-audit/Trivy advisories + GuardDuty; attested."),
    ("3.14.4", "Update malicious code protection mechanisms.", 1, "automated", None, None, None, "Trivy DB updated each CI run; collector pending."),
    ("3.14.5", "Perform periodic and real-time scans of the system.", 3, "automated", None, None, None, "CI scans on every change; overlaps 3.11.2."),
    ("3.14.6", "Monitor systems to detect attacks and indicators.", 5, "manual", None, None, None, "GuardDuty + VPC Flow Logs + CloudTrail; attested."),
    ("3.14.7", "Identify unauthorized use of organizational systems.", 3, "manual", None, None, None, "Audit log + GuardDuty anomaly detection; attested."),
]


def build():
    controls = []
    for cid, title, weight, ctype, hipaa, onc, part2, rationale in ROWS:
        fam = FAM_OF(cid)
        level = 1 if cid in L1 else 2
        weight = SPRS_WEIGHT.get(cid, weight)  # Annex A is authoritative for weights
        # Genuinely unimplemented controls are honest gaps (scored not-met).
        if cid in NOT_IMPLEMENTED:
            ctype = "gap"
        # Controls with a collector are automated regardless of the row's default.
        elif cid in HAS_COLLECTOR:
            ctype = "automated"
        # Implemented-but-not-automated controls are attested, not gaps.
        elif cid in ROADMAP:
            ctype = "attested"
        # Split the legacy "manual" bucket: genuine docs/process -> policy;
        # everything else implemented in the app -> attested.
        elif ctype == "manual":
            ctype = "policy" if cid in POLICY else "attested"
        mappings = {
            "cmmc_l2": f"{fam}.L{level}-{cid}",
            "hipaa": hipaa,
            "onc": onc,
            "part2": part2,
        }
        entry = {
            "id": cid,
            "family": fam,
            "family_name": FAMILIES[fam],
            "title": title,
            "sprs_weight": weight,
            "type": ctype,
            "mappings": mappings,
        }
        if rationale:
            entry["rationale"] = rationale
        controls.append(entry)

    # numeric sort by the two/three id segments
    def key(c):
        return [int(p) for p in c["id"].split(".")[1:]]
    controls.sort(key=lambda c: (int(c["id"].split(".")[1]), *key(c)[1:]))

    catalog = {
        "framework": "NIST SP 800-171 Rev 2",
        "scoring_model": "DoD Assessment Methodology (SPRS), base score 110",
        "notes": [
            "GENERATED by build_catalog.py. Edit that builder, not this file.",
            "SPRS weights are sourced from the NIST SP 800-171 DoD Assessment Methodology v1.2.1, Annex A (verified). Dispositions (type) and HIPAA/ONC/42 CFR Part 2 mappings remain best-effort and should still be verified against ../references/SOURCES.md.",
            "type: automated (collector-proven), attested (implemented in the app, collector pending), policy (satisfied by a document/process), inherited (AWS-provided), na (not applicable).",
            "CMMC IDs are derived as family.Ln-id. Objectives for automated controls are provided by their collectors at runtime.",
        ],
        "controls": controls,
    }

    out = Path(__file__).resolve().parent / "controls.json"
    out.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out} with {len(controls)} controls.")
    # quick breakdown
    from collections import Counter
    print("By type:", dict(Counter(c["type"] for c in controls)))


if __name__ == "__main__":
    build()
