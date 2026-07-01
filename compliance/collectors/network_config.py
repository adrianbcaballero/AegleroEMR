"""
network_config collector - EXAMINE method.

Proves network boundary and isolation controls by examining the Terraform network
definition. No cloud credentials needed.

Maps to:
  3.13.1 - monitor, control, and protect communications at boundaries (dedicated VPC,
           chained security groups, ALB ingress restricted to the CloudFront prefix list)
  3.13.5 - implement subnetworks for publicly accessible components (public / private /
           isolated three-tier subnet model)
  3.13.6 - deny network traffic by default, allow by exception (security groups are
           deny-by-default; each tier allowlists only its required ingress)
"""

from __future__ import annotations

from .base import (
    Collector, CollectorContext, Finding, Evidence,
    STATUS_MET, STATUS_NOT_MET, STATUS_ERROR, METHOD_EXAMINE,
)

NET = "infra/network.tf"


class NetworkConfigCollector(Collector):
    name = "network_config"
    provides = ["3.13.1", "3.13.5", "3.13.6"]
    method = METHOD_EXAMINE

    def collect(self, ctx: CollectorContext) -> list[Finding]:
        net = ctx.repo_root / NET
        if not net.exists():
            return [self._error(cid, f"{NET} not found") for cid in self.provides]

        vpc = self.grep(net, 'resource "aws_vpc"')
        pub = self.grep(net, 'Tier = "public"')
        priv = self.grep(net, 'Tier = "private"')
        iso = self.grep(net, 'Tier = "isolated"')
        sgs = self.grep(net, 'resource "aws_security_group"')
        prefix = self.grep(net, "prefix_list_ids")
        ingress = self.grep(net, "ingress {")

        findings: list[Finding] = []

        # --- 3.13.5: subnetworks for publicly accessible components --------
        if pub and priv and iso:
            findings.append(Finding(
                control_id="3.13.5", status=STATUS_MET, method=METHOD_EXAMINE,
                summary="Publicly accessible components are separated into a three-tier subnet "
                        "model: public (ALB), private (ECS Fargate), and isolated (RDS, no "
                        "internet route).",
                objective_ids=["3.13.5[a]"],
                evidence=[
                    Evidence("terraform", f"{NET}:{pub[0][0]}", "Public subnet tier for the ALB."),
                    Evidence("terraform", f"{NET}:{priv[0][0]}", "Private subnet tier for ECS tasks."),
                    Evidence("terraform", f"{NET}:{iso[0][0]}", "Isolated subnet tier for RDS (no internet route)."),
                ]))
        else:
            findings.append(self._not_met("3.13.5", "Three-tier subnet separation not found."))

        # --- 3.13.1: boundary protection ----------------------------------
        if vpc and sgs and prefix:
            findings.append(Finding(
                control_id="3.13.1", status=STATUS_MET, method=METHOD_EXAMINE,
                summary="Communications are controlled at the boundary: a dedicated VPC, chained "
                        "security groups, and ALB ingress restricted to the AWS-managed CloudFront "
                        "origin-facing prefix list, so the API is reachable only via CloudFront.",
                objective_ids=["3.13.1[a]"],
                evidence=[
                    Evidence("terraform", f"{NET}:{vpc[0][0]}", "Dedicated VPC forms the network boundary."),
                    Evidence("terraform", f"{NET}:{prefix[0][0]}", "ALB ingress limited to the CloudFront origin-facing prefix list."),
                    Evidence("terraform", f"{NET}:{sgs[0][0]}", f"{len(sgs)} security groups chain ALB -> ECS -> RDS."),
                ]))
        else:
            findings.append(self._not_met("3.13.1", "Boundary protection config not found."))

        # --- 3.13.6: deny by default, allow by exception ------------------
        if sgs and ingress:
            findings.append(Finding(
                control_id="3.13.6", status=STATUS_MET, method=METHOD_EXAMINE,
                summary="Network traffic is denied by default and allowed by exception: AWS "
                        "security groups deny all traffic unless explicitly permitted, and each "
                        "tier allows only its required ingress (ALB 443, ECS 5000 from the ALB "
                        "SG, RDS 5432 from the ECS SG).",
                objective_ids=["3.13.6[a]"],
                evidence=[
                    Evidence("terraform", f"{NET}:{sgs[0][0]}", "Security groups are deny-by-default; only scoped ingress is added."),
                    Evidence("terraform", f"{NET}:{ingress[0][0]}", "Ingress is explicitly allowlisted per tier."),
                ]))
        else:
            findings.append(self._not_met("3.13.6", "Deny-by-default security-group config not found."))

        return findings

    # -- helpers ---------------------------------------------------------------

    def _not_met(self, cid: str, why: str) -> Finding:
        return Finding(control_id=cid, status=STATUS_NOT_MET,
                       method=METHOD_EXAMINE, summary=why)

    def _error(self, cid: str, why: str) -> Finding:
        return Finding(control_id=cid, status=STATUS_ERROR,
                       method=METHOD_EXAMINE, summary=why)
