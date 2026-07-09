# Workforce Security Policy

**Status:** Draft
**Owner:** Security Officer (system owner acts in this role for the current deployment)
**Effective date:** 2026-07-08
**Review cycle:** Annual
**Regulatory basis:** HIPAA 45 CFR 164.308(a)(3), 164.308(a)(5); NIST SP 800-171 Rev 2

## 1. Purpose

This policy governs how the workforce is screened before being granted access, how they are trained
on their security responsibilities, and how access is managed through role changes and departure.
It also defines the sanctions for security violations.

## 2. Scope

This policy applies to any person granted access to PHI or to the systems that support it, including
employees, contractors, and any third party acting on the organization's behalf.

## 3. Policy

### 3.1 Applicability note for the current deployment

Aeglero is currently a single-operator demonstration system with no workforce beyond the owner. The
controls in this policy are organizational controls that require an actual workforce to be in effect,
so they are documented here as the program that applies the moment a second person is granted access.
Until then, the related NIST 800-171 controls (3.2.1, 3.2.2, 3.2.3, 3.9.1, 3.9.2) are tracked as open
items in the POA&M rather than claimed as satisfied. This is deliberate: the policy states intent, and
the controls close when there are people to screen and train and records to show for it.

### 3.2 Personnel screening (3.9.1)

Before an individual is authorized to access PHI or supporting systems, they are screened
appropriately for the sensitivity of the access, which for a healthcare system includes an identity
and background check consistent with applicable law. Access is not granted until screening is
complete.

### 3.3 Security awareness and training (3.2.1, 3.2.2, 3.2.3)

- **Awareness (3.2.1).** Everyone with access is made aware of the security risks associated with
  their activities and of the policies that apply to them, at onboarding and at least annually
  thereafter.
- **Role-based training (3.2.2).** Individuals are trained to carry out the specific security
  responsibilities of their role. Administrators and operators receive additional training on
  privileged access, incident response, and handling of PHI and 42 CFR Part 2 records.
- **Insider threat awareness (3.2.3).** Training includes recognizing and reporting indicators of
  insider threat.

Training completion is recorded so that coverage can be demonstrated.

### 3.4 Role changes and least privilege

When a person's role changes, their access is re-evaluated and adjusted to match the new role under
the Information Access Management Policy, removing any access that is no longer needed.

### 3.5 Termination and personnel actions (3.9.2)

Access is protected during and after personnel actions such as transfer or termination. On
departure, access is revoked promptly, within 24 hours and immediately for an involuntary
termination. The application supports this directly: an administrator can permanently lock an
account, which blocks future logins and ends all of that account's active sessions at once, while
preserving the audit trail. Physical and credential access, where applicable, is also recovered.

### 3.6 Sanctions

Workforce members who violate this policy or the security policies it sits under are subject to
sanctions appropriate to the severity of the violation, up to and including termination and referral
to authorities where the law requires it. Sanctions are applied consistently and recorded.

## 4. Roles and responsibilities

- **Security Officer.** Owns screening standards, the training program, and the sanction process.
- **Administrators.** Provision and revoke access in line with screening and role status.

In the current single-operator deployment the system owner holds these roles. In a staffed
organization, screening and sanction decisions would involve human resources and management, separate
from the technical administrator.

## 5. Review and maintenance

Reviewed at least annually. Training records and access changes are retained as evidence.

## Control mapping

| Control | Title | How this policy addresses it |
|---|---|---|
| 3.2.1 | Make personnel aware of security risks | Awareness training at onboarding and annually (section 3.3) |
| 3.2.2 | Train personnel for their assigned security duties | Role-based training (section 3.3) |
| 3.2.3 | Provide insider-threat awareness training | Insider threat content in training (section 3.3) |
| 3.9.1 | Screen individuals before authorizing access | Pre-access screening (section 3.2) |
| 3.9.2 | Protect CUI during and after personnel actions | Prompt revocation and session termination (section 3.5) |

HIPAA basis: 45 CFR 164.308(a)(3) (workforce security), 164.308(a)(5) (awareness and training).
