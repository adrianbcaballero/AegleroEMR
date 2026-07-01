"""
aws_live collector - TEST method (queries the running AWS account via boto3).

Where crypto_config EXAMINEs the Terraform (intent), this collector TESTs the
live account (reality) and flags drift when the two disagree. It corroborates:

  3.13.8  - RDS enforces TLS live (rds.force_ssl = 1 on the parameter group)
  3.13.11 - KMS customer-managed keys have rotation enabled AND RDS storage is
            actually encrypted, confirmed against the running resources

SAFETY: this collector is OPT-IN. It only runs when COMPLIANCE_ENABLE_AWS is set
(the live GitHub Actions job sets it). Without that flag, without boto3, or without
reachable credentials, it returns nothing - it never fabricates a pass, and never
breaks the credential-free local run. Missing IAM permissions skip that check
rather than failing it.
"""

from __future__ import annotations

import os

from .base import (
    Collector, CollectorContext, Finding, Evidence,
    STATUS_MET, STATUS_NOT_MET, METHOD_TEST,
)

_ENABLED = ("1", "true", "yes", "on")


class AwsLiveCollector(Collector):
    name = "aws_live"
    provides = ["3.13.8", "3.13.11"]
    method = METHOD_TEST

    def collect(self, ctx: CollectorContext) -> list[Finding]:
        if os.environ.get("COMPLIANCE_ENABLE_AWS", "").lower() not in _ENABLED:
            return []  # opt-in only

        try:
            import boto3
            from botocore.exceptions import ClientError
        except ImportError:
            return []

        try:
            boto3.client("sts").get_caller_identity()
        except Exception:
            return []  # no reachable credentials -> contribute nothing (no fake pass)

        findings: list[Finding] = []
        for check in (self._check_encryption_at_rest, self._check_force_ssl):
            try:
                f = check(boto3, ClientError)
                if f:
                    findings.append(f)
            except Exception:
                # A missing permission or API error skips this check, it does not
                # turn into a false failure.
                continue
        return findings

    # -- 3.13.11: KMS rotation + RDS storage encryption -----------------------
    def _check_encryption_at_rest(self, boto3, ClientError) -> Finding | None:
        kms = boto3.client("kms")
        customer_keys, no_rotation = [], []
        for page in kms.get_paginator("list_keys").paginate():
            for k in page.get("Keys", []):
                kid = k["KeyId"]
                try:
                    meta = kms.describe_key(KeyId=kid)["KeyMetadata"]
                except ClientError:
                    continue
                if meta.get("KeyManager") != "CUSTOMER" or meta.get("KeyState") != "Enabled":
                    continue
                customer_keys.append(kid)
                try:
                    if not kms.get_key_rotation_status(KeyId=kid).get("KeyRotationEnabled"):
                        no_rotation.append(kid)
                except ClientError:
                    no_rotation.append(kid)

        rds = boto3.client("rds")
        instances = rds.describe_db_instances().get("DBInstances", [])
        unencrypted = [db.get("DBInstanceIdentifier") for db in instances
                       if not db.get("StorageEncrypted")]

        if not customer_keys and not instances:
            return None  # nothing to assert live

        ev = [Evidence("aws-live", "kms:GetKeyRotationStatus",
                       f"{len(customer_keys)} customer-managed KMS key(s); "
                       f"{len(customer_keys) - len(no_rotation)} with rotation enabled (live).")]
        if instances:
            ev.append(Evidence("aws-live", "rds:DescribeDBInstances",
                               f"{len(instances)} RDS instance(s); "
                               f"{len(instances) - len(unencrypted)} StorageEncrypted=true (live)."))

        if no_rotation or unencrypted:
            parts = []
            if no_rotation:
                parts.append(f"{len(no_rotation)} KMS key(s) without rotation")
            if unencrypted:
                parts.append(f"{len(unencrypted)} unencrypted RDS instance(s)")
            return Finding("3.13.11", STATUS_NOT_MET, METHOD_TEST,
                           summary="Live check found: " + "; ".join(parts) + ".",
                           objective_ids=["3.13.11[a]"], evidence=ev)

        return Finding("3.13.11", STATUS_MET, METHOD_TEST,
                       summary="Live AWS confirms KMS keys (FIPS 140-2) have rotation "
                               "enabled and RDS storage is encrypted.",
                       objective_ids=["3.13.11[a]"], evidence=ev)

    # -- 3.13.8: RDS force_ssl live -------------------------------------------
    def _check_force_ssl(self, boto3, ClientError) -> Finding | None:
        rds = boto3.client("rds")
        instances = rds.describe_db_instances().get("DBInstances", [])
        if not instances:
            return None

        pg_names = {pg.get("DBParameterGroupName")
                    for db in instances for pg in db.get("DBParameterGroups", [])}
        checked = []
        for pg in filter(None, pg_names):
            try:
                val = None
                for page in rds.get_paginator("describe_db_parameters").paginate(
                        DBParameterGroupName=pg):
                    for p in page.get("Parameters", []):
                        if p.get("ParameterName") == "rds.force_ssl":
                            val = p.get("ParameterValue")
                checked.append((pg, val))
            except ClientError:
                continue

        if not checked:
            return None

        ev = [Evidence("aws-live", "rds:DescribeDBParameters",
                       "; ".join(f"{pg}: rds.force_ssl={v}" for pg, v in checked) + " (live)")]
        all_forced = all(v == "1" for _, v in checked)
        if all_forced:
            return Finding("3.13.8", STATUS_MET, METHOD_TEST,
                           summary="Live AWS confirms RDS enforces TLS (rds.force_ssl=1).",
                           objective_ids=["3.13.8[c]"], evidence=ev)
        return Finding("3.13.8", STATUS_NOT_MET, METHOD_TEST,
                       summary="Live AWS shows rds.force_ssl is not enforced on all "
                               "parameter groups.",
                       objective_ids=["3.13.8[c]"], evidence=ev)
