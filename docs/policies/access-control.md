# Information Access Management Policy

**Status:** Draft
**Owner:** Security Officer (system owner acts in this role for the current deployment)
**Effective date:** 2026-07-08
**Review cycle:** Annual; access reviews performed quarterly
**Regulatory basis:** HIPAA 45 CFR 164.308(a)(4); NIST SP 800-171 Rev 2

## 1. Purpose

This policy governs how access to PHI and to the systems that support it is requested, approved,
provisioned, reviewed, changed, and revoked. The goal is least privilege: every identity, human or
machine, has only the access it needs to do its job and no more.

## 2. Scope

This policy covers application users, administrators, and the machine identities (CI/CD roles) that
act on the system. It applies to the Aeglero application, its AWS account, and its deployment
pipeline.

## 3. Policy

### 3.1 Least privilege and role-based access

Access is granted through roles, not to individuals directly. The application uses a role-based
access control model in which each user holds one role per tenant, and each role carries an explicit
set of permissions. Patient visibility is further scoped by care team, so a user sees only the
patients assigned to a care team they belong to. Access is granted at the minimum level required.

### 3.2 Separation of duties (3.1.4)

Duties are separated so that no single identity can both perform and conceal a sensitive action.
In the application, the permission catalog separates duties across functional domains. In the
pipeline, two distinct machine identities are used: a read-only role that can examine the AWS
account but cannot change it, and a deploy role that can publish the dashboard but cannot read
application data. In the current single-operator deployment the system owner performs all human
duties; in a staffed organization, provisioning, approval, and audit review would be assigned to
different people so that the person who grants access is not the only person who reviews it.

### 3.3 Account lifecycle

- **Provisioning.** New accounts are created through the invite flow, which issues a
  single-use invitation and requires the recipient to set their own credentials on first use.
- **Temporary credentials (3.5.9).** Any temporary or invitation-issued credential is valid for a
  single use or a short window and requires the user to set a permanent credential before normal
  access is granted. Temporary credentials are never reused.
- **Inactivity disablement (3.5.6).** Accounts that show no activity within a defined period are
  disabled pending review. Sessions themselves expire on a 15-minute sliding idle timeout, and an
  administrator can permanently lock an account, which immediately ends all of that user's active
  sessions.
- **Revocation.** Access is revoked promptly on role change or departure. The permanent lock action
  both blocks future logins and terminates existing sessions in one step.

### 3.4 Privileged and remote access (3.1.15, 3.7.5)

Privileged operational access to the running system is performed only through AWS Systems Manager
Session Manager (`aws ecs execute-command`). There is no SSH and no bastion host. Every session is
recorded in CloudTrail. Privileged remote actions, including nonlocal maintenance sessions (3.7.5),
require multi-factor authentication on the operator's AWS identity before the session can begin.

### 3.5 Public surfaces and CUI on public systems (3.1.22, 3.1.9)

Only non-sensitive content is placed on publicly reachable surfaces. The compliance dashboard is a
public, non-sensitive demonstration that contains no PHI or secrets and carries a noindex tag.
Application interfaces that handle PHI are not publicly anonymous; they require authentication, and
users are presented with the applicable privacy and security notices (3.1.9) as part of access.

### 3.6 Access reviews

Access and role assignments are reviewed at least quarterly to confirm they still match need. The
review checks for dormant accounts, over-broad roles, and any access that should have been revoked.

## 4. Roles and responsibilities

- **Security Officer.** Approves access requests and elevated access, and owns the quarterly review.
- **Administrators.** Provision, modify, and revoke accounts within approved roles.
- **Users.** Use only the access granted to them and report access that appears excessive.

## 5. Review and maintenance

Reviewed at least annually. Quarterly access reviews are recorded in version control or the audit
log.

## Control mapping

| Control | Title | How this policy addresses it |
|---|---|---|
| 3.1.4 | Separate the duties of individuals | Duty separation, machine and human (section 3.2) |
| 3.1.9 | Provide privacy and security notices | Notices on authenticated access (section 3.5) |
| 3.1.15 | Authorize remote execution of privileged commands | SSM only, MFA, CloudTrail (section 3.4) |
| 3.1.22 | Control CUI posted on publicly accessible systems | Non-sensitive public surfaces only (section 3.5) |
| 3.5.6 | Disable identifiers after a defined period of inactivity | Inactivity disablement and lock (section 3.3) |
| 3.5.9 | Allow temporary passwords with immediate change | Single-use invite credentials (section 3.3) |
| 3.7.5 | Require MFA for nonlocal maintenance sessions | MFA on privileged/remote sessions (section 3.4) |

HIPAA basis: 45 CFR 164.308(a)(4) (information access management), 164.312(a)(1) (access control).
