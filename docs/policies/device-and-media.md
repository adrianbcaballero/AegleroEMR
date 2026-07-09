# Device and Media Controls Policy

**Status:** Draft
**Owner:** Security Officer (system owner acts in this role for the current deployment)
**Effective date:** 2026-07-08
**Review cycle:** Annual
**Regulatory basis:** HIPAA 45 CFR 164.310(d); NIST SP 800-171 Rev 2

## 1. Purpose

This policy covers the devices and media that can access or store PHI: how endpoints are used, how
data at rest on media is protected, and how media is sanitized before disposal or reuse. It also
records why several media-related framework controls do not apply to this system.

## 2. Scope

This policy covers the operator's administrative workstation, the cloud storage that holds
application data, and any media that could hold PHI. Aeglero is a cloud-hosted system with no
on-premises servers.

## 3. Policy

### 3.1 Workstation use

The administrative workstation used to operate Aeglero is a managed endpoint. It uses full-disk
encryption, requires authentication, locks on inactivity, and is kept current on security updates.
It is the same hardened environment described in the operator's private infrastructure setup, kept
segmented from untrusted networks.

### 3.2 Encryption of data at rest on managed storage

All application data at rest lives in AWS and is encrypted with customer-managed KMS keys: the
database, secrets, logs, and object storage. PHI is not stored on local devices in the normal course
of operation; the application is accessed through the browser and the authoritative record stays in
the encrypted database.

### 3.3 Media sanitization and disposal

Because storage is cloud-managed, media disposal is handled by the cloud provider under its
attestations, and cryptographic erasure applies: destroying the KMS key renders the encrypted data
unrecoverable. Any local media that ever held PHI is sanitized to a recognized standard before reuse
and destroyed before disposal.

### 3.4 Movement and tracking of media

Movement of any device or media that stores PHI is minimized and, where it occurs, tracked. In
practice this system does not move PHI onto portable media.

## 4. Controls that do not apply, with rationale

Several framework controls address component types that are not present in Aeglero's authorization
boundary. They are marked not applicable with the following rationale, so the disposition is on the
record rather than assumed:

- **Wireless access (3.1.16, 3.1.17).** There is no wireless network component in the boundary; the
  system is cloud-hosted and accessed over the public internet using TLS.
- **Mobile devices and mobile code platforms (3.1.18, 3.1.19).** There is no managed mobile device
  fleet and no mobile application in scope.
- **User-installed software (3.4.9).** The application runs in immutable container images; there is no
  end-user software installation surface on the servers.
- **Removable and portable media (3.1.21, 3.8.4 through 3.8.8).** The system does not use removable or
  portable storage media for PHI.
- **Diagnostic and test media (3.7.4).** No maintenance is performed using external diagnostic media.
- **Split tunneling (3.13.7).** There are no remote devices configured with split tunneling in scope.
- **Collaborative computing devices (3.13.12).** No cameras, microphones, or shared collaborative
  devices are part of the system.
- **Voice over IP (3.13.14).** There is no VoIP component in the boundary.

Summary line: no wireless, no mobile, no removable media, and no VoIP. These are components that do
not exist in the boundary, and each is documented above rather than silently skipped.

## 5. Roles and responsibilities

- **Security Officer.** Owns endpoint standards and the not-applicable determinations, and revisits
  them if the boundary changes (for example, if a mobile application is ever added).
- **Operators.** Keep their endpoints compliant with section 3.1.

## 6. Review and maintenance

Reviewed at least annually and whenever a new component type is introduced that could change an
applicability determination.

## Control mapping

This policy documents endpoint and media handling and records the rationale for the media-related
controls determined not applicable (3.1.16, 3.1.17, 3.1.18, 3.1.19, 3.1.21, 3.4.9, 3.7.4, 3.8.4
through 3.8.8, 3.13.7, 3.13.12, 3.13.14).

HIPAA basis: 45 CFR 164.310(d) (device and media controls: disposal, reuse, accountability, backup).
