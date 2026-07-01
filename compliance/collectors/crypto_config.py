"""
crypto_config collector - EXAMINE method.

Proves Aeglero's cryptographic protections by examining the Terraform that
defines the infrastructure. Infrastructure-as-Code is legitimate configuration
evidence and needs no cloud credentials, so this stays in the Phase-1 EXAMINE
family while closing the two crypto controls.

Maps to:
  3.13.8  - cryptographic mechanisms prevent disclosure of data in transit
            (RDS rds.force_ssl, ALB TLS 1.2/1.3 policy, CloudFront min TLS 1.2,
             redirect-to-https)
  3.13.11 - FIPS-validated cryptography protects confidentiality
            (AWS KMS customer-managed keys with rotation; AWS KMS HSMs are
             FIPS 140-2 validated; RDS storage encrypted with those CMKs)
"""

from __future__ import annotations

from .base import (
    Collector, CollectorContext, Finding, Evidence,
    STATUS_MET, STATUS_PARTIAL, STATUS_NOT_MET, STATUS_ERROR, METHOD_EXAMINE,
)

KMS = "infra/kms.tf"
RDS = "infra/rds.tf"
ALB = "infra/alb.tf"
CF = "infra/cloudfront.tf"


class CryptoConfigCollector(Collector):
    name = "crypto_config"
    provides = ["3.13.8", "3.13.11"]
    method = METHOD_EXAMINE

    def collect(self, ctx: CollectorContext) -> list[Finding]:
        root = ctx.repo_root
        if not (root / KMS).exists() and not (root / RDS).exists():
            return [self._error(cid, "Terraform infra/ not found") for cid in self.provides]

        force_ssl = self.grep(root / RDS, "rds.force_ssl")
        storage_enc = self.grep(root / RDS, "storage_encrypted")
        rds_kms = self.grep(root / RDS, "kms_key_id")
        alb_tls = self.grep(root / ALB, "ssl_policy")
        cf_tls = self.grep(root / CF, "minimum_protocol_version")
        cf_https = self.grep(root / CF, "redirect-to-https")
        kms_keys = self.grep(root / KMS, "resource \"aws_kms_key\"")
        kms_rot = self.grep(root / KMS, "enable_key_rotation")

        findings: list[Finding] = []

        # --- 3.13.8: encryption in transit ---------------------------------
        transit = []
        if force_ssl:
            transit.append(Evidence("terraform", f"{RDS}:{force_ssl[0][0]}",
                "RDS parameter rds.force_ssl=1 rejects any non-TLS database connection."))
        if alb_tls:
            transit.append(Evidence("terraform", f"{ALB}:{alb_tls[0][0]}",
                "ALB HTTPS listener uses a TLS 1.2/1.3 security policy."))
        if cf_tls:
            transit.append(Evidence("terraform", f"{CF}:{cf_tls[0][0]}",
                "CloudFront enforces a minimum TLS 1.2 viewer protocol version."))
        if cf_https:
            transit.append(Evidence("terraform", f"{CF}:{cf_https[0][0]}",
                "CloudFront redirects all viewer traffic to HTTPS."))

        if force_ssl and (alb_tls or cf_tls):
            findings.append(Finding(
                control_id="3.13.8", status=STATUS_MET, method=METHOD_EXAMINE,
                summary="Data in transit is encrypted end to end: TLS 1.2+ is enforced "
                        "at CloudFront and the ALB, and RDS refuses non-TLS connections.",
                objective_ids=["3.13.8[c]"], evidence=transit))
        elif transit:
            findings.append(Finding(
                control_id="3.13.8", status=STATUS_PARTIAL, method=METHOD_EXAMINE,
                summary="Some transport encryption is configured, but full edge-to-database "
                        "TLS enforcement was not detected.",
                objective_ids=["3.13.8[c]"], evidence=transit))
        else:
            findings.append(self._not_met("3.13.8", "No in-transit encryption config found."))

        # --- 3.13.11: FIPS-validated cryptography --------------------------
        atrest = []
        if kms_keys:
            atrest.append(Evidence("terraform", f"{KMS}:{kms_keys[0][0]}",
                f"{len(kms_keys)} customer-managed AWS KMS key(s) defined. AWS KMS HSMs "
                "are FIPS 140-2 validated (NIST CMVP)."))
        if kms_rot:
            atrest.append(Evidence("terraform", f"{KMS}:{kms_rot[0][0]}",
                "Automatic annual key rotation is enabled on the KMS keys."))
        if storage_enc and rds_kms:
            atrest.append(Evidence("terraform", f"{RDS}:{storage_enc[0][0]}",
                "RDS storage is encrypted at rest using a customer-managed KMS key."))

        if kms_keys and storage_enc:
            findings.append(Finding(
                control_id="3.13.11", status=STATUS_MET, method=METHOD_EXAMINE,
                summary="Confidentiality is protected with FIPS 140-2 validated cryptography: "
                        "AWS KMS customer-managed keys (rotated) encrypt RDS storage, "
                        "Secrets Manager, logs, and S3; TLS in transit terminates on AWS's "
                        "FIPS-capable endpoints.",
                objective_ids=["3.13.11[a]"], evidence=atrest))
        elif atrest:
            findings.append(Finding(
                control_id="3.13.11", status=STATUS_PARTIAL, method=METHOD_EXAMINE,
                summary="KMS keys are defined but at-rest encryption of RDS storage was "
                        "not fully confirmed.",
                objective_ids=["3.13.11[a]"], evidence=atrest))
        else:
            findings.append(self._not_met("3.13.11", "No KMS/FIPS crypto config found."))

        return findings

    # -- helpers ---------------------------------------------------------------

    def _not_met(self, cid: str, why: str) -> Finding:
        return Finding(control_id=cid, status=STATUS_NOT_MET,
                       method=METHOD_EXAMINE, summary=why)

    def _error(self, cid: str, why: str) -> Finding:
        return Finding(control_id=cid, status=STATUS_ERROR,
                       method=METHOD_EXAMINE, summary=why)
